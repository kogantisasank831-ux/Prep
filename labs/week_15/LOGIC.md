# Week 15 LangGraph fundamentals contracts — revision 1

Source: `Path.md` Week 15, the Week 14 controller/approval contracts and the
request to create Week 15 content before its questionnaire. These rules describe
a local synthetic teaching graph, not a production procurement service.

| ID | Effective rule and acceptance |
| --- | --- |
| W15-BR1 | Investigate three synthetic procurement price cases with the Week 14 decision policy: missing contract terms produce `needs_human`; an inactive supplier or variance above the retrieved threshold produces `review_required`; otherwise produce `no_review`. Every supported result still stops for human review. |
| W15-FR1 | Compile an explicit `StateGraph` containing query classification, document retrieval, parameterized SQL analysis, exact price calculation, recommendation generation, report validation and human approval. Nodes return partial updates; edges, not node prose, own the route. |
| W15-FR2 | Route supported procurement-price queries to investigation and unsupported queries to a terminal no-tool node. Route only validated reports to approval; invalid reports end as `validation_failed`. |
| W15-FR3 | Use additive reducers for ordered `evidence` and `trace` channels. All scalar channels use replacement semantics. A reducer demonstrates merge behavior; it is not a substitute for evidence validation. |
| W15-FR4 | Compile with an injected checkpointer. Every invocation has a nonblank bounded `thread_id`; starting over an existing thread is rejected. The lab's `InMemorySaver` preserves thread checkpoints only while that Python process lives. |
| W15-FR5 | The approval node calls one dynamic interrupt with a JSON-safe exact report and SHA-256 digest. Resume requires the same thread plus `approve` or `reject`, a nonblank bounded reviewer and the matching lowercase digest. Approval accepts this report only; it cannot approve an order, contact a supplier, pay money or perform another external write. |
| W15-DR1 | Use dated fictional values, local contract fixtures and a disposable in-memory SQLite table. Query SQL with a bound parameter. Calculate prices with `Decimal` and `ROUND_HALF_EVEN` to two places. Make no network, provider or prior-lab data call at runtime. |
| W15-DR2 | Preserve source identities in evidence: one document search record and one SQL analysis record. Missing contract evidence remains an explicit observation and never becomes proof that no threshold exists. |
| W15-NFR1 | Keep nodes deterministic, separately testable and safe to re-execute. In particular, code before `interrupt()` has no external side effect because LangGraph restarts that node when the thread resumes. |
| W15-NFR2 | A `thread_id` selects checkpoint state; it is not user authentication or authorization. A report digest detects snapshot mismatch; it is not a signature. Production persistence, identity, concurrency, retention, encryption and audit ownership remain deployment work. |
| W15-ENG1 | Pin `langgraph==1.2.19` in the lab requirement file and exercise its real `StateGraph`, reducer, `InMemorySaver`, `interrupt` and `Command(resume=...)` APIs. Keep framework-specific code behind `GraphRuntime`; add no model, prompt, API key, paid service or hosted backend. |
| W15-ER1 | Test topology, all three recommendation branches, reducer order, typed interrupt metadata, checkpoint presence, approve/reject resume, digest mismatch, wrong-thread resume, thread isolation, duplicate starts, fail-closed validation, parameterized SQL and CLI smoke. Run Ruff, format, strict mypy, pytest, CI and live lesson-route verification before publication. |

Accepted engineering choices: classification is a transparent keyword-and-case
rule because this week teaches graph mechanics, not model routing quality. SQL is
real SQLite execution over disposable fixtures; document retrieval is a fixed
local mapping. The sequential graph makes every dependency visible before later
weeks introduce memory and multi-agent coordination.

Durable PostgreSQL/SQLite checkpointers, model-backed classification, real
document stores, authenticated reviewers, external effects, retries, distributed
tracing, retention and operating ownership are intentionally out of scope. Their
absence prevents a production-readiness claim but does not block the local graph
learning outcomes.

