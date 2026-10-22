---
week: 7
phase: 2
status: approved
version: 1.1.0
last_reviewed: 2026-10-22
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested Week 7 following the explicitly approved weekly creation-and-push workflow
---

# Week 7 content and hybrid retrieval lab review

## Scope and provenance

Repository `kogantisasank831-ux/Prep`, baseline main commit
`494e9bcf1d57dffc191e65a9836c919cacb03d60`, tree
`9b87e81f850b8556e4200ac362330bdc923ad24a`.
Local work used `week07-content` from freshly fetched `origin/main`. The only
applicable instruction file is the root `AGENTS.md`; no `Design/` directory
exists. Existing untracked Week 4–6 QA material was preserved.

Inspected `Path.md` Week 7, README and content workflow, both existing lessons
and all displayed Python, existing layout/navigation, declared quality tools,
and Week 5/6 source, embedding, metric, and provenance interfaces. The user's
request continues the authorized one-week generation, checking, and publication
workflow. Candidates were rendered/executed before canonical replacement.
No separate human review, rubric score, or independent benchmark is claimed.

## Curriculum and retained material

| Path.md requirement | Coverage |
| --- | --- |
| BM25 / keyword retrieval | Identifier-preserving ASCII terms, TF saturation, positive IDF variant, length normalization, hand calculation |
| Dense versus sparse | Code/entity/number risks versus paraphrase help; explicit teaching fake and optional actual local adapter |
| Hybrid retrieval | Shared authorized corpus, candidate-depth union, deterministic final ranking |
| Score normalization | Min–max arithmetic, flat/extreme/nonfinite cases, distribution/calibration limitations |
| RRF | Rank arithmetic, equal/default weights, constant/depth distinction, raw contributor provenance, duplicate/conflict validation |
| Metadata filtering | Allowlisted supplier/type equality predicates after object grants; request/corpus scope compatibility |
| Build | Executed sparse/dense/hybrid comparison on the same eligible snapshot for each query |
| Required query types | Exact CW-1000/PP-20, suppliers, commercial terms, semantic paraphrases; extra alias/OCR/abbreviation/denied cases |
| Interview | Original three answers, eight recall questions/answers, five main exercises, five beginner exercises and readiness checklist retained |

Added prerequisites, outcomes, an eight-hour route, more natural questions,
worked BM25/RRF examples, runnable commands, measured practice results, evidence
inspection, and a weekly handoff. Compressed repetitive alias paragraphs while
retaining owner/evidence/effective-range/scope/version, query-versus-document
expansion, original-token preservation, diagnostics, evaluation, and UI-policy
implications. Original substantive topics, examples, questions, and source URLs
remain. No unrelated weeks or UI/configuration were changed; Week 7 was already
in `PUBLISHED_WEEKS`.

## Continuity correction

The old Week 7 draft reused P-106 for a catalogue, conflicting with Week 6's
quarantined OCR invoice. Catalogue examples now use P-107. The actual lab adds
P-108 for the PP-20 Beacon code note, leaving accepted P-101–105 text, versions,
structure-chunk IDs, and locations unchanged. P-106 remains `needs_review` and
excluded. Beginner alias exercise 1 now uses P-109 to avoid a new ID collision;
its question and learning objective are otherwise preserved.

The shortened standalone lesson passages are explicitly an independent teaching
snapshot, not replacements for Week 6 immutable records. The actual lab imports
Week 6 parsed fixtures and chunk contracts. Supplier/type labels are explicit
curated synthetic metadata, with their policy recorded separately from parser
provenance; no automated entity-extraction accuracy is claimed.

## Implementation and technical corrections

- New lab modules: `retrieval.py` for core contracts, `fixtures.py` for source
  continuity/data, `compare.py` for evaluation/CLI and optional local cosine
  bridge. JSONL practice labels, executed JSON summary, README, and pytest cases
  make the build independently runnable without a new dependency.
- BM25 rejects invalid/bool/nonfinite parameters, keeps read-only statistics,
  deduplicates query terms explicitly, checks scored snapshot membership, and
  avoids overflow in the term-frequency ratio for a very large finite k1.
  Its algorithm/version and full-precision parameters enter the fingerprint.
- Source and request input limits are explicit. Metadata predicates are unique,
  allowlisted exact equalities; a reused corpus must match principal and filters.
  Authorization precedes private corpus statistics and candidate scoring.
- Zero-score padding is removed. Sparse scores must exceed zero; dense scores
  must exceed the floor in its configuration. Empty lists cannot manufacture
  fusion support. A real cosine score floor is experimental selection behavior,
  not calibrated relevance or a general abstention detector.
- RRF validates integer ranks/constants, finite scores/weights, unique contiguous
  ranks per retriever, duplicate contributions, and conflicting source identity;
  it retains raw contributors and breaks ties by chunk ID.
- Min–max handles all-equal scores explicitly and extreme signed ranges without
  subtraction overflow. Invalid/nonfinite scores fail before ranking.
- Corpus fingerprints include actual text and metadata, not only supplied source
  hashes. Manifest schema becomes `procurement-hybrid-retrieval/1.1.0`; no durable
  index or existing API is migrated. Hashes require trusted manifests and are not
  signatures. Dense identity/floor/dimension and observable adapter drift are checked.
