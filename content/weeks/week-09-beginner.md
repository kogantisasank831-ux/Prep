---
layout: week
week: 9
phase: 3
status: approved
version: 1.0.0
last_reviewed: 2026-10-22
estimated_hours: 8
permalink: /weeks/week-09/beginner/
title: "RAG evaluation: a beginner's introduction"
description: Learn what to test at each step of a RAG assistant, calculate useful metrics, and run a 30-question evaluation without mistaking a citation for a correct answer.
summary: Use the missing delivery date for CW-1000 to separate search quality, context quality, answer quality and citation support, then inspect saved results from the procurement assistant.
kicker_primary: RAG evaluation fundamentals
kicker_secondary: Beginner context
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-09/
---

## Start with an answer that looks reassuring

You ask: “What is the delivery date for CW-1000?” The assistant returns an Atlas Metals catalogue excerpt. It shows the correct product code, quantity and unit price, plus a genuine citation. You open the source and every quoted word is there.

There is still no delivery date. The catalogue never provided one.

This is the difference between finding related evidence and answering a question. Week 8 built an assistant that returns cited source excerpts. Week 9 teaches you to test what it actually accomplishes and to locate what failed when the output falls short.

You will examine seven parts of a RAG system: parsing, chunking, retrieval, context relevance, answer faithfulness, answer correctness and citation correctness. You will calculate precision, recall and rank metrics, compare exact matching with semantic judgment, and run thirty labelled procurement questions while saving the actual results.

Bring the ideas from earlier weeks: documents become traceable chunks; hybrid retrieval finds candidates; reranking and context selection choose evidence. Basic Python functions, dictionaries, lists and imports are enough for the examples. The default lab needs no paid service, GPU or downloaded evaluator model.

Allow about eight hours: one for the failure story, two for metrics, one for labels, two for running and inspecting results, one for review and one for exercises. Use the [production lesson]({{ '/weeks/week-09/' | relative_url }}) when you want the fuller contracts and experiment design.

## Ask a smaller question at each step

Instead of asking only “Was the answer good?”, ask what each stage promised to preserve.

| Stage | Everyday question | Example failure |
| --- | --- | --- |
| Parsing | Did we read the source accurately? | A price loses its decimal point |
| Chunking | Did useful pieces and their source locations survive? | A payment exception is separated from its rule |
| Retrieval | Did search find the evidence we need? | The controlling clause never enters the shortlist |
| Context relevance | Did the final evidence focus on this question? | Useful text is replaced by unrelated background |
| Answer faithfulness | Are claims supported by the supplied evidence? | The answer says inspection is optional when the source requires it |
| Answer correctness | Does the response adequately answer the question? | Genuine catalogue text is returned for an unavailable date |
| Citation correctness | Does the cited source resolve and support the claim? | A real document is attached to an unsupported conclusion |

These stages can fail independently. Search can find exactly the text it was given, while the parser supplied the wrong number. An answer can quote a source accurately and still omit a necessary condition. A model can even answer correctly from outside knowledge while the retrieved context supplies no support.

That last case explains why the final score alone can hide trouble. A correct answer does not prove retrieval worked; an incorrect answer does not tell you which earlier step went wrong. Save the intermediate observations so you can follow the evidence path.

**Pause:** If the source was misread as USD 1200 instead of USD 12.00, would a valid citation fix the answer? No. It could faithfully point to the corrupted representation.

## Check the source before grading search

The new lab has a small source-check file separate from the assistant's predictions. It states which fixture documents should be accepted or held for review, which facts should survive and where those facts belong.

P-106 contains an OCR-like `USD 12.O0`, with the letter O. The right behavior for this controlled example is to retain the uncertain value under review, not silently turn it into a confidently searchable price. The other accepted sources retain their established text and locations.

The audit compares facts in the parser's representation with the declared input facts. It separately checks that the accepted body units survive in retrieval chunks. If the invoice clause is lost during chunking, the expected clause remains in the test labels and the check fails. We do not create the gold answer from whatever the assistant happened to return.

The current source audit matches all nine expected statuses and retains all twelve accepted body units. One accepted document is a synthetic private distractor inspected by the offline auditor; the analyst's query runs still cannot access it. These results concern controlled layout records, not arbitrary PDF or OCR accuracy.

**Pause:** Why keep expected facts separate from output? Otherwise a dropped condition could disappear from both the system and its test, making the omission look successful.

## Choose what you count as one relevant result

Suppose the question asks about the Schedule A payment condition. P-105 contains the supplier, the line-item quantity, the payment terms and the sentence connecting those terms to Schedule A.

