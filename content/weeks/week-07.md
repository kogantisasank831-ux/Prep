---
layout: week
permalink: /weeks/week-07/
title: "Sparse and hybrid retrieval: preserve exact evidence and semantic recall"
description: Build an authorization-aware, reproducible sparse/dense retrieval boundary for procurement codes, names, commercial terms, and paraphrases.
summary: Continue the frozen P-101 through P-106 corpus from a versioned token contract and authorized BM25 corpus through provenance-preserving dense candidates, reciprocal-rank fusion, and held-out evaluation.
kicker_primary: Sparse and hybrid retrieval
kicker_secondary: Exact evidence plus semantic recall
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-07/beginner/
---

## P-106 changes what “relevant” must preserve

P-101 through P-105 are now immutable, traceable chunks from Week 6. P-106 adds an exact commercial identifier:

```text
P-106 | Atlas Metals catalogue note | version 1
Tenant: northwind-procurement
Product code: CW-1000
Commercial name: Copper wire, 1,000 kg coil
Quoted unit price: USD 12.00
```

An authorized analyst can ask questions with materially different evidence needs:

| Query class | Example | Retrieval risk |
| --- | --- | --- |
| Exact identifier | `CW-1000` | a semantic representation can dilute or confuse the code |
| Supplier/entity | `Atlas Metals copper wire quote` | name variants and generic product language can collide |
| Commercial term | `Net 30 after inspection approval` | a generic invoice clause can crowd out the full condition |
| Semantic paraphrase | `receiving-team sign-off before payment` | literal tokens differ from P-104’s `signs off` |

The central design question is:

> How can sparse and dense retrieval be combined for codes, names, terms, and paraphrases while preserving authorization, reproducibility, provenance, and honest evaluation?

The answer is not “add two scores.” Sparse and dense systems observe different signals, produce incompatible score distributions, and can fail independently. They must operate on the same authorised frozen corpus, record their configuration, return source lineage, and be compared against held-out relevance/support labels.

```text
authenticated principal + typed metadata predicate
                    |
                    v
         authorised frozen chunk corpus only
                    |
        +-----------+------------+
        |                        |
        v                        v
versioned BM25             versioned dense adapter
        |                        |
        +------ ranked candidates+
                    |
                    v
   rank fusion + contributor provenance + deterministic tie rule
                    |
                    v
  reviewable source chunks, or an explicit empty/weak outcome
```

Retrieval relevance is not factual truth. A `CW-1000` match may be superseded, unauthorised for the current caller, or attached to a different agreement. No code below writes to a procurement system, generates an answer, or treats a ranking score as permission to act.

## 1. Make the keyword and lexical contract explicit before building BM25

### Orienting question: what exactly is an “exact” product-code match?

Sparse retrieval begins with a tokenizer. It maps visible text into terms, so its behavior decides whether `CW-1000` survives as one token, becomes `cw` plus `1000`, or disappears. Tokenization, normalization, aliases, and BM25 parameters are retrieval behavior; they belong in a versioned configuration and manifest.

For this corpus, preserve internal hyphens, underscores, and slashes:

```text
CW-1000       -> cw-1000
PO_2026/18    -> po_2026/18
Net 30        -> net, 30
```

That is intentionally conservative. `CW1000` does not match `CW-1000`, and `CW-100O` with letter O does not match zero. An alias table could map a known supplier code variant to a canonical token, but aliases create false-positive risk, must preserve the original text, need an owner and effective version, and require evaluation against exact-code/OCR cases. Do not normalize punctuation away merely because it looks convenient.

```python
from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from hashlib import sha256
from math import isfinite, log
import re
from typing import Protocol, Self


TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:[-_/][a-z0-9]+)*")
MANIFEST_SCHEMA = "procurement-hybrid-retrieval/1.0.0"


class RetrievalError(Exception):
    """Base class for explicit sparse/dense retrieval boundary failures."""


class CorpusInvariantError(RetrievalError):
    """Frozen chunks or authorised corpus invariants were violated."""


class ConfigurationError(RetrievalError):
    """Tokenizer, BM25, dense, or fusion configuration is invalid."""


class ManifestCompatibilityError(RetrievalError):
    """A caller attempted to combine incompatible retrieval artifacts."""


@dataclass(frozen=True)
class SourceChunk:
    chunk_id: str
    tenant_id: str
    document_id: str
    document_version: str
    source_digest: str
    text: str
    metadata: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class TokenContract:
    name: str
    version: str
    pattern: str

    def fingerprint(self) -> str:
        if not self.name or not self.version or not self.pattern:
            raise ConfigurationError("token contract fields must be non-empty")
        return digest_text("\x1f".join((self.name, self.version, self.pattern)))


DEFAULT_TOKEN_CONTRACT = TokenContract(
    name="identifier-preserving",
    version="1.0.0",
    pattern=TOKEN_PATTERN.pattern,
)


@dataclass(frozen=True)
class MetadataFilter:
    field: str
    value: str


@dataclass(frozen=True)
class RetrievalRequest:
    principal_id: str
    query_text: str
    top_k: int
    filters: tuple[MetadataFilter, ...] = ()


def digest_text(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def tokenize(text: str, contract: TokenContract = DEFAULT_TOKEN_CONTRACT) -> tuple[str, ...]:
    if contract.pattern != TOKEN_PATTERN.pattern:
        raise ConfigurationError("reference tokenizer does not implement this contract")
    return tuple(TOKEN_PATTERN.findall(text.lower()))


def metadata_values(chunk: SourceChunk) -> dict[str, str]:
    return dict(chunk.metadata)
```

The reference tokenizer is local and deterministic. It does not correct typos, do OCR, expand abbreviations, or recognize company aliases. Those are material retrieval-policy changes, not harmless preprocessing. Keep the original document text and the token contract fingerprint with every index build so a reviewer can explain what matched.

### Aliases and normalization need the same evidence discipline as source data

It is tempting to make sparse search friendlier by indexing both `cw-1000` and `cw1000`, stripping punctuation, or expanding an abbreviation such as `AM` to `Atlas Metals`. Each operation can improve one query while creating a different error. `AM` may mean another supplier or an internal field; punctuation may distinguish two catalogue codes; an OCR correction may turn an uncertain source value into an apparently exact match.

