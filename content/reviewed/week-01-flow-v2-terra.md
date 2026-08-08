---
layout: week
permalink: /weeks/week-01/
description: Build a typed, validated, and testable procurement-document extraction API with Python and FastAPI.
title: Python for production AI systems
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-01/beginner/
---

## A dependable answer to one small question

A procurement operations team receives short supplier notes: delivery confirmations, scope clarifications, and exception reports. Analysts should not have to copy these documents into an internal workflow by hand. Our service accepts one uploaded text document and returns a stable, machine-readable description of it.

Start with the answer a downstream system needs, not with FastAPI, a directory diagram, or a catalog of Python features:

```json
{
  "correlation_id": "procurement-2026-0042",
  "media_type": "text/plain",
  "text": "Supplier confirms delivery on 18 August.\nEscalate any delay.",
  "character_count": 62,
  "line_count": 2
}
```

The service is intentionally narrow. It accepts multipart form data with `media_type`, `correlation_id`, and a `file`; it supports UTF-8 `.txt` documents only; and it returns either the stable result above or a safe, stable failure category. A caller uploads bytes. It does **not** submit a path on the application server. That distinction prevents the API from becoming a way to read files that happen to be accessible to the server process.

We will build the explanation in the same order that a reliable implementation becomes necessary. First make one transformation trustworthy. Then decide where state belongs. Then make contracts precise, make failures useful, and make evidence safe. Only after those pieces are familiar will we assemble the HTTP application around them.

### The contract, stated precisely

For this first version, success means all of the following are true:

- the filename has a `.txt` suffix (case-insensitively);
- both the declared form value and the upload content type are exactly `text/plain`;
- at most 1,048,576 bytes are accepted;
- the bytes decode as strict UTF-8;
- the decoded document contains at least one non-whitespace character;
- newline representation is normalized to `\n`, without trimming other whitespace; and
- the response contains the correlation identifier, normalized text, and counts derived from that text.

The restriction is useful rather than arbitrary. Metadata does not prove what bytes contain, so the service checks metadata *and* strict decoding. Neither is a malware scan, document authenticity guarantee, or authorization policy. Those are separate concerns and are outside this bounded service.

**Checkpoint.** Which field should a downstream system use to connect an extraction result to its request? `correlation_id`, not a filename: a filename is untrusted metadata and may be sensitive or non-unique.

The output tells us what must be true. Our next question is smaller: how can one of those truths be made easy to reason about?

## 1. Begin with a transformation that has no hidden state

### Question: what does it mean to normalize a document without changing its content?

Text documents can use `\n`, Windows `\r\n`, or legacy `\r` line endings. A consumer that counts or splits lines should not have to remember all three. Normalization makes line representation uniform while deliberately preserving leading spaces, trailing spaces, and the content of each line.

The repository uses this pure function:

```python
def normalize_newlines(text: str) -> str:
    """Normalize newline representation without trimming other whitespace."""
    return text.replace("\r\n", "\n").replace("\r", "\n")
```

Its contract is compact:

```python
assert normalize_newlines("alpha\r\nbeta\rgamma") == "alpha\nbeta\ngamma"
assert normalize_newlines("  alpha  \r\n") == "  alpha  \n"
```

There is no file access, clock, logging, dependency, or object state. The output is determined by the input. That makes a pure function easy to test, reuse, and move without changing its meaning. It also tells a future reader that this code owns one policy: newline representation.

**Boundary.** `text.strip()` would make an attractive but wrong implementation. It removes whitespace that may be meaningful to a procurement note or an upstream parser. The service may use `normalized_text.strip() == ""` to decide whether a document is empty, but it must return the original normalized text rather than the stripped text.

**Checkpoint.** If input is `"  \r\n"`, should normalization return `"\n"` or `""`? It returns `"  \n"`; emptiness is a separate decision.

This separation exposes the next pressure. Newline replacement needs no collaborator. Strictly decoding uploaded bytes does.

## 2. Put state and responsibility where they belong

### Question: when should this code become a class?

A class earns its existence when it owns state, a dependency, a lifecycle, or a coherent set of operations. An extraction coordinator has an injected reader and a policy for composing validation, decoding, normalization, and a result. That is a real responsibility. A stateless newline transformation is not.

The service holds its reader on each instance:

```python
class DocumentExtractionService:
    supported_media_type: ClassVar[str] = "text/plain"
    supported_suffix: ClassVar[str] = ".txt"

    def __init__(self, reader: TextReader) -> None:
        self._reader = reader
```

`self._reader` is instance state: two services can use different readers. The supported media type and suffix are class policy in this small implementation: one shared value for every instance. `ClassVar` documents that these values are not per-instance data. `__init__` constructs a usable service by receiving, rather than secretly creating, its external collaborator.

The resulting usage is composition:

```python
reader = Utf8TextReader()
service = DocumentExtractionService(reader=reader)
result = service.extract(command)
```

Composition says “the service has a reader.” Inheritance would say “the service is a reader,” which is false. It would also mix orchestration with decoding policy and make replacement less direct.

### Methods are not all the same tool

An instance method takes `self` because it uses instance state, as `extract()` uses `self._reader`. A class method takes `cls` and is useful when its behavior is based on class policy. The repository makes `_validate_command` a class method because it refers to `cls.supported_media_type` and `cls.supported_suffix`. A static method is simply a function placed on a class namespace; use one only when that location conveys a strong conceptual relationship. Do not add one merely to make an API look object-oriented.

**Boundary.** A service that imports `Utf8TextReader` and constructs it inside every business method is harder to test: the test must patch a concrete dependency to simulate a decode failure. Constructor injection makes the test pass a small fake instead. This is not dependency injection theatre; it is a direct response to replaceability.

**Checkpoint.** Where should a future PDF parser fit: subclass `DocumentExtractionService`, or provide an appropriate reader/parser dependency? Prefer the latter unless the service itself truly becomes a specialized kind of another service.

