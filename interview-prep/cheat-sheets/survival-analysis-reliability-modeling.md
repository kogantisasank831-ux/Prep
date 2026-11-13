---
layout: "week"
status: "approved"
version: "1.0.0"
last_reviewed: "2026-11-11"
imported_on: "2026-11-13"
source_repository: "kogantisasank831-ux/transformer-explainer"
source_commit: "cdd45b6b0c08c5d88a626e4d16853abdf285f08d"
source_path: "AI_Data_Science_Interview_Cheat_Sheets/Batch_9_Specialized_Modeling/35_Survival_Analysis_Reliability_Modeling_Cheat_Sheet.md"
header_context: "Interview cheat sheets"
back_label: "Cheat sheets"
back_url: "/cheat-sheets/"
toc_heading: "Cheat-sheet sections"
pagination_label: "Cheat sheets hub"
pagination_url: "/cheat-sheets/"
title: "Survival analysis and reliability modeling interview cheat sheet"
description: "Interview revision for censored time-to-event data, survival models, competing risks, evaluation, maintenance decisions, and monitoring."
summary: "Revise time-to-event contracts, censoring, Kaplan–Meier, Cox and AFT models, competing risks, evaluation, reliability decisions, and production monitoring."
permalink: "/interview-prep/cheat-sheets/survival-analysis-reliability-modeling/"
kicker_primary: "Interview revision"
kicker_secondary: "Batch 9 · Survival analysis"
current_label: "Revision guide"
alternate_label: "Cheat sheets hub"
alternate_url: "/cheat-sheets/"
---

**Target roles:** Lead Data Scientist, Senior Data Scientist, Applied Scientist, ML Engineer, Reliability/Predictive-Maintenance Scientist<br>
**Use:** churn, credit/risk, healthcare, maintenance, warranty, customer lifetime, failure prediction, and modeling-case interviews<br>
**Interview rule:** define the time origin, event, censoring, competing events, prediction horizon, and intervention before fitting a model. Turning censored records into ordinary negatives changes the question and biases evaluation.

## 1. Thirty-second revision

- Survival analysis models time until an event while handling incomplete observation.
- Define time origin, event, time scale, follow-up end, censoring reason, delayed entry, repeated events, and competing risks.
- Survival function `S(t)=P(T>t)`; cumulative distribution `F(t)=1−S(t)`; density `f(t)`; hazard `h(t)=f(t)/S(t)`.
- Hazard is an instantaneous rate conditional on surviving to `t`; it is not the probability of failing at exactly `t`.
- Kaplan-Meier estimates the survival curve nonparametrically under independent/non-informative censoring assumptions.
- Nelson-Aalen estimates cumulative hazard.
- Cox proportional hazards models relative hazard without specifying the baseline hazard; proportional hazards is a central assumption.
- Accelerated failure time models act on survival time and can be more intuitive when a distributional assumption fits.
- Random survival forests and boosting/deep models capture nonlinearities but still need censoring-aware objectives and metrics.
- Concordance measures ranking, not absolute risk calibration. Use time-dependent AUC, Brier/Integrated Brier, calibration, and decision metrics.
- Evaluate with temporal/entity splits and censoring-aware estimators. Training-set censoring distribution may be needed for IPCW.
- Competing events prevent the event of interest; use cause-specific hazards and/or cumulative-incidence methods according to the question.
- Reliability decisions require action lead time, maintenance policy, downtime/spares capacity, cost, and post-intervention feedback—not model score alone.

## 2. Define the time-to-event contract

Write:

> For population/assets **P** entering at **origin O**, estimate the risk or distribution of **event E** over **horizon H**, using information available by **landmark T**, to support **action A**, while accounting for **censoring, competing events, interventions, and capacity C**.

Examples:

- time from signup to churn;
- time from loan origination to default;
- time from machine overhaul to bearing failure;
- time from treatment to relapse or death;
- time from product shipment to warranty claim.

Clarify:

- calendar time versus age/usage time;
- event definition and adjudication;
- whether event can recur;
- observation/follow-up end;
- right, left, or interval censoring;
- left truncation/delayed entry;
- competing events;
- time-varying covariates;
- intervention after a high-risk score;
- prediction form: risk by 30 days, survival curve, median time, or ranking.

## 3. Core notation and intuition

Let nonnegative event time be `T`.

