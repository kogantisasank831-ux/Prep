---
layout: week
week: 7
phase: 2
status: approved
version: 1.1.0
last_reviewed: 2026-10-22
estimated_hours: 8
permalink: /weeks/week-07/
title: "Sparse and hybrid retrieval: preserve exact evidence and semantic recall"
description: Build an authorization-aware, reproducible sparse/dense retrieval boundary for procurement codes, names, commercial terms, and paraphrases.
summary: Continue the frozen procurement corpus from a versioned token contract and authorized BM25 corpus through provenance-preserving dense candidates, reciprocal-rank fusion, and held-out evaluation.
kicker_primary: Sparse and hybrid retrieval
kicker_secondary: Exact evidence plus semantic recall
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-07/beginner/
---

Test your understanding with the [Week 7 assessment]({{ '/assessments/week-07/' | relative_url }}): a random ten-question paper from 100 questions, including Python exercises on exact codes, BM25, authorized corpus scope and reciprocal rank fusion.

## Your route through Week 7

By the end of this week, you should be able to explain a BM25 score, preserve an exact product code through tokenization, combine two ranked lists with RRF, and diagnose a hybrid result from its contributors. You will compare sparse, dense, and hybrid retrieval on one frozen collection, including code, supplier, commercial-term, and paraphrase queries.

Bring Week 5's embedding/ranking ideas and Week 6's source identities, chunk boundaries, and metadata. The main implementation uses immutable dataclasses, protocols, mappings, and explicit boundary errors. Start with the [beginner lesson]({{ '/weeks/week-07/beginner/' | relative_url }}) if you want to work through the ranking formulas before the full contracts.

| Time | Work | What you should produce |
| --- | --- | --- |
| Hour 1 | Try a code query and a paraphrase against the same evidence | A prediction about which signal will help |
| Hours 2–3 | Work through tokenization and BM25; calculate one score by hand | A checked rare-term/length-normalization example |
| Hour 4 | Trace authorization and exact metadata predicates | The eligible corpus shared by both paths |
| Hour 5 | Calculate min–max and RRF examples | A contributor table you can explain |
| Hours 6–7 | Run the lab, inspect failures, change one parameter | A measured comparison and category breakdown |
| Hour 8 | Complete the exercises and interview explanation | A short retrieval decision note |

Ask this as you read each result: “Did this candidate preserve the identifier or condition the question depends on?” A good topic match can still lose the decisive detail.

## P-107 changes what “relevant” must preserve

P-101 through P-105 have immutable, traceable chunks from Week 6. P-106 remains the uncertain OCR fixture and stays out of the accepted index. A separate P-107 catalogue note adds an exact commercial identifier:

```text
P-107 | Atlas Metals catalogue note | version 1
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

Sparse and dense systems observe different signals, produce incompatible score distributions, and can fail independently. They must operate on the same authorised frozen corpus, record their configuration, return source lineage, and be compared against held-out relevance/support labels.

Follow the request in this order:

1. Derive the principal from trusted authentication context and apply its object grants.
2. Apply the allowed metadata predicates to form the shared eligible corpus.
3. Rank that corpus independently with versioned BM25 and dense scorers.
4. Fuse accepted ranked candidates, retaining contributor ranks and raw scores.
5. Return source-linked candidates or an empty outcome for review.


Retrieval relevance is not factual truth. A `CW-1000` match may be superseded, unauthorised for the current caller, or attached to a different agreement. No code below writes to a procurement system, generates an answer, or treats a ranking score as permission to act.

## 1. Make the keyword and lexical contract explicit before building BM25

### What exactly is an “exact” product-code match?

Sparse retrieval begins with a tokenizer. It maps visible text into terms, so its behavior decides whether `CW-1000` survives as one token, becomes `cw` plus `1000`, or disappears. Tokenization, normalization, aliases, and BM25 parameters are retrieval behavior; they belong in a versioned configuration and manifest.

For this corpus, preserve internal hyphens, underscores, and slashes:

```text
CW-1000       -> cw-1000
PO_2026/18    -> po_2026/18
Net 30        -> net, 30
```

That is intentionally conservative. `CW1000` does not match `CW-1000`, and `CW-100O` with letter O does not match zero. An alias table could map a known supplier code variant to a canonical token, but aliases create false-positive risk, must preserve the original text, need an owner and effective version, and require evaluation against exact-code/OCR cases. Do not normalize punctuation away merely because it looks convenient.

```python
"""Exact sparse/dense/fusion contracts for the Week 7 teaching lab."""

from __future__ import annotations


from collections import Counter, defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass
from hashlib import sha256
from math import isfinite, log
import json
import platform
from types import MappingProxyType
import re
from typing import Protocol, Self


TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:[-_/][a-z0-9]+)*")
MANIFEST_SCHEMA = "procurement-hybrid-retrieval/1.1.0"


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


def tokenize(
    text: str, contract: TokenContract = DEFAULT_TOKEN_CONTRACT
) -> tuple[str, ...]:
    contract.fingerprint()
    if contract != DEFAULT_TOKEN_CONTRACT:
        raise ConfigurationError("reference tokenizer does not implement this contract")
    if not isinstance(text, str) or len(text) > 4000:
        raise ConfigurationError("tokenizer requires bounded text")
    try:
        text.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ConfigurationError("tokenizer requires valid UTF-8 text") from exc
    return tuple(TOKEN_PATTERN.findall(text.lower()))


