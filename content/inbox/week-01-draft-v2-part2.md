<!-- CONTINUATION_START: testing-matrix -->

### Required test categories

| Behavior                                                                      | Layer                    | Expected result                                                                               |
| ----------------------------------------------------------------------------- | ------------------------ | --------------------------------------------------------------------------------------------- |
| Valid multipart request containing `media_type`, `correlation_id`, and `file` | HTTP boundary            | `200` with the typed extraction response                                                      |
| Missing `media_type` field                                                    | HTTP boundary            | Framework validation response, normally `422`                                                 |
| Missing `correlation_id` field                                                | HTTP boundary            | Framework validation response, normally `422`                                                 |
| Missing `file` field                                                          | HTTP boundary            | Framework validation response, normally `422`                                                 |
| Unsafe correlation identifier                                                 | Pydantic boundary        | Validation failure without echoing the rejected value into application logs                   |
| Upload at exactly 1,048,576 bytes                                             | HTTP boundary            | Accepted for subsequent format, decoding, and content validation                              |
| Upload above 1,048,576 bytes                                                  | HTTP boundary            | `413` with code `document_too_large`                                                          |
| Bounded upload read                                                           | HTTP boundary            | `UploadFile.read()` is called with a maximum of 1,048,577 bytes: 1 MiB plus one sentinel byte |
| Valid `.txt` filename                                                         | Service policy           | Accepted when both media types are also `text/plain`                                          |
| Unsupported filename suffix                                                   | Service policy           | `415` with code `unsupported_document_format`                                                 |
| Declared media type is not `text/plain`                                       | Service policy           | `415` with code `unsupported_document_format`                                                 |
| Upload content type is not `text/plain`                                       | Service policy           | `415` with code `unsupported_document_format`                                                 |
| Declared and upload media types differ                                        | Service policy           | `415` with code `unsupported_document_format`                                                 |
| Valid UTF-8 bytes                                                             | Decoder                  | Decoded text is returned unchanged before normalization                                       |
| Invalid UTF-8 bytes                                                           | Decoder and service      | Low-level decoding failure is chained into a stable document-decoding failure                 |
| Windows newline bytes `\r\n`                                                  | Domain normalization     | Normalized to `\n`                                                                            |
| Classic Mac newline bytes `\r` after decoding                                 | Domain normalization     | Normalized to `\n`                                                                            |
| Byte-exact newline fixture                                                    | Test boundary            | Direct byte payloads are used rather than text-mode writes                                    |
| Zero-byte upload                                                              | Service                  | Rejected as empty content                                                                     |
| Whitespace-only decoded content                                               | Service                  | Rejected with the stable empty-document failure                                               |
| Valid non-whitespace Unicode content                                          | Decoder and service      | Preserved after strict UTF-8 decoding                                                         |
| Successful extraction logging                                                 | Logging                  | Lifecycle records contain safe structured fields without content or filename                  |
| Failed extraction logging                                                     | Logging                  | Failure record contains a stable failure code and safe correlation identifier                 |
| Raw uploaded text in logs                                                     | Logging                  | Secret marker is absent from `caplog.text` and record messages                                |
| Uploaded filename in logs                                                     | Logging                  | Secret filename marker is absent from `caplog.text` and record messages                       |
| Correlation identifier supplied through `extra`                               | Logging test             | Asserted through attributes on `caplog.records`, not assumed to appear in `caplog.text`       |
| Decoder failure                                                               | Service                  | Translated into the application exception hierarchy with causal chaining                      |
| Unexpected infrastructure failure                                             | Service and HTTP mapping | Stable infrastructure response without leaking low-level details                              |
| Pydantic response serialization                                               | Boundary model           | Structured JSON contains the documented response fields                                       |
| Endpoint test-client dependency                                               | Test environment         | Uses the resolved `httpx2==2.7.0`; installation instructions do not add `httpx`               |
| Multipart parser dependency                                                   | Runtime environment      | Uses `python-multipart==0.0.32`                                                               |
| Static typing                                                                 | Repository quality gate  | Strict mypy succeeds for the verified repository files                                        |
| Linting                                                                       | Repository quality gate  | Ruff check succeeds for the verified repository files                                         |
| Formatting                                                                    | Repository quality gate  | Ruff format check succeeds for the verified repository files                                  |

### Exact repository test integration

The exact verified repository tests were not attached to the V2 generation input. They must not be reconstructed from narrative examples or inferred module names.

Where the canonical document needs complete source listings, Codex must insert the verified `tests/` files directly:

**Codex integration required**

The same rule applies to verified application files referenced by those tests. Narrative examples demonstrate concepts; they are not substitutes for repository source.

### Byte-exact test inputs

Tests that depend on newline representation should use direct bytes:

```python
content = b"alpha\r\nbeta\rgamma"
```

Multipart endpoint tests should place those bytes directly in the file tuple:

```python
files = {
    "file": (
        "sample.txt",
        b"alpha\r\nbeta",
        "text/plain",
    )
}
```

This avoids platform-dependent text-mode newline conversion.

When a separate test genuinely requires a temporary file outside this upload-oriented service, exact bytes should be written with `write_bytes()`. The Week 1 service itself does not accept or open that file through its HTTP contract.

### Structured logging assertions

`logging` fields supplied through `extra` become attributes on captured `LogRecord` objects:

```python
logger.info(
    "document_extraction_completed",
    extra={
        "correlation_id": correlation_id,
        "character_count": character_count,
    },
)
```

The active formatter determines whether those attributes appear in `caplog.text`. A robust test separates rendered-message assertions from structured-field assertions:

```python
assert secret_text not in caplog.text
assert secret_filename not in caplog.text

assert any(
    getattr(record, "correlation_id", None)
    == "safe-correlation-123"
    for record in caplog.records
)
```

A failure-code assertion should use the same record-oriented approach:

```python
assert any(
    getattr(record, "failure_code", None)
    == "document_decoding_failed"
    for record in caplog.records
)
```

### Repository validation commands

The repository quality gates recorded by Codex technical review were:

```text
python -m pytest -q
python -m ruff check document_service tests
python -m ruff format --check document_service tests
python -m mypy --strict document_service tests
```

