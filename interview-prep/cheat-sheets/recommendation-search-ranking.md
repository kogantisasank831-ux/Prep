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
title: "Recommendation, search, and ranking interview cheat sheet"
description: "Multi-stage architectures, feedback and exposure, collaborative filtering, two-tower retrieval, learning to rank, ranking metrics, counterfactual evaluation, cold start, exploration, and reliability."
summary: "Revise recommendation and ranking from candidate universe and exposure through retrieval, scoring, list policy, causal evaluation, feedback loops, and production evidence."
permalink: "/interview-prep/cheat-sheets/recommendation-search-ranking/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 8 · Recommendation, search, and ranking"
current_label: "Revision guide"
alternate_label: "Cheat sheets hub"
alternate_url: "/cheat-sheets/"
---
> **Batch 8 source:** This page integrates the prepared `28_Recommendation_Search_Ranking_Interview_Cheat_Sheet.md` artifact in the Prep site. It is separate from the Week 1–30 learning assessments.

**Target roles:** Data Scientist, Lead Data Scientist, Applied Scientist, ML Engineer, AI/Search Engineer  
**Use:** recommender-system, personalized-search, learning-to-rank, ML-system-design, product, and leadership interviews  
**Interview rule:** recommendations optimize a user decision under exposure and feedback loops. Define the request, candidate universe, eligibility, action, logged exposure, and product objective before choosing matrix factorization, a two-tower model, or LambdaMART.

## 1. Thirty-second revision

- A common production stack is candidate generation → scoring/ranking → rule/policy re-ranking.
- Candidate generation maximizes useful recall under latency; ranking spends more compute on a smaller set; re-ranking enforces diversity, freshness, safety, fairness, inventory, and business constraints.
- Start with popularity, recency, co-visitation, content, and simple collaborative baselines.
- Implicit feedback is not an ordinary label: unclicked items may be unseen, not disliked. Log exposure, position, policy, and action.
- Matrix factorization learns user/item factors; two-tower retrieval supports independent embeddings and ANN serving; a ranker uses richer cross features.
- Negative sampling changes the learning problem. Define the sampling distribution, false-negative risk, in-batch bias, and correction.
- Use time-aware/user-aware offline splits. Prevent future interactions, duplicate impressions, and candidate leakage.
- Evaluate retrieval recall before ranking metrics. Ranking cannot recover relevant items absent from the candidate set.
- Precision@K, Recall@K, MAP, MRR, and NDCG answer different questions; include coverage, diversity, novelty, calibration, safety, and business constraints.
- Offline metrics are biased by the historical logging policy. Use online experiments for product impact; counterfactual estimators need propensities, overlap, and variance control.
- Cold start, long tail, popularity feedback, position bias, filter bubbles, and exploration are core design concerns.
- Optimize a metric tree: long-term user value and business outcome, product behavior, model quality, service reliability, and cost.

## 2. Define the recommendation contract

Specify:

- user/account/session/query and context;
- item/document/content universe;
- eligibility, availability, policy, tenancy, and safety constraints;
- request time and latency budget;
- candidate sources and inventory freshness;
- action: impression, click, save, watch, purchase, hide, report, or long-term retention;
- feedback/label window and delayed conversions;
- logged exposure, position, score, policy/version, and propensity if available;
- primary outcome, guardrails, and intervention capacity.

Distinguish:

- **recommendation:** choose personalized items without an explicit query;
- **search:** satisfy an explicit information/product need;
- **ranking:** order a candidate list by utility/relevance;
- **retrieval:** efficiently produce a high-recall candidate set;
- **re-ranking:** apply additional list-level constraints or objectives.

## 3. Multi-stage architecture

### Stage 0: eligibility and policy

Remove unavailable, unauthorized, unsafe, blocked, already-consumed, geographically invalid, or legally restricted items. Apply user-bound authorization outside model text/scores.

### Stage 1: candidate generation

Union candidates from:

- popularity/trending and freshness;
- user/item co-visitation;
- content or semantic retrieval;
- collaborative filtering;
- two-tower embeddings + ANN;
- followed creators/categories;
- business or exploration pools.

