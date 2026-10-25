---
layout: week
week: 12
phase: 3
status: approved
version: 1.0.1
last_reviewed: 2026-10-25
estimated_hours: 8
permalink: /weeks/week-12/
title: "Deploy the guarded assistant as a service"
description: Put the RAG assistant behind FastAPI, persist scoped sources in PostgreSQL and pgvector, and test its configuration, streaming, health, cache and admission boundaries.
summary: Follow one invoice question from a local HTTP client to authenticated scope, database retrieval, validated output and a repeatable container demonstration.
kicker_primary: Deploying the RAG service
kicker_secondary: A working function becomes a demonstrable service
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-12/beginner/
---

## The assistant works. Can someone else run it?

You can answer the invoice question from a Python script. Now a colleague wants to call it from another program, restart it tomorrow and inspect a failure without opening your notebook. Those requests introduce a service boundary: an agreed request, a running process, persistent state and an observable response.

The useful starting point is the assistant you already have. [Week 11]({{ '/weeks/week-11/' | relative_url }}) established trusted scope, permitted evidence and a closed quote contract. This week carries those decisions through HTTP and a real database. The result is a local FastAPI backend, PostgreSQL with pgvector, generated file-backed credentials, a Compose setup and an API documentation page. The responder remains a scripted formatter. You can demonstrate deployment behavior without a GPU, a provider key or a model download.

Bring the Python/API ideas from Week 1, source lineage from Week 6, retrieval/context from Weeks 7–8, evaluation from Week 9 and the operational/security boundaries from Weeks 10–11. The [beginner version]({{ '/weeks/week-12/beginner/' | relative_url }}) follows the same build with smaller steps.

| Time | Focus | Evidence to retain |
| --- | --- | --- |
| Hour 1 | Read the request/response and identity boundaries | One valid request and a rejected forged-tenant request |
| Hour 2 | Trace async database work and synchronous computation | A cancellation/admission explanation |
| Hour 3 | Follow persisted policies, chunks and vectors | A two-tenant retrieval comparison |
| Hour 4 | Examine revalidation, caching and rate limits | A revoked cached-source case and a 429 response |
| Hours 5–6 | Build and run the containers | Successful readiness, API documentation and HTTP smoke |
| Hour 7 | Read the failure and integration tests | A storage permission negative and a restart demonstration |
| Hour 8 | Present the service and defend its limits | A short interview demo and a deployment decision note |

Use the supplied lab as the working reference; the eight hours are for understanding, running, changing and explaining it. The full implementation does not need to be retyped.

The [Week 12 assessment]({{ '/assessments/week-12/' | relative_url }}) draws 10 balanced questions from a bank of 100, with explanations and browser Python checks.

## Give the caller a small contract

What should a client have to know? It needs a server address, a credential and a question. It should not need the Python classes used inside retrieval.

The request body is deliberately familiar:

```json
{"question": "What are the invoice payment terms for CW-1000?"}
```

`POST /v1/ask` returns a JSON envelope containing `request_id`, `status`, `answer`, `citation_ids` and `cache_hit`. An answered result contains permitted exact quotations. A refused result uses Week 11's common refusal text. Internal reasons, candidate counts and denied-source identifiers stay out of this public contract.

The server generates the request ID. It supports correlation across this execution; it supplies no permission. The two outcomes also answer different questions: HTTP 200 means the request reached a normal application outcome, while `status: refused` means the assistant did not produce an allowed evidence answer.

| Interface | Purpose | What the caller must interpret |
| --- | --- | --- |
| `POST /v1/ask` | A complete JSON answer/refusal | The public status and citation labels |
| `POST /v1/ask/stream` | A framed, validated-result stream | The result frame and final `done` marker |
| `GET /health/live` | A cheap process response | The process is responding |
| `GET /health/ready` | A real database/schema/extension check | This dependency path is currently usable |
| `GET /openapi.json` and `/docs` | API contract and interactive documentation | How to call this local service |

