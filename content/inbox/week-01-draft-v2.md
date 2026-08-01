---

week: 1
phase: 1
title: Python for production AI systems
status: draft
version: 0.2.0
last_reviewed: 2026-07-22
estimated_hours: null
prerequisites: ["Working knowledge of Python syntax", "Basic JSON knowledge"]
generated_with: ChatGPT Web
technical_review: review_candidate
human_review: pending
---------------------

# Python for Production AI Systems

## Overview

Production AI systems fail most often at boundaries: malformed model output, unsupported uploads, inconsistent metadata, unexpected encodings, unbounded payloads, blocking dependencies, poorly isolated responsibilities, and logs that accidentally expose sensitive inputs.

This week builds the Python engineering foundation needed to handle those boundaries deliberately. The guided implementation is a small FastAPI document-extraction service that:

* accepts a bounded multipart upload;
* receives multipart fields named `media_type`, `correlation_id`, and `file`;
* supports UTF-8 `.txt` documents only;
* limits an uploaded document to 1 MiB;
* reads at most 1 MiB plus one sentinel byte;
* returns HTTP `413` with code `document_too_large` when the limit is exceeded;
* requires the declared media type and upload content type to both equal `text/plain`;
* validates the uploaded filename suffix;
* uses Pydantic v2 models to validate untrusted metadata;
* keeps the FastAPI route thin;
* separates extraction orchestration into a service layer;
* isolates strict UTF-8 decoding behind an injectable decoder protocol;
* returns typed, serializable results;
* distinguishes validation, unsupported-format, extraction, size, and infrastructure failures;
* emits operational logs without logging document text or filenames;
* includes deterministic unit and endpoint tests.

The service never accepts or opens a caller-supplied server filesystem location. The uploaded bytes are the document boundary.

The implementation targets **Python 3.13.12** and uses `pip`. The resolved repository dependencies are:

```text
fastapi==0.139.2
pydantic==2.13.4
python-multipart==0.0.32
uvicorn==0.51.0
```

The resolved development dependencies are:

```text
-r requirements.txt
httpx2==2.7.0
mypy==2.3.0
pytest==9.1.1
ruff==0.15.22
```

These dependency versions are taken from the supplied repository requirement files.
The approved Week 1 outline defines the learning scope, upload boundary, exercises, and acceptance criteria. The Codex technical review defines the verified dependency set, corrections, and repository validation results.

No statement in this module claims that ChatGPT executed code, commands, tests, linters, type checking, or URLs. Execution results are included only where they are explicitly attributed to Codex’s technical review.

### Scope boundary

Week 1 does not cover:

* authentication or authorization;
* tenant isolation;
* persistence or databases;
* cloud object storage;
* response-size limits;
* deployment or production server configuration;
* Docker or CI;
* middleware architecture;
* rate limiting;
* caching;
* health checks;
* advanced HTTP streaming;
* production async deployment or concurrency tuning;
* parallel document processing;
* OCR, scanned documents, PDFs, or table extraction;
* queues or background workers;
* LLM calls, prompting, embeddings, RAG, or agent frameworks;
* exhaustive treatment of Python’s object model, typing system, or `asyncio`.

The endpoint returns the complete normalized document text for this learning exercise. A production system would need a separate response-size and data-retention design.

## Learning outcomes

By the end of Week 1, you should be able to:

1. Organize a small FastAPI service into cohesive modules with narrow public interfaces.
2. Explain instance state, class attributes, constructors, instance methods, class methods, static methods, composition, and inheritance.
3. Decide when a class represents useful state or lifecycle and when a module-level function is simpler.
4. Apply type hints that improve static analysis without mistaking annotations for runtime guarantees.
5. Define and use a narrow protocol such as `decode(content: bytes) -> str`.
6. Explain that Pydantic models are Python classes derived from `BaseModel`.
7. Use Pydantic v2 annotated fields, model configuration, field validators, model validators, serialization methods, and appropriate model methods.
8. Choose among plain classes, dataclasses, frozen dataclasses, and Pydantic models according to responsibility and boundary placement.
9. Validate untrusted multipart metadata and return structured, serializable results.
10. Enforce a bounded upload read using a 1 MiB limit plus one sentinel byte.
11. Validate filename suffix, declared media type, upload content type, strict UTF-8 decoding, and non-whitespace content.
12. Design an exception hierarchy that distinguishes validation, unsupported-format, oversized-document, extraction, and infrastructure failures.
13. Translate low-level decoding failures at the boundary where their implementation details become meaningful.
14. Use exception chaining to preserve causal information.
15. Emit useful lifecycle and failure logs without exposing uploaded content, filenames, credentials, or sensitive metadata.
16. Explain iterable, iterator, and generator behavior, including lazy evaluation, single consumption, deferred failure, and resource lifetime.
17. Explain why `UploadFile.read()` is awaited and why that does not make all downstream work automatically non-blocking.
18. Explain when async improves throughput and when blocking or CPU-bound work defeats it.
19. Write deterministic pytest tests using byte-exact inputs.
20. Inspect structured logging fields on captured `LogRecord` objects.
21. Test multipart FastAPI endpoints with `TestClient`.
22. Defend these design choices in a senior engineering interview.

## Prerequisites

### Required knowledge

* Working knowledge of Python syntax.
* Basic JSON knowledge.
* Familiarity with modules, functions, classes, and exceptions is helpful.

The module revisits Python classes explicitly from a production-design perspective. No previous Pydantic, pytest, multipart upload, or production async experience is required.

### Required environment

Use Python 3.13.12.

Confirm the interpreter:

```bash
python --version
```

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

Install the pinned runtime dependencies:

```bash
python -m pip install -r requirements.txt
```

Install the pinned development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

The intended `requirements.txt` content is:

```text
fastapi==0.139.2
pydantic==2.13.4
python-multipart==0.0.32
uvicorn==0.51.0
```

The intended `requirements-dev.txt` content is:

```text
-r requirements.txt
httpx2==2.7.0
mypy==2.3.0
pytest==9.1.1
ruff==0.15.22
```

Dependency responsibilities:

| Dependency         | Scope           | Responsibility                                                                              |
| ------------------ | --------------- | ------------------------------------------------------------------------------------------- |
| `fastapi`          | Runtime         | HTTP application, multipart fields, routing, dependency injection, and response integration |
| `pydantic`         | Runtime         | Runtime validation and serialization of untrusted metadata                                  |
| `python-multipart` | Runtime         | Parsing multipart form requests used by file uploads                                        |
| `uvicorn`          | Runtime tooling | Local ASGI server for manually running the application                                      |
| `pytest`           | Test            | Test discovery, fixtures, parametrization, exception assertions, and log capture            |
| `httpx2`           | Test            | Resolved client implementation used by the pinned Starlette test client                     |
| `ruff`             | Development     | Linting and formatting checks                                                               |
| `mypy`             | Development     | Static type checking in strict mode                                                         |

Python virtual environments are documented at:

https://docs.python.org/3.13/library/venv.html

`pip install` is documented at:

https://pip.pypa.io/en/stable/cli/pip_install/

> **Verification required:** The listed versions were verified together in the repository environment recorded by Codex. Compatibility with a different operating system or a modified dependency set must be checked independently.

## Concept map

```text
Multipart request
├── media_type: form field
├── correlation_id: form field
└── file: UploadFile
          |
          v
Thin async FastAPI route
- validates HTTP-level presence
- awaits bounded UploadFile.read()
- reads at most 1 MiB + 1 byte
- rejects oversized uploads
- never accepts a server filesystem location
          |
          v
Pydantic metadata model
- correlation identifier rules
- declared media-type structure
- filename metadata
- upload content-type metadata
          |
          v
Extraction service
- supported suffix policy
- media-type agreement
- orchestration
- safe lifecycle logging
- low-level failure translation
          |
          +---------------------------+
          |                           |
          v                           v
Decoder Protocol                Pure domain functions
decode(bytes) -> str            - newline normalization
- narrow interface              - line counting
- injectable                    - deterministic
          |
          v
UTF-8 byte decoder
- strict decoding
- exception translation
          |
          v
Frozen domain result
          |
          v
Pydantic response model
- serialization
- response schema
```

