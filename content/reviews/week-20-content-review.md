# Week 20 content and lab review

## Scope and disposition

Roadmap source: `Path.md`, Week 20 — Reliability and failure handling.

Candidate artifacts:

- `content/weeks/week-20.md`
- `content/weeks/week-20-beginner.md`
- `labs/week_20/`
- `tests/test_week20_reliability.py`

Version 1.0.0 is approved for candidate validation. It adds two lesson depths
and one deterministic reliability worker spanning all five required failure
simulations. It does not publish a Week 20 assessment; `ASSESSMENT_WEEKS` remains
at Week 19 and neither lesson links to a nonexistent questionnaire.

## Coverage mapping

| Roadmap requirement | Learner-facing treatment | Executable evidence |
| --- | --- | --- |
| Retries with backoff | classification, safety, attempt/time budgets, caps, jitter and retry-layer amplification | transient-only retries; exact exponential delay and cap tests |
| Circuit breakers | closed/open/half-open behavior and resource scoping | threshold, fail-fast, successful probe, failed probe and isolation tests |
| Model fallbacks | contract, quality, dependency and capacity cautions | primary model opens; secondary model returns compatible data and degraded label |
| Tool fallbacks | stale-cache and lexical-search tradeoffs | database/cache and vector/lexical scenario assertions |
| Timeout handling | attempt versus total deadline, cancellation and ambiguous-write cautions | simulated late response becomes `timeout`; late data discarded |
| Queue-based processing | lease, acknowledge, redelivery, idempotency and at-least-once limits | state-transition, duplicate, conflict and delivery-budget tests |
| Partial failure | per-item terminal result and dependency-aware continuation | invalid third job does not block fourth and fifth jobs |
| Graceful degradation | fallback identity, warnings, freshness/method visibility and SLO interpretation | three `degraded/fallback_used` results with selected dependency |
| Dead-letter queues | quarantine, alert, retention, diagnosis and controlled redrive | minimal record and permanent first-delivery DLQ tests |
| LLM-provider outage | transient primary outage and circuit opening | secondary model selected after two unavailable outcomes |
| Database timeout | two responses over the 100 ms deadline | bounded cache selected with `stale-45s` freshness |
| Invalid API result | transport success separated from data-contract validity | missing required fields; no retry; `invalid_response` DLQ |
| Vector-store failure | semantic retrieval failure and reduced retrieval mode | lexical search selected and labeled |
| Rate-limit errors | bounded `Retry-After` combined with local backoff | 300 ms virtual delay then primary recovery |

## Technical review

The implementation uses strict frozen Pydantic boundary models and standard
library control flow. `DependencyExecutor` is the single retry layer. It retries
only unavailable, rate-limited and timed-out calls, stops at finite attempt and
delay caps, and never accepts data arriving beyond the configured deadline.
Contract-invalid and permanent responses are not replayed with the same request.

Each dependency owns a separate circuit. Two failures open the default circuit;
the recovery interval transitions it to half-open for a probe, which closes on
success or reopens on failure. The lessons explicitly limit this sequential,
process-local implementation and discuss endpoint/shard/region scope and
concurrent probe coordination.

Fallbacks are an ordered declared chain, not arbitrary exception recovery. The
secondary model preserves `answer/model`, the cache exposes freshness and the
lexical tool exposes its retrieval mode. All are `degraded`, name the selected
dependency and include controlled warnings. The supplier API has no fallback;
inventing a risk value would violate the contract.

`InMemoryWorkQueue` models submit, lease, acknowledge, requeue and dead-letter
transitions with bounded deliveries. An idempotency key binds tenant and
scenario, suppresses the same replay and rejects semantic conflict. This state
is neither durable nor transactional; the lessons do not claim exactly-once
effects.

The all-scenarios batch retains input order and one terminal result per job. The
third item is permanently invalid, but later vector and catalog jobs still run.
Its DLQ record contains identifiers, controlled code and counts—not arbitrary
payload or exception text.

