---
week: 6
phase: 2
status: approved
version: 1.1.0
last_reviewed: 2026-10-22
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested Week 6 after explicitly approving the weekly creation-and-push workflow
---

# Week 6 content and chunking lab review

## Scope and baseline

Repository `kogantisasank831-ux/Prep`, branch `main`, baseline commit
`3e78ed2812eaaa9e4ab435c62380acbe89f8cf05`, tree
`95ddfc0aa363e9ff0d43136a0a2c4ae8f83037a0`.
Local work used an isolated `week06-content` branch from current `origin/main`.
Existing untracked Week 4/5 QA material was preserved. The root `AGENTS.md` is the
only applicable instruction file; there is no `Design/` directory.

Read the Week 6 scope in `Path.md`, existing main/beginner content and all code,
root instructions, README/content workflow, site configuration and layout,
Week 5 lab/adapter/metrics contracts, and declared quality-tool dependencies.
The objective continues the user's authorized one-week generation, verification,
and publication workflow. No independent human review or rubric score is claimed.
Candidates were rendered and executed before replacing canonical Markdown.

## Coverage and preservation

| Path.md requirement | Lesson and lab coverage |
| --- | --- |
| Fixed-size / overlap | Character windows, half-open precise source spans, final-window stopping, cost arithmetic |
| Sentence boundaries | Whole-sentence grouping, soft width, regex limitations, retained nonparagraph blocks |
| Semantic boundaries | Versioned local similarity interface; explicitly heuristic Jaccard teaching implementation |
| Structure-aware | Heading inheritance and row preservation; parser quality and isolated-heading limitation |
| Parent-child | Children-only matching, stored parents, same-source lineage, repeated authorization and shared context budget |
| Metadata extraction | Heuristic fields versus source facts, parser/layout/metadata fingerprints |
| PDF / tables | Reading order, scanned pages, row/header mapping, OCR ambiguity, status/review route |
| Comparison build | All six policies on the same five accepted parsed documents and nine visible practice queries |
| Required measurements | Document recall, stored/indexed counts, character lengths, text bytes, packed-vector estimate, support proxy; answer quality explicitly unmeasured/null |
| Interview | Original answers, all eight recall questions/answers, all five independent exercises retained |

Both public lessons retain their original topic sequence, substantive examples,
questions, exercise wording, and source URLs. The beginner definition of done is
preserved. Added prerequisites, outcomes, an eight-hour route, more natural
section questions, worked overlap/storage examples, guided commands, actual
practice output, Q04 evidence inspection, and weekly handoff instructions.
Original exercises for OCR review and precise spans remain for independent
practice, with the supplied reference implementation identified explicitly.

## Technical changes

- Parser validates bounded identities, blocks, UTF-8 and locations. Ambiguous
  labelled tables and replacement characters require review; malformed inputs
  reject explicitly. P-106 is simulated parsed OCR, never a claimed real scan.
- Accepted indexing requires `ParseStatus.ACCEPTED` and a matching text digest.
  The narrow fixture table grammar does not prove source accuracy.
- Fixed/overlap chunks cite intersecting block-relative character ranges instead
  of every document block. Overlap stops on reaching the source end, avoiding a
  redundant tail contained in its preceding window. Integer parameters reject
  booleans and invalid bounds.
- Sentence and shared-term policies preserve headings/table rows atomically.
  Semantic thresholds/scores must be finite and within the declared ranges.
  Parent-child also retains isolated headings as children.
- IDs incorporate the representation fingerprint. The manifest separately
  records canonical-text digest, representation fingerprint, and serialized
  chunk checksum, and validates counts/policy/source/lineage. Schema changes
  locally to `procurement-chunks/1.1.0`; no existing durable index is migrated.
  A trusted manifest is required: these hashes are not signatures.
- Parent expansion checks lineage/policy/source identity and authorization again,
  deduplicates parents, and admits only whole context units that fit. It cannot
  silently attach an unrelated section or version.
- Comparison uses the existing Week 5 vector math and optional adapter interface,
  not its short-document index with an incompatible initial-chunking manifest.
  Vector batch shape, finite/nonzero normalization and adapter identity are checked.

## Practice collection and measurements

`labs/week_06/fixtures.py` contains five accepted synthetic documents P-101–105
and one ambiguous P-106 row. Both parser and policies run locally; no PDF parser
or OCR engine was installed or called. `queries.jsonl` contains seven labelled
queries and two no-gold queries, explicitly marked `practice`. It is visible
teaching data, not a development/holdout benchmark or source-quality audit.

