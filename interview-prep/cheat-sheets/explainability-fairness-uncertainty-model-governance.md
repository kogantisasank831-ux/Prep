---
layout: "week"
status: "approved"
version: "0.1.0"
last_reviewed: "2026-11-11"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "Explainability, fairness, uncertainty, and model governance interview cheat sheet"
description: "Global and local explanations, explanation validation, uncertainty, calibration, conformal prediction, fairness harms and metrics, mitigation, evidence, release gates, and lifecycle governance."
summary: "Revise model assurance as an evidence chain connecting explanation questions, uncertainty and calibration, fairness harms and trade-offs, release decisions, human oversight, and monitoring."
permalink: "/interview-prep/cheat-sheets/explainability-fairness-uncertainty-model-governance/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 9 · Explainability, fairness, uncertainty, and governance"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 9 source-backed scope:** This approved page publishes the canonical interview sheet without altering its instructional body. It remains separate from the Week 1–20 learning assessments.

**Target roles:** Data Science Lead, Lead/Senior Data Scientist, Applied Scientist, ML Engineer, AI Engineer, Responsible AI Engineer  
**Use:** model-assurance, high-impact AI, evaluation, system-design, governance, leadership, and risk interviews  
**Interview rule:** start from the decision, affected people, intended and excluded use, harms, and accountable owner. An explanation, fairness score, confidence value, or policy document is evidence—not automatic proof that a system is safe or acceptable.

## 1. Thirty-second revision

- Interpretability is how understandable a model or mechanism is; explainability usually refers to methods that communicate why a prediction/model behaved as it did.
- Define the explanation audience and question: developer debugging, reviewer decision support, affected-person reason, regulator/auditor evidence, or global product understanding.
- Global explanations describe overall behavior; local explanations describe one prediction. Neither implies causality.
- Coefficients, trees, permutation importance, PDP/ICE/ALE, SHAP, LIME, counterfactuals, and saliency answer different questions and make different assumptions.
- Correlated features, unrealistic perturbations, unstable samples, baseline choice, and model interactions can make post-hoc explanations misleading.
- Uncertainty includes irreducible outcome noise, uncertainty from limited model/data knowledge, distribution shift, and measurement/label uncertainty.
- Calibration asks whether stated probabilities match observed frequencies. It is different from discrimination and must be checked by slice and time.
- Conformal methods can provide marginal coverage under exchangeability-related assumptions; they do not automatically guarantee conditional coverage for every subgroup or protect against arbitrary shift.
- Fairness begins with a harm and affected groups, not a metric menu. Allocation and quality-of-service harms often need different measurements.
- Demographic parity, equal opportunity, equalized odds, predictive parity, and calibration encode incompatible goals in many real settings. Select metrics from the decision and social/legal context.
- Evaluate intersections and sample uncertainty. A global average can hide a small harmed group.
- Governance ties requirements, exact artifacts, independent evaluation, approvals/exceptions, rollout, monitoring, appeal, incident response, rollback, and retirement into an auditable lifecycle.

## 2. Model-assurance contract

Before metrics, document:

| Field | Questions |
|---|---|
| decision and owner | What decision uses the output? Who is accountable? |
| intended use | Population, context, action, scale, and users supported |
| excluded use | Populations, geographies, modalities, or decisions not supported |
| affected parties | Who receives benefits, errors, delays, surveillance, or denial? |
| harm model | What can go wrong, for whom, and how severe/reversible is it? |
| human role | Can a reviewer understand, override, defer, and appeal? |
| evidence boundary | Which exact model, data, configuration, and environment were tested? |
| release criteria | Required performance, slices, robustness, safety, fairness, latency, and operations evidence |
| monitoring | Signals, windows, owners, escalation, and delayed-outcome evaluation |
| recovery | Safe default, rollback, incident response, and retirement |

There is no universal set of fairness or uncertainty thresholds. They must be predeclared from the use case, regulation/policy, harm tolerance, baseline performance, and action constraints.

## 3. Interpretability and explanation questions

### Choose the question first

