---
week: 7
status: reviewed
version: 1.0.0
last_reviewed: 2026-10-24
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested Week 7 within the established explicitly approved build-check-push-publish workflow
---

# Week 7 assessment review

## Baseline and scope

Base main commit: ed91d3b93e412799cf59811c294a8cd6e4bbff6d, tree
8ed675b829c614d47a892185fa177a22eb5aabba. Work uses week07-assessment
from freshly fetched origin/main. Root AGENTS.md is the sole applicable
instruction file and is unchanged from the previously inspected version.
There is no Design directory. Earlier untracked Week 5/6 QA work is preserved.
No subagents were used.

Inspected main/beginner Week 7 scope, BM25/fusion examples and evaluation
sections; all of retrieval.py, fixtures.py, practice queries and existing
hybrid tests; comparison scope, local adapter and measurement paths; lab README,
content review, prior assessments and declared tooling. The scope is a new
practice bank/page and tests, navigation/lesson links, documentation and a
candidate pytest workflow. No retrieval lab, scoring/runtime code or old bank
is rewritten.

The bank has 100 authored questions: 30 single-choice, 20 multiple-correct,
15 matching, 15 short syntax and 20 Python tasks. IDs/prompts are unique and
all questions have topics, difficulties, keys and explanations. No independent
human item validation or psychometric calibration is claimed.

## Traceability and coding boundaries

| Accepted learning contract | Assessment evidence |
| --- | --- |
| Exact code identity | Internal hyphen/underscore/slash preservation, case, O/0 and unmapped aliases |
| BM25 arithmetic | TF versus DF, positive IDF, TF saturation, length normalization, unique query terms and stable huge-k1 arithmetic |
| Authorized snapshot | Full principal/tenant/document/version grants, exact allowlisted filters, partition reuse and private statistics |
| Candidate selection | Finite exact numeric types, strict score floors, short/empty results, deterministic ties and no zero padding |
| Score comparison | Stable signed min-max ranges, flat lists, scale/calibration limitations |
| RRF | Positive weights/constants, one-based contiguous ranks, duplicate/conflicting votes, weighted sums and raw contributor provenance |
| Depth and identity | Per-path truncation before union, output k, complete manifest and actual text/metadata corpus digests |
| Evaluation | Source-key resolution, own-chunk support atoms, requested-k precision, no-gold populations and source repeats |
| Validity and operations | Teaching fake versus real models, fair category comparisons, curated metadata, immutable continuity and unmeasured outcomes |

Every coding task has an explicit signature, input domain, result, error and
mutation policy, plus five public checks. Reference imports are only re,
collections, math, json and hashlib. No model, inference API, GPU or new
runtime dependency is required.

The helpers are bounded teaching contracts rather than replacements for every
typed lab class. TF math uses its declared 1..4000 token-length domain; positive
IDF permits df=0 as an arithmetic exercise while full scoring skips absent terms.
The tokenizer permits empty text but corpus chunks require tokens; requests
require nonblank queries. The scorer uses a snapshot index rather than the
full lab SourceChunk membership check. Stable ratios preserve huge finite k1
without weakening parameter validation.

Eligible-row helpers consume trusted grants. Denied records' metadata is never
inspected, filters cannot grant access, and partition reuse binds canonical
predicates and principal. These exercises do not authenticate a browser user
or prove constant-time/side-channel safety.

Fusion uses a trusted full-record snapshot fingerprint in its compact teaching
rows. The full lab compares complete SourceChunk records. A caller cannot treat
an arbitrary supplied fingerprint as authenticated. Raw candidate admission
already occurred upstream; fusion validation checks rank/provenance consistency
but does not infer a retriever's score floor. The corpus-digest task separately
binds actual text/metadata even when a supplied source hash is unchanged.

RRF sums ranks and weights rather than raw scores, retains raw contributor
values, rejects duplicate votes/ranks and conflicting snapshots, and cannot
recover a candidate absent from both prefixes. Candidate union deduplicates IDs,
not source meanings. Evidence keys resolve only inside the eligible snapshot;
atoms must occur in their own declared chunks. Source-repeat fractions retain
tenant/document/version and do not establish semantic redundancy.

## Review findings and release gates

Applied the ds-code-review skill to the bounded assessment diff and relevant
unchanged contracts, using this repository's review format. Traced inputs from
trusted grants/filters through statistics, candidate admission, provenance,
scoring and failure paths. Challenged tests with independent known arithmetic,
denied-record invariance, malformed rank/source contributions and source-bound
labels. No outstanding actionable correctness/regression finding is supported
within the reviewed scope after local verification. This is not a security
audit, production model evaluation or production-readiness certification.

