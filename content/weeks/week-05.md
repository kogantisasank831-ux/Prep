---
layout: week
permalink: /weeks/week-05/
title: "Embeddings and vector retrieval: build a defensible local search boundary"
description: Build a typed, local-only semantic-search baseline that protects document access, preserves vector provenance, and measures retrieval rather than mistaking similarity for truth.
summary: Follow P-101 through P-104 from bounded procurement documents to an authorization-filtered exact cosine index, a versioned manifest, and a controlled evaluation of retrieval quality and ANN trade-offs.
kicker_primary: Embeddings and vector retrieval
kicker_secondary: Retrieval evidence before interpretation
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-05/beginner/
---

## Four documents, one retrieval boundary

Week 4 turned a purchase confirmation into a typed candidate and required visible document evidence before accepting any extracted field. That discipline continues here. Retrieval does not answer a procurement question; it selects source passages that may be worth reading.

The synthetic corpus remains deliberately small:

```text
P-101 | Atlas Metals purchase confirmation
Tenant: northwind-procurement
Copper wire will ship after incoming-material inspection.
Invoice terms: Net 30 after inspection approval.

P-102 | Beacon Plastics purchase confirmation
Tenant: northwind-procurement
Polymer pellets will ship on 2026-09-03.
Invoice terms: Net 15 from receipt.

P-103 | Atlas Metals delivery update
Tenant: northwind-procurement
The copper-wire shipment is delayed by two days while quality checks finish.

P-104 | Cedar Fasteners payment note
Tenant: northwind-procurement
Payment is due after the receiving team signs off on the delivered bolts.
```

An authorised analyst asks:

> Which supplier documents state that approval or sign-off is required before payment?

The expected candidates are P-101 and P-104. P-103 is related to inspection and quality, but it does not state a payment condition. P-102 mentions invoice terms, but not approval. A system that returns P-103 above either expected record is not merely “a little vague”: it has failed the declared retrieval intent.

The goal is a narrow semantic-search service with these properties:

```text
untrusted sensitive documents
        |
        v
bounded, immutable source records -----> versioned local embedding boundary
        |                                         |
        v                                         v
tenant/object authorisation ------------> immutable vectors + manifest
                                                  |
authorised query -------------------------------> exact ranked candidates
                                                  |
                                                  v
                                  source text + score + provenance for review
```

No component generates an answer, writes to a procurement system, approves payment, executes a tool, or broadens a caller’s access. A vector and a score are derived data, not a business decision. The original documents, vectors, query text, and result metadata may all be sensitive; do not treat numeric representation as de-identification.

### What this lesson proves, and what it does not

The code below proves deterministic behavior of its contracts on a synthetic corpus. It proves that a denied object is excluded before scoring, that an incompatible embedder is refused, that ranking ties resolve predictably, and that the exact index returns the expected synthetic candidates. It does **not** prove that a toy embedder understands procurement language, that a chosen local model is safe or licensed, or that a high cosine score establishes a contractual fact.

The scope stops at retrieval. Detailed long-document splitting is deferred to Week 6. This system returns only selected source records; it has no generated answer, external service, database infrastructure, or capability invocation.

**Checkpoint.** If P-104 is retrieved, what may the caller conclude? Only that the stored P-104 text is a candidate relevant to the query under this model, metric, and index. The caller must inspect its text, identity, active version, and business context before asserting a payment rule.

## 1. Semantic embeddings are model outputs, not facts

### Orienting question: what has changed when text becomes a vector?

An **embedding** is a fixed-width vector of numbers produced for text by an embedding model. The model is trained so that texts used in related contexts often occupy useful nearby positions under a chosen metric. It is a representation optimized for a task family, not an explanation of text and not a live lookup into the source system.

For intuition only, imagine:

```text
"invoice terms after inspection approval"
    -> [0.64, -0.12, 0.48, 0.09, ...]

"receiving signs off before payment"
    -> [0.61, -0.08, 0.52, 0.14, ...]
```

Meaning is distributed across dimensions. It is usually wrong to label one coordinate “approval” and another “payment.” A model may place the two sentences near each other because it learned broad co-occurrence and semantic patterns, while still missing negation, a supplier identifier, a date, or the direction of a condition.

Embeddings are distinct from three nearby concepts:

| Object | Role | Why it is not this retrieval vector |
| --- | --- | --- |
| Token ID | integer name from a tokenizer vocabulary | an ID has no geometric meaning by itself |
| Token embedding | initial vector for one token inside a neural model | it represents a token before broader text representation is formed |
| Generative model hidden state | context-dependent intermediate computation | it is not automatically a stable retrieval API or metric contract |
| Retrieval embedding | exposed vector for a query or document | it is designed and evaluated for comparison/ranking |

Treat any embedding as untrusted model output. It is derived from untrusted text, can leak corpus membership or sensitive semantic content, and can be corrupted by an adapter fault or configuration mismatch. Store it only under the same tenant and retention controls as the source. Do not let a client submit arbitrary vectors into a shared index, and never accept a caller-supplied tenant or document identifier as authorization.

**Bridge.** A vector is useful only relative to the model convention that produced it. Query/document roles make that convention explicit.

## 2. Query and document representations may be asymmetric

### Orienting question: why not call one `embed(text)` method everywhere?

In a symmetric similarity task, both inputs play the same role: “Are these two sentences related?” A single representation function can be appropriate. Retrieval has different roles. A short analyst query asks for evidence; a document or passage supplies evidence. An embedding model may be trained with distinct query and document encoders, or with role-specific prefixes/instructions, to make this asymmetric relation useful.

