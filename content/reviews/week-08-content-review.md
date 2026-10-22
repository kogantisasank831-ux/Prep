---
week: 8
phase: 2
status: approved
version: 1.0.0
last_reviewed: 2026-10-22
generation_surface: Codex in ChatGPT Work
publication_authorization: Continuation of the user's explicitly approved weekly creation-and-push workflow
---

# Week 8 review: reranking and Procurement Knowledge Assistant v1

## Baseline, authorization and recovery

Repository: `kogantisasank831-ux/Prep`. Remote main at the start of this pass:
`a13759a006711ad729b4170dee62c7b4ff6aa867`, tree
`a7068c4fa87ca4af940ec0fbc901084627765f67` (published Week 7).
Work used `week08-content` from a fresh `origin/main` fetch. The root
`AGENTS.md` is the only applicable instruction file. The existing untracked
Week 4–7 QA directories were preserved. No `Design/` specification applies to
this curriculum repository; `Path.md` Week 8 and `plan.md` define this work.

The prior Week 8 session finished local work, but its first GitHub blob upload
was interrupted. On the user's “did this complete” follow-up, remote main was
still at Week 7. The prior Week 8 commit and files were absent from this restored
workspace, and the expected remote tree/first blob returned 404. This pass rebuilt
the change from the retained scope and implementation notes, then re-executed
validation. It does not claim byte-for-byte recovery of the lost local artifact.

The user's Week 8 request continues the established direct generation,
verification, push and Pages-verification workflow, already explicitly approved
in this conversation. No separate human rubric scores or independent review are
invented. Candidate lessons were executed and structurally rendered before
canonical integration. Approval/provenance stays in this excluded review path.

## Inspected evidence and scope

Inspected root instructions, curriculum and content workflow; existing Week 7
main/beginner lessons, review, navigation and layout; Week 5 local model and
ranking metrics; Week 6 typed parser/chunk/fixture contracts; Week 7 source
fixtures, hybrid/authorization/manifest contracts, comparison and query labels;
the pinned root and optional dependency declarations and available QA tools.

| Week 8 requirement | Implemented coverage |
| --- | --- |
| Cross-encoder / bi-encoder | Joint pair scoring versus separate representations, costs, candidate ceiling and model-dependent scores |
| Query rewriting | Original retained; up to two reviewed variants; identifier/number/condition lexical guard with explicit semantic limits |
| Multi-query retrieval | Same authorized/filter snapshot, per-query hybrid lists, second RRF and bounded combined pool; original question for reranking |
| Deduplication | Exact text scoped to tenant/document/version/digest; complementary clauses and distinct sources/versions retained |
| Context compression | Optional exact sentence spans, original order and offsets, atomic table rows, demonstrated qualifier/support loss |
| Context formatting | Full serialized JSON character budget including headers; whole selected unit admission; distinct empty/admission statuses |
| Lost in the middle | Original study and a proposed controlled positional protocol; no unexecuted generator result claimed |
| Cited answers | Authorized stored chunk/version/offset checks; cited extractive answer policy; validity/support/correctness distinguished |
| Milestone | Bounded controlled JSONL ingestion, hybrid retrieval, reranking, cited excerpts and safe basic request events |
| Measurement | Paired same-pool top-three baseline/treatment, candidate recall, binary ranking metrics and labelled support-atom checks |
| Learning material | Main and beginner narratives, eight-hour routes, six runnable Python blocks, interview/recall, seven/six exercises and readiness/handoff |

The milestone is explicitly a local, in-memory CLI with cited source excerpts.
No free-form generator, authenticated HTTP interface, persistent ingestion or
production hosting was added to the existing document service. This bounded
scope avoids unmeasured model/cost/deployment claims. Earlier-week implementation
and curriculum source remain unchanged. The only shared UI change adds Week 8
to `PUBLISHED_WEEKS`.

## Source continuity and data boundaries

`corpus.jsonl` materializes the existing P-101–105 documents, P-106 review-only
OCR fixture, separate P-107/108 catalogues and a denied private distractor. Nine
records yield eight accepted documents and twelve chunks before authorization;
the analyst sees seven documents and eleven chunks. Existing accepted text,
version, structure chunk IDs, source digests and locations match Week 7.
P-106's `USD 12.O0` remains `needs_review` and unindexed.

The JSONL boundary enforces 128 KiB, 1–32 records, strict fields, UTF-8 and
bounded text/locations/blocks. Duplicate JSON keys fail. Repeated identical source
versions are idempotent; conflicts fail the batch. Parser review/reject outcomes
remain issues rather than being silently indexed. Supplier/type labels are input
assertions with a separate metadata-policy identity; source-version grants are
independent and do not derive from those labels.

## Implementation checks and limits

- Reranking receives exactly the bounded candidate pool and original question.
  Wrong output count, nonfinite/bool scores and observable model identity drift
  fail; ties use retrieval rank and stable chunk ID.
- Authorization precedes corpus statistics and both retrieval paths. Denied
  content cannot change the visible result or request manifest in the tested
  snapshot. Context admission and final citation validation recheck access.
- Deduplication removes only same-source/version/digest exact text. It does not
  delete complementary clauses or pretend to solve semantic duplicates or active
  source-version authority.
