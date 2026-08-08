# Week 1 concept-first rewrite review

## Inputs

- Candidate: `content/reviewed/week-01-flow-v2-terra.md`
- Generation model: `gpt-5.6-terra`
- Generation brief: `content/outlines/week-01-flow-v2-outline.md`
- Technical source of truth: `document_service/`, `tests/`, and pinned requirement files
- Teaching-flow reference: <https://deepankarkotnala.github.io/genai_glassmorphism/genai-portal/study-plan.html>
- Additional teaching-style input: project-owner-provided chat excerpt on teaching one dependent concept at a time

The project owner stated that the reference site may be used. The rewrite adopts
its progression patterns but does not copy its lesson text.

## Decision

Approved by the project owner for publication on 2026-08-08. The approved
candidate was promoted byte-for-byte to `content/weeks/week-01.md` before the
publication validation run.

## Material change from the current lesson

The current public lesson reveals architecture early and later combines
generators, resource lifetime, and concurrency. The new candidate instead:

1. starts with one stable output;
2. motivates one Python concept from one concrete pressure;
3. uses an orienting question, tiny example, boundary, checkpoint, and bridge;
4. teaches generators without async;
5. teaches async from blocking versus waiting in a separate unit;
6. assembles FastAPI only after functions, classes, typing, validation,
   dataclasses, protocols, failures, logging, laziness, and concurrency are known;
7. reveals the complete request and failure traces near the end; and
8. consolidates through mistakes, progressive exercises, a mini-project,
   interview defence, and active recall.

## Coverage

All 11 outcomes from `content/outlines/week-01-outline.md` remain represented:

- cohesive modules and dependency direction;
- class state, construction, methods, composition, and inheritance;
- type hints, optionals, typed collections, protocols, and runtime limits;
- Pydantic fields, configuration, validators, errors, and serialization;
- frozen dataclasses and shallow immutability;
- explicit failure hierarchy and chained translation;
- safe structured logging;
- iterator/generator semantics and lifetime;
- async, blocking work, threads/processes, cancellation, timeouts, and backpressure;
- deterministic pytest testing from unit to multipart boundary; and
- senior-level design defence.

The original scope boundaries remain unchanged: UTF-8 `.txt`, multipart
`UploadFile`, a 1 MiB sentinel read, synchronous domain logic, and the existing
stable HTTP mappings.

## Primary-agent corrections

- Removed repetitive repository/provenance comments from learner-facing code
  blocks because they interrupted the narrative. Provenance remains in this
  review artifact.
- Corrected the mini-project's “literal word `delay`” classifier. The generated
  substring check also matched `delayed`; it now uses an explicit word-boundary
  regular expression.
- Corrected the illustrative Pydantic request-model docstring from “JSON” to
  “scalar” because this endpoint receives multipart form fields.
- Added explicit iterator return annotations to the generator examples.
- Strengthened the content verifier to enforce concept order, required learning
  markers, absence of learner-facing provenance labels, and internal metadata
  leakage.

## Validation

- Structural/content-flow verifier: passed.
- Candidate size: approximately 8,000 words, 22 top-level chapters, and 32 fenced examples.
- Python fence syntax audit: passed for all 28 Python examples, either directly
  or in the surrounding function context.
- `python -m pytest`: 26 passed.
- Ruff lint: passed.
- Ruff format check: passed.
- Strict mypy: passed for `document_service`, `tests`, and the verifier.
- `git diff --check`: passed with existing LF-to-CRLF working-copy warnings.

## Follow-up observations

The project owner approved the content flow, checkpoints, deeper material, and
mini-project. Dedicated visual callout styling remains an optional presentation
enhancement; it is not required for this publication and does not change the
lesson contract.
