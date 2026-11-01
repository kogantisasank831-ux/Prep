"""Typed domain contracts for the Week 14 control-flow comparison."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from decimal import Decimal
from enum import StrEnum
from hashlib import sha256
import json


class Action(StrEnum):
    """Operations a planner may propose to the trusted executor."""

    LOAD_ORDER = "load_order"
    LOOKUP_SUPPLIER = "lookup_supplier"
    GET_REFERENCE_PRICE = "get_reference_price"
    CALCULATE_VARIANCE = "calculate_variance"
    SEARCH_CONTRACT_TERMS = "search_contract_terms"
    FINISH = "finish"


TOOL_ACTIONS: frozenset[Action] = frozenset(
    action for action in Action if action is not Action.FINISH
)


class Route(StrEnum):
    WORKFLOW = "workflow"
    AGENT = "agent"


class Recommendation(StrEnum):
    NO_REVIEW = "no_review"
    REVIEW_REQUIRED = "review_required"
    NEEDS_HUMAN = "needs_human"


class RunStatus(StrEnum):
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    FAILED = "failed"


class ApprovalDecision(StrEnum):
    APPROVE = "approve"
    REJECT = "reject"


@dataclass(frozen=True)
class ProcurementCase:
    case_id: str
    purchase_order_id: str


@dataclass(frozen=True)
class PurchaseOrder:
    purchase_order_id: str
    supplier_id: str
    commodity_id: str
    current_price: Decimal
    currency: str
    unit: str


@dataclass(frozen=True)
class Supplier:
    supplier_id: str
    name: str
    status: str


@dataclass(frozen=True)
class ReferencePrice:
    commodity_id: str
    amount: Decimal
    currency: str
    unit: str
    as_of: str


@dataclass(frozen=True)
class PriceVariance:
    absolute: Decimal
    percent: Decimal
    currency: str
    unit: str


@dataclass(frozen=True)
class ContractTerms:
    purchase_order_id: str
    found: bool
    max_variance_percent: Decimal | None
    excerpt: str


Fact = PurchaseOrder | Supplier | ReferencePrice | PriceVariance | ContractTerms


@dataclass
class InvestigationState:
    case: ProcurementCase
    order: PurchaseOrder | None = None
    supplier: Supplier | None = None
    reference_price: ReferencePrice | None = None
    variance: PriceVariance | None = None
    contract_terms: ContractTerms | None = None
    completed: set[Action] = field(default_factory=set)
    last_error: str | None = None

    def ready_for_report(self) -> bool:
        """Return whether every required investigation fact has been observed."""
        return all(
            value is not None
            for value in (
                self.order,
                self.supplier,
                self.reference_price,
                self.variance,
                self.contract_terms,
            )
        )


@dataclass(frozen=True)
class InvestigationReport:
    case_id: str
    purchase_order_id: str
    recommendation: Recommendation
    summary: str
    evidence: tuple[str, ...]

    def digest(self) -> str:
        """Bind an approval to the exact report snapshot shown to a reviewer."""
        payload = json.dumps(
            {
                "case_id": self.case_id,
                "purchase_order_id": self.purchase_order_id,
                "recommendation": self.recommendation,
                "summary": self.summary,
                "evidence": self.evidence,
            },
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        return sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class HumanApproval:
    """Trusted host input for the lab, not authentication or a signed token."""

    report_digest: str
    reviewer: str
    decision: ApprovalDecision


@dataclass(frozen=True)
class Metrics:
    model_calls: int
    tool_calls: int
    input_tokens: int
    output_tokens: int
    estimated_model_cost_usd: str
    modeled_latency_ms: int
    trace_events: int


@dataclass(frozen=True)
class RunResult:
    route: Route
    status: RunStatus
    report: InvestigationReport | None
    metrics: Metrics
    trace: tuple[str, ...]
    failure_reason: str | None = None

    @property
    def successful_investigation(self) -> bool:
        return self.status is not RunStatus.FAILED and self.report is not None


def finalize(result: RunResult, approval: HumanApproval) -> RunResult:
    """Apply a human decision only to the report snapshot it reviewed."""
    if result.status is not RunStatus.AWAITING_APPROVAL or result.report is None:
        raise ValueError("result_not_awaiting_approval")
    if (
        not isinstance(approval, HumanApproval)
        or not isinstance(approval.decision, ApprovalDecision)
        or not isinstance(approval.report_digest, str)
        or len(approval.report_digest) != 64
        or any(
            character not in "0123456789abcdef" for character in approval.report_digest
        )
    ):
        raise ValueError("approval_invalid")
    if (
        not isinstance(approval.reviewer, str)
        or not approval.reviewer.strip()
        or len(approval.reviewer) > 80
    ):
        raise ValueError("reviewer_required")
    if approval.report_digest != result.report.digest():
        raise ValueError("approval_report_mismatch")
    status = (
        RunStatus.APPROVED
        if approval.decision is ApprovalDecision.APPROVE
        else RunStatus.REJECTED
    )
    trace = (*result.trace, f"human:{approval.decision}:{approval.reviewer}")
    return replace(
        result,
        status=status,
        trace=trace,
        metrics=replace(result.metrics, trace_events=len(trace)),
    )
