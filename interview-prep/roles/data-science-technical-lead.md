---
layout: "week"
status: "review"
version: "1.8.0"
last_reviewed: "2026-11-10"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "Data Science Technical Lead foundation interview bank"
description: "One hundred eighty guided questions for Data Science Technical Lead interviews."
summary: "Practise AI and data leadership across experimentation, vision and graph strategy, responsible-ML governance, survival/risk/pricing decisions, optimization, delivery, and business outcomes."
permalink: "/interview-prep/roles/data-science-technical-lead/"
kicker_primary: "Data Science Technical Lead"
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

**Bank size:** 180 questions across Batches 1–9 · **Status:** Batches 1–8 approved · Batch 9 review candidate

## Problem framing

### DSTL-B1-01 — Turn an ambiguous request to reduce churn into a model-ready problem.

**Round:** Case · **Depth:** Foundation

**Strong answer signals**

- Define user, decision, prediction unit, observation time, target, horizon, and intervention.
- Establish the current business baseline and cost/capacity constraints.
- Separate churn propensity from treatment effect when outreach changes outcomes.

**Follow-up probe:** What label would you reject even if it is easy to calculate?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }})

### DSTL-B1-02 — When is a rule or dashboard better than a machine-learning model?

**Round:** Case · **Depth:** Applied

**Strong answer signals**

- Use the simplest approach that meets decision quality, latency, and maintenance needs.
- Rules are strong when policy is explicit, data is sparse, and exceptions require auditability.
- Require measured incremental value over the baseline before accepting model complexity.

**Follow-up probe:** How would you design a challenger test?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

## Data reasoning

### DSTL-B1-03 — Why must you declare table grain before writing an analytical query?

**Round:** SQL · **Depth:** Foundation

**Strong answer signals**

- Grain defines what one row represents and which keys should be unique.
- It prevents one-to-many joins from multiplying facts and corrupting denominators.
- It guides aggregation, window partitions, and point-in-time joins.

**Follow-up probe:** Give an example where two valid tables have incompatible grains.

**Revision links:** [SQL]({{ '/interview-prep/cheat-sheets/sql/' | relative_url }})

### DSTL-B1-04 — How do you build a point-in-time correct feature from transaction history?

**Round:** SQL · **Depth:** Applied

**Strong answer signals**

- Anchor every feature to the prediction timestamp.
- Filter events to those available at that time and preserve effective/arrival timing.
- Validate with temporal tests and exclude late corrections unavailable online.

**Follow-up probe:** How would you handle slowly changing customer attributes?

**Revision links:** [SQL]({{ '/interview-prep/cheat-sheets/sql/' | relative_url }}) · [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }})

### DSTL-B1-05 — A KPI changes after a schema migration although row counts look similar. How do you investigate?

**Round:** SQL · **Depth:** Applied

**Strong answer signals**

- Compare definitions, keys, null semantics, filters, units, time zones, and late-arrival rules.
- Reconcile aggregates across old/new paths using controlled snapshots and key-level samples.
- Treat metric ownership and semantic contracts as part of the migration.

**Follow-up probe:** What would make you stop the rollout?

**Revision links:** [SQL]({{ '/interview-prep/cheat-sheets/sql/' | relative_url }})

## Statistics and experimentation

### DSTL-B1-06 — Explain p-value, confidence interval, effect size, and power without mixing them up.

**Round:** Statistics · **Depth:** Foundation

**Strong answer signals**

- P-value measures extremeness under the null; it is not the probability the null is true.
- A confidence interval gives a range from a long-run coverage procedure and conveys precision.
- Effect size addresses practical magnitude; power is the probability of detecting a specified effect under assumptions.

**Follow-up probe:** Which quantity should drive a product decision when they disagree?

**Revision links:** [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

### DSTL-B1-07 — Design an A/B test for a new recommendation model.

**Round:** Experimentation · **Depth:** Applied

**Strong answer signals**

- Choose randomization unit, eligibility, exposure, primary outcome, guardrails, and analysis window.
- Predefine minimum useful effect, sample size, stopping rule, and treatment policy.
- Check balance, sample-ratio mismatch, novelty, interference, attrition, and heterogeneous effects.

**Follow-up probe:** What if users interact across treatment groups?

**Revision links:** [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

### DSTL-B1-08 — A stakeholder wants to stop an experiment early because the dashboard is positive. What do you do?

**Round:** Experimentation · **Depth:** Lead

**Strong answer signals**

- Explain peeking and the inflated false-positive risk under a fixed-horizon design.
- Use a pre-agreed sequential method or continue to the planned information threshold.
- Report uncertainty, guardrails, operational events, and practical significance.

**Follow-up probe:** When is stopping early still the right decision?

**Revision links:** [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

## Model development

### DSTL-B1-09 — Explain bias versus variance and how you diagnose each.

**Round:** ML · **Depth:** Foundation

**Strong answer signals**

- High bias appears as poor train and validation performance; high variance as strong train but weak validation.
- Use learning curves, simpler/stronger models, regularization, data, and error analysis.
- Separate model variance from invalid splits, leakage, or label noise.

**Follow-up probe:** Why can a more complex model have both lower bias and lower observed variance?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }})

### DSTL-B1-10 — Choose between logistic regression and gradient-boosted trees for a risk model.

**Round:** ML · **Depth:** Applied

**Strong answer signals**

- Compare baseline quality, nonlinearities, calibration, interpretability, latency, data size, and maintenance.
- Use leakage-safe validation and threshold decisions tied to cost.
- Do not assume the more complex model wins; quantify incremental value and explanation needs.

**Follow-up probe:** How would regulated review change your recommendation?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

### DSTL-B1-11 — For 1% positives and limited review capacity, which metrics matter?

**Round:** Metrics · **Depth:** Applied

**Strong answer signals**

- Use precision/recall or PR-AUC, plus precision@K and recall@K at capacity.
- Select threshold with false-positive, false-negative, and review costs.
- Check calibration, prevalence, subgroup performance, and confidence intervals.

**Follow-up probe:** Why is 99% accuracy nearly useless here?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

### DSTL-B1-12 — How do you select a split strategy for customer and time-dependent data?

**Round:** Validation · **Depth:** Applied

**Strong answer signals**

- Match deployment: train on past and validate on future.
- Keep the same entity out of train and validation when memorization is possible.
- Fit preprocessing and feature selection inside each fold; protect a final test period.

**Follow-up probe:** When would nested cross-validation be worth the cost?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }})

### DSTL-B1-13 — Why can a high-AUC model still be unusable for decisions?

**Round:** Calibration · **Depth:** Applied

**Strong answer signals**

- AUC measures ranking, not probability accuracy or an operating threshold.
- Costs, capacity, calibration, subgroup behavior, and stability determine usefulness.
- Validate probabilities and choose thresholds on representative data.

**Follow-up probe:** How would class weighting affect calibration?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

## Production and governance

### DSTL-B1-14 — Differentiate data drift, concept drift, and performance degradation.

**Round:** Monitoring · **Depth:** Applied

**Strong answer signals**

- Data drift changes input distribution; concept drift changes the target relationship.
- Performance degradation is measured on outcomes and may occur with or without a drift alert.
- Use drift for diagnosis, not automatic retraining; require validation and rollout gates.

**Follow-up probe:** What do you monitor before labels arrive?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

### DSTL-B1-15 — Design the release path for a new scoring model.

**Round:** System design · **Depth:** Lead

**Strong answer signals**

- Version data, features, code, model, thresholds, and contracts.
- Run offline gates, shadow or canary evaluation, human acceptance, and rollback-ready deployment.
- Monitor service, data, model, business, and fairness signals with clear ownership.

**Follow-up probe:** What must be reversible within minutes?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [Python]({{ '/interview-prep/cheat-sheets/python/' | relative_url }})

### DSTL-B1-16 — How do you communicate SHAP or feature importance responsibly?

**Round:** Explainability · **Depth:** Lead

**Strong answer signals**

- Describe model behavior, not causal effect.
- State the background data, correlation limitations, stability, and local/global scope.
- Pair explanations with error analysis, calibration, subgroup evidence, and domain review.

**Follow-up probe:** What would make an explanation misleading even if computed correctly?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

## Leadership

### DSTL-B1-17 — Your team has five model ideas and capacity for two. How do you prioritize?

**Round:** Prioritization · **Depth:** Lead

**Strong answer signals**

- Rank by decision value, feasibility, data readiness, risk, time to evidence, and reuse.
- Fund a baseline or discovery spike before large build commitments.
- Make trade-offs explicit, preserve stakeholder input, and define stop criteria.

**Follow-up probe:** How do you handle a politically important but low-evidence request?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

### DSTL-B1-18 — Two senior scientists disagree on model architecture. How do you resolve it?

**Round:** Technical disagreement · **Depth:** Lead

**Strong answer signals**

- Clarify the decision criteria and constraints before debating algorithms.
- Design the smallest fair experiment using shared data, metrics, and failure slices.
- Document the decision, dissent, follow-up trigger, and owner.

**Follow-up probe:** What if the statistically better model is operationally worse?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }})

### DSTL-B1-19 — How do you review a junior scientist's unexpectedly high validation score?

**Round:** Mentoring · **Depth:** Lead

**Strong answer signals**

- Start with target timing, duplicates, entity/time overlap, preprocessing leakage, and split design.
- Reproduce the pipeline and compare with simple baselines and ablations.
- Teach the reasoning without taking ownership away; add tests and review checkpoints.

**Follow-up probe:** Which evidence would persuade you the result is genuine?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [SQL]({{ '/interview-prep/cheat-sheets/sql/' | relative_url }})

### DSTL-B1-20 — Describe a project that failed or underperformed.

**Round:** Project deep dive · **Depth:** Lead

**Strong answer signals**

- Own the decision and explain assumptions, evidence, warning signals, and business impact.
- Separate technical, data, product, and execution causes.
- Show the corrective action, reusable learning, and how future gates changed.

**Follow-up probe:** What would you do differently with half the original time?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

## Batch 2 · Deep learning

### DSTL-B2-01 — When should a Data Science team choose deep learning over trees or linear models?

**Round:** Model strategy · **Depth:** Lead

**Strong answer signals**

- Require a problem where representation learning, scale, unstructured data, or transfer provides measurable value.
- Compare against strong simple baselines under the same split, metrics, latency, cost, interpretability, and maintenance constraints.
- Factor data volume/quality, skills, hardware, iteration speed, and operational risk into the decision.

**Follow-up probe:** What evidence would make you reverse the deep-learning decision?

**Revision links:** [Deep learning]({{ '/interview-prep/cheat-sheets/deep-learning-neural-networks/' | relative_url }})

### DSTL-B2-02 — What must be versioned to reproduce a neural-network experiment?

**Round:** Training governance · **Depth:** Applied

**Strong answer signals**

- Data snapshot and split, labels, preprocessing, augmentation, tokenizer where relevant, code, config, seed, environment, and hardware/runtime.
- Architecture, initialization, optimizer, schedule, batch/accumulation, precision, checkpoints, and stopping rule.
- Metrics, slices, artifacts, and provenance; a random seed alone does not guarantee bitwise reproducibility.

**Follow-up probe:** Which differences are acceptable if exact reproducibility is impossible?

**Revision links:** [Deep learning]({{ '/interview-prep/cheat-sheets/deep-learning-neural-networks/' | relative_url }})

### DSTL-B2-03 — How would you review a neural model that fails to learn?

**Round:** Debugging · **Depth:** Lead

**Strong answer signals**

- Verify labels, target alignment, input ranges, loss/activation compatibility, and a tiny-batch overfit test.
- Inspect gradients, activations, learning rate, initialization, frozen parameters, precision, and data-loader behavior.
- Compare with a trivial baseline and simplify until the failure boundary is isolated.

**Follow-up probe:** Why is overfitting a tiny sample a useful diagnostic?

**Revision links:** [Deep learning]({{ '/interview-prep/cheat-sheets/deep-learning-neural-networks/' | relative_url }})

### DSTL-B2-04 — Decide between frozen features, partial unfreezing, and full fine-tuning.

**Round:** Transfer learning · **Depth:** Applied

**Strong answer signals**

- Start from task/data similarity, label volume, compute, latency, and catastrophic-forgetting risk.
- Frozen features are cheapest; partial unfreezing adapts later layers; full fine-tuning offers capacity at greater cost/risk.
- Use staged experiments, discriminative learning rates where appropriate, and a held-out evaluation.

**Follow-up probe:** How would domain shift change your plan?

**Revision links:** [Deep learning]({{ '/interview-prep/cheat-sheets/deep-learning-neural-networks/' | relative_url }})

### DSTL-B2-05 — What production metrics matter for a neural model beyond accuracy?

**Round:** Production · **Depth:** Lead

**Strong answer signals**

- Latency percentiles, throughput, saturation, memory, cost, availability, and fallback behavior.
- Calibration, subgroup errors, robustness, drift, and delayed business outcomes.
- Model/data versions, rollback, hardware/kernel compatibility, and operational ownership.

**Follow-up probe:** Which metric could block deployment even when offline quality improves?

**Revision links:** [Deep learning]({{ '/interview-prep/cheat-sheets/deep-learning-neural-networks/' | relative_url }})

## Batch 2 · NLP

### DSTL-B2-06 — Frame an enterprise text-classification problem with ambiguous and evolving labels.

**Round:** Problem framing · **Depth:** Applied

**Strong answer signals**

- Define decision, taxonomy owner, multilabel/unknown behavior, annotation policy, and escalation path.
- Establish classical baseline, representative time/source/language splits, and label-quality audits.
- Version taxonomy and map migrations; monitor new intents, ambiguity, and reviewer disagreement.

**Follow-up probe:** How would you measure taxonomy quality separately from model quality?

**Revision links:** [NLP]({{ '/interview-prep/cheat-sheets/nlp/' | relative_url }})

### DSTL-B2-07 — How do you build a trustworthy NLP labeling program?

**Round:** Data strategy · **Depth:** Lead

**Strong answer signals**

- Create operational definitions, positive/negative examples, edge cases, and adjudication rules.
- Measure inter-annotator agreement by label and slice; sample for coverage rather than convenience.
- Protect privacy, version instructions and datasets, audit disagreements, and feed model errors back without contaminating evaluation.

**Follow-up probe:** What does low agreement tell you before model training?

**Revision links:** [NLP]({{ '/interview-prep/cheat-sheets/nlp/' | relative_url }})

### DSTL-B2-08 — Choose among translation, multilingual models, and language-specific models.

**Round:** Multilingual systems · **Depth:** Lead

**Strong answer signals**

- Compare language coverage, label availability, privacy, domain terms, latency, cost, and maintenance.
- Translation centralizes modeling but adds errors and dependency; multilingual models share capacity; specialist models may win critical languages.
- Evaluate per language and dialect with fallback/review paths; never report only an aggregate.

**Follow-up probe:** How do you prioritize languages for launch?

**Revision links:** [NLP]({{ '/interview-prep/cheat-sheets/nlp/' | relative_url }})

### DSTL-B2-09 — Why can BLEU, ROUGE, or perplexity be insufficient for a business NLP system?

**Round:** Evaluation · **Depth:** Applied

**Strong answer signals**

- Reference-overlap or likelihood metrics may not capture factuality, task completion, safety, or usefulness.
- Pair automatic metrics with task-specific checks, human rubrics, error slices, and operational outcomes.
- Define the decision each metric supports and avoid cross-dataset comparisons without context.

**Follow-up probe:** What metric would you use for entity extraction versus summarization?

**Revision links:** [NLP]({{ '/interview-prep/cheat-sheets/nlp/' | relative_url }})

## Batch 2 · Transformers

### DSTL-B2-10 — How do you explain transformer-family choice to a product team?

**Round:** Architecture choice · **Depth:** Lead

**Strong answer signals**

- Map encoder, decoder, or encoder-decoder strengths to the task and output contract.
- Compare quality, context, latency, memory, throughput, fine-tuning data, licensing, and deployment environment.
- Use workload benchmarks and a simple baseline; do not choose by parameter count alone.

**Follow-up probe:** Which family would you shortlist for high-throughput classification?

**Revision links:** [Transformers]({{ '/interview-prep/cheat-sheets/transformers/' | relative_url }}) · [NLP]({{ '/interview-prep/cheat-sheets/nlp/' | relative_url }})

### DSTL-B2-11 — Why does a longer context window not automatically solve document understanding?

