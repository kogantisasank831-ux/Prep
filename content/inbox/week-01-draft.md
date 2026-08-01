---

week: 1
phase: 1
title: Python for production AI systems
status: draft
version: 0.1.0
last_reviewed: null
estimated_hours: null
prerequisites: ["Working knowledge of Python syntax", "Basic JSON knowledge"]
generated_with: ChatGPT Web
technical_review: pending
human_review: pending
---------------------

# Python for Production AI Systems

## Overview

Production AI systems fail at boundaries: malformed model output, unsupported documents, unavailable files, unexpected encodings, blocking libraries, poorly isolated dependencies, and logs that accidentally expose sensitive inputs.

This week builds the Python engineering foundation needed to handle those boundaries deliberately. The guided implementation is a small FastAPI service that:

* accepts a JSON request containing a document path, declared media type, and safe external correlation identifier;
* supports UTF-8 `.txt` documents only;
* uses Pydantic v2 models to validate untrusted HTTP data;
* keeps FastAPI routes thin;
* separates orchestration into a service layer;
* isolates filesystem access behind an injectable reader interface;
* returns typed, serializable results;
* distinguishes validation, unsupported-format, extraction, and infrastructure failures;
* emits operational logs without logging document contents or paths;
* includes deterministic unit and endpoint tests.

The implementation targets **Python 3.13.12** and installs packages with `pip`. Python 3.13.12 was released on February 3, 2026. The official release page now notes that it has been superseded by a later Python 3.13 maintenance release, but this module deliberately retains 3.13.12 as its target.

> **Verification required:** Confirm that Python 3.13.12 installers remain available for the learner’s operating system and confirm that the selected FastAPI, Pydantic, pytest, HTTPX, and Uvicorn releases support Python 3.13.12 before creating a locked dependency file.

The code, commands, tests, dependency combinations, and URLs in this module are instructional material. No claim is made that they were executed or verified in ChatGPT Web.

### Scope boundary

This week does not cover deployment, Docker, production servers, middleware architecture, authentication, databases, queues, cloud storage, OCR, PDF parsing, LLM calls, embeddings, RAG, agent frameworks, or production HTTP streaming. Those topics require additional operational and architectural decisions.

The Week 1 scope and acceptance criteria come from the approved outline. The document structure and generation constraints come from the supplied generation policy.

## Learning outcomes

By the end of Week 1, you should be able to:

1. Organize a small FastAPI service into cohesive modules with narrow public interfaces.
2. Explain instance state, class attributes, constructors, instance methods, class methods, static methods, composition, and inheritance.
3. Decide when a class represents useful state or lifecycle and when a module-level function is simpler.
4. Apply type hints that support static analysis without mistaking annotations for runtime validation.
5. Explain that Pydantic models are Python classes derived from `BaseModel`.
6. Use Pydantic v2 annotated fields, model configuration, field validators, model validators, serialization methods, and appropriate custom model methods.
7. Choose among plain classes, dataclasses, frozen dataclasses, and Pydantic models according to responsibility and boundary placement.
8. Validate untrusted document requests and produce typed, serializable results.
9. Design an exception hierarchy that distinguishes validation, unsupported-format, extraction, and infrastructure failures.
10. Translate low-level exceptions at the boundary where their implementation details become meaningful.
11. Use exception chaining to preserve causal information.
12. Emit useful lifecycle and failure logs without exposing document contents, filesystem paths, credentials, or sensitive metadata.
13. Explain iterable, iterator, and generator behavior, including lazy evaluation, single consumption, deferred failure, and resource lifetime.
14. Explain when asynchronous programming improves throughput and when blocking or CPU-bound work defeats it.
15. Write deterministic pytest tests for success, boundaries, logging behavior, and meaningful failure paths.
16. Test FastAPI endpoints with `TestClient` while replacing external dependencies.
17. Defend these design choices in a senior engineering interview.

## Prerequisites

### Required knowledge

* Working knowledge of Python syntax.
* Basic JSON knowledge.

You should already recognize functions, imports, exceptions, and basic class syntax. The module revisits classes explicitly from a production-design perspective rather than treating them as assumed knowledge.

### Required environment

Use Python 3.13.12 for the exercises.

Confirm the interpreter before installing dependencies:

```bash
python --version
```

The intended result is a version string identifying Python 3.13.12. This command has not been run or verified here.

Create an isolated virtual environment:

```bash
python -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Activate it in Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Python’s `venv` module creates an environment whose packages are isolated from the base interpreter by default. The official documentation also recommends treating virtual environments as disposable and recreatable rather than movable project artifacts.

Install the runtime dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install fastapi "pydantic>=2,<3" uvicorn
```

Install the test dependencies:

```bash
python -m pip install pytest httpx
```

Dependency purposes:

| Dependency | Scope           | Responsibility                                                                    |
| ---------- | --------------- | --------------------------------------------------------------------------------- |
| `fastapi`  | Runtime         | HTTP application, routing, dependency injection, request and response integration |
| `pydantic` | Runtime         | Runtime validation and serialization of untrusted boundary data                   |
| `uvicorn`  | Runtime tooling | Local ASGI server for manually running the application                            |
| `pytest`   | Test            | Test discovery, fixtures, parametrization, assertions, and log capture            |
| `httpx`    | Test            | HTTP client functionality used by FastAPI/Starlette testing tools                 |

> **Verification required:** These commands intentionally allow `pip` to resolve current compatible releases. Current releases can change. A reviewed project should resolve the environment once, run the tests, and record exact versions in a lock file or fully pinned requirements file. `pip install` behavior is documented by the Python Packaging Authority.

## Concept map

```text
Untrusted JSON
     |
     v
Pydantic request model
- shape validation
- field constraints
- cross-field validation
     |
     v
Thin FastAPI route
- HTTP concerns only
- dependency acquisition
- request -> domain conversion
     |
     v
Extraction service
- supported-format policy
- orchestration
- safe lifecycle logging
- low-level error translation
     |
     +-------------------------+
     |                         |
     v                         v
Reader Protocol          Pure domain functions
- narrow interface       - deterministic
- injectable             - no I/O
     |                    - easy unit tests
     v
UTF-8 text reader
- filesystem access
- context-managed resource
- decoding/error translation
     |
     v
Frozen domain result
     |
     v
Pydantic response model
- serialization
- HTTP response schema
```

The dependency direction is intentional:

```text
HTTP layer -> service/domain abstractions -> adapter interface
                                      adapter implementation -> filesystem
```

The deterministic core should not import FastAPI. The reader interface should not depend on a specific route. The route should not contain file-reading or text-normalization rules.

## Detailed lessons

### 1. Functions, classes, and modules as design tools

#### 1.1 The responsibility test

Before creating a class, ask:

1. Does this concept own state that persists across method calls?
2. Does it coordinate dependencies?
3. Does it enforce an invariant over an object’s lifetime?
4. Does it represent a substitutable capability?
5. Does construction establish meaningful configuration?

A class is justified when one or more answers are yes.

A module-level function is usually better when the operation:

* is stateless;
* depends only on its arguments;
* has no meaningful construction or lifecycle;
* does not need polymorphic replacement;
* becomes easier to test as a pure function.

For this week:

* `normalize_newlines(text)` is a module-level function because it is deterministic and stateless.
* `Utf8TextFileReader` is a class because it represents an adapter with a replaceable capability and may later own reader configuration.
* `DocumentExtractionService` is a class because it owns a reader dependency and coordinates an extraction lifecycle.
* `ExtractionCommand` and `ExtractedDocument` are dataclasses because they primarily carry internal domain data.
* HTTP request and response objects are Pydantic classes because they cross an untrusted serialization boundary.

#### 1.2 What a Python class creates

Defining a class creates a new type. Instances of that type may hold instance-specific attributes, while functions defined on the class become methods when accessed through an instance. Python’s class documentation describes classes as a way to bundle data and behavior and distinguishes instance-specific data from class-shared attributes.

```python
from typing import ClassVar


class TextReader:
    default_encoding: ClassVar[str] = "utf-8"

    def __init__(self, errors: str = "strict") -> None:
        self.errors = errors

    def describe(self) -> str:
        return f"encoding={self.default_encoding}, errors={self.errors}"
```

Here:

* `default_encoding` is a **class attribute** shared through the class.
* `errors` is **instance state** stored separately on each object.
* `__init__` is the constructor-initialization method invoked during normal instantiation.
* `describe` is an **instance method** and receives the current instance as `self`.

```python
strict_reader = TextReader()
replacement_reader = TextReader(errors="replace")
```

The two instances share the class-level default encoding but have different `errors` state.

#### 1.3 Avoid mutable class attributes for per-instance state

This is dangerous:

```python
class ExtractionTracker:
    completed_ids: list[str] = []

    def record(self, correlation_id: str) -> None:
        self.completed_ids.append(correlation_id)
```

Every instance can observe and mutate the same list.

Prefer:

```python
class ExtractionTracker:
    def __init__(self) -> None:
        self.completed_ids: list[str] = []

    def record(self, correlation_id: str) -> None:
        self.completed_ids.append(correlation_id)
```

Python’s class documentation explicitly warns that mutable class variables may be unexpectedly shared by all instances.

#### 1.4 Instance, class, and static methods

##### Instance methods

An instance method operates on instance state or dependencies.

```python
class ExtractionService:
    def __init__(self, reader: "Reader") -> None:
        self._reader = reader

    def extract(self, path: str) -> str:
        return self._reader.read(path)
```

##### Class methods

A class method receives the class as `cls`. Appropriate uses include:

* alternate constructors;
* operations that depend on overridable class policy;
* constructing the current subclass instead of hard-coding a concrete class.

```python
from typing import Self


class CorrelationId:
    def __init__(self, value: str) -> None:
        self.value = value

    @classmethod
    def from_header(cls, raw_header: str) -> Self:
        cleaned = raw_header.strip()
        return cls(cleaned)
```

A class method should not be introduced merely to avoid writing a normal function.

##### Static methods

A static method receives neither `self` nor `cls`.

```python
class MediaTypeRules:
    @staticmethod
    def is_text(media_type: str) -> bool:
        return media_type.startswith("text/")
```

This is legal, but a module-level function may communicate the design more directly:

```python
def is_text_media_type(media_type: str) -> bool:
    return media_type.startswith("text/")
```

Use a static method when the operation is strongly part of a class’s public conceptual API. Do not use one merely as a namespace.

#### 1.5 Composition

Composition means one object performs its responsibility using another object.

```python
class DocumentExtractionService:
    def __init__(self, reader: "TextReader") -> None:
        self._reader = reader
```

The service **has a reader**. It is not a specialized kind of reader.

Composition is appropriate because:

* orchestration and filesystem access are separate responsibilities;
* tests can inject a fake reader;
* future adapters can implement the same narrow interface;
* the service does not inherit irrelevant reader implementation details.

#### 1.6 Inheritance

Inheritance expresses an “is-a” relationship and allows a derived class to reuse or override behavior from a base class. Python resolves missing attributes through base classes and permits derived classes to override methods.

Good uses in this module include:

* Pydantic request models inheriting from `BaseModel`;
* domain exception subclasses inheriting from a common service error;
* specialized exceptions inheriting from broader failure categories.

```python
class DocumentServiceError(Exception):
    pass


class UnsupportedDocumentFormatError(DocumentServiceError):
    pass
```

Avoid inheritance for sharing a few utility methods. In service design, deep inheritance hierarchies often create hidden coupling, fragile override behavior, and difficult construction requirements.

#### 1.7 Modules and public interfaces

A module should group cohesive responsibilities. A narrow public interface makes it easier to change implementation details.

Example responsibility split:

```text
models.py       HTTP validation and serialization models
domain.py       internal commands, results, and pure transformations
ports.py        reader protocol
readers.py      filesystem implementation
errors.py       failure taxonomy
service.py      orchestration
api.py          FastAPI router
main.py         application assembly and error mappings
```

Avoid circular dependency patterns such as:

```text
service imports api
api imports service
```

Prefer:

```text
api imports service
service imports domain and ports
reader imports ports/errors
```

**Knowledge check:** Why is `normalize_newlines` a function while `DocumentExtractionService` is a class?

---

### 2. Type hints: static information, not runtime enforcement

Type hints describe intended types to readers, editors, and static analyzers. Python does not generally enforce ordinary function annotations when a function is called. The `typing` documentation and PEP 484 define annotations as support for static analysis rather than automatic runtime validation.

#### 2.1 Misleading confidence

```python
def character_count(text: str) -> int:
    return len(text)
```

The annotation communicates that callers should provide a `str`. It does not prevent this call at runtime:

