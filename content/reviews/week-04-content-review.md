---
week: 4
phase: 1
status: approved
version: 1.1.0
last_reviewed: 2026-10-21
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested creation and push to git in this conversation
---

# Week 4 content and lab review

## Scope and inspected sources

Baseline: `0dd909c87444bd2ae22c305793a61ce4e7eb0f3d` in
`kogantisasank831-ux/Prep`, branch `main`. The initial working tree was clean.
Root `AGENTS.md` is the only applicable instruction file. No `Design/` directory
exists. Reviewed `Path.md`, `plan.md`, README content workflow, the weekly
template, Week 3's structure/review, both existing Week 4 lessons, site layout and
configuration, publication navigation, and configured Python dependencies.

The user explicitly requested direct creation and publication of Week 4. That
request authorizes this content pass and its push; no independent human rubric
scores or separate learner review are claimed. Editorial and technical review
were performed in this pass. Drafts were validated before replacing canonical
lesson files.

## Curriculum coverage

| Path.md requirement | Lesson/lab coverage |
| --- | --- |
| System, user, tool messages | Message roles, templates, source trust, and no implicit tool authority |
| Zero-shot, few-shot, role prompting | Baseline, optional example bundle, limits, held-out comparison |
| Structured output | Prose/JSON/constrained-decoding distinctions and runtime compatibility limits |
| JSON Schema validation | Pydantic contract, extra/missing/null rules, custom-validator limitations |
| Prompt versioning | Initial/repair versions, request fingerprints, configuration provenance |
| Retry strategies | Per-call records, transport/repair separation, independent caps, four-call default maximum |
| Prompt sensitivity | Fixed settings, split cases, field support versus schema metrics, unmeasured model quality |
| Procurement extraction build | Supplier, product, quantity, unit, price, currency, delivery date, payment terms, application-owned status |
| Interview preparation | Original six interview answers and ten recall questions/answers retained; new exercises and notebook answer |

## Changes and content preservation

- Revised both introductions and transitions in plain language; removed repetitive
  "Orienting question"/"Bridge" labels while retaining their teaching content.
- Added prerequisites, measurable outcomes, an eight-hour route, guided build,
  six independent exercises, mini-project deliverables, and definition of done.
- Retained every original lesson section, original source URL, interview answer,
  recall item/answer, and beginner readiness item. Existing concepts and examples
  remain; technical corrections below intentionally change affected snippets.
- Corrected duplicate-label overwrite, decimal comparison by display string,
  decimal-string wire enforcement, whitespace-only names, strict ISO candidate
  dates, and status ordering so absent dates cannot conceal another mismatch.
- Corrected beginner prompts that accidentally asked the model to set status.
- Added a complete offline Python lab, twelve synthetic cases (six development,
  six holdout), a lab README, and 63 tests. No dependencies or other weeks changed.
- Kept existing public permalinks and version-switch links. Week 4 was already
  in `PUBLISHED_WEEKS`; navigation did not need modification.

## Verification executed

Environment: Linux, Python 3.12.14, repository-pinned Pydantic 2.13.4, pytest 9.1.1,
Ruff 0.15.22, mypy 2.3.0. No live model or GPU inference was performed.

| Check | Observed result |
| --- | --- |
| `python -m labs.week_04.extractor` | Scripted demo returns valid, expected typed fields, one attempt |
| `python -m pytest tests --ignore=tests/test_llm_comparison.py -q -rs` | 89 passed, 1 skipped; includes all 63 new Week 4 tests |
| `python -m ruff check document_service llm_comparison labs/week_04 tests` | Passed |
| `python -m ruff format --check document_service llm_comparison labs/week_04 tests` | 25 files already formatted |
| `python -m mypy --strict --explicit-package-bases labs/week_04/extractor.py tests/test_week04_extractor.py` | Passed for both changed Python files |
| Lesson snippet execution | Seven original example tests passed, plus numeric-equivalence and duplicate-label regression checks |
| Markdown/Liquid preview | Both pages rendered with existing layout; 26/16 code blocks and 6/3 tables; no duplicate IDs or unresolved Liquid; asset links checked |
| Content checks | Front matter, stable permalinks, original URLs, retained interview/recall/readiness text, JSON examples, Python syntax, and fence balance checked |

`python -m pytest -q` was also attempted. Collection is blocked by the existing
unconditional Windows-only `msvcrt` import in `llm_comparison/storage.py`.
The complete typing command over existing packages/tests similarly reports four
existing Linux-platform `msvcrt.locking`/constant errors in that file. These are
outside Week 4 and were not suppressed or changed. The skipped test is the
pre-existing live-model smoke test, which requires
`LLM_COMPARISON_INTEGRATION=1` and a configured local runtime.

The local renderer is a structural Python Markdown/Liquid preview, not an exact
Jekyll or visual-browser pass. Hosted GitHub Pages build/deployment is verified
after pushing. No real-model extraction accuracy, prompt-quality comparison,
throughput, or privacy-control implementation is claimed.

## Technical sources and remaining boundaries

Primary Pydantic models/strict-mode/JSON-Schema docs, Python JSON/decimal/datetime
docs, JSON Schema object/reference docs, and Hugging Face chat-template docs were
opened during verification. Public lessons link these sources directly.

The lab accepts a deliberately narrow labelled, USD-only source grammar with
`kg`/`ea` units; only the delivery date may be null, and null requires review.
Its parser already extracts such controlled documents deterministically. The
LLM boundary teaches proposal validation rather than justifying an unnecessary
production model call. Free-form contracts need a separately evaluated evidence
policy. Rejecting unknown lines is not general prompt-injection detection.

Attempt records are in memory. Production retention/access controls, durable
storage, live adapters, runtime artifact/generation provenance, backoff/deadlines,
and provider-specific schema support remain explicitly outside this offline lab.
No procurement-system writes, payment decisions, hosted requests, or automatic
configuration promotion were added. Real-model measurements remain unmeasured.
