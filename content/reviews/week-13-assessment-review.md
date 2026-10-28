---
week: 13
status: reviewed
version: 1.0.0
last_reviewed: 2026-10-28
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested the Week 13 question piece within the established test-push-publish workflow
---

# Week 13 assessment review

## Baseline and scope

Base main is 3ab05b1922fd3f1186d2d2fe38b008528ba7b895; its tree is
9434cff8710ea9eb4600b635c2d9ada18cc4c021. Only root AGENTS.md applies.
Its Finance App references do not describe this curriculum, and there is no
Design directory. Path.md Week 13, plan.md, the approved main/beginner lessons,
labs/week_13/LOGIC.md revision 1 and the user's weekly assessment requirements
define this addition. Earlier untracked QA work is preserved. No subagents
were used.

Inspected the preceding bank/page/tests/review, shared paper/scoring verifier,
Python runner and worker, Week 13 contracts, dispatch, ledger, demo and tool
tests, lesson text, layout, navigation, README, dependency pins and workflow.
The staged candidate was checked before canonical integration.

Added the bank, assessment page, regression module and this review. Existing
changes are limited to navigation, README, the new module's lint/type targets
and assessment links in the two Week 13 lessons. Their patch versions become
1.0.1 and review dates become 2026-10-28. Reversing those declared edits
reproduces the original lesson files exactly. All 256 other previously tracked
files are byte-identical to the base, including earlier banks/lessons, labs,
dependencies and shared assessment assets.

## Coverage

There are 100 distinct authored prompts: 30 single-choice, 20 multiple-correct,
15 matching, 15 short syntax and 20 Python coding questions. Every item has a
topic, difficulty, answer key and explanatory feedback. Each coding task
specifies its local inputs, outputs, failure behavior and five public checks;
it can be solved independently of the other questions drawn in a paper.

| Learning goal | Assessment evidence |
| --- | --- |
| Function/tool boundary | Narrow capability, definitions and JSON Schema, fixed dispatch, provider adaptation, selection versus argument meaning |
| Strict proposals | Exact scalar types, closed fields, duplicate JSON, named queries, cross-field IDs and price comparability |
| Trusted caller | Application-injected scope, catalogue visibility versus execution authority, current grants and scope before limiting rows |
| Five read tools | Scoped SQL, exact price variance, supplier lookup, dated fictional commodity data and guarded document search |
| Result handling | Closed envelopes, exact correlation, serialization bounds, safe error categories, untrusted prose and successful-call evidence |
| Loop and retries | Distinct turn/call/attempt budgets, correction versus retry, transient reads, permanent defects, cancellation and cooperative deadlines |
| Optional write | Exact approval, scope/arguments/version binding, stable intent keys, replay/conflict, current authority and uncertain outcomes |
| Retained ledger | Atomic local SQLite protection, concurrent writers, lost-response recovery, deletion and external-effect limits |
| Syntax | async/await, Pydantic validation/schema methods, closed models, Decimal context/quantize, SQL binding/transactions, Literal inspection and SHA-256 |

## Coding contracts and limits

The exercises use only re, hashlib, json, copy, decimal and asyncio. They need
no provider, database, server, threads, paid service or repository imports in
the browser. Async checks use the existing runner's top-level-await support.

Canonical price parsing rejects floats, signs, leading zeros, exponent forms
and non-ASCII digits. Variance uses already normalized canonical prices,
matching declared currency/unit, a positive baseline, local precision 28 and
explicit two-place half-even rounding, including negative zero. Independent
expected examples cover baseline-denominator percentages, ties, extreme values
and preservation of the caller's decimal context. Arithmetic does not verify
that the proposed prices came from the intended business record.

Schema visibility and row-projection helpers receive trusted application
definitions/caller scope; they do not authenticate the caller. Result correlation
receives fields whose other values have already passed a separate DTO contract.
Final evidence checks membership in successful calls, not summary entailment or
source truth. Transcript accounting measures the complete specified UTF-8 JSON
representation, not model tokens or process memory.

The intent digest uses the lab's exact create_review/1 canonical representation
and binds tenant, principal, application key and normalized arguments. The
approval helper checks exact digest and strict expiry under a trusted approval
origin; current grants remain separate. Replay lookup checks current grant and
approval before consulting retained results, and returns an independent copy.

The ledger decision and store-once tasks explicitly model single-threaded
in-memory components. They do not claim transaction, concurrency or external
rollback guarantees. Their checks cover full scoped identity, changed-argument
conflicts, independent copies and insertion only after a successful callback.
The real SQLite transaction and concurrent-writer behavior remain in the
separately runnable lab and its existing tests.

Retry classification distinguishes read transients from known pre-effect write
rejections and unknown write effects. The async retry exercise is explicitly
READ-only, bounded to two attempts with an injected delay, and propagates
permanent failure, cancellation and delay failure unchanged. Validation precedes
execution and result projection follows it. A real brief cooperative timeout
checks cancellation cleanup; neither that timer nor caller cancellation proves
that a write rolled back or preempts synchronous blocking code.

## Executed local verification

Used local Python 3.12.14, Node 24.22.1 and the repository's pinned tools.
Reinstalled the same pinned Ruff 0.15.22 to repair a local executable crash;
no dependency declaration or version changed.

- 1,303 targeted pytest cases pass, including all thirteen assessment suites,
  64 new assessment cases, existing Week 7–13 lab/application cases and Week 1
  service regressions.
- All 20 reference implementations pass five checks; all 20 starters score
  zero; each of 20 distinct plausible wrong implementations loses marks.
- Five composed checks cover closed capabilities/scoped rows, exact arithmetic
  and correlated evidence, scoped intent/approval/conflict, current replay
  authority/copy ownership and ordered validation/retry/deadline/projection.
- The shared JavaScript verifier exercises 1,000 balanced reproducible papers,
  reaches every item, checks all objective keys, complete-set and partial
  scoring, pending coding marks, stale-code rejection and restored attempts.
- Ruff lint and formatting pass for the configured 34 files; strict mypy passes
  the same 34 files. Dependency consistency, shell.js syntax and git whitespace
  checks pass.
- The runnable CLI smoke passes 12 observations over actual SQLite and guarded
  search, with no external actions.
- Liquid/Markdown rendering and local HTTP checks pass for both lessons, the
  assessment page and bank. The lessons retain 16 second-level headings each,
  5/2 tables and 7/6 code blocks. IDs are unique and both assessment links resolve.

Reviewed answer keys, matching pairs, syntax and coding contracts against the
approved lessons and actual implementation. No unresolved actionable technical
finding remains after these checks. This review is not an independent human
rubric score or psychometric calibration. Exact-candidate CI, actual
PostgreSQL/container HTTP/restart checks and deployed browser observations are
recorded separately in the publication verification evidence.

The established paper remains ten distinct questions, two of each format,
ten marks each. Multiple-correct requires the complete set; matching awards
2.5 per pair and coding two per check. Five checks provide bounded practice
feedback. Public keys and editable browser results are not authenticated exam
records. Runtime unavailability leaves coding marks pending, and optional
Colab use remains manual copy/paste. Shared worker deadlines, Stop, save/restore,
print/download and scoring rules are unchanged. GitHub Pages remains static.
