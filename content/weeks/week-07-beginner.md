---
layout: week
permalink: /weeks/week-07/beginner/
title: "Sparse and hybrid retrieval: a beginner's introduction"
description: Learn why exact procurement identifiers need keyword search and how sparse, dense, and rank-fused retrieval complement one another.
summary: Continue the P-101 through P-105 chunks with a product-code example, then compare deterministic BM25, a teaching-only dense boundary, and reciprocal-rank fusion without mistaking relevance for truth.
kicker_primary: Sparse and hybrid retrieval
kicker_secondary: Beginner context
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-07/
---

## One query exposes a dense-retrieval blind spot

Week 6 turned P-101 through P-105 into bounded, traceable chunks. Now add one short, synthetic product-code record:

```text
P-106 | Atlas Metals catalogue note
Tenant: northwind-procurement
Product code: CW-1000
Commercial name: Copper wire, 1,000 kg coil
Quoted unit price: USD 12.00
```

An analyst asks four different questions:

1. “Where is **CW-1000** defined?”
2. “What does **Atlas Metals** quote for copper wire?”
3. “Which terms say payment follows inspection approval?”
4. “Which note describes receiving-team sign-off before payment?”

The first question depends on an exact identifier. The second relies on a supplier name and commercial wording. The third should find the literal clause in P-101 or P-105. The fourth uses different words from P-104: `receiving-team sign-off` versus `signs off`.

Dense retrieval from Week 5 can help with broad meaning, but embeddings can compress or blur product codes, abbreviations, spelling variants, supplier names, and rare commercial terms. A vector that puts “copper wire” near “wire coil” does not promise that `CW-1000`, `CW1000`, and `CW-100O` stay distinguishable. A locally run model changes the network boundary; it does not turn identifiers into a reliable exact-match system.

Sparse retrieval adds a second view of the same frozen chunks:

```text
authorised query + metadata filter
        |
        +--> sparse/BM25: exact token evidence and term statistics
        |
        +--> dense: broad learned or teaching-only similarity
        |
        +--> hybrid: combine rankings under one declared policy
        |
        v
traceable candidate chunks for source review
```

Retrieval still ranks candidates. It does not prove that a price is current, that a code belongs to an active catalogue, or that a payment condition applies to a particular order. Documents, chunks, query text, vectors, and scores remain sensitive and untrusted data. Authorization and metadata constraints must reduce the candidate set before either retriever scores it.

**Checkpoint.** If a sparse search returns P-106 for `CW-1000`, has it proved that the quote is valid today? No. It has found a chunk containing the exact token. A reviewer must check source version, scope, effective date, and the relevant commercial process.

## Keyword retrieval starts with a token contract

Keyword retrieval does not compare raw characters blindly. It first applies a **tokenizer**: a declared rule for turning query and chunk text into terms. The token rule determines whether `CW-1000` stays one token, becomes `cw` and `1000`, or is discarded. It therefore changes retrieval behavior and must be versioned with the index.

For this procurement example, preserve internal hyphens, underscores, and slashes in code-like terms:

```text
CW-1000       -> cw-1000
PO_2026/18    -> po_2026/18
Net 30        -> net, 30
```

This is useful for exact identifiers, but it has limits:

- `CW1000` does not exactly equal `CW-1000` under this tokenizer.
- `CW-100O` with letter O is a different term from zero.
- a supplier rename or abbreviation may be absent from the query.
- language-specific morphology, accents, punctuation, and OCR defects need a separately designed normalization policy.

Do not “helpfully” remove punctuation without measuring the effect. Splitting every hyphen can improve a query for `copper-wire` but can destroy the distinct product code `CW-1000`. Keep the original source text and explainable token policy so a reviewer can see what matched.

```python
from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from math import log
import re
from typing import Protocol


TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:[-_/][a-z0-9]+)*")


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    tenant_id: str
    document_id: str
    document_version: str
    text: str
    metadata: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class RetrievalQuery:
    principal_id: str
    text: str
    top_k: int
    metadata_filters: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class SearchResult:
    chunk: Chunk
    score: float
    rank: int
    retriever: str


def tokenize(text: str) -> tuple[str, ...]:
    return tuple(TOKEN_PATTERN.findall(text.lower()))


def metadata_dict(chunk: Chunk) -> dict[str, str]:
    return dict(chunk.metadata)
```