Optimize Recall@K, latency, index freshness, source contribution, and coverage. Deduplicate and preserve source/provenance features.

### Stage 2: scoring/ranking

Use richer user, item, context, and cross features to predict click, conversion, dwell time, satisfaction, or expected utility. Models include logistic/GBDT, factorization machines, deep interaction models, sequence/session models, and learning-to-rank objectives.

### Stage 3: re-ranking

Apply:

- diversity and category/creator limits;
- novelty, serendipity, and freshness;
- fairness/exposure constraints;
- safety and policy;
- inventory, margin, and capacity;
- deduplication;
- exploration;
- list-level utility.

Hard constraints belong in deterministic enforcement where possible; a model score is not authorization or policy.

## 4. Baselines

Always benchmark:

- global popularity;
- popularity by segment/context;
- recency/trending;
- item-to-item co-occurrence;
- content similarity;
- business/editorial rule;
- non-personalized search ranker.

Baselines are production fallbacks, cold-start strategies, and debugging tools. A personalized model that barely beats popularity may be exploiting leakage or the evaluation distribution.

## 5. Feedback and labels

### Explicit feedback

Ratings, likes/dislikes, survey labels, relevance judgments. Usually sparse and selected; people who rate are not a random population.

### Implicit feedback

Clicks, views, purchases, watch time, dwell, skips, hides. A missing action means **unknown under exposure**, not necessarily negative preference.

Log:

- candidate eligibility and set;
- which items were displayed;
- position/layout and UI treatment;
- timestamp, request/session, and user context;
- model/retriever/index/config version;
- score and candidate source;
- action and delayed outcome;
- exploration probability/propensity when used.

Common biases:

- position and presentation bias;
- exposure/selection bias;
- popularity feedback loop;
- survivorship and unavailable-item bias;
- delayed conversion;
- bots/fraud;
- repeated impressions and fatigue;
- policy changes over time.

## 6. Collaborative filtering and matrix factorization

Approximate a user–item preference matrix:

$$
\hat{r}_{ui} = \mu + b_u + b_i + p_u^Tq_i
$$

where $p_u$ and $q_i$ are user/item latent factors. For explicit data, minimize observed rating error plus regularization. For implicit data, use confidence-weighted ALS, BPR/pairwise loss, sampled classification, or ranking objectives.

Strengths:

- captures latent collaborative patterns;
- efficient dot-product retrieval;
- strong when interaction density is sufficient.

Weaknesses:

- cold users/items;
- popularity and exposure bias;
- limited context/content understanding;
- rapidly changing taste;
- factor staleness and large embedding storage.

## 7. Content, sequence, and hybrid models

Content-based systems use item/user attributes, text/image embeddings, categories, creators, or knowledge graphs. They handle new items but can overspecialize and inherit representation bias.

Sequence/session models use recent ordered interactions to model short-term intent. Recognize RNN/Transformer/session-based recommenders, but verify maximum sequence length, temporal leakage, causal masks, event weighting, and serving state.

Hybrid approaches combine collaborative, content, context, rules, and candidate sources. Ensembles can merge sources before ranking; record source identity to measure incremental value.

## 8. Two-tower retrieval

Learn query/user embedding $f(u,c)$ and item embedding $g(i)$:

$$
s(u,i)=f(u,c)^T g(i)
$$

Independent item embeddings can be precomputed and indexed with ANN, enabling retrieval from millions of items.

Key choices:

- training positives and exposure window;
- random, popularity, hard, in-batch, or mixed negatives;
- temperature and normalization;
- embedding dimension and similarity metric;
- item index refresh and deletion;
- user/context online features;
- ANN recall/latency/memory trade-off.

Risks:

- sampled negatives may contain relevant unseen items;
- in-batch negatives overrepresent frequent items or treat another user’s positive as negative;
- training candidate distribution differs from serving;
- stale item embeddings/index;
- dot-product retrieval cannot express all cross features.

Use the ranker for expensive user–item interactions after high-recall retrieval.

## 9. Learning to rank

### Pointwise

Predict relevance/action for each item independently with regression or classification. Simple and flexible but does not directly model ordering.

### Pairwise

