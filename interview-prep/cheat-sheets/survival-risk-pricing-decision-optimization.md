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
title: "Survival, risk, pricing, and decision optimization interview cheat sheet"
description: "Censoring and survival models, risk and CLV, causal pricing, LP/MILP/constraint programming, solver evidence, uncertainty, predict-then-optimize evaluation, and decision services."
summary: "Revise specialized decision modeling from time-to-event and causal response through calibrated value, explicit constraints, solver reliability, and downstream regret."
permalink: "/interview-prep/cheat-sheets/survival-risk-pricing-decision-optimization/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 9 · Survival, risk, pricing, and optimization"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 9 scope:** This review candidate derives from the approved master index and the cited primary documentation. It is separate from the Week 1–20 learning assessments.

**Target roles:** Senior/Lead Data Scientist, Applied Scientist, Decision Scientist, ML Engineer, Operations Research Scientist, AI/Data Science Lead  
**Use:** time-to-event modeling, risk scoring, churn and lifetime value, pricing, allocation, scheduling, optimization, and decision-system interviews  
**Interview rule:** distinguish prediction from decision. Define the event or objective, time origin, action, constraints, counterfactual response, uncertainty, and cost before selecting a survival model, risk score, elasticity model, or solver.

## 1. Thirty-second revision

- Survival analysis models time to an event while handling censoring; ordinary binary labels discard timing and can misclassify censored cases.
- Define time origin, event, censoring, competing events, delayed entry, horizon, and action before modeling.
- Kaplan–Meier estimates a marginal survival curve; Cox models covariate effects through proportional hazards; flexible models relax assumptions but still need censoring-aware evaluation.
- C-index measures ranking, not probability calibration. Add time-dependent AUC, Brier/calibration evidence, and decision utility at relevant horizons.
- A risk score must be calibrated and thresholded for a specific action, capacity, and cost. Ranking performance alone is insufficient.
- Selective labels, interventions, reject inference, policy changes, and delayed outcomes can make historical risk data misleading.
- Pricing needs a causal demand response, not only prediction of purchases at observed prices. Price is a treatment chosen by a prior policy.
- CLV needs horizon, retention/survival, margin, cost, discounting, uncertainty, and cohort assumptions.
- Optimization requires decision variables, objective, constraints, units, and feasibility. Linear programs allow continuous decisions; mixed-integer programs encode discrete choices; constraint programming excels at logical/scheduling structure.
- Solver status, bounds/gap, time limit, tolerances, and fallback are part of the output contract.
- Predict-then-optimize systems must test downstream decision regret and sensitivity, not only upstream prediction error.
- Constraints encode policy and safety; do not let an optimizer invent business rules or treat infeasibility as an empty answer.

## 2. Choose the correct decision formulation

Ask:

- Is the target an event by a fixed horizon, time until event, repeated events, count, amount, or causal response to an action?
- Are some outcomes unobserved because follow-up ended, the entity left the dataset, or another event occurred?
- Does the decision change the future label?
- Is the output a probability, ranking, price, treatment, resource allocation, schedule, or route?
- What constraints, capacities, service levels, budgets, and fairness/safety policies apply?
- What is the fallback if data is missing, uncertainty is high, or no feasible solution is found?

Model the final decision metric. A strong AUC does not prove lower losses, better retention, profitable pricing, or a feasible schedule.

## 3. Survival-analysis contract

For each observation define:

- **time origin:** when the clock starts;
- **event:** exact outcome and first/recurrent-event policy;
- **duration:** time from origin to event or censoring;
- **event indicator:** observed event versus censored;
- **censoring:** right, left, or interval; administrative versus informative;
- **delayed entry/left truncation:** unit becomes observable after risk began;
- **competing risks:** another event prevents or changes the event of interest;
- **covariate time:** baseline or time-varying, with point-in-time availability;
- **prediction horizon and action.**

Right censoring does not mean the event never occurs. Treating censored cases as negatives biases the target, especially for recent cohorts.

## 4. Survival and hazard functions

For event time $T$:

$$
S(t)=P(T>t)
$$

The hazard is an instantaneous event rate conditional on survival so far:

$$
h(t)=\lim_{\Delta t\to0}\frac{P(t\le T<t+\Delta t\mid T\ge t)}{\Delta t}
$$

The cumulative hazard is $H(t)=\int_0^t h(u)du$ and, under standard conditions, $S(t)=e^{-H(t)}$.

