---
layout: week
week: 8
phase: 2
status: approved
version: 1.0.0
last_reviewed: 2026-10-22
estimated_hours: 8
permalink: /weeks/week-08/beginner/
title: "Reranking and context construction: a beginner's introduction"
description: Learn how to choose useful passages from search results, preserve their conditions, and build a local assistant that shows exact cited evidence.
summary: Follow one procurement question from a shortlist to a cited answer, with gentle examples of pair scoring, rewrites, deduplication, compression and context limits.
kicker_primary: Reranking and context construction
kicker_secondary: Beginner context
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-08/
---

## Start with the sentence the answer needs

You have found the right agreement. It mentions Atlas Metals, copper wire and Schedule A. Someone asks what payment condition applies to the 1,000 kg line. You read the first three search results, but none states the actual payment terms. The useful sentence is lower down:

```text
Invoice terms are Net 30 after inspection approval.
```

The search was close. It found the right neighborhood without putting the needed evidence on your desk. This week teaches you how to inspect that shortlist more carefully and how to keep the answer's supporting details together.

By the end, you will explain why retrieval and reranking do different jobs, try a reviewed query variant, spot a harmful duplicate rule, fit source evidence into a declared context budget and run **Procurement Knowledge Assistant v1**. This local assistant ingests controlled document records, uses hybrid retrieval, reranks, returns cited source excerpts and records basic request events.

Bring the Week 5 idea of ranking, Week 6's traceable chunks and Week 7's combination of keyword and dense retrieval. You need basic Python functions, lists, dictionaries and imports to follow the lab. You do not need a paid API or a downloaded model for the default examples.

Use about eight hours: one for the story, two for scoring and measurement, one for query variants, one for evidence selection, two for the lab and one for exercises. Pause at the checkpoints and explain your answer aloud before moving on.

## Retrieval makes a shortlist; reranking checks that shortlist

Imagine asking a colleague to collect six potentially useful passages. A second colleague reads those six alongside the question and puts the strongest answers first. The first job is retrieval. The second is reranking.

The second colleague cannot choose a paragraph the first colleague never brought back. This is the most useful debugging rule of the week. If the payment condition is missing from the entire shortlist, investigate ingestion, chunk boundaries, permissions, filters or retrieval. If it is present but too low, reranking might help.

The lab makes the limits explicit:

| Step | Default limit | Plain meaning |
| --- | ---: | --- |
| Each first-stage search path | 8 candidates | How far the keyword and dense lists can reach |
| Fused shortlist | 6 candidates | How many passages the reranker inspects |
| Final evidence selection | 3 source chunks | How many chunks can supply the answer context |
| Serialized context | 1,400 characters | How much JSON, source information and quoted text fits |

Suppose a question needs three different chunks. If only two reach the six-item shortlist, a reranker cannot get all three into the final context. Its maximum recall for those three chunks is 2/3. If all three reach the shortlist, the next question is whether the scoring and selection stages keep them.

**Pause:** You increase the final evidence limit from three to four, but the missing clause was never in the shortlist. Will that reliably fix the problem? No. You have increased space for the candidates you already have.

## Two ways to compare a question and a passage

A **bi-encoder** makes a representation of the question and another representation of the passage. A similarity function compares them. A passage representation can be prepared before a question arrives, so this is useful for searching a large collection.

A **cross-encoder** reads the question and passage together and produces a pair score. It has a chance to inspect relationships between their words. For example, it can learn that “after inspection approval” is a condition attached to payment. Because the score depends on the question–passage pair, it needs new work for every candidate pair.

Neither name means “always better.” A model can misunderstand an identifier, a number or a condition. A cross-encoder can also lose useful text if its joint input is too long and gets truncated. You choose a shortlist size and measure the actual model rather than trusting the architecture's name.

The [Sentence Transformers guide](https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html) explains retrieval followed by cross-encoder scoring. In this repository, the default pair scorer is intentionally much simpler: it counts matching terms and adds a few commercial-phrase bonuses. You can inspect it without installing model weights.

```python
from labs.week_08.pipeline import TeachingPairScorer

question = "Net 30 after inspection approval"
scores = TeachingPairScorer().score_pairs((
    (question, "Invoice terms are Net 30 after inspection approval."),
    (question, "The receiving team records an inspection."),
))
assert scores[0] > scores[1]
print(scores)
```

