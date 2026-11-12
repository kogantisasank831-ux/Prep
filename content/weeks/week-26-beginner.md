---
layout: week
week: 26
phase: 7
status: approved
version: 1.0.0
last_reviewed: 2026-11-12
estimated_hours: 8
permalink: /weeks/week-26/beginner/
title: "Turn raw documents into safe, repeatable training data"
description: Follow a simple path through permission, cleaning, duplicates, private data, splitting, tokenisation and a manifest.
summary: Good training data is permitted, traceable, cleaned consistently and kept separate from evaluation.
kicker_primary: Beginner path
kicker_secondary: A visible decision for every accepted document
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-26/
---

## Ask whether the data may be used

Publicly visible does not always mean permitted for model training. Save the
source and licence or consent. If permission is unclear, keep the document out
until reviewed. The [production route]({{ '/weeks/week-26/' | relative_url }})
adds source mixing, grouped leakage controls and manifests. Use the
[assessment]({{ '/assessments/week-26/' | relative_url }}) after the lab.

## Follow one visible pipeline

1. Load a fixed snapshot and keep document IDs.
2. Reject sources without approved rights.
3. Clean encoding, whitespace and known boilerplate carefully.
4. Check language and basic quality.
5. remove exact and near duplicates.
6. compare against the evaluation set for contamination.
7. remove or replace personal and confidential information.
8. prevent one source from overwhelming the rest.
9. split whole document groups into train and validation.
10. tokenise, create fixed sequences and write a manifest.

Keep a rejection reason. “The final file has 5,000 rows” is less useful than
knowing how many were rejected for rights, duplicates, private information or
quality.

## Know the common traps

- Splitting chunks from one document can leak content.
- Cleaning train and validation separately can miss duplicates between them.
- An email regex does not find every kind of private information.
- A language detector can be uncertain on short text.
- Removing all punctuation can damage numbers and tables.
- A random seed does not help if the source files changed.

## Run the example

~~~shell
python -m labs.week_26.demo smoke
python -m pytest tests/test_week26_data_pipeline.py -q
~~~

Read the accepted documents, rejection reasons, redaction counts, split labels,
fixed-length sequences and two hashes. Change one configuration value and see
the configuration hash change.

## Completion checklist

- Explain why permission is checked first.
- Keep a reason for every excluded record.
- Separate duplicates from evaluation contamination.
- Split whole related groups.
- Build vocabulary only from training data.
- State why simple redaction is incomplete.
- Save a manifest that another person can reproduce.