Treat aliases as governed retrieval data. Each alias needs a canonical target, source/evidence, owner, effective range, tenant/supplier scope, and version. Preserve the original tokens separately, make the alias policy visible in the manifest, and test positive and negative cases. An alias that changes the candidate corpus or query terms after an incident is a new retrieval configuration, not a harmless patch. The safe fallback is a visible no-exact-match result with the original query intact, followed by authorised review if the business workflow requires it.

Normalization should also be asymmetric where the task demands it. Query-time expansion can be useful when it is explicitly recorded, while document-time expansion changes index statistics and storage. Applying both without a defined policy can double-count an alias in BM25, increase duplicate candidates, and make an exact source token appear more certain than it is. Evaluate code, supplier, and commercial-term categories separately before adopting a convenience rule across the corpus.

The decision belongs to the retrieval boundary, not to an unversioned UI convenience feature. A user must be able to distinguish an exact literal match from an alias-assisted candidate during authorised review.

If that distinction is unavailable in logs, result provenance, and evaluation labels, an operator cannot safely diagnose a code-search regression or explain why a particular candidate was returned.

It also prevents accidental claims that lexical identity survived a transformation when it did not.

## 2. BM25 is a sparse ranking formula with corpus-dependent behavior

### Orienting question: why does `CW-1000` deserve more credit than `invoice`?

BM25 ranks chunks using terms present in the query and corpus statistics. For query term `t` and chunk `d`, a common form is:

```text
BM25(q, d) = sum over terms t in q of
  IDF(t) * f(t, d) * (k1 + 1) /
  (f(t, d) + k1 * (1 - b + b * |d| / avgdl))

IDF(t) = log(1 + (N - df(t) + 0.5) / (df(t) + 0.5))
```

`f(t, d)` is term frequency in the chunk. Its fraction gives **term-frequency saturation**: repeating `CW-1000` increases evidence, but does not create unbounded score. `df(t)` is document frequency, so **inverse document frequency** gives rare terms more discriminative weight. `|d| / avgdl` is **document-length normalization**; it prevents a long chunk from winning merely because it contains more possible terms. `k1` and `b` are configuration parameters, not universal constants.

BM25 is strong when lexical identity matters: exact product codes, supplier names, abbreviations, and commercial terms. It can miss paraphrases, synonyms, spelling variants, or `signs off` when the query says `approval`. It can also match an inactive version or a negated clause. Sparse relevance remains retrieval relevance, not truth.

```python
@dataclass(frozen=True)
class BM25Config:
    k1: float = 1.2
    b: float = 0.75

    def fingerprint(self) -> str:
        if not isfinite(self.k1) or not isfinite(self.b) or self.k1 <= 0.0 or not 0.0 <= self.b <= 1.0:
            raise ConfigurationError("BM25 requires k1 > 0 and b in [0, 1]")
        return digest_text(f"k1={self.k1:.12g}\x1fb={self.b:.12g}")


@dataclass(frozen=True)
class BM25Index:
    chunks: tuple[SourceChunk, ...]
    term_frequencies: Mapping[str, Counter[str]]
    document_frequencies: Mapping[str, int]
    document_lengths: Mapping[str, int]
    average_document_length: float
    token_contract: TokenContract
    config: BM25Config

    @classmethod
    def build(
        cls,
        chunks: Sequence[SourceChunk],
        *,
        token_contract: TokenContract,
        config: BM25Config,
    ) -> Self:
        config.fingerprint()
        if not chunks:
            raise CorpusInvariantError("BM25 requires at least one authorised chunk")
        term_frequencies: dict[str, Counter[str]] = {}
        document_frequencies: Counter[str] = Counter()
        document_lengths: dict[str, int] = {}
        for chunk in chunks:
            if chunk.chunk_id in term_frequencies:
                raise CorpusInvariantError("chunk IDs must be unique")
            terms = tokenize(chunk.text, token_contract)
            if not terms:
                raise CorpusInvariantError("chunks must have at least one token")
            term_frequencies[chunk.chunk_id] = Counter(terms)
            document_lengths[chunk.chunk_id] = len(terms)
            document_frequencies.update(term_frequencies[chunk.chunk_id].keys())
        return cls(
            chunks=tuple(chunks),
            term_frequencies=term_frequencies,
            document_frequencies=dict(document_frequencies),
            document_lengths=document_lengths,
            average_document_length=sum(document_lengths.values()) / len(document_lengths),
            token_contract=token_contract,
            config=config,
        )

    def score(self, query_text: str, chunk: SourceChunk) -> float:
        frequencies = self.term_frequencies[chunk.chunk_id]
        length = self.document_lengths[chunk.chunk_id]
        total = 0.0
        for term in tokenize(query_text, self.token_contract):
            frequency = frequencies[term]
            if frequency == 0:
                continue
            document_frequency = self.document_frequencies[term]
            inverse_document_frequency = log(
                1.0 + (len(self.chunks) - document_frequency + 0.5) / (document_frequency + 0.5)
            )
            denominator = frequency + self.config.k1 * (
                1.0 - self.config.b + self.config.b * length / self.average_document_length
            )
            total += inverse_document_frequency * frequency * (self.config.k1 + 1.0) / denominator
        return total
```

The formula makes an important security/reproducibility point: IDF and `avgdl` are corpus statistics. If unauthorised chunks remain in the index, they influence scores even when final display filters them away. That is an information leak and produces rankings that the authorised caller could not reproduce from their permitted corpus.

## 3. Build the authorised corpus before either retriever scores

### Orienting question: what may an unauthorized exact match influence?

Nothing: no BM25 term frequency, no IDF, no average length, no dense candidate, no fusion contributor, no result count, and no cache key derived from the candidate set. The reference implementation builds a small exact authorised corpus per request. That is straightforward and correct for this lesson, but it is not the scalable final architecture.

Metadata filters are typed, allowlisted predicates. They can narrow a query to a supplier or document type, but they are not authorization. The access policy derives object visibility from a trusted principal. A caller cannot obtain another tenant by adding a metadata filter.

