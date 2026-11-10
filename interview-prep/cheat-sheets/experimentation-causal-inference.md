---
layout: "week"
status: "review"
version: "0.1.0"
last_reviewed: "2026-11-10"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "Experimentation and causal inference interview cheat sheet"
description: "Estimands, randomization, power, A/A and SRM, metrics, CUPED, sequential decisions, switchbacks, DAGs, propensity methods, DiD, RDD, IV, and uplift."
summary: "Revise trustworthy experiments and observational causal designs from decision contract through assumptions, execution, inference, guardrails, and launch evidence."
permalink: "/interview-prep/cheat-sheets/experimentation-causal-inference/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 7 · Experimentation and causality"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 7 source:** This review candidate integrates the newly prepared revision source into the Prep site. It is separate from the Week 1–20 learning assessments.

**Target roles:** Data Scientist, Applied Scientist, ML Engineer, AI/Data Science Lead, Product Data Scientist  
**Use:** A/B testing, metric design, causal inference, product experimentation, and decision-science rounds  
**Interview rule:** begin with the decision and causal estimand, then justify assignment, exposure, analysis, and assumptions. A small p-value is not a product decision.

## 1. Thirty-second revision

- Define the decision, population, treatment, comparator, outcome, time window, estimand, and guardrails before choosing a statistical test.
- Randomization balances observed and unobserved causes in expectation; execution failures can destroy that advantage.
- Choose the randomization unit to match interference, product delivery, and analysis. Analyze uncertainty at the assignment unit.
- Power depends on baseline variance/rate, minimum detectable effect, significance level, power, allocation, clustering, and eligible traffic.
- Intention-to-treat compares assignment groups and preserves randomization. Treatment-on-the-treated needs stronger assumptions when exposure differs from assignment.
- A/A tests and sample-ratio-mismatch checks find instrumentation, assignment, logging, and analysis problems before effect interpretation.
- Report effect size and confidence interval; do not equate “not significant” with “no effect” or significance with practical value.
- Repeated peeking, many metrics, and many variants inflate false positives unless the design and inference account for them.
- CUPED and pre-period covariates can reduce variance when chosen before outcome inspection and measured consistently.
- Causal diagrams clarify confounders, mediators, colliders, and adjustment choices. Do not control for every available variable.
- Observational methods exchange randomization for assumptions: overlap, parallel trends, exclusion restriction, continuity, or no unmeasured confounding.
- Validate novelty, carryover, network effects, heterogeneous impacts, long-term outcomes, and operational guardrails before scaling.

## 2. Decision and estimand contract

Record:

| Field | Question |
|---|---|
| Decision | launch, stop, iterate, target, or learn? |
| Population | which eligible users, accounts, regions, devices, or events? |
| Treatment | what exact experience or policy changes? |
| Comparator | current product, placebo, alternate model, or no action? |
| Outcome | primary metric with unit, direction, and observation window |
| Guardrails | safety, quality, fairness, latency, cost, complaints, retention |
| Estimand | ITT, ATE, ATT, per-protocol, uplift, long-term effect? |
| Horizon | exposure, maturation, novelty, seasonality, and follow-up |
| Decision rule | required value, risk tolerance, and owner |

The **estimand** is the precise causal quantity to estimate. For potential outcomes $Y_i(1)$ and $Y_i(0)$, average treatment effect is:

$$
ATE=\mathbb{E}[Y(1)-Y(0)]
$$

Only one potential outcome is observed per unit. Experimental design or causal assumptions bridge that missing counterfactual.

## 3. Randomization unit, interference, and clustering

Common units include user, session, account, household, store, geography, or time block. Choose the smallest unit that avoids unacceptable contamination and matches delivery.

If one user's treatment affects another user's outcome, the Stable Unit Treatment Value Assumption is violated. Examples include marketplaces, social graphs, shared sales teams, inventory, and recommendation feedback.

Cluster randomization can reduce contamination but lowers effective sample size because outcomes within clusters correlate. Approximate design effect for equal cluster size $m$ and intracluster correlation $\rho$:

$$
DE=1+(m-1)\rho
$$

Analyze with cluster-robust or design-consistent methods. Millions of events do not create millions of independent experimental units.

## 4. Power, MDE, and sample size

Power is the probability of rejecting the null under a specified true effect. The minimum detectable effect (MDE) should come from the smallest effect worth acting on, not from the sample the team happens to have.

For a simple balanced comparison of means, required sample per arm scales approximately as:

$$
n\propto\frac{\sigma^2(z_{1-\alpha/2}+z_{1-\beta})^2}{\delta^2}
$$

