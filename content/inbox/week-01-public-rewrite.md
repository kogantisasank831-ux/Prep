---

layout: week
permalink: /weeks/week-01/
description: Build a typed, validated and testable document extraction API with Python and FastAPI.
title: Python for production AI systems
---------------------------------------

## The service we are building

A procurement team receives supplier notes, scope clarifications and exception reports as small text documents. Analysts currently copy the text into internal tools by hand. They need a small API that accepts one uploaded document and returns predictable JSON that downstream systems can trust.

The first question is: **what stable JSON should downstream procurement systems receive?**

<!-- VERIFIED_EXCERPT: models -->

```json
{
  "correlation_id": "procurement-2026-0042",
  "media_type": "text/plain",
  "text": "Supplier confirms delivery on 18 August.\nEscalate any delay.",
  "character_count": 62,
  "line_count": 2
}
```

The contract is deliberately narrow:

* the HTTP request is multipart form data with scalar fields `media_type` and `correlation_id`, plus a file field named `file`;
* the file is represented by FastAPI's `UploadFile`—the caller never supplies a server filesystem path;
* only filenames ending in `.txt` are supported;
* the declared media type and the upload content type must both be `text/plain` and must match;
* the application reads no more than 1 MiB plus one sentinel byte;
* an oversized upload returns HTTP `413` with code `document_too_large`;
* the bytes must decode as strict UTF-8;
* empty and whitespace-only documents are rejected;
* Windows and classic Mac newlines are normalized to `\n`, but other whitespace is preserved;
* successful output is validated and serialized as structured JSON.

The target environment is Python 3.13.12 installed and managed with `pip`. The runtime uses FastAPI 0.139.2, Pydantic 2.13.4, Uvicorn 0.51.0 and `python-multipart==0.0.32`. Endpoint tests use the resolved `httpx2==2.7.0` dependency with Starlette's `TestClient`.

A virtual environment keeps the lesson isolated from other projects. Create one with `python -m venv .venv`, activate it, then install the pinned runtime and development requirement files with `python -m pip install -r requirements.txt` and `python -m pip install -r requirements-dev.txt`. Python's `venv` behavior is documented at https://docs.python.org/3.13/library/venv.html, and `pip install` at https://pip.pypa.io/en/stable/cli/pip_install/.

### Start with the obvious implementation

The first version is tempting because everything is visible in one place. It receives the upload, reads it, validates it, decodes it, normalizes it, logs it and constructs the response.

The question this excerpt answers is: **what would a competent engineer write before the design pressures become visible?**

<!-- VERIFIED_EXCERPT: api -->

```python
MAX_UPLOAD_BYTES = 1_048_576


@router.post("/extract")
async def extract_document(
    media_type: Annotated[str, Form()],
    correlation_id: Annotated[str, Form()],
    file: Annotated[UploadFile, File()],
) -> dict[str, object]:
    content = await file.read(MAX_UPLOAD_BYTES + 1)

    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail={"code": "document_too_large"},
        )

    if not (file.filename or "").lower().endswith(".txt"):
        raise HTTPException(status_code=415, detail="unsupported format")

    if media_type != "text/plain" or file.content_type != media_type:
        raise HTTPException(status_code=415, detail="unsupported format")

    text = content.decode("utf-8", errors="strict")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")

    if normalized.strip() == "":
        raise HTTPException(status_code=422, detail="empty document")

    logger.info(
        "document_extraction_completed",
        extra={"correlation_id": correlation_id},
    )

    return {
        "correlation_id": correlation_id,
        "media_type": "text/plain",
        "text": normalized,
        "character_count": len(normalized),
        "line_count": len(normalized.splitlines()),
    }
```

This route already contains several good decisions: it uses `UploadFile`, performs a bounded read, checks multiple format signals and avoids logging the document. The problem is not that the code is careless. The problem is that one function now owns too many reasons to change:

* a new media type changes it;
* a new metadata rule changes it;
* a decoding strategy changes it;
* a response-field change changes it;
* a logging-policy change changes it;
* a new error contract changes it;
* almost every test must enter through HTTP to exercise the rules.

The route is also returning `dict[str, object]`, which says little about the exact response contract. `HTTPException` calls scatter transport concerns through business decisions. A decoding failure surfaces as a raw `UnicodeDecodeError` unless we remember to translate it. The function is readable today, but it is becoming the place where every future concern accumulates.

> **Design checkpoint:** A small function is not automatically a focused function. Count responsibilities and reasons to change, not lines of code.

Our starting architecture is therefore simple but overloaded:

> **Architecture, step 0**
> `multipart request → one FastAPI route → JSON response`
> Inside the route: upload reading + metadata validation + format policy + UTF-8 decoding + normalization + logging + response construction

The first improvement is not “add classes.” It is to separate stateless transformations and module responsibilities. That gives us a cleaner basis for deciding which parts actually need objects.

## From one route to deliberate design

The procurement API performs two kinds of work:

1. **Boundary work** depends on FastAPI and the HTTP request: reading `UploadFile`, interpreting multipart fields and returning status codes.
2. **Domain work** is independent of HTTP: newline normalization, line counting, format policy and construction of extraction results.

The distinction matters because deterministic domain behavior should be testable without starting an HTTP client. It also prevents FastAPI types from spreading through the application.

### Extract the transformations that have no state

The question this excerpt answers is: **which behavior can become a pure function?** A pure function's result depends only on its inputs and it does not perform observable side effects such as I/O or logging.

<!-- VERIFIED_EXCERPT: domain -->

```python
def normalize_newlines(text: str) -> str:
    """Normalize newline representation without trimming other whitespace."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def count_logical_lines(text: str) -> int:
    """Count logical lines for a non-empty document."""
    lines = text.splitlines()
    return len(lines) if lines else 1
```

These functions establish two explicit policies.

First, newline normalization changes representation, not meaning. It converts `\r\n` and `\r` to `\n`, but it does not call `strip()`, collapse spaces, lowercase text or perform Unicode normalization. Empty-content detection can inspect `normalized_text.strip()` without replacing the text returned to the caller.

Second, line counting is named and testable. The rule for a trailing newline is no longer buried in response construction. If that policy changes later, one function and its tests change.

> **Common trap:** “Cleaning text” often becomes an unnamed collection of irreversible transformations. Name each transformation and preserve the original meaning unless the product contract explicitly allows a change.

### Let modules communicate responsibility

A practical module split for this service is:

| Module            | Responsibility                                                 |
| ----------------- | -------------------------------------------------------------- |
| `api.py`          | Multipart and HTTP concerns, including the bounded upload read |
| `models.py`       | Pydantic boundary and response models                          |
| `domain.py`       | Frozen domain values and pure transformations                  |
| `ports.py`        | Narrow interfaces required by the service                      |
| `readers.py`      | Strict UTF-8 decoder implementation                            |
| `errors.py`       | Stable failure categories                                      |
| `service.py`      | Format policy and extraction orchestration                     |
| `dependencies.py` | Concrete object construction                                   |
| `main.py`         | Application assembly and HTTP error mappings                   |

This is not a rule that every service needs nine files. Each boundary exists here because it has a distinct reason to change and a distinct testing strategy. A smaller application can combine modules while preserving the same dependency direction.

The architecture has now started to separate:

> **Architecture, step 1**
> `multipart request → FastAPI boundary → extraction logic → JSON response`
> `domain.py`: deterministic text functions
> The route still owns validation, decoding, logging and orchestration

We have removed stateless transformations from the route, but we still need somewhere to hold dependencies and shared policy. This is where classes become useful—provided they earn their place.

> **Try it:** Write three tests for `normalize_newlines`: one for `\r\n`, one for `\r`, and one proving that leading and trailing spaces are preserved.

## Classes should earn their place

Production Python code often contains too many classes because “enterprise design” is mistaken for “object-oriented design.” The opposite mistake is to avoid classes entirely and pass dependencies through long function chains. The useful question is not “functions or classes?” It is **what responsibility requires state, dependency ownership or lifecycle?**