The class now expresses ownership, but Python still has to communicate what may cross its methods. That is the role of static contracts.

## 3. Let type hints state intent, not pretend to police the boundary

### Question: what does `content: bytes` actually guarantee?

Type annotations make internal expectations visible to people and static analysis tools. They help a checker notice that a caller supplies text where bytes are expected, or that a function returns an optional value without handling `None`. Ordinary Python annotations do not, by themselves, validate values passed at runtime.

```python
def decode_document(content: bytes) -> str:
    return content.decode("utf-8", errors="strict")

decode_document("not bytes")  # Annotation does not prevent this call at runtime.
```

The call will fail only when `.decode` is attempted, and its failure vocabulary will be an implementation accident. At an untrusted HTTP boundary we want predictable validation before internal code relies on data.

Use precise annotations to make meaningful distinctions:

```python
def select_label(labels: list[str], preferred: str | None) -> str:
    if preferred is not None:
        return preferred
    return labels[0]

def summarize(lines: tuple[str, ...]) -> dict[str, int]:
    return {"line_count": len(lines)}
```

`str | None` forces the implementation to narrow the optional value before treating it as `str`. `list[str]`, `tuple[str, ...]`, and `dict[str, int]` say more than unparameterized collections. They do not prove that an input is safe, truthful, UTF-8, or authorized.

### A protocol is a contract for behavior

The decoder boundary is deliberately narrow:

```python
from typing import Protocol

class TextReader(Protocol):
    """Narrow interface required by the extraction service."""

    def decode(self, content: bytes) -> str: ...
```

`Protocol` describes the capability the service needs rather than a base class the reader must inherit. Any object with a compatible `decode(bytes) -> str` can satisfy the static contract. A test fake can therefore be tiny:

```python
class FixedReader:
    def __init__(self, text: str) -> None:
        self._text = text

    def decode(self, content: bytes) -> str:
        return self._text
```

**Boundary.** Structural typing does not make an arbitrary object safe at runtime. Nor does a protocol need to model every possible parser operation. Start with the operation actually required; broad interfaces make both implementations and tests harder to understand.

**Checkpoint.** Can a type checker prove `b"\xff"` is valid UTF-8? No. Validity of the bytes is runtime data, so it belongs in a runtime boundary.

We now need a boundary that turns HTTP strings into trusted scalar values with explicit failures.

## 4. Validate untrusted values at the runtime boundary

### Question: why introduce Pydantic after type hints?

The distinction is clearest after seeing a correctly annotated function accept a wrong runtime value. `DocumentRequest` is a Pydantic `BaseModel` precisely because form fields come from an untrusted request. It parses, validates, and serializes a declared schema; it is not the domain object for every value in the application.

```python
class DocumentRequest(BaseModel):
    """Untrusted scalar request boundary."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    media_type: str = Field(min_length=1, max_length=128)
    correlation_id: str = Field(min_length=1, max_length=64)

    @field_validator("media_type")
    @classmethod
    def validate_media_type_text(cls, value: str) -> str:
        if value != value.strip():
            raise ValueError("media_type must not contain surrounding whitespace")
        return value
```

This is ordinary Python class inheritance with framework-defined behavior. Fields are class annotations, `model_config` sets model policy, and a field validator adds a rule local to one field. `extra="forbid"` rejects undeclared fields when model validation receives a mapping; `strict=True` asks Pydantic not to silently coerce values where strict behavior applies; `frozen=True` prevents ordinary field reassignment on the model. Pydantic reports invalid input as a structured `ValidationError`.

The correlation identifier has a deliberately restricted character set in the repository: an initial alphanumeric character followed by up to 63 alphanumeric, dot, underscore, or hyphen characters. The point is not that regex validation authenticates a caller. It provides a bounded, safe identifier format for the service’s own correlation context.

```python
request = DocumentRequest(
    media_type="text/plain",
    correlation_id="procurement-2026-0042",
)
payload = request.model_dump()
```

`model_dump()` is serialization at a typed boundary. A field validator is appropriate when one field can be checked alone. A model validator would be appropriate for a rule involving multiple declared fields. Neither should be used to validate upload bytes, because those bytes arrive through a different HTTP object.

**Boundary.** “Validated” does not mean “true.” A caller can label non-text bytes `text/plain`; strict UTF-8 decoding must still inspect the bytes. A valid correlation identifier does not establish identity or tenant authorization.

**Checkpoint.** Why not parse `UploadFile` into this model too? The model owns scalar form metadata; file reading and upload content type belong to FastAPI’s upload boundary.

Once values have been checked, internal code needs a lightweight way to carry them without repeatedly invoking a boundary framework.

## 5. Carry trusted internal values as values

### Question: what should hold a request after its boundary fields are available?

The extraction coordinator receives an internal command and produces an internal result. The repository represents both with frozen, slotted dataclasses:

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

A dataclass supplies value-oriented construction and comparison with little ceremony. `frozen=True` prevents reassignment such as `command.filename = "other.txt"`, which reduces accidental mutation as the value crosses layers. `slots=True` prevents an arbitrary instance dictionary and makes the shape explicit; it is not a security control.

Frozen is shallow. It protects the dataclass attribute binding, not necessarily objects stored in it:

```python
@dataclass(frozen=True)
class Labels:
    values: list[str]

labels = Labels(values=["urgent"])
labels.values.append("review")  # Allowed: the list itself remains mutable.
```

For immutable nested state, choose immutable nested types such as `tuple[str, ...]`, use a read-only mapping representation, or make a defensive copy at a well-chosen boundary. Do not promise deep immutability merely because a dataclass is frozen.

The choice of representation follows responsibility:

- a function performs a stateless transformation;
- a plain class owns a dependency and behavior;
- a frozen dataclass carries already-known internal values; and
- a Pydantic model parses or serializes an external contract.

