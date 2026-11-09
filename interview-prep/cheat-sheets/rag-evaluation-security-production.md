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
title: "RAG evaluation, security, and production interview cheat sheet"
description: "RAG datasets, retrieval and generation metrics, release gates, adversarial testing, observability, reliability, and production operations."
summary: "Revise retrieval metrics, groundedness, citations, abstention, LLM-as-judge, human evaluation, prompt injection defenses, SLOs, and release decisions."
permalink: "/interview-prep/cheat-sheets/rag-evaluation-security-production/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 3 · RAG evaluation and production"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 3 source:** This page integrates the prepared revision artifact into the Prep site. It is separate from the Week 1–20 learning assessments.

**Target roles:** RAG/AI Engineer, ML Engineer, AI Security Engineer, Senior/Lead Data Scientist  
**Use:** evaluation design, release gates, security review, observability, and production operations  
**Interview rule:** separate retrieval quality, generation quality, end-to-end task success, security, and operations. One aggregate judge score cannot establish readiness.

## 1. Thirty-second revision

- Build a versioned evaluation set from real tasks, confirmed failures, edge cases, and adversarial cases; preserve train/eval separation.
- Retrieval metrics need query-to-relevant-document or chunk labels: Recall@K, Precision@K, Hit Rate, MRR, MAP, and NDCG.
- Generation metrics include correctness, completeness, faithfulness/groundedness, answer relevance, citation precision/coverage, and abstention quality.
- Evaluate components independently and end-to-end. A correct answer can hide bad retrieval, and high retrieval recall can still produce a wrong answer.
- LLM judges are instruments with position, verbosity, style, and self-preference biases. Calibrate them against human labels and deterministic checks.
- Slice results by source, format, language, tenant, query type, answerability, length, freshness, risk, and evidence position.
- RAG adds attack surfaces: poisoned documents, indirect prompt injection, cross-tenant retrieval, stale ACLs, cache leakage, citation tampering, and incomplete deletion.
- Enforce authorization before retrieval/model context. Treat retrieved content as untrusted data and validate citations/output.
- Trace stage latency, versions, filters, IDs, scores, and decisions with privacy-safe logging.
- Release through offline gates, shadow/canary comparison, monitored rollout, and rollback tied to exact model/index/prompt versions.

## 2. Evaluation starts with the decision

Define what the system must help a user do:

- find a relevant source;
- answer a factual question;
- synthesize several sources;
- extract structured fields;
- decide whether evidence is sufficient;
- cite an authoritative current policy;
- route/escalate a case.

Then define failure severity and acceptance thresholds per risk tier. A low-stakes FAQ and a compliance assistant should not share one release threshold.

## 3. Evaluation record schema

A useful test case contains:

- stable case ID and version;
- user query and relevant conversation context;
- principal/tenant/permissions and effective time;
- expected route/tool/source collection;
- relevant document/chunk IDs and graded relevance when known;
- reference answer or key facts;
- required/forbidden claims;
- expected citations;
- answerable/unanswerable/conflict label;
- language/domain/risk slices;
- provenance and reviewer/adjudication status.

Avoid copying production PII/secrets into a test set. Redact or synthesize while preserving the failure structure.

## 4. Building a representative dataset

Combine:

- frequent real user intents;
- business-critical rare tasks;
- confirmed production failures;
- known-answer expert-authored cases;
- recent/freshness and point-in-time cases;
- multilingual, typo, acronym, ID, numeric, table, and long-document queries;
- no-answer and contradictory-source cases;
- authorization and adversarial cases;
- paraphrase/format perturbations.

Synthetic question generation can expand coverage but may be easier and stylistically closer to the documents than real queries. Sample and adjudicate synthetic cases; keep a human-authored holdout.

## 5. Retrieval relevance labels

Labels can be:

- binary relevant/not relevant;
- graded relevance (for example, 0/1/2/3);
- evidence completeness sets for multi-document questions;
- source-authority labels;
- passage utility: can this chunk help the generator answer?

Document-level labels may overstate chunk retrieval quality. If the answer depends on one section, label at passage/chunk level or preserve both.

Use more than one reviewer for ambiguous cases and record adjudication rules.

## 6. Precision@K and Recall@K

Let $R_K$ be the top-$K$ retrieved items and $G$ the set of known relevant items.

$$
\operatorname{Precision@K}=\frac{|R_K\cap G|}{K}
$$