where $\sigma$ is outcome standard deviation, $\delta$ the MDE, $\alpha$ type-I error, and $1-\beta$ power.

Smaller MDE, noisier outcome, lower alpha, higher power, uneven allocation, clustering, noncompliance, and multiple comparisons require more traffic. Convert sample size to calendar time using eligible units and maturation delay; include weekly cycles and operational constraints.

## 5. Assignment, eligibility, exposure, and analysis sets

- **Eligibility:** who could enter the experiment.
- **Assignment:** randomized treatment allocation.
- **Exposure:** whether the assigned experience was actually delivered or seen.
- **Outcome:** measurement after a defined treatment opportunity.

Intention-to-treat (ITT) compares all assigned units, preserving randomization and estimating the effect of the assignment policy. Per-protocol or exposed-only analyses can introduce selection bias because exposure may depend on user behavior or system health.

Log assignment once with immutable experiment, variant, unit, timestamp, and version. Keep assignment stable for the required horizon. Distinguish failure to render from genuine non-engagement.

## 6. A/A tests, SRM, and instrumentation

An A/A test sends equivalent experiences through the full assignment and measurement path. It can reveal false-positive inflation, unstable metrics, timestamp issues, inconsistent eligibility, duplicate units, or correlated analysis mistakes.

Sample ratio mismatch (SRM) tests whether observed allocation differs materially from the planned ratio. Investigate before estimating treatment effects. Causes include:

- hashing or bucketing defects;
- variant-specific crashes or redirects;
- logging loss;
- eligibility evaluated after assignment;
- bot/internal traffic filters applied asymmetrically;
- joins that drop one arm;
- overlapping experiments or stale configuration.

Do not “fix” SRM by reweighting until the mechanism is understood; the missingness may be outcome-related.

## 7. Metric design and metric trees

Use one primary metric tied to the decision, a small set of guardrails, and diagnostic metrics for mechanism understanding.

A metric definition needs numerator, denominator, unit, window, attribution, deduplication, eligibility, late-data rule, and owner. Prefer user-level or assignment-unit aggregates when the unit is randomized.

Metric trees connect business outcome to controllable drivers. For example:

$$
Revenue = Eligible\ users \times Conversion\ rate \times Average\ order\ value
$$

Ratios require care: average of user-level ratios, ratio of totals, and event-level averages answer different questions. Use the estimator aligned with the estimand.

## 8. Effect sizes, intervals, and tests

For treatment mean $\bar Y_T$ and control mean $\bar Y_C$:

$$
\hat\tau=\bar Y_T-\bar Y_C
$$

Also report relative lift only when the baseline is stable and nonzero. A confidence interval expresses uncertainty under the design and model assumptions. It is not the probability that the fixed true effect lies in that realized interval.

Choose tests from the outcome and design:

- difference in means or regression for continuous outcomes;
- proportion tests or regression for binary outcomes;
- count/time-to-event methods when appropriate;
- randomization inference for design-based testing;
- cluster-robust standard errors for clustered assignment;
- bootstrap only with resampling at the correct independent unit.

Large samples make tiny effects significant. Compare the interval with the minimum practical effect, guardrail limits, and implementation cost.

## 9. Variance reduction and CUPED

Pre-period covariates correlated with the outcome can reduce variance without changing treatment assignment. CUPED forms an adjusted outcome:

$$
Y_{adj}=Y-\theta(X-\mathbb{E}[X])
$$

where $X$ is a pre-treatment covariate and $\theta$ is chosen to reduce variance.

Requirements:

- covariate measured before treatment;
- consistent availability and definition across arms;
- no leakage from treatment;
- method declared before inspecting treatment outcomes;
- uncertainty computed for the adjusted estimator;
- handling for new users without history.

Regression adjustment and stratification can also improve precision. Variance reduction cannot rescue biased assignment or broken instrumentation.

## 10. Multiple testing, peeking, and sequential designs

Testing many metrics, variants, segments, or stopping times increases the chance of a false discovery. Options include:

- one predeclared primary outcome;
- family-wise control such as Holm when any false positive is costly;
- false-discovery-rate control for exploratory families;
- hierarchical or gatekeeping procedures;
- holdout confirmation for discovered segments;
- Bayesian or sequential designs with a predeclared stopping and decision rule;
- alpha-spending or always-valid methods designed for repeated looks.

Ordinary fixed-horizon p-values are not valid after repeatedly stopping when they cross a threshold. Operational safety monitoring can run continuously, but the primary efficacy analysis needs its planned inference.

## 11. Switchback, geo, and marketplace experiments

