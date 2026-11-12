---
layout: week
week: 29
phase: 7
status: review
version: 1.0.0
last_reviewed: 2026-11-11
estimated_hours: 8
permalink: /weeks/week-29/beginner/
title: "Test four model approaches on the same questions"
description: Compare base, prompted, fine-tuned and RAG answers using task metrics, clean test data and human review.
summary: A fair evaluation changes the candidate, not the questions or scoring rules.
kicker_primary: Beginner path
kicker_secondary: One frozen test set and several kinds of evidence
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-29/
---

## Make the comparison fair

Use the same test questions for the base model, prompted base, fine-tuned model
and RAG system. Decide the expected answers and scoring rules first. Record every
failure rather than dropping it.

The [production route]({{ '/weeks/week-29/' | relative_url }}) adds segmented
metrics, paired uncertainty and judge validation. The [assessment]({{ '/assessments/week-29/' | relative_url }})
draws ten balanced questions.

## Use metrics for different questions

- **Perplexity:** how surprising held-out tokens are; lower is better only for
  comparable tokenisation and text.
- **Exact match:** whether a normalised answer is exactly expected.
- **Precision:** how often a predicted positive is correct.
- **Recall:** how many real positives were found.
- **F1:** one balance of precision and recall.
- **Human pairwise preference:** which anonymous output a reviewer prefers.

No single metric proves overall quality. Exact match may reject a correct
paraphrase, and a preferred answer may still contain an unsupported fact.

## Protect the test

Do not train on evaluation questions or answers. Check duplicates and close
copies. Keep related examples together. Report results by task or difficulty so
a strong average cannot hide one weak group.

## Treat judges as tools, not truth

People should use a clear rubric and see anonymous outputs in random order. An
LLM judge should also use a fixed rubric, but its scores can change with model,
prompt, answer order or verbosity. Compare it with human labels before trusting
it.

## Run the example

~~~shell
python -m labs.week_29.demo smoke
python -m pytest tests/test_week29_evaluation.py -q
~~~

Find the five clean test IDs and one excluded contaminated ID. Compare exact
match, classification metrics, perplexity, segment results and pairwise votes.
The numbers are intentionally synthetic.

## Completion checklist

- Use the same questions and scoring rules for every candidate.
- Keep contaminated cases out of the main result.
- Explain what each metric does and does not show.
- Count timeouts and invalid answers as outcomes.
- Review results by important segment.
- Blind pairwise human review.
- State which approach wins each requirement and why.

