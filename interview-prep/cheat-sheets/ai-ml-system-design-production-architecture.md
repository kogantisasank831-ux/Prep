---
layout: "week"
status: "approved"
version: "1.0.0"
last_reviewed: "2026-11-10"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "AI/ML system design and production architecture interview cheat sheet"
description: "Requirements, metrics, scale estimates, control and serving planes, storage, APIs, queues, tenancy, security, reliability, rollout, and operations."
summary: "Revise the complete AI system-design method from user outcome and capacity estimates through production architecture, failure handling, validation, and rollback."
permalink: "/interview-prep/cheat-sheets/ai-ml-system-design-production-architecture/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 5 · System design"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 5 source:** This page integrates the prepared revision artifact into the Prep site. It is separate from the Week 1–20 learning assessments.

**Target roles:** AI Engineer, ML Engineer, GenAI Engineer, Senior Data Scientist, ML/AI Platform Engineer, Data Science/AI Lead  
**Use:** system-design rounds, architecture reviews, scale estimation, reliability, security, and technical leadership  
**Interview rule:** do not begin with a model or framework. Begin with users, decisions, constraints, measurable outcomes, and failure cost.

## 1. Thirty-second revision

- Clarify users, business objective, scope, non-goals, risk, latency, scale, freshness, and cost before drawing architecture.
- Define business, model/quality, safety, and operational metrics separately.
- Establish a simple baseline and an incremental path; avoid designing the final global platform on day one.
- Separate the **data/control plane** from the **online serving/data plane** and identify every source of truth.
- Estimate requests, concurrency, data volume, model size, context/output length, storage growth, and peak capacity.
- Choose batch, synchronous online, asynchronous, streaming, or edge inference from the product contract.
- Design explicit APIs, schemas, idempotency, timeouts, backpressure, retries, and terminal states.
- Add data/model/prompt/index/agent lineage, evaluation, authorization, observability, rollout, and rollback.
- Discuss trade-offs: quality versus latency/cost, availability versus consistency, freshness versus complexity, and isolation versus utilization.
- Close with failure modes, degraded modes, monitoring, incident ownership, and the next validation experiment.

## 2. The interview structure

A strong answer follows eight stages:

1. **Clarify:** users, journey, decision/action, scope, risk, non-goals.
2. **Measure:** success, quality, safety, service, and cost metrics.
3. **Estimate:** traffic, concurrency, data, tokens, model memory, throughput, and growth.
4. **Baseline:** rules, small model, retrieval-only, or human process.
5. **Design:** data/label flow, training or indexing, online path, APIs, storage, and state.
6. **Protect:** security, privacy, tenant isolation, failure handling, and human oversight.
7. **Validate:** offline evaluation, load/security/fault tests, shadow/canary, and acceptance gates.
8. **Operate:** lineage, monitoring, rollback, incident response, feedback, and retirement.

State assumptions explicitly. An interviewer can correct an assumption; they cannot evaluate an invisible one.

## 3. Requirements checklist

### Functional

- What input arrives, from whom, and through which interface?
- What output, decision, recommendation, or external action is required?
- Is the response synchronous, streaming, asynchronous, or scheduled?
- Are retrieval, tools, human approval, explanations, or citations required?
- What is the fallback when the model cannot decide?

### Non-functional

| Dimension | Questions |
|---|---|
| Scale | average/peak request rate, concurrency, tenants, data growth |
| Latency | end-to-end and stage percentiles; streaming TTFT/TPOT |
| Availability | target, dependency failure behavior, disaster recovery |
| Freshness | source-to-feature/index/model delay |
| Quality | metric, slice, threshold source, confidence/uncertainty |
| Security/privacy | identity, permissions, retention, residency, audit |
| Cost | per request/outcome, monthly ceiling, GPU/provider budget |
| Operations | ownership, on-call, rollout, rollback, support lifecycle |

Do not invent targets. In an interview, propose reasonable assumptions and explain how measurements would replace them.

## 4. Metric hierarchy

