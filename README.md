# Applied GenAI Roadmap

A static learning roadmap for the 30-week curriculum in [`Path.md`](Path.md).
The dashboard is dependency-free; GitHub Pages uses its native Jekyll build to
render approved weekly Markdown lessons. The site provides responsive sidebar
navigation, phase filtering, full-text search, light/dark and focused reading
modes, weekly completion tracking, and private browser-local notes.

## Run locally

The site loads `Path.md` with `fetch`, so it must be served over HTTP rather than
opened directly from the filesystem.

```powershell
python -m http.server 8000
```

Open <http://localhost:8000>.

## Publish with GitHub Pages

1. Push the repository to GitHub.
2. In **Settings → Pages**, select **Deploy from a branch**.
3. Select the repository's default branch and the `/ (root)` folder.
4. Save and open the published URL after the deployment completes.

GitHub Pages runs the Jekyll build automatically. Progress and notes are stored in
`localStorage`, so they remain specific to the current browser and device.

## Content workflow

`Path.md` is the source of truth. Keep phase headings in the form
`# Phase N: Title`, week headings as `## Week N — Title`, and subsection headings
as `### Title`. Changes that follow this structure appear automatically on the
website after refresh.

Approved detailed lessons live in `content/weeks/` with `layout: week` and a
stable permalink. Add the week number to `PUBLISHED_WEEKS` in `shell.js` only after
technical and human review pass.

The Python HTTP server can preview the dashboard shell, but it does not execute
Jekyll and therefore cannot render weekly Markdown pages. Use GitHub Pages or a
local Ruby/Jekyll installation for a complete preview.

## Run the Week 1 Python service

