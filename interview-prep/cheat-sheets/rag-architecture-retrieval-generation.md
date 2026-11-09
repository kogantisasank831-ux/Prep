---
layout: "week"
status: "approved"
version: "1.0.0"
last_reviewed: "2026-11-09"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "RAG architecture, retrieval, and generation interview cheat sheet"
description: "End-to-end RAG design covering query transformation, staged retrieval, reranking, context assembly, generation, citations, and abstention."
summary: "Revise RAG boundaries, request contracts, hybrid retrieval, reranking, context budgets, grounded prompts, citations, and conversation-aware retrieval."
permalink: "/interview-prep/cheat-sheets/rag-architecture-retrieval-generation/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 3 · RAG architecture"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 3 source:** This page integrates the prepared revision artifact into the Prep site. It is separate from the Week 1–20 learning assessments.

**Target roles:** Generative AI Engineer, RAG Engineer, Agentic AI Engineer, ML Engineer, Senior/Lead Data Scientist  
**Use:** explain, design, implement, and debug an end-to-end retrieval-augmented generation system  
**Boundary:** evaluation, security testing, and production release gates are expanded in the next sheet.

## 1. Thirty-second revision

- RAG retrieves external evidence at inference time and supplies it to a generator; it does not retrain the model or guarantee truth.
- Separate offline ingestion/indexing from online query/retrieval/generation paths.
- A strong pipeline may perform query understanding, hard filters, sparse+dense retrieval, fusion, reranking, deduplication, context assembly, generation, and citation validation.
- Retrieve a wider candidate set and rerank a smaller set; choose sizes using recall, latency, and token-budget evidence.
- Query rewriting can improve retrieval but may remove names, constraints, or intent. Preserve the original query and evaluate both.
- Hybrid retrieval handles semantic and exact-term cases. RRF fuses ranks without assuming comparable raw scores.
- Retrieved content is untrusted data. Delimit it, retain provenance, and never let it grant permissions or tool authority.
- Citations require stable source IDs and claim-support validation; displaying the nearest chunks is not citation correctness.
- RAG should abstain when evidence is missing, unauthorized, stale, contradictory, or insufficient.
- Diagnose component-by-component: answer failure may come from ingestion, retrieval, reranking, context packing, prompting, model, or validation.

## 2. What RAG is—and is not

RAG combines:

- **parametric memory:** knowledge and behavior in model weights;
- **non-parametric memory:** retrievable documents, rows, graph facts, tools, or other external state.

The original RAG research combined a neural retriever over a dense Wikipedia index with a sequence generator. In production, “RAG” now covers many retrieval and grounding designs.

### RAG is useful when

- knowledge changes frequently;
- private/domain evidence must be used;
- citations/provenance are required;
- a smaller model can succeed with the right context;
- access must be enforced per source/document.

### RAG is not automatically best when

- the task is deterministic lookup/calculation that SQL or code can answer;
- the model already performs the stable task without external knowledge;
- no reliable corpus or relevance signal exists;
- latency/cost prohibits retrieval/generation;
- the requested behavior, not knowledge, is the main gap—fine-tuning may help.

## 3. Reference architecture

### Offline path

Sources → parse/OCR → canonical elements → clean/deduplicate → chunk → embed → lexical/vector/metadata indexes → validation → publish.

### Online path

User/context → authentication/authorization → query understanding → retrieval → fusion/rerank → context assembly → grounded prompt → generation → validation/citations → response/trace.

Keep the online path read-only unless the use case explicitly includes controlled actions. RAG answers should not silently become agent actions.

## 4. Online request contract

Clarify:

- user/service identity and tenant;
- question and conversation/session ID;
- permitted collections and effective time;
- language/locale;
- latency and token/cost budget;
- required output schema and citations;
- answerability/refusal policy;
- risk tier and human-review requirement.

Reject or clarify an ambiguous high-impact request before spending tokens.

## 5. Query understanding

### Classification and routing

Classify whether the request needs:

- no retrieval;
- lexical/dense document search;
- SQL/structured data;
- graph traversal;
- web/current information;
- calculation or another tool;
- human escalation.