**Boundary.** A dataclass annotation is still not runtime input validation. Constructing `ExtractionCommand(content="text")` is possible unless another check prevents it. That is acceptable because it is an internal type, built after the route has received bytes and the service owns further document policy.

**Checkpoint.** Does freezing `ExtractionCommand` prove the contents are valid UTF-8? No. Immutability controls reassignment; decoding validates representation.

The command tells us what to decode. Next we make the decoding policy replaceable and its failure meaningful.

## 6. Isolate strict decoding behind a small adapter

### Question: why not call `content.decode()` directly in the service?

The real UTF-8 reader is intentionally small:

```python
class Utf8TextReader:
    """Decode complete UTF-8 document content strictly."""

    encoding: ClassVar[str] = "utf-8"

    def decode(self, content: bytes) -> str:
        try:
            return content.decode(self.encoding, errors="strict")
        except UnicodeDecodeError as exc:
            raise ReaderDecodingError(
                "document resource is not valid UTF-8"
            ) from exc
```

The reader owns a codec-specific operation. The service owns document extraction policy. Separating them means a future adapter can decode another accepted representation without turning the service into a switchboard for codec internals. It also means a test can make the reader fail deterministically without corrupt bytes or depending on implementation details.

This boundary gives a useful import direction:

```text
service  --->  ports  <---  readers
    |                         |
    +-------> domain/errors <--+
```

The service depends on the `TextReader` protocol, not on `Utf8TextReader`. Composition happens at the application edge. If a domain module must import the FastAPI route, while the route already imports the domain module, the circular import is usually a design signal: a lower-level module has learned about its caller’s framework.

**Boundary.** Strict decoding rejects invalid byte sequences. It does not check that a sentence is useful, that an encoding label is truthful, or that text is free of malicious instructions. Keep claims aligned with the control actually implemented.

**Checkpoint.** Which layer should know about `UnicodeDecodeError`? The reader knows the codec error; the service should receive an application-relevant reader failure instead.

Now we can name every important way the operation fails.

## 7. Give failures a stable vocabulary

### Question: why not let every exception reach HTTP unchanged?

Callers need stable categories, not Python implementation details. Operators need causal context, not a mysterious generic error. Those are compatible when each boundary translates only when it can add meaning.

The repository establishes a hierarchy rooted in `DocumentServiceError`, including validation failures, unsupported formats, extraction failures, decode failures, empty documents, and infrastructure failures. Each carries a stable `code` and the correlation identifier. The reader translates a codec exception into `ReaderDecodingError`; the service translates that into `DocumentDecodingError`:

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

`raise ... from exc` retains the causal chain in `__cause__`. This supports diagnosis without copying a low-level exception message into a public response or log field. Translate where vocabulary changes: codec failure becomes document-decoding failure, which later becomes a documented client response. Do not wrap an exception merely to add another stack frame.

The service validates its actual business policy before decode:

```python
if command.declared_media_type != cls.supported_media_type:
    raise UnsupportedDocumentFormatError(...)
if command.upload_media_type != command.declared_media_type:
    raise UnsupportedDocumentFormatError(...)
if not command.filename.lower().endswith(cls.supported_suffix):
    raise UnsupportedDocumentFormatError(...)
```

These signals are independently untrusted. A `.txt` suffix does not redeem `application/pdf`; two matching unsupported types do not become supported; a claimed `text/plain` type does not prove UTF-8 bytes.

**Boundary.** Avoid `except Exception: return ""` or a bare `except`. It destroys failure categories, may hide programming bugs, and can turn a bad document into a misleading successful result. Cleanup belongs in a context manager or `finally` when a resource truly needs it; it is not a reason to suppress a failure.

**Checkpoint.** When should an exception propagate unchanged? When the current layer cannot add policy or vocabulary and the next layer already owns the error contract.

Failures now have safe names. We can record their occurrence without recording the procurement document itself.

## 8. Produce operational evidence without leaking the document

### Question: what would an on-call engineer need to know at 02:00?

They need to connect events for one request, see the stage and category of a failure, and observe safe dimensions such as media type or output counts. They do not need raw supplier text, filenames, arbitrary request metadata, or a decoder’s unreviewed error message.

The service uses a module logger and structured fields:

```python
logger = logging.getLogger(__name__)

logger.info(
    "document_extraction_completed",
    extra={
        "correlation_id": result.correlation_id,
        "media_type": result.media_type,
        "character_count": result.character_count,
        "line_count": result.line_count,
    },
)
```

`logging.getLogger(__name__)` lets application configuration decide handlers, formatters, routing, and levels. A library module should not configure the root logger as an import side effect. Use `DEBUG` for diagnostic detail, `INFO` for meaningful lifecycle events, `WARNING` for handled expected failures, and `ERROR`/`logger.exception` when an unexpected failure needs a traceback. The appropriate level depends on the operational contract, not on a universal numeric rule.

`extra` creates attributes on a `LogRecord`. A formatter might not render them into `caplog.text`, so tests for structured context should inspect `caplog.records` too.

```python
assert all(
    record.correlation_id == "procurement-2026-0042"
    for record in caplog.records
)
assert "SUPPLIER-SECRET" not in caplog.text
```

**Boundary.** A correlation ID must itself be handled as governed metadata. The constrained format here helps avoid uncontrolled values in logs, but it is not a substitute for an organizational retention policy. Filenames are often sensitive enough to exclude.

**Checkpoint.** Why is logging a document’s character count usually safer than logging its text? The count supports capacity and outcome diagnosis without reproducing the document’s semantic content.

We have dealt with eager, bounded processing. The next concept is laziness, by itself—no event loop required.

## 9. Learn generators without smuggling in concurrency

### Question: should line processing return a list or a generator?

An *iterable* can provide an iterator. An *iterator* produces items one at a time with `next()` until it raises `StopIteration`. A generator function is a convenient way to construct such an iterator: its body begins only when iteration begins, pauses at `yield`, and resumes for the next item.