def metadata_values(chunk: SourceChunk) -> dict[str, str]:
    return dict(chunk.metadata)
```

The reference tokenizer is local and deterministic. It does not correct typos, do OCR, expand abbreviations, or recognize company aliases. Those are material retrieval-policy changes, not harmless preprocessing. Keep the original document text and the token contract fingerprint with every index build so a reviewer can explain what matched.

### Aliases and normalization need the same evidence discipline as source data

An alias such as `CW1000 → CW-1000` may improve a lookup while also collapsing two distinct supplier codes. `AM` can identify more than one company; an OCR correction can turn an uncertain value into an apparently exact token. Preserve the original text and tokens alongside any canonical form.

Treat aliases as versioned retrieval data. Record the target, source/evidence, owner, effective range, tenant/supplier scope, and policy version. Test positive and false matches before changing either the document or query representation. If no approved mapping exists, retain the query and expose the lack of an exact lexical match for authorized review.

Query-time expansion and document-time expansion have different effects. The latter changes index statistics and storage; applying both can double-count a term. Compare code, supplier, and commercial-term queries separately. Include alias provenance in results, safe diagnostics, manifests, and labels so an operator can distinguish literal matching from assisted retrieval and explain regressions. An unversioned UI rewrite would hide that distinction.

## 2. BM25 is a sparse ranking formula with corpus-dependent behavior

### Why does `CW-1000` deserve more credit than `invoice`?

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
    algorithm: str = "log1p-idf-unique-query/v1"

    def fingerprint(self) -> str:
        if self.algorithm != "log1p-idf-unique-query/v1":
            raise ConfigurationError("unsupported BM25 algorithm contract")
        if (
            type(self.k1) not in (int, float)
            or type(self.b) not in (int, float)
            or not isfinite(self.k1)
            or not isfinite(self.b)
            or self.k1 <= 0
            or not 0 <= self.b <= 1
        ):
            raise ConfigurationError("BM25 requires finite k1 > 0 and b in [0, 1]")
        return digest_text(json.dumps(asdict(self), sort_keys=True))


@dataclass(frozen=True)
class BM25Index:
    chunks: tuple[SourceChunk, ...]
    term_frequencies: Mapping[str, Mapping[str, int]]
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
        token_contract.fingerprint()
        validate_chunks(chunks)
        if not chunks:
            raise CorpusInvariantError("BM25 requires at least one authorised chunk")
        frequencies: dict[str, Mapping[str, int]] = {}
        df: Counter[str] = Counter()
        lengths: dict[str, int] = {}
        for chunk in chunks:
            terms = tokenize(chunk.text, token_contract)
            if not terms:
                raise CorpusInvariantError("chunks must contain at least one token")
            counts = Counter(terms)
            frequencies[chunk.chunk_id] = MappingProxyType(dict(counts))
            lengths[chunk.chunk_id] = len(terms)
            df.update(counts.keys())
        return cls(
            tuple(chunks),
            MappingProxyType(frequencies),
            MappingProxyType(dict(df)),
            MappingProxyType(lengths),
            sum(lengths.values()) / len(lengths),
            token_contract,
            config,
        )

    def score(self, query_text: str, chunk: SourceChunk) -> float:
        if chunk not in self.chunks:
            raise ManifestCompatibilityError("scored chunk differs from index snapshot")
        frequencies = self.term_frequencies[chunk.chunk_id]
        length = self.document_lengths[chunk.chunk_id]
        total = 0.0
        # Query terms are unique in this version; repetition is not a hidden boost.
        for term in dict.fromkeys(tokenize(query_text, self.token_contract)):
            frequency = frequencies.get(term, 0)
            if frequency == 0:
                continue
            df = self.document_frequencies[term]
            idf = log(1.0 + (len(self.chunks) - df + 0.5) / (df + 0.5))
            norm = (
                1
                - self.config.b
                + self.config.b * length / self.average_document_length
            )
            k1 = self.config.k1
            # Equivalent ratio avoids overflow for a very large finite k1.
            tf_weight = (
                frequency * (1 + 1 / k1) / (frequency / k1 + norm)
                if k1 >= 1
                else frequency * (1 + k1) / (frequency + k1 * norm)
            )
            total += idf * tf_weight
        return total
```

Try a tiny calculation before inspecting the larger fixture. Suppose there are two chunks: `CW-1000` and `invoice invoice invoice`. Then `N=2`, `df(CW-1000)=1`, `avgdl=2`, and the code chunk has length 1. With `k1=1.2` and `b=0.75`, its score is `ln(2) × 2.2 / (1 + 1.2 × (0.25 + 0.75 × 1/2))`, approximately **0.8714**. The score measures a lexical ranking signal, not a probability.

The implementation uses a positive `log(1 + …)` IDF variant and unique query terms, so repeating `CW-1000` in the query does not create a hidden boost. It is an inspectable BM25 variant, not a promise of identical scores to a search engine: analyzers, query-term handling, fields, length norms, synonym overlap, and shard statistics can differ. The default `k1` and `b` are starting parameters to evaluate.

The formula also makes a security/reproducibility point: IDF and `avgdl` are corpus statistics. If unauthorised chunks remain in the index, they influence scores even when final display filters them away. Under this lesson’s partition-local statistics contract, that can expose private-corpus influence and makes scores depend on evidence outside the caller’s eligible snapshot. A separate design using approved public background statistics would need to declare that policy explicitly.

