---
week: 1
phase: 1
title: Python for production AI systems
status: approved
version: 1.0.0
estimated_hours: null
---

# Week 1 Outline: Python for Production AI Systems

## Objective

Build the Python engineering foundation needed for reliable AI services by
implementing and testing a small FastAPI document-extraction service with typed
domain models, explicit validation, safe error handling, and useful logging.

The week emphasizes production reasoning and interfaces rather than introductory
Python syntax.

## Measurable learning outcomes

By the end of Week 1, the learner should be able to:

1. Organize a small FastAPI service into cohesive modules with narrow public
   interfaces.
2. Explain Python class mechanics relevant to service design, including instance
   state, class attributes, methods, constructors, composition, and inheritance;
   use classes according to responsibility, state, and lifecycle.
3. Apply type hints that improve static analysis without creating misleading
   guarantees at runtime.
4. Explain how Pydantic models are Python classes derived from `BaseModel`, how
   fields and class configuration are declared, and when to select them instead
   of immutable dataclasses.
5. Validate untrusted document metadata and return structured, serializable
   results.
6. Design an explicit exception hierarchy that distinguishes validation,
   unsupported-format, extraction, and infrastructure failures.
7. Emit useful operational logs without exposing uploaded document content,
   filenames, or sensitive metadata.
8. Use iterators and generators for streaming document processing and explain
   their memory and lifecycle trade-offs.
9. Explain when async improves throughput, when it does not, and how blocking work
   affects an event loop.
10. Write deterministic pytest tests for successful behavior, boundaries, and
    failure paths.
11. Defend the design choices in senior-level interview discussion.

## Prerequisites

- Working knowledge of Python syntax, modules, functions, classes, and exceptions.
- Python 3.13.12 and familiarity with virtual environments and `pip`.
- Basic understanding of JSON and HTTP-style service boundaries.
- No prior Pydantic, pytest, or async production experience is required.

## Concepts in scope

### Functions, classes, and modules

- Cohesion, responsibility, dependency direction, and public interfaces.
- Pure domain functions versus stateful adapters or services.
- Class construction, instance and class attributes, instance/class/static
  methods, composition, inheritance, and appropriate use of each.
- Composition over unnecessary inheritance.
- Import boundaries and avoiding circular dependencies.

### Type hints

- Runtime values versus static type information.
- Function signatures, return types, unions, protocols, and typed collections.
- Narrowing optional values and containing untyped boundaries.
- Limits of type hints and the separate role of runtime validation.

### Dataclasses and Pydantic

- Dataclasses for internal domain values and configuration-free data containers.
- Frozen dataclasses and practical immutability.
- Pydantic models for parsing and validating untrusted boundary data.
- `BaseModel` inheritance, annotated fields, model configuration, field and model
  validators, and model methods.
- The distinction between declaring Pydantic models as classes and using classes
  as an unnecessary abstraction for stateless logic.
- Validation errors, serialization, strictness, and version-sensitive behavior.

### Exception handling

- Domain-specific exception hierarchy.
- Translating low-level failures at boundaries.
- Exception chaining and actionable error context.
- Cleanup with context managers and avoiding broad exception suppression.

### Logging

- Module loggers, log levels, structured context, and exception traces.
- Logging lifecycle and failure information without logging document contents.
- Library versus application logging configuration.

### Iterators and generators

- Iterable, iterator, and generator mental models.
- Lazy evaluation, memory usage, single consumption, and deferred failures.
- Generator cleanup and appropriate use in document pipelines.

### Async fundamentals

- Cooperative concurrency and the event loop.
- Awaitable I/O versus blocking upload parsing or CPU work.
- Task cancellation, timeouts, exception propagation, and resource cleanup.
- Threads versus async as workload and integration choices.

### Reusable and testable design

- Separating deterministic domain logic from upload and decoder adapters.
- Dependency injection at external boundaries.
- Small interfaces and observable behavior.
- Avoiding speculative abstractions.

### Pytest fundamentals

- Arrange–act–assert and behavior-focused tests.
- Parametrization, fixtures, exception assertions, and byte-exact test inputs.
- Mocking only external boundaries.
- Determinism, isolation, boundaries, and regression cases.

### FastAPI boundary fundamentals

- Application and router construction.
- Request models, response models, status codes, and exception translation.
- Dependency injection at the HTTP boundary.
- `TestClient`-based endpoint tests.
- Keeping validation and business rules out of route functions.

## Explicitly out of scope

- FastAPI deployment, production servers, streaming, advanced async endpoints,
  middleware architecture, caching, rate limiting, and health checks; these remain
  Week 12 topics.
- OCR, table extraction, scanned PDFs, and production-grade PDF parsing.
- Cloud object storage, queues, databases, authentication, or tenant isolation.
- LLM calls, prompting, embeddings, RAG, or agent frameworks.
- Parallel document processing or performance benchmarking.
- Docker, CI, dependency scanning, or deployment automation.
- Exhaustive coverage of Python's object model, typing system, or asyncio APIs.

These exclusions keep the week feasible while leaving clear extension points.

## Guided build

Create a small FastAPI document-extraction service that:

1. Accepts a bounded multipart upload, declared media type, and safe external
   correlation identifier through an HTTP endpoint.
2. Validates supported types, filename suffix, upload media type, and size at the
   appropriate boundary.
3. Decodes UTF-8 plain-text content through an injectable reader interface.
4. Rejects unsupported formats and malformed or undecodable content explicitly.
5. Normalizes extracted text without silently changing its meaning.
6. Returns a typed result that serializes to structured JSON.
7. Logs lifecycle events and failures without logging document text or filename.
8. Includes unit tests for success, validation errors, unsupported formats,
   decoding errors, empty and oversized documents, media-type mismatches, decoder
   failures, and sensitive-data leakage from logs.
9. Includes endpoint tests for the success response and stable error mappings.

The initial implementation supports UTF-8 `.txt` only. Route functions must stay
thin, and another parser should remain implementable without introducing a generic
plugin framework.

## Proposed implementation boundaries

The generated lesson should explain the responsibilities below without requiring
these exact filenames:

```text
multipart upload -> FastAPI route -> Pydantic metadata -> extraction service
                                                               |
                                                               v
                                                        decoder adapter
                                                               |
                                                               v
                                                       domain result/error
```

- **FastAPI route:** performs a bounded upload read, handles HTTP concerns, and
  maps domain failures to stable responses.
- **Boundary model:** validates untrusted request data.
- **Extraction service:** coordinates deterministic rules and dependency calls.
- **Decoder adapter:** isolates strict UTF-8 decoding.
- **Domain result:** represents validated extracted output.
- **Error types:** preserve failure categories without leaking payloads.

## Worked-example requirements

The draft must include focused examples for:

1. A misleading type hint contrasted with runtime validation.
2. Mutable versus frozen dataclass behavior, including shallow immutability.
3. Pydantic validation at an untrusted boundary.
4. Pydantic's class inheritance and configuration model contrasted with a plain
   class and a dataclass.
5. An exception translated and chained at an adapter boundary.
6. Safe structured logging with a correlation identifier.
7. A generator that streams logical lines and demonstrates single consumption.
8. Async I/O contrasted with blocking or CPU-bound work.
9. A behavior-focused pytest test using byte-exact uploaded content.
10. A FastAPI endpoint test using `TestClient`.

Examples must not claim to have been executed in ChatGPT Web.

## Independent exercises

1. Add a Markdown-text adapter without changing the extraction service's public
   behavior.
2. Make the mandatory 1 MiB upload limit configurable without weakening the
   bounded-read guarantee.
3. Add parametrized tests for allowed and rejected media types.
4. Verify through captured logs that raw document text is never emitted.
5. Design, but do not implement, an async batch-extraction interface and justify
   whether it should use async tasks, threads, processes, or sequential execution.

Each exercise must include acceptance criteria, edge cases, and optional hints,
but not a complete solution.

## Interview outcomes

The learner must be able to answer and defend follow-up questions about:

- Mutable versus immutable objects, aliasing, shallow immutability, and why this
  matters for shared AI pipeline state.
- Generators versus lists, including memory, latency, repeatability, deferred
  exceptions, and resource lifetime.
- Threads versus async, including workload type, blocking libraries, cancellation,
  backpressure, debugging, and operational complexity.
- Why type validation matters when LLM or document-derived data crosses a trust
  boundary.
- Why static typing and runtime validation solve different problems.
- Where exceptions should be translated and where they should propagate.
- What useful logs contain and what sensitive logs must exclude.

## Acceptance criteria

The Week 1 content is ready for technical review when:

- all 11 learning outcomes are addressed explicitly;
- the guided build uses thin FastAPI routes and remains UTF-8 `.txt`-only;
- Python class fundamentals and Pydantic's class-based model are explained
  explicitly;
- code uses explicit type hints and contains no unexplained `Any`;
- boundary validation, domain types, I/O, and orchestration responsibilities are
  distinguishable;
- failures use explicit exception types and chained context where applicable;
- logging examples avoid document content and sensitive metadata;
- async is taught as a concurrency choice rather than a universal optimization;
- tests cover successful behavior, boundaries, and meaningful failures;
- exercises contain acceptance criteria without full solutions;
- interview material includes trade-offs and follow-up questions;
- primary-source URLs support version-sensitive claims; and
- no code execution or validation is falsely claimed.

## Approved decisions

1. Week 1 produces a FastAPI service with thin routes over a separated service
   layer.
2. The first supported document type is UTF-8 plain text only.
3. FastAPI and Pydantic are runtime dependencies; pytest and FastAPI's test-client
   requirements are test dependencies.
4. The implementation targets Python 3.13.12 and uses `pip` for dependency
   installation.
5. Content quality and completeness take priority over a fixed time constraint.
6. The HTTP API accepts an `UploadFile` rather than a caller-controlled server
   filesystem path.
7. Uploads are capped at 1 MiB and require `python-multipart`.
8. Endpoint tests use `httpx2` with the resolved Starlette version.

## Outline review

- Human review: approved with changes on 2026-07-21
- Technical review: pending
- Approved for full content generation: yes
- Final content review: approved by the project owner on 2026-08-01
