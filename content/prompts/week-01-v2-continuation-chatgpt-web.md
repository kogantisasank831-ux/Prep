# Week 1 V2 Continuation Instructions

## Why this continuation is required

`content/inbox/week-01-draft-v2.md` was truncated inside the test-coverage table
under `## Testing and validation`. Do not regenerate the completed portion. Create
only the missing continuation so Codex can join it at a controlled section
boundary.

## Files to attach

1. `content/inbox/week-01-draft-v2.md`
2. `content/outlines/week-01-outline.md`
3. `content/reviews/week-01-technical-review.md`

## Prompt to paste

```text
Continue the attached Week 1 V2 draft without repeating its existing content.
The attached V2 file was truncated inside `## Testing and validation`, in the
`### Required test categories` table. Return only a Markdown fragment that Codex
can splice into the document.

Begin your response with this exact marker on its own line:

<!-- CONTINUATION_START: testing-matrix -->

Immediately after the marker, write a complete replacement for:

### Required test categories

Include the full table from its header onward. Then finish `## Testing and
validation` and provide all remaining required H2 sections, in exactly this order:

## Interview preparation
## Knowledge check
## Weekly deliverables
## Definition of done
## Sources and further reading
## Assumptions and unresolved questions
## Review history

Binding requirements:

1. Use the approved bounded multipart `UploadFile` design only. Never reintroduce
   a caller-controlled server filesystem path.
2. Cover the multipart fields `media_type`, `correlation_id`, and `file`.
3. Cover the 1 MiB plus sentinel-byte read, HTTP 413, `.txt`, matching
   `text/plain` media types, strict UTF-8, and empty-content rejection.
4. Use `python-multipart==0.0.32` and `httpx2==2.7.0`; do not instruct installing
   `httpx`.
5. Preserve the distinction between `caplog.text` and structured attributes on
   `caplog.records`.
6. State that exact verified repository tests will be inserted by Codex when
   needed; do not reconstruct unattached source files.
7. Attribute the recorded 26 passing tests, Ruff results, and strict mypy result
   to Codex technical review. Do not claim ChatGPT executed them.
8. Interview material must include strong answers, trade-offs, and follow-up
   questions for mutable versus immutable objects, class choices, static typing
   versus runtime validation, generators versus lists, threads versus async,
   exception translation, safe logging, thin routes, bounded uploads, and why
   arbitrary server paths are unsafe.
9. Include a substantive knowledge check with an answer key.
10. Include reviewable deliverables and a checkbox-based definition of done.
11. Use primary official sources and direct URLs. Do not fabricate citations or
    claim every link was verified.
12. Keep response-size limits, authentication, authorization, persistence,
    deployment, advanced streaming, and concurrency tuning outside Week 1.
13. In review history, record ChatGPT Web V2 generation separately from Codex
    technical verification and leave human review pending.
14. End with this exact marker on its own line:

<!-- CONTINUATION_END -->

Return the Markdown fragment only. Do not include commentary or wrap the whole
fragment in a code fence.
```

## Save the response

Save the exact response as:

```text
content/inbox/week-01-draft-v2-part2.md
```

Do not append it manually to V2. Codex will remove the truncated table, splice at
the controlled marker, insert verified repository code, repair the YAML delimiter,
and validate the combined review candidate.
