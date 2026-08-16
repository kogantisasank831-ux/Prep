---
layout: week
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

The answer is not a magic token count. It is a chain of contracts:

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

### Orienting question: what do we know after a PDF returns text?

Only that a parser produced text. A PDF can contain positioned glyphs rather than logical paragraphs; a scanned page can contain only pixels; an OCR engine can confuse `0` with `O`, a decimal point with a speck, or a table header with a footer. Multi-column layout can yield wrong reading order. A table can be emitted as a sequence of cells without row/column association.

For P-105, this is not cosmetic. `USD 12.00` is meaningful only with its `unit price` header, `copper wire` row, and document/version context. A parser that produces this flat string has lost constraints:

```text
1 copper wire 1,000 kg USD 12.00 line product quantity unit price
```

The parser boundary should return typed blocks, source locations, parser identity, a status, and explicit reasons. A parser may return `accepted`, `needs_review`, or `rejected`; it must not silently drop a malformed table or truncate an oversized page and call the remaining text complete.

```python
from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
import re
from statistics import mean
from typing import Protocol, Self


MAX_DOCUMENT_CHARS = 4_000
MAX_BLOCK_CHARS = 1_000
CHUNK_MANIFEST_SCHEMA = "procurement-chunks/1.0.0"


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

    def label(self) -> str:
        table = f":{self.table_id}" if self.table_id else ""
        row = f":row-{self.row_index}" if self.row_index is not None else ""
        return f"p{self.page}:block-{self.block_index}{table}{row}"


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
    def parse(self, document: UntrustedDocument) -> ParseResult:
        ...


@dataclass(frozen=True)
class FixtureParser:
    """Deterministic fixture boundary; it does not parse PDF bytes or OCR images."""

    parser_id: str = "fixture-parser"
    parser_version: str = "1.0.0"

    def parse(self, document: UntrustedDocument) -> ParseResult:
        identity_values = (document.tenant_id, document.document_id, document.version)
        text = canonical_block_text(document.raw_blocks)
        invalid_block = any(
            not block.text.strip() or len(block.text) > MAX_BLOCK_CHARS
            for block in document.raw_blocks
        )
        if not all(value.strip() for value in identity_values) or not document.title.strip():
            return ParseResult(ParseStatus.REJECTED, None, ("missing source identity",))
        if not text or len(text) > MAX_DOCUMENT_CHARS or invalid_block:
            return ParseResult(ParseStatus.REJECTED, None, ("invalid or oversized parsed blocks",))
        metadata = extract_metadata(document.title, document.raw_blocks)
        source = ParsedSource(
            identity=SourceIdentity(
                tenant_id=document.tenant_id,
                document_id=document.document_id,
                version=document.version,
                content_digest=digest_text(text),
            ),
            title=document.title,
            parser_id=self.parser_id,
            parser_version=self.parser_version,
            metadata=metadata,
            blocks=document.raw_blocks,
        )
        table_blocks = [block for block in document.raw_blocks if block.kind == BlockKind.TABLE_ROW]
        status = ParseStatus.NEEDS_REVIEW if any("=" not in block.text for block in table_blocks) else ParseStatus.ACCEPTED
        reasons = ("table row lacks labelled fields",) if status == ParseStatus.NEEDS_REVIEW else ()
        return ParseResult(status, source, reasons)


def extract_metadata(title: str, blocks: Sequence[ParsedBlock]) -> tuple[tuple[str, str], ...]:
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

### Orienting question: what must a reviewer receive besides text?

Every chunk must lead back to an immutable source identity, document version, parser configuration, block locations, and metadata. Metadata enables two very different operations:

- **interpretation:** a reviewer can see that a result is from P-105 version 1, Schedule A, and Section 3; and
- **deterministic boundary checks:** the service can restrict a search to an authorised tenant or supported document type before candidate retrieval.

Metadata is not permission. A client’s request containing `tenant_id=northwind-procurement` is not proof that the caller can read that tenant. An authorization service must derive permitted objects from the authenticated principal. The chunker preserves `tenant_id` for lineage; it does not decide access.

For tables, preserve at least table ID, row index, page, header representation, and the source text/formula used to create the retrieval representation. A row should not be presented as a complete contractual fact if the parser cannot state which header belongs to which value.

## 3. A policy is a versioned function, not a string in a config file

### Orienting question: what changes when “use 200 characters” becomes “use 240”?

Chunk policy changes the indexable corpus. It affects IDs, count, average length, duplicate context, vector storage, and which evidence can be returned. Treat it as a typed, versioned contract with explicit parameters. The code below embeds the policy fingerprint in every chunk ID and manifest.

```python
@dataclass(frozen=True)
class ChunkPolicyIdentity:
    name: str
    version: str
    parameters: tuple[tuple[str, str], ...]

    def fingerprint(self) -> str:
        items = (self.name, self.version, *(f"{key}={value}" for key, value in self.parameters))
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
    def identity(self) -> ChunkPolicyIdentity:
        ...

    def chunk(self, source: ParsedSource) -> tuple[Chunk, ...]:
        ...


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
    if not locations:
        raise ChunkPolicyError("chunk must preserve at least one source location")
    payload = "\x1f".join(
        (
            source.identity.tenant_id,
            source.identity.document_id,
            source.identity.version,
            source.identity.content_digest,
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


@dataclass(frozen=True)
class FixedSizePolicy:
    width: int

    @property
    def identity(self) -> ChunkPolicyIdentity:
        return ChunkPolicyIdentity("fixed", "1.0.0", (("width", str(self.width)),))

    def chunk(self, source: ParsedSource) -> tuple[Chunk, ...]:
        if self.width <= 0:
            raise ChunkPolicyError("fixed width must be positive")
        text = canonical_block_text(source.blocks)
        if len(text) > MAX_DOCUMENT_CHARS:
            raise ChunkPolicyError("source exceeds bounded chunk policy")
        locations = tuple(block.location for block in source.blocks)
        return tuple(
            make_chunk(
                source,
                self.identity,
                ordinal=offset // self.width,
                text=text[offset : offset + self.width],
                locations=locations,
            )
            for offset in range(0, len(text), self.width)
        )


@dataclass(frozen=True)
class OverlapPolicy:
    width: int
    overlap: int

    @property
    def identity(self) -> ChunkPolicyIdentity:
        return ChunkPolicyIdentity(
            "overlap", "1.0.0", (("width", str(self.width)), ("overlap", str(self.overlap))),
        )

    def chunk(self, source: ParsedSource) -> tuple[Chunk, ...]:
        if self.width <= 0 or not 0 <= self.overlap < self.width:
            raise ChunkPolicyError("require positive width and overlap smaller than width")
        text = canonical_block_text(source.blocks)
        stride = self.width - self.overlap
        locations = tuple(block.location for block in source.blocks)
        return tuple(
            make_chunk(
                source,
                self.identity,
                ordinal=ordinal,
                text=text[offset : offset + self.width],
                locations=locations,
            )
            for ordinal, offset in enumerate(range(0, len(text), stride))
            if text[offset : offset + self.width]
        )
```

Fixed-size chunks are a useful baseline because they are simple, repeatable, and easy to count. Their failure is structural blindness: they can cut a statement, table row, or page transition anywhere. Overlap reduces boundary loss by repeating text, but every repeated span produces more chunks, vectors, storage, potential duplicate results, and opportunity for an evaluation set to count the same evidence twice.

The policy stores locations conservatively in this reference implementation. A production parser should attach a precise range per chunk rather than all document locations. That limitation is visible and testable; it is not hidden as page-level provenance.

**Checkpoint.** Why is overlap a manifest-changing policy rather than a query-time option? It changes the stored chunks themselves. Comparing a no-overlap index with an overlap index is a corpus-policy experiment, not merely a search parameter change.

## 4. Sentence and structure policies preserve different signals

### Orienting question: what boundary is meaningful in P-105?

Sentence-based chunking protects readable prose. It creates chunks from complete sentences until a target width is reached. It can avoid cutting `Net 30 after inspection approval` in half, but it cannot know that P-105’s cross-reference requires both the heading and Schedule A context. Sentence detection itself is format- and language-dependent; a period can be an abbreviation, decimal, item label, or malformed OCR mark.

Structure-aware chunking uses parser blocks. It can attach a heading to its subsequent paragraph and represent a table row with header-aware fields. It is often the more meaningful policy for P-105, but only when parser layout reconstruction is trustworthy enough to identify those blocks. A structure-aware policy with a wrong heading is worse than a transparent fixed baseline.

```python
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


@dataclass(frozen=True)
class SentencePolicy:
    target_width: int

    @property
    def identity(self) -> ChunkPolicyIdentity:
        return ChunkPolicyIdentity("sentence", "1.0.0", (("target_width", str(self.target_width)),))

    def chunk(self, source: ParsedSource) -> tuple[Chunk, ...]:
        if self.target_width <= 0:
            raise ChunkPolicyError("sentence target width must be positive")
        chunks: list[Chunk] = []
        sentences: list[str] = []
        locations: list[SourceLocation] = []
        for block in source.blocks:
            if block.kind != BlockKind.PARAGRAPH:
                continue
            for sentence in SENTENCE_END.split(block.text.strip()):
                candidate = " ".join((*sentences, sentence)).strip()
                if sentences and len(candidate) > self.target_width:
                    chunks.append(
                        make_chunk(
                            source,
                            self.identity,
                            ordinal=len(chunks),
                            text=" ".join(sentences),
                            locations=locations,
                        )
                    )
                    sentences, locations = [sentence], [block.location]
                else:
                    sentences.append(sentence)
                    locations.append(block.location)
        if sentences:
            chunks.append(
                make_chunk(
                    source,
                    self.identity,
                    ordinal=len(chunks),
                    text=" ".join(sentences),
                    locations=locations,
                )
            )
        return tuple(chunks)


@dataclass(frozen=True)
class StructurePolicy:
    include_heading: bool = True

    @property
    def identity(self) -> ChunkPolicyIdentity:
        return ChunkPolicyIdentity(
            "structure", "1.0.0", (("include_heading", str(self.include_heading)),),
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

The sentence regex is a deterministic illustrative splitter, not a general language parser. The structure policy keeps each table row as a separate block and inherits its heading, but it does not create a table parser. A real table policy should keep table header, row, column, page, parser confidence, and original coordinates; it should reject ambiguous field mapping rather than make column order look reliable.

## 5. Semantic chunking changes the boundary algorithm, not the truth model

### Orienting question: can local similarity decide where a topic ends?

Semantic chunking evaluates the relationship between neighbouring units—often sentences or paragraphs—and starts a new chunk when similarity falls below a threshold. It can group topic-consistent prose better than a fixed window, but it adds a model, metric, threshold, preprocessing, language, and evaluation boundary.

It can also fail precisely where procurement documents are most consequential. Schedule A and Section 3 may be linguistically different while contractually related. A local similarity threshold can split their relationship; a repeated boilerplate clause can look similar while applying to another supplier or version.

Use an injected boundary, not an invisible model call. This deterministic example measures shared lower-case terms only. It exists to make the policy/testable threshold contract visible; it does not measure semantic quality or stand in for a real local embedding model.

```python
class AdjacentSimilarity(Protocol):
    @property
    def identity(self) -> str:
        ...

    def score(self, left: str, right: str) -> float:
        ...


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
            "1.0.0",
            (
                ("similarity", self.similarity.identity),
                ("threshold", str(self.threshold)),
            ),
        )

    def chunk(self, source: ParsedSource) -> tuple[Chunk, ...]:
        if not 0.0 <= self.threshold <= 1.0:
            raise ChunkPolicyError("semantic threshold must be in [0, 1]")
        paragraphs = [block for block in source.blocks if block.kind == BlockKind.PARAGRAPH]
        if not paragraphs:
            return ()
        groups: list[list[ParsedBlock]] = [[paragraphs[0]]]
        for block in paragraphs[1:]:
            previous = groups[-1][-1]
            if self.similarity.score(previous.text, block.text) < self.threshold:
                groups.append([block])
            else:
                groups[-1].append(block)
        return tuple(
            make_chunk(
                source,
                self.identity,
                ordinal=ordinal,
                text=" ".join(block.text for block in group),
                locations=[block.location for block in group],
            )
            for ordinal, group in enumerate(groups)
        )
```

A real local embedding adapter should record model/artifact digest, runtime, query/document or boundary instruction, dimension, normalization, metric, and threshold. A changed threshold is a different policy; a changed model is a different policy even with the same threshold. Evaluate both against fixed and structure-aware policies on the same frozen source snapshot.

## 6. Parent-child retrieval separates matching from readable context

### Orienting question: how can a small match return sufficient evidence?

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
            "parent-child", "1.0.0", (("child_unit", "parsed_block"),),
        )

    def chunk(self, source: ParsedSource) -> tuple[Chunk, ...]:
        parent_chunks: list[Chunk] = []
        child_chunks: list[Chunk] = []
        heading: ParsedBlock | None = None
        section_blocks: list[ParsedBlock] = []

        def flush_section() -> None:
            if not section_blocks:
                return
            parent_heading = heading.text if heading else source.title
            parent_locations = [block.location for block in section_blocks]
            if heading:
                parent_locations.insert(0, heading.location)
            parent = make_chunk(
                source,
                self.identity,
                ordinal=len(parent_chunks),
                text="\n".join((parent_heading, *(block.text for block in section_blocks))),
                locations=parent_locations,
            )
            parent_chunks.append(parent)
            for block in section_blocks:
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

### Orienting question: what makes a chunk collection reproducible?

The same document under a different parser, policy, parameter, or source version is a different retrieval corpus. A manifest records what was built. It does not grant access and it does not replace source records.

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


@dataclass(frozen=True)
class ChunkCollection:
    manifest: ChunkManifest
    chunks: tuple[Chunk, ...]

    @classmethod
    def build(
        cls,
        source: ParsedSource,
        policy: ChunkPolicy,
        *,
        created_at: datetime,
    ) -> Self:
        if created_at.tzinfo is None:
            raise ValueError("manifest time must be timezone-aware")
        if source.identity.content_digest != digest_text(canonical_block_text(source.blocks)):
            raise ManifestCompatibilityError("source digest does not match parsed blocks")
        chunks = policy.chunk(source)
        if not chunks:
            raise ChunkPolicyError("accepted source produced no chunks")
        if any(chunk.source_identity != source.identity for chunk in chunks):
            raise ManifestCompatibilityError("chunk source identity differs from collection source")
        if any(chunk.policy_fingerprint != policy.identity.fingerprint() for chunk in chunks):
            raise ManifestCompatibilityError("chunk policy differs from collection policy")
        manifest = ChunkManifest(
            schema_version=CHUNK_MANIFEST_SCHEMA,
            parser_id=source.parser_id,
            parser_version=source.parser_version,
            policy_fingerprint=policy.identity.fingerprint(),
            source_digest=source.identity.content_digest,
            chunk_count=len(chunks),
            created_at=created_at.astimezone(UTC),
        )
        return cls(manifest=manifest, chunks=chunks)


class ChunkAccessPolicy(Protocol):
    def can_read(self, principal_id: str, chunk: Chunk) -> bool:
        ...


@dataclass(frozen=True)
class StaticChunkAccessPolicy:
    permitted: frozenset[tuple[str, str, str, str]]

    def can_read(self, principal_id: str, chunk: Chunk) -> bool:
        source = chunk.source_identity
        return (principal_id, source.tenant_id, source.document_id, source.version) in self.permitted


def authorized_chunks(
    principal_id: str,
    chunks: Iterable[Chunk],
    access_policy: ChunkAccessPolicy,
) -> tuple[Chunk, ...]:
    if not principal_id.strip():
        raise ValueError("principal ID must be non-empty")
    return tuple(chunk for chunk in chunks if access_policy.can_read(principal_id, chunk))
```

Authorization must constrain candidate selection before retrieval scores are computed. Filtering after a vector search can leak whether an unauthorized document exists through result count, timing, score, or cache behavior. This local reference therefore exposes `authorized_chunks` as the only collection a downstream retrieval caller should receive.

Operationally, build a new manifest when the parser, OCR engine, raw-source snapshot, metadata policy, chunk policy, tokenizer accounting, or local embedding configuration changes. Promote an immutable manifest only after tests and held-out evaluation; rollback means selecting a prior approved manifest/source snapshot, not mutating chunks in place. Rebuilds should be idempotent for the same source and configuration.

## 8. Compare policies fairly: retrieval, cost, and support completeness

### Orienting question: how do we compare chunks without choosing a favorite example?

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
    policy = collection[0].manifest.policy_fingerprint
    if any(item.manifest.policy_fingerprint != policy for item in collection):
        raise ManifestCompatibilityError("comparison collection must use one policy")
    source_digest = digest_text("\n".join(sorted(item.manifest.source_digest for item in collection)))
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

The illustrative metric table contains no measured values. That is intentional. A production measurement must state its corpus snapshot, parser/OCR version, policy identity, local model/index identity, authorization filter, query split, label version, hardware, and latency boundary. One policy may improve Recall@5 while creating duplicate chunks, reducing Precision@5, increasing storage, or failing on OCR/table subgroups.

### A reasonable evaluation procedure

1. Build a governed development set and a held-out set. Split near-duplicate agreements and amendments by source family or time so copied text cannot leak across splits.
2. Define direct relevance, partial relevance, non-relevance, and support atoms before inspecting rankings. Retain label disagreement/adjudication rather than hiding it in one number.
3. Run fixed, overlap, sentence, semantic, structure-aware, and parent-child policies on the same source snapshot. Freeze local embedding, metric, top-k, filtering, and retrieval implementation.
4. Measure retrieval metrics, chunk count, average length, storage, index build time, query latency, duplicate rate, and support completeness. Stratify by document type, table/OCR condition, language, amendment/version, and query type.
5. Inspect false positives and false negatives with authorized reviewers. Promote only a policy with acceptable quality, security, cost, and failure behavior; retain an exact rollback manifest.

## 9. Cumulative fixtures and tests make failure visible

### Orienting question: which chunking claims can deterministic tests prove?

The following fixture creates P-101 through P-105. It verifies parser failure, no silent truncation, overlap constraints, stable IDs, version isolation, parent-child lineage, authorization, and that several policies receive the same source collection. It does not prove that a local semantic model retrieves well.

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

## 13. Exercises

1. Add P-106 as a scanned invoice with an OCR-confused character. Define parser status, review route, and a test that prevents an uncertain price from becoming accepted table metadata.
2. Add P-105 version 2 with a changed payment clause. Verify old and new chunks have different identity/digests and write an authorization/filter rule that chooses the allowed active version.
3. Make the fixed policy preserve precise character ranges instead of the conservative all-block location tuple. Add tests for first/last boundary mapping.
4. Create five held-out queries that distinguish a fixed-boundary failure, a heading dependency, a table-header dependency, an amendment conflict, and a cross-tenant denial.
5. Design a semantic-policy experiment with a real approved local adapter. State its model manifest, threshold grid, development/held-out split, failure metrics, and rollback condition before running it.

## Primary documentation

- [Python 3.13 `dataclasses`](https://docs.python.org/3.13/library/dataclasses.html)
- [Python 3.13 `typing` and `Protocol`](https://docs.python.org/3.13/library/typing.html)
- [Python 3.13 `hashlib`](https://docs.python.org/3.13/library/hashlib.html)
