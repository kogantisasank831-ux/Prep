---
layout: "week"
status: "approved"
version: "1.8.0"
last_reviewed: "2026-11-11"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "Agentic AI Engineer foundation interview bank"
description: "One hundred eighty guided questions for AI and Agentic AI engineering interviews."
summary: "Practise production AI and agents alongside numerical and optimization reliability, unsupervised systems, rare-event operations, model assurance, security, monitoring, and incident leadership."
permalink: "/interview-prep/roles/agentic-ai-engineer/"
kicker_primary: "Agentic AI Engineer"
kicker_secondary: "Batches 1–9 · 180 guided questions"
current_label: "Role bank"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
question_count: 180
---
## How to use this bank

These are interview-practice prompts, not a scored learning assessment. Answer aloud before opening the revision links. A strong response should state assumptions, make a decision, explain trade-offs, and identify evidence or failure modes. Use the follow-up probe to test whether the answer survives a deeper round.

### Suggested practice loop

1. Select five questions from different sections.
2. Give a 90-second answer without notes.
3. Compare your answer with the strong-answer signals.
4. Open only the revision sheet needed for the gap.
5. Repeat the answer in 45 seconds, then record one concrete project example.

**Bank size:** 180 questions across Batches 1–9 · **Status:** Batches 1–9 approved

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

## Agent design and workflow patterns

### AIE-B4-01 — A support workflow has fixed validation and approval rules but one ambiguous triage step. Would you build an agent?

**Round:** Architecture · **Depth:** Applied

**Strong answer signals**

- Keep validation, approval, and side effects in deterministic code; use bounded model judgment only for ambiguous triage.
- Define allowed routes, confidence or abstention behavior, budgets, and a deterministic fallback before adding autonomy.
- Compare the hybrid design with a rules or classifier baseline on quality, latency, cost, and recoverability.

**Follow-up probe:** What evidence would justify expanding the model's control over later steps?

**Revision links:** [Agent fundamentals]({{ '/interview-prep/cheat-sheets/agent-fundamentals-workflow-patterns/' | relative_url }})

### AIE-B4-02 — Design a production-grade tool contract for an agent that can create a purchase request.

**Round:** Tool engineering · **Depth:** Advanced

**Strong answer signals**

- Use a narrow typed schema with semantic field descriptions, validation, explicit errors, and a stable version.
- Enforce identity, authorization, amount limits, idempotency keys, timeouts, audit records, and dry-run or approval modes outside the model.
- Return bounded structured results that distinguish validation, policy, transient, and terminal failures.

**Follow-up probe:** How do you prevent a retry from creating the request twice?

**Revision links:** [Agent fundamentals]({{ '/interview-prep/cheat-sheets/agent-fundamentals-workflow-patterns/' | relative_url }}) · [Protocols and reliability]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }})

### AIE-B4-03 — Separate execution state, short-term memory, and long-term memory for a troubleshooting agent.

**Round:** State and memory · **Depth:** Applied

**Strong answer signals**

- Keep current plan, observations, budgets, and tool outputs in execution state; scope conversation memory to the thread.
- Store only useful, consented, attributable facts across sessions with ownership, retention, correction, and deletion controls.
- Retrieve long-term memory selectively and treat it as untrusted, stale evidence rather than authoritative instruction.

**Follow-up probe:** Which data should never be promoted automatically into long-term memory?

**Revision links:** [Agent fundamentals]({{ '/interview-prep/cheat-sheets/agent-fundamentals-workflow-patterns/' | relative_url }})

### AIE-B4-04 — A team proposes five specialist agents for a task currently handled by one prompt. Review the design.

**Round:** Multi-agent design · **Depth:** Advanced

**Strong answer signals**

- Ask which specialists require distinct tools, policies, context, ownership, or deployment boundaries; task decomposition alone is insufficient.
- Compare a single agent with tools, a deterministic pipeline, and agents-as-tools before accepting peer coordination.
- Require explicit handoff contracts, termination rules, shared-state ownership, traceability, and an ablation showing net benefit.

**Follow-up probe:** What failure modes appear only after introducing agent-to-agent handoffs?

**Revision links:** [Agent fundamentals]({{ '/interview-prep/cheat-sheets/agent-fundamentals-workflow-patterns/' | relative_url }})

### AIE-B4-05 — Bound an iterative research agent so it cannot loop or spend indefinitely.

**Round:** Reliability · **Depth:** Applied

**Strong answer signals**

- Set step, wall-clock, token, cost, tool-call, and repeated-action limits with a clear stop reason.
- Detect no-progress cycles from repeated states or calls, require evidence before continuing, and preserve partial results.
- Route exhausted or consequential cases to safe abstention, clarification, or human review rather than silently returning a guess.

**Follow-up probe:** How would you choose budgets without truncating legitimate difficult cases?

**Revision links:** [Agent fundamentals]({{ '/interview-prep/cheat-sheets/agent-fundamentals-workflow-patterns/' | relative_url }}) · [Protocols and reliability]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }})

## LangGraph implementation and recovery

### AIE-B4-06 — Design typed LangGraph state for parallel researchers that contribute evidence to one answer.

**Round:** LangGraph state · **Depth:** Advanced

**Strong answer signals**

- Separate immutable request context from evolving evidence, errors, budgets, and final decision fields.
- Give concurrently updated collections an explicit associative reducer and avoid ambiguous last-write-wins behavior.
- Keep large documents outside checkpoints and carry stable references plus provenance instead.

**Follow-up probe:** What can go wrong if two workers update a field with no reducer?

**Revision links:** [LangGraph deep dive]({{ '/interview-prep/cheat-sheets/langgraph-deep-dive/' | relative_url }})

### AIE-B4-07 — Explain checkpointers, stores, and `thread_id` without treating them as the same persistence mechanism.

**Round:** LangGraph persistence · **Depth:** Applied

**Strong answer signals**

- A checkpointer persists graph execution state for a thread at boundaries; a store holds application-defined data across threads.
- `thread_id` identifies an execution or conversation and is neither user identity nor an authorization boundary.
- Choose durable backends, namespace by tenant and user, encrypt sensitive data, and define retention and deletion.

**Follow-up probe:** How would you resume a thread safely after the user's permissions changed?

**Revision links:** [LangGraph deep dive]({{ '/interview-prep/cheat-sheets/langgraph-deep-dive/' | relative_url }})

### AIE-B4-08 — Place a human approval interrupt before a payment tool and make resumption safe.

**Round:** Human in the loop · **Depth:** Advanced

**Strong answer signals**

- Persist the proposed action and approval context, then interrupt before the irreversible side effect.
- Expect the interrupted node to restart; move side effects after approval or make preceding work deterministic and idempotent.
- Bind approval to the exact operation, amount, actor, expiry, and policy version; revalidate authorization on resume.

**Follow-up probe:** What if the payment amount changes while the graph is paused?

**Revision links:** [LangGraph deep dive]({{ '/interview-prep/cheat-sheets/langgraph-deep-dive/' | relative_url }}) · [Protocols and reliability]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }})

### AIE-B4-09 — When would you use conditional edges, `Command`, and `Send` in the same graph?

**Round:** LangGraph control flow · **Depth:** Advanced

**Strong answer signals**

- Use conditional edges for explicit routing from state, and `Command` when a node must combine an update with its next route.
- Use `Send` for dynamic fan-out with worker-specific input, then merge results through a defined reducer.
- Bound fan-out, preserve ordering only when required, and handle partial worker failures and cancellation.

**Follow-up probe:** How would you prevent one failed worker from discarding all successful evidence?

**Revision links:** [LangGraph deep dive]({{ '/interview-prep/cheat-sheets/langgraph-deep-dive/' | relative_url }})

### AIE-B4-10 — Test a resumable LangGraph workflow that calls nondeterministic models and external tools.

**Round:** Testing · **Depth:** Advanced

**Strong answer signals**

- Unit-test nodes and routing with deterministic fixtures, typed state assertions, and controlled model or tool doubles.
- Add integration tests for checkpoint, interrupt, resume, replay, duplicate delivery, timeout, and partial-failure paths.
- Assert trajectory invariants and side-effect counts, then keep a small end-to-end suite against real dependencies.

**Follow-up probe:** Which assertion proves that replay did not duplicate an external action?

**Revision links:** [LangGraph deep dive]({{ '/interview-prep/cheat-sheets/langgraph-deep-dive/' | relative_url }}) · [Protocols and reliability]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }})

## Framework and library decisions

### AIE-B4-11 — Select a framework for a stateful, resumable agent with branching, approvals, and long-running tools.

**Round:** Framework selection · **Depth:** Applied

**Strong answer signals**

- Translate requirements into control flow, persistence, HITL, streaming, deployment, evaluation, and observability criteria.
- Favor explicit graph orchestration such as LangGraph when cycles, durable state, and recovery must be visible and testable.
- Validate the choice with a thin spike covering the hardest failure path, not a happy-path feature checklist.

**Follow-up probe:** When would a simple SDK plus task queue be the better choice?

**Revision links:** [Framework comparison]({{ '/interview-prep/cheat-sheets/agent-frameworks-libraries-comparison/' | relative_url }})

### AIE-B4-12 — Keep an agent application portable while using one framework deeply.

**Round:** Software design · **Depth:** Advanced

**Strong answer signals**

- Put domain state, tool interfaces, policies, and acceptance tests behind application-owned typed boundaries.
- Isolate framework messages, checkpoints, callbacks, and tracing in adapters rather than leaking them through business logic.
- Pin versions, record serialized-state compatibility, and prove migration with contract tests and replayable cases.

**Follow-up probe:** Which framework coupling is reasonable to accept rather than abstract prematurely?

**Revision links:** [Framework comparison]({{ '/interview-prep/cheat-sheets/agent-frameworks-libraries-comparison/' | relative_url }})

### AIE-B4-13 — Compare Google ADK, OpenAI Agents SDK, and PydanticAI for a typed Python service.

**Round:** Framework comparison · **Depth:** Advanced

**Strong answer signals**

- Compare required agent loop, workflow agents, sessions, callbacks, handoffs, guardrails, tracing, dependency injection, and deployment fit.
- Consider provider and cloud constraints, team skill, testing surface, maturity, and how much orchestration the application actually needs.
- Run the same representative tool, structured-output, and failure-recovery scenario before choosing.

**Follow-up probe:** Why is counting built-in integrations a weak selection method?

**Revision links:** [Framework comparison]({{ '/interview-prep/cheat-sheets/agent-frameworks-libraries-comparison/' | relative_url }})

### AIE-B4-14 — Choose between an agent framework and LlamaIndex or Haystack for a retrieval-heavy product.

**Round:** Architecture · **Depth:** Applied

**Strong answer signals**

- Identify whether ingestion, indexing, retrieval, and evidence pipelines or autonomous control flow dominate the problem.
- Use a retrieval framework for data-centric pipelines and add minimal orchestration only where dynamic decisions are needed.
- Avoid duplicating state, tracing, retries, and evaluation across overlapping frameworks; define one owner per concern.

**Follow-up probe:** What signal would show that a retrieval pipeline has outgrown deterministic orchestration?

**Revision links:** [Framework comparison]({{ '/interview-prep/cheat-sheets/agent-frameworks-libraries-comparison/' | relative_url }})

### AIE-B4-15 — A proposal says “use Nemotron as the agent framework with NeMo for everything.” Correct the architecture.

**Round:** NVIDIA ecosystem · **Depth:** Applied

**Strong answer signals**

- Clarify that Nemotron is a model family, while NeMo Framework, Guardrails, NIM, and other NVIDIA products address different layers.
- Map each actual requirement to model, serving, orchestration, guardrail, evaluation, and infrastructure components.
- Select only necessary layers and retain standard interfaces so model serving and orchestration can evolve independently.

**Follow-up probe:** Which experiment would determine whether a Nemotron model is suitable for the target tools?

**Revision links:** [Framework comparison]({{ '/interview-prep/cheat-sheets/agent-frameworks-libraries-comparison/' | relative_url }})

## Protocols, reliability, and evaluation

