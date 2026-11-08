---
layout: week
week: 15
phase: 4
status: approved
version: 1.1.0
last_reviewed: 2026-11-08
estimated_hours: 8
permalink: /weeks/week-15/
title: "Make the control flow visible with LangGraph"
description: Build a typed, checkpointed procurement graph with explicit nodes, conditional edges, reducers, validation and report-bound human approval.
summary: Turn the Week 14 workflow into a real StateGraph, inspect every state update, pause safely for review and resume the same checkpointed thread.
kicker_primary: LangGraph fundamentals
kicker_secondary: State, routes, checkpoints and interrupts
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-15/beginner/
---

## A graph is executable control flow

Week 14 asked who chooses the next step. Week 15 makes that answer visible in a
graph. The application declares shared state, gives each unit of work a named
node and connects those nodes with fixed or conditional edges. LangGraph executes
the resulting program and can checkpoint it between steps.

This structure is useful when a process has several branches, may run for a long
time or must pause for external input. It does not make an unsafe design safe by
itself. You still own state contracts, permissions, business validation,
idempotency, timeouts, failure handling and the meaning of human approval.

The lab builds the exact roadmap flow:

1. classify the query;
2. retrieve contract evidence;
3. run SQL analysis;
4. calculate price variance;
5. generate a recommendation;
6. validate the report; and
7. interrupt for human approval.

It uses the real pinned LangGraph package but no model. Classification is a small
deterministic rule, retrieval is a local fixture and SQL runs against a disposable
in-memory SQLite table. This isolates graph mechanics from model quality and
provider availability.

If graphs are new, start with the [beginner version]({{ '/weeks/week-15/beginner/' | relative_url }}).
Read Week 14 first if the workflow-versus-agent distinction is not yet clear.

## Before you start

This route is for someone who already understands typed Python state, tool boundaries and why workflows own known transitions. It concentrates on LangGraph's executable state contract: reducers, closed routes, checkpoints, interrupts and same-thread resumption.

The core route is one supported and one unsupported trace, explicit reducer behavior, a checkpoint and a report-bound interrupt/resume. Treat durable checkpointers, concurrent updates, replay analysis and provider integration as stretch work rather than prerequisites.

The [Week 15 assessment]({{ '/assessments/week-15/' | relative_url }}) draws
10 balanced questions from a bank of 100, with explanations and browser Python
checks.

| Time | Focus | Evidence to retain |
| --- | --- | --- |
| Hour 1 | Map state, nodes and edges | One topology sketch |
| Hour 2 | Define typed state and reducers | Replacement and append examples |
| Hour 3 | Build fixed and conditional routes | Supported and unsupported traces |
| Hour 4 | Run document, SQL and exact price nodes | Two source identities and 10.00% math |
| Hour 5 | Validate and compile | One fail-closed validation result |
| Hour 6 | Checkpoint a thread | State snapshot and checkpoint count |
| Hour 7 | Interrupt and resume | Matching approve and reject runs |
| Hour 8 | Test failure boundaries | Wrong digest, wrong thread and interview answer |

## Start with the state contract

State is the current application snapshot. A node reads that snapshot and returns
a partial update. The framework applies an update according to the reducer for
each channel.

The lab uses a `TypedDict` so every node shares a visible contract. Scalar fields
such as `recommendation` use the default replacement behavior. Two list fields
use `operator.add` as a reducer:

~~~python
class InvestigationState(TypedDict, total=False):
    case_id: str
    query: str
    recommendation: Recommendation
    report_digest: str
    evidence: Annotated[list[str], add]
    trace: Annotated[list[str], add]
~~~

If one node returns `{"evidence": ["document:contract-1501-v1:found"]}` and a
later node returns `{"evidence": ["sql:price_analysis:PO-1501"]}`, the reducer
keeps both entries. A node need not copy the entire state.

Reducer choice is part of correctness:

| Channel | Update rule | Why |
| --- | --- | --- |
| `evidence` | append list items | retain all source identities |
| `trace` | append list items | retain ordered node outcomes |
| `recommendation` | replace | there is one current decision |
| `validation_errors` | replace | validation emits one complete result |
| `report_digest` | replace | bind review to one current snapshot |

