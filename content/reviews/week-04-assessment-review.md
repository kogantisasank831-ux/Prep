---
week: 4
status: approved
version: 1.0.0
last_reviewed: 2026-10-23
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested Week 4 within the established explicitly approved build-check-push-publish workflow
---

# Week 4 assessment review

## Scope and inspected baseline

Baseline main commit: 7376c2a1edb3fc2dc75707f18f5561526ac9ed61, tree
521c00e2a4e07ac0bc7e385b79f34998958d61ab. Work uses week04-assessment,
created after a fresh origin/main fetch. Root AGENTS.md is the sole applicable
instruction file. No Design directory exists. Prior untracked QA work remains
untouched; no subagents were used.

Inspected the main/beginner Week 4 contracts, lab implementation and README,
existing content review, current assessment engine/worker and prior bank/test
conventions, requirements and navigation. This adds an assessment to the
published Week 4 lesson, without rewriting the lesson or extraction lab.

The bank has 100 authored items: 30 single-choice, 20 multiple-correct,
15 matching, 15 short syntax and 20 written Python functions. Every ID/prompt is
unique and each item has a topic, difficulty and explanation. No independent
human item validation or psychometric calibration is claimed.

## Coverage and contracts

| Lesson requirement | Assessment evidence |
| --- | --- |
| Prompts and roles | Zero/few-shot distinctions, example versioning, role prompting and untrusted user/tool material |
| Structured output | JSON syntax versus schema versus evidence, required/null/extra rules, constrained-decoding limits |
| Exact fields | Decimal strings, positive quantities, non-negative prices, strict dates, preserved payment conditions |
| Bounded evidence | UTF-8 byte limits, repeated labels/JSON keys, controlled quantity/price grammar and unit compatibility |
| Application status | Candidate cannot self-certify; schema/mismatch/absent-date precedence |
| Recovery | Same-request transport retries, versioned repair, explicit kinds/reasons and finite call caps |
| Provenance | Source serialization, exact request digests and version/configuration changes |
| Evaluation | Separate structural/support metrics, all-case denominators, holdout hygiene, promotion/rollback and no business authorization |

Each written task states its signature, domain, mutation/error policy and
expected result. Five public checks test normal behavior, relevant boundaries
and invalid inputs. All reference imports are standard-library datetime,
decimal, hashlib, json or re. No Pydantic installation, model weights, GPU,
network inference or API key is needed by these functions.

The coding helpers are deliberately smaller than the lab. Decimal grammar,
amount ranges and source grammar do not substitute for Pydantic's complete
precision/scale constraints. The JSON parser exercise uses Decimal for JSON
fractional numbers to retain exact decoding; field-specific validation must
still reject numeric JSON values for amount fields requiring strings. Parsing
an object is not full schema validation or source support.

The labelled mapping exercise recognizes only the documented synthetic labels,
not arbitrary document semantics. The request-digest exercise defines its own
explicit UTF-8 canonical serialization. The recovery simulation has fixed
default caps and a SCRIPT_EXHAUSTED teaching outcome when its finite fake event
sequence ends. This extra simulation state is not added to the unchanged lab's
public reason-code contract.

Independent expected assertions cover known values and failures, rather than
calling reference functions to generate their own answers. Composed checks
include 1,000 * USD 12.00 = USD 12,000, quantity/price unit comparison, a required
present-null date versus omission, mismatch precedence with an absent date,
and transport exhaustion inside a repair round. Differences in display scale
between Decimal('12.0') and Decimal('12.00') must not change amount equality.
Binary-float precision loss and malformed grouping are explicit negative cases.

## Integration and preserved behavior

The existing static assessment engine is reused without code changes. Papers
have two of each format, ten distinct questions, shuffled ordering and
seed/version reproducibility. Ten marks per question: exact single/short keys,
full-set multiple-correct, 2.5 per matching pair and 2 per passed coding check.
The page preserves saved attempts, blank print, share links, locked submission,
explanations/reference solutions and JSON downloads.