```text
query:    "approval before payment"
                 |
             query encoder
                 v
              q vector

P-104: "Payment is due after the receiving team signs off..."
                 |
           document encoder
                 v
              d vector

                    compare(q, d) -> ranking score
```

An API that exposes `embed_queries` and `embed_documents` prevents an easy configuration error: accidentally applying document preprocessing to a query, or treating a retrieval model’s required query instruction as optional prose. The two functions may delegate to the same local runtime, but their difference remains part of the declared model contract.

The corpus is embedded ahead of time. A query is embedded at search time. A model/runtime replacement, template change, normalization policy change, or document preprocessing change means the old vectors are no longer necessarily comparable. Version the whole configuration and rebuild rather than silently mixing generations of vectors.

### Dimensionality is a contract and a cost

The count of scalar values is the embedding **dimensionality**. A 384-dimensional vector has 384 positions; a 1,024-dimensional vector has 1,024. Higher dimension can provide model capacity, but is not a quality certificate. Quality depends on training, supported languages, corpus, query style, relevance policy, and evaluation evidence.

At a simple level, storing `N` vectors of dimension `D` requires storage proportional to `N × D`. A `float32` value occupies four bytes before metadata or index overhead. Ten million 768-dimensional vectors therefore require roughly 28.6 GiB for vector values alone (`10,000,000 × 768 × 4 / 2^30`), not counting source text, metadata, copies, or index structures. Exact brute-force comparison also performs work proportional to `N × D` per query.

That arithmetic explains why dimension affects storage, memory bandwidth, latency, hardware fit, and rebuild cost. It does not say “fewer dimensions are better.” Select a dimension/model pair from held-out retrieval evidence and operational budget, then pin it in the manifest.

**Checkpoint.** Can a 768-dimensional query be compared with a 384-dimensional document vector? No. The operation is undefined. A dimension match is necessary, but it is not enough: two unrelated models can emit the same width.

## 3. Similarity metrics encode different geometry

### Orienting question: what exactly does a score compare?

Let `a` and `b` be equal-length vectors. Three common comparisons are worth keeping separate.

The **dot product** is:

```text
dot(a, b) = sum(a[i] * b[i])
```

It grows when components align, and it also depends on vector magnitude. If a model encodes useful confidence or frequency in magnitude, dot product may be its intended metric. If magnitude is an accidental preprocessing artifact, dot product can over-rank long vectors.

**Euclidean distance** is straight-line distance:

```text
distance(a, b) = sqrt(sum((a[i] - b[i])^2))
```

Smaller distance means closer vectors. It is sensitive to both direction and magnitude. A search API must state whether a larger score is better or a smaller distance is better; mixing that ordering is a common and damaging bug.

**Cosine similarity** compares direction:

```text
cosine(a, b) = dot(a, b) / (norm(a) * norm(b))
norm(a) = sqrt(sum(a[i]^2))
```

For non-zero vectors, cosine is between -1 and 1. With non-negative toy vectors it lies between 0 and 1. It is not a probability, confidence score, legal relevance score, or factuality measurement. Its meaningful ranges are model- and corpus-dependent.

Consider `q = [1, 1]` and `d = [2, 0]`:

```text
dot(q, d)       = 2
norm(q)         = sqrt(2)
norm(d)         = 2
cosine(q, d)    = 2 / (2 * sqrt(2)) ~= 0.707
euclidean(q, d) = sqrt((1 - 2)^2 + (1 - 0)^2) = sqrt(2)
```

Now compare `q` with `[10, 10]`. Its dot product is much larger, Euclidean distance is large, but cosine similarity is `1.0`: the two vectors point in the same direction. This illustrates why metric selection and vector normalization must match the embedding model’s documented convention.

### Normalization changes the contract

**L2 normalization** scales a non-zero vector so its Euclidean norm is one:

```text
normalize(a) = a / norm(a)
```

For normalized vectors, cosine similarity equals the dot product. The equality is useful for speed and index compatibility, but only because normalization is an explicit invariant. If an index expects unit vectors and receives raw vectors, its dot-product ranking no longer means cosine ranking.

The baseline below stores normalized vectors and still calls `cosine_similarity` for clarity. It rejects zero vectors instead of inventing a score. A real adapter must document whether it already normalizes vectors. Applying normalization twice is mathematically harmless for non-zero vectors but can obscure provenance; omitting required normalization changes rankings.

**Checkpoint.** If cosine similarity is `0.91`, is the returned clause 91% true? No. The score records geometric alignment under one model and metric. Truth requires source review and domain validation.

## 4. State retrieval invariants before starting a local model

### Orienting question: what must be impossible rather than merely discouraged?

The service has six non-negotiable invariants:

1. An indexed source record has a non-empty tenant, immutable document ID/version, bounded text, and SHA-256 content digest.
2. Initial chunking makes exactly one chunk from one already-short document. It never silently truncates or splits a longer document.
3. Every stored vector is non-zero, normalized, and has the manifest dimension.
4. Every vector was produced under the exact model identity and preprocessing contract in the manifest.
5. Authorization determines the candidate set before a score is computed. Ranking an object and filtering it afterward can leak existence, scores, or timing.
6. Equal scores sort by stable `chunk_id`, not insertion order or runtime luck.

These are small but consequential contracts. They make a failure explicit at the right boundary rather than producing a plausible result after an incompatible rebuild or unauthorised search.

The Python 3.13 baseline uses only the standard library. It models a local adapter with a `Protocol`; an actual approved local runtime belongs behind that protocol. No lesson code downloads a model, starts a server, or sends a document over the network.

