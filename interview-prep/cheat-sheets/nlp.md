---
layout: "week"
status: "approved"
version: "1.0.0"
last_reviewed: "2026-11-09"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "Natural language processing interview cheat sheet"
description: "End-to-end NLP revision covering text data, tokenization, classical and neural models, evaluation, and production failures."
summary: "Revise text representation, tokenization, TF-IDF, embeddings, classification, sequence labeling, generation metrics, data quality, and multilingual systems."
permalink: "/interview-prep/cheat-sheets/nlp/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 2 · NLP"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 2 source:** This page integrates the prepared revision artifact into the Prep site. It is separate from the Week 1–20 learning assessments.

**Target roles:** AI Engineer, NLP Engineer, Applied Scientist, Senior/Lead Data Scientist  
**Goal:** understand the full text pipeline—from data and tokenization through classical/deep models, evaluation, and production failure modes.

## 1. Thirty-second revision

- Text must be represented numerically; the representation and objective determine what information the model can learn.
- Classical TF-IDF + linear models remain strong, fast, interpretable baselines.
- Tokenization is part of the model contract: changing it invalidates vocabulary IDs and usually the checkpoint.
- Word embeddings are static per token; contextual models produce representations dependent on surrounding text.
- RNN/LSTM/GRU process sequences recurrently; transformers use attention for parallel context modeling.
- Choose metrics per task: macro F1 for imbalanced classes, entity-level span F1 for NER, perplexity for next-token likelihood, and human/task evaluation for generation.
- Data leakage, duplicates, annotation inconsistency, language mix, and train-serving preprocessing drift are frequent causes of misleading NLP results.

## 2. NLP task map

| Task | Input → output | Typical metrics |
|---|---|---|
| Text classification | Document → class(es) | F1, PR-AUC, calibration |
| Intent detection | Utterance → intent | Macro F1, reject/unknown accuracy |
| Sentiment | Text → polarity/score | F1, MAE, calibration |
| NER | Tokens → entity spans/types | Entity-level precision/recall/F1 |
| Information extraction | Text → structured fields/relations | Exact/field/span F1, schema validity |
| Semantic similarity | Pair → similarity score | Spearman/Pearson, retrieval metrics |
| Search/retrieval | Query → ranked documents | Recall@K, MRR, NDCG |
| Translation | Source → target text | COMET/human review; BLEU as limited proxy |
| Summarization | Document → summary | ROUGE, factuality, coverage, human/task metrics |
| Language modeling | Prefix → next token | Cross-entropy, perplexity, downstream eval |
| Question answering | Question/context → answer | Exact match, token/span F1, groundedness |

No single automatic metric proves generated-text quality.

## 3. Text normalization

Possible operations:

- Unicode normalization;
- case folding/lowercasing;
- whitespace normalization;
- punctuation or accent handling;
- URL, email, number, emoji placeholders;
- spelling correction;
- sentence segmentation;
- stemming or lemmatization;
- stop-word handling.

### Do not normalize blindly

- Case can distinguish entities/acronyms.
- Punctuation and emoji carry sentiment/intent.
- Numbers may be decisive for finance, dates, dosages, or versions.
- Code, formulas, IDs, and multilingual text can be damaged.
- Modern pretrained tokenizers expect preprocessing compatible with pretraining.

Fit/lock preprocessing as a versioned part of the model and apply exactly the same logic at inference.

## 4. Tokenization

### Word-level

Simple and interpretable, but large vocabulary and many out-of-vocabulary words.

### Character-level

Handles arbitrary strings and morphology but creates long sequences and makes semantic learning harder.

### Subword-level

Balances vocabulary size and sequence length; composes uncommon words from common pieces.

| Method | Core idea | Interview distinction |
|---|---|---|
| BPE | Repeatedly merge frequent symbol pairs | Frequency-based merge vocabulary |
| WordPiece | Choose merges using a likelihood-style objective | Commonly associated with BERT tokenization |
| Unigram LM | Start with large vocabulary and prune pieces by likelihood impact | Probabilistic segmentation |
| SentencePiece | Trains directly on raw text; supports BPE/unigram | Treats whitespace as a symbol; language-agnostic pipeline |

Important special tokens may represent padding, unknown text, start/end, separator, mask, system/user roles, or multimodal placeholders.

### Padding and masks

- Padding makes batch tensors equal length.
- Attention/loss masks ensure padding does not influence representations or loss.
- Left versus right padding can matter for decoder-only generation and implementation.
- Truncation strategy must match the task; keeping only the beginning may remove the answer.

