---
layout: week
week: 6
phase: 2
status: approved
version: 1.1.0
last_reviewed: 2026-10-22
estimated_hours: 8
permalink: /weeks/week-06/
title: "Document parsing and chunking: preserve evidence before retrieval"
description: Build a typed, local-only boundary that turns sensitive procurement documents into versioned, traceable retrieval units without silently losing structural evidence.
summary: Continue P-101 through P-105 from parser status and immutable source identity through deterministic chunk policies, parent-child lineage, manifest compatibility, and fair support-quality evaluation.
kicker_primary: Document parsing and chunking
kicker_secondary: Evidence-preserving retrieval units
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-06/beginner/
---

Test your understanding with the [Week 6 assessment]({{ '/assessments/week-06/' | relative_url }}): a random ten-question paper from 100 questions, including Python exercises on parsing, chunk boundaries, source spans, parent expansion and support completeness.

## Your route through Week 6

By the end, you should be able to take a parsed document, explain why each chunk boundary exists, trace a result to its source, and compare policies without changing the evidence underneath them. You will run six policies on the same five documents, keep an ambiguous sixth document out of the index, and explain why finding the right document can still leave an answer unsupported.

Bring the Week 5 ideas of embeddings, cosine ranking, source identity, and Recall@k. The main code uses dataclasses, protocols, enums, and immutable tuples. If those still need practice, start with the [beginner lesson]({{ '/weeks/week-06/beginner/' | relative_url }}) and return here for the boundary contracts.

| Time | Work | Evidence you should have |
| --- | --- | --- |
| Hour 1 | Read P-105; mark the three pieces needed for its payment question | A row, a clause, and their cross-reference |
| Hours 2–3 | Work through parsing, metadata, fixed, overlap, and sentence policies | Chunk text beside source locations |
| Hour 4 | Compare structure, semantic boundaries, and parent-child context | A reason each policy can fail |
| Hours 5–6 | Run the comparison lab and inspect Q04 | One shared corpus fingerprint and six result rows |
| Hour 7 | Change one parameter and inspect the resulting evidence | A measured cost/quality trade-off |
| Hour 8 | Complete the exercises and defend your choice aloud | A short decision note with limitations |

Keep P-105 open as you read. A useful habit is to ask, after every split: “Could I still establish which line this condition applies to?”

## P-105 makes the retrieval unit a design decision

Week 5 accepts an already-bounded document and ranks it as one retrieval record. P-105 is different. It is a synthetic Atlas Metals framework agreement with a table and a cross-section condition:

```text
P-105 | Atlas Metals framework agreement | version 1

Section 1 — Scope
Atlas Metals supplies copper wire to the Northwind plant.

Section 2 — Delivery and acceptance
The receiving team records incoming-material inspection before acceptance.

Schedule A — line items
| line | product      | quantity | unit price |
| 1    | copper wire  | 1,000 kg | USD 12.00  |

Section 3 — Invoicing
Invoice terms are Net 30 after inspection approval.
The payment condition in this section controls Schedule A.
```

The analyst’s question is deliberately narrow:

> What payment condition applies to the 1,000 kg copper-wire line?

The table alone provides the product and quantity. The invoicing paragraph provides the payment condition. The cross-reference supplies their relation. A fixed boundary can split `Net 30` from `after inspection approval`; a table-only result can hide the condition; a broad whole-document result can bury both facts among irrelevant sections.

The central design question is therefore:

> How can a system parse and chunk sensitive documents into traceable retrieval units without losing the evidence a reviewer needs?

Follow the evidence through a series of explicit contracts:

```text
untrusted file bytes
        -> parser result with status and locations
        -> immutable parsed source/version/digest
        -> declared chunk policy and parameters
        -> immutable chunks with lineage and stable IDs
        -> authorised candidate units for retrieval
        -> source text plus provenance for human/deterministic review
```

No stage answers the procurement question, approves payment, updates a record, or calls a tool. Parsing and chunking make evidence selectable. They do not make the evidence true, current, authorised, or complete.

## 1. Parsing is a trust boundary, not an implementation detail

### What do we know after a PDF returns text?

Only that a parser produced text. A PDF can contain positioned glyphs rather than logical paragraphs; a scanned page can contain only pixels; an OCR engine can confuse `0` with `O`, a decimal point with a speck, or a table header with a footer. Multi-column layout can yield wrong reading order. A table can be emitted as a sequence of cells without row/column association.

For P-105, this is not cosmetic. `USD 12.00` is meaningful only with its `unit price` header, `copper wire` row, and document/version context. A parser that produces this flat string has lost constraints:

```text
1 copper wire 1,000 kg USD 12.00 line product quantity unit price
```

The parser boundary should return typed blocks, source locations, parser identity, a status, and explicit reasons. A parser may return `accepted`, `needs_review`, or `rejected`; it must not silently drop a malformed table or truncate an oversized page and call the remaining text complete.

