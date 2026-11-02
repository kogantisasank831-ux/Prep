# Week 15 content and lab review

## Scope and disposition

Roadmap source: `Path.md`, Week 15 — LangGraph fundamentals.

Candidate artifacts:

- `content/weeks/week-15.md`
- `content/weeks/week-15-beginner.md`
- `labs/week_15/`
- `tests/test_week15_langgraph.py`

Version 1.0.0 is approved for the static learning site after local review. The
owner requested Week 15 content after Week 14 content and its questionnaire were
published. This pass covers content and the runnable lab only. It does not add or
expose a Week 15 questionnaire; `ASSESSMENT_WEEKS` remains through Week 14.

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
- Navigation adds Week 15 to `PUBLISHED_WEEKS` while intentionally leaving
  `ASSESSMENT_WEEKS` unchanged.

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

- Ruff lint passes for all 47 files in the configured CI scope.
- Ruff format reports all 47 files already formatted.
- Strict mypy passes for all 47 configured files.
- The configured regression suite passes: 1,392 tests, including 13 focused
  Week 15 graph cases.
- Week 13 actual-SQLite smoke passes all 12 observations.
- Week 14 controller smoke passes all eight observations.
- Week 15 graph smoke passes all ten observations.
- Front matter, code-fence balance, YAML parsing, JavaScript syntax, UTF-8 reads,
  whitespace and changed-link checks pass locally.

Candidate branch CI, main CI, GitHub Pages deployment and live route verification
are required before publication is recorded as complete.
