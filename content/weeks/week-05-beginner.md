---
layout: week
permalink: /weeks/week-05/beginner/
title: "Embeddings and vector retrieval: a beginner's introduction"
description: Learn how a small, local semantic-search system can find related procurement text without treating a match as proof.
summary: Follow a synthetic procurement query from bounded source documents through embeddings, cosine similarity, an in-memory vector index, and carefully interpreted top-k results.
kicker_primary: Embeddings and vector retrieval
kicker_secondary: Beginner context
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-05/
---

## Start with a search problem, not an answer generator

Imagine a procurement team has a small collection of synthetic supplier documents:

```text
P-101 | Atlas Metals purchase confirmation
Copper wire will ship after incoming-material inspection.
Invoice terms: Net 30 after inspection approval.

P-102 | Beacon Plastics purchase confirmation
Polymer pellets will ship on 2026-09-03.
Invoice terms: Net 15 from receipt.

P-103 | Atlas Metals delivery update
The copper-wire shipment is delayed by two days while quality checks finish.

P-104 | Cedar Fasteners payment note
Payment is due after the receiving team signs off on the delivered bolts.
```

An analyst asks: **“Which supplier documents say that approval or sign-off is needed before payment?”**

A keyword search for `approval` finds P-101, but it can miss P-104 because it says `signs off` instead. A search system that notices related meanings could return both. That is the narrow job of **semantic search**: rank stored text by how relevant it appears to a query’s meaning.

Semantic search is not an assistant that writes a conclusion. It does not approve an invoice, decide that a contract applies, or prove that a returned passage is current or correct. It proposes relevant evidence for a person or a later deterministic process to inspect. The documents are untrusted input, and a high similarity score is not factual truth.

Our small system will keep this boundary explicit:

```text
untrusted procurement documents + untrusted query
                 |
                 v
        bounded text records
                 |
                 v
   local embedding boundary creates vectors
                 |
                 v
       vector storage ranks similar records
                 |
                 v
    top-k candidate passages for human review
```

There is no answer-generation step in this lesson. We will not ask a language model to summarize the results, use an orchestration framework, connect to a hosted service, or add database infrastructure. First learn the retrieval boundary itself.

**Checkpoint.** If P-104 is returned for the query, has the system proved that Cedar Fasteners owes payment only after approval? No. It has found a passage worth checking. A person must read the exact passage, identify the applicable document and version, and apply the relevant policy.

## An embedding is a numeric representation of text

An **embedding** is an ordered list of numbers, called a **vector**, produced for a piece of text. An embedding model is trained so that texts used in similar ways tend to have vectors that are close under a chosen comparison rule.

For a toy illustration, an embedding might look like this:

```text
"payment after inspection approval"
    -> [0.74, -0.08, 0.51, 0.11, ...]

"receiving team signs off before payment"
    -> [0.69, -0.03, 0.55, 0.16, ...]
```

The individual positions are dimensions. It would be tempting to call the first one “payment” and the third one “approval,” but that is usually not how useful learned embeddings work. Meaning is distributed across many dimensions and interactions. A single number rarely has a stable, human-readable interpretation.

This is different from searching raw strings. A string match asks whether characters or tokens appear together. An embedding model maps an entire input into a geometry where phrasing such as “approval” and “signs off” may end up near each other because of patterns learned during training.

It is also different from the token embeddings inside a generative language model. A token embedding represents one token at an early model stage. A retrieval embedding is the exposed representation for a whole query, sentence, or document segment, produced by a model selected and configured for similarity tasks. Both are vectors, but their purpose and interface differ.

An embedding has no innate understanding and no link to a live contract system. It is an untrusted model output. Treat it as derived, potentially sensitive data: retain only what the system needs, associate it with source identity and model version, and do not assume that making data numeric removes security or privacy obligations.

### Dimensions describe the vector’s width, not its quality

The number of values in an embedding is its **dimensionality**. A vector such as `[0.2, -0.4, 0.7]` has three dimensions; a real model might output hundreds or thousands.

More dimensions give a model more numeric capacity to represent distinctions, but they do not automatically make search better. Quality depends on the model’s training objective, the language and domain of the input, the evaluation data, the comparison metric, and the retrieval task. A 1,024-dimensional general-purpose embedding can be worse for procurement payment clauses than a smaller model evaluated and tuned for that domain.

