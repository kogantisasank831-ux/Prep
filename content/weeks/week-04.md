---
layout: week
permalink: /weeks/week-04/
title: "Prompting and structured output: make extraction evidence defensible"
description: Build a typed procurement-document extraction boundary that treats model output as untrusted, validates it deterministically, and records every attempt.
summary: Follow one Atlas Metals purchase confirmation from bounded text through versioned messages, constrained structured output, evidence checks, retries, and controlled evaluation.
kicker_primary: Prompting and structured output
kicker_secondary: Extraction contracts before prose
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-04/beginner/
---

## One confirmation, one question that prose cannot answer safely

An operations team receives this synthetic purchase confirmation:

```text
Purchase confirmation

Supplier: Atlas Metals
Product: Copper wire
Quantity: 1,000 kg
Unit price: USD 12.00 per kg
Delivery date: 2026-08-18
Payment terms: Net 30 after inspection approval
```

The desired extraction is not a friendly summary. It is a typed candidate that a downstream review workflow can inspect without reparsing a model sentence:

```json
{
  "supplier_name": "Atlas Metals",
  "product": "Copper wire",
  "quantity": "1000",
  "unit": "kg",
  "unit_price": "12.00",
  "currency": "USD",
  "delivery_date": "2026-08-18",
  "payment_terms": "Net 30 after inspection approval"
}
```

The business question is deliberately narrower than “what does the model know about procurement?”:

> Can this bounded document produce one candidate that satisfies a declared contract and is supported by visible evidence, or a reviewable failure that says why it did not?

The answer is never “because the model sounded certain.” A document may be incomplete or hostile, a parser or tool may return corrupt text, and a local or remote model may emit plausible but unsupported fields. The system must distinguish four results:

```text
received document -> untrusted model candidate -> structural validation
                                                -> evidence/semantic checks
                                                -> valid | invalid | needs_review
```

For this lesson, `PO` creation, payment approval, external retrieval, tool execution, and system writes are out of scope. The extractor only produces a candidate plus provenance and a final application-owned validation status. It never treats “Net 30 after inspection approval” as permission to pay.

### The contract for every extraction

Every result must state these components:

```text
source document + output schema + validation policy + evidence rule + versioned configuration
```

The source document is synthetic text. The output schema defines names and types. The validation policy says which values are permitted. The evidence rule defines what counts as supported by this document. The configuration identifies the prompt, schema, local model boundary, and generation settings that produced the candidate.

Model output can be JSON-valid yet wrong. Schema-valid output can be typed yet semantically wrong. A self-reported `confidence: 0.99` is merely another generated value unless calibration has been measured for a specified model, task, population, and decision rule. This design reports deterministic validation status and evidence/provenance instead.

**Checkpoint.** Does `{"delivery_date": "2026-08-18"}` prove the document contains that date? No. JSON syntax and a date parser say nothing about the evidence. The application must compare the candidate against the document under its declared policy.

**Bridge.** A model cannot satisfy an extraction contract that the application has not first made explicit.

## 1. Design the output contract before composing messages

### Orienting question: what must one accepted field mean?

The output is a business boundary, not a convenient dictionary. Each field has one type and one meaning:

| Field | Meaning | Accepted internal type |
| --- | --- | --- |
| `supplier_name` | supplier stated in the document | `str` |
| `product` | purchased product stated in the document | `str` |
| `quantity` | ordered numerical quantity | `Decimal` |
| `unit` | unit attached to quantity | constrained `str` |
| `unit_price` | agreed price per unit | `Decimal` |
| `currency` | unit-price currency | constrained `str` |
| `delivery_date` | stated calendar delivery date, when the document provides one | `date | None` |
| `payment_terms` | payment condition as stated | `str` |

`Decimal("12.00")` preserves the base-10 price representation. A binary `float` is not a persisted money type: many decimal fractions cannot be represented exactly in binary. The date is a business calendar date, not a timestamp and not an inferred deadline. The payment term remains document text because this small contract does not define a payment-calendar calculator.

Missing, null, and invalid values have different operational meanings:

| State | Candidate fragment | Meaning |
| --- | --- | --- |
| missing | no `delivery_date` key | producer failed to provide a required key; schema-invalid |
| null | `"delivery_date": null` | document has no delivery-date evidence; structurally permitted but never application-valid |
| invalid | `"delivery_date": "18/08/2026"` | value exists but fails the ISO-date contract |
| unsupported | `"delivery_date": "2026-08-19"` | type is valid but document evidence does not support it |

This lesson requires all eight keys. `delivery_date` alone may be explicitly null when the document has no delivery-date label. A missing `delivery_date` key is schema-invalid; a null date is a visible `needs_review` outcome, not an invitation to guess and never an application-valid extraction. The remaining seven values are non-null. A different nullability policy is a public behavior decision that must define its status and downstream consequences.

The external JSON representation carries decimal values as strings. JSON has one generic number primitive and implementations vary in their handling of numeric precision. The typed boundary parses `"1000"` and `"12.00"` to `Decimal`, then rejects non-finite or out-of-policy values. `ExtractionCandidate` never owns `validation_status` or confidence: the candidate is model output only. `ExtractionOutcome` receives its application-owned status after structural and evidence checks; an LLM-written confidence score is not part of this contract.

**Checkpoint.** Why is `"quantity": "1000"` preferable to `"quantity": 1000` in this contract? It gives the boundary an explicit decimal lexical form to parse deliberately. Either form can be designed, but accepting a generic JSON number without a precision policy leaves financial representation ambiguous.

**Bridge.** The contract identifies the fields; Pydantic makes the structural portion executable.

## 2. Use a typed boundary, not a permissive mapping

### Orienting question: which invariants can code decide without asking a model?

Pydantic v2 parses untrusted JSON into a typed value and reports structured failures. It is not the final judge of document truth. The following Python 3.13 interface is intentionally strict and narrow:

```python
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


NonBlank = Annotated[str, Field(min_length=1, max_length=200)]


class ExtractionCandidate(BaseModel):
    """Untrusted model candidate after structural parsing only."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    supplier_name: NonBlank
    product: NonBlank
    quantity: Decimal = Field(gt=Decimal("0"), max_digits=18, decimal_places=3)
    unit: Literal["kg", "ea"]
    unit_price: Decimal = Field(
        ge=Decimal("0"), max_digits=19, decimal_places=4
    )
    currency: Literal["USD"]
    delivery_date: date | None
    payment_terms: NonBlank

    @field_validator("quantity", "unit_price")
    @classmethod
    def reject_non_finite_decimal(cls, value: Decimal) -> Decimal:
        if not value.is_finite():
            raise ValueError("decimal must be finite")
        return value

    @field_validator("supplier_name", "product", "payment_terms")
    @classmethod
    def reject_surrounding_whitespace(cls, value: str) -> str:
        if value != value.strip():
            raise ValueError("text must not contain surrounding whitespace")
        return value
```

`extra="forbid"` protects the public shape: an unexpected `confidence`, `approved`, or `payment_due` field cannot quietly enter the candidate. `strict=True` avoids broad coercion at this boundary. `frozen=True` prevents ordinary reassignment after parsing; it is not deep immutability or a trust control. `Literal` is deliberately narrow for this synthetic contract. A production currency and unit catalog must have an explicit ownership and versioning policy rather than expanding when a model emits another token.

Use Pydantic's JSON entry point rather than parsing JSON to `dict[str, object]` and then trusting dictionary access:

```python
from pydantic import ValidationError


def parse_candidate(raw_json: str) -> ExtractionCandidate:
    try:
        return ExtractionCandidate.model_validate_json(raw_json)
    except ValidationError as exc:
        raise CandidateSchemaError("candidate failed extraction schema") from exc
```

The complete JSON Schema is derived from the same model with `ExtractionCandidate.model_json_schema()`. This avoids maintaining one handwritten schema for model output and another unreviewed set of Python assumptions. JSON Schema expresses portable structure; Pydantic gives the Python service a typed representation. Neither verifies that the model faithfully read the document.

**Boundary.** Do not accept a model object because it contains the expected keys. `"quantity": "NaN"`, an unknown currency, a missing payment condition, a future-only field, and a typo in `delivery_date` are contract failures with different remediation paths.

**Checkpoint.** Does a `date | None` annotation make a missing date valid? No. The `delivery_date` key remains required. It accepts ISO `YYYY-MM-DD` or explicit JSON `null`; null deterministically becomes application status `needs_review`, while a missing key remains schema-invalid.

**Bridge.** Structural validation checks representation. It cannot establish what the document actually said.

## 3. Separate evidence checks from schema checks

### Orienting question: how can an ISO date still be wrong?

A candidate with `delivery_date=date(2026, 8, 19)` is structurally perfect. It is also wrong for the Atlas document. The final decision therefore needs a deterministic, field-by-field evidence policy.

For the controlled exercise, parse the known label-value document into a normalized evidence map. This is not a general OCR or natural-language understanding claim; it is a bounded policy for this document shape:

```python
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


class EvidenceError(ValueError):
    """The bounded document violates the labelled-evidence grammar."""


@dataclass(frozen=True, slots=True)
class ProcurementEvidence:
    supplier_name: str
    product: str
    quantity: Decimal
    unit: str
    unit_price: Decimal
    currency: str
    delivery_date: date | None
    payment_terms: str


def parse_labelled_evidence(text: str) -> ProcurementEvidence:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        if ":" in line:
            key, value = line.split(":", maxsplit=1)
            fields[key.strip().casefold()] = value.strip()

    try:
        quantity_text, unit = fields["quantity"].replace(",", "").split(maxsplit=1)
        currency, price_text, per_token, price_unit = fields["unit price"].split(maxsplit=3)
        if per_token.casefold() != "per":
            raise EvidenceError("unit price must contain the token 'per'")
        if price_unit != unit:
            raise EvidenceError("price unit must equal quantity unit")
        return ProcurementEvidence(
            supplier_name=fields["supplier"],
            product=fields["product"],
            quantity=Decimal(quantity_text),
            unit=unit,
            unit_price=Decimal(price_text),
            currency=currency,
            delivery_date=(
                None
                if "delivery date" not in fields
                else date.fromisoformat(fields["delivery date"])
            ),
            payment_terms=fields["payment terms"],
        )
    except EvidenceError:
        raise
    except (KeyError, ValueError, InvalidOperation) as exc:
        raise EvidenceError("document does not match the labelled-evidence contract") from exc
```

The parser validates both parts of the commercial expression: the connector token must be `per`, and its price unit must equal the quantity unit. Thus `USD 12.00 per ea` beside `Quantity: 1,000 kg` cannot become evidence for this candidate. An absent delivery-date label becomes `None` evidence under the explicit nullable rule; malformed present dates still raise `EvidenceError`. Do not extend this parser by assumption to arbitrary vendor formats.

An explicit comparison owns the acceptance decision:

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SemanticCheck:
    field: str
    expected: str
    actual: str
    passed: bool


def check_evidence(
    candidate: ExtractionCandidate, evidence: ProcurementEvidence
) -> tuple[SemanticCheck, ...]:
    def date_text(value: date | None) -> str:
        return "null" if value is None else value.isoformat()

    pairs = (
        ("supplier_name", evidence.supplier_name, candidate.supplier_name),
        ("product", evidence.product, candidate.product),
        ("quantity", str(evidence.quantity), str(candidate.quantity)),
        ("unit", evidence.unit, candidate.unit),
        ("unit_price", str(evidence.unit_price), str(candidate.unit_price)),
        ("currency", evidence.currency, candidate.currency),
        ("delivery_date", date_text(evidence.delivery_date), date_text(candidate.delivery_date)),
        ("payment_terms", evidence.payment_terms, candidate.payment_terms),
    )
    return tuple(
        SemanticCheck(field, expected, actual, expected == actual)
        for field, expected, actual in pairs
    )
