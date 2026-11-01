"""Deterministic workflow and bounded agent over the same Week 14 tools."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Protocol

from labs.week_14.models import (
    Action,
    InvestigationReport,
    InvestigationState,
    Metrics,
    ProcurementCase,
    Recommendation,
    Route,
    RunResult,
    RunStatus,
    TOOL_ACTIONS,
)
from labs.week_14.tools import FixtureTools, ToolFailure, apply_fact


WORKFLOW_ACTIONS: tuple[Action, ...] = (
    Action.LOAD_ORDER,
    Action.LOOKUP_SUPPLIER,
    Action.GET_REFERENCE_PRICE,
    Action.CALCULATE_VARIANCE,
    Action.SEARCH_CONTRACT_TERMS,
)


class Planner(Protocol):
    """A provider adapter may implement this boundary with structured output."""

    calls: int
    input_tokens: int
    output_tokens: int
    modeled_latency_ms: int
    estimated_cost_usd: Decimal

    def choose(self, state: InvestigationState) -> str: ...


@dataclass
class ScriptedPlanner:
    """Repeatable model stand-in; its metrics are teaching assumptions."""

    choices: tuple[str, ...]
    input_price_per_million: Decimal = Decimal("1.00")
    output_price_per_million: Decimal = Decimal("3.00")
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    modeled_latency_ms: int = 0
    estimated_cost_usd: Decimal = Decimal("0")

    def choose(self, state: InvestigationState) -> str:
        observed = len(state.completed)
        prompt_tokens = 120 + (observed * 35) + (20 if state.last_error else 0)
        completion_tokens = 12
        self.calls += 1
        self.input_tokens += prompt_tokens
        self.output_tokens += completion_tokens
        self.modeled_latency_ms += 70 + (observed * 8)
        self.estimated_cost_usd += (
            Decimal(prompt_tokens) * self.input_price_per_million
            + Decimal(completion_tokens) * self.output_price_per_million
        ) / Decimal("1000000")
        position = self.calls - 1
        return self.choices[position] if position < len(self.choices) else Action.FINISH


PLANNER_SCRIPTS: dict[str, tuple[str, ...]] = {
    "happy": tuple(action.value for action in (*WORKFLOW_ACTIONS, Action.FINISH)),
    "detour": (
        Action.LOAD_ORDER,
        Action.SEARCH_CONTRACT_TERMS,
        Action.LOOKUP_SUPPLIER,
        Action.GET_REFERENCE_PRICE,
        Action.CALCULATE_VARIANCE,
        Action.FINISH,
    ),
    "loop": (
        Action.LOAD_ORDER,
        Action.LOAD_ORDER,
        Action.LOAD_ORDER,
        Action.LOAD_ORDER,
        Action.LOAD_ORDER,
        Action.LOAD_ORDER,
        Action.LOAD_ORDER,
        Action.LOAD_ORDER,
    ),
    "unsafe": (
        Action.LOAD_ORDER,
        "send_supplier_email",
        "send_supplier_email",
        "send_supplier_email",
        "send_supplier_email",
        "send_supplier_email",
        "send_supplier_email",
        "send_supplier_email",
    ),
}


def _build_report(state: InvestigationState) -> InvestigationReport:
    if not state.ready_for_report():
        raise ValueError("investigation_incomplete")
    assert state.order is not None
    assert state.supplier is not None
    assert state.reference_price is not None
    assert state.variance is not None
    assert state.contract_terms is not None
    terms = state.contract_terms
    if not terms.found or terms.max_variance_percent is None:
        recommendation = Recommendation.NEEDS_HUMAN
        reason = "The applicable price-variance term was not found."
    elif state.supplier.status != "active":
        recommendation = Recommendation.REVIEW_REQUIRED
        reason = f"Supplier status is {state.supplier.status}."
    elif state.variance.percent > terms.max_variance_percent:
        recommendation = Recommendation.REVIEW_REQUIRED
        reason = (
            f"The {state.variance.percent}% variance exceeds the "
            f"{terms.max_variance_percent}% contract threshold."
        )
    else:
        recommendation = Recommendation.NO_REVIEW
        reason = (
            f"The {state.variance.percent}% variance is within the "
            f"{terms.max_variance_percent}% contract threshold."
        )
    summary = (
        f"{state.order.purchase_order_id}: {reason} Human approval is required "
        "before this report is accepted."
    )
    evidence = (
        f"order:{state.order.purchase_order_id}",
        f"supplier:{state.supplier.supplier_id}",
        f"reference:{state.reference_price.commodity_id}:{state.reference_price.as_of}",
        f"contract:{terms.purchase_order_id}:{'found' if terms.found else 'missing'}",
    )
    return InvestigationReport(
        state.case.case_id,
        state.order.purchase_order_id,
        recommendation,
        summary,
        evidence,
    )


def _metrics(
    tools: FixtureTools,
    trace: list[str],
    planner: Planner | None = None,
) -> Metrics:
    model_calls = planner.calls if planner else 0
    input_tokens = planner.input_tokens if planner else 0
    output_tokens = planner.output_tokens if planner else 0
    model_latency = planner.modeled_latency_ms if planner else 0
    cost = planner.estimated_cost_usd if planner else Decimal("0")
    return Metrics(
        model_calls=model_calls,
        tool_calls=tools.calls,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        estimated_model_cost_usd=str(
            cost.quantize(Decimal("0.000001"), rounding=ROUND_HALF_EVEN)
        ),
        modeled_latency_ms=model_latency + tools.modeled_latency_ms,
        trace_events=len(trace),
    )


def _failed(
    route: Route,
    reason: str,
    tools: FixtureTools,
    trace: list[str],
    planner: Planner | None = None,
) -> RunResult:
    trace.append(f"{route}:failed:{reason}")
    return RunResult(
        route,
        RunStatus.FAILED,
        None,
        _metrics(tools, trace, planner),
        tuple(trace),
        reason,
    )


def run_workflow(case: ProcurementCase) -> RunResult:
    """Execute the explicit state machine and stop at human approval."""
    tools = FixtureTools()
    state = InvestigationState(case)
    trace = ["workflow:start"]
    for action in WORKFLOW_ACTIONS:
        try:
            fact = tools.execute(action, state)
            apply_fact(state, action, fact)
        except ToolFailure as error:
            return _failed(Route.WORKFLOW, str(error), tools, trace)
        trace.append(f"workflow:{action}:complete")
    report = _build_report(state)
    trace.append("workflow:awaiting_approval")
    return RunResult(
        Route.WORKFLOW,
        RunStatus.AWAITING_APPROVAL,
        report,
        _metrics(tools, trace),
        tuple(trace),
    )


def run_agent(
    case: ProcurementCase,
    planner: Planner,
    *,
    max_steps: int = 8,
) -> RunResult:
    """Run a bounded proposal/execution loop and stop at human approval."""
    if not 1 <= max_steps <= 20:
        raise ValueError("max_steps_out_of_range")
    tools = FixtureTools()
    state = InvestigationState(case)
    trace = ["agent:start"]
    for _ in range(max_steps):
        raw_action = planner.choose(state)
        trace.append(f"planner:proposed:{raw_action}")
        try:
            action = Action(raw_action)
        except ValueError:
            state.last_error = "unsupported_action"
            trace.append("executor:rejected:unsupported_action")
            continue
        if action is Action.FINISH:
            if not state.ready_for_report():
                state.last_error = "incomplete_evidence"
                trace.append("executor:rejected:incomplete_evidence")
                continue
            report = _build_report(state)
            trace.append("agent:awaiting_approval")
            return RunResult(
                Route.AGENT,
                RunStatus.AWAITING_APPROVAL,
                report,
                _metrics(tools, trace, planner),
                tuple(trace),
            )
        if action not in TOOL_ACTIONS:
            state.last_error = "unsupported_action"
            trace.append("executor:rejected:unsupported_action")
            continue
        if action in state.completed:
            state.last_error = "duplicate_action"
            trace.append(f"executor:rejected:duplicate:{action}")
            continue
        try:
            fact = tools.execute(action, state)
            apply_fact(state, action, fact)
        except ToolFailure as error:
            state.last_error = str(error)
            trace.append(f"executor:rejected:{error}")
            continue
        trace.append(f"executor:completed:{action}")
    return _failed(
        Route.AGENT,
        state.last_error or "step_budget_exhausted",
        tools,
        trace,
        planner,
    )


def comparison(case: ProcurementCase) -> dict[str, dict[str, object]]:
    """Run four controlled planner scripts against the same case."""
    workflow_results = [run_workflow(case) for _ in PLANNER_SCRIPTS]
    agent_results = [
        run_agent(case, ScriptedPlanner(script)) for script in PLANNER_SCRIPTS.values()
    ]
    return {
        Route.WORKFLOW: _aggregate(workflow_results, "fixed transition log"),
        Route.AGENT: _aggregate(agent_results, "proposal and execution log"),
    }


def _aggregate(results: list[RunResult], explainability: str) -> dict[str, object]:
    runs = len(results)
    failures = sum(result.status is RunStatus.FAILED for result in results)
    return {
        "runs": runs,
        "successful_investigations": runs - failures,
        "failures": failures,
        "failure_rate": f"{(failures / runs) * 100:.1f}%",
        "average_model_calls": round(
            sum(result.metrics.model_calls for result in results) / runs, 2
        ),
        "average_tool_calls": round(
            sum(result.metrics.tool_calls for result in results) / runs, 2
        ),
        "total_estimated_model_cost_usd": str(
            sum(
                (
                    Decimal(result.metrics.estimated_model_cost_usd)
                    for result in results
                ),
                start=Decimal("0"),
            ).quantize(Decimal("0.000001"))
        ),
        "average_modeled_latency_ms": round(
            sum(result.metrics.modeled_latency_ms for result in results) / runs,
            2,
        ),
        "explainability": explainability,
    }