**Round:** Capacity planning · **Depth:** Lead

**Strong answer signals**

- Attention cost, KV memory, latency, and lost-in-the-middle behavior grow with context.
- Irrelevant or conflicting text can reduce quality; position and truncation policies matter.
- Retrieval, chunking, summaries, and task-specific long-context evaluation remain necessary.

**Follow-up probe:** What experiment compares long context with retrieval fairly?

**Revision links:** [Transformers]({{ '/interview-prep/cheat-sheets/transformers/' | relative_url }})

### DSTL-B2-12 — Explain prefill versus decode and why the distinction matters commercially.

**Round:** Inference economics · **Depth:** Applied

**Strong answer signals**

- Prefill processes the input largely in parallel and scales with prompt length; decode generates tokens sequentially.
- They stress compute, memory bandwidth, KV cache, and batching differently.
- Cost and capacity planning need input/output distributions, concurrency, latency SLOs, and cache memory—not only average tokens.

**Follow-up probe:** How would very long outputs change your bottleneck?

**Revision links:** [Transformers]({{ '/interview-prep/cheat-sheets/transformers/' | relative_url }}) · [LLM and Generative AI]({{ '/interview-prep/cheat-sheets/llm-generative-ai/' | relative_url }})

### DSTL-B2-13 — A smaller GQA model nearly matches a larger MHA model. What evidence decides deployment?

**Round:** Model comparison · **Depth:** Applied

**Strong answer signals**

- Compare task/safety slices, calibration, robustness, context behavior, and statistical uncertainty.
- Benchmark latency percentiles, throughput, concurrency, memory, power, and total cost on target hardware.
- Include licensing, tooling, quantization support, operational maturity, and rollback.

**Follow-up probe:** How would traffic shape alter the winner?

**Revision links:** [Transformers]({{ '/interview-prep/cheat-sheets/transformers/' | relative_url }})

## Batch 2 · LLM and Generative AI

### DSTL-B2-14 — A stakeholder asks to replace every classifier with an LLM. How do you respond?

**Round:** GenAI strategy · **Depth:** Lead

**Strong answer signals**

- Return to decisions, error costs, explainability, latency, privacy, and current baseline.
- Use LLMs where language variability or low-shot flexibility creates measured value; retain deterministic or smaller models where they meet the contract.
- Propose a bounded comparison with explicit quality, safety, cost, and operational gates.

**Follow-up probe:** Which use case would you reject immediately and why?

**Revision links:** [LLM and Generative AI]({{ '/interview-prep/cheat-sheets/llm-generative-ai/' | relative_url }})

### DSTL-B2-15 — Choose among prompt engineering, RAG, LoRA/QLoRA, and full fine-tuning.

**Round:** Adaptation strategy · **Depth:** Lead

**Strong answer signals**

- Diagnose whether the gap is instruction, knowledge, domain language, output style, or model capability.
- Choose the least complex intervention and define data/evaluation requirements before training.
- Account for freshness, privacy, serving compatibility, rollback, and continuous maintenance.

**Follow-up probe:** What result would prove fine-tuning was unnecessary?

**Revision links:** [LLM and Generative AI]({{ '/interview-prep/cheat-sheets/llm-generative-ai/' | relative_url }})

### DSTL-B2-16 — Design an organization-wide LLM evaluation program.

**Round:** Evaluation program · **Depth:** Lead

**Strong answer signals**

- Create versioned use-case datasets with deterministic metrics, human rubrics, safety cases, slices, and baselines.
- Separate development, release, and audit sets; control contamination and judge versions.
- Define owners, severity gates, review cadence, cost/latency budgets, regression triage, and promotion/rollback evidence.

**Follow-up probe:** How do teams contribute cases without turning the set into an ungoverned dump?

**Revision links:** [LLM and Generative AI]({{ '/interview-prep/cheat-sheets/llm-generative-ai/' | relative_url }})

### DSTL-B2-17 — What are the limits of LLM-as-judge?

**Round:** LLM-as-judge · **Depth:** Applied

**Strong answer signals**

- Judges can be position-, verbosity-, style-, model-, and prompt-biased and may miss domain errors.
- Calibrate against blinded human labels, randomize order, use explicit rubrics, measure agreement, and retain raw reasons.
- Use judges as one signal, not sole authority for safety or high-stakes correctness.

**Follow-up probe:** When is pairwise judging stronger than absolute scoring?

**Revision links:** [LLM and Generative AI]({{ '/interview-prep/cheat-sheets/llm-generative-ai/' | relative_url }})

### DSTL-B2-18 — How do you evaluate hosted versus self-hosted LLMs for a portfolio of use cases?

**Round:** Build versus buy · **Depth:** Lead

**Strong answer signals**

- Segment workloads by quality, sensitivity, latency, context, volume, and availability needs.
- Model total cost including idle capacity, engineering, upgrades, monitoring, support, and provider risk.
- Run representative benchmarks and design routing/fallback so the decision is not irreversible.

**Follow-up probe:** Which data-handling fact could override a cheaper option?

**Revision links:** [LLM and Generative AI]({{ '/interview-prep/cheat-sheets/llm-generative-ai/' | relative_url }})

### DSTL-B2-19 — How do you prevent framework enthusiasm from driving architecture?

**Round:** Leadership · **Depth:** Lead

**Strong answer signals**

- Require a problem statement, baseline, measurable success, and explicit constraints before tool selection.
- Use small reversible spikes and architecture decision records comparing alternatives.
- Set standards for evaluation, security, ownership, operability, and decommissioning.

**Follow-up probe:** How do you keep innovation speed without creating platform sprawl?

**Revision links:** [LLM and Generative AI]({{ '/interview-prep/cheat-sheets/llm-generative-ai/' | relative_url }}) · [Transformers]({{ '/interview-prep/cheat-sheets/transformers/' | relative_url }})

### DSTL-B2-20 — A model upgrade silently changes output behavior across teams. What do you do?

**Round:** Incident leadership · **Depth:** Lead

**Strong answer signals**

- Freeze or roll back routing, identify affected versions/use cases, and communicate scope.
- Replay versioned cases, compare schemas/safety/task slices, and reconcile downstream effects.
- Add pinning, compatibility contracts, canaries, change notices, and release ownership before retrying.

**Follow-up probe:** Which evidence determines whether the upgrade can be restored safely?

**Revision links:** [LLM and Generative AI]({{ '/interview-prep/cheat-sheets/llm-generative-ai/' | relative_url }})


## Batch 3 · Embeddings and vector search

### DSTL-B3-01 — When should a team choose sparse, dense, or hybrid retrieval?

**Round:** Technical strategy · **Depth:** Applied

**Strong answer signals**

- Start from query types, corpus language, exact-token needs, semantic variation, freshness, latency, and permission constraints.
- Use sparse retrieval for strong lexical signals, dense retrieval for semantic matching, and hybrid only when evaluation shows complementary gains.
- Define a representative benchmark and operational budget before selecting an architecture or vendor.

**Follow-up probe:** Which query slices would you use to prove that hybrid retrieval adds value?

**Revision links:** [Embeddings and vector search]({{ '/interview-prep/cheat-sheets/embeddings-vector-search/' | relative_url }})

### DSTL-B3-02 — Lead the selection of an embedding model for a multilingual enterprise corpus.

**Round:** Model selection · **Depth:** Advanced

**Strong answer signals**

- Define languages, domains, query-document asymmetry, context length, vector size, licensing, hosting, privacy, and cost constraints.
- Evaluate on in-domain relevance judgments and hard negatives by language and business slice, not only public leaderboard averages.
- Include index size, encoding throughput, migration effort, versioning, and rollback in the decision record.

**Follow-up probe:** How would you handle a model that wins overall but regresses the lowest-volume language?

**Revision links:** [Embeddings and vector search]({{ '/interview-prep/cheat-sheets/embeddings-vector-search/' | relative_url }})

### DSTL-B3-03 — Define the evaluation and acceptance criteria for a new ANN index.

**Round:** Quality governance · **Depth:** Advanced

**Strong answer signals**

- Create exact-search ground truth and measure recall@K, ranking quality, filtered-query correctness, latency percentiles, throughput, and memory.
- Set slice-specific thresholds for tenants, languages, document types, and rare-query classes rather than relying on a single average.
- Require repeatable index builds, versioned parameters, capacity evidence, and a rollback path before production approval.

**Follow-up probe:** Why is end-to-end answer quality alone insufficient for approving an ANN change?

**Revision links:** [Embeddings and vector search]({{ '/interview-prep/cheat-sheets/embeddings-vector-search/' | relative_url }})

### DSTL-B3-04 — How do you govern authorization metadata in a retrieval platform shared by teams?

**Round:** Governance · **Depth:** Leadership

**Strong answer signals**

- Define canonical ownership and semantics for tenant, principal, classification, retention, and source-access fields.
- Make missing or invalid authorization metadata fail closed and test enforcement across ingestion, retrieval, caches, and context assembly.
- Audit schema changes, access decisions, and index synchronization while minimizing sensitive data in logs.

**Follow-up probe:** Which team should own a permission-field migration, and what evidence must they provide?

**Revision links:** [Embeddings and vector search]({{ '/interview-prep/cheat-sheets/embeddings-vector-search/' | relative_url }}) · [RAG security and production]({{ '/interview-prep/cheat-sheets/rag-evaluation-security-production/' | relative_url }})

### DSTL-B3-05 — Make a build-versus-buy decision for the vector-search layer.

**Round:** Architecture decision · **Depth:** Leadership

**Strong answer signals**

- Compare required scale, filtering, hybrid search, consistency, tenancy, availability, observability, portability, and team operating capability.
- Model total cost including data movement, replicas, index rebuilds, support, incident load, and exit or migration cost.
- Run a bounded proof against the real corpus and workload, then record assumptions, rejected options, and review triggers.

**Follow-up probe:** What requirement would make a seemingly cheaper managed service unacceptable?

**Revision links:** [Embeddings and vector search]({{ '/interview-prep/cheat-sheets/embeddings-vector-search/' | relative_url }})


## Batch 3 · Document ingestion, chunking, and indexing

### DSTL-B3-06 — Define contracts and ownership for a multi-source ingestion program.

**Round:** Platform leadership · **Depth:** Leadership

**Strong answer signals**

- Inventory sources, owners, formats, update and deletion semantics, permissions, data quality, retention, and expected service levels.
- Define a canonical document model and versioned stage contracts for parsing, provenance, chunking, embedding, indexing, and publication.
- Assign operational ownership, reconciliation metrics, quarantine handling, replay procedures, and change-review triggers.

**Follow-up probe:** What should happen when a source owner cannot provide reliable deletion events?

**Revision links:** [Ingestion, chunking, and indexing]({{ '/interview-prep/cheat-sheets/document-ingestion-chunking-indexing/' | relative_url }})

### DSTL-B3-07 — Design an experiment to choose chunking strategy and size.

**Round:** Experimentation · **Depth:** Advanced

**Strong answer signals**

- Hold the corpus, embedding model, retriever, and evaluator stable while comparing structural, semantic, parent-child, and fixed-window variants.
- Measure retrieval relevance, evidence completeness, citation precision, answer quality, latency, index size, and duplicate concentration.
- Analyze results by document type and query class, then select a policy with explicit exceptions rather than one global number.

**Follow-up probe:** How would you prevent the evaluation answers from leaking into the chunking decision?

**Revision links:** [Ingestion, chunking, and indexing]({{ '/interview-prep/cheat-sheets/document-ingestion-chunking-indexing/' | relative_url }})

### DSTL-B3-08 — Establish lineage, deletion, and retention controls for a RAG corpus.

**Round:** Data governance · **Depth:** Advanced

**Strong answer signals**

- Trace every chunk to source identity, source version, parser, chunker, embedding model, index version, and access policy.
- Define deterministic deletion and replacement behavior across raw storage, derived artifacts, indexes, caches, backups, and evaluation samples.
- Prove controls with reconciliation and negative retrieval tests, while documenting legal or policy owners for retention decisions.

**Follow-up probe:** How do you demonstrate that a deleted source is no longer answerable from stale caches?

**Revision links:** [Ingestion, chunking, and indexing]({{ '/interview-prep/cheat-sheets/document-ingestion-chunking-indexing/' | relative_url }})

### DSTL-B3-09 — Scope support for tables, images, and scanned documents.

**Round:** Product scoping · **Depth:** Leadership

**Strong answer signals**

- Start from user tasks and evidence requirements, then measure how often each content type affects critical answers.
- Compare native extraction, OCR, layout-aware parsing, table serialization, multimodal models, and human fallback with quality and cost evidence.
- Ship explicit supported and unsupported cases with confidence checks instead of implying universal document understanding.

**Follow-up probe:** When is excluding a difficult document type the responsible product decision?

**Revision links:** [Ingestion, chunking, and indexing]({{ '/interview-prep/cheat-sheets/document-ingestion-chunking-indexing/' | relative_url }})

### DSTL-B3-10 — Plan capacity and change management for incremental indexing.

**Round:** Delivery planning · **Depth:** Advanced

**Strong answer signals**

- Forecast source growth, update bursts, embedding throughput, index-build time, storage, replicas, and deletion or compaction work.
- Separate freshness SLOs from backfill objectives and reserve capacity for retries, migrations, and incident replay.
- Use versioned shadow indexes, reconciliation gates, controlled cutover, and observable rollback for material changes.

**Follow-up probe:** Which freshness metric would you present to a business owner?

**Revision links:** [Ingestion, chunking, and indexing]({{ '/interview-prep/cheat-sheets/document-ingestion-chunking-indexing/' | relative_url }})


## Batch 3 · RAG architecture, retrieval, and generation

### DSTL-B3-11 — Choose among RAG, fine-tuning, long-context prompting, and deterministic search.

**Round:** Solution framing · **Depth:** Leadership

**Strong answer signals**

- Separate knowledge freshness, behavior adaptation, reasoning, exact lookup, latency, cost, privacy, and audit requirements.
- Prefer the simplest approach that satisfies the task, and combine techniques only when their distinct contribution is measurable.
- Define baselines, excluded uses, evaluation criteria, and an exit path before committing to a platform.

**Follow-up probe:** What problem does fine-tuning solve that document retrieval does not?

**Revision links:** [RAG architecture]({{ '/interview-prep/cheat-sheets/rag-architecture-retrieval-generation/' | relative_url }})

### DSTL-B3-12 — Review a proposed RAG architecture before implementation.

**Round:** Architecture review · **Depth:** Advanced

**Strong answer signals**

- Trace authenticated scope, ingestion lineage, retrieval, authorization, reranking, context assembly, generation, citations, and feedback end to end.
- Challenge hidden coupling, unbounded fan-out, silent fallbacks, provider lock-in, sensitive logging, and missing deletion or rollback paths.
- Require measurable contracts for quality, latency, cost, safety, ownership, and failure behavior at each boundary.

**Follow-up probe:** Which architecture gap is most likely to appear only after the first production incident?

**Revision links:** [RAG architecture]({{ '/interview-prep/cheat-sheets/rag-architecture-retrieval-generation/' | relative_url }})

### DSTL-B3-13 — Set stage-level budgets and contracts across retrieval, reranking, and generation teams.

**Round:** Cross-team delivery · **Depth:** Leadership

**Strong answer signals**

- Translate the user SLO and quality target into bounded latency, candidate, token, cost, and error budgets for each stage.
- Define versioned request and response schemas, provenance fields, timeout behavior, degradation modes, and owner-facing dashboards.
- Use integration and replay tests to prevent one team's optimization from silently shifting cost or quality to another stage.

**Follow-up probe:** How would you resolve a dispute between retrieval recall and generation latency owners?

**Revision links:** [RAG architecture]({{ '/interview-prep/cheat-sheets/rag-architecture-retrieval-generation/' | relative_url }})

### DSTL-B3-14 — Define product behavior for answerability, abstention, and citations.

**Round:** Product-quality decision · **Depth:** Leadership

**Strong answer signals**

- Agree on which tasks require evidence, which sources are authoritative, and what insufficient or conflicting evidence should look like to users.
- Set separate costs and thresholds for false answers and false abstentions by risk tier.
- Validate citation support and usability with domain reviewers, and provide escalation or search-result alternatives where needed.

**Follow-up probe:** When should the system return sources without synthesizing an answer?

