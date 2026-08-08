---
layout: week
permalink: /weeks/week-04/beginner/
title: "Prompting and structured output: a beginner's introduction"
description: Learn to turn one procurement document into typed, reviewable data without trusting a model's prose.
summary: Follow a synthetic Atlas Metals order from document text to a validated extraction contract, then learn the prompting, validation, retry, and evaluation concepts that make the result usable.
kicker_primary: Prompting and structured output
kicker_secondary: Beginner context
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-04/
---

## One document, one bounded job

Imagine an operations inbox receives this synthetic procurement document:

```text
Purchase confirmation

Supplier: Atlas Metals
Product: Copper wire
Quantity: 1,000 kg
Unit price: USD 12.00 per kg
Delivery date: 2026-08-18
Payment terms: Net 30 after inspection approval
```

An analyst can read this in seconds. A downstream system cannot safely rely on someone copying it into a spreadsheet, nor can it reliably consume an assistant response such as “Atlas will deliver copper wire for twelve dollars next month.” We want an extractor that returns the facts in a predictable shape:

```json
{
  "supplier_name": "Atlas Metals",
  "product": "Copper wire",
  "quantity": "1000",
  "unit": "kg",
  "unit_price": "12.00",
  "currency": "USD",
  "delivery_date": "2026-08-18",
  "payment_terms": "Net 30 after inspection approval",
  "validation_status": "valid"
}
```

This is the application's final result, including its validation status. The model may propose the source fields, but it does not produce the authoritative status and is not the authority on whether a field is true. The document is still untrusted input, model output is still untrusted input, and a syntactically valid JSON object may still contain the wrong supplier, a guessed date, or a swapped currency.

This lesson follows that one document from raw text to a bounded extraction result. The goal is not to make an assistant sound convincing. It is to define a contract, check it deterministically, preserve evidence for review, and expose failure instead of silently inventing a value.

**Checkpoint.** Does valid JSON prove that Atlas Metals agreed to the stated terms? No. It proves only that some text has the required JSON shape. Factual support still needs evidence from the supplied document and the appropriate business review.

## The extraction contract comes before the prompt

Before writing an instruction, define what the output means. This is an **extraction contract**: a compact agreement about fields, types, allowed values, missing-data rules, and status.

For this mini-build, the fields are supplier name, product, unit price, quantity, delivery date, payment terms, currency, and validation status. The prompt should not decide these fields anew each time. The application owns the contract.

| Field | Meaning | Example type/value |
| --- | --- | --- |
| `supplier_name` | supplier named by the document | non-empty string, `Atlas Metals` |
| `product` | ordered item name | non-empty string, `Copper wire` |
| `quantity` | ordered numeric amount | `Decimal("1000")` |
| `unit` | quantity unit | `kg` |
| `unit_price` | agreed amount per unit | `Decimal("12.00")` |
| `currency` | price currency | `USD` |
| `delivery_date` | promised calendar date | `date(2026, 8, 18)` |
| `payment_terms` | payment condition as stated | `Net 30 after inspection approval` |
| `validation_status` | outcome of application validation | `valid`, `invalid`, or `needs_review` |

The quote marks around numeric JSON values in the first example are deliberate. JSON has one generic number type, while financial applications care about exact decimal representation. A typed validator can parse the string `"12.00"` into `Decimal("12.00")` rather than accept binary floating-point approximation. Similarly, the string `"2026-08-18"` becomes a `date` only after validation.

The contract also has to say what absence means. These three states differ:

| State | Example | Meaning |
| --- | --- | --- |
| Missing | `delivery_date` is absent from the object | producer did not supply the field |
| Null | `"delivery_date": null` | producer explicitly says no value is available |
| Invalid | `"delivery_date": "18/08/26"` when ISO date is required | a value was supplied but violates the contract |

Do not merge those states merely to make a pipeline continue. A missing mandatory field may need repair; a null-permitted field may be acceptable; an invalid field is evidence that the output failed validation. This mini-build requires every field name to be present. It permits `delivery_date` to be explicitly null when the document omits the date, but that outcome must be `needs_review`; the other business fields in this bounded contract are non-null. A fuller contract could define different nullability, but it must do so explicitly rather than guess.

```text
raw document
      |
      v
model candidate JSON -----> typed validation -----> accepted extraction
      |                           |
      |                           +-----> invalid / needs review, with reason
      v
preserved attempt and evidence
```

