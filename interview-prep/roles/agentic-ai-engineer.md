---
layout: "week"
status: "approved"
version: "1.2.0"
last_reviewed: "2026-11-09"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "Agentic AI Engineer foundation interview bank"
description: "Sixty guided questions for AI and Agentic AI engineering interviews."
summary: "Practise production Python, AI systems, embeddings, ingestion, RAG architecture, evaluation, security, reliability, and incident decisions."
permalink: "/interview-prep/roles/agentic-ai-engineer/"
kicker_primary: "Agentic AI Engineer"
kicker_secondary: "Batches 1–3 · 60 guided questions"
current_label: "Role bank"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
question_count: 60
---
## How to use this bank

These are interview-practice prompts, not a scored learning assessment. Answer aloud before opening the revision links. A strong response should state assumptions, make a decision, explain trade-offs, and identify evidence or failure modes. Use the follow-up probe to test whether the answer survives a deeper round.

### Suggested practice loop

1. Select five questions from different sections.
2. Give a 90-second answer without notes.
3. Compare your answer with the strong-answer signals.
4. Open only the revision sheet needed for the gap.
5. Repeat the answer in 45 seconds, then record one concrete project example.

**Bank size:** 60 questions across Batches 1–3 · **Status:** Batches 1–3 approved

## Python and service engineering

### AIE-B1-01 — Why are mutable default arguments dangerous, and how would you fix the function?

**Round:** Python · **Depth:** Foundation

**Strong answer signals**

- Defaults are created once at function definition, so calls can share state.
- Use `None` or an immutable sentinel and create the container inside the function.
- Mention a regression test proving two calls do not affect one another.

**Follow-up probe:** How does this differ from a shallow-copy bug in nested state?

**Revision links:** [Python]({{ '/interview-prep/cheat-sheets/python/' | relative_url }})

### AIE-B1-02 — Choose among threads, processes, and `asyncio` for an AI API that performs HTTP model calls plus CPU-heavy parsing.

**Round:** Python · **Depth:** Applied

**Strong answer signals**

- Use async I/O for many waiting network calls with bounded concurrency.
- Move CPU-bound parsing to a process pool or separate worker; the GIL limits CPU-bound threads.
- Discuss timeouts, cancellation, pool limits, and measurement instead of choosing one mechanism globally.

**Follow-up probe:** What changes if the model client is synchronous and cannot be replaced?

**Revision links:** [Python]({{ '/interview-prep/cheat-sheets/python/' | relative_url }})

### AIE-B1-03 — How would you prevent 1,000 concurrent requests from overwhelming an external model endpoint?

**Round:** System design · **Depth:** Applied

**Strong answer signals**

- Bound admission and in-flight calls with queues, semaphores, or worker limits.
- Apply deadlines, rate limits, backpressure, and explicit overload responses.
- Track queue depth, saturation, latency percentiles, timeout rate, and downstream quotas.

**Follow-up probe:** Where should retries be placed, and when should they be disabled?

**Revision links:** [Python]({{ '/interview-prep/cheat-sheets/python/' | relative_url }}) · [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }})

### AIE-B1-04 — Design the validation and error contract for a classification endpoint.

**Round:** API design · **Depth:** Applied

**Strong answer signals**

- Validate types, sizes, enums, and cross-field invariants at the boundary.
- Return stable machine-readable error codes with safe messages and correlation IDs.
- Keep business failures distinct from transport failures and never expose prompts, secrets, or stack traces.

**Follow-up probe:** Which failures are safe to retry automatically?

**Revision links:** [Python]({{ '/interview-prep/cheat-sheets/python/' | relative_url }})

## Data and persistence

### AIE-B1-05 — A join doubled the reported number of successful model runs. How do you diagnose it?

**Round:** SQL · **Depth:** Foundation

**Strong answer signals**

- State the intended grain of every table before joining.
- Measure row counts and key uniqueness before and after each join.
- Pre-aggregate or deduplicate the many side, then validate totals against an independent query.

**Follow-up probe:** When is `COUNT(DISTINCT run_id)` a repair, and when does it hide a modeling error?

**Revision links:** [SQL]({{ '/interview-prep/cheat-sheets/sql/' | relative_url }})

### AIE-B1-06 — Design a minimal relational model for idempotent AI requests and attempts.

**Round:** SQL and architecture · **Depth:** Applied

**Strong answer signals**

- Separate the semantic request from individual attempts and outputs.
- Use a unique idempotency key scoped to tenant and operation, plus request fingerprint.
- Persist status transitions, model/config version, timestamps, error class, and audit-safe metrics transactionally.

**Follow-up probe:** How would you handle the same idempotency key with a different payload?

**Revision links:** [SQL]({{ '/interview-prep/cheat-sheets/sql/' | relative_url }}) · [Python]({{ '/interview-prep/cheat-sheets/python/' | relative_url }})

### AIE-B1-07 — Write the reasoning for selecting the latest valid model result per request.

**Round:** SQL · **Depth:** Applied

**Strong answer signals**

- Define valid status and deterministic ordering, including a tie-breaker.
- Use `ROW_NUMBER()` over request partitions ordered by completion time and attempt ID.
- Filter validity before ranking when invalid attempts must not displace a valid result.

