---
layout: week
permalink: /weeks/week-01/beginner/
description: A beginner-friendly introduction to the Python and FastAPI concepts used in the production Week 1 lesson.
title: Python service foundations—a simpler introduction
summary: Build the mental model first, then continue to the complete production-oriented lesson.
kicker_primary: Python foundations
kicker_secondary: Beginner context
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-01/
---
## What are we trying to build?

Imagine that a procurement team receives short supplier notes as text files. We want to create an API that accepts one `.txt` file and returns its text together with a few useful facts:

```json
{
  "correlation_id": "request-42",
  "media_type": "text/plain",
  "text": "Delivery confirmed.",
  "character_count": 19,
  "line_count": 1
}
```

An **API** is a contract that lets one program communicate with another. In this example, a client sends an HTTP request containing a file. Our FastAPI application checks it, reads it and returns JSON.

The feature sounds small, but it introduces most of the Python ideas needed for larger AI services. AI applications also receive untrusted inputs, call external components, transform data and return structured results. Learning to make this small service predictable gives us a foundation for those systems.

The service deliberately supports only:

- one uploaded file per request;
- UTF-8 text;
- the `.txt` suffix and `text/plain` media type;
- files no larger than 1 MiB.

PDF parsing, databases, authentication, LLM calls, deployment and high-volume concurrency are not part of this introduction. They require separate design decisions.

## Follow one request through the system

A successful request moves through a few clear stages:

```text
uploaded file
    ↓
FastAPI reads a bounded number of bytes
    ↓
Pydantic validates request metadata
    ↓
the service checks document rules
    ↓
a reader decodes UTF-8 bytes into text
    ↓
the result becomes JSON
```

Each stage has one main responsibility. This separation helps us answer important questions:

- Where should invalid input be rejected?
- Which code can be tested without starting a web server?
- Which failures should become HTTP status codes?
- How do we replace a real decoder with a controlled fake in a test?

The detailed lesson uses several modules, but the filenames are less important than the boundaries. HTTP code should not contain every business rule, and text-processing code should not need to know about FastAPI.

## Functions and classes solve different problems

A function is a good choice when an operation depends only on its inputs. Newline normalization is an example:

```python
def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")
```

The same input produces the same output. The function does not read a file, change global state or write a log. This makes it easy to understand and test.

A class becomes useful when behavior needs state or dependencies. Our extraction service needs a text reader:

```python
class DocumentExtractionService:
    def __init__(self, reader: TextReader) -> None:
        self._reader = reader
```

`self._reader` is **instance state**. Different service instances can receive different readers. The service uses composition: it **has a** reader rather than **being a** reader.

Class attributes belong to the class and are shared as policy. Mutable request-specific data should not be stored in a class-level list or dictionary because every instance could accidentally share it.

Methods have three common forms:

- An instance method receives `self` and works with an object's state.
- A class method receives `cls` and can use class-level policy or construct an alternative instance.
- A static method receives neither. If an operation is simply a stateless transformation, a module-level function is often clearer.

Inheritance is useful for a real “is a” relationship, such as a specific decoding error being a type of extraction error. It should not be used merely to reuse a few lines of code.

## Types describe intent; validation checks reality

This annotation tells readers and static-analysis tools what the function expects:

```python
def character_count(text: str) -> int:
    return len(text)
```

Python does not automatically reject every incorrect runtime value. Passing a list would still call `len()`. Type hints improve development-time feedback, but they do not make an HTTP request trustworthy.

Values such as filenames may arrive as `str | None`. Resolve that uncertainty at the boundary instead of letting optional values spread through the application. Avoid allowing `Any` to spread as well: it disables many useful type checks.

Pydantic performs runtime validation for untrusted values:

```python
class DocumentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    media_type: str = Field(min_length=1, max_length=128)
    correlation_id: str = Field(min_length=1, max_length=64)
```

A Pydantic model is a Python class that inherits from `BaseModel`. Its annotated attributes declare fields. `Field` adds constraints, while model configuration controls behavior for the whole model.

A field validator checks one field—for example, whether a correlation identifier contains only allowed characters. A model validator is useful when a rule depends on several fields together. Validation proves that input matches our schema; it does not prove that a supplier statement is true or that uploaded content is safe for every possible use.

## Dataclasses represent trusted internal values

After the boundary is validated, the service needs a compact object containing the values it will use:

```python
@dataclass(frozen=True, slots=True)
class ExtractionCommand:
    filename: str
    declared_media_type: str
    upload_media_type: str
    correlation_id: str
    content: bytes
```

A dataclass generates routine methods such as initialization and representation. `frozen=True` prevents normal field reassignment, making accidental changes less likely. `slots=True` declares a fixed set of instance attributes.

“Frozen” is shallow. If a frozen dataclass contains a list, the field cannot be replaced normally, but the list itself can still be mutated. Prefer immutable nested values when the object is intended to behave as a value.

The distinction is useful:

| Situation | Suitable tool |
| --- | --- |
| Untrusted request or response schema | Pydantic model |
| Trusted internal value | Frozen dataclass |
| Stateful orchestration with dependencies | Plain class |
| Stateless transformation | Function |

## Interfaces make dependencies replaceable

