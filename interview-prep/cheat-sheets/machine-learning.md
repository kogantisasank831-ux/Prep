---
layout: "week"
status: "approved"
version: "1.0.1"
last_reviewed: "2026-11-13"
header_context: "Interview cheat sheets"
back_label: "Cheat sheets"
back_url: "/cheat-sheets/"
toc_heading: "Cheat-sheet sections"
pagination_label: "Cheat sheets hub"
pagination_url: "/cheat-sheets/"
title: "Machine-learning fundamentals interview cheat sheet"
description: "End-to-end machine-learning revision for AI Engineer, ML Engineer, and senior Data Science interviews."
summary: "Revise framing, leakage, algorithms, metrics, validation, calibration, debugging, deployment, monitoring, and lead-level trade-offs."
permalink: "/interview-prep/cheat-sheets/machine-learning/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 1 · Machine learning"
current_label: "Revision guide"
alternate_label: "Cheat sheets hub"
alternate_url: "/cheat-sheets/"
---
> **Batch 1 source:** This page integrates the previously prepared revision artifact into the Prep site. It is separate from the Week 1–30 learning assessments.

**Target roles:** AI Engineer, ML Engineer, Senior/Lead Data Scientist  
**Goal:** select, train, evaluate, debug, deploy, and explain a model under real business constraints.

## 1. Thirty-second revision

- Start from the decision and baseline—not the algorithm.
- Define prediction unit, target, observation time, prediction horizon, and action.
- Split data before learning preprocessing; time/entity-aware splits prevent leakage.
- Bias is systematic underfitting; variance is sensitivity/overfitting.
- Optimize the metric that represents business cost, but monitor guardrails and subgroups.
- ROC-AUC can look good on rare positives; inspect PR-AUC, thresholds, and calibration.
- Cross-validation estimates generalization only if folds reproduce deployment conditions.
- Production success needs monitoring, rollback, data quality, and retraining—not just a model file.

## 2. End-to-end ML framing

Before modeling, answer:

1. **User/decision:** who uses the prediction and what action follows?
2. **Unit:** one row represents what—customer, order, machine, document, or event?
3. **Observation time:** what information is available when prediction is made?
4. **Target:** exactly how is the label defined?
5. **Horizon:** what future period is being predicted?
6. **Latency/frequency:** batch daily, streaming, or online milliseconds?
7. **Costs:** false positive, false negative, delay, review, infrastructure.
8. **Baseline:** rule, historical average, current process, or simple linear/tree model.
9. **Success:** offline metric, business outcome, operational and safety guardrails.
10. **Feedback:** when and how do labels arrive; can model actions alter labels?

### Example: churn

- Unit: active customer on weekly snapshot date.
- Features: information available through snapshot time.
- Target: no paid activity during the following 30 days.
- Action: retention offer or human outreach.
- Constraint: outreach capacity and offer cost.
- Primary model metric: perhaps precision/recall at the contact budget, not generic accuracy.

## 3. Data splitting and leakage

### Split strategies

| Data situation | Appropriate split |
|---|---|
| Independent, stable rows | Random train/validation/test |
| Imbalanced classes | Stratified split |
| Multiple rows per user/machine | Group split |
| Future deployment | Chronological/rolling split |
| Hyperparameter selection plus final estimate | Nested CV or untouched final test set |

### Leakage types

| Leakage | Example | Prevention |
|---|---|---|
| Target leakage | Feature contains outcome or post-outcome action | Define observation cutoff and review causality/time |
| Future leakage | December feature predicts November target | Point-in-time joins and chronological validation |
| Entity leakage | Same customer appears in train and validation | Group-aware splitting |
| Preprocessing leakage | Scaler/imputer fit on all data | Fit inside pipeline on each training fold |
| Duplicate leakage | Near-identical records cross folds | Deduplicate/group before split |
| Selection leakage | Test set repeatedly guides changes | Preserve a final untouched test set |

If an offline score is surprisingly high, investigate leakage before celebrating.

## 4. Data preparation and feature engineering

### Missing data

- Understand MCAR/MAR/MNAR and whether missingness is predictive.
- Numeric: median, model-based, or domain value; add indicator when justified.
- Categorical: explicit missing/unknown category or most frequent.
- Fit imputation on training data only.
- Some tree libraries handle missing values natively; still validate behavior.