```

Exact string equality is appropriate only because the evidence contract has already normalized this synthetic fixture. Names, units, whitespace, date formats, product aliases, and language variants need a separately specified normalization policy. A fuzzy matcher is not an excuse to accept a candidate because it is “close enough.” If a mismatch could change a financial, delivery, or approval meaning, surface it for review.

**Checkpoint.** Is the evidence parser more trusted than the original document? No. It is deterministic code operating on untrusted text. It produces a reproducible interpretation under a narrow grammar; it does not authenticate the source document.

**Bridge.** The application now knows what to accept. Messages tell the model what candidate to attempt.

## 4. Message roles organise context; they do not create trust

### Orienting question: what should a local model receive?

Chat interfaces often represent inputs as system, user, and tool messages. Model templates may use those roles to format tokens differently, but role labels are not authorization boundaries.

```python
from dataclasses import dataclass
from typing import Literal


MessageRole = Literal["system", "user", "tool"]


@dataclass(frozen=True, slots=True)
class ChatMessage:
    role: MessageRole
    content: str
```

A system message contains stable application instruction. A user message contains the requested operation and bounded document. A tool message, if an application uses a parser or other external component, carries that component's result. All three can carry untrusted content or be misunderstood by the model:

- system instructions express application intent but cannot force model behavior;
- user documents can include misleading text such as “ignore the extraction contract”; and
- tool output can be malformed, stale, manipulated, or semantically wrong.

The application must not let arbitrary text choose the output schema, change its versioning, or cause side effects. Delimiters identify data boundaries for the model and for human review:

```text
<procurement_document id="atlas-confirmation-001">
Supplier: Atlas Metals
...
</procurement_document>
```

They are not a sandbox. A document can contain closing tags, prompt-like instructions, or deceptive labels. The service constrains document size and source format outside the prompt, renders its own fixed instructions, and validates the candidate after inference. This Week 4 model boundary has no tool-execution capability. A future tool call would need an allowlisted interface, authorization, data provenance, and independent result validation; none follows from a `tool` role.

```text
application-owned system message
              + bounded user document
              + optional untrusted parser result
                           |
                           v
                   local model boundary
                           |
                           v
                untrusted JSON candidate text
```

**Checkpoint.** Does a system message outrank a malicious document as a security mechanism? No. It is a model-conditioning convention, not a privilege enforcement mechanism. The only final enforcement here is deterministic application code.

**Bridge.** With roles understood, choose the smallest prompting method that demonstrates the contract.

## 5. Zero-shot, few-shot, and role prompting have different jobs

### Orienting question: what is the least context needed for this extractor?

A **zero-shot** prompt gives the task and contract without demonstrations. It is the correct baseline for the Atlas document because it reveals whether the output contract is sufficiently clear:

```text
Extract only facts explicitly stated in the delimited procurement document.
Return one object matching the supplied JSON Schema. Do not add fields.
Do not infer missing fields. If a field cannot be stated, still return a schema-valid
candidate only when the schema permits that state.
```

The schema is sent as a machine-readable response contract to the local adapter, not pasted as an unversioned block that a model is merely asked to imitate. Zero-shot is not “we gave no constraints”; the schema and system instruction are the constraints.

A **few-shot** prompt adds a small input/output example. It can explain a legitimate ambiguous mapping or a required missing-value behavior, but it changes the experiment. Examples consume context, may leak fixture-specific wording, and can make a model copy irrelevant values. Version the example set with the prompt and test it against held-out documents.

```text
Example: a document with no delivery-date label is not evidence for a guessed date.
Expected handling: produce the contract's explicit missing/null state, or surface the
candidate as non-valid when the field is required.
```

**Role prompting** adds a perspective such as “You are a procurement-document extraction assistant.” It can make the task easier for a model to recognise, but it does not grant domain authority, calibration, access to a vendor system, or permission to approve the outcome. Requirements that deterministic code can check are more valuable than theatrical claims of expertise.

```text
Useful:   Return only the declared fields and use the supplied document as evidence.
Insufficient: You are an infallible procurement auditor.
```

**Boundary.** Few-shot examples and role wording influence output behavior. They do not replace schema validation, evidence checks, or an evaluation set. If adding an example changes a decision-critical field, record that as prompt sensitivity rather than calling the new answer more “intelligent.”

**Checkpoint.** When is few-shot prompting justified? When a versioned, representative example resolves a known mapping ambiguity and a held-out evaluation shows the change improves the declared metric without unacceptable regressions.

**Bridge.** Prompt wording can request JSON. That is not the same as receiving a constrained structured response.

## 6. “Return JSON” is weaker than structured output

### Orienting question: why not parse a polished answer after the fact?

There are three increasingly strong output arrangements:

| Arrangement | What the model is asked or allowed to do | What the application still must do |
| --- | --- | --- |
| Free-form prose | explain the document | parse language or ask a second model to do so |
| Prompted JSON | “return JSON with these fields” | parse JSON, reject malformed/extra/missing values, validate types and evidence |
| Runtime-constrained structured decoding | adapter asks the runtime for JSON matching a supplied schema | validate schema and evidence anyway |

Free-form prose has no stable field boundary. “Atlas will deliver 1,000 kg on August 18” leaves a program to infer the year, locate the supplier, decide whether the price was omitted, and preserve the inspection condition. A regex parser becomes a fragile second extractor.

Prompting for JSON is better, but the model can still emit markdown fences, explanatory text, duplicate keys, a malformed comma, an extra `confidence` field, or values with the wrong type. Parsing failure is an expected boundary outcome, not a rare exception to hide.

Runtime-constrained structured decoding asks a capable local runtime to limit generation to a response schema or grammar. It can reduce syntax failure and make interfaces more reliable. It does **not** make the contents true. A runtime can produce a schema-conforming date that was never in the document, and implementations differ in which JSON Schema features they honour. Treat the runtime's guarantee as an optimization whose observed behavior is tested, not as the application's final trust decision.

The local adapter therefore receives the schema as data and returns raw response text plus its own observed identity:

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ModelIdentity:
    model_id: str
    runtime_version: str
    template_id: str


@dataclass(frozen=True, slots=True)
class GenerationConfig:
    temperature: Decimal
    max_output_tokens: int
    timeout_seconds: Decimal


@dataclass(frozen=True, slots=True)
class ModelResponse:
    raw_json: str
    identity: ModelIdentity


class LocalStructuredModel(Protocol):
    """Injected local inference boundary; no provider SDK is assumed."""

    def complete(
        self,
        *,
        messages: tuple[ChatMessage, ...],
        response_schema: dict[str, object],
        config: GenerationConfig,
    ) -> ModelResponse: ...
```

