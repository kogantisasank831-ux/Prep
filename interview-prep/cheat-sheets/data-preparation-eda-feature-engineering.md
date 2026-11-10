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
title: "Feature engineering and ML data validation interview cheat sheet"
description: "Modeling grain, data identity, splits, leakage, feature design, missingness, temporal aggregates, selection, point-in-time correctness, validation layers, drift, and parity."
summary: "Revise features as governed time-aware data products with reproducible identity, deployment-aligned validation, explicit failure policy, and online/offline evidence."
permalink: "/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 8 · Expanded features and validation"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 8 source:** This review candidate updates the prepared `26_Feature_Engineering_Data_Validation_Cheat_Sheet.md` artifact in the Prep site. It is separate from the Week 1–20 learning assessments.

**Target roles:** Data Scientist, Lead Data Scientist, ML Engineer, AI Engineer, Applied Scientist  
**Use:** modeling, data-quality, leakage, feature-store, ML-system-design, debugging, and leadership interviews  
**Interview rule:** a feature is not merely a column. It has an entity key, event time, availability time, source, transformation, default, freshness contract, owner, and allowed use.

## 1. Thirty-second revision

- Define the prediction unit, entity, prediction time, horizon, outcome window, label availability, and action before exploring columns.
- Preserve immutable source/snapshot and transformation identities. A reproducible model needs reproducible data, labels, features, splits, and code.
- Split according to deployment: by entity/group, time, geography, or combinations. Fit every learned preprocessing step on the training fold only.
- Leakage includes future data, target-derived features, post-outcome records, duplicated entities, full-data preprocessing, aggregate leakage, and point-in-time errors.
- Join a feature using what was available—not merely what had happened—at prediction time.
- Missing, zero, unknown, not applicable, and censored are different states. Preserve their semantics.
- Start with stable, explainable features tied to the mechanism; add complexity only when cross-validated error analysis justifies it.
- One-hot, ordinal, hashing, frequency, target encoding, and embeddings solve different cardinality and model constraints. Target encoding must be out-of-fold and time-safe.
- Validate schema, content, relationships, domain rules, labels, splits, transformation outputs, offline/online parity, freshness, and meaningful slices.
- Drift is a symptom. Separate real population change, seasonality, upstream bugs, sampling shifts, and training-serving skew before responding.
- Never silently infer a new schema or accept a new baseline just because current data fails.
- Quarantine bad partitions, record scoped exceptions with expiry, and block publication when an accepted critical rule fails.

## 2. Define the modeling grain before features

Use a contract such as:

> At **prediction time $t$**, for **entity $e$**, predict **outcome $Y$** during **$[t+h_1,t+h_2]$** so that **actor A** can take **action D**.

Record:

- prediction unit and unique key;
- entity, event, processing, and availability timestamps;
- label definition, source, observation window, delay, revisions, and censoring;
- training, validation, test, and serving populations;
- intended and excluded use;
- acceptable latency/freshness and failure response;
- business and data owners.

Examples:

- churn: one customer at weekly decision time, outcome in next 30 days;
- fraud: one transaction at authorization time, confirmed label after investigation;
- ranking: one query–candidate pair at request time, observed interaction under exposure;
- forecasting: one series–horizon target at forecast origin.

If the grain is ambiguous, joins, duplicates, leakage checks, and metrics will also be ambiguous.

## 3. Preserve data identity and provenance

For each dataset stage retain:

- source systems and collection purpose;
- access/usage rights and privacy class;
- extraction query/job and parameters;
- schema and contract version;
- partition range and watermark;
- transformation code/config version;
- row/entity counts and checksums/manifests;
- raw, cleaned, labeled, transformed, feature, and published identities;
- environment, owner, and creation time.

“The latest table” is not a reproducible training input. Use immutable snapshots or manifests and distinguish corrected/reprocessed data from the original evidence.

## 4. Split strategy is part of the model

| Deployment pattern | Preferred evaluation boundary | Leakage prevented |
|---|---|---|
| IID new rows | random/stratified split | class imbalance only; not entity repetition |
| repeat records per entity | group split by entity | same customer/device/patient in train and test |
| future prediction | temporal/rolling split | future information and regime optimism |
| new sites/regions | group/geographic holdout | location-specific memorization |
| model/tuning selection | nested CV or locked final test | tuning on final evaluation |
| ranking/recommendation | user/time-aware split with exposure | future interactions and repeated candidate leakage |

Rules:

1. Split raw entities/events before fitted transformations.
2. Deduplicate and near-deduplicate with the deployment grain in mind.
3. Fit imputers, scalers, encoders, feature selection, resampling, and text vocabularies inside each training fold.
4. Preserve a locked final set after model and threshold selection.
5. Use a temporal gap when labels/features near the boundary overlap the future outcome window.

