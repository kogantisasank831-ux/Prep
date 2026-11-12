"""Strict contracts for Week 30 serving and reporting."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


WeightBits = Literal[4, 8, 16]


class ServingConfig(BaseModel):
    """Bounded memory-capacity assumptions for one serving replica."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    model_parameters_billions: float = Field(gt=0.0, le=1_000.0)
    weight_bits: WeightBits
    gpu_memory_gib: float = Field(gt=0.0)
    non_weight_memory_gib: float = Field(gt=0.0)
    kv_bytes_per_token: int = Field(gt=0)
    max_context_tokens: int = Field(gt=0)
    requested_concurrency: int = Field(gt=0)


class ServingObservation(BaseModel):
    """One controlled load-observation result."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    generated_tokens: int = Field(gt=0)
    duration_seconds: float = Field(gt=0.0)
    batch_size: int = Field(gt=0)
    time_to_first_token_ms: float = Field(ge=0.0)
    end_to_end_latency_ms: float = Field(ge=0.0)

    @model_validator(mode="after")
    def validate_latency_order(self) -> ServingObservation:
        if self.end_to_end_latency_ms < self.time_to_first_token_ms:
            raise ValueError("end_to_end_before_first_token")
        return self


class ServingProfile(BaseModel):
    """Transparent estimate plus measured throughput and latency."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    weight_memory_gib: float = Field(gt=0.0)
    kv_cache_per_request_gib: float = Field(gt=0.0)
    requested_memory_gib: float = Field(gt=0.0)
    estimated_max_concurrency: int = Field(ge=0)
    requested_concurrency: int = Field(gt=0)
    feasible: bool
    measured_tokens_per_second: float = Field(gt=0.0)
    ttft_p50_ms: float = Field(ge=0.0)
    ttft_p95_ms: float = Field(ge=0.0)
    latency_p50_ms: float = Field(ge=0.0)
    latency_p95_ms: float = Field(ge=0.0)
    warnings: tuple[str, ...]


class PackageManifest(BaseModel):
    """Version binding for a deployable model package."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    model_id: str = Field(min_length=1)
    model_revision: str = Field(min_length=1)
    tokenizer_revision: str = Field(min_length=1)
    adapter_revision: str | None = None
    quantisation: str = Field(min_length=1)
    runtime: str = Field(min_length=1)
    model_checksum: str = Field(pattern=r"^[0-9a-f]{64}$")
    config_checksum: str = Field(pattern=r"^[0-9a-f]{64}$")


class ExperimentReport(BaseModel):
    """Required final evidence for the optional training experiment."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    objective: str = Field(min_length=20)
    dataset: str = Field(min_length=20)
    training_configuration: str = Field(min_length=20)
    compute_used: str = Field(min_length=10)
    loss_curve: tuple[float, ...] = Field(min_length=2)
    evaluation: str = Field(min_length=20)
    failures: tuple[str, ...]
    cost_usd: float = Field(ge=0.0)
    rag_comparison: str = Field(min_length=20)
    lessons_learned: tuple[str, ...] = Field(min_length=1)
    package: PackageManifest
    serving: ServingProfile


class ReportReview(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    valid: bool
    missing_sections: tuple[str, ...]
    warnings: tuple[str, ...]