The protocol permits a local server adapter, a subprocess adapter, or a deterministic fake in tests. It does not bind the domain to FastAPI, a hosted API, or any model family. “Local” changes where inference runs; it does not make model output, tool output, prompt content, or model artifacts trusted.

**Checkpoint.** If constrained decoding returns valid JSON every time, can the application delete `parse_candidate()` and `check_evidence()`? No. The decoding constraint addresses a generation interface. The application still owns type policy, semantic support, version checks, and final status.

**Bridge.** A constrained model call needs versioned inputs and a failure vocabulary before it can be retried safely.

## 7. Make model calls reproducible and failures explicit

### Orienting question: what changed when an extraction changes?

An output may change because the document, prompt, schema, model artifact, chat template, decoding configuration, or local runtime changed. Record each separately:

```text
document_id and SHA-256 digest
prompt_id and prompt version
schema_id and schema version
model ID, artifact digest, runtime version, template ID
temperature, output cap, timeout, constrained-decoding mode
attempt ID, attempt kind, timestamp, raw candidate digest, outcome
```

Prompt versioning must capture the rendered instructions, examples, delimiter policy, and repair wording—not only a friendly name. Schema versioning prevents a caller from silently interpreting an old output under new fields. Model identity must be more precise than “a local 7B model”: retain the actual artifact revision or digest and runtime configuration. Configuration includes sampling and output caps because they influence generated text.

Use explicit exception types at the adapter and orchestration boundaries:

```python
class ExtractionError(Exception):
    """Base error for the extraction workflow."""


class ModelTransportError(ExtractionError):
    """No usable response arrived from the injected model boundary."""


class ModelIdentityError(ExtractionError):
    """A responding local runtime did not match the expected identity."""


class CandidateSchemaError(ExtractionError):
    """Raw model response could not become an ExtractionCandidate."""
```

An adapter should translate its library-specific timeout, connection, and protocol failures into `ModelTransportError`, preserving the original cause. It should check the returned identity against the request's expected model boundary. A responsive wrong local model is a reproducibility failure, not a successful extraction.

Do not log document text, raw prompts, or raw candidate values by default. They can carry commercially sensitive information. `AttemptRecord` is deliberately non-sensitive operational metadata: it stores a raw-candidate digest, versions, attempt counts, status, and stable error codes. A digest proves equality only for someone who already has a candidate to hash; it does not preserve the candidate.

If policy requires raw candidate or prompt retention, store a separately access-controlled audit payload keyed by the attempt ID, with defined encryption, retention, deletion, and authorization controls. Link that protected payload to `AttemptRecord`; do not put raw text in routine logs or pretend the compact record contains it. This lesson defines the metadata record only and makes no retention implementation claim.

**Checkpoint.** Why version the schema if Pydantic generates it from code? The generated schema still changes when code changes. A stored schema identifier/version tells reviewers which contract governed a durable attempt and exposes compatibility work.

**Bridge.** Now distinguish a failure to receive a response from a response that fails the contract.

## 8. Transport retry and validation repair are not the same operation

### Orienting question: what should happen after a timeout versus an invalid date?

A **transport retry** is for an unavailable or incomplete model interaction: local process down, connection reset, timeout, or invalid transport envelope. It resends the exact same immutable request to the same expected boundary under a bounded retry policy. It does not alter the prompt, schema, or document.

A **validation repair** starts only after a response arrived and failed JSON parsing, schema validation, or evidence validation. It creates a new, explicitly versioned repair message that identifies the narrow failure category without treating the model's previous candidate as trusted evidence. A repair is a new attempt, not a hidden repeat of the original.

```text
transport failure
  -> bounded retry of identical request
  -> record each failure and final transport outcome

candidate schema/evidence failure
  -> preserve non-sensitive metadata, digest, and reason
  -> retain raw candidate only in an authorised audit payload, if policy requires it
  -> bounded repair request with immutable source/schema
  -> record repair prompt version and outcome
```

The orchestrator makes the cap and attempt identity visible:

```python
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from typing import Literal


AttemptKind = Literal["initial", "transport_retry", "validation_repair"]
ValidationStatus = Literal["valid", "invalid", "needs_review"]


@dataclass(frozen=True, slots=True)
class AttemptRecord:
    attempt_no: int
    kind: AttemptKind
    requested_at: datetime
    prompt_version: str
    schema_version: str
    model_identity: ModelIdentity | None
    raw_candidate_sha256: str | None
    status: ValidationStatus
    reason_code: str | None


def text_sha256(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def call_with_transport_retries(
    model: LocalStructuredModel,
    *,
    messages: tuple[ChatMessage, ...],
    response_schema: dict[str, object],
    config: GenerationConfig,
    max_attempts: int,
) -> ModelResponse:
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least one")
    last_error: ModelTransportError | None = None
    for _attempt_no in range(1, max_attempts + 1):
        try:
            return model.complete(
                messages=messages,
                response_schema=response_schema,
                config=config,
            )
        except ModelTransportError as exc:
            last_error = exc
    assert last_error is not None
    raise last_error
```

This compact helper omits sleeping intentionally: backoff and cancellation are injected operational concerns, not hidden inside domain logic. A real application supplies a bounded delay policy, deadline, and observability hooks. It must not use an unbounded `while True`, catch all exceptions, or silently switch models after failure.

For repair, preserve the source and schema and state what failed. Do not let an opaque “try harder” suffix mutate the original prompt. A repair response that becomes schema-valid but changes `2026-08-18` to `2026-08-19` fails evidence and remains non-valid.

```text
Repair contract v1:
The previous candidate failed reason code DATE_FORMAT.
Return a replacement candidate matching the unchanged schema.
Use only the delimited source document. Do not add fields or explanation.
```

