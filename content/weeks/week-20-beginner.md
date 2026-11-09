---
layout: week
week: 20
phase: 5
status: approved
version: 1.1.0
last_reviewed: 2026-11-09
estimated_hours: 8
permalink: /weeks/week-20/beginner/
title: "Keep the delivery desk useful when one service breaks"
description: Learn retries, waiting, timeouts, circuit breakers, backups, queues, partial failure and dead letters through five local incidents.
summary: A reliable worker retries only temporary problems, stops within a budget, labels backup results and keeps one bad job from blocking the rest.
kicker_primary: Beginner path
kicker_secondary: Five failures, finite retries and honest fallbacks
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-20/
---

## Before you start

This route is for someone new to reliability engineering. Basic Python functions, exceptions and dictionaries are enough; retries, deadlines, circuits, fallbacks, queues and dead letters are introduced with one delivery-desk example. The [Week 19 beginner route]({{ '/weeks/week-19/beginner/' | relative_url }}) helps with the safe execution boundary that this worker extends.

On your first pass, learn to classify a failure, retry only safe temporary work within a budget, reject late or malformed results, label fallbacks as degraded and keep later jobs moving after one item fails. Treat distributed circuit coordination, crash-safe queue transactions, jitter design, SLOs and capacity planning as stretch topics.

| Time | Work | A small success to show |
| --- | --- | --- |
| Hour 1 | Classify temporary and permanent failures | Choose retry or stop for five examples |
| Hour 2 | Add deadlines and finite attempt budgets | Calculate one capped backoff sequence |
| Hour 3 | Protect replay with idempotency rules | Explain why a timed-out write is different |
| Hour 4 | Trace closed, open and half-open circuits | Predict the next admitted call |
| Hour 5 | Inspect declared fallbacks | Label a fallback result as degraded |
| Hour 6 | Lease, acknowledge and requeue work | Follow one job through its states |
| Hour 7 | Continue a partial batch and inspect the DLQ | Preserve all five outcomes in order |
| Hour 8 | Run incidents, tests and practice | State what the simulator does not prove |

## Imagine a delivery desk

A desk receives five work cards. One asks an AI provider for an answer, one reads
a database, one calls a supplier API, one searches a vector store and one calls a
catalog API.

Any station may be slow or broken. A weak desk either gives up on everything or
keeps shouting the same request forever. A reliable desk asks:

1. Is this problem likely to be temporary?
2. Is repeating this exact request safe?
3. How many attempts and how much time remain?
4. Is there an approved backup that returns the right shape?
5. If this card cannot finish, can the other cards continue?
6. Where should the failed card wait for investigation?

Week 20 builds that desk as a deterministic local Python lab. Nothing contacts a
real provider, database, API, vector store or queue.

The [production version]({{ '/weeks/week-20/' | relative_url }}) explains
deadline propagation, retry amplification, circuit scope, at-least-once
delivery, idempotency and operational ownership in more depth.

The [Week 20 assessment]({{ '/assessments/week-20/' | relative_url }}) draws
10 balanced questions from a bank of 100, with explanations and browser Python
checks.

## Learn nine small ideas

| Idea | Plain meaning | Lab example |
| --- | --- | --- |
| Retry | try the same safe request again after a temporary problem | catalog API gets a second call |
| Backoff | wait longer between repeated attempts | 100 ms, then 200 ms in virtual time |
| Timeout | stop accepting a call after its time budget | database result after 250 ms is too late |
| Circuit breaker | temporarily stop calling a station that keeps failing | primary model circuit opens after two failures |
| Model fallback | use a declared backup model | secondary model returns an answer |
| Tool fallback | use a simpler compatible tool | lexical search replaces vector search |
| Queue | hold separate cards for workers | lease one job, then acknowledge it |
| Partial failure | keep independent successes when one item fails | cards four and five run after card three fails |
| Dead-letter queue | quarantine a card that needs investigation | invalid supplier result is retained safely |

## Temporary and permanent problems differ

Suppose a shop door is briefly blocked. Trying later may work. Suppose the work
card is missing the delivery address. Waiting and reading the same card again
will not add an address.

The lab treats these as temporary:

- dependency unavailable;
- rate limited; and
- response took longer than the deadline.

It does not retry a response that is missing required fields. That is a contract
problem. Code, data or configuration needs to change, or a declared backup must
be used.

**Check yourself:** would the same request probably succeed later without any
change? If no, a retry wastes time and load.

## Put a timer on the call

A worker waiting forever cannot help another card. A timeout says how long one
attempt may occupy the desk.

The database fixture returns after 250 ms, but the lab deadline is 100 ms. The
worker labels it `timeout` and does not use the late result. It tries once more,
then opens the database circuit and uses a bounded cache.

The lab only compares numbers; it does not cancel a real network call. Real code
must configure the HTTP or database client's timeout and clean up connections or
tasks when time expires.

Very short timeouts can reject healthy slow calls. Very long timeouts hold
resources. Measure the real station and choose a budget that fits the whole user
request.

## Retry with a stop sign

Immediate repeated calls can make a busy service even busier. Backoff inserts a
pause:

~~~text
attempt 1 fails -> wait 100 ms
attempt 2 fails -> wait 200 ms
attempt 3 fails -> stop
~~~

The delay is capped so it cannot grow forever, and the number of attempts is
finite. The lab advances a manual clock instead of really waiting, which keeps
tests fast and repeatable.

Real systems usually add a little randomness called **jitter**. If a thousand
workers fail together and all wait exactly 100 ms, they attack the recovering
service together again. Jitter spreads them out.

Do not retry every error. A bad password, denied permission or invalid response
will usually fail in the same way.

## Repeat only safe work

