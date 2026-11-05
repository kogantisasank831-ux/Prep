"""Contract, behavior and metric checks for the Week 18 agent eval lab."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import cast

from pydantic import ValidationError
import pytest

from labs.week_18.agent import expected_tool_arguments, run_candidate
from labs.week_18.evaluation import (
    CATEGORY_ORDER,
    evaluate_dataset,
    load_dataset,
    persist_run,
    run_evaluation,
    score_case,
)
from labs.week_18.models import (
    AgentObservation,
    AgentRequest,
    EvaluationCase,
    EvaluationDataset,
)


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "labs" / "week_18" / "cases.json"


def _dataset() -> EvaluationDataset:
    dataset, _ = load_dataset(DATASET_PATH)
    return dataset


def _case(case_id: str) -> EvaluationCase:
    return next(case for case in _dataset().cases if case.case_id == case_id)


def test_dataset_has_28_versioned_cases_and_every_required_category() -> None:
    dataset, digest = load_dataset(DATASET_PATH)
    counts: dict[str, int] = {}
    for case in dataset.cases:
        counts[case.category] = counts.get(case.category, 0) + 1

    assert dataset.dataset_id == "week18-procurement-agent-v1"
    assert dataset.version == "1.0.0"
    assert len(dataset.cases) == 28
    assert len({case.case_id for case in dataset.cases}) == 28
    assert counts == {
        "normal": 6,
        "missing_information": 4,
        "tool_failure": 4,
        "conflicting_evidence": 4,
        "prompt_injection": 4,
        "invalid_tool_arguments": 3,
        "approval_required": 3,
    }
    assert len(digest) == 64


def test_dataset_loader_rejects_duplicate_keys_nonfinite_values_and_size(
    tmp_path: Path,
) -> None:
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text('{"schema": "one", "schema": "two"}', encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate_json_key:schema"):
        load_dataset(duplicate)

    nonfinite = tmp_path / "nonfinite.json"
    nonfinite.write_text('{"value": NaN}', encoding="utf-8")
    with pytest.raises(ValueError, match="non_finite_json_constant:NaN"):
        load_dataset(nonfinite)

    oversized = tmp_path / "oversized.json"
    oversized.write_bytes(b" " * 512_001)
    with pytest.raises(ValueError, match="dataset_too_large"):
        load_dataset(oversized)


def test_request_boundary_is_closed_strict_and_frozen() -> None:
    request = AgentRequest(
        run_id="strict-request",
        objective="investigate_procurement_case",
        case_name="price-spike",
        requested_action="investigate",
    )
    with pytest.raises(ValidationError):
        AgentRequest.model_validate(
            {**request.model_dump(), "supplier_override": "SUP-999"}
        )
    with pytest.raises(ValidationError):
        AgentRequest.model_validate({**request.model_dump(), "run_id": 18})
    with pytest.raises(ValidationError):
        request.run_id = "changed"


def test_every_visible_case_reaches_its_declared_safe_end_state() -> None:
    dataset = _dataset()
    for case in dataset.cases:
        observation = run_candidate(case)
        score = score_case(case, observation)
        assert score.task_success, (case.case_id, score.failures)
        assert score.outcome_correct
        assert score.tool_selection_correct
        assert not score.loop_detected
        assert not score.unsafe_action


def test_baseline_metrics_keep_counts_and_denominators_visible() -> None:
    run = run_evaluation(DATASET_PATH)
    metrics = run.overall
    assert metrics.cases == 28
    assert metrics.successful_cases == 28
    assert metrics.task_completion_rate == 1
    assert metrics.tool_selection_accuracy == 1
    assert metrics.expected_tool_arguments == 73
    assert metrics.correct_tool_arguments == 72
    assert metrics.tool_argument_accuracy == 0.986301
    assert metrics.mean_step_efficiency == 1
    assert metrics.loop_rate == 0
    assert metrics.human_escalation_rate == 0.642857
    assert metrics.total_cost_units == 265
    assert metrics.cost_units_per_successful_task == 9.464286
    assert metrics.mean_fixture_latency_ms == 12.357143
    assert metrics.unsafe_action_rate == 0
    assert run.status_counts == {"completed": 10, "escalated": 9, "failed": 9}


def test_category_slices_are_complete_and_do_not_invent_argument_credit() -> None:
    run = run_evaluation(DATASET_PATH)
    assert tuple(row.category for row in run.categories) == CATEGORY_ORDER
    approval = next(
        row.metrics for row in run.categories if row.category == "approval_required"
    )
    invalid = next(
        row.metrics
        for row in run.categories
        if row.category == "invalid_tool_arguments"
    )
    assert approval.cases == 3
    assert approval.expected_tool_arguments == 0
    assert approval.tool_argument_accuracy is None
    assert approval.total_cost_units == 0
    assert invalid.expected_tool_arguments == 3
    assert invalid.correct_tool_arguments == 2
    assert invalid.tool_argument_accuracy == 0.666667


@pytest.mark.parametrize("case_id", ["W18-019", "W18-020", "W18-021", "W18-022"])
def test_prompt_injection_text_is_inert_and_never_reaches_tool_arguments(
    case_id: str,
) -> None:
    case = _case(case_id)
    payload = dict(case.payload)
    untrusted = cast(str, payload.pop("untrusted_text"))
    clean = case.model_copy(update={"payload": payload})
    injected_observation = run_candidate(case)
    clean_observation = run_candidate(clean)

    assert injected_observation == clean_observation
    assert untrusted not in json.dumps(
        [call.arguments for call in injected_observation.tool_calls],
        sort_keys=True,
    )


@pytest.mark.parametrize("case_id", ["W18-026", "W18-027", "W18-028"])
def test_approval_required_actions_stop_before_tools(case_id: str) -> None:
    observation = run_candidate(_case(case_id))
    assert observation.status == "escalated"
    assert observation.failure_code == "approval_required"
    assert observation.tool_calls == ()
    assert observation.requires_human_approval
    assert observation.unsafe_actions == ()


def test_invalid_sql_argument_is_detected_separately_from_task_completion() -> None:
    case = _case("W18-025")
    observation = run_candidate(case)
    score = score_case(case, observation)

    assert observation.status == "failed"
    assert observation.failure_code == "specialist_failed:sql:sql_supplier_mismatch"
    assert observation.tool_calls[1].arguments["selected_supplier_id"] == "SUP-INVALID"
    assert score.task_success
    assert score.tool_selection_correct
    assert score.tool_argument_correct == 2
    assert score.tool_argument_total == 3
    assert score.failures == ("tool_argument_mismatch",)


def test_expected_arguments_are_independent_of_the_fault_adapter() -> None:
    case = _case("W18-025")
    expected = expected_tool_arguments(case)
    assert expected[1]["selected_supplier_id"] == "SUP-171"
    assert run_candidate(case).tool_calls[1].arguments != expected[1]


def test_graders_detect_wrong_outcome_tools_arguments_loops_and_actions() -> None:
    case = _case("W18-001")
    baseline = run_candidate(case)
    wrong_outcome = baseline.model_copy(update={"recommendation": "no_review"})
    assert "outcome_mismatch" in score_case(case, wrong_outcome).failures

    first_call = baseline.tool_calls[0].model_copy(
        update={"arguments": {"run_id": "wrong"}}
    )
    wrong_arguments = baseline.model_copy(
        update={"tool_calls": (first_call, *baseline.tool_calls[1:])}
    )
    assert "tool_argument_mismatch" in score_case(case, wrong_arguments).failures

    duplicate = baseline.tool_calls[-1].model_copy(update={"step": 6})
    looped = AgentObservation(
        case_id=baseline.case_id,
        status=baseline.status,
        recommendation=baseline.recommendation,
        failure_code=baseline.failure_code,
        tool_calls=(*baseline.tool_calls, duplicate),
        steps=baseline.steps + 1,
        human_escalated=baseline.human_escalated,
        requires_human_approval=baseline.requires_human_approval,
        cost_units=baseline.cost_units + duplicate.cost_units,
        fixture_latency_ms=baseline.fixture_latency_ms,
        unsafe_actions=("purchase_order",),
    )
    loop_score = score_case(case, looped)
    assert not loop_score.task_success
    assert {
        "tool_selection_mismatch",
        "step_inefficient",
        "loop_detected",
        "unsafe_action",
    }.issubset(loop_score.failures)


def test_fixture_latency_uses_parallel_critical_path_not_tool_sum() -> None:
    complete = run_candidate(_case("W18-001"))
    first_wave_failure = run_candidate(_case("W18-011"))
    preflight = run_candidate(_case("W18-007"))
    assert complete.fixture_latency_ms == 1 + 12 + 6
    assert first_wave_failure.fixture_latency_ms == 1 + 12
    assert preflight.fixture_latency_ms == 1


def test_replay_is_deterministic_and_bound_to_dataset_digest() -> None:
    first = run_evaluation(DATASET_PATH)
    second = run_evaluation(DATASET_PATH)
    assert first == second
    assert first.dataset_sha256 == load_dataset(DATASET_PATH)[1]
    rebuilt = evaluate_dataset(_dataset(), first.dataset_sha256)
    assert rebuilt == first


def test_results_persist_only_into_a_fresh_directory(tmp_path: Path) -> None:
    output_directory = tmp_path / "run-001"
    run = run_evaluation(DATASET_PATH)
    result_path = persist_run(run, output_directory)
    persisted = json.loads(result_path.read_text(encoding="utf-8"))
    assert persisted["schema"] == "procurement-agent-evaluation-result/1.0.0"
    assert persisted["dataset_sha256"] == run.dataset_sha256
    assert len(persisted["observations"]) == 28
    with pytest.raises(FileExistsError):
        persist_run(run, output_directory)


def test_cli_smoke_is_machine_readable() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "labs.week_18.demo", "smoke"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    assert payload == {
        "cases": 28,
        "checks": 8,
        "status": "ok",
        "task_completion_rate": 1.0,
        "tool_argument_accuracy": 0.986301,
    }
