---
layout: week
week: 10
phase: 3
status: approved
version: 1.0.0
last_reviewed: 2026-10-24
estimated_hours: 8
permalink: /weeks/week-10/beginner/
title: "LLM observability: see what happened inside one answer"
description: Learn traces and spans through a small retrieval assistant, follow evidence through each stage, and explain timings, missing token counts and failures without guessing.
summary: Build a request history, compare a complete answer with one that lost supporting context, and practice reading the evidence one stage at a time.
kicker_primary: LLM observability
kicker_secondary: Beginner route through the same build
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-10/
---

## Start with a question you can investigate

The assistant answered a procurement question well last week. Today it gives a shorter answer. Someone says, “The model must have changed.” That is a possibility in a real system, but we need evidence before choosing it.

Our question is: “What payment condition controls Schedule A for the 1,000 kg copper-wire line?” The complete result has three parts: the payment term, a clause saying it controls Schedule A, and the matching line item. With a smaller context budget, only the payment-term quote fits. The system still finds and ranks all three pieces. The loss occurs later, when deciding what goes into the answer's evidence.

This week you will make that process visible. **Observability** means collecting useful evidence about a system's behavior so you can investigate it. Our build is local Python with a controlled synthetic corpus. The default assistant quotes sources; it does not call a generative model. An optional scripted fixture lets us practice observing a prompt, response and usage counts without an API account.

If retrieval, context or citations are unfamiliar, revisit [Week 8]({{ '/weeks/week-08/beginner/' | relative_url }}). [Week 9]({{ '/weeks/week-09/beginner/' | relative_url }}) explains whether answers meet their task criteria. The [main lesson]({{ '/weeks/week-10/' | relative_url }}) develops the production trade-offs after these basics.

| Study time | Focus | Keep this result |
| --- | --- | --- |
| Hour 1 | Why one answer needs an execution history | A clear debugging question |
| Hour 2 | Trace, span and parent IDs | A two-span example |
| Hour 3 | Search, rank and context stages | A stage-by-stage explanation |
| Hour 4 | Time and version identities | A correct timing calculation |
| Hours 5–6 | Run the local scenarios | Trace files and an optional synthetic capture |
| Hour 7 | Compare full and smaller context | Evidence for the stage that lost support |
| Hour 8 | Exercises and interview practice | A reproducible diagnostic note |

## A log, a metric and a trace answer different questions

A **log** records an event: “request completed.” A **metric** summarizes observations across events: “how many requests failed?” A **trace** follows related operations inside one execution: validation, search, ranking and answer construction.

Suppose you learn that the response took two seconds. A metric can show whether that is unusual. A trace can show which operation occupied most of the interval. A log can add a specific event such as a retry. You may need all three in a service; this lab builds traces only.

There is a fourth question: “Was the answer good?” That is evaluation. The missing-date example from Week 9 can complete normally while returning excerpts that do not answer the question. A trace status of `ok` means the operation did not raise an error; it does not grade the answer.

**Pause and check:** A tool finishes normally and returns no evidence. Is that necessarily a broken tool? No. The request may have no eligible matching evidence. Record the outcome accurately before deciding it is a failure.

## One trace contains several spans

A **span** describes one operation: its name, start, duration and result. A **trace** groups the related spans. A parent span contains a smaller operation. For example, the request contains retrieval, and retrieval contains a hybrid-search call.

Run this Python in the repository's configured environment:

```python
from labs.week_10.tracing import Stage, TraceRecorder

trace = TraceRecorder("first-example")
with trace.span(Stage.REQUEST) as request:
    with trace.span(Stage.RETRIEVAL, parent=request) as search:
        search.set(candidate_count=3)

saved = trace.document()
assert len(saved["spans"]) == 2
print(saved["schema"])
```

The `with` block marks an operation's lifetime. When you leave the inner block, search finishes. Leaving the outer block finishes the request. If an exception occurs inside, the recorder still closes the spans and raises the same exception again.

The schema printed is `week10-local-trace/1.0.0`. `trace_id` identifies the group; each `span_id` identifies one operation; `parent_span_id` points to the containing span. The root request has no parent. The human-readable `request_id` helps correlation and does not grant access to documents.

