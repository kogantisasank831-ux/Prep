---
layout: "week"
status: "approved"
version: "1.0.0"
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
kicker_secondary: "Batch 1 · 20 guided questions"
current_label: "Role bank"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
question_count: 20
---
## How to use this bank

These are interview-practice prompts, not a scored learning assessment. Answer aloud before opening the revision links. A strong response should state assumptions, make a decision, explain trade-offs, and identify evidence or failure modes. Use the follow-up probe to test whether the answer survives a deeper round.

### Suggested practice loop

1. Select five questions from different sections.
2. Give a 90-second answer without notes.
3. Compare your answer with the strong-answer signals.
4. Open only the revision sheet needed for the gap.
5. Repeat the answer in 45 seconds, then record one concrete project example.

**Bank size:** 20 questions · **Batch:** 1 core foundations · **Status:** approved

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

## Completion evidence

- You can answer at least 16 of 20 questions without reading the signals first.
- Every answer includes one relevant metric, constraint, failure mode, or project example.
- You can compress an applied answer from two minutes to 45 seconds without losing the decision.
- You have recorded weak areas against the stable question IDs for later re-testing.