Dimensions are also an operational cost. Storing `N` vectors of `D` floating-point values takes space proportional to `N × D`, and comparing a query to every vector takes work proportional to `N × D` in a simple exact search. This does not make a larger vector wrong; it makes dimension a deliberate quality, latency, and storage trade-off.

**Checkpoint.** Does a 1,536-dimensional embedding contain 1,536 independently named facts about a document? No. It is a fixed-width learned representation. Its usefulness must be measured on the retrieval problem, not inferred from its width.

## Similarity is a rule for comparing vectors

Once text becomes vectors, the system needs a **similarity measure**: a numerical rule that says how close two vectors are. Common choices include dot product, Euclidean distance, and cosine similarity. A model’s documentation and evaluation convention matter here; do not freely swap measures because they sound interchangeable.

For this lesson, use **cosine similarity**. It compares the angle between vectors rather than their raw length:

```text
cosine_similarity(a, b) = (a dot b) / (length(a) * length(b))
```

The dot product multiplies matching positions and adds them. The vector length is the square root of the sum of squared positions. For non-zero real vectors, cosine similarity is mathematically between -1 and 1 (apart from possible tiny floating-point round-off):

- `1` means the vectors point in exactly the same direction.
- `0` means they are perpendicular under this representation, so neither direction contributes to the other.
- `-1` means opposite directions.

Those are geometric statements, not natural-language guarantees. Real retrieval scores depend on the selected model and inputs; a score of `0.78` is not automatically “78% correct.”

Here is a small numerical example. Suppose a query and a record have two-dimensional toy vectors:

```text
query  q = [1, 1]
record r = [2, 0]

q dot r        = (1 * 2) + (1 * 0) = 2
length(q)      = sqrt(1^2 + 1^2)    = sqrt(2)
length(r)      = sqrt(2^2 + 0^2)    = 2
cosine(q, r)   = 2 / (sqrt(2) * 2)  about 0.71
```

The result is about `0.71` because the vectors point in broadly, but not exactly, the same direction. Now compare `[1, 1]` with `[10, 10]`. The second vector is longer, but it points in exactly the same direction, so cosine similarity is `1.0`. That length-insensitivity is useful when a model’s vector magnitude is not meant to signal relevance.

Cosine similarity requires vectors of the same length. If a document vector has 384 values and a query vector has 768, the comparison is invalid. That is why an index must retain the embedding model and version that created its contents, and why a model change normally requires re-embedding the indexed corpus rather than mixing vectors silently.

**Checkpoint.** Is a cosine score a probability that a statement is true? No. It is a model- and metric-dependent geometric score used to rank candidates.

## Dense retrieval ranks by embeddings

**Dense retrieval** stores a dense vector for every indexed record and retrieves records whose vectors are closest to the query vector. “Dense” means most positions have useful numeric values, unlike a sparse representation where a very large vocabulary vector might be mostly zeros.

For the procurement example, the system embeds each bounded document record once, then embeds the analyst’s query at search time:

```text
P-101 text  -> document vector  ----+
P-102 text  -> document vector  ----+--> stored vector index
P-103 text  -> document vector  ----+
P-104 text  -> document vector  ----+

query text  -> query vector ----> compare --> ranked records
```

The document and query encoders must be compatible. Some models use one encoder for both; others explicitly distinguish a query instruction or query encoder from a passage/document encoder. Follow the chosen model’s documented input convention. Embedding a query with an arbitrary text-generation endpoint or with mismatched preprocessing may produce numbers, but it does not establish a valid retrieval setup.

Dense retrieval can bridge vocabulary differences, which is why P-104 can be a candidate for a query that says “approval.” It also creates new failure modes. It may return a document about inspection because “inspection” is common, even though the question is specifically about payment conditions. It may blur negation (“approval is not required”), dates, numbers, supplier identity, or narrow contractual distinctions. The vector captures a compressed representation; it does not perform a legal or factual reading.

That is why source metadata matters. A result should carry the original text, document ID, location, source/version information, model ID, and score. Showing only a score or a generated label prevents useful review. Retrieval relevance means “worth examining for this query,” not “safe to treat as an established fact.”

## Build the smallest useful local pipeline

Before code, make the pipeline’s contracts visible. Each input document is bounded and stored with its identity. Each initial chunk retains its parent ID and text. The embedding component is injected behind a narrow interface. Vector storage accepts only vectors of the expected dimension. Search returns the original text alongside the ranking score.