## 3. Build the authorised corpus before either retriever scores

### What may an unauthorized exact match influence?

The reference requires denied text to affect no BM25 term counts, IDF, average length, dense score, or fusion contributor. It constructs a small authorized corpus per request before either scorer runs. Its partition key binds the trusted principal, eligible representation, and canonical metadata predicates. This provides a clear correctness baseline for the lesson; it is not a scalable serving design or a constant-time guarantee. Traversal, grant checks, total request timing, caches, and infrastructure still require their own assessment.

Metadata filters are typed, allowlisted predicates. They can narrow a query to a supplier or document type, but they are not authorization. The access policy derives object visibility from a trusted principal. A caller cannot obtain another tenant by adding a metadata filter.

```python
def validate_request(request: RetrievalRequest) -> None:
    if (
        not isinstance(request.principal_id, str)
        or not request.principal_id.strip()
        or len(request.principal_id) > 128
        or not isinstance(request.query_text, str)
        or not request.query_text.strip()
        or len(request.query_text) > 1000
        or type(request.top_k) is not int
        or request.top_k < 1
        or request.top_k > 256
    ):
        raise ConfigurationError(
            "request requires bounded principal/query and integer top_k in [1, 256]"
        )
    try:
        request.query_text.encode("utf-8")
        request.principal_id.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ConfigurationError("request requires valid UTF-8 text") from exc
    validate_filters(request.filters)


def validate_chunks(chunks: Sequence[SourceChunk]) -> None:
    if len(chunks) > 256 or len({chunk.chunk_id for chunk in chunks}) != len(chunks):
        raise CorpusInvariantError("corpus must have at most 256 unique chunk IDs")
    for chunk in chunks:
        fields = (
            chunk.chunk_id,
            chunk.tenant_id,
            chunk.document_id,
            chunk.document_version,
            chunk.source_digest,
        )
        if (
            any(
                not isinstance(value, str) or not value.strip() or len(value) > 256
                for value in fields
            )
            or not isinstance(chunk.text, str)
            or not chunk.text.strip()
            or len(chunk.text) > 4000
            or len(chunk.metadata) > 32
            or len(dict(chunk.metadata)) != len(chunk.metadata)
            or any(
                not isinstance(k, str)
                or not k.strip()
                or not isinstance(v, str)
                or not v.strip()
                or len(k) > 100
                or len(v) > 1000
                for k, v in chunk.metadata
            )
        ):
            raise CorpusInvariantError(
                "chunks require bounded identity, text, and unique metadata"
            )
        try:
            for value in (
                *fields,
                chunk.text,
                *(value for pair in chunk.metadata for value in pair),
            ):
                value.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise CorpusInvariantError("chunks require valid UTF-8 text") from exc


def require_request_corpus(request: RetrievalRequest, corpus: AuthorizedCorpus) -> None:
    validate_request(request)
    if (
        request.principal_id != corpus.principal_id
        or tuple(sorted(request.filters, key=lambda f: f.field)) != corpus.filters
    ):
        raise ManifestCompatibilityError(
            "request principal/filters differ from authorised corpus"
        )


ALLOWED_FILTER_FIELDS = frozenset({"supplier", "document_type"})


class AccessPolicy(Protocol):
    def can_read(self, principal_id: str, chunk: SourceChunk) -> bool: ...


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
    if len(filters) > len(ALLOWED_FILTER_FIELDS) or any(
        filter_.field not in ALLOWED_FILTER_FIELDS
        or not isinstance(filter_.value, str)
        or not filter_.value.strip()
        or len(filter_.value) > 200
        for filter_ in filters
    ):
        raise ConfigurationError(
            "metadata filters must use bounded allowlisted equality predicates"
        )
    if len({filter_.field for filter_ in filters}) != len(filters):
        raise ConfigurationError("metadata filter fields must be unique")


@dataclass(frozen=True)
class AuthorizedCorpus:
    principal_id: str
    chunks: tuple[SourceChunk, ...]
    partition_fingerprint: str
    filters: tuple[MetadataFilter, ...] = ()

    @classmethod
    def build(
        cls,
        request: RetrievalRequest,
        chunks: Sequence[SourceChunk],
        access_policy: AccessPolicy,
    ) -> Self:
        validate_request(request)
        if len(chunks) > 256:
            raise CorpusInvariantError("reference corpus exceeds 256 chunks")
        authorised = tuple(
            chunk
            for chunk in chunks
            if access_policy.can_read(request.principal_id, chunk)
        )
        validate_chunks(authorised)
        eligible = tuple(
            chunk
            for chunk in authorised
            if all(
                metadata_values(chunk).get(f.field) == f.value for f in request.filters
            )
        )
        filters = tuple(sorted(request.filters, key=lambda f: f.field))
        partition = digest_text(
            json.dumps(
                {
                    "principal": request.principal_id,
                    "corpus": corpus_fingerprint(eligible),
                    "filters": [asdict(f) for f in filters],
                },
                sort_keys=True,
            )
        )
        return cls(request.principal_id, eligible, partition, filters)

    def bm25(
        self, token_contract: TokenContract, config: BM25Config
    ) -> BM25Index | None:
        token_contract.fingerprint()
        config.fingerprint()
        return (
            BM25Index.build(self.chunks, token_contract=token_contract, config=config)
            if self.chunks
            else None
        )
```

