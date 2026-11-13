---
layout: "week"
status: "approved"
version: "1.0.1"
last_reviewed: "2026-11-13"
header_context: "Interview cheat sheets"
back_label: "Cheat sheets"
back_url: "/cheat-sheets/"
toc_heading: "Cheat-sheet sections"
pagination_label: "Cheat sheets hub"
pagination_url: "/cheat-sheets/"
title: "Embeddings and vector search interview cheat sheet"
description: "Representation, similarity, dense and sparse retrieval, ANN indexes, reranking, filtering, and production trade-offs."
summary: "Revise embedding spaces, similarity metrics, hybrid retrieval, bi-encoders, cross-encoders, ANN tuning, authorization filters, and vector-search failures."
permalink: "/interview-prep/cheat-sheets/embeddings-vector-search/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 3 · Embeddings and vector search"
current_label: "Revision guide"
alternate_label: "Cheat sheets hub"
alternate_url: "/cheat-sheets/"
---
> **Batch 3 source:** This page integrates the prepared revision artifact into the Prep site. It is separate from the Week 1–30 learning assessments.

**Target roles:** AI Engineer, RAG Engineer, ML Engineer, Applied Scientist, Senior/Lead Data Scientist  
**Use:** quick revision, search-system interviews, retrieval design, and production trade-off discussion  
**Boundary:** this sheet covers representation and candidate retrieval. Document ingestion and full RAG orchestration are covered in the next sheets.

## 1. Thirty-second revision

- An embedding maps an item to a vector so useful relationships can be measured geometrically.
- Use the similarity function expected by the model/index. Cosine compares direction; dot product includes magnitude; Euclidean distance measures geometric distance.
- If vectors are L2-normalized, cosine similarity equals their dot product, and cosine ranking is closely related to Euclidean ranking.
- Sparse retrieval is strong for exact terms, IDs, numbers, and rare words; dense retrieval is strong for semantic matches. Hybrid retrieval often combines both.
- A bi-encoder embeds queries and documents independently and scales to large corpora; a cross-encoder jointly scores a query-document pair and is usually used to rerank a small candidate set.
- Exact search maximizes recall but scans broadly. ANN indexes trade some recall for latency/memory.
- HNSW is graph-based; IVF partitions the vector space; product quantization compresses vectors. Parameters must be tuned against recall and latency.
- Metadata filters are part of retrieval correctness and authorization—not a cosmetic post-processing step.
- Vector scores are model/index-specific and are not calibrated probabilities.
- Evaluate retrieval on labeled queries with Recall@K, Precision@K, MRR/NDCG, latency, memory, freshness, and filter correctness.

## 2. What an embedding represents

An embedding function $f$ maps an object $x$ to a vector:

$$
f(x) = \mathbf{v}\in\mathbb{R}^{d}
$$

The object may be text, image, audio, user, product, graph node, or multimodal pair. Training determines what “near” means. A text embedding trained for general semantic similarity may not rank legal clauses, product codes, or code snippets well without evaluation.

### Common embedding objectives

- contrastive learning: bring positive pairs closer and negatives farther apart;
- triplet/ranking loss: score a positive above a negative by a margin;
- in-batch negatives: other examples in the batch act as negatives;
- distillation: train a smaller embedding model from a stronger teacher/reranker;
- task-supervised retrieval: learn from query-positive-negative examples.

**Interview point:** embedding quality is not an intrinsic scalar. It depends on the task, query distribution, corpus, language, chunking, similarity, and evaluation labels.

## 3. Similarity and distance

For vectors $x,y\in\mathbb{R}^{d}$:

### Dot product

$$
x\cdot y=\sum_{i=1}^{d}x_i y_i
$$

Fast and commonly used by retrieval models. Vector magnitude affects the score.

### Cosine similarity

$$
\cos(x,y)=\frac{x\cdot y}{\lVert x\rVert_2\lVert y\rVert_2}
$$

Measures direction and ranges from $-1$ to $1$ for real nonzero vectors. Many embedding spaces produce mostly narrower practical ranges.

### Euclidean distance

$$
d(x,y)=\lVert x-y\rVert_2
$$

Smaller is nearer. For unit-normalized vectors:

$$
\lVert x-y\rVert_2^2=2-2(x\cdot y)
$$

Therefore, dot-product, cosine, and squared-Euclidean rankings become equivalent under unit normalization.

```python
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def cosine_similarity(
    left: NDArray[np.float64],
    right: NDArray[np.float64],
) -> float:
    if left.shape != right.shape:
        raise ValueError("vectors must have the same shape")
    denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
    if denominator == 0.0:
        raise ValueError("cosine similarity is undefined for a zero vector")
    return float(np.dot(left, right) / denominator)
```

Do not silently normalize if the model documentation expects raw inner product.

## 4. Sparse, dense, and multi-vector representations