### Instance state, class policy and construction

The extraction service needs a decoder. That dependency should be selected during application assembly and reused by the service. The service also has format policy shared by all instances.

The question this excerpt answers is: **what state belongs to each service instance, and what policy belongs to the class?**

<!-- VERIFIED_EXCERPT: service -->

```python
class DocumentExtractionService:
    supported_media_type: ClassVar[str] = "text/plain"
    supported_suffix: ClassVar[str] = ".txt"

    def __init__(self, reader: TextReader) -> None:
        self._reader = reader
```

`self._reader` is **instance state**: each service object owns a decoder dependency. `supported_media_type` and `supported_suffix` are **class attributes**: they describe policy shared by the class rather than request-specific state.

`__init__` initializes a newly created instance. It is commonly called the constructor in day-to-day Python discussion, although object creation begins in `__new__` and initialization occurs in `__init__`. For this service, `__init__` establishes the dependency the instance requires to do useful work.

The question this excerpt answers is: **what goes wrong when request-specific mutable state is placed on the class?**

<!-- VERIFIED_EXCERPT: service -->

```python
class BadTracker:
    completed_ids: list[str] = []

    def record(self, correlation_id: str) -> None:
        self.completed_ids.append(correlation_id)
```

Every instance can mutate the same list. If mutable state is truly per instance, create it in `__init__`. Better still, avoid storing request history in this stateless service unless the product requires it.

### Instance, class and static methods

An **instance method** receives `self` and should use instance state or behavior. `extract()` is an instance method because it uses the injected decoder.

A **class method** receives `cls`. It is useful for alternate constructors or behavior that deliberately depends on overridable class-level policy. The question this excerpt answers is: **when should validation read policy from the class rather than one instance?**

<!-- VERIFIED_EXCERPT: service -->

```python
@classmethod
def _validate_command(cls, command: ExtractionCommand) -> None:
    if command.declared_media_type != cls.supported_media_type:
        raise UnsupportedDocumentFormatError(
            "only text/plain documents are supported",
            correlation_id=command.correlation_id,
        )
```

A **static method** receives neither `self` nor `cls`. It can be appropriate when a stateless operation is conceptually inseparable from a class's public API. In many cases, a module-level function communicates the design more clearly. Newline normalization does not become more maintainable merely because it is placed inside `DocumentExtractionService`.

### Composition before inheritance

The service **has a decoder**; it is not a decoder. This is composition: one object performs its responsibility using another object.

Inheritance is justified when the relationship is genuinely “is a.” Pydantic request models are `BaseModel` subclasses. Specialized application failures are subclasses of broader application exceptions. By contrast, making `DocumentExtractionService` inherit from `Utf8TextReader` would mix orchestration with decoding and make substitution harder.

| Need                                         | Better tool                   |
| -------------------------------------------- | ----------------------------- |
| Stateless transformation                     | Module function               |
| Internal value with generated initialization | Dataclass                     |
| Boundary validation and serialization        | Pydantic `BaseModel` subclass |
| Dependency-owning orchestration              | Plain class                   |
| Replaceable capability                       | Protocol plus composition     |
| Shared failure category                      | Exception inheritance         |

> **Design checkpoint:** A class earns its place through state, dependency ownership, lifecycle or polymorphic responsibility—not because the code “looks more structured” inside a class body.

Our architecture is now:

> **Architecture, step 2**
> `multipart request → FastAPI boundary → DocumentExtractionService → JSON response`
> `DocumentExtractionService` owns a decoder dependency
> Pure functions still own normalization and counting

The service shape is clearer, but annotations such as `reader: TextReader` and `content: bytes` still describe intent only. They do not validate untrusted multipart values. We need a deliberate trust boundary.

## Types inside, validation at the boundary

Type hints and runtime validation solve related but different problems.

A type hint helps developers, editors and static analyzers understand an internal contract. It does not generally stop an arbitrary caller from passing a different runtime value. PEP 484 explicitly defines type hints primarily for static analysis: https://peps.python.org/pep-0484/.

### A type hint can be correct and still accept the wrong value

The question this excerpt answers is: **why does an annotation not make a boundary safe?**

<!-- VERIFIED_EXCERPT: models -->

```python
def character_count(text: str) -> int:
    return len(text)


character_count(["supplier", "note"])
```

The call violates the annotated contract, but `len()` accepts a list, so Python can return `2`. A type checker can flag the call before execution; the runtime does not automatically enforce the annotation.

This distinction is especially important in Applied AI systems. LLM output, document metadata, tool arguments, queue messages and HTTP requests all cross trust boundaries. A schema can be well typed in our source code while the live input remains malformed.

### Validate scalar multipart metadata with Pydantic

The procurement endpoint has two scalar form fields: `media_type` and `correlation_id`. These are good Pydantic inputs because they are ordinary values that need runtime constraints and clear error reporting.

The question this excerpt answers is: **what should the boundary model validate?**

<!-- VERIFIED_EXCERPT: models -->

```python
_SAFE_CORRELATION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class DocumentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    media_type: str = Field(min_length=1, max_length=128)
    correlation_id: str = Field(min_length=1, max_length=64)

    @field_validator("media_type")
    @classmethod
    def validate_media_type_text(cls, value: str) -> str:
        if value != value.strip():
            raise ValueError(
                "media_type must not contain surrounding whitespace"
            )
        return value

    @field_validator("correlation_id")
    @classmethod
    def validate_correlation_id(cls, value: str) -> str:
        if _SAFE_CORRELATION_ID.fullmatch(value) is None:
            raise ValueError(
                "correlation_id contains unsupported characters"
            )
        return value
```

A Pydantic model is a Python class derived from `BaseModel`. Annotated class attributes declare fields. `Field` adds constraints and schema metadata. `model_config` applies model-wide behavior:

* `extra="forbid"` rejects undeclared fields when constructing the model from a mapping;
* `strict=True` reduces coercion, though exact strict behavior remains type- and input-mode-dependent;
* `frozen=True` blocks normal reassignment after construction.

Pydantic v2 field validators operate on one or more named fields. A model validator operates on the model as a whole and is useful for cross-field invariants. We deliberately do **not** place the upload filename or upload content type in `DocumentRequest`: they come from `UploadFile`, not from scalar form fields. The service later checks their relationship with the validated declared media type.

That placement matters. Duplicating `filename` and `upload_content_type` as user-supplied Pydantic fields would create two competing sources of truth: the multipart file metadata and separate scalar values.

Pydantic models also provide serialization and construction APIs such as `model_dump()`, `model_dump_json()`, `model_validate()` and `model_validate_json()`. The question this excerpt answers is: **how should a trusted domain result become a validated response model?**

<!-- VERIFIED_EXCERPT: models -->

```python
class ExtractionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    correlation_id: str
    media_type: str
    text: str
    character_count: int = Field(ge=0)
    line_count: int = Field(ge=1)

    @classmethod
    def from_domain(cls, result: ExtractedDocument) -> Self:
        return cls(
            correlation_id=result.correlation_id,
            media_type=result.media_type,
            text=result.text,
            character_count=result.character_count,
            line_count=result.line_count,
        )
```

The custom class method is appropriate because it constructs the current response class from a domain value. Reading the upload or decoding bytes inside `from_domain()` would not be appropriate; those are different responsibilities.

> **Common trap:** Pydantic validation establishes that data satisfies a declared schema. It does not establish that a media type is truthful, a supplier statement is factually correct or a document is safe to persist.

Our architecture now has a real trust boundary:

> **Architecture, step 3**
> `multipart form scalars → Pydantic DocumentRequest`
> `UploadFile metadata → HTTP boundary`
> `validated metadata + bounded bytes → service`
> Type hints describe internal contracts; runtime checks validate live input

The boundary model gives us validated scalars, but we do not want Pydantic objects to become the universal data structure for the whole application. The next step is to model already-trusted internal state explicitly.

## Model trusted state explicitly