### Scaling

| Method | Formula/behavior | Useful for |
|---|---|---|
| Standardization | $(x-\mu)/\sigma$ | Linear/logistic regression, SVM, PCA, neural nets |
| Min-max | Maps to fixed range | Bounded-input needs; sensitive to extremes |
| Robust scaling | Median/IQR | Heavy outliers |
| Log transform | Compresses right tail | Positive skewed features |

Tree splits usually do not require monotonic feature scaling.

### Categorical encoding

- One-hot: low/moderate cardinality; handle unseen categories.
- Ordinal: only when order is meaningful or model interprets codes appropriately.
- Frequency/count: compact but loses category identity.
- Target encoding: powerful for high cardinality; must be out-of-fold/smoothed to prevent leakage.
- Learned embeddings: useful with large data and neural architectures.

### Feature principles

- Prefer features available, stable, and explainable at inference time.
- Use domain aggregates with explicit windows: last 7/30/90 days.
- Add interactions when model cannot learn them easily.
- Avoid identifiers unless they represent stable, generalizable information.
- Validate feature freshness, cost, privacy, and training-serving parity.

## 5. Bias, variance, and learning curves

Expected prediction error can be viewed conceptually as:

$$
\text{Error}=\text{Bias}^2+\text{Variance}+\text{Irreducible noise}
$$

| Pattern | Training score | Validation score | Likely action |
|---|---|---|---|
| Underfitting/high bias | Poor | Poor and similar | Better features/model, less regularization |
| Overfitting/high variance | Very good | Much worse | More data, regularization, simpler model, robust CV |
| Data/label noise | Limited ceiling | Limited | Improve data/labels; uncertainty handling |

Learning curves help distinguish whether more data is likely to help.

## 6. Regularization

### L2 / Ridge

$$
\min_\beta \sum_i (y_i-x_i^T\beta)^2+\lambda\sum_j\beta_j^2
$$

- Shrinks coefficients smoothly; rarely makes them exactly zero.
- Stabilizes correlated/noisy features.
- Scaling matters because the penalty depends on coefficient magnitude.

### L1 / Lasso

$$
\min_\beta \sum_i (y_i-x_i^T\beta)^2+\lambda\sum_j|\beta_j|
$$

- Can produce exact zero coefficients and implicit feature selection.
- With strongly correlated variables, selection may be unstable.

### Elastic Net

Combines L1 and L2; useful for sparse solutions with groups of correlated features.

## 7. Algorithm comparison

| Algorithm | Strengths | Weaknesses / assumptions | Common uses |
|---|---|---|---|
| Linear regression | Fast, interpretable, calibrated continuous baseline | Linear/additive form; sensitive to specification/outliers | Forecast components, pricing, interpretable regression |
| Logistic regression | Strong probability baseline, interpretable, scalable | Linear log-odds boundary unless features added | Churn, risk, propensity |
| k-nearest neighbors | Simple, nonlinear, no parametric fit | Slow inference, scaling-sensitive, curse of dimensionality | Small/local-pattern datasets |
| Naive Bayes | Very fast; works well on sparse text | Strong conditional-independence assumption | Text/document classification baseline |
| Decision tree | Nonlinear, interactions, easy to explain | High variance and unstable | Rules, interpretable segmentation |
| Random forest | Robust bagging, nonlinear, little preprocessing | Larger/slower; probabilities may need calibration | Strong general tabular baseline |
| Gradient-boosted trees | Excellent tabular performance | Tuning, leakage/overfit risk, less transparent | Most structured-data tasks |
| SVM | Effective margins and kernels | Scaling required; expensive at large `n`; probability not native | Medium-size high-dimensional data |

Always benchmark against a simple baseline. The best model is the one meeting quality, latency, cost, interpretability, and operational constraints.

## 8. Linear regression

Model:

$$
y=X\beta+\epsilon
$$

Ordinary least squares minimizes:

$$
\sum_i(y_i-\hat y_i)^2
$$

For unbiased coefficient inference under the standard linear model, discuss:

- correct linear/additive specification;
- exogeneity: $E[\epsilon\mid X]=0$;
- independent errors as appropriate to design;
- no perfect multicollinearity;
- homoscedasticity for usual standard-error formula;
- approximately normal errors mainly for small-sample inference, not prediction itself.