**Follow-up probe:** How would late-arriving corrections change the query?

**Revision links:** [SQL]({{ '/interview-prep/cheat-sheets/sql/' | relative_url }})

## Evaluation and model decisions

### AIE-B1-08 — Explain a confidence interval for an observed 92% task-success rate.

**Round:** Statistics · **Depth:** Foundation

**Strong answer signals**

- It is an interval from a procedure with stated long-run coverage, not a probability that a fixed parameter lies inside.
- State the sample size, independence assumptions, and sampling design.
- Report the interval and important slices rather than only the point estimate.

**Follow-up probe:** What if cases are clustered by customer or workflow?

**Revision links:** [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

### AIE-B1-09 — For a rare unsafe-action detector, when would PR-AUC be more useful than ROC-AUC?

**Round:** Metrics · **Depth:** Applied

**Strong answer signals**

- Rare positives can make a small false-positive rate operationally large.
- PR focuses on precision and recall for the positive class and should be compared with prevalence.
- Still choose an operating threshold using harm, review capacity, and recall requirements.

**Follow-up probe:** What metric would you add if predicted probabilities drive escalation?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

### AIE-B1-10 — How do you detect leakage in an agent or LLM evaluation dataset?

**Round:** ML · **Depth:** Applied

**Strong answer signals**

- Trace whether labels, future outcomes, reference answers, or derived fields enter inputs.
- Check near-duplicate entities and templates across train, development, and held-out sets.
- Keep preprocessing and prompt/model selection inside the development boundary and protect the final set.

**Follow-up probe:** How would contamination from public benchmark answers appear?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

### AIE-B1-11 — A larger model improves accuracy by 1% but triples latency and cost. How do you decide?

**Round:** ML · **Depth:** Applied

**Strong answer signals**

- Start from minimum acceptable quality and operational constraints.
- Compare confidence intervals, failure slices, calibration, latency percentiles, throughput, and total cost.
- Consider routing, cascade, abstention, or a smaller baseline rather than one model for every case.

**Follow-up probe:** What evidence is required before claiming the 1% improvement is meaningful?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

### AIE-B1-12 — Design an experiment to compare a new AI-assisted workflow with the current process.

**Round:** Statistics and product · **Depth:** Applied

**Strong answer signals**

- Define the unit, randomization, primary outcome, guardrails, exposure, and analysis window.
- Estimate sample size from baseline, minimum useful effect, variance, and power.
- Plan for noncompliance, interference, novelty, sample-ratio mismatch, and operational adoption.

**Follow-up probe:** When would a switchback or cluster-randomized design be preferable?

**Revision links:** [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }}) · [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }})

## Production reasoning

### AIE-B1-13 — Offline accuracy improved, but production business outcomes did not. What do you check first?

**Round:** Debugging · **Depth:** Applied

**Strong answer signals**

- Verify instrumentation, population, label timing, and online/offline feature parity.
- Check threshold, calibration, workflow adoption, latency, capacity, and whether the action can change the outcome.
- Segment by time and cohort, compare with the baseline, and avoid blaming drift without evidence.

**Follow-up probe:** How would you separate model failure from product-workflow failure?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [SQL]({{ '/interview-prep/cheat-sheets/sql/' | relative_url }})

### AIE-B1-14 — Design a production email-classification service before adding any generative model.

**Round:** System design · **Depth:** Applied

**Strong answer signals**

- Define taxonomy, ambiguity/escalation policy, throughput, latency, privacy, and success metrics.
- Start with a deterministic or classical baseline, versioned preprocessing, API validation, and an auditable result store.
- Include canary rollout, monitoring, human review, retry/idempotency behavior, and rollback.

**Follow-up probe:** Which requirements would justify an LLM instead of a smaller classifier?

**Revision links:** [Python]({{ '/interview-prep/cheat-sheets/python/' | relative_url }}) · [SQL]({{ '/interview-prep/cheat-sheets/sql/' | relative_url }}) · [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }})

### AIE-B1-15 — An AI assistant returns five candidate documents. Which retrieval metrics would you use and why?

**Round:** Ranking metrics · **Depth:** Applied

**Strong answer signals**

- Use Recall@K when missing relevant evidence is costly.
- Use MRR for the first useful result and NDCG for graded relevance across the ranking.
- Define the judged query population and include latency, coverage, and failure slices.

**Follow-up probe:** How can a higher offline NDCG fail to improve answer quality?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

### AIE-B1-16 — Explain a safe retry policy for model calls.

**Round:** Reliability · **Depth:** Applied

**Strong answer signals**

- Classify transient versus permanent failures and require idempotent semantics.
- Bound attempts, backoff, jitter, per-attempt timeout, and total deadline.
- Honor server retry hints, prevent retry storms, and expose exhaustion as an explicit outcome.

**Follow-up probe:** Why is retrying a validation error harmful?

**Revision links:** [Python]({{ '/interview-prep/cheat-sheets/python/' | relative_url }})

## Ownership and evidence

### AIE-B1-17 — What do you inspect when reviewing a Python AI-service pull request?

**Round:** Code review · **Depth:** Lead

**Strong answer signals**