```python
from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from hashlib import sha256
from math import isfinite, sqrt
from re import fullmatch
from typing import Protocol, Self


Vector = tuple[float, ...]
MAX_DOCUMENT_CHARS = 1_000
MAX_TITLE_CHARS = 200
INDEX_SCHEMA_VERSION = "procurement-semantic-index/1.0.0"
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
    if any(not isfinite(value) for value in vector):
        raise VectorInvariantError("vectors must contain only finite values")


def l2_norm(vector: Vector) -> float:
    validate_vector(vector)
    return sqrt(sum(value * value for value in vector))


def dot_product(left: Vector, right: Vector) -> float:
    validate_vector(left)
    validate_vector(right)
    if len(left) != len(right):
        raise VectorInvariantError("vectors must have matching dimensions")
    return sum(a * b for a, b in zip(left, right, strict=True))


def euclidean_distance(left: Vector, right: Vector) -> float:
    validate_vector(left)
    validate_vector(right)
    if len(left) != len(right):
        raise VectorInvariantError("vectors must have matching dimensions")
    return sqrt(sum((a - b) ** 2 for a, b in zip(left, right, strict=True)))


def normalize(vector: Vector) -> Vector:
    length = l2_norm(vector)
    if length == 0.0:
        raise VectorInvariantError("cannot normalize a zero vector")
    return tuple(value / length for value in vector)


def cosine_similarity(left: Vector, right: Vector) -> float:
    left_length = l2_norm(left)
    right_length = l2_norm(right)
    if left_length == 0.0 or right_length == 0.0:
        raise VectorInvariantError("cosine similarity is undefined for zero vectors")
    return dot_product(left, right) / (left_length * right_length)
```

The functions are pure and testable. Empty vectors and non-finite values such as `NaN` or infinity are rejected before they can undermine norm and ordering checks. `VectorInvariantError` deliberately distinguishes an invalid vector from a document loader failure or a runtime failure. Callers can expose a safe operational status without suppressing the cause, while logs should record identifiers and digests rather than sensitive document/query text.

**Bridge.** The math contract protects comparison; source records protect the text and tenant relationship being compared.

## 5. Load bounded source records and make the initial chunk policy explicit

### Orienting question: what information must survive embedding?

Embedding a naked string loses the identity needed to explain or authorise a result. Preserve tenant, document ID, immutable document version, content digest, and original text in frozen records. The loader treats its inputs as untrusted values. It validates size and identifiers, but it is not an upload parser: type allowlists, file scanning, parser isolation, retention, and audit logging belong at the actual file-ingestion boundary.

```python
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
```

The narrow source-ID allowlist makes the colon-delimited chunk ID unambiguous; a broader identifier alphabet would need an escaping or canonical serialization rule. This is intentionally not a generic chunker. A long contract is rejected instead of arbitrarily sliced at a character count. Splitting rules can detach a negation from its clause, separate a quantity from a unit, or duplicate evidence across segments. Week 6 will design and evaluate chunk boundaries; this week establishes the retrieval contract that a later chunk policy must preserve.

The content digest lets an operator distinguish “P-101 version 1 with these exact bytes” from an identically titled but amended record. A digest does not prove source authenticity by itself; it proves identity of bytes relative to a trusted ingestion record.

**Checkpoint.** Why include `document_version` in a chunk ID? A source title and document ID can survive an amendment. Retrieval must be able to show which immutable version supplied its evidence.

## 6. Inject a local embedding adapter and version its behavior

### Orienting question: where does model-specific code stop?

The index depends on an interface, not an embedding library. `EmbeddingModelIdentity` makes the model artifact, runtime, preprocessing, dimension, metric, and query/document mode durable inputs to compatibility checks. `LocalEmbeddingAdapter` separates query and document calls. An adapter may call a loopback process, an in-process local library, or a test fake; the index does not need to know which.

```python
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
        if self.dimension < 1:
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
```

The fake maps a few lexical features to the same dimensions and thereby makes the demo repeatable. It cannot evaluate language understanding: it does not parse negation, conditional direction, synonyms beyond its tiny allowlist, tenant meaning, or document authority. Its apparent success on four documents says nothing about a real embedding model.

A real local adapter should implement the same protocol and add bounded batch sizes, timeouts, explicit `EmbeddingRuntimeError` translation, artifact verification, controlled runtime configuration, and redacted observability. It should never silently fall back to a remote endpoint. The adapter identity should be constructed from observed artifact/runtime configuration, not a model nickname copied from a README.

**Bridge.** Adapter identity says what produced a vector. The index manifest makes that identity inseparable from the stored corpus.

## 7. Build an exact, immutable in-memory cosine index

### Orienting question: what does a correctness baseline look like?

For a modest corpus, compare the query vector with every authorised stored vector. This **exact nearest-neighbour** baseline is simple and gives a reference ranking for tests and later ANN evaluation. It is not a claim that exhaustive scans will meet every latency target. It is the measurement oracle: if an approximate path disagrees, quantify the disagreement rather than assuming the fast result is correct.

The manifest records the source/chunk policy, corpus digest, model fingerprint, metric, dimension, vector count, and deterministic build timestamp. It is metadata, not a substitute for the actual source/version records.

