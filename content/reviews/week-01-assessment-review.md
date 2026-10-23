---
week: 1
status: approved
version: 1.0.0
last_reviewed: 2026-10-23
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested the Week 1 assessment within the established explicitly approved build-check-push-publish workflow
---

# Week 1 assessment review

## Scope and requirements

Baseline: `kogantisasank831-ux/Prep` main commit
`5d69818a22992cff0a5a167867eb193d0793eb65`, tree
`b6a64ba9fbc440aea8995c0393efcfbe31902c57`. Work used
`week01-assessment` from a fresh `origin/main` fetch. Root `AGENTS.md` is the
sole applicable instruction file; no `Design/` directory exists here. Existing
untracked QA work and all earlier implementation were preserved.

The user requested a 100-question weekly bank, random ten-question papers,
several objectively scored formats, written coding solutions that test syntax
and behavior, legitimate external coding workspaces, and compatibility with
GitHub Pages. This pass enables Week 1 only. The sampling/scoring engine can
serve later reviewed banks; its coding checker currently supports Python.

Inspected the root instructions, roadmap/content workflow, complete Week 1
lessons and service contracts, existing tests/requirements, layout, navigation,
dashboard scripts and theme styles. Learning scope comes from `Path.md` and the
published Week 1 lesson. All 100 items and twenty reference solutions are
authored for this bank; no independent human item-validation or psychometric
calibration is claimed.

| Requirement | Implemented contract |
| --- | --- |
| 100 questions | Exactly 30 single-choice, 20 multiple-correct, 15 matching, 15 short syntax and 20 coding items with unique IDs/prompts |
| Random paper | Two of each format, sampled without replacement and shuffled; ten unique questions |
| Reproducible paper | Random 128-bit seed plus bank version reproduces question/option order; share links carry no answers |
| Score | Ten marks each; exact single/short keys; full-set multiple-correct; matching 2.5 per pair with one use per option; coding 2 per passed check |
| Syntax and concepts | Code output, annotations, identifiers, class/decorator syntax, failures, generators, async, validation, logging and tests; twenty written Python exercises |
| Written solutions | A real Python interpreter executes five public behavioral checks per exercise, including boundary/failure cases |
| Paper and review | Blank printable questions, saved attempts, locked submitted answers, explanations/references and downloadable JSON results |
| Third-party workspace | Optional Google Colab link; sign-in stated; code/results are not automatically transferred |
| Pages | Static HTML/CSS/JS/JSON; Python runs on the learner's device, without a backend execution API |

Multiple-correct keys vary between two, three and four correct choices. Option
order is shuffled independently of the authored answer IDs. Short-answer case
policy is explicit; only surrounding whitespace is normalized. Matching and
coding partial credit are distinguished from exact multiple-correct grading.
There are no negative marks or unmeasured subjective/LLM scores.

## Architecture and boundaries

`assessment-core.mjs` owns bank validation, deterministic selection, answer
normalization, score computation and restored-attempt checks. `assessment.mjs`
owns accessible form controls, lifecycle, local persistence, printing and
downloads. The assessment page reuses the existing Jekyll shell, with scoped
styles and links from the dashboard and both Week 1 lessons. Only Week 1 enters
`ASSESSMENT_WEEKS`; existing published-week navigation remains unchanged.

Coding lazily loads pinned Pyodide 0.29.3 into a fresh module worker per run.
`assessment_runner.py` is fetched as static text and executed inside that
interpreter; GitHub Pages never executes the Python file. Checks use the
standard library. The worker is terminated after completion, Stop, loading
failure or its deadline. Runtime loading has a separate 45-second budget;
execution has a five-second deadline that repeated ready messages cannot extend.
No SharedArrayBuffer, cross-origin-isolation header, API key, server process or
application npm dependency is required.

Source is limited to 20,000 characters and captured output to 4,000. Each run
registers a temporary module for dataclass/type-hint correctness and restores
that registration afterward. Individual check failures retain partial credit.
Syntax/top-level failures produce five failed checks. A genuine execution
timeout produces zero; unavailable infrastructure or a stopped run leaves coding
marks pending. A submitted pending solution stays locked but its checks can be
retried. Editing a draft invalidates its old coding result.