- Contracts, validation, authorization, resource cleanup, concurrency bounds, and failure semantics.
- Tests for happy, boundary, negative, duplicate, and cancellation paths.
- Observability, dependency/config changes, privacy, rollout, rollback, and whether complexity is justified.

**Follow-up probe:** Which issues block merge versus become follow-up work?

**Revision links:** [Python]({{ '/interview-prep/cheat-sheets/python/' | relative_url }})

### AIE-B1-18 — Explain one AI project at two-minute and ten-minute depth.

**Round:** Project deep dive · **Depth:** Lead

**Strong answer signals**

- Lead with the business decision, constraints, baseline, and measurable outcome.
- Defend architecture, data, evaluation, operational trade-offs, and alternatives.
- State what failed, what remains unproven, and what you would change next.

**Follow-up probe:** Which number would a skeptical interviewer ask you to prove?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

### AIE-B1-19 — A release increases p95 latency and duplicate downstream calls. How do you respond?

**Round:** Incident · **Depth:** Lead

**Strong answer signals**

- Stop or roll back the change using the safest bounded path.
- Use traces and idempotency evidence to isolate queueing, retry, and concurrency changes.
- Reconcile ambiguous side effects, communicate impact, and add a regression gate after root cause is established.

**Follow-up probe:** What data must be retained without logging sensitive payloads?

**Revision links:** [Python]({{ '/interview-prep/cheat-sheets/python/' | relative_url }}) · [SQL]({{ '/interview-prep/cheat-sheets/sql/' | relative_url }})

### AIE-B1-20 — When should an AI workflow remain deterministic instead of becoming an agent?

**Round:** Trade-off · **Depth:** Lead

**Strong answer signals**

- Prefer deterministic logic when the path, rules, and acceptable outputs are known.
- Use model-driven choice only when variability provides measurable value and is bounded by validation and authority.
- Compare reliability, auditability, latency, cost, security, and recovery—not novelty.

**Follow-up probe:** What is the smallest experiment that could justify agentic behavior?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

## Batch 2 · Deep learning

### AIE-B2-01 — Walk through the forward pass, loss, backpropagation, and optimizer step.

**Round:** Deep learning · **Depth:** Foundation

**Strong answer signals**

- Affine layers and nonlinearities produce activations and a prediction.
- The loss converts prediction error into a scalar objective; backprop applies the chain rule to compute parameter gradients.
- The optimizer updates parameters, gradients are cleared deliberately, and train/eval modes must be handled correctly.

**Follow-up probe:** What symptom would you see if gradients were never cleared?

**Revision links:** [Deep learning]({{ '/interview-prep/cheat-sheets/deep-learning-neural-networks/' | relative_url }})

### AIE-B2-02 — Training loss falls while validation loss rises. How do you investigate?

**Round:** Training debugging · **Depth:** Applied

**Strong answer signals**

- Confirm split integrity, label quality, preprocessing parity, and duplicate or entity leakage before calling it overfitting.
- Inspect learning curves, capacity, regularization, augmentation, early stopping, and distribution mismatch.
- Re-evaluate on slices and a protected holdout; do not tune repeatedly on the test set.

**Follow-up probe:** How would you distinguish overfitting from train/validation preprocessing drift?

**Revision links:** [Deep learning]({{ '/interview-prep/cheat-sheets/deep-learning-neural-networks/' | relative_url }})

### AIE-B2-03 — Compare BatchNorm, LayerNorm, and RMSNorm for an interview answer.

**Round:** Architecture · **Depth:** Applied

**Strong answer signals**

- BatchNorm uses batch statistics and behaves differently in training and evaluation, making batch composition relevant.
- LayerNorm normalizes features per example/token and is common in transformers.
- RMSNorm scales by root-mean-square without mean subtraction; choice depends on architecture, kernels, and verified quality.

**Follow-up probe:** Why can very small batches make BatchNorm unreliable?

**Revision links:** [Deep learning]({{ '/interview-prep/cheat-sheets/deep-learning-neural-networks/' | relative_url }}) · [Transformers]({{ '/interview-prep/cheat-sheets/transformers/' | relative_url }})

### AIE-B2-04 — A model has unstable or exploding gradients. What do you check?

**Round:** Optimization · **Depth:** Applied

**Strong answer signals**

- Verify inputs, targets, loss scale, learning rate, initialization, and numerical precision.
- Inspect gradient norms and activation distributions; use residuals, normalization, suitable activations, and stable losses.
- Clipping can bound updates but should not hide the underlying cause.

**Follow-up probe:** How do vanishing gradients require a different response?

**Revision links:** [Deep learning]({{ '/interview-prep/cheat-sheets/deep-learning-neural-networks/' | relative_url }})

### AIE-B2-05 — Explain mixed precision, quantization, and gradient accumulation without treating them as interchangeable.

**Round:** Efficiency · **Depth:** Applied

**Strong answer signals**

- Mixed precision accelerates training/inference with selected lower-precision operations and loss scaling where needed.
- Quantization stores or computes weights/activations at lower precision, mainly reducing memory/bandwidth with kernel and quality trade-offs.
- Gradient accumulation emulates a larger effective batch across micro-batches but does not reduce total compute and changes optimizer-step frequency.