The JSON array lists spans when they finish. A child can appear before its parent. Follow IDs rather than assuming the first array element is the request. The lab uses explicit Python parent handles and supports one synchronous request per recorder.

**Pause and check:** Can two searches share one parent? Yes. That tells you they belong to the same retrieval operation. Their timings tell you whether they overlap; this lab runs them sequentially.

## Follow the evidence through the assistant

What should the trace record at each step? Use a small question with a concrete result:

| Step | What happens | Useful observation |
| --- | --- | --- |
| Validation | Check the request contract | Success or a bounded failure category |
| Query planning | Keep the question and reviewed search variants | Query count and each variant's index |
| Eligible snapshot | Apply document-version access and metadata filters | Eligible count and snapshot fingerprint |
| Hybrid search | Search permitted sources using lexical and dense teaching components | Ordered candidate IDs and scores |
| Fusion and reranking | Combine results and reorder the same pool | Before/after order and component identity |
| Context | Choose exact evidence that fits the budget | Selected source IDs, quote count and serialized size |
| Citations and answer | Validate selected source references and return excerpts | Citation count and application outcome |

A fingerprint is a digest used to compare a defined set of inputs. Different fingerprints tell you something in that set changed; they do not explain why it changed. You still need to inspect the relevant configuration or source mapping.

A rewrite can help search but can also drop a condition. The lab rejects variants that lose protected words, codes or numbers. This guard checks text constraints, not full meaning. The reranker continues to use the original question. Search never gets extra permission just because we are tracing it.

Routine trace files contain metadata rather than raw questions or passages. The optional synthetic capture contains the controlled text and authorized retrieved chunks. Denied material is excluded from both retrieval and its observations.

**Pause and check:** If the right chunk reached the ranked pool but never reached context, where do you investigate first? Context admission, budget and compression rules. Replacing the retriever would not address the observed boundary.

## Read time in the right units

“When?” and “how long?” need different measurements. UTC tells us when the trace began on a calendar. A monotonic performance counter measures elapsed time. Python's `perf_counter_ns()` returns integer nanoseconds for interval calculations; see its [time documentation](https://docs.python.org/3.13/library/time.html#time.perf_counter_ns).

To convert 2,500,000 nanoseconds into milliseconds, divide by 1,000,000: the result is 2.5 ms. Nanosecond units do not promise nanosecond accuracy. If a clock reading is invalid, the lab records missing timing and increments a timing-error counter.

The parent already includes time spent inside its children. If the request lasts 100 ms and its search lasts 40 ms, the total request time is still 100 ms. Adding them double-counts search. Concurrent operations need even more care because their intervals may overlap.

Our request timer covers the observed assistant call, including instrumentation. It excludes loading the corpus beforehand and writing files afterward. It is not a browser-to-server journey or a real model benchmark. The fixture has no streaming output, so it measures no time to first token.

**Pause and check:** Does a null duration mean an operation was instant? No. It means a valid interval is unavailable.

## Versions help explain changed behavior

You cannot compare two runs fairly if you do not know what ran. Keep identities for code, configuration, eligible sources and search/ranking components. On the optional model path, also keep the prompt version, model name, revision and whether it is a fixture or provider adapter.

The lab hashes its teaching Python sources as a development implementation identity. It does not include every installed dependency or represent a signed production build. A real release needs those extra identities. Likewise, a model display name can refer to a changing provider alias; record a resolved revision when available and state when it is unavailable.

The constructed prompt matters too. The same template can receive different evidence. In our optional fixture, the prompt has system and user text messages, and the user message contains JSON question/evidence. The explicit capture lets you inspect that input. It is not proof of prompt-injection resistance or answer truth.

**Pause and check:** The model name stayed the same while the context budget changed. Can the response change? Yes. Start with the changed inputs before blaming the model.

## Unknown token usage is different from zero

A token is a model-dependent unit of text processing. Characters are not a reliable token count. Our default extractive path makes no generative call, so generation usage is `not_applicable`, with null counts.

