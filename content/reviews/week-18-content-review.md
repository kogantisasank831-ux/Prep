# Week 18 content and lab review

## Scope and disposition

Roadmap source: `Path.md`, Week 18 — Agent evaluation.

Candidate artifacts:

- `content/weeks/week-18.md`
- `content/weeks/week-18-beginner.md`
- `labs/week_18/`
- `tests/test_week18_agent_evaluation.py`

Version 1.0.0 is approved for candidate validation. It adds two lesson depths and
a deterministic offline evaluation over Procurement Intelligence Agent v1. It
does not publish a Week 18 assessment; `ASSESSMENT_WEEKS` therefore remains at
Week 17 and neither lesson links to a nonexistent questionnaire.

## Coverage mapping

| Roadmap requirement | Learner-facing treatment | Executable evidence |
| --- | --- | --- |
| Task-completion rate | declared end-state contract, safe failure semantics and raw counts | status/recommendation/failure/unsafe-action grader |
| Tool-selection accuracy | exact ordered route including correct no-tool decisions | 28 route comparisons |
| Tool-argument accuracy | expected call-position denominator and independent oracle | 72/73 baseline with injected SQL supplier defect |
| Step efficiency | symmetric expected/actual formula | exact baseline plus missing/extra mutation checks |
| Loop rate | repeated-tool definition and retry caveat | duplicate-call mutation detection |
| Human escalation rate | invalid input, uncertainty, technical failure and approval categories | 18/28 explicit escalations and category slices |
| Cost per successful task | failures retained in total-attempt numerator | 265 fixture units / 28 successes |
| Latency per task | parallel critical-path fixture and production caveat | deterministic 1 + max(first wave) + commercial arithmetic |
| Unsafe-action rate | hard failure signal rather than averaged quality | prohibited actions stop before tools; unsafe mutation fails |
| Normal requests | six price/risk policy investigations | completed recommendations and stable replay |
| Missing information | malformed requests and valid missing terms | no-tool request escalation and `needs_human` report |
| Tool failures | one controlled failure per specialist | fail-closed codes and no report |
| Conflicting evidence | wrong run/case, supplier conflict and digest mismatch | correlation failures without commercial action |
| Prompt injection | four direct/indirect-looking strings with narrow claim | injected/clean observations match; text absent from arguments |
| Invalid tool arguments | extra/coerced request data and wrong SQL supplier | strict validation plus independent argument-grader failure |
| Approval required | approve, purchase and supplier-contact requests | preflight escalation with zero calls/actions |
| 20–30 cases | exactly 28 visible, versioned synthetic cases | strict count, unique IDs and category coverage |
| Procurement Intelligence Agent v1 | Week 17 supervisor is the evaluated candidate | adapter retains existing specialists and policy |

## Technical review

The Week 17 supervisor and four deterministic specialists remain the system under
evaluation. Week 18 adds only a strict public request boundary, controlled fault
adapters and minimal trace projection. This prevents the evaluator from silently
reimplementing the commercial decision policy it claims to assess.

The JSON dataset is size-bounded, UTF-8, duplicate-key checked and rejects
non-finite constants. Strict frozen Pydantic models reject unknown fields,
coercion, duplicate case IDs, an incorrect case count and missing category
coverage. Results bind the named candidate to the exact dataset SHA-256 and can
be persisted only into a fresh directory.

End-state success and trajectory quality are separate. `W18-025` sends an invalid
supplier argument, is safely rejected by SQL and reaches the declared failure
state. Its task grader passes while its argument grader records two correct of
three expected calls. Expected arguments derive from the accepted request and
immutable fixture rather than the fault adapter.

Tool-selection credit includes correct no-tool decisions. No-tool cases are
excluded from the argument denominator. Step efficiency penalizes both missing
and extra steps. Loop, escalation, cost, latency and unsafe action keep their raw
counts or declared units visible. Category slices use the same metric function as
the overall result.

Cost and latency are explicitly synthetic. Latency follows the declared parallel
critical path rather than measured local runtime. The stress-heavy escalation
rate is not presented as representative production traffic. The implementation
uses no current clock or random source, so the complete artifact replays exactly.

Prompt-injection cases verify only that `untrusted_text` does not enter this
deterministic adapter's routing, registry, authorization or tool arguments. The
lessons state that this is not evidence of broad model resistance. The candidate
has no external write capability; approval, purchase and supplier-contact requests
stop before tool execution.

The grader suite is itself tested with mutated observations for wrong outcome,
arguments, tool route, steps, loop and unsafe action. This reduces the risk of an
always-green evaluator.

## Source review

Primary and first-party technical material accessed on 2026-11-04:

- OpenAI agent-evals documentation for end-to-end workflow, tool-call and
  handoff evaluation;
- OpenAI trace-grading documentation for structured trajectory graders;
- OpenAI evaluation best practices for objectives, datasets, metrics, comparison
  and continuous evaluation;
- LangSmith evaluation-types documentation for offline benchmarking, unit and
  regression evaluation, backtesting and online evaluation;
- Anthropic's agent-evaluation guide for task, trial, grader and trace terminology
  and repeated trials for variable candidates; and
- OWASP LLM01:2025 for direct/indirect prompt injection and its possible effect on
  tool access and critical decisions.

The lessons use these sources to distinguish deterministic contract graders from
subjective human/model rubrics, offline gates from online monitoring, and narrow
controlled evidence from production or safety claims.

## Executed local checks

Local environment: Python 3.12.14. The declared CI environment is Python 3.13.12.

- All 20 focused Week 18 behavior and evaluator tests pass.
- Ruff lint passes for all 70 files in the configured CI scope, and Ruff format
  reports all 70 files already formatted.
- Strict mypy passes for all 70 configured files with a clean isolated cache.
- The configured regression suite passes 1,645 tests, including every published
  assessment bank and the focused Week 18 evaluator suite.
- Week 13 actual-SQLite smoke passes all 12 observations.
- Week 14 controller smoke passes all eight observations.
- Week 15 graph smoke passes all ten observations.
- Week 16 memory/context smoke passes all 12 observations.
- Week 17 supervisor/specialist smoke passes all ten observations.
- Week 18 evaluation smoke passes eight baseline assertions over all 28 cases.
- Front matter, reciprocal lesson links, code-fence balance, YAML parsing,
  JavaScript syntax, UTF-8 reads, whitespace, CI wiring, Week 18 lesson
  navigation and absence of a premature Week 18 assessment link pass locally.

Candidate CI, main promotion and live Pages verification must pass before the
publication section is completed.

## Publication verification

Publication verification completed on 2026-11-05 for implementation commit
`d4babe7e8ce6f6c78f616a2dffda56a8cb3b103a`:

- Candidate CI run `41976331296` passed the Python 3.13.12 lint, format, strict
  typing, 1,645-test regression and six CLI smoke gates, followed by the real
  PostgreSQL/pgvector permission, revocation and named-volume restart job.
- Main CI run `41976583730` passed both required jobs after fast-forward
  promotion.
- GitHub Pages run `41976583214` built and deployed successfully.
- The production route rendered “Evaluate agents by outcomes, trajectories and
  safety,” and the beginner route rendered “Test an agent like a careful driving
  examiner.” Their reciprocal depth links resolved in both directions.
- Live navigation exposed Week 18 as a lesson and left Week 19 as a roadmap item.
  Both routes exposed zero Week 18 assessment links, matching the content-only
  scope.
- Neither route logged a page-origin warning or error during final browser
  verification.

GitHub Pages hosts only the static lessons. The evaluation candidate, dataset,
graders and CLI run locally; no public Python service, model, provider, database
or procurement action was deployed.