### AIE-B4-16 — Choose MCP, A2A, or a normal service API for three agent-system boundaries.

**Round:** Protocol design · **Depth:** Advanced

**Strong answer signals**

- Use MCP for capability discovery and invocation, A2A for independently deployed agent collaboration, and HTTP/gRPC for stable known services.
- Keep in-process calls typed and local unless deployment, reuse, or trust boundaries justify a network protocol.
- Define identity, authorization, versioning, timeouts, error semantics, and observability beyond the protocol's wire format.

**Follow-up probe:** When can an MCP server safely wrap an existing OpenAPI service?

**Revision links:** [Protocols and reliability]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }})

### AIE-B4-17 — Secure an agent that calls a remote MCP server on behalf of multiple tenants.

**Round:** Security · **Depth:** Advanced

**Strong answer signals**

- Authenticate workload and user context, authorize every capability and resource, and never treat `thread_id` as identity.
- Apply least privilege, tenant-scoped credentials, egress controls, schema validation, output limits, and auditable policy decisions.
- Treat tool descriptions and results as untrusted prompt-injection inputs; prevent them from changing higher-priority policy.

**Follow-up probe:** How would you detect cross-tenant leakage in testing and production?

**Revision links:** [Protocols and reliability]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }})

### AIE-B4-18 — Design retries for a remote tool that sometimes times out after completing its side effect.

**Round:** Distributed reliability · **Depth:** Advanced

**Strong answer signals**

- Use a stable operation or idempotency key and a status-reconciliation endpoint before repeating an ambiguous request.
- Retry only classified transient failures within a deadline using bounded exponential backoff and jitter.
- Persist intent and outcome, deduplicate server-side, and define compensation or human recovery for non-idempotent actions.

**Follow-up probe:** Why can “exactly once” not be guaranteed by the agent runtime alone?

**Revision links:** [Protocols and reliability]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }})

### AIE-B4-19 — Build an evaluation suite for a tool-using agent beyond final-answer accuracy.

**Round:** Agent evaluation · **Depth:** Advanced

**Strong answer signals**

- Score task success plus tool selection, argument correctness, evidence use, handoffs, recovery, stop behavior, safety, latency, and cost.
- Use versioned realistic, edge, adversarial, and fault-injection cases with deterministic checks where possible.
- Calibrate model judges against human labels and inspect trajectory-level failures rather than hiding them in one aggregate score.

**Follow-up probe:** Which metric would reveal a correct answer reached through an unsafe tool call?

**Revision links:** [Protocols and reliability]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }})

### AIE-B4-20 — A downstream agent service is slow and failing intermittently. Stabilize the caller.

**Round:** Incident response · **Depth:** Leadership

**Strong answer signals**

- Enforce deadlines, bounded concurrency, backpressure, rate limits, and a circuit breaker; cancel work that no longer benefits the user.
- Use a safe fallback, partial response, queue, or explicit degradation based on request risk and freshness needs.
- Trace attempts and dependency versions, distinguish saturation from functional errors, and recover gradually through probes or canaries.

**Follow-up probe:** What measurements tell you whether retries are amplifying the outage?

**Revision links:** [Protocols and reliability]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }})

## AI/ML system design and production architecture

### AIE-B5-01 — Design an AI support assistant without starting from a model or framework.

**Round:** System design · **Depth:** Applied

**Strong answer signals**

- Clarify users, decisions, scope, risk, traffic, latency, freshness, quality, cost, and non-goals before drawing components.
- Define business, task-quality, safety, service, and efficiency metrics plus a simple baseline and fallback.
- Separate offline/control and online/data planes, identify sources of truth, and close with validation, rollout, monitoring, and rollback.

**Follow-up probe:** Which assumption would you validate first with a small production-like experiment?

**Revision links:** [AI/ML system design]({{ '/interview-prep/cheat-sheets/ai-ml-system-design-production-architecture/' | relative_url }})

### AIE-B5-02 — Design a multi-tenant AI gateway that routes to self-hosted and managed models.

**Round:** Architecture · **Depth:** Advanced

**Strong answer signals**

- Authenticate users and workloads, authorize model/data/tool access server-side, and isolate tenant quotas, caches, indexes, traces, and budgets.
- Route by capability, risk, residency, load, quality tier, and cost with bounded queues, deadlines, cancellation, and safe fallbacks.
- Preserve resolved model, prompt, index, policy, and cohort lineage; validate every route with contract, quality, load, and security tests.

**Follow-up probe:** How would you prevent a low-cost fallback from violating a tenant's quality or residency contract?

**Revision links:** [AI/ML system design]({{ '/interview-prep/cheat-sheets/ai-ml-system-design-production-architecture/' | relative_url }})

### AIE-B5-03 — Define the API and state machine for a long-running agent job.

**Round:** API design · **Depth:** Advanced

**Strong answer signals**

- Use versioned request/response schemas, principal and tenant context, correlation and idempotency keys, deadlines, cancellation, and stable errors.
- Expose explicit pending, running, waiting, succeeded, failed, cancelled, and expired states with polling or webhook semantics.
- Distinguish request acceptance from business success and reconcile partial tool side effects before declaring a terminal result.

**Follow-up probe:** What should a repeated submission with the same idempotency key return?

**Revision links:** [AI/ML system design]({{ '/interview-prep/cheat-sheets/ai-ml-system-design-production-architecture/' | relative_url }})

### AIE-B5-04 — Choose sources of truth and rebuild paths for a RAG and agent service.

**Round:** Data architecture · **Depth:** Advanced

**Strong answer signals**

- Keep authoritative documents, permissions, transactional state, and operation outcomes separate from derived indexes, caches, embeddings, and memory.
- Version derivations and propagate updates, revocations, and deletions with reconciliation and completeness checks.
- Define atomic publication, fallback to a last-known-good version, and tested rebuild or disaster-recovery procedures.

**Follow-up probe:** Why should a vector index normally not be the authoritative document store?

**Revision links:** [AI/ML system design]({{ '/interview-prep/cheat-sheets/ai-ml-system-design-production-architecture/' | relative_url }})

### AIE-B5-05 — Design graceful degradation when retrieval, a model provider, or an agent tool fails.

**Round:** Reliability design · **Depth:** Advanced

**Strong answer signals**

- Classify dependency failure and choose a tested reduced-capability path such as cached, retrieval-only, queued, smaller-model, abstention, or human escalation.
- Preserve authorization, schema, minimum quality, and user expectations; do not retry unsafe or expired work.
- Add deadlines, circuit breakers, bulkheads, bounded queues, monitoring, and exact rollback or kill-switch ownership.

**Follow-up probe:** When is returning no answer safer than using a technically available fallback?

**Revision links:** [AI/ML system design]({{ '/interview-prep/cheat-sheets/ai-ml-system-design-production-architecture/' | relative_url }})

## LLM inference and serving optimization

### AIE-B5-06 — Diagnose high end-to-end latency when GPU utilization looks healthy.

**Round:** Performance diagnosis · **Depth:** Advanced

**Strong answer signals**

- Decompose admission, queue, tokenization, prefill, decode, post-processing, tools, and delivery with p50/p95/p99 by request class.
- Compare TTFT, TPOT, token backlog, active sequences, KV pressure, preemption, rejection, and goodput rather than GPU utilization alone.
- Reproduce the production arrival and token-length distributions before changing scheduler or batch settings.

**Follow-up probe:** What evidence distinguishes queue-bound latency from slow decode?

**Revision links:** [LLM inference optimization]({{ '/interview-prep/cheat-sheets/llm-inference-serving-optimization/' | relative_url }})

### AIE-B5-07 — Estimate whether a model and target concurrency fit on the available GPUs.

**Round:** Capacity estimation · **Depth:** Advanced

**Strong answer signals**

- Estimate raw weight memory from parameters and precision, then add quantization metadata, runtime, activations, workspaces, adapters, fragmentation, and margin.
- Estimate KV cache from layers, KV heads, head dimension, element bytes, and total cached tokens, accounting for GQA/MQA and sharding.
- Treat calculations as feasibility bounds and confirm mixed-length concurrency, OOM, preemption, latency, and goodput under load.

**Follow-up probe:** Why does fitting raw FP16 weights into VRAM not prove the server can run safely?

**Revision links:** [LLM inference optimization]({{ '/interview-prep/cheat-sheets/llm-inference-serving-optimization/' | relative_url }})

### AIE-B5-08 — Tune continuous batching and chunked prefill for mixed short and long prompts.

**Round:** Serving optimization · **Depth:** Advanced

**Strong answer signals**

- Sweep concurrent-sequence, batched-token, prefill-chunk, queue, and scheduling limits against TTFT, TPOT, throughput, rejection, and goodput.
- Prevent long prefills from starving interactive decode through chunking, priority or traffic segmentation, and fairness controls.
- Record engine/model/hardware/workload identity and retain OOM, timeout, and cancellation results rather than benchmarking only survivors.

**Follow-up probe:** Why can a larger token batch improve throughput while worsening user experience?

**Revision links:** [LLM inference optimization]({{ '/interview-prep/cheat-sheets/llm-inference-serving-optimization/' | relative_url }})

### AIE-B5-09 — Add prefix caching to a multi-tenant LLM service safely.

**Round:** Cache engineering · **Depth:** Advanced

**Strong answer signals**

- Confirm repeated stable token prefixes and key by exact model, tokenizer, template, adapters, precision, and token sequence.
- Isolate tenants and permissions, define TTL, invalidation, memory and eviction, and prevent sensitive prefix reuse across trust boundaries.
- Measure hit rate, saved prefill, memory pressure, latency, quality, and behavior after version changes; disable it if overhead exceeds benefit.

**Follow-up probe:** Which apparently identical prompts can still require different cache keys?

**Revision links:** [LLM inference optimization]({{ '/interview-prep/cheat-sheets/llm-inference-serving-optimization/' | relative_url }})

### AIE-B5-10 — Compare vLLM, SGLang, TensorRT-LLM, and a local runtime for one production workload.

**Round:** Engine selection · **Depth:** Advanced

**Strong answer signals**

- Freeze model revision, tokenizer/template, precision, hardware, generation settings, workload, API contract, and quality set.
- Test warm and cold behavior, request-rate and concurrency sweeps, TTFT/TPOT/goodput, memory, stability, tool/schema behavior, and cost.
- Include operational fit such as distributed topology, autoscaling, metrics, drain, upgrades, support, and rollback—not kernel speed alone.

**Follow-up probe:** Why does OpenAI-compatible API support not establish behavioral compatibility?

**Revision links:** [LLM inference optimization]({{ '/interview-prep/cheat-sheets/llm-inference-serving-optimization/' | relative_url }})

## MLOps, LLMOps, deployment, and lifecycle

### AIE-B5-11 — Define an immutable release manifest for a RAG and agent application.

**Round:** Release engineering · **Depth:** Advanced

**Strong answer signals**

- Bind source and image digests, model/tokenizer/adapters, prompts/schema, corpus/index/reranker, graph/tools/policies, runtime config, and evaluation suite.
- Use immutable identifiers with signed provenance or SBOM where applicable; never place secret values in the manifest.
- Resolve aliases at runtime, attach the exact manifest to traces and cohorts, and retain the prior compatible rollback bundle.

**Follow-up probe:** Which behavior-changing artifact is most commonly omitted from GenAI release identity?

**Revision links:** [MLOps and LLMOps]({{ '/interview-prep/cheat-sheets/mlops-llmops-deployment-lifecycle/' | relative_url }})

### AIE-B5-12 — Build the lifecycle for RAG indexes and agent tools.

**Round:** LLMOps · **Depth:** Advanced

**Strong answer signals**

- Version source manifest, permissions, extraction, chunking, embeddings, index, reranker, graph, tool contracts, and downstream capability versions.
- Build candidates in stages with completeness, ACL/deletion, retrieval, trajectory, and side-effect tests before atomic promotion.
- Canary exact bundles, retain rollback and active-thread compatibility, and clean old artifacts only after retention and caller checks.

**Follow-up probe:** How can changing only a tool description cause a production regression?