The code uses a small, local token contract. It does not correct spelling, expand abbreviations, identify named entities, or extract product codes from PDFs. Those are separate policies with their own false-positive/false-negative trade-offs.

## BM25: sparse relevance with a useful amount of restraint

**BM25** is a sparse ranking function. A sparse index records which chunks contain which tokens and how often. BM25 gives more credit when a query term occurs in a chunk, but it does not let repeated occurrences grow without bound. It also gives more weight to rare terms and adjusts for document length.

For a query term `t` in document/chunk `d`, one common BM25 component is:

```text
score(q, d) = sum over query terms t of
  IDF(t) * (f(t, d) * (k1 + 1)) /
           (f(t, d) + k1 * (1 - b + b * |d| / avgdl))

IDF(t) = log(1 + (N - df(t) + 0.5) / (df(t) + 0.5))
```

Where:

| Symbol | Meaning |
| --- | --- |
| `f(t, d)` | count of term `t` in chunk `d` |
| `df(t)` | number of indexed chunks containing `t` |
| `N` | number of indexed chunks |
| `|d|` | token count of chunk `d` |
| `avgdl` | average token count across indexed chunks |
| `k1` | term-frequency saturation control, often a positive value around 1–2 |
| `b` | document-length normalization control between 0 and 1 |

The fraction containing `f(t, d)` is **term-frequency saturation**: seeing `cw-1000` twice can help, but one boilerplate-heavy chunk should not gain unlimited relevance by repeating it fifty times. `IDF` is **inverse document frequency**: a term found in few chunks, such as `cw-1000`, is generally more discriminative than `invoice`. The `|d| / avgdl` part is **document-length normalization**: a matching term in a long chunk is adjusted relative to the corpus average so long chunks do not win only because they contain more words.

BM25 is not a semantic model. It can miss `signs off` when the query says `approval`, fail on synonyms, and treat an exact term as relevant even when its negation or date makes it unusable. Its strength is that it preserves lexical evidence and makes rare identifiers valuable.

```python
@dataclass(frozen=True)
class BM25Index:
    chunks: tuple[Chunk, ...]
    term_frequencies: Mapping[str, Counter[str]]
    document_frequencies: Mapping[str, int]
    document_lengths: Mapping[str, int]
    average_document_length: float
    k1: float = 1.2
    b: float = 0.75

    @classmethod
    def build(cls, chunks: Sequence[Chunk], *, k1: float = 1.2, b: float = 0.75) -> BM25Index:
        if not chunks:
            raise ValueError("BM25 needs at least one chunk")
        if k1 <= 0 or not 0.0 <= b <= 1.0:
            raise ValueError("require k1 > 0 and b in [0, 1]")
        frequencies: dict[str, Counter[str]] = {}
        document_frequency: Counter[str] = Counter()
        lengths: dict[str, int] = {}
        for chunk in chunks:
            terms = tokenize(chunk.text)
            if not terms:
                raise ValueError("chunks must contain at least one token")
            if chunk.chunk_id in frequencies:
                raise ValueError("chunk IDs must be unique")
            frequencies[chunk.chunk_id] = Counter(terms)
            lengths[chunk.chunk_id] = len(terms)
            document_frequency.update(frequencies[chunk.chunk_id].keys())
        return cls(
            chunks=tuple(chunks),
            term_frequencies=frequencies,
            document_frequencies=dict(document_frequency),
            document_lengths=lengths,
            average_document_length=sum(lengths.values()) / len(lengths),
            k1=k1,
            b=b,
        )

    def score(self, query_text: str, chunk: Chunk) -> float:
        query_terms = tokenize(query_text)
        frequencies = self.term_frequencies[chunk.chunk_id]
        length = self.document_lengths[chunk.chunk_id]
        total = 0.0
        for term in query_terms:
            frequency = frequencies[term]
            if frequency == 0:
                continue
            document_frequency = self.document_frequencies[term]
            inverse_document_frequency = log(
                1.0 + (len(self.chunks) - document_frequency + 0.5) / (document_frequency + 0.5)
            )
            denominator = frequency + self.k1 * (
                1.0 - self.b + self.b * length / self.average_document_length
            )
            total += inverse_document_frequency * frequency * (self.k1 + 1.0) / denominator
        return total
```

