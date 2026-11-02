---
layout: week
week: 15
phase: 4
status: approved
version: 1.0.0
last_reviewed: 2026-11-02
estimated_hours: 8
permalink: /weeks/week-15/beginner/
title: "Build your first stateful graph"
description: Learn LangGraph through a small procurement investigation that remembers its work, follows visible routes and pauses for a person.
summary: Treat state as a case folder, nodes as workstations, edges as arrows and a checkpoint as a saved place before human approval.
kicker_primary: Beginner path
kicker_secondary: Follow one case through the graph
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-15/
---

## Think of a case moving through workstations

Imagine a paper folder for a price investigation. It visits several desks:

1. reception decides whether the request belongs here;
2. contracts finds the relevant document;
3. analytics reads price rows;
4. finance calculates the change;
5. policy recommends the next step;
6. quality checks that the folder is complete; and
7. a reviewer accepts or rejects the report.

That is the mental model for this week’s graph.

| Graph word | Simple meaning |
| --- | --- |
| State | The case folder and everything currently known |
| Node | One workstation that reads the folder and adds a result |
| Edge | An arrow saying which workstation comes next |
| Conditional edge | A choice between named arrows |
| Reducer | A rule for combining a new update with an old value |
| Checkpoint | A saved snapshot of the folder and current place |
| Interrupt | A safe pause while the program waits for input |
| Resume | Continue the same saved case with that input |

The [production version]({{ '/weeks/week-15/' | relative_url }}) adds deeper
design, persistence and testing guidance. Start here if the vocabulary is new.

## See the route before reading code

The lab follows this route:

~~~text
classify query
  ├─ unsupported → end
  └─ supported → retrieve contract
                → analyze SQL
                → calculate price
                → recommend
                → validate report
                    ├─ invalid → end failed
                    └─ valid → pause for human
                                 → approve or reject
~~~

Unlike an unrestricted agent loop, the graph cannot invent a new destination.
The application has declared the nodes and edges in advance.

## Install and run the first case

From the repository root:

~~~shell
python -m pip install -r requirements-dev.txt -r labs/week_15/requirements.txt
python -m labs.week_15.demo run --case price-spike --thread first-week15
~~~

The output should contain:

- `status: awaiting_approval`;
- `recommendation: review_required`;
- a 64-character `report_digest`;
- two evidence entries;
- six completed trace entries; and
- an `interrupt` asking a person to accept the report.

Nothing was sent to a supplier and no order was approved. The program only built
a fictional report and paused.

## State is the case folder

At first, state contains the case ID, query and two empty lists. Each node returns
only what it learned.

After classification, state has a purchase-order ID. After document retrieval,
it has contract evidence. After SQL analysis, it has price facts. Later nodes add
the variance, recommendation, report and digest.

The node does not need to copy every old field:

~~~python
def calculate_price(state):
    # read prices from state
    return {
        "variance_percent": "10.00",
        "trace": ["calculate_price:10.00%"],
    }
~~~

LangGraph applies this small update to the existing state.

## Reducers decide how updates combine

Most values are replaced. If a node returns a new `recommendation`, that becomes
the current recommendation.

Lists such as `evidence` are different. The lab marks them with an addition
reducer. The document node adds one item and the SQL node adds another:

~~~text
document:contract-1501-v1:found
sql:price_analysis:PO-1501
~~~

The list keeps both. A reducer is simply a combine rule. It does not prove either
item is true, so the validation node still checks the folder.

## Nodes and edges have different jobs

A node does work. An edge says where control goes next.

The classifier node writes one of two intents. A conditional edge reads that
intent:

- a procurement price investigation goes to document retrieval;
- anything else goes to the unsupported terminal node.

Try the unsupported route:

~~~shell
python -c "from labs.week_15.graph import GraphRuntime; print(GraphRuntime().start('price-spike', 'Write a poem.', thread_id='poem'))"
~~~

It ends after classification. There is no document evidence, SQL analysis or
approval interrupt.

## Follow the three business outcomes

The fixture has three cases:

| Command case | Result | Why |
| --- | --- | --- |
| `price-spike` | `review_required` | 10.00% is above 5.00% |
| `stable-price` | `no_review` | 2.00% is within 5.00% |
| `missing-terms` | `needs_human` | the contract threshold was not found |

Run them:

~~~shell
python -m labs.week_15.demo run --case price-spike --thread spike
python -m labs.week_15.demo run --case stable-price --thread stable
python -m labs.week_15.demo run --case missing-terms --thread missing
~~~