For this first version, “chunking” has a deliberately limited meaning: each already-short document becomes one chunk after a maximum-length check. A longer document is rejected for review rather than split by a clever heuristic. Deciding how to split long documents, preserve overlap, respect headings or tables, and evaluate chunk boundaries is a separate Week 6 problem. Silently slicing a contract clause here could detach a condition from its exception.

### 1. Load documents through a bounded boundary

The following code uses synthetic documents in memory. In a real loader, validate permitted file types and size before parsing, isolate untrusted parsers, authenticate access, and avoid logging source contents. The `load_documents` function demonstrates only a compact text-length boundary; it is not a secure file-ingestion implementation.

```python
from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from math import sqrt
from re import findall
from typing import Protocol


MAX_DOCUMENT_CHARS = 1_000


@dataclass(frozen=True)
class SourceDocument:
    document_id: str
    title: str
    text: str


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    document_id: str
    text: str


def load_documents(records: Iterable[SourceDocument]) -> tuple[SourceDocument, ...]:
    """Accept a bounded set of non-empty synthetic source documents."""
    loaded: list[SourceDocument] = []
    seen_ids: set[str] = set()
    for record in records:
        if not record.document_id or record.document_id in seen_ids:
            raise ValueError("document IDs must be non-empty and unique")
        if not record.text.strip() or len(record.text) > MAX_DOCUMENT_CHARS:
            raise ValueError("document text must be non-empty and within the limit")
        seen_ids.add(record.document_id)
        loaded.append(record)
    return tuple(loaded)


def initial_chunks(documents: Iterable[SourceDocument]) -> tuple[Chunk, ...]:
    """Keep one bounded document as one traceable initial chunk."""
    return tuple(
        Chunk(
            chunk_id=f"{document.document_id}:0",
            document_id=document.document_id,
            text=document.text,
        )
        for document in documents
    )
```

The code keeps the document ID in every chunk. If the same supplier text appears in multiple files, the system must still be able to tell where a result came from. The title is preserved at the document level for later display, though this small chunk type needs only the source ID and text.

**Checkpoint.** Why reject an oversized document instead of truncating it? Silent truncation can remove the condition that makes a clause relevant, distort evaluation, and make a returned passage appear complete when it is not.

### 2. Embed behind an injected local boundary

The application should not scatter model-runtime calls throughout loading, indexing, and search code. Give the embedding provider one narrow interface. That makes the local runtime replaceable and lets tests inject a deterministic fake without claiming that the fake understands language.

The model below is intentionally a tiny, deterministic teaching surrogate. Its terms map related procurement words to the same toy features so the example can demonstrate cosine ranking without a download, GPU, hosted API, or paid service. It is not a real semantic embedding model and must not be used to evaluate retrieval quality.

```python
Vector = tuple[float, ...]


class LocalEmbedder(Protocol):
    """A local boundary that returns one compatible vector per input text."""

    dimension: int

    def embed(self, texts: Sequence[str]) -> tuple[Vector, ...]:
        ...


@dataclass(frozen=True)
class DemoLocalEmbedder:
    """Deterministic teaching-only substitute for a local embedding runtime."""

    dimension: int = 4

    def embed(self, texts: Sequence[str]) -> tuple[Vector, ...]:
        vectors: list[Vector] = []
        for text in texts:
            terms = set(findall(r"[a-z0-9]+", text.casefold()))
            vectors.append(
                (
                    float(bool(terms & {"payment", "invoice", "due"})),
                    float(bool(terms & {"approval", "approve", "sign", "signs", "off"})),
                    float(bool(terms & {"inspection", "quality", "receiving"})),
                    float(bool(terms & {"copper", "wire", "bolts", "pellets"})),
                )
            )
        return tuple(vectors)


def cosine_similarity(left: Vector, right: Vector) -> float:
    if len(left) != len(right):
        raise ValueError("vectors must have matching dimensions")
    left_length = sqrt(sum(value * value for value in left))
    right_length = sqrt(sum(value * value for value in right))
    if left_length == 0.0 or right_length == 0.0:
        raise ValueError("cosine similarity is undefined for a zero vector")
    dot_product = sum(a * b for a, b in zip(left, right, strict=True))
    return dot_product / (left_length * right_length)
```

