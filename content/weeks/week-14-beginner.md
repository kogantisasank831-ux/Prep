---
layout: week
week: 14
phase: 4
status: approved
version: 1.0.2
last_reviewed: 2026-11-02
estimated_hours: 8
permalink: /weeks/week-14/beginner/
title: "Workflows and agents, one step at a time"
description: Learn who chooses the next step, then run the same procurement investigation as a fixed workflow and a bounded agent.
summary: Start with a recipe, add a planner only where the route is uncertain, and keep tools, limits and human approval under application control.
kicker_primary: Beginner path
kicker_secondary: Who chooses what happens next?
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-14/
---

## Start with a recipe

Imagine checking a price increase. You always need to:

1. open the purchase order;
2. find the supplier;
3. find a reference price;
4. calculate the percentage change;
5. read the contract limit; and
6. show the result to a person.

That is a workflow. The application already knows the order of the steps.

Now imagine the request is vague: “Investigate what went wrong with this supplier.” You may need a purchase-order tool, a document search, delivery records or a question back to the user. The best next step depends on what you discover. An agent can ask a model to propose that next step.

The key difference is simple:

| Controller | Who chooses the next step? |
| --- | --- |
| Workflow | Application code |
| Agent | A planner proposes it; application code checks and executes it |

This week builds both versions over the same fictional data. There is no model download or API key. A scripted planner stands in for a model so you can see correct routes, wrong routes and loops every time.

The [production version]({{ '/weeks/week-14/' | relative_url }}) adds deeper design and evaluation guidance. Use this version to build the mental model first.

The [Week 14 assessment]({{ '/assessments/week-14/' | relative_url }}) draws 10 balanced questions from a bank of 100, with explanations and browser Python checks.

## Know the shared task

The example purchase order is `PO-1401`:

- current price: USD 2.20/kg;
- dated reference price: USD 2.00/kg;
- calculated increase: 10.00%; and
- contract review limit: 5.00%.

Because 10.00% is above 5.00%, the report recommends `review_required`. It still waits for a human. The program does not approve an order, contact a supplier or make a payment.

Both controllers use exactly the same facts and decision rule. This matters. If we gave them different data, we could not tell whether the controller caused the difference.

## State means what the system knows now

At the beginning, the system knows only the case and purchase-order ID. After each step, it adds one fact:

| After step | New fact |
| --- | --- |
| Load order | Supplier ID, commodity, current price and unit |
| Lookup supplier | Supplier name and status |
| Get reference price | Amount, unit and date |
| Calculate variance | Absolute and percentage change |
| Search contract | Threshold or a clear missing-evidence result |

This collection of facts is business state. The system also keeps control state: completed actions, the last error and the number of steps used.

A model saying “I have enough evidence” does not change those facts. The application checks whether every required fact is really present.

## Follow the fixed workflow

The workflow uses this order:

~~~text
load order
→ lookup supplier
→ get reference price
→ calculate variance
→ search contract terms
→ build report
→ wait for human approval
~~~

Run it from the repository root:

~~~shell
python -m labs.week_14.demo workflow --case price-spike
~~~

Look for these fields in the JSON output:

- `route` is `workflow`;
- `status` is `awaiting_approval`;
- `recommendation` is `review_required`;
- `model_calls` is `0`; and
- `tool_calls` is `5`.

The workflow has a transition log. If loading the order fails, it stops. It does not guess a supplier or skip forward.

Try the other decision branches:

~~~shell
python -m labs.week_14.demo workflow --case stable-price
python -m labs.week_14.demo workflow --case missing-terms
~~~

The stable price produces `no_review`. Missing contract terms produce `needs_human`; missing evidence is not treated as proof that there is no limit.

**Check yourself:** Does a workflow use no AI at all? It can still call a model for a bounded task such as summarising evidence. It remains a workflow when application code chooses the route.

## Follow the agent loop

The agent has a planner and an executor.

- The planner proposes an action such as `load_order`.
- The executor checks whether that action exists and is allowed now.
- A trusted tool runs and returns a fact.
- The planner sees the updated state and proposes again.
- The loop stops when the planner proposes `finish` and the application confirms that evidence is complete.

Run the happy route:

~~~shell
python -m labs.week_14.demo agent --case price-spike --script happy
~~~

The output report is identical to the workflow report. The trace looks different:

~~~text
planner:proposed:load_order
executor:completed:load_order
planner:proposed:lookup_supplier
executor:completed:lookup_supplier
...
planner:proposed:finish
agent:awaiting_approval
~~~

The happy script makes six assumed model calls: five tool proposals and one `finish` proposal. A real provider adapter would replace the script later. The application checks would stay.

## Allowed does not always mean ready

`calculate_variance` is an allowed action, but it needs an order and reference price. If the planner asks for it first, the executor returns `order_required`.

Think of this as a kitchen. “Bake” is a valid operation, but it is too early if the ingredients are not mixed. The operation list tells you what can exist; state tells you what can happen now.

The executor also rejects:

- an action outside the list;
- a repeated completed action;
- `finish` before all evidence exists; and
- any proposal after the step budget is exhausted.

These rules belong in code. A prompt that says “do not loop” is useful guidance, but it is not a limit.

## See a loop stop safely

Run the repeated-action script:

~~~shell
python -m labs.week_14.demo agent --case price-spike --script loop
~~~

The command intentionally exits with status 2. The first `load_order` runs. Later duplicates are rejected. After eight planner proposals, the run stops with `duplicate_action`. It does not continue forever.

Now try an unsupported action:

~~~shell
python -m labs.week_14.demo agent --case price-spike --script unsafe
~~~

The planner proposes `send_supplier_email`, but that text is not in the action enum. The executor rejects it, and no email tool exists. A model cannot create a new capability by naming it.

## Understand planner–executor

Planner–executor divides one large responsibility into two smaller ones:

| Planner | Executor |
| --- | --- |
| Suggests what to try | Decides whether the proposal is valid |
| Reacts to observations | Runs trusted code |
| May make mistakes | Enforces limits and prerequisites |
| Can propose completion | Checks that work is actually complete |

The planner is useful for uncertain choices. The executor protects the application boundary.

You should be able to replace the planner model without rewriting permissions, tool code or business rules. You should also be able to test the executor with no model.

## Understand evaluator–optimizer

Sometimes a first draft needs improvement. An evaluator–optimizer loop works like this:

1. create a draft;
2. compare it with a rubric;
3. list specific problems;
4. revise the draft; and
5. stop after a small maximum number of rounds.

For this report, ordinary code should check purchase-order ID, numeric variance, units and evidence IDs. A model evaluator may check whether the explanation is clear and supported.

Do not ask a model to check simple arithmetic. Do not allow unlimited revisions. If the report still fails after the limit, send it to a person.

## Understand orchestrator–worker

An orchestrator splits a larger task into smaller worker tasks. For example:

- one worker checks contracts;
- one checks delivery delays;
- one checks quality incidents; and
- the orchestrator combines their evidence.

Use this when the needed workers change with the request. If the same three checks always run, normal workflow branches are simpler.

The orchestrator still needs a maximum number of workers, correlation IDs, permission checks and a rule for conflicting results.

## Stop for a human decision

Both controllers finish their investigation at `awaiting_approval`. The report has a digest, which is a fingerprint of its exact content.

Run the synthetic approval example:

~~~shell
python -m labs.week_14.demo workflow --case price-spike --approve
~~~

The status becomes `approved`, and the trace records the reviewer fixture. If the report changes, the digest changes and the old approval no longer matches.

The CLI flag is only a local demonstration. A real system needs authenticated reviewer identity, permissions, expiry, persistent audit history and protection against a report changing while it is open.

**Check yourself:** Can the planner approve its own report? No. Planner output comes from the untrusted proposal side of the boundary.

## Read the comparison honestly

Run:

~~~shell
python -m labs.week_14.demo compare
~~~

| Metric | Workflow | Scripted agent |
| --- | ---: | ---: |
| Runs | 4 | 4 |
| Successful investigations | 4 | 2 |
| Failure rate | 0.0% | 50.0% |
| Average model calls | 0.0 | 7.0 |
| Average tool calls | 5.0 | 3.0 |
| Total estimated model cost | USD 0.000000 | USD 0.006148 |
| Average modelled latency | 20.0 ms | 590.5 ms |

