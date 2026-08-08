from __future__ import annotations

import json
from collections import deque
from datetime import UTC, datetime, timedelta, timezone
from email.message import Message
from pathlib import Path
from typing import Mapping

import pytest
from pydantic import ValidationError

from llm_comparison.client import LlamaServerClient
from llm_comparison.models import (
    AdapterConfig,
    ArtifactShard,
    BaselineRequest,
    BlindedEvaluation,
    EvaluationEnvelope,
    Envelope,
    ExperimentPlan,
    FailedObservation,
    GenerationConfiguration,
    IdentityMapping,
    IdentityMappingEnvelope,
    ManifestEnvelope,
    Metric,
    ModelProvenance,
    OperationalEvidence,
    OperationalEvidenceEnvelope,
    PlanEnvelope,
    ReadinessObservation,
    RubricScore,
    RunManifest,
    RuntimeProvenance,
    SuccessfulObservation,
    TrialEnvelope,
    TrialObservation,
    TrialRequestSettings,
    canonical_request_schedule_hash,
    canonical_prompt_suite_hash,
)
from llm_comparison.ports import HttpResponse, ModelClientError
from llm_comparison.service import ComparisonService, ComparisonTarget
from llm_comparison.storage import (
    CorruptJsonlError,
    DuplicateRecordError,
    RecordConflictError,
    WindowsJsonlStore,
)
from llm_comparison.transport import (
    MAX_RESPONSE_BYTES,
    UrllibHttpTransport,
    build_local_opener,
)


class FakeClock:
    def __init__(
        self,
        monotonic_values: tuple[float, ...] = (1.0, 1.1, 10.0, 10.25),
    ) -> None:
        self.values = deque(monotonic_values)

    def monotonic(self) -> float:
        return self.values.popleft()

    def utc_now(self) -> datetime:
        return datetime(2026, 8, 8, 12, 0, tzinfo=UTC)


class FakeTransport:
    def __init__(self, responses: tuple[HttpResponse | BaseException, ...]) -> None:
        self.responses = deque(responses)
        self.requests: list[tuple[str, str, bytes | None]] = []

    def request(
        self,
        *,
        method: str,
        url: str,
        headers: Mapping[str, str],
        body: bytes | None,
        timeout_seconds: float,
    ) -> HttpResponse:
        self.requests.append((method, url, body))
        response = self.responses.popleft()
        if isinstance(response, BaseException):
            raise response
        return response


def response(status: int, body: object) -> HttpResponse:
    return HttpResponse(status, json.dumps(body).encode(), {})


def make_manifest(identity: str = "qwen-local") -> RunManifest:
    is_large = identity == "large"
    artifacts = (
        (
            ArtifactShard(
                order=0,
                filename="qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf",
                sha256="a" * 64,
                size_bytes=10,
            ),
            ArtifactShard(
                order=1,
                filename="qwen2.5-7b-instruct-q4_k_m-00002-of-00002.gguf",
                sha256="b" * 64,
                size_bytes=11,
            ),
        )
        if is_large
        else (
            ArtifactShard(
                order=0,
                filename="qwen2.5-1.5b-instruct-q4_k_m.gguf",
                sha256="a" * 64,
                size_bytes=10,
            ),
        )
    )
    return RunManifest(
        experiment_id="exp-1",
        run_id="run-1",
        created_at=datetime(2026, 8, 8, tzinfo=UTC),
        adapter=AdapterConfig(
            base_url="http://127.0.0.1:8080",
            expected_model_identity=identity,
            adapter_version="1",
        ),
        runtime=RuntimeProvenance(
            runtime_revision="commit-abc",
            runtime_binary_sha256="c" * 64,
            server_arguments=(
                "--host",
                "127.0.0.1",
                "--ctx-size",
                "4096",
                "--n-gpu-layers",
                "99",
            ),
            os_version="Windows 11",
            gpu_model="RTX 3070 Ti",
            gpu_vram_bytes=8_000_000_000,
            system_ram_bytes=16_000_000_000,
            nvidia_driver_version="pinned-driver",
            cuda_backend="runtime-reported-cuda",
            cpu_threads=8,
            harness_version="1",
        ),
        model=ModelProvenance(
            source_repository=(
                "Qwen/Qwen2.5-7B-Instruct-GGUF"
                if is_large
                else "Qwen/Qwen2.5-1.5B-Instruct-GGUF"
            ),
            repository_revision="revision-abc",
            artifacts=artifacts,
            quantization="Q4_K_M",
            declared_license="Apache-2.0",
            verified_license_revision="license-revision",
            chat_template_identity="qwen2.5",
            chat_template_sha256="b" * 64,
            tokenizer_identity="qwen2.5-tokenizer",
            tokenizer_sha256="d" * 64,
        ),
        generation=GenerationConfiguration(
            requested_gpu_layers=99,
            effective_gpu_layers=99,
            cache_policy="runtime default; not reset",
            warmup_policy="one unmeasured request",
        ),
        block_index=0,
        readiness=ReadinessObservation(
            elapsed_seconds=None, unavailable_reason="not captured in unit fixture"
        ),
        startup_evidence_id=f"startup-{identity}",
        readiness_evidence_id=f"readiness-{identity}",
        warmup_evidence_id=f"warmup-{identity}",
    )


