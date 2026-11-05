---
layout: week
week: 19
phase: 5
status: approved
version: 1.0.0
last_reviewed: 2026-11-05
estimated_hours: 8
permalink: /weeks/week-19/
title: "Put enforceable guardrails between agents and tools"
description: Build a least-privilege gateway with separate read and write authority, exact human approval, bounded steps, a closed sandbox, secret-minimized audit events and reversible local actions.
summary: An agent may propose an action; trusted application code must independently decide whether that exact action is allowed before any tool runs.
kicker_primary: Agent safety and guardrails
kicker_secondary: Least privilege, approval, isolation, audit and recovery
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-19/beginner/
---

## Safety belongs on the execution path

“Only use safe tools” is useful instruction and weak authorization. A model can
misunderstand a request, follow injected content, choose the wrong tool or send
the wrong arguments. If the same model output decides both what should happen
and whether it is permitted, a fluent mistake can become a real action.

Week 19 puts a deterministic gateway between Procurement Intelligence Agent v1
and its tools. The agent proposes a call. Trusted application code supplies the
identity and permissions, validates the tool and arguments, checks a hard step
budget, requires an exact human grant for writes, records a safe audit event and
only then enters a closed local dispatcher.

The lab has three read tools, one reversible review-flag write and one separately
authorized reversal. It has no shell, generic HTTP fetch, dynamic SQL, file path,
provider or external procurement action.

If authorization and capability boundaries are new, start with the
[beginner version]({{ '/weeks/week-19/beginner/' | relative_url }}).

| Time | Focus | Evidence to retain |
| --- | --- | --- |
| Hour 1 | Draw trust boundaries | proposal separated from authority and execution |
| Hour 2 | Minimize the tool surface | closed registry and permission matrix |
| Hour 3 | Validate every request | exact schemas and tenant-scoped lookup |
| Hour 4 | Gate writes | one human grant bound to one exact action |
| Hour 5 | Bound and isolate execution | step budget and closed sandbox dispatcher |
| Hour 6 | Protect secrets and audit events | safe fields, lifecycle coverage and hash chain |
| Hour 7 | Make local writes recoverable | receipt, fresh reversal approval and conflict check |
| Hour 8 | Attack the controls | failure, replay, tamper and CLI evidence |

## Separate proposal, authority and execution

The most important boundary is structural:

| Layer | May decide | Must not decide |
| --- | --- | --- |
| Agent | which available tool may help and with what business arguments | its tenant, identity, permissions or whether its own write is approved |
| Trusted host | authenticated scope, policy, approval, limits and audit | business facts returned by the tool |
| Tool sandbox | execute one fixed operation over scoped resources | add capabilities, widen permissions or reinterpret policy |

The lab's `ToolRequest` contains a request ID, tool, arguments and optional
approval reference. It deliberately contains no `permissions`, `tenant_id` or
“approved” boolean. Those values come from `TrustedScope`, which the host creates
outside agent-controlled data.

This prevents a confused-deputy pattern such as:

~~~json
{
  "tool": "review_flag_set",
  "tenant_id": "tenant-rival",
  "permissions": ["review_flag:write"],
  "approved": true
}
~~~

The request can claim anything in text; the gateway does not treat those claims
as authority. It uses the server-owned tenant and permissions on every call.

**Checkpoint:** ask where each authorization fact originates. If the answer is
“the prompt” or “the model said so,” it is not an authorization control.

## Minimize functionality, permission and autonomy

Excessive agency has three common dimensions:

1. **Functionality:** the agent has tools it does not need.
2. **Permission:** a necessary tool can access too much.
3. **Autonomy:** a high-impact action runs without independent review.

The Week 19 registry narrows all three:

| Tool | Mode | Permission | Exact arguments | Human approval |
| --- | --- | --- | --- | --- |
| `contract_lookup` | read | `contract:read` | `contract_id` | no |
| `purchase_order_lookup` | read | `order:read` | `order_id` | no |
| `supplier_risk_lookup` | read | `risk:read` | `supplier_id` | no |
| `review_flag_set` | write | `review_flag:write` | `flag_id`, `value` | always |
| `review_flag_revert` | write | `review_flag:revert` | `undo_token` | always, fresh grant |

