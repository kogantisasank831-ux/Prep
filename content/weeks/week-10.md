---
layout: week
week: 10
phase: 3
status: approved
version: 1.0.0
last_reviewed: 2026-10-24
estimated_hours: 8
permalink: /weeks/week-10/
title: "LLM observability: follow a request and explain what changed"
description: Trace a retrieval assistant, inspect stage latency and version identities, account for model usage honestly, and diagnose a changed answer with a controlled comparison.
summary: Follow one procurement question through query planning, authorized search, reranking, context and citations, then add explicit prompt, model, usage and failure observations.
kicker_primary: LLM observability
kicker_secondary: Explain one request with evidence
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-10/beginner/
---

## The answer worked last week. What changed?

Ask the assistant: “What payment condition controls Schedule A for the 1,000 kg copper-wire line?” The full run returns three pieces of evidence: the Net 30 term after inspection approval, the clause connecting that term to Schedule A, and the matching line item. Now reduce the context budget from 1,400 to 300 characters. The answer still contains Net 30. It has lost the connecting clause and line item.

The retriever did not lose those sources. The reranker did not demote them. They were excluded while packing context. If all you saved was a final answer and total duration, several plausible explanations would remain unresolved. This week builds enough request history to locate that boundary.

Week 9 asked whether a system meets its evaluation criteria across labelled cases. Week 10 asks what happened inside a particular execution. Keep both: a completed trace cannot certify answer correctness, and a failing quality score cannot tell you every operational cause.

You will build a local tracing lab around the actual Week 7–8 retrieval components. Its normal response remains cited source excerpts. An optional **scripted model fixture** demonstrates prompts, model identity, synthetic usage and failure handling. It makes no provider call, downloads no weights and does not replace the extractive answer. The [beginner version]({{ '/weeks/week-10/beginner/' | relative_url }}) follows the same build more slowly.

Bring source/version lineage from Week 6, authorized retrieval from Week 7, context and citation contracts from Week 8, and quality boundaries from Week 9.

| Time | Work | Evidence to retain |
| --- | --- | --- |
| Hour 1 | Distinguish logs, metrics, traces and evaluation | A precise question for each signal |
| Hour 2 | Build a request with child spans | IDs, parents and a completed failure record |
| Hour 3 | Follow query planning and retrieved evidence | Eligible snapshot, ordered candidates and reranker identity |
| Hour 4 | Explain timings and version changes | Measurement boundary and comparison assumptions |
| Hours 5–6 | Run the tracing scenarios | Trace files, optional synthetic capture and cost calculation |
| Hour 7 | Diagnose the context regression | First differing stage and a controlled verification |
| Hour 8 | Complete exercises and interview practice | A short incident explanation with remaining uncertainty |

## Choose the signal that answers your question

Imagine a customer reports a slow response at 14:03. A latency histogram can tell you whether many requests slowed down around that time. A request trace can tell you which stages occupied this execution. A correlated log can add a discrete event such as a retry decision. The Week 9 evaluator tells you whether the answer met an independently defined task criterion.

| Signal | Question it helps answer | Example in this project |
| --- | --- | --- |
| Log | What event occurred? | Request completed with a manifest fingerprint |
| Metric | How often, how much, or how distributed? | Request count and duration distribution by operation/outcome |
| Trace | What operations made up this request? | Search variants, reranking, context and optional model span |
| Evaluation | Was the behavior acceptable for this case? | Required support retained; unavailable fact correctly handled |

The lab exports individual traces; it does not implement a metrics backend or dashboard. A useful future metric might group durations by a bounded operation and outcome. Attaching every question or request ID as a metric label creates a separate series for each value, making aggregation expensive and hard to interpret. Keep request-level correlation in traces or controlled logs.

**Checkpoint:** Can `status: ok` accompany a poor answer? Run `missing-fact`: source excerpts are returned without a runtime exception, although the Week 9 unavailable-date case expects abstention. Operational success and semantic success need separate fields. Now give those operational steps a structure.

## Give each operation a parent