```python
"""Versioned parsing/chunk policies for controlled Week 6 fixtures."""

from __future__ import annotations


from collections.abc import Callable, Iterable, Sequence
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
import json
from math import isfinite
import re
from statistics import mean
from typing import Protocol, Self


MAX_DOCUMENT_CHARS = 4_000
MAX_BLOCK_CHARS = 1_000
CHUNK_MANIFEST_SCHEMA = "procurement-chunks/1.1.0"


class ChunkingError(Exception):
    """Base class for explicit parser and chunking boundary failures."""


class ParseRejectedError(ChunkingError):
    """The parser cannot create an accepted source record."""


class ChunkPolicyError(ChunkingError):
    """A chunk policy violates its declared input or size contract."""


class ManifestCompatibilityError(ChunkingError):
    """A chunk collection does not match a requested build contract."""


class BlockKind(StrEnum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    TABLE_ROW = "table_row"


class ParseStatus(StrEnum):
    ACCEPTED = "accepted"
    NEEDS_REVIEW = "needs_review"
    REJECTED = "rejected"


@dataclass(frozen=True)
class SourceLocation:
    page: int
    block_index: int
    table_id: str | None = None
    row_index: int | None = None
    start_char: int | None = None
    end_char: int | None = None

    def label(self) -> str:
        table = f":{self.table_id}" if self.table_id else ""
        row = f":row-{self.row_index}" if self.row_index is not None else ""
        span = (
            ""
            if self.start_char is None
            else f"@chars-{self.start_char}-{self.end_char}"
        )
        return f"p{self.page}:block-{self.block_index}{table}{row}{span}"


@dataclass(frozen=True)
class ParsedBlock:
    kind: BlockKind
    location: SourceLocation
    text: str


@dataclass(frozen=True)
class UntrustedDocument:
    tenant_id: str
    document_id: str
    version: str
    title: str
    raw_blocks: tuple[ParsedBlock, ...]


@dataclass(frozen=True)
class SourceIdentity:
    tenant_id: str
    document_id: str
    version: str
    content_digest: str


@dataclass(frozen=True)
class ParsedSource:
    identity: SourceIdentity
    title: str
    parser_id: str
    parser_version: str
    metadata: tuple[tuple[str, str], ...]
    blocks: tuple[ParsedBlock, ...]
    parse_status: ParseStatus = ParseStatus.ACCEPTED


@dataclass(frozen=True)
class ParseResult:
    status: ParseStatus
    source: ParsedSource | None
    reasons: tuple[str, ...]


def digest_text(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def canonical_block_text(blocks: Sequence[ParsedBlock]) -> str:
    return "\n".join(block.text.strip() for block in blocks if block.text.strip())


class ParserBoundary(Protocol):
    def parse(self, document: UntrustedDocument) -> ParseResult: ...


@dataclass(frozen=True)
class FixtureParser:
    """Validate fixture blocks; this does not parse PDF bytes or OCR images."""

    parser_id: str = "fixture-parser"
    parser_version: str = "1.1.0"

    def parse(self, document: UntrustedDocument) -> ParseResult:
        identifiers = (document.tenant_id, document.document_id, document.version)
        if any(
            not isinstance(value, str)
            or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", value) is None
            for value in identifiers
        ):
            return ParseResult(ParseStatus.REJECTED, None, ("invalid source identity",))
        if (
            not isinstance(document.title, str)
            or not document.title.strip()
            or len(document.title) > 200
        ):
            return ParseResult(ParseStatus.REJECTED, None, ("invalid title",))
        if not document.raw_blocks or len(document.raw_blocks) > 64:
            return ParseResult(ParseStatus.REJECTED, None, ("invalid block count",))
        seen: set[tuple[int, int, str | None, int | None]] = set()
        review: list[str] = []
        try:
            document.title.encode("utf-8")
            for block in document.raw_blocks:
                if not isinstance(block, ParsedBlock) or not isinstance(
                    block.kind, BlockKind
                ):
                    raise ValueError("invalid block kind")
                if (
                    not isinstance(block.text, str)
                    or not block.text.strip()
                    or len(block.text) > MAX_BLOCK_CHARS
                ):
                    raise ValueError("invalid or oversized parsed block")
                block.text.encode("utf-8")
                location = block.location
                if not isinstance(location, SourceLocation):
                    raise ValueError("invalid source location")
                if location.table_id is not None and (
                    not isinstance(location.table_id, str)
                    or re.fullmatch(r"[A-Za-z0-9._-]{1,128}", location.table_id) is None
                ):
                    raise ValueError("invalid table identifier")
                if location.row_index is not None and (
                    type(location.row_index) is not int or location.row_index < 1
                ):
                    raise ValueError("invalid row index")
                if (
                    type(location.page) is not int
                    or location.page < 1
                    or type(location.block_index) is not int
                    or location.block_index < 1
                ):
                    raise ValueError("source page/block must be positive integers")
                if location.start_char is not None or location.end_char is not None:
                    raise ValueError(
                        "input fixture locations must identify full blocks"
                    )
                key = (
                    location.page,
                    location.block_index,
                    location.table_id,
                    location.row_index,
                )
                if key in seen:
                    raise ValueError("duplicate source location")
                seen.add(key)
                if block.kind == BlockKind.TABLE_ROW:
                    if (
                        not location.table_id
                        or type(location.row_index) is not int
                        or location.row_index < 1
                    ):
                        review.append("table row lacks location metadata")
                    # This is a deliberately narrow fixture grammar, not a table parser.
                    if not re.search(
                        r"product=[^;]+; quantity=[0-9,]+(?:\.[0-9]+)? (?:kg|ea); unit price=USD [0-9]+\.[0-9]{2}\.?$",
                        block.text,
                    ):
                        review.append("table row requires labelled numeric review")
                if "\ufffd" in block.text:
                    review.append("replacement character requires review")
        except (ValueError, UnicodeEncodeError) as exc:
            return ParseResult(ParseStatus.REJECTED, None, (str(exc),))
        text = canonical_block_text(document.raw_blocks)
        if len(text) > MAX_DOCUMENT_CHARS:
            return ParseResult(
                ParseStatus.REJECTED, None, ("oversized parsed document",)
            )
        if all(block.kind == BlockKind.HEADING for block in document.raw_blocks):
            review.append("document has no substantive body")
        status = ParseStatus.NEEDS_REVIEW if review else ParseStatus.ACCEPTED
        source = ParsedSource(
            SourceIdentity(*identifiers, digest_text(text)),
            document.title,
            self.parser_id,
            self.parser_version,
            extract_metadata(document.title, document.raw_blocks),
            document.raw_blocks,
            status,
        )
        return ParseResult(status, source, tuple(dict.fromkeys(review)))


def extract_metadata(
    title: str, blocks: Sequence[ParsedBlock]
) -> tuple[tuple[str, str], ...]:
    """Extract only deterministic fixture metadata; missing labels remain absent."""
    values: list[tuple[str, str]] = [("title", title)]
    source_text = canonical_block_text(blocks)
    supplier = re.search(r"([A-Z][A-Za-z]+(?: [A-Z][A-Za-z]+)*) supplies", source_text)
    if supplier:
        values.append(("supplier", supplier.group(1)))
    if any(block.kind == BlockKind.TABLE_ROW for block in blocks):
        values.append(("contains_table", "true"))
    return tuple(values)
```

`FixtureParser` is intentionally not a PDF/OCR implementation. It is a local, deterministic boundary that lets the remaining contracts be tested without claiming semantic parser quality. A real parser adapter should validate file type and size before parsing, isolate untrusted parsers, record parser/OCR artifact/version, preserve page/table coordinates, report malformed layout explicitly, and avoid logging raw document content.

The parser may accept a document with a table only when its representation meets the stated fixture policy. A real policy can permit a `needs_review` source to be stored for review while refusing to index table-derived facts. That distinction is safer than dropping the table or treating a degraded reconstruction as authoritative.

**Checkpoint.** Does a digest make the parsed content trustworthy? No. It identifies the exact parsed text under a known record. Authenticity, authorization, parser correctness, and document truth require separate controls.

## 2. Metadata and locations are part of a retrieval record

### What must a reviewer receive besides text?

Every chunk must lead back to an immutable source identity, document version, parser configuration, block locations, and metadata. Metadata enables two very different operations:

- **interpretation:** a reviewer can see that a result is from P-105 version 1, Schedule A, and Section 3; and
- **deterministic boundary checks:** the service can restrict a search to an authorised tenant or supported document type before candidate retrieval.

Metadata is not permission. A client’s request containing `tenant_id=northwind-procurement` is not proof that the caller can read that tenant. An authorization service must derive permitted objects from the authenticated principal. The chunker preserves `tenant_id` for lineage; it does not decide access.

For tables, preserve at least table ID, row index, page, header representation, and the source text/formula used to create the retrieval representation. A row should not be presented as a complete contractual fact if the parser cannot state which header belongs to which value.

## 3. A policy is a versioned function, not a string in a config file

### What changes when “use 200 characters” becomes “use 240”?

Chunk policy changes the indexable corpus. It affects IDs, count, average length, duplicate context, vector storage, and which evidence can be returned. Treat it as a typed, versioned contract with explicit parameters. The code below embeds the policy fingerprint in every chunk ID and manifest.

