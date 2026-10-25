# Week 12 local service contracts (revision 1)

Source: Path.md Week 12, approved Week 11 source/quote contracts and the user's
weekly build/publish instruction. This is the lab's scoped logic handoff, not a
new finance product specification. Numeric limits below are explicit synthetic
teaching configuration choices, not measured service objectives.

| ID | Effective rule and acceptance |
| --- | --- |
| W12-FR1 | Provide FastAPI /v1/ask JSON and /v1/ask/stream SSE, /docs and /openapi.json; accept only the Week 11 question envelope, max 4096 UTF-8 bytes/1000 decoded characters, with no body-supplied identity. Invalid type/schema 400; media 415; oversized body 413; body-read deadline 408. |
| W12-FR2 | Generated file-backed bearer secrets map to fixed synthetic North/South tenant+analyst identities. Missing/invalid credential is 401 before body/database work. Tokens are not logged, returned or committed; restart is required after file rotation. This is local demo authentication, without account lifecycle/OIDC/TLS/public exposure. |
| W12-DR1 | PostgreSQL persists source-version policies, source chunk representations and vector(32) embeddings. A separate bootstrap identity owns schema/seed writes. The API DB role has SELECT only. SQL parameters carry scope/data, never model-generated SQL. |
| W12-FR3 | Filter tenant/current approved reader grants in SQL, validate source/representation pins and known content findings before the pgvector candidate query, then run Week 11 secure_ask over at most 12 selected chunks. Exact vector search is over this eligible set, without an ANN index. Hash features are a synthetic baseline, not a semantic model or quality guarantee. |
| W12-FR4 | Reconstruct each first snapshot in a read-only repeatable-read transaction. After compute/cache access, obtain a NEW snapshot and compare complete selected chunks/policies. A changed snapshot produces the common refusal with no cached success. It cannot retract earlier reads, cover changes after the last check or establish distributed atomic revocation. |
| W12-FR5 | A bounded 32-entry/15-second monotonic TTL cache retains only fully validated successful results, keyed by tenant, principal, exact question digest, complete snapshot fingerprint and pipeline configuration. Hits still perform the two DB snapshot reads. New request IDs replace cached correlation IDs. DB failure returns 503, never stale success. Clear entries on shutdown. |
| W12-NFR1 | Authenticate, then count each ask attempt in a process-local per-principal fixed window (default 12 per 60 seconds). Return 429/Retry-After on exhaustion. Two identities bound key cardinality; authentication failures need a separate edge control in a public system. Multiple workers would multiply this allowance. |
| W12-NFR2 | Admit at most two expensive request pipelines per process, fail excess admission with 503/Retry-After and release slots in finally. Async database calls yield while waiting. Offload the bounded synchronous guarded assistant to a thread and retain admission until it actually finishes even if the request is cancelled; do not pretend cancellation kills Python threads. |
| W12-FR6 | Validate a full result before streaming headers. SSE sends meta, result, done frames with JSON-escaped data. Network interruption may omit done; consumers must require it. It is not early token streaming, replay or durable job execution. Public responses omit internal reason codes/candidate counts and use Cache-Control: no-store. |
| W12-NFR3 | Liveness proves process response only. Readiness performs an actual authenticated database/schema/extension read; failures are 503 without raw driver details. Secret/config failure prevents startup. Connect/statement/body bounds are explicit; no promised end-to-end SLO, memory cap or hard thread-kill deadline. |
| W12-ENG1 | Compose isolates DB to its private network and binds API to 127.0.0.1. Files supply secrets, the API runs non-root/read-only with a tmpfs, capability drop and one worker, named DB volume persists across normal down/up. Reusing a volume must not silently reset data; bootstrap is insert-only and rejects conflicting fixtures. |
| W12-ER1 | Check API success/refusal, two-tenant isolation, duplicate/extra fields, SQL parameterization, source tampering, revocation, cache scope/expiry/outage, rate/admission/cancellation cleanup, stream frames, OpenAPI, readiness and DB persistence/role privileges. Real Docker/PostgreSQL CI plus server smoke are mandatory before promotion; local doubles are not integration proof. |

Question/decision ledger: user-visible scope is supplied by Path.md. The concrete
demo choices above fit that scope and are reversible engineering decisions.
Public hosting, TLS/OIDC provider, backup/restore objectives, real embedding/model
quality, production traffic/latency targets, distributed cache/rate semantics and
operational owner are unassigned future deployment decisions, not prerequisites
for this local synthetic teaching build. No automatic actions or model training.

Implementation reads this revision before code. Rule-to-test evidence and exact
release identities are recorded in content/reviews/week-12-content-review.md and
candidate CI; no completion result is implied by this pre-implementation contract.
