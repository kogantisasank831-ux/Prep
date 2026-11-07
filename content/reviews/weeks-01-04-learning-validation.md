# Weeks 1–4 audience and learning validation

## Scope and decision

This batch validates both lesson depths and the assessment for:

- Week 1 — Python for production AI systems;
- Week 2 — SQL and data modelling;
- Week 3 — LLM foundations; and
- Week 4 — Prompting and structured output.

The batch is approved as a learning-content revision. It does not add the future
Data Scientist or AI Engineer interview banks and does not add cheat sheets.
Those artifacts have a different purpose from the weekly understanding checks.

## Validation standard

| Area | Beginner version | Production version | Assessment |
| --- | --- | --- | --- |
| Starting point | Treat the weekly topic as new and state the small prerequisite set | Assume basic familiarity or relevant experience | Assume only material taught in the lesson |
| Explanation | Plain language, one running example, concepts before framework detail | Trade-offs, failure modes, tests and operational boundaries | Recognition, prediction and application rather than interview performance |
| Route | Mark a core path and defer stretch detail | Provide a bounded eight-hour path and reviewable evidence | Ten questions: two per format, with a declared difficulty mix |
| Completion evidence | Learner can explain the flow and predict a result | Learner can defend a design and its limits | Explanations plus executable checks for coding tasks |

## Findings and remediation

| Week | Finding | Change |
| --- | --- | --- |
| 1 | The beginner explanation was clear but did not state prerequisites or separate the first-pass core from framework/concurrency detail. The production lesson lacked the shared metadata and an explicit route. | Added a new-to-services starting point, an eight-hour beginner path, a production audience statement, an eight-hour evidence path and consistent review metadata. |
| 2 | The running purchase-order example was strong, but the beginner route presented windows, indexes and concurrency too early as equal-weight goals. | Kept grain, keys, aggregation, joins and dates in the core; moved nested queries, windows, indexes and transactions to a labelled preview on the first pass. Clarified the experienced SQL audience for the production lesson. |
| 3 | The lesson explained the model path accurately, but its conceptual and local-evaluation scopes were broad for a first-time learner. | Added a beginner route that prioritises tokens, generation, attention, context and evidence; marked derivations and the full local comparison as stretch work. Split the production route into conceptual core and operational evidence-hardening stages. |
| 4 | Both depths were already coherent and safety-conscious, but the beginner page did not expose the end-to-end path as clearly as the production lesson. | Added a contract-to-outcome beginner route, labelled exact validation/recovery mechanics as stretch detail and made the production audience assumption explicit. |

## Assessment decision

All four banks retain 100 unique questions and each paper retains ten questions:
two single-choice, two multiple-correct, two matching, two short exact-answer and
two coding questions. The short questions check essential technical vocabulary
or syntax; the coding questions require small applications of lesson contracts.
The other formats test concepts, predicted outcomes, failure recognition and
design reasoning.

Difficulty selection is now an executable bank contract:

| Week | Paper mix | Reason |
| --- | --- | --- |
| 1 | 6 foundation + 4 applied | The existing bank intentionally uses foundation single/matching/short items and applied multiple/coding items. |
| 2 | 5 foundation + 5 applied, one of each per format | Prevents a random paper from over-sampling the bank's applied items. |
| 3 | 5 foundation + 5 applied, one of each per format | Keeps first-principles understanding and small model/evaluation applications together. |
| 4 | 5 foundation + 5 applied, one of each per format | Keeps contract knowledge and extraction/recovery applications together. |

The shared engine rejects missing or unknown difficulty labels, malformed quotas
and quotas that the bank cannot satisfy. Bank versions move from 1.0.0 to 1.1.0
because paper selection changed; incompatible saved attempts are therefore not
silently restored.

These labels express curriculum intent, not independent psychometric
calibration. Scores remain practice evidence, not authenticated exam records.

## Executed validation

- Each Week 1–4 bank passed the shared JavaScript verifier across 1,000 seeded
  papers: ten unique questions, two per format, exact declared difficulty quotas,
  full-bank reachability, deterministic regeneration, objective keys, partial and
  pending coding scores, stale-code rejection and attempt restoration. All other
  published banks (Weeks 5–19) also passed after the shared-engine change.
- The verifier also rejected an unknown difficulty, an incomplete difficulty
  policy and a quota whose counts do not match the paper contract.
- All 60 Python reference solutions in Weeks 1, 3 and 4 passed their five named
  standard-library checks. All 20 Week 2 SQL tasks retained one `SELECT`/`WITH`
  reference and five complete fixture/result contracts; actual PGlite execution
  remains a browser-runtime check.
- Node syntax checks passed for the assessment engine, verifier, browser entry
  point and shared site shell.
- The focused Week 1–4 pytest suite passed all 216 tests. The complete published
  assessment regression suite passed all 1,171 tests. Ruff lint and format checks
  passed for the four modified Python test files, and strict mypy passed those
  files with a fresh cache.
- UTF-8 reads and YAML front matter passed for all changed lesson and assessment
  pages. Static checks also passed for required review metadata, reciprocal depth
  links, weekly assessment links, balanced code fences, the audience routes and
  the stated learning-check purpose. The modified Python tests compile, and
  `git diff --check` reports no whitespace errors.

The broader configured regression command could not finish locally because the
available environment does not contain the Week 15 `langgraph` dependency; it
stopped during collection before running tests. The configured Python 3.13.12 CI
suite remains required before promotion. Publication is a separate gated action.