**Checkpoint.** Is `"quantity": "one thousand"` necessarily wrong? Not as document text, but it is invalid for a contract that requires a decimal numeric representation. The system can request a corrected representation or route the attempt for review; it should not silently infer a numeric value without an explicit policy.

## A prompt is an input program

A prompt is not magic wording. It is structured input that tells a language model what task to attempt, what evidence it may use, and what output contract it must follow. Its quality comes from clarity, constraints, examples when needed, and evaluation—not from grand claims about the model's intelligence.

For a simple extractor, make the task boundary clear with delimiters. Delimiters mark where untrusted source material starts and ends:

```text
Extract only facts explicitly stated in the procurement document.
Return one JSON object matching the supplied schema.
Do not infer missing values. Use the validation-status rules.

<procurement_document>
Supplier: Atlas Metals
Product: Copper wire
Quantity: 1,000 kg
Unit price: USD 12.00 per kg
Delivery date: 2026-08-18
Payment terms: Net 30 after inspection approval
</procurement_document>
```

Delimiters improve readability and reduce accidental mixing of instructions with document text. They are **not security boundaries**. A document can contain text that looks like an instruction, and a model can still follow it. The application must treat document content as data, apply size and format controls at the input boundary, and validate the final output independently. Never conclude that “ignore previous instructions” inside a prompt secures a workflow.

### System, user, and tool messages

Chat-style model interfaces usually organise a conversation into roles:

- A **system message** sets durable application-level behavior, such as “extract only explicitly stated fields; emit the defined object.”
- A **user message** contains the task and the bounded procurement document.
- A **tool message** contains the recorded result of a tool call, such as a document parser returning text.

These roles help the model distinguish context, but their names do not grant trust. A tool parser can return malformed or hostile text. A user-supplied document can include misleading instructions. A model can misunderstand a system instruction. Validate content based on its source and contract, not the chat role used to carry it.

For this beginner lesson, the document is passed as text and the model does not execute tools. Future retrieval and tool execution introduce separate authorization, provenance, and execution boundaries; they are intentionally outside this Week 4 extractor.

## Start simple: zero-shot, then few-shot

A **zero-shot** prompt gives instructions but no example input/output pair. The delimited prompt above is zero-shot. It is often the right place to start because it tests whether the instruction and schema are clear without hiding ambiguity inside examples.

A **few-shot** prompt adds a small number of carefully chosen demonstrations. Examples show the mapping, not merely the desired prose style. For example, an optional example could prove how a missing delivery date is represented:

```text
Example document:
Supplier: Atlas Metals
Product: Copper wire
Quantity: 50 kg
Unit price: USD 12.00 per kg
Payment terms: Net 30 after inspection approval

Example result:
{"supplier_name":"Atlas Metals","product":"Copper wire",
 "quantity":"50","unit":"kg","unit_price":"12.00","currency":"USD",
 "delivery_date":null,"payment_terms":"Net 30 after inspection approval"}
```

The example is useful only if the contract says when null is permitted. After validation, the application assigns this case `needs_review`; that status is not part of the model candidate. Too many examples consume context, can anchor the model to irrelevant wording, and can accidentally teach a bad shortcut. Keep examples short, representative, and versioned along with the prompt.

**Checkpoint.** Should few-shot examples replace validation code? No. Examples influence model behavior. Validation code decides whether a particular response satisfies the application contract.

## Role prompting is a style aid, not an authority

**Role prompting** gives the model a perspective, for example: “You are a procurement-document extraction assistant.” It can focus wording and encourage task-relevant behavior, especially when combined with explicit constraints.

It does not give the model procurement expertise, access to a contract system, permission to approve payment terms, or a factual guarantee. “You are a meticulous auditor” cannot turn an unsupported delivery date into a supported one. Prefer requirements that can be checked:

```text
Extract only text supported by the delimited document.
Return fields exactly as defined by the schema.
For an absent required field, do not guess; return the declared non-valid status.
```

Role language can remain as a small orienting sentence. The extraction contract, schema, validation, evidence capture, and review policy do the safety-critical work.

## Why structured output beats parsing prose

Consider these two model responses:

```text
Atlas Metals will deliver 1,000 kg of copper wire on August 18.
Payment is Net 30 once the inspection has been approved.
```

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

The prose is readable, but a program must guess where each fact begins, whether “August 18” includes a year, whether “once” preserves the contractual condition, and whether USD 12 was omitted or misunderstood. Small wording changes can break a fragile parser. Parsing prose after the fact creates a second extraction problem.