Dependency direction:

```text
HTTP layer -> metadata models and service
service -> domain, decoder protocol, and errors
decoder implementation -> decoder protocol and decoder errors
domain -> standard library only
```

The route owns the bounded upload read because `UploadFile.read()` is an HTTP-boundary operation. The service owns document policy and orchestration. The decoder owns byte-to-text conversion. Pure functions own deterministic text transformations.

## Detailed lessons

### 1. Functions, classes, and modules as design tools

#### 1.1 The responsibility test

Before creating a class, ask:

1. Does the concept own state that persists across calls?
2. Does it coordinate one or more dependencies?
3. Does it enforce invariants over an object’s lifetime?
4. Does it represent a substitutable capability?
5. Does construction establish meaningful configuration?

A class is justified when one or more answers are yes.

A module-level function is usually better when the operation:

* is stateless;
* depends only on its arguments;
* has no meaningful construction or lifecycle;
* does not require substitutable implementations;
* is clearer as a deterministic transformation.

For this week:

* `normalize_newlines(text)` is a module-level function.
* `count_logical_lines(text)` is a module-level function.
* `Utf8ByteDecoder` is a class because it implements a replaceable boundary capability.
* `DocumentExtractionService` is a class because it owns a decoder dependency and coordinates extraction.
* `ExtractionCommand` and `ExtractedDocument` are internal dataclasses.
* Multipart metadata and response objects are Pydantic classes because they cross serialization and trust boundaries.

#### 1.2 What a Python class creates

Defining a class creates a new type. Instances can hold instance-specific state, while attributes declared on the class can represent class-wide policy.

```python
from typing import ClassVar


class TextDecoder:
    encoding: ClassVar[str] = "utf-8"

    def __init__(self, errors: str = "strict") -> None:
        self.errors = errors

    def describe(self) -> str:
        return f"encoding={self.encoding}, errors={self.errors}"
```

Here:

* `encoding` is a class attribute.
* `errors` is instance state.
* `__init__` initializes the instance.
* `describe` is an instance method and receives `self`.

```python
strict_decoder = TextDecoder()
replacement_decoder = TextDecoder(errors="replace")
```

The instances share the class-level encoding policy but have different instance state.

Python class fundamentals are documented at:

https://docs.python.org/3.13/tutorial/classes.html

#### 1.3 Avoid mutable class attributes for instance state

Dangerous:

```python
class ExtractionTracker:
    completed_ids: list[str] = []

    def record(self, correlation_id: str) -> None:
        self.completed_ids.append(correlation_id)
```

The list can be shared across every instance.

Prefer:

```python
class ExtractionTracker:
    def __init__(self) -> None:
        self.completed_ids: list[str] = []

    def record(self, correlation_id: str) -> None:
        self.completed_ids.append(correlation_id)
```

Use class attributes for genuine shared policy, not request-specific mutable data.

#### 1.4 Instance methods

An instance method uses instance state or dependencies.

```python
class DocumentExtractionService:
    def __init__(self, decoder: "TextDecoderProtocol") -> None:
        self._decoder = decoder

    def extract_text(self, content: bytes) -> str:
        return self._decoder.decode(content)
```

`extract_text` needs `self` because it uses the injected decoder.

#### 1.5 Class methods

A class method receives the class as `cls`.

Appropriate uses include:

* alternate constructors;
* construction that should preserve subclasses;
* behavior based on overridable class policy.

```python
from typing import Self


class CorrelationId:
    def __init__(self, value: str) -> None:
        self.value = value

    @classmethod
    def from_form_value(cls, raw_value: str) -> Self:
        return cls(raw_value.strip())
```

A class method should not be introduced merely to avoid a module function.

#### 1.6 Static methods

A static method receives neither `self` nor `cls`.

```python
class MediaTypeRules:
    @staticmethod
    def is_plain_text(media_type: str) -> bool:
        return media_type == "text/plain"
```

A module function may communicate this more directly:

```python
def is_plain_text_media_type(media_type: str) -> bool:
    return media_type == "text/plain"
```

Use a static method only when the operation clearly belongs to the class’s conceptual API.

#### 1.7 Composition

Composition means that one object performs its responsibility using another object.

```python
class DocumentExtractionService:
    def __init__(self, decoder: "TextDecoderProtocol") -> None:
        self._decoder = decoder
```

The service **has a decoder**. It is not a specialized decoder.

Composition is appropriate because:

* orchestration and byte decoding are separate responsibilities;
* tests can inject a deterministic fake decoder;
* another decoder can satisfy the same narrow protocol;
* the service does not inherit decoder implementation details.

#### 1.8 Inheritance

Inheritance expresses an “is-a” relationship.

Appropriate uses in this module include:

* Pydantic models inheriting from `BaseModel`;
* application exceptions inheriting from a common service exception;
* specialized extraction errors inheriting from a broader extraction category.

```python
class DocumentServiceError(Exception):
    pass


class UnsupportedDocumentFormatError(DocumentServiceError):
    pass
```

Avoid deep service inheritance hierarchies. They often create hidden coupling and fragile override behavior.

#### 1.9 When a class is unnecessary

Do not write this:

```python
class NewlineNormalizer:
    def normalize(self, text: str) -> str:
        return text.replace("\r\n", "\n").replace("\r", "\n")
```

Prefer:

```python
def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")
```

The operation has no state, dependency, or lifecycle.

#### 1.10 Modules and public interfaces

A cohesive module groups related responsibilities. A narrow interface makes implementation changes easier.

Possible responsibility boundaries:

```text
models.py       multipart metadata and response models
domain.py       commands, results, and pure transformations
ports.py        decoder protocol
decoders.py     strict UTF-8 implementation
errors.py       failure taxonomy
service.py      extraction orchestration
api.py          bounded multipart HTTP route
main.py         application assembly and error mappings
```

Avoid circular dependencies such as:

```text
service imports api
api imports service
```

Prefer:

```text
api imports service
service imports domain, ports, and errors
decoder imports ports and decoder errors
```

**Knowledge check:** Why is newline normalization a function while the extraction service is a class?

---

### 2. Type hints: static information, not runtime enforcement

Type hints describe intended types to readers, editors, and static analyzers. Ordinary annotations do not generally reject incorrect values at runtime.

The `typing` documentation is available at:

https://docs.python.org/3.13/library/typing.html

PEP 484 is available at:

https://peps.python.org/pep-0484/

#### 2.1 Misleading confidence

```python
def character_count(text: str) -> int:
    return len(text)
```

The annotation communicates that callers should provide a string. It does not prevent this runtime call:

```python
result = character_count(["not", "a", "string"])
```

Because lists also support `len`, the function may return `3`. The annotation has not validated the boundary.

#### 2.2 Runtime boundary validation

```python
from pydantic import BaseModel, ConfigDict


class CountRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    text: str
```

Pydantic validates actual runtime input when constructing the model.

Static typing and runtime validation solve different problems:

| Concern                          | Static typing                          | Runtime validation        |
| -------------------------------- | -------------------------------------- | ------------------------- |
| When applied                     | Before execution or during development | During execution          |
| Primary audience                 | Developers and tools                   | Live system boundary      |
| Detects                          | Inconsistent code usage                | Invalid actual input      |
| Guarantees truth                 | No                                     | No                        |
| Prevents malformed runtime shape | Not by itself                          | When correctly configured |

#### 2.3 Useful signatures

```python
def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def count_nonempty_lines(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip())


def decode_document(
    decoder: "TextDecoderProtocol",
    content: bytes,
) -> str:
    return decoder.decode(content)
```

Avoid vague return types:

```python
def extract(content: bytes) -> object:
    ...
```

Prefer a domain result:

```python
def extract(command: "ExtractionCommand") -> "ExtractedDocument":
    ...
```

#### 2.4 Typed collections

Use element types:

```python
documents: list[bytes]
errors_by_id: dict[str, str]
supported_media_types: set[str]
```

Avoid unparameterized forms:

```python
documents: list
errors_by_id: dict
```

