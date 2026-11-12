---
layout: week
week: 21
phase: 5
status: review
version: 1.0.0
last_reviewed: 2026-11-11
estimated_hours: 8
permalink: /weeks/week-21/
title: "Optimise the whole inference path without trading away quality"
description: Measure routing, token budgets, optional-context pruning, exact caching, parallel work, streaming latency and synthetic cost under one explicit quality gate.
summary: Cost and latency improvements are safe only when identical work, quality evidence and failure behavior remain visible.
kicker_primary: Cost and latency optimisation
kicker_secondary: Routing, tokens, caching, concurrency and evidence
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-21/beginner/
---

## Before you start

This route assumes you can read service metrics, reason about model calls and
write basic Python tests. Start with the [beginner route]({{ '/weeks/week-21/beginner/' | relative_url }})
if tokens, time-to-first-token or cache scope are unfamiliar.

The goal is not “use the smallest model.” It is to compare the same workload
under two explicit strategies while retaining a quality floor, request budget
and visible rejection state. All prices, speeds and quality values in the lab
are synthetic fixtures—not vendor prices or benchmarks.

The [Week 21 assessment]({{ '/assessments/week-21/' | relative_url }}) draws ten
balanced questions from a 100-item practice bank.

| Hour | Focus | Evidence to retain |
| --- | --- | --- |
| 1 | Define workload and baselines | task mix, token sizes and all-large report |
| 2 | Add model routing | route reason, escalation and quality delta |
| 3 | Budget context | required versus optional tokens |
| 4 | Measure latency | TTFT, completion and critical path |
| 5 | Scope caching | tenant, model, prompt and data version |
| 6 | Batch and parallelise | dependency graph and backpressure limits |
| 7 | Stream honestly | TTFT gain without hiding total duration |
| 8 | Validate the strategy | cost, latency, quality and rejection tests |

## Start with a workload, not a trick

Optimisation has no meaning without a fixed workload and acceptance criteria.
Capture at least:

- task class, such as routing, extraction or recommendation;
- input, output and optional-context tokens;
- concurrency and arrival shape;
- time-to-first-token (TTFT) and end-to-end latency;
- quality metric and acceptable floor;
- estimated cost under a declared unit; and
- error, rejection and fallback rates.

The lab compares `all-large` with `routed` over the same materialised tuple of
four requests. Materialising the input matters: consuming a generator for the
first strategy would give the second strategy an empty workload and fabricate a
large saving.

## Route by task and evidence

A router should map observable request features to a model class. Keep the rule
small enough to inspect:

1. simple routing and extraction begin on the small model;
2. complex recommendations begin on the large model;
3. an estimated result below the quality floor escalates once; and
4. work above the per-request cost budget is rejected explicitly.

In production, replace the lab's synthetic quality function with an evaluation
set segmented by task, language, risk and difficulty. Measure routing mistakes:
a false downgrade harms quality, while an unnecessary escalation harms latency
and cost. Shadow routing can compare decisions before traffic is switched.

Do not allow a model to assign itself a higher budget. Budget and routing policy
belong to trusted application code.

## Count the tokens that decisions actually use

Input tokens often mix four different things:

| Context class | Example | Treatment |
| --- | --- | --- |
| required instruction | output schema and safety rule | preserve |
| required evidence | retrieved clause used by the answer | preserve |
| optional evidence | redundant low-ranked passage | candidate for pruning |
| history | earlier turns or tool traces | summarise or trim by policy |

The lab prunes only `optional_context_tokens`, never the declared required
boundary. If input exceeds the context target and optional context is too small,
the remaining request may still exceed the target. That is honest: silently
cutting required evidence would turn a cost optimisation into a quality bug.

Prompt compression is useful only when evaluated on the downstream task. Track
compression ratio alongside answer/citation quality, instruction retention and
adversarial behavior. A shorter prompt is not automatically a better prompt.

## Separate TTFT from completion latency

Streaming improves perceived responsiveness because the first token arrives
before generation finishes. It does not make the generation free or guarantee a
better end-to-end result.

The lab uses two transparent estimates:

~~~text
TTFT = base latency + input tokens / prefill throughput
completion = TTFT + output tokens / decode throughput
~~~

Real measurements need percentiles, warm/cold state, queue time, batch size,
model version and hardware. Compare p50 and tail latency; an optimisation that
improves the median while making p99 unstable may be a regression.

## Parallelise only independent work

If two calls have no data or side-effect dependency, their latency contribution
is the maximum of their durations, not their sum. The lab labels independent
requests with one `parallel_group` and computes a critical path.

Parallelism also increases simultaneous demand. Bound it with a semaphore or
worker pool, propagate cancellation, retain per-item outcomes and respect
provider or GPU capacity. Never parallelise two writes that require ordering or
share an unsafe mutable state simply to improve a dashboard.

Batching is different: multiple compatible requests share one scheduler or
model batch. It can improve throughput but add queue delay. Measure throughput,
TTFT and tail latency together.

## Cache a decision, not just text

An exact response cache is safe only when its key contains every input that can
change the result. The lab scopes by:

- tenant;
- selected model;
- prompt version; and
- caller-provided data/version key.

It caches only read-like routing and extraction fixtures. Recommendations are
not cached by default. A production key may also need locale, authorization
scope, retrieval snapshot, generation parameters and policy version.

Semantic caching raises a harder question: how similar is similar enough? A
nearest cached answer can be fluent and wrong for a subtly different request.
Use task-specific thresholds, authorization filtering, expiry, provenance and a
measured false-hit rate. Never share private cached content across tenants.

## Build the quality–latency–cost decision table

Do not report one winning number. Use a trade-off table:

| Strategy | Quality | TTFT/p95 | End-to-end/p95 | Cost/request | Rejection/degradation |
| --- | --- | --- | --- | --- | --- |
| all-large baseline | measured | measured | measured | measured | measured |
| routed | measured | measured | measured | measured | measured |
| routed + pruning | measured | measured | measured | measured | measured |
| routed + scoped cache | measured | measured | measured | measured | measured |

Promote only a strategy whose quality and safety gates pass. Record the exact
model, prompt, dataset, code and hardware versions so the comparison can be
reproduced.

## Run the local lab

~~~shell
python -m labs.week_21.demo compare
python -m labs.week_21.demo smoke
python -m pytest tests/test_week21_optimization.py -q
~~~

Inspect `labs/week_21/LOGIC.md` before the implementation. Tests cover routing,
quality escalation, safe pruning, per-request budgets, TTFT, critical paths,
cache isolation, generator materialisation and deterministic replay.

## Production gaps to state aloud

The lab does not call a model, tokenizer or provider. Its microunits, throughput
and quality values are synthetic. It does not model queue contention, GPU memory,
continuous batching, network cancellation, semantic-cache correctness or real
streaming. Use it to learn the control contract, then replace every fixture with
measured evidence from the intended workload.

## Completion checklist

- Compare identical materialised work against an explicit baseline.
- Keep a quality floor and visible budget rejection.
- Prune only context classified as optional.
- Report TTFT and completion latency separately.
- Parallelise only independent calls and bound concurrency.
- Scope cache keys by tenant and every result-changing version.
- Treat synthetic units as teaching data, never current vendor pricing.
- Pass the lab tests and explain what they do not prove.