Codex technical review recorded the following final results for the verified repository files:

```text
26 passed in 0.33s

All checks passed!

14 files already formatted

Success: no issues found in 14 source files
```

These results are attributed to Codex. ChatGPT did not run the commands. The results apply to the repository files used during technical review, not automatically to every standalone snippet in this learning module or to later modifications.

### What passing tests do not prove

Even the recorded passing repository suite does not establish that:

* authentication is implemented;
* authorization or tenant isolation is correct;
* uploaded content is safe to persist;
* response bodies are appropriately bounded;
* the service is deployable in production;
* concurrency has been tuned;
* all Unicode edge cases are covered;
* media-type metadata is truthful;
* all dependency combinations remain compatible after upgrades;
* logs are safe under every future handler and formatter;
* all possible multipart parser failures have been exercised;
* the service is protected against every denial-of-service pattern.

Tests provide evidence for specific behavior under the tested environment and inputs. They do not replace threat modelling, operational validation, or production review.

## Interview preparation

### 1. Mutable versus immutable objects

**Question:** Why does mutability matter in AI pipelines?

**Strong answer:**

Python variables hold references to objects. Multiple pipeline components can therefore refer to the same list, dictionary, model state, retrieved-document collection, or prompt fragment. If one component mutates that shared object, every other component observes the changed state.

This matters because shared mutation can cause:

* prompts to vary according to execution order;
* cached results to become inconsistent;
* evaluation inputs to change after scoring;
* request state to leak across operations;
* tests to pass or fail depending on earlier tests;
* logging or observability code to alter the payload it is inspecting.

A frozen dataclass prevents normal attribute reassignment, but immutability is shallow. A frozen dataclass containing a list still refers to a mutable list. Stronger value semantics require immutable nested types such as tuples, defensive copying, or APIs that return new values instead of mutating shared ones.

**Trade-offs:**

* Copying large collections consumes time and memory.
* Deep immutability can make incremental construction less convenient.
* Mutable objects are appropriate when controlled state transitions are part of the object’s responsibility.
* The goal is not to ban mutation; it is to make ownership and mutation explicit.

**Follow-up questions:**

* Does `frozen=True` recursively freeze nested data?
* What is aliasing?
* When would a defensive copy be too expensive?
* How can mutation corrupt a cache key?
* How would you design shared metadata that must remain stable?

---

### 2. Plain classes, dataclasses, frozen dataclasses, and Pydantic models

**Question:** How do you choose among these class forms?

**Strong answer:**

I choose according to responsibility.

A plain class is suitable when an object owns behavior, dependencies, lifecycle, or controlled state transitions. `DocumentExtractionService` is a plain class because it owns an injected decoder dependency and coordinates extraction.

A dataclass is useful for internal data records where generated initialization, representation, and comparison are helpful. A frozen dataclass is suitable for internal commands and results that should not be rebound after validation.

A Pydantic model is a Python class derived from `BaseModel`. It is appropriate at an untrusted boundary where runtime parsing, validation, configuration, serialization, and schema generation are required.

For this service, multipart metadata should be validated at the boundary and then converted into narrow internal values. The decoder remains a replaceable class behind a protocol. Stateless newline normalization remains a function because a class would add no state, dependency, or lifecycle.

**Trade-offs:**

* Pydantic adds runtime behavior and library coupling.
* Dataclasses are lighter but do not automatically validate untrusted values.
* Frozen values simplify reasoning but can be inconvenient during staged construction.
* Plain classes are flexible but can become oversized collections of unrelated methods.

**Follow-up questions:**

* Is a Pydantic model still a normal Python class?
* Can a dataclass define methods?
* When is a static method less clear than a module function?
* Why should the service compose with the decoder rather than inherit from it?
* Where should conversion from a Pydantic model to a domain value occur?

---

### 3. Static typing versus runtime validation

**Question:** Why are both needed?

**Strong answer:**

Static typing helps developers and analysis tools reason about code before execution. It catches inconsistent calls, improves editor support, documents interfaces, and makes refactoring safer.

It does not normally stop an arbitrary runtime caller from supplying a value of the wrong type. An annotation such as `content: bytes` is not an automatic runtime guard.

Runtime validation checks the values that actually cross a trust boundary. Multipart form values, uploaded metadata, model-generated structures, queue messages, and external API responses must be validated during execution.

In the Week 1 service:

* type hints describe the internal interfaces;
* Pydantic validates untrusted metadata;
* the size check validates the uploaded byte count;
* the decoder validates the byte encoding;
* the service validates filename and media-type policy.

**Trade-offs:**

* Excessive repeated validation can add noise and cost inside already trusted code.
* Coercive runtime validation may hide upstream errors.
* Strict validation can reject inputs that a permissive interface might safely normalize.
* Static type success does not prove runtime correctness or business validity.

**Follow-up questions:**

* Can mypy prove that uploaded bytes are valid UTF-8?
* Does valid JSON prove that an LLM response is truthful?
* What should happen immediately after an untyped SDK response enters the application?
* When is coercion useful?
* Why should internal code avoid spreading untyped dictionaries?

---

### 4. Generators versus lists

**Question:** When would you use a generator instead of a list?

**Strong answer:**

A generator produces values lazily and is normally consumed once. It can reduce peak memory, reduce time to the first result, and avoid producing values the caller never requests.

A list is eagerly materialized and uses memory for all elements, but it is repeatable, has simpler failure timing, and usually has a clearer resource lifecycle.

Generators introduce important operational considerations:

* errors may occur during iteration rather than construction;
* partial consumption complicates retries;
* a suspended generator may retain a resource;
* a second iteration over the same generator returns no values;
* logging and metrics may record only partial progress.

The Week 1 HTTP endpoint does not expose a streaming generator. It performs one bounded upload read, decodes the bounded bytes, and returns a complete result. Generators are taught as a durable pipeline concept, not as an instruction to add advanced HTTP streaming.

**Trade-offs:**

* Lists simplify repeatability and debugging.
* Generators reduce memory for large or indefinite sequences.
* Materializing a generator removes laziness and may defeat its purpose.
* Keeping resources inside a generator requires explicit ownership and cleanup.