**Revision links:** [MLOps and LLMOps]({{ '/interview-prep/cheat-sheets/mlops-llmops-deployment-lifecycle/' | relative_url }})

### AIE-B5-13 — Design CI/CD gates for an AI service.

**Round:** Delivery pipeline · **Depth:** Advanced

**Strong answer signals**

- Run lint, types, unit, data, contract, integration, model/GenAI evaluation, security, load, recovery, and packaging checks proportionate to risk.
- Promote the exact tested image and release manifest; continuous training may create a candidate but must not authorize production automatically.
- Use shadow or canary, explicit abort thresholds, fast rollback, post-release smoke, and evidence tied to the deployed cohort.

**Follow-up probe:** Which deterministic checks should run before expensive LLM-judge evaluation?

**Revision links:** [MLOps and LLMOps]({{ '/interview-prep/cheat-sheets/mlops-llmops-deployment-lifecycle/' | relative_url }})

### AIE-B5-14 — Configure Kubernetes probes and shutdown for a slow-starting model server.

**Round:** Kubernetes operations · **Depth:** Applied

**Strong answer signals**

- Use startup to protect model loading or compilation, readiness only after the server is warmed enough for traffic, and liveness for unrecoverable process failure.
- Handle termination signals, stop admission, drain streams and in-flight work within a deadline, and preserve or cancel jobs deliberately.
- Set measured CPU/RAM/GPU requests, placement, disruption, cache, and autoscaling behavior; avoid restarting a merely busy server.

**Follow-up probe:** What failure occurs when liveness is used to police a long but healthy model load?

**Revision links:** [MLOps and LLMOps]({{ '/interview-prep/cheat-sheets/mlops-llmops-deployment-lifecycle/' | relative_url }})

### AIE-B5-15 — Roll back an AI release whose model is unchanged but prompt, index, and tool behavior regressed.

**Round:** Release recovery · **Depth:** Advanced

**Strong answer signals**

- Roll back the complete compatible bundle rather than only a model alias, including prompt, index, tools, policy, config, and feature flags.
- Account for state schemas, active jobs or threads, cache invalidation, irreversible effects, and database/index compatibility.
- Verify restored service, quality, permissions, and external-effect reconciliation, then preserve evidence and add regression coverage.

**Follow-up probe:** When can forward recovery be safer than rollback?

**Revision links:** [MLOps and LLMOps]({{ '/interview-prep/cheat-sheets/mlops-llmops-deployment-lifecycle/' | relative_url }})

## Production monitoring, cost, and capacity

### AIE-B5-16 — Design observability that can attribute a production regression to the exact AI release.

**Round:** Observability · **Depth:** Advanced

**Strong answer signals**

- Correlate gateway, retrieval, model, agent/tool, storage, and side-effect spans with privacy-safe request and operation identifiers.
- Attach code/image, model/tokenizer, prompt, index, graph, tool/policy, config, evaluator, and rollout-cohort identity.
- Monitor traffic, errors, latency stages, saturation, data freshness, task quality, safety, cost, and telemetry health by meaningful slices.

**Follow-up probe:** Which lineage fields let you distinguish a model regression from a prompt or index regression?

**Revision links:** [AI production operations]({{ '/interview-prep/cheat-sheets/ai-production-monitoring-cost-capacity/' | relative_url }})

### AIE-B5-17 — Monitor an agent whose workflow completes but external actions can remain uncertain.

**Round:** Agent operations · **Depth:** Advanced

**Strong answer signals**

- Track terminal outcome, steps, loops, budgets, routes, tool arguments, authorization, approvals, retries, checkpoints, and external operation IDs.
- Represent committed, failed, partial, and unknown side effects explicitly and reconcile ambiguous outcomes against authoritative systems.
- Alert on duplicate or unauthorized actions, budget exhaustion, repeated loops, rising unknown outcomes, and missing audit telemetry.

**Follow-up probe:** Why is a graph's `SUCCEEDED` state insufficient evidence that the business task succeeded?

**Revision links:** [AI production operations]({{ '/interview-prep/cheat-sheets/ai-production-monitoring-cost-capacity/' | relative_url }})

### AIE-B5-18 — Size and autoscale an LLM service from measured production-like benchmarks.

**Round:** Capacity planning · **Depth:** Advanced

**Strong answer signals**

- Measure safe per-replica goodput by input/output class under the latency and quality SLO, then apply peak, burst, failure-zone, and maintenance headroom.
- Scale on queue or token backlog, queue age/TTFT burn, active sequences, and KV pressure with warm floors, bounds, cooldown, and cluster capacity.
- Test cold start, image/model download, compilation, readiness, spike, soak, drain, failure, and downstream limits.

**Follow-up probe:** Why can scaling only on GPU utilization react too late?

**Revision links:** [AI production operations]({{ '/interview-prep/cheat-sheets/ai-production-monitoring-cost-capacity/' | relative_url }})

### AIE-B5-19 — Reduce AI serving cost without silently reducing accepted quality.

**Round:** FinOps · **Depth:** Applied

**Strong answer signals**

- Attribute provider tokens, GPU idle and active time, retrieval, tools, telemetry, evaluation, and operations to requests and successful outcomes.
- Compare smaller models, routing, context limits, caching, batching, quantization, cancellation, and scale-down on a quality-latency-cost frontier.
- Apply tenant/task budgets, quotas, anomaly alerts, and kill switches while retaining safety and availability gates.

**Follow-up probe:** Why can cost per request make a cheap but failing route look efficient?

**Revision links:** [AI production operations]({{ '/interview-prep/cheat-sheets/ai-production-monitoring-cost-capacity/' | relative_url }})

### AIE-B5-20 — Telemetry disappears while latency dashboards turn green. Lead the technical response.

**Round:** Incident response · **Depth:** Leadership

**Strong answer signals**

- Treat missing telemetry as unknown, verify heartbeats, volume, schema, delay, sampling, and trace completeness before trusting product metrics.
- Assess user and safety impact through independent signals, contain risky traffic if evidence is insufficient, and preserve exact release state.
- Restore the pipeline, backfill where valid, add no-data alerts and synthetic end-to-end checks, and verify responders can execute the runbook.

**Follow-up probe:** Which synthetic event proves that collection, alert routing, and responder recovery all work?

**Revision links:** [AI production operations]({{ '/interview-prep/cheat-sheets/ai-production-monitoring-cost-capacity/' | relative_url }})

## Data and distributed compute engineering

### AIE-B6-01 — Choose between DuckDB or Polars and Spark for a daily document-processing pipeline.

**Round:** Data architecture · **Depth:** Applied

**Strong answer signals**

- Start from data size and growth, file count, transformations, memory, freshness, replay, team skill, and operational constraints rather than choosing a cluster by default.
- Benchmark a representative slice including startup, remote reads, serialization, spill, retries, and cost; prefer the smallest system that meets the contract.
- Define the evidence that triggers distribution, such as sustained memory pressure, missed completion SLOs, unavoidable shuffle scale, or required fault-tolerant parallelism.

**Follow-up probe:** Why can a cluster make a 50 GB workload slower and less reliable?

**Revision links:** [Data and distributed compute]({{ '/interview-prep/cheat-sheets/data-distributed-compute-engineering/' | relative_url }})

### AIE-B6-02 — Diagnose a Spark join where a few tasks run far longer than the rest.

**Round:** Distributed performance · **Depth:** Advanced

**Strong answer signals**

- Inspect the physical plan, key-frequency and partition-size distributions, task-time tails, shuffle bytes, spill, and maximum-to-median ratios before tuning.
- Reduce data before the shuffle, broadcast only a measured-small side, pre-aggregate, isolate or salt hot keys, and use adaptive execution when validated.
- Verify row counts and join semantics after mitigation, then control output partitioning and small files rather than optimizing time alone.

**Follow-up probe:** What correctness work does salting add after it spreads a hot key?

**Revision links:** [Data and distributed compute]({{ '/interview-prep/cheat-sheets/data-distributed-compute-engineering/' | relative_url }})

### AIE-B6-03 — Make a Kafka consumer that calls an external procurement API safe under retries.

**Round:** Streaming reliability · **Depth:** Advanced

**Strong answer signals**

- Define the observable business effect, key and partition ordering, offset boundary, stable operation ID, and behavior after a timeout with an unknown outcome.
- Persist intent and result, make the API idempotent or reconcile its authoritative status before retrying, and commit progress only after the accepted effect boundary.
- Inject failures before and after the API call and offset commit; prove duplicate delivery cannot create a duplicate procurement action.

**Follow-up probe:** Why does Kafka exactly-once processing not make an arbitrary HTTP side effect exactly once?

**Revision links:** [Data and distributed compute]({{ '/interview-prep/cheat-sheets/data-distributed-compute-engineering/' | relative_url }})

### AIE-B6-04 — Design event-time fraud features that serve online and rebuild point-in-time-correct training data.

**Round:** Streaming architecture · **Depth:** Advanced

**Strong answer signals**

- Define event IDs, account keys, event time, ordering, duplicate and correction behavior, watermark, late-data policy, state TTL, freshness, and fallback.
- Keep immutable governed events, versioned stream logic, online features with freshness metadata, and offline history that supports point-in-time joins and replay.
- Reconcile online and offline values, isolate backfills, canary feature versions, and monitor lag, skew, checkpoint health, missing/stale features, and cost.

**Follow-up probe:** How would a record arriving after the watermark change an already served feature?

**Revision links:** [Data and distributed compute]({{ '/interview-prep/cheat-sheets/data-distributed-compute-engineering/' | relative_url }})

### AIE-B6-05 — Select DDP, FSDP, tensor, or pipeline parallelism for a model-training job.

**Round:** Distributed training · **Depth:** Advanced

**Strong answer signals**

- Estimate model, gradient, optimizer, activation, and batch memory first; use data parallelism when the model fits and sharding when replicated state does not.
- Introduce tensor or pipeline parallelism only when model scale requires it, accounting for collectives, topology, bubbles, stragglers, checkpoint format, and recovery.
- Hold global batch and optimizer policy deliberately, measure tokens per second and scaling efficiency, and prove reproducibility and resharding across worker changes.

**Follow-up probe:** Why can adding GPUs reduce throughput or change convergence?

**Revision links:** [Data and distributed compute]({{ '/interview-prep/cheat-sheets/data-distributed-compute-engineering/' | relative_url }})

## AI security, privacy, and governance

### AIE-B6-06 — Threat-model a multi-tenant procurement document agent before selecting guardrail libraries.

**Round:** Threat modeling · **Depth:** Advanced

**Strong answer signals**

- Bind users, tenants, documents, model/runtime, prompts, index, tools, credentials, external effects, assets, entry points, and trust boundaries.
- Identify confidentiality, integrity, authorization, poisoning, injection, SSRF, replay, approval, resource-abuse, and partial-effect scenarios with impact evidence.
- Assign deterministic controls, bounded test authority, synthetic canaries, owners, release gates, containment, rollback, and residual-risk acceptance.

**Follow-up probe:** Which threat would an OWASP checklist miss without the exact procurement workflow?

**Revision links:** [AI security, privacy, and governance]({{ '/interview-prep/cheat-sheets/ai-security-privacy-governance/' | relative_url }})

### AIE-B6-07 — Defend a tool-using agent against indirect prompt injection from retrieved documents.

**Round:** Agent security · **Depth:** Advanced

**Strong answer signals**

- Treat retrieved text as untrusted evidence, keep principal and tenant context outside model text, and never let document content grant tools or permissions.
- Expose narrow typed tools, validate semantics, reauthorize the exact resource and action, use scoped credentials and egress controls, and approve high-impact effects.
- Test malicious documents with bounded accounts and external-state assertions that distinguish unsafe text, attempted action, blocked action, and committed effect.

**Follow-up probe:** Why does a model refusal not prove that no tool action occurred?

**Revision links:** [AI security, privacy, and governance]({{ '/interview-prep/cheat-sheets/ai-security-privacy-governance/' | relative_url }})

### AIE-B6-08 — Enforce authorization, revocation, and deletion in a multi-tenant RAG service.

