"""Exact local retrieval baseline for Week 5; no orchestration framework."""

from __future__ import annotations


from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from math import fsum, hypot, isfinite
from re import fullmatch
from typing import Protocol, Self


Vector = tuple[float, ...]
MAX_DOCUMENT_CHARS = 1_000
MAX_TITLE_CHARS = 200
INDEX_SCHEMA_VERSION = "procurement-semantic-index/1.1.0"
SOURCE_ID_PATTERN = r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}"


class RetrievalError(Exception):
    """Base class for explicit semantic-retrieval boundary failures."""


class DocumentRejectedError(RetrievalError):
    """Raised when untrusted source text violates the bounded loader contract."""


class VectorInvariantError(RetrievalError):
    """Raised when a vector cannot satisfy the metric/index contract."""


class IndexCompatibilityError(RetrievalError):
    """Raised when an adapter cannot safely query an existing index."""


class EmbeddingRuntimeError(RetrievalError):
    """Raised when a local embedding runtime has no usable response."""


def digest_text(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def validate_vector(vector: Vector) -> None:
    if not vector:
        raise VectorInvariantError("vectors must be non-empty")
    if any(type(value) not in (int, float) or not isfinite(value) for value in vector):
        raise VectorInvariantError("vectors must contain only finite values")


def l2_norm(vector: Vector) -> float:
    validate_vector(vector)
    length = hypot(*vector)
    if not isfinite(length):
        raise VectorInvariantError("vector norm exceeds finite range")
    return length


def dot_product(left: Vector, right: Vector) -> float:
    validate_vector(left)
    validate_vector(right)
    if len(left) != len(right):
        raise VectorInvariantError("vectors must have matching dimensions")
    try:
        value = fsum(a * b for a, b in zip(left, right, strict=True))
    except (OverflowError, ValueError) as exc:
        raise VectorInvariantError("dot product exceeds finite range") from exc
    if not isfinite(value):
        raise VectorInvariantError("dot product exceeds finite range")
    return value


def euclidean_distance(left: Vector, right: Vector) -> float:
    validate_vector(left)
    validate_vector(right)
    if len(left) != len(right):
        raise VectorInvariantError("vectors must have matching dimensions")
    distance = hypot(*(a - b for a, b in zip(left, right, strict=True)))
    if not isfinite(distance):
        raise VectorInvariantError("distance exceeds finite range")
    return distance


def normalize(vector: Vector) -> Vector:
    validate_vector(vector)
    scale = max(abs(value) for value in vector)
    if scale == 0.0:
        raise VectorInvariantError("cannot normalize a zero vector")
    scaled = tuple(value / scale for value in vector)
    length = hypot(*scaled)
    return tuple(value / length for value in scaled)


def cosine_similarity(left: Vector, right: Vector) -> float:
    # Normalize before multiplying to avoid overflow/underflow in norm products.
    value = dot_product(normalize(left), normalize(right))
    return max(-1.0, min(1.0, value))


@dataclass(frozen=True)
class UntrustedDocument:
    tenant_id: str
    document_id: str
    document_version: str
    title: str
    text: str


@dataclass(frozen=True)
class SourceDocument:
    tenant_id: str
    document_id: str
    document_version: str
    title: str
    text: str
    content_digest: str


@dataclass(frozen=True)
class SourceChunk:
    chunk_id: str
    tenant_id: str
    document_id: str
    document_version: str
    text: str
    content_digest: str


def load_documents(records: Iterable[UntrustedDocument]) -> tuple[SourceDocument, ...]:
    loaded: list[SourceDocument] = []
    seen: set[tuple[str, str, str]] = set()
    for record in records:
        identity = (record.tenant_id, record.document_id, record.document_version)
        if any(
            not isinstance(part, str) or fullmatch(SOURCE_ID_PATTERN, part) is None
            for part in identity
        ):
            raise DocumentRejectedError(
                "tenant, document ID, and version must use the source-ID format"
            )
        if identity in seen:
            raise DocumentRejectedError("document identity must be unique")
        if not isinstance(record.title, str) or not isinstance(record.text, str):
            raise DocumentRejectedError("title and text must be strings")
        if not record.title.strip() or not record.text.strip():
            raise DocumentRejectedError("title and text must be non-empty")
        if len(record.title) > MAX_TITLE_CHARS:
            raise DocumentRejectedError("document title exceeds the bounded policy")
        if len(record.text) > MAX_DOCUMENT_CHARS:
            raise DocumentRejectedError("document exceeds the initial bounded policy")
        try:
            record.title.encode("utf-8")
            record.text.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise DocumentRejectedError("source must be valid UTF-8 text") from exc
        seen.add(identity)
        loaded.append(
            SourceDocument(
                tenant_id=record.tenant_id,
                document_id=record.document_id,
                document_version=record.document_version,
                title=record.title,
                text=record.text,
                content_digest=digest_text(record.text),
            )
        )
    return tuple(loaded)


def initial_chunks(documents: Iterable[SourceDocument]) -> tuple[SourceChunk, ...]:
    """Make one traceable chunk from each already-short accepted document."""
    return tuple(
        SourceChunk(
            chunk_id=(
                f"{document.tenant_id}:{document.document_id}:"
                f"{document.document_version}:0"
            ),
            tenant_id=document.tenant_id,
            document_id=document.document_id,
            document_version=document.document_version,
            text=document.text,
            content_digest=document.content_digest,
        )
        for document in documents
    )


@dataclass(frozen=True)
class EmbeddingModelIdentity:
    model_id: str
    artifact_digest: str
    runtime_version: str
    preprocessing_version: str
    dimension: int
    metric: str
    asymmetric: bool

    def __post_init__(self) -> None:
        text_fields = (
            self.model_id,
            self.artifact_digest,
            self.runtime_version,
            self.preprocessing_version,
            self.metric,
        )
        if not all(value.strip() for value in text_fields):
            raise ValueError("embedding identity fields must be non-empty")
        if type(self.dimension) is not int or self.dimension < 1:
            raise ValueError("embedding dimension must be positive")

    def fingerprint(self) -> str:
        fields = (
            self.model_id,
            self.artifact_digest,
            self.runtime_version,
            self.preprocessing_version,
            str(self.dimension),
            self.metric,
            str(self.asymmetric),
        )
        return digest_text("\x1f".join(fields))


class LocalEmbeddingAdapter(Protocol):
    """Local-only embedding boundary; implementations must expose stable identity."""

    @property
    def identity(self) -> EmbeddingModelIdentity: ...

    def embed_documents(self, texts: Sequence[str]) -> tuple[Vector, ...]: ...

    def embed_queries(self, texts: Sequence[str]) -> tuple[Vector, ...]: ...


@dataclass(frozen=True)
class DemoLocalEmbeddingAdapter:
    """Teaching fake, not a semantic model or a quality measurement."""

    identity: EmbeddingModelIdentity = EmbeddingModelIdentity(
        model_id="demo-procurement-features",
        artifact_digest="synthetic-only",
        runtime_version="none",
        preprocessing_version="lower-punctuation-hyphen-split/v2",
        dimension=5,
        metric="cosine",
        asymmetric=True,
    )

    def _vector(self, text: str, *, query_mode: bool) -> Vector:
        normalized = (
            text.lower().replace("-", " ").translate(str.maketrans("", "", ".,?!:;"))
        )
        terms = set(normalized.split())
        payment = bool(terms & {"payment", "invoice", "due"})
        approval = bool(terms & {"approval", "approve", "sign", "signs", "off"})
        inspection = bool(terms & {"inspection", "quality", "receiving"})
        products = bool(terms & {"copper", "wire", "bolts", "pellets"})
        query_intent = query_mode and bool(terms & {"which", "require", "required"})
        return tuple(
            float(value)
            for value in (payment, approval, inspection, products, query_intent)
        )

    def embed_documents(self, texts: Sequence[str]) -> tuple[Vector, ...]:
        return tuple(self._vector(text, query_mode=False) for text in texts)

    def embed_queries(self, texts: Sequence[str]) -> tuple[Vector, ...]:
        return tuple(self._vector(text, query_mode=True) for text in texts)


@dataclass(frozen=True)
class IndexedVector:
    source: SourceChunk
    vector: Vector
    model_fingerprint: str


@dataclass(frozen=True)
class IndexManifest:
    schema_version: str
    index_id: str
    created_at: datetime
    chunk_policy: str
    metric: str
    dimension: int
    model_fingerprint: str
    corpus_digest: str
    vector_count: int


@dataclass(frozen=True)
class SearchRequest:
    principal_id: str
    query_text: str
    top_k: int


@dataclass(frozen=True)
class RetrievalProvenance:
    index_id: str
    model_fingerprint: str
    metric: str
    source_digest: str
    document_version: str


@dataclass(frozen=True)
class SearchResult:
    rank: int
    score: float
    source: SourceChunk
    provenance: RetrievalProvenance


class AccessPolicy(Protocol):
    def can_read(self, principal_id: str, source: SourceChunk) -> bool: ...


@dataclass(frozen=True)
class StaticObjectAccessPolicy:
    """Deterministic test policy; production policy belongs at the identity boundary."""

    permitted: frozenset[tuple[str, str, str, str]]

    def can_read(self, principal_id: str, source: SourceChunk) -> bool:
        return (
            principal_id,
            source.tenant_id,
            source.document_id,
            source.document_version,
        ) in self.permitted


def corpus_digest(chunks: Sequence[SourceChunk]) -> str:
    ordered = sorted(f"{chunk.chunk_id}\x1f{chunk.content_digest}" for chunk in chunks)
    return digest_text("\n".join(ordered))


def logical_index_id(
    *,
    schema_version: str,
    model_fingerprint: str,
    corpus_fingerprint: str,
    chunk_policy: str,
) -> str:
    return digest_text(
        "\x1f".join(
            (schema_version, model_fingerprint, corpus_fingerprint, chunk_policy)
        )
    )


@dataclass(frozen=True)
class InMemoryCosineIndex:
    manifest: IndexManifest
    entries: tuple[IndexedVector, ...]

    def __post_init__(self) -> None:
        if self.manifest.schema_version != INDEX_SCHEMA_VERSION:
            raise IndexCompatibilityError("index schema version is unsupported")
        if self.manifest.vector_count < 1 or self.manifest.dimension < 1:
            raise VectorInvariantError("manifest needs positive count and dimension")
        if self.manifest.metric != "cosine":
            raise IndexCompatibilityError("index manifest must declare cosine")
        if self.manifest.created_at.tzinfo is None:
            raise VectorInvariantError("manifest build time must be timezone-aware")
        if self.manifest.vector_count != len(self.entries):
            raise VectorInvariantError("manifest vector count differs from entries")
        chunk_ids = [entry.source.chunk_id for entry in self.entries]
        if len(chunk_ids) != len(set(chunk_ids)):
            raise VectorInvariantError("index contains duplicate chunk IDs")
        for entry in self.entries:
            if entry.source.content_digest != digest_text(entry.source.text):
                raise IndexCompatibilityError(
                    "stored source text differs from its digest"
                )
            if len(entry.vector) != self.manifest.dimension:
                raise VectorInvariantError(
                    "stored vector dimension differs from manifest"
                )
            if abs(l2_norm(entry.vector) - 1.0) > 1e-12:
                raise VectorInvariantError("stored vector must be L2-normalized")
            if entry.model_fingerprint != self.manifest.model_fingerprint:
                raise IndexCompatibilityError(
                    "stored vector model differs from manifest"
                )
        observed_corpus_digest = corpus_digest([entry.source for entry in self.entries])
        if observed_corpus_digest != self.manifest.corpus_digest:
            raise IndexCompatibilityError("stored corpus differs from manifest")
        observed_index_id = logical_index_id(
            schema_version=self.manifest.schema_version,
            model_fingerprint=self.manifest.model_fingerprint,
            corpus_fingerprint=self.manifest.corpus_digest,
            chunk_policy=self.manifest.chunk_policy,
        )
        if observed_index_id != self.manifest.index_id:
            raise IndexCompatibilityError("logical index ID differs from manifest")

    @classmethod
    def build(
        cls,
        chunks: Sequence[SourceChunk],
        adapter: LocalEmbeddingAdapter,
        *,
        created_at: datetime,
    ) -> Self:
        if not chunks:
            raise VectorInvariantError("an index needs at least one source chunk")
        if created_at.tzinfo is None:
            raise ValueError("index build time must be timezone-aware")
        if adapter.identity.metric != "cosine":
            raise IndexCompatibilityError("baseline index requires cosine metric")
        identity = adapter.identity
        document_vectors = adapter.embed_documents([chunk.text for chunk in chunks])
        if adapter.identity != identity:
            raise IndexCompatibilityError("embedding identity changed during build")
        if len(document_vectors) != len(chunks):
            raise EmbeddingRuntimeError("adapter must return one vector per document")
        entries: list[IndexedVector] = []
        for chunk, raw_vector in zip(chunks, document_vectors, strict=True):
            if len(raw_vector) != identity.dimension:
                raise VectorInvariantError(
                    "adapter returned an unexpected document dimension"
                )
            entries.append(
                IndexedVector(
                    source=chunk,
                    vector=normalize(raw_vector),
                    model_fingerprint=identity.fingerprint(),
                )
            )
        ordered_entries = tuple(
            sorted(entries, key=lambda entry: entry.source.chunk_id)
        )
        corpus_fingerprint = corpus_digest([entry.source for entry in ordered_entries])
        index_id = logical_index_id(
            schema_version=INDEX_SCHEMA_VERSION,
            model_fingerprint=identity.fingerprint(),
            corpus_fingerprint=corpus_fingerprint,
            chunk_policy="one-short-document-one-chunk/v1",
        )
        manifest = IndexManifest(
            schema_version=INDEX_SCHEMA_VERSION,
            index_id=index_id,
            created_at=created_at.astimezone(UTC),
            chunk_policy="one-short-document-one-chunk/v1",
            metric="cosine",
            dimension=identity.dimension,
            model_fingerprint=identity.fingerprint(),
            corpus_digest=corpus_fingerprint,
            vector_count=len(ordered_entries),
        )
        return cls(manifest=manifest, entries=ordered_entries)

    def _validate_query_adapter(self, adapter: LocalEmbeddingAdapter) -> None:
        if adapter.identity.metric != self.manifest.metric:
            raise IndexCompatibilityError("query metric differs from index metric")
        if adapter.identity.dimension != self.manifest.dimension:
            raise IndexCompatibilityError(
                "query dimension differs from index dimension"
            )
        if adapter.identity.fingerprint() != self.manifest.model_fingerprint:
            raise IndexCompatibilityError(
                "query adapter differs from index model contract"
            )

    def search(
        self,
        request: SearchRequest,
        *,
        adapter: LocalEmbeddingAdapter,
        access_policy: AccessPolicy,
    ) -> tuple[SearchResult, ...]:
        if not isinstance(request.principal_id, str) or not isinstance(
            request.query_text, str
        ):
            raise ValueError("principal and query text must be strings")
        if not request.principal_id.strip() or not request.query_text.strip():
            raise ValueError("principal and query text must be non-empty")
        if len(request.query_text) > MAX_DOCUMENT_CHARS:
            raise ValueError("query exceeds the bounded text policy")
        try:
            request.query_text.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise ValueError("query must be valid UTF-8 text") from exc
        if type(request.top_k) is not int or request.top_k < 1:
            raise ValueError("top_k must be an integer")
        self._validate_query_adapter(adapter)
        authorised = tuple(
            entry
            for entry in self.entries
            if access_policy.can_read(request.principal_id, entry.source)
        )
        if not authorised:
            return ()
        if not 1 <= request.top_k <= len(authorised):
            raise ValueError("top_k must fit the authorised candidate set")
        identity = adapter.identity
        query_vectors = adapter.embed_queries([request.query_text])
        if adapter.identity != identity:
            raise IndexCompatibilityError("embedding identity changed during query")
        if len(query_vectors) != 1:
            raise EmbeddingRuntimeError("adapter must return exactly one query vector")
        query_vector = query_vectors[0]
        if len(query_vector) != self.manifest.dimension:
            raise VectorInvariantError("adapter returned an unexpected query dimension")
        normalized_query = normalize(query_vector)
        ranked = sorted(
            (
                (cosine_similarity(normalized_query, entry.vector), entry)
                for entry in authorised
            ),
            key=lambda scored: (-scored[0], scored[1].source.chunk_id),
        )
        return tuple(
            SearchResult(
                rank=rank,
                score=score,
                source=entry.source,
                provenance=RetrievalProvenance(
                    index_id=self.manifest.index_id,
                    model_fingerprint=self.manifest.model_fingerprint,
                    metric=self.manifest.metric,
                    source_digest=entry.source.content_digest,
                    document_version=entry.source.document_version,
                ),
            )
            for rank, (score, entry) in enumerate(ranked[: request.top_k], start=1)
        )