## 5. Vocabulary and OOV trade-offs

- Larger vocabulary: shorter sequences, larger embedding/output matrices, more rare pieces.
- Smaller vocabulary: longer sequences, smaller matrices, better compositional coverage.
- Domain-specific tokenizer: may improve specialized compression but breaks compatibility with pretrained embeddings/checkpoints unless adapted carefully.
- Multilingual tokenizer: shares pieces across languages, sometimes at the cost of inefficient representation for low-resource scripts.

Measure tokens per document, truncation rate, unknown rate, language slices, and downstream quality.

## 6. Bag of words, n-grams, and TF-IDF

### Bag of words

Represents a document by token counts; ignores order.

### N-grams

Add local order such as `not good`. They improve expressiveness but increase sparsity and vocabulary size.

### TF-IDF

One common form:

$$
TFIDF(t,d)=TF(t,d)\times\log\frac{N+1}{DF(t)+1}
$$

TF emphasizes terms frequent in a document; IDF downweights terms common across documents.

### Strong classical baseline

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

classifier = Pipeline(
    steps=[
        (
            "tfidf",
            TfidfVectorizer(
                ngram_range=(1, 2),
                min_df=3,
                max_df=0.98,
                sublinear_tf=True,
            ),
        ),
        ("model", LogisticRegression(max_iter=1_000)),
    ]
)
```

Fit vocabulary/IDF only on training folds. Group duplicates/templates/senders when splitting if they could leak.

## 7. Sparse retrieval and BM25

BM25 improves on raw TF-IDF using term-frequency saturation and document-length normalization. Conceptually:

$$
score(q,d)=\sum_{t\in q}IDF(t)\cdot
\frac{TF(t,d)(k_1+1)}{TF(t,d)+k_1(1-b+b|d|/avgdl)}
$$

Strengths: exact terms, IDs, product names, rare keywords, transparent behavior. Weaknesses: vocabulary mismatch and limited semantic equivalence. Hybrid retrieval combines sparse and dense signals; detailed RAG coverage belongs in Batch 3.

## 8. Static word embeddings

### Word2Vec

- CBOW predicts a target word from context.
- Skip-gram predicts surrounding words from a target.
- Negative sampling turns a full-vocabulary objective into sampled binary decisions.

### GloVe

Learns vectors from global word co-occurrence statistics.

### Limitations

- One vector per token cannot represent polysemy: “bank” in finance versus river bank.
- OOV handling depends on vocabulary; subword/character approaches help.
- Embeddings may encode bias from training data.
- Vector analogies are not a general guarantee of semantic reasoning.

## 9. Contextual embeddings

Contextual models generate a different representation for a token depending on surrounding tokens. Uses:

- token-level states for NER/tagging;
- pooled/special-token representation for classification;
- sentence embeddings trained for semantic similarity/retrieval;
- decoder states for autoregressive generation.

Do not assume a raw language-model hidden state is an optimal sentence embedding; use an objective/model trained for the similarity task and evaluate retrieval quality.

## 10. Language models and perplexity

Autoregressive factorization:

$$
P(x_1,\ldots,x_T)=\prod_{t=1}^{T}P(x_t\mid x_{<t})
$$

Token-average cross-entropy:

$$
H=-\frac{1}{T}\sum_{t=1}^{T}\log P(x_t\mid x_{<t})
$$

Perplexity:

$$
PPL=e^H
$$

Lower perplexity means the model assigns higher likelihood to the reference tokens under the same tokenizer/evaluation contract. Perplexity is not directly comparable across different tokenizers and does not prove factuality or usefulness.

## 11. RNNs

$$
h_t=\phi(W_xx_t+W_hh_{t-1}+b)
$$

Advantages: natural sequential state and streaming. Limitations: sequential computation and vanishing/exploding gradients across long dependencies.

### Bidirectional RNN

Combines left-to-right and right-to-left states for tasks with full input available. It cannot be used causally when future tokens are unavailable.

## 12. LSTM and GRU

LSTM uses input, forget, and output gates plus a cell state. The additive state path improves long-range gradient flow.

GRU combines gates into a simpler update/reset structure, often using fewer parameters.

| Model | Strength | Limitation |
|---|---|---|
| Vanilla RNN | Simple, light | Weak long-range gradients |
| LSTM | Explicit memory/gating | More parameters and sequential compute |
| GRU | Simpler gated recurrence | Still sequential; architecture choice is empirical |

## 13. Sequence-to-sequence and attention

Classic encoder-decoder compresses source sequence into a representation; attention lets the decoder dynamically weight encoder states.

Additive attention concept:

$$
e_{t,s}=v^T\tanh(W_hh_s+W_qq_{t-1})
$$

$$
\alpha_{t,s}=softmax(e_{t,s}),\qquad
c_t=\sum_s\alpha_{t,s}h_s
$$

This reduced the fixed-vector bottleneck and led toward transformer attention.

## 14. Text classification workflow

1. Define label taxonomy, unknown/other policy, hierarchy, and action.
2. Deduplicate and split by entity/template/time as deployment requires.
3. Build majority/rule and TF-IDF + linear baselines.
4. Compare pretrained encoder fine-tuning if data/value justify it.
5. Tune threshold and calibration to business cost/capacity.
6. Analyze slices: language, length, source, rare intent, ambiguous labels.
7. Add reject/abstain route for low confidence or unseen intents.

### Multi-class versus multi-label

- Multi-class: exactly one label; softmax + cross-entropy.
- Multi-label: zero or more labels; independent sigmoid outputs + binary cross-entropy; thresholds may differ by label.

## 15. Named entity recognition

### Representations

- BIO/BILOU token tags;
- start/end span prediction;
- structured generation with validation;
- span classification.

Evaluate exact entity spans and types. Token accuracy is misleading when `O` dominates.

Subword problem: a word may split into several pieces. Common strategies label only the first piece or propagate a compatible tag with masked loss; reconstruct and evaluate original spans carefully.

## 16. Information extraction

Pipeline choices:

- rules/regex for stable, precise formats;
- token/span classifiers for fixed schemas;
- sequence-to-sequence/LLM structured output for complex documents;
- hybrid candidates + validator.

Evaluate per-field exactness, normalization, missing/extra fields, semantic constraints, and document slices. JSON validity alone does not mean correct extraction.

## 17. Similarity and sentence embeddings

### Bi-encoder

Encode query and document independently; fast retrieval and reusable document embeddings.

### Cross-encoder

Encode query-document pair jointly; stronger interaction modeling but expensive per pair. Often reranks a small candidate set.

### Similarity

$$
cosine(a,b)=\frac{a\cdot b}{\|a\|\|b\|}
$$

Dot product equals cosine only if vectors are normalized. The correct metric depends on model training and index configuration.

## 18. Generation and decoding awareness

- Greedy: highest-probability token; deterministic but may be myopic.
- Beam search: keeps several high-likelihood sequences; useful in constrained tasks but can produce generic text.
- Temperature: scales logits; lower is sharper.
- Top-k: sample from k highest-probability tokens.
- Top-p/nucleus: sample from smallest set whose cumulative probability reaches p.

Generation quality needs task/factual/safety evaluation, not only likelihood.

## 19. Evaluation by task

### Classification

- macro/micro/weighted F1;
- PR-AUC for rare classes;
- confusion matrix and per-class recall;
- calibration and reject accuracy;
- latency/cost.

### NER/extraction

- exact/partial span precision, recall, F1;
- correct type and normalized value;
- schema and semantic validation;
- document/source/language slices.

### Generation

- reference-overlap metrics are limited;
- factual consistency/groundedness;
- coverage and omission;
- task success and human rubric;
- toxicity/privacy/policy;
- pairwise comparison and uncertainty.

### Retrieval

- Recall@K for candidate coverage;
- MRR for first relevant result;
- NDCG for graded ranking;
- hard-negative and tail-query slices.

## 20. Data and annotation quality

- Write label definitions with positive, negative, and edge examples.
- Measure annotator agreement and adjudicate disagreement.
- Separate ambiguous/unknown from forced labels.
- Track source, language, timestamp, template, and annotator provenance.
- Remove exact/near duplicates before splitting.
- Audit representation across languages, dialects, domains, and long-tail intents.
- Preserve a challenge set of real failure modes.

Low agreement may indicate a bad taxonomy rather than weak annotators.

## 21. Multilingual and code-switched NLP

- Language identification may be sentence- or segment-level.
- Unicode/script and transliteration matter.
- Shared multilingual models enable transfer but capacity/token efficiency differs by language.
- Translation-based pipelines introduce translation error and latency.
- Evaluate per language/script and code-switch pattern.
- Use native-speaker/domain review for consequential tasks.
- Do not infer fairness from aggregate multilingual accuracy.

## 22. Production concerns

- Version tokenizer, vocabulary, preprocessing, model, label map, and thresholds together.
- Define maximum length and truncation/chunking behavior.
- Batch by approximate length to reduce padding waste.
- Monitor token length, unknown/rare pieces, language mix, score drift, reject rate, and latency.
- Protect PII in training data, prompts, logs, and error examples.
- Add fallback/human review for unknown intents and extraction uncertainty.
- Re-evaluate when taxonomy, upstream text, tokenizer, or model changes.

## 23. Common traps

| Trap | Better reasoning |
|---|---|
| Remove all punctuation/stop words | Preserve signals required by task/model |
| Random split duplicated templates | Group/deduplicate before split |
| Token accuracy for NER | Use entity-level span/type metrics |
| Perplexity compared across tokenizers | Comparison needs identical tokenization/eval contract |
| Raw encoder state assumed semantic embedding | Use similarity-trained embeddings and retrieval eval |
| BLEU/ROUGE treated as truthfulness | Add factuality, task, and human evaluation |
| New tokenizer with old checkpoint | Token IDs/embeddings are incompatible without adaptation |
| Force every intent | Add unknown/reject route and coverage metrics |
| Translate everything to English | Measure translation loss, latency, privacy, and native alternatives |

## 24. Rapid interview questions and answers

1. **Stemming versus lemmatization?** Stemming applies crude affix rules; lemmatization uses vocabulary/morphology to return a canonical lemma.
2. **Why TF-IDF remains useful?** It is fast, sparse, interpretable, strong on keyword-driven tasks, and an essential baseline.
3. **BPE versus WordPiece?** Both build subwords; BPE merges frequent pairs, while WordPiece commonly selects pieces using a likelihood-style criterion.
4. **Static versus contextual embedding?** Static gives one vector per token; contextual representation changes with surrounding text.
5. **Why LSTM over vanilla RNN?** Gates and cell state improve selective memory and gradient flow.
6. **Bi-encoder versus cross-encoder?** Bi-encoder scales retrieval via independent embeddings; cross-encoder is slower but models rich pair interactions for reranking.
7. **Why is macro F1 useful?** It gives each class equal influence and exposes failure on rare classes.
8. **What is perplexity?** Exponentiated average token cross-entropy under a fixed tokenization/evaluation contract.
9. **How handle unseen intent?** Calibrated rejection/unknown class, out-of-scope data, monitoring, and human routing.
10. **Main NLP leakage source?** Duplicate templates/entities or information created after the label/prediction time crossing splits.

## 25. Lead-level case

**Question:** Build a multilingual support-ticket router for 50 intents, with new intents introduced every month.

**Strong answer structure:**

1. Define languages, intent hierarchy, multi-label rules, unknown/escalation policy, SLA, and routing cost.
2. Audit historic labels, duplicates, templates, customer/source groups, and time drift.
3. Establish keyword/rule and TF-IDF + logistic-regression baselines; compare multilingual encoder.
4. Use time/group-aware validation and report macro F1, per-intent recall, calibration, unknown detection, and routing cost.
5. Add language/script slices and native-review challenge set.
6. Use hierarchical routing or candidate retrieval when taxonomy grows; avoid retraining assumptions without measurement.
7. Version taxonomy, label mapping, tokenizer, preprocessing, model, and thresholds.
8. Route low-confidence/novel tickets to humans and feed adjudicated outcomes back safely.
9. Shadow new versions, monitor class/language mix, reject rate, queue impact, latency, and confirmed misroutes.
10. Define controlled onboarding for new intents: examples, confusion review, regression set, and rollback.

## 26. Final revision checklist

- [ ] I can compare word, character, and subword tokenization.
- [ ] I can build and defend a TF-IDF baseline.
- [ ] I understand Word2Vec, static/contextual embeddings, and similarity.
- [ ] I can explain RNN, LSTM, GRU, seq2seq, and attention.
- [ ] I can choose output/loss/metrics for classification, NER, extraction, and generation.
- [ ] I can handle multilingual, unknown, and long-tail cases.
- [ ] I can identify duplicate/template/entity/time leakage.
- [ ] I can version and monitor the full tokenizer-preprocessing-model contract.

## Primary references

- [Hugging Face documentation](https://huggingface.co/docs)
- [Hugging Face Tokenizers](https://huggingface.co/docs/tokenizers/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)
