---
layout: week
week: 9
phase: 3
status: approved
version: 1.0.0
last_reviewed: 2026-10-22
estimated_hours: 8
permalink: /weeks/week-09/
title: "RAG evaluation: find the stage that lost the answer"
description: Build a 30-question procurement evaluation, separate retrieval from answer quality, and retain reproducible results with explicit human and model-review gaps.
summary: Follow a missing delivery date through source audits, ranked evidence, context selection, cited excerpts and a review rubric that keeps automated proxies separate from semantic judgment.
kicker_primary: RAG evaluation fundamentals
kicker_secondary: Evidence before a headline score
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-09/beginner/
---

## A valid citation can still leave the question unanswered

Ask the Week 8 assistant: “What is the delivery date for CW-1000?” Restrict it to the Atlas Metals catalogue. It finds the right code, the right supplier and a genuine source quote. Every citation resolves correctly. The problem is that this catalogue contains no delivery date.

The assistant does not invent a date. It returns relevant-looking excerpts when this evaluation expects it to abstain. If we checked only whether a source existed, we would call the run successful. If we checked only a final reference string, we would see a failure without knowing whether retrieval, context construction or the response policy caused it.

This week makes that distinction operational. You will evaluate parsing, chunking, retrieval, context relevance, answer faithfulness, answer correctness and citation correctness separately. You will calculate ranking metrics, choose an exact-match policy, examine semantic similarity and design human/LLM review. The build adds thirty labelled procurement questions with reference answers and expected source citations, runs the existing assistant and stores the observed results.

The default system remains the Week 8 local assistant with teaching scorers and cited source excerpts. It has no free-form generator. Automated checks report what they can establish; semantic correctness and claim entailment remain unreviewed until someone actually evaluates them. A null review field is part of an honest result.

Bring Week 5's ranking metrics, Week 6's parsed-source lineage, Week 7's eligible retrieval snapshot and Week 8's context/citation contracts. Start with the [beginner version]({{ '/weeks/week-09/beginner/' | relative_url }}) for a slower route through the same failures.

| Time | Work | What to retain |
| --- | --- | --- |
| Hour 1 | Explain the missing-date failure across stages | A failure hypothesis with observable evidence |
| Hours 2–3 | Work through precision, recall, MRR, nDCG and exact match | Hand calculations and a normalization policy |
| Hour 4 | Inspect the question labels and source oracle | A checked source/version/location for each expected fact |
| Hours 5–6 | Run and inspect the 30-case evaluation | Raw results, summary and exact configuration identity |
| Hour 7 | Compare context ablations and prepare review | A paired diagnostic and an unfilled or actually completed rubric |
| Hour 8 | Complete interview answers and exercises | A decision note explaining what improved and what remains unknown |

## Draw a boundary around each evaluation claim

“RAG quality” is too broad to debug directly. Start with a question at each boundary. If that boundary fails, inspect it before guessing about later stages.

| Layer | Orienting question | A useful check | A failure the check can miss |
| --- | --- | --- | --- |
| Parsing | Did the source become a faithful usable representation? | Expected text, numbers, layout and acceptance status | A well-formed but incorrect OCR digit |
| Chunking | Did answer-bearing units survive with usable boundaries and lineage? | Required facts at expected source locations | Evidence split across chunks in an unhelpful way |
| Retrieval | Did eligible evidence reach the pool and top k? | Precision, recall, rank and source coverage | A generator ignoring perfectly retrieved text |
| Context relevance | Is the admitted context useful for this question? | Relevant-unit precision and required-support retention | A topic match that does not answer the question |
| Answer faithfulness | Are the answer's claims supported by supplied evidence? | Claim-to-evidence review | Whether the evidence itself is authoritative or the answer is complete |
| Answer correctness | Does the response adequately answer the question under the task rules? | Reference comparison and calibrated domain review | A reference set missing an acceptable answer |
| Citation correctness | Does each citation resolve and support its attached claim? | Identity/offset validity plus claim-level support review | A genuine source attached to the wrong inference |

These checks overlap without being interchangeable. Parsing can preserve `12.O0` exactly while leaving a commercially uncertain value that belongs in review. Retrieval can find the right document while missing its controlling clause. A faithful quotation can fail to answer the question. A correct-looking answer can come from memory and be unsupported by the provided sources.

When you say a check passed, name the contract. “All selected spans resolve to authorized stored text” is precise. “Citations are correct” is broader because it can imply that each quote supports the claim. The lab records exact validity and leaves semantic support unreviewed.

