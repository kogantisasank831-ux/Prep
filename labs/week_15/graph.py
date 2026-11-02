"""A deterministic, checkpointed LangGraph procurement investigation."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN, localcontext
from hashlib import sha256
import json
import re
from typing import Literal, cast

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command, interrupt

from labs.week_15.fixtures import CASE_ORDERS, analyze_order_sql, retrieve_contract
from labs.week_15.models import (
    ApprovalDecision,
    ApprovalResponse,
    InvestigationReport,
    InvestigationState,
    Recommendation,
)


GraphRoute = Literal["retrieve_documents", "unsupported_query"]
ValidationRoute = Literal["human_approval", "__end__"]


def canonical_report_digest(report: InvestigationReport) -> str:
    """Return the digest used to bind approval to an exact report snapshot."""
    payload = json.dumps(
        report,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256(payload.encode("utf-8")).hexdigest()


def classify_query(state: InvestigationState) -> InvestigationState:
    """Classify a narrow local query without a model or network call."""
    case_id = state.get("case_id", "")
    query = state.get("query", "")
    purchase_order_id = CASE_ORDERS.get(case_id)
    normalized = " ".join(query.casefold().split())
    supported = bool(
        purchase_order_id
        and ("price" in normalized or "cost" in normalized)
        and (
            "purchase order" in normalized or purchase_order_id.casefold() in normalized
        )
    )
    if not supported or purchase_order_id is None:
        return {
            "intent": "unsupported",
            "approval_status": "unsupported",
            "failure_reason": "unsupported_query_or_case",
            "trace": ["classify_query:unsupported"],
        }
    return {
        "intent": "procurement_price_investigation",
        "purchase_order_id": purchase_order_id,
        "trace": ["classify_query:procurement_price_investigation"],
    }


def route_after_classification(state: InvestigationState) -> GraphRoute:
    """Choose the first business node from explicit classified state."""
    if state.get("intent") == "procurement_price_investigation":
        return "retrieve_documents"
    return "unsupported_query"


def unsupported_query(state: InvestigationState) -> InvestigationState:
    """End a request that is outside this teaching graph's contract."""
    del state
    return {"trace": ["unsupported_query:end"]}


def retrieve_documents(state: InvestigationState) -> InvestigationState:
    """Retrieve a synthetic contract result and preserve its source identity."""
    purchase_order_id = state["purchase_order_id"]
    contract = retrieve_contract(purchase_order_id)
    availability = "found" if contract["found"] else "missing"
    return {
        "contract": contract,
        "evidence": [f"document:{contract['document_id']}:{availability}"],
        "trace": [f"retrieve_documents:{availability}"],
    }


def analyze_sql(state: InvestigationState) -> InvestigationState:
    """Run the parameterized SQL analysis for the classified purchase order."""
    analysis = analyze_order_sql(state["purchase_order_id"])
    return {
        "sql_analysis": analysis,
        "evidence": [f"sql:price_analysis:{analysis['purchase_order_id']}"],
        "trace": ["analyze_sql:complete"],
    }


def calculate_price(state: InvestigationState) -> InvestigationState:
    """Calculate exact two-place price variance with Decimal."""
    analysis = state["sql_analysis"]
    try:
        current = Decimal(analysis["current_price"])
        reference = Decimal(analysis["reference_price"])
    except InvalidOperation as error:
        raise ValueError("price_not_decimal") from error
    if reference <= 0:
        raise ValueError("reference_price_invalid")
    with localcontext() as context:
        context.prec = 28
        absolute = current - reference
        percent = (absolute / reference) * Decimal("100")
        quantizer = Decimal("0.01")
        absolute_text = str(absolute.quantize(quantizer, rounding=ROUND_HALF_EVEN))
        percent_text = str(percent.quantize(quantizer, rounding=ROUND_HALF_EVEN))
    return {
        "variance_absolute": absolute_text,
        "variance_percent": percent_text,
        "trace": [f"calculate_price:{percent_text}%"],
    }