- **How does the model behave globally?** Coefficients, tree structure, permutation importance, PDP/ALE, global surrogate, error slices.
- **Why this output?** Local attribution, local surrogate, example-based explanation, counterfactual.
- **What would change the decision?** Actionable counterfactual under feasibility/causal constraints.
- **Which training examples mattered?** Influence or nearest-example methods, with privacy and approximation caveats.
- **What concept/region drives a neural output?** Saliency, Integrated Gradients, concept activation, occlusion.
- **Is the model using a forbidden shortcut?** feature ablation, counterfactual data, subgroup tests, challenge sets, causal/domain investigation.

An explanation should include model/output version, feature definitions and values as known at decision time, reference/background population, method/parameters, stability, and limitations.

## 4. Intrinsic models and common global methods

### Intrinsic interpretability

Linear/logistic models, small decision trees, generalized additive models, monotonic models, rule lists, and scorecards can be understandable by design.

Caveats:

- a coefficient depends on units, link function, regularization, interactions, and correlated covariates;
- a sparse model can still use proxies or leaked features;
- a small tree may be unstable under data changes;
- monotonicity encodes a directional constraint, not causal truth;
- “simple model” does not mean “fair” or “correct.”

For high-impact decisions, compare a constrained/interpretable baseline with complex candidates. Require measurable benefit for added complexity.

### Permutation importance

Shuffle one feature and measure performance degradation. It is model-agnostic and tied to a chosen dataset/metric.

Problems:

- correlated features can substitute for each other, understating importance;
- shuffling can create unrealistic combinations;
- results depend on test population, metric, repeats, and grouping;
- importance describes prediction reliance, not causal effect.

Group related features or use conditional/domain-respecting perturbations when justified.

### PDP, ICE, and ALE

- Partial dependence plot (PDP) averages predictions while varying a feature.
- Individual conditional expectation (ICE) draws a curve per example and exposes heterogeneity.
- Accumulated local effects (ALE) uses local changes within observed regions and is often less vulnerable to extrapolated combinations.

PDP/ICE commonly assume feature manipulation that can be implausible when variables are correlated. Always show data support/rug plots, important interactions, slice behavior, and uncertainty.

## 5. Local post-hoc explanations

### SHAP-style feature attribution

Shapley-value explanations allocate the difference between a prediction and a reference expectation among features under a specified value function/background distribution.

Strengths:

- additive local decomposition;
- model-specific efficient algorithms exist;
- can aggregate local attributions for global views.

Caveats:

- background population defines the baseline;
- conditional versus interventional feature treatment answers different questions;
- correlated features make credit allocation ambiguous;
- approximate explainers have sampling/model assumptions;
- an attribution is not the effect of intervening on the real world.

### LIME/local surrogates

Perturb near an example, query the model, weight samples by locality, and fit an interpretable surrogate. Validate local fidelity and stability across seeds/kernel widths. Perturbations may be off-manifold, especially for text, images, categorical, or correlated tabular data.

### Counterfactual explanations

Find a nearby feasible input that changes the output. Useful properties:

- valid: output actually changes;
- proximal: small meaningful change;
- sparse: few changes;
- feasible/actionable: respects immutable variables and constraints;
- plausible: stays on data/domain manifold;
- diverse: offers alternatives;
- stable: small model changes do not reverse advice.

A predictive counterfactual is not automatically causal. Changing debt ratio in a record does not guarantee a real intervention causes approval. Avoid suggesting actions outside a person's control or revealing gaming vulnerabilities.

### Neural-network attribution

Saliency/gradients, Integrated Gradients, DeepLIFT, occlusion, Grad-CAM, and concept methods attribute neural outputs to inputs/layers/concepts.

Validate with:

- sanity checks under randomized model parameters/labels;
- deletion/insertion or occlusion tests;
- multiple baselines;
- input transformations that should preserve semantics;
- expert review and known shortcut cases.

Visually appealing heatmaps can be insensitive, noisy, or architecture-driven.

## 6. Explanation validation

An explanation method needs its own evaluation:

| Property | Test |
|---|---|
| fidelity | does the explanation approximate the actual model locally/globally? |
| stability | do similar inputs/runs produce appropriately similar explanations? |
| sensitivity | does it react when model behavior or relevant features change? |
| sparsity/comprehensibility | can the intended user act without losing critical nuance? |
| data realism | are perturbations/references supported by the domain? |
| usefulness | does it improve debugging, review accuracy, or contestability? |
| security/privacy | can it expose sensitive data, model details, or gaming paths? |