```python
result = character_count(["not", "a", "string"])
```

`len` also accepts a list, so this call may return `3` instead of failing. The annotation has not made the runtime boundary safe.

At an untrusted boundary, validate before constructing trusted domain values:

```python
from pydantic import BaseModel, ConfigDict


class CountRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    text: str
```

Now Pydantic performs runtime validation during model construction.

#### 2.2 Useful function signatures

```python
from pathlib import Path


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def count_nonempty_lines(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip())


def select_existing_path(
    preferred: Path | None,
    fallback: Path,
) -> Path:
    if preferred is not None:
        return preferred
    return fallback
```

The explicit `None` check narrows `preferred` from `Path | None` to `Path`.

Avoid returning a broad type when a narrower type is available:

```python
# Too vague
def extract(path: Path) -> object:
    ...
```

Prefer:

```python
def extract(path: Path) -> "ExtractedDocument":
    ...
```

#### 2.3 Typed collections

Use concrete element types:

```python
paths: list[Path]
errors_by_id: dict[str, str]
supported_types: set[str]
```

This is more informative than:

```python
paths: list
errors_by_id: dict
```

#### 2.4 Protocols

A protocol describes the behavior a dependency must provide without requiring inheritance from a shared base implementation.

```python
from pathlib import Path
from typing import Protocol


class TextReader(Protocol):
    def read_text(self, path: Path) -> str:
        ...
```

Any object with a compatible `read_text` method can satisfy this interface for static checking purposes. Protocol-based structural subtyping is specified by PEP 544 and documented in Python’s typing facilities.

This keeps tests simple:

```python
class FixedReader:
    def read_text(self, path: Path) -> str:
        return "fixed content"
```

`FixedReader` does not need to inherit from `TextReader`.

#### 2.5 Containing untyped boundaries

Third-party libraries or decoded JSON may produce values whose precise type is not yet trusted. Contain that uncertainty at the boundary and convert it quickly.

Do not spread weak typing through the service:

```python
# Avoid allowing an unvalidated dictionary to flow everywhere.
def extract(payload: dict) -> dict:
    ...
```

Prefer:

```python
def extract(command: "ExtractionCommand") -> "ExtractedDocument":
    ...
```

**Knowledge check:** What guarantee does `path: Path` provide at runtime when an arbitrary caller invokes the function?

---

### 3. Plain classes, dataclasses, frozen dataclasses, and Pydantic models

These tools overlap syntactically but serve different responsibilities.

| Construct                     | Primary responsibility                                  | Validation                             | Mutation                    | Typical placement                                         |
| ----------------------------- | ------------------------------------------------------- | -------------------------------------- | --------------------------- | --------------------------------------------------------- |
| Plain class                   | Behavior, lifecycle, dependencies, state transitions    | Manually implemented                   | Developer-controlled        | Services, adapters, stateful collaborators                |
| Dataclass                     | Internal data representation with generated boilerplate | No automatic trust-boundary validation | Mutable by default          | Commands, internal records, configuration values          |
| Frozen dataclass              | Internal value-like representation                      | No automatic trust-boundary validation | Attribute rebinding blocked | Domain results, immutable commands, policy values         |
| Pydantic `BaseModel` subclass | Parsing, validation, serialization, schema generation   | Runtime validation                     | Configurable                | HTTP, message, file-metadata, and model-output boundaries |

#### 3.1 Dataclasses

A standard-library dataclass can generate initialization, representation, and comparison behavior from annotated fields. PEP 557 and the Python documentation describe dataclasses as normal Python classes whose generated methods are based on declared fields.

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class ExtractionCommand:
    path: Path
    media_type: str
    correlation_id: str
```

A dataclass does not automatically reject this:

```python
command = ExtractionCommand(
    path="not-a-Path",  # Runtime construction is still possible.
    media_type=42,      # Runtime construction is still possible.
    correlation_id=[],
)
```

Static analysis may report problems, but runtime validation is a separate responsibility.

#### 3.2 Frozen dataclasses

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExtractedDocument:
    correlation_id: str
    text: str
    tags: list[str]
```

This prevents attribute rebinding:

```python
document.text = "replacement"
```

It does not recursively freeze nested mutable values:

```python
document.tags.append("still mutable")
```

This is **shallow immutability**. The frozen object cannot be rebound through normal attribute assignment, but referenced mutable objects can still change.

For stronger value semantics, prefer immutable nested types:

```python
@dataclass(frozen=True, slots=True)
class SaferExtractedDocument:
    correlation_id: str
    text: str
    tags: tuple[str, ...]
```

Aliasing matters in AI pipelines because several components may hold references to the same mutable prompt fragments, retrieved-document lists, metadata dictionaries, or intermediate model state. A mutation in one component can change what another component observes.

#### 3.3 Pydantic models are Python classes

A Pydantic model is a Python class that inherits from `pydantic.BaseModel`. Fields are normally declared as annotated class attributes. Pydantic analyzes the model class and uses the resulting schema for validation and serialization.

```python
from pydantic import BaseModel, ConfigDict, Field


class DocumentRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    path: str = Field(min_length=1, max_length=1024)
    media_type: str = Field(min_length=1, max_length=128)
    correlation_id: str = Field(min_length=1, max_length=64)
```

This is inheritance:

```text
DocumentRequest -> BaseModel -> Python object
```

It is not evidence that all stateless logic should be put inside classes. Pydantic uses a class because a model class declares fields, validators, configuration, schema, serialization behavior, and construction rules.

#### 3.4 Annotated fields

```python
from pydantic import Field


class UploadMetadata(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    declared_size_bytes: int = Field(ge=0, le=10_000_000)
```

Annotations communicate the target types. `Field` adds constraints and metadata.

#### 3.5 Model configuration

Pydantic v2 commonly uses `ConfigDict` through the `model_config` class attribute.

```python
from pydantic import BaseModel, ConfigDict


class StrictBoundaryModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        frozen=True,
    )
```

Responsibilities:

* `extra="forbid"` rejects undeclared fields.
* `strict=True` reduces coercion for supported types.
* `frozen=True` blocks normal attribute assignment to the constructed model.

Pydantic’s defaults and exact strictness behavior are version-sensitive. The official model documentation notes that Pydantic commonly performs conversion unless strict behavior is selected and that extra fields are ignored by default unless configuration changes that behavior.

> **Verification required:** Confirm coercion and strictness for every field type against the installed Pydantic v2 release. Do not infer all strict-mode behavior from one example.

#### 3.6 Field validators

A field validator handles rules associated primarily with one field.

```python
import re

from pydantic import BaseModel, field_validator


_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class CorrelatedRequest(BaseModel):
    correlation_id: str

    @field_validator("correlation_id")
    @classmethod
    def validate_correlation_id(cls, value: str) -> str:
        if _SAFE_ID.fullmatch(value) is None:
            raise ValueError("correlation_id contains unsupported characters")
        return value
```

A validator should return the validated value or raise an appropriate validation exception. Pydantic v2 supports decorator-based and annotated validator patterns.

Avoid validators that:

* perform network calls;
* read files;
* mutate global state;
* produce nondeterministic results;
* silently alter security-sensitive identifiers;
* contain orchestration that belongs in a service.

#### 3.7 Model validators

A model validator can evaluate relationships involving several fields or the model as a whole.

```python
from pathlib import Path
from typing import Self

from pydantic import BaseModel, model_validator


class FileDeclaration(BaseModel):
    path: str
    media_type: str

    @model_validator(mode="after")
    def require_extension(self) -> Self:
        if Path(self.path).suffix == "":
            raise ValueError("path must include a file extension")
        return self
```

The model validator checks a property that depends on the complete model state.

Do not place file existence checks here. File existence is I/O, can change between validation and use, and belongs at the filesystem adapter boundary.

#### 3.8 Serialization

Pydantic v2 models expose methods such as:

* `model_dump()` for a Python dictionary;
* `model_dump_json()` for JSON text;
* `model_validate()` for validating Python data;
* `model_validate_json()` for validating JSON text;
* `model_json_schema()` for JSON Schema generation.

These are model responsibilities provided by `BaseModel`.

```python
request = DocumentRequest(
    path="notes.txt",
    media_type="text/plain",
    correlation_id="job-123",
)

payload = request.model_dump()
```

#### 3.9 Appropriate custom model methods

A model method should remain closely related to conversion or presentation of that model.

```python
from typing import Self


class ExtractionResponse(BaseModel):
    correlation_id: str
    text: str
    character_count: int

    @classmethod
    def from_domain(cls, result: "ExtractedDocument") -> Self:
        return cls(
            correlation_id=result.correlation_id,
            text=result.text,
            character_count=result.character_count,
        )
```

This is an appropriate alternate constructor. Reading a file or calling an LLM from `from_domain` would not be appropriate.

**Knowledge check:** Why should untrusted HTTP JSON normally become a Pydantic model before it becomes a frozen domain dataclass?

---

### 4. Exception design and translation

#### 4.1 Exceptions are part of the interface

A caller needs to know what categories of failure it can handle.

This week uses these service-level categories:

```text
DocumentServiceError
├── DocumentValidationError
├── UnsupportedDocumentFormatError
├── DocumentExtractionError
│   ├── DocumentDecodingError
│   └── EmptyDocumentError
└── DocumentInfrastructureError
    └── DocumentNotFoundError
```

The HTTP layer can map these categories without understanding filesystem implementation details.

#### 4.2 Translate at abstraction boundaries

A filesystem adapter understands `FileNotFoundError`, `UnicodeDecodeError`, and `OSError`.

The extraction service understands “document not found,” “document cannot be decoded,” and “reader infrastructure failed.”

The API understands HTTP status codes and stable response bodies.

Translate when crossing those boundaries:

```python
try:
    raw_text = reader.read_text(path)
except ReaderDecodingError as exc:
    raise DocumentDecodingError(
        "document is not valid UTF-8",
        correlation_id=correlation_id,
    ) from exc
```

The higher-level exception exposes language meaningful to the service while `from exc` preserves the original cause.

Python supports explicit exception chaining with `raise NewException(...) from original_exception`.

#### 4.3 Preserve useful context without leaking payloads

Unsafe:

```python
raise DocumentExtractionError(
    f"Could not extract {path}: {raw_document_text}"
)
```

Safer:

```python
raise DocumentExtractionError(
    "document extraction failed",
    correlation_id=correlation_id,
)
```

Internal traces may preserve the original exception through chaining. Public messages should remain stable and non-sensitive.

#### 4.4 Avoid broad suppression

Dangerous:

```python
try:
    return reader.read_text(path)
except Exception:
    return ""
```

This converts every defect into an apparently valid empty document. It hides programming errors, infrastructure failures, cancellations, and unsupported behavior.

Better:

* catch specific exceptions you can translate;
* log at the appropriate layer;
* re-raise or translate with causal context;
* allow unknown programming errors to remain visible.

#### 4.5 Use context managers for cleanup

```python
with path.open("r", encoding="utf-8", errors="strict") as stream:
    return stream.read()
```

The context manager closes the file when the block exits, including exceptional exits. Do not rely on garbage collection timing for resource cleanup.

**Knowledge check:** Why should a route not catch `OSError` directly?

---

### 5. Operational logging

#### 5.1 Module-level logger

```python
import logging

logger = logging.getLogger(__name__)
```

Each module emits through its own named logger. Application startup code or the process runner decides formatting, destinations, and severity thresholds. A reusable module should not call `logging.basicConfig()` or reconfigure the root logger.

Python’s logging documentation recommends module-level loggers based on `__name__` and describes severity levels for progressively more serious events.

#### 5.2 Useful events

For extraction, useful fields include:

* event name;
* correlation identifier;
* declared media type;
* stable failure code;
* character count;
* line count;
* elapsed time, when measured by an injected or carefully isolated clock;
* exception trace for unexpected internal failures.

Do not log:

* document text;
* prompts or model responses containing sensitive data;
* arbitrary metadata dictionaries;
* credentials;
* personal information;
* complete filesystem paths;
* raw exception messages from untrusted or low-level sources without review.

#### 5.3 Structured context

Standard logging supports extra record attributes:

```python
logger.info(
    "document_extraction_started",
    extra={
        "correlation_id": correlation_id,
        "media_type": media_type,
    },
)
```

Whether those fields appear as JSON depends on application logging configuration. The library code should emit structured fields without deciding the global formatter.

#### 5.4 Levels

A practical policy:

