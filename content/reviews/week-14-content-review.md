# Week 14 content and lab review

## Scope and disposition

Roadmap source: `Path.md`, Week 14 — Workflows versus agents.

Published artifacts:

- `content/weeks/week-14.md`
- `content/weeks/week-14-beginner.md`
- `labs/week_14/`
- `tests/test_week14_workflows.py`

Version 1.0.0 is approved for the static learning site. The project owner asked
to start Week 14 content after approving and publishing Week 13. This pass follows
the established one-week content/build/test/publish workflow. No separate claim
is made that the owner performed a line-by-line editorial review before release.

## Coverage mapping

| Roadmap requirement | Learner-facing treatment | Executable evidence |
| --- | --- | --- |
| Deterministic workflows | Fixed transition table, dependency order and terminal states | `run_workflow`, exact trace assertion |
| LLM-based routing | Planner proposals, structured action validation and route uncertainty | `ScriptedPlanner`, happy/detour/unsafe scripts |
| State machines | Business state versus control state, transition table | `InvestigationState`, fixed action sequence |
| Agent loops | Proposal → validation → execution → observation with finite budget | `run_agent`, loop and premature/dependency cases |
| Planner–executor | Responsibility table and shared trusted executor | Allowed enum, prerequisite and unsupported-action tests |
| Evaluator–optimizer | Deterministic checks first, semantic rubric and bounded revision | Lesson pseudocode and exercises; no unnecessary second model in the lab |
| Orchestrator–worker | Dynamic decomposition, bounded fan-out, correlation and merge conflicts | Design treatment and exercise; fixed lab graph stays an ordinary workflow |
| Human approval | Pending terminal state and exact report-snapshot binding | SHA-256 report digest, approve/reject validation |
| Reliability, calls, cost, latency, failure, explainability | Same-case comparison with explicit assumptions and denominator warning | Four-script comparison aggregation |
| “When should you not use an agent?” | Selection table, failure modes and interview response | Both lesson depths |

The assessment is intentionally absent. `PUBLISHED_WEEKS` includes Week 14 while
`ASSESSMENT_WEEKS` remains through Week 13, so the roadmap cannot expose a broken
Week 14 assessment link.

## Technical boundaries

Both controllers use the same three synthetic cases, typed facts, five tools,
`Decimal` variance calculation, decision function, deterministic report and
human-review boundary. The workflow makes no model calls. The agent uses a fixed
planner boundary so route validation and termination are repeatable.

Reference prices are fictional and dated 2026-10-01. Model prices (USD 1.00 per
million input tokens and USD 3.00 per million output tokens) and latency values
are teaching inputs. The displayed 50% scripted-agent failure rate is produced
by two valid and two deliberately failing scripts. The lessons explicitly reject
provider-price, wall-clock, real-model-quality and universal-reliability claims.

Human approval accepts only a local report whose digest matches the reviewed
snapshot. Runtime checks require a valid decision enum, lowercase 64-character
hex digest and nonblank bounded reviewer. The lab has no external write, supplier
communication, purchase approval or payment capability. This is not identity,
a signature or a durable approval service.

## Review findings resolved

- The first aggregate-cost implementation let `sum` infer `int | Decimal` under
  strict mypy. A `Decimal("0")` start value now preserves the numeric contract.
- Approval originally relied on annotations for decision type. Runtime validation
  now rejects a string masquerading as an approval decision instead of treating
  it as a rejection.
- Cost, latency and failure-rate language was narrowed throughout the lessons and
  README so simulated values cannot be mistaken for deployment measurements.
- The unsupported-action scenario has no matching tool, and the repeated-action
  scenario records only one actual tool call before its finite terminal failure.

No unresolved actionable finding remains within the declared local teaching
scope. Real provider evaluation, authenticated approval, persistent state,
external effects and production operating controls remain future design work.

## Executed local checks

Local environment: Python 3.12.14 with the repository virtual environment.

- Ruff lint passes for the 40 files in the configured CI scope.
- Ruff format check reports all 40 files already formatted.
- Strict mypy passes for all 40 configured files.
- The configured regression suite passes: 1,315 tests, including 12 Week 14
  workflow/agent tests.
- Week 13 actual-SQLite smoke passes all 12 observations, preserving the prior
  gate after the CI edit.
- Week 14 CLI smoke passes eight observations.
- Workflow, happy-agent and comparison commands produce the values reproduced in
  the lesson: identical report digest, 0 versus 6 model calls for successful
  routes, and 0% versus 50% failure in the selected four-run control set.
- Front matter, balanced code fences, UTF-8 reads, heading presence, absent Week
  14 assessment links, JavaScript syntax and whitespace checks pass.

The local runtime is Python 3.12 rather than the declared CI Python 3.13.12.
Exact-candidate CI on Python 3.13.12, the existing real PostgreSQL/container job,
GitHub Pages build and live-route checks remain release gates and must be recorded
after publication. GitHub Pages hosts only the lessons; Python runs locally.
