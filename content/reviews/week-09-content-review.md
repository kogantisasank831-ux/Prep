---
week: 9
phase: 3
status: approved
version: 1.0.0
last_reviewed: 2026-10-22
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested Week 9 within the established explicitly approved create-check-push-publish workflow
---

# Week 9 review: RAG evaluation fundamentals

## Scope, baseline and authorization

Repository `kogantisasank831-ux/Prep`, main baseline
`5365a1e823ab6799321dfc987bdfbc6eb97a138a`, tree
`3e23c838000c6ad0323a5f36dbd9909f455cabbe` (published Week 8).
Work used `week09-content` from a fresh `origin/main` fetch. The sole applicable
instruction file is root `AGENTS.md`. No `Design/` directory exists in this
curriculum repository. Existing untracked Week 4–8 QA directories were preserved.

The user requested “week 9 do,” continuing the authorized direct generation,
verification, push and Pages workflow. `Path.md` Week 9 and `plan.md` determine
the teaching scope. Candidate lessons were written under `.qa-week09`, executed
and structurally rendered before canonical integration. No independent human
rubric score or annotation campaign is invented. Publication authorization is
distinct from the thirty pending semantic evaluation reviews.

Inspected the full root instructions and content workflow, Week 9/10 curriculum,
existing Week 8 main/beginner content and source contracts, Week 5 ranking
metrics, Week 6 parser/chunk/source representations, Week 7 authorization and
source fixtures, Week 8 ingestion/assistant/comparison, layout/navigation,
requirements and configured pytest/Ruff/mypy conventions.

## Requirement mapping

| Path.md requirement | Coverage |
| --- | --- |
| Parsing quality | Independent fixture status/fact oracle and parser representation audit; OCR uncertainty retained |
| Chunking quality | Declared accepted facts retained at expected body locations; stable granularity and boundary limits |
| Retrieval quality | Candidate ceiling, requested-k precision, recall, MRR and binary nDCG on scoped evidence units |
| Context relevance | Valid selected-unit precision, expected-citation recall, source-specific support completeness and paired context ablations |
| Answer faithfulness | Claim/evidence distinction and rubric; measured extractive traceability named narrowly, semantic score left null |
| Answer correctness | Explicit reference normalization, lexical proxy counterexamples, expected availability behavior and pending semantic review |
| Citation correctness | Exact authorized stored-span validity separated from expected evidence recall and claim-level support |
| Exact match | Versioned S-label/case/whitespace normalization preserving numbers, codes, punctuation and negation |
| Semantic similarity | Embedding/token-representation concepts, calibration and numeric/negation failure cases; unmeasured rather than fabricated |
| LLM-as-judge | Rubric, evidence boundaries, bias/calibration design, untrusted output validation, model/prompt provenance; no actual judge call |
| Human evaluation | Anchored four-axis rubric, independent review/adjudication guidance, exact-run pending/completed review contract |
| Approximately 30 questions | Exactly 30 authored visible synthetic cases, 22 answerable and 8 unanswerable |
| Expected answers/documents/citations | Reference alternatives, required answer atoms and fully scoped source/version/body-location labels |
| Run and store results | CLI plus executed sample summary, all thirty raw case records and pending review template |
| Interview | Four main explanations, ten main/eight beginner recall answers, seven/six exercises and readiness/handoff |

Both lessons use a missing catalogue delivery date as an orienting example, then
introduce metrics one concept at a time before assembling the evaluator. Each
has four complete runnable Python blocks, an eight-hour route, failure cases,
checkpoints, practical commands and sources. Internal provenance remains here.

## Dataset and source continuity

Week 8 input bytes and all earlier implementation remain unchanged. P-101–105,
P-106 review-only OCR, P-107/108 catalogues and the private distractor retain
their identities. The offline source auditor can inspect the synthetic complete
collection; analyst requests retain the existing seven-document/eleven-chunk
grant boundary. No new public endpoint, persistence or generator was added.

