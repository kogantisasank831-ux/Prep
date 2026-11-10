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
title: "Data preparation, EDA, and feature engineering interview cheat sheet"
description: "Prediction grain, labels, splits, leakage, data quality, missingness, outliers, scaling, encoding, temporal and aggregate features, imbalance, point-in-time correctness, and monitoring."
summary: "Revise how decision time, identity, lineage, reproducible transformations, and point-in-time evidence turn raw data into reliable model inputs."
permalink: "/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 7 · Data and feature foundations"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 7 source:** This review candidate integrates the newly prepared revision source into the Prep site. It is separate from the Week 1–20 learning assessments.

**Target roles:** Data Scientist, ML Engineer, AI Engineer, Analytics Engineer, AI/Data Science Lead  
**Use:** data-quality, exploratory-analysis, modeling, feature-platform, and production-ML rounds  
**Interview rule:** define the prediction unit, decision time, label horizon, and data-availability contract before cleaning or engineering features. Most serious feature bugs are time, identity, or lineage bugs.

## 1. Thirty-second revision

- Define one row: entity, event, timestamp, observation window, prediction time, label horizon, and action.
- Split before learning imputation, scaling, encoding, feature selection, or resampling. Fit preprocessing on training data only.
- Leakage is information unavailable at decision time or information created by the outcome, future, or split construction.
- EDA should test data-generating and measurement assumptions, not merely render charts.
- Validate schema, keys, units, ranges, categories, freshness, missingness, duplicates, lineage, and changes by important slice.
- Missingness can be informative, but a missingness indicator is not a substitute for understanding its mechanism.
- Scaling matters for distance, gradient, and regularization-sensitive models; trees usually do not need it.
- Encode categories with an explicit unseen-value policy. Target encoding must be out-of-fold and time-aware.
- Temporal, aggregate, and rolling features require point-in-time joins and event-time cutoffs.
- Handle imbalance with decision-aware metrics, thresholds, weighting or resampling inside training folds—not by duplicating data before splitting.
- Put transformations in one reproducible pipeline used by training and serving; version code, data, schema, and feature definitions.
- Monitor feature availability, freshness, distribution, nulls, categories, lineage, and online/offline parity—not only model scores.

## 2. Prediction and data contract

Before opening a notebook, write:

| Field | Example question |
|---|---|
| Unit | one customer, machine-hour, document, order, or event? |
| Key | which stable identifier prevents duplicates and bad joins? |
| Decision time | when must the prediction be available? |
| Observation window | which history may features use? |
| Label horizon | what future interval defines the outcome? |
| Action | what changes because of the score? |
| Availability | which sources exist, with what delay, at decision time? |
| Population | which entities are eligible and which are excluded? |
| Cost | consequences of false positive, false negative, abstention, delay |

Example: “At 08:00 each day, score each operating pump using telemetry available through 07:55 to predict failure in the next seven days, enabling inspection under a daily capacity limit.”

This makes future maintenance records, post-failure fields, and late laboratory readings visibly unavailable.

## 3. Grain, keys, joins, and duplicates

State the grain of every table. A one-to-many join can multiply rows and silently change weights, totals, class balance, and train/test independence.

For each join, validate:

- key uniqueness on the expected side;
- null keys and fallback behavior;
- row counts before/after;
- unmatched rates by source and slice;
- time validity and slowly changing dimensions;
- duplicate precedence;
- units and timezone;
- late-arriving corrections.

Duplicates may be exact ingestion retries, repeated legitimate events, conflicting records, or multiple measurements. Deduplicate only after defining identity and precedence. “Drop duplicates” is not a business rule.

## 4. Labels and target audit

Audit label definition, source, timing, noise, missingness, adjudication, and feedback loops.

Ask:

- Is the label observable for every eligible unit?
- Is it delayed or censored?
- Does intervention prevent the outcome, creating selective labels?
- Was it created using a model or policy being evaluated?
- Does a proxy match the decision objective?
- Can positive and negative labels be confirmed?
- Are label definitions stable across time, sites, or annotators?

For document or LLM tasks, record annotation instructions, rubric, examples, adjudication, agreement, model assistance, and dataset license/provenance. Weak labels can scale coverage but need an audited high-quality evaluation set.

## 5. Split strategy

Choose splits from deployment:

- **random stratified:** approximately IID units, no grouped dependency;
- **group split:** people, devices, accounts, documents, patients, or sites must not cross splits;
- **time split/backtest:** future prediction, changing behavior, or temporal availability;
- **geographic/domain holdout:** generalization to new regions, clients, or environments;
- **nested cross-validation:** unbiased model-selection assessment when data is limited;
- **rolling/expanding windows:** repeated time-based evaluation under retraining plans.

Keep a final test set untouched by feature and hyperparameter decisions. Validation must reproduce feature availability and label maturation. Random splitting a repeated entity often measures memorization of identity rather than future generalization.

## 6. Leakage taxonomy

### Target leakage

A feature directly or indirectly encodes the outcome: closure reason, post-diagnosis treatment, final invoice, or human resolution note.

### Temporal leakage

Feature value was produced after prediction time, even if stored in a table with an earlier business date.

### Split leakage

Same entity, near-duplicate document, augmented example, or future-derived statistic crosses train and validation.

### Preprocessing leakage

Imputer, scaler, encoder, feature selector, resampler, or vocabulary is fit before the split.

### Evaluation leakage

Test results repeatedly guide model choices, prompts, thresholds, or data cleanup.

### Feedback leakage

Labels or features reflect decisions made by an earlier model, so observed outcomes are policy-dependent.

Use a feature-availability table with source event, produced-at time, available-at time, decision cutoff, and lineage. Column names alone cannot prove safety.

## 7. EDA as hypothesis testing

Good EDA answers questions:

- What is the actual unit and population?
- Are keys unique and time ordered?
- How do missingness and labels vary by time, source, geography, device, tenant, or cohort?
- Are ranges, units, categories, and relationships plausible?
- Is the target prevalence stable and measurable?
- Are train/validation periods or groups materially different?
- Which anomalies are data errors versus real rare cases?
- Where can leakage or selection enter?

Use distributions, quantiles, counts, scatter/hexbin plots, correlations with caveats, time plots, missingness matrices, and slice tables. Report denominators and uncertainty. A correlation heatmap alone is not EDA.

## 8. Schema and quality checks

Quality dimensions include:

- **validity:** type, range, allowed category, format;
- **completeness:** required fields and missingness;
- **uniqueness:** primary/business keys;
- **consistency:** cross-field, cross-table, and unit rules;
- **timeliness:** freshness and event/ingestion delay;
- **accuracy:** agreement with an authoritative source where available;
- **lineage:** source, transformations, owner, version, and retention.

Use blocking gates for violations that make results invalid; quarantine bounded bad records when policy allows; alert on distributional changes; and define recovery/backfill. Thresholds need a baseline and owner, not arbitrary round numbers.

## 9. Missing data

Missingness mechanisms:

- **MCAR:** independent of observed and unobserved values;
- **MAR:** explained by observed variables;
- **MNAR:** depends on the missing value or unobserved causes.

These are assumptions, not labels a library discovers. Investigate collection workflow, outages, eligibility, and policy.

Options:

- drop only with a defensible missingness and population argument;
- simple median/mode imputation as a strong baseline;
- model-based or multiple imputation when uncertainty and assumptions justify it;
- missing indicator when absence itself may carry signal;
- native missing-value handling in supported models;
- explicit “unknown” category distinct from “not applicable.”

Fit imputation inside training folds. Validate missingness shift and serving fallback. Do not impute identifiers or labels casually.

## 10. Outliers, transformations, and units

An outlier may be error, rare valid case, regime change, fraud, or the most important event. Trace source and business context before removal.

Options include:

- correct unit or parsing errors;
- cap/winsorize using training-derived, justified limits;
- log or power transform positive skew;
- robust scaling by median and interquartile range;
- use robust losses or tree models;
- model regimes separately;
- retain and add an anomaly/quality flag.

Ensure physical units are consistent. A model trained on Celsius and served Fahrenheit values can pass type checks and fail catastrophically.

## 11. Scaling and normalization

- **Standardization:** $(x-\mu)/\sigma$; common for linear models, neural nets, PCA, SVMs, and k-means.
- **Min-max scaling:** maps training range to a bounded interval but is sensitive to extremes and future values can fall outside it.
- **Robust scaling:** median and IQR; useful with heavy tails.
- **Vector normalization:** makes each sample unit norm; common for cosine geometry.

Scaling affects regularization because penalties operate on coefficient magnitudes. Fit statistics only on training data and preserve them with the model. Trees split by order and generally do not need scaling, though downstream distances or mixed pipelines may.

## 12. Categorical encoding

