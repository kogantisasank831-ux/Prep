---
layout: "week"
status: "review"
version: "1.1.0"
last_reviewed: "2026-11-09"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "Senior Data Scientist foundation interview bank"
description: "Twenty guided foundation questions for Senior Data Scientist interviews."
summary: "Practise SQL, statistics, leakage-safe ML, metrics, cases, explainability, monitoring, and defensible business impact."
permalink: "/interview-prep/roles/senior-data-scientist/"
kicker_primary: "Senior Data Scientist"
kicker_secondary: "Batches 1–2 · 40 guided questions"
current_label: "Role bank"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
question_count: 40
---
## How to use this bank

These are interview-practice prompts, not a scored learning assessment. Answer aloud before opening the revision links. A strong response should state assumptions, make a decision, explain trade-offs, and identify evidence or failure modes. Use the follow-up probe to test whether the answer survives a deeper round.

### Suggested practice loop

1. Select five questions from different sections.
2. Give a 90-second answer without notes.
3. Compare your answer with the strong-answer signals.
4. Open only the revision sheet needed for the gap.
5. Repeat the answer in 45 seconds, then record one concrete project example.

**Bank size:** 40 questions across Batches 1–2 · **Status:** Batch 1 approved; Batch 2 review candidate

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


## Completion evidence

- You can answer at least 16 of 20 questions in each batch without reading the signals first.
- Every answer includes one relevant metric, constraint, failure mode, or project example.
- You can compress an applied answer from two minutes to 45 seconds without losing the decision.
- You have recorded weak areas against the stable question IDs for later re-testing.