Repeated K-fold scores do not repair a split that violates deployment.

## 5. Leakage taxonomy

| Leakage type | Example | Prevention |
|---|---|---|
| Target leakage | “refund issued” predicts fraudulent transaction | causal timeline and feature review |
| Future leakage | next-month balance in current churn score | event/availability-time join |
| Label-window leakage | activity inside the outcome window used as input | explicit cutoff and horizon |
| Train–test leakage | scaler or vocabulary fitted on all data | pipeline fitted per train fold |
| Entity leakage | same customer in train and validation | group-aware split |
| Duplicate leakage | near-identical documents/images cross sets | content hash/near-duplicate detection |
| Aggregate leakage | customer lifetime aggregate includes future events | cutoff-aware window aggregation |
| Target encoding leakage | category mean includes the current row/validation | out-of-fold and time-safe encoding |
| Selection leakage | dataset contains only users who completed a post-treatment action | eligibility from pre-decision state |
| Serving leakage | offline feature uses a source unavailable online | availability contract and parity test |

Ask of every feature: **Could this exact value have been known, computed, and retrieved at the real decision time?**

## 6. Feature-engineering mental model

A good feature should be:

- causally/operationally available at prediction time;
- stable enough for the deployment horizon;
- expressive of a plausible mechanism;
- computable within serving cost and latency;
- consistently defined offline and online;
- monitored and owned;
- compliant with privacy, fairness, and policy constraints.

Start with baselines:

1. constant/rule or historical rate;
2. raw stable variables;
3. simple recency, frequency, magnitude, trend, and interaction features;
4. domain aggregates;
5. learned representations only where they add validated value.

Feature importance is not proof of causality or data quality. A leaked identifier often appears extremely important.

## 7. Numeric features

Common transformations:

- standardization: `(x−μ)/σ`;
- robust scaling using median/IQR;
- min–max scaling when bounded inputs are required;
- log or signed-log for heavy positive tails;
- winsorization/capping using training-derived, domain-approved rules;
- bins/splines for nonlinear effects;
- ratios only with denominator semantics and zero handling;
- interactions when the model cannot learn them efficiently.

Scaling matters for distance-based models, regularized linear models, SVMs, neural networks, and optimization. Tree ensembles usually do not require monotonic scaling, but still need valid units, finite values, and consistent missing semantics.

Treat outliers as possible data errors, rare valid cases, regime changes, or the business events of interest. Do not delete them automatically.

## 8. Categorical features

| Method | Suitable when | Main risk |
|---|---|---|
| One-hot | modest cardinality, linear/tree baseline | wide sparse matrix |
| Ordinal | real order exists or tree model supports category order carefully | invented order |
| Frequency/count | cardinality is high and prevalence helps | drift and no target relation |
| Hashing | open vocabulary and bounded memory | collisions and weak interpretability |
| Target encoding | category has outcome signal | leakage/overfit; needs OOF smoothing |
| Learned embedding | large data and interactions justify it | cold start, complexity, serving parity |

Specify unknown/unseen-category behavior. Reserve a stable unknown token; do not map unseen categories to an arbitrary existing class.

## 9. Missing data and labels

Distinguish:

- missing because not collected;
- structurally not applicable;
- not yet available;
- suppressed for privacy;
- sensor/system failure;
- censored outcome;
- true zero.

MCAR/MAR/MNAR are assumptions about the missingness mechanism, not labels produced by a library. Use domain reasoning, missingness indicators, sensitivity analysis, and data-collection fixes.

For labels, define:

- authoritative source and adjudication;
- positive and negative observation rules;
- availability delay and revision policy;
- ambiguous/unlabeled handling;
- class prevalence by time and slice;
- inter-annotator agreement or audit sample where applicable.

Absence of a recorded event is not automatically a negative outcome.

## 10. Temporal, text, and aggregate features

### Temporal

- age/tenure at prediction time;
- recency since last event;
- counts/sums/unique counts over fixed lookback windows;
- slopes, volatility, seasonality, and change from baseline;
- cyclical encodings `sin(2πt/P)` and `cos(2πt/P)`;
- holiday/event flags known at forecast/prediction time.

### Text/documents

- language, length, format, extraction confidence;
- lexical features, embeddings, or task-specific model outputs;
- document/version identity and access rights;
- duplication/near-duplication and contamination;
- generation timestamp and model/version for derived features.

### Aggregates

An aggregate requires entity key, event-time window, availability-time cutoff, filter, unit, late-data policy, and transform version. “Last 30 days” is incomplete without the exact reference time and inclusion boundary.

