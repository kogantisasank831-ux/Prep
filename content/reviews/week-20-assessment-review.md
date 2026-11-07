---
week: 20
status: reviewed
version: 1.0.0
last_reviewed: 2026-11-07
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested completion and publication of the Week 20 questionnaire within the established test-push-publish workflow
---

# Week 20 assessment review

## Baseline and scope

The published content baseline is main commit
`0371e5ffe756b09018c62ed6a69b2e7791a8f921`. Local source commit `5a9ea15`
has the equivalent reviewed Week 20 content tree. Only the root `AGENTS.md`
applies. Its Finance App references do not describe this curriculum, and there
is no `Design/` directory. `Path.md` Week 20, the approved production and
beginner lessons, `labs/week_20/LOGIC.md`, the deterministic reliability worker
and the established weekly assessment contract define this addition. No
subagents were used.

Inspected the Week 19 bank, page, tests and review; the shared assessment engine,
Python runner and browser worker; Week 20 models, retry executor, circuits,
fallback plans, queue, worker, scenarios and focused tests; navigation, README,
dependency pins and CI workflow. The assessment adds no dependency, provider,
model, hosted execution service, database, network call, secret or external
procurement action.

Added `assessments/week-20.json`, `assessments/week-20.html`,
`tests/test_week20_assessment.py` and this review. The same change exposes the
assessment in navigation and CI, links it twice from both lesson depths, updates
the lesson patch version to 1.0.1 and records the assessment contract as
W20-AS1 in `labs/week_20/LOGIC.md` revision 2.

## Coverage

The bank contains 100 distinct authored prompts: 30 single-choice, 20
multiple-correct, 15 matching, 15 short syntax and 20 Python coding questions.
Every item has a topic, foundation/applied difficulty, answer key and explanatory
feedback. Each coding task is independent, states accepted input and failure
behavior and has five executable checks.

| Learning goal | Assessment evidence |
| --- | --- |
| Failure taxonomy | unavailable, rate-limited and timeout outcomes versus contract-invalid, configuration and ambiguous-write failures |
| Retry safety | safe-operation gate, finite attempts, one retry layer and explicit non-replay of Week 19 approval-bound writes |
| Retry timing | capped exponential backoff, bounded `Retry-After`, production jitter rationale and caller-budget boundaries |
| Deadlines | late-result rejection, attempt versus total deadline and real cancellation/resource-cleanup limits |
| Circuit breakers | closed/open/half-open admission, exact threshold, recovery boundary, successful reset, failed-probe reopen and dependency isolation |
| Fallbacks | compatible model, cache and lexical contracts with `degraded/fallback_used`, selected dependency and reduction warnings |
| Idempotency | exact replay suppression, tenant/scenario conflict rejection and limits of process-local state |
| Queue processing | submit, lease, acknowledge, requeue and dead-letter transitions with separate dependency-attempt and delivery budgets |
| Partial failure | ordered per-item terminal results, independent continuation and explicit prerequisite caveat |
| Dead letters | minimal diagnostic projection, ownership, retention, repair, authorized redrive and replay-loop prevention |
| Observability | controlled attempt fields, low-cardinality outcome metrics and separate normal/degraded/failure objectives |
| Scenario evidence | model outage, database timeout, invalid supplier output, vector outage and catalog throttling outcomes |
| Production limits | no real cancellation, durable broker, distributed circuit state, concurrent probes, exactly-once effects or fallback quality proof |

## Coding contracts and limits

The browser exercises are self-contained and use no imports. They need no
Pydantic package, repository import, provider, model, server, network, database,
filesystem or credentials. The complete frozen boundary models, scripted
dependencies, circuits, queue and worker remain in the local Week 20 lab.

Inputs use exact built-in containers and primitive types where the question says
strict. Bool-as-int coercion, malformed counters, blank identifiers, duplicate
fields, unknown states and incomplete terminal coverage are rejected. Deadline
classification precedes data acceptance. Backoff and `Retry-After` have separate
caps. Retry eligibility combines failure class, operation safety, remaining
attempts and circuit state.

