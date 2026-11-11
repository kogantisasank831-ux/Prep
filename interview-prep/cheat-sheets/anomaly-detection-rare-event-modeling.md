---
layout: "week"
status: "review"
version: "0.1.0"
last_reviewed: "2026-11-11"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "Anomaly detection and rare-event modeling interview cheat sheet"
description: "Detection contracts, robust baselines, isolation and local-density methods, deep representations, change points, class imbalance, calibration, metrics, thresholds, backtests, and alert operations."
summary: "Revise anomaly and rare-event systems from event definitions and robust baselines through leakage-safe evaluation, alert-budget thresholds, delayed labels, monitoring, and incident response."
permalink: "/interview-prep/cheat-sheets/anomaly-detection-rare-event-modeling/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 9 · Anomaly detection and rare-event modeling"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 9 source-backed scope:** This review candidate publishes the canonical interview sheet without altering its instructional body. It remains separate from the Week 1–20 learning assessments.

**Target roles:** Lead Data Scientist, Senior Data Scientist, Applied Scientist, ML Engineer, AI Engineer  
**Use:** fraud, equipment monitoring, cybersecurity, quality, observability, risk, and imbalanced-classification interviews  
**Interview rule:** define the event, unit, context, label delay, alert capacity, and consequence of each error before choosing a detector. An anomaly score is not an incident, and a rare event is not necessarily anomalous.

## 1. Thirty-second revision

- An anomaly is unusual relative to a reference context; a rare event is infrequent. A rare but regular event may not be anomalous, and a subtle fraud pattern may not be globally rare in feature space.
- Distinguish outlier detection on contaminated training data from novelty detection trained mainly on normal data.
- Define point, contextual, and collective anomalies. The same value may be normal for one machine, season, location, or customer and abnormal for another.
- Establish simple baselines first: rules, robust statistics, seasonal residuals, and known limits often outperform complex models operationally.
- Isolation Forest isolates points with short random-partition paths; LOF compares local density; one-class SVM learns a boundary; autoencoders score reconstruction error. Each has assumptions and threshold problems.
- For supervised rare-event models, use time-aware/identity-aware splits, class weighting or sampling only inside training, calibrated probabilities, and decision thresholds based on cost/capacity.
- Accuracy and ROC-AUC can look excellent under extreme imbalance. Prefer precision-recall behavior, recall at an alert budget, false alerts per unit time, detection delay, and event-level metrics.
- Never select a threshold from the final test set. Fit model, calibrate, and choose threshold on separate data or a nested procedure.
- Backtesting must reproduce information availability, delayed labels, deduplication, suppression, and incident grouping.
- Synthetic anomaly injection tests sensitivity to specified perturbations; it does not prove performance on real unknown incidents.
- Detection needs an operating system: aggregation, cooldown, severity, routing, human feedback, explanation/context, rollback, and drift monitoring.
- A lower false-positive rate can still create more alerts if traffic grows. Monitor counts, rates, workloads, and missed-event estimates.

## 2. Define the detection contract

Write:

> For **entity E** and observation window **W**, use information available by **time T** to identify **event definition A**, produce **score S** and **action X**, under **alert capacity C**, with acceptable **miss, false-alarm, delay, and harm limits H**.

Clarify:

- unit: transaction, device reading, time window, user, account, host, batch, image, or graph substructure;
- event start/end and whether multiple records belong to one incident;
- normal reference population and its stationarity;
- contextual keys: asset type, geography, hour, season, operating state, user cohort;
- contamination in training data;
- labels, adjudication policy, censoring, and feedback delay;
- action: block, review, warn, degrade, schedule maintenance, or only log;
- capacity and cost by severity;
- excluded use and protected populations.

The target should be an operationally resolvable event. “Find anything weird” is an exploratory request, not a deployable specification.

## 3. Taxonomy

### By structure

| Type | Meaning | Example |
|---|---|---|
| point anomaly | one observation is unusual | unusually large payment |
| contextual anomaly | value is unusual given context | high temperature for idle equipment |
| collective anomaly | a sequence/set is abnormal as a whole | repeated small login failures |
| change point | generating process changes | sensor mean shifts after maintenance |
| graph anomaly | node/edge/subgraph pattern is unusual | coordinated accounts sharing devices |

