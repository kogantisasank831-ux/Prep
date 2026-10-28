---
week: 13
status: reviewed
version: 1.0.0
last_reviewed: 2026-10-26
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested Week 13 content within the established approved test-push-publish workflow
---

# Week 13 content review

## Baseline, scope and review process

Base main is 5d3f0a8984e36b1422a34f4f36f28ad777bcbf6a; tree is
acd83d0b82403474c22d5a234f982f779275bc4a. Only root AGENTS.md applies.
Its Finance App design references do not describe this curriculum and no Design
directory exists. Accepted scope comes from Path.md Week 13, plan.md, the
approved Week 11–12 contracts and the user's established weekly content-first,
then assessment, verification and publication workflow.

Applied the requirements, production-coding and bounded code-review workflows.
Read the applicable instructions, prior main/beginner structure, dependency
pins, guarded input/source/quote contracts, Week 12 logic/fixtures/CI, shared
layout, navigation and README. Recorded the scoped contract in
labs/week_13/LOGIC.md revision 1 before implementation, then reviewed the entire
new lab, tests, both candidate lessons and bounded integration diff. No subagents
were used. Existing QA directories and user work were preserved.

The new files are main/beginner lessons, the tool-calling lab, focused tests and
this review. Existing edits are only navigation, README and the new CI test/smoke
targets. All 247 other tracked files remain byte-identical to the base, including
earlier lesson bodies, question banks, shared scoring/workers/styles, previous
labs, source data, requirements and the Week 12 deployment configuration.
The unchanged container job and read-only workflow permissions were compared
structurally against the base.

Candidates were staged under publication QA before canonical integration.
Approved lessons are version 1.0.0 and each provide an eight-hour route. The
main narrative has 16 sections, five tables and seven code blocks; the beginner
route has 16 sections, two tables and six code blocks. They introduce one
operation/decision at a time, connect small examples with failure cases and
checkpoints, and introduce the loop after function/schema/result concepts.
Review/provenance stays here rather than in public lesson prose.

The existing user instruction authorizes direct generation and publication.
No independent owner rubric scores, separate human review or psychometric
calibration are fabricated. Week 13 questions remain a later task; assessments
stay published only through Week 12, while lessons advance through Week 13.

## Requirements, implementation and evidence

| Contract | Implementation | Verification |
| --- | --- | --- |
| W13-BR1 / FR1 | Fixed registry, five roadmap read tools and optional local review record; scripted planner | Actual five-tool loop and CLI scenarios; no provider/model-quality claim |
| W13-FR2 | Bounded strict JSON turns, closed Pydantic models, fixed dispatch, unique IDs | Duplicate/nonfinite/extra keys, bad types/values, unknown name, repeated call IDs, invalid final evidence |
| W13-FR3 / DR1 | Trusted Actor/SecurityContext, named bound SQL, current grant joins, reused guarded search | Two-tenant same-ID results, restricted/outsider negatives, read-only connection, independent SQL parameter case |
| W13-DR2 | Canonical decimal price strings, matching units/currencies, local Decimal context and half-even output | Independent positive/negative/zero/extreme examples and exact rounding ties; malformed/incomparable inputs rejected |
| W13-FR4 | Per-tool result models, calendar validation, UTF-8 byte bound, correlated tool messages | Action-shaped extra fields, type/length/date errors, multibyte overflow, permitted prose cannot authorize a subsequent write |
| W13-NFR1 | Sequential six-call/eight-turn defaults, finite representations, cooperative deadlines | Call/turn/transcript termination, invalid limits, actual cancellation cleanup and fixed attempt counts |
| W13-FR5 | At most two transient read attempts; no automatic write retry; unknown outcome stops loop | Controlled transient read, cooperative timeout, cancellation, post-commit lost response, malformed write result and overall deadline during write |
| W13-FR6 / DR3 | Host-owned operation key and exact expiring approval, BEGIN IMMEDIATE scoped intent ledger | Actual SQLite replay after reopening, conflicting arguments, copied/expired approval, current revoked grant, concurrent writers, manual recovery |
| W13-ENG1 / ER1 | Existing Python/Pydantic/tooling, bounded logs, focused CI/CLI targets | Ruff/mypy/native regressions, payload-free exception category and actual command-line storage smoke |

The review-record tool is a fictional local write, not order approval or an
external financial action. The CLI's approval object is an explicit trusted
fixture, not authenticated human consent or a signed token. Caller shape
validation does not authenticate identity. The SQLite file/application owner
and callback implementations are trusted; this is not hostile-plugin isolation.

The registry's document search uses the previous guarded in-memory source
catalogue, while purchase/supplier/commodity and intent data use actual SQLite.
The fixture SQL has two named queries over its open synthetic orders. SQLite
is separate from the unchanged Week 12 PostgreSQL service. Commodity values
are explicitly fictional and dated 2026-10-01; none are live quotes.

