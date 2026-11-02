"""Behavior checks for the Week 15 LangGraph fundamentals lab."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
from typing import cast

from langgraph.types import Interrupt
import pytest

from labs.week_15.fixtures import CASES, analyze_order_sql
from labs.week_15.graph import GraphRuntime, validate_report
from labs.week_15.models import (
    ApprovalDecision,
    ApprovalResponse,
    InvestigationState,
    Recommendation,
)


ROOT = Path(__file__).resolve().parents[1]


def _pause(runtime: GraphRuntime, case_name: str, thread_id: str) -> dict[str, object]:
    case = CASES[case_name]
    return runtime.start(case["case_id"], case["query"], thread_id=thread_id)


def _interrupt(result: dict[str, object]) -> Interrupt:
    values = result["__interrupt__"]
    assert isinstance(values, (list, tuple)) and len(values) == 1
    value = values[0]
    assert isinstance(value, Interrupt)
    return value


def test_graph_exposes_the_reviewed_nodes_and_routes() -> None:
    runtime = GraphRuntime()
    graph = runtime.graph.get_graph()
    assert set(graph.nodes) == {
        "__start__",
        "classify_query",
        "unsupported_query",
        "retrieve_documents",
        "analyze_sql",
        "calculate_price",
        "generate_recommendation",
        "validate_report",
        "human_approval",
        "__end__",
    }
    edges = {(edge.source, edge.target, edge.conditional) for edge in graph.edges}
    assert ("retrieve_documents", "analyze_sql", False) in edges
    assert ("validate_report", "human_approval", True) in edges
    assert ("human_approval", "__end__", False) in edges


def test_price_spike_accumulates_evidence_and_pauses_at_typed_interrupt() -> None:
    runtime = GraphRuntime()
    result = _pause(runtime, "price-spike", "price-spike-thread")
    assert result["approval_status"] == "awaiting_approval"
    assert result["recommendation"] == "review_required"
    assert result["variance_percent"] == "10.00"
    assert result["evidence"] == [
        "document:contract-1501-v1:found",
        "sql:price_analysis:PO-1501",
    ]
    assert result["trace"] == [
        "classify_query:procurement_price_investigation",
        "retrieve_documents:found",
        "analyze_sql:complete",
        "calculate_price:10.00%",
        "generate_recommendation:review_required",
        "validate_report:passed",
    ]
    pause = _interrupt(result)
    assert isinstance(pause.value, dict)
    assert pause.value["report_digest"] == result["report_digest"]
    assert pause.response_schema is not None
    assert pause.response_schema["required"] == [
        "decision",
        "reviewer",
        "report_digest",
    ]
    checkpoint = runtime.state("price-spike-thread")
    assert checkpoint["report_digest"] == result["report_digest"]
    assert runtime.checkpoint_count("price-spike-thread") >= 8


@pytest.mark.parametrize(
    ("case_name", "recommendation", "variance"),
    [
        ("price-spike", "review_required", "10.00"),
        ("stable-price", "no_review", "2.00"),
        ("missing-terms", "needs_human", "10.00"),
    ],
)
def test_conditional_business_results_still_require_human_review(
    case_name: str,
    recommendation: Recommendation,
    variance: str,
) -> None:
    runtime = GraphRuntime()
    result = _pause(runtime, case_name, f"thread-{case_name}")
    assert result["recommendation"] == recommendation
    assert result["variance_percent"] == variance
    assert result["approval_status"] == "awaiting_approval"
    assert _interrupt(result).value["kind"] == "human_approval"


@pytest.mark.parametrize(
    ("decision", "status"),
    [("approve", "approved"), ("reject", "rejected")],
)
def test_resume_uses_the_same_thread_and_exact_report_snapshot(
    decision: str, status: str
) -> None:
    runtime = GraphRuntime()
    paused = _pause(runtime, "price-spike", f"resume-{decision}")
    report_before = deepcopy(paused["report"])
    final = runtime.resume(
        f"resume-{decision}",
        ApprovalResponse(
            decision=cast(ApprovalDecision, decision),
            reviewer="reviewer-15",
            report_digest=str(paused["report_digest"]),
        ),
    )
    assert final["approval_status"] == status
    assert final["reviewer"] == "reviewer-15"
    assert final["report"] == report_before
    trace = cast(list[str], final["trace"])
    assert trace.count("validate_report:passed") == 1
    assert trace[-1] == f"human_approval:{decision}:reviewer-15"


def test_wrong_digest_is_rejected_and_another_thread_cannot_resume() -> None:
    runtime = GraphRuntime()
    _pause(runtime, "price-spike", "digest-thread")
    with pytest.raises(ValueError, match="approval_report_mismatch"):
        runtime.resume(
            "digest-thread",
            ApprovalResponse(
                decision="approve",
                reviewer="reviewer-15",
                report_digest="0" * 64,
            ),
        )
    with pytest.raises(ValueError, match="thread_not_waiting_for_approval"):
        runtime.resume(
            "different-thread",
            ApprovalResponse(
                decision="approve",
                reviewer="reviewer-15",
                report_digest="0" * 64,
            ),
        )


def test_threads_are_isolated_and_duplicate_start_is_rejected() -> None:
    runtime = GraphRuntime()
    spike = _pause(runtime, "price-spike", "isolated-spike")
    stable = _pause(runtime, "stable-price", "isolated-stable")
    assert spike["report_digest"] != stable["report_digest"]
    assert runtime.state("isolated-spike")["case_id"] == "price-spike"
    assert runtime.state("isolated-stable")["case_id"] == "stable-price"
    with pytest.raises(ValueError, match="thread_already_exists"):
        _pause(runtime, "price-spike", "isolated-spike")


def test_unsupported_query_routes_to_end_without_tools_or_interrupt() -> None:
    runtime = GraphRuntime()
    result = runtime.start(
        "price-spike", "Write a poem about steel.", thread_id="unsupported"
    )
    assert result["approval_status"] == "unsupported"
    assert result["failure_reason"] == "unsupported_query_or_case"
    assert result["trace"] == [
        "classify_query:unsupported",
        "unsupported_query:end",
    ]
    assert "sql_analysis" not in result
    assert "__interrupt__" not in result


def test_validation_fails_closed_when_required_evidence_is_absent() -> None:
    malformed: InvestigationState = {
        "case_id": "malformed",
        "query": "Investigate a price.",
        "evidence": [],
        "trace": [],
    }
    update = validate_report(malformed)
    assert update["valid"] is False
    assert update["approval_status"] == "validation_failed"
    assert update["validation_errors"] == [
        "sql_analysis_required",
        "contract_result_required",
        "recommendation_required",
        "variance_required",
        "sql_evidence_required",
        "document_evidence_required",
    ]


def test_sql_analysis_is_parameterized_and_unknown_order_is_controlled() -> None:
    row = analyze_order_sql("PO-1501")
    assert row["supplier_id"] == "SUP-115"
    with pytest.raises(ValueError, match="purchase_order_not_found"):
        analyze_order_sql("PO-1501' OR 1=1 --")


def test_cli_smoke_and_resume_demo_are_machine_readable() -> None:
    smoke = subprocess.run(
        [sys.executable, "-m", "labs.week_15.demo", "smoke"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(smoke.stdout) == {"checks": 10, "status": "ok"}
    resumed = subprocess.run(
        [
            sys.executable,
            "-m",
            "labs.week_15.demo",
            "resume-demo",
            "--decision",
            "reject",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    output = json.loads(resumed.stdout)
    assert output["status"] == "rejected"
    assert output["interrupt"] is None