| Level      | Use                                                                 |
| ---------- | ------------------------------------------------------------------- |
| `DEBUG`    | Internal diagnostic details safe for restricted logs                |
| `INFO`     | Normal lifecycle milestones                                         |
| `WARNING`  | Expected request-specific failure that needs operational visibility |
| `ERROR`    | Serious failure that prevented an operation                         |
| `CRITICAL` | Process-wide or service-wide failure requiring immediate attention  |

Unsupported input may be a warning rather than an error because the application handled it correctly.

#### 5.5 Logging exceptions

Use `logger.exception` inside an active exception handler when a traceback is valuable:

```python
try:
    perform_operation()
except UnexpectedInfrastructureFailure:
    logger.exception(
        "unexpected_infrastructure_failure",
        extra={"correlation_id": correlation_id},
    )
    raise
```

Do not include the document text in the event message or `extra`.

**Knowledge check:** Why is a correlation ID safer and more useful than logging a complete input path?

---

### 6. Iterables, iterators, and generators

#### 6.1 Mental model

An **iterable** can produce an iterator.

An **iterator** produces values one at a time and tracks traversal state.

A **generator** is a convenient way to implement an iterator using `yield`.

```python
values = ["a", "b", "c"]  # Iterable
iterator = iter(values)   # Iterator
first = next(iterator)
```

Python’s class tutorial covers iterator protocol methods and generators as concise iterator-producing functions.

#### 6.2 Lazy logical-line generator

```python
from collections.abc import Iterator
from pathlib import Path


def iter_logical_lines(path: Path) -> Iterator[str]:
    with path.open(
        "r",
        encoding="utf-8",
        errors="strict",
        newline="",
    ) as stream:
        for line in stream:
            yield line.rstrip("\r\n")
```

The file is not fully read when the generator object is created. Work happens as values are requested.

#### 6.3 Single consumption

```python
lines = iter_logical_lines(path)

first_pass = list(lines)
second_pass = list(lines)
```

After the first pass exhausts the generator, `second_pass` is empty.

A list is repeatable because it stores all produced elements:

```python
lines = list(iter_logical_lines(path))
first_pass = list(lines)
second_pass = list(lines)
```

The trade-off is memory.

#### 6.4 Memory and latency

Generators may:

* reduce peak memory;
* allow the first result to appear before all results are produced;
* avoid work when iteration stops early.

They may also:

* defer errors until iteration;
* hold resources open;
* complicate retries;
* prevent repeated traversal;
* move failure timing away from the function call.

#### 6.5 Deferred failures

```python
line_iterator = iter_logical_lines(path)
```

This may not open the file yet. A missing-file or decoding error can occur later during `next(line_iterator)`.

Callers must understand where failures can occur.

#### 6.6 Resource lifetime

The generator’s `with` block remains active while iteration is suspended between yielded values. If a caller stops early, the file may remain open until the generator is closed or finalized.

```python
generator = iter_logical_lines(path)

try:
    first_line = next(generator)
finally:
    generator.close()
```

For simple small-document extraction, eagerly reading a bounded file may produce a clearer lifecycle. The independent size-limit exercise makes that assumption explicit.

This week does not implement HTTP streaming.

**Knowledge check:** Why can returning a generator move an exception from function invocation to a later point in the caller?

---

### 7. Async fundamentals

#### 7.1 Cooperative concurrency

`asyncio` runs coroutines cooperatively. A task gives the event loop an opportunity to run other tasks when it reaches an awaitable operation that suspends.

Python describes `asyncio` as a library for concurrent code using `async` and `await`.

Async is useful when:

* many operations spend time waiting;
* the libraries provide non-blocking awaitable APIs;
* concurrency is bounded;
* cancellation and timeouts are handled deliberately.

Async does not make arbitrary Python work faster.

#### 7.2 Awaitable I/O

```python
from typing import Protocol


class AsyncMetadataClient(Protocol):
    async def fetch_label(self, document_id: str) -> str:
        ...


async def load_label(
    client: AsyncMetadataClient,
    document_id: str,
) -> str:
    return await client.fetch_label(document_id)
```

The benefit depends on `fetch_label` actually releasing control while waiting.

#### 7.3 Blocking work inside an async function

Bad:

```python
from pathlib import Path


async def read_document_bad(path: Path) -> str:
    return path.read_text(encoding="utf-8")
```

The function is syntactically asynchronous, but the filesystem call is synchronous. While it runs, it can block the event-loop thread.

A bridge for blocking I/O is:

```python
import asyncio
from pathlib import Path


async def read_document_via_thread(path: Path) -> str:
    return await asyncio.to_thread(
        path.read_text,
        encoding="utf-8",
        errors="strict",
    )
```

This moves the blocking call to a worker thread. It adds scheduling, cancellation, debugging, and capacity-management considerations.

For the guided FastAPI endpoint, use a normal synchronous `def` route because its reader is synchronous and blocking. FastAPI’s concurrency guidance recommends normal `def` path operations for blocking libraries that do not expose awaitable APIs.

> **Verification required:** Confirm the installed FastAPI/Starlette behavior for synchronous path functions and dependency execution. This is framework-version-sensitive operational behavior.

#### 7.4 CPU-bound work

CPU-heavy parsing, image processing, or pure-Python numerical work does not become faster merely because it runs in coroutines. Parallel CPU execution may require processes, native libraries that release the GIL, or an external worker architecture.

Python’s `concurrent.futures` documentation distinguishes thread and process executors as mechanisms for asynchronous task execution.

#### 7.5 Cancellation and cleanup

A coroutine may be cancelled while awaiting.

```python
async def use_resource(resource: "AsyncResource") -> None:
    await resource.open()
    try:
        await resource.process()
    finally:
        await resource.close()
```

Cleanup belongs in `finally` or an asynchronous context manager.

Do not swallow cancellation through broad exception handling.

#### 7.6 Timeouts

A timeout is part of the operation’s contract, not merely a performance tweak. After a timeout:

* determine whether the underlying operation is actually cancelled;
* release resources;
* decide whether retry is safe;
* retain a stable failure category;
* avoid duplicate side effects.

#### 7.7 Threads versus async

| Concern               | Async                            | Threads                                   |
| --------------------- | -------------------------------- | ----------------------------------------- |
| Best fit              | Awaitable I/O                    | Blocking libraries or I/O                 |
| Scheduling            | Cooperative                      | Operating-system/runtime-managed          |
| Shared state          | Same process and event loop      | Same process, concurrent access           |
| Cancellation          | Structured but library-dependent | Often cannot forcibly stop running call   |
| Backpressure          | Must be designed                 | Must bound worker and queue capacity      |
| Debugging             | Task and event-loop context      | Thread stacks and race conditions         |
| CPU-bound pure Python | Generally not accelerated        | Generally not a reliable parallel speedup |
| Integration           | Requires async-compatible stack  | Works around synchronous libraries        |

**Knowledge check:** Why is changing `def` to `async def` not an optimization by itself?

---

### 8. Reusable and testable design

#### 8.1 Separate deterministic logic from adapters

Pure function:

```python
def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")
```

Adapter:

```python
class Utf8TextFileReader:
    def read_text(self, path: Path) -> str:
        ...
```

The pure function can be tested with strings. The adapter needs filesystem tests.

#### 8.2 Inject external boundaries

```python
class DocumentExtractionService:
    def __init__(self, reader: TextReader) -> None:
        self._reader = reader
```

The service does not construct a reader inside `extract`. Tests can inject deterministic behavior.

Avoid:

```python
class DocumentExtractionService:
    def extract(self, path: Path) -> str:
        reader = Utf8TextFileReader()
        return reader.read_text(path)
```

This hard-codes the dependency and makes failure simulation less direct.

#### 8.3 Keep interfaces small

This week’s reader needs one operation:

```python
class TextReader(Protocol):
    def read_text(self, path: Path) -> str:
        ...
```

Do not create a generic plugin framework with registration, discovery, priorities, lifecycle hooks, or configuration schemas before there is a demonstrated need.

#### 8.4 Test observable behavior

Prefer:

```python
assert result.text == "expected"
```

Avoid testing private implementation steps:

```python
mock_reader.read_text.assert_called_once_with(path)
```

Call assertions are appropriate when interaction itself is the behavior, but they should not replace result and failure assertions.

---

### 9. Pytest fundamentals

#### 9.1 Arrange–act–assert

```python
def test_normalize_newlines() -> None:
    # Arrange
    source = "a\r\nb\rc"

    # Act
    result = normalize_newlines(source)

    # Assert
    assert result == "a\nb\nc"
```

#### 9.2 `tmp_path`

pytest’s `tmp_path` fixture supplies a unique `pathlib.Path` directory for each test function.

```python
from pathlib import Path


def test_reader_reads_utf8(tmp_path: Path) -> None:
    path = tmp_path / "document.txt"
    path.write_text("नमस्ते", encoding="utf-8")

    reader = Utf8TextFileReader()
    result = reader.read_text(path)

    assert result == "नमस्ते"
```

#### 9.3 Exception assertions

```python
import pytest


def test_empty_document_is_rejected() -> None:
    with pytest.raises(EmptyDocumentError):
        ...
```

Use the narrowest expected exception. Verify stable attributes when useful.

#### 9.4 Parametrization

```python
import pytest


@pytest.mark.parametrize(
    ("media_type", "is_supported"),
    [
        ("text/plain", True),
        ("application/pdf", False),
        ("text/markdown", False),
    ],
)
def test_media_type_policy(
    media_type: str,
    is_supported: bool,
) -> None:
    assert is_supported_media_type(media_type) is is_supported
```

pytest’s `@pytest.mark.parametrize` runs a test against multiple argument sets.

#### 9.5 Captured logs

```python
import logging


def test_document_text_is_not_logged(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.INFO):
        ...
```

pytest provides `caplog` for capturing and inspecting log records.

#### 9.6 Mock only external boundaries

Good candidates:

* filesystem reader;
* HTTP client;
* database repository;
* clock;
* model client.

Usually do not mock:

* newline normalization;
* simple dataclass construction;
* basic Pydantic serialization;
* small domain rules.

---

### 10. FastAPI boundary fundamentals

A FastAPI route should handle HTTP concerns:

* receive a validated request model;
* obtain the service dependency;
* convert request data into a domain command;
* invoke the service;
* convert the result into a response model.

It should not:

* open files;
* decode bytes;
* normalize text;
* select parser implementations;
* log document contents;
* define business rules inline.

FastAPI integrates Pydantic request models with request-body parsing and supports response models for serialization and API schema generation.

FastAPI also supports dependency injection and dependency replacement during tests.

Thin route:

```python
@router.post("/extract", response_model=ExtractionResponse)
def extract_document(
    request: DocumentRequest,
    service: Annotated[
        DocumentExtractionService,
        Depends(get_extraction_service),
    ],
) -> ExtractionResponse:
    command = ExtractionCommand(
        path=Path(request.path),
        media_type=request.media_type,
        correlation_id=request.correlation_id,
    )
    result = service.extract(command)
    return ExtractionResponse.from_domain(result)
```

FastAPI’s `APIRouter` supports organizing path operations across modules, while `TestClient` supports endpoint tests with pytest.

## Production considerations

### Trust boundaries

The request body is untrusted. Pydantic validates its declared shape, but successful schema validation does not prove that:

* the file exists;
* the file is authorized for this caller;
* the file remains unchanged;
* the bytes are valid UTF-8;
* the file is reasonably sized;
* the extension accurately represents the content.

Each guarantee belongs at a different boundary.

### Arbitrary filesystem paths

This learning service accepts a path to keep the reader boundary visible. A production public API should generally avoid accepting unrestricted server filesystem paths.

Safer production designs often use:

* opaque document identifiers;
* a storage root with canonical-path enforcement;
* pre-authorized storage handles;
* tenant-aware repositories;
* uploaded content stored outside the web process.

Authentication and tenant isolation are out of scope for Week 1.

### Time-of-check/time-of-use behavior

Checking `path.exists()` before opening a file does not guarantee that the file will still exist when opened. Prefer attempting the operation and translating the resulting exception.

### File-size limits

The initial build reads the full file into memory and does not enforce a maximum size. This is acceptable only as an explicit learning constraint. Exercise 2 adds a configurable reader-boundary limit.

### Encoding

The reader uses:

```python
encoding="utf-8"
errors="strict"
```

Do not use `errors="ignore"` at a trust boundary. It can silently discard undecodable bytes and change document meaning.

### Normalization

The service normalizes newline representations:

* `\r\n` becomes `\n`;
* remaining `\r` becomes `\n`.

It does not:

* trim leading or trailing whitespace;
* collapse repeated spaces;
* lowercase text;
* remove punctuation;
* remove a byte-order mark;
* apply Unicode normalization.

