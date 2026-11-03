"""Fictional, dated memory fixtures for the Week 16 lab."""

from __future__ import annotations

from datetime import date, datetime, timezone
from hashlib import sha256

from labs.week_16.models import (
    AccessScope,
    ApprovalStatus,
    Calculation,
    CaseMemoryInput,
    EvidenceReference,
)


FIXED_NOW = datetime(2026, 11, 3, 5, 0, tzinfo=timezone.utc)
EXPIRES_AT = datetime(2026, 12, 3, 5, 0, tzinfo=timezone.utc)
TENANT_ID = "tenant-north"
CASE_ID = "price-spike"


def _digest(label: str) -> str:
    return sha256(label.encode("utf-8")).hexdigest()


def scope(*, write: bool = False, tenant_id: str = TENANT_ID) -> AccessScope:
    """Return a trusted synthetic host scope for the one demonstration case."""
    return AccessScope(
        tenant_id=tenant_id,
        allowed_case_ids=frozenset({CASE_ID}),
        can_write=write,
    )


def case_memory(
    approval_status: ApprovalStatus = "awaiting_approval",
) -> CaseMemoryInput:
    """Return the selected facts from the fictional Week 15 price-spike run."""
    return CaseMemoryInput(
        case_id=CASE_ID,
        objective="Investigate the dated price variance for purchase order PO-1501.",
        selected_supplier_id="SUP-115",
        evidence=(
            EvidenceReference(
                source_type="document",
                source_id="contract-1501-v1",
                content_digest=_digest("fictional-contract-1501-v1"),
                observed_at=FIXED_NOW,
            ),
            EvidenceReference(
                source_type="sql",
                source_id="price-analysis-PO-1501",
                content_digest=_digest("fictional-sql-price-analysis-PO-1501"),
                observed_at=FIXED_NOW,
            ),
        ),
        calculation=Calculation(
            metric="price_variance_percent",
            value="10.00",
            currency="USD",
            unit="kg",
            reference_as_of=date(2026, 10, 1),
            rounding="ROUND_HALF_EVEN",
        ),
        approval_status=approval_status,
        source_run_id="week15-price-spike-01",
        source_report_digest=_digest("fictional-week15-price-spike-report"),
        observed_at=FIXED_NOW,
        expires_at=EXPIRES_AT,
    )