After boundary validation, the service needs one object containing the document metadata and bounded bytes, and one object representing the successful result. These objects are internal values, not parsers. A frozen dataclass is a better fit than another Pydantic model.

### Use frozen dataclasses for already-validated values

The question this excerpt answers is: **what should cross from the HTTP boundary into the synchronous service?**

<!-- VERIFIED_EXCERPT: domain -->

```python
@dataclass(frozen=True, slots=True)
class ExtractionCommand:
    filename: str
    declared_media_type: str
    upload_media_type: str
    correlation_id: str
    content: bytes


@dataclass(frozen=True, slots=True)
class ExtractedDocument:
    correlation_id: str
    media_type: str
    text: str
    character_count: int
    line_count: int
```

`ExtractionCommand` combines values from two sources:

* validated scalar metadata from `DocumentRequest`;
* filename, upload content type and bounded bytes from `UploadFile`.

The service receives one coherent command rather than a long list of loosely related arguments. `ExtractedDocument` represents the successful domain result before it becomes an HTTP response model.

`frozen=True` prevents normal attribute reassignment, which reduces accidental mutation while a value moves through the pipeline. `slots=True` removes the per-instance `__dict__` and makes the declared fields explicit.

The question this excerpt answers is: **what does frozen fail to protect when a field refers to a mutable object?**

<!-- VERIFIED_EXCERPT: domain -->

```python
@dataclass(frozen=True)
class ReviewBatch:
    document_ids: list[str]


batch = ReviewBatch(document_ids=["A-101"])
batch.document_ids.append("A-102")  # Nested list still mutates.
```

This is **shallow immutability**. For value-like state shared across AI pipeline stages, prefer immutable nested structures such as tuples or make ownership and copying explicit. Aliasing—the condition where multiple names reference the same mutable object—can otherwise create order-dependent prompts, corrupted evaluation inputs and cache inconsistencies.

### Isolate decoding behind a narrow protocol

We now have bounded `bytes`, but decoding is still an external capability from the service's perspective. Today the rule is strict UTF-8. Tomorrow a different text adapter might be introduced. The service should depend on the capability it needs, not on a concrete decoder class.

The question this excerpt answers is: **what is the smallest useful interface?**

<!-- VERIFIED_EXCERPT: ports -->

```python
class TextReader(Protocol):
    """Narrow interface required by the extraction service."""

    def decode(self, content: bytes) -> str: ...
```

A `Protocol` supports structural typing: an object satisfies the interface when it provides a compatible `decode()` method. It does not have to inherit from `TextReader`. This keeps tests simple because a small fake decoder can be injected directly.

The question this excerpt answers is: **where should strict UTF-8 policy and codec-error translation live?**

<!-- VERIFIED_EXCERPT: readers -->

```python
class Utf8TextReader:
    encoding: ClassVar[str] = "utf-8"

    def decode(self, content: bytes) -> str:
        try:
            return content.decode(self.encoding, errors="strict")
        except UnicodeDecodeError as exc:
            raise ReaderDecodingError(
                "document resource is not valid UTF-8"
            ) from exc
```

The class is justified because it implements a replaceable boundary and carries class-level encoding policy. The service composes with it through `TextReader`.

Why not call `content.decode()` directly in the service? Because the adapter gives us one place to:

* define strict decoding policy;
* translate codec-specific exceptions;
* substitute a fake in service tests;
* add a second decoder later without coupling orchestration to implementation details.

Why not build a generic decoder registry? Because one interface and one implementation solve the current problem. A plugin framework would introduce discovery, registration and lifecycle behavior without a demonstrated requirement.

The architecture now has clear value and capability boundaries:

> **Architecture, step 4**
> `UploadFile → bounded bytes`
> `Pydantic metadata + UploadFile metadata + bytes → frozen ExtractionCommand`
> `DocumentExtractionService --uses→ TextReader protocol`
> `Utf8TextReader → strict UTF-8`
> `service → frozen ExtractedDocument → Pydantic response`

We have separated data, behavior and dependencies. The next weakness is failure handling. Raw framework, codec and application errors still need stable categories so callers and operators can reason about what went wrong.

> **Try it:** Create a fake decoder whose `decode()` method returns a fixed string regardless of input. Use it to test the service without exercising the UTF-8 adapter.

## Make failures part of the design

A production API is defined as much by its failures as by its successful response. “Something failed” is not enough. An oversized upload, unsupported format, invalid UTF-8 document and infrastructure problem require different client behavior and different operational response.

### Define failure categories before mapping status codes

The question this excerpt answers is: **which failures should callers be able to distinguish?**

<!-- VERIFIED_EXCERPT: errors -->

```python
class DocumentServiceError(Exception):
    code: ClassVar[str] = "document_service_error"

    def __init__(self, message: str, *, correlation_id: str) -> None:
        super().__init__(message)
        self.message = message
        self.correlation_id = correlation_id


class DocumentValidationError(DocumentServiceError):
    code = "document_validation_failed"


class DocumentTooLargeError(DocumentValidationError):
    code = "document_too_large"


class UnsupportedDocumentFormatError(DocumentServiceError):
    code = "unsupported_document_format"


class DocumentExtractionError(DocumentServiceError):
    code = "document_extraction_failed"


class DocumentDecodingError(DocumentExtractionError):
    code = "document_decoding_failed"


class EmptyDocumentError(DocumentExtractionError):
    code = "empty_document"


class DocumentInfrastructureError(DocumentServiceError):
    code = "document_infrastructure_failure"
```

Inheritance is useful here because HTTP handlers can catch a broad category while clients still receive a specific stable code. `DocumentDecodingError` is an extraction failure; `DocumentTooLargeError` is a validation failure; both remain `DocumentServiceError` instances.

The exception stores a safe `correlation_id`, not the filename or document text. Public clients can connect the error to their request without receiving sensitive payload data.

### Translate where the vocabulary changes

`Utf8TextReader` understands Python's `UnicodeDecodeError`. The service understands “the document could not be decoded.” The HTTP layer understands status codes and error bodies.

The question this excerpt answers is: **where should the low-level decoding error become an application error?**

<!-- VERIFIED_EXCERPT: service -->

```python
def _decode(self, command: ExtractionCommand) -> str:
    try:
        return self._reader.decode(command.content)
    except ReaderDecodingError as exc:
        raise DocumentDecodingError(
            "document is not valid UTF-8",
            correlation_id=command.correlation_id,
        ) from exc
```

`raise ... from exc` creates an explicit causal chain. The service exposes a stable category while preserving the original decoder failure for internal diagnosis.

Translate an exception only when the current layer adds useful meaning. Wrapping every exception at every call site creates noise and hides the original structure. Conversely, returning raw `UnicodeDecodeError` from an HTTP endpoint leaks implementation details and forces the client to understand Python codecs.

### Keep transport mapping at the transport boundary

Application exceptions should not carry HTTP status codes. The same service could later be invoked from a queue consumer or command-line tool. FastAPI exception handlers map domain categories to HTTP behavior:

| Failure                          | HTTP status | Stable code                       |
| -------------------------------- | ----------: | --------------------------------- |
| Upload above 1 MiB               |         413 | `document_too_large`              |
| Unsupported suffix or media type |         415 | `unsupported_document_format`     |
| Invalid UTF-8                    |         422 | `document_decoding_failed`        |
| Empty or whitespace-only text    |         422 | `empty_document`                  |
| Infrastructure read failure      |         503 | `document_infrastructure_failure` |

The size decision occurs immediately after the bounded upload read because only the HTTP boundary owns `UploadFile`. Format, decoding and empty-content rules belong to the synchronous service.

### Avoid broad suppression

The question this excerpt answers is: **why is broad exception suppression unsafe for document extraction?**

<!-- VERIFIED_EXCERPT: service -->

```python
try:
    return self._reader.decode(command.content)
except Exception:
    return ""
```

It converts programming defects, cancellation-related problems and infrastructure failures into valid-looking empty text. The service might then raise the wrong error or return incorrect data. Catch only failures that the current layer can handle or translate deliberately.