**Follow-up questions:**

* When does a generator body begin executing?
* What happens during a second pass?
* How do deferred exceptions affect API error handling?
* How would you close a partially consumed generator?
* Why is a generator not automatically faster?

---

### 5. Threads versus async

**Question:** How do you decide between threads and async?

**Strong answer:**

Async is a good fit when the dependency stack exposes genuinely awaitable I/O. A coroutine can suspend while waiting so that the event loop can run other tasks.

Threads are useful when integrating blocking I/O libraries that do not provide awaitable APIs. They require bounded worker and queue capacity because unbounded thread submission can create memory pressure, contention, and downstream overload.

Neither model automatically accelerates CPU-heavy pure-Python work. CPU-bound workloads may require processes, native code, accelerators, external workers, or simply sequential execution.

In this service, `UploadFile.read()` is awaitable, so the thin route is `async def`. The decoder and normalization functions operate synchronously over a payload already bounded at 1 MiB. Making those functions async would add ceremony without creating suspension points.

**Trade-offs:**

* Async requires compatible libraries throughout the relevant call chain.
* Threads integrate synchronous code but introduce shared-state and cancellation complications.
* Processes add serialization, startup, and lifecycle overhead.
* Sequential execution may be operationally simpler and sufficient.
* Concurrency always requires backpressure and capacity decisions.

**Follow-up questions:**

* Does `async def` make a blocking call non-blocking?
* Can a running thread be forcibly cancelled safely?
* What is backpressure?
* Why must executor capacity be bounded?
* When would a process pool be inappropriate?

---

### 6. Exception translation

**Question:** Where should exceptions be translated?

**Strong answer:**

An exception should be translated where the current abstraction understands the lower-level failure and can express it in terms meaningful to its caller.

The decoder understands `UnicodeDecodeError` and can translate it into a decoder-specific failure while preserving the cause with `raise ... from exc`.

The extraction service can translate that decoder failure into a stable document-decoding category and attach a safe correlation identifier.

The HTTP layer maps application failure categories to status codes and stable response bodies. It should not need to understand Python codec internals.

I avoid translating an exception when the current layer adds no useful meaning. I also avoid exposing raw low-level messages because they may be unstable or contain sensitive values.

**Trade-offs:**

* Too little translation leaks implementation details.
* Too much translation creates repetitive wrappers and obscures the original cause.
* Public error messages should be stable and safe.
* Internal traces may retain more diagnostic context than public responses.

**Follow-up questions:**

* What does explicit exception chaining preserve?
* When should an exception propagate unchanged?
* Why is `except Exception: return ""` dangerous?
* Which layer should decide HTTP `415`?
* Where should retry policy live?

---

### 7. Safe logging

**Question:** What should a useful extraction log contain?

**Strong answer:**

A useful log should describe the operation without duplicating its sensitive payload.

Appropriate fields include:

* a stable event name;
* a safe correlation identifier;
* declared and upload media types;
* byte count;
* character count;
* line count;
* stable failure code;
* duration when measured deliberately.

The log should exclude:

* uploaded bytes;
* decoded document text;
* filename;
* arbitrary multipart objects;
* credentials;
* PII;
* raw model outputs;
* unreviewed low-level exception messages.

Fields passed through `extra` become `LogRecord` attributes. They are not guaranteed to appear in `caplog.text`, because that string reflects the active formatter. Tests should inspect `caplog.records` for structured attributes and use `caplog.text` to detect forbidden rendered payloads.

**Trade-offs:**

* More context improves diagnosis but increases leakage risk.
* Tracebacks are useful for unexpected failures but can expose low-level values.
* Logging every expected client error at `ERROR` can create noise.
* Logging too little makes distributed failures difficult to trace.

**Follow-up questions:**

* Is a filename sensitive?
* When should `logger.exception` be used?
* Who configures the root logger?
* How would you test that a secret marker is absent?
* Why should rejected validation values usually not be logged?

---

### 8. Thin routes

**Question:** What makes the Week 1 route thin?

**Strong answer:**

The route handles concerns specific to the HTTP upload boundary:

1. receive multipart fields `media_type`, `correlation_id`, and `file`;
2. await `UploadFile.read()` with a limit of 1 MiB plus one sentinel byte;
3. reject an oversized upload with HTTP `413`;
4. construct validated metadata and an internal command;
5. invoke the extraction service;
6. convert the result into the response model.

The route does not implement strict UTF-8 decoding, newline normalization, empty-content policy, filename policy, media-type policy, or operational logging rules. Those responsibilities remain in the decoder, service, models, and domain functions.

This separation allows the service to be tested without an HTTP client and prevents framework concerns from spreading through the domain.

**Trade-offs:**

* A separate service and conversion layer add files and code.
* Very small applications can be over-layered.
* The separation is justified when boundaries, failure categories, and testing needs are genuinely distinct.
* The route still owns the bounded read because reading `UploadFile` is an HTTP-boundary operation.

**Follow-up questions:**

* Should the service receive `UploadFile` directly?
* Where should HTTP `413` be decided?
* Can a route contain any validation?
* How do dependency overrides improve endpoint tests?
* When would a service layer be unnecessary?

---

### 9. Bounded uploads and the sentinel byte

**Question:** Why read 1 MiB plus one byte?

**Strong answer:**

The accepted maximum is 1,048,576 bytes. Reading only that amount cannot distinguish an exactly-at-limit upload from the first 1 MiB of a larger upload.

The route therefore requests at most 1,048,577 bytes. If the returned content is longer than 1,048,576 bytes, the extra sentinel byte proves that the upload exceeds the limit. The route can reject it with HTTP `413` and code `document_too_large` without requesting an unbounded read.

This is a bounded-memory contract. It does not rely on a caller-supplied size declaration.

**Trade-offs:**

* The full accepted document is still held in memory.
* A 1 MiB limit is a product and resource-policy decision.
* Making the limit configurable requires validation and deployment-specific review.
* Advanced streaming, incremental parsing, and request-body enforcement are outside Week 1.

**Follow-up questions:**