**Revision links:** [RAG architecture]({{ '/interview-prep/cheat-sheets/rag-architecture-retrieval-generation/' | relative_url }}) · [RAG evaluation]({{ '/interview-prep/cheat-sheets/rag-evaluation-security-production/' | relative_url }})

### DSTL-B3-15 — Govern conversation memory and personalization in a RAG product.

**Round:** Privacy and product design · **Depth:** Leadership

**Strong answer signals**

- Define which data is session-only, durable, user-editable, derived, or prohibited, with explicit consent and retention rules.
- Keep memory separate from authoritative retrieved evidence and reapply tenant and permission checks on every request.
- Evaluate topic shifts, stale preferences, shared accounts, deletion, correction, and personalization harms across user slices.

**Follow-up probe:** Who owns the decision to retain a derived user preference, and what evidence is required?

**Revision links:** [RAG architecture]({{ '/interview-prep/cheat-sheets/rag-architecture-retrieval-generation/' | relative_url }}) · [RAG security and production]({{ '/interview-prep/cheat-sheets/rag-evaluation-security-production/' | relative_url }})


## Batch 3 · RAG evaluation, security, and production

### DSTL-B3-16 — Build a sustainable RAG evaluation program rather than a one-time benchmark.

**Round:** Evaluation leadership · **Depth:** Leadership

**Strong answer signals**

- Create governed datasets from real tasks with representative, long-tail, unanswerable, adversarial, permission, and regression cases.
- Assign owners for labels, metric definitions, judge calibration, slice coverage, dataset versioning, and release thresholds.
- Connect offline component metrics, human review, online feedback, incidents, and drift monitoring without treating any one signal as truth.

**Follow-up probe:** How do you prevent the benchmark from becoming overfitted and unrepresentative?

**Revision links:** [RAG evaluation and production]({{ '/interview-prep/cheat-sheets/rag-evaluation-security-production/' | relative_url }})

### DSTL-B3-17 — Define a release gate for a major RAG change.

**Round:** Release governance · **Depth:** Advanced

**Strong answer signals**

- Require versioned candidate identity, reproducible component and end-to-end evaluation, security tests, capacity evidence, and rollback readiness.
- Set non-compensating thresholds for critical permissions, safety, and high-risk slices alongside aggregate quality, latency, and cost targets.
- Use ablations, shadow traffic, or canaries where safe, and record acceptance, known limitations, and post-release monitoring owners.

**Follow-up probe:** Which regression should block release even if business-success metrics improve?

**Revision links:** [RAG evaluation and production]({{ '/interview-prep/cheat-sheets/rag-evaluation-security-production/' | relative_url }})

### DSTL-B3-18 — Create a threat model for enterprise RAG.

**Round:** AI security leadership · **Depth:** Advanced

**Strong answer signals**

- Map assets, trust boundaries, actors, and data flows across sources, ingestion, indexes, retrieval, prompts, models, tools, caches, and logs.
- Cover poisoning, indirect prompt injection, cross-tenant retrieval, exfiltration, malicious files, citation spoofing, denial of service, and supply-chain risk.
- Assign preventive, detective, and recovery controls with owners and executable adversarial tests.

**Follow-up probe:** Which control remains necessary even if the model is highly resistant to prompt injection?

**Revision links:** [RAG security and production]({{ '/interview-prep/cheat-sheets/rag-evaluation-security-production/' | relative_url }})

### DSTL-B3-19 — Define production ownership and SLOs for a cross-team RAG platform.

**Round:** Operating model · **Depth:** Leadership

**Strong answer signals**

- Name owners for sources, ingestion, retrieval, models, prompts, policies, application behavior, incidents, and user support.
- Define availability, latency, freshness, permission correctness, quality-sampling, cost, and recovery objectives with alert and escalation rules.
- Provide runbooks, version inventories, replay tooling, capacity reviews, and post-incident learning rather than relying on individual expertise.

**Follow-up probe:** How would you allocate an error budget when multiple dependencies contribute to one user request?

**Revision links:** [RAG security and production]({{ '/interview-prep/cheat-sheets/rag-evaluation-security-production/' | relative_url }})

### DSTL-B3-20 — A pilot improves average answer quality but harms a regulated workflow. Make the decision.

**Round:** Executive decision · **Depth:** Leadership

**Strong answer signals**

- Separate the regulated slice and its failure cost from the overall average; do not trade mandatory controls for broad gains.
- Verify evidence with domain, risk, and product owners, identify whether scope restriction or remediation can make deployment safe.
- Document the decision, limitations, monitoring, and re-entry criteria; prefer a bounded launch or no-launch when residual risk is unacceptable.

**Follow-up probe:** What evidence would support launching only the low-risk use cases?

**Revision links:** [RAG evaluation and production]({{ '/interview-prep/cheat-sheets/rag-evaluation-security-production/' | relative_url }})

## Agent strategy and operating model

### DSTL-B4-01 — A product team asks for an autonomous agent because competitors have one. Frame the decision.

**Round:** Product architecture · **Depth:** Leadership

**Strong answer signals**

- Start from user outcome, decision uncertainty, consequences, latency, cost, and compliance rather than the requested label.
- Compare deterministic software, an LLM-enhanced workflow, a bounded agent, and a human-assisted baseline.
- Approve autonomy only where model judgment adds measured value within explicit policy, budget, evaluation, and rollback boundaries.

**Follow-up probe:** What evidence would make you reject the agent even if its average task score is higher?

**Revision links:** [Agent fundamentals]({{ '/interview-prep/cheat-sheets/agent-fundamentals-workflow-patterns/' | relative_url }})

### DSTL-B4-02 — Define autonomy tiers and human approval rules for an enterprise agent portfolio.

**Round:** Governance · **Depth:** Advanced

**Strong answer signals**

- Classify actions by reversibility, financial or legal consequence, data sensitivity, blast radius, and confidence.
- Map each tier to allowed tools, limits, evidence, approval, logging, monitoring, and incident ownership.
- Make approval protect consequential actions while keeping low-risk tasks efficient; bind it to an exact, expiring operation.

**Follow-up probe:** How should an agent behave when risk classification is uncertain?

**Revision links:** [Agent fundamentals]({{ '/interview-prep/cheat-sheets/agent-fundamentals-workflow-patterns/' | relative_url }}) · [Protocols and reliability]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }})

### DSTL-B4-03 — Establish ownership for a cross-team agent that uses shared tools and customer data.

**Round:** Operating model · **Depth:** Leadership

**Strong answer signals**

- Name owners for product outcome, prompts and policies, models, tools, data, identity, infrastructure, evaluation, and incidents.
- Define versioned contracts, approval paths, SLOs, error budgets, escalation, and change notification across boundaries.
- Keep a service and risk inventory so no shared capability becomes an unaudited source of authority.

**Follow-up probe:** Who owns a failure caused jointly by a model decision and a stale tool policy?

**Revision links:** [Agent fundamentals]({{ '/interview-prep/cheat-sheets/agent-fundamentals-workflow-patterns/' | relative_url }}) · [Protocols and reliability]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }})

### DSTL-B4-04 — Decide whether a complex workflow needs multiple agents.

**Round:** Architecture review · **Depth:** Advanced

**Strong answer signals**

- Require a concrete need for separate tools, context, policy, ownership, scale, or deployment boundaries.
- Compare with one agent using tools and with deterministic orchestration; account for handoff errors, latency, cost, and observability.
- Demand an ablation, stable contracts, termination rules, and a clear owner for shared state before production use.

**Follow-up probe:** When is a specialist implemented as a tool better than a peer agent?

**Revision links:** [Agent fundamentals]({{ '/interview-prep/cheat-sheets/agent-fundamentals-workflow-patterns/' | relative_url }})

### DSTL-B4-05 — Define success criteria for a customer-service agent pilot.

**Round:** Evaluation strategy · **Depth:** Leadership

**Strong answer signals**

- Link task resolution and user outcome to safety, escalation quality, containment, latency, cost, and agent-assist adoption.
- Build versioned offline cases from real distributions, edge cases, failures, and adversarial scenarios, then validate in shadow or bounded rollout.
- Set slice-specific release gates and stop conditions; an average score cannot offset a critical-policy regression.

**Follow-up probe:** How would you measure whether automation merely shifts work to downstream teams?

**Revision links:** [Agent fundamentals]({{ '/interview-prep/cheat-sheets/agent-fundamentals-workflow-patterns/' | relative_url }}) · [Protocols and reliability]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }})

## LangGraph architecture and durable execution

### DSTL-B4-06 — Review a proposal to use LangGraph for a three-step acyclic summarization pipeline.

**Round:** Architecture review · **Depth:** Applied

**Strong answer signals**

- Ask whether branching, cycles, persistent state, interruption, replay, or dynamic fan-out is actually required.
- Prefer a simple function pipeline or task queue if the flow is short and deterministic.
- Accept LangGraph only when its explicit state and recovery model solves expected complexity at an acceptable operating cost.

**Follow-up probe:** Which future requirement would most strongly change your recommendation?

**Revision links:** [LangGraph deep dive]({{ '/interview-prep/cheat-sheets/langgraph-deep-dive/' | relative_url }})

### DSTL-B4-07 — Set standards for LangGraph state schemas and reducers across teams.

**Round:** Platform governance · **Depth:** Advanced

**Strong answer signals**

- Require typed, minimal state with documented ownership, lifecycle, sensitivity, and serialization compatibility.
- Make concurrent fields use explicit deterministic reducers and keep bulky or regulated payloads behind references.
- Version schemas and migrations, test replay compatibility, and prohibit hidden mutation outside declared updates.

**Follow-up probe:** How would you review a reducer that appears correct only for one update order?

**Revision links:** [LangGraph deep dive]({{ '/interview-prep/cheat-sheets/langgraph-deep-dive/' | relative_url }})

### DSTL-B4-08 — Govern checkpointing, stores, and identity for a multi-tenant LangGraph platform.

**Round:** Data governance · **Depth:** Leadership

**Strong answer signals**

- Separate execution checkpoints from application long-term memory and from authoritative business records.
- Namespace by tenant and subject, enforce authorization independently of `thread_id`, and revalidate access on every resume.
- Define encryption, retention, deletion, legal hold, backup, residency, and restore testing with named owners.

**Follow-up probe:** What should happen to paused threads after a user requests deletion?

**Revision links:** [LangGraph deep dive]({{ '/interview-prep/cheat-sheets/langgraph-deep-dive/' | relative_url }})

### DSTL-B4-09 — A team claims checkpointing gives exactly-once business actions. Challenge the claim.

**Round:** Reliability review · **Depth:** Advanced

**Strong answer signals**

- Explain that durable graph state can replay nodes while a remote side effect may have succeeded before its acknowledgement was lost.
- Require operation IDs, server-side idempotency or deduplication, status reconciliation, and compensation.
- Test crash points around every consequential side effect and document residual ambiguity and manual recovery.

**Follow-up probe:** Which business actions cannot be made safely idempotent and how would you control them?

**Revision links:** [LangGraph deep dive]({{ '/interview-prep/cheat-sheets/langgraph-deep-dive/' | relative_url }}) · [Protocols and reliability]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }})

### DSTL-B4-10 — Define observability and recovery evidence for a long-running LangGraph workflow.

**Round:** Production readiness · **Depth:** Leadership

**Strong answer signals**

- Trace graph and node versions, routes, state deltas, tool attempts, interrupts, budgets, errors, and side-effect identifiers with privacy controls.
- Provide replay or simulation tooling, checkpoint inspection, runbooks, SLOs, alerts, and bounded diagnostic access.
- Prove recovery through fault injection, dependency outages, schema upgrades, pause/resume, and rollback drills.

**Follow-up probe:** Which trace fields are essential for explaining an unexpected routing decision?

**Revision links:** [LangGraph deep dive]({{ '/interview-prep/cheat-sheets/langgraph-deep-dive/' | relative_url }})

## Framework portfolio and migration

### DSTL-B4-11 — Lead a framework-selection RFC for several agent products.

**Round:** Technical strategy · **Depth:** Leadership

**Strong answer signals**

- Inventory common and product-specific needs across control flow, state, HITL, protocols, deployment, evaluation, tracing, security, and support.
- Weight criteria and test representative hard paths with the same fixtures instead of comparing marketing feature counts.
- Record the decision, rejected options, assumptions, exit strategy, ownership, and review triggers.

**Follow-up probe:** When should one organization deliberately support more than one framework?

**Revision links:** [Framework comparison]({{ '/interview-prep/cheat-sheets/agent-frameworks-libraries-comparison/' | relative_url }})

### DSTL-B4-12 — Reduce framework lock-in without building a lowest-common-denominator platform.

**Round:** Platform architecture · **Depth:** Advanced

**Strong answer signals**

- Standardize application-owned tool contracts, identity, policy, telemetry, evaluation cases, and domain state.
- Isolate provider and framework adapters while allowing products to use valuable native orchestration features behind them.
- Track lock-in explicitly through checkpoint formats, message types, hosted services, and migration cost; test an exit path periodically.

**Follow-up probe:** Which abstractions are most likely to become expensive internal frameworks themselves?

**Revision links:** [Framework comparison]({{ '/interview-prep/cheat-sheets/agent-frameworks-libraries-comparison/' | relative_url }})

### DSTL-B4-13 — Assess team and operational fit when choosing between Google ADK, OpenAI Agents SDK, and LangGraph.

**Round:** Delivery strategy · **Depth:** Leadership

**Strong answer signals**

- Match runtime control, durability, cloud or provider constraints, debugging, deployment, and support needs to the product risk.
- Include engineering skill, testability, learning curve, ecosystem maturity, security review, and on-call ownership.
- Fund a time-boxed spike and production-readiness review for the highest-risk workflow before standardizing.

**Follow-up probe:** How would you avoid a prototype benchmark that unfairly favors the team's familiar framework?

**Revision links:** [Framework comparison]({{ '/interview-prep/cheat-sheets/agent-frameworks-libraries-comparison/' | relative_url }})

### DSTL-B4-14 — Choose the primary stack for a data-centric assistant with complex ingestion but limited autonomy.

**Round:** System architecture · **Depth:** Advanced

**Strong answer signals**

- Prioritize ingestion, provenance, retrieval, evaluation, and data operations through LlamaIndex, Haystack, or application-owned pipelines.
- Keep workflow control simple and add an agent SDK only for bounded decisions that show measurable value.
- Define ownership so retrieval, orchestration, caching, observability, and policy are not duplicated across libraries.

**Follow-up probe:** What change in requirements would justify introducing graph orchestration?

**Revision links:** [Framework comparison]({{ '/interview-prep/cheat-sheets/agent-frameworks-libraries-comparison/' | relative_url }})

### DSTL-B4-15 — Plan a safe migration from a deprecated agent framework.

**Round:** Migration leadership · **Depth:** Leadership

**Strong answer signals**

- Inventory APIs, serialized state, prompts, tools, traces, hosted dependencies, and behavior relied on implicitly.
- Freeze a replayable acceptance suite, introduce adapters, migrate low-risk flows first, and run shadow comparisons on identical cases.
- Define compatibility, rollback, data migration, dual-run duration, owner communication, and decommission evidence.

**Follow-up probe:** How would you handle in-flight conversations whose checkpoints use the old framework format?

**Revision links:** [Framework comparison]({{ '/interview-prep/cheat-sheets/agent-frameworks-libraries-comparison/' | relative_url }})

## Protocol governance, reliability, and release

### DSTL-B4-16 — Define an enterprise policy for adopting MCP and A2A.

**Round:** Protocol governance · **Depth:** Leadership

**Strong answer signals**

- Use MCP for governed capability access and A2A for independently deployed agent collaboration only where those boundaries exist.
- Require registry ownership, identity, authorization, versioning, data classification, audit, testing, deprecation, and incident controls.
- Prefer normal APIs or local interfaces for stable services; protocol adoption must reduce integration cost without widening trust implicitly.

**Follow-up probe:** What evidence should a team provide before publishing an MCP server company-wide?

**Revision links:** [Protocols and reliability]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }})

### DSTL-B4-17 — Prevent cross-tenant access across tools, agents, checkpoints, and caches.

**Round:** Security governance · **Depth:** Advanced

**Strong answer signals**

- Propagate authenticated tenant and user context explicitly and authorize at every resource boundary.
- Partition credentials, stores, caches, queues, indexes, and telemetry; do not rely on prompts, model behavior, or thread IDs.
- Add negative isolation tests, policy-decision logs, anomaly detection, and rapid credential revocation.

