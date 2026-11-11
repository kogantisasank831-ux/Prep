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
title: "Unsupervised learning and dimensionality reduction interview cheat sheet"
description: "Representations and distance, k-means, mixtures and EM, hierarchical and density clustering, PCA, t-SNE, UMAP, evaluation, stability, and production lifecycle."
summary: "Revise unsupervised learning as a decision system: define useful structure, choose geometry and algorithms deliberately, test stability and downstream utility, and operate the result safely."
permalink: "/interview-prep/cheat-sheets/unsupervised-learning-dimensionality-reduction/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 9 · Unsupervised learning and dimensionality reduction"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 9 source-backed scope:** This review candidate publishes the canonical interview sheet without altering its instructional body. It remains separate from the Week 1–20 learning assessments.

**Target roles:** Lead Data Scientist, Senior Data Scientist, Applied Scientist, ML Engineer, AI Engineer  
**Use:** clustering, segmentation, representation-learning, visualization, anomaly-detection, and modeling-case interviews  
**Interview rule:** “no target label” does not mean “no objective.” Define the decision, representation, similarity, evaluation evidence, stability requirement, and treatment of new points before selecting an algorithm.

## 1. Thirty-second revision

- Unsupervised learning discovers structure from inputs without a supervised target, but every method still encodes assumptions through its objective, distance, neighborhood, architecture, or prior.
- The business unit matters: customer, account, session, product, document, time window, or graph node can lead to different results.
- Scaling, missing-value treatment, categorical representation, feature weighting, and distance choice often affect clusters more than algorithm selection.
- K-means minimizes within-cluster squared Euclidean distance and favors roughly spherical, similarly scaled clusters.
- Gaussian mixture models provide soft memberships under a probabilistic mixture assumption; covariance choice controls cluster geometry and parameter count.
- Hierarchical clustering exposes nested structure; linkage and distance define what “close clusters” means.
- DBSCAN finds density-connected regions and labels noise; HDBSCAN handles variable density more flexibly but still needs meaningful distance and stability checks.
- PCA is linear, global, and variance-preserving; t-SNE and UMAP are mainly neighborhood-preserving visualization/representation tools, not proof of discrete populations.
- Clustering evaluation needs multiple lenses: internal geometry, external labels if available, resampling/seed stability, temporal stability, and business utility.
- Silhouette can favor convex separation and becomes expensive; a high score is not sufficient evidence that segments are actionable.
- Cluster IDs have no inherent ordering and may permute between fits. Production needs cluster matching/versioning, new-point assignment, drift monitoring, and fallbacks.
- Treat names and narratives as hypotheses. Inspect representative examples, distributions, uncertainty, and possible harms before operational use.

## 2. Frame the problem before modeling

Write an unsupervised-learning contract:

> Group or represent **entities E**, observed over **window W**, using **features F** and **similarity S**, so that **decision D** improves, subject to **stability, capacity, privacy, and fairness constraints C**.

Ask:

1. What decision changes because of the discovered structure?
2. Is the goal segmentation, compression, visualization, retrieval, denoising, topic discovery, pretraining, or anomaly scoring?
3. What is one row/entity, and are rows independent?
4. Which time period is available at decision time?
5. Should magnitude, direction, sequence, geography, or connectivity define similarity?
6. Must the method assign future points?
7. Are overlapping/soft memberships acceptable?
8. Is “noise” a valid outcome?
9. How will a domain expert reject a misleading result?

Clustering is often the wrong tool when the real goal is a supervised outcome, a rule-based operational tier, causal personalization, or nearest-neighbor retrieval.

## 3. Representation and distance

### Preprocessing decisions

| Data characteristic | Candidate treatment | Main risk |
|---|---|---|
| different numeric units | standardize, robust-scale, domain normalization | outliers or zero variance |
| heavy tails | log/Box-Cox-like transform, robust distance | changing business interpretation |
| categorical features | one-hot, target-independent embeddings, matching distance | high cardinality and arbitrary geometry |
| mixed data | Gower-like distance or separate representations | weighting incomparable feature types |
| sparse counts/text | TF-IDF, cosine, latent semantic representation | document length and vocabulary drift |
| sequences | summary features, alignment distance, learned sequence embedding | temporal information loss |
| geospatial coordinates | haversine/network distance | Euclidean distance on latitude/longitude |
| graphs | structural features or graph embeddings | topology leakage and unstable embedding axes |

Standardization should be fit on the training/reference population. Do not include IDs or future information. Weighting a feature is equivalent to defining importance in the geometry; document it as a product/model choice.

### Distance and similarity

- Euclidean: straight-line distance; sensitive to scale and high dimensions.
- Manhattan: sum of absolute differences; sometimes more robust and axis-aligned.
- Cosine: angle between nonzero vectors; common for text/embeddings.
- Mahalanobis: accounts for covariance but needs a stable covariance estimate.
- Jaccard: overlap for sets/binary indicators.
- Hamming: positions that differ.
- Dynamic time warping: flexible sequence alignment with computational and interpretability costs.

