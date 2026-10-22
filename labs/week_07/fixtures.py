"""Reuse Week 6 parsed sources without changing their versions or text."""

from __future__ import annotations

import json

from labs.week_06.chunking import (
    BlockKind,
    ChunkCollection,
    ParseStatus,
    StructurePolicy,
    UntrustedDocument,
    source_fingerprint,
)
from labs.week_06.fixtures import (
    FIXED_TIME,
    PARSER,
    accepted_sources,
    block,
    ocr_review_document,
)
from labs.week_07.retrieval import SourceChunk, StaticObjectAccessPolicy, digest_text

PRINCIPAL = "analyst"


def frozen_chunks() -> tuple[SourceChunk, ...]:
    """Eleven chunks: unchanged Week 6 sources plus two separately identified notes."""
    additions = (
        UntrustedDocument(
            "northwind-procurement",
            "P-107",
            "1",
            "Atlas Metals catalogue note",
            (
                block(
                    BlockKind.PARAGRAPH,
                    1,
                    1,
                    "Atlas Metals catalogue note. Product code CW-1000. Commercial name Copper wire, 1,000 kg coil. Quoted unit price USD 12.00.",
                ),
            ),
        ),
        UntrustedDocument(
            "northwind-procurement",
            "P-108",
            "1",
            "Beacon Plastics code note",
            (
                block(
                    BlockKind.PARAGRAPH,
                    1,
                    1,
                    "Beacon Plastics catalogue. Product code PP-20 identifies polymer pellets.",
                ),
            ),
        ),
    )
    sources = list(accepted_sources())
    for document in additions:
        parsed = PARSER.parse(document)
        if parsed.status != ParseStatus.ACCEPTED or parsed.source is None:
            raise ValueError("new controlled fixture was not accepted")
        sources.append(parsed.source)
    chunks: list[SourceChunk] = []
    for source in sources:
        collection = ChunkCollection.build(
            source, StructurePolicy(), created_at=FIXED_TIME
        )
        # Curated synthetic labels, not automatic supplier extraction from prose.
        supplier = {
            "P-101": "Atlas Metals",
            "P-102": "Beacon Plastics",
            "P-103": "Atlas Metals",
            "P-104": "Cedar Fasteners",
            "P-105": "Atlas Metals",
            "P-107": "Atlas Metals",
            "P-108": "Beacon Plastics",
        }[source.identity.document_id]
        document_type = {
            "P-101": "confirmation",
            "P-102": "confirmation",
            "P-103": "delivery_update",
            "P-104": "payment_note",
            "P-105": "framework_agreement",
            "P-107": "catalogue",
            "P-108": "catalogue",
        }[source.identity.document_id]
        for item in collection.chunks:
            body_location = item.locations[-1]
            metadata = (
                ("supplier", supplier),
                ("document_type", document_type),
                (
                    "evidence_key",
                    f"{source.identity.document_id}/{source.identity.version}/{body_location.block_index}",
                ),
                (
                    "source_locations",
                    json.dumps([location.label() for location in item.locations]),
                ),
                ("parser", f"{source.parser_id}/{source.parser_version}"),
                ("parsed_representation", source_fingerprint(source)),
                ("chunk_policy", collection.manifest.policy_fingerprint),
                ("metadata_policy", "curated-synthetic-fixture-labels/1.0.0"),
            )
            chunks.append(
                SourceChunk(
                    item.chunk_id,
                    source.identity.tenant_id,
                    source.identity.document_id,
                    source.identity.version,
                    source.identity.content_digest,
                    item.text,
                    metadata,
                )
            )
    return tuple(chunks)


def access_policy(chunks: tuple[SourceChunk, ...]) -> StaticObjectAccessPolicy:
    return StaticObjectAccessPolicy(
        frozenset(
            (PRINCIPAL, item.tenant_id, item.document_id, item.document_version)
            for item in chunks
        )
    )


def denied_code_match() -> SourceChunk:
    return SourceChunk(
        "private:1:0",
        "other-tenant",
        "PRIVATE",
        "1",
        digest_text("synthetic private source"),
        "CW-1000 SECRET-900 Atlas Metals quote. Net 30 after inspection approval.",
        (("supplier", "Atlas Metals"), ("document_type", "catalogue")),
    )


def quarantine_summary() -> dict[str, object]:
    parsed = PARSER.parse(ocr_review_document())
    return {
        "document_id": "P-106",
        "version": "1",
        "status": parsed.status,
        "reasons": parsed.reasons,
    }
