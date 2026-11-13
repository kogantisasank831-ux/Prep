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
title: "AI production monitoring, cost, and capacity interview cheat sheet"
description: "Release lineage, observability, SLOs, drift, delayed labels, LLM/RAG/agent monitoring, telemetry quality, capacity, autoscaling, and FinOps."
summary: "Revise actionable AI monitoring, production-quality evidence, privacy-safe telemetry, capacity from measured goodput, cost controls, alerts, and incidents."
permalink: "/interview-prep/cheat-sheets/ai-production-monitoring-cost-capacity/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 5 · Production operations"
current_label: "Revision guide"
alternate_label: "Cheat sheets hub"
alternate_url: "/cheat-sheets/"
---
> **Batch 5 source:** This page integrates the prepared revision artifact into the Prep site. It is separate from the Week 1–30 learning assessments.

**Target roles:** AI/ML Engineer, AI Platform Engineer, MLOps/LLMOps Engineer, Senior Data Scientist, AI/Data Science Lead  
**Use:** production observability, data/model drift, GenAI/RAG/agent monitoring, SLOs, alerting, capacity, and FinOps  
**Interview rule:** every metric must support a decision. A dashboard without exact release lineage, an owner, a threshold source, and a response is not an operational control.

## 1. Thirty-second revision

- Monitor the complete logical outcome across gateway, data/features, retrieval, model, agent/tools, storage, and external effects.
- Bind telemetry to exact code/image, model/tokenizer, prompt, index, tool/policy, data, configuration, and rollout cohort.
- Separate service health, data health, model/behavior quality, safety/security, business outcome, and cost.
- Track latency distributions and stages: queue, TTFT, TPOT/ITL, retrieval/tool time, and end-to-end—not only averages.
- Production quality needs real or adjudicated outcomes. Drift and model confidence are not correctness.
- Delayed labels require maturation windows, coverage/censoring, and immutable prediction identity.
- For RAG monitor index freshness, retrieval/citation/ACL behavior; for agents monitor trajectory, tools, loops, approvals, effects, and reconciliation.
- Monitor telemetry itself: volume, delay, schema validity, join coverage, and sampling. Missing data is unknown, not healthy.
- Capacity comes from measured goodput under the SLO, peak demand, failure headroom, and scale-up delay.
- Attribute tokens/GPU/provider/retrieval/tool cost to useful outcomes and protect with budgets, quotas, and anomaly alerts.

## 2. Monitoring decision hierarchy

For each signal define:

1. **decision:** observe, investigate, ticket, page, pause, fallback, rollback, or incident;
2. **scope:** population, tenant class, endpoint, release, model, and slice;
3. **statistic:** count/rate/percentile/distribution and aggregation;
4. **window:** evaluation interval and seasonality;
5. **minimum evidence:** sample size, label coverage, uncertainty;
6. **threshold source:** SLO, policy, baseline, experiment, or owner decision;
7. **no-data behavior:** unknown, warning, or page;
8. **owner/runbook:** who responds and how;
9. **recovery condition:** when the alert resolves.

Avoid auto-rollback from a noisy model judge alone.

## 3. Exact deployed lineage

Every telemetry record should be correlatable to the relevant release identity:

- source commit and image digest;
- service/config/feature flags and environment;
- requested and resolved model/provider identity;
- tokenizer/template, adapters, precision, generation defaults;
- prompt/examples/output schema;
- RAG corpus/index/embedding/reranker/config;
- agent graph, tools, policy, memory/checkpoint version;
- data/features and evaluation rubric/judge;
- rollout cohort and operation IDs.

Without lineage, a metric movement cannot be attributed reliably.

## 4. Observability signals

### Metrics

Aggregated numeric trends and SLOs: request rate, p95 latency, error rate, queue depth, token cost.

### Logs

Discrete diagnostic events. Use structured fields, redaction, correlation, retention, and bounded cardinality.

### Traces

End-to-end causality across model, retrieval, tools, and dependencies. Sampling must preserve critical errors, safety decisions, and audit events.

### Profiles

CPU/GPU/kernel/memory performance investigation. They are expensive and typically activated selectively.

OpenTelemetry can standardize traces/metrics/log context, but GenAI semantic conventions evolve; pin the convention version and keep prompt/content capture opt-in and privacy controlled.

## 5. Golden service signals

| Signal | AI examples |
|---|---|
| Traffic | requests/s, input/output tokens/s, jobs, active sessions |
| Errors | 4xx/5xx, model/tool errors, schema failures, OOM, cancellations |
| Latency | queue, TTFT, TPOT, E2E, retrieval/tool stages |
| Saturation | queue/token backlog, active sequences, KV/GPU/CPU/RAM, pool usage |