Automatic retries deliberately represent safe read-like work. Week 19's
approval-bound writes remain outside the loop. The lessons explain that timeout
after a consequential dispatch can be ambiguous and requires reconciliation,
domain idempotency and potentially a fresh approval.

The manual clock and scripted responses make exact failure paths reproducible.
They do not exercise socket/task cancellation, a durable broker, concurrent
workers, distributed circuits, randomized jitter, real fallback quality or
outage capacity. These limits are repeated in both lessons, lab documentation
and the production-readiness checklist.

## Source review

Primary and first-party technical material accessed on 2026-11-06:

- AWS Builders' Library for timeout scope, transient retries, capped exponential
  backoff, jitter, idempotent side effects and avoiding multiplied retry layers;
- AWS Well-Architected reliability guidance for retry classification, finite
  attempts, backoff/jitter, testing and observability;
- Microsoft Azure Architecture Center for closed/open/half-open circuit behavior,
  recovery probes, monitoring and resource differentiation;
- Amazon SQS documentation for receive-count policy, DLQ diagnosis, retention,
  alerting and controlled redrive; and
- Google SRE guidance for overload, cascading-failure prevention and degraded
  responses instead of retry amplification.

## Executed local checks

Local environment: Python 3.12.14. The declared CI environment is Python 3.13.12.

- All 39 focused Week 20 schema, retry, deadline, circuit, fallback, queue,
  idempotency, partial-failure, DLQ and CLI tests pass.
- Ruff lint passes for all 82 files in the configured CI scope, and Ruff format
  reports all 82 files already formatted.
- Strict mypy passes for all 82 configured files with a clean isolated cache.
- The configured regression suite passes 1,841 tests, including every published
  assessment bank and the focused Week 20 worker suite.
- Week 13 actual-SQLite smoke passes all 12 observations.
- Week 14 controller smoke passes all eight observations.
- Week 15 graph smoke passes all ten observations.
- Week 16 memory/context smoke passes all 12 observations.
- Week 17 supervisor/specialist smoke passes all ten observations.
- Week 18 evaluation smoke passes eight baseline assertions over all 28 cases.
- Week 19 safety-gateway smoke passes 12 assertions over all seven scenarios.
- Week 20 reliability-worker smoke passes 16 assertions over all five scenarios.
- Front matter, reciprocal lesson links, code-fence balance, YAML parsing,
  JavaScript syntax, UTF-8 reads, whitespace, CI wiring, Week 20 lesson
  navigation and absence of a premature Week 20 assessment link pass locally.

Candidate CI, the real PostgreSQL/pgvector job, main promotion and live Pages
verification were then required before publication could be recorded below.

## Publication verification

Publication verification completed on 2026-11-06 for implementation commit
`fc48e9cf8864748351b2db850f07ff73b8842877`.

- Candidate CI run `42252595960` passed on Python 3.13.12: Ruff lint and format,
  strict mypy, all 1,841 tests, the Week 13-20 CLI smokes, and the real
  PostgreSQL/pgvector permission, revocation and restart checks.
- Lease-protected promotion to `main` completed, and main CI run `42253153613`
  passed the same Python and PostgreSQL/pgvector jobs.
- Pages deployment run `42253153501` completed successfully.
- The production lesson renders the heading “Design failure as a controlled
  state, not a surprise”; its circuit states render as native prose rather than
  raw Mermaid source. The beginner lesson renders “Keep the delivery desk useful
  when one service breaks,” and the depth links resolve reciprocally.
- The live sidebar and Week 20 roadmap card each expose the Week 20 lesson. The
  card has one lesson link and zero questionnaire links; the production lesson,
  beginner lesson and roadmap have zero Week 20 assessment links.
- Browser checks found no page-origin warnings or errors on the production
  lesson, beginner lesson or roadmap.

GitHub Pages will host only the static lessons. The manual clock, scripted
dependencies, circuits, queue, retry worker and CLI run locally; no public Python
service, provider, database, vector store, broker, credential or procurement
action is deployed.

