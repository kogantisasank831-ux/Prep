---
layout: "week"
status: "approved"
version: "1.0.0"
last_reviewed: "2026-11-11"
imported_on: "2026-11-13"
source_repository: "kogantisasank831-ux/transformer-explainer"
source_commit: "cdd45b6b0c08c5d88a626e4d16853abdf285f08d"
source_path: "AI_Data_Science_Interview_Cheat_Sheets/Batch_10_AI_Engineering_Platform/40_End_to_End_AI_Architecture_Mock_Interview_Cheat_Sheet.md"
header_context: "Interview cheat sheets"
back_label: "Cheat sheets"
back_url: "/cheat-sheets/"
toc_heading: "Cheat-sheet sections"
pagination_label: "Cheat sheets hub"
pagination_url: "/cheat-sheets/"
title: "End-to-end AI architecture and mock interview cheat sheet"
description: "Interview revision for requirement framing, capacity math, architecture contracts, lifecycle, security, operations, leadership, and timed mock cases."
summary: "Practise a timed AI system-design method covering requirements, metrics, capacity, architecture, lifecycle, failures, security, operations, and leadership delivery."
permalink: "/interview-prep/cheat-sheets/end-to-end-ai-architecture-mock-interview/"
kicker_primary: "Interview revision"
kicker_secondary: "Batch 10 · Architecture"
current_label: "Revision guide"
alternate_label: "Cheat sheets hub"
alternate_url: "/cheat-sheets/"
---

**Target roles:** AI Engineer, Agentic AI Engineer, ML Engineer, Applied Scientist, Senior/Lead Data Scientist, Data Science Technical Lead<br>
**Use:** 45–60 minute system-design rounds, architecture reviews, project defense, ambiguous product cases, and final interview revision<br>
**Interview rule:** convert ambiguity into explicit requirements and numbers, present one coherent baseline, then deepen the highest-risk decisions. A catalog of cloud services is not a design.

## 1. Thirty-second revision

- Start with the user decision and business outcome—not a model or framework.
- Clarify functional scope, exclusions, scale, latency/availability, data sensitivity, quality/safety, cost, and delivery timeline.
- Define the unit of work and estimate requests, tokens, data volume, concurrency, storage, and accelerator capacity.
- Establish a simple baseline and a measurable evaluation plan before advanced RAG, fine-tuning, or agents.
- Separate offline/training or ingestion paths from online serving; separate control plane from data plane.
- Make data/model/prompt/index/tool identity and lineage explicit.
- Design contracts: API/events, schemas, idempotency, ordering, timeouts, retries, auth, tenant scope, and state ownership.
- Put deterministic controls around probabilistic components. The model proposes; policy authorizes high-risk actions.
- Evaluate offline and by slice, then shadow/canary with stop conditions. Monitor service, data, model/GenAI, safety, business, and cost.
- Name failure modes, blast radius, fallback, recovery, human escalation, and rollback.
- Discuss trade-offs with evidence: build/buy, managed/self-hosted, sync/async, batch/online, simple workflow/agent, RAG/fine-tune.
- A lead answer covers ownership, phased delivery, risk register, decision records, team boundaries, and stakeholder communication.

## 2. A reusable 60-minute answer structure

| Time | Focus | Output |
|---:|---|---|
| 0–5 min | clarify user, decision, scope, constraints | accepted requirements and assumptions |
| 5–10 min | success, quality, safety, SLO and scale | metric tree and rough numbers |
| 10–18 min | baseline and data/evaluation | smallest valid solution and evidence plan |
| 18–32 min | high-level architecture and flow | components, contracts, state and identity |
| 32–42 min | deepest risks/trade-offs | two or three defended choices |
| 42–50 min | failure, security, operations | fallback, monitoring, rollout, rollback |
| 50–57 min | capacity, cost and evolution | bottleneck math and phased roadmap |
| 57–60 min | summarize and invite depth | concise decision narrative |

Adapt to interviewer signals. Do not spend half the interview drawing before confirming the problem.

## 3. Requirements checklist

### Functional

