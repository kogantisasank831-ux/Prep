---
layout: "week"
status: "approved"
version: "1.6.0"
last_reviewed: "2026-11-10"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "Senior Data Scientist foundation interview bank"
description: "One hundred forty guided questions for Senior Data Scientist interviews."
summary: "Practise mathematical derivations, optimization diagnostics, experimental and causal inference, leakage-safe feature engineering, clustering, anomaly evaluation, production evidence, and business impact."
permalink: "/interview-prep/roles/senior-data-scientist/"
kicker_primary: "Senior Data Scientist"
kicker_secondary: "Batches 1–7 · 140 guided questions"
current_label: "Role bank"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
question_count: 140
---
## How to use this bank

These are interview-practice prompts, not a scored learning assessment. Answer aloud before opening the revision links. A strong response should state assumptions, make a decision, explain trade-offs, and identify evidence or failure modes. Use the follow-up probe to test whether the answer survives a deeper round.

### Suggested practice loop

1. Select five questions from different sections.
2. Give a 90-second answer without notes.
3. Compare your answer with the strong-answer signals.
4. Open only the revision sheet needed for the gap.
5. Repeat the answer in 45 seconds, then record one concrete project example.

**Bank size:** 140 questions across Batches 1–7 · **Status:** Batches 1–7 approved

## SQL and data

### SDS-B1-01 — Explain `WHERE` versus `HAVING` and give a case where confusing them changes the result.

**Round:** SQL · **Depth:** Foundation

**Strong answer signals**

- `WHERE` filters rows before grouping; `HAVING` filters groups after aggregation.
- Push row predicates before aggregation for correctness and efficiency when semantics permit.
- Use a grouped metric example and state null behavior.

**Follow-up probe:** Can a `HAVING` predicate be moved safely to `WHERE`?

**Revision links:** [SQL]({{ '/interview-prep/cheat-sheets/sql/' | relative_url }})

### SDS-B1-02 — Return the latest event per user with deterministic behavior.

**Round:** SQL · **Depth:** Applied

**Strong answer signals**

- Use `ROW_NUMBER()` partitioned by user and ordered by event time descending.
- Add a stable tie-breaker such as event ID.
- Clarify whether invalid or late-arriving events are filtered before ranking.

**Follow-up probe:** How does `RANK()` change the result?

**Revision links:** [SQL]({{ '/interview-prep/cheat-sheets/sql/' | relative_url }})

### SDS-B1-03 — A retention query shows more retained users than sign-ups. Find the likely bug.

**Round:** SQL · **Depth:** Applied

**Strong answer signals**

- Check denominator grain, duplicate events, one-to-many joins, and cohort assignment.
- Aggregate events to one eligible user-period before joining.
- Validate counts at each CTE and reconcile a small cohort manually.

**Follow-up probe:** How would you define retention for users with no eligible observation window?

**Revision links:** [SQL]({{ '/interview-prep/cheat-sheets/sql/' | relative_url }})

### SDS-B1-04 — When do window functions solve a problem that `GROUP BY` cannot?

**Round:** SQL · **Depth:** Applied

**Strong answer signals**

- Windows calculate across related rows while retaining row-level detail.
- Use examples such as running totals, lag, rank, and rolling metrics.
- Specify partition, order, and frame; the default frame can surprise.

**Follow-up probe:** Why can `LAST_VALUE` return the current row rather than the partition's last row?

**Revision links:** [SQL]({{ '/interview-prep/cheat-sheets/sql/' | relative_url }})

### SDS-B1-05 — Explain SQL `NULL` and three-valued logic.

**Round:** SQL · **Depth:** Foundation

**Strong answer signals**

- `NULL` represents unknown or missing, so comparisons yield unknown rather than true/false.
- Use `IS NULL`, `IS DISTINCT FROM`, and deliberate `COALESCE` semantics.
- `NOT IN` with a null can eliminate all rows; prefer a null-safe anti-join.

**Follow-up probe:** When does replacing null with zero corrupt meaning?

**Revision links:** [SQL]({{ '/interview-prep/cheat-sheets/sql/' | relative_url }})

## Probability and inference

### SDS-B1-06 — A test is 95% sensitive and 95% specific for a 1% condition. Is a positive result 95% likely to be true?

**Round:** Probability · **Depth:** Foundation

**Strong answer signals**

- No; use Bayes and the low base rate.
- Out of 10,000, expect about 95 true positives and 495 false positives.
- Positive predictive value is about 16%, subject to the stated assumptions.

**Follow-up probe:** How does prevalence shift affect the answer?

**Revision links:** [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

### SDS-B1-07 — What does a p-value of 0.03 mean?

**Round:** Statistics · **Depth:** Foundation

**Strong answer signals**

- Assuming the null and analysis assumptions, data this extreme or more would occur with probability 0.03.
- It is not the probability the null is true or the probability results replicate.
- Interpret with effect size, interval, design, multiplicity, and practical value.

**Follow-up probe:** Would you ship a feature solely because p is below 0.05?

**Revision links:** [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

### SDS-B1-08 — Explain a 95% confidence interval to a product manager.

**Round:** Statistics · **Depth:** Applied

**Strong answer signals**

- It comes from a method that covers the fixed parameter in 95% of repeated samples under assumptions.
- Use it to communicate plausible magnitude and precision, not only significance.
- State sampling, independence, and model assumptions.

**Follow-up probe:** What does an interval crossing zero imply and not imply?

**Revision links:** [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

### SDS-B1-09 — Why does testing 100 metrics create false discoveries?

**Round:** Statistics · **Depth:** Applied

**Strong answer signals**

- Each test has a false-positive chance, so family-wise risk grows with many tests.
- Predefine primary metrics and use Bonferroni/Holm or FDR methods when appropriate.
- Treat exploratory findings as hypotheses requiring confirmation.

**Follow-up probe:** When is FDR preferable to strict family-wise error control?

**Revision links:** [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

### SDS-B1-10 — How do MCAR, MAR, and MNAR change missing-data decisions?

**Round:** Statistics · **Depth:** Applied

**Strong answer signals**

- MCAR is independent of observed/unobserved values; MAR depends on observed data; MNAR depends on missing values or unobserved causes.
- Imputation assumptions and uncertainty must match the mechanism.
- Add missingness indicators or sensitivity analysis where informative; avoid blanket deletion.

**Follow-up probe:** How would you test an operational cause of missingness?

**Revision links:** [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }}) · [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }})

## Machine learning

### SDS-B1-11 — Compare bagging and boosting.

**Round:** ML · **Depth:** Foundation

**Strong answer signals**

- Bagging trains resampled models largely in parallel and mainly reduces variance.
- Boosting adds sequential corrections and can reduce bias while building complexity.
- Compare robustness, tuning, parallelism, overfitting risk, and baseline evidence.

**Follow-up probe:** Why does diversity among ensemble members matter?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }})

### SDS-B1-12 — How do you handle a 0.5% positive class?

**Round:** ML · **Depth:** Applied

**Strong answer signals**

- Use realistic validation prevalence and precision/recall, PR-AUC, or capacity metrics.
- Consider class weights or within-fold resampling; do not rebalance the test set.
- Tune threshold and calibration against operational cost and review capacity.

**Follow-up probe:** When is anomaly detection a better framing?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

### SDS-B1-13 — Why must preprocessing be inside the cross-validation pipeline?

**Round:** Validation · **Depth:** Applied

**Strong answer signals**

- Fitting imputation, scaling, encoding, selection, or sampling on all rows leaks validation information.
- Each fold must learn transformations only from its training partition.
- Use a pipeline and the correct group/time splitter.

**Follow-up probe:** Which apparently unsupervised transformations can still leak?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }})

### SDS-B1-14 — A model has near-perfect validation performance. What is your debugging sequence?

**Round:** Validation · **Depth:** Applied

**Strong answer signals**

- Check label timing, direct target proxies, duplicates, and entity/time overlap.
- Compare with simple baselines, remove suspicious features, and inspect train/validation construction.
- Reproduce on a protected temporal or external holdout before celebrating.

**Follow-up probe:** What if performance remains high after suspect features are removed?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [SQL]({{ '/interview-prep/cheat-sheets/sql/' | relative_url }})

### SDS-B1-15 — How do you create aggregate customer features without future leakage?

**Round:** Feature engineering · **Depth:** Applied

**Strong answer signals**

- Define a snapshot time and compute only from events available before it.
- Use bounded lookback windows and point-in-time joins.
- Fit encoders/statistics within training folds and test boundary timestamps.

**Follow-up probe:** How do late-arriving events affect offline and online parity?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [SQL]({{ '/interview-prep/cheat-sheets/sql/' | relative_url }})

## Cases and production

### SDS-B1-16 — Design a churn model when the team can contact only 100,000 of 10 million customers.

**Round:** Case · **Depth:** Applied

**Strong answer signals**

- Define eligibility, weekly snapshot, horizon, intervention, and current baseline.
- Evaluate precision/recall and expected value at 100,000, calibration, time slices, and subgroup stability.
- Run randomized outreach to estimate incremental lift; high risk is not the same as persuadability.

**Follow-up probe:** How would you allocate contacts across channels and costs?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }}) · [SQL]({{ '/interview-prep/cheat-sheets/sql/' | relative_url }})

### SDS-B1-17 — How would you evaluate an anomaly detector with very few labels?

**Round:** Anomaly detection · **Depth:** Applied

**Strong answer signals**

- Use synthetic/known incidents carefully, expert review, temporal backtests, and alert-yield metrics.
- Measure precision at review capacity, coverage of known failure modes, detection delay, and false-alert burden.
- Build a feedback loop without treating reviewer decisions as perfect ground truth.

**Follow-up probe:** How would you choose a threshold during a label-scarce launch?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

### SDS-B1-18 — What can and cannot be concluded from feature importance?

**Round:** Explainability · **Depth:** Applied

**Strong answer signals**

- It describes model reliance under a method and dataset, not causal effect.
- Correlated features, scale/cardinality, and distribution affect interpretations.
- Use stability checks, permutation/SHAP with caveats, and domain validation.

**Follow-up probe:** How can removing a highly important feature improve production performance?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }})

### SDS-B1-19 — What should be monitored after deploying a classifier?

**Round:** Monitoring · **Depth:** Applied

**Strong answer signals**

- Service latency/errors/throughput; data schema, freshness, missingness, and distribution.
- Scores, thresholds, calibration, delayed performance, subgroup results, and business outcomes.
- Ownership, alert thresholds, investigation paths, rollback, and retraining gates.

**Follow-up probe:** Which signals are actionable before ground-truth labels arrive?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

### SDS-B1-20 — Defend the business impact of one Data Science project.

**Round:** Project deep dive · **Depth:** Lead

**Strong answer signals**

- State baseline, decision changed, eligible population, measurement design, and realized or estimated impact.
- Separate model contribution from product, operations, and external factors.
- Give uncertainty, limitations, adoption, costs, and what evidence is independently reproducible.

**Follow-up probe:** What counterfactual supports your impact claim?

**Revision links:** [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }}) · [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }})

## Batch 2 · Deep learning

### SDS-B2-01 — What does a neuron compute, and why is a nonlinear activation necessary?

**Round:** Deep learning · **Depth:** Foundation

**Strong answer signals**

- A neuron applies an affine transformation `wᵀx+b` followed by an activation.
- Without nonlinearity, stacked linear layers collapse to one linear transformation.
- Activation choice affects gradient flow, output range, sparsity, and task compatibility.

**Follow-up probe:** Where would sigmoid, softmax, ReLU, and GELU typically appear?

**Revision links:** [Deep learning]({{ '/interview-prep/cheat-sheets/deep-learning-neural-networks/' | relative_url }})

### SDS-B2-02 — Choose among binary cross-entropy, categorical cross-entropy, and MSE.

**Round:** Loss functions · **Depth:** Foundation

**Strong answer signals**

- Binary cross-entropy fits independent binary labels with logits/sigmoid; categorical cross-entropy fits one mutually exclusive class with softmax logits.
- MSE is common for continuous regression and is sensitive to large errors.
- Match output shape, target encoding, likelihood assumptions, and numerical-stability APIs.

**Follow-up probe:** Why should loss functions often consume logits rather than probabilities?