#### 2.5 Protocols

A protocol describes behavior without forcing implementation inheritance.

```python
from typing import Protocol


class TextDecoderProtocol(Protocol):
    def decode(self, content: bytes) -> str:
        ...
```

Any compatible object can satisfy the protocol for static analysis:

```python
class FixedDecoder:
    def decode(self, content: bytes) -> str:
        return "fixed text"
```

`FixedDecoder` does not have to inherit from `TextDecoderProtocol`.

Protocol-based structural typing is defined by PEP 544:

https://peps.python.org/pep-0544/

#### 2.6 Containing untyped boundaries

Do not allow unvalidated multipart values or arbitrary dictionaries to flow through the service:

```python
def extract(payload: dict) -> dict:
    ...
```

Prefer converting boundary values into explicit types:

```python
def extract(command: "ExtractionCommand") -> "ExtractedDocument":
    ...
```

The route handles framework objects. Pydantic handles metadata validation. The service receives a typed internal command.

**Knowledge check:** What runtime guarantee does `content: bytes` provide when an arbitrary caller invokes a normal Python function?

---

### 3. Plain classes, dataclasses, frozen dataclasses, and Pydantic models

These constructs overlap syntactically but have different responsibilities.

| Construct                     | Primary responsibility                                  | Automatic trust-boundary validation | Mutation                    | Typical placement                                 |
| ----------------------------- | ------------------------------------------------------- | ----------------------------------- | --------------------------- | ------------------------------------------------- |
| Plain class                   | Behavior, lifecycle, dependencies, state transitions    | No                                  | Developer-controlled        | Services, adapters, stateful collaborators        |
| Dataclass                     | Internal data representation with generated boilerplate | No                                  | Mutable by default          | Commands, internal records, configuration         |
| Frozen dataclass              | Internal value-like representation                      | No                                  | Attribute rebinding blocked | Domain commands and results                       |
| Pydantic `BaseModel` subclass | Parsing, validation, serialization, schema generation   | Yes                                 | Configurable                | HTTP metadata, messages, model outputs, responses |

#### 3.1 Dataclasses

A dataclass is still a Python class. The decorator generates selected methods based on annotated fields.

```python
from dataclasses import dataclass


@dataclass(slots=True)
class ExtractionCommand:
    filename: str
    declared_media_type: str
    upload_media_type: str
    correlation_id: str
    content: bytes
```

A dataclass does not automatically prevent incorrect runtime construction:

```python
command = ExtractionCommand(
    filename=42,
    declared_media_type=[],
    upload_media_type=None,
    correlation_id={},
    content="not bytes",
)
```

A static analyzer may reject this, but runtime validation is a separate responsibility.

Dataclasses are documented at:

https://docs.python.org/3.13/library/dataclasses.html

PEP 557 is available at:

https://peps.python.org/pep-0557/

#### 3.2 Frozen dataclasses and shallow immutability

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExtractedDocument:
    correlation_id: str
    text: str
    tags: list[str]
```

Attribute rebinding is blocked:

```python
# document.text = "replacement"
```

Nested mutation may still be possible:

```python
document.tags.append("still mutable")
```

This is shallow immutability.

For stronger value semantics:

```python
@dataclass(frozen=True, slots=True)
class SaferExtractedDocument:
    correlation_id: str
    text: str
    tags: tuple[str, ...]
```

Aliasing matters in AI pipelines because retrieval, ranking, prompting, evaluation, and logging components may share references to the same mutable object. Mutation by one component changes what the others observe.

#### 3.3 Pydantic models are Python classes

A Pydantic model is a Python class derived from `pydantic.BaseModel`.

```python
from pydantic import BaseModel, ConfigDict, Field


class UploadMetadata(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    filename: str = Field(min_length=1, max_length=255)
    media_type: str = Field(min_length=1, max_length=128)
    upload_content_type: str = Field(min_length=1, max_length=128)
    correlation_id: str = Field(min_length=1, max_length=64)
```

Inheritance relationship:

```text
UploadMetadata -> BaseModel -> Python object
```

Pydantic uses classes because the model class declares:

* fields;
* validation constraints;
* model configuration;
* field validators;
* model validators;
* schema behavior;
* serialization behavior;
* construction methods.

This does not imply that stateless domain transformations should become classes.

Pydantic model documentation:

https://docs.pydantic.dev/latest/concepts/models/

#### 3.4 Annotated fields

```python
from pydantic import Field


class UploadLimits(BaseModel):
    maximum_bytes: int = Field(gt=0, le=1_048_576)
```

The annotation communicates the target type. `Field` adds runtime constraints and schema metadata.

#### 3.5 Model configuration

Pydantic v2 commonly uses `ConfigDict` through `model_config`.

```python
from pydantic import BaseModel, ConfigDict


class StrictBoundaryModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        frozen=True,
    )
```

Typical meanings:

* `extra="forbid"` rejects undeclared fields.
* `strict=True` reduces coercion.
* `frozen=True` blocks normal field assignment after construction.

Strictness can vary by type and input mode. Confirm behavior against the installed Pydantic version.

Pydantic configuration:

https://docs.pydantic.dev/latest/concepts/config/

Pydantic strict mode:

https://docs.pydantic.dev/latest/concepts/strict_mode/

#### 3.6 Field validators

A field validator handles a rule primarily associated with one field.

```python
import re

from pydantic import BaseModel, field_validator


_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class CorrelatedUpload(BaseModel):
    correlation_id: str

    @field_validator("correlation_id")
    @classmethod
    def validate_correlation_id(cls, value: str) -> str:
        if _SAFE_ID.fullmatch(value) is None:
            raise ValueError(
                "correlation_id contains unsupported characters"
            )
        return value
```

Avoid validators that:

* read the uploaded stream;
* perform network calls;
* mutate global state;
* log rejected sensitive values;
* perform extraction orchestration;
* silently rewrite security-sensitive identifiers.

Pydantic validators:

https://docs.pydantic.dev/latest/concepts/validators/

#### 3.7 Model validators

A model validator handles relationships among fields.

```python
from typing import Self

from pydantic import BaseModel, model_validator


class MediaTypeDeclaration(BaseModel):
    declared_media_type: str
    upload_content_type: str

    @model_validator(mode="after")
    def require_matching_media_types(self) -> Self:
        if self.declared_media_type != self.upload_content_type:
            raise ValueError("media types must match")
        return self
```

Whether media-type agreement belongs in a Pydantic model or the service depends on the verified repository boundary. Do not duplicate the same policy in several layers.

#### 3.8 Serialization

Important Pydantic v2 methods include:

* `model_dump()`;
* `model_dump_json()`;
* `model_validate()`;
* `model_validate_json()`;
* `model_json_schema()`.

```python
metadata = UploadMetadata(
    filename="notes.txt",
    media_type="text/plain",
    upload_content_type="text/plain",
    correlation_id="job-123",
)

payload = metadata.model_dump()
```

Serialization documentation:

https://docs.pydantic.dev/latest/concepts/serialization/

#### 3.9 Appropriate custom model methods

A model method should remain closely related to model conversion or presentation.

```python
from typing import Self


class ExtractionResponse(BaseModel):
    correlation_id: str
    text: str
    character_count: int

    @classmethod
    def from_domain(
        cls,
        result: "ExtractedDocument",
    ) -> Self:
        return cls(
            correlation_id=result.correlation_id,
            text=result.text,
            character_count=result.character_count,
        )
```

Reading an upload, decoding bytes, or invoking an LLM inside `from_domain` would mix responsibilities.

**Knowledge check:** Why should validated multipart metadata be converted into an internal dataclass before orchestration?

---

### 4. Exception design and translation

#### 4.1 Exceptions are part of the interface

A caller needs stable categories it can handle.

A suitable conceptual hierarchy is:

```text
DocumentServiceError
├── DocumentValidationError
├── UnsupportedDocumentFormatError
├── DocumentTooLargeError
├── DocumentExtractionError
│   ├── DocumentDecodingError
│   └── EmptyDocumentError
└── DocumentInfrastructureError
```

The exact repository definitions must come from the verified source files.

#### 4.2 Size failure belongs to the upload boundary

The route reads:

```text
1_048_576 bytes + 1 sentinel byte
```

If the result contains more than 1,048,576 bytes, the route returns:

```text
HTTP 413
code: document_too_large
```

The sentinel byte proves that the payload exceeds the accepted maximum without requesting an unbounded read.

#### 4.3 Translate at abstraction boundaries

The UTF-8 decoder understands `UnicodeDecodeError`.

The extraction service understands a document decoding failure.

The HTTP layer understands stable status codes and error bodies.

Illustrative adapter translation:

```python
class DecoderDecodingError(Exception):
    pass