| Method | Use | Risk |
|---|---|---|
| one-hot | low/moderate cardinality, linear or simple models | wide sparse matrix, unseen categories |
| ordinal | genuinely ordered categories | false order if used for nominal values |
| hashing | bounded width and streaming/unseen values | collisions, harder interpretation |
| frequency/count | stable frequency signal | drift and population leakage |
| target encoding | high-cardinality predictive categories | severe target leakage/overfit |
| learned embedding | large data and complex interactions | training/serving complexity, rare values |

Target encoding must use out-of-fold values for training rows and only past data for time problems. Apply smoothing and a global fallback. Treat unseen, rare, missing, and retired categories explicitly.

## 13. Temporal features

Examples:

- calendar: hour, weekday, holiday, fiscal period;
- cyclical encoding: sine/cosine for known periodicity;
- recency: time since last event;
- frequency: events in trailing windows;
- trend: slope/change over past intervals;
- lag: prior observed values;
- rolling statistics: count, mean, max, volatility;
- lifecycle: tenure or time since activation.

Every window needs an event-time cutoff, inclusion rule, late-data policy, timezone, and minimum history. Centered rolling windows and globally computed aggregates leak future data. Backtests must rebuild features as they would have existed at each prediction time.

## 14. Text, image, geographic, and domain features

For text, start with length, language, metadata, and TF-IDF baselines before embeddings. Prevent near-duplicate documents across splits and fit vocabulary/IDF on training data.

For images/audio, validate acquisition device, compression, orientation, sampling rate, artifacts, augmentation, and subject/group splits. Metadata can leak the target.

For geography, use appropriate coordinate systems, distances, regions, and privacy controls. Latitude/longitude Euclidean distance is unreliable over large areas; use geodesic methods or local projections.

Domain features should encode mechanisms or constraints, not post-outcome knowledge. Document definition, units, availability, and owner.

## 15. Aggregates, interactions, and relational features

Aggregates often carry strong signal: spend in prior 30 days, failure count by asset, supplier delay rate, or graph degree. They also create common leakage.

For each aggregate specify:

- entity key and relationship;
- event-time window and cutoff;
- allowed records and outcome exclusion;
- minimum support and smoothing;
- update frequency and late corrections;
- offline/online computation;
- privacy and group-size constraints.

Interactions allow non-additive effects, such as price × segment. Linear models may need explicit interactions; trees and neural networks can learn many automatically but still benefit from meaningful ratios or invariants. Avoid combinatorial feature generation without validation and capacity controls.

## 16. Feature selection

Reasons include generalization, stability, latency, cost, interpretability, privacy, and maintainability.

- **Filter:** variance, univariate score, mutual information; fast but ignores joint behavior.
- **Wrapper:** recursive elimination or forward selection; expensive and selection-biased without nested validation.
- **Embedded:** L1, trees, regularized models; importance is model-dependent.
- **Domain/operational:** remove unavailable, expensive, unstable, redundant, sensitive, or unactionable features.

Run selection inside training folds. Permutation importance needs a valid holdout and can dilute importance among correlated features. SHAP values explain the fitted model under its assumptions; they do not prove causality.

## 17. Class imbalance and sampling

Accuracy can be useless under imbalance. Select metrics from costs and capacity: precision/recall, PR-AUC, recall at alert budget, cost-weighted utility, calibration, or expected value.

Options:

- class/sample weights;
- over/under-sampling inside training folds;
- focal loss for suitable hard-example settings;
- anomaly or ranking formulation;
- threshold optimization on validation data;
- targeted label acquisition.

Preserve real prevalence for calibration and final evaluation. Synthetic sampling such as SMOTE can help some tabular problems but may create implausible examples or cross group/time boundaries. Compare with simpler weighting and threshold baselines.

## 18. Reproducible preprocessing pipeline

```python
from __future__ import annotations

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


numeric = Pipeline(
    steps=[
        ("impute", SimpleImputer(strategy="median", add_indicator=True)),
        ("scale", StandardScaler()),
    ]
)
categorical = Pipeline(
    steps=[
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("encode", OneHotEncoder(handle_unknown="ignore")),
    ]
)
preprocess = ColumnTransformer(
    transformers=[("num", numeric, ["age", "balance"]), ("cat", categorical, ["region"])]
)
model = Pipeline(
    steps=[("preprocess", preprocess), ("model", LogisticRegression(max_iter=1_000))]
)
```

Split first; then fit the complete pipeline on training data. Cross-validation should refit every learned step in each fold. Serialize or rebuild from a versioned definition, and validate exact schema plus a representative prediction fixture.