A deterministic rule can outperform an LLM router for stable, high-risk cases.

### Entity and constraint extraction

Extract product IDs, dates, jurisdictions, document types, language, and filters. Validate them against known values and authorization.

### Standalone-question rewriting

Resolve conversational references such as “What about the previous contract?” using session context. Preserve the original query in the trace and prevent the rewrite from inventing entities.

## 6. Query transformation techniques

| Technique | Method | Benefit | Risk |
|---|---|---|---|
| Rewrite | Produce clearer search query | Resolves verbosity/coreference | Drops constraints or changes intent |
| Expansion | Add aliases/synonyms | Improves recall | Adds noisy concepts |
| Multi-query | Generate several formulations | Covers multiple vocabulary/angles | More calls and duplicate results |
| Decomposition | Split a multi-part question | Retrieves evidence per subproblem | Error propagation and synthesis complexity |
| HyDE | Generate a hypothetical relevant document, embed it | Bridges query-document style gap | Extra latency and hallucinated retrieval direction |
| Step-back query | Search a broader underlying concept | Finds background/context | Can become too generic |

Always retain the original query and run ablations. More transformations do not guarantee better retrieval.

## 7. Retrieval stages

A practical stack may be:

1. apply tenant/ACL/effective-date filters;
2. retrieve lexical candidates;
3. retrieve dense or multi-vector candidates;
4. fuse rank lists;
5. rerank a bounded union;
6. deduplicate and diversify;
7. expand parent/neighbor context;
8. enforce final token budget and provenance.

Not every use case requires all stages. Start with a baseline and add complexity only when a labeled failure slice improves.

## 8. Candidate count: `fetch_k` versus `top_k`

- `fetch_k`: candidates requested from first-stage retrieval.
- rerank depth: candidates scored by the stronger reranker.
- `top_k`: chunks/parents retained for context.

Increasing `fetch_k` can improve recall but adds ANN/search, fusion, network, and reranker work. Increasing final `top_k` can add evidence but also noise and context cost.

Tune these independently using retrieval labels and answer outcomes.

## 9. Hybrid retrieval and fusion

Run sparse and dense retrieval over compatible filters. Combine by:

- weighted/normalized scores;
- Reciprocal Rank Fusion;
- learned ranker;
- rules for exact fields/IDs.

RRF is a strong starting point because it uses rank positions. A learned fusion model may outperform it when sufficient unbiased relevance data exists, but requires feature/version monitoring.

## 10. Reranking

### Cross-encoder

Jointly processes query and candidate. Strong relevance quality, bounded by pairwise inference cost and input length.

### LLM reranking

Can apply nuanced instructions and pair/listwise reasoning but adds latency, cost, nondeterminism, and prompt-injection exposure. Use only when it wins measured high-value cases.

### Rule/business reranking

Boost authoritative/current/approved sources or exact product/jurisdiction matches. Keep rules auditable and avoid hiding poor base retrieval.

### Reranking inputs

Include useful title/section metadata, but do not exceed the reranker's token limit or allow untrusted text to masquerade as control instructions.

## 11. Deduplication and diversity

Remove duplicates by:

- canonical source/version/chunk ID;
- parent section/document ID;
- content hash or near-duplicate similarity;
- overlapping-window provenance.

Use MMR or coverage rules when the answer requires multiple aspects. Preserve the strongest supporting chunk even if similar evidence is removed.

## 12. Context assembly

Context assembly decides what the generator actually sees.

### Token budget

$$
B_{context}=B_{window}-B_{system}-B_{history}-B_{user}-B_{output}-B_{safety}
$$

Pack chunks by marginal utility, authority, evidence coverage, and diversity—not only retrieval score.

### Useful context format

For each evidence block include:

- stable source/chunk ID;
- title/section/effective date;
- delimited content;
- optional page/location;
- clear statement that content is data, not instructions.

Avoid mixing retrieved evidence into the system message.

### Lost-in-the-middle concern

Models may use evidence differently based on position and context length. Test placement and put the most critical evidence where the chosen model reliably uses it; do not rely on one universal ordering rule.

## 13. Context compression

Options:

- extract query-relevant sentences/spans;
- summarize a parent section;
- remove duplicate boilerplate;
- rerank smaller units inside a retrieved parent;
- structured projection of only required fields.

Compression saves tokens but can remove qualifiers, negation, numbers, or provenance. Retain source text for citation validation and audit.

## 14. Grounded generation prompt

A grounded prompt contract should specify:

- answer only from supplied authorized evidence for factual claims;
- cite source IDs next to supported claims;
- distinguish evidence from instructions;
- report conflicts/uncertainty;
- abstain when evidence is insufficient;
- follow an output schema;
- never invent source IDs.

Prompt instructions reduce risk but do not prove grounding. Validate outputs.

## 15. Citation design

### Citation pipeline

1. pass immutable evidence IDs to the model;
2. restrict citations to supplied IDs;
3. parse cited IDs from structured output;
4. verify IDs were retrieved and authorized;
5. check each material claim against cited evidence;
6. render human-friendly title/page/URL from trusted metadata.

### Metrics

- citation precision: cited sources that support claims / cited sources;
- citation recall/coverage: support-requiring claims with a valid citation / all support-requiring claims;
- source correctness: cited ID/location maps to the intended source version.

“Sources” listed at the end without claim mapping are weaker than inline claim citations.

## 16. Answerability and abstention

No single similarity threshold is universally reliable. Combine signals:

- retrieval/reranker scores and score margin;
- presence of required entities/dates;
- evidence agreement/contradiction;
- answerability classifier or verifier;
- citation/claim support;
- source authority and freshness;
- task risk.

Tune thresholds on labeled answerable/unanswerable cases. High-risk questions should prefer safe escalation over confident guessing.

## 17. Provider-neutral Python architecture

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class SearchRequest:
    query: str
    tenant_id: str
    principal_id: str
    top_k: int = 5


@dataclass(frozen=True, slots=True)
class Evidence:
    chunk_id: str
    document_id: str
    text: str
    score: float
    citation_label: str


@dataclass(frozen=True, slots=True)
class GroundedAnswer:
    text: str
    cited_chunk_ids: tuple[str, ...]
    abstained: bool


class Retriever(Protocol):
    def retrieve(self, request: SearchRequest) -> list[Evidence]: ...


class Generator(Protocol):
    def generate(self, query: str, evidence: list[Evidence]) -> GroundedAnswer: ...


class CitationValidator(Protocol):
    def validate(self, answer: GroundedAnswer, evidence: list[Evidence]) -> None: ...


class RagService:
    def __init__(
        self,
        retriever: Retriever,
        generator: Generator,
        citation_validator: CitationValidator,
    ) -> None:
        self._retriever = retriever
        self._generator = generator
        self._citation_validator = citation_validator

    def answer(self, request: SearchRequest) -> GroundedAnswer:
        if not request.query.strip():
            raise ValueError("query cannot be empty")
        evidence = self._retriever.retrieve(request)
        if not evidence:
            return GroundedAnswer(
                text="I do not have sufficient authorized evidence.",
                cited_chunk_ids=(),
                abstained=True,
            )
        answer = self._generator.generate(request.query, evidence)
        self._citation_validator.validate(answer, evidence)
        return answer
