---
week: 10
status: reviewed
version: 1.0.0
last_reviewed: 2026-10-25
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested Week 10 questions within the established approved build-check-push-publish workflow
---

# Week 10 assessment review

## Baseline and accepted scope

Base main: `e21381e3b607e00e330496f5e26efb63dcd3049c`; tree
`01980bf959533a483c939b185f12bf983eaf7325`. Only root AGENTS.md applies.
There is no Design directory for this curriculum. Actual scope comes from
Path.md Week 10, the published main/beginner lessons, local tracing lab and the
user's established weekly 100-question/random-10 assessment requirement.
Existing untracked QA work is preserved. No subagents were used.

Inspected the existing bank schema, shared scorer/verifier, Python runner,
Week 9 test/browser conventions, Week 10 lessons/lab contracts, dependency pins,
navigation and CI. Applicable production-coding and code-review skill workflows
retain the exact-candidate pytest CI gate and post-Pages live checks.

Scope is a new bank/page/test/review, lesson assessment links, README/navigation
and adding the new test module to existing lint/type gates. Shared engine,
workers, dependencies, styles, previous banks, Week 10 lab and its source data
are unchanged. The lesson versions advance to 1.0.1 for the additive link and
replacement of the two old assessment-next-step sentences. Other lesson body
characters are verified against the base revision.

## Item coverage and teaching contracts

The bank contains 100 unique authored prompts: 30 single-choice, 20
multiple-correct, 15 matching, 15 short syntax and 20 Python tasks. Each includes
topic, difficulty, key and explanatory feedback. Every coding task states its
own contract and five public executable checks; no preceding question or local
repository import is required by a random paper.

| Learning goal | Assessment coverage |
| --- | --- |
| Request/span relationships | Nonzero hex identities, parent resolution, duplicate/orphan/cycle rejection, root identification and completion-order interpretation |
| Stage traces | Query preservation, original-question reranking, eligible snapshot, ordered candidates, selected source units and first meaningful stage difference |
| Latency | Monotonic versus UTC, integer units, inclusive parent intervals, overlap unions, null timing and matched request populations |
| Usage and cost | Exact integer counts, bool rejection, unknown versus known zero, synthetic provenance, cached subset, Decimal per-million arithmetic and missing-rate reasons |
| Failures | Ordered exception categories, original exception/cancellation propagation, finally cleanup, unchanged falsey results and a single export attempt |
| Prompt/model versions | Complete canonical manifest identity, ordered explicit messages, UTF-8/size validation and mutable-alias/reproduction limitations |
| Payload handling | Explicit allowlist projection, trusted upstream source-scope decisions, synthetic opt-in, deep-copy independence and no anonymity/DLP inference |
| Operational limits | Bounded storage, visible omissions, span versus request counts, application/recorder/delivery/quality distinctions, cardinality and sampling bias |
| Framework translation | Custom JSON versus OTLP, task-aware propagation/lifecycle and correlation independent of authentication |

Small functions deliberately declare their boundaries rather than silently
replacing the production lesson interfaces. trace_root uses arbitrary bounded
IDs while valid_ids separately checks hex form. Timeline, source-unit selection,
stage comparison and summary receive trusted upstream-normalized observations.
The synthetic capture's authorized bool is a trusted fixture input, never a
client-controlled permission mechanism. Metadata projection bounds scalar shape
and omits unknown keys; it is not a content-sensitive PII detector.

Token-cost inputs have an explicit trusted rate/count contract and use invented
rates, not current prices. Estimated/unreported/inapplicable sources do not
become billable observations. Retry totals retain independent input/output
completeness and reject duplicate attempt identities. Root intervals are not
summed with descendants; exclusive time subtracts a union. Paired comparisons
reject changed request populations and retain missing, zero and negative deltas.

No model/provider call, tokenizer, inference benchmark, real payload collection,
paid service or automatic semantic answer judge is introduced.

## Review and local evidence