- Whole chunks are default. Optional query-overlap sentence compression preserves
  exact spans but can discard conditions; tests deliberately demonstrate that a
  valid quote can lose an exception. Table rows remain atomic.
- The entire serialized context is counted, including headers and escaping.
  Character counts are not represented as model-token enforcement. Empty
  candidates and candidates that cannot fit are different statuses.
- Citation labels, stored chunk equality, authorization, exact integer bounds
  and stored slices are checked. These establish exact-source validity, not
  entailment, source authority, completeness or business correctness.
- Fingerprints bind eligible corpus/partition, ordered query digests, retrieval
  identities, reranker, budgets and policy versions. They require trusted
  manifests and are not signatures.
- Library events use module logging without global handlers. The CLI allowlists
  request IDs/counts/status/fingerprint and excludes raw question/source text.
- The optional scalar raw-pair adapter targets reviewed materialized local files,
  no remote code/downloads/credentials, CPU, explicit reviewed joint token limit,
  empty role prompts, artifact/runtime identity and scalar finite outputs.
  Joint tokenization disables truncation and fails overlength pairs. Multiclass
  and instruction-specific models need a matching contract instead.

## Executed practice comparison

Fourteen visible Week 7 questions: ten labelled and four no-gold probes. Labels
resolve uniquely inside the eligible source snapshot and required atoms must
exist in the declared source/version. Candidate Recall@6 mean is 1.0. Both
orderings share candidate membership, request scope, labels and k=3.

| Labelled mean | Hybrid | Teaching reranker |
| --- | ---: | ---: |
| Precision@3 | 0.400000 | 0.433333 |
| Recall@3 | 0.966667 | 1.000000 |
| MRR@3 | 0.900000 | 0.950000 |
| Binary nDCG@3 | 0.916165 | 0.963093 |

Q09 changes P-105 block order 2/9/6 to 8/9/6, exposing Net 30 after inspection
approval while preserving the cross-reference and quantity row. The three-span
filtered context is 707 serialized characters. Default complete support fraction
is 1.0, sentence compression gives 0.9, and a 300-character whole-chunk budget
gives 0.7. All four no-gold probes return empty under the narrow default scorers.
No-gold recall/rank/nDCG remain null and outside labelled means.

These are constructed visible synthetic practice results, with handwritten dense
features and pair rules. No held-out learned-model quality, real model inference,
generated-answer faithfulness, latency, memory or positional effects were
measured. No model weights were installed/loaded and no hosted model call was
made. Optional integration is fake-backend tested, not real-weight validated.

## Validation actually executed

Environment: Linux, Python 3.12.14, pytest 9.1.1, Ruff 0.15.22, mypy 2.3.0.
The restored Ruff native executable segfaulted initially; reinstalling the same
pinned version restored it. No requirement pins or project tooling were changed.

| Check | Observed result |
| --- | --- |
| Week 8 tests | 57 passed |
| `python -m pytest tests --ignore=tests/test_llm_comparison.py -q -rs --basetemp=.runtime/pytest-week08-final` | 294 passed, 1 skipped |
| `python -m ruff check document_service llm_comparison labs tests` | Passed |
| `python -m ruff format --check document_service llm_comparison labs tests` | 48 files formatted |
| `python -m mypy --strict --explicit-package-bases labs/week_08 tests/test_week08_assistant.py` | Passed, seven files |
| Main/beginner displayed Python | All six complete blocks executed, three per lesson |
| Default demo and full/summary comparison | Executed; sample and published metric tables agree |
| Compression and tight-budget comparisons | Executed; 0.9/0.7 support fractions confirmed |
| Markdown plus Liquid structural previews | Main: 19 sections, 8 code blocks, 8 tables; beginner: 17 sections, 7 code blocks, 2 tables |
| Layout/metadata checks | One H1, no duplicate IDs/unresolved templates, valid fences, internal assets and alternate lesson links |
| README schema example | JSON parsed successfully |

The unrestricted `pytest tests` command was attempted and still fails at
collection because existing `llm_comparison/storage.py` imports Windows-only
`msvcrt`. Full strict typing of `document_service llm_comparison labs` reports
four pre-existing `msvcrt` locking/constant attribute errors in that file. No
unrelated source/tests were changed to bypass them. The compatible suite excludes
that one module explicitly. The skipped local-server smoke test requires
`LLM_COMPARISON_INTEGRATION=1`; no server was started.

Structural previews use Python Markdown and Liquid, not local Ruby/Jekyll or a
visual browser review. The hosted Pages workflow must be checked after the push;
its final status is reported in the task handoff. Local QA candidates/previews
are not published.

## Primary evidence

Opened the Sentence-BERT paper, official Sentence Transformers retrieve/rerank
guide and CrossEncoder API, the Lost in the Middle paper and Python logging API.
Fetched the exact Sentence Transformers v6.1.0 CrossEncoder source through GitHub;
verified scalar `num_labels`, current `max_seq_length`, constructor limits and
prediction prompt/output options. Public references link those primary sources.
The original paper's position effects are described in their tested scope,
without extrapolating a universal result to current models.

Remaining work belongs to later evaluated extensions: actual reviewed models,
held-out task quality, generated-claim support, active-version authority,
persistence, production authentication/retention/operations and deployment
hardening. The local milestone does not imply those have been completed.
