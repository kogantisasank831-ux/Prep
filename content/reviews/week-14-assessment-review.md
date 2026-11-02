---
week: 14
status: reviewed
version: 1.0.0
last_reviewed: 2026-11-02
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested the Week 14 questionnaire within the established test-push-publish workflow
---

# Week 14 assessment review

## Baseline and scope

The published implementation baseline is main commit
`a7bca433ad78245074e0fa9b9549eed3b3d04cfa`. Only the root `AGENTS.md`
applies. Its Finance App references do not describe this curriculum, and there
is no `Design/` directory. `Path.md` Week 14, `plan.md`, the approved main and
beginner lessons, `labs/week_14/LOGIC.md`, the controller/tool implementation
and the established weekly assessment contract define this addition. No
subagents were used.

Inspected the Week 13 bank, page, tests and review; the shared assessment engine,
Python runner and worker; Week 14 models, tools, controllers, CLI and tests;
navigation, layout, README, dependency pins and CI workflow. The assessment adds
no dependency, provider, hosted execution service, database or external action.

Added `assessments/week-14.json`, `assessments/week-14.html`,
`tests/test_week14_assessment.py` and this review. The same change exposes the
assessment in navigation and CI, links it from both lesson depths, updates the
lesson patch version to 1.0.2 and records the assessment contract as W14-AS1 in
`labs/week_14/LOGIC.md` revision 2.

## Coverage

The bank contains 100 distinct authored prompts: 30 single-choice, 20
multiple-correct, 15 matching, 15 short syntax and 20 Python coding questions.
Every item has a topic, foundation/applied difficulty, answer key and explanatory
feedback. Each coding task is independent, states its boundary and failure
behavior, and has five executable checks.

| Learning goal | Assessment evidence |
| --- | --- |
| Controller selection | Stable workflow, bounded agent and conservative hybrid-selection scenarios |
| State and transitions | Business versus control state, reachable workflow prefixes, fact readiness and typed observation assignment |
| Bounded agent loop | Strict actions, finish readiness, duplicates, unsupported actions, prerequisites and proposal budgets |
| Shared business logic | Exact variance, missing terms, supplier status, strict threshold boundary and route report parity |
| Planner–executor | Proposal classification, application-owned admission and shared execution authority |
| Evaluator–optimizer | Deterministic report gates versus bounded semantic criteria |
| Orchestrator–worker | Worker allowlist, fan-out, duplicate/capacity rejection, provenance and conflict-preserving merge |
| Human approval | Canonical report digest, awaiting state, exact decision/reviewer validation and mismatch rejection |
| Evaluation honesty | Scripted usage assumptions, controlled aggregation, labelled trials and scoped failure rates |
| Python syntax | dataclass/default factory, enum identity, Protocol, frozenset, Decimal, canonical JSON, hashing and finite loops |

## Coding contracts and limits

The browser exercises use only `re`, `copy`, `decimal`, `hashlib` and `json` from
the standard library. They need no provider, database, server, thread, network,
repository import or model. Closed proposal parsing never grants execution
authority. Workflow transition practice accepts only reachable prefix states,
and the bounded-loop exercise distinguishes planner calls from actual tool
attempts while preserving the lab's dependency behavior.

Recommendation and variance exercises reject floats, signs where forbidden,
leading zeros, exponent forms, whitespace and Unicode lookalike digits. Variance
uses a positive reference denominator, matching currency/unit, precision 28 and
explicit two-place half-even rounding. The exact examples reproduce the
price-spike and stable-price fixture values but do not establish source accuracy.

Report hashing uses a closed five-field payload, ASCII JSON, sorted keys and
compact separators. Approval checks exact lowercase hexadecimal identity,
reviewer shape, decision and lifecycle. These functions accept a report only;
they do not authenticate a person or authorize procurement, communication or
payment effects.

The orchestrator exercises are pure planning and merge functions. They enforce a
worker catalogue, maximum fan-out, duplicate and capacity policy, one result per
expected worker, source provenance and explicit conflict detection. They do not
run parallel jobs or prove distributed cancellation and recovery.

Usage, latency and cost values remain teaching assumptions. Aggregation reports
only the supplied trial set. The four-script 50.0% result is tested as selected
control data, never as real-model accuracy or production reliability.

## Executed local verification

Used Python 3.12.14, Node 24.22.1 and the repository's pinned tools.

- The focused Week 14 assessment module passes 64 cases. All 20 references pass
  five checks; all 20 starters score zero; every one of 20 distinct plausible
  wrong implementations loses marks.
- The shared JavaScript verifier validates the 100-item bank, exercises 1,000
  balanced reproducible papers, reaches every item and checks objective,
  partial/pending, stale-code and restoration contracts.
- Five composed checks cover proposal/fact/business-rule separation, exact
  approval binding, controller selection, bounded workers/provenance and scoped
  trial/metric aggregation.
- The configured regression suite passes 1,379 tests, including all fourteen
  assessment banks, the Week 7–14 labs and the Week 1 service regressions.
- Ruff lint and formatting pass for all 41 configured files. Strict mypy passes
  the same 41 files. Node syntax and git whitespace checks pass.
- The Week 13 actual-SQLite smoke passes 12 observations with zero external
  actions. The Week 14 workflow/agent smoke passes eight observations.

This is a public practice bank. A seeded paper draws two questions of each type
for 100 marks. Multiple-correct requires the complete set; matching awards 2.5
per pair; coding awards two points per passed check. Public keys and editable
browser results are not authenticated exam records. Runtime unavailability
leaves coding marks pending. Save/restore, print, result download and scoring
behavior use the unchanged shared engine.

## Publication verification

Publication verification completed on 2026-11-02 for implementation commit
`cd00c913d2d17e6344e984135b90bb2b41edf2a8`:

- Candidate CI run `41455476959` passed the Python 3.13 lint, format, strict
  typing, 1,379-test regression and both CLI smoke gates, followed by the real
  PostgreSQL/pgvector permission, revocation and named-volume restart job.
- Main CI run `41455931354` passed both jobs after fast-forward promotion.
- GitHub Pages run `41455930166` built and deployed successfully.
- The live assessment loaded bank version 1.0.0 with the status “100 questions
  ready,” created a 10-question paper with exactly two questions of every type,
  exposed two Python-run controls and one scoring submission control, and logged
  no page-origin console error.

GitHub Pages hosts the static assessment and downloads the pinned browser Python
runtime only when a learner runs a coding solution. No public Python service or
database was deployed.
