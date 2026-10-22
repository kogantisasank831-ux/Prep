# Week 9: evaluate the stage that lost the answer

Run the Week 8 procurement assistant on thirty versioned synthetic practice
questions. Retain source audits, ranked evidence, final context/citations,
actual answers, explicit metric contracts and pending semantic review.

This lab adds evaluation, not a new answer generator. The assistant still uses
the named teaching dense/pair scorers and emits cited source excerpts. The
default run does not download models, call an LLM judge or install another
evaluation framework. Earlier-week source and application interfaces are
unchanged.

## Run

From the repository root:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m labs.week_09.run --output-dir .runtime/week09-default
.venv/bin/python -m pytest tests/test_week09_evaluation.py -q
```

On Windows use `.venv\Scripts\python.exe`. Output directories must be fresh;
existing results are never overwritten. The CLI prints the summary and saves:

| File | Contents |
| --- | --- |
| `summary.json` | Input/system identity, source audit, metric means, categories, failures and review status |
| `results.jsonl` | One actual result per question: scope, references, expected evidence, answer, spans/offsets, ranking keys, metrics and record digest |
| `review-template.jsonl` | Pending rubric rows tied to exact run and case-record digests |

The repository also includes an executed `sample-summary.json`, all thirty
`sample-results.jsonl` records and `sample-review-template.jsonl`. They are
synthetic practice artifacts. No human/LLM ratings have been completed in the
published sample.

## Dataset and independent source checks

`cases.jsonl` contains 22 answerable and 8 unanswerable cases. It covers codes,
suppliers, commercial terms, date/quantity facts, paraphrases, conditions,
cross-references, multiple sources, filters, uncertain OCR, denied access and an
unmapped alias. Every case has:

- unique safe query ID and explicit `practice` split;
- principal, original question and allowlisted exact filters;
- boolean answerability and nonblank reference-answer alternatives;
- required answer atoms for answerable cases;
- expected source citations: tenant, document, version, body-location and facts.

Expected citations identify stable source units, not the answer-local S labels.
Unanswerable cases have no gold evidence/answer atoms. Their expected abstention
is relative to the fixed source/access/filter/identifier-policy snapshot.
`CW1000` has no approved alias mapping here; revising that policy requires
revisiting its label. An absent date in this catalogue is not a claim that the
date does not exist elsewhere in the business.

`source_checks.jsonl` independently declares expected parser status and source
facts at input block locations. Labels were authored for this artifact, not
derived from assistant predictions; no independent human annotation campaign or
hidden held-out test set is claimed. Incorrect facts, denied gold citations and
gold outside the case's filters fail validation rather than being scored as
model targets.

The frozen input is `labs/week_08/corpus.jsonl`. Its nine synthetic layout
records yield eight accepted documents/twelve chunks before analyst access.
P-106 remains under review. The offline source auditor sees the entire synthetic
collection, including the private distractor; analyst retrieval still sees only
its seven granted accepted documents/eleven chunks.

The source audit separately checks the parser representation and fact/location
retention in emitted chunks. Baseline: 9/9 parser statuses match, declared parsed
atom recall is 1.0 and accepted chunk-unit recall is 12/12. This is controlled
layout-fixture validation, not PDF/OCR extraction accuracy or proof of optimal
chunk boundaries.

`dataset.json` binds cases, source checks and corpus to SHA-256 digests with
dataset ID/version/schema. A copied practice slice may use a new semantic version
and updated fingerprints while retaining the supported local-corpus contract.
The loader accepts 1–64 question records up to 256 KiB, rejects malformed UTF-8,
duplicate JSON keys, nonfinite JSON constants, unknown fields and inconsistent
answerability/evidence. Source-check files are limited to 32 records/64 KiB.
This runner intentionally supports visible `practice` labels only; design a
separate reviewed held-out workflow before making generalization claims.

## Metric contracts

| Measure | Contract | Limit |
| --- | --- | --- |
| Parser status / fact preservation | Declared statuses and text atoms in parsed fixture representation | Not arbitrary extraction accuracy or commercial validation |
| Chunk-unit recall | Expected accepted facts retained at expected body location | Not full boundary/coherence quality |
| Candidate Recall@6 | Required eligible source units present in the reranking pool | No guarantee of final context or answer quality |
| Precision@3 | Relevant unique units divided by requested k=3 | A one-unit gold set caps it at 1/3 |
| Recall@3 | Gold units found divided by gold-unit count | Depends on declared granularity and complete labels |
| MRR@3 | Mean reciprocal rank of first relevant hit | Does not measure multi-unit completeness |
| Binary nDCG@3 | Discounted binary relevance relative to ideal ordering | No invented graded labels |
| Context source precision | Relevant labelled units among valid selected source units | Unlabelled useful background can lower it; invalid citations are counted separately |
| Expected-citation recall | Gold source units with valid selected citations | Not claim-level entailment |
| Context support complete | Every declared atom survives in spans of its specific gold source/version/location | A substring test, not semantic support |
| Exact match | Strip S display labels, case-fold, collapse whitespace, compare accepted reference alternatives | Longer/correct paraphrases can fail |
| Answer-atom coverage | Fraction of required substrings in actual answer | Negation or a wrong relationship can still pass |
| Exact citation validity | Authorized stored identity, unique label, integer offsets and exact stored quote | Not authority, entailment or completeness |
| Extractive traceability | Actual answer equals its validated quoted spans plus labels | Not a general free-form faithfulness score |
| Expected response behavior | Emit evidence for answerable; abstain for unanswerable cases | An evidence-bearing answer can still be inadequate |

No-gold recall/rank/nDCG remain null and are excluded from answerable means.
Unanswerable abstention is reported on its own denominator. Empty emitted
citations do not receive a manufactured perfect citation-validity fraction.
The summary distinguishes all-query exact match from answerable-only exact match.

`metrics.graded_ndcg` is a separate teaching helper with grades 0–3 and
`2**grade-1` gain. The run itself uses binary Week 5 metrics. Exact-match
normalization preserves punctuation, numbers, product-code hyphens, units and
negation; it is not claimed to match another benchmark's normalization.

`semantic_similarity`, semantic `answer_faithfulness`, semantic
`answer_correctness` and semantic citation support are null in raw automated
records. Lexical proxies never fill those fields. Actual imported semantic
ratings appear separately in the review summary.

## Observed baseline and useful failures

Means below use the 22 answerable questions and fixed source-unit labels. The
baseline and treatment share their candidate pool, eligible snapshot and k=3.

| Mean | Hybrid ordering | Teaching reranker |
| --- | ---: | ---: |
| Precision@3 | 0.378788 | 0.393939 |
| Recall@3 | 0.984848 | 1.000000 |
| MRR@3 | 0.954545 | 0.977273 |
| Binary nDCG@3 | 0.961893 | 0.983224 |

Candidate Recall@6 is 1.0. Default context support completeness, expected-citation
recall and answer-atom coverage are 1.0. Valid selected-unit context precision is
0.689394. No emitted citation is invalid; extractive traceability is 1.0 among
answered cases.

Normalized exact match is 9/30 overall and 4/22 on answerable cases. Expected
abstention is 5/8 on unanswerable cases. The three failures are deliberately
retained:

| Case | Unavailable target fact | Observed behavior |
| --- | --- | --- |
| W09Q23 | Delivery date in Atlas catalogue for CW-1000 | Returns authentic catalogue excerpts |
| W09Q24 | 5 percent discount in framework agreement | Returns authentic agreement excerpts |
| W09Q25 | Atlas Metals contact phone number | Returns authentic related excerpts |

The failure is `unanswerable_evidence_returned`, not a claim that a date,
discount or phone number was fabricated. A valid quote does not satisfy the
annotated task's expected abstention. Reference mismatch and perfect lexical
coverage are both diagnostics rather than semantic answer grades.

## Paired context ablations

```bash
.venv/bin/python -m labs.week_09.run --compression sentences \
  --output-dir .runtime/week09-sentences
