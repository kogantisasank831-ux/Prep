---
week: 5
status: approved
version: 1.0.0
last_reviewed: 2026-10-24
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested Week 5 within the established explicitly approved build-check-push-publish workflow
---

# Week 5 assessment review

## Scope and inspected baseline

Baseline main commit: f3283450ff21100db2d1c293b11671431e4e7063, tree
d1a6a65a4bd6c08d579cb72e042015bc59300693. Work uses week05-assessment
from a fresh origin/main fetch. The remote head was checked again before
publication. Root AGENTS.md is the sole applicable instruction file. No
Design directory exists. No subagents were used.

Inspected the relevant main/beginner lesson sections and headings, the retrieval
implementation, metric/data helpers, corpus/query practice contracts and lab
README, prior assessment conventions, shared runner/worker interfaces,
navigation, requirements and Jekyll configuration. This adds the missing
assessment to the existing lesson without rewriting its learning content or lab.

The bank contains 100 authored items: 30 single-choice, 20 multiple-correct,
15 matching, 15 short syntax and 20 written Python functions. IDs and prompts
are unique. Every question has a topic, difficulty and explanation. Choice
keys were reviewed against the lesson/lab contracts; no independent human
item validation or psychometric calibration is claimed.

## Coverage and contracts

| Lesson requirement | Assessment evidence |
| --- | --- |
| Vector geometry | Dot, cosine, stable normalization, Euclidean versus squared distance, sign/magnitude and unit-vector identities |
| Numerical boundaries | Finite exact numeric types excluding bool, zero directions, dimensions, overflow/underflow and immutable inputs |
| Embedding compatibility | Artifact/runtime/preparation identity, task-specific encoding, count/dimension checks and observable drift |
| Bounded sources | Character/byte/token distinctions, strict scoped IDs, complete initial chunks and exact text digests |
| Access control | Full principal/tenant/document/version grants, authorized candidates before scoring, empty/count policies |
| Provenance | Ordered model fingerprint, canonical corpus digest, logical recipe versus persisted artifact bytes |
| Ranking evaluation | Requested-k precision, gold-set recall, first-hit RR, binary nDCG, explicit undefined populations |
| Evaluation design | Direct support, missing evidence, negative queries, grouped splits, frozen holdout and label versioning |
| Operational tradeoffs | Packed coordinate arithmetic, exact O(ND) comparisons, ANN neighbor agreement versus human relevance, latency boundaries and sensitive logs |

Each coding task declares its signature, input domain, validation/error policy,
output and mutation behavior. Five public checks per task cover ordinary cases,
relevant boundaries and invalid inputs. Some helpers explicitly assume valid
row/identity shapes; these assumptions are stated rather than presented as
complete input parsers. All reference imports are standard-library math,
hashlib or re. No model weights, Sentence Transformers installation, network
inference, API key or GPU is needed to score these tasks.

The smaller helpers preserve the relevant lab semantics while using plain
lists/dicts and ValueError rather than its complete typed exception hierarchy.
Vector conversion rejects integers outside finite float range. Batch validation
normalizes vectors but cannot prove adapter identity. Source validation creates
one chunk and does not establish cross-record uniqueness. The corpus digest
task assumes valid digest shapes but rejects repeated chunk IDs. Fingerprints
follow explicit UTF-8/unit-separator recipes, independent of dict/input order.

The access exercises consume synthetic grants supplied by the caller; they do
not authenticate a browser user or add server-side access control to this
public page. The exact-search capstone receives an already-authorized set and
has no embedding model, relevance threshold or abstention policy. Separate
callback tests prove unreadable objects are not scored before selection.

Precision divides by requested k even when fewer results are returned.
Recall/RR/nDCG return None for no-gold queries and zero for defined queries
without a hit. Duplicate IDs anywhere in a ranking are rejected before slicing.
The MRR helper reports both defined and undefined counts and includes observed
zeros. ANN neighbor overlap requires full k on both sides and measures set
agreement, not positional accuracy or human relevance.

Independent expected values include the 3-4-5 norm, 153,600,000 packed bytes,
negative/orthogonal cosine, position-sensitive binary nDCG constants and the
P-103/P-101/P-102/P-104 ranking. Composed checks verify unit-vector geometry,
authorization before callback evaluation, no-gold versus zero-hit behavior,
stable tie ordering and input preservation.

## Integration and preserved behavior

