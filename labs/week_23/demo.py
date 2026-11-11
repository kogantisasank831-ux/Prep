"""Run six cases and the Week 23 system-design readiness rubric."""

from __future__ import annotations

import argparse
import json
from typing import cast

from labs.week_23.cases import CASES, get_case
from labs.week_23.models import (
    DIMENSIONS,
    CaseId,
    DesignProposal,
    Dimension,
    SectionAnswer,
)
from labs.week_23.reviewer import review_proposal


def sample_proposal(case_id: CaseId, *, complete: bool = True) -> DesignProposal:
    """Create a deterministic answer fixture for rubric practice."""

    included: tuple[Dimension, ...]
    if complete:
        included = DIMENSIONS
    else:
        included = tuple(
            dimension
            for dimension in DIMENSIONS
            if dimension not in {"evaluation", "security", "failure"}
        )
    sections = tuple(
        SectionAnswer(
            dimension=dimension,
            decision=f"State the bounded {dimension} decision for this case.",
            evidence=f"Name a measurable test or observation for {dimension}.",
            trade_off=f"Compare the chosen {dimension} option with one alternative.",
            failure_control=f"Detect and contain a plausible {dimension} failure.",
        )
        for dimension in included
    )
    return DesignProposal(
        case_id=case_id,
        sections=sections,
        assumptions=("Peak traffic and permission-change rates require measurement.",),
        rejected_alternatives=(
            "A single unbounded model call was rejected because it hides control points.",
        ),
    )


def _smoke() -> dict[str, object]:
    checks = 0
    assert len(CASES) == 6
    checks += 1
    for case_id in CASES:
        review = review_proposal(sample_proposal(case_id))
        assert review.gate == "ready_for_mock_interview"
        assert review.total_score == 48
        checks += 2
    incomplete = review_proposal(sample_proposal("enterprise-rag", complete=False))
    assert incomplete.gate == "revise"
    assert incomplete.critical_gaps == ("evaluation", "security", "failure")
    checks += 2
    assert review_proposal(sample_proposal("enterprise-rag")) == review_proposal(
        sample_proposal("enterprise-rag")
    )
    checks += 1
    return {"cases": len(CASES), "checks": checks, "status": "ok"}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("cases", "review", "smoke"))
    parser.add_argument("--case", choices=tuple(CASES), default="enterprise-rag")
    parser.add_argument("--incomplete", action="store_true")
    return parser


def main() -> None:
    args = _parser().parse_args()
    case_id = cast(CaseId, args.case)
    if args.command == "smoke":
        payload: object = _smoke()
    elif args.command == "cases":
        payload = [case.model_dump(mode="json") for case in CASES.values()]
    else:
        proposal = sample_proposal(case_id, complete=not args.incomplete)
        payload = {
            "case": get_case(case_id).model_dump(mode="json"),
            "review": review_proposal(proposal).model_dump(mode="json"),
        }
    print(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