```python
from collections.abc import Iterator


def nonblank_lines(text: str) -> Iterator[str]:
    for line in text.splitlines():
        if line.strip():
            yield line

lines = nonblank_lines("alpha\n\nbeta\n")
first_pass = list(lines)     # ["alpha", "beta"]
second_pass = list(lines)    # []
```

The benefit is deferred work and potentially lower memory use. If a downstream operation can stop after finding the first matching line, it need not materialize every line. That does **not** mean generators are automatically better. The current upload is limited to 1 MiB and the repository returns the full normalized text anyway; a list can be simpler when repeatable traversal is needed.

Deferred execution changes where errors appear:

```python
from collections.abc import Iterator


def parse_numbers(values: list[str]) -> Iterator[int]:
    for value in values:
        yield int(value)

stream = parse_numbers(["1", "not-a-number"])
next(stream)       # 1
next(stream)       # ValueError occurs here, not at construction.
```

Generators may also retain resources. A generator that owns a file handle or database cursor needs an explicit lifecycle strategy, such as a context manager around the resource owner; abandonment after partial iteration must not leak it. For a small complete text document, an ordinary function returning a concrete value may be the safer default.

**Boundary.** A generator is lazy and single-pass; it is not asynchronous and it does not make CPU work parallel. Conflating those ideas creates debugging and retry surprises.

**Checkpoint.** Can you retry a partially consumed generator by iterating it again? No. Construct a new generator from durable input, and decide explicitly whether re-reading the source is safe.

We now start over with a separate problem: handling waiting without blocking unrelated requests.

## 10. Choose concurrency from the work that actually waits

### Question: why is the route `async def` while extraction is synchronous?

An event loop coordinates tasks cooperatively. When a task reaches `await` on an awaitable operation, it can suspend, allowing the loop to run another ready task. It resumes when the awaited operation completes. This helps throughput for overlapping waiting, such as network or upload reads. It does not turn ordinary CPU work into parallel execution.

The eventual route uses:

```python
content = await file.read(MAX_UPLOAD_BYTES + 1)
```

`UploadFile.read()` is awaitable, so the HTTP boundary is async. The repository’s strict decode, newline replacement, object construction, and policy checks are bounded synchronous work on at most 1 MiB. They do not require an asynchronous service interface merely because the route is asynchronous.

Consider three workload shapes:

| Work | Useful initial choice | Reason |
| --- | --- | --- |
| Awaitable upload or network I/O | `async`/`await` | Tasks can yield while waiting. |
| Blocking third-party I/O with no async client | Bounded thread pool, if justified | Keeps blocking wait off the event-loop thread. |
| CPU-heavy OCR or parsing | Process pool or external worker, if measured and needed | Avoids starving the event loop; processes have serialization and lifecycle costs. |

For this service, sequential synchronous domain work is the simplest defensible choice. A route declared `async` that calls a slow blocking SDK directly can stall the event loop; changing the function signature does not repair that. Conversely, a thread pool is not a free optimization: it needs worker bounds, queue limits, error handling, observability, and shutdown behavior.

Cancellation is cooperative. A task awaiting an operation can receive cancellation at an await point; a running thread is not safely force-cancelled by Python. Timeouts should be scoped to the operation with a defined cleanup policy. Backpressure means bounding admission and queued work so a surge does not turn into unbounded memory, file descriptors, or executor tasks.

**Boundary.** Do not infer “async is faster.” It may increase throughput for waiting workloads, while adding overhead and failure modes. Do not make this 1 MiB, complete-read extraction path stream merely because the framework supports streaming.

**Checkpoint.** If a future parser spends two seconds in CPU-bound OCR, what is the first question? Measure whether it blocks the event loop and characterize workload, not “where can I add `await`?”

The pieces are ready. Only now do we assemble the route around them.

## 11. Assemble the HTTP boundary after the domain is familiar

### Question: what is the thinnest route that still owns HTTP responsibilities?

The route is allowed to make transport decisions: parse multipart form fields, read an `UploadFile`, enforce the byte read bound, construct an internal command from transport values, invoke the service, and convert a result to a response model. It should not contain the document-format policy, decoding implementation, normalization, or logging policy.

First, scalar multipart metadata is parsed by a dependency that creates `DocumentRequest`. It catches Pydantic’s `ValidationError` and re-expresses it as FastAPI’s request-validation form. The file remains a separate `UploadFile`, because it has its own filename, content type, and async read operation.

Second, the route reads *one byte beyond* the permitted maximum:

```python
MAX_UPLOAD_BYTES = 1_048_576

content = await file.read(MAX_UPLOAD_BYTES + 1)
if len(content) > MAX_UPLOAD_BYTES:
    raise DocumentTooLargeError(
        "document exceeds the 1 MiB upload limit",
        correlation_id=request.correlation_id,
    )
```

Reading exactly 1,048,576 bytes cannot distinguish an exactly-at-limit upload from the first 1,048,576 bytes of a larger upload. The sentinel byte makes that distinction while bounding the application read. Exactly 1 MiB proceeds to service validation; 1 MiB plus one byte produces the stable `document_too_large` category and HTTP 413. Byte size is not decoded character count: UTF-8 characters can require multiple bytes.

If `UploadFile.read` raises `OSError`, the route translates it to `DocumentInfrastructureError`, because the route owns that upload I/O boundary. It does not expose an operating-system message to the client.

Third, build the domain command from the correct sources:

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

The fallback upload media type fails the strict supported-type policy. The service, not the route, checks suffix, declared type, upload type, strict decoding, whitespace-only content, normalization, and output counts. `ExtractionResponse` is a separate Pydantic serialization boundary that makes the successful JSON shape explicit.

Finally, the application maps semantic failures to HTTP. Unsupported format maps to 415; oversized content to 413; request validation and extraction failures to 422; upload infrastructure failure to 503. The stable response is an `ErrorResponse` containing `code`, a safe message, and correlation ID. HTTP mapping is deliberately outside the domain service: the service remains useful and testable without a web server.