Do not optimize explanation satisfaction alone; persuasive explanations can increase inappropriate trust.

## 7. Uncertainty taxonomy

### Sources

- **Aleatoric uncertainty:** irreducible variability/noise conditional on inputs; can be heteroscedastic.
- **Epistemic uncertainty:** limited data/model knowledge; can reduce with informative data but is hard to identify exactly.
- **Distributional uncertainty:** deployment input/relationship differs from evaluation data.
- **Measurement/label uncertainty:** noisy sensors, ambiguous adjudication, delayed or censored outcomes.
- **Decision uncertainty:** uncertain utility, cost, capacity, or policy response even when predictive uncertainty is known.

Softmax probability is not a complete uncertainty estimate. Neural models can be highly confident on unfamiliar inputs.

### Practical techniques

| Technique | Captures/approximates | Caveat |
|---|---|---|
| calibrated probabilities | frequency-aligned predictive probabilities | can fail by slice/time/shift |
| ensembles | variation across fitted models | compute/storage; shared bias |
| Bayesian posterior/predictive | parameter and predictive uncertainty under model/prior | approximation and misspecification |
| MC dropout | stochastic predictive variation | approximation; setup sensitive |
| quantile regression | conditional outcome quantiles | crossing/calibration and coverage |
| conformal prediction | prediction sets/intervals with marginal coverage under assumptions | set efficiency and exchangeability |
| OOD detector | departure from reference representation/data | no universal OOD score |
| abstention/selective prediction | defer uncertain/high-risk cases | coverage, queue capacity, fairness |

Uncertainty should change an action: wider interval, human review, safer fallback, more data, or refusal.

## 8. Calibration

A binary predictor is calibrated if, among cases assigned probability near `p`, roughly fraction `p` are positive over the relevant population.

Evaluate:

- reliability diagram with counts per bin;
- Brier score and log loss;
- expected calibration error (ECE) as a summary, with bin sensitivity disclosed;
- calibration intercept/slope where appropriate;
- overall and per important slice/time period;
- discrimination alongside calibration.

Brier/log loss combine aspects beyond calibration alone. ECE hides within-bin variation and depends on binning. Reliability diagrams without sample counts can mislead.

Calibration methods:

- sigmoid/Platt scaling;
- isotonic regression;
- temperature scaling for logits;
- multiclass-specific methods.

Fit the calibrator on data not used to fit base-model parameters, and test on a separate representative set. If prevalence or relationships change, calibration may break even when ranking is stable.

## 9. Conformal prediction and coverage

Split conformal regression concept:

1. train a base model on a training set;
2. compute nonconformity residuals on a separate calibration set;
3. choose an appropriate finite-sample residual quantile;
4. add that radius to future point predictions.

Under exchangeability and correct procedure, conformal prediction offers marginal coverage. Important limitations:

- marginal 90% coverage does not mean 90% coverage for every subgroup/input;
- distribution shift, dependence, time series, and adaptive feedback can violate assumptions;
- small calibration sets create coarse/unstable quantiles;
- intervals can be too wide to be useful;
- repeated decisions and selective action require careful analysis.

Use group-conditional/Mondrian, weighted, time-series, or adaptive variants only with their specific assumptions and evidence. Always report empirical coverage and interval/set size by slice.

## 10. Minimal dependency-free example: expected calibration error

