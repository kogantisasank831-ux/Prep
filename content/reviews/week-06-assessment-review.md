---
week: 6
status: approved
version: 1.0.0
last_reviewed: 2026-10-24
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested Week 6 within the established explicitly approved build-check-push-publish workflow
---

# Week 6 assessment review

## Scope and inspected baseline

Baseline main commit: 5f0e87a24a57cf30694c068421fd3fa1e22c23bc, tree
f199a0cc67beff18893802b882f4f50d0072e3c0. Work uses week06-assessment
from freshly fetched origin/main. Root AGENTS.md is the sole applicable
instruction file; no Design directory exists. Earlier untracked Week 5 QA
work is preserved. No subagents were used.

Inspected Week 6 main/beginner scope, examples and evaluation sections, all of
chunking.py, compare.py, fixtures.py, queries.jsonl, lab README and existing
chunking tests, plus the prior content review and assessment conventions,
runner interfaces, navigation and declared dependencies. The assessment adds
practice to the already-published lessons without rewriting them or the lab.

There are 100 authored questions: 30 single-choice, 20 multiple-correct,
15 matching, 15 short syntax and 20 written Python tasks. IDs/prompts are
unique; all items have topics, difficulties, keys and explanations. No
independent human item review or psychometric calibration is claimed.

## Coverage and contracts

| Lesson requirement | Assessment evidence |
| --- | --- |
| Parsing trust boundary | PDF reading order, OCR/table ambiguity, hard rejection versus review, bounded fixture validation |
| Metadata and provenance | Scoped source identity, heuristic metadata/missing labels, canonical text, parser/layout/status fingerprints |
| Fixed and overlap windows | Exact integer parameters, positive stride, final stopping, preserved fragments, half-open trimmed-block offsets |
| Sentence and structure | Soft grouping target, regex limitations, atomic nonparagraph units, heading text plus locations, isolated-heading differences |
| Semantic boundaries | ASCII term-set Jaccard, strict threshold comparison, finite score domains, declared adjacency and versioned policy identity |
| Parent-child retrieval | Children-only matching, stored parents, full source/policy lineage, repeated authorization, deduplication |
| Context admission | Whole units only, separator costs, ranked-order greedy admission, skipped oversized units |
| Evaluation | Chunk-budget document recall, within-source support atoms, no-gold populations, fixed comparison controls and holdout hygiene |
| Honest costs and operations | Stored UTF-8 bytes versus characters, indexed vector estimates, null token/answer grades, privacy, rollback and manifest trust |

The twenty coding tasks each declare their signature, domain, output, error
and mutation policies. Five public checks per task exercise normal behavior,
relevant boundaries and incorrect interpretations. Reference imports are only
math, re, hashlib and json. No PDF parser, OCR engine, model package, GPU,
inference service, API key or root dependency is introduced.

Helpers are intentionally smaller than the complete typed lab. Canonical-text
and raw-window helpers permit empty input as stated; accepted source documents
do not. The single-block router does not decide document-wide block counts,
duplicate locations or heading-only status. Its narrow numeric regex is the
fixture grammar, not source-file validation. Hard malformed values reject;
uncertain row formats or replacement characters require review without repair.

Sentence grouping is paragraph-only and keeps a soft target. Structure inputs
are already-trimmed valid blocks; the simple policy can omit isolated headings.
The paragraph boundary helper consumes supplied adjacent scores and does not
learn or call a similarity model. The policy hash preserves declared parameter
order; the representation hash uses its explicitly stated compact JSON recipe,
not a claim to implement the lab's whole dataclass schema.

Parent records and source tuples are simplified synthetic objects. The lineage
helper checks tenant/document/version/digest and policy, while expansion checks
read permissions for child and parent separately. Callbacks and grants are
trusted inputs to the exercise, not new server authentication. A separate
budget helper counts characters and newline separators, preserves whole units,
and continues after an oversized candidate rather than truncating it.

Document recall takes the chunk cutoff before deduplicating document hits.
Unlike chunk IDs, document IDs can repeat in a ranked chunk list. The caller
guarantees the practice snapshot's one-tenant/version-per-ID rule; production
labels need full scope. Support completeness joins context within each labelled
document and averages complete sources, never pooled atom hits. It is a
conservative casefolded substring proxy: split phrases and equivalent wording
can fail, and matching words do not prove entailment. No-gold queries remain
undefined and counted separately from observed zero results.

Measurement summaries distinguish stored and indexed populations. Parents and
duplicate stored text consume bytes, but only children consume coordinate
storage in parent-child mode. Float32 storage is an estimate excluding all
metadata, IDs, objects and index overhead. Token lengths and generated-answer
quality remain null because neither is measured.

