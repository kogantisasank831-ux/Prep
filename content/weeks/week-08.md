---
layout: week
week: 8
phase: 2
status: approved
version: 1.0.0
last_reviewed: 2026-10-22
estimated_hours: 8
permalink: /weeks/week-08/
title: "Reranking and context construction: turn candidates into cited evidence"
description: Compare reranking on a fixed candidate pool, preserve procurement conditions during context construction, and assemble a local assistant with validated citations.
summary: Follow the missing Schedule A payment clause from hybrid candidates through pair scoring, careful deduplication, bounded context and cited source excerpts.
kicker_primary: Reranking and context construction
kicker_secondary: Procurement Knowledge Assistant v1
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-08/beginner/
---

Test your understanding with the [Week 8 assessment]({{ '/assessments/week-08/' | relative_url }}): a random ten-question paper from 100 questions, including Python exercises on reranking, protected rewrites, exact source spans, context budgets and citations.

## The right document can still leave you without an answer

Last week, hybrid retrieval found P-105, the Atlas Metals framework agreement. That sounds like success until someone asks: “What payment condition controls Schedule A for the 1,000 kg copper-wire line?” The first three chunks contain the supplier, the line item and a cross-reference. The clause that actually says **Net 30 after inspection approval** sits farther down the candidate list.

This is a useful failure. We do not need another document, and a fluent answer will not repair the missing evidence. We need to choose the right passages from the material we already retrieved, then preserve their relationship when we construct context.

Week 8 adds that second stage. You will compare a bi-encoder with a cross-encoder, measure a reranker on the same candidate pool, review query variants, remove only justified duplicates, fit evidence into a declared budget and validate every displayed citation. The build finishes **Procurement Knowledge Assistant v1**: controlled document ingestion, hybrid retrieval, reranking, cited answers and basic logging.

The included assistant is a local, in-memory teaching CLI. Its answers are **cited source excerpts**. A deterministic pair scorer lets you inspect the pipeline without downloading a model; an optional adapter accepts a reviewed local scalar cross-encoder. Neither the default dense scorer nor the default reranker is a trained model. Keep that distinction attached to every result you report.

Bring Week 5's ranking metrics, Week 6's source identities and chunk boundaries, and Week 7's authorized hybrid snapshot. The [beginner lesson]({{ '/weeks/week-08/beginner/' | relative_url }}) develops the same ideas more slowly.

| Time | Work | Evidence of understanding |
| --- | --- | --- |
| Hour 1 | Inspect the missing payment clause | Explain why document-level relevance is insufficient |
| Hours 2–3 | Compare encoders and score a fixed candidate list | Separate candidate recall from ordering quality |
| Hour 4 | Review rewrites and fuse query variants | Preserve codes, quantities, conditions and access scope |
| Hour 5 | Deduplicate and compress an example | Identify a removed qualifier or complementary clause |
| Hours 6–7 | Run the assistant and paired comparison | Inspect citations, budgets, logs and failure cases |
| Hour 8 | Complete exercises and interview explanations | Write a measured decision with its limits |

## Give retrieval and reranking different jobs

Ask two questions in sequence. First: “Which passages deserve closer inspection?” Then: “Which of those passages best answers this question?” The first stage searches an eligible collection. The second stage spends more work on a bounded shortlist.

In this lab, authorization and metadata predicates determine the eligible corpus before either sparse or dense scoring. Hybrid retrieval takes up to eight candidates from each path, fuses them and keeps at most six. The reranker scores that same bounded pool against the original question. Context construction then admits evidence from at most three source chunks, subject to a 1,400-character serialized-context budget.

These are separate limits:

| Limit | Default | What it controls |
| --- | ---: | --- |
| Retrieval depth per path | 8 | How far BM25 and the dense path can contribute |
| Fused candidate count | 6 | How many query–passage pairs reach the reranker |
| Evidence source-unit count | 3 | How many distinct admitted chunks can supply context |
| Serialized context characters | 1,400 | JSON headers, source locations, text and punctuation together |
| Query variants | Original plus at most 2 | Additional first-stage retrieval work |

