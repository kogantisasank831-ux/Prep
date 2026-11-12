---
layout: week
week: 25
phase: 7
status: approved
version: 1.0.0
last_reviewed: 2026-11-12
estimated_hours: 8
permalink: /weeks/week-25/beginner/
title: "See what happens inside a small language-model training loop"
description: Learn next-token prediction, train and validation data, loss, learning rate, accumulated gradients and checkpoints step by step.
summary: Training repeatedly predicts the next token, measures error and makes a controlled update.
kicker_primary: Beginner path
kicker_secondary: From tokens to a reproducible update
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-25/
---

## Start with the one job

A causal language model reads earlier tokens and guesses the next one. In “the
invoice is due”, training examples include “the → invoice” and “the invoice →
is”. A tokenizer turns text into token IDs. Special beginning, end, unknown and
padding tokens have fixed jobs.

The [production route]({{ '/weeks/week-25/' | relative_url }}) adds optimiser
state, numerical precision and checkpoint recovery. The [assessment]({{ '/assessments/week-25/' | relative_url }})
draws a balanced ten-question paper.

## Keep practice and checking data separate

- **Training data** is used to update the model.
- **Validation data** is held back to check whether learning transfers.

Split complete documents first. If two pieces from the same document appear on
both sides, the validation result can reward memory. Build vocabulary from the
training side only.

## Understand one update

1. Encode a small batch of token sequences.
2. Ask the model for next-token probabilities.
3. Calculate loss: a confident wrong answer costs more.
4. Back-propagate to calculate gradients.
5. Let the optimiser make one bounded parameter update.
6. Repeat and periodically check held-out loss.

The learning rate controls update size. Warm-up starts cautiously; decay makes
later updates smaller. Gradient accumulation collects several small batches
before one update when a full batch does not fit in memory.

Mixed precision can make supported hardware faster and use less memory, but
very small numbers can disappear. That is why real runs watch finite loss and
gradient values instead of enabling a switch blindly.

## Save enough to continue

A checkpoint is more than weights. Exact continuation may also need optimiser
history, learning-rate position, random state, tokenizer, configuration and
dataset version. Test by stopping and resuming a tiny run.

## Run the CPU example

~~~shell
python -m labs.week_25.demo smoke
python -m pytest tests/test_week25_training.py -q
~~~

This example uses a small table of next-token scores. It is not a transformer.
Look for disjoint document IDs, the training-only vocabulary, lower training
loss, learning-rate changes and reproducible checkpoint digests.

## Completion checklist

- Describe next-token prediction in your own words.
- Explain why full documents are split first.
- Distinguish a micro-batch from an optimiser step.
- Explain warm-up, decay and accumulation.
- Name the state needed to resume training.
- Avoid treating lower training loss as proof of usefulness.

