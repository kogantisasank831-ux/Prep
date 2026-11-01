"""Behavior checks for the Week 14 workflow-versus-agent comparison."""

from dataclasses import replace
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys
from typing import cast

import pytest

from labs.week_14.controllers import (
    PLANNER_SCRIPTS,
    ScriptedPlanner,
    comparison,
    run_agent,
    run_workflow,
)
from labs.week_14.models import (
    ApprovalDecision,
    HumanApproval,
    ProcurementCase,
    Recommendation,
    RunStatus,
    finalize,
)
from labs.week_14.tools import CASES

ROOT = Path(__file__).resolve().parents[1]


def test_workflow_follows_fixed_route_and_waits_for_human() -> None:
    result = run_workflow(CASES["price-spike"])
    assert result.status is RunStatus.AWAITING_APPROVAL
    assert result.report is not None
    assert result.report.recommendation is Recommendation.REVIEW_REQUIRED
    assert result.metrics.model_calls == 0
    assert result.metrics.tool_calls == 5
    assert result.metrics.modeled_latency_ms == 20
    assert result.trace == (
        "workflow:start",
        "workflow:load_order:complete",
        "workflow:lookup_supplier:complete",
        "workflow:get_reference_price:complete",
        "workflow:calculate_variance:complete",
        "workflow:search_contract_terms:complete",
        "workflow:awaiting_approval",
    )


def test_happy_agent_reaches_same_report_through_validated_proposals() -> None:
    workflow = run_workflow(CASES["price-spike"])
    agent = run_agent(CASES["price-spike"], ScriptedPlanner(PLANNER_SCRIPTS["happy"]))
    assert agent.status is RunStatus.AWAITING_APPROVAL
    assert agent.report == workflow.report
    assert agent.metrics.model_calls == 6
    assert agent.metrics.tool_calls == 5
    assert agent.metrics.input_tokens == 1245
    assert agent.metrics.output_tokens == 72
    assert agent.metrics.estimated_model_cost_usd == "0.001461"
    assert agent.metrics.modeled_latency_ms == 560


@pytest.mark.parametrize(
    ("case_name", "recommendation"),
    [
        ("price-spike", Recommendation.REVIEW_REQUIRED),
        ("stable-price", Recommendation.NO_REVIEW),
        ("missing-terms", Recommendation.NEEDS_HUMAN),
    ],
)
def test_business_decision_is_shared_across_routes(
    case_name: str, recommendation: Recommendation
) -> None:
    workflow = run_workflow(CASES[case_name])
    agent = run_agent(CASES[case_name], ScriptedPlanner(PLANNER_SCRIPTS["detour"]))
    assert workflow.report is not None and agent.report is not None
    assert workflow.report.recommendation is recommendation
    assert agent.report == workflow.report


def test_agent_executor_enforces_dependencies_even_for_allowed_actions() -> None:
    planner = ScriptedPlanner(
        (
            "calculate_variance",
            "load_order",
            "lookup_supplier",
            "get_reference_price",
            "calculate_variance",
            "search_contract_terms",
            "finish",
        )
    )
    result = run_agent(CASES["price-spike"], planner)
    assert result.status is RunStatus.AWAITING_APPROVAL
    assert "executor:rejected:order_required" in result.trace
    assert result.metrics.tool_calls == 6


def test_repeated_action_terminates_without_repeating_tool_execution() -> None:
    result = run_agent(CASES["price-spike"], ScriptedPlanner(PLANNER_SCRIPTS["loop"]))
    assert result.status is RunStatus.FAILED
    assert result.failure_reason == "duplicate_action"
    assert result.metrics.model_calls == 8
    assert result.metrics.tool_calls == 1
    assert result.trace.count("executor:completed:load_order") == 1


def test_unsupported_action_never_reaches_tool_executor() -> None:
    result = run_agent(CASES["price-spike"], ScriptedPlanner(PLANNER_SCRIPTS["unsafe"]))
    assert result.status is RunStatus.FAILED
    assert result.failure_reason == "unsupported_action"
    assert result.metrics.tool_calls == 1
    assert "planner:proposed:send_supplier_email" in result.trace
    assert "executor:rejected:unsupported_action" in result.trace


def test_unknown_order_fails_with_a_controlled_reason() -> None:
    result = run_workflow(ProcurementCase("unknown", "PO-DOES-NOT-EXIST"))
    assert result.status is RunStatus.FAILED
    assert result.failure_reason == "order_not_found"
    assert result.report is None


def test_approval_is_bound_to_exact_report_snapshot_and_reviewer() -> None:
    result = run_workflow(CASES["price-spike"])
    assert result.report is not None
    approval = HumanApproval(
        result.report.digest(), "reviewer-1", ApprovalDecision.APPROVE
    )
    approved = finalize(result, approval)
    assert approved.status is RunStatus.APPROVED
    assert approved.trace[-1] == "human:approve:reviewer-1"

    changed = replace(result.report, summary=result.report.summary + " changed")
    tampered = replace(result, report=changed)
    with pytest.raises(ValueError, match="approval_report_mismatch"):
        finalize(tampered, approval)
    with pytest.raises(ValueError, match="reviewer_required"):
        finalize(
            result,
            HumanApproval(result.report.digest(), " ", ApprovalDecision.REJECT),
        )
    with pytest.raises(ValueError, match="approval_invalid"):
        finalize(
            result,
            HumanApproval(
                result.report.digest(),
                "reviewer-1",
                cast(ApprovalDecision, "approve"),
            ),
        )


def test_comparison_labels_the_control_scenarios() -> None:
    rows = comparison(CASES["price-spike"])
    assert rows["workflow"] == {
        "runs": 4,
        "successful_investigations": 4,
        "failures": 0,
        "failure_rate": "0.0%",
        "average_model_calls": 0.0,
        "average_tool_calls": 5.0,
        "total_estimated_model_cost_usd": "0.000000",
        "average_modeled_latency_ms": 20.0,
        "explainability": "fixed transition log",
    }
    assert rows["agent"]["runs"] == 4
    assert rows["agent"]["successful_investigations"] == 2
    assert rows["agent"]["failure_rate"] == "50.0%"
    assert Decimal(str(rows["agent"]["total_estimated_model_cost_usd"])) > 0
    assert rows["agent"]["explainability"] == "proposal and execution log"


def test_cli_smoke_and_comparison_are_machine_readable() -> None:
    smoke = subprocess.run(
        [sys.executable, "-m", "labs.week_14.demo", "smoke"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(smoke.stdout) == {"checks": 8, "status": "ok"}
    compared = subprocess.run(
        [sys.executable, "-m", "labs.week_14.demo", "compare"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(compared.stdout)["agent"]["failures"] == 2