The agent is given two successful scripts and two intentionally failing scripts. That is why its failure rate is 50%. This number does not describe a real model.

The cost and latency are also teaching assumptions. They make sure the program can count calls and calculate a comparison. For a real decision, use the exact model version, current price, measured request times and a labelled task set.

Notice that failed agents average fewer tool calls. That is not efficiency; they stopped before finishing. Always examine success together with cost.

## Choose a controller

Choose a workflow when:

- steps are known;
- branches are clear rules;
- you need predictable cost and latency;
- you need easy replay and audit; or
- a wrong route could be costly.

Consider an agent when:

- the right tools depend on the request;
- observations may change the route;
- the action set is bounded;
- wrong proposals can be rejected safely;
- the loop has strict limits; and
- you have test cases for route quality.

A hybrid is often best. Keep the overall lifecycle as a workflow, use an agent inside one uncertain read-only step, and return to deterministic validation and human approval.

## Avoid these mistakes

1. **Calling every LLM application an agent.** A fixed chain with an LLM summary is still a workflow.
2. **Letting the prompt define permissions.** The executor needs an actual action allowlist and current authorization.
3. **Forgetting a terminal budget.** Limit steps, retries, time and result size.
4. **Using a model for arithmetic or thresholds.** Put deterministic rules in code.
5. **Comparing different tasks.** Keep tools, facts and success criteria equal.
6. **Treating missing evidence as a negative result.** Use `needs_human` when you cannot support a conclusion.
7. **Approving changed content.** Bind approval to the reviewed report snapshot.
8. **Calling scripted results a model benchmark.** Test a real model on labelled cases before making quality claims.

## Complete the lab

Work through these steps:

1. Read `labs/week_14/LOGIC.md`.
2. Run all three workflow cases and explain each recommendation.
3. Run the happy and detour agent scripts. Confirm that their reports match the workflow.
4. Run the loop and unsafe scripts. Find the exact stopping reason in each trace.
5. Inspect `Action`, `InvestigationState` and `FixtureTools.execute`.
6. Change one planner proposal and predict the result before running it.
7. Approve one report, change its summary in a test and confirm the approval mismatch.
8. Run the focused checks:

~~~shell
python -m labs.week_14.demo smoke
python -m pytest tests/test_week14_workflows.py -q
~~~

## Practice questions

1. Who chooses the next step in a workflow?
2. Who proposes the next step in an agent?
3. Why does the executor still validate an allowed action?
4. Why is a step limit stronger than “do not loop” in a prompt?
5. When does missing contract evidence become `needs_human`?
6. Why must workflow and agent use the same tools for a fair comparison?
7. What does a report digest protect?
8. When is orchestrator–worker more useful than fixed parallel branches?
9. Which report checks belong in code instead of a model evaluator?
10. Give one task where you would refuse to use an agent and explain why.

You are ready when you can follow both traces, explain every rejected proposal and choose the simpler controller for a new task. Week 15 will place these same ideas into a graph with explicit nodes, edges, conditional routing, persistence and interrupts.

Try the [Week 14 assessment]({{ '/assessments/week-14/' | relative_url }}) for a random paper covering workflows, bounded agents, human approval and orchestration patterns.

## Read alongside the lab

- [Anthropic: Building effective AI agents](https://www.anthropic.com/research/building-effective-agents) introduces the workflow/agent distinction and the routing, orchestrator–worker and evaluator–optimizer patterns used in this lesson.
- [OpenAI Agents SDK: Running agents](https://openai.github.io/openai-agents-python/running_agents/) provides a concrete example of a tool-using loop with a maximum-turn limit.
- [OpenAI Agents SDK: Human-in-the-loop](https://openai.github.io/openai-agents-python/human_in_the_loop/) explains how an agent run can pause for approval or rejection and later resume.
- [LangGraph: Graph API overview](https://docs.langchain.com/oss/python/langgraph/graph-api) introduces state, nodes and edges, which are the focus of Week 15.

These are framework and pattern references. The Week 14 code remains a local scripted comparison, so its assumed cost, latency and failure values must not be attributed to any of these sources.