When the repair cap is reached, return `needs_review` with preserved attempts and reasons. Do not keep retrying until a desirable value appears. A schema failure can be `invalid`; a source that cannot meet the narrow evidence grammar can be `needs_review`; the precise taxonomy is application policy and must be stable.

**Checkpoint.** Why must a transport retry use the same messages? Otherwise it is a new experiment with a hidden prompt change, not recovery from an unavailable boundary.

**Bridge.** The records make retry behavior auditable; tests make it safe to change.

## 9. Assemble an outcome without giving the model the final word

### Orienting question: what does the caller receive when any stage fails?

The caller should not need to infer success from a missing exception or parse a model's apology. It receives an explicit result whose status was assigned by the application. `AttemptRecord` carries non-sensitive metadata and candidate digests; raw candidate text belongs only in a separately authorised audit payload when retention policy requires it, not in a casual success payload.

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ExtractionOutcome:
    document_sha256: str
    status: ValidationStatus
    candidate: ExtractionCandidate | None
    checks: tuple[SemanticCheck, ...]
    attempts: tuple[AttemptRecord, ...]


class AttemptRecorder(Protocol):
    """Append one immutable attempt record to the selected audit boundary."""

    def append(self, record: AttemptRecord) -> None: ...


def decide_validation_status(
    candidate: ExtractionCandidate,
    evidence: ProcurementEvidence,
    checks: tuple[SemanticCheck, ...],
) -> tuple[ValidationStatus, str | None]:
    """Assign the application-owned status after deterministic checks."""
    if candidate.delivery_date is None and evidence.delivery_date is None:
        return "needs_review", "DELIVERY_DATE_ABSENT"
    if all(check.passed for check in checks):
        return "valid", None
    return "invalid", "EVIDENCE_MISMATCH"
```

The status has a deliberately limited meaning:

| Status | Meaning in this lesson |
| --- | --- |
| `valid` | candidate passed structural validation and every configured evidence check |
| `invalid` | a received candidate is malformed or violates the output contract |
| `needs_review` | the bounded process cannot establish an accepted candidate, including exhausted repair or evidence-policy ambiguity |

There is no `approved` state. An extractor cannot approve commercial terms merely because it copied them. There is also no status called `confident`: confidence is not a control category. `ExtractionCandidate` has neither status nor confidence fields; `decide_validation_status()` assigns the final `ExtractionOutcome.status` from deterministic checks and attempt-cap policy. A null delivery date with absent source evidence always becomes `needs_review`.

The service receives its nondeterministic dependencies instead of reaching for globals. The clock is injected so attempts are testable; the local adapter is injected so domain tests do not launch a model; the recorder is injected so persistence is not hidden in prompt code.

```python
from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class ExtractionPlan:
    prompt_version: str
    schema_version: str
    response_schema: dict[str, object]
    transport_attempts: int
    repair_attempts: int
    generation: GenerationConfig


class ProcurementExtractionService:
    def __init__(
        self,
        *,
        model: LocalStructuredModel,
        recorder: AttemptRecorder,
        now: Callable[[], datetime],
    ) -> None:
        self._model = model
        self._recorder = recorder
        self._now = now

    def extract(
        self,
        *,
        document_text: str,
        plan: ExtractionPlan,
    ) -> ExtractionOutcome:
        document_sha256 = text_sha256(document_text)
        records: list[AttemptRecord] = []
        try:
            evidence = parse_labelled_evidence(document_text)
        except EvidenceError:
            self._record(
                records, "initial", plan, None, None,
                "needs_review", "EVIDENCE_POLICY_UNSATISFIED"
            )
            return ExtractionOutcome(document_sha256, "needs_review", None, (), tuple(records))

        messages = render_initial_messages(document_text, plan.prompt_version)

        for repair_no in range(0, plan.repair_attempts + 1):
            kind: AttemptKind = "initial" if repair_no == 0 else "validation_repair"
            try:
                response = call_with_transport_retries(
                    self._model,
                    messages=messages,
                    response_schema=plan.response_schema,
                    config=plan.generation,
                    max_attempts=plan.transport_attempts,
                )
            except ModelTransportError:
                self._record(
                    records, kind, plan, None, None, "needs_review", "TRANSPORT_EXHAUSTED"
                )
                return ExtractionOutcome(document_sha256, "needs_review", None, (), tuple(records))
            except ModelIdentityError:
                self._record(
                    records, kind, plan, None, None, "needs_review", "MODEL_IDENTITY_MISMATCH"
                )
                return ExtractionOutcome(document_sha256, "needs_review", None, (), tuple(records))

            try:
                candidate = parse_candidate(response.raw_json)
            except CandidateSchemaError:
                self._record(
                    records, kind, plan, response, response.raw_json, "invalid", "SCHEMA_INVALID"
                )
                if repair_no == plan.repair_attempts:
                    return ExtractionOutcome(document_sha256, "needs_review", None, (), tuple(records))
                messages = render_repair_messages(
                    document_text, plan.prompt_version, "SCHEMA_INVALID"
                )
                continue

            checks = check_evidence(candidate, evidence)
            status, reason_code = decide_validation_status(candidate, evidence, checks)
            if status == "valid":
                self._record(records, kind, plan, response, response.raw_json, "valid", None)
                return ExtractionOutcome(document_sha256, "valid", candidate, checks, tuple(records))

            if status == "needs_review":
                self._record(
                    records, kind, plan, response, response.raw_json, status, reason_code
                )
                return ExtractionOutcome(document_sha256, status, candidate, checks, tuple(records))

            self._record(
                records, kind, plan, response, response.raw_json, status, reason_code
            )
            if repair_no == plan.repair_attempts:
                return ExtractionOutcome(document_sha256, "needs_review", candidate, checks, tuple(records))
            messages = render_repair_messages(
                document_text, plan.prompt_version, "EVIDENCE_MISMATCH"
            )

        raise AssertionError("repair loop must return")

    def _record(
        self,
        records: list[AttemptRecord],
        kind: AttemptKind,
        plan: ExtractionPlan,
        response: ModelResponse | None,
        raw_json: str | None,
        status: ValidationStatus,
        reason_code: str | None,
    ) -> AttemptRecord:
        record = AttemptRecord(
            attempt_no=len(records) + 1,
            kind=kind,
            requested_at=self._now(),
            prompt_version=plan.prompt_version,
            schema_version=plan.schema_version,
            model_identity=None if response is None else response.identity,
            raw_candidate_sha256=None if raw_json is None else text_sha256(raw_json),
            status=status,
            reason_code=reason_code,
        )
        self._recorder.append(record)
        records.append(record)
        return record