Any additional transformation should be separately named, documented, and tested.

### Error stability

Expose stable error codes such as:

* `unsupported_document_format`;
* `document_not_found`;
* `document_decoding_failed`;
* `empty_document`;
* `document_infrastructure_failure`.

Do not make clients parse raw exception messages.

### Sensitive logging

Treat all document text as potentially sensitive. Also avoid logging:

* complete paths;
* filenames that may contain identities;
* arbitrary request objects;
* stack traces containing payload values;
* validator inputs;
* model outputs.

Use the externally safe correlation ID to connect related events.

### Dependency management

The unpinned installation commands are for initial learning setup. A reviewed project should:

1. resolve compatible versions;
2. run the test suite;
3. inspect dependency release notes;
4. record exact versions;
5. define a deliberate update process.

### Synchronous versus asynchronous route

The guided route is synchronous because its reader uses a blocking filesystem API. Converting the route to `async def` without changing the dependency stack would not make the reader non-blocking.

### Import boundaries

Recommended dependency direction:

```text
main/api -> models/service
service -> domain/ports/errors
readers -> ports/errors
domain -> standard library only
```

Avoid importing FastAPI in `domain.py`, `ports.py`, or `service.py`.

### No speculative parser framework

The service supports one document type. Exercise 1 should add Markdown text support with the smallest design change that preserves the service’s public behavior. It should not introduce dynamic plugin discovery.

## Common failure modes

### 1. Treating type annotations as validation

```python
def extract(path: str) -> str:
    ...
```

This does not ensure an arbitrary runtime value is a string.

**Correction:** Validate untrusted data with a boundary model.

### 2. Reading files inside the route

This couples HTTP behavior, I/O, decoding, business rules, and error translation.

**Correction:** Route to a service that uses an injected reader.

### 3. Returning raw dictionaries everywhere

Raw dictionaries weaken interfaces and allow keys and value types to drift.

**Correction:** Use Pydantic models at serialized boundaries and dataclasses for internal values.

### 4. Using Pydantic models for every internal object

This adds validation and serialization responsibilities where plain domain values may be clearer.

**Correction:** Use Pydantic where data enters or leaves a trust boundary.

### 5. Using dataclasses to validate untrusted JSON

Dataclasses do not automatically validate runtime input types.

**Correction:** Construct a Pydantic boundary model first, then convert to a domain dataclass.

### 6. Assuming `frozen=True` recursively freezes data

Nested lists and dictionaries remain mutable.

**Correction:** Use immutable nested types or defensive copies where shared state matters.

### 7. Shared mutable class attributes

A list declared at class scope may be shared by every instance.

**Correction:** Create per-instance mutable state in `__init__`.

### 8. Unnecessary service inheritance

Subclassing a reader to create a service confuses “uses” with “is.”

**Correction:** Compose the service with a reader.

### 9. Catching `Exception` and returning an empty result

This hides defects and converts failures into valid-looking data.

**Correction:** Catch specific expected exceptions and preserve unexpected failures.

### 10. Losing the original exception

```python
except OSError:
    raise DocumentInfrastructureError("reader failed")
```

This discards causal context.

**Correction:**

```python
except OSError as exc:
    raise DocumentInfrastructureError("reader failed") from exc
```

### 11. Leaking paths or content through logs

```python
logger.error("failed path=%s text=%s", path, text)
```

**Correction:** Log correlation ID and stable failure category.

### 12. Logging and suppressing

```python
except ReaderError:
    logger.exception("reader failed")
```

Without `raise`, execution may continue with invalid state.

### 13. Returning a generator without documenting lifecycle

The caller may assume immediate validation or repeatability.

**Correction:** Document laziness, single consumption, resource ownership, and deferred exceptions.

### 14. Declaring a blocking route `async def`

The event loop can still be blocked by synchronous work.

**Correction:** Use a synchronous route or explicitly bridge a blocking dependency with bounded threads.

### 15. Mocking the entire service under test

A test that mocks all meaningful behavior proves only that mocks were configured.

**Correction:** Use fakes at external boundaries and execute real domain/service logic.

### 16. Asserting entire third-party error bodies

Framework validation payloads can evolve.

**Correction:** Assert stable status codes and essential fields unless the complete body is part of your own contract.

### 17. Adding generic abstractions for hypothetical parsers

A registry with plugins and hooks increases complexity before the second concrete need exists.

**Correction:** Add the next adapter with the smallest clear selection mechanism.

## Worked examples

### Example 1: A misleading type hint versus runtime validation

Type hint only:

```python
def normalize_title(title: str) -> str:
    return title.strip()
```

A caller can still pass a runtime value that is not a string.

Runtime boundary validation:

```python
from pydantic import BaseModel, ConfigDict


class TitleRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    title: str
```

**Production conclusion:** Static typing improves code understanding before execution. Runtime validation protects a live boundary. Use both.

---

### Example 2: Mutable and frozen dataclasses

```python
from dataclasses import dataclass


@dataclass
class MutableBatch:
    document_ids: list[str]


@dataclass(frozen=True)
class FrozenBatch:
    document_ids: list[str]
```

```python
mutable = MutableBatch(document_ids=["a"])
mutable.document_ids = ["b"]

frozen = FrozenBatch(document_ids=["a"])
# frozen.document_ids = ["b"]  # Attribute rebinding is blocked.

frozen.document_ids.append("b")  # Nested list can still mutate.
```

Safer nested value:

```python
@dataclass(frozen=True)
class ImmutableBatch:
    document_ids: tuple[str, ...]
```

**Production conclusion:** Frozen dataclasses provide shallow protection, not deep immutability.

---

### Example 3: Pydantic validation at an untrusted boundary

```python
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class DocumentRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        frozen=True,
    )

    path: str = Field(min_length=1, max_length=1024)
    media_type: str = Field(min_length=1, max_length=128)
    correlation_id: str

    @field_validator("correlation_id")
    @classmethod
    def validate_correlation_id(cls, value: str) -> str:
        if _SAFE_ID.fullmatch(value) is None:
            raise ValueError("invalid correlation_id")
        return value
```

**Boundary behavior:**

* undeclared fields are rejected;
* incorrect strict field types are rejected;
* unsafe correlation IDs are rejected;
* successful validation still does not prove the file exists.

---

### Example 4: Plain class, dataclass, and Pydantic inheritance

Plain behavior-owning class:

```python
class RetryCounter:
    def __init__(self, limit: int) -> None:
        self._limit = limit
        self._attempts = 0

    def can_retry(self) -> bool:
        return self._attempts < self._limit

    def record_attempt(self) -> None:
        self._attempts += 1
```

Internal data:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RetryDecision:
    allowed: bool
    attempts_remaining: int
```

Boundary model:

```python
from pydantic import BaseModel, ConfigDict


class RetryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    limit: int
```

`RetryRequest` is a class derived from `BaseModel`. `RetryDecision` is a standard Python class transformed by `@dataclass`. `RetryCounter` is a manually implemented class with mutable lifecycle state.

---

### Example 5: Exception translation and chaining

Adapter boundary:

```python
from pathlib import Path


class ReaderDecodingError(Exception):
    pass


def read_utf8(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="strict") as stream:
            return stream.read()
    except UnicodeDecodeError as exc:
        raise ReaderDecodingError(
            "reader could not decode input as UTF-8"
        ) from exc
```

Service boundary:

```python
try:
    text = read_utf8(path)
except ReaderDecodingError as exc:
    raise DocumentDecodingError(
        "document is not valid UTF-8",
        correlation_id=correlation_id,
    ) from exc
```

**Production conclusion:** Each boundary translates to the vocabulary understood by its caller while retaining the original cause.

---

### Example 6: Safe structured logging

```python
logger.info(
    "document_extraction_completed",
    extra={
        "correlation_id": correlation_id,
        "media_type": media_type,
        "character_count": len(text),
    },
)
```

Unsafe:

```python
logger.info(
    "document_extraction_completed path=%s text=%s",
    path,
    text,
)
```

**Production conclusion:** Log lifecycle and dimensions, not payloads.

---

### Example 7: Generator streaming logical lines

```python
from collections.abc import Iterator
from pathlib import Path


def iter_logical_lines(path: Path) -> Iterator[str]:
    with path.open(
        "r",
        encoding="utf-8",
        errors="strict",
        newline="",
    ) as stream:
        for physical_line in stream:
            yield physical_line.rstrip("\r\n")
```

Single consumption:

```python
lines = iter_logical_lines(path)

first = list(lines)
second = list(lines)

assert second == []
```

The file may remain open while iteration is suspended.

---

### Example 8: Async I/O versus blocking and CPU work

Awaitable I/O:

```python
async def fetch_remote_document(
    client: AsyncMetadataClient,
    document_id: str,
) -> str:
    return await client.fetch_label(document_id)
```

Blocking work disguised as async:

```python
async def read_local_document_bad(path: Path) -> str:
    return path.read_text(encoding="utf-8")
```

Bridge to a thread:

```python
import asyncio


async def read_local_document_threaded(path: Path) -> str:
    return await asyncio.to_thread(
        path.read_text,
        encoding="utf-8",
        errors="strict",
    )
```

CPU-heavy pure Python work should not be expected to speed up merely because it is wrapped in `asyncio.to_thread`.

---

### Example 9: Behavior-focused pytest test with `tmp_path`

```python
from pathlib import Path


def test_utf8_reader_preserves_unicode(tmp_path: Path) -> None:
    path = tmp_path / "unicode.txt"
    path.write_text("भारत\nAI", encoding="utf-8")

    reader = Utf8TextFileReader()

    assert reader.read_text(path) == "भारत\nAI"
```

This test verifies observable behavior using a real temporary filesystem boundary.

---

### Example 10: FastAPI endpoint test with `TestClient`

```python
from fastapi.testclient import TestClient


