---
week: 11
status: reviewed
version: 1.0.0
last_reviewed: 2026-10-25
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested Week 11 questions within the established approved build-check-push-publish workflow
---

# Week 11 assessment review

## Baseline and scope

Base main: `db7d12b7cc710ccb96ae5ad766b6185fe318c344`; tree
`85406c02edad0b8a8db70ca68fc966947025a929`. Only root AGENTS.md applies.
There is no Design directory for this curriculum. Accepted scope comes from
Path.md Week 11, both approved lessons, the local security lab and the user's
established weekly 100-question/random-10 assessment requirement. Existing QA
work is preserved. No subagents were used.

Inspected the previous bank/page/tests/review, shared scorer, paper verifier,
Python runner/worker, Week 11 policy and assistant, both lessons, navigation,
README, dependency pins and CI. The applicable coding/review workflow retains
the exact-candidate CI gate and post-Pages live verification. This is a bounded
assessment addition, not a security architecture change or a new deployment
service.

Changes are the new bank/page/test/review, README/navigation, the new test's
existing lint/type gates and lesson assessment links. The two lesson versions
advance to 1.0.1; the deferred-assessment sentences are replaced. Every other
lesson body character is checked against the base. Earlier banks, labs, source
data, dependencies, shared scoring, workers and styles are unchanged.

## Coverage and question contracts

The bank contains 100 distinct authored prompts: 30 single-choice, 20
multiple-correct, 15 matching, 15 short syntax and 20 Python exercises. Every
item has a topic, difficulty, answer key and explanatory feedback. Each coding
task states its own complete input/output/failure contract and five public
checks. Random selection does not require answers or imports from another item.

| Learning goal | Evidence in the bank |
| --- | --- |
| Trust and identity | Direct/indirect entry points, content versus authority, shape versus authentication, strict question-only requests |
| Access-controlled retrieval | Tenant/document/version identity, current principal grant/state, deny by default, filtering before scanning/statistics/ranking |
| Source integrity | Independently protected source and full representation pins, metadata edits, self-declared hashes, approved false facts |
| Screening | NFKC/case folding/whitespace, preserved original text, declared misses/false positives and narrow email/canary scope |
| Resource bounds | UTF-8 bytes versus characters, duplicate/nonfinite JSON, quoted/escaped depth counting, complete serialized context accounting |
| Response validation | Closed envelope/row keys, 1–3 unique selected labels, exact quote text, action-shaped unknown fields and no implied truth/completeness |
| Permission lifecycle | All supplied context, including omitted quotes, full scoped source keys, current recheck and limits on retroactive/distributed revocation |
| Consumers and diagnostics | HTML text escaping, authorized source resolution, fixed internal categories/counts, no routine payload/denied-ID projection |
| Failure and derived state | One synchronous callback attempt, original errors/cancellation, no-evidence skip, copy independence and hypothetical cache scope |
| Evaluation limits | Scripted control evidence, benign/malicious case sets, no claimed real-model attack resistance, complete DLP or authenticated exam records |

Small functions have explicit boundaries. strict_question is a flat schema
exercise; pre-decode structural depth is a separate lexical helper whose raw
input is assumed syntactically valid. selected_quotes receives already-decoded
data; strict JSON, byte bounds, content screening, source authorization and
rendering remain separate. permits receives an independently computed actual
representation digest and trusted normalized policy/context, never a digest
assertion accepted from document prose. representation_pin covers the complete
JSON-compatible record, not just text, and does not establish baseline truth.

simple_findings implements exactly two published patterns as a teaching subset,
including their deliberate false positive and miss. It is not the full lab
scanner or a comprehensive privacy/security classifier. The context-budget
exercise states its canonical compact JSON serialization and prefix rule; it
does not replace the Week 8 packer's interface. security_event validates an
explicit internal projection with exact integer counts and controlled reasons;
bounded fields do not independently authenticate their producer or authorize a
public audience.

cache_scope is expressly hypothetical and only one component of a cache key.
It includes tenant, principal, permission version, complete source keys and
configuration identity; task/generation identity and read-time access checks
remain required for a real cache. catalogue_snapshot tests deep-copy semantics,
not protected storage, concurrent atomicity or lasting access grants. Callback
implementations are trusted code; returned proposals remain untrusted data.

## Technical review and executed checks

Reviewed the complete bounded diff for incorrect keys, ambiguous matching,
source-scope collapse, mutable aliasing, normalization/escaping errors, quote
membership/exactness, byte versus character accounting, hidden callback retries
and unsupported security claims. No unresolved actionable finding is supported
after the executed checks. This is a technical item review, not independent
human psychometric calibration or a fabricated owner rubric score.

Executed locally with Python 3.12.14, Node 24.22.1 and the repository's pinned
pytest/Ruff/mypy:

- **1,024 targeted pytest tests pass**, including 64 new assessment cases, all
  eleven assessment suites, the Week 7–11 lab gates and Week 1 service regressions.
- All 20 Python references pass all five public checks; every starter scores
  zero, and each of 20 distinct plausible incorrect solutions loses marks.
- Composed checks cover denied distractors never reaching scanner/ranker,
  metadata pin mismatch and current grant revocation, detector miss versus an
  independently closed output contract, omitted-context source checks, complete
  budget accounting, HTML text, safe event projection and copy/scope independence.
- JavaScript verification passes 1,000 balanced reproducible papers, all-item
  reachability, objective answer keys, exact/partial/pending scoring, saved
  attempts and stale code/result rejection.
- Reference/starter/check compilation and standard-library import/size bounds
  pass. Ruff check/format and strict mypy pass on 17 scoped Python files.
- JavaScript syntax, whitespace and exact lesson-body preservation checks pass.

The selected suite excludes the pre-existing Windows-only comparison module;
this is not an unrestricted whole-repository pass. Five public checks provide
bounded practice feedback, not proof of arbitrary submission correctness.

The existing read-only CI includes the new bank through its assessment glob;
only the new module is added to its lint/type target list. Candidate CI on the
declared Python 3.13.12 environment must pass before main promotion. Local HTTP
checks and subsequent Pages/live bank-byte, navigation, scoring and restoration
evidence are retained with immutable commit/run identities in publication QA.
No remote/browser success is asserted in advance in this record.

## Sources and release limitations

Conceptual scope follows the published Week 11 lessons and executable local
lab contracts. Primary references rechecked on 2026-10-25:

- [OWASP RAG security](https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html)
- [Python JSON](https://docs.python.org/3.13/library/json.html)
- [Python Unicode normalization](https://docs.python.org/3.13/library/unicodedata.html)
- [Python HTML escaping](https://docs.python.org/3.13/library/html.html)

The static paper keeps ten distinct questions, two per format and 100 marks.
Multiple-correct requires the full set; matching awards 2.5 per correct pair;
coding awards two per passed check. Public keys and editable client results are
practice records. Runtime failure leaves coding marks pending for retry; the
existing pinned worker retains its loading/execution deadlines and Stop. Worker
termination is not a memory cap or a secure arbitrary-code service. Optional
Colab is manual copy/paste, requires sign-in and has no automatic score sync.

There is no new paid dependency, provider call, real sensitive fixture, action
dispatcher, authentication endpoint, cache/history store or model robustness
benchmark. No browser security setting or hosting architecture changes. Bank
revisions need a version bump to avoid stale restored attempts. Rollback is a
normal feature revert and Pages rebuild, with no data migration.