The shared static assessment engine is reused unchanged. Papers draw two of
each format, ten distinct questions, with seed/version reproducibility and
shuffled order. Each question has ten marks: exact single/short keys, full-set
multiple-correct, 2.5 per matching pair and two per passed coding check.
Saved attempts, blank printing, share links, locked submission, explanations,
reference solutions and downloaded JSON remain available.

The existing pinned Pyodide 0.29.3 worker loads on demand, with a 45-second
loading deadline, five-second execution deadline and Stop termination. Failed
runtime loading leaves coding marks pending for retry against locked submitted
source. Google Colab remains an optional copy/paste workspace; opening it does
not transfer an answer or synchronize a result.

Changes are confined to the Week 5 page/bank/tests/review, shell.js enablement,
README and one link paragraph in each Week 5 lesson. Removing those added
paragraphs reproduces each complete original lesson exactly, including front
matter and examples. Earlier banks, shared engine, labs, dependencies, Jekyll
configuration and CI remain unchanged.

## Validation executed

Environment: Python 3.12.14, Node 24.19.0, Chromium 153.0.8010.0. Actual browser
references use the existing worker's Python 3.13.2 runtime.

- 362 targeted pytest tests pass: all assessment suites through Week 5, the
  existing Week 5 retrieval lab and Week 1 service regressions. The new suite
  has 63 tests: every reference/starter/incorrect-solution contract, composed
  retrieval checks, bank content and shared paper/scoring validation.
- All twenty references pass five checks each. Unimplemented starters receive
  zero and all twenty plausible incorrect implementations lose marks.
- The JavaScript validator passes 1,000 balanced reproducible papers, all items
  reachable, no bank mutation, objective keys, partial/pending marks, stale-code
  rejection and restored attempts.
- All twenty references pass through actual browser module workers. A complete
  paper scores 100/100, restores after reload and downloads correct result JSON;
  submitted answers remain locked.
- A blocked runtime yields 80/80 graded plus 20 pending, then retries recover
  through 90/90 to 100/100. Stop and the infinite-loop deadline preserve source
  and keep the page responsive before a correct replacement passes.
- Blank print has ten questions without keys. Mobile 390px light/dark layouts
  have no horizontal overflow. Screenshots inspected. New-paper reproduction,
  active Week 5 navigation and five dashboard assessment links pass.
- No page errors or unexpected failed requests in the completed local run.
- Ruff lint/format, strict mypy, JavaScript syntax and whitespace checks pass.
  AST review confirms only the stated standard-library imports and no authored
  file reads, input prompts, eval/exec or dynamic imports.
- Source comparisons confirm complete lesson preservation and unchanged lab,
  engine and prior banks.

Local preview uses the existing layout with QA Markdown/Liquid/YAML rendering,
not a local Ruby/Jekyll build. The browser CDN relay fetches original HTTPS
runtime assets with TLS verification and normal browser security. No deployed
URLs change. Tests run without cross-origin isolation or SharedArrayBuffer.
Hosted Pages deployment and live paper scoring are verified after publication.

## Recovery on 2026-10-24

The initial upload stalled before the branch update. Main still pointed to the
Week 4 baseline. Workspace maintenance then removed the unpublished local
checkout. The repository was re-cloned and the assessment recovered from the
conversation draft, including all 100 questions and 100 coding checks. The bank
retains its original 130,394-byte size. Native validation and the complete local
browser suite passed again after recovery. Hosted checks follow publication.

## Sources, limitations and rollback

Primary references checked on 2026-10-23:

- [Faiss metric types, squared L2 and normalized cosine](https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances)
- [Sentence Transformers semantic search and task-specific encoding](https://www.sbert.net/examples/sentence_transformer/applications/semantic-search/README.html)

The bank evaluates deterministic contracts on synthetic inputs. It does not
measure learned-model accuracy, production access enforcement, ANN performance
or answer factuality. The published four-document practice collection is not an
independent held-out benchmark. A high cosine score does not authorize payment
or any procurement-system write.

Keys and local scores are public/editable practice results, not authenticated
exam records. Five checks provide bounded feedback rather than proof for every
implementation. Worker termination bounds time, not memory; runtime loading
depends on browser/network support. No learner identity, central score upload,
paid service or backend is introduced.

Rollback is a normal feature revert. Future bank edits must increment its
version; attempts remain separated by week/version/seed.
