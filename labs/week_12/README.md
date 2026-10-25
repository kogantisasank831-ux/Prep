# Week 12: local guarded RAG service

Run the real Week 11 guarded assistant through FastAPI and PostgreSQL/pgvector.
The included five source records and two identities are synthetic. Token-hash
embeddings and a scripted quote responder require no GPU/provider/model download.
This is a local interview demonstration; GitHub Pages hosts the lessons only.

## Start from the repository root

Use the declared Python 3.13.12 environment and a Linux-container Docker Engine
with Compose. Create a virtual environment with `python -m venv .venv`, then
activate it using `.venv\Scripts\Activate.ps1` in PowerShell or
`source .venv/bin/activate` in bash. The application is also checked locally on
Python 3.12; the container/CI runtime is pinned to 3.13.12.

```shell
python -m pip install -r requirements-dev.txt -r labs/week_12/requirements.txt
python -m labs.week_12.cli secrets
docker compose -f labs/week_12/compose.yml build api
docker compose -f labs/week_12/compose.yml up -d --no-build api
python -m labs.week_12.cli smoke
```

The setup creates `.runtime/week12-secrets` exclusively. Generate once for a
fresh setup; retain the same files with an initialized volume. Neither secret
values nor passwords appear in the command arguments or output. The application
image is shared by `api` and the one-shot `bootstrap`; build `api` first as above.
Bootstrap accepts identical existing fixtures and aborts on conflicting source
or policy data. It does not reset an edited database.

Open `http://127.0.0.1:8000/docs` locally. Its Authorize control accepts one of
the generated `north_token`/`south_token` values; supply it only to this local
interface. `/openapi.json` provides the schema. The smoke client exercises real
HTTP, including the completed stream, without printing a credential or following
redirects with one. A documentation UI may buffer SSE display.

The commands are verified with Docker Compose in CI. A Podman/other Compose
provider needs its own compatibility check; no claim is made that every
runtime implements the same mounts/network behavior. On Windows use Linux
containers. Host ACLs determine secret-file access; Linux mode bits do not
establish NTFS isolation. Keep the generated host directory private. Files are
readable within explicitly granted containers, including their non-root users.

## API contract

| Route | Contract |
| --- | --- |
| `POST /v1/ask` | Bearer header; exactly `{"question":"..."}`; returns request_id, answered/refused status, answer, citation_ids and cache_hit |
| `POST /v1/ask/stream` | Same request; complete validation first, then JSON-data SSE events meta/result/done; require done for complete delivery |
| `GET /health/live` | Cheap process response |
| `GET /health/ready` | Real authenticated database/schema/extension/table-read check; 503 when unavailable |
| `/docs`, `/openapi.json` | Local API interface and machine-readable specification |

Received raw body limit: 4,096 UTF-8 bytes, including JSON syntax. Question:
nonblank valid UTF-8 string, at most 1,000 characters. Duplicate/extra keys,
nonfinite constants and structural nesting over eight levels are rejected.
Valid body text remains unchanged. The service reserializes it compactly before
the Week 11 guard, so a valid boundary-size envelope is not accidentally inflated.

401 precedes body/database work. Authenticated ask attempts consume the rate
allowance before parsing: 429 with Retry-After when exhausted. Body errors use
400/413/415/408. Busy/database paths use 503 with Retry-After; unexpected
application failures use a bounded 500. A normal refusal uses 200 and the common
Week 11 refusal text. Internal reasons/counts stay out of the public envelope.
Responses include a fresh server-generated X-Request-ID and Cache-Control:
no-store. There is no broad CORS configuration, source-viewer endpoint, document
upload/admin API, model provider, action dispatcher or public deployment.

## Runtime settings and credentials

| Variable | Python default | Compose behavior |
| --- | --- | --- |
| `W12_DB_HOST` | db | Fixed db service name |
| `W12_DB_PORT` | 5432 | Database's internal port |
| `W12_DB_NAME` | rag_demo | Isolated lab database |
| `W12_DB_USER` | rag_reader | Restricted application role |
| `W12_DB_PASSWORD_FILE` | .runtime/week12-secrets/db_app | /run/secrets/db_app |
| `W12_NORTH_TOKEN_FILE` | .runtime/week12-secrets/north_token | /run/secrets/north_token |
| `W12_SOUTH_TOKEN_FILE` | .runtime/week12-secrets/south_token | /run/secrets/south_token |
| `W12_CONTEXT_CHARS` | 1400 (2–1400) | Explicit host-environment substitution |
| `W12_REQUESTS_PER_MINUTE` | 12 (1–120) | Explicit host-environment substitution |
| `W12_CACHE_SECONDS` | 15 (1–60) | Explicit host-environment substitution |