**Follow-up probe:** Which technique helps when activations, not weights, dominate memory?

**Revision links:** [Deep learning]({{ '/interview-prep/cheat-sheets/deep-learning-neural-networks/' | relative_url }}) · [LLM and Generative AI]({{ '/interview-prep/cheat-sheets/llm-generative-ai/' | relative_url }})

## Batch 2 · NLP

### AIE-B2-06 — Why is TF-IDF plus a linear model still a serious NLP baseline?

**Round:** NLP · **Depth:** Foundation

**Strong answer signals**

- It is fast, sparse, interpretable, and strong for many classification tasks with enough lexical signal.
- It provides a low-cost reference for accuracy, latency, memory, and debugging.
- Its limitations include weak context, word order, semantics, and vocabulary transfer.

**Follow-up probe:** Which error pattern would justify moving to contextual embeddings?

**Revision links:** [NLP]({{ '/interview-prep/cheat-sheets/nlp/' | relative_url }})

### AIE-B2-07 — Why is the tokenizer part of the model contract?

**Round:** Tokenization · **Depth:** Applied

**Strong answer signals**

- It defines token IDs, boundaries, special tokens, truncation, and input length.
- Changing tokenizer or normalization can invalidate checkpoint embeddings and training-serving parity.
- Version model and tokenizer together and test multilingual, numeric, whitespace, and adversarial edge cases.

**Follow-up probe:** How can tokenization increase latency and cost for one language?

**Revision links:** [NLP]({{ '/interview-prep/cheat-sheets/nlp/' | relative_url }}) · [Transformers]({{ '/interview-prep/cheat-sheets/transformers/' | relative_url }})

### AIE-B2-08 — Design evaluation for a multilingual intent classifier with an unknown-intent route.

**Round:** Evaluation · **Depth:** Applied

**Strong answer signals**

- Use per-language and macro metrics, calibration, reject/unknown accuracy, and confusion analysis.
- Build representative language, dialect, code-switching, short-text, and rare-intent slices.
- Choose rejection thresholds from business risk and review capacity; monitor language mix and preprocessing drift.

**Follow-up probe:** How would you evaluate a language with very few labels?

**Revision links:** [NLP]({{ '/interview-prep/cheat-sheets/nlp/' | relative_url }})

### AIE-B2-09 — How should named-entity recognition be evaluated?

**Round:** Information extraction · **Depth:** Applied

**Strong answer signals**

- Prefer entity-level exact or declared partial span precision, recall, and F1, not only token accuracy.
- Define boundary and type matching, nested entities, discontinuous spans, and annotation policy.
- Audit errors by entity type, document source, language, length, and downstream consequence.

**Follow-up probe:** Why can token accuracy look excellent while entity extraction is poor?

**Revision links:** [NLP]({{ '/interview-prep/cheat-sheets/nlp/' | relative_url }})

## Batch 2 · Transformers

### AIE-B2-10 — Explain scaled dot-product attention using Q, K, and V.

**Round:** Transformers · **Depth:** Foundation

**Strong answer signals**

- Queries score compatibility with keys; softmax converts scaled scores into weights; weights combine values.
- Scaling by the square root of key dimension prevents dot products from driving softmax into saturation.
- State tensor shapes, mask semantics, and quadratic sequence interaction cost.

**Follow-up probe:** What changes between self-attention and cross-attention?

**Revision links:** [Transformers]({{ '/interview-prep/cheat-sheets/transformers/' | relative_url }})

### AIE-B2-11 — Choose among encoder-only, decoder-only, and encoder-decoder models.

**Round:** Architecture · **Depth:** Applied

**Strong answer signals**

- Encoder-only models suit bidirectional representation tasks such as classification or retrieval.
- Decoder-only models suit causal generation and flexible instruction following.
- Encoder-decoder models naturally map a source sequence to a target sequence; compare quality, latency, data, and serving constraints.

**Follow-up probe:** Why might a decoder-only model still be used for classification?

**Revision links:** [Transformers]({{ '/interview-prep/cheat-sheets/transformers/' | relative_url }}) · [NLP]({{ '/interview-prep/cheat-sheets/nlp/' | relative_url }})

### AIE-B2-12 — What masking bugs commonly break transformer systems?

**Round:** Masking · **Depth:** Applied

**Strong answer signals**

- Confusing causal and padding masks can leak future tokens or attend to padding.
- Incorrect shape, broadcast, dtype, or sign can silently change attention.
- Test tiny sequences with known visibility and inspect logits/attention behavior rather than trusting the API call.

**Follow-up probe:** How would future-token leakage appear during training and inference?

**Revision links:** [Transformers]({{ '/interview-prep/cheat-sheets/transformers/' | relative_url }})

### AIE-B2-13 — What does the KV cache save, and what does it cost?

**Round:** Inference · **Depth:** Applied

**Strong answer signals**

- It reuses previous-layer keys and values so autoregressive decoding avoids recomputing the entire prefix.
- Memory grows with layers, sequence length, batch/concurrency, KV heads, head dimension, and precision.
- It improves decode compute but introduces memory pressure, paging, eviction, and concurrency limits.

