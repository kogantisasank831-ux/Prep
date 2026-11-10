---
layout: "week"
status: "review"
version: "1.1.0"
last_reviewed: "2026-11-10"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "Experimentation and causal inference interview cheat sheet"
description: "Causal contracts, power, trustworthy experiments, ratio metrics, CUPED, sequential decisions, interference, DAGs, observational identification, uplift, and implementation."
summary: "Revise causal decisions from estimand and assignment through telemetry, inference, identification assumptions, heterogeneous effects, and production evidence."
permalink: "/interview-prep/cheat-sheets/experimentation-causal-inference/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 8 · Expanded experimentation and causality"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 8 source:** This review candidate updates the prepared `25_Experimentation_Causal_Inference_Interview_Cheat_Sheet.md` artifact in the Prep site. It is separate from the Week 1–20 learning assessments.

**Target roles:** Lead Data Scientist, Senior Data Scientist, Applied Scientist, Product Data Scientist, ML/AI Engineer  
**Use:** statistics, product experimentation, causal-inference, modeling-case, system-design, and leadership interviews  
**Interview rule:** begin with the decision and target estimand. A sophisticated estimator cannot repair an undefined outcome, broken randomization, post-treatment filtering, or an implausible causal assumption.

## 1. Thirty-second revision

- Define the user/business decision, treatment, outcome, population, unit, exposure rule, time window, and causal estimand before choosing a test.
- Randomize at the unit where interference and implementation permit; analyze uncertainty at the unit that was randomized.
- Predeclare the primary metric, guardrails, diagnostic metrics, minimum detectable effect, duration, and stopping rule.
- Validate assignment and telemetry before reading treatment effects: A/A behavior, invariant metrics, exposure counts, and sample-ratio mismatch.
- Prefer intention-to-treat for the primary estimate; treatment-on-the-treated needs additional assumptions or an instrument.
- Report absolute effect, relative effect, uncertainty interval, practical significance, and decision—not only a p-value.
- Peeking inflates false positives unless the design uses a valid sequential method. A fixed-horizon test is not sequential merely because a dashboard refreshes.
- CUPED can reduce variance using a pre-treatment covariate correlated with the outcome; never use a variable affected by treatment.
- In observational studies, draw the causal graph and state the identification assumptions before matching, regression, weighting, or machine learning.
- Distinguish confounders, mediators, and colliders. Adjusting for the wrong variable can create bias.
- Check overlap, balance, sensitivity, pre-trends, placebo outcomes/treatments, and estimate stability. These checks support an argument; they do not prove untestable assumptions.
- Heterogeneous treatment effects are useful only when discovered and evaluated with honest sample splitting, shrinkage, multiplicity control, and an actionable policy.

## 2. Start with the causal contract

Write one sentence:

> For **population P**, what is the effect of assigning **treatment T** rather than **control C** on **outcome Y** over **window W**, measured at **unit U**, under **policy and interference assumptions A**?

Key terms:

| Term | Meaning | Interview trap |
|---|---|---|
| Experimental unit | entity independently assigned to a variant | randomizing sessions when users cross sessions |
| Exposure | opportunity to experience the treatment | conditioning on a post-treatment click |
| Outcome | behavior/value the decision should change | optimizing a proxy with no business link |
| Estimand | precise causal quantity being targeted | saying “impact” without population or contrast |
| ATE | average effect in the target population | averaging away important constraints or harm |
| ATT | average effect among treated units | confusing it with ATE after selective treatment |
| CATE | effect conditional on characteristics $X=x$ | treating noisy subgroups as personalized truth |
| ITT | effect of assignment, regardless of compliance | excluding non-compliers and breaking randomization |

Potential-outcome notation:

- Potential outcomes: `Y_i(1)` and `Y_i(0)`
- Individual effect: `τ_i = Y_i(1) − Y_i(0)`

Only one potential outcome is observed for each unit. Randomization makes treatment independent of potential outcomes in expectation, enabling:

`estimated ATE = mean(Y_T) − mean(Y_C)`

State assumptions when relevant: consistency, positivity/overlap, no unmeasured confounding for observational adjustment, and an interference model. “SUTVA” is shorthand, not a substitute for describing spillovers and treatment versions.

## 3. Experiment design sequence

1. **Decision:** what changes if the result is positive, negative, or inconclusive?
2. **Hypothesis and mechanism:** why should the treatment move the outcome?
3. **Population and eligibility:** who can enter, and when?
4. **Randomization unit:** user, account, household, store, region, query, creator, or time block.
5. **Assignment and exposure:** preserve assignment logs separately from triggered exposure.
6. **Variants and allocation:** include ramp plan, mutual exclusions, and interacting experiments.
7. **Metrics:** one primary outcome; guardrails; mechanism and data-quality diagnostics.
8. **Power:** baseline variance/rate, α, power, MDE, allocation, clustering, attrition.
9. **Duration:** cover operational cycles and delayed outcomes, not merely required sample size.
10. **Analysis plan:** estimator, variance method, missing-data handling, multiplicity, slices, stopping.
11. **Launch safety:** A/A checks, instrumentation validation, staged ramp, kill conditions.
12. **Decision record:** estimate, interval, risks, heterogeneity, limitations, and follow-up.

For clustered assignment, effective information is lower when observations within clusters correlate. A common approximation is `DE = 1 + (m−1)ρ`, where `m` is average cluster size and `ρ` is intra-cluster correlation. Use cluster-aware power and standard errors rather than applying this approximation blindly to unequal clusters.

## 4. Power, MDE, and effect reporting

For two equally sized groups and a continuous outcome, a planning approximation is:

`n_group ≈ 2σ²(z_(1−α/2) + z_(1−β))² / δ²`

Here `δ` is the minimum detectable absolute effect. For proportions, use the variance appropriate to the expected rates. Planning inputs are estimates, so run sensitivity scenarios.

Power depends on:

- outcome variance or baseline rate;
- MDE worth acting on;
- Type I error `α` and desired power `1−β`;
- treatment allocation;
- unit and clustering;
- repeated measures, CUPED, and estimator choice;
- attrition, non-compliance, and multiple comparisons.

Report:

- control and treatment sample sizes;
- control baseline;
- absolute effect with unit;
- relative effect with a defined denominator;
- confidence/credible interval and analysis method;
- guardrail and slice results;
- whether the test was powered for the observed magnitude;
- practical decision and remaining uncertainty.

A non-significant result is not proof of no effect. Ask whether the interval excludes effects that matter.

## 5. Trustworthiness checks before outcome interpretation

### Sample-ratio mismatch

Compare observed allocation counts with the configured allocation using a predeclared goodness-of-fit test. SRM is a symptom, not a correction target. Investigate assignment, eligibility, redirects, identifier instability, logging loss, joins, bot filtering, ramp changes, and post-assignment segmentation. Do not simply reweight unexplained SRM away.

### A/A and invariant checks

- A/A tests exercise assignment, exposure, logging, metrics, and false-positive calibration.
- Invariant metrics such as pre-treatment attributes should not change causally.
- Run balance checks as diagnostics; do not repeatedly rerandomize until every covariate is “significant.”
- Reconcile counts from assignment to exposure to outcome tables.

### Common failure modes

| Failure | Why it biases or weakens the result | Better response |
|---|---|---|
| Peeking at fixed-horizon p-values | raises false-positive probability | fixed stop or valid sequential design |
| Post-treatment filtering | conditions on treatment consequences | ITT; pre-treatment eligibility |
| Survivorship/attrition | missingness differs by treatment/outcome | measure attrition; bounds/sensitivity |
| Novelty/learning effects | early response differs from steady state | inspect time profile; run long enough |
| Seasonality/event shocks | period is unrepresentative | concurrent control; planned duration |
| Interference | one unit affects another | cluster/switchback/network design |
| Metric logging changes | treatment alters measurement | invariant telemetry and source reconciliation |
| Multiple slicing | winner’s curse and false discoveries | predeclare; adjust; validate independently |
| Unit mismatch | standard errors are too small | analyze/cluster at assignment unit |

