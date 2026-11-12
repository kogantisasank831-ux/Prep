---
layout: week
week: 29
phase: 7
status: approved
version: 1.0.0
last_reviewed: 2026-11-12
estimated_hours: 8
permalink: /weeks/week-29/
title: "Compare base, prompted, fine-tuned and RAG systems fairly"
description: Freeze tasks and baselines, use task metrics and paired uncertainty, and keep human or LLM-judge evidence within its limits.
summary: A defensible model comparison uses the same uncontaminated cases, multiple metrics, segmented errors and explicit uncertainty.
kicker_primary: Model evaluation
kicker_secondary: Comparable baselines, contamination and human judgment
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-29/beginner/
---

## Start with a decision, not a leaderboard

Write the decision the evaluation supports: whether adaptation adds enough
domain behavior to justify its cost, whether RAG is better for changing facts,
or whether the prompted base already meets the release gate. Freeze the test
cases, metric definitions and thresholds before looking at final candidate
results.

The [beginner route]({{ '/weeks/week-29/beginner/' | relative_url }}) introduces
the metric families. The [Week 29 assessment]({{ '/assessments/week-29/' | relative_url }})
checks fair comparison and limitations.

## Hold the comparison constant

Evaluate these candidates on the same eligible examples:

1. unchanged base model;
2. prompted base model;
3. fine-tuned model with its exact template; and
4. RAG system with versioned retriever, corpus and prompt.

Keep decoding settings, output schema, time/cost measurement boundary and
failure policy explicit. Candidate-specific instructions may be necessary, but
record them: a weak base prompt makes the fine-tune comparison meaningless.
Require exactly one terminal result per candidate and example, including
timeouts, refusals and invalid outputs.

## Separate language-model loss from task success

Perplexity is exponentiated average token negative log-likelihood. It measures
how surprising held-out tokens are under a model and is only comparable when
tokenizer, token set and loss masking match. It does not directly measure
factual QA, instruction following or safety, and API-only/RAG systems may not
expose comparable token probabilities.

Use task-specific metrics for the behavior you need:

- exact match for canonical short answers or strict structured fields;
- schema-valid rate for structured output;
- precision, recall and F1 for classification;
- retrieval recall and citation support for RAG;
- task completion, unsafe action and escalation for agents; and
- latency and cost per accepted task for operations.

Publish exact normalisation rules. Exact match can reject a valid paraphrase,
while a loose substring rule can reward a wrong answer that happens to contain
the expected term.

## Interpret classification metrics with the use case

Define the positive class. Precision asks how many predicted positives were
correct; recall asks how many actual positives were found. F1 balances both but
does not encode business cost. Include confusion matrices, class support and
macro/weighted choices for multiclass tasks. Accuracy can look strong when the
important class is rare.

## Segment before averaging

Report performance by task, source, language, difficulty, length, new versus
seen entity, answerability and safety category. A mean can improve while a
critical subgroup regresses. Keep a fixed regression suite plus a separately
versioned challenge set; do not repeatedly tune against the final test.

## Exclude and investigate contamination

Compare evaluation fingerprints and near-duplicate signatures against all
training and retrieval corpora. Exclude declared contaminated cases from the
primary result and report them separately. Suspiciously high scores on known
phrasing are evidence to investigate, not a success to hide. A negative
contamination scan has bounded coverage.

## Add paired uncertainty

Because every candidate sees the same cases, compare paired correctness or
score differences. Bootstrap the example IDs to estimate an interval around
the mean delta. Report sample size and seed. An interval describes variation
within the supplied sample; it does not correct biased labels, missing segments
or dependence between near-duplicate examples.

## Run human pairwise evaluation carefully

For qualities that automated metrics miss, show reviewers the input and two
anonymised, randomised outputs. Use a rubric with win, loss, tie and critical-
error definitions. Collect multiple reviewers on a subset and report agreement,
ties and adjudication. Never let candidate name or output position determine the
presentation.

Pairwise preference is not absolute correctness. Reviewers can prefer confident
but unsupported prose, so retain factual and safety checks separately.

## Bound LLM-as-judge evidence

An LLM judge can scale rubric application, but it may be biased toward verbosity,
position, shared model style or reference phrasing. It is prompt- and version-
sensitive and can be vulnerable to instructions inside the candidate output.
Pin judge model and prompt, randomise positions, validate against human labels,
measure agreement and route material disagreements to people. Do not use one
unvalidated judge score as a release gate.

## Run the comparable synthetic evaluation

~~~shell
python -m labs.week_29.demo smoke
python -m pytest tests/test_week29_evaluation.py -q
~~~

The lab requires a complete candidate-by-example matrix, excludes a declared
contaminated case, calculates exact match, binary precision/recall/F1,
synthetic-token perplexity, segment scores, paired bootstrap deltas and separate
blind pairwise counts. The constructed ordering where RAG wins factual cases is
a teaching fixture, not evidence that RAG always wins.

## Write the evaluation conclusion

State which candidate meets which gate, the size and uncertainty of improvements,
regressed segments, invalid/failure rate, latency and cost, human/judge evidence,
contamination findings and limitations. A useful result can be “prompting is
sufficient” or “RAG beats tuning on current facts.” Negative results prevent
needless serving complexity.

## Completion checklist

- Freeze cases, metrics and thresholds before final comparison.
- Evaluate all four candidates on the same eligible records.
- Keep perplexity separate from task and safety quality.
- Report class support, segments, invalid outputs and failures.
- Exclude and disclose contamination.
- Use paired deltas with bounded uncertainty.
- Blind and randomise human pairwise review.
- Validate an LLM judge against people before using it.
- Include latency and cost per accepted task in the decision.