| Layer | Example |
|---|---|
| Business outcome | resolved cases, fraud loss avoided, conversion, analyst hours saved |
| Product behavior | completion, acceptance, correction, escalation, abandonment |
| Model/RAG/agent quality | F1, calibration, groundedness, citation support, task success |
| Safety/guardrail | unauthorized action, harmful output, privacy or policy violation |
| Service | availability, p95 latency, timeout, rejection, freshness |
| Efficiency | tokens/request, GPU-hours, cost/success, cache hit, utilization |

Optimize the business outcome subject to safety, quality, service, and cost constraints. A model metric is usually a proxy, not the product objective.

## 5. Back-of-the-envelope estimation

Let:

- $\lambda$ = average arrival rate in requests/second;
- $W$ = average time in system in seconds;
- $L$ = average concurrent requests.

Little's Law:

$$
L = \lambda W
$$

For 20 requests/s averaging 2 seconds, average concurrency is about 40. Peak and tail behavior require headroom; averages alone are unsafe.

Estimate:

- peak-to-average ratio;
- input/output token percentiles;
- daily/monthly tokens and external calls;
- records/day and retained bytes;
- model replicas from measured goodput per replica;
- queue capacity from accepted waiting time;
- growth and reprocessing/backfill volume.

Always validate estimates under production-like load.

## 6. Reference architecture

### Control/offline plane

- source ingestion and validation;
- label/feedback processing;
- feature, document, or training dataset creation;
- training/fine-tuning/indexing/evaluation pipelines;
- experiment, artifact, prompt, and model registry;
- approval, deployment configuration, policy, and secrets;
- batch jobs, backfills, and deletion propagation.

### Online/data plane

- API gateway/authentication and request validation;
- routing/admission/rate limiting;
- online features, retrieval, model inference, tools/agents;
- state/session/cache/storage;
- response validation and external effects;
- telemetry and audit events.

### Cross-cutting

- identity/authorization, encryption, tenancy;
- configuration and lineage;
- observability and evaluation;
- queues, retries, idempotency, reconciliation;
- rollout, rollback, incident response, and disaster recovery.

Keep online serving independent of the training control plane where possible: a failed training job should not take down inference.

## 7. Batch, online, streaming, asynchronous, and edge

| Mode | Best for | Trade-off |
|---|---|---|
| Batch | scores/reports for many items on a schedule | high throughput, lower freshness |
| Synchronous online | interactive decisions with bounded latency | strict availability and tail-latency needs |
| Asynchronous job | long-running generation/research | requires job state, polling/webhook, cancellation |
| Event streaming | continuously changing facts/features | ordering, late data, replay, and state complexity |
| Edge/on-device | privacy, offline use, very low network latency | constrained memory/compute and update lifecycle |

One product may use several modes—for example, batch candidate generation plus online ranking.

## 8. API and job contracts

A production inference contract should define:

- versioned request/response schema;
- model/task selector and supported parameters;
- tenant/principal context outside model-controlled input;
- correlation and idempotency keys;
- synchronous versus job semantics;
- deadline, cancellation, pagination, streaming, and partial-result behavior;
- validation and stable error categories;
- resolved model/prompt/index/config metadata where safe;
- deprecation and compatibility policy.

For async jobs, expose `PENDING`, `RUNNING`, `WAITING`, `SUCCEEDED`, `FAILED`, `CANCELLED`, and `EXPIRED` states as applicable. A `200 OK` accepting a job is not proof the business task succeeded.

## 9. Data and label architecture

Define:

- authoritative sources and ownership;
- event time versus processing time;
- schema, quality, freshness, deduplication, and late-arrival rules;
- point-in-time-correct joins to prevent leakage;
- immutable raw layer and reproducible transformations where appropriate;
- label definition, observation window, maturation, censoring, and revision;
- feature/document lineage and deletion/permission propagation;
- training-serving consistency.

For GenAI, the “data plane” also includes prompts, exemplars, retrieval corpus, chunking, embeddings, rerankers, tools, policies, and memory.

## 10. Storage selection

| Need | Typical choice | Key question |
|---|---|---|
| Transactional state | relational/transactional database | consistency, indexes, transactions, tenancy |
| High-rate key lookup/session | key-value store/cache | TTL, eviction, persistence, hot keys |
| Analytics/training | object store + warehouse/lakehouse | partitioning, lineage, backfill, cost |
| Search | inverted index/search engine | ranking, filters, freshness, scale |
| Vector retrieval | vector index/database | metadata filters, recall, update/delete semantics |
| Events/jobs | log/broker/queue | ordering, delivery, replay, dead-letter behavior |
| Artifacts | object store + registry metadata | immutable digest, access, retention |