def make_request(**changes: object) -> BaselineRequest:
    values: dict[str, object] = {
        "experiment_id": "exp-1",
        "run_id": "run-1",
        "trial_id": "trial-1",
        "prompt_suite_id": "heldout-v1",
        "prompt_case_id": "case-1",
        "prompt": "Explain one fact.",
        "temperature": 0.2,
        "top_k": 40,
        "top_p": 0.9,
        "seed": 7,
        "timeout_seconds": 30.0,
    }
    values.update(changes)
    return BaselineRequest.model_validate(values)


def make_plan() -> ExperimentPlan:
    small = make_manifest("small")
    large = make_manifest("large")
    selected_suite_hash = canonical_prompt_suite_hash(
        (("case-1", make_request().prompt_hash),)
    )
    return ExperimentPlan(
        experiment_id="exp-1",
        run_id="run-1",
        mode="calibration",
        model_repositories=(
            "Qwen/Qwen2.5-1.5B-Instruct-GGUF",
            "Qwen/Qwen2.5-7B-Instruct-GGUF",
        ),
        prompt_suite_hash=selected_suite_hash,
        request_schedule_hash=canonical_request_schedule_hash((make_request(),)),
        calibration_suite_hash=selected_suite_hash,
        heldout_suite_hash="c" * 64,
        reference_material_hash="d" * 64,
        rubric_hash="e" * 64,
        calibration_case_ids=("case-1",),
        heldout_case_ids=("held-1",),
        ordered_case_ids=("case-1",),
        ordering_seed=7,
        measured_run=False,
        runtime_revision="commit-abc",
        runtime_binary_sha256="c" * 64,
        artifact_revisions=("revision-abc", "revision-abc"),
        artifact_set_hashes=(
            small.model.artifact_set_hash(),
            large.model.artifact_set_hash(),
        ),
        generation_config_hashes=(
            small.generation.configuration_hash(),
            large.generation.configuration_hash(),
        ),
        adapter_versions=(small.adapter.adapter_version, large.adapter.adapter_version),
        chat_template_hashes=(
            small.model.chat_template_sha256,
            large.model.chat_template_sha256,
        ),
        tokenizer_hashes=(small.model.tokenizer_sha256, large.model.tokenizer_sha256),
    )


