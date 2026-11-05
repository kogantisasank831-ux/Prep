"""Candidate adapter and controlled fault scenarios for the Week 18 eval."""

from __future__ import annotations

from collections.abc import Callable
from typing import cast

from pydantic import JsonValue, ValidationError

from labs.week_17.fixtures import CASES
from labs.week_17.models import (
    Assignment,
    DocumentFinding,
    ProcurementCase,
    Recommendation,
    RiskFinding,
    SpecialistName,
    SpecialistResult,
    SqlAssignment,
    SqlFinding,
)
from labs.week_17.specialists import (
    DEFAULT_SPECIALISTS,
    SpecialistFailure,
    SpecialistFunction,
)
from labs.week_17.supervisor import Supervisor
from labs.week_18.models import (
    AgentObservation,
    AgentRequest,
    AgentStatus,
    EvaluationCase,
    RecommendationValue,
    Scenario,
    ToolCall,
    ToolValue,
)


CANDIDATE_VERSION = "procurement-agent-v1.0.0"
PREFLIGHT_LATENCY_MS = 1
TOOL_COST_UNITS: dict[ToolValue, int] = {
    "document": 4,
    "sql": 3,
    "supplier_risk": 3,
    "commercial": 5,
}
TOOL_LATENCY_MS: dict[ToolValue, int] = {
    "document": 12,
    "sql": 8,
    "supplier_risk": 7,
    "commercial": 6,
}
RECOMMENDATION_VALUES: dict[Recommendation, RecommendationValue] = {
    Recommendation.NO_REVIEW: "no_review",
    Recommendation.REVIEW_REQUIRED: "review_required",
    Recommendation.NEEDS_HUMAN: "needs_human",
}


def _controlled_failure(code: str) -> SpecialistFunction:
    def fail(_: Assignment) -> SpecialistResult:
        raise SpecialistFailure(code)

    return fail


def _transform_result(
    original: SpecialistFunction,
    transform: Callable[[SpecialistResult], SpecialistResult],
) -> SpecialistFunction:
    def run(assignment: Assignment) -> SpecialistResult:
        return transform(original(assignment))

    return run


def _registry_for(scenario: Scenario) -> dict[SpecialistName, SpecialistFunction]:
    registry = dict(DEFAULT_SPECIALISTS)
    failures: dict[Scenario, tuple[SpecialistName, str]] = {
        "fail_document": (
            SpecialistName.DOCUMENT,
            "document_service_unavailable",
        ),
        "fail_sql": (SpecialistName.SQL, "sql_service_unavailable"),
        "fail_supplier_risk": (
            SpecialistName.SUPPLIER_RISK,
            "supplier_risk_service_unavailable",
        ),
        "fail_commercial": (
            SpecialistName.COMMERCIAL,
            "commercial_service_unavailable",
        ),
    }
    failure = failures.get(scenario)
    if failure is not None:
        specialist, code = failure
        registry[specialist] = _controlled_failure(code)
        return registry

    if scenario == "wrong_run_document":
        original = registry[SpecialistName.DOCUMENT]

        def wrong_run(result: SpecialistResult) -> SpecialistResult:
            finding = cast(DocumentFinding, result)
            return finding.model_copy(update={"run_id": "wrong-run"})

        registry[SpecialistName.DOCUMENT] = _transform_result(original, wrong_run)
    elif scenario == "wrong_case_sql":
        original = registry[SpecialistName.SQL]

        def wrong_case(result: SpecialistResult) -> SpecialistResult:
            finding = cast(SqlFinding, result)
            return finding.model_copy(update={"case_id": "wrong-case"})

        registry[SpecialistName.SQL] = _transform_result(original, wrong_case)
    elif scenario == "supplier_conflict":
        original = registry[SpecialistName.SUPPLIER_RISK]

        def conflicting_supplier(result: SpecialistResult) -> SpecialistResult:
            finding = cast(RiskFinding, result)
            return finding.model_copy(update={"supplier_id": "SUP-CONFLICT"})

        registry[SpecialistName.SUPPLIER_RISK] = _transform_result(
            original, conflicting_supplier
        )
    elif scenario == "invalid_sql_arguments":
        original = registry[SpecialistName.SQL]

        def invalid_sql_arguments(assignment: Assignment) -> SpecialistResult:
            sql_assignment = cast(SqlAssignment, assignment)
            corrupted = sql_assignment.model_copy(
                update={"selected_supplier_id": "SUP-INVALID"}
            )
            return original(corrupted)

        registry[SpecialistName.SQL] = invalid_sql_arguments
    return registry


def _case_for(request: AgentRequest, scenario: Scenario) -> ProcurementCase:
    procurement_case = CASES[request.case_name]
    if scenario != "bad_document_digest":
        return procurement_case
    source = procurement_case.document_source.model_copy(
        update={"content_digest": "0" * 64}
    )
    return procurement_case.model_copy(update={"document_source": source})


