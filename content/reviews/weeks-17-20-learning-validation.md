# Weeks 17–20 audience and learning validation

## Scope and decision

This batch validates both lesson depths and the assessment for:

- Week 17 — multi-agent coordination;
- Week 18 — agent evaluation;
- Week 19 — agent safety and guardrails; and
- Week 20 — reliability and failure handling.

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
| 17 | The supervisor, specialist boundaries, handoffs and fail-closed comparison were technically strong. Neither route stated its prerequisite floor or separated the essential coordination path from remote-worker production concerns, and the beginner route lacked an eight-hour study plan. Short questions had no applied candidates and coding had no foundation candidates. | Added audience-specific prerequisites, a first-wave-to-commercial core route, explicit production stretch topics and an eight-hour beginner plan. Classified small contract and implementation tasks so every paper can combine recognition with application. |
| 18 | The 28-case evaluator already covered outcomes, trajectories, denominators, slices and safety honestly. A new learner still needed a bounded path through those ideas, while subjective judges, stochastic trials and live telemetry could look like first-pass requirements. Coding had no foundation-labelled candidates. | Added beginner and experienced starting points, an eight-hour case-to-gate route and explicit stretch boundaries. Classified five bounded metric functions as foundation coding while retaining the deeper evaluator tasks as applied work. |
| 19 | The gateway, exact approval, tenant isolation, audit minimisation and reversal contracts were coherent, but the beginner page advertised six hours and neither route clearly separated the local execution boundary from production sandbox and durable-ledger work. Short and coding difficulty pools were one-sided. | Restored an eight-hour beginner route, stated prerequisite and core/stretch boundaries, and balanced implementation-specific short answers with five foundational guardrail coding tasks. |
| 20 | The reliability lesson covered the required failure matrix, bounded retry, circuits, fallbacks, queue state and dead letters. The beginner route advertised six hours, and distributed coordination, transactional queue semantics and SLO work were not explicitly deferred. Short and coding pools could not produce mixed-difficulty papers. | Added the eight-hour failure-to-DLQ route, clarified the experienced evidence path and deferred distributed production extensions. Balanced implementation-specific short answers with five foundational reliability helpers. |

## Assessment decision

All four banks retain 100 unique questions and every paper retains ten questions:
two single-choice, two multiple-correct, two matching, two short exact-answer and
two Python coding questions. Bank prompts, answer keys, explanations, reference
solutions and executable checks are unchanged; only curriculum difficulty labels
and paper-selection policy changed.

Every generated Week 17–20 paper now has one foundation and one applied question
from each format, for a five/five paper. Each pool has at least five candidates:

| Week | Single F/A | Multiple F/A | Matching F/A | Short F/A | Coding F/A |
| --- | ---: | ---: | ---: | ---: | ---: |
| 17 | 22 / 8 | 8 / 12 | 7 / 8 | 10 / 5 | 5 / 15 |
| 18 | 21 / 9 | 9 / 11 | 10 / 5 | 9 / 6 | 5 / 15 |
| 19 | 19 / 11 | 8 / 12 | 7 / 8 | 10 / 5 | 5 / 15 |
| 20 | 15 / 15 | 5 / 15 | 9 / 6 | 10 / 5 | 5 / 15 |

The bank versions move from 1.0.0 to 1.1.0 because selection behaviour changed.
That prevents an older saved attempt from silently restoring against a different
paper contract. Difficulty labels express curriculum intent; they are not
independent psychometric calibration, and scores remain practice evidence rather
than authenticated exam records.

## Executed validation

- Each Week 17–20 bank passed the shared JavaScript verifier across 1,000 seeded
  papers: ten unique questions, two per format, exact five/five difficulty
  balance, full-bank reachability, reproducible generation, scoring and saved
  attempt behaviour.
- The focused Week 17–20 suite passed 369 tests covering all 80 coding
  references, deliberate wrong solutions, assessment-bank contracts and the
  multi-agent, evaluation, safety and reliability labs.
- The complete published assessment regression suite passed all 1,235 tests.
- The CI-equivalent non-container Python regression suite passed all 1,905
  tests. The four runnable Week 17–20 CLI smokes also passed.
- Ruff lint and format checks passed for the complete 83-file CI target. Strict
  mypy passed the same target with explicit package bases.
- Node syntax, JSON parsing, required metadata, reciprocal depth links,
  assessment links, balanced code fences, eight-hour beginner routes and the
  stated learning-check purpose passed. A structural comparison with the merged
  base proves that prompts, keys, explanations, reference solutions and coding
  checks did not change. `git diff --check` reports no whitespace errors.

The Week 12 PostgreSQL/pgvector container integration remains a pull-request CI
gate. No service, database or runtime implementation changed in this
learning-content batch.
