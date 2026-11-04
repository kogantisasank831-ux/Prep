"""Closed contracts for the Week 17 supervisor-specialist system."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_EVEN, localcontext
from enum import StrEnum
from typing import Annotated, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, model_validator


Identifier = Annotated[
    str, Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9._:-]+$")
]
Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Money = Annotated[Decimal, Field(gt=0, max_digits=18, decimal_places=6)]
Percent = Annotated[Decimal, Field(ge=Decimal("-100"), le=Decimal("10000"))]


class StrictModel(BaseModel):
    """Reject coercion, unknown fields and in-place mutation at every boundary."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class SpecialistName(StrEnum):
    DOCUMENT = "document"
    SQL = "sql"
    SUPPLIER_RISK = "supplier_risk"
    COMMERCIAL = "commercial"


class SourceKind(StrEnum):
    DOCUMENT = "document"
    SQL = "sql"
    RISK_REGISTER = "risk_register"


class SupplierStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class RiskLevel(StrEnum):
    LOW = "low"
    ELEVATED = "elevated"


class Recommendation(StrEnum):
    NO_REVIEW = "no_review"
    REVIEW_REQUIRED = "review_required"
    NEEDS_HUMAN = "needs_human"


class RunStatus(StrEnum):
    AWAITING_APPROVAL = "awaiting_approval"
    FAILED = "failed"


class Architecture(StrEnum):
    SUPERVISOR = "supervisor_specialists"
    SINGLE_WORKFLOW = "single_workflow"


class SourceReference(StrictModel):
    kind: SourceKind
    source_id: Identifier
    content_digest: Digest


class ProcurementCase(StrictModel):
    case_id: Identifier
    purchase_order_id: Identifier
    selected_supplier_id: Identifier
    document_source: SourceReference
    sql_source: SourceReference
    risk_source: SourceReference

    @model_validator(mode="after")
    def sources_have_distinct_expected_kinds(self) -> ProcurementCase:
        kinds = (
            self.document_source.kind,
            self.sql_source.kind,
            self.risk_source.kind,
        )
        expected = (
            SourceKind.DOCUMENT,
            SourceKind.SQL,
            SourceKind.RISK_REGISTER,
        )
        if kinds != expected:
            raise ValueError("case_source_kind_mismatch")
        if len({source.source_id for source in self.sources}) != 3:
            raise ValueError("case_sources_not_distinct")
        return self

    @property
    def sources(self) -> tuple[SourceReference, ...]:
        return (self.document_source, self.sql_source, self.risk_source)


class DocumentAssignment(StrictModel):
    run_id: Identifier
    case_id: Identifier
    specialist: Literal[SpecialistName.DOCUMENT] = SpecialistName.DOCUMENT
    purchase_order_id: Identifier
    source: SourceReference


class SqlAssignment(StrictModel):
    run_id: Identifier
    case_id: Identifier
    specialist: Literal[SpecialistName.SQL] = SpecialistName.SQL
    purchase_order_id: Identifier
    selected_supplier_id: Identifier
    source: SourceReference


class RiskAssignment(StrictModel):
    run_id: Identifier
    case_id: Identifier
    specialist: Literal[SpecialistName.SUPPLIER_RISK] = SpecialistName.SUPPLIER_RISK
    selected_supplier_id: Identifier
    source: SourceReference


class DocumentFinding(StrictModel):
    run_id: Identifier
    case_id: Identifier
    specialist: Literal[SpecialistName.DOCUMENT] = SpecialistName.DOCUMENT
    source: SourceReference
    terms_found: bool
    max_variance_percent: Percent | None

    @model_validator(mode="after")
    def terms_and_threshold_agree(self) -> DocumentFinding:
        if self.terms_found != (self.max_variance_percent is not None):
            raise ValueError("document_terms_threshold_mismatch")
        if self.max_variance_percent is not None and self.max_variance_percent < 0:
            raise ValueError("document_threshold_negative")
        return self