**Checkpoint:** Can an answer be faithful but incomplete? Yes. Quoting the catalogue accurately does not supply its absent delivery date. Can an answer be correct but unfaithful to the supplied context? Yes. A model can happen to know the correct date from elsewhere; that does not establish grounded support for this request.

## Audit sources before scoring search results

Suppose an invoice's unit price changes from `12.00` to `1200` during extraction. The retriever may find that text, the reranker may rank it first and the answer may quote it perfectly. A high retrieval or citation score cannot repair the earlier corruption.

The new lab includes an independent source-check file. It declares expected parser status and small sets of source facts at specific body locations. These labels are authored from the controlled input records rather than produced from the assistant's answers. The audit examines the parser representation and then the emitted retrieval chunks separately.

Nine synthetic records have nine expected statuses. Eight are accepted and one, P-106, remains `needs_review`. Its OCR-like `USD 12.O0` value is preserved as uncertain text, not silently converted to `USD 12.00`. Twelve accepted body units, including the private distractor available to the offline corpus auditor, are checked for fact preservation and location lineage.

The source auditor is a local fixture evaluator with access to the synthetic input collection. The analyst's question runs still use independent source-version grants and cannot retrieve that private source. Do not confuse privileged offline auditing with a user's permitted retrieval scope.

Current parser-status matches are 9/9, declared parsed-atom recall is 1.0 and accepted chunk-unit recall is 12/12. These numbers describe controlled parsed-layout records. They are **not PDF extraction accuracy, OCR character accuracy or general table understanding**. Those require representative source files and separately annotated references.

The chunk check is also deliberately narrow: did the declared fact survive in a chunk carrying the expected source location? That does not prove the chunk size is optimal or that neighboring exceptions are retained. Add boundary/completeness labels when testing a different chunk policy. Evaluate at a stable evidence unit rather than relabelling the gold set to match whatever a new policy happens to emit.

**Checkpoint:** Why not derive expected facts from the returned chunks? If the chunker drops a payment condition, deriving the labels from its output can erase that condition from the test too. The system would then grade its own omission as success.

## Decide what a relevant item means before counting it

Week 8's Schedule A question needs a row, an invoice clause and a cross-reference from P-105. At document level, retrieving any P-105 passage can yield document Recall@1 of 1. At the evidence-unit level, returning only its supplier summary misses all three required units.

Neither granularity is inherently wrong. They answer different questions. Declare which unit your labels and predictions use and keep it constant across comparisons. This lab uses fully scoped source units: tenant, document, version and body-location label. It does not collapse every clause into one document hit.

The labelled gold set is relative to the request's principal and exact metadata filters. Evidence in another tenant, a denied source or a filtered-out supplier is not eligible gold for that request. Uncertain P-106 text is not accepted evidence. The loader validates those boundaries before running the test, so a mislabeled private citation fails the dataset instead of becoming a retrieval target.

Let `G` be the relevant eligible evidence units, `R_k` the first k returned unique units and `h` their intersection count:

```text
Precision@k = h / k
Recall@k    = h / |G|
```

Precision uses the requested number of slots. Returning one relevant unit for a request of three gives Precision@3 of 1/3 under this contract, even if no other results are returned. Some systems choose a returned-count denominator instead; that is a different metric and must be named accordingly.

```python
from labs.week_05.metrics import evaluate_ranking

metrics = evaluate_ranking(
    ["supplier-summary", "payment-clause", "line-item"],
    frozenset({"payment-clause", "line-item", "cross-reference"}),
    k=3,
)
assert metrics.precision_at_k == 2 / 3
assert metrics.recall_at_k == 2 / 3
assert metrics.reciprocal_rank_at_k == 0.5
print(metrics)
```

Now separate **candidate recall** from final top-k recall. If a six-item pool contains all three required units, candidate Recall@6 is 1.0. If only two survive into the first three, Recall@3 is 2/3. The first stage has made a complete answer possible; the ranking or later selection still needs attention. If the pool itself contains only two, reordering alone cannot get beyond that ceiling.

**Checkpoint:** Does low Precision@3 always mean retrieval is broken? No. A question may have one labelled sufficient unit, giving an upper limit of 1/3 under a three-slot denominator. Inspect the labels, requested k and surplus context rather than treating the number as a universal pass mark.