Both ask endpoints consume the same strict raw envelope. Received body bytes are counted as they arrive, with a 4,096-byte bound and a three-second body-read deadline. Decoding then enforces the existing 1,000-character question, duplicate-key, nesting and UTF-8 rules. The declared OpenAPI model describes the body; the raw parser supplies the additional representation checks. A `Content-Length` assertion cannot authorize a larger actual body.

**Checkpoint:** Should a client treat a 200 refusal as a successful answer-quality result? It should record the normal transport outcome and the refusal separately. Next, decide which identity is allowed to ask.

## Establish identity before reading the question

The local demo has two generated bearer credentials. One maps to North's analyst, and the other to South's analyst. Authentication creates the trusted `SecurityContext`; body text never chooses its tenant or principal.

The credential is carried in the `Authorization: Bearer …` header. An invalid or missing credential returns 401 before the body parser or database runs. The server compares the configured token values without returning them. Supplying `tenant_id`, `principal_id` or an action field in the JSON produces a schema rejection.

This is an intentionally small authentication adapter. It has no signup, account recovery, tenant-membership database or token-issuing endpoint. Credentials are read at startup; changing their files requires a restart. A public deployment would need an accepted identity/session design, TLS, rotation and an owner. Merely copying this local token scheme onto a public host would leave those decisions unanswered.

The distinction matters inside the database too. A signed-in analyst still needs a grant on a particular source version. The protected catalogue retains that decision, and the application database role cannot update it.

**Checkpoint:** If North and South both use the name `analyst`, can that name alone select a document? The source identity must still include tenant and version. Follow that identity into storage.

## Persist the source and its permission together

PostgreSQL holds two related sets of records. A document-policy row identifies a tenant, document and version, with source digest, approval state, readers and representation bindings. A chunk row carries its normalized source representation, embedding and embedding-contract identifier. Foreign keys connect the records; the chunk's identity remains scoped to its tenant.

Using pgvector keeps vector values in that same database. It avoids introducing a second service merely to demonstrate vector storage. The extension supplies the `vector(32)` column and cosine-distance operator used by this lab; it does not supply application authentication or decide which rows a principal may read.

The initial read joins chunks to current approved reader policies. Parameters carry the trusted tenant and principal:

```sql
SELECT c.representation
FROM week12_chunks c JOIN week12_documents d
  USING (tenant_id, document_id, document_version)
WHERE d.tenant_id = %s
  AND d.state = 'approved'
  AND %s = ANY(d.readers);
```

The placeholders are bound by Psycopg. The question does not become SQL, and the responder never proposes a query. This excerpt shows the permission predicate; the implementation additionally selects policy fields, checks the embedding contract and bounds the source batch.

Two database identities have different jobs. The bootstrap process creates the isolated schema and inserts the synthetic fixture. The API's `rag_reader` role receives SELECT on the owned tables. Its requests also use read-only transactions. These permissions reduce the consequences of an application mistake; they do not turn a shared database credential into row-level tenant authentication. The fixed scoped query remains a boundary that needs tests.

**Checkpoint:** Would a database password shared by the API prove which end user owns a request? It identifies the application's database role. End-user scope still comes from the trusted HTTP adapter.

## Check the representation before vector ranking

An authorized row can still contain a changed representation. The repository reconstructs bounded source objects, checks their current policy and full representation pins, and excludes known unsafe body findings. Only those eligible chunk IDs enter the vector query.

That order preserves last week's central invariant: a denied, tampered or known attack-bearing chunk should not occupy the candidate budget before a valid source is considered. The candidate query uses a materialized eligible set and an exact cosine scan. There is no approximate-nearest-neighbor index in this small teaching build.

The vectors themselves use a deterministic 32-dimensional token-hashing baseline. Tokens add signed counts to hash-selected positions, then the vector is normalized. You can inspect the contract without a running database:

```python
from math import isclose
from labs.week_12.store import EMBEDDING_CONTRACT, embedding

vector = embedding("CW-1000 invoice payment terms")
assert EMBEDDING_CONTRACT == "token-hash32-l2/v1"
assert len(vector) == 32
assert isclose(sum(value * value for value in vector), 1.0)
assert embedding(" ") == ()
```

This is actual persisted vector search, with a deliberately simple feature generator. Hash collisions and word overlap limit its retrieval quality. It is not a trained semantic embedding model. An empty query vector produces no candidates rather than asking cosine distance to interpret a zero vector.

At most twelve vector candidates proceed to the actual Week 11 guarded assistant. That assistant still performs its bounded retrieval/context and exact-quote validation. The new database candidate stage can lose evidence before that later processing begins; a good reranker cannot recover a source that never arrived. Treat a future embedding or candidate-depth change as an evaluation change, using Week 9's source-dependent cases rather than assuming the database made quality better.

The repository reads at most 256 scoped chunks before pin validation. This design makes the ordering easy to verify, but it reads more source data than a large indexed service would. Scaling it would require a reviewed storage/index contract that preserves authorization and integrity checks, followed by workload and recall measurements.

**Checkpoint:** Does adding an ANN index automatically preserve these guarantees? Its filtering and recall behavior must be evaluated under the intended scope. The present exact eligible-set scan avoids making that untested claim.

## Let the event loop wait for I/O

An async endpoint can pause while a database operation is waiting. During that pause, the event loop can serve another ready task. Writing `async def` does not change the behavior of a blocking call placed inside it.

Here is a small scheduling example. `sleep(0)` is only an explicit yield; it is not a database benchmark:

```python
import asyncio

async def waiting_stage(name):
    await asyncio.sleep(0)
    return name

async def main():
    values = await asyncio.gather(
        waiting_stage("request-a"), waiting_stage("request-b")
    )
    assert values == ["request-a", "request-b"]

asyncio.run(main())
```

In the service, Psycopg's asynchronous connection performs database I/O. Each snapshot owns and closes its short-lived connection. A connection is not shared accidentally across requests or transactions. A connection pool would be a possible later optimization with its own lifetime, saturation and reset rules.

The existing guarded assistant is synchronous Python work. The service sends that bounded computation to a thread so it does not run inline in the endpoint. This does not establish CPU parallel speedup or make arbitrary Python code interruptible. Pure Python work still has the runtime's execution constraints; a heavy model or CPU pipeline needs measured scheduling and a suitable worker boundary.

The two source reads also have a dependency: the later read checks whether the earlier computation is still returnable. Running them together would defeat that purpose, even though async tools can schedule independent operations concurrently.

**Checkpoint:** If an async function calls a synchronous SDK directly, has the SDK become nonblocking? The adapter's actual I/O behavior decides that. Now account for what happens when the caller leaves.

## Keep admission until the work actually ends

This process admits two expensive request pipelines at a time. A third request receives 503 with a retry hint instead of joining an unbounded queue. Admission is separate from how many requests are allowed during a minute.

Cancellation introduces a subtle case. A caller can cancel its await while a Python thread continues computing. Returning the slot immediately would allow another request to start, and repeated cancellations could create more active work than the advertised bound.

The service shields the worker task from cancellation of that await and keeps a strong task reference. If the request exits while the worker is still running, a completion callback returns the slot when the worker actually finishes. Ordinary success, database failure and computation failure also release their slot. Shutdown waits for owned worker tasks, clears process-local state and closes the repository.

This is bounded ownership, not a hard thread-kill mechanism. A replaced adapter that never returns would keep its slot. The supplied computation is constrained by the small corpus and context limits; a future remote call needs a real I/O deadline, and an untrusted or unbounded computation needs a different isolation strategy.

Database connects use a three-second connect setting; statements have a two-second server-side timeout, and each snapshot await has a four-second application timeout. These bounds cover different pieces of work. They are not a measured end-to-end latency promise or a process memory cap.

