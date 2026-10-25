---
layout: week
week: 12
phase: 3
status: approved
version: 1.0.1
last_reviewed: 2026-10-25
estimated_hours: 8
permalink: /weeks/week-12/beginner/
title: "Run your assistant through a local API"
description: Learn how a question reaches a guarded assistant through FastAPI, PostgreSQL, containers and a documented request, with clear checks for identity and failure.
summary: Build a small local service you can restart and demonstrate, then explain async waiting, vector storage, safe caching, streaming and health checks.
kicker_primary: Deploying the RAG service
kicker_secondary: From a Python call to a running local application
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-12/
---

## A colleague wants to call your assistant

Until now, you have usually run a Python command yourself. You know which files it uses and when to run it. A colleague's application needs a repeatable way to send a question and receive a result while your assistant is already running.

An API gives the two programs that agreement. Your program becomes the server; the calling program is a client. FastAPI receives the HTTP request and passes the accepted question to your guarded assistant. PostgreSQL keeps source records and permissions after the application process restarts.

The practical build is a local demonstration with synthetic invoice text. It uses the real guarded core from Week 11 and actual PostgreSQL/pgvector storage. The responder is scripted, so you can learn the service without buying model access or downloading weights. The [main lesson]({{ '/weeks/week-12/' | relative_url }}) explains the deeper transaction, cancellation and deployment trade-offs.

| Time | Work | Small success to show |
| --- | --- | --- |
| Hour 1 | Follow one request and its credential | Explain who chose the tenant |
| Hour 2 | Understand waiting and source storage | Identify the database read in the flow |
| Hour 3 | Read caching, rate and streaming examples | Predict a hit, a 429 and an incomplete stream |
| Hour 4 | Read configuration and container files | Locate settings, secret mounts and persistent data |
| Hours 5–6 | Start the supplied local stack | Run the smoke command and open API documentation |
| Hour 7 | Try a failure and inspect the tests | Explain a refusal or readiness failure |
| Hour 8 | Rehearse the project demonstration | Present the working path and its remaining limits |

Use this as an alternative eight-hour route through the same week. Revisit [Week 1's API material]({{ '/weeks/week-01/beginner/' | relative_url }}) or [Week 11's security lesson]({{ '/weeks/week-11/beginner/' | relative_url }}) when a boundary feels unfamiliar.

The [Week 12 assessment]({{ '/assessments/week-12/' | relative_url }}) draws 10 balanced questions from a bank of 100, with explanations and browser Python checks.

## Start with a question envelope

Your client sends a POST request to `/v1/ask`. The body is JSON:

```json
{"question": "What are the invoice payment terms for CW-1000?"}
```

The server answers with a small public record. It includes a new request ID, an answered/refused status, answer text, citation labels and whether validated computation was reused from the internal cache. Exact quotation and source permission still matter after the question crosses HTTP.

An HTTP status and an answer status describe different things. A 200 response can contain a deliberate refusal because no allowed evidence could be returned. A 503 describes an unavailable service/dependency path or full admission capacity. A client should preserve that distinction instead of displaying every 200 as “correct.”

The body accepts only `question`. A tenant or principal field is rejected. The raw parser also checks received bytes, duplicate keys, valid UTF-8, nesting, nonblank text and decoded length. The published limits are 4,096 raw bytes and 1,000 question characters. A three-second read deadline prevents a body from being awaited indefinitely on this path.

**Pause and predict:** If a client adds `"principal_id": "admin"`, should the server use it? It should reject the extra field. Identity has a different entry point.

## Let the credential choose identity

The demo creates two independent bearer tokens. A token is a secret value the client presents in an `Authorization` header. The configured North token maps to North's analyst; the South token maps to South's analyst.

That mapping creates the trusted context passed to source policy checks. A document's text or the question's wording cannot change it. An incorrect token returns 401 before the server reads the body or asks the database for sources.

Authentication and authorization remain separate. The token identifies the synthetic caller. Each document version still has an approved state and explicit readers. Two callers named `analyst` in different tenants remain different scopes.

This adapter is suitable for the bounded local exercise. It does not provide user registration, password recovery, a token issuer or a public login system. The credential files are loaded at startup; rotation needs a restart and, for a database password, a matching database change.

**Pause and predict:** Could a valid North token read South's invoice by putting “South” in the question? The source predicate still uses the trusted North context.

