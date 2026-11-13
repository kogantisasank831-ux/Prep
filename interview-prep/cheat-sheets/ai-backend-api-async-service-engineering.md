---
layout: "week"
status: "approved"
version: "1.0.0"
last_reviewed: "2026-11-11"
imported_on: "2026-11-13"
source_repository: "kogantisasank831-ux/transformer-explainer"
source_commit: "cdd45b6b0c08c5d88a626e4d16853abdf285f08d"
source_path: "AI_Data_Science_Interview_Cheat_Sheets/Batch_10_AI_Engineering_Platform/37_AI_Backend_API_Async_Service_Engineering_Cheat_Sheet.md"
header_context: "Interview cheat sheets"
back_label: "Cheat sheets"
back_url: "/cheat-sheets/"
toc_heading: "Cheat-sheet sections"
pagination_label: "Cheat sheets hub"
pagination_url: "/cheat-sheets/"
title: "AI backend, API, and async-service engineering interview cheat sheet"
description: "Interview revision for AI service contracts, APIs, async work, queues, idempotency, security, overload, observability, and recovery."
summary: "Revise HTTP and job contracts, async concurrency, queues, delivery semantics, idempotency, backpressure, transactions, inference gateways, security, and recovery."
permalink: "/interview-prep/cheat-sheets/ai-backend-api-async-service-engineering/"
kicker_primary: "Interview revision"
kicker_secondary: "Batch 10 · AI backend"
current_label: "Revision guide"
alternate_label: "Cheat sheets hub"
alternate_url: "/cheat-sheets/"
---

**Target roles:** AI Engineer, ML Engineer, Agentic AI Engineer, Backend Engineer for AI, Senior/Lead Data Scientist<br>
**Use:** coding rounds, API design, inference gateways, RAG/agent services, reliability reviews, and system-design interviews<br>
**Interview rule:** start with the consumer contract, workload, latency budget, consistency, failure behavior, and security boundary. Choosing FastAPI, a queue, or `async def` is not an architecture.

## 1. Thirty-second revision

- A production AI endpoint is a software service around a probabilistic component. Its contract must define inputs, outputs, errors, limits, version, identity, authorization, and observability.
- Use synchronous request/response when work reliably finishes inside the client timeout. Use an asynchronous job when work is long, variable, resumable, or independently retried.
- Python `asyncio` provides cooperative concurrency for waiting-heavy work. It does not make CPU/GPU computation parallel; blocking the event loop delays every coroutine on that worker.
- Bound concurrency at scarce dependencies. Unlimited tasks merely move overload to a database, model server, vector store, or vendor API.
- Timeouts need a total deadline and smaller per-hop budgets. Propagate cancellation and clean up in `finally`; do not swallow `CancelledError`.
- Retries are safe only for transient failures and replay-safe operations. Use exponential backoff, jitter, attempt/deadline limits, and idempotency.
- Delivery through a broker is usually at least once in practice. Make consumers idempotent and acknowledge only after the durable effect is complete.
- Backpressure, admission control, rate limits, quotas, queue bounds, and load shedding protect useful work during overload.
- Keep routes thin: validate/authorize at the boundary, put use-case logic in a service layer, isolate infrastructure adapters, and make domain logic testable.
- Streaming improves time to first result but not necessarily total latency. Define disconnect, cancellation, partial-output, moderation, and billing behavior.
- Authentication answers “who”; authorization answers “may this identity perform this action on this resource?” Recheck tenant ownership at every data/tool boundary.
- Operate with correlation IDs, structured logs, metrics, traces, SLOs, runbooks, progressive rollout, and rollback—not logs alone.

## 2. Service contract before framework

Write a short contract:

> For **actor A** and **tenant T**, accept **request R vN**, return **response S** or **documented error E**, within **latency/deadline D**, at **load L**, with **consistency C**, **idempotency I**, and **audit/retention policy P**.

Clarify:

- caller: browser, backend, batch job, agent, or external partner;
- request rate, bursts, concurrency, payload/token distribution, and batch size;
- p50/p95/p99 latency, time to first token, total deadline, and availability;
- sync, streaming, webhook, polling, or queued-job interaction;
- schema evolution, optional fields, defaults, units, and maximum sizes;
- authentication, scopes/roles, tenant and resource ownership;
- duplicate requests, retries, ordering, cancellation, and partial results;
- data classification, retention, deletion, residency, and audit needs;
- model/prompt/index/tool version returned for reproducibility;
- overload and dependency-failure behavior.

Do not expose an internal model function directly as a public API. The stable product contract and replaceable model runtime have different change rates.

## 3. HTTP and API design essentials

### Resources, methods, and status

- `GET` reads and should be safe; `PUT` replaces and is intended to be idempotent; `PATCH` partially updates; `POST` creates or invokes work and is not automatically idempotent.
- Use `200` for a successful response, `201` for created resources, `202` for accepted asynchronous work, and `204` for success without a body.
- Distinguish invalid syntax/schema (`400`), unauthenticated (`401`), unauthorized (`403`), absent resource (`404`), conflict (`409`), semantic validation (`422` when adopted), rate limit (`429`), and server/dependency failures (`5xx`).
- Return a stable machine-readable error code, safe message, correlation ID, and field details. Do not leak stack traces, prompts, credentials, or internal hosts.

### Contract quality

- Describe schemas with a pinned OpenAPI version supported by the toolchain.
- Validate type, length, range, enum, cross-field rules, content type, and total body size.
- Prefer cursor/keyset pagination for changing or large datasets; define ordering and cursor lifetime.
- Version incompatible behavior deliberately. Additive fields still need clients that ignore unknown fields.
- Define a request ID and an idempotency key separately: the first traces an attempt; the second identifies one logical operation.
- Store an idempotency record atomically with request fingerprint, outcome/status, and expiry. Reject key reuse with materially different input.
- Use optimistic concurrency through a version/ETag for conflicting updates when suitable.

### Long-running and streaming work

For asynchronous work:

1. `POST /jobs` validates and durably records intent;
2. return `202` with job ID and status location;
3. a worker claims the job idempotently;
4. `GET /jobs/{id}` exposes state and safe progress;
5. cancellation is a state transition, not merely killing a process;
6. terminal output has explicit retention and authorization.

For server-sent events, WebSockets, or streamed HTTP, define event schema, heartbeats, reconnect/resume, ordering, terminal/error events, buffer limits, proxy timeouts, client disconnect, and whether partial output is committed.

## 4. Clean service boundaries

A practical dependency direction is:

`route/controller → application service → domain policy → ports/interfaces → adapters`

- **Route:** parse protocol, authenticate, validate, call one use case, translate errors.
- **Application service:** orchestration, transaction boundary, idempotency, authorization policy calls.
- **Domain:** deterministic rules and entities independent of HTTP, queues, and databases.
- **Repository/client port:** narrow interface for persistence or remote systems.
- **Adapter:** SQL, object storage, model gateway, vector DB, broker, or vendor implementation.

Pydantic or equivalent boundary models are useful for wire validation. Do not allow transport models or ORM objects to become the entire domain model. Dependency injection should make boundaries explicit and tests replace dependencies; it should not conceal global mutable state.

## 5. Async, threads, processes, and accelerators

| Work | Appropriate starting point | Important caveat |
|---|---|---|
| Network/database waits | `asyncio` with async clients | Every library on the path must avoid blocking the loop |
| Blocking I/O library | bounded thread pool | Threads and connection pools still need limits |
| CPU-heavy Python | process pool, native/vectorized code, or worker service | Serialization and process memory can dominate |
| GPU inference | specialized model server/batcher | Request coroutine is not the GPU scheduler |
| Durable long task | broker plus workers | Broker delivery does not make business effects exactly once |

Key concepts:

- A coroutine runs until it awaits; a task schedules it on an event loop.
- Use structured concurrency such as `TaskGroup` when child lifetimes belong to a parent.
- A semaphore bounds admission but does not create capacity. Coordinate it with client pools, worker count, and downstream limits.
- Apply total deadlines. Per-call timeouts that each reset can exceed the user deadline.
- Preserve cancellation. Cleanup may be shielded only when a small critical action must finish.
- Avoid fire-and-forget tasks without ownership, exception collection, shutdown handling, and durability.
- An `async` route that calls blocking inference, file I/O, DNS, or a synchronous database client still blocks.

