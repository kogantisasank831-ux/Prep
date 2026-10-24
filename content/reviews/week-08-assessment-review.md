---
week: 8
status: reviewed
version: 1.0.0
last_reviewed: 2026-10-24
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested Week 8 within the established explicitly approved build-check-push-publish workflow
---

# Week 8 assessment review

## Baseline and inspected scope

Base main: `42d26cafc72f49c3916b4a6b5f9cb54def331581`; tree
`9527f5be6549fdd1aba29bcf2dfa038bcf3db3ac`. The assessment branch starts
from freshly fetched origin/main. Root AGENTS.md is the only applicable
instruction file. No Design directory applies to this curriculum. Existing
untracked Week 5–7 QA work is preserved; no subagents were used.

Inspected Path.md's Week 8 requirements, the content workflow, both complete
Week 8 lessons and content review, the assistant lab README, pipeline, loader,
optional local adapter, CLI, comparison and all assistant tests. Inspected the
existing assessment page/bank/test conventions, shared bank validator and paper
verification script, navigation, dependency pins and candidate CI workflow.

Scope is one new practice bank/page/test/review, additive lesson links,
navigation/README integration and extending the existing candidate test gate.
Retrieval/assistant implementations, earlier banks, scoring/runtime code,
stylesheets, dependency pins and Jekyll configuration remain unchanged.

## Content and accepted contracts

There are 100 authored items: 30 single-choice, 20 multiple-correct, 15 matching,
15 short syntax and 20 Python tasks. All IDs/prompts are unique; every item has
a topic, difficulty, answer key and explanation. Coding prompts contain their
own required contracts because the related question may not appear in a random
paper. No independent human item validation or psychometric calibration is claimed.

| Learning requirement | Assessment evidence |
| --- | --- |
| Candidate coverage and same-pool comparison | Missing-clause diagnosis, 2/3 ceiling, exact pool permutation, requested precision denominator and no-gold null recalls |
| Bi-encoder versus cross-encoder | Separate reusable representations, query-dependent pair interaction, model-dependent scores and joint length |
| Reranker boundary | Original-question pairs, bounded batch, aligned finite scalars, no boolean scores, stable ties and observable identity drift |
| Query rewriting and multiple queries | Original retained, two raw reviewed variants, digit/condition token guard, exact stable dedup, lexical limits, second RRF and additional work |
| Deduplication | Tenant/document/version/digest/exact-text key, highest-ranked copy retained, complementary clauses and different versions preserved |
| Compression and selection | Narrow punctuation spans, unique-token overlap, original source order, atomic table rows and demonstrated qualifier loss |
| Context budget | Full compact JSON including headers/escaping, source units versus spans, whole-unit admission, skipped large units and distinct availability statuses |
| Citations and support | Full stored record equality, independent grants, unique labels, integer offsets, exact quotes, own-source atoms and validity/support/correctness distinctions |
| Assistant milestone | Idempotent source versions, label conflicts, strict bounded JSON, review outcomes, safe event projection and complete request identity |
| Measurement limits | Teaching rules versus actual learned models, held-out/cost needs, controlled positional protocol and no unexecuted generator claims |

Every Python task has a signature, declared input/error/mutation behavior and
five public checks. References use only re, math, json and hashlib. Tasks require
no downloaded model, API key, GPU, generator or inference service. The full
typed assistant lab remains a separate exercise.

Some helpers deliberately expose smaller teaching interfaces. unique_records
uses a five-field in-memory record, not the full parsed-block loader schema.
decode_unique_json checks syntax, byte size and ambiguity, not that document
schema. joint_pair_ids accepts already joint token-ID rows rather than invoking
a tokenizer. safe_event projects opaque metadata; validation of the other
event fields belongs upstream. pack_units consumes already-authorized span
groups; validate_citations separately rechecks grants and full stored equality.

The support exercise requires each atom wholly within a selected quote under
its own source key; it does not manufacture a match across joined spans. This
is an explicit bounded exercise contract, not a rewrite of lab evaluation.
The manifest exercise declares its compact canonical JSON bytes explicitly;
it teaches identity binding without claiming bit identity with every lab hash.
The status helper declares its four-spans-per-candidate count boundary.

## Correctness review and preserved integration

Applied the ds-code-review main instructions to the bounded change and traced
scores, candidates, authority, source identity, context admission and failure
paths. The skill provider could not supply its linked companion checklist;
the direct instructions and inspected repository contracts governed the review.
No outstanding actionable correctness/regression finding is supported after
the checks below. This is not a security audit or production readiness review.