## Integration and mobile correction

The existing paper, scoring and runtime JavaScript is unchanged. A paper draws
two of each format, ten unique questions, using a seed and bank version with
shuffled order. Ten marks per item: exact single/short keys, complete-set
multiple-correct, 2.5 per matching pair and two per passed coding check.
Saved attempts, share links, blank print, locked submission, explanations,
reference solutions and result downloads remain supported.

The pinned Pyodide 0.29.3 worker, 45-second runtime-loading deadline, five-second
execution limit and Stop behavior are unchanged. Failed loading leaves coding
marks pending for retry against submitted source. Colab remains optional and
requires manual copy/paste; opening it sends no answer or synchronized score.

Browser QA exposed a long technical identifier overflowing the 390px viewport
to 442px. Added overflow-wrap:anywhere to assessment question cards. The
viewport now remains 390px; source prompts are retained in full. Code blocks
retain their existing preformatted internal scrolling. The fix was checked on
all six assessment pages in light/dark themes and against all 100 Week 6 prompts.

Changes are limited to the new page/bank/tests/review, assessment.css wrapping,
shell.js enablement, README and one assessment-link paragraph in each Week 6
lesson. Removing those paragraphs reproduces the complete original lesson
texts, front matter and examples exactly. Labs, earlier banks, runtime/scoring
code, dependencies, Jekyll configuration and CI remain unchanged.

## Validation executed

Environment: Python 3.12.14, Node 24.19.0, Chromium 153.0.8010.0; actual browser
workers use the existing Python 3.13.2 runtime.

- 413 targeted pytest tests pass: all assessment suites through Week 6, all
  45 existing Week 6 lab tests and Week 1 service regressions. The new suite
  has 63 tests including all twenty references, starters and plausible wrong
  solutions plus bank/paper and composed behavior checks.
- All twenty references pass five checks each. Every unimplemented starter
  gets zero and every plausible incorrect implementation loses marks.
- Composed checks prove exact window coverage/reconstruction across parameter
  combinations, local offsets excluding separators, authorized parent expansion
  before whole-unit budgets, document hits without complete support, and distinct
  parent storage/child vector costs.
- The JavaScript validator passes 1,000 balanced reproducible papers, all items
  reachable, objective keys, partial/pending scores, no bank mutation, stale-code
  rejection and restored attempts.
- All twenty references pass actual browser module-worker execution. A complete
  paper scores 100/100, restores after reload, downloads JSON and locks answers.
- Runtime blocking leaves 80/80 graded plus 20 pending; retries recover through
  90/90 to 100/100. Stop, infinite-loop deadline, source retention and corrected
  replacement solution all pass.
- Blank print has ten questions without answer keys. Mobile 390px light/dark,
  navigation, new-paper reproduction and six dashboard assessment links pass.
  Screenshot inspection confirms readable desktop/mobile presentation.
- All six assessment pages pass light/dark mobile overflow checks; all 100
  Week 6 prompt strings pass the mobile wrapping sweep.
- Completed browser runs have no page errors or unexpected failed requests.
- Ruff lint/format, strict mypy, JavaScript syntax and final whitespace checks
  pass. AST inspection confirms only the stated standard-library imports and
  no authored file reads, input calls, eval/exec or dynamic imports.
- Source comparisons confirm complete lesson preservation and unchanged labs,
  prior banks and shared runtime/scoring implementation.

Local preview uses the current layout with QA Markdown/Liquid/YAML rendering,
not local Ruby/Jekyll. The QA relay fetches original HTTPS runtime assets with
TLS verification and normal browser security. No deployed URLs change. Browser
tests run without cross-origin isolation or SharedArrayBuffer. Hosted Pages
deployment, exact live assets and live paper scoring follow publication.

## Sources, limitations and rollback

Primary documentation checked on 2026-10-24:

- [pypdf extraction, layout and OCR limitations](https://pypdf.readthedocs.io/en/stable/user/extract-text.html)
- [Python regular-expression syntax and splitting](https://docs.python.org/3/library/re.html)

Lab-specific constants, outcomes and measurement definitions are grounded in
the inspected repository. The public five-document/nine-query collection is
synthetic practice data, not independent policy/model evaluation. No learned
boundary model, real PDF/OCR run, generated answers or measured production
latency/memory is claimed. An assessment score does not authorize payment or
any procurement-system write.

Answer keys and editable local scores are public practice records, not an
authenticated examination system. Five checks provide bounded feedback, not
proof of every possible implementation. Worker termination limits time, not
memory; runtime loading still depends on network/browser support. No learner
identity, central score upload, paid service or backend is added.

Rollback is a normal feature revert. Future bank changes must increment the
bank version; attempts remain separated by week/version/seed.
