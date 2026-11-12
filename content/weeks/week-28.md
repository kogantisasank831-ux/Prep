---
layout: week
week: 28
phase: 7
status: approved
version: 1.0.0
last_reviewed: 2026-11-12
estimated_hours: 8
permalink: /weeks/week-28/
title: "Prepare and evaluate instruction-tuning data"
description: Build diverse instruction-response examples, apply the exact chat template, mask prompt loss and detect memorisation.
summary: Supervised fine-tuning teaches response behavior only when examples, templates, masks and held-out evaluation match the intended contract.
kicker_primary: Supervised instruction tuning
kicker_secondary: Chat templates, response loss and diversity
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-28/beginner/
---

## Specify behavior before generating examples

Define task categories, inputs, required output schema, refusal/escalation
behavior, languages, difficulty and evaluation gates. A large collection of
loosely related conversations can blur the behavior you wanted to teach.

The [beginner route]({{ '/weeks/week-28/beginner/' | relative_url }}) explains
the format and mask visually. The [Week 28 assessment]({{ '/assessments/week-28/' | relative_url }})
checks data and evaluation decisions.

## Give every example a traceable schema

Store stable ID, source/group, category, instruction, optional context,
response, licence/consent, author or generator version, reviewer status and
quality flags. For structured tasks, validate the response against the same
schema used at inference. Remove secrets and personal data before training.

Human-written, transformed and synthetic examples each need review. A strong
model can generate fluent but incorrect labels; generating more copies does not
repair the error. Sample across categories and inspect both accepted and
rejected records.

## Use the model's exact chat template

A chat template converts roles into the token sequence expected by the base
model. System, user, assistant, tool and end markers differ across model
families. Applying the wrong template can waste training or create doubled
special tokens at inference.

Unit-test one rendered training sample against the model/tokenizer pair. Pin
tokenizer revision and template. Verify beginning/end tokens, role order,
truncation side and inference parity.

## Mask the intended loss

In response-only supervised fine-tuning, system and user prompt tokens provide
context but receive loss weight zero. Assistant response tokens—including the
chosen end token—receive weight one. Padding also receives zero. Otherwise the
model spends capacity reproducing prompts and metrics include tokens it is not
asked to generate.

Full-conversation loss can be intentional for some objectives, but it must be a
declared choice. Inspect masks after tokenisation and truncation; a malformed
mask can train on nothing or on the wrong role without a runtime error.

## Build diversity without leakage

Balance task, intent, difficulty, length, format, positive/negative outcome and
language. Include missing information, ambiguity, conflicts, safe refusals and
schema errors. Avoid thousands of surface-level rewrites of one template.

Deduplicate normalised instruction-response pairs and near duplicates. Split by
source, scenario or template family so variations cannot cross train and
validation. Fit data-dependent preprocessing on training only.

## Prevent silent truncation and bad packing

Measure token lengths after applying the chat template. Reject, revise or
explicitly truncate over-limit examples; do not silently cut off the response
or JSON closing brace. Packing can combine short examples into one sequence for
efficiency, but preserve boundaries, labels, attention policy and loss masks.

## Diagnose overfitting

Track training and held-out response loss plus task metrics such as exact match,
schema validity, class F1 or rubric scores. Memorised training answers can look
excellent while new phrasing fails. Compare base, prompted base and adapted
model on unseen source groups, and inspect category-level errors.

## Run the data and memorisation lab

~~~shell
python -m labs.week_28.demo smoke
python -m pytest tests/test_week28_instruction.py -q
~~~

The lab removes exact duplicate pairs, keeps sources within one partition,
applies explicit role tokens, fits vocabulary on training only, masks prompt
and padding tokens, and creates aligned batches. Its lookup baseline scores 100%
on memorised training instructions and 0% on unseen validation instructions.
That contrast teaches leakage; it is not a transformer training result.

## Real SFT experiment evidence

Record dataset card and manifest, base/tokenizer revisions, template, maximum
length, packing policy, response-mask test, adapter settings, effective token
batch, hardware, checkpoints and all evaluation suites. Review sampled model
outputs for factuality, format, privacy, refusal and domain errors before any
release claim.

## Completion checklist

- Define behavior and evaluation categories before writing data.
- Preserve source, rights, generation and review provenance.
- Pin and test the exact chat template.
- Verify response-only and padding masks after tokenisation.
- Split by source/template family and remove near duplicates.
- Reject or document truncation explicitly.
- Compare held-out behavior with base and prompted baselines.
- Treat memorisation as failure evidence, not model quality.

