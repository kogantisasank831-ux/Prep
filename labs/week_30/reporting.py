"""Validate completeness and visible caveats in the final experiment report."""

from __future__ import annotations

from collections.abc import Mapping
import json

from pydantic import ValidationError

from labs.week_30.models import ExperimentReport, ReportReview


REQUIRED_SECTIONS = (
    "objective",
    "dataset",
    "training_configuration",
    "compute_used",
    "loss_curve",
    "evaluation",
    "failures",
    "cost_usd",
    "rag_comparison",
    "lessons_learned",
    "package",
    "serving",
)


def review_report(payload: object) -> ReportReview:
    """Return a bounded review rather than silently accepting incomplete prose."""

    if not isinstance(payload, Mapping):
        return ReportReview(
            valid=False,
            missing_sections=REQUIRED_SECTIONS,
            warnings=("Report payload must be a mapping.",),
        )
    keys = {key for key in payload if isinstance(key, str)}
    missing = tuple(section for section in REQUIRED_SECTIONS if section not in keys)
    try:
        report = ExperimentReport.model_validate_json(json.dumps(payload))
    except (TypeError, ValidationError):
        return ReportReview(
            valid=False,
            missing_sections=missing,
            warnings=("One or more report sections fail the strict schema.",),
        )
    warnings: list[str] = []
    if report.loss_curve[-1] >= report.loss_curve[0]:
        warnings.append(
            "Final loss is not below initial loss; explain the failed or unstable run."
        )
    if not report.failures:
        warnings.append(
            "No failures are recorded; confirm this is evidence rather than omission."
        )
    if report.cost_usd == 0.0:
        warnings.append(
            "Zero external spend still needs compute ownership and opportunity-cost context."
        )
    if not report.serving.feasible:
        warnings.append(
            "The requested serving profile is infeasible under its declared memory assumptions."
        )
    return ReportReview(valid=True, missing_sections=(), warnings=tuple(warnings))