- Survival: `S(t)=P(T>t)`
- CDF: `F(t)=P(T≤t)=1−S(t)`
- Density: `f(t)=dF(t)/dt` for continuous time
- Hazard: `h(t)=lim_(Δt→0) P(t≤T<t+Δt | T≥t)/Δt`
- Cumulative hazard: `H(t)=∫₀ᵗ h(u)du`
- Relationship: `S(t)=exp(−H(t))` under standard continuous-time conditions

Hazard can rise, fall, remain constant, or vary non-monotonically. A hazard ratio compares conditional rates, not directly probabilities or expected times.

### Observation representation

For each subject:

- observed time `Y=min(T,C)`;
- event indicator `δ=1(T≤C)`;
- censoring time `C`.

Treating every `δ=0` as “will never fail” is wrong; it only states no event was observed by `Y`.

## 4. Censoring, truncation, and recurrent events

### Censoring

- right-censored: event occurs after last observation or is never observed;
- left-censored: event occurred before observation threshold;
- interval-censored: event occurred between two inspections;
- administrative: study/data window ends;
- loss to follow-up: may be informative.

Standard methods often assume censoring is independent of event time conditional on modeled covariates. If high-risk customers disappear from observation, that assumption may fail.

### Left truncation/delayed entry

Subjects enter only after surviving to an entry time. The risk set must include them only after entry. Ignoring this creates survivorship bias.

### Recurrent events

Repeated failures, hospitalizations, or purchases need event-process methods, gap-time/calendar-time definitions, frailty/random effects, or carefully defined episodes. Ordinary single-event survival discards dependence and event count.

## 5. Kaplan-Meier and Nelson-Aalen

At ordered event time `t_j`:

- `n_j` subjects are at risk immediately before `t_j`;
- `d_j` events occur.

Kaplan-Meier:

`S_hat(t)=Π_(t_j≤t) (1−d_j/n_j)`

Censoring reduces later risk sets but does not create an event drop.

Uses:

- descriptive survival curves;
- median survival where curve crosses 0.5;
- group comparison;
- baseline/check for parametric or model behavior.

Caveats:

- curves are marginal, not covariate-adjusted;
- late estimates may be unstable with few at risk;
- log-rank comparisons emphasize particular alternatives and do not measure practical effect;
- crossing curves challenge one-number summaries;
- competing risks require cumulative-incidence methods for absolute cause-specific risk.

Nelson-Aalen:

`H_hat(t)=Σ_(t_j≤t) d_j/n_j`

It estimates cumulative hazard and connects to counting-process methods.

## 6. Minimal dependency-free example: Kaplan-Meier steps

```python
from __future__ import annotations

from collections import Counter
from collections.abc import Sequence


def kaplan_meier(
    durations: Sequence[float],
    events: Sequence[bool],
) -> list[tuple[float, float]]:
    """Return (event_time, survival) after each distinct event time."""
    if len(durations) != len(events) or not durations:
        raise ValueError("durations and events must have equal nonzero length")
    if any(duration < 0 for duration in durations):
        raise ValueError("durations must be nonnegative")

    event_counts = Counter(
        duration for duration, event in zip(durations, events, strict=True) if event
    )
    all_counts = Counter(durations)
    at_risk = len(durations)
    survival = 1.0
    steps: list[tuple[float, float]] = []

    for time in sorted(all_counts):
        event_count = event_counts[time]
        if event_count:
            survival *= 1.0 - event_count / at_risk
            steps.append((time, survival))
        at_risk -= all_counts[time]
    return steps


curve = kaplan_meier([1, 2, 2, 3], [True, True, False, True])
assert curve[0] == (1, 0.75)
assert curve[1] == (2, 0.5)
assert curve[2] == (3, 0.0)
```

This illustrates risk sets and tied event/censoring times. Production libraries provide confidence intervals, delayed entry, weights, and tested tie conventions.

## 7. Cox proportional hazards

The Cox model:

`h(t|x)=h₀(t) exp(βᵀx)`

It leaves baseline hazard `h₀(t)` unspecified and estimates coefficients through partial likelihood.

Interpretation: a one-unit increase in feature `x_k` multiplies hazard by `exp(β_k)`, holding modeled covariates fixed, under proportional hazards and model assumptions.

### Assumptions/checks

