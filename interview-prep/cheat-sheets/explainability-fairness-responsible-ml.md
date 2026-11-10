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
title: "Explainability, fairness, and responsible ML interview cheat sheet"
description: "Model inspection, local and global explanations, calibration, uncertainty, abstention, fairness definitions, subgroup evidence, mitigation, governance, monitoring, and appeals."
summary: "Revise explanations and responsible decisions as context-bound evidence with explicit harms, uncertainty, ownership, release gates, human oversight, and lifecycle controls."
permalink: "/interview-prep/cheat-sheets/explainability-fairness-responsible-ml/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 9 · Explainability, fairness, and responsible ML"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 9 scope:** This review candidate derives from the approved master index and the cited primary documentation. It is separate from the Week 1–20 learning assessments.

**Target roles:** Senior Data Scientist, Applied Scientist, ML/AI Engineer, Responsible AI Engineer, Data Science Technical Lead  
**Use:** model review, high-impact decisions, explainability, fairness, governance, release, monitoring, and leadership interviews  
**Interview rule:** begin with the decision, affected people, plausible harms, legal/policy owner, and action enabled by an explanation. No metric or explanation method can decide fairness or acceptable risk by itself.

## 1. Thirty-second revision

- Interpretability is how understandable a model is; post-hoc explainability approximates or summarizes behavior after training.
- A global explanation describes overall behavior; a local explanation describes one prediction under a defined method and background/reference.
- Coefficients, impurity importance, permutation importance, PDP/ICE, SHAP, counterfactuals, examples, and saliency answer different questions.
- Feature importance is not causal importance. Correlated features, interactions, proxies, leakage, and model error change interpretation.
- Explain only after verifying the model, data, prediction, and preprocessing identity. A precise explanation of a bad model is still bad evidence.
- Calibrated probabilities support decisions; ranking discrimination alone does not establish reliable risk estimates.
- Uncertainty can be aleatoric, epistemic, distributional, or operational; one confidence score rarely covers all four.
- Abstention needs a threshold, fallback, capacity, user communication, and outcome evaluation.
- Fairness starts with harms, groups, decision context, and measurement quality. Demographic parity, equal opportunity, equalized odds, predictive parity, and calibration can conflict.
- Always report performance and error rates by meaningful intersections with uncertainty and sample support—not only one gap.
- Mitigation can act on data, training, threshold/policy, product process, or whether the model should be used at all.
- Governance needs ownership, intended/excluded use, data/model lineage, validation, approvals, monitoring, incident response, appeal, change triggers, and retirement.

## 2. Define the decision and explanation user

Document:

- decision, action, affected population, and decision maker;
- model output, threshold, ranking or allocation policy;
- user of the explanation: developer, reviewer, customer, regulator, auditor, or affected person;
- task the explanation must support: debug, contest, justify, understand, monitor, or improve;
- plausible harms, protected or otherwise important groups, and sensitive-data authority;
- acceptable uncertainty, review path, appeal, and override;
- owner for legal, policy, fairness, product, and technical decisions.

An explanation for debugging can be technical and distribution-level. An explanation to an affected user must be accurate, actionable, stable enough, privacy-safe, and appropriate to policy. Do not reuse one visualization for every audience.

## 3. Model inspection methods

| Method | Main question | Strength | Limitation |
|---|---|---|---|
| Linear coefficient | how does modeled log-odds/output change with a feature? | direct for the fitted model | scale, encoding, correlation and interactions matter |
| Tree impurity importance | which features reduced training impurity? | cheap, built in | biased toward high-cardinality/split-rich features |
| Permutation importance | how much held-out score drops when a feature is disrupted? | model agnostic, performance-linked | correlation can hide/share importance; distribution may become unrealistic |
| PDP | average modeled response as one/two features vary | global shape | assumes interpretable intervention; can evaluate implausible combinations |
| ICE | individual response curves | shows heterogeneity | visually dense; still model behavior, not causal effect |
| SHAP-style attribution | additive allocation versus a reference/background | local/global summaries | background and dependence assumptions change values; not causal |
| LIME-style surrogate | local simple approximation near a point | intuitive local view | sampling/kernel/seed instability and poor local fidelity |
| Counterfactual | what feasible change could alter the decision? | action-oriented | feasibility, causality, recourse cost and policy constraints are hard |
| Example/prototype | which known cases are similar? | concrete | similarity metric and privacy can mislead |
| Saliency/attention | which input regions/tokens influence a score under a method? | useful diagnostic | instability and faithfulness limits; attention is not proof of reasoning |

