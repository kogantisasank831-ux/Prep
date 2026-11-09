---
layout: "week"
status: "approved"
version: "1.0.0"
last_reviewed: "2026-11-09"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "AI agent fundamentals and workflow patterns interview cheat sheet"
description: "Agent and workflow boundaries, tool contracts, state, memory, multi-agent patterns, autonomy, human approval, and bounded execution."
summary: "Revise when to use agents, core runtime anatomy, tool safety, routing and coordination patterns, memory boundaries, budgets, and human oversight."
permalink: "/interview-prep/cheat-sheets/agent-fundamentals-workflow-patterns/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 4 · Agent fundamentals"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 4 source:** This page integrates the prepared revision artifact into the Prep site. It is separate from the Week 1–20 learning assessments.

**Target roles:** Agentic AI Engineer, AI Engineer, ML Engineer, Senior Data Scientist, Data Science/AI Lead  
**Use:** architecture discussions, agent design, tool use, memory, multi-agent patterns, and production trade-offs  
**Interview rule:** start with the least autonomous design that can meet the requirement. More agents increase coordination, latency, cost, security exposure, and failure modes.

## 1. Thirty-second revision

- A **workflow** follows code-defined paths; an **agent** lets a model choose at least some next actions at runtime.
- An agent is usually a loop around a model, tools, state, policies, and a stop condition—not just a prompt.
- Keep deterministic business rules in code. Use model judgment where inputs are ambiguous or paths cannot be enumerated economically.
- Tool descriptions, typed schemas, authorization, validation, timeouts, and idempotency matter as much as model quality.
- Common patterns are routing, sequential pipelines, parallel fan-out/fan-in, evaluator–optimizer, supervisor, handoff, and agents-as-tools.
- State is the working data for one execution; short-term memory is normally thread/session scoped; long-term memory survives across sessions.
- Multi-agent designs help when specialists need separate tools, policies, context, ownership, or deployment boundaries—not merely because a task has several steps.
- Human approval should protect consequential or irreversible actions, not every low-risk step.
- Bound every loop with step, token, time, cost, and tool-call budgets.
- Evaluate task success and the trajectory: tool choice, arguments, handoffs, evidence, recovery, latency, cost, and safety.

## 2. Workflow, agent, and autonomy spectrum

| Design | Who chooses the path? | Best fit | Main risk |
|---|---|---|---|
| Deterministic function/pipeline | Code | Known rules and stable inputs | Rule explosion when ambiguity grows |
| LLM-enhanced workflow | Code chooses stages; model handles bounded judgment | Extraction, classification, summarization, RAG | Model variability inside a fixed path |
| Router workflow | Model or classifier chooses one of approved paths | Intent routing, support triage | Wrong route or weak fallback |
| Bounded agent | Model selects tools/next step within budgets and policy | Research, troubleshooting, complex case handling | Loops, unsafe calls, inconsistent plans |
| Open-ended agent | Model has broad control and dynamic goals | Sandboxed exploration and research | Unbounded cost and side effects |

An interviewer may ask, “When should you not use an agent?” Strong answer: when the path is known, correctness must be deterministic, the action is high consequence, or latency/cost requirements leave no room for iterative reasoning.

## 3. Core agent anatomy

1. **Goal/input:** the user request plus acceptance criteria.
2. **Policy/instructions:** role, constraints, priorities, and forbidden actions.
3. **Model:** proposes actions or final output.
4. **Tools:** typed capabilities for reading or changing external systems.
5. **State:** messages, intermediate results, budgets, approvals, and status.
6. **Memory:** selected information available beyond the current step or session.
7. **Orchestrator/runtime:** executes the loop, persists progress, retries safe operations, and emits events.
8. **Guardrails:** validation, authorization, content/action policies, and human gates.
9. **Observability:** traces, versions, tool calls, latency, cost, and outcomes.
10. **Termination:** success, safe refusal, escalation, budget exhaustion, or failure.

Do not let “the model decides” replace a state machine. Model decisions should produce validated proposals that the runtime can accept, reject, route, or require approval for.

## 4. A bounded agent loop

