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
title: "Unsupervised learning and anomaly detection interview cheat sheet"
description: "K-means, hierarchical clustering, DBSCAN/HDBSCAN, Gaussian mixtures, cluster validation, PCA, t-SNE/UMAP, anomaly methods, thresholds, scarce-label evaluation, and operations."
summary: "Revise clustering, representation, and anomaly systems through explicit geometry, reference populations, external validation, alert economics, feedback, and operations."
permalink: "/interview-prep/cheat-sheets/unsupervised-learning-anomaly-detection/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 7 · Unsupervised and anomaly methods"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 7 source:** This review candidate integrates the newly prepared revision source into the Prep site. It is separate from the Week 1–20 learning assessments.

**Target roles:** Data Scientist, ML Engineer, AI Engineer, Applied Scientist, AI/Data Science Lead  
**Use:** clustering, dimensionality reduction, segmentation, representation, anomaly-detection, and monitoring rounds  
**Interview rule:** unsupervised algorithms always optimize an objective, distance, density, or reconstruction assumption. Define the decision and validate external usefulness; a visually pleasing cluster plot is not evidence.

## 1. Thirty-second revision

- Start with the downstream decision: segmentation, discovery, compression, visualization, alerting, quality control, or feature creation.
- Define entity, time window, representation, distance, scale, missingness, and deployment population before choosing an algorithm.
- K-means minimizes within-cluster squared Euclidean distance and prefers roughly spherical, similar-scale clusters.
- Hierarchical clustering exposes nested structure but linkage and distance determine the tree; dendrogram cuts are modeling choices.
- DBSCAN finds dense regions and marks sparse points as noise; it struggles when density varies strongly. HDBSCAN handles variable density better but still needs validation.
- Gaussian mixtures give soft probabilistic assignments under distributional assumptions; expectation-maximization can converge to local optima.
- PCA is linear variance-preserving projection. t-SNE and UMAP are primarily neighborhood visualizers; apparent gaps and cluster sizes can be misleading.
- An anomaly is rare relative to a defined reference and context. Rare does not mean harmful, and harmful does not always mean globally rare.
- Isolation Forest isolates points by random partitions; one-class SVM learns a boundary; LOF compares local density; autoencoders use reconstruction error.
- Thresholds should come from error costs, alert capacity, prevalence, and time/slice behavior—not the default contamination value alone.
- Evaluate with confirmed labels where possible, time-based backtests, injected faults with caveats, analyst yield, delay, stability, and downstream value.
- Monitor data quality, score distribution, alert volume, novelty, feedback, model/version lineage, and concept changes; provide safe fallback and retraining rules.

## 2. Problem and representation contract

Record:

| Dimension | Question |
|---|---|
| Decision | what action follows a cluster or anomaly score? |
| Entity/grain | customer, machine window, transaction, document, embedding? |
| Reference | normal relative to which population and period? |
| Context | time, peer group, season, location, operating mode? |
| Representation | raw, engineered, embedding, sequence, graph? |
| Geometry | Euclidean, cosine, Manhattan, learned metric, density? |
| Scale | which features dominate distance and why? |
| Validation | labels, experts, stability, downstream outcome, intervention? |
| Operations | batch/online, latency, alert budget, explanation, feedback? |

Exclude identifiers that create accidental separation unless identity is intentionally modeled. Fit preprocessing and representation on training/reference data, then apply it unchanged to validation and production.

## 3. Distance, scale, and high dimensions

Distance-based methods are sensitive to feature scale, redundant dimensions, sparsity, and irrelevant features. Standardize or robust-scale continuous features when appropriate; handle categorical and mixed data with suitable encodings or distances.

In high dimensions, nearest and farthest distances can become less distinguishable, density estimates become sparse, and noise dimensions dominate. Remedies include domain feature selection, PCA or learned representations, cosine geometry for appropriate embeddings, and methods designed for the data type.

Validate that neighborhoods are meaningful. Similarity in representation space does not automatically mean equivalent business risk or behavior.

## 4. K-means

K-means minimizes within-cluster sum of squares:

$$
\min_{C_1,\ldots,C_k}\sum_{j=1}^k\sum_{x_i\in C_j}\lVert x_i-\mu_j\rVert_2^2
$$

Algorithm:

1. initialize centroids, preferably with k-means++;
2. assign each point to its nearest centroid;
3. recompute centroids;
4. repeat until assignment/objective convergence.