The bank selects the existing pinned Pyodide 0.29.3 worker. Runtime download is
on demand. A 45-second loading deadline, five-second execution deadline and
Stop behavior stay unchanged. Runtime unavailability leaves coding marks
pending for retry against the locked submitted source. Colab is the optional
copy/paste workspace; sign-in and lack of automatic answer/result transfer
remain explicit.

Changes are confined to the new Week 4 page/bank/tests/review, its enablement
in shell.js, README and one assessment-link paragraph per Week 4 lesson.
Every original lesson character, front-matter field and fenced example remains
identical after removing those link paragraphs. The lab, prior banks, shared
engine, runtime dependencies, Jekyll configuration and CI remain unchanged.

## Validation executed

Environment: Python 3.12.14, Node 24.19.0, Chromium 153.0.8010.0. Actual browser
references use the existing worker's Python 3.13.2 runtime.

- 305 targeted pytest tests pass: 63 new bank/coding tests, all 63 existing
  Week 4 lab tests, earlier assessment checks and Week 1 service regressions.
- All twenty references pass their five checks (100 cases). All twenty
  unimplemented starters receive zero; all twenty plausible wrong solutions
  lose marks.
- Composed business checks cover exact amounts, nullable presence, comparable
  units, outcome precedence and repair-round transport exhaustion.
- The shared JavaScript validator checks 1,000 balanced reproducible papers,
  every item reachable, no bank mutation, objective keys, matching/code partial
  marks, pending scores, stale-result rejection and restored attempts.
- All twenty references pass in the actual browser module worker. A complete
  paper scores 100/100, reloads its saved state and downloads the expected
  result; submitted answers remain locked.
- A blocked runtime produces 80/80 graded plus 20 pending; retries recover to
  90/90 then 100/100. Stop and an infinite-loop deadline preserve source and
  keep the UI responsive before a successful replacement solution.
- Mobile 390px light/dark layouts have no horizontal overflow; blank print has
  ten questions without keys; new-paper/share reproduction, active Week 4
  navigation and four dashboard assessment links pass. Screenshots inspected.
- No browser page errors or failed requests in the completed local run.
- Ruff lint/format, strict mypy, JavaScript syntax checks and final whitespace/
  diff checks pass. Source-preservation checks confirm both complete lesson
  texts and unchanged lab/engine/earlier banks.
- Reference AST inspection confirms standard-library imports and no authored
  file reads, input prompts, eval/exec or dynamic imports.

Local preview uses the current layout with QA Markdown/Liquid/YAML rendering,
not a local Ruby/Jekyll build. The browser's CDN transport uses a QA relay
fetching original HTTPS assets with TLS verification and normal browser web
security. No deployed worker URLs are changed for this relay. Tests run with
crossOriginIsolated false and no SharedArrayBuffer. Hosted Pages deployment
and live scoring checks follow publication.

## Sources, limitations and rollback

Primary references checked on 2026-10-23:

- [Python JSON decoding](https://docs.python.org/3/library/json.html)
- [Pydantic strict-mode behavior](https://docs.pydantic.dev/latest/concepts/strict_mode/)
- [JSON Schema object/required/extra properties](https://json-schema.org/understanding-json-schema/reference/object)

The assessment evaluates deterministic contracts on synthetic inputs. Neither
a successful paper nor the scripted lab measures real model accuracy, runtime
constrained-decoding support or production audit/retention controls. A valid
extraction does not authorize payments or procurement-system writes.

Keys are public and local scores are editable practice results, not
authenticated exam records. Five checks give bounded feedback rather than
proof for every implementation. Worker termination bounds execution time, not
memory. Runtime loading depends on network/browser support. No learner
identity, central score upload, paid API or additional backend is introduced.

Rollback is a normal feature revert. Future bank edits must increment the bank
version; attempts remain namespaced by week/version/seed.