An additive reducer does not clear when a node returns an empty list; adding
nothing leaves prior items in place. Use a deliberate overwrite or a different
state design when clearing is required. Do not use an append reducer for values
where duplicates would change meaning.

**Checkpoint:** Does a reducer prove evidence is valid? No. It describes how
updates combine. The validation node still checks source categories and fields.

## Nodes do work; edges own the route

The graph has eight named nodes:

| Node | Reads | Writes |
| --- | --- | --- |
| `classify_query` | case and query | intent and purchase-order ID |
| `unsupported_query` | classification | terminal trace |
| `retrieve_documents` | purchase-order ID | contract result and document evidence |
| `analyze_sql` | purchase-order ID | structured price row and SQL evidence |
| `calculate_price` | SQL analysis | exact absolute and percentage variance |
| `generate_recommendation` | variance, supplier, contract | recommendation and reason |
| `validate_report` | all required facts | canonical report, digest and validity |
| `human_approval` | validated report | approved/rejected status and reviewer |

Nodes return updates; they do not choose arbitrary destinations from text. Fixed
edges declare known dependencies. Conditional routing functions return one of a
small set of node names:

~~~python
def route_after_classification(state: InvestigationState) -> GraphRoute:
    if state.get("intent") == "procurement_price_investigation":
        return "retrieve_documents"
    return "unsupported_query"
~~~

The supported route is deliberately sequential. Document retrieval completes
before SQL analysis, followed by price math, recommendation and validation. A
future graph could execute independent reads in parallel, but only after defining
merge rules, cancellation, timeout and partial-failure behavior.

Run both branches:

~~~shell
python -m labs.week_15.demo run --case price-spike --thread supported-15
python -c "from labs.week_15.graph import GraphRuntime; print(GraphRuntime().start('price-spike', 'Write a poem.', thread_id='unsupported-15'))"
~~~

The unsupported request ends without document or SQL work. Classification is not
permission. If a later model replaces this rule, the route still needs a trusted
allowlist, current authorization and validation.

## Keep data operations ordinary and testable

LangGraph nodes are normal functions. Framework use does not require hiding
domain logic inside prompts.

The document node preserves a source identifier and whether the term was found.
The SQL node creates a local table and executes a bound query parameter. The price
node converts stored strings to `Decimal`, rejects a nonpositive reference and
uses `ROUND_HALF_EVEN` for two-place display.

For `PO-1501`:

$$
\text{variance} = \frac{2.20 - 2.00}{2.00} \times 100 = 10.00\%
$$

The dated reference and contract threshold produce `review_required`. `PO-1502`
produces `no_review`; `PO-1503` produces `needs_human` because its contract search
did not find the applicable term. Missing evidence never becomes a zero threshold
or permission to continue silently.

~~~shell
python -m labs.week_15.demo run --case stable-price --thread stable-15
python -m labs.week_15.demo run --case missing-terms --thread missing-15
~~~

Every supported case still pauses. A recommendation of `no_review` means the
business rule did not request additional procurement review; it does not grant
the software authority to accept an order.

## Validate before the human boundary

Compilation checks graph structure, such as whether referenced nodes exist. It
does not prove your report has every required fact. The lab therefore has an
application validation node.

It requires:

- a SQL analysis record;
- a contract-search result, including an explicit missing result;
- a known recommendation;
- a calculated variance;
- SQL evidence; and
- document evidence.

A valid state produces a canonical report and SHA-256 digest. An invalid state
routes directly to `END` with `validation_failed`; it never reaches approval.

The digest is calculated over sorted compact JSON. It detects whether the report
resumed for approval differs from the one displayed. It is not a signature,
identity proof or authorization check.

## Compile with a checkpointer

A `StateGraph` becomes runnable only after compilation. The lab injects an
`InMemorySaver`:

~~~python
checkpointer = InMemorySaver()
graph = builder.compile(
    checkpointer=checkpointer,
    name="week_15_procurement",
)
~~~