### Executable bounded-concurrency pattern

This standard-library example proves that at most `limit` workers enter the scarce section while preserving input order:

```python
import asyncio
from collections.abc import Awaitable, Callable, Sequence
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")


async def bounded_map(
    items: Sequence[T],
    worker: Callable[[T], Awaitable[R]],
    *,
    limit: int,
) -> list[R]:
    if limit < 1:
        raise ValueError("limit must be positive")

    semaphore = asyncio.Semaphore(limit)

    async def run_one(item: T) -> R:
        async with semaphore:
            return await worker(item)

    async with asyncio.TaskGroup() as group:
        tasks = [group.create_task(run_one(item)) for item in items]
    return [task.result() for task in tasks]


async def example() -> None:
    active = 0
    maximum_active = 0

    async def worker(value: int) -> int:
        nonlocal active, maximum_active
        active += 1
        maximum_active = max(maximum_active, active)
        await asyncio.sleep(0)
        active -= 1
        return value * value

    result = await bounded_map([3, 1, 2, 4], worker, limit=2)
    assert result == [9, 1, 4, 16]
    assert maximum_active <= 2


asyncio.run(example())
```

Production code must additionally define per-item/total timeouts, cancellation semantics, partial-failure policy, telemetry, and the downstream's true safe concurrency.

## 6. Queues, retries, and workflow recovery

### Queue when

- processing exceeds an interactive deadline;
- work needs durable retry or independent scaling;
- burst absorption is valuable;
- producer and consumer lifecycles differ;
- fan-out or scheduled execution is required.

Do not queue merely to hide a slow design. A queue adds lag, duplicate delivery, ordering questions, poison messages, schema evolution, and operational state.

### Delivery and idempotency

“Exactly once” is an end-to-end business property, not a broker slogan. A common safe consumer:

1. receives message with stable operation ID;
2. checks or atomically claims an idempotency record;
3. performs the business transaction;
4. writes an outbox event in the same transaction if another message is required;
5. acknowledges after durable success;
6. treats replay as the already-recorded outcome.

Choose ordering key and partition carefully. Global ordering limits scale. A dead-letter queue is evidence for diagnosis and controlled replay—not a disposal bin.

### Retry decision

Retry timeouts, temporary unavailability, throttling, and some optimistic conflicts when the operation is replay-safe. Do not blindly retry validation, authorization, permanent-not-found, deterministic model/input errors, or resource exhaustion without changed conditions.

Use:

- exponential backoff plus jitter;
- maximum attempts and total deadline;
- server `Retry-After` when provided;
- circuit breaking and concurrency reduction during dependency failure;
- retry budgets so retries do not amplify an outage;
- observable attempt count and terminal reason.

## 7. Transactions, state, cache, and consistency

- Keep database transactions short; never hold a row lock across model or network calls.
- Use an outbox to atomically record a state change and event intent, then publish asynchronously.
- A saga coordinates multi-service actions with explicit compensations; compensation is business logic, not a database rollback.
- Cache only with a key that includes every value affecting the result: tenant, authorization visibility, model/prompt/index version, parameters, and input hash.
- Define TTL, invalidation, stampede control, negative caching, and behavior when cache is unavailable.
- Store conversation or workflow state with optimistic versioning/checkpoints when concurrent turns are possible.
- Distinguish source of truth, derived index, cache, and trace store. They have different recovery and deletion rules.

## 8. AI inference gateway concerns

An inference gateway may provide:

- stable provider-neutral request/response contract;
- authentication, per-tenant quota, rate and token limits;
- model routing/fallback under an approved policy;
- request validation and maximum context/output;
- batching/admission and overload rejection;
- prompt/model/config release identity;
- content/tool policy enforcement;
- token, latency, cost, cache, and quality telemetry;
- streaming normalization and cancellation.

Avoid silent fallback to a weaker or differently governed model. Record the actual model/runtime used. Bound input and output tokens before admission; a request-rate limit alone does not control LLM compute.