Important diagnostics: residual plots, heteroscedasticity, influential points, multicollinearity, nonlinear patterns, and train/validation error.

### $R^2$

$$
R^2=1-\frac{\sum(y_i-\hat y_i)^2}{\sum(y_i-\bar y)^2}
$$

`R²` can be negative out of sample and does not prove causal relevance or good calibration for decisions.

## 9. Logistic regression

$$
p(y=1\mid x)=\sigma(z)=\frac{1}{1+e^{-z}},\quad z=\beta_0+x^T\beta
$$

$$
\log\frac{p}{1-p}=\beta_0+x^T\beta
$$

For a one-unit increase in $x_j$, holding other variables fixed, odds multiply by $e^{\beta_j}$.

Binary cross-entropy/log loss:

$$
-\frac{1}{n}\sum_i[y_i\log p_i+(1-y_i)\log(1-p_i)]
$$

Advantages: fast, regularizable, interpretable, often well calibrated. Limitation: linear decision boundary in supplied feature space.

## 10. kNN and Naive Bayes

### kNN

- Fit stores training data; inference finds nearest points.
- Small `k`: lower bias, higher variance.
- Large `k`: smoother, higher bias.
- Scale features and choose distance carefully.
- High dimensions make distances less discriminative.

### Naive Bayes

$$
P(y\mid x_1,\ldots,x_d)\propto P(y)\prod_jP(x_j\mid y)
$$

Variants: Gaussian, multinomial, Bernoulli. Independence is usually false, yet classification can still work well—especially for sparse text.

## 11. Decision trees

A tree recursively chooses splits that improve node purity/loss.

### Gini impurity

$$
Gini=1-\sum_k p_k^2
$$

### Entropy

$$
H=-\sum_k p_k\log_2p_k
$$

### Solved impurity example

Node has 80 positives and 20 negatives:

$$
Gini=1-(0.8^2+0.2^2)=0.32
$$

A split is good if the weighted child impurity is meaningfully below 0.32.

Regularize trees with maximum depth, minimum samples per leaf/split, maximum leaves, pruning, or minimum gain.

## 12. Random forests and bagging

Bagging trains models on bootstrap samples and averages/votes. Random forests add random feature subsets at splits, reducing correlation among trees.

- Mainly reduces variance.
- Out-of-bag samples can estimate performance.
- Handles nonlinearities/interactions and mixed scales well.
- Impurity importance can favor high-cardinality/continuous features; prefer permutation or carefully interpreted SHAP for analysis.

## 13. Gradient boosting

Boosting adds weak learners sequentially to correct current errors or follow the loss gradient.

Conceptual regression process:

1. start with a constant prediction;
2. compute residuals/negative gradients;
3. fit a small tree to them;
4. add the tree multiplied by learning rate;
5. repeat with regularization and early stopping.

Important controls:

- number of trees;
- learning rate;
- tree depth/leaves;
- minimum child samples/weight;
- row/column subsampling;
- L1/L2 penalties;
- early stopping.

### XGBoost, LightGBM, CatBoost

| Library | Practical distinction |
|---|---|
| XGBoost | Mature regularized boosting and broad ecosystem |
| LightGBM | Histogram/leaf-wise growth; fast on large data but can overfit small data if unconstrained |
| CatBoost | Strong handling of categorical features using ordered/statistical strategies that reduce leakage |

The library name is less important than correct validation, leakage control, and tuning.

## 14. Support vector machines

The linear SVM seeks a separating hyperplane with maximum margin. Soft margin uses `C` to trade margin width against violations.

- Large `C`: penalize errors strongly, potentially narrower margin/more variance.
- Small `C`: stronger regularization, wider margin/more bias.
- Kernel trick enables nonlinear boundaries using implicit feature spaces.
- Scale features.
- Native SVM scores are margins; probability estimates need calibration.

## 15. Ensembles

| Method | Training relation | Main effect |
|---|---|---|
| Bagging | Models in parallel on resamples | Reduce variance |
| Boosting | Sequential error correction | Reduce bias and fit complex patterns |
| Voting/averaging | Combine predictions | Improve robustness if errors differ |
| Stacking | Meta-model combines out-of-fold predictions | Learn combination; leakage risk if not out-of-fold |