If you count documents, any P-105 passage may count as finding the document. If you count the required evidence units, you need the row, the actual payment clause and the cross-reference. Finding the supplier paragraph alone does not satisfy that requirement.

The lab counts expected body units with full tenant, document, version and location identity. It checks labels against the input source facts and the request's permissions and filters. A private document cannot become an analyst's gold reference just because its words match the query.

For a question needing three units, imagine the first three results are:

1. A general supplier summary.
2. The payment clause.
3. The line item.

Two returned units are relevant. The required cross-reference is missing. This gives us two related measures:

```text
Precision@3 = relevant returned units / requested slots = 2/3
Recall@3    = relevant returned units / required units  = 2/3
```

They happen to be equal in this example, but they need not be. If the question needs five units and we return two of them in three slots, precision is 2/3 and recall is 2/5. If only one unit is required and it returns alone for a three-slot request, this lab's precision is 1/3 and recall is 1.

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

The requested-slot denominator is a declared policy. A different tool may divide by the number actually returned. Compare definitions before comparing score tables.

**Pause:** Can document recall be perfect while the answer's needed clause is missing? Yes. The document may be present without its decisive passage.

## Check whether the shortlist made a complete answer possible

The Week 8 pipeline reranks up to six candidates and then selects evidence from up to three source chunks. Before judging the final order, inspect whether the six-candidate pool contains all required units.

If all three required units are in the pool, candidate recall is 1.0. If the top three contain only two, the problem occurs in ordering or later context selection. If the pool never contained the payment clause, reranking cannot recover it. That is the candidate ceiling from last week.

This distinction saves wasted experiments. A larger reranker cannot repair a missing source, a filtered-out document or a clause lost during ingestion. Keep candidate keys and final keys so you can tell which situation occurred.

## MRR asks how soon you find something useful

For one question, find the first relevant result's position. If it is first, reciprocal rank is 1. If it is second, the score is 1/2. If it is third, the score is 1/3. If there is no relevant hit within the cutoff, the score is zero. Average those values across the included questions to get mean reciprocal rank, MRR.

In our supplier-summary/payment-clause/line-item example, the first useful hit is second, so reciprocal rank is 0.5. Move the payment clause to first and it becomes 1.0.

That is helpful, but it does not tell you whether the cross-reference also arrived. MRR rewards the first relevant hit, not complete support for every part of a question.

**Pause:** Can MRR rise while a required quantity is still absent? Yes. You can improve the first hit without fixing the missing evidence.

## nDCG asks whether useful items occupy favorable positions

Discounted cumulative gain gives useful results more credit when they appear earlier. Normalized DCG compares that value with an ideal ordering under the same relevance labels.

You can use binary labels, where a result is relevant or not, or explicit graded labels. For a tiny teaching example, give the controlling clause grade 3 and general supporting context grade 1. Under the chosen `2^grade - 1` gain rule, the controlling clause contributes more and belongs earlier.

```python
from labs.week_09.metrics import graded_ndcg

grades = {"controlling-clause": 3, "general-context": 1}
assert graded_ndcg(["controlling-clause", "general-context"], grades, k=2) == 1.0
score = graded_ndcg(["general-context", "controlling-clause"], grades, k=2)
assert score is not None and 0 < score < 1
print(score)
```

Those grades are an explicit toy example. The actual practice dataset uses binary relevance, so its reported nDCG is binary. Do not add impressive-looking grades when nobody has established what those levels mean.

For an unanswerable question, there is no nonempty gold evidence set. The lab leaves recall and rank-based relevance scores null and evaluates expected abstention separately. Null means the measure is undefined or unmeasured under the contract; it does not mean perfect, zero or missing work that can be filled arbitrarily.

## Inspect the context after search has finished

The reranker may select all the right units, but compression or a tight budget can remove part of them. Search scores alone will not detect that later loss.

The lab asks whether required source units reached the selected spans and whether their declared text atoms survived there. It checks the specific expected source/version/location. The same phrase in another supplier's document cannot satisfy the reference.

It also measures how much selected source material belongs to the labelled relevant set. Required evidence can be complete while extra material remains. That is why high recall and modest precision can coexist.

Keep the limitation in view: these are declared source/fact checks. A substring match does not understand a relationship. “Net 30 does not apply” contains `Net 30`, so a simple atom check can pass despite the negative meaning. Semantic support still needs a different review.

**Pause:** If retrieval metrics stay unchanged after compression, have you proved the change is harmless? No. Inspect the evidence that survived compression and packing.

