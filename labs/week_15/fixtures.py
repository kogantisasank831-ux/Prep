"""Synthetic document and SQL fixtures for the Week 15 graph."""

from __future__ import annotations

import sqlite3

from labs.week_15.models import CaseInput, ContractEvidence, SqlAnalysis


CASES: dict[str, CaseInput] = {
    "price-spike": {
        "case_id": "price-spike",
        "query": "Investigate the price increase on purchase order PO-1501.",
    },
    "stable-price": {
        "case_id": "stable-price",
        "query": "Review the price on purchase order PO-1502.",
    },
    "missing-terms": {
        "case_id": "missing-terms",
        "query": "Investigate the price change on purchase order PO-1503.",
    },
}

CASE_ORDERS: dict[str, str] = {
    "price-spike": "PO-1501",
    "stable-price": "PO-1502",
    "missing-terms": "PO-1503",
}

ORDER_ROWS: tuple[tuple[str, str, str, str, str, str, str, str, str], ...] = (
    (
        "PO-1501",
        "SUP-115",
        "active",
        "STEEL-A",
        "2.20",
        "2.00",
        "USD",
        "kg",
        "2026-10-01",
    ),
    (
        "PO-1502",
        "SUP-116",
        "active",
        "RESIN-B",
        "2.04",
        "2.00",
        "USD",
        "kg",
        "2026-10-01",
    ),
    (
        "PO-1503",
        "SUP-117",
        "active",
        "COPPER-C",
        "3.30",
        "3.00",
        "USD",
        "kg",
        "2026-10-01",
    ),
)

CONTRACTS: dict[str, ContractEvidence] = {
    "PO-1501": {
        "purchase_order_id": "PO-1501",
        "found": True,
        "max_variance_percent": "5.00",
        "excerpt": "Unit-price changes above 5.00% require procurement review.",
        "document_id": "contract-1501-v1",
    },
    "PO-1502": {
        "purchase_order_id": "PO-1502",
        "found": True,
        "max_variance_percent": "5.00",
        "excerpt": "Unit-price changes above 5.00% require procurement review.",
        "document_id": "contract-1502-v1",
    },
    "PO-1503": {
        "purchase_order_id": "PO-1503",
        "found": False,
        "max_variance_percent": None,
        "excerpt": "",
        "document_id": "contract-search-1503",
    },
}


def retrieve_contract(purchase_order_id: str) -> ContractEvidence:
    """Return a copy of a local document-search result."""
    contract = CONTRACTS.get(purchase_order_id)
    if contract is None:
        return {
            "purchase_order_id": purchase_order_id,
            "found": False,
            "max_variance_percent": None,
            "excerpt": "",
            "document_id": f"contract-search-{purchase_order_id}",
        }
    return ContractEvidence(**contract)


def analyze_order_sql(purchase_order_id: str) -> SqlAnalysis:
    """Run a parameterized query over a disposable in-memory SQL fixture."""
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute(
            """
            CREATE TABLE price_analysis (
                purchase_order_id TEXT PRIMARY KEY,
                supplier_id TEXT NOT NULL,
                supplier_status TEXT NOT NULL,
                commodity_id TEXT NOT NULL,
                current_price TEXT NOT NULL,
                reference_price TEXT NOT NULL,
                currency TEXT NOT NULL,
                unit TEXT NOT NULL,
                reference_as_of TEXT NOT NULL
            )
            """
        )
        connection.executemany(
            "INSERT INTO price_analysis VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ORDER_ROWS,
        )
        row = connection.execute(
            """
            SELECT purchase_order_id, supplier_id, supplier_status, commodity_id,
                   current_price, reference_price, currency, unit, reference_as_of
              FROM price_analysis
             WHERE purchase_order_id = ?
            """,
            (purchase_order_id,),
        ).fetchone()
    finally:
        connection.close()
    if row is None:
        raise ValueError("purchase_order_not_found")
    return SqlAnalysis(
        purchase_order_id=str(row[0]),
        supplier_id=str(row[1]),
        supplier_status=str(row[2]),
        commodity_id=str(row[3]),
        current_price=str(row[4]),
        reference_price=str(row[5]),
        currency=str(row[6]),
        unit=str(row[7]),
        reference_as_of=str(row[8]),
    )
