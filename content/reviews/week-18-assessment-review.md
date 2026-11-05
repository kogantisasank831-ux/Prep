---
week: 18
status: reviewed
version: 1.0.0
last_reviewed: 2026-11-05
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested completion and publication of the Week 18 questionnaire within the established test-push-publish workflow
---

# Week 18 assessment review

## Baseline and scope

The published implementation baseline is main commit
`02af99411ebec97258c14aae09d733c4612d679c`. Local source commit
`c7358eb` has the equivalent reviewed Week 18 content tree. Only the root
`AGENTS.md` applies. Its Finance App references do not describe this curriculum,
and there is no `Design/` directory. `Path.md` Week 18, the approved production
and beginner lessons, `labs/week_18/LOGIC.md`, the deterministic evaluator and
the established weekly assessment contract define this addition. No subagents
were used.

Inspected the Week 17 bank, page, tests and review; the shared assessment engine,
Python runner and browser worker; Week 18 dataset, contracts, candidate adapter,
graders, aggregation, persistence, CLI and tests; navigation, layout, README,
dependency pins and CI workflow. The assessment adds no dependency, provider,
model, hosted execution service, database, network call or external procurement
action.

Added `assessments/week-18.json`, `assessments/week-18.html`,
`tests/test_week18_assessment.py` and this review. The same change exposes the
assessment in navigation and CI, links it twice from both lesson depths, updates
the lesson patch version to 1.0.1 and records the assessment contract as W18-AS1
in `labs/week_18/LOGIC.md` revision 2.

## Coverage

The bank contains 100 distinct authored prompts: 30 single-choice, 20
multiple-correct, 15 matching, 15 short syntax and 20 Python coding questions.
Every item has a topic, foundation/applied difficulty, answer key and explanatory
feedback. Each coding task is independent, states its accepted input and failure
behavior and has five executable checks.

| Learning goal | Assessment evidence |
| --- | --- |
| Evaluation unit | Named candidate, versioned dataset, task, trial, observation, grader, score and run distinctions |
| Outcome success | Declared status/recommendation/failure matches plus a hard no-unsafe-action condition |
| Tool selection | Exact ordered route, including correct empty routes and detection of omission, addition, reordering and repetition |
| Tool arguments | Independent positional oracle, expected-position denominator and the W18-025 outcome/argument split |
| Efficiency and loops | One-plus-tool expected steps, bounded min/max efficiency and repeated-tool trajectory signal |
| Escalation | Explicit handoff evidence, correct approval/uncertainty cases and stress-heavy dataset caveat |
| Cost | All-attempt fixture numerator, successful-task denominator and explicit zero-success result |
| Latency | Preflight plus maximum parallel first-wave fixture plus downstream commercial fixture |
| Safety | Forbidden external action as a hard case failure, approval stop and explicit unsafe-action rate |
| Dataset integrity | Stable ID, semantic version, exact byte digest, 28-case count, unique IDs and seven-category coverage |
| Category analysis | Recomputed raw counts, rates and denominators rather than labels derived from an overall average |
| Grader choice | Deterministic code checks, rubric-guided people, calibrated model review and hard safety gates |
| Interpretation | Offline/online distinction, held-out release sets, leakage control and limited fixture/injection claims |
| Release evidence | Candidate comparison with safety precedence, trace audit and final raw-count consistency audit |

## Coding contracts and limits

The browser exercises are self-contained and use only `hashlib` from the Python
standard library. They need no Pydantic or LangGraph package, repository import,
provider, model, server, network, database or credentials. The complete strict
dataset loader, candidate, observation models and 28-case evaluation remain in
the local Week 18 lab.

Inputs use exact built-in containers and primitive types where the question says
strict. Closed shapes reject undeclared fields, non-boolean flags, bool-as-int
coercion, blank identities, duplicate case IDs and invalid count relationships.
Rates keep their raw numerator and denominator. Tool-argument accuracy returns
zero positions for no-tool cases; cost includes failed attempts; latency uses a
declared critical path; and zero-success or zero-argument ratios remain `None`
instead of receiving invented perfect values.

The argument-projection task demonstrates only that one declared untrusted field
does not enter four deterministic projections. It is not a model prompt-injection
certificate. The held-out split is an ordering and membership contract, not a
claim that the public practice bank is secret. Candidate comparison makes any
nonzero unsafe-action rate a veto before completion or synthetic cost, but it is
an instructional policy rather than a universal production release standard.

## Executed local verification

Used Python 3.12.14, Node 24.22.1 and the repository's pinned tools in an isolated
temporary environment.

- The focused Week 18 assessment module passes 64 cases. All 20 references pass
  five checks; all 20 starters score zero; every one of 20 distinct plausible
  wrong implementations loses marks.
- The shared JavaScript verifier validates the 100-item bank, exercises 1,000
  balanced reproducible papers, reaches every item and checks objective,
  partial/pending, stale-code and restoration contracts.
- Five composed checks cover independent outcome/argument grading, trajectory
  defects, metric denominators, dataset identity/held-out evidence and
  safety-first candidate comparison.
- The assessment plus deterministic Week 18 evaluator pass 84 tests.
- The configured regression suite passes 1,709 tests, including all eighteen
  assessment banks, the Week 7–18 labs and the Week 1 service regressions.
- Ruff lint and formatting pass for all 71 configured files. Strict mypy passes
  the same 71 files with an isolated cache.
- The Week 13 actual-SQLite smoke passes 12 observations with zero external
  actions. Week 14 passes eight checks, Week 15 ten, Week 16 twelve, Week 17 ten
  and Week 18 eight baseline assertions over all 28 cases.
- Static checks confirm 100 unique ordered IDs, exactly five checks per coding
  task, two lesson links at each depth, the page-to-bank path, front matter,
  fence balance, UTF-8 reads, navigation allowlist, JavaScript syntax, CI wiring
  and clean whitespace.

This is a public practice bank. A seeded paper draws two questions of each type
for 100 marks. Multiple-correct requires the complete set; matching awards 2.5
per pair; coding awards two points per passed check. Public keys and editable
browser results are not authenticated exam records. Runtime unavailability
leaves coding marks pending. Save/restore, print, result download and scoring
behavior use the unchanged shared engine.

## Publication verification

Publication verification completed on 2026-11-05 for implementation commit
`7266cf5386653621ebd854cf27ff7a8ee3ed1788`:

- Candidate CI run `42062744655` passed the Python 3.13.12 lint, format, strict
  typing, 1,709-test regression and six CLI smoke gates, followed by the real
  PostgreSQL/pgvector permission, revocation and named-volume restart job.
- Main CI run `42064705434` passed both jobs after fast-forward promotion.
- GitHub Pages run `42064702847` built and deployed successfully.
- The production and beginner lessons each expose two Week 18 assessment links
  and retain their reciprocal depth navigation.
- The live assessment loaded bank version 1.0.0 with the status “100 questions
  ready,” created a 10-question paper with exactly two questions of every type,
  exposed two Python-run controls, ten question-navigation links and one scoring
  submission control, and linked back to the Week 18 lesson.
- The production, beginner and assessment routes logged no page-origin warning
  or error during the final browser verification.

GitHub Pages hosts the static assessment and downloads the pinned browser Python
runtime only when a learner runs a coding solution. The complete 28-case agent
evaluation remains local; no public Python service, model, provider, database or
procurement action was deployed.