An unknown `shell_exec`, `fetch_url` or `run_sql` name has no dispatcher entry.
There is no broad tool whose prompt promises to use only safe subcommands.

Least privilege must also exist downstream. An application check is useful, but
a production database identity used for reads should still lack insert, update
and delete privileges. Complete mediation means every action is checked at the
gateway and again by the system that owns the resource.

## Read and write authority are different capabilities

Reading may disclose data. Writing changes state. Deleting, sending, purchasing
and publishing can cause irreversible effects. Treating one “tool access” flag as
authority for all of them hides this difference.

Week 19 uses separate permission strings. A principal with `contract:read`
cannot set a review flag. A principal with `review_flag:write` cannot reverse an
earlier action unless it also has `review_flag:revert`. The split supports roles
such as:

- an investigation agent that can only read;
- an operator that may set a reversible review flag after approval; and
- a recovery operator that may reverse an action after a new review.

Permission does not replace approval. Permission answers, “May this principal
ever perform this class of action?” Approval answers, “Did a human authorize this
exact action in this exact context now?”

## Validate the operation before policy evaluation

Every registered tool declares an exact set of argument names. Values must be
strict bounded identifiers; Pydantic coercion and unknown boundary fields are
disabled. The write accepts only `clear` or `needs_human`.

That closes several gaps:

- extra arguments cannot smuggle a tenant, callback URL or alternate command;
- missing values do not fall through to tool defaults;
- integer `171` does not silently become string `"171"`;
- path separators, spaces and command fragments fail the identifier pattern;
- non-finite JSON numbers fail the strict model boundary; and
- a valid tool cannot receive another tool's argument shape.

Validation is not authorization. Perform both, in a stable order, and return
controlled failure codes rather than raw library errors.

## Bind human approval to the exact write

A reusable `approved=true` flag is permission laundering. The reviewer may have
seen one supplier, amount or destination while the eventual call contains
another. The lab computes a canonical JSON SHA-256 over the arguments and binds
the grant to:

- tenant and principal;
- run and case;
- request ID and tool;
- exact argument digest; and
- approving human identity.

Changing any field produces `approval_mismatch`. An unknown grant produces
`approval_not_found`. A write with no grant produces `approval_required`.

The gateway consumes a valid grant before dispatch. That matters when a tool
times out or fails after starting: silently replaying the same authorization
could duplicate an action. This Week 19 lab does not implement retries; Week 20
will address reliability. Here, a failed write needs a fresh human decision.

Canonical hashing lets the approval and audit trail refer to the same exact
action without copying raw values into the log. A digest is not encryption or
proof that a human understood the action. Low-entropy values may be guessable,
and the approval user interface must show a clear normalized preview.

**Checkpoint:** approval is attached to a call, not to a conversation's mood.

## Enforce a hard maximum-step budget

An agent loop can spend money, repeatedly touch systems or amplify a mistaken
action. “Try no more than six times” in a prompt is not a hard stop.

`GatewayConfig` accepts a maximum from 1 through 20. The gateway counts calls in
trusted code. An attempt beyond the configured budget records a `step_limit`
event and returns `step_limit_exceeded` before the sandbox runs.

The number should match the workflow's accepted graph. A normal procurement
investigation with four specialists does not need hundreds of steps. Different
routes may need different budgets, but every budget needs:

- a clear unit: model turns, tool calls or graph transitions;
- a trusted counter;
- a stop state the caller understands; and
- an audit event that distinguishes exhaustion from tool failure.

This control bounds tool chaining. Token, time and cost budgets are related but
separate production controls.

## Use a real capability boundary, not a reassuring label

The lab's `InMemorySandbox` exposes five direct Python branches over synthetic
dictionaries. It has no function for arbitrary code, shell, network, filesystem,
database or environment access. That is a closed capability surface.

It is not an operating-system sandbox. All objects live in one trusted Python
process. If hostile code could obtain the sandbox object or import arbitrary
modules, this boundary would not contain it.

Production sandboxing depends on the risk:

| Risk | Typical enforcement |
| --- | --- |
| untrusted code | separate process/VM/container, syscall policy and disposable filesystem |
| network exfiltration | deny-by-default egress and destination allowlist |
| resource exhaustion | CPU, memory, process, output and wall-time limits |
| cross-tenant access | authenticated identity and downstream row/object policy |
| secret theft | no ambient secret; short-lived scoped handle from a secret manager |
| destructive state | narrow API, transaction/idempotency policy, approval and recovery plan |