**Follow-up probe:** Why do GQA and MQA help serving concurrency?

**Revision links:** [Transformers]({{ '/interview-prep/cheat-sheets/transformers/' | relative_url }}) · [LLM and Generative AI]({{ '/interview-prep/cheat-sheets/llm-generative-ai/' | relative_url }})

### AIE-B2-14 — Differentiate FlashAttention, GQA/MQA, and quantization.

**Round:** Efficiency · **Depth:** Lead

**Strong answer signals**

- FlashAttention changes the exact-attention execution to reduce memory traffic and intermediate storage.
- GQA/MQA reduce the number of KV heads and therefore KV-cache memory, with architecture/quality trade-offs.
- Quantization reduces representation precision for weights and possibly activations/cache; each technique targets a different bottleneck.

**Follow-up probe:** Which one helps prefill latency versus decode concurrency?

**Revision links:** [Transformers]({{ '/interview-prep/cheat-sheets/transformers/' | relative_url }}) · [LLM and Generative AI]({{ '/interview-prep/cheat-sheets/llm-generative-ai/' | relative_url }})

## Batch 2 · LLM and Generative AI

### AIE-B2-15 — Compare prompting, RAG, and fine-tuning.

**Round:** LLM engineering · **Depth:** Foundation

**Strong answer signals**

- Prompting changes instructions/context, RAG supplies external evidence, and fine-tuning changes model behavior or parameters.
- Choose the least complex option that addresses the observed error: knowledge freshness often favors retrieval; consistent behavior/style may favor adaptation.
- Evaluate combinations against a fixed baseline, data boundary, latency, cost, and maintenance plan.

**Follow-up probe:** Which approach would you choose for rapidly changing policy documents?

**Revision links:** [LLM and Generative AI]({{ '/interview-prep/cheat-sheets/llm-generative-ai/' | relative_url }})

### AIE-B2-16 — Why does valid JSON not prove a correct LLM answer?

**Round:** Structured output · **Depth:** Applied

**Strong answer signals**

- Syntax/schema validation proves shape and types, not factual support or business validity.
- Add semantic validators, allowlists, cross-field rules, evidence checks, and safe fallbacks.
- Treat output as untrusted input and retain model/prompt/schema versions for audit.

**Follow-up probe:** Which validation failures should trigger retry versus human review?

**Revision links:** [LLM and Generative AI]({{ '/interview-prep/cheat-sheets/llm-generative-ai/' | relative_url }})

### AIE-B2-17 — Explain LoRA and QLoRA, including what they do not guarantee.

**Round:** Fine-tuning · **Depth:** Applied

**Strong answer signals**

- LoRA learns low-rank adapter updates while the base remains frozen; QLoRA keeps the frozen base quantized during adapter training.
- They reduce trainable parameters and memory but still need sound data, templates, evaluation, and deployment compatibility.
- They do not automatically add reliable factual knowledge, safety, calibration, or production quality.

**Follow-up probe:** When would full fine-tuning be justified despite higher cost?

**Revision links:** [LLM and Generative AI]({{ '/interview-prep/cheat-sheets/llm-generative-ai/' | relative_url }}) · [Deep learning]({{ '/interview-prep/cheat-sheets/deep-learning-neural-networks/' | relative_url }})

### AIE-B2-18 — Design an LLM evaluation gate for a production release.

**Round:** Evaluation · **Depth:** Applied

**Strong answer signals**

- Use versioned representative and adversarial cases with deterministic task metrics where possible.
- Measure task quality, grounding, schema validity, safety, robustness, latency, cost, and failure slices against a current baseline.
- Use human review and judges with calibrated rubrics; record judge bias/variance and block release on declared critical regressions.

**Follow-up probe:** How do you prevent the evaluation set from becoming a tuning set?

**Revision links:** [LLM and Generative AI]({{ '/interview-prep/cheat-sheets/llm-generative-ai/' | relative_url }})

### AIE-B2-19 — Choose between a hosted model and a self-hosted open-weight model.

**Round:** Serving · **Depth:** Lead

**Strong answer signals**

- Compare quality, data handling, latency, concurrency, regional/compliance needs, licensing, hardware, operations, and total cost.
- Benchmark the actual workload, context lengths, output lengths, batching, and failure behavior.
- Plan routing, observability, version pinning, rollback, and provider/model substitution rather than relying on headline tokens per second.

**Follow-up probe:** At what utilization does self-hosting stop being obviously cheaper?

**Revision links:** [LLM and Generative AI]({{ '/interview-prep/cheat-sheets/llm-generative-ai/' | relative_url }}) · [Transformers]({{ '/interview-prep/cheat-sheets/transformers/' | relative_url }})

### AIE-B2-20 — A new prompt improves average quality but increases unsafe outputs on one slice. Do you release?

**Round:** Safety and release · **Depth:** Lead

**Strong answer signals**

- Do not average away a declared safety gate; quantify severity, frequency, reachability, and affected users.
- Investigate prompt/model interaction, add deterministic controls where possible, and retest on independent cases.
- Release only with accepted residual risk, bounded rollout, monitoring, and immediate rollback.

**Follow-up probe:** Who must own the residual-risk decision?