- proportional hazards: hazard ratios do not change with time;
- linear predictor is appropriately specified;
- relevant confounding/model variables are addressed for the intended claim;
- censoring assumptions;
- independent subjects or appropriately modeled clustering;
- no severe collinearity/unstable separation.

Diagnostics:

- Schoenfeld-residual-based proportionality checks;
- martingale/deviance residuals;
- log-minus-log plots as exploratory evidence;
- nonlinear terms/splines and interactions;
- influence and outliers;
- calibration by time and slice.

### Violations

- time-varying coefficients/interactions;
- stratified Cox for different baseline hazards;
- alternative time scale;
- accelerated failure time model;
- flexible parametric survival;
- landmark/dynamic models.

Do not automatically discard a feature after a significance test; align treatment with prediction purpose, uncertainty, and domain.

## 8. Accelerated failure time and parametric models

An AFT model commonly writes:

`log(T)=βᵀx+σε`

Covariates multiply the time scale: an acceleration factor above one stretches expected/quantile survival time under the model.

Common distributions:

- exponential: constant hazard;
- Weibull: monotonic hazard and can be expressed in PH/AFT forms under parameterization;
- log-normal/log-logistic: non-monotonic hazard possibilities;
- Gompertz and flexible spline models for particular domains.

Benefits:

- full survival distribution and extrapolation;
- interpretable time ratios;
- efficient when distribution is suitable.

Risks:

- wrong tail/hazard shape;
- extrapolation beyond observed follow-up;
- parameterization differences across libraries.

Compare distributional diagnostics and out-of-time calibration, not likelihood alone.

## 9. Time-varying covariates and dynamic prediction

Values such as usage, lab measures, load, and maintenance state change over time.

Use start-stop/interval format:

| entity | start | stop | features known during interval | event at stop |
|---|---:|---:|---|---:|

Critical rules:

- covariates must be known before the interval/event;
- update frequency must match deployment;
- avoid forward filling information recorded after the event;
- distinguish time-varying covariate from time-varying effect;
- account for repeated rows per entity.

Landmarking predicts from a chosen time among subjects event-free then. Joint models can connect longitudinal measurements and event risk when measurement process is informative.

## 10. Machine-learning survival models

| Model | Strength | Main caveat |
|---|---|---|
| penalized Cox | high-dimensional linear effects | proportional hazards/linearity |
| survival tree | nonlinear interactions and interpretability | instability |
| random survival forest | nonlinearities/interactions, survival functions | data/compute, calibration, extrapolation |
| survival boosting | flexible risk functions | tuning and objective semantics |
| neural Cox/DeepSurv-style | nonlinear relative risk | PH objective and calibration |
| discrete-time neural model | flexible hazards per interval | interval design and competing events |
| multi-task/time-to-event net | joint horizon outputs | consistency/calibration |

Complex models need a Kaplan-Meier/group and penalized Cox baseline. Ensure the implementation produces the prediction type required by the metric: risk score, survival function, cumulative hazard, or cumulative incidence.

Feature importance in survival models must specify outcome time and method. Permutation can be time-metric-specific; hazard ratios are not causal effects without stronger design.

## 11. Evaluation with censoring

### Concordance

Concordance measures whether higher predicted risk correctly orders comparable event times. Harrell's C can be biased under heavy censoring; IPCW/Uno-style alternatives address aspects under assumptions.

Limitations:

- ranking only;
- insensitive to absolute risk calibration;
- comparable-pair definition matters;
- can hide time/slice differences.

### Time-dependent AUC

At time `t`, define cases/controls according to event status and risk set, using censoring-aware estimation. Evaluate across decision-relevant times, not a single cherry-picked horizon.

### Brier score

At time `t`, the Brier score measures squared error between predicted survival/event status and observed outcome with censoring adjustment. Integrated Brier score summarizes over a time range.

### Calibration

Compare predicted risk by horizon with observed censoring-aware incidence:

- calibration-in-the-large;
- calibration slope;
- grouped curves with counts/intervals;
- flexible calibration plot;
- slices and future periods.

### Decision metrics

- recall/precision among failures within lead-time window;
- maintenance interventions per avoided failure;
- net benefit/decision curve;
- downtime, warranty cost, or retained customers;
- alarm lead time and capacity.

Metric estimators can require the training censoring distribution and time support. Do not evaluate beyond reliable follow-up.

## 12. Splits, leakage, and validation

### Split design