* Why is a declared file size insufficient?
* Is an exactly 1 MiB upload accepted?
* What happens with multibyte UTF-8 characters?
* Why is byte count different from character count?
* What additional controls would a production upload service need?

---

### 10. Why arbitrary server paths are unsafe

**Question:** Why must an upload API not accept an arbitrary server location from the caller?

**Strong answer:**

A caller-controlled server location asks the application to access resources using the server process’s permissions. That can expose configuration files, credentials, application source, other tenants’ data, mounted volumes, or operating-system resources.

Path normalization alone is not a complete solution. Symbolic links, alternate path forms, mount boundaries, race conditions, and platform differences can still make file access difficult to secure.

The Week 1 contract avoids that class of risk by accepting uploaded bytes through `UploadFile`. The filename is treated only as untrusted metadata for suffix validation and is never opened by the application.

A production system that needs stored documents should use opaque identifiers and an authorization-aware storage abstraction rather than accepting arbitrary locations.

**Trade-offs:**

* Uploading bytes consumes network and application resources.
* An upload API still needs size, media-type, authorization, and retention controls.
* Opaque identifiers require persistence and ownership models, which are outside Week 1.
* Avoiding arbitrary locations removes one risk category but does not make uploaded content inherently safe.

**Follow-up questions:**

* Why is removing `../` insufficient?
* Can a filename be safely used as a storage key?
* How would tenant-aware storage change the design?
* What role do symbolic links play?
* Why should filenames be excluded from logs?

## Knowledge check

### Questions

1. Which three multipart fields does the endpoint require?
2. What FastAPI type represents the uploaded file?
3. Why is the route declared with `async def`?
4. What is the fixed upload limit in bytes?
5. How many bytes may the route request from `UploadFile.read()`?
6. What purpose does the extra byte serve?
7. What HTTP status is returned for an oversized upload?
8. What stable error code represents an oversized upload?
9. Is an upload of exactly 1,048,576 bytes within the size limit?
10. Why should the route not call `await file.read()` without a size argument?
11. Which filename suffix is supported?
12. What must the declared `media_type` equal?
13. What must the upload content type equal?
14. What happens when the two media types differ?
15. Does a `text/plain` content type prove that the bytes are valid text?
16. What encoding is required?
17. What decoding-error policy is required?
18. Why is `errors="ignore"` inappropriate?
19. How should a zero-byte upload be handled?
20. How should whitespace-only decoded text be handled?
21. What narrow method must the decoder protocol expose?
22. Why is the decoder injected into the service?
23. Does a protocol require the fake decoder to inherit from it?
24. What does a normal Python type annotation guarantee at runtime?
25. What does Pydantic add at an untrusted boundary?
26. From which class do Pydantic models inherit?
27. When is a plain class more appropriate than a dataclass?
28. When is a frozen dataclass useful?
29. Why is frozen-dataclass immutability shallow?
30. Why is newline normalization a function rather than a service class?
31. What does exception chaining preserve?
32. At which layer should `UnicodeDecodeError` first be translated?
33. Which layer should map an application failure to HTTP `415`?
34. Why should uploaded text never be logged?
35. Why should the filename normally not be logged?
36. Where are values passed through logging’s `extra` argument stored?
37. Why might a correlation identifier not appear in `caplog.text`?
38. How should a logging test inspect a structured correlation identifier?
39. Why should exact newline tests use byte payloads?
40. What happens when an exhausted generator is iterated again?
41. Name one advantage of a generator over a list.
42. Name one disadvantage of a generator compared with a list.
43. Does changing a function to `async def` make CPU work faster?
44. When are threads commonly considered?
45. Why must thread-pool capacity be bounded?
46. What responsibilities belong in the thin route?
47. What responsibilities belong in the extraction service?
48. Why should the service not receive a caller-selected server location?
49. Which multipart parsing dependency is pinned?
50. Which resolved test-client dependency is pinned?
51. Did ChatGPT execute the recorded repository suite?
52. Who recorded the 26 passing tests?
53. To what files do the recorded Ruff and mypy results apply?
54. Are response-size limits part of Week 1?
55. Are authentication and authorization part of Week 1?
56. Is persistence part of Week 1?
57. Is production concurrency tuning part of Week 1?
58. What must happen before exact verified repository test files are reproduced in the canonical module?

### Answer key

1. `media_type`, `correlation_id`, and `file`.
2. `UploadFile`.
3. Because `UploadFile.read()` is awaitable.
4. 1,048,576 bytes.
5. 1,048,577 bytes.
6. It proves that the upload exceeds the accepted maximum.
7. HTTP `413`.
8. `document_too_large`.
9. Yes, subject to the remaining validation rules.
10. It would permit an unbounded in-memory read.
11. `.txt`.
12. `text/plain`.
13. `text/plain`.
14. The upload is rejected as an unsupported or inconsistent format.
15. No; it is caller-controlled metadata.
16. UTF-8.
17. Strict decoding.
18. It can silently discard bytes and change meaning.
19. Reject it as empty content.
20. Reject it as empty content.
21. `decode(content: bytes) -> str`.
22. To separate orchestration from decoding and permit deterministic substitutes in tests.
23. No; structural compatibility is sufficient for a protocol.
24. It communicates intent but does not generally enforce the value automatically.
25. Runtime parsing, validation, configuration, serialization, and schema behavior.
26. `pydantic.BaseModel`.
27. When the object owns behavior, dependencies, lifecycle, or controlled state.
28. For internal value-like commands or results that should not be rebound after construction.
29. Nested mutable objects can still be changed.
30. It has no state, dependency, or lifecycle.
31. The original causal exception.
32. At the UTF-8 decoder boundary.
33. The HTTP application boundary.
34. It may contain confidential, personal, regulated, or proprietary information.
35. It can reveal identities, document subjects, or client-controlled sensitive text.
36. On the emitted `LogRecord`.
37. The active formatter may not render that record attribute.
38. Inspect attributes on `caplog.records`.
39. Text-mode newline translation differs across operating systems.
40. It produces no additional values.
41. Lower peak memory, earlier first result, or avoidance of unnecessary work.
42. Single consumption, deferred failures, harder retries, or resource-lifetime complexity.
43. No.
44. When integrating blocking I/O libraries that do not provide awaitable APIs.
45. To prevent unbounded queues, memory pressure, contention, and overload.
46. Receive multipart fields, await the bounded read, reject oversize, construct boundary values, call the service, and return the response.
47. Format policy, decoder invocation, normalization, empty-content validation, domain-result creation, and safe lifecycle logging.
48. It could cause the application to access resources using the server process’s permissions.
49. `python-multipart==0.0.32`.
50. `httpx2==2.7.0`.
51. No.
52. Codex technical review.
53. The verified repository files used by Codex, not every narrative snippet.
54. No.
55. No.
56. No.
57. No.
58. Codex must insert the attached or otherwise verified repository source exactly.