def generate_recommendation(state: InvestigationState) -> InvestigationState:
    """Apply the same deterministic price-review policy used in Week 14."""
    analysis = state["sql_analysis"]
    contract = state["contract"]
    variance = Decimal(state["variance_percent"])
    threshold_text = contract["max_variance_percent"]
    recommendation: Recommendation
    if not contract["found"] or threshold_text is None:
        recommendation = "needs_human"
        reason = "The applicable price-variance contract term was not found."
    elif analysis["supplier_status"] != "active":
        recommendation = "review_required"
        reason = f"Supplier status is {analysis['supplier_status']}."
    elif variance > Decimal(threshold_text):
        recommendation = "review_required"
        reason = f"The {variance}% variance exceeds the {threshold_text}% contract threshold."
    else:
        recommendation = "no_review"
        reason = f"The {variance}% variance is within the {threshold_text}% contract threshold."
    return {
        "recommendation": recommendation,
        "reason": reason,
        "trace": [f"generate_recommendation:{recommendation}"],
    }


def validate_report(state: InvestigationState) -> InvestigationState:
    """Validate required evidence and construct the exact review snapshot."""
    errors: list[str] = []
    analysis = state.get("sql_analysis")
    contract = state.get("contract")
    recommendation = state.get("recommendation")
    variance_percent = state.get("variance_percent")
    evidence = state.get("evidence", [])
    if analysis is None:
        errors.append("sql_analysis_required")
    if contract is None:
        errors.append("contract_result_required")
    if recommendation not in {"no_review", "review_required", "needs_human"}:
        errors.append("recommendation_required")
    if variance_percent is None:
        errors.append("variance_required")
    if not any(item.startswith("sql:") for item in evidence):
        errors.append("sql_evidence_required")
    if not any(item.startswith("document:") for item in evidence):
        errors.append("document_evidence_required")
    if errors:
        return {
            "valid": False,
            "validation_errors": errors,
            "approval_status": "validation_failed",
            "trace": ["validate_report:failed"],
        }
    assert analysis is not None
    assert contract is not None
    assert recommendation is not None
    assert variance_percent is not None
    report = InvestigationReport(
        case_id=state["case_id"],
        purchase_order_id=analysis["purchase_order_id"],
        recommendation=recommendation,
        reason=state["reason"],
        variance_percent=variance_percent,
        reference_as_of=analysis["reference_as_of"],
        evidence=list(evidence),
    )
    return {
        "valid": True,
        "validation_errors": [],
        "report": report,
        "report_digest": canonical_report_digest(report),
        "approval_status": "awaiting_approval",
        "trace": ["validate_report:passed"],
    }


def route_after_validation(state: InvestigationState) -> ValidationRoute:
    """Pause for review only when the report passed application validation."""
    return "human_approval" if state.get("valid") else "__end__"


def human_approval(state: InvestigationState) -> InvestigationState:
    """Pause and bind a trusted host decision to the displayed report digest."""
    report = state["report"]
    digest = state["report_digest"]
    raw_response: object = interrupt(
        {
            "kind": "human_approval",
            "question": "Accept this investigation report?",
            "report": report,
            "report_digest": digest,
            "allowed_decisions": ["approve", "reject"],
        },
        response_schema=ApprovalResponse,
    )
    if not isinstance(raw_response, dict):
        raise ValueError("approval_invalid")
    decision = raw_response.get("decision")
    reviewer = raw_response.get("reviewer")
    reviewed_digest = raw_response.get("report_digest")
    if decision not in {"approve", "reject"}:
        raise ValueError("approval_decision_invalid")
    if not isinstance(reviewer, str) or not reviewer.strip() or len(reviewer) > 80:
        raise ValueError("approval_reviewer_invalid")
    if (
        not isinstance(reviewed_digest, str)
        or re.fullmatch(r"[0-9a-f]{64}", reviewed_digest) is None
    ):
        raise ValueError("approval_digest_invalid")
    if reviewed_digest != digest:
        raise ValueError("approval_report_mismatch")
    typed_decision = cast(ApprovalDecision, decision)
    return {
        "approval_status": "approved" if typed_decision == "approve" else "rejected",
        "reviewer": reviewer.strip(),
        "trace": [f"human_approval:{typed_decision}:{reviewer.strip()}"],
    }