Challenged each task with a distinct plausible wrong solution. Composed checks
cover protected constraints/candidate ceilings, complementary deduplication,
valid quotes with lost exceptions, permission revocation, whole-unit JSON
budgets, source-bound support and policy/query identity changes. Independent
oracles include literal canonical JSON/digest bytes, the 98-character source
envelope and known 2/3/1/3 ranking fractions. Draft check-string escaping and
an incorrectly counted envelope were corrected before acceptance.

The shared engine still selects two of each format, with ten distinct questions
and reproducible seed/version links. Each question is worth ten marks;
matching gives 2.5 per pair, coding gives two per passed check and other formats
require their complete key. Saved attempts, locked submissions, explanations,
reference solutions, blank print and result downloads are retained.

All original lesson characters remain after removing the single added link
paragraph from each lesson. Only Week 8 is added to ASSESSMENT_WEEKS; the
existing published-lesson set remains unchanged.

## Executed validation

Local environment: Python 3.12.14, Node 24.22.1, pytest 9.1.1, Ruff 0.15.22,
mypy 2.3.0 and Chromium 153.0.8010.0. Actual worker runs report Python 3.13.2.

- 597 targeted pytest tests pass: all eight assessment suites, Week 7 hybrid
  and Week 8 assistant regressions, and Week 1 API/model/reader/service tests.
  The new assessment contributes 63 tests. This is not an unrestricted
  whole-repository pass; the unrelated Windows-only comparison module is outside it.
- Every coding reference passes all five checks; every starter scores zero,
  and every plausible incorrect implementation loses marks.
- The shared JavaScript verifier checks 1,000 balanced reproducible papers,
  reachability of all 100 items, objective keys, partial/pending marks,
  submitted/restored attempts and stale-code rejection.
- All twenty references pass the actual browser worker (100 checks). A full
  paper scores 100/100, downloads its result, locks source and restores on reload.
- Blocked runtime leaves 80/80 graded and 20 pending; retries recover through
  90/90 to 100/100. Stop, the execution deadline and replacement source pass.
- Blank print has ten questions and no keys. Paper links reproduce the same
  selection; dashboard navigation exposes eight assessment links.
- All eight assessment pages pass 390px light/dark overflow checks, plus all
  100 Week 8 prompt texts. Desktop and stable mobile screenshots are inspected.
  QA screenshots disable transient resize animations; no product CSS changed.
- Completed browser checks have no page errors or unexpected failed requests.
- Ruff/format, strict mypy, JS syntax and whitespace checks pass. AST checks
  compile authored Python, verify only the four declared imports, bounded
  reference length and no authored file reads, input, eval/exec or dynamic imports.
- Source comparison proves complete lesson preservation. Workflow shape,
  read-only permissions and pinned action identities are checked.

The candidate workflow retains all previous checks and adds the new test's
Ruff/typing checks plus Week 8 assistant regressions. The exact proposed commit
must pass its remote pytest job on the assessment branch before main promotion.
Pages deployment and exact live assets/browser scoring are checked afterward.
This document records local evidence; it does not substitute for remote CI or
claim a remote result before that run completes. No branch-protection policy is
changed and no ability to prevent administrative bypass is claimed.

Local browser preview uses the existing layout with QA Markdown/Liquid
rendering, not Ruby/Jekyll. The runtime relay retrieves original HTTPS assets
with TLS verification and normal browser security. Production URLs are unchanged.
Workers run without cross-origin isolation or SharedArrayBuffer.

## Primary references and limits

Primary sources opened on 2026-10-24:

- [Sentence Transformers retrieve/rerank guide](https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html)
- [CrossEncoder input, output and activation API](https://sbert.net/docs/package_reference/cross_encoder/model.html)
- [Lost in the Middle, original positional study](https://arxiv.org/abs/2307.03172)

The bank does not infer source truth from a relevance scalar or a valid quote.
Teaching results cannot establish learned-model effectiveness, generator
faithfulness, production latency/memory or positional robustness. Source-version
authority and commercial actions remain outside these helpers.

The reused pinned Pyodide worker enforces its existing load/execution deadlines,
Stop and pending-result handling. Time termination does not impose a memory cap.
Google Colab remains an optional copy/paste workspace with sign-in and no result
sync. Public keys and editable client scores are practice records, not authenticated
exam results. Five checks supply bounded feedback, not proof for every solution.
No backend, central learner store, model downloads or new dependency is added.
Rollback is a normal feature revert; later bank edits must increment its version.