## 6. Ratio metrics and variance reduction

Ratios such as clicks/impressions are not generally equivalent to averaging per-user ratios. Define the estimand first: ratio of totals, average user ratio, or another business quantity. Use an estimator and variance method appropriate to dependence—delta method, cluster-robust variance, or a unit-level/bootstrap design that reproduces assignment.

For CUPED, let `X` be a pre-treatment covariate:

`Y_cv = Y − θ(X − mean(X))`, where `θ = Cov(Y, X) / Var(X)`.

Randomization preserves unbiasedness when the adjustment is pre-treatment and the implementation is correct. Fit/define the adjustment without using treatment-induced information. Recheck missingness, stability, and whether one common coefficient matches the analysis plan.

Other variance-reduction approaches include stratification, regression adjustment, repeated-measures models, triggered metrics with careful eligibility, and covariate-adaptive designs. Do not change the estimand merely to obtain a smaller p-value.

## 7. Sequential tests, multiple testing, and adaptive allocation

- **Fixed horizon:** analyze at the predeclared information/time boundary.
- **Group sequential:** planned interim looks with alpha spending or boundaries.
- **Always-valid/e-process methods:** support continuous monitoring under their assumptions.
- **Bayesian monitoring:** requires a prior, loss/decision rule, and operating-characteristic checks; it is not automatically immune to optional stopping concerns.
- **Multiple outcomes/variants/slices:** control family-wise error or false discovery where the decision family requires it; separate confirmatory from exploratory analysis.
- **Bandits:** optimize cumulative reward while learning, but can complicate unbiased inference, delayed outcomes, non-stationarity, guardrails, and reproducibility.

Choose an A/B test for clean causal estimation, a bandit for online allocation under exploration costs, and contextual/policy learning only when the action space, feedback, safety, and evaluation support it.

## 8. When ordinary user-level A/B testing does not fit

| Design | Use when | Main risks/checks |
|---|---|---|
| Cluster randomization | spillovers within teams, stores, schools | few clusters, imbalance, cluster variance |
| Switchback | marketplace/operations treatment applies by time | carryover, autocorrelation, block length |
| Geo experiment | media or policy assigned by region | matching, spillover, regional shocks |
| Factorial | estimate effects/interactions efficiently | interaction power, operational complexity |
| Stepped wedge | staged cluster rollout is required | time confounding and carryover |
| Encouragement/IV | assignment affects adoption, not treatment directly | exclusion, relevance, monotonicity |

## 9. Causal graphs and observational identification

Use a DAG to encode the causal story:

- **Confounder:** causes treatment and outcome; often needs adjustment.
- **Mediator:** lies on the causal path; adjust only for a direct-effect estimand.
- **Collider:** is caused by two variables; conditioning can open a spurious path.
- **Instrument:** changes treatment, affects outcome only through treatment under strong assumptions.

Identification asks whether the causal estimand can be expressed from observed data under assumptions. Estimation computes that expression. A predictive model with high accuracy does not identify a causal effect.

| Method | Core identifying idea | Frequent failure |
|---|---|---|
| Outcome regression | outcome model removes observed confounding | misspecification, poor overlap |
| Matching/stratification | compare similar propensity/covariate groups | hidden confounding, discarded population |
| IPW | reweight to a pseudo-population | extreme weights, positivity violations |
| Doubly robust/AIPW | combine treatment and outcome models | both wrong; nuisance overfit without cross-fitting |
| Difference-in-differences | treated/control would have parallel trends | anticipatory effects, differential trends |
| Regression discontinuity | assignment changes at a cutoff | manipulation, bandwidth/model sensitivity |
| Instrumental variables | instrument shifts treatment but has no other outcome path | weak instrument, exclusion failure |
| Synthetic control | weighted controls approximate counterfactual trajectory | donor contamination, poor pre-fit |

