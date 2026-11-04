"""Behavior checks for the Week 17 supervisor-specialist lab."""

from __future__ import annotations

from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys
from threading import Barrier
from typing import cast

from pydantic import ValidationError
import pytest

from labs.week_17.fixtures import CASES
from labs.week_17.models import (
    Assignment,
    Architecture,
    DocumentAssignment,
    DocumentFinding,
    ProcurementCase,
    Recommendation,
    RunStatus,
    SpecialistName,
    SpecialistResult,
    SqlFinding,
)
from labs.week_17.specialists import (
    DEFAULT_SPECIALISTS,
    SpecialistFailure,
    SpecialistFunction,
    analyze_document,
    analyze_sql,
    assess_supplier_risk,
)
from labs.week_17.supervisor import (
    Supervisor,
    compare_architectures,
    default_supervisor,
    run_single_workflow,
)


ROOT = Path(__file__).resolve().parents[1]


def test_assignments_are_closed_frozen_and_minimal() -> None:
    case = CASES["price-spike"]
    assignment = DocumentAssignment(
        run_id="closed-handoff",
        case_id=case.case_id,
        purchase_order_id=case.purchase_order_id,
        source=case.document_source,
    )
    assert set(assignment.model_dump()) == {
        "run_id",
        "case_id",
        "specialist",
        "purchase_order_id",
        "source",
    }
    with pytest.raises(ValidationError):
        DocumentAssignment.model_validate(
            {**assignment.model_dump(), "raw_conversation": ["do not pass this"]}
        )
    with pytest.raises(ValidationError):
        DocumentAssignment(
            run_id=cast(str, 17),
            case_id=case.case_id,
            purchase_order_id=case.purchase_order_id,
            source=case.document_source,
        )
    with pytest.raises(ValidationError):
        assignment.run_id = "changed"


def test_each_first_wave_specialist_returns_its_owned_finding() -> None:
    result = default_supervisor().run(CASES["price-spike"], run_id="owned")
    assert [finding.specialist for finding in result.findings] == [
        SpecialistName.DOCUMENT,
        SpecialistName.SQL,
        SpecialistName.SUPPLIER_RISK,
    ]
    assert isinstance(result.findings[0], DocumentFinding)
    sql = cast(SqlFinding, result.findings[1])
    assert sql.variance_percent == Decimal("10.00")
    assert result.findings[2].source.source_id == "risk-register-171"


@pytest.mark.parametrize(
    ("case_name", "expected"),
    [
        ("price-spike", Recommendation.REVIEW_REQUIRED),
        ("stable-price", Recommendation.NO_REVIEW),
        ("missing-terms", Recommendation.NEEDS_HUMAN),
        ("supplier-risk", Recommendation.REVIEW_REQUIRED),
    ],
)
def test_supervisor_combines_all_business_scenarios(
    case_name: str, expected: Recommendation
) -> None:
    result = default_supervisor().run(CASES[case_name], run_id=f"case-{case_name}")
    assert result.status is RunStatus.AWAITING_APPROVAL
    assert result.report is not None
    assert result.report.recommendation is expected
    assert result.report.requires_human_approval is True
    assert len(result.report.evidence) == 3


def test_supplier_risk_can_require_review_even_with_stable_price() -> None:
    result = default_supervisor().run(CASES["supplier-risk"], run_id="risk-first")
    assert result.report is not None
    assert result.report.recommendation is Recommendation.REVIEW_REQUIRED
    assert "open incidents: 2" in result.report.summary


def test_first_wave_really_runs_concurrently_but_trace_is_stable() -> None:
    barrier = Barrier(3, timeout=5)
    registry = dict(DEFAULT_SPECIALISTS)

    def synchronized(name: SpecialistName) -> SpecialistFunction:
        original = registry[name]

        def run(assignment: Assignment) -> SpecialistResult:
            barrier.wait()
            return original(assignment)

        return run

    for name in (
        SpecialistName.DOCUMENT,
        SpecialistName.SQL,
        SpecialistName.SUPPLIER_RISK,
    ):
        registry[name] = synchronized(name)

    result = Supervisor(registry).run(CASES["price-spike"], run_id="parallel")
    assert result.status is RunStatus.AWAITING_APPROVAL
    assert result.metrics.parallel_groups == 1
    assert result.metrics.max_parallel_workers == 3
    assert result.trace[1:4] == (
        "supervisor:dispatch:document",
        "supervisor:dispatch:sql",
        "supervisor:dispatch:supplier_risk",
    )
    assert result.trace[4:7] == (
        "supervisor:complete:document",
        "supervisor:complete:sql",
        "supervisor:complete:supplier_risk",
    )


