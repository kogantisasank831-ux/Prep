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

[Week 4 assessment](https://kogantisasank831-ux.github.io/Prep/assessments/week-04/)
has 100 questions with the same distribution and balanced paper policy. Twenty
standard-library Python tasks cover decimal/date/text contracts, required and
extra keys, duplicate JSON names, UTF-8 limits, labelled evidence, exact field
comparison, status precedence, document serialization, versioned request
digests, bounded recovery and separate structural/support rates. They run in
the existing Python worker on synthetic inputs. The full Pydantic extraction
lab and any real-model evaluation remain separate; no new runtime dependency
or inference service is added.

[Week 5 assessment](https://kogantisasank831-ux.github.io/Prep/assessments/week-05/)
has 100 questions with the same distribution and balanced paper policy. Twenty
standard-library Python tasks cover finite vectors, stable normalization,
cosine and Euclidean math, packed storage, deterministic ties, full object
grants, authorization before scoring, initial chunks, embedding/corpus
fingerprints, batch validation, Precision/Recall/reciprocal-rank/nDCG,
explicit MRR populations, ANN neighbor overlap and exact synthetic retrieval.
They run in the existing Python worker without model weights or an inference
API. The full retrieval lab and governed model/ANN evaluation remain separate.

[Week 6 assessment](https://kogantisasank831-ux.github.io/Prep/assessments/week-06/)
has the same 100-question distribution and balanced paper policy. Twenty
standard-library Python tasks cover canonical text, parser review routing,
fixed/overlap spans, exact block-relative locations, sentence/structure/shared-term
boundaries, policy/representation checksums, child-only indexing, parent lineage
and reauthorization, whole-unit context budgets, stored bytes, document recall
at a chunk cutoff, per-source support completeness and honest measurement
summaries. They run on synthetic inputs in the existing Python worker; no PDF
parser, OCR engine, model weights or inference service is added.

[Week 7 assessment](https://kogantisasank831-ux.github.io/Prep/assessments/week-07/)
has the same 100-question distribution and balanced paper policy. Twenty
standard-library Python tasks cover identifier-preserving tokens, TF/DF and
BM25 math, authorized partitions, exact metadata filters, score floors,
stable min-max scaling, weighted RRF with contributor validation/provenance,
candidate depth, manifest/corpus fingerprints and source-faithful evidence
labels. All tasks use synthetic inputs in the existing Python worker; the full
retrieval lab and any real-model evaluation remain separate.

[Week 8 assessment](https://kogantisasank831-ux.github.io/Prep/assessments/week-08/)
adds 100 questions with the same distribution and balanced paper policy. Twenty
standard-library Python tasks cover finite pair scores, stable same-pool ranking,
original-question pairs, guarded query variants, independent budgets, exact
source-scoped duplicates, sentence coordinates/selection, serialized context,
whole-unit packing, authorized citations, source-bound support, availability
statuses, idempotent records, unambiguous bounded JSON, joint token-ID checks,
safe events, request identity and paired metrics. Inputs are synthetic; no model
weights, inference server or generator is loaded by these browser tasks.

[Week 9 assessment](https://kogantisasank831-ux.github.io/Prep/assessments/week-09/)
adds 100 questions with the same mixed formats and balanced paper policy. Twenty
Python tasks cover normalization/reference alternatives, lexical coverage,
precision/recall/first hit, graded DCG/nDCG, null-aware means, scoped abstention,
citation populations, context-source metrics, independent source audits,
stage failure labels, pending/validated reviews, separate reviewer groups,
paired regressions, grouped split planning and observation/run fingerprints.
Tasks use synthetic standard-library inputs; no evaluator model, LLM judge or
paid service is loaded. The 30-case assistant evaluation remains separate.

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

Weeks 1, 2, 3, 4, 5, 6, 7, 8 and 9 use the shared engine. Future weeks need their own
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

Run `python -m pytest tests/test_week04_assessment.py tests/test_week04_extractor.py`
for the Week 4 bank, all twenty coding references/starters/incorrect solutions,
composed business checks, shared scoring contracts and the existing offline lab.

Run `python -m pytest tests/test_week05_assessment.py tests/test_week05_retrieval.py`
for the Week 5 bank, twenty coding references/starters/incorrect solutions,
composed vector/access/metric checks, shared scoring contracts and the existing
offline retrieval lab.

Run `python -m pytest tests/test_week06_assessment.py tests/test_week06_chunking.py`
for the Week 6 bank, twenty coding references/starters/incorrect solutions,
composed evidence-preservation/access/metric checks, shared scoring contracts
and the existing offline chunking lab.

Run `python -m pytest tests/test_week07_assessment.py tests/test_week07_hybrid.py`
for the Week 7 bank, twenty coding references/starters/incorrect solutions,
composed authorization/statistics/fusion/evidence checks and the existing lab.

Run `python -m pytest tests/test_week08_assessment.py tests/test_week08_assistant.py`
for the Week 8 bank, twenty coding references/starters/incorrect solutions,
composed evidence-preservation/citation/budget checks and the existing assistant.

Run `python -m pytest tests/test_week09_assessment.py tests/test_week09_evaluation.py`
for the Week 9 bank, twenty coding references/starters/incorrect solutions,
composed metric/source/review regressions and the existing 30-case evaluation.

The `Weekly learning checks` workflow runs on assessment/content-branch and main
pushes and pull requests. It installs the declared Python 3.13.12 environment,
requires Node 20+, checks the Week 7–12 assessment tests and Week 10–13 labs'
Ruff/typing gates, and runs every published assessment suite, Week 7 hybrid/
Week 8 assistant/Week 9 evaluation/Week 10 tracing/Week 11 security/Week 12
application/Week 13 tool-calling tests and Week 1 service regressions. A second
required job builds
the real Week 12 Compose stack, runs PostgreSQL/pgvector permission/revocation
integration and real HTTP smoke before and after its volume-preserving restart.
The candidate commit must pass before its branch is promoted to
main; GitHub Pages build and relevant live browser checks follow promotion. The
selected suite avoids the unrelated Windows-only comparison module and does
not claim an unrestricted whole-repository test pass.

## Week 10 content and tracing lab

[Week 10 lesson](https://kogantisasank831-ux.github.io/Prep/weeks/week-10/)
and its [beginner version](https://kogantisasank831-ux.github.io/Prep/weeks/week-10/beginner/)
follow one request through query planning, authorized hybrid search, reranking,
context and citations. The [local lab](labs/week_10/README.md) adds request/span
identities, monotonic stage timing, version fingerprints, bounded failure records,
explicit synthetic payload capture and labelled token/cost examples.

```shell
python -m labs.week_10.demo --scenario payment --output-dir .runtime/week10-payment
python -m labs.week_10.demo --scenario model-fixture --output-dir .runtime/week10-model --capture-synthetic-content
python -m pytest tests/test_week10_tracing.py -q
```

Choose fresh output directories. The optional model is a scripted fixture with
synthetic usage and invented rates; it makes no provider call and does not
replace the extractive answer. JSON is a custom local trace format, not OTLP.
The [Week 10 assessment](https://kogantisasank831-ux.github.io/Prep/assessments/week-10/)
adds 100 questions: 30 single-choice, 20 multiple-correct, 15 matching, 15 short
syntax and 20 Python tasks. A random paper draws two of each format for 100 marks.
Run `python -m pytest tests/test_week10_assessment.py tests/test_week10_tracing.py`
for the bank/reference checks, composed observation contracts and local tracing lab.

## Week 11 content and security lab

[Week 11 lesson](https://kogantisasank831-ux.github.io/Prep/weeks/week-11/)
and its [beginner version](https://kogantisasank831-ux.github.io/Prep/weeks/week-11/beginner/)
cover direct/indirect prompt injection, malicious sources, leakage, poisoning,
trusted tenant/principal scope, access-controlled retrieval and input/output
validation. The [local security lab](labs/week_11/README.md) reuses the Week 8
retrieval pipeline with a protected synthetic catalogue and quote-only output.

```shell
python -m labs.week_11.demo --scenario clean --output-dir .runtime/week11-clean --show-answer
python -m labs.week_11.demo --scenario detector-miss --output-dir .runtime/week11-miss --show-answer
python -m labs.week_11.demo --scenario poisoned-fact --output-dir .runtime/week11-poisoned --show-answer
python -m pytest tests/test_week11_security.py -q
```

Choose fresh directories. Thirteen synthetic cases include source isolation,
tampering, unsafe proposals, revocation, a detector miss/false positive and an
approved false statement. These demonstrate local controls and their limits;
the responder is scripted, with no provider call or action dispatcher. The
existing CI gate includes the security lab's tests, lint and typing. The
[Week 11 assessment](https://kogantisasank831-ux.github.io/Prep/assessments/week-11/)
adds 100 questions: 30 single-choice, 20 multiple-correct, 15 matching, 15 short
syntax and 20 Python tasks. A random paper draws two of each format for 100 marks.
The coding exercises use standard-library functions with five checks each;
public practice scores do not establish source truth or complete attack detection.
Run `python -m pytest tests/test_week11_assessment.py tests/test_week11_security.py`
for bank/reference checks, composed security contracts and the local security lab.

## Week 12 content and local deployment lab

[Week 12 lesson](https://kogantisasank831-ux.github.io/Prep/weeks/week-12/)
and its [beginner version](https://kogantisasank831-ux.github.io/Prep/weeks/week-12/beginner/)
turn the guarded assistant into a local FastAPI service backed by PostgreSQL
and pgvector. The [lab](labs/week_12/README.md) includes strict authenticated
requests, current source/pin checks before vector selection, validated-result
SSE, bounded process-local caching/rate/admission, secret files, health checks,
versioned insert-only bootstrap and a non-root Compose setup.

```shell
python -m pip install -r requirements-dev.txt -r labs/week_12/requirements.txt
python -m labs.week_12.cli secrets
docker compose -f labs/week_12/compose.yml build api
docker compose -f labs/week_12/compose.yml up -d --no-build api
python -m labs.week_12.cli smoke
python -m pytest tests/test_week12_service.py -q
```

Run from the repository root in an activated environment; generate credentials
once for a fresh setup. Keep the files and named volume together. The API binds
to 127.0.0.1:8000 and provides /docs and /openapi.json. The ordinary Compose file
keeps PostgreSQL private; the CI override provides an isolated loopback test port.
The responder is scripted and the 32-dimensional token-hash encoder is a
synthetic baseline. No provider/GPU/paid service or public backend is introduced.
GitHub Pages publishes the static lessons, while these services run locally.
The [Week 12 assessment](https://kogantisasank831-ux.github.io/Prep/assessments/week-12/)
adds 100 reviewed questions and balanced random 10-question papers. Its 20
standard-library Python exercises cover settings, raw bytes, vectors, scoped
identity, cache TTL/LRU, fixed windows, public projections, SSE, async callback
failures, fresh rechecks, completion ownership and insert-only seed conflicts.
The browser checker supports top-level await in checks. No database, backend
server, container or provider is started by these small practice exercises.

Run the bank and local service regression checks from the repository root:

    python -m pytest tests/test_week12_assessment.py tests/test_week12_service.py -q

These cover the shared scorer, reference/starter/wrong-solution checks and local
service behavior. Required CI additionally runs the real database/container
checks described above before promotion.

## Week 13 content and tool-calling lab

[Week 13 lesson](https://kogantisasank831-ux.github.io/Prep/weeks/week-13/)
and its [beginner version](https://kogantisasank831-ux.github.io/Prep/weeks/week-13/beginner/)
follow a proposed operation through closed schemas, trusted caller scope,
validated results, a bounded serial loop, retries and cooperative deadlines.
The [lab](labs/week_13/README.md) implements named SQL, price variance, supplier
lookup, dated synthetic commodity lookup and the existing guarded document search.

An optional local review-record tool demonstrates exact approval, stable
application-supplied intent keys, atomic SQLite replay/conflict protection and
recovery after a deliberately lost write response. It has no external action
capability. SQLite is a separate fixture/ledger; the Week 12 PostgreSQL/API
contracts and data remain unchanged.

~~~shell
python -m pip install -r requirements-dev.txt
python -m labs.week_13.demo init
python -m labs.week_13.demo run --scenario read
python -m labs.week_13.demo smoke
python -m pytest tests/test_week13_tools.py -q
~~~

Initialize only a fresh .runtime/week13.sqlite3, then reuse it; init refuses
existing files. The planner and approval are explicit synthetic fixtures,
not a real-model benchmark or authenticated human approval flow. No provider,
paid service, new dependency or public backend is introduced. CI requires the
tool tests and actual CLI smoke alongside the existing database/container gates.
Week 13 assessment questions are a separate next step.
