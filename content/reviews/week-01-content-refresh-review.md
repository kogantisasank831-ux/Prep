---
week: 1
phase: 1
status: approved
version: 2.1.0
last_reviewed: 2026-10-23
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested Week 1 within the established explicitly approved create-check-push-publish workflow
---

# Week 1 content refresh review

## Scope and continuity

Repository `kogantisasank831-ux/Prep`, main baseline
`207b6e786efe55f1934d0171335e2762b1a9f9d7`, tree
`f5c3a122968b6a447cc70fb1830e6720538f3d44`. Work used
`week01-refresh` from a fresh `origin/main` fetch. The sole applicable instruction
file is root `AGENTS.md`; no `Design/` directory exists in this curriculum
repository. Existing untracked QA directories and all unrelated material remain
untouched.

The user requested Week 1, continuing the authorized direct review, correction,
push and Pages workflow. The existing concept-first teaching sequence was
approved on 2026-08-08. This is a targeted refresh rather than another complete
rewrite. The publication authorization is not an invented independent human
rubric score.

Inspected `Path.md` Week 1, `plan.md`, both Week 1 outlines, the public-rewrite
and concept-first reviews, both complete lessons, root README, all ten
`document_service/` Python files, its four test modules, pinned requirements,
the existing content verifier and shared layout/config. Historical reviews and
generation artifacts remain unchanged.

Exactly four documentation files change: the main lesson, beginner lesson, root
README and this review. Service code, tests, requirements, verifier, site
configuration/navigation and later weeks are unchanged.

## Changes and preservation

The main lesson retains all 22 top-level chapters in order, all 28 Python
fragments, exercises, mini-project, interview answers and eleven recall
questions/answers. All primary source URLs remain. Its opening JSON's text has
60 characters, not the previously stated 62; the corrected complete response
was reproduced against the real endpoint.

The beginner lesson retains all ten top-level chapters, original six recall
questions and substantive teaching material. Its request diagram becomes an
ordered explanation with the correct dependency-before-route-read sequence.
The error-translation fragment now supplies the required keyword-only
`correlation_id`; the corrected fragment was executed and preserves the reader
failure as its cause. The other nine Python fragments and opening JSON remain
unchanged. Added six recall answers and three small input experiments.

Additional clarifications match the current implementation:

- `extra="forbid"` acts on model input keys. The route supplies two named fields,
  so it does not thereby reject every unknown multipart field.
- Application document failures use `code`/`message`/`correlation_id`. Framework
  scalar-validation failures use a `detail` list, including when both paths
  produce HTTP 422.
- The sentinel bounds the endpoint's read. Parsing/spooling may precede that
  read; it does not establish a complete HTTP-body or storage limit.
- The start log records the declared media type before the supported-type check.
  Length-bounded caller input is not an allowlisted value, and the existing
  content/filename test does not establish universal metadata log safety.
- The illustrative algorithm allowlist reads one field; the main text now
  identifies a field validator as the simpler choice for that particular rule,
  while retaining the model-validator mechanism and explaining its proper use.
- The beginner generator discussion now states that `splitlines()` eagerly
  allocates a list even when its results are subsequently yielded.

The README gains a Week 1 setup, virtual-environment alternatives, scoped test
command, loopback Uvicorn command, exclusive creation of a byte-exact synthetic
sample, multipart curl request and expected JSON. Both lessons link there.
Original README content is a byte-for-byte prefix of the candidate. Exercises
such as Markdown support and review-item classification are explicitly practice
changes, not existing features.

Public front matter is preserved. The existing Week 1 verifier deliberately
keeps approval/review metadata internal and fixes the concept order. This
review records version and authorization without weakening that verifier or
introducing public provenance/time-boxing sections.

## Requirement mapping

All original Week 1 requirements remain covered: functions/classes/modules;
static typing; frozen dataclasses versus Pydantic boundaries; explicit errors;
safe logging; iterators/generators; async and workload choices; reusable,
testable code; pytest; a document upload/extraction/validation/JSON service; and
the four requested interview themes. No broader runtime or product contract is
introduced.