Choose the method from the question. Report model, data, preprocessing, reference/background, output scale, method parameters, and fidelity/stability checks.

## 4. Coefficients and correlated features

For logistic regression:

$$
\log\frac{p(y=1\mid x)}{1-p(y=1\mid x)}=\beta_0+\sum_j\beta_jx_j
$$

$e^{\beta_j}$ is an odds multiplier for a one-unit increase in $x_j$, holding modeled covariates fixed. Interpretation depends on units, encoding, interactions, regularization, sampling, and correct specification.

Do not say “feature $j$ causes the outcome.” Predictive coefficients can reflect confounding, selection, measurement, or proxies. With correlated features, coefficients and importance may be unstable or split arbitrarily. Use grouped/conditional analysis, domain review, stability checks, and causal methods only when the causal question and assumptions are explicit.

## 5. Permutation importance, PDP, and ICE

Permutation importance on held-out data is approximately:

$$
I_j=s(f,X,y)-s(f,\operatorname{permute}_j(X),y)
$$

where $s$ is a chosen score. Repeat permutations and report variability. A small value may mean redundancy with correlated features, not irrelevance. First confirm the model has acceptable held-out performance.

PDP for feature subset $S$ averages model predictions over other observed features:

$$
PD_S(x_S)=\mathbb{E}_{X_C}[f(x_S,X_C)]
$$

If $X_S$ and $X_C$ are dependent, the calculation may evaluate implausible combinations. ICE retains one curve per observation and can reveal interactions hidden by the average. Neither establishes the effect of intervening on a feature.

## 6. Local attributions and counterfactuals

For additive attribution, state:

- prediction/output explained: raw score, logit, probability, or class;
- reference/base value and background population;
- feature grouping and dependence handling;
- local additivity/fidelity;
- stability under small perturbations and plausible reference choices;
- sensitive proxy and privacy review.

A counterfactual should respect immutable attributes, domain constraints, causal/temporal order, action feasibility, cost, and model validity. “Increase income by ₹X” may be mathematically close but not actionable or fair. Distinguish an explanation from guaranteed recourse.

## 7. Calibration, uncertainty, and abstention

For binary outcomes, calibration means predictions near $p$ occur roughly $p$ of the time under the evaluated distribution. Evaluate reliability curves, Brier/log loss, calibration error with disclosed binning, and group/time slices.

Calibration can drift when prevalence, policy, or measurement changes. Calibrating on the final test set leaks evaluation. Fit calibration on a separate validation fold or nested procedure and retain an untouched test.

Uncertainty sources:

- **aleatoric:** irreducible outcome noise;
- **epistemic:** limited knowledge/data/model uncertainty;
- **distributional:** request differs from supported data;
- **operational:** missing/stale features, service failure, or version mismatch.

Abstention/deferral policy should define:

- confidence, OOD, rule, or disagreement signal;
- coverage-risk trade-off and subgroup effects;
- fallback or human-review capacity/SLA;
- what the user sees;
- monitoring and re-entry after recovery;
- whether deferred cases receive labels differently, creating selective feedback.

## 8. Fairness assessment

Start with harm mapping:

1. who is affected directly and indirectly;
2. allocation, quality-of-service, representation, privacy, and stereotyping harms;
3. groups and intersections with enough authority and data quality to measure;
4. decision and policy responsible for the harm—not only the model;
5. baseline process and alternative without AI;
6. metric, uncertainty, threshold, and owner for action.

Common definitions for binary decisions:

- **Demographic parity:** $P(\hat Y=1\mid A=a)$ is similar across groups.
- **Equal opportunity:** true-positive rates are similar across groups.
- **Equalized odds:** true-positive and false-positive rates are similar across groups.
- **Predictive parity:** precision/positive predictive value is similar across groups.
- **Calibration within groups:** predicted probabilities have similar outcome meaning within groups.

These encode different harm assumptions and may be mutually incompatible when base rates differ. Select and justify metrics with product, domain, legal/policy, and affected-stakeholder input. A small aggregate gap does not prove fairness.

## 9. Measurement and statistical discipline

For every group/intersection report:

- sample and event count;
- data and label quality;
- exposure/eligibility and missingness;
- selection rate, confusion-matrix rates, precision, calibration, utility, and accepted primary measures;
- confidence intervals or another uncertainty representation;
- threshold and policy;
- time/site/product slices;
- suppressed or pooled results when privacy or support is insufficient.

Multiple exploratory slices create false discoveries. Predeclare critical groups/metrics where possible, use hierarchical or multiplicity-aware reasoning, and treat small samples as uncertainty—not as permission to ignore a group.

Feedback loops matter: a decision can change future labels, access, behavior, and who remains observable. Compare outcomes, not only model scores.

## 10. Mitigation choices

### Before training

- improve collection/coverage and label quality;
- remove leakage and measurement bias;
- reweight/resample with clear target distribution;
- redesign features or problem framing;
- decide not to automate the decision.

### During training

- constrained optimization or reduction methods;
- group-robust objectives;
- adversarial or representation approaches;
- monotonicity or shape constraints where domain-justified.

### After training / policy

- group-aware or common thresholds subject to authority and trade-offs;
- calibrated risk bands;
- human review, appeals, resource changes, or alternative action;
- reject option/abstention;
- changed objective or eligibility policy.

Mitigating one metric can reduce accuracy, calibration, another fairness property, stability, or simplicity. Re-evaluate end to end, including affected outcomes. A library guarantee about a mathematical constraint does not certify that the system is fair.

## 11. Model cards and governance evidence

A release record should include:

- owner, decision, intended/excluded use and population;
- exact data, feature, label, split, code, model, dependency, and runtime identity;
- privacy/usage rights and sensitive-data handling;
- baseline, metrics, slices, uncertainty and limitations;
- explainability method and known interpretation limits;
- fairness harm analysis, selected metrics, trade-offs and accepted owner decision;
- security, robustness, load/cost and operational evidence;
- thresholds, abstention, human oversight, appeal and rollback;
- monitoring, label delay, incident, change/review and retirement triggers;
- approvals and unresolved risks.

Documentation is evidence and accountability infrastructure, not proof that the system is safe or fair.

## 12. Monitoring and incidents

Monitor by meaningful slice:

- eligibility/exposure and input/label missingness;
- score, threshold, selection, abstention, override and appeal rates;
- performance, calibration and fairness metrics after labels mature;
- explanation stability/fidelity and explanation-service failures;
- policy, feature, data, model and dependency identity;
- downstream outcomes and human-review workload;
- complaints, harms, incidents and unanticipated use.

Predefine alert severity and action. A fairness or calibration alert may require pausing, narrowing scope, reverting policy/model, increasing review, fixing data, or gathering evidence. Preserve affected decisions and versions, protect sensitive data, communicate uncertainty, and perform retrospective evaluation.

## 13. Minimal slice-metric example

```python
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class SliceCounts:
    total: int
    selected: int
    positives: int
    true_positives: int

    @property
    def selection_rate(self) -> float | None:
        return self.selected / self.total if self.total else None

    @property
    def true_positive_rate(self) -> float | None:
        return self.true_positives / self.positives if self.positives else None


def counts_by_group(
    groups: list[str], truths: list[int], predictions: list[int]
) -> dict[str, SliceCounts]:
    raw: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0, 0])
    for group, truth, prediction in zip(groups, truths, predictions, strict=True):
        row = raw[group]
        row[0] += 1
        row[1] += int(prediction == 1)
        row[2] += int(truth == 1)
        row[3] += int(truth == 1 and prediction == 1)
    return {group: SliceCounts(*values) for group, values in raw.items()}
```