```

The service computes `document_sha256` from the exact `document_text`; a caller cannot supply a digest for different text. A document that violates the narrow labelled-evidence grammar returns `needs_review` with `EVIDENCE_POLICY_UNSATISFIED` before model inference. The message-rendering functions are intentionally not implicit in this service. They should accept the fixed document and explicitly versioned prompt text, produce tuples of `ChatMessage`, and be unit tested separately. Repair uses the same document and unchanged response schema; it has a separately recorded message version in a fuller implementation, for example `procurement-extract-repair/1.0.0`. For compactness, the snippet stores the base prompt version in `AttemptRecord`; production evidence should store both base and repair prompt identifiers when they differ.

There is one detail to make explicit: `call_with_transport_retries()` above retries internally, but `AttemptRecord` should ultimately represent each transport attempt as well as each response/repair attempt. The compact code records the final exhausted transport result, which is enough to show outcome control flow but not enough for a complete operational audit. In a production implementation, inject an attempt callback into the retry helper and append a record for every timeout, reset, and successful response. Do not invent missing failures after the fact.

The method returns `needs_review` after the cap because it has not established a valid result. It returns `needs_review` immediately for the permitted null-delivery-date state: no repair may invent a date absent from the document. It does not reclassify a schema failure as `valid` just because a later prompt changed. It also does not persist business data, issue a purchase order, interpret payment due dates, or call an external tool.

**Checkpoint.** Why does a final evidence mismatch end as `needs_review` rather than being silently dropped? It is a useful, reproducible observation: the model produced a typed value that the configured source policy could not support. Preserving the metadata, reason, and optional authorised audit payload enables review and evaluation.

**Bridge.** With the final status owned by deterministic code, tests can distinguish every status transition from a model's wording.

## 10. Test the contract, not a particular model's phrasing

### Orienting question: which behavior can be proven without starting a model?

Most of this workflow is deterministic. Test it with an injected fake, fixed document, and fixed clock; reserve real local inference for an explicit integration environment. The following pytest-style tests describe behavior at the narrowest useful boundary:

```python
from datetime import date
from decimal import Decimal

import pytest


ATLAS_TEXT = """Supplier: Atlas Metals
Product: Copper wire
Quantity: 1,000 kg
Unit price: USD 12.00 per kg
Delivery date: 2026-08-18
Payment terms: Net 30 after inspection approval
"""


def test_candidate_parses_exact_decimal_and_date() -> None:
    candidate = parse_candidate(
        """{
        "supplier_name":"Atlas Metals", "product":"Copper wire",
        "quantity":"1000", "unit":"kg", "unit_price":"12.00",
        "currency":"USD", "delivery_date":"2026-08-18",
        "payment_terms":"Net 30 after inspection approval"
        }"""
    )
    assert candidate.quantity == Decimal("1000")
    assert candidate.unit_price == Decimal("12.00")
    assert candidate.delivery_date == date(2026, 8, 18)


def test_missing_delivery_date_key_is_schema_invalid() -> None:
    with pytest.raises(CandidateSchemaError):
        parse_candidate(
            """{
            "supplier_name":"Atlas Metals", "product":"Copper wire",
            "quantity":"1000", "unit":"kg", "unit_price":"12.00",
            "currency":"USD", "payment_terms":"Net 30 after inspection approval"
            }"""
        )


def test_null_delivery_date_with_absent_source_requires_review() -> None:
    candidate = parse_candidate(
        """{
        "supplier_name":"Atlas Metals", "product":"Copper wire",
        "quantity":"1000", "unit":"kg", "unit_price":"12.00",
        "currency":"USD", "delivery_date":null,
        "payment_terms":"Net 30 after inspection approval"
        }"""
    )
    evidence = parse_labelled_evidence(ATLAS_TEXT.replace("Delivery date: 2026-08-18\n", ""))
    checks = check_evidence(candidate, evidence)
    assert decide_validation_status(candidate, evidence, checks) == (
        "needs_review", "DELIVERY_DATE_ABSENT"
    )


def test_evidence_rejects_price_unit_mismatch() -> None:
    with pytest.raises(EvidenceError, match="price unit"):
        parse_labelled_evidence(ATLAS_TEXT.replace("per kg", "per ea"))


def test_evidence_rejects_typed_but_unsupported_date() -> None:
    candidate = parse_candidate(
        """{
        "supplier_name":"Atlas Metals", "product":"Copper wire",
        "quantity":"1000", "unit":"kg", "unit_price":"12.00",
        "currency":"USD", "delivery_date":"2026-08-19",
        "payment_terms":"Net 30 after inspection approval"
        }"""
    )
    checks = check_evidence(candidate, parse_labelled_evidence(ATLAS_TEXT))
    failed = [check for check in checks if not check.passed]
    assert failed == [
        SemanticCheck("delivery_date", "2026-08-18", "2026-08-19", False)
    ]


def test_candidate_rejects_extra_model_confidence() -> None:
    with pytest.raises(CandidateSchemaError):
        parse_candidate(
            """{
            "supplier_name":"Atlas Metals", "product":"Copper wire",
            "quantity":"1000", "unit":"kg", "unit_price":"12.00",
            "currency":"USD", "delivery_date":"2026-08-18",
            "payment_terms":"Net 30 after inspection approval", "confidence":0.99
            }"""
        )
```

For retry behavior, make the fake record its requests. The assertion should prove no silent prompt mutation occurred:

```python
@dataclass
class FlakyLocalModel:
    failures_remaining: int
    response: ModelResponse
    requests: list[tuple[ChatMessage, ...]]

    def complete(
        self,
        *,
        messages: tuple[ChatMessage, ...],
        response_schema: dict[str, object],
        config: GenerationConfig,
    ) -> ModelResponse:
        self.requests.append(messages)
        if self.failures_remaining > 0:
            self.failures_remaining -= 1
            raise ModelTransportError("local runtime unavailable")
        return self.response