class Utf8ByteDecoder:
    def decode(self, content: bytes) -> str:
        try:
            return content.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise DecoderDecodingError(
                "uploaded content is not valid UTF-8"
            ) from exc
```

Illustrative service translation:

```python
try:
    text = decoder.decode(command.content)
except DecoderDecodingError as exc:
    raise DocumentDecodingError(
        "document is not valid UTF-8",
        correlation_id=command.correlation_id,
    ) from exc
```

Each layer uses vocabulary meaningful to its caller. `from exc` preserves the original cause.

Python exception chaining:

https://docs.python.org/3.13/tutorial/errors.html

#### 4.4 Preserve context without leaking payloads

Unsafe:

```python
raise DocumentExtractionError(
    f"Could not extract {filename}: {raw_text}"
)
```

Safer:

```python
raise DocumentExtractionError(
    "document extraction failed",
    correlation_id=correlation_id,
)
```

Do not attach uploaded bytes, decoded text, or filename to public exceptions.

#### 4.5 Avoid broad suppression

Dangerous:

```python
try:
    return decoder.decode(content)
except Exception:
    return ""
```

This turns defects and infrastructure failures into apparently valid empty documents.

Prefer:

* catching specific expected failures;
* translating only when the current boundary adds meaning;
* preserving causal context;
* allowing unknown programming defects to remain visible.

#### 4.6 Cleanup

`UploadFile` owns an underlying upload resource managed by the framework. The route should avoid retaining it beyond the request lifecycle.

This week’s service accepts bounded bytes and does not own the upload stream. Advanced upload streaming and lifecycle tuning are outside scope.

**Knowledge check:** Why should the service not catch a FastAPI-specific upload exception directly?

---

### 5. Operational logging

#### 5.1 Module-level logger

```python
import logging

logger = logging.getLogger(__name__)
```

Application startup or the process runner decides formatting, handlers, destinations, and severity thresholds. Reusable modules should not configure the root logger.

Python logging documentation:

https://docs.python.org/3.13/howto/logging.html

https://docs.python.org/3.13/library/logging.html

#### 5.2 Useful events

Useful extraction fields include:

* event name;
* safe correlation identifier;
* declared media type;
* upload content type;
* stable failure code;
* byte count;
* character count;
* line count;
* elapsed time when measured through a deliberately isolated clock.

Do not log:

* uploaded bytes;
* decoded text;
* filename;
* complete multipart request objects;
* credentials;
* personal information;
* arbitrary metadata dictionaries;
* unreviewed low-level exception messages.

#### 5.3 Structured context

```python
logger.info(
    "document_extraction_started",
    extra={
        "correlation_id": correlation_id,
        "media_type": media_type,
        "byte_count": len(content),
    },
)
```

Fields provided through `extra` become attributes on the `LogRecord`.

They are **not guaranteed** to appear in `caplog.text`. The active formatter decides which record attributes are rendered.

A correct test inspects records:

```python
correlation_ids = [
    getattr(record, "correlation_id", None)
    for record in caplog.records
]

assert "request-123" in correlation_ids
```

#### 5.4 Levels

| Level      | Appropriate use                                               |
| ---------- | ------------------------------------------------------------- |
| `DEBUG`    | Internal diagnostic details that are safe for restricted logs |
| `INFO`     | Normal lifecycle events                                       |
| `WARNING`  | Expected request-specific failure with operational value      |
| `ERROR`    | Serious failure preventing the operation                      |
| `CRITICAL` | Process-wide or service-wide failure                          |

An unsupported format or oversized request can be a warning because the system handled it deliberately.

#### 5.5 Exception traces

Use `logger.exception` inside an active exception handler when the traceback adds operational value:

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

Do not include the filename or content in the event message.

**Knowledge check:** Why should tests inspect `caplog.records` for structured fields?

---

### 6. Iterables, iterators, and generators

#### 6.1 Mental model

An **iterable** can produce an iterator.

An **iterator** produces values one at a time and tracks traversal state.

A **generator** is a concise iterator implementation using `yield`.

```python
values = ["a", "b", "c"]
iterator = iter(values)
first = next(iterator)
```

Python iterator and generator documentation:

https://docs.python.org/3.13/tutorial/classes.html#iterators

https://peps.python.org/pep-0255/

#### 6.2 Lazy logical-line generator

The current endpoint returns the complete bounded text and does not implement HTTP streaming. A generator can still illustrate lazy logical-line processing after newline normalization.

```python
from collections.abc import Iterator
from io import StringIO


def iter_logical_lines(text: str) -> Iterator[str]:
    with StringIO(text) as stream:
        for line in stream:
            yield line.rstrip("\n")
```

Work happens as the caller requests values.

#### 6.3 Single consumption

```python
lines = iter_logical_lines("alpha\nbeta")

first_pass = list(lines)
second_pass = list(lines)

assert first_pass == ["alpha", "beta"]
assert second_pass == []
```

The generator is exhausted after one complete pass.

A stored list is repeatable but consumes memory for all values.

#### 6.4 Trade-offs

Generators may:

* reduce peak memory;
* provide the first value earlier;
* avoid unnecessary work if iteration stops early.

They may also:

* defer exceptions;
* prevent repeated traversal;
* complicate retries;
* keep resources alive while suspended;
* move failure timing away from function invocation.

#### 6.5 Deferred failure

```python
generator = iter_logical_lines(text)
```

Creating a generator does not necessarily execute its body. A failure may occur during `next(generator)` rather than during construction.

#### 6.6 Resource lifetime

A generator can hold a file, network response, database cursor, or in-memory stream while suspended around `yield`.

The current implementation avoids exposing an upload-backed generator. The route performs one bounded awaitable read and passes bytes into the service.

**Knowledge check:** Why can a list produce simpler retry behavior than a partially consumed generator?

---

### 7. Async fundamentals

#### 7.1 Cooperative concurrency

`asyncio` supports cooperative concurrency through `async` and `await`.

https://docs.python.org/3.13/library/asyncio.html

Async is useful when:

* operations spend time waiting;
* dependencies expose awaitable APIs;
* concurrency is bounded;
* cancellation and cleanup are handled deliberately.

Async does not make arbitrary work faster.

#### 7.2 Why the route is `async def`

FastAPI’s `UploadFile.read()` is awaitable.

The thin route therefore uses:

```python
content = await file.read(MAX_UPLOAD_BYTES + 1)
```

The route is asynchronous because it awaits the upload read. This is an HTTP-boundary decision.

The route should not perform an unbounded read:

```python
content = await file.read()
```

The bounded form reads at most:

```text
1,048,577 bytes
```

That is the accepted 1 MiB plus one sentinel byte.

FastAPI upload documentation:

https://fastapi.tiangolo.com/tutorial/request-files/

FastAPI forms-and-files documentation:

https://fastapi.tiangolo.com/tutorial/request-forms-and-files/

#### 7.3 Awaitable does not mean CPU work is faster

After the upload is read, strict UTF-8 decoding and text normalization are ordinary synchronous operations over a bounded payload.

Changing a synchronous function to `async def` does not automatically make it concurrent or faster.

#### 7.4 Blocking work inside async code

Bad conceptual pattern:

```python
async def process_bad() -> str:
    return blocking_library_call()