```python
@dataclass(frozen=True)
class ChunkPolicyIdentity:
    name: str
    version: str
    parameters: tuple[tuple[str, str], ...]

    def fingerprint(self) -> str:
        items = (
            self.name,
            self.version,
            *(f"{key}={value}" for key, value in self.parameters),
        )
        return digest_text("\x1f".join(items))


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    chunk_digest: str
    source_identity: SourceIdentity
    policy_fingerprint: str
    text: str
    locations: tuple[SourceLocation, ...]
    metadata: tuple[tuple[str, str], ...]
    parent_chunk_id: str | None


class ChunkPolicy(Protocol):
    @property
    def identity(self) -> ChunkPolicyIdentity: ...

    def chunk(self, source: ParsedSource) -> tuple[Chunk, ...]: ...


def make_chunk(
    source: ParsedSource,
    policy: ChunkPolicyIdentity,
    *,
    ordinal: int,
    text: str,
    locations: Sequence[SourceLocation],
    parent_chunk_id: str | None = None,
) -> Chunk:
    if not text.strip() or len(text) > MAX_DOCUMENT_CHARS:
        raise ChunkPolicyError("chunk text must be non-empty and bounded")
    if type(ordinal) is not int or ordinal < 0:
        raise ChunkPolicyError("chunk ordinal must be a non-negative integer")
    locations = tuple(dict.fromkeys(locations))
    if not locations:
        raise ChunkPolicyError("chunk must preserve at least one source location")
    for location in locations:
        original = replace(location, start_char=None, end_char=None)
        blocks = [block for block in source.blocks if block.location == original]
        if len(blocks) != 1:
            raise ChunkPolicyError("chunk location must resolve to one source block")
        if (location.start_char is None) != (location.end_char is None):
            raise ChunkPolicyError("chunk range requires both offsets")
        if location.start_char is not None:
            if (
                type(location.start_char) is not int
                or type(location.end_char) is not int
                or not 0
                <= location.start_char
                < location.end_char
                <= len(blocks[0].text.strip())
            ):
                raise ChunkPolicyError("chunk range is outside its source block")
    payload = "\x1f".join(
        (
            source.identity.tenant_id,
            source.identity.document_id,
            source.identity.version,
            source.identity.content_digest,
            source_fingerprint(source),
            policy.fingerprint(),
            str(ordinal),
            parent_chunk_id or "",
            text,
            *(location.label() for location in locations),
        )
    )
    chunk_digest = digest_text(payload)
    return Chunk(
        chunk_id=f"{source.identity.document_id}:{source.identity.version}:{policy.name}:{ordinal}:{chunk_digest[:12]}",
        chunk_digest=chunk_digest,
        source_identity=source.identity,
        policy_fingerprint=policy.fingerprint(),
        text=text,
        locations=tuple(locations),
        metadata=source.metadata,
        parent_chunk_id=parent_chunk_id,
    )


def source_fingerprint(source: ParsedSource) -> str:
    """Fingerprint parsed representation, including layout and parser metadata."""
    return digest_text(
        json.dumps(
            {
                "identity": asdict(source.identity),
                "title": source.title,
                "parser": (source.parser_id, source.parser_version),
                "metadata": source.metadata,
                "status": source.parse_status,
                "blocks": [asdict(block) for block in source.blocks],
            },
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )
    )


def window_locations(
    source: ParsedSource, start: int, end: int
) -> tuple[SourceLocation, ...]:
    """Map half-open canonical-text ranges to trimmed block-relative ranges."""
    locations: list[SourceLocation] = []
    cursor = 0
    for block in source.blocks:
        text = block.text.strip()
        lo, hi = max(start, cursor), min(end, cursor + len(text))
        if lo < hi:
            locations.append(
                replace(block.location, start_char=lo - cursor, end_char=hi - cursor)
            )
        cursor += len(text) + 1  # canonical newline separator
    return tuple(locations)


def window_chunks(
    source: ParsedSource, policy: ChunkPolicyIdentity, width: int, overlap: int
) -> tuple[Chunk, ...]:
    if (
        type(width) is not int
        or width < 1
        or type(overlap) is not int
        or not 0 <= overlap < width
    ):
        raise ChunkPolicyError("require integer width > 0 and 0 <= overlap < width")
    text = canonical_block_text(source.blocks)
    if not text or len(text) > MAX_DOCUMENT_CHARS:
        raise ChunkPolicyError("source exceeds bounded chunk policy")
    chunks: list[Chunk] = []
    start = 0
    while start < len(text):
        end = min(start + width, len(text))
        fragment = text[start:end]
        if fragment.strip():
            chunks.append(
                make_chunk(
                    source,
                    policy,
                    ordinal=len(chunks),
                    text=fragment,
                    locations=window_locations(source, start, end),
                )
            )
        if end == len(text):
            break  # do not add a tail entirely contained in the previous window
        start += width - overlap
    return tuple(chunks)


def chunk_set_digest(chunks: Sequence[Chunk]) -> str:
    return digest_text(
        json.dumps(
            [asdict(chunk) for chunk in chunks],
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )
    )


@dataclass(frozen=True)
class FixedSizePolicy:
    width: int

    @property
    def identity(self) -> ChunkPolicyIdentity:
        return ChunkPolicyIdentity("fixed", "1.1.0", (("width", str(self.width)),))

    def chunk(self, source: ParsedSource) -> tuple[Chunk, ...]:
        return window_chunks(source, self.identity, self.width, 0)


@dataclass(frozen=True)
class OverlapPolicy:
    width: int
    overlap: int

    @property
    def identity(self) -> ChunkPolicyIdentity:
        return ChunkPolicyIdentity(
            "overlap",
            "1.1.0",
            (("width", str(self.width)), ("overlap", str(self.overlap))),
        )

    def chunk(self, source: ParsedSource) -> tuple[Chunk, ...]:
        return window_chunks(source, self.identity, self.width, self.overlap)
```

Fixed-size chunks are a useful baseline because they are simple, repeatable, and easy to count. Their failure is structural blindness: they can cut a statement, table row, or page transition anywhere. Overlap reduces boundary loss by repeating text, but every repeated span produces more chunks, vectors, storage, potential duplicate results, and opportunity for an evaluation set to count the same evidence twice.

The fixed and overlap policies now attach only the blocks their windows actually intersect. Each span is half-open: `start_char` is included and `end_char` is excluded. Offsets refer to the **trimmed parsed block**, measured in Python characters. They are not raw-file byte offsets, PDF coordinates, or tokenizer positions. A real parser must keep the mapping back to its source representation.

For example, a 200-character block with width 120 and overlap 40 produces `[0,120)` and `[80,200)`. Stop there: a third `[160,200)` window would contain only text already covered by the second. With stride `s = width - overlap`, the window count for ordinary nonblank text is `1` when `L <= width`, otherwise `1 + ceil((L - width) / s)`. Whitespace-only windows are omitted by this bounded implementation. For long text, an overlap fraction `r` approaches a text-volume multiplier of `1 / (1-r)`; finite documents, newlines, UTF-8 encoding, and partial tails change the exact byte count.

Before embedding, check the selected model's actual tokenizer limit **including document instructions and special tokens**. Character width is a convenient teaching parameter. Sentence and structure policies use soft targets or natural units, so they can exceed that width. Split, review, or reject oversized model inputs explicitly; silent encoder truncation can remove the very exception you preserved.

**Checkpoint.** Why is overlap a manifest-changing policy rather than a query-time option? It changes the stored chunks themselves. Comparing a no-overlap index with an overlap index is a corpus-policy experiment, not merely a search parameter change.

## 4. Sentence and structure policies preserve different signals

### What boundary is meaningful in P-105?

Sentence-based chunking protects readable prose. It creates chunks from complete sentences until a target width is reached. It can avoid cutting `Net 30 after inspection approval` in half, but it cannot know that P-105’s cross-reference requires both the heading and Schedule A context. Sentence detection itself is format- and language-dependent; a period can be an abbreviation, decimal, item label, or malformed OCR mark.

Structure-aware chunking uses parser blocks. It can attach a heading to its subsequent paragraph and represent a table row with header-aware fields. It is often the more meaningful policy for P-105, but only when parser layout reconstruction is trustworthy enough to identify those blocks. A structure-aware policy with a wrong heading is worse than a transparent fixed baseline.