- Who is the user and what action/decision follows the output?
- What inputs, outputs, evidence, edits, approvals, and integrations exist?
- Is the workload prediction, generation, retrieval, ranking, optimization, workflow, or autonomous action?
- Is state session, user, tenant, document, job, or global?
- What is explicitly out of scope?

### Nonfunctional

- load distribution, bursts, concurrency and growth;
- p50/p95/p99, time to first token, deadline and availability;
- batch freshness or online consistency;
- response/output quality and abstention;
- data classification, privacy, retention, residency and deletion;
- tenant isolation, authorization, audit and human oversight;
- cost per request/task/valid outcome and total budget;
- RTO/RPO, regional/failure-domain needs and operational staffing;
- delivery deadline, team skills, vendor constraints and portability.

### Assumption discipline

State assumptions numerically and mark what would change the architecture:

> I will assume 50 requests/s at peak, 4× bursts, 2,000 input and 300 output tokens at p95, a 3-second TTFT target, internal confidential documents, and no autonomous external action. I would validate these with traffic and risk owners.

An interviewer can correct one number; that is progress, not failure.

## 4. Metric tree

Connect levels:

`business outcome → user task success → AI/model behavior → service behavior → resource/cost`

Example for an internal support assistant:

- outcome: resolved cases per agent-hour without increased complaints;
- task: correct useful answer or appropriate escalation;
- AI: grounded accuracy, citation correctness, abstention, unsafe disclosure;
- retrieval: Recall@K, ACL correctness, index freshness;
- service: availability, TTFT, completion p95, error;
- resource: tokens, GPU time, retrieval calls, cost per valid answer.

Define guardrails such as security incidents, critical-hallucination rate, cross-tenant exposure, human override, or customer complaint. A model metric must not be presented as proven business impact without a causal measurement plan.

## 5. Scale and capacity math

Estimate with ranges:

- requests/day and peak requests/s;
- concurrent work using Little's Law: `in-flight ≈ arrival rate × time in system`;
- input/output tokens per request and tokens/s;
- documents/day, pages/bytes, chunks and index growth;
- embedding and re-index throughput;
- model weight/KV/activation memory;
- storage replication, retention and trace volume;
- calls and cost per successful workflow.

### Latency budget

For serial stages, add latency. For truly parallel branches on the critical path, take the slowest branch plus orchestration overhead.

```python
from collections.abc import Mapping, Sequence


def critical_path_latency_ms(
    serial_stages: Sequence[float],
    parallel_groups: Sequence[Mapping[str, float]],
    *,
    orchestration_overhead_ms: float = 0.0,
) -> float:
    if any(value < 0 for value in serial_stages):
        raise ValueError("serial latency cannot be negative")
    if orchestration_overhead_ms < 0:
        raise ValueError("overhead cannot be negative")

    parallel_latency = 0.0
    for group in parallel_groups:
        if not group or any(value < 0 for value in group.values()):
            raise ValueError("parallel groups must be nonempty and nonnegative")
        parallel_latency += max(group.values())

    return sum(serial_stages) + parallel_latency + orchestration_overhead_ms


budget = critical_path_latency_ms(
    serial_stages=[40, 70, 900],
    parallel_groups=[{"vector": 120, "keyword": 80}],
    orchestration_overhead_ms=30,
)
assert budget == 1160
```

The branches must actually run concurrently and be independent. Use p95 stage distributions carefully: adding p95 values is conservative but not the true end-to-end p95. Validate with trace and load data.

### Capacity questions

- What is one replica's sustainable throughput under the target tail latency?
- What resource saturates first?
- How many warm replicas cover peak plus a failure?
- How long does Pod/node/model cold start take?
- Can a queue absorb the burst before the deadline?
- What happens when quota or GPU capacity is unavailable?

## 6. Baseline and solution selection

Use the smallest intervention that can meet the need:

| Need | Start with | Escalate when evidence shows |
|---|---|---|
| deterministic policy | rules/SQL/workflow | complexity or learned generalization is valuable |
| tabular prediction | heuristic and linear/tree model | validated nonlinear/representation gain |
| known-document Q&A | search plus extractive/cited response | generation adds measured value |
| domain knowledge freshness | RAG | retrieval cannot encode required behavior |
| behavior/style/task format | prompting then SFT/PEFT | examples and evaluation justify training |
| multi-step process | deterministic workflow | bounded model-directed routing is necessary |
| hosted versus self-hosted model | API baseline | privacy, control, scale, latency or economics justify platform |

### RAG versus fine-tuning

- RAG supplies changeable external knowledge and evidence; it depends on ingestion, retrieval, ACL, and freshness.
- Fine-tuning changes behavior/representation; it does not reliably create a current, citeable database.
- Prompting may solve format/instruction needs first.
- They can coexist, but each adds distinct data, evaluation, release, and rollback work.

### Workflow versus agent

Prefer a deterministic graph when steps and transitions are known. Add bounded model decisions for classification, routing, planning, or tool choice only where flexibility has measured value. Define allowed tools, state, budgets, approval, termination, and fallback. Multi-agent systems need an actual decomposition/ownership benefit—not role-play names.

## 7. High-level architecture vocabulary

### Planes

- **Experience/edge:** UI, API gateway, auth, rate/quota, streaming.
- **Application/orchestration:** workflow, policy, session/job state, tool routing.
- **Intelligence:** model gateway/serving, embeddings, reranker, classical models, optimizer.
- **Data:** source systems, object store, warehouse/lake, feature/vector/search/graph stores.
- **Offline:** ingestion, labeling, training/fine-tuning, indexing, evaluation.
- **Control:** registry, configuration, secrets, deployment, policy, lineage.
- **Operations:** logs/metrics/traces, SLO, incident, audit, cost and feedback.

Do not include every plane if the case does not need it. Name the source of truth and derived stores.

### Control versus data plane

The data plane executes user inference/workflows. The control plane manages model/prompt/index/config registration, evaluation, promotion, routing and policy. Restrict control-plane permissions; a config change can be as consequential as a code deployment.

### Online versus offline

Offline pipelines collect/validate data, train or index, evaluate, and publish immutable artifacts. Online paths validate/authorize requests, fetch features/context, infer, apply policy, return or queue results, and emit telemetry/feedback. Define the freshness bridge and rollback.

## 8. Contracts, state, and consistency

For each arrow on the design, state:

- request/event schema and version;
- producer, consumer and owner;
- authentication/authorization/tenant key;
- timeout/deadline and retry classification;
- idempotency/operation ID;
- ordering and consistency;
- payload/token/size limits;
- telemetry and error behavior.

Choose state deliberately:

- database for durable transaction/source of truth;
- object store for large immutable artifacts;
- broker/log for asynchronous delivery/stream;
- cache for recomputable acceleration;
- vector/search index as derived retrieval state;
- checkpoint store for resumable workflows;
- trace store for diagnostics/evaluation with controlled retention.

Avoid distributed transactions across model/tools. Use short local transactions, outbox/events, idempotent consumers and compensating business actions.

## 9. Data and ML lifecycle

### Data contract

Define entity/grain, timestamp/cutoff, label availability, source, ownership, schema, quality rules, privacy, retention and point-in-time semantics. Prevent train-serving skew and future leakage.

### Model lifecycle

1. problem and baseline;
2. collection/labeling and data validation;
3. reproducible training/tuning;
4. offline/slice/safety/robustness evaluation;
5. immutable registry candidate;
6. integration/performance/security gates;
7. shadow/canary and approval;
8. monitoring, feedback and delayed outcomes;
9. retraining/change trigger, rollback and retirement.

For GenAI, extend identity to prompt, model/provider, decoding, retrieval corpus/chunker/embedding/index, tool schemas, workflow graph, guardrails and evaluator.

## 10. Reliability and failure review

Walk the critical path and ask “What if this is slow, wrong, unavailable, duplicated, stale, compromised, or overloaded?”