$$
\operatorname{Recall@K}=\frac{|R_K\cap G|}{|G|}
$$

- Precision rewards focused result sets.
- Recall rewards finding all relevant evidence.
- In RAG, high candidate Recall@K is often important before reranking, while final context needs precision and utility.

If relevance labels are incomplete, measured precision can punish an unlabeled but valid result.

## 7. Hit Rate and MRR

### Hit Rate@K

Whether at least one relevant item appears in the top $K$, averaged over queries.

### Reciprocal Rank

For first relevant result at rank $r$:

$$
RR=\frac{1}{r}
$$

Mean Reciprocal Rank averages $RR$ across queries. It emphasizes the first relevant result and does not reward additional relevant items.

```python
from __future__ import annotations

from collections.abc import Sequence, Set


def recall_at_k(
    retrieved: Sequence[str],
    relevant: Set[str],
    k: int,
) -> float:
    if k <= 0:
        raise ValueError("k must be positive")
    if not relevant:
        raise ValueError("relevant set cannot be empty")
    return len(set(retrieved[:k]) & relevant) / len(relevant)


def reciprocal_rank(retrieved: Sequence[str], relevant: Set[str]) -> float:
    for rank, item_id in enumerate(retrieved, start=1):
        if item_id in relevant:
            return 1.0 / rank
    return 0.0
```

Define duplicate handling and label scope before computing metrics.

## 8. MAP and NDCG

### Average Precision

Average the precision at each rank where a relevant item occurs; MAP averages this across queries. It rewards ranking all binary-relevant items early.

### NDCG

Discounted cumulative gain supports graded relevance:

$$
DCG@K=\sum_{i=1}^{K}\frac{2^{rel_i}-1}{\log_2(i+1)}
$$

$$
NDCG@K=\frac{DCG@K}{IDCG@K}
$$

NDCG captures ordering and relevance grade, but grading consistency matters.

## 9. Retrieval evaluation layers

Measure:

1. source discovery/ingestion coverage;
2. exact-search model quality;
3. ANN recall versus exact neighbors;
4. relevance before fusion;
5. relevance after fusion/reranking;
6. final context utility after dedup/packing;
7. access-control and temporal correctness;
8. latency, memory, cost, and empty-result rate.

This separates an embedding problem from an ANN/index or reranking problem.

## 10. Generation quality dimensions

| Dimension | Question |
|---|---|
| Correctness | Does the answer match known facts/reference? |
| Completeness | Does it cover required aspects without omitting critical constraints? |
| Faithfulness/groundedness | Are factual claims supported by supplied evidence? |
| Answer relevance | Does it answer the user's question directly? |
| Instruction/schema adherence | Does it follow required format and policy? |
| Citation correctness | Do cited sources support nearby claims and map to the right version/location? |
| Abstention | Does it refuse/escalate when evidence is insufficient? |
| Safety/privacy | Does it avoid prohibited disclosure or action? |

Fluency and confidence are not evidence of correctness.

## 11. Claim-level groundedness

One practical method:

1. split the answer into material factual claims;
2. map each claim to cited/retrieved evidence;
3. label supported, contradicted, or not supported;
4. weight critical claims if appropriate;
5. separately record citation validity.

This is more diagnostic than one answer-level score. Human or model-based entailment can be used, but calibrate the procedure.

## 12. Citation evaluation

For support-requiring claims:

$$
\text{Citation coverage}=
\frac{\text{claims with at least one supporting citation}}
{\text{support-requiring claims}}
$$

Also measure:

- citation precision/support;
- source ID validity;
- page/span correctness;
- authority and effective-date correctness;
- citation completeness for multi-source claims;
- tampering or invented IDs.

Do not award credit merely because a citation is topically related.

## 13. Answerability and abstention metrics

Treat answerability as a decision problem:

- true positive: answers an answerable question correctly;
- false positive: answers when evidence is insufficient or unauthorized;
- true negative: abstains/escalates correctly;
- false negative: abstains despite sufficient evidence.

Measure precision/recall for answering, plus task-specific cost. High-risk systems should heavily penalize unsupported answers.

Tune thresholds on separate validation data; do not tune on the final test set.

## 14. Component versus end-to-end evaluation

### Component-level

- parser/table/OCR quality;
- chunk retrieval metrics;
- query rewrite preservation;
- fusion/reranker lift;
- context packing coverage;
- citation validator accuracy.

