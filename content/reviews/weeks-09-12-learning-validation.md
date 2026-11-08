# Weeks 9–12 audience and learning validation

## Scope and decision

This batch validates both lesson depths and the assessment for:

- Week 9 — RAG evaluation;
- Week 10 — LLM observability;
- Week 11 — RAG security; and
- Week 12 — deploying the guarded RAG service.

The weekly questions remain learning checks. They assess whether a learner can
recognise a concept, predict an outcome and apply a small lesson contract. The
future Data Scientist and AI Engineer interview banks and the topic cheat sheets
remain separate artifacts with a different purpose.

## Validation standard

| Area | Beginner version | Production version | Assessment |
| --- | --- | --- | --- |
| Starting point | Treat the weekly topic as new and state the small prerequisite set | Assume basic familiarity with the preceding pipeline and Python concepts | Assume only material taught in the lesson |
| Explanation | Use plain language, one running procurement example and concepts before operational detail | Emphasise trade-offs, failure modes, evidence and remaining limits | Test understanding rather than role-specific interview performance |
| Route | Mark an eight-hour first-pass core and defer stretch detail | State the experienced audience and provide a bounded evidence path | Draw ten questions: two per format with a declared difficulty mix |
| Completion evidence | Explain the flow and predict an observed result | Defend a diagnosis or design and state what it does not prove | Explanations plus five executable checks for every coding question |

## Findings and remediation

| Week | Finding | Change |
| --- | --- | --- |
| 9 | Both lessons already separated retrieval, context, answer and citation claims carefully. The beginner page did not explicitly state its prerequisite floor or distinguish the first-pass evaluation core from experiment-design extensions. | Added a new-to-evaluation starting point, a core stage-diagnosis and metric route, and explicit stretch work for judge calibration, grouped splits and expanded experiments. Clarified the experienced audience and retained evidence path in the production lesson. |
| 10 | The tracing story and eight-hour table were coherent, but a new learner could read cost, OpenTelemetry and retention concerns as equal-weight prerequisites. Matching, short and coding items were also all labelled applied despite including direct concepts and bounded transformations. | Made the beginner foundation and experienced audience explicit, separated request-level trace diagnosis from deeper operations topics, and reclassified the genuinely foundational bank items. |
| 11 | The lessons gave unusually clear security limits, but the first-pass controls were not separated from detector analysis, representation pins, revocation races and consumer hardening. Every assessment item was labelled applied, including direct trust and authorization concepts. | Added explicit beginner and in-depth routes, kept the trust/permission/output gates in the core, moved the deeper control analysis to stretch, and classified foundational recognition and small applications accordingly. |
| 12 | The service lesson already had a usable eight-hour build route. It did not explicitly say that the beginner route requires no prior FastAPI, PostgreSQL or Docker experience, or separate the demonstrable request path from cancellation, caching, streaming and production operations. Every assessment item was labelled applied. | Stated both audience assumptions, marked the request/identity/storage/health/container path as core, marked the operational extensions as stretch, and classified foundational service concepts and bounded applications. |

## Assessment decision

All four banks retain 100 unique questions and every paper retains ten questions:
two single-choice, two multiple-correct, two matching, two short exact-answer and
two Python coding questions. Bank questions and answer keys are unchanged; only
curriculum difficulty labels were corrected where needed.

Every generated Week 9–12 paper now has one foundation and one applied question
from each format, for a five/five paper. Each bank has enough independently
reviewed questions to satisfy that policy:

| Format | Foundation items in each bank | Applied items in each bank | Per-paper selection |
| --- | ---: | ---: | ---: |
| Single-choice | 10 | 20 | 1 + 1 |
| Multiple-correct | 7 | 13 | 1 + 1 |
| Matching | 5 | 10 | 1 + 1 |
| Short exact-answer | 5 | 10 | 1 + 1 |
| Python coding | 7 | 13 | 1 + 1 |

The bank versions move from 1.0.0 to 1.1.0 because selection behavior changed.
That prevents an older saved attempt from silently restoring against a different
paper contract. The difficulty labels express curriculum intent; they are not
independent psychometric calibration, and scores remain practice evidence rather
than authenticated exam records.

## Executed validation

- Each Week 9–12 bank passed the shared JavaScript verifier across 1,000 seeded
  papers: ten unique questions, two per format, exact five/five difficulty
  balance, full-bank reachability, reproducible generation, scoring and saved
  attempt behavior.
- The focused Week 9–12 suite passed 553 tests covering all 80 coding references,
  deliberate wrong solutions, assessment-bank contracts and the evaluation,
  tracing, security and service labs.
- The complete published assessment regression suite passed all 1,235 tests.
- Ruff lint and format checks passed for the four modified Python tests. Strict
  mypy passed the same files with explicit package bases.
- Node syntax checks passed for the assessment engine, browser entry point and
  verifier. JSON parsing, required lesson/assessment metadata, reciprocal depth
  links, assessment links, balanced code fences, audience routes and the stated
  learning-check purpose also passed. `git diff --check` reports no whitespace
  errors.

The Week 12 PostgreSQL/pgvector container integration remains a pull-request CI
gate. No service or database code changed in this learning-content batch.