## Weekly deliverables

1. A Python 3.13.12 virtual environment.
2. A pinned `requirements.txt` containing:

   * `fastapi==0.139.2`;
   * `pydantic==2.13.4`;
   * `python-multipart==0.0.32`;
   * `uvicorn==0.51.0`.
3. A pinned `requirements-dev.txt` containing:

   * `-r requirements.txt`;
   * `httpx2==2.7.0`;
   * `mypy==2.3.0`;
   * `pytest==9.1.1`;
   * `ruff==0.15.22`.
4. A FastAPI endpoint at `/v1/documents/extract`.
5. A multipart contract containing `media_type`, `correlation_id`, and `file`.
6. An `async def` route that awaits the upload read.
7. A bounded read of at most 1 MiB plus one sentinel byte.
8. A stable HTTP `413` response with code `document_too_large`.
9. Validation requiring:

   * `.txt` filename suffix;
   * declared media type `text/plain`;
   * upload content type `text/plain`;
   * matching media types;
   * strict UTF-8;
   * non-whitespace content.
10. Pydantic v2 metadata, response, and error models.
11. Typed internal command and result values.
12. A decoder protocol exposing `decode(content: bytes) -> str`.
13. An injected strict UTF-8 decoder.
14. A separated extraction service.
15. Pure newline-normalization and line-count logic.
16. An explicit application exception hierarchy.
17. Stable HTTP error mappings.
18. Module-level loggers created with `logging.getLogger(__name__)`.
19. Logging that excludes uploaded text and filename.
20. Tests using direct byte payloads where exact newlines matter.
21. Logging tests that distinguish `caplog.text` from `caplog.records`.
22. Multipart endpoint tests using the resolved Starlette test client.
23. Tests covering success, size boundaries, format rejection, media-type mismatch, invalid UTF-8, empty content, decoder failure, and log leakage.
24. A written design for the async batch-extraction exercise.
25. Written answers to the interview questions.
26. A technical-review record distinguishing repository execution from narrative examples.
27. Exact verified repository source inserted by Codex wherever full implementation or test listings are required.
28. A human-review checklist with unresolved decisions clearly identified.

## Definition of done

Week 1 is ready for human review when all applicable items below are satisfied.

### Document structure

* [ ] All 18 required H2 sections exist in the required order.
* [ ] YAML front matter is valid.
* [ ] Document status remains `draft`.
* [ ] Document version is `0.2.0`.
* [ ] Human review remains `pending`.
* [ ] No fixed eight-hour constraint appears.
* [ ] No content after this continuation is missing or truncated.

### HTTP contract

* [ ] The endpoint uses multipart form data.
* [ ] The required fields are `media_type`, `correlation_id`, and `file`.
* [ ] The uploaded document is represented by `UploadFile`.
* [ ] The route is `async def`.
* [ ] The route awaits `UploadFile.read()`.
* [ ] No caller-selected server location is accepted.
* [ ] No application example opens a resource selected through caller-supplied server location metadata.
* [ ] The filename is treated only as untrusted metadata.

### Upload-size enforcement

* [ ] The accepted maximum is 1,048,576 bytes.
* [ ] The route requests at most 1,048,577 bytes.
* [ ] The additional byte is documented as a sentinel.
* [ ] Exactly-at-limit content is accepted for further validation.
* [ ] Above-limit content returns HTTP `413`.
* [ ] The stable oversized code is `document_too_large`.
* [ ] No unbounded upload read appears.
* [ ] Making the limit configurable remains optional exercise work without weakening the bound.

### Format and content validation

* [ ] Only `.txt` is supported.
* [ ] The declared media type must be `text/plain`.
* [ ] The upload content type must be `text/plain`.
* [ ] The two media types must match.
* [ ] UTF-8 decoding is strict.
* [ ] Invalid UTF-8 has a stable failure category.
* [ ] Zero-byte content is rejected.
* [ ] Whitespace-only content is rejected.
* [ ] Newlines are normalized without silently rewriting other text.
* [ ] Media-type metadata is not described as proof of the actual content.

### Architecture

* [ ] The FastAPI route is thin.
* [ ] Upload reading remains at the HTTP boundary.
* [ ] Extraction orchestration is in a separate service.
* [ ] Strict decoding is behind an injected narrow protocol.
* [ ] The protocol is `decode(content: bytes) -> str`.
* [ ] Domain modules do not import FastAPI.
* [ ] Pure transformations remain module functions.
* [ ] Dependency direction is clear.
* [ ] No speculative plugin framework has been introduced.
* [ ] Another text adapter can be added without changing the public service behavior.

### Python classes

* [ ] Instance state is explained.
* [ ] Class attributes are explained.
* [ ] `__init__` and construction are explained.
* [ ] Instance, class, and static methods are distinguished.
* [ ] Composition is preferred for service-to-decoder collaboration.
* [ ] Appropriate inheritance examples are included.
* [ ] Mutable class-attribute hazards are explained.
* [ ] The module explains when a class is unnecessary.

### Types and models

* [ ] Public interfaces use explicit type hints.
* [ ] No unexplained `Any` appears.
* [ ] Static typing is not described as runtime validation.
* [ ] The decoder uses a typed protocol.
* [ ] Pydantic models are described as `BaseModel` subclasses.
* [ ] Annotated fields are covered.
* [ ] `ConfigDict` and model configuration are covered.
* [ ] Field validators are covered.
* [ ] Model validators are covered.
* [ ] Pydantic v2 serialization methods are covered.
* [ ] Plain classes, dataclasses, frozen dataclasses, and Pydantic models have distinct responsibilities.
* [ ] Shallow immutability is explained.

