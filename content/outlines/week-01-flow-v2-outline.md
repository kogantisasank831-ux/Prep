---
week: 1
title: Python for production AI systems
status: generation-brief
version: 2.0.0-draft
generation_model: gpt-5.6-terra
---

# Week 1 concept-first rewrite

## Objective

Teach the existing verified FastAPI document-extraction service through a
dependency-aware learning sequence. The lesson must build intuition one concept
at a time instead of presenting architecture, memory/laziness, concurrency, and
framework mechanics in the same explanatory unit.

## Learner experience

Every major concept follows this rhythm:

1. State one concrete question from the document-upload scenario.
2. Temporarily ignore concepts that are not needed yet.
3. Explain the idea from first principles in plain technical language.
4. Use one tiny example or diagram.
5. Show one boundary, trap, or counterexample.
6. Ask a short comprehension question or prediction.
7. Connect the answer to exactly one next concept.

The learner should never need to understand a later framework feature to grasp
the current Python concept.

## Required teaching sequence

1. **Orientation:** trace one successful document request and define the stable
   output. Do not explain the full architecture yet.
2. **Pure transformation:** isolate newline normalization to establish functions,
   inputs, outputs, side effects, and testability.
3. **State and responsibility:** introduce a reader dependency to motivate a
   plain class, `__init__`, instance state, class policy, methods, composition,
   and appropriate inheritance.
4. **Static contracts:** explain type hints, unions, optionals, typed collections,
   `Protocol`, and why annotations do not validate runtime input.
5. **Runtime boundary:** introduce Pydantic only after the type-hint limitation is
   visible. Explain `BaseModel`, fields, configuration, field/model validators,
   errors, and serialization.
6. **Trusted internal values:** introduce frozen dataclasses only after validation;
   explain shallow immutability and contrast functions, plain classes,
   dataclasses, and Pydantic models.
7. **Replaceable decoding:** use the protocol and dependency injection to isolate
   strict UTF-8 decoding. Explain module/import direction and circular-dependency
   signals here.
8. **Failure vocabulary:** build the exception hierarchy, translate errors where
   vocabulary changes, preserve causes, and map to HTTP only at the boundary.
9. **Safe evidence:** introduce logging after failure paths exist; cover module
   loggers, levels, structured fields, traces, and non-leakage.
10. **Lazy processing:** teach iterable, iterator, and generator behavior alone.
    Cover single consumption, deferred errors, memory, and resource lifetime.
    Do not introduce async in this unit.
11. **Concurrency:** begin again from blocking versus waiting. Explain the event
    loop, `async`/`await`, blocking I/O, CPU work, threads, processes,
    cancellation, timeouts, cleanup, and backpressure. Connect to `UploadFile`
    only at the end.
12. **Framework assembly:** now assemble router, dependency construction,
    Pydantic form parsing, bounded upload read, command construction, service
    call, response conversion, and exception handlers.
13. **Proof ladder:** test pure functions, Pydantic boundaries, decoder, service,
    logs, and multipart HTTP in that dependency order. Cover AAA, fixtures,
    fakes, parametrization, exact bytes, dependency overrides, and boundary cases.
14. **Integration view:** reveal the complete architecture only after every box is
    familiar. Include a request trace and failure trace.
15. **Consolidation:** top mistakes, progressive exercises, interview questions by
    level, active recall, knowledge check, and one bounded mini-project.

## Public structure

Use the reference site's useful progression without copying its text:

- executive orientation;
- first-principles sequence;
- small visual models;
- progressive practical Python;
- production integration only after fundamentals;
- top mistakes;
- interview preparation grouped by difficulty;
- knowledge check and active recall;
- exercises and a mini-project;
- explicit bridge to later roadmap topics.

Avoid public curriculum metadata, generation provenance, approval status, time
boxing, review transcripts, or “Week X deliverables” language.

## Technical source of truth

The rewrite must remain consistent with:

- `document_service/`;
- `tests/`;
- `requirements.txt` and `requirements-dev.txt`;
- `content/outlines/week-01-outline.md` for scope and learning outcomes.

The implementation remains UTF-8 `.txt` only, accepts multipart `UploadFile`,
uses a 1 MiB sentinel read, keeps synchronous domain logic, and preserves the
existing stable failure categories and HTTP mappings.

## Content constraints

- Target 8,000–12,000 words; depth comes from intuition and examples, not lists.
- Use one continuous procurement-document scenario.
- Prefer focused excerpts and tiny illustrative examples over repeated large code
  listings.
- Clearly label illustrative code; do not claim it is copied from or executed
  against the repository.
- Do not fabricate citations, validation results, output, or source behavior.
- Cite primary documentation for version-sensitive claims.
- Do not merge generators and async into one lesson unit.
- Do not reveal the complete module architecture before its components have been
  motivated.
- Preserve the existing beginner/production page switch.

## Acceptance criteria

- All 11 approved learning outcomes remain covered.
- Each required teaching-sequence item is visible and ordered as specified.
- Every conceptual unit has an orienting question, small example, trap/boundary,
  checkpoint, and bridge.
- Framework vocabulary is introduced only when the learner has the prerequisite
  mental model.
- The complete architecture appears near the end, not near the beginning.
- Exercises progress from prediction to implementation to design defence.
- Technical statements and code survive Codex verification and existing quality
  gates.
- The candidate receives explicit human approval before replacing the canonical
  production lesson.