## Understand where the data lives

PostgreSQL is the persistent database service. One table stores source-version policies: tenant, document, version, readers, approval state and protected pins. Another stores the chunks and their vectors, linked to those policies.

A vector is a list of numbers used for similarity comparison. The pgvector extension adds vector storage and distance operators to PostgreSQL. Keeping policies and vectors together makes this first service easier to run than introducing an additional vector database.

The teaching encoder uses deterministic token hashing into 32 numbers. It requires no trained model. You can inspect its output locally:

```python
from labs.week_12.store import embedding

first = embedding("CW-1000 invoice terms")
second = embedding("cw-1000 INVOICE terms")
assert len(first) == 32
assert first == second
assert embedding(" ") == ()
```

Those vectors demonstrate storage and search mechanics. Hash collisions and word overlap limit the quality; the encoder does not understand meaning like a trained embedding model might. A matching source hash also does not decide whether the invoice fact is true.

Before vector ranking, the repository filters the tenant and current reader grants, checks representations against protected pins, and excludes known unsafe findings. Only the remaining chunk IDs enter the candidate query. It uses an exact scan over that bounded set, with no approximate index.

Up to twelve candidates then reach the actual Week 11 assistant. That core still builds bounded evidence and validates exact selected quotes. Missing a useful source at the earlier candidate stage can still harm the answer, so a future retrieval change needs evaluation.

**Pause and predict:** Why is filtering only the final displayed answer too late? A denied source could already have entered retrieval statistics, context or another processing step.

## Notice the difference between waiting and computing

When the endpoint sends a database request, it must wait for a response. An async database call can yield that waiting time to the event loop, allowing another ready request to progress.

Calling a blocking function inside `async def` does not automatically change the function. The service therefore uses Psycopg's actual async connection for database I/O. Each source snapshot owns its connection and closes it when finished.

The guarded assistant's Python computation is synchronous. The API sends it to a thread through an explicit bounded worker task. This avoids running that work directly inside the endpoint, but does not promise multicore speedup or let the server kill an arbitrary Python thread.

Only two expensive request pipelines are admitted per process. Extra work receives a 503 busy response instead of accumulating without a bound. If a waiting client cancels, its computing thread can continue; its admission slot is retained until that work really ends. This is why request cancellation and worker completion need separate tests.

The thread/admission mechanics are already implemented. For this week, be able to find the `finally` block and explain who returns a slot on normal success, failure and cancellation.

**Pause and predict:** If a caller stops waiting while its thread is still running, is the compute capacity free? That work still occupies capacity until it finishes.

## Check permissions again before release

Suppose the first read permits North's invoice. An administrator then revokes the grant while the assistant prepares its result. Returning the old success without checking would use stale authority.

The service reads a new database snapshot after computation. It compares the complete selected source representations and policies with the earlier snapshot. A difference produces the common refusal. This also covers sources considered for the result even if the final answer omitted one of their quotes.

A new transaction matters: a repeatable-read transaction is intentionally a consistent earlier view. A second query within that same transaction need not show a change committed afterward. The lab closes the first snapshot and obtains a fresh one for the release check.

The boundary remains limited. A late check cannot erase a source already read, or cover every change that happens after the final check. It is useful local evidence, without a distributed atomic-revocation promise.

**Pause and predict:** Would a perfectly quoted sentence necessarily be safe to return after its source grant changes? Current permission still needs to allow that return.

## Reuse answers carefully

A cache stores reusable work for a short time. If North asks the same question again under the same selected sources and configuration, the service can reuse its fully validated assistant result.

The key includes tenant, principal, question identity, selected source/policy fingerprint and context configuration. South's identical question therefore uses another key. A hit gets a fresh request ID for the new execution.

The internal cache has at most 32 entries and a fifteen-second monotonic expiry. Reading an entry does not extend that expiry. Refusals are not stored; shutdown clears the cache.

Both database snapshots still happen on a hit. The cache saves the middle Python computation, rather than bypassing current source checks. If the database is unavailable, the request receives a dependency failure. The cache does not become an undocumented stale-answer fallback.

| Situation | Expected result |
| --- | --- |
| Same caller, same question and unchanged evidence | A live validated entry may be reused |
| Same question from another tenant | A separate scoped key |
| Source/grant changes | Recompute under the new scope or refuse on a changed recheck |
| Entry expires | Compute again |
| Database fails | Report dependency unavailability |