## 11. Feature selection and imbalance

Feature-selection families:

- **filter:** variance, correlation, mutual information;
- **wrapper:** forward/backward selection, recursive elimination;
- **embedded:** L1, tree/boosting importance;
- **stability-based:** repeated folds/time windows and slice consistency.

Run selection inside training folds. Prefer a smaller stable set when additional features add fragile or unexplained lift.

For imbalance:

- choose metrics that reflect costs and prevalence;
- use class/sample weights or resampling inside the training fold;
- tune the decision threshold on validation data;
- preserve real prevalence in validation/test;
- evaluate calibration and operational capacity.

SMOTE-like methods can be useful for some continuous feature spaces but may create impossible samples, leak across folds, or distort categories/time. Validate against simpler weighting and threshold baselines.

## 12. Point-in-time correctness

Track both:

- **event time:** when the real-world fact occurred;
- **availability time:** when the system could actually retrieve the processed value.

For a prediction at `t_p`, use only feature rows with `availability_time ≤ t_p`.

and select the appropriate event/aggregation window. Late-arriving data can have an old event time but a future availability time and must not appear in historical training before it was available.

Test:

- events exactly at cutoff boundaries;
- late and corrected records;
- source timezone and DST;
- backfilled partitions;
- feature expiration/TTL;
- entity reuse or changing identifiers;
- offline historical retrieval against online values for matched entity–timestamp pairs.

## 13. Validation layers

| Layer | Example checks | Failure response |
|---|---|---|
| Schema | required fields, type, shape, encoding | reject/quarantine incompatible data |
| Content | finite, ranges, units, categories, missing/default | block critical violations; sample evidence |
| Relationships | uniqueness, keys, referential integrity, grain | stop duplicate/fan-out corruption |
| Domain | conservation, monotonicity, feasible combinations | domain-owner review |
| Temporal | order, gaps, overlap, timezone, freshness, late data | hold affected partitions |
| Labels | source, delay, prevalence, agreement, revisions | relabel, exclude, or mark uncertain |
| Splits | entity/time isolation, duplicates, contamination | rebuild split before training |
| Transform | fitted-on-train, deterministic outputs, version | block candidate |
| Parity | offline/online names, values, defaults, precision | stop release or degrade safely |
| Slices | coverage and failure rates for meaningful groups | targeted investigation |

Test validators with known-good data and deliberately seeded failures. Passing a schema inferred from historical data proves only conformity to that inferred schema, not business fitness.

## 14. Drift, skew, and parity

- **Data drift:** input distribution changes over time.
- **Concept drift:** relationship between inputs and outcome changes.
- **Label drift:** outcome prevalence changes.
- **Schema drift:** structure or categories change.
- **Training-serving skew:** values or transformations differ between offline training and online inference.

Possible statistics include missing-rate change, PSI, KS, Wasserstein distance, Jensen–Shannon divergence, population moments, and category-frequency distance. Choose feature-specific methods, sample sizes, slices, and thresholds based on accepted risk; do not copy one threshold across all features.

A drift alert should answer:

1. Is the data pipeline healthy?
2. Is the change expected seasonality or a real population shift?
3. Does model performance/calibration change?
4. Is retraining valid, or would it learn a corrupted regime?
5. Which owner acts, and what is the safe fallback?

## 15. Library map

| Tool | Primary use | Boundary |
|---|---|---|
| Pandera | dataframe schemas/checks across supported Python backends | backend capabilities differ; pin version |
| Great Expectations | expectation suites, validation definitions/results, data docs | expectations still need domain ownership |
| TensorFlow Data Validation | statistics, schema anomalies, drift/skew in TFX workflows | inferred schema needs review |
| Deequ | scalable data-quality constraints on Spark | not an ML leakage detector by itself |
| Feast | feature definitions, historical retrieval, point-in-time joins, online serving | feature store does not invent correct semantics |
| Evidently/whylogs | profiles and monitoring/drift workflows | distance alert is not root-cause proof |
| custom SQL/Python | domain invariants and reconciliation | needs tests, versioning, and evidence storage |

Select tooling by execution engine, volume, contract/version workflow, streaming/batch needs, evidence retention, and integration—not popularity.

## 16. Minimal point-in-time retrieval

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class FeatureEvent:
    entity_id: str
    event_time: int
    available_time: int
    value: float


def latest_available_value(
    events: Iterable[FeatureEvent],
    *,
    entity_id: str,
    prediction_time: int,
) -> float | None:
    """Return the latest event that was actually available by prediction time."""
    eligible = [
        event
        for event in events
        if event.entity_id == entity_id
        and event.available_time <= prediction_time
        and event.event_time <= prediction_time
    ]
    if not eligible:
        return None
    return max(eligible, key=lambda event: (event.event_time, event.available_time)).value