**Round:** RAG security · **Depth:** Advanced

**Strong answer signals**

- Bind trusted user and tenant identity before retrieval, store immutable source/ACL/version lineage, and isolate indexes, caches, embeddings, traces, and evaluation data.
- Recheck current permissions during candidate assembly, propagate revocation and deletion to derived stores, and fail closed when ACL or lineage state is stale.
- Add cross-tenant canaries, revoked-document cases, cache-key tests, enumeration limits, citation-support checks, and reconciliation for incomplete propagation.

**Follow-up probe:** How can a permission-aware vector filter still leak through a shared cache?

**Revision links:** [AI security, privacy, and governance]({{ '/interview-prep/cheat-sheets/ai-security-privacy-governance/' | relative_url }})

### AIE-B6-09 — Secure the model, tokenizer, adapter, container, and dataset supply chain.

**Round:** Supply-chain security · **Depth:** Advanced

**Strong answer signals**

- Record immutable provenance for code, lockfile, image, model bytes, tokenizer, adapters, datasets, prompts, tools, policies, runtime, and evaluation suite.
- Use trusted registries, digests or signatures, SBOM/model BOM, license and vulnerability review, safe formats, restricted deserialization, and isolated evaluation.
- Promote the exact tested bundle, monitor for changed artifacts, retain rollback, and define quarantine and credential-rotation actions for compromise.

**Follow-up probe:** Why is a familiar model repository name not proof that the loaded bytes are safe?

**Revision links:** [AI security, privacy, and governance]({{ '/interview-prep/cheat-sheets/ai-security-privacy-governance/' | relative_url }})

### AIE-B6-10 — Build a bounded red-team regression suite for an agent release.

**Round:** Adversarial testing · **Depth:** Advanced

**Strong answer signals**

- Cover direct and indirect injection, cross-tenant access, secrets/PII, tool arguments, SSRF, replay, approval confusion, loops, budget exhaustion, and poisoned retrieval.
- Give each case a synthetic canary, expected control, forbidden effect, deterministic oracle, rate and cost cap, cleanup, severity, and exact release identity.
- Use scanners and model judges as coverage aids, calibrate subjective labels, and gate releases on reproducible application-state evidence rather than pass counts alone.

**Follow-up probe:** Which oracle would prove that a malicious tool call was blocked before any external effect?

**Revision links:** [AI security, privacy, and governance]({{ '/interview-prep/cheat-sheets/ai-security-privacy-governance/' | relative_url }})

## Technical leadership and product thinking

### AIE-B6-11 — Reframe an executive request for a multi-agent assistant into a testable first release.

**Round:** Product framing · **Depth:** Leadership

**Strong answer signals**

- Identify the user, decision, baseline, pain, constraints, failure cost, measurable outcome, guardrails, and non-goals; multi-agent is not itself a requirement.
- Compare search, deterministic workflow, RAG, one bounded agent, vendor service, and human process before accepting extra autonomy.
- Propose one vertical slice with an evidence plan, stop/pivot criteria, owner, risk tier, human approval for writes, and a decision date.

**Follow-up probe:** What evidence would justify adding a second agent rather than another deterministic workflow step?

**Revision links:** [AI technical leadership and product thinking]({{ '/interview-prep/cheat-sheets/ai-technical-leadership-product-thinking/' | relative_url }})

### AIE-B6-12 — Lead a build-versus-buy-versus-self-host decision for model serving.

**Round:** Technical strategy · **Depth:** Leadership

**Strong answer signals**

- Compare quality and capability, privacy/residency, latency, demand shape, reliability, observability, support, team skill, delivery time, and exit requirements.
- Model total cost across usage, idle capacity, GPUs/cloud, staffing, security, upgrades, licenses, migration, and provider failure rather than price per token alone.
- Run a representative benchmark and risk review, document assumptions and triggers, preserve an interface and fallback, and assign lifecycle ownership.

**Follow-up probe:** At what utilization or risk threshold would you revisit the selected option?

**Revision links:** [AI technical leadership and product thinking]({{ '/interview-prep/cheat-sheets/ai-technical-leadership-product-thinking/' | relative_url }})

### AIE-B6-13 — Run an architecture decision for a public agent API and persistent state schema.

**Round:** Architecture leadership · **Depth:** Leadership

**Strong answer signals**

- Separate facts, assumptions, risks, and preferences; define contracts, scale, security, recovery, migration, observability, and supported version requirements.
- Treat the public API, identity boundary, state and retention model as high-reversal-cost choices; compare alternatives and require broader review and an exit path.
- Record the decision, dissent, owner, validation evidence, rollout and rollback, and explicit triggers that reopen it.

**Follow-up probe:** Which internal implementation choice could remain reversible behind that contract?

**Revision links:** [AI technical leadership and product thinking]({{ '/interview-prep/cheat-sheets/ai-technical-leadership-product-thinking/' | relative_url }})

### AIE-B6-14 — Delegate ownership of an agent evaluation subsystem without becoming the bottleneck.

**Round:** Delegation and mentoring · **Depth:** Leadership

**Strong answer signals**

- Delegate the outcome, scope, non-goals, interfaces, decision authority, evidence bar, dependencies, and escalation triggers—not only a task list.
- Provide representative scenarios and review checkpoints proportional to risk while leaving room for the owner to make and defend decisions.
- Measure success through independent ownership, reusable standards, release evidence, and improved team throughput; give specific artifact-based feedback.

**Follow-up probe:** Which decisions would you retain because their risk crosses the delegated boundary?

**Revision links:** [AI technical leadership and product thinking]({{ '/interview-prep/cheat-sheets/ai-technical-leadership-product-thinking/' | relative_url }})

### AIE-B6-15 — Lead an AI incident involving wrong actions, incomplete telemetry, and stakeholder pressure.

**Round:** Incident leadership · **Depth:** Leadership

**Strong answer signals**

- Protect users and data first, stop or narrow harmful effects, establish incident command and a source of truth, preserve exact release identity, and bound impact.
- Communicate known, unknown, decisions, risk, and next update; roll back, disable tools, or degrade safely while reconciling external actions.
- Verify recovery, run an evidence-based postmortem, and assign systemic actions for authorization, telemetry, release gates, runbooks, and later effectiveness checks.

**Follow-up probe:** How would you proceed when the business asks to restore service before action reconciliation is complete?

**Revision links:** [AI technical leadership and product thinking]({{ '/interview-prep/cheat-sheets/ai-technical-leadership-product-thinking/' | relative_url }})

## Project deep dives, behavioral answers, and mock interviews

### AIE-B6-16 — Give a two-minute defense of a production RAG or agent project.

**Round:** Project deep dive · **Depth:** Leadership

**Strong answer signals**

- Lead with the user decision, measured baseline, scale, constraints, why AI was justified, and the simplest viable architecture rather than a framework list.
- State your exact ownership and team contributions, then cover data, evaluation, permissions, failure handling, rollout, monitoring, cost, and operational status.
- Quantify the outcome with unit, population, window, comparator, attribution limits, and one trade-off or learning; label prototypes honestly.

**Follow-up probe:** Which artifact most clearly proves your personal contribution?

**Revision links:** [Project deep dive and mock interviews]({{ '/interview-prep/cheat-sheets/project-deep-dive-behavioral-mock-interview/' | relative_url }})

### AIE-B6-17 — Defend a claimed latency or cost improvement from an inference project.

**Round:** Impact evidence · **Depth:** Advanced

**Strong answer signals**

- State exact candidate, hardware, workload and token distributions, baseline, metric definitions, time window, traffic cohort, and quality acceptance gates.
- Separate queue, TTFT, TPOT, throughput, goodput, rejection, and cost per successful outcome; include warm/cold behavior and failures.
- Explain experiment or phased-rollout attribution, uncertainty and confounders, net operating cost, and whether results were projected, observed, or realized.

**Follow-up probe:** How could lower cost per request hide a worse production result?

**Revision links:** [Project deep dive and mock interviews]({{ '/interview-prep/cheat-sheets/project-deep-dive-behavioral-mock-interview/' | relative_url }})

### AIE-B6-18 — Tell a failure story about an agent that completed workflows incorrectly.

**Round:** Behavioral · **Depth:** Leadership

**Strong answer signals**

- Explain the missed assumption, affected users or external effects, detection gap, and your accountability without blaming the model, data, or another team.
- Describe containment, communication, exact-state preservation, root-mechanism investigation, action reconciliation, correction, and verification.
- Show the durable change to contracts, evaluation, approval, monitoring, or rollout and provide later evidence that the change worked.

**Follow-up probe:** What leading signal could have detected the failure before a user report?

**Revision links:** [Project deep dive and mock interviews]({{ '/interview-prep/cheat-sheets/project-deep-dive-behavioral-mock-interview/' | relative_url }})

### AIE-B6-19 — Describe a disagreement over graph orchestration versus a simpler workflow.

**Round:** Behavioral · **Depth:** Leadership

**Strong answer signals**

- Establish the shared outcome and each view's valid concern, then make state, recovery, latency, operability, team skill, and change criteria explicit.
- Gather the smallest discriminating evidence through a thin spike or failure-path test and route any residual consequential decision to the accountable owner.
- Explain the final decision, your exact influence, team commitment, outcome, and what evidence would trigger reconsideration without portraying peers as incompetent.

**Follow-up probe:** What did the other proposal reveal that improved your preferred design?

**Revision links:** [Project deep dive and mock interviews]({{ '/interview-prep/cheat-sheets/project-deep-dive-behavioral-mock-interview/' | relative_url }})

### AIE-B6-20 — Handle a mock design follow-up that increases LLM-gateway traffic and context size by 10×.

**Round:** Mock system design · **Depth:** Advanced

**Strong answer signals**

- Recalculate request and token distributions, queueing, prefill/decode capacity, KV memory, network, storage, provider limits, and failure headroom rather than scaling every box uniformly.
- Introduce admission, quotas, traffic classes, batching, caching, routing, model or context optimization, horizontal and parallel scaling only where measured bottlenecks require them.
- Preserve quality, tenancy, security, observability, rollback, and cost per accepted outcome; propose load, spike, soak, failure, and recovery gates.

**Follow-up probe:** Which measurement would determine whether more replicas or a shorter context policy is the better first move?

**Revision links:** [Project deep dive and mock interviews]({{ '/interview-prep/cheat-sheets/project-deep-dive-behavioral-mock-interview/' | relative_url }})

## Mathematical foundations and optimization

### AIE-B7-01 — Trace tensor shapes and compute through one multi-head attention block.

**Round:** Mathematical engineering · **Depth:** Applied

**Strong answer signals**

- Name batch, sequence, model, head-count and head-width axes; derive Q/K/V, attention-score, mask, weighted-value, concatenation and output shapes.
- Distinguish elementwise, batched matrix and broadcast operations; identify where an apparently valid mask shape could leak attention across positions or batches.
- Connect score-matrix size to quadratic sequence cost, then discuss grouped/multi-query attention, chunking or alternate attention only against the workload.

**Follow-up probe:** Which broadcasting mistake could pass runtime shape checks but apply one sequence's mask to every item?

**Revision links:** [Linear algebra, calculus, and optimization]({{ '/interview-prep/cheat-sheets/linear-algebra-calculus-optimization/' | relative_url }})

### AIE-B7-02 — Choose cosine, dot-product, or Euclidean similarity for an embedding service.

**Round:** Retrieval mathematics · **Depth:** Advanced

**Strong answer signals**

- Establish whether embedding magnitude carries meaning, how the model was trained, whether vectors are normalized, and which index metrics are supported.
- Explain that normalized vectors make cosine and dot-product ranking equivalent and relate squared Euclidean distance monotonically, while unnormalized vectors need not agree.
- Validate on labeled retrieval slices and operational constraints, version normalization with the index, and monitor norm and score-distribution drift.

**Follow-up probe:** What failure appears if documents are normalized at indexing but queries are not?

**Revision links:** [Linear algebra, calculus, and optimization]({{ '/interview-prep/cheat-sheets/linear-algebra-calculus-optimization/' | relative_url }})

