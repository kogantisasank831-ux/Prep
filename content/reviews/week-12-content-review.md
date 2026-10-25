---
week: 12
status: reviewed
version: 1.0.0
last_reviewed: 2026-10-25
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested the next week within the established approved content-first build-check-push-publish workflow
---

# Week 12 content and service review

## Baseline, scope and logic handoff

Base main: `6a011afd344297791d088891d33ad362c80be602`; tree
`06186df63d5f9b1e3b196a0e3d441a1cedab0df7`. Only root AGENTS.md applies.
There is no Design directory for this curriculum. Path.md Week 12 and plan.md
govern the learning scope; the root instruction file's finance-app description
does not introduce unrelated finance features into this weekly service lesson.
Existing QA directories and previous content/labs/banks are preserved. No agents.

Read the actual Week 11 policy/assistant and source fixtures, relevant Week 7–8
contracts, Week 1 API conventions, declared dependency/CI files, layout/navigation,
Path.md and plan.md. Applied requirements analysis and production coding with
their relevant reference checks; retained bounded diff review and the existing
exact-candidate CI/server-smoke release policy.

Component logic revision 1 lives in labs/week_12/LOGIC.md. W12-FR1–6, DR1,
NFR1–3, ENG1 and ER1 specify request/identity/storage, pre-vector scope/pins,
fresh return snapshots, cache/admission/rate lifetime, streaming, config/health
and verification. Numeric defaults are explicitly teaching configuration, not
stakeholder performance targets. Public hosting, real-model quality/SLOs,
distributed control semantics, backups/recovery and operating ownership remain
future decisions. They do not block the authorized local synthetic build.

## Teaching and implementation coverage

The main and beginner candidates were staged before canonical integration.
They contain 17/14 learning sections and approximately 4,730/3,144 body words,
with separate eight-hour routes, first-principles examples, failure boundaries,
checkpoints, guided commands, exercises, interview explanations and primary
sources. Both cover every Path.md Week 12 topic. The Phase 3 deliverable is a
reproducible local interview demonstration. Questions remain a separate pass;
Week 12 is added only to published lessons, not assessment navigation.

The scoped lab implements actual FastAPI, asynchronous Psycopg I/O and
PostgreSQL/pgvector with versioned insert-only bootstrap. Two generated file
bearers map to fixed synthetic tenant/principal contexts; no body assertion
selects identity. A separate bootstrap identity owns writes; the application
role receives SELECT on the owned tables and uses read-only snapshot reads.

SQL scope, independently pinned representations and known-body screening precede
an exact eligible-set vector query. The 32-dimensional token-hash encoder is
explicitly a synthetic baseline; no ANN or semantic quality claim is made.
Up to twelve candidates enter the unchanged actual Week 11 guard. This candidate
stage can lose recall and is not claimed equivalent to searching an entire
earlier corpus.

Cache identity retains caller scope, exact question/pipeline identity, complete
selected source/policy snapshot and context configuration. Both DB reads remain
on a hit. A new transaction after computation observes committed changes hidden
from an earlier repeatable-read snapshot. Current differences suppress the
return; this is neither retroactive nor distributed atomic revocation. Cache
expiry is absolute/monotonic, bounded to 32 successful results, with a new
request ID on reuse and no stale-success outage fallback.

The two-slot process-local gate retains ownership after cancellation until its
thread really finishes. Fixed-window rate, gate and cache deliberately remain
one-process controls; the image runs one worker. The service performs full
validation before three JSON-data SSE frames, with a required done marker.
No early token generation, replay/durable job, process sandbox or hard thread
kill is claimed. A public API, identity lifecycle, TLS and real provider are
not deployed by publishing GitHub Pages lessons.

Container packaging uses a digest-pinned Python 3.13.12 base and version-pinned
pgvector/PG17, non-root/read-only application containers and explicit secret
mounts. A frontend bridge carries loopback API publishing; the normal database
stays on an internal backend. CI explicitly adds a loopback DB test port.
Ordinary down/up retains a named volume and its existing credentials; bootstrap
rejects conflicting policies/representations instead of resetting data.

