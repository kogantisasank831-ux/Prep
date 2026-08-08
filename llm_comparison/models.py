from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime
from typing import Annotated, Literal, Self
from urllib.parse import urlsplit

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    field_validator,
    model_validator,
)


STRICT = ConfigDict(extra="forbid", frozen=True, strict=True)
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_prompt_suite_hash(cases: tuple[tuple[str, str], ...]) -> str:
    canonical = json.dumps(
        [
            {"prompt_case_id": case_id, "prompt_hash": prompt_hash}
            for case_id, prompt_hash in cases
        ],
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256_text(canonical)


def _validate_identifier(value: str) -> str:
    if _ID.fullmatch(value) is None:
        raise ValueError("identifier contains unsupported characters")
    return value


def _validate_utc(value: datetime) -> datetime:
    offset = value.utcoffset()
    if value.tzinfo is None or offset is None or offset.total_seconds() != 0:
        raise ValueError("timestamp must be UTC")
    return value


class StrictModel(BaseModel):
    model_config = STRICT


class AdapterConfig(StrictModel):
    base_url: str
    expected_model_identity: str = Field(min_length=1)
    api_route: Literal["/v1/chat/completions"] = "/v1/chat/completions"
    adapter_version: str = Field(min_length=1)
    bind_attestation: Literal["127.0.0.1"] = "127.0.0.1"

    @field_validator("base_url")
    @classmethod
    def loopback_http_only(cls, value: str) -> str:
        parsed = urlsplit(value)
        if (
            parsed.scheme != "http"
            or parsed.hostname != "127.0.0.1"
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
            or parsed.path != ""
            or parsed.port is None
        ):
            raise ValueError("base_url must be an explicit loopback HTTP origin")
        return value.rstrip("/")


class BaselineRequest(StrictModel):
    experiment_id: str
    run_id: str
    trial_id: str
    prompt_suite_id: str
    prompt_case_id: str
    prompt: str = Field(min_length=1)
    prompt_hash: str = ""
    context_size: Literal[4096] = 4096
    max_output_tokens: Literal[512] = 512
    stream: Literal[False] = False
    temperature: float = Field(ge=0.0, le=2.0)
    top_k: int = Field(ge=0)
    top_p: float = Field(gt=0.0, le=1.0)
    stop: tuple[str, ...] = ()
    seed: int
    timeout_seconds: float = Field(gt=0.0, le=3600.0)

    @field_validator(
        "experiment_id", "run_id", "trial_id", "prompt_suite_id", "prompt_case_id"
    )
    @classmethod
    def safe_identifier(cls, value: str) -> str:
        return _validate_identifier(value)

    @field_validator("prompt")
    @classmethod
    def nonblank_prompt(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("prompt must not be blank")
        return value

    @field_validator("temperature", "top_p", "timeout_seconds")
    @classmethod
    def finite_number(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("value must be finite")
        return value

    @field_validator("stop")
    @classmethod
    def valid_stop(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) > 8 or any(not item or len(item) > 128 for item in value):
            raise ValueError(
                "stop must contain at most eight non-empty bounded strings"
            )
        return value

    @model_validator(mode="after")
    def derive_prompt_hash(self) -> Self:
        expected = sha256_text(self.prompt)
        if self.prompt_hash and self.prompt_hash != expected:
            raise ValueError("prompt_hash does not match canonical prompt")
        object.__setattr__(self, "prompt_hash", expected)
        return self

    def generation_fingerprint(self) -> str:
        canonical = json.dumps(
            {
                "context_size": self.context_size,
                "max_output_tokens": self.max_output_tokens,
                "prompt_hash": self.prompt_hash,
                "seed": self.seed,
                "stop": self.stop,
                "stream": self.stream,
                "temperature": self.temperature,
                "timeout_seconds": self.timeout_seconds,
                "top_k": self.top_k,
                "top_p": self.top_p,
            },
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return sha256_text(canonical)


def canonical_request_schedule_hash(requests: tuple[BaselineRequest, ...]) -> str:
    canonical = json.dumps(
        [
            {
                "case_id": request.prompt_case_id,
                "context_size": request.context_size,
                "max_output_tokens": request.max_output_tokens,
                "prompt_hash": request.prompt_hash,
                "prompt_suite_id": request.prompt_suite_id,
                "seed": request.seed,
                "stop": request.stop,
                "stream": request.stream,
                "temperature": request.temperature,
                "timeout_seconds": request.timeout_seconds,
                "top_k": request.top_k,
                "top_p": request.top_p,
                "trial_id": request.trial_id,
            }
            for request in requests
        ],
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256_text(canonical)


class ArtifactShard(StrictModel):
    order: int = Field(ge=0)
    filename: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    size_bytes: int = Field(gt=0)


class RuntimeProvenance(StrictModel):
    runtime_name: Literal["llama.cpp"] = "llama.cpp"
    runtime_revision: str = Field(min_length=1)
    runtime_binary_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    server_arguments: tuple[str, ...]
    os_version: str = Field(min_length=1)
    gpu_model: str = Field(min_length=1)
    gpu_vram_bytes: int = Field(gt=0)
    system_ram_bytes: int = Field(gt=0)
    nvidia_driver_version: str = Field(min_length=1)
    cuda_backend: str = Field(min_length=1)
    cpu_threads: int = Field(gt=0)
    harness_version: str = Field(min_length=1)


class ModelProvenance(StrictModel):
    source_repository: Literal[
        "Qwen/Qwen2.5-1.5B-Instruct-GGUF",
        "Qwen/Qwen2.5-7B-Instruct-GGUF",
    ]
    repository_revision: str = Field(min_length=1)
    artifacts: tuple[ArtifactShard, ...]
    quantization: Literal["Q4_K_M"]
    declared_license: Literal["Apache-2.0"]
    verified_license_revision: str = Field(min_length=1)
    chat_template_identity: str = Field(min_length=1)
    chat_template_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    tokenizer_identity: str = Field(min_length=1)
    tokenizer_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def ordered_unique_shards(self) -> Self:
        orders = [item.order for item in self.artifacts]
        names = [item.filename for item in self.artifacts]
        if not orders or orders != list(range(len(orders))):
            raise ValueError("artifact shards must be ordered contiguously from zero")
        if len(names) != len(set(names)):
            raise ValueError("artifact filenames must be unique")
        if self.source_repository == "Qwen/Qwen2.5-1.5B-Instruct-GGUF":
            if (
                len(names) != 1
                or names[0].lower() != "qwen2.5-1.5b-instruct-q4_k_m.gguf"
            ):
                raise ValueError(
                    "the locked 1.5B artifact must contain exactly one shard"
                )
        elif len(names) != 2 or tuple(name.lower() for name in names) != (
            "qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf",
            "qwen2.5-7b-instruct-q4_k_m-00002-of-00002.gguf",
        ):
            raise ValueError("the locked 7B artifact must contain two coherent shards")
        return self

    def artifact_set_hash(self) -> str:
        canonical = json.dumps(
            [artifact.model_dump(mode="json") for artifact in self.artifacts],
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return sha256_text(canonical)


class GenerationConfiguration(StrictModel):
    context_size: Literal[4096] = 4096
    max_output_tokens: Literal[512] = 512
    stream: Literal[False] = False
    requested_gpu_layers: int = Field(ge=0)
    effective_gpu_layers: int = Field(ge=0)
    cache_policy: str = Field(min_length=1)
    warmup_policy: str = Field(min_length=1)
    gpu_offload_failure_record_id: str | None = None

    @model_validator(mode="after")
    def effective_offload_is_bounded(self) -> Self:
        if self.effective_gpu_layers > self.requested_gpu_layers:
            raise ValueError("effective GPU layers cannot exceed requested GPU layers")
        if (
            self.effective_gpu_layers < self.requested_gpu_layers
            and self.gpu_offload_failure_record_id is None
        ):
            raise ValueError("reduced GPU offload requires a failed-load record")
        if (
            self.effective_gpu_layers == self.requested_gpu_layers
            and self.gpu_offload_failure_record_id is not None
        ):
            raise ValueError("full GPU offload cannot reference a fallback failure")
        return self

    def configuration_hash(self) -> str:
        canonical = json.dumps(
            {
                "cache_policy": self.cache_policy,
                "context_size": self.context_size,
                "effective_gpu_layers": self.effective_gpu_layers,
                "max_output_tokens": self.max_output_tokens,
                "requested_gpu_layers": self.requested_gpu_layers,
                "stream": self.stream,
                "warmup_policy": self.warmup_policy,
            },
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return sha256_text(canonical)


class ReadinessObservation(StrictModel):
    elapsed_seconds: float | None
    unit: Literal["seconds"] = "seconds"
    boundary: Literal["process invocation through ready health response"] = (
        "process invocation through ready health response"
    )
    unavailable_reason: str | None = None

    @model_validator(mode="after")
    def value_or_reason(self) -> Self:
        if self.elapsed_seconds is None:
            if not self.unavailable_reason:
                raise ValueError("unavailable readiness requires a reason")
        elif self.unavailable_reason is not None:
            raise ValueError("available readiness cannot have an unavailable reason")
        elif not math.isfinite(self.elapsed_seconds) or self.elapsed_seconds < 0:
            raise ValueError("readiness elapsed time must be finite and nonnegative")
        return self


class RunManifest(StrictModel):
    manifest_version: Literal[1] = 1
    experiment_id: str
    run_id: str
    created_at: datetime
    adapter: AdapterConfig
    runtime: RuntimeProvenance
    model: ModelProvenance
    generation: GenerationConfiguration
    block_index: int = Field(ge=0, le=1)
    readiness: ReadinessObservation
    startup_evidence_id: str
    readiness_evidence_id: str
    warmup_evidence_id: str
    prior_shutdown_evidence_id: str | None = None

    @field_validator("experiment_id", "run_id")
    @classmethod
    def safe_identifier(cls, value: str) -> str:
        return _validate_identifier(value)

    @field_validator("created_at")
    @classmethod
    def aware_datetime(cls, value: datetime) -> datetime:
        return _validate_utc(value)

    @model_validator(mode="after")
    def server_arguments_match_configuration(self) -> Self:
        arguments = self.runtime.server_arguments
        required_values = {
            "--host": "127.0.0.1",
            "--ctx-size": str(self.generation.context_size),
            "--n-gpu-layers": str(self.generation.effective_gpu_layers),
        }
        for flag, expected in required_values.items():
            positions = [
                index for index, value in enumerate(arguments) if value == flag
            ]
            if (
                len(positions) != 1
                or positions[0] + 1 >= len(arguments)
                or arguments[positions[0] + 1] != expected
            ):
                raise ValueError(
                    "server arguments do not attest bind/context/GPU configuration"
                )
        return self


class ExperimentPlan(StrictModel):
    plan_version: Literal[1] = 1
    experiment_id: str
    run_id: str
    mode: Literal["calibration", "heldout"]
    model_repositories: tuple[
        Literal["Qwen/Qwen2.5-1.5B-Instruct-GGUF"],
        Literal["Qwen/Qwen2.5-7B-Instruct-GGUF"],
    ]
    block_order: tuple[Literal[0], Literal[1]] = (0, 1)
    warmup_requests: Literal[1] = 1
    measured_trials_per_case: Literal[3] = 3
    prompt_suite_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    request_schedule_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    calibration_suite_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    heldout_suite_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    reference_material_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    rubric_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    calibration_case_ids: tuple[str, ...]
    heldout_case_ids: tuple[str, ...]
    ordered_case_ids: tuple[str, ...]
    ordering_seed: int
    measured_run: bool
    runtime_revision: str
    runtime_binary_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    artifact_revisions: tuple[str, str]
    artifact_set_hashes: tuple[str, str]
    generation_config_hashes: tuple[str, str]
    adapter_versions: tuple[str, str]
    chat_template_hashes: tuple[str, str]
    tokenizer_hashes: tuple[str, str]

    @field_validator("experiment_id", "run_id")
    @classmethod
    def safe_experiment_id(cls, value: str) -> str:
        return _validate_identifier(value)

    @model_validator(mode="after")
    def frozen_measured_plan(self) -> Self:
        if not self.ordered_case_ids or any(
            len(set(case_ids)) != len(case_ids)
            for case_ids in (
                self.ordered_case_ids,
                self.calibration_case_ids,
                self.heldout_case_ids,
            )
        ):
            raise ValueError("case ordering must be non-empty and unique")
        for identifier in (
            *self.ordered_case_ids,
            *self.calibration_case_ids,
            *self.heldout_case_ids,
        ):
            _validate_identifier(identifier)
        if set(self.calibration_case_ids) & set(self.heldout_case_ids):
            raise ValueError("calibration and held-out cases must be disjoint")
        expected_cases = (
            self.heldout_case_ids
            if self.mode == "heldout"
            else self.calibration_case_ids
        )
        if self.ordered_case_ids != expected_cases:
            raise ValueError("ordered cases must exactly match the selected plan mode")
        if self.mode == "heldout" and not self.measured_run:
            raise ValueError("held-out plans must be measured runs")
        if self.mode == "calibration" and self.measured_run:
            raise ValueError("calibration plans cannot be measured runs")
        selected_hash = (
            self.heldout_suite_hash
            if self.mode == "heldout"
            else self.calibration_suite_hash
        )
        if self.prompt_suite_hash != selected_hash:
            raise ValueError("prompt suite hash must match the selected plan mode")
        if self.mode == "heldout":
            pins = (
                self.runtime_revision,
                self.runtime_binary_sha256,
                *self.artifact_revisions,
                *self.artifact_set_hashes,
                *self.generation_config_hashes,
            )
            if any(not value or value.startswith("UNRESOLVED") for value in pins):
                raise ValueError(
                    "measured runs require resolved runtime and artifact pins"
                )
        if any(
            len(value) != 64
            or any(character not in "0123456789abcdef" for character in value)
            for value in (*self.artifact_set_hashes, *self.generation_config_hashes)
        ):
            raise ValueError("block hashes must be SHA-256 values")
        return self

    def canonical_hash(self) -> str:
        return sha256_text(
            json.dumps(
                self.model_dump(mode="json"),
                ensure_ascii=False,
                allow_nan=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        )


MetricSource = Literal["client_observed", "runtime_reported", "derived"]


class Metric(StrictModel):
    name: str = Field(min_length=1)
    value: int | float | None
    unit: str = Field(min_length=1)
    boundary: str = Field(min_length=1)
    source: MetricSource
    unavailable_reason: str | None = None

    @model_validator(mode="after")
    def available_xor_reason(self) -> Self:
        if self.value is None:
            if not self.unavailable_reason:
                raise ValueError("an unavailable metric requires a reason")
        elif self.unavailable_reason is not None:
            raise ValueError("an available metric cannot have an unavailable reason")
        elif self.unit == "tokens" and (
            isinstance(self.value, bool) or not isinstance(self.value, int)
        ):
            raise ValueError("token metrics require nonnegative integer values")
        elif not math.isfinite(self.value) or self.value < 0:
            raise ValueError("metric values must be finite and nonnegative")
        return self


class ObservationBase(StrictModel):
    experiment_id: str
    run_id: str
    trial_id: str
    prompt_suite_id: str
    prompt_case_id: str
    prompt_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    generation_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    model_identity: str = Field(min_length=1)
    started_at: datetime
    elapsed_seconds: float = Field(ge=0.0)
    metrics: tuple[Metric, ...]

    @field_validator(
        "experiment_id", "run_id", "trial_id", "prompt_suite_id", "prompt_case_id"
    )
    @classmethod
    def safe_identifier(cls, value: str) -> str:
        return _validate_identifier(value)

    @field_validator("started_at")
    @classmethod
    def utc_started_at(cls, value: datetime) -> datetime:
        return _validate_utc(value)

    @field_validator("elapsed_seconds")
    @classmethod
    def finite_elapsed(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("elapsed time must be finite")
        return value


class SuccessfulObservation(ObservationBase):
    outcome: Literal["success"] = "success"
    generated_text: str
    finish_reason: Literal["stop", "length", "content_filter", "unknown"] | None
    raw_finish_reason: str | None
    finish_reason_unavailable_reason: str | None = None

    @model_validator(mode="after")
    def finish_reason_is_explicit(self) -> Self:
        if self.raw_finish_reason is None:
            if (
                self.finish_reason is not None
                or not self.finish_reason_unavailable_reason
            ):
                raise ValueError("invalid finish reason requires an unavailable reason")
        elif (
            self.finish_reason is None
            or self.finish_reason_unavailable_reason is not None
        ):
            raise ValueError("raw finish reason requires a normalized value")
        return self


FailureCategory = Literal[
    "not_ready", "configuration", "timeout", "transport", "protocol", "server"
]


class FailedObservation(ObservationBase):
    outcome: Literal["failure"] = "failure"
    category: FailureCategory
    sanitized_detail: str = Field(min_length=1, max_length=512)
    finish_reason: Literal["error"] = "error"


TrialResult = Annotated[
    SuccessfulObservation | FailedObservation, Field(discriminator="outcome")
]


class TrialRequestSettings(StrictModel):
    experiment_id: str
    run_id: str
    trial_id: str
    prompt_suite_id: str
    prompt_case_id: str
    prompt_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    context_size: Literal[4096] = 4096
    max_output_tokens: Literal[512] = 512
    stream: Literal[False] = False
    temperature: float = Field(ge=0.0, le=2.0)
    top_k: int = Field(ge=0)
    top_p: float = Field(gt=0.0, le=1.0)
    stop: tuple[str, ...]
    seed: int
    timeout_seconds: float = Field(gt=0.0, le=3600.0)

    @classmethod
    def from_request(cls, request: BaselineRequest) -> Self:
        return cls(
            experiment_id=request.experiment_id,
            run_id=request.run_id,
            trial_id=request.trial_id,
            prompt_suite_id=request.prompt_suite_id,
            prompt_case_id=request.prompt_case_id,
            prompt_hash=request.prompt_hash,
            context_size=request.context_size,
            max_output_tokens=request.max_output_tokens,
            stream=request.stream,
            temperature=request.temperature,
            top_k=request.top_k,
            top_p=request.top_p,
            stop=request.stop,
            seed=request.seed,
            timeout_seconds=request.timeout_seconds,
        )

    def generation_fingerprint(self) -> str:
        canonical = json.dumps(
            {
                "context_size": self.context_size,
                "max_output_tokens": self.max_output_tokens,
                "prompt_hash": self.prompt_hash,
                "seed": self.seed,
                "stop": self.stop,
                "stream": self.stream,
                "temperature": self.temperature,
                "timeout_seconds": self.timeout_seconds,
                "top_k": self.top_k,
                "top_p": self.top_p,
            },
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return sha256_text(canonical)


def canonical_persisted_schedule_hash(
    settings: tuple[TrialRequestSettings, ...],
) -> str:
    canonical = json.dumps(
        [
            {
                "case_id": item.prompt_case_id,
                "context_size": item.context_size,
                "max_output_tokens": item.max_output_tokens,
                "prompt_hash": item.prompt_hash,
                "prompt_suite_id": item.prompt_suite_id,
                "seed": item.seed,
                "stop": item.stop,
                "stream": item.stream,
                "temperature": item.temperature,
                "timeout_seconds": item.timeout_seconds,
                "top_k": item.top_k,
                "top_p": item.top_p,
                "trial_id": item.trial_id,
            }
            for item in settings
        ],
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256_text(canonical)


class TrialObservation(StrictModel):
    observation_version: Literal[1] = 1
    manifest_record_id: str
    plan_record_id: str
    plan_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    request_settings: TrialRequestSettings
    block_index: int = Field(ge=0)
    result: TrialResult

    @model_validator(mode="after")
    def request_matches_result(self) -> Self:
        settings = self.request_settings
        result = self.result
        identities = (
            (settings.experiment_id, result.experiment_id),
            (settings.run_id, result.run_id),
            (settings.trial_id, result.trial_id),
            (settings.prompt_suite_id, result.prompt_suite_id),
            (settings.prompt_case_id, result.prompt_case_id),
            (settings.prompt_hash, result.prompt_hash),
            (settings.generation_fingerprint(), result.generation_fingerprint),
        )
        if any(expected != actual for expected, actual in identities):
            raise ValueError("persisted request settings do not match trial result")
        return self


class RubricScore(StrictModel):
    criterion: str = Field(min_length=1)
    score: Literal[0, 1, 2] | None
    not_applicable_reason: str | None = None

    @model_validator(mode="after")
    def score_or_reason(self) -> Self:
        if (self.score is None) == (self.not_applicable_reason is None):
            raise ValueError("provide exactly one of score or not_applicable_reason")
        return self


class BlindedEvaluation(StrictModel):
    evaluation_version: Literal[1] = 1
    blinded_output_id: str
    rubric_version: str
    evaluator_id: str
    evaluated_at: datetime
    scores: tuple[RubricScore, ...]
    notes: str
    uncertainty: str

    @field_validator("evaluated_at")
    @classmethod
    def utc_evaluated_at(cls, value: datetime) -> datetime:
        return _validate_utc(value)


class IdentityMapping(StrictModel):
    mapping_version: Literal[1] = 1
    blinded_output_id: str
    trial_record_id: str


EvidenceType = Literal[
    "startup",
    "readiness",
    "warmup_completed",
    "server_shutdown",
    "gpu_load_failure",
    "block_completed",
]


class OperationalEvidence(StrictModel):
    evidence_version: Literal[1] = 1
    evidence_type: EvidenceType
    observed_at: datetime
    model_identity: str
    block_index: int = Field(ge=0, le=1)
    generation_config_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    success: bool
    safe_detail_code: str
    attempted_gpu_layers: int | None = Field(default=None, ge=0)
    elapsed_seconds: float | None = Field(default=None, ge=0.0)
    plan_record_id: str | None = None
    plan_hash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    request_schedule_hash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    durable_trial_count: int | None = Field(default=None, ge=0)
    durable_trial_set_hash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")

    @field_validator("observed_at")
    @classmethod
    def utc_observed_at(cls, value: datetime) -> datetime:
        return _validate_utc(value)

    @model_validator(mode="after")
    def evidence_semantics(self) -> Self:
        if self.evidence_type == "gpu_load_failure":
            if (
                self.success
                or self.attempted_gpu_layers is None
                or self.elapsed_seconds is not None
            ):
                raise ValueError(
                    "GPU load failure evidence requires a failed layer attempt"
                )
        elif not self.success or self.attempted_gpu_layers is not None:
            raise ValueError(
                "successful lifecycle evidence cannot contain GPU attempt fields"
            )
        elif self.evidence_type in {"startup", "readiness"}:
            if self.elapsed_seconds is None or not math.isfinite(self.elapsed_seconds):
                raise ValueError(
                    "startup and readiness evidence require finite elapsed time"
                )
        elif self.elapsed_seconds is not None:
            raise ValueError(
                "non-timing lifecycle evidence cannot contain elapsed time"
            )
        completion_fields = (
            self.plan_record_id,
            self.plan_hash,
            self.request_schedule_hash,
            self.durable_trial_count,
            self.durable_trial_set_hash,
        )
        if self.evidence_type == "block_completed":
            if any(value is None for value in completion_fields):
                raise ValueError(
                    "block completion requires durable plan and trial-set proof"
                )
        elif any(value is not None for value in completion_fields):
            raise ValueError(
                "only block completion may contain durable trial-set proof"
            )
        return self


class EnvelopeBase(StrictModel):
    schema_version: Literal[1] = 1
    record_id: str
    experiment_id: str
    run_id: str
    trial_id: str

    @field_validator("record_id", "experiment_id", "run_id", "trial_id")
    @classmethod
    def safe_identifier(cls, value: str) -> str:
        return _validate_identifier(value)


class ManifestEnvelope(EnvelopeBase):
    record_type: Literal["manifest"] = "manifest"
    payload: RunManifest

    @model_validator(mode="after")
    def identity_matches_manifest(self) -> Self:
        if (
            self.experiment_id != self.payload.experiment_id
            or self.run_id != self.payload.run_id
        ):
            raise ValueError("envelope identity does not match manifest")
        return self


class PlanEnvelope(EnvelopeBase):
    record_type: Literal["experiment_plan"] = "experiment_plan"
    plan_hash: str = ""
    payload: ExperimentPlan

    @model_validator(mode="after")
    def identity_and_hash_match(self) -> Self:
        expected = self.payload.canonical_hash()
        if (
            self.experiment_id != self.payload.experiment_id
            or self.run_id != self.payload.run_id
            or (self.plan_hash and self.plan_hash != expected)
        ):
            raise ValueError("plan envelope identity or hash mismatch")
        object.__setattr__(self, "plan_hash", expected)
        return self


class OperationalEvidenceEnvelope(EnvelopeBase):
    record_type: Literal["operational_evidence"] = "operational_evidence"
    payload: OperationalEvidence


class TrialEnvelope(EnvelopeBase):
    record_type: Literal["trial_observation"] = "trial_observation"
    payload: TrialObservation

    @model_validator(mode="after")
    def identity_matches_observation(self) -> Self:
        result = self.payload.result
        if (
            self.experiment_id != result.experiment_id
            or self.run_id != result.run_id
            or self.trial_id != result.trial_id
        ):
            raise ValueError("envelope identity does not match trial observation")
        return self


class EvaluationEnvelope(EnvelopeBase):
    record_type: Literal["blinded_evaluation"] = "blinded_evaluation"
    payload: BlindedEvaluation


class IdentityMappingEnvelope(EnvelopeBase):
    record_type: Literal["identity_mapping"] = "identity_mapping"
    payload: IdentityMapping


Envelope = Annotated[
    ManifestEnvelope
    | PlanEnvelope
    | OperationalEvidenceEnvelope
    | TrialEnvelope
    | EvaluationEnvelope
    | IdentityMappingEnvelope,
    Field(discriminator="record_type"),
]
ENVELOPE_ADAPTER: TypeAdapter[Envelope] = TypeAdapter(Envelope)
