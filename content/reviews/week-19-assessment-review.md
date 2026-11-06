---
week: 19
status: reviewed
version: 1.0.0
last_reviewed: 2026-11-06
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested completion and publication of the Week 19 questionnaire within the established test-push-publish workflow
---

# Week 19 assessment review

## Baseline and scope

The published implementation baseline is main commit
`2d3aa23e5b4c1d277a3b8278024a5322b1b4070a`. Local source commit `24e8c35`
has the equivalent reviewed Week 19 content tree. Only the root `AGENTS.md`
applies. Its Finance App references do not describe this curriculum, and there
is no `Design/` directory. `Path.md` Week 19, the approved production and
beginner lessons, `labs/week_19/LOGIC.md`, the deterministic gateway and the
established weekly assessment contract define this addition. No subagents were
used.

Inspected the Week 18 bank, page, tests and review; the shared assessment engine,
Python runner and browser worker; Week 19 trusted models, closed registry,
approval ledger, audit chain, in-memory sandbox, gateway, scenarios and focused
tests; navigation, layout, README, dependency pins and CI workflow. The
assessment adds no dependency, provider, model, hosted execution service,
database, network call, secret or external procurement action.

Added `assessments/week-19.json`, `assessments/week-19.html`,
`tests/test_week19_assessment.py` and this review. The same change exposes the
assessment in navigation and CI, links it twice from both lesson depths, updates
the lesson patch version to 1.0.1 and records the assessment contract as W19-AS1
in `labs/week_19/LOGIC.md` revision 2.

## Coverage

The bank contains 100 distinct authored prompts: 30 single-choice, 20
multiple-correct, 15 matching, 15 short syntax and 20 Python coding questions.
Every item has a topic, foundation/applied difficulty, answer key and explanatory
feedback. Each coding task is independent, states accepted input and failure
behavior and has five executable checks.

| Learning goal | Assessment evidence |
| --- | --- |
| Trust boundary | Agent proposal is untrusted; tenant, principal, permissions, run and case come from trusted application scope |
| Capability minimization | Fixed server-owned tool registry with no dynamic shell, URL, code, path or SQL route |
| Least privilege | Exact independent read, write and reversal permissions with no implication between them |
| Closed validation | Exact tool argument names, strict built-in values, recursive secret-key checks and tenant-scoped lookup |
| Human approval | Independent ledger grant bound to tenant, principal, run, case, request, tool and canonical argument digest |
| Replay resistance | Complete match, one-time consumption and consumption before tool dispatch |
| Bounded autonomy | Hard 1–20 step budget checked before the over-budget operation runs |
| Isolation | Honest distinction between a fixed local capability boundary and hostile-code process isolation |
| Audit evidence | Secret-minimized projection, canonical digest, linked event construction and full supplied-chain verification |
| Audit limits | Hash links detect supplied-sequence mutation and reorder but do not prove origin, durability or absence of truncation |
| Controlled failure | Closed completed/blocked/failed status-code pairs and arbitrary exception sanitization |
| Recovery | Tenant-scoped deterministic receipt, separate reversal authority, unused token and post-write state conflict check |
| Concept boundaries | Permission versus approval, approval versus isolation, idempotency versus grant replay, and compensation versus true undo |
| Production limits | Authentication, downstream authorization, transactional state, protected audit storage, isolation, egress and operations remain required |

## Coding contracts and limits

The browser exercises are self-contained and use only `hashlib` and `json` from
the Python standard library. They need no Pydantic package, repository import,
provider, model, server, network, database, filesystem or credentials. The
complete frozen boundary models, approval store, audit stream, sandbox and
gateway remain in the local Week 19 lab.