```python
from __future__ import annotations

from typing import Sequence


def expected_calibration_error(
    labels: Sequence[int],
    probabilities: Sequence[float],
    *,
    bins: int = 10,
) -> float:
    """Compute equal-width binary ECE for educational use."""
    if len(labels) != len(probabilities) or not labels:
        raise ValueError("labels and probabilities must have equal nonzero length")
    if bins < 1:
        raise ValueError("bins must be positive")
    if any(label not in (0, 1) for label in labels):
        raise ValueError("labels must be binary")
    if any(not 0.0 <= probability <= 1.0 for probability in probabilities):
        raise ValueError("probabilities must lie in [0, 1]")

    total = len(labels)
    error = 0.0
    for bin_index in range(bins):
        lower = bin_index / bins
        upper = (bin_index + 1) / bins
        members = [
            index
            for index, probability in enumerate(probabilities)
            if lower <= probability < upper
            or (bin_index == bins - 1 and probability == 1.0)
        ]
        if not members:
            continue
        average_confidence = sum(probabilities[i] for i in members) / len(members)
        observed_rate = sum(labels[i] for i in members) / len(members)
        error += (len(members) / total) * abs(average_confidence - observed_rate)
    return error


perfect_labels = [0, 0, 1, 1]
perfect_probabilities = [0.0, 0.0, 1.0, 1.0]
assert expected_calibration_error(perfect_labels, perfect_probabilities, bins=2) == 0.0

uncalibrated = expected_calibration_error(
    [0, 0, 1, 1],
    [0.4, 0.4, 0.6, 0.6],
    bins=2,
)
assert abs(uncalibrated - 0.4) < 1e-12
```

ECE should not be used alone. Report the diagram, counts, binning, proper scores, uncertainty, and slices.

## 11. Fairness starts with harms

### Common harm types

- **Allocation:** opportunity/resource is withheld or granted.
- **Quality of service:** error, latency, or accessibility differs across groups.
- **Stereotyping/representation:** outputs demean, erase, or reinforce harmful associations.
- **Privacy/surveillance:** data collection or inference disproportionately burdens groups.
- **Feedback and long-term harm:** decisions alter future data/opportunity.
- **Contestability:** affected people cannot understand, correct, or appeal.

Identify protected and affected groups, including intersections. Sensitive attributes may be missing, inaccurate, fluid, or legally restricted. Not measuring them can also hide disparities; decide with privacy, legal, and domain review.

### Bias sources

- historical inequity in outcomes;
- selection and coverage gaps;
- measurement/proxy bias;
- label/adjudication bias;
- aggregation across different populations;
- feature leakage or proxy discrimination;
- optimization objective and threshold;
- deployment access, human override, and feedback loops.

A model can accurately reproduce an unjust label. Better predictive performance does not resolve construct validity.

## 12. Fairness metrics and trade-offs

Let sensitive group be `A`, prediction `Ŷ`, and outcome `Y`.

| Concept | Rough requirement | Appropriate question | Caveat |
|---|---|---|---|
| demographic parity | `Ŷ` rate independent of `A` | are benefits allocated at similar rates? | ignores qualification/outcome |
| equal opportunity | true-positive rate similar across groups | are qualified positives recognized similarly? | ignores false-positive disparity |
| equalized odds | TPR and FPR similar | are error rates comparable? | may require group-aware decisions |
| predictive parity | precision similar | is a positive decision equally reliable? | conflicts under differing base rates |
| calibration by group | same score means same observed rate | is risk score interpretable similarly? | can coexist with unequal errors |
| individual fairness | similar people treated similarly | is the similarity definition defensible? | metric is difficult and normative |
| counterfactual fairness | decision stable under a causal protected-attribute counterfactual | would protected identity causally change output? | requires strong causal model |

When base rates differ and prediction is imperfect, several desirable group criteria generally cannot all hold simultaneously. Do not hide the trade-off in a composite score.

Assessment sequence:

1. identify harm and groups with affected stakeholders/domain experts;
2. validate label/construct and data coverage;
3. choose performance and fairness measures tied to harm;
4. compute disaggregated and intersectional results with sample counts/uncertainty;
5. compare model, baseline, and full decision pipeline;
6. investigate error examples and mechanisms;
7. evaluate mitigation trade-offs and downstream effects;
8. document unresolved risks and decision/owner.

Avoid declaring a system “fair” from a threshold rule alone. A numeric screen is not a legal conclusion.

## 13. Mitigation strategies

### Pre-processing

- improve sampling/coverage and measurement;
- repair labels or use multiple adjudicators;
- reweight/resample;
- remove or transform features after proxy analysis;
- learn representations with constraints.

### In-processing