A trace groups related operations. A span records one operation's identity, interval, status and attributes. Parent relationships show containment. These concepts also appear in [OpenTelemetry's trace model](https://opentelemetry.io/docs/concepts/signals/traces/); the lab uses a smaller, explicitly custom schema.

Here is the smallest runnable example, from the repository root in the configured Python environment:

```python
from labs.week_10.tracing import Stage, TraceRecorder

trace = TraceRecorder("example-001")
with trace.span(Stage.REQUEST) as request:
    request.set(generation_mode="cited_extractive")
    with trace.span(Stage.RETRIEVAL, parent=request) as search:
        search.set(candidate_count=3)

document = trace.document()
assert len(document["spans"]) == 2
print(document["schema"])
```

The schema is `week10-local-trace/1.0.0`. Each recorder creates a random nonzero 32-hex trace ID and distinct 16-hex span IDs. `request_id` is an application correlation label, not an authorization credential. Passing the active parent handle is explicit: this recorder supports one synchronous request, with no global “current request” variable. Cross-request, closed and fabricated parent handles are rejected.

| Operation | Parent | Why it gets this boundary |
| --- | --- | --- |
| `request` | None | Contains the observed assistant call |
| `query_plan` | request | Validates the original plus reviewed variants |
| `eligible_snapshot` | request | Applies source-version grants and filters before search |
| `retrieval` | request | Contains the search work across variants |
| `tool.hybrid_search` | retrieval | One actual read-only hybrid search per query variant |
| `query_fusion`, `rerank`, `deduplicate` | request | Distinct candidate transformations |
| `context`, `citations`, `extractive_answer` | request | Admission, citation validation and response construction |
| `prompt`, `model` | request | Present only when the optional model path has evidence |

The hybrid-search tool is a local function call. Calling it a tool does not make this an autonomous agent or imply that it can write to an external system. `attempt=1` records one call; the lab has no retries.

Records are appended when spans finish, so children usually appear before parents in the JSON array. Reconstruct relationships from IDs, and sort by start offset for a timeline. Array position is not execution order.

**Checkpoint:** If two tools share the retrieval parent, are they necessarily parallel? No. The lab runs them sequentially. Parentage describes relationship; intervals describe overlap.

## Preserve the question while observing search

What exactly was searched? A rewrite can make retrieval better while accidentally removing a number, code or condition. The lab reuses Week 8's query planner: the original remains first, variants are bounded, duplicates are removed, and protected terms must survive. That lexical guard cannot establish semantic equivalence; “approval after Net 30” can retain words while changing a relation.

Routine metadata records query length, variant counts and each tool's `query_index`. Full text belongs in the explicit synthetic capture. The reranker still scores candidates against the original question, and retrieval operates only on the authorized, filtered snapshot. Tracing must not run a second privileged search merely to explain a user's result.

Each tool records ordered candidate IDs and aligned retrieval scores. Query fusion records the combined pool; reranking records its ordered IDs and scores. Retrieval and reranker scores have different meanings: comparing their raw values as though they shared a probability scale is invalid. Compare membership, ordering and evaluated outcomes.

The snapshot fingerprint binds eligible source state; retrieval manifests bind configuration; source chunks carry version and location lineage in the controlled capture. A chunk ID is useful only while its immutable source/version mapping remains resolvable. Keeping an ID after deleting all supporting source artifacts limits what you can later reconstruct.

**Checkpoint:** Should adding a document denied to this analyst change their candidate list or trace metadata? No. The test suite compares the corpus with and without the private distractor and expects identical observed results and stage attributes. Timing and random IDs are excluded from that equality.

## Measure an interval before interpreting latency

When did the request occur, and how long did it take? Those are separate questions. The trace records an aware UTC start for chronology and uses integer `perf_counter_ns()` differences for elapsed intervals. Python documents this performance counter for short-duration measurement; its raw reference point is not a wall-clock timestamp. See the [Python time reference](https://docs.python.org/3.13/library/time.html#time.perf_counter_ns).

Convert a duration to milliseconds by dividing nanoseconds by 1,000,000. Integer nanoseconds avoid float timestamp subtraction, but do not imply nanosecond hardware accuracy. Unknown or invalid readings remain null, with `timing_error_count` incremented. A broken clock is not a measured zero-duration operation.

Parent durations are inclusive. If a request occupies 100 ms and retrieval occupies 40 ms inside it, adding them gives 140 ms of double-counted time. In a simple sequential trace, subtracting non-overlapping direct-child intervals can estimate uninstrumented/self time. With overlapping work, subtract the union of child intervals; sums overstate coverage. In a distributed service, queueing, network time and clock alignment require their own boundaries. The critical path matters more than the sum of concurrent work.

The lab's request interval begins inside `observe_request` and ends after response construction and any optional fixture call. It includes tracing overhead and development source hashing. It excludes corpus ingestion before the call, file export afterward, browser/network time and a user's full journey. There is no streaming path or time-to-first-token measurement.

A single local duration is a diagnostic observation. Performance comparisons need repeated controlled workloads, environment/version identity, warm/cold conditions, comparable instrumentation and an explicit distribution. Do not present this fixture's timing as model inference performance.

**Checkpoint:** Can a 60 ms parent contain two 40 ms children? Yes if those children overlap. The current synchronous lab does not create that overlap, but a future service can.

## Record the versions that can change behavior

Suppose the model name is identical in two runs. Could the answer still change? Yes: source ingestion, grants, index configuration, rewriting, reranking, context policy or the prompt may differ. A provider model alias may also move while keeping its display name.

The request records pipeline, configuration and implementation identities. `implementation_digest()` hashes the lab Python sources from Weeks 5–10; it is a development-file identity, not a signed release artifact or dependency lock. For a deployed system, add an immutable build/commit identity, runtime/dependency identity, data/index snapshot and relevant feature flags. A digest detects difference only for the inputs it actually includes.

The optional model span records model name, revision, fixture/provider mode and prompt version. The raw template is represented as explicit system/user text messages; the user message contains question and evidence JSON. Serialization boundaries matter: capturing a template name alone cannot show whether the wrong context was inserted. The controlled content artifact includes the constructed prompt and fixture response.

This prompt has no real tokenizer or provider request envelope. An eventual adapter must bind the actual serialized provider request, generation settings, resolved model revision where available, response identity and usage semantics. If a provider exposes only a mutable alias, state that limitation. Traces help reproduce inputs; they do not guarantee identical stochastic generations or recreate a disappeared service.

**Checkpoint:** Is a prompt version enough to compare two executions? No. Pair it with the supplied context, request configuration and model/artifact identity. That also prevents attributing a context-budget regression to a model update.

## Keep unreported tokens unknown

How many tokens did this request consume? In the normal lab path there is no generative model call, so generative usage is **not applicable**. The retrieval/reranking functions still use local CPU time. Absence of a provider token bill does not imply zero infrastructure cost.

| Usage provenance | Meaning | How this lab handles it |
| --- | --- | --- |
| `provider_reported` | An adapter reports counts from an actual provider response | Supported typed boundary; no live adapter supplied |
| `estimated` | A separate estimate rather than measured provider usage | Preserved as an estimate; not used as billable observation |
| `synthetic_fixture` | Scripted teaching values | Used only for the labelled fixture example |
| `not_reported` | Usage is unavailable for a model attempt | Counts remain null |
| `not_applicable` | No generative model attempt applies | Counts remain null |

Known zero and unknown have different meanings. A provider reporting zero cached input tokens is an observation. A timeout without usage is missing information; it does not establish that a provider performed no work or charged nothing. Streaming cancellation can likewise lose final usage. The lab simulates a timeout exception; it does not enforce a network deadline or reconcile provider billing.

Input and output counts must be exact nonnegative integers, with booleans rejected. Cached input tokens are a subset of total input. Do not add them to input again. A future adapter must normalize the provider's categories and document treatment of reasoning, tools, retries and cache writes before aggregating costs. Do not infer token counts from character counts.

**Checkpoint:** If input is 1,000 and cached input is 200, how much input is uncached? 800. This gives us the denominator for a transparent cost example.

## Calculate an estimate with an explicit rate card

Use invented rates to understand the arithmetic: USD 2 per million uncached input tokens, USD 0.50 per million cached input tokens and USD 8 per million output tokens. These are teaching values, not current provider prices.

For 1,000 total input, 200 cached input and 300 output tokens:

```python
from decimal import Decimal
from labs.week_10.demo import illustrative_prices
from labs.week_10.generation import Usage, estimate_cost

usage = Usage(1000, 300, 200, "synthetic_fixture")
cost = estimate_cost(usage, illustrative_prices())
assert cost.amount == Decimal("0.0041")
assert cost.currency == "USD"
print(cost.amount)
```

The independent arithmetic is `(800 × 2 + 200 × 0.50 + 300 × 8) / 1,000,000 = 0.0041`. The standard fixture uses zero cached tokens and produces `0.0044`. `Decimal` rates are constructed from strings, with bounded precision and finite nonnegative values. See [Python's decimal documentation](https://docs.python.org/3.13/library/decimal.html) for the numeric model.

Missing counts, unknown cache usage, a missing applicable cache rate or missing pricing leave cost null with a reason. A rate card carries identity and currency; changing it changes the interpretation of an estimate. The lab retains sub-cent values rather than rounding every request to cents. An accounting system would need a separately specified aggregation and rounding policy.

This estimate covers one model attempt's declared token categories. It excludes provider-specific fees, discounts, taxes, storage, retrieval infrastructure and other attempts. Reconcile against actual billing before calling it spend.

## Let failed operations leave useful records

What survives when generation raises? The span context manager closes active intervals in `finally`, records a bounded failure category, and re-raises the original exception. Parent spans also close during unwinding. Cancellation is recorded as `cancelled`; it is not converted into a successful answer.

| Failure category | Example trigger | What it establishes |
| --- | --- | --- |
| `validation` | A rewrite drops protected terms | The request plan failed its declared input contract |
| `identity_drift` | Retrieval/reranker configuration changes during execution | Compared component identity was unstable |
| `timeout` | Scripted backend raises `TimeoutError` | The attempted operation did not return normally |
| `model_contract` | Empty output, changed identity or fixture/provider provenance mix | The model boundary rejected its result |
| `permission`, `dependency`, `internal` | Corresponding application exceptions | A bounded operational category, requiring further authorized investigation |

The model boundary validates response shape and provenance. It does not establish claim truth, faithfulness or citation entailment. The fixture text itself is not a model-quality experiment. An expected `no_evidence` result is a completed application outcome, rather than a permission exception.

Routine traces deliberately omit exception messages and stack traces because these can contain payloads or credentials. An actual service may need protected diagnostic logging with reviewed redaction and access controls. Keep its correlation IDs consistent and its payload policy explicit.

**Checkpoint:** Does `telemetry_complete: true` mean the application succeeded? No. A failure can be completely observed. That field describes recorder drops/timing validity, not semantic quality, payload completeness or successful delivery.

## Observe the recorder too

What happens when the trace cannot be written? `deliver()` makes one export attempt and returns a separate delivery result. It does not replace an already computed answer, retry the model or disguise the export failure. The demo returns a nonzero exit status when either application work or trace delivery fails.

The recorder keeps at most 64 spans by default, configurable within a fixed bound. Once full, later spans are counted as dropped and their bodies still execute. Descendants of an omitted parent are omitted too, avoiding orphan records. Attribute names, text sizes and arrays are bounded. These are resource limits, not a guarantee that arbitrary values placed under allowed names are safe.

In a service, a synchronous file sink could delay the response or fail after partial writes. A production exporter needs bounded buffering, timeouts, explicit drop counters and shutdown behavior. Decide the service's failure policy deliberately: a best-effort diagnostic stream and a mandatory regulated audit record can require different guarantees. This teaching trace is not a durable audit log.

**Checkpoint:** If the model succeeded but export failed, should you rerun generation to recover the trace? That would create a second model attempt with potentially different output and cost. Diagnose delivery separately.

## Separate routine telemetry from content inspection

Do you need the full prompt in every trace? Usually the first investigation is cheaper with version identities, counts, source IDs and ordered ranks. For this fixed synthetic dataset, `--capture-synthetic-content` writes a separate `synthetic-content.json` containing the original request, rewrites, authorized retrieved chunks, context, constructed prompt and returned text when available. Without the flag, only `trace.json` is created.

On a failed request the demo may have no completed result to capture; null content is not proof that no intermediate work happened. Use completed stage metadata to understand the partial execution. The content flag is a controlled demonstration, not an automatic PII detector or approval to upload real conversations. No external collector receives either file.

Identifiers and fingerprints can still disclose relationships. Predictable inputs can make hashes guessable. Apply collection minimization and restricted access even when raw text is absent; [OpenTelemetry's sensitive-data guidance](https://opentelemetry.io/docs/security/handling-sensitive-data/) explains that instrumentation itself needs review. For real payload capture, define purpose, authorization, scrubbing, encryption, retention, deletion and source-access checks before collection. Broad access to observability must not bypass document permissions.

At higher traffic, sampling adds another boundary. Head sampling chooses early and cannot know every eventual failure. Tail sampling considers completed or mostly completed traces but needs buffering and enough relevant spans. Error-biased samples are useful for diagnosis and are not an unbiased denominator for overall failure rates. See [OpenTelemetry sampling](https://opentelemetry.io/docs/concepts/sampling/). This lab attempts every span within its capacity; it implements neither sampling strategy.

## Assemble and run the observed assistant

All commands run from the repository root. Use the project's declared Python environment; after installing `requirements-dev.txt`, the lab itself needs no additional packages, keys or model downloads. On Windows, replace `.venv/bin/python` with `.venv\Scripts\python.exe`. Each output directory must be new; choose another suffix when repeating a run.

```bash
.venv/bin/python -m labs.week_10.demo --scenario payment --output-dir .runtime/week10-payment
.venv/bin/python -m labs.week_10.demo --scenario tight --output-dir .runtime/week10-tight
.venv/bin/python -m labs.week_10.demo --scenario model-fixture --output-dir .runtime/week10-model --capture-synthetic-content
```

The model fixture reports `model_fixture_observed: true`. The default run reports false. These summaries contain no answer payload. Inspect the metadata with this script after the first command:

```python
import json
from pathlib import Path

trace = json.loads(Path(".runtime/week10-payment/trace.json").read_text())
assert trace["schema"] == "week10-local-trace/1.0.0"
assert trace["telemetry_complete"]
for span in sorted(trace["spans"], key=lambda item: item["start_offset_ns"]):
    duration = span["duration_ns"]
    ms = None if duration is None else duration / 1_000_000
    print(span["name"], span["status"], ms)
```

The default recorder has valid timing in this scenario; for arbitrary imported traces, handle null start offsets before sorting. Durations vary across machines and runs. Inspect the source responsibilities in `labs/week_10/`: `tracing.py` owns records/lifecycle, `generation.py` owns prompt/model/usage contracts, `pipeline.py` observes reused domain functions, and `demo.py` owns fixed scenarios and file output. See the [lab README](https://github.com/kogantisasank831-ux/Prep/tree/main/labs/week_10).

Run the deliberate error cases individually. Their nonzero exits are expected:

```bash
.venv/bin/python -m labs.week_10.demo --scenario bad-rewrite --output-dir .runtime/week10-bad-rewrite
.venv/bin/python -m labs.week_10.demo --scenario model-timeout --output-dir .runtime/week10-timeout
.venv/bin/python -m labs.week_10.demo --scenario model-invalid --output-dir .runtime/week10-invalid
.venv/bin/python -m pytest tests/test_week10_tracing.py -q
```

The rewrite case fails at planning. The timeout and invalid-output cases reach the model stage. Each file retains completed failure records. The tests also check cancellation, missing usage, exact cost arithmetic, source isolation, output preservation and parity with all thirty Week 9 assistant results.

## Find the first meaningful difference

Return to the “worked last week” report. Use controlled synthetic content capture for both `payment` and `tight` when you want to inspect source text. Compare these runs in stage order:

1. Confirm the same question, grants, filters, source snapshot and component identities. Record the intentional context-budget difference.
2. Compare ordered candidates after query fusion. In this pair they are equal.
3. Compare reranked results. These are equal too.
4. Compare context source IDs and citation counts. Full context admits three supporting spans; the 300-character context admits only the payment-term span.
5. Inspect the retained quotes. The connecting clause and line item have disappeared while the actual Net 30 term survives.
6. Restore the budget and verify support retention, then run the Week 9 evaluation to check broader effects. A fix for one query is not a general quality guarantee.

A changed config fingerprint is a lead, not a diagnosis by itself. The paired run plus the first differing stage supports the context-admission explanation. If retrieval already differed, investigate eligible data, index, query and retriever versions before adjusting generation. If context and constructed prompt matched but a real model response differed, investigate generation identity/settings and nondeterminism. Keep unknowns visible.

For latency, perform a separate comparison under controlled workload and environment. Adding these spans can change timings. This lesson's support-loss result makes no claim that either context setting is faster in production.

## Carry the model into an instrumented service

Only after understanding these boundaries should you choose a tracing stack. An OpenTelemetry SDK can create spans, propagate context and export through a collector/backend. The local JSON includes nulls and custom statuses; it is **not OTLP** and cannot be sent unchanged as an OTel payload. Map contracts explicitly and check the SDK's current semantic conventions for the integrations you adopt.

Across HTTP or queues, use a supported propagator to inject/extract trace context, rather than passing this Python handle. Context correlation is not authentication; apply normal authorization independently. Review incoming untrusted headers and outgoing metadata. [OpenTelemetry's propagation guide](https://opentelemetry.io/docs/concepts/context-propagation/) explains the cross-process boundary. For asynchronous Python work, use task-aware SDK context management; this recorder is neither thread-safe nor an async context manager.

A future real-model adapter must enforce actual timeouts/cancellation, validate provider responses, normalize reported usage and retain resolved identity where available. A deployment also needs export health, sampling policy and payload controls. This week provides the local observation contract, not that service deployment. Week 11 will examine prompt injection and other security boundaries; Week 12 will address deployment and monitoring.

## Practice explaining the evidence

**Exercise 1 — Reconstruct one trace.** Generate `payment`, identify the root and every tool's parent, and calculate root milliseconds without summing nested intervals. Retain a small table of IDs, parents and durations. Acceptance: no orphan records; all intervals are nonnegative or explicitly missing; the stated measurement boundary excludes ingestion and export.

**Exercise 2 — Diagnose lost support.** Generate full and tight captures in new directories. Write a five-sentence explanation naming the first differing stage and the specific missing evidence. Acceptance: candidate and reranked equality demonstrated; three-versus-one context spans shown; no claim that the payment term itself disappeared.

**Exercise 3 — Defend the cost.** Calculate the zero-cache and 200-cache examples by hand. Then change cached usage to null without substituting zero. Acceptance: `0.0044`, `0.0041` and unknown respectively, with synthetic provenance, currency and rate identity retained.

**Exercise 4 — Separate two failures.** Inspect the model-timeout trace, then call `deliver()` with a sink that raises. Acceptance: timeout usage remains null, original application exceptions propagate, delivery has one attempt, and an already obtained answer is unchanged. Do not simulate a second generation as an export retry.

**Exercise 5 — Propose a payload policy.** List what goes into routine metadata versus a restricted debug artifact for a real document assistant. Acceptance: source permissions apply to inspection; identifiers are treated as potentially sensitive; purpose, retention and deletion are explicit. Do not upload real data as part of this exercise.

For interviews, answer with a boundary and a concrete consequence:

| Prompt | A defensible answer |
| --- | --- |
| How do you debug a changed answer? | Freeze request/data/component identities, compare stage outputs and test one hypothesized cause; rerun relevant evaluation before generalizing. |
| Why isn't a trace enough to judge RAG quality? | It records execution. A completed extraction can return catalogue text that lacks the requested date; semantic expectations need evaluation. |
| Why use two clocks? | UTC places an event in time; monotonic differences measure elapsed intervals without treating a wall-clock adjustment as request latency. |
| Why not sum span durations? | Parent intervals include children, and concurrent children can overlap. Use the root boundary and analyze the critical path. |
| What does missing usage cost? | It is unknown. Failed calls may still incur work; reconcile usage/billing rather than treating missing telemetry as free. |
| Which versions matter? | Build/runtime, source/index snapshot, retrieval/reranker/configuration, prompt and resolved generation identity; record what cannot be pinned. |
| How do you protect observability data? | Minimize routine fields, restrict source/payload inspection, control retention, and verify instrumentation/export behavior. |

Close your notebook and explain why a complete error trace differs from a successful answer, why a hash does not establish anonymity, and why the tight context case is a context failure despite successful retrieval. Reopen the trace and point to the fields supporting each statement.

Your weekly deliverable is the observed assistant plus a short diagnostic note, trace artifacts, cost calculation and payload policy. It is ready for handoff when someone else can reproduce the controlled support loss, locate its stage and state what the trace cannot establish. The Week 10 assessment is a separate next step.

## Sources and next reading

- [OpenTelemetry traces](https://opentelemetry.io/docs/concepts/signals/traces/) — spans, relationships, attributes and exporters.
- [Python performance-counter reference](https://docs.python.org/3.13/library/time.html#time.perf_counter_ns) — elapsed measurements and integer nanoseconds.
- [Python decimal arithmetic](https://docs.python.org/3.13/library/decimal.html) — explicit decimal construction and precision.
- [OpenTelemetry sensitive data](https://opentelemetry.io/docs/security/handling-sensitive-data/) — minimization and the limits of hashing.
- [OpenTelemetry sampling](https://opentelemetry.io/docs/concepts/sampling/) — head/tail decisions and their trade-offs.
- [OpenTelemetry context propagation](https://opentelemetry.io/docs/concepts/context-propagation/) — correlation across execution boundaries.
- [Week 9 evaluation]({{ '/weeks/week-09/' | relative_url }}) — independent quality checks to pair with execution evidence.
