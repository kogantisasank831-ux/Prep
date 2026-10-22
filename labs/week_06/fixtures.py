"""Synthetic parsed-layout fixtures, including one quarantined OCR example."""

from __future__ import annotations
from datetime import UTC, datetime
from labs.week_06.chunking import (
    BlockKind,
    FixtureParser,
    ParseStatus,
    ParsedBlock,
    ParsedSource,
    SourceLocation,
    UntrustedDocument,
)

FIXED_TIME = datetime(2026, 8, 16, tzinfo=UTC)
PARSER = FixtureParser()


def block(
    kind: BlockKind,
    page: int,
    index: int,
    text: str,
    *,
    table: str | None = None,
    row: int | None = None,
) -> ParsedBlock:
    return ParsedBlock(kind, SourceLocation(page, index, table, row), text)


def fixture_documents() -> tuple[UntrustedDocument, ...]:
    return (
        UntrustedDocument(
            "northwind-procurement",
            "P-101",
            "1",
            "Atlas Metals purchase confirmation",
            (
                block(
                    BlockKind.PARAGRAPH,
                    1,
                    1,
                    "Copper wire will ship after incoming-material inspection. Invoice terms: Net 30 after inspection approval.",
                ),
            ),
        ),
        UntrustedDocument(
            "northwind-procurement",
            "P-102",
            "1",
            "Beacon Plastics purchase confirmation",
            (
                block(
                    BlockKind.PARAGRAPH,
                    1,
                    1,
                    "Polymer pellets will ship on 2026-09-03. Invoice terms: Net 15 from receipt.",
                ),
            ),
        ),
        UntrustedDocument(
            "northwind-procurement",
            "P-103",
            "1",
            "Atlas Metals delivery update",
            (
                block(
                    BlockKind.PARAGRAPH,
                    1,
                    1,
                    "The copper-wire shipment is delayed by two days while quality checks finish.",
                ),
            ),
        ),
        UntrustedDocument(
            "northwind-procurement",
            "P-104",
            "1",
            "Cedar Fasteners payment note",
            (
                block(
                    BlockKind.PARAGRAPH,
                    1,
                    1,
                    "Payment is due after the receiving team signs off on the delivered bolts.",
                ),
            ),
        ),
        UntrustedDocument(
            "northwind-procurement",
            "P-105",
            "1",
            "Atlas Metals framework agreement",
            (
                block(BlockKind.HEADING, 1, 1, "Section 1 — Scope"),
                block(
                    BlockKind.PARAGRAPH,
                    1,
                    2,
                    "Atlas Metals supplies copper wire to the Northwind plant.",
                ),
                block(BlockKind.HEADING, 1, 3, "Section 2 — Delivery and acceptance"),
                block(
                    BlockKind.PARAGRAPH,
                    1,
                    4,
                    "The receiving team records incoming-material inspection before acceptance.",
                ),
                block(BlockKind.HEADING, 1, 5, "Schedule A — line items"),
                block(
                    BlockKind.TABLE_ROW,
                    1,
                    6,
                    "Schedule A, row 1: product=copper wire; quantity=1,000 kg; unit price=USD 12.00.",
                    table="schedule-a",
                    row=1,
                ),
                block(BlockKind.HEADING, 1, 7, "Section 3 — Invoicing"),
                block(
                    BlockKind.PARAGRAPH,
                    1,
                    8,
                    "Invoice terms are Net 30 after inspection approval.",
                ),
                block(
                    BlockKind.PARAGRAPH,
                    1,
                    9,
                    "The payment condition in this section controls Schedule A.",
                ),
            ),
        ),
    )


def accepted_sources() -> tuple[ParsedSource, ...]:
    results = tuple(PARSER.parse(document) for document in fixture_documents())
    assert all(
        result.status == ParseStatus.ACCEPTED and result.source is not None
        for result in results
    )
    return tuple(result.source for result in results if result.source is not None)


def ocr_review_document() -> UntrustedDocument:
    """P-106 simulates uncertain parsed OCR; it is not an OCR engine output."""
    return UntrustedDocument(
        "northwind-procurement",
        "P-106",
        "1",
        "Scanned Atlas Metals invoice",
        (
            block(
                BlockKind.TABLE_ROW,
                1,
                1,
                "Invoice row 1: product=copper wire; quantity=100 kg; unit price=USD 12.O0.",
                table="invoice-lines",
                row=1,
            ),
        ),
    )
