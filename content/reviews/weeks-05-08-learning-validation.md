# Weeks 5–8 audience and learning validation

## Scope and decision

This batch validates both lesson depths and the assessment for:

- Week 5 — Embeddings and vector retrieval;
- Week 6 — Document parsing and chunking;
- Week 7 — Sparse and hybrid retrieval; and
- Week 8 — Reranking and context construction.

The batch is approved as a learning-content revision. It does not add the future
Data Scientist or AI Engineer interview banks and does not add cheat sheets.
Those artifacts have a different purpose from the weekly understanding checks.

## Validation standard

| Area | Beginner version | Production version | Assessment |
| --- | --- | --- | --- |
| Starting point | Treat the weekly retrieval topic as new and state the small prerequisite set | Assume basic familiarity with earlier retrieval concepts and Python | Assume only material taught in the lessons |
| Explanation | Use the continuing procurement example, plain language and concepts before implementation detail | Emphasise contracts, failure modes, evaluation and operational trade-offs | Test recognition, prediction and small applications rather than interview performance |
| Route | Provide an eight-hour core path and label stretch material | Provide an eight-hour evidence path suitable for an experienced learner | Draw ten questions: two per format and one per difficulty in every format |
| Completion evidence | Explain the pipeline and diagnose a simple result | Defend a design, measurement and stated limitation | Explanations plus executable checks for coding tasks |

## Findings and remediation

| Week | Finding | Change |
| --- | --- | --- |
| 5 | The beginner explanation was clear, but it directed the learner to the production build after only a short conceptual pass. The production page had outcomes but no evidence-oriented timetable. | Added a complete beginner route from vector intuition through evaluation, labelled storage/ANN/model integration as stretch work and added a production evidence path. |
| 6 | Both versions used the same strong P-105 example, but a new learner could treat parser manifests, semantic boundaries and storage accounting as equal first-pass goals. | Prioritised parser status, source locations, boundary trade-offs and complete evidence; moved deeper compatibility/accounting details to stretch work and stated the production audience explicitly. |
| 7 | The sparse/dense comparison was understandable, but the beginner route did not clearly separate BM25/RRF essentials from manifest and parameter-depth work. | Added a four-stage beginner route around exact tokens, BM25 intuition, authorization and RRF; labelled advanced identity and sensitivity work as stretch and clarified production prerequisites. |
| 8 | The lesson covered the complete assistant pipeline, but query rewriting, compression and model integration competed with the core reranking/context ideas for beginner attention. | Centred the first pass on candidate ceilings, fair reranking comparison, evidence completeness, budgets and citations; deferred multi-query, compression, model and position experiments to stretch work. |

## Assessment decision

All four banks retain 100 unique questions and each paper retains ten questions:
two single-choice, two multiple-correct, two matching, two short exact-answer and
two Python coding questions. The bank topics cover the lesson's conceptual,
failure-diagnosis, measurement and implementation boundaries. Short answers
check essential terms or syntax; coding tasks apply small, declared contracts
with synthetic data and five executable checks.

The shared assessment engine already supports an executable difficulty policy.
Weeks 5–8 now require one foundation and one applied item in every question
format, producing five foundation and five applied questions in every paper.
This prevents the banks' larger applied pools from dominating a random paper.
All four bank versions move from 1.0.0 to 1.1.0 because paper selection changed;
incompatible saved attempts are not silently restored.

Difficulty labels express curriculum intent, not independent psychometric
calibration. Scores remain practice evidence, not authenticated exam records.

## Executed local validation

Environment: Python 3.12.14, Node 24.22.1, pytest 9.1.1, Ruff 0.15.22 and
mypy 2.3.0.

- Each Week 5–8 bank passed the shared JavaScript verifier across 1,000 seeded
  papers: ten unique questions, two per format, one foundation and one applied
  item per format, full-bank reachability, deterministic regeneration,
  objective keys, partial/pending coding scores, stale-code rejection and
  attempt restoration.
- The focused Week 5–8 assessment and lab suite passed all 457 tests. This
  includes reference solutions, deliberately wrong implementations and the
  retrieval, chunking, hybrid-search and assistant regression suites.
- The complete published assessment suite for Weeks 1–20 passed all 1,235
  tests after the bank-version and selection-policy changes.
- Ruff lint and format checks and strict mypy passed for the four modified test
  modules. JavaScript syntax and `git diff --check` passed.
- Static checks passed for UTF-8 content, balanced code fences, required review
  metadata, reciprocal beginner/production links, assessment links, explicit
  audience routes, the learning-check purpose and the declared difficulty
  quotas.

This is a targeted curriculum and assessment validation, not a psychometric
study, production model evaluation or security audit. Real-model retrieval
quality, ANN latency/memory and generated-answer quality remain explicitly
outside these local teaching fixtures.

## Candidate validation

The candidate branch must pass the repository's pull-request workflow on the
exact proposed commit before merge. Promotion to `main`, Pages deployment and
live-site verification remain separate approval-gated actions.