Choose a source of truth. A cache, vector index, and feature store are usually derived views and need rebuild/reconciliation paths.

## 11. Caches

Possible caches:

- API/result cache;
- feature/retrieval cache;
- embedding cache;
- prompt/prefix/KV cache;
- model artifact/kernel cache;
- agent node/tool cache.

For each define key, version namespace, TTL, invalidation, size/eviction, tenant scope, privacy, consistency, stampede protection, and fallback. A high hit rate can still be wrong if stale or cross-tenant.

## 12. Queues, load shedding, and backpressure

Queues absorb short bursts; they do not create capacity. Unbounded queues convert overload into extreme latency and memory failure.

Define:

- admission and per-tenant quotas;
- bounded queue and maximum waiting time;
- priority/fairness;
- retry and dead-letter handling;
- cancellation and expiration;
- load shedding or degraded responses;
- autoscaling signal and stabilization.

For LLM serving, waiting requests, token backlog, KV-cache pressure, and TTFT are often more useful than CPU alone.

## 13. Availability and consistency

Discuss:

- replication and failure domains;
- stateless versus stateful components;
- synchronous versus asynchronous writes;
- stale-read tolerance and freshness contract;
- regional failover and data residency;
- recovery point objective (RPO) and recovery time objective (RTO);
- dependency timeouts, circuit breakers, and bulkheads;
- degraded modes.

Examples of graceful degradation:

- cached or retrieval-only response;
- smaller accepted fallback model;
- disable optional reranking/tools;
- queue long work;
- safe abstention or human escalation.

Fallback must preserve schema, permissions, safety, and minimum accepted quality.

## 14. Multi-tenancy

Choose isolation level deliberately:

- shared model and infrastructure with logical tenant controls;
- separate indexes/caches/namespaces;
- separate process/node/pool;
- separate account/project/cluster for strict isolation.

Controls include tenant-bound identity, authorization before retrieval/action, quotas, fair scheduling, cache/index keys, encrypted storage, audit, and noisy-neighbor monitoring. Do not rely on a prompt to preserve isolation.

## 15. Security and privacy by design

- minimize collected and retained data;
- classify inputs, outputs, prompts, traces, labels, and artifacts;
- separate secrets from prompts/state;
- least-privilege workload and user credentials;
- validate model/tool output before execution/rendering;
- sandbox code and restrict network/filesystem access;
- scan dependencies, images, and model artifacts;
- implement deletion, consent, retention, and audit requirements;
- add adversarial and abuse tests.

For high-impact decisions, define human oversight, explanation/appeal, and deterministic policy enforcement outside the model.

## 16. Deployment and evolution

Use immutable candidate identity:

- code/image digest;
- model/tokenizer/adapters and generation defaults;
- feature/data/prompt/index/tool/policy versions;
- infrastructure and runtime configuration.

Rollout choices:

| Strategy | Purpose |
|---|---|
| Shadow | compare without affecting user response |
| Canary | expose a small controlled cohort |
| Blue-green | maintain fast environment switch/rollback |
| A/B | measure product outcome between accepted variants |
| Feature flag | disable or target a capability independently |

Roll back the complete bundle, not only the model alias.

## 17. Observability and operating model

Trace a logical outcome across gateway, features/retrieval, model, agent/tools, storage, and external effects.

Monitor:

- traffic, errors, saturation, queue, latency, availability;
- data/feature/index freshness and quality;
- model/RAG/agent behavior and delayed outcomes;
- safety, security, privacy, fairness where applicable;
- tokens, GPU/provider usage, and cost;
- telemetry completeness itself.

Every alert needs an owner, threshold source, response, runbook, and no-data behavior.

## 18. Common failure-mode questions