Learn that relevant item $i$ should outrank $j$. Examples include RankNet/BPR-style losses and LambdaRank/LambdaMART. Pair construction and bias matter.

### Listwise

Optimize a whole query/list distribution or ranking surrogate. Closer to list metrics but more complex and sensitive to variable list sizes.

LambdaMART uses boosted trees with metric-aware lambda gradients, commonly targeting NDCG. Keep items grouped by query/request; a random row split or lost group boundary invalidates the task.

Features:

- query/user and item features;
- lexical/semantic relevance;
- historical engagement with exposure correction;
- price, quality, freshness, availability;
- cross features such as user-category affinity;
- candidate source and first-stage score;
- context: device, locale, time, session intent.

All temporal aggregates must be point-in-time correct.

## 10. Ranking metrics

For top $K$:

$$
Precision@K = \frac{|Relevant \cap TopK|}{K}
$$

$$
Recall@K = \frac{|Relevant \cap TopK|}{|Relevant|}
$$

Use retrieval Recall@K to ensure the candidate generator contains useful items. Precision focuses list purity; recall focuses coverage of relevant items.

Reciprocal rank:

$$
RR = \frac{1}{rank\ of\ first\ relevant\ item}
$$

MRR averages RR across queries and is useful when the first correct item dominates.

Discounted cumulative gain:

$$
DCG@K = \sum_{r=1}^{K}\frac{2^{rel_r}-1}{\log_2(r+1)}, \qquad
NDCG@K = \frac{DCG@K}{IDCG@K}
$$

NDCG supports graded relevance and discounts lower positions. When no relevant item exists, define the query policy explicitly.

MAP averages precision at each relevant hit. Also track hit rate, AUC where meaningful, calibration, catalog/user coverage, novelty, diversity, serendipity, repetition, freshness, and constraint violation.

Aggregate carefully:

- macro per user/query versus micro across impressions;
- head versus tail users/items/queries;
- new versus established entities;
- locale/device/category/safety slices;
- horizon/session and candidate-source breakdown.

## 11. Offline evaluation design

Use:

- chronological split per user or global deployment time;
- leave-last-N only when it matches product behavior;
- user holdout for new-user generalization;
- item holdout for cold-item evaluation;
- deduplication of repeated interactions and near-identical content;
- candidate set reconstructed from items actually eligible at that time;
- negative/evaluation sampling documented and consistent.

Avoid:

- using future interactions in user features;
- treating every unobserved item as a true negative;
- evaluating only among easy sampled negatives;
- allowing test items in training aggregates or vocabularies without an explicit transductive policy;
- comparing metrics computed with different candidate sets.

Offline metrics reflect logged exposure and policy. A better offline NDCG may not improve long-term satisfaction or business value.

## 12. Online evaluation and causal impact

Metric tree:

1. **business/user outcome:** retention, purchase, successful search, long-term satisfaction;
2. **product behavior:** CTR, conversion, dwell, saves, hides, abandonment;
3. **model:** retrieval recall, NDCG, calibration, coverage/diversity;
4. **service:** latency, timeout, empty-result, stale-index, error;
5. **cost/safety:** compute, policy violations, complaints, harmful exposure.

Use randomized online experiments for product impact. Randomize at a unit that handles cross-session effects and network/interference. Track novelty, position/layout changes, creator/seller effects, and long-term feedback.

Interleaving can compare search rankers sensitively for preference signals, but requires a valid interleaving method and does not replace longer-term outcome tests.

## 13. Counterfactual evaluation and exploration

Historical actions come from a logging policy. Off-policy evaluation may use:

- inverse propensity scoring (IPS);
- self-normalized IPS;
- direct outcome model;
- doubly robust estimator;
- replay where action spaces permit.

Requirements:

- logged action probability/propensity;
- overlap: target policy does not choose unsupported actions;
- stable reward definition and context;
- clipping/variance diagnostics;
- sensitivity to model misspecification.

Exploration approaches include epsilon-greedy, Thompson sampling, UCB, contextual bandits, or randomized candidate slots. Bound exploration with safety, inventory, fairness, and user-experience constraints. Adaptive allocation complicates ordinary inference.

## 14. Cold start, long tail, and feedback loops

### New user