## Exact match is clear only after you define its rules

An exact-match check compares an answer with accepted reference text. It is useful for strict outputs, but a correct paraphrase or a longer source quote may fail.

This lab removes display citation labels such as `[S1]`, ignores case and collapses whitespace. It keeps punctuation, digits, units, product-code hyphens and negation. That means Net 15 does not become equivalent to Net 30, and CW1000 does not silently become CW-1000.

```python
from labs.week_09.metrics import atom_coverage, exact_match

assert exact_match("Net 30 after approval [S1]", ("net 30 after approval",))
assert not exact_match("Net 15 after approval", ("Net 30 after approval",))
assert not exact_match("CW1000", ("CW-1000",))
assert atom_coverage("Net 30 does not apply", ("Net 30",)) == 1.0
print("The last check detects words, not correct meaning.")
```

The last line is a deliberate warning about the metric, not a successful correctness test. The runner calls it lexical answer-atom coverage. It does not rename it semantic correctness.

For the default thirty cases, exact match succeeds on 9/30. Among the 22 answerable cases it succeeds on only 4/22, even though all declared required answer atoms appear. Many responses contain full excerpts and extra context rather than only the concise reference. You need to inspect those mismatches before calling them wrong answers.

**Pause:** Is 30% exact match the same as 30% semantic accuracy? No. The normalization, references, output format and task determine what that figure can mean.

## Similarity can help with paraphrases and still miss the decisive difference