| Failure | Design response |
|---|---|
| Feature pipeline is stale | freshness gate, last-good snapshot, abstain/degrade, alert |
| Model provider times out | deadline, circuit breaker, accepted fallback or queue |
| Traffic spikes 10× | admission, bounded queue, load shed, pre-scaled headroom |
| New model quality regresses | shadow/canary gates, cohort metrics, rollback bundle |
| Duplicate job delivery | idempotency, operation ledger, consumer deduplication |
| Vector index update is partial | manifest/version, atomic alias switch, reconciliation |
| Telemetry disappears | explicit no-data alert; do not infer health |
| Tenant data appears in another response | containment, revoke access, audit, incident response |

## 19. Common interview traps

- Starting with “use Kubernetes and a vector DB” before requirements.
- Reporting only average traffic/latency.
- Treating model accuracy as the business metric.
- Ignoring labels, feedback, and deletion flows.
- Using a queue without bounded waiting or overload behavior.
- Assuming autoscaling is instantaneous.
- Calling a fallback safe without testing quality and permissions.
- Storing every prompt/response for observability without privacy controls.
- Omitting rollout, rollback, ownership, and incident response.
- Designing for massive scale with no incremental baseline.

## 20. Rapid interview questions

**Q1. What do you clarify first?**  
User journey, decision/action, failure cost, scale, latency, freshness, quality, safety, and non-goals.

**Q2. Why separate control and data planes?**  
To isolate training/configuration operations from the latency- and availability-critical serving path.

**Q3. Queue or autoscale?**  
Both may be needed: queues absorb bounded bursts; autoscaling adds delayed capacity. Admission/load shedding protects the SLO during the gap.

**Q4. How do you estimate concurrency?**  
Use Little’s Law as a baseline, then model peak arrivals and latency distributions and validate with load tests.

**Q5. What is a complete release identity?**  
Code/image, model/tokenizer, prompt/config, data/features/index, tools/policies, runtime, and deployment cohort.

**Q6. Shadow versus A/B?**  
Shadow evaluates a candidate without affecting responses; A/B intentionally changes user experience to measure outcomes.

**Q7. What is graceful degradation?**  
A safe reduced-capability path that preserves authorization, schema, minimum quality, and clear user expectations.

**Q8. How do you prove the architecture works?**  
Offline quality/security tests plus contract, integration, load, fault/recovery tests and a monitored progressive rollout.

## 21. Lead-level design case

**Prompt:** Design a multi-tenant enterprise AI gateway serving self-hosted and managed LLMs with RAG and agent tools.

A strong answer should:

1. define tenant classes, risk, data residency, model/tool policies, latency, and cost SLOs;
2. separate gateway/control plane, inference pools, retrieval services, and tool/action services;
3. authenticate users/workloads and authorize model, data, and actions server-side;
4. route by capability, risk, load, quality tier, and residency—not cost alone;
5. use bounded queues, token/concurrency quotas, cancellation, and backpressure;
6. maintain exact model/prompt/index/tool/policy lineage;
7. isolate tenant caches, indexes, traces, and budgets;
8. define fallback/abstention and human approval for consequential actions;
9. evaluate and canary every model-route combination;
10. monitor task success, TTFT/TPOT, queue, errors, safety, tokens, GPU/provider cost, and outcome.

## 22. Final checklist

- [ ] I start with users, outcome, risk, scale, and non-goals.
- [ ] I define business, quality, safety, service, and cost metrics.
- [ ] I can estimate traffic, concurrency, storage, and capacity.
- [ ] I can draw offline/control and online/data planes with sources of truth.
- [ ] I can justify storage, cache, queue, and inference-mode choices.
- [ ] I cover tenancy, authorization, privacy, failure handling, and degraded modes.
- [ ] I define exact lineage, evaluation, progressive rollout, and rollback.
- [ ] I close with monitoring, runbooks, ownership, and an incremental plan.

## 23. Primary references

- Google Cloud, [Machine learning system design](https://developers.google.com/machine-learning/guides/rules-of-ml)
- AWS, [Machine Learning Lens — Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/machine-learning-lens/machine-learning-lens.html)
- Kubernetes, [Production environment](https://kubernetes.io/docs/setup/production-environment/)
- KServe, [Model serving documentation](https://kserve.github.io/website/docs/intro)
- NIST, [AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)

Architecture is workload-specific. Validate assumptions with exact data, models, runtimes, infrastructure, and failure tests.