## MRR rewards the first useful hit; nDCG inspects the order

For one question, reciprocal rank is `1/r`, where r is the first relevant rank inside the evaluated cutoff. It is zero when there is no relevant hit in that cutoff. Mean reciprocal rank, MRR, averages that value across the included questions.

If a payment clause is first, reciprocal rank is 1. If a supplier summary comes first and the clause is second, it is 1/2. MRR is a useful first-hit measure. It does not reward a system for also returning the quantity and cross-reference needed to complete a multi-part answer.

Discounted cumulative gain lets several relevant positions contribute. This lesson's graded teaching function uses:

```text
gain(relevance) = 2^relevance - 1
DCG@k          = sum(gain(relevance_at_rank_r) / log2(r + 1))
nDCG@k         = DCG@k / ideal_DCG@k
```

The ideal ordering uses the same labelled source universe, sorted by relevance grade. When no positive grade exists, this implementation returns null. A different gain function is possible, so record the chosen contract. Do not invent graded relevance values when your data supplies only binary labels.

```python
from labs.week_09.metrics import graded_ndcg

grades = {"controlling-clause": 3, "general-context": 1}
ideal = graded_ndcg(["controlling-clause", "general-context"], grades, k=2)
reversed_order = graded_ndcg(["general-context", "controlling-clause"], grades, k=2)
assert ideal == 1.0
assert reversed_order is not None and 0 < reversed_order < ideal
print(reversed_order)
```

Those two grades are an explicit toy example. The actual thirty-question run uses the existing binary Week 5 ranking metrics. All labelled required units have binary relevance. Its reported nDCG is therefore **binary nDCG**, not a graded domain-utility score.

No-gold/unanswerable cases need another treatment. Recall and rank-based relevance metrics remain null and stay outside answerable-query means. Evaluate the expected abstention behavior separately. Silently assigning no-gold cases a perfect recall inflates the headline; silently treating every returned passage as a known false positive confuses incomplete labels with a deliberate unanswerability annotation.

## Evaluate the context that actually reached the answer builder

Retrieval metrics end before the character budget, compression and citation packaging have finished their work. Inspect the admitted spans too.

The lab measures relevant-source precision over the valid selected source units and expected-source recall over the labelled units. It then checks whether every declared atom survives in the selected spans of its specific expected source/version/location. It does not let the same phrase from an unrelated document satisfy the label.

This support-completeness check can catch a lost `Net 30` condition after sentence selection. It cannot establish semantic entailment. The presence of `Net 30` in “Net 30 does not apply” is not support for a positive payment claim. A substring check is an observable proxy with known failure cases, not a substitute for reading the relation.

Context source precision is also stricter than broad topical relevance: a real passage may provide useful background without being one of the authored required units. If your labels are not exhaustive, interpret low precision with that limitation. Keep the required-evidence set, acceptable background and prohibited evidence separate in a larger dataset.

The default run's relevant selected-unit precision averages 0.689394 while required-support completeness is 1.0 on the 22 answerable cases. Both can be true: the needed evidence is present, along with some unlabelled surplus material. Increasing k can preserve recall while wasting context, so inspect both.

**Checkpoint:** Why compare whole-chunk and compressed context on the same run? It isolates a downstream selection change. If retrieval membership changes too, you can no longer attribute every difference to compression.

## Exact match needs a task-specific normalization policy

Reference answers make a claim about acceptable outputs. A concise reference such as “Net 30 after inspection approval” can express the right fact while the assistant returns a whole paragraph, its heading and two other cited excerpts. Strict exact match will reject that longer answer. It is a formatting/content-identity test, not automatically a semantic verdict.

This lab removes display citation labels of the form `[S1]`, case-folds text and collapses whitespace. It preserves punctuation, product-code hyphens, numbers, negation and units. Multiple explicit reference alternatives are allowed. The policy is versioned in the report; it is not claimed to reproduce a benchmark's unrelated normalization rules.

```python
from labs.week_09.metrics import atom_coverage, exact_match

assert exact_match("Net 30 after approval [S1]", ("net 30 after approval",))
assert not exact_match("Net 15 after approval", ("Net 30 after approval",))
assert not exact_match("CW1000", ("CW-1000",))
assert atom_coverage("Net 30 does not apply", ("Net 30",)) == 1.0
print("Lexical coverage can pass while the meaning is wrong.")
```