.venv/bin/python -m labs.week_09.run --context-chars 300 \
  --output-dir .runtime/week09-tight
```

| Policy | Complete context support | Mean answer-atom coverage | Exact match, all 30 |
| --- | ---: | ---: | ---: |
| Whole chunks, 1,400 characters | 22/22 | 1.000000 | 9/30 |
| Sentence spans, 1,400 characters | 20/22 | 0.977273 | 7/30 |
| Whole chunks, 300 characters | 18/22 | 0.924242 | 10/30 |

Retrieval metrics remain identical across all three settings. Compression loses
two labelled contexts; the tight budget loses four. The tight setting raises
exact match while losing support, demonstrating why an answer-only score can
reward a harmful change. Unanswerable abstention stays 5/8.

Diagnostic labels distinguish candidate misses, ranking losses from a complete
pool, context losses after a complete top-k, answer-atom losses after complete
context, unexpected abstention, unavailable-fact excerpts, invalid citations and
extractive-format mismatch. Several labels may apply; they are not a universal
causal proof for all RAG architectures.

## Human/LLM review without invented scores

The pending template includes four axes: context relevance, answer faithfulness,
answer correctness and citation support. Use anchors 1 = material failure,
3 = partial/ambiguous success, 5 = fully satisfied under the task rubric, with
2/4 as intermediate ratings. Faithfulness is judged against actual context;
correctness additionally uses references/task policy; citation support checks
claim alignment as well as validity. Appropriate abstention can satisfy an axis
without inventing a source claim. If an axis cannot be assessed, keep the review
pending rather than guessing a score.

Inspect the actual record and relevant source material, then fill a copy with
`status: reviewed`, actual reviewer kind (`human` or `llm`), identity, all four
integer ratings 1–5 and a nonblank evidence-based rationale. Keep run ID,
record digest and rubric version unchanged. Human reviews leave prompt version
null; LLM reviews must name a judge prompt version as well as model/revision in
the reviewer identity. Candidate/source instructions remain data during judging.

```bash
.venv/bin/python -m labs.week_09.run \
  --reviews .runtime/week09-default/review-template.jsonl \
  --output-dir .runtime/week09-review-import
