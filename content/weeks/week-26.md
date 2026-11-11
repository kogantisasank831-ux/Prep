---
layout: week
week: 26
phase: 7
status: review
version: 1.0.0
last_reviewed: 2026-11-11
estimated_hours: 8
permalink: /weeks/week-26/
title: "Build a reproducible and lawful training-data pipeline"
description: Gate rights, language, quality, duplicates, contamination, source balance and personal information before producing versioned sequences.
summary: Model quality and risk inherit the data pipeline's provenance, exclusions, split discipline and reproducibility.
kicker_primary: Training-data engineering
kicker_secondary: Rights, quality, contamination and manifests
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-26/beginner/
---

## Begin with permission, not cleaning

The right to read a document is not automatically the right to train on it,
redistribute derivatives or retain it indefinitely. Record source, licence or
consent basis, permitted purpose, attribution, retention and deletion behavior.
Quarantine unknown rights. Automated filtering cannot make an unlicensed source
lawful.

The [beginner route]({{ '/weeks/week-26/beginner/' | relative_url }}) introduces
the pipeline in one pass. The [Week 26 assessment]({{ '/assessments/week-26/' | relative_url }})
checks decision order and limitations.

## Treat the pipeline as a versioned product

An auditable flow is:

**snapshot → rights gate → parse → normalise → language/quality gates → deduplicate → contamination check → PII handling → source mixing → grouped split → tokenise/pack → manifest**

Never silently discard records. Emit reason counts and representative samples
that reviewers can inspect without exposing sensitive content.

## Clean without erasing meaning

Parsing should preserve headings, tables, lists, code and document boundaries
when they matter. Normalisation can standardise Unicode and whitespace, but
aggressive boilerplate removal or punctuation stripping can destroy domain
meaning. Version every rule and test it on multilingual and structured cases.

Language identification is probabilistic for short or mixed text. Use a
confidence policy and a review path. Quality filters can consider length,
character composition, repetition, broken markup and source-specific signals;
one score should not become an unexplained truth label.

## Deduplicate at more than one level

- Exact hashes catch identical normalised text.
- Near-duplicate methods catch small edits or mirrored pages.
- Semantic comparison can find paraphrases but risks deleting legitimately
  distinct facts.

Run deduplication across train and held-out candidates before the final split.
Retain the chosen canonical record and its provenance. Deduplicating each split
independently leaves leakage between them.

## Protect evaluation from contamination

Contamination occurs when training contains benchmark questions, answers or
close variants. Keep evaluation data access controlled, compare fingerprints
and near-duplicate signatures, and inspect suspiciously high scores. A failed
match does not prove absence; document method coverage and residual risk.

## Handle personal information deliberately

Minimise collection before redaction. Detect direct identifiers and review
contextual identifiers, secrets and confidential business data. Replace values
only when the token preserves useful structure. Record counts, not raw PII, and
provide deletion propagation through raw snapshots, derived datasets and model
artefact governance. Regex catches some emails and phones; it is not a complete
privacy programme.

## Mix sources and split groups

Large sources can dominate training even when they add repetitive text. Declare
source weights or caps, observe accepted token counts and inspect representation
by language, domain, time and document type.

Split by the strongest leakage group: document family, customer, supplier,
thread, author or time boundary. Fit tokenizer/vocabulary state on training
only. Pack short documents efficiently only after deciding whether cross-
document attention is acceptable; preserve boundaries and masks.

## Make the output reproducible

A useful manifest includes input snapshot IDs and hashes, code/runtime version,
configuration digest, filter/rejection counts, source/token distribution,
split rule and seed, tokenizer identity, sequence policy, output hashes and
known limitations. Re-running against the same immutable inputs should produce
the same manifest.

## Run the bounded pipeline

~~~shell
python -m labs.week_26.demo smoke
python -m pytest tests/test_week26_data_pipeline.py -q
~~~

The lab uses explicit allowlists, minimum quality, exact normalised hashes,
benchmark fingerprints, per-source caps, simple email/phone redaction, stable
document splits and a training-only vocabulary. It intentionally omits
near-duplicate search, full PII recognition, immutable object storage and legal
review.

## Completion checklist

- Record permission and retention before accepting a source.
- Version cleaning and rejection rules.
- Deduplicate across candidate partitions.
- Check benchmark contamination and state coverage limits.
- Minimise and review personal or confidential information.
- Declare source mixing in accepted tokens.
- Split by leakage group before fitting tokenizer state.
- Produce a deterministic manifest with visible rejection evidence.