```python
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
        document_vectors = adapter.embed_documents([chunk.text for chunk in chunks])
        if len(document_vectors) != len(chunks):
            raise EmbeddingRuntimeError("adapter must return one vector per document")
        entries: list[IndexedVector] = []
        for chunk, raw_vector in zip(chunks, document_vectors, strict=True):
            if len(raw_vector) != adapter.identity.dimension:
                raise VectorInvariantError(
                    "adapter returned an unexpected document dimension"
                )
            entries.append(
                IndexedVector(
                    source=chunk,
                    vector=normalize(raw_vector),
                    model_fingerprint=adapter.identity.fingerprint(),
                )
            )
        ordered_entries = tuple(
            sorted(entries, key=lambda entry: entry.source.chunk_id)
        )
        corpus_fingerprint = corpus_digest([entry.source for entry in ordered_entries])
        index_id = logical_index_id(
            schema_version=INDEX_SCHEMA_VERSION,
            model_fingerprint=adapter.identity.fingerprint(),
            corpus_fingerprint=corpus_fingerprint,
            chunk_policy="one-short-document-one-chunk/v1",
        )
        manifest = IndexManifest(
            schema_version=INDEX_SCHEMA_VERSION,
            index_id=index_id,
            created_at=created_at.astimezone(UTC),
            chunk_policy="one-short-document-one-chunk/v1",
            metric="cosine",
            dimension=adapter.identity.dimension,
            model_fingerprint=adapter.identity.fingerprint(),
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
        if type(request.top_k) is not int:
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
        query_vectors = adapter.embed_queries([request.query_text])
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
```

The authorization filter is deliberately before query embedding and scoring. Returning an empty tuple for no accessible sources avoids turning an object-level permission check into a document-existence oracle. An actual API should authenticate the principal outside this class, derive permissions from a trusted authorization service, constrain tenants at the storage query boundary, and audit access decisions without recording sensitive query text.

The deterministic key sorts first by descending score and then by `chunk_id`. Floating-point implementations can still vary across hardware/runtimes at extremely close scores; where ranking is consequential, record the runtime and define an epsilon/tie policy only after measuring its effects. Do not round scores before ranking.

## 8. Assemble P-101 through P-104 and test contracts, not model folklore

### Orienting question: which behavior can run without a downloaded model?

The following uses the teaching fake. It makes exactly four vectors, builds one index at a fixed UTC time, grants a principal access to all four documents, and retrieves two results. The test functions use only `assert`, so the displayed code runs sequentially as a standalone script and remains pytest-style when collected by pytest.

```python
FIXED_BUILD_TIME = datetime(2026, 8, 16, tzinfo=UTC)
ADAPTER = DemoLocalEmbeddingAdapter()


def sample_documents() -> tuple[SourceDocument, ...]:
    return load_documents(
        (
            UntrustedDocument(
                tenant_id="northwind-procurement",
                document_id="P-101",
                document_version="1",
                title="Atlas Metals purchase confirmation",
                text=(
                    "Copper wire will ship after incoming-material inspection. "
                    "Invoice terms: Net 30 after inspection approval."
                ),
            ),
            UntrustedDocument(
                tenant_id="northwind-procurement",
                document_id="P-102",
                document_version="1",
                title="Beacon Plastics purchase confirmation",
                text="Polymer pellets will ship on 2026-09-03. Invoice terms: Net 15 from receipt.",
            ),
            UntrustedDocument(
                tenant_id="northwind-procurement",
                document_id="P-103",
                document_version="1",
                title="Atlas Metals delivery update",
                text="The copper-wire shipment is delayed by two days while quality checks finish.",
            ),
            UntrustedDocument(
                tenant_id="northwind-procurement",
                document_id="P-104",
                document_version="1",
                title="Cedar Fasteners payment note",
                text="Payment is due after the receiving team signs off on the delivered bolts.",
            ),
        )
    )


def allow_all_sample_documents(principal_id: str) -> StaticObjectAccessPolicy:
    return StaticObjectAccessPolicy(
        permitted=frozenset(
            (
                principal_id,
                source.tenant_id,
                source.document_id,
                source.document_version,
            )
            for source in initial_chunks(sample_documents())
        )
    )


def sample_index() -> InMemoryCosineIndex:
    return InMemoryCosineIndex.build(
        initial_chunks(sample_documents()),
        ADAPTER,
        created_at=FIXED_BUILD_TIME,
    )


def expect_raises(expected: type[Exception], operation: Callable[[], object]) -> None:
    try:
        operation()
    except expected:
        return
    raise AssertionError(f"expected {expected.__name__}")


def test_exact_search_returns_payment_condition_candidates() -> None:
    results = sample_index().search(
        SearchRequest(
            principal_id="analyst-1",
            query_text="Which supplier documents require approval before payment?",
            top_k=2,
        ),
        adapter=ADAPTER,
        access_policy=allow_all_sample_documents("analyst-1"),
    )
    assert [result.source.document_id for result in results] == ["P-101", "P-104"]
    assert [result.rank for result in results] == [1, 2]
    assert results[0].score == results[1].score
    assert all(
        result.provenance.index_id == sample_index().manifest.index_id
        for result in results
    )


def test_access_is_filtered_before_candidate_scoring() -> None:
    policy = StaticObjectAccessPolicy(
        permitted=frozenset(
            {
                ("analyst-2", "northwind-procurement", "P-101", "1"),
            }
        )
    )
    results = sample_index().search(
        SearchRequest("analyst-2", "approval before payment", top_k=1),
        adapter=ADAPTER,
        access_policy=policy,
    )
    assert [result.source.document_id for result in results] == ["P-101"]
    assert (
        sample_index().search(
            SearchRequest("denied", "approval before payment", top_k=1),
            adapter=ADAPTER,
            access_policy=policy,
        )
        == ()
    )


def test_incompatible_adapter_is_rejected() -> None:
    incompatible = DemoLocalEmbeddingAdapter(
        identity=EmbeddingModelIdentity(
            model_id="another-local-model",
            artifact_digest="other-artifact",
            runtime_version="none",
            preprocessing_version="lower-punctuation-hyphen-split/v2",
            dimension=5,
            metric="cosine",
            asymmetric=True,
        )
    )
    expect_raises(
        IndexCompatibilityError,
        lambda: sample_index().search(
            SearchRequest("analyst-1", "approval before payment", top_k=1),
            adapter=incompatible,
            access_policy=allow_all_sample_documents("analyst-1"),
        ),
    )


def test_loader_rejects_oversized_untrusted_text() -> None:
    expect_raises(
        DocumentRejectedError,
        lambda: load_documents(
            (UntrustedDocument("tenant", "P-999", "1", "oversized", "x" * 1_001),)
        ),
    )


def test_vector_boundary_rejects_non_finite_values() -> None:
    expect_raises(
        VectorInvariantError,
        lambda: normalize((float("nan"), 1.0)),
    )


def test_index_rejects_tampered_manifest() -> None:
    index = sample_index()
    tampered = replace(index.manifest, corpus_digest="0" * 64)
    expect_raises(
        IndexCompatibilityError,
        lambda: InMemoryCosineIndex(tampered, index.entries),
    )


def run_displayed_tests() -> None:
    test_exact_search_returns_payment_condition_candidates()
    test_access_is_filtered_before_candidate_scoring()
    test_incompatible_adapter_is_rejected()
    test_loader_rejects_oversized_untrusted_text()
    test_vector_boundary_rejects_non_finite_values()
    test_index_rejects_tampered_manifest()


run_displayed_tests()
```