Probability, density, and hazard are different. A hazard ratio is not a risk ratio or difference in expected survival time.

## 5. Kaplan–Meier and comparisons

The Kaplan–Meier estimator multiplies conditional survival estimates at event times:

$$
\hat S(t)=\prod_{t_i\le t}\left(1-\frac{d_i}{n_i}\right)
$$

where $d_i$ events occur among $n_i$ at risk at $t_i$.

Use it for descriptive survival curves and a non-feature baseline. Show number at risk and confidence intervals; late tails can be unstable. The log-rank test compares entire survival curves under assumptions and does not quantify a clinically/business-relevant effect by itself.

If censoring differs by group or depends on unobserved risk, ordinary comparisons may be biased. Competing events need cumulative-incidence methods rather than treating every competing event as ordinary independent censoring.

## 6. Cox proportional hazards and alternatives

Cox models:

$$
h(t\mid x)=h_0(t)\exp(\beta^\top x)
$$

It leaves baseline hazard $h_0(t)$ unspecified and assumes covariate hazard ratios are proportional over time unless extensions are used.

Check:

- proportional-hazards assumption and time interactions;
- functional form/nonlinearity;
- influential observations and correlated covariates;
- time-varying covariate construction;
- train/test temporal and group split;
- calibration at decision horizons.

Alternatives include parametric accelerated-failure-time models, survival trees/forests, gradient boosting, discrete-time hazard models, and neural survival models. Choose from assumptions, sample/event count, nonlinearity, competing events, calibration, interpretability, compute, and deployment—not leaderboard C-index alone.

## 7. Survival evaluation

- **C-index:** ranks comparable pairs; can be optimistic with heavy censoring and says little about absolute probabilities.
- **Time-dependent AUC:** discrimination by a chosen horizon under a censoring estimator.
- **Brier score:** squared probability error adjusted for censoring; reflects discrimination and calibration.
- **Integrated Brier score:** aggregates Brier score over a defined time interval.
- **Calibration:** predicted versus observed event-free probability at relevant times.
- **Decision utility:** action cost/benefit, capacity, lead time, and intervention outcome.

Use censoring information from training appropriately, restrict evaluation to supported follow-up, report event/censor counts and horizon support, and compare Kaplan–Meier/simple baselines. Evaluate cohorts, sites, segments, censoring patterns, and time drift.

## 8. Risk scoring and operational thresholds

A risk system has at least four layers:

1. eligibility and feature construction;
2. probability/risk model;
3. calibration and policy threshold/risk band;
4. action, review, limit, or intervention.

Evaluate each layer. Define the event window, exposure/amount, class imbalance, loss severity, capacity, and asymmetric cost. Metrics can include PR-AUC, log loss/Brier, calibration, recall at review capacity, expected loss captured, stability, subgroup evidence, and realized outcome.

Common traps:

- labels exist only for approved/reviewed cases;
- intervention prevents the event, creating selective labels;
- defaults/fraud are delayed or revised;
- macros, economic regimes, or policy change prevalence and calibration;
- proxies create unfair or prohibited effects;
- a high rank score is treated as a probability.

Keep model score separate from policy. Version both and log the decision context.

## 9. Churn and customer lifetime value

Churn can be contractual (explicit cancellation) or non-contractual (inactivity definition). Define the observation window, inactivity threshold, return/reactivation, censoring, interventions, and horizon.

A simple discounted expected CLV form is:

$$
CLV=\sum_{t=1}^{H}\frac{P(\text{active at }t)\,\mathbb{E}[\text{margin}_t\mid active]-\mathbb{E}[\text{service cost}_t]}{(1+r)^t}
$$

State horizon $H$, discount rate $r$, margin rather than revenue, acquisition/retention costs, return/refund behavior, uncertainty, and cohort/regime assumptions.

Predicting who will churn is not the same as deciding whom to contact. Uplift/causal evidence is needed to target people whose outcome changes because of the intervention, subject to cost and capacity.

## 10. Pricing and elasticity

Demand at observed prices reflects the old pricing policy, inventory, promotions, competition, seasonality, customer mix, and selection. A predictive purchase model can learn that policy rather than the response to a new price.

Point elasticity is:

$$
\epsilon=\frac{\partial Q}{\partial P}\frac{P}{Q}
$$

Pricing design should cover:

- objective: revenue, margin, contribution, utilization, retention, or long-term value;
- unit and timing of price/action;
- eligibility, floors/ceilings, contracts, fairness and legal/policy constraints;
- randomized price/promotion experiments or credible causal identification;
- heterogeneous response and support/overlap;
- competitor, inventory, cannibalization, substitution and network effects;
- uncertainty and safe exploration;
- guardrails, rollback and customer communication.

Never extrapolate far beyond historically supported prices without explicit risk control. Short-term conversion lift may harm trust or long-term value.

## 11. Optimization model anatomy

Define:

- decision variables $x$;
- objective $f(x)$;
- constraints $g_i(x)\le b_i$ and equalities;
- variable domains (continuous, integer, binary);
- units, time indices, scenarios, and data source;
- feasibility and business-rule owner;
- solve time, optimality requirement, and fallback.

A linear program is:

$$
\min_x c^\top x \quad \text{subject to}\quad Ax\le b,\; A_{eq}x=b_{eq},\; \ell\le x\le u
$$

LP variables are continuous. Mixed-integer linear programming adds integer/binary variables for on/off, assignment, setup, and logical choices. Constraint programming/CP-SAT is often effective for scheduling and rich discrete logic. Routing, network flow, matching, knapsack, and assignment have specialized structures and algorithms.

## 12. Solver evidence and sensitivity

Record:

- solver/version, model/data identity, parameters and random seed where relevant;
- status: optimal, feasible, infeasible, unbounded, time/iteration limit, numerical failure, or unknown;
- incumbent objective, best bound, relative/absolute gap;
- runtime, memory, node/iteration counts;
- constraint violations under explicit tolerances;
- sensitivity to data/forecast changes;
- fallback and human override.

For LPs, dual/shadow prices can describe local objective sensitivity to a constraint RHS under assumptions. They are not universal causal values and may change after basis/active-set or integer decisions change.

Diagnose infeasibility with constraint groups, relaxations, irreducible infeasible subsets when supported, and domain owners. Never silently drop a hard constraint to return a solution.

## 13. Predict-then-optimize systems

A common workflow predicts demand, risk, duration, or response, then optimizes an action. Errors matter through the downstream decision, not equally in all rows.

Evaluate:

- prediction metrics by decision-relevant slice;
- realized objective/utility and regret versus an oracle or accepted benchmark;
- feasibility and constraint violations;
- stability/turnover of decisions;
- sensitivity to uncertainty and scenario stress;
- calibration of probabilistic inputs;
- robust/stochastic alternatives versus deterministic point estimates;
- runtime, fallback, and policy compliance.

Avoid leakage between prediction and optimization evaluation. Reproduce what inputs were knowable at each decision origin. An optimizer can amplify small prediction errors near a constraint or discrete switch.

## 14. Robust, stochastic, and multi-objective decisions

- **Scenario/stochastic optimization:** optimize expected or risk-adjusted outcomes over possible futures with probabilities.
- **Robust optimization:** protect against a defined uncertainty set, often trading average performance for worst-case guarantees.
- **Chance constraints:** require a constraint to hold with specified probability under a model.
- **Multi-objective optimization:** expose trade-offs or combine objectives using owner-approved weights/constraints.

State how uncertainty sets/scenarios/probabilities were derived and validated. Worst-case protection is only as meaningful as the uncertainty set. A weighted sum can hide stakeholder trade-offs; show Pareto/frontier or sensitivity evidence when useful.

## 15. Production decision service

A reliable service:

1. validates model and optimization inputs, units, freshness, and scenario identity;
2. runs prediction/calibration under exact versions;
3. constructs a versioned optimization model;
4. applies authorized hard and soft constraints;
5. enforces time/resource limits and cancellation;
6. interprets solver status before accessing a solution;
7. verifies feasibility and post-solve business rules;
8. returns decision, confidence/scenario evidence, model/solver identity, and reason codes;
9. falls back safely when inputs or solve fail;
10. logs outcomes for delayed evaluation and rollback.

Protect against duplicate execution and stale replays when decisions create side effects. Separate generating a plan from authorizing or executing it.

## 16. Minimal discounted-value example