```python
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


@dataclass(frozen=True)
class SentencePolicy:
    target_width: int

    @property
    def identity(self) -> ChunkPolicyIdentity:
        return ChunkPolicyIdentity(
            "sentence", "1.1.0", (("target_width", str(self.target_width)),)
        )

    def chunk(self, source: ParsedSource) -> tuple[Chunk, ...]:
        if type(self.target_width) is not int or self.target_width <= 0:
            raise ChunkPolicyError("sentence target width must be a positive integer")
        chunks: list[Chunk] = []
        pending: list[str] = []
        locations: list[SourceLocation] = []

        def flush() -> None:
            if pending:
                chunks.append(
                    make_chunk(
                        source,
                        self.identity,
                        ordinal=len(chunks),
                        text=" ".join(pending),
                        locations=locations,
                    )
                )
                pending.clear()
                locations.clear()

        for block in source.blocks:
            if block.kind != BlockKind.PARAGRAPH:
                flush()
                chunks.append(
                    make_chunk(
                        source,
                        self.identity,
                        ordinal=len(chunks),
                        text=block.text.strip(),
                        locations=[block.location],
                    )
                )
                continue
            for sentence in SENTENCE_END.split(block.text.strip()):
                if pending and len(" ".join((*pending, sentence))) > self.target_width:
                    flush()
                pending.append(sentence)
                locations.append(block.location)
        flush()
        return tuple(chunks)


@dataclass(frozen=True)
class StructurePolicy:
    include_heading: bool = True

    @property
    def identity(self) -> ChunkPolicyIdentity:
        return ChunkPolicyIdentity(
            "structure",
            "1.0.0",
            (("include_heading", str(self.include_heading)),),
        )

    def chunk(self, source: ParsedSource) -> tuple[Chunk, ...]:
        chunks: list[Chunk] = []
        heading: ParsedBlock | None = None
        for block in source.blocks:
            if block.kind == BlockKind.HEADING:
                heading = block
                continue
            if block.kind not in {BlockKind.PARAGRAPH, BlockKind.TABLE_ROW}:
                continue
            prefix = f"{heading.text}\n" if self.include_heading and heading else ""
            locations = tuple(
                location
                for location in (
                    heading.location if self.include_heading and heading else None,
                    block.location,
                )
                if location is not None
            )
            chunks.append(
                make_chunk(
                    source,
                    self.identity,
                    ordinal=len(chunks),
                    text=f"{prefix}{block.text}".strip(),
                    locations=locations,
                )
            )
        return tuple(chunks)
```

The sentence regex is a deterministic illustrative splitter, not a general language parser. Headings and table rows are emitted as atomic chunks, so choosing sentence boundaries does not discard non-prose evidence. A single long sentence can exceed the target width. Sentence citations retain block-level granularity rather than pretending to provide exact sentence offsets. The structure policy keeps each table row as a separate block and inherits its heading, but it does not create a table parser. A real table policy should keep table header, row, column, page, parser confidence, and original coordinates; it should reject ambiguous field mapping rather than make column order look reliable.

## 5. Semantic chunking changes the boundary algorithm, not the truth model

### Can local similarity decide where a topic ends?

Semantic chunking evaluates the relationship between neighbouring units—often sentences or paragraphs—and starts a new chunk when similarity falls below a threshold. It can group topic-consistent prose better than a fixed window, but it adds a model, metric, threshold, preprocessing, language, and evaluation boundary.

It can also fail precisely where procurement documents are most consequential. Schedule A and Section 3 may be linguistically different while contractually related. A local similarity threshold can split their relationship; a repeated boilerplate clause can look similar while applying to another supplier or version.

Use an injected boundary, not an invisible model call. This deterministic example measures shared lower-case terms only. It exists to make the policy/testable threshold contract visible; it does not measure semantic quality or stand in for a real local embedding model.

```python
class AdjacentSimilarity(Protocol):
    @property
    def identity(self) -> str: ...

    def score(self, left: str, right: str) -> float: ...


@dataclass(frozen=True)
class SharedTermSimilarity:
    """Teaching-only deterministic boundary, not an embedding model."""

    @property
    def identity(self) -> str:
        return "shared-term-jaccard/1.0.0"

    def score(self, left: str, right: str) -> float:
        left_terms = set(re.findall(r"[a-z0-9]+", left.lower()))
        right_terms = set(re.findall(r"[a-z0-9]+", right.lower()))
        union = left_terms | right_terms
        return len(left_terms & right_terms) / len(union) if union else 0.0


@dataclass(frozen=True)
class SemanticPolicy:
    similarity: AdjacentSimilarity
    threshold: float

    @property
    def identity(self) -> ChunkPolicyIdentity:
        return ChunkPolicyIdentity(
            "semantic",
            "1.1.0",
            (
                ("similarity", self.similarity.identity),
                ("threshold", str(self.threshold)),
            ),
        )

    def chunk(self, source: ParsedSource) -> tuple[Chunk, ...]:
        if (
            type(self.threshold) not in (int, float)
            or not isfinite(self.threshold)
            or not 0.0 <= self.threshold <= 1.0
        ):
            raise ChunkPolicyError("semantic threshold must be finite and in [0, 1]")
        groups: list[list[ParsedBlock]] = []
        pending: list[ParsedBlock] = []
        for block in source.blocks:
            if block.kind != BlockKind.PARAGRAPH:
                if pending:
                    groups.append(pending)
                    pending = []
                groups.append([block])
                continue
            if pending:
                score = self.similarity.score(pending[-1].text, block.text)
                if (
                    type(score) not in (int, float)
                    or not isfinite(score)
                    or not -1 <= score <= 1
                ):
                    raise ChunkPolicyError(
                        "adjacent similarity must be finite and in [-1, 1]"
                    )
                if score < self.threshold:
                    groups.append(pending)
                    pending = []
            pending.append(block)
        if pending:
            groups.append(pending)
        return tuple(
            make_chunk(
                source,
                self.identity,
                ordinal=ordinal,
                text=" ".join(block.text.strip() for block in group),
                locations=[block.location for block in group],
            )
            for ordinal, group in enumerate(groups)
        )
```

A real local embedding adapter should record model/artifact digest, runtime, query/document or boundary instruction, dimension, normalization, metric, and threshold. A changed threshold is a different policy; a changed model is a different policy even with the same threshold. Evaluate both against fixed and structure-aware policies on the same frozen source snapshot.

## 6. Parent-child retrieval separates matching from readable context

### How can a small match return sufficient evidence?

The most focused unit for matching may be a single P-105 paragraph. The readable unit may be the parent section containing its heading and neighbouring cross-reference. Parent-child retrieval stores both relationships explicitly:

```text
parent: P-105 / Section 3 — Invoicing
  child: Invoice terms are Net 30 after inspection approval.
  child: The payment condition in this section controls Schedule A.

match child -> return child plus declared parent context -> review source locations
```

This is not permission to return arbitrary document context. Parent and child must share source identity/version, preserve lineage, and both pass authorization before matching or display. Returning a whole parent can increase sensitive-text exposure and noise, so define the context rule and measure its effect on support completeness.

```python
@dataclass(frozen=True)
class ParentChildPolicy:
    @property
    def identity(self) -> ChunkPolicyIdentity:
        return ChunkPolicyIdentity(
            "parent-child",
            "1.1.0",
            (("child_unit", "parsed_block"),),
        )

    def chunk(self, source: ParsedSource) -> tuple[Chunk, ...]:
        parent_chunks: list[Chunk] = []
        child_chunks: list[Chunk] = []
        heading: ParsedBlock | None = None
        section_blocks: list[ParsedBlock] = []

        def flush_section() -> None:
            if not section_blocks and heading is None:
                return
            # An isolated heading remains an explicit child, rather than disappearing.
            body_blocks = (
                tuple(section_blocks)
                if section_blocks
                else ((heading,) if heading else ())
            )
            parent_heading = heading.text if heading else source.title
            parent_locations = [block.location for block in body_blocks]
            if heading and section_blocks:
                parent_locations.insert(0, heading.location)
            parent = make_chunk(
                source,
                self.identity,
                ordinal=len(parent_chunks),
                text="\n".join(
                    (parent_heading, *(block.text for block in section_blocks))
                ),
                locations=parent_locations,
            )
            parent_chunks.append(parent)
            for block in body_blocks:
                child_chunks.append(
                    make_chunk(
                        source,
                        self.identity,
                        ordinal=len(child_chunks),
                        text=block.text,
                        locations=[block.location],
                        parent_chunk_id=parent.chunk_id,
                    )
                )

        for block in source.blocks:
            if block.kind == BlockKind.HEADING:
                flush_section()
                heading, section_blocks = block, []
            elif block.kind in {BlockKind.PARAGRAPH, BlockKind.TABLE_ROW}:
                section_blocks.append(block)
        flush_section()
        return tuple((*parent_chunks, *child_chunks))
```

