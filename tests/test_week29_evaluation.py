"""Week 29 comparable model-evaluation contracts."""

from __future__ import annotations

import math
import subprocess
import sys

import pytest
from pydantic import ValidationError

from labs.week_29.demo import sample_examples, sample_outputs, sample_votes
from labs.week_29.evaluation import evaluate_candidates, normalise_answer
from labs.week_29.models import (
    CandidateOutput,
    EvaluationConfig,
    EvaluationReport,
    PairwiseVote,
)


def _report(include_contaminated: bool = False) -> EvaluationReport:
    return evaluate_candidates(
        sample_examples(),
        sample_outputs(),
        sample_votes(),
        EvaluationConfig(include_contaminated=include_contaminated),
    )


def test_answer_normalisation_is_bounded_and_deterministic() -> None:
    assert normalise_answer("  Net\n30 DAYS ") == "net 30 days"
    assert normalise_answer("INR.") != normalise_answer("INR")


def test_candidates_use_same_uncontaminated_examples() -> None:
    report = _report()
    assert report.evaluated_example_ids == ("e1", "e2", "e3", "e4", "e6")
    assert report.excluded_contaminated_ids == ("e5",)
    assert {metric.count for metric in report.metrics} == {5}


def test_expected_exact_match_order_is_visible() -> None:
    metrics = {metric.candidate: metric for metric in _report().metrics}
    assert metrics["base"].exact_match_rate == 2 / 5
    assert metrics["prompted_base"].exact_match_rate == 3 / 5
    assert metrics["fine_tuned"].exact_match_rate == 4 / 5
    assert metrics["rag"].exact_match_rate == 1.0


def test_classification_metrics_use_declared_positive_label() -> None:
    metrics = {metric.candidate: metric for metric in _report().metrics}
    base = metrics["base"]
    assert base.classification_precision == 1.0
    assert base.classification_recall == 0.5
    assert math.isclose(base.classification_f1 or 0.0, 2 / 3)
    assert metrics["rag"].classification_f1 == 1.0


def test_perplexity_uses_mean_negative_log_likelihood() -> None:
    metrics = {metric.candidate: metric for metric in _report().metrics}
    assert math.isclose(metrics["base"].perplexity or 0.0, math.exp(1.2))
    assert math.isclose(metrics["rag"].perplexity or 0.0, math.exp(0.7))


def test_comparisons_are_paired_and_reproducible() -> None:
    first = _report()
    second = _report()
    assert first.comparisons == second.comparisons
    deltas = {item.candidate: item.exact_match_delta for item in first.comparisons}
    assert deltas == {"fine_tuned": 0.4, "prompted_base": 0.2, "rag": 0.6}


def test_pairwise_votes_remain_separate_counts() -> None:
    summary = _report().pairwise[0]
    assert summary.left_candidate == "fine_tuned"
    assert summary.right_candidate == "rag"
    assert (summary.left_wins, summary.right_wins, summary.ties) == (0, 2, 1)


def test_including_contamination_changes_declared_scope() -> None:
    report = _report(include_contaminated=True)
    assert report.excluded_contaminated_ids == ()
    assert len(report.evaluated_example_ids) == 6


def test_duplicate_or_missing_outputs_are_rejected() -> None:
    outputs = sample_outputs()
    with pytest.raises(ValueError, match="duplicate_candidate_output"):
        evaluate_candidates(
            sample_examples(), (*outputs, outputs[0]), (), EvaluationConfig()
        )
    with pytest.raises(ValueError, match="matrix_incomplete"):
        evaluate_candidates(sample_examples(), outputs[:-1], (), EvaluationConfig())


def test_partial_perplexity_inputs_are_rejected() -> None:
    outputs = list(sample_outputs())
    first = outputs[0]
    outputs[0] = CandidateOutput(
        candidate=first.candidate,
        example_id=first.example_id,
        response=first.response,
    )
    with pytest.raises(ValueError, match="negative_log_likelihood_incomplete"):
        evaluate_candidates(sample_examples(), tuple(outputs), (), EvaluationConfig())


def test_unknown_pairwise_candidate_is_rejected() -> None:
    vote = PairwiseVote(
        case_id="x",
        reviewer_id="r",
        left_candidate="base",
        right_candidate="missing",
        winner="left",
    )
    with pytest.raises(ValueError, match="pairwise_candidate_unknown"):
        evaluate_candidates(
            sample_examples(), sample_outputs(), (vote,), EvaluationConfig()
        )


def test_strict_config_and_pair_contracts() -> None:
    with pytest.raises(ValidationError):
        EvaluationConfig(seed=True)
    with pytest.raises(ValidationError, match="distinct"):
        PairwiseVote(
            case_id="x",
            reviewer_id="r",
            left_candidate="base",
            right_candidate="base",
            winner="tie",
        )


def test_cli_smoke() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "labs.week_29.demo", "smoke"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert '"comparisons"' in completed.stdout
    assert '"excluded_contaminated_ids"' in completed.stdout
