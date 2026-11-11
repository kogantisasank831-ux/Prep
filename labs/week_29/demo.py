"""CLI for the Week 29 comparable model-evaluation lab."""

from __future__ import annotations

import argparse
import json

from labs.week_29.evaluation import evaluate_candidates
from labs.week_29.models import (
    CandidateOutput,
    EvaluationConfig,
    EvaluationExample,
    PairwiseVote,
)


def sample_examples() -> tuple[EvaluationExample, ...]:
    return (
        EvaluationExample(
            example_id="e1", task="qa", segment="policy", expected="30 days"
        ),
        EvaluationExample(
            example_id="e2", task="qa", segment="extraction", expected="INR"
        ),
        EvaluationExample(
            example_id="e3", task="classification", segment="risk", expected="review"
        ),
        EvaluationExample(
            example_id="e4", task="classification", segment="risk", expected="approve"
        ),
        EvaluationExample(
            example_id="e5",
            task="qa",
            segment="policy",
            expected="7 days",
            contaminated=True,
        ),
        EvaluationExample(
            example_id="e6", task="classification", segment="risk", expected="review"
        ),
    )


def sample_outputs() -> tuple[CandidateOutput, ...]:
    responses = {
        "base": ("45 days", "USD", "review", "approve", "unknown", "approve"),
        "prompted_base": ("30 days", "USD", "review", "approve", "unknown", "approve"),
        "fine_tuned": ("30 days", "INR", "review", "approve", "7 days", "approve"),
        "rag": ("30 days", "INR", "review", "approve", "7 days", "review"),
    }
    nll = {"base": 1.2, "prompted_base": 1.0, "fine_tuned": 0.8, "rag": 0.7}
    return tuple(
        CandidateOutput(
            candidate=candidate,
            example_id=example.example_id,
            response=response,
            negative_log_likelihood=nll[candidate],
        )
        for candidate, candidate_responses in responses.items()
        for example, response in zip(
            sample_examples(), candidate_responses, strict=True
        )
    )


def sample_votes() -> tuple[PairwiseVote, ...]:
    return (
        PairwiseVote(
            case_id="p1",
            reviewer_id="r1",
            left_candidate="fine_tuned",
            right_candidate="rag",
            winner="right",
        ),
        PairwiseVote(
            case_id="p1",
            reviewer_id="r2",
            left_candidate="fine_tuned",
            right_candidate="rag",
            winner="tie",
        ),
        PairwiseVote(
            case_id="p2",
            reviewer_id="r1",
            left_candidate="fine_tuned",
            right_candidate="rag",
            winner="right",
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("evaluate", "smoke"), nargs="?", default="evaluate"
    )
    parser.add_argument("--include-contaminated", action="store_true")
    args = parser.parse_args()
    report = evaluate_candidates(
        sample_examples(),
        sample_outputs(),
        sample_votes(),
        EvaluationConfig(include_contaminated=args.include_contaminated),
    )
    print(json.dumps(report.model_dump(mode="json"), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
