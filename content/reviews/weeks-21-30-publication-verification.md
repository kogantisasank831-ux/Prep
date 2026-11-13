# Weeks 21–30 publication verification

## Release identity

- User publication approval: 2026-11-12.
- Pull request: `#19`.
- Candidate commit: `3b50ede3b75de3ab09ed6fa27bb77113fc35365d`.
- Published `main` commit: `f37a78df3fbf10bbbd4c614c7ee21e029ebcba4f`.
- Published tree: `afd2e256c65c2d0691c7e553268a13ffe16ee0de`.

## Candidate and post-merge gates

| Gate | Identity | Result |
| --- | --- | --- |
| Pull-request CI | Workflow run `43217012234` on candidate `3b50ede3b75de3ab09ed6fa27bb77113fc35365d` | Passed |
| Main CI | Workflow run `43217456656` on `f37a78df3fbf10bbbd4c614c7ee21e029ebcba4f` | Passed, including pytest and the real Week 12 PostgreSQL/pgvector job |
| GitHub Pages | Workflow run `43217453922` on `f37a78df3fbf10bbbd4c614c7ee21e029ebcba4f` | Passed |

## Post-publication verification

Checked on 2026-11-13 against the deployed GitHub Pages site:

- Ruff lint, Ruff formatting, and strict MyPy passed across the configured 139 Python files.
- The shared navigation JavaScript suite passed all 3 then-current tests.
- The complete local pytest suite passed all 2,487 tests.
- The live route matrix passed 120/120 routes: 30 production lessons, 30 beginner lessons, 30 assessments, and 30 JSON banks.
- All 30 banks contained 100 questions, for 3,000 total questions, with the required 30 single-choice, 20 multiple-select, 15 matching, 15 short-answer, and 20 code distribution.
- Browser inspection found 30 roadmap cards, 30 lesson links, and 30 assessment links.
- Interview Prep was selected without Roadmap also appearing selected; Week 30 was selected without another week appearing selected.
- The Week 30 assessment exposed a 100-question bank, a 10-question paper, and two coding questions.
- No page-origin browser warnings or errors were observed during the checked journeys.

## Evidence boundary

These build, regression, route, data-contract, and browser-smoke results verify the named source and deployed site behavior within the exercised scope. They do not replace human editorial review, learner-outcome evaluation, assistive-technology testing, or proof that every external technical claim remains current.