### AIE-B7-03 — Diagnose a mixed-precision training run whose loss becomes NaN after 2,000 steps.

**Round:** Optimization debugging · **Depth:** Advanced

**Strong answer signals**

- Pin code, data shard, checkpoint, batch, optimizer, schedule and precision; locate the first non-finite input, activation, loss, gradient or parameter with a small reproducible run.
- Check label range, masking, reductions, log/softmax stability, normalization, distributed aggregation, overflow/underflow and data-specific triggers before adding clipping.
- Compare full precision, stable fused losses, loss scaling, lower learning rate or warmup one hypothesis at a time, then add finite-value and gradient telemetry to CI/release gates.

**Follow-up probe:** Why can gradient clipping make this incident harder to diagnose?

**Revision links:** [Linear algebra, calculus, and optimization]({{ '/interview-prep/cheat-sheets/linear-algebra-calculus-optimization/' | relative_url }})

### AIE-B7-04 — Use SVD or PCA to compress a high-dimensional inference input safely.

**Round:** Model efficiency · **Depth:** Applied

**Strong answer signals**

- Clarify whether data is centered, sparse and scaled; distinguish centered PCA from truncated SVD and fit every learned transform on training/reference data only.
- Select dimension from validation quality, latency, memory and reconstruction or downstream error rather than explained variance alone.
- Package the exact transform with serving, monitor component/input drift and parity, and retain a fallback because low-variance directions can still be predictive.

**Follow-up probe:** Why might 95% explained variance still damage the production classifier?

**Revision links:** [Linear algebra, calculus, and optimization]({{ '/interview-prep/cheat-sheets/linear-algebra-calculus-optimization/' | relative_url }})

### AIE-B7-05 — Scale global batch size across GPUs without silently changing optimization.

**Round:** Distributed training · **Depth:** Advanced

**Strong answer signals**

- Calculate physical batch, data-parallel replicas and gradient accumulation; compare runs by tokens/examples, optimizer steps, wall time and held-out quality.
- Treat learning-rate scaling, warmup, decay, optimizer state, gradient reduction and stochasticity as explicit experimental choices rather than automatic rules.
- Verify throughput, numerical stability, convergence, reproducibility and checkpoint recovery; reject extra scale when communication or generalization erases the gain.

**Follow-up probe:** Why are two runs with the same epoch count not comparable after the global batch changes?

**Revision links:** [Linear algebra, calculus, and optimization]({{ '/interview-prep/cheat-sheets/linear-algebra-calculus-optimization/' | relative_url }})

## Experimentation and causal inference

### AIE-B7-06 — Design an online experiment for an agent-assisted support workflow.

**Round:** Product experimentation · **Depth:** Advanced

**Strong answer signals**

- Define eligible agent or customer unit, immutable assignment, treatment version, ITT estimand, resolution horizon and exposure diagnostics without conditioning the primary result on usage.
- Use resolution or repeat-contact outcome plus safety, hallucination, escalation, latency, cost and employee-workload guardrails; plan power at the randomization unit.
- Validate assignment/logging with A/A and SRM checks, ramp safely, preserve long enough follow-up and reconcile whether product lift survives delivery failures.

**Follow-up probe:** Why would analyzing only conversations where the agent suggestion was opened bias the result?

**Revision links:** [Experimentation and causal inference]({{ '/interview-prep/cheat-sheets/experimentation-causal-inference/' | relative_url }})

### AIE-B7-07 — Choose the randomization unit for a recommendation model used by shared business accounts.

**Round:** Experimental architecture · **Depth:** Advanced

**Strong answer signals**

- Map persistent assignment, shared users/devices, account-level inventory, cross-user learning and interference before choosing user, account or cluster randomization.
- Analyze uncertainty at the assignment unit and inflate sample needs for within-account correlation rather than treating recommendation events as independent.
- Keep eligibility, assignment, exposure and metric joins auditable; quantify contamination and prefer the smallest unit that keeps it acceptably bounded.

**Follow-up probe:** What changes in power if assignment moves from users to accounts?

**Revision links:** [Experimentation and causal inference]({{ '/interview-prep/cheat-sheets/experimentation-causal-inference/' | relative_url }})

### AIE-B7-08 — Investigate sample ratio mismatch before reading an experiment's lift.

**Round:** Experiment reliability · **Depth:** Advanced

**Strong answer signals**

- Recompute planned versus observed assignment at the immutable randomized unit and segment by time, platform, version, geography and eligibility path.
- Trace hashing, bucketing, crashes, logging loss, post-assignment filters, joins, bots and overlapping experiments; preserve raw assignment as the source of truth.
- Pause effect interpretation, repair and validate with A/A/shadow evidence; avoid reweighting until the missingness mechanism and outcome relationship are understood.

**Follow-up probe:** Why can an arm-specific crash create both SRM and biased outcome estimates?

**Revision links:** [Experimentation and causal inference]({{ '/interview-prep/cheat-sheets/experimentation-causal-inference/' | relative_url }})

### AIE-B7-09 — Design a switchback test for a routing model that changes shared queue behavior.

**Round:** Causal system design · **Depth:** Advanced

**Strong answer signals**

- Explain why concurrent request-level randomization interferes through shared capacity, then choose randomized time blocks, eligible queues and a policy-level estimand.
- Set block and washout lengths using queue persistence, autocorrelation and operational cycles; balance time-of-day/day-of-week and account for shared shocks.
- Track service level, delay, abandonment, quality, cost and safety with block-aware inference, ramp controls and a carryover sensitivity analysis.

**Follow-up probe:** What happens if the block is shorter than the queue's recovery time?

**Revision links:** [Experimentation and causal inference]({{ '/interview-prep/cheat-sheets/experimentation-causal-inference/' | relative_url }})

### AIE-B7-10 — Estimate the effect of voluntary AI-assistant adoption from observational logs.

**Round:** Causal inference · **Depth:** Advanced

**Strong answer signals**

- Define adoption, outcome, population and horizon; draw a DAG covering motivation, skill, workload, manager policy, prior performance, exposure opportunity and post-treatment engagement.
- State that propensity weighting/matching can balance measured pre-treatment covariates only; check overlap, balance, extreme weights and temporal ordering.
- Seek a stronger design such as randomized encouragement or phased rollout, run negative-control and sensitivity analyses, and label residual unmeasured-confounding limits.

**Follow-up probe:** Why would controlling for post-adoption usage time change or bias the estimand?

**Revision links:** [Experimentation and causal inference]({{ '/interview-prep/cheat-sheets/experimentation-causal-inference/' | relative_url }})

## Data preparation, EDA, and feature engineering

### AIE-B7-11 — Build point-in-time fraud features for online serving and offline training.

**Round:** Feature architecture · **Depth:** Advanced

**Strong answer signals**

- Define transaction key, event and available-at times, prediction cutoff, rolling-window inclusion, late/correction policy, label horizon and online freshness fallback.
- Preserve immutable events and versioned definitions; use point-in-time joins offline and materialized keyed values online with source, timestamp, TTL and lineage.
- Reconcile sampled online/offline values, isolate backfills, test clock/timezone boundaries and monitor missing, stale, defaulted and drifted features by slice.

**Follow-up probe:** How would a chargeback recorded thirty days later leak into a historical feature rebuild?

**Revision links:** [Data preparation, EDA, and feature engineering]({{ '/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/' | relative_url }})

### AIE-B7-12 — Repair a document classifier whose random-split validation is unrealistically high.

**Round:** Leakage debugging · **Depth:** Advanced

**Strong answer signals**

- Audit duplicated/templated documents, customer/source identity, file metadata, post-resolution text, label-generation artifacts and vocabulary or embeddings fit before splitting.
- Rebuild group- and time-aware splits matching new-document deployment, fitting every parser-derived vocabulary, selector and transform inside training folds.
- Compare a metadata-only and simple text baseline, report performance by source/time, and add similarity-based duplicate gates plus a final untouched holdout.

**Follow-up probe:** Why can removing exact duplicates still leave near-duplicate leakage?

**Revision links:** [Data preparation, EDA, and feature engineering]({{ '/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/' | relative_url }})

### AIE-B7-13 — Encode a high-cardinality supplier field without target leakage.

**Round:** Feature engineering · **Depth:** Advanced

**Strong answer signals**

- Compare hashing, frequency, learned embeddings and smoothed target encoding against cardinality, data volume, interpretability, unseen suppliers, privacy and latency.
- If target encoding is used, compute training values out of fold and strictly from earlier outcomes for temporal data, with smoothing and global/rare/unseen fallbacks.
- Package mapping/version with serving and monitor category coverage, support, drift and performance; validate that supplier identity will legitimately exist at decision time.

**Follow-up probe:** How does full-data target encoding reveal each row's own label?

**Revision links:** [Data preparation, EDA, and feature engineering]({{ '/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/' | relative_url }})

### AIE-B7-14 — Eliminate training-serving skew in a feature preprocessing pipeline.

**Round:** ML reliability · **Depth:** Advanced

**Strong answer signals**

- Inventory schema, units, defaults, imputation, encoders, windows, sources and version boundaries in training and online paths; identify duplicated implementations.
- Move learned transforms into one versioned artifact or shared definition, enforce strict input contracts and retain event/produced-at timestamps for time-sensitive values.
- Add golden fixtures and sampled parity reconciliation with tolerances, plus alerts for stale/defaulted/unseen values and a safe fallback or rollback.

**Follow-up probe:** Why can identical feature code still produce different offline and online values?

**Revision links:** [Data preparation, EDA, and feature engineering]({{ '/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/' | relative_url }})

### AIE-B7-15 — Train an imbalanced incident detector under a fixed daily review capacity.

**Round:** Decision-aware modeling · **Depth:** Advanced

**Strong answer signals**

- Define incident label maturity, false-negative cost, review capacity and intervention; use time/entity splits and preserve real prevalence for validation.
- Compare weighting or fold-local resampling with simple baselines; select by precision/recall and captured value at the daily alert budget plus calibration and slice constraints.
- Version the threshold separately, shadow/canary the workflow, sample below-threshold cases and monitor alert volume, yield, delay, workload and prevalence shift.

**Follow-up probe:** Why can ROC-AUC improve while the top 100 daily alerts become worse?

**Revision links:** [Data preparation, EDA, and feature engineering]({{ '/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/' | relative_url }})

## Unsupervised learning and anomaly detection

### AIE-B7-16 — Build a customer-segmentation service that supports an actual product decision.

**Round:** Unsupervised system design · **Depth:** Advanced

**Strong answer signals**

- Start from the decision and unit, define a point-in-time behavior window, exclude identifiers/outcomes, choose scale and geometry, and state how new customers are assigned.
- Compare k-means, mixtures and density methods using stability across seeds/time, interpretability, minimum support, migration and prospective downstream value—not one 2D plot.
- Version representation, model and segment definitions; monitor coverage, drift and fairness, and require a controlled test before claiming segment-specific treatment value.

**Follow-up probe:** What evidence would show the segments are actionable rather than merely descriptive?

**Revision links:** [Unsupervised learning and anomaly detection]({{ '/interview-prep/cheat-sheets/unsupervised-learning-anomaly-detection/' | relative_url }})

### AIE-B7-17 — Select an anomaly detector for multivariate machine telemetry.

**Round:** Anomaly engineering · **Depth:** Advanced

**Strong answer signals**

- Define machine/window, operating modes, seasonality, reference period, failure labels, detection delay, review/maintenance action and missing-sensor behavior.
- Benchmark rules and forecast/PCA residuals against Isolation Forest, local methods or autoencoders, fitting only on justified reference data and using rolling-origin validation.
- Choose thresholds from incident cost and inspection capacity, expose feature/context evidence, group alerts into cases and preserve model/threshold rollback.

**Follow-up probe:** When would a global detector mistake a valid operating mode for an anomaly?

**Revision links:** [Unsupervised learning and anomaly detection]({{ '/interview-prep/cheat-sheets/unsupervised-learning-anomaly-detection/' | relative_url }})

### AIE-B7-18 — Use UMAP or t-SNE responsibly in an embedding-analysis tool.