Each invocation supplies a `thread_id` in the configurable runtime data. The
checkpointer stores successive snapshots under that thread. Reusing the ID lets
the runtime find the paused state; a different ID points somewhere else.

The lab rejects blank IDs, IDs over 200 characters, duplicate starts and resume
attempts when the thread is not waiting at an interrupt. Those checks make the
teaching API deterministic. They do not authenticate a caller.

`InMemorySaver` is process memory. It survives multiple calls to the same
`GraphRuntime` instance but disappears when Python exits. The `run` command can
show a pause, while `resume-demo` pauses and resumes in one process:

~~~shell
python -m labs.week_15.demo resume-demo --case price-spike --decision approve
python -m labs.week_15.demo resume-demo --case price-spike --decision reject
~~~

Production recovery needs a durable supported checkpointer plus schema migration,
retention, encryption, backup, concurrency and ownership decisions. Do not call
an in-memory demo “durable” merely because its API uses checkpoints.

## Interrupt once, then resume the same thread

The approval node calls `interrupt()` with a JSON-safe payload. Execution pauses,
the checkpoint records where it stopped and the caller receives the payload under
`__interrupt__` when using `invoke()`.

~~~python
response = interrupt(
    {
        "kind": "human_approval",
        "report": report,
        "report_digest": digest,
        "allowed_decisions": ["approve", "reject"],
    },
    response_schema=ApprovalResponse,
)
~~~

Resume passes a `Command` with external input and the same configuration:

~~~python
final = graph.invoke(
    Command(resume={
        "decision": "approve",
        "reviewer": "reviewer-15",
        "report_digest": digest,
    }),
    config={"configurable": {"thread_id": thread_id}},
)
~~~

The response schema helps a client render and validate fields. The node validates
decision, reviewer and digest again because host input crosses a trust boundary.

There is one subtle rule: when resumed, the interrupted node starts again from
its beginning. Code before `interrupt()` may run more than once. Keep that region
deterministic and side-effect free. If a node must send email, charge money or
write a durable record, separate proposal, approval and idempotent execution;
never perform the effect before the interrupt.

## Persistence is not all one thing

Distinguish three concerns:

| Concern | Scope | Lab choice |
| --- | --- | --- |
| Graph checkpoint | node progress and thread state | `InMemorySaver` |
| Business record | accepted investigation and audit history | not implemented |
| Long-term memory | facts shared across future threads | deferred to Week 16 |

A checkpoint can resume execution without being the system of record. Conversely,
a business database can store a report without knowing which graph node should
run next. Keep lifecycle, retention and access policies explicit for both.

## Test the graph as a program

Do not stop at “the graph ran once.” Tests should cover topology and state
transitions as well as final text.

The focused suite proves:

- exact node presence and important edges;
- supported and unsupported conditional routes;
- reducer ordering for document and SQL evidence;
- all three recommendation outcomes;
- the typed interrupt payload and checkpoint snapshot;
- approve and reject resume on the same thread;
- wrong-digest and wrong-thread rejection;
- isolation between two threads;
- fail-closed report validation;
- parameterized SQL behavior; and
- machine-readable CLI smoke.

Run the gates:

~~~shell
python -m pip install -r requirements-dev.txt -r labs/week_15/requirements.txt
python -m labs.week_15.demo smoke
python -m pytest tests/test_week15_langgraph.py -q
python -m ruff check labs/week_15 tests/test_week15_langgraph.py
python -m ruff format --check labs/week_15 tests/test_week15_langgraph.py
python -m mypy --strict --explicit-package-bases labs/week_15 tests/test_week15_langgraph.py
~~~

## Know what the graph does not guarantee

### A compiled route is not a correct business policy

Compilation catches structural mistakes. Tests and review must establish whether
the transition, threshold and terminal status are right.

### A thread ID is not identity

Treat it as a checkpoint cursor. Authenticate the caller and authorize access to
the case separately. Use unguessable scoped identifiers where appropriate.

### A checkpoint is not permanent by default

The in-memory saver loses state at process exit. Durable backends still need
operations, migrations and retention.

### An interrupt is not approval