For a larger system, common correct alternatives include per-tenant/authorisation-partitioned indexes, pre-filtered shard routing, or an index/filter design whose candidate generation itself enforces object visibility. The invariant remains: forbidden chunks cannot influence retrieval statistics or candidate scoring. “Search everything then hide the result” is not an access control design.

### Scaling the authorization boundary without weakening it

Building a fresh exact BM25 index for every authorised request is a correctness reference, not a throughput recommendation. At larger scale, the partition selected before search must still be a trusted representation of the caller's visible corpus. A per-tenant index is simple when every object belongs to exactly one tenant; it is insufficient when documents can be shared selectively across tenants. Object-level grants may require a secure pre-filter, a dedicated access partition, or a materialized authorised view with carefully designed invalidation.

The same discipline applies to dense candidates. A vector index that generates neighbours across all tenants and removes them afterward has already allowed forbidden vectors to affect traversal, timing, cache state, and potentially result-count behavior. Design the storage/index boundary so it can enforce the applicable access partition before candidate search, then test negative cases under realistic cardinality and cache conditions.

Metadata filters are also part of the attack surface. The reference only permits `supplier` and `document_type`, with exact equality over stored values. Adding free-form fields, prefix search, ranges, or user-defined expressions broadens the query contract and can create enumeration paths. Give each predicate an explicit semantic meaning, type, authorization implication, and manifest identity. Filter values themselves can be commercially sensitive; logs should record a safe policy identifier rather than unrestricted query payloads.

## 4. Dense and sparse signals complement, but do not validate each other

### When does each retriever fail first?

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
    minimum_score: float = 0.0
    dimension: int | None = None

    def fingerprint(self) -> str:
        if self.dimension is not None and (
            type(self.dimension) is not int or self.dimension < 1
        ):
            raise ConfigurationError(
                "dense dimension must be a positive integer when supplied"
            )
        if not all(
            isinstance(value, str) and value.strip()
            for value in (
                self.adapter_id,
                self.artifact_digest,
                self.runtime_id,
                self.preprocessing_version,
                self.metric,
            )
        ):
            raise ConfigurationError("dense configuration fields must be non-empty")
        if type(self.minimum_score) not in (int, float) or not isfinite(
            self.minimum_score
        ):
            raise ConfigurationError("dense minimum score must be finite")
        return digest_text(json.dumps(asdict(self), sort_keys=True))


class DenseAdapter(Protocol):
    @property
    def config(self) -> DenseConfig: ...

    def score(self, query_text: str, chunk_text: str) -> float: ...