Strengths: simple, scalable, interpretable centroids. Assumptions: Euclidean geometry, mean represents a cluster, and clusters are reasonably compact/convex.

Watch random initialization, empty/small clusters, outliers, categorical data, unequal densities, and forced assignment of every point. Run multiple initializations and assess stability plus external utility. Elbow and silhouette are aids, not automatic selectors of $k$.

## 5. Hierarchical clustering

Agglomerative clustering starts with each point as a cluster and repeatedly merges:

- **single linkage:** minimum cross-cluster distance; finds chains, sensitive to bridges;
- **complete linkage:** maximum distance; compact clusters, sensitive to outliers;
- **average linkage:** average cross-distance;
- **Ward linkage:** merges that minimally increase within-cluster variance, usually with Euclidean geometry.

A dendrogram records merge distances, not a unique true partition. Choose a cut using stability, domain interpretability, downstream utility, and scale constraints.

Naive hierarchical methods are expensive for very large datasets. Sample, summarize, use approximate methods, or cluster within meaningful partitions when necessary—while checking that the shortcut preserves structure.

## 6. DBSCAN and HDBSCAN

DBSCAN uses neighborhood radius $\varepsilon$ and minimum samples:

- core point: enough neighbors within $\varepsilon$;
- border point: near a core but not dense itself;
- noise point: not density-reachable from a core.

It can find non-convex clusters and mark noise without specifying $k$. It is sensitive to scale and one global density threshold.

HDBSCAN builds a hierarchy across density levels and extracts stable clusters, often handling variable densities better. It can return membership probabilities and noise, but parameters and distance still encode assumptions.

Use k-distance plots as diagnostics, not proof. Validate small-cluster stability, noise rate, perturbation robustness, and whether “noise” is a valid business category rather than discarded data.

## 7. Gaussian mixtures and EM

A Gaussian mixture models density as:

$$
p(x)=\sum_{k=1}^{K}\pi_k\mathcal{N}(x\mid\mu_k,\Sigma_k)
$$

Expectation-maximization alternates:

- **E-step:** compute posterior membership responsibilities;
- **M-step:** update mixture weights, means, and covariances.

GMMs provide soft assignments and elliptical clusters under Gaussian components. Covariance choice—full, tied, diagonal, spherical—trades flexibility, sample need, and stability.

Use multiple starts, regularize covariance, and inspect degenerate components. AIC/BIC can compare likelihood-complexity tradeoffs under model assumptions, but external usefulness and stability still matter.

## 8. Cluster validation

### Internal

- silhouette score compares cohesion and separation;
- Davies–Bouldin and Calinski–Harabasz summarize geometry;
- likelihood/AIC/BIC apply to probabilistic models;
- objective value tracks the algorithm's own criterion.

### Stability

Refit across seeds, samples, time windows, and small perturbations. Align cluster labels before comparing. Unstable clusters may not support durable targeting.

### External and downstream

- agreement with trusted labels, if available;
- enrichment for meaningful outcomes without leaking them into fitting;
- interpretability and actionability;
- uplift or value from cluster-specific policy tested prospectively;
- fairness and representation across groups;
- persistence and migration over time.

Never select a solution only because a 2D projection looks separated.

## 9. PCA for reduction and anomaly structure

PCA projects centered data onto orthogonal directions of maximum variance. It can denoise, compress, decorrelate, visualize, or supply residual-based anomaly scores.

For reconstruction with top-$k$ components, residual is:

$$
r_i=\lVert x_i-\hat x_i^{(k)}\rVert_2
$$

Large residual means a point is poorly represented by the retained linear subspace. This detects off-subspace anomalies but may miss unusual points within the main subspace.

Fit scaling and PCA on a reference period believed to represent acceptable behavior. Validate component stability and whether high variance corresponds to signal rather than sensor scale or batch effects.

## 10. t-SNE and UMAP caveats

t-SNE emphasizes local neighbor relationships and is excellent for exploratory visualization. Global distances, cluster area, and gaps are not directly trustworthy; perplexity, initialization, learning rate, and sampling can change the plot.

UMAP builds a neighborhood graph and optimizes a low-dimensional representation. It often preserves more broad structure and supports transformation of new points in implementations, but its geometry still depends on neighbors, minimum distance, metric, seed, and data density.

Best practice:

- fit on a documented sample/reference set;
- compare multiple seeds/parameters;
- color only after creating the embedding to avoid confirmation bias;
- validate clusters in original or justified representation space;
- do not infer causality or population prevalence from plot area.