The `allow_all_sample_documents` helper is test-only policy, not an authorization design. The index sees every corpus vector at build time, but a query sees only entries passing `can_read` before it reaches the scoring comprehension. In a multi-tenant deployment, defense in depth requires tenant isolation in the source/index persistence boundary as well as authorization in the service layer.

### A compact manifest inspection

The index ID derives from the schema, model fingerprint, corpus digest, and chunk-policy version. It is stable for the same immutable inputs. `created_at` is provenance but deliberately not part of the identity, so repeating the same deterministic build does not invent a new logical index configuration.

```python
index = sample_index()
assert index.manifest.schema_version == "procurement-semantic-index/1.0.0"
assert index.manifest.metric == "cosine"
assert index.manifest.dimension == 5
assert index.manifest.vector_count == 4
assert index.manifest.chunk_policy == "one-short-document-one-chunk/v1"
```

An operational manifest should additionally reference an immutable source snapshot, build command/config digest, approval state, and storage location. It should not embed document text or credentials. Keep source/document access checks authoritative at read time; an index manifest is not an access-control list.

**Checkpoint.** Why is a matching dimension insufficient for compatibility? Two embeddings can both have five, 384, or 768 dimensions while using different models, artifacts, preprocessing, normalization, or query/document instructions. Their coordinates do not share a guaranteed geometry.

## 9. Dense retrieval and the exact baseline

### Orienting question: what does “dense retrieval” buy and lose?

Dense retrieval stores one dense vector per source unit and ranks vectors by a metric. It can bridge wording changes: P-101 says `approval`, while P-104 says `signs off`. It is useful when literal overlap is insufficient.

It compresses text. That compression is its cost. The relevant condition “after approval” can be entangled with `invoice`, `inspection`, supplier names, or generic procurement language. A dense vector does not preserve every token-level constraint. It cannot by itself prove that P-104 has the same scope, contract hierarchy, or current status as P-101.

The exact index is the baseline for three separate reasons:

1. It gives deterministic expected output for contract tests and small-corpus debugging.
2. It provides a reference set to measure how often an ANN implementation returns the exact neighbours.
3. It makes metric, normalization, filtering, and tie behavior inspectable before system complexity is introduced.

Exact does not mean relevant. An exact scan returns the closest vectors under the selected embedding and metric; it may still rank P-103 too highly. Distinguish **search exactness** (“did we return the metric’s nearest vectors?”) from **retrieval relevance** (“do those vectors correspond to the labelled evidence?”). ANN evaluation needs the former; model evaluation needs the latter.

## 10. Approximate nearest-neighbour search is a measured trade-off

### Orienting question: why approximate a correct baseline?

At large `N × D`, exhaustive comparison can exceed latency or memory-bandwidth budgets. **Approximate nearest-neighbour (ANN)** methods inspect a strategically selected portion of vector space and return likely neighbours more quickly. Graph- and partition-based algorithms differ internally, but the contract is common: parameters exchange exact-neighbour recall, latency, build cost, and memory.

```text
exact scan: query -> compare with every authorised vector -> exact metric ranking

ANN path:  query -> traverse/search a configured structure -> likely neighbours
                                  |                          |
                                  +---- tune and measure -----+
```

ANN is not a quality upgrade. It may miss the exact best neighbour, return a different order, require more memory than raw vectors, or show uneven latency across query types. An implementation can have high ANN recall and still retrieve semantically irrelevant passages because the embedding model is wrong for the task.

Measure ANN recall against the same authorization-filtered exact baseline. For each evaluation query, request a declared `k` from both paths. A simple set-based measure is:

```text
ANN recall@k = |ANN_top_k intersect exact_top_k| / |exact_top_k|
```

This is not relevance Recall@k. It asks whether ANN recovered the baseline’s vector neighbours. Report it beside end-to-end relevance metrics, p50/p95/p99 latency at an explicit measurement boundary, memory footprint, build duration, update/rebuild cost, and failure behavior. Tune on one governed development set; hold out another set for final comparison. Never select parameters based on the final held-out results and call that result unbiased.