**Boundary.** A thin route is not a route with zero code. A bounded `UploadFile` read and 413 response are inherently HTTP concerns. Passing `UploadFile` into the service would make the service depend on FastAPI’s transport object and blur this boundary.

**Checkpoint.** Why check both form `media_type` and `file.content_type`? They are independent, caller-controlled signals. Agreement is necessary but not sufficient; the agreed type must also be supported.

## 12. Prove behavior in the same order it was built

### Question: which test fails closest to the defect?

Use a proof ladder. Test deterministic, framework-free logic first; test boundaries next; test the composed HTTP path last. This produces failures with small search spaces and avoids making every policy test a multipart test.

1. **Pure domain functions.** Verify newline normalization and logical line counting with direct strings, including `\r\n`, `\r`, and whitespace preservation.
2. **Pydantic request boundary.** Verify accepted safe identifiers, rejected spaces and path-like values, extra-field rejection, and field constraints.
3. **Reader adapter.** Send byte-exact valid UTF-8 and invalid byte sequences. Assert a `ReaderDecodingError` chains from `UnicodeDecodeError`.
4. **Service.** Supply a fake reader to test normalization, media policy, empty document rejection, and error translation without HTTP.
5. **Logs.** Use `caplog` to check safe record attributes and absence of unique secret text/filenames in rendered logs.
6. **Multipart endpoint.** Use `TestClient` to exercise form parsing, sentinel size handling, response serialization, and HTTP exception mappings together.

The service test’s fake isolates an external boundary rather than mocking the implementation under test. It follows Arrange–Act–Assert:

```python
def test_service_extracts_and_normalizes_text() -> None:
    # Arrange
    service = DocumentExtractionService(
        reader=FixedReader("alpha\r\nbeta\rgamma")
    )
    command = make_command(content=b"irrelevant-to-fixed-reader")

    # Act
    result = service.extract(command)

    # Assert
    assert result.text == "alpha\nbeta\ngamma"
    assert result.line_count == 3
```

For multipart HTTP, the actual test helper uses byte-exact data and a filename/content-type tuple:

```python
response = client.post(
    "/v1/documents/extract",
    data={"media_type": "text/plain", "correlation_id": "endpoint-success-1"},
    files={"file": ("sample.txt", b"alpha\r\nbeta", "text/plain")},
)
assert response.status_code == 200
assert response.json()["text"] == "alpha\nbeta"
```

Parametrization is effective for a decision table. Vary filename suffix, declared media type, and upload media type one signal at a time, then include matching-but-unsupported types. Fixtures should establish real reusable context, not hide the subject under test. Dependency overrides are appropriate when an endpoint needs a controlled external dependency; use them narrowly and restore application state after the test.

**Boundary.** A passing test only supports the named behavior under its named conditions. It is not proof of deployment safety, authorization, proxy limits, response-size controls, or production performance. Do not write a test that asserts private method calls when a public result or failure category expresses the required behavior.

**Checkpoint.** What should distinguish an invalid UTF-8 test from an empty-document test? Exact bytes: `b"\xff\xfe\xfa"` exercises decoding, while `b" \t\r\n"` decodes then exercises the whitespace policy.

With each box proven in isolation, the final architecture is a map of familiar responsibilities rather than a mystery diagram.

## 13. The complete request and failure traces

### Successful procurement note

```text
multipart request
  |
  | scalar form fields
  v
DocumentRequest (Pydantic runtime validation)
  |
  | UploadFile, bounded async read (1 MiB + 1)
  v
ExtractionCommand (trusted internal carrier)
  |
  v
DocumentExtractionService
  |-- checks suffix and both media-type signals
  |-- calls TextReader.decode(bytes)
  |-- normalizes newlines
  |-- rejects whitespace-only text
  v
ExtractedDocument
  |
  v
ExtractionResponse (Pydantic serialization) -> JSON 200
```

Dependency construction sits at the outer edge: `get_extraction_service()` creates `Utf8TextReader` and passes it to `DocumentExtractionService`. The service imports the protocol, domain values, and application errors—not FastAPI. The app includes a router and registers exception handlers. This direction keeps framework and wiring concerns at the edge.

### Invalid UTF-8 failure

```text
UploadFile bytes -> route bound check -> command -> service -> Utf8TextReader
                                                          |
                                                 UnicodeDecodeError
                                                          v
                                                 ReaderDecodingError
                                                          v
                                                 DocumentDecodingError
                                                          v
                                    application exception handler -> 422 JSON error
```

The client receives the documented document-decoding category and correlation ID, not a raw Python traceback or the byte content. The causal exception remains attached for controlled diagnosis. The service records a safe failure event with the stable failure code.

This is the design goal in miniature: one contract, explicit boundaries, and no hidden leap from framework object to business rule.

## 14. Mistakes that make this service less dependable

### Treating the filename as a server path

Never accept a caller-supplied path and read it with server permissions. Normalizing `../` cannot solve symlinks, race conditions, mounted volumes, or authorization. Upload bytes belong at this boundary; durable storage later should use opaque, authorized identifiers.

### Trusting one metadata signal

The suffix, declared media type, and upload media type are three distinct hints. Enforce all three policy rules, then decode strictly. A correct policy rejects a `.txt` labelled `application/pdf`, matching `application/pdf` values, and bytes that claim to be plain text but cannot decode as UTF-8.

### Hiding domain rules in the route

Putting format policy, newline handling, and decode logic in an endpoint makes HTTP tests the only way to understand core behavior. Keep route-owned transport work in the route and domain policy in the service.

### Using Pydantic everywhere

Pydantic is valuable at parsing and serialization boundaries. Making every internal function and carrier a `BaseModel` couples domain code to a boundary library and can obscure ownership. A frozen dataclass or function is often the more direct expression.

