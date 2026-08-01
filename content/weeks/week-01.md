---

layout: week
permalink: /weeks/week-01/
description: Production Python and FastAPI foundations for reliable AI services.
week: 1
phase: 1
title: Python for production AI systems
status: approved
version: 1.0.0
last_reviewed: 2026-08-01
estimated_hours: null
prerequisites: ["Working knowledge of Python syntax", "Basic JSON knowledge"]
generated_with: ChatGPT Web
technical_review: passed
human_review: passed
---

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
| ------------------ | --------------- | ------------------- |
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
          +---------+
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
| -------------- | -------------------- | ------- |
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
| ----------- | ------------------- | ----------------- | --------- | ------------- |
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
| ---------- | ------------------------- |
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
| --- | ----------------- | ----------------------- |
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
| ---------------- | ---------- | --------- |
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

The exact technically verified `document_service/` source files are integrated below by Codex.

Where verified source content belongs, this section uses the required marker:

Verified repository source is integrated in the subsections below.

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

```text
document_service/
|-- __init__.py
|-- api.py
|-- dependencies.py
|-- domain.py
|-- errors.py
|-- main.py
|-- models.py
|-- ports.py
|-- readers.py
-- service.py
tests/
|-- test_api.py
|-- test_models.py
|-- test_readers.py
-- test_service.py
```

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

```python
from typing import ClassVar


class ReaderError(Exception):
    """Base exception for the low-level reader boundary."""


class ReaderDecodingError(ReaderError):
    """The reader could not decode the resource."""


class DocumentServiceError(Exception):
    """Base exception exposed by the extraction service."""

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

### 5. Domain values and pure transformations

The verified domain source must define typed internal commands and results and deterministic newline and line-count behavior.

Exact verified source:

```python
from dataclasses import dataclass


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


def normalize_newlines(text: str) -> str:
    """Normalize newline representation without trimming other whitespace."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def count_logical_lines(text: str) -> int:
    """Count logical lines for a non-empty document."""
    lines = text.splitlines()
    return len(lines) if lines else 1
```

### 6. Decoder protocol

The required narrow protocol is:

```text
decode(content: bytes) -> str
```

Exact verified source:

```python
from typing import Protocol


class TextReader(Protocol):
    """Narrow interface required by the extraction service."""

    def decode(self, content: bytes) -> str: ...
```

### 7. UTF-8 decoder implementation

The verified decoder must:

* accept bytes;
* use strict UTF-8;
* translate `UnicodeDecodeError`;
* preserve causal context;
* avoid logging content.

Exact verified source:

```python
from typing import ClassVar

from document_service.errors import ReaderDecodingError


class Utf8TextReader:
    """Decode complete UTF-8 document content strictly."""

    encoding: ClassVar[str] = "utf-8"

    def decode(self, content: bytes) -> str:
        try:
            return content.decode(self.encoding, errors="strict")
        except UnicodeDecodeError as exc:
            raise ReaderDecodingError("document resource is not valid UTF-8") from exc
```

### 8. Pydantic metadata and response models

The verified models cover:

* scalar multipart metadata received separately from the file;
* safe correlation identifiers;
* the declared media type;
* response serialization; and
* stable error serialization.

The filename and upload content type belong to `UploadFile` and are carried by
the internal command for deterministic service-policy validation; they are not
duplicated as Pydantic request fields.

Exact verified source:

```python
import re
from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from document_service.domain import ExtractedDocument


_SAFE_CORRELATION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class DocumentRequest(BaseModel):
    """Untrusted JSON request boundary."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    media_type: str = Field(min_length=1, max_length=128)
    correlation_id: str = Field(min_length=1, max_length=64)

    @field_validator("media_type")
    @classmethod
    def validate_media_type_text(cls, value: str) -> str:
        if value != value.strip():
            raise ValueError("media_type must not contain surrounding whitespace")
        return value

    @field_validator("correlation_id")
    @classmethod
    def validate_correlation_id(cls, value: str) -> str:
        if _SAFE_CORRELATION_ID.fullmatch(value) is None:
            raise ValueError("correlation_id contains unsupported characters")
        return value


class ExtractionResponse(BaseModel):
    """Serialized successful response boundary."""

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