```python
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Literal


ActionKind = Literal["tool", "finish", "escalate"]


@dataclass(frozen=True)
class Action:
    kind: ActionKind
    name: str = ""
    arguments: dict[str, Any] = field(default_factory=dict)
    answer: str = ""


@dataclass
class RunState:
    observations: list[str] = field(default_factory=list)
    steps: int = 0


def run_bounded_agent(
    decide: Callable[[RunState], Action],
    tools: dict[str, Callable[..., str]],
    *,
    max_steps: int = 8,
) -> str:
    state = RunState()
    while state.steps < max_steps:
        state.steps += 1
        action = decide(state)
        if action.kind == "finish":
            return action.answer
        if action.kind == "escalate":
            return "ESCALATED"
        tool = tools.get(action.name)
        if tool is None:
            state.observations.append(f"Unknown tool: {action.name}")
            continue
        state.observations.append(tool(**action.arguments))
    return "STOPPED: step budget exhausted"
```

Production additions include schema validation, authorization, deadlines, cancellation, idempotency keys, approval gates, tracing, persistent checkpoints, and typed errors.

## 5. ReAct and plan–execute–reflect

### ReAct-style loop

The model alternates between reasoning/action selection and observations from tools. It is flexible and responsive but can be expensive, repetitive, and difficult to reproduce.

### Plan then execute

The model first creates a plan; an executor performs or delegates steps. It improves visibility and approval but plans become stale when observations change. Replanning should be explicit and budgeted.

### Reflection/evaluator loop

One stage critiques an output and another revises it. This helps when the rubric is clear and improvement can be measured. It can amplify shared model blind spots, so use deterministic checks or independent evidence where possible.

Never expose private chain-of-thought as a product requirement. Store concise decisions, plans, evidence, and reasons needed for auditability.

## 6. Tool design is API design

A production tool needs:

- a narrow, unambiguous name and description;
- typed input/output schemas and constraints;
- caller identity, tenant, scopes, and resource-level authorization;
- semantic validation, not only valid JSON;
- explicit read-only versus mutating behavior;
- timeout, retry safety, rate limits, and cancellation;
- idempotency or deduplication for mutations;
- redacted logs and trace correlation;
- stable error categories the agent can act on;
- a human-readable preview for consequential actions.

### Good versus weak tools

| Weak tool | Better tool | Why |
|---|---|---|
| `run_sql(sql)` | `get_customer_orders(customer_id, start_date, end_date)` | Narrows authorization and injection surface |
| `send_email(text)` | `prepare_email(...)` then `send_approved_email(draft_id, approval_id)` | Separates generation from side effect |
| `update_account(data)` | `change_address(account_id, expected_version, address, idempotency_key)` | Adds concurrency and duplicate protection |

Keep tool output concise and structured. Returning a 20,000-token raw response increases cost and lets untrusted data dominate the context.

## 7. Tool errors and recovery

Classify errors before deciding whether to retry:

| Error | Typical response |
|---|---|
| Invalid model arguments | Return validation details; allow a bounded correction |
| Transient timeout/429/5xx | Retry with backoff, jitter, deadline, and retry cap |
| Permanent 4xx/business rejection | Do not retry unchanged; replan or explain |
| Authorization failure | Do not ask the model to bypass it; request correct access or escalate |
| Ambiguous user intent | Pause for clarification |
| Unknown internal defect | Fail safely, preserve state, alert, and surface a trace ID |

Retrying an external write without idempotency can duplicate payments, messages, or tickets.

## 8. Single-agent workflow patterns

### Routing

A classifier or model selects a bounded specialist/path. Use confidence or explicit fallback; evaluate a confusion matrix by business cost, not only accuracy.

### Sequential pipeline

Stages such as classify → retrieve → draft → validate. Easy to observe and test, but an early error propagates.

### Parallel fan-out/fan-in

Independent workers search sources or process partitions concurrently; an aggregator combines results. Define reducers, ordering, partial-failure behavior, concurrency limits, and deduplication.

### Evaluator–optimizer

Generate → score against a rubric → revise until accepted or budget exhausted. Prefer measurable criteria such as schema validity, cited evidence, tests, or policy checks.

### Map–reduce

Map a task across documents/items and reduce structured results. Useful for long corpora, but reduction can lose minority or conflicting evidence.

## 9. Multi-agent patterns