In high dimensions, distances can concentrate and neighborhoods become unstable. Feature selection, domain representation, PCA, metric learning, or more data may help; dimensionality reduction is not an automatic cure.

## 4. K-means and its assumptions

K-means minimizes:

`Σ_i ||x_i − μ_(c_i)||₂²`

The alternating procedure assigns points to the nearest centroid and recomputes centroids. It converges to a local optimum, so initialization and repeated starts matter.

Works well when:

- Euclidean mean is meaningful;
- clusters are compact and roughly isotropic;
- cluster sizes/densities are not extremely different;
- hard membership is acceptable;
- the number of clusters is chosen and validated.

Fails or misleads with non-convex shapes, unscaled features, categorical variables treated as numbers, strong outliers, unequal densities, or a continuous population forced into bins.

K-means++ improves initialization. Mini-batch k-means trades some fidelity for scale. Medoid-based methods use an observed representative and can support arbitrary distances, usually at higher computational cost.

### Choosing the number of clusters

- inertia always decreases as `k` increases, so the “elbow” is subjective;
- silhouette compares cohesion with nearest-cluster separation;
- gap statistics compare against a null reference;
- information criteria can compare probabilistic mixtures;
- stability measures whether membership persists under perturbation;
- business constraints may bound useful segment count.

Use several criteria plus domain review. Do not optimize a single internal metric and call the result “true.”

## 5. Probabilistic mixtures and expectation-maximization

A Gaussian mixture model represents:

`p(x) = Σ_k π_k N(x | μ_k, Σ_k)`

It produces posterior membership probabilities. Expectation-maximization alternates:

- E-step: compute responsibilities under current parameters;
- M-step: update mixture weights, means, and covariances.

Covariance options trade flexibility and sample requirement:

- spherical: one variance per component;
- diagonal: variance per feature;
- tied: one covariance shared by components;
- full: separate full covariance per component.

Risks include local optima, singular covariance, component collapse, too many parameters, sensitivity to scale/outliers, and Gaussian assumptions. Regularize covariance, use multiple starts, inspect likelihood and membership entropy, and evaluate held-out density carefully.

Soft membership is useful when boundaries are ambiguous, but a probability from a misspecified mixture is not automatically calibrated uncertainty about a real-world class.

## 6. Hierarchical, density, and graph-based clustering

### Hierarchical clustering

Agglomerative clustering begins with separate points and merges clusters. Linkage controls inter-cluster distance:

- single: nearest pair; captures chains but can bridge through noise;
- complete: farthest pair; produces compact groups and is outlier-sensitive;
- average: average pairwise distance;
- Ward: minimizes within-cluster variance, usually with Euclidean geometry.

A dendrogram visualizes merge distances, but its appearance depends on preprocessing, metric, linkage, and ordering. Cutting at a height creates clusters; it does not validate them.

### DBSCAN and HDBSCAN

DBSCAN uses a neighborhood radius `eps` and minimum sample count:

- core points have enough neighbors;
- border points attach to a core region;
- remaining points are noise.

It finds arbitrary shapes without specifying `k`, but one global radius struggles with variable density. Feature scale and distance are decisive. Memory/performance can degrade with broad neighborhoods.

HDBSCAN builds a hierarchy across density scales and extracts stable clusters. It supports noise and membership strengths. It does not eliminate parameter choices or guarantee meaningful clusters, and prediction for unseen points may be approximate or library-specific.

### Spectral clustering

Spectral methods construct an affinity graph, use eigenvectors of a graph Laplacian, and cluster in the resulting space. They can recover non-convex structures, but affinity construction, scale parameters, memory, and out-of-sample assignment are challenges.

## 7. Other unsupervised objectives

| Method | Objective/idea | Useful for | Caveat |
|---|---|---|---|
| NMF | nonnegative low-rank factors | parts/topics in nonnegative data | local optimum and scale |
| ICA | statistically independent components | source separation | identifiability assumptions |
| LDA topic model | documents mix latent topics | interpretable topic exploration | bag-of-words and topic-count assumptions |
| autoencoder | reconstruct input through bottleneck | nonlinear representation/denoising | identity shortcut and poor semantic geometry |
| contrastive learning | align positive views, separate negatives | pretrained representations | augmentation defines invariance |
| self-organizing map | topology-aware prototype grid | exploratory visualization | parameter and distance sensitivity |

Representation quality must be evaluated against downstream tasks and operational behavior, not reconstruction loss alone.

## 8. PCA and dimensionality reduction

Given centered data matrix `X`, PCA selects orthogonal directions maximizing projected variance. Equivalently, truncated SVD gives a low-rank approximation.