**Revision links:** [Deep learning]({{ '/interview-prep/cheat-sheets/deep-learning-neural-networks/' | relative_url }})

### SDS-B2-03 — Explain backpropagation to a mathematically comfortable interviewer.

**Round:** Backpropagation · **Depth:** Applied

**Strong answer signals**

- It applies the chain rule through the computation graph from loss to parameters.
- Local derivatives are multiplied/accumulated along paths; autodiff records operations and propagates vector-Jacobian products.
- Gradient computation is separate from the optimizer update and can fail through saturation, detachment, or numerical instability.

**Follow-up probe:** What is the difference between a gradient and a parameter update?

**Revision links:** [Deep learning]({{ '/interview-prep/cheat-sheets/deep-learning-neural-networks/' | relative_url }})

### SDS-B2-04 — Compare weight decay, dropout, early stopping, and data augmentation.

**Round:** Regularization · **Depth:** Applied

**Strong answer signals**

- Weight decay penalizes/shrinks parameters; dropout stochastically removes activations during training.
- Early stopping limits fitting time using validation evidence; augmentation encodes label-preserving transformations.
- They address different failure modes and must be validated for the data and architecture.

**Follow-up probe:** Why can inappropriate augmentation reduce generalization?

**Revision links:** [Deep learning]({{ '/interview-prep/cheat-sheets/deep-learning-neural-networks/' | relative_url }})

### SDS-B2-05 — Why do training and evaluation modes matter?

**Round:** Training behavior · **Depth:** Applied

**Strong answer signals**

- Dropout is active only during training; BatchNorm updates/uses statistics differently.
- Evaluation should disable gradient tracking where appropriate and use deterministic preprocessing.
- A mode mismatch causes unstable or biased validation and production predictions.

**Follow-up probe:** Which layers remain numerically active in both modes?

**Revision links:** [Deep learning]({{ '/interview-prep/cheat-sheets/deep-learning-neural-networks/' | relative_url }})

## Batch 2 · NLP

### SDS-B2-06 — Compare bag-of-words, TF-IDF, static embeddings, and contextual embeddings.

**Round:** NLP · **Depth:** Foundation

**Strong answer signals**

- Bag-of-words counts terms; TF-IDF downweights globally common terms.
- Static embeddings assign one vector per token; contextual embeddings change with surrounding text.
- Complexity, data, semantics, latency, interpretability, and transfer determine the choice.

**Follow-up probe:** Which representation would you try first for a small labeled text dataset?

**Revision links:** [NLP]({{ '/interview-prep/cheat-sheets/nlp/' | relative_url }})

### SDS-B2-07 — Compare word, character, and subword tokenization.

**Round:** Tokenization · **Depth:** Applied

**Strong answer signals**

- Word tokens are interpretable but suffer large vocabularies and unknown words.
- Characters handle arbitrary text but produce long sequences; subwords balance vocabulary and sequence length.
- Evaluate domain terms, morphology, languages, noise, cost, and checkpoint compatibility.

**Follow-up probe:** Why might a code or medical tokenizer outperform a general tokenizer?

**Revision links:** [NLP]({{ '/interview-prep/cheat-sheets/nlp/' | relative_url }})

### SDS-B2-08 — Design evaluation for an imbalanced multilabel text classifier.

**Round:** Classification · **Depth:** Applied

**Strong answer signals**

- Use per-label and macro/micro precision, recall, F1, PR curves, and calibration.
- Tune label-specific thresholds with costs and capacity on validation data.
- Audit rare labels, co-occurrence, unknown cases, source/time/language slices, and annotation quality.

**Follow-up probe:** Why can micro F1 hide poor minority-label behavior?

**Revision links:** [NLP]({{ '/interview-prep/cheat-sheets/nlp/' | relative_url }})

### SDS-B2-09 — Why is entity-level F1 preferred over token accuracy for NER?

**Round:** Sequence labeling · **Depth:** Applied

**Strong answer signals**

- Token accuracy is dominated by non-entity tokens and can reward broken spans.
- Entity-level scoring checks declared boundary and type correctness.
- Report precision/recall by entity type and define exact versus partial/nested matching.

**Follow-up probe:** How would annotation disagreement affect the apparent ceiling?

**Revision links:** [NLP]({{ '/interview-prep/cheat-sheets/nlp/' | relative_url }})

### SDS-B2-10 — How do duplicates and templated text distort NLP validation?

**Round:** Data quality · **Depth:** Applied

**Strong answer signals**

- Near-duplicates across splits let the model memorize lexical patterns and inflate performance.
- Templates can make random splits easier than future/source-generalization conditions.
- Deduplicate with normalized and semantic checks, group by source/entity/template, and use temporal holdouts.

**Follow-up probe:** What useful signal might aggressive deduplication accidentally remove?

**Revision links:** [NLP]({{ '/interview-prep/cheat-sheets/nlp/' | relative_url }})

## Batch 2 · Transformers

### SDS-B2-11 — Why divide attention logits by the square root of key dimension?

**Round:** Attention · **Depth:** Foundation

**Strong answer signals**

- Dot-product variance grows with dimension under common assumptions.
- Large logits saturate softmax, producing tiny gradients and unstable learning.
- Scaling keeps scores in a more useful range before masking and softmax.

**Follow-up probe:** Why must masked positions be excluded before softmax?

**Revision links:** [Transformers]({{ '/interview-prep/cheat-sheets/transformers/' | relative_url }})

### SDS-B2-12 — Compare self-attention and cross-attention.

**Round:** Architecture · **Depth:** Foundation

**Strong answer signals**

- Self-attention derives Q, K, and V from the same sequence to relate its tokens.
- Cross-attention uses queries from one sequence and keys/values from another source.
- Masks, shapes, and computational cost depend on the two sequence lengths.

**Follow-up probe:** Where does cross-attention appear in encoder-decoder models?

**Revision links:** [Transformers]({{ '/interview-prep/cheat-sheets/transformers/' | relative_url }})

### SDS-B2-13 — Why do transformers need positional information?

**Round:** Position · **Depth:** Applied

**Strong answer signals**

- Attention without position is permutation-equivariant and cannot distinguish order by itself.
- Absolute, relative, or rotary schemes inject order/distance in different ways.
- Extrapolation beyond trained lengths and implementation compatibility must be evaluated.

**Follow-up probe:** Why does a larger configured context not prove long-range reasoning?

**Revision links:** [Transformers]({{ '/interview-prep/cheat-sheets/transformers/' | relative_url }})

### SDS-B2-14 — Choose an architecture for classification, generation, and translation.

**Round:** Model families · **Depth:** Applied

**Strong answer signals**

- Encoder-only for bidirectional representations/classification, decoder-only for causal generation, encoder-decoder for explicit source-to-target mapping.
- Compare pretrained checkpoints, data, output constraints, latency, and serving ecosystem.
- Validate on the actual task; family labels are strong priors, not guarantees.

**Follow-up probe:** When can a generative model be wasteful for classification?

**Revision links:** [Transformers]({{ '/interview-prep/cheat-sheets/transformers/' | relative_url }}) · [NLP]({{ '/interview-prep/cheat-sheets/nlp/' | relative_url }})

### SDS-B2-15 — Why is autoregressive generation slow even with a KV cache?

**Round:** Inference · **Depth:** Applied

**Strong answer signals**

- Output tokens are generated sequentially, limiting parallelism across time.
- Each step reads model weights and KV state; memory bandwidth and batching matter.
- KV cache removes prefix recomputation but consumes memory and does not eliminate per-token layer computation.

**Follow-up probe:** How do output length and concurrency interact?

**Revision links:** [Transformers]({{ '/interview-prep/cheat-sheets/transformers/' | relative_url }})

## Batch 2 · LLM and Generative AI

### SDS-B2-16 — Explain temperature and top-p without claiming they improve knowledge.

**Round:** Generation · **Depth:** Foundation

**Strong answer signals**

- Temperature rescales logits; lower values sharpen and higher values flatten the distribution.
- Top-p restricts sampling to a probability-mass nucleus that changes by step.
- They alter variability and determinism, not training data, grounding, or factual capability.

**Follow-up probe:** Why can temperature zero still produce wrong answers?

**Revision links:** [LLM and Generative AI]({{ '/interview-prep/cheat-sheets/llm-generative-ai/' | relative_url }})

### SDS-B2-17 — When would you use few-shot prompting, RAG, or fine-tuning?

**Round:** Model adaptation · **Depth:** Applied

**Strong answer signals**

- Few-shot prompting teaches a pattern within context; RAG supplies current/private evidence; fine-tuning changes learned behavior.
- Diagnose the failure and start with the least complex intervention.
- Compare quality, freshness, data/privacy, latency, cost, serving, and rollback.

**Follow-up probe:** Which one best addresses a new output style versus new facts?

**Revision links:** [LLM and Generative AI]({{ '/interview-prep/cheat-sheets/llm-generative-ai/' | relative_url }})

### SDS-B2-18 — How do you evaluate hallucination or factuality?

**Round:** Evaluation · **Depth:** Applied

**Strong answer signals**

- Define claim-level support against authoritative evidence and separate unsupported, contradicted, and unverifiable claims.
- Use representative and adversarial cases, deterministic checks where possible, and blinded human review.
- Measure citation correctness/coverage, abstention, task success, and severity-weighted failures; judges need calibration.

**Follow-up probe:** How can a fluent answer score well while being unsafe?

**Revision links:** [LLM and Generative AI]({{ '/interview-prep/cheat-sheets/llm-generative-ai/' | relative_url }})

### SDS-B2-19 — Design an LLM-based document classifier and decide whether an LLM is justified.

**Round:** Case · **Depth:** Applied

**Strong answer signals**

- Define labels, unknown/escalation behavior, privacy, latency, throughput, and current baseline.
- Compare TF-IDF/linear, encoder classifier, and prompted LLM on the same cases and costs.
- Use structured output plus semantic validation, caching/batching where safe, monitoring, human review, and rollback.

**Follow-up probe:** What result would make you deploy the classical model instead?

**Revision links:** [NLP]({{ '/interview-prep/cheat-sheets/nlp/' | relative_url }}) · [LLM and Generative AI]({{ '/interview-prep/cheat-sheets/llm-generative-ai/' | relative_url }})

### SDS-B2-20 — Explain an LLM experiment so the interviewer can separate evidence from enthusiasm.

**Round:** Project deep dive · **Depth:** Lead

**Strong answer signals**

- State the decision, baseline, dataset/version, model/prompt/config, metrics, and representative failures.
- Quantify quality, safety, latency, cost, and uncertainty; describe human/judge procedures and limits.
- Explain alternatives, deployment boundary, rollback, and what was not proven.

**Follow-up probe:** Which claim in your story is most vulnerable to evaluation leakage?

**Revision links:** [LLM and Generative AI]({{ '/interview-prep/cheat-sheets/llm-generative-ai/' | relative_url }})


## Batch 3 · Embeddings and vector search

### SDS-B3-01 — Compare cosine similarity, dot product, and Euclidean distance for retrieval.

**Round:** Representation fundamentals · **Depth:** Foundation

**Strong answer signals**

- Cosine measures direction, dot product includes vector magnitude, and Euclidean distance measures geometric separation.
- For L2-normalized vectors, cosine equals dot product and induces a ranking closely related to Euclidean distance.
- Use the metric expected during model training and supported consistently by the index; validate ranking on task data.

**Follow-up probe:** How can missing normalization change dot-product rankings?

**Revision links:** [Embeddings and vector search]({{ '/interview-prep/cheat-sheets/embeddings-vector-search/' | relative_url }})

### SDS-B3-02 — Explain when to use a bi-encoder and when to add a cross-encoder.

**Round:** Retrieval modeling · **Depth:** Applied

**Strong answer signals**

- A bi-encoder embeds queries and documents independently, enabling reusable document vectors and scalable candidate retrieval.
- A cross-encoder jointly scores each query-document pair and usually improves relevance at much higher per-pair cost.
- Use staged retrieval: broad bi-encoder candidates followed by bounded cross-encoder reranking, tuned against recall and latency.

**Follow-up probe:** What training negatives would make the bi-encoder more useful before reranking?

**Revision links:** [Embeddings and vector search]({{ '/interview-prep/cheat-sheets/embeddings-vector-search/' | relative_url }})