Diversity matters: averaging identical errors provides little benefit.

## 16. Classification metrics

| | Predicted positive | Predicted negative |
|---|---:|---:|
| Actual positive | TP | FN |
| Actual negative | FP | TN |

$$
Accuracy=\frac{TP+TN}{TP+FP+FN+TN}
$$

$$
Precision=\frac{TP}{TP+FP},\quad Recall=\frac{TP}{TP+FN}
$$

$$
Specificity=\frac{TN}{TN+FP}
$$

$$
F1=\frac{2\cdot Precision\cdot Recall}{Precision+Recall}
$$

### Solved example

`TP=80, FP=20, FN=40, TN=860`:

- Accuracy = `940/1000 = 94%`
- Precision = `80/100 = 80%`
- Recall = `80/120 = 66.7%`
- Specificity = `860/880 = 97.7%`
- F1 ≈ `72.7%`

High accuracy hides that one-third of positives are missed.

### ROC-AUC versus PR-AUC

- ROC curve: true-positive rate versus false-positive rate across thresholds.
- ROC-AUC: ranking probability that a random positive scores above a random negative.
- PR curve: precision versus recall; often more informative for rare positives.
- PR-AUC depends on prevalence; compare against the positive-rate baseline and across comparable datasets.

AUC does not select an operating threshold or prove probabilities are calibrated.

### Macro, micro, and weighted averaging

- Macro: equal weight per class; exposes minority-class performance.
- Micro: pool all decisions; dominated by frequent classes.
- Weighted: class metric weighted by class support.

## 17. Thresholds, costs, and calibration

Choose a threshold using business cost/capacity, not 0.5 by habit.

Expected cost at threshold $t$:

$$
Cost(t)=C_{FP}FP(t)+C_{FN}FN(t)+C_{review}N_{flagged}(t)
$$

Use precision@K/recall@K when operations can review only K cases.

### Calibration

A model is calibrated if cases predicted near 0.7 are positive about 70% of the time.

Measure with:

- reliability diagrams;
- Brier score;
- log loss;
- calibration error summaries used cautiously.

Methods: Platt/sigmoid scaling and isotonic regression, fit on separate validation/out-of-fold predictions. Class weighting/resampling and distribution shift can harm calibration.

## 18. Regression metrics

| Metric | Formula/behavior | Use/limitation |
|---|---|---|
| MAE | mean $|y-\hat y|$ | Robust relative to MSE; median-optimal |
| MSE | mean $(y-\hat y)^2$ | Strongly penalizes large errors; mean-optimal |
| RMSE | $\sqrt{MSE}$ | Original target units, still outlier-sensitive |
| $R^2$ | variance-relative fit | Can be negative out of sample |
| MAPE | mean relative absolute error | Undefined/unstable near zero; asymmetric |
| RMSLE | RMSE in log space | Relative errors; requires valid transformed domain |
| Quantile loss | asymmetric absolute loss | Prediction intervals/under-over costs |

Report subgroup and time-slice errors; a single average can hide systematic failures.

## 19. Ranking and retrieval metrics

- Precision@K: relevant items among top K.
- Recall@K: relevant items retrieved in top K.
- MRR: reciprocal rank of first relevant result, averaged.
- MAP: average precision across relevant ranks and queries.
- NDCG: discounted gain emphasizing relevant items near top, normalized by ideal ranking.

Select metric based on user behavior: first good result, all relevant results, or graded relevance.

## 20. Cross-validation

### Common strategies

- K-fold: stable independent rows.
- Stratified K-fold: preserve class proportions.
- Group K-fold: no entity appears in both train and validation.
- Time-series/rolling validation: train on past, validate on future.
- Nested CV: outer generalization estimate, inner hyperparameter tuning.

All learned preprocessing and feature selection must occur inside each training fold.

### What CV does not fix

- nonrepresentative data;
- leakage already embedded in feature creation;
- future distribution shifts absent from folds;
- a metric disconnected from business value;
- repeated test-set-driven experimentation.

## 21. Hyperparameter tuning

- Grid search: exhaustive predefined combinations; inefficient in large spaces.
- Random search: often stronger coverage when only a few parameters matter.
- Bayesian optimization: model promising regions; useful when trials are expensive.
- Successive halving/Hyperband: stop poor configurations early.
- Early stopping: monitor validation metric while training.