Browser/proxy caching is separate. Public responses use `Cache-Control: no-store` while the application owns its internal bounded cache.

**Pause and predict:** Does a cache hit prove permission forever? The hit is allowed only after the current database checks on this request.

## Limit attempts as well as active work

The two-pipeline admission bound counts work happening now. A rate limit counts attempts over a time window. A client can send requests one after another and exceed the rate even if only one pipeline is busy at a time.

The default limit is twelve authenticated ask attempts per principal per sixty-second fixed window. A request that exceeds it receives 429 with a `Retry-After` hint. Authenticated malformed bodies count too, because the limiter runs before their parsing work.

Here is a smaller controlled-clock example:

```python
from labs.week_11.policy import SecurityContext
from labs.week_12.service import FixedWindow

now = [0.0]
limiter = FixedWindow(1, lambda: now[0])  # One for this example.
caller = SecurityContext("north", "analyst", "demo")
assert limiter.consume(caller) == 0
assert limiter.consume(caller) == 60
now[0] = 60.0
assert limiter.consume(caller) == 0
```

The limiter belongs to one process, as do the cache and admission slots. Four separate API workers would have four independent allowances. The supplied container therefore runs one worker. Shared enforcement and public-edge abuse protection are future design work, not features obtained automatically by starting more containers.

A fixed window also allows bursts around its boundary. Explain that behavior openly instead of describing the implementation as a smooth global request rate.

**Pause and predict:** Which response describes exhausted time-window allowance: 429 or 503 busy? It is 429. A full expensive-work slot pool uses the distinct 503 path.

## Recognize a completed stream

Streaming lets a server send a response in frames. This build uses three named events: `meta`, `result`, then `done`. Each event's data is JSON, so quotation newlines remain data rather than changing the frame structure.

The complete answer is checked before any of those frames are released. This makes it a validated-result stream. It does not generate model tokens or reveal an early partial quote while later checks are pending.

The last `done` event carries `complete: true`. If a connection stops after `meta` or `result`, the client should retain the incomplete-delivery state. A 200 streaming header alone cannot prove that the whole answer reached the caller.

Authentication, input and dependency failures occur before the stream begins, so they retain their ordinary HTTP status. The streaming endpoint is a POST with a bearer header; use an HTTP streaming client that supports that request shape. The bundled smoke command checks the actual frame sequence. An interactive documentation page may display the stream only once its buffer completes.

**Pause and predict:** Why wait for full validation before streaming the answer? Once content has reached a client, a later refusal cannot retract it.

## Keep settings and secret files out of the image

Settings describe how the process should run. A database hostname and a context size are examples. Secrets are the passwords and bearer values used to establish authority.

The setup command generates four independent secret files. It refuses to replace an existing directory and prints no token values. Compose mounts the database admin secret only where bootstrap needs it, while the API receives the restricted application password and its two caller credentials.

`Settings.from_env()` reads the documented process variables and the mounted secret files at startup. A stray `.env` file is not loaded automatically by the Python code. The Compose file's explicit environment mapping is the configuration you should inspect.

The default database address inside the API is `db:5432`. `db` is the Compose service name. Inside a container, `localhost` refers to that same container, so it would not identify the separate database service.

Secret mounts are still local files. They are not a managed encrypted vault, and host permissions remain important. On Windows, filesystem ACLs determine access; the Linux mode flags used by the setup command do not define that policy. Keep the same credential files when reusing an initialized database volume, since the stored role passwords do not regenerate automatically.

**Pause and predict:** If you replace a password file without changing the database's role password, why can readiness fail? The application and the stored credential would disagree.

## Start the supplied containers

The Compose project has three services. PostgreSQL runs continuously. Bootstrap runs once to create the isolated schema and insert the synthetic fixture. The API starts after those prerequisites succeed.

The API image contains the declared Python dependencies and application files. Its container runs as a non-root user with a read-only root filesystem and a temporary writable area. The normal setup publishes the API only on the local machine at `127.0.0.1:8000`; the database stays on the backend network.

