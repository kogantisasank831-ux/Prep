# LangSmith curriculum addition — 14 November 2026

## Scope and accepted behavior

Owner request: add LangSmith to the existing Prep roadmap. Source base:
`914e227efecb801697278ebb7317376f7cfd8945` on `main`. Keep exactly 30 weeks,
existing public routes, both lesson depths, and the two 100-question assessment
contracts. No change to the local tracing recorder, agent evaluator, dependency
files, provider integrations or hosted site configuration. An observed CI setup
failure also requires pinning the two verification jobs to Ubuntu 24.04, retaining
the accepted Python 3.13.12 runtime and every existing gate.

| Document / task | Audience and purpose | Source / version | Evidence / next review |
| --- | --- | --- | --- |
| `Path.md`, README | Discover where LangSmith fits | Existing Weeks 10 and 18 | Same 30-week scope; review when week titles or routes change |
| Week 10, both depths | Learn projects, parent/child runs, custom instrumentation, metadata and delivery boundaries | Lesson 1.2.0; SDK 0.14.17 | Real SDK default-path smoke, regression test and strict snippet typing; review on SDK/config changes |
| Week 18, both depths | Compare datasets, independent targets/references, code evaluators and experiments | Lesson 1.2.0; three synthetic routes | Account-free script smoke, wrong-output grader checks and strict snippet typing; review on evaluator/schema changes |
| Assessment pages and JSON | Check understanding of the new material | Banks 1.2.0 | Four revised questions per bank; IDs, types, difficulty quotas and coding tasks preserved |
| Lab READMEs | Discover the optional walkthroughs from the existing labs | Existing deterministic lab contracts | Describe separate examples rather than claiming native lab export |

## Accuracy and executed local evidence

Environment: Python 3.13.12, Node 24.22.1, declared development/Week 12/Week 15
dependencies, optional `langsmith==0.14.17`. Primary LangChain documentation for
custom instrumentation, runtime enablement, payload controls, SDK evaluation,
dataset versions, experiment comparisons and `Client.flush` was checked on the
review date. New examples contain invented data and no credentials/model calls.

- Ran both copyable scripts: the trace example returns the invented payment term
  with `upload_requested: false`; the evaluation example reports baseline 1/3
  and candidate 3/3.
- The tracing regression enables ambient tracing while blocking client
  construction/network connection and verifies that the explicit default still
  makes no upload. Opt-in without a key fails before client construction.
- The evaluation regression executes the actual snippet with Python `-S`, so its
  default route needs no installed SDK. The grader rejects wrong and extra fields.
- Strict mypy passes for both examples and the affected assessment tests.
- The real SDK's `evaluate(..., upload_results=False)` also scored in-memory
  schema examples as `[true, false, false]` and `[true, true, true]` with outbound
  requests blocked. The SDK attempted an informational `/info` read, logged its
  blocked failure and completed locally. This is why the lesson's default
  evaluation route uses only the standard library rather than claiming every
  SDK local-evaluation mode is network-free.
- Ran every runnable command in the existing `pytest` workflow job with the
  declared Python environment: Ruff and formatting checks (139 files), strict
  mypy (139 files), 10 JavaScript tests, 2,494 pytest tests, and all configured
  Week 13–30 CLI smokes passed. The full regression run includes the two new
  snippet checks and the revised banks' balanced-paper verification.
- Validated all six affected lesson/assessment front matters, version/review
  metadata, both new cross-page anchors, 30 roadmap weeks and `git diff --check`.

## Evidence boundaries and handoff

Hosted LangSmith tracing, dataset writes, experiment delivery, account-specific
permissions and cleanup were not executed: no account credentials were used.
The lesson identifies the upload side effects, key/workspace/endpoint setup,
dataset-write permissions, payload limits and explicit opt-in. Local output and
SDK flush completion are not presented as evidence of hosted delivery.

The three-case routing example teaches SDK concepts, not the quality of a real
agent or the outcome of the unchanged 28-case lab. Core labs and browser
assessments remain account-free. No independent beginner cold-reader review was
performed; beginner steps were checked for stated prerequisites and outcomes.

Local Jekyll rendering was unavailable because Ruby/Jekyll are not installed in
this environment. Front matter/anchors were checked structurally; this is not a
rendered-site or browser verification. The real Week 12 container integration
remains a candidate-matched CI gate. Candidate CI, approval to merge, exact
merged-commit Pages build and deployed route checks are separate release stages
and are not established by this local record.

## CI runner repair

The first PR candidate `a1d84ace9e3c69d87ca2019117aa9c680835d325` failed before
tests in [run 43593409792](https://github.com/kogantisasank831-ux/Prep/actions/runs/43593409792).
`ubuntu-latest` selected Ubuntu 26.04, and `actions/setup-python` could not find
Python 3.13.12 for that platform. The official
[Python versions manifest](https://github.com/actions/python-versions/blob/main/versions-manifest.json)
lists a Linux x64 build for 24.04 and none for 26.04. Pin `pytest` and
`week12-stack` to `ubuntu-24.04`; keep action pins, runtime, triggers, permissions,
dependency installation, required tests, service setup and cleanup unchanged.

The observed failure proves the prior setup blocks the gate. YAML validation
and the official platform manifest justify the repair; only a new exact-candidate
workflow run can verify the configured runner actually executes both jobs.
Owner: repository maintainer. Review the runner pin when changing the Python
patch release or supported runner image; do not restore an unverified floating
image merely to remove the pin. This repair does not change deployment authority
or turn a missing/skipped gate into a successful result.