Semantic similarity compares meaning-related representations rather than only identical text. For example, an embedding metric might consider “payment follows approval” close to “approval is required before payment.” [BERTScore](https://arxiv.org/abs/1904.09675) is one research example using contextual token representations for generated-text comparison.

But similar sentences can disagree on the important detail. “The terms are Net 15” and “The terms are Net 30” have the same topic and most of the same words. A useful semantic metric still needs calibration on wrong numbers, codes, dates and negation.

If you add one, record its model/revision and input policy, then compare its judgments with independently reviewed examples. A score from one model is not a universal correctness probability. The default lab computes no semantic similarity: that field stays null. No model download is hidden behind a label called “semantic.”

## Separate faithful, correct and well-cited

These three questions are easier to see with examples:

- **Faithful:** Does the answer stay within what the supplied evidence supports? A verbatim catalogue quote has strong traceability, though selecting it can still omit a condition.
- **Correct:** Does the response adequately answer this question? A catalogue quote without a delivery date fails the expected availability behavior for a date request.
- **Well-cited:** Do the cited sources resolve and support the attached claims? A genuine source attached to an unsupported inference is insufficient.

The deterministic citation validator checks authorized stored identity, version, location lineage and exact quoted offsets. That establishes where the quote came from. A human or calibrated judge still needs to assess whether the quote supports the claim and whether the response is complete.

The assistant's current output is cited excerpts. The evaluator therefore measures **extractive traceability**, including whether the answer equals those labelled quotes. It leaves general semantic faithfulness, answer correctness and citation support unreviewed. Reporting all of them as 100% because the quote matches would overstate the evidence.

**Pause:** Can a citation be valid while the response is inadequate? Yes. That is the central missing-date example.

## Let a person or model review a defined question

Human evaluation is useful for relationships, completeness and task judgment that a string check misses. Give the reviewer the actual question, response, evidence, references and task policy. Ask for a short rationale pointing to decisive text, not just “good” or “bad.”

The lab uses four review axes: context relevance, answer faithfulness, answer correctness and citation support. Each completed review uses a 1–5 score with explicit anchors in the production lesson and lab README. A 1 indicates a material failure; a 3 indicates partial or uncertain success; a 5 indicates that the axis is fully satisfied under the rubric. If you cannot assess it, keep the review pending.

An LLM can apply a rubric too, but then you need to evaluate that judge. It may reward length or a favored answer position, miss a numeric error or prefer its own style. The [LLM-as-judge study](https://arxiv.org/abs/2306.05685) examines such biases in its tested settings. Test your chosen judge against independent human reviews rather than assuming another model cannot make the same mistake.

For faithfulness, a judge should assess claims against the actual provided context. For correctness, supply references and the source/policy scope too. Do not ask it to prove that a fact is absent from the whole business just because search did not return it. Candidate answers and documents are data; instructions inside them should not control the judge.

Record the model/revision, prompt version, settings, rubric and evidence-based rationale. Validate all scores as untrusted output. Keep human and model reviewer results separate. A submitted file can claim a reviewer identity; that metadata does not authenticate who performed the review.

The default command does not call a judge. It creates pending review rows. The published sample has **zero completed human or LLM reviews**, so semantic review fields are null. This is a useful distinction between preparing an evaluation process and having executed it.

## Inspect the thirty-question dataset

The dataset has 22 answerable and 8 unanswerable questions. It covers exact codes, supplier names, commercial terms, a date, quantities, paraphrases, conditions, cross-references, multiple sources, filters, uncertain OCR, denied access and an unmapped alias.

Each case stores the question, principal, filters, answerability, accepted reference answers, required answer atoms and expected citations. Expected citations identify source/version/body locations, not answer-local labels such as S1. The labels are authored visible synthetic practice, not an independently annotated hidden test set.

Unanswerability is relative to the exact available evidence and policy. The Atlas catalogue has no delivery date. The uncertain invoice remains under review. A stranger has no source grants. CW1000 has no approved alias mapping in this fixture. These are distinct reasons for expected abstention, not proof that all similarly worded questions are impossible in every system.

Before running, the lab checks that expected facts exist in the declared input block and that gold sources fit the case's access and filters. Dataset/source digests prevent changed labels from silently using an old version. Keep this set for learning and regression diagnosis; create a separately reviewed held-out set before claiming general model quality.

**Pause:** Why include negative cases? A system that always returns related text might look excellent if every test question is guaranteed answerable.

## Run and save the evaluation

From the repository root:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m labs.week_09.run --output-dir .runtime/week09-default
.venv/bin/python -m pytest tests/test_week09_evaluation.py -q
```

On Windows use `.venv\Scripts\python.exe`. Use a fresh output directory each time; the writer refuses to overwrite a previous result.

You receive three files:

- `summary.json`: configuration, source audit, metric means, category results and review status.
- `results.jsonl`: one observed record per question, including the actual answer, cited text/offsets, expected evidence and stage metrics.
- `review-template.jsonl`: pending rubric rows tied to the exact run and case records.

The [Week 9 lab](https://github.com/kogantisasank831-ux/Prep/tree/main/labs/week_09) also includes the executed sample summary and all thirty saved results. Digests connect dataset, source snapshot, implementation, runtime and settings. They help reproduce a run; they are not signatures or guarantees of truth.

```python
from labs.week_09.run import run_evaluation

summary, records = run_evaluation()
assert summary["query_count"] == 30
assert summary["answerable_count"] == 22
failed = [record["query_id"] for record in records if record["metrics"]["failures"]]
assert failed == ["W09Q23", "W09Q24", "W09Q25"]
print(summary["failure_counts"])
```

Those three cases ask for a delivery date, a 5 percent discount and a phone number absent from the relevant source snapshot. The assistant returns authentic related excerpts instead of the expected abstention. We preserve those failures rather than altering the labels or claiming that valid citations mean the response is sufficient.

## Read several numbers together

On the answerable cases, candidate Recall@6 is 1.0. Hybrid top-three recall is 0.984848; reranked top-three recall is 1.0. MRR@3 changes from 0.954545 to 0.977273. All required labelled support survives in the default final contexts.

At the same time, only 5 of 8 unanswerable cases abstain as expected, and exact match is 9/30. No emitted citation is invalid, but no semantic review has been completed. These are complementary observations, not contradictory scores that need to be forced into one average.

Try changing only the final context policy:

```bash
.venv/bin/python -m labs.week_09.run --compression sentences \
  --output-dir .runtime/week09-sentences
.venv/bin/python -m labs.week_09.run --context-chars 300 \
  --output-dir .runtime/week09-tight
```

| Policy | Answerable cases with complete declared support | Exact match across all 30 |
| --- | ---: | ---: |
| Whole chunks, 1,400 characters | 22/22 | 9/30 |
| Sentence spans, 1,400 characters | 20/22 | 7/30 |
| Whole chunks, 300 characters | 18/22 | 10/30 |

The tight budget improves exact match while losing required support more often. Shorter excerpts can resemble a concise reference more closely. That does not make missing evidence harmless.

Retrieval metrics stay the same across these runs. The losses happen after retrieval, which is why the evaluator calls them `context_loss`. Expected abstention remains 5/8. A single output score would hide both the location and the nature of the regression.

**Pause:** If you saw only 10/30 exact match, would you know whether the tight budget was better? No. You need the support result and the actual changed cases.

## Turn a pending template into a real review carefully

Inspect a saved case before assigning scores. Copy its template row and retain the run ID, case-record digest and rubric version. Fill actual reviewer identity, all four axes and an evidence-based rationale only after review. Human reviews leave the judge prompt null; LLM reviews name the model/revision and prompt version.

```bash
.venv/bin/python -m labs.week_09.run \
  --reviews .runtime/week09-default/review-template.jsonl \
  --output-dir .runtime/week09-review-import
```

The untouched template imports as zero completed reviews. It does not start a model call. A completed copy can be imported instead, but it must match the exact configuration and answer that was reviewed. A rating for the compressed run cannot quietly grade the whole-chunk run.

For a serious evaluation, let reviewers independently assess a shared subset, compare disagreements and improve ambiguous references. Keep judge/human groups separate. Do not claim independent review if the only completed rating is your own.

## Answer these without looking back

1. **Why not evaluate only the final answer?** It can hide retrieval failure or combine several causes into the same mismatch.
2. **What is the difference between precision and recall?** Precision asks about useful returned slots; recall asks how much required evidence was found.
3. **What does MRR miss?** Required evidence beyond the first useful hit.
4. **Why preserve numbers and hyphens during normalization?** Their differences may be the answer rather than cosmetic variation.
5. **Can a semantic score certify a payment amount?** No. It needs calibration and domain checks for decisive errors.
6. **What does a valid citation prove?** Where an authorized exact quote came from, before checking whether it supports the claim.
7. **Why are some fields null?** No appropriate semantic evaluation has been executed; a proxy must not fill the gap silently.
8. **What did the thirty-case run reveal?** Good labelled evidence coverage can coexist with unavailable-fact response failures and context-budget regressions.

In an interview, tell the missing-date story, show which stage passed and which behavior failed, then name the next experiment. This demonstrates diagnosis more clearly than listing metric names.

## Exercises

1. **Calculate one ranking by hand.** Use three returned items and three gold units, with the first relevant hit second. Check precision, recall and reciprocal rank with the helper. Explain which extra source is still needed.
2. **Find a dangerous normalization.** Compare Net 15/Net 30, CW1000/CW-1000 and a sentence with/without negation. Show why your policy must preserve each difference.
3. **Inspect an unavailable-fact case.** Read its full eligible source and returned excerpts. Explain why no target fact is available and why an authentic quote is insufficient. Do not confuse this with fabrication of a new number.
4. **Compare two saved contexts.** Join the default and tight-budget run by question ID. Find a lost required unit and point to its source/version/location. Explain why unchanged retrieval recall missed the problem.
5. **Perform a real review.** Score one answerable case and one unavailable-fact case using the rubric. Record your actual identity and rationale, retain pending status elsewhere, and import the completed copy. Do not fill an axis you cannot assess.
6. **Plan a held-out check.** Propose unseen questions with numbers, conditions, aliases, versions and unavailable answers. Group related paraphrases/source versions when planning the split. Keep the proposal separate from any claim that it has been run.

## Readiness checklist

- I can name the seven evaluation layers and one failure each can hide.
- I can distinguish finding a document from finding every required clause.
- I can calculate precision, recall and reciprocal rank with explicit denominators.
- I can explain binary versus graded nDCG without inventing labels.
- I can compare admitted context with the original ranked evidence.
- I can explain why exact match, lexical coverage and semantic correctness differ.
- I can distinguish source validity from claim support and answer adequacy.
- I can run thirty cases and retain observed outputs and pending review status.
- I can describe the three unavailable-fact failures and the tight-budget regression honestly.

Keep the dataset, run records, one paired comparison and a small failure backlog in your weekly project handoff. Week 10 adds production tracing; this week gives you a repeatable way to evaluate frozen questions before you interpret those live traces.

## Further reading

- [NIST trec_eval reciprocal-rank definition](https://github.com/usnistgov/trec_eval/blob/main/m_recip_rank.c): first-relevant-hit semantics; the lab uses its own cutoff policy.
- [Scikit-learn nDCG documentation](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html): normalized discounted gain; gain and tie conventions must be stated per implementation.

- [Stanford IR evaluation chapter](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-in-information-retrieval-1.html): retrieval measures and relevance judgments.
- [BERTScore](https://arxiv.org/abs/1904.09675): contextual text comparison.
- [Ragas](https://arxiv.org/abs/2309.15217) and [ARES](https://arxiv.org/abs/2311.09476): research approaches to separating RAG evaluation dimensions.
- [Judging LLM-as-a-Judge](https://arxiv.org/abs/2306.05685): why model judges need calibration and bias checks.