```

Production adapters add async I/O, deadlines, tracing, retries, filtering, and error policies. The interfaces keep retrieval and generation independently testable.

## 18. Conversation-aware RAG

Challenges:

- coreference and omitted constraints;
- accumulating irrelevant history;
- stale facts and permissions;
- user correction versus source truth;
- memory poisoning.

Approach:

1. maintain structured session state separately from raw transcript;
2. rewrite a standalone query while preserving original constraints;
3. retrieve using current authorization and current source versions;
4. include only relevant history;
5. do not let conversation memory bypass evidence or policy.

## 19. Caching

### Retrieval cache

Cache query/filter/index-version → candidate IDs. Include tenant/ACL/effective-time context and invalidate on relevant changes.

### Embedding cache

Cache canonical text + model/prefix/preprocessing version → vector. Do not reuse across incompatible versions.

### Response/semantic cache

High risk for private/fresh data. Scope by permissions, corpus version, prompt/model version, locale, and policy. Revalidate access and freshness before returning.

Cache hits should be observable but should not bypass authorization.

## 20. Structured and database retrieval

Vector search is not the answer to every query.

- Use SQL/OLAP for exact filters, aggregates, and current transactional facts.
- Use APIs for authoritative operational state.
- Use a calculator for arithmetic.
- Use knowledge graphs for explicit multi-hop relationships when graph construction/maintenance is justified.
- Combine deterministic facts with document evidence using typed contracts.

Never execute model-generated SQL against broad production permissions without validation, allowlists, limits, and isolation.

## 21. Advanced RAG patterns

### Corrective RAG

Assess retrieved evidence and retry/rewrite/use another source when it appears inadequate. Bound retries and define a final abstention path.

### Adaptive RAG

Route questions to no retrieval, simple retrieval, or multi-step retrieval based on complexity/risk. Router errors become a new evaluation target.

### Agentic RAG

An agent chooses retrieval tools and iterates. Useful for heterogeneous sources and multi-step research; adds loop, cost, security, and reproducibility risks. Prefer a deterministic pipeline when the workflow is known.

### RAPTOR

Clusters and recursively summarizes chunks into a tree, enabling retrieval at multiple abstraction levels. Useful for broad long-document questions; indexing/summarization cost and summary faithfulness require evaluation.

### GraphRAG

Extracts entities/relationships and community summaries for local/entity and global/theme questions. It can improve corpus-level synthesis but graph extraction/indexing is expensive and lossy; it is not a default replacement for text retrieval.

### Multimodal RAG

Retrieve text, images, tables, audio, or video regions with modality-aware representations and citations. Evaluate whether the generator actually uses the non-text evidence correctly.

## 22. RAG framework map

| Library/platform | Primary use | What to know |
|---|---|---|
| LangChain | Retrieval/model/tool components and integrations | Retrievers, runnables/chains, document loaders, vector stores; architecture remains your responsibility |
| LlamaIndex | Data-centric indexes, retrievers, query engines, workflows, evaluation | Node/document model, retriever/query-engine composition, metadata filters |
| Haystack | Component pipelines for search/RAG/agents | Typed components, document stores, retrievers, rankers, generators, evaluation |
| Elasticsearch/OpenSearch | Lexical/vector/hybrid search platform | Query DSL, filters, ANN, hybrid fusion, operations/security |
| Vector databases | Vector/metadata retrieval | Index/filter semantics, tenancy, deletion, backup, cost |
| DSPy | Optimize modular LM programs against metrics | Signatures/modules/optimizers; needs representative data and metric |
| LiteLLM/gateways | Model-provider abstraction/routing | Provider differences, deadlines, fallbacks, budgets, observability |

Framework convenience does not remove the need for access control, evaluation, tracing, and explicit failure handling.

## 23. Latency and cost budgeting

Break down end-to-end latency:

$$
T=T_{auth}+T_{rewrite}+T_{embed}+T_{retrieve}+T_{rerank}+T_{prompt}+T_{generation}+T_{validate}
$$

Control with:

- parallel independent sparse/dense searches;
- bounded candidate/rerank/context sizes;
- appropriately small embedding/reranker models;
- connection pooling and colocated services;
- safe caching;
- streaming only after required safety/citation approach is defined;
- total deadline and graceful degradation.

Optimize cost per successful grounded answer, not cost per model call.

## 24. Debugging by component

| Failure | First questions |
|---|---|
| Correct source not indexed | Was source discovered, parsed, chunked, embedded, published, and permitted? |
| Correct source indexed but not retrieved | Query transformation, filters, embedding, lexical terms, ANN recall, candidate depth? |
| Retrieved but not retained | Fusion, reranker, dedup, parent mapping, context budget? |
| In context but answer wrong | Prompt, evidence position, model capability, conflicting chunks, output limit? |
| Answer correct but citation wrong | Evidence IDs, claim mapping, rendering metadata, validator? |
| Intermittent failure | Version skew, cache, replica freshness, timeout/retry, nondeterministic rewrite/rerank? |

Store replayable stage outputs with privacy controls so a failure can be reproduced.

## 25. Common interview traps

- Saying RAG “eliminates hallucination.”
- Retrieving directly from raw documents with no version/permission model.
- Using only dense search for IDs and exact terminology.
- Adding multiple query transformations without ablation evidence.
- Sending top similarity results directly to the model with no dedup/context budget.
- Treating retrieved documents as trusted instructions.
- Displaying sources without validating claim support.
- Using a similarity threshold as a universal confidence score.
- Calling every multi-step retrieval pipeline an agent.
- Optimizing answer style while retrieval recall is poor.

## 26. Rapid interview questions and answers

1. **RAG versus fine-tuning?** RAG supplies external evidence at inference; fine-tuning changes model parameters/behavior.
2. **Why hybrid retrieval?** It combines exact lexical and semantic dense strengths.
3. **Why rerank?** First-stage retrieval scales; a stronger model improves ordering over a bounded candidate set.
4. **`fetch_k` versus `top_k`?** `fetch_k` is the broad candidate pool; `top_k` is the final retained evidence count.
5. **Why rewrite a query?** Resolve conversational or poorly phrased queries, while preserving original intent and constraints.
6. **What is HyDE?** Generate a hypothetical relevant document, embed it, and retrieve real documents near it.
7. **How prevent unsupported answers?** Strong retrieval, evidence-only prompt, answerability/claim checks, valid citations, and abstention.
8. **How cite correctly?** Preserve immutable IDs/locations, restrict outputs to retrieved IDs, and verify each claim's support.
9. **When use GraphRAG?** Corpus-level themes/entity relationships justify expensive graph extraction and outperform simpler retrieval on target cases.
10. **How debug RAG?** Trace and evaluate ingestion, retrieval, reranking, packing, generation, and validation separately.

## 27. Lead-level design case

**Question:** Build an internal policy assistant that must answer by country, employee type, and effective date with inline citations.

**Strong answer structure:**

1. Define users, policy owners, jurisdictions, temporal semantics, answer risk, latency, and escalation path.
2. Ingest immutable policy versions with section/page provenance, authoritative status, country/employee/effective intervals, and ACLs.
3. Build labeled answerable/unanswerable/contradictory queries and exact-term plus semantic baselines.
4. Extract and validate filters; enforce authorization and point-in-time eligibility inside retrieval.
5. Run hybrid retrieval, fuse/rerank, deduplicate versions, and pack evidence by authority and token utility.
6. Generate structured answers with claim-level source IDs; validate IDs, effective dates, and entailment.
7. Abstain/escalate on missing or conflicting policy and show the conflict rather than silently choose.
8. Trace every stage/version and monitor retrieval recall, citation correctness, unsupported-claim rate, p95, freshness, and cost.
9. Canary model/retriever/chunk changes against the fixed evaluation set and high-risk slices.
10. Support rollback, immediate revocation/deletion, and an owner workflow for confirmed content errors.

## 28. Final revision checklist

- [ ] I can draw offline and online RAG paths.
- [ ] I can design query routing, rewriting, expansion, decomposition, and HyDE with trade-offs.
- [ ] I can choose candidate depth, hybrid fusion, reranking, deduplication, and context expansion.
- [ ] I can assemble a token-budgeted prompt with untrusted evidence and provenance.
- [ ] I can design claim-level citations and abstention.
- [ ] I can handle conversation history, structured data, caching, and current authorization.
- [ ] I can compare simple, corrective, adaptive, agentic, RAPTOR, GraphRAG, and multimodal RAG.
- [ ] I can budget latency/cost and debug each pipeline component.
- [ ] I can explain what frameworks help with and what they do not guarantee.

## Primary references

- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://papers.nips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html)
- [Precise Zero-Shot Dense Retrieval without Relevance Labels (HyDE)](https://aclanthology.org/2023.acl-long.99/)
- [RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval](https://proceedings.iclr.cc/paper_files/paper/2024/hash/8a2acd174940dbca361a6398a4f9df91-Abstract-Conference.html)
- [Microsoft GraphRAG documentation](https://microsoft.github.io/graphrag/)
- [Elasticsearch RAG documentation](https://www.elastic.co/docs/solutions/search/rag)
- [OWASP RAG Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html)