Use switchback designs when treatment operates at a shared system level, such as dispatch, ranking, pricing, or capacity. Alternate treatment and control over randomized time blocks, accounting for:

- carryover and washout;
- time-of-day/day-of-week seasonality;
- autocorrelation;
- block length;
- shared shocks;
- interference across regions or inventory pools.

Geo experiments aggregate treatment by region and often require matched or synthetic controls, enough independent geographies, stable tracking, and sensitivity to spillover.

Marketplace experiments should define whether the estimand is buyer, seller, transaction, or ecosystem welfare. Treating one side can change supply, competition, and equilibrium for both arms.

## 12. Novelty, duration, and long-term effects

Early lift can reflect novelty, learning, or temporary operational attention. Short experiments may miss retention, fatigue, delayed conversion, model-feedback loops, or cost accumulation.

Set duration from:

- required independent units and power;
- full business cycles;
- outcome maturation;
- novelty/carryover risk;
- ramp safety and seasonality;
- capacity and support constraints.

Use long-term holdouts, repeated measurement, or surrogate validation when immediate metrics do not capture durable value. Do not extend a losing unsafe experiment merely to hit a sample-size target.

## 13. Causal diagrams: confounders, mediators, and colliders

A directed acyclic graph (DAG) makes assumed causal relationships explicit.

- **Confounder:** causes both treatment and outcome; often needs adjustment.
- **Mediator:** lies on the treatment-to-outcome path; adjusting for it changes the estimand toward a direct effect.
- **Collider:** is caused by two variables; conditioning on it can create a spurious association.
- **Instrument:** affects treatment and affects outcome only through treatment under strong assumptions.

Example: if user motivation affects both feature adoption and purchase, it confounds an observational adoption analysis. If adoption affects engagement which affects purchase, engagement is a mediator. Filtering only users who completed a workflow can create collider bias.

Do not let feature availability decide the adjustment set. Let the causal question and graph do it.

## 14. Identification assumptions

Observational estimation often needs:

1. **Consistency:** observed outcome under received treatment equals the corresponding potential outcome.
2. **Exchangeability/no unmeasured confounding:** after adjustment, treatment is as-if random.
3. **Positivity/overlap:** each relevant covariate profile has nonzero chance of each treatment.
4. **Correct temporal order:** covariates precede treatment and outcome.
5. **No unacceptable interference:** one unit's treatment does not alter another's outcome, or the interference is modeled.

These are domain claims, not facts proven by a library. Use negative controls, placebo tests, balance/overlap checks, sensitivity analysis, triangulation, and explicit limitations.

## 15. Propensity scores, matching, and weighting

The propensity score is $e(x)=P(T=1\mid X=x)$. Matching, stratification, and inverse-probability weighting use it to balance observed covariates.

For ATE weighting:

$$
w_i=\frac{T_i}{e(X_i)}+\frac{1-T_i}{1-e(X_i)}
$$

Workflow:

1. define pre-treatment covariates from a causal model;
2. estimate treatment propensity without outcome leakage;
3. inspect overlap and extreme weights;
4. trim or redefine the population when positivity fails;
5. check standardized balance after adjustment;
6. estimate effects with appropriate uncertainty;
7. run sensitivity and alternate-specification checks.

High propensity-model accuracy is not the goal; covariate balance and credible identification are.

## 16. Difference-in-differences

Difference-in-differences (DiD) compares outcome changes in treated and comparison groups:

$$
\hat\tau_{DiD}=(\bar Y_{T,post}-\bar Y_{T,pre})-(\bar Y_{C,post}-\bar Y_{C,pre})
$$

The central assumption is parallel untreated trends, not equal levels. Inspect multiple pre-periods, anticipation, composition changes, concurrent shocks, and spillovers. With staggered adoption and heterogeneous effects, naive two-way fixed-effects estimators can be misleading; use methods appropriate to treatment timing.

Event studies help visualize dynamics but pre-trend non-significance is not proof of parallel trends.

## 17. Regression discontinuity

Regression discontinuity design (RDD) uses a treatment rule with a threshold on a running variable. Near the cutoff, units just above and below may be comparable.

Validate:

- exact or fuzzy treatment assignment at the threshold;
- no precise manipulation of the running variable;
- continuity of potential outcomes and covariates;
- bandwidth and functional-form sensitivity;
- enough data near the cutoff;
- local estimand and limited external validity.

Plot raw binned outcomes and density near the threshold. High-order polynomials are not a substitute for robust local analysis.

## 18. Instrumental variables

An instrument $Z$ changes treatment $T$ but should affect outcome $Y$ only through treatment. Core assumptions include relevance, independence, exclusion restriction, and usually monotonicity for a local average treatment effect.

