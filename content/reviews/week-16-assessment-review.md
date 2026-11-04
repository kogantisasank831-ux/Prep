---
week: 16
status: reviewed
version: 1.0.0
last_reviewed: 2026-11-04
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested completion and publication of the Week 16 questionnaire within the established test-push-publish workflow
---

# Week 16 assessment review

## Baseline and scope

The published implementation baseline is main commit
`180d158e1f797b650bc2de1d5a70c3eab58f1915`. Local source commit
`afa6bc04663f06db7dcf9f0fa39e5c3726db9ae3` has the same reviewed tree. Only
the root `AGENTS.md` applies. Its Finance App references do not describe this
curriculum, and there is no `Design/` directory. `Path.md` Week 16, the approved
production and beginner lessons, `labs/week_16/LOGIC.md`, the durable SQLite lab
and the established weekly assessment contract define this addition. No
subagents were used.

Inspected the Week 15 bank, page, tests and review; the shared assessment engine,
Python runner and browser worker; Week 16 models, fixtures, context selection,
memory store, CLI and tests; navigation, layout, README, dependency pins and CI
workflow. The assessment adds no dependency, provider, model, hosted execution
service, database, network call or external action.

Added `assessments/week-16.json`, `assessments/week-16.html`,
`tests/test_week16_assessment.py` and this review. The same change exposes the
assessment in navigation and CI, links it from both lesson depths, updates the
lesson patch version to 1.0.1 and records the assessment contract as W16-AS1 in
`labs/week_16/LOGIC.md` revision 2.

## Coverage

The bank contains 100 distinct authored prompts: 30 single-choice, 20
multiple-correct, 15 matching, 15 short syntax and 20 Python coding questions.
Every item has a topic, foundation/applied difficulty, answer key and explanatory
feedback. Each coding task is independent, states its accepted input and failure
behavior and has five executable checks.

| Learning goal | Assessment evidence |
| --- | --- |
| Memory boundaries | Runtime context, Week 15 checkpoints, working context and cross-thread long-term memory have separate lifecycles |
| Semantic and episodic design | Current typed snapshot, compact ordered events, deterministic summaries and explicit state transitions |
| Data minimisation | Raw dialogue, prompts, current questions and evidence bodies stay outside accepted durable schemas |
| Provenance | Document and SQL source references, content digests, report binding and use-time accessibility/digest verification |
| Scope and privacy | Tenant/case allowlists, separate write authority, collision-safe namespaces and context projections |
| Retention | Canonical UTC time, 90-day maximum, use-time expiry, purge metrics and explicit case forgetting |
| Incorrect-memory prevention | Strict closed schemas, canonical digests, exact replay, optimistic revisions, immutable facts and one-way approval status |
| Bounded recall | Deterministic token overlap, stable tie-breaks, complete-line packing and hard character budgets |
| Persistence boundaries | SQLite transactions, process restart, private file mode and the production controls the lab does not claim |
| Python syntax | Exact built-in types, `datetime`, canonical JSON, SHA-256, deep copies, exceptions and deterministic sorting |

## Coding contracts and limits

The browser exercises use only `copy`, `datetime`, `hashlib`, `json` and `re`
from the standard library. They need no SQLite file, LangGraph installation,
provider, model, server, network, repository import or credentials. Actual
schema-versioned SQLite persistence and cross-process behavior remain covered by
the local Week 16 integration lab.

All records use closed shapes or explicitly documented scope fields. Type checks
distinguish exact booleans and integers, reject subclasses where the contract
requires exact built-ins, and reject blank identifiers. Canonical timestamps use
UTC `YYYY-MM-DDTHH:MM:SSZ`; the retention exercise rejects future observations,
non-positive lifetimes and lifetimes beyond the declared maximum.

Evidence projection requires one document and one SQL reference and removes raw
bodies. Canonical hashing uses sorted compact JSON and UTF-8. Source verification
checks current access and content digests at recall time; a digest detects changed
bytes but does not prove source truth, identity or authorization.

Write decisions distinguish create, replay, conflict and update. Status changes
use a closed one-way transition set. Episode append uses contiguous sequences,
an expected-next comparison and count/UTF-8 byte limits. Recall, purge and forget
apply exact namespace and deadline rules without mutating caller data. These
small functions model observable contracts; they do not implement authenticated
identity, production encryption, legal holds, backups or distributed concurrency.

## Executed local verification

Used Python 3.12.14, Node 24.22.1 and the repository's pinned tools in an isolated
temporary environment.

- The focused Week 16 assessment module passes 64 cases. All 20 references pass
  five checks; all 20 starters score zero; every one of 20 distinct plausible
  wrong implementations loses marks.
- The shared JavaScript verifier validates the 100-item bank, exercises 1,000
  balanced reproducible papers, reaches every item and checks objective,
  partial/pending, stale-code and restoration contracts.
- Five composed checks cover scoped minimal provenance, summary/digest/replay,
  retention/recall/forgetting, ranked bounded context and episode/lifecycle audit
  behavior.
- The assessment plus durable SQLite memory lab pass 80 tests.
- The configured regression suite passes 1,536 tests, including all sixteen
  assessment banks, the Week 7–16 labs and the Week 1 service regressions.
- Ruff lint and formatting pass for all 56 configured files. Strict mypy passes
  the same 56 files.
- The Week 13 actual-SQLite smoke passes 12 observations with zero external
  actions. The Week 14 controller smoke passes eight checks, the Week 15 graph
  smoke passes ten and the Week 16 durable-memory smoke passes 12.

This is a public practice bank. A seeded paper draws two questions of each type
for 100 marks. Multiple-correct requires the complete set; matching awards 2.5
per pair; coding awards two points per passed check. Public keys and editable
browser results are not authenticated exam records. Runtime unavailability
leaves coding marks pending. Save/restore, print, result download and scoring
behavior use the unchanged shared engine.

## Publication verification

Publication verification completed on 2026-11-04 for implementation commit
`cc4956d61cd3ae621a040a48374a527972c4dd57`:

- Candidate CI run `41652890299` passed the Python 3.13.12 lint, format, strict
  typing, 1,536-test regression and four CLI smoke gates, followed by the real
  PostgreSQL/pgvector permission, revocation and named-volume restart job.
- Main CI run `41653317589` passed both jobs after fast-forward promotion.
- GitHub Pages run `41653316507` built and deployed successfully.
- The production and beginner lessons each expose two Week 16 assessment links
  and retain their reciprocal depth navigation.
- The live assessment loaded bank version 1.0.0 with the status “100 questions
  ready,” created a 10-question paper with exactly two questions of every type,
  exposed two Python-run controls, ten question-navigation links and one scoring
  submission control, and linked back to the Week 16 lesson.
- The production, beginner and assessment routes logged no page-origin warning
  or error during the final browser verification.

GitHub Pages hosts the static assessment and downloads the pinned browser Python
runtime only when a learner runs a coding solution. The SQLite memory lab remains
local; no public Python service, model, provider or database was deployed.