- onboarding preferences;
- contextual/session features;
- segment/popularity mix;
- safe exploration;
- rapid online updates.

### New item

- content/category/creator embeddings;
- quality/policy checks;
- controlled exploration and freshness pools;
- seller/creator metadata;
- index/materialization SLA.

### Feedback loops

Popularity creates exposure, exposure creates interaction, and interaction trains more popularity. Counter with exposure-aware learning, calibrated exploration, tail coverage, diversity, and policy evaluation.

Monitor item/provider exposure distribution, concentration, repeated content, echo chambers, and vulnerable-user outcomes. Fairness may apply to users, content providers, or both; define whose opportunity and harm are measured.

## 15. Search-specific considerations

Search adds explicit query intent:

- lexical retrieval such as BM25 for exact terms;
- dense semantic retrieval for meaning/generalization;
- hybrid fusion and reranking;
- query rewriting, spelling, intent/category, filters;
- document freshness and authority;
- personalized signals only when they improve the query goal and respect privacy.

Evaluate navigational, informational, transactional, head/tail, ambiguous, multilingual, and zero-result queries separately. Semantic similarity is not automatically relevance; exact identifiers, price/availability, and policy filters may dominate.

## 16. Production reliability

Design for:

- index/feature/model version compatibility;
- partial candidate-source failure;
- stale or missing user features;
- ANN timeout/recall degradation;
- duplicate and unavailable items;
- cache key/tenant leakage;
- deterministic policy filters;
- fallback to popular/contextual safe lists;
- impression and propensity logging;
- shadow/canary rollout and rollback;
- deletion/privacy propagation through features and indexes.

Separate batch item embedding/index build from online user/query encoding. Capacity plan peak request rate, candidate counts, feature fetches, model compute, re-ranking, and tail latency.

## 17. Library map

| Tool | Primary use | Interview boundary |
|---|---|---|
| TensorFlow Recommenders | retrieval/ranking models and evaluation | production serving/index policy is separate |
| TorchRec | large-scale PyTorch recommendation embeddings/distributed training | useful when embedding scale justifies complexity |
| NVIDIA Merlin | GPU-oriented preprocessing/training/serving ecosystem | benchmark current component lifecycle and hardware |
| implicit/LightFM | practical matrix-factorization baselines | limited versus rich multi-stage production stacks |
| RecBole | research/benchmark implementations | benchmark protocol may differ from production |
| XGBoost/LightGBM/CatBoost rankers | GBDT learning-to-rank | preserve query groups and point-in-time features |
| FAISS/ScaNN | ANN retrieval | index is not the recommender objective |
| Elasticsearch/OpenSearch/Vespa | lexical/vector/hybrid retrieval and ranking infrastructure | validate relevance, filtering, and operational semantics |

Verify versions, licenses, supported objectives, distributed behavior, and serving constraints before selecting a stack.

## 18. Minimal NDCG implementation

```python
from __future__ import annotations

from math import log2
from typing import Sequence


def dcg_at_k(relevance: Sequence[float], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive")
    return sum(
        (2.0**rel - 1.0) / log2(rank + 1)
        for rank, rel in enumerate(relevance[:k], start=1)
    )


def ndcg_at_k(relevance: Sequence[float], k: int) -> float:
    actual = dcg_at_k(relevance, k)
    ideal = dcg_at_k(sorted(relevance, reverse=True), k)
    return 0.0 if ideal == 0.0 else actual / ideal


assert ndcg_at_k([3, 2, 1, 0], 4) == 1.0
assert 0.0 < ndcg_at_k([0, 1, 3, 2], 4) < 1.0
assert ndcg_at_k([0, 0], 2) == 0.0
```

Production evaluation must define judgments, candidate universe, query grouping, tie handling, sampling, and aggregation.

## 19. Rapid interview questions

**Why separate retrieval and ranking?** Retrieval cheaply maximizes recall over a huge corpus; ranking uses richer features and models on hundreds of candidates under latency.

**Why is an unclicked item not a negative?** The user may never have seen it, it may have appeared at a poor position, or the logging policy may not have selected it.