| Representation | Shape | Strength | Weakness |
|---|---|---|---|
| Sparse lexical | Vocabulary-sized, mostly zeros | Exact terms, identifiers, rare words, explainability | Weak synonym/paraphrase matching |
| Dense single vector | Fixed $d$ dimensions | Semantic similarity, compact index | Can blur token-level detail |
| Multi-vector/late interaction | Several vectors per item | Fine-grained token/region matching | Larger index and more complex scoring |

BM25 is a strong sparse baseline. Dense retrieval should beat it on the target task, not merely appear more modern.

## 5. Bi-encoder versus cross-encoder

### Bi-encoder

The query and document are encoded independently:

$$
s(q,d)=\operatorname{sim}(f_q(q),f_d(d))
$$

Document embeddings can be precomputed and indexed. This makes bi-encoders suitable for first-stage retrieval across large corpora.

### Cross-encoder

The query and document are jointly processed:

$$
s(q,d)=g([q;d])
$$

Joint attention captures richer interactions, but requires one forward pass per query-document pair. Use it to rerank perhaps tens or hundreds of retrieved candidates, not millions of documents.

### Retrieve and rerank

1. sparse/dense/hybrid retriever returns `fetch_k` candidates;
2. optional authorization and hard filters are already enforced;
3. cross-encoder scores candidates;
4. deduplicate/diversify;
5. send the final `top_k` to the generator.

## 6. Embedding-model selection

Evaluate:

- task: question-passage, query-document, similarity, classification, or multimodal retrieval;
- language and domain coverage;
- symmetric versus asymmetric search;
- maximum input tokens and truncation behavior;
- vector dimension, normalization, and recommended prefixes/templates;
- quality on representative queries and hard negatives;
- latency, throughput, memory, batch behavior, and license;
- compatibility with reranker, index, hardware, and deployment environment.

Some models require query/document prefixes such as `query:` and `passage:`. Omitting trained prefixes can materially change quality.

### Dimension trade-off

For $N$ vectors of dimension $d$ stored with $b$ bytes per component, raw vector storage is roughly:

$$
N\times d\times b
$$

This excludes index graph/centroids, IDs, metadata, replicas, and temporary build memory. Higher dimension can capture more information but increases storage, transfer, cache pressure, and distance-computation cost.

## 7. Exact nearest-neighbor search

Exact search scores the query against every eligible vector and returns the true top-$k$ under that similarity.

Advantages:

- maximum retrieval recall for the indexed vectors;
- simple baseline and correctness oracle for ANN tuning;
- practical for small corpora or highly filtered subsets.

Limitations:

- compute grows with corpus size and dimension;
- large scans increase latency and memory bandwidth;
- distributed exact search may require broad fan-out.

Always compare an ANN index with exact search on the same queries when tuning recall.

## 8. Approximate nearest-neighbor search

ANN avoids scoring every vector. It returns a likely top-$k$ and trades recall for speed, memory, or build time.

### HNSW

Hierarchical Navigable Small World builds a multilayer proximity graph and navigates from coarse to fine layers.

Common controls:

- `M`: graph connectivity; higher values usually improve recall but increase memory/build work;
- `ef_construction`: candidate breadth while building; higher can improve graph quality but slows construction;
- `ef_search`: breadth at query time; higher usually improves recall and latency cost.

HNSW is often strong for low-latency in-memory search, but index memory and build/update behavior must be measured.

### IVF

Inverted-file indexing trains centroids, assigns vectors to lists/cells, and searches only selected lists.

- more lists create finer partitions;
- `nprobe` controls how many partitions are searched;
- too few probes hurts recall, especially near partition boundaries;
- training data must represent the deployed vector distribution.

### Product quantization

PQ divides vectors into subspaces and replaces each subvector with a codebook entry. This compresses storage and permits approximate distance calculations.

Benefits: smaller memory footprint and potentially faster scans.  
Cost: quantization error, training complexity, and possible reranking need.

## 9. ANN evaluation

For queries with exact top-$k$ neighbors, ANN recall can be measured as:

$$
\operatorname{ANNRecall@K}=
\frac{|\text{ANN top-K}\cap\text{exact top-K}|}{K}
$$

Tune on the deployed distribution, including filters and concurrent load. Report:

- ANN recall at the required $K$;
- p50/p95/p99 latency and throughput;
- index size, build time, update/deletion cost, and memory;
- filter selectivity and empty/undersized result rates;
- quality before and after reranking.

ANN recall is not the same as business relevance: exact nearest neighbors can still be semantically wrong.

## 10. Metadata filters and authorization

Useful metadata includes:

- tenant and access-control identifiers;
- source/document/chunk/version IDs;
- language, region, product, document type, and effective dates;
- confidentiality and retention class;
- timestamps and ingestion status.

### Pre-filter versus post-filter