An approval mechanism does not create isolation. The executor still has to
enforce where a command runs, what it can reach and what identity it uses.

## Isolate secrets from agents, tools and logs

The safest secret is one the model never sees. A production agent should ask for
a named operation while trusted infrastructure resolves a short-lived credential
inside the tool boundary.

Week 19 rejects argument keys that look like API keys, authorization headers,
credentials, passwords, secrets or tokens. It never stores raw arguments in
audit events. The reversal's `undo_token` is the only declared sensitive
capability; it is accepted only by the fixed reversal tool and represented in
audit by the whole-argument digest.

This is a teaching check, not a general data-loss-prevention engine. A secret can
appear under an innocent key or inside a document. Production controls include
data classification, secret managers, output filtering, restricted log access,
rotation and incident response.

Do not print secrets and then hope a later redaction catches every copy. Prevent
them from entering model context and ordinary telemetry in the first place.

## Audit the lifecycle without hoarding payloads

“Full audit logging” means every consequential transition is covered, not every
byte is retained. The lab records:

- monotonically increasing sequence;
- trusted tenant, principal, run and case;
- tool and controlled decision code;
- canonical argument digest;
- approval ID and reviewer only after a valid check;
- predecessor hash; and
- current event hash.

Event types cover request, approval check, denial, execution, reversal, step
limit and failure. Raw arguments, secret values, arbitrary exceptions and stack
traces are excluded.

Each hash covers the safe event fields plus the previous hash. Verification
detects a changed or reordered event in the supplied chain. It does not prove
who created the chain, prevent deletion or reveal that someone removed a valid
suffix. A production trail needs authenticated event origin, access control,
durable append-only storage, externally anchored or signed heads, retention and
monitoring when logging stops.

**Checkpoint:** logs are another sensitive system. Least privilege applies to
who can read and alter them.

## Prefer reversible actions—and understand their limits

`review_flag_set` returns a receipt containing the prior value, new value and an
opaque undo token. Reversal requires:

1. the separate `review_flag:revert` permission;
2. a fresh human approval bound to the reversal call;
3. the same tenant that created the token;
4. a token that has not already been used; and
5. current state that still equals the value written by the original action.

The last check prevents a stale undo from overwriting a newer legitimate change.
If state has moved, the result is `undo_conflict`, not a blind rollback.

Reversibility is not idempotency. An idempotency key prevents the same operation
from taking effect twice; an undo operation compensates after an effect. Some
actions—messages already read, data already disclosed, money already settled—may
not be fully reversible. For those, use staged drafts, delayed execution,
stronger review or no autonomous authority.

## Fail safely and reveal only controlled information

The gateway uses three public statuses:

| Status | Meaning | Example code |
| --- | --- | --- |
| `completed` | permitted action finished | `ok` |
| `blocked` | policy prevented dispatch | `permission_denied`, `approval_required`, `step_limit_exceeded` |
| `failed` | an allowed tool could not complete safely | `data_not_found`, `undo_conflict`, `tool_failure` |

Unexpected exceptions map to `tool_failure`. The public result and audit event do
not expose the internal message, connection string or stack. Detailed diagnostic
data belongs in a separately protected operational channel with its own
redaction and access policy.

Safe failure also means no silent fallback to a broader tool. A failed contract
lookup must not trigger arbitrary SQL or web access merely to keep the run moving.

## Run the seven scenarios

~~~shell
python -m pip install -r requirements-dev.txt
python -m labs.week_19.demo case --scenario read
python -m labs.week_19.demo case --scenario write-without-approval
python -m labs.week_19.demo case --scenario approved-write
python -m labs.week_19.demo case --scenario reversal
python -m labs.week_19.demo case --scenario secret-rejected
python -m labs.week_19.demo case --scenario max-steps
python -m labs.week_19.demo case --scenario tool-failure
python -m labs.week_19.demo smoke
python -m pytest tests/test_week19_agent_safety.py -q
~~~