@dataclass(frozen=True)
class DemoDenseAdapter:
    config: DenseConfig = DenseConfig(
        adapter_id="demo-procurement-features",
        artifact_digest="synthetic-only",
        runtime_id=f"python-stdlib/{platform.python_version()}",
        preprocessing_version="identifier-dropping-positive-candidates/v2",
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
        return len(query_features & chunk_features) / len(
            query_features | chunk_features
        )
```

## 5. Preserve raw ranks and contributor provenance through fusion

### Why can’t we simply add BM25 and dense scores?

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
            type(self.rank_constant) is not int
            or self.rank_constant <= 0
            or not self.weights
            or any(
                not name
                or type(weight) not in (int, float)
                or not isfinite(weight)
                or weight <= 0
                for name, weight in self.weights
            )
        ):
            raise ConfigurationError(
                "RRF requires an integer rank constant and positive finite weights"
            )
        if len({name for name, _ in self.weights}) != len(self.weights):
            raise ConfigurationError("RRF retriever names must be unique")
        return digest_text(
            json.dumps(
                {"rank_constant": self.rank_constant, "weights": sorted(self.weights)},
                sort_keys=True,
            )
        )


def rank_candidates(
    scores: Iterable[tuple[SourceChunk, float]],
    *,
    top_k: int,
    retriever: str,
    minimum_score: float = 0.0,
) -> tuple[RankedCandidate, ...]:
    if type(top_k) is not int or top_k < 1 or not retriever:
        raise ValueError("positive integer top_k and retriever name are required")
    if type(minimum_score) not in (int, float) or not isfinite(minimum_score):
        raise ConfigurationError("score floor must be finite")
    items = tuple(scores)
    if any(
        type(score) not in (int, float) or not isfinite(score) for _, score in items
    ):
        raise ConfigurationError("candidate scores must be finite numbers")
    if len({chunk.chunk_id for chunk, _ in items}) != len(items):
        raise CorpusInvariantError("ranked candidates must have unique IDs")
    ordered = sorted(
        (item for item in items if item[1] > minimum_score),
        key=lambda item: (-item[1], item[0].chunk_id),
    )[:top_k]
    return tuple(
        RankedCandidate(chunk, score, rank, retriever)
        for rank, (chunk, score) in enumerate(ordered, 1)
    )


def sparse_candidates(
    request: RetrievalRequest, corpus: AuthorizedCorpus, index: BM25Index | None
) -> tuple[RankedCandidate, ...]:
    require_request_corpus(request, corpus)
    if not corpus.chunks and index is None:
        return ()
    if index is None or index.chunks != corpus.chunks:
        raise ManifestCompatibilityError(
            "BM25 index corpus differs from authorised corpus"
        )
    return rank_candidates(
        ((chunk, index.score(request.query_text, chunk)) for chunk in corpus.chunks),
        top_k=request.top_k,
        retriever="bm25",
    )


def dense_candidates(
    request: RetrievalRequest, corpus: AuthorizedCorpus, adapter: DenseAdapter
) -> tuple[RankedCandidate, ...]:
    require_request_corpus(request, corpus)
    config = adapter.config
    config.fingerprint()
    scores = tuple(
        (chunk, adapter.score(request.query_text, chunk.text))
        for chunk in corpus.chunks
    )
    if adapter.config != config:
        raise ManifestCompatibilityError("dense configuration changed during scoring")
    return rank_candidates(
        scores,
        top_k=request.top_k,
        retriever="dense",
        minimum_score=config.minimum_score,
    )


def min_max_normalize(scores: Mapping[str, float]) -> dict[str, float]:
    if not scores:
        return {}
    if any(
        type(value) not in (int, float) or not isfinite(value)
        for value in scores.values()
    ):
        raise ConfigurationError("normalization requires finite numeric scores")
    lower, upper = min(scores.values()), max(scores.values())
    if lower == upper:
        return {key: 0.0 for key in scores}
    # Scale first if subtracting extreme signed values would overflow.
    span = upper - lower
    if isfinite(span):
        return {key: (value - lower) / span for key, value in scores.items()}
    scale = max(abs(lower), abs(upper))
    lo, hi = lower / scale, upper / scale
    return {key: (value / scale - lo) / (hi - lo) for key, value in scores.items()}


def reciprocal_rank_fusion(
    ranked_lists: Sequence[Sequence[RankedCandidate]],
    config: FusionConfig,
    *,
    top_k: int,
) -> tuple[FusedCandidate, ...]:
    if type(top_k) is not int or top_k < 1:
        raise ValueError("top_k must be a positive integer")
    weights = dict(config.weights)
    config.fingerprint()
    fused_scores: defaultdict[str, float] = defaultdict(float)
    chunks: dict[str, SourceChunk] = {}
    contributors: defaultdict[str, list[Contributor]] = defaultdict(list)
    seen_contributors: set[tuple[str, str]] = set()
    ranks_by_retriever: defaultdict[str, set[int]] = defaultdict(set)
    for ranked_list in ranked_lists:
        for candidate in ranked_list:
            if candidate.retriever not in weights:
                raise ConfigurationError("fusion received an unconfigured retriever")
            if (
                type(candidate.rank) is not int
                or candidate.rank <= 0
                or type(candidate.score) not in (int, float)
                or not isfinite(candidate.score)
            ):
                raise ConfigurationError(
                    "fusion candidates require positive ranks and finite scores"
                )
            contribution_key = (candidate.retriever, candidate.chunk.chunk_id)
            if contribution_key in seen_contributors:
                raise ConfigurationError(
                    "fusion received a duplicate retriever/chunk contribution"
                )
            seen_contributors.add(contribution_key)
            if candidate.rank in ranks_by_retriever[candidate.retriever]:
                raise ConfigurationError("retriever ranks must be unique")
            ranks_by_retriever[candidate.retriever].add(candidate.rank)
            existing_chunk = chunks.get(candidate.chunk.chunk_id)
            if existing_chunk is not None and existing_chunk != candidate.chunk:
                raise CorpusInvariantError(
                    "one chunk ID resolved to conflicting source chunks"
                )
            fused_scores[candidate.chunk.chunk_id] += weights[candidate.retriever] / (
                config.rank_constant + candidate.rank
            )
            chunks[candidate.chunk.chunk_id] = candidate.chunk
            contributors[candidate.chunk.chunk_id].append(
                Contributor(candidate.retriever, candidate.rank, candidate.score)
            )
    if any(
        ranks != set(range(1, len(ranks) + 1)) for ranks in ranks_by_retriever.values()
    ):
        raise ConfigurationError("retriever ranks must be contiguous from one")
    if any(not isfinite(score) for score in fused_scores.values()):
        raise ConfigurationError("fusion score exceeded finite range")
    ordered = sorted(fused_scores.items(), key=lambda item: (-item[1], item[0]))[:top_k]
    return tuple(
        FusedCandidate(
            chunk=chunks[chunk_id],
            score=score,
            rank=rank,
            contributors=tuple(
                sorted(contributors[chunk_id], key=lambda item: item.retriever)
            ),
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
    if (
        type(candidate_depth) is not int
        or candidate_depth < request.top_k
        or candidate_depth > 256
    ):
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

Before fusion, the reference admits only sparse scores strictly above zero and dense scores strictly above the floor in `DenseConfig` (zero for the teaching scorer). A no-match chunk therefore cannot gain an RRF vote just because it was padded into a top-k list. For a real cosine adapter, zero is a declared starting floor, not a calibrated relevance threshold; valid cosine similarities can be negative. Choose a threshold using development evidence and report missed positives. Unsupported ASCII tokenization, no positive match, and an empty authorized corpus are distinguishable causes of an empty list.

For equal weights and rank constant 60, a chunk at sparse rank 1 and dense rank 3 receives `1/61 + 1/63 ≈ 0.032266`. A chunk at rank 1 in only one list gets `1/61 ≈ 0.016393`. RRF discards the original score gaps: rank 1 beats rank 2 by the same rule even if their raw scores are nearly equal. The rank constant is separate from output `top_k`; candidate depth limits what the fusion can ever see.

The normalization helper rejects nonfinite/bool values and handles extreme signed scores without subtraction overflow. It maps an all-equal list to zeros by an explicit convention. That convention supplies no evidence that an equal-score candidate is relevant.

Contributor ranks and raw scores let an operator diagnose an RRF result: “P-107 appeared because BM25 ranked it first and dense did not contribute,” rather than inventing a misleading combined meaning. Keep raw scores internal/authorised where they may reveal corpus statistics; a user-facing result normally needs source provenance and a safe explanation of the retrieval path, not unrestricted diagnostics.

## 6. Record the whole retrieval configuration in one manifest

### What changed if a hybrid result changes tomorrow?

Source/chunk snapshot, token contract, BM25 parameters, dense adapter configuration, access partition/filter, fusion policy, candidate depth, and top-k all affect the candidate set. A manifest turns those hidden inputs into explicit compatibility checks. The corpus fingerprint includes actual chunk text and metadata, not just a supplied source digest. A text change with a stale digest still changes the fingerprint. BM25 parameter fingerprints preserve full numeric values rather than rounding distinct settings to the same string. These are compatibility checks against trusted records, not signatures or proof of source authenticity.

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
        if (
            self.schema_version != MANIFEST_SCHEMA
            or type(self.candidate_depth) is not int
            or type(self.top_k) is not int
            or not 1 <= self.top_k <= self.candidate_depth <= 256
        ):
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
    """Bind actual chunk text and metadata as well as externally supplied source IDs."""
    records = [
        {**asdict(chunk), "metadata": sorted(chunk.metadata)}
        for chunk in sorted(chunks, key=lambda c: c.chunk_id)
    ]
    return digest_text(
        json.dumps(records, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
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
    tokenize("", token_contract)
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


def require_compatible(
    expected: RetrievalManifest, observed: RetrievalManifest
) -> None:
    if expected.fingerprint() != observed.fingerprint():
        raise ManifestCompatibilityError(
            "retrieval manifest differs from the requested contract"
        )
```

Build a new manifest when source/chunk policy, tokenization, alias policy, BM25 parameters, dense artifact/runtime/preprocessing/metric, metadata filtering/access partition, fusion weights, candidate depth, or top-k changes. Promotion is manual after invariant tests and held-out evaluation. Rollback selects a prior immutable manifest and its compatible corpus/index artifacts; it does not mutate old chunks or mix new dense vectors with an old token policy.

## 7. Compare sparse, dense, and hybrid on the same frozen evidence

### What is a fair comparison?

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

No metric proves factual correctness. The P-107 price still needs source/version review. No average should hide a catastrophic code or tenant-isolation failure. Record parser/chunk manifest, model artifact/runtime, hardware, local measurement boundary, and label version with every result. Do not claim a benchmark score or winner until the governed experiment runs.

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


def precision_at_k(
    returned_ids: Sequence[str], relevant_ids: frozenset[str], *, k: int
) -> float:
    if type(k) is not int or k < 1 or len(set(returned_ids)) != len(returned_ids):
        raise ValueError("positive k and unique ranking IDs are required")
    return len(set(returned_ids[:k]) & relevant_ids) / k


def reciprocal_rank(returned_ids: Sequence[str], relevant_ids: frozenset[str]) -> float:
    for rank, chunk_id in enumerate(returned_ids, start=1):
        if chunk_id in relevant_ids:
            return 1.0 / rank
    return 0.0


def support_complete(chunks: Sequence[SourceChunk], atoms: frozenset[str]) -> bool:
    source_text = "\n".join(chunk.text.lower() for chunk in chunks)
    return all(atom.lower() in source_text for atom in atoms)
```

`nDCG` supports binary or graded relevance. The lab uses a written direct-support rule and binary nDCG; a graded experiment needs a separately defined scale. Precision in the runnable lab divides by **requested k**, including short or empty lists. Recall, reciprocal rank, and nDCG are null when a query has no labelled relevant chunks. The three compact recall/rank helpers above assume an already selected top-k list; the lab reuses Week 5's validated metric implementation for all reported results. Support completeness is stricter than relevance: for the P-105 question, it may require the table row, `Net 30 after inspection approval`, and the cross-reference to Schedule A. It evaluates reviewable evidence, not generated prose.

### Read evaluation metrics as a decision record, not a leaderboard

Define a query and relevance guide before tuning token aliases, `k1`, `b`, dense adapters, candidate depth, or fusion weights. A useful corpus has direct positives, lexical distractors, paraphrases, product-code variants, supplier-name collisions, numbers/units, negation, expired amendments, OCR-like character errors, and tenant-denied records. Preserve label provenance and adjudication notes: a disagreement about whether P-101 or P-107 is relevant to a catalogue query may reflect an unresolved business meaning, not a model failure.

Split documents by family or time where possible. A version-2 amendment that repeats version-1 wording should not sit in held-out evaluation if the model, alias rules, or chunk policy was tuned on version 1. The same applies to duplicate overlapping chunks: if a labelled phrase appears in many chunks, aggregate or group evaluation carefully so repeated copies do not manufacture apparent recall. Freeze the source/chunk manifest and access partition for all paths in a comparison. Sparse, dense, and hybrid cannot be compared fairly if one sees a different corpus.

Report both aggregate and subgroup behavior. For example, a hybrid policy may improve average Recall@10 but regress on `CW-1000`-style identifiers, `Net 15` versus `Net 30` commercial distinctions, or a tenant with only short documents. Review category failures before promotion. A single mean can hide a retrieval boundary that is unacceptable for one important query class.

Latency, cost, and memory need declared boundaries too. Record whether latency begins before or after authorization, whether it includes local embedding, BM25 construction, fusion, serialization, and cache lookup, plus corpus cardinality, vector dimension, hardware, concurrency, and cold/warm state. Separate raw chunk text/metadata storage, sparse postings/statistics, dense vectors, and index overhead. A configuration that wins one offline metric but exceeds the operator's local resource budget or harms p99 latency may not be deployable.

Finally, define the empty/weak-result policy before evaluation. An empty authorised corpus after a filter, a zero-term BM25 query, and a low-confidence semantic candidate are different operational states. Preserve a safe status, manifest fingerprint, and allowed source provenance where applicable. Do not broaden filters, access another tenant, silently rewrite the query, or fabricate a conclusion to make the interface look helpful.

## 8. Cumulative fixtures and contract tests

### What can a deterministic reference prove?

The shortened fixture passages below form a self-contained teaching snapshot for these four contract tests. They include the code and supplier text directly so each test is easy to inspect. Keep this illustrative snapshot separate from Week 6's immutable records; do not overwrite a source version with the shortened text. The runnable comparison in Section 13 instead imports Week 6's actual parsed sources and chunk IDs, with new code notes as P-107/P-108. The tests below also add an unauthorized exact-code match and check the boundary behavior. It does not claim that the teaching dense adapter represents a real embedding model or that any strategy wins.

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
    chunk("P-107:1:0", "P-107", "Atlas Metals catalogue note. Product code CW-1000. Commercial name Copper wire, 1,000 kg coil. Quoted unit price USD 12.00.", document_type="catalogue"),
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
    assert [item.document_id for item in corpus.chunks] == ["P-107"]
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
    cases = (EvaluationCase("code", RetrievalRequest("analyst", "CW-1000", 3), frozenset({"P-107:1:0"}), frozenset({"cw-1000"}), "identifier"),)
    returned = [candidate.chunk.chunk_id for candidate in sparse_candidates(cases[0].request, corpus_for(cases[0].request), corpus_for(cases[0].request).bm25(DEFAULT_TOKEN_CONTRACT, BM25))]
    assert 0.0 <= recall_at_k(returned, cases[0].relevant_chunk_ids) <= 1.0
    assert 0.0 <= precision_at_k(returned, cases[0].relevant_chunk_ids, k=cases[0].request.top_k) <= 1.0
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

An authorized request can have an empty corpus after filters, no lexical matches, weak dense scores, or only obsolete evidence. The local API returns an empty tuple when no candidate exceeds its score floor; it does not implement a calibrated weak-result classifier or automatic source-currentness rule. Return an explicit empty or weak-result status with safe manifest/source provenance. Do not broaden permissions, silently alter the query, look in another tenant, or generate an answer to conceal the absence.

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

The authorization answers below refer to the lab's partition-local statistics and trusted-principal contract. The deterministic tests prove invariance of its eligible records, scores, and fusion output when a denied distractor is added; they do not prove constant-time execution or production side-channel resistance.

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

## 13. Run the sparse, dense, and hybrid comparison

Open the [Week 7 lab](https://github.com/kogantisasank831-ux/Prep/tree/main/labs/week_07). From the repository root in its Python environment:

```shell
python -m pip install -r requirements-dev.txt
python -m labs.week_07.compare --summary
python -m labs.week_07.compare
python -m pytest tests/test_week07_hybrid.py -q
```

The default run makes no network/model call and needs no credential or GPU. It reuses the exact accepted P-101–P-105 source text, versions, structure-chunk IDs, and locations from Week 6. It adds the P-107 catalogue note for `CW-1000` and a separate P-108 Beacon note for `PP-20`. P-106 remains the OCR-review fixture. The result is seven accepted documents and eleven searchable chunks. Supplier/document-type labels are explicit curated synthetic metadata, recorded under `curated-synthetic-fixture-labels/1.0.0`; they are not a claim of automatic entity extraction.

The fourteen queries are visible `practice` data. Ten have direct evidence labels, and four cover an unmapped alias, an OCR-like code variant, an undefined abbreviation, and an identifier found only in a denied tenant. Those four queries have no labelled support. They do not simulate every negative or authorization failure, and they are not held-out evidence for choosing parameters.

### Keep the comparison controlled

For each query, all three modes see the same authorized and metadata-filtered corpus. Exact supplier and document-type filters narrow it before BM25 statistics and dense scoring. The source/query fingerprints, token contract, BM25 algorithm/parameters, dense configuration, metadata policy, fusion configuration, top-k, and candidate depth appear in the report. The unfiltered corpus fingerprint stays fixed; per-query fingerprints change when the declared predicates change.

Sparse and dense baselines return at most three accepted candidates. Hybrid takes at most five accepted candidates from each path and fuses down to three, using equal weights and rank constant 60. That larger union is part of the hybrid configuration and extra work, not a free quality gain; the standalone lists are the first three of the same scoring rules. Ties use chunk ID. Both paths drop nonpositive teaching scores rather than padding lists, and raw contributor scores/ranks remain available in the full output.

The dense path is the identifier-dropping feature/Jaccard scorer shown earlier. It deliberately has no feature for `CW-1000` or `PP-20`. A zero recall on those queries demonstrates the fake's construction, not a measured failure rate of embedding models. Real encoders can behave differently in both directions.

### Executed teaching results

The [sample summary](https://github.com/kogantisasank831-ux/Prep/blob/main/labs/week_07/sample-comparison.json) contains these default results, rounded here:

| Retrieval mode | Macro P@3 | Macro R@3 | MRR@3 | Binary nDCG@3 | Complete-support fraction | Empty queries |
| --- | --- | --- | --- | --- | --- | --- |
| sparse | 0.400 | 0.967 | 0.883 | 0.890 | 0.900 | 4 / 14 |
| dense | 0.233 | 0.467 | 0.333 | 0.372 | 0.400 | 9 / 14 |
| hybrid | 0.400 | 0.967 | 0.900 | 0.916 | 0.900 | 4 / 14 |

The quality means use the ten labelled queries. P@3 keeps denominator 3 even when an exact-code lookup has only one accepted hit, so that lookup has precision `1/3` and recall `1`. The four no-gold cases have null recall/rank/support metrics and are excluded from quality means; all four return empty lists under the default teaching configuration. This tests a narrow no-positive-match rule, not a general abstention or uncertainty detector. Adding a semantically related distractor or a real encoder could change those outcomes.

Support requires the declared substring atoms in their specifically labelled chunks and source versions. It is a deterministic evidence check, not entailment or generated-answer correctness. The `same_source_repeat_fraction` field counts multiple hits from one document/version; two hits may be complementary clauses, so this is not a semantic-duplicate or wasted-context rate.

Sparse and hybrid have the same mean recall in this fixture. Their ordering differs on some queries. Avoid turning the slightly higher hybrid MRR into a production recommendation: the labels are tiny and visible, the dense representation is hand-written, and candidate depth differs from a single baseline's output budget. Latency, actual postings/vector/index memory, real-model effectiveness, and generated-answer quality were not measured.

### Follow three queries all the way to the evidence

1. **Q01, `CW-1000`:** inspect sparse's token match, dense's empty result, and the single sparse contributor in RRF. The default fusion does not invent a dense vote for a zero-score chunk.
2. **Q07, the sign-off paraphrase:** inspect the payment/sign-off/receiving features and P-104's original wording. This is where a richer representation could help, but the result still depends on the declared labels.
3. **Q09, the Schedule A condition:** use each result's `source_locations` and `returned_evidence_keys` to identify which row/clause/cross-reference is missing. In the default run, all modes retrieve only two of three labelled units at k=3. High topical relevance still leaves support incomplete.

Then change just the candidate depth and inspect Q09 again:

```shell
python -m labs.week_07.compare --candidate-depth 3 --summary
python -m labs.week_07.compare --candidate-depth 8 --summary
```

Keep top-k and all labels fixed. A larger depth cannot rescue evidence absent from both accepted lists, and an increased union may promote noise. Record the changed manifest and explain what changed in the actual contributors. Do not adjust relevance labels after seeing rankings.

### Optional actual local dense adapter

The lab includes `LocalCosineAdapter` as a reference for original exercise 5. It reuses the reviewed-local-model boundary from [Week 5](https://github.com/kogantisasank831-ux/Prep/tree/main/labs/week_05#optional-actual-local-model-run), including role-specific query/document encoding, artifact/runtime identity, exact prefixes, local-only loading, and token preflight. Follow those optional dependency and artifact instructions before running:

```shell
python -m labs.week_07.compare --model-directory .runtime/embedding-model --model-id reviewed-local-model --summary
```

Pass the selected model's required `--query-prefix` and `--document-prefix`. `--dense-min-score` defaults to zero and is recorded in the dense configuration; it is an experimental selection floor, not a relevance probability. Negative cosine scores can be valid. This pairwise adapter intentionally recomputes encodings as a small correctness reference; it is not a vector-index or serving-latency benchmark. No actual model artifact was loaded for the checked-in sample. The new wrapper is exercised with the deterministic Week 5 encoder.

## 14. Your Week 7 handoff

Write a one-page decision note: corpus/query fingerprints, metadata/authorization scope, tokenizer and BM25 settings, dense identity, RRF constant/weights/depth, category metrics, and one failure with source locations. Explain why an exact code lookup needs token identity, why a paraphrase may benefit from another representation, and what evidence would justify changing the fusion policy.

You are ready for the next week when you can calculate one BM25 and one RRF score, reproduce the comparison, trace a fused result to its contributors, and separate “retrieved a candidate” from “returned complete current evidence.” Reranking, broader query rewriting, duplicate control, and context construction belong to Week 8; they have not been silently added to this retrieval baseline.

## Primary documentation

- [Python 3.13 `dataclasses`](https://docs.python.org/3.13/library/dataclasses.html)
- [Python 3.13 `typing` and `Protocol`](https://docs.python.org/3.13/library/typing.html)
- [Python 3.13 `collections.Counter`](https://docs.python.org/3.13/library/collections.html#collections.Counter)

- [Stanford IR book: Okapi BM25](https://nlp.stanford.edu/IR-book/html/htmledition/okapi-bm25-a-non-binary-model-1.html)
- [Lucene 9.12.3 BM25Similarity: positive IDF variant and parameters](https://lucene.apache.org/core/9_12_3/core/org/apache/lucene/search/similarities/BM25Similarity.html)
- [Cormack, Clarke, and Buettcher: reciprocal rank fusion](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)