**Checkpoint.** Does a high BM25 score prove that every query constraint is satisfied? No. BM25 rewards matched tokens under its formula. It does not check factual support, active document version, authorization, negation, or contractual applicability.

## Dense and sparse retrieval fail in different ways

Sparse retrieval is usually strong at exact product codes, supplier names, rare terms, and commercial wording that appears literally. It may be weak when a user paraphrases the source: `approval before payment` versus P-104’s `signs off` wording.

Dense retrieval is often useful for broader semantic similarity. It may connect those paraphrases, but it can perform poorly for identifiers because a code carries little natural-language meaning. It can also confuse a supplier name with an unrelated similar-looking name, blur a version suffix, or retrieve a semantically adjacent delivery note instead of a payment clause.

Neither is a source of truth. They provide different candidate sets from the same authorised chunks. A robust first comparison therefore does not announce a universal winner; it asks which retrieval mode finds the labelled source evidence for each query type.

The local dense adapter below is a deterministic teaching boundary. It maps a few procurement terms into features so the code has a reproducible semantic-like score. It cannot measure embedding quality and must not be used to select a real model.

```python
class DenseScorer(Protocol):
    def score(self, query_text: str, chunk_text: str) -> float:
        ...


@dataclass(frozen=True)
class DemoDenseScorer:
    """Teaching-only feature scorer; it is not an embedding model."""

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

The teaching scorer deliberately ignores `CW-1000`. That exposes the desired limitation: a semantic-like feature representation can match “copper wire” yet drop the exact identifier distinction. A real local embedding adapter belongs behind the same narrow boundary and needs its own model/version, preprocessing, metric, and held-out evaluation record.

## Filter first, then score both retrievers

Metadata filtering is useful when a caller is already limited to a supplier, document type, date range, or tenant. It is also a security boundary when authorization determines which objects the caller may inspect. Filtering after ranking is too late: score, timing, result count, cache, or existence information can leak an unauthorised chunk.

```python
class AccessPolicy(Protocol):
    def can_read(self, principal_id: str, chunk: Chunk) -> bool:
        ...


@dataclass(frozen=True)
class StaticAccessPolicy:
    permitted: frozenset[tuple[str, str, str, str]]

    def can_read(self, principal_id: str, chunk: Chunk) -> bool:
        return (
            principal_id,
            chunk.tenant_id,
            chunk.document_id,
            chunk.document_version,
        ) in self.permitted


def eligible_chunks(
    query: RetrievalQuery,
    chunks: Iterable[Chunk],
    access_policy: AccessPolicy,
) -> tuple[Chunk, ...]:
    if not query.principal_id.strip() or not query.text.strip():
        raise ValueError("principal and query text must be non-empty")
    def matches_metadata(chunk: Chunk) -> bool:
        values = metadata_dict(chunk)
        return all(values.get(key) == value for key, value in query.metadata_filters)
    return tuple(
        chunk
        for chunk in chunks
        if access_policy.can_read(query.principal_id, chunk) and matches_metadata(chunk)
    )


def rank_scores(
    scores: Iterable[tuple[Chunk, float]],
    *,
    top_k: int,
    retriever: str,
) -> tuple[SearchResult, ...]:
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    ordered = sorted(scores, key=lambda item: (-item[1], item[0].chunk_id))[:top_k]
    return tuple(
        SearchResult(chunk=chunk, score=score, rank=rank, retriever=retriever)
        for rank, (chunk, score) in enumerate(ordered, start=1)
    )


def sparse_search(query: RetrievalQuery, index: BM25Index, access_policy: AccessPolicy) -> tuple[SearchResult, ...]:
    eligible = eligible_chunks(query, index.chunks, access_policy)
    if not eligible:
        return ()
    eligible_index = BM25Index.build(eligible, k1=index.k1, b=index.b)
    return rank_scores(
        ((chunk, eligible_index.score(query.text, chunk)) for chunk in eligible),
        top_k=query.top_k,
        retriever="bm25",
    )


def dense_search(
    query: RetrievalQuery,
    chunks: Sequence[Chunk],
    access_policy: AccessPolicy,
    scorer: DenseScorer,
) -> tuple[SearchResult, ...]:
    eligible = eligible_chunks(query, chunks, access_policy)
    return rank_scores(
        ((chunk, scorer.score(query.text, chunk.text)) for chunk in eligible),
        top_k=query.top_k,
        retriever="dense-demo",
    )
