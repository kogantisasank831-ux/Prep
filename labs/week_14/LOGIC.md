# Week 14 workflow-versus-agent contracts — revision 1

Source: `Path.md` Week 14, the established Week 13 tool-boundary lesson, and the
request to create Week 14 content before its assessment. These rules describe a
local synthetic teaching lab, not a production procurement system.

| ID | Effective rule and acceptance |
| --- | --- |
| W14-BR1 | Investigate the same synthetic purchase order with an explicit deterministic workflow and a bounded planner–executor agent. Both routes use the same tool implementation, decision rule, report model and human-review boundary so the comparison changes control flow rather than business logic. |
| W14-FR1 | The workflow follows five visible transitions: load order, lookup supplier, get dated reference price, calculate exact variance and search contract terms. Each required observation is stored in typed state before the next dependent operation. |
| W14-FR2 | The agent planner may propose only five read/calculation operations or `finish`. The executor validates the action, enforces prerequisites, rejects duplicate/unsupported actions, and stops after at most eight proposals by default. A proposed action never acquires execution authority by appearing in model output. |
| W14-FR3 | Both routes produce one of `no_review`, `review_required` or `needs_human`. Missing contract terms produce `needs_human`; an inactive supplier or variance above the retrieved threshold produces `review_required`; otherwise the result is `no_review`. |
| W14-FR4 | A successful investigation stops at `awaiting_approval`. A trusted host-side human decision is bound to the SHA-256 digest of the exact report snapshot and reviewer identity. Approval accepts the report only; the lab cannot email a supplier, approve a purchase order, make a payment or perform any external write. |
| W14-FR5 | Provide fixed planner scripts for a valid route, a valid detour, a repeated-action loop and an unsupported action. The scripts make termination and policy behavior reproducible; they are not evidence of real-model routing quality. |
| W14-DR1 | Use three small in-memory synthetic cases and dated fictional reference prices. Use `Decimal` with `ROUND_HALF_EVEN` for displayed two-place variance. Require matching currency/unit and a positive reference price. No network, market source, personal data or prior lab store is used. |
| W14-NFR1 | Record model calls, tool calls, assumed tokens, estimated model cost, modeled latency and ordered trace events. Prices and latency are configurable teaching assumptions, not current provider prices, wall-clock measurements or service-level objectives. |
| W14-NFR2 | The comparison runs four controlled scripts against the same case. Failure rate is the observed result of those selected scripts and must be labelled as a control-flow demonstration, never a benchmark or proof that workflows are universally more reliable. |
| W14-ENG1 | Use the standard library and existing repository environment. Keep controllers, models, tools and CLI separately testable. Add no provider, framework, paid service, public API, database migration or assessment. |
| W14-ER1 | Test route parity on a successful case, all three recommendation branches, dependency checks, unsupported/duplicate action rejection, finite loop termination, exact approval binding, deterministic metrics, comparison aggregation and CLI smoke. Run Ruff, strict mypy, pytest, Markdown/front-matter/link checks, CI and live Pages verification before publication. |

Accepted engineering choices: the workflow uses no model calls because this
investigation has a known sequence and deterministic decision rule. The agent
uses a scripted stand-in at the planner boundary so routing calls and termination
are observable without a provider key. The report formatter remains deterministic
to isolate routing as the independent variable.

Real model/provider evaluation, prompt versions, labelled routing data, wall-clock
load tests, authenticated identity, a durable approval service, external effects,
distributed tracing and operating ownership remain deployment decisions. Their
absence prevents production-readiness and model-quality claims but does not block
the bounded local lesson.
