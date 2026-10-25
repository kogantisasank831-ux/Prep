# Week 11 content review — 2026-10-25

## Scope, source and authorization

Base main: `11dc32dabbe34ba28c49b45598eaac063d5bd942`; tree
`d43a169fde64dd260d5e3ca7490f47af89df05fc`. Workspace maintenance removed
the previous checkout; this work uses a fresh clean clone without changing the
surviving earlier QA output directory. Only root AGENTS.md applies. There is no
Design directory; Path.md Week 11 and plan.md govern this curriculum.

The user requested Week 11 content within the established approved weekly
generation/push/publish workflow. Questions remain deferred, as in Week 10's
content-first sequence. Direct Codex generation staged both lesson candidates
in QA before canonical integration. No additional human rubric ratings,
independent review or real-system risk acceptance are invented.

Applied the production-coding, threat-modeling and bounded code-review skill
workflows with their implementation/check references. Inspected the Week 7
source/access contracts, Week 8 ingestion/corpus/assistant/citation components,
Week 10 continuity, dependency pins, shared renderer/navigation and CI. The
primary agent performed design, implementation, review and verification; no
subagents were used.

Scope: main/beginner eight-hour lessons, a local synthetic security lab and
tests, README/navigation and CI inclusion. Earlier labs, data, assessment banks,
shared scoring/worker/style code, dependencies and Jekyll configuration remain
unchanged. PUBLISHED_WEEKS adds 11; ASSESSMENT_WEEKS remains 1–10.

## Accepted teaching contracts

| Requirement | Concrete implementation / lesson evidence |
| --- | --- |
| Direct/indirect injection and malicious documents | Known request/body fixtures, separately identified origins, pre-context screening and documented detector mistakes |
| Data exfiltration | Closed quote-only response schema rejects action/destination fields; no network/email/shell action dispatcher supplied |
| Sensitive-data leakage | Synthetic email/canary rules and payload-free events; no general PII/DLP claim |
| Retrieval poisoning | Protected source + full content/metadata representation pins; tampered exclusion and approved-false-fact residual case |
| Tenant isolation and document access | Trusted caller context and independent tenant/document/version/state/reader catalogue before actual reused retrieval |
| Input/output validation | Strict question-only JSON, duplicate-key/encoding/depth/size bounds; selected unique labels and exact quotes |
| Maximum context | Trusted 2..1400 serialized-character cap; no-context skips responder and refuses |
| Permission changes | All context source grants rechecked after proposal, including omitted quotes; local/non-atomic scope stated |
| Interview objective | Why prompt secrecy/wording cannot enforce authority or contain downstream effects |

The catalogue is separately controlled fixture data. SecurityContext validates
shape and does not authenticate a user. PolicyStore.replace models a trusted
administrator update; source bytes cannot call it. Representation pins include
metadata/source-location assertions as well as text, and malformed permitted
representations deny access. The catalogue helper intentionally creates one
chunk per document version for these fixtures; the policy record itself permits
multiple bindings.

The responder implementation is trusted Python code; its returned JSON is
untrusted. The library is not a Python sandbox or network firewall. The output
contract is intentionally quote-only and does not validate arbitrary generated
claims, factual source truth or completeness. Source labels are local span
labels, not permanent authorized document-viewer URLs. No real provider, HTTP
auth/admin service, source upload/PDF parser, cache/history, model classifier or
production renderer is added.

## Scoped threat register and ownership

Qualitative priorities describe the fictional design's consequences, not a
production CVSS score or reported incident. Fixture implementation ownership is
the primary agent for this change. Suggested production review roles below are
unassigned proposals, not accepted organizational responsibilities.

| ID / priority | Actor, boundary and consequence | Executed control evidence | Residual / proposed production reviewer |
| --- | --- | --- | --- |
| S1 / high | Client supplies another tenant/principal; cross-scope reading | Strict body rejection, same-name tenant and reader/version tests | Real identity/storage adapters absent; identity/platform owner |
| S2 / high | Uploader changes approved bytes/metadata; integrity loss | Protected representation pin and self-assertion tests | Baseline approval/storage/signatures trusted; ingestion/data owner |
| S3 / high | Allowed document tries to control later work | Known chunk excluded; detector miss does not enable extra action fields | Other text/media attacks unmeasured; application security owner |
| S4 / high | Responder invents quotes/actions; disclosure/effects | Exact selected quote/label/schema checks, no action sink | Broader generation/tool integration requires new contracts; application owner |
| S5 / medium | Allowed content contains sensitive text | Narrow pre/post rules, no raw payload/denied identifiers in event | Misses/false positives/retention policy unresolved for real data; data owner |
| S6 / high | Trusted permission changes during response | Recheck all supplied context, including omitted spans | Cannot retract earlier reads or claim distributed atomicity; storage/platform owner |
| S7 / medium | Oversized/deep input; resource exhaustion | Byte/depth/text/source/context/output bounds | No service rate limiter/memory isolation/provider deadline; service owner |
| S8 / medium | Approved source asserts a false fact | poisoned-fact intentionally returns permitted false Net 1 quote | Integrity pin does not establish truth; domain/evaluation owner |

