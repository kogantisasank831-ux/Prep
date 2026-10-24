# Week 10 content review — 2026-10-24

## Scope and provenance

Source base: `6c5855f7ee4560fe5c068d13480f312baa1ced73`.
Only root `AGENTS.md` applies; this repository has no `Design/` directory.
Actual curriculum authority is `Path.md` Week 10 and `plan.md`, alongside the
existing Weeks 7–9 implementation and weekly publishing conventions.

The user requested Week 10 content first, with questions afterward. Earlier
explicit authorization to generate, push and publish persists in this ongoing
weekly workflow. Direct Codex generation was used, with main/beginner candidates
staged under the local Week 10 QA directory before canonical integration. No
independent human rubric ratings or additional human review are claimed.
The ongoing user instruction supplies publication authorization; it is distinct
from the technical checks below. No Week 10 assessment is created or advertised.

Applicable skills: ds-production-coding-practices and ds-code-review, including
their implementation/review references and candidate-matched CI release policy.
The primary agent performed implementation, content review and integration;
no delegated or independent model review is claimed.

## Accepted contracts and coverage

| Curriculum requirement | Implementation/content evidence |
| --- | --- |
| Request/retrieval/tool traces | One request recorder; explicit active parents; real hybrid-search calls; ordered candidate and reranker identities |
| Query/rewrite trace | Query counts/indices in metadata, actual original/variants in explicit synthetic capture; protected-term query planner reused |
| Documents and reranking | Authorized snapshot and aligned IDs/scores; controlled capture retains source version/location text; no privileged second search |
| Prompt/model/response | Explicit two-message raw-text prompt and typed model port; scripted fixture observed separately from returned extractive answer |
| Latency | Aware UTC chronology, monotonic integer intervals, missing invalid readings, stated ingestion/export exclusion and inclusive parent semantics |
| Usage/cost | Known zero distinct from unknown; cached subset; exact Decimal rates; versioned illustrative currency/rate card and unknown reasons |
| Failure classification | Closed error categories, original errors/cancellation re-raised, completed parent/child records, no exception payload export |
| Versioning/debugging | Pipeline/config/source/component and development-code identity; paired full/tight context comparison locates lost supporting clauses |
| Production boundaries | Payload minimization, source-aware inspection, cardinality/sampling concepts, OTel propagation translation, recorder/export health |

Main and beginner lessons include eight-hour routes, orienting examples,
checkpoints, runnable code/commands, failure boundaries, exercises with acceptance
evidence, interview reasoning, deliverables and primary sources. Scope stops
before Week 11 security implementation and Week 12 service deployment.

## Technical review and executed local evidence

- Ruff check and format check passed for the Week 7–9 assessment test modules,
  `labs/week_10` and `tests/test_week10_tracing.py` (nine Python sources).
- Strict mypy with explicit package bases passed for the same nine sources.
- Targeted pytest: **797 passed**, zero failed/skipped. This is the existing
  assessment/retrieval/assistant/evaluation/service gate plus **91 new tracing
  cases**. The unrelated Windows-only comparison module remains outside this
  selected suite; this is not an unrestricted whole-repository test claim.
- All eight CLI scenarios executed. Payment/tight/denied/missing-fact/model
  fixture exited zero. Bad rewrite, scripted model timeout and invalid model
  response exited one with the expected classified trace records.
- All six Python fenced examples across both lessons executed successfully.
  Duplicate examples were still executed in each lesson's context. Runtime output
  paths were mapped to a fresh synthetic QA directory for repeatable execution.
- Full/tight evidence was inspected: the same candidates and reranking produce
  three versus one context spans. Net 30 survives the tight run; the connecting
  clause and matching line item do not. The initial draft hypothesis that the
  term itself disappeared was rejected by execution before lesson publication.
- Browser preview checked main/beginner rendering, code/tables, heading/TOC
  correspondence, active navigation, depth switch, persistent reading mode,
  mobile TOC, light/dark modes, menu/Escape and 390 px horizontal containment.
  Dashboard exposes Week 10 content and retains exactly nine assessment links.
  Screenshots were inspected. No page errors or failed resource requests.

Local Python is 3.12.14; the declared remote CI runtime is 3.13.12. Local tests
do not substitute for the exact candidate SHA CI gate. The candidate branch must
pass the updated `Weekly learning checks` workflow before main promotion.
GitHub Pages build and live lesson/dashboard checks are required after promotion;
immutable candidate/run identities are retained in the publishing QA evidence.

## Review findings resolved and limits

The code review traced authorization through eligible corpus construction,
query fusion, same-pool reranking, context/citation validation and output, plus
failure/cancellation/export paths. Independent math examples, source invariance,
all-30-case parity and negative boundary tests provide the principal oracles.

Resolved before release: nullable UTC-offset validation, active-parent ownership,
completed-root requirement, explicit no-model usage, prompt role/size/UTF-8
validation, required Decimal rates and no-evidence model-call skip. No old lab
interfaces or datasets were changed. Source/test/config edits are bounded to
the new lab, lessons, navigation, README and CI inclusion.

Residual boundaries are explicit in public content: local synchronous custom
JSON, not OTLP; fixture counters rather than inference; no real provider adapter,
streaming/network timeout enforcement, metrics collector, durable audit store,
production sampling or latency benchmark. Model response shape does not prove
faithfulness. The fixture response is observed separately and is not promoted
as the assistant's answer. Full capture is synthetic-only and not a PII detector;
allowed metadata values and fingerprints can still be sensitive. Export is a
single best-effort file write, not a transactional persistence guarantee.

Rollback: restore the previous lesson/navigation/code revision and rebuild Pages;
the changes introduce no data migration or third-party service dependency.

## Primary sources checked

Retrieved 2026-10-24; public lessons link to the originals. No quoted passages,
vendor performance claims or current provider pricing are used.

- https://opentelemetry.io/docs/concepts/signals/traces/ — span relationships,
  metadata, trace/export vocabulary; custom lab differences stated.
- https://docs.python.org/3.13/library/time.html#time.perf_counter_ns — integer
  performance-counter intervals, monotonic/reference-point semantics.
- https://docs.python.org/3.13/library/decimal.html — decimal construction and
  explicit precision; invented rate arithmetic is independently tested.
- https://opentelemetry.io/docs/security/handling-sensitive-data/ — minimization,
  instrumentation review and predictable-hash limitations.
- https://opentelemetry.io/docs/concepts/sampling/ — head/tail decision boundaries.
- https://opentelemetry.io/docs/concepts/context-propagation/ — propagation across
  processes, correlation versus authority and untrusted metadata boundaries.

The previously located GenAI semantic-convention page reports that it moved;
the lesson avoids depending on that stale API location or a particular unstable
attribute spelling. Implementations should check their chosen SDK's current
conventions when adding a real integration.