**Revision links:** [LLM and Generative AI]({{ '/interview-prep/cheat-sheets/llm-generative-ai/' | relative_url }})


## Batch 3 · Embeddings and vector search

### AIE-B3-01 — Retrieval quality collapsed after changing the embedding model. How do you debug it?

**Round:** Vector search debugging · **Depth:** Applied

**Strong answer signals**

- Verify that query and document embeddings use the same model, preprocessing, dimensions, normalization, and version.
- Check whether the index metric matches the model contract and compare exact-search recall with ANN recall before blaming generation.
- Inspect data slices, stale vectors, deployment order, and rollback readiness; re-embed into a versioned index rather than mutating blindly.

**Follow-up probe:** How would you migrate a large corpus without serving mixed embedding spaces?

**Revision links:** [Embeddings and vector search]({{ '/interview-prep/cheat-sheets/embeddings-vector-search/' | relative_url }})

### AIE-B3-02 — Design hybrid retrieval for queries containing both business meaning and exact identifiers.

**Round:** Retrieval design · **Depth:** Applied

**Strong answer signals**

- Use sparse retrieval for exact tokens, codes, numbers, and rare terms while dense retrieval covers semantic matches.
- Normalize or rank-fuse independent result lists, then deduplicate and rerank a bounded candidate set.
- Evaluate lexical, dense, hybrid, and reranked variants on representative query slices instead of assuming hybrid is always better.

**Follow-up probe:** When would reciprocal-rank fusion be safer than combining raw scores?

**Revision links:** [Embeddings and vector search]({{ '/interview-prep/cheat-sheets/embeddings-vector-search/' | relative_url }})

### AIE-B3-03 — Tune an HNSW-backed service that misses latency SLOs but cannot lose much recall.

**Round:** ANN performance · **Depth:** Advanced

**Strong answer signals**

- Establish exact-search ground truth and measure recall@K, p50/p95 latency, memory, throughput, and filtered-query behavior.
- Tune build-time and query-time parameters separately, including graph connectivity, construction effort, and search effort.
- Profile filters, vector dimensions, concurrency, and hardware; use controlled sweeps and retain a rollbackable index artifact.

**Follow-up probe:** Why can an ANN setting that works without filters fail badly after selective metadata filtering?

**Revision links:** [Embeddings and vector search]({{ '/interview-prep/cheat-sheets/embeddings-vector-search/' | relative_url }})

### AIE-B3-04 — How do you enforce tenant and document permissions in vector retrieval?

**Round:** Retrieval security · **Depth:** Advanced

**Strong answer signals**

- Derive trusted tenant and principal scope from authenticated server-side context, never from an untrusted prompt.
- Apply authorization-compatible metadata filters during candidate retrieval and re-check access before context assembly.
- Test cross-tenant negatives, cache keys, filter fallbacks, and index synchronization so missing metadata fails closed.

**Follow-up probe:** What can leak if permission filtering happens only after top-K retrieval?

**Revision links:** [Embeddings and vector search]({{ '/interview-prep/cheat-sheets/embeddings-vector-search/' | relative_url }}) · [RAG security and production]({{ '/interview-prep/cheat-sheets/rag-evaluation-security-production/' | relative_url }})

### AIE-B3-05 — Choose between a bi-encoder, cross-encoder, and late-interaction retriever.

**Round:** Retrieval architecture · **Depth:** Advanced

**Strong answer signals**

- Use a bi-encoder for scalable first-stage retrieval because queries and documents are encoded independently.
- Use a cross-encoder to rerank a small candidate set when quality justifies added latency and cost.
- Consider late interaction when token-level matching quality matters, but include its larger index and operational complexity in the decision.

**Follow-up probe:** How would you choose the candidate count sent to an expensive cross-encoder?

**Revision links:** [Embeddings and vector search]({{ '/interview-prep/cheat-sheets/embeddings-vector-search/' | relative_url }})


## Batch 3 · Document ingestion, chunking, and indexing

### AIE-B3-06 — Design an idempotent ingestion pipeline for files that can be retried, updated, or deleted.

**Round:** Ingestion reliability · **Depth:** Advanced

**Strong answer signals**

- Separate source discovery, parsing, canonicalization, chunking, embedding, indexing, and publication with explicit stage contracts.
- Use deterministic document and chunk IDs plus content, parser, chunker, and embedding versions so retries converge.
- Handle tombstones and replacement atomically, quarantine failed documents, and expose replay plus reconciliation tooling.

**Follow-up probe:** How would you prevent a partial re-index from leaving both old and new chunks searchable?

**Revision links:** [Ingestion, chunking, and indexing]({{ '/interview-prep/cheat-sheets/document-ingestion-chunking-indexing/' | relative_url }})

### AIE-B3-07 — Choose a chunking strategy for manuals containing headings, tables, code, and cross-references.

**Round:** Chunking design · **Depth:** Applied

**Strong answer signals**

- Preserve structural units and metadata instead of applying one blind character window to every element.
- Use token-aware limits, modest overlap only where continuity needs it, and parent-child or neighbor expansion for wider context.
- Treat tables and code as typed content with appropriate representations, then validate retrieval and citation quality by content type.

**Follow-up probe:** What failure would excessive overlap create during retrieval and generation?