### Exceptions

* [ ] Validation, unsupported-format, oversized, decoding, empty-content, extraction, and infrastructure failures are distinguishable.
* [ ] Low-level decoding failures are translated at the decoder boundary.
* [ ] Causal context is preserved with exception chaining.
* [ ] Public messages do not expose uploaded content or filename.
* [ ] Broad exception suppression is absent.
* [ ] HTTP status mapping remains an HTTP-layer responsibility.

### Logging

* [ ] Module loggers use `logging.getLogger(__name__)`.
* [ ] Library modules do not configure the root logger.
* [ ] Uploaded bytes are never logged.
* [ ] Decoded text is never logged.
* [ ] Filename is never logged.
* [ ] Safe correlation identifiers are available as structured fields.
* [ ] Stable failure codes are available as structured fields.
* [ ] The distinction between `caplog.text` and `caplog.records` is explicit.
* [ ] Tests inspect `LogRecord` attributes for fields supplied through `extra`.
* [ ] Tests check forbidden content in rendered logs.

### Iteration and async

* [ ] Iterable, iterator, and generator concepts are explained.
* [ ] Generator single consumption is demonstrated.
* [ ] Deferred failures are explained.
* [ ] Resource lifetime is explained.
* [ ] The current endpoint is not presented as advanced streaming.
* [ ] `UploadFile.read()` is identified as awaitable.
* [ ] Async is presented as a concurrency choice, not a universal optimization.
* [ ] Blocking and CPU-bound work are distinguished from awaitable I/O.
* [ ] Threads, async, processes, and sequential execution can be compared.
* [ ] Production concurrency tuning remains outside Week 1.

### Testing

* [ ] Multipart success behavior is tested.
* [ ] Missing multipart fields are tested.
* [ ] Exactly-at-limit upload behavior is tested.
* [ ] Above-limit upload behavior is tested.
* [ ] HTTP `413` and `document_too_large` are tested.
* [ ] `.txt` suffix policy is tested.
* [ ] Declared media-type policy is tested.
* [ ] Upload content-type policy is tested.
* [ ] Media-type mismatch is tested.
* [ ] Valid UTF-8 is tested.
* [ ] Invalid UTF-8 is tested.
* [ ] Empty content is tested.
* [ ] Whitespace-only content is tested.
* [ ] Decoder failure translation is tested.
* [ ] Newline normalization uses byte-exact input.
* [ ] Sensitive log leakage is tested.
* [ ] Structured log fields are asserted through `caplog.records`.
* [ ] Tests are deterministic and isolated.
* [ ] Fakes or mocks are limited to external boundaries.
* [ ] Exact verified test files are inserted by Codex rather than reconstructed.

### Dependencies and technical verification

* [ ] `python-multipart==0.0.32` is present.
* [ ] `httpx2==2.7.0` is present.
* [ ] No instruction installs `httpx`.
* [ ] Python 3.13.12 remains the target.
* [ ] Resolved versions are recorded.
* [ ] Codex’s recorded `26 passed` result is clearly attributed.
* [ ] Ruff check results are clearly attributed to Codex.
* [ ] Ruff format-check results are clearly attributed to Codex.
* [ ] Strict mypy results are clearly attributed to Codex.
* [ ] The module states that repository results do not validate every narrative snippet.
* [ ] ChatGPT does not claim to have executed commands or checked every URL.

### Exercises and interview readiness

* [ ] Every independent exercise includes acceptance criteria.
* [ ] Every independent exercise includes edge cases.
* [ ] Every independent exercise includes optional hints.
* [ ] Exercises do not provide complete solutions.
* [ ] Interview answers include reasoning and trade-offs.
* [ ] Interview follow-up questions are included.
* [ ] Mutable versus immutable objects are covered.
* [ ] Class choices are covered.
* [ ] Static typing versus runtime validation is covered.
* [ ] Generators versus lists are covered.
* [ ] Threads versus async is covered.
* [ ] Exception translation is covered.
* [ ] Safe logging is covered.
* [ ] Thin routes are covered.
* [ ] Bounded uploads are covered.
* [ ] The danger of arbitrary server locations is covered.

### Scope control

* [ ] Response-size limits remain outside Week 1.
* [ ] Authentication remains outside Week 1.
* [ ] Authorization remains outside Week 1.
* [ ] Tenant isolation remains outside Week 1.
* [ ] Persistence remains outside Week 1.
* [ ] Deployment remains outside Week 1.
* [ ] Production server configuration remains outside Week 1.
* [ ] Advanced HTTP streaming remains outside Week 1.
* [ ] Concurrency tuning remains outside Week 1.
* [ ] Cloud storage, queues, databases, OCR, PDFs, LLMs, RAG, and agents remain outside Week 1.

## Sources and further reading

The sources below are official documentation, specifications, or official package-index pages. Live documentation can change. The links have not all been exhaustively revalidated by ChatGPT for this continuation.

### Python 3.13 and environment management

