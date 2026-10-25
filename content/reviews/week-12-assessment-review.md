---
week: 12
status: reviewed
version: 1.0.0
last_reviewed: 2026-10-25
generation_surface: Codex in ChatGPT Work
publication_authorization: User accepted Week 12 assessment as the next step in the established test-push-publish workflow
---

# Week 12 assessment review

## Baseline and accepted scope

Base main is f40671042d9373ce2bfac5243f28ac0dcde17b6a; its tree is
492dc3c1f78f59c6b6676d702c4d7cd4fe02d788. Only root AGENTS.md applies.
Its Finance App design references do not describe this curriculum; there is
no Design directory. Path.md Week 12, plan.md, the approved main/beginner
lessons, the runnable Week 12 lab and the user's weekly assessment requirement
define this bounded addition. Existing untracked QA work is preserved and no
subagents were used.

Inspected the preceding bank/page/tests/review, shared paper/scoring verifier,
Python runner and browser worker, Week 12 settings, transport, service,
repository, Compose and bootstrap, relevant lesson text, layout, navigation,
README, dependency pins and CI. No service architecture, runtime dependency,
database schema, shared engine, worker or scoring-policy change is required.

Added the bank, assessment page, regression module and this review. Existing
changes are limited to navigation, README, the new test's lint/type targets and
assessment links in the two lessons, whose patch versions become 1.0.1. The
lesson body is otherwise preserved exactly. All 241 other previously tracked
files are byte-identical to the base, including earlier lessons/banks, source
data, labs, dependencies and shared assessment assets.

## Coverage and exercise boundaries

There are 100 distinct authored prompts: 30 single-choice, 20 multiple-correct,
15 matching, 15 short syntax and 20 Python coding questions. Every item has a
topic, difficulty, answer key and explanatory feedback. Coding tasks state
complete local input/output/failure contracts and five public executable checks.
Each can be solved independently of which other questions appear in the paper.

| Learning goal | Assessment evidence |
| --- | --- |
| Service contracts | Transport versus answered/refused outcome, fixed public fields, strict question-only input and server correlation |
| Authentication and input | Trusted bearer scope before application parsing/database work, actual bytes, body deadlines, strict JSON and compact serialization |
| Async ownership | Cooperative I/O, bounded offloading, shield limits, retained tasks, original errors/cancellation and completion-based slot release |
| PostgreSQL and vectors | Coherent snapshots, new return-time transaction, parameterized values, reader privileges, pin/screening checks before vector IDs, exact distance ordering |
| Synthetic encoder | Fixed dimensionality, signed features, normalization, zero-vector absence and no trained semantic-quality claim |
| Scoped cache | Complete snapshot/configuration identity, exact question digest, current rechecks, fresh request IDs, absolute TTL, LRU, capacity and success-only insertion |
| Rate and admission | Scoped fixed windows, valid zero clock, ceiling-rounded retry, boundary bursts, two application slots and separate server concurrency |
| Streaming | Preflight validation, JSON-safe framing, ordered meta/result/done, correlation, incomplete delivery and no token/replay claims |
| Configuration and secrets | Exact integer grammar, secret representation, startup loading, no implicit Python dotenv, least-needed mounts and coordinated rotation |
| Docker and operations | Image/container/volume/network distinction, service DNS, loopback API, private ordinary database, startup dependencies and insert-only seed conflicts |
| Verification limits | Controlled repository versus real PostgreSQL versus runnable HTTP/container evidence; static Pages versus separately started local backend |

These are small standard-library tasks, not a portable copy of the complete
backend. Question serialization receives an already-decoded value and is not
a replacement strict raw parser. Chunk collection models early byte accounting
without a network deadline or memory-sandbox claim. Configuration and header
shape checks confer no authentication or authorization.

The vector-normalization exercise explicitly accepts a broader bounded numeric
domain than token counts. It uses hypot to preserve tiny nonzero values rather
than letting squared terms underflow to a false zero result. Candidate ordering
receives IDs that have already been verified; it does not independently verify
policy. The snapshot exercise defines a normalized dictionary schema rather
than silently copying the lab's dataclass adapter; complete fields and ordered
chunks remain covered while policy/reader order is normalized.

