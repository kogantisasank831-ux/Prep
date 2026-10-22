# Week 8: reranking, context construction and cited excerpts

This lab assembles **Procurement Knowledge Assistant v1**: controlled ingestion,
authorization-aware hybrid retrieval, reranking, conservative deduplication,
bounded source context, validated citations and basic logging. It continues the
Week 6/7 source versions instead of replacing their text.

The implementation is a local in-memory CLI. Answers contain selected source
excerpts with citation labels; no free-form answer generator or HTTP service is
added. The default dense path and pair reranker are explicitly named teaching
rules. Their visible-practice results are not real-model quality measurements.

## Run from the repository root

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m labs.week_08.demo --document-type framework_agreement
.venv/bin/python -m labs.week_08.compare --summary
.venv/bin/python -m pytest tests/test_week08_assistant.py -q
```

On Windows use `.venv\Scripts\python.exe`. Existing root dependencies are
unchanged. The teaching path uses the standard library and earlier lab modules;
it does not download models or call a hosted API.

Example requests:

```bash
.venv/bin/python -m labs.week_08.demo --query CW-1000
.venv/bin/python -m labs.week_08.demo --query SECRET-900
.venv/bin/python -m labs.week_08.demo --query CW-1000 \
  --supplier "Atlas Metals" --document-type catalogue \
  --rewrite "CW-1000 catalogue"