Also track rejection/rate-limit/fallback/retry rates. A 200 response with an empty or invalid answer is an application failure even if HTTP succeeded.

## 6. SLI, SLO, SLA, and error budget

- **SLI:** measured indicator, such as proportion of valid responses under 2 seconds.
- **SLO:** internal target for an SLI over a window.
- **SLA:** external commitment with consequences.
- **Error budget:** allowed unreliability implied by the SLO.

For an availability SLO $S$ over window duration $T$:

$$
ErrorBudget = (1-S)T
$$

A 99.9% monthly target permits roughly 0.1% of the window, subject to the precise SLI definition. Use burn-rate alerts to detect rapid budget consumption rather than paging on every small fluctuation.

## 7. Latency and goodput monitoring

Segment p50/p95/p99 by:

- endpoint/task;
- model/route/candidate;
- input/output/context length bucket;
- streaming versus non-streaming;
- tenant/priority class;
- cache hit/miss;
- tool/retrieval path;
- region/hardware.

Goodput is the rate completing within the latency and quality contract. If throughput rises while SLO-compliant completions fall, the optimization failed.

## 8. Data and feature monitoring

Monitor:

- source availability, volume, schema, domain/range, missingness, duplicates;
- event-time freshness, processing lag, late data, partition completeness;
- join and label coverage;
- feature distribution, category changes, point-in-time correctness;
- online/offline feature skew;
- replay/backfill and publication status.

Compare with versioned baselines and relevant slices. A healthy endpoint serving stale features is not a healthy ML product.

## 9. Drift

Distinguish:

- **data/covariate drift:** $P(X)$ changes;
- **label/prior drift:** $P(Y)$ changes;
- **concept drift:** $P(Y\mid X)$ changes;
- **prediction/output drift:** model output distribution changes;
- traffic mix, provider, model, prompt, index, or instrumentation change.

Possible detectors include domain constraints, PSI, KS test, chi-square, Wasserstein/Jensen–Shannon distance, embedding/cluster analysis, and learned detectors.

For each detector define baseline, window, sample size, seasonality, multiple-comparison treatment, missing-data behavior, and threshold source. Drift triggers investigation; it does not prove quality degradation or mandate retraining.

## 10. Delayed ground truth

Store the original prediction/decision with immutable lineage and event time. When truth arrives:

- join using stable entity/decision ID;
- enforce a maturation/observation window;
- track label coverage and censoring;
- allow label revisions without overwriting the original prediction;
- backfill metrics by prediction cohort;
- report uncertainty and slice sample size.

Leading proxies such as clicks or thumbs-up should not be mislabeled as confirmed outcome.

## 11. Classical ML behavior monitoring

Depending on task:

- prediction/class/score distribution;
- calibration and threshold operating point;
- precision/recall/F1/AUC with matured labels;
- regression error and residual slices;
- abstention/manual review;
- fairness/subgroup outcomes where lawful and accepted;
- business cost from false positives/negatives;
- explanation/feature-contribution stability only as a diagnostic.

Do not infer performance from average confidence.

## 12. LLM and structured-output monitoring

Track:

- prompt/output token distributions and truncation;
- schema/parse/semantic validation success;
- refusals, abstentions, fallbacks, retries;
- task correctness/completeness on sampled labeled cases;
- hallucination/groundedness where evidence exists;
- tool-call and structured-output validity;
- safety/policy outcomes;
- latency/cost by model and task.

If using an LLM judge, pin judge model/prompt/rubric, protect sensitive content, calibrate against expert/deterministic labels, track disagreement, and retain judge failure as unknown.

## 13. RAG monitoring

### Ingestion/index

- source and partition completeness;
- extraction/OCR failures;
- index freshness/lag and version;
- update/delete/ACL propagation;
- embedding/index errors and size.

### Retrieval

- zero/low-result rate;
- lexical/dense/fusion/reranker scores and source mix;
- metadata/tenant filter behavior;
- retrieval latency and candidate depth;
- recall/utility on sampled labeled queries.

### Generation/citation

- answerability and abstention;
- claim support, citation correctness/coverage/accessibility;
- source authority/effective date;
- contradictory evidence behavior.

Score distribution shifts can result from corpus or traffic changes; investigate before changing thresholds.

## 14. Agent monitoring

Track:

- terminal outcome and business effect;
- steps, loops, repeated actions, and budget exhaustion;
- route/handoff/delegation decisions;
- tool selection, argument validation, authorization denial, latency, error;
- approvals and human corrections;
- checkpoints/resumes/retries;
- partial or unknown side effects and reconciliation;
- tokens/cost by node and task.

“Workflow completed” is not proof that the external ticket/payment/message was correct.

## 15. Safety, security, privacy, and fairness

Monitor policy-relevant outcomes:

- blocked and committed high-risk tool actions;
- unauthorized/cross-tenant attempts and ACL violations;
- direct/indirect prompt-injection indicators;
- sensitive-data detections and exfiltration attempts;
- harmful-content categories/refusals;
- suspicious corpus/tool/memory changes;
- credential/policy override paths;
- subgroup outcomes where accepted and lawful.

Avoid logging the sensitive content you are trying to protect. Use hashes, categories, counts, secure samples, and restricted audit stores as appropriate.

## 16. Telemetry quality

Monitor the monitor:

- expected event volume/heartbeats;
- ingestion delay and loss;
- schema/version validity;
- trace/span completeness;
- prediction-to-label join coverage;
- sampling rate and bias;
- clock skew and duplicate events;
- evaluator availability/failure.

Missing telemetry must become explicit `unknown` or an alert; never an automatic green status.

## 17. Capacity planning

Start from production-like measured **safe goodput per replica**, $G$, and peak arrival rate, $\lambda_{peak}$.

With headroom factor $h>1$:

$$
Replicas = \left\lceil \frac{\lambda_{peak}}{G} \times h \right\rceil
$$

Then check:

- N+1 or failure-zone capacity;
- burst/queue tolerance;
- scale-up delay and minimum warm replicas;
- token/context mix and KV memory;
- tenant fairness;
- downstream/provider limits;
- maintenance/deployment capacity;
- cluster and regional quotas.

```python
from __future__ import annotations

from math import ceil


def required_replicas(
    peak_requests_per_second: float,
    safe_goodput_per_replica: float,
    *,
    headroom: float = 1.25,
    failed_replicas: int = 1,
) -> int:
    if peak_requests_per_second <= 0 or safe_goodput_per_replica <= 0:
        raise ValueError("rates must be positive")
    if headroom < 1 or failed_replicas < 0:
        raise ValueError("invalid resilience settings")
    traffic_replicas = ceil(
        peak_requests_per_second / safe_goodput_per_replica * headroom
    )
    return traffic_replicas + failed_replicas
```

Goodput must come from the same model, runtime, hardware, request distribution, and SLO.

## 18. Autoscaling

Potential signals:

- requests/tokens waiting and queue age;
- active/ongoing requests per replica;
- TTFT/queue SLO burn;
- token arrival rate;
- KV-cache utilization/preemption;
- GPU utilization/memory as supporting signals;
- scheduled or forecast demand.

Configure minimum/maximum replicas, target utilization/concurrency, scale-up/down rate, stabilization/cooldown, readiness, and cluster capacity.

Scaling from zero may require GPU provisioning, image/model download, compilation, and warm-up. Use it only when cold-start latency is acceptable or an external queue protects requests.

## 19. Cost model

Total cost can include:

- training/fine-tuning GPU/CPU/storage/network;
- inference GPU or provider input/output/cache tokens;
- idle/warm capacity;
- retrieval/embedding/reranking/vector/search;
- agent tool/API calls;
- databases, queues, egress, telemetry, evaluation;
- human review and operations.

For a dedicated self-hosted replica costing $C_h$ per hour, with benchmark capacity $G$ requests/s at full use and average effective utilization $u$:

$$
CostPerRequest \approx \frac{C_h}{3600 \times G \times u}
$$

Use measured utilization and include shared infrastructure/operations for a real TCO. Provider cost is typically calculated from exact input/output/cached-token and tool usage prices, which can change.

Useful units:

- cost per request and per successful task;
- cost per 1K/1M tokens;
- cost per tenant/workflow/node;
- GPU-hours per accepted output;
- idle-cost ratio and fallback cost;
- cost versus quality/latency frontier.

## 20. Cost controls

- per-user/tenant/task budgets and quotas;
- prompt/context trimming and output limits;
- smaller model for accepted task tiers;
- caching with correctness/privacy controls;
- batching, quantization, optimized engines;
- request routing by quality/risk;
- cancellation and duplicate suppression;
- bounded agent/tool loops;
- scale-down with cold-start trade-off;
- anomaly alerts and spending kill switches.

Cost optimization must not silently reduce required quality, safety, or availability.

## 21. Alert design

Page when immediate human action is required; ticket when work can wait; dashboard when no direct action is expected.

Good alert content:

- affected user/task/slice and exact candidate;
- current versus expected value and window;
- sample/coverage and telemetry health;
- likely dependencies/recent changes;
- business/risk impact;
- runbook and owner;
- rollback/fallback/kill-switch status.

Use multi-window burn rates, persistence, deduplication, and inhibition to reduce noise. Test alert delivery and runbooks with safe synthetic failures.

## 22. Incident and rollback loop