The teaching encoder uses Week 5 hand features plus a constant 0.1 coordinate,
with a distinct six-dimensional identity. Jaccard at 0.1 supplies semantic-policy
boundaries independently. Default k is three chunks and context is 800 Python
characters for every policy. Only children are indexed in parent-child mode.
All strategies receive the same corpus representation fingerprint. Source IDs
must be unique across versions/tenants because practice labels are document-only;
production evaluation needs scoped source/version labels and active-version rules.

Executed summary counts: fixed 8 stored/8 indexed; overlap 9/9; sentence 12/12;
structure 9/9; Jaccard 13/13; parent-child 17/9. The checked-in sample report is
reproduced by `python -m labs.week_06.compare --summary` and checked by pytest.

Document recall is computed from distinct relevant documents reached at the
chunk budget. The separate support proxy requires each labelled source's atoms
within that source's admitted context; then averages per-source fractions per
query and across seven labelled queries. No-gold cases get null metrics and do
not count as successful answers. No abstention is implemented. Matching atoms
is not entailment and can miss equivalent wording or split phrases.

Text storage excludes metadata/IDs. Vector storage assumes packed float32 and
excludes index/allocator/Python overhead. Actual tokens, latency, memory, real
model quality, generated answers/human grades, and PDF/OCR accuracy are
unmeasured. Answer quality and token averages stay explicitly null. This is
consistent with recording missing measurements rather than fabricating results;
a complete production answer-quality evaluation remains follow-up work.

## Validation executed

Environment: Linux, Python 3.12.14, pytest 9.1.1, Ruff 0.15.22, mypy 2.3.0.
No new root dependency, UI, workflow, infrastructure, or other-week changes.

| Check | Result |
| --- | --- |
| Default CLI comparison and `--summary` | All six policies run; P-106 excluded consistently; sample regenerated |
| New Week 6 pytest | 45 passed |
| Compatible suite: `python -m pytest tests --ignore=tests/test_llm_comparison.py -q -rs --basetemp=.runtime/pytest-week06-final` | 191 passed, 1 skipped |
| `python -m ruff check document_service llm_comparison labs tests` | Passed |
| `python -m ruff format --check document_service llm_comparison labs tests` | 36 files formatted |
| `python -m mypy --strict --explicit-package-bases labs/week_06 tests/test_week06_chunking.py` | Passed; five Python files |
| Main displayed code | All five original tests executed successfully |
| Beginner displayed code | All four strategies execute; sentence output retains the table row |
| Markdown/Liquid structural render with existing layout | Main/beginner: 14/15 code blocks, 3/4 tables; no duplicate IDs or unresolved templates |
| Preservation checks | Original URLs, interview/recall/exercise text, beginner DoD, valid front matter/permalinks, code syntax/fences, JSON and local asset links |

The full `pytest tests` attempt fails at collection because pre-existing
`llm_comparison/storage.py` imports Windows-only `msvcrt`. Full strict typing of
`document_service llm_comparison labs` reports four pre-existing `msvcrt`
locking/constant attribute errors in that file. It and its tests are unchanged.
The compatible-suite exclusion is explicit, not an unrestricted full-suite pass.
The skipped local runtime integration test requires
`LLM_COMPARISON_INTEGRATION=1`; no real local runtime was started.

Local preview uses Python Markdown/Liquid for structure, not Ruby/Jekyll or
browser visual QA. The hosted Pages build/deployment is verified after the push.
Public sample data is synthetic. QA intermediates are not included in the commit.

## Sources and integration limits

Checked primary pypdf extraction guidance, Python dataclass/typing/hashlib/regex
docs, current Sentence Transformers model API, and the Lost in the Middle paper
for the limited observation that retrieved-context position can affect results.
No universal context-position claim or new model recommendation is made.
Public lessons link primary documentation. The existing Week 5 optional adapter
is reused unchanged; no actual embedding artifact was loaded or benchmarked.

For real-model integration, the operator must supply the reviewed materialized
model and its exact model-card prefixes, follow the adapter's offline and
input-preparation contract, and measure token/quality/runtime behavior. A learned
boundary adapter is a separate experiment. The current work does not certify
arbitrary PDFs, OCR output, model files, production multi-tenant security,
persistent snapshot promotion, or generated-answer correctness.