| Pattern | Control | Use when | Failure to watch |
|---|---|---|---|
| Supervisor | Central agent delegates and synthesizes | One place must enforce policy and completion | Supervisor bottleneck/context overload |
| Handoff | Current agent transfers control to a specialist | Ownership should change during a conversation | Ping-pong loops and lost context |
| Agent as tool | Parent calls a specialist and receives a result | Parent should retain control | Hidden specialist errors |
| Peer collaboration | Agents exchange messages/claims | Exploration or independent expertise | Excess discussion and no accountable owner |
| Debate/judge | Candidates argue; judge selects | High-value ambiguity with evaluable evidence | Correlated errors and persuasive nonsense |
| Hierarchical | Supervisors manage worker groups | Large decomposable programs | Deep latency and difficult debugging |

### When a second agent is justified

- It owns different tools, permissions, or safety policy.
- It requires a materially different context or model.
- A team/service independently owns and deploys it.
- It is a reusable remote capability.
- Isolation improves evaluation or limits blast radius.

Different personas alone are weak justification. Often a single graph with typed nodes is simpler.

## 10. Routing, delegation, and handoff

Distinguish these terms:

- **Routing:** choose a branch; control remains with the orchestrator.
- **Delegation:** assign a task and expect a result; the caller retains responsibility.
- **Handoff:** transfer control/ownership to another agent.
- **Agent-as-tool:** expose an agent through a tool-like contract.

A handoff contract should carry the goal, relevant state, allowed actions, deadline/budget, provenance, and expected return/termination condition. Do not copy the entire transcript by default.

## 11. State, context, and memory

| Concept | Meaning | Example |
|---|---|---|
| State | Authoritative working data for the run | order ID, plan status, retrieved evidence |
| Model context | Selected information sent in one model call | system rules, recent messages, tool results |
| Short-term memory | Thread/session information across turns | conversation summary, pending approval |
| Long-term memory | Cross-session durable knowledge | verified preference, prior resolved case |

State can be larger than model context. A context builder selects what the model needs rather than serializing the entire state every time.

### Memory categories

- **Semantic:** facts, preferences, entities, relationships.
- **Episodic:** prior events and outcomes.
- **Procedural:** policies, skills, or successful routines.

Memory writes require provenance, confidence, scope, retention, correction, deletion, and conflict rules. Never treat a model inference as a verified fact merely because it was stored.

## 12. Context engineering

Useful controls include:

- stable system policy separated from untrusted content;
- task-specific retrieval rather than full-history replay;
- summaries that preserve decisions, commitments, unresolved questions, and source IDs;
- structured tool outputs and selective field projection;
- token budgets per component;
- recency, relevance, authority, and access filters;
- explicit conflict handling when sources disagree.

Prompt compression can save tokens but may remove constraints or evidence. Measure downstream task quality, not compression ratio alone.

## 13. Human-in-the-loop (HITL)

Common intervention points:

1. approve a plan before expensive execution;
2. approve, edit, or reject a consequential tool call;
3. resolve ambiguous input or missing credentials;
4. review low-confidence or policy-sensitive output;
5. recover a paused/failing run.

Store who approved what, the exact proposed arguments, time, scope, and post-approval changes. If arguments change materially, previous approval no longer applies.

## 14. Parallelism and concurrency

Parallelism reduces wall-clock time only for independent work. Control:

- maximum concurrent model/tool calls;
- provider and downstream rate limits;
- shared-state reducers and write conflicts;
- deterministic merge rules;
- cancellation when enough evidence exists;
- partial results and deadlines;
- duplicate work from retries/resumption.

Do not parallelize steps that mutate the same entity without version checks or transactions.

## 15. Termination and budgets

Every agent run should have explicit limits:

- maximum steps and repeated identical actions;
- wall-clock deadline and per-call timeout;
- input/output token limits;
- monetary budget;
- maximum tool calls and concurrency;
- maximum delegation/handoff depth;
- success, abstain, escalate, cancel, and failed terminal states.

A stop condition based only on the model saying “done” is insufficient.

## 16. Security model

Treat user input, retrieved documents, websites, tool output, and messages from other agents as untrusted data.

Key threats:

- direct and indirect prompt injection;
- tool argument injection and confused-deputy behavior;
- secret or cross-tenant data leakage;
- excessive agency/permissions;
- SSRF, unsafe browsing, shell/code execution;
- poisoned memory or retrieved content;
- unapproved external communication;
- denial of wallet through loops or large outputs.

Controls include least privilege, tenant filters before context construction, schema plus semantic validation, allowlists, sandboxing, egress restrictions, output encoding, secret isolation, human approval, and budget enforcement.

## 17. Observability and evaluation

