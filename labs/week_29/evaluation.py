"""Comparable metrics, paired uncertainty and preference summaries."""

from __future__ import annotations

from collections import defaultdict
import math
import random
import re

from labs.week_29.models import (
    BaselineComparison,
    CandidateMetrics,
    CandidateOutput,
    EvaluationConfig,
    EvaluationExample,
    EvaluationReport,
    PairwiseSummary,
    PairwiseVote,
    SegmentMetric,
)


SPACE_PATTERN = re.compile(r"\s+")


def normalise_answer(value: str) -> str:
    """Apply the declared exact-match normalisation only."""

    return SPACE_PATTERN.sub(" ", value).strip().lower()


def _safe_ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = round((len(ordered) - 1) * fraction)
    return ordered[index]


def _bootstrap_delta(
    candidate: list[int], baseline: list[int], config: EvaluationConfig
) -> tuple[float, float]:
    rng = random.Random(config.seed)
    count = len(candidate)
    deltas: list[float] = []
    for _ in range(config.bootstrap_samples):
        indexes = [rng.randrange(count) for _ in range(count)]
        deltas.append(
            sum(candidate[index] - baseline[index] for index in indexes) / count
        )
    return _percentile(deltas, 0.025), _percentile(deltas, 0.975)


def evaluate_candidates(
    examples: tuple[EvaluationExample, ...],
    outputs: tuple[CandidateOutput, ...],
    votes: tuple[PairwiseVote, ...],
    config: EvaluationConfig,
) -> EvaluationReport:
    """Evaluate every candidate on the same frozen eligible examples."""

    if not examples:
        raise ValueError("examples_required")
    if len({example.example_id for example in examples}) != len(examples):
        raise ValueError("duplicate_example_id")
    candidates = tuple(sorted({output.candidate for output in outputs}))
    if config.baseline_candidate not in candidates:
        raise ValueError("baseline_candidate_missing")
    output_index: dict[tuple[str, str], CandidateOutput] = {}
    for output in outputs:
        key = (output.candidate, output.example_id)
        if key in output_index:
            raise ValueError("duplicate_candidate_output")
        output_index[key] = output
    expected_keys = {
        (candidate, example.example_id)
        for candidate in candidates
        for example in examples
    }
    if set(output_index) != expected_keys:
        raise ValueError("candidate_output_matrix_incomplete")

    eligible = tuple(
        example
        for example in examples
        if config.include_contaminated or not example.contaminated
    )
    if not eligible:
        raise ValueError("no_eligible_examples")
    excluded = tuple(
        example.example_id
        for example in examples
        if example.contaminated and not config.include_contaminated
    )
    correctness: dict[str, list[int]] = {}
    metrics: list[CandidateMetrics] = []
    for candidate in candidates:
        flags = [
            int(
                normalise_answer(output_index[(candidate, example.example_id)].response)
                == normalise_answer(example.expected)
            )
            for example in eligible
        ]
        correctness[candidate] = flags
        classification = [
            example for example in eligible if example.task == "classification"
        ]
        true_positive = false_positive = false_negative = 0
        for example in classification:
            expected_positive = normalise_answer(example.expected) == normalise_answer(
                config.positive_label
            )
            predicted_positive = normalise_answer(
                output_index[(candidate, example.example_id)].response
            ) == normalise_answer(config.positive_label)
            true_positive += int(expected_positive and predicted_positive)
            false_positive += int(not expected_positive and predicted_positive)
            false_negative += int(expected_positive and not predicted_positive)
        precision = _safe_ratio(true_positive, true_positive + false_positive)
        recall = _safe_ratio(true_positive, true_positive + false_negative)
        f1 = _safe_ratio(
            2 * true_positive, 2 * true_positive + false_positive + false_negative
        )

        nll_values = [
            output_index[(candidate, example.example_id)].negative_log_likelihood
            for example in eligible
        ]
        has_nll = [value is not None for value in nll_values]
        if any(has_nll) and not all(has_nll):
            raise ValueError("negative_log_likelihood_incomplete")
        perplexity = None
        if all(has_nll):
            concrete = [value for value in nll_values if value is not None]
            perplexity = math.exp(sum(concrete) / len(concrete))
        segment_metrics: list[SegmentMetric] = []
        for segment in sorted({example.segment for example in eligible}):
            indexes = [
                index
                for index, example in enumerate(eligible)
                if example.segment == segment
            ]
            segment_metrics.append(
                SegmentMetric(
                    segment=segment,
                    count=len(indexes),
                    exact_match_rate=sum(flags[index] for index in indexes)
                    / len(indexes),
                )
            )
        metrics.append(
            CandidateMetrics(
                candidate=candidate,
                count=len(eligible),
                exact_matches=sum(flags),
                exact_match_rate=sum(flags) / len(flags),
                classification_precision=precision if classification else None,
                classification_recall=recall if classification else None,
                classification_f1=f1 if classification else None,
                perplexity=perplexity,
                segments=tuple(segment_metrics),
            )
        )

    baseline_flags = correctness[config.baseline_candidate]
    comparisons: list[BaselineComparison] = []
    for candidate in candidates:
        if candidate == config.baseline_candidate:
            continue
        low, high = _bootstrap_delta(correctness[candidate], baseline_flags, config)
        comparisons.append(
            BaselineComparison(
                candidate=candidate,
                baseline=config.baseline_candidate,
                exact_match_delta=(sum(correctness[candidate]) - sum(baseline_flags))
                / len(eligible),
                bootstrap_low=low,
                bootstrap_high=high,
            )
        )

    vote_groups: dict[tuple[str, str], list[PairwiseVote]] = defaultdict(list)
    for vote in votes:
        if (
            vote.left_candidate not in candidates
            or vote.right_candidate not in candidates
        ):
            raise ValueError("pairwise_candidate_unknown")
        vote_groups[(vote.left_candidate, vote.right_candidate)].append(vote)
    pairwise = tuple(
        PairwiseSummary(
            left_candidate=left,
            right_candidate=right,
            left_wins=sum(vote.winner == "left" for vote in grouped),
            right_wins=sum(vote.winner == "right" for vote in grouped),
            ties=sum(vote.winner == "tie" for vote in grouped),
        )
        for (left, right), grouped in sorted(vote_groups.items())
    )
    return EvaluationReport(
        evaluated_example_ids=tuple(example.example_id for example in eligible),
        excluded_contaminated_ids=excluded,
        metrics=tuple(metrics),
        comparisons=tuple(comparisons),
        pairwise=pairwise,
        limitations=(
            "Synthetic fixtures do not estimate production quality.",
            "Exact match can reject valid paraphrases and reward shallow matches.",
            "Bootstrap intervals quantify sample variation, not dataset bias.",
            "Human pairwise votes require blinding, rubrics and reviewer agreement.",
            "An LLM judge can inherit bias, position effects and prompt sensitivity.",
        ),
    )