1. detect and verify telemetry integrity;
2. assess user/business/safety impact;
3. contain: pause traffic/tool, fallback, quarantine, revoke, or roll back;
4. preserve evidence and exact versions;
5. reconcile partial side effects/data;
6. communicate and recover;
7. identify contributing causes;
8. add tests/monitors/runbook and verify prevention.

Do not destroy evidence or feed incident data into training before review.

## 23. Common interview traps

- Equating uptime with AI product health.
- Monitoring only aggregate averages.
- Treating drift as confirmed performance loss.
- Treating model confidence or judge score as ground truth.
- Ignoring label delay/coverage and telemetry loss.
- Capturing raw prompts/secrets for every trace.
- Autoscaling only on GPU utilization.
- Calculating capacity from theoretical FLOPS instead of goodput.
- Reporting cost per request without successful outcome or idle capacity.
- Creating alerts with no owner/runbook/action.

## 24. Rapid interview questions

**Q1. What must every prediction/trace include?**  
Enough immutable lineage and correlation to identify the exact release, input cohort, execution path, and eventual outcome without exposing secrets.

**Q2. Drift versus concept drift?**  
Input distribution drift changes $P(X)$; concept drift changes the relationship $P(Y\mid X)$ and requires outcome evidence.

**Q3. Why monitor telemetry?**  
Missing or delayed events can make every product metric falsely look healthy or unmeasurable.

**Q4. How do you monitor delayed labels?**  
Join truth to immutable predictions after a maturation window and report coverage, censoring, revisions, slices, and uncertainty.

**Q5. Best LLM autoscaling signal?**  
No universal single signal; combine queue/token backlog, TTFT, active sequences/KV pressure, measured capacity, and supporting resource metrics.

**Q6. Cost per request or successful task?**  
Both, but successful business outcome prevents a cheap failing model from looking efficient.

**Q7. Why not store all traces?**  
Privacy, security, retention, cost, and high-cardinality risks; sample safely while preserving critical audit/error events.

**Q8. What proves an alert works?**  
An injected known event traverses the deployed telemetry pipeline, fires the correct route, and responders can execute the runbook and verify recovery.

## 25. Lead-level design case

**Prompt:** Define monitoring and capacity for a multi-model RAG/agent platform with self-hosted GPUs and managed-provider fallback.

A strong answer should:

1. define business/task, quality/safety, service, and cost SLOs per risk/tenant class;
2. bind telemetry to model/prompt/index/graph/tool/policy/config/cohort identity;
3. trace gateway → retrieval → model → tools → side effect with privacy-safe correlation;
4. monitor queue, TTFT/TPOT/E2E, goodput, KV/GPU, retrieval/citations, trajectory/effects, safety, and outcome;
5. include telemetry health and delayed-label coverage;
6. benchmark safe goodput by request-length class and size N+1 peak capacity;
7. autoscale on backlog/SLO/capacity with warm floors and cluster limits;
8. attribute GPU/provider/tool/evaluation cost to successful tasks and tenants;
9. define fallback compatibility, budget controls, alerts, runbooks, and kill switches;
10. verify with shadow/canary, load/spike/soak, dependency failure, telemetry outage, and rollback drills.

## 26. Final checklist

- [ ] I separate service, data, model, GenAI, safety, business, cost, and telemetry health.
- [ ] I correlate outcomes to exact release lineage.
- [ ] I can explain SLI/SLO/SLA/error budget and actionable alerting.
- [ ] I understand drift limits and delayed-label monitoring.
- [ ] I can specify LLM, RAG, and agent-specific production signals.
- [ ] I plan privacy-safe telemetry and judge calibration.
- [ ] I size capacity from measured goodput, peaks, failures, and scale delay.
- [ ] I can calculate and control cost per request and successful outcome.

## 27. Primary references

- NIST, [AI RMF Measure playbook](https://airc.nist.gov/airmf-resources/playbook/measure/)
- NIST, [Challenges to monitoring deployed AI systems](https://www.nist.gov/publications/challenges-monitoring-deployed-ai-systems-center-ai-standards-and-innovation)
- OpenTelemetry, [Semantic conventions](https://opentelemetry.io/docs/specs/semconv/)
- Prometheus, [Monitoring practices](https://prometheus.io/docs/practices/)
- Google, [Site Reliability Engineering workbook](https://sre.google/workbook/table-of-contents/)
- MLflow, [LLM and agent evaluation/monitoring](https://mlflow.org/docs/latest/genai/eval-monitor/)
- vLLM, [Production metrics](https://docs.vllm.ai/en/latest/design/metrics.html)
- Ray, [Serve observability](https://docs.ray.io/en/latest/serve/monitoring.html)
- KServe, [Generative inference autoscaling](https://kserve.github.io/website/docs/model-serving/generative-inference/autoscaling)

Thresholds and capacity are workload- and risk-specific. Replace assumptions with measured evidence and revalidate after material changes.