```python
ALLOWED_FILTER_FIELDS = frozenset({"supplier", "document_type"})


class AccessPolicy(Protocol):
    def can_read(self, principal_id: str, chunk: SourceChunk) -> bool:
        ...


@dataclass(frozen=True)
class StaticObjectAccessPolicy:
    permitted: frozenset[tuple[str, str, str, str]]

    def can_read(self, principal_id: str, chunk: SourceChunk) -> bool:
        return (
            principal_id,
            chunk.tenant_id,
            chunk.document_id,
            chunk.document_version,
        ) in self.permitted


def validate_filters(filters: Sequence[MetadataFilter]) -> None:
    if any(filter_.field not in ALLOWED_FILTER_FIELDS or not filter_.value for filter_ in filters):
        raise ConfigurationError("metadata filters must use a non-empty allowlisted predicate")
    if len({filter_.field for filter_ in filters}) != len(filters):
        raise ConfigurationError("metadata filter fields must be unique")


@dataclass(frozen=True)
class AuthorizedCorpus:
    principal_id: str
    chunks: tuple[SourceChunk, ...]
    partition_fingerprint: str

    @classmethod
    def build(
        cls,
        request: RetrievalRequest,
        chunks: Sequence[SourceChunk],
        access_policy: AccessPolicy,
    ) -> Self:
        if not request.principal_id.strip() or not request.query_text.strip() or request.top_k <= 0:
            raise ValueError("principal, query text, and positive top_k are required")
        validate_filters(request.filters)
        def matches_filters(chunk: SourceChunk) -> bool:
            values = metadata_values(chunk)
            return all(values.get(filter_.field) == filter_.value for filter_ in request.filters)
        authorised = tuple(
            chunk for chunk in chunks if access_policy.can_read(request.principal_id, chunk)
        )
        chunk_ids = [chunk.chunk_id for chunk in authorised]
        if len(set(chunk_ids)) != len(chunk_ids):
            raise CorpusInvariantError("authorised chunk IDs must be unique")
        if any(
            not all(
                (
                    chunk.chunk_id,
                    chunk.tenant_id,
                    chunk.document_id,
                    chunk.document_version,
                    chunk.source_digest,
                    chunk.text.strip(),
                )
            )
            or len(dict(chunk.metadata)) != len(chunk.metadata)
            for chunk in authorised
        ):
            raise CorpusInvariantError("authorised chunks require complete identity, text, and unique metadata fields")
        eligible = tuple(chunk for chunk in authorised if matches_filters(chunk))
        identity = "\n".join(
            sorted(
                f"{chunk.tenant_id}\x1f{chunk.chunk_id}\x1f{chunk.source_digest}"
                for chunk in eligible
            )
        )
        filters = "\n".join(
            sorted(f"{filter_.field}={filter_.value}" for filter_ in request.filters)
        )
        return cls(
            request.principal_id,
            eligible,
            digest_text(f"{request.principal_id}\n{identity}\n{filters}"),
        )

    def bm25(self, token_contract: TokenContract, config: BM25Config) -> BM25Index | None:
        if not self.chunks:
            return None
        return BM25Index.build(self.chunks, token_contract=token_contract, config=config)
```

For a larger system, common correct alternatives include per-tenant/authorisation-partitioned indexes, pre-filtered shard routing, or an index/filter design whose candidate generation itself enforces object visibility. The invariant remains: forbidden chunks cannot influence retrieval statistics or candidate scoring. “Search everything then hide the result” is not an access control design.

### Scaling the authorization boundary without weakening it

Building a fresh exact BM25 index for every authorised request is a correctness reference, not a throughput recommendation. At larger scale, the partition selected before search must still be a trusted representation of the caller's visible corpus. A per-tenant index is simple when every object belongs to exactly one tenant; it is insufficient when documents can be shared selectively across tenants. Object-level grants may require a secure pre-filter, a dedicated access partition, or a materialized authorised view with carefully designed invalidation.

The same discipline applies to dense candidates. A vector index that generates neighbours across all tenants and removes them afterward has already allowed forbidden vectors to affect traversal, timing, cache state, and potentially result-count behavior. Design the storage/index boundary so it can enforce the applicable access partition before candidate search, then test negative cases under realistic cardinality and cache conditions.

Metadata filters are also part of the attack surface. The reference only permits `supplier` and `document_type`, with exact equality over stored values. Adding free-form fields, prefix search, ranges, or user-defined expressions broadens the query contract and can create enumeration paths. Give each predicate an explicit semantic meaning, type, authorization implication, and manifest identity. Filter values themselves can be commercially sensitive; logs should record a safe policy identifier rather than unrestricted query payloads.

## 4. Dense and sparse signals complement, but do not validate each other

### Orienting question: when does each retriever fail first?

Sparse retrieval preserves visible lexical evidence. It is usually the first choice for `CW-1000`, a supplier name, a rare payment acronym, or a commercial term. It can fail on paraphrase: P-104 says `signs off`, not `approval`.

Dense retrieval can help bridge paraphrases and related language. It can fail on identifiers, aliases, entity/version distinctions, numbers, negation, and narrow commercial conditions. It may return a copper-wire delivery delay for a code query because “copper wire” dominates its representation. It may be useful, but never as a substitute for exact source checks.

The adapter protocol makes model behavior explicit. `DemoDenseAdapter` is a deterministic teaching fake, not an embedding model, quality claim, or model-selection result. A real local adapter must be pinned by artifact/runtime/preprocessing/metric identity and evaluated on held-out data.