def test_commercial_specialist_runs_only_after_required_results() -> None:
    result = default_supervisor().run(CASES["price-spike"], run_id="dependency")
    commercial = result.trace.index("supervisor:dispatch:commercial")
    assert commercial > result.trace.index("supervisor:complete:document")
    assert commercial > result.trace.index("supervisor:complete:sql")
    assert commercial > result.trace.index("supervisor:complete:supplier_risk")
    assert result.metrics.dependency_stages == 2


def test_output_and_trace_are_deterministic() -> None:
    first = default_supervisor().run(CASES["price-spike"], run_id="repeatable")
    for _ in range(10):
        assert (
            default_supervisor().run(CASES["price-spike"], run_id="repeatable") == first
        )


def test_specialist_exception_fails_closed_without_a_report() -> None:
    registry = dict(DEFAULT_SPECIALISTS)

    def fail(_: Assignment) -> SpecialistResult:
        raise SpecialistFailure("document_service_unavailable")

    registry[SpecialistName.DOCUMENT] = fail
    result = Supervisor(registry).run(CASES["price-spike"], run_id="failed")
    assert result.status is RunStatus.FAILED
    assert result.report is None
    assert result.failure_reason is not None
    assert result.failure_reason.startswith("specialist_failed:document:")
    assert "document_service_unavailable" in result.failure_reason


def test_unexpected_exception_text_is_not_exposed() -> None:
    registry = dict(DEFAULT_SPECIALISTS)

    def fail(_: Assignment) -> SpecialistResult:
        raise RuntimeError("credential-value-must-not-leak")

    registry[SpecialistName.SQL] = fail
    result = Supervisor(registry).run(CASES["price-spike"], run_id="sanitized")
    assert result.failure_reason == "specialist_failed:sql:unexpected_RuntimeError"
    assert "credential-value" not in json.dumps(result.model_dump(mode="json"))


def test_registry_must_contain_every_declared_specialist() -> None:
    registry = dict(DEFAULT_SPECIALISTS)
    del registry[SpecialistName.COMMERCIAL]
    result = Supervisor(registry).run(CASES["price-spike"], run_id="registry")
    assert result.status is RunStatus.FAILED
    assert result.failure_reason == "registry_incomplete:commercial"
    assert result.metrics.specialist_calls == 0


def test_supervisor_copies_the_registry_before_running() -> None:
    registry = dict(DEFAULT_SPECIALISTS)
    supervisor = Supervisor(registry)
    del registry[SpecialistName.COMMERCIAL]
    result = supervisor.run(CASES["stable-price"], run_id="registry-copy")
    assert result.status is RunStatus.AWAITING_APPROVAL
    assert result.report is not None
    assert result.report.recommendation is Recommendation.NO_REVIEW


def test_mismatched_result_identity_is_rejected() -> None:
    registry = dict(DEFAULT_SPECIALISTS)
    original = registry[SpecialistName.DOCUMENT]

    def wrong_case(assignment: Assignment) -> SpecialistResult:
        finding = cast(DocumentFinding, original(assignment))
        return finding.model_copy(update={"case_id": "another-case"})

    registry[SpecialistName.DOCUMENT] = wrong_case
    result = Supervisor(registry).run(CASES["price-spike"], run_id="mismatch")
    assert result.status is RunStatus.FAILED
    assert result.failure_reason is not None
    assert "result_case_mismatch" in result.failure_reason