```

The function is syntactically async, but the blocking call can still prevent the event loop from progressing.

The Week 1 endpoint does not introduce production concurrency tuning, custom executors, or worker pools.

#### 7.5 CPU-bound work

CPU-heavy parsing or transformation does not become faster merely because it runs in a coroutine. Depending on the workload, processes, native libraries, external workers, or sequential execution may be more appropriate.

Python executor documentation:

https://docs.python.org/3.13/library/concurrent.futures.html

#### 7.6 Cancellation and cleanup

A coroutine may be cancelled while awaiting.

```python
async def use_resource(resource: "AsyncResource") -> None:
    await resource.open()
    try:
        await resource.process()
    finally:
        await resource.close()
```

Do not swallow cancellation through broad exception handling.

#### 7.7 Threads versus async

| Concern               | Async                               | Threads                                   |
| --------------------- | ----------------------------------- | ----------------------------------------- |
| Best fit              | Awaitable I/O                       | Blocking libraries or I/O                 |
| Scheduling            | Cooperative                         | Runtime or operating-system managed       |
| Shared state          | Same process and event-loop context | Same process with concurrent access       |
| Cancellation          | Structured but dependency-sensitive | Running calls are often difficult to stop |
| Backpressure          | Must be designed                    | Worker and queue capacity must be bounded |
| Debugging             | Tasks and event-loop context        | Thread stacks and races                   |
| CPU-heavy pure Python | Usually not accelerated             | Usually not a reliable parallel speedup   |
| Integration           | Requires awaitable APIs             | Can bridge synchronous APIs               |

**Knowledge check:** Why is awaiting `UploadFile.read()` appropriate without making the extraction service asynchronous?

---

### 8. Reusable and testable design

#### 8.1 Separate deterministic logic from adapters

Pure function:

```python
def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")
```

Decoder adapter:

```python
class Utf8ByteDecoder:
    def decode(self, content: bytes) -> str:
        ...
```

The pure function is tested with strings. The decoder is tested with exact byte payloads.

#### 8.2 Inject the decoder boundary

```python
class DocumentExtractionService:
    def __init__(self, decoder: TextDecoderProtocol) -> None:
        self._decoder = decoder
```

Avoid constructing the decoder inside every extraction call:

```python
class DocumentExtractionService:
    def extract(self, content: bytes) -> str:
        decoder = Utf8ByteDecoder()
        return decoder.decode(content)
```

Explicit injection makes deterministic failure simulation easier.

#### 8.3 Keep interfaces small

The required decoder interface has one method:

```python
class TextDecoderProtocol(Protocol):
    def decode(self, content: bytes) -> str:
        ...
```

Do not add registration, discovery, priorities, hooks, or plugin lifecycle behavior before there is a concrete need.

#### 8.4 Keep the route thin

The route’s responsibilities are limited to:

1. receive multipart fields;
2. await the bounded upload read;
3. reject a payload above 1 MiB;
4. construct validated metadata;
5. create a domain command;
6. call the service;
7. return the typed response.

Filename, media-type, decoding, empty-content, normalization, and logging policies should not all be reimplemented in the route.

#### 8.5 Test observable behavior

Prefer:

```python
assert result.text == "expected"
```

Use interaction assertions only when the interaction is itself part of the contract.

A fake decoder is preferable to mocking every internal method.

---

### 9. Pytest fundamentals

#### 9.1 Arrange–act–assert

```python
def test_normalize_newlines() -> None:
    source = "a\r\nb\rc"

    result = normalize_newlines(source)

    assert result == "a\nb\nc"
```

#### 9.2 Byte-exact fixtures

When exact newline bytes matter, use direct byte values:

```python
content = b"alpha\r\nbeta\rgamma"
```

Do not depend on text-mode newline translation.

This matters particularly on Windows, where writing text can translate newline sequences according to text-mode behavior.

#### 9.3 Exception assertions

```python
import pytest


def test_invalid_utf8_is_rejected() -> None:
    decoder = Utf8ByteDecoder()

    with pytest.raises(DecoderDecodingError):
        decoder.decode(b"\xff\xfe\xfa")
```

Use the narrowest expected exception.

#### 9.4 Parametrization

```python
import pytest


@pytest.mark.parametrize(
    ("declared_type", "upload_type", "is_supported"),
    [
        ("text/plain", "text/plain", True),
        ("application/pdf", "application/pdf", False),
        ("text/plain", "application/pdf", False),
    ],
)
def test_media_type_policy(
    declared_type: str,
    upload_type: str,
    is_supported: bool,
) -> None:
    assert (
        is_supported_media_type_pair(
            declared_type,
            upload_type,
        )
        is is_supported
    )
```

pytest parametrization:

https://docs.pytest.org/en/stable/how-to/parametrize.html

#### 9.5 Captured logs

```python
import logging

import pytest