def test_extract_endpoint_returns_typed_result(
    tmp_path: Path,
) -> None:
    path = tmp_path / "sample.txt"
    path.write_text("alpha\r\nbeta", encoding="utf-8")

    app = create_app()

    with TestClient(app) as client:
        response = client.post(
            "/v1/documents/extract",
            json={
                "path": str(path),
                "media_type": "text/plain",
                "correlation_id": "request-123",
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "correlation_id": "request-123",
        "media_type": "text/plain",
        "text": "alpha\nbeta",
        "character_count": 10,
        "line_count": 2,
    }
```

The example is illustrative and has not been executed here.

## Guided implementation

### 1. Project structure

```text
week-01-document-service/
├── document_service/
│   ├── __init__.py
│   ├── api.py
│   ├── dependencies.py
│   ├── domain.py
│   ├── errors.py
│   ├── main.py
│   ├── models.py
│   ├── ports.py
│   ├── readers.py
│   └── service.py
└── tests/
    ├── test_api.py
    ├── test_models.py
    ├── test_readers.py
    └── test_service.py
```

This layout is intentionally small. It separates responsibilities without introducing a generic plugin architecture.

---

### 2. Domain and adapter errors

Create `document_service/errors.py`:

```python
from typing import ClassVar


class ReaderError(Exception):
    """Base exception for the low-level reader boundary."""


class ReaderNotFoundError(ReaderError):
    """The requested reader resource does not exist."""


class ReaderDecodingError(ReaderError):
    """The reader could not decode the resource."""


class ReaderAccessError(ReaderError):
    """The reader could not access the resource."""


class DocumentServiceError(Exception):
    """Base exception exposed by the extraction service."""

    code: ClassVar[str] = "document_service_error"

    def __init__(
        self,
        message: str,
        *,
        correlation_id: str,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.correlation_id = correlation_id


class DocumentValidationError(DocumentServiceError):
    code = "document_validation_failed"


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


class DocumentNotFoundError(DocumentInfrastructureError):
    code = "document_not_found"
```

Design notes:

* Reader exceptions describe the filesystem adapter boundary.
* Service exceptions describe domain-visible categories.
* Each public service error has a stable machine-readable `code`.
* The safe correlation ID is carried without attaching the path or content.
* Inheritance is useful here because handlers need broader failure categories.

---

### 3. Internal domain values and pure normalization

Create `document_service/domain.py`:

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ExtractionCommand:
    path: Path
    media_type: str
    correlation_id: str


@dataclass(frozen=True, slots=True)
class ExtractedDocument:
    correlation_id: str
    media_type: str
    text: str
    character_count: int
    line_count: int


def normalize_newlines(text: str) -> str:
    """Normalize newline representation without trimming other whitespace."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def count_logical_lines(text: str) -> int:
    """Count logical lines for a non-empty document."""
    lines = text.splitlines()
    return len(lines) if lines else 1
```

Why frozen dataclasses:

* these values are internal;
* they have already crossed boundary validation;
* they should not change after construction;
* they do not need JSON parsing or schema generation;
* they remain ordinary lightweight domain values.

`normalize_newlines` is a function rather than a class because it has no state, dependency, or lifecycle.

---

### 4. Reader protocol

Create `document_service/ports.py`:

```python
from pathlib import Path
from typing import Protocol


class TextReader(Protocol):
    """Narrow interface required by the extraction service."""

    def read_text(self, path: Path) -> str:
        ...
```

The service depends on this capability rather than a concrete filesystem class.

---

### 5. UTF-8 text reader

Create `document_service/readers.py`:

```python
from pathlib import Path
from typing import ClassVar

from document_service.errors import (
    ReaderAccessError,
    ReaderDecodingError,
    ReaderNotFoundError,
)


class Utf8TextFileReader:
    """Read complete UTF-8 text files using strict decoding."""

    encoding: ClassVar[str] = "utf-8"

    def read_text(self, path: Path) -> str:
        try:
            with path.open(
                "r",
                encoding=self.encoding,
                errors="strict",
                newline="",
            ) as stream:
                return stream.read()
        except FileNotFoundError as exc:
            raise ReaderNotFoundError(
                "document resource was not found"
            ) from exc
        except UnicodeDecodeError as exc:
            raise ReaderDecodingError(
                "document resource is not valid UTF-8"
            ) from exc
        except OSError as exc:
            raise ReaderAccessError(
                "document resource could not be accessed"
            ) from exc
```

Important properties:

* UTF-8 is explicit.
* Decode errors are strict.
* The file is context-managed.
* Low-level exceptions are translated and chained.
* Error messages do not contain the path.
* The reader does not decide whether `.txt` or `text/plain` is supported; that is service policy.

---

### 6. Pydantic request and response models

Create `document_service/models.py`:

```python
import re
from pathlib import Path
from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from document_service.domain import ExtractedDocument


_SAFE_CORRELATION_ID = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$"
)


class DocumentRequest(BaseModel):
    """Untrusted JSON request boundary."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        frozen=True,
    )

    path: str = Field(min_length=1, max_length=1024)
    media_type: str = Field(min_length=1, max_length=128)
    correlation_id: str = Field(min_length=1, max_length=64)

    @field_validator("path")
    @classmethod
    def validate_path_text(cls, value: str) -> str:
        if "\x00" in value:
            raise ValueError("path must not contain a null character")
        if value != value.strip():
            raise ValueError(
                "path must not contain surrounding whitespace"
            )
        return value

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

    @model_validator(mode="after")
    def require_file_extension(self) -> Self:
        if Path(self.path).suffix == "":
            raise ValueError("path must include a file extension")
        return self


class ExtractionResponse(BaseModel):
    """Serialized successful response boundary."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        frozen=True,
    )

    correlation_id: str
    media_type: str
    text: str
    character_count: int = Field(ge=0)
    line_count: int = Field(ge=1)

    @classmethod
    def from_domain(
        cls,
        result: ExtractedDocument,
    ) -> Self:
        return cls(
            correlation_id=result.correlation_id,
            media_type=result.media_type,
            text=result.text,
            character_count=result.character_count,
            line_count=result.line_count,
        )


class ErrorResponse(BaseModel):
    """Stable error body owned by this application."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        frozen=True,
    )

    code: str
    message: str
    correlation_id: str
```

Boundary decisions:

* Unsupported media types are not rejected by the request model. They pass structural validation and are rejected by service policy, allowing a stable HTTP `415` mapping.
* A path without any extension is structurally malformed and receives request validation failure.
* File existence and decoding are not Pydantic concerns.
* Response conversion is an appropriate class method because it constructs the current response class from a domain value.
* The models are Pydantic classes derived from `BaseModel`; their configuration is declared through the class attribute `model_config`.

---

### 7. Extraction service

Create `document_service/service.py`:

```python
import logging
from typing import ClassVar

from document_service.domain import (
    ExtractedDocument,
    ExtractionCommand,
    count_logical_lines,
    normalize_newlines,
)
from document_service.errors import (
    DocumentDecodingError,
    DocumentInfrastructureError,
    DocumentNotFoundError,
    DocumentServiceError,
    DocumentValidationError,
    EmptyDocumentError,
    ReaderAccessError,
    ReaderDecodingError,
    ReaderNotFoundError,
    UnsupportedDocumentFormatError,
)
from document_service.ports import TextReader


logger = logging.getLogger(__name__)


class DocumentExtractionService:
    """Coordinate format policy, reading, normalization, and results."""

    supported_media_type: ClassVar[str] = "text/plain"
    supported_suffix: ClassVar[str] = ".txt"

    def __init__(self, reader: TextReader) -> None:
        self._reader = reader

    def extract(
        self,
        command: ExtractionCommand,
    ) -> ExtractedDocument:
        logger.info(
            "document_extraction_started",
            extra={
                "correlation_id": command.correlation_id,
                "media_type": command.media_type,
            },
        )

        try:
            self._validate_command(command)
            raw_text = self._read(command)
            normalized_text = normalize_newlines(raw_text)

            if normalized_text.strip() == "":
                raise EmptyDocumentError(
                    "document contains no non-whitespace text",
                    correlation_id=command.correlation_id,
                )

            result = ExtractedDocument(
                correlation_id=command.correlation_id,
                media_type=self.supported_media_type,
                text=normalized_text,
                character_count=len(normalized_text),
                line_count=count_logical_lines(normalized_text),
            )
        except DocumentServiceError as exc:
            logger.warning(
                "document_extraction_failed",
                extra={
                    "correlation_id": command.correlation_id,
                    "failure_code": exc.code,
                },
            )
            raise

        logger.info(
            "document_extraction_completed",
            extra={
                "correlation_id": result.correlation_id,
                "media_type": result.media_type,
                "character_count": result.character_count,
                "line_count": result.line_count,
            },
        )
        return result

    @classmethod
    def _validate_command(
        cls,
        command: ExtractionCommand,
    ) -> None:
        if command.correlation_id == "":
            raise DocumentValidationError(
                "correlation_id must not be empty",
                correlation_id=command.correlation_id,
            )

        if command.media_type != cls.supported_media_type:
            raise UnsupportedDocumentFormatError(
                "only text/plain documents are supported",
                correlation_id=command.correlation_id,
            )

        if command.path.suffix.lower() != cls.supported_suffix:
            raise UnsupportedDocumentFormatError(
                "only .txt documents are supported",
                correlation_id=command.correlation_id,
            )

    def _read(self, command: ExtractionCommand) -> str:
        try:
            return self._reader.read_text(command.path)
        except ReaderNotFoundError as exc:
            raise DocumentNotFoundError(
                "document was not found",
                correlation_id=command.correlation_id,
            ) from exc
        except ReaderDecodingError as exc:
            raise DocumentDecodingError(
                "document is not valid UTF-8",
                correlation_id=command.correlation_id,
            ) from exc
        except ReaderAccessError as exc:
            raise DocumentInfrastructureError(
                "document reader is unavailable",
                correlation_id=command.correlation_id,
            ) from exc
```

Class mechanics in this implementation:

* `supported_media_type` and `supported_suffix` are class attributes.
* `_reader` is instance state.
* `__init__` establishes the service’s reader dependency.
* `extract` and `_read` are instance methods.
* `_validate_command` is a class method because it uses overridable class policy.
* The service uses composition: it has a `TextReader`.
* The service does not inherit from the reader.
* Pure normalization remains outside the class.

---

### 8. Dependency assembly

Create `document_service/dependencies.py`:

```python
from document_service.readers import Utf8TextFileReader
from document_service.service import DocumentExtractionService


def get_extraction_service() -> DocumentExtractionService:
    reader = Utf8TextFileReader()
    return DocumentExtractionService(reader=reader)
```

The application assembly owns concrete construction. The service itself knows only the reader protocol.

For a larger application, dependency lifetime and reuse would need explicit review. This small stateless reader does not justify a container or service locator.

---

### 9. Thin FastAPI router

Create `document_service/api.py`:

```python
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, status

from document_service.dependencies import get_extraction_service
from document_service.domain import ExtractionCommand
from document_service.models import (
    DocumentRequest,
    ExtractionResponse,
)
from document_service.service import DocumentExtractionService


router = APIRouter(
    prefix="/v1/documents",
    tags=["documents"],
)


@router.post(
    "/extract",
    response_model=ExtractionResponse,
    status_code=status.HTTP_200_OK,
)
def extract_document(
    request: DocumentRequest,
    service: Annotated[
        DocumentExtractionService,
        Depends(get_extraction_service),
    ],
) -> ExtractionResponse:
    command = ExtractionCommand(
        path=Path(request.path),
        media_type=request.media_type,
        correlation_id=request.correlation_id,
    )
    result = service.extract(command)
    return ExtractionResponse.from_domain(result)
```

The route performs only:

1. HTTP request reception.
2. Dependency acquisition.
3. Boundary-to-domain conversion.
4. Service invocation.
5. Domain-to-response conversion.

It does not contain validation policy, filesystem access, normalization, logging policy, or error translation.

---

### 10. Application and stable error mappings

Create `document_service/main.py`:

```python
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from document_service.api import router
from document_service.errors import (
    DocumentExtractionError,
    DocumentInfrastructureError,
    DocumentNotFoundError,
    DocumentValidationError,
    UnsupportedDocumentFormatError,
)
from document_service.models import ErrorResponse


def _error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    correlation_id: str,
) -> JSONResponse:
    payload = ErrorResponse(
        code=code,
        message=message,
        correlation_id=correlation_id,
    )
    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(),
    )


def create_app() -> FastAPI:
    app = FastAPI(
        title="Week 1 Document Extraction Service",
        version="0.1.0",
    )
    app.include_router(router)

    @app.exception_handler(DocumentValidationError)
    async def handle_document_validation(
        _request: Request,
        exc: DocumentValidationError,
    ) -> JSONResponse:
        return _error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            code=exc.code,
            message=exc.message,
            correlation_id=exc.correlation_id,
        )

    @app.exception_handler(UnsupportedDocumentFormatError)
    async def handle_unsupported_format(
        _request: Request,
        exc: UnsupportedDocumentFormatError,
    ) -> JSONResponse:
        return _error_response(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            code=exc.code,
            message=exc.message,
            correlation_id=exc.correlation_id,
        )

    @app.exception_handler(DocumentNotFoundError)
    async def handle_document_not_found(
        _request: Request,
        exc: DocumentNotFoundError,
    ) -> JSONResponse:
        return _error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            code=exc.code,
            message=exc.message,
            correlation_id=exc.correlation_id,
        )

    @app.exception_handler(DocumentExtractionError)
    async def handle_extraction_failure(
        _request: Request,
        exc: DocumentExtractionError,
    ) -> JSONResponse:
        return _error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            code=exc.code,
            message=exc.message,
            correlation_id=exc.correlation_id,
        )

    @app.exception_handler(DocumentInfrastructureError)
    async def handle_infrastructure_failure(
        _request: Request,
        exc: DocumentInfrastructureError,
    ) -> JSONResponse:
        return _error_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            code=exc.code,
            message=exc.message,
            correlation_id=exc.correlation_id,
        )

    return app


app = create_app()
```

The handlers map domain-visible failures to HTTP concerns. They do not inspect `OSError`, `UnicodeDecodeError`, or filesystem paths.

---

### 11. Optional local run command

From the project root:

```bash
python -m uvicorn document_service.main:app --reload
```

This command is provided for local learning only. It has not been run or verified here. Deployment and production-server configuration are out of scope.

---

### 12. Example request

```json
{
  "path": "/tmp/example.txt",
  "media_type": "text/plain",
  "correlation_id": "week1-demo-001"
}
```

Illustrative success body:

```json
{
  "correlation_id": "week1-demo-001",
  "media_type": "text/plain",
  "text": "First line\nSecond line",
  "character_count": 22,
  "line_count": 2
}
```

The example output is derived from the shown text, not from an executed request.

## Independent exercises

### Exercise 1: Add a Markdown-text adapter

Add support for UTF-8 Markdown text without changing the public behavior of `DocumentExtractionService.extract`.

Do not add Markdown rendering, HTML conversion, front-matter parsing, or a generic plugin framework.

#### Acceptance criteria

* `.md` with declared media type `text/markdown` is accepted.
* UTF-8 decoding remains strict.
* `.txt` with `text/plain` continues to behave unchanged.
* Mismatched suffix and media type are rejected explicitly.
* Route functions remain thin.
* The service still depends on a narrow reader/parser abstraction.
* Error responses retain stable codes.
* Tests demonstrate both document types.

#### Edge cases

* Uppercase `.MD`.
* `notes.md.txt`.
* `text/markdown; charset=utf-8`.
* Empty Markdown document.
* Invalid UTF-8 bytes.
* A `.md` file declared as `text/plain`.
* A `.txt` file declared as `text/markdown`.

#### Optional hints

* Start with an explicit two-case selection rather than a registry.
* Decide whether selection belongs in the service or a small injected resolver.
* Keep Markdown extraction identical to text reading unless a concrete requirement says otherwise.

---

### Exercise 2: Enforce a configurable maximum document size

Add a configurable maximum number of bytes at the reader boundary.

#### Acceptance criteria

* The limit is injected or configured explicitly.
* A file over the limit is rejected before its entire content is retained in memory.
* A file exactly at the limit is handled according to a documented rule.
* The public error does not expose the path or content.
* The failure has a stable error category.
* Tests cover below, equal to, and above the limit.
* Unicode byte length is not confused with Python character count.

#### Edge cases

* Empty file.
* Multibyte UTF-8 text.
* File changes size between metadata inspection and reading.
* Negative configured limit.
* Symbolic links.
* Very large declared size but small actual file.
* Reader receives a non-regular file.

#### Optional hints

* Byte size and decoded character count are different.
* Metadata checks alone do not eliminate time-of-check/time-of-use races.
* Consider a bounded binary read followed by strict UTF-8 decoding.

---

### Exercise 3: Parametrize allowed and rejected media types

Add parametrized tests for media-type and suffix combinations.

#### Acceptance criteria

* At least one valid `.txt`/`text/plain` case is included.
* Unsupported media types are rejected with `UnsupportedDocumentFormatError`.
* Unsupported suffixes are rejected.
* Test IDs make failed combinations readable.
* Mutable parameter objects are not shared or mutated across cases.
* Tests assert behavior rather than private method calls.

#### Edge cases

* Uppercase media type.
* Surrounding whitespace.
* Empty media type.
* `text/plain; charset=utf-8`.
* `.TXT`.
* No extension.
* Multiple suffixes.

#### Optional hints

* Use `pytest.param(..., id="...")`.
* Decide explicitly whether media-type matching is case-sensitive.
* Keep request-shape failures separate from supported-format policy failures.

---

### Exercise 4: Prove raw document text is never logged

Use captured logs to verify that successful and failed extraction paths do not emit document text.

#### Acceptance criteria

* The test includes a unique secret marker in the document.
* Logs are captured for success.
* Logs are captured for at least one failure.
* The secret marker does not appear in `caplog.text`.
* The complete path does not appear in `caplog.text`.
* The correlation ID does appear.
* A stable failure code appears for the failure case.
* The test does not disable logging globally.

#### Edge cases

* Multiline secret.
* Secret included in an exception message from a fake dependency.
* Filename contains sensitive text.
* Failure before reading.
* Failure after reading.
* Logs emitted at different levels.

#### Optional hints

* Review whether propagating arbitrary low-level exception messages can leak payloads.
* Assert both required presence and forbidden absence.
* Inspect `caplog.records` when field-level checks are clearer than formatted text.

---

### Exercise 5: Design an async batch-extraction interface

Design, but do not implement, an interface for extracting several documents.

Choose among:

* sequential execution;
* asynchronous tasks;
* a bounded thread pool;
* a process pool;
* an external worker system.

#### Acceptance criteria

The design document explains:

* expected workload type;
* whether each dependency is synchronous or awaitable;
* concurrency limit;
* ordering guarantees;
* per-document and batch failure behavior;
* timeout behavior;
* cancellation behavior;
* backpressure;
* resource cleanup;
* retry safety;
* observability;
* why the rejected alternatives are less appropriate.

#### Edge cases

* One slow document.
* One invalid UTF-8 document.
* Cancellation after some documents complete.
* More inputs than available workers.
* CPU-heavy parser.
* Blocking third-party library.
* Duplicate document identifiers.
* Partial success.
* Caller disconnects.

#### Optional hints

* Async tasks help only when the work can suspend through awaitable operations.
* Threads can integrate blocking I/O but require a bounded executor.
* Processes may suit CPU-bound work but add serialization and lifecycle costs.
* Sequential execution may be the most reliable initial design.

## Testing and validation

### Validation status

The following code is a proposed test suite. It has not been executed or verified in this document.

A technical review should record:

* Python version;
* resolved package versions;
* operating system;
* exact command;
* pass/fail results;
* warnings;
* any version-sensitive changes.

### 1. Model tests

Create `tests/test_models.py`:

```python
import pytest
from pydantic import ValidationError

from document_service.models import DocumentRequest


def test_document_request_accepts_safe_values() -> None:
    request = DocumentRequest(
        path="notes.txt",
        media_type="text/plain",
        correlation_id="request-123",
    )

    assert request.path == "notes.txt"
    assert request.media_type == "text/plain"
    assert request.correlation_id == "request-123"


@pytest.mark.parametrize(
    "correlation_id",
    [
        "",
        "contains space",
        "../escape",
        "value/segment",
        "a" * 65,
    ],
)
def test_document_request_rejects_unsafe_correlation_id(
    correlation_id: str,
) -> None:
    with pytest.raises(ValidationError):
        DocumentRequest(
            path="notes.txt",
            media_type="text/plain",
            correlation_id=correlation_id,
        )


def test_document_request_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        DocumentRequest.model_validate(
            {
                "path": "notes.txt",
                "media_type": "text/plain",
                "correlation_id": "request-123",
                "unexpected": "value",
            }
        )


def test_document_request_requires_extension() -> None:
    with pytest.raises(ValidationError):
        DocumentRequest(
            path="notes",
            media_type="text/plain",
            correlation_id="request-123",
        )
```

### 2. Reader tests

Create `tests/test_readers.py`:

```python
from pathlib import Path

import pytest

from document_service.errors import (
    ReaderDecodingError,
    ReaderNotFoundError,
)
from document_service.readers import Utf8TextFileReader


def test_reader_reads_utf8_text(tmp_path: Path) -> None:
    path = tmp_path / "document.txt"
    path.write_text("भारत\nAI", encoding="utf-8")

    result = Utf8TextFileReader().read_text(path)

    assert result == "भारत\nAI"


def test_reader_rejects_invalid_utf8(tmp_path: Path) -> None:
    path = tmp_path / "invalid.txt"
    path.write_bytes(b"\xff\xfe\xfa")

    with pytest.raises(ReaderDecodingError) as captured:
        Utf8TextFileReader().read_text(path)

    assert isinstance(captured.value.__cause__, UnicodeDecodeError)


def test_reader_translates_missing_file(tmp_path: Path) -> None:
    path = tmp_path / "missing.txt"

    with pytest.raises(ReaderNotFoundError) as captured:
        Utf8TextFileReader().read_text(path)

    assert isinstance(captured.value.__cause__, FileNotFoundError)
```

### 3. Service tests

Create `tests/test_service.py`:

```python
import logging
from dataclasses import dataclass
from pathlib import Path

import pytest

from document_service.domain import ExtractionCommand
from document_service.errors import (
    DocumentDecodingError,
    DocumentInfrastructureError,
    EmptyDocumentError,
    ReaderAccessError,
    ReaderDecodingError,
    UnsupportedDocumentFormatError,
)
from document_service.service import DocumentExtractionService


@dataclass(slots=True)
class FixedReader:
    text: str

    def read_text(self, path: Path) -> str:
        return self.text


class DecodingFailingReader:
    def read_text(self, path: Path) -> str:
        raise ReaderDecodingError("simulated decode failure")


class AccessFailingReader:
    def read_text(self, path: Path) -> str:
        raise ReaderAccessError("simulated access failure")


def make_command(
    *,
    path: str = "document.txt",
    media_type: str = "text/plain",
    correlation_id: str = "request-123",
) -> ExtractionCommand:
    return ExtractionCommand(
        path=Path(path),
        media_type=media_type,
        correlation_id=correlation_id,
    )


def test_service_extracts_and_normalizes_text() -> None:
    service = DocumentExtractionService(
        reader=FixedReader("alpha\r\nbeta\rgamma")
    )

    result = service.extract(make_command())

    assert result.correlation_id == "request-123"
    assert result.media_type == "text/plain"
    assert result.text == "alpha\nbeta\ngamma"
    assert result.character_count == len("alpha\nbeta\ngamma")
    assert result.line_count == 3


@pytest.mark.parametrize(
    ("path", "media_type"),
    [
        ("document.pdf", "application/pdf"),
        ("document.md", "text/markdown"),
        ("document.txt", "application/pdf"),
        ("document.pdf", "text/plain"),
    ],
)
def test_service_rejects_unsupported_formats(
    path: str,
    media_type: str,
) -> None:
    service = DocumentExtractionService(
        reader=FixedReader("content")
    )

    with pytest.raises(UnsupportedDocumentFormatError):
        service.extract(
            make_command(
                path=path,
                media_type=media_type,
            )
        )


@pytest.mark.parametrize(
    "text",
    [
        "",
        " ",
        "\n",
        "\t\r\n",
    ],
)
def test_service_rejects_empty_or_whitespace_document(
    text: str,
) -> None:
    service = DocumentExtractionService(
        reader=FixedReader(text)
    )

    with pytest.raises(EmptyDocumentError):
        service.extract(make_command())


def test_service_translates_decoding_failure() -> None:
    service = DocumentExtractionService(
        reader=DecodingFailingReader()
    )

    with pytest.raises(DocumentDecodingError) as captured:
        service.extract(make_command())

    assert isinstance(
        captured.value.__cause__,
        ReaderDecodingError,
    )


def test_service_translates_reader_access_failure() -> None:
    service = DocumentExtractionService(
        reader=AccessFailingReader()
    )

    with pytest.raises(
        DocumentInfrastructureError
    ) as captured:
        service.extract(make_command())

    assert isinstance(
        captured.value.__cause__,
        ReaderAccessError,
    )


def test_service_does_not_log_document_text_or_path(
    caplog: pytest.LogCaptureFixture,
) -> None:
    secret_text = "UNIQUE-SECRET-DOCUMENT-CONTENT"
    path = Path("/sensitive/location/private-document.txt")
    service = DocumentExtractionService(
        reader=FixedReader(secret_text)
    )

    with caplog.at_level(
        logging.INFO,
        logger="document_service.service",
    ):
        result = service.extract(
            ExtractionCommand(
                path=path,
                media_type="text/plain",
                correlation_id="safe-correlation-123",
            )
        )

    assert result.text == secret_text
    assert secret_text not in caplog.text
    assert str(path) not in caplog.text
    assert "safe-correlation-123" in caplog.text
```

### 4. Endpoint tests

Create `tests/test_api.py`:

```python
from pathlib import Path

from fastapi.testclient import TestClient

from document_service.main import create_app


def test_extract_endpoint_success(tmp_path: Path) -> None:
    path = tmp_path / "sample.txt"
    path.write_text("alpha\r\nbeta", encoding="utf-8")
    app = create_app()

    with TestClient(app) as client:
        response = client.post(
            "/v1/documents/extract",
            json={
                "path": str(path),
                "media_type": "text/plain",
                "correlation_id": "endpoint-success-1",
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "correlation_id": "endpoint-success-1",
        "media_type": "text/plain",
        "text": "alpha\nbeta",
        "character_count": len("alpha\nbeta"),
        "line_count": 2,
    }


def test_extract_endpoint_maps_unsupported_format(
    tmp_path: Path,
) -> None:
    path = tmp_path / "sample.txt"
    path.write_text("content", encoding="utf-8")
    app = create_app()

    with TestClient(app) as client:
        response = client.post(
            "/v1/documents/extract",
            json={
                "path": str(path),
                "media_type": "application/pdf",
                "correlation_id": "endpoint-format-1",
            },
        )

    assert response.status_code == 415
    assert response.json() == {
        "code": "unsupported_document_format",
        "message": "only text/plain documents are supported",
        "correlation_id": "endpoint-format-1",
    }


def test_extract_endpoint_maps_missing_document(
    tmp_path: Path,
) -> None:
    path = tmp_path / "missing.txt"
    app = create_app()

    with TestClient(app) as client:
        response = client.post(
            "/v1/documents/extract",
            json={
                "path": str(path),
                "media_type": "text/plain",
                "correlation_id": "endpoint-missing-1",
            },
        )

    assert response.status_code == 404
    assert response.json() == {
        "code": "document_not_found",
        "message": "document was not found",
        "correlation_id": "endpoint-missing-1",
    }


def test_extract_endpoint_rejects_invalid_request() -> None:
    app = create_app()

    with TestClient(app) as client:
        response = client.post(
            "/v1/documents/extract",
            json={
                "path": "sample.txt",
                "media_type": "text/plain",
                "correlation_id": "contains space",
            },
        )

    assert response.status_code == 422
```

### 5. Recommended validation sequence

After creating the files, a learner should run:

```bash
python --version
python -m pip list
python -m pytest
```

Optional focused runs:

```bash
python -m pytest tests/test_models.py
python -m pytest tests/test_readers.py
python -m pytest tests/test_service.py
python -m pytest tests/test_api.py
```

Optional verbose run:

```bash
python -m pytest -vv
```

No result is asserted here because these commands have not been executed in this document.

### 6. Required test coverage matrix

| Behavior                   | Layer          | Expected test                                           |
| -------------------------- | -------------- | ------------------------------------------------------- |
| Valid request shape        | Pydantic model | Model construction succeeds                             |
| Unsafe correlation ID      | Pydantic model | `ValidationError`                                       |
| Extra request fields       | Pydantic model | `ValidationError`                                       |
| UTF-8 Unicode text         | Reader         | Text preserved                                          |
| Invalid UTF-8              | Reader         | `ReaderDecodingError` chained from `UnicodeDecodeError` |
| Missing file               | Reader         | `ReaderNotFoundError` chained from `FileNotFoundError`  |
| Newline normalization      | Service        | Stable normalized text                                  |
| Unsupported media type     | Service        | `UnsupportedDocumentFormatError`                        |
| Unsupported suffix         | Service        | `UnsupportedDocumentFormatError`                        |
| Empty document             | Service        | `EmptyDocumentError`                                    |
| Reader decode failure      | Service        | `DocumentDecodingError`                                 |
| Reader access failure      | Service        | `DocumentInfrastructureError`                           |
| Sensitive log exclusion    | Service        | Content and path absent                                 |
| Success endpoint           | HTTP           | `200` typed JSON                                        |
| Unsupported endpoint input | HTTP           | `415` stable error                                      |
| Missing file endpoint      | HTTP           | `404` stable error                                      |
| Invalid request shape      | HTTP           | `422`                                                   |

### 7. What not to infer from passing tests

Even a passing suite would not prove:

* unrestricted paths are secure;
* files cannot change during reading;
* large files are safe;
* concurrency is safe;
* all operating systems behave identically;
* all Unicode edge cases are covered;
* dependency upgrades are compatible;
* the service is production-deployable;
* logs are safe under every formatter and exception handler.

Tests provide evidence for specific stated behavior, not universal correctness.

## Interview preparation

### 1. Mutable versus immutable objects

**Question:** Why does mutability matter in an AI pipeline?

**Strong answer:**

Python names can refer to the same object. When a mutable list or dictionary is shared between retrieval, ranking, prompting, evaluation, and logging components, an in-place mutation by one component changes what the others observe. This can cause nondeterministic prompts, corrupted caches, cross-request contamination, and tests that depend on execution order.

A frozen dataclass prevents normal attribute rebinding but does not recursively freeze nested values. For stronger value semantics, use immutable nested types such as tuples, create defensive copies at boundaries, or use APIs that return new values.

**Follow-up questions:**

* Does `frozen=True` make a dataclass deeply immutable?
* What happens when two objects hold the same list?
* When is copying too expensive?
* How would you prevent mutation of nested metadata?
* How does mutation affect cache keys?

---

### 2. Plain class versus dataclass versus Pydantic model

**Question:** How do you choose among them?

**Strong answer:**

I use a plain class when the object owns behavior, dependencies, lifecycle, or controlled state transitions. I use a dataclass for internal records where generated initialization and comparison are useful. A frozen dataclass is useful for internal value-like commands and results after validation. I use a Pydantic `BaseModel` subclass when data crosses an untrusted serialization boundary and requires runtime validation, coercion policy, serialization, or schema generation.

I avoid using Pydantic for every internal value because that couples domain logic to a boundary library. I avoid using dataclasses to claim runtime validation because annotations alone do not enforce input types.

**Follow-up questions:**

* Can a dataclass contain methods?
* Is a Pydantic model a class?
* Where should conversion between Pydantic and domain values occur?
* Why might strict mode matter?
* When is a plain dictionary sufficient?

---

### 3. Static typing versus runtime validation

**Question:** Why do both matter?

**Strong answer:**

Static typing detects inconsistencies before execution and improves maintainability, refactoring, editor support, and interface clarity. It does not generally prevent arbitrary runtime callers from passing incorrect values.

Runtime validation checks actual input at the moment it crosses a trust boundary. In an AI system, document metadata, LLM output, queue messages, API payloads, and tool results are runtime data and must be validated independently of type annotations.

**Follow-up questions:**

* Can type hints change runtime behavior?
* Where would you isolate an untyped SDK response?
* Can Pydantic coercion hide bad data?
* What does strict validation trade away?
* Should trusted internal functions validate every argument again?

---

### 4. Why validation matters for LLM-derived data

**Question:** The LLM returned JSON. Why validate it?

**Strong answer:**

Valid JSON proves only syntactic parseability. It does not prove the required keys exist, values have the intended types, identifiers are safe, constraints hold, or mutually dependent fields are consistent.

An LLM may emit missing fields, invented fields, wrong units, strings where numbers are expected, unsafe tool arguments, or semantically contradictory values. A boundary model converts the output into either a trusted typed representation or an explicit validation failure before downstream side effects occur.

**Follow-up questions:**

* Is schema validation enough to prove truth?
* What validation belongs after schema validation?
* How would you handle unknown fields?
* Should invalid output be retried?
* How do you prevent a model-generated path from accessing arbitrary files?

---

### 5. Exception translation

**Question:** Where should exceptions be translated?

**Strong answer:**

Translate where the current abstraction understands the lower-level failure and can express it in vocabulary meaningful to its caller.

The reader translates `UnicodeDecodeError` into `ReaderDecodingError`. The service translates that into `DocumentDecodingError` and adds the safe correlation ID. The API maps the service category to a stable HTTP response. I preserve the original cause with `raise ... from exc`.

I do not translate exceptions repeatedly without adding meaning, and I do not expose raw low-level messages to clients.

**Follow-up questions:**

* When should an exception propagate unchanged?
* Why is catching `Exception` dangerous?
* How do you classify timeouts?
* Is “file not found” infrastructure or validation?
* Should retries occur in the route, service, or adapter?

---

### 6. Generators versus lists

**Question:** What are the trade-offs?

**Strong answer:**

A generator is lazy and single-consumption. It can reduce peak memory and improve time-to-first-result, but failures may be deferred until iteration. It can also keep files, network responses, or database cursors open while suspended.

A list eagerly computes and stores results. It uses more memory but is repeatable, surfaces construction failures earlier, and has a simpler resource lifecycle.

I choose based on bounded size, latency requirements, repeatability, failure timing, and who owns resource cleanup—not simply because generators appear more memory-efficient.

**Follow-up questions:**

* What happens on a second iteration?
* When is the file opened in a generator?
* How do you close a partially consumed generator?
* How do retries work after partial consumption?
* Can generators improve total computation time?

---

### 7. Threads versus async

**Question:** When do you choose each?

**Strong answer:**

Async fits a stack whose I/O operations expose awaitable APIs and can suspend without blocking the event loop. Threads are useful for integrating blocking I/O libraries or synchronous SDKs, but require bounded worker capacity and careful shared-state handling.

Neither is automatically the right answer for CPU-heavy pure-Python work. That may require processes, native implementations, accelerators, or external workers.

I also consider cancellation semantics, backpressure, debugging, library compatibility, and operational complexity. Sequential processing may be preferable when throughput requirements are modest and reliability is the priority.

**Follow-up questions:**

* What happens when synchronous file I/O runs in `async def`?
* Can a Python thread be forcibly cancelled safely?
* How do you bound concurrency?
* What is backpressure?
* When would a process pool be inappropriate?

---

### 8. Useful and sensitive logs

**Question:** What should extraction logs contain?

**Strong answer:**

Useful logs contain a stable event name, safe correlation ID, media type, success or failure category, counts, duration when measured safely, and an internal trace for unexpected failures.

They should exclude raw document text, full paths, credentials, arbitrary metadata, prompts, model outputs, and unreviewed low-level exception messages. The goal is to diagnose lifecycle and failure class without duplicating the sensitive payload into another storage system.

**Follow-up questions:**

* Are filenames sensitive?
* Should validation failures include rejected values?
* When should a traceback be logged?
* Who configures the root logger?
* How would you test that secrets do not appear?

---

### 9. Why thin routes matter

**Question:** Why not put extraction directly in the FastAPI route?

**Strong answer:**

A route is an HTTP adapter. Keeping it thin prevents HTTP concerns from becoming coupled to filesystem access, decoding, normalization, policy, and logging. The service can then be tested without an HTTP client, and the same orchestration can be invoked from another interface.

Thin routes also make exception mapping and dependency replacement clearer. The trade-off is additional modules and conversion code, which is justified when responsibilities are genuinely distinct.

**Follow-up questions:**

* Can a route ever contain validation?
* Where should status-code selection live?
* How do you avoid excessive layering?
* Would a three-line endpoint need a service?
* How do dependency overrides affect tests?

## Knowledge check

### Questions

1. What is the difference between an instance attribute and a class attribute?
2. Why is a mutable list usually unsafe as a class attribute?
3. What does `__init__` do during normal object construction?
4. When is an instance method more appropriate than a module-level function?
5. What receives the first argument of a class method?
6. Why is a static method sometimes less clear than a module-level function?
7. What does composition mean in the extraction service?
8. Name two appropriate uses of inheritance in this module.
9. Do Python function annotations automatically reject incorrect runtime values?
10. What problem does a `Protocol` solve?
11. Why should untyped data be contained near a boundary?
12. Does a standard dataclass validate incoming runtime values automatically?
13. What does `frozen=True` prevent?
14. Why is frozen dataclass immutability shallow?
15. What class does a Pydantic model inherit from?
16. What is `model_config` used for in Pydantic v2?
17. When should you use a field validator?
18. When should you use a model validator?
19. What is the difference between `model_dump()` and `model_dump_json()`?
20. Why should file existence not be checked in a Pydantic validator?
21. Where should `UnicodeDecodeError` first be translated?
22. What does `raise NewError(...) from exc` preserve?
23. Why is returning `""` after catching every exception dangerous?
24. Why should library modules avoid configuring the root logger?
25. Name three fields safe to include in extraction logs.
26. Why can a generator reduce peak memory?
27. Why can a generator make error handling harder?
28. What happens when an exhausted generator is iterated again?
29. Why can a generator hold a file open?
30. Does `async def` make synchronous filesystem access non-blocking?
31. When does async improve throughput?
32. Why should thread-pool capacity be bounded?
33. Which layer should know about HTTP status code `415`?
34. Which layer should know about `FileNotFoundError`?
35. Why does the service depend on a `TextReader` protocol?
36. What makes the guided FastAPI route thin?
37. Why are complete arbitrary paths excluded from logs?
38. Why is invalid UTF-8 rejected instead of ignored?
39. What does the current implementation do with whitespace-only documents?
40. Which test verifies that document content is not logged?

### Answer key

1. Instance attributes belong to a particular object; class attributes are defined on and shared through the class.
2. All instances may observe and mutate the same list.
3. It initializes the newly created instance’s state during normal instantiation.
4. When behavior uses instance state, dependencies, or lifecycle.
5. The current class, conventionally named `cls`.
6. A module function can state stateless behavior more directly.
7. `DocumentExtractionService` contains and uses a reader dependency.
8. Pydantic models from `BaseModel`; specialized exceptions from common error categories.
9. No.
10. It describes required behavior structurally without forcing implementation inheritance.
11. So uncertainty does not spread through the typed internal design.
12. No.
13. Normal attribute rebinding.
14. Nested mutable objects can still change.
15. `pydantic.BaseModel`.
16. Declaring model-wide validation and behavior options.
17. For a rule primarily associated with one field.
18. For relationships involving several fields or the model as a whole.
19. The first produces Python data; the second produces JSON text.
20. It is changing I/O state, may block, and can become stale before use.
21. At the filesystem reader boundary.
22. The original causal exception.
23. It turns defects and infrastructure failures into apparently valid empty data.
24. Logging policy belongs to the application or process owner.
25. Correlation ID, media type, stable failure code, character count, or line count.
26. It produces values lazily rather than storing all of them at once.
27. Failures can occur later during iteration and resources can remain open.
28. It yields no further values.
29. Its context manager can remain suspended around a `yield`.
30. No.
31. When multiple operations spend time awaiting genuinely non-blocking I/O.
32. To prevent unbounded queues, memory use, contention, and downstream overload.
33. The HTTP application layer.
34. The filesystem adapter.
35. To separate orchestration from concrete I/O and permit deterministic fakes.
36. It converts models, invokes the service, and returns a response without business or I/O logic.
37. Paths may expose user names, tenant information, internal layout, or document identity.
38. Ignoring undecodable bytes can silently change meaning.
39. It raises `EmptyDocumentError`.
40. `test_service_does_not_log_document_text_or_path`.

## Weekly deliverables

1. A Python 3.13.12 virtual environment created with `venv`.
2. Runtime and test dependencies installed through `pip`.
3. The complete `document_service` package.
4. A thin FastAPI route at `/v1/documents/extract`.
5. Pydantic v2 request, response, and error models.
6. Frozen domain command and result dataclasses.
7. A reader protocol and UTF-8 filesystem adapter.
8. An extraction service with explicit format policy.
9. A documented exception hierarchy.
10. Safe lifecycle logging.
11. Unit tests for models, reader behavior, service behavior, and logs.
12. Endpoint tests for success and stable error mappings.
13. Written answers to the interview questions.
14. A design response for the async batch-extraction exercise.
15. A short technical-review record containing versions, commands, results, and unresolved issues.

## Definition of done

Week 1 is ready for technical review when all of the following are true:

### Architecture

* [ ] The FastAPI route is thin.
* [ ] The extraction service is separate from the route.
* [ ] Filesystem reading is isolated behind a narrow interface.
* [ ] Domain modules do not import FastAPI.
* [ ] Dependencies point inward toward narrow interfaces.
* [ ] No speculative plugin framework has been added.

### Python classes

* [ ] Instance state is used for the injected reader.
* [ ] Class attributes represent shared format policy.
* [ ] The role of `__init__` is understood.
* [ ] Instance, class, and static methods can be distinguished.
* [ ] Composition is used between service and reader.
* [ ] Inheritance is limited to genuine “is-a” relationships.
* [ ] Stateless normalization remains a function.
* [ ] Mutable class-attribute hazards can be explained.

### Types and models

* [ ] Public functions have explicit parameter and return types.
* [ ] No unexplained `Any` appears.
* [ ] Optional values are narrowed explicitly.
* [ ] The reader uses a typed protocol.
* [ ] Pydantic models are understood as `BaseModel` subclasses.
* [ ] Annotated fields and `ConfigDict` are used.
* [ ] Field and model validators have focused responsibilities.
* [ ] Pydantic v2 serialization methods are used.
* [ ] Plain classes, dataclasses, frozen dataclasses, and Pydantic models have distinguishable roles.

### Supported behavior

* [ ] Only UTF-8 `.txt` with `text/plain` is accepted.
* [ ] Newlines are normalized without trimming other whitespace.
* [ ] Empty or whitespace-only documents are rejected.
* [ ] Results serialize to structured JSON.
* [ ] Another text parser can be added without changing the route contract.

### Failures

* [ ] Validation, unsupported format, extraction, and infrastructure failures are distinct.
* [ ] Missing files have a stable error category.
* [ ] Invalid UTF-8 has a stable error category.
* [ ] Low-level exceptions are translated at adapter boundaries.
* [ ] Causal exceptions are preserved with chaining.
* [ ] Broad exception suppression is absent.
* [ ] Context managers protect filesystem cleanup.

### Logging

* [ ] Module loggers use `logging.getLogger(__name__)`.
* [ ] Library modules do not configure the root logger.
* [ ] Correlation identifiers are logged.
* [ ] Stable failure codes are logged.
* [ ] Document text is never logged.
* [ ] Complete paths are never logged.
* [ ] Tests assert sensitive-data exclusion.

### Iteration and concurrency

* [ ] Iterable, iterator, and generator differences can be explained.
* [ ] Generator single-consumption behavior can be demonstrated.
* [ ] Deferred exceptions and resource lifetime can be explained.
* [ ] Async is treated as a concurrency choice, not a universal speed improvement.
* [ ] Blocking work inside an event loop can be identified.
* [ ] Threads, async, processes, and sequential execution can be compared.

### Testing

* [ ] Model validation tests exist.
* [ ] `tmp_path` is used for filesystem behavior.
* [ ] Success behavior is tested.
* [ ] Unsupported media types and suffixes are tested.
* [ ] Invalid UTF-8 is tested.
* [ ] Empty documents are tested.
* [ ] Reader failures are tested.
* [ ] Exception chaining is tested.
* [ ] Log leakage is tested.
* [ ] Endpoint success is tested.
* [ ] Stable endpoint error mappings are tested.
* [ ] Tests are deterministic and isolated.
* [ ] Mocks or fakes are limited to external boundaries.

### Review integrity

* [ ] Python 3.13.12 is confirmed.
* [ ] Resolved dependency versions are recorded.
* [ ] Version-sensitive claims are checked against installed documentation.
* [ ] Commands and tests are actually run by the learner or reviewer.
* [ ] Results are recorded without claiming unperformed verification.
* [ ] All independent exercises include acceptance criteria, edge cases, and hints.
* [ ] Interview answers include trade-offs and follow-up reasoning.

## Sources and further reading

All sources below are primary documentation or specifications. Live documentation may change after this module is generated.

### Python 3.13.12 and environment

* Python 3.13.12 release: https://www.python.org/downloads/release/python-31312/
* Python source releases: https://www.python.org/downloads/source/
* Python `venv`: https://docs.python.org/3.13/library/venv.html
* `pip install`: https://pip.pypa.io/en/stable/cli/pip_install/

Python’s official release page confirms the 3.13.12 release and currently notes that it has been superseded.

### Python classes and object behavior

* Classes tutorial: https://docs.python.org/3.13/tutorial/classes.html
* Python data model: https://docs.python.org/3.13/reference/datamodel.html
* Built-in types: https://docs.python.org/3.13/library/stdtypes.html

The classes tutorial covers constructors, instance state, class attributes, methods, inheritance, iterators, and generators.

### Type hints and protocols

* `typing` module: https://docs.python.org/3.13/library/typing.html
* PEP 484 — Type Hints: https://peps.python.org/pep-0484/
* PEP 544 — Protocols: https://peps.python.org/pep-0544/

### Dataclasses and immutability

* `dataclasses`: https://docs.python.org/3.13/library/dataclasses.html
* PEP 557 — Data Classes: https://peps.python.org/pep-0557/

Dataclasses are standard Python classes with generated methods based on annotated fields; frozen behavior must not be mistaken for recursive immutability.

### Exceptions and resource management

* Errors and exceptions tutorial: https://docs.python.org/3.13/tutorial/errors.html
* `contextlib`: https://docs.python.org/3.13/library/contextlib.html
* PEP 343 — The `with` Statement: https://peps.python.org/pep-0343/

### Logging

* Logging HOWTO: https://docs.python.org/3.13/howto/logging.html
* Logging library reference: https://docs.python.org/3.13/library/logging.html

### Iterators and generators

* Classes tutorial, iterators and generators: https://docs.python.org/3.13/tutorial/classes.html#iterators
* Generator expressions: https://docs.python.org/3.13/reference/expressions.html#generator-expressions
* PEP 255 — Simple Generators: https://peps.python.org/pep-0255/

### Async and concurrency

* `asyncio`: https://docs.python.org/3.13/library/asyncio.html
* Coroutines and tasks: https://docs.python.org/3.13/library/asyncio-task.html
* `concurrent.futures`: https://docs.python.org/3.13/library/concurrent.futures.html
* FastAPI concurrency guidance: https://fastapi.tiangolo.com/async/

Python and FastAPI documentation distinguish awaitable I/O, blocking work, concurrency, and CPU-bound parallelism.

### Pydantic v2

* Models: https://docs.pydantic.dev/latest/concepts/models/
* Configuration: https://docs.pydantic.dev/latest/concepts/config/
* Fields: https://docs.pydantic.dev/latest/concepts/fields/
* Validators: https://docs.pydantic.dev/latest/concepts/validators/
* Serialization: https://docs.pydantic.dev/latest/concepts/serialization/
* Strict mode: https://docs.pydantic.dev/latest/concepts/strict_mode/
* Error handling: https://docs.pydantic.dev/latest/errors/errors/
* Migration from v1 to v2: https://docs.pydantic.dev/latest/migration/

The official documentation defines Pydantic models as classes inheriting from `BaseModel` with fields declared through annotated attributes. It also documents model configuration, validators, validation methods, and serialization methods.

### FastAPI

* Request bodies: https://fastapi.tiangolo.com/tutorial/body/
* Response models: https://fastapi.tiangolo.com/tutorial/response-model/
* Dependencies: https://fastapi.tiangolo.com/tutorial/dependencies/
* Larger applications and routers: https://fastapi.tiangolo.com/tutorial/bigger-applications/
* Error handling: https://fastapi.tiangolo.com/tutorial/handling-errors/
* Testing: https://fastapi.tiangolo.com/tutorial/testing/
* Dependency overrides: https://fastapi.tiangolo.com/advanced/testing-dependencies/

FastAPI documentation covers Pydantic request bodies, response-model serialization, dependency injection, routers, error handling, `TestClient`, and dependency overrides.

### pytest

* Assertions and expected exceptions: https://docs.pytest.org/en/stable/how-to/assert.html
* Fixtures: https://docs.pytest.org/en/stable/how-to/fixtures.html
* Temporary paths: https://docs.pytest.org/en/stable/how-to/tmp_path.html
* Parametrization: https://docs.pytest.org/en/stable/how-to/parametrize.html
* Log capture: https://docs.pytest.org/en/stable/how-to/logging.html

pytest documents `tmp_path`, parametrization, expected-exception assertions, and log capture.

## Assumptions and unresolved questions

### Assumptions

1. Python 3.13.12 is mandatory even though a later Python 3.13 patch release exists.
2. The service runs in an environment where the process can read local files.
3. The caller supplies a path that is meaningful to the server process.
4. Only UTF-8 `.txt` documents with exact media type `text/plain` are supported.
5. `.TXT` is accepted because suffix comparison is case-insensitive.
6. Media-type comparison is exact and case-sensitive.
7. `text/plain; charset=utf-8` is rejected by the current policy.
8. Newline normalization is allowed and documented.
9. Other whitespace is preserved.
10. Whitespace-only documents are considered empty and rejected.
11. Full-document reading is acceptable for the initial learning build.
12. Maximum file size is deferred to an exercise.
13. Authentication, authorization, tenant isolation, and path sandboxing are outside this week.
14. HTTP request validation errors use FastAPI’s framework-provided `422` response.
15. Application-owned domain errors use the stable `ErrorResponse` schema.
16. The synchronous reader justifies a synchronous FastAPI route.
17. Logging formatting and destinations are configured by the application environment, not the library modules.

### Verification required

1. Confirm the Python 3.13.12 binary and `pip` installation method for the learner’s platform.
2. Confirm that resolved FastAPI, Pydantic, Starlette, HTTPX, pytest, and Uvicorn releases support Python 3.13.12.
3. Confirm exact Pydantic v2 strict-mode behavior for every declared field.
4. Confirm FastAPI’s current handling of synchronous route functions and dependencies.
5. Confirm `TestClient` compatibility with the resolved HTTPX and Starlette versions.
6. Run the complete suite and record actual results.
7. Review whether the selected error status codes match the organization’s API standards.
8. Review whether a missing document should remain `404` or be hidden behind another status for security reasons.
9. Review whether case-insensitive `.TXT` support is desired.
10. Review whether media types should be normalized or parsed rather than compared exactly.
11. Review path authorization before exposing this design beyond a controlled learning environment.
12. Decide whether a leading UTF-8 byte-order mark should be preserved, rejected, or handled explicitly.
13. Decide whether line counting should treat a trailing newline as creating an additional empty logical line.
14. Decide whether successful responses should return full text or only extraction metadata in later production designs.

## Review history

* **2026-07-21 — Initial generation:** Created as Week 1, Phase 1 from the approved binding outline and required generation schema. The module targets Python 3.13.12, `pip`, FastAPI with thin routes, a separate service layer, UTF-8 `.txt` documents, explicit class instruction, Pydantic v2, exception taxonomy, safe logging, generators, async fundamentals, pytest, independent exercises, and interview preparation.
* **Technical review:** Pending.
* **Human review:** Pending.
* **Execution verification:** Not performed or claimed.