### By supervision

- **Supervised:** labeled normal and event cases; usually rare-event classification.
- **Semi-supervised/novelty:** train a normality model on mostly clean normal examples.
- **Unsupervised/outlier:** assume anomalies are a minority or differ structurally without labels.
- **Positive-unlabeled:** known positives exist, while “unlabeled” mixes negative and positive cases.
- **Weak supervision:** combine noisy rules/heuristics into probabilistic labels or features.

### Outlier versus novelty APIs

In common libraries, fitting and predicting on the same contaminated dataset can use a different interface and score interpretation from fitting a boundary on normal reference data and scoring future points. Verify exact estimator semantics and score direction.

## 4. Start with robust baselines

### Statistical rules

For approximately symmetric stable data:

- z-score uses mean and standard deviation;
- modified z-score uses median and median absolute deviation (MAD);
- interquartile-range rules use quantiles;
- control charts detect process shifts under specified assumptions;
- extreme-value models focus on distribution tails.

Mean and standard deviation can be distorted by the anomalies they should detect. MAD is robust but becomes zero for constant/discrete samples and still ignores context and dependence.

### Time-series baselines

Model expected value by:

- seasonal median/quantiles;
- rolling baseline with lagged-only values;
- exponential smoothing;
- decomposition into trend, seasonality, and residual;
- regression on calendar/operating context.

Score residuals rather than raw values when seasonality is strong. Use causal windows; a centered rolling statistic leaks future values in online evaluation.

### Rule systems

Rules are strong when domain limits are known, consequences are severe, and explanations are required. Production systems commonly combine:

- hard safety constraints;
- statistical/model score;
- trusted allow/deny context;
- temporal aggregation;
- human escalation.

Measure each rule's incremental value and interactions. An unversioned pile of rules becomes an untestable model.

## 5. Classical unsupervised and novelty methods

| Method | Core idea | Strength | Frequent failure |
|---|---|---|---|
| Isolation Forest | anomalies isolate in fewer random splits | scalable, nonlinear, little distribution assumption | contamination/threshold and irrelevant features |
| Local Outlier Factor | compare local density with neighbors | detects local anomalies | high dimension, neighbor choice, tricky new-point semantics |
| One-Class SVM | boundary around normal data in kernel space | flexible novelty boundary | scaling, kernel parameters, poor scaling |
| Elliptic envelope | robust Gaussian covariance contour | interpretable for elliptical data | multimodal/non-Gaussian structure |
| kNN/distance score | far from reference neighbors | intuitive | scale, memory, distance concentration |
| clustering residual | distance to centroid or noise membership | reuses segmentation | clusters do not necessarily define normality |
| kernel density | low estimated density | probabilistic intuition | bandwidth and dimensionality |

No detector automatically knows the event rate. The algorithm often produces a ranking; the threshold creates the operational classifier.

### Isolation Forest intuition

Randomly choose features and split values. Points in sparse/extreme regions generally need fewer splits to isolate. Important checks:

- subsample and tree count;
- contamination or threshold handling;
- categorical encoding and irrelevant dimensions;
- stability across seeds/time;
- score drift when the population changes.

### LOF intuition

LOF compares a point's local reachability density with neighbors. A point can be anomalous within a dense/heterogeneous population even if it is not globally extreme. Choose neighbor count against expected local structure and evaluate boundary cases.

## 6. Representation and deep methods

### Autoencoders

Train an encoder-decoder to reconstruct normal inputs and use reconstruction error or a learned score.

Failure modes:

- an over-capable network reconstructs anomalies too;
- anomalies contaminate training;
- pixel/feature reconstruction does not match event semantics;
- scaling makes some features dominate;
- threshold changes across cohorts;
- adversarial or shifted inputs receive low error.

Use bottlenecks/regularization, normal reference validation, per-feature residual review, and a simple baseline. Variational autoencoders add a probabilistic latent objective but do not create guaranteed anomaly probabilities.