**Round:** Representation analysis · **Depth:** Applied

**Strong answer signals**

- Treat the projection as an exploratory neighborhood visualization, document sample, preprocessing, metric, parameters and seed, and compare multiple runs.
- Do not infer global distance, prevalence, causal structure or validated clusters from gap/area; test neighborhoods and clustering in the original justified space.
- Keep labels/colors out of fitting, provide source examples and uncertainty, and avoid using an unstable plot coordinate as a production feature without independent validation.

**Follow-up probe:** Why can the same embeddings show different apparent islands under another seed or perplexity?

**Revision links:** [Unsupervised learning and anomaly detection]({{ '/interview-prep/cheat-sheets/unsupervised-learning-anomaly-detection/' | relative_url }})

### AIE-B7-19 — Evaluate an anomaly detector when confirmed incidents are scarce.

**Round:** Evaluation · **Depth:** Advanced

**Strong answer signals**

- Use time-held historical incidents and prospective shadow adjudication, while randomly auditing below-threshold cases to estimate missed events and reviewer-selection bias.
- Add bounded synthetic fault injection only for known signatures; test stability across seeds/windows and report precision at capacity, delay, alert burden and downstream value.
- Track evidence provenance and uncertainty, maintain an adjudicated set, and require a feedback path rather than claiming recall from unlabeled data.

**Follow-up probe:** Why is analyst precision among reviewed alerts an incomplete metric?

**Revision links:** [Unsupervised learning and anomaly detection]({{ '/interview-prep/cheat-sheets/unsupervised-learning-anomaly-detection/' | relative_url }})

### AIE-B7-20 — Respond when a newly onboarded site causes an anomaly-alert flood.

**Round:** Production incident · **Depth:** Leadership

**Strong answer signals**

- Cap and triage alerts without discarding scores/evidence, identify model, threshold, schema and reference versions, and compare units, firmware, sampling, missingness and operating modes by site.
- Decide whether the change is pipeline error, legitimate new population or real incident; avoid automatic retraining until the mechanism and safety impact are known.
- Repair or build context-aware reference models in shadow mode, audit suppressed cases, and add onboarding contracts, unit checks, threshold ownership and rollback.

**Follow-up probe:** Which evidence would justify a site-specific model instead of correcting the ingestion path?

**Revision links:** [Unsupervised learning and anomaly detection]({{ '/interview-prep/cheat-sheets/unsupervised-learning-anomaly-detection/' | relative_url }})

## Experimentation and causal inference — advanced practice

### AIE-B8-01 — Design the assignment and exposure services for an AI product experiment.

**Round:** Experiment platform engineering · **Depth:** Advanced

**Strong answer signals**

- Define the stable randomization unit, eligibility point, deterministic bucketing, experiment and variant versions, mutual exclusions, and persistent assignment semantics.
- Log assignment separately from delivery and exposure with event time, request identity, treatment configuration, and reason codes for failed or partial rendering.
- Add A/A, sample-ratio-mismatch, duplicate-unit, telemetry-loss, rollback, and replay tests so analysis can reconstruct intention-to-treat without joining on post-treatment behavior.

**Follow-up probe:** Why must assignment remain queryable even when the treatment service times out?

**Revision links:** [Experimentation and causal inference]({{ '/interview-prep/cheat-sheets/experimentation-causal-inference/' | relative_url }})

### AIE-B8-02 — Implement a valid sequential decision process for a costly model experiment.

**Round:** Statistical engineering · **Depth:** Advanced

**Strong answer signals**

- Predeclare the estimand, primary metric, monitoring cadence, information horizon, error control, efficacy/futility boundaries, guardrails, and maximum sample.
- Use a supported group-sequential, alpha-spending, always-valid, or Bayesian decision method instead of repeatedly applying a fixed-horizon p-value.
- Version the analysis policy, preserve every interim data cut, separate safety stops from efficacy, and simulate operating characteristics before launch.

**Follow-up probe:** Why does refreshing a fixed-horizon dashboard every hour inflate false positives?

**Revision links:** [Experimentation and causal inference]({{ '/interview-prep/cheat-sheets/experimentation-causal-inference/' | relative_url }})

### AIE-B8-03 — Add CUPED variance reduction without leaking treatment information.

**Round:** Experiment implementation · **Depth:** Advanced

**Strong answer signals**

- Build the covariate strictly from pre-assignment data with a stable unit, window, availability rule, missing-history fallback, and definition shared across arms.
- Estimate the adjustment within the declared analysis, retain intention-to-treat, and compute uncertainty at the randomization unit rather than treating events as independent.
- Test invariant behavior in A/A data, compare adjusted and unadjusted estimates, and block any covariate whose production timestamp or source can be affected by treatment.

**Follow-up probe:** How could a “seven-day activity” feature become post-treatment even if its table is called historical?

**Revision links:** [Experimentation and causal inference]({{ '/interview-prep/cheat-sheets/experimentation-causal-inference/' | relative_url }})

### AIE-B8-04 — Instrument a tool-using agent so causal product impact can be estimated.

**Round:** Agent analytics architecture · **Depth:** Advanced

**Strong answer signals**

- Log immutable assignment, agent/prompt/tool/policy versions, exposure opportunity, user action, tool effects, errors, latency, cost, safety outcomes, and matured business outcomes.
- Keep diagnostics such as accepted suggestions or tool use out of the primary ITT filter because they are post-treatment; use them for mechanism analysis with caveats.
- Preserve user/account identity and privacy boundaries, deterministic event IDs, late-data corrections, and an analysis-ready unit table that reconciles partial workflows.

**Follow-up probe:** Which useful-looking agent event would become a collider if used to select the analysis population?

**Revision links:** [Experimentation and causal inference]({{ '/interview-prep/cheat-sheets/experimentation-causal-inference/' | relative_url }})

### AIE-B8-05 — Choose between user randomization, cluster randomization, and a switchback.

**Round:** Causal system design · **Depth:** Advanced

**Strong answer signals**

- Map persistence, shared capacity, social or marketplace interference, contamination paths, carryover, and the policy-level decision before selecting the unit.
- Prefer the smallest independent unit that delivers the treatment correctly; move to clusters or randomized time blocks when shared state invalidates simultaneous user assignment.
- Analyze at the assigned unit, account for intracluster correlation or autocorrelation, balance operational cycles, and test washout and spillover sensitivity.

**Follow-up probe:** What evidence shows a switchback block is long enough for system state to wash out?

**Revision links:** [Experimentation and causal inference]({{ '/interview-prep/cheat-sheets/experimentation-causal-inference/' | relative_url }})

## Feature engineering and ML data validation

### AIE-B8-06 — Turn a feature definition into an executable production contract.

**Round:** Feature platform engineering · **Depth:** Advanced

**Strong answer signals**

- Bind entity key, event/processing/availability times, source, transformation version, unit, type, null/default semantics, freshness, privacy class, TTL, owner, and allowed use.
- Add schema, range, relationship, uniqueness, point-in-time, distribution, and online/offline parity tests with blocking versus quarantine behavior.
- Version compatible changes, publish lineage and consumers, support backfill and deletion propagation, and fail safely when a critical contract is unknown or stale.

**Follow-up probe:** Why is a feature's event timestamp insufficient to prove it was available to the model?

**Revision links:** [Feature engineering and ML data validation]({{ '/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/' | relative_url }})

### AIE-B8-07 — Rebuild historical features after late corrections without creating leakage.

**Round:** Point-in-time data engineering · **Depth:** Advanced

**Strong answer signals**

- Preserve event time, arrival/availability time, correction version, original record identity, and the policy for what a historical decision could have known.
- Distinguish as-known-at-the-time training reconstruction from latest-truth reporting, and use bitemporal or versioned snapshots when both are required.
- Isolate the backfill, pin code/config/source identity, compare affected entities and labels, reconcile downstream stores, and prevent duplicate online effects.

**Follow-up probe:** When should corrected truth update labels but not historical serving features?

**Revision links:** [Feature engineering and ML data validation]({{ '/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/' | relative_url }})

### AIE-B8-08 — Diagnose feature drift before triggering retraining.

**Round:** ML reliability · **Depth:** Advanced

**Strong answer signals**

- Segment the change by source, time, tenant, version and pipeline stage; inspect schema, units, missingness, sampling, freshness, category coverage and parity first.
- Separate upstream defect, legitimate seasonality, population shift, policy feedback and target-concept change using source evidence and delayed outcomes.
- Contain unsafe inputs, choose repair, recalibration or retraining from the diagnosed mechanism, and retain a rollback plus effectiveness check.

**Follow-up probe:** Why can retraining on a unit-conversion bug make recovery harder?

**Revision links:** [Feature engineering and ML data validation]({{ '/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/' | relative_url }})

### AIE-B8-09 — Design a safe feature-store backfill and online materialization.

**Round:** Data platform reliability · **Depth:** Advanced

**Strong answer signals**

- Define bounded entity/time scope, exact feature version, source snapshots, event and availability cutoffs, compute capacity, publication mode and consumer impact.
- Write idempotently to staged/offline outputs, validate point-in-time fixtures and distributions, then materialize online values with timestamps, TTL and atomic version switching.
- Reconcile offline/online samples, rate-limit production load, preserve prior values for rollback, and communicate changed semantics to every consuming model.

**Follow-up probe:** How would you avoid mixing two feature definitions during a long backfill?

**Revision links:** [Feature engineering and ML data validation]({{ '/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/' | relative_url }})

### AIE-B8-10 — Build an active-learning and annotation pipeline without corrupting evaluation.

**Round:** Data-centric AI · **Depth:** Advanced

**Strong answer signals**

- Separate randomly sampled adjudicated evaluation data from uncertain, diverse or high-impact examples selected for labeling; version rubric, annotator and provenance.
- Track selection probability, coverage, disagreement, conflicts, turnaround and privacy; prevent model suggestions from becoming unreviewed ground truth.
- Retrain through reproducible data versions, evaluate on untouched representative/time holdouts, and maintain random audits to estimate blind spots outside the selected pool.

**Follow-up probe:** Why does evaluating only actively selected examples misstate production performance?

**Revision links:** [Feature engineering and ML data validation]({{ '/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/' | relative_url }})

## Time series and forecasting

### AIE-B8-11 — Define the contract for a production demand-forecasting API.

**Round:** Forecasting system design · **Depth:** Advanced

**Strong answer signals**

- Specify series/hierarchy, target and unit, forecast origin, frequency, horizons, lead time, known-future versus observed covariates, output type and decision loss.
- Version model, data cutoff, calendar, scenario/covariate inputs and quantiles; return freshness, fallback and partial-series diagnostics with the forecast.
- Set latency, availability, backfill, reconciliation and publication semantics, including what happens when required history or future covariates are missing.

**Follow-up probe:** How should the API distinguish a realized weather value from a weather forecast available at origin?

**Revision links:** [Time series and forecasting]({{ '/interview-prep/cheat-sheets/time-series-forecasting/' | relative_url }})

### AIE-B8-12 — Implement rolling-origin evaluation for many related series.

**Round:** Forecast evaluation engineering · **Depth:** Advanced

**Strong answer signals**

- Generate origins in chronological order with fixed/expanding training windows, required gaps, horizon-specific targets and label-maturity checks; never shuffle rows.
- Refit preprocessing and model per fold as production would, retain naive/seasonal baselines, and aggregate metrics by horizon, series, segment and business weight.
- Persist origin, cutoff, feature/covariate versions and predictions for reproducibility; control compute with representative folds without leaking future tuning evidence.

**Follow-up probe:** Why can one final holdout hide a model that degrades badly at longer horizons?

**Revision links:** [Time series and forecasting]({{ '/interview-prep/cheat-sheets/time-series-forecasting/' | relative_url }})

### AIE-B8-13 — Prevent future-covariate leakage in a forecasting feature pipeline.

**Round:** Temporal data correctness · **Depth:** Advanced

**Strong answer signals**

