---
layout: "week"
status: "review"
version: "1.1.0"
last_reviewed: "2026-11-09"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "Data Science Technical Lead foundation interview bank"
description: "Twenty guided foundation questions for Data Science Technical Lead interviews."
summary: "Practise problem framing, experimentation, model decisions, validation, production governance, prioritization, mentoring, and technical leadership."
permalink: "/interview-prep/roles/data-science-technical-lead/"
kicker_primary: "Data Science Technical Lead"
kicker_secondary: "Batches 1–2 · 40 guided questions"
current_label: "Role bank"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
question_count: 40
---
## How to use this bank

These are interview-practice prompts, not a scored learning assessment. Answer aloud before opening the revision links. A strong response should state assumptions, make a decision, explain trade-offs, and identify evidence or failure modes. Use the follow-up probe to test whether the answer survives a deeper round.

### Suggested practice loop

1. Select five questions from different sections.
2. Give a 90-second answer without notes.
3. Compare your answer with the strong-answer signals.
4. Open only the revision sheet needed for the gap.
5. Repeat the answer in 45 seconds, then record one concrete project example.

**Bank size:** 40 questions across Batches 1–2 · **Status:** Batch 1 approved; Batch 2 review candidate

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


## Completion evidence

- You can answer at least 16 of 20 questions in each batch without reading the signals first.
- Every answer includes one relevant metric, constraint, failure mode, or project example.
- You can compress an applied answer from two minutes to 45 seconds without losing the decision.
- You have recorded weak areas against the stable question IDs for later re-testing.