| Failure | Control ideas |
|---|---|
| model API unavailable | deadline, bounded retry, circuit breaker, approved fallback/manual path |
| vector index stale | freshness SLO, versioned index, source citation/date, rebuild/rollback |
| broker duplicates | stable operation ID, idempotent effect, outbox/inbox |
| GPU overload | admission, bounded queue, batching, priority, autoscale and shed |
| bad model/prompt/index | exact identity, canary, guardrail, rapid rollback |
| worker crash mid-tool | checkpoint, lease, tool idempotency, reconciliation |
| observability fails | telemetry health signal and independent synthetic checks |
| regional failure | traffic failover plus replicated/restorable state based on RTO/RPO |

Define degradation in product terms. “Use another model” is incomplete unless quality, security, contract, cost, and capacity are approved.

## 11. Security, privacy, and governance review

Cover four planes:

- **Application:** auth, tenant/resource authorization, session, rate and input validation.
- **AI/data:** training/RAG poisoning, leakage, prompt injection, unsafe output and artifact provenance.
- **Action:** tool permissions, destination/argument validation, approval, idempotency and audit.
- **Platform/supply chain:** workload identity, network/egress, secrets, images/dependencies/models and deployment permissions.

Use data minimization, purpose/retention/deletion, encryption, access logging, and privacy-safe evaluation. Map risk to the intended use and applicable organizational/legal owners; do not claim compliance from architecture alone.

## 12. Observability and operation

### Signal layers

- **service:** rate, errors, duration, saturation, availability;
- **data:** schema, missingness, freshness, volume, drift, lineage;
- **model:** performance/calibration/slices and delayed labels;
- **RAG/agent:** retrieval/citation, tool errors, loops, budget, approvals;
- **safety/security:** policy events, injection/denial, cross-tenant attempts;
- **business:** task success, override/escalation, downstream outcome;
- **cost:** tokens, calls, accelerator, storage, egress, cost per valid task;
- **telemetry:** dropped spans, missing labels, pipeline lag.

An alert needs an owner, threshold tied to user impact, diagnostic context, runbook, and escalation. Dashboards without action are not an operating model.

## 13. Delivery and team plan

A lead can phase:

1. **Discovery:** validate workflow, risk, data rights/quality, baseline and metric.
2. **Thin slice:** one user journey, simple model/search, manual approval and observable trace.
3. **Pilot:** representative users/data, evaluation set, security and operations.
4. **Production:** SLO, capacity, progressive rollout, support, rollback and governance.
5. **Scale/evolve:** optimize bottlenecks only from observed evidence.

Define ownership across product/domain, data, modeling, backend, platform, security/privacy, QA/evaluation and operations. Maintain decision records for consequential choices and a risk register with owner/mitigation/trigger.

Build versus buy should compare time-to-evidence, quality/control, data/privacy, reliability/support, integration, portability, unit economics at expected scale, exit cost and team capability—not license price alone.

## 14. Mock case 1: enterprise document assistant

**Prompt:** Design an assistant over internal policies and contracts with citations.

Clarify tenants, ACL source, document types/languages, freshness, answerability, sensitive data, latency, volume and required abstention.

Baseline and flow:

1. authorized source connector writes immutable document versions;
2. parse/OCR, classify, chunk and attach source/ACL/version metadata;
3. embed and index dense plus sparse representations;
4. query auth and tenant filters apply before retrieval;
5. retrieve, hybrid fuse/rerank and build bounded context;
6. generate cited answer or abstain;
7. verify citation/source visibility; log safe trace and feedback.

Evaluation: ingestion coverage, ACL negative tests, Recall@K, citation entailment, grounded answer accuracy, unanswerable abstention, stale-document rate, latency and cost by document/query slice.

Risks: indirect prompt injection, stale ACL/index, OCR/table loss, cross-tenant cache, overlong context, citation decoration, deletion propagation. Roll out read-only to a limited group with source links and easy escalation.

## 15. Mock case 2: procurement workflow agent

**Prompt:** Read a tender, compare policy and vendor data, draft a recommendation, and submit only after approval.

Use a deterministic state graph:

`received → validated → extracted → evidence_retrieved → drafted → reviewed → approved → submitted → reconciled`