Notice two ordinary but important checks: all vectors must have the expected compatible dimension, and cosine similarity is undefined for an all-zero vector. A real embedding boundary should also record the model identifier, artifact/version, preprocessing convention, and embedding dimension. Errors from its local runtime should be explicit and should not be turned into a plausible empty result.

The toy normalization is intentionally weak. It makes “signs off” share a feature with “approval,” but it does not handle grammar, negation, multiword terms, or most vocabulary. That weakness is educational: a few matching features are not semantic understanding. A real local model must be selected and evaluated for the supported languages and procurement task.

### 3. Store document vectors and retrieve top-k candidates

An **index** is a data structure that organizes vectors for search. The smallest possible vector index is an in-memory list of `(chunk, vector)` entries. It performs **exact nearest-neighbour search** by comparing the query with every stored vector, then sorting by score. This is simple, transparent, and useful for small collections or a correctness baseline.

```python
@dataclass(frozen=True)
class IndexedChunk:
    chunk: Chunk
    vector: Vector


@dataclass(frozen=True)
class SearchResult:
    chunk: Chunk
    score: float


@dataclass(frozen=True)
class InMemoryVectorIndex:
    dimension: int
    entries: tuple[IndexedChunk, ...]

    @classmethod
    def build(
        cls,
        chunks: Sequence[Chunk],
        embedder: LocalEmbedder,
    ) -> "InMemoryVectorIndex":
        vectors = embedder.embed([chunk.text for chunk in chunks])
        if len(vectors) != len(chunks):
            raise ValueError("embedder must return one vector per chunk")
        if any(len(vector) != embedder.dimension for vector in vectors):
            raise ValueError("embedder returned an unexpected vector dimension")
        return cls(
            dimension=embedder.dimension,
            entries=tuple(
                IndexedChunk(chunk=chunk, vector=vector)
                for chunk, vector in zip(chunks, vectors, strict=True)
            ),
        )

    def search(
        self,
        query: str,
        *,
        embedder: LocalEmbedder,
        top_k: int,
    ) -> tuple[SearchResult, ...]:
        if not query.strip():
            raise ValueError("query must be non-empty")
        if not 1 <= top_k <= len(self.entries):
            raise ValueError("top_k must be between one and the index size")
        if embedder.dimension != self.dimension:
            raise ValueError("query embedder is incompatible with this index")
        query_vectors = embedder.embed([query])
        if len(query_vectors) != 1 or len(query_vectors[0]) != self.dimension:
            raise ValueError("query embedder returned an invalid vector")
        query_vector = query_vectors[0]
        ranked = sorted(
            (
                SearchResult(
                    chunk=entry.chunk,
                    score=cosine_similarity(query_vector, entry.vector),
                )
                for entry in self.entries
            ),
            key=lambda result: result.score,
            reverse=True,
        )
        return tuple(ranked[:top_k])
```

The storage type accepts vectors only at index build time and checks the embedding dimension. It also refuses a query vector from an incompatible embedder. In production, the model/version identity belongs in the persistent index metadata as well; a dimension match alone is not sufficient evidence that two model outputs are comparable.

Assemble the synthetic example without network access:

```python
documents = load_documents(
    [
        SourceDocument(
            "P-101",
            "Atlas Metals purchase confirmation",
            "Copper wire will ship after incoming-material inspection. "
            "Invoice terms: Net 30 after inspection approval.",
        ),
        SourceDocument(
            "P-102",
            "Beacon Plastics purchase confirmation",
            "Polymer pellets will ship on 2026-09-03. Invoice terms: Net 15 from receipt.",
        ),
        SourceDocument(
            "P-103",
            "Atlas Metals delivery update",
            "The copper-wire shipment is delayed by two days while quality checks finish.",
        ),
        SourceDocument(
            "P-104",
            "Cedar Fasteners payment note",
            "Payment is due after the receiving team signs off on the delivered bolts.",
        ),
    ]
)
embedder = DemoLocalEmbedder()
index = InMemoryVectorIndex.build(initial_chunks(documents), embedder)
results = index.search(
    "Which supplier documents require approval before payment?",
    embedder=embedder,
    top_k=2,
)

assert [result.chunk.document_id for result in results] == ["P-101", "P-104"]
assert all(result.score > 0.0 for result in results)
```

The assertion is a deterministic test of this teaching surrogate and synthetic corpus, not proof that a real embedding model will produce the same result. It demonstrates the full pipeline: document loading, bounded initial chunking, embedding, vector storage, and top-k retrieval.