Capture privacy-safe traces with:

- run/thread/step IDs and parent-child relationships;
- framework, model, prompt, tool, policy, and data versions;
- routes, handoffs, tool names, validation, and error categories;
- input/output token counts, cache usage, latency, retries, and cost;
- checkpoint/approval events and final outcome;
- redaction decisions rather than raw secrets.

Evaluate at several levels:

| Level | Examples |
|---|---|
| Task | success, correctness, completion, business outcome |
| Trajectory | valid route, necessary steps, loop/redundancy rate |
| Tool | selection, argument validity, result use, side-effect safety |
| Collaboration | handoff accuracy, context transfer, duplicate work |
| Safety | policy violations, unauthorized actions, data exposure |
| Operations | p50/p95 latency, cost, recovery, timeout, escalation rate |

## 18. Common interview traps

- Calling any chatbot an agent.
- Treating multi-agent architecture as automatically more capable.
- Adding retries without classifying errors or protecting writes.
- Confusing memory with replaying every prior message.
- Assuming JSON-valid arguments are business-valid or authorized.
- Letting a supervisor see every specialist’s full context.
- Reporting only final-answer quality and ignoring trajectory, latency, cost, and safety.
- Claiming deterministic output because temperature is zero.
- Persisting private reasoning instead of concise auditable decisions.

## 19. Rapid interview questions

**Q1. Agent versus workflow?**  
A workflow’s control flow is mostly code-defined; an agent lets a model select some actions or path at runtime. Many production systems combine both.

**Q2. Why not expose one generic API tool?**  
Narrow tools are easier to describe, authorize, validate, observe, and test, and they reduce prompt-injection and blast-radius risk.

**Q3. When use a supervisor?**  
When centralized routing, policy, synthesis, or accountability is valuable. Avoid it if it becomes a context and latency bottleneck.

**Q4. Handoff versus agent-as-tool?**  
A handoff transfers control; an agent-as-tool returns a bounded result while the caller retains control.

**Q5. How do you prevent loops?**  
Explicit terminal states, step/time/token/cost budgets, repeated-action detection, progress checks, and escalation.

**Q6. What makes a tool retry-safe?**  
Idempotency/deduplication, stable operation ID, bounded retry policy, observable status, and no unprotected duplicate side effects.

**Q7. Why separate state from model context?**  
State is authoritative execution data; context is a limited view selected for one model call. Separation improves cost, privacy, and control.

**Q8. When is long-term memory dangerous?**  
When unverified or malicious information is stored, scopes/tenants mix, retention is indefinite, or corrections/deletion are not supported.

## 20. Lead-level design case

**Prompt:** Design an agent that triages procurement requests, gathers policy evidence, drafts a recommendation, and can create an approval ticket.

A strong answer should:

1. define task outcomes, risk tiers, SLAs, and non-goals;
2. keep policy checks and permissions deterministic;
3. route standard cases through a bounded workflow and ambiguous cases to an agent;
4. expose read-only retrieval separately from ticket creation;
5. retrieve tenant-authorized, effective-date-correct policy evidence;
6. require approval for ticket creation or high-value recommendations;
7. use idempotency keys and checkpoint before the side effect;
8. bound loops, costs, and specialist handoffs;
9. evaluate route/tool/citation/abstention quality and business outcomes;
10. canary by risk tier with rollback to manual triage.

## 21. Final checklist

- [ ] I can distinguish deterministic workflows, bounded agents, and open-ended agents.
- [ ] I can explain router, supervisor, handoff, agent-as-tool, parallel, and evaluator patterns.
- [ ] I can design typed, authorized, idempotent tools.
- [ ] I separate state, context, short-term memory, and long-term memory.
- [ ] I can place human approval around consequential actions.
- [ ] I can explain budgets, termination, retry taxonomy, and concurrency control.
- [ ] I evaluate task, trajectory, tool, collaboration, safety, latency, and cost.
- [ ] I can justify why a multi-agent design is or is not needed.

## 22. Primary references

- Anthropic, [Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- Google Cloud, [Agent design patterns](https://cloud.google.com/architecture/choose-design-pattern-agentic-ai-system)
- OpenAI, [A practical guide to building agents](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/)
- LangChain, [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)
- Google, [Agent Development Kit documentation](https://google.github.io/adk-docs/)

Framework APIs change. Verify behavior against the pinned version before implementation.