### SDS-B3-03 — Combine lexical and dense retrieval without assuming their scores are comparable.

**Round:** Hybrid retrieval · **Depth:** Applied

**Strong answer signals**

- Sparse and dense scores have different scales and distributions, so raw-score addition requires calibration.
- Rank-fusion methods such as reciprocal-rank fusion combine order rather than incompatible raw values.
- Evaluate lexical, dense, and fused systems by query slice, then rerank and deduplicate only when incremental gain is measured.

**Follow-up probe:** Which queries are likely to benefit most from the sparse branch?

**Revision links:** [Embeddings and vector search]({{ '/interview-prep/cheat-sheets/embeddings-vector-search/' | relative_url }})

### SDS-B3-04 — Evaluate an approximate-nearest-neighbor configuration.

**Round:** Retrieval evaluation · **Depth:** Advanced

**Strong answer signals**

- Use exact nearest-neighbor results as ground truth and compute ANN recall@K on representative queries.
- Measure latency percentiles, throughput, memory, build time, and behavior under filters and concurrency.
- Sweep parameters reproducibly and select a Pareto-appropriate setting rather than optimizing recall or latency alone.

**Follow-up probe:** Why can a small average recall loss still be unacceptable?

**Revision links:** [Embeddings and vector search]({{ '/interview-prep/cheat-sheets/embeddings-vector-search/' | relative_url }})

### SDS-B3-05 — Use maximal marginal relevance to improve result diversity.

**Round:** Ranking · **Depth:** Applied

**Strong answer signals**

- MMR balances query relevance against similarity to already selected items, reducing redundant evidence.
- Tune the relevance-diversity trade-off and candidate pool on tasks where multiple aspects or sources matter.
- Measure coverage and answer quality because diversity can remove useful corroboration when overapplied.

**Follow-up probe:** How would you distinguish healthy corroboration from wasteful duplication?

**Revision links:** [Embeddings and vector search]({{ '/interview-prep/cheat-sheets/embeddings-vector-search/' | relative_url }})


## Batch 3 · Document ingestion, chunking, and indexing

### SDS-B3-06 — Choose the chunking unit and overlap for a new corpus.

**Round:** Data preparation · **Depth:** Applied

**Strong answer signals**

- Start from document structure, query granularity, evidence span, embedding context limits, and citation needs.
- Compare structural or semantic chunks with fixed token windows; add overlap only where boundary loss justifies duplication.
- Evaluate retrieval and downstream answers by document type while monitoring index growth and redundant candidates.

**Follow-up probe:** What evidence would tell you that chunks are too small?

**Revision links:** [Ingestion, chunking, and indexing]({{ '/interview-prep/cheat-sheets/document-ingestion-chunking-indexing/' | relative_url }})

### SDS-B3-07 — Prevent duplicate and near-duplicate documents from biasing retrieval evaluation.

**Round:** Dataset quality · **Depth:** Advanced

**Strong answer signals**

- Create content and source-aware fingerprints before splitting or indexing, with a documented near-duplicate policy.
- Group versions and related documents so train, tuning, and test queries do not leak equivalent evidence across boundaries.
- Report duplicate prevalence and evaluate both deduplicated relevance and production behavior where legitimate versions remain.

**Follow-up probe:** How can duplicated chunks inflate both retrieval and generation scores?

**Revision links:** [Ingestion, chunking, and indexing]({{ '/interview-prep/cheat-sheets/document-ingestion-chunking-indexing/' | relative_url }})

### SDS-B3-08 — Explain parent-child retrieval and when it helps.

**Round:** Chunking architecture · **Depth:** Applied

**Strong answer signals**

- Index small child chunks for precise matching while returning a larger parent or selected neighbors for complete context.
- Preserve deterministic relationships and provenance so expanded context remains traceable and permission-correct.
- Evaluate evidence completeness, noise, token cost, and duplicates against direct large-chunk and small-chunk baselines.

**Follow-up probe:** When can parent expansion reduce answer quality?

**Revision links:** [Ingestion, chunking, and indexing]({{ '/interview-prep/cheat-sheets/document-ingestion-chunking-indexing/' | relative_url }})

### SDS-B3-09 — Represent tables and metadata for retrieval experiments.

**Round:** Feature design · **Depth:** Advanced

**Strong answer signals**

- Preserve headers, units, row and column relationships, source coordinates, and surrounding section context.
- Compare structured serialization, lexical fields, dense representations, and table-specific or multimodal approaches by question type.
- Use metadata for filtering and analysis without leaking target answers or sensitive attributes into inappropriate features.

**Follow-up probe:** Why does flattening every table into plain text often fail?

**Revision links:** [Ingestion, chunking, and indexing]({{ '/interview-prep/cheat-sheets/document-ingestion-chunking-indexing/' | relative_url }})

### SDS-B3-10 — Detect corpus and ingestion drift after launch.

**Round:** Data monitoring · **Depth:** Advanced

**Strong answer signals**

- Monitor source counts, update and deletion lag, parser failures, language and document-type mix, chunk-size distributions, and embedding norms.
- Compare retrieval coverage and quality by stable slices, linking changes to parser, chunker, model, and index versions.
- Investigate with source samples and reconciliation before interpreting answer-quality drift as a model problem.

**Follow-up probe:** Which drift signal might reveal a parser regression before evaluation labels arrive?

**Revision links:** [Ingestion, chunking, and indexing]({{ '/interview-prep/cheat-sheets/document-ingestion-chunking-indexing/' | relative_url }})


## Batch 3 · RAG architecture, retrieval, and generation

### SDS-B3-11 — Design a baseline and ablation plan for a RAG experiment.

**Round:** Experimental design · **Depth:** Advanced

**Strong answer signals**

- Start with simple lexical or dense retrieval and a fixed generation setup before adding rewriting, fusion, reranking, or compression.
- Change one stage at a time, preserve candidate and prompt traces, and evaluate component plus end-to-end outcomes on the same dataset.
- Report effect by slice with latency, token, and cost changes so gains are attributable and operationally meaningful.

**Follow-up probe:** Why is comparing two fully different pipelines a weak experiment?

**Revision links:** [RAG architecture]({{ '/interview-prep/cheat-sheets/rag-architecture-retrieval-generation/' | relative_url }}) · [RAG evaluation]({{ '/interview-prep/cheat-sheets/rag-evaluation-security-production/' | relative_url }})

### SDS-B3-12 — Tune `fetch_k` and final `top_k` using evidence rather than defaults.

**Round:** Retrieval tuning · **Depth:** Applied

**Strong answer signals**

- Increase `fetch_k` to test whether broader candidates improve recall and reranking opportunities.
- Tune final `top_k` for evidence coverage against duplication, context noise, token cost, and latency.
- Plot retrieval and answer metrics jointly by query slice; choose a stable operating point rather than the highest isolated score.

**Follow-up probe:** What result would show that the reranker, not `fetch_k`, is the bottleneck?

**Revision links:** [RAG architecture]({{ '/interview-prep/cheat-sheets/rag-architecture-retrieval-generation/' | relative_url }})

### SDS-B3-13 — Evaluate whether a reranker provides real incremental value.

**Round:** Model evaluation · **Depth:** Advanced

**Strong answer signals**

- Hold the retriever candidate set fixed and compare ranking metrics plus downstream grounded-answer metrics with and without reranking.
- Analyze gains by query type, candidate depth, and hard-negative class while including latency and cost confidence intervals.
- Check score stability, truncation effects, domain mismatch, and calibration before setting decision thresholds.

**Follow-up probe:** Why might NDCG improve without improving final answer quality?

**Revision links:** [Embeddings and vector search]({{ '/interview-prep/cheat-sheets/embeddings-vector-search/' | relative_url }}) · [RAG architecture]({{ '/interview-prep/cheat-sheets/rag-architecture-retrieval-generation/' | relative_url }})

### SDS-B3-14 — Measure groundedness, answer relevance, and citation correctness separately.

**Round:** Generation evaluation · **Depth:** Advanced

**Strong answer signals**

- Groundedness asks whether claims are supported by supplied evidence; answer relevance asks whether the response addresses the question.
- Citation correctness verifies that each cited passage entails the nearby claim, while citation completeness checks supported claims are cited.
- Use claim-level labels and report dimensions separately because one aggregate score hides distinct failure modes.

**Follow-up probe:** Can an answer be fully grounded but still be poor? Give an example.

**Revision links:** [RAG evaluation and production]({{ '/interview-prep/cheat-sheets/rag-evaluation-security-production/' | relative_url }})

### SDS-B3-15 — Calibrate an abstention threshold for answerable and unanswerable questions.

**Round:** Decision thresholds · **Depth:** Advanced

**Strong answer signals**

- Define evidence and answerability signals, then label both answerable and unanswerable cases across risk and query slices.
- Choose thresholds from the relative cost of unsupported answers and unnecessary abstentions, not accuracy alone.
- Validate calibration on a protected set and monitor coverage, selective risk, false answers, and false abstentions after launch.

**Follow-up probe:** How would threshold policy differ for employee search versus medical guidance?

**Revision links:** [RAG architecture]({{ '/interview-prep/cheat-sheets/rag-architecture-retrieval-generation/' | relative_url }}) · [RAG evaluation]({{ '/interview-prep/cheat-sheets/rag-evaluation-security-production/' | relative_url }})


## Batch 3 · RAG evaluation, security, and production

### SDS-B3-16 — Choose among Precision@K, Recall@K, MRR, MAP, and NDCG.

**Round:** Retrieval metrics · **Depth:** Foundation

**Strong answer signals**

- Precision@K measures relevance concentration, while Recall@K measures how much known relevant evidence is recovered.
- MRR emphasizes the first relevant result; MAP averages precision at relevant ranks; NDCG supports graded relevance and position discounting.
- Choose metrics from user behavior and label completeness, and report multiple metrics when they capture different costs.

**Follow-up probe:** Why can Recall@K be misleading when relevance labels are incomplete?

**Revision links:** [RAG evaluation and production]({{ '/interview-prep/cheat-sheets/rag-evaluation-security-production/' | relative_url }})

### SDS-B3-17 — Validate an LLM-as-judge before using it for release decisions.

**Round:** Evaluation methodology · **Depth:** Advanced

**Strong answer signals**

- Define a rubric with examples and blind candidate identity, then compare judge outputs with qualified human labels.
- Measure agreement, bias by model or style, order sensitivity, variance, and failure on adversarial or unsupported answers.
- Use repeated or panel judging only when justified, keep judge versions fixed, and retain human review for consequential slices.

**Follow-up probe:** What would make high judge-human agreement still untrustworthy?

**Revision links:** [RAG evaluation and production]({{ '/interview-prep/cheat-sheets/rag-evaluation-security-production/' | relative_url }})

### SDS-B3-18 — Compare two RAG candidates statistically across a fixed evaluation set.

**Round:** Statistical inference · **Depth:** Advanced

**Strong answer signals**

- Use paired per-query outcomes because both systems answer the same cases, and retain slice membership.
- Report effect sizes and uncertainty through appropriate paired bootstrap or permutation methods, not only a p-value.
- Account for multiple metrics, judge noise, missing outputs, and practical thresholds before claiming improvement.

**Follow-up probe:** Why is an unpaired test wasteful in this comparison?

**Revision links:** [RAG evaluation and production]({{ '/interview-prep/cheat-sheets/rag-evaluation-security-production/' | relative_url }})

### SDS-B3-19 — Build an adversarial evaluation set for RAG security.

**Round:** Security evaluation · **Depth:** Advanced

**Strong answer signals**

- Cover poisoned documents, indirect prompt injection, cross-tenant requests, sensitive-data extraction, malicious citations, encoding tricks, and tool escalation.
- Generate cases from the real trust boundaries and verify both attack success and benign-task utility to avoid unusable defenses.
- Version attacks and controls, include adaptive variants, and route consequential findings to security owners rather than treating one scan as proof.

**Follow-up probe:** How would you test that a defense is not merely overfitted to known attack phrases?

**Revision links:** [RAG security and production]({{ '/interview-prep/cheat-sheets/rag-evaluation-security-production/' | relative_url }})

### SDS-B3-20 — Diagnose a production decline in grounded-answer rate.

**Round:** Monitoring and incident analysis · **Depth:** Leadership