That final assertion is a counterexample to overclaiming. The lab reports answer-atom coverage because it helps locate lost facts, but semantic answer correctness stays unreviewed. An exact-match mismatch may mean a wrong value, an acceptable paraphrase or simply extra source text. Inspect the case before assigning a cause.

For extraction tasks with a strict schema, exact match can be especially useful when applied to normalized typed fields: currency, amount, unit, date and identifier. Define normalization in the domain contract. Do not erase the difference between `CW-1000` and `CW1000`, `1,000 kg` and `1.000 kg`, or Net 15 and Net 30 just to raise the score.

## Semantic similarity is a signal, not a truth detector

Two answers can use different words for the same relationship. A semantic similarity metric can help identify acceptable paraphrases that exact match rejects. An embedding cosine compares representations; methods such as [BERTScore](https://arxiv.org/abs/1904.09675) compare contextual token representations instead of requiring exact token equality.

Similarity does not supply a task's correctness rules. “The invoice is Net 15” and “The invoice is Net 30” share most words and the same topic while disagreeing on the decisive number. Negation, effective dates and supplier identity can cause the same problem. Calibrate any threshold against independently labelled examples of those errors.

Record the metric model/revision, preprocessing, pooling or token-alignment policy, reference selection and aggregation. A score from one embedding model is not necessarily comparable with another. Validate shape, finite numbers and input truncation when integrating a model, just as you did for retrieval and reranking.

The default lab does not load an embedding evaluator or calculate a semantic score. It leaves `semantic_similarity` null. Adding a model would be a separate measured extension; lexical atom coverage is never relabelled as semantic similarity.

**Checkpoint:** Would a high semantic score justify ignoring a wrong product code? No. Use identifier/number/condition checks and a calibrated correctness review alongside any similarity metric.

## Faithfulness, correctness and citations need different review questions

Take a response containing three accurate source quotes. It may be perfectly traceable and still omit the answer. Take a fluent sentence claiming “inspection is optional” with a citation to a clause requiring inspection. Its source exists, but the relationship is wrong.

For faithfulness, break the answer into checkable claims and ask whether each follows from the context that was actually supplied. Include numbers, conditions, cross-source joins and implied relationships. Do not let a reviewer silently use external knowledge to repair unsupported claims.

For correctness, ask whether the response answers the user's question under the reference/policy/source snapshot. Consider completeness, unavailable facts, source authority and acceptable alternatives. A source may be faithful to an outdated version; a short answer may omit a controlling exception. These are different causes even if both lead to a poor response.

For citations, start with deterministic validity: stored source/version, authorized identity, exact offsets and quoted text. Then review whether the cited span supports its attached claim. Citation precision and recall should state their unit: claims with adequate citations, cited sources in a reference set or expected evidence units present. A document-ID match does not establish claim-level support.

The Week 8 answer policy returns source quotes with labels. Week 9 therefore measures **extractive traceability**: does the actual answer equal its quoted spans with the expected label formatting, and do those spans validate? It does not report this as a general generated-answer faithfulness score. All emitted default citations validate; broader semantic faithfulness, correctness and citation support remain null until review.

**Checkpoint:** Is “all quotes are authentic” enough to mark the missing-date answer correct? No. Authenticity and task adequacy are separate. The response policy should recognize that the requested date is unavailable in this snapshot.

## Build a judge around a rubric, not around a compliment

An LLM judge can help process more cases than a person can read immediately. It remains another model whose mistakes need evaluation. [Ragas](https://arxiv.org/abs/2309.15217) separates dimensions of RAG assessment, while [ARES](https://arxiv.org/abs/2311.09476) studies automated component judges with human-annotated calibration. They are useful research references, not libraries required by this lab or promises that a judge score is ground truth.

Give a judge one explicit task at a time. For faithfulness, provide the question, actual admitted evidence and answer; ask for claim-level supported/unsupported decisions with evidence locations. For correctness, provide reference answers and the relevant task/source policy as well. Do not require it to infer that a fact is absent from the entire source universe merely because that fact is absent from the retrieved snippets.

A proposed judge output might contain the rubric version, model/revision, prompt version, per-axis score and a short evidence-based rationale. Validate the response as untrusted data. Reject missing axes, out-of-range scores, booleans masquerading as integers and references to foreign evidence. Treat instructions embedded in candidate answers or source documents as data, not as authority over the evaluation.

Before adopting the judge, calibrate it on an independently reviewed subset. Include wrong numbers, negation, plausible unsupported statements, correct paraphrases, irrelevant citations, partial support and appropriate abstention. Inspect disagreement patterns. Compare different answer orders in pairwise judging and avoid revealing which system you prefer.

The [MT-Bench judge study](https://arxiv.org/abs/2306.05685) examines position, verbosity and self-enhancement biases in its evaluated settings. Those findings motivate tests; they do not establish a universal error rate for your current judge. Record model and prompt changes, sampling settings and repeated-run stability. A more verbose answer should not receive a better factuality score simply for sounding thorough.

The provided runner **does not call an LLM judge**. It produces pending templates and can validate/import ratings supplied later. No paid endpoint, new model dependency or automatic grading claim is hidden behind the default command.

## Make human review reproducible enough to disagree productively

“Looks good” gives the next reviewer little to work with. Define score anchors and request a rationale pointing to the decisive evidence. Review the same cases independently before discussing disagreements; use adjudication to improve either the answer or the labels.

The lab's review file has four axes, each scored from 1 to 5 only after review:

| Axis | Score 1 anchor | Score 3 anchor | Score 5 anchor |
| --- | --- | --- | --- |
| Context relevance | Selected material cannot support the task or needed empty-context policy | Some useful evidence, important distraction or gap | Focused sufficient evidence, or appropriate absence for an unanswerable case |
| Answer faithfulness | Material claims contradict or exceed provided evidence | Mixture of supported and unsupported/ambiguous claims | All substantive claims are supported; qualifications remain intact |
| Answer correctness | Wrong, misleading or violates expected availability behavior | Partly correct but incomplete or imprecise | Adequately answers the task, including an appropriate abstention where required |
| Citation support | Missing/invalid references or evidence contradicts the claim | Some claims supported, others weakly aligned | All claims needing evidence have adequate cited support; an abstention makes no unsupported source claim |

Scores 2 and 4 represent intermediate cases. If the reviewer cannot assess an axis, leave the review pending and explain what additional material is needed outside the completed-rating file. Do not substitute a guessed score to satisfy the schema. In a larger system, extend the schema with an explicit adjudication/not-applicable policy rather than overloading a number.

The current completed-review contract requires all four axes, reviewer kind/identity, rationale and the exact rubric version. LLM reviews additionally require a judge prompt version. Human and model reviewers are summarized separately; model prompt versions are not blended. These identities are self-declared metadata, not authenticated signatures or proof that an independent review occurred.

Each review binds to a run ID and an exact case-record digest. A rating for a prior answer or different context configuration is rejected. This prevents accidental stale-score reuse; it does not prevent someone from fabricating a new file. Preserve raw results and the actual review process as well as hashes.

No human or model scores have been filled for the published sample. All thirty semantic reviews are pending. That is the state of the evidence, not a zero-quality verdict and not a pass.

## Author the thirty cases before inspecting their predictions

The dataset extends the visible procurement practice collection. It contains 22 answerable and 8 unanswerable cases, including codes, suppliers, payment terms, a date, quantities, paraphrases, conditions, cross-references, multiple sources, filters, uncertain OCR and denied access.

The answerable labels include concise reference answers, explicit accepted alternatives where useful, required answer atoms and expected evidence with full tenant/document/version/location identity. The expected citations refer to source units, not to answer-local labels such as `S1`; the system may assign those labels in another order.

```json
{
  "query_id": "EXAMPLE_01",
  "category": "numeric",
  "split": "practice",
  "principal_id": "analyst",
  "question": "What is the quoted unit price for CW-1000?",
  "filters": {"document_type": "catalogue"},
  "answerable": true,
  "reference_answers": ["The quoted unit price for CW-1000 is USD 12.00."],
  "answer_atoms": ["CW-1000", "USD 12.00"],
  "evidence": [
    {
      "tenant_id": "northwind-procurement",
      "document_id": "P-107",
      "version": "1",
      "location": "p1:block-1",
      "atoms": ["CW-1000", "Quoted unit price USD 12.00"]
    }
  ]
}
```

An unanswerable case has no gold evidence or answer atoms and expects an abstention. That label is relative to the defined source and access snapshot. It does not assert that no delivery date exists anywhere in the business. `CW1000` is a deliberate unmapped-alias case under the current identifier policy; adding an approved alias mapping would require revisiting that expectation.

The source oracle checks whether labelled atoms exist in the declared raw input block, rather than accepting invented references. Gold citations must also be expected-accepted, authorized and within the case's metadata filters. Wrong annotations fail before the evaluation can present them as a model regression.

All cases are explicitly **visible synthetic practice**. The labels were authored for this learning artifact; no independent human annotation campaign or hidden test set is claimed. Several cases reuse earlier practice patterns. Use this set for debugging, then freeze a separately reviewed held-out set for model selection. Keep paraphrases of the same question, related source versions and shared supplier facts together when deciding splits so near-duplicates do not create misleading independence.

**Checkpoint:** Why should the test set contain questions with no available answer? Otherwise a system that always returns a plausible passage can look strong without ever demonstrating that it knows when evidence is insufficient.

## Run the assistant and retain the evidence

From the repository root, reuse the pinned development environment:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m labs.week_09.run --output-dir .runtime/week09-default
.venv/bin/python -m pytest tests/test_week09_evaluation.py -q
```

On Windows use `.venv\Scripts\python.exe`. The default command needs no model download, GPU or external evaluator. Use a fresh output directory for each run; the writer refuses to overwrite earlier evidence.

The output directory contains `summary.json`, `results.jsonl` and `review-template.jsonl`. Each result stores the question/scope, references, expected source units, actual status and answer, cited text and offsets, candidate/reranked/context keys, stage metrics, failure labels and request provenance. The context digest/character count identifies the exact assembled context; the recorded spans and source locations allow its evidence to be reconstructed.

```python
from labs.week_09.run import run_evaluation

summary, records = run_evaluation()
assert summary["query_count"] == 30
assert summary["answerable_count"] == 22
failures = [record["query_id"] for record in records
            if record["metrics"]["failures"]]
assert failures == ["W09Q23", "W09Q24", "W09Q25"]
print(summary["failure_counts"])
```

Dataset metadata binds question labels, source checks and the frozen Week 8 corpus to their digests. The run identity also binds configuration, teaching model identities, Python runtime, normalization and a hash of the Week 5–9 implementation bundle. Changing any of those inputs creates another run identity. Editing labels requires an intentional manifest/version update; it cannot silently reuse the old dataset fingerprint.

The result record then has its own digest, so a review cannot accidentally attach to another answer from the same question ID. These hashes support reproducibility under trusted inputs; they do not establish source authenticity, protect secrets or authenticate reviewers.

The checked-in `sample-summary.json` and `sample-results.jsonl` retain an executed default run. The `sample-review-template.jsonl` contains pending rows. They are synthetic examples suitable for this repository; real evaluation outputs can contain sensitive questions and document excerpts and need the project's actual retention/access policy.

## Read the default results before choosing a change

First inspect the 22 answerable cases. The baseline and reranked results share their candidate pool and k=3. Candidate Recall@6 is 1.0, so every required unit is somewhere in the pool.

| Answerable-query mean | Hybrid ordering | Teaching reranker |
| --- | ---: | ---: |
| Precision@3 | 0.378788 | 0.393939 |
| Recall@3 | 0.984848 | 1.000000 |
| MRR@3 | 0.954545 | 0.977273 |
| Binary nDCG@3 | 0.961893 | 0.983224 |

The final default contexts preserve all declared required support on these 22 cases. Expected-citation recall and lexical answer-atom coverage also average 1.0. No emitted citation fails the exact stored-span validation. These are narrow fixture results from teaching scorers, not learned-model accuracy or semantic certification.

Now inspect the other denominators:

| Check | Observed default result | Interpretation |
| --- | ---: | --- |
| Normalized exact match, all questions | 9/30 = 0.300000 | Reference-string agreement including abstention references |
| Normalized exact match, answerable only | 4/22 = 0.181818 | Whole excerpts often differ from concise references |
| Expected abstention, unanswerable only | 5/8 = 0.625000 | Three unavailable-fact requests still receive excerpts |
| Exact citation invalidity | 0 emitted invalid spans | Traceability passes; semantic support has not been reviewed |
| Human/LLM semantic reviews completed | 0/30 | No inferred faithfulness/correctness rating |

W09Q23 asks for the catalogue's absent delivery date. W09Q24 asks whether Schedule A has a 5 percent discount. W09Q25 asks for the supplier's phone number. The source snapshot supplies none of those requested facts, yet the assistant returns real related excerpts. The failure label is `unanswerable_evidence_returned`.

This is an evaluation of response behavior. It does not claim the assistant invented a date, discount or phone number. Its excerpt policy has returned material where the annotated task expects a clear abstention. A future answerability gate needs its own evidence-based design and evaluation; choosing a relevance threshold from three examples is not enough.

The low exact-match rate tells another story. Extra authentic source text and alternative wording create mismatches, so it cannot be read as “70% of answers are semantically wrong.” Conversely, full atom coverage cannot be read as “100% correct.” Use both as diagnostics while semantic review remains pending.

## Change one context policy and keep the upstream work fixed

Run two paired ablations:

```bash
.venv/bin/python -m labs.week_09.run --compression sentences \
  --output-dir .runtime/week09-sentences
.venv/bin/python -m labs.week_09.run --context-chars 300 \
  --output-dir .runtime/week09-tight
```

| Policy | Complete labelled context support | Mean answer-atom coverage | Exact match, all 30 |
| --- | ---: | ---: | ---: |
| Whole chunks, 1,400 characters | 22/22 = 1.000000 | 1.000000 | 9/30 = 0.300000 |
| Sentence spans, 1,400 characters | 20/22 = 0.909091 | 0.977273 | 7/30 = 0.233333 |
| Whole chunks, 300 characters | 18/22 = 0.818182 | 0.924242 | 10/30 = 0.333333 |

All three have the same retrieval metrics. The new failures occur after ranking: two `context_loss` cases under sentence selection and four under the tight budget. Unanswerable abstention remains 5/8.

The tight budget improves exact match while losing required evidence on more answerable questions. A shorter returned excerpt can accidentally match a concise reference more often. This is exactly why a single output score is a poor release decision. You need to know what was removed and whether it mattered.

The runner localizes a missing pool unit as `candidate_miss`, loss from a complete pool before context as `ranking_loss`, and loss after a complete top-k as `context_loss`. It can also flag missing answer atoms, invalid citations, unexpected abstention and extractive-format mismatch. These are practical diagnostic labels under this pipeline, not a proof that only one stage caused a real-world failure.

**Checkpoint:** Which table would tell you that a token-saving change damaged evidence? The context-support comparison, not unchanged retrieval recall. Which table would stop you from celebrating the higher exact match? The same paired evidence-loss result.

## Use the review template when a review has actually happened

Copy the pending template, inspect each saved case with its evidence and references, then fill only completed reviews. Keep the exact run ID, record digest and rubric version. Add the actual reviewer identity, ratings and rationale. A human review leaves the judge prompt null; a model review records its exact model/revision identity and prompt version.

```bash
.venv/bin/python -m labs.week_09.run \
  --reviews .runtime/week09-default/review-template.jsonl \
  --output-dir .runtime/week09-review-import
```

Importing the untouched pending template produces zero completed reviews. It does not execute a judge. To import actual ratings, point the command to the completed copy instead. The run configuration must match the reviewed output; using a compressed-context review with the default configuration fails the identity check.

The importer validates score ranges, required axes, rationale, reviewer kind, prompt identity and duplicate completed ratings. It reports each human/model/prompt group separately. It does not turn a self-declared review file into authenticated evidence of expert agreement.

For a larger evaluation, sample difficult cases deliberately, use multiple independent reviewers for a shared subset, report agreement and disagreement categories, and adjudicate ambiguous references. Keep the process independent of the model change you want to promote. A judge can accelerate triage; humans remain responsible for the rubric and its limits.

## Explain the system in an interview

**Why does evaluating only the final answer hide retrieval failures?** Different pipeline failures can produce the same final mismatch. A missing source, a lost clause during context packing and an unsupported generator inference all need different fixes. A model may also answer correctly from memory despite retrieval failure. I keep source, candidate, rank, context and answer observations so I can identify where required evidence disappeared.

**How would you choose RAG metrics?** I start from task decisions and evidence granularity. Candidate recall establishes a ceiling; top-k recall/MRR/nDCG inspect selection and order; context checks inspect the admitted evidence. Exact match is useful under an explicit normalization/schema contract. I use semantic similarity and calibrated human/LLM review for broader answer judgments, with identifiers, quantities, negation, citations and unanswerability covered separately.

**Would you use LLM-as-judge?** Yes, for a defined rubric after calibration on an independent human-reviewed subset. I preserve actual question/context/answer, model/prompt versions, validated score schemas and rationales, and test order/verbosity/number-error biases. I distinguish judge agreement with people from factual correctness and keep unreviewed fields null instead of filling them with lexical proxies.

**What did this week's evaluation find?** The teaching assistant retained every labelled required unit for 22 answerable cases, but returned excerpts on three questions with unavailable target facts. A 300-character budget raised exact match while reducing support completeness. Those findings motivate answerability and context-selection work; they do not justify claiming real-model generalization or semantic quality without further review.

## Active recall

1. **Why audit parsing separately?** A later faithful quote can repeat an earlier extraction error.
2. **Why fix evidence granularity?** Document-level recall can hide a missing clause or table row.
3. **What is the candidate ceiling?** Only relevant units present in the reranker's pool can be promoted.
4. **What does MRR omit?** Completeness after the first relevant hit.
5. **When does nDCG need grades?** When the chosen metric intends to reward different relevance levels; binary data should stay binary.
6. **Why are no-gold recall values null?** There is no nonempty relevant-set denominator; abstention is measured separately.
7. **Can exact match improve while evidence quality worsens?** Yes; the tight-budget ablation demonstrates it.
8. **Can lexical atoms certify semantic correctness?** No; negation can preserve every substring while reversing a claim.
9. **What does a valid citation establish?** Resolvable authorized stored identity and exact text, before semantic support review.
10. **Why bind reviews to records?** The same question ID can produce a different answer/context in another run.

## Exercises with acceptance criteria

1. **Trace one missing unit.** Use a copy of a recorded result or a new experiment to remove one required candidate. Show the candidate recall, top-k recall and failure label. Keep the label independent of the changed output; do not delete it to make the score pass.
2. **Expose a normalization mistake.** Construct code, amount, date and negation pairs. Propose one safe normalization and one that changes their meaning. Submit assertions showing why the unsafe policy would overstate exact match.
3. **Review the three unavailable facts.** Read the full eligible source snapshot for W09Q23–25. Explain why the required fact is unavailable under each filter. Distinguish an irrelevant excerpt from an invented factual claim, then propose an answerability experiment without tuning a threshold on these three cases alone.
4. **Compare the context ablations.** Save both runs, join by question ID, and list the source units lost. Explain one case in which exact match rises while required evidence disappears. Your explanation must use observed spans, not only summary means.
5. **Complete two genuine human reviews.** Choose one answerable and one unavailable-fact case. Apply all four axes with evidence-based rationales. Import the completed copy, leaving other rows pending. If no independent reviewer is available, label your own review as such; do not claim independent agreement.
6. **Design judge calibration.** Specify a frozen human-reviewed subset, difficult error categories, judge identity/prompt, score schema, order tests and acceptance criteria. State that the protocol is proposed until actual reviews and judge calls exist.
7. **Version a new practice slice.** Copy the dataset, add independently sourced question/reference/citation labels and update its version/fingerprints. Keep source/access scope explicit. Plan a separate held-out split with shared-source variants grouped, rather than treating this visible exercise as evidence of generalization.

Your handoff should contain the versioned thirty-question dataset, source oracle, executed default results, one paired context comparison, unreviewed/reviewed status and a short failure backlog. Every claimed improvement should name its denominator, frozen inputs and unresolved semantic questions.

## Primary references

- [NIST trec_eval reciprocal-rank definition](https://github.com/usnistgov/trec_eval/blob/main/m_recip_rank.c): first-relevant-hit semantics; the lab uses its own cutoff policy.
- [Scikit-learn nDCG documentation](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html): normalized discounted gain; gain and tie conventions must be stated per implementation.

- [Stanford Introduction to Information Retrieval, evaluation chapter](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-in-information-retrieval-1.html): retrieval evaluation and relevance judgments.
- [BERTScore](https://arxiv.org/abs/1904.09675): contextual representation matching for text-generation evaluation; a similarity signal rather than a domain correctness rule.
- [Ragas](https://arxiv.org/abs/2309.15217): separating dimensions of RAG evaluation.
- [ARES](https://arxiv.org/abs/2311.09476): automated component judges and human-annotated calibration.
- [Judging LLM-as-a-Judge](https://arxiv.org/abs/2306.05685): judge behavior and biases in the study's settings.
- [Week 9 lab and stored results](https://github.com/kogantisasank831-ux/Prep/tree/main/labs/week_09): the exact contracts and executed practice artifacts used here.

Week 10 adds observability and tracing. Keep the distinction clear: this week's reproducible evaluation records help compare frozen cases; production traces will help investigate live requests under operational and data-handling constraints.