class ErrorResponse(BaseModel):
    """Stable error body owned by this application."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    code: str
    message: str
    correlation_id: str
```

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
    DocumentServiceError,
    DocumentValidationError,
    EmptyDocumentError,
    ReaderDecodingError,
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

    def extract(self, command: ExtractionCommand) -> ExtractedDocument:
        logger.info(
            "document_extraction_started",
            extra={
                "correlation_id": command.correlation_id,
                "media_type": command.declared_media_type,
            },
        )

        try:
            self._validate_command(command)
            raw_text = self._decode(command)
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
    def _validate_command(cls, command: ExtractionCommand) -> None:
        if command.correlation_id == "":
            raise DocumentValidationError(
                "correlation_id must not be empty",
                correlation_id=command.correlation_id,
            )

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

    def _decode(self, command: ExtractionCommand) -> str:
        try:
            return self._reader.decode(command.content)
        except ReaderDecodingError as exc:
            raise DocumentDecodingError(
                "document is not valid UTF-8",
                correlation_id=command.correlation_id,
            ) from exc
```

### 10. Dependency construction

The verified dependency assembly must construct the UTF-8 decoder and inject it into the service.

Exact verified source:

```python
from document_service.readers import Utf8TextReader
from document_service.service import DocumentExtractionService


def get_extraction_service() -> DocumentExtractionService:
    reader = Utf8TextReader()
    return DocumentExtractionService(reader=reader)
```

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

```python
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from document_service.dependencies import get_extraction_service
from document_service.domain import ExtractionCommand
from document_service.errors import DocumentInfrastructureError, DocumentTooLargeError
from document_service.models import DocumentRequest, ExtractionResponse
from document_service.service import DocumentExtractionService


router = APIRouter(prefix="/v1/documents", tags=["documents"])
MAX_UPLOAD_BYTES = 1_048_576


def parse_document_request(
    media_type: Annotated[str, Form()],
    correlation_id: Annotated[str, Form()],
) -> DocumentRequest:
    """Validate multipart metadata with the boundary model."""
    try:
        return DocumentRequest(
            media_type=media_type,
            correlation_id=correlation_id,
        )
    except ValidationError as exc:
        raise RequestValidationError(exc.errors()) from exc


@router.post(
    "/extract",
    response_model=ExtractionResponse,
    status_code=status.HTTP_200_OK,
)
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

### 12. Application and error mappings

The verified application must map domain errors to stable HTTP responses, including:

| Condition                        | HTTP status | Stable code                                  |
| -------------- | ----------: | -------- |
| Oversized upload                 |         413 | `document_too_large`                         |
| Unsupported suffix or media type |         415 | `unsupported_document_format`                |
| Invalid UTF-8                    |         422 | `document_decoding_failed`                   |
| Empty or whitespace-only text    |         422 | `empty_document`                             |
| Invalid metadata                 |         422 | Application or framework validation contract |
| Infrastructure failure           |         503 | `document_infrastructure_failure`            |

Exact verified source:

```python
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from document_service.api import router
from document_service.errors import (
    DocumentExtractionError,
    DocumentInfrastructureError,
    DocumentTooLargeError,
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
    return JSONResponse(status_code=status_code, content=payload.model_dump())


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


### Required test categories

| Behavior                                                                      | Layer                    | Expected result                                                                               |
| ----------------------- | ------ | --------------------- |
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

#### `tests/test_models.py`

```python
import pytest
from pydantic import ValidationError

from document_service.models import DocumentRequest


def test_document_request_accepts_safe_values() -> None:
    request = DocumentRequest(
        media_type="text/plain",
        correlation_id="request-123",
    )

    assert request.media_type == "text/plain"
    assert request.correlation_id == "request-123"


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


def test_document_request_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        DocumentRequest.model_validate(
            {
                "media_type": "text/plain",
                "correlation_id": "request-123",
                "unexpected": "value",
            }
        )
```

#### `tests/test_readers.py`

```python
import pytest

from document_service.errors import ReaderDecodingError
from document_service.readers import Utf8TextReader


def test_reader_decodes_utf8_text() -> None:
    result = Utf8TextReader().decode("भारत\nAI".encode())

    assert result == "भारत\nAI"


def test_reader_rejects_invalid_utf8() -> None:
    with pytest.raises(ReaderDecodingError) as captured:
        Utf8TextReader().decode(b"\xff\xfe\xfa")

    assert isinstance(captured.value.__cause__, UnicodeDecodeError)
```

#### `tests/test_service.py`

```python
import logging
from dataclasses import dataclass

import pytest

from document_service.domain import ExtractionCommand
from document_service.errors import (
    DocumentDecodingError,
    EmptyDocumentError,
    ReaderDecodingError,
    UnsupportedDocumentFormatError,
)
from document_service.service import DocumentExtractionService


@dataclass(slots=True)
class FixedReader:
    text: str

    def decode(self, content: bytes) -> str:
        return self.text


class DecodingFailingReader:
    def decode(self, content: bytes) -> str:
        raise ReaderDecodingError("simulated decode failure")


def make_command(
    *,
    filename: str = "document.txt",
    declared_media_type: str = "text/plain",
    upload_media_type: str = "text/plain",
    correlation_id: str = "request-123",
    content: bytes = b"content",
) -> ExtractionCommand:
    return ExtractionCommand(
        filename=filename,
        declared_media_type=declared_media_type,
        upload_media_type=upload_media_type,
        correlation_id=correlation_id,
        content=content,
    )


def test_service_extracts_and_normalizes_text() -> None:
    service = DocumentExtractionService(reader=FixedReader("alpha\r\nbeta\rgamma"))

    result = service.extract(make_command())

    assert result.correlation_id == "request-123"
    assert result.media_type == "text/plain"
    assert result.text == "alpha\nbeta\ngamma"
    assert result.character_count == len("alpha\nbeta\ngamma")
    assert result.line_count == 3


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


@pytest.mark.parametrize("text", ["", " ", "\n", "\t\r\n"])
def test_service_rejects_empty_or_whitespace_document(text: str) -> None:
    service = DocumentExtractionService(reader=FixedReader(text))

    with pytest.raises(EmptyDocumentError):
        service.extract(make_command())


def test_service_translates_decoding_failure() -> None:
    service = DocumentExtractionService(reader=DecodingFailingReader())

    with pytest.raises(DocumentDecodingError) as captured:
        service.extract(make_command())

    assert isinstance(captured.value.__cause__, ReaderDecodingError)


def test_service_does_not_log_document_text_or_filename(
    caplog: pytest.LogCaptureFixture,
) -> None:
    secret_text = "UNIQUE-SECRET-DOCUMENT-CONTENT"
    filename = "private-document.txt"
    service = DocumentExtractionService(reader=FixedReader(secret_text))

    with caplog.at_level(logging.INFO, logger="document_service.service"):
        result = service.extract(
            make_command(
                filename=filename,
                correlation_id="safe-correlation-123",
            )
        )

    assert result.text == secret_text
    assert secret_text not in caplog.text
    assert filename not in caplog.text
    assert all(
        getattr(record, "correlation_id", None) == "safe-correlation-123"
        for record in caplog.records
    )
```

#### `tests/test_api.py`

```python
from fastapi.testclient import TestClient
from httpx2 import Response

from document_service.api import MAX_UPLOAD_BYTES
from document_service.main import create_app


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


def test_extract_endpoint_success() -> None:
    with TestClient(create_app()) as client:
        response = post_document(client)

    assert response.status_code == 200
    assert response.json() == {
        "correlation_id": "endpoint-success-1",
        "media_type": "text/plain",
        "text": "alpha\nbeta",
        "character_count": len("alpha\nbeta"),
        "line_count": 2,
    }


def test_extract_endpoint_maps_unsupported_format() -> None:
    with TestClient(create_app()) as client:
        response = post_document(
            client,
            declared_media_type="application/pdf",
            upload_media_type="application/pdf",
        )

    assert response.status_code == 415
    assert response.json() == {
        "code": "unsupported_document_format",
        "message": "only text/plain documents are supported",
        "correlation_id": "endpoint-success-1",
    }


def test_extract_endpoint_rejects_mismatched_media_type() -> None:
    with TestClient(create_app()) as client:
        response = post_document(client, upload_media_type="application/octet-stream")

    assert response.status_code == 415
    assert response.json()["code"] == "unsupported_document_format"


def test_extract_endpoint_rejects_oversized_document() -> None:
    with TestClient(create_app()) as client:
        response = post_document(client, content=b"a" * (MAX_UPLOAD_BYTES + 1))

    assert response.status_code == 413
    assert response.json() == {
        "code": "document_too_large",
        "message": "document exceeds the 1 MiB upload limit",
        "correlation_id": "endpoint-success-1",
    }


def test_extract_endpoint_rejects_invalid_request() -> None:
    with TestClient(create_app()) as client:
        response = post_document(client, correlation_id="contains space")

    assert response.status_code == 422
```

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
* [x] Human review was approved on 2026-08-01.
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
* **2026-07-22 - Codex source integration:** Inserted the exact verified `document_service/` and `tests/` files into the review candidate.
* **2026-07-22 - Technical content review:** Structural, executable, lint, formatting, and strict-type gates passed; human content review was approved on 2026-08-01.
* **2026-08-01 - Human review:** Approved by the project owner.
* **2026-08-01 - Content approval:** Approved as canonical Week 1 version 1.0.0.
* **2026-08-01 - Website integration:** Assigned the approved Jekyll weekly layout and stable `/weeks/week-01/` permalink.