* Python 3.13.12 release: [https://www.python.org/downloads/release/python-31312/](https://www.python.org/downloads/release/python-31312/)
* Python virtual environments: [https://docs.python.org/3.13/library/venv.html](https://docs.python.org/3.13/library/venv.html)
* `pip install`: [https://pip.pypa.io/en/stable/cli/pip_install/](https://pip.pypa.io/en/stable/cli/pip_install/)

### Python classes and object behavior

* Python classes tutorial: [https://docs.python.org/3.13/tutorial/classes.html](https://docs.python.org/3.13/tutorial/classes.html)
* Python data model: [https://docs.python.org/3.13/reference/datamodel.html](https://docs.python.org/3.13/reference/datamodel.html)
* Built-in types: [https://docs.python.org/3.13/library/stdtypes.html](https://docs.python.org/3.13/library/stdtypes.html)

### Type hints and protocols

* Python `typing`: [https://docs.python.org/3.13/library/typing.html](https://docs.python.org/3.13/library/typing.html)
* PEP 484 — Type Hints: [https://peps.python.org/pep-0484/](https://peps.python.org/pep-0484/)
* PEP 544 — Protocols: [https://peps.python.org/pep-0544/](https://peps.python.org/pep-0544/)

### Dataclasses and immutability

* Python `dataclasses`: [https://docs.python.org/3.13/library/dataclasses.html](https://docs.python.org/3.13/library/dataclasses.html)
* PEP 557 — Data Classes: [https://peps.python.org/pep-0557/](https://peps.python.org/pep-0557/)

### Exceptions and cleanup

* Python errors and exceptions: [https://docs.python.org/3.13/tutorial/errors.html](https://docs.python.org/3.13/tutorial/errors.html)
* Python `contextlib`: [https://docs.python.org/3.13/library/contextlib.html](https://docs.python.org/3.13/library/contextlib.html)
* PEP 343 — The `with` Statement: [https://peps.python.org/pep-0343/](https://peps.python.org/pep-0343/)

### Logging

* Python Logging HOWTO: [https://docs.python.org/3.13/howto/logging.html](https://docs.python.org/3.13/howto/logging.html)
* Python logging reference: [https://docs.python.org/3.13/library/logging.html](https://docs.python.org/3.13/library/logging.html)

### Iterators and generators

* Python iterators: [https://docs.python.org/3.13/tutorial/classes.html#iterators](https://docs.python.org/3.13/tutorial/classes.html#iterators)
* Python generators: [https://docs.python.org/3.13/tutorial/classes.html#generators](https://docs.python.org/3.13/tutorial/classes.html#generators)
* Generator expressions: [https://docs.python.org/3.13/reference/expressions.html#generator-expressions](https://docs.python.org/3.13/reference/expressions.html#generator-expressions)
* PEP 255 — Simple Generators: [https://peps.python.org/pep-0255/](https://peps.python.org/pep-0255/)

### Async and concurrency

* Python `asyncio`: [https://docs.python.org/3.13/library/asyncio.html](https://docs.python.org/3.13/library/asyncio.html)
* Coroutines and tasks: [https://docs.python.org/3.13/library/asyncio-task.html](https://docs.python.org/3.13/library/asyncio-task.html)
* `concurrent.futures`: [https://docs.python.org/3.13/library/concurrent.futures.html](https://docs.python.org/3.13/library/concurrent.futures.html)
* FastAPI async guidance: [https://fastapi.tiangolo.com/async/](https://fastapi.tiangolo.com/async/)

### Pydantic v2

* Models: [https://docs.pydantic.dev/latest/concepts/models/](https://docs.pydantic.dev/latest/concepts/models/)
* Configuration: [https://docs.pydantic.dev/latest/concepts/config/](https://docs.pydantic.dev/latest/concepts/config/)
* Fields: [https://docs.pydantic.dev/latest/concepts/fields/](https://docs.pydantic.dev/latest/concepts/fields/)
* Validators: [https://docs.pydantic.dev/latest/concepts/validators/](https://docs.pydantic.dev/latest/concepts/validators/)
* Serialization: [https://docs.pydantic.dev/latest/concepts/serialization/](https://docs.pydantic.dev/latest/concepts/serialization/)
* Strict mode: [https://docs.pydantic.dev/latest/concepts/strict_mode/](https://docs.pydantic.dev/latest/concepts/strict_mode/)
* Error handling: [https://docs.pydantic.dev/latest/errors/errors/](https://docs.pydantic.dev/latest/errors/errors/)
* Migration guidance: [https://docs.pydantic.dev/latest/migration/](https://docs.pydantic.dev/latest/migration/)

### FastAPI multipart uploads and boundaries

* Request files and `UploadFile`: [https://fastapi.tiangolo.com/tutorial/request-files/](https://fastapi.tiangolo.com/tutorial/request-files/)
* Forms and files: [https://fastapi.tiangolo.com/tutorial/request-forms-and-files/](https://fastapi.tiangolo.com/tutorial/request-forms-and-files/)
* Dependencies: [https://fastapi.tiangolo.com/tutorial/dependencies/](https://fastapi.tiangolo.com/tutorial/dependencies/)
* Response models: [https://fastapi.tiangolo.com/tutorial/response-model/](https://fastapi.tiangolo.com/tutorial/response-model/)
* Error handling: [https://fastapi.tiangolo.com/tutorial/handling-errors/](https://fastapi.tiangolo.com/tutorial/handling-errors/)
* Larger applications and routers: [https://fastapi.tiangolo.com/tutorial/bigger-applications/](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
* FastAPI testing: [https://fastapi.tiangolo.com/tutorial/testing/](https://fastapi.tiangolo.com/tutorial/testing/)
* Dependency overrides in tests: [https://fastapi.tiangolo.com/advanced/testing-dependencies/](https://fastapi.tiangolo.com/advanced/testing-dependencies/)

### Multipart and test-client dependencies

* `python-multipart` package index: [https://pypi.org/project/python-multipart/](https://pypi.org/project/python-multipart/)
* Starlette `TestClient`: [https://www.starlette.io/testclient/](https://www.starlette.io/testclient/)
* `httpx2` package index: [https://pypi.org/project/httpx2/](https://pypi.org/project/httpx2/)

The repository pins:

```text
python-multipart==0.0.32
httpx2==2.7.0
```

The resolved repository dependency takes precedence over generic installation guidance for this reviewed version. This module does not instruct installation of `httpx`.

### pytest

* Assertions and expected exceptions: [https://docs.pytest.org/en/stable/how-to/assert.html](https://docs.pytest.org/en/stable/how-to/assert.html)
* Fixtures: [https://docs.pytest.org/en/stable/how-to/fixtures.html](https://docs.pytest.org/en/stable/how-to/fixtures.html)
* Parametrization: [https://docs.pytest.org/en/stable/how-to/parametrize.html](https://docs.pytest.org/en/stable/how-to/parametrize.html)
* Logging and `caplog`: [https://docs.pytest.org/en/stable/how-to/logging.html](https://docs.pytest.org/en/stable/how-to/logging.html)

### Ruff and mypy

* Ruff documentation: [https://docs.astral.sh/ruff/](https://docs.astral.sh/ruff/)
* mypy documentation: [https://mypy.readthedocs.io/en/stable/](https://mypy.readthedocs.io/en/stable/)
* mypy strict-mode configuration reference: [https://mypy.readthedocs.io/en/stable/config_file.html](https://mypy.readthedocs.io/en/stable/config_file.html)

## Assumptions and unresolved questions

### Assumptions

1. Python 3.13.12 remains the required interpreter for this module.
2. The endpoint path remains `/v1/documents/extract`.
3. The request uses multipart form data.
4. The multipart fields are exactly `media_type`, `correlation_id`, and `file`.
5. The file object is a FastAPI `UploadFile`.
6. The route is `async def` because it awaits `UploadFile.read()`.
7. The maximum accepted upload is exactly 1,048,576 bytes.
8. The route requests at most 1,048,577 bytes.
9. Content larger than 1 MiB returns HTTP `413`.
10. The stable oversized code is `document_too_large`.
11. The only supported suffix is `.txt`.
12. The declared media type must be exactly `text/plain`.
13. The upload content type must be exactly `text/plain`.
14. The declared and upload media types must match.
15. UTF-8 decoding uses strict error handling.
16. Empty and whitespace-only documents are rejected.
17. Newline normalization converts `\r\n` and `\r` to `\n`.
18. The service receives bounded bytes rather than an upload stream.
19. The service depends on an injected decoder exposing `decode(content: bytes) -> str`.
20. Uploaded text and filename are excluded from logs.
21. A safe correlation identifier may be logged as a structured field.
22. Structured logging fields are asserted through captured `LogRecord` attributes.
23. `python-multipart==0.0.32` is the multipart dependency.
24. `httpx2==2.7.0` is the resolved test-client dependency.
25. The direct dependency files are pinned but are not a hash-locked record of all transitive dependencies.
26. Exact verified repository files will be inserted by Codex.
27. Narrative examples are not represented as exact repository source.
28. The full normalized text remains in the response for the learning exercise.

### Verification required

1. Confirm the exact filename-suffix case policy in the verified repository.
2. Confirm whether `text/plain; charset=utf-8` is deliberately rejected or parsed.
3. Confirm behavior when `UploadFile.content_type` is absent.
4. Confirm the exact Pydantic model names and field names after Codex source integration.
5. Confirm the exact exception-class hierarchy from the repository.
6. Confirm the exact stable response messages in addition to stable codes.
7. Confirm whether metadata validation failures use only FastAPI’s default response shape or an application-owned shape.
8. Confirm the line-count rule for a trailing newline.
9. Decide whether a leading UTF-8 byte-order mark is preserved, rejected, or handled specially.
10. Confirm that upload resources are closed according to the verified route and framework lifecycle.
11. Confirm that the application does not retain uploaded bytes after response completion.
12. Confirm that all structured log fields are compatible with the production formatter selected in a later phase.
13. Confirm whether `byte_count` is logged for rejected oversized documents.
14. Confirm whether unsupported-format failures are logged at `WARNING` or another level.
15. Re-run validation after any Codex integration or source change.
16. Record actual results separately for each new operating system or dependency change.
17. Review whether returning full extracted text remains appropriate before any production use.
18. Define response-size limits in a later phase.
19. Define authentication and authorization in a later phase.
20. Define persistence, retention, and deletion policy in a later phase.
21. Define production deployment, advanced streaming, and concurrency controls in later phases.
22. Perform a dedicated security review before exposing the service outside a controlled learning environment.

### Explicitly deferred beyond Week 1

* response-size limits;
* authentication;
* authorization;
* tenant isolation;
* persistence;
* data retention;
* cloud object storage;
* databases;
* queues;
* deployment;
* production server configuration;
* middleware architecture;
* rate limiting;
* caching;
* health checks;
* advanced HTTP streaming;
* concurrency tuning;
* parallel extraction;
* performance benchmarking;
* OCR;
* PDF parsing;
* table extraction;
* LLM calls;
* embeddings;
* RAG;
* agent frameworks.

## Review history

* **2026-07-21 — ChatGPT Web V1 generation:** Generated the initial comprehensive Week 1 module from the original approved outline. The initial narrative used an earlier document-boundary design and did not constitute executed repository validation.
* **2026-07-21 — Codex initial technical review:** Codex extracted and evaluated the repository implementation. The initial generated suite reported three failed tests, 24 passed tests, and one warning. The identified issues involved platform-dependent text-mode newline fixtures, an endpoint newline fixture, structured logging assertions, and the resolved test-client dependency.
* **2026-07-21 — Codex test corrections:** Codex changed exact-newline fixtures to byte-exact inputs, changed logging assertions to inspect captured `LogRecord` attributes, recorded `httpx2==2.7.0`, and applied Ruff formatting where needed.
* **2026-07-22 — Upload-boundary decision:** The project owner approved replacing the earlier boundary with a bounded multipart `UploadFile` contract using `media_type`, `correlation_id`, and `file`. The approved design introduced the mandatory 1 MiB limit, sentinel-byte read, strict UTF-8 decoder protocol, matching `text/plain` metadata, and removal of caller-selected server resource access.
* **2026-07-22 — Codex upload-boundary verification:** Codex recorded `26 passed in 0.33s`, Ruff lint success, Ruff format-check success for 14 files, and strict mypy success for 14 source files. These results apply to the verified repository files, not every isolated narrative snippet.
* **2026-07-22 — ChatGPT Web V2 generation:** Revised the learning module around the approved bounded multipart upload design, pinned `python-multipart==0.0.32` and `httpx2==2.7.0`, corrected the logging-test explanation, and separated narrative examples from verified source integration.
* **2026-07-22 — ChatGPT Web V2 continuation:** Completed the truncated testing matrix and supplied the remaining required sections: interview preparation, knowledge check, weekly deliverables, definition of done, sources, assumptions, and review history. ChatGPT did not execute the repository suite or reconstruct unattached verified source files.
* **Codex source integration:** Pending. Exact verified `document_service/` and `tests/` files must be inserted where required.
* **Technical content review:** Pending final confirmation after Codex integration.
* **Human review:** Pending.
* **Publication approval:** Pending.

<!-- CONTINUATION_END -->
