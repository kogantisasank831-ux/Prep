---
layout: week
week: 25
phase: 7
status: approved
version: 1.0.0
last_reviewed: 2026-11-12
estimated_hours: 8
permalink: /weeks/week-25/
title: "Understand a causal language-model training loop"
description: Trace data splitting, tokenisation, next-token loss, optimisation, accumulation, mixed precision and recoverable checkpoints.
summary: A useful training experiment starts with a leakage-safe objective and a reproducible loop, not with a large model.
kicker_primary: Optional LLM training experiment
kicker_secondary: Causal objective, optimiser state and reproducibility
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-25/beginner/
---

## Before you start

This optional phase should not delay applications or interview practice. Use the
[beginner route]({{ '/weeks/week-25/beginner/' | relative_url }}) if gradients,
tokens and checkpoints are new. The [Week 25 assessment]({{ '/assessments/week-25/' | relative_url }})
checks the contracts rather than memorised framework calls.

The local lab is deliberately a **bigram causal surrogate, not a transformer**.
It lets you inspect every loss and update on CPU. The separate stretch exercise
is to train a genuinely tiny transformer in an isolated framework environment.

## Define the learning problem first

A causal language model predicts the next token from earlier tokens. For tokens
\(x_1,\ldots,x_T\), it models
\(p(x_t\mid x_1,\ldots,x_{t-1})\). Training minimises average negative
log-likelihood, usually called token cross-entropy:

\[
\mathcal{L}=-\frac{1}{N}\sum_{t=1}^{N}\log p(x_t\mid x_{<t}).
\]

Shifting inputs and labels by one position is therefore part of the objective,
not a formatting convenience. Padding tokens must be excluded from loss. A
decreasing training loss shows that optimisation is fitting the training data;
it does not prove factuality, usefulness, safety or held-out generalisation.

## Split documents before fitting anything

Create train and validation partitions at the document or source-group level
before vocabulary fitting, sequence construction or augmentation. Sentence- or
chunk-level random splits can place near-identical text in both partitions.
Fit the tokenizer or vocabulary on training data, then map unseen validation
tokens through the declared unknown-token behavior.

Record source snapshot, licence, filtering version, split rule and seed. A seed
cannot reproduce a dataset that changed underneath it.

## Tokenisation creates the model's interface

Production tokenizers commonly use subword units so uncommon words can be
represented without a huge word vocabulary. Vocabulary size changes embedding
and output-layer parameters; sequence length changes attention compute and
activation memory. Special tokens need declared semantics and stable IDs.

Inspect samples after encoding and decoding. Check languages, numbers, domain
terms, Unicode, control text and the rate of unknown or fragmented tokens. Do
not compare runs whose token counts or sequence construction silently differ.

## Make the optimiser state explicit

An optimiser turns gradients into parameter updates. AdamW is common for
transformers because it combines adaptive moments with decoupled weight decay,
but its defaults are not universal evidence. Track:

- optimiser and all hyperparameters;
- global batch in tokens, not only examples;
- gradient norm and clipping;
- update count, not only epochs;
- learning-rate value at each update; and
- training and validation loss on comparable tokens.

A warm-up gradually raises learning rate while early moments are unreliable. A
decay schedule then reduces it. The schedule should advance on optimiser steps,
not micro-batches.

Gradient accumulation sums several micro-batch gradients before an optimiser
step. It can emulate a larger batch when scaling and loss normalisation match,
but dropout, batch-dependent operations, clipping and distributed reduction can
prevent exact equivalence. It reduces activation-memory pressure; it does not
make each token free.

## Use precision deliberately

Mixed precision retains selected state in higher precision while using lower
precision for supported compute and storage. FP16 often needs dynamic loss
scaling to avoid underflow; BF16 has a wider exponent range but needs compatible
hardware. Validate finite loss, gradient norms and throughput. “Runs without an
exception” is not a numerical-stability result.

## Design checkpoints for resumption

A resumable checkpoint normally needs model weights, optimiser moments,
scheduler position, gradient-scaler state, completed update, random states,
configuration, tokenizer identity and data/split version. Saving only weights
supports inference or restart-from-weights, not exact training continuation.

Test restoration: interrupt a short run, restore it and compare the next update
with an uninterrupted control within a declared tolerance. Keep a bounded
retention policy and verify files before deleting earlier checkpoints.

## Run the inspectable lab

~~~shell
python -m labs.week_25.demo smoke
python -m pytest tests/test_week25_training.py -q
~~~

The lab hashes stable document IDs, fits vocabulary only on training documents,
creates beginning-to-end next-token pairs, applies scheduled SGD with gradient
accumulation and records checkpoint digests. It omits attention, embeddings,
mixed-precision kernels, distributed workers and checkpoint restoration.

## Stretch: a genuinely tiny transformer

Use only public or synthetic text whose licence permits the experiment. Pin the
framework, tokenizer and model configuration. Keep the parameter count and
corpus small enough for a bounded run, then record hardware, wall time, tokens,
peak memory, loss curves and a held-out comparison. Do not call the result a
useful LLM; the objective is to explain the loop and its failure modes.

## Completion checklist

- Explain causal shifting and padding-loss masking.
- Split whole documents before fitting vocabulary or tokenizer state.
- Report global token batch and optimiser updates.
- Advance warm-up and decay on optimiser steps.
- Explain accumulation limits and mixed-precision risks.
- Save and test all state required for recovery.
- Compare train and validation loss without claiming task quality.
- Label the local surrogate and tiny-transformer experiment honestly.

