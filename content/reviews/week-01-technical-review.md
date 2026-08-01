---
week: 1
draft_version: 0.1.0
review_date: 2026-07-21
review_status: approved
reviewer: Codex
---

# Week 1 Technical Review

## Outcome

The draft covers the approved Week 1 outline comprehensively, but it is not ready
for human approval or publication without corrections. The extracted
implementation passes its tests after three generated test defects were fixed.
The project owner approved the recommended upload boundary on 2026-07-22. The
executable implementation is verified; the generated lesson still needs to be
revised to match it.

## Environment

- Operating system: Windows
- Python: 3.13.12
- pip: 25.3
- FastAPI: 0.139.2
- Pydantic: 2.13.4
- python-multipart: 0.0.32
- Starlette: 1.3.1
- HTTPX2: 2.7.0
- Uvicorn: 0.51.0
- pytest: 9.1.1
- Ruff: 0.15.22
- mypy: 2.3.0

Top-level dependencies are recorded in `requirements.txt` and
`requirements-dev.txt`. These files pin direct dependencies but are not a
hash-locked record of all transitive packages.

## Structural review

### Passed

- All 18 required H2 sections are present and in the required order.
- The draft covers FastAPI, classes, Pydantic v2, dataclasses, type hints,
  exceptions, logging, generators, async fundamentals, testing, exercises, and
  interview preparation.
- All code fences declare a language.
- Independent exercises contain acceptance criteria, edge cases, and hints
  without complete solutions.
- The draft does not claim that its generated code was executed.
- The sources section uses primary documentation and specifications.

### Required corrections

1. The YAML front matter closes with `---------------------` rather than `---`.
   The canonical weekly document must use a valid closing delimiter.
2. The dependency instructions prescribe `httpx`, but Starlette 1.3.1 emits a
   deprecation warning and requests `httpx2`. The current tested dependency is
   `httpx2==2.7.0`.
3. The generated code and test blocks must be updated to match the verified files
   in `document_service/` and `tests/`.
4. The validation-status section must record the actual commands, versions,
   initial failures, corrections, and final results.
5. The review history must distinguish ChatGPT-generated content from corrections
   made during Codex technical review.

## Execution results

### Initial generated suite

Command:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Result: **failed — 3 failed, 24 passed, 1 warning**.

Failures:

1. `test_reader_reads_utf8_text` used `Path.write_text()` and assumed `\n` bytes.
   On Windows, text-mode newline translation wrote `\r\n`, while the reader
   deliberately used `newline=""` to preserve raw newlines.
2. `test_extract_endpoint_success` wrote an explicit `\r\n` through text mode on
   Windows, producing `\r\r\n`. Normalization correctly converted that byte
   sequence to two newlines, contradicting the generated expected result.
3. `test_service_does_not_log_document_text_or_path` expected a field supplied
   through `logging`'s `extra` argument to appear in pytest's default formatted
   `caplog.text`. Extra fields are stored on captured `LogRecord` objects and need
   not be rendered by the active formatter.

Warning:

- Starlette deprecated using `httpx` for `TestClient` and requested `httpx2`.

### Corrections applied to executable tests

- Binary fixtures now use `Path.write_bytes()` so newline bytes are deterministic
  across operating systems.
- The logging assertion now checks the captured `LogRecord.correlation_id` field.
- `httpx2==2.7.0` was installed and recorded as the test-client dependency.
- Ruff formatted the extracted code; one reader file required formatting.

### Final validation

Commands and results:

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

These results apply to the extracted repository files, not every isolated snippet
elsewhere in the educational narrative.

### Upload-boundary validation

After owner approval, the path-based contract was replaced with a bounded
multipart upload and the full validation suite was rerun:

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

The test count changed because obsolete filesystem-path and missing-file cases
were replaced with upload-size and media-type-boundary cases.

## Source verification

The following material claims were checked against current primary sources on
2026-07-21:

1. Python 3.13.12 was released on 2026-02-03 and has been superseded by Python
   3.13.14. Its official release page still provides Windows, macOS, and source
   artifacts: <https://www.python.org/downloads/release/python-31312/>.
2. Pydantic models are classes inheriting from `BaseModel`, with fields declared
   as annotated attributes. Current documentation confirms `model_dump()`,
   `model_dump_json()`, configuration, extra-field behavior, and validation
   methods: <https://pydantic.dev/docs/validation/latest/concepts/models/>.
3. Pydantic strict mode reduces coercion but can differ by input mode and type; it
   is not accurately summarized as universally allowing only identical runtime
   types: <https://pydantic.dev/docs/validation/latest/concepts/strict_mode/>.
4. FastAPI executes normal synchronous route functions and synchronous
   dependencies in an external thread pool. This supports the draft's synchronous
   route choice for blocking filesystem access:
   <https://fastapi.tiangolo.com/async/>.
5. Current FastAPI documentation still says to install `httpx` for `TestClient`,
   while the resolved Starlette 1.3.1 runtime deprecates it in favor of `httpx2`.
   The executable environment takes precedence for this pinned dependency set:
   <https://fastapi.tiangolo.com/tutorial/testing/> and
   <https://starlette.dev/testclient/>.
6. pytest documents `tmp_path` as a unique `pathlib.Path` per test. Captured log
   records and formatted log text are separate interfaces:
   <https://docs.pytest.org/en/stable/how-to/tmp_path.html> and
   <https://docs.pytest.org/en/stable/how-to/logging.html>.

The remaining primary-source links were checked for plausible official domains
and structure but were not exhaustively matched claim by claim. No broken-link
crawler was run.

## Resolved security and API decision

The generated endpoint accepted a caller-controlled filesystem path and opened it
with the server process's permissions. The project owner approved replacing that
unsafe contract with a bounded multipart upload on 2026-07-22.

The verified implementation now:

- accepts `UploadFile` with separately validated multipart metadata;
- reads no more than 1 MiB plus one sentinel byte;
- returns HTTP `413` for an oversized upload;
- compares declared and upload media types;
- accepts `.txt` with `text/plain` only;
- decodes UTF-8 strictly through an injected decoder; and
- never accepts or opens a caller-controlled server path.

This change introduced `python-multipart==0.0.32`. The route is asynchronous
because `UploadFile.read()` is awaitable; async deployment and concurrency tuning
remain outside Week 1 scope.

## Residual content observations

- At approximately 126 KB and 3,937 lines, the draft is comprehensive but may be
  too dense for a single web page. Website rendering should support a sticky table
  of contents, section anchors, and progressive disclosure.
- Returning the full extracted document text is appropriate for this exercise but
  needs response-size limits before production use.
- The 1 MiB input limit is mandatory; making it configurable remains an exercise.
- `line_count` semantics for a trailing newline remain a documented open question.
- The draft correctly preserves Python 3.13.12 as the owner-selected target even
  though a later patch release exists.

## Approval gate

The technical and content approval gates are complete. The canonical Markdown
incorporates verified code and review results, and the project owner completed
HITL approval. Website rendering remains an independent implementation gate.

## Final HITL decision

The project owner approved the assembled Week 1 review candidate on 2026-08-01.
The verified content was promoted to canonical version `1.0.0`. Website rendering
remains a separate architecture decision and is not implied by content approval.
