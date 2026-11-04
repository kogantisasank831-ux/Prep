---
week: 17
status: reviewed
version: 1.0.0
last_reviewed: 2026-11-04
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested completion and publication of the Week 17 questionnaire within the established test-push-publish workflow
---

# Week 17 assessment review

## Baseline and scope

The published implementation baseline is main commit
`bf23b255bf49d7f74a89659de38aabee0ad8e05f`. Local source commit
`91b6047b6c079a29a12e2b7df22c3bdb285e336d` has the same reviewed tree. Only
the root `AGENTS.md` applies. Its Finance App references do not describe this
curriculum, and there is no `Design/` directory. `Path.md` Week 17, the approved
production and beginner lessons, `labs/week_17/LOGIC.md`, the concurrent local
lab and the established weekly assessment contract define this addition. No
subagents were used.

Inspected the Week 16 bank, page, tests and review; the shared assessment engine,
Python runner and browser worker; Week 17 contracts, models, fixtures,
specialists, supervisor, sequential baseline, CLI and tests; navigation, layout,
README, dependency pins and CI workflow. The assessment adds no dependency,
provider, model, hosted execution service, database, network call or external
action.

Added `assessments/week-17.json`, `assessments/week-17.html`,
`tests/test_week17_assessment.py` and this review. The same change exposes the
assessment in navigation and CI, links it twice from both lesson depths, updates
the lesson patch version to 1.0.1 and records the assessment contract as W17-AS1
in `labs/week_17/LOGIC.md` revision 2.

## Coverage

The bank contains 100 distinct authored prompts: 30 single-choice, 20
multiple-correct, 15 matching, 15 short syntax and 20 Python coding questions.
Every item has a topic, foundation/applied difficulty, answer key and explanatory
feedback. Each coding task is independent, states its accepted input and failure
behavior and has five executable checks.

| Learning goal | Assessment evidence |
| --- | --- |
| Pattern selection | Distinct context, governance, ownership and independent work versus shared-context function-sized steps |
| Specialist boundaries | Document, SQL, supplier-risk and commercial responsibilities with truthful source ownership |
| Minimal handoffs | Closed role-specific assignment projections that exclude prompts, dialogue and unrelated source bodies |
| State ownership | Frozen values, stateless specialists, supervisor-only aggregation and deep-independent projections |
| Dependency planning | One three-role bounded first wave followed only by validated commercial synthesis |
| Determinism | Declared result collection, exact successful trace, explicit policy precedence and repeated-output expectations |
| Validation | Result class/role/run/case correlation, supplier correlation, source kind, digest and identifier checks |
| Failure propagation | Technical failures produce `failed` with no report; valid missing terms produce `needs_human` |
| Commercial policy | Missing terms first, supplier risk second, strictly above-threshold variance third and `no_review` otherwise |
| Exact arithmetic | Positive `Decimal` prices, two-place `ROUND_HALF_EVEN` variance and no binary-float decision path |
| Approval and provenance | Three compact evidence references, mandatory human approval and no procurement action capability |
| Architecture comparison | Equal controlled reports, four versus zero handoffs, two versus four stages and null measured latency |
| Production limits | Closed registry plus a bounded illustrative retry policy; remote identity, durability and tracing remain deployment work |

## Coding contracts and limits

The browser exercises use only `copy`, `decimal` and `re` from the standard
library. They need no Pydantic or LangGraph package, thread pool, repository
import, provider, model, server, network, database or credentials. Actual
concurrent admission and the complete supervisor and sequential routes remain
covered by the local Week 17 lab.

Inputs use exact built-in containers and primitive types where the contract says
strict. Closed shapes reject undeclared conversation, prompt, source-body,
latency and action fields. Assignment/result exercises return independent data;
identity checks reject wrong role, run and case correlations before aggregation.
Stage planning permits only the declared four roles, while batching permits only
the three source roles and a worker bound from one through three.

Commercial policy uses exact `Decimal` values and checks equality at the
threshold as `no_review`. Reports always set `requires_human_approval=true` and
stop at `awaiting_approval`. Failure exercises either return a controlled domain
code or an unexpected exception class; arbitrary exception text is rejected.
Digest exercises require lowercase SHA-256 shapes but explicitly teach that byte
agreement is not factual truth, authentication, authorization or approval.

The retry-candidate exercise models one control a remote production adapter
would need; it is not a claim that the local supervisor retries. It allows only
bounded service-unavailable/timeout cases and never retries identity, type or
digest defects. The architecture exercise reports only observed outcome equality,
handoffs and dependency stages and leaves measured latency null.

## Executed local verification

Used Python 3.12.14, Node 24.22.1 and the repository's pinned tools in an isolated
temporary environment.

- The focused Week 17 assessment module passes 64 cases. All 20 references pass
  five checks; all 20 starters score zero; every one of 20 distinct plausible
  wrong implementations loses marks.
- The shared JavaScript verifier validates the 100-item bank, exercises 1,000
  balanced reproducible papers, reaches every item and checks objective,
  partial/pending, stale-code and restoration contracts.
- Five composed checks cover minimal correlated handoffs, bounded stable
  scheduling, exact evidence and approval, sanitized reportless failure, and
  evidence-bounded architecture selection/comparison.
- The assessment plus concurrent Week 17 lab pass 89 tests.
- The configured regression suite passes 1,625 tests, including all seventeen
  assessment banks, the Week 7–17 labs and the Week 1 service regressions.
- Ruff lint and formatting pass for all 64 configured files. Strict mypy passes
  the same 64 files.
- The Week 13 actual-SQLite smoke passes 12 observations with zero external
  actions. The Week 14 controller smoke passes eight checks, the Week 15 graph
  smoke passes ten, the Week 16 durable-memory smoke passes 12 and the Week 17
  coordination smoke passes ten.
- Static checks confirm 100 unique ordered IDs, two lesson links at each depth,
  the Week 17 page-to-bank path, navigation allowlist and explicit CI scope.

This is a public practice bank. A seeded paper draws two questions of each type
for 100 marks. Multiple-correct requires the complete set; matching awards 2.5
per pair; coding awards two points per passed check. Public keys and editable
browser results are not authenticated exam records. Runtime unavailability
leaves coding marks pending. Save/restore, print, result download and scoring
behavior use the unchanged shared engine.

## Publication verification

Publication verification completed on 2026-11-04 for implementation commit
`4a84f318226ccd4054f04c7b6d46792bbbdba00f`:

- Candidate CI run `41833565507` passed the Python 3.13.12 lint, format, strict
  typing, 1,625-test regression and five CLI smoke gates, followed by the real
  PostgreSQL/pgvector permission, revocation and named-volume restart job.
- Main CI run `41833945262` passed both jobs after fast-forward promotion.
- GitHub Pages run `41833945754` built and deployed successfully.
- The production and beginner lessons each expose two Week 17 assessment links
  and retain their reciprocal depth navigation.
- The live assessment loaded bank version 1.0.0 with the status “100 questions
  ready,” created a 10-question paper with exactly two questions of every type,
  exposed two Python-run controls, ten question-navigation links and one scoring
  submission control, and linked back to the Week 17 lesson.
- The production, beginner and assessment routes logged no page-origin warning
  or error during the final browser verification.

GitHub Pages hosts the static assessment and downloads the pinned browser Python
runtime only when a learner runs a coding solution. The concurrent multi-agent
lab remains local; no public Python service, model, provider or database was
deployed.