def test_document_text_is_not_logged(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(
        logging.INFO,
        logger="document_service.service",
    ):
        ...
```

Check forbidden payloads in rendered text:

```python
assert secret_text not in caplog.text
assert secret_filename not in caplog.text
```

Check structured fields on records:

```python
assert any(
    getattr(record, "correlation_id", None)
    == "safe-correlation-123"
    for record in caplog.records
)
```

pytest logging documentation:

https://docs.pytest.org/en/stable/how-to/logging.html

#### 9.6 Multipart endpoint tests

A multipart endpoint test supplies normal form fields separately from the file tuple:

```python
response = client.post(
    "/v1/documents/extract",
    data={
        "media_type": "text/plain",
        "correlation_id": "request-123",
    },
    files={
        "file": (
            "sample.txt",
            b"alpha\r\nbeta",
            "text/plain",
        )
    },
)
```

This directly controls the filename, payload bytes, and upload content type.

#### 9.7 Mock only external boundaries

Good fake boundaries include:

* decoder;
* model client;
* network client;
* repository;
* clock.

Usually do not mock:

* newline normalization;
* simple dataclass construction;
* Pydantic serialization;
* small domain rules.

---

### 10. FastAPI boundary fundamentals

The endpoint contract is multipart, not JSON.

Required multipart fields:

| Field            | Kind       | Meaning                                       |
| ---------------- | ---------- | --------------------------------------------- |
| `media_type`     | Form field | Caller-declared document media type           |
| `correlation_id` | Form field | Safe external request identifier              |
| `file`           | File field | Uploaded document represented by `UploadFile` |

The route should:

* receive `media_type`;
* receive `correlation_id`;
* receive `file`;
* await `file.read(1_048_577)`;
* reject a result longer than 1,048,576 bytes;
* map the size failure to HTTP `413`;
* construct validated metadata;
* invoke the extraction service;
* return a response model.

The service should:

* require filename suffix `.txt`;
* require declared media type `text/plain`;
* require upload content type `text/plain`;
* require agreement between the declared and upload media types;
* invoke the decoder;
* reject non-whitespace-free emptiness;
* normalize newlines;
* construct a domain result;
* emit safe logs.

The decoder should:

* accept `bytes`;
* decode with UTF-8;
* use strict error handling;
* translate `UnicodeDecodeError`;
* avoid logging content.

FastAPI dependency injection:

https://fastapi.tiangolo.com/tutorial/dependencies/

FastAPI routers:

https://fastapi.tiangolo.com/tutorial/bigger-applications/

FastAPI error handling:

https://fastapi.tiangolo.com/tutorial/handling-errors/

FastAPI response models:

https://fastapi.tiangolo.com/tutorial/response-model/

FastAPI testing:

https://fastapi.tiangolo.com/tutorial/testing/

Starlette test client:

https://starlette.dev/testclient/

## Production considerations

### Upload trust boundary

All multipart values are untrusted:

* `media_type`;
* `correlation_id`;
* uploaded filename;
* upload content type;
* uploaded bytes.

Successful multipart parsing does not prove that:

* the media-type declaration is accurate;
* the filename suffix is supported;
* the bytes are UTF-8;
* the text is meaningful;
* the upload is within the application limit;
* the content is safe to persist or return.

Each guarantee needs an explicit check.

### Fixed upload-size limit

The accepted maximum is:

```text
1 MiB = 1,048,576 bytes
```

The route requests at most:

```text
1,048,577 bytes
```

The extra byte is a sentinel. Its presence proves the upload exceeds the maximum.

A document at exactly 1,048,576 bytes is within the fixed limit. A document with at least 1,048,577 bytes is rejected with:

```text
HTTP 413
code: document_too_large
```

Making the limit configurable remains an exercise. The bounded-read guarantee must remain mandatory.

### Filename handling

The filename is used only as untrusted metadata for suffix validation.

The application must not:

* treat it as a local location;
* open it;
* join it to an application directory;
* persist it without a separate design;
* include it in logs.

The contract requires suffix `.txt`. Case-handling must follow the verified repository implementation when its source files are integrated.

### Media-type agreement

A supported upload requires:

```text
declared media type: text/plain
upload content type: text/plain
filename suffix: .txt
```

A mismatch is rejected. The service should not infer support from only one of these signals.

Media types are metadata, not proof that the bytes are actually text. Strict UTF-8 decoding remains necessary.

### Encoding

Decode using UTF-8 strict behavior:

```python
content.decode("utf-8", errors="strict")
```

Do not use `errors="ignore"` at a trust boundary. Ignoring undecodable bytes can silently alter meaning.

### Empty content

A zero-byte upload is invalid.

A document containing only whitespace is also invalid after decoding and newline normalization.

The stable error category should distinguish empty content from unsupported format and invalid UTF-8.

### Normalization

Allowed normalization:

* `\r\n` becomes `\n`;
* remaining `\r` becomes `\n`.

The service does not silently:

* trim meaningful leading or trailing whitespace;
* collapse spaces;
* lowercase text;
* remove punctuation;
* rewrite Unicode;
* remove a byte-order mark unless explicitly specified;
* interpret Markdown;
* parse tables.

### Error stability

Clients should receive stable codes such as:

* `document_too_large`;
* `unsupported_document_format`;
* `document_decoding_failed`;
* `empty_document`;
* `document_validation_failed`;
* `document_infrastructure_failure`.

Clients should not parse raw Python exception messages.

### Sensitive logging

Never log:

* uploaded bytes;
* decoded text;
* filename;
* complete multipart objects;
* credentials;
* PII;
* arbitrary metadata;
* raw validation inputs.

Useful logs can contain:

* safe correlation identifier;
* event name;
* declared media type;
* upload content type;
* byte count;
* character count;
* line count;
* stable failure code.

### Dependency management

The repository pins direct dependencies but does not provide a hash-locked record of every transitive package.

A production dependency process would additionally consider:

* transitive locking;
* reproducible builds;
* vulnerability review;
* controlled upgrades;
* release-note review.

Those activities are outside Week 1 implementation scope.

### Async route boundary

The route is `async def` because `UploadFile.read()` is awaitable.

This does not imply that:

* decoding is asynchronous;
* normalization is asynchronous;
* CPU-heavy parsing should run on the event loop;
* deployment concurrency has been tuned.

Production async deployment and concurrency tuning remain outside scope.

### Response size

The input is bounded at 1 MiB, but the endpoint still returns complete normalized text. Response-size policy is explicitly outside Week 1 scope.

### Persistence

The service does not persist the upload. Database storage, object storage, retention, and deletion policies are outside scope.

### Authentication and authorization

The service does not decide who may upload or retrieve a document. Authentication, authorization, and tenant isolation are outside scope.

### Import boundaries

Recommended direction:

```text
main/api -> models/service
service -> domain/ports/errors
decoder -> ports/decoder errors
domain -> standard library only
```

### No speculative parser framework

The first implementation supports one format. Exercise 1 adds Markdown text using the smallest clear design change. It should not create dynamic plugin discovery.

## Common failure modes

### 1. Accepting a server location from the caller

This exposes the server process’s file permissions and creates an unsafe contract.

**Correction:** Accept uploaded bytes through `UploadFile`.

### 2. Reading the upload without a bound

```python
content = await file.read()
```

This permits the application to retain an arbitrarily large request body.

**Correction:**

```python
content = await file.read(MAX_UPLOAD_BYTES + 1)
```

Reject content longer than the accepted maximum.

### 3. Reading only the maximum without a sentinel

```python
content = await file.read(MAX_UPLOAD_BYTES)
```

This does not distinguish an exactly-at-limit document from the prefix of a larger document.

**Correction:** Read one additional sentinel byte.

### 4. Trusting only the filename

A `.txt` suffix does not prove that the declaration, upload content type, or bytes are valid.

**Correction:** Check suffix, both media types, strict UTF-8 decoding, and non-whitespace content.

### 5. Trusting only the upload content type

Multipart content type is caller-controlled metadata.

**Correction:** Treat it as one validation signal rather than proof.

### 6. Treating type annotations as runtime validation

```python
def extract(content: bytes) -> str:
    ...
```

This does not stop an arbitrary runtime caller from passing another value.

**Correction:** Validate untrusted boundary values before creating trusted internal objects.

### 7. Using dataclasses as untrusted boundary validators

Dataclasses do not automatically enforce runtime types.

**Correction:** Use a Pydantic boundary model, then convert to domain dataclasses.

### 8. Using Pydantic for all internal values

This unnecessarily couples domain logic to a serialization library.

**Correction:** Use Pydantic at boundaries and dataclasses for internal values where appropriate.

### 9. Assuming frozen means deeply immutable

Nested lists and dictionaries may remain mutable.

**Correction:** Use immutable nested types or defensive copying.

### 10. Shared mutable class attributes

Request-specific state declared at class scope may be shared across instances.

**Correction:** Initialize mutable instance state in `__init__`.

### 11. Unnecessary service inheritance

Making the service inherit from the decoder confuses “uses” with “is.”

**Correction:** Compose the service with an injected decoder.

### 12. Catching every exception and returning empty text

This hides programming defects and infrastructure failures.

**Correction:** Catch only failures that the current layer can translate meaningfully.

### 13. Losing the causal exception

```python
except UnicodeDecodeError:
    raise DecoderDecodingError("invalid UTF-8")
```

**Correction:**

```python
except UnicodeDecodeError as exc:
    raise DecoderDecodingError("invalid UTF-8") from exc
```

### 14. Logging uploaded text or filename

```python
logger.error(
    "failed filename=%s text=%s",
    filename,
    text,
)
```

**Correction:** Log a safe correlation ID and stable failure code.

### 15. Assuming `extra` appears in `caplog.text`

Structured fields are record attributes. A formatter may omit them.

**Correction:** Inspect `caplog.records`.

### 16. Using text-mode fixtures for exact newline bytes

Platform newline translation can change the actual bytes.

**Correction:** Use direct byte payloads or `write_bytes()` when a real file fixture is independently needed.

The verified upload-oriented tests use direct byte payloads rather than filesystem fixtures.

### 17. Making the whole service asynchronous

Only the upload read must be awaited. Converting deterministic decoding and normalization into coroutines adds complexity without benefit.

**Correction:** Keep async at the HTTP boundary unless downstream APIs are genuinely awaitable.

### 18. Returning a generator without defining ownership

The caller may assume repeatability or immediate failure.

**Correction:** Document lazy execution, single consumption, deferred errors, and resource lifetime.

### 19. Mocking every internal function

A test built entirely from mocks proves little about real behavior.

**Correction:** Use fakes at the decoder boundary and exercise real service logic.

### 20. Asserting complete framework validation payloads

Third-party validation response details can change.

**Correction:** Assert stable status codes and application-owned error contracts.

### 21. Adding a generic parser plugin system

A registry, hooks, priorities, and discovery logic are speculative with one or two formats.

**Correction:** Add the smallest explicit abstraction that handles demonstrated requirements.

## Worked examples

The following examples are pedagogical illustrations. They are not claimed to be exact copies of the verified repository files and were not executed by ChatGPT.

### Example 1: Misleading type hint versus runtime validation

Type hint only:

```python
def normalize_title(title: str) -> str:
    return title.strip()
```

Runtime validation:

```python
from pydantic import BaseModel, ConfigDict


class TitleRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    title: str
```

**Production conclusion:** Type hints improve static reasoning. Runtime validation protects the live boundary.

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
# frozen.document_ids = ["b"]

frozen.document_ids.append("b")
```

Safer nested value:

```python
@dataclass(frozen=True)
class ImmutableBatch:
    document_ids: tuple[str, ...]
```

**Production conclusion:** Frozen dataclasses provide shallow rather than recursive immutability.

---

### Example 3: Pydantic validation at an upload boundary

```python
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class UploadMetadata(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        frozen=True,
    )

    filename: str = Field(min_length=1, max_length=255)
    media_type: str = Field(min_length=1, max_length=128)
    upload_content_type: str = Field(min_length=1, max_length=128)
    correlation_id: str = Field(min_length=1, max_length=64)

    @field_validator("correlation_id")
    @classmethod
    def validate_correlation_id(cls, value: str) -> str:
        if _SAFE_ID.fullmatch(value) is None:
            raise ValueError("invalid correlation_id")
        return value
```

Successful model construction proves that the metadata satisfies the declared schema. It does not prove that the uploaded bytes are UTF-8 or semantically truthful.

---

### Example 4: Plain class, dataclass, and Pydantic inheritance

Plain class with state:

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

Internal value:

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

`RetryRequest` inherits from `BaseModel`. `RetryDecision` is a dataclass. `RetryCounter` is a manually implemented stateful class.

---

### Example 5: Exception translation and chaining

Decoder boundary:

```python
class DecoderDecodingError(Exception):
    pass


class Utf8ByteDecoder:
    def decode(self, content: bytes) -> str:
        try:
            return content.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise DecoderDecodingError(
                "uploaded content is not valid UTF-8"
            ) from exc
```

Service boundary:

```python
try:
    text = decoder.decode(content)
except DecoderDecodingError as exc:
    raise DocumentDecodingError(
        "document is not valid UTF-8",
        correlation_id=correlation_id,
    ) from exc
```

**Production conclusion:** Translate into the caller’s vocabulary and preserve the original cause.

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
    "document_extraction_completed filename=%s text=%s",
    filename,
    text,
)
```

Correct record-oriented test:

```python
assert any(
    getattr(record, "correlation_id", None)
    == correlation_id
    for record in caplog.records
)
```

**Production conclusion:** Log lifecycle and dimensions, not payloads or filenames.

---

### Example 7: Generator processing logical lines

```python
from collections.abc import Iterator
from io import StringIO