**Checkpoint:** Why does the cancellation test check that a third request remains busy after the first caller cancels? It verifies the lifetime of actual work rather than only the lifetime of an HTTP await.

## Read a new snapshot before returning

Imagine the first database read permits an invoice. While the guarded assistant is computing, the trusted administrator removes the analyst's reader grant. A second read inside the same repeatable-read transaction could still show the earlier view.

The repository therefore uses a read-only repeatable-read transaction for each individual snapshot, then closes it. After computation or a cache lookup, the service obtains a new snapshot in a new transaction. It compares a fingerprint of the complete selected source representations and policies, including their order and grants. A changed snapshot produces the common refusal and removes the corresponding cache entry.

This check is conservative: a relevant catalogue change can reject a response even when some returned text would remain allowed. It also has a time boundary. It cannot erase a source already read, detect a later change after the final check, or prove atomic revocation across a database, provider and network client. Define those consistency requirements explicitly before a real deployment needs stronger guarantees.

The real PostgreSQL integration test changes and commits a grant during the computation callback. That is important evidence: two in-memory dictionaries alone would not demonstrate the transaction behavior.

**Checkpoint:** Would keeping a transaction open for the whole answer automatically make a later permission read current? Its isolation level and snapshot rules decide what it sees. A new transaction makes the intended visibility check explicit here.

## Cache validated work within its scope

Two identical questions can have different answers for different principals or source versions. A question-only key would merge those cases.

The local cache key includes tenant, principal, the exact question digest, the selected snapshot fingerprint and the context configuration. The pipeline version participates in the question identity. A hit receives a fresh request ID, so it does not pretend to be the earlier execution.

The cache retains at most 32 fully validated successful results, with a fifteen-second monotonic expiry. Reading an entry does not extend its expiry. Refusals are not inserted. Shutdown clears it; there is no durable history or cross-process cache.

Most importantly, a hit still performs the first scoped vector snapshot and the new return-time snapshot. It saves the intermediate Python assistant computation. It does not avoid database reads, keep the service available during a database outage, or justify a claimed speedup without measurement. A database failure returns 503 even when an older answer exists in memory.

| Event | Expected cache behavior |
| --- | --- |
| Same principal, question, source snapshot and configuration | A live entry can be reused after current checks |
| Another tenant or principal | A different key |
| Changed selected source representation or grant | New identity or a refusal during recheck |
| Expired entry | Recompute; do not extend it on a read |
| Database unavailable | Fail the dependency path; do not serve stale success |

HTTP responses separately use `Cache-Control: no-store`. The server's deliberate internal cache and a browser/proxy cache have different owners and rules.

**Checkpoint:** Does a correct key make a cached answer permanently authorized? Permission is a current read decision, so the hit still needs its checks.

## Distinguish rate from concurrency

A rate limiter counts admitted attempts over time. An admission limiter bounds work currently in flight. Neither quantity can be inferred from a count of registered users.

The demo allows twelve authenticated ask attempts per principal in a sixty-second fixed window. Counting happens before body parsing, so malformed authenticated attempts consume allowance too. An exhausted allowance returns 429 and `Retry-After`. North's allowance is separate from South's.

Use a controlled clock to see the boundary without waiting:

```python
from labs.week_11.policy import SecurityContext
from labs.week_12.service import FixedWindow

clock = [0.0]
limiter = FixedWindow(2, lambda: clock[0])  # Two for this example.
identity = SecurityContext("north", "analyst", "demo-request")
assert limiter.consume(identity) == 0
assert limiter.consume(identity) == 0
assert limiter.consume(identity) == 60
clock[0] = 60.0
assert limiter.consume(identity) == 0
```

A fixed window permits a burst around a window boundary. The limiter also lives in one process. Starting four independent workers would multiply the effective allowance and the two-slot admission capacity, and each would have its own cache. Shared enforcement would need an accepted coordination design. Invalid credentials are rejected before this per-principal limiter; a public edge would need its own abuse controls.

