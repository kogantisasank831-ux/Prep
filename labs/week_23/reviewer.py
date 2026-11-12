"""Transparent structural rubric for GenAI system-design answers."""

from __future__ import annotations

from labs.week_23.models import (
    CRITICAL_DIMENSIONS,
    DIMENSIONS,
    DesignProposal,
    DesignReview,
    Dimension,
    DimensionReview,
    Gate,
    MissingField,
    SectionAnswer,
)


_FIELDS: tuple[MissingField, ...] = (
    "decision",
    "evidence",
    "trade_off",
    "failure_control",
)


def _is_substantive(value: str) -> bool:
    return len(value.strip()) >= 12


def _review_section(
    dimension: Dimension, section: SectionAnswer | None
) -> DimensionReview:
    if section is None:
        return DimensionReview(
            dimension=dimension,
            score=0,
            missing_fields=_FIELDS,
        )
    missing = tuple(
        field for field in _FIELDS if not _is_substantive(getattr(section, field))
    )
    return DimensionReview(
        dimension=dimension,
        score=4 - len(missing),
        missing_fields=missing,
    )


def review_proposal(proposal: DesignProposal) -> DesignReview:
    """Review completeness; do not claim that the architecture is correct."""

    supplied = {section.dimension: section for section in proposal.sections}
    reviews = tuple(
        _review_section(dimension, supplied.get(dimension)) for dimension in DIMENSIONS
    )
    missing_dimensions = tuple(
        review.dimension for review in reviews if review.score == 0
    )
    critical_gaps = tuple(
        review.dimension
        for review in reviews
        if review.dimension in CRITICAL_DIMENSIONS and review.score < 3
    )
    total_score = sum(review.score for review in reviews)
    warnings: list[str] = [
        "structural_score_only_semantic_correctness_requires_human_review"
    ]
    if not proposal.assumptions:
        warnings.append("assumptions_not_declared")
    if not proposal.rejected_alternatives:
        warnings.append("alternatives_not_compared")
    gate: Gate = (
        "ready_for_mock_interview"
        if total_score >= 36
        and not critical_gaps
        and proposal.assumptions
        and proposal.rejected_alternatives
        else "revise"
    )
    return DesignReview(
        case_id=proposal.case_id,
        gate=gate,
        total_score=total_score,
        reviews=reviews,
        missing_dimensions=missing_dimensions,
        critical_gaps=critical_gaps,
        warnings=tuple(warnings),
    )