> **Common trap:** Logging an exception and then continuing is still suppression. If the operation cannot produce a trustworthy result, re-raise or translate the failure.

The failure path is now explicit:

> **Architecture, step 5**
> low-level codec failure `→ ReaderDecodingError`
> service vocabulary `→ DocumentDecodingError`
> HTTP mapping `→ 422 + stable JSON code`
> causal chain retained internally

Stable exceptions tell clients what happened. Operators still need to understand when it happened and which request was affected—without copying sensitive procurement documents into logs.

## Observe behavior without leaking data

Logs are another data boundary. A document-extraction API can accidentally create a second, less protected copy of every supplier note by logging request objects, filenames, decoded text or raw exception messages.

The operational goal is narrower: explain the lifecycle and failure category while excluding payload data.

### Use module-level loggers and structured context

The question this excerpt answers is: **what should the service emit during a normal extraction?**

<!-- VERIFIED_EXCERPT: service -->

```python
logger = logging.getLogger(__name__)


logger.info(
    "document_extraction_started",
    extra={
        "correlation_id": command.correlation_id,
        "media_type": command.declared_media_type,
    },
)
```

`logging.getLogger(__name__)` gives each module a hierarchical logger. Library modules emit records; application startup or the process runner decides handlers, formatting, destinations and log levels. Calling `logging.basicConfig()` inside service modules would take control away from the application.

Useful structured fields include:

* safe correlation identifier;
* declared and upload media types;
* byte, character and line counts;
* stable failure code;
* duration when measured deliberately.

Do not emit:

* raw uploaded bytes;
* decoded document text;
* filename;
* full multipart objects;
* credentials or personal information;
* arbitrary validation inputs;
* unreviewed low-level exception messages.

The question this excerpt answers is: **what should a failure log preserve when the payload must remain private?**

<!-- VERIFIED_EXCERPT: service -->

```python
except DocumentServiceError as exc:
    logger.warning(
        "document_extraction_failed",
        extra={
            "correlation_id": command.correlation_id,
            "failure_code": exc.code,
        },
    )
    raise
```

Expected client-specific failures such as unsupported formats can be warnings rather than errors because the application handled them according to contract. Unexpected infrastructure defects may justify `logger.exception()` when a traceback is operationally useful, but the exception and formatter still need review for leakage.

### `caplog.text` and `caplog.records` answer different questions

Fields supplied through `extra` become attributes on the emitted `LogRecord`. They are not guaranteed to appear in formatted log text. The active formatter decides what `caplog.text` contains.

The question this excerpt answers is: **how do we test both secrecy and structured context?**

<!-- VERIFIED_EXCERPT: tests -->

```python
assert secret_text not in caplog.text
assert filename not in caplog.text

assert all(
    getattr(record, "correlation_id", None)
    == "safe-correlation-123"
    for record in caplog.records
)
```

Use `caplog.text` to assert that forbidden rendered values are absent. Use `caplog.records` to inspect structured attributes such as `correlation_id` and `failure_code`.

> **Design checkpoint:** Observability is not “log more.” It is “record enough safe context to explain behavior.”

The architecture now has an operational side channel with an explicit data policy:

> **Architecture, step 6**
> request lifecycle `→ structured LogRecord`
> safe identifiers and counts allowed
> document content and filename prohibited
> tests verify both rendered text and record attributes

The service is reliable for one bounded document. The procurement team now asks whether line-by-line processing or multiple simultaneous uploads would be “more scalable.” That question introduces laziness, concurrency and resource lifetime—concepts that are easy to misuse when taught as isolated syntax.

## Laziness, concurrency and resource lifetime

Suppose a later procurement rule checks each logical line for a supplier code. For a 1 MiB bounded document, converting all lines to a list is usually simple and acceptable. A generator becomes interesting only when lazy production creates a concrete benefit.

### Generators trade repeatability for laziness

An **iterable** can produce an iterator. An **iterator** yields one item at a time and tracks traversal state. A **generator** is a convenient iterator created by a function containing `yield`.

The question this excerpt answers is: **how could we inspect lines without materializing a second list?**

<!-- VERIFIED_EXCERPT: domain -->

```python
from collections.abc import Iterator
from io import StringIO


def iter_logical_lines(text: str) -> Iterator[str]:
    with StringIO(text) as stream:
        for line in stream:
            yield line.rstrip("\n")
```

The generator is lazy: its body starts when iteration requests a value, not when the generator object is created. It can reduce peak memory and allow early termination when a rule finds what it needs.

The trade-offs are equally important:

* the generator is normally consumed once;
* a second iteration produces no values;
* exceptions may occur later during iteration rather than at construction;
* a partially consumed generator complicates retries;
* a generator can retain a file, network response, cursor or in-memory stream while suspended.

The question this excerpt answers is: **what does single consumption look like in observable behavior?**

<!-- VERIFIED_EXCERPT: domain -->

```python
lines = iter_logical_lines("PO-1\nPO-2")

first_pass = list(lines)
second_pass = list(lines)

assert first_pass == ["PO-1", "PO-2"]
assert second_pass == []
```

For this endpoint, the upload is capped at 1 MiB and the response returns complete normalized text. The implementation does not expose an upload-backed generator or advanced HTTP streaming. A list may be the clearer design when repeatability and simple failure timing matter more than avoiding a bounded allocation.

> **Try it:** Compare a list and generator design for “stop after the first line containing `URGENT`.” Write down when the input is consumed, when errors surface and whether the operation can be retried.

### Async appears because the boundary API is awaitable

FastAPI's `UploadFile.read()` is awaitable, so the route is `async def` and uses `await`. That is a property of the HTTP boundary—not a command to make the whole application asynchronous.

The question this excerpt answers is: **where does asynchronous execution actually enter the design?**

<!-- VERIFIED_EXCERPT: api -->

```python
MAX_UPLOAD_BYTES = 1_048_576

content = await file.read(MAX_UPLOAD_BYTES + 1)
```

While an awaitable operation is waiting, the event loop may run other tasks. After the bounded bytes are available, strict decoding, validation, normalization and result construction remain ordinary synchronous work.

The question this excerpt answers is: **why can an async function still block the event loop?**

<!-- VERIFIED_EXCERPT: api -->

```python
async def misleading() -> str:
    return blocking_library_call()
```

If `blocking_library_call()` occupies the event-loop thread, other tasks cannot progress during that call.

### Choose concurrency according to the workload

| Workload                        | Typical first choice                  | Main concern                                     |
| ------------------------------- | ------------------------------------- | ------------------------------------------------ |
| Awaitable network or upload I/O | Async tasks                           | Cancellation, timeouts and backpressure          |
| Blocking I/O library            | Bounded thread pool                   | Worker capacity and difficult cancellation       |
| CPU-heavy pure Python           | Process or external worker evaluation | Serialization and process lifecycle              |
| Small bounded operation         | Sequential execution                  | Simplicity may be more valuable than parallelism |

Threads can bridge synchronous libraries, but a running thread usually cannot be forcibly cancelled safely. Worker and queue capacity must be bounded to prevent memory growth and downstream overload.

CPU-heavy work does not become faster because it is called from `async def`. Processes, native code that releases the GIL, accelerators or an external worker may be appropriate, but each adds operational complexity.

Cancellation is part of the contract. A coroutine may be cancelled while awaiting an upload or remote call, so resource cleanup belongs in `finally` blocks or context managers. Timeouts do not automatically prove the underlying operation stopped; retry safety and side effects still need analysis.

> **Common trap:** “Async” is not a performance tier. It is a concurrency model that works when the operations in the call path can genuinely suspend.

Our architecture is nearly complete:

> **Architecture, step 7**
> `async FastAPI route --awaits→ bounded UploadFile.read()`
> `route → frozen command → synchronous service`
> `service → synchronous decoder + pure functions`
> Async remains at the awaitable boundary; domain logic remains synchronous

We can now assemble the boundary without placing all the decisions back into one route.

## Assemble the FastAPI boundary