The existing Pages build did not run pytest. Added the read-only
Weekly assessment checks workflow, with official checkout/setup-python actions
pinned to SHAs resolved from their v4/v5 tags. It installs the declared
Python 3.13.12 test environment, requires Node 20+, runs Ruff/format/strict mypy
for the new test module, and runs all published assessment suites, the Week 7
hybrid lab and Week 1 service regressions. It runs on assessment/main pushes
and main-targeted pull requests, with cancellation and a ten-minute timeout.

The reviewed candidate is uploaded to the assessment branch first. Its exact
commit must pass remote pytest CI before main is updated. Local checks are not
substituted for remote CI. Pages build/deployment and live browser scoring are
then checked against that same candidate. Branch tests provide this promotion
gate; the workflow does not claim to configure repository branch protection or
prevent administrators from bypassing the process.

## Preserved integration

The static engine is unchanged: two of each format, ten distinct questions,
seed/version reproduction and shuffled order. Ten marks each; complete
single/short/multiple keys, 2.5 per matching pair and two per coding check.
Saved attempts, blank printing, share links, locked answers, explanations,
reference solutions and downloaded results remain available.

The existing pinned Pyodide 0.29.3 worker, 45-second loading deadline,
five-second execution deadline, Stop and pending-mark retry behavior are reused.
Google Colab remains an optional copy/paste workspace, with sign-in and manual
result transfer explained. Opening it sends no answer. No backend or central
learner store is introduced.

All original main/beginner lesson characters are retained after removing the
single new assessment-link paragraph. Earlier banks, labs, shared engine,
assessment CSS, dependencies and Jekyll configuration remain unchanged.

## Executed local validation

Environment: Python 3.12.14, Node 24.19.0 and Chromium 153.0.8010.0.
Browser references use the existing worker's Python 3.13.2.

- 477 targeted pytest tests pass, including 63 new assessment tests, all
  46 existing hybrid lab tests, all earlier assessment suites and service
  regressions. The selected command is the same one used by candidate CI.
- All twenty references pass five checks each; every unimplemented starter
  scores zero and every plausible incorrect implementation loses marks.
- Composed cases verify the independent 0.871385 BM25 example, unique query
  terms, authorized statistics unchanged by a denied exact-code record, no
  zero-padding votes, the known RRF winner and own-source evidence labels.
- The JavaScript validator passes 1,000 balanced reproducible papers,
  reachability of all questions, objective keys, partial/pending scores,
  restored attempts and stale-code rejection.
- All twenty references pass actual browser workers. A full paper scores
  100/100, restores after reload, locks submitted source and downloads JSON.
- Runtime blocking leaves 80/80 graded plus 20 pending; retries recover through
  90/90 to 100/100. Stop, timeout, source preservation and replacement all pass.
- Blank print contains ten questions without keys. Seven dashboard assessment
  links, active navigation and new-paper reproduction pass.
- All seven assessment pages pass 390px light/dark overflow checks, along
  with a mobile sweep of all 100 Week 7 prompts. Screenshots are inspected.
- Completed browser runs have no page errors or unexpected failed requests.
- Ruff lint/format, strict mypy, JavaScript syntax, workflow structural and
  whitespace checks pass. AST inspection finds only the stated standard-library
  imports and no authored file reads, input, eval/exec or dynamic imports.
- Source comparisons verify full lesson preservation and unchanged prior
  banks, labs, runtime/scoring code and CSS.

This is a targeted suite, not an unrestricted whole-repository pass. The known
unrelated Windows-only comparison module is outside it. Actual model and
external-service integration tests are not claimed. Local preview uses the
existing layout with QA Markdown/Liquid rendering, not local Ruby/Jekyll.
The QA runtime relay uses original HTTPS assets, TLS verification and normal
browser security; deployed URLs are unchanged. Workers run without
cross-origin isolation or SharedArrayBuffer.

## Sources and remaining limits

Primary references checked on 2026-10-24:

- [Lucene 9.12.3 positive BM25 IDF and parameter roles](https://lucene.apache.org/core/9_12_3/core/org/apache/lucene/search/similarities/BM25Similarity.html)
- [Cormack, Clarke and Buettcher: original RRF paper](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)

Lab constants and source/measurement semantics are grounded in inspected
repository code. The fake dense scorer and visible practice labels cannot
establish a production winner, real model quality, serving latency, index
memory or generated-answer correctness. A score never authorizes procurement
writes or payment.

Keys and editable client scores are public practice records, not authenticated
exam results. Five checks are bounded feedback, not proof for every possible
solution. Worker termination limits time, not memory; loading depends on
browser/network support. Rollback is a normal feature revert. Future bank
edits must increment its version; attempts remain week/version/seed scoped.