.venv/bin/python -m labs.week_08.demo --query CW-1000 --context-chars 2
```

The framework-agreement request selects the Net 30 clause, its Schedule A
cross-reference and the 1,000 kg row. Three spans occupy 707 serialized characters.
The denied identifier returns `no_evidence`. A two-character context budget is
valid because it fits `[]`, but a retrieved source cannot fit and produces
`context_budget_exhausted`.

The CLI writes answer JSON to stdout and safe completed-request events to stderr.
In the Python API use `KnowledgeAssistant.ask(RetrievalRequest(...))` with the
request's `top_k` equal to the configured evidence-unit count.

## Files and boundaries

| File | Responsibility |
| --- | --- |
| `data.py` | Bounded JSONL schema, parser acceptance, source continuity and independent demo grants |
| `corpus.jsonl` | Controlled synthetic parsed-layout documents, including review and denied cases |
| `pipeline.py` | Query plan, same-pool scoring, exact deduplication, context packing, citation validation and answer policy |
| `local_reranker.py` | Optional reviewed scalar raw-text pair-model boundary |
| `demo.py` | CLI request fields, logging configuration and inspectable answer JSON |
| `compare.py` | Paired baseline/treatment evaluation and context-support checks |
| `sample-comparison.json` | Executed default summary with input and configuration identity |
| `tests/test_week08_assistant.py` | Ingestion, scope, score, budget, citation and optional-backend regression cases |

The existing public document service and all previous-week source code remain
unchanged. This fixture loader does not persist user uploads, parse arbitrary
PDFs, run OCR or expose an authenticated service.

## Controlled ingestion contract

`--corpus` accepts UTF-8 JSONL, up to 128 KiB and 1–32 nonblank document records.
Every record must contain exactly these fields:

```json
{
  "tenant_id": "northwind-procurement",
  "document_id": "P-109",
  "version": "1",
  "title": "Separate synthetic payment example",
  "supplier": "Atlas Metals",
  "document_type": "payment_note",
  "blocks": [
    {
      "kind": "paragraph",
      "page": 1,
      "block_index": 1,
      "table_id": null,
      "row_index": null,
      "text": "Payment is due after approval."
    }
  ]
}
```

Identity, title and label strings are nonblank, valid UTF-8 and at most 200
characters. Each record has 1–32 blocks. Blocks have the exact fields shown,
`heading`, `paragraph` or `table_row` kind, positive integer page/block locations,
optional nonblank table ID and positive row index, and bounded nonblank text up
to 1,000 characters. Booleans are rejected as integer locations. The Week 6
parser also enforces its document and structural constraints.

Malformed JSON, duplicate JSON object keys, extra fields and invalid structures
fail the batch. Identical repeated records under `(tenant, document, version)`
are idempotent. Different content or asserted labels under that identity fail as
a conflict. Parser `needs_review` or `rejected` outcomes remain inspectable issues
and contribute no chunks. There is no partial persistent write to roll back.

The fixture contains nine records. Eight accepted documents produce twelve
chunks, including a denied private document. Seven accepted documents and eleven
chunks are visible to `analyst`. P-106's `USD 12.O0` table row remains under
review. P-101–105 preserve Week 6 text/version/chunk identity/location; P-107/108
preserve Week 7 catalogue identities. New examples should use separate IDs or
versions rather than editing frozen identities in place.

Supplier/type labels are input assertions, not parser accuracy measurements or
authorization grants. The manifest records their separate metadata policy.
`demo_access()` independently grants analyst access only to P-101–105 and
P-107/108, version 1, in `northwind-procurement`. A caller-supplied tenant label
or supplier filter cannot extend those grants.

## Request pipeline

1. Validate request identity, text, top-k and allowlisted exact filters. Retain
   the original question and at most two caller-reviewed variants.
2. Build one authorized/filter-eligible corpus before BM25 statistics or dense
   scoring. Reuse the same scope for every query variant.
3. Retrieve up to eight results per sparse/dense path, RRF-fuse to at most six
   per variant, then fuse variant lists into one capped six-item pool.
4. Score the original question against exactly those candidates. Require one
   finite scalar per pair, stable model identity and deterministic tie breaks.
5. Remove identical text only within the same tenant/document/version/digest.
   Preserve complementary clauses and distinct source/version evidence.
6. Select whole chunks by default or exact sentence spans experimentally. Keep
   table rows atomic. Admit all selected spans from a chunk together and count
   the full serialized JSON against the character budget.
7. Recheck access and validate every selected citation against the stored chunk
   and its exact integer offsets. Emit source excerpts with their labels.

Default configuration is six candidates, depth eight, three admitted source
units, 1,400 serialized context characters, whole chunks and at most two
sentences if compression is enabled. Counts must be exact integers, and
`1 <= evidence <= candidates <= depth <= 32`. Context budget is 2–16,000
characters; sentence limit is 1–4. These small bounds are teaching contracts.

The rewrite guard protects original digit-bearing tokens and a small set of
negation/condition words. It is not a semantic-equivalence check: rearranging
the same words can still change meaning. There is no automatic LLM rewriting.
Principal identity and structured metadata predicates are never rewritten.

Citation labels are unique `S1`, `S2`, etc. Quotes must equal authorized stored
spans. Locations describe the controlled parsed representation; chunk offsets
are not PDF byte/OCR coordinates. Exact-span validity does not establish claim
entailment, source authority or answer completeness. `evidence_available` means
some context survived, not that the answer is complete.

An invalid scorer output or changed model contract raises explicitly. A denied
principal or empty eligible search produces no evidence. Candidates unable to
fit the budget are distinguished from an empty candidate pool. No arbitrary
mid-sentence slicing is used to hide an admission failure.

## Paired practice comparison

```bash
.venv/bin/python -m labs.week_08.compare --summary
.venv/bin/python -m labs.week_08.compare
.venv/bin/python -m labs.week_08.compare --compression sentences --summary
.venv/bin/python -m labs.week_08.compare --context-chars 300 --summary
```

The baseline uses the first three hybrid candidates. The treatment reorders the
same pool and uses its first three. Both share the original request, source
versions, authorization, filters, practice labels and k. Candidate-pool recall
is reported separately. The full output contains keys, context-support results,
statuses and request-manifest fingerprints for each query.

Fourteen visible Week 7 queries include ten labelled cases and four no-gold
probes. Evidence labels must resolve uniquely inside each eligible snapshot;
declared atoms must exist in their source text. Practice keys omit tenant only
because these labels resolve to one eligible tenant; ambiguity fails.

| Default labelled mean | Hybrid top 3 | Teaching reranker top 3 |
| --- | ---: | ---: |
| Precision@3 | 0.400000 | 0.433333 |
| Recall@3 | 0.966667 | 1.000000 |
| MRR@3 | 0.900000 | 0.950000 |
| Binary nDCG@3 | 0.916165 | 0.963093 |

Candidate Recall@6 is 1.0. Q09's top three change from P-105 blocks 2/9/6 to
8/9/6, promoting the actual payment clause. The final context's required-atom
support fraction is 1.0 by default, 0.9 under sentence compression and 0.7 with
a 300-character whole-chunk budget. The check uses the specifically labelled
source/version and selected text; it is not a semantic answer judge.

Precision uses requested k even for a short list. Recall/rank/nDCG stay null for
no-gold cases and are excluded from labelled means. All four no-gold probes
return empty here; that is not a calibrated relevance/abstention guarantee.

The dense feature scorer and pair rules are synthetic and visible. No held-out
quality, real embedding/reranker quality, generated-answer faithfulness,
latency, memory use or lost-in-the-middle effect was measured. A real decision
needs a frozen held-out set, paired category outcomes and hardware-specific
timing/cost measurements. Changing first-stage depth while changing the reranker
is a different end-to-end experiment and must be reported as such.

## Optional actual scalar cross-encoder

Review and materialize a compatible model yourself. The adapter assumes plain
raw question/passage pairs, one scalar output and no required model-specific
instructions. Multiclass or instruction-based rerankers need another adapter.
Review model card, license, revision, preprocessing, token limit and activation;
do not infer a probability of correctness from a relevance score.

```bash
# Existing optional pin; use an isolated compatible environment if needed.
.venv/bin/python -m pip install -r labs/week_05/requirements-local-model.txt
.venv/bin/python -m labs.week_08.compare --summary \
  --reranker-directory /path/to/reviewed-materialized-scalar-model \
  --reranker-id reviewed-model-and-revision \
  --reranker-token-limit 512