def iter_logical_lines(text: str) -> Iterator[str]:
    with StringIO(text) as stream:
        for line in stream:
            yield line.rstrip("\n")
```

Single consumption:

```python
lines = iter_logical_lines("alpha\nbeta")

first = list(lines)
second = list(lines)

assert first == ["alpha", "beta"]
assert second == []
```

The generator is lazy and single-use.

---

### Example 8: Awaitable upload I/O versus blocking or CPU work

Awaitable upload read:

```python
MAX_UPLOAD_BYTES = 1_048_576

content = await file.read(MAX_UPLOAD_BYTES + 1)
```

Synchronous bounded decoding:

```python
text = decoder.decode(content)
```

CPU-heavy work does not become faster merely because it is called from an async route.

**Production conclusion:** Keep async where the API is genuinely awaitable.

---

### Example 9: Behavior-focused pytest test with byte-exact content

```python
def test_decoder_preserves_valid_utf8() -> None:
    content = "भारत\r\nAI".encode("utf-8")
    decoder = Utf8ByteDecoder()

    result = decoder.decode(content)

    assert result == "भारत\r\nAI"
```

Newline normalization can be tested separately:

```python
def test_normalize_windows_and_classic_newlines() -> None:
    source = b"alpha\r\nbeta\rgamma".decode("utf-8")

    assert normalize_newlines(source) == "alpha\nbeta\ngamma"
```

The payload bytes are deterministic across operating systems.

---

### Example 10: FastAPI endpoint test with `TestClient`

```python
from fastapi.testclient import TestClient


