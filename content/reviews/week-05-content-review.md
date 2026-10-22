---
week: 5
phase: 2
status: approved
version: 1.1.0
last_reviewed: 2026-10-22
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested the next week after the completed Week 4 creation/push workflow
---

# Week 5 content and retrieval lab review

## Baseline and scope

Baseline `1a5aad45112dec3998969e9fd873816dc187b59f`, tree
`8c2480b6757475296f74c5ffedeb8f4699bc23d3`, in `kogantisasank831-ux/Prep`.
Local work began on a branch based on current `origin/main`, preserving existing
untracked Week 4 QA files. The root `AGENTS.md` is the only applicable instruction
file; the repository has no `Design/` directory. Previously reviewed root
instructions/content workflow remain applicable.

Inspected the Week 5 scope in `Path.md`, both existing Week 5 lessons and all six
Python blocks, adjacent Week 4 conventions, publication configuration/layout,
and configured test/lint/type dependencies. The task continues the user's
authorised one-week creation-and-push workflow. No separate human rubric scores
or independent learner review are claimed. Drafts were checked before copying
to canonical files.

## Curriculum coverage and retained material

| Path.md requirement | Coverage |
| --- | --- |
| Semantic embeddings | Learned representations, limits, token/document embedding distinctions |
| Similarity/cosine | Dot/L2/cosine geometry, normalization, stable vector math, numeric counterexamples |
| Dense retrieval | Compatible query/document encoders, exact retrieval, failure analysis |
| Vector indexing | Immutable in-memory entries, source/version provenance, model/manifest compatibility |
| ANN | Exact baseline, neighbour overlap versus relevance recall, latency/memory/build trade-offs |
| Dimensionality | Compatibility checks and explicit packed-float32 storage calculation |
| Domain-specific embeddings | Task labels, model/runtime/artifact/preprocessing provenance, domain evaluation |
| Build | JSONL loading, initial one-short-document chunking, embeddings, storage, authorised top-k |
| Interview | All original interview answers, ten recall questions/answers, five independent exercises retained |

Original lesson sections, research/documentation URLs, interview/recall text,
independent exercises, and beginner readiness items were retained. Added clearer
introductions/transitions, prerequisites, outcomes, eight-hour route, worked
metrics, runnable lab, twelve practice queries, and weekly handoff/definition of
done. Corrected the beginner payment-direction example: payment is to Cedar,
not owed by the supplier.

Technical corrections deliberately update affected snippets: finite/type checks
reject boolean coordinates; scaled normalization avoids overflow/underflow,
including subnormal inputs; invalid UTF-8 sources and oversized/invalid queries
fail explicitly; positive k is checked consistently; observable embedder identity
changes during build/query are rejected; manifest count/dimension are positive.
Index schema is versioned to `procurement-semantic-index/1.1.0`.

Clarified that logical index IDs identify source/configuration recipes, not
vector-byte checksums or bitwise reproducibility; pre-filtering is not a
constant-time guarantee; exact neighbours are not relevance labels; and teaching
feature vectors are not learned semantic-model quality measurements.

## Lab implementation and sample data

- `labs/week_05/data.py`: bounded strict UTF-8 JSONL parsing and source loading.
- `retrieval.py`: typed source/vector contracts, teaching embedder, exact index,
  manifest/provenance, query validation, and access filtering before scoring.
- `metrics.py`: binary Precision@k, Recall@k, reciprocal rank@k, and nDCG@k.
- `local_model.py`: optional local Sentence Transformers adapter, directory
  fingerprinting, role-specific APIs/prefixes, token preflight, output checks.
- `demo.py`: default teaching run or explicit already-downloaded local model.
- `corpus.jsonl`: the four synthetic source records P-101 through P-104.
- `queries.jsonl`: twelve independently specified practice labels, including
  missing-price/exact-code/negation cases with no supporting source.
- README and optional pinned dependency explain operation and integration limits.

All query rows are marked `practice`, not held-out benchmark data. The original
exercise for a separate governed 30-query evaluation remains. No generated
accuracy or latency figures are reported for a real embedding model.

## Checks executed

Environment: Linux, Python 3.12.14; repository-pinned pytest 9.1.1, Ruff 0.15.22,
mypy 2.3.0. The core lab uses the standard library. The optional model dependency
is isolated in `requirements-local-model.txt`; root dependencies are unchanged.

| Command/check | Result |
| --- | --- |
| `python -m labs.week_05.demo` | P-101/P-104 returned in stable order with tied teaching scores; no model/network call |
| Week 5 pytest cases | 57 passed as part of the final compatible-suite run |
| `python -m pytest tests --ignore=tests/test_llm_comparison.py -q -rs --basetemp=.runtime/pytest-week05-final` | 146 passed, 1 skipped |
| `python -m ruff check document_service llm_comparison labs/week_04 labs/week_05 tests` | Passed |
| `python -m ruff format --check document_service llm_comparison labs/week_04 labs/week_05 tests` | 31 files already formatted |
| `python -m mypy --strict --explicit-package-bases labs/week_05 tests/test_week05_retrieval.py` | Passed, six Python files checked |
| Displayed lesson code | Six original tests and new worked metric example executed successfully |
| Markdown/Liquid structural preview | Main/beginner pages rendered with existing layout; 24/12 code blocks, 2/0 tables; no duplicate IDs or unresolved templates |
| Content preservation | Original URLs, interview/recall/exercise text, readiness items, front matter/permalinks, code syntax/fences, JSON examples, and asset links checked |

The pre-existing `llm_comparison/storage.py` imports Windows-only `msvcrt`, which
blocked full Linux collection in the preceding verified environment. That module
and its tests were not changed or suppressed; its comparison test module remains
excluded in the compatible-suite command. The skipped test is the pre-existing
local-runtime smoke test requiring `LLM_COMPARISON_INTEGRATION=1`.
Do not describe this as an unrestricted full-suite pass. The new Python files
pass strict typing; older Windows-platform typing limitations remain out of scope.

Local rendering used Python Markdown/Liquid for structure, not Ruby/Jekyll or a
visual browser. The hosted Pages build/deployment is verified after pushing.

## Primary-source verification and limits

Opened the original Python typing/dataclass/hashlib docs, Sentence-BERT, Faiss
metric/index guidance, HNSW, BEIR, MTEB, and current Sentence Transformers model
API/release docs. Checked query/document encoding, explicit prompts, local-only
loading, and the official 6.1.0 optional dependency pin. Hugging Face Hub and
Transformers offline docs support `HF_HUB_OFFLINE=1`; legacy offline options are
not prescribed. Public material links primary documentation directly.

No real model artifact was downloaded, loaded, or benchmarked; the optional
dependency was not installed in the base environment. Adapter behavior is tested
with an injected fake backend, including no-download constructor arguments,
prefix/role handling, token limits, directory fingerprinting, and malformed
outputs. A compatible real artifact smoke run and relevance/latency/memory
measurements are separate integration work, explicitly labelled in the lesson.

The optional adapter assumes text-only prefix-plus-text preprocessing matching
the encoder API. Custom chat/multimodal preprocessing needs another adapter.
Artifacts must be reviewed and materialized without symlinks; no flag certifies
arbitrary model files. CPU defaults are not a measured hardware-fit claim.

Storage is immutable in memory. Durable snapshots, checksum/atomic promotion,
production identity/retention controls, scalable ANN, extensive chunking, and
answer generation remain outside this baseline. No other weeks, UI, runtime
infrastructure, production data, or external actions were changed.