- Classify static, observed-past, known-future and forecasted covariates; record when each value was operationally available at every forecast origin.
- Build lags and rolling statistics using strictly prior observations, fit scaling/encoding on training history, and evaluate with the same forecasted external inputs used in production.
- Add hand-audited origin fixtures, timestamp/timezone boundary tests and lineage so realized future prices, stockouts or weather cannot enter training silently.

**Follow-up probe:** Why is a published holiday calendar safe while realized future promotion uptake is not?

**Revision links:** [Time series and forecasting]({{ '/interview-prep/cheat-sheets/time-series-forecasting/' | relative_url }})

### AIE-B8-14 — Serve probabilistic forecasts for an inventory decision.

**Round:** Decision-aware forecasting · **Depth:** Advanced

**Strong answer signals**

- Produce calibrated quantiles or scenarios aligned to overage/underage costs and lead time rather than returning only a point forecast.
- Validate pinball loss, interval coverage and sharpness by horizon/segment, check quantile crossing and reconcile hierarchy or inventory constraints deliberately.
- Expose model/data version and uncertainty to the optimizer, monitor realized coverage and cost, and fall back to conservative baseline intervals under data failure.

**Follow-up probe:** Which quantile is appropriate when stockout cost is much larger than holding cost?

**Revision links:** [Time series and forecasting]({{ '/interview-prep/cheat-sheets/time-series-forecasting/' | relative_url }})

### AIE-B8-15 — Operate a forecasting service through regime change.

**Round:** Production reliability · **Depth:** Leadership

**Strong answer signals**

- Monitor input timeliness, forecast bias, residuals, interval coverage, error by horizon/series, baseline comparison, overrides and downstream cost.
- Diagnose pipeline defect, one-off shock, lasting regime shift, censoring/stockout change or model staleness before choosing retraining or reweighting.
- Use champion/challenger or shadow evidence, bounded recent windows, manual/domain overrides, rollback and post-change forecast-value measurement.

**Follow-up probe:** Why can shortening the training window help one regime change but harm seasonal estimation?

**Revision links:** [Time series and forecasting]({{ '/interview-prep/cheat-sheets/time-series-forecasting/' | relative_url }})

## Recommendation, search, and ranking

### AIE-B8-16 — Design a multi-stage recommendation service under a strict latency budget.

**Round:** Ranking system design · **Depth:** Advanced

**Strong answer signals**

- Define request context, item universe, eligibility/safety, freshness, objective and exposure logging; allocate latency across candidate sources, ranking and policy re-ranking.
- Combine popularity/recency/content/collaborative or two-tower candidates for high recall, deduplicate, then use richer cross features only on the bounded candidate set.
- Cache/version embeddings and features safely, support cold-start fallbacks, monitor stage recall, ranking quality, availability, latency, cost and rollback.

**Follow-up probe:** Why can improving the ranker fail when the relevant item never reaches its candidate set?

**Revision links:** [Recommendation, search, and ranking]({{ '/interview-prep/cheat-sheets/recommendation-search-ranking/' | relative_url }})

### AIE-B8-17 — Implement negative sampling for a two-tower retrieval model.

**Round:** Retrieval modeling · **Depth:** Advanced

**Strong answer signals**

- Distinguish exposed non-actions from unexposed items, choose random, popularity, in-batch and hard negatives with an explicit sampling distribution and false-negative policy.
- Prevent same-user/duplicate positives from becoming negatives, account for batch/cross-device dependence, and use weighting or correction when training and serving distributions differ.
- Evaluate full-corpus or representative retrieval recall by slice and popularity, inspect embedding norms and hard-negative quality, and compare simple candidate baselines.

**Follow-up probe:** How can in-batch negatives penalize an item that is relevant to several users?

**Revision links:** [Recommendation, search, and ranking]({{ '/interview-prep/cheat-sheets/recommendation-search-ranking/' | relative_url }})

### AIE-B8-18 — Build offline evaluation that separates retrieval from ranking.

**Round:** Evaluation engineering · **Depth:** Advanced

**Strong answer signals**

- Use time- and user-aware splits with logged exposure and an explicit candidate universe; prevent future interactions, duplicate impressions and target-derived features.
- Measure candidate Recall@K/coverage first, then ranker NDCG/MRR/precision with diversity, novelty, calibration, safety, long-tail and latency diagnostics.
- Reproduce the historical policy and label window, report popularity/position bias limitations, and require an online experiment before claiming product impact.

**Follow-up probe:** Why is sampled-candidate NDCG not directly comparable with full-corpus NDCG?

**Revision links:** [Recommendation, search, and ranking]({{ '/interview-prep/cheat-sheets/recommendation-search-ranking/' | relative_url }})

### AIE-B8-19 — Handle cold start and controlled exploration in a recommender.

**Round:** Recommendation reliability · **Depth:** Advanced

**Strong answer signals**

- Separate new user, new item and sparse-context cases; combine onboarding/context, content, popularity/recency and business-safe fallback rather than returning empty results.
- Introduce bounded exploration with eligibility, safety, traffic/cost caps and logged propensities so new or long-tail items can receive evidence without uncontrolled harm.
- Monitor coverage, novelty, regret, user feedback and segment fairness, and keep exploitation plus rollback when exploration telemetry or policy fails.

**Follow-up probe:** Why does always recommending popular items make future offline evaluation more biased?

**Revision links:** [Recommendation, search, and ranking]({{ '/interview-prep/cheat-sheets/recommendation-search-ranking/' | relative_url }})

### AIE-B8-20 — Diagnose a ranking release that improved offline NDCG but reduced conversions.

**Round:** Production incident · **Depth:** Leadership

**Strong answer signals**

- Verify exact model/candidate/feature/policy versions, exposure and position logging, online assignment, latency/errors, inventory eligibility and metric definitions before blaming user preference.
- Test candidate recall, calibration, diversity, repetition, long-tail, price/availability and segment shifts; inspect whether offline labels reproduce the old policy rather than the new objective.
- Roll back or narrow exposure, preserve evidence, correct the stage or metric, rerun guarded experiments and add end-to-end business plus reliability gates.

**Follow-up probe:** Which online failure could lower conversion even if the served ordering matches the offline model?

**Revision links:** [Recommendation, search, and ranking]({{ '/interview-prep/cheat-sheets/recommendation-search-ranking/' | relative_url }})

## Linear algebra, calculus, and optimization

### AIE-B9-01 — Implement a numerically stable softmax endpoint and prove it matches the model contract.

**Round:** Numerical reliability · **Depth:** Advanced

**Strong answer signals**

- Subtract the row maximum before exponentiation, preserve the intended axis and shape, use an appropriate accumulation dtype, and reject or handle non-finite inputs explicitly.
- Compare against a trusted implementation across extreme logits, batched and singleton shapes, mixed precision, empty/invalid cases, and verify probabilities are finite, non-negative, and sum to one within tolerance.
- Version preprocessing, model, runtime and postprocessing together; monitor non-finite values and distribution shifts and fail safely instead of returning plausible corrupted scores.

**Follow-up probe:** Why does subtracting the maximum preserve the probabilities while preventing overflow?

**Revision links:** [Linear algebra, calculus, and optimization]({{ '/interview-prep/cheat-sheets/linear-algebra-calculus-optimization/' | relative_url }})

### AIE-B9-02 — Add a custom differentiable operation to a training pipeline and validate its backward pass.

**Round:** Automatic differentiation · **Depth:** Advanced

**Strong answer signals**

- State input/output shapes and dtypes, derive the local Jacobian-vector product, preserve only required forward state, and define behavior at non-differentiable or invalid points.
- Run central-difference gradient checks in double precision on small, non-saturated inputs and compare directional derivatives rather than relying only on a falling training loss.
- Test broadcasting, batching, device and mixed-precision behavior; add finite-gradient checks and isolate the release behind reproducible seeds and rollback.

**Follow-up probe:** Why can finite-difference checks fail near a kink even when the implementation is correct?

**Revision links:** [Linear algebra, calculus, and optimization]({{ '/interview-prep/cheat-sheets/linear-algebra-calculus-optimization/' | relative_url }})

### AIE-B9-03 — Build an optimization service that distinguishes infeasible, unbounded, timed-out, and feasible solutions.

**Round:** Constrained optimization · **Depth:** Advanced

**Strong answer signals**

- Validate units, domains, bounds and constraint dimensions before solving; assign immutable model/data/solver identities and make the objective and feasibility tolerances explicit.
- Return typed statuses with incumbent, bound/gap, violations, runtime and diagnostics; never convert an absent or partial solution into an empty valid plan.
- Test known feasible/infeasible/unbounded fixtures, enforce time and memory limits, preserve solver evidence, and use an approved fallback or human review when guarantees are not met.

**Follow-up probe:** When may a timed-out incumbent be operationally usable, and what evidence must accompany it?

**Revision links:** [Linear algebra, calculus, and optimization]({{ '/interview-prep/cheat-sheets/linear-algebra-calculus-optimization/' | relative_url }})

### AIE-B9-04 — Migrate a training job from Adam to AdamW while increasing global batch size.

**Round:** Training optimization · **Depth:** Advanced

**Strong answer signals**

- Treat optimizer, decoupled weight decay, excluded parameters, learning-rate schedule, warmup, gradient accumulation and effective batch as one versioned experiment contract.
- Match tokens/examples and update counts, log gradient and update norms plus loss/validation trajectories, and compare controlled candidates rather than changing batch, optimizer and regularization without attribution.
- Add non-finite and divergence stops, checkpoint optimizer/scheduler/scaler state, test resume equivalence, and promote only after quality, stability, throughput and memory gates pass.

**Follow-up probe:** Why is an L2 penalty inside Adam not generally equivalent to AdamW weight decay?

**Revision links:** [Linear algebra, calculus, and optimization]({{ '/interview-prep/cheat-sheets/linear-algebra-calculus-optimization/' | relative_url }})

### AIE-B9-05 — Diagnose a linear-system feature transform that became unstable after new correlated inputs arrived.

**Round:** Linear algebra incident · **Depth:** Leadership

**Strong answer signals**

- Reproduce the exact matrix and scaling path, inspect rank, singular values and condition number, and separate data duplication/collinearity from dtype or solver changes.
- Avoid explicit matrix inversion; compare stable factorizations or SVD/pseudoinverse with justified truncation or regularization and measure downstream sensitivity.
- Roll back or quarantine the change, version the feature basis and tolerance, and add conditioning, finite-output and perturbation tests plus drift alerts.

**Follow-up probe:** Why can a system have a mathematically unique solution yet still be unreliable in floating-point arithmetic?

**Revision links:** [Linear algebra, calculus, and optimization]({{ '/interview-prep/cheat-sheets/linear-algebra-calculus-optimization/' | relative_url }})

## Unsupervised learning and dimensionality reduction

### AIE-B9-06 — Build a clustering pipeline whose distance geometry is identical offline and online.

**Round:** Unsupervised data engineering · **Depth:** Advanced

**Strong answer signals**

- Define the unit, feature snapshot, missing-value policy, scaling, encoding and distance/similarity contract; fit all learned transforms only on the training/reference population.
- Package transform, feature order, metric and cluster model under one artifact identity, test online/offline parity, and reject schema or unit mismatches.
- Monitor representation drift, assignment confidence, cluster size/stability and downstream utility, with a deterministic fallback for unseen or invalid inputs.

**Follow-up probe:** Why can one unscaled high-variance feature dominate Euclidean k-means even if it is not useful?

**Revision links:** [Unsupervised learning and dimensionality reduction]({{ '/interview-prep/cheat-sheets/unsupervised-learning-dimensionality-reduction/' | relative_url }})

### AIE-B9-07 — Publish customer-segment labels without breaking downstream consumers when clusters are retrained.

**Round:** Cluster lifecycle · **Depth:** Advanced

**Strong answer signals**

- Treat cluster numbers as arbitrary; align candidate clusters to prior semantic segments using overlap/centroid/assignment evidence and route ambiguous splits or merges to review.
- Version population window, transforms, model, mapping and business label; publish atomically and preserve the previous mapping for rollback and historical reproducibility.
- Contract-test segment values and eligibility, monitor membership churn and outcome utility, and require downstream owners to accept material definition changes.

