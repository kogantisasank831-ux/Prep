---
week: 15
status: reviewed
version: 1.0.0
last_reviewed: 2026-11-03
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested completion of the Week 15 questionnaire within the established test-push-publish workflow
---

# Week 15 assessment review

## Baseline and scope

The published implementation baseline is main commit
`39895077bd8bd58825da9a48e385d9746303aa69`. Local source commit
`81466df25c967b7f7e2402dcd11884a1d919faf0` has the same reviewed tree. Only
the root `AGENTS.md` applies. Its Finance App references do not describe this
curriculum, and there is no `Design/` directory. `Path.md` Week 15, the
approved production and beginner lessons, `labs/week_15/LOGIC.md`, the real
LangGraph lab and the established weekly assessment contract define this
addition. No subagents were used.

Inspected the Week 14 bank, page, tests and review; the shared assessment engine,
Python runner and browser worker; Week 15 state, fixtures, graph, CLI and tests;
navigation, layout, README, dependency pins and CI workflow. The assessment adds
no dependency, model, provider, hosted execution service, database or external
action.

Added `assessments/week-15.json`, `assessments/week-15.html`,
`tests/test_week15_assessment.py` and this review. The same change exposes the
assessment in navigation and CI, links it from both lesson depths, updates the
lesson patch version to 1.0.1 and records the assessment contract as W15-AS1 in
`labs/week_15/LOGIC.md` revision 2.

## Coverage

The bank contains 100 distinct authored prompts: 30 single-choice, 20
multiple-correct, 15 matching, 15 short syntax and 20 Python coding questions.
Every item has a topic, foundation/applied difficulty, answer key and explanatory
feedback. Each coding task is independent, states input and failure behavior and
has five executable checks.

| Learning goal | Assessment evidence |
| --- | --- |
| State and partial updates | Typed channels, narrow node outputs, replacement values and ordered additive evidence/trace reducers |
| Nodes and edges | Fixed dependencies, closed conditional destinations, exact topology and unsupported terminal routing |
| Validation | Required SQL/contract facts, known recommendation, exact variance and both evidence categories |
| Checkpointing | Opaque bounded thread IDs, duplicate-start rejection, thread isolation, history and redacted snapshot projections |
| Interrupts and resume | JSON-shaped review payload, exact decision/reviewer validation, same-thread resume and report-digest equality |
| Persistence boundaries | In-memory process lifetime, checkpoint versus business record versus long-term memory, migration and retention concerns |
| Replay safety | Deterministic pre-interrupt work, bounded trace state and idempotent post-approval recording |
| Procurement policy | Parameterized-source concepts, exact Decimal variance, strict threshold, missing terms and supplier-status branches |
| Framework limits | Compilation versus business correctness, identity, authorization, durability, conflict handling and observability |
| Python syntax | `TypedDict`, `Annotated`, `StateGraph`, `START`, `END`, `Decimal`, canonical JSON and SHA-256 |

## Coding contracts and limits

The browser exercises use only `copy`, `decimal`, `hashlib`, `json` and
`re` from the standard library. They need no LangGraph installation, provider,
database, server, thread, network, repository import or model. Framework API
knowledge is tested through objective and short-syntax items; the actual
`langgraph==1.2.19` behavior remains covered by the local integration lab.

Reducers and partial state-update exercises preserve ordered contributions,
replacement semantics and caller immutability. Route functions accept only
declared state values. The exact topology exercise rejects both missing and
unexpected nodes or edges.

Price parsing rejects floats, signs, exponent forms, leading zeros, whitespace
and non-string values. Calculation uses a positive reference denominator,
matching currency/unit, precision 28 and explicit two-place half-even rounding.
The recommendation exercise preserves missing contract evidence as
`needs_human` and uses a strict greater-than threshold.

Report hashing uses a closed seven-field payload, ASCII JSON, sorted keys and
compact separators. Approval and resume exercises validate exact lowercase
digest shape and equality, closed decisions, bounded reviewer text and the same
thread. These functions test snapshot binding; they do not authenticate a
reviewer or authorize an order, supplier contact, payment or other external
effect.

Checkpoint projections deliberately exclude query, report and evidence payloads.
The effect exercise models an idempotency decision after approval but performs no
write. The run audit checks lifecycle consistency using trace and evidence
markers; those markers demonstrate state contracts, not source truth.

## Executed local verification

Used Python 3.12.14, Node 24.22.1 and the repository's pinned tools in an isolated
temporary environment.

- The focused Week 15 assessment module passes 64 cases. All 20 references pass
  five checks; all 20 starters score zero; every one of 20 distinct plausible
  wrong implementations loses marks.
- The shared JavaScript verifier validates the 100-item bank, exercises 1,000
  balanced reproducible papers, reaches every item and checks objective,
  partial/pending, stale-code and restoration contracts.
- Five composed checks cover reducer/state/routing behavior, classification plus
  exact price policy, validation/digest/approval binding, interrupt/resume
  binding and topology/effect/audit boundaries.
- The assessment plus real LangGraph lab pass 77 tests.
- The configured regression suite passes 1,456 tests, including all fifteen
  assessment banks, the Week 7–15 labs and the Week 1 service regressions.
- Ruff lint and formatting pass for all 48 configured files. Strict mypy passes
  the same 48 files.
- The Week 13 actual-SQLite smoke passes 12 observations with zero external
  actions. The Week 14 controller smoke passes eight checks. The Week 15 graph
  smoke passes ten checks.

This is a public practice bank. A seeded paper draws two questions of each type
for 100 marks. Multiple-correct requires the complete set; matching awards 2.5
per pair; coding awards two points per passed check. Public keys and editable
browser results are not authenticated exam records. Runtime unavailability
leaves coding marks pending. Save/restore, print, result download and scoring
behavior use the unchanged shared engine.