### Catching too broadly or logging too freely

Broad catches blur client mistakes, decoding failures, and infrastructure incidents. Logging raw text, filenames, or arbitrary exception messages creates a new sensitive-data store. Stable codes and allowlisted context are more useful operationally.

### Reaching for generators or async without a workload reason

A generator can complicate repeatability and resource cleanup. Async can make blocking work harder to observe. Start with a measured need: streaming/early termination for generators, overlapping wait for async, bounded threads for blocking I/O, or processes for CPU-heavy work.

## 15. Exercises: extend the contract without dissolving it

### Exercise 1: predict the result before running code

For each case, predict success or the stable failure family, then explain the earliest responsible layer.

| Filename | Declared type | Upload type | Bytes | Expected reasoning |
| --- | --- | --- | --- | --- |
| `note.TXT` | `text/plain` | `text/plain` | `b"a\rb"` | Suffix is case-insensitive; normalize on success. |
| `note.txt` | `application/pdf` | `application/pdf` | UTF-8 text | Matching unsupported metadata still fails. |
| `note.txt` | `text/plain` | `text/plain` | `b" \t\r\n"` | Decode succeeds; service rejects whitespace-only text. |
| `note.txt` | `text/plain` | `text/plain` | `b"\xff"` | Strict decoder failure. |
| `note.pdf` | `text/plain` | `text/plain` | UTF-8 text | Suffix policy failure. |

**Acceptance criteria:** name the layer and error family for each, distinguish metadata from bytes, and do not treat the exercise table as proof of an executed test.

### Exercise 2: make the size limit configuration explicit

Replace the hard-coded route constant with trusted immutable configuration assembled at the application edge.

**Acceptance criteria:** the default remains 1 MiB; the configured limit is positive; the route reads `limit + 1` bytes; exactly-at-limit non-whitespace input reaches service validation; above-limit input maps to 413; tests use multibyte UTF-8 to demonstrate that byte count and character count differ.

**Edge cases:** zero or negative configuration; one-byte limit; a two-byte UTF-8 character at the boundary; a document whose first `limit` bytes are whitespace but whose sentinel byte is non-whitespace.

**Hint:** a frozen settings dataclass is sufficient. Do not put mutable global configuration inside the service.

### Exercise 3: add Markdown text support without a plugin framework

Support `.md` only when both metadata values are `text/markdown`. Markdown remains strict UTF-8 text; do not render it and do not add dynamic discovery.

**Acceptance criteria:** existing `.txt` behavior and public service method remain unchanged; uppercase suffixes work; mismatched metadata fails; size, empty-content, decoding, and log-safety policies remain identical; parametrized tests explain each policy decision.

**Edge cases:** `.markdown` should not accidentally pass; matching `text/markdown` with a `.txt` name should fail; oversized Markdown should fail before decoding.

**Hint:** begin with an explicit small policy mapping or conditional. A registry is not justified by two formats.

### Exercise 4: protect the logging policy

Create success and failure tests with unique secret markers in both content and filename.

**Acceptance criteria:** neither marker appears in `caplog.text`; relevant records contain the correlation ID; a failure record exposes the stable `failure_code`; the test does not assume the formatter renders `extra` fields.

**Hint:** inspect `caplog.records` for record attributes and `caplog.text` for rendered leakage.

### Exercise 5: design a batch interface; do not implement it

Write a one-page design for several uploaded procurement documents. Choose sequential processing, async tasks, bounded threads, a process pool, or an external worker system.

**Acceptance criteria:** state per-document and total batch limits, ordering, partial success, cancellation, timeouts, retry safety, queue/worker bounds, backpressure, cleanup, and safe observability. Identify which operation actually waits or consumes CPU. Explain why rejected models fit less well.

**Hint:** sequential execution is a valid first answer if documents stay small and the service has no expensive parser.

## 16. Mini-project: an extraction review queue

The bounded project is to add an in-memory *review queue representation* after successful extraction. It does not persist a document, call an LLM, send a notification, or change holdings or any other financial state. Its purpose is to practise choosing a representation and preserving the existing API’s safety properties.

### Product question: what should a reviewer see next?

Procurement operations wants to triage successfully extracted notes. A reviewer needs a correlation ID, the normalized text, a small deterministic category, and an indication of whether human review is required. The category must not claim semantic understanding. It can be a transparent keyword rule such as “contains the literal word `delay`” rather than an AI recommendation.

Start with a value that can be passed around safely:

```python
import re
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class ReviewItem:
    correlation_id: str
    text: str
    category: str
    needs_human_review: bool


def classify_for_review(document: ExtractedDocument) -> ReviewItem:
    normalized = document.text.casefold()
    has_delay_signal = re.search(r"\bdelay\b", normalized) is not None
    return ReviewItem(
        correlation_id=document.correlation_id,
        text=document.text,
        category="delay-mentioned" if has_delay_signal else "no-delay-keyword",
        needs_human_review=has_delay_signal,
    )
```

This is a pure, deterministic classifier. Its output is explainable: it records the literal rule, not a probabilistic conclusion. `casefold()` is an explicit text-matching choice; it is not linguistic analysis. The rule should be treated as a workflow hint and reviewed for false positives and false negatives before any operational use.

**Boundary.** Do not put a mutable global `list[ReviewItem]` in the route module and call it a queue. It makes test order affect results, has no durability or concurrency semantics, and may retain sensitive document text indefinitely. The exercise asks for a representation and tests, not a production queue architecture.

**Checkpoint.** Should `ReviewItem` be a Pydantic model? Not merely because it has fields. A frozen dataclass is a good default for this trusted internal result. Use a Pydantic model only if it becomes an external parsing or serialization boundary.

### Build it in dependency order