def build_graph(
    checkpointer: InMemorySaver,
) -> CompiledStateGraph[
    InvestigationState, None, InvestigationState, InvestigationState
]:
    """Compile the explicit graph with an injected checkpoint store."""
    builder: StateGraph[
        InvestigationState, None, InvestigationState, InvestigationState
    ] = StateGraph(InvestigationState)
    builder.add_node("classify_query", classify_query)
    builder.add_node("unsupported_query", unsupported_query)
    builder.add_node("retrieve_documents", retrieve_documents)
    builder.add_node("analyze_sql", analyze_sql)
    builder.add_node("calculate_price", calculate_price)
    builder.add_node("generate_recommendation", generate_recommendation)
    builder.add_node("validate_report", validate_report)
    builder.add_node("human_approval", human_approval)
    builder.add_edge(START, "classify_query")
    builder.add_conditional_edges("classify_query", route_after_classification)
    builder.add_edge("unsupported_query", END)
    builder.add_edge("retrieve_documents", "analyze_sql")
    builder.add_edge("analyze_sql", "calculate_price")
    builder.add_edge("calculate_price", "generate_recommendation")
    builder.add_edge("generate_recommendation", "validate_report")
    builder.add_conditional_edges("validate_report", route_after_validation)
    builder.add_edge("human_approval", END)
    return builder.compile(checkpointer=checkpointer, name="week_15_procurement")


class GraphRuntime:
    """Own one in-memory checkpointer and its compiled graph."""

    checkpointer: InMemorySaver
    graph: CompiledStateGraph[
        InvestigationState, None, InvestigationState, InvestigationState
    ]

    def __init__(self) -> None:
        self.checkpointer = InMemorySaver()
        self.graph = build_graph(self.checkpointer)

    @staticmethod
    def _config(thread_id: str) -> RunnableConfig:
        if not isinstance(thread_id, str) or not thread_id.strip():
            raise ValueError("thread_id_required")
        if len(thread_id) > 200:
            raise ValueError("thread_id_too_long")
        return {"configurable": {"thread_id": thread_id}}

    def start(self, case_id: str, query: str, *, thread_id: str) -> dict[str, object]:
        """Start a new thread and run until END or the approval interrupt."""
        if self.state(thread_id):
            raise ValueError("thread_already_exists")
        initial: InvestigationState = {
            "case_id": case_id,
            "query": query,
            "evidence": [],
            "trace": [],
        }
        result = self.graph.invoke(initial, config=self._config(thread_id))
        return cast(dict[str, object], result)

    def resume(
        self,
        thread_id: str,
        response: ApprovalResponse,
    ) -> dict[str, object]:
        """Resume exactly one interrupted thread with host-supplied review input."""
        config = self._config(thread_id)
        snapshot = self.graph.get_state(config)
        if not snapshot.values or not any(task.interrupts for task in snapshot.tasks):
            raise ValueError("thread_not_waiting_for_approval")
        result = self.graph.invoke(Command(resume=dict(response)), config=config)
        return cast(dict[str, object], result)

    def state(self, thread_id: str) -> dict[str, object]:
        """Return a copy of the latest checkpoint values for one thread."""
        snapshot = self.graph.get_state(self._config(thread_id))
        return dict(snapshot.values)

    def checkpoint_count(self, thread_id: str) -> int:
        """Count checkpoints for bounded tests and demonstrations."""
        return sum(1 for _ in self.graph.get_state_history(self._config(thread_id)))