```

The sparse and dense functions receive the same `eligible_chunks` result. The teaching sparse path rebuilds BM25 statistics over that eligible set so an unauthorised document cannot influence IDF or average length even when its text is never returned. Rebuilding at query time is intentionally simple, not operationally efficient; a production design can use pre-partitioned authorised indexes or another access-aware statistics policy. The simple ranking function has deterministic tie-breaking by `chunk_id`; a zero score remains a candidate only because this illustrative baseline returns top-k from the eligible corpus. A real product may define an explicit empty or low-quality-result policy, but it should not invent an answer when all scores are weak.

## Hybrid retrieval combines evidence, not raw scales

Suppose BM25 produces scores such as `8.4`, `1.1`, and `0.0`, while a dense model produces `0.81`, `0.77`, and `0.12`. Adding `8.4 + 0.81` and comparing it to another sum treats both scales as if they mean the same thing. They do not. BM25 depends on corpus term statistics, query length, and parameters; dense scores depend on a model and metric. Raw addition can silently make one retriever dominate.

One explanatory technique is **score normalization**, for example min–max scaling:

```text
normalized(score) = (score - minimum) / (maximum - minimum)
```

This produces values between zero and one within one candidate set. It is not a universal fix. A single outlier can compress other scores; a one-document query has no useful range; score distributions can change across corpora; and a normalized `0.8` remains neither a probability nor proof of relevance.

```python
def min_max_normalize(scores: Mapping[str, float]) -> dict[str, float]:
    if not scores:
        return {}
    minimum = min(scores.values())
    maximum = max(scores.values())
    if minimum == maximum:
        return {key: 0.0 for key in scores}
    return {key: (value - minimum) / (maximum - minimum) for key, value in scores.items()}
```

Other choices include z-score normalization, rank normalization, calibration on held-out data, or a learned combiner. Each makes assumptions and needs its own evaluation. For this beginner hybrid baseline, use **reciprocal rank fusion (RRF)** because it combines ranks, not incomparable raw scores:

```text
RRF(chunk) = sum over ranked lists of 1 / (k + rank(chunk))
```

`k` is a positive constant that softens the difference between top ranks. A chunk that appears high in both lists receives more evidence than a chunk appearing only once. RRF does not understand truth, document version, constraints, or scores hidden beyond the chosen candidate depth. It can preserve duplicates if the corpus contains overlapping chunks, so deduplicate by stable chunk/source policy before interpreting results.

```python
def reciprocal_rank_fusion(
    ranked_lists: Sequence[Sequence[SearchResult]],
    *,
    rank_constant: int = 60,
    top_k: int,
) -> tuple[SearchResult, ...]:
    if rank_constant <= 0 or top_k <= 0:
        raise ValueError("rank constant and top_k must be positive")
    scores: defaultdict[str, float] = defaultdict(float)
    chunks: dict[str, Chunk] = {}
    for ranked_list in ranked_lists:
        for result in ranked_list:
            scores[result.chunk.chunk_id] += 1.0 / (rank_constant + result.rank)
            chunks[result.chunk.chunk_id] = result.chunk
    return rank_scores(
        ((chunks[chunk_id], score) for chunk_id, score in scores.items()),
        top_k=top_k,
        retriever="rrf",
    )


def hybrid_search(
    query: RetrievalQuery,
    index: BM25Index,
    access_policy: AccessPolicy,
    scorer: DenseScorer,
    *,
    candidate_depth: int,
) -> tuple[SearchResult, ...]:
    if candidate_depth < query.top_k:
        raise ValueError("candidate depth must be at least top_k")
    expanded_query = RetrievalQuery(
        principal_id=query.principal_id,
        text=query.text,
        top_k=candidate_depth,
        metadata_filters=query.metadata_filters,
    )
    sparse = sparse_search(expanded_query, index, access_policy)
    dense = dense_search(expanded_query, index.chunks, access_policy, scorer)
    return reciprocal_rank_fusion((sparse, dense), top_k=query.top_k)