### End-to-end

- final task success;
- correctness/groundedness/citations;
- latency/cost;
- user or business outcome;
- safety/authorization.

Both are required. End-to-end alone is hard to diagnose; component metrics alone can optimize the wrong proxy.

## 15. Ablation strategy

Change one controlled factor at a time where feasible:

- lexical versus dense versus hybrid;
- chunk strategy/size/overlap;
- embedding model;
- exact versus ANN parameters;
- fusion method;
- reranker and depth;
- query rewrite/multi-query/HyDE;
- context count/order/compression;
- generator/prompt.

Use the same frozen dataset and corpus snapshot. Report confidence intervals or paired uncertainty when sample sizes allow.

## 16. LLM-as-judge

Benefits:

- scalable rubric evaluation of open-ended answers;
- pairwise comparisons;
- claim extraction/entailment assistance;
- analysis without exact lexical matches.

Risks:

- position/order bias;
- verbosity and style bias;
- self/model-family preference;
- weak specialist knowledge;
- sensitivity to prompt and evidence order;
- inconsistent scores and hidden provider changes.

Controls:

1. explicit rubric and examples;
2. randomize/swap pair order;
3. blind model/system identity;
4. use deterministic checks first;
5. calibrate against expert-labeled samples;
6. measure judge-human agreement and failure slices;
7. pin judge/prompt/version and retain raw reasoning-independent outputs;
8. route critical disagreements to humans.

## 17. Human evaluation

Use trained reviewers and a concise rubric. Define evidence access, allowed uncertainty, scoring examples, and adjudication.

Track:

- inter-rater agreement;
- time per case;
- disagreement categories;
- reviewer expertise/language;
- blind/randomized system order;
- unresolved cases.

Human preference is not always correctness; ask separate questions for factuality, support, usefulness, and style.

## 18. Evaluation framework map

| Tool | Primary role | Interview consideration |
|---|---|---|
| Ragas | RAG-focused metrics such as context precision and faithfulness | Metric inputs, judge dependence, prompt/model version |
| LangSmith | Dataset experiments, traces, offline/online evaluators | Framework-agnostic use, judge calibration, data governance |
| LlamaIndex evaluation | Retrieval and response evaluators | Ground-truth versus judge-based metrics |
| Haystack evaluation | Component and pipeline evaluators | Statistical versus model-based evaluators |
| TruLens | Feedback functions and RAG/agent evaluation | Groundedness/relevance instrumentation and judge limits |
| DeepEval | Test-style LLM/RAG metrics | Metric semantics, reproducibility, CI cost |
| Phoenix | Tracing and evaluation workflows | OpenTelemetry-style traces, dataset/evaluator management |
| MLflow GenAI evaluation | Experiment/run tracking and scorers | Versioned evaluation and production integration |
| Custom harness | Business rules, retrieval metrics, security and regression tests | Often the canonical release gate |

Framework metric names are not universal definitions. Document the exact formula, inputs, judge, and threshold.

## 19. Security threat model

Assets:

- private source documents and embeddings;
- permissions and identity mappings;
- prompts, queries, conversations, and traces;
- model/tool credentials;
- index integrity and availability;
- generated answers and citations.

Trust boundaries:

- external/source connectors;
- ingestion/parser/OCR services;
- document contributors;
- vector/search databases;
- model providers;
- caches and observability systems;
- downstream tools/actions.

Threat modeling is specific to the deployment; a generic prompt-injection filter is not sufficient.

## 20. Document poisoning

An attacker or compromised source introduces content intended to be retrieved and influence answers.

Controls:

- authenticated source provenance and contributor authorization;
- malware/content validation and quarantine;
- approval/status metadata and source allowlists for high-risk domains;
- immutable version/audit history;
- anomaly detection on index/source distributions;
- retrieval/display of authority/effective status;
- rapid quarantine and cache invalidation;
- poisoned-document evaluation cases.

Semantic similarity alone cannot distinguish authoritative from malicious content.

## 21. Indirect prompt injection

Retrieved text may contain instructions such as “ignore previous rules” or request data exfiltration.

Defense in depth:

- treat retrieved content as untrusted data with explicit delimiters;
- keep system/tool policies outside retrieved content;
- minimize context and scan/risk-score content where useful;
- prohibit documents from granting tool authority;
- validate all tool calls/outputs in application code;
- use least-privilege tools and human approval for consequential actions;
- test multi-document and encoded/obfuscated injections;
- monitor anomalous tool/retrieval behavior.