### Sequence, image, graph, and embedding methods

- forecasting residuals or sequence models for temporal data;
- convolutional/self-supervised representations for images;
- graph features/embeddings for connected fraud or security events;
- pretrained embeddings followed by density/distance scoring for text.

Representation learning changes the meaning of distance. Validate the representation on incident retrieval and important counterexamples, not only pretraining loss.

## 7. Change-point detection versus point anomalies

Point detection asks whether an observation is unusual; change-point detection asks whether the data-generating regime changed.

Methods include CUSUM, Bayesian online change detection, binary segmentation, PELT, window-based tests, and kernel costs. Design choices:

- offline versus online;
- mean, variance, distribution, or relationship change;
- minimum segment length;
- penalty or false-alarm control;
- expected detection delay;
- repeated alerts after one shift.

A sustained shift can cause every later point to trigger a point-anomaly rule. Detect the regime change, open one incident, and reset/relearn only under a controlled policy.

## 8. Supervised rare-event classification

When reliable labels exist, supervised learning often provides better task alignment.

### Splits and leakage

- split by time for future deployment;
- group by user/device/account so identity patterns do not leak;
- prevent duplicates or incident fragments across splits;
- compute aggregates with point-in-time data;
- preserve label delay and adjudication rules;
- test on a recent untouched period and critical slices.

Random stratified splits can be misleading when behavior, attackers, machines, or policies evolve.

### Handling imbalance

| Technique | Benefit | Risk/control |
|---|---|---|
| class weights | emphasizes rare-class loss | probability calibration may change |
| undersampling | faster, balanced training signal | discards majority structure |
| oversampling | more rare examples per batch | duplicates and overfit |
| synthetic sampling | interpolated minority examples | unrealistic data/leakage if before split |
| focal loss | focuses on hard examples | extra tuning and calibration changes |
| hard-negative mining | learns confusing normal cases | feedback selection bias |
| two-stage cascade | cheap filter then precise model | compounded recall loss |

Apply sampling only to training folds. Keep evaluation prevalence representative, or reweight explicitly and report the target prevalence.

### Calibration

A ranking score is not necessarily a probability. Use reliability diagrams, Brier/log loss, and calibration on data separated from model fitting when possible. Platt/sigmoid, isotonic, or other calibrators require enough representative data and must be refit when the score distribution shifts.

## 9. Metrics for rare events

From true positives `TP`, false positives `FP`, false negatives `FN`, and true negatives `TN`:

- precision = `TP / (TP + FP)`
- recall/sensitivity = `TP / (TP + FN)`
- specificity = `TN / (TN + FP)`
- false-positive rate = `FP / (FP + TN)`
- F1 = harmonic mean of precision and recall

### Why accuracy and ROC can mislead

At 0.1% prevalence, predicting “normal” always yields 99.9% accuracy. ROC-AUC measures ranking across all thresholds and can look strong because the negative class is enormous. PR-AUC focuses on positive retrieval, but its baseline and interpretation depend on prevalence.

Operational metrics:

- recall at `K` alerts per day or review capacity;
- precision at `K`;
- alerts per entity/time;
- incident-level recall after deduplication;
- detection delay and lead time;
- cost avoided versus review/intervention cost;
- severity-weighted miss rate;
- coverage of novel categories;
- workload and reviewer agreement.

Report uncertainty, especially with few positive events. One incident producing many rows should not falsely create a narrow interval.

## 10. Threshold selection

Choose threshold using the action:

`expected cost(t) = C_FP × FP(t) + C_FN × FN(t) + intervention costs`

or optimize recall subject to alert capacity, minimum precision, latency, and safety constraints.

Thresholds may differ by:

- cohort or device type;
- event severity;
- review queue;
- time/context;
- model uncertainty.

Group thresholds can improve performance but may create fairness, legal, or operational concerns. Analyze the entire decision pipeline and obtain appropriate review.

Do not tune a threshold on the final test set. Freeze it before test evaluation, then monitor it after deployment.

## 11. Evaluation and backtesting

### Offline test design