```

Candidate depth matters. If `top_k=3` but each input retriever supplies only its first three candidates, RRF cannot recover a useful chunk that both rank fourth. Increasing depth can improve recall but adds scoring work and duplicate/noise handling. Choose both depth and final `top_k` from held-out evaluation and the reviewer’s bounded reading budget.

The compact fused `SearchResult` records only the fused score and `rrf` label. A production result should also retain each contributing retriever, its rank, its configuration/manifest identity, and the candidate depth so the fused order can be reproduced and explained.

**Checkpoint.** Does RRF prove that a chunk supported by two retrievers is factually correct? No. It says two ranking methods placed that chunk highly. The source still requires identity/version checks and review.

### Read the fused list as a candidate set

Hybrid retrieval is most useful when the query has mixed evidence needs. For `CW-1000`, sparse retrieval can make the exact code visible; dense retrieval may add chunks about the commercial name `copper wire`. For “receiving-team sign-off before payment,” dense similarity can help surface P-104 even when literal terms differ, while sparse retrieval retains the visible words it did match. The fused order is a proposal for review, not a merged fact.

Inspect the separate sparse and dense ranks during evaluation. If RRF repeatedly promotes a chunk because both methods respond to generic `invoice` language, that is a failure signal rather than proof that agreement is valuable. If a code query succeeds only through BM25, that can be an entirely acceptable result: hybrid does not require every retriever to contribute equally to every query category.

Keep result provenance sufficient to explain which source chunk was returned, which document version it belongs to, which metadata filter applied, and which retrieval paths included it. Do not expose unrelated chunks merely to make a fused result look more complete. If the returned candidates do not contain the evidence atoms needed for a reviewable conclusion, return that limitation visibly rather than turning the retrieval list into generated prose.

This keeps the system honest about uncertainty while preserving a useful audit trail for later diagnosis and controlled improvement.

## Compare the same chunks, not three different experiments

The frozen fixture below keeps P-101 through P-106 stable. Each chunk has the same tenant, source version, metadata, and text for BM25, dense-demo, and RRF. The exact product code, supplier name, commercial term, and semantic question are all represented as queries; the code provides comparison scaffolding, not benchmark results.

```python
CHUNKS = (
    Chunk("P-101:1:0", "northwind-procurement", "P-101", "1", "Atlas Metals. Copper wire will ship after incoming-material inspection. Invoice terms: Net 30 after inspection approval.", (("supplier", "Atlas Metals"), ("document_type", "confirmation"))),
    Chunk("P-102:1:0", "northwind-procurement", "P-102", "1", "Beacon Plastics. Product code PP-20. Invoice terms: Net 15 from receipt.", (("supplier", "Beacon Plastics"), ("document_type", "confirmation"))),
    Chunk("P-103:1:0", "northwind-procurement", "P-103", "1", "Atlas Metals delivery update. Copper-wire shipment delayed while quality checks finish.", (("supplier", "Atlas Metals"), ("document_type", "delivery_update"))),
    Chunk("P-104:1:0", "northwind-procurement", "P-104", "1", "Cedar Fasteners. Payment is due after the receiving team signs off on delivered bolts.", (("supplier", "Cedar Fasteners"), ("document_type", "payment_note"))),
    Chunk("P-105:1:row-1", "northwind-procurement", "P-105", "1", "Schedule A row 1: product copper wire; quantity 1,000 kg; unit price USD 12.00.", (("supplier", "Atlas Metals"), ("document_type", "framework_agreement"))),
    Chunk("P-105:1:section-3", "northwind-procurement", "P-105", "1", "Section 3 Invoicing: Invoice terms are Net 30 after inspection approval. This condition controls Schedule A.", (("supplier", "Atlas Metals"), ("document_type", "framework_agreement"))),
    Chunk("P-106:1:0", "northwind-procurement", "P-106", "1", "Atlas Metals catalogue note. Product code CW-1000. Commercial name Copper wire, 1,000 kg coil. Quoted unit price USD 12.00.", (("supplier", "Atlas Metals"), ("document_type", "catalogue"))),
)

INDEX = BM25Index.build(CHUNKS)
DEMO_DENSE = DemoDenseScorer()
ACCESS = StaticAccessPolicy(
    frozenset(("analyst", "northwind-procurement", chunk.document_id, chunk.document_version) for chunk in CHUNKS)
)

EVALUATION_QUERIES = (
    RetrievalQuery("analyst", "CW-1000", top_k=3),
    RetrievalQuery("analyst", "Atlas Metals copper wire quote", top_k=3),
    RetrievalQuery("analyst", "Net 30 inspection approval", top_k=3),
    RetrievalQuery("analyst", "receiving-team sign-off before payment", top_k=3),
)