Inputs use exact built-in containers and primitive types where the question says
strict. Closed shapes reject undeclared fields, blank identities, duplicate
permissions, malformed hashes and bool-as-int coercion. Tenant lookup never
falls back across tenants. Approval matching covers every declared binding;
consumption mutates only trusted ledger state. Step boundaries are inclusive.
Canonical JSON uses sorted keys and compact separators. Audit projections omit
raw arguments and arbitrary exception text. Reversal hides cross-tenant receipt
existence, rejects replay and refuses to overwrite state that no longer matches
the original post-write value.

The recursive secret-key exercise is an instructional declared-key policy, not a
general data-loss-prevention system. The argument digest provides an equality
reference, not encryption or authorization. A valid supplied audit prefix can
still be incomplete. The local flag receipt cannot make an external message,
payment or disclosure reversible. These limitations are tested or stated rather
than hidden behind a broad safety claim.

## Executed local verification

Used Python 3.12.14, Node 24.22.1 and the repository's pinned tools in an
isolated temporary environment.

- The focused Week 19 assessment module passes 64 cases. All 20 references pass
  five checks; all 20 starters score zero; every one of 20 distinct plausible
  wrong implementations loses marks.
- The shared JavaScript verifier validates the 100-item bank, exercises 1,000
  balanced reproducible papers, reaches every item and checks objective,
  partial/pending, stale-code and restoration contracts.
- Five composed checks cover closed policy mediation, exact one-use approval and
  step limits, secret-minimized linked audit evidence, tenant-scoped reversible
  writes and controlled failure/lifecycle semantics.
- The assessment plus guarded Week 19 gateway pass 93 tests; the gateway smoke
  passes 12 checks over seven scenarios.
- The configured regression suite passes 1,802 tests, including all nineteen
  assessment banks, the Week 7–19 labs and the Week 1 service regressions.
- Ruff lint and formatting pass for all 77 configured files. Strict mypy passes
  the same 77 files with an isolated cache.
- The Week 13 actual-SQLite smoke passes 12 observations with zero external
  actions. Week 14 passes eight checks, Week 15 ten, Week 16 twelve, Week 17 ten,
  Week 18 eight assertions over all 28 cases and Week 19 twelve checks over all
  seven safety scenarios.
- Static checks confirm 100 unique ordered IDs, exactly five checks per coding
  task, two lesson links at each depth, the page-to-bank path, front matter,
  fence balance, UTF-8 reads, navigation allowlist, JavaScript syntax, CI wiring
  and clean whitespace.

This is a public practice bank. A seeded paper draws two questions of each type
for 100 marks. Multiple-correct requires the complete set; matching awards 2.5
per pair; coding awards two points per passed check. Public keys and editable
browser results are not authenticated exam records. Runtime unavailability
leaves coding marks pending. Save/restore, print, result download and scoring
behavior use the unchanged shared engine.

## Publication verification

Publication verification completed on 2026-11-06 for implementation commit
`a0767d1887f015edf4d41992e29c6d4565ccdfae`:

- Candidate CI run `42208018065` passed the Python 3.13.12 lint, format, strict
  typing, 1,802-test regression and seven CLI smoke gates, followed by the real
  PostgreSQL/pgvector permission, revocation and named-volume restart job.
- Main CI run `42208355148` passed both jobs after lease-protected fast-forward
  promotion of the exact candidate commit.
- GitHub Pages run `42208354243` built and deployed successfully.
- The production and beginner lessons each expose two Week 19 assessment links
  and retain their reciprocal depth navigation. The roadmap exposes the Week 19
  lesson and assessment actions.
- The live assessment loaded bank version 1.0.0 with the status “100 questions
  ready,” created a 10-question paper with exactly two questions of every type,
  exposed two Python-run controls, ten question-navigation links and one scoring
  submission control, and linked back to the Week 19 lesson.
- The production, beginner, roadmap and assessment routes logged no page-origin
  warning or error during the final browser verification.

GitHub Pages hosts the static assessment and downloads the pinned browser Python
runtime only when a learner runs a coding solution. The complete guarded gateway
remains local; no public Python service, model, provider, database, credential or
procurement action was deployed.