**Strong answer signals**

- Decompose the metric by query, tenant, language, source, document type, and version instead of inspecting only the aggregate.
- Trace ingestion freshness, retrieval recall, rank distribution, context composition, prompt and model versions, and judge drift.
- Reproduce cases with preserved artifacts, compare a known-good candidate, and separate real quality change from measurement change.

**Follow-up probe:** What evidence would show that the evaluator, not the RAG system, caused the apparent decline?

**Revision links:** [RAG evaluation and production]({{ '/interview-prep/cheat-sheets/rag-evaluation-security-production/' | relative_url }}) · [Ingestion and indexing]({{ '/interview-prep/cheat-sheets/document-ingestion-chunking-indexing/' | relative_url }})

## Agent behavior and experimental design

### SDS-B4-01 — Compare a deterministic workflow with a bounded agent for the same analytical task.

**Round:** Experimental design · **Depth:** Applied

**Strong answer signals**

- Use identical representative cases and define task quality, failure severity, latency, token or tool cost, and human effort.
- Analyze paired outcomes and slices, including abstention, invalid actions, and long-tail cases hidden by averages.
- Prefer the simpler workflow unless the agent's adaptive behavior yields a practically meaningful gain within risk limits.

**Follow-up probe:** How would you prevent evaluator bias toward longer agent answers?

**Revision links:** [Agent fundamentals]({{ '/interview-prep/cheat-sheets/agent-fundamentals-workflow-patterns/' | relative_url }})

### SDS-B4-02 — Evaluate a model-based router that selects one of five specialist workflows.

**Round:** Classification and routing · **Depth:** Advanced

**Strong answer signals**

- Define mutually understandable route labels, ambiguous or multi-intent cases, and an abstain or fallback path.
- Report confusion by route, cost-sensitive errors, calibration, coverage, downstream task success, latency, and drift.
- Compare against rules and a lightweight classifier; inspect whether routing gains survive end-to-end evaluation.

**Follow-up probe:** When can high routing accuracy still produce poor product outcomes?

**Revision links:** [Agent fundamentals]({{ '/interview-prep/cheat-sheets/agent-fundamentals-workflow-patterns/' | relative_url }})

### SDS-B4-03 — Test whether long-term memory improves a personal assistant.

**Round:** Memory evaluation · **Depth:** Advanced

**Strong answer signals**

- Define useful recall, correction, contradiction, staleness, provenance, privacy, and deletion behavior before measuring answer preference.
- Compare no-memory, session-only, and long-term-memory variants on consented longitudinal cases.
- Measure both utility and harms such as irrelevant personalization, sensitive recall, cross-user leakage, and persistent false facts.

**Follow-up probe:** How would you distinguish retrieval failure from a model ignoring correctly retrieved memory?

**Revision links:** [Agent fundamentals]({{ '/interview-prep/cheat-sheets/agent-fundamentals-workflow-patterns/' | relative_url }})

### SDS-B4-04 — Analyze tool-selection quality for an agent with overlapping tools.

**Round:** Agent evaluation · **Depth:** Applied

**Strong answer signals**

- Label acceptable tool sets, necessary order, argument constraints, and cases where no tool should be called.
- Measure selection precision and recall, invalid calls, redundant calls, argument accuracy, recovery, task success, and cost.
- Slice by intent ambiguity and tool-description similarity, then improve contracts or routing rather than only changing prompts.

**Follow-up probe:** How would you score a successful answer that used an unnecessary sensitive tool?

**Revision links:** [Agent fundamentals]({{ '/interview-prep/cheat-sheets/agent-fundamentals-workflow-patterns/' | relative_url }}) · [Protocols and reliability]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }})

### SDS-B4-05 — Determine whether a multi-agent design outperforms one agent with tools.

**Round:** Ablation study · **Depth:** Advanced

**Strong answer signals**

- Hold model, tools, information, budgets, and evaluation cases constant while changing coordination design.
- Compare paired task success, handoff loss, duplicated work, latency, cost, variance, safety, and recovery.
- Inspect trajectories to identify which specialist or handoff creates value; reject complexity without a robust slice-level gain.

**Follow-up probe:** What confound appears if the multi-agent design receives a larger token budget?

**Revision links:** [Agent fundamentals]({{ '/interview-prep/cheat-sheets/agent-fundamentals-workflow-patterns/' | relative_url }})

## LangGraph state, replay, and measurement

### SDS-B4-06 — Design a LangGraph state schema for an iterative data-analysis assistant.

**Round:** State modeling · **Depth:** Applied

**Strong answer signals**

- Separate request context, hypotheses, evidence, executed analysis references, validation results, budgets, and final conclusion.
- Store provenance and stable artifact IDs rather than copying full datasets into checkpoints.
- Specify reducers for accumulated evidence and errors, with deterministic semantics under parallel updates.

**Follow-up probe:** Which state fields should be excluded from model context even though the runtime needs them?

**Revision links:** [LangGraph deep dive]({{ '/interview-prep/cheat-sheets/langgraph-deep-dive/' | relative_url }})

### SDS-B4-07 — Results vary depending on the completion order of parallel LangGraph workers. Diagnose it.

**Round:** Debugging · **Depth:** Advanced

**Strong answer signals**

- Check for non-associative reducers, list-order dependence, shared mutable data, last-write-wins fields, and nondeterministic prompts.
- Replay the same worker outputs in different orders and compare state deltas to isolate orchestration from model variance.
- Define order-independent aggregation or an explicit stable sort and add property-based reducer tests.

**Follow-up probe:** Why must a parallel reducer ideally be associative and commutative?

**Revision links:** [LangGraph deep dive]({{ '/interview-prep/cheat-sheets/langgraph-deep-dive/' | relative_url }})

### SDS-B4-08 — Evaluate recovery after interrupting and resuming a LangGraph workflow.

**Round:** Reliability experiment · **Depth:** Advanced

**Strong answer signals**

- Inject pauses and crashes before, during, and after model, tool, and side-effect boundaries.
- Compare final state, tool-call counts, external records, latency, and errors against uninterrupted baseline runs.
- Verify authorization recheck, checkpoint integrity, idempotency, expiry, and behavior after code or schema version changes.

**Follow-up probe:** Which crash point is most likely to reveal duplicate side effects?

**Revision links:** [LangGraph deep dive]({{ '/interview-prep/cheat-sheets/langgraph-deep-dive/' | relative_url }}) · [Protocols and reliability]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }})

### SDS-B4-09 — Measure whether node caching helps a LangGraph application without corrupting results.

**Round:** Performance evaluation · **Depth:** Advanced

**Strong answer signals**

- Identify pure or safely cacheable nodes and include all behavior-changing inputs, model, prompt, tool, policy, and data versions in the key.
- Compare hit rate, latency, tokens, cost, freshness, and output equivalence against an uncached baseline.
- Test invalidation, tenant isolation, sensitive-data handling, stampedes, and stale or failed-result caching.

**Follow-up probe:** Why is a semantic response cache riskier than deterministic node-result caching?

**Revision links:** [LangGraph deep dive]({{ '/interview-prep/cheat-sheets/langgraph-deep-dive/' | relative_url }})

### SDS-B4-10 — Build a trajectory analysis for LangGraph failures.

**Round:** Observability and analytics · **Depth:** Advanced

**Strong answer signals**

- Capture versioned nodes, routes, state deltas, tool calls, interrupts, errors, budgets, and final outcomes with privacy-safe identifiers.
- Derive route frequency, loop depth, recovery rate, tool error, abandonment, latency, and cost by task slice.
- Cluster recurring paths and compare good and bad paired cases while retaining inspectable examples for causal diagnosis.

**Follow-up probe:** How would you avoid treating a common trajectory as proof that it is optimal?

**Revision links:** [LangGraph deep dive]({{ '/interview-prep/cheat-sheets/langgraph-deep-dive/' | relative_url }})

## Framework comparison and benchmark design

### SDS-B4-11 — Design a fair benchmark for two agent frameworks.

**Round:** Benchmarking · **Depth:** Advanced

**Strong answer signals**

- Implement the same representative tasks, models, tools, budgets, concurrency, persistence needs, and failure injections.
- Measure correctness, trajectory, recovery, developer effort, latency, cost, observability, and operational complexity.
- Separate framework capability from implementation quality through review, repeated runs, and transparent configuration.

**Follow-up probe:** Why is a single happy-path latency benchmark insufficient?

**Revision links:** [Framework comparison]({{ '/interview-prep/cheat-sheets/agent-frameworks-libraries-comparison/' | relative_url }})

### SDS-B4-12 — Explain when DSPy complements rather than replaces an agent orchestration framework.

**Round:** LM program optimization · **Depth:** Applied

**Strong answer signals**

- DSPy optimizes modular LM programs against metrics; orchestration controls state, branches, tools, persistence, and recovery.
- Use DSPy for measurable prompt or module behavior inside a stable workflow when training and evaluation data are adequate.
- Prevent evaluation leakage and verify optimized modules end to end because local metric gains can change system behavior.

**Follow-up probe:** What dataset split is required before optimizing a module against an evaluation metric?

**Revision links:** [Framework comparison]({{ '/interview-prep/cheat-sheets/agent-frameworks-libraries-comparison/' | relative_url }})

### SDS-B4-13 — Choose between LlamaIndex, Haystack, and a general agent framework for a research assistant.

**Round:** Data and architecture · **Depth:** Applied

**Strong answer signals**

- Decompose ingestion, indexing, retrieval, synthesis, dynamic planning, persistence, and production constraints.
- Prioritize a data or retrieval framework when evidence pipelines dominate; add bounded agent control only for genuinely adaptive work.
- Test retrieval and end-to-end quality separately so orchestration changes do not hide data-pipeline regressions.

**Follow-up probe:** Which requirement makes explicit graph orchestration materially useful?

**Revision links:** [Framework comparison]({{ '/interview-prep/cheat-sheets/agent-frameworks-libraries-comparison/' | relative_url }})

### SDS-B4-14 — A framework comparison changes both the runtime and the model provider. Explain the problem.

**Round:** Experimental validity · **Depth:** Applied

**Strong answer signals**

- Model capability, tool-calling behavior, tokenization, latency, and provider policies are confounded with framework effects.
- Hold model and settings constant where possible, or use a factorial design and report interactions explicitly.
- Normalize budgets and tool contracts, repeat stochastic runs, and retain raw trajectories for error analysis.

**Follow-up probe:** How would you compare frameworks that do not support the same provider?

**Revision links:** [Framework comparison]({{ '/interview-prep/cheat-sheets/agent-frameworks-libraries-comparison/' | relative_url }})

### SDS-B4-15 — Validate a migration from one agent framework to another.

**Round:** Regression evaluation · **Depth:** Advanced

**Strong answer signals**

- Replay a frozen representative suite and compare paired task outcomes, trajectories, safety, latency, cost, and escalation.
- Include in-flight state, tool errors, interrupts, retries, long contexts, and adversarial cases rather than only fresh requests.
- Set equivalence or non-inferiority bounds for critical slices and inspect disagreements before rollout.

**Follow-up probe:** When is exact trajectory equality neither possible nor desirable?

**Revision links:** [Framework comparison]({{ '/interview-prep/cheat-sheets/agent-frameworks-libraries-comparison/' | relative_url }})

## Protocol, reliability, and evaluation science

### SDS-B4-16 — Design data collection for evaluating MCP and A2A integrations.

**Round:** Evaluation design · **Depth:** Advanced

**Strong answer signals**

- Log capability or agent version, identity decision, request schema, latency, error class, retries, artifacts, and final task outcome.
- Use privacy minimization and stable correlation IDs without storing unrestricted sensitive payloads.
- Build contract, interoperability, authorization, malformed-input, timeout, and partial-result cases for each boundary.

**Follow-up probe:** Which metric distinguishes protocol success from end-to-end task success?

**Revision links:** [Protocols and reliability]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }})

### SDS-B4-17 — Define reliability metrics for a tool-using agent.

**Round:** Production analytics · **Depth:** Applied

**Strong answer signals**

- Measure task completion, valid tool-call rate, timeout and error rates, retry amplification, duplicate side effects, and recovery.
- Add latency distributions, queue time, saturation, circuit-breaker state, cost, and safe-degradation or escalation rates.
- Slice by tool, tenant, task, risk, version, and dependency so aggregates do not hide concentrated failures.