The implementation uses a nested `flush_section` function to make section state explicit. It returns parents and children in one collection; production retrieval should classify them by lineage and define which kinds are allowed to be matched versus shown. The code does not embed or rank chunks—it produces the lineage a downstream Week 5-compatible retrieval boundary can index.

## 7. Build a chunk manifest and filter authorized records before retrieval

### What makes a chunk collection reproducible?

The same document under a different parser, policy, parameter, or source version is a different retrieval corpus. A manifest records what was built. It does not grant access and it does not replace source records.

Use two different fingerprints deliberately. `content_digest` hashes canonical parsed text. `source_fingerprint` also includes title, parser version, metadata, status, block kinds, and locations: the same words on a different page or under a different heading are a changed representation. `contents_digest` checks the serialized chunk snapshot, including parent links. These hashes detect inconsistency against a trusted manifest; they are not signatures or evidence that a parser or source is authentic. Store and authorize the manifest itself through trusted application code.

```python
@dataclass(frozen=True)
class ChunkManifest:
    schema_version: str
    parser_id: str
    parser_version: str
    policy_fingerprint: str
    source_digest: str
    chunk_count: int
    created_at: datetime
    source_fingerprint: str
    contents_digest: str


@dataclass(frozen=True)
class ChunkCollection:
    manifest: ChunkManifest
    chunks: tuple[Chunk, ...]

    def __post_init__(self) -> None:
        if self.manifest.schema_version != CHUNK_MANIFEST_SCHEMA:
            raise ManifestCompatibilityError("unsupported chunk schema")
        if self.manifest.created_at.tzinfo is None:
            raise ManifestCompatibilityError("manifest time must be timezone-aware")
        if not self.chunks or self.manifest.chunk_count != len(self.chunks):
            raise ManifestCompatibilityError("manifest chunk count mismatch")
        if self.manifest.contents_digest != chunk_set_digest(self.chunks):
            raise ManifestCompatibilityError("chunk contents differ from manifest")
        by_id = {chunk.chunk_id: chunk for chunk in self.chunks}
        if len(by_id) != len(self.chunks):
            raise ManifestCompatibilityError("duplicate chunk IDs")
        if len({chunk.source_identity for chunk in self.chunks}) != 1:
            raise ManifestCompatibilityError(
                "collection must contain one source identity"
            )
        for chunk in self.chunks:
            if chunk.policy_fingerprint != self.manifest.policy_fingerprint:
                raise ManifestCompatibilityError("chunk policy mismatch")
            if chunk.source_identity.content_digest != self.manifest.source_digest:
                raise ManifestCompatibilityError("chunk source mismatch")
            if chunk.parent_chunk_id is not None:
                parent = by_id.get(chunk.parent_chunk_id)
                if (
                    parent is None
                    or parent.parent_chunk_id is not None
                    or parent.source_identity != chunk.source_identity
                ):
                    raise ManifestCompatibilityError("invalid parent-child lineage")

    @classmethod
    def build(
        cls, source: ParsedSource, policy: ChunkPolicy, *, created_at: datetime
    ) -> Self:
        if created_at.tzinfo is None:
            raise ValueError("manifest time must be timezone-aware")
        if source.parse_status != ParseStatus.ACCEPTED:
            raise ParseRejectedError(
                "review-required source cannot enter an accepted index"
            )
        if source.identity.content_digest != digest_text(
            canonical_block_text(source.blocks)
        ):
            raise ManifestCompatibilityError(
                "source digest does not match parsed blocks"
            )
        identity = policy.identity
        chunks = policy.chunk(source)
        if policy.identity != identity:
            raise ManifestCompatibilityError("policy identity changed during chunking")
        if any(chunk.source_identity != source.identity for chunk in chunks):
            raise ManifestCompatibilityError(
                "chunk source identity differs from collection source"
            )
        manifest = ChunkManifest(
            CHUNK_MANIFEST_SCHEMA,
            source.parser_id,
            source.parser_version,
            identity.fingerprint(),
            source.identity.content_digest,
            len(chunks),
            created_at.astimezone(UTC),
            source_fingerprint(source),
            chunk_set_digest(chunks),
        )
        return cls(manifest, chunks)


class ChunkAccessPolicy(Protocol):
    def can_read(self, principal_id: str, chunk: Chunk) -> bool: ...


@dataclass(frozen=True)
class StaticChunkAccessPolicy:
    permitted: frozenset[tuple[str, str, str, str]]

    def can_read(self, principal_id: str, chunk: Chunk) -> bool:
        source = chunk.source_identity
        return (
            principal_id,
            source.tenant_id,
            source.document_id,
            source.version,
        ) in self.permitted


def authorized_chunks(
    principal_id: str,
    chunks: Iterable[Chunk],
    access_policy: ChunkAccessPolicy,
) -> tuple[Chunk, ...]:
    if not principal_id.strip():
        raise ValueError("principal ID must be non-empty")
    return tuple(
        chunk for chunk in chunks if access_policy.can_read(principal_id, chunk)
    )
```

Authorization must constrain candidate selection before retrieval scores are computed. Filtering after a vector search can leak whether an unauthorized document exists through result count, timing, score, or cache behavior. This local reference therefore exposes `authorized_chunks` as the only collection a downstream retrieval caller should receive.

Operationally, build a new manifest when the parser, OCR engine, raw-source snapshot, metadata policy, chunk policy, tokenizer accounting, or local embedding configuration changes. Promote an immutable manifest only after tests and held-out evaluation; rollback means selecting a prior approved manifest/source snapshot, not mutating chunks in place. Rebuilds should be idempotent for the same source and configuration.

## 8. Compare policies fairly: retrieval, cost, and support completeness

### How do we compare chunks without choosing a favorite example?

The comparison unit is a frozen collection of P-101 through P-105 with the same parser output, source versions, authorization filter, retrieval configuration, and query labels. The independent variable is the chunk policy. Do not allow one policy to preserve table headers or metadata while another is given only flattened text unless that is explicitly the comparison being measured.

Retrieval quality needs labels. Answer-support completeness needs stricter labels. For the P-105 query, a result set supports a reviewer only if it contains all required evidence atoms: the `1,000 kg copper wire` row, `Net 30 after inspection approval`, and the statement linking Section 3 to Schedule A. This is not generated-answer evaluation; it is a check that retrieved source units permit a reviewer to support a stated response.

```python
@dataclass(frozen=True)
class EvaluationCase:
    query_id: str
    required_atoms: frozenset[str]
    relevant_document_ids: frozenset[str]


@dataclass(frozen=True)
class PolicyMeasurement:
    policy_name: str
    source_digest: str
    chunk_count: int
    average_chunk_length: float
    text_storage_bytes: int
    support_complete: bool


def chunks_contain_all(chunks: Iterable[Chunk], atoms: frozenset[str]) -> bool:
    available = "\n".join(chunk.text.lower() for chunk in chunks)
    return all(atom.lower() in available for atom in atoms)


def measure_policy(
    collection: Sequence[ChunkCollection],
    case: EvaluationCase,
    returned_chunk_ids: frozenset[str],
) -> PolicyMeasurement:
    all_chunks = tuple(chunk for item in collection for chunk in item.chunks)
    if not all_chunks:
        raise ValueError("collection must contain chunks")
    if not returned_chunk_ids <= {chunk.chunk_id for chunk in all_chunks}:
        raise ValueError("returned IDs must belong to the compared collection")
    policy = collection[0].manifest.policy_fingerprint
    if any(item.manifest.policy_fingerprint != policy for item in collection):
        raise ManifestCompatibilityError("comparison collection must use one policy")
    source_digest = digest_text(
        "\n".join(sorted(item.manifest.source_fingerprint for item in collection))
    )
    returned_relevant = tuple(
        chunk
        for chunk in all_chunks
        if chunk.chunk_id in returned_chunk_ids
        and chunk.source_identity.document_id in case.relevant_document_ids
    )
    return PolicyMeasurement(
        policy_name=policy,
        source_digest=source_digest,
        chunk_count=len(all_chunks),
        average_chunk_length=mean(len(chunk.text) for chunk in all_chunks),
        text_storage_bytes=sum(len(chunk.text.encode("utf-8")) for chunk in all_chunks),
        support_complete=chunks_contain_all(returned_relevant, case.required_atoms),
    )
```