## 9. Security and multi-tenancy

- Use workload identity or short-lived credentials; keep secrets out of code, images, logs, prompts, and traces.
- Authenticate at ingress and authorize at the resource, retrieval, cache, conversation, and tool boundary.
- Scope database queries by tenant in a fail-closed way; test cross-tenant negative cases.
- Validate destinations for URL-fetching tools to reduce SSRF; restrict schemes, DNS/IP ranges, redirects, and egress.
- Treat pickle and untrusted model/artifact formats as code-execution risks.
- Enforce tool schemas and policy outside the model. The model may propose an action; a deterministic control authorizes it.
- Apply size, time, recursion, token, tool-call, and spend budgets against denial-of-wallet attacks.
- Minimize sensitive telemetry and protect trace access and retention.

## 10. Observability, SLOs, and overload

Track separately:

- **service:** request rate, success, error classes, p50/p95/p99, saturation;
- **queue:** depth, age of oldest item, enqueue/claim/complete, retries, DLQ;
- **dependency:** pool utilization, timeouts, circuit state, vendor limits;
- **AI:** input/output tokens, time to first token, model time, finish reason, fallback;
- **business:** accepted/completed/abandoned jobs and valid outcome rate.

Propagate a trace/correlation ID across HTTP, broker, database, retrieval, model, and tools. Do not use high-cardinality user text as metric labels.

During overload, reject early with a documented retry signal, prioritize critical classes, cap queues, shed optional work, and preserve health endpoints. Scaling reacts after saturation; it does not replace admission control.

## 11. Framework and library map

| Need | Common options | Interview-level distinction |
|---|---|---|
| Python API | FastAPI/Starlette, Django, Flask | Async support and generated schema do not replace architecture |
| Validation/serialization | Pydantic, dataclasses, Protobuf | Wire contract versus internal domain model |
| HTTP clients | HTTPX, aiohttp | Pool limits, deadlines, retries, streaming |
| App server | Uvicorn/ASGI servers | Worker/process model and graceful shutdown |
| Background jobs | Celery, Dramatiq, RQ, ARQ | Broker, delivery, scheduling, workflow, async support |
| Messaging | Kafka, RabbitMQ, cloud queues | Log/stream versus broker/queue semantics and ordering |
| Cache/state | Redis, database, object store | Correctness, durability, eviction, tenant-safe keys |
| Telemetry | OpenTelemetry plus a backend | Vendor-neutral signals still need schema and sampling |

Pin versions and verify maintained status, license, failure semantics, and operational fit. Do not combine three retry layers or three queues without one owner for the resulting behavior.

## 12. Failure modes and debugging

| Symptom | Likely causes | First evidence |
|---|---|---|
| Latency rises with traffic | unbounded concurrency, pool/GPU saturation, queueing | in-flight, pool wait, queue age, accelerator metrics |
| Event loop stalls | blocking library or CPU work | loop lag, stack/profile, slow-task logging |
| Duplicate external action | replay without idempotency | operation ID, attempt trace, transaction/outbox record |
| Retry storm | broad retry policy, synchronized backoff | attempts per request, dependency errors, `Retry-After` |
| Job stuck “running” | lost lease/worker death/no recovery | heartbeat, claim expiry, broker ack, worker termination |
| Cross-tenant result | missing scope in query/cache/retrieval | authorization decision, cache key, data lineage |
| Memory grows | unbounded queue/tasks/buffers or leaked clients | heap/task count, open connections, payload/token size |
| Stream stops halfway | proxy timeout, disconnect, worker restart | stream events, cancellation, ingress/server logs |

## 13. Rapid interview questions

**1. Does `async def` make inference faster?**<br>
No. It lets a worker make progress while awaiting nonblocking I/O. GPU/CPU throughput needs batching, parallel execution, model optimization, or more capacity.

**2. Semaphore versus rate limiter?**<br>
A semaphore caps concurrent in-flight work. A rate limiter caps starts or consumed quota over time. A system often needs both.

**3. Why idempotency if the client promises not to retry?**<br>
Networks, proxies, workers, and clients can lose responses or retry. The server must make duplicate logical operations safe.