A thin route is not a route with no logic. It is a route whose logic is limited to HTTP concerns. For this service, the route must receive multipart data, await a bounded upload read, translate a read failure into an infrastructure category, reject oversized content, create the internal command and call the synchronous service.

### Parse scalar form fields through a Pydantic dependency

FastAPI receives form fields individually. A dependency function can construct `DocumentRequest`, allowing Pydantic to validate the scalar metadata before the route begins extraction.

The question this excerpt answers is: **how do scalar multipart values enter the Pydantic boundary model?**

<!-- VERIFIED_EXCERPT: api -->

```python
def parse_document_request(
    media_type: Annotated[str, Form()],
    correlation_id: Annotated[str, Form()],
) -> DocumentRequest:
    try:
        return DocumentRequest(
            media_type=media_type,
            correlation_id=correlation_id,
        )
    except ValidationError as exc:
        raise RequestValidationError(exc.errors()) from exc
```

Only `media_type` and `correlation_id` are Pydantic request fields. `file.filename` and `file.content_type` remain properties of `UploadFile`. This preserves one source of truth for each value.

### Enforce the bound before domain processing

The question this excerpt answers is: **how does the endpoint distinguish exactly-at-limit content from a larger upload?**

<!-- VERIFIED_EXCERPT: api -->

```python
MAX_UPLOAD_BYTES = 1_048_576


async def extract_document(
    request: Annotated[DocumentRequest, Depends(parse_document_request)],
    file: Annotated[UploadFile, File()],
    service: Annotated[
        DocumentExtractionService,
        Depends(get_extraction_service),
    ],
) -> ExtractionResponse:
    try:
        content = await file.read(MAX_UPLOAD_BYTES + 1)
    except OSError as exc:
        raise DocumentInfrastructureError(
            "uploaded document could not be read",
            correlation_id=request.correlation_id,
        ) from exc

    if len(content) > MAX_UPLOAD_BYTES:
        raise DocumentTooLargeError(
            "document exceeds the 1 MiB upload limit",
            correlation_id=request.correlation_id,
        )
```

Reading only `MAX_UPLOAD_BYTES` would be ambiguous: the returned bytes could be the complete upload or merely the first 1 MiB of a larger upload. Reading one additional sentinel byte resolves that ambiguity while preserving a bounded-memory contract.

An upload of exactly 1,048,576 bytes passes the size check and proceeds to format and content validation. An upload that returns 1,048,577 bytes is rejected with `DocumentTooLargeError`, which the HTTP layer maps to status `413` and code `document_too_large`.

This application-level read bound limits how much the route requests from `UploadFile`; it is not a complete deployment-level request-body defense. Reverse-proxy limits, server settings, multipart parser behavior and streaming controls belong to later production design.

### Build the command from the correct sources

The question this excerpt answers is: **where do the command fields come from?**

<!-- VERIFIED_EXCERPT: api -->

```python
command = ExtractionCommand(
    filename=file.filename or "",
    declared_media_type=request.media_type,
    upload_media_type=file.content_type or "application/octet-stream",
    correlation_id=request.correlation_id,
    content=content,
)
result = service.extract(command)
return ExtractionResponse.from_domain(result)
```

The source mapping is deliberate:

| Command field         | Source                                     |
| --------------------- | ------------------------------------------ |
| `filename`            | `UploadFile.filename`                      |
| `declared_media_type` | Validated `DocumentRequest.media_type`     |
| `upload_media_type`   | `UploadFile.content_type`                  |
| `correlation_id`      | Validated `DocumentRequest.correlation_id` |
| `content`             | Bounded result of `await file.read()`      |

If the upload content type is absent, the route substitutes `application/octet-stream`, causing the service's strict media-type agreement rule to reject it. The route does not invent `text/plain` on the caller's behalf.

### Let the service enforce document policy

The service validates the relationship among filename, declared media type and upload media type before decoding.

The question this excerpt answers is: **which rules remain synchronous domain policy?**

<!-- VERIFIED_EXCERPT: service -->

```python
@classmethod
def _validate_command(cls, command: ExtractionCommand) -> None:
    if command.declared_media_type != cls.supported_media_type:
        raise UnsupportedDocumentFormatError(
            "only text/plain documents are supported",
            correlation_id=command.correlation_id,
        )

    if command.upload_media_type != command.declared_media_type:
        raise UnsupportedDocumentFormatError(
            "declared media type does not match the upload media type",
            correlation_id=command.correlation_id,
        )

    if not command.filename.lower().endswith(cls.supported_suffix):
        raise UnsupportedDocumentFormatError(
            "only .txt documents are supported",
            correlation_id=command.correlation_id,
        )
```

The suffix check is case-insensitive because the implementation calls `.lower()`. The media-type checks are exact: `text/plain; charset=utf-8` does not equal `text/plain` under this contract.

These signals are still metadata, not proof. A file named `supplier.txt` with both media types set to `text/plain` can contain invalid bytes. Strict UTF-8 decoding provides the next check.

The question this excerpt answers is: **how can we reject whitespace-only content without trimming valid returned text?**

<!-- VERIFIED_EXCERPT: service -->

```python
raw_text = self._decode(command)
normalized_text = normalize_newlines(raw_text)

if normalized_text.strip() == "":
    raise EmptyDocumentError(
        "document contains no non-whitespace text",
        correlation_id=command.correlation_id,
    )
```

Calling `strip()` only in the predicate is important. The returned text remains `normalized_text`, so meaningful leading and trailing whitespace is not silently removed.

### Map application failures to stable HTTP responses

The HTTP layer owns status codes. The question this excerpt answers is: **where should `DocumentTooLargeError` become HTTP 413?**

<!-- VERIFIED_EXCERPT: api -->

```python
@app.exception_handler(DocumentTooLargeError)
async def handle_document_too_large(
    _request: Request,
    exc: DocumentTooLargeError,
) -> JSONResponse:
    return _error_response(
        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
        code=exc.code,
        message=exc.message,
        correlation_id=exc.correlation_id,
    )
```

The same pattern maps unsupported format to `415`, extraction failures to `422` and infrastructure failures to `503`. Clients depend on stable codes, not raw Python exception text.

### The final architecture

> **Architecture, final**
> `multipart request`
> `├─ media_type → Form → Pydantic DocumentRequest`
> `├─ correlation_id → Form → Pydantic DocumentRequest`
> `└─ file → UploadFile → await read(1 MiB + 1)`
> `       ├─ oversized → DocumentTooLargeError → HTTP 413`
> `       └─ bounded bytes + UploadFile metadata`
> `                         ↓`
> `               frozen ExtractionCommand`
> `                         ↓`
> `             DocumentExtractionService`
> `               ├─ format policy`
> `               ├─ TextReader protocol → strict UTF-8 adapter`
> `               ├─ pure normalization and counting`
> `               ├─ explicit exceptions`
> `               └─ safe structured logs`
> `                         ↓`
> `               frozen ExtractedDocument`
> `                         ↓`
> `               Pydantic response JSON`

The runtime needs `python-multipart==0.0.32` to parse form and file fields. The resolved endpoint-test environment uses `httpx2==2.7.0` with Starlette's `TestClient`; do not add a separate `httpx` installation to this pinned environment. FastAPI documents uploads at https://fastapi.tiangolo.com/tutorial/request-files/ and combined forms/files at https://fastapi.tiangolo.com/tutorial/request-forms-and-files/.

The question this excerpt answers is: **how does a client upload bytes without supplying a server path?**

<!-- VERIFIED_EXCERPT: api -->

```bash
curl \
  -X POST \
  -F "media_type=text/plain" \
  -F "correlation_id=procurement-2026-0042" \
  -F "file=@supplier-note.txt;type=text/plain" \
  http://127.0.0.1:8000/v1/documents/extract
```

The `@supplier-note.txt` syntax is interpreted by the client. The server receives uploaded bytes plus untrusted filename metadata. It never opens a caller-selected server path.

> **Design checkpoint:** A thin route owns transport mechanics that cannot exist elsewhere—the awaitable upload read and HTTP size response—while delegating document policy and deterministic work to synchronous collaborators.