This exposes denominators. A real assessment still needs uncertainty, intersectional groups, data-quality checks, privacy thresholds, more error/utility metrics, and an owner-approved harm interpretation.

## 14. Common failure modes

- Explaining a model before validating its accuracy, calibration, and data lineage.
- Calling feature importance causal.
- Ignoring preprocessing or explaining a transformed feature as if it were raw.
- Using one SHAP background/reference without sensitivity analysis.
- Evaluating PDP in impossible correlated-feature regions.
- Treating attention or saliency as proof of reasoning.
- Choosing a fairness metric after seeing which one looks best.
- Reporting only an aggregate ratio without denominators or uncertainty.
- Dropping sensitive attributes and assuming proxies disappear.
- Applying a mitigation library and declaring the system fair.
- Calibrating or selecting thresholds on the final test set.
- Deferring uncertain cases without capacity, SLA, or selective-label analysis.
- Publishing a model card once but not linking it to release/change/retirement.

## 15. Rapid interview questions

**Global versus local explanation?** Global methods summarize behavior across a population; local methods explain one prediction under defined references and assumptions.

**Why is permutation importance low for a useful feature?** A correlated feature may substitute for it, the model may use it only in a slice/interaction, or the held-out score/model may be weak.

**Does SHAP show causality?** No. It allocates model output relative to a background under method/dependence assumptions; it explains modeled associations.

**Why can fairness metrics conflict?** They encode different harm criteria and can be mathematically incompatible when outcome base rates differ.

**Why keep sensitive attributes for evaluation?** Removing them from training does not remove proxies; lawful, protected evaluation data may be necessary to measure group outcomes.

**What makes abstention useful?** It improves risk only when its signal is meaningful and the fallback, capacity, communication, monitoring, and group effects are acceptable.

## 16. Design case: high-impact risk model

For a model that prioritizes applications for manual review, cover:

1. decision, eligibility, affected users, baseline process, harms and owners;
2. label definition, policy/selective-label bias, sensitive-data authority and point-in-time features;
3. baseline, calibration, thresholds, capacity and abstention;
4. group/intersection performance, uncertainty, fairness definitions and trade-offs;
5. reviewer and user explanations with fidelity, stability, privacy and appeal;
6. model card, independent validation, approval and unresolved-risk record;
7. canary/shadow release, outcome experiment where appropriate and rollback;
8. monitoring after label maturation, overrides, appeals, complaints and incidents;
9. change triggers for data, policy, population, threshold and law;
10. retirement and deletion requirements.

## 17. Interview checklist

- [ ] I can distinguish interpretability, post-hoc explanation, causality, and recourse.
- [ ] I can compare coefficients, permutation importance, PDP/ICE, SHAP/LIME, counterfactuals, examples, and saliency.
- [ ] I can evaluate calibration, uncertainty, OOD signals, and abstention.
- [ ] I can define fairness harms and explain metric trade-offs with denominators and uncertainty.
- [ ] I can propose data, training, policy, product, and non-deployment mitigations.
- [ ] I can design model-card evidence, approval, monitoring, appeal, incident, and retirement workflows.

## References

- scikit-learn, [Inspection](https://scikit-learn.org/stable/inspection.html)
- scikit-learn, [Permutation feature importance](https://scikit-learn.org/stable/modules/permutation_importance.html)
- Fairlearn, [Assessment](https://fairlearn.org/main/user_guide/assessment/index.html)
- Fairlearn, [Mitigations](https://fairlearn.org/main/user_guide/mitigation/index.html)
- NIST, [AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- NIST, [AI RMF Playbook](https://airc.nist.gov/airmf-resources/playbook/)

Fairness, explanation, and governance requirements are context- and jurisdiction-dependent. Technical documentation and metrics support—but do not replace—the responsible owners' legal, policy, product, and affected-stakeholder decisions.