The container consequently runs one API worker. Uvicorn also has a connection/concurrency setting of sixteen; that server setting is a separate protective layer with its own refusal behavior, not the two-pipeline application contract.

**Checkpoint:** Is a 429 interchangeable with a 503 busy response? They describe different constraints and should lead to different diagnosis.

## Stream a result only after it is safe to release

Streaming changes when bytes reach a client. That timing becomes a security decision if an early quote is emitted before the remaining output or current access has been checked.

This endpoint computes and validates the complete result first. Then it sends three Server-Sent Events: `meta`, `result` and `done`. The `result` event contains the same public answer envelope as the JSON endpoint. JSON escaping keeps newlines inside source text from becoming new SSE control lines.

The frame shape is:

```text
event: meta
data: {"request_id":"…","mode":"validated-result"}

event: result
data: {"request_id":"…","status":"answered","answer":"…","citation_ids":["S1"],"cache_hit":false}

event: done
data: {"request_id":"…","complete":true}
```

This is a validated-result stream, with no model token generation. It deliberately trades early content for validation before release. A future token stream needs an explicit policy for partial output, validation and irreversible disclosure; it cannot inherit a full-answer guarantee automatically.

Authentication, body, admission and dependency failures occur before streaming headers. Once a stream has started, a connection can still fail. Clients should require `done` before treating it as complete. There is no replay cursor, durable job or promise to finish after a disconnected client. The generator checks disconnection between its bounded frames. A POST/bearer stream also needs an HTTP streaming client that supports that contract; the browser's basic GET-oriented EventSource interface is not a direct replacement.

**Checkpoint:** Does receiving a 200 streaming header prove the client received the full answer? The completion marker supplies an additional piece of transport evidence.

## Configure the process without baking in secrets

Configuration answers questions such as which database host to use and how large context may be. Credentials prove authority and need a more restricted handling path.

`Settings.from_env()` reads documented process variables and validates their shape/range at startup. It reads passwords and bearer values from bounded files. It does not automatically load an arbitrary `.env` file. Compose supplies its explicit environment mapping and mounts only the secrets each service needs.

| Setting | Default/local meaning |
| --- | --- |
| `W12_DB_HOST`, `W12_DB_PORT` | `db`, `5432` inside the service network |
| `W12_DB_NAME`, `W12_DB_USER` | `rag_demo`, `rag_reader` for the API |
| `W12_DB_PASSWORD_FILE` | A mounted application-password file |
| `W12_NORTH_TOKEN_FILE`, `W12_SOUTH_TOKEN_FILE` | Mounted credential files for the two demo identities |
| `W12_CONTEXT_CHARS` | 1,400 serialized characters, validated within 2–1,400 |
| `W12_REQUESTS_PER_MINUTE` | 12, process-local and per authenticated principal |
| `W12_CACHE_SECONDS` | 15, within the lab's bounded configuration range |

The setup command generates four independent secrets: a database bootstrap password, a restricted application password and the two bearer values. It creates a fresh directory and refuses to overwrite it. Values are not printed, embedded in images, checked into Git or placed in smoke-command arguments.

Compose secrets are file mounts with explicit per-service access. This local arrangement is not an encrypted managed vault. Host filesystem permissions still matter, and Linux mode bits do not define Windows NTFS access policy. Keep the host directory private and retain the same credential files when reusing an initialized database volume.

A bad or missing secret prevents application startup. A changed file does not update credentials already loaded in memory. Database-role rotation also needs a coordinated database change; replacing one mounted file alone cannot change a stored password.

**Checkpoint:** Why can deleting and regenerating local password files break an otherwise healthy persisted database? The stored role password and the newly supplied password would no longer agree.

## Package the running boundary

An image contains the application and its declared dependencies. A container is a running instance with configuration and mounts. PostgreSQL's named volume supplies persistence beyond an individual container's writable layer.