`measure_policy` deliberately measures only chunk count, average text length, text bytes, and a synthetic support predicate. It is not a retrieval benchmark: it does not call an embedding model or claim a winner. For an actual comparison, add held-out query–relevance judgments and measure retrieval metrics under a fixed local embedding/index configuration.

Record at least:

| Measure | Definition | Failure to avoid |
| --- | --- | --- |
| Retrieval quality | Recall@k, Precision@k, MRR, or nDCG on held-out labels | testing on the same cases used to choose policy parameters |
| Chunk count | total retrieval units per frozen source set | comparing different document snapshots |
| Average length | tokenizer-versioned token count or an explicit proxy | calling characters “tokens” |
| Storage impact | text, metadata, vector, and index overhead separately | reporting only raw vector bytes |
| Support completeness | required evidence atoms present in reviewable returned units | treating a fluent answer as evidence |

The table above defines the measurements. Section 14 adds an executed practice run, with its model and measurement limits shown explicitly. A production measurement must state its corpus snapshot, parser/OCR version, policy identity, local model/index identity, authorization filter, query split, label version, hardware, and latency boundary. One policy may improve Recall@5 while creating duplicate chunks, reducing Precision@5, increasing storage, or failing on OCR/table subgroups.

### A reasonable evaluation procedure

1. Build a governed development set and a held-out set. Split near-duplicate agreements and amendments by source family or time so copied text cannot leak across splits.
2. Define direct relevance, partial relevance, non-relevance, and support atoms before inspecting rankings. Retain label disagreement/adjudication rather than hiding it in one number.
3. Run fixed, overlap, sentence, semantic, structure-aware, and parent-child policies on the same source snapshot. Freeze local embedding, metric, top-k, filtering, and retrieval implementation.
4. Measure retrieval metrics, chunk count, average length, storage, index build time, query latency, duplicate rate, and support completeness. Stratify by document type, table/OCR condition, language, amendment/version, and query type.
5. Inspect false positives and false negatives with authorized reviewers. Promote only a policy with acceptable quality, security, cost, and failure behavior; retain an exact rollback manifest.

## 9. Cumulative fixtures and tests make failure visible

### Which chunking claims can deterministic tests prove?

The following fixture creates P-101 through P-105. The runnable lab also supplies P-106 with `USD 12.O0`, which the fixture grammar marks `needs_review`. It verifies parser failure, no silent truncation, overlap constraints, stable IDs, version isolation, parent-child lineage, authorization, and that several policies receive the same source collection. It does not prove that a local semantic model retrieves well.

```python
FIXED_TIME = datetime(2026, 8, 16, tzinfo=UTC)
PARSER = FixtureParser()


def block(kind: BlockKind, page: int, index: int, text: str, *, table: str | None = None, row: int | None = None) -> ParsedBlock:
    return ParsedBlock(kind, SourceLocation(page, index, table, row), text)


def fixture_documents() -> tuple[UntrustedDocument, ...]:
    return (
        UntrustedDocument(
            "northwind-procurement", "P-101", "1", "Atlas Metals purchase confirmation",
            (block(BlockKind.PARAGRAPH, 1, 1, "Copper wire will ship after incoming-material inspection. Invoice terms: Net 30 after inspection approval."),),
        ),
        UntrustedDocument(
            "northwind-procurement", "P-102", "1", "Beacon Plastics purchase confirmation",
            (block(BlockKind.PARAGRAPH, 1, 1, "Polymer pellets will ship on 2026-09-03. Invoice terms: Net 15 from receipt."),),
        ),
        UntrustedDocument(
            "northwind-procurement", "P-103", "1", "Atlas Metals delivery update",
            (block(BlockKind.PARAGRAPH, 1, 1, "The copper-wire shipment is delayed by two days while quality checks finish."),),
        ),
        UntrustedDocument(
            "northwind-procurement", "P-104", "1", "Cedar Fasteners payment note",
            (block(BlockKind.PARAGRAPH, 1, 1, "Payment is due after the receiving team signs off on the delivered bolts."),),
        ),
        UntrustedDocument(
            "northwind-procurement", "P-105", "1", "Atlas Metals framework agreement",
            (
                block(BlockKind.HEADING, 1, 1, "Section 1 — Scope"),
                block(BlockKind.PARAGRAPH, 1, 2, "Atlas Metals supplies copper wire to the Northwind plant."),
                block(BlockKind.HEADING, 1, 3, "Section 2 — Delivery and acceptance"),
                block(BlockKind.PARAGRAPH, 1, 4, "The receiving team records incoming-material inspection before acceptance."),
                block(BlockKind.HEADING, 1, 5, "Schedule A — line items"),
                block(BlockKind.TABLE_ROW, 1, 6, "Schedule A, row 1: product=copper wire; quantity=1,000 kg; unit price=USD 12.00.", table="schedule-a", row=1),
                block(BlockKind.HEADING, 1, 7, "Section 3 — Invoicing"),
                block(BlockKind.PARAGRAPH, 1, 8, "Invoice terms are Net 30 after inspection approval."),
                block(BlockKind.PARAGRAPH, 1, 9, "The payment condition in this section controls Schedule A."),
            ),
        ),
    )


def accepted_sources() -> tuple[ParsedSource, ...]:
    results = tuple(PARSER.parse(document) for document in fixture_documents())
    assert all(result.status == ParseStatus.ACCEPTED and result.source is not None for result in results)
    return tuple(result.source for result in results if result.source is not None)


def expect_raises(expected: type[Exception], operation: Callable[[], object]) -> None:
    try:
        operation()
    except expected:
        return
    raise AssertionError(f"expected {expected.__name__}")


def test_parser_rejects_malformed_blocks_without_drop() -> None:
    result = PARSER.parse(UntrustedDocument("tenant", "P-bad", "1", "bad", (block(BlockKind.PARAGRAPH, 1, 1, ""),)))
    assert result.status == ParseStatus.REJECTED
    assert result.source is None


def test_fixed_policy_refuses_silent_truncation() -> None:
    source = accepted_sources()[0]
    oversized = ParsedSource(source.identity, source.title, source.parser_id, source.parser_version, source.metadata, (block(BlockKind.PARAGRAPH, 1, 1, "x" * 4_001),))
    expect_raises(ChunkPolicyError, lambda: FixedSizePolicy(100).chunk(oversized))


def test_overlap_validation_and_stable_ids() -> None:
    source = accepted_sources()[-1]
    expect_raises(ChunkPolicyError, lambda: OverlapPolicy(100, 100).chunk(source))
    first = FixedSizePolicy(100).chunk(source)
    second = FixedSizePolicy(100).chunk(source)
    assert [chunk.chunk_id for chunk in first] == [chunk.chunk_id for chunk in second]


def test_version_isolation_and_parent_lineage() -> None:
    source = accepted_sources()[-1]
    amended = UntrustedDocument(
        source.identity.tenant_id, "P-105", "2", source.title,
        (block(BlockKind.PARAGRAPH, 1, 1, "Invoice terms are Net 45 after approval."),),
    )
    amended_source = PARSER.parse(amended).source
    assert amended_source is not None and amended_source.identity.content_digest != source.identity.content_digest
    lineage = ParentChildPolicy().chunk(source)
    parent_ids = {chunk.chunk_id for chunk in lineage if chunk.parent_chunk_id is None}
    assert parent_ids and all(
        chunk.parent_chunk_id in parent_ids for chunk in lineage if chunk.parent_chunk_id is not None
    )


def test_same_corpus_comparison_and_authorization() -> None:
    sources = accepted_sources()
    policies: tuple[ChunkPolicy, ...] = (
        FixedSizePolicy(120),
        OverlapPolicy(120, 40),
        SentencePolicy(120),
        StructurePolicy(),
        SemanticPolicy(SharedTermSimilarity(), 0.1),
        ParentChildPolicy(),
    )
    collections = tuple(
        tuple(ChunkCollection.build(source, policy, created_at=FIXED_TIME) for source in sources)
        for policy in policies
    )
    source_sets = [
        {item.manifest.source_digest for item in collection} for collection in collections
    ]
    assert all(source_set == source_sets[0] for source_set in source_sets[1:])
    semantic_parameters = dict(SemanticPolicy(SharedTermSimilarity(), 0.1).identity.parameters)
    assert semantic_parameters["similarity"] == "shared-term-jaccard/1.0.0"
    policy = StaticChunkAccessPolicy(
        frozenset({("analyst", "northwind-procurement", "P-105", "1")})
    )
    visible = authorized_chunks("analyst", collections[0][-1].chunks, policy)
    assert visible and all(chunk.source_identity.document_id == "P-105" for chunk in visible)
    support_case = EvaluationCase(
        "p105-payment",
        frozenset(
            {
                "quantity=1,000 kg",
                "Net 30 after inspection approval",
                "controls Schedule A",
            }
        ),
        frozenset({"P-105"}),
    )
    structure_collection = collections[3]
    returned_ids = frozenset(chunk.chunk_id for chunk in structure_collection[-1].chunks)
    assert measure_policy(structure_collection, support_case, returned_ids).support_complete
    assert not measure_policy(structure_collection, support_case, frozenset()).support_complete


def run_displayed_tests() -> None:
    test_parser_rejects_malformed_blocks_without_drop()
    test_fixed_policy_refuses_silent_truncation()
    test_overlap_validation_and_stable_ids()
    test_version_isolation_and_parent_lineage()
    test_same_corpus_comparison_and_authorization()


run_displayed_tests()
```