This shows the input/output contract: two pairs enter and two scores leave in the same order. The first passage gets the stronger teaching score. It does not prove the passage is true or demonstrate a trained cross-encoder's quality. We reject missing scores, NaN, infinity and changed model identity before accepting a reranking result.

**Pause:** Does a high relevance score mean “this supplier's terms are correct”? No. Relevance, source authority and commercial correctness are different questions.

## Keep the comparison fair

If you want to know whether reranking helped, give the baseline and reranker the same six candidates. Compare the first three before and after reordering. Keep the question, source versions, permissions, filters and relevance labels fixed too.

For the Schedule A question, the three necessary source units are:

1. The row that identifies copper wire and the 1,000 kg quantity.
2. The clause that says Net 30 after inspection approval.
3. The sentence linking that payment condition to Schedule A.

The baseline top three include a general supplier paragraph instead of the payment clause. The teaching reranker brings the clause up and keeps the other two needed pieces. It has improved this example by changing the order of existing candidates.

You can ask different measurement questions:

- **Candidate recall:** Did the shortlist include the needed evidence at all?
- **Precision@3:** How many of the three requested result slots contain labelled useful evidence?
- **Recall@3:** How much of the labelled useful evidence reached those three slots?
- **MRR@3:** How early did the first useful result appear, averaged over questions?
- **nDCG@3:** Is useful evidence placed favorably under the stated relevance labels?
- **Context support:** Did the required fixture details survive the final selection?

One good first result can improve MRR while the answer still lacks a second required clause. That is why the lab also checks the declared support atoms in their specific source chunks. This is a substring check on a small fixture, not a general understanding of whether one statement entails another.

The practice set contains fourteen questions. Ten have evidence labels; four deliberately probe unsupported aliases, an OCR variant, an abbreviation and a denied identifier. Recall and rank metrics stay undefined for a no-gold question. We report these probes separately rather than inventing missing labels.

**Pause:** Is a reranker that sees twenty candidates fairly compared with a baseline that saw only six? It is a useful system comparison if declared, but you have changed candidate discovery as well as ordering.

## Rewrite the wording while protecting the request

Users and documents may describe the same idea differently. “Receiving-team sign-off” might benefit from a reviewed search variant containing “inspection approval.” That is a reason to try another query, not permission to change what the user asked.

Consider `CW-1000 Net 30 after approval`. A rewrite to “supplier payment details” drops a product identifier, a duration and a condition. It may find plausible paragraphs for the wrong task. The lab therefore preserves the original query and accepts at most two reviewed variants.

Its lexical guard requires original tokens containing digits to survive. It also preserves a short list of negations and relationship words such as `not`, `except`, `unless`, `after` and `before`.

```python
from labs.week_08.pipeline import PipelineError, query_plan

original = "CW-1000 Net 30 after approval"
variants = query_plan(original, ("CW-1000 payment terms Net 30 after approval",))
assert variants[0] == original
assert len(variants) == 2
try:
    query_plan(original, ("CW-1000 payment details",))
except PipelineError:
    print("The rewrite lost a protected constraint.")
else:
    raise AssertionError("constraint loss should fail")
```

The guard is useful but limited. “Approval after Net 30” contains the same protected words while changing their relationship. A person still needs to review meaning. The current CLI does not call an LLM to generate rewrites.

Permissions and supplier/type filters remain separate fields. A rewrite cannot make the analyst eligible to read another tenant's document. If you add model-generated rewrites later, keep those access decisions in deterministic code.

**Pause:** Why keep the original query? A rewrite can help with alternative wording while accidentally weakening an exact clue. Retaining the original keeps both paths available for inspection.

## Use multiple queries without pretending the extra work is free

Multi-query retrieval runs the original and reviewed variants against the same eligible collection. Each gets a ranked list. The lab combines those lists using RRF, the rank-based fusion method from Week 7, and keeps a bounded final shortlist. It then reranks those candidates against the original question.

If a passage ranks first in two query lists, equal-weight RRF with constant 60 gives it `1/61 + 1/61`. A passage appearing only second in one list gets `1/62`. This combines rank support without requiring the raw scores to have comparable scales.