```python
@dataclass(frozen=True)
class DenseConfig:
    adapter_id: str
    artifact_digest: str
    runtime_id: str
    preprocessing_version: str
    metric: str

    def fingerprint(self) -> str:
        values = (
            self.adapter_id,
            self.artifact_digest,
            self.runtime_id,
            self.preprocessing_version,
            self.metric,
        )
        if not all(values):
            raise ConfigurationError("dense configuration fields must be non-empty")
        return digest_text("\x1f".join(values))


class DenseAdapter(Protocol):
    @property
    def config(self) -> DenseConfig:
        ...

    def score(self, query_text: str, chunk_text: str) -> float:
        ...


@dataclass(frozen=True)
class DemoDenseAdapter:
    config: DenseConfig = DenseConfig(
        adapter_id="demo-procurement-features",
        artifact_digest="synthetic-only",
        runtime_id="python-stdlib/3.13",
        preprocessing_version="identifier-dropping/v1",
        metric="jaccard-features",
    )

    def _features(self, text: str) -> frozenset[str]:
        preserved_terms = set(tokenize(text))
        component_terms = {
            component
            for term in preserved_terms
            for component in re.split(r"[-_/]", term)
        }
        terms = preserved_terms | component_terms
        features: set[str] = set()
        if terms & {"payment", "invoice", "due"}:
            features.add("payment")
        if terms & {"approval", "approve", "sign", "signs", "off"}:
            features.add("approval")
        if terms & {"inspection", "quality", "receiving"}:
            features.add("inspection")
        if terms & {"copper", "wire", "coil"}:
            features.add("copper-wire")
        return frozenset(features)

    def score(self, query_text: str, chunk_text: str) -> float:
        query_features = self._features(query_text)
        chunk_features = self._features(chunk_text)
        if not query_features or not chunk_features:
            return 0.0
        return len(query_features & chunk_features) / len(query_features | chunk_features)
```

## 5. Preserve raw ranks and contributor provenance through fusion

### Orienting question: why can’t we simply add BM25 and dense scores?

BM25 scores depend on query terms, corpus statistics, `k1`, and `b`; dense scores depend on the model, metric, and vector normalization. A BM25 score of `8.4` and a cosine-like score of `0.81` have no shared unit. Raw addition silently grants one signal an arbitrary dominance.

Min–max normalization is useful for explaining the problem:

```text
normalized(s) = (s - min(scores)) / (max(scores) - min(scores))
```

It is not a universal fusion policy. An outlier compresses the rest, a flat list has no range, distributions shift across tenant partitions, and a normalized value is still not a probability. Other approaches—z-score, rank normalization, calibration, or a learned combiner—need held-out governance and evaluation.

For this baseline, use **reciprocal rank fusion (RRF)**. It combines positions rather than incompatible raw scales:

```text
RRF(chunk) = sum over contributors r of weight(r) / (rank_constant + rank_r(chunk))
```

Weights are not free tuning knobs. If they differ from one, record an explicit governed configuration, reason, development split, and rollback target. The default configuration below uses equal weights. RRF sees only the candidate depth supplied by each retriever, so a useful fourth-ranked sparse candidate cannot be recovered if sparse depth is three. It can also retain duplicate chunks produced by overlap; measure duplicate rate and group source lineage before presenting results.

```python
@dataclass(frozen=True)
class RankedCandidate:
    chunk: SourceChunk
    score: float
    rank: int
    retriever: str


@dataclass(frozen=True)
class Contributor:
    retriever: str
    rank: int
    raw_score: float


@dataclass(frozen=True)
class FusedCandidate:
    chunk: SourceChunk
    score: float
    rank: int
    contributors: tuple[Contributor, ...]


@dataclass(frozen=True)
class FusionConfig:
    rank_constant: int = 60
    weights: tuple[tuple[str, float], ...] = (("bm25", 1.0), ("dense", 1.0))

    def fingerprint(self) -> str:
        if (
            self.rank_constant <= 0
            or not self.weights
            or any(not name or not isfinite(weight) or weight <= 0.0 for name, weight in self.weights)
        ):
            raise ConfigurationError("RRF rank constant and weights must be positive")
        if len({name for name, _ in self.weights}) != len(self.weights):
            raise ConfigurationError("RRF retriever names must be unique")
        values = (
            str(self.rank_constant),
            *(f"{name}={weight:.12g}" for name, weight in sorted(self.weights)),
        )
        return digest_text("\x1f".join(values))


def rank_candidates(
    scores: Iterable[tuple[SourceChunk, float]],
    *,
    top_k: int,
    retriever: str,
) -> tuple[RankedCandidate, ...]:
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    ordered = sorted(scores, key=lambda item: (-item[1], item[0].chunk_id))[:top_k]
    return tuple(
        RankedCandidate(chunk, score, rank, retriever)
        for rank, (chunk, score) in enumerate(ordered, start=1)
    )


def sparse_candidates(
    request: RetrievalRequest,
    corpus: AuthorizedCorpus,
    index: BM25Index | None,
) -> tuple[RankedCandidate, ...]:
    if index is None:
        return ()
    if index.chunks != corpus.chunks:
        raise ManifestCompatibilityError("BM25 index corpus differs from authorised corpus")
    return rank_candidates(
        ((chunk, index.score(request.query_text, chunk)) for chunk in corpus.chunks),
        top_k=request.top_k,
        retriever="bm25",
    )


def dense_candidates(
    request: RetrievalRequest,
    corpus: AuthorizedCorpus,
    adapter: DenseAdapter,
) -> tuple[RankedCandidate, ...]:
    return rank_candidates(
        ((chunk, adapter.score(request.query_text, chunk.text)) for chunk in corpus.chunks),
        top_k=request.top_k,
        retriever="dense",
    )


def min_max_normalize(scores: Mapping[str, float]) -> dict[str, float]:
    if not scores:
        return {}
    lower, upper = min(scores.values()), max(scores.values())
    if lower == upper:
        return {key: 0.0 for key in scores}
    return {key: (value - lower) / (upper - lower) for key, value in scores.items()}


def reciprocal_rank_fusion(
    ranked_lists: Sequence[Sequence[RankedCandidate]],
    config: FusionConfig,
    *,
    top_k: int,
) -> tuple[FusedCandidate, ...]:
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    weights = dict(config.weights)
    config.fingerprint()
    fused_scores: defaultdict[str, float] = defaultdict(float)
    chunks: dict[str, SourceChunk] = {}
    contributors: defaultdict[str, list[Contributor]] = defaultdict(list)
    seen_contributors: set[tuple[str, str]] = set()
    for ranked_list in ranked_lists:
        for candidate in ranked_list:
            if candidate.retriever not in weights:
                raise ConfigurationError("fusion received an unconfigured retriever")
            if candidate.rank <= 0 or not isfinite(candidate.score):
                raise ConfigurationError("fusion candidates require positive ranks and finite scores")
            contribution_key = (candidate.retriever, candidate.chunk.chunk_id)
            if contribution_key in seen_contributors:
                raise ConfigurationError("fusion received a duplicate retriever/chunk contribution")
            seen_contributors.add(contribution_key)
            existing_chunk = chunks.get(candidate.chunk.chunk_id)
            if existing_chunk is not None and existing_chunk != candidate.chunk:
                raise CorpusInvariantError("one chunk ID resolved to conflicting source chunks")
            fused_scores[candidate.chunk.chunk_id] += weights[candidate.retriever] / (
                config.rank_constant + candidate.rank
            )
            chunks[candidate.chunk.chunk_id] = candidate.chunk
            contributors[candidate.chunk.chunk_id].append(
                Contributor(candidate.retriever, candidate.rank, candidate.score)
            )
    ordered = sorted(fused_scores.items(), key=lambda item: (-item[1], item[0]))[:top_k]
    return tuple(
        FusedCandidate(
            chunk=chunks[chunk_id],
            score=score,
            rank=rank,
            contributors=tuple(sorted(contributors[chunk_id], key=lambda item: item.retriever)),
        )
        for rank, (chunk_id, score) in enumerate(ordered, start=1)
    )


def hybrid_candidates(
    request: RetrievalRequest,
    corpus: AuthorizedCorpus,
    index: BM25Index | None,
    adapter: DenseAdapter,
    fusion: FusionConfig,
    *,
    candidate_depth: int,
) -> tuple[FusedCandidate, ...]:
    if candidate_depth < request.top_k:
        raise ConfigurationError("candidate depth must be at least top_k")
    expanded = RetrievalRequest(
        principal_id=request.principal_id,
        query_text=request.query_text,
        top_k=candidate_depth,
        filters=request.filters,
    )
    return reciprocal_rank_fusion(
        (
            sparse_candidates(expanded, corpus, index),
            dense_candidates(expanded, corpus, adapter),
        ),
        fusion,
        top_k=request.top_k,
    )
```