Price arithmetic checks declared values/units, not their business provenance.
The read script uses known fixture amounts instead of inferring a price-to-order
binding through a model. Result schemas and evidence-call membership do not
prove summary entailment, source truth, completeness or real-model quality.
Provider-native objects/schema subsets/continuation state need an unimplemented
adapter; the exported local catalogue is not claimed as a drop-in API request.

## Resolved technical findings

The bounded review traced proposed data through parsing, argument validation,
authority, SQL/Decimal/search handlers, output validation, retry classification,
transaction/duplicate state and final response.

- A valid question that exceeded a smaller configured transcript budget was
  initially classified as invalid input. Input validation and budget admission
  are now separate, with a regression asserting budget_exhausted.
- Search arguments now bound the compact forwarded question representation
  before invoking the guarded core, including an exact 4096-byte boundary and
  an escaped-control-character overflow. A character limit alone was insufficient.
- Controlled error categories are enforced at runtime, preventing an accidental
  free-form adapter error from becoming an output channel.
- Known schema-version mismatches are permanent result errors. Only SQLite
  busy/locked driver categories map to transient unavailability; unrelated
  driver failures do not receive blind read retries.
- Resource checks use explicit connection closing; Future/task cancellation
  remains original cancellation. Invalid output after an admitted write is an
  uncertain effect, not evidence that no record was inserted.

No unresolved actionable finding is supported within these declared local
contracts after verification. This is a bounded technical review, not a full
security audit, real-model benchmark or production-readiness sign-off.

## Executed local checks and release gate

Local environment: Python 3.12.14, Pydantic 2.13.4, SQLite 3.53.1, Node 24.22.1,
with repository-pinned pytest 9.1.1, Ruff 0.15.22 and mypy 2.3.0.

- Final targeted regression command: 1,239 tests pass, including 89 new
  tool/storage/protocol cases, all twelve assessment suites, Week 7–12 lab/
  application checks and Week 1 service regressions.
- Ruff lint/format and strict mypy pass on 33 scoped source files. Declared
  dependency consistency, JavaScript syntax and whitespace checks pass.
- Three complete Python and two JSON lesson examples execute/parse. Twelve CLI
  scenarios/definition observations use an owned temporary fixture, including
  expected exit code 2 on the first injected lost response and success on replay.
- The mandatory CLI smoke makes twelve observations over real SQLite, guarded
  retrieval and the scripted loop. It is also exercised by pytest and CI.
- Liquid/Markdown/shared-layout rendering and both local HTTP paths pass:
  code fences, tables, alternate links, unique IDs and publication metadata.
  There is no active embedded content or premature Week 13 assessment link.
- Byte comparison protects 247 existing files; the previous container job and
  read-only CI permissions are preserved.

The selected suite excludes the unrelated pre-existing Windows-only comparison
module; no unrestricted whole-repository pass is claimed. Actual SQLite tests
are local integration evidence; injected planner/adapter failures test control
semantics, not a remote service's behavior. Local Docker/PostgreSQL are absent,
so their existing mandatory real CI job remains required on the exact candidate,
including nine database tests and HTTP smoke around restart.

Candidate-matched Python 3.13.12 CI, the new actual CLI smoke, previous container
checks and subsequent Pages/live verification are required before completion.
Immutable candidate/tree/run identities and live evidence are retained in
publication QA; remote success is not asserted in advance in this record.

## Primary sources and remaining deployment decisions

Rechecked on 2026-10-26:

- [Function-calling protocol and result correlation](https://developers.openai.com/api/docs/guides/function-calling)
- [Pydantic strict mode](https://docs.pydantic.dev/latest/concepts/strict_mode/)
- [Python Decimal](https://docs.python.org/3.13/library/decimal.html)
- [Python SQLite binding, connections and transactions](https://docs.python.org/3.13/library/sqlite3.html)
- [SQLite transaction semantics](https://www.sqlite.org/lang_transaction.html)
- [Asyncio tasks, cancellation and timeouts](https://docs.python.org/3.13/library/asyncio-task.html)

Deadlines are cooperative; the tiny synchronous SQLite operations have a
separate bounded busy wait and cannot be preempted by an asyncio timer.
No hard wall-clock SLO, memory sandbox or distributed limit is promised.
Atomic review/idempotency scope is this retained SQLite ledger and its
cooperating writers. Deletion loses history; external effects require a
separate reconciliation/idempotency design.

Real provider/model evaluation, authenticated identity/approval, external
effects, production retention/recovery and operating ownership remain future
deployment decisions with unassigned owners. They do not block this synthetic
teaching lab. GitHub Pages serves static lessons; the Python build runs locally.
