# Week 17 content and lab review

## Scope and disposition

Roadmap source: `Path.md`, Week 17 — Multi-agent systems.

Candidate artifacts:

- `content/weeks/week-17.md`
- `content/weeks/week-17-beginner.md`
- `labs/week_17/`
- `tests/test_week17_multi_agent.py`

Version 1.0.0 is approved for candidate validation. It adds lesson content and a
runnable local supervisor-specialist lab. It does not publish a Week 17
assessment; `ASSESSMENT_WEEKS` therefore remains at Week 16 and neither lesson
links to a nonexistent questionnaire.

## Coverage mapping

| Roadmap requirement | Learner-facing treatment | Executable evidence |
| --- | --- | --- |
| Supervisor-specialist pattern | Central route and four justified roles | supervisor trace and registry |
| Handoffs | Minimal strict assignments/findings with correlation | extra-field, identity and wrong-type rejection |
| Agent boundaries | owned context, result and explicit exclusions per role | isolated specialist functions and source checks |
| Shared state | supervisor-only aggregate over immutable messages | frozen models and unchanged-case test |
| Parallel execution | three independent evidence roles in one bounded wave | three-party barrier and worker metrics |
| Coordination failures | missing, raising, wrong type/run/case and digest faults | fail-closed runs with no report |
| Error propagation | technical failure separated from valid uncertainty | exception failure and `needs_human` scenario |
| When unnecessary | structural comparison and single-workflow guidance | equal report, zero-handoff baseline |
| Document analysis | contract threshold or explicit absence | found and missing-term cases |
| SQL analysis | exact dated current/reference variance | `Decimal` 10.00% assertion |
| Supplier-risk assessment | status, incidents and risk classification | low/elevated cases and cross-source identity |
| Commercial recommendation | deterministic decision precedence | four recommendation scenarios |
| Supervisor combines results | validation followed by dependent synthesis | trace-order and equal-output assertions |
| Compare with single agent/workflow | same components/rules, different coordination shape | handoff/stage comparison without latency claim |
| Justify why each agent exists | ownership and distinct-source table | boundaries reflected in assignment types |

## Technical review

The lab represents agents as deterministic, stateless specialist functions behind
strict contracts. This isolates coordination behavior from model variability and
requires no provider, model, API key or new dependency. The same boundary can
later host a governed model adapter without changing the supervisor contract.

Assignments and findings are closed, strict and frozen. Every result is checked
for exact type, specialist, run and case identity before aggregation. Source
specialists also bind findings to source kind, digest, purchase order and supplier
identity. The digest is correctly described as a mismatch detector rather than a
signature or source-truth guarantee.

The first wave has an allowlist of three roles and at most three workers. Each is
submitted once. Commercial synthesis runs once after validation. Stable
collection order prevents nondeterministic public traces even though worker
execution is concurrent. There is no agent-created fan-out or unbounded loop.

Technical failures produce no report. Valid missing contract evidence produces a
`needs_human` report and still stops at approval. The commercial policy uses
exact decimal comparison, explicit precedence and no external action. The
sequential baseline shares all domain functions and returns an equal report.

The comparison reports structural handoffs and dependency stages only. It does
not convert tiny local fixture timings into a production performance claim.
Remote timeouts, cancellation, retry/idempotency policy, durable job state,
distributed tracing, authenticated identity and production evaluation are
explicitly out of scope.

## Source review

Primary documentation accessed on 2026-11-04:

- official LangChain multi-agent overview for pattern selection, context
  isolation, distributed ownership, parallelization and the single-agent
  alternative;
- official LangChain subagents guide for central supervisor control, stateless
  specialists, inputs/outputs and parallel calls;
- official LangChain handoffs guide for the distinct state-driven
  transfer-of-control pattern; and
- Python 3.13 `concurrent.futures` documentation for executor, future,
  exception, worker-bound and shutdown behavior.

The lessons distinguish those patterns instead of treating every data transfer
as conversational control transfer. Procurement cases, identities, values and
decisions are synthetic and support no production-readiness claim.

## Executed local checks

Local environment: Python 3.12.14. The declared CI environment is Python 3.13.12.

- All 25 focused Week 17 behavior tests pass.
- Ruff lint passes for all 63 files in the configured CI scope, and Ruff format
  reports all 63 files already formatted.
- Strict mypy passes for all 63 configured files with a clean isolated cache.
- The configured regression suite passes: 1,561 tests, including all published
  assessment banks, 16 Week 16 memory cases and 25 Week 17 coordination cases.
- Week 13 actual-SQLite smoke passes all 12 observations.
- Week 14 controller smoke passes all eight observations.
- Week 15 graph smoke passes all ten observations.
- Week 16 memory/context smoke passes all 12 observations.
- Week 17 supervisor/specialist smoke passes all ten observations.
- Front matter, reciprocal lesson links, code-fence balance, YAML parsing,
  JavaScript syntax, UTF-8 reads, whitespace, CI wiring, Week 17 lesson
  navigation and absence of a premature Week 17 assessment link pass locally.

Candidate CI, main promotion and live Pages verification must pass before the
publication section is completed.

## Publication verification

Pending candidate CI and production publication.