The LLM may extract/draft/route within bounds. Deterministic policy validates schema, authorization, spend/vendor constraints and approval. Submission tool requires a short-lived scoped capability and idempotency key.

Persist checkpoint and audit evidence; use outbox/job queue for long stages. Test crash immediately before/after submission. Reconcile external status rather than assuming a timeout means failure.

Metrics: field extraction, policy evidence/citation, recommendation acceptance/edit, approval turnaround, duplicate/forbidden action, valid completion, latency and cost. High-value/novel cases remain human-led.

## 16. Mock case 3: high-throughput email classifier

**Prompt:** Classify 10 million messages/day into 50 intents with a 100 ms p95 online tier and a lower-cost batch tier.

Clarify languages, multi-label versus single, imbalance, evolving intents, privacy, delayed labels and action cost.

Start with rules and a compact supervised baseline. Separate online and batch:

- online gateway validates, fetches approved features, calls a warm CPU/GPU model, calibrates confidence, and abstains/escalates;
- batch reads immutable partitions, processes idempotently, writes versioned results, and supports backfill;
- training uses temporal/entity-safe splits, label-quality audit and per-intent calibration.

Capacity: 10 million/day averages about 116/s, but design for measured peak/burst and p95; benchmark batch size and CPU versus GPU. Cache only exact safe duplicates if useful.

Evaluate macro/per-class precision/recall, calibration and action-weighted cost; monitor new/unknown intents, class mix, language, latency and human corrections. Canary by traffic shard and preserve the previous model/threshold.

## 17. Mock case 4: local-model configuration recommender

**Prompt:** Recommend an open model and serving configuration from task, traffic, latency, quality, hardware, and budget.

Treat this as a constrained decision-support system, not an LLM guess.

1. Normalize workload: model task, context/output distribution, concurrency, quality floor, accelerator/VRAM, software version and budget.
2. Maintain a versioned catalog of model license, architecture, precision, weight estimate, context and runtime compatibility.
3. Use explicit memory/capacity formulas to filter infeasible candidates.
4. Retrieve real benchmark evidence matching hardware/runtime/config; do not compare incomparable tests.
5. Rank by approved multi-objective policy and expose assumptions, uncertainty and rejected reasons.
6. Generate recommended engine parameters only within supported version ranges.
7. Run a small validation benchmark before production; record observed versus predicted.

Metrics: feasible recommendation rate, top-K quality/latency/cost regret versus benchmark, memory-estimate error, unsafe/incompatible recommendation, explanation correctness and catalog freshness. Separate facts from estimates and user overrides.

## 18. Common weak answers and repairs

| Weak answer | Why weak | Repair |
|---|---|---|
| “Use microservices/Kubernetes” | no requirement or scale link | start with modular service; split at independent scale/ownership/failure boundaries |
| “Use a vector database” | retrieval contract absent | define corpus, ACL, freshness, hybrid/rerank, Recall@K and deletion |
| “Use an agent” | uncontrolled flexibility | show deterministic workflow, bounded decisions, tools, state, budget and approval |
| “Autoscale GPUs” | metric/cold start/supply ignored | benchmark, warm minimum, queue/token metric, node delay and admission |
| “Accuracy is 95%” | no dataset, baseline, slice or cost | give provenance, confusion/slices, uncertainty, threshold and business action |
| “Exactly once” | end-to-end effect unexplained | idempotency, transaction/outbox, acknowledgement and reconciliation |
| “Encrypt data” | no identity/access/retention | include authorization, keys, audit, minimization, deletion and threat model |
| “Monitor drift” | no action | metric, threshold, owner, diagnosis, retrain/rollback and label delay |

## 19. Interviewer follow-ups to practise

Be ready for:

- Which assumption is most dangerous?
- What would you remove for a four-week MVP?
- What becomes the first bottleneck at 10× load?
- Why this model/database/framework rather than the simplest alternative?
- How do you prove business value rather than correlation?
- How do you avoid leakage and evaluation contamination?
- What happens on duplicate, timeout, partial failure, or concurrent update?
- How do you isolate tenants and prevent prompt/tool abuse?
- What is immutable in a release and how do you roll back?
- Which metric would page someone at 2 a.m. and what would they do?
- What changes if data cannot leave the customer's environment?
- What would make you stop or not launch the project?