- temporal split for future deployment;
- group by entity/site/patient/family;
- maintain origin and follow-up logic;
- ensure enough follow-up to label horizon-specific outcomes;
- handle delayed entry and competing events consistently;
- nested tuning before untouched test.

Leakage examples:

- features recorded after event or censoring;
- maintenance/review triggered by the risk signal;
- full-lifetime aggregates at baseline;
- multiple episodes from one entity across folds;
- censoring date reveals calendar cohort;
- imputing with future values;
- defining negative as “no event yet” without adequate horizon.

### Validation plan

1. data timeline audit;
2. descriptive KM/cumulative incidence;
3. simple model;
4. assumption and residual checks;
5. future/entity holdout;
6. discrimination, calibration, and decision utility;
7. important slices and uncertainty;
8. sensitivity to censoring/competing-risk definitions;
9. external/site validation where claimed.

## 13. Competing risks

A competing event prevents the event of interest—for example, death from another cause before relapse or asset retirement before failure.

Quantities:

- cause-specific hazard: instantaneous rate of a cause among those currently event-free;
- cumulative incidence function (CIF): absolute probability of a particular cause by time while accounting for competitors;
- subdistribution hazard: modeling device linked to CIF in Fine-Gray methods.

Choose by question:

- etiologic/rate association and process modeling: cause-specific hazard often useful;
- absolute incidence prediction/decision: CIF is central;
- multiple-cause prediction: evaluate each cause and sum consistency.

Treating competing events as ordinary independent censoring and using `1−KM` can overestimate absolute event probability. Report the estimand clearly.

## 14. Reliability engineering connection

### Reliability quantities

- reliability `R(t)=P(T>t)`, equivalent to survival;
- failure distribution `F(t)`;
- hazard/failure rate;
- mean time to failure (MTTF) for non-repairable units;
- mean time between failures (MTBF) for repairable systems, with careful renewal assumptions;
- mean time to repair (MTTR);
- availability roughly depends on uptime and repair, but definitions vary.

### System reliability

Under independence:

- series system reliability: all components must work, so multiply component reliabilities;
- parallel redundancy: system works if at least one works, so use complement of all failing.

Dependencies, common-cause failures, load sharing, repair, and standby invalidate simple multiplication.

### Maintenance decisions

- preventive interval;
- condition-based maintenance;
- remaining useful life distribution;
- spares/workforce scheduling;
- inspection cadence;
- warranty and replacement policy.

Model actions change future failure/censoring. Use causal/experimental designs where claiming maintenance impact, and track policy feedback.

## 15. Production lifecycle

Artifact identity:

- cohort/time origin/event/censoring/competing-risk definitions;
- feature and landmark timestamps;
- data and code versions;
- model/runtime and parameters;
- baseline hazard/calibrator;
- prediction horizons and supported time range;
- threshold/policy and capacity;
- evaluation bundle.

Serving contract should return:

- risk score and/or survival probabilities at named horizons;
- supported horizon/version;
- input timestamp/freshness;
- uncertainty/coverage where validated;
- abstention/reason code;
- model and feature versions.

Monitor:

- origin/event/censor counts and delays;
- follow-up length and censoring distribution;
- feature and score drift;
- predicted risk/survival curve validity;
- calibration and discrimination when outcomes mature;
- alert/intervention volume and lead time;
- failure/downtime/churn outcomes;
- slice disparities;
- policy-induced missing outcomes.

## 16. Library map

| Tool | Best fit | Verify |
|---|---|---|
| lifelines | classical survival analysis and diagnostics in Python | parameterization, ties, time-varying format |
| scikit-survival | sklearn-style Cox/RSF and censoring-aware metrics | structured outcome format and time support |
| statsmodels | proportional hazards and statistical models | exact API/assumptions |
| pycox | neural survival methods | objective, discretization, calibration, maintenance |
| survival (R) | mature Cox/counting-process workflows | formula, ties, clustering and version |
| cmprsk/riskRegression ecosystems | competing-risk analysis | estimand and prediction/evaluation contract |

The library does not choose the time origin or censoring assumptions for you.

## 17. Rapid interview questions

**Why not ordinary binary classification?**<br>
It discards time and mishandles people/assets whose event has not yet been observed; fixed-horizon classification can work only with adequate follow-up and correct censoring treatment.