Use PCA for:

- compression and noise reduction;
- decorrelation;
- visualization with two or three components;
- faster downstream methods;
- diagnosing dominant variance directions.

Choices and caveats:

- standardizing features changes the covariance structure;
- explained variance is not predictive importance;
- components have sign ambiguity;
- loadings can rotate or change under correlated features;
- rare low-variance signals can be discarded;
- fit the entire pipeline only on training/reference data;
- choose component count using downstream validation, reconstruction need, or a predeclared variance target.

Whitening scales component variance to one. It can help models assuming isotropy but amplifies low-variance noise and removes original scale information.

## 9. t-SNE and UMAP without visualization myths

### t-SNE

t-SNE matches local-neighborhood probability distributions between high and low dimensions. It is effective for exploratory visualization, but:

- global distances and cluster sizes are not reliably preserved;
- perplexity, learning rate, initialization, and seed affect the plot;
- separated islands can appear even without discrete natural groups;
- out-of-sample transformation is not the standard strength of classic t-SNE.

### UMAP

UMAP constructs a weighted neighborhood graph and optimizes a low-dimensional layout. It is often faster and supports transformation in common implementations. Key parameters such as neighbor count and minimum distance control local/global trade-offs and compactness.

For both:

- scale and represent features first;
- run multiple seeds/parameters;
- color by known metadata only after creating the embedding to avoid visual storytelling;
- quantify neighborhood preservation where relevant;
- never use a pretty plot as the sole evidence for segmentation.

## 10. Evaluation without a single ground truth

### Internal geometry

- Silhouette for point `i`: `s(i) = [b(i) − a(i)] / max(a(i), b(i))`
- Davies-Bouldin: within/between cluster similarity; lower is better.
- Calinski-Harabasz: between-cluster versus within-cluster dispersion; higher is better.

These metrics inherit the selected metric/geometry and can favor particular shapes.

### External agreement

If trustworthy labels exist, use adjusted Rand index, adjusted mutual information, homogeneity/completeness, or task-specific agreement. Labels may represent a different concept from the unsupervised objective.

### Stability and utility

- rerun across seeds;
- bootstrap or subsample entities;
- perturb preprocessing and hyperparameters;
- compare membership using label-invariant matching;
- test on future periods and important slices;
- measure downstream lift, reduced manual workload, or action response;
- obtain blinded domain review of representatives and counterexamples.

Stability can be low because the data has weak cluster structure—not merely because the algorithm is poor. Report uncertainty rather than forcing a definitive taxonomy.

## 11. Minimal dependency-free example: mean silhouette

```python
from __future__ import annotations

from math import dist
from statistics import mean
from typing import Hashable, Sequence


def mean_silhouette(
    points: Sequence[Sequence[float]],
    labels: Sequence[Hashable],
) -> float:
    """Compute an educational O(n²) Euclidean mean silhouette score."""
    if len(points) != len(labels) or len(points) < 2:
        raise ValueError("points and labels must have the same length >= 2")
    if len(set(labels)) < 2:
        raise ValueError("at least two clusters are required")
    width = len(points[0])
    if width == 0 or any(len(point) != width for point in points):
        raise ValueError("all points must have the same nonzero dimension")

    scores: list[float] = []
    for index, point in enumerate(points):
        same = [
            dist(point, other)
            for other_index, other in enumerate(points)
            if labels[other_index] == labels[index] and other_index != index
        ]
        if not same:
            scores.append(0.0)
            continue

        a_value = mean(same)
        other_cluster_means = []
        for other_label in set(labels):
            if other_label == labels[index]:
                continue
            distances = [
                dist(point, other)
                for other, label in zip(points, labels, strict=True)
                if label == other_label
            ]
            other_cluster_means.append(mean(distances))

        b_value = min(other_cluster_means)
        denominator = max(a_value, b_value)
        scores.append(0.0 if denominator == 0.0 else (b_value - a_value) / denominator)
    return mean(scores)


sample_points = [(0.0, 0.0), (0.1, 0.0), (10.0, 10.0), (10.1, 10.0)]
sample_labels = ["left", "left", "right", "right"]
score = mean_silhouette(sample_points, sample_labels)
assert 0.98 < score <= 1.0
```

This implementation is intentionally small and slow. Production libraries provide optimized implementations and edge-case behavior that should be verified.

## 12. Production lifecycle

1. Version the entity definition, time window, feature pipeline, scaler, representation, algorithm, parameters, and reference data.
2. Store cluster profiles and representative/edge examples, not only IDs.
3. Match new clusters to old ones using centroids, distributions, or assignment overlap; do not assume numeric IDs persist.
4. Define how new points are assigned, deferred, or labeled as noise.
5. Monitor input drift, cluster prevalence, distance-to-prototype, membership confidence, and business outcomes.
6. Treat cluster-specific policies as experiments when possible.
7. Protect small/sensitive groups, prevent re-identification, and review proxy discrimination.
8. Establish retraining, rollback, and retirement rules.