The fixture parser labels P-105’s table row as accepted because it uses the declared `key=value` representation. That is a fixture contract, not a claim about a PDF parser. The tests are intentionally small, deterministic, and local. Extend them with parser-specific integration tests only after choosing an approved parser/runtime and constructing governed documents.

## 10. Operational boundaries: sensitive documents, rollout, and rollback

### Parser/OCR/table limitations

PDF text extraction can preserve visible text while losing logical order. OCR can produce plausible wrong values. A table engine can mix columns or omit a continuing header. A parser can fail only on one page. Record status and reason per document/page/table, keep source locations, and make unsupported layout visible. Never silently drop an invalid page, row, or a `needs_review` result just to make an index build pass.

### Security and privacy

Documents, metadata, chunks, vectors, query text, and retrieval results can expose sensitive commercial information. Enforce tenant/object authorization before candidate retrieval; use least-privilege parser/index access; encrypt stored data as required; retain only approved content; and avoid source text, raw vectors, parser payloads, or prompts in general logs. A locally run parser/model reduces a network boundary but does not remove host-security, artifact-provenance, caching, retention, or access-control obligations.

### Observability without content leakage

Measure parser status counts, page/table failure reasons, chunk count, average token/character length, build duration, policy/manifest ID, index size, retrieval metrics, support-completeness rate, authorization-denied/empty-result counts, and rebuild/rollback events. Attach digests and configuration IDs rather than raw text. Review sufficiently sampled, authorised source cases in a protected workflow when a metric shifts.

### Rebuild, promotion, rollback

The parser/OCR version, metadata policy, source snapshot, chunk policy, tokenizer accounting, and local embedding/index configuration all affect retrieval. A change requires a new build/manifest and a controlled comparison. Promote only after invariant tests and held-out evaluation pass the agreed threshold. Roll back by selecting an existing approved manifest/source snapshot; do not overwrite old chunks or silently reuse vectors from an incompatible policy.

## 11. Common failure modes

### “We use 500 tokens for every document.”

Which document boundary, retrieval unit, table context, model budget, and held-out evaluation supports that value? A fixed number is a parameter, not a rationale.

### “The parser returned text, so the table is correct.”

Which header, row, page coordinates, OCR/parser status, and source review confirm the field mapping? Visible text can be structurally wrong.

### “Overlap fixes missing context.”

What duplicate rate, storage impact, Precision@k, and support-completeness result justify the repeated content? Overlap can mask a bad boundary while inflating cost.

### “Semantic chunks understand the contract.”

Which local model, threshold, version, and evaluation prove it preserves exceptions, direction, edition, and cross-reference context? Similarity is not legal or factual reasoning.

### “We can filter unauthorized results afterward.”

What prevents score, timing, count, or cache existence leakage? Authorization must constrain candidate retrieval itself.

### “The new parser is a harmless upgrade.”

Does its reading order, table representation, OCR behavior, or metadata extraction change the chunk corpus? Treat it as a manifest-changing build input.

## 12. Interview defense and active recall

**How would you choose chunk size?**

Start from the document’s meaningful structure and the retrieval unit a reviewer must see: a clause, heading-plus-paragraph, table header-plus-row, or parent section. Check the local embedding model’s supported input behavior and the downstream review/context budget. Then compare fixed, overlap, sentence, semantic, structure-aware, and parent-child candidates on the same frozen, held-out collection. Measure Recall@k, Precision@k, MRR/nDCG where appropriate, support completeness, chunk count, token length, storage, latency, and failure subgroups. Select a versioned policy with acceptable security and operational trade-offs; there is no universal 500-token answer.

**Why is parent-child retrieval useful?**

It can match a small focused child while presenting a controlled parent context that preserves headings and cross-references. It requires immutable lineage, source/version compatibility, and authorization for both levels; otherwise it can increase noise or expose unrelated content.

**Why do PDFs and tables need special handling?**

Their visible layout can diverge from extracted logical text. Reading order, OCR, headers, rows, page boundaries, and column mapping can change the meaning of a value. Preserve structural metadata and source locations, treat parser output as untrusted, and test against representative documents.

**What makes a chunking comparison fair?**

Hold source snapshot, parser output, labels, access filter, embedding/index configuration, top-k, and measurement boundary fixed; vary one policy. Report quality, cost, support completeness, and failure groups rather than one attractive example.

### Active recall

1. What does a parsed content digest identify, and what does it not prove?
2. Why must a chunk ID include source version and policy fingerprint?
3. What is the difference between parser acceptance and factual acceptance?
4. Why can a table row without its header be misleading?
5. How can overlap improve Recall@k while harmfully changing the index?
6. What additional contract does semantic chunking introduce?
7. What must parent and child chunks share?
8. Why is support completeness stricter than retrieval relevance?

### Answers

1. It identifies the exact parsed text for a record; it does not prove source authenticity, parser correctness, or factual truth.
2. The same text under another edition or policy is a different retrieval unit and must not collide or silently mix.
3. Parser acceptance says the representation met a boundary contract; factual acceptance requires source evidence and any applicable business review.
4. A price, quantity, or value can change meaning when its column/row association is lost.
5. It creates more copies of boundary text, raising count, storage, duplicate candidates, and potentially evaluation leakage.
6. A local similarity model/metric/preprocessing/threshold/version and its separate evaluation.
7. Immutable source identity/version, declared lineage, and authorization checks before matching or display.
8. A relevant chunk may mention a topic; complete support requires every declared evidence atom needed for the reviewer’s conclusion.

Before the exercises, try answering the recall questions without scrolling back. If your answer is only “make chunks bigger,” revisit which evidence is missing.

## 13. Exercises