def test_wrong_specialist_result_type_is_rejected() -> None:
    registry = dict(DEFAULT_SPECIALISTS)
    case = CASES["price-spike"]
    document_assignment = DocumentAssignment(
        run_id="wrong-type",
        case_id=case.case_id,
        purchase_order_id=case.purchase_order_id,
        source=case.document_source,
    )
    document_result = analyze_document(document_assignment)

    def wrong_type(_: Assignment) -> SpecialistResult:
        return document_result

    registry[SpecialistName.SQL] = wrong_type
    result = Supervisor(registry).run(case, run_id="wrong-type")
    assert result.status is RunStatus.FAILED
    assert result.failure_reason is not None
    assert "result_type_mismatch" in result.failure_reason


def test_tampered_source_digest_propagates_as_controlled_failure() -> None:
    case = CASES["price-spike"]
    bad_source = case.document_source.model_copy(update={"content_digest": "0" * 64})
    tampered = case.model_copy(update={"document_source": bad_source})
    result = default_supervisor().run(tampered, run_id="tampered")
    assert result.status is RunStatus.FAILED
    assert result.failure_reason is not None
    assert "document_digest_mismatch" in result.failure_reason


def test_case_is_immutable_and_not_shared_as_working_state() -> None:
    case: ProcurementCase = CASES["price-spike"]
    before = case.model_dump_json()
    result = default_supervisor().run(case, run_id="immutable")
    assert case.model_dump_json() == before
    assert all(
        not hasattr(finding, "purchase_order_id") for finding in result.findings[::2]
    )


def test_single_workflow_reaches_same_report_without_agent_handoffs() -> None:
    case = CASES["price-spike"]
    supervisor = default_supervisor().run(case, run_id="same-outcome")
    workflow = run_single_workflow(case, run_id="same-outcome")
    assert workflow.architecture is Architecture.SINGLE_WORKFLOW
    assert workflow.report == supervisor.report
    assert workflow.metrics.handoffs == 0
    assert supervisor.metrics.handoffs == 4
    assert workflow.metrics.parallel_groups == 0


def test_comparison_is_structural_and_makes_no_latency_claim() -> None:
    compared = compare_architectures(CASES["price-spike"], run_id="compare")
    assert compared.outcome_equal is True
    assert compared.supervisor_dependency_stages == 2
    assert compared.workflow_dependency_stages == 4
    assert compared.measured_latency_ms is None
    assert "Prefer the single workflow" in compared.conclusion


@pytest.mark.parametrize(
    ("function", "assignment"),
    [
        (analyze_document, None),
        (analyze_sql, None),
        (assess_supplier_risk, None),
    ],
)
def test_specialists_reject_the_wrong_handoff_type(
    function: SpecialistFunction, assignment: Assignment | None
) -> None:
    del assignment
    case = CASES["price-spike"]
    wrong = DocumentAssignment(
        run_id="wrong-handoff",
        case_id=case.case_id,
        purchase_order_id=case.purchase_order_id,
        source=case.document_source,
    )
    if function is analyze_document:
        wrong = wrong.model_copy(update={"source": case.sql_source})
        with pytest.raises(SpecialistFailure, match="source_kind_mismatch"):
            function(wrong)
    else:
        with pytest.raises(SpecialistFailure, match="assignment_invalid"):
            function(wrong)


def test_worker_bound_is_enforced() -> None:
    with pytest.raises(ValueError, match="max_workers_out_of_range"):
        Supervisor(DEFAULT_SPECIALISTS, max_workers=0)
    with pytest.raises(ValueError, match="max_workers_out_of_range"):
        Supervisor(DEFAULT_SPECIALISTS, max_workers=4)


def test_cli_smoke_and_comparison_are_machine_readable() -> None:
    smoke = subprocess.run(
        [sys.executable, "-m", "labs.week_17.demo", "smoke"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(smoke.stdout) == {"checks": 10, "status": "ok"}
    compared = subprocess.run(
        [
            sys.executable,
            "-m",
            "labs.week_17.demo",
            "compare",
            "--case",
            "price-spike",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(compared.stdout)
    assert payload["outcome_equal"] is True
    assert payload["measured_latency_ms"] is None