- Reported metrics reuse Week 5: P@k uses requested k; no-gold recall/rank/nDCG
  stay null. Binary nDCG is valid without invented graded labels. Legacy compact
  recall/rank helpers assume an already-selected top-k list and are not used
  to calculate the lab's reported metrics.
- The optional bridge uses separate query/document APIs, existing reviewed-local
  model/token/role-prefix checks, vector shape and numeric invariants. Pairwise
  recomputation is a reference, not an optimized vector index or latency result.

## Executed comparison and measurement limits

Seven accepted synthetic documents yield eleven structure-aware chunks. Fourteen
queries are visible `practice` cases: ten labelled, four no-gold. Practice keys
resolve to unique source/version/body-block chunks within each eligible snapshot;
missing keys or atoms absent from their declared text fail. Current keys assume
one tenant per document/version in this fixture; a production label store needs
fully scoped keys and active-version semantics.

Standalone modes return up to three accepted candidates. Hybrid takes up to five
per path and fuses to three, with equal weights and rank constant 60. This larger
union is configured extra work. A denied exact-code distractor is present at the
boundary but absent from both scored sets. Each query's eligible-corpus
fingerprint is equal across all three modes; source/query/configuration identity
is recorded in full output and the checked-in summary.

Default mean Recall@3: sparse 0.966667, teaching dense 0.466667, RRF 0.966667.
Default MRR@3: 0.883333, 0.333333, 0.900000 respectively. The fake dense scorer
has no identifier feature, so its code misses reflect its construction. All
modes find only two of Q09's three evidence units, omitting the payment clause.
Support fractions are 0.9, 0.4, and 0.9. All four no-gold queries return empty in
this narrow default configuration. These values are visible fixture arithmetic,
not held-out quality, a production winner, or real embedding-model accuracy.

Quality means use labelled queries only; no-gold counts are separate. Support
checks required substrings within specifically labelled chunks/versions; it is
not entailment or an answer grade. Same-source repeat fraction can represent
complementary clauses and is not semantic-duplicate waste. No latency, actual
postings/vector/index memory, generated answers, or real-model effectiveness was
measured. No model was downloaded/loaded and no actual PDF/OCR was run.

## Validation executed

Environment: Linux, Python 3.12.14, pytest 9.1.1, Ruff 0.15.22, mypy 2.3.0.
Root dependencies, workflow/infrastructure, and other-week source are unchanged.

| Check | Result |
| --- | --- |
| Default full/summary CLI | All three modes execute; sample reproduced; all per-query corpus fingerprints match |
| Candidate-depth 3 and 8 CLI | Both execute with top-k held at 3 |
| New Week 7 pytest | 46 passed |
| `python -m pytest tests --ignore=tests/test_llm_comparison.py -q -rs --basetemp=.runtime/pytest-week07-final` | 237 passed, 1 skipped |
| `python -m ruff check document_service llm_comparison labs tests` | Passed |
| `python -m ruff format --check document_service llm_comparison labs tests` | 41 files formatted |
| `python -m mypy --strict --explicit-package-bases labs/week_07 tests/test_week07_hybrid.py` | Passed; five Python files |
| Main displayed code | All four original displayed tests execute with corrected contracts/catalogue ID |
| Beginner displayed code | All functions/fixtures/assertions execute; exact-code counts are sparse 1, dense 0, RRF 1 |
| Markdown/Liquid structure with existing layout | Main/beginner: 16/15 code blocks, 4/2 tables; no duplicate IDs or unresolved templates |
| Preservation | Original URLs, interview/recall/main exercises, beginner exercises with documented ID change, readiness checklist, front matter, syntax/fences/links checked |

Full `pytest tests` was attempted and remains blocked at collection by the
pre-existing Windows-only `msvcrt` import in `llm_comparison/storage.py`. Full
strict typing of `document_service llm_comparison labs` reports four pre-existing
`msvcrt` locking/constant attribute errors there. Its source and tests are
unchanged. The compatible-suite command explicitly excludes that test module;
this is not an unrestricted full-suite pass. The skipped runtime integration
test requires `LLM_COMPARISON_INTEGRATION=1`; no runtime was started.

Local rendering uses Python Markdown/Liquid, not Ruby/Jekyll or visual browser
QA. The hosted Pages build/deployment is checked after pushing. QA intermediates
and the local environment are not published.

## Primary sources and remaining scope

Opened Stanford IR-book BM25, Lucene BM25Similarity positive IDF/parameter docs,
Elastic similarity settings, the original Cormack/Clarke/Buettcher RRF paper,
and the original Python dataclass/typing/Counter documentation. Public lessons
link primary references. No search-engine bit-for-bit score equivalence or
universal RRF improvement is claimed.

Authorization invariance tests cover this small partition-local statistics
contract; they do not prove constant-time behavior, general side-channel
resistance, scalable ACL-aware search, or a public-global-statistics design.
Real model integration still requires the reviewed materialized artifact, exact
model-card prefixes, optional dependency/offline setup, and actual evaluation.
Reranking, query rewriting, semantic duplicate control, and context construction
remain Week 8 work, rather than unreviewed scope added here.
