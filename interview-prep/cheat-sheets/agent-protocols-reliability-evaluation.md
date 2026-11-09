---
layout: "week"
status: "review"
version: "0.1.0"
last_reviewed: "2026-11-09"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "Agent protocols, reliability, security, and evaluation interview cheat sheet"
description: "MCP, A2A, identity, authorization, idempotency, retries, backpressure, threat boundaries, trajectory evaluation, and release readiness."
summary: "Revise protocol boundaries, durable side effects, least privilege, resilience controls, agent evaluation, observability, SLOs, and rollout gates."
permalink: "/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 4 · Protocols and reliability"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 4 source:** This review candidate integrates the prepared revision artifact into the Prep site. It is separate from the Week 1–20 learning assessments.

**Target roles:** Agentic AI Engineer, AI Platform Engineer, ML Engineer, AI Security Engineer, AI/Data Science Lead  
**Use:** MCP, A2A, tool contracts, identity, durable execution, evaluation, observability, and production readiness  
**Interview rule:** a protocol standardizes communication; it does not establish trust, authorization, correctness, durability, or business semantics.

## 1. Thirty-second revision

- **MCP** standardizes how an AI host/client discovers and invokes server capabilities such as tools, resources, and prompts.
- **A2A** standardizes communication with remote, independently implemented agents through discoverable capabilities, tasks/messages/artifacts, and streaming/updates.
- MCP is usually agent/application-to-capability; A2A is agent-to-agent. They can coexist.
- OpenAPI describes HTTP APIs; JSON Schema describes data; events/queues decouple asynchronous services. Pick protocols by boundary, not hype.
- Authentication establishes identity; authorization decides allowed action and resource. Propagate user/tenant context explicitly and use least privilege.
- Durable workflow state does not make side effects exactly once. Use idempotency, deduplication, status reconciliation, and compensation.
- Retry only transient, safe operations; use deadlines, exponential backoff with jitter, circuit breakers, rate limits, and backpressure.
- Treat remote tools, retrieved content, and agent messages as untrusted input vulnerable to prompt injection and data exfiltration.
- Evaluate final outcome plus trajectory, tool calls, handoffs, recovery, safety, latency, tokens, and cost.
- Release with versioned offline suites, fault/security tests, shadow/canary rollout, SLOs, alerts, and rollback.

## 2. Protocol map

| Boundary | Prefer | Why |
|---|---|---|
| Model/application needs discoverable tools or context | MCP | common capability discovery and invocation model |
| One independently deployed agent delegates to another | A2A | agent discovery and long-running task collaboration |
| Stable service API with known endpoints | OpenAPI/HTTP or gRPC | explicit service contract and mature infrastructure |
| Asynchronous domain change/integration | event/queue protocol | decoupling, buffering, replay, delivery controls |
| Internal in-process function call | typed function/interface | lowest complexity and latency |

Do not replace a simple internal function with a network protocol unless independent deployment, reuse, or security boundaries justify it.

## 3. MCP mental model

MCP separates three roles:

- **Host:** the AI application coordinating users, model access, permissions, and one or more MCP clients.
- **Client:** the protocol participant inside the host that maintains a connection/session to a server.
- **Server:** exposes capabilities to clients.

Core server primitives:

| Primitive | Typical control | Purpose | Example |
|---|---|---|---|
| Tool | model requests; host governs execution | perform computation/action | search, create ticket, query service |
| Resource | application selects/reads | expose contextual data | file, schema, record, API response |
| Prompt | user/app selects | reusable prompt/message template | review command, guided analysis |

The official SDK describes the intuition as tools being model-controlled, resources application-controlled, and prompts user-controlled. In production, the host still needs policy and approval around all three.

## 4. MCP lifecycle and transport concerns

MCP implementations negotiate protocol/capabilities and exchange structured messages. Common transports include local process `stdio` and Streamable HTTP; exact supported transports depend on spec/SDK version.

Design for:

- protocol/version negotiation and capability discovery;
- initialization failure and incompatible features;
- connection/session lifecycle and cancellation;
- progress, pagination, and large payload handling;
- HTTP authentication and secure local process launching;
- network timeouts, proxies, DNS, TLS, and egress controls;
- server/tool versioning and deprecation;
- trace propagation without leaking secrets.

Never assume a locally launched MCP server is harmless. It is code with the user’s process permissions unless sandboxed.

## 5. Secure MCP tool design

For every tool:

1. describe exactly what it does and whether it mutates state;
2. use constrained input/output schemas;
3. authenticate the caller and authorize tenant/resource/action;
4. validate business semantics and current state;
5. limit output size and redact sensitive fields;
6. assign deadlines, quotas, and concurrency limits;
7. use idempotency keys for mutations;
8. require approval for consequential actions;
9. return stable, typed error categories;
10. audit operation ID, principal, resource, outcome, and policy decision.

The model must never choose its own authorization scope.

## 6. MCP security threats

- malicious tool descriptions or server substitution;
- prompt injection embedded in resource/tool output;
- token theft, confused-deputy behavior, or excessive OAuth scopes;
- DNS rebinding/SSRF and unsafe remote URLs;
- command execution through local servers;
- cross-tenant resource enumeration;
- tool-name collision/shadowing;
- output flooding or denial of wallet;
- sensitive trace/log capture;
- approval fatigue and misleading action previews.

Mitigations include trusted registries/pinning, signed or reviewed packages, OAuth/resource indicators as required by the current spec, least-privilege scopes, audience validation, sandboxing, network allowlists, explicit consent, semantic validation, tenant-aware logs, and server kill switches.

## 7. A2A mental model

A2A is for collaboration across opaque agent systems that may use different frameworks or vendors.

Important concepts include:

- **Agent Card:** metadata for discovering an agent’s identity, endpoint, capabilities/skills, and supported security/interface information;
- **Message/parts:** communication between user/client agent and remote agent;
- **Task:** a stateful unit of work that can progress over time;
- **Artifact:** an output produced by the task;
- **updates/streaming:** progress or task-state changes for long-running work.

A2A commonly uses web standards such as HTTP(S), JSON-RPC, and streaming mechanisms depending on the protocol version/binding. Verify the exact current specification before coding.

## 8. A2A design concerns

- Discover and pin the correct Agent Card; do not trust arbitrary discovery output.
- Authenticate both transport and workload identities where appropriate.
- Authorize the task, data, and tools available to the remote agent.
- Minimize the context sent; redact secrets and irrelevant transcript history.
- Define task ownership, cancellation, deadline, and terminal states.
- Correlate remote task IDs with local run/operation IDs.
- Validate artifacts before using them or triggering downstream actions.
- Handle duplicate requests, retries, late results, and unavailable agents.
- Version skills and task schemas.
- Decide whether a remote response is evidence, a recommendation, or an authorized decision.

Agent Cards advertise capabilities; they are not proof of quality or trust.

## 9. MCP versus A2A versus APIs/events

| Question | MCP | A2A | OpenAPI/gRPC | Events/queues |
|---|---|---|---|---|
| Primary abstraction | tools/resources/prompts | agent tasks/messages/artifacts | service methods/resources | facts/commands/messages |
| Typical caller | AI host/client | client/remote agent | any service/client | producer/consumer |
| Discovery | capability listing/server metadata | Agent Card/skills | API/service catalog | schema/topic catalog |
| Long-running work | possible but capability/version dependent | central design concern | polling/webhook/stream patterns | natural async processing |
| Model-aware semantics | yes | yes | no | no |
| Durable delivery | not implied | not implied | not implied | broker-dependent |
| Authorization | must be implemented/configured | must be implemented/configured | mature patterns | broker + consumer policy |
| Best use | reusable AI capabilities/context | remote agent collaboration | stable service contract | decoupled async integration |

MCP and A2A can wrap existing APIs rather than replace them.

## 10. Identity, delegation, and authorization

Separate identities:

- end user/principal;
- application/agent workload;
- tool/MCP/A2A server;
- downstream service;
- approving human.

Key questions:

- Is the agent acting **as the user** or **on behalf of the application**?
- Which tenant and resource scope applies?
- Can the downstream service verify token audience, issuer, expiry, and scope?
- Is delegation attenuated, time-bound, and auditable?
- Can a remote agent further delegate?
- Does human approval grant one operation or broad future access?

Do not pass a powerful long-lived user token into prompts, state, or another agent. Prefer short-lived, audience-bound credentials and server-side policy enforcement.

## 11. Reliability state machine

Model runs as explicit states, for example:

```text
RECEIVED → VALIDATED → RUNNING → WAITING_FOR_INPUT
                     ↘ RETRY_WAIT
RUNNING → SUCCEEDED | FAILED | CANCELLED | EXPIRED | ESCALATED
```

Define valid transitions, ownership, timestamps, reason codes, and terminal behavior. The model can propose a transition, but application code should validate it.

## 12. Idempotency and deduplication

An idempotency key identifies one intended business operation. Repeating the same operation with the same key should return the original result/status rather than repeat the side effect.

```python
from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable
from typing import Protocol


@dataclass(frozen=True)
class OperationResult:
    status: str
    external_id: str | None


class OperationStore(Protocol):
    def get(self, key: str) -> OperationResult | None: ...
    def reserve(self, key: str) -> bool: ...
    def complete(self, key: str, result: OperationResult) -> None: ...


def execute_once(
    key: str,
    store: OperationStore,
    action: Callable[[str], OperationResult],
) -> OperationResult:
    existing = store.get(key)
    if existing is not None:
        return existing
    if not store.reserve(key):
        return OperationResult(status="IN_PROGRESS", external_id=None)
    result = action(key)
    store.complete(key, result)
    return result
```

Real implementations need atomic uniqueness, lease/timeout recovery, payload hashing, unknown-outcome reconciliation, and retention.

### The exactly-once illusion

Networks can fail after a remote service commits but before the caller receives the response. The caller cannot know whether the action happened. Solve with:

- remote idempotency keys;
- a status lookup/reconciliation API;
- transactional outbox/inbox for events;
- deduplication at consumers;
- compensation for reversible business actions.

“Exactly once” is usually an end-to-end business property engineered above delivery attempts.

## 13. Retry policy

Retry only when all are true:

- the error is plausibly transient;
- the operation is retry-safe;
- the overall deadline remains;
- the attempt budget is not exhausted;
- retries will not overload a failing dependency.

Use exponential backoff with randomized jitter. Honor provider retry hints where trustworthy. Maintain separate policies for rate limits, timeouts, connection errors, validation errors, and business rejections.

Never retry authentication/authorization denial unchanged or an invalid request endlessly.

## 14. Timeouts, deadlines, cancellation, and backpressure

- **Timeout:** maximum duration for one operation.
- **Deadline:** remaining time for the end-to-end request.
- **Cancellation:** stop work that is no longer needed.
- **Backpressure:** slow/reject intake when capacity is saturated.

Propagate the remaining deadline to sub-agents/tools. Reserve time for fallback/cleanup. Limit queues, concurrency, and fan-out. When clients disconnect, decide whether durable business work continues or is cancelled.

A timeout does not prove a remote mutation failed; reconcile before retrying.

## 15. Circuit breakers, bulkheads, and fallbacks

- **Circuit breaker:** temporarily stop calls to an unhealthy dependency.
- **Bulkhead:** isolate capacity so one provider/tool/tenant cannot exhaust all resources.
- **Fallback:** alternate model/tool/path, cached answer, reduced service, or human escalation.

Fallback is safe only if capability, policy, data residency, tool schema, and quality remain acceptable. A cheaper model may not preserve tool-call behavior.

## 16. Side-effect barriers and compensation

Separate:

1. propose action;
2. validate policy/business rules;
3. display exact preview;
4. obtain approval if required;
5. persist intent/idempotency key;
6. execute;
7. reconcile and record outcome.

For multi-step business processes, use a saga/compensation design. Compensation is domain logic—not simply “undo”; a sent email cannot be unsent, but a correction can be issued.

## 17. Loop and resource controls

Enforce:

- step and repeated-action limits;
- tool/sub-agent call limits;
- delegation depth;
- input/output/context token budgets;
- dollar budget;
- wall-clock deadline;
- concurrency/fan-out cap;
- maximum result size;
- progress/no-progress detection.

Route budget exhaustion to a defined partial-result, safe-abstain, or escalation state.

## 18. Observability model

Use a trace tree such as:

```text
request/run
├── route or plan
├── model call
├── tool or MCP call
│   └── downstream API/database
├── A2A task/handoff
└── validation/approval/finalization
```

Record:

- correlation, run, thread, task, operation, and idempotency IDs;
- principal/tenant in protected metadata;
- model/prompt/tool/server/framework/policy/data versions;
- route, arguments hash/schema validation, result status, and error category;
- queue time, model/tool latency, tokens, cache usage, retries, and cost;
- approvals, cancellations, checkpoint/resume, and final business outcome.

Redact prompts, tool arguments, credentials, PII, and retrieved content according to policy. Observability must not become the largest data leak.

## 19. Evaluation layers

| Layer | What to measure |
|---|---|
| Final task | correctness, completion, business outcome, abstention |
| Plan/route | correct intent, decomposition, branch selection |
| Tool | correct tool, argument validity, authorization, result use |
| Trajectory | necessary steps, loops, redundancy, progress |
| Retrieval/evidence | relevance, coverage, authority, citation support |
| Multi-agent | delegation/handoff correctness, context loss, duplicate work |
| Reliability | recovery, retry safety, resume success, duplicate side effects |
| Security | prompt injection resistance, data/tool policy violations |
| Operations | p50/p95/p99 latency, throughput, tokens, cost, error/escalation rate |

An aggregate judge score hides which subsystem failed.

## 20. Evaluation dataset design

Include:

- frequent and high-value real tasks;
- rare high-severity cases;
- ambiguous/missing-input and no-answer cases;
- tool failures, timeouts, stale data, and partial outages;
- duplicate delivery and resume-after-crash cases;
- multilingual/long-context/large-result cases;
- authorization boundaries and cross-tenant attempts;
- direct/indirect prompt injection and poisoned tool output;
- policy changes and version regressions.

Store expected outcomes, acceptable routes/tools, forbidden actions, required evidence, risk slice, and adjudication. Keep a final holdout separate from optimization.

## 21. Deterministic and model-based evaluation

### Deterministic checks first

- schema and state-transition validity;
- exact tool/route requirements;
- no forbidden tool/action;
- citation/source ID existence;
- budget and latency limits;
- duplicate-side-effect absence;
- authorization decisions;
- unit/integration/property tests.

### Model or human judges

Use for nuanced correctness, completeness, groundedness, and communication quality. Calibrate model judges against expert labels, randomize pairwise order, version judge prompts/models, and measure disagreement.

The agent under test should not be the only judge of its own success.

## 22. Fault injection and adversarial testing

Inject:

- model 429/5xx/malformed tool output;
- slow/hung/unavailable MCP or A2A servers;
- failure before and after external commit;
- duplicate requests/events/resume commands;
- lost streaming connection and cancellation;
- corrupt/old checkpoint or incompatible state version;
- malicious resource/tool descriptions and indirect instructions;
- huge outputs, tool loops, and agent handoff loops;
- identity/scope mismatch and tenant-crossing attempts.

Verify bounded failure, preserved state, no duplicated mutation, safe user message, alerting, and recovery runbook.

## 23. Release gates and SLOs

Example gates should be risk-specific:

- no critical unauthorized-action/data-leak failures;
- task success and tool accuracy above agreed slice thresholds;
- zero duplicate high-impact side effects in fault tests;
- p95 latency and cost within budget;
- resume/recovery success target met;
- judge-human agreement calibrated;
- rollback and kill switch tested.

Roll out through offline validation → integration/fault/security tests → shadow → restricted canary → gradual expansion. Monitor business and safety outcomes, not only HTTP uptime.

## 24. Common interview traps