Do not tune on the final test set. Track experiment configuration, seed, data version, code, metrics, and artifacts.

## 22. Class imbalance

Options:

- use appropriate metrics and threshold;
- class weights/cost-sensitive loss;
- undersampling/oversampling;
- synthetic sampling such as SMOTE, applied within training folds only;
- anomaly/ranking framing for extreme rarity;
- collect better labels or use active review.

Do not balance the test set if production prevalence matters. Evaluate on realistic prevalence and recalibrate if training distribution was altered.

## 23. Feature selection

| Type | Examples | Risk |
|---|---|---|
| Filter | variance, correlation, mutual information | Ignores model interactions |
| Wrapper | recursive feature elimination | Expensive; overfit if CV incorrect |
| Embedded | L1, tree selection | Model-specific and potentially unstable |
| Domain | availability, cost, privacy, causality | Requires expert review but often highest value |

Feature selection must be fit inside training folds. Importance is not the same as causal effect.

## 24. Interpretability

- Coefficients: direction/magnitude under scaling and model assumptions.
- Tree rules: local path; entire large ensemble is not simple.
- Permutation importance: performance drop after shuffling; correlated features can mask each other.
- Partial dependence: average prediction as feature varies; unreliable in sparse/correlated regions.
- ICE: individual curves reveal heterogeneity.
- SHAP: additive local attribution under a background/conditionality definition; not causal proof.
- LIME: local surrogate; can be unstable to sampling/settings.

Validate explanations for stability and communicate that they describe model behavior, not necessarily the real-world causal process.

## 25. Unsupervised fundamentals

### k-means

Minimizes within-cluster squared Euclidean distance to centroids.

- Scale features.
- Assumes roughly spherical, similarly sized clusters under Euclidean geometry.
- Use multiple initializations.
- Choose K using domain value plus diagnostics such as elbow/silhouette—not one metric alone.

### PCA

Finds orthogonal directions of maximum variance.

- Center features; usually scale if units differ.
- Useful for compression, visualization and collinearity reduction.
- Components are linear and may be hard to interpret.
- Fit PCA only on training data.

### Density/anomaly awareness

- DBSCAN/HDBSCAN: density-based clusters and noise; sensitive to distance/scale.
- Isolation Forest: anomalies are isolated with fewer random splits.
- One-class SVM: boundary around normal data; scale/tune carefully.

## 26. Production-ready scikit-learn pattern

```python
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

numeric_features = ["age", "monthly_spend"]
categorical_features = ["country", "plan"]

numeric_pipeline = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ]
)

categorical_pipeline = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        ("numeric", numeric_pipeline, numeric_features),
        ("categorical", categorical_pipeline, categorical_features),
    ]
)

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", LogisticRegression(max_iter=1_000)),
    ]
)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_validate(
    pipeline,
    X,
    y,
    cv=cv,
    scoring={"roc_auc": "roc_auc", "average_precision": "average_precision"},
    return_train_score=True,
)
```

For repeated customers or time-dependent data, replace stratified random CV with group/time-aware validation.

## 27. Model debugging sequence

1. Verify target definition and label timing.
2. Compare against trivial and business baselines.
3. Inspect duplicates, train/validation overlap, leakage, and split logic.
4. Overfit a tiny sample to confirm pipeline can learn.
5. Check feature distributions, missingness, units, and preprocessing.
6. Review learning curves and train/validation gap.
7. Segment errors by time, geography, entity, class and data source.
8. Check threshold, calibration and cost matrix.
9. Audit label quality on false positives/negatives.
10. Run ablations; remove suspicious features and compare.
11. Confirm offline/online feature parity.

## 28. Production monitoring

### Layers

| Layer | Examples |
|---|---|
| Service | latency p50/p95/p99, throughput, errors, saturation |
| Data | schema, missingness, ranges, categories, freshness |
| Drift | feature/score/label/prevalence changes |
| Model | delayed accuracy, precision/recall, calibration, subgroup metrics |
| Business | revenue, churn reduction, review workload, user outcome |
| Fairness/safety | disparity, harmful errors, policy violations |

Drift is a diagnostic signal, not automatic proof of performance loss. Retraining should have explicit triggers, validation gates, rollout, and rollback.

## 29. Common traps

