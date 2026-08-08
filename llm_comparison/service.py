from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import timedelta
from typing import cast

from llm_comparison.models import (
    BaselineRequest,
    ExperimentPlan,
    FailedObservation,
    FailureCategory,
    ManifestEnvelope,
    Metric,
    OperationalEvidence,
    OperationalEvidenceEnvelope,
    PlanEnvelope,
    TrialEnvelope,
    TrialObservation,
    TrialRequestSettings,
    canonical_prompt_suite_hash,
    canonical_persisted_schedule_hash,
    canonical_request_schedule_hash,
    sha256_text,
)
from llm_comparison.ports import Clock, EnvelopeStore, ModelClient, ModelClientError


@dataclass(frozen=True, slots=True)
class ComparisonTarget:
    client: ModelClient
    manifest_record_id: str
    target_id: str
    adapter_version: str
    block_index: int


class ComparisonService:
    """Executes one externally loaded model block at a time."""

    def __init__(self, *, store: EnvelopeStore, clock: Clock) -> None:
        self._store = store
        self._clock = clock

    def run_target_block(
        self,
        target: ComparisonTarget,
        requests: tuple[BaselineRequest, ...],
        plan_record_id: str,
    ) -> tuple[TrialEnvelope, ...]:
        records = self._store.read_all()
        plan_envelope = self._plan_for(records, plan_record_id)
        plan = plan_envelope.payload
        manifest = self._manifest_for(target.manifest_record_id)
        if target.block_index not in {0, 1}:
            raise ValueError("target block index must be zero or one")
        if (
            target.target_id != manifest.payload.adapter.expected_model_identity
            or target.adapter_version != manifest.payload.adapter.adapter_version
            or target.block_index != manifest.payload.block_index
        ):
            raise ValueError("target configuration does not match persisted manifest")
        if (
            plan.experiment_id != manifest.payload.experiment_id
            or plan.run_id != manifest.payload.run_id
            or plan.block_order[target.block_index] != target.block_index
            or plan.model_repositories[target.block_index]
            != manifest.payload.model.source_repository
        ):
            raise ValueError("experiment plan does not match target block")
        if (
            plan.runtime_revision != manifest.payload.runtime.runtime_revision
            or plan.runtime_binary_sha256
            != manifest.payload.runtime.runtime_binary_sha256
            or plan.artifact_revisions[target.block_index]
            != manifest.payload.model.repository_revision
            or plan.artifact_set_hashes[target.block_index]
            != manifest.payload.model.artifact_set_hash()
            or plan.generation_config_hashes[target.block_index]
            != manifest.payload.generation.configuration_hash()
            or plan.adapter_versions[target.block_index]
            != manifest.payload.adapter.adapter_version
            or plan.chat_template_hashes[target.block_index]
            != manifest.payload.model.chat_template_sha256
            or plan.tokenizer_hashes[target.block_index]
            != manifest.payload.model.tokenizer_sha256
        ):
            raise ValueError("active manifest does not match frozen plan pins")
        self._validate_block_requests(requests, plan)
        self._validate_operational_evidence(
            records, manifest, plan_envelope, len(requests)
        )
        existing_trials = self._existing_trials(
            records, requests, target, plan_envelope
        )
        persisted: list[TrialEnvelope] = []
        for request in requests:
            record_id = self._record_id(request, target.target_id)
            if record_id in existing_trials:
                persisted.append(existing_trials[record_id])
                continue
            self._validate_request_manifest(request, manifest)
            try:
                result = target.client.generate(request)
            except ModelClientError as exc:
                category = (
                    cast(FailureCategory, exc.category)
                    if exc.category
                    in {
                        "not_ready",
                        "configuration",
                        "timeout",
                        "transport",
                        "protocol",
                        "server",
                    }
                    else "protocol"
                )
                result = FailedObservation(
                    experiment_id=request.experiment_id,
                    run_id=request.run_id,
                    trial_id=request.trial_id,
                    prompt_suite_id=request.prompt_suite_id,
                    prompt_case_id=request.prompt_case_id,
                    prompt_hash=request.prompt_hash,
                    generation_fingerprint=request.generation_fingerprint(),
                    model_identity=manifest.payload.adapter.expected_model_identity,
                    started_at=self._clock.utc_now(),
                    elapsed_seconds=0.0,
                    metrics=(
                        Metric(
                            name="request_wall_time",
                            value=None,
                            unit="seconds",
                            boundary="model client call",
                            source="client_observed",
                            unavailable_reason="client_failed_without_observation",
                        ),
                    ),
                    category=category,
                    sanitized_detail=exc.safe_code,
                )
            expected_identity = manifest.payload.adapter.expected_model_identity
            if result.model_identity != expected_identity:
                raise ValueError(
                    "target result identity does not match persisted manifest"
                )
            if plan.mode == "heldout":
                warmup = self._matching_evidence(
                    records,
                    manifest,
                    manifest.payload.warmup_evidence_id,
                    "warmup_completed",
                )
                if result.started_at < warmup.payload.observed_at:
                    raise ValueError(
                        "measured trial predates required warm-up evidence"
                    )
            envelope = TrialEnvelope(
                record_id=record_id,
                experiment_id=request.experiment_id,
                run_id=request.run_id,
                trial_id=request.trial_id,
                payload=TrialObservation(
                    manifest_record_id=target.manifest_record_id,
                    plan_record_id=plan_record_id,
                    plan_hash=plan_envelope.plan_hash,
                    request_settings=TrialRequestSettings.from_request(request),
                    block_index=manifest.payload.block_index,
                    result=result,
                ),
            )
            self._store.append(envelope)
            persisted.append(envelope)
        completed_at = self._clock.utc_now()
        if any(
            completed_at
            < record.payload.result.started_at
            + timedelta(seconds=record.payload.result.elapsed_seconds)
            for record in persisted
        ):
            raise ValueError(
                "block completion clock precedes a persisted trial outcome"
            )
        completion = OperationalEvidenceEnvelope(
            record_id=(
                f"block-completed-{manifest.payload.experiment_id}-"
                f"{manifest.payload.run_id}-{target.block_index}"
            ),
            experiment_id=manifest.payload.experiment_id,
            run_id=manifest.payload.run_id,
            trial_id="block-completion",
            payload=OperationalEvidence(
                evidence_type="block_completed",
                observed_at=completed_at,
                model_identity=manifest.payload.adapter.expected_model_identity,
                block_index=target.block_index,
                generation_config_hash=manifest.payload.generation.configuration_hash(),
                success=True,
                safe_detail_code="all_trial_outcomes_persisted",
                plan_record_id=plan_record_id,
                plan_hash=plan_envelope.plan_hash,
                request_schedule_hash=plan.request_schedule_hash,
                durable_trial_count=len(persisted),
                durable_trial_set_hash=self._trial_set_hash(persisted),
            ),
        )
        self._store.append(completion)
        return tuple(persisted)

    @staticmethod
    def _existing_trials(
        records: tuple[object, ...],
        requests: tuple[BaselineRequest, ...],
        target: ComparisonTarget,
        plan: PlanEnvelope,
    ) -> dict[str, TrialEnvelope]:
        existing: dict[str, TrialEnvelope] = {}
        for request in requests:
            record_id = ComparisonService._record_id(request, target.target_id)
            matches = [
                record
                for record in records
                if isinstance(record, TrialEnvelope) and record.record_id == record_id
            ]
            if not matches:
                continue
            if len(matches) != 1:
                raise ValueError("duplicate durable trial record")
            record = matches[0]
            expected = TrialRequestSettings.from_request(request)
            if (
                record.payload.manifest_record_id != target.manifest_record_id
                or record.payload.plan_record_id != plan.record_id
                or record.payload.plan_hash != plan.plan_hash
                or record.payload.block_index != target.block_index
                or record.payload.request_settings != expected
                or record.payload.result.model_identity != target.target_id
            ):
                raise ValueError("pre-existing trial conflicts with active block")
            existing[record_id] = record
        return existing

    @staticmethod
    def _plan_for(records: tuple[object, ...], record_id: str) -> PlanEnvelope:
        matches = [
            record
            for record in records
            if isinstance(record, PlanEnvelope) and record.record_id == record_id
        ]
        if len(matches) != 1:
            raise ValueError("execution requires exactly one persisted experiment plan")
        return matches[0]

    def _validate_operational_evidence(
        self,
        records: tuple[object, ...],
        manifest: ManifestEnvelope,
        plan_envelope: PlanEnvelope,
        expected_trial_count: int,
    ) -> None:
        plan = plan_envelope.payload
        block = manifest.payload.block_index
        completion_id = self._completion_record_id(plan, block)
        completion_matches = [
            record
            for record in records
            if isinstance(record, OperationalEvidenceEnvelope)
            and record.record_id == completion_id
        ]
        if completion_matches:
            if len(completion_matches) != 1:
                raise ValueError("duplicate canonical block completion evidence")
            self._validate_completion(
                completion_matches[0],
                records,
                manifest,
                plan_envelope,
                expected_trial_count,
            )
            raise ValueError("target block is already complete")
        prior_completion: OperationalEvidenceEnvelope | None = None
        shutdown: OperationalEvidenceEnvelope | None = None
        if block == 0:
            if manifest.payload.prior_shutdown_evidence_id is not None:
                raise ValueError("first block cannot reference prior shutdown evidence")
        else:
            if manifest.payload.prior_shutdown_evidence_id is None:
                raise ValueError("second block requires prior shutdown evidence")
            prior_completions = [
                record
                for record in records
                if isinstance(record, OperationalEvidenceEnvelope)
                and record.record_id == self._completion_record_id(plan, 0)
            ]
            if len(prior_completions) != 1:
                raise ValueError(
                    "second block requires exactly one first-block completion"
                )
            prior_completion = prior_completions[0]
            block_zero_manifest = self._block_zero_manifest(records, plan)
            self._validate_completion(
                prior_completion,
                records,
                block_zero_manifest,
                plan_envelope,
                expected_trial_count,
            )
            shutdown = self._matching_evidence(
                records,
                manifest,
                manifest.payload.prior_shutdown_evidence_id,
                "server_shutdown",
                expected_block=0,
                expected_config_hash=plan.generation_config_hashes[0],
                expected_model_identity=block_zero_manifest.payload.adapter.expected_model_identity,
            )
            if prior_completion.payload.observed_at > shutdown.payload.observed_at:
                raise ValueError("shutdown evidence predates first-block completion")
        if plan.mode != "heldout":
            return
        startup = self._matching_evidence(
            records, manifest, manifest.payload.startup_evidence_id, "startup"
        )
        readiness = self._matching_evidence(
            records, manifest, manifest.payload.readiness_evidence_id, "readiness"
        )
        warmup = self._matching_evidence(
            records, manifest, manifest.payload.warmup_evidence_id, "warmup_completed"
        )
        warmups = [
            record
            for record in records
            if isinstance(record, OperationalEvidenceEnvelope)
            and record.payload.evidence_type == "warmup_completed"
            and record.experiment_id == manifest.payload.experiment_id
            and record.run_id == manifest.payload.run_id
            and record.payload.block_index == block
        ]
        if len(warmups) != plan.warmup_requests:
            raise ValueError("measured block requires exactly one warm-up observation")
        if (
            manifest.payload.readiness.elapsed_seconds is None
            or readiness.payload.elapsed_seconds
            != manifest.payload.readiness.elapsed_seconds
        ):
            raise ValueError(
                "manifest readiness does not match durable readiness evidence"
            )
        if not (
            startup.payload.observed_at
            <= readiness.payload.observed_at
            <= warmup.payload.observed_at
            <= manifest.payload.created_at
        ):
            raise ValueError(
                "startup, readiness and warm-up evidence chronology is invalid"
            )
        generation = manifest.payload.generation
        if generation.effective_gpu_layers < generation.requested_gpu_layers:
            assert generation.gpu_offload_failure_record_id is not None
            failure = self._matching_evidence(
                records,
                manifest,
                generation.gpu_offload_failure_record_id,
                "gpu_load_failure",
            )
            if (
                failure.payload.success
                or failure.payload.attempted_gpu_layers
                != generation.requested_gpu_layers
            ):
                raise ValueError(
                    "GPU fallback evidence does not match full-offload failure"
                )
            if failure.payload.observed_at > startup.payload.observed_at:
                raise ValueError("GPU load failure must precede successful startup")
        if block == 1 and (
            prior_completion is None
            or shutdown is None
            or shutdown.payload.observed_at > startup.payload.observed_at
        ):
            raise ValueError("block transition evidence chronology is invalid")

    @staticmethod
    def _matching_evidence(
        records: tuple[object, ...],
        manifest: ManifestEnvelope,
        record_id: str,
        evidence_type: str,
        *,
        expected_block: int | None = None,
        expected_config_hash: str | None = None,
        expected_model_identity: str | None = None,
    ) -> OperationalEvidenceEnvelope:
        matches = [
            record
            for record in records
            if isinstance(record, OperationalEvidenceEnvelope)
            and record.record_id == record_id
        ]
        if len(matches) != 1:
            raise ValueError("required operational evidence is missing or duplicated")
        evidence = matches[0]
        if (
            evidence.payload.evidence_type != evidence_type
            or evidence.experiment_id != manifest.payload.experiment_id
            or evidence.run_id != manifest.payload.run_id
            or evidence.payload.block_index
            != (
                manifest.payload.block_index
                if expected_block is None
                else expected_block
            )
            or evidence.payload.generation_config_hash
            != (
                manifest.payload.generation.configuration_hash()
                if expected_config_hash is None
                else expected_config_hash
            )
            or evidence.payload.model_identity
            != (
                manifest.payload.adapter.expected_model_identity
                if expected_model_identity is None
                else expected_model_identity
            )
        ):
            raise ValueError("operational evidence does not match active block")
        if evidence_type != "gpu_load_failure" and not evidence.payload.success:
            raise ValueError("required operational evidence did not succeed")
        return evidence

    @staticmethod
    def _block_zero_manifest(
        records: tuple[object, ...], plan: ExperimentPlan
    ) -> ManifestEnvelope:
        matches = [
            record
            for record in records
            if isinstance(record, ManifestEnvelope)
            and record.payload.experiment_id == plan.experiment_id
            and record.payload.run_id == plan.run_id
            and record.payload.block_index == 0
        ]
        if len(matches) != 1:
            raise ValueError(
                "block transition requires exactly one block-zero manifest"
            )
        return matches[0]

    @staticmethod
    def _completion_record_id(plan: ExperimentPlan, block_index: int) -> str:
        return f"block-completed-{plan.experiment_id}-{plan.run_id}-{block_index}"

    @staticmethod
    def _trial_set_hash(records: list[TrialEnvelope]) -> str:
        canonical = json.dumps(
            [
                record.model_dump(mode="json")
                for record in sorted(records, key=lambda item: item.record_id)
            ],
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return sha256_text(canonical)

    @staticmethod
    def _validate_completion(
        completion: OperationalEvidenceEnvelope,
        records: tuple[object, ...],
        manifest: ManifestEnvelope,
        plan: PlanEnvelope,
        expected_trial_count: int,
    ) -> None:
        trials = [
            record
            for record in records
            if isinstance(record, TrialEnvelope)
            and record.payload.manifest_record_id == manifest.record_id
            and record.payload.plan_record_id == plan.record_id
            and record.payload.block_index == manifest.payload.block_index
        ]
        payload = completion.payload
        durable_schedule_hash = canonical_persisted_schedule_hash(
            tuple(record.payload.request_settings for record in trials)
        )
        canonical_trial_ids = all(
            record.record_id
            == ComparisonService._record_id_from_settings(
                record.payload.request_settings,
                manifest.payload.adapter.expected_model_identity,
            )
            for record in trials
        )
        if (
            completion.record_id
            != ComparisonService._completion_record_id(
                plan.payload, manifest.payload.block_index
            )
            or payload.evidence_type != "block_completed"
            or payload.model_identity
            != manifest.payload.adapter.expected_model_identity
            or payload.generation_config_hash
            != manifest.payload.generation.configuration_hash()
            or payload.plan_record_id != plan.record_id
            or payload.plan_hash != plan.plan_hash
            or payload.request_schedule_hash != plan.payload.request_schedule_hash
            or payload.durable_trial_count != expected_trial_count
            or len(trials) != expected_trial_count
            or durable_schedule_hash != plan.payload.request_schedule_hash
            or not canonical_trial_ids
            or payload.durable_trial_set_hash
            != ComparisonService._trial_set_hash(trials)
        ):
            raise ValueError("block completion evidence failed durable authentication")

    @staticmethod
    def _validate_block_requests(
        requests: tuple[BaselineRequest, ...], plan: ExperimentPlan
    ) -> None:
        if len({request.trial_id for request in requests}) != len(requests):
            raise ValueError("trial identifiers must be unique within a block")
        observed_cases = tuple(
            dict.fromkeys(request.prompt_case_id for request in requests)
        )
        if observed_cases != plan.ordered_case_ids:
            raise ValueError(
                "request cases do not follow the frozen deterministic order"
            )
        case_hashes: list[tuple[str, str]] = []
        for case_id in observed_cases:
            hashes = {
                request.prompt_hash
                for request in requests
                if request.prompt_case_id == case_id
            }
            if len(hashes) != 1:
                raise ValueError(
                    "all trials for a case must use the same frozen prompt"
                )
            case_hashes.append((case_id, hashes.pop()))
        if canonical_prompt_suite_hash(tuple(case_hashes)) != plan.prompt_suite_hash:
            raise ValueError("block prompts do not match the frozen prompt-suite hash")
        if canonical_request_schedule_hash(requests) != plan.request_schedule_hash:
            raise ValueError("block requests do not match the frozen request schedule")
        if plan.mode == "heldout":
            counts = {
                case_id: sum(request.prompt_case_id == case_id for request in requests)
                for case_id in plan.ordered_case_ids
            }
            if any(count != plan.measured_trials_per_case for count in counts.values()):
                raise ValueError(
                    "held-out blocks require exactly three trials per case"
                )

    def _manifest_for(self, record_id: str) -> ManifestEnvelope:
        matches = [
            record
            for record in self._store.read_all()
            if isinstance(record, ManifestEnvelope) and record.record_id == record_id
        ]
        if len(matches) != 1:
            raise ValueError("target requires exactly one persisted manifest")
        return matches[0]

    @staticmethod
    def _validate_request_manifest(
        request: BaselineRequest, manifest: ManifestEnvelope
    ) -> None:
        if (
            request.experiment_id != manifest.payload.experiment_id
            or request.run_id != manifest.payload.run_id
        ):
            raise ValueError("request identity does not match persisted manifest")

    @staticmethod
    def _record_id(request: BaselineRequest, target_id: str) -> str:
        return ComparisonService._record_id_from_settings(
            TrialRequestSettings.from_request(request), target_id
        )

    @staticmethod
    def _record_id_from_settings(settings: TrialRequestSettings, target_id: str) -> str:
        material = json.dumps(
            {
                "experiment_id": settings.experiment_id,
                "generation_fingerprint": settings.generation_fingerprint(),
                "prompt_case_id": settings.prompt_case_id,
                "prompt_suite_id": settings.prompt_suite_id,
                "run_id": settings.run_id,
                "target_id": target_id,
                "trial_id": settings.trial_id,
            },
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return "trial-" + hashlib.sha256(material.encode("utf-8")).hexdigest()