Threats are grounded in local code paths and controlled fixtures. No remote
scanning, real payload disclosure, compromised production system or actual LLM
attack-success rate is claimed. New providers, tools, sources, identities,
caches/history or classifications trigger another boundary review.

## Executed local verification

Environment: Python 3.12.14, Node 24.22.1, pinned pytest 9.1.1, Ruff 0.15.22 and
mypy 2.3.0. The clean remote CI environment uses declared Python 3.13.12.

- **960 targeted pytest tests pass**, including **99 Week 11 security cases**,
  all ten assessment suites, Week 7–10 lab gates and Week 1 service regressions.
  No failures/skips. The unrelated Windows-only comparison module is outside
  this selected suite; no unrestricted whole-repository pass is claimed.
- Ruff check/format and strict mypy pass for the existing CI targets plus the
  five new lab sources and security test: sixteen Python files.
- All thirteen CLI scenarios run in fresh directories with expected internal
  reasons. Runtime/cancellation propagation, no retries/fallback, caller-data
  preservation, selected-source revocation and refusal consistency are tested.
- All seven Python fenced lesson examples execute; the JSON example parses.
  Both drafts include coherent prerequisites, eight-hour routes, worked cases,
  checkpoints, exercises with acceptance evidence, interview answers and sources.
- Markdown/Liquid renders main/beginner with 16/13 section headings and 6/5
  tables, bounded code blocks, resolved templates and no assessment-11 link.
  A local HTTP server smoke returns 200 for both rendered lesson URLs.
- QA-only Markdown 3.7, PyYAML 6.0.2 and python-liquid 2.3.6 are installed only
  for preview rendering; project manifests and production dependencies do not
  change. The actual Pages build uses Jekyll and remains a release gate.

Local interactive preview is not claimed: the cloud browser could not reach
the local server, and its URL policy disallows file URLs. No alternate browser
surface or egress workaround is used to bypass that restriction. Local HTML/
HTTP and CLI checks establish the candidate smoke evidence; public live lesson
navigation/rendering must be checked after the authorized Pages deployment.
Existing responsive styles are unchanged; no unsupported device-emulation result
is invented.

## Review findings and release evidence boundary

The final review follows request origin through current catalogue eligibility,
protected representation comparison, actual retrieval/reranking/context,
untrusted response validation, source recheck and safe output/event fields.
Tests use independently constructed negative inputs, real domain functions and
controlled responder ports rather than mocking the controls themselves.

Resolved before release: representation pinning covers metadata as well as text;
source checks happen before findings so denied chunks do not affect blocked
counts; current access is rechecked for the whole supplied context; source truth,
detector misses/false positives, renderer and trusted-adapter limitations are
explicit rather than reported as successful defenses. No outstanding actionable
correctness finding is supported in the declared scope after verification.
This is not an exhaustive security audit, model efficacy study or certification.

The exact candidate must pass remote pytest/lint/type CI before main promotion.
Pages build and live public-page checks follow promotion. Immutable candidate,
tree and workflow identities are retained in publication QA evidence. This
record does not claim those remote gates passed before they execute. Rollback
is a normal feature revert plus Pages rebuild, with no migration or paid service.

## Primary sources checked

Opened on 2026-10-25; public lessons link to the originals. No benchmark numbers,
legal compliance claims or verbatim source passages are reproduced.

- https://genai.owasp.org/llmrisk/llm01-prompt-injection/ — direct/indirect origins,
  application-dependent impact and limits of prompt instructions.
- https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html —
  authentication/authorization, current resource permissions and default denial.
- https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html —
  protected baselines, derived source scope and retrieval/output boundaries.
- https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html —
  screening limitations, untrusted outputs and independently controlled effects.
- https://docs.python.org/3.13/library/json.html — bounded parsing and decoder hooks.
- https://docs.python.org/3.13/library/html.html — HTML text escaping and its scope.

The concrete limits, catalogue/update model, phrase patterns, quote schema and
test outcomes are this lab's explicit teaching policy. They are not universal
thresholds, a standard RAG security API or a substitute for production ownership.
