# Week 13 tool-calling lab contracts — revision 1

Source: Path.md Week 13, approved Week 11–12 contracts, and the user's instruction
to create Week 13 content within the established build/test/publish workflow.
These are reversible local teaching choices, not a finance product specification.
The requirements/coding workflow was used; implementation reads this revision.

| ID | Effective rule and acceptance |
| --- | --- |
| W13-BR1 | Teach a proposed-call → application-validation/authorization → execution → correlated-result → final-response loop. A deterministic scripted planner exercises the protocol without claiming real-model selection, argument or answer quality. |
| W13-FR1 | Expose five tools: named parameterized SQL, exact price variance, supplier lookup, dated synthetic commodity lookup and reused guarded document search. SQL never accepts arbitrary SQL. A sixth optional create_review writes only a local synthetic review record and has no external action capability. |
| W13-FR2 | Accept bounded strict JSON turns with exactly one call or final response. Reject duplicate/nonfinite JSON, extra envelope fields, repeated call IDs and invalid final evidence IDs. Arguments are closed Pydantic strict models; invalid calls get a bounded correlated error without handler invocation. No eval, shell, arbitrary URL, dynamic import or model-supplied identity. |
| W13-FR3 | Inject trusted tenant/principal via Actor/SecurityContext; constructors validate shape, not authentication. Filter SQL/lookup rows by tenant and current principal access. Reuse Week 11 policy/pin controls for document search. Catalogue visibility is convenience, while execution independently enforces write capability, current target grant and exact approval. |
| W13-DR1 | Use fixed synthetic SQLite records for purchases, supplier and commodity facts, with explicit currency/unit/date. Keep existing PostgreSQL code/data unchanged. Read through mode=ro connections and parameterized named queries. The SQLite file and all callbacks are trusted local application dependencies, not a hostile-plugin sandbox. |
| W13-DR2 | Prices are canonical strings with two decimal places, 0.00–999999.99. Variance requires positive baseline and equal currency/unit; delta=current-baseline, percent=delta/baseline*100. Return decimal strings rounded to two places with ROUND_HALF_EVEN. This is a declared fixture arithmetic convention, not accounting, FX or commodity-market advice. |
| W13-FR4 | Treat tool output as data. Validate the expected closed output schema and bound its serialized bytes before forwarding; reject action-shaped extra fields. Preserve call correlation. Permitted result text may still contain untrusted instructions. Final evidence-ID membership does not prove factual truth, entailment or completeness. |
| W13-NFR1 | Sequential execution, at most six calls/eight planner turns by default, two attempts only for explicitly transient read failures/timeouts, 0.05-second retry delay, per-await deadlines and a five-second cooperative run budget. Numeric values are teaching settings, not SLOs. Bound request/turn/result/transcript representations. |
| W13-FR5 | Never automatically retry a write. Timeout, unavailable/unknown execution or invalid output after write admission yields unknown_outcome and stops the loop. Caller cancellation propagates and may leave a committed effect; reconcile using the original operation key. Async deadlines cannot hard-kill blocking work; SQLite has a separate bounded busy wait. |
| W13-FR6 | The trusted caller supplies an operation key and approval bound to tenant, principal, tool/version and validated arguments, with monotonic expiry. Neither key nor approval is a model argument. The CLI's explicit approved-write scenario supplies a synthetic approval fixture, not a real authenticated human approval workflow. |
| W13-DR3 | In one BEGIN IMMEDIATE transaction, recheck the target grant, check approval, compare the stored argument digest for (tenant,principal,operation_key), then insert one review and its replay result. Same key+same arguments returns the original review ID; same key+changed arguments conflicts. Check current authority even on replay. Unique constraint/transaction cover cooperating writers to this SQLite file. Retain history until the fixture file is explicitly discarded; no distributed/external exactly-once claim. |
| W13-ENG1 | Reuse declared Python/Pydantic, pytest, Ruff and mypy; no new dependency, paid provider, hosted service, schema migration of prior labs or assessment change. Log bounded categories/counts rather than prompts, arguments, result bodies or exception messages. Actual CLI output deliberately displays only synthetic lesson data. |
| W13-ER1 | Test each tool against independent expected results and scope negatives; malformed arguments/results/turns; exact decimal and units; correlation and budget termination; transient retry versus permanent errors; timeout and cancellation; actual SQLite replay/conflict/expiry/current-grant/concurrent writes and lost-response recovery. Run actual CLI smoke and mandatory exact-candidate CI, retaining the previous PostgreSQL/container HTTP gates. |

Accepted engineering choices: a small separate SQLite fixture and scripted
planner make action contracts reproducible without extending Week 12's HTTP or
database interfaces. The optional review record gives side-effect protection
an observable local example within the roadmap's idempotency requirement.

Coverage: interface/access/storage/failure/retry/cancellation/evaluation rules are
covered above; model training, labels/splits, GPU/paid-provider evaluation and
external side effects are not applicable to this deterministic local build.
Public identity/TLS, durable approval service, ledger retention policy for real
data, external reconciliation, shared infrastructure limits, provider adapter
and real-model quality thresholds remain deferred to an actual deployment.
Their owners are unassigned; no production-readiness or quality sign-off is implied.

Implementation/test mappings and actual results belong in the internal content
review. No planned check is recorded as executed in this baseline.
