# Week 20 reliability contracts — revision 1

Source: `Path.md` Week 20 and the Week 19 guarded-tool boundary. These rules
define a deterministic local simulator for safe read-like work. They do not
create a durable broker, cancel real sockets, distribute circuit state or make
consequential writes safe to replay.

| ID | Effective rule and acceptance |
| --- | --- |
| W20-BR1 | Treat every remote dependency as fallible. A job ends as `completed`, visibly `degraded` or `dead_letter`; arbitrary exceptions are not a public contract. |
| W20-BR2 | Process queued jobs independently. A permanent failure in one item must not abort later items in the same batch. |
| W20-FR1 | Retry only classified transient outcomes: unavailable, rate limited and deadline exceeded. Do not retry a contract-invalid response or declared permanent failure with the same request. |
| W20-FR2 | Bound retries to 1–8 attempts. Use capped exponential backoff, honor a bounded `Retry-After`, and record virtual delay instead of sleeping in the deterministic lab. |
| W20-FR3 | Enforce a per-attempt deadline before accepting response data. A response whose simulated elapsed time exceeds the deadline is a timeout even if it eventually contains valid data. |
| W20-FR4 | Keep one closed/open/half-open circuit per dependency. Open at the configured threshold, fail fast during the recovery interval, allow a recovery probe after it, close on success and reopen on probe failure. |
| W20-FR5 | Use only declared, contract-compatible fallback chains. A secondary model, bounded stale cache or lexical search result is labeled `degraded`; fallback is never silently reported as the primary path. |
| W20-FR6 | Submit jobs with a tenant-scoped semantic idempotency key. Suppress an exact replay and reject reuse of the same key for a different tenant or scenario. |
| W20-FR7 | Lease, acknowledge, requeue or dead-letter a job explicitly. Bound deliveries to 1–20; only a leased job can transition. |
| W20-FR8 | Preserve dead-letter metadata for diagnosis and controlled replay: job, tenant, scenario, controlled code, deliveries and dependency-attempt count. Do not copy arbitrary payload or exception text into it. |
| W20-DR1 | Validate dependency output against required fields before success. An HTTP-like `ok` status with missing fields is `invalid_response`, not usable data. |
| W20-DR2 | Retain one terminal `JobResult` for every accepted idempotency key, including dead-lettered work, so callers can inspect rather than duplicate work. |
| W20-SR1 | Automatic retries in this lab represent safe, idempotent reads only. Never infer permission to replay a Week 19 write, approval, message, payment or destructive action. |
| W20-SR2 | Return stable codes, dependency names, safe warnings and attempt metadata. Do not expose credentials, connection strings, raw stack traces or provider exception text. |
| W20-NFR1 | Given the same scenarios and configuration, output order, virtual delays, circuit transitions, fallbacks and dead-letter records are deterministic. No wall clock, random source, sleep, network or external service participates. |
| W20-NFR2 | Use only the standard library and the repository's pinned Pydantic runtime. Keep boundary models strict, frozen and closed to extra fields. |
| W20-ER1 | Test schema rejection, retry classification and caps, `Retry-After`, timeout handling, circuit transitions and isolation, every fallback, partial batch continuation, idempotency conflicts, queue transitions, DLQ minimization, deterministic replay and all CLI paths. |

## Required failure matrix

| Scenario | Primary behavior | Retry decision | Terminal behavior |
| --- | --- | --- | --- |
| LLM-provider outage | primary model returns unavailable twice; its circuit opens | one 100 ms virtual backoff, then stop when the circuit opens | secondary model succeeds; `degraded/fallback_used` |
| Database timeout | two responses exceed the 100 ms deadline; database circuit opens | one 100 ms virtual backoff | bounded 45-second-old cache succeeds; `degraded/fallback_used` |
| Invalid API result | nominally successful response omits `supplier_id` and `risk` | no retry because the contract will not heal by replay | first delivery enters DLQ as `invalid_response` |
| Vector-store failure | vector store is unavailable twice; its circuit opens | one 100 ms virtual backoff | lexical search succeeds; `degraded/fallback_used` |
| Rate-limit errors | catalog API returns a 300 ms `Retry-After` | wait 300 virtual ms, within the configured cap | second primary call succeeds; `completed/recovered_after_retry` |

The all-scenarios batch retains five terminal results in submission order: one
normal completion, three visible degradations and one dead letter. The invalid
API item appears before two successful later items, proving continuation after
partial failure.

## Retry classification and budgets

The retry unit is one dependency call, not a whole agent run. `unavailable`,
`rate_limited` and `timeout` are transient. `invalid_response` and
`dependency_failure` are permanent for the unchanged request. A fallback may
still follow either class when the chain declares a compatible alternative.

For attempt number *n*, deterministic delay is:

~~~text
min(max_backoff, base_backoff * 2 ** (n - 1))
~~~

For a rate limit, the worker uses the larger of that value and a bounded
`Retry-After`. Attempts and delay are both finite. Production clients should
also add randomized jitter or use a proven SDK so many workers do not synchronize
their retries. Jitter is intentionally absent here to keep exact replay evidence.

Retries belong at one deliberate layer. Retrying the same call in a client,
service, worker and broker multiplies traffic. A queue redelivery is a separate
outer budget and is used only after the dependency chain still returns a
transient failure.

## Timeout interpretation

The simulator classifies `elapsed_ms > timeout_ms` as a timeout and discards its
late data. That proves the policy branch, not real cancellation. A production
adapter must configure connection and end-to-end request deadlines in its
client, cancel or abandon work safely, release sockets/tasks and distinguish an
unknown write outcome from a confirmed failure.

## Circuit interpretation

Each dependency name owns one circuit. Occasional failure below the threshold
leaves it closed. The threshold opens it and subsequent calls fail fast until
the recovery interval. The next call becomes a half-open probe. Success closes
the circuit; failure reopens it.

The lab is sequential and process-local. Production must decide whether a
circuit is per process, endpoint, shard, tenant or region; merging unrelated
resources can block healthy traffic. Concurrent half-open probes need their own
coordination, and state transitions need metrics and alerts.

## Queue, idempotency and dead letters

The local queue models at-least-once delivery with explicit lease/ack/requeue
transitions. Its idempotency key maps `(tenant, scenario)` to one terminal
result. The key prevents duplicate processing in one process; it is not a
transactional exactly-once guarantee.

A production consumer needs a durable broker, visibility/lease renewal,
crash-safe result storage and an atomic or otherwise reconcilable relationship
between side effects and acknowledgement. Use an outbox/inbox, conditional
write or domain-specific idempotency record where needed.

The DLQ is quarantine, not deletion and not automatic correctness. Alert on new
entries, retain them under an explicit policy, diagnose the cause, repair code or
data, and redrive only with authorization and idempotency controls. Avoid a
blind replay loop that returns the same poison item to the source queue.

## Accepted limitations

- All dependencies and data are synthetic; no model, database, API, vector
  store or broker is contacted.
- Virtual elapsed time does not exercise thread, task, socket or process
  cancellation.
- Deterministic backoff has no jitter and is not a production retry client.
- Circuit and queue state vanish when the process exits and are not safe for
  concurrent workers.
- The fallback fixtures demonstrate contract checks, not semantic equivalence,
  answer quality, cache freshness policy or capacity under a real outage.
- No consequential write is automatically retried. Week 19 approvals remain
  one-use and ambiguous outcomes require reconciliation plus a fresh decision.