**Follow-up probe:** Which leading indicator would warn that retries are becoming harmful?

**Revision links:** [Protocols and reliability]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }})

### SDS-B4-18 — Calibrate an LLM judge for agent trajectories.

**Round:** Evaluation methodology · **Depth:** Advanced

**Strong answer signals**

- Create a human-labeled, blinded calibration set with explicit rubrics for outcome, tool use, evidence, safety, and efficiency.
- Measure agreement and systematic position, verbosity, style, and self-preference bias by slice.
- Combine the judge with deterministic checks, periodically revalidate it, and preserve uncertainty or disagreement.

**Follow-up probe:** How would you detect that the judge rewards unnecessary tool calls?

**Revision links:** [Protocols and reliability]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }})

### SDS-B4-19 — Build a fault-injection experiment for an agent workflow.

**Round:** Resilience evaluation · **Depth:** Advanced

**Strong answer signals**

- Inject timeouts, throttling, malformed results, stale data, partial completion, lost acknowledgements, and dependency outages at controlled points.
- Define expected retry, fallback, circuit-breaker, escalation, side-effect, and recovery behavior before running tests.
- Measure containment, user impact, recovery time, duplicate actions, and observability; turn failures into regression cases.

**Follow-up probe:** How do you keep a chaos test from causing real external side effects?

**Revision links:** [Protocols and reliability]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }})

### SDS-B4-20 — Compare a new agent release statistically with the current version.

**Round:** Statistical release decision · **Depth:** Leadership

**Strong answer signals**

- Use paired cases and repeated runs where stochasticity matters; report effect sizes and uncertainty, not only p-values.
- Predefine primary metrics, critical slices, non-inferiority safety bounds, practical thresholds, and multiple-comparison handling.
- Combine offline evidence with guarded shadow or canary outcomes and reject average gains that violate a high-risk gate.

**Follow-up probe:** When would a paired bootstrap be more useful than comparing two aggregate means?

**Revision links:** [Protocols and reliability]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }})

## Data, metrics, and system-design evidence

### SDS-B5-01 — Design point-in-time-correct data and labels for an online prediction system.

**Round:** Data architecture · **Depth:** Advanced

**Strong answer signals**

- Define authoritative events, event versus processing time, entity keys, observation and prediction times, label window, maturation, censoring, and revisions.
- Reconstruct features as known at prediction time, prevent entity overlap and future leakage, and version source snapshots and transformations.
- Test training-serving consistency, late data, backfills, deletion, label coverage, and joins against controlled examples.

**Follow-up probe:** How can a correct SQL join still leak future information?

**Revision links:** [AI/ML system design]({{ '/interview-prep/cheat-sheets/ai-ml-system-design-production-architecture/' | relative_url }})

### SDS-B5-02 — Define success metrics for a recommendation model that improves offline ranking but not conversion.

**Round:** Product analytics · **Depth:** Advanced

**Strong answer signals**

- Connect conversion and user value to exposure, ranking quality, calibration or relevance, latency, diversity, guardrails, and cost.
- Check treatment delivery, traffic mix, position bias, novelty, downstream friction, and slice effects before blaming model quality.
- Use a properly powered online experiment or quasi-experimental evidence with practical effect sizes and safety constraints.

**Follow-up probe:** Which offline metric can improve while user value falls, and why?

**Revision links:** [AI/ML system design]({{ '/interview-prep/cheat-sheets/ai-ml-system-design-production-architecture/' | relative_url }})

### SDS-B5-03 — Choose batch, synchronous online, asynchronous, or streaming inference for a risk model.

**Round:** System design · **Depth:** Applied

**Strong answer signals**

- Map decision timing, freshness, response contract, volume, latency, availability, and correction needs to each mode.
- Consider batch precomputation with online lookup or a hybrid path before defaulting to a complex streaming system.
- Define stale-data handling, idempotency, late events, backfill, monitoring, and fallback for the chosen architecture.

**Follow-up probe:** When can daily batch scores be safer than a real-time model?

**Revision links:** [AI/ML system design]({{ '/interview-prep/cheat-sheets/ai-ml-system-design-production-architecture/' | relative_url }})

### SDS-B5-04 — Design a feedback loop without poisoning training data or leaking evaluation cases.

**Round:** Data and evaluation · **Depth:** Advanced

**Strong answer signals**

- Capture feedback with provenance, consent, prediction identity, cohort, task context, and whether it is a proxy, correction, or confirmed outcome.
- Deduplicate, validate, quarantine abuse or incidents, handle disagreement, and enforce privacy, retention, and deletion.
- Keep holdouts and adversarial suites isolated, version approved datasets, and require review before feedback changes training, prompts, retrieval, or memory.

**Follow-up probe:** Why should model-generated traces not flow directly into the next training set?

**Revision links:** [AI/ML system design]({{ '/interview-prep/cheat-sheets/ai-ml-system-design-production-architecture/' | relative_url }}) · [MLOps and LLMOps]({{ '/interview-prep/cheat-sheets/mlops-llmops-deployment-lifecycle/' | relative_url }})

### SDS-B5-05 — Evaluate whether caching improves a prediction or RAG product correctly.

**Round:** Experimentation · **Depth:** Advanced

**Strong answer signals**

- Define key, version namespace, tenant scope, TTL, invalidation, and which outputs are safe to reuse.
- Compare hit rate, latency, cost, freshness, task quality, stale errors, privacy leakage, and stampede behavior by slice.
- Include version changes, deletions, permission updates, cold starts, and a no-cache baseline; a high hit rate alone is not success.

**Follow-up probe:** How would you detect that a cache improves latency by serving obsolete answers?

**Revision links:** [AI/ML system design]({{ '/interview-prep/cheat-sheets/ai-ml-system-design-production-architecture/' | relative_url }})

## Inference benchmark and optimization science

### SDS-B5-06 — Design a benchmark comparing two LLM serving configurations.

**Round:** Performance experiment · **Depth:** Advanced

**Strong answer signals**

- Freeze model, tokenizer/template, precision, engine, hardware, generation, workload distribution, arrival process, and quality set.
- Measure queue, TTFT, TPOT, E2E, goodput, memory, failures, rejections, variability, quality, and cost over warm, spike, and soak trials.
- Use paired requests or controlled repetitions, report uncertainty and slices, and retain timed-out or invalid outputs.

**Follow-up probe:** Why can fixed-concurrency and open-loop request-rate tests produce different conclusions?

**Revision links:** [LLM inference optimization]({{ '/interview-prep/cheat-sheets/llm-inference-serving-optimization/' | relative_url }})

### SDS-B5-07 — Evaluate INT4, INT8, FP8, and BF16 candidates for a domain task.

**Round:** Model evaluation · **Depth:** Advanced

**Strong answer signals**

- Confirm hardware and engine compatibility, calibration or conversion method, and exact quantized artifact identity.
- Compare task and critical-slice quality, schema/tool behavior, numerical or long-context sensitivity, memory, TTFT, TPOT, throughput, and stability.
- Use equivalence or non-inferiority bounds where appropriate and reject aggregate speedups that violate a high-risk slice.

**Follow-up probe:** Why can perplexity alone miss quantization damage important to the application?

**Revision links:** [LLM inference optimization]({{ '/interview-prep/cheat-sheets/llm-inference-serving-optimization/' | relative_url }})

### SDS-B5-08 — Test whether speculative decoding benefits the workload.

**Round:** Optimization evaluation · **Depth:** Advanced

**Strong answer signals**

- Compare target-only and speculative candidates with the same prompts, outputs, generation semantics, concurrency, and quality checks.
- Measure accepted tokens or acceptance length, draft and verification cost, TPOT, E2E, memory, batch interaction, and variability by request class.
- Analyze short outputs, low-acceptance domains, and high concurrency separately; extra machinery can be slower.

**Follow-up probe:** Which workload characteristic most strongly limits speculative decoding gains?

**Revision links:** [LLM inference optimization]({{ '/interview-prep/cheat-sheets/llm-inference-serving-optimization/' | relative_url }})

### SDS-B5-09 — Segment workload results so an inference optimization is not hidden by averages.

**Round:** Performance analytics · **Depth:** Applied

**Strong answer signals**

- Slice by input/output length, task, streaming, tenant or priority, cache state, route, tool path, hardware, and time period.
- Report p50/p95/p99 TTFT/TPOT/E2E, goodput, failure and rejection, quality, and cost with sample sizes.
- Check interaction effects such as long prefills harming short decodes and use production traffic weights only after slice safety is established.

**Follow-up probe:** How can Simpson's paradox mislead an overall latency comparison?

**Revision links:** [LLM inference optimization]({{ '/interview-prep/cheat-sheets/llm-inference-serving-optimization/' | relative_url }})

### SDS-B5-10 — Quantify uncertainty in a capacity estimate derived from load tests.

**Round:** Statistical capacity planning · **Depth:** Advanced

**Strong answer signals**

- Repeat production-like trials across arrival and token distributions, random seeds where relevant, and stable environmental conditions.
- Estimate goodput and tail-latency variability, identify saturation and failure thresholds, and apply peak and resilience headroom separately.
- Validate on an independent run and monitor forecast error after release; a single maximum-throughput point is not a confidence bound.

**Follow-up probe:** Why does adding a fixed 20% headroom not address an unrepresentative workload sample?

**Revision links:** [LLM inference optimization]({{ '/interview-prep/cheat-sheets/llm-inference-serving-optimization/' | relative_url }}) · [AI production operations]({{ '/interview-prep/cheat-sheets/ai-production-monitoring-cost-capacity/' | relative_url }})

## Reproducibility, lifecycle, and release evaluation

### SDS-B5-11 — Make an ML experiment reproducible within realistic limits.

**Round:** Experiment reproducibility · **Depth:** Advanced

**Strong answer signals**

- Record hypothesis, metrics, data snapshot, code/config/environment, preprocessing, initialization, seeds, hyperparameters, hardware, logs, and artifact digests.
- State nondeterministic GPU or distributed behavior and compare within justified tolerances rather than promising bitwise equality.
- Re-run from retained inputs in a clean environment and verify both headline and slice metrics plus failure and cost evidence.

**Follow-up probe:** Why do fixed random seeds not guarantee identical distributed-training results?

**Revision links:** [MLOps and LLMOps]({{ '/interview-prep/cheat-sheets/mlops-llmops-deployment-lifecycle/' | relative_url }})

### SDS-B5-12 — Explain when an experiment tracker and a model registry provide different evidence.

**Round:** MLOps foundations · **Depth:** Applied

**Strong answer signals**

- A tracker records development runs, parameters, metrics, artifacts, and comparisons; a registry governs immutable candidate identity, lineage, gates, approval, deployment, and retirement.
- Link accepted registry versions back to exact runs and data while preventing mutable aliases from replacing immutable evidence.
- Record evaluator, thresholds, approver, deployment cohort, and rollback reference rather than storing only weights.

**Follow-up probe:** Can one product implement both responsibilities, and what separation still matters?

**Revision links:** [MLOps and LLMOps]({{ '/interview-prep/cheat-sheets/mlops-llmops-deployment-lifecycle/' | relative_url }})

### SDS-B5-13 — Define data validation gates before retraining.

**Round:** Data quality · **Depth:** Advanced

**Strong answer signals**

- Validate schema, types, ranges, missingness, duplicates, volume, freshness, source completeness, labels, entity overlap, and point-in-time correctness.
- Compare distributions by meaningful slices with versioned baselines and distinguish expected population change from pipeline defects.
- Block or quarantine candidates when evidence is incomplete, preserve the failing snapshot, and require owner-approved resolution.

**Follow-up probe:** Which leakage check cannot be replaced by a simple train/test row split?

**Revision links:** [MLOps and LLMOps]({{ '/interview-prep/cheat-sheets/mlops-llmops-deployment-lifecycle/' | relative_url }})

### SDS-B5-14 — Validate a new RAG index before promotion.

**Round:** RAG lifecycle · **Depth:** Advanced

**Strong answer signals**