Cache helpers separate key identity, copy ownership, lookup expiry/recency and
insertion policy. They do not replace the lab's two current database reads.
The fixed-window function represents one already-scoped caller, with state
storage and global coordination outside its boundary.

Async exercises use the existing runner's top-level-await support. They need
no Python threads, FastAPI, psycopg, Docker, network or repository imports in
the browser. Revalidation orders callbacks; its read callback must actually
provide new transaction freshness. Slot release follows a Future/Task's actual
completion, while the service must separately retain strong task ownership.
These components do not kill a running thread, retract past reads or create
atomic distributed revocation. Test fixtures retrieve their own deliberately
created exceptions in cleanup even when a submitted implementation fails.

The seed merge is an independent deep-copied in-memory model of insert-only
conflict semantics, not a database transaction or schema/role bootstrap.
The public projection assumes an already guarded result. SSE completion checks
only the stated markers, not all answer fields or event authenticity. The
full implementation remains the separate local Week 12 lab.

## Technical review and executed local checks

Reviewed all authored keys, matching pairs, syntax spellings, coding domains
and checks against the approved lesson and actual code contracts. Checked
scope filtering before truncation, metadata/grant fingerprint coverage, Unicode
and serialized-byte boundaries, falsey values, absolute expiry, zero clock,
async failure identity, completion ownership, framing and nonmutation.
No unresolved actionable technical finding is supported after the checks.
This is a technical item review, not independent human psychometric calibration
or a fabricated project-owner rubric score.

Executed with local Python 3.12.14, Node 24.22.1 and the repository's pinned
pytest/Ruff/mypy:

- 1,150 targeted pytest cases pass, including 64 new assessment cases, all
  twelve assessment suites, existing Week 7–12 application/lab regressions
  and Week 1 service checks.
- All 20 references pass all five checks; all 20 starters score zero; each of
  20 distinct plausible wrong implementations loses marks.
- Five composed checks cover config/4096-byte handoff, vector scope and changed
  cache identity, TTL/LRU/fresh public responses, fixed-window/SSE completion
  and actual async ownership around a changed final snapshot.
- Shared JavaScript verification passes 1,000 balanced reproducible papers,
  all-question reachability, every objective key, exact/partial/pending scoring,
  stale source/result rejection and saved-attempt restoration.
- Ruff lint/format and strict mypy pass on 27 scoped source files. Declared
  dependency consistency, JavaScript syntax and whitespace checks pass.
- Liquid/Markdown/layout rendering and four local HTTP paths pass. Both lesson
  structures and their original content are preserved except declared links;
  241 other tracked files remain byte-identical.

The selected suite excludes the pre-existing Windows-only comparison module,
so this is not an unrestricted whole-repository pass. No local Docker/PostgreSQL
execution is claimed: those tools are unavailable in this workspace. The
unchanged mandatory CI stack job supplies that real dependency/container/HTTP
evidence on the exact candidate before main promotion. Candidate/run identities,
post-promotion CI/Pages and live browser evidence are retained in publication QA;
success is not asserted in advance here.

## Sources and remaining limits

Primary documentation rechecked on 2026-10-25 alongside the repository contracts:

- [Python asyncio tasks, cancellation, timeouts and threads](https://docs.python.org/3.13/library/asyncio-task.html)
- [PostgreSQL 17 transaction isolation](https://www.postgresql.org/docs/17/transaction-iso.html)
- [pgvector distance and index contracts](https://github.com/pgvector/pgvector)
- [Docker Compose networking](https://docs.docker.com/compose/how-tos/networking/)

The established paper has ten distinct questions, two of each format, ten marks
each. Multiple-correct requires the complete set; matching awards 2.5 per pair;
coding awards two per passed check. Five checks provide bounded practice feedback,
not proof for every possible submission. Public keys and editable browser results
are practice records, not authenticated examination results.

The existing pinned worker keeps its load/execution deadlines and Stop. Runtime
unavailability leaves coding marks pending for retry. Optional Colab remains
manual copy/paste with no automatic score sync. No paid provider, hosted backend,
production-scale benchmark or real-model quality guarantee is introduced.