**Follow-up probe:** Why is sorting new centroids and reusing the old numeric IDs unsafe?

**Revision links:** [Unsupervised learning and dimensionality reduction]({{ '/interview-prep/cheat-sheets/unsupervised-learning-dimensionality-reduction/' | relative_url }})

### AIE-B9-08 — Operationalize a Gaussian-mixture model whose EM training sometimes collapses a component.

**Round:** Probabilistic clustering · **Depth:** Advanced

**Strong answer signals**

- Standardize inputs, use multiple seeded initializations and covariance regularization, bound iterations/tolerance, and detect tiny weights, singular covariance and non-finite likelihood.
- Select a candidate using held-out likelihood, stability and downstream usefulness rather than accepting the highest training likelihood from one run.
- Store responsibilities as calibrated soft assignments where appropriate, version component alignment, and fall back or retrain when convergence diagnostics fail.

**Follow-up probe:** How can a Gaussian component drive likelihood upward by collapsing around very few observations?

**Revision links:** [Unsupervised learning and dimensionality reduction]({{ '/interview-prep/cheat-sheets/unsupervised-learning-dimensionality-reduction/' | relative_url }})

### AIE-B9-09 — Serve a density-based clustering result to new observations.

**Round:** Density clustering · **Depth:** Advanced

**Strong answer signals**

- Clarify that standard DBSCAN produces fitted clusters/noise but does not define a universal prediction rule; choose a documented approximation, refit cadence or HDBSCAN-style prediction capability.
- Persist scaling, metric, neighborhood parameters, reference points and cluster identities; bound nearest-neighbor search and define low-confidence/noise behavior explicitly.
- Test boundary, sparse and shifted regions, measure assignment stability and downstream utility, and avoid presenting forced assignments as discovered ground truth.

**Follow-up probe:** What is lost when every new point is assigned to the nearest existing cluster regardless of density?

**Revision links:** [Unsupervised learning and dimensionality reduction]({{ '/interview-prep/cheat-sheets/unsupervised-learning-dimensionality-reduction/' | relative_url }})

### AIE-B9-10 — Create an embedding-analysis tool that uses PCA and UMAP without turning a visualization into a production model.

**Round:** Dimensionality-reduction tooling · **Depth:** Advanced

**Strong answer signals**

- Fit scaling and PCA on a declared reference set, persist components/means and explained variance, then treat UMAP parameters and random seed as visualization metadata rather than causal evidence.
- Separate transformable production representations from exploratory two-dimensional views; test reconstruction/neighborhood preservation and label overlays only after the embedding is fixed.
- Warn users that distances and apparent clusters can change across seeds/settings, preserve source IDs and versions, and prohibit decisions based solely on the plot.

**Follow-up probe:** Why does a visually separated UMAP island not prove a real, stable population segment?

**Revision links:** [Unsupervised learning and dimensionality reduction]({{ '/interview-prep/cheat-sheets/unsupervised-learning-dimensionality-reduction/' | relative_url }})

## Anomaly detection and rare-event modeling

### AIE-B9-11 — Implement a robust statistical anomaly baseline before adding a learned detector.

**Round:** Detection baseline · **Depth:** Applied

**Strong answer signals**

- Define entity, signal, context, window, event-time availability and anomaly action; compute median/MAD or seasonal residual thresholds on an uncontaminated reference window.
- Handle zero dispersion, missing/late values, repeated alerts and cold start explicitly; version baseline window, transformations and threshold policy.
- Backtest event-level precision/recall, detection delay and alerts per period, then use the simple baseline as a shadow comparator for any complex model.

**Follow-up probe:** Why is a mean-and-standard-deviation rule fragile under heavy tails and contaminated history?

**Revision links:** [Anomaly detection and rare-event modeling]({{ '/interview-prep/cheat-sheets/anomaly-detection-rare-event-modeling/' | relative_url }})

### AIE-B9-12 — Design an event-time pipeline that separates point anomalies from change points.

**Round:** Streaming detection · **Depth:** Advanced

**Strong answer signals**

- Define event time, watermark/late-data policy and state per entity; use point scores for isolated deviations and a separate persistent-regime detector with reset/cooldown semantics.
- Make updates idempotent and replayable, checkpoint detector state, prevent future observations entering historical baselines, and bound state and recovery time.
- Evaluate detection delay, duplicate/missed events and alert duration under late/out-of-order fixtures, then expose the anomaly type and supporting window to responders.

**Follow-up probe:** Why can repeatedly flagging every sample after a mean shift be worse than emitting one change-point event?

**Revision links:** [Anomaly detection and rare-event modeling]({{ '/interview-prep/cheat-sheets/anomaly-detection-rare-event-modeling/' | relative_url }})

### AIE-B9-13 — Train a supervised rare-event service with delayed and selectively reviewed labels.

**Round:** Rare-event ML platform · **Depth:** Advanced

**Strong answer signals**

- Split by time/entity before resampling, define label maturity and availability, preserve exposure/review propensity, and prevent future outcomes or investigation features leaking backward.
- Apply weights or sampling only within training, calibrate on a deployment-like untouched set, and evaluate PR curves, recall at alert capacity, calibration and subgroup/time slices.
- Log scores, thresholds, eligibility, review decisions and mature outcomes; monitor selection effects and maintain shadow/random audits to estimate blind spots.

**Follow-up probe:** How can training only on investigated alerts create a self-reinforcing blind spot?

**Revision links:** [Anomaly detection and rare-event modeling]({{ '/interview-prep/cheat-sheets/anomaly-detection-rare-event-modeling/' | relative_url }})

### AIE-B9-14 — Implement thresholds for a detector with a fixed daily investigation budget.

**Round:** Alert decision engineering · **Depth:** Advanced

**Strong answer signals**

- Convert capacity, event cost, miss cost and response SLA into an explicit policy such as top-k or calibrated risk threshold, with deterministic tie and overload behavior.
- Tune on out-of-time data using event-level precision/recall, delay and alerts per entity/period; test thresholds by segment while guarding minimum evidence and fairness constraints.
- Version score, calibration and policy separately, monitor queue saturation and realized yield after labels mature, and provide fallback/prioritization when volume spikes.

**Follow-up probe:** Why can a fixed score threshold violate the same review budget after prevalence or score scale changes?

**Revision links:** [Anomaly detection and rare-event modeling]({{ '/interview-prep/cheat-sheets/anomaly-detection-rare-event-modeling/' | relative_url }})

### AIE-B9-15 — Recover from an anomaly release that floods responders while offline ROC-AUC remains high.

**Round:** Detection incident · **Depth:** Leadership

**Strong answer signals**

- Stop or narrow routing, preserve requests and versions, and compare prevalence, score distribution, threshold/calibrator, entity mix, deduplication and queue behavior with the last good release.
- Recompute precision-recall, alert yield, repeat-alert rate and capacity at the deployed operating point; inspect data/schema/seasonality shift and label delay rather than relying on ROC-AUC.
- Roll back model or policy atomically, drain/deduplicate safely, communicate impact, and add alert-budget, event-level and shadow-baseline release gates.

**Follow-up probe:** Why can ROC-AUC stay impressive while almost every alert sent to investigators is false?

**Revision links:** [Anomaly detection and rare-event modeling]({{ '/interview-prep/cheat-sheets/anomaly-detection-rare-event-modeling/' | relative_url }})

## Explainability, fairness, uncertainty, and model governance

### AIE-B9-16 — Design a versioned explanation service for tabular predictions.

**Round:** Model-assurance platform · **Depth:** Advanced

**Strong answer signals**

- Bind prediction, raw/transformed features, preprocessing, model, output scale, explainer, reference data and parameters to one immutable request identity.
- Return schema-validated attributions with local fidelity/additivity and stability diagnostics, privacy-safe feature labels, and explicit non-causal limitations.
- Cache only on the full identity, enforce access/retention, monitor failures and drift, and fall back to approved reason codes or human review rather than fabricate an explanation.

**Follow-up probe:** Why can changing the SHAP background dataset change the meaning of the same prediction's attribution?

**Revision links:** [Explainability, fairness, uncertainty, and model governance]({{ '/interview-prep/cheat-sheets/explainability-fairness-uncertainty-model-governance/' | relative_url }})

### AIE-B9-17 — Implement subgroup assurance metrics without exposing sensitive attributes to unauthorized consumers.

**Round:** Fairness telemetry · **Depth:** Advanced

**Strong answer signals**

- Keep protected evaluation data outside serving features, enforce purpose-limited access, and compute approved aggregates in a restricted boundary.
- Emit denominators, performance/error/calibration/selection measures and uncertainty by time/intersection with minimum-support and privacy rules.
- Version group definitions, label maturity, threshold/policy and metric code; alert accountable owners without leaking row-level membership and retain auditable decisions.

**Follow-up probe:** Why is removing a protected column from model inputs insufficient to rule out proxy effects?

**Revision links:** [Explainability, fairness, uncertainty, and model governance]({{ '/interview-prep/cheat-sheets/explainability-fairness-uncertainty-model-governance/' | relative_url }})

### AIE-B9-18 — Add calibration, conformal uncertainty, and abstention to a high-impact classifier API.

**Round:** Uncertainty engineering · **Depth:** Advanced

**Strong answer signals**

- Fit calibration and conformal quantiles on separate exchangeable validation/calibration data, pin all artifacts, and report reliability, coverage and set size by time and important groups.
- Define abstention from supported uncertainty/OOD/operational signals with coverage-risk targets, review capacity, user communication and deterministic fallback.
- Monitor prevalence, calibration and coverage after labels mature, detect assumption-breaking drift, and avoid describing marginal conformal coverage as a guarantee for every subgroup or individual.

**Follow-up probe:** What happens to conformal coverage claims when the deployment distribution shifts materially?

**Revision links:** [Explainability, fairness, uncertainty, and model governance]({{ '/interview-prep/cheat-sheets/explainability-fairness-uncertainty-model-governance/' | relative_url }})

### AIE-B9-19 — Build a release gate for model cards and model-assurance evidence.

**Round:** Governance automation · **Depth:** Leadership

**Strong answer signals**

- Require immutable data/model/runtime identities, intended and excluded use, baseline, metrics/slices/uncertainty, explanation limits, fairness-harm decisions and unresolved risks with owners.
- Verify privacy/security, robustness, threshold/abstention, human oversight, appeal, rollback and monitoring evidence through machine-checkable manifests where possible.
- Block promotion when required evidence or approval is missing, preserve the failed candidate, and trigger re-review on data, policy, population, interface or dependency changes.

**Follow-up probe:** Which parts of a governance gate must remain accountable human decisions even when evidence collection is automated?

**Revision links:** [Explainability, fairness, uncertainty, and model governance]({{ '/interview-prep/cheat-sheets/explainability-fairness-uncertainty-model-governance/' | relative_url }})

### AIE-B9-20 — Diagnose a fairness dashboard whose group gaps changed overnight with no model release.

**Round:** Model-assurance incident · **Depth:** Leadership

**Strong answer signals**

- Freeze decisions and verify metric code, group mapping, join grain, threshold/policy, label maturity, eligibility/exposure and data/backfill versions before interpreting harm.
- Recompute denominators, confusion rates and calibration from known-good snapshots; separate telemetry or population shift from real decision/outcome change and quantify affected users.
- Correct or roll back instrumentation or policy, notify responsible owners, preserve audit evidence, and add schema, mapping, late-label and minimum-support regression gates.

**Follow-up probe:** How can a label backfill move equalized-odds metrics without changing any historical prediction?

**Revision links:** [Explainability, fairness, uncertainty, and model governance]({{ '/interview-prep/cheat-sheets/explainability-fairness-uncertainty-model-governance/' | relative_url }})

## Completion evidence

- You can answer at least 16 of 20 questions in each batch without reading the signals first.
- Every answer includes one relevant metric, constraint, failure mode, or project example.
- You can compress an applied answer from two minutes to 45 seconds without losing the decision.
- You have recorded weak areas against the stable question IDs for later re-testing.