Always include falsification and sensitivity work appropriate to the design: pre-trends, placebo dates/outcomes/treatments, negative controls, balance/overlap plots, weight diagnostics, alternate specifications, leave-one-group-out, Rosenbaum/E-value-style sensitivity, or bounds. Robustness to many models does not rule out a shared wrong assumption.

## 10. Heterogeneous effects and uplift

Use CATE/uplift when the action changes by segment. Separate:

1. estimating whether heterogeneity exists;
2. discovering candidate segments/policies;
3. evaluating the policy on held-out or new experimental data;
4. enforcing budget, fairness, safety, and capacity constraints.

Prefer honest trees/forests, causal forests, meta-learners, or orthogonal learners only when sample size and overlap support them. Report uncertainty and policy value; avoid presenting unstable individual effects as facts.

## 11. Library map

| Tool | Best fit | Do not confuse it with |
|---|---|---|
| SciPy/statsmodels | tests, power, regression, robust/cluster covariance | an experimentation platform |
| DoWhy | graph-first model–identify–estimate–refute workflow | proof that assumptions are true |
| EconML | orthogonal ML and heterogeneous treatment effects | automatic confounder discovery |
| CausalML | uplift and treatment-effect estimators | a substitute for design/identification |
| PyMC/Stan | Bayesian models and decision uncertainty | automatic causal identification |
| experiment platform | assignment, exposure, metrics, guardrails, analysis | a guarantee of trustworthy instrumentation |

Pin versions and verify estimator assumptions, variance behavior, clustering, missingness, and supported treatments/outcomes against the exact library documentation.

## 12. Minimal dependency-free estimate

```python
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from statistics import NormalDist, mean, variance
from typing import Sequence


@dataclass(frozen=True)
class MeanDifference:
    control_mean: float
    treatment_mean: float
    absolute_effect: float
    standard_error: float
    lower: float
    upper: float


def difference_in_means(
    control: Sequence[float],
    treatment: Sequence[float],
    *,
    confidence: float = 0.95,
) -> MeanDifference:
    """Illustrative independent-unit normal interval, not a universal test."""
    if len(control) < 2 or len(treatment) < 2:
        raise ValueError("each arm needs at least two observations")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be between zero and one")

    control_mean = mean(control)
    treatment_mean = mean(treatment)
    effect = treatment_mean - control_mean
    se = sqrt(variance(control) / len(control) + variance(treatment) / len(treatment))
    z = NormalDist().inv_cdf(0.5 + confidence / 2.0)
    return MeanDifference(
        control_mean=control_mean,
        treatment_mean=treatment_mean,
        absolute_effect=effect,
        standard_error=se,
        lower=effect - z * se,
        upper=effect + z * se,
    )


estimate = difference_in_means([1, 2, 3, 4], [2, 3, 4, 5])
assert estimate.absolute_effect == 1.0
assert estimate.lower < estimate.absolute_effect < estimate.upper
```

Real analyses must match the randomization, repeated observations, clustering, metric type, missingness, multiplicity, and stopping design.

## 13. Rapid interview questions

**Why is randomization powerful?** It makes assignment independent of potential outcomes in expectation, so treatment groups provide a credible counterfactual subject to implementation, interference, attrition, and chance.

**What is the difference between statistical and practical significance?** Statistical significance measures incompatibility with a null under a model; practical significance asks whether the magnitude justifies value, cost, and risk.

**What does SRM mean?** Observed variant counts differ implausibly from configured allocation. It is a diagnostic for assignment, logging, eligibility, joining, or analysis problems.

**Why use ITT?** It preserves the randomization and estimates the effect of the assignment policy. Excluding non-compliers can reintroduce selection bias.