Increasing retrieval depth can help a missing clause reach the shortlist. Increasing the evidence budget can expose more shortlisted material. Increasing one does not silently increase the others. Production values need workload and hardware measurements; these small defaults are teaching choices.

Suppose the eligible gold evidence consists of three chunks and the six-candidate pool contains only two. Even a perfect reordering can return at most those two, so Recall@3 cannot exceed 2/3 for that request. If all three enter the pool but only two enter the top three, reranking has room to improve the result. Inspect that candidate ceiling before changing the scoring model.

**Checkpoint:** If a payment clause is absent from all six candidates, which stage should you investigate first? Start with ingestion, chunking, eligibility and candidate retrieval. A reranker cannot score a passage it never receives.

## Why a cross-encoder sees a different problem

A bi-encoder represents a query and a passage separately. A similarity function compares those representations. Passage vectors can be prepared before the query arrives, which makes this useful for retrieving from a large collection.

A cross-encoder processes a query and a passage jointly. Query tokens can interact with passage tokens during that computation. This gives the model an opportunity to distinguish “payment is due after inspection approval” from a passage that mentions payment and inspection separately. It also requires query-dependent work for each pair, rather than one reusable passage embedding.

| Question | Bi-encoder | Cross-encoder reranker |
| --- | --- | --- |
| What is computed? | Separate representations, then similarity | A score for the query–passage pair |
| Can passage representations be reused? | Usually, under a fixed model/preprocessing contract | A final pair score depends on the query |
| Where is it useful? | Candidate discovery over a collection | Detailed ordering of a shortlist |
| What can go wrong? | Exact identifiers or relationships may be missed | Truncation, domain mismatch, poor calibration, missing candidates |

The [Sentence Transformers retrieve-and-rerank guide](https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html) describes this two-stage arrangement. It is an architecture, not a guarantee that every cross-encoder improves every corpus. Compare your actual model and task.