def successful_result(
    model_identity: str = "qwen-local", request: BaselineRequest | None = None
) -> SuccessfulObservation:
    request = request if request is not None else make_request()
    return SuccessfulObservation(
        experiment_id=request.experiment_id,
        run_id=request.run_id,
        trial_id=request.trial_id,
        prompt_suite_id=request.prompt_suite_id,
        prompt_case_id=request.prompt_case_id,
        prompt_hash=request.prompt_hash,
        generation_fingerprint=request.generation_fingerprint(),
        model_identity=model_identity,
        started_at=datetime(2026, 8, 8, tzinfo=UTC),
        elapsed_seconds=0.25,
        metrics=(
            Metric(
                name="request_wall_time",
                value=0.25,
                unit="seconds",
                boundary="request",
                source="client_observed",
            ),
        ),
        generated_text="answer",
        finish_reason="stop",
        raw_finish_reason="stop",
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"prompt": "   "},
        {"temperature": float("nan")},
        {"top_p": float("inf")},
        {"context_size": 8192},
        {"max_output_tokens": 511},
        {"stream": True},
        {"prompt_hash": "0" * 64},
    ],
)
def test_baseline_request_enforces_canonical_constraints(
    changes: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        make_request(**changes)


def test_baseline_request_derives_hash_and_configuration_fingerprint() -> None:
    original = make_request()
    changed = make_request(temperature=0.3)

    assert len(original.prompt_hash) == 64
    assert original.generation_fingerprint() != changed.generation_fingerprint()


def test_generation_fingerprint_is_unambiguous_for_control_characters() -> None:
    left = make_request(stop=("a\x1fb", "c"))
    right = make_request(stop=("a", "b\x1fc"))

    assert left.generation_fingerprint() != right.generation_fingerprint()


def test_timeout_changes_fingerprint() -> None:
    assert (
        make_request(timeout_seconds=1.0).generation_fingerprint()
        != make_request(timeout_seconds=2.0).generation_fingerprint()
    )


def test_local_opener_disables_proxies_and_rejects_redirects() -> None:
    opener = build_local_opener()
    assert opener.proxies_disabled is True
    assert opener.redirects_disabled is True


class BoundedResponse:
    def __init__(self, body: bytes, content_length: str | None = None) -> None:
        self.body = body
        self.headers = Message()
        if content_length is not None:
            self.headers["Content-Length"] = content_length
        self.read_sizes: list[int] = []

    def read(self, size: int) -> bytes:
        self.read_sizes.append(size)
        return self.body[:size]


def test_transport_bounded_read_never_requests_an_unbounded_body() -> None:
    exact = BoundedResponse(b"x" * MAX_RESPONSE_BYTES, str(MAX_RESPONSE_BYTES))
    assert len(UrllibHttpTransport._bounded_read(exact)) == MAX_RESPONSE_BYTES
    assert exact.read_sizes == [MAX_RESPONSE_BYTES + 1]

    with pytest.raises(OSError, match="exceeds"):
        UrllibHttpTransport._bounded_read(
            BoundedResponse(b"x", str(MAX_RESPONSE_BYTES + 1))
        )
    with pytest.raises(OSError, match="exceeds"):
        UrllibHttpTransport._bounded_read(
            BoundedResponse(b"x" * (MAX_RESPONSE_BYTES + 1))
        )


@pytest.mark.parametrize(
    "url",
    [
        "https://127.0.0.1:8080",
        "http://192.168.1.2:8080",
        "http://127.0.0.1",
        "http://user:pass@127.0.0.1:8080",
        "http://127.0.0.1:8080/path",
        "http://127.0.0.1:8080?next=remote",
        "http://localhost:8080",
        "http://[::1]:8080",
        "http://127.1:8080",
    ],
)
def test_adapter_config_rejects_non_loopback_origins(url: str) -> None:
    with pytest.raises(ValidationError):
        AdapterConfig(
            base_url=url,
            expected_model_identity="model",
            adapter_version="1",
        )


def test_manifest_rejects_unordered_artifact_attestation() -> None:
    with pytest.raises(ValidationError):
        ModelProvenance(
            source_repository="Qwen/Qwen2.5-1.5B-Instruct-GGUF",
            repository_revision="rev",
            artifacts=(
                ArtifactShard(order=1, filename="x", sha256="a" * 64, size_bytes=1),
            ),
            quantization="Q4_K_M",
            declared_license="Apache-2.0",
            verified_license_revision="rev",
            chat_template_identity="template",
            chat_template_sha256="b" * 64,
            tokenizer_identity="tokenizer",
            tokenizer_sha256="c" * 64,
        )


def test_manifest_envelope_rejects_mismatched_identity() -> None:
    with pytest.raises(ValidationError):
        ManifestEnvelope(
            record_id="manifest-1",
            experiment_id="different",
            run_id="run-1",
            trial_id="manifest",
            payload=make_manifest(),
        )


def test_runtime_records_require_utc_and_bounded_gpu_offload() -> None:
    manifest_values = make_manifest().model_dump()
    manifest_values["created_at"] = datetime(
        2026, 8, 8, tzinfo=timezone(timedelta(hours=5, minutes=30))
    )
    with pytest.raises(ValidationError):
        RunManifest.model_validate(manifest_values)

    with pytest.raises(ValidationError):
        GenerationConfiguration(
            requested_gpu_layers=10,
            effective_gpu_layers=11,
            cache_policy="runtime default",
            warmup_policy="one request",
        )


def test_observation_and_evaluation_timestamps_require_utc() -> None:
    result_values = successful_result().model_dump()
    result_values["started_at"] = datetime(2026, 8, 8)
    with pytest.raises(ValidationError):
        SuccessfulObservation.model_validate(result_values)

    with pytest.raises(ValidationError):
        BlindedEvaluation(
            blinded_output_id="opaque-1",
            rubric_version="v1",
            evaluator_id="human-1",
            evaluated_at=datetime(2026, 8, 8),
            scores=(RubricScore(criterion="correctness", score=2),),
            notes="note",
            uncertainty="low",
        )


def completion_transport(*, include_usage: bool = True) -> FakeTransport:
    completion: dict[str, object] = {
        "model": "qwen-local",
        "choices": [{"message": {"content": "hello"}, "finish_reason": "stop"}],
    }
    if include_usage:
        completion["usage"] = {"prompt_tokens": 5, "completion_tokens": 2}
        completion["timings"] = {"prompt_ms": 4.5, "predicted_ms": 10.0}
    return FakeTransport(
        (
            response(200, {"status": "ok"}),
            response(200, {"data": [{"id": "qwen-local"}]}),
            response(200, completion),
        )
    )


def test_client_sends_minimal_non_streaming_request_and_parses_metrics() -> None:
    transport = completion_transport()
    result = LlamaServerClient(
        manifest=make_manifest(), transport=transport, clock=FakeClock()
    ).generate(make_request())

    assert result.outcome == "success"
    assert result.generated_text == "hello"
    sent = json.loads(transport.requests[-1][2] or b"{}")
    assert "stop" not in sent
    assert sent["stream"] is False
    assert sent["max_tokens"] == 512
    assert {metric.name for metric in result.metrics} >= {
        "request_wall_time",
        "prompt_tokens",
        "completion_tokens",
        "prompt_ms",
        "predicted_ms",
    }
    wall_time = next(
        metric for metric in result.metrics if metric.name == "request_wall_time"
    )
    assert wall_time.value == 0.25


def test_client_marks_unexposed_metrics_unavailable() -> None:
    result = LlamaServerClient(
        manifest=make_manifest(),
        transport=completion_transport(include_usage=False),
        clock=FakeClock(),
    ).generate(make_request())

    unavailable = {metric.name: metric.unavailable_reason for metric in result.metrics}
    assert unavailable["prompt_tokens"] == "runtime_missing_or_invalid_prompt_tokens"
    assert unavailable["predicted_ms"] == "runtime_missing_or_invalid_predicted_ms"
    assert unavailable["time_to_first_token"] is not None


def test_client_returns_sanitized_timed_protocol_failure() -> None:
    secret = "SECRET RESPONSE BODY"
    transport = FakeTransport(
        (
            response(200, {"status": "ok"}),
            response(200, {"data": [{"id": "qwen-local"}]}),
            HttpResponse(200, secret.encode(), {}),
        )
    )
    result = LlamaServerClient(
        manifest=make_manifest(),
        transport=transport,
        clock=FakeClock((1.0, 1.1, 2.0, 2.75)),
    ).generate(make_request())

    assert result.outcome == "failure"
    assert result.category == "protocol"
    assert result.elapsed_seconds == 0.75
    assert secret not in result.sanitized_detail


def test_client_preserves_timeout_without_claiming_server_cancellation() -> None:
    transport = FakeTransport(
        (
            response(200, {}),
            response(200, {"data": [{"id": "qwen-local"}]}),
            TimeoutError(),
        )
    )
    result = LlamaServerClient(
        manifest=make_manifest(),
        transport=transport,
        clock=FakeClock((0.0, 0.1, 1.0, 1.5)),
    ).generate(make_request())

    assert result.outcome == "failure"
    assert result.category == "timeout"
    assert result.finish_reason == "error"


class MemoryStore:
    def __init__(self) -> None:
        self.records: list[Envelope] = [make_plan_envelope()]

    def append(self, envelope: Envelope) -> bool:
        self.records.append(envelope)
        return True

    def read_all(self) -> tuple[Envelope, ...]:
        return tuple(self.records)


class FixedClient:
    def __init__(self, identity: str) -> None:
        self.identity = identity

    def generate(self, request: BaselineRequest) -> SuccessfulObservation:
        return successful_result(self.identity, request)


class FailingClient:
    def generate(self, request: BaselineRequest) -> FailedObservation:
        return FailedObservation(
            experiment_id=request.experiment_id,
            run_id=request.run_id,
            trial_id=request.trial_id,
            prompt_suite_id=request.prompt_suite_id,
            prompt_case_id=request.prompt_case_id,
            prompt_hash=request.prompt_hash,
            generation_fingerprint=request.generation_fingerprint(),
            model_identity="failed-model",
            started_at=datetime(2026, 8, 8, tzinfo=UTC),
            elapsed_seconds=0.5,
            metrics=(
                Metric(
                    name="request_wall_time",
                    value=0.5,
                    unit="seconds",
                    boundary="request",
                    source="client_observed",
                ),
            ),
            category="server",
            sanitized_detail="completion_status_500",
        )


class ExpectedErrorThenSuccessClient:
    def __init__(self) -> None:
        self.calls = 0

    def generate(self, request: BaselineRequest) -> SuccessfulObservation:
        self.calls += 1
        if self.calls == 1:
            raise ModelClientError("transport", "connection_failed")
        return successful_result("small", request)


class ExplodingClient:
    def generate(self, request: BaselineRequest) -> SuccessfulObservation:
        raise RuntimeError("must not regenerate a durable trial")


def test_comparison_service_persists_each_target_with_collision_safe_ids() -> None:
    store = MemoryStore()
    store.append(make_manifest_envelope("manifest-small", "small", 0))
    store.append(make_manifest_envelope("manifest-large", "large", 1))
    service = ComparisonService(store=store, clock=FakeClock())

    first_records = service.run_target_block(
        ComparisonTarget(FixedClient("small"), "manifest-small", "small", "1", 0),
        (make_request(),),
        "plan-1",
    )
    store.append(
        make_evidence_envelope(
            record_id="shutdown-small",
            evidence_type="server_shutdown",
            identity="small",
            block_index=0,
            observed_at=datetime(2026, 8, 8, 13, 0, tzinfo=UTC),
        )
    )
    second_records = service.run_target_block(
        ComparisonTarget(FixedClient("large"), "manifest-large", "large", "1", 1),
        (make_request(),),
        "plan-1",
    )
    records = first_records + second_records

    assert len(records) == 2
    assert records[0].record_id != records[1].record_id
    assert {record.payload.result.model_identity for record in records} == {
        "small",
        "large",
    }


def test_comparison_service_preserves_success_and_failure_independently() -> None:
    store = MemoryStore()
    store.append(make_manifest_envelope("manifest-failed", "failed-model", 0))
    service = ComparisonService(store=store, clock=FakeClock())

    records = service.run_target_block(
        ComparisonTarget(FailingClient(), "manifest-failed", "failed-model", "1", 0),
        (make_request(),),
        "plan-1",
    )

    assert [record.payload.result.outcome for record in records] == ["failure"]


def test_comparison_service_requires_persisted_manifests() -> None:
    service = ComparisonService(store=MemoryStore(), clock=FakeClock())

    with pytest.raises(ValueError, match="persisted manifest"):
        service.run_target_block(
            ComparisonTarget(FixedClient("small"), "missing-manifest", "small", "1", 0),
            (make_request(),),
            "plan-1",
        )


def test_expected_client_error_is_sanitized_and_block_continues() -> None:
    store = MemoryStore()
    store.append(make_manifest_envelope("manifest-small", "small", 0))
    service = ComparisonService(store=store, clock=FakeClock())
    requests = (make_request(trial_id="trial-1"), make_request(trial_id="trial-2"))
    two_plan = ExperimentPlan.model_validate(
        {
            **make_plan().model_dump(),
            "request_schedule_hash": canonical_request_schedule_hash(requests),
        }
    )
    store.append(
        PlanEnvelope(
            record_id="plan-two",
            experiment_id="exp-1",
            run_id="run-1",
            trial_id="plan",
            payload=two_plan,
        )
    )

    records = service.run_target_block(
        ComparisonTarget(
            ExpectedErrorThenSuccessClient(), "manifest-small", "small", "1", 0
        ),
        requests,
        "plan-two",
    )

    assert [record.payload.result.outcome for record in records] == [
        "failure",
        "success",
    ]
    assert records[0].payload.result.outcome == "failure"
    assert records[0].payload.result.sanitized_detail == "connection_failed"


def test_block_rejects_out_of_range_index_and_changed_prompt_suite() -> None:
    store = MemoryStore()
    store.append(make_manifest_envelope("manifest-small", "small", 0))
    service = ComparisonService(store=store, clock=FakeClock())
    with pytest.raises(ValueError, match="zero or one"):
        service.run_target_block(
            ComparisonTarget(FixedClient("small"), "manifest-small", "small", "1", 2),
            (make_request(),),
            "plan-1",
        )
    with pytest.raises(ValueError, match="prompt-suite hash"):
        service.run_target_block(
            ComparisonTarget(FixedClient("small"), "manifest-small", "small", "1", 0),
            (make_request(prompt="Changed frozen prompt"),),
            "plan-1",
        )


def test_trial_observation_rejects_request_result_mismatch() -> None:
    request = make_request(temperature=0.3)
    with pytest.raises(ValidationError, match="settings do not match"):
        TrialObservation(
            manifest_record_id="manifest-small",
            plan_record_id="plan-1",
            plan_hash=make_plan().canonical_hash(),
            request_settings=TrialRequestSettings.from_request(request),
            block_index=0,
            result=successful_result("small", make_request(temperature=0.4)),
        )


def test_measured_experiment_plan_rejects_unresolved_pins() -> None:
    with pytest.raises(ValidationError, match="resolved"):
        ExperimentPlan(
            experiment_id="exp-1",
            run_id="run-1",
            mode="heldout",
            model_repositories=(
                "Qwen/Qwen2.5-1.5B-Instruct-GGUF",
                "Qwen/Qwen2.5-7B-Instruct-GGUF",
            ),
            prompt_suite_hash="c" * 64,
            request_schedule_hash="a" * 64,
            calibration_suite_hash="b" * 64,
            heldout_suite_hash="c" * 64,
            reference_material_hash="d" * 64,
            rubric_hash="e" * 64,
            calibration_case_ids=("cal-1",),
            heldout_case_ids=("held-1",),
            ordered_case_ids=("held-1",),
            ordering_seed=7,
            measured_run=True,
            runtime_revision="UNRESOLVED-runtime",
            runtime_binary_sha256="0" * 64,
            artifact_revisions=("rev-1", "rev-2"),
            artifact_set_hashes=("3" * 64, "4" * 64),
            generation_config_hashes=("5" * 64, "6" * 64),
            adapter_versions=("1", "1"),
            chat_template_hashes=("7" * 64, "8" * 64),
            tokenizer_hashes=("9" * 64, "a" * 64),
        )


def test_plan_enforces_mode_cases_and_selected_suite_hash() -> None:
    values = make_plan().model_dump()
    with pytest.raises(ValidationError, match="calibration plans cannot"):
        ExperimentPlan.model_validate({**values, "measured_run": True})
    with pytest.raises(ValidationError, match="exactly match"):
        ExperimentPlan.model_validate(
            {**values, "ordered_case_ids": ("case-1", "case-2")}
        )
    with pytest.raises(ValidationError, match="selected plan mode"):
        ExperimentPlan.model_validate({**values, "prompt_suite_hash": "9" * 64})


def test_plan_hash_is_stable_and_changes_with_frozen_fields() -> None:
    plan = make_plan()
    restored = ExperimentPlan.model_validate_json(plan.model_dump_json())
    changed = ExperimentPlan.model_validate(
        {**plan.model_dump(), "ordering_seed": plan.ordering_seed + 1}
    )

    assert restored.canonical_hash() == plan.canonical_hash()
    assert changed.canonical_hash() != plan.canonical_hash()
    envelope = make_plan_envelope()
    assert envelope.plan_hash == plan.canonical_hash()


def test_locked_artifact_structure_and_hash_are_content_sensitive() -> None:
    small = make_manifest("small").model
    changed_values = small.model_dump()
    changed_values["artifacts"] = (
        {**changed_values["artifacts"][0], "size_bytes": 99},
    )
    changed = ModelProvenance.model_validate(changed_values)
    assert changed.artifact_set_hash() != small.artifact_set_hash()

    invalid_large = make_manifest("large").model.model_dump()
    invalid_large["artifacts"] = tuple(reversed(invalid_large["artifacts"]))
    with pytest.raises(ValidationError):
        ModelProvenance.model_validate(invalid_large)


def test_operational_evidence_enforces_event_semantics() -> None:
    base = {
        "observed_at": datetime(2026, 8, 8, tzinfo=UTC),
        "model_identity": "small",
        "block_index": 0,
        "generation_config_hash": make_manifest(
            "small"
        ).generation.configuration_hash(),
        "safe_detail_code": "recorded",
    }
    with pytest.raises(ValidationError):
        OperationalEvidence.model_validate(
            {
                **base,
                "evidence_type": "warmup_completed",
                "success": True,
                "attempted_gpu_layers": 99,
            }
        )
    with pytest.raises(ValidationError):
        OperationalEvidence.model_validate(
            {
                **base,
                "evidence_type": "gpu_load_failure",
                "success": True,
                "attempted_gpu_layers": 99,
            }
        )


def test_partial_block_recovery_does_not_regenerate_durable_trials() -> None:
    store = MemoryStore()
    store.append(make_manifest_envelope("manifest-small", "small", 0))
    service = ComparisonService(store=store, clock=FakeClock())
    target = ComparisonTarget(FixedClient("small"), "manifest-small", "small", "1", 0)
    first = service.run_target_block(target, (make_request(),), "plan-1")
    assert store.records[-1].record_type == "operational_evidence"
    store.records.pop()

    recovered = service.run_target_block(
        ComparisonTarget(ExplodingClient(), "manifest-small", "small", "1", 0),
        (make_request(),),
        "plan-1",
    )

    assert recovered == first


def test_frozen_schedule_rejects_timeout_mutation_before_client_call() -> None:
    store = MemoryStore()
    store.append(make_manifest_envelope("manifest-small", "small", 0))
    with pytest.raises(ValueError, match="frozen request schedule"):
        ComparisonService(store=store, clock=FakeClock()).run_target_block(
            ComparisonTarget(ExplodingClient(), "manifest-small", "small", "1", 0),
            (make_request(timeout_seconds=31.0),),
            "plan-1",
        )


def test_frozen_schedule_includes_prompt_suite_identifier() -> None:
    store = MemoryStore()
    store.append(make_manifest_envelope("manifest-small", "small", 0))
    with pytest.raises(ValueError, match="frozen request schedule"):
        ComparisonService(store=store, clock=FakeClock()).run_target_block(
            ComparisonTarget(ExplodingClient(), "manifest-small", "small", "1", 0),
            (make_request(prompt_suite_id="different-suite"),),
            "plan-1",
        )


def test_plan_run_must_match_manifest_run() -> None:
    store = MemoryStore()
    store.append(make_manifest_envelope("manifest-small", "small", 0))
    other_plan = ExperimentPlan.model_validate(
        {**make_plan().model_dump(), "run_id": "run-2"}
    )
    store.append(
        PlanEnvelope(
            record_id="plan-run-2",
            experiment_id="exp-1",
            run_id="run-2",
            trial_id="plan",
            payload=other_plan,
        )
    )
    with pytest.raises(ValueError, match="experiment plan"):
        ComparisonService(store=store, clock=FakeClock()).run_target_block(
            ComparisonTarget(ExplodingClient(), "manifest-small", "small", "1", 0),
            (make_request(),),
            "plan-run-2",
        )


def test_arbitrary_completion_evidence_cannot_block_recovery() -> None:
    store = MemoryStore()
    manifest = make_manifest_envelope("manifest-small", "small", 0)
    store.append(manifest)
    plan = make_plan_envelope()
    store.append(
        OperationalEvidenceEnvelope(
            record_id="forged-noncanonical-completion",
            experiment_id="exp-1",
            run_id="run-1",
            trial_id="block-completion",
            payload=OperationalEvidence(
                evidence_type="block_completed",
                observed_at=datetime(2026, 8, 8, 11, 0, tzinfo=UTC),
                model_identity="small",
                block_index=0,
                generation_config_hash=manifest.payload.generation.configuration_hash(),
                success=True,
                safe_detail_code="forged",
                plan_record_id=plan.record_id,
                plan_hash=plan.plan_hash,
                request_schedule_hash=plan.payload.request_schedule_hash,
                durable_trial_count=0,
                durable_trial_set_hash="0" * 64,
            ),
        )
    )

    records = ComparisonService(store=store, clock=FakeClock()).run_target_block(
        ComparisonTarget(FixedClient("small"), "manifest-small", "small", "1", 0),
        (make_request(),),
        "plan-1",
    )

    assert len(records) == 1


def test_canonical_completion_requires_authenticated_durable_trial_set() -> None:
    store = MemoryStore()
    manifest = make_manifest_envelope("manifest-small", "small", 0)
    store.append(manifest)
    plan = make_plan_envelope()
    store.append(
        OperationalEvidenceEnvelope(
            record_id="block-completed-exp-1-run-1-0",
            experiment_id="exp-1",
            run_id="run-1",
            trial_id="block-completion",
            payload=OperationalEvidence(
                evidence_type="block_completed",
                observed_at=datetime(2026, 8, 8, 11, 0, tzinfo=UTC),
                model_identity="small",
                block_index=0,
                generation_config_hash=manifest.payload.generation.configuration_hash(),
                success=True,
                safe_detail_code="forged",
                plan_record_id=plan.record_id,
                plan_hash=plan.plan_hash,
                request_schedule_hash=plan.payload.request_schedule_hash,
                durable_trial_count=1,
                durable_trial_set_hash="0" * 64,
            ),
        )
    )

    with pytest.raises(ValueError, match="durable authentication"):
        ComparisonService(store=store, clock=FakeClock()).run_target_block(
            ComparisonTarget(ExplodingClient(), "manifest-small", "small", "1", 0),
            (make_request(),),
            "plan-1",
        )


def test_recomputed_trial_set_cannot_hide_block_zero_schedule_mutation() -> None:
    store = MemoryStore()
    small_manifest = make_manifest_envelope("manifest-small", "small", 0)
    large_manifest = make_manifest_envelope("manifest-large", "large", 1)
    store.append(small_manifest)
    store.append(large_manifest)
    plan = make_plan_envelope()
    mutated_request = make_request(temperature=0.9)
    mutated_trial = TrialEnvelope(
        record_id=ComparisonService._record_id(mutated_request, "small"),
        experiment_id="exp-1",
        run_id="run-1",
        trial_id=mutated_request.trial_id,
        payload=TrialObservation(
            manifest_record_id="manifest-small",
            plan_record_id="plan-1",
            plan_hash=plan.plan_hash,
            request_settings=TrialRequestSettings.from_request(mutated_request),
            block_index=0,
            result=successful_result("small", mutated_request),
        ),
    )
    store.append(mutated_trial)
    store.append(
        OperationalEvidenceEnvelope(
            record_id="block-completed-exp-1-run-1-0",
            experiment_id="exp-1",
            run_id="run-1",
            trial_id="block-completion",
            payload=OperationalEvidence(
                evidence_type="block_completed",
                observed_at=datetime(2026, 8, 8, 12, 0, tzinfo=UTC),
                model_identity="small",
                block_index=0,
                generation_config_hash=small_manifest.payload.generation.configuration_hash(),
                success=True,
                safe_detail_code="forged_with_matching_set_hash",
                plan_record_id="plan-1",
                plan_hash=plan.plan_hash,
                request_schedule_hash=plan.payload.request_schedule_hash,
                durable_trial_count=1,
                durable_trial_set_hash=ComparisonService._trial_set_hash(
                    [mutated_trial]
                ),
            ),
        )
    )
    store.append(
        make_evidence_envelope(
            record_id="shutdown-small",
            evidence_type="server_shutdown",
            identity="small",
            block_index=0,
            observed_at=datetime(2026, 8, 8, 13, 0, tzinfo=UTC),
        )
    )

    with pytest.raises(ValueError, match="durable authentication"):
        ComparisonService(store=store, clock=FakeClock()).run_target_block(
            ComparisonTarget(ExplodingClient(), "manifest-large", "large", "1", 1),
            (make_request(),),
            "plan-1",
        )


def test_second_block_requires_first_completion_before_client_call() -> None:
    store = MemoryStore()
    store.append(make_manifest_envelope("manifest-small", "small", 0))
    store.append(make_manifest_envelope("manifest-large", "large", 1))
    store.append(
        make_evidence_envelope(
            record_id="shutdown-small",
            evidence_type="server_shutdown",
            identity="small",
            block_index=0,
            observed_at=datetime(2026, 8, 8, 13, 0, tzinfo=UTC),
        )
    )
    service = ComparisonService(store=store, clock=FakeClock())

    with pytest.raises(ValueError, match="first-block completion"):
        service.run_target_block(
            ComparisonTarget(FixedClient("large"), "manifest-large", "large", "1", 1),
            (make_request(),),
            "plan-1",
        )


def test_heldout_block_requires_durable_lifecycle_evidence() -> None:
    request = make_request(
        trial_id="trial-1", prompt_case_id="held-1", prompt="Frozen held-out prompt"
    )
    heldout_requests = tuple(
        request.model_copy(update={"trial_id": f"trial-{index}"})
        for index in range(1, 4)
    )
    suite_hash = canonical_prompt_suite_hash((("held-1", request.prompt_hash),))
    plan_values = make_plan().model_dump()
    heldout_plan = ExperimentPlan.model_validate(
        {
            **plan_values,
            "mode": "heldout",
            "measured_run": True,
            "prompt_suite_hash": suite_hash,
            "request_schedule_hash": canonical_request_schedule_hash(heldout_requests),
            "heldout_suite_hash": suite_hash,
            "ordered_case_ids": ("held-1",),
        }
    )
    plan_envelope = PlanEnvelope(
        record_id="plan-heldout",
        experiment_id="exp-1",
        run_id="run-1",
        trial_id="plan",
        payload=heldout_plan,
    )
    manifest = make_manifest("small").model_copy(
        update={
            "readiness": ReadinessObservation(elapsed_seconds=1.0),
            "block_index": 0,
        }
    )
    manifest_envelope = ManifestEnvelope(
        record_id="manifest-heldout",
        experiment_id="exp-1",
        run_id="run-1",
        trial_id="manifest",
        payload=manifest,
    )
    store = MemoryStore()
    store.append(plan_envelope)
    store.append(manifest_envelope)
    for evidence in (
        make_evidence_envelope(
            record_id="startup-small",
            evidence_type="startup",
            identity="small",
            block_index=0,
            observed_at=datetime(2026, 8, 7, 10, 0, tzinfo=UTC),
            elapsed_seconds=2.0,
        ),
        make_evidence_envelope(
            record_id="readiness-small",
            evidence_type="readiness",
            identity="small",
            block_index=0,
            observed_at=datetime(2026, 8, 7, 10, 1, tzinfo=UTC),
            elapsed_seconds=1.0,
        ),
        make_evidence_envelope(
            record_id="warmup-small",
            evidence_type="warmup_completed",
            identity="small",
            block_index=0,
            observed_at=datetime(2026, 8, 7, 10, 2, tzinfo=UTC),
        ),
    ):
        store.append(evidence)
    records = ComparisonService(store=store, clock=FakeClock()).run_target_block(
        ComparisonTarget(FixedClient("small"), "manifest-heldout", "small", "1", 0),
        heldout_requests,
        "plan-heldout",
    )

    assert len(records) == 3
    assert all(
        record.payload.plan_hash == plan_envelope.plan_hash for record in records
    )


def make_manifest_envelope(
    record_id: str = "manifest-1", identity: str = "qwen-local", block_index: int = 0
) -> ManifestEnvelope:
    return ManifestEnvelope(
        record_id=record_id,
        experiment_id="exp-1",
        run_id="run-1",
        trial_id="manifest",
        payload=make_manifest(identity).model_copy(
            update={
                "block_index": block_index,
                "prior_shutdown_evidence_id": (
                    "shutdown-small" if block_index == 1 else None
                ),
            }
        ),
    )


def make_evidence_envelope(
    *,
    record_id: str,
    evidence_type: str,
    identity: str,
    block_index: int,
    observed_at: datetime,
    elapsed_seconds: float | None = None,
) -> OperationalEvidenceEnvelope:
    manifest = make_manifest(identity)
    return OperationalEvidenceEnvelope.model_validate(
        {
            "record_id": record_id,
            "experiment_id": "exp-1",
            "run_id": "run-1",
            "trial_id": "operation",
            "payload": {
                "evidence_type": evidence_type,
                "observed_at": observed_at,
                "model_identity": identity,
                "block_index": block_index,
                "generation_config_hash": manifest.generation.configuration_hash(),
                "success": True,
                "safe_detail_code": "recorded",
                "elapsed_seconds": elapsed_seconds,
            },
        }
    )


def make_plan_envelope() -> PlanEnvelope:
    return PlanEnvelope(
        record_id="plan-1",
        experiment_id="exp-1",
        run_id="run-1",
        trial_id="plan",
        payload=make_plan(),
    )


def test_jsonl_round_trip_idempotency_and_conflict(tmp_path: Path) -> None:
    store = WindowsJsonlStore(tmp_path / "records.jsonl")
    record = make_manifest_envelope()

    assert store.append(record) is True
    assert store.append(record) is False
    assert store.read_all() == (record,)

    conflicting = record.model_copy(update={"trial_id": "changed"})
    with pytest.raises(RecordConflictError):
        store.append(conflicting)
    assert store.append(make_manifest_envelope("manifest-2")) is True


def test_jsonl_trial_round_trip_persists_generation_settings(tmp_path: Path) -> None:
    store = WindowsJsonlStore(tmp_path / "trial-records.jsonl")
    request = make_request(stop=("END",), temperature=0.3)
    plan = ExperimentPlan.model_validate(
        {
            **make_plan().model_dump(),
            "request_schedule_hash": canonical_request_schedule_hash((request,)),
        }
    )
    store.append(
        PlanEnvelope(
            record_id="plan-1",
            experiment_id="exp-1",
            run_id="run-1",
            trial_id="plan",
            payload=plan,
        )
    )
    store.append(make_manifest_envelope("manifest-small", "small"))
    service = ComparisonService(store=store, clock=FakeClock())

    service.run_target_block(
        ComparisonTarget(FixedClient("small"), "manifest-small", "small", "1", 0),
        (request,),
        "plan-1",
    )

    trial = store.read_all()[2]
    assert isinstance(trial, TrialEnvelope)
    assert trial.payload.request_settings.temperature == 0.3
    assert trial.payload.request_settings.stop == ("END",)
    assert trial.payload.request_settings.seed == 7
    assert trial.payload.request_settings.timeout_seconds == 30.0
    assert trial.payload.plan_record_id == "plan-1"
    assert trial.payload.plan_hash == plan.canonical_hash()


def test_jsonl_reports_exact_multibyte_corruption_offset(tmp_path: Path) -> None:
    path = tmp_path / "records.jsonl"
    store = WindowsJsonlStore(path)
    store.append(make_manifest_envelope())
    first_size = path.stat().st_size
    with path.open("ab") as output:
        output.write(b"{\xe2\x82\xac")

    with pytest.raises(CorruptJsonlError) as captured:
        store.read_all()

    assert captured.value.byte_offset == first_size


def test_jsonl_detects_duplicate_ids_on_read(tmp_path: Path) -> None:
    path = tmp_path / "records.jsonl"
    store = WindowsJsonlStore(path)
    store.append(make_manifest_envelope())
    line = path.read_bytes()
    with path.open("ab") as output:
        output.write(line)

    with pytest.raises(DuplicateRecordError):
        store.read_all()


def test_evaluation_and_identity_mapping_are_separate_versioned_envelopes(
    tmp_path: Path,
) -> None:
    store = WindowsJsonlStore(tmp_path / "evaluations.jsonl")
    evaluation = EvaluationEnvelope(
        record_id="evaluation-1",
        experiment_id="exp-1",
        run_id="run-1",
        trial_id="trial-1",
        payload=BlindedEvaluation(
            blinded_output_id="opaque-7",
            rubric_version="rubric-v1",
            evaluator_id="human-1",
            evaluated_at=datetime(2026, 8, 8, tzinfo=UTC),
            scores=(RubricScore(criterion="format adherence", score=2),),
            notes="Meets the requested form.",
            uncertainty="low",
        ),
    )
    mapping = IdentityMappingEnvelope(
        record_id="mapping-1",
        experiment_id="exp-1",
        run_id="run-1",
        trial_id="trial-1",
        payload=IdentityMapping(
            blinded_output_id="opaque-7", trial_record_id="trial-record-1"
        ),
    )

    store.append(evaluation)
    store.append(mapping)

    records = store.read_all()
    assert [record.record_type for record in records] == [
        "blinded_evaluation",
        "identity_mapping",
    ]