- Saying MCP or A2A provides authentication/authorization automatically.
- Treating Agent Cards/tool descriptions as trusted attestations.
- Using retries to solve permanent or semantic failures.
- Claiming a checkpoint creates exactly-once side effects.
- Evaluating only final text while tools perform unsafe actions.
- Logging raw prompts/tool payloads “for observability.”
- Using one timeout for an entire multi-step workflow.
- Falling back to an untested model/provider during an outage.
- Measuring average latency while p95/p99 breaches user deadlines.
- Running LLM-as-judge without calibration or deterministic checks.

## 25. Rapid interview questions

**Q1. MCP versus A2A?**  
MCP exposes tools/context/prompts to an AI host; A2A supports collaboration with an independently deployed remote agent. They address complementary boundaries.

**Q2. Does MCP secure a tool?**  
No. The deployment must authenticate, authorize, validate, sandbox, limit, audit, and sometimes require approval.

**Q3. What is an A2A Agent Card?**  
Discoverable metadata describing an agent endpoint/capabilities and relevant interface/security information; it is not a quality or trust guarantee.

**Q4. What makes an operation idempotent?**  
The same intended operation/key can be retried without producing an additional business effect, and returns/reconciles the original status.

**Q5. Why can a timeout be dangerous?**  
The server may have committed the action although the caller did not receive the result; blind retry may duplicate it.

**Q6. What is trajectory evaluation?**  
Assessing the path—routes, tools, arguments, evidence, loops, handoffs, and recovery—not only the final answer.

**Q7. Circuit breaker versus retry?**  
Retry handles a small number of transient failures; a circuit breaker stops repeated load when a dependency appears unhealthy.

**Q8. How do you test agent reliability?**  
Use deterministic fake tools/models plus fault injection for timeouts, duplicate delivery, crash/resume, partial commits, invalid outputs, and adversarial content.

## 26. Lead-level design case

**Prompt:** Design a customer-support orchestrator that uses MCP tools for account actions and delegates specialist investigations to remote A2A agents.

A strong answer should:

1. define user/workload identity, tenant scope, risk tiers, and SLOs;
2. use MCP for narrow account tools and A2A only for independently owned specialists;
3. pin trusted servers/Agent Cards and enforce least-privilege credentials;
4. keep account authorization in downstream services;
5. use durable task states, deadlines, cancellation, and correlation IDs;
6. protect mutations with previews, approval, idempotency, and reconciliation;
7. treat remote messages/tool results as untrusted and validate artifacts;
8. add bounded retries, circuit breakers, bulkheads, and human fallback;
9. evaluate route/tool/handoff/task/safety/recovery/latency/cost metrics;
10. canary low-risk intents first with tested kill switches and manual queues.

## 27. Final checklist

- [ ] I can distinguish MCP, A2A, service APIs, schemas, and events.
- [ ] I understand MCP host/client/server and tools/resources/prompts.
- [ ] I understand A2A Agent Cards, tasks, messages, artifacts, and updates.
- [ ] I can design identity propagation and least-privilege delegated access.
- [ ] I can explain idempotency, unknown outcomes, deduplication, and compensation.
- [ ] I can apply retries, deadlines, cancellation, backpressure, circuit breakers, and bulkheads.
- [ ] I can design privacy-safe traces and risk-based SLOs.
- [ ] I can evaluate outcome, trajectory, tools, collaboration, reliability, security, and cost.

## 28. Primary references

- Model Context Protocol, [Official documentation](https://modelcontextprotocol.io/docs/getting-started/intro)
- Model Context Protocol, [Specification](https://modelcontextprotocol.io/specification/)
- Model Context Protocol, [Security best practices](https://modelcontextprotocol.io/specification/latest/basic/security_best_practices)
- Agent2Agent Protocol, [Official documentation](https://a2a-protocol.org/latest/)
- Agent2Agent Protocol, [Specification](https://a2a-protocol.org/latest/specification/)
- Google Cloud, [Getting started with MCP, ADK, and A2A](https://codelabs.developers.google.com/intro-a2a-purchasing-concierge)
- OpenTelemetry, [Generative AI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)

Protocol details evolve. Pin a specification/SDK version and verify transport, authorization, and task semantics against that version.