**Revision links:** [Ingestion, chunking, and indexing]({{ '/interview-prep/cheat-sheets/document-ingestion-chunking-indexing/' | relative_url }})

### AIE-B3-08 — How do you preserve provenance precise enough for trustworthy citations?

**Round:** Provenance · **Depth:** Applied

**Strong answer signals**

- Keep immutable source identity, version, URI, page or section coordinates, element type, and parser lineage in the canonical model.
- Carry provenance from source elements into chunks and through reranking and context assembly without reconstructing it from generated text.
- Validate that displayed citations resolve to the exact indexed version and fail visibly when coordinates are unavailable.

**Follow-up probe:** Why is a document-level URL alone insufficient for audited answers?

**Revision links:** [Ingestion, chunking, and indexing]({{ '/interview-prep/cheat-sheets/document-ingestion-chunking-indexing/' | relative_url }}) · [RAG architecture]({{ '/interview-prep/cheat-sheets/rag-architecture-retrieval-generation/' | relative_url }})

### AIE-B3-09 — An OCR parser silently drops tables from some PDFs. How should the pipeline respond?

**Round:** Data-quality incident · **Depth:** Advanced

**Strong answer signals**

- Add extraction-quality signals such as page coverage, element counts, empty-page checks, table expectations, and parser warnings.
- Quarantine or route low-confidence documents to a fallback parser or human review instead of publishing incomplete content.
- Version parser outputs, retain samples and diagnostics, and reprocess affected documents after a verified fix.

**Follow-up probe:** Which checks would distinguish a genuinely blank page from a parser failure?

**Revision links:** [Ingestion, chunking, and indexing]({{ '/interview-prep/cheat-sheets/document-ingestion-chunking-indexing/' | relative_url }})

### AIE-B3-10 — Plan an embedding and index backfill without disrupting online retrieval.

**Round:** Index migration · **Depth:** Advanced

**Strong answer signals**

- Build a versioned shadow index from a fixed source snapshot while incremental changes are captured for replay.
- Compare document counts, deletion state, retrieval metrics, latency, and permission behavior before a controlled traffic shift.
- Switch through an alias or routing layer, monitor the new version, and retain the old index for bounded rollback.

**Follow-up probe:** How do you close the change gap between the backfill snapshot and cutover?

**Revision links:** [Ingestion, chunking, and indexing]({{ '/interview-prep/cheat-sheets/document-ingestion-chunking-indexing/' | relative_url }})


## Batch 3 · RAG architecture, retrieval, and generation

### AIE-B3-11 — Walk through a production RAG request from authenticated input to cited answer.

**Round:** System design · **Depth:** Advanced

**Strong answer signals**

- Validate the request and trusted scope, transform the query deliberately, retrieve candidates, apply authorization, fuse or rerank, and assemble bounded context.
- Generate with instructions that distinguish untrusted evidence from system policy, then validate answerability, citations, and structured output.
- Emit traceable stage metrics and identities while keeping raw sensitive content out of routine logs.

**Follow-up probe:** At which boundaries would you add timeouts, fallbacks, and circuit breakers?

**Revision links:** [RAG architecture]({{ '/interview-prep/cheat-sheets/rag-architecture-retrieval-generation/' | relative_url }})

### AIE-B3-12 — Explain `fetch_k`, reranking depth, and final `top_k` as separate controls.

**Round:** Retrieval pipeline · **Depth:** Applied

**Strong answer signals**

- `fetch_k` controls first-stage candidate breadth and therefore the ceiling for downstream recall.
- Reranking depth bounds the expensive scorer's work, while final `top_k` controls evidence volume sent to context assembly.
- Tune all three against retrieval recall, reranker gains, latency, token budget, and duplicate concentration.

**Follow-up probe:** Why can increasing final `top_k` reduce answer quality even when recall rises?

**Revision links:** [RAG architecture]({{ '/interview-prep/cheat-sheets/rag-architecture-retrieval-generation/' | relative_url }})

### AIE-B3-13 — Build context under a strict token budget without losing critical evidence.

**Round:** Context engineering · **Depth:** Advanced

**Strong answer signals**

- Allocate explicit budgets for instructions, user input, conversation state, evidence, and output rather than truncating at the end.
- Deduplicate, diversify, order, and compress evidence while preserving claim-bearing text and provenance.
- Prefer relevance-aware selection, parent or neighbor expansion when justified, and deterministic overflow behavior with observability.

**Follow-up probe:** How would you detect that context compression is removing qualifiers or exceptions?

**Revision links:** [RAG architecture]({{ '/interview-prep/cheat-sheets/rag-architecture-retrieval-generation/' | relative_url }})

### AIE-B3-14 — Design conversation-aware RAG without letting stale history corrupt retrieval.

**Round:** Conversational RAG · **Depth:** Advanced

**Strong answer signals**

- Separate durable user facts, recent dialogue, and retrieval query state; do not concatenate the entire transcript blindly.
- Rewrite follow-up queries with explicit references while retaining the original query for audit and fallback.
- Apply privacy, tenant, expiry, and correction rules to memory, and evaluate pronouns, topic shifts, and adversarial history.