**Follow-up probe:** Which shared caches are most likely to create subtle tenant leakage?

**Revision links:** [Protocols and reliability]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }})

### DSTL-B4-18 — Set SLOs and resilience requirements for an agent platform with many downstream tools.

**Round:** Reliability leadership · **Depth:** Advanced

**Strong answer signals**

- Define user-facing availability, latency, correctness or safety guardrails, freshness, and cost, then allocate dependency budgets.
- Require deadlines, load shedding, backpressure, circuit breakers, bounded retries, idempotency, and graceful degradation.
- Test capacity, spike, partial outage, recovery, and retry storms; tie error-budget policy to change velocity.

**Follow-up probe:** How do you define success when a response is available but a consequential tool action failed?

**Revision links:** [Protocols and reliability]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }})

### DSTL-B4-19 — Establish release gates for a new agent version.

**Round:** Model and system governance · **Depth:** Leadership

**Strong answer signals**

- Gate versioned offline task, trajectory, safety, adversarial, latency, and cost suites with critical-slice thresholds.
- Calibrate model-based judges, retain deterministic checks and human review, and compare paired cases to the release baseline.
- Use shadow or canary rollout, monitored rollback criteria, exact artifact versions, and accountable approval.

**Follow-up probe:** Which regression should block release even when overall task success improves?

**Revision links:** [Protocols and reliability]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }})

### DSTL-B4-20 — Lead an incident where agent retries amplified a downstream outage.

**Round:** Incident leadership · **Depth:** Leadership

**Strong answer signals**

- Stop amplification through retry suppression, concurrency limits, circuit breaking, queue control, or safe degradation.
- Establish user and data impact, preserve traces, communicate owners and decisions, and recover through bounded probes.
- Correct retry classification, budgets, idempotency, alerts, capacity assumptions, and runbooks; verify with a recurrence test.

**Follow-up probe:** What telemetry would have detected the retry storm before the dependency collapsed?

**Revision links:** [Protocols and reliability]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }})

## AI/ML architecture and product decisions

### DSTL-B5-01 — Lead an ambiguous system-design round for an enterprise AI product.

**Round:** System design leadership · **Depth:** Leadership

**Strong answer signals**

- Clarify users, decision or action, failure cost, risk, non-goals, scale, latency, freshness, residency, and budget with explicit assumptions.
- Define business, product, model, safety, service, and cost metrics plus a credible non-AI or simpler baseline.
- Evolve from a bounded first release to control and serving planes with ownership, validation, rollout, monitoring, and retirement.

**Follow-up probe:** How would you keep the discussion at decision level rather than listing infrastructure products?

**Revision links:** [AI/ML system design]({{ '/interview-prep/cheat-sheets/ai-ml-system-design-production-architecture/' | relative_url }})

### DSTL-B5-02 — Build a metric hierarchy for an AI initiative whose model score and business result disagree.

**Round:** Product measurement · **Depth:** Leadership

**Strong answer signals**

- Map business outcome to user behavior, task quality, safety, service, and efficiency metrics and state which are proxies.
- Diagnose population, threshold, workflow, adoption, latency, and downstream-process effects by cohort and slice.
- Optimize outcome subject to non-negotiable safety and service constraints rather than maximizing an isolated model metric.

**Follow-up probe:** What evidence would show that the model improved but the product workflow became worse?

**Revision links:** [AI/ML system design]({{ '/interview-prep/cheat-sheets/ai-ml-system-design-production-architecture/' | relative_url }})

### DSTL-B5-03 — Decide how far to scale an architecture before product demand is proven.

**Round:** Architecture strategy · **Depth:** Leadership

**Strong answer signals**

- Establish measured current and plausible near-term traffic, failure cost, growth, and constraints rather than designing for an arbitrary global maximum.
- Choose a simple baseline with stable contracts and observable bottlenecks, then define triggers for queues, partitioning, dedicated pools, or regionalization.
- Preserve migration and rollback paths while delaying expensive complexity that has no validated user or operational need.

**Follow-up probe:** Which early interface decisions most reduce future migration cost?

**Revision links:** [AI/ML system design]({{ '/interview-prep/cheat-sheets/ai-ml-system-design-production-architecture/' | relative_url }})

### DSTL-B5-04 — Choose between managed models and self-hosted inference for several business units.

**Round:** Build-versus-buy · **Depth:** Leadership

**Strong answer signals**

- Compare required quality, models, residency, privacy, latency, scale variability, customization, availability, lock-in, team capability, and total cost.
- Benchmark exact workloads and include engineering, idle capacity, support, upgrades, security, and incident ownership—not token price alone.
- Allow tiered routing only with equivalent contracts, policy, evaluation, lineage, and tested fallback for each route.

**Follow-up probe:** What usage pattern most strongly favors managed elasticity over dedicated GPUs?

**Revision links:** [AI/ML system design]({{ '/interview-prep/cheat-sheets/ai-ml-system-design-production-architecture/' | relative_url }}) · [LLM inference optimization]({{ '/interview-prep/cheat-sheets/llm-inference-serving-optimization/' | relative_url }})

### DSTL-B5-05 — Define multi-tenant isolation and operating ownership for a shared AI platform.

**Round:** Platform governance · **Depth:** Leadership

**Strong answer signals**

- Tier isolation across identity, authorization, credentials, data/index/cache, compute pools, quotas, logs, residency, and administrative access.
- Assign platform and product owners for sources, models, prompts, tools, policies, evaluation, SLOs, incidents, and support.
- Test noisy-neighbor, cross-tenant, quota, failover, deletion, and audit behavior; do not rely on prompts for isolation.

**Follow-up probe:** When does a high-risk tenant justify a separate account or cluster rather than logical isolation?

**Revision links:** [AI/ML system design]({{ '/interview-prep/cheat-sheets/ai-ml-system-design-production-architecture/' | relative_url }})

## Inference platform and performance governance

### DSTL-B5-06 — Review a capacity proposal based only on theoretical GPU FLOPS and average requests.

**Round:** Capacity governance · **Depth:** Advanced

**Strong answer signals**

- Reject theoretical compute as capacity evidence; require exact model/runtime/hardware and production-like arrival, input, output, concurrency, and quality distributions.
- Size from safe goodput within TTFT/TPOT/E2E SLOs with peak, burst, failure, maintenance, and scale-delay headroom.
- Include queue policy, rejection, warm capacity, downstream quotas, cost, and repeatable spike, soak, and recovery tests.

**Follow-up probe:** Which percentile and request classes should determine capacity rather than the average?

**Revision links:** [LLM inference optimization]({{ '/interview-prep/cheat-sheets/llm-inference-serving-optimization/' | relative_url }})

### DSTL-B5-07 — Decide whether to adopt quantization, speculative decoding, or more GPUs.

**Round:** Optimization strategy · **Depth:** Leadership

**Strong answer signals**

- Start from the measured bottleneck—memory fit, bandwidth-bound decode, compute-heavy prefill, latency, or capacity—and define quality and SLO gates.
- Compare memory, TTFT, TPOT, goodput, stability, scaling efficiency, cost, and task or slice quality on the exact workload.
- Prefer the smallest reversible change with clear rollback; extra GPUs may lose efficiency through communication and speculative methods may have low acceptance.

**Follow-up probe:** When can INT4 make a model fit but fail to improve throughput?

**Revision links:** [LLM inference optimization]({{ '/interview-prep/cheat-sheets/llm-inference-serving-optimization/' | relative_url }})

### DSTL-B5-08 — Set an organization-wide inference benchmark standard.

**Round:** Engineering standards · **Depth:** Leadership

**Strong answer signals**

- Require immutable model, tokenizer/template, precision, engine, driver, hardware, generation, dataset, and client identity.
- Reproduce traffic and token distributions, warm and cold states, concurrency and request-rate sweeps, errors, quality, tail latency, goodput, and cost.
- Retain raw results, variability, failures, and workload classes; prohibit cross-team comparisons lacking equivalent contracts.

**Follow-up probe:** Why should timed-out and rejected requests remain in benchmark results?

**Revision links:** [LLM inference optimization]({{ '/interview-prep/cheat-sheets/llm-inference-serving-optimization/' | relative_url }})

### DSTL-B5-09 — Select an inference engine and serving platform for a multi-model Kubernetes estate.

**Round:** Platform architecture · **Depth:** Advanced

**Strong answer signals**

- Separate engine concerns such as batching, kernels, KV cache, and parallelism from platform concerns such as routing, rollout, autoscaling, tenancy, and lifecycle.
- Evaluate model and hardware support, distributed topology, API contracts, observability, upgrades, security, operational skill, and support.
- Prove the choice with representative failure, drain, scale, rollback, and compatibility tests rather than a feature matrix.

**Follow-up probe:** Why might vLLM plus Kubernetes primitives be enough for one team but not an enterprise platform?

**Revision links:** [LLM inference optimization]({{ '/interview-prep/cheat-sheets/llm-inference-serving-optimization/' | relative_url }}) · [MLOps and LLMOps]({{ '/interview-prep/cheat-sheets/mlops-llmops-deployment-lifecycle/' | relative_url }})

### DSTL-B5-10 — A new server configuration raises throughput but worsens p95 TTFT for premium users. Make the release decision.

**Round:** Release decision · **Depth:** Leadership

**Strong answer signals**

- Evaluate goodput and contractual slices, not aggregate throughput; a premium SLO regression can block release.
- Identify scheduler, batching, queue, long-prompt interference, and capacity causes through paired traffic classes and traces.
- Consider isolated pools or priority controls, canary the exact configuration, and define abort, rollback, and re-entry evidence.

**Follow-up probe:** What evidence would justify releasing the configuration only for batch traffic?

**Revision links:** [LLM inference optimization]({{ '/interview-prep/cheat-sheets/llm-inference-serving-optimization/' | relative_url }})

## MLOps/LLMOps operating model and delivery

### DSTL-B5-11 — Define platform and product-team responsibilities across the AI lifecycle.

**Round:** Operating model · **Depth:** Leadership

**Strong answer signals**

- The platform owns paved paths for identity, lineage, registries, CI/CD, serving, telemetry, security controls, and reusable evaluation infrastructure.
- Product teams own use-case requirements, data semantics, task evaluation, prompts/workflows, risk decisions, user outcomes, and domain support.
- Establish contracts, escalation, exception review, SLOs, costs, lifecycle ownership, and evidence required for promotion.

**Follow-up probe:** Which responsibility must remain with the product team even when the platform supplies an evaluation service?

**Revision links:** [MLOps and LLMOps]({{ '/interview-prep/cheat-sheets/mlops-llmops-deployment-lifecycle/' | relative_url }})

### DSTL-B5-12 — Govern experiment tracking, registry approval, and production aliases.

**Round:** Model governance · **Depth:** Advanced

**Strong answer signals**

- Keep experiments for development evidence and a registry for immutable candidate identity, lineage, gates, approval, deployment, and retirement.
- Make aliases resolve to immutable artifacts in traces and restrict mutation through authorized, audited promotion workflows.
- Define owners, segregation of duties where needed, revalidation triggers, rollback references, and retention.

**Follow-up probe:** What audit gap appears if production traces record only the alias `champion`?

**Revision links:** [MLOps and LLMOps]({{ '/interview-prep/cheat-sheets/mlops-llmops-deployment-lifecycle/' | relative_url }})

### DSTL-B5-13 — Introduce continuous training without allowing silent production replacement.

**Round:** Lifecycle governance · **Depth:** Leadership

**Strong answer signals**

- Define approved triggers, data and label maturation, reproducible pipelines, candidate lineage, and failure handling.
- Treat training output as a candidate subject to data, quality, safety, performance, fairness where applicable, and operational gates.
- Require accountable promotion, progressive rollout, rollback, and feedback controls that prevent poisoning and train/eval leakage.

**Follow-up probe:** Which data change should invalidate a previously accepted evaluation result?

**Revision links:** [MLOps and LLMOps]({{ '/interview-prep/cheat-sheets/mlops-llmops-deployment-lifecycle/' | relative_url }})

### DSTL-B5-14 — Choose shadow, canary, blue-green, rolling, or A/B for an AI release.

**Round:** Deployment strategy · **Depth:** Advanced

**Strong answer signals**

- Match shadow to behavior comparison without user impact, canary to release risk, blue-green to fast environment switching, rolling to ordinary replacement, and A/B to product experiments.
- Account for duplicate cost, state and schema compatibility, cohort comparability, side-effect fencing, capacity, and rollback speed.
- Define exact candidate, exposure, success and abort gates, owner, duration, and post-release verification.

**Follow-up probe:** Why must a shadow agent have write tools disabled or fenced?

**Revision links:** [MLOps and LLMOps]({{ '/interview-prep/cheat-sheets/mlops-llmops-deployment-lifecycle/' | relative_url }})

### DSTL-B5-15 — Approve a release with a database migration that may make rollback unsafe.

**Round:** Change governance · **Depth:** Leadership

**Strong answer signals**

- Require expand-contract or backward-compatible migration where possible, tested backups, active-job strategy, and explicit point-of-no-return.
- Compare rollback with forward recovery, including data integrity, irreversible side effects, downtime, and operator capability.
- Stage the change, validate old and new versions, rehearse recovery, assign authority, and document residual risk before exposure.

**Follow-up probe:** When should the application release be separated from the irreversible migration?

**Revision links:** [MLOps and LLMOps]({{ '/interview-prep/cheat-sheets/mlops-llmops-deployment-lifecycle/' | relative_url }})

## Production quality, SLOs, capacity, and FinOps

### DSTL-B5-16 — Define SLOs for a shared RAG and agent platform.

**Round:** Reliability leadership · **Depth:** Leadership

**Strong answer signals**

- Separate availability, latency, task quality, permission correctness, safety, freshness, side-effect integrity, and cost by risk and tenant class.
- Define SLIs, windows, sample and label coverage, no-data behavior, threshold authority, error budgets, and dependency allocation.
- Tie burn alerts and release policy to actionable runbooks, degraded modes, rollback, and accountable owners.

**Follow-up probe:** How do you represent an HTTP-successful response with an invalid or unauthorized answer in the SLI?

**Revision links:** [AI production operations]({{ '/interview-prep/cheat-sheets/ai-production-monitoring-cost-capacity/' | relative_url }})

### DSTL-B5-17 — Decide whether production drift warrants retraining.

**Round:** Model operations · **Depth:** Advanced

**Strong answer signals**

- Distinguish covariate, prior, concept, output, traffic, and instrumentation changes using versioned baselines and slices.
- Verify telemetry, sample size, seasonality, label coverage, and actual outcome degradation; drift alone is not correctness evidence.
- Choose investigation, threshold review, data repair, retraining, rollback, or no action based on validated cause and business impact.

**Follow-up probe:** Which type of drift cannot be established without labels or outcome evidence?

**Revision links:** [AI production operations]({{ '/interview-prep/cheat-sheets/ai-production-monitoring-cost-capacity/' | relative_url }})

### DSTL-B5-18 — Establish cost governance for teams sharing GPUs and managed providers.

**Round:** FinOps leadership · **Depth:** Leadership

**Strong answer signals**

- Attribute dedicated and provider compute, tokens, idle capacity, retrieval, tools, storage, telemetry, evaluation, and human review to teams and successful outcomes.
- Set budgets, quotas, service tiers, showback or chargeback, anomaly alerts, and exception governance while preserving minimum quality and safety.
- Use measured cost-quality-latency frontiers for routing and capacity decisions and revisit them after workload or price changes.

**Follow-up probe:** How would you prevent one team's long-context jobs from consuming shared interactive capacity?

**Revision links:** [AI production operations]({{ '/interview-prep/cheat-sheets/ai-production-monitoring-cost-capacity/' | relative_url }})

### DSTL-B5-19 — Design an alerting and on-call model for AI quality and service failures.

**Round:** Operating model · **Depth:** Leadership

**Strong answer signals**

- Page only actionable immediate risks, ticket slower work, and use dashboards for observation; every signal needs owner, threshold source, and runbook.
- Include exact lineage, affected slices, evidence coverage, telemetry health, likely changes, fallback and rollback state, and business impact.
- Test delivery, escalation, no-data behavior, deduplication, and runbooks through safe synthetic failures and incident drills.

**Follow-up probe:** Why should a noisy LLM-judge score rarely trigger automatic rollback by itself?