@dataclass(frozen=True)
class ComparisonCase:
    query: RetrievalQuery
    relevant_chunk_ids: frozenset[str]


def run_same_corpus_comparison(cases: Sequence[ComparisonCase]) -> dict[str, tuple[int, int, int]]:
    """Return result counts only; this is not an effectiveness measurement."""
    output: dict[str, tuple[int, int, int]] = {}
    for case in cases:
        sparse = sparse_search(case.query, INDEX, ACCESS)
        dense = dense_search(case.query, CHUNKS, ACCESS, DEMO_DENSE)
        hybrid = hybrid_search(case.query, INDEX, ACCESS, DEMO_DENSE, candidate_depth=5)
        output[case.query.text] = (len(sparse), len(dense), len(hybrid))
    return output


COMPARISON_CASES = (
    ComparisonCase(EVALUATION_QUERIES[0], frozenset({"P-106:1:0"})),
    ComparisonCase(EVALUATION_QUERIES[1], frozenset({"P-106:1:0"})),
    ComparisonCase(EVALUATION_QUERIES[2], frozenset({"P-101:1:0", "P-105:1:section-3"})),
    ComparisonCase(EVALUATION_QUERIES[3], frozenset({"P-104:1:0"})),
)


assert tokenize("CW-1000 / PO_2026/18") == ("cw-1000", "po_2026/18")
COMPARISON_COUNTS = run_same_corpus_comparison(COMPARISON_CASES)
assert set(COMPARISON_COUNTS) == {case.query.text for case in COMPARISON_CASES}
assert all(counts == (3, 3, 3) for counts in COMPARISON_COUNTS.values())

exact_results = sparse_search(EVALUATION_QUERIES[0], INDEX, ACCESS)
assert exact_results[0].chunk.chunk_id == "P-106:1:0"
semantic_results = dense_search(EVALUATION_QUERIES[3], CHUNKS, ACCESS, DEMO_DENSE)
assert semantic_results[0].chunk.chunk_id == "P-104:1:0"

catalogue_query = RetrievalQuery(
    "analyst",
    "CW-1000",
    top_k=3,
    metadata_filters=(("document_type", "catalogue"),),
)
assert [result.chunk.chunk_id for result in sparse_search(catalogue_query, INDEX, ACCESS)] == [
    "P-106:1:0"
]