Detection patterns alone are bypassable; enforce capability boundaries.

## 22. Authorization and tenant isolation

Required controls:

- authenticate user and service identities;
- resolve current authoritative ACLs;
- filter eligible items inside retrieval;
- prevent unauthorized content from reaching prompts, rerankers, caches, logs, or judge services;
- scope caches and traces by tenant/security context;
- handle revocation and group changes within an explicit SLO;
- test cross-tenant queries, crafted filters, shared docs, and stale replicas.

An LLM refusal is not an authorization control.

## 23. Privacy and data protection

- minimize source/query/context sent to external models;
- classify and redact sensitive fields where appropriate;
- use approved regions/providers and retention settings;
- encrypt in transit/at rest and separate keys/access;
- avoid raw prompt/response logging by default;
- control evaluation dataset access and reviewer exposure;
- implement retention, deletion, and legal-hold requirements across derived stores;
- prevent embeddings from being treated as anonymized by assumption.

Privacy requirements come from responsible organizational/legal owners, not the RAG framework.

## 24. Additional RAG security tests

- unauthorized/cross-tenant retrieval;
- stale permission after revocation;
- poisoned document and malicious metadata;
- indirect prompt injection in one or multiple chunks;
- source/citation ID tampering;
- semantic/exact cache leakage;
- deleted document still retrievable/citable;
- oversized query/document context denial of service;
- malformed parser/OCR/archive inputs;
- hidden/white-on-white/encoded content;
- retrieval of secrets or regulated data;
- output triggering an unauthorized downstream tool.

Keep a regression case for every confirmed security incident.

## 25. Observability and trace design

Trace, with privacy controls:

- request/correlation ID and authorized principal/tenant reference;
- route/rewrite version and sanitized query fingerprint;
- embedding/reranker/generator model versions;
- corpus/index/chunk/prompt/policy versions;
- filters and authorization decision reference;
- retrieved/fused/reranked chunk IDs and scores;
- context token count and truncation;
- cited IDs and validator outcomes;
- abstention/fallback/escalation;
- stage latency, retries, tokens, and cost;
- final outcome/feedback when available.

Do not log raw sensitive content by default. Provide restricted, audited evidence capture for incident investigation.

## 26. SLOs and operational metrics

Examples:

- availability and successful grounded-answer rate;
- p50/p95/p99 end-to-end and per-stage latency;
- ingestion/search freshness;
- permission revocation and deletion completion time;
- retrieval empty rate and fallback rate;
- unsupported-claim and invalid-citation rate from sampled review;
- timeout, retry, provider, index, and validation failures;
- token/cost per successful answer;
- queue depth, saturation, cache hit rate, and index health.

SLO thresholds must reflect business risk and observed baselines.

## 27. Release gates

Before release:

1. pin corpus/index, parser/chunker, embedding, reranker, prompt, generator, and evaluator identities;
2. run deterministic/unit/schema tests;
3. run retrieval and end-to-end evaluation with critical slices;
4. run security/adversarial suite;
5. compare latency, capacity, cost, and operational errors;
6. inspect regressions and obtain required owner approval;
7. shadow/canary against the incumbent;
8. define rollback triggers and verify old artifacts remain usable.

Averages should not hide critical-slice failures.

## 28. Online evaluation

Useful signals:

- answer acceptance, reformulation, escalation, and confirmed correction;
- source opens/clicks only as weak behavior signals;
- sampled expert review;
- downstream task completion;
- latency, failure, fallback, and cost;
- A/B tests where risk and sample design allow.

User thumbs-up is sparse, biased, and ambiguous. Do not treat it as ground-truth correctness.

## 29. Drift and feedback loops

Monitor changes in:

- query intent/language/entity distribution;
- source formats and parser quality;
- corpus freshness and authority;
- retrieval scores/result overlap;
- answerability and escalation;
- model/provider behavior;
- security/adversarial patterns.

Only feed adjudicated, permission-safe examples back into prompts/training/evaluation. Automatic learning from raw user feedback can amplify abuse and errors.

## 30. Incident response

For poisoned or unauthorized content:

1. stop/quarantine affected source/version/index partition;
2. invalidate relevant retrieval/response caches;
3. identify requests that retrieved or cited it using trace IDs;
4. block downstream actions and notify responsible owners;
5. correct permissions/content and rebuild safely;
6. verify removal across replicas/derived stores;
7. add regression tests and document root cause;
8. restore through controlled rollout.

Prepare this runbook before an incident.

## 31. Common interview traps

- Reporting only answer relevance and calling it RAG quality.
- Using synthetic questions as the entire evaluation set.
- Measuring document-level recall when the needed passage is missing.
- Treating LLM judge scores as objective ground truth.
- Tuning thresholds on the final test set.
- Averaging away cross-tenant or high-risk failures.
- Sending unauthorized chunks to a model and relying on output redaction.
- Logging full prompts/documents for convenience.
- Claiming embeddings are anonymous.
- Releasing a new embedding index without versioned rollback.
- Treating successful canary traffic as proof of factual correctness.

## 32. Rapid interview questions and answers

1. **Recall@K versus Precision@K?** Recall measures relevant items found; precision measures how focused the top $K$ is.
2. **When use MRR?** When the rank of the first relevant result matters.
3. **Why NDCG?** It supports graded relevance and discounts lower ranks.
4. **Faithfulness versus correctness?** Faithfulness asks whether claims follow from context; correctness asks whether they are true/reference-aligned. A faithful answer can repeat wrong context.
5. **How evaluate citations?** Validate IDs and measure whether each support-requiring claim is supported by its cited source/location.
6. **Why component evaluation?** It locates whether failure came from retrieval, reranking, context, generation, or validation.
7. **How trust an LLM judge?** Calibrate on expert labels, measure agreement/bias, pin versions, and retain deterministic checks.
8. **Main RAG security risk?** There is no single one: poisoning, indirect injection, authorization, cache, privacy, and deletion all matter.
9. **Where enforce ACLs?** Before/during retrieval so unauthorized content never reaches downstream stages.
10. **What enables rollback?** Immutable, versioned corpus/index/model/prompt/config artifacts and a controlled pointer/alias switch.

## 33. Lead-level evaluation case

**Question:** Approve or reject a new RAG pipeline for a regulated policy assistant.

**Strong answer structure:**

1. Define decisions, risk tiers, owners, required authority/effective-date semantics, and explicit release thresholds.
2. Freeze candidate identities and corpus snapshot; construct expert-labeled answerable, no-answer, conflict, temporal, multilingual, and adversarial cases.
3. Measure ingestion coverage, candidate Recall@K, reranked NDCG/MRR, final context utility, correctness, groundedness, citation support/coverage, and abstention.
4. Report critical slices and paired regressions, not only averages; inspect every severe failure.
5. Calibrate any LLM judge against domain experts and deterministic source/date/schema checks.
6. Run cross-tenant, revoked-access, poisoning, indirect injection, cache, citation-tampering, deletion, and denial-of-service tests.
7. Load/capacity test p95/p99, freshness/revocation SLOs, provider failure, fallback, cost, and observability privacy.
8. Shadow/canary with human review and no autonomous high-impact action; define rollback triggers.
9. Require responsible data/security/product/domain approvals where applicable and document residual risk.
10. Release only if critical gates pass; convert failures into permanent regression cases and monitor online.

## 34. Final revision checklist

- [ ] I can define a representative, versioned RAG evaluation record.
- [ ] I can calculate and choose Precision@K, Recall@K, Hit Rate, MRR, MAP, and NDCG.
- [ ] I can evaluate correctness, completeness, groundedness, citations, and abstention.
- [ ] I can separate component, end-to-end, offline, and online evaluation.
- [ ] I can design ablations and calibrate human/LLM judging.
- [ ] I can threat-model ingestion, retrieval, context, cache, logging, and downstream tools.
- [ ] I can enforce and test current tenant/ACL boundaries.
- [ ] I can design privacy-safe traces, SLOs, release gates, canary, and rollback.
- [ ] I can respond to poisoned or unauthorized indexed content.

## Primary references

- [Ragas metrics documentation](https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/)
- [LlamaIndex evaluation documentation](https://docs.llamaindex.ai/en/stable/module_guides/evaluating/)
- [Haystack evaluation documentation](https://docs.haystack.deepset.ai/docs/evaluation)
- [LangSmith evaluation documentation](https://docs.smith.langchain.com/evaluation)
- [OWASP RAG Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html)
- [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/)
