"""Versioned parsing/chunk policies for controlled Week 6 fixtures."""

from __future__ import annotations


from collections.abc import Iterable, Sequence
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
