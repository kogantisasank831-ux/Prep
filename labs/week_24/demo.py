"""Generate 2-minute, 10-minute and deep project-story practice packs."""

from __future__ import annotations

import argparse
import json
from typing import cast

from labs.week_24.models import (
    DecisionEvidence,
    Depth,
    LeadershipEvidence,
    MetricEvidence,
    ProjectEvidence,
)
from labs.week_24.storytelling import build_story, review_evidence


def sample_evidence() -> ProjectEvidence:
    """Return synthetic evidence whose provenance is deliberately explicit."""

    return ProjectEvidence(
        project_id="supplier-copilot",
        project_name="Synthetic supplier-risk copilot",
        situation=(
            "Analysts manually combined supplier records and policy documents before each review."
        ),
        task=(
            "The team needed a cited read-only assistant while preserving tenant and document permissions."
        ),
        role=(
            "I owned the retrieval and evaluation design within a team that owned ingestion, UI and operations."
        ),
        actions=(
            "I defined permission-aware retrieval and an abstention path for unsupported answers.",
            "I built a versioned evaluation set with answer, citation and authorization cases.",
            "I added trace fields for retrieval, model version, latency and controlled failure codes.",
        ),
        decisions=(
            DecisionEvidence(
                decision="Filter by tenant and document permission before semantic ranking.",
                reason="Post-retrieval filtering could expose unauthorized text to the model.",
                rejected_alternative="Retrieve globally and remove unauthorized citations afterward.",
                consequence="The index and query path required permission metadata and drift tests.",
            ),
            DecisionEvidence(
                decision="Abstain when citation support falls below the accepted threshold.",
                reason="A fluent unsupported answer was more harmful than a visible no-answer result.",
                rejected_alternative="Always return the model's best completion.",
                consequence="Coverage decreased while unsupported-answer risk became observable.",
            ),
        ),
        metrics=(
            MetricEvidence(
                name="grounded-answer acceptance",
                value="18 of 20 synthetic evaluation cases",
                source="versioned Week 24 teaching fixture, run 2026-11-11",
                attribution="team",
            ),
            MetricEvidence(
                name="authorization negatives blocked",
                value="10 of 10 synthetic cases",
                source="versioned Week 24 teaching fixture, run 2026-11-11",
                attribution="team",
            ),
        ),
        failure=(
            "An early fixture allowed stale permission metadata; a negative authorization test detected it, so the team added permission-version checks and blocked stale reads."
        ),
        limitation=(
            "The fixture proves deterministic teaching behavior only; it does not establish production quality, scale or regulatory compliance."
        ),
        reflection=(
            "I would measure permission-change lag and failure behavior earlier, then rehearse rollback before expanding the pilot."
        ),
        leadership=LeadershipEvidence(
            situation="The team disagreed on whether to optimize answer coverage or safety first.",
            action="I proposed shared failure cases and a documented release gate for both goals.",
            result="The team accepted one measurable decision rule and assigned owners for gaps.",
            learning="Concrete cases resolved the disagreement faster than framework preferences.",
        ),
    )


def _smoke() -> dict[str, object]:
    evidence = sample_evidence()
    checks = 0
    expected = {"two-minute": 2, "ten-minute": 10, "deep-dive": 20}
    claim_counts: dict[str, int] = {}
    for depth, minutes in expected.items():
        pack = build_story(evidence, cast(Depth, depth))
        assert pack.estimated_minutes == minutes
        assert pack.project_id == evidence.project_id
        claim_counts[depth] = len(pack.claims)
        checks += 2
    assert claim_counts["two-minute"] < claim_counts["ten-minute"]
    assert claim_counts["ten-minute"] < claim_counts["deep-dive"]
    checks += 2
    review = review_evidence(evidence)
    assert review.gate == "ready_for_mock_interview"
    assert review.total_score == 12
    checks += 2
    assert build_story(evidence, "deep-dive") == build_story(evidence, "deep-dive")
    checks += 1
    return {"checks": checks, "depths": 3, "status": "ok"}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("story", "review", "smoke"))
    parser.add_argument(
        "--depth",
        choices=("two-minute", "ten-minute", "deep-dive"),
        default="two-minute",
    )
    return parser


def main() -> None:
    args = _parser().parse_args()
    evidence = sample_evidence()
    if args.command == "smoke":
        payload: object = _smoke()
    elif args.command == "review":
        payload = review_evidence(evidence).model_dump(mode="json")
    else:
        payload = build_story(evidence, cast(Depth, args.depth)).model_dump(mode="json")
    print(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