**4. When use `202 Accepted`?**<br>
When work is durably accepted but not complete. Return a job resource and define polling/webhook, cancellation, retention, and terminal states.

**5. How do you avoid retry amplification?**<br>
Retry only transient replay-safe operations, enforce attempt/deadline and retry budgets, add jitter, respect backoff signals, and avoid stacked retries.

**6. What is backpressure?**<br>
A mechanism that slows, rejects, or bounds producers when consumers/dependencies lack capacity, preventing uncontrolled queues and collapse.

**7. Why not use FastAPI background tasks for every long job?**<br>
In-process tasks share the web worker lifecycle and generally lack durable claim/recovery. Durable, long, or independently scaled work belongs in an external job system.

**8. Readiness versus liveness?**<br>
Readiness controls whether the instance should receive traffic. Liveness asks whether it should be restarted. A slow dependency should not automatically create restart loops.

## 14. Lead-level case: multi-tenant document-analysis API

**Prompt:** Design an API that analyzes uploaded contracts with OCR, retrieval, an LLM, and optional human approval.

Strong answer:

1. Define actors, document size/types, tenants, sensitivity, interactive versus batch SLA, volume, retention, and approval risk.
2. Create an upload session using short-lived object-storage access; validate type/size and malware policy before processing.
3. `POST /analyses` records immutable document/version, requested policy, idempotency key, tenant, and release identity; return `202`.
4. Publish via an outbox; workers run bounded stages with leases/checkpoints and stage-specific retry rules.
5. Store source, extracted text, chunks/index, outputs, evidence/citations, model/prompt versions, and audit trail with separate lifecycle rules.
6. Authorize every job/status/result/download; tenant-scope cache and retrieval; restrict outbound tools.
7. Gate high-risk findings or actions through human approval. A model never directly approves a contract.
8. Track queue age, stage latency/failure, OCR quality, grounded accuracy, cost, approval/override, and stale-index/version rates.
9. Load-test representative page/token distributions; canary code/model/prompt changes; replay a frozen evaluation set.
10. Define deterministic fallback: safe partial result, manual queue, or failure with retriable state—never invented completion.

Call out trade-offs: synchronous preview versus complete job, early page streaming, per-document isolation, GPU batching versus tenant latency, and deletion across derived artifacts.

## 15. Final checklist

- [ ] Consumer, schema, errors, version, limits, and identity are explicit.
- [ ] Sync/async/streaming choice follows deadlines and recovery needs.
- [ ] Event-loop work is nonblocking; CPU/GPU and blocking I/O are isolated.
- [ ] Concurrency, pools, queues, tokens, and spend are bounded.
- [ ] Total deadlines, cancellation, retries, jitter, and retry budgets align.
- [ ] Logical operations and message consumers are idempotent.
- [ ] Transactions, outbox, leases, acknowledgements, and replay are defined.
- [ ] Authentication, authorization, tenant isolation, egress, and secrets fail closed.
- [ ] Cache/state keys include tenant and release-dependent inputs.
- [ ] Logs, metrics, traces, SLOs, alerts, runbooks, canary, and rollback exist.
- [ ] Tests cover contracts, concurrency, duplicates, timeouts, overload, and cross-tenant denial.

## Primary references

- [Python documentation — Coroutines and Tasks](https://docs.python.org/3/library/asyncio-task.html)
- [FastAPI documentation — Concurrency and async/await](https://fastapi.tiangolo.com/async/)
- [FastAPI documentation — Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [OpenAPI Specification](https://spec.openapis.org/oas/)
- [IETF HTTP Semantics, RFC 9110](https://www.rfc-editor.org/rfc/rfc9110)
- [Apache Kafka documentation — Design](https://kafka.apache.org/documentation/#design)
- [Celery documentation — Tasks](https://docs.celeryq.dev/en/stable/userguide/tasks.html)
- [OpenTelemetry documentation](https://opentelemetry.io/docs/)
- [Google SRE Book — Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)

**Evidence boundary:** APIs and framework defaults change. Validate the pinned runtime, broker, database, ingress, client, and failure behavior with contract, integration, load, and security tests before production use.