def test_extract_endpoint_returns_typed_result() -> None:
    app = create_app()

    with TestClient(app) as client:
        response = client.post(
            "/v1/documents/extract",
            data={
                "media_type": "text/plain",
                "correlation_id": "request-123",
            },
            files={
                "file": (
                    "sample.txt",
                    b"alpha\r\nbeta",
                    "text/plain",
                )
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

Oversized endpoint behavior:

```python
def test_extract_endpoint_rejects_oversized_document() -> None:
    app = create_app()
    content = b"a" * (1_048_576 + 1)

    with TestClient(app) as client:
        response = client.post(
            "/v1/documents/extract",
            data={
                "media_type": "text/plain",
                "correlation_id": "request-large-1",
            },
            files={
                "file": (
                    "large.txt",
                    content,
                    "text/plain",
                )
            },
        )

    assert response.status_code == 413
    assert response.json()["code"] == "document_too_large"
```

These examples show the required contract but are not asserted to reproduce the verified repository source exactly.

## Guided implementation

The verified `document_service/` source files were not included with the attached review inputs. Exact repository code must therefore not be reconstructed from inference.

Where verified source content belongs, this section uses the required marker:

**Codex integration required**

### 1. Repository structure

The implementation should preserve distinct responsibilities for:

* FastAPI routing;
* application construction;
* multipart metadata validation;
* domain command and result types;
* exception definitions;
* the decoder protocol;
* strict UTF-8 decoding;
* extraction orchestration;
* dependency construction.

Exact verified tree:

**Codex integration required**

### 2. Runtime requirements

The attached verified runtime requirements are:

```text
fastapi==0.139.2
pydantic==2.13.4
python-multipart==0.0.32
uvicorn==0.51.0
```

### 3. Development requirements

The attached verified development requirements are:

```text
-r requirements.txt
httpx2==2.7.0
mypy==2.3.0
pytest==9.1.1
ruff==0.15.22
```

### 4. Error definitions

The verified repository error source must include stable categories for:

* metadata validation;
* unsupported format;
* oversized document;
* UTF-8 decoding;
* empty content;
* extraction failure;
* infrastructure failure.

Exact verified source:

**Codex integration required**

### 5. Domain values and pure transformations

The verified domain source must define typed internal commands and results and deterministic newline and line-count behavior.

Exact verified source:

**Codex integration required**

### 6. Decoder protocol

The required narrow protocol is:

```text
decode(content: bytes) -> str
```

Exact verified source:

**Codex integration required**

### 7. UTF-8 decoder implementation

The verified decoder must:

* accept bytes;
* use strict UTF-8;
* translate `UnicodeDecodeError`;
* preserve causal context;
* avoid logging content.

Exact verified source:

**Codex integration required**

### 8. Pydantic metadata and response models

The verified models must cover:

* multipart metadata;
* safe correlation identifiers;
* filename metadata;
* declared media type;
* upload content type;
* response serialization;
* stable error serialization.

Exact verified source:

**Codex integration required**

### 9. Extraction service

The verified service must:

* validate filename suffix `.txt`;
* require declared media type `text/plain`;
* require upload content type `text/plain`;
* require matching media types;
* invoke the injected decoder;
* normalize newlines;
* reject whitespace-only content;
* create the typed result;
* log lifecycle and failure events safely.

Exact verified source:

**Codex integration required**

### 10. Dependency construction

The verified dependency assembly must construct the UTF-8 decoder and inject it into the service.

Exact verified source:

**Codex integration required**

### 11. Thin multipart route

The verified route contract is:

```text
POST /v1/documents/extract

multipart fields:
- media_type
- correlation_id
- file
```

The route must:

* be declared with `async def`;
* receive `UploadFile`;
* await a read of at most 1 MiB plus one sentinel byte;
* return HTTP `413` with `document_too_large` when exceeded;
* avoid decoding and extraction business rules;
* invoke the service;
* return a typed response.

Exact verified source:

**Codex integration required**

### 12. Application and error mappings

The verified application must map domain errors to stable HTTP responses, including:

| Condition                        | HTTP status | Stable code                                  |
| -------------------------------- | ----------: | -------------------------------------------- |
| Oversized upload                 |         413 | `document_too_large`                         |
| Unsupported suffix or media type |         415 | `unsupported_document_format`                |
| Invalid UTF-8                    |         422 | `document_decoding_failed`                   |
| Empty or whitespace-only text    |         422 | `empty_document`                             |
| Invalid metadata                 |         422 | Application or framework validation contract |
| Infrastructure failure           |         503 | `document_infrastructure_failure`            |

Exact verified source:

**Codex integration required**

### 13. Optional local run command

```bash
python -m uvicorn document_service.main:app --reload
```

This command is instructional. ChatGPT did not execute it.

### 14. Example multipart request

A command-line client could conceptually submit:

```bash
curl \
  -X POST \
  -F "media_type=text/plain" \
  -F "correlation_id=week1-demo-001" \
  -F "file=@example.txt;type=text/plain" \
  http://127.0.0.1:8000/v1/documents/extract
```

This example assumes a client-local file selected by `curl`. It does not send a location for the application to open.

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

## Independent exercises

### Exercise 1: Add a Markdown-text adapter

Add support for UTF-8 Markdown text without changing the extraction service’s public behavior.

Do not add Markdown rendering, HTML conversion, front-matter parsing, or a generic plugin framework.

#### Acceptance criteria

* `.md` with declared media type `text/markdown` is accepted.
* Upload content type must agree with the declared type.
* UTF-8 decoding remains strict.
* `.txt` with `text/plain` remains unchanged.
* Mismatched suffix and media type are rejected explicitly.
* The 1 MiB bounded-read contract remains unchanged.
* The route remains thin.
* Error responses retain stable codes.
* Tests demonstrate both formats.

#### Edge cases

* Uppercase suffix.
* `notes.md.txt`.
* `text/markdown; charset=utf-8`.
* Empty Markdown upload.
* Invalid UTF-8 bytes.
* `.md` declared as `text/plain`.
* `.txt` declared as `text/markdown`.
* Missing upload content type.
* Oversized Markdown upload.

#### Optional hints

* Start with an explicit two-case policy.
* Avoid dynamic discovery.
* Keep Markdown extraction equivalent to plain text unless a requirement says otherwise.
* Do not weaken the sentinel-byte size check.

---

### Exercise 2: Make the 1 MiB limit configurable

Replace the fixed constant with an explicit configuration value without weakening the bounded-read guarantee.

#### Acceptance criteria

* The default remains 1 MiB.
* The configured value is positive.
* The route still requests only `configured_limit + 1` bytes.
* Exactly-at-limit content is accepted.
* Above-limit content returns HTTP `413`.
* The error code remains `document_too_large`.
* Byte length is not confused with decoded character count.
* Tests cover below, equal to, and above the configured limit.
* Configuration does not leak into unrelated domain functions.

#### Edge cases

* Zero limit.
* Negative limit.
* One-byte limit.
* Multibyte UTF-8 content.
* Very large configuration value.
* Configuration change between application instances.
* Upload with missing content type.

#### Optional hints

* Inject a small immutable settings value at application assembly.
* Keep the route’s read bound explicit.
* Do not read the full upload before applying the limit.

---

### Exercise 3: Parametrize media-type combinations

Add parametrized tests for declared media type, upload content type, and suffix combinations.

#### Acceptance criteria

* At least one valid `.txt`/`text/plain`/`text/plain` case is included.
* Unsupported declarations are rejected.
* Unsupported upload content types are rejected.
* Mismatched declared and upload types are rejected.
* Unsupported suffixes are rejected.
* Test IDs make failed combinations readable.
* Tests assert public behavior rather than private call sequences.

#### Edge cases

* Empty declared media type.
* Missing upload content type.
* Uppercase media type.
* Surrounding whitespace.
* `text/plain; charset=utf-8`.
* Uppercase suffix.
* No suffix.
* Multiple suffixes.

#### Optional hints

* Use `pytest.param(..., id="...")`.
* Treat media-type normalization as an explicit policy decision.
* Keep schema failures separate from unsupported-format failures.

---

### Exercise 4: Prove content and filename are never logged

Use captured logs to verify that raw uploaded content and the filename are never emitted.

#### Acceptance criteria

* The payload contains a unique secret marker.
* The filename contains a different unique secret marker.
* Logs are captured for success.
* Logs are captured for at least one failure.
* Neither marker appears in `caplog.text`.
* The correlation identifier is present on a captured `LogRecord`.
* A stable failure code is present on a failure record.
* The test does not require the formatter to render `extra` fields.
* Logging is not disabled globally.

#### Edge cases

* Multiline secret content.
* Secret included in a fake decoder exception message.
* Failure before decoding.
* Failure after decoding.
* Oversized upload.
* Invalid UTF-8.
* Logs at different levels.

#### Optional hints

* Inspect `caplog.records`.
* Use `getattr(record, "correlation_id", None)`.
* Check both required presence and forbidden absence.
* Review whether arbitrary exception messages can leak payload data.

---

### Exercise 5: Design an async batch-extraction interface

Design, but do not implement, an interface for extracting multiple uploads.

Choose among:

* sequential execution;
* asynchronous tasks;
* a bounded thread pool;
* a process pool;
* an external worker system.

#### Acceptance criteria

The design explains:

* expected workload type;
* whether each dependency is synchronous or awaitable;
* concurrency limit;
* input-size enforcement per document;
* total batch-size policy;
* ordering guarantees;
* partial-success behavior;
* timeout behavior;
* cancellation behavior;
* backpressure;
* resource cleanup;
* retry safety;
* observability;
* why rejected alternatives are less appropriate.

#### Edge cases

* One slow upload.
* One invalid UTF-8 upload.
* One oversized upload.
* Cancellation after partial completion.
* More items than available workers.
* CPU-heavy parser.
* Blocking third-party library.
* Duplicate identifiers.
* Caller disconnect.
* Partial success.

#### Optional hints

* Async tasks help only when work can suspend through awaitable operations.
* Threads can bridge blocking APIs but require bounded capacity.
* Processes add serialization and lifecycle costs.
* Sequential execution may be the best first design.
* Preserve per-item bounded reads.

## Testing and validation

### Technical-review execution record

The following results are attributed to **Codex technical review**, not to ChatGPT.

Environment recorded by Codex:

```text
Operating system: Windows
Python: 3.13.12
pip: 25.3
FastAPI: 0.139.2
Pydantic: 2.13.4
python-multipart: 0.0.32
Starlette: 1.3.1
HTTPX2: 2.7.0
Uvicorn: 0.51.0
pytest: 9.1.1
Ruff: 0.15.22
mypy: 2.3.0
```

Codex reported that the initial generated suite exposed three test defects:

1. A Windows text-mode fixture incorrectly assumed exact `\n` bytes.
2. An endpoint fixture wrote explicit `\r\n` through text mode, producing platform-dependent bytes.
3. A logging test incorrectly expected an `extra` field to appear in `caplog.text`.

Codex corrected the executable repository tests by:

* using byte-exact fixtures;
* inspecting structured `LogRecord` attributes;
* using `httpx2==2.7.0`;
* formatting the repository source with Ruff.

After the upload boundary replaced the earlier design, Codex reported:

```text
python -m pytest -q
26 passed in 0.33s

python -m ruff check document_service tests
All checks passed!

python -m ruff format --check document_service tests
14 files already formatted

python -m mypy --strict document_service tests
Success: no issues found in 14 source files
```

These results apply to the verified repository files reviewed by Codex. They do not prove that every isolated narrative snippet in this module is executable or identical to repository source. The full technical-review record is supplied in the attached review document.

### Exact repository test source

The verified `tests/` files were not attached to this revision request.

**Codex integration required**

### Required test categories

The repository suite should cover:

| Behavior                       | Layer             | Expected result            |
| ------------------------------ | ----------------- | -------------------------- |
| Valid metadata                 | Pydantic boundary | Validation succeeds        |
| Unsafe correlation ID          | Pydantic boundary | Validation failure         |
| Missing multipart field        | HTTP boundary     | `422`                      |
| Valid `.txt` filename          | Service           | Accepted                   |
| Unsupported suffix             | Service           | Unsupported-format failure |
| Declared type not `text/plain` | Service           | Unsupported-format failure |
| Upload type not `              |                   |                            |