The [main lesson](https://kogantisasank831-ux.github.io/Prep/weeks/week-01/)
and [beginner lesson](https://kogantisasank831-ux.github.io/Prep/weeks/week-01/beginner/)
teach the existing `document_service/` application. Its lesson reference is
Python 3.13.12. Run these commands from the repository root in a virtual
environment; keep the versions pinned in the existing requirement files.

Create the environment:

```shell
python -m venv .venv
```

Activate it with `.venv\Scripts\Activate.ps1` in PowerShell, or
`source .venv/bin/activate` in Bash. If activation is blocked, use the environment's
Python executable directly (`.venv\Scripts\python.exe` or `.venv/bin/python`)
in place of `python` below.

```shell
python -m pip install -r requirements-dev.txt
python -m pytest tests/test_models.py tests/test_readers.py tests/test_service.py tests/test_api.py
python -m uvicorn document_service.main:app --host 127.0.0.1 --port 8001
```

The test command covers the Week 1 service rather than the later labs. The
Uvicorn command starts the local API on port 8001; the static dashboard command
above uses port 8000. Open <http://127.0.0.1:8001/docs> to try the endpoint.

In another terminal with the same environment, create a byte-exact synthetic
sample. Exclusive creation preserves an existing file with the same name:

```shell
python -c "from pathlib import Path; Path('week01-sample.txt').open('xb').write(b'alpha\r\nbeta')"
```

Send both scalar form fields and the uploaded file. Use `curl.exe` instead of
`curl` in PowerShell to avoid its command alias:

```shell
curl --fail-with-body --request POST http://127.0.0.1:8001/v1/documents/extract --form media_type=text/plain --form correlation_id=request-42 --form "file=@week01-sample.txt;type=text/plain"
```

The successful response is:

```json
{
  "correlation_id": "request-42",
  "media_type": "text/plain",
  "text": "alpha\nbeta",
  "character_count": 10,
  "line_count": 2
}
```

Try a renamed `.pdf` (415), whitespace-only `.txt` (422), invalid UTF-8 (422),
and input larger than 1,048,576 bytes (413). The document-error body has `code`,
`message` and `correlation_id`. Missing/invalid scalar form fields instead use
FastAPI's 422 `detail` response. The sentinel read bounds the endpoint's read;
it does not establish a complete HTTP-body or upload-storage limit.

The existing service stays UTF-8 `.txt` only. Markdown support, configurable
limits and review-item classification in the lesson are exercises. Keep sample
uploads local and use synthetic text; the API has no authentication or persistence.

## Weekly assessments

[Week 1 assessment](https://kogantisasank831-ux.github.io/Prep/assessments/week-01/)
has 100 authored questions: 30 single-choice, 20 multiple-correct, 15 matching,
15 short syntax and 20 Python coding tasks. Each random paper takes two of each
format without duplicates. A shareable seed and bank version reproduce both
question selection and option order. Print produces a blank question paper.

Every question is worth 10 marks. Single-choice and short answers use exact
declared keys; surrounding spaces are ignored for short answers and their case
policy is shown. Multiple-correct requires the complete set. Matching gives
2.5 per correct pair with one use per option. Coding gives 2 per passed check.
There are no negative marks. Explanations and references appear after submission.

[Week 2 assessment](https://kogantisasank831-ux.github.io/Prep/assessments/week-02/)
has the same 30/20/15/15/20 distribution and paper/scoring policy, with twenty
written PostgreSQL query tasks. Topics follow Week 2's procurement model,
including joins, cutoff dates, CTEs, windows, comparable prices, indexes,
normalization, transactions and locking.

[Week 3 assessment](https://kogantisasank831-ux.github.io/Prep/assessments/week-03/)
has the same 100-question distribution and balanced paper policy. Its twenty
standard-library Python tasks cover context budgets, stable softmax, sampling,
causal visibility, embedding lookup, attention/residual arithmetic, strict JSON,
prompt hashes, baseline settings, loopback origins, response/metric validation,
frozen schedules and evidence idempotency. Synthetic inputs run through the
existing Python worker; no LLM, weights, server, GPU or inference API is needed.
The full local-model experiment and its Windows storage/lifecycle integration
remain separate from these portable coding checks.

The site stays static. A Python coding run downloads pinned Pyodide 0.29.3 from its
documented jsDelivr distribution into a separate browser worker. This version
uses Python 3.13, matching the lesson's language family. The app terminates each
worker after its run, after Stop, or after the 5-second execution deadline.
Runtime loading has a separate 45-second deadline. The checks use only the
standard library, without running FastAPI/Pydantic or sending learner code to
a remote execution API. Loading the CDN still makes normal network requests.

Week 2 downloads pinned @electric-sql/pglite 0.5.11 from jsDelivr to run
PostgreSQL in a disposable worker. Its Apache-2.0 package requires no server,
paid account, API key or build step. Each of five datasets starts with fresh
synthetic tables. A single query runs in a read-only transaction and is checked
against independently calculated expected rows, including column names, order,
duplicates, NULLs and exact decimal values. The same loading/execution deadlines
apply. PGlite has one connection; the full lab remains the place for two-session
locking experiments. Query execution stays on the device.

Google Colab is an optional external Python workspace requiring Google sign-in:
learners copy their code there and paste it back for local checks. Results are
not imported from that tool. For SQL, the optional workspace is
[db<>fiddle with PostgreSQL 18](https://dbfiddle.uk/?rdbms=postgres_18).
Learners can copy the schema/example data and their query; opening the link does
not transfer an answer. External SQL results likewise do not sync.
When the runtime is unavailable, submitted coding marks stay pending and can be
retried; the displayed score clearly separates graded and pending marks.

Attempts are stored in the current browser, separately by week, bank version and
paper seed. They can be resumed by link and downloaded as JSON. This is a public
practice bank with client-side scoring; neither answer secrecy nor authenticated
exam results are provided. No central learner database or score upload is added.

Weeks 1, 2 and 3 use the shared engine. Future weeks need their own
reviewed 100-question JSON bank and assessment page before being added to
`ASSESSMENT_WEEKS` in `shell.js`. A bank revision needs a new version; an old
version's paper link is rejected instead of silently changing its questions.
The page chooses the Python or SQL worker from bank metadata; other languages
need an explicit execution integration.

Run `python -m pytest tests/test_week01_assessment.py` to validate bank structure,
reference solutions, negative submissions and grading/selection behavior. The
JavaScript checks in that suite use the existing Node executable (Node 20+).

Run `python -m pytest tests/test_week02_assessment.py` for Week 2 bank/engine
contracts. To check actual PostgreSQL results, install the pinned runtime outside
tracked source (for example, `npm install --prefix .qa-week02-assessment/tools @electric-sql/pglite@0.5.11`) and run
`node scripts/verify_sql_assessment.mjs .qa-week02-assessment/tools/node_modules/@electric-sql/pglite/dist/index.js`.

Run `python -m pytest tests/test_week03_assessment.py` for the Week 3 bank,
all twenty references and plausible incorrect implementations, numerical
properties, and shared paper/scoring/restoration contracts.