**Follow-up probe:** When should a query rewrite be rejected in favor of the user's original wording?

**Revision links:** [RAG architecture]({{ '/interview-prep/cheat-sheets/rag-architecture-retrieval-generation/' | relative_url }})

### AIE-B3-15 — How do you make a RAG system abstain and cite evidence reliably?

**Round:** Grounded generation · **Depth:** Advanced

**Strong answer signals**

- Define answerability from evidence sufficiency, not model confidence alone, and provide a clear no-answer contract.
- Require claims to map to retrieved source identifiers and validate that citations support the nearby text.
- Calibrate thresholds on answerable and unanswerable cases, measure false answers and false abstentions, and preserve escalation paths.

**Follow-up probe:** What should happen when retrieved passages disagree with one another?

**Revision links:** [RAG architecture]({{ '/interview-prep/cheat-sheets/rag-architecture-retrieval-generation/' | relative_url }}) · [RAG evaluation]({{ '/interview-prep/cheat-sheets/rag-evaluation-security-production/' | relative_url }})


## Batch 3 · RAG evaluation, security, and production

### AIE-B3-16 — Design component and end-to-end evaluation for a RAG release.

**Round:** Evaluation design · **Depth:** Advanced

**Strong answer signals**

- Use a versioned dataset with answerable, unanswerable, permission-sensitive, multilingual, long-tail, and adversarial slices.
- Measure retrieval independently with recall, ranking, and filter correctness, then measure groundedness, answer relevance, citations, abstention, latency, and cost.
- Run controlled ablations so a system-level change can be traced to retrieval, context, prompt, model, or policy.

**Follow-up probe:** Why can a strong end-to-end score hide a broken retriever?

**Revision links:** [RAG evaluation and production]({{ '/interview-prep/cheat-sheets/rag-evaluation-security-production/' | relative_url }})

### AIE-B3-17 — Defend a RAG pipeline against prompt injection inside retrieved documents.

**Round:** AI security · **Depth:** Advanced

**Strong answer signals**

- Treat retrieved content as untrusted data, clearly delimit it, and keep system policy and tool permissions outside its control.
- Use least-privilege tools, allowlisted actions, server-side authorization, output validation, and human confirmation for consequential operations.
- Test direct and indirect injection, data exfiltration, cross-tenant retrieval, malicious citations, and encoded payloads in release gates.

**Follow-up probe:** Why is an instruction such as “ignore retrieved commands” insufficient by itself?

**Revision links:** [RAG security and production]({{ '/interview-prep/cheat-sheets/rag-evaluation-security-production/' | relative_url }})

### AIE-B3-18 — Define observability and SLOs for a production RAG service.

**Round:** Operations · **Depth:** Advanced

**Strong answer signals**

- Track stage-level latency, errors, timeouts, candidate counts, empty retrieval, reranker behavior, token usage, cost, cache state, and dependency versions.
- Define user-facing availability and latency SLOs plus quality guardrails such as permission correctness, groundedness samples, and abstention health.
- Use privacy-safe traces with request, corpus, index, embedding, prompt, and model identities so incidents are reproducible.

**Follow-up probe:** Which leading indicators would warn of retrieval degradation before users report bad answers?

**Revision links:** [RAG security and production]({{ '/interview-prep/cheat-sheets/rag-evaluation-security-production/' | relative_url }})

### AIE-B3-19 — A new index is faster overall but fails one high-risk query slice. Do you release it?

**Round:** Release decision · **Depth:** Leadership

**Strong answer signals**

- Treat slice-specific permission, safety, or critical-answer regressions as release blockers even if averages improve.
- Confirm the regression with paired cases, inspect the affected pipeline stage, and define an explicit acceptance threshold with the owner.
- Use shadow or canary traffic only when exposure is safe, keep rollback immediate, and document the decision and residual risk.

**Follow-up probe:** What evidence would justify a narrowly scoped exception rather than a full rollback?

**Revision links:** [RAG evaluation and production]({{ '/interview-prep/cheat-sheets/rag-evaluation-security-production/' | relative_url }})

### AIE-B3-20 — Retrieval quality drops after deployment while the generator is unchanged. Lead the incident response.

**Round:** Incident response · **Depth:** Leadership

**Strong answer signals**

- Stabilize service through rollback, degraded-mode search, or a safe abstention policy before deep diagnosis.
- Compare source freshness, ingestion lag, deletion state, embedding and index versions, filters, ANN settings, and query-transform changes.
- Preserve traces and candidate sets, identify blast radius, communicate clearly, then add reconciliation and regression checks from the failure.

**Follow-up probe:** How would you distinguish corpus drift from an index-build defect?

**Revision links:** [Ingestion and indexing]({{ '/interview-prep/cheat-sheets/document-ingestion-chunking-indexing/' | relative_url }}) · [RAG security and production]({{ '/interview-prep/cheat-sheets/rag-evaluation-security-production/' | relative_url }})

## Completion evidence

- You can answer at least 16 of 20 questions in each batch without reading the signals first.
- Every answer includes one relevant metric, constraint, failure mode, or project example.
- You can compress an applied answer from two minutes to 45 seconds without losing the decision.
- You have recorded weak areas against the stable question IDs for later re-testing.
