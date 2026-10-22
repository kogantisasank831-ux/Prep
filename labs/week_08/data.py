"""Ingest controlled JSONL layout records through the existing parser contract."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from labs.week_06.chunking import (
    BlockKind,
    ChunkCollection,
    ParsedBlock,
    ParseStatus,
    SourceLocation,
    StructurePolicy,
    UntrustedDocument,
    source_fingerprint,
)
from labs.week_06.fixtures import FIXED_TIME, PARSER
from labs.week_07.retrieval import (
    SourceChunk,
    StaticObjectAccessPolicy,
    digest_text,
    validate_chunks,
)

MAX_INPUT_BYTES = 128 * 1024


class IngestionError(ValueError):
    """A JSONL batch violates the controlled input contract."""


@dataclass(frozen=True)
class IngestionIssue:
    source_key: str
    status: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class IngestedCorpus:
    chunks: tuple[SourceChunk, ...]
    accepted_documents: int
    issues: tuple[IngestionIssue, ...]
    input_digest: str


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise IngestionError("duplicate JSON object key")
        result[key] = value
    return result


def _text(value: object, *, limit: int = 200) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise IngestionError("expected bounded nonblank text")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise IngestionError("text must be valid UTF-8") from exc
    return value


def _positive_int(value: object) -> int:
    if type(value) is not int or value < 1:
        raise IngestionError("location must be a positive integer")
    return value


def _block(value: object) -> ParsedBlock:
    fields = {"kind", "page", "block_index", "table_id", "row_index", "text"}
    if not isinstance(value, dict) or set(value) != fields:
        raise IngestionError("unexpected block fields")
    try:
        kind = BlockKind(_text(value["kind"]))
    except ValueError as exc:
        raise IngestionError("unsupported block kind") from exc
    table = None if value["table_id"] is None else _text(value["table_id"])
    row = None if value["row_index"] is None else _positive_int(value["row_index"])
    return ParsedBlock(
        kind,
        SourceLocation(
            _positive_int(value["page"]),
            _positive_int(value["block_index"]),
            table,
            row,
        ),
        _text(value["text"], limit=1000),
    )


def load_corpus(path: Path) -> IngestedCorpus:
    """Fail conflicting batches; retain review/reject outcomes without indexing them.

    Supplier/type labels are input assertions, never access grants. This accepts
    synthetic parsed-layout JSONL, not arbitrary PDFs or untrusted parser code.
    """
    with path.open("rb") as handle:
        raw = handle.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise IngestionError("input exceeds 128 KiB")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise IngestionError("input must be UTF-8") from exc
    lines = [line for line in text.splitlines() if line.strip()]
    if not 1 <= len(lines) <= 32:
        raise IngestionError("input requires 1 to 32 records")
    seen: dict[tuple[str, str, str], str] = {}
    chunks: list[SourceChunk] = []
    issues: list[IngestionIssue] = []
    accepted = 0
    for line in lines:
        try:
            record = json.loads(line, object_pairs_hook=_unique_object)
        except json.JSONDecodeError as exc:
            raise IngestionError("malformed JSON record") from exc
        if not isinstance(record, dict) or set(record) != {
            "tenant_id",
            "document_id",
            "version",
            "title",
            "supplier",
            "document_type",
            "blocks",
        }:
            raise IngestionError("unexpected document fields")
        blocks = record["blocks"]
        if not isinstance(blocks, list) or not 1 <= len(blocks) <= 32:
            raise IngestionError("expected 1 to 32 layout blocks")
        document = UntrustedDocument(
            _text(record["tenant_id"]),
            _text(record["document_id"]),
            _text(record["version"]),
            _text(record["title"]),
            tuple(_block(item) for item in blocks),
        )
        supplier = _text(record["supplier"])
        document_type = _text(record["document_type"])
        key = (document.tenant_id, document.document_id, document.version)
        record_digest = digest_text(
            json.dumps(record, sort_keys=True, ensure_ascii=False)
        )
        if key in seen:
            if seen[key] != record_digest:
                raise IngestionError("conflicting records for one source version")
            continue
        seen[key] = record_digest
        parsed = PARSER.parse(document)
        if parsed.status != ParseStatus.ACCEPTED or parsed.source is None:
            issues.append(
                IngestionIssue("/".join(key), parsed.status.value, parsed.reasons)
            )
            continue
        source = parsed.source
        collection = ChunkCollection.build(
            source, StructurePolicy(), created_at=FIXED_TIME
        )
        accepted += 1
        for chunk in collection.chunks:
            metadata = (
                ("supplier", supplier),
                ("document_type", document_type),
                (
                    "evidence_key",
                    f"{source.identity.document_id}/{source.identity.version}/{chunk.locations[-1].block_index}",
                ),
                (
                    "source_locations",
                    json.dumps([location.label() for location in chunk.locations]),
                ),
                ("parser", f"{source.parser_id}/{source.parser_version}"),
                ("parsed_representation", source_fingerprint(source)),
                ("chunk_policy", collection.manifest.policy_fingerprint),
                ("metadata_policy", "input-asserted-fixture-labels/1.0.0"),
            )
            chunks.append(
                SourceChunk(
                    chunk.chunk_id,
                    source.identity.tenant_id,
                    source.identity.document_id,
                    source.identity.version,
                    source.identity.content_digest,
                    chunk.text,
                    metadata,
                )
            )
    validate_chunks(chunks)
    return IngestedCorpus(tuple(chunks), accepted, tuple(issues), digest_text(text))


def demo_access() -> StaticObjectAccessPolicy:
    """Independent, explicit source-version grants for the synthetic analyst."""
    return StaticObjectAccessPolicy(
        frozenset(
            ("analyst", "northwind-procurement", document, "1")
            for document in (
                "P-101",
                "P-102",
                "P-103",
                "P-104",
                "P-105",
                "P-107",
                "P-108",
            )
        )
    )


def evidence_keys(chunks: tuple[SourceChunk, ...]) -> dict[str, SourceChunk]:
    """Practice keys assume a single eligible tenant; reject ambiguous labels."""
    result = {dict(chunk.metadata)["evidence_key"]: chunk for chunk in chunks}
    if len(result) != len(chunks):
        raise IngestionError("practice evidence keys are ambiguous")
    return result
