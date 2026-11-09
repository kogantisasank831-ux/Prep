# Weeks 13–16 audience and learning validation

## Scope and decision

This batch validates both lesson depths and the assessment for:

- Week 13 — tool calling;
- Week 14 — workflows versus agents;
- Week 15 — LangGraph fundamentals; and
- Week 16 — memory and context engineering.

The weekly questions remain learning checks. They assess whether a learner can
recognise a concept, predict an outcome and apply a small lesson contract. The
future Data Scientist and AI Engineer interview banks and the topic cheat sheets
remain separate artifacts with a different purpose.

## Validation standard

| Area | Beginner version | Production version | Assessment |
| --- | --- | --- | --- |
| Starting point | Treat the weekly topic as new and state the small prerequisite set | Assume basic familiarity with the preceding system and Python concepts | Assume only material taught in the lesson |
| Explanation | Use plain language, one running procurement example and concepts before operational detail | Emphasise trade-offs, failure modes, evidence and remaining limits | Test understanding rather than role-specific interview performance |
| Route | Mark an eight-hour first-pass core and defer stretch detail | State the experienced audience and provide a bounded evidence path | Draw ten questions: two per format with a declared difficulty mix |
| Completion evidence | Explain the flow and predict an observed result | Defend a design choice and state what it does not prove | Explanations plus five executable checks for every coding question |

## Findings and remediation

| Week | Finding | Change |
| --- | --- | --- |
| 13 | Both routes already had a coherent eight-hour build and unusually strong execution-boundary coverage. They did not explicitly state the beginner prerequisite floor or separate the essential proposal-to-result loop from provider adapters, approval ledgers and lost-response recovery. Four assessment formats had no foundation-labelled candidates. | Added explicit audience assumptions, marked the proposal → validation → authority → execution → correlated-result path as the core, identified deeper work as stretch and classified foundational recognition and bounded coding tasks. |
| 14 | The workflow-versus-agent comparison was strong, but the beginner route lacked an eight-hour plan and neither route clearly separated controller-selection essentials from orchestration-pattern and real-model evaluation extensions. Several difficulty pools could not generate a five/five paper reliably. | Added a beginner study plan, prerequisite and core/stretch guidance; clarified the experienced route; and balanced every question format without changing prompts or keys. |
| 15 | The graph explanation, reducer contract and interrupt/resume lab were technically sound. A new learner had no explicit prerequisite floor or study plan, while production extensions such as durable persistence and replay were not clearly deferred. The short and coding pools had too few applied and foundation candidates respectively. | Added audience-specific routes and an eight-hour beginner path, kept topology, reducers, checkpoints and same-thread resumption in the core, deferred production persistence and concurrency, and corrected difficulty labels. |
| 16 | The memory lessons already separated runtime, checkpoint and long-term scopes well. The beginner route still needed a bounded study path, and production concerns such as encryption, migration, backup and conflict arbitration could look like first-pass requirements. Single-choice, short and coding pools were also too uneven for the declared paper policy. | Added prerequisites, a beginner eight-hour plan and explicit core/stretch boundaries; preserved the governed-memory lifecycle; and balanced the assessment pools for repeatable mixed-difficulty papers. |

## Assessment decision

All four banks retain 100 unique questions and every paper retains ten questions:
two single-choice, two multiple-correct, two matching, two short exact-answer and
two Python coding questions. Bank prompts, answer keys, explanations and coding
checks are unchanged; only curriculum difficulty labels and paper-selection
policy changed.

Every generated Week 13–16 paper now has one foundation and one applied question
from each format, for a five/five paper. Each pool has at least five candidates:

| Week | Single F/A | Multiple F/A | Matching F/A | Short F/A | Coding F/A |
| --- | ---: | ---: | ---: | ---: | ---: |
| 13 | 8 / 22 | 5 / 15 | 5 / 10 | 5 / 10 | 5 / 15 |
| 14 | 16 / 14 | 6 / 14 | 7 / 8 | 10 / 5 | 5 / 15 |
| 15 | 19 / 11 | 7 / 13 | 5 / 10 | 10 / 5 | 5 / 15 |
| 16 | 25 / 5 | 8 / 12 | 8 / 7 | 10 / 5 | 5 / 15 |

The bank versions move from 1.0.0 to 1.1.0 because selection behavior changed.
That prevents an older saved attempt from silently restoring against a different
paper contract. Difficulty labels express curriculum intent; they are not
independent psychometric calibration, and scores remain practice evidence rather
than authenticated exam records.

## Executed validation

- Each Week 13–16 bank passed the shared JavaScript verifier across 1,000 seeded
  papers: ten unique questions, two per format, exact five/five difficulty
  balance, full-bank reachability, reproducible generation, scoring and saved
  attempt behavior.
- The focused Week 13–16 suite passed 386 tests covering all 80 coding
  references, deliberate wrong solutions, assessment-bank contracts and the
  tool-calling, controller, LangGraph and memory labs.
- The complete published assessment regression suite passed all 1,235 tests.
- The CI-equivalent non-container Python regression suite passed all 1,905
  tests. The four runnable CLI smokes also passed over actual local SQLite and
  checkpoint/memory paths.
- Ruff lint and format checks passed for the complete 83-file CI target. Strict
  mypy passed the same target with explicit package bases.
- Node syntax checks, JSON parsing, required lesson/assessment metadata,
  reciprocal depth links, assessment links, balanced code fences, eight-hour
  routes and the stated learning-check purpose passed. `git diff --check`
  reports no whitespace errors.

The Week 12 PostgreSQL/pgvector container integration remains a pull-request CI
gate. No service, database or runtime implementation changed in this
learning-content batch.