**Revision links:** [AI production operations]({{ '/interview-prep/cheat-sheets/ai-production-monitoring-cost-capacity/' | relative_url }})

### DSTL-B5-20 — Lead a platform incident involving queue growth, fallback traffic, and rising cost.

**Round:** Incident leadership · **Depth:** Leadership

**Strong answer signals**

- Verify telemetry, declare impact, stop amplification through admission, load shedding, retry control, quotas, circuit breaking, or reduced capability.
- Preserve exact release and routing evidence, coordinate model, platform, provider, product, and security owners, and communicate user impact.
- Reconcile incomplete work, restore gradually, then correct capacity, fallback, alert, cost, and change-management gaps with recurrence tests.

**Follow-up probe:** Which signals show that the fallback is protecting availability but violating quality or budget?

**Revision links:** [AI production operations]({{ '/interview-prep/cheat-sheets/ai-production-monitoring-cost-capacity/' | relative_url }})

## Data and distributed compute engineering

### DSTL-B6-01 — Define a workload contract before standardizing a data-processing engine.

**Round:** Data-platform strategy · **Depth:** Leadership

**Strong answer signals**

- Capture volume and growth, file shape, arrival and skew distributions, freshness, latency, replay, correctness, security, retention, cost, and operating ownership by workload class.
- Compare database, warehouse, single-node, batch-distributed, and streaming options on representative work, including coordination and operational overhead.
- Establish a paved road with evidence-based escape criteria, portability and migration expectations, telemetry, support ownership, and periodic review triggers.

**Follow-up probe:** How would you prevent the platform standard from forcing small teams onto unnecessary clusters?

**Revision links:** [Data and distributed compute]({{ '/interview-prep/cheat-sheets/data-distributed-compute-engineering/' | relative_url }})

### DSTL-B6-02 — Govern reproducible backfills across live feature, RAG, and analytics pipelines.

**Round:** Data operations · **Depth:** Advanced

**Strong answer signals**

- Require bounded intervals, immutable source snapshot or offsets, code and config identity, output manifest, owner, capacity quota, downstream impact, and rollback plan.
- Keep raw evidence reproducible and derived products rebuildable; use deterministic keys, staged publication, idempotent sinks, and reconciliation rather than silent overwrites.
- Isolate live SLOs, validate counts and distributions plus point-in-time correctness and permissions, notify consumers, and retain an auditable run record.

**Follow-up probe:** When should a backfill create a new version instead of replacing the current table or index?

**Revision links:** [Data and distributed compute]({{ '/interview-prep/cheat-sheets/data-distributed-compute-engineering/' | relative_url }})

### DSTL-B6-03 — Lead the design of a real-time fraud-feature platform with online/offline parity.

**Round:** System architecture · **Depth:** Leadership

**Strong answer signals**

- Align event definitions, event time, keys, ordering, duplicates, corrections, watermark, label delay, freshness, availability, and acceptable fallback with domain owners.
- Separate immutable events, curated snapshots, versioned stream processing, online features, and point-in-time offline history with ownership and access contracts.
- Gate rollout on replay, parity, late-data, failure, capacity, and reconciliation tests; monitor lag, state, skew, checkpoints, feature quality, cost, and business outcomes.

**Follow-up probe:** Who should own a late-event correction that changes both a served feature and a historical label?

**Revision links:** [Data and distributed compute]({{ '/interview-prep/cheat-sheets/data-distributed-compute-engineering/' | relative_url }})

### DSTL-B6-04 — Establish data contracts and quality gates for ML and GenAI products.

**Round:** Data governance · **Depth:** Leadership

**Strong answer signals**

- Define owner, schema and semantics, keys, units, event time, freshness, allowed evolution, privacy, retention, compatibility, and downstream decision consequences.
- Layer deterministic schema, uniqueness, invariant, volume, freshness, distribution, point-in-time, deletion, and access checks with quarantine and recovery behavior.
- Assign thresholds and response owners, version contracts with consumers, test breaking evolution, and measure incidents and rebuild success rather than tool adoption.

**Follow-up probe:** Which type-compatible schema change can still break model behavior?

**Revision links:** [Data and distributed compute]({{ '/interview-prep/cheat-sheets/data-distributed-compute-engineering/' | relative_url }})

### DSTL-B6-05 — Decide how far to scale a distributed-training platform.

**Round:** Platform strategy · **Depth:** Leadership

**Strong answer signals**

- Segment actual model size, data volume, run frequency, time-to-result, reliability, topology, utilization, checkpoint, and team-skill needs before funding complexity.
- Standardize DDP first where models fit, add sharding or other parallelism for demonstrated memory and throughput limits, and preserve global-batch and reproducibility controls.
- Track useful training throughput, scaling efficiency, queue time, failure recovery, idle capacity, cost per accepted model, adoption, exceptions, and platform exit criteria.

**Follow-up probe:** What evidence would tell you that a managed service is cheaper than operating the internal platform?

**Revision links:** [Data and distributed compute]({{ '/interview-prep/cheat-sheets/data-distributed-compute-engineering/' | relative_url }})

## AI security, privacy, and governance

### DSTL-B6-06 — Create an AI-governance operating model that supports delivery rather than a one-time checklist.

**Round:** Governance · **Depth:** Leadership

**Strong answer signals**

- Maintain an inventory with accountable owner, intended and excluded use, users, system boundary, risk tier, data and release lineage, and applicable policy or jurisdiction.
- Define decision rights for data, product, DS, engineering, security, privacy, legal, model risk, operations, release approval, exceptions, incidents, and retirement.
- Require proportional evaluation, threat modeling, human oversight, rollout, monitoring, evidence retention, review triggers, and time-bounded residual-risk acceptance.

**Follow-up probe:** Which material change should automatically reopen a previously approved assessment?

**Revision links:** [AI security, privacy, and governance]({{ '/interview-prep/cheat-sheets/ai-security-privacy-governance/' | relative_url }})

### DSTL-B6-07 — Lead security and privacy design for a cross-domain enterprise RAG service.

**Round:** Security architecture · **Depth:** Leadership

**Strong answer signals**

- Map identities, tenants, corpora, permissions, data classes, providers, indexes, caches, traces, regions, tools, and trust boundaries with data owners.
- Enforce current authorization before retrieval, lineage and revocation through derived stores, minimization and retention, tenant-scoped caching, safe provider settings, and auditable access.
- Gate each domain independently with cross-tenant canaries, poisoned/revoked content, citation support, deletion, incident, and recovery cases; prohibit shared rollout when evidence is incomplete.

**Follow-up probe:** How would you handle one business unit requesting a weaker retention policy for faster delivery?

**Revision links:** [AI security, privacy, and governance]({{ '/interview-prep/cheat-sheets/ai-security-privacy-governance/' | relative_url }})

### DSTL-B6-08 — Define impact-based security release gates for an agent platform.

**Round:** Security assurance · **Depth:** Leadership

**Strong answer signals**

- Prioritize unauthorized data access and effects, cross-tenant isolation, tool permission, approval, injection, supply chain, replay, resource abuse, and recovery from the exact threat model.
- Combine ordinary application tests, deterministic state assertions, bounded adversarial scenarios, scanners, calibrated content evaluation, load caps, and rollback rehearsal.
- Set severity and acceptance criteria, evidence identity, exception owner and expiry, remediation and retest workflow, plus kill-switch and incident ownership.

**Follow-up probe:** Why should a scanner pass never be the sole release criterion?

**Revision links:** [AI security, privacy, and governance]({{ '/interview-prep/cheat-sheets/ai-security-privacy-governance/' | relative_url }})

### DSTL-B6-09 — Govern sensitive data across prompts, traces, evaluation, fine-tuning, and feedback.

**Round:** Privacy leadership · **Depth:** Leadership

**Strong answer signals**

- Build a purpose and data inventory across inputs, retrieval, embeddings, memory, output, caches, telemetry, evaluation, feedback, provider retention, and training.
- Apply minimization, classification, access, encryption, pseudonymization or redaction, residency, retention, deletion propagation, privacy-safe test data, and field-level logging controls.
- Assign data and privacy owners, validate provider contracts and workflows for access/export/correction/deletion, test incidents, and avoid claiming anonymity without a threat model.

**Follow-up probe:** Which derived artifact is most likely to survive after the source record is deleted?

**Revision links:** [AI security, privacy, and governance]({{ '/interview-prep/cheat-sheets/ai-security-privacy-governance/' | relative_url }})

### DSTL-B6-10 — Respond to a request to claim NIST, OWASP, or EU AI Act compliance.

**Round:** Risk communication · **Depth:** Leadership

**Strong answer signals**

- Clarify that catalogs and frameworks organize risk evidence while legal applicability and formal conformity depend on jurisdiction, actor role, use, dates, and accountable qualified owners.
- Map the exact system to applicable lifecycle, security, privacy, transparency, oversight, documentation, monitoring, and incident obligations without inventing certification.
- Present implemented, tested, missing, excepted, and owner-accepted controls separately; define evidence, deadlines, change triggers, and external review where required.

**Follow-up probe:** How would you explain residual risk to an executive without hiding uncertainty or making a legal conclusion?

**Revision links:** [AI security, privacy, and governance]({{ '/interview-prep/cheat-sheets/ai-security-privacy-governance/' | relative_url }})

## Technical leadership and product thinking

### DSTL-B6-11 — Turn an ambiguous “use GenAI” request into an outcome-based roadmap.

**Round:** Product strategy · **Depth:** Leadership

**Strong answer signals**

- Define user and decision, current workflow and baseline, value, error cost, constraints, guardrails, adoption path, and explicit non-goals.
- Compare process change, rules, dashboard, search, classical ML, RAG, agent, vendor, and human service using the smallest evidence that can change a decision.
- Sequence now/next/later around one vertical slice, uncertainty and dependencies, with owners, stop or pivot criteria, accepted risk, and decision dates.

**Follow-up probe:** What would make you stop the initiative after the first experiment?

**Revision links:** [AI technical leadership and product thinking]({{ '/interview-prep/cheat-sheets/ai-technical-leadership-product-thinking/' | relative_url }})

### DSTL-B6-12 — Build a metric tree for an AI decision-support product.

**Round:** Product metrics · **Depth:** Leadership

**Strong answer signals**

- Connect business outcome, user workflow, adoption and correction, model or retrieval quality, safety and fairness, service reliability, and cost per accepted outcome.
- Define unit, direction, population and slices, window, source, owner, uncertainty, threshold, and action for each metric; distinguish leading proxies from actual outcomes.
- Establish baseline and experiment or rollout attribution, guardrails and capacity limits, delayed-label handling, and a review that can stop or narrow the product.

**Follow-up probe:** Which strong offline metric could coexist with poor user or business value?

**Revision links:** [AI technical leadership and product thinking]({{ '/interview-prep/cheat-sheets/ai-technical-leadership-product-thinking/' | relative_url }})

### DSTL-B6-13 — Prioritize model quality, platform reuse, technical debt, and a new feature under limited capacity.

**Round:** Prioritization · **Depth:** Leadership

**Strong answer signals**

- Compare outcome, urgency, evidence confidence, effort and opportunity cost, risk reduction, dependency unlock, reversibility, learning value, and compliance deadlines.
- Quantify technical debt through incidents, toil, blocked releases, cost, security exposure, or user impact and avoid treating every platform idea as strategic reuse.
- Present options and consequences, choose the smallest work that reduces the largest uncertainty or risk, assign owners, and define triggers for the deferred items.

**Follow-up probe:** How would you resist a stakeholder who treats a scoring framework as an objective answer?

**Revision links:** [AI technical leadership and product thinking]({{ '/interview-prep/cheat-sheets/ai-technical-leadership-product-thinking/' | relative_url }})

### DSTL-B6-14 — Define cross-functional ownership for an AI product without becoming the final approver for everything.

**Round:** Operating model · **Depth:** Leadership

**Strong answer signals**

- Clarify decision rights across Product, domain, data, DS, ML/AI engineering, platform, security, privacy/legal/risk, and operations for outcomes and interfaces.
- Delegate real outcomes and reversible decisions with context, access, evidence bars, checkpoints, and escalation triggers while retaining only consequential boundary decisions.
- Publish standards and paved roads with exception paths, use decision records for costly ambiguity, and measure independent ownership, delivery, reliability, and reduced toil.

**Follow-up probe:** Which decision should remain with a data owner rather than the technical lead?

**Revision links:** [AI technical leadership and product thinking]({{ '/interview-prep/cheat-sheets/ai-technical-leadership-product-thinking/' | relative_url }})

### DSTL-B6-15 — Lead a postmortem after an AI release causes silent quality degradation.

**Round:** Incident leadership · **Depth:** Leadership

**Strong answer signals**

- Contain user harm, preserve model, data, prompt, index, tool, config and cohort identity, bound affected slices and delayed-label windows, and communicate uncertainty.
- Trace the mechanism across upstream data, evaluation representativeness, release gates, telemetry, feedback, and human workflow without blaming an individual.
- Assign systemic actions with owners and verification for monitoring, acceptance sets, shadow or canary rollout, rollback, ownership, and later evidence of effectiveness.

**Follow-up probe:** What would you do if the aggregate metric remained stable while one high-impact slice failed?

**Revision links:** [AI technical leadership and product thinking]({{ '/interview-prep/cheat-sheets/ai-technical-leadership-product-thinking/' | relative_url }})

## Project deep dives, behavioral answers, and mock interviews

### DSTL-B6-16 — Present a lead-level project deep dive without taking sole credit.

**Round:** Project defense · **Depth:** Leadership

**Strong answer signals**

- Structure the answer around user decision, baseline, scale, constraints, alternatives, architecture, validation, rollout, outcome, operating state, and remaining risk.
- Separate what you owned, implemented, influenced, reviewed, and delegated from the team's work, naming one decision artifact or mechanism you personally created.
- Quantify quality, product, business, safety, reliability, and cost evidence with attribution limits and explain one trade-off, failure, or changed decision.

**Follow-up probe:** Which outcome would not have happened without your specific leadership contribution?

**Revision links:** [Project deep dive and mock interviews]({{ '/interview-prep/cheat-sheets/project-deep-dive-behavioral-mock-interview/' | relative_url }})

### DSTL-B6-17 — Defend a GenAI pilot that had strong demos but low adoption and high corrections.

**Round:** Failure and product judgment · **Depth:** Leadership

**Strong answer signals**

- Admit the demo and production-decision mismatch; reconstruct baseline, workflow, cohort, adoption funnel, correction, escalation, source support, latency, permissions, and cost.
- Segment failures across product fit, data freshness and coverage, retrieval, generation, policy, UX, and evaluation selection; contain unsupported tasks.
- Run discriminating tests, re-estimate value, and decide to fix, narrow, pivot to search or workflow, or stop; explain how later discovery and release gates changed.

**Follow-up probe:** Which result would convince you to stop rather than improve the model?

**Revision links:** [Project deep dive and mock interviews]({{ '/interview-prep/cheat-sheets/project-deep-dive-behavioral-mock-interview/' | relative_url }})

### DSTL-B6-18 — Describe a disagreement with an executive about scope or delivery date.

**Round:** Stakeholder leadership · **Depth:** Leadership

**Strong answer signals**

- Restate the shared outcome, expose capacity, evidence, dependency, and risk assumptions, and separate mandatory controls from optional scope.
- Present concrete options with user value, date, quality, safety, operational, and debt consequences; offer a narrower reversible release and escalation path.
- State the accountable decision, your influence and commitment, result, relationship outcome, and what planning or communication behavior changed later.

**Follow-up probe:** What would you do if the executive knowingly accepted a risk outside their authority?

**Revision links:** [Project deep dive and mock interviews]({{ '/interview-prep/cheat-sheets/project-deep-dive-behavioral-mock-interview/' | relative_url }})

### DSTL-B6-19 — Tell a mentoring story that proves another engineer gained independent ownership.

**Round:** People leadership · **Depth:** Leadership

**Strong answer signals**

- Define the capability gap and desired ownership, diagnose it through observed work, and provide context, guardrails, access, and progressively larger decisions.
- Use specific artifact and reasoning feedback, proportional checkpoints, and an escalation contract while leaving room for a different valid approach.
- Show the person's later independent result and team throughput or quality benefit, plus what you changed in your own coaching practice.

**Follow-up probe:** Which mistake did you allow safely because correcting it yourself would have reduced learning?

