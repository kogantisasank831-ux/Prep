"""Strict contracts for the Week 16 case-memory lab."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Annotated, Literal, Self, get_args
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


Identifier = Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")]
SourceIdentifier = Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")]
Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
ApprovalStatus = Literal["awaiting_approval", "approved", "rejected"]
EpisodeKind = Literal[
    "objective_recorded",
    "supplier_selected",
    "evidence_retrieved",
    "calculation_recorded",
    "approval_status_recorded",
    "approval_status_changed",
]
MemoryErrorCode = Literal[
    "invalid_scope",
    "forbidden",
    "not_found",
    "store_exists",
    "store_missing",
    "schema_invalid",
    "source_in_future",
    "memory_expired",
    "revision_conflict",
    "immutable_fact_changed",
    "status_transition_invalid",
    "store_failed",
]


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError("timestamp_must_be_utc")
    return value.astimezone(timezone.utc)


def _identifier(value: str) -> str:
    if (
        type(value) is not str
        or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", value) is None
    ):
        raise ValueError("identifier_invalid")
    return value


class MemoryError(Exception):
    """Expose only controlled memory-layer failure categories."""

    def __init__(self, code: MemoryErrorCode) -> None:
        if type(code) is not str or code not in get_args(MemoryErrorCode):
            code = "store_failed"
        super().__init__(code)
        self.code = code


class ClosedModel(BaseModel):
    """Reject coercion and undeclared fields at every memory boundary."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class EvidenceReference(ClosedModel):
    """A source identity and digest, never the raw evidence body."""

    source_type: Literal["document", "sql"]
    source_id: SourceIdentifier
    content_digest: Digest
    observed_at: datetime

    @field_validator("observed_at")
    @classmethod
    def observed_in_utc(cls, value: datetime) -> datetime:
        return _utc(value)


class Calculation(ClosedModel):
    """One exact, source-dated calculation retained for the case."""

    metric: Literal["price_variance_percent"]
    value: Annotated[str, Field(pattern=r"^-?(0|[1-9][0-9]{0,7})\.[0-9]{2}$")]
    currency: Annotated[str, Field(pattern=r"^[A-Z]{3}$")]
    unit: Literal["kg", "tonne", "piece"]
    reference_as_of: date
    rounding: Literal["ROUND_HALF_EVEN"]


EvidenceSet = Annotated[
    tuple[EvidenceReference, ...], Field(min_length=2, max_length=8)
]


class CaseMemoryInput(ClosedModel):
    """Application-selected facts eligible for cross-thread retention."""

    case_id: Identifier
    objective: Annotated[str, Field(min_length=1, max_length=320)]
    selected_supplier_id: Identifier
    evidence: EvidenceSet
    calculation: Calculation
    approval_status: ApprovalStatus
    source_run_id: Identifier
    source_report_digest: Digest
    observed_at: datetime
    expires_at: datetime

    @field_validator("observed_at", "expires_at")
    @classmethod
    def timestamps_in_utc(cls, value: datetime) -> datetime:
        return _utc(value)

    @model_validator(mode="after")
    def validate_memory_contract(self) -> Self:
        if self.objective != self.objective.strip():
            raise ValueError("objective_whitespace")
        if len(self.objective.encode("utf-8")) > 512:
            raise ValueError("objective_too_large")
        identities = [(item.source_type, item.source_id) for item in self.evidence]
        if len(set(identities)) != len(identities):
            raise ValueError("duplicate_evidence")
        if {item.source_type for item in self.evidence} != {"document", "sql"}:
            raise ValueError("evidence_categories_required")
        if self.expires_at <= self.observed_at:
            raise ValueError("expiry_not_after_observation")
        if self.expires_at - self.observed_at > timedelta(days=90):
            raise ValueError("retention_exceeds_policy")
        return self


class CaseMemoryRecord(CaseMemoryInput):
    """Persisted semantic memory with revision and integrity metadata."""

    revision: Annotated[int, Field(ge=1)]
    memory_digest: Digest
    summary: Annotated[str, Field(min_length=1, max_length=1200)]
    created_at: datetime
    updated_at: datetime

    @field_validator("created_at", "updated_at")
    @classmethod
    def record_timestamps_in_utc(cls, value: datetime) -> datetime:
        return _utc(value)


class EpisodeRecord(ClosedModel):
    """A compact event retained as episodic memory."""

    sequence: Annotated[int, Field(ge=1)]
    kind: EpisodeKind
    summary: Annotated[str, Field(min_length=1, max_length=360)]
    occurred_at: datetime
    source_run_id: Identifier
    memory_digest: Digest

    @field_validator("occurred_at")
    @classmethod
    def episode_timestamp_in_utc(cls, value: datetime) -> datetime:
        return _utc(value)


class MemoryWriteResult(ClosedModel):
    """Write outcome that makes replay behavior visible."""

    record: CaseMemoryRecord
    replayed: bool


class ContextSelection(ClosedModel):
    """Bounded context assembled for one new turn."""

    case_id: Identifier
    memory_revision: Annotated[int, Field(ge=1)]
    approval_status: ApprovalStatus
    source_report_digest: Digest
    semantic_summary: str
    selected_episodes: tuple[str, ...]
    omitted_episode_count: Annotated[int, Field(ge=0)]
    rendered: str
    character_count: Annotated[int, Field(ge=1)]
    expires_at: datetime

    @field_validator("expires_at")
    @classmethod
    def context_expiry_in_utc(cls, value: datetime) -> datetime:
        return _utc(value)

    @model_validator(mode="after")
    def rendered_count_matches(self) -> Self:
        if len(self.rendered) != self.character_count:
            raise ValueError("context_character_count_mismatch")
        return self


@dataclass(frozen=True)
class AccessScope:
    """Trusted host scope; identifiers are not authentication credentials."""

    tenant_id: str
    allowed_case_ids: frozenset[str]
    can_write: bool = False

    def __post_init__(self) -> None:
        try:
            _identifier(self.tenant_id)
            if (
                type(self.allowed_case_ids) is not frozenset
                or not self.allowed_case_ids
            ):
                raise ValueError("allowed_cases_required")
            for case_id in self.allowed_case_ids:
                _identifier(case_id)
            if type(self.can_write) is not bool:
                raise ValueError("write_flag_invalid")
        except ValueError as error:
            raise MemoryError("invalid_scope") from error

    def require(self, case_id: str, *, write: bool = False) -> None:
        try:
            _identifier(case_id)
        except ValueError as error:
            raise MemoryError("not_found") from error
        if case_id not in self.allowed_case_ids:
            raise MemoryError("not_found")
        if write and not self.can_write:
            raise MemoryError("forbidden")
