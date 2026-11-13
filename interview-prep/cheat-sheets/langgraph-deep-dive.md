---
layout: "week"
status: "approved"
version: "1.0.1"
last_reviewed: "2026-11-13"
header_context: "Interview cheat sheets"
back_label: "Cheat sheets"
back_url: "/cheat-sheets/"
toc_heading: "Cheat-sheet sections"
pagination_label: "Cheat sheets hub"
pagination_url: "/cheat-sheets/"
title: "LangGraph deep-dive interview cheat sheet"
description: "StateGraph, nodes, edges, reducers, commands, fan-out, persistence, interrupts, durable execution, streaming, caching, and testing."
summary: "Revise typed state, reducers, routing, Command and Send, checkpoints, stores, human-in-the-loop, replay-safe side effects, and production validation."
permalink: "/interview-prep/cheat-sheets/langgraph-deep-dive/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 4 · LangGraph"
current_label: "Revision guide"
alternate_label: "Cheat sheets hub"
alternate_url: "/cheat-sheets/"
---
> **Batch 4 source:** This page integrates the prepared revision artifact into the Prep site. It is separate from the Week 1–30 learning assessments.

**Target roles:** Agentic AI Engineer, LangGraph Developer, AI Engineer, ML Engineer, Senior/Lead Data Scientist  
**Use:** graph design, state, persistence, human-in-the-loop, recovery, streaming, caching, and testing  
**Interview rule:** LangGraph is an orchestration runtime for long-running, stateful workflows and agents. It does not replace model selection, tool security, evaluation, or application APIs.

## 1. Thirty-second revision

- A LangGraph application is a graph of nodes connected by fixed or conditional edges over typed shared state.
- A node reads state/runtime context and returns a **partial state update**; reducers define how updates are combined.
- `StateGraph` makes control flow explicit while still allowing model-driven routing.
- `Command` can combine a state update with routing; `Send` supports dynamic fan-out to worker tasks.
- A checkpointer persists thread-scoped graph state at execution boundaries. A store holds application-defined long-term data across threads.
- `thread_id` identifies a persistent execution/conversation; it is not the user ID or authorization boundary.
- `interrupt()` pauses for external input. Resumption restarts the interrupted node, so work before the interrupt must be idempotent or moved after it.
- Durable execution still requires side-effect discipline: deterministic/idempotent tasks, operation IDs, and safe replay.
- Streaming improves responsiveness and observability but does not reduce total compute automatically.
- Node result caching, checkpointing, model/provider prompt caching, and semantic response caching solve different problems.

## 2. When LangGraph fits

Use it when the application needs several of:

- explicit branching, cycles, or dynamic fan-out;
- long-running, resumable execution;
- state shared across model/tool nodes;
- human approval or clarification;
- checkpointing, replay, or time-travel debugging;
- multi-agent subgraphs and handoffs;
- fine-grained streaming and observability.

A direct model call, a simple function pipeline, or a task queue may be better for a short acyclic flow with no persistent state.

## 3. Mental model

| Primitive | Meaning | Interview example |
|---|---|---|
| State schema | Authoritative fields carried through the graph | messages, order ID, evidence, attempt count |
| Node | Unit of computation returning state updates | classify, retrieve, call tool, approve |
| Edge | Fixed transition | validate → respond |
| Conditional edge | Runtime route chosen from state | approved → execute; rejected → revise |
| Reducer | Combines multiple/previous updates for a field | append messages; merge worker results |
| Checkpointer | Persists thread snapshots | resume after human approval or failure |
| Store | Cross-thread application memory | user preference or verified fact |
| Subgraph | Reusable graph nested in a parent | research specialist |
| Runtime context | Dependencies not meant to be persistent state | database client, tenant context, feature flags |

Think in state transitions: for each node define inputs, outputs, possible failures, retry safety, and next state.

## 4. Minimal typed graph

```python
from __future__ import annotations

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class TicketState(TypedDict, total=False):
    text: str
    category: Literal["billing", "technical", "other"]
    answer: str


def classify(state: TicketState) -> dict[str, str]:
    text = state["text"].lower()
    category = "billing" if "invoice" in text else "technical"
    return {"category": category}


def route(state: TicketState) -> str:
    return state["category"]


def billing(state: TicketState) -> dict[str, str]:
    return {"answer": "Route to billing operations."}


def technical(state: TicketState) -> dict[str, str]:
    return {"answer": "Start technical diagnostics."}


builder = StateGraph(TicketState)
builder.add_node("classify", classify)
builder.add_node("billing", billing)
builder.add_node("technical", technical)
builder.add_edge(START, "classify")
builder.add_conditional_edges(
    "classify",
    route,
    {"billing": "billing", "technical": "technical"},
)
builder.add_edge("billing", END)
builder.add_edge("technical", END)
graph = builder.compile()
```