**Revision links:** [Project deep dive and mock interviews]({{ '/interview-prep/cheat-sheets/project-deep-dive-behavioral-mock-interview/' | relative_url }})

### DSTL-B6-20 — Lead a mock enterprise-agent roadmap across HR, procurement, and finance.

**Round:** Mock leadership case · **Depth:** Leadership

**Strong answer signals**

- Reject “multi-agent everywhere” as a requirement; select one high-value journey from baseline, risk, data and permission readiness, adoption, and measurable outcome.
- Design shared identity, policy, release lineage, observability and operations with domain-owned corpora and tools, bounded autonomy, approvals, audit, and kill switches.
- Deliver one vertical slice, gate a second domain on acceptance evidence, assign cross-functional decisions, show capacity trade-offs, and state what cannot fit the quarter.

**Follow-up probe:** Which reusable platform component should wait until the second domain proves repeated need?

**Revision links:** [Project deep dive and mock interviews]({{ '/interview-prep/cheat-sheets/project-deep-dive-behavioral-mock-interview/' | relative_url }})

## Mathematical foundations and optimization

### DSTL-B7-01 — Review the mathematical correctness of a proposed attention-based architecture.

**Round:** Architecture review · **Depth:** Leadership

**Strong answer signals**

- Require named tensor axes, mask semantics, normalization, objective, parameter and activation memory, numerical precision and complexity estimates before discussing libraries.
- Use shape checks, invariance/property tests, tiny synthetic cases and a simple baseline to expose broadcast, padding, reduction and loss-contract mistakes.
- Separate mathematical validity, optimization evidence and business value; assign owners and acceptance gates for each rather than approving from a diagram.

**Follow-up probe:** Which invariant would you test to catch attention paid to padded positions?

**Revision links:** [Linear algebra, calculus, and optimization]({{ '/interview-prep/cheat-sheets/linear-algebra-calculus-optimization/' | relative_url }})

### DSTL-B7-02 — Standardize embedding similarity across several product teams.

**Round:** Platform strategy · **Depth:** Leadership

**Strong answer signals**

- Define model-specific representation, normalization, metric, index capability, filtering and labeled retrieval benchmarks; reject one universal metric without evidence.
- Publish a versioned vector contract covering dimensions, dtype, norm expectations, distance semantics, score calibration caveats and migration/reindex behavior.
- Gate changes on slice quality, latency, memory and cost, monitor norm/score drift, and preserve dual-read or rollback during model and index transitions.

**Follow-up probe:** Why is a raw similarity threshold not portable across embedding model versions?

**Revision links:** [Linear algebra, calculus, and optimization]({{ '/interview-prep/cheat-sheets/linear-algebra-calculus-optimization/' | relative_url }})

### DSTL-B7-03 — Govern optimizer and training-scale experiments for a costly foundation-model adaptation.

**Round:** Experimental leadership · **Depth:** Leadership

**Strong answer signals**

- Fix model/data identity, token budget, global batch, schedule, precision, evaluation cadence and compute ceiling so SGD/AdamW or schedule comparisons are meaningful.
- Require learning curves, throughput, stability, held-out task/safety quality and uncertainty across seeds/checkpoints rather than choosing the lowest observed training loss.
- Use staged low-cost screens, explicit stop rules, reproducible manifests and promotion gates; retain checkpoint compatibility and rollback evidence.

**Follow-up probe:** What must remain constant when comparing two optimizers under a fixed compute budget?

**Revision links:** [Linear algebra, calculus, and optimization]({{ '/interview-prep/cheat-sheets/linear-algebra-calculus-optimization/' | relative_url }})

### DSTL-B7-04 — Decide whether PCA belongs in a regulated tabular-model pipeline.

**Round:** Model governance · **Depth:** Advanced

**Strong answer signals**

- Frame the need—conditioning, compression, privacy, latency or multicollinearity—and compare with regularization, feature removal and simpler models.
- Evaluate downstream quality, stability, slice effects, reproducibility and explanation obligations; explained variance alone does not establish predictive or regulatory value.
- Fit within folds, version the transform, preserve lineage back to source features, validate serving parity and document the loss of direct feature interpretability.

**Follow-up probe:** How would you explain a principal-component model decision to a reviewer who needs source-feature evidence?

**Revision links:** [Linear algebra, calculus, and optimization]({{ '/interview-prep/cheat-sheets/linear-algebra-calculus-optimization/' | relative_url }})

### DSTL-B7-05 — Lead a constrained optimization design for production scheduling.

**Round:** Decision optimization · **Depth:** Leadership

**Strong answer signals**

- Define objective units, hard/soft constraints, uncertainty, time horizon, decision cadence, feasibility, data latency and accountable business owner.
- Separate predictive inputs from the solver, compare baseline heuristics, test sensitivity and shadow prices, and avoid claiming a local or relaxed result is globally optimal.
- Require solver status/tolerance, infeasibility diagnosis, safe fallback, human override, replayable inputs, realized-outcome attribution and rollback.

**Follow-up probe:** What should the system do when the mathematical model is infeasible but operations must continue?

**Revision links:** [Linear algebra, calculus, and optimization]({{ '/interview-prep/cheat-sheets/linear-algebra-calculus-optimization/' | relative_url }})

## Experimentation and causal inference

### DSTL-B7-06 — Establish an experimentation standard for AI product releases.

**Round:** Operating model · **Depth:** Leadership

**Strong answer signals**

- Require decision, estimand, unit, eligibility, assignment, treatment version, primary metric, guardrails, power, duration and stop/launch rule before exposure.
- Standardize immutable assignment, A/A and SRM monitoring, design-consistent uncertainty, multiple-testing policy, analysis review and reproducible result artifacts.
- Tier requirements by impact, preserve emergency safety stops, assign metric and decision owners, and audit whether launches achieved durable downstream value.

**Follow-up probe:** Which controls should be mandatory even for a low-traffic experiment?

**Revision links:** [Experimentation and causal inference]({{ '/interview-prep/cheat-sheets/experimentation-causal-inference/' | relative_url }})

### DSTL-B7-07 — Select a design for a marketplace ranking change with seller and buyer interference.

**Round:** Causal strategy · **Depth:** Leadership

**Strong answer signals**

- Define whether the target is buyer utility, seller welfare, transactions or ecosystem value and map inventory/competition spillovers that invalidate simple user randomization.
- Compare cluster, geo, switchback and marketplace-specific designs using contamination, power, carryover, operational risk and representativeness.
- Measure both sides, concentration/fairness, latency, cancellations and long-term equilibrium; use staged ramp and sensitivity analysis before scaling.

**Follow-up probe:** Why might buyer-level randomization change outcomes for control-group sellers?

**Revision links:** [Experimentation and causal inference]({{ '/interview-prep/cheat-sheets/experimentation-causal-inference/' | relative_url }})

### DSTL-B7-08 — Make a launch decision when the primary effect interval crosses zero.

**Round:** Product judgment · **Depth:** Leadership

**Strong answer signals**

- Compare the full confidence/credible interval with the minimum practical effect, downside tolerance, guardrails, cost and reversibility rather than labeling the test simply failed.
- Check power assumptions, SRM, metric maturity, heterogeneity, novelty and implementation fidelity without fishing for a favorable segment or extended horizon.
- Choose stop, iterate, gather more data or bounded rollout using a pre-agreed decision owner and record uncertainty, opportunity cost and next evidence.

**Follow-up probe:** When is gathering more data worse than stopping and reallocating traffic?

**Revision links:** [Experimentation and causal inference]({{ '/interview-prep/cheat-sheets/experimentation-causal-inference/' | relative_url }})

### DSTL-B7-09 — Review an observational claim that AI-tool adoption improved employee productivity.

**Round:** Causal governance · **Depth:** Leadership

**Strong answer signals**

- Demand a precise adoption policy, productivity outcome, population, horizon and DAG including motivation, skill, workload, manager support and post-treatment behavior.
- Challenge self-selection, overlap, missing outcomes and policy feedback; require balance, sensitivity, negative controls and transparent residual-confounding limits.
- Prefer randomized encouragement or phased rollout when feasible and prevent an associational estimate from being presented as company-wide causal ROI.

**Follow-up probe:** Which variable might look like a useful control but actually mediate adoption's effect?

**Revision links:** [Experimentation and causal inference]({{ '/interview-prep/cheat-sheets/experimentation-causal-inference/' | relative_url }})

### DSTL-B7-10 — Design an experimentation platform roadmap rather than only an analysis notebook.

**Round:** Data platform leadership · **Depth:** Leadership

**Strong answer signals**

- Prioritize identity, eligibility, deterministic assignment, configuration/versioning, exposure, metric definitions, power planning, SRM and analysis reproducibility as product contracts.
- Separate control and data planes, secure permissions, preserve audit lineage, support cluster/holdout designs and prevent mutually contaminating experiments.
- Define SLOs, ownership, migration, cost, self-service guardrails and adoption metrics; deliver a vertical slice before a general framework.

**Follow-up probe:** What is the minimum platform capability needed to trust an experiment result?

**Revision links:** [Experimentation and causal inference]({{ '/interview-prep/cheat-sheets/experimentation-causal-inference/' | relative_url }})

## Data preparation, EDA, and feature engineering

### DSTL-B7-11 — Define a cross-team data and label contract for a high-impact ML use case.

**Round:** Data governance · **Depth:** Leadership

**Strong answer signals**

- Specify entity/grain, keys, event/available times, schema, units, label horizon, adjudication, population, privacy, retention and allowed evolution with owners.
- Turn correctness into executable uniqueness, referential, freshness, range, distribution, point-in-time and deletion tests with quarantine, recovery and escalation.
- Version definitions and lineage, measure quality by slice, negotiate backward-compatible changes and tie contract failures to model fallback and release decisions.

**Follow-up probe:** Which label change requires a new dataset/model version even if the column type remains the same?

**Revision links:** [Data preparation, EDA, and feature engineering]({{ '/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/' | relative_url }})

### DSTL-B7-12 — Build a label strategy when outcomes are delayed, selective, and expensive to review.

**Round:** Applied-science strategy · **Depth:** Leadership

**Strong answer signals**

- Map label source, maturity, censoring, intervention-created selective labels, annotator rubric, disagreement and the decision's false-error costs.
- Combine a randomly sampled adjudicated gold set with weak supervision or active learning, retaining provenance and correcting evaluation selection bias.
- Plan delayed-outcome monitoring, exploration or holdouts where ethical, uncertainty and feedback SLAs; do not optimize only the currently observable policy outcomes.

**Follow-up probe:** How can a successful intervention make future training labels systematically missing?

**Revision links:** [Data preparation, EDA, and feature engineering]({{ '/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/' | relative_url }})

### DSTL-B7-13 — Decide whether the organization needs a feature store.

**Round:** Build-versus-buy · **Depth:** Leadership

**Strong answer signals**

- Start from reuse, online latency, point-in-time correctness, parity, freshness, governance and duplicated-computation pain rather than adopting a platform category.
- Compare warehouse pipelines, shared transformation libraries and managed/self-hosted feature stores across scale, ownership, migration, lock-in, cost and recovery.
- Require entity/time semantics, lineage, backfills, TTL, materialization, deletion and reconciliation contracts; pilot one valuable feature family with adoption evidence.

**Follow-up probe:** Which correctness problem remains a team responsibility even after buying a feature store?

**Revision links:** [Data preparation, EDA, and feature engineering]({{ '/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/' | relative_url }})

### DSTL-B7-14 — Run a leakage review before approving a model release.

**Round:** Release governance · **Depth:** Leadership

**Strong answer signals**

- Reconstruct real decision time, unit, label horizon and source produced/available timestamps; review target, temporal, entity, preprocessing, evaluation and feedback leakage.
- Require group/time backtests, pipeline-in-fold fitting, duplicate/similarity tests, metadata-only baselines and point-in-time feature reconstruction.
- Record reviewer, evidence, residual risks and blocked features; add reusable availability metadata and regression tests rather than relying on a one-time checklist.

**Follow-up probe:** Which leakage can remain even when every feature timestamp precedes the label timestamp?

**Revision links:** [Data preparation, EDA, and feature engineering]({{ '/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/' | relative_url }})

### DSTL-B7-15 — Govern feature ownership and change across multiple production models.

**Round:** ML operating model · **Depth:** Leadership

**Strong answer signals**

- Assign source, semantic-definition, pipeline and consuming-model owners; version schema, units, time semantics, default, privacy class and deprecation policy.
- Map dependencies, require compatibility and point-in-time tests, canary changes, dual computation and consumer sign-off proportional to risk.
- Monitor freshness, parity, drift, cost and downstream impact; support rollback/backfill and retire unused or sensitive features with deletion propagation.

**Follow-up probe:** How would you prevent a harmless-looking unit change from silently corrupting five models?

**Revision links:** [Data preparation, EDA, and feature engineering]({{ '/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/' | relative_url }})

## Unsupervised learning and anomaly detection

### DSTL-B7-16 — Decide whether customer clustering should become a product capability.

**Round:** Product strategy · **Depth:** Leadership

**Strong answer signals**

- Start from the decision and compare rules, supervised uplift and continuous scores with clustering; define who acts and what reversible treatment changes.
- Require point-in-time representation, stability, interpretability, support, fairness and prospective treatment-value evidence rather than silhouette or a colorful projection.
- Establish segment versioning, migration, monitoring, ownership and retirement because customer labels can become stale or self-fulfilling.

**Follow-up probe:** When is a continuous propensity score preferable to discrete segments?

**Revision links:** [Unsupervised learning and anomaly detection]({{ '/interview-prep/cheat-sheets/unsupervised-learning-anomaly-detection/' | relative_url }})

### DSTL-B7-17 — Design an enterprise anomaly-detection operating model.

**Round:** Platform leadership · **Depth:** Leadership

**Strong answer signals**

- Separate domain-specific reference populations and actions from shared ingestion, scoring, threshold, case-management, feedback, lineage and monitoring capabilities.
- Define severity, alert capacity, random audit, adjudication, escalation, retraining, rollback and incident ownership; do not optimize a central model score alone.
- Track prevented loss, precision at capacity, delay, workload and missed-event estimates with site/slice governance and cost allocation.

**Follow-up probe:** Which components should be shared while thresholds remain domain-owned?

**Revision links:** [Unsupervised learning and anomaly detection]({{ '/interview-prep/cheat-sheets/unsupervised-learning-anomaly-detection/' | relative_url }})

### DSTL-B7-18 — Set the evidence bar for choosing among clustering algorithms.

**Round:** Model evaluation · **Depth:** Leadership

**Strong answer signals**

- Predefine decision, representation, distance, constraints and baselines; compare k-means, mixtures, hierarchical or density methods only where their assumptions fit.
- Require stability across seeds/samples/time, cluster support and migration, expert interpretability, slice/fairness analysis and downstream prospective value.
- Treat internal scores and 2D plots as diagnostics, retain reproducible artifacts, and reject solutions whose operational assignment or monitoring is undefined.

**Follow-up probe:** Why can the algorithm with the best silhouette be the worst product choice?

**Revision links:** [Unsupervised learning and anomaly detection]({{ '/interview-prep/cheat-sheets/unsupervised-learning-anomaly-detection/' | relative_url }})

### DSTL-B7-19 — Approve risk-based anomaly thresholds under limited investigation capacity.

**Round:** Risk decision · **Depth:** Leadership

**Strong answer signals**

- Translate scores into severity tiers using error costs, daily capacity, time-to-harm, prevalence and slice obligations; separate model from policy versions.
- Evaluate precision and captured value at capacity, delay and random below-threshold audit rather than relying on ROC-AUC or a guessed contamination rate.
- Define override, escalation, capacity overload, drift response and accountable acceptance of residual risk; monitor whether investigations produce beneficial action.

**Follow-up probe:** Who should own the trade-off when raising recall doubles analyst workload?

**Revision links:** [Unsupervised learning and anomaly detection]({{ '/interview-prep/cheat-sheets/unsupervised-learning-anomaly-detection/' | relative_url }})

### DSTL-B7-20 — Lead an anomaly-system incident after onboarding a new region.

**Round:** Incident leadership · **Depth:** Leadership

**Strong answer signals**

- Contain alert overload without losing evidence, establish incident command, identify exact data/model/threshold versions and protect high-severity response.
- Distinguish source/unit/schema failure, legitimate population shift and real incident through region comparisons, domain owners and sampled adjudication.
- Recover with correction or bounded shadow model, reconcile missed/suppressed alerts, communicate uncertainty and add onboarding gates, reference ownership and effectiveness checks.