1. Write tests for `classify_for_review` using fixed `ExtractedDocument` values. Test both categories and a case-insensitive match.
2. Add a unit test showing that a phrase like `"delayed"` does not match the literal `"delay"` rule, unless you intentionally broaden the rule and document the resulting behavior.
3. Decide where the new call belongs. It is downstream of successful extraction, so it must not change decoding or format failures. Keep it out of the upload route until its ownership is clear.
4. Add safe lifecycle logging that records the correlation ID and category, but never the text.
5. Design, but do not implement, persistence: define retention, authorization, tenant ownership, idempotency key, audit events, and deletion behavior before storing any procurement content.

**Definition of done:** existing extraction response behavior is unchanged; classification is deterministic and unit-tested; no logging adds document text or filename; false-positive/false-negative limitations are explicit; and no action is automated from the category. The mini-project is successful when another engineer can explain both what the rule does and what it deliberately does not infer.

## 17. Deeper practical checkpoints

### Pydantic errors are data for the framework, not public prose

The parsing dependency performs a small but important adaptation:

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

`exc.errors()` produces structured Pydantic error details that FastAPI understands as request validation. The dependency does not turn a validation error into a handcrafted string because the framework owns the transport representation for malformed input. The application’s own exception types are used once the request has crossed that scalar boundary and document-specific policy is being applied.

There are three related but different claims to keep straight:

- the request model can reject a correlation identifier with unsafe characters;
- the service can reject an unsupported filename/type combination; and
- the response model can validate the shape that the application intends to serialize.

None can attest to supplier identity, contract validity, or the factual content of a note. Validation is a gate on representation and local invariants, not a source of truth.

**Boundary.** `model_config = ConfigDict(..., frozen=True)` makes model fields resistant to ordinary assignment, but it is not a concurrency primitive, database constraint, authentication mechanism, or deep immutability guarantee. State the particular property a configuration option supplies.

**Checkpoint.** Why is `RequestValidationError` not raised by the domain service? It names an HTTP/framework request concern. The service should remain callable in a non-HTTP unit test.

### A model validator is not an excuse to collapse boundaries

Suppose a future external JSON API supplies *both* a declared type and a claimed checksum. A model validator could check a relation between those scalar fields:

```python
from typing import Self

class Metadata(BaseModel):
    declared_media_type: str
    checksum_algorithm: str

    @model_validator(mode="after")
    def allow_known_checksum_algorithm(self) -> Self:
        if self.checksum_algorithm not in {"sha256"}:
            raise ValueError("unsupported checksum algorithm")
        return self
```

This is a relationship within one parsed model. Computing a checksum of a file, imposing a maximum read, or comparing a digest to bytes is an I/O and content-processing concern. Keep the validation at the boundary where all of the needed trusted inputs are available; do not force large upload content through scalar validation merely for aesthetic uniformity.

### Generator cleanup is a lifetime design, not a syntax trick

An illustrative streaming line reader makes lifetime visible:

```python
from collections.abc import Iterator
from pathlib import Path

def read_lines(path: Path) -> Iterator[str]:
    with path.open(encoding="utf-8") as source:
        yield from source
```

The `with` block remains active while the iterator is being consumed. If a caller abandons it early, resource cleanup depends on generator finalization/closure timing; a caller that needs deterministic lifetime should own an explicit context manager around the resource and iteration. This is exactly why the present service reads a small bounded upload to bytes and decodes it completely: it has a simple request lifetime and returns complete text. Changing to streaming is an architectural change requiring an end-to-end limit and cleanup design, not a local `yield` substitution.

**Boundary.** `text.splitlines()` itself builds a list in this illustrative context. A generator wrapped around it changes output consumption but does not make the initial split streaming. Measure the whole pipeline before making memory claims.

**Checkpoint.** What resource does the repository’s current `Utf8TextReader` retain? None; it decodes the bytes already held by the request path.

### Timeouts, cancellation, and backpressure form one operational contract

Imagine the project later adds remote document enrichment. A timeout without cancellation/cleanup policy merely changes the error a caller sees; the underlying task may continue to consume a connection or worker. A reasonable design needs to say:

- which operation has a timeout and its budget;
- whether cancellation is safe at that operation’s await points;
- what finally closes files, releases semaphore permits, or returns connections;
- how many requests/tasks may run and queue simultaneously;
- what response or retry guidance applies when capacity is exhausted; and
- how correlation IDs connect timeout, cancellation, and completion logs without logging payloads.

For blocking libraries, do not assume cancellation kills a worker thread. The calling coroutine can stop waiting, but the underlying work may continue. For a process worker, cancellation may require a different protocol and has cost. These are reasons to start with the current bounded synchronous extraction path, not reasons to avoid concurrency forever.

**Boundary.** A semaphore only bounds code paths that actually acquire it. It does not protect a separate server process, proxy buffering, or an unbounded executor queue. Put limits at every relevant admission boundary.

**Checkpoint.** Which control stops a client from sending an enormous body before application code runs? Potentially a proxy/server configuration; the route’s sentinel read only bounds what this application read performs.

## 18. Interview practice: defend the trade-offs

### Foundation

**Why use a function for normalization but a class for extraction?**

Start from responsibility. Normalization is a deterministic transformation with no dependency or lifecycle. Extraction coordinates policy and an injected reader, so instance state and composition clarify ownership. Follow-up: a dataclass can contain methods; its use here is not forbidden, just less direct than a behavior-owning service.

**What do type hints protect?**

They document and statically check internal expectations; they do not generally validate HTTP values or prove byte encoding. The live controls are Pydantic scalar validation, bounded byte read, type/suffix policy, and strict decoding. Follow-up: Pydantic validates schema conformance, not whether a caller’s metadata is truthful.

### Applied design

**Why frozen dataclasses for command and result?**

They give value-like internal carriers and prevent accidental field rebinding while objects cross layers. This reduces aliasing surprises in shared pipeline state. Freezing is shallow, so nested mutable collections need immutable representations or deliberate copying. Mutable state remains appropriate when one owner controls its lifecycle.