A relevance score is also not a probability that the passage is true. Depending on the model and activation, it may be a logit or transformed scalar. The [CrossEncoder API](https://sbert.net/docs/package_reference/cross_encoder/model.html) exposes model-dependent scoring and activation options. Do not invent a universal “0.8 means safe” threshold.

Before loading a model, establish a narrow interface: input is a bounded ordered list of `(original_question, passage_text)` pairs; output is exactly one finite scalar per pair. Reject the wrong output length, NaN, infinity, booleans and a model identity that changes during the request. Break equal-score ties by original retrieval rank, then stable chunk ID. The result should be reproducible enough to diagnose.

The default implementation deliberately makes its rules visible:

```python
from labs.week_08.pipeline import TeachingPairScorer

question = "Net 30 after inspection approval"
scores = TeachingPairScorer().score_pairs((
    (question, "Invoice terms: Net 30 after inspection approval."),
    (question, "The receiving team records an inspection."),
))
assert scores[0] > scores[1]
print(scores)
```

It counts unique-token overlap, adds bonuses for a few commercial phrases and contains a small payment-clause rule. It is useful for tracing a reranker boundary, but its improvement on visible procurement examples is partly constructed by those rules. It is **not** evidence of learned language understanding. The optional local model must pass the same output contract, and its effectiveness must be measured separately.

**Checkpoint:** Can the default scorer prove a statement is commercially correct? No. It only assigns a teaching relevance score. We still need source identity, support and a clear answer policy.

## Measure the reorder without changing the contest

To ask whether reranking improves the top results, freeze the candidates for each query. The baseline is the first three items from the hybrid pool of at most six. The treatment is the first three after scoring and sorting that entire pool. Keep source versions, eligibility, filters, labels and requested k equal.

If you retrieve a larger pool only for the treatment, you have changed retrieval work as well as ordering. That can be a useful end-to-end experiment, but it does not isolate the reranker. Record it as a different comparison.

The lab reuses fourteen visible Week 7 practice queries: ten have evidence labels, while four probe unmapped aliases, OCR variants, abbreviations and a denied identifier. Relevance is labelled at the source/version/body-block level. A label must resolve uniquely inside the eligible snapshot, and each required text atom must actually exist in its declared chunk.

| Metric | What it asks | What it does not establish |
| --- | --- | --- |
| Candidate Recall@6 | Did the pool include the labelled evidence? | Correct order or adequate final context |
| Precision@3 | How many of the three requested slots contain labelled evidence? | Whether every required clause survived |
| Recall@3 | How much of the labelled evidence reached the top three? | Answer correctness |
| Reciprocal rank / MRR@3 | How early did the first relevant item appear? | Completeness for a multi-clause question |
| Binary nDCG@3 | How favorable is the ordering under binary labels? | Invented degrees of relevance or model confidence |
| Context support complete | Did declared atoms survive in their labelled source spans? | Semantic entailment or free-form answer faithfulness |

Precision uses the requested denominator three even if fewer items return. Recall, reciprocal rank and nDCG are undefined for a no-gold case and remain null. Report those cases separately instead of quietly counting them as perfect retrieval or automatically treating every nonempty result as a false positive.

For Q09, the important change is concrete:

| Stage | P-105 evidence keys in order |
| --- | --- |
| Hybrid top three | `P-105/1/2`, `P-105/1/9`, `P-105/1/6` |
| Teaching reranker top three | `P-105/1/8`, `P-105/1/9`, `P-105/1/6` |

Block 8 carries the Net 30 clause. Block 9 links that condition to Schedule A. Block 6 supplies the 1,000 kg line item. All three have a job; replacing the supplier summary with the actual clause is what repairs this example.

**Checkpoint:** Could MRR improve while the answer still lacks the quantity? Yes. MRR rewards the first relevant result. A question that needs three evidence units needs a completeness check too.

## A rewrite must keep the question's constraints

Imagine a user asks for `CW-1000 Net 30 after inspection approval`. A rewrite that says “Atlas payment details” may improve broad topic matching while losing the product code, duration and dependency. Fluent wording alone is not a safe search plan.

The lab accepts at most two **caller-reviewed** rewrites. It retains the original query, removes exact repeated variants and checks that every original token containing a digit survives. It also preserves a small allowlist of negation and relationship words, including `not`, `except`, `unless`, `after` and `before`.

```python
from labs.week_08.pipeline import PipelineError, query_plan

original = "CW-1000 Net 30 after approval"
queries = query_plan(original, ("CW-1000 payment terms Net 30 after approval",))
assert queries[0] == original
try:
    query_plan(original, ("CW-1000 payment terms",))
except PipelineError:
    print("Review required: the rewrite dropped a constraint.")
else:
    raise AssertionError("an unsafe rewrite was accepted")
```

This check catches specific lexical losses. It cannot prove equivalence. “Approval after Net 30” retains the protected words but can reverse the intended relationship. Supplier aliases, pronoun resolution, date ranges and “not more than” also require more than a token subset. Keep a semantic review, use a controlled domain mapping where appropriate, and evaluate original-versus-rewritten retrieval before adopting automatic rewriting.

Principal identity and metadata filters remain structured request fields. A rewritten query cannot grant access to another tenant or change a supplier predicate. If a future LLM proposes a query, validate its output as data at that boundary; do not let it choose authorization policy.

**Checkpoint:** Why retain the original query even when a rewrite looks good? It preserves an independent retrieval path for exact wording and makes it possible to inspect what the variant added or displaced.

## Multi-query retrieval adds opportunities and work

A query about “receiving-team sign-off” and a reviewed variant about “inspection approval” may find complementary passages. Retrieve each variant against the same authorized, filtered snapshot. Each variant gets the declared first-stage depth and contributes one ranked list. Fuse those lists with a second RRF step, cap the final pool at six, then rerank against the **original** question.

For a chunk present at rank 1 in both lists, its second-stage fusion score with constant 60 and equal weights is `1/61 + 1/61`. Another chunk present only at rank 2 receives `1/62`. This arithmetic gives repeated support a chance to help without mixing raw model scales. It does not prove the duplicated evidence is more relevant.

More variants can increase recall, widen topic drift and increase the number of retrieval calls. A fixed final cap means a new candidate can displace an old one. Identical query text is deduplicated, but semantically redundant variants can still overweight one interpretation. Log the ordered query digests, per-query retrieval manifests, fusion configuration and final candidate identity so you can reproduce a surprising result.

The normal comparison uses only the original query. If you add variants, run a separate experiment that reports their extra retrieval work. In a service, query parallelism, timeouts and partial failures need an explicit policy; the local CLI executes a small sequence and makes no latency claim.

## Deduplicate redundancy without deleting the answer

Three passages from P-105 are not necessarily three copies of the same fact. A table row, a payment clause and the cross-reference joining them are complementary evidence. A policy that keeps only one chunk per document would destroy Q09's support.

The default deduplicator removes only identical text with the same tenant, document ID, document version and source digest. It keeps the highest-ranked occurrence and records dropped chunk IDs. Equal text from a different source or version remains separate evidence.

| Pair of passages | Default decision | Reason |
| --- | --- | --- |
| Same source/version/digest and exactly equal text | Keep the first | Avoid repeated bytes from that source |
| Same agreement, different clauses | Keep both | They may establish a dependency |
| Same text, different versions | Keep both | Version validity needs a separate policy |
| Same text, different suppliers/documents | Keep both | Corroboration and conflicting authority are separate concerns |
| Similar wording, different quantities | Keep both | Similarity can hide a material difference |

This conservative rule will miss semantic duplicates and repeated headers embedded in otherwise different chunks. That is a deliberate limit, not a finished duplicate detector. A broader policy needs document authority, active-version rules, numeric/identifier protection and evaluation of lost evidence. Reranker similarity scores alone do not supply those decisions.

Deduplication follows scoring here so the highest-ranked copy survives. Source diversity can be a later selection objective, but do not maximize diversity at the expense of required clauses from the same document. Inspect the answer's evidence structure before adding a diversity heuristic.

**Checkpoint:** Should two different versions with the same paragraph be collapsed by exact text alone? No. First decide which version the question is permitted to use. Text equality does not settle effective dates or authority.

## Compression changes what evidence the reader receives

Whole chunks are easy to inspect, but some contain material that does not help the question. Compression tries to use less context for the same needed evidence. The hard part is “the same”: shorter text can omit the condition that makes a sentence correct.

Consider this separate teaching passage:

```text
Payment is due. Except disputed invoices require approval.
```

If a sentence selector keeps only the first sentence for a “payment due” query, every remaining character is an authentic source quote. The source offsets can be valid while the result is materially incomplete. Compression has not hallucinated a word; it has removed a qualifier.

The optional `sentences` mode ranks sentence spans by unique query-token overlap and keeps at most two per chunk, in original source order. Its sentence splitting is a narrow punctuation rule, not a linguistic parser. It preserves the original character offsets and never rewrites selected text. Table-row chunks stay whole so a price does not lose its product, quantity or unit.

This is an experiment, not the default policy. Sentences can depend on headings, pronouns, exceptions or neighboring clauses. Repeating source headers and keeping every selected span from a chunk together make the transformation traceable; neither proves that its meaning is sufficient. On the visible practice set, this mode loses one query's declared support even though exact-span citation checks still pass.

Abstractive compression adds another boundary: a model creates new text that may alter a number, merge sources or erase a negation. To adopt it, preserve source alignment, evaluate required facts and conditions, validate structured output and compare with an extractive baseline. Do not label a generated summary as a verbatim source quote.

**Checkpoint:** Why are valid citation offsets insufficient to approve compression? They prove where a surviving quote came from. They say nothing about the source material the compressor discarded.

## Budget the context you actually serialize

Five hundred characters of source text do not produce a five-hundred-character context. The envelope also includes citation labels, document/version identifiers, locations, separators and JSON escaping. Counting only paragraph lengths makes the budget misleading.

`pack_context` processes the reranked, deduplicated list in order. It rechecks source access, proposes all selected spans from the next chunk, serializes the entire proposed context and admits that chunk only if it fits. It stops after three admitted source units. A source that is too large is skipped, allowing a later smaller source to fit; it never slices a sentence or a numeric row halfway through.

Each selected span gets a stable label within the answer, such as `S1`. Multiple sentence spans from one chunk get separate labels but consume one admitted source-unit slot. The budget is measured over the actual JSON string, including all repeated source headers. An empty context is `[]`, which requires two characters. If candidates exist but none fit, the assistant reports `context_budget_exhausted` rather than calling that a retrieval miss.

The character budget is intentionally inspectable, and it is **not** a model token limit. When you add a real generator, use its tokenizer over the exact rendered input and its actual chat template. A planning equation is:

```text
available context tokens
  = model input/output window
  - system and developer instructions
  - user question and retained conversation
  - source wrappers and tool/schema overhead
  - reserved output tokens
  - safety margin required by the serving contract
```

Check the serving API's actual input/output constraints; a single advertised window number may not describe every limit. Tokenize the final messages, including delimiters and wrappers. Do not use a fixed “four characters equals one token” conversion as enforcement, especially for codes, JSON or different languages.

Pairwise reranking has its own joint input budget. A 200-token query and a 450-token passage can exceed a 512-token pair limit after special tokens, even though each fits alone. The optional adapter checks the joint tokenization with truncation disabled and rejects an oversized pair before inference. Silent passage truncation could remove the payment condition you are trying to rank.

## Context order is an evaluation variable

Once the right evidence fits, where should it go? Ranking order is a sensible initial policy: put the most relevant item first. It is still a policy to test, especially when context becomes long or the answer depends on several related passages.

The 2023 study [Lost in the Middle](https://arxiv.org/abs/2307.03172) varied evidence position in multi-document question answering and key-value retrieval. In the evaluated settings, relevant information was often used better near the beginning or end than in the middle. That is evidence of a positional failure mode in those experiments, not a universal curve for every current model or prompt.

To test your generator, hold evidence membership, wording, total length, question and generation settings fixed. Move the decisive clause to the beginning, middle and end; repeat across representative questions and seeds where appropriate. Measure answer correctness, condition preservation, citation support and abstention. Compare relevant-first, grouped-source and other ordering policies only after you can separate membership effects from position effects.

Adding filler changes length and content as well as position. Changing which chunks fit changes evidence membership. Record those changes instead of calling the entire difference a lost-in-the-middle effect. The current lab assembles context and has no generative model, so it reports **no measurement of position effects**.

**Checkpoint:** Does a 100% context-support score prove a model will use the evidence? No. The needed text can be present and the generator can still overlook or misinterpret it.

## A citation needs a resolvable source and a supported claim

There are at least three distinct questions to ask of a cited answer:

1. **Validity:** Does the citation resolve to an authorized stored source/version and the exact displayed span?
2. **Support:** Does that evidence substantiate the claim, with its qualifiers and relationships?
3. **Correctness:** Is the answer adequate for the question under the applicable source authority and task rules?

The validator in this lab handles the first question deterministically. It verifies a unique citation label, the entire stored chunk identity/text/metadata, source access, integer offsets within bounds and exact equality between the quote and the stored slice. A matching document name alone is insufficient. A quote from version 1 cannot be silently relabelled as version 2.

Source locations are the Week 6 parsed-layout labels: page, block and table row where present. Span offsets are relative to the stored chunk text, which can include a repeated heading. They are not PDF byte positions, OCR coordinates or a claim that arbitrary source files have been parsed. The input source digest and parsed/chunk policy metadata retain the lineage needed to interpret them.

The answer builder emits each selected quote with its validated label. It does not ask an LLM to synthesize a commercial recommendation. `evidence_available` means at least one eligible span survived selection; it does not mean the answer is complete. The comparison's support-atom check is a separate, limited check of declared fixture facts in specifically labelled evidence.

If you later generate prose, make claims and evidence alignment explicit. Reject invented labels and foreign sources outside the context. Evaluate unsupported inferences, contradictions, numeric relationships, omissions and abstention. The phrase “the cited source exists” should never stand in for “the answer is supported.”

## Assemble Procurement Knowledge Assistant v1

Run commands from the repository root. Reuse the existing Python environment and pinned development dependencies:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m labs.week_08.demo --document-type framework_agreement
.venv/bin/python -m labs.week_08.compare --summary
.venv/bin/python -m pytest tests/test_week08_assistant.py -q
```

On Windows, use `.venv\Scripts\python.exe` in place of `.venv/bin/python`. You do not need the optional model stack for these commands. The [lab README](https://github.com/kogantisasank831-ux/Prep/tree/main/labs/week_08) explains the file contract, optional model path and experiments.

The fixture file contains nine controlled parsed-layout records. Eight are accepted into the local collection, producing twelve chunks. One of those documents is a synthetic private distractor in another tenant. The analyst's independent grants expose seven accepted documents and eleven chunks. P-106, the uncertain `USD 12.O0` OCR example, remains `needs_review` and produces no searchable chunks.

The loader enforces a 128 KiB batch limit, 1–32 records, exact fields, bounded strings and positive integer locations. Duplicate JSON keys fail. An identical repeated source/version record is idempotent; conflicting content or labels for the same identity fail the batch. Parser review/reject outcomes are retained as issues and excluded from the index. The collection is in memory; no durable ingestion store or PDF parser has been added.

P-101 through P-105 retain their Week 6 text, versions, chunk IDs and locations. P-107 and P-108 keep the separate Week 7 catalogue identities. Supplier and document-type fields are asserted fixture metadata; they do not grant authorization and their policy is recorded separately from parser provenance.

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

For this request, the final context contains three source spans and occupies 707 serialized characters. The answer quotes the invoicing clause, its cross-reference and the Schedule A row. Each displayed citation includes the source/version/chunk, source digest, page/block/row labels, offsets and quote.

The sequence has observable boundaries: parse and accept; build the eligible snapshot; retrieve/fuse; score the same pool; deduplicate; select spans under budget; validate citations; emit excerpts. Invalid scorer output or identity drift fails explicitly. No eligible candidates yields `no_evidence`; candidates that cannot fit yield `context_budget_exhausted`.

Basic logging uses Python's standard `logging` API. Libraries emit events without installing handlers; the CLI installs a formatter once. Its completed-request event includes a bounded request ID, candidate count, selected-span count, status and manifest fingerprint. It excludes raw questions, document text and model prompts. A future service still needs a retention policy, failure/latency metrics and operational handling; these local events are the milestone's starting point.

The request fingerprint binds the authorized corpus/partition, ordered query digests, retrieval manifests, reranker identity, all selection budgets and versioned dedup/context/answer policies. That makes a change explainable. A hash is not an authenticity signature, and a trusted manifest cannot make an untrusted model truthful.

## Read the measured result with its limits attached

The checked-in `sample-comparison.json` is the executed default summary. Means below use only the ten labelled practice questions; the four no-gold cases are reported separately. Every baseline/treatment pair uses the same candidate pool, sources and k.

| Practice metric | Hybrid ordering | Teaching pair reranker |
| --- | ---: | ---: |
| Mean Precision@3 | 0.400000 | 0.433333 |
| Mean Recall@3 | 0.966667 | 1.000000 |
| MRR@3 | 0.900000 | 0.950000 |
| Mean binary nDCG@3 | 0.916165 | 0.963093 |

Mean candidate Recall@6 is 1.0. The default final contexts preserve all declared support atoms on the ten labelled examples. All four no-gold probes return empty with these narrow default scorers. That behavior is not a general out-of-domain detector or a calibrated abstention policy.

Now change only context construction:

```bash
.venv/bin/python -m labs.week_08.compare --compression sentences --summary
.venv/bin/python -m labs.week_08.compare --context-chars 300 --summary
```

| Context policy | Labelled questions with complete declared support |
| --- | ---: |
| Whole chunks, 1,400 characters | 1.0 |
| Up to two sentence spans per chunk, 1,400 characters | 0.9 |
| Whole chunks, 300 characters | 0.7 |

These are visible synthetic practice results. The rules were written with this domain in view, the corpus is small and the support check uses substrings. The table demonstrates pipeline behavior and useful diagnostics. It does not establish learned reranker quality, generalization, generated-answer faithfulness, latency, memory use or positional robustness.

For a credible model decision, freeze a held-out set with representative commercial questions, multi-clause support, unavailable answers, revised documents and access boundaries. Compare paired query outcomes and category regressions, not just an overall mean. Measure model loading/inference and end-to-end latency on the intended hardware. Report candidate depth, pair length, batching, retries, truncation policy and cost along with quality.

## Try a real local reranker only under a reviewed contract

The optional adapter targets an already materialized plain-text pair model with one scalar output. It disables remote-code trust and downloads, uses CPU, records the model-directory digest before and after loading, clears role prompts for this narrow contract and requires an explicit reviewed joint token limit. The existing optional requirements pin Sentence Transformers 6.1.0. Its loader and prediction boundary have fake-backend tests; no real weights were loaded for this lesson's results.

```bash
# Use a separate compatible environment if the optional torch stack requires it.
.venv/bin/python -m pip install -r labs/week_05/requirements-local-model.txt
.venv/bin/python -m labs.week_08.compare --summary \
  --reranker-directory /path/to/reviewed-materialized-scalar-model \
  --reranker-id reviewed-model-and-revision \
  --reranker-token-limit 512
```

`512` is an example contract value, not a recommendation for an arbitrary model. Review the model card, license, artifact revision, required inputs/prompts, joint limit, activation and domain fit first. Instruction-based or multiclass rerankers need a matching adapter rather than being squeezed into this interface. A local path does not itself establish that model files are trusted.

This command changes the reranker only. The first stage remains the explicitly named Week 7 teaching dense adapter plus BM25. If you later replace that too, record its identity and evaluate it as a separate experiment. Inference success establishes integration, not a quality improvement.

## Explain the decisions in an interview

**Why use both a retriever and a reranker?** A retriever cheaply narrows the eligible corpus; a query–passage model can spend more computation ordering that shortlist. I choose candidate and context budgets separately, measure candidate recall as a ceiling and compare the reranker against the original order of exactly the same pool. The quality/cost trade-off depends on the actual model, workload and hardware.

**How do you keep context construction from damaging evidence?** I retain source/version/location identity, use a conservative duplicate policy, count the actual serialized context and keep exact spans. I test conditions, exceptions, numbers and cross-references after selection. Exact citations are necessary for traceability, while support and answer correctness require additional checks. I compare compression with whole chunks rather than assuming shorter means better.

**What does your first assistant demonstrate, and what remains?** It ingests bounded controlled layout records, keeps uncertain OCR under review, applies source-version grants before retrieval, reranks a fixed pool and emits validated cited excerpts with safe request events. It demonstrates deterministic boundaries and practice evaluation. Real model quality, free-form generation, persistent ingestion, service authentication, operational SLOs and deployment hardening remain separate work.

## Check what you can explain without the page

1. **What ceiling limits a reranker?** The relevant evidence present in its candidate pool.
2. **Why can't a cross-encoder reuse one final passage score for every query?** It scores query and passage jointly; relevance depends on the pair.
3. **What must stay fixed in a same-pool comparison?** Candidate membership, eligible sources/versions, labels, filters and requested k.
4. **Why retain the original query?** A variant may drop or distort exact constraints; the original remains an independent retrieval path.
5. **Does token preservation prove rewrite equivalence?** No. It cannot establish relationships or scope.
6. **Why keep three chunks from one agreement?** They may jointly supply a fact, condition and cross-reference.
7. **Can extractive compression be misleading?** Yes. Exact surviving sentences can omit a qualifier.
8. **What belongs in a context budget?** The actual rendered envelope, text and overhead under the relevant tokenizer; the lab enforces characters only.
9. **What does citation validation prove here?** Authorized stored identity and exact quoted offsets, not entailment or completeness.
10. **Was lost-in-the-middle measured in the lab?** No. No generative model was run.

## Exercises that leave inspectable evidence

1. **Expose the candidate ceiling.** Lower candidate count/depth together while keeping evidence count valid. Find a query that loses a labelled source from the pool. Submit the before/after candidate keys, Recall@pool and Recall@3; explain which stage now limits quality.
2. **Audit a rewrite.** Propose one useful and one misleading variant for a code-plus-payment question. Keep principal and filters fixed. Show what the lexical guard catches and a meaning change it cannot catch. Review the candidate additions/displacements before deciding whether to retain the variant.
3. **Protect complementary evidence.** Add a repeated chunk within one source version and a separate authoritative version with the same wording. Show that the duplicate is removed, the separate version remains and Q09's three distinct clauses survive. Do not edit the frozen sources in place.
4. **Break compression safely.** Add a new controlled source with an exception in a second sentence. Compare whole-chunk and one-sentence context, including exact offsets and a required exception label. Demonstrate that a valid citation can accompany incomplete evidence.
5. **Sweep the budget.** Run at 300, 700 and 1,400 characters. Record admitted keys, serialized length, status and support completeness. Explain a skipped large chunk and whether a later small one fits; never infer model token use from character counts.
6. **Design the positional test.** Write a protocol that holds evidence and wording fixed while varying the decisive clause's position. Specify questions, generator identity, token lengths, settings, metrics and repetition. Label the protocol as proposed until you run it.
7. **Evaluate an actual reranker.** With an approved compatible local artifact, compare paired outcomes and latency against the unchanged first-stage baseline. Record artifact/runtime/input contracts and category failures. If no model is available, submit the experiment design and keep learned-quality claims unmeasured.

For each exercise, retain the request, source/configuration identity, observed result, failure explanation and next change. A successful command alone is not the acceptance criterion; another reader should be able to reproduce the claim.

## Your Week 8 handoff

You are ready to move on when you can run the assistant from ingestion to citations, explain the missing-clause repair, reproduce the paired summary, demonstrate a denied-source case and a context-budget failure, and show why compression or a rewrite can silently change support. Keep the runnable lab, a short decision note, comparison output and a list of unmeasured properties in your weekly project record.

This is also the roadmap's first application milestone. You have a concrete system to discuss: describe the local teaching scope, the deterministic boundaries and the measurement limits honestly. Week 9 builds the broader evaluation discipline around it: datasets, retrieval and answer metrics, groundedness, unavailable answers and regression tracking.

## Primary sources

- [Sentence-BERT paper](https://arxiv.org/abs/1908.10084): separately computed sentence representations and the bi-encoder motivation.
- [Sentence Transformers retrieve and rerank](https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html): shortlist retrieval followed by pair scoring.
- [CrossEncoder API](https://sbert.net/docs/package_reference/cross_encoder/model.html) and [the pinned 6.1.0 implementation](https://github.com/huggingface/sentence-transformers/blob/v6.1.0/sentence_transformers/cross_encoder/model.py): model-loading and scoring contracts; check the pin when implementing adapters.
- [Lost in the Middle](https://arxiv.org/abs/2307.03172): the original positional experiments and their settings.
- [Python logging](https://docs.python.org/3.13/library/logging.html): module loggers, application configuration and structured event fields.
