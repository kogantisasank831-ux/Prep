# Week 4: procurement extraction lab

Turn a synthetic purchase confirmation into a typed candidate, then check every
field against the source. This lab accompanies the
[main lesson](https://kogantisasank831-ux.github.io/Prep/weeks/week-04/) and
[beginner lesson](https://kogantisasank831-ux.github.io/Prep/weeks/week-04/beginner/).

## Run from the repository root

Use the project's Python environment and existing dependency files:

```shell
python -m pip install -r requirements-dev.txt
python -m labs.week_04.extractor
python -m pytest tests/test_week04_extractor.py -q
```

The underscore in `week_04` makes the directory importable as a Python namespace
package. Run commands from the repository root rather than from this directory.

The demo prints `demo_mode: scripted; no LLM call`, `validation_status: valid`,
one attempt, and the eight expected candidate fields. The model boundary returns
a predetermined response. No inference, network request, GPU, model download, or
credential is involved. Test success demonstrates policy behavior on fixtures;
it is not a measurement of a model's quality, speed, or structured-decoding support.

## Follow the code

1. `ExtractionCandidate` forbids extra fields, requires decimal strings on the
   JSON boundary, and parses dates and amounts into typed values. All eight keys
   are required; only `delivery_date` may be null.
2. `parse_labelled_evidence` handles the controlled fixture grammar. It rejects
   repeated/unknown labels, unexpected lines, malformed grouping, missing required
   facts, non-USD prices, and quantity/price-unit disagreement. It accepts an
   optional `Purchase confirmation` title, blank lines, and case-insensitive
   labels. Values retain their contractual wording.
3. `parse_candidate` bounds JSON to 32 KiB, rejects repeated keys and non-standard
   constants, then applies Pydantic. Source text is bounded to 1 MiB of UTF-8.
4. `mismatched_fields` compares decimal amounts numerically and text exactly.
   Schema validity alone cannot make an invented date pass.
5. `extract` sets the final status, records every call, and separates identical
   transport retries from versioned validation repairs. Default caps allow at
   most four calls: two transport attempts in each of two rounds.

Final statuses are `valid` and `needs_review`. An individual rejected response
has an attempt reason such as `SCHEMA_INVALID` or `EVIDENCE_MISMATCH`. Exhausted
repair returns `REPAIR_EXHAUSTED`; transport exhaustion returns
`TRANSPORT_EXHAUSTED`. A missing source date with a null candidate returns
`DELIVERY_DATE_ABSENT`. A source rejected before inference has no model-call
records and reason `DOCUMENT_INVALID`.

The output candidate remains a proposal even when valid. Status does not approve
commercial terms or authorize a write. A digest is an equality/provenance aid,
not encryption or storage of the original payload. Invalid UTF-8 represented by
unpaired surrogates has no exact UTF-8 document digest, so the result uses null.

## Sample data and prompt comparison

`evaluation_cases.jsonl` contains twelve manually specified synthetic cases:
six development and six holdout cases. Each includes a stable ID, policy version,
source text, expected candidate (or null), expected status, and reason.

Use development cases when designing few-shot demonstrations. Freeze a candidate
prompt before evaluating it on holdout cases; do not keep selecting prompts on
the same holdout and continue calling it unseen. The published split supports a
learning exercise, not an independent benchmark certification.

Expected labels apply to the narrow `labelled-usd/1.1.0` policy, including its
nullable-date rule. Rejected formats are review cases, not extraction permission
to guess a conversion. Record the model artifact/runtime/template identity,
generation settings, decoding mode, schema version, prompt/example version,
per-case responses, and denominators when running an actual model. Keep expected
labels out of model messages. Report parse/schema pass, field support, review
rate, repair volume, latency, and unavailable measurements separately.

## Exercises

- Replace the candidate's date with another valid date and observe the evidence
  failure.
- Remove the source date and return null; observe review without an invented date.
- Compare `12.0` with `12.00`, then drop the inspection condition from payment
  terms. Explain why their acceptance differs.
- Use the test fake to simulate timeout → invalid candidate → timeout → repair.
  Inspect four records and the distinct prompt versions.
- Add duplicate source labels and duplicate JSON keys. Explain why neither may
  use last-write-wins semantics here.

## Boundaries to retain

This controlled grammar can already be parsed deterministically. A real project
with consistently labelled documents should consider using that parser directly.
The model proposal is retained here to teach an application boundary. Broader
documents need a new evidence policy and evaluation, not an assertion that this
parser is a general fact checker or prompt-injection detector.

Records are in memory. The lab does not implement durable audit storage,
retention/access controls for real documents, a live model adapter, retry delays,
overall deadlines, provider-specific schema translation, or a deployed API.
Real integrations must enforce those controls and validate runtime envelopes and
finish reasons before delivering `ModelResponse`. No model quality results are
claimed by this exercise.