1. Reconstruct exactly what was known at scoring time.
2. Use rolling or future holdouts.
3. Preserve natural event prevalence.
4. Group records into incidents before final metrics.
5. Apply production suppression, cooldown, and queue capacity.
6. Evaluate by cohort, severity, device, geography, and time.
7. Compare against rules/current system and analyst decisions.
8. Replay historically important incidents and benign spikes.
9. Report confidence intervals and label uncertainty.

### Labels are part of the system

Labels may be delayed, selectively reviewed, inconsistent, or changed by intervention. This creates:

- verification bias: only alerted cases receive labels;
- censoring: unresolved events look negative;
- policy feedback: blocked events cannot reveal their natural outcome;
- concept drift: fraud/adversaries adapt;
- reviewer drift: adjudication standards change.

Maintain label provenance, adjudication version, disagreement, and time-to-label. Consider randomized review samples among non-alerts to estimate misses, where ethical and practical.

### Synthetic injection

Injecting spikes, shifts, drops, stuck sensors, or known attack patterns is useful for regression and sensitivity testing. It only supports those injected perturbations. Separate synthetic, historical replay, shadow, and live evidence.

## 12. Minimal dependency-free example: robust modified z-scores

```python
from __future__ import annotations

from statistics import median
from typing import Sequence


def modified_z_scores(values: Sequence[float]) -> list[float]:
    """Return median/MAD scores; reject samples with zero dispersion."""
    if len(values) < 3:
        raise ValueError("at least three values are required")

    center = median(values)
    absolute_deviations = [abs(value - center) for value in values]
    mad = median(absolute_deviations)
    if mad == 0.0:
        raise ValueError("MAD is zero; use a domain fallback or another scale")

    consistency_constant = 0.6744897501960817
    return [
        consistency_constant * (value - center) / mad
        for value in values
    ]


sample = [10.0, 10.1, 9.9, 10.2, 9.8, 100.0]
scores = modified_z_scores(sample)
flagged = [value for value, score in zip(sample, scores, strict=True) if abs(score) > 3.5]
assert flagged == [100.0]
```

This is a univariate screening example, not a universal threshold. It ignores seasonality, dependence, multiple testing, and incident costs.

## 13. Alert pipeline and production design

`score → contextual threshold → aggregate/deduplicate → severity → suppress/cooldown → route → investigate → label → learn`

Design:

- idempotent event IDs and score timestamps;
- model/feature/rule/threshold versions on each alert;
- score reason and relevant context;
- aggregation into incidents;
- separate hard safety rules from learned scores;
- queue backpressure and degraded modes;
- retry/dead-letter behavior for delivery;
- reviewer controls and audit history;
- shadow and canary rollout;
- kill switch and rollback to known rules/model;
- privacy and access controls for sensitive investigation data.

### Monitoring

Monitor:

- traffic and eligible entity counts;
- feature missingness/range/drift;
- score and threshold distributions;
- alert counts/rates by slice;
- deduplication and suppression rates;
- review capacity, backlog, and latency;
- delayed precision/recall proxies and confirmed outcomes;
- incident detection delay;
- model/rule disagreements;
- data/feature pipeline failures;
- feedback coverage and reviewer agreement.

Drift does not automatically require retraining. Diagnose source, data quality, policy change, seasonality, and outcome impact first.

## 14. Library map

| Tool | Best fit | Verify |
|---|---|---|
| scikit-learn | Isolation Forest, LOF, one-class SVM, robust covariance | novelty/outlier API, score direction, threshold |
| PyOD | broad anomaly-detector toolbox | exact detector maturity, dependencies, benchmark fit |
| River | online learning and streaming statistics | update order, delayed labels, reset strategy |
| ruptures | offline change-point detection | cost model, penalty, minimum segment |
| statsmodels | statistical/seasonal time-series baselines | stationarity and interval assumptions |
| PyTorch/JAX | learned representations and sequence models | reconstruction shortcut, calibration, serving |
| Evidently/monitoring stack | data/score monitoring | metric semantics and operational integration |

Library breadth does not replace a representative backtest. Pin versions and record exact defaults.

## 15. Rapid interview questions