The Compose project starts a database, a one-shot bootstrap process and the API. It waits for the database health check, then for successful bootstrap, before starting the API. The API subsequently has its own readiness check. A started process and a ready dependency path remain different states.

The API runs as a non-root numeric user, with a read-only root filesystem, a temporary writable mount, dropped Linux capabilities and no-new-privileges. The bootstrap process gets the administrative database secret; the API does not. Only the API's host port is published by the normal Compose file, on `127.0.0.1:8000`. PostgreSQL remains on the backend network. The CI override temporarily adds a loopback database port for runner-side integration tests.

The API joins a frontend bridge for host port publishing and the internal backend for database communication. The database does not join the normal frontend. These are local network boundaries, not a public ingress/TLS architecture or a verified operating-system egress allowlist.

The Dockerfile pins Python 3.13.12; the database image pins a pgvector/PG17 versioned tag. Candidate CI records the built image ID and verifies the real stack. A production release would additionally require its image provenance, vulnerability policy, immutable promotion, recovery and ownership decisions.

**Checkpoint:** Where does `localhost` point from inside the API container? It refers to that container. `db` is the service name used for the PostgreSQL connection.

## Run the demonstration from a clean checkout

Use a Python environment and a Linux-container runtime with Docker Compose. The [lab README](https://github.com/kogantisasank831-ux/Prep/tree/main/labs/week_12) contains activation steps, file responsibilities, configuration and troubleshooting. These commands run from the repository root after activating the environment:

```shell
python -m pip install -r requirements-dev.txt -r labs/week_12/requirements.txt
python -m labs.week_12.cli secrets
docker compose -f labs/week_12/compose.yml build api
docker compose -f labs/week_12/compose.yml up -d --no-build api
python -m labs.week_12.cli smoke
python -m pytest tests/test_week12_service.py -q
```

Generate secrets once for a fresh local setup. The smoke command waits for readiness within a bounded startup window, then checks the real HTTP routes, North/South terms, cache reuse, invalid credentials, a forged body, a known injection refusal and the completed stream. Its own client stays on a local HTTP address and does not follow redirects with credentials.

Open `http://127.0.0.1:8000/docs` locally for the API interface. Supply a generated demo token only to that local interface's authorization control. `/openapi.json` exposes the schema directly. The scripted smoke is useful when an interactive documentation client buffers SSE output.

Ordinary `docker compose -f labs/week_12/compose.yml down` removes these containers and their network while retaining the named database volume. Bootstrap is insert-only: identical fixture rows are accepted, but a conflicting policy or representation aborts rather than silently resetting the database. Keep the secret files with that volume. Removing the volume is a separate data-deletion operation.

GitHub Pages publishes these lessons and the static assessments. It cannot run this Python backend or PostgreSQL. The backend remains your local demonstration; publishing the lesson does not create a public API or incur a hosted database service.

## Verify the layers and diagnose a failure

The local service tests use the real FastAPI transport and guarded assistant with a controlled repository boundary. They verify application contracts, but do not establish PostgreSQL behavior. The separate required integration suite uses actual PostgreSQL/pgvector, and container CI runs the real HTTP smoke before and after the named-volume restart path.

| Observation | Useful interpretation | Evidence to check next |
| --- | --- | --- |
| 401 | Credential missing or invalid | Header and configured identity adapter; avoid printing the secret |
| 400 / 413 / 415 / 408 | Body schema, received size, media type or read deadline | The specific input boundary, before retrieval |
| 429 | This principal exhausted its local time-window allowance | Retry hint and limiter scope |
| 503 `busy` | Expensive-work admission is full | In-flight work and cancellation ownership |
| 503 dependency failure | The current database path failed | Readiness, network/role/schema and bounded diagnostics |
| 200 with refusal | A normal guarded outcome without an allowed answer | Internal restricted reason, eligible evidence and context budget |
| `live` 200, `ready` 503 | The process responds while a dependency is unusable | The database path; liveness alone is insufficient |
| Stream ends before `done` | Incomplete delivery | Connection/cancellation; do not invent a completed result |

Request IDs correlate responses and bounded application events. Routine event fields omit raw questions, source bodies, tokens and driver messages. Access logging is disabled in the supplied server command. A response-prepared event describes preparation of headers/result, not proof that every streamed byte reached a client. Configure the application's logging sink deliberately if you need to collect its informational records; a logger call alone does not create a retained audit system.

The demonstration's health checks cannot prove source truth, retrieval quality or immunity to prompt injection. Retain the security and evaluation tests alongside the deployment tests. A green container is only one piece of the argument.

## Present the service as an interview project

Demonstrate the system in a small sequence: open its schema, ask as North, ask as South, show a refused forged request, inspect a validated stream, and explain the persistent data and restart path. Keep a test/commit reference with the demonstration so “works” refers to a specific candidate.

Try these independent exercises:

1. Lower the trusted context setting to two characters in a separate test configuration. Show a common refusal and explain why the responder is skipped. Restore the normal setting afterward.
2. Use a controlled clock to show the fixed-window boundary and absolute cache expiry. Explain which behavior would change with additional workers.
3. Read the committed-revocation PostgreSQL test. Identify which transaction owns each read and why an in-memory replacement would be weaker evidence.
4. Propose a real-model substitution. Write down the embedding/version migration, evaluation population, provider deadline, partial-stream policy and credentials/egress decisions it would require. Keep those as reviewed design work rather than enabling an untested provider call.

| Interview question | A defensible answer should include |
| --- | --- |
| Why does async matter here? | Database waiting yields; synchronous computation uses an explicit bounded worker boundary. |
| Why one PostgreSQL service? | Relational policy/source data and pgvector fit this local build; separate storage adds consistency work that is not required yet. |
| Why check cache hits against the database? | The key identifies a scope/snapshot, while authorization can change before the current return. |
| Why stream after full validation? | It preserves the product's release boundary; it intentionally provides no early token stream. |
| What does cancelling an await stop? | It can stop the waiting request; it does not automatically terminate its Python thread. |
| What remains before public hosting? | Identity/TLS, traffic and latency objectives, shared limits/cache policy, backups/recovery, image/security gates and an operating owner. |

Your deliverable is a reproducible local service, an allowed/refused request comparison, real storage/HTTP evidence, and an honest explanation of the remaining deployment decisions. That completes the Phase 3 demonstration milestone. Week 13 introduces tool calling, where arguments and actual actions need their own authority checks. Use the [Week 12 assessment]({{ '/assessments/week-12/' | relative_url }}) to check the service concepts and Python syntax before presenting the build.

## Sources and further reading

- [FastAPI async guidance](https://fastapi.tiangolo.com/async/) — waiting, synchronous calls and execution boundaries.
- [FastAPI lifespan](https://fastapi.tiangolo.com/advanced/events/) and [streaming responses](https://fastapi.tiangolo.com/advanced/custom-response/) — application lifetime and response transport.
- [Psycopg asynchronous operations](https://www.psycopg.org/psycopg3/docs/advanced/async.html) — connection/cursor ownership and async database usage.
- [pgvector](https://github.com/pgvector/pgvector) — vector storage, distance operators and exact versus approximate search.
- [PostgreSQL transaction isolation](https://www.postgresql.org/docs/17/transaction-iso.html) — visibility across reads and transactions.
- [Docker Compose startup order](https://docs.docker.com/compose/how-tos/startup-order/), [secrets](https://docs.docker.com/compose/how-tos/use-secrets/) and [networks](https://docs.docker.com/reference/compose-file/networks/) — the container boundary used in this build.
- [Python task cancellation and threads](https://docs.python.org/3.13/library/asyncio-task.html) — what cancellation and `to_thread` actually control.