Inspect the JSON for each scenario. A permitted read has `requested` and
`executed` events. An approved write adds `approval_checked`. A missing approval
ends in `denied` without state mutation. A reversal produces its own approval and
`reversed` event. The smoke command checks all seven scenarios and deterministic
replay.

The 29 focused tests also mutate every approval binding field, cross tenant
scope, replay a grant, exceed the step budget, inject secret-looking fields,
force an internal exception, alter and reorder audit events, reuse an undo token
and try a stale rollback.

## Know what this lab proves

It proves that one local implementation enforces its declared contracts over
synthetic state. It does not prove:

- a model will always choose the correct tool;
- the human reviewer is authorized, attentive or uncompromised;
- SHA-256 events are durably stored or authenticated;
- one Python process can safely execute hostile code;
- string-key checks find every secret;
- a real downstream service enforces the same tenant and permission scope; or
- reversible local flags make external procurement actions safe.

Before production, add real authentication, a policy decision point, downstream
authorization, transactional approval consumption, protected audit storage,
short-lived secret handles, process/container isolation, egress controls,
resource limits, operational alerts and adversarial testing for the actual tool
surface.

## Interview answer

> I treat model output as an untrusted action proposal. A server-side gateway
> obtains tenant, principal and permissions from authenticated context, then
> allowlists the tool, validates a closed argument schema, checks least privilege
> and a hard step budget, and requires a per-call human grant for consequential
> writes. The grant is bound to run, resource context, tool and canonical
> arguments and is consumed once. Tools execute through a narrow isolated
> capability with no ambient secrets. Every lifecycle decision emits structured,
> secret-minimized audit metadata with tamper evidence. Failures return controlled
> codes, and reversible actions use separately authorized compensation with
> conflict checks. I still enforce authorization downstream because prompts,
> approvals and SDK features are not security boundaries by themselves.

## Independent exercises

1. Add `supplier_message_draft` as a local reversible write. Define its exact
   permission, arguments, reviewer view, receipt and reversal conflict.
2. Add expiry to approval grants using an injected deterministic clock. Test both
   sides of the boundary without using the current clock directly.
3. Replace SHA-256 action references with an HMAC from a protected fixture key.
   Explain which threat changes and which threats remain.
4. Add an idempotency key to `review_flag_set`. Distinguish duplicate prevention
   from approval replay prevention and reversal.
5. Persist audit events to an append-only fixture and anchor the final head in a
   separately controlled file. Test truncation detection.
6. Define a permission set for a read-only investigation agent. Prove no registry
   route can write even when its prompt asks to.
7. Design a two-person approval policy for a payment-like action. State how
   separation of duties is enforced outside the model.

## Finish with evidence

You are done when you can show:

- trusted identity and authority never come from a tool request;
- a closed registry with separate read, write and reversal permissions;
- exact schemas and tenant-scoped resource lookup;
- one-time human approval bound to one normalized write;
- a hard maximum-step stop before dispatch;
- a dispatcher with no open-ended shell, URL, code or path capability;
- secret-minimized lifecycle audit events and honest hash-chain limits;
- a reversible local action with fresh approval, tenant scope and conflict check;
- controlled policy and tool failure responses;
- deterministic replay, CLI smoke and 29 focused passing tests; and
- explicit production gaps rather than a broad safety claim.

## Sources and further reading

- [OWASP LLM06:2025 Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)
  for minimizing tool functionality, permissions and autonomy, requiring approval
  and enforcing downstream authorization.
- [OWASP AI Agent Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html)
  for least privilege, human oversight, execution isolation, limits and structured
  security metadata.
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
  for lifecycle events, sensitive-data exclusion, access control and tamper
  detection.
- [NIST glossary: least privilege](https://csrc.nist.gov/glossary/term/least_privilege)
  for granting only the resources and authorization needed for a function.
- [OpenAI Agents SDK human-in-the-loop guide](https://openai.github.io/openai-agents-python/human_in_the_loop/)
  for per-call approval, paused runs and approval-scope cautions.
- [OpenAI Agents SDK tools guide](https://openai.github.io/openai-agents-python/tools/)
  for the explicit distinction between approval and executor isolation.
- [Week 19 lab](https://github.com/kogantisasank831-ux/Prep/tree/main/labs/week_19)
  for the complete local contracts, gateway, scenarios and tests.
