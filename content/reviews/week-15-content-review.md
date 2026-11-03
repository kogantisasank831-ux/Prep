# Week 15 content and lab review

## Scope and disposition

Roadmap source: `Path.md`, Week 15 — LangGraph fundamentals.

Candidate artifacts:

- `content/weeks/week-15.md`
- `content/weeks/week-15-beginner.md`
- `labs/week_15/`
- `tests/test_week15_langgraph.py`

Version 1.0.1 is approved for the static learning site after local review. The
owner requested Week 15 content after Week 14 content and its questionnaire were
published. Patch 1.0.1 adds only reviewed links to the separately tested Week 15
assessment. `ASSESSMENT_WEEKS` is extended to Week 15 in the same change that
adds the bank, page and regression module, so navigation cannot expose a missing
route.

## Coverage mapping

| Roadmap requirement | Learner-facing treatment | Executable evidence |
| --- | --- | --- |
| State | Typed business/control channels and partial updates | `InvestigationState`, checkpoint state assertions |
| Nodes | Eight separately named and testable functions | Exact topology test and node-level malformed validation |
| Edges | Fixed dependency route from retrieval through validation | Exact graph-edge assertions |
| Conditional routing | Supported/unsupported and valid/invalid branches | Unsupported no-tool terminal test; validation router coverage |
| Reducers | Additive evidence/trace versus scalar replacement | Ordered two-source evidence and nonduplicated resume trace |
| Checkpointing | Compiled `InMemorySaver`, checkpoint history and isolation | Checkpoint-count, thread-state and duplicate-start tests |
| Interrupts | Typed JSON-safe approval pause and `Command(resume=...)` | Response-schema, approve/reject and wrong-digest tests |
| Persistence | Checkpointer/store distinction and in-memory restart limit | Same-process resume plus explicit production exclusions |
| Query classification | Transparent narrow deterministic classifier | Supported and unsupported route tests |
| Document retrieval | Local result preserving document ID and missing status | Found/missing evidence in three case branches |
| SQL analysis | Parameterized disposable SQLite query | Valid row and injection-shaped unknown-ID tests |
| Price calculation | Exact `Decimal` two-place calculation | 10.00% and 2.00% case assertions |
| Recommendation generation | Same Week 14 three-branch business rule | Parameterized `review_required`, `no_review`, `needs_human` tests |
| Validation | Required fact/source checks before approval | Fail-closed malformed-state assertion |
| Human approval | Same thread, exact report digest, reviewer and decision | Approve/reject, mismatch and wrong-thread assertions |
| Graph reliability interview | Finite topology, typed state, deterministic gates and replay-safe pause | Production interview response and failure-boundary section |

## Technical boundaries

The lab pins `langgraph==1.2.19` and uses its real `StateGraph`, additive reducer,
conditional edges, `InMemorySaver`, typed `interrupt()` and
`Command(resume=...)` behavior. There is no framework imitation and no model,
prompt or API key. Classification is deterministic so the lab evaluates graph
orchestration rather than model quality.

All procurement data is fictional. Contract retrieval is a local mapping. SQL
executes against a fresh in-memory SQLite table with a bound parameter. Price
math uses `Decimal` and `ROUND_HALF_EVEN`. Missing contract evidence is preserved
as an observation and routes to `needs_human`.

The approval interrupt accepts or rejects only the canonical local report whose
SHA-256 digest matches the displayed snapshot. `thread_id` is described as a
checkpoint cursor, not authentication. The reviewer value is not verified
identity, and the digest is not a signature. The graph cannot communicate with a
supplier, approve a purchase order, make a payment or perform another external
write.

`InMemorySaver` lasts only for the owning Python process. The lessons explicitly
separate graph checkpoints, business records and the longer-lived memory planned
for Week 16. Durable checkpointers, migrations, retention, encryption,
concurrency, authenticated reviewers and operating ownership remain production
work.

## Review findings resolved

- The lab initially used the runtime without its declared dependency. A dedicated
  pinned requirement file and both CI install/cache paths now cover it.
- Strict typing identified a redundant recommendation cast and an untyped `END`
  return from the conditional router. The implementation now relies on the
  narrowed literal and returns the declared terminal literal.
- The approval response uses a generated typed schema but is also validated at
  the host boundary for decision, reviewer and exact digest.
- The node before `interrupt()` constructs only a JSON-safe payload. It performs
  no external side effect that resume could duplicate when the node restarts.
- The content-only publication added Week 15 to `PUBLISHED_WEEKS` while leaving
  `ASSESSMENT_WEEKS` unchanged. Patch 1.0.1 adds assessment links only after the
  complete bank, page and regression module exist.
- Patch 1.0.1 does not change the lesson's technical claims, lab behavior or
  procurement values. Assessment verification is recorded in
  `content/reviews/week-15-assessment-review.md`.

No unresolved actionable finding remains within the declared local teaching
scope.

## Source review

The lessons use primary documentation for current framework behavior:

- the official LangGraph overview for framework scope;
- the official Graph API guide for state, reducers, nodes, edges and compilation;
- the official persistence guide for checkpointers, stores, thread IDs and the
  in-memory restart limitation;
- the official interrupt guide for pause/resume, typed response schemas and node
  restart behavior;
- the maintainer-published PyPI release page for the pinned 1.2.19 package; and
- the Python standard-library documentation for SQLite and decimal behavior.

Those pages were accessed on 2026-11-02 and support the adjacent framework/API
claims. They do not justify the fictional procurement facts or imply production
readiness.

## Executed local checks

Local environment: Python 3.12.14. The declared CI environment is Python 3.13.12.

- Ruff lint passes for all 48 files in the configured CI scope.
- Ruff format reports all 48 files already formatted.
- Strict mypy passes for all 48 configured files.
- The configured regression suite passes: 1,456 tests, including 64 Week 15
  assessment cases and 13 focused Week 15 graph cases.
- Week 13 actual-SQLite smoke passes all 12 observations.
- Week 14 controller smoke passes all eight observations.
- Week 15 graph smoke passes all ten observations.
- Front matter, code-fence balance, YAML parsing, JavaScript syntax, UTF-8 reads,
  whitespace and resolved Week 15 assessment-link checks pass locally.

## Publication verification

Publication verification completed on 2026-11-03 for implementation commit
`6630944797fcbfe5736c99b1a4378468077f3957`:

- Candidate CI run `41460854488` passed the Python 3.13.12 lint, format, strict
  typing, 1,392-test regression and three CLI smoke gates, followed by the real
  PostgreSQL/pgvector permission, revocation and named-volume restart job.
- Main CI run `41461335198` passed both jobs after fast-forward promotion.
- GitHub Pages run `41461334201` built and deployed successfully.
- The production route rendered “Make the control flow visible with LangGraph,”
  the beginner route rendered “Build your first stateful graph,” and both depth
  links resolved to one another.
- At that content-only implementation commit, live navigation exposed Week 15 as
  a lesson, left Week 16 as a roadmap item and correctly exposed no questionnaire.
  Neither lesson logged a page-origin console error. Assessment publication is
  recorded separately in `content/reviews/week-15-assessment-review.md`.

GitHub Pages hosts only static lesson and assessment assets. The LangGraph
runtime, in-memory SQLite fixture and checkpoints run locally after the learner
installs the pinned lab requirement.