For an access-controlled corpus, make the filtering semantics part of the comparison. An ANN structure built over all tenants cannot authorize a query by searching all candidates and merely hiding the final text. The candidate generation itself must respect the allowed partition or trustworthy pre-filter. The teaching index solves this simply by filtering frozen entries before exact scoring; it does not claim to solve scalable multi-tenant ANN.

**Checkpoint.** If ANN recall@10 is 0.98, does that mean relevance Recall@10 is 0.98? No. It means the ANN result overlaps the exact vector neighbours at the configured cutoff. Both paths can be irrelevant to the user’s question.

## 11. Domain-specific models require domain-specific evidence

### Orienting question: when is a general embedding model not enough?

Procurement text can contain terms with local meaning: approval types, receiving codes, product identifiers, amendment references, abbreviations, multilingual vendor notes, and legal exceptions. A broad model may perform well on generic semantic similarity while mishandling one distinction that controls a financial workflow.

A domain-specific embedding model is trained or adapted using procurement-like data. A general model may instead be selected because it performs well on procurement relevance evidence, but that does not make its training domain-specific. Either choice can improve retrieval if its task, language, and evaluation evidence match the corpus. A specialized model can also overfit terminology, encode historic policy, fail on a newly acquired business unit, or obscure critical negation. “Domain-specific” is not an evidence-free quality label.

Start with a written relevance contract. For the query in this lesson, directly relevant evidence must state a payment condition and preserve that approval/sign-off precedes payment. A quality-only shipment delay is not directly relevant. Capture disagreements between qualified reviewers and resolve them under a documented policy; relevance labels are judgement data, not extracted ground truth.

Then choose candidates under governance:

- verify artifact origin, integrity, license, supported language, and permitted use;
- keep sensitive evaluation documents local unless data handling is approved;
- pin exact artifact, runtime, tokenizer/preprocessing, query/document instruction, normalization, and batch configuration;
- measure a general baseline and each candidate on the same frozen task; and
- promote manually only after failure, subgroup, latency, memory, and access-control review.

Local execution changes the network boundary, not the trust model. A local model artifact can be compromised, out of date, or incompatible with hardware; its logs and caches can retain sensitive text. Model output still needs index validation and evaluation.

## 12. Evaluate retrieval as a held-out experiment

### Orienting question: how do you know P-101/P-104 is not a cherry-picked demo?

Build a governed evaluation collection before choosing a real model. It should contain source snapshots, query IDs, relevance judgments, label provenance, subset tags, and a split assignment. Avoid adding a query to both model selection and final reporting merely because it is convenient.

```text
source snapshot + chunk-policy version
        |
        +--> development queries/judgments -> choose model and ANN parameters
        |
        +--> held-out queries/judgments ---> one final comparison/report
```

Include direct positives, alternative terminology, negation, temporal amendments, supplier/entity collisions, product-code queries, short ambiguous questions, multilingual text if supported, and near-duplicate documents. Split by source family or time where possible. If an amendment and its near duplicate land on opposite sides, the model can appear to generalise merely by recognising copied language. Keep training/fine-tuning data, model selection data, ANN tuning data, and held-out evaluation data distinct.

### Relevance metrics answer different questions

For a query `q`, let `R_q` be its labelled relevant source chunks and `TopK_q` the returned chunks.

```text
Recall@k(q)    = |R_q intersect TopK_q| / |R_q|
Precision@k(q) = |R_q intersect TopK_q| / k
```

Recall@k asks whether relevant evidence appears in the review set. Precision@k asks how much noise the reviewer must inspect. For P-101/P-104, `k=1` can yield only one of two relevant records; `k=2` can expose both; `k=4` adds more procurement-adjacent noise.

**MRR** (mean reciprocal rank) is useful when finding the first relevant result quickly matters. For each query, take `1 / rank_of_first_relevant`, or zero if no relevant result appears, then average. It does not reward finding the second relevant clause after a good first one.

**nDCG** supports graded relevance. Assign a gain to each result label, discount lower ranks, and compare with the ideal order. It is useful if P-101 is a direct match, P-104 is relevant but needs contextual verification, and P-103 is only weakly related. Grading requires a clearly documented rubric; a convenient score scale without reviewer agreement only adds false precision.

Record metric definition, `k`, corpus snapshot, chunk policy, access-policy test configuration, model/manifest IDs, split, label version, hardware/runtime, and timestamp. A bare “Recall@10 = 0.84” cannot be reproduced or interpreted.

Label quality is part of evaluation quality. Keep adjudication notes, distinguish “not enough context to judge” from “non-relevant,” and measure reviewer disagreement before compressing judgments into one number. Do not let a model, prompt, or ranking result generate labels for the same held-out data used to promote it unless that procedure is the explicitly evaluated task. Where relevance depends on a private policy interpretation, record the policy version and route disagreements to the authorised owners. A benchmark with perfect arithmetic over unstable or leaked labels is not reliable evidence for deployment.

### Operational and failure analysis belongs beside scores

Measure latency at a declared boundary: for example, from accepted authorized query to returned result records, including local embedding and index search but excluding UI rendering. Report distributions, not a single best run: p50, p95, p99, cold/warm status, corpus size, dimension, batch behavior, hardware, and concurrency. Measure memory separately for artifact loading, raw vectors, and any index structure.

Stratify metrics by document type, language, query length, supplier/product-code presence, negation, temporal amendments, and tenant size where privacy permits. A model that improves average Recall@10 while failing all negation queries is unsafe for a contract-search use case. Inspect false positives and false negatives with authorised reviewers; do not log raw sensitive text into a general telemetry system.

