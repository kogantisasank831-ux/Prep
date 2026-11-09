---
layout: "week"
status: "review"
version: "1.3.0"
last_reviewed: "2026-11-09"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "Data Science Technical Lead foundation interview bank"
description: "Eighty guided questions for Data Science Technical Lead interviews."
summary: "Practise framing, ML and LLM decisions, RAG leadership, agent strategy, LangGraph governance, framework portfolios, protocols, security, and operating models."
permalink: "/interview-prep/roles/data-science-technical-lead/"
kicker_primary: "Data Science Technical Lead"
kicker_secondary: "Batches 1–4 · 80 guided questions"
current_label: "Role bank"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
question_count: 80
---
## How to use this bank

These are interview-practice prompts, not a scored learning assessment. Answer aloud before opening the revision links. A strong response should state assumptions, make a decision, explain trade-offs, and identify evidence or failure modes. Use the follow-up probe to test whether the answer survives a deeper round.

### Suggested practice loop

1. Select five questions from different sections.
2. Give a 90-second answer without notes.
3. Compare your answer with the strong-answer signals.
4. Open only the revision sheet needed for the gap.
5. Repeat the answer in 45 seconds, then record one concrete project example.

**Bank size:** 80 questions across Batches 1–4 · **Status:** Batches 1–3 approved · Batch 4 review candidate

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

## Completion evidence

- You can answer at least 16 of 20 questions in each batch without reading the signals first.
- Every answer includes one relevant metric, constraint, failure mode, or project example.
- You can compress an applied answer from two minutes to 45 seconds without losing the decision.
- You have recorded weak areas against the stable question IDs for later re-testing.