The design is coherent on paper. Production engineering requires evidence that each boundary behaves as promised, especially under failure.

## Prove the behavior with tests

The test strategy follows the architecture. Each layer is tested through its public behavior, and external boundaries are replaced only where substitution adds control.

| Layer          | Evidence we want                                                                             |
| -------------- | -------------------------------------------------------------------------------------------- |
| Pydantic model | Scalar metadata is accepted or rejected predictably                                          |
| Decoder        | Valid UTF-8 is preserved; invalid UTF-8 keeps causal context                                 |
| Service        | Format policy, normalization, empty-content handling and error translation work without HTTP |
| Logging        | Content and filename are absent; structured fields exist on records                          |
| HTTP boundary  | Multipart contract, sentinel limit and status mappings are stable                            |

### Test the model as a runtime boundary

The question this excerpt answers is: **does unsafe scalar metadata fail before extraction?**

<!-- VERIFIED_EXCERPT: tests -->

```python
@pytest.mark.parametrize(
    "correlation_id",
    ["", "contains space", "../escape", "value/segment", "a" * 65],
)
def test_document_request_rejects_unsafe_correlation_id(
    correlation_id: str,
) -> None:
    with pytest.raises(ValidationError):
        DocumentRequest(
            media_type="text/plain",
            correlation_id=correlation_id,
        )
```

Parametrization turns one behavioral rule into a compact boundary table. The test asserts the public Pydantic failure, not the internal validator method call.

### Test the decoder with byte-exact input

The question this excerpt answers is: **does invalid UTF-8 become the decoder's stable failure while retaining the codec cause?**

<!-- VERIFIED_EXCERPT: tests -->

```python
def test_reader_rejects_invalid_utf8() -> None:
    with pytest.raises(ReaderDecodingError) as captured:
        Utf8TextReader().decode(b"\xff\xfe\xfa")

    assert isinstance(captured.value.__cause__, UnicodeDecodeError)
```

Direct byte payloads are deterministic across operating systems. When exact newline bytes matter, avoid text-mode file writes because Windows can translate newline sequences. In this upload-oriented design, most tests do not need temporary files at all.

### Test the service with a fake decoder

The service should be tested without depending on the UTF-8 adapter for every case. The question this excerpt answers is: **how can a fake satisfy the protocol while real orchestration still runs?**

<!-- VERIFIED_EXCERPT: tests -->

```python
@dataclass(slots=True)
class FixedReader:
    text: str

    def decode(self, content: bytes) -> str:
        return self.text


def test_service_extracts_and_normalizes_text() -> None:
    service = DocumentExtractionService(
        reader=FixedReader("alpha\r\nbeta\rgamma")
    )

    result = service.extract(make_command())

    assert result.text == "alpha\nbeta\ngamma"
    assert result.line_count == 3
```

The fake is intentionally smaller than a mock-heavy arrangement. It satisfies the protocol and lets the real service execute. This gives stronger evidence than mocking private methods and asserting call sequences.

The question this excerpt answers is: **how can one test express a readable decision table for format policy?**

<!-- VERIFIED_EXCERPT: tests -->

```python
@pytest.mark.parametrize(
    ("filename", "declared_media_type", "upload_media_type"),
    [
        ("document.pdf", "application/pdf", "application/pdf"),
        ("document.md", "text/markdown", "text/markdown"),
        ("document.txt", "application/pdf", "application/pdf"),
        ("document.pdf", "text/plain", "text/plain"),
        ("document.txt", "text/plain", "application/octet-stream"),
    ],
)
def test_service_rejects_unsupported_formats(
    filename: str,
    declared_media_type: str,
    upload_media_type: str,
) -> None:
    service = DocumentExtractionService(reader=FixedReader("content"))

    with pytest.raises(UnsupportedDocumentFormatError):
        service.extract(
            make_command(
                filename=filename,
                declared_media_type=declared_media_type,
                upload_media_type=upload_media_type,
            )
        )
```

### Test structured logs without assuming a formatter

The question this excerpt answers is: **can we prove both non-leakage and traceability?**

<!-- VERIFIED_EXCERPT: tests -->

```python
assert result.text == secret_text
assert secret_text not in caplog.text
assert filename not in caplog.text
assert all(
    getattr(record, "correlation_id", None)
    == "safe-correlation-123"
    for record in caplog.records
)
```

The first two log assertions protect rendered output. The record assertion verifies structured context. A separate failure test should inspect `failure_code` on `caplog.records` rather than expecting it in `caplog.text`.

### Test the multipart boundary as multipart

Endpoint tests send form data and the file tuple separately. The question this excerpt answers is: **how do tests control each multipart source independently?**

<!-- VERIFIED_EXCERPT: tests -->

```python
def post_document(
    client: TestClient,
    *,
    content: bytes = b"alpha\r\nbeta",
    filename: str = "sample.txt",
    declared_media_type: str = "text/plain",
    upload_media_type: str = "text/plain",
    correlation_id: str = "endpoint-success-1",
) -> Response:
    return client.post(
        "/v1/documents/extract",
        data={
            "media_type": declared_media_type,
            "correlation_id": correlation_id,
        },
        files={"file": (filename, content, upload_media_type)},
    )
```

The question this excerpt answers is: **what assertion proves the sentinel-byte policy at the HTTP boundary?**

<!-- VERIFIED_EXCERPT: tests -->

```python
def test_extract_endpoint_rejects_oversized_document() -> None:
    with TestClient(create_app()) as client:
        response = post_document(
            client,
            content=b"a" * (MAX_UPLOAD_BYTES + 1),
        )

    assert response.status_code == 413
    assert response.json() == {
        "code": "document_too_large",
        "message": "document exceeds the 1 MiB upload limit",
        "correlation_id": "endpoint-success-1",
    }
```

A complete boundary suite should also cover:

* an exactly 1 MiB non-whitespace document;
* missing `media_type`, `correlation_id` and `file` fields;
* invalid correlation identifiers;
* `.txt` with the wrong declared media type;
* `.txt` with the wrong upload content type;
* matching non-text media types;
* invalid UTF-8;
* zero-byte and whitespace-only uploads;
* decoder failure translation;
* successful response serialization;
* absence of content and filename in logs.

### Run focused quality gates

Use `python -m pytest` for behavior. Use `python -m ruff check document_service tests` and `python -m ruff format --check document_service tests` for lint and formatting checks. Use `python -m mypy --strict document_service tests` for static analysis. These tools answer different questions: passing mypy does not prove UTF-8 correctness, and passing endpoint tests does not prove every type contract.

Tests also do not prove authentication, authorization, persistence safety, response-size policy, deployment configuration or production concurrency behavior. Those concerns are intentionally outside this lesson.

> **Common trap:** A test suite is evidence for named behavior under named conditions. It is not a certificate that the service is production-safe in every environment.

The implementation is now decomposed according to the failures and tests we need, not according to an abstract layering template. The remaining work is to extend the design yourself and practise defending the trade-offs.

## Practice and interview lab

The goal of this lab is not to produce more abstractions. It is to extend the service while preserving its boundary guarantees and being able to explain every design choice.

### Progressive implementation challenge

Extend the procurement document API in four stages. Complete each stage before moving to the next so that every abstraction is introduced by a real requirement.

#### Stage 1: Strengthen the existing boundary suite

Add missing tests without changing application behavior.

**Acceptance criteria**

* A multipart request missing each required field is rejected.
* An upload of exactly 1,048,576 non-whitespace bytes reaches service validation rather than returning `413`.
* An upload of 1,048,577 bytes returns `413` and `document_too_large`.
* A `.txt` file is rejected when the declared type is not `text/plain`.
* A `.txt` file is rejected when the upload content type is not `text/plain`.
* Zero-byte, whitespace-only and invalid UTF-8 uploads have distinct expected outcomes.
* Newline-sensitive tests use direct bytes.
* Structured log fields are asserted through `caplog.records`.

**Hints**