The optional fixture returns scripted numbers: 1,000 input, 300 output and zero cached input tokens. They are labelled `synthetic_fixture`. They were not measured by a tokenizer or reported by a provider. A future provider adapter has a separate `provider_reported` provenance.

If a model attempt times out before usage arrives, record `not_reported` and null counts. The provider might still have done work. Filling missing counts with zero would falsely imply known zero usage. Estimated counts must also remain distinguishable from actual reports.

Cached input is already inside the total input count. If total input is 1,000 and cached input is 200, uncached input is 800. You do not have 1,200 input tokens.

Use invented prices to practice: USD 2 per million uncached input, USD 0.50 per million cached input and USD 8 per million output. With 200 cached tokens and 300 output, the estimate is `(800 × 2 + 200 × 0.50 + 300 × 8) / 1,000,000 = 0.0041 USD`. With zero cached tokens, it is `0.0044 USD`.

```python
from decimal import Decimal
from labs.week_10.demo import illustrative_prices
from labs.week_10.generation import Usage, estimate_cost

usage = Usage(1000, 300, 200, "synthetic_fixture")
estimate = estimate_cost(usage, illustrative_prices())
assert estimate.amount == Decimal("0.0041")
```

The code uses exact decimal rates with an explicit currency and price identity. These are teaching prices, not a current price list. Missing required counts or rates leave cost unknown. This calculation is neither an invoice nor total infrastructure cost; normal retrieval still uses CPU resources.

**Pause and check:** Is a failed model call free? The trace alone cannot establish that. Missing usage requires investigation or billing reconciliation.

## Run the scenarios and inspect their files

From the repository root, use the declared Python environment with `requirements-dev.txt` installed. On Windows, use `.venv\Scripts\python.exe` in place of `.venv/bin/python`. No additional package, API key, paid account or model download is needed. Choose a fresh output directory every time; existing directories are preserved.

```bash
.venv/bin/python -m labs.week_10.demo --scenario payment --output-dir .runtime/week10-payment
.venv/bin/python -m labs.week_10.demo --scenario tight --output-dir .runtime/week10-tight
.venv/bin/python -m labs.week_10.demo --scenario model-fixture --output-dir .runtime/week10-model --capture-synthetic-content
```

Each run writes `trace.json`. The third command also writes `synthetic-content.json`, which includes the controlled prompt and fixture response. The returned assistant answer remains the extractive answer; the fixture output is observed separately. Without the content flag, raw request/prompt/response text is not exported.

Inspect the first trace after running it:

```python
import json
from pathlib import Path

trace = json.loads(Path(".runtime/week10-payment/trace.json").read_text())
assert trace["telemetry_complete"]
for span in trace["spans"]:
    print(span["name"], span["status"], span["parent_span_id"])
```

Remember that completion order puts children before parents. `telemetry_complete` means no span drops or invalid clock readings were reported. It does not mean that the answer is correct or that export always works.

Try these separately; both are intended to exit with an error while saving their trace:

```bash
.venv/bin/python -m labs.week_10.demo --scenario bad-rewrite --output-dir .runtime/week10-bad-rewrite
.venv/bin/python -m labs.week_10.demo --scenario model-timeout --output-dir .runtime/week10-timeout
.venv/bin/python -m pytest tests/test_week10_tracing.py -q
```

The first rejects the query plan. The second raises a scripted timeout in the model stage; it is not a live network timeout test. Error messages are excluded from routine traces. Bounded categories show the failing stage while the original exception is preserved for the caller.

Trace writing can fail separately from application work. The exporter tries once and reports delivery failure; it does not run the model again. The recorder also has a span limit. Beyond that limit, operations still execute while omitted spans are counted. Missing telemetry is visible rather than treated as complete observation.

## Explain the changed answer with evidence

Compare `payment` and `tight`. For raw quotes, generate both again in new directories with `--capture-synthetic-content`.

| Comparison | What this controlled pair shows |
| --- | --- |
| Question and source scope | Same request and eligible sources |
| Retrieved candidates | Same ordered pool |
| Reranked candidates | Same ordered results |
| Context budget | 1,400 versus 300 characters |
| Selected context | Three supporting spans versus one |
| Answer | Payment term survives; connecting clause and line item are omitted |