**What is right censoring?**<br>
The event time is known only to exceed the last observed time.

**Hazard versus probability?**<br>
Hazard is an instantaneous conditional rate among survivors; cumulative incidence/risk is a probability over an interval.

**What does Kaplan-Meier assume?**<br>
Among key conditions, censoring is independent/non-informative relative to event time for the target population, possibly conditional on design.

**What does a Cox hazard ratio of two mean?**<br>
The modeled instantaneous hazard is doubled for a one-unit contrast, conditional on covariates, if proportional hazards and other assumptions hold.

**What if proportional hazards fails?**<br>
Use time-varying effects, stratification, alternative time scale, AFT/flexible model, or horizon-specific prediction according to the goal.

**Why is C-index insufficient?**<br>
It measures ordering, not absolute probability calibration, horizon utility, or operational benefit.

**What is competing risk?**<br>
An event that prevents the event of interest and changes its absolute incidence.

**Can RSF ignore censoring?**<br>
No. Survival forests use censoring-aware splitting/estimation; ordinary random forest targets are not equivalent.

**How do you validate maintenance benefit?**<br>
Prediction accuracy is not causal impact. Use staged/experimental or credible quasi-experimental policy evaluation with safety constraints.

## 18. Lead-level case: refinery equipment failure

Structure the response:

1. Define component, failure mode, repair/overhaul origin, usage-time scale, required lead time, and action.
2. Join sensor, operating regime, maintenance, inspection, configuration, environment, and failure/adjudication timelines point-in-time.
3. Distinguish retirement/replacement and other failure modes as censoring or competing events according to the estimand.
4. Split by future time and hold out assets/sites to test transfer; prevent episode/entity leakage.
5. Establish engineering-limit, KM by regime, and Cox/AFT baselines before RSF/deep models.
6. Evaluate time-dependent discrimination, Brier/calibration, event recall at maintenance capacity, false work orders, and lead time.
7. Check proportional hazards or distribution assumptions, censoring sensitivity, rare regimes, and site/asset-age slices.
8. Integrate risk with spares, workforce, production loss, and safety constraints; allow abstention for unsupported regimes.
9. Shadow, then stage recommendations; keep hard safety protection independent and log operator overrides.
10. Monitor censoring/failure maturity, score calibration, interventions and outcomes; use causal evaluation before claiming downtime reduction.

## 19. Final checklist

- [ ] I define origin, event, time scale, horizon, censoring, truncation, recurrence, and competitors.
- [ ] I can explain `S(t)`, `h(t)`, `H(t)`, KM, and Nelson-Aalen.
- [ ] I interpret Cox hazard ratios and test proportional-hazards evidence.
- [ ] I distinguish Cox, AFT/parametric, forest/boosting, and neural methods.
- [ ] I handle time-varying covariates with point-in-time intervals.
- [ ] I evaluate concordance, time-dependent AUC, Brier, calibration, and decision utility.
- [ ] I use temporal/entity splits and censoring-aware estimators.
- [ ] I distinguish cause-specific hazard, CIF, and subdistribution hazard.
- [ ] I connect reliability prediction to maintenance capacity, lead time, safety, and feedback.
- [ ] I version definitions/artifacts and monitor outcomes after they mature.

## 20. Primary references

- [scikit-survival user guide](https://scikit-survival.readthedocs.io/en/stable/user_guide/)
- [scikit-survival model-evaluation guide](https://scikit-survival.readthedocs.io/en/stable/user_guide/evaluating-survival-models.html)
- [scikit-survival metrics API](https://scikit-survival.readthedocs.io/en/stable/api/metrics.html)
- [lifelines documentation](https://lifelines.readthedocs.io/en/latest/)
- [R survival package documentation](https://cran.r-project.org/package=survival)
- [Cox, Regression Models and Life-Tables](https://doi.org/10.1111/j.2517-6161.1972.tb00899.x)
- [Kaplan and Meier, Nonparametric Estimation from Incomplete Observations](https://doi.org/10.1080/01621459.1958.10501452)
- [Ishwaran et al., Random Survival Forests](https://doi.org/10.1214/08-AOAS169)
- [Fine and Gray, A Proportional Hazards Model for the Subdistribution of a Competing Risk](https://doi.org/10.1080/01621459.1999.10474144)
- [Pölsterl, scikit-survival](https://jmlr.org/papers/v21/20-729.html)
