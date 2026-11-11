---
layout: week
week: 30
phase: 7
status: review
version: 1.0.0
last_reviewed: 2026-11-11
estimated_hours: 8
permalink: /weeks/week-30/beginner/
title: "Estimate serving needs and finish the experiment report"
description: Learn quantisation, weight and KV memory, throughput, latency, package versions and the final report sections.
summary: A model is ready to discuss only when its files, measurements, failures and comparison are traceable.
kicker_primary: Beginner path
kicker_secondary: From model file to measured, documented experiment
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-30/
---

## Know the main serving terms

- **Quantisation:** storing weights with fewer bits, such as 8 or 4.
- **Weight memory:** parameter count multiplied by bytes per weight.
- **KV cache:** per-request memory for attention history; it grows with context
  and concurrency.
- **Throughput:** completed requests or generated tokens per second.
- **TTFT:** time until the first output token.
- **End-to-end latency:** time until the usable response finishes.
- **Batching:** processing compatible requests together.

The [production route]({{ '/weeks/week-30/' | relative_url }}) adds capacity
headroom, realistic load profiles and packaging controls. The [assessment]({{ '/assessments/week-30/' | relative_url }})
tests the complete handoff.

## Do not count weight memory alone

Model weights share the GPU with KV cache, activations, temporary runtime memory
and fragmentation. A 4-bit estimate is only a first calculation. Keep safety
headroom and test the actual runtime. More concurrent long requests need more KV
memory.

## Measure speed from the user's view

Record throughput, TTFT and full latency together. A large batch may generate
more tokens each second but make one user wait longer. Test several input and
output lengths and concurrency levels, then report p50 and slow-tail values.

## Package exact versions

Save the model revision, tokenizer and chat template, adapter, quantisation,
runtime version, settings and checksums. Load them in a clean environment and
run known examples. Keep a rollback package.

## Complete the report

Include:

1. objective;
2. dataset and permission;
3. training configuration;
4. compute used;
5. loss curve;
6. evaluation;
7. failures;
8. cost;
9. comparison with RAG; and
10. lessons learned.

Add the package manifest and serving measurements. A failed experiment is still
valuable when the report explains why.

## Run the example

~~~shell
python -m labs.week_30.demo capacity
python -m labs.week_30.demo smoke
python -m pytest tests/test_week30_serving.py -q
~~~

Check the estimated weight and KV memory, requested versus possible concurrency,
measured synthetic latency and the report warnings. No real model server or GPU
is used by this lab.

## Completion checklist

- Explain why 4-bit weights do not equal total GPU memory.
- Measure throughput and user latency together.
- Test realistic request lengths and concurrency.
- Pin every model/package/runtime version.
- Test clean loading and rollback.
- Complete all ten report sections and include failures.
- Compare the result with prompting and RAG before recommending deployment.