unauthorised = Chunk(
    "private:1:0",
    "another-tenant",
    "PRIVATE",
    "1",
    "CW-1000 CW-1000 confidential catalogue",
    (("document_type", "catalogue"),),
)
expanded_index = BM25Index.build((*CHUNKS, unauthorised))
assert sparse_search(EVALUATION_QUERIES[0], expanded_index, ACCESS) == exact_results
```

The assertions prove that each deterministic retriever receives the same frozen corpus and returns the requested count for every fixture query. They do not measure which list is better. `relevant_chunk_ids` represents judged evidence, not facts generated by a retriever; keep those labels held out from retrieval-policy tuning.

## Evaluate retrieval and support, not an attractive result list

For each held-out query, label which chunks are directly relevant and what evidence a reviewer needs. In this fixture, the product-code query labels P-106 because it is the only source that defines `CW-1000`. A broader query about the related copper-wire agreement could require P-101 or P-105 as additional evidence. Define that intent before examining rankings rather than changing relevance labels to fit the returned order.

Record:

| Measurement | Question |
| --- | --- |
| Recall@k | Did the first `k` candidates include the labelled evidence? |
| Precision@k | How much review noise appeared in the first `k` candidates? |
| MRR/nDCG, when appropriate | Was direct or graded evidence placed early enough? |
| Candidate depth | Did the sparse and dense lists give fusion enough candidates? |
| Duplicate rate | Did overlap or repeated source text consume several result slots? |
| Support completeness | Do returned chunks include every declared evidence atom, source location, and version needed for review? |
| Empty/weak result behavior | Does the system visibly return no useful evidence rather than fabricate an answer? |

Use one frozen source/chunk manifest, access policy, local dense configuration, tokenizer/BM25 configuration, top-k, candidate depth, and label version across sparse, dense, and hybrid comparisons. Split duplicate documents, amendments, and near-identical catalogue entries by source family or time between development and held-out evaluation. Report failure groups: exact codes, supplier names, abbreviations, commercial terms, semantic paraphrases, OCR-like errors, tenant boundaries, and version conflicts.

This is an evaluation procedure, not a benchmark result. It contains no measured scores or winner. A hybrid system that improves average Recall@10 but returns duplicate clauses, increases sensitive-text exposure, or fails code queries is not automatically the right choice.

## Failure modes to expect before trusting a hybrid result

### Exact matching is only as exact as tokenization

`CW-1000` and `CW1000` can differ; `CW-100O` may be an OCR error; `ATLAS` may not match `Atlas Metals`; an abbreviation can be unknown. Add normalizations or aliases only when they are versioned, auditable, and evaluated for false matches. Preserve the original token and source text.

### BM25 cannot infer every paraphrase

BM25 can miss `approval` when the source says `signs off`, and it may rank an unrelated chunk high because it repeats `invoice`. It is a lexical signal, not a language-understanding guarantee.

### Dense retrieval can lose identifiers and constraints

A dense score may retrieve `copper wire` for an exact code question while missing the code-bearing catalogue chunk. It can also blur `Net 15` and `Net 30`, an old version and an amendment, or a negated condition and an active one. Keep exact/sparse evidence available for these cases.

### RRF can fuse noise and duplicates

RRF rewards agreement in rank, not factual truth. If two retrievers both over-rank a boilerplate chunk, fusion can preserve it. If overlap created five similar chunks from one source span, they can crowd the final list. Define duplicate handling and parent/source grouping in a later context-construction policy; do not hide the problem by claiming RRF solved it.

### Empty and low-quality results are legitimate outcomes

An authorised query can have no eligible chunks, no exact terms, weak dense scores, or only outdated evidence. Return a visible empty/low-quality retrieval outcome with safe provenance. Do not broaden permissions, query unrelated tenants, silently change the query, or manufacture an answer.

## Interview-quality answer: why can dense search miss codes?

Dense models optimize broad representation similarity. Product codes, abbreviations, supplier names, version suffixes, and commercial terms are often rare, arbitrary, and semantically thin. Tokenization and pooling can dilute them, and a model may consider nearby descriptive text more important than exact character identity. Sparse search preserves lexical tokens and can use rare terms strongly through IDF, so it is a valuable complement. Hybrid retrieval gives both signals a chance to contribute, but it still requires score/rank fusion policy, authorization filtering, duplicate control, and held-out evaluation. Neither sparse nor dense ranking proves the retrieved text is factually applicable.

## Exercises

1. Add a P-107 record containing `CW1000` without a hyphen. Define whether it is an alias, a distinct code, or an OCR-review case; update the token/alias policy only after defining tests.
2. Add an unauthorised tenant with an exact `CW-1000` match. Prove that it is excluded before BM25 and dense scoring, not merely hidden after ranking.
3. Define a metadata filter for `document_type=catalogue`. Compare it with an unrestricted search using the same query labels; explain the recall/noise trade-off.
4. Create a held-out label set for supplier name, commercial term, semantic paraphrase, abbreviation, and typo/OCR cases. Define direct, partial, and non-relevant evidence before tuning candidate depth.
5. Replace `DemoDenseScorer` with an approved local adapter protocol implementation. Record model identity, preprocessing, metric, artifact provenance, and evaluation results without changing the sparse corpus.

## Readiness checklist

- [ ] I can explain why code-preserving tokenization matters for sparse retrieval.
- [ ] I can describe BM25 term-frequency saturation, IDF, and document-length normalization.
- [ ] I can identify a query where sparse search is likely stronger and one where dense search may help.
- [ ] I know why raw BM25 and dense scores cannot be blindly added.
- [ ] I can explain min–max normalization’s use and its outlier/distribution limitations.
- [ ] I can explain RRF as rank fusion and name its duplicate/noise trade-offs.
- [ ] I can apply metadata and tenant/object authorization before candidate scoring for both retrievers.
- [ ] I can compare dense, sparse, and hybrid retrieval on the same frozen chunks without fabricating a winner.
- [ ] I can distinguish retrieval relevance from source truth, currentness, and permission to act.

The production lesson can harden this comparison with fuller interfaces, index provenance, tests, and operational trade-offs. It remains bounded to candidate retrieval; later work addresses further ranking and context construction.