- **Pre-filter:** restrict eligible candidates before/during vector search. Better for security/correctness, but engine support and ANN behavior vary.
- **Post-filter:** search broadly, then discard. It can return fewer than $k$ and must never be the sole tenant/ACL boundary if unauthorized data reaches later stages.

Some ANN implementations apply filters after an initial scan and may need iterative/expanded scans to return enough eligible results. Test high-selectivity and adversarial filters.

## 11. Hybrid search

Hybrid search combines lexical and dense retrieval:

- lexical catches exact names, part numbers, error codes, dates, and rare terms;
- dense catches paraphrases and semantic intent;
- fusion reduces dependence on one representation.

### Score normalization approach

Normalize lexical and dense scores, then combine:

$$
s(d)=\alpha s_{dense}(d)+(1-\alpha)s_{sparse}(d)
$$

Raw scores from different systems are not directly comparable; normalization and $\alpha$ require tuning.

### Reciprocal Rank Fusion

RRF combines ranks rather than incomparable score magnitudes:

$$
\operatorname{RRF}(d)=\sum_{r\in R}\frac{w_r}{c+\operatorname{rank}_r(d)}
$$

```python
from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence


def reciprocal_rank_fusion(
    rankings: Sequence[Sequence[str]],
    *,
    rank_constant: int = 60,
) -> list[tuple[str, float]]:
    if rank_constant <= 0:
        raise ValueError("rank_constant must be positive")

    scores: defaultdict[str, float] = defaultdict(float)
    for ranking in rankings:
        for rank, document_id in enumerate(ranking, start=1):
            scores[document_id] += 1.0 / (rank_constant + rank)
    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))
```

RRF is robust and simple, but it discards score confidence and still needs task evaluation.

## 12. Diversity and maximal marginal relevance

Top results can be near-duplicates. Maximal Marginal Relevance balances query relevance and novelty:

$$
\operatorname{MMR}(d)=
\lambda\operatorname{sim}(q,d)-
(1-\lambda)\max_{s\in S}\operatorname{sim}(d,s)
$$

MMR can improve coverage when multiple aspects are needed, but excessive diversity may remove the best supporting passages.

## 13. Late interaction and ColBERT awareness

Late-interaction retrievers encode queries and documents into multiple token-level vectors. Relevance is computed from fine-grained interactions, often MaxSim-style matching.

Compared with:

- **single-vector dense:** higher storage/scoring complexity, potentially better detail;
- **cross-encoder:** document representations remain indexable/reusable, but interaction is richer than one-vector similarity;
- **sparse:** semantic token matching rather than only lexical overlap.

Choose it when measured quality justifies index and serving complexity.

## 14. Vector-search system map

| Tool/category | Typical use | Interview consideration |
|---|---|---|
| FAISS | In-process similarity indexes and research/prototyping | Index families, CPU/GPU, persistence/operations built around it |
| pgvector | Vectors with PostgreSQL data/transactions | Exact, HNSW/IVFFlat, SQL filters, relational joins, scale limits |
| Elasticsearch/OpenSearch | Lexical, vector, filtering, hybrid search | Inverted index + ANN, RRF/ranking, cluster operations |
| Qdrant | Dedicated vector search | Payload filters, HNSW, sparse+dense/hybrid querying |
| Milvus | Distributed vector database | Index selection, partitions, consistency, cluster operations |
| Weaviate | Vector database/search platform | Hybrid search, filters, modules, operational model |
| Pinecone | Managed vector service | Service limits, namespaces/metadata, cost and portability |
| Chroma | Developer-oriented embedding store | Useful locally; evaluate production durability/scale needs |

This table describes roles, not endorsements. Evaluate tenancy, consistency, backups, deletion, observability, filter semantics, scale, cost, and team expertise.

## 15. Retrieval model and library map

| Need | Examples | Purpose |
|---|---|---|
| Embedding/reranking | Sentence Transformers, Hugging Face Transformers | Bi-encoders, cross-encoders, model loading/training |
| Sparse retrieval | Lucene/Elasticsearch/OpenSearch, PostgreSQL FTS | Inverted-index and lexical ranking |
| Dense index | FAISS, ScaNN, vector databases | Exact/approximate nearest neighbors |
| NVIDIA retrieval stack | Nemotron retrieval/embedding/reranking models, NeMo Retriever components | NVIDIA-centered retrieval models and workflows |
| Evaluation | custom labeled harness, BEIR/MTEB-style benchmarks where relevant | Compare models and retrieval strategies |

Public leaderboard results help shortlist models; they do not replace corpus-specific evaluation.

## 16. Common failure modes