* Build a reusable multipart request helper rather than duplicating every request.
* Use `pytest.param(..., id="...")` to make media-type cases readable.
* For the exact-limit test, make the content non-whitespace so the size assertion is not confused with empty-content rejection.

#### Stage 2: Make the upload limit configurable

Replace the hard-coded constant with explicit immutable configuration while preserving the sentinel rule.

**Acceptance criteria**

* The default remains 1 MiB.
* The configured limit must be positive.
* The route reads only `configured_limit + 1` bytes.
* Exactly-at-limit content is accepted for further validation.
* Above-limit content still returns `413` and `document_too_large`.
* Byte size is not confused with decoded character count.
* Configuration is assembled at the application boundary rather than read from global mutable state inside the service.

**Hints**

* A small frozen settings dataclass can represent trusted internal configuration.
* The size limit belongs to upload handling, not newline normalization or the decoder.
* Test with multibyte UTF-8 so that byte count and character count visibly differ.

#### Stage 3: Add Markdown as a second text format

Support `.md` with declared and upload media type `text/markdown`. Do not render Markdown or build a plugin framework.

**Acceptance criteria**

* Existing `.txt` behavior remains unchanged.
* `.md` is accepted only when both media types equal `text/markdown`.
* Strict UTF-8, size, empty-content and logging policies remain identical.
* The route contract does not change.
* The service public method does not change.
* Format selection remains explicit and understandable.
* Tests cover `.md`, uppercase suffix, mismatched types and oversized Markdown.

**Hints**

* Start with a small policy mapping or explicit conditional.
* Ask whether the decoder actually needs to differ; Markdown is still UTF-8 text.
* Avoid registries, entry points and dynamic discovery until a real third-party extension requirement exists.

#### Stage 4: Design batch extraction without implementing it

Write a design note for accepting several uploads. Choose sequential execution, async tasks, a bounded thread pool, a process pool or an external worker system.

**Acceptance criteria**

Your design explains:

* per-document 1 MiB enforcement and a total batch-size policy;
* whether upload reads are awaitable;
* whether decoding or parsing is blocking or CPU-heavy;
* concurrency and queue limits;
* ordering guarantees;
* partial-success behavior;
* cancellation and timeout semantics;
* retry safety;
* backpressure;
* resource cleanup;
* observability without payload leakage;
* why the rejected concurrency models are less appropriate.

**Hints**

* Begin with workload characteristics, not a preferred framework.
* Sequential processing may be the best initial answer.
* If you choose async tasks, state exactly which operations can suspend.
* If you choose threads, state how worker and queue capacity are bounded.
* If you choose processes, account for serialization and process lifecycle.

### Boundary and failure-path exercises

#### Exercise A: Decoder exception hygiene

Create a fake decoder that raises an exception whose message contains a secret marker. Verify that the public response and logs do not reproduce that marker.

**Acceptance criteria**

* The service translates the decoder failure into the documented application category.
* The original exception remains available as `__cause__`.
* The public error body contains a stable code and safe message.
* The secret marker is absent from `caplog.text`.

**Hint:** Stable public messages should be authored by the application layer rather than copied from arbitrary dependency exceptions.

#### Exercise B: Media-type decision table

Write a parametrized test table for filename suffix, declared media type and upload content type.

**Acceptance criteria**

* Valid `.txt`/`text/plain`/`text/plain` succeeds.
* Every single-field mismatch fails.
* Matching non-text types still fail.
* Missing upload content type is represented by the route's fallback and fails.
* Test IDs explain the failed policy case.

**Hint:** Separate “the two types match” from “the matched type is supported.” Both rules matter.

#### Exercise C: Logging policy regression test

Add one success case and one failure case containing unique secrets in both content and filename.

**Acceptance criteria**

* Neither secret appears in rendered log text.
* The correlation identifier exists on the relevant records.
* The failure record contains the expected `failure_code` attribute.
* The test does not depend on a formatter rendering `extra` values.

**Hint:** Inspect both `caplog.text` and `caplog.records`; they expose different aspects of logging behavior.

### Senior-level discussion prompts

Use the frameworks below to structure an answer. A strong answer should begin with the decision criterion, apply it to this service, state trade-offs and then handle the follow-up scenario.

#### Mutable versus immutable objects

**Question:** Why use frozen dataclasses for the command and result?

**Strong-answer framework**

1. Explain reference semantics and aliasing: multiple components can observe the same mutable object.
2. Connect mutation to Applied AI risks such as order-dependent prompts, changed evaluation inputs and inconsistent cache keys.
3. Explain that `frozen=True` blocks field reassignment but is shallow.
4. State when mutable state is still appropriate: controlled lifecycle owned by one object.
5. Discuss copying and immutable nested values as trade-offs rather than universal rules.

**Follow-up questions**

* What changes if the command contains `list[str]`?
* When would a defensive copy be too expensive?
* How would you protect a nested metadata mapping?

#### Plain classes versus dataclasses versus Pydantic

**Question:** Why is the service a plain class, the command a dataclass and the request a Pydantic model?

**Strong-answer framework**

1. Start with responsibility, not syntax.
2. Plain class: owns a decoder dependency and orchestration behavior.
3. Frozen dataclass: carries already-validated internal state with value-like semantics.
4. Pydantic `BaseModel`: validates and serializes untrusted boundary data.
5. Explain why using Pydantic everywhere would couple the domain to a boundary library.
6. Explain why a stateless transformation remains a function.

**Follow-up questions**

* Can a dataclass contain methods?
* When would a class method be preferable to a module function?
* Why is composition preferable to making the service inherit from the decoder?

#### Static typing versus runtime validation

**Question:** What does `content: bytes` protect us from?

**Strong-answer framework**

1. State that annotations communicate an internal contract and support static analysis.
2. State that Python does not generally enforce ordinary annotations at call time.
3. Identify the live checks: Pydantic metadata validation, byte-length limit, media-type policy and strict decoding.
4. Explain that validation proves schema conformance, not factual truth or safety.
5. Discuss containing untyped external values near the boundary.

**Follow-up questions**

* Can mypy prove that content is valid UTF-8?
* Can Pydantic prove that `text/plain` is truthful?
* When can strict validation be too restrictive?

#### Generators versus lists

**Question:** Should line processing return a generator?

**Strong-answer framework**

1. Compare lazy single-pass production with eager repeatable materialization.
2. Evaluate the actual bound: the current document is at most 1 MiB.
3. Discuss deferred errors, retry behavior and resource lifetime.
4. State whether early termination creates a concrete benefit.
5. Choose the simpler list unless laziness solves a measured problem.

**Follow-up questions**

* When does a generator body execute?
* How do you retry after partial consumption?
* What happens if a generator holds a database cursor?

#### Threads versus async

**Question:** Why is the route async while the service is synchronous?

**Strong-answer framework**

1. Identify the concrete awaitable: `UploadFile.read()`.
2. Explain cooperative concurrency and suspension.
3. State that decoding and normalization are bounded synchronous work.
4. Explain that `async def` does not make blocking or CPU work faster.
5. Compare bounded threads for blocking I/O, processes for CPU-heavy work and sequential execution for simplicity.
6. Include cancellation, timeouts and backpressure.

**Follow-up questions**

* What happens if the service calls a blocking SDK?
* Can a running worker thread be safely cancelled?
* When would a process pool be a poor fit?

#### Exception translation

**Question:** Why not return `UnicodeDecodeError` directly?

**Strong-answer framework**

1. Name the abstraction boundaries: codec, decoder, service and HTTP.
2. Translate when the vocabulary changes and the layer can add meaning.
3. Preserve causal context with `raise ... from exc`.
4. Keep public codes stable and messages safe.
5. Avoid wrapping errors when no meaning is added.

**Follow-up questions**

* When should an exception propagate unchanged?
* Why is `except Exception: return ""` dangerous?
* Which layer should choose HTTP `415`?

#### Safe logging

**Question:** What information is useful without leaking the procurement document?

**Strong-answer framework**

