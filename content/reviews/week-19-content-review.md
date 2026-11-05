# Week 19 content and lab review

## Scope and disposition

Roadmap source: `Path.md`, Week 19 — Agent safety and guardrails.

Candidate artifacts:

- `content/weeks/week-19.md`
- `content/weeks/week-19-beginner.md`
- `labs/week_19/`
- `tests/test_week19_agent_safety.py`

Version 1.0.0 is approved for candidate validation. It adds two lesson depths and
a deterministic local safety gateway in front of synthetic procurement tools. It
does not publish a Week 19 assessment; `ASSESSMENT_WEEKS` remains at Week 18 and
neither lesson links to a nonexistent questionnaire.

## Coverage mapping

| Roadmap requirement | Learner-facing treatment | Executable evidence |
| --- | --- | --- |
| Least-privilege tools | functionality, permission and autonomy minimized separately | five-entry closed registry; unknown tool denial |
| Read versus write | separate tool modes and permission strings | read, write and reversal permission checks |
| Approval gates | one exact human grant per consequential call | absence, unknown, mismatch and replay tests |
| Allowlisted operations | no generic shell, URL, SQL, code or path tool | fixed direct dispatcher and exact argument schemas |
| Maximum-step limits | trusted 1–20 budget outside prompt text | third-call stop with configured limit two |
| Sandboxed execution | explicit capability surface and OS-isolation caveat | in-memory dispatcher with no I/O capability |
| Secret isolation | prevent model/log exposure and declare reversal capability | recursive secret-key rejection and no-value audit checks |
| Audit trails | complete lifecycle metadata with secret minimization | deterministic sequence and SHA-256 predecessor verification |
| Reversible actions | receipt, separate permission/approval and conflict safety | restore, tenant, reuse and stale-undo tests |
| Human approval before writes | permission does not imply approval | flag remains unchanged without exact grant |
| Tool permission checks | trusted scope is separate from agent request | missing permission and cross-tenant tests |
| Full audit logging | request through final decision, without payload hoarding | seven event types and controlled codes |
| Safe failure responses | policy blocks separated from tool failure | stable statuses/codes; raw internal text suppressed |

## Technical review

The Week 18 candidate remains the conceptual agent. Week 19 adds an execution
boundary rather than changing its model, prompt, specialist logic or evaluation.
`TrustedScope` carries tenant, principal, run, case and permissions from host
code. `ToolRequest` cannot supply any of those authority fields.

The registry maps five literal tools to one permission, mode and exact argument
set. Three reads are tenant scoped. `review_flag_set` and
`review_flag_revert` are writes, always need approval and have separate
permissions. Unknown tools, extra/missing/coerced values and invalid flag states
fail before dispatch.

Approval grants bind tenant, principal, run, case, request ID, tool and canonical
argument digest. Valid grants are consumed before dispatch. This prevents replay
after success or ambiguous failure; retries and backoff remain Week 20 scope.

The step counter lives in the gateway, not agent state. The closed local sandbox
uses direct branches over synthetic dictionaries and exposes no generic I/O. The
lessons explicitly distinguish this capability sandbox from hostile-code process
or container isolation.

Audit events retain trusted correlation, tool, controlled code, argument digest,
valid reviewer identity, sequence and hash links. They exclude raw arguments,
secret values and arbitrary exceptions. Chain verification detects edits and
reordering in supplied events, but not valid-prefix truncation, deletion, origin
forgery or storage compromise; the lessons do not call it immutable.

A write receipt includes before/after state and an opaque undo capability. A
reversal needs separate authority and a fresh grant, stays in the original
tenant, is one-use and compares current state with the original post-write value.
That conflict check prevents stale compensation from overwriting newer work.

## Source review

Primary and first-party technical material accessed on 2026-11-05:

- OWASP LLM06:2025 Excessive Agency for minimizing extension functionality,
  permission and autonomy, human approval and complete downstream mediation;
- OWASP AI Agent Security Cheat Sheet for least privilege, structured validation,
  human oversight, execution isolation, limits and safe metadata;
- OWASP Logging Cheat Sheet for event selection, sensitive-data exclusion, log
  access protection and tamper detection;
- NIST's least-privilege glossary entry for minimum required resources and
  authorization;
- OpenAI Agents SDK human-in-the-loop documentation for per-call approvals,
  interruption/resume and sticky-approval scope cautions; and
- OpenAI Agents SDK tool documentation for the explicit warning that tool
  approval does not itself provide executor isolation.

## Executed local checks

Local environment: Python 3.12.14. The declared CI environment is Python 3.13.12.

- All 29 focused Week 19 contract, behavior, failure, reversal and CLI tests pass.
- Ruff lint passes for all 76 files in the configured CI scope, and Ruff format
  reports all 76 files already formatted.
- Strict mypy passes for all 76 configured files with a clean isolated cache.
- The configured regression suite passes 1,738 tests, including every published
  assessment bank and the focused Week 19 gateway suite.
- Week 13 actual-SQLite smoke passes all 12 observations.
- Week 14 controller smoke passes all eight observations.
- Week 15 graph smoke passes all ten observations.
- Week 16 memory/context smoke passes all 12 observations.
- Week 17 supervisor/specialist smoke passes all ten observations.
- Week 18 evaluation smoke passes eight baseline assertions over all 28 cases.
- Week 19 safety-gateway smoke passes 12 assertions over all seven scenarios.
- Front matter, reciprocal lesson links, code-fence balance, YAML parsing,
  JavaScript syntax, UTF-8 reads, whitespace, CI wiring, Week 19 lesson
  navigation and absence of a premature Week 19 assessment link pass locally.

Candidate CI, main promotion and live Pages verification must pass before the
publication section is completed.

## Publication verification

Publication verification completed on 2026-11-05 for implementation commit
`54e53ea92da6eb9f7d0581745a579aa1403c848c`:

- Candidate CI run `42079948716` passed the Python 3.13.12 lint, format, strict
  typing, 1,738-test regression and seven CLI smoke gates, followed by the real
  PostgreSQL/pgvector permission, revocation and named-volume restart job.
- Main CI run `42080444613` passed both required jobs after lease-protected
  fast-forward promotion.
- GitHub Pages run `42080443965` built and deployed successfully.
- The production route rendered “Put enforceable guardrails between agents and
  tools,” and the beginner route rendered “Give an agent a small keyring, a
  supervisor and an undo plan.” Their reciprocal depth links resolved in both
  directions.
- Live navigation exposed Week 19 as a lesson, left Week 20 as a roadmap item
  and exposed zero Week 19 assessment links. The roadmap's Week 19 card contained
  one lesson link and no questionnaire link, matching the content-only scope.
- The production, beginner and roadmap routes logged no page-origin warning or
  error during final browser verification.

GitHub Pages hosts only the static lessons. The approval ledger, gateway,
sandbox, audit chain, synthetic procurement records and CLI run locally; no
public Python service, model, provider, database, secret or procurement action
was deployed.