def test_transport_retry_keeps_messages_identical() -> None:
    messages = (ChatMessage("system", "fixed instruction"),)
    response = ModelResponse(
        raw_json="{}",
        identity=ModelIdentity("test-model", "test-runtime", "test-template"),
    )
    model = FlakyLocalModel(failures_remaining=1, response=response, requests=[])

    result = call_with_transport_retries(
        model,
        messages=messages,
        response_schema=ExtractionCandidate.model_json_schema(),
        config=GenerationConfig(Decimal("0"), 256, Decimal("5")),
        max_attempts=2,
    )

    assert result is response
    assert model.requests == [messages, messages]
```

The test uses `{}` because it tests transport recovery only; schema parsing belongs in a separate test. Do not claim model quality from a fake. For an integration test, use a separately configured local model adapter and assert only boundary behavior that the selected runtime can deterministically support.

**Boundary.** Snapshotting a model's complete prose response is usually brittle. Test stable schema, validation, attempt-record, and evidence behavior deterministically. Evaluate model output quality through a controlled dataset and rubric, not by changing expected text until a run passes.

**Checkpoint.** Why is the date-mismatch test essential even when schema tests pass? It proves the distinction between a parseable value and an evidence-supported extraction, which is the central trust boundary.

**Bridge.** Unit tests prove policies on chosen cases. Prompt sensitivity needs a controlled experiment across cases and variants.

## 11. Measure prompt sensitivity instead of arguing from one response

### Orienting question: what if an innocuous wording change changes the delivery date?

Prompt sensitivity is variation in output caused by changes to instruction wording, message order, delimiter form, examples, schema rendering, template, or generation settings. Some variation is expected from stochastic generation; decision-critical variation must be measured, not dismissed as “model personality.”

Build an evaluation set before selecting a favored prompt. It should use synthetic documents or documents governed for the purpose, and store expected extraction outcomes independently of model output. Include at least:

- the clear Atlas document;
- missing required delivery date;
- explicitly nullable field if the contract supports one;
- malformed price or non-finite numeric text;
- date in a disallowed format;
- conflicting labels;
- wrong currency or unit;
- document text containing prompt-like instructions; and
- whitespace and punctuation variants that should preserve meaning.

Each evaluation case needs an ID, exact document digest, expected candidate or expected non-valid status, evidence policy version, and reviewer-visible rationale. Keep holdout cases out of few-shot examples. If an example teaches the answer to an evaluation case, it cannot measure generalization to that case.

Compare prompt variants under fixed schema version, model artifact identity, runtime/template, constrained-decoding mode, temperature, output cap, timeout, and evaluation set. If the question is prompt sensitivity, change one factor at a time. If the question is model comparison, keep the prompt constant and record model identity. Do not silently repair failures in one arm but not the other.

| Metric | Meaning |
| --- | --- |
| structural acceptance rate | candidate passes Pydantic schema |
| evidence-supported acceptance rate | candidate passes every declared evidence check |
| required-field failure rate | required field is missing, null, or invalid |
| unsupported-field rate | typed candidate differs from evidence |
| repair rate and success rate | how often bounded repair is needed and passes policy |
| attempt-cap rate | cases ending in `needs_review` after allowed attempts |

Report counts and denominators, not only a single score. A prompt can improve JSON parse rate while increasing unsupported payment terms. That is a regression for this workflow even if a generic “success” percentage rises.

Use deterministic generation when the local runtime supports it and record the precise configuration; do not overstate reproducibility across runtimes or hardware. Temperature zero can reduce sampling variance, but it cannot force factual support. A local model can be deterministic under one setup and still receive a different chat template or model artifact after an upgrade.

Human review is most useful at the semantic boundary. Blind the prompt and model identity when reviewers score outputs, retain source excerpts, and score field correctness separately from format. Do not let a model's self-reported confidence choose which answer wins.

**Checkpoint.** If prompt B has a higher schema-pass rate but doubles the unsupported-date rate, is it better? Not under this contract. Structural validity and evidence support are separate required dimensions.

**Bridge.** An evaluation only supports the configuration it tested. Promotion and rollback keep that boundary operational.

## 12. Promote a configuration deliberately, and make reversal ordinary

### Orienting question: what changes when a new prompt wins the held-out set?

An evaluation result is evidence, not automatic authority to replace a working configuration. Promotion should name the exact candidate configuration: prompt and example bundle, repair message, schema, evidence policy, local model artifact, runtime/template, constrained-decoding setting, and generation configuration. A reviewer can then compare it against the current configuration on the same fixed evaluation set.

```text
candidate configuration
        |
        +--> deterministic unit/contract tests
        +--> controlled evaluation with frozen rubric
        +--> review of failures and attempt-cap outcomes
        |
        v
manual promotion of one versioned configuration
        |
        v