## 11. Anomaly taxonomy

- **Point anomaly:** one observation is unusual globally.
- **Contextual anomaly:** unusual given context, such as time, peer group, or operating mode.
- **Collective anomaly:** a sequence or group is unusual though individual points may not be.
- **Novelty detection:** learn normal reference data and score new observations.
- **Outlier detection:** training data may already contain anomalies.

Define whether the target is data-quality error, fraud, failure, intrusion, novel customer behavior, or model drift. Each has different labels, costs, response, and adversarial behavior.

## 12. Isolation Forest

Isolation Forest repeatedly selects a feature and random split. Anomalies tend to be isolated with shorter paths. It scales well and handles nonlinear interactions without distance computation.

Watch:

- irrelevant/high-cardinality features;
- sparse categories and encoded identifiers;
- reference contamination;
- context ignored by a global model;
- score and contamination semantics across implementations;
- unstable thresholds under drift.

Use a separate validation or operational threshold rather than assuming the training contamination equals future anomaly prevalence.

## 13. One-class SVM

One-class SVM learns a boundary around reference data in kernel space. With an RBF kernel, `gamma` controls locality and `nu` constrains the expected fraction outside/support-vector behavior.

It can model complex normal regions but is sensitive to scaling, kernel parameters, reference contamination, and dataset size. Tune on confirmed normal plus representative anomalies or operational utility where available. A boundary that encloses training data tightly can overwhelm analysts in production.

## 14. Local Outlier Factor

LOF compares a point's local density with densities of its neighbors. It can identify points that are unusual within a region even when global density varies.

The neighborhood size controls locality. Too small is noisy; too large becomes global. Scaling and distance remain critical. Distinguish transductive outlier detection from novelty mode for scoring new points in the chosen implementation.

LOF explanations can cite influential features and neighbors, but the density ratio itself may be hard for operators to act on.

## 15. Autoencoder anomaly detection

An autoencoder learns $\hat x=g(f(x))$ and uses reconstruction error as a score. It is useful for high-dimensional nonlinear data when enough representative normal data exists.

Risks:

- a powerful network reconstructs anomalies well;
- contaminated training teaches abnormal patterns;
- loss is dominated by high-scale/noisy features;
- reconstruction error does not match business harm;
- temporal or relational context is lost;
- changing sensors cause false alerts.

Constrain capacity, normalize thoughtfully, hold out known events, inspect per-feature residuals, and compare with PCA and simple baselines. For sequences, use time-aware architectures only when they add validated value.

## 16. Time-series and collective anomalies

Time-series anomalies require seasonality, trend, operating state, and event alignment. Useful approaches include:

- forecast residuals with prediction intervals;
- seasonal decomposition and robust residual thresholds;
- change-point detection;
- multivariate state-space or representation models;
- rules for impossible rates, missing blocks, or stuck sensors;
- sequence or window embeddings followed by density/isolation methods.

Use rolling-origin evaluation. Prevent future values from entering smoothing, normalization, or windows. Group related alerts into incidents and suppress repeated notifications without hiding continued harm.

## 17. Thresholds, alert budgets, and calibration

The detector produces a score; the system chooses an action threshold. Select it using:

- false-positive and false-negative costs;
- analyst/inspection capacity;
- expected prevalence and base-rate shift;
- recall at top-$k$ or alert budget;
- severity tiers and abstention;
- detection delay;
- per-asset/segment normalization;
- stability over time.

For a capacity of 100 investigations per day, evaluate precision and captured value among the top 100, not only ROC-AUC. Use separate thresholds or models only when group/context differences are legitimate and governance approves the consequences.

Unsupervised scores are not probabilities without calibration against labeled outcomes and a stable reference population.

## 18. Evaluation with scarce labels

Use an evidence ladder:

1. audited historical incidents with time-based holdout;
2. prospective shadow mode and expert adjudication;
3. random audit sample to estimate missed anomalies;
4. controlled fault injection or simulation, labeled as synthetic;
5. stability across seeds, windows, and benign perturbations;
6. downstream intervention or prevented-loss evidence;
7. operational metrics: alert yield, time to detect, workload, recurrence.

Precision measured only among reviewed alerts is biased if unreviewed cases are assumed negative. Sample below-threshold events for review. Synthetic anomalies test known signatures but rarely establish real-world recall.

## 19. Production architecture and monitoring