Structured output assigns a stable name and expected type to each value. A JSON Schema or Pydantic model can reject extra fields, missing mandatory fields, wrong units, invalid dates, malformed decimals, and status values outside an allowlist. That gives downstream code a narrow interface rather than a sentence-completion interface.

Two mechanisms are often given the same “structured output” label. A prompt can merely *ask* the model to emit JSON, in which case it may still return prose or malformed structure. A runtime can instead constrain decoding with a supported schema or grammar, which can reduce syntax and shape failures. That capability is runtime-specific, and neither mechanism proves that extracted values are supported. Always validate the received object at the application boundary.

Structured output is not truth. The model could return a fully valid object with `"delivery_date": "2026-08-28"`. Schema-valid is not necessarily semantically correct: the schema checked shape and types, while semantic validation must compare the candidate against document evidence or a deterministic business rule.

## Validate with JSON Schema or Pydantic

JSON Schema is a language-neutral way to declare allowed JSON structure. Pydantic provides a Python model that parses and validates values into typed objects. Both can represent a boundary contract; choose the established project convention when implementing.

Here is a compact Pydantic-style shape. It illustrates types and constraints rather than a complete production policy:

```python
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProcurementCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    supplier_name: str = Field(min_length=1, max_length=200)
    product: str = Field(min_length=1, max_length=200)
    quantity: Decimal = Field(gt=0)
    unit: Literal["kg", "ea"]
    unit_price: Decimal = Field(ge=0)
    currency: Literal["USD"]
    delivery_date: date | None
    payment_terms: str = Field(min_length=1, max_length=200)
```

`extra="forbid"` prevents unnoticed fields—including a model-authored status or confidence—from slipping through the stated candidate contract. `Decimal` and `date` express the types needed by the application after parsing. The annotation `date | None` has no default, so the key remains required even though its value may be null. The application assigns a null date `needs_review` after validation; the candidate cannot certify itself. The `Literal` examples are intentionally narrow for this bounded exercise; a real currency or unit policy should be explicitly designed, not expanded implicitly by a model response.

Because the candidate arrives as JSON, validate the raw JSON bytes or text with `ProcurementCandidate.model_validate_json(...)`. Pydantic's strict JSON handling can convert the JSON string forms shown above into `Decimal` and `date`; validating an already-decoded Python dictionary follows different strict-conversion rules.

Validation can establish facts such as “quantity is a positive decimal” and “delivery date parses as an ISO date.” It cannot establish “this delivery date was actually stated in the document.” Add separate semantic checks and evidence where needed. One simple approach is to preserve the source span or quoted text supporting each field, then compare it with the candidate value under a deterministic normalization policy.

```text
candidate: delivery_date = 2026-08-18
evidence:  "Delivery date: 2026-08-18"
                 |
                 v
typed parse + support check -> validation status
```

Do not use a model-reported `confidence: 0.98` as a calibrated probability. Unless calibration has been separately measured for a specified model, task, and distribution, that number is merely another model-generated field. Prefer a validation status, explicit reasons, and provenance such as document ID, document digest, source span, schema version, prompt version, model identifier, and timestamp.

**Checkpoint.** What happens if the model adds `validation_status: "valid"`? The candidate schema rejects the unexpected field. The application—not the model—sets status after validation and evidence checks.

## Version the instructions and their contract

The output depends on more than the document. It depends on the prompt wording, schema, model, model configuration, and message template. If any changes, a comparison may no longer be apples-to-apples.

Record at least:

```text
document digest and source identifier
prompt version: procurement-extract/1.0.0
schema version: procurement-extraction/1.0.0
model identifier and runtime version
sampling and output-limit settings
attempt number, timestamp, candidate output, validation result
```

Versioning is not bureaucracy. It lets an operator answer, “Which instruction produced this candidate?” and safely evaluate a new prompt or model before it replaces an old one. Do not silently mutate a prompt between attempts; preserve the exact prompt or a content digest and explicit version. A repair prompt is a new, recorded input, not a hidden retry.

## Retries: transport is not validation repair

Failures have different causes and need different handling.

A **transport retry** addresses a failure before a usable model response arrives: a local runtime is temporarily unavailable, a connection resets, or a timeout occurs. It should be bounded, use a documented backoff policy, and preserve the original request identity. Repeating it does not change the task or prompt.

A **validation repair** begins after a response arrives but fails parsing, schema validation, or a declared semantic check. The repair request should say what failed while preserving the original document, contract, and candidate. For example:

```text
The previous candidate failed validation because delivery_date must use YYYY-MM-DD.
Return a replacement object using only the source document. Do not add fields.
```

This is not permission to keep asking until a convenient answer appears. Cap repair attempts, record every candidate and failure reason, and return a visible non-valid result when the cap is reached. A bounded sequence might be:

```text
attempt 1: candidate fails date validation
attempt 2: explicit repair candidate fails evidence check
attempt 3: stop; status = needs_review, preserve both attempts
```

Avoid silent prompt mutation such as automatically adding increasingly forceful instructions without recording them. It destroys reproducibility and can conceal a model's sensitivity to wording. It is also dangerous to retry a validation failure as though it were a network error: the two failures signal different operational problems.

## Prompt sensitivity requires evaluation

Language models can change output when formatting, order, delimiters, examples, or harmless-looking phrasing changes. This is **prompt sensitivity**. It is not necessarily a defect in every case, but an extractor should measure it before claiming reliability.

Create a small held-out evaluation set of synthetic or appropriately governed documents. Include clear cases, missing fields, null-permitted fields, alternative date formats, units, conflicting-looking statements, unsupported instructions inside document text, malformed prices, and near-duplicate wording. Keep expected outcomes and the evaluation policy separate from the prompt being tested.

For each case, evaluate at least four dimensions:

| Dimension | Question |
| --- | --- |
| Parse and schema | Is the candidate valid under the declared structural contract? |
| Field correctness | Do values match the labelled source facts? |
| Missing-data behavior | Did it avoid inventing values and use the prescribed status? |
| Evidence/provenance | Can a reviewer trace the candidate to the input and configuration? |

Run controlled prompt variants against the same cases and freeze the model, schema, settings, and scoring rules while comparing them. Report the observed failures, not only a pass rate. A prompt that produces clean JSON but invents payment terms is not ready for operational use.

No paid or hosted API is assumed here. A local runtime, a mocked adapter in tests, or another approved model boundary can produce candidates. Local inference can reduce a network boundary, but it does not make document content, tool results, or model output trusted. The same contract, validation, attempts, and evaluation discipline still applies.

**Checkpoint.** If two prompts both pass ten easy examples, can we declare them equivalent? No. They may differ on missing fields, adversarial document text, formatting variation, or cases outside that small sample. The result is bounded evidence, not a universal guarantee.

## The mini-build, assembled

The beginner implementation has one modest purpose: transform the Atlas Metals document into a typed result with visible status. It should produce these fields:

```text
supplier_name       Atlas Metals
product             Copper wire
quantity            Decimal("1000")
unit                kg
unit_price          Decimal("12.00")
currency            USD
delivery_date       date(2026, 8, 18)
payment_terms       Net 30 after inspection approval
validation_status   valid, invalid, or needs_review
```

A complete result should also keep provenance outside, or alongside, the business payload: input document identifier or digest, source excerpt locations, prompt version, schema version, model/runtime identity, attempt number, and validation reason. Do not put an unaudited model confidence score in place of this evidence.

The narrow workflow is:

```text
bounded document text
        |
        v
versioned messages + extraction schema
        |
        v
untrusted candidate object
        |
        +--> typed/schema validation
        +--> declared semantic/evidence checks
        |
        v
valid result or preserved needs-review outcome
```

This Week 4 scope ends at extraction and validation. It does not retrieve external knowledge, execute tools on a model's behalf, update a procurement system, or decide that payment is due. Those functions require distinct future designs and controls.

## Readiness checklist

- [ ] I can define an extraction contract before choosing prompt wording.
- [ ] I can explain what system, user, and tool roles organise, and why none is a security boundary.
- [ ] I can distinguish zero-shot, few-shot, and role prompting, including their limits.
- [ ] I can explain why a named, typed object is safer for software integration than parsing prose.
- [ ] I can distinguish schema validity from factual or semantic correctness.
- [ ] I can distinguish missing, null, and invalid values without silently filling them in.
- [ ] I know why `Decimal` and `date` validation suit the quantity, price, and delivery fields here.
- [ ] I can record prompt, schema, model, settings, evidence, attempts, and validation status for reproducibility.
- [ ] I can distinguish a bounded transport retry from a bounded validation-repair attempt.
- [ ] I can describe a prompt-sensitivity evaluation without assuming local or hosted output is trusted.

Continue with the [production version]({{ '/weeks/week-04/' | relative_url }}). It hardens this contract with fuller interfaces, failure handling, tests, and operational trade-offs.