Python reads process environment; it does not automatically read a `.env` file.
For a context experiment, set `W12_CONTEXT_CHARS` in the host shell and recreate
the API with Compose so its environment changes. Clear the override and recreate
it to restore defaults. File-secret changes are read on process restart, but
database-password rotation also needs a matching database role change. The
generated bootstrap secret is available to `db`/`bootstrap`, never to `api`.
Local Compose mounts are not an encrypted vault or automatic rotation service.

## Processing and bounds

1. Authenticate the configured token into a fixed synthetic tenant/principal.
2. Apply the process-local fixed-window rate allowance and bounded body parser.
3. Acquire one of two fail-fast expensive-work slots.
4. In a read-only repeatable-read transaction, query current scoped grants,
   validate chunk/policy representations and known content findings, then perform
   exact pgvector cosine selection over those eligible IDs (maximum twelve).
5. Use the scoped snapshot/config/question identity for the bounded internal
   cache; on a miss, run the actual Week 11 guarded assistant in an owned thread.
6. Obtain a **new** database transaction/snapshot before returning, including on
   a cache hit. Changed selected source/policy data causes the common refusal.
7. Emit the public JSON or fully validated-result SSE frames.

The source read is bounded to 256 rows and the reused policy store to 64 source
versions. The 32-dimensional `token-hash32-l2/v1` encoder is a synthetic lexical
baseline. All pin/screening decisions precede the vector query. No ANN index or
semantic-model quality claim is introduced. The candidate stage can lose recall;
the later assistant cannot recover evidence it never received.

Cache: at most 32 successful validated entries, absolute monotonic TTL, complete
selected snapshot/scope/config identity, fresh request ID on reuse, clear on
shutdown. Both database snapshots still run on a hit; database failure never
serves an older success. This saves only the intermediate Python computation.
No latency benchmark or availability improvement is claimed.

Rate limiting, cache and admission are process-local. The supplied API uses one
worker; multiple workers would multiply their independent limits. Uvicorn's
separate concurrency setting is sixteen. Connect timeout is three seconds,
server statement timeout two seconds, each snapshot await four seconds and body
read three seconds. These are distinct bounds, not a measured end-to-end SLO or
memory cap. Cancellation does not kill Python threads: admission is retained
until the owned worker finishes. An unbounded replacement adapter needs a
different execution/isolation/deadline contract.

## Ownership and verification

| File | Responsibility |
| --- | --- |
| config.py | Validated settings and bounded file secrets |
| store.py | Actual async PostgreSQL I/O, scoped/pinned eligible set, vector search, immutable snapshots |
| service.py | Worker ownership, admission, TTL cache and per-principal fixed-window limit |
| api.py | Authentication, raw request/status contracts, public projection, readiness and SSE framing |
| fixtures.py / cli.py | Synthetic insert-only seed, explicit secret setup and local HTTP smoke |
| schema.sql | Versioned additive relational/vector schema |
| Dockerfile / compose.yml | Non-root API, bootstrap/database lifetimes, private backend, loopback publishing and named volume |
| LOGIC.md | Stable scoped rules and acceptance expectations |

```shell
python -m pytest tests/test_week12_service.py -q
```

That suite uses real FastAPI/guarded computation and a controlled external
repository; it is application evidence, not PostgreSQL integration proof.
`tests/test_week12_postgres.py` is a separate required integration suite that
fails unless explicitly configured for the isolated loopback database with
`W12_INTEGRATION=1`, `W12_DB_HOST=127.0.0.1`, `W12_DB_PORT=55432`. The CI-only
Compose override supplies that port. CI builds the actual image, initializes
PostgreSQL/pgvector, runs these tests and real HTTP smoke, then runs smoke again
after ordinary down/up preserves its named volume. No skipped integration gate
counts as success.

SQL scope, vector dimensions, source metadata tampering, current grants,
committed mid-computation revocation, read-only-role denial, cache changes and
insert-only/conflict-preserving bootstrap are tested against the actual database.
Pure/application tests include malformed/oversized input, status contracts,
absolute expiry, clock-zero/window boundaries, per-principal allowance,
cancellation/admission ownership, complete SSE frames and readiness failures.

Normal shutdown:

```shell
docker compose -f labs/week_12/compose.yml down
```

The named database volume and credential files remain. Bootstrap conflicts
require inspecting the intended data/version rather than deleting it to make a
test pass. Public hosting still needs its identity/TLS design, traffic/SLO and
recovery requirements, shared limiting/cache policy, image/security gates and an
operating owner. Exact quoting does not establish source truth; a return-time
snapshot cannot retract earlier reads or provide distributed atomic revocation.
The stream has no model-token generation, durable completion or replay cursor.
Application logging uses bounded metadata events; collecting INFO records and
retaining an audit history requires an explicit logging sink/configuration.