Reading the same product list twice usually has the same effect. Sending the same
purchase order twice may create two orders.

This lab's automatic retries stand for safe reads. They are not permission to
repeat a payment, email, deletion, approval or other change.

An **idempotency key** labels one exact business intent. The queue remembers the
tenant and scenario for each key. The same job replay is ignored; reusing the key
for different work is rejected.

That dictionary disappears when the program stops. A real service needs durable
idempotency records and must handle two workers arriving at the same time.

Week 19's human approval works once. If an approved write times out, first find
out whether it happened. Do not silently spend the approval again.

## Honor “try later” within a limit

The catalog API responds with a rate limit and says to retry after 300 ms. The
worker records a 300 ms virtual wait. The second primary call succeeds.

Its final state is:

~~~text
status: completed
code: recovered_after_retry
selected_dependency: catalog-api
~~~

The worker also caps the requested delay. A broken service must not be allowed to
park the job for an absurd amount of time.

## Use a circuit breaker like a safety switch

When a station fails over and over, repeated calls waste time. A circuit breaker
has three states:

| State | What happens |
| --- | --- |
| closed | calls are allowed |
| open | calls fail fast while the station gets recovery time |
| half-open | one limited probe checks whether recovery happened |

Two failures open a circuit in this lab. After the recovery interval, a
successful probe closes it. A failed probe opens it again.

Each station has its own switch. A broken vector store should not turn off the
catalog API. In a real system, teams must decide whether the switch belongs to a
host, shard, region or provider and prevent many half-open probes at once.

## Label every backup honestly

A backup is not always equal to the primary:

| Broken primary | Backup | Honest label |
| --- | --- | --- |
| primary AI model | secondary model | different model selected |
| live database | cache | data is 45 seconds old |
| vector search | lexical search | simpler retrieval method |

All three lab results are `degraded`, not normal `completed` results. They still
have useful data, but callers can see the reduced path.

The supplier API's output lacks required fields. No backup is declared. The
worker refuses to invent supplier risk and moves the card to the dead-letter
queue.

Before trusting a backup, check that it returns required fields, has acceptable
quality and can handle traffic when the primary is down.

## Give every card its own outcome

The queue accepts one card with a job ID, tenant, idempotency key and scenario. A
worker **leases** it, which means “I am responsible for this card for now.”

After processing, the worker either:

- acknowledges a completed or degraded result;
- requeues a temporary failure if a delivery remains; or
- moves a permanent/exhausted failure to the dead-letter queue.

Run all five cards and you get:

| Card | Incident | Outcome |
| --- | --- | --- |
| 1 | AI provider outage | degraded through secondary model |
| 2 | database timeout | degraded through cache |
| 3 | invalid supplier result | dead letter |
| 4 | vector-store failure | degraded through lexical search |
| 5 | catalog rate limit | completed after retry |

Card three fails, but cards four and five still run. That is **partial failure**.
Independent work continues and each result remains visible.

If card four depended on card three, continuing might be wrong. Dependencies
must be explicit; “always continue” is not a reliability rule.

## A dead-letter queue is an investigation shelf

A dead-letter queue does not fix a card. It moves the card away from normal
traffic so one poison item does not block everything.

The lab retains the job, tenant, scenario, controlled error code and counts. It
does not copy secrets, raw payloads or stack traces.

A real team must decide:

- who gets alerted;
- how long the card is retained;
- how to inspect it safely;
- what must be repaired;
- who may replay it; and
- how replay avoids a duplicate effect.

Automatically bouncing a broken card back and forth only creates a failure loop.

## Run the five incidents

From the repository root:

~~~shell
python -m pip install -r requirements-dev.txt
python -m labs.week_20.demo case --scenario llm-provider-outage
python -m labs.week_20.demo case --scenario database-timeout
python -m labs.week_20.demo case --scenario invalid-api-result
python -m labs.week_20.demo case --scenario vector-store-failure
python -m labs.week_20.demo case --scenario rate-limit-errors
python -m labs.week_20.demo batch
python -m labs.week_20.demo smoke
~~~

Look at these JSON fields:

| Field | Question it answers |
| --- | --- |
| `status` | normal, degraded or dead-lettered? |
| `code` | why did this terminal state happen? |
| `selected_dependency` | primary or backup? |
| `warnings` | what reduction should the caller know? |
| `attempts` | what was called, delayed and stopped? |
| `delivery_count` | how many times did the queue deliver the job? |

Run the 39 focused checks:

~~~shell
python -m pytest tests/test_week20_reliability.py -q
~~~

They prove the boundaries as well as the happy paths: strict input rejection,
finite retry delays, `Retry-After` cap, timeout classification, circuit recovery,
fallback selection, duplicate suppression, lease rules, partial continuation,
minimal dead-letter records and deterministic CLI output.

Try the [Week 20 assessment]({{ '/assessments/week-20/' | relative_url }}) for a
random paper covering temporary and permanent failures, safe retries, circuit
breakers, honest fallbacks, queue transitions and dead-letter handling.

## What this small lab cannot prove

- A manual clock does not cancel real sockets or database work.
- Scripted responses do not measure provider, model or retrieval quality.
- The queue and circuits disappear when the Python process ends.
- One-threaded code does not test races between workers or half-open probes.
- Exact backoff has no production jitter.
- An in-memory idempotency key does not create exactly-once effects.

Use the lab to understand decisions. Use real clients, brokers, concurrency,
metrics, fault injection and load tests before claiming production reliability.

For deeper reading, see AWS on
[timeouts, retries, backoff and jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/),
Microsoft on the
[Circuit Breaker pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker),
Amazon SQS on
[dead-letter queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html)
and Google SRE on
[cascading failures](https://sre.google/sre-book/addressing-cascading-failures/).