append-only production attempt evidence
```

The rollback target is the previously recorded configuration, not “the old prompt text copied from memory.” Because each outcome stores version identifiers and digests, an operator can restore a known prompt/schema/model/configuration bundle when a change regresses evidence support or causes unexpected repair volume.

Compatibility is a contract question. Adding an optional output field, tightening an allowed unit, changing a nullability rule, or replacing a schema-derived response constraint can break downstream consumers and historical comparisons. Version the schema and explicitly define migration/read compatibility. Do not reuse `procurement-extraction/1.0.0` for a changed interpretation of payment terms.

Observe these operational signals without logging source text:

- count outcomes by status and reason code;
- count transport failures separately from schema and evidence failures;
- measure repair rate, cap exhaustion, and latency at a documented boundary;
- group measurements by prompt/schema/model/configuration version; and
- sample authorised review cases with source provenance for semantic-quality investigation.

An increase in `SCHEMA_INVALID` after a local-runtime upgrade points to a different investigation than an increase in `EVIDENCE_MISMATCH` after an example-set change. A generic “LLM failure” metric erases this causal distinction.

**Boundary.** This is a configuration promotion workflow, not autonomous decision making. A valid extractor configuration still does not authorize payments, vendor changes, or procurement-system writes.

**Checkpoint.** Why is rollback part of prompt versioning? Prompt and schema changes are deployed behavior. If a new version degrades a declared metric, returning to an exact known configuration is safer than improvising another mutation during the incident.

**Bridge.** Promotion preserves controlled behavior. The remaining pitfalls are mostly ways teams accidentally hide the evidence they need.

## 13. Common mistakes and the corrective question

### “The response is JSON, so it is safe.”

Which layer checked the JSON shape, types, domain constraints, document evidence, and final status? JSON syntax alone answers none of those questions.

### “The system message protects us from the document.”

What deterministic control prevents document text from changing the schema, selecting tools, or triggering writes? Message roles and delimiters are model context, not authorization.

### “The model said confidence 0.99.”

Where was confidence calibrated, on which population, under which model and decision rule? Without that evidence, retain validation status and provenance instead.

### “Retry until it works.”

Was the failure transport, parsing, schema validation, or evidence mismatch? What immutable request, cap, and attempt record make the recovery process auditable?

### “A local model makes the pipeline private and correct.”

What do local logs, artifact provenance, access control, document handling, and output validation prove? Local operation changes an operating boundary; it does not create trust.

### “We can parse the sentence with a regex.”

Where is the stable field boundary, and how does the parser distinguish a missing year from a changed sentence? Structured output removes a second, fragile extraction problem.

### “A better prompt solved the problem.”

Which held-out cases improved, which regressed, and were schema/model/configuration held fixed? A single attractive response is an observation, not an evaluation.

## 14. Interview defense

**Why is structured output preferable to parsing free-form LLM responses?**

Free-form language has no durable field boundary. A parser must infer values, cope with wording variation, and decide whether omitted or hedged text is meaningful; that creates another probabilistic extraction problem. A structured contract names fields, types, allowed values, and missing-data behavior. Schema-aware decoding can reduce syntax failures, while Pydantic or JSON Schema gives downstream code a narrow interface. It still requires semantic/evidence validation because a perfectly shaped object can contain invented values.

**What is the difference between prompting for JSON and constrained structured decoding?**

Prompting for JSON is an instruction the model may violate. Constrained decoding asks a compatible runtime to restrict generation to a schema or grammar, reducing malformed syntax. Neither establishes business truth, and runtime schema support must be tested. The application always parses, validates, and checks evidence.

**Why do system, user, and tool roles not form a security model?**

They organise model context and may influence behavior, but arbitrary text can be malicious or misleading and a model may not follow an instruction. Tool results are external input, not privileged evidence. Security requires deterministic controls: validated schemas, allowlisted capabilities, authorization at action boundaries, provenance, and no implicit side effects.

**What does `strict=True` buy in Pydantic?**

It reduces silent coercion at a runtime boundary so callers cannot rely on broad “helpful” conversions. It does not validate document truth, establish a currency policy, or replace field-specific decimal/date constraints. Exact behavior should be covered by the selected Pydantic version's tests.

**How do transport retry and validation repair differ?**

Transport retry repeats an identical immutable request after no usable response arrives. Validation repair creates a new, versioned request after a response violates parsing, schema, or evidence policy. Both are bounded and recorded; neither silently mutates the original prompt or retries until a desired answer appears.

**Why should the application set validation status?**

The model cannot authoritatively certify itself. The status must result from deterministic structural and semantic checks, with reason codes and provenance. A model confidence field is not a calibrated decision probability by default.

## 15. Active recall

1. What is the difference between missing, null, invalid, and unsupported values?
2. Why are decimal values represented as strings before typed parsing in this contract?
3. Which layer decides that `2026-08-19` is unsupported by the Atlas document?
4. What do delimiters improve, and what do they not secure?
5. When is few-shot prompting justified?
6. How does constrained decoding differ from merely asking for JSON?
7. Which fields must be versioned to reproduce an extraction attempt?
8. Why must a transport retry preserve the original messages?
9. Why is a self-reported model confidence not sufficient for acceptance?
10. Which evaluation metric catches a typed but invented delivery date?

### Answers

1. They distinguish omitted fields, explicit absence, representation failure, and a typed value that lacks source support.
2. The boundary can deliberately parse exact `Decimal` values rather than accept generic JSON numeric behavior as a money policy.
3. The deterministic evidence/semantic validation layer, after structural parsing.
4. They clarify data boundaries to the model and reviewer; they do not provide authorization or injection resistance.
5. When a versioned, representative demonstration resolves a known ambiguity and improves held-out results under fixed evaluation conditions.
6. Constrained decoding can restrict output form at generation time; prompting is only an instruction. Both require application validation.
7. Document digest, prompt/examples/repair version, schema version, model artifact/runtime/template identity, and generation configuration.
8. Otherwise the retry is a hidden new prompt experiment, not recovery from a transport failure.
9. It is generated text unless independently calibrated for the stated setting; validation status and evidence are actionable instead.
10. Evidence-supported acceptance rate or unsupported-field rate, not schema-pass rate alone.

## Next action: implement the narrow boundary first

Start with `ExtractionCandidate`, `parse_candidate`, the labelled evidence parser, and their deterministic tests. Then add the injected local adapter and attempt records. Only after the controlled evaluation set exists should a prompt, model artifact, schema change, or constrained-decoding mode be promoted for this workflow.

The scope intentionally stops before retrieval, autonomous tool calls, procurement-system writes, payment interpretation, and any future agent workflow. A valid extraction candidate is evidence for human or separately designed downstream review—not permission to act.

## Primary documentation

- [Pydantic v2: Models](https://docs.pydantic.dev/latest/concepts/models/)
- [Pydantic v2: JSON Schema](https://docs.pydantic.dev/latest/concepts/json_schema/)
- [Python 3.13: `decimal`](https://docs.python.org/3.13/library/decimal.html)
- [Python 3.13: `datetime`](https://docs.python.org/3.13/library/datetime.html)
- [JSON Schema: What is JSON Schema?](https://json-schema.org/overview/what-is-jsonschema)