**Follow-up probe:** What must be reconciled before declaring the incident resolved?

**Revision links:** [Unsupervised learning and anomaly detection]({{ '/interview-prep/cheat-sheets/unsupervised-learning-anomaly-detection/' | relative_url }})

## Experimentation and causal inference — advanced practice

### DSTL-B8-01 — Define the minimum experimentation standard for all AI product teams.

**Round:** Experiment governance · **Depth:** Leadership

**Strong answer signals**

- Require decision, population, treatment, unit, estimand, primary metric, guardrails, MDE/power, duration, stopping rule, assignment/exposure and accountable owner before launch.
- Standardize immutable configuration, A/A and SRM checks, design-consistent analysis, multiplicity policy, reproducible result records and safety stop paths.
- Tier review by user/business impact, train teams through templates and examples, and audit whether shipped decisions created durable value rather than counting experiments.

**Follow-up probe:** Which controls remain mandatory for a low-risk experiment with little traffic?

**Revision links:** [Experimentation and causal inference]({{ '/interview-prep/cheat-sheets/experimentation-causal-inference/' | relative_url }})

### DSTL-B8-02 — Establish a multiple-testing and sequential-monitoring policy.

**Round:** Statistical leadership · **Depth:** Leadership

**Strong answer signals**

- Classify one primary outcome, guardrails, confirmatory families and exploratory diagnostics; choose family-wise, false-discovery, hierarchical or confirmation rules from decision cost.
- Permit continuous safety monitoring while requiring supported sequential inference or predeclared looks for efficacy; prohibit optional stopping with ordinary fixed-horizon p-values.
- Encode policy in the platform, simulate error/power trade-offs, require transparent reporting of all variants/segments and retain an independent confirmation path.

**Follow-up probe:** When is false-discovery-rate control more appropriate than family-wise error control?

**Revision links:** [Experimentation and causal inference]({{ '/interview-prep/cheat-sheets/experimentation-causal-inference/' | relative_url }})

### DSTL-B8-03 — Decide whether an observational study is sufficient for an executive ROI claim.

**Round:** Causal governance · **Depth:** Leadership

**Strong answer signals**

- Demand a precise policy contrast, population, horizon and outcome plus a causal graph covering selection, opportunity, prior performance, management and post-treatment behavior.
- Review identification, overlap, balance, missing outcomes, negative/placebo controls and sensitivity; make residual unmeasured-confounding and external-validity limits visible.
- Prefer randomized encouragement, phased rollout or natural experiment when feasible, and label estimates as directional rather than realized causal ROI when assumptions are weak.

**Follow-up probe:** What evidence would justify delaying the executive claim for a stronger design?

**Revision links:** [Experimentation and causal inference]({{ '/interview-prep/cheat-sheets/experimentation-causal-inference/' | relative_url }})

### DSTL-B8-04 — Govern heterogeneous-effect models used to target treatment.

**Round:** Decision-science leadership · **Depth:** Leadership

**Strong answer signals**

- Require randomized or credibly identified data, overlap, honest sample splitting, sufficient support and a targeting decision with capacity, fairness and safety constraints.
- Compare treat-all, treat-none, simple segments and uplift models using out-of-sample policy value, uncertainty and sensitivity rather than response-model accuracy.
- Confirm discovered segments prospectively, version the policy and threshold, monitor distribution and treatment allocation, and prevent self-reinforcing exclusion.

**Follow-up probe:** Who owns the risk when an estimated low-benefit group receives less service?

**Revision links:** [Experimentation and causal inference]({{ '/interview-prep/cheat-sheets/experimentation-causal-inference/' | relative_url }})

### DSTL-B8-05 — Select a causal design for a shared-capacity marketplace change.

**Round:** Causal strategy · **Depth:** Leadership

**Strong answer signals**

- Define buyer, seller, transaction and ecosystem estimands; map inventory, competition, queue and geographic spillovers that invalidate simple user assignment.
- Compare cluster, geo, switchback, saturation and staged designs by contamination, effective sample, carryover, operational risk and representativeness.
- Measure welfare on both sides, concentration, safety, cost and long-term equilibrium; require staged ramp, washout and sensitivity before scaling.

**Follow-up probe:** Why can a treatment assigned only to buyers change control sellers' outcomes?

**Revision links:** [Experimentation and causal inference]({{ '/interview-prep/cheat-sheets/experimentation-causal-inference/' | relative_url }})

## Feature engineering and ML data validation

### DSTL-B8-06 — Create an organization-wide feature ownership and change policy.

**Round:** ML governance · **Depth:** Leadership

**Strong answer signals**

- Assign source, semantic, pipeline and consuming-model owners; define entity/time, unit, default, privacy, retention, freshness, allowed use and deprecation in a versioned contract.
- Map consumers and require compatibility, point-in-time, parity and downstream acceptance tests with canary/dual computation for high-risk changes.
- Monitor quality and cost, support rollback/backfill/deletion propagation, and retire unused features rather than growing an unowned registry.

**Follow-up probe:** Which semantic change requires a new feature version even when name and type remain unchanged?

**Revision links:** [Feature engineering and ML data validation]({{ '/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/' | relative_url }})

### DSTL-B8-07 — Design a label strategy for delayed and selectively observed outcomes.

**Round:** Applied-science strategy · **Depth:** Leadership

**Strong answer signals**

- Map label source, maturation, censoring, policy-created missingness, adjudication, disagreement, revisions and the action's false-error costs.
- Maintain a randomly sampled independent gold set, combine weak supervision or active learning with provenance, and preserve exploration/holdouts where ethical.
- Define feedback SLAs, delayed-outcome monitoring and evaluation-selection corrections; prevent current interventions from defining all future “ground truth.”

**Follow-up probe:** How can a successful fraud block remove the label needed to learn whether the transaction was truly fraudulent?

**Revision links:** [Feature engineering and ML data validation]({{ '/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/' | relative_url }})

### DSTL-B8-08 — Build a reusable ML data-validation standard without hiding domain rules.

**Round:** Data platform leadership · **Depth:** Leadership

**Strong answer signals**

- Provide shared schema, uniqueness, freshness, distribution, lineage, point-in-time and parity primitives while keeping domain semantics and thresholds owned by the producing/consuming teams.
- Define block, quarantine, warn and scoped-exception behavior with expiry, evidence and recovery; never silently learn a new baseline from failing production data.
- Integrate checks at ingestion, transformation, training and serving, measure false alarms and incidents caught, and version rules with datasets and models.

**Follow-up probe:** Which data failure should block publication even if the model's aggregate score still passes?

**Revision links:** [Feature engineering and ML data validation]({{ '/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/' | relative_url }})

### DSTL-B8-09 — Lead a feature-store decision and adoption roadmap.

**Round:** Build-versus-buy · **Depth:** Leadership

**Strong answer signals**

- Quantify reuse, online latency, point-in-time, parity, governance, backfill and duplicated-pipeline pain before treating a feature store as the solution.
- Compare warehouse/shared-library/managed/self-hosted options across semantics, migration, ownership, scale, availability, cost, lock-in, deletion and disaster recovery.
- Pilot one valuable cross-team feature family, publish adoption and correctness metrics, preserve an exit path, and require teams to own meaning despite platform support.

**Follow-up probe:** What evidence would show the platform adds complexity without reducing training-serving skew?

**Revision links:** [Feature engineering and ML data validation]({{ '/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/' | relative_url }})

### DSTL-B8-10 — Set an operating response for feature and label drift.

**Round:** Production governance · **Depth:** Leadership

**Strong answer signals**

- Separate schema/source defects, seasonality, population/policy shifts, label-definition change and target-concept drift with source and outcome evidence by slice.
- Define owners, severity, containment, fallback, repair, recalibration, retraining and risk-acceptance decisions; do not make drift score an automatic retraining trigger.
- Retain incident lineage, validate recovery and measure whether changed thresholds/models improved downstream outcomes without hiding affected groups.

**Follow-up probe:** When should the team freeze retraining even though feature drift is large?

**Revision links:** [Feature engineering and ML data validation]({{ '/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/' | relative_url }})

## Time series and forecasting

### DSTL-B8-11 — Define a forecasting strategy across hundreds of heterogeneous series.

**Round:** Forecasting leadership · **Depth:** Leadership

**Strong answer signals**

- Segment series by volume, intermittency, history, hierarchy, decision value and lead time; define common origins, horizons, information sets and business loss.
- Establish seasonal-naive and domain baselines, then compare local statistical, global ML/deep and foundation models with portfolio-aware backtests.
- Choose tiered models and fallbacks from value, uncertainty, latency, maintainability and data support rather than forcing one model family everywhere.

**Follow-up probe:** Which series should remain on a simple baseline even if a global model wins on average?

**Revision links:** [Time series and forecasting]({{ '/interview-prep/cheat-sheets/time-series-forecasting/' | relative_url }})

### DSTL-B8-12 — Decide whether to adopt a time-series foundation model.

**Round:** Model strategy · **Depth:** Leadership

**Strong answer signals**

- Compare with seasonal-naive, ETS/ARIMA, boosting and existing global models on representative origins, horizons, intermittent/shifted slices and probabilistic calibration.
- Evaluate context/horizon limits, covariates, adaptation, latency, memory, throughput, license, privacy, observability, reproducibility and vendor/model lifecycle.
- Run a bounded benchmark with stop criteria, total cost and rollback; adopt only where incremental forecast value justifies operational complexity.

**Follow-up probe:** What result would favor a classical model despite lower average accuracy?

**Revision links:** [Time series and forecasting]({{ '/interview-prep/cheat-sheets/time-series-forecasting/' | relative_url }})

### DSTL-B8-13 — Govern hierarchical and probabilistic forecasts used for planning.

**Round:** Decision governance · **Depth:** Leadership

**Strong answer signals**

- Define hierarchy, aggregation constraints, decision levels, quantiles/scenarios, asymmetric costs and which totals must reconcile.
- Compare bottom-up, top-down and reconciliation methods with coherent uncertainty, horizon/segment coverage and downstream optimization value.
- Assign override authority, record versions and assumptions, monitor bias/coverage and reconcile actual decisions rather than accepting mathematically coherent but unusable forecasts.

**Follow-up probe:** Why can separately calibrated intervals become incoherent after hierarchy reconciliation?

**Revision links:** [Time series and forecasting]({{ '/interview-prep/cheat-sheets/time-series-forecasting/' | relative_url }})

### DSTL-B8-14 — Measure forecast value rather than only forecast error.

**Round:** Product and business metrics · **Depth:** Leadership

**Strong answer signals**

- Link horizon/series error and uncertainty to inventory, capacity, service, waste, margin or regret through an explicit decision baseline.
- Track forecast value add against naive and prior process, adoption/overrides, constraint feasibility and realized outcomes with attribution limits.
- Prevent metric gaming through weighted slice reporting, guardrails and a holdout or phased decision test when forecast improvements do not guarantee operational benefit.

**Follow-up probe:** How can lower RMSE increase inventory cost?

**Revision links:** [Time series and forecasting]({{ '/interview-prep/cheat-sheets/time-series-forecasting/' | relative_url }})

### DSTL-B8-15 — Lead a forecasting incident during a structural break.

**Round:** Incident leadership · **Depth:** Leadership

**Strong answer signals**

- Protect decisions with baseline/manual/scenario fallbacks, establish exact data/model/calendar/override versions and bound affected series, horizons and business exposure.
- Distinguish corrupted pipeline, stockout censoring, one-time shock and persistent regime change using source, residual, bias and external-event evidence.
- Recover through corrected inputs or shadow challenger, communicate uncertainty, reconcile decisions and add break detection, runbooks and later effectiveness checks.

**Follow-up probe:** What must be reconciled after the model recovers but planners already acted on bad forecasts?

**Revision links:** [Time series and forecasting]({{ '/interview-prep/cheat-sheets/time-series-forecasting/' | relative_url }})

## Recommendation, search, and ranking

### DSTL-B8-16 — Define the objective and architecture for a recommendation product.

**Round:** Product system design · **Depth:** Leadership

**Strong answer signals**

- Define user decision, candidate universe, eligibility/safety, exposure, short- and long-term value, business constraints, feedback window and failure cost.
- Compare popularity/content/collaborative baselines with candidate-generation, ranking and policy re-ranking stages under latency, freshness, scale and explainability.
- Create a metric tree spanning product outcome, retrieval/ranking quality, coverage/diversity/fairness, service reliability, cost and responsible exploration.

**Follow-up probe:** Which objective prevents optimizing clicks at the expense of long-term user value?

**Revision links:** [Recommendation, search, and ranking]({{ '/interview-prep/cheat-sheets/recommendation-search-ranking/' | relative_url }})

### DSTL-B8-17 — Set evidence gates from offline ranking metrics to online launch.

**Round:** Evaluation governance · **Depth:** Leadership

**Strong answer signals**

- Require time/user-aware evaluation, candidate recall, ranking metrics and slice diagnostics with exact data/policy identity and exposure-bias limitations.
- Gate on relevance plus coverage, diversity, novelty, calibration, safety, fairness, latency, availability and cost; compare current and simple baselines.
- Use guarded online experiments for causal product impact, staged ramp and long-term holdouts where feedback loops or novelty can hide harm.

**Follow-up probe:** Which offline result is necessary but insufficient before an online ranking test?

**Revision links:** [Recommendation, search, and ranking]({{ '/interview-prep/cheat-sheets/recommendation-search-ranking/' | relative_url }})

### DSTL-B8-18 — Govern popularity bias, fairness, and feedback loops.

**Round:** Responsible recommendation · **Depth:** Leadership

**Strong answer signals**

- Map who receives exposure and benefit, historical policy bias, cold-start/long-tail effects and protected or contractual constraints at user, creator and item levels.
- Combine calibrated relevance with diversity/coverage constraints and bounded exploration; log propensities and audit outcomes rather than forcing demographic parity blindly.
- Monitor concentration, opportunity, complaints, safety and long-term retention, assign risk ownership and test policy changes prospectively.

**Follow-up probe:** How can optimizing only historical clicks make the long tail permanently invisible?

**Revision links:** [Recommendation, search, and ranking]({{ '/interview-prep/cheat-sheets/recommendation-search-ranking/' | relative_url }})

### DSTL-B8-19 — Make a build-versus-buy decision for search and ranking infrastructure.

**Round:** Technical strategy · **Depth:** Leadership

**Strong answer signals**

- Define catalog/index scale, query volume, latency, freshness, filters, personalization, multilingual relevance, experimentation, tenancy, security and availability needs.
- Compare managed search/vector/ranking services and custom stacks across relevance control, integrations, operations, skills, migration, lock-in, total cost and provider failure.
- Benchmark representative queries and failure modes, preserve an interface/data export path, and assign lifecycle, evaluation and incident ownership.

**Follow-up probe:** Which requirement can justify custom ranking while retaining a managed retrieval layer?

**Revision links:** [Recommendation, search, and ranking]({{ '/interview-prep/cheat-sheets/recommendation-search-ranking/' | relative_url }})

### DSTL-B8-20 — Lead a ranking incident that harms conversion and seller exposure.

**Round:** Incident leadership · **Depth:** Leadership

**Strong answer signals**

- Stop or narrow the release, establish exact candidate/model/feature/policy identities, bound user/seller impact and preserve exposure, ordering and action evidence.
- Separate service latency/availability, inventory/filter, candidate recall, model, re-ranking and telemetry failures with segment and marketplace analysis.
- Reconcile missed/incorrect exposure, communicate knowns and uncertainty, restore safely and add end-to-end gates, concentration monitors, rollback and post-incident effectiveness checks.

**Follow-up probe:** Why must recovery verify both user conversion and seller exposure distribution?

**Revision links:** [Recommendation, search, and ranking]({{ '/interview-prep/cheat-sheets/recommendation-search-ranking/' | relative_url }})

## Computer vision and multimodal AI

### DSTL-B9-01 — Decide whether a defect-detection product needs classification, detection, or segmentation.

**Round:** Vision problem framing · **Depth:** Lead

**Strong answer signals**

- Start from operator action: whether presence is enough, localization is required for repair, or pixel area/boundary drives severity; define latency and miss/false-alarm cost.
- Compare annotation cost/quality, object size/overlap, explainability and deployment capacity with simple rules and transfer-learning baselines.
- Select the minimum output that changes the decision, then gate it with slice metrics, calibration/abstention, reviewer workflow and measurable operational impact.