Use the [lab README](https://github.com/kogantisasank831-ux/Prep/tree/main/labs/week_12) for environment activation and full file/configuration details. From the repository root in an activated Python environment:

```shell
python -m pip install -r requirements-dev.txt -r labs/week_12/requirements.txt
python -m labs.week_12.cli secrets
docker compose -f labs/week_12/compose.yml build api
docker compose -f labs/week_12/compose.yml up -d --no-build api
python -m labs.week_12.cli smoke
```

The secret-creation command is for the first fresh setup. Keep the existing files on later starts. Once smoke succeeds, open `http://127.0.0.1:8000/docs` on your own computer. It provides the simple interface/API documentation for the demonstration; `/openapi.json` is its machine-readable contract.

For a normal stop, use `docker compose -f labs/week_12/compose.yml down`. The named database volume remains. Bootstrap accepts identical existing fixture values and rejects conflicting ones, so restarting does not silently reset edited policy data. Removing the volume would be a separate deletion operation.

The published GitHub Pages lesson is static. It teaches and links the build; it does not host this running Python API or database. These commands create a local demo on a container runtime with Compose support. The tested command path uses Docker Compose; another runtime needs its own compatibility checks.

## Read health and tests as evidence

Liveness asks whether the process can respond. Readiness checks an actual database connection, the expected schema version, the vector extension and required table reads. A service can be alive while its database path is unavailable.

| Response or check | Meaning you can defend |
| --- | --- |
| `/health/live` responds | The process is responding |
| `/health/ready` succeeds | The tested current database path is usable |
| North gets Net 30; South gets Net 15 | Those synthetic requests used separate source scopes |
| Forged-tenant body is rejected | Question data did not choose identity |
| A changed grant causes refusal | The tested return boundary rechecked current evidence |
| The stream ends with `done` | The server emitted its complete framed result |
| A source quote is exact | Its selected text matches; source truth still needs evaluation |

Run `python -m pytest tests/test_week12_service.py -q` for the application tests. Those tests use real FastAPI and the guarded assistant with a controlled external repository. They do not prove actual PostgreSQL behavior by themselves.

The separate required PostgreSQL suite runs against the real Compose database in CI. It checks vector dimensions, scope, reader-role write denial, metadata tampering, committed revocation, cache behavior and insert-only bootstrap. The same candidate also runs real HTTP smoke and the named-volume restart path. Failed or skipped required checks block promotion.

You will see request IDs and bounded diagnostic categories rather than raw questions or credentials. The application provides logging events; collecting and retaining them requires an explicitly configured sink. A health check, a log record and an answer-quality evaluation support different claims.

## Finish with a demonstration you can explain

Rehearse this short sequence: show the OpenAPI request, ask as North, ask as South, try a forged body, inspect the completed stream, and restart the service while retaining its volume and credentials.

Then complete three exercises:

1. Find the cache key and name every scope/version input it retains. Explain why a hit still reads the database.
2. Read the cancellation test and identify when an admission slot returns. Explain why cancelling an await cannot be treated as killing its thread.
3. Propose public hosting in a short decision note. Include identity/TLS, backup and recovery, traffic targets, shared limiting/caching, model evaluation and operating ownership. Keep unknowns explicit.

For interviews, be ready to answer: Why async? Why PostgreSQL with pgvector here? What changes with multiple workers? Why does streaming start after validation? What does the new transaction establish about revocation? What does this local build still need before public use?

You finish the week when another person can follow the run instructions and you can explain both an allowed request and a failure. Keep the code, test/commit reference and a small boundary diagram or note with your project. This reaches the Phase 3 interview-demo milestone. Try the [Week 12 assessment]({{ '/assessments/week-12/' | relative_url }}) for a random paper with concept, syntax and Python questions. Week 13 adds tool calling and the permissions around actual actions.

## Read alongside the build

- [Main lesson]({{ '/weeks/week-12/' | relative_url }}) — detailed code boundaries, consistency and deployment trade-offs.
- [FastAPI async guidance](https://fastapi.tiangolo.com/async/) and [response types](https://fastapi.tiangolo.com/advanced/custom-response/) — waiting and HTTP transport.
- [Psycopg async operations](https://www.psycopg.org/psycopg3/docs/advanced/async.html) and [pgvector](https://github.com/pgvector/pgvector) — the actual storage tools.
- [PostgreSQL isolation](https://www.postgresql.org/docs/17/transaction-iso.html) — why a new read transaction matters.
- [Compose startup order](https://docs.docker.com/compose/how-tos/startup-order/) and [secret mounts](https://docs.docker.com/compose/how-tos/use-secrets/) — prerequisites and credential files.
