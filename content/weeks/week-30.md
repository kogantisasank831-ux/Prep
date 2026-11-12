---
layout: week
week: 30
phase: 7
status: review
version: 1.0.0
last_reviewed: 2026-11-11
estimated_hours: 8
permalink: /weeks/week-30/
title: "Package, benchmark and document the training experiment"
description: Estimate memory transparently, benchmark serving under load, bind model artefacts to versions and write the final evidence report.
summary: Serving readiness needs measured quality, memory, throughput, latency, packaging and rollback evidence—not a model file alone.
kicker_primary: Serving and documentation
kicker_secondary: Quantisation, capacity, load evidence and experiment report
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-30/beginner/
---

## Separate packaging from serving readiness

A saved model or adapter is an artefact. A deployable package also binds model
revision, tokenizer, chat template, adapter, quantisation format, generation
defaults, runtime compatibility, licences, checksums and evaluation report.
Serving readiness additionally needs target-hardware load evidence, security,
observability, rollback and an owner.

The [beginner route]({{ '/weeks/week-30/beginner/' | relative_url }}) introduces
the capacity terms. The [Week 30 assessment]({{ '/assessments/week-30/' | relative_url }})
checks formulas, measurement boundaries and report completeness.

## Treat quantisation as a candidate, not a free compression

Weight-only quantisation reduces theoretical weight storage:

\[
\text{weight GiB}=\frac{\text{parameters}\times\text{bits per weight}}{8\times2^{30}}.
\]

Actual allocation also includes scales/metadata, possibly unquantised layers,
dequantisation buffers, activations, KV cache, runtime workspaces and memory
fragmentation. Quantisation can change quality and kernel support. Compare each
format on the same evaluation and load suite, and record library, method,
calibration data, compute dtype and hardware.

Do not conflate training-time QLoRA storage, a merged adapter and a production
quantised inference artefact.

## Estimate KV cache and concurrency explicitly

For a declared architecture/runtime, calculate KV bytes per token from layers,
key/value heads, head dimension and cache dtype, or use a verified runtime
measurement. A conservative reservation is:

\[
\text{KV GiB/request}=\frac{\text{KV bytes/token}\times\text{maximum context}}{2^{30}}.
\]

Then subtract packed weights, runtime/activation budget and headroom from device
memory before dividing by per-request KV. This is an upper-bound planning model,
not a guarantee: paged allocation, prefix sharing, variable lengths, batching,
preemption and tensor/pipeline parallelism change behavior.

## Benchmark the actual serving stack

Use vLLM or an equivalent tool only if it supports the model, quantisation,
hardware and API contract you need. Pin its version and launch parameters. Test
the request distribution, not one prompt:

- input/output token percentiles and maximums;
- arrival pattern, concurrency and tenant mix;
- cold and warm starts;
- streaming and non-streaming;
- expected cancellation and timeout behavior; and
- representative structured outputs and tool calls.

Measure time to first token (TTFT), inter-token latency, end-to-end latency,
generated tokens per second, requests per second, queue time, errors, peak GPU
memory and quality. Report p50/p95/p99 and the exact interval. A larger batch can
increase throughput while worsening TTFT; choose from the SLO, not one maximum.

## Apply admission control and headroom

Reject, queue or reshape requests before memory exhaustion. Bound context and
output tokens, concurrent sequences and batching. Reserve headroom for workload
variation and runtime fragmentation. Validate overload behavior: controlled 429
or queue timeout is better than a process crash. Autoscaling cannot repair a
single replica that admits infeasible requests.

## Bind and verify the package

Create a manifest containing:

- model ID, immutable revision and licence;
- tokenizer/template revision;
- adapter revision and merge state;
- quantisation method and checksums;
- runtime/container version and launch configuration;
- generation defaults and safety controls;
- evaluation/report IDs; and
- target hardware plus compatibility tests.

Load the package in a clean environment, run a golden smoke suite and verify
checksums. Keep the previous compatible package and test rollback. Never rely on
an unpinned `latest` model or runtime tag.

## Write the final experiment report

The deliverable must include objective, dataset and rights, split/contamination
controls, training configuration, compute and runtime, loss curves, Week 29
evaluation, failures, cost, RAG comparison and lessons learned. Add package and
serving evidence so another engineer can reproduce or reject the conclusion.

Cost includes external spend plus consumed accelerator/CPU hours and engineering
time context. Report zero external spend honestly without implying zero resource
cost. Include negative findings and stopped runs; hiding them makes the final
comparison less useful.

## Run the capacity and report lab

~~~shell
python -m labs.week_30.demo capacity
python -m labs.week_30.demo report
python -m labs.week_30.demo smoke
python -m pytest tests/test_week30_serving.py -q
~~~

The lab separates theoretical packed-weight and worst-context KV estimates from
measured synthetic load observations. It validates a strict report schema and
emits warnings for omitted memory, infeasible concurrency, weak loss evidence,
missing failures or zero external spend. It does **not** launch vLLM, allocate a
GPU or prove production capacity.

## Final conclusion template

State whether the fine-tune met its domain gate, what regressed, whether RAG or
prompting won factual tasks, which quantisation retained quality, the measured
serving envelope, total resources, remaining risks and the recommended next
step. “Do not deploy this adapter” is a valid evidence-based conclusion.

## Completion checklist

- Benchmark every quantisation candidate on quality and target hardware.
- Separate weights, KV, activations/runtime and headroom.
- Load-test realistic lengths, concurrency, cold/warm state and streaming.
- Report throughput with TTFT and latency tails.
- Enforce context, output and concurrency admission limits.
- Bind model, tokenizer, template, adapter and runtime revisions.
- Verify clean-load smoke, checksums and rollback.
- Complete every report section, including failures, cost and RAG comparison.
- State a bounded recommendation without overstating the experiment.