## Exact search and approximate nearest neighbours

The in-memory index compares the query against every vector. With 10 documents, that is trivial. With millions of records and high-dimensional vectors, scanning all vectors for every query can become too slow or expensive. **Approximate nearest-neighbour (ANN) search** is a family of techniques that trades a small amount of exactness for faster retrieval at scale.

An ANN index organizes the vector space so it can inspect a promising subset rather than every vector. Different algorithms use different structures, but the basic contract is the same: return neighbours that are likely to be near the query under the configured metric, within a time and resource budget.

“Approximate” matters. An ANN index can miss the exact best neighbour or return a slightly different ranking than a full scan. That is not automatically a defect; it is a measurable recall–latency trade-off. Tune it against a fixed evaluation set and compare it with an exact baseline where practical. Do not describe ANN as an accuracy upgrade simply because it is more sophisticated.

For this beginner system, a simple list remains the right index because it makes the metric and returned evidence easy to inspect. Sharding, filtering policies, access control, persistence, update/delete semantics, backup, and index-parameter tuning are not part of this lesson. They add operational responsibilities, not merely speed.

**Checkpoint.** Does an ANN result with the highest reported score prove that no better document exists? No. The score ranks what the approximate search considered and returned; the exact closest vector may have been missed.

## Domain-specific embeddings deserve domain-specific evidence

An embedding model learns from a particular objective and data distribution. A broad general-purpose model may understand ordinary English similarity well, yet still confuse a procurement exception, an internal abbreviation, a supplier code, or a distinction between `payment after approval` and `approval after payment`.

A **domain-specific embedding model** is trained or adapted for a narrower area such as procurement, legal clauses, biomedical text, or source code. A general model can instead be selected because it performs well on domain evidence, but that does not make its training domain-specific. Either choice can help when the domain has specialized vocabulary, recurring document structures, or relevance judgments that generic evaluation does not capture. A specialized model can also overfit a narrow distribution, age badly as terminology changes, or perform poorly on another language or document type.

Selection should start with a written retrieval task, not a model name. For our corpus, define what “relevant” means: does the result need to mention a payment condition, identify a supplier, and preserve whether approval is required before payment? Gather appropriately governed labelled query–passage pairs that reflect real wording variants, negations, distractors, document types, and supported languages. Keep source permissions, access boundaries, and sensitive text out of an unreviewed external service.

If a locally run model is chosen, pin its artifact and runtime, verify provenance and license, and record the preprocessing and version used to build the index. Local execution reduces one network boundary; it does not make documents or vectors trusted, eliminate hardware costs, or remove the need for authorization and retention controls.

## Evaluate retrieval before trusting it in a workflow

The interview question “How are embedding models evaluated?” is best answered as an information-retrieval experiment, not as a claim based on a few impressive searches.

First define a held-out set of realistic queries and labelled relevant passages. A query can have more than one relevant result, and relevance can be graded: P-101 may be directly relevant to the approval-before-payment question, while P-103 may be only contextually related through quality checks. Label criteria before comparing models, and keep the benchmark separate from model/prompt selection when possible.

Then measure ranking quality at a declared cutoff. Common measures include:

- **Recall@k:** of all labelled relevant passages, how many appear in the first `k` results? This reveals whether retrieval finds evidence at all.
- **Precision@k:** of the first `k` returned passages, how many are labelled relevant? This reveals how much review noise the result list creates.
- **MRR (mean reciprocal rank):** for each query, take the reciprocal of the rank of the first relevant result, then average. It rewards getting a useful first result near the top.
- **nDCG:** a ranking measure that can use graded relevance and discounts useful results that appear lower in the list.

No single metric answers every product question. If an analyst reviews only three results, `Recall@3` and `Precision@3` may be more informative than an unconstrained average. Record the corpus snapshot, document/chunk policy, model and version, metric, query set, labels, and evaluation date. A score without those conditions is hard to reproduce and easy to overinterpret.

Also inspect failures manually. A model can score well on easy paraphrases but fail on negation, supplier names, dates, product codes, table layouts, short queries, or a new business unit. Check whether apparent retrieval quality comes from accidental duplicate documents or leakage between training, tuning, and held-out evaluation data. The labels themselves deserve review: treating all passages from a relevant document as relevant can hide a bad chunk boundary.