Attempt keys include week, bank version and full seed. The page validates
restored answer shapes and exact-source coding results, handles unavailable
storage, and rejects an old-version paper link instead of silently replacing
its questions. Results identify the bank, paper, answers and check outcomes.
User strings and source are rendered as text, not injected HTML.

The bank and keys are public. Local storage and downloadable results can be
edited by their owner; these are practice/supervised-review scores, not
authenticated exam records. A worker supplies lifecycle separation, not a
general security sandbox or hard memory quota. No learner account/database,
score upload, secret test bank, proctoring or remote execution service is added.
Google Colab is opened only by the learner's chosen external link.

## Verification executed

Native environment: Linux, Python 3.12.14, existing pytest 9.1.1/Ruff 0.15.22/
mypy 2.3.0, Node 24.19.0. Browser: headless Chromium 153.0.8010.0. Actual
Pyodide runtime reported CPython 3.13.2. Requirement files and the existing
Python document service are unchanged.

| Check | Observed result |
| --- | --- |
| New assessment pytest module | 67 passed |
| Assessment plus four existing Week 1 modules | 93 passed, no warnings |
| Reference and negative solutions | All twenty references pass five checks; all twenty starters and twenty plausible faulty solutions lose marks |
| Engine selection/keys | 1,000 balanced papers, no duplicates, all 100 items reached, deterministic reproduction, all eighty objective keys validated |
| Engine score/restore | Exact and partial credit, pending denominators, stale-source rejection, malformed banks and version mismatch checked |
| Ruff lint/format, strict mypy | Passed over service, Week 1 tests, assessment runner/tests and existing lesson verifier; seventeen Python files |
| JavaScript syntax | Assessment modules plus changed dashboard/navigation scripts parse successfully |
| Lesson preservation | All existing 32 main and 11 beginner fences and front matter byte-identical; existing content verifier passes both |
| Real browser paper | Ten rendered questions; complete answer set scores 100/100; reload restores it; downloaded result agrees |
| Real browser coding | All twenty references/five checks each passed through fresh Pyodide workers |
| Infrastructure failure | Blocking the runtime gives 80/80 graded with twenty pending, then retries recover 90/90 and finally 100/100 without changing locked answers |
| Worker lifetime | Stop preserves source; an infinite loop hits the five-second limit; a subsequent corrected solution passes |
| Mobile/print/navigation | 390-pixel light/dark layouts have no horizontal overflow; print exposes ten blank questions without references; share/new-paper/dashboard and active-week navigation work |
| Browser requirements | Verified with normal web security, crossOriginIsolated false and SharedArrayBuffer unavailable; no application page errors |

Browser QA used a temporary HTTPS asset relay to the same official CDN URLs
because direct Chromium CDN traffic in this execution environment returned
`net::ERR_EMPTY_RESPONSE`. Node fetched the real pinned assets over HTTPS and
preserved their content types/CORS headers for the browser. The application
worker/CDN URL was unchanged, and no TLS or browser web-security bypass was used
for the completed tests. Temporary browser tooling/assets stay outside the
publication set. Desktop/mobile screenshots were visually inspected.

Final diff/whitespace and exact commit/blob/tree checks precede the push. Hosted
Jekyll/Pages completion, public assessment/bank/module MIME types and a published
paper are checked after pushing and reported in the handoff. The unrestricted
later-week application suite was not rerun for this frontend/assessment change.

## Primary evidence and remaining limits

Opened official GitHub Pages hosting documentation, the versioned Pyodide worker
guide and Google Colab's FAQ/homepage. The application does not use Colab as a
backend or promise imported marks. Current CDN reachability and learner device
capacity remain runtime dependencies; failure preserves the submitted solution
and provisional score. No production-capacity or assessment-validity benchmark
is claimed.

- https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages
- https://pyodide.org/en/0.29.3/usage/webworker.html
- https://research.google.com/colaboratory/faq.html
- https://colab.research.google.com/

Repeat the maintained checks with
`python -m pytest tests/test_week01_assessment.py` (Node 20+ for JS checks),
`node scripts/verify_assessment.mjs`, the documented Week 1 test command and the
existing lesson verifier. Later weeks require their own reviewed banks/pages;
another coding language requires a matching execution integration.