This code is illustrative; pin LangGraph and verify imports/API behavior for that version.

## 5. State schema design

Store raw, authoritative data—not formatted prompts that become difficult to reuse.

Good state fields:

- stable IDs and statuses;
- structured tool results or references;
- normalized decisions and validation errors;
- budgets/attempt counters;
- approval and checkpoint metadata;
- selected messages/evidence needed downstream.

Avoid:

- database clients, sockets, or secrets in persistent state;
- duplicate derivable values without a source of truth;
- entire large documents when IDs/URIs suffice;
- one untyped `dict[str, Any]` containing everything;
- user/tenant identity without independent authorization checks.

TypedDict is lightweight; dataclasses or Pydantic models can add defaults/validation depending on version and requirements. Runtime dependencies belong in runtime context or dependency injection rather than checkpointed business state.

## 6. Partial updates and reducers

A node usually returns only changed fields. This is sometimes informally called a **delta update**.

```python
import operator
from typing import Annotated, TypedDict


class ResearchState(TypedDict):
    query: str
    findings: Annotated[list[str], operator.add]
```

If parallel nodes return `{"findings": [...]}`, the reducer concatenates the lists. Without an appropriate reducer, concurrent writes to the same channel can conflict or overwrite.

Important: returning state deltas does **not by itself** save model tokens. Tokens fall only when the context builder sends less content, summaries replace history, retrieval is selective, or provider/model caching applies.

### Reducer rules

- Choose associative, predictable merge behavior for parallel updates.
- Define overwrite versus append explicitly.
- Avoid mutable shared objects.
- Deduplicate when retries could repeat an update.
- Test order sensitivity; parallel completion order may vary.
- Keep business invariants outside a naive list concatenation.

## 7. Messages and message reducers

Conversation agents often use a message list with a message-aware reducer. The reducer should preserve IDs and support updates/replacements when required, rather than blindly appending duplicates.

Separate:

- durable conversation record;
- summarized/selected context for the next model call;
- tool audit events;
- private application metadata.

Do not assume every message should be presented to every node or specialist.

## 8. Nodes and edges

Good nodes are cohesive and testable. A node boundary is useful when it adds one of:

- a checkpoint/recovery boundary;
- a distinct retry or timeout policy;
- a separate security/approval decision;
- a reusable responsibility;
- useful trace visibility;
- an independent parallel task.

Too many tiny nodes add orchestration overhead; one giant node hides state transitions and makes recovery coarse.

Conditional edges should route from explicit state such as a validated enum. Avoid letting arbitrary model text become a node name.

## 9. `Command`: update and route together

`Command` is useful when a node must both update state and choose the next node—for example, a specialist handoff.

Conceptually:

```python
from langgraph.types import Command


def decide(state: TicketState) -> Command[Literal["billing", "technical"]]:
    destination = "billing" if state["category"] == "billing" else "technical"
    return Command(update={"answer": "Routed"}, goto=destination)
```

Use explicit route types and validate model-generated destinations. A `Command` is orchestration, not authorization.

## 10. `Send`: dynamic fan-out

`Send` supports creating a variable number of worker tasks at runtime, such as one worker per document or research question. Workers return updates merged through reducers.

Design questions:

- How many workers can be created?
- What is the per-worker and overall deadline?
- How are results deduplicated and ordered?
- Can the reducer tolerate partial failure?
- When can remaining work be cancelled?
- Which state fields are safe to expose to each worker?

Dynamic fan-out without concurrency and cost caps creates denial-of-wallet risk.

## 11. Checkpoints, threads, and stores

### Checkpointer

Persists snapshots of a thread’s graph state so an execution can continue after a failure, pause, or new turn. Checkpoints also support history inspection and replay/time-travel workflows.

### Thread

A sequence of checkpoints identified by `thread_id`. Reusing a thread ID loads the same thread; a new ID starts a new one.

### Store

Persists application-defined data across threads, such as verified preferences or shared knowledge.

| Need | Mechanism |
|---|---|
| Resume the same run/conversation | Checkpointer + thread ID |
| Inspect prior graph states | Checkpoint history |
| Remember a verified preference across conversations | Store |
| Cache a repeated expensive node result | Cache |
| Authenticate or isolate a user/tenant | Application identity and authorization—not thread ID |

