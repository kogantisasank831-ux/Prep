# Week 1 public rewrite review

Reviewed source: `content/inbox/week-01-public-rewrite.md`

## Decision

The draft is not too short. It has enough material for a substantial Week 1 lesson and should not be expanded globally. Proceed with targeted correction and excerpt verification before human review and publication.

Publication status: **candidate ready for human review**.

## Measured scope

- 12 required top-level chapters.
- Approximately 9,800 words in total after targeted coverage corrections.
- Approximately 7,200 words of lesson/reference material plus a 2,200-word practice and interview lab.
- 37 third-level sections.
- 37 fenced code examples.
- The smallest conceptual chapter is still roughly 450 words; no chapter is merely a placeholder.

The practice and interview lab is the largest chapter. This is acceptable for an applied lesson, but future expansion should strengthen explanations only where a concrete learning gap is found—not add more exercises by default.

## Coverage assessment

The draft adequately covers the requested Week 1 concepts in one continuous document-extraction scenario:

- functions, purity, side effects and module boundaries;
- class responsibilities, instance and class state, mutable class attributes, `__init__`, class methods, static methods, composition and inheritance;
- type hints versus runtime validation;
- Pydantic `BaseModel`, fields, strict/frozen configuration, field validators, model validators and construction/serialization APIs;
- frozen dataclasses, protocols and avoiding `Any` at internal boundaries;
- exception taxonomy, transport mapping and explicit exception chaining;
- safe structured logging and `caplog.text` versus `caplog.records`;
- iterables, iterators, generators, deferred failure and resource lifetime;
- async I/O, blocking I/O, CPU-heavy work, bounded concurrency, cancellation and backpressure;
- FastAPI multipart boundaries, dependency injection and bounded upload reads;
- unit, service and endpoint tests, including parametrization and dependency overrides.

The final targeted pass also makes import direction and circular-dependency avoidance, optional/untyped value narrowing, FastAPI composition-root responsibilities, Arrange–Act–Assert, and fixture usage explicit.

No broad content-generation pass is warranted. Any later additions should be driven by human-review findings.

## Flow and public-content hygiene

The narrative flow is materially better than the currently published lesson. A procurement upload service is introduced first and then refined as each Python concept creates or resolves a design problem.

The draft does not expose the internal generation workflow, review status, approval state, version history, weekly plan or time-boxing. These remain internal concerns.

## Corrections completed

1. The reviewed candidate has valid Jekyll YAML front matter.
2. Misleading `VERIFIED_EXCERPT` claims were removed. The lesson uses focused source-derived fragments and illustrative teaching examples without claiming they are literal repository excerpts.
3. Python fences were syntax-audited. Thirty-four are independently parseable either directly or inside a function wrapper. One `except DocumentServiceError` fragment is intentionally shown in the surrounding `try`/`except` discussion and is not a standalone program.
4. A deterministic publication-preparation script and a structural/content-hygiene verifier were added.

## Validation results

- `python -m pytest`: 26 passed.
- `python -m ruff check document_service tests scripts/verify_week01_public.py`: passed.
- `python -m ruff format --check document_service tests scripts/verify_week01_public.py`: passed.
- `python -m mypy --strict document_service tests scripts/verify_week01_public.py`: passed.
- `python scripts/verify_week01_public.py`: passed with 9,765 words, 12 chapters and 37 fenced examples.
- `git diff --check`: passed; Git reported pre-existing LF-to-CRLF working-copy warnings for three unrelated modified files.

## Integration recommendation

- Preserve the inbox file as the raw generated artifact.
- Review `content/reviewed/week-01-public-review-candidate.md` for teaching quality and readability.
- After explicit human approval, replace `content/weeks/week-01.md` with the reviewed candidate and run the deployment checks.