**Why use a protocol rather than inherit from a reader base class?**

The service needs one capability: `decode(bytes) -> str`. A protocol keeps that contract structural and lets production adapters and test fakes remain small. Inheritance would only be useful if the base type offered meaningful shared behavior or lifecycle.

**Where should errors be translated?**

At a boundary that can add vocabulary. The codec adapter turns `UnicodeDecodeError` into reader failure; the service turns reader failure into a document failure; the app maps document failure to HTTP. Preserve `__cause__`; do not expose raw exception text to clients.

### Senior follow-ups

**Generators versus lists?**

Compare lazy single-pass production with eager repeatable materialization. Include memory, first-result latency, deferred errors, retry semantics, and resource lifetime. In this 1 MiB complete-read service, select a generator only for a demonstrated streaming/early-stop benefit.

**Threads versus async?**

Name the workload before the tool. Async overlaps awaitable waiting; it does not speed a blocking SDK or CPU parser. A bounded thread pool can isolate blocking I/O but complicates cancellation and queueing. Processes suit CPU-heavy work but add serialization and worker lifecycle. Mention timeouts and backpressure.

**What belongs in safe logs?**

Event name, safe correlation identifier, controlled media type, counts, and stable failure code. Exclude document contents, filenames, arbitrary metadata, and unreviewed third-party exception text. Explain that logging configuration belongs to the application entry point, not a library module.

## 19. Active recall and knowledge check

Try these without looking back. For each answer, name the boundary that owns the decision before naming a library feature. That habit prevents a technically true but incomplete answer such as “Pydantic validates it” when the actual issue is upload size, byte decoding, HTTP status mapping, or safe logging. A useful self-check is to ask four questions: what enters this component, what leaves it, what can fail, and what information must never escape it? If you can answer those for the route, service, reader, and response model, you understand the service as a composition of contracts rather than a memorized framework recipe.

1. Why is newline normalization a function rather than a service method?
2. Which values are validated by `DocumentRequest`, and which are obtained from `UploadFile`?
3. Why does the route read 1,048,577 bytes for a 1 MiB policy?
4. What exact risk remains after checking `text/plain` metadata?
5. What does `frozen=True` fail to protect in a dataclass containing `list[str]`?
6. Why does `raise NewError(...) from exc` matter?
7. What information can a test obtain from `caplog.records` that might not appear in `caplog.text`?
8. When does a generator body execute, and what happens after consumption?
9. Why can an `async def` still harm throughput?
10. Why should the service not accept `UploadFile` directly?
11. Which failure category should an upload larger than the limit produce at HTTP level?

### Answers

1. It has no state or dependency and its result depends only on input text.
2. Pydantic validates scalar `media_type` and `correlation_id`; FastAPI provides file name, upload content type, and bytes through `UploadFile`.
3. The extra sentinel byte distinguishes exactly-at-limit input from a longer upload with the same prefix.
4. Metadata can be false; bytes may still be invalid UTF-8 or otherwise not satisfy document policy.
5. The list remains mutable; frozen prevents rebinding the attribute, not mutation inside it.
6. It preserves the underlying causal exception while publishing a boundary-appropriate error.
7. Structured `extra` attributes such as correlation ID and failure code on individual log records.
8. On iteration, not generator creation; an exhausted generator does not replay values.
9. Blocking or CPU-heavy code run directly in it can block the event-loop thread.
10. `UploadFile` is an HTTP-framework transport object; accepting it couples the domain service to FastAPI.
11. `document_too_large`, mapped by the application to HTTP 413.

## Where this foundation leads

This service intentionally stops before authentication, authorization, persistence, OCR/PDF parsing, streaming, deployment, and parallel document processing. Those additions need their own trust boundaries, ownership model, operational limits, and tests. The transferable foundation is the method: start from a stable outcome, isolate a single responsibility, distinguish static intent from runtime enforcement, and reveal integration only after its components are understood.

The next roadmap topics can reuse this design discipline for model inputs, retrieval documents, evaluation records, and AI-assisted outputs. In each case, an LLM or parser output remains untrusted until deterministic validation accepts it; a recommendation remains separate from an action; and useful observability must not become a sensitive-data leak.

When the implementation changes, repeat the proof ladder rather than relying on the lesson narrative: test the smallest changed rule, the boundary that supplies its inputs, the error and logging behavior, then the end-to-end contract. That keeps a new feature from silently weakening a guarantee that downstream systems already depend on.

## Primary documentation

- [Python classes](https://docs.python.org/3.13/tutorial/classes.html), [type hints](https://docs.python.org/3.13/library/typing.html), [dataclasses](https://docs.python.org/3.13/library/dataclasses.html), [exception chaining](https://docs.python.org/3.13/tutorial/errors.html), [logging](https://docs.python.org/3.13/library/logging.html), [iterators](https://docs.python.org/3.13/tutorial/classes.html#iterators), and [asyncio tasks](https://docs.python.org/3.13/library/asyncio-task.html).
- [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/), [configuration](https://docs.pydantic.dev/latest/concepts/config/), [fields](https://docs.pydantic.dev/latest/concepts/fields/), [validators](https://docs.pydantic.dev/latest/concepts/validators/), and [serialization](https://docs.pydantic.dev/latest/concepts/serialization/).
- [FastAPI request files](https://fastapi.tiangolo.com/tutorial/request-files/), [forms and files](https://fastapi.tiangolo.com/tutorial/request-forms-and-files/), [dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/), [error handling](https://fastapi.tiangolo.com/tutorial/handling-errors/), [async guidance](https://fastapi.tiangolo.com/async/), and [testing](https://fastapi.tiangolo.com/tutorial/testing/).
- [pytest assertions](https://docs.pytest.org/en/stable/how-to/assert.html), [fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html), [parametrization](https://docs.pytest.org/en/stable/how-to/parametrize.html), and [logging capture](https://docs.pytest.org/en/stable/how-to/logging.html).