## Validation executed

Environment: Linux, Python 3.12.14, FastAPI 0.139.2, Pydantic 2.13.4, pytest
9.1.1, Ruff 0.15.22 and mypy 2.3.0, using existing pinned requirements. The
outline's target remains Python 3.13.12; this pass did not execute that target
interpreter. QA-only Markdown 3.11.2, python-liquid 2.3.5 and PyYAML 6.0.3 were
used without changing requirement files.

| Check | Observed result |
| --- | --- |
| Existing Week 1 pytest modules | 26 passed |
| Ruff lint on service, four test modules and existing verifier | Passed |
| Ruff format check on the same scope | 15 files already formatted |
| Strict mypy on the same scope | Passed, 15 source files |
| Existing content verifier on both candidates | Main 8,435 words/22 chapters/32 fences; beginner 2,268 words/10 chapters/11 fences |
| Python fragment syntax | All 38 compiled; five require the surrounding function/async-function context |
| Preservation | All 28 main Python fragments unchanged; nine of ten beginner Python fragments unchanged; only the required error argument changed in the tenth |
| JSON and runtime examples | Both opening JSON responses and README response reproduced exactly |
| Input/failure probes | Suffix 415; blank/invalid UTF-8 422 with document code; oversized 413; unsupported declared type 415; invalid scalar metadata 422 with `detail`; unknown multipart field accepted as existing behavior |
| Exact size boundary | 1 MiB of multibyte UTF-8 accepted with 524,288 decoded characters; 1 MiB plus one byte rejected |
| Read order and bound | Invalid scalar metadata triggers no endpoint read; a valid request calls `read(MAX_UPLOAD_BYTES + 1)` |
| Selected Python examples | Generator single-pass/deferred failure, algorithm allowlist and corrected chained exception executed |
| Local Uvicorn/curl smoke | Real multipart request returned expected ten-character/two-line JSON on a dedicated ephemeral loopback port; server cleaned up |
| Sample-file protection | Second exclusive creation rejected; original bytes preserved |
| Structural rendering | Both candidates rendered through the existing layout; one H1 each, no duplicate IDs or unresolved templates, internal links/assets valid |
| Source preservation | Service, tests, verifier and pinned requirements byte-identical to baseline |

Ruff initially crashed before executing a check because the restored local
binary was unusable. Reinstalling the same pinned 0.15.22 wheel repaired that QA
environment; the subsequent lint and format commands above passed. No repository
dependency or rule changed.

The fragment audit is not a claim that every partial/illustrative snippet is a
standalone executable program. Runtime checks named above are distinct from
syntax checks. Local rendering uses Python Markdown/Liquid rather than
Ruby/Jekyll or visual browser QA. Final diff/whitespace and commit-tree checks
precede publication; hosted Jekyll/Pages completion and both public lesson URLs
are verified after pushing and reported in the handoff.

## Primary sources and limits

Opened the official Pydantic validator documentation, FastAPI request-file and
form/file guides, and Python 3.13 iterator/generator documentation. These support
the targeted clarifications; observed API, count, read-order and exception
behavior was also checked against local source and executed probes.

- https://docs.pydantic.dev/latest/concepts/validators/
- https://fastapi.tiangolo.com/tutorial/request-files/
- https://fastapi.tiangolo.com/tutorial/request-forms-and-files/
- https://docs.python.org/3.13/tutorial/classes.html#generators

This pass does not establish production deployment, general log non-leakage,
HTTP admission limits, authentication, persistence or throughput. The application
is unchanged and the full later-week test suite was not rerun for a Week 1
documentation refresh. To repeat the relevant checks, use the four-module pytest
command in the README; run the scoped Ruff and strict mypy commands described
above and `python scripts/verify_week01_public.py` with each lesson path.
