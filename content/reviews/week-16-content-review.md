# Week 16 content and lab review

## Scope and disposition

Roadmap source: `Path.md`, Week 16 — Memory and context engineering.

Candidate artifacts:

- `content/weeks/week-16.md`
- `content/weeks/week-16-beginner.md`
- `labs/week_16/`
- `tests/test_week16_memory.py`

Version 1.0.0 is approved for the static learning site after local review. It
adds lesson content and a runnable local memory lab. It does not publish a Week 16
assessment; `ASSESSMENT_WEEKS` therefore remains at Week 15 and neither lesson
links to a nonexistent questionnaire.

## Coverage mapping

| Roadmap requirement | Learner-facing treatment | Executable evidence |
| --- | --- | --- |
| Conversation state | Current question is transient selection input | Marker question absent from SQLite bytes |
| Working memory | Bounded semantic anchor plus relevant episodes | Character-count contract and complete-entry packing |
| Long-term memory | Separate SQLite cross-thread case store | New store instance and cross-process CLI recall |
| Semantic memory | One current typed snapshot of five required facts | Persisted row assertions and deterministic summary |
| Episodic memory | Compact ordered fact and status-transition events | Five initial events plus one approval event |
| Summarisation | Stable application rendering from structured fields | Deterministic digest/summary tests |
| Context selection | Scope/expiry filter, word-overlap rank and hard budget | Relevant order, provenance and maximum-size assertions |
| Memory expiry | UTC deadline, hidden recall and cascade purge | Invalid time, post-expiry and deletion tests |
| Privacy | Data minimisation, trusted scope, explicit forgetting | Schema/byte checks, tenant isolation and forget tests |
| Incorrect-memory prevention | provenance, closed schemas, replay, revisions, immutable facts and one-way status | strict validation, stale write, mutation and terminal-state tests |
| Objective | Retained as a bounded semantic field and episode | Restart persistence and context assertions |
| Selected supplier | Retained as immutable structured identity | `SUP-115` persistence and changed-supplier rejection |
| Retrieved evidence | Document/SQL references, digests and observation times | Required categories and no evidence bodies |
| Calculations | Exact displayed value, unit, currency, date and rounding | `10.00` persistence and typed calculation validation |
| Approval status | Current semantic status plus transition episode | awaiting-to-approved revision and no terminal rewrite |
| Do not store raw conversation indefinitely | Raw messages are outside every accepted schema and table | extra-field rejection, column inspection and transient marker test |

## Technical review

The lab deliberately separates the Week 15 graph checkpointer from Week 16
cross-thread memory. SQLite is schema-versioned, created without overwrite and
uses tenant/case primary keys, bound values, explicit transactions and cascading
episode cleanup. A local `0600` file demonstrates a storage safeguard without
claiming encryption.

Every boundary model is strict and closed. Evidence stores identity and SHA-256
digests rather than bodies. Exact replays are idempotent, while real changes use
compare-and-set revisions. The narrow update operation locks all investigation
facts and permits one approval transition from waiting to a terminal status.

Context selection is deterministic so tests can establish relevance and size.
The semantic anchor, provenance, revision and expiry are mandatory; optional
episodes are ranked and added whole. Recalled content is labelled as data that
requires verification. Keyword overlap is presented as a transparent baseline,
not semantic-search quality.

`AccessScope` is correctly described as an input from a trusted host rather than
authentication. Report/content digests are described as change detectors rather
than truth, authorization or digital signatures. Production identity, encryption,
backup, migration, distributed concurrency, legal hold and deletion evidence are
explicit exclusions.

## Resolved findings

1. The first SQLite insert supplied 17 placeholders for a 16-column table. The
   insert now names all columns and supplies exactly 16 bound values.
2. The relevance test originally expected supplier or approval first, but the
   objective legitimately matched both “price” and “variance.” The test now
   asserts the deterministic objective-first order followed by approval and
   supplier.
3. The repository’s local `.venv/bin/python` is a broken symbolic-link loop in
   this workspace. Validation uses a clean temporary environment installed only
   from `requirements-dev.txt`; no project dependency changed.
4. The default mypy cache database in this workspace was malformed. Strict mypy
   succeeds with a clean isolated cache, which is also how a fresh CI runner
   behaves.

## Source review

The lessons use primary documentation accessed on 2026-11-03:

- official LangChain long-term-memory documentation for cross-thread stores,
  namespaced JSON records and the development-only in-memory example;
- official context-engineering documentation for runtime context, short-term
  state, long-term stores and selecting the right information;
- official LangGraph persistence/store documentation for the checkpointer versus
  cross-thread-store boundary and lifecycle concerns; and
- Python standard-library `sqlite3` documentation for connections, transactions
  and parameter substitution.

Those sources support adjacent software claims only. The procurement identities,
prices, decisions and dates are fictional and do not imply production readiness.

## Executed local checks

Local environment: Python 3.12.14. The declared CI environment is Python 3.13.12.

- The 16 focused Week 16 behavior tests pass.
- Ruff lint passes for all 55 files in the configured CI scope, and Ruff format
  reports all 55 files already formatted.
- Strict mypy passes for all 55 configured files with a clean isolated cache.
- The configured regression suite passes: 1,472 tests, including 64 Week 15
  assessment cases, 13 Week 15 graph cases and 16 Week 16 memory cases.
- Week 13 actual-SQLite smoke passes all 12 observations.
- Week 14 controller smoke passes all eight observations.
- Week 15 graph smoke passes all ten observations.
- Week 16 memory/context smoke passes all 12 observations.
- Front matter, reciprocal lesson links, code-fence balance, YAML parsing,
  JavaScript syntax, UTF-8 reads, whitespace, CI wiring, Week 16 navigation and
  absence of a premature Week 16 assessment link pass locally.

## Publication verification

Pending candidate CI, main promotion, GitHub Pages deployment and live-route
verification.