**Matrix factorization versus two-tower?** Both can use dot products, but two-tower models flexibly encode user/item/context features and support neural representations; both need cold-start and negative-sampling strategies.

**What makes a good candidate generator?** High relevant-item recall, low latency/cost, fresh/eligible items, catalog coverage, and useful incremental candidates.

**Why can offline NDCG fail online?** Logged-policy bias, sampled candidates, wrong relevance labels, UI effects, novelty, latency, diversity, and long-term behavior are absent or distorted.

**Pointwise versus pairwise versus listwise?** Pointwise predicts individual relevance, pairwise learns preferences between items, and listwise uses whole-list objectives/surrogates.

**How do you handle cold start?** Use content/context, onboarding, segment popularity, controlled exploration, and rapid updates; define separate new-user/item evaluation.

**How do you reduce popularity bias?** Log exposure, use exposure-aware learning, diversify candidate sources, calibrate/re-rank, explore safely, and monitor head/tail/provider exposure.

**What is counterfactual policy evaluation?** Estimate a new policy’s expected reward from data logged under another policy using propensities and assumptions such as overlap.

**How do you make a recommender safe?** Deterministic eligibility/authorization/policy filters, least data, age/context controls, harmful-content guardrails, exposure monitoring, appeals, and rollback.

## 20. Lead-level case

**Prompt:** Design recommendations for a two-sided marketplace with buyers and sellers.

Cover:

1. buyer decision and long-term marketplace objective, not CTR alone;
2. item eligibility, location, stock, price, delivery, trust, and policy filters;
3. exposure logging for buyers and opportunity/exposure metrics for sellers;
4. popularity/co-visitation/content baselines and cold-start pools;
5. candidate sources plus two-tower/ANN option with freshness/deletion SLA;
6. ranking features for relevance, conversion, quality, price, delivery, and context;
7. re-ranking for diversity, seller concentration, fairness, inventory, sponsored disclosure, and exploration;
8. time-aware offline evaluation: retrieval recall, NDCG, calibration, coverage, tail/new seller slices;
9. online randomization with purchase/retention outcome and cancellation, complaint, latency, concentration guardrails;
10. feedback loops, strategic seller behavior, fraud, delayed conversion, and network interference;
11. failure fallback to safe contextual/popularity lists and partial-source degradation;
12. model/index/feature/logging versioning, monitoring, staged rollout, and rollback.

## 21. Final checklist

- [ ] I can define users/queries, items, eligibility, exposure, action, outcome window, and constraints.
- [ ] I can explain candidate generation, ranking, and policy re-ranking.
- [ ] I can implement popularity, co-visitation, content, and collaborative baselines.
- [ ] I can compare matrix factorization, two-tower retrieval, sequence models, and rankers.
- [ ] I can explain negative sampling and implicit-feedback bias.
- [ ] I can derive Precision@K, Recall@K, MRR, MAP, and NDCG.
- [ ] I can design a time-aware offline split and candidate set without leakage.
- [ ] I can connect offline evaluation to online experiments and counterfactual assumptions.
- [ ] I can handle cold start, exploration, long tail, diversity, fairness, and feedback loops.
- [ ] I can design reliable low-latency serving, logging, fallbacks, monitoring, and rollback.

## 22. Primary references

- Google for Developers, [Recommendation systems overview](https://developers.google.com/machine-learning/recommendation/overview/types)
- TensorFlow, [TensorFlow Recommenders](https://www.tensorflow.org/recommenders)
- Google Cloud, [Two-tower retrieval reference architecture](https://cloud.google.com/architecture/implement-two-tower-retrieval-large-scale-candidate-generation)
- PyTorch, [TorchRec documentation](https://meta-pytorch.org/torchrec/)
- NVIDIA, [Merlin recommender-system framework](https://developer.nvidia.com/nvidia-merlin)
- XGBoost, [Learning to rank](https://xgboost.readthedocs.io/en/stable/tutorials/learning_to_rank.html)
- Covington, Adams, and Sargin, [Deep Neural Networks for YouTube Recommendations](https://research.google/pubs/deep-neural-networks-for-youtube-recommendations/)

Frameworks change; architecture, logging, eligibility, evaluation, and feedback-loop reasoning are the durable interview knowledge.