Circuit tasks assert the threshold and recovery boundaries rather than only
happy states. Fallback results copy data and expose degraded evidence. The queue
tasks reject idempotency conflicts, require a lease for acknowledgement and stop
redelivery at the exact delivery ceiling. Dead-letter records omit the
idempotency key and accept no arbitrary payload. Batch summaries derive counts
from explicit ordered terminal results.

These exercises are policy-scale functions, not a production retry SDK or
broker. The public bank exposes answer keys and runs learner code in a disposable
browser worker; its scores are practice feedback, not authenticated exam records.

## Executed local verification

Used Python 3.12.14, Node 24.22.1 and the repository's pinned tools in an
isolated ignored environment.

- The focused Week 20 assessment module passes 64 cases. All 20 references pass
  five checks; all 20 starters score zero; every one of 20 distinct plausible
  wrong implementations loses marks.
- The shared JavaScript verifier validates the 100-item bank, exercises 1,000
  balanced reproducible papers, reaches every item and checks objective,
  partial/pending, stale-code and restoration contracts.
- Five composed checks cover classification/retry timing, circuit recovery,
  output/fallback evidence, idempotent queue transitions and partial-batch/DLQ
  behavior.
- The assessment plus reliability worker pass 103 tests; the worker smoke passes
  16 checks over all five scenarios.
- The configured regression suite passes 1,905 tests, including all twenty
  assessment banks, the Week 7-20 labs and the Week 1 service regressions.
- Ruff lint and formatting pass for all 83 configured files. Strict mypy passes
  the same 83 files with an isolated cache.
- The Week 13 actual-SQLite smoke passes 12 observations with zero external
  actions. Week 14 passes eight checks, Week 15 ten, Week 16 twelve, Week 17 ten,
  Week 18 eight assertions over all 28 cases, Week 19 twelve checks over seven
  safety scenarios and Week 20 sixteen checks over five reliability scenarios.
- Static checks confirm 100 unique ordered IDs, exactly five checks per coding
  task, two lesson links at each depth, the page-to-bank path, front matter,
  fence balance, UTF-8 reads, navigation allowlist, JavaScript syntax, CI wiring
  and clean whitespace.

Each seeded paper draws two questions of every type for 100 marks.
Multiple-correct requires the complete set; matching awards 2.5 per pair; coding
awards two points per passed check. Runtime unavailability leaves coding marks
pending. Save/restore, print, result download and scoring behavior use the
unchanged shared engine.

## Publication verification

Completed 2026-11-07 for implementation commit
`a8cd0d91d99f37211a040308d277c9028ab18ef2`.

- Candidate CI run `42343532231` passed before promotion. Its Python 3.13.12
  job passed Ruff lint and format, strict mypy, all 1,905 tests and all eight
  configured CLI smokes. Its PostgreSQL/pgvector job also passed the real
  database permission, revocation and restart checks.
- Main CI run `42343729924` passed the same Python and real
  PostgreSQL/pgvector gates after lease-protected promotion from the reviewed
  baseline.
- Pages run `42343729768` completed successfully for the promoted commit.
- The live production and beginner lessons each expose two Week 20 assessment
  links and reciprocal depth navigation. The roadmap Week 20 card exposes one
  lesson link and one assessment link, while the sidebar exposes one Week 20
  lesson link.
- The live assessment reports 100 questions ready at version 1.0.0 and renders
  a 10-question paper with exactly two questions of each format. It exposes ten
  question jump links, two Python check controls, one submit-and-score control
  and a working link back to the production lesson.
- The production lesson, beginner lesson, roadmap and assessment produced no
  page-origin browser warnings or errors during verification.

GitHub Pages will host the static assessment and download the pinned browser
Python runtime only when a learner runs a coding solution. The complete
reliability worker remains local; no public Python service, model, provider,
database, broker, credential or procurement action is deployed.