| Trap | Better answer |
|---|---|
| Optimize accuracy on 1% positive data | Use PR/recall/precision/cost and realistic threshold |
| Fit scaler before CV | Put preprocessing in pipeline inside folds |
| Random split on future prediction | Use chronological/rolling split |
| Same user in train and validation | Group split |
| Tune on test set | Tune on validation/inner CV; test once for final estimate |
| Use feature importance as causal impact | Importance describes model reliance, not intervention effect |
| Select threshold 0.5 | Optimize expected cost/capacity and validate calibration |
| Oversample before split | Resample training fold only |
| Claim AUC means “85% accuracy” | AUC is threshold-free ranking performance |
| Deploy model alone | Ship preprocessing, schema, versions, monitoring and rollback |

## 30. Rapid interview questions and answers

1. **Bias versus variance?** Bias is systematic error from restrictive assumptions; variance is sensitivity to training samples. Complexity often lowers bias and raises variance.
2. **Why regularize?** Reduce variance/unstable coefficients by penalizing complexity, improving generalization.
3. **L1 versus L2?** L1 can make coefficients exactly zero; L2 smoothly shrinks them and handles correlated features more stably.
4. **Bagging versus boosting?** Bagging fits models largely in parallel to reduce variance; boosting fits sequential corrections to reduce bias and build complexity.
5. **Why can ROC-AUC mislead?** With extreme imbalance, a small FPR can still produce many false positives; PR and operational thresholds expose this.
6. **What is calibration?** Agreement between predicted probabilities and empirical frequencies.
7. **Why does scaling matter for kNN/SVM but little for trees?** Distance/margin objectives depend on magnitude; tree ordering/split thresholds are invariant to monotonic scaling.
8. **How do you detect leakage?** Review timing/availability, group overlap, suspicious features, near-duplicates, unexpectedly high scores, and performance after removing suspect variables.
9. **Why use nested CV?** Inner folds tune hyperparameters; outer folds estimate performance without tuning optimism.
10. **What if offline improves but business KPI does not?** Metric may not represent decision value, action may be ineffective, threshold/workflow/adoption may be wrong, or experiment/instrumentation may fail.
11. **Random forest versus gradient boosting?** Random forest is robust bagging and easier to tune; boosting often wins tabular accuracy but needs careful regularization/validation.
12. **What is concept drift?** The relationship $P(y\mid x)$ changes; data drift only means input distribution $P(x)$ changed.

## 31. Lead-level case

**Question:** Build a churn system for 10 million customers when the retention team can contact only 100,000 customers weekly.

**Strong answer structure:**

1. Define churn, eligible population, weekly snapshot, observation window, 30/60-day horizon, and intervention.
2. Establish current rule/business baseline and measure incremental value of contact.
3. Build point-in-time features and use chronological plus customer-group-aware validation.
4. Begin with logistic regression and gradient-boosted trees; compare accuracy, calibration, latency, interpretability and maintenance.
5. Evaluate precision@100k, recall@100k, expected profit, calibration, subgroup stability and time-based backtests.
6. Separate churn propensity from treatment effect: high-risk customers may not be persuadable. If possible, run randomized outreach and model uplift.
7. Select customers under budget, channel, eligibility and fairness constraints.
8. Batch-score with versioned features/model; publish an auditable ranked list.
9. Run a controlled experiment measuring incremental retained value minus contact/offer cost.
10. Monitor data freshness, score distribution, calibration, contact capacity, outcome delay and subgroup performance.
11. Use canary rollout, champion/challenger evaluation and rollback.
12. Retrain only after data/quality gates; feed confirmed outcomes and treatment assignments back into the pipeline.

## 32. Final revision checklist

- [ ] I can frame the target, unit, horizon, baseline and action.
- [ ] I can identify target, time, entity and preprocessing leakage.
- [ ] I can compare classical algorithms and their assumptions/trade-offs.
- [ ] I understand bias/variance, regularization, bagging and boosting.
- [ ] I can calculate and choose classification/regression/ranking metrics.
- [ ] I can choose thresholds using costs and capacity.
- [ ] I can design valid random/group/time/nested validation.
- [ ] I can build a leakage-safe preprocessing pipeline.
- [ ] I can debug unexpectedly weak or strong performance.
- [ ] I can design deployment, monitoring, retraining and rollback.
