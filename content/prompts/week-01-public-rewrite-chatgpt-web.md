# Week 1 Public-Lesson Rewrite Instructions

## Purpose

Peer review found the approved technical material accurate but difficult to learn
from: it is dense, lacks narrative flow, repeats planning information, and exposes
internal generation and review details. This rewrite creates a learner-facing
lesson while keeping technical provenance in separate review files.

## Files to attach

Attach:

1. `content/weeks/week-01.md`
2. `content/outlines/week-01-outline.md`
3. `content/reviews/week-01-technical-review.md`

The first file is a technical source, not a structure to preserve. The outline
defines topic coverage. The review defines verified facts and corrections.

## Prompt to paste

```text
Rewrite the attached Week 1 material as a cohesive, learner-facing technical
lesson for an experienced Data Scientist / ML Engineer moving into production
Applied AI engineering.

Return exactly one Markdown document. Do not return a patch, commentary, or an
outer code fence.

## Central teaching story

Use one continuous scenario: a procurement team needs a small API that accepts an
uploaded UTF-8 text document and returns validated structured JSON. Begin with a
naive route and improve it only when the story encounters a concrete problem.

The architecture should emerge in this sequence:

1. A naive endpoint mixes validation, decoding, business rules, and logging.
2. Functions and modules separate stateless transformations and responsibilities.
3. Classes become justified by state, dependencies, or lifecycle—not by style.
4. Type hints describe internal contracts but do not validate untrusted runtime
   input.
5. Pydantic `BaseModel` classes validate scalar multipart metadata at the HTTP
   boundary.
6. Frozen dataclasses carry already-validated domain values internally.
7. A narrow decoder protocol and composition isolate UTF-8 decoding.
8. Explicit exceptions preserve failure categories and causal context.
9. Safe structured logs explain lifecycle and failure without exposing content or
   filenames.
10. Generators are introduced through a real memory/lifecycle trade-off, not as an
    isolated language feature.
11. Async is introduced because `UploadFile.read()` is awaitable, while clearly
    explaining blocking I/O, thread pools, CPU work, cancellation, and why `async
    def` is not automatically faster.
12. A thin FastAPI route composes the pieces and enforces the bounded upload.
13. Tests prove behavior and failure handling at model, service, decoder, logging,
    and HTTP boundaries.

Each chapter must create the need for the next chapter. Use transitions that
explain what the current design still gets wrong and why the next concept solves
that specific problem.

## Public document structure

Use this front matter exactly:

---
layout: week
permalink: /weeks/week-01/
description: Build a typed, validated and testable document extraction API with Python and FastAPI.
title: Python for production AI systems
---

After the front matter, use exactly these H2 sections:

1. `## The service we are building`
2. `## From one route to deliberate design`
3. `## Classes should earn their place`
4. `## Types inside, validation at the boundary`
5. `## Model trusted state explicitly`
6. `## Make failures part of the design`
7. `## Observe behavior without leaking data`
8. `## Laziness, concurrency and resource lifetime`
9. `## Assemble the FastAPI boundary`
10. `## Prove the behavior with tests`
11. `## Practice and interview lab`
12. `## References`

Do not add public sections named Overview, Learning outcomes, Prerequisites,
Concept map, Weekly deliverables, Definition of done, Assumptions, Review history,
Testing and validation, or Guided implementation.

## Teaching style

- Write as a senior engineer mentoring another experienced engineer.
- Prefer causal explanation: problem -> constraint -> design choice -> consequence.
- Define terminology at first use, then apply it immediately.
- Use short focused code excerpts instead of complete-file dumps.
- Before each excerpt, state the question it answers; after it, explain the
  important lines and trade-offs.
- Use one evolving architecture diagram and update it as responsibilities split.
- Include brief recurring callouts when useful:
  - `> **Design checkpoint:** ...`
  - `> **Common trap:** ...`
  - `> **Try it:** ...`
- Use comparison tables only when they clarify an actual decision.
- Remove repetition and encyclopedic lists that interrupt the main flow.
- Keep explanations technically deep; improved flow must not mean superficial
  content.