`cases.jsonl` covers identifier, supplier, commercial, paraphrase, cross-reference,
filter, date, numeric, condition, multi-source, unavailable-fact, mismatched
filter, review-only, denied-access and unmapped-alias categories. The questions
are visible practice and partially extend earlier patterns, not held-out data.
Their labels were authored for this artifact; no separate human annotation is
claimed.

`source_checks.jsonl` declares nine expected statuses and independent text atoms
at input body locations. Expected source citations include tenant, document,
version, location and atoms. Labels are validated against raw source/oracle facts,
expected accepted status, principal grants and exact metadata predicates.
Required answer atoms must also occur in their declared evidence atoms. This is
a lexical consistency check, not semantic validation of reference prose.

Absent current predicted chunks do not delete gold labels or stop loss
measurement. Source checks can expose a missing chunk while parser preservation
remains intact. Incorrect source facts fail as annotation errors instead of being
misrepresented as parser regressions.

Dataset schema/version and SHA-256 fingerprints bind source snapshot, questions
and source checks. The reader enforces bounded UTF-8 JSONL, exact fields, unique
IDs, nonfinite/duplicate-key rejection and consistent answerability. A revised
practice copy needs intentional version/fingerprint updates. This runner supports
the local corpus/practice contract; no hidden-test workflow is implied.

## Implementation decisions

- Six new modules separate dataset validation, source audit, explicit metric
  helpers, review validation and CLI/run persistence. The teaching path uses the
  standard library and existing labs, with no new dependency or CI/config pin.
- Retrieval labels use fully scoped source units, not document-only hits or
  unscoped evidence aliases. Candidate/hybrid/reranked membership, source scope
  and requested k are retained for diagnostics.
- Ranking metrics reuse Week 5. Precision divides by requested k; no-gold
  recall/rank/nDCG stay null outside answerable means. A separate graded toy
  helper states its grade/gain contract explicitly; the actual run stays binary.
- Context support uses valid exact selected spans at their expected source
  locations. Context precision's valid-span denominator is documented; invalid
  spans are counted separately rather than hidden as semantic success.
- Exact match strips display S labels, case-folds and collapses whitespace only.
  Product codes, numbers, punctuation, units and negation remain. A test explicitly
  shows lexical atom coverage passing a negative statement, so it cannot be
  mistaken for semantic correctness.
- Exact citation validity and extractive answer traceability are deterministic.
  General semantic similarity, faithfulness, answer correctness and citation
  support remain null/not reviewed. Pending reviews never enter a quality mean.
- Failure labels identify candidate/ranking/context losses, missing answer atoms,
  expected availability behavior, invalid citations and extractive mismatch.
  The labels are pipeline diagnostics, not a universal causal proof.
- Results store actual answer, spans/offsets/locations, expected references,
  scopes, ranking keys, context digest/length, metrics and provenance. Run IDs
  bind dataset/system/runtime/normalization/source-bundle identity; each case
  record then gets a digest. Paths/time do not change a deterministic run ID.
- The writer creates a fresh directory and refuses to overwrite prior evidence.
  The default run saves summary, thirty records and pending templates. The same
  executed artifacts are checked into the lab for durable review.
- Optional human/LLM review imports validate exact run/record/rubric, all axes,
  integer ranges, rationale and reviewer/model/prompt identities. Reviewer/prompt
  groups use unambiguous identifiers so slashes in model names cannot merge
  distinct groups. Identities/digests are self-declared metadata, not signatures
  or proof of independent review. No rating is generated automatically.

## Executed findings

Source status matches: 9/9. Declared parsed-atom recall: 1.0. Accepted chunk-unit
recall: 12/12. These describe controlled parsed-layout fixtures only, not
arbitrary PDF/OCR accuracy or commercially verified source values.

Across 22 answerable cases, candidate Recall@6 is 1.0. Baseline/treatment share
source snapshot, scope, candidate membership, labels and k=3.

| Answerable mean | Hybrid | Teaching reranker |
| --- | ---: | ---: |
| Precision@3 | 0.378788 | 0.393939 |
| Recall@3 | 0.984848 | 1.000000 |
| MRR@3 | 0.954545 | 0.977273 |
| Binary nDCG@3 | 0.961893 | 0.983224 |