| Symptom | Likely causes | Checks |
|---|---|---|
| Semantically related but unusable chunks | Wrong objective/domain or oversized chunks | Review hard negatives, chunk utility, reranker |
| Exact IDs are missed | Dense-only retrieval | Add lexical/hybrid path and field-aware rules |
| Scores suddenly shift | Model/preprocessing/normalization changed | Pin and trace model, tokenizer, prefixes, metric |
| Fewer than $k$ after filtering | Post-filter or narrow tenant subset | Pre-filter/iterative scan, enlarge candidate pool |
| High offline recall, poor answers | Relevant document but wrong passage/context | Passage labels, chunking, reranking, generator-use eval |
| Duplicated context | Document versions/overlap/near duplicates | Canonical IDs, deduplication, diversity |
| Cross-tenant result | Missing or stale ACL metadata/filter | Authorization-before-retrieval tests and cache scope |
| ANN recall regression | Changed data distribution/index parameters | Compare against exact search and rebuild/tune |

## 17. Common interview traps

- Calling an embedding “meaning” without naming its training objective and task.
- Treating cosine score as a confidence probability.
- Assuming higher dimension always means better retrieval.
- Comparing raw BM25 and cosine scores without calibration/fusion.
- Saying HNSW is always better than IVF without scale, memory, update, and filter evidence.
- Measuring only end-to-end answer quality and hiding weak retrieval.
- Applying tenant filters after unauthorized chunks enter prompts or logs.
- Switching embedding models without re-embedding and versioning the corpus.
- Evaluating with random easy queries rather than hard, temporal, multilingual, and exact-term cases.

## 18. Rapid interview questions and answers

1. **Cosine versus dot product?** Cosine removes magnitude; dot product includes it. They rank equivalently for unit-normalized vectors.
2. **Why a bi-encoder?** Independent document embeddings can be precomputed and searched efficiently.
3. **Why a cross-encoder?** Joint query-document attention improves relevance scoring but is too costly for the entire corpus.
4. **Exact versus ANN?** Exact returns true nearest neighbors; ANN trades some recall for speed/memory.
5. **HNSW `ef_search` effect?** Broader graph exploration generally improves recall and increases query work/latency.
6. **Why hybrid search?** Lexical and dense retrieval cover different failure modes.
7. **Why RRF?** It fuses rank lists without assuming comparable raw scores.
8. **What is retrieval Recall@K?** Fraction of known relevant items found in the top $K$.
9. **What must be versioned?** Model/tokenizer, prefixes, preprocessing, dimension, metric, index parameters, corpus/chunk version, and filters.
10. **How test filters?** Use selective, empty, revoked, cross-tenant, concurrent-update, and cache-isolation cases.

## 19. Lead-level design case

**Question:** Search 20 million multilingual support articles with p95 under 300 ms and strict tenant access.

**Strong answer structure:**

1. Define languages, relevance labels, exact-term needs, update rate, tenant distribution, p95 budget, availability, and cost.
2. Build lexical and small exact-dense baselines; create a group/time-aware query set with hard negatives.
3. Select multilingual embedding/reranker candidates using representative queries and licenses.
4. Enforce tenant/ACL eligibility inside retrieval; test highly selective tenants and revocation lag.
5. Benchmark HNSW/IVF or managed alternatives against exact-neighbor recall, memory, build/update, and concurrent latency.
6. Retrieve sparse and dense candidates, fuse with tuned RRF/weights, rerank a bounded set, and deduplicate.
7. Partition/replicate only with evidence; plan incremental indexing, deletion, backups, and re-embedding migration.
8. Trace query, index/model versions, filters, returned IDs/scores, latency stages, and authorization decisions without leaking content.
9. Canary changes and gate on Recall@K/NDCG, p95/p99, filter correctness, empty rate, and downstream success.
10. Retain rollback to the prior model/index and a lexical degraded mode.

## 20. Final revision checklist

- [ ] I can derive cosine, dot product, and Euclidean relationships.
- [ ] I can compare sparse, dense, multi-vector, bi-encoder, and cross-encoder retrieval.
- [ ] I understand exact search, HNSW, IVF, and product quantization.
- [ ] I can explain hybrid fusion and implement RRF.
- [ ] I can size raw vector storage and name index overheads.
- [ ] I can design secure metadata filtering and tenant isolation.
- [ ] I can evaluate ANN recall separately from business relevance.
- [ ] I can choose a vector/search system based on data and operational constraints.
- [ ] I can diagnose score drift, duplicates, filter starvation, and model mismatch.

## Primary references

- [Sentence Transformers: Retrieve and Re-Rank](https://www.sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html)
- [FAISS documentation](https://faiss.ai/)
- [pgvector documentation](https://github.com/pgvector/pgvector)
- [Elasticsearch hybrid search documentation](https://www.elastic.co/docs/solutions/search/hybrid-search)
- [Qdrant hybrid queries](https://qdrant.tech/documentation/hybrid-queries/)
- [ColBERTv2](https://aclanthology.org/2022.naacl-main.272/)