```python
from __future__ import annotations

from collections.abc import Sequence


def discounted_expected_margin(
    survival_probability: Sequence[float],
    margin_if_active: Sequence[float],
    service_cost: Sequence[float],
    discount_rate: float,
) -> float:
    if not (
        len(survival_probability)
        == len(margin_if_active)
        == len(service_cost)
    ):
        raise ValueError("All horizon sequences must have equal length")
    if discount_rate <= -1.0:
        raise ValueError("discount_rate must be greater than -1")
    total = 0.0
    for period, (survival, margin, cost) in enumerate(
        zip(
            survival_probability,
            margin_if_active,
            service_cost,
            strict=True,
        ),
        start=1,
    ):
        if not 0.0 <= survival <= 1.0:
            raise ValueError("Survival probabilities must be in [0, 1]")
        total += (survival * margin - cost) / ((1.0 + discount_rate) ** period)
    return total
```

This is an accounting function, not a complete CLV estimator. Production evidence must validate probability calibration, conditional margin/cost, dependence, interventions, cohort stability, horizon, and uncertainty.

## 17. Common failure modes

- Treating censored observations as negatives.
- Defining time origin after seeing future data.
- Reporting only C-index without horizon calibration or decision utility.
- Interpreting a hazard ratio as a probability or causal effect.
- Ignoring competing risks or delayed entry.
- Using a risk ranking as a calibrated probability.
- Training only on previously approved/reviewed cases without handling selective labels.
- Estimating price response from observational prices without policy/confounding analysis.
- Optimizing revenue while ignoring margin, inventory, substitution, fairness, or long-term effects.
- Building an optimizer before owners define hard versus soft constraints.
- Reading solution values after an infeasible/unbounded/unknown status.
- Claiming optimality when the solver stopped with a nonzero gap.
- Silently relaxing hard constraints or returning yesterday’s plan without freshness disclosure.
- Improving prediction RMSE while downstream decision regret worsens.

## 18. Rapid interview questions

**Why not binary classification for churn by 90 days?** It can work for a fixed matured horizon, but survival methods use timing and censored observations and can provide multiple-horizon risk.

**What does the C-index measure?** Ranking of comparable event times; it does not establish probability calibration or business utility.

**What is proportional hazards?** Covariate hazard ratios remain constant over time in the basic Cox model; test and adapt when violated.

**Why is price a treatment?** The price is chosen by a policy and changes demand; observed outcomes are confounded by where/when/to whom each price was offered.

**LP versus MILP?** LP uses continuous variables and convex linear structure; MILP adds discrete choices and can be much harder computationally.

**What should an optimization API return?** Decision plus feasibility, solver status, objective/bound/gap where applicable, versions, runtime, constraint diagnostics, and fallback/review information.

## 19. Design case: retention-budget allocation

For allocating a limited retention budget, cover:

1. customer/action/time origin, churn/reactivation definition, censoring and label delay;
2. baseline contact policy and causal treatment-effect evidence;
3. survival/uplift/value estimates with calibration and uncertainty;
4. eligibility, contact frequency, budget, channel, fairness and capacity constraints;
5. simple rank-by-value baseline versus optimization;
6. robust scenarios for uncertain effect/value and feasibility;
7. offline policy value/regret plus randomized online validation;
8. solver status/gap/time limit, stable fallback and human override;
9. contact, complaint, churn, margin and subgroup monitoring;
10. exact prediction/policy/solver versions, audit, rollback and retirement.

## 20. Interview checklist

- [ ] I can define time origin, event, censoring, competing risks, horizon, and action.
- [ ] I can explain Kaplan–Meier, Cox assumptions, C-index, time-dependent AUC, Brier score, and calibration.
- [ ] I can connect risk scores and CLV to capacity, cost, interventions, and selective labels.
- [ ] I can distinguish predictive demand from causal price response.
- [ ] I can formulate LP/MILP/constraint problems with variables, objective, constraints, units, and feasibility.
- [ ] I can interpret solver status, gap, tolerances, sensitivity, uncertainty, fallback, and predict-then-optimize regret.

## References

- scikit-survival, [Evaluating Survival Models](https://scikit-survival.readthedocs.io/en/stable/user_guide/evaluating-survival-models.html)
- scikit-survival, [User Guide](https://scikit-survival.readthedocs.io/en/stable/user_guide/)
- Google OR-Tools, [Optimization overview](https://developers.google.com/optimization)
- Google OR-Tools, [MathOpt basic example and termination handling](https://developers.google.com/optimization/math_opt/basic_example)
- Google OR-Tools, [CP-SAT solver limits](https://developers.google.com/optimization/cp/cp_tasks)

Modeling and solver libraries evolve. Pin the event/decision contract, data horizon, model, policy, optimization formulation, solver/runtime, tolerances, and evaluation protocol used for every claim.