Contributor ranks and raw scores let an operator diagnose an RRF result: “P-106 appeared because BM25 ranked it first and dense did not contribute,” rather than inventing a misleading combined meaning. Keep raw scores internal/authorised where they may reveal corpus statistics; a user-facing result normally needs source provenance and a safe explanation of the retrieval path, not unrestricted diagnostics.

## 6. Record the whole retrieval configuration in one manifest

### Orienting question: what changed if a hybrid result changes tomorrow?

The answer is not just “the model.” Source/chunk snapshot, token contract, BM25 parameters, dense adapter configuration, access partition/filter, fusion policy, candidate depth, and top-k all affect the candidate set. A manifest turns those hidden inputs into explicit compatibility checks.

```python
@dataclass(frozen=True)
class RetrievalManifest:
    schema_version: str
    corpus_fingerprint: str
    partition_fingerprint: str
    token_fingerprint: str
    bm25_fingerprint: str
    dense_fingerprint: str
    fusion_fingerprint: str
    candidate_depth: int
    top_k: int

    def fingerprint(self) -> str:
        if self.candidate_depth < self.top_k or self.top_k <= 0:
            raise ConfigurationError("candidate depth must be at least positive top_k")
        fields = (
            self.schema_version,
            self.corpus_fingerprint,
            self.partition_fingerprint,
            self.token_fingerprint,
            self.bm25_fingerprint,
            self.dense_fingerprint,
            self.fusion_fingerprint,
            str(self.candidate_depth),
            str(self.top_k),
        )
        return digest_text("\x1f".join(fields))


def corpus_fingerprint(chunks: Sequence[SourceChunk]) -> str:
    return digest_text(
        "\n".join(
            sorted(
                "\x1f".join(
                    (
                        chunk.tenant_id,
                        chunk.document_id,
                        chunk.document_version,
                        chunk.chunk_id,
                        chunk.source_digest,
                    )
                )
                for chunk in chunks
            )
        )
    )


def make_manifest(
    corpus: AuthorizedCorpus,
    token_contract: TokenContract,
    bm25_config: BM25Config,
    dense_adapter: DenseAdapter,
    fusion_config: FusionConfig,
    *,
    candidate_depth: int,
    top_k: int,
) -> RetrievalManifest:
    manifest = RetrievalManifest(
        schema_version=MANIFEST_SCHEMA,
        corpus_fingerprint=corpus_fingerprint(corpus.chunks),
        partition_fingerprint=corpus.partition_fingerprint,
        token_fingerprint=token_contract.fingerprint(),
        bm25_fingerprint=bm25_config.fingerprint(),
        dense_fingerprint=dense_adapter.config.fingerprint(),
        fusion_fingerprint=fusion_config.fingerprint(),
        candidate_depth=candidate_depth,
        top_k=top_k,
    )
    manifest.fingerprint()
    return manifest


def require_compatible(expected: RetrievalManifest, observed: RetrievalManifest) -> None:
    if expected.fingerprint() != observed.fingerprint():
        raise ManifestCompatibilityError("retrieval manifest differs from the requested contract")
```

Build a new manifest when source/chunk policy, tokenization, alias policy, BM25 parameters, dense artifact/runtime/preprocessing/metric, metadata filtering/access partition, fusion weights, candidate depth, or top-k changes. Promotion is manual after invariant tests and held-out evaluation. Rollback selects a prior immutable manifest and its compatible corpus/index artifacts; it does not mutate old chunks or mix new dense vectors with an old token policy.

## 7. Compare sparse, dense, and hybrid on the same frozen evidence

### Orienting question: what is a fair comparison?

Hold source chunks, document versions, authorization filter, metadata predicate, query split, labels, token/BM25 configuration, dense adapter, candidate depth, and final `top_k` fixed. Vary only the retrieval/fusion path. Split near-duplicate catalogues, amendments, and repeated boilerplate by source family or time between development and held-out sets to avoid leakage.

Evaluate more than one attractive query:

| Measure | Why it matters |
| --- | --- |
| Recall@k / Precision@k | evidence found versus reviewer noise |
| MRR / nDCG where appropriate | whether direct or graded evidence appears early |
| Support completeness | whether returned chunks contain all declared evidence atoms for review |
| Duplicate rate | whether overlap/repetition consumes result slots |
| Latency, cost, memory | local adapter/index practicality at the measurement boundary |
| Category failures | codes, abbreviations, suppliers, commercial terms, paraphrases, OCR, versions, tenants |