- fairness-constrained optimization;
- adversarial debiasing;
- cost-sensitive objectives;
- monotonicity or other domain constraints;
- multi-objective optimization.

### Post-processing

- threshold/decision adjustment;
- calibrated equalized-odds-style procedures;
- human review or abstention;
- resource/capacity policy changes.

Removing a protected attribute does not remove proxies. Group-specific thresholds can reduce some disparities but may be restricted, contested, or harmful in context. Evaluate utility, calibration, privacy, individual impacts, and operational behavior after mitigation.

## 14. Governance across the lifecycle

### Evidence chain

`requirement → dataset/label version → training run → candidate artifact → evaluation bundle → approval/exception → release → monitoring → incident/rollback → retirement`

The release candidate must be immutable and identifiable: model weights, preprocessing, features, rules, prompt/configuration where relevant, thresholds, calibrator, runtime, dependencies, and serving contract.

### Model/data documentation

A model card should cover:

- identity/version and owners;
- intended and excluded use;
- training/evaluation data provenance and limitations;
- metrics with slices and uncertainty;
- fairness, robustness, security, privacy, and explainability evidence;
- ethical/safety considerations;
- operational requirements and monitoring;
- known limitations and change history.

A data card/datasheet records collection, consent/licensing, population, schema, labels, transformations, quality, sensitive fields, retention, and known gaps.

### Release gates

Define before final evaluation:

- representative test population and untouched data;
- baseline and required practical improvement;
- safety/quality floors by critical slice;
- calibration/uncertainty and abstention behavior;
- robustness and shift/challenge testing;
- fairness/harm assessment;
- latency, throughput, availability, and cost;
- reproducible artifact/environment;
- human workflow and appeal;
- monitoring, rollback, and incident owner.

Evidence should be independently reproducible when risk warrants it. A waiver records criterion, owner, rationale, scope, expiry, compensating controls, and follow-up; it is not silent approval.

### Post-deployment

Monitor both leading and delayed signals:

- input/feature/label quality and drift;
- output/score/calibration/coverage;
- slice performance and disparities;
- abstention, override, appeal, and incident rates;
- business outcome and unintended effects;
- latency, availability, cost, and security;
- unresolved labels and feedback representativeness.

Use staged rollout, shadow/canary evaluation, safe defaults, rollback drills, and periodic revalidation. Material changes to data, model, threshold, workflow, population, or regulation should trigger change review.

## 15. Library and framework map

| Tool | Best fit | Verify |
|---|---|---|
| scikit-learn inspection | permutation importance, PDP/ICE, calibration | feature dependence and scoring semantics |
| SHAP | additive feature attribution | explainer, background, output scale, dependence assumptions |
| Captum | PyTorch neural attribution | baseline/layer/method and sanity tests |
| InterpretML | glass-box and explanation workflows | estimator limitations and fidelity |
| Fairlearn | disaggregated metrics and mitigation | harm-to-metric mapping and intersections |
| AI Fairness 360 | fairness metrics/algorithms | method assumptions and maintenance/version |
| MAPIE | conformal-style intervals/sets for sklearn models | coverage assumptions and API/version |
| NIST AI RMF/AIRC | risk-governance structure and resources | adapt to organizational/legal context |
| MLflow/model registry | lineage, artifacts, approvals | immutable linkage and access controls |

Tools calculate evidence; accountable teams interpret and govern it.

## 16. Rapid interview questions

**Feature importance versus explanation?**  
Importance ranks performance reliance or attribution under a method; an explanation must answer a specific audience's question with context and limitations.

**Does SHAP show causality?**  
No. It allocates model output relative to a reference/value function. It does not prove real-world intervention effects.

**Why can PDP be misleading?**  
It may evaluate impossible combinations when the varied feature is correlated with others and can average away heterogeneous effects.

**Accuracy versus calibration?**  
Accuracy/discrimination concerns correct ordering/classes; calibration concerns whether probabilities correspond to observed frequencies.

**What does 90% conformal coverage mean?**  
Under the method's assumptions, long-run marginal coverage is targeted. It does not mean every subgroup or individual has 90% conditional coverage.

**Can one fairness metric prove fairness?**  
No. Metrics encode specific harm assumptions, data/labels may be biased, criteria conflict, and the full sociotechnical workflow matters.