A weak instrument produces unstable, biased estimates. The exclusion restriction is a substantive claim and is often the hardest to defend. Report the complier population represented by the local effect rather than generalizing to everyone.

Examples such as randomized encouragement can be credible when encouragement changes uptake without directly changing the outcome.

## 19. Heterogeneous effects and uplift

Average effects can hide important variation. Estimate conditional average treatment effects only with adequate sample size, overlap, and honest validation.

Pre-specify a small number of decision-relevant segments or use causal forests/meta-learners with sample splitting and out-of-sample evaluation. Validate policies using incremental outcome, uplift/Qini curves, value under treatment capacity, and guardrails—not ordinary response-model AUC alone.

Segment mining after seeing results invites false discoveries. Confirm exploratory heterogeneity in a new experiment or holdout.

## 20. Experiment analysis skeleton

```python
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def difference_in_means(
    treatment: NDArray[np.float64], control: NDArray[np.float64]
) -> tuple[float, float]:
    if treatment.size < 2 or control.size < 2:
        raise ValueError("each arm needs at least two independent units")
    effect = float(treatment.mean() - control.mean())
    standard_error = float(
        np.sqrt(treatment.var(ddof=1) / treatment.size + control.var(ddof=1) / control.size)
    )
    return effect, standard_error
```

This skeleton assumes independent units and a simple design. Clustered assignment, ratio metrics, triggered analysis, missing outcomes, repeated measures, and sequential decisions need design-consistent estimators.

## 21. Common interview failure modes

- choosing a t-test before defining the estimand;
- randomizing sessions while treatment persists at user level;
- treating events as independent when users were randomized;
- removing non-exposed users from the primary analysis;
- continuing despite unexplained SRM;
- calling a non-significant result “no effect”;
- peeking until significance without sequential correction;
- optimizing many metrics and reporting only the winner;
- controlling for a mediator or collider without changing the estimand explicitly;
- claiming propensity methods remove unmeasured confounding;
- using pre-trend tests as proof of DiD validity;
- presenting a local RDD or IV effect as a population-wide ATE.

## 22. Rapid interview Q&A

**Why use ITT?**  
It preserves randomization and estimates the effect of assigning the policy, including delivery and uptake realities.

**What does SRM mean?**  
Observed allocation is inconsistent with the planned ratio beyond expected chance; investigate assignment and data before effects.

**Can CUPED create bias?**  
Yes, if the covariate is affected by treatment, inconsistently measured, or selected after inspecting outcomes.

**Why not adjust for every feature?**  
Post-treatment variables, colliders, poor overlap, and model instability can bias or weaken the estimate.

**When is a switchback useful?**  
When treatment acts on a shared system and simultaneous unit-level randomization would contaminate outcomes.

## 23. Lead-level case

**Case:** an agent-assisted support workflow reports a 7% resolution lift, but only exposed sessions were analyzed and treatment had more logging loss.

A strong answer should:

1. stop the launch decision and reconstruct eligibility, immutable assignment, exposure, outcomes, and logging completeness by arm;
2. test SRM and differential missingness at the randomized unit;
3. restore ITT as the primary estimand and treat exposed-only results as selected diagnostics;
4. define resolution window, repeat contacts, escalation, hallucination/safety, latency, and cost guardrails;
5. repair instrumentation, run an A/A or shadow validation, and repeat with a predeclared analysis;
6. separate product effect from delivery reliability and record the decision threshold and owner.

## 24. Final checklist

- Can you define treatment, comparator, unit, population, outcome, horizon, and estimand?
- Can you explain power, MDE, design effect, and calendar duration?
- Can you distinguish assignment, exposure, ITT, and treatment-on-treated?
- Can you diagnose SRM and explain A/A tests?
- Can you handle multiple testing, peeking, and variance reduction?
- Can you choose user, cluster, switchback, or geo randomization?
- Can you identify confounders, mediators, and colliders in a DAG?
- Can you state the assumptions behind propensity methods, DiD, RDD, and IV?
- Can you validate heterogeneous effects without segment fishing?
- Can you translate statistical uncertainty into a launch decision with guardrails?

## Primary references

- Kohavi, Tang, and Xu, *Trustworthy Online Controlled Experiments*.
- Imbens and Rubin, *Causal Inference for Statistics, Social, and Biomedical Sciences*.
- Hernán and Robins, *Causal Inference: What If*.
- Pearl, Glymour, and Jewell, *Causal Inference in Statistics: A Primer*.
- Original or official documentation for CUPED, cluster-robust analysis, and the chosen sequential-testing procedure.
