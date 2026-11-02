"""Typed state and wire contracts for the Week 15 LangGraph lab."""

from __future__ import annotations

from operator import add
from typing import Annotated, Literal

from typing_extensions import NotRequired, TypedDict


Intent = Literal["procurement_price_investigation", "unsupported"]
Recommendation = Literal["no_review", "review_required", "needs_human"]
ApprovalStatus = Literal[
    "unsupported",
    "validation_failed",
    "awaiting_approval",
    "approved",
    "rejected",
]
ApprovalDecision = Literal["approve", "reject"]


class CaseInput(TypedDict):
    """A deterministic query/case pair supplied to the graph."""

    case_id: str
    query: str


class SqlAnalysis(TypedDict):
    """Fields returned by the parameterized local SQL query."""

    purchase_order_id: str
    supplier_id: str
    supplier_status: str
    commodity_id: str
    current_price: str
    reference_price: str
    currency: str
    unit: str
    reference_as_of: str


class ContractEvidence(TypedDict):
    """A retrieved synthetic contract fragment."""

    purchase_order_id: str
    found: bool
    max_variance_percent: str | None
    excerpt: str
    document_id: str


class InvestigationReport(TypedDict):
    """Canonical report shown at the human-review interrupt."""

    case_id: str
    purchase_order_id: str
    recommendation: Recommendation
    reason: str
    variance_percent: str
    reference_as_of: str
    evidence: list[str]


class ApprovalResponse(TypedDict):
    """Trusted host input expected when the graph resumes."""

    decision: ApprovalDecision
    reviewer: str
    report_digest: str


class InvestigationState(TypedDict, total=False):
    """Shared graph state; list channels demonstrate additive reducers."""

    case_id: str
    query: str
    purchase_order_id: str
    intent: Intent
    sql_analysis: SqlAnalysis
    contract: ContractEvidence
    variance_absolute: str
    variance_percent: str
    recommendation: Recommendation
    reason: str
    report: InvestigationReport
    report_digest: str
    validation_errors: list[str]
    valid: bool
    approval_status: ApprovalStatus
    reviewer: str
    evidence: Annotated[list[str], add]
    trace: Annotated[list[str], add]
    failure_reason: NotRequired[str]


class PublicRun(TypedDict):
    """JSON-safe projection returned by the command-line demonstration."""

    case_id: str
    status: ApprovalStatus
    recommendation: Recommendation | None
    report_digest: str | None
    reviewer: str | None
    trace: list[str]
    evidence: list[str]
    interrupt: dict[str, object] | None