All three pause for a person. `no_review` is a recommendation from one rule, not
permission for the software to act.

## A checkpoint saves your place

The graph is compiled with `InMemorySaver`. After each step, LangGraph can save a
snapshot under a `thread_id`.

Think of `thread_id` as the label on the case folder. Resume with the same label
and the runtime can find the pause. Use a different label and it cannot.

Important limits:

- the label is not a username or password;
- memory disappears when the Python process ends;
- a production system needs durable storage and access control; and
- old checkpoints need a retention policy.

The lab prevents two new cases from starting with the same ID because mixing case
histories would be confusing and unsafe.

## An interrupt pauses before a decision

The approval node calls `interrupt()`. It sends the caller a report, the report
digest and the allowed decisions. The graph stops there.

Run a complete pause and approve in one process:

~~~shell
python -m labs.week_15.demo resume-demo --case price-spike --decision approve
~~~

Then reject it:

~~~shell
python -m labs.week_15.demo resume-demo --case price-spike --decision reject
~~~

The resume input contains:

- `decision`: `approve` or `reject`;
- `reviewer`: a nonblank local demo name; and
- `report_digest`: the digest shown at the pause.

If the digest changes, the lab rejects the decision. This prevents a decision for
one report being silently applied to another report. It does not prove who the
reviewer is; real identity and permission checks would be separate.

## Why code before an interrupt must be safe to repeat

When LangGraph resumes, it starts the interrupted node again. Work before the
interrupt may run twice.

The lab only constructs a dictionary before pausing. That is safe. A bad node
would send an email, then interrupt for permission; resuming could send the email
again. The correct order is:

1. prepare and display the proposed action;
2. pause;
3. validate the reviewer response; and
4. perform an idempotent effect afterward, if the application is authorized.

This lab has no external effect at all.

## Validation is a separate workstation

The graph does not ask a person to review an incomplete folder. The validation
node requires SQL facts, contract-search facts, variance, recommendation and both
evidence types.

If something is absent, it writes `validation_failed` and routes to the end.
Compiling the graph cannot discover a missing business fact; application checks
must do that work.

## Test more than the happy path

Run:

~~~shell
python -m labs.week_15.demo smoke
python -m pytest tests/test_week15_langgraph.py -q
~~~

The tests check:

- the graph’s nodes and arrows;
- the three recommendation branches;
- evidence-list reducer order;
- the approval pause and response schema;
- checkpoint creation;
- approve and reject;
- a changed report digest;
- a different thread ID;
- two isolated threads;
- an unsupported query;
- incomplete report validation; and
- parameterized SQL.

Testing only the final sentence would miss most graph failures.

## Avoid these beginner mistakes

1. **Putting every value in one message list.** Use named fields for facts with
   known types and business meaning.
2. **Letting a node return any next node name.** Keep destinations small and
   explicit.
3. **Using append for everything.** Choose replacement or a custom reducer based
   on the field’s meaning.
4. **Calling `thread_id` authentication.** It only selects checkpoint state.
5. **Calling memory durable.** `InMemorySaver` is lost at process exit.
6. **Doing the effect before approval.** Pause first and make later execution
   idempotent.
7. **Treating missing documents as “no restriction.”** Preserve missing evidence
   and ask a person.
8. **Assuming a framework removes loops.** A conditional edge can still point
   backward; limits and tests remain necessary.

## Practice questions

1. What information belongs in graph state?
2. What is the difference between a node and an edge?
3. Why does `evidence` use an additive reducer?
4. Why does `recommendation` use replacement instead?
5. Which two routes can follow query classification?
6. What does a checkpoint remember?
7. Why must resume use the same thread ID?
8. Why is thread ID not authentication?
9. What does the report digest protect?
10. Why must work before an interrupt be safe to repeat?
11. Why does `missing-terms` become `needs_human`?
12. When might an ordinary function be simpler than a graph?

You are ready when you can draw the route, explain each state update, show the
pause and resume the same thread without confusing a checkpoint with identity or
permanent storage.

## Read alongside the lab

- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)
  introduces the framework and a small `StateGraph`.
- [Graph API overview](https://docs.langchain.com/oss/python/langgraph/graph-api)
  explains state, reducers, nodes, edges and compilation.
- [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
  explains checkpointers, thread IDs and the limits of in-memory storage.
- [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
  explains how a graph pauses and resumes with `Command`.

These sources explain framework behavior. The procurement facts and decisions in
this lesson are fictional teaching fixtures, not production or provider results.

