"""Deterministic local specialists with typed, minimal handoffs."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_EVEN, localcontext
from typing import Callable, TypeAlias

from labs.week_17.fixtures import DOCUMENT_RECORDS, RISK_RECORDS, SQL_RECORDS
from labs.week_17.models import (
    Assignment,
    CommercialAssignment,
    CommercialFinding,
    DocumentAssignment,
    DocumentFinding,
    Recommendation,
    RiskAssignment,
    RiskFinding,
    RiskLevel,
    SourceKind,
    SpecialistName,
    SpecialistResult,
    SqlAssignment,
    SqlFinding,
    SupplierStatus,
)


class SpecialistFailure(RuntimeError):
    """A controlled specialist or source-contract failure."""


SpecialistFunction: TypeAlias = Callable[[Assignment], SpecialistResult]


def _check_source(actual_kind: SourceKind, expected_kind: SourceKind) -> None:
    if actual_kind is not expected_kind:
        raise SpecialistFailure("source_kind_mismatch")


def analyze_document(assignment: Assignment) -> SpecialistResult:
    """Return only the applicable threshold and its governed source reference."""
    if not isinstance(assignment, DocumentAssignment):
        raise SpecialistFailure("document_assignment_invalid")
    _check_source(assignment.source.kind, SourceKind.DOCUMENT)
    record = DOCUMENT_RECORDS.get(assignment.source.source_id)
    if record is None:
        raise SpecialistFailure("document_not_found")
    if record.digest() != assignment.source.content_digest:
        raise SpecialistFailure("document_digest_mismatch")
    if record.purchase_order_id != assignment.purchase_order_id:
        raise SpecialistFailure("document_case_mismatch")
    return DocumentFinding(
        run_id=assignment.run_id,
        case_id=assignment.case_id,
        source=assignment.source,
        terms_found=record.terms_found,
        max_variance_percent=record.max_variance_percent,
    )


def analyze_sql(assignment: Assignment) -> SpecialistResult:
    """Return an exact price comparison from the synthetic SQL source."""
    if not isinstance(assignment, SqlAssignment):
        raise SpecialistFailure("sql_assignment_invalid")
    _check_source(assignment.source.kind, SourceKind.SQL)
    record = SQL_RECORDS.get(assignment.source.source_id)
    if record is None:
        raise SpecialistFailure("sql_row_not_found")
    if record.digest() != assignment.source.content_digest:
        raise SpecialistFailure("sql_digest_mismatch")
    if record.purchase_order_id != assignment.purchase_order_id:
        raise SpecialistFailure("sql_case_mismatch")
    if record.supplier_id != assignment.selected_supplier_id:
        raise SpecialistFailure("sql_supplier_mismatch")
    if record.reference_price <= 0:
        raise SpecialistFailure("reference_price_invalid")
    with localcontext() as context:
        context.prec = 28
        variance = (
            (record.current_price - record.reference_price)
            / record.reference_price
            * Decimal("100")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
    return SqlFinding(
        run_id=assignment.run_id,
        case_id=assignment.case_id,
        source=assignment.source,
        purchase_order_id=record.purchase_order_id,
        supplier_id=record.supplier_id,
        current_price=record.current_price,
        reference_price=record.reference_price,
        variance_percent=variance,
        currency=record.currency,
        unit=record.unit,
        as_of=record.as_of,
    )


def assess_supplier_risk(assignment: Assignment) -> SpecialistResult:
    """Return a narrow risk classification for the selected supplier."""
    if not isinstance(assignment, RiskAssignment):
        raise SpecialistFailure("risk_assignment_invalid")
    _check_source(assignment.source.kind, SourceKind.RISK_REGISTER)
    record = RISK_RECORDS.get(assignment.source.source_id)
    if record is None:
        raise SpecialistFailure("risk_record_not_found")
    if record.digest() != assignment.source.content_digest:
        raise SpecialistFailure("risk_digest_mismatch")
    if record.supplier_id != assignment.selected_supplier_id:
        raise SpecialistFailure("risk_supplier_mismatch")
    risk_level = (
        RiskLevel.LOW
        if record.supplier_status is SupplierStatus.ACTIVE
        and record.open_incidents == 0
        else RiskLevel.ELEVATED
    )
    return RiskFinding(
        run_id=assignment.run_id,
        case_id=assignment.case_id,
        source=assignment.source,
        supplier_id=record.supplier_id,
        supplier_status=record.supplier_status,
        open_incidents=record.open_incidents,
        risk_level=risk_level,
    )


def recommend_commercial_action(assignment: Assignment) -> SpecialistResult:
    """Synthesize validated findings without taking a procurement action."""
    if not isinstance(assignment, CommercialAssignment):
        raise SpecialistFailure("commercial_assignment_invalid")
    findings = (assignment.document, assignment.sql, assignment.risk)
    if any(finding.run_id != assignment.run_id for finding in findings):
        raise SpecialistFailure("commercial_run_mismatch")
    if any(finding.case_id != assignment.case_id for finding in findings):
        raise SpecialistFailure("commercial_case_mismatch")
    if assignment.sql.supplier_id != assignment.risk.supplier_id:
        raise SpecialistFailure("commercial_supplier_mismatch")

    document = assignment.document
    sql = assignment.sql
    risk = assignment.risk
    if not document.terms_found or document.max_variance_percent is None:
        recommendation = Recommendation.NEEDS_HUMAN
        reason = "The applicable contract threshold was not found."
    elif (
        risk.supplier_status is SupplierStatus.INACTIVE
        or risk.risk_level is RiskLevel.ELEVATED
    ):
        recommendation = Recommendation.REVIEW_REQUIRED
        reason = (
            f"Supplier risk is {risk.risk_level}; open incidents: "
            f"{risk.open_incidents}."
        )
    elif sql.variance_percent > document.max_variance_percent:
        recommendation = Recommendation.REVIEW_REQUIRED
        reason = (
            f"The {sql.variance_percent}% variance exceeds the "
            f"{document.max_variance_percent}% contract threshold."
        )
    else:
        recommendation = Recommendation.NO_REVIEW
        reason = (
            f"The {sql.variance_percent}% variance is within the "
            f"{document.max_variance_percent}% contract threshold."
        )

    evidence = tuple(
        f"{finding.source.kind}:{finding.source.source_id}:"
        f"{finding.source.content_digest[:12]}"
        for finding in findings
    )
    return CommercialFinding(
        run_id=assignment.run_id,
        case_id=assignment.case_id,
        recommendation=recommendation,
        summary=(
            f"{sql.purchase_order_id}: {reason} A human must review this report "
            "before any procurement action."
        ),
        evidence=evidence,
    )


DEFAULT_SPECIALISTS: dict[SpecialistName, SpecialistFunction] = {
    SpecialistName.DOCUMENT: analyze_document,
    SpecialistName.SQL: analyze_sql,
    SpecialistName.SUPPLIER_RISK: assess_supplier_risk,
    SpecialistName.COMMERCIAL: recommend_commercial_action,
}