An interrupt only pauses. Approval exists only after trusted input is validated,
bound to the reviewed snapshot and recorded with the required authority.

### A reducer is not conflict resolution

Appending two values may preserve both while leaving a semantic conflict. Define
ownership and merge policy for parallel writers.

### A graph can still loop

Conditional edges may create cycles. Bound retries and steps, classify terminal
failures and test recursion behavior. This lab is acyclic except for interrupt
resume.

### Framework visibility is not observability

Named nodes improve trace structure, but production still needs correlated logs,
metrics, redaction, failure categories and alert ownership.

## When is a graph more reliable than an unrestricted agent loop?

A graph can be more reliable when the valid lifecycle is expressible as reviewed
state transitions. Named nodes narrow responsibility, typed state makes required
facts inspectable, conditional edges limit destinations, deterministic validation
guards terminal transitions, checkpoints preserve progress and interrupts place a
human before consequential work.

The improvement comes from those explicit contracts and their tests—not from the
word “graph.” A graph with permissive state, unbounded cycles, unsafe nodes and no
failure policy can be less reliable than a small ordinary function.

A concise interview answer:

> I use graph orchestration when the process has meaningful state, branches,
> pauses or recovery needs that benefit from explicit transitions. I keep stable
> business rules in deterministic nodes, constrain conditional routes, validate
> before terminal states, checkpoint by an authorized case/thread identity and
> make pre-interrupt code replay-safe. Compared with an unrestricted agent loop,
> that gives me a finite topology and testable invariants. I still evaluate any
> model-driven node separately and operate persistence, concurrency and approval
> as real system boundaries.

## Independent exercises

1. Add a `supplier-inactive` fixture and prove the recommendation remains
   `review_required` even when variance is below the threshold.
2. Add a clarification node for a missing purchase-order ID. Decide whether it
   should interrupt or terminate with a structured request.
3. Parallelize document and SQL reads. Define reducer, join, timeout and
   partial-failure behavior before editing the edges.
4. Add an invalid human response route that re-prompts using one interrupt per
   node invocation rather than a `while True` loop inside the node.
5. Replace `InMemorySaver` with a local durable checkpointer in a private branch.
   Test process restart, migration and cleanup.
6. Add idempotent post-approval recording keyed by report digest and decision.
   Simulate a lost response and prove replay does not duplicate the record.
7. Replace deterministic classification with a structured model adapter. Keep
   the route allowlist and evaluate classification on labelled queries.
8. Add state redaction to a debug projection so checkpoint inspection does not
   expose confidential fields.

## Finish with evidence

You are done when you can name every state channel, reducer, node, fixed edge,
conditional destination and terminal state. You should be able to show the
checkpoint before approval, resume only the matching thread, reject a changed
report and explain why in-memory persistence is not production durability.

Week 16 will separate working graph state from longer-lived case memory, context
selection, summarisation, expiry and incorrect-memory prevention.

Use the [Week 15 assessment]({{ '/assessments/week-15/' | relative_url }}) to
practise state contracts, routes, reducers, checkpoint boundaries, interrupts
and report-bound resumption before moving to memory engineering.

## Sources and further reading

- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)
  positions LangGraph as a low-level orchestration runtime that can mix
  deterministic and model-driven steps.
- [Graph API overview](https://docs.langchain.com/oss/python/langgraph/graph-api)
  documents `StateGraph`, state schemas, reducers, nodes, normal edges,
  conditional edges and compilation.
- [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
  distinguishes thread-scoped checkpointers from cross-thread stores and notes
  that in-memory savers do not survive process restarts.
- [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
  documents `interrupt()`, `thread_id`, `Command(resume=...)`, response schemas
  and the rule that an interrupted node restarts when resumed.
- [LangGraph 1.2.19 on PyPI](https://pypi.org/project/langgraph/1.2.19/)
  is the exact version pinned by this lab.
- [Python `sqlite3`](https://docs.python.org/3/library/sqlite3.html) and
  [`decimal`](https://docs.python.org/3/library/decimal.html) document the local
  parameterized query and exact arithmetic primitives used by the fixtures.