```

The untouched template yields zero completed reviews and makes no model call.
For real ratings, supply the completed copy. Stale run/record/rubric identities,
unknown fields, missing axes, bool/out-of-range scores, empty rationales and
duplicate ratings from the same reviewer/prompt/case fail. Human/model/prompt
groups are reported separately. Self-declared identity and a digest are not
authentication or proof of an independent review.

Calibrate a proposed LLM judge on an independently reviewed subset with numeric
errors, negation, missing support, acceptable paraphrases, irrelevant citations
and abstentions. Test answer-order and verbosity effects, retain model/prompt
versions and review disagreements. None of those judge/human evaluations has
been executed for the published sample; all thirty reviews remain pending.

## Reproducibility and remaining scope

Run IDs bind dataset/corpus fingerprints, configuration, named teaching model
identities, Python runtime, normalization and a digest of the Week 5–9 source
bundle. Each stored case then hashes its observed output/metrics. Reviewer
imports must match the exact case record. No timestamps or live model calls
introduce nondeterminism into the default practice run.

No new package, paid service, production endpoint, trace system or earlier-week
behavior was added. This is a small visible diagnostic set. Held-out real-model
quality, semantic similarity, claim entailment, semantic answer/citation
correctness, general PDF/OCR quality, latency and memory remain unmeasured.
Production evaluation records need appropriate access and retention controls;
the committed examples contain only controlled synthetic content.

Primary conceptual references:
[IR evaluation](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-in-information-retrieval-1.html),
[BERTScore](https://arxiv.org/abs/1904.09675),
[Ragas](https://arxiv.org/abs/2309.15217),
[ARES](https://arxiv.org/abs/2311.09476),
[LLM-as-judge study](https://arxiv.org/abs/2306.05685).