- Bind corpus, permissions, parser, chunker, embedding, index, reranker, retrieval config, and deletion state to an immutable candidate.
- Test completeness, ACL and revocation, retrieval recall and ranking, latency, citations, answer quality, and critical slices against the current index.
- Use paired canary queries and an atomic alias switch with rollback; investigate disagreements rather than relying on one aggregate judge.

**Follow-up probe:** Why can higher retrieval recall still reduce answer quality?

**Revision links:** [MLOps and LLMOps]({{ '/interview-prep/cheat-sheets/mlops-llmops-deployment-lifecycle/' | relative_url }})

### SDS-B5-15 — Analyze a canary release statistically and operationally.

**Round:** Release evaluation · **Depth:** Leadership

**Strong answer signals**

- Confirm comparable routing and exposure, exact candidate identity, primary metrics, safety gates, power or minimum evidence, and predeclared abort criteria.
- Compare outcomes and uncertainty by critical slice while monitoring service, cost, fallback, and telemetry health.
- Separate release-risk evidence from long-term product experimentation and account for delayed labels before full promotion.

**Follow-up probe:** What selection bias appears if only low-latency requests reach the canary?

**Revision links:** [MLOps and LLMOps]({{ '/interview-prep/cheat-sheets/mlops-llmops-deployment-lifecycle/' | relative_url }})

## Production monitoring and decision quality

### SDS-B5-16 — Monitor performance when ground truth arrives weeks later.

**Round:** Delayed-label monitoring · **Depth:** Advanced

**Strong answer signals**

- Preserve immutable prediction, entity or decision ID, event time, candidate lineage, and original threshold or action.
- Join labels after a defined maturation window, retain revisions, and report coverage, censoring, uncertainty, and cohort or slice metrics.
- Use leading proxies only as clearly labeled diagnostics and avoid declaring quality from confidence or early responders.

**Follow-up probe:** How can outcome-dependent label availability bias the monitored metric?

**Revision links:** [AI production operations]({{ '/interview-prep/cheat-sheets/ai-production-monitoring-cost-capacity/' | relative_url }})

### SDS-B5-17 — Choose and interpret drift detectors for production features.

**Round:** Drift analysis · **Depth:** Advanced

**Strong answer signals**

- Match domain rules, PSI, KS, chi-square, Wasserstein, Jensen–Shannon, or learned detectors to feature type and decision need.
- Define reference, window, sample size, seasonality, multiple comparisons, missing-data behavior, threshold source, and slices.
- Treat drift as investigation evidence and verify labels, instrumentation, traffic, and outcome impact before retraining.

**Follow-up probe:** Why can a statistically significant shift be operationally irrelevant?

**Revision links:** [AI production operations]({{ '/interview-prep/cheat-sheets/ai-production-monitoring-cost-capacity/' | relative_url }})

### SDS-B5-18 — Calibrate an LLM judge used in production quality monitoring.

**Round:** Evaluation operations · **Depth:** Advanced

**Strong answer signals**

- Pin judge model, prompt, rubric, sampling, and version; create a blinded expert or deterministic calibration set.
- Measure agreement, uncertainty, and position, verbosity, style, and self-preference bias by task and risk slice.
- Treat judge failure or disagreement as unknown, protect sensitive content, and avoid automatic rollback from the judge alone.

**Follow-up probe:** How would you detect that a judge drifted after its provider changed the resolved model?

**Revision links:** [AI production operations]({{ '/interview-prep/cheat-sheets/ai-production-monitoring-cost-capacity/' | relative_url }})

### SDS-B5-19 — Construct a quality-latency-cost frontier for model routing.

**Round:** Decision analysis · **Depth:** Advanced

**Strong answer signals**

- Evaluate exact routes on identical representative cases with task and safety quality, tail latency, failure, tokens, provider/GPU and tool cost.
- Identify dominated options and slice-specific frontiers rather than collapsing all objectives into one arbitrary weighted score.
- Choose routes by accepted risk and SLO tier, then validate with canary outcomes and monitor route drift.

**Follow-up probe:** Why might one model be optimal for routine cases but unacceptable for the high-risk tail?

**Revision links:** [AI production operations]({{ '/interview-prep/cheat-sheets/ai-production-monitoring-cost-capacity/' | relative_url }})

### SDS-B5-20 — Production quality falls after a release while input drift also rises. Diagnose causally.

**Round:** Production investigation · **Depth:** Leadership

**Strong answer signals**

- Verify telemetry and labels, preserve exact release identity, and decompose by time, cohort, feature, route, model, prompt/index, and data pipeline versions.
- Compare rollback or shadow candidates on the same requests and separate instrumentation, traffic composition, data quality, and behavior changes.
- Quantify affected outcomes and uncertainty, contain high-risk slices, and add the confirmed failure to release and monitoring suites.

**Follow-up probe:** What evidence would show that drift is correlated with, but did not cause, the regression?

**Revision links:** [AI production operations]({{ '/interview-prep/cheat-sheets/ai-production-monitoring-cost-capacity/' | relative_url }})

## Data and distributed compute engineering

### SDS-B6-01 — Decide whether a large analytical feature job needs distributed compute.

**Round:** Data engineering judgment · **Depth:** Applied

**Strong answer signals**

- Define bytes and rows, growth, file count, joins and groupings, memory, freshness, repetition, skew, failure and replay needs, and current single-node evidence.
- Compare SQL, DuckDB or Polars and Spark on a representative slice including I/O, startup, shuffle, spill, serialization, engineering time, and cost.
- Prefer the smallest reliable boundary, then define migration triggers and preserve deterministic outputs, data lineage, tests, and benchmark identity.

**Follow-up probe:** Which wide operation is most likely to make the single-node approach fail first?

**Revision links:** [Data and distributed compute]({{ '/interview-prep/cheat-sheets/data-distributed-compute-engineering/' | relative_url }})

### SDS-B6-02 — Build point-in-time-correct training data from historical and streaming sources.

**Round:** Feature correctness · **Depth:** Advanced

**Strong answer signals**

- Define prediction time, event time, label observation and maturation windows, entity keys, corrections, missingness, duplicates, and source availability at decision time.
- Use as-of or point-in-time joins, fit transformations on training only, group and time-aware splits, deduplication, immutable test data, and versioned source snapshots.
- Test online/offline parity, late-event and backfill behavior, leakage canaries, freshness and distributions by slice, and reproducibility of the exact dataset.

**Follow-up probe:** How can a recently observed negative label create censoring bias?

**Revision links:** [Data and distributed compute]({{ '/interview-prep/cheat-sheets/data-distributed-compute-engineering/' | relative_url }})

### SDS-B6-03 — Choose event-time windows, watermarks, and late-data behavior for online features.

**Round:** Streaming data science · **Depth:** Advanced

**Strong answer signals**

- Derive windows from the decision and label process, then measure arrival-delay distributions rather than choosing a watermark from convenience.
- Define state key, retention, duplicate and correction semantics, whether late records update, side-output, or trigger batch correction, and what freshness is exposed to the model.
- Evaluate quality and operational cost across delay slices, replay failures and checkpoint recovery, and monitor watermark lag, state size, missing features, and drift.

**Follow-up probe:** What bias can result if late events are dropped disproportionately for one population?

**Revision links:** [Data and distributed compute]({{ '/interview-prep/cheat-sheets/data-distributed-compute-engineering/' | relative_url }})

### SDS-B6-04 — Diagnose a distributed aggregation whose totals are correct but completion time is unstable.

**Round:** Performance and correctness · **Depth:** Advanced

**Strong answer signals**

- Inspect the physical plan, task-time and partition-size distributions, hot keys, shuffle, spill, small files, executor loss, retries, and input variation by interval.
- Filter or project earlier, pre-aggregate, isolate or salt exceptional keys, adjust partitioning, remove slow UDFs, and validate adaptive execution with the real skew.
- Preserve exact aggregation semantics and reconcile counts; report tail time, useful throughput, cost, and output correctness rather than average CPU.

**Follow-up probe:** Why might simply adding executors leave the p99 task unchanged?

**Revision links:** [Data and distributed compute]({{ '/interview-prep/cheat-sheets/data-distributed-compute-engineering/' | relative_url }})

### SDS-B6-05 — Make a multi-GPU training experiment reproducible and statistically comparable.

**Round:** Distributed experimentation · **Depth:** Advanced

**Strong answer signals**

- Pin data order and snapshot, model and code, precision, topology, parallel strategy, global batch, accumulation, optimizer and schedule, seeds, and determinism limits.
- Compare candidates on accepted quality and slices plus tokens per second, scaling efficiency, memory, communication, failures, checkpoint and recovery, and total cost.
- Repeat enough runs to characterize variance, preserve exact checkpoints and manifests, and avoid attributing convergence changes to architecture when effective batch changed.

**Follow-up probe:** Which worker-count change can silently alter the optimization trajectory?

**Revision links:** [Data and distributed compute]({{ '/interview-prep/cheat-sheets/data-distributed-compute-engineering/' | relative_url }})

## AI security, privacy, and governance

### SDS-B6-06 — Explain why prompt-injection robustness cannot be established from model refusal rate alone.

**Round:** AI security · **Depth:** Advanced

**Strong answer signals**

- Separate unsafe text, attempted application action, control decision, and committed business effect; a probabilistic refusal is not an authorization boundary.
- Test direct and indirect channels across documents, tool results, memory and peer messages with trusted identity, least privilege, semantic validation, approval, and sandbox controls.
- Use bounded synthetic canaries and deterministic state or side-effect assertions, report false positives and coverage, and bind results to the exact release.

**Follow-up probe:** Which metric would reveal a model that refuses visibly but still emits a valid dangerous tool call?

**Revision links:** [AI security, privacy, and governance]({{ '/interview-prep/cheat-sheets/ai-security-privacy-governance/' | relative_url }})

### SDS-B6-07 — Prepare a privacy-safe dataset for model evaluation and feedback learning.

**Round:** Privacy engineering · **Depth:** Advanced

**Strong answer signals**

- Define purpose, lawful or organizational basis, population, data classes, sensitive fields, consent where applicable, access, retention, deletion, provider use, and excluded uses.
- Minimize and pseudonymize or redact where useful, retain linkage only under control, use synthetic canaries, restrict traces and exports, and assess reidentification rather than claiming anonymity.
- Version provenance and transformations, test slice representativeness and deletion propagation, document limitations, and require accountable review before feedback changes production behavior.

**Follow-up probe:** How can removing direct identifiers still leave a dataset reidentifiable?

**Revision links:** [AI security, privacy, and governance]({{ '/interview-prep/cheat-sheets/ai-security-privacy-governance/' | relative_url }})

### SDS-B6-08 — Evaluate a RAG system for poisoning, unauthorized retrieval, and unsupported citations.

**Round:** RAG assurance · **Depth:** Advanced

**Strong answer signals**

- Create versioned clean, malicious, cross-tenant, revoked, stale, and authority-spoofed documents with immutable source and ACL lineage.
- Measure authorization violations separately from candidate recall, ranking, answer correctness, groundedness and citation support; assert protected canaries never appear.
- Test ingestion quarantine, current permission checks, permission-aware caches, deletion and index rebuild, suspicious enumeration, abstention, incident containment, and recovery.

**Follow-up probe:** Why can a grounded answer still be unsafe or wrong?

**Revision links:** [AI security, privacy, and governance]({{ '/interview-prep/cheat-sheets/ai-security-privacy-governance/' | relative_url }})

### SDS-B6-09 — Define fairness and governance evidence for a high-impact classifier.

**Round:** Responsible AI · **Depth:** Leadership

**Strong answer signals**

- Identify affected users, decision, error costs, relevant groups and intersections, label and sampling bias, human workflow, appeal, and whether automation is appropriate.
- Report performance, calibration and outcome disparities with uncertainty by meaningful slice, threshold trade-offs, data limitations, and comparison with the existing baseline.
- Assign accountable owners, review and release criteria, monitoring with delayed outcomes, escalation and fallback, documented exceptions, and triggers to pause or narrow use.

**Follow-up probe:** Why can equal aggregate accuracy hide unacceptable group harm?

**Revision links:** [AI security, privacy, and governance]({{ '/interview-prep/cheat-sheets/ai-security-privacy-governance/' | relative_url }})

### SDS-B6-10 — Design an adversarial evaluation campaign without overstating what the tools prove.

**Round:** Evaluation design · **Depth:** Advanced