```

`512` is illustrative, not a universal limit. The loader uses local files only,
CPU, `trust_remote_code=False`, `token=False` and empty role prompts for this
narrow contract. It records artifact hashes before/after loading and runtime
versions. It checks scalar output and the current `max_seq_length` contract.
Joint pair tokenization includes special tokens, disables truncation and rejects
overlength inputs before prediction. Unknown/unbounded tokenizer limits fail.

These boundary behaviors are fake-backend tested against the pinned 6.1.0 API.
No actual weights were loaded during the default validation. A successful real
inference run would establish integration only; evaluate quality separately.
The first-stage dense scorer remains the teaching implementation when this
option changes only the reranker.

Primary implementation references:
[retrieve/rerank](https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html),
[CrossEncoder API](https://sbert.net/docs/package_reference/cross_encoder/model.html),
[pinned source](https://github.com/huggingface/sentence-transformers/blob/v6.1.0/sentence_transformers/cross_encoder/model.py).

## Logs, manifests and next steps

Library code emits `assistant_request_completed` with safe request ID, candidate
count, selected-span count, status and manifest fingerprint. It never configures
the root logger. The CLI configures its handler once and allowlists event
fields. Raw queries, source text and prompts are excluded from its event output.

The request manifest binds eligible corpus/partition, ordered query digests,
retrieval manifests, model identity, configuration and versioned selection/
answer policies. Digests support reproducibility under a trusted manifest;
they are not authenticity signatures or evidence of answer truth.

To extend this milestone, evaluate held-out questions and revised-source
authority, add a generator with its own exact token budget and claim-support
evaluation, then design persistence, authentication, retention, observability,
timeouts and deployment separately. A position experiment must hold evidence
membership/wording/length fixed. See the original
[Lost in the Middle paper](https://arxiv.org/abs/2307.03172) for the studied
failure mode; it is not measured by this context-only lab.