No metric proves factual correctness. The P-106 price still needs source/version review. No average should hide a catastrophic code or tenant-isolation failure. Record parser/chunk manifest, model artifact/runtime, hardware, local measurement boundary, and label version with every result. Do not claim a benchmark score or winner until the governed experiment runs.

```python
@dataclass(frozen=True)
class EvaluationCase:
    query_id: str
    request: RetrievalRequest
    relevant_chunk_ids: frozenset[str]
    required_atoms: frozenset[str]
    category: str


def recall_at_k(returned_ids: Sequence[str], relevant_ids: frozenset[str]) -> float:
    if not relevant_ids:
        raise ValueError("evaluation case needs at least one relevant chunk")
    return len(set(returned_ids) & relevant_ids) / len(relevant_ids)


def precision_at_k(returned_ids: Sequence[str], relevant_ids: frozenset[str]) -> float:
    if not returned_ids:
        return 0.0
    return len(set(returned_ids) & relevant_ids) / len(returned_ids)


def reciprocal_rank(returned_ids: Sequence[str], relevant_ids: frozenset[str]) -> float:
    for rank, chunk_id in enumerate(returned_ids, start=1):
        if chunk_id in relevant_ids:
            return 1.0 / rank
    return 0.0


def support_complete(chunks: Sequence[SourceChunk], atoms: frozenset[str]) -> bool:
    source_text = "\n".join(chunk.text.lower() for chunk in chunks)
    return all(atom.lower() in source_text for atom in atoms)
```

`nDCG` is appropriate when a written rubric assigns graded relevance; do not invent grades merely to produce the metric. Support completeness is stricter than relevance: for the P-105 question, it may require the table row, `Net 30 after inspection approval`, and the cross-reference to Schedule A. It evaluates reviewable evidence, not generated prose.

### Read evaluation metrics as a decision record, not a leaderboard

Define a query and relevance guide before tuning token aliases, `k1`, `b`, dense adapters, candidate depth, or fusion weights. A useful corpus has direct positives, lexical distractors, paraphrases, product-code variants, supplier-name collisions, numbers/units, negation, expired amendments, OCR-like character errors, and tenant-denied records. Preserve label provenance and adjudication notes: a disagreement about whether P-101 or P-106 is relevant to a catalogue query may reflect an unresolved business meaning, not a model failure.

Split documents by family or time where possible. A version-2 amendment that repeats version-1 wording should not sit in held-out evaluation if the model, alias rules, or chunk policy was tuned on version 1. The same applies to duplicate overlapping chunks: if a labelled phrase appears in many chunks, aggregate or group evaluation carefully so repeated copies do not manufacture apparent recall. Freeze the source/chunk manifest and access partition for all paths in a comparison. Sparse, dense, and hybrid cannot be compared fairly if one sees a different corpus.

Report both aggregate and subgroup behavior. For example, a hybrid policy may improve average Recall@10 but regress on `CW-1000`-style identifiers, `Net 15` versus `Net 30` commercial distinctions, or a tenant with only short documents. Review category failures before promotion. A single mean can hide a retrieval boundary that is unacceptable for one important query class.

Latency, cost, and memory need declared boundaries too. Record whether latency begins before or after authorization, whether it includes local embedding, BM25 construction, fusion, serialization, and cache lookup, plus corpus cardinality, vector dimension, hardware, concurrency, and cold/warm state. Separate raw chunk text/metadata storage, sparse postings/statistics, dense vectors, and index overhead. A configuration that wins one offline metric but exceeds the operator's local resource budget or harms p99 latency may not be deployable.

Finally, define the empty/weak-result policy before evaluation. An empty authorised corpus after a filter, a zero-term BM25 query, and a low-confidence semantic candidate are different operational states. Preserve a safe status, manifest fingerprint, and allowed source provenance where applicable. Do not broaden filters, access another tenant, silently rewrite the query, or fabricate a conclusion to make the interface look helpful.

## 8. Cumulative fixtures and contract tests

### Orienting question: what can a deterministic reference prove?

The fixture below freezes P-101 through P-106, adds an unauthorized exact-code match, and tests the important boundary behavior. It does not claim that the teaching dense adapter represents a real embedding model or that any strategy wins.