1. Start with operational questions: which request, which stage, which failure category and what size/result dimensions?
2. Allow a safe correlation identifier, event name, media types, counts and stable failure code.
3. Exclude content, filename, arbitrary metadata and unreviewed exception messages.
4. Explain module-level loggers and application-owned configuration.
5. Explain `caplog.records` versus `caplog.text`.

**Follow-up questions**

* Is a filename sensitive?
* When should a traceback be logged?
* How would you test a field supplied through `extra`?

#### Thin routes

**Question:** Is the bounded read business logic, and does it make the route too thick?

**Strong-answer framework**

1. Define a thin route as one limited to transport responsibilities, not one with zero decisions.
2. Explain that `UploadFile.read()` and HTTP `413` exist only at the HTTP boundary.
3. Keep format policy, decoding, normalization and logging in the service and adapters.
4. Discuss the cost of extra modules and when a separate service would be unnecessary.
5. Emphasize testability without HTTP.

**Follow-up questions**

* Should the service accept `UploadFile`?
* Where should request-model conversion happen?
* When is layering speculative?

#### Bounded uploads

**Question:** Why read one byte beyond the limit?

**Strong-answer framework**

1. State the accepted maximum in bytes.
2. Explain the ambiguity of reading exactly the maximum.
3. Explain how the sentinel proves excess while keeping the read bounded.
4. Distinguish byte count from decoded character count.
5. State what this does not solve: proxy limits, parser behavior, response size and deployment controls.

**Follow-up questions**

* Is exactly 1 MiB accepted?
* Why not trust a declared size?
* What changes when the limit becomes configurable?

#### Unsafe server paths

**Question:** Why use `UploadFile` instead of accepting a path string?

**Strong-answer framework**

1. Explain that a caller-supplied server path asks the process to access resources with server permissions.
2. Name risks: configuration, credentials, mounted volumes, other tenants' data, symbolic links and race conditions.
3. Explain why string normalization alone is insufficient.
4. Treat the filename only as untrusted metadata.
5. For stored documents, propose opaque identifiers plus authorization-aware storage rather than arbitrary paths.

**Follow-up questions**

* Why is removing `../` insufficient?
* Can the uploaded filename become a storage key?
* How would tenant isolation alter the design?

### Compact knowledge check

#### Questions

1. Which multipart values are validated by `DocumentRequest`, and which relevant values come from `UploadFile`?
2. Why does the route request 1,048,577 bytes for a 1 MiB limit?
3. What response should an oversized upload produce?
4. Why are both media types checked even when the filename ends in `.txt`?
5. Why is strict UTF-8 decoding still required after media-type validation?
6. How does the service reject whitespace-only content without trimming the returned text?
7. What does `TextReader` contribute beyond calling `bytes.decode()` directly?
8. Why are `ExtractionCommand` and `ExtractedDocument` frozen dataclasses rather than Pydantic models?
9. What does `raise DocumentDecodingError(...) from exc` preserve?
10. Why might `correlation_id` be absent from `caplog.text` but present in `caplog.records`?
11. What is one generator advantage and one generator risk?
12. Why does the async route not require an async service?
13. Which dependency parses multipart form data?
14. Which dependency is used by the resolved endpoint-test setup?
15. Why must the API never accept a caller-controlled server path?

#### Answers

1. `DocumentRequest` validates scalar form fields `media_type` and `correlation_id`; filename and upload content type come from `UploadFile`.
2. The extra sentinel byte distinguishes exactly-at-limit content from the prefix of a larger upload.
3. HTTP `413` with stable code `document_too_large`.
4. Suffix and media types are independent untrusted signals; all required signals must satisfy the policy.
5. Media types are metadata and do not prove that the bytes form valid UTF-8 text.
6. It checks `normalized_text.strip() == ""` but returns `normalized_text` rather than the stripped value.
7. It isolates decoding policy, enables substitution in tests and provides a boundary for exception translation.
8. They carry already-validated internal values and do not need boundary parsing, schema generation or coercion behavior.
9. The original causal exception and traceback relationship.
10. `extra` creates `LogRecord` attributes; the active formatter may omit those attributes from rendered text.
11. A generator can reduce memory or support early termination; it is single-pass and can defer errors or retain resources.
12. Only the upload read is awaitable; bounded decoding and domain transformations remain synchronous.
13. `python-multipart==0.0.32`.
14. `httpx2==2.7.0` with Starlette's `TestClient` in this pinned environment.
15. It could cause the application to read resources using server-process permissions, exposing sensitive files or other tenants' data.

The lesson intentionally stops before response-size controls, authentication, authorization, persistence, deployment, advanced streaming and production concurrency tuning. Those concerns require additional product and operational context rather than more Week 1 abstractions.

## References

### Python

* Python 3.13.12 release: https://www.python.org/downloads/release/python-31312/
* Virtual environments: https://docs.python.org/3.13/library/venv.html
* Classes: https://docs.python.org/3.13/tutorial/classes.html
* Data model: https://docs.python.org/3.13/reference/datamodel.html
* Type hints: https://docs.python.org/3.13/library/typing.html
* Dataclasses: https://docs.python.org/3.13/library/dataclasses.html
* Exceptions and chaining: https://docs.python.org/3.13/tutorial/errors.html
* Logging HOWTO: https://docs.python.org/3.13/howto/logging.html
* Logging reference: https://docs.python.org/3.13/library/logging.html
* Iterators and generators: https://docs.python.org/3.13/tutorial/classes.html#iterators
* `asyncio`: https://docs.python.org/3.13/library/asyncio.html
* Coroutines and tasks: https://docs.python.org/3.13/library/asyncio-task.html
* Executors: https://docs.python.org/3.13/library/concurrent.futures.html
* PEP 484 — Type Hints: https://peps.python.org/pep-0484/
* PEP 544 — Protocols: https://peps.python.org/pep-0544/
* PEP 557 — Data Classes: https://peps.python.org/pep-0557/
* PEP 255 — Simple Generators: https://peps.python.org/pep-0255/

### Pydantic v2

* Models and `BaseModel`: https://docs.pydantic.dev/latest/concepts/models/
* Model configuration: https://docs.pydantic.dev/latest/concepts/config/
* Fields: https://docs.pydantic.dev/latest/concepts/fields/
* Validators: https://docs.pydantic.dev/latest/concepts/validators/
* Serialization: https://docs.pydantic.dev/latest/concepts/serialization/
* Strict mode: https://docs.pydantic.dev/latest/concepts/strict_mode/
* Validation errors: https://docs.pydantic.dev/latest/errors/errors/

### FastAPI and Starlette

* Uploading files with `UploadFile`: https://fastapi.tiangolo.com/tutorial/request-files/
* Combining forms and files: https://fastapi.tiangolo.com/tutorial/request-forms-and-files/
* Dependencies: https://fastapi.tiangolo.com/tutorial/dependencies/
* Response models: https://fastapi.tiangolo.com/tutorial/response-model/
* Error handling: https://fastapi.tiangolo.com/tutorial/handling-errors/
* Application routers: https://fastapi.tiangolo.com/tutorial/bigger-applications/
* Async guidance: https://fastapi.tiangolo.com/async/
* FastAPI testing: https://fastapi.tiangolo.com/tutorial/testing/
* Testing dependency overrides: https://fastapi.tiangolo.com/advanced/testing-dependencies/
* Starlette `TestClient`: https://www.starlette.io/testclient/

### pytest and dependencies

* pytest assertions and expected exceptions: https://docs.pytest.org/en/stable/how-to/assert.html
* pytest fixtures: https://docs.pytest.org/en/stable/how-to/fixtures.html
* pytest parametrization: https://docs.pytest.org/en/stable/how-to/parametrize.html
* pytest logging and `caplog`: https://docs.pytest.org/en/stable/how-to/logging.html
* `python-multipart`: https://pypi.org/project/python-multipart/
* `httpx2`: https://pypi.org/project/httpx2/
* `pip install`: https://pip.pypa.io/en/stable/cli/pip_install/