class SqlFinding(StrictModel):
    run_id: Identifier
    case_id: Identifier
    specialist: Literal[SpecialistName.SQL] = SpecialistName.SQL
    source: SourceReference
    purchase_order_id: Identifier
    supplier_id: Identifier
    current_price: Money
    reference_price: Money
    variance_percent: Percent
    currency: Annotated[str, Field(pattern=r"^[A-Z]{3}$")]
    unit: Annotated[str, Field(min_length=1, max_length=20)]
    as_of: Annotated[str, Field(pattern=r"^\d{4}-\d{2}-\d{2}$")]

    @model_validator(mode="after")
    def variance_is_exact(self) -> SqlFinding:
        with localcontext() as context:
            context.prec = 28
            expected = (
                (self.current_price - self.reference_price)
                / self.reference_price
                * Decimal("100")
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
        if self.variance_percent != expected:
            raise ValueError("sql_variance_mismatch")
        return self


class RiskFinding(StrictModel):
    run_id: Identifier
    case_id: Identifier
    specialist: Literal[SpecialistName.SUPPLIER_RISK] = SpecialistName.SUPPLIER_RISK
    source: SourceReference
    supplier_id: Identifier
    supplier_status: SupplierStatus
    open_incidents: Annotated[int, Field(ge=0, le=10000)]
    risk_level: RiskLevel

    @model_validator(mode="after")
    def risk_matches_evidence(self) -> RiskFinding:
        expected = (
            RiskLevel.LOW
            if self.supplier_status is SupplierStatus.ACTIVE
            and self.open_incidents == 0
            else RiskLevel.ELEVATED
        )
        if self.risk_level is not expected:
            raise ValueError("risk_level_mismatch")
        return self


class CommercialAssignment(StrictModel):
    run_id: Identifier
    case_id: Identifier
    specialist: Literal[SpecialistName.COMMERCIAL] = SpecialistName.COMMERCIAL
    document: DocumentFinding
    sql: SqlFinding
    risk: RiskFinding


class CommercialFinding(StrictModel):
    run_id: Identifier
    case_id: Identifier
    specialist: Literal[SpecialistName.COMMERCIAL] = SpecialistName.COMMERCIAL
    recommendation: Recommendation
    summary: Annotated[str, Field(min_length=1, max_length=600)]
    evidence: Annotated[tuple[str, ...], Field(min_length=3, max_length=3)]
    requires_human_approval: Literal[True] = True

    @model_validator(mode="after")
    def evidence_is_unique(self) -> CommercialFinding:
        if len(set(self.evidence)) != len(self.evidence):
            raise ValueError("commercial_evidence_not_unique")
        return self


Assignment: TypeAlias = (
    DocumentAssignment | SqlAssignment | RiskAssignment | CommercialAssignment
)
SpecialistResult: TypeAlias = (
    DocumentFinding | SqlFinding | RiskFinding | CommercialFinding
)
FirstWaveFinding: TypeAlias = DocumentFinding | SqlFinding | RiskFinding


class CoordinationMetrics(StrictModel):
    specialist_calls: Annotated[int, Field(ge=0, le=4)]
    handoffs: Annotated[int, Field(ge=0, le=4)]
    parallel_groups: Annotated[int, Field(ge=0, le=1)]
    dependency_stages: Annotated[int, Field(ge=0, le=4)]
    max_parallel_workers: Annotated[int, Field(ge=1, le=3)]


class RunResult(StrictModel):
    architecture: Architecture
    run_id: Identifier
    case_id: Identifier
    status: RunStatus
    report: CommercialFinding | None
    findings: tuple[FirstWaveFinding, ...]
    metrics: CoordinationMetrics
    trace: tuple[str, ...]
    failure_reason: str | None = None

    @model_validator(mode="after")
    def status_fields_agree(self) -> RunResult:
        if self.status is RunStatus.AWAITING_APPROVAL:
            if self.report is None or self.failure_reason is not None:
                raise ValueError("successful_run_fields_invalid")
        elif self.report is not None or self.failure_reason is None:
            raise ValueError("failed_run_fields_invalid")
        return self


class ArchitectureComparison(StrictModel):
    case_id: Identifier
    outcome_equal: bool
    supervisor_recommendation: Recommendation | None
    workflow_recommendation: Recommendation | None
    supervisor_handoffs: int
    workflow_handoffs: int
    supervisor_dependency_stages: int
    workflow_dependency_stages: int
    measured_latency_ms: None = None
    conclusion: str