**Checkpoint.** Can an embedding benchmark replace your governed procurement evaluation set? No. Broad benchmarks are useful screening evidence, but only task-aligned held-out queries, labels, access constraints, and operating conditions establish suitability for this retrieval boundary.

## 13. Semantic similarity can be operationally wrong

### Orienting question: why might P-103 outrank P-104?

The vector geometry may associate `quality checks`, `inspection`, and `approval` strongly. P-103 contains quality language and Atlas context, so an embedding can rank it highly despite the absence of a payment condition. That is a semantic near miss, not a source of truth.

Common error classes include:

- **Constraint loss:** `inspection` matches but `before payment` does not.
- **Negation/modality failure:** “approval is not required” is close to “approval is required.”
- **Direction failure:** “pay before approval” differs materially from “approve before payment.”
- **Entity collision:** an amendment belongs to another supplier, account, or product.
- **Temporal/version conflict:** an older clause is close to an active superseding clause.
- **Granularity failure:** a whole document vector compresses an exception that changes the meaning of one sentence.
- **Distribution shift:** new terminology, layout, language, or policy falls outside the evidence used for selection.

Mitigations are not a score threshold alone. Preserve source text and provenance; enforce tenant/object access before retrieval; verify identifiers, dates, active version, and deterministic constraints outside the embedding; and route consequential interpretation to authorised human review. A retrieval result should never grant permission to pay, change a supplier record, or tell a downstream model that a claim is true.

## 14. Top-k is a recall/noise and workflow decision

### Orienting question: why not always return more records?

`top_k` controls the number of highest-ranked authorised candidates returned. Increasing `k` often improves Recall@k because more relevant evidence has room to appear. It also increases review noise, latency/payload, and the chance that a reader treats a weakly related passage as decisive.

Choose `k` from workflow evidence, not habit. If a reviewer can inspect two passages, measure Recall@2 and Precision@2, then examine real error cases. If a missing clause is costly, a larger `k` might be justified with an interface that makes document/version provenance prominent. If reviewers need one direct policy statement, MRR and Precision@1 may matter more.

Do not confuse top-k with a confidence threshold. A result appears at rank one even when every score is weak. A score threshold introduces another policy that requires calibration, an explicit empty-result outcome, and evaluation by query group. “No authorized result above threshold” means exactly that; it does not prove the source corpus contains no relevant fact.

**Checkpoint.** Why is `top_k=100` not automatically safer? It can find more candidates, but it can swamp review with semantically adjacent text, increase sensitive-data exposure, and make the relevant source harder to identify.

## 15. Rebuild, promotion, rollback, and observability

### Orienting question: what happens after a model or document changes?

An index is a materialized view of an immutable corpus under a model configuration. It must be rebuilt when the embedding artifact, runtime, preprocessing, normalization rule, dimension, metric, query/document convention, or source/chunk policy changes. New document versions should produce new source records and a new corpus digest; never mutate an old vector in place while retaining old provenance.

Use a controlled lifecycle:

```text
candidate manifest + immutable source snapshot
        |
        +--> loader/index invariant tests
        +--> held-out relevance evaluation
        +--> ANN comparison with exact baseline, if applicable
        +--> latency, memory, subgroup, security review
        |
        v
manual promotion of immutable manifest
        |
        +--> serve known index ID
        |
        +--> rollback by selecting prior approved manifest
```

Rollback is manifest selection, not “embed everything again with whatever version worked last month.” Preserve prior approved artifacts/index snapshots according to retention policy, verify their digests, and record why promotion or rollback occurred. A cache keyed only by model nickname is unsafe because nicknames hide artifact and preprocessing changes.

Useful observability is aggregate and redacted: count index builds, source rejection reasons, adapter failures, authorization-denied/empty-result outcomes, latency distributions, result-count distributions, manifest/model IDs, and evaluation regressions. Do not log document text, query text, raw vectors, credentials, or unrestricted document identifiers. Store an auditable retrieval event only where governance permits, with principal/purpose, manifest ID, authorized result identities, and timestamp.

Rebuilds should be idempotent: the same source snapshot and model contract produce the same logical index ID. If a build fails, retain the last approved manifest rather than serving a partially populated replacement. Test recovery intentionally; an empty or mixed index is worse than a visible unavailable status.

## 16. Common mistakes and the corrective question

### “Cosine 0.92 means the passage is true.”

What source version, authority, and deterministic business rule turn a geometric score into a factual conclusion? Similarity ranks candidates; it does not validate claims.

### “The vectors have the same dimension, so they are compatible.”

Do artifact digest, runtime, preprocessing, normalization, metric, and query/document mode also match the manifest? Width is one invariant, not the model contract.

### “We filter results after ANN search.”

Could timing, score, count, or candidate existence leak an unauthorised object? Authorization must constrain candidate retrieval itself.

### “Our toy fake found P-104, so embeddings work.”

Which held-out, governed query/relevance judgments show quality on negation, amendments, suppliers, languages, and new terms? A deterministic fake tests application mechanics, not semantics.

### “ANN is faster, therefore better.”

What are ANN recall against exact search, relevance metrics, p95/p99 latency, memory, build cost, and failure behavior under the intended authorization filter?

### “A larger k prevents misses.”

Who reviews the added results, what noise do they introduce, and which measured Recall@k/Precision@k trade-off supports that choice?

### “A local model keeps everything private.”