## 13. Library map

| Tool | Best fit | Verify |
|---|---|---|
| scikit-learn | preprocessing, PCA, k-means, mixtures, hierarchical, DBSCAN, metrics | estimator assumptions and out-of-sample support |
| hdbscan / sklearn HDBSCAN | hierarchical density clustering | parameter semantics, prediction behavior, memory |
| UMAP | nonlinear neighborhood representation | metric, seed, neighbor/min-distance sensitivity |
| PyTorch/JAX | autoencoders and learned representations | objective, leakage, batch/inference behavior |
| Gensim | classical topic modeling | preprocessing, topic stability, version support |
| RAPIDS cuML | GPU-accelerated clustering/reduction | numerical parity, memory, workload size |

Pin exact versions. Similar class names across libraries can have different defaults, distance definitions, and prediction contracts.

## 14. Rapid interview questions

**Why is scaling crucial for k-means?**  
Squared Euclidean distance lets large-range features dominate the objective.

**Does a high silhouette prove useful clusters?**  
No. It measures geometry under a chosen distance and can reward shapes unrelated to the decision.

**K-means versus GMM?**  
K-means gives hard assignments around centroids under squared Euclidean geometry. GMM models component densities and gives soft responsibilities with covariance assumptions.

**Why might DBSCAN label many points as noise?**  
The radius/min-sample settings, feature scale, distance metric, dimensionality, or genuinely low-density data may be mismatched.

**Can PCA improve k-means?**  
It may remove noise and reduce computation, but can discard low-variance structure that defines useful groups.

**Can t-SNE show clusters that are not real?**  
Yes. Its neighborhood objective and visualization parameters can create apparent islands; validate in original/held-out space.

**How do you compare two clustering runs?**  
Use label-invariant agreement, cluster matching, profile comparison, and downstream stability—not raw numeric IDs.

**What is the strongest evidence for customer segments?**  
Stable membership and interpretable differences that lead to reproducible improvement in a controlled policy or business outcome.

## 15. Lead-level case: customer segmentation for retention

Answer in this sequence:

1. Clarify whether the decision is messaging, service level, offer allocation, or investigation; retention itself suggests a supervised/causal component.
2. Define customers, observation and action windows, eligibility, exclusions, and privacy constraints.
3. Build point-in-time features covering behavior, value, tenure, service issues, and engagement without future leakage.
4. Establish interpretable business-rule and PCA+k-means baselines; compare mixture/density methods only if geometry supports them.
5. Evaluate stability across seeds, samples, time, geography, and important customer slices.
6. Profile clusters with distributions and examples; involve domain experts without using post-hoc names as validation.
7. Test whether cluster-aware actions outperform a simpler propensity/uplift policy under capacity and fairness constraints.
8. Version assignments, monitor drift and outcome, stage rollout, and keep a safe default for uncertain/new customers.

The strongest lead may conclude that clustering is exploratory and recommend supervised uplift modeling for the actual retention treatment.

## 16. Final checklist

- [ ] I define entity, decision, observation window, and similarity.
- [ ] I can explain how scaling and representation change geometry.
- [ ] I know k-means, GMM, hierarchical, DBSCAN/HDBSCAN, and spectral assumptions.
- [ ] I distinguish PCA, t-SNE, UMAP, and learned representations.
- [ ] I use internal, external, stability, temporal, and business evidence.
- [ ] I do not treat a 2-D plot as proof of natural clusters.
- [ ] I plan cluster matching, new-point assignment, drift, and rollback.
- [ ] I review privacy, sensitive proxies, and harms before activation.
- [ ] I can explain when clustering is the wrong problem formulation.

## 17. Primary references

- [scikit-learn clustering user guide](https://scikit-learn.org/stable/modules/clustering.html)
- [scikit-learn Gaussian mixture models](https://scikit-learn.org/stable/modules/mixture.html)
- [scikit-learn decomposition and PCA](https://scikit-learn.org/stable/modules/decomposition.html)
- [scikit-learn clustering performance evaluation](https://scikit-learn.org/stable/modules/clustering.html#clustering-performance-evaluation)
- [scikit-learn manifold learning](https://scikit-learn.org/stable/modules/manifold.html)
- [UMAP documentation](https://umap-learn.readthedocs.io/en/latest/)
- [HDBSCAN documentation](https://hdbscan.readthedocs.io/en/latest/)
- [van der Maaten and Hinton, Visualizing Data using t-SNE](https://www.jmlr.org/papers/v9/vandermaaten08a.html)
- [McInnes, Healy, and Melville, UMAP](https://arxiv.org/abs/1802.03426)
- [scikit-learn common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html)