The first lost support appears at context selection. Restore the budget and verify that support returns, then rerun broader evaluation before claiming a general improvement. A changed fingerprint alone is only a lead. This controlled comparison connects it to actual stage behavior.

Also run `missing-fact` and `denied` if you want to separate quality from execution. The first returns real excerpts without the requested delivery date. The second returns no eligible evidence. Both can complete without a runtime exception, for different reasons.

**Pause and check:** Does this comparison prove a new retriever is unnecessary for every query? No. It diagnoses this pair. Other cases need their own evidence and evaluation.

## Decide what you are allowed to retain

More saved text can help debugging and can expose more sensitive information. This demo's content flag is only for fixed synthetic examples. It does not detect PII and does not authorize capturing real conversations. Even metadata can reveal source relationships, and hashing predictable values does not guarantee anonymity.

For a real system, first define the purpose and access/retention policy. Keep ordinary telemetry small. Put approved payload inspection behind source-aware permissions, scrubbing and a restricted storage policy. Avoid request IDs and questions as metric labels because each distinct value creates another series.

Larger systems sometimes sample traces. Head sampling chooses early; tail sampling can use later outcomes but needs buffering. A set chosen mainly for errors will not represent the overall error rate fairly. This lab has a bounded recorder and no sampling backend.

OpenTelemetry provides a standard ecosystem for instrumented services. Our file format is custom and is not OTLP. Moving across HTTP or queues requires supported context propagation; trace IDs never replace authentication. The current recorder is synchronous and should not be shared across concurrent requests.

## Practice before moving on

**Build a two-span history.** Run the first Python example and identify the root and search parent. Acceptance: two distinct span IDs in one trace, with a null root parent and a search parent pointing to the root.

**Find the lost support.** Keep full/tight traces and a short comparison note. Acceptance: demonstrate equal candidate/reranked results, three-versus-one context spans and the missing connecting clause. Explain why the Net 30 term itself was not lost.

**Calculate without guessing.** Reproduce `0.0044` for zero cached tokens and `0.0041` for 200 cached tokens. Then inspect missing usage. Acceptance: null stays unknown; synthetic counts and rates are labelled; cached tokens are not counted twice.

**Inspect failure honestly.** Find the failed span in the timeout run. Acceptance: bounded timeout category, null token counts and a completed error record, without claiming the provider charged zero.

Practice these interview answers aloud:

| Question | Answer to develop |
| --- | --- |
| What is a trace? | Related operations from one execution, connected through IDs and parent relationships. |
| Why keep evaluation too? | A trace explains execution; task criteria judge whether the answer was acceptable. |
| Why not add all durations? | Parent intervals already contain children, and operations can overlap. |
| What might change besides the model? | Sources, grants, query plan, retriever, reranker, context budget, prompt and configuration. |
| What if usage is unavailable? | Keep it unknown and distinguish it from known zero or estimated usage. |
| Can observability expose private data? | Yes. Minimize collection and control source/payload access and retention. |

You are ready to move on when you can show another person where support disappeared, explain the timing boundary, and separate an application failure from a trace-delivery failure. Keep the runnable lab, traces, calculation and diagnostic note. The assessment question bank will be a separate step.

## Read alongside the lab

- [OpenTelemetry traces](https://opentelemetry.io/docs/concepts/signals/traces/) — the wider span/trace vocabulary.
- [Python time](https://docs.python.org/3.13/library/time.html#time.perf_counter_ns) and [decimal](https://docs.python.org/3.13/library/decimal.html) — timing and explicit arithmetic.
- [Sensitive data in telemetry](https://opentelemetry.io/docs/security/handling-sensitive-data/) — collection choices and hashing limits.
- [Sampling](https://opentelemetry.io/docs/concepts/sampling/) and [context propagation](https://opentelemetry.io/docs/concepts/context-propagation/) — concepts for a later instrumented service.
- [Main Week 10 lesson]({{ '/weeks/week-10/' | relative_url }}) and [runnable lab](https://github.com/kogantisasank831-ux/Prep/tree/main/labs/week_10) — deeper contracts and implementation boundaries.