There are trade-offs. Two variants can find complementary clauses. They can also repeat the same interpretation, drift toward a different task or displace a useful original candidate from the final cap. Exact repeated queries are removed, but similar wording is not automatically independent evidence.

The default benchmark uses only the original query. Try reviewed variants as a separate experiment and record their extra retrieval work. More calls may affect latency and cost in a real service; this small local exercise does not measure either.

## A repeated document is not always duplicate evidence

It is tempting to keep one passage per document. That would break the Schedule A example: all three needed evidence units belong to P-105. They are different clauses doing different jobs.

The lab uses a conservative rule. It removes a later occurrence only when tenant, document, version, source digest and text all match an earlier occurrence exactly. It retains the first, highest-ranked copy and records the dropped ID.

| What you see | Default action | Why |
| --- | --- | --- |
| Exactly repeated text from the same source/version | Keep the first | Repeating those bytes uses space without adding evidence |
| A table row and a payment clause from the same document | Keep both | They supply different required details |
| The same wording in another version | Keep both | Version authority needs its own decision |
| Similar wording with a different quantity | Keep both | A small textual change can be commercially important |

This rule misses some true duplicates. That is preferable to silently treating two different prices as the same fact. A broader semantic duplicate policy needs tests for numbers, codes, versions, source authority and lost support.

**Pause:** Should “Net 30” and “Net 15” be collapsed because the sentences look similar? No. Their difference may be the answer.

## Compression can remove the condition without inventing a word

Context compression tries to retain needed evidence in less space. The simplest version chooses original sentences rather than writing a new summary. That makes exact quotes possible, but it can still be misleading.

Read this separate example:

```text
Payment is due. Except disputed invoices require approval.
```

If you keep only “Payment is due,” the quote is authentic. The missing exception changes what a reader might conclude. Source accuracy for the surviving words is not the same as complete evidence.

The optional `sentences` mode ranks sentence spans by query-term overlap and keeps at most two per chunk in their original order. It saves exact source offsets. Table rows stay whole so a unit price does not lose its product and quantity. Its punctuation-based splitting is deliberately simple, and it can lose headings, exceptions or related sentences.

Default mode keeps whole chunks. Compare compression against that baseline and test whether the required conditions survive. If you later ask a model to summarize instead, the new summary needs additional checks for changed numbers, invented wording, merged sources and unsupported conclusions. It must not be displayed as a verbatim quote.

**Pause:** Can every citation be valid while a compressed answer is incomplete? Yes. The missing exception has no surviving citation to invalidate.

## Count the full context and leave the evidence intact

The final context includes more than quoted paragraphs. It contains citation labels, source/version IDs, locations, JSON keys, punctuation and escaping. The lab counts the full serialized string.

It tries chunks in reranked order. For each chunk, it checks permission again, selects its spans, builds the proposed JSON and admits the entire selected unit only if it fits. If the chunk is too large, it can try a later smaller chunk. It never cuts a source halfway through a sentence to force it into the budget.

Three source chunks is an upper limit, not a promise. A tight character budget can admit fewer. If search has no eligible candidates, the result is `no_evidence`. If candidates exist but no selected source fits, the result is `context_budget_exhausted`. These failures need different fixes.

The lab enforces **characters**, not model tokens. A real generator needs its own tokenizer and exact message template. Reserve space for instructions, the user question, conversation, source wrappers and output before admitting evidence. Product codes and JSON can tokenize differently from ordinary prose, so a rough characters-per-token estimate is not an enforcement rule.

The reranker has a separate joint token limit for question plus passage and special tokens. The optional local adapter checks that joint input without truncation and rejects an oversized pair. This keeps a long passage from silently losing the condition near its end.

## Being present is different from being used