Separate:

- immutable raw/reference data;
- versioned preprocessing and representation;
- fitted detector and score contract;
- threshold/policy version;
- explanation/context service;
- alert deduplication and case management;
- analyst feedback and label store;
- retraining and rollback workflow.

Monitor input quality/freshness, feature and score distributions, percentage alerted, alerts by slice, reviewer yield, delay, model and threshold version, feedback latency, and downstream actions. A score shift may mean more incidents, data drift, pipeline failure, or a changed operating regime—triage before retraining.

## 20. Small comparison scaffold

```python
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler


def fit_detector(
    reference: NDArray[np.float64], *, random_state: int = 17
) -> tuple[RobustScaler, IsolationForest]:
    if reference.ndim != 2 or reference.shape[0] < 20:
        raise ValueError("reference must contain at least 20 two-dimensional samples")
    scaler = RobustScaler().fit(reference)
    detector = IsolationForest(
        n_estimators=300,
        contamination="auto",
        random_state=random_state,
        n_jobs=-1,
    ).fit(scaler.transform(reference))
    return scaler, detector
```

The model score is only one layer. Threshold it on a later, representative set using labels, review capacity, and cost. Keep the reference period, preprocessing, detector, and threshold identities together.

## 21. Common interview failure modes

- clustering without a downstream decision;
- leaving raw units to dominate Euclidean distance;
- selecting $k$ from one elbow plot;
- treating DBSCAN noise as bad records;
- interpreting mixture probabilities as causal segment membership;
- clustering a t-SNE plot instead of the justified representation;
- calling every rare point fraud or failure;
- setting contamination equal to guessed business prevalence and stopping;
- evaluating only reviewed alerts;
- random splitting time-series windows;
- training an autoencoder with excessive capacity and contaminated normal data;
- retraining immediately after score drift without diagnosing the data path.

## 22. Rapid interview Q&A

**K-means or GMM?**  
K-means gives hard centroid assignments under spherical squared-distance geometry; GMM gives soft probabilistic assignments with configurable covariance assumptions.

**Why can silhouette mislead?**  
It rewards a particular geometric separation and may reject meaningful non-convex, overlapping, or operationally useful groups.

**Can t-SNE prove clusters?**  
No. It is a parameter-sensitive local-neighborhood visualization; validate structure in the original or justified space.

**Why use local anomaly methods?**  
A point can be normal globally but unusual among comparable peers or contexts.

**How do you estimate false negatives without labels?**  
Randomly audit below-threshold cases, use prospective feedback, and triangulate with known incidents and bounded simulations.

## 23. Lead-level case

**Case:** a global Isolation Forest generates thousands of daily alerts after a new factory begins sending telemetry.

A strong answer should:

1. protect operations by capping/triaging alerts while preserving scores and raw evidence;
2. compare schema, units, missingness, firmware, sampling, operating regimes, and score contributions by factory;
3. determine whether the new site is erroneous, legitimately different, or outside the reference population;
4. rebuild context-aware peer groups or models only with enough representative normal and incident evidence;
5. set thresholds from investigation capacity and cost, sample suppressed alerts, and run shadow validation;
6. add site onboarding contracts, unit checks, reference-population ownership, drift diagnosis, and rollback.

## 24. Final checklist

- Can you define the downstream decision, entity, representation, geometry, and reference population?
- Can you explain k-means assumptions and validate $k$ beyond an elbow?
- Can you compare hierarchical, DBSCAN/HDBSCAN, and Gaussian mixtures?
- Can you validate clusters with stability and downstream evidence?
- Can you explain PCA versus t-SNE/UMAP without overclaiming plots?
- Can you distinguish point, contextual, collective, novelty, and outlier detection?
- Can you compare Isolation Forest, one-class SVM, LOF, PCA, and autoencoders?
- Can you set an alert threshold from costs, capacity, and time-based evidence?
- Can you estimate missed anomalies through random audit and prospective feedback?
- Can you operate, monitor, explain, retrain, and roll back the full anomaly system?

## Primary references

- scikit-learn documentation: clustering, decomposition, manifold learning, novelty and outlier detection.
- Ester et al., original DBSCAN paper; Campello et al., HDBSCAN research.
- Liu, Ting, and Zhou, original Isolation Forest papers.
- Breunig et al., original Local Outlier Factor paper.
- van der Maaten and Hinton, t-SNE; McInnes, Healy, and Melville, UMAP.