**Can you stop when p < 0.05?** Not under an ordinary fixed-horizon test. Use a predeclared sequential design if repeated looks are required.

**When does CUPED help?** When a stable pre-treatment covariate predicts the outcome. It reduces variance without changing the estimand when correctly specified.

**Why not control every available variable?** Controlling mediators changes the estimand; controlling colliders can introduce bias; irrelevant variables may increase variance or instability.

**What is positivity?** Each covariate pattern in the target population needs a non-zero probability of receiving each compared treatment. Poor overlap makes estimates extrapolative and unstable.

**How would you validate a DiD?** Examine domain plausibility, pre-trends/event-study patterns, anticipation, composition, concurrent shocks, treatment timing, clustering, and placebo tests.

**How do you evaluate uplift?** On held-out randomized data using policy value, Qini/uplift curves with uncertainty, treatment capacity, and guardrails—not only CATE fit.

## 14. Lead-level case

**Prompt:** A product team wants to deploy an AI-generated notification because a pilot showed higher clicks.

Structure the answer:

1. define the business decision and distinguish clicks from retained value;
2. specify eligibility, user-level assignment, treatment variants, and exposure logging;
3. choose a primary downstream outcome, click mechanism metric, unsubscribe/complaint/safety guardrails, and infrastructure metrics;
4. establish baseline, MDE, delayed outcome window, power, duration, ramp, and kill conditions;
5. verify content-policy and model-version invariants across variants;
6. perform SRM, assignment, exposure, logging, and contamination checks before effect analysis;
7. estimate ITT with user-level uncertainty and CUPED only from pre-period data;
8. inspect predeclared slices for accessibility, language, and vulnerable-user harm with multiplicity awareness;
9. separate novelty from steady-state response and check repeated-notification fatigue;
10. decide ship, iterate, or stop using the estimate interval, guardrails, operational risk, and expected value;
11. version the treatment/model/prompt and retain an audit-ready decision record.

## 15. Final checklist

- [ ] I can state treatment, control, population, unit, exposure, outcome window, and estimand.
- [ ] I can explain power, MDE, Type I/II error, and why non-significance is not equivalence.
- [ ] I can diagnose SRM, attrition, instrumentation, post-treatment filtering, and interference.
- [ ] I can distinguish fixed-horizon, sequential, multiple-testing, and bandit designs.
- [ ] I can derive difference-in-means and explain cluster-aware uncertainty.
- [ ] I can explain CUPED and why its covariate must be pre-treatment.
- [ ] I can distinguish confounder, mediator, collider, and instrument using a DAG.
- [ ] I can compare matching, IPW, doubly robust, DiD, RDD, IV, and synthetic control assumptions.
- [ ] I can defend heterogeneous-effect validation and policy evaluation.
- [ ] I can connect causal evidence to a concrete product decision, guardrails, rollout, and limitations.

## 16. Primary references

- Microsoft Experimentation Platform, [CUPED paper](https://exp-platform.com/Documents/2013-02-CUPED-ImprovingSensitivityOfControlledExperiments.pdf)
- Microsoft Research, [Diagnosing Sample Ratio Mismatch](https://www.microsoft.com/en-us/research/publication/diagnosing-sample-ratio-mismatch-in-online-controlled-experiments-a-taxonomy-and-rules-of-thumb-for-practitioners/)
- PyWhy, [DoWhy effect-estimation workflow](https://www.pywhy.org/dowhy/v0.13/user_guide/causal_tasks/estimating_causal_effects/effect_estimation_with_estimators.html)
- Microsoft Research, [EconML documentation](https://econml.azurewebsites.net/)
- Hernán and Robins, [Causal Inference: What If](https://www.hsph.harvard.edu/miguel-hernan/causal-inference-book/)
- Kohavi, Tang, and Xu, *Trustworthy Online Controlled Experiments*

Use these sources to verify assumptions and methods; do not memorize a company-specific threshold as a universal experiment policy.