Use durable production backends, retention/deletion policies, encryption, tenant isolation, schema/version migration, and backup/recovery appropriate to the data.

## 12. Interrupts and human-in-the-loop

`interrupt()` can pause a node and surface a JSON-serializable payload. The caller later resumes the graph with a `Command` containing the response.

Critical execution rule: resuming restarts the node from its beginning. Therefore:

- place side effects after the interrupt where practical;
- make pre-interrupt work idempotent;
- do not swallow the graph’s interrupt signal in a broad exception handler;
- keep interrupt order stable if a node has more than one;
- persist the exact proposal being approved;
- re-approve if material arguments change.

Conceptual flow:

```python
from langgraph.types import interrupt


def approval_node(state: dict[str, object]) -> dict[str, object]:
    decision = interrupt(
        {
            "action": "send_email",
            "recipient": state["recipient"],
            "preview": state["draft"],
        }
    )
    return {"approved": bool(decision)}
```

## 13. Durable execution and replay safety

Durability means the runtime can resume stateful execution; it does not make external actions exactly once.

For side-effecting nodes:

1. generate a stable operation/idempotency key from the business action;
2. record intent/status transactionally where possible;
3. call the external service with the key;
4. reconcile unknown outcomes before retrying;
5. store the external result/reference;
6. make repeated execution return the same result or safe status.

Keep nondeterministic work—current time, random IDs, external calls—inside controlled tasks or persist its result so replay does not silently change decisions.

## 14. Subgraphs and multi-agent systems

A subgraph encapsulates a reusable workflow or specialist. Decide how it shares state:

- common state keys for tightly coupled parent/child graphs;
- explicit adapters for isolated schemas;
- per-invocation persistence for one-off work;
- per-thread persistence when a specialist needs conversational memory.

Benefits: isolation, reuse, team ownership, separate testing. Costs: nested traces, state mapping, persistence choices, and error propagation.

Do not make every node a “multi-agent” system. A specialist should have a clear contract, distinct responsibility, and bounded context.

## 15. Streaming

Depending on the API/version, LangGraph can stream state updates, values, model messages/tokens, custom progress, and debug/events.

Use streaming to:

- show early tokens or stage progress;
- surface interrupt/approval requests;
- emit tool and workflow status;
- observe long-running work;
- support cancellation.

Production concerns:

- backpressure and slow/disconnected clients;
- event ordering and reconnect cursor;
- duplicate events after retries;
- redaction of tool arguments/state;
- final durable status separate from transient UI events.

## 16. Node caching versus other caches

| Mechanism | Stores | Key purpose |
|---|---|---|
| Checkpoint | Thread execution state | resume, memory, recovery, history |
| Node result cache | Output for equivalent node inputs | skip repeated computation |
| Provider prompt/prefix cache | Reused model input prefix computation | reduce model latency/cost where supported |
| Semantic response cache | Prior answer for similar meaning | avoid a model call with quality/privacy trade-offs |
| Retrieval cache | Query/retrieval result | reduce search latency/load |

A node cache needs a safe key, namespace/version, TTL, tenant scope, invalidation, and rules for nondeterminism. Never cache a mutating node merely because it is expensive.

Good cache keys include normalized relevant inputs plus model/prompt/tool/data/policy versions. Exclude unstable noise, but never omit a field that changes correctness or authorization.

## 17. Retries and error handling

Separate failures:

- **Transient infrastructure:** retry with bounded exponential backoff and jitter.
- **Model-fixable:** return structured feedback to a bounded correction loop.
- **User-fixable:** interrupt for missing/ambiguous input.
- **Business rejection:** route to an explicit terminal/review state.
- **Unexpected defect:** let it surface to the runtime, preserve the checkpoint, and alert.

Attach retry policies to the smallest safe unit. Retrying a composite node may repeat successful side effects.

## 18. Time travel, replay, and debugging

Checkpoint history helps inspect prior states, fork from a checkpoint, reproduce a decision, or correct state and resume. This is powerful but requires:

- exact model/prompt/tool/data versions;
- clear distinction between replay and new execution;
- no automatic repetition of irreversible side effects;
- audit records for manual state edits;
- retention and privacy controls.

Replay with a changed model or live external data is a new experiment, not exact reproduction.

## 19. Graph evolution and deployment

Long-running threads may outlive a code release. Plan for:

- backward-compatible state additions/defaults;
- migration of renamed/removed fields;
- nodes renamed or removed while old checkpoints reference them;
- prompt/model/tool version pinning;
- drain, migrate, or restart policies for active threads;
- canary deployments and rollback compatibility.

Treat state schemas and node names as persistent contracts once executions can survive deployments.

## 20. Testing strategy

### Unit tests

- call nodes with small typed states;
- test routing functions and reducers deterministically;
- validate tool arguments, budgets, and error mapping.

### Graph integration tests

- use fake models/tools and an in-memory checkpointer;
- assert visited nodes and final state;
- exercise each branch, loop limit, retry, and partial failure.

### Persistence/HITL tests

- pause, reconstruct the graph/runtime, and resume using the same thread;
- verify the node re-executes safely;
- test duplicate resume and expired/invalid approval.

### Evaluation/release tests

- replay a versioned scenario set;
- compare task, trajectory, latency, token, cost, and safety metrics;
- canary with shadow or restricted-risk traffic.

Prefer state/trajectory assertions over exact natural-language equality.

## 21. Common interview traps

- Saying a reducer automatically reduces tokens.
- Treating a checkpointer as long-term semantic memory or a cache.
- Using `thread_id` as authentication or tenant isolation.
- Assuming interrupt resumes at the next source-code line.
- Retrying nodes with unprotected writes.
- Putting clients/secrets/huge documents into persistent state.
- Using dynamic fan-out without concurrency or cost limits.
- Claiming replay is deterministic while model, prompt, or external data changed.
- Building a graph when a small deterministic function is sufficient.

## 22. Rapid interview questions

**Q1. Why does LangGraph use reducers?**  
To define how a state field combines updates, especially when multiple nodes or parallel workers write it.

**Q2. Partial update versus full state?**  
A node normally returns only changed fields; the runtime merges them according to state channels/reducers.

**Q3. Checkpointer versus store?**  
Checkpointers persist thread-scoped execution snapshots; stores hold application data that can span threads.

**Q4. Why can an interrupt duplicate work?**  
Resumption restarts the node, so code before `interrupt()` runs again.

**Q5. `Command` versus conditional edge?**  
Both can route. `Command` is convenient when the node also updates state or performs a handoff; conditional edges keep routing separate.

**Q6. When use `Send`?**  
For runtime-determined fan-out such as map–reduce, with reducers and strict concurrency/cost controls.

**Q7. Does checkpointing guarantee exactly-once tool execution?**  
No. External side effects need idempotency, deduplication, reconciliation, or compensation.

**Q8. How would you shrink token use?**  
Select context from state, summarize, retrieve only relevant items, compact tool outputs, and use appropriate caches; state deltas alone do not change prompt size.

## 23. Lead-level design case

**Prompt:** Build a LangGraph research-and-approval workflow that searches internal sources, produces a cited recommendation, and may create a procurement ticket.

A strong design:

1. defines typed state for goal, tenant, plan, findings, citations, budgets, draft, approval, and operation status;
2. separates plan, parallel research, reduce/rerank, draft, validate, approve, and execute nodes;
3. uses `Send` only for bounded independent research tasks and a deterministic reducer;
4. checkpoints before approval and before/after the external write;
5. uses an interrupt with exact ticket preview and immutable approval reference;
6. makes ticket creation idempotent and reconciles unknown outcomes;
7. stores long-term verified preferences separately from thread state;
8. streams progress without exposing secrets or raw private reasoning;
9. tests branch/loop/partial-failure/resume behavior with fake tools;
10. versions state, prompts, tools, model, corpus, and policy for replay and rollback.

## 24. Final checklist

- [ ] I can draw a state graph with nodes, edges, routes, loops, and terminal states.
- [ ] I can design state schemas and reducers for sequential and parallel updates.
- [ ] I understand `Command`, `Send`, subgraphs, and runtime context.
- [ ] I can distinguish checkpoints, threads, stores, and caches.
- [ ] I know why interrupts and durable execution require idempotency.
- [ ] I can design streaming, retry, timeout, and cancellation behavior.
- [ ] I can test nodes, routes, reducers, graph trajectories, persistence, and HITL.
- [ ] I can plan state/graph migrations across deployments.

## 25. Primary references

- LangChain, [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)
- LangChain, [Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)
- LangChain, [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- LangChain, [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
- LangChain, [Streaming](https://docs.langchain.com/oss/python/langgraph/streaming)
- LangChain, [Thinking in LangGraph](https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph)

APIs and import paths are version-sensitive. Verify examples against the pinned LangGraph release.