```python
def chunk(
    chunk_id: str,
    document_id: str,
    text: str,
    *,
    tenant: str = "northwind-procurement",
    version: str = "1",
    supplier: str = "Atlas Metals",
    document_type: str = "note",
) -> SourceChunk:
    return SourceChunk(
        chunk_id=chunk_id,
        tenant_id=tenant,
        document_id=document_id,
        document_version=version,
        source_digest=digest_text(f"{document_id}:{version}:{text}"),
        text=text,
        metadata=(("supplier", supplier), ("document_type", document_type)),
    )


FROZEN_CHUNKS = (
    chunk("P-101:1:0", "P-101", "Atlas Metals. Copper wire will ship after incoming-material inspection. Invoice terms: Net 30 after inspection approval.", document_type="confirmation"),
    chunk("P-102:1:0", "P-102", "Beacon Plastics. Product code PP-20. Invoice terms: Net 15 from receipt.", supplier="Beacon Plastics", document_type="confirmation"),
    chunk("P-103:1:0", "P-103", "Atlas Metals delivery update. Copper-wire shipment delayed while quality checks finish.", document_type="delivery_update"),
    chunk("P-104:1:0", "P-104", "Cedar Fasteners. Payment is due after the receiving team signs off on delivered bolts.", supplier="Cedar Fasteners", document_type="payment_note"),
    chunk("P-105:1:row-1", "P-105", "Schedule A row 1: product copper wire; quantity 1,000 kg; unit price USD 12.00.", document_type="framework_agreement"),
    chunk("P-105:1:section-3", "P-105", "Section 3 Invoicing: Invoice terms are Net 30 after inspection approval. This condition controls Schedule A.", document_type="framework_agreement"),
    chunk("P-106:1:0", "P-106", "Atlas Metals catalogue note. Product code CW-1000. Commercial name Copper wire, 1,000 kg coil. Quoted unit price USD 12.00.", document_type="catalogue"),
)
UNAUTHORIZED_CODE_MATCH = chunk(
    "P-secret:1:0", "P-secret", "Secret tenant product code CW-1000 with unrelated quote.", tenant="other-tenant",
)
ACCESS = StaticObjectAccessPolicy(
    frozenset(("analyst", item.tenant_id, item.document_id, item.document_version) for item in FROZEN_CHUNKS)
)
BM25 = BM25Config()
DENSE = DemoDenseAdapter()
FUSION = FusionConfig()


def corpus_for(request: RetrievalRequest, chunks: Sequence[SourceChunk] = FROZEN_CHUNKS) -> AuthorizedCorpus:
    return AuthorizedCorpus.build(request, chunks, ACCESS)


def expect_raises(expected: type[Exception], operation: Callable[[], object]) -> None:
    try:
        operation()
    except expected:
        return
    raise AssertionError(f"expected {expected.__name__}")


def test_identifier_token_and_duplicate_id_contracts() -> None:
    assert tokenize("CW-1000 / PO_2026/18") == ("cw-1000", "po_2026/18")
    duplicate = (*FROZEN_CHUNKS, FROZEN_CHUNKS[0])
    expect_raises(CorpusInvariantError, lambda: BM25Index.build(duplicate, token_contract=DEFAULT_TOKEN_CONTRACT, config=BM25))


def test_invalid_bm25_and_authorization_isolation() -> None:
    expect_raises(ConfigurationError, lambda: BM25Config(k1=0.0).fingerprint())
    request = RetrievalRequest("analyst", "CW-1000", top_k=3)
    baseline = corpus_for(request)
    with_secret = corpus_for(request, (*FROZEN_CHUNKS, UNAUTHORIZED_CODE_MATCH))
    baseline_index = baseline.bm25(DEFAULT_TOKEN_CONTRACT, BM25)
    secret_index = with_secret.bm25(DEFAULT_TOKEN_CONTRACT, BM25)
    assert baseline.chunks == with_secret.chunks
    assert baseline_index is not None and secret_index is not None
    assert baseline_index.document_frequencies == secret_index.document_frequencies
    assert baseline_index.average_document_length == secret_index.average_document_length
    assert baseline_index.score("CW-1000", FROZEN_CHUNKS[-1]) == secret_index.score("CW-1000", FROZEN_CHUNKS[-1])
    assert dense_candidates(request, baseline, DENSE) == dense_candidates(request, with_secret, DENSE)
    assert hybrid_candidates(request, baseline, baseline_index, DENSE, FUSION, candidate_depth=5) == hybrid_candidates(
        request,
        with_secret,
        secret_index,
        DENSE,
        FUSION,
        candidate_depth=5,
    )


def test_metadata_filter_manifest_and_candidate_depth() -> None:
    request = RetrievalRequest("analyst", "CW-1000", top_k=1, filters=(MetadataFilter("document_type", "catalogue"),))
    corpus = corpus_for(request)
    assert [item.document_id for item in corpus.chunks] == ["P-106"]
    expect_raises(ConfigurationError, lambda: AuthorizedCorpus.build(RetrievalRequest("analyst", "CW-1000", 1, (MetadataFilter("tenant_id", "other-tenant"),)), FROZEN_CHUNKS, ACCESS))
    expect_raises(
        ConfigurationError,
        lambda: corpus_for(
            RetrievalRequest(
                "analyst",
                "CW-1000",
                1,
                (
                    MetadataFilter("supplier", "Atlas Metals"),
                    MetadataFilter("supplier", "Beacon Plastics"),
                ),
            )
        ),
    )
    ordered_filters = (
        MetadataFilter("supplier", "Atlas Metals"),
        MetadataFilter("document_type", "catalogue"),
    )
    reversed_filters = tuple(reversed(ordered_filters))
    assert corpus_for(RetrievalRequest("analyst", "CW-1000", 1, ordered_filters)).partition_fingerprint == corpus_for(
        RetrievalRequest("analyst", "CW-1000", 1, reversed_filters)
    ).partition_fingerprint
    manifest = make_manifest(corpus, DEFAULT_TOKEN_CONTRACT, BM25, DENSE, FUSION, candidate_depth=2, top_k=1)
    require_compatible(manifest, manifest)
    incompatible = RetrievalManifest(**{**manifest.__dict__, "candidate_depth": 3})
    expect_raises(ManifestCompatibilityError, lambda: require_compatible(manifest, incompatible))
    index = corpus.bm25(DEFAULT_TOKEN_CONTRACT, BM25)
    full_corpus = corpus_for(RetrievalRequest("analyst", "CW-1000", top_k=1))
    full_index = full_corpus.bm25(DEFAULT_TOKEN_CONTRACT, BM25)
    expect_raises(
        ManifestCompatibilityError,
        lambda: sparse_candidates(request, corpus, full_index),
    )
    expect_raises(
        ConfigurationError,
        lambda: hybrid_candidates(request, corpus, index, DENSE, FUSION, candidate_depth=0),
    )


def test_rrf_contributors_ties_and_same_corpus_evaluation() -> None:
    request = RetrievalRequest("analyst", "approval before payment", top_k=2)
    corpus = corpus_for(request)
    index = corpus.bm25(DEFAULT_TOKEN_CONTRACT, BM25)
    assert index is not None
    sparse = sparse_candidates(RetrievalRequest("analyst", request.query_text, 4), corpus, index)
    dense = dense_candidates(RetrievalRequest("analyst", request.query_text, 4), corpus, DENSE)
    fused = reciprocal_rank_fusion((sparse, dense), FUSION, top_k=2)
    assert fused and all(candidate.contributors for candidate in fused)
    tied = reciprocal_rank_fusion(
        ((RankedCandidate(FROZEN_CHUNKS[1], 1.0, 1, "bm25"), RankedCandidate(FROZEN_CHUNKS[0], 1.0, 1, "dense")),),
        FUSION,
        top_k=2,
    )
    assert [candidate.chunk.chunk_id for candidate in tied] == ["P-101:1:0", "P-102:1:0"]
    cases = (EvaluationCase("code", RetrievalRequest("analyst", "CW-1000", 3), frozenset({"P-106:1:0"}), frozenset({"cw-1000"}), "identifier"),)
    returned = [candidate.chunk.chunk_id for candidate in sparse_candidates(cases[0].request, corpus_for(cases[0].request), corpus_for(cases[0].request).bm25(DEFAULT_TOKEN_CONTRACT, BM25))]
    assert 0.0 <= recall_at_k(returned, cases[0].relevant_chunk_ids) <= 1.0
    assert 0.0 <= precision_at_k(returned, cases[0].relevant_chunk_ids) <= 1.0
    assert 0.0 <= reciprocal_rank(returned, cases[0].relevant_chunk_ids) <= 1.0


def run_displayed_tests() -> None:
    test_identifier_token_and_duplicate_id_contracts()
    test_invalid_bm25_and_authorization_isolation()
    test_metadata_filter_manifest_and_candidate_depth()
    test_rrf_contributors_ties_and_same_corpus_evaluation()


run_displayed_tests()
```

