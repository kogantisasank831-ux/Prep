# Week 1 ChatGPT Web Revision Instructions

## Files to attach

Attach these files to a new ChatGPT Web conversation:

1. `content/inbox/week-01-draft.md`
2. `content/outlines/week-01-outline.md`
3. `content/reviews/week-01-technical-review.md`
4. `requirements.txt`
5. `requirements-dev.txt`

The verified implementation lives in `document_service/` and `tests/`. If the
Web interface supports a directory or archive attachment, include those two
directories as well. Otherwise, the revision may leave the guided implementation
code blocks marked `Codex integration required`; Codex will insert the verified
files without asking ChatGPT to reconstruct them.

## Prompt to paste

```text
Revise the attached Week 1 draft into a review candidate using the approved
outline and technical-review findings as binding inputs.

Return exactly one complete Markdown document. Do not return a patch, summary,
commentary, or surrounding code fence.

Required corrections:

1. Preserve all 18 required H2 sections and their order.
2. Use valid YAML front matter closed by exactly `---`.
3. Keep status `draft`, increment version to `0.2.0`, and keep human review
   `pending`.
4. Replace the caller-controlled server-path API everywhere with a bounded
   multipart `UploadFile` API.
5. The verified HTTP contract contains multipart fields `media_type`,
   `correlation_id`, and `file`.
6. The route reads at most 1 MiB plus one sentinel byte and returns HTTP 413 with
   code `document_too_large` when the limit is exceeded.
7. Require filename suffix `.txt`, declared media type `text/plain`, matching
   upload content type `text/plain`, strict UTF-8 decoding, and non-whitespace
   content.
8. Never accept or open a server filesystem path. Remove path traversal, missing
   server file, `tmp_path`, and arbitrary-path examples that no longer apply.
9. Replace the filesystem reader with an injected UTF-8 byte decoder whose narrow
   protocol is `decode(content: bytes) -> str`.
10. Explain that `UploadFile.read()` is awaitable, so the thin route is `async
    def`; do not expand into production async deployment or concurrency tuning.
11. Use `python-multipart==0.0.32` for multipart parsing and `httpx2==2.7.0` for
    the resolved Starlette test client. Do not instruct installation of `httpx`.
12. Correct the Windows newline fixtures: when exact newline bytes matter, use
    `write_bytes()` or direct byte payloads instead of relying on text-mode
    `Path.write_text()` behavior.
13. Correct logging tests: fields supplied via `extra` are attributes on captured
    `LogRecord` objects and are not guaranteed to appear in `caplog.text` unless
    the formatter renders them.
14. Do not claim that ChatGPT executed anything. Add a clearly attributed
    technical-review record stating that Codex executed the repository suite on
    Python 3.13.12 with 26 tests passing, Ruff lint/format passing, and strict mypy
    passing. State that these results apply to repository files, not every
    isolated narrative snippet.
15. Preserve the detailed Python classes, Pydantic v2, exception, logging,
    generator, async, pytest, exercise, and interview content unless it conflicts
    with the revised upload design.
16. Preserve primary-source URLs, update upload/testing sources where necessary,
    and do not fabricate source verification.
17. Remove statements that maximum size is deferred; making the fixed 1 MiB limit
    configurable may remain an exercise.
18. Keep response-size limits, authentication, persistence, deployment, advanced
    streaming, and authorization explicitly outside Week 1 scope.

If the verified `document_service/` and `tests/` files are attached, reproduce
their content exactly in the guided implementation and testing sections. Do not
invent improvements or alternate APIs. If they are not attached, preserve the
section structure and insert `Codex integration required` where verified code
must be placed.

Before responding, silently check that no server-path API, `httpx` installation,
invalid YAML delimiter, false execution claim, or eight-hour constraint remains.
```

## Save the response

Save the exact response as:

```text
content/inbox/week-01-draft-v2.md
```

Do not overwrite the original draft and do not promote the revision directly to
`content/weeks/week-01.md`.