## 20. Rapid interview questions

**1. What should you draw first?**<br>
Usually the user/client and critical request or job flow after requirements, then add source of truth, asynchronous/offline path, and control/operations only as needed.

**2. How much capacity headroom?**<br>
There is no universal percentage. Derive it from forecast uncertainty, failure tolerance, scaling delay, traffic burst, quota/supply and SLO, then load-test it.

**3. When choose asynchronous processing?**<br>
When duration is long/variable, work must survive client disconnect, burst buffering or independent retry/scale is needed, or a human step exists.

**4. When use a feature store?**<br>
When multiple models need governed reusable features and point-in-time/offline-online consistency. A small system may need only a well-versioned pipeline.

**5. What is the source of truth for RAG?**<br>
The authorized source document/system. Chunks, embeddings and indexes are derived artifacts that require lineage, version, freshness and deletion propagation.

**6. How do you defend a technology choice?**<br>
Tie it to an accepted requirement, compare feasible alternatives on measured criteria, state operational cost/risk, and name the evidence or experiment.

**7. What makes an architecture production-ready?**<br>
Not a diagram alone: contracts, identity/lineage, tests/evaluation, security, capacity, observability, ownership, rollout, rollback and recovery evidence.

**8. What is a good final summary?**<br>
Restate user outcome, baseline architecture, two decisive trade-offs, main risk/control, rollout metric and the next assumption to validate.

## 21. Final architecture and interview checklist

### Problem and evidence

- [ ] User, decision, outcome, scope/exclusions and assumptions are explicit.
- [ ] Quality, safety, business, SLO and cost metrics form a coherent tree.
- [ ] Workload and capacity use numeric distributions, not only averages.
- [ ] Baseline and evaluation dataset/slices/uncertainty are defined.

### Design

- [ ] Critical online/job flow, offline path, source of truth and derived state are clear.
- [ ] API/events define schema, auth, tenant, idempotency, timeout, retry and errors.
- [ ] Data cutoff/lineage, model/prompt/index/tool/release identity are traceable.
- [ ] RAG, fine-tune, agent, platform and vendor choices follow evidence.

### Risk and operation

- [ ] Failure modes, overload, fallback, checkpoints, recovery, RTO/RPO and rollback are explicit.
- [ ] Security/privacy cover application, AI/data, actions and platform/supply chain.
- [ ] Tests include deterministic, evaluation/slices, security, load and resilience.
- [ ] Monitoring covers service, data, AI, safety, business, cost and telemetry health.

### Leadership

- [ ] MVP/pilot/production phases and stop conditions are stated.
- [ ] Ownership, review/approval, runbook and incident path are clear.
- [ ] Build/buy and cost discuss total lifecycle and exit risk.
- [ ] Final summary connects technology to user value, risk and next validation.

## Primary references

- [Google SRE Book — Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)
- [Google SRE Workbook — Non-Abstract Large System Design](https://sre.google/workbook/non-abstract-design/)
- [AWS Well-Architected — Machine Learning Lens](https://docs.aws.amazon.com/wellarchitected/latest/machine-learning-lens/machine-learning-lens.html)
- [AWS Well-Architected — Generative AI Lens](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/generative-ai-lens.html)
- [Azure Well-Architected Framework — AI workload architecture pattern](https://learn.microsoft.com/azure/well-architected/ai/architecture-pattern)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [OpenAPI Specification](https://spec.openapis.org/oas/)
- [Kubernetes documentation](https://kubernetes.io/docs/home/)
- [OWASP GenAI Security Project](https://genai.owasp.org/)

**Evidence boundary:** this framework organizes an interview answer; it does not prove the design. Production fitness requires accepted requirements, exact-candidate implementation, representative evaluation and load tests, security/privacy review, progressive rollout, operational ownership, and observed outcomes.
