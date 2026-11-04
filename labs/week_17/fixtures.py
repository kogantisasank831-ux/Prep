"""Synthetic governed sources for the Week 17 lab."""

from __future__ import annotations

from decimal import Decimal
from hashlib import sha256
import json

from labs.week_17.models import (
    ProcurementCase,
    SourceKind,
    SourceReference,
    StrictModel,
    SupplierStatus,
)


def _digest(payload: dict[str, object]) -> str:
    canonical = json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256(canonical.encode("utf-8")).hexdigest()


class DocumentRecord(StrictModel):
    source_id: str
    purchase_order_id: str
    terms_found: bool
    max_variance_percent: Decimal | None

    def digest(self) -> str:
        return _digest(
            {
                "source_id": self.source_id,
                "purchase_order_id": self.purchase_order_id,
                "terms_found": self.terms_found,
                "max_variance_percent": (
                    str(self.max_variance_percent)
                    if self.max_variance_percent is not None
                    else None
                ),
            }
        )


class SqlRecord(StrictModel):
    source_id: str
    purchase_order_id: str
    supplier_id: str
    current_price: Decimal
    reference_price: Decimal
    currency: str
    unit: str
    as_of: str

    def digest(self) -> str:
        return _digest(
            {
                "source_id": self.source_id,
                "purchase_order_id": self.purchase_order_id,
                "supplier_id": self.supplier_id,
                "current_price": str(self.current_price),
                "reference_price": str(self.reference_price),
                "currency": self.currency,
                "unit": self.unit,
                "as_of": self.as_of,
            }
        )


class RiskRecord(StrictModel):
    source_id: str
    supplier_id: str
    supplier_status: SupplierStatus
    open_incidents: int

    def digest(self) -> str:
        return _digest(
            {
                "source_id": self.source_id,
                "supplier_id": self.supplier_id,
                "supplier_status": self.supplier_status,
                "open_incidents": self.open_incidents,
            }
        )


DOCUMENT_RECORDS: dict[str, DocumentRecord] = {
    "contract-1701-v1": DocumentRecord(
        source_id="contract-1701-v1",
        purchase_order_id="PO-1701",
        terms_found=True,
        max_variance_percent=Decimal("5.00"),
    ),
    "contract-1702-v1": DocumentRecord(
        source_id="contract-1702-v1",
        purchase_order_id="PO-1702",
        terms_found=True,
        max_variance_percent=Decimal("5.00"),
    ),
    "contract-1703-missing": DocumentRecord(
        source_id="contract-1703-missing",
        purchase_order_id="PO-1703",
        terms_found=False,
        max_variance_percent=None,
    ),
    "contract-1704-v1": DocumentRecord(
        source_id="contract-1704-v1",
        purchase_order_id="PO-1704",
        terms_found=True,
        max_variance_percent=Decimal("5.00"),
    ),
}

SQL_RECORDS: dict[str, SqlRecord] = {
    "price-analysis-1701": SqlRecord(
        source_id="price-analysis-1701",
        purchase_order_id="PO-1701",
        supplier_id="SUP-171",
        current_price=Decimal("2.20"),
        reference_price=Decimal("2.00"),
        currency="USD",
        unit="kg",
        as_of="2026-11-01",
    ),
    "price-analysis-1702": SqlRecord(
        source_id="price-analysis-1702",
        purchase_order_id="PO-1702",
        supplier_id="SUP-172",
        current_price=Decimal("2.04"),
        reference_price=Decimal("2.00"),
        currency="USD",
        unit="kg",
        as_of="2026-11-01",
    ),
    "price-analysis-1703": SqlRecord(
        source_id="price-analysis-1703",
        purchase_order_id="PO-1703",
        supplier_id="SUP-173",
        current_price=Decimal("3.30"),
        reference_price=Decimal("3.00"),
        currency="USD",
        unit="kg",
        as_of="2026-11-01",
    ),
    "price-analysis-1704": SqlRecord(
        source_id="price-analysis-1704",
        purchase_order_id="PO-1704",
        supplier_id="SUP-174",
        current_price=Decimal("5.05"),
        reference_price=Decimal("5.00"),
        currency="USD",
        unit="kg",
        as_of="2026-11-01",
    ),
}

RISK_RECORDS: dict[str, RiskRecord] = {
    "risk-register-171": RiskRecord(
        source_id="risk-register-171",
        supplier_id="SUP-171",
        supplier_status=SupplierStatus.ACTIVE,
        open_incidents=0,
    ),
    "risk-register-172": RiskRecord(
        source_id="risk-register-172",
        supplier_id="SUP-172",
        supplier_status=SupplierStatus.ACTIVE,
        open_incidents=0,
    ),
    "risk-register-173": RiskRecord(
        source_id="risk-register-173",
        supplier_id="SUP-173",
        supplier_status=SupplierStatus.ACTIVE,
        open_incidents=0,
    ),
    "risk-register-174": RiskRecord(
        source_id="risk-register-174",
        supplier_id="SUP-174",
        supplier_status=SupplierStatus.ACTIVE,
        open_incidents=2,
    ),
}


def _source(kind: SourceKind, source_id: str, digest: str) -> SourceReference:
    return SourceReference(kind=kind, source_id=source_id, content_digest=digest)


def _case(
    case_id: str,
    purchase_order_id: str,
    supplier_id: str,
    document_id: str,
    sql_id: str,
    risk_id: str,
) -> ProcurementCase:
    document = DOCUMENT_RECORDS[document_id]
    sql = SQL_RECORDS[sql_id]
    risk = RISK_RECORDS[risk_id]
    return ProcurementCase(
        case_id=case_id,
        purchase_order_id=purchase_order_id,
        selected_supplier_id=supplier_id,
        document_source=_source(SourceKind.DOCUMENT, document_id, document.digest()),
        sql_source=_source(SourceKind.SQL, sql_id, sql.digest()),
        risk_source=_source(SourceKind.RISK_REGISTER, risk_id, risk.digest()),
    )


CASES: dict[str, ProcurementCase] = {
    "price-spike": _case(
        "price-spike",
        "PO-1701",
        "SUP-171",
        "contract-1701-v1",
        "price-analysis-1701",
        "risk-register-171",
    ),
    "stable-price": _case(
        "stable-price",
        "PO-1702",
        "SUP-172",
        "contract-1702-v1",
        "price-analysis-1702",
        "risk-register-172",
    ),
    "missing-terms": _case(
        "missing-terms",
        "PO-1703",
        "SUP-173",
        "contract-1703-missing",
        "price-analysis-1703",
        "risk-register-173",
    ),
    "supplier-risk": _case(
        "supplier-risk",
        "PO-1704",
        "SUP-174",
        "contract-1704-v1",
        "price-analysis-1704",
        "risk-register-174",
    ),
}
