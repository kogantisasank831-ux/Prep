"""Closed data contracts for the Week 20 reliability worker."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator


Identifier = Annotated[
    str, Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9._:-]+$")
]
Scenario = Literal[
    "llm-provider-outage",
    "database-timeout",
    "invalid-api-result",
    "vector-store-failure",
    "rate-limit-errors",
]
DependencyName = Literal[
    "model-primary",
    "model-secondary",
    "database-primary",
    "bounded-cache",
    "supplier-api",
    "vector-store",
    "lexical-search",
    "catalog-api",
]
DependencyStatus = Literal["ok", "unavailable", "rate_limited", "invalid", "failed"]
AttemptOutcome = Literal[
    "ok",
    "unavailable",
    "rate_limited",
    "timeout",
    "invalid_response",
    "dependency_failure",
    "circuit_open",
]
CircuitState = Literal["closed", "open", "half_open"]
ResolutionStatus = Literal["completed", "degraded", "failed"]
FailureKind = Literal["none", "transient", "permanent"]
ResultStatus = Literal["completed", "degraded", "dead_letter"]
ResultCode = Literal[
    "ok",
    "recovered_after_retry",
    "fallback_used",
    "dependency_unavailable",
    "rate_limited",
    "timeout",
    "invalid_response",
    "dependency_failure",
    "circuit_open",
    "retry_exhausted",
]


class StrictModel(BaseModel):
    """Reject coercion, non-finite values and unknown fields."""

    model_config = ConfigDict(
        allow_inf_nan=False, extra="forbid", frozen=True, strict=True
    )


class RetryPolicy(StrictModel):
    """A finite retry and per-attempt deadline budget."""

    max_attempts: Annotated[int, Field(ge=1, le=8)] = 3
    base_backoff_ms: Annotated[int, Field(ge=1, le=60_000)] = 100
    max_backoff_ms: Annotated[int, Field(ge=1, le=300_000)] = 1_000
    max_retry_after_ms: Annotated[int, Field(ge=1, le=300_000)] = 2_000
    timeout_ms: Annotated[int, Field(ge=1, le=300_000)] = 100

    @model_validator(mode="after")
    def backoff_bounds_agree(self) -> RetryPolicy:
        if self.base_backoff_ms > self.max_backoff_ms:
            raise ValueError("base_backoff_exceeds_cap")
        return self


class CircuitConfig(StrictModel):
    """Failure threshold and recovery-probe interval for one dependency."""

    failure_threshold: Annotated[int, Field(ge=1, le=20)] = 2
    recovery_timeout_ms: Annotated[int, Field(ge=1, le=3_600_000)] = 500


class QueueConfig(StrictModel):
    """Bounded delivery attempts before a job enters the dead-letter queue."""

    max_deliveries: Annotated[int, Field(ge=1, le=20)] = 2


class DependencyResponse(StrictModel):
    """One deterministic adapter response used by the local simulator."""

    dependency: DependencyName
    status: DependencyStatus
    elapsed_ms: Annotated[int, Field(ge=0, le=300_000)]
    data: dict[str, JsonValue]
    retry_after_ms: Annotated[int, Field(ge=1, le=300_000)] | None = None

    @model_validator(mode="after")
    def retry_after_matches_status(self) -> DependencyResponse:
        if self.status == "rate_limited" and self.retry_after_ms is None:
            raise ValueError("rate_limit_requires_retry_after")
        if self.status != "rate_limited" and self.retry_after_ms is not None:
            raise ValueError("retry_after_only_for_rate_limit")
        return self


class AttemptRecord(StrictModel):
    """Safe evidence for one dependency decision or invocation."""

    dependency: DependencyName
    attempt: Annotated[int, Field(ge=1, le=20)]
    invoked: bool
    outcome: AttemptOutcome
    elapsed_ms: Annotated[int, Field(ge=0, le=300_000)]
    scheduled_backoff_ms: Annotated[int, Field(ge=0, le=300_000)]
    circuit_state_after: CircuitState


class CallResolution(StrictModel):
    """The dependency chain's controlled result."""

    status: ResolutionStatus
    code: ResultCode
    failure_kind: FailureKind
    selected_dependency: DependencyName | None
    data: dict[str, JsonValue]
    warnings: tuple[str, ...]
    attempts: tuple[AttemptRecord, ...]

    @model_validator(mode="after")
    def resolution_fields_agree(self) -> CallResolution:
        if self.status == "failed":
            if self.failure_kind == "none" or self.selected_dependency is not None:
                raise ValueError("failed_resolution_fields_disagree")
        elif self.failure_kind != "none" or self.selected_dependency is None:
            raise ValueError("successful_resolution_fields_disagree")
        if self.status == "degraded" and self.code != "fallback_used":
            raise ValueError("degraded_resolution_requires_fallback")
        return self


class Job(StrictModel):
    """One tenant-scoped, idempotently keyed unit of queue work."""

    job_id: Identifier
    tenant_id: Identifier
    idempotency_key: Identifier
    scenario: Scenario


class JobResult(StrictModel):
    """Terminal public result for one job."""

    job_id: Identifier
    scenario: Scenario
    status: ResultStatus
    code: ResultCode
    selected_dependency: DependencyName | None
    data: dict[str, JsonValue]
    warnings: tuple[str, ...]
    attempts: tuple[AttemptRecord, ...]
    delivery_count: Annotated[int, Field(ge=1, le=20)]

    @model_validator(mode="after")
    def terminal_fields_agree(self) -> JobResult:
        if self.status == "dead_letter" and self.selected_dependency is not None:
            raise ValueError("dead_letter_cannot_select_dependency")
        if self.status != "dead_letter" and self.selected_dependency is None:
            raise ValueError("completed_job_requires_dependency")
        return self


class DeadLetterRecord(StrictModel):
    """Secret-minimized metadata retained for diagnosis and controlled replay."""

    job_id: Identifier
    tenant_id: Identifier
    scenario: Scenario
    code: ResultCode
    delivery_count: Annotated[int, Field(ge=1, le=20)]
    dependency_attempt_count: Annotated[int, Field(ge=0, le=100)]


class BatchReport(StrictModel):
    """Terminal results prove that one failed item does not abort its batch."""

    results: tuple[JobResult, ...]
    dead_letters: tuple[DeadLetterRecord, ...]
    completed_count: Annotated[int, Field(ge=0)]
    degraded_count: Annotated[int, Field(ge=0)]
    dead_letter_count: Annotated[int, Field(ge=0)]

    @model_validator(mode="after")
    def counts_match_results(self) -> BatchReport:
        expected = {
            "completed": sum(result.status == "completed" for result in self.results),
            "degraded": sum(result.status == "degraded" for result in self.results),
            "dead_letter": sum(
                result.status == "dead_letter" for result in self.results
            ),
        }
        if (
            self.completed_count != expected["completed"]
            or self.degraded_count != expected["degraded"]
            or self.dead_letter_count != expected["dead_letter"]
            or self.dead_letter_count != len(self.dead_letters)
        ):
            raise ValueError("batch_counts_disagree")
        return self
