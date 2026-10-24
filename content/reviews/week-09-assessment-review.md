---
week: 9
status: reviewed
version: 1.0.0
last_reviewed: 2026-10-24
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested Week 9 within the established explicitly approved build-check-push-publish workflow
---

# Week 9 assessment review

## Baseline and scope

Base main commit: `ee48816e9e27ba99c8078998b9c3ababe03fe4d1`; tree
`d35b93c1bd13340ea8919007e5ae3e8bb683e3b7`. The assessment branch starts
from a freshly fetched origin/main. Root AGENTS.md is the sole applicable
instruction file. No Design specification applies to this curriculum. Existing
untracked Week 5–8 QA work is preserved; no subagents were used.

Inspected Path.md's Week 9 scope, both complete lessons, lab README, dataset
manifest and all six implementation modules, all Week 9 evaluation tests,
the existing assessment conventions, shared validator/verifier, dependency
pins, navigation and candidate workflow. The existing 30-case dataset/source
oracle, saved results and review templates remain unchanged.

Scope is a new assessment bank/page/test/review, additive lesson links,
navigation/README integration and extending existing CI. Earlier assessments,
lab implementations, shared runtime/scoring/styles, dependencies and Jekyll
configuration are unchanged. The existing source and answer policies are not
replaced by the small teaching functions.

## Accepted learning coverage

The bank has 100 authored questions: 30 single-choice, 20 multiple-correct,
15 matching, 15 short syntax and 20 Python exercises. IDs/prompts are unique;
every item has a topic, difficulty, answer key and explanation. Each coding
prompt states its own contract so related questions need not appear in the
same random paper. No independent human item validation or psychometric
calibration is claimed.

| Requirement | Assessment evidence |
| --- | --- |
| Parsing/chunking quality | Independent raw-source oracle, bad-label rejection, parsed-atom versus chunk-unit retention and controlled-audit limits |
| Retrieval quality | Full source-unit scope, requested-slot precision, gold-denominator recall, cutoff reciprocal rank, candidate ceiling and binary/graded distinction |
| DCG/nDCG | Declared exponential gain, one-based log discount, full ideal label universe, absent hits and zero ideal gain |
| Context relevance/support | Valid source-unit precision/recall, duplicate span collapse, own-source atoms and post-ranking evidence loss |
| Exact match and similarity | Display/case/whitespace normalization, multiple references, preserved codes/values/negation, lexical counterexamples and unmeasured semantic fields |
| Faithfulness/correctness/citations | Traceability versus claim support/task adequacy, correct-from-memory case and unavailable-fact abstention |
| Human/LLM evaluation | Pending nulls, four rubric axes, exact integer ratings, rationale/model/prompt identity, calibration and bias checks |
| Stored evaluation evidence | Case/run association, complete canonical fingerprints, denominator-aware means, raw records and protected prior outputs |
| Regression and later held-out design | Matched case populations, conflicting exact-match/support movement, separate groups and declared related-family split checks |

Every coding task has five public checks and a declared input/result/error/
mutation policy. References use only re, math, json and hashlib. No evaluator
weights, GPU, paid endpoint, model judge or free-form generator is loaded.
The twenty tasks exercise Python syntax and bounded evaluation behavior using
synthetic data rather than assigning unexecuted semantic scores.

Teaching interfaces are explicit. Normalization uses the lab's narrow positive
S-label regex. exact_answer additionally rejects a reference whose normalized
content is empty. atom_fraction counts listed lexical checks; dataset label
uniqueness is enforced separately. Ranking helpers declare a 64-item/cutoff
bound; observed means declare finite measurements within a bounded range and
explicitly allow bool indicators. Rating integers still reject bool.

Source-unit metric keys use tuples of tenant/document/version/location to avoid
delimiter ambiguity. support_complete requires each atom within one surviving
quote of its own key rather than manufacturing a phrase across joined spans.
audit_units is an in-memory retention exercise: atoms may survive in several
chunks of one unit, so its result does not prove boundary coherence. These
declared helper contracts do not rewrite the existing lab's implementations.

failure_flags consumes trusted stage metrics. Template construction consumes
validated record identities, and rating aggregation consumes already validated
reviews; valid_review is the separate untrusted schema/association boundary.
Grouped split planning is a proposed-data helper, not a change to the lab's
practice-only loader or a claim to detect every source of leakage.

## Correctness review and integration

Applied the ds-code-review instructions to the bounded change, tracing
independent labels, scope, denominators, nulls, candidate/context/answer losses,
rating state and exact observation association. Challenges include wrong
denominators, zero filtering, missing ideal labels, forged pending ratings,
stale records, group-name collisions and changed paired populations.

No outstanding actionable correctness/regression finding is supported after
the checks below. This is not an exhaustive security audit, real-model quality
study or production-readiness certification. Independent human content review
and hidden item calibration remain outside this pass.