**Follow-up probe:** When could a weaker classifier deliver more value than a higher-AP segmenter?

**Revision links:** [Computer vision and multimodal AI]({{ '/interview-prep/cheat-sheets/computer-vision-multimodal-ai/' | relative_url }})

### DSTL-B9-02 — Establish a visual-data and annotation governance program across sites.

**Round:** Data leadership · **Depth:** Lead

**Strong answer signals**

- Define capture/consent/rights, retention and identity standards plus ontology, ambiguous-case, occlusion, negative and adjudication rules with accountable owners.
- Version manifests, label guide and annotator/tool provenance; audit duplicates, site/device coverage, rare classes, disagreement and privacy-sensitive content.
- Use group/site/time splits and external holdouts, sample quality reviews and drift/change triggers; block publication when critical lineage or annotation gates fail.

**Follow-up probe:** How would you handle a site whose annotators systematically draw looser boxes?

**Revision links:** [Computer vision and multimodal AI]({{ '/interview-prep/cheat-sheets/computer-vision-multimodal-ai/' | relative_url }})

### DSTL-B9-03 — Build a roadmap for a multimodal document-understanding product.

**Round:** Product and architecture · **Depth:** Lead

**Strong answer signals**

- Prioritize user tasks and schemas—classification, OCR/extraction, tables, visual Q&A or grounded generation—with privacy, review, latency and cost requirements.
- Stage OCR/rules and task-specific baselines before general VLMs; benchmark build/buy and routing options on a versioned representative corpus.
- Plan visual grounding/hallucination, prompt-injection and access controls, human correction, observability and rollout/rollback with business and quality gates.

**Follow-up probe:** Which evidence would justify adding a costly VLM after a strong OCR-plus-rules baseline?

**Revision links:** [Computer vision and multimodal AI]({{ '/interview-prep/cheat-sheets/computer-vision-multimodal-ai/' | relative_url }})

### DSTL-B9-04 — Define release gates for a safety-sensitive vision system.

**Round:** Model governance · **Depth:** Lead

**Strong answer signals**

- Require exact data/label/split/model/preprocessing/runtime identities, intended/excluded environments and baseline comparisons across class, site, device, lighting, object-size and rare-event slices.
- Gate calibration/abstention, robustness within the threat model, latency/capacity, privacy/security, reviewer load, failure fallback and rollback—not only average AP.
- Use independent review and guarded shadow/canary evidence, predeclare stop criteria and retain unresolved risks with owners before production approval.

**Follow-up probe:** Why should synthetic corruption benchmarks not be the only robustness gate?

**Revision links:** [Computer vision and multimodal AI]({{ '/interview-prep/cheat-sheets/computer-vision-multimodal-ai/' | relative_url }})

### DSTL-B9-05 — Lead an incident where a vision model misses rare defects after a new production line launches.

**Round:** Incident leadership · **Depth:** Leadership

**Strong answer signals**

- Protect users by reverting/narrowing automation and increasing review; bound affected parts/sites/times and preserve image, capture, model and decision evidence.
- Separate capture/preprocessing drift, annotation policy, object scale, class support and threshold/calibration failures using known-good comparisons and expert review.
- Communicate impact/uncertainty, correct data or system, backtest and canary the fix, then add new-line acceptance, rare-class and delayed-outcome gates plus accountable follow-up.

**Follow-up probe:** How would you avoid training immediately on biased labels produced during the incident?

**Revision links:** [Computer vision and multimodal AI]({{ '/interview-prep/cheat-sheets/computer-vision-multimodal-ai/' | relative_url }})

## Graph ML and knowledge graphs

### DSTL-B9-06 — Decide whether a business problem genuinely requires a graph model.

**Round:** Modeling strategy · **Depth:** Lead

**Strong answer signals**

- Define relational hypothesis, nodes/edges/time and decision; ask whether relationships add signal or constraints unavailable to a tabular model.
- Compare rules, degree/path aggregates, matrix factorization and tabular baselines with a GNN on leakage-safe temporal/group splits.
- Include graph construction/identity cost, privacy, scale, freshness, explainability, serving and deletion; choose the simplest approach with stable decision value.

**Follow-up probe:** What ablation shows whether the GNN uses structure rather than only node features?

**Revision links:** [Graph ML and knowledge graphs]({{ '/interview-prep/cheat-sheets/graph-ml-knowledge-graphs/' | relative_url }})

### DSTL-B9-07 — Set organization-wide standards for temporal graph evaluation.

**Round:** Technical standards · **Depth:** Lead

**Strong answer signals**

- Require event/availability times, snapshot manifests, target-edge removal, entity grouping, reverse-edge deduplication and explicit transductive versus inductive claims.
- Standardize eligible candidate and negative policies, full/representative ranking metrics, degree/age/cold-start slices, calibration and dependence-aware uncertainty.
- Mandate baseline/ablation, code/sampler/model identity and independent leakage review; block release when future structure or unrealistic candidates contaminate evidence.

**Follow-up probe:** Why is a random edge split especially misleading for a growing marketplace graph?

**Revision links:** [Graph ML and knowledge graphs]({{ '/interview-prep/cheat-sheets/graph-ml-knowledge-graphs/' | relative_url }})

### DSTL-B9-08 — Design a graph platform serving fraud, recommendations, and GraphRAG.

**Round:** Platform architecture · **Depth:** Lead

**Strong answer signals**

- Separate canonical typed/time-valid graph with provenance from task-specific point-in-time snapshots, feature/embedding pipelines and serving indexes.
- Provide authorized bounded traversal, sampling, versioned publication, entity merge/split and late-edge handling with deletion/revocation propagation and audit.
- Offer task-specific SLAs/fallbacks and monitor freshness, quality, degree/skew, latency/cost and incidents; avoid one schema or embedding silently serving incompatible purposes.

**Follow-up probe:** Which artifact identities must be atomic when publishing graph embeddings and an ANN index?

**Revision links:** [Graph ML and knowledge graphs]({{ '/interview-prep/cheat-sheets/graph-ml-knowledge-graphs/' | relative_url }})

### DSTL-B9-09 — Review a proposal to add GraphRAG to an enterprise assistant.

**Round:** Architecture review · **Depth:** Lead

**Strong answer signals**

- Demand a relationship/multi-hop use case and compare SQL/graph queries, metadata, lexical and vector baselines on a representative evaluation set.
- Review entity/relation extraction quality, provenance, temporal validity, ACL traversal, bounded expansion, deletion and graph-update ownership.
- Gate on seed/path/evidence recall, grounded answers, authorization violations, latency/token/cost and operational simplicity; reject if graph errors outweigh lift.

**Follow-up probe:** When might a deterministic graph query be preferable to learned subgraph retrieval?

**Revision links:** [Graph ML and knowledge graphs]({{ '/interview-prep/cheat-sheets/graph-ml-knowledge-graphs/' | relative_url }})

### DSTL-B9-10 — Lead a response to a knowledge-graph entity merge that contaminated recommendations.

**Round:** Data/model incident · **Depth:** Leadership

**Strong answer signals**

- Stop graph/embedding publication, identify merged entities, downstream snapshots/indexes/caches/models and affected recommendations, and preserve provenance/audit evidence.
- Split/correct entities under owner-approved rules, propagate invalidation/deletion through derived artifacts and verify repaired neighborhoods plus decision outcomes.
- Rebuild atomically, shadow/canary against known-good, notify stakeholders and add merge confidence, human review, reversible lineage and blast-radius checks.

**Follow-up probe:** Why is correcting the canonical node insufficient if embeddings remain cached?

**Revision links:** [Graph ML and knowledge graphs]({{ '/interview-prep/cheat-sheets/graph-ml-knowledge-graphs/' | relative_url }})

## Explainability, fairness, and responsible ML

### DSTL-B9-11 — Select an explanation strategy for developers, reviewers, and affected users.

**Round:** Responsible product design · **Depth:** Lead

**Strong answer signals**

- Map each audience to a task: developer debugging, reviewer evidence, user notice/contest/recourse; define accuracy, stability, actionability, privacy and language needs.
- Combine model-appropriate global inspection, local reason/attribution with fidelity limits and feasible counterfactual or supporting evidence where policy permits.
- Validate comprehension and misuse, version explanation with prediction/model/reference and provide appeal/human oversight rather than presenting association as causality.

**Follow-up probe:** Why might a technically faithful attribution still be unsuitable for an affected user?

**Revision links:** [Explainability, fairness, and responsible ML]({{ '/interview-prep/cheat-sheets/explainability-fairness-responsible-ml/' | relative_url }})

### DSTL-B9-12 — Choose fairness metrics for a capacity-constrained review system.

**Round:** Fairness decision · **Depth:** Lead

**Strong answer signals**

- Identify allocation and error harms, eligible population, sensitive/intersection groups, baseline process and whose decision/rights are affected with legal/policy owners.
- Compare selection rate, opportunity/equalized-odds, predictive value, calibration and utility under capacity, base-rate and measurement differences with denominators/uncertainty.
- Document why selected metrics fit the harm, unavoidable trade-offs, mitigation and residual risk; test downstream outcomes and review/appeal rather than optimizing a dashboard gap alone.

**Follow-up probe:** Why can equalized odds and calibrated probabilities conflict when base rates differ?

**Revision links:** [Explainability, fairness, and responsible ML]({{ '/interview-prep/cheat-sheets/explainability-fairness-responsible-ml/' | relative_url }})

### DSTL-B9-13 — Govern subgroup analysis when many intersections have small samples.

**Round:** Statistical governance · **Depth:** Lead

**Strong answer signals**

- Predeclare critical groups/metrics, report support/events and uncertainty, protect privacy and avoid treating no significant difference as proof of parity.
- Use pooled/hierarchical or multiplicity-aware analysis where appropriate, combine quantitative evidence with qualitative harm review and plan targeted data collection.
- Set owner-approved action thresholds and recurring review; never drop a vulnerable group solely because current data is inconveniently sparse.

**Follow-up probe:** How can minimum-cell privacy rules hide the group with the greatest potential harm?

**Revision links:** [Explainability, fairness, and responsible ML]({{ '/interview-prep/cheat-sheets/explainability-fairness-responsible-ml/' | relative_url }})

### DSTL-B9-14 — Establish a responsible-ML release and change-management process.

**Round:** Operating model · **Depth:** Leadership

**Strong answer signals**

- Tier systems by impact and require proportionate data/model lineage, intended use, validation, explanation/fairness, privacy/security, human oversight, rollback and owner approvals.
- Separate evidence creation, independent review and risk acceptance; record unresolved limits and block release when mandatory gates fail.
- Trigger re-review on data/population, label, threshold/policy, interface, vendor/dependency, law or incident changes and maintain monitoring, appeal and retirement workflows.

**Follow-up probe:** Who should be allowed to accept a fairness trade-off, and why not the model team alone?

**Revision links:** [Explainability, fairness, and responsible ML]({{ '/interview-prep/cheat-sheets/explainability-fairness-responsible-ml/' | relative_url }})

### DSTL-B9-15 — Respond when a mitigation improves parity but reduces calibration and business utility.

**Round:** Trade-off leadership · **Depth:** Leadership

**Strong answer signals**

- Revisit harm/decision objective and verify comparable data, thresholds, groups, uncertainty and downstream outcomes; do not choose the metric with the best optics.
- Present a frontier of fairness, calibration, error, capacity and user/business outcomes plus non-model product/process alternatives and affected-stakeholder implications.
- Route the explicit trade-off to accountable policy/legal/product owners, document decision/residual risk and use guarded rollout, monitoring and appeal if approved.

**Follow-up probe:** What non-model change could improve both fairness and utility in a review-capacity problem?

**Revision links:** [Explainability, fairness, and responsible ML]({{ '/interview-prep/cheat-sheets/explainability-fairness-responsible-ml/' | relative_url }})

## Survival, risk, pricing, and decision optimization

### DSTL-B9-16 — Choose between fixed-horizon classification and survival analysis for churn.

**Round:** Modeling strategy · **Depth:** Lead

**Strong answer signals**

- Define contractual/non-contractual churn, time origin, censoring/reactivation, action lead time and whether one or multiple horizons drive decisions.
- Fixed-horizon classification can be simple with matured labels; survival uses event timing/censoring and supports horizon curves but adds assumptions/evaluation complexity.
- Compare calibrated decision utility, follow-up support, intervention/selective-label effects and operational usability against simple baselines before standardizing.

**Follow-up probe:** When would a 90-day classifier incorrectly label a recent active customer as negative?

**Revision links:** [Survival, risk, pricing, and decision optimization]({{ '/interview-prep/cheat-sheets/survival-risk-pricing-decision-optimization/' | relative_url }})

### DSTL-B9-17 — Govern a risk model affected by selective approvals and delayed defaults.

**Round:** Risk governance · **Depth:** Lead

**Strong answer signals**

- Map eligibility, approval/review/intervention policy, outcome maturation and unobserved counterfactual labels; prevent recent unknowns from becoming negatives.
- Use policy/randomized or credible correction evidence where available, stress assumptions and keep a representative audited evaluation/monitoring set with calibration and loss metrics.
- Separate score from approval policy, require fairness/legal review, human appeal, drift/recalibration and conservative fallback when support or labels are inadequate.

**Follow-up probe:** Why can training only on approved applicants reverse conclusions about rejected applicants?

**Revision links:** [Survival, risk, pricing, and decision optimization]({{ '/interview-prep/cheat-sheets/survival-risk-pricing-decision-optimization/' | relative_url }})

### DSTL-B9-18 — Design a pricing experimentation and decision program.

**Round:** Causal product strategy · **Depth:** Lead

**Strong answer signals**

- Define margin/long-term objective, eligible unit, price support, inventory/substitution/competition, contracts and fairness/legal guardrails rather than conversion alone.
- Start with approved randomized price/promotion variation or defensible quasi-experiment, log propensities/policy and estimate heterogeneous response with uncertainty.
- Use bounded optimization/exploration, predeclared guardrails and rollback; monitor customer trust, retention, margin, mix and interference before scaling.

**Follow-up probe:** Why can a demand model trained on historical prices recommend the old policy rather than the best price?

**Revision links:** [Survival, risk, pricing, and decision optimization]({{ '/interview-prep/cheat-sheets/survival-risk-pricing-decision-optimization/' | relative_url }})

### DSTL-B9-19 — Set engineering and governance standards for optimization models.

**Round:** Decision systems leadership · **Depth:** Lead

**Strong answer signals**

- Require owner-approved variables, objective, units, hard/soft constraints, feasibility/fallback and input lineage before solver selection.
- Standardize formulation/data/solver identities, status/gap/tolerance reporting, reproducible cases, constraint tests, sensitivity/scenario and predict-then-optimize regret evidence.
- Separate recommendation from execution, define human override/rollback and incident review, and prohibit silent hard-constraint relaxation or stale-plan reuse.

**Follow-up probe:** Why should an optimal solver status not alone authorize execution?

**Revision links:** [Survival, risk, pricing, and decision optimization]({{ '/interview-prep/cheat-sheets/survival-risk-pricing-decision-optimization/' | relative_url }})

### DSTL-B9-20 — Prioritize a portfolio spanning forecasting, pricing, risk, and optimization.

**Round:** Portfolio leadership · **Depth:** Leadership

**Strong answer signals**

- Rank decisions by value, frequency, controllability, data/label maturity, causal support, constraint clarity, risk, integration effort and measurable baseline.
- Fund vertical slices that connect prediction to action and outcome, with simple policy/solver baselines, owner, stop criteria, evidence budget and shared platform only after repeated need.
- Sequence high-learning reversible work first, expose dependencies and reject projects where no owner can define/authorize the action or evaluate counterfactual impact.

**Follow-up probe:** Which project would you pause even if its predictive model already has excellent offline accuracy?

**Revision links:** [Survival, risk, pricing, and decision optimization]({{ '/interview-prep/cheat-sheets/survival-risk-pricing-decision-optimization/' | relative_url }})

## Completion evidence

- You can answer at least 16 of 20 questions in each batch without reading the signals first.
- Every answer includes one relevant metric, constraint, failure mode, or project example.
- You can compress an applied answer from two minutes to 45 seconds without losing the decision.
- You have recorded weak areas against the stable question IDs for later re-testing.