**Why evaluate intersections?**  
Aggregate group metrics can hide harm at combinations such as age-region-language or gender-disability.

**What is a model release gate?**  
A predeclared, executable decision rule linking the exact candidate to required evidence, owners, exceptions, and deployment controls.

**When should a model abstain?**  
When inputs are invalid/out of supported scope, uncertainty is too high for the harm level, or required evidence/context is missing—and a safe alternative exists.

## 17. Lead-level case: high-impact eligibility model

Structure the answer:

1. Clarify the benefit/resource, legal/policy context, population, decision owner, affected people, human review, and appeal/correction process.
2. Challenge label construct validity: historical approval is not necessarily qualification or future benefit.
3. Define intended/excluded use and harm scenarios; involve domain, legal/privacy, operations, and affected-stakeholder expertise.
4. Build a simple interpretable baseline and a complex challenger; require practical benefit for complexity.
5. Use temporally and geographically representative evaluation with identity-safe splitting and point-in-time features.
6. Report discrimination, calibration, decision utility, uncertainty/abstention, data coverage, and error slices with intervals.
7. Select fairness metrics from allocation/error harms, examine intersections and thresholds, and evaluate the human/model pipeline.
8. Validate explanations with fidelity/stability and provide specific reason/recourse information without exposing sensitive data or false causal advice.
9. Predeclare release gates; independently reproduce the exact artifact; document exceptions and approvals.
10. Shadow, canary, monitor appeals/overrides/outcomes/disparities, audit non-selected cases where feasible, and preserve rollback/manual processing.

A lead should be willing to recommend no deployment when labels, recourse, evaluation coverage, or harm controls are inadequate.

## 18. Final checklist

- [ ] I define decision, audience, intended/excluded use, affected parties, and harm.
- [ ] I distinguish global/local, intrinsic/post-hoc, predictive/causal explanations.
- [ ] I know the questions and limitations of permutation, PDP/ICE/ALE, SHAP/LIME, counterfactual, and saliency methods.
- [ ] I validate explanation fidelity, stability, realism, usefulness, privacy, and security.
- [ ] I distinguish calibration, discrimination, uncertainty, shift, and abstention.
- [ ] I understand marginal conformal coverage and its assumptions.
- [ ] I choose fairness metrics from harms and report intersectional uncertainty.
- [ ] I do not treat attribute removal or one metric as proof of fairness.
- [ ] I link exact artifacts to independent evidence and predeclared release gates.
- [ ] I design monitoring, appeals, incident response, rollback, and retirement.

## 19. Primary references

- [scikit-learn permutation feature importance](https://scikit-learn.org/stable/modules/permutation_importance.html)
- [scikit-learn partial dependence and ICE](https://scikit-learn.org/stable/modules/partial_dependence.html)
- [scikit-learn probability calibration](https://scikit-learn.org/stable/modules/calibration.html)
- [SHAP documentation](https://shap.readthedocs.io/en/latest/)
- [Captum attribution documentation](https://captum.ai/docs/attribution_algorithms)
- [Fairlearn fairness assessment](https://fairlearn.org/main/user_guide/assessment/perform_fairness_assessment.html)
- [Fairlearn common fairness metrics](https://fairlearn.org/main/user_guide/assessment/common_fairness_metrics.html)
- [IBM AI Fairness 360 documentation](https://aif360.readthedocs.io/en/latest/)
- [MAPIE conformal-prediction foundations](https://mapie.readthedocs.io/en/stable/content/conformal-prediction/theory/)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [NIST AI RMF Playbook](https://airc.nist.gov/airmf-resources/playbook/)
- [Mitchell et al., Model Cards for Model Reporting](https://research.google/pubs/model-cards-for-model-reporting/)
- [Gebru et al., Datasheets for Datasets](https://doi.org/10.1145/3458723)
- [Ribeiro, Singh, and Guestrin, “Why Should I Trust You?”](https://doi.org/10.1145/2939672.2939778)
- [Sundararajan, Taly, and Yan, Axiomatic Attribution for Deep Networks](https://proceedings.mlr.press/v70/sundararajan17a.html)