The reference validation rejects mixed invalid relevance-grade types before
sorting so invalid input raises the promised ValueError. Floating DCG checks
use tolerances where appropriate and import their own math helpers rather than
depending on a student's implementation namespace. Canonical hash tests use
literal independently assembled JSON bytes, and metric tests use known
2/3, 2/5, 1/2, 1/3 and reversed graded-gain calculations.

The static engine still draws two of each format, ten distinct questions and
100 marks. Single/short/multiple require complete keys; matching earns 2.5 per
pair and coding earns two per passed check. Existing seed/version links,
saved attempts, locked submissions, explanations/references, blank printing
and JSON result downloads remain available.

All lesson characters are preserved after removing the one added assessment
paragraph from each lesson. ASSESSMENT_WEEKS adds 9; PUBLISHED_WEEKS is unchanged.

## Executed local verification

Environment: Python 3.12.14, Node 24.22.1, pytest 9.1.1, Ruff 0.15.22,
mypy 2.3.0 and Chromium 153.0.8010.0. Browser worker runs report Python 3.13.2.

- 706 targeted pytest tests pass: all nine assessment suites, Week 7 hybrid,
  Week 8 assistant, Week 9 evaluation and Week 1 service regressions. The new
  assessment contributes 63 tests; all 46 existing Week 9 lab tests pass.
- Every reference passes five checks, every starter scores zero, and every
  distinct plausible wrong implementation loses marks.
- Composed checks cover independent ranking arithmetic, lexical proxy limits,
  raw-source/chunk-loss separation, foreign-source denial of metric credit,
  paired exact-match gains with support loss, changed observation digests and
  separate actual-rating coverage/group counts.
- The JavaScript verifier passes 1,000 balanced reproducible papers, complete
  item reachability, objective keys, partial/pending scoring, saved attempts
  and stale-code rejection.
- All twenty references pass actual browser Python (100 checks). A complete
  paper scores 100/100, downloads, locks source and restores after reload.
- Runtime blocking leaves 80/80 graded plus 20 pending; retries recover through
  90/90 to 100/100. Stop, execution timeout and replacement source pass.
- Blank print contains ten questions without keys. Share/new-paper reproduction,
  active navigation and all nine dashboard assessment links pass.
- All nine assessment pages pass 390px light/dark overflow checks, as do all
  100 Week 9 prompt texts. Desktop and stable mobile rendering are inspected.
- Completed browser checks report no page errors or unexpected failed requests.
- Ruff/format and strict mypy pass for the Week 7–9 assessment test modules.
  JavaScript syntax, whitespace, AST compilation/import/call bounds, workflow
  structure/read-only permissions and complete lesson preservation pass.

This is a targeted pass, not an unrestricted whole-repository run; the
unrelated Windows-only comparison module remains outside it. No actual evaluator
model, LLM judge, independent human rating campaign, performance workload or
arbitrary PDF/OCR extraction test is claimed.

The existing workflow retains all prior gates and adds Week 9 assessment lint/
typing plus evaluation-lab tests. The exact candidate must pass remote pytest
CI on its assessment branch before main promotion. Pages build/deployment and
exact live assets/scoring are checked afterward. Local results and this record
do not substitute for remote CI; no remote success is claimed in advance.
No branch-protection policy or ability to prevent administrative bypass changes.

Local previews render the existing layout with QA Markdown/Liquid rather than
Ruby/Jekyll. The browser runtime relay retrieves original HTTPS assets with TLS
verification and normal browser security; deployed URLs are unchanged. Workers
run without cross-origin isolation or SharedArrayBuffer. QA screenshots disable
transient resize animations; product styles are unchanged.

## Primary references and practical limits

Primary papers opened on 2026-10-24:

- [BERTScore](https://arxiv.org/abs/1904.09675): contextual candidate/reference token comparison.
- [Ragas](https://arxiv.org/abs/2309.15217): distinct RAG evaluation dimensions.
- [Judging LLM-as-a-Judge](https://arxiv.org/abs/2306.05685): bias and agreement in the study's settings.

Metric formulas, gain/cutoff policies, status/review semantics and dataset
examples are grounded in the inspected repository contracts. No universal
similarity threshold, judge error rate or semantic quality is inferred.

Public keys and editable client-side scores are practice records, not
authenticated examination results. Five checks give bounded feedback rather
than proof for every possible solution. The reused pinned Pyodide worker keeps
its load/execution deadlines, Stop and pending-mark behavior; time termination
does not impose a memory cap. Google Colab remains optional copy/paste with
sign-in and no automatic result sync. No backend, learner store, new dependency
or automatic review service is added. Later bank edits require a version bump;
rollback is a normal feature revert.