Default labelled-context completeness, expected-citation recall and lexical
answer-atom coverage are 1.0. Valid selected-unit context precision is 0.689394.
No emitted citation is invalid; extractive traceability is 1.0 among answered
cases. These are narrow automated observations, not semantic ratings.

Normalized exact match is 9/30 overall and 4/22 among answerable cases. Expected
unanswerable abstention is 5/8. W09Q23 (catalogue delivery date), W09Q24 (agreement
5 percent discount) and W09Q25 (supplier phone number) receive authentic excerpts
instead of expected abstention. The evaluator preserves these three failures;
it does not claim the assistant fabricated the missing facts or silently repair
the existing response policy.

Sentence compression retains complete support on 20/22 cases and gives mean
answer-atom coverage 0.977273, exact match 7/30. A 300-character whole-chunk budget
retains support on 18/22, coverage 0.924242 and exact match 10/30. Retrieval metrics
remain unchanged. The tight budget improves exact match while losing evidence:
an explicit counterexample to choosing a release from a final-answer score alone.
Expected abstention stays 5/8 in both ablations.

No semantic similarity model, generator, actual LLM judge or human annotation
review was run. Thirty semantic reviews remain pending in the published sample.
No learned-model, held-out, latency, memory, claim-entailment or real extraction
quality measurement is invented.

## Validation executed

Environment: Linux, Python 3.12.14, pytest 9.1.1, Ruff 0.15.22, mypy 2.3.0.

| Check | Observed result |
| --- | --- |
| New Week 9 tests | 46 passed |
| Linux-compatible suite excluding the existing Windows-only comparison test module | 340 passed, 1 skipped |
| Global Ruff lint | Passed |
| Global Ruff format check | 55 files formatted |
| Strict mypy for Week 9 plus its tests | Passed, seven files |
| Default, sentence and 300-character CLI runs | Executed and persisted; expected paired metrics agree |
| Run reproducibility / output protection | Repeated identical results; existing output directory preserved |
| Dataset/gold/review failure cases | Invalid input, stale identities, private gold, lost units, invalid citations and fabricated ratings rejected or measured as specified |
| Main/beginner Python examples | All eight full blocks executed |
| Markdown/Liquid structural previews | Main: 20 sections, 10 code blocks, 6 tables; beginner: 20 sections, 8 code blocks, 2 tables |
| Layout/metadata | One H1, no duplicate IDs/unresolved templates, bounded/fenced code, valid internal assets and alternate lesson links |
| Main JSON example | Parsed successfully |

The unrestricted full pytest command was also attempted and remains blocked at
collection by pre-existing Windows-only `msvcrt` in `llm_comparison/storage.py`.
Full strict mypy over `document_service llm_comparison labs` reports the same
four pre-existing `msvcrt` locking/constant attributes in that file (43 source
files checked). Its source/tests are unchanged. The compatible suite explicitly
excludes that module; this is not an unrestricted full-suite pass. The one
skipped local-server integration test requires `LLM_COMPARISON_INTEGRATION=1`.

Local previews use Python Markdown/Liquid, not local Ruby/Jekyll or visual
browser QA. The hosted Pages workflow and public main/beginner URLs are verified
after pushing. Only the existing publication set gains Week 9; intermediate QA
artifacts and environments are not committed.

## Primary evidence and limits

Opened the BERTScore, Ragas, ARES and MT-Bench judge papers. Retrieved the NIST
trec_eval first-relevant reciprocal-rank definition and official scikit-learn
nDCG documentation. The lab uses its own stated cutoff/gain/tie contracts and
existing metric code, not copied third-party implementations or a new dependency.
Stanford IR chapter URLs were located through the authoritative index; direct
HTML/PDF fetches timed out. Formula arithmetic was independently checked by
executed hand examples and tests. Public links distinguish conceptual references
from the lab's exact metric contract.

Remaining work is explicit: broader independently reviewed held-out questions,
source/version authority, actual model and judge calibration, semantic
correctness/faithfulness/citation evaluation and production data handling.
Week 10 tracing remains a later curriculum task rather than hidden scope here.