The extraction service needs anything capable of decoding bytes into text. A protocol describes that small requirement:

```python
class TextReader(Protocol):
    def decode(self, content: bytes) -> str: ...
```

The service depends on this capability, not on one concrete implementation. The real reader performs strict UTF-8 decoding. A test can supply a tiny fake reader with the same method.

This is dependency injection: an object receives a dependency from outside rather than constructing it secretly inside its business method. FastAPI also supports dependency injection at the HTTP boundary. The application assembly code chooses the real implementations; tests can override them.

Keep dependencies pointing inward. Domain values and protocols should not import FastAPI. The outer application knows about the framework and assembles the inner pieces. Circular imports often indicate that responsibilities or dependency direction need reconsideration.

## Fail clearly and log safely

Different failures deserve different categories:

- an oversized upload is a validation failure;
- an unsupported suffix or media type is a format failure;
- invalid UTF-8 is a decoding failure;
- a failed upload read is an infrastructure failure.

Low-level errors should be translated where the vocabulary changes:

```python
try:
    return reader.decode(content)
except ReaderDecodingError as exc:
    raise DocumentDecodingError("document is not valid UTF-8") from exc
```

`raise ... from exc` keeps the original cause for diagnosis while exposing a stable application-level failure. FastAPI exception handlers can later map that failure to an HTTP status and safe JSON response. Domain exceptions should not need to know about HTTP.

Avoid `except Exception: return ""`. It converts unexpected defects into apparently valid data and makes failures difficult to diagnose.

Logs should describe events, not duplicate uploaded documents. Safe fields include a controlled correlation identifier, media type, counts and a stable failure code. Do not log document bytes, decoded text, filenames, credentials or arbitrary exception messages.

```python
logger.info(
    "document_extraction_started",
    extra={"correlation_id": command.correlation_id},
)
```

Application startup configures handlers and formatting. Reusable modules obtain a module logger with `logging.getLogger(__name__)` and emit records without taking control of global logging.

## Generators and async are choices, not upgrades

A generator yields values one at a time:

```python
def non_empty_lines(text: str) -> Iterator[str]:
    for line in text.splitlines():
        if line.strip():
            yield line
```

Generators can reduce memory use and allow early stopping. They are normally consumed once, and errors may occur later while iterating. A suspended generator may also keep a file, cursor or network response open. For our bounded 1 MiB document, a normal list may be simpler and entirely adequate.

`async def` is useful when work can wait without blocking the event-loop thread. FastAPI's upload read is awaitable:

```python
content = await file.read(MAX_UPLOAD_BYTES + 1)
```

The extra byte tells us whether the upload is larger than the limit. Reading exactly 1 MiB cannot distinguish a complete 1 MiB file from the first 1 MiB of a larger file.

Putting blocking or CPU-heavy work inside `async def` does not make it non-blocking. Awaitable I/O often fits async tasks; blocking I/O may need a bounded thread pool; CPU-heavy Python may need processes or external workers. Sequential processing is often the correct first design for small bounded work.

Cancellation, timeouts, cleanup and capacity limits are part of concurrency design. “Use async” is not a complete performance plan.

## Test behavior at each boundary

Tests should prove observable behavior rather than private implementation details:

- Pure-function tests verify newline normalization and line counts.
- Reader tests use exact bytes and verify invalid UTF-8.
- Service tests inject a fake reader and exercise real orchestration.
- Pydantic tests verify accepted and rejected metadata.
- Endpoint tests send real multipart requests through `TestClient`.
- Logging tests prove that content and filenames are absent.

Arrange the inputs, act once, then assert the public result or failure. Parametrization is useful when the same rule has several input cases. Fixtures are useful for reusable setup with a clear lifecycle, but they should not hide the values that make a test meaningful.

Boundary cases matter. Test exactly 1,048,576 bytes and 1,048,577 bytes separately. Test empty, whitespace-only and invalid UTF-8 content. Test mismatched declared and uploaded media types. Use direct byte strings when newline or encoding behavior matters.

Tests provide evidence for the cases they execute. They do not prove deployment security, authentication, persistence safety or production capacity.

## You are ready for the production version

You should now be able to explain the main design in plain language:

1. FastAPI owns HTTP and the bounded upload read.
2. Pydantic validates untrusted request metadata.
3. Frozen dataclasses carry trusted internal values.
4. A service class coordinates rules and dependencies.
5. A protocol keeps the decoder replaceable.
6. Explicit exceptions describe failures without leaking implementation details.
7. Logs contain safe operational context, not document content.
8. Async is used at the awaitable boundary, while synchronous domain logic stays simple.
9. Tests prove behavior at each boundary.

Continue with the [production version]({{ '/weeks/week-01/' | relative_url }}). It uses the same ideas, but adds the complete implementation, deeper trade-offs, failure mappings, test strategy, exercises and senior-level interview questions.

Before switching, try answering these questions:

1. Why is a type hint not enough for an HTTP request?
2. When would you choose a dataclass instead of a Pydantic model?
3. Why should the service receive its reader from outside?
4. What information must never appear in the logs?
5. Why does the route read one byte beyond the upload limit?
6. Why can blocking work still block inside `async def`?

If the answers are roughly clear—even without remembering every class name—you have enough context for the detailed lesson.