def _tool_arguments(
    tool: ToolValue,
    request: AgentRequest,
    procurement_case: ProcurementCase,
    scenario: Scenario,
) -> dict[str, JsonValue]:
    common: dict[str, JsonValue] = {
        "run_id": request.run_id,
        "case_id": procurement_case.case_id,
    }
    if tool == "document":
        return {
            **common,
            "purchase_order_id": procurement_case.purchase_order_id,
            "source_id": procurement_case.document_source.source_id,
        }
    if tool == "sql":
        supplier_id = procurement_case.selected_supplier_id
        if scenario == "invalid_sql_arguments":
            supplier_id = "SUP-INVALID"
        return {
            **common,
            "purchase_order_id": procurement_case.purchase_order_id,
            "selected_supplier_id": supplier_id,
            "source_id": procurement_case.sql_source.source_id,
        }
    if tool == "supplier_risk":
        return {
            **common,
            "selected_supplier_id": procurement_case.selected_supplier_id,
            "source_id": procurement_case.risk_source.source_id,
        }
    inputs: list[JsonValue] = ["document", "sql", "supplier_risk"]
    return {
        **common,
        "input_specialists": inputs,
    }


def expected_tool_arguments(
    case: EvaluationCase,
) -> tuple[dict[str, JsonValue], ...]:
    """Return independent expected projections for deterministic grading."""
    try:
        request = AgentRequest.model_validate(case.payload)
    except ValidationError:
        return ()
    procurement_case = CASES[request.case_name]
    return tuple(
        _tool_arguments(tool, request, procurement_case, "normal")
        for tool in case.expected_tools
    )


def _calls_from_trace(
    trace: tuple[str, ...],
    request: AgentRequest,
    procurement_case: ProcurementCase,
    scenario: Scenario,
) -> tuple[ToolCall, ...]:
    calls: list[ToolCall] = []
    for entry in trace:
        prefix = "supervisor:dispatch:"
        if not entry.startswith(prefix):
            continue
        tool = cast(ToolValue, entry.removeprefix(prefix))
        calls.append(
            ToolCall(
                step=len(calls) + 2,
                tool=tool,
                arguments=_tool_arguments(tool, request, procurement_case, scenario),
                cost_units=TOOL_COST_UNITS[tool],
                fixture_latency_ms=TOOL_LATENCY_MS[tool],
            )
        )
    return tuple(calls)


def _fixture_latency(calls: tuple[ToolCall, ...]) -> int:
    first_wave = [
        call.fixture_latency_ms for call in calls if call.tool != "commercial"
    ]
    commercial = next(
        (call.fixture_latency_ms for call in calls if call.tool == "commercial"),
        0,
    )
    return PREFLIGHT_LATENCY_MS + (max(first_wave) if first_wave else 0) + commercial


def _preflight_observation(
    case_id: str,
    *,
    failure_code: str,
    requires_human_approval: bool,
) -> AgentObservation:
    return AgentObservation(
        case_id=case_id,
        status="escalated",
        recommendation=None,
        failure_code=failure_code,
        tool_calls=(),
        steps=1,
        human_escalated=True,
        requires_human_approval=requires_human_approval,
        cost_units=0,
        fixture_latency_ms=PREFLIGHT_LATENCY_MS,
        unsafe_actions=(),
    )


def _postrun_observation(
    case_id: str,
    calls: tuple[ToolCall, ...],
    *,
    status: AgentStatus,
    recommendation: RecommendationValue | None,
    failure_code: str | None,
    human_escalated: bool,
    requires_human_approval: bool,
) -> AgentObservation:
    return AgentObservation(
        case_id=case_id,
        status=status,
        recommendation=recommendation,
        failure_code=failure_code,
        tool_calls=calls,
        steps=1 + len(calls),
        human_escalated=human_escalated,
        requires_human_approval=requires_human_approval,
        cost_units=sum(call.cost_units for call in calls),
        fixture_latency_ms=_fixture_latency(calls),
        unsafe_actions=(),
    )


def run_candidate(case: EvaluationCase) -> AgentObservation:
    """Run one visible case against the bounded Procurement Agent v1 adapter."""
    try:
        request = AgentRequest.model_validate(case.payload)
    except ValidationError:
        return _preflight_observation(
            case.case_id,
            failure_code="invalid_request",
            requires_human_approval=False,
        )

    if request.requested_action != "investigate":
        return _preflight_observation(
            case.case_id,
            failure_code="approval_required",
            requires_human_approval=True,
        )

    procurement_case = _case_for(request, case.scenario)
    result = Supervisor(_registry_for(case.scenario)).run(
        procurement_case,
        run_id=request.run_id,
    )
    calls = _calls_from_trace(
        result.trace,
        request,
        procurement_case,
        case.scenario,
    )
    if result.report is None:
        return _postrun_observation(
            case.case_id,
            calls,
            status="failed",
            recommendation=None,
            failure_code=result.failure_reason,
            human_escalated=True,
            requires_human_approval=False,
        )

    recommendation = RECOMMENDATION_VALUES[result.report.recommendation]
    status: AgentStatus = (
        "escalated" if recommendation == "needs_human" else "completed"
    )
    return _postrun_observation(
        case.case_id,
        calls,
        status=status,
        recommendation=recommendation,
        failure_code=None,
        human_escalated=recommendation == "needs_human",
        requires_human_approval=result.report.requires_human_approval,
    )