The test suite shows that adding an unauthorized exact `CW-1000` chunk leaves the authorised corpus, BM25 statistics, and score unchanged. It also checks stable configuration fingerprints, filter allowlists, contributors, deterministic ties, and same-corpus metric bounds. It intentionally does not report a benchmark result.

## 9. Empty/weak outcomes, observability, and operational change

An authorized request can have an empty corpus after filters, no lexical matches, weak dense scores, or only obsolete evidence. Return an explicit empty or weak-result status with safe manifest/source provenance. Do not broaden permissions, silently alter the query, look in another tenant, or generate an answer to conceal the absence.

Observability should record aggregate counts and safe identifiers: access-denied/empty outcomes, filter fields (not sensitive values where prohibited), corpus/manifest fingerprint, retriever/fusion configuration ID, candidate depth, top-k, latency at a documented boundary, memory/index size, duplicate rate, and category-level evaluation regressions. Avoid raw source text, query text, unrestricted document IDs, vectors, aliases, credentials, and parser payloads in general logs.

Promotion is manual. Run deterministic contract tests and held-out evaluation before serving a new tokenizer, alias policy, BM25 parameter, dense artifact/runtime, filter/access partition, fusion weight, candidate depth, or top-k. A rollback selects the previous approved manifest and compatible corpus/index artifacts. It should be ordinary operational behavior, not an emergency prompt change.

## 10. Common failures

### “BM25 is exact, so it is correct.”

Exact matching depends on tokenization and source text. It does not resolve aliases, OCR, negation, active version, or contractual scope.

### “We can add raw sparse and dense scores.”

What shared meaning do the score scales have? Without an explicitly evaluated normalization/calibration contract, raw arithmetic only hides an arbitrary weighting decision.

### “Unauthorized chunks are hidden, so they cannot matter.”

Did they affect IDF, average length, dense candidate generation, fusion depth, timing, cache, or diagnostics? They must be absent before each of those operations.

### “RRF agreement proves relevance.”

RRF rewards rank agreement. Two retrievers can agree on generic invoice boilerplate, duplicated overlap chunks, or an outdated amendment.

### “A local dense model handles product codes.”

Which held-out identifier/abbreviation/OCR cases show that? Dense representations commonly need sparse lexical support for arbitrary identifiers.

## 11. Interview defense and active recall

**Why can dense retrieval perform poorly for product codes and abbreviations?**

They are often rare, arbitrary, semantically thin strings. Tokenization, pooling, and learned similarity may dilute or blur exact character identity, while nearby descriptive text dominates. Sparse retrieval preserves lexical terms and BM25 can weight rare identifiers through IDF. Hybrid retrieval lets both signals contribute but does not remove source/version validation.

**Why must authorization happen before BM25 scoring?**

BM25’s IDF and average length depend on the indexed corpus. Leaving forbidden chunks in statistics affects authorised rankings and leaks corpus information even if results are filtered later. Dense candidate generation, fusion, cache, and observability need the same restriction.

**Why use RRF rather than raw-score addition initially?**

Ranks avoid pretending BM25 and dense scores share a unit. RRF is simple and reproducible when candidate depth, rank constant, retriever weights, and tie rules are versioned. It still needs held-out evaluation and contributor provenance.

### Active recall

1. What behavior does the token contract control for `CW-1000`?
2. Which three BM25 components make a rare identifier useful without unbounded repetition?
3. Why is a metadata filter not authorization?
4. What retrieval artifacts can an unauthorized chunk influence if filtering is late?
5. What does RRF preserve that min–max raw-score fusion does not?
6. Why are non-default fusion weights a governed change?
7. What must a retrieval manifest include to reproduce a hybrid result?
8. Why is support completeness stricter than Recall@k?

### Answers

1. Whether the code is preserved, lowercased, split, or discarded, which determines lexical match behavior.
2. Term-frequency saturation, inverse document frequency, and document-length normalization.
3. It narrows records by allowed field/value predicates; only a trusted access policy decides whether the principal may read an object.
4. BM25 statistics, dense candidates, fusion contributors, timing, counts, caches, and diagnostics.
5. Rank evidence from each list without assuming raw score distributions are commensurate.
6. They change the relative influence of retrievers and require a rationale, development evidence, version, and rollback target.
7. Source/chunk snapshot, token/BM25/dense configuration, access partition/filter, fusion configuration, candidate depth, and top-k.
8. A relevant result can mention the topic; complete support needs all declared source evidence needed for review.

## 12. Exercises

1. Add an approved alias policy for `CW1000`, including original-token preservation, effective date, owner, false-match tests, and manifest versioning.
2. Add an unauthorized tenant with a rare exact supplier code. Verify it changes neither authorised BM25 statistics nor dense/fusion candidates.
3. Define a source-level duplicate policy for overlapping P-105 chunks. Measure its effect on duplicate rate, Recall@k, and support completeness on held-out labels.
4. Specify a governed non-default RRF-weight experiment: development/held-out split, candidate depth, metric suite, category failures, promotion threshold, and rollback manifest.
5. Implement an actual approved local dense adapter behind `DenseAdapter`; pin artifact/runtime/preprocessing/metric and compare it with the teaching fake without changing the sparse corpus.

## Primary documentation

- [Python 3.13 `dataclasses`](https://docs.python.org/3.13/library/dataclasses.html)
- [Python 3.13 `typing` and `Protocol`](https://docs.python.org/3.13/library/typing.html)
- [Python 3.13 `collections.Counter`](https://docs.python.org/3.13/library/collections.html#collections.Counter)