events = [
    FeatureEvent("A", event_time=10, available_time=11, value=2.0),
    FeatureEvent("A", event_time=12, available_time=20, value=99.0),  # late
    FeatureEvent("A", event_time=14, available_time=14, value=3.0),
]
assert latest_available_value(events, entity_id="A", prediction_time=15) == 3.0
assert latest_available_value(events, entity_id="A", prediction_time=10) is None
```

Production joins also need window boundaries, deduplication, corrections, TTL, source priority, and deterministic tie-breaking.

## 17. Rapid interview questions

**Why split before preprocessing?** Learned preprocessing otherwise uses validation/test information and makes evaluation optimistic.

**What is point-in-time correctness?** Reconstructing features using only values that would have been available at each historical prediction time.

**Why is target encoding risky?** Category outcome means can directly include the current row or future validation outcomes. Use out-of-fold, smoothed, time-safe computation.

**Should trees use unscaled data?** Trees usually do not need standardization for split ordering, but still need correct types, units, missingness, ranges, and consistent train/serve logic.

**How do you handle unseen categories?** Define an explicit unknown path or hashing strategy and test it in training and serving.

**What is training-serving skew?** Offline and online feature schemas, values, transforms, defaults, precision, or freshness differ for equivalent entity/timestamp requests.

**Does drift mean retrain?** No. First identify pipeline errors, sampling changes, seasonality, population shifts, and whether model quality changed.

**How do you validate labels?** Document source/time/window/revisions, audit a sample, measure prevalence/slices/agreement, and distinguish unlabeled or censored cases from negatives.

**When is a feature store useful?** When shared definitions, point-in-time historical retrieval, online access, freshness, lineage, and reuse justify its operational cost.

**How would you reduce a large feature set?** Leakage audit, stability and redundancy analysis, fold-safe embedded/filter methods, ablation, cost/latency review, and slice-level validation.

## 18. Lead-level case

**Prompt:** Build a fraud-risk model using transaction, customer, device, and investigation data.

Cover:

1. prediction at authorization time, transaction entity, fraud confirmation window, and decision/action;
2. label delay, chargeback revisions, false reports, censored recent transactions, and adjudication;
3. immutable source snapshots and privacy/retention classification;
4. time-based split with customer/device grouping and a gap matching outcome delay;
5. point-in-time joins using processed availability, not only event time;
6. transaction amount/currency, velocity windows, device/account novelty, merchant history, and network signals;
7. unknown/missing semantics, currency/unit normalization, duplicate attempts, and identifier rotation;
8. class-weight/threshold baseline before synthetic resampling;
9. schema, domain, referential, temporal, label, split, parity, and slice validation gates;
10. offline–online matched-value tests and fallback when an online feature is stale;
11. PR-AUC plus calibrated cost/capacity metrics and customer-friction/fairness guardrails;
12. monitoring for upstream failures, fraud adaptation, label delay, calibration, and decision outcomes.

## 19. Final checklist

- [ ] I can define prediction grain, prediction time, horizon, label window, and action.
- [ ] I can select random, stratified, group, temporal, geographic, or nested splits based on deployment.
- [ ] I can identify target, future, preprocessing, entity, duplicate, aggregate, and serving leakage.
- [ ] I can compare numeric/categorical transformations and unknown-category behavior.
- [ ] I can explain missingness and label uncertainty without treating all absence as zero/negative.
- [ ] I can design point-in-time features with event and availability timestamps.
- [ ] I can define feature contracts, ownership, freshness, defaults, and versions.
- [ ] I can validate schema, content, relationships, domain, temporal, labels, splits, transforms, parity, and slices.
- [ ] I can distinguish drift, skew, seasonality, sampling change, and concept change.
- [ ] I can connect validation failures to quarantine, release blocking, safe fallback, and accountable action.

## 20. Primary references

- TensorFlow, [TensorFlow Data Validation](https://www.tensorflow.org/tfx/guide/tfdv)
- Feast, [Point-in-time joins](https://docs.feast.dev/master/getting-started/concepts/point-in-time-joins)
- Pandera, [official documentation](https://pandera.readthedocs.io/en/stable/)
- Great Expectations, [Run Validations](https://docs.greatexpectations.io/docs/core/run_validations/)
- scikit-learn, [Common pitfalls and recommended practices](https://scikit-learn.org/stable/common_pitfalls.html)
- scikit-learn, [Preprocessing and pipelines](https://scikit-learn.org/stable/modules/compose.html)

Library APIs and supported backends change. Verify the pinned version and test the exact production data path.