**Strong answer signals**

- Derive scenarios from the application threat model and ordinary security risks, covering injection, data disclosure, tenant isolation, poisoned content, unsafe sinks, agency, and resource abuse.
- Combine PyRIT, garak, promptfoo, guardrails or custom suites with deterministic oracles, calibrated subjective labels, bounded authority, synthetic data, and cleanup.
- Preserve scenario and release identity, severity, reproduction, failed and skipped cases, remediation and retest, residual gaps, and accountable risk acceptance.

**Follow-up probe:** Which claim remains invalid even if every configured scanner test passes?

**Revision links:** [AI security, privacy, and governance]({{ '/interview-prep/cheat-sheets/ai-security-privacy-governance/' | relative_url }})

## Technical leadership and product thinking

### SDS-B6-11 — Build a metric tree that connects a model improvement to product and business value.

**Round:** Product thinking · **Depth:** Leadership

**Strong answer signals**

- Start from user decision and baseline, then connect business outcome, product adoption and corrections, model quality, safety or fairness, service reliability, and cost.
- Define metric unit, direction, population and slices, window, source, owner, threshold and action; label proxy versus outcome and expected delay.
- Propose an ethical experiment or phased rollout, guardrails, attribution limits, and a decision rule that can reject a statistically better but operationally worse model.

**Follow-up probe:** Which metric would show that higher recall overloaded the human review team?

**Revision links:** [AI technical leadership and product thinking]({{ '/interview-prep/cheat-sheets/ai-technical-leadership-product-thinking/' | relative_url }})

### SDS-B6-12 — Challenge a request for an LLM when a simpler baseline may be sufficient.

**Round:** Technical judgment · **Depth:** Leadership

**Strong answer signals**

- Clarify the user, action, baseline, frequency, value, error cost, explainability, privacy, latency, budget, and adoption constraints.
- Compare process change, rules, SQL, search, classical ML, retrieval, LLM and human service using a representative dataset and outcome-aligned evaluation.
- Recommend the simplest accepted option, state trade-offs and non-goals, and define evidence and thresholds that would justify more complexity later.

**Follow-up probe:** How would you communicate this recommendation to an executive who specifically requested GenAI?

**Revision links:** [AI technical leadership and product thinking]({{ '/interview-prep/cheat-sheets/ai-technical-leadership-product-thinking/' | relative_url }})

### SDS-B6-13 — Prioritize experiments when labels, adoption, latency, and fairness are all uncertain.

**Round:** Experiment strategy · **Depth:** Leadership

**Strong answer signals**

- List uncertainties and decision impact, dependencies, evidence confidence, reversibility, effort, risk and learning value rather than ranking model ideas by novelty.
- Start with workflow and data audits, baseline and label-agreement studies, then offline, user, shadow and controlled rollout evidence only as justified.
- Set stop or pivot criteria, owners, decision dates and guardrails; update the roadmap when evidence changes instead of protecting sunk work.

**Follow-up probe:** Which uncertainty would you resolve first if the label definition itself is disputed?

**Revision links:** [AI technical leadership and product thinking]({{ '/interview-prep/cheat-sheets/ai-technical-leadership-product-thinking/' | relative_url }})

### SDS-B6-14 — Contribute technical depth to an architecture review without owning every component.

**Round:** Technical influence · **Depth:** Leadership

**Strong answer signals**

- Bring data and label contracts, point-in-time correctness, evaluation and uncertainty, model or retrieval alternatives, monitoring, and change triggers tied to requirements.
- Ask how failures, drift, delayed outcomes, feedback, rollout and rollback affect evidence; separate observed facts, assumptions, preferences and open risks.
- Record your exact recommendation and validation action, respect interface owners, escalate only consequential unresolved risk, and support the accountable decision.

**Follow-up probe:** Which modeling concern should block design approval rather than become a follow-up experiment?

**Revision links:** [AI technical leadership and product thinking]({{ '/interview-prep/cheat-sheets/ai-technical-leadership-product-thinking/' | relative_url }})

### SDS-B6-15 — Escalate a fairness or privacy concern when the release deadline is fixed.

**Round:** Responsible leadership · **Depth:** Leadership

**Strong answer signals**

- Document affected populations, data flow, measured evidence and uncertainty, potential harm, policy boundary, and which release scope creates the risk.
- Bring domain, product, privacy, security, legal or model-risk owners early and present pause, narrower cohort, human review, data minimization, or alternative-process options.
- Preserve accountable decision and dissent, define required evidence and monitoring, and refuse to hide or relabel risk merely to meet the date.

**Follow-up probe:** What narrower release could preserve learning without exposing the high-risk population?

**Revision links:** [AI technical leadership and product thinking]({{ '/interview-prep/cheat-sheets/ai-technical-leadership-product-thinking/' | relative_url }})

## Project deep dives, behavioral answers, and mock interviews

### SDS-B6-16 — Give a 30-second headline and two-minute overview of a high-impact ML project.

**Round:** Project storytelling · **Depth:** Leadership

**Strong answer signals**

- Lead with user or business decision, measured baseline, scale and constraints, then state your exact ownership and the team's complementary work.
- Explain why ML was justified, data and validation approach, simplest architecture, rollout and operational evidence without turning the answer into an algorithm chronology.
- State outcome with unit, window, population, comparator and attribution limits plus the key trade-off or learning, then pause for the interviewer to choose depth.

**Follow-up probe:** What should you remove first if the two-minute answer becomes four minutes?

**Revision links:** [Project deep dive and mock interviews]({{ '/interview-prep/cheat-sheets/project-deep-dive-behavioral-mock-interview/' | relative_url }})

### SDS-B6-17 — Defend a business-impact claim from an optimization or predictive project.

**Round:** Impact attribution · **Depth:** Advanced

**Strong answer signals**

- Provide metric and unit, baseline and comparator, eligible volume, time window, seasonality, adoption, gross versus net value, and operating or change costs.
- Explain the strongest feasible attribution method—projected, before/after, matched, phased or randomized—plus uncertainty, confounders and overlapping benefits.
- Separate offline score, recommended opportunity, accepted decision, realized outcome and owner validation; never multiply accuracy by revenue without a causal bridge.

**Follow-up probe:** Which part of the claimed value would you label projected rather than realized?

**Revision links:** [Project deep dive and mock interviews]({{ '/interview-prep/cheat-sheets/project-deep-dive-behavioral-mock-interview/' | relative_url }})

### SDS-B6-18 — Tell a failure story about drift or leakage that reached a user-facing workflow.

**Round:** Behavioral · **Depth:** Leadership

**Strong answer signals**

- State the assumption or signal missed, affected users and slices, decision impact, detection path, and your accountability without disguising the failure as routine retraining.
- Cover containment, stakeholder communication, version and evidence preservation, root mechanism, correction, backfill or reconciliation, and recovery verification.
- Show durable changes to data contracts, split strategy, acceptance sets, monitoring, release gates or ownership and later evidence that recurrence risk fell.

**Follow-up probe:** Why did the original monitoring fail to reveal the issue?

**Revision links:** [Project deep dive and mock interviews]({{ '/interview-prep/cheat-sheets/project-deep-dive-behavioral-mock-interview/' | relative_url }})

### SDS-B6-19 — Describe a disagreement over model complexity or operating threshold.

**Round:** Behavioral · **Depth:** Leadership

**Strong answer signals**

- Frame the shared outcome and valid concerns, then make error costs, capacity, latency, calibration, explainability, adoption, and uncertainty explicit.
- Gather a discriminating ablation, threshold simulation or controlled test; present reversible options and route risk tolerance to the accountable owner.
- Explain your contribution, final decision, commitment and result, credit the other perspective, and name the evidence that would reopen the choice.

**Follow-up probe:** Which result could make the simpler model preferable even with lower offline accuracy?

**Revision links:** [Project deep dive and mock interviews]({{ '/interview-prep/cheat-sheets/project-deep-dive-behavioral-mock-interview/' | relative_url }})

### SDS-B6-20 — Solve a mock demand-forecasting and optimization case end to end.

**Round:** Mock system case · **Depth:** Advanced

**Strong answer signals**

- Define the downstream decision, objective, constraints, hierarchy, horizon, baseline, error asymmetry, exogenous information availability, override and business counterfactual.
- Design time-aware backtesting, leakage controls, uncertainty or scenarios, reconciliation across hierarchy, model and optimization interface, feasibility fallback, and human review.
- Connect forecast metrics to decision regret and business outcome, then cover rollout, drift, constraint changes, capacity, monitoring, retraining, rollback and impact attribution.

**Follow-up probe:** How would you prove that a better forecast actually improved the optimization decision?

**Revision links:** [Project deep dive and mock interviews]({{ '/interview-prep/cheat-sheets/project-deep-dive-behavioral-mock-interview/' | relative_url }})

## Mathematical foundations and optimization

### SDS-B7-01 — Derive the gradient of logistic loss and explain every shape.

**Round:** Mathematical foundations · **Depth:** Advanced

**Strong answer signals**

- Define `X` as `(n, d)`, `w` as `(d,)`, logits `Xw`, probabilities `sigmoid(Xw)` and average binary cross-entropy.
- Use chain rule to obtain `Xᵀ(p-y)/n`, note that the gradient matches `w`, and add the appropriate regularization gradient if present.
- Connect the residual term to maximum likelihood, numerical stable logits-based loss and finite-difference checks on a tiny smooth example.

**Follow-up probe:** How does the Hessian explain convexity and poor conditioning in logistic regression?

**Revision links:** [Linear algebra, calculus, and optimization]({{ '/interview-prep/cheat-sheets/linear-algebra-calculus-optimization/' | relative_url }})

### SDS-B7-02 — Diagnose multicollinearity and decide between regularization and PCA.

**Round:** Statistical modeling · **Depth:** Advanced

**Strong answer signals**

- Use domain redundancy, correlation, singular values/condition number and coefficient instability across samples while separating prediction quality from coefficient interpretation.
- Compare ridge shrinkage, lasso sparsity, feature redesign and PCA against explanation, stability, scale and downstream performance; fit all choices inside validation folds.
- Report coefficient/feature stability and held-out value, preserve units and lineage, and avoid explicit inverse-based solutions on ill-conditioned matrices.

**Follow-up probe:** Why can predictions remain stable while individual coefficients change sign?

**Revision links:** [Linear algebra, calculus, and optimization]({{ '/interview-prep/cheat-sheets/linear-algebra-calculus-optimization/' | relative_url }})

### SDS-B7-03 — Explain when L1, L2, and elastic net produce different practical models.

**Round:** Model regularization · **Depth:** Advanced

**Strong answer signals**

- Explain L1's non-smooth sparse solutions, L2's smooth shrinkage and elastic net's grouped/stabilizing compromise for correlated predictors.
- Standardize features where penalty comparability requires it and tune regularization only inside cross-validation or time-aware validation.
- Compare predictive uncertainty, selection stability, calibration and interpretability; do not present a selected nonzero coefficient as causal evidence.

**Follow-up probe:** Why might lasso arbitrarily keep one of several correlated variables?

**Revision links:** [Linear algebra, calculus, and optimization]({{ '/interview-prep/cheat-sheets/linear-algebra-calculus-optimization/' | relative_url }})

### SDS-B7-04 — Separate optimization, generalization, and numerical failures in a neural model.

**Round:** Training diagnostics · **Depth:** Advanced

**Strong answer signals**

- Use train/validation curves, gradient and activation norms, finite-value checks, learning-rate/batch experiments and tiny-batch overfit to classify the failure.
- Treat decreasing train loss with widening validation gap as generalization, flat train loss as optimization/data/model issue, and NaN/Inf as numerical or invalid-data evidence.
- Change one hypothesis at a time—scaling, initialization, optimizer, schedule, regularization or stable loss—and retain reproducible checkpoints and baselines.

**Follow-up probe:** Which evidence argues against “bad local minimum” as the explanation?

**Revision links:** [Linear algebra, calculus, and optimization]({{ '/interview-prep/cheat-sheets/linear-algebra-calculus-optimization/' | relative_url }})

### SDS-B7-05 — Explain the geometry behind an embedding nearest-neighbor model.

**Round:** Representation learning · **Depth:** Advanced

**Strong answer signals**