What governs artifact provenance, local logs, caches, host access, retention, vector access, and incident response? Locality is not a complete security control.

## 17. Interview defense

**What is the difference between dense retrieval and exact retrieval?**

Dense retrieval represents source units as dense embedding vectors and ranks them by a vector metric. Exact retrieval describes the search algorithm: it compares a query with every eligible stored vector under that metric. An exact dense search can still return semantically irrelevant records if the embedding or relevance definition is wrong.

**Why expose separate query and document embedding methods?**

Retrieval can be asymmetric: a question and an evidence passage play different roles, and a model may require different encoders or instructions. Separate methods make the convention explicit and prevent accidental mixing. Their model identity and preprocessing must match the index manifest.

**When are dot product and cosine similarity equivalent?**

When both vectors are L2-normalized. Without that invariant, dot product includes magnitude and can rank differently. The model’s intended metric determines whether normalization is correct.

**How do you evaluate an ANN index?**

First compare its top-k results with the authorization-filtered exact baseline to measure ANN recall@k. Then evaluate end-to-end relevance with held-out labels, plus latency distributions, memory, build/update cost, and failure/subgroup behavior. ANN recall is not relevance recall.

**Why can semantically similar text retrieve incorrectly?**

Embeddings compress broad semantic associations and may lose negation, direction, entity, temporal, numeric, and exception constraints. A similar passage is a review candidate, not a validated answer.

**How do you choose top-k?**

From the review workflow and held-out Recall@k, Precision@k, MRR/nDCG, payload/latency, and error costs. More candidates may improve recall but add review noise and sensitive-data exposure.

## 18. Active recall

1. Why is an embedding model identity more than its model name?
2. What invariant makes normalized dot product equal cosine similarity?
3. Why must authorization run before candidate scoring rather than after sorting?
4. What does exact search prove that ANN search does not?
5. What does ANN recall@k measure, and what does it not measure?
6. Why is a document content digest useful but not proof of authenticity?
7. Which changes require a manifest/versioned rebuild?
8. How can `top_k` improve recall while harming an analyst?
9. Why should an evaluation split separate near-duplicate amendments?
10. What remains necessary after retrieval returns P-101?

### Answers

1. It includes artifact, runtime, preprocessing, dimension, metric, and query/document behavior that define vector comparability.
2. Both non-zero vectors must be L2-normalized to length one.
3. Later filtering can leak object existence, score, timing, or rank and wastes work on forbidden candidates.
4. It returns the true nearest vectors under the selected metric and eligible candidate set; it does not prove relevance.
5. It measures overlap with exact vector neighbours at a cutoff; it does not establish semantic relevance or factual support.
6. It identifies the bytes used by the index relative to a trusted record, but says nothing alone about who authored or authorised them.
7. Any change to source snapshot, chunk policy, model/artifact/runtime, preprocessing, normalization, dimension, metric, or query/document convention.
8. More records can surface relevant evidence but also create noise, burden review, raise latency, and expose extra sensitive text.
9. Otherwise copied language lets a model appear to generalise by recognising a near duplicate rather than handling new evidence.
10. Source/version review, authorization context, deterministic business validation, and required human approval.

## 19. Exercises

### Exercise A: metric invariant tests

Add tests showing that normalized dot product equals cosine similarity within a declared floating-point tolerance, that mismatched dimensions raise `VectorInvariantError`, and that a zero vector is rejected. Explain why exact equality is not a portable floating-point policy.

### Exercise B: source-version rebuild

Create P-101 version 2 with an amended payment clause. Show that its changed content digest produces a different corpus digest and logical index ID. Define which version is authorised for a query; do not let an old version silently remain the active answer.

### Exercise C: authorization negative cases

Add a second tenant with a semantically perfect matching clause. Demonstrate that an analyst granted only `northwind-procurement` cannot observe its result count, score, ID, or text. Keep the test data synthetic.

### Exercise D: evaluation plan

Write a label guide for 30 held-out procurement queries. Include at least five negation/direction cases, five version conflicts, five product-code/entity cases, and a language subgroup only if it is in scope. Define direct, partial, and non-relevant judgements before running model selection.

### Exercise E: ANN proposal without implementation

Specify an ANN experiment: exact baseline, eligible corpus partition, development/held-out split, ANN recall@k, relevance metrics, p50/p95/p99 boundary, memory measurement, build budget, rollback condition, and an access-control test. Do not choose a product or use a production corpus until those requirements are approved.

## Next action: replace the teaching adapter only after the benchmark exists

Keep the one-short-document/one-chunk exact baseline and its tests. Create the governed relevance set, baseline a candidate local embedding model, record its identity in the manifest, and compare it against exact retrieval before considering an approximate path. The next design task is chunk policy, not answer generation.

## Primary documentation and research

- [Python 3.13 typing: `Protocol` and typed interfaces](https://docs.python.org/3.13/library/typing.html)
- [Python 3.13 `dataclasses`](https://docs.python.org/3.13/library/dataclasses.html)
- [Python 3.13 `hashlib`](https://docs.python.org/3.13/library/hashlib.html)
- [Sentence-BERT: sentence embeddings for similarity search](https://aclanthology.org/D19-1410/)
- [Faiss: metric types, cosine normalization, and distances](https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances)
- [Faiss: exact indexes as the ANN evaluation baseline](https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index)
- [HNSW: approximate nearest-neighbour search](https://arxiv.org/abs/1603.09320)
- [BEIR: heterogeneous retrieval evaluation](https://arxiv.org/abs/2104.08663)
- [MTEB: Massive Text Embedding Benchmark](https://arxiv.org/abs/2210.07316)
