# Week 21 cost and latency optimisation contracts

Source: `Path.md`, Week 21. The lab compares two synthetic strategies over the
same deterministic workload. It does not contact a model provider and its
microunits, latency and quality values are fixtures—not prices or benchmarks.

| ID | Effective rule and acceptance |
| --- | --- |
| W21-BR1 | Compare `all-large` and `routed` over an identical materialized workload. Report quality, end-to-end latency and cost together. |
| W21-FR1 | Route simple routing/extraction work to the small profile and complex recommendations to the large profile; escalate when the estimated quality floor would be missed. |
| W21-FR2 | Prune only declared optional context. Never remove required context merely to fit the configured limit. |
| W21-FR3 | Reject a request whose estimated cost exceeds its explicit budget; do not silently choose an unapproved model or truncate required output. |
| W21-FR4 | Separate TTFT from end-to-end latency and compute parallel groups by the critical path, not by adding independent call durations. |
| W21-FR5 | Scope response-cache entries by tenant, model, prompt version and exact cache key. Cache only safe read-like routing/extraction results in this lab. |
| W21-DR1 | Use integer tokens, basis points, milliseconds and synthetic microunits so calculations are deterministic and no floating-point price claim is implied. |
| W21-SR1 | Never share cache entries across tenants or prompt/model versions. Never cache recommendation decisions by default. |
| W21-NFR1 | Identical workload and policy produce identical reports without network, model, clock, random source or secret. |
| W21-ER1 | Test strict schemas, routing and escalation, optional pruning, budget rejection, TTFT/E2E math, critical-path parallelism, cache scope, determinism and CLI paths. |

## Accepted limitations

- Quality values are declared scenario fixtures, not measured model accuracy.
- Latency excludes queues, networks, provider scheduling and tokenisation variance.
- Cost uses synthetic microunits and must not be presented as vendor pricing.
- Exact response caching does not demonstrate semantic-cache correctness.
- Parallel groups assume independence; real tools require dependency and capacity checks.
- Streaming changes perceived latency, not the time or cost required to finish generation.