You can place the correct clause in a long prompt and still receive an answer that overlooks it. The 2023 paper [Lost in the Middle](https://arxiv.org/abs/2307.03172) studied evidence position in question answering and key-value retrieval. Performance in its tested settings often depended on where relevant information appeared.

Treat this as a failure mode to test on your chosen generator, not a rule that every current model behaves identically. To investigate, keep the same question, evidence, wording and total length, then move the decisive clause to the beginning, middle and end. Compare correctness, conditions and citation support under fixed settings.

Changing the number of evidence chunks at the same time would mix selection and position effects. Adding lots of filler also changes length. Name those changes in your experiment. This lab has no generative model and makes no claim to have measured a lost-in-the-middle effect.

**Pause:** Does “the required text is in context” prove the generated answer will use it correctly? No. Evidence selection and answer evaluation are separate steps.

## Know what a citation actually proves

A source name by itself is weak evidence. The lab's citation resolves to an authorized stored chunk with a particular document version, source digest, page/block/row location and exact character span. The displayed quote must equal that stored slice. Unknown sources, changed versions, invalid offsets and repeated citation labels fail.

There are three levels to keep separate:

1. **Citation validity:** The quote is a real authorized stored span.
2. **Claim support:** The span supports the claim, including relevant conditions.
3. **Answer correctness:** The response adequately answers this question under the task's authority and business rules.

The deterministic validator handles the first level. The fixture's required-atom check gives a limited signal for the second. Neither is a complete commercial answer evaluator.

To keep the first milestone inspectable, its answer builder returns selected source quotes with labels such as `[S1]`. It does not generate a fluent synthesis or recommend a supplier. `evidence_available` means at least one span survived; it does not certify completeness. When you inspect an answer, ask which source establishes each fact and which source establishes the relationship between facts.

Locations refer to controlled parsed-layout records, not arbitrary PDF byte positions or OCR coordinates. Chunk offsets are relative to the stored text, which may include a repeated heading. That distinction matters when you later build a viewer that opens the original source.

## Run your first complete assistant

From the repository root, use the existing environment or create one with the pinned development dependencies:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m labs.week_08.demo --document-type framework_agreement
.venv/bin/python -m labs.week_08.compare --summary
.venv/bin/python -m pytest tests/test_week08_assistant.py -q
```

On Windows, replace `.venv/bin/python` with `.venv\Scripts\python.exe`. No optional model installation is needed for the default teaching run.

The corpus contains nine synthetic document records. Eight are accepted and one OCR-like invoice remains under review. The accepted collection has twelve chunks, including a private distractor in another tenant. The analyst can read seven accepted documents and eleven chunks. The independent source-version grants, not supplier labels or query wording, determine that access.

The loader accepts bounded JSONL layout records and keeps source identity stable. Repeating the exact same record is harmless; conflicting content under the same tenant/document/version fails. Review/rejected parser outcomes are recorded without being indexed. This is an in-memory fixture loader, not a new PDF parser or a persistent document service.

Here is the full public call for the Schedule A example:

```python
from pathlib import Path

from labs.week_07.retrieval import MetadataFilter, RetrievalRequest
from labs.week_08.data import demo_access, load_corpus
from labs.week_08.pipeline import KnowledgeAssistant

corpus = load_corpus(Path("labs/week_08/corpus.jsonl"))
assistant = KnowledgeAssistant(corpus.chunks, demo_access())
result = assistant.ask(RetrievalRequest(
    "analyst",
    "What payment condition controls Schedule A for the 1,000 kg copper-wire line?",
    3,
    (MetadataFilter("document_type", "framework_agreement"),),
))
assert result.answer_mode == "cited_extractive"
assert len(result.citations) == 3
assert "Net 30 after inspection approval" in result.answer
print(result.answer)
```

Inspect the three citations, not just the answer string. You should find the invoicing clause, the sentence linking it to Schedule A and the row with the quantity. The final context for this filtered request occupies 707 serialized characters.

The CLI writes answer JSON to standard output and a completed-request event to standard error. The event contains a request ID, counts, status and manifest fingerprint. It excludes raw question/document text. The fingerprint records the configuration and source/model identities needed to investigate a change; it is not a guarantee that an answer is true.

## Read the practice result honestly

The default teaching reranker improves mean Recall@3 from 0.966667 to 1.0 and MRR@3 from 0.90 to 0.95 on the ten labelled examples. Mean Precision@3 changes from 0.40 to 0.433333. All required labelled chunks were already present somewhere in the pools of at most six candidates.

Those are small, visible synthetic examples and handwritten rules. The results demonstrate the pipeline, not the general quality of a learned reranker. The four no-gold probes happen to return no candidates under these narrow scorers; this is not a general confidence threshold.

Try two context experiments:

```bash
.venv/bin/python -m labs.week_08.compare --compression sentences --summary
.venv/bin/python -m labs.week_08.compare --context-chars 300 --summary
```

Whole chunks at 1,400 characters preserve all declared support on the labelled examples. Sentence compression preserves complete support for nine of ten. A 300-character whole-chunk budget preserves complete support for seven of ten. Valid source spans can remain while the final evidence becomes incomplete.

The optional [local reranker adapter](https://github.com/kogantisasank831-ux/Prep/tree/main/labs/week_08) accepts a reviewed materialized scalar pair model with an explicit joint token limit. Its integration boundary is tested with a fake backend. No real model weights, generated-answer quality, latency, memory or positional experiment underlie the default numbers. Use the [production lesson]({{ '/weeks/week-08/' | relative_url }}) for the adapter contract and a broader experiment design.

## Questions to answer out loud

1. **Can reranking recover a missing candidate?** No. It can only reorder the pool it receives.
2. **Why score the original question against each passage?** Query variants help retrieval, while the original question remains the target of the final relevance decision.
3. **Why not keep one chunk per document?** Several clauses can jointly establish the answer.
4. **Can exact quotes still mislead?** Yes. Selecting one sentence can omit a nearby exception.
5. **Why count source headers in the budget?** They are part of the actual serialized input, just like text and punctuation.
6. **What does this assistant's answer contain?** Validated cited source excerpts; it does not produce a free-form synthesis.

For an interview, explain the missing-clause example first. Then name the design decision, show the paired measurement and say what the experiment cannot prove. That is more useful than reciting the names of several retrieval libraries.

## Exercises

1. **Find the ceiling.** Reduce the candidate pool while keeping the configuration valid. Find a labelled query that loses required evidence. Save candidate keys and top-three keys, then explain why reranking cannot repair it.
2. **Review two rewrites.** Write a helpful variant and one that changes a number or condition. Run the guard. Then write a misleading variant that keeps all protected tokens, showing why human semantic review remains necessary.
3. **Keep complementary clauses.** List the three P-105 chunks Q09 needs and explain each role. Add a separately identified exact duplicate and check which item is removed. Keep the original fixture identities unchanged.
4. **Lose an exception deliberately.** Create a new synthetic document with an exception in its second sentence. Compare whole and one-sentence context, retaining exact citation offsets. Show the lost condition in the support result.
5. **Try a tight budget and a denied query.** Inspect `context_budget_exhausted` with a very small valid budget, then search for `SECRET-900`. Explain how an admission failure differs from no eligible evidence.
6. **Describe a real model test.** Specify a reviewed compatible model, fixed candidate pools, held-out questions, quality metrics and latency measurements. Clearly label the design as proposed until executed.

Each exercise should leave a small result someone else can inspect: the request, source/configuration identity, returned keys, observed failure and your explanation. Avoid changing several parameters and then guessing which one caused the result.

## Readiness checklist

- I can explain candidate recall before discussing reranker scores.
- I can distinguish separate embeddings from joint pair scoring.
- I can compare the same candidate pool before and after reordering.
- I can preserve an identifier, duration and condition in a reviewed rewrite.
- I can explain the extra work and possible drift from multiple queries.
- I can keep complementary clauses while removing an exact same-source duplicate.
- I can show why compression and valid citations do not guarantee complete support.
- I can inspect the full serialized budget, source identity and citation offsets.
- I can run the assistant, a denied-source case and a budget failure without claiming learned-model quality.

Keep your lab output and a short decision note for the Week 8 project milestone. You now have a local assistant whose evidence path is inspectable. Week 9 asks how to evaluate that path and its eventual answers more systematically. The roadmap also suggests beginning selective applications at this milestone; describe what you built and measured with these boundaries intact.

## Further reading

- [Retrieve and rerank](https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html): the first-stage/second-stage architecture.
- [CrossEncoder API](https://sbert.net/docs/package_reference/cross_encoder/model.html): input, loading and output details for an actual model adapter.
- [Lost in the Middle](https://arxiv.org/abs/2307.03172): the original context-position research and its tested settings.
- [Python logging](https://docs.python.org/3.13/library/logging.html): emitting library events and configuring an application.