- Do not impose an eight-hour or any other time limit.

## Technical contract

The public lesson must preserve this verified behavior:

- Python 3.13.12 and `pip`.
- FastAPI 0.139.2 and Pydantic 2.13.4 concepts.
- Multipart fields: `media_type`, `correlation_id`, and `file`.
- `UploadFile`; never a caller-controlled server filesystem path.
- Maximum upload: 1 MiB, read as limit plus one sentinel byte.
- HTTP 413 with `document_too_large` when oversized.
- Filename suffix `.txt`.
- Declared and upload media types must both be `text/plain` and match.
- Strict UTF-8 decoding.
- Empty or whitespace-only documents are rejected.
- Newlines are normalized without silently trimming other whitespace.
- Pydantic validates scalar boundary metadata.
- Filename and upload content type come from `UploadFile`; they are not Pydantic
  request fields.
- Frozen dataclasses represent internal command/result values.
- `TextReader.decode(content: bytes) -> str` is the narrow injected protocol.
- The route is thin and `async` because upload reading is awaitable.
- Domain logic remains synchronous.
- `python-multipart==0.0.32` is a runtime dependency.
- `httpx2==2.7.0` is the resolved endpoint-test dependency.
- Logs exclude raw content and filenames; structured `extra` values are asserted
  through `caplog.records`, not assumed to appear in `caplog.text`.

## Code policy

Do not reproduce complete repository files. Use only focused excerpts needed to
teach a decision. For every excerpt derived from verified source, place one of
these exact markers immediately before the code fence:

<!-- VERIFIED_EXCERPT: models -->
<!-- VERIFIED_EXCERPT: domain -->
<!-- VERIFIED_EXCERPT: ports -->
<!-- VERIFIED_EXCERPT: readers -->
<!-- VERIFIED_EXCERPT: errors -->
<!-- VERIFIED_EXCERPT: service -->
<!-- VERIFIED_EXCERPT: api -->
<!-- VERIFIED_EXCERPT: tests -->

Use a marker more than once if separate excerpts from the same file are needed.
Codex will replace generated excerpts with exact extracts from the verified
repository. Do not claim an excerpt was executed.

## Practice and interview material

Integrate exercises after the concepts they reinforce, but consolidate the final
challenge and interview material under `Practice and interview lab`.

Include:

- one progressive implementation challenge;
- boundary and failure-path exercises with acceptance criteria and hints;
- senior-level questions on mutable versus immutable objects, plain classes versus
  dataclasses versus Pydantic, static typing versus runtime validation, generators
  versus lists, threads versus async, exception translation, safe logging, thin
  routes, bounded uploads, and unsafe server paths;
- strong-answer frameworks and follow-up questions rather than memorized scripts;
- a compact knowledge check with answers placed after the questions.

## Information that must not appear publicly

Remove every reference to:

- Codex;
- ChatGPT or model generation;
- technical-review or HITL status;
- human approval;
- draft or publication status;
- review dates or content versions;
- test-run transcripts attributed to reviewers;
- prompt instructions;
- approved outlines;
- weekly schedules, roadmap administration, or completion checklists;
- internal file-integration markers other than the `VERIFIED_EXCERPT` markers;
- claims that the lesson or commands were generated, reviewed, approved, or
  executed.

The lesson may say which tests learners should run and what behavior those tests
should assert. It must not publish internal validation history.

## Sources

- Retain direct links to authoritative Python, Pydantic, FastAPI, Starlette, and
  pytest documentation that support the lesson.
- Cite sources naturally near version-sensitive claims and provide a compact
  References section.
- Do not fabricate citations or claim every link was checked during generation.

Before responding, silently verify that the narrative flows from one design
pressure to the next, all required concepts remain covered, exactly 12 H2 sections
exist, no internal process information remains, and every code excerpt has the
appropriate verification marker.
```

## Save the response

Save the exact response as:

```text
content/inbox/week-01-public-rewrite.md
```

Do not overwrite the approved technical source. Codex will validate the rewrite,
replace marked excerpts with verified source, and create a new HITL candidate.