Reviewed the bounded diff against the above contracts, checking subtype ordering,
cached-token arithmetic, Decimal precision, missingness, parent-chain traversal,
list ordering, complete version input coverage, source scope, copy/mutation
boundaries, cancellation and application/export isolation. No unresolved
actionable correctness finding is supported after verification. This is a
technical item review, not independent human validation or psychometric
calibration.

Executed with local Python 3.12.14, Node 24.22.1 and the repository's pinned
pytest/Ruff/mypy. Chromium is 153.0.8010.0; browser Python reports 3.13.2.

- **861 targeted pytest tests pass**, including 64 new assessment cases, all
  ten assessment suites, Week 7–10 lab gates and the Week 1 service regressions.
- All 20 references pass all five checks; all starters score zero; every one of
  20 distinct plausible incorrect implementations loses marks.
- Composed checks independently exercise parent validation and interval unions,
  known 0.0041 cached-cost arithmetic, incomplete retry totals, context-first
  divergence, full configuration identities, source-version scope, one
  application call plus a separate failed export, and paired latency direction.
- Shared JavaScript verification passes 1,000 balanced reproducible papers,
  all-item reachability, objective keys, partial/pending scoring, saved attempts
  and stale source/result rejection.
- All 20 references pass real browser Python: **100 executed public checks**.
  A completed paper scores 100/100, locks answers, downloads and restores after
  reload. A blocked runtime retains 80 graded marks plus 20 pending; retries
  recover through 90/90 to 100/100. Stop/timeout/replacement-code recovery passes.
- Blank print has ten questions without answer keys. Share/new-paper
  reproduction, active Week 10 navigation and ten dashboard assessment links
  pass. No browser page errors or unexpected failed requests.
- All ten assessment pages fit 390px in light/dark, as do all 100 new prompt
  texts. Desktop and stable mobile screenshots were inspected.
- Ruff check/format and strict mypy pass on the four Week 7–10 assessment test
  modules, five Week 10 lab sources and tracing test (ten Python files).
- Python reference/check compilation, source-size/import bounds, JavaScript
  syntax, whitespace and exact lesson-body preservation checks pass.

The selected test suite excludes the existing unrelated Windows-only comparison
module. This is not an unrestricted whole-repository pass. Five public checks
provide bounded practice feedback, not a proof of arbitrary solution correctness.

## Release gate and practical limits

The existing read-only CI workflow includes the new assessment through its test
glob and adds its lint/type gates without weakening existing checks. Candidate
pytest CI on declared Python 3.13.12 must pass before main promotion. Exact live
bank/shared-asset bytes, Pages success and a live scored/restored paper are
checked afterward; immutable commit/run identities are retained in publication
QA evidence. No remote success is claimed in advance by this review record.

The static scorer keeps ten distinct questions, two per format and 100 marks.
Matching awards 2.5 per pair; coding awards two per passed check. Public bank
keys and editable client-side results remain practice records rather than
authenticated exams. The existing pinned Pyodide worker retains execution/load
deadlines and Stop; termination does not impose a memory cap. Optional Colab
remains copy/paste with sign-in and no automatic result synchronization.

Local previews use the existing layout with QA Markdown/Liquid; deployed Pages
uses Jekyll. The browser-runtime relay retains original HTTPS assets and normal
TLS/browser security, without changing deployed URLs. Workers operate without
cross-origin isolation or SharedArrayBuffer. No hosting/security contract changes.

Conceptual sources are the primary references already checked for the published
Week 10 lessons: OpenTelemetry trace/propagation/sampling/sensitive-data guidance
and Python time/decimal documentation. Custom statuses, counters, algorithms and
teaching rates follow the explicit repository/exercise contracts; they are not
claimed to be standard OTel wire attributes or provider billing rules.

Future bank revisions require a version bump to avoid restoring stale attempts.
Rollback is a normal feature revert and Pages rebuild; there is no migration or
external service dependency.