1. Add P-106 as a scanned invoice with an OCR-confused character. Define parser status, review route, and a test that prevents an uncertain price from becoming accepted table metadata.
2. Add P-105 version 2 with a changed payment clause. Verify old and new chunks have different identity/digests and write an authorization/filter rule that chooses the allowed active version.
3. Make the fixed policy preserve precise character ranges instead of the conservative all-block location tuple. Add tests for first/last boundary mapping.
4. Create five held-out queries that distinguish a fixed-boundary failure, a heading dependency, a table-header dependency, an amendment conflict, and a cross-tenant denial.
5. Design a semantic-policy experiment with a real approved local adapter. State its model manifest, threshold grid, development/held-out split, failure metrics, and rollback condition before running it.

## 14. Run the same-corpus comparison

The [Week 6 lab](https://github.com/kogantisasank831-ux/Prep/tree/main/labs/week_06) turns the snippets into a runnable experiment. Start at the repository root in the project's Python environment:

```shell
python -m pip install -r requirements-dev.txt
python -m labs.week_06.compare --summary
python -m labs.week_06.compare > .runtime/week06-comparison.json
python -m pytest tests/test_week06_chunking.py -q
```

Create `.runtime` first if it does not exist. The default run uses no model download, credential, network request, or GPU. It uses Week 5's hand-written procurement features plus a constant `0.1` coordinate, which gives heading-only chunks a nonzero vector. That extra coordinate changes the geometry and has its own identity: `week06-teaching-features-with-bias`, dimension 6. The semantic boundary policy separately uses shared-term Jaccard similarity at threshold 0.1. Neither component is a learned semantic model.

### What stays fixed

P-101 through P-105 enter every policy with the same parsed text, metadata, versions, and representation fingerprint. P-106 is a **simulated parsed-layout/OCR defect**, not a PDF that this lab has OCR'd. Its ambiguous price is retained for review and excluded from every index. The parser's accepted table grammar is deliberately narrow; passing it does not prove a number is correct.

Nine checked-in queries are marked `practice`: seven have direct-support labels and two have no labelled support. They are visible teaching cases, not a held-out benchmark. Each strategy ranks its authorized chunk candidates with cosine similarity, breaks ties by chunk ID, returns up to **three chunks**, and admits whole context units into the same **800-character** budget. A unit that does not fit is skipped; no hidden source text is added.

For parent-child retrieval, only children are embedded and ranked. The matching child is replaced by its parent for context after checking parent source/version/policy and authorization again. Repeated parents are deduplicated and their text consumes the same context budget. Stored counts include both parents and children; vector estimates include indexed children only. A Section 3 parent still does not automatically contain Schedule A, so parent expansion alone need not solve Q04.

### Measured teaching output

This is the checked-in [sample summary](https://github.com/kogantisasank831-ux/Prep/blob/main/labs/week_06/sample-comparison.json), produced by the default command:

| Policy | Stored / indexed chunks | Avg indexed chars | Stored text UTF-8 bytes | Packed float32 vector estimate | Document recall at 3 chunks | Complete-support source fraction |
| --- | --- | --- | --- | --- | --- | --- |
| fixed | 8 / 8 | 94.4 | 763 | 192 bytes | 1.000 | 0.667 |
| overlap | 9 / 9 | 101.7 | 927 | 216 bytes | 0.857 | 0.524 |
| sentence | 12 / 12 | 62.3 | 756 | 288 bytes | 0.857 | 0.714 |
| structure | 9 / 9 | 85.9 | 783 | 216 bytes | 0.810 | 0.667 |
| semantic | 13 / 13 | 57.5 | 755 | 312 bytes | 0.810 | 0.667 |
| parent-child | 17 / 9 | 72.3 | 1542 | 216 bytes | 0.810 | 0.667 |

“Document recall at 3 chunks” counts distinct relevant **documents** reached by the three ranked chunks, divided by the query's labelled relevant documents. Chunk IDs change between policies, so these practice labels use a common document granularity. Multiple hits from one document consume the chunk budget while contributing only one document hit. This is not Recall@3 over an independently ranked list of three distinct documents, nor chunk-level evidence recall.

For each query, the support check requires every declared substring atom for a labelled source to appear in that source's admitted context. It never combines a row from one document with a condition from another. It averages the fraction of labelled sources with complete atoms, then averages over the seven labelled queries. It is a conservative synthetic check: equivalent wording can fail, repeated overlap can interrupt a phrase, and matching text does not establish entailment or a valid interpretation. Q08 and Q09 have null recall/support metrics and are excluded from these means. The lab still returns candidates for them; it does **not** implement abstention or certify successful no-answer behavior.

Vector storage here is `indexed_count × 6 × 4` bytes, assuming packed float32 coordinates. It excludes metadata, IDs, parent mappings, Python object overhead, allocator use, and any ANN structure. Text bytes cover stored chunk text only. Token counts, latency, actual index memory, generated answers, and human answer grades were not measured. `generated_answer_quality` and `average_tokens` are explicitly `null` in the report. The table gives you arithmetic to inspect, not a production winner to deploy.

### Inspect Q04 before changing a parameter

Open the full JSON and find Q04. Compare its ranked chunk IDs with the actual chunk text in `chunking.py`/`fixtures.py` or in a Python session. A sufficient P-105 result needs three linked pieces:

1. The copper-wire row with `quantity=1,000 kg`.
2. `Net 30 after inspection approval`, including the condition.
3. The sentence connecting that payment condition to Schedule A.

A relevant document hit can satisfy the retrieval metric while omitting one of these pieces from context. Follow the recorded `context_chunk_ids`, not just the document IDs. Then lower the context budget to 100 and rerun. Which whole units stop fitting? Change width or overlap in `policy_candidates()` as a separate run, record the changed policy fingerprint, and explain one failure in terms of actual source text. Restore or record the parameter before comparing another factor.

Original exercises 1 and 3 now have reference implementations for OCR review and precise fixed-window spans. Attempt them independently first, then extend them with a new ambiguous value and a window crossing two blocks. Exercise 2 and the held-out evaluation design remain independent work.

### Optional actual local-model run

Reuse the Week 5 adapter only after obtaining a reviewed, materialized local text embedding model compatible with its input preparation. Follow the [Week 5 model instructions](https://github.com/kogantisasank831-ux/Prep/tree/main/labs/week_05#optional-actual-local-model-run), including its optional dependency, exact query/document prefixes, and offline settings. Then run:

```shell
python -m labs.week_06.compare --model-directory .runtime/embedding-model --model-id reviewed-local-model --summary
```

The adapter checks prompted token counts before encoding and refuses inputs beyond its model limit. No actual local model, PDF parser, OCR engine, generator, or human grading run is included in the sample above. A real embedding run changes retrieval measurements; it does not turn the shared-term boundary heuristic into learned semantic chunking. To study learned boundaries, implement and version a separate `AdjacentSimilarity` adapter as exercise 5 specifies.

## 15. Your Week 6 handoff

Write a short decision note with the source/query fingerprints, parser policy, chunk parameters, model identity, candidate/context budgets, and your measured results. Include one cited failure where the relevant document was found but the returned evidence was incomplete. State which measurements are still missing before you would choose a production policy.

You are ready to move on when you can run the comparison, explain the extra storage from overlap and parent context, prove a returned citation resolves to its source version, and choose a boundary from the evidence unit and model/context limits. Continue with [Week 7: retrieval]({{ '/weeks/week-07/' | relative_url }}) after completing the independent exercises.

## Primary documentation

- [Python 3.13 `dataclasses`](https://docs.python.org/3.13/library/dataclasses.html)
- [Python 3.13 `typing` and `Protocol`](https://docs.python.org/3.13/library/typing.html)
- [Python 3.13 `hashlib`](https://docs.python.org/3.13/library/hashlib.html)

- [pypdf: text extraction, layout, and OCR limitations](https://pypdf.readthedocs.io/en/stable/user/extract-text.html)
- [Python regular expressions](https://docs.python.org/3.13/library/re.html)
- [Sentence Transformers local model API](https://www.sbert.net/docs/package_reference/sentence_transformer/SentenceTransformer.html)