**Checkpoint.** If Model A has higher Recall@10 than Model B, must it be the better choice? Not necessarily. It may also deliver more noise, be too slow, fail a critical subgroup, use unacceptable data terms, or rank the useful passage too low for the actual review workflow.

## Why a semantically similar result can still be wrong

Similarity is a broad relationship, while many procurement questions require a narrow one. A model may retrieve P-103 for the approval-before-payment query because it mentions quality checks and an Atlas shipment. That is semantically connected, but it does not state a payment condition. Other common failure paths include:

- **Missing constraints:** a result matches `inspection` but not `before payment`.
- **Negation and modality:** “approval is not required” may be close to “approval is required.”
- **Entity confusion:** a clause about one supplier, product, or order is incorrectly used for another.
- **Time/version confusion:** a superseded amendment can be close to the current agreement.
- **Granularity loss:** an embedding for a whole passage compresses a critical exception or number.
- **Distribution shift:** new terms, languages, layouts, or policies differ from the material used for model selection.

The remedy is not to pretend the vector score is an answer. Return traceable source text and metadata, apply authorization filters before search so users cannot retrieve another tenant’s documents, and use deterministic checks or human review for the claims that matter. In the P-101/P-104 result set, a reviewer still needs to read whether each clause applies to the same transaction and whether it is the active version.

This distinction is useful in an interview: embeddings improve candidate selection; they do not replace source verification, business rules, access control, or auditability.

## Top-k is a recall-versus-noise decision

**Top-k** is the number of highest-ranked results returned. Asking for more results generally gives a relevant passage more chances to appear, so recall can rise. It also exposes more irrelevant or weakly related passages, increasing review noise and the risk that a downstream reader focuses on the wrong one.

For the synthetic query, `top_k=1` might return P-101 and hide the related Cedar Fasteners clause. `top_k=2` can surface both useful candidates. At `top_k=4`, the analyst also sees a delivery delay and receipt-based payment terms, which may be distracting. The right `k` depends on the task, corpus, score distribution, review interface, and the cost of missing evidence versus reviewing extra text.

Choose it empirically. Measure Recall@k and Precision@k over labelled queries for several values of `k`; review the actual returned passages; and document the selected value and reason. A fixed `k` is not a confidence threshold. Conversely, a score threshold needs its own calibration and failure policy; it is not automatically safer because it looks numeric.

For consequential workflows, a low-quality or empty result set should remain visible as a retrieval outcome. Do not replace it with invented text, silently broaden a user’s permissions, or claim that “no results” proves a fact is absent from every document.

**Checkpoint.** Why not always set `k` to the largest possible value? More results can improve recall, but it burdens review and can bury the relevant evidence under semantically related noise.

## What you should now be able to explain

This one synthetic procurement search has introduced a complete beginner-level retrieval path:

```text
bounded source documents
        -> one traceable initial chunk per short document
        -> compatible local embeddings
        -> dimension-checked in-memory vector index
        -> cosine-ranked top-k candidate passages
        -> human or deterministic verification of the source text
```

The important discipline is to keep the last arrow. Retrieval can make the right evidence easier to find; it cannot turn relevance into truth.

## Readiness checklist

- [ ] I can define a semantic embedding and distinguish it from raw keyword matching and from a generative model’s token embedding.
- [ ] I can explain dimensionality as vector width and name its quality, storage, and latency trade-offs.
- [ ] I can describe cosine similarity, including why its score is not a probability or factual guarantee.
- [ ] I can trace dense retrieval from source text through document embeddings, a compatible query embedding, and ranked results.
- [ ] I can explain why an index must not silently mix embeddings from different models or versions.
- [ ] I can build the conceptual pipeline: bounded document loading, initial chunking, local embedding, vector storage, and top-k retrieval.
- [ ] I can distinguish exact search from approximate nearest-neighbour search and name the recall–latency trade-off.
- [ ] I can explain when domain-specific embeddings may help and how to evaluate that claim on held-out labelled data.
- [ ] I can answer why a semantically similar passage may still be incorrect for a narrow factual or contractual question.
- [ ] I can choose and justify top-k as a recall-versus-noise trade-off rather than a default constant.

Continue with the [production version]({{ '/weeks/week-05/' | relative_url }}). It hardens this pipeline with versioned model and index contracts, authorization-before-scoring, deterministic exact retrieval, governed evaluation, and operational lifecycle controls.