## 19. Point-in-time features and feature stores

A feature value is correct only if it was available at the prediction timestamp. Store or reconstruct:

- entity key;
- feature event time;
- produced/ingested time;
- feature definition/version;
- source lineage;
- TTL/freshness;
- correction and deletion semantics.

Offline training and online serving need semantic parity, not necessarily identical storage. Use point-in-time joins for training, materialize online values with freshness metadata, and reconcile sampled offline/online results. A feature store can standardize this contract; it cannot infer correct event time or business meaning.

## 20. Drift, parity, and feature monitoring

Monitor:

- schema and category changes;
- missingness and default/fallback rate;
- freshness and age at prediction;
- distribution and range by meaningful slice;
- online/offline value parity;
- feature/model version compatibility;
- source lineage and failed jobs;
- relationship to prediction and delayed outcome;
- compute, storage, latency, and serving cost.

Population Stability Index or statistical distances are signals, not universal alarms. Large benign seasonality and small high-impact shifts are both possible. Tie thresholds to baselines, consequences, and response playbooks.

## 21. Weak supervision and active learning

Weak supervision combines noisy labeling rules, heuristics, distant supervision, or model outputs. Keep labeling-function coverage, conflict, correlation, provenance, and version. Validate against independently adjudicated gold data.

Active learning selects examples whose labels may be valuable—uncertain, diverse, representative, or high-impact cases. Correct for selection bias in evaluation and maintain random samples. Human-label capacity, adjudication, privacy, and turnaround are part of the system.

Never evaluate only on examples selected because the current model found them difficult.

## 22. Common interview failure modes

- cleaning before defining row grain and decision time;
- random splitting repeated users or future records;
- fitting scalers or encoders on all data;
- deleting outliers because a boxplot marked them;
- treating missing as zero without meaning;
- using ordinal integers for nominal categories;
- target encoding without out-of-fold/time-aware computation;
- calculating rolling features with centered or future windows;
- oversampling before the split;
- selecting features on the test set;
- assuming feature-store adoption guarantees point-in-time correctness;
- monitoring global distributions while critical slices fail.

## 23. Rapid interview Q&A

**What is the first leakage question?**  
Could this exact value have been known, in this form, at the real decision time?

**Why split before preprocessing?**  
Learned statistics otherwise transfer validation or future information into training.

**When do trees need scaling?**  
Usually not for their splits, but a surrounding distance, regularization, or mixed-model pipeline may.

**Why can a missing indicator help?**  
Collection behavior or eligibility may carry information, though it can also drift when operations change.

**What is online/offline skew?**  
Training and serving compute different values because definitions, sources, timing, defaults, or versions differ.

## 24. Lead-level case

**Case:** a churn model has excellent random-split AUC but fails after launch.

A strong answer should:

1. reconstruct the real scoring time, action, observation window, label horizon, and entity population;
2. test whether users, future transactions, cancellation fields, support notes, or globally fitted transforms crossed the split boundary;
3. rebuild a time- and entity-aware backtest with point-in-time features and matured labels;
4. compare against a simple baseline and evaluate calibration, lift at contact capacity, cost, and slices;
5. verify feature freshness and online/offline parity, then canary with an action holdout;
6. add availability contracts, join/cardinality tests, leakage review, and delayed-outcome monitoring.

## 25. Final checklist

- Can you define grain, key, decision time, observation window, and label horizon?
- Can you choose random, group, time, geo, or nested splits from deployment?
- Can you identify target, temporal, split, preprocessing, evaluation, and feedback leakage?
- Can you audit labels, joins, missingness, duplicates, units, and outliers?
- Can you choose scaling and encoding with unseen-value behavior?
- Can you build point-in-time temporal and aggregate features?
- Can you handle imbalance without corrupting prevalence or validation?
- Can you put all learned transformations inside a reproducible pipeline?
- Can you explain feature-store value without outsourcing semantics to the platform?
- Can you monitor feature quality, freshness, parity, drift, and cost with an owner?

## Primary references

- scikit-learn documentation: common pitfalls, pipelines, preprocessing, model selection, and inspection.
- Google, *Rules of Machine Learning*, especially training-serving skew and pipeline guidance.
- Sculley et al., “Hidden Technical Debt in Machine Learning Systems.”
- Pandera, Great Expectations, or equivalent official documentation for executable data contracts.
- Feature-store official documentation for point-in-time joins and online/offline materialization semantics.