**Rare event versus anomaly?**  
Rarity is frequency; anomaly is deviation from an expected context. They overlap but are not equivalent.

**Outlier detection versus novelty detection?**  
Outlier detection fits amid possible contamination; novelty detection learns from mostly normal reference data and scores new observations.

**Why can a reconstruction autoencoder miss anomalies?**  
High capacity or learned generalization may reconstruct abnormal inputs well, and reconstruction loss may not align with the event.

**Why prefer PR curves under imbalance?**  
They expose the precision-recall trade-off for retrieving rare positives, whereas abundant negatives can make ROC behavior appear comfortable.

**How do you set contamination?**  
Do not guess it as truth. Use known prevalence ranges, labeled validation, capacity/cost constraints, and sensitivity analysis.

**What if labels exist only for alerted cases?**  
Evaluation is selection-biased. Add unbiased sampling/audits where possible, use delayed outcomes/weak supervision carefully, and state uncertainty.

**How do you reduce alert fatigue?**  
Improve ranking/thresholds, group records into incidents, add cooldown/suppression, prioritize severity, enrich context, and measure reviewer capacity and miss cost.

**When should a detector abstain?**  
When input validity, reference coverage, or score uncertainty is outside the supported domain; route to safe default or review.

## 16. Lead-level case: predictive maintenance

Structure the answer:

1. Define failure modes, assets, operating regimes, lead-time requirement, maintenance action, and costs of missed versus unnecessary service.
2. Build a point-in-time asset timeline including telemetry, maintenance, configuration, utilization, and label/adjudication delay.
3. Split by future time and hold out assets or sites to test generalization.
4. Establish engineering limits, robust seasonal residuals, and simple supervised baselines.
5. Compare anomaly, forecasting-residual, survival/risk, and supervised failure models according to label availability.
6. Evaluate event recall, false alerts per asset-month, lead time, maintenance capacity, severity, and slices by asset type/site.
7. Replay failures and benign regime changes; shadow without triggering maintenance.
8. Aggregate signals into incidents, explain contributing sensors/context, provide abstention for unseen regimes, and keep safety rules independent.
9. Canary by site/asset class, monitor workload/outcomes, document threshold changes, and retain rollback.

The decision objective is avoided downtime and safe maintenance—not the prettiest anomaly-score distribution.

## 17. Final checklist

- [ ] I distinguish anomaly, rare event, novelty, outlier, and change point.
- [ ] I define entity, context, window, label delay, action, and alert capacity.
- [ ] I begin with robust rules/statistical baselines.
- [ ] I know Isolation Forest, LOF, one-class SVM, covariance, and autoencoder assumptions.
- [ ] I prevent temporal, identity, aggregate, and resampling leakage.
- [ ] I report PR behavior, alert-budget metrics, incident recall, and delay.
- [ ] I choose thresholds outside the test set using cost/capacity constraints.
- [ ] I replay incidents with production deduplication and suppression.
- [ ] I account for selective/delayed labels and feedback loops.
- [ ] I design monitoring, human review, degraded modes, and rollback.

## 18. Primary references

- [scikit-learn novelty and outlier detection guide](https://scikit-learn.org/stable/modules/outlier_detection.html)
- [scikit-learn Isolation Forest documentation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)
- [scikit-learn Local Outlier Factor documentation](https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.LocalOutlierFactor.html)
- [PyOD documentation](https://pyod.readthedocs.io/en/latest/)
- [River anomaly-detection documentation](https://riverml.xyz/latest/api/anomaly/)
- [ruptures documentation](https://centre-borelli.github.io/ruptures-docs/)
- [Liu, Ting, and Zhou, Isolation Forest](https://doi.org/10.1109/ICDM.2008.17)
- [Breunig et al., LOF: Identifying Density-Based Local Outliers](https://doi.org/10.1145/335191.335388)
- [Saito and Rehmsmeier, Precision-Recall Plot Is More Informative for Imbalanced Datasets](https://doi.org/10.1371/journal.pone.0118432)
- [scikit-learn probability calibration guide](https://scikit-learn.org/stable/modules/calibration.html)