- Connect the training objective to expected geometry, discuss vector norms and derive cosine/dot/Euclidean relationships after unit normalization.
- Explain high-dimensional concentration, anisotropy, hubness and approximate-index effects, then validate neighbors with task labels and slices.
- Separate representation quality, index recall and downstream decision quality; monitor model/version, normalization, norm and score drift.

**Follow-up probe:** How would you determine whether poor neighbors come from the embedding or ANN index?

**Revision links:** [Linear algebra, calculus, and optimization]({{ '/interview-prep/cheat-sheets/linear-algebra-calculus-optimization/' | relative_url }})

## Experimentation and causal inference

### SDS-B7-06 — Calculate and defend sample size for a binary-conversion experiment.

**Round:** Experimental design · **Depth:** Advanced

**Strong answer signals**

- State baseline rate, absolute MDE from practical value, two-sided alpha, power, allocation, randomization unit, expected eligible traffic and outcome maturation.
- Use an appropriate two-proportion approximation or simulation, then adjust for clustering, attrition/noncompliance, multiple primary comparisons and ramp.
- Convert units to calendar duration with business cycles, predeclare stopping and report sensitivity when baseline or variance assumptions are uncertain.

**Follow-up probe:** Why does halving the MDE require roughly four times the sample in the simple case?

**Revision links:** [Experimentation and causal inference]({{ '/interview-prep/cheat-sheets/experimentation-causal-inference/' | relative_url }})

### SDS-B7-07 — Apply CUPED without contaminating an experiment.

**Round:** Variance reduction · **Depth:** Advanced

**Strong answer signals**

- Choose a pre-treatment covariate measured consistently for both arms and correlated with the outcome, define handling for new users and lock it before effect inspection.
- Explain the adjusted outcome and estimated coefficient, preserve ITT and compute uncertainty under the actual randomization design.
- Verify no treatment leakage, compare variance/power gain, inspect slice behavior and retain the unadjusted estimate as a transparent robustness check.

**Follow-up probe:** What goes wrong if the covariate includes activity after assignment?

**Revision links:** [Experimentation and causal inference]({{ '/interview-prep/cheat-sheets/experimentation-causal-inference/' | relative_url }})

### SDS-B7-08 — Choose an adjustment set from a causal DAG.

**Round:** Causal reasoning · **Depth:** Advanced

**Strong answer signals**

- Define treatment, outcome and estimand, then identify pre-treatment common causes, mediators, colliders and proxy relationships with domain experts.
- Block backdoor paths using a sufficient pre-treatment set while avoiding post-treatment mediators and collider conditioning; state unmeasured-confounding risk.
- Check temporal order, positivity and balance, compare plausible DAGs and use negative controls or sensitivity analysis rather than claiming the graph is proven.

**Follow-up probe:** How can conditioning on workflow completion create an association that did not exist?

**Revision links:** [Experimentation and causal inference]({{ '/interview-prep/cheat-sheets/experimentation-causal-inference/' | relative_url }})

### SDS-B7-09 — Evaluate a difference-in-differences policy study.

**Round:** Quasi-experimental methods · **Depth:** Advanced

**Strong answer signals**

- Define treated/comparison groups, intervention timing and outcome; defend parallel untreated trends using domain context and multiple pre-periods, not a p-value alone.
- Examine anticipation, composition, spillovers, concurrent shocks, autocorrelation and staggered adoption; use timing-appropriate estimators and clustered uncertainty.
- Present event-time dynamics and sensitivity/placebo analyses, bound external validity and avoid translating a local policy effect into a universal claim.

**Follow-up probe:** Why can naive two-way fixed effects mislead with staggered treatment and heterogeneous effects?

**Revision links:** [Experimentation and causal inference]({{ '/interview-prep/cheat-sheets/experimentation-causal-inference/' | relative_url }})

### SDS-B7-10 — Estimate and validate heterogeneous treatment effects for targeting.

**Round:** Uplift modeling · **Depth:** Advanced

**Strong answer signals**

- Use randomized or credibly identified data, ensure overlap and enough sample, and separate outcome prediction from treatment-effect estimation.
- Predeclare important segments or use honest sample splitting/causal forests or meta-learners; tune and evaluate out of sample with uplift/value curves and capacity.
- Confirm exploratory subgroups in a holdout/new experiment, include guardrails and fairness, and compare the targeting policy with treat-all/treat-none baselines.

**Follow-up probe:** Why is high response-model AUC insufficient for an uplift policy?

**Revision links:** [Experimentation and causal inference]({{ '/interview-prep/cheat-sheets/experimentation-causal-inference/' | relative_url }})

## Data preparation, EDA, and feature engineering

### SDS-B7-11 — Design the unit, label, and validation split for a churn model.

**Round:** Problem framing · **Depth:** Advanced

**Strong answer signals**

- Define customer scoring date, eligible population, observation window, churn event/horizon, censoring, intervention and repeated-score handling.
- Use time- and customer-aware backtesting with matured labels, fitting preprocessing within folds and keeping a future final test period.
- Audit cancellation/post-contact leakage, selective outcomes and seasonality; evaluate calibration and lift/value at contact capacity by cohort.

**Follow-up probe:** How would you label customers whose outcome horizon is not yet complete?

**Revision links:** [Data preparation, EDA, and feature engineering]({{ '/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/' | relative_url }})

### SDS-B7-12 — Handle informative missingness and outliers in industrial sensor data.

**Round:** Data preparation · **Depth:** Advanced

**Strong answer signals**

- Trace outages, maintenance, sensor limits, operating modes and units; distinguish absent, not applicable, censored, stuck and invalid values by asset/time.
- Compare robust imputation/scaling, missing indicators, model-native handling and regime-specific models while fitting all statistics on training/reference periods.
- Preserve rare valid failures, use physical plausibility and source evidence before capping, and monitor missing/outlier mechanisms because operations can change them.

**Follow-up probe:** Why might a missingness indicator be predictive today but dangerous after a sensor upgrade?

**Revision links:** [Data preparation, EDA, and feature engineering]({{ '/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/' | relative_url }})

### SDS-B7-13 — Compare categorical encoders for a high-cardinality tabular model.

**Round:** Feature engineering · **Depth:** Advanced

**Strong answer signals**

- Compare one-hot, hashing, frequency, target encoding and embeddings by support, sparsity, model family, interpretability, unseen values, drift and latency.
- Implement target encoding out of fold and, for temporal problems, only from prior labels with smoothing and a global fallback.
- Evaluate time/group holdouts, rare-category slices and calibration; version mappings and monitor coverage rather than choosing by training AUC.

**Follow-up probe:** When can hashing outperform target encoding despite collisions?

**Revision links:** [Data preparation, EDA, and feature engineering]({{ '/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/' | relative_url }})

### SDS-B7-14 — Perform feature selection for an imbalanced, correlated dataset.

**Round:** Modeling strategy · **Depth:** Advanced

**Strong answer signals**

- Define decision metric and capacity, split by deployment, and place scaling, resampling and selection inside each training fold.
- Compare domain removal, regularization, permutation or embedded importance with stability across folds/time; treat correlated feature importance cautiously.
- Evaluate calibration, PR/capacity metrics, latency and slice performance on untouched prevalence; avoid selecting from test performance or causal claims from importance.

**Follow-up probe:** Why can selecting features before cross-validation inflate performance?

**Revision links:** [Data preparation, EDA, and feature engineering]({{ '/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/' | relative_url }})

### SDS-B7-15 — Prove a rolling aggregate is point-in-time correct.

**Round:** Feature validation · **Depth:** Advanced

**Strong answer signals**

- Define entity, event time, produced/available time, prediction cutoff, interval endpoints, timezone, late corrections and minimum history explicitly.
- Recompute small hand-audited examples and historical snapshots, ensuring no centered window, future partition or final-state dimension enters the join.
- Compare offline and online sampled values with lineage/version, test boundary times and backfills, and monitor freshness/default rates after deployment.

**Follow-up probe:** How can a source event timestamp still leak if the feature was not operationally available then?

**Revision links:** [Data preparation, EDA, and feature engineering]({{ '/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/' | relative_url }})

## Unsupervised learning and anomaly detection

### SDS-B7-16 — Choose the number of customer clusters and defend the result.

**Round:** Clustering · **Depth:** Advanced

**Strong answer signals**

- Define point-in-time features, scaling, distance and downstream decision; compare a no-segmentation or business-rule baseline.
- Use objective/elbow and silhouette only as diagnostics, then test stability across seeds/bootstraps/time, minimum support, interpretability and migration.
- Validate cluster-specific action prospectively and assess fairness; reject a mathematically neat partition that has no distinct useful treatment.

**Follow-up probe:** How would you compare two clusterings when their numeric labels are permuted?

**Revision links:** [Unsupervised learning and anomaly detection]({{ '/interview-prep/cheat-sheets/unsupervised-learning-anomaly-detection/' | relative_url }})

### SDS-B7-17 — Compare k-means with a Gaussian mixture for overlapping segments.

**Round:** Unsupervised modeling · **Depth:** Advanced

**Strong answer signals**

- Explain hard nearest-centroid assignments and spherical squared-distance assumptions versus probabilistic memberships and covariance choices.
- Fit multiple starts with scaled data, check singular/degenerate components and compare BIC/likelihood, stability, calibration of memberships and external utility.
- Prefer soft assignment only when uncertainty is meaningful to the action; do not treat mixture membership as an immutable customer type.

**Follow-up probe:** What happens when a full-covariance GMM has too few points per component?

**Revision links:** [Unsupervised learning and anomaly detection]({{ '/interview-prep/cheat-sheets/unsupervised-learning-anomaly-detection/' | relative_url }})

### SDS-B7-18 — Evaluate an Isolation Forest with very few confirmed fraud labels.

**Round:** Anomaly evaluation · **Depth:** Advanced

**Strong answer signals**

- Use a time-held incident set, prospective review and random below-threshold audits; preserve prevalence and avoid labeling every unreviewed case negative.
- Report precision/recall or captured value at investigation capacity, detection delay and stability by time/slice; compare supervised and rule baselines where possible.
- Treat injected anomalies as signature tests only, analyze feature/context evidence and update an adjudicated set with selection-aware feedback.

**Follow-up probe:** How would you estimate false negatives when investigators see only top-scored cases?

**Revision links:** [Unsupervised learning and anomaly detection]({{ '/interview-prep/cheat-sheets/unsupervised-learning-anomaly-detection/' | relative_url }})

### SDS-B7-19 — Detect collective anomalies in seasonal multivariate time series.

**Round:** Time-series modeling · **Depth:** Advanced

**Strong answer signals**

- Define series/window, operating regimes, seasonal calendar, acceptable delay and incident grouping; build naive seasonal and rule baselines.
- Compare forecast residuals, robust decomposition, change points and window representations with rolling-origin evaluation and strictly past normalization.
- Threshold by incident cost/capacity, test known events and benign regime changes, expose contributing signals and monitor reference/seasonality drift.

**Follow-up probe:** Why can independent point thresholds miss a dangerous sequence?

**Revision links:** [Unsupervised learning and anomaly detection]({{ '/interview-prep/cheat-sheets/unsupervised-learning-anomaly-detection/' | relative_url }})

### SDS-B7-20 — Decide whether an autoencoder improves anomaly detection over PCA.

**Round:** Representation evaluation · **Depth:** Advanced

**Strong answer signals**

- Compare on the same scaled reference period, time holdout and threshold policy; control capacity so the autoencoder cannot trivially reconstruct everything.
- Evaluate per-feature and total residuals, known incidents, random audits, stability, latency and maintenance while checking reference contamination and regime coverage.
- Choose the nonlinear model only for reproducible downstream gain beyond PCA/rules, and retain versioned preprocessing, explanation and rollback.

**Follow-up probe:** Why can lower reconstruction error make anomaly detection worse?

**Revision links:** [Unsupervised learning and anomaly detection]({{ '/interview-prep/cheat-sheets/unsupervised-learning-anomaly-detection/' | relative_url }})

## Completion evidence

- You can answer at least 16 of 20 questions in each batch without reading the signals first.
- Every answer includes one relevant metric, constraint, failure mode, or project example.
- You can compress an applied answer from two minutes to 45 seconds without losing the decision.
- You have recorded weak areas against the stable question IDs for later re-testing.