## Executed technical checks

Local environment is Python 3.12.14 and Node 24.22.1 with declared pytest/Ruff/
mypy. The workspace has no Docker/Podman/PostgreSQL server executables. Real
container/database evidence therefore comes from the required GitHub runner,
not from local doubles or an invented local deployment.

- The initial deep regression run passed 1,085 targeted tests. The final
  serialization-boundary regression raises the required count to 1,086.
  Final local/CI transcripts and immutable identities are retained in QA.
- The service's 62 local cases use actual FastAPI and guarded computation with
  an explicit repository substitute. They cover credentials-before-body,
  strict/received-byte input bounds, current scope, public error/refusal data,
  SSE preflight/completion, OpenAPI/health, cache scope/expiry/outage, rate-window
  boundaries and cancellation/admission cleanup.
- A valid compact 4,096-byte/1,000-character question exposed an intermediate
  JSON reserialization expansion. Compact serialization now preserves that
  boundary; the independent HTTP regression exercises the real guarded core.
- Five self-contained lesson Python examples execute; two JSON bodies and
  three SSE data lines parse. SQL and shell examples correspond to the tested
  adapter/bootstrap/Compose/smoke paths, rather than claimed local DB execution.
- Ruff formatting/lint and strict mypy cover 26 scoped Python files, including
  both Week 12 suites. No checks or existing tests are weakened or skipped.

The real-stack candidate `54ec2f48188a37b1340cd5654f89e91f08790ae9`
(tree `2fdaf8786aa399353aeab27fb1980fccce53631a`) passed workflow
`40216501402`, including unit job `121238662356` and stack job `121238832338`.
The stack ran PostgreSQL 17.11 and pgvector 0.8.7 on Linux amd64. All nine actual
DB tests passed; eleven real-HTTP smoke assertions passed both before and after
ordinary volume-preserving down/up. The job recorded its built image ID.

These checks establish the implemented transaction/schema/role behavior for
that candidate. The final content/serialization/base-image-reference changes
require a fresh exact-candidate run of both jobs before main promotion; no
future success is asserted by this review. Post-Pages lesson navigation/rendering
and live asset identity checks follow promotion, with QA retaining run/SHA data.

Review found no remaining supported actionable defect after the local fixes.
This is technical/content review; no independent human rubric scores or
production readiness approval are fabricated. The selected regression command
excludes the pre-existing unrelated Windows-only comparison module and is not
an unrestricted whole-repository pass. Actual mobile-device rendering and an
external hosted API are not claimed.

## Sources, dependencies and remaining limits

Primary sources were opened on 2026-10-25: FastAPI async/lifespan/streaming,
Psycopg async ownership, pgvector, PostgreSQL 17 isolation and Docker Compose
secrets/startup/networks. The source links are in the lessons. Their principles
are separated from this lab's custom defaults, envelopes and algorithms.

The only added application dependency is scoped psycopg[binary]==3.3.6 for real
async PostgreSQL access. Its published Python 3.12/3.13 wheels were checked and
the declared install exercised; existing FastAPI/Pydantic/Uvicorn pins are reused.
No ORM, Redis, model SDK or paid service is introduced. Binary distribution
metadata/licenses remain with installed packages; no unrestricted-license or
security certification claim is made. Dependencies are not presented as a fully
locked/scanned production software supply chain.

Routine application events use bounded categories/metadata; no raw query,
source, token or driver message projection. Access logging is disabled in the
image command. Retaining informational events requires a deliberate logging
sink; a logger call is not an audit-retention system. The local secret directory
uses explicit creation/modes, while Windows host access remains an ACL concern.
File mounts are not a managed encrypted vault or automatic rotation mechanism.

Rollback is a normal feature revert and Pages rebuild for the lessons. The new
lab's owned database volume is separate local data; reverting Git must not be
interpreted as permission to remove it. No earlier lesson body, assessment bank,
shared scorer/style or existing source dataset is changed.
