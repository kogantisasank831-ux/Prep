---
layout: week
week: 14
phase: 4
status: approved
version: 1.0.1
last_reviewed: 2026-11-01
estimated_hours: 8
permalink: /weeks/week-14/
title: "Choose the controller before you build the agent"
description: Compare a deterministic state-machine workflow with a bounded tool-using agent over the same procurement investigation, tools, decision rule and human-approval boundary.
summary: Build the same investigation twice, inspect every transition and proposal, and decide when model-directed routing earns its extra cost and failure surface.
kicker_primary: Workflows versus agents
kicker_secondary: Put uncertainty only where it is useful
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-14/beginner/
---

## The route may already be known

A buyer asks you to investigate a unit-price increase. The work is familiar:

1. load the purchase order;
2. check the supplier;
3. retrieve the dated reference price;
4. calculate the variance;
5. find the contract threshold; and
6. prepare a report for human review.

Nothing in that description requires a model to decide what happens next. The route is known, the data contracts are known and the decision rule can be written in ordinary code. A deterministic workflow is the natural first controller.

Now change the request: “Investigate this supplier problem. Use whichever sources are useful, ask for missing context and stop when you have enough evidence.” The route is no longer completely known. A planner may need to choose among tools and revise its route as observations arrive. That is where an agent can earn its complexity.

The important design question is therefore not “How do I add an agent?” It is “Which decisions are uncertain enough to justify model-directed control?” This week answers that question by implementing the same synthetic procurement investigation twice:

- a workflow whose state transitions are application code; and
- an agent whose planner proposes the next operation while the application validates and executes it.

Both versions use the same tools, facts, price calculation, recommendation rule and approval boundary. Keeping those parts equal makes control flow the independent variable. The runnable lab uses a scripted planner so every route and failure is reproducible without a provider key. It tests orchestration behavior; it does not measure a real model.

If agent terminology is new, use the [beginner version]({{ '/weeks/week-14/beginner/' | relative_url }}) first. Week 13’s tool contracts remain the boundary underneath this lesson: a model can propose an operation, but application code still owns authority and execution.

| Time | Focus | Evidence to retain |
| --- | --- | --- |
| Hour 1 | Classify fixed and uncertain decisions | A route ownership table |
| Hour 2 | Follow the deterministic state machine | One complete workflow trace |
| Hour 3 | Follow the bounded agent loop | One proposal/execution trace |
| Hour 4 | Study planner–executor and validation | Rejected premature and unsupported actions |
| Hour 5 | Compare evaluator–optimizer and orchestrator–worker | One justified use case for each |
| Hour 6 | Bind a report to human approval | A report digest and explicit decision |
| Hour 7 | Run the controlled comparison and failure scripts | Calls, assumed cost/latency and failure outcomes |
| Hour 8 | Select a controller for a new task | A design note and interview answer |

## Separate business state from control state

The investigation has business state: the order, supplier, reference price, calculated variance and contract terms. It also has control state: which step has completed, what may run next, how many attempts remain and whether the report is waiting for approval.

Mixing the two produces fragile systems. A string such as “supplier checked” is not a supplier record, and a model sentence such as “all evidence is complete” is not proof that required fields exist. The Week 14 lab stores typed facts in `InvestigationState` and derives readiness from those facts:

~~~python
@dataclass
class InvestigationState:
    case: ProcurementCase
    order: PurchaseOrder | None = None
    supplier: Supplier | None = None
    reference_price: ReferencePrice | None = None
    variance: PriceVariance | None = None
    contract_terms: ContractTerms | None = None
    completed: set[Action] = field(default_factory=set)
    last_error: str | None = None

    def ready_for_report(self) -> bool:
        return all(
            value is not None
            for value in (
                self.order,
                self.supplier,
                self.reference_price,
                self.variance,
                self.contract_terms,
            )
        )
~~~

The state does not contain an arbitrary `next_step` supplied by a model. Each controller decides what to propose or execute, but the application checks prerequisites against the same facts.

**Checkpoint:** If an agent says `finish` after loading only the order, is the investigation complete? No. The executor rejects the proposal because four required observations are absent.

## A workflow owns the transition table

A deterministic workflow maps a known state to a known next operation. The lab’s route is deliberately visible:

~~~python
WORKFLOW_ACTIONS = (
    Action.LOAD_ORDER,
    Action.LOOKUP_SUPPLIER,
    Action.GET_REFERENCE_PRICE,
    Action.CALCULATE_VARIANCE,
    Action.SEARCH_CONTRACT_TERMS,
)
~~~

Each successful tool result is assigned to the corresponding typed state slot. A missing order stops the run with `order_not_found`. Variance cannot run before both the order and reference price exist. When all five observations are present, deterministic code builds the report and moves to `awaiting_approval`.

This is a state machine even though it does not use a graph library. Its states and transitions can be expressed as a table:

| Current state | Operation | Success state | Failure state |
| --- | --- | --- | --- |
| Started | Load order | Order loaded | Failed |
| Order loaded | Lookup supplier | Supplier loaded | Failed |
| Supplier loaded | Get reference price | Reference loaded | Failed |
| Reference loaded | Calculate variance | Variance calculated | Failed |
| Variance calculated | Search contract terms | Evidence complete | Failed |
| Evidence complete | Build report | Awaiting approval | Failed |
| Awaiting approval | Human decision | Approved or rejected | Remains pending |

The route is easy to explain because every run follows the same transition table. Testing can cover each edge directly. Cost and maximum tool calls can be bounded before execution: this route requires five tool calls and no model calls.

Run it:

~~~shell
python -m labs.week_14.demo workflow --case price-spike
~~~

The verified trace is:

~~~text
workflow:start
workflow:load_order:complete
workflow:lookup_supplier:complete
workflow:get_reference_price:complete
workflow:calculate_variance:complete
workflow:search_contract_terms:complete
workflow:awaiting_approval
~~~

The fixture’s current price is USD 2.20/kg, its dated reference is USD 2.00/kg and its contract threshold is 5.00%. Exact decimal calculation produces a 10.00% variance, so the shared decision rule recommends `review_required`. The workflow does not accept the report automatically.

**Checkpoint:** Does deterministic mean infallible? No. A workflow can contain incorrect rules, bad transitions or unreliable tools. Deterministic means the application owns the route and the same state produces the same routing decision.

## An agent chooses part of the route at runtime

An agent loop gives a planner observations and an allowed action catalogue. The planner proposes the next action. The executor validates the proposal, runs an allowed operation and returns an observation. The loop continues until it reaches a valid terminal state or a bound.

The lab exposes only these planner actions:

~~~python
class Action(StrEnum):
    LOAD_ORDER = "load_order"
    LOOKUP_SUPPLIER = "lookup_supplier"
    GET_REFERENCE_PRICE = "get_reference_price"
    CALCULATE_VARIANCE = "calculate_variance"
    SEARCH_CONTRACT_TERMS = "search_contract_terms"
    FINISH = "finish"
~~~

The planner cannot extend that enum by writing a convincing new action. `send_supplier_email` is rejected as unsupported and never reaches the tool executor. An allowed action can still be invalid in the current state: `calculate_variance` is rejected until the order and reference price are available.

A simplified loop looks like this:

~~~python
for _ in range(max_steps):
    raw_action = planner.choose(state)
    action = validate_allowed_action(raw_action)

    if action is Action.FINISH:
        require_complete_evidence(state)
        return build_report_and_wait_for_approval(state)

    require_not_already_completed(action, state)
    fact = tools.execute(action, state)
    apply_fact(state, action, fact)

return fail("step_budget_exhausted")
~~~

In a provider integration, `planner.choose` would call a model with a versioned prompt and a structured output contract. This lab uses `ScriptedPlanner`, which crosses the same boundary while returning fixed proposals. Every assumed model call records tokens, cost and latency from an explicit teaching profile.

Run the valid route:

~~~shell
python -m labs.week_14.demo agent --case price-spike --script happy
~~~

The agent produces the same report digest as the workflow. Its trace includes both sides of the boundary:

~~~text
planner:proposed:load_order
executor:completed:load_order
planner:proposed:lookup_supplier
executor:completed:lookup_supplier
...
planner:proposed:finish
agent:awaiting_approval
~~~

The planner owns route proposals. The executor owns the allowlist, prerequisites, duplicate protection, tool invocation, terminal readiness and step budget.

**Checkpoint:** If a prompt says the model is “authorized to use any necessary tool,” has the authorization boundary changed? No. Prompt text does not add an action to the executor or grant a capability.

## Planner–executor is a separation of responsibilities

Planner–executor is often described as an agent pattern, but the useful idea is simpler: separate deciding *what to try* from performing an operation.

The planner should receive enough state to choose a useful next action. It should not receive database credentials or a Python function object that bypasses application checks. The executor should accept a small structured proposal, apply current policy and return a bounded result.

| Planner owns | Executor owns |
| --- | --- |
| Proposing the next allowed action | Parsing and validating the proposal |
| Choosing among available routes | Checking prerequisites and current authority |
| Reacting to controlled observations | Invoking trusted implementations |
| Proposing completion | Verifying terminal state |
| Explaining why it chose a route | Recording actual operations and outcomes |

Planner errors are ordinary operating conditions. The model can choose a valid tool at the wrong time, repeat an already completed action, request an unsupported action or stop early. The executor needs defined behavior for each case.

The lab allows a planner to recover from a dependency error. This script first proposes variance too early, receives `order_required`, then follows a valid route. It completes with six tool invocations because the rejected prerequisite check entered the tool boundary once. A production design could reject known prerequisites before incrementing the adapter count; the important requirement is to define and measure the boundary consistently.

The repeated-action script demonstrates loop protection:

~~~shell
python -m labs.week_14.demo agent --case price-spike --script loop
~~~

The first `load_order` executes. Seven repeated proposals are rejected, and the run exits with status 2 after eight planner calls. Tool calls remain one. A loop budget is a terminal rule, not a polite suggestion in the system prompt.

## LLM routing should be earned by route uncertainty

LLM-based routing is useful when the input cannot be classified adequately with stable rules and the cost of a wrong route is controlled. Examples include choosing whether an ambiguous request needs document retrieval, structured data, clarification or no action.

It is a poor fit when:

- the next step follows directly from typed state;
- every case needs the same operations;
- a rule or classifier meets the routing requirement;
- latency or per-request cost is tight;
- reproducibility is mandatory;
- a wrong route could create a consequential effect; or
- there is no labelled evaluation set for routing quality.

You do not need to choose one controller for an entire product. A hybrid design can keep the outer lifecycle deterministic and use a model at one uncertain node. For example, a workflow can validate the request, load the permitted sources and enforce approval, while an LLM chooses which of three read-only investigation tools to try inside a bounded node.

That design puts uncertainty in one visible location. It also leaves a simple fallback: if routing confidence or validation fails, ask a human or follow a conservative default.

## Evaluator–optimizer adds a bounded revision loop

An evaluator–optimizer pattern generates a candidate, evaluates it against explicit criteria and revises it when the evaluation identifies a correctable gap.

For the procurement report, an evaluator might check whether the draft:

- names the purchase order;
- states the reference date;
- preserves currency and unit;
- compares the variance with the retrieved threshold;
- distinguishes missing evidence from a negative finding; and
- avoids claiming that a recommendation has been approved.

Use deterministic checks first. Required fields, evidence IDs, arithmetic and threshold comparison do not need another model. A model evaluator may help with semantic coverage or clarity after those checks pass.

A safe optimizer loop needs a stopping rule:

~~~python
draft = generate_report(facts)
for _ in range(2):
    findings = evaluate(draft, rubric)
    if not findings:
        break
    draft = revise(draft, findings)
else:
    return needs_human_review(draft, findings)
~~~

Without an iteration cap, the two models can trade stylistic opinions indefinitely. Without a stable rubric, “improve this” creates movement without a measurable finish. The evaluator must not grant approval merely because its own score is high.

**Checkpoint:** Should a model evaluate whether `10.00 > 5.00`? No. Deterministic code should own that check. Reserve model evaluation for criteria that actually require semantic judgement.

## Orchestrator–worker manages dynamic parallel work

An orchestrator decomposes a task into worker jobs, collects results and merges them. This helps when the number or type of subtasks varies by request. A complex supplier investigation might need separate workers for contract evidence, delivery history, quality incidents and market context.

Parallelism is not free. The orchestrator must bound fan-out, carry correlation IDs, preserve caller scope, cancel unnecessary work and define what to do with partial results. Two workers may return contradictory dates or duplicate the same source. The merge step needs provenance and conflict rules.

For the five-step Week 14 case, a dynamic orchestrator would add little value. After the order is loaded, supplier lookup, reference lookup and contract search could run concurrently, but a normal workflow can express that fan-out directly. A model does not need to rediscover a stable dependency graph on every request.

Use orchestrator–worker when decomposition is genuinely input-dependent. Use ordinary concurrency inside a workflow when the branches are known.

## Human approval is a state, not a sentence

Both controllers stop at `awaiting_approval`. The report includes a digest over its case, purchase order, recommendation, summary and evidence. The synthetic reviewer input contains that digest, a reviewer identity and an approve/reject decision.

~~~python
approval = HumanApproval(
    report_digest=result.report.digest(),
    reviewer="reviewer-1",
    decision=ApprovalDecision.APPROVE,
)
approved = finalize(result, approval)
~~~

If the report changes after review, the digest changes and the old approval is rejected. Blank reviewer identity is rejected. Approval accepts the local report; it does not approve the purchase order or trigger an external action.

Run the explicit synthetic approval path:

~~~shell
python -m labs.week_14.demo workflow --case price-spike --approve
~~~

The CLI flag is a teaching fixture supplied by the trusted host process after the report exists. It is not authentication, a digital signature or proof that a real person used a review interface. A production approval service would also need identity assurance, role checks, expiry, durable audit history, concurrent-change handling and a defined rejection/revision path.

**Checkpoint:** Can a model place `"approved": true` in its output? It can emit the text, but that field is not a `HumanApproval` constructed by the trusted host and bound to the report digest.

## Compare the controllers with the same case

Run four controlled planner scripts—happy, detour, loop and unsupported action—against the same price-spike case:

~~~shell
python -m labs.week_14.demo compare
~~~

The verified local result is:

| Metric | Deterministic workflow | Scripted agent |
| --- | ---: | ---: |
| Runs | 4 | 4 |
| Successful investigations | 4 | 2 |
| Failures | 0 | 2 |
| Failure rate | 0.0% | 50.0% |
| Average model calls | 0.0 | 7.0 |
| Average tool calls | 5.0 | 3.0 |
| Total estimated model cost | USD 0.000000 | USD 0.006148 |
| Average modelled latency | 20.0 ms | 590.5 ms |
| Trace style | Fixed transition log | Proposal and execution log |

Interpret this table carefully. The workflow repeats one valid fixed route four times. The agent is intentionally given two valid and two failing scripts. Therefore the 50% failure rate is a property of this selected control set, not an estimate of any real model and not proof that agents are always half as reliable.

The cost uses assumed prices of USD 1.00 per million input tokens and USD 3.00 per million output tokens. Latency is a deterministic value attached to each simulated call. Neither figure is a provider quote or wall-clock benchmark. Replace the profile with an actual versioned model price and collect real request telemetry before making a deployment decision.

The comparison is still useful. It proves that the harness records the dimensions requested by the roadmap and exposes the extra routing surface. It also shows why averages need context: failing agents make fewer tool calls because they stop before completing the work.

## Reliability needs a task-level denominator

“The agent succeeded” is incomplete without a task set and an expected result. Build an evaluation dataset that contains:

- straightforward cases with a known route;
- missing and contradictory evidence;
- requests that require clarification;
- irrelevant requests that should use no tool;
- transient tool failures;
- forbidden or unavailable actions;
- attempts to finish early; and
- cases where the correct outcome is human escalation.

For each case, label acceptable routes and terminal outcomes. Some tasks can have more than one valid tool order. Measure at least:

| Measure | Question |
| --- | --- |
| Task success | Did the run reach an acceptable terminal outcome? |
| Route accuracy | Were the selected tools appropriate for the case? |
| Argument accuracy | Were tool arguments grounded and valid? |
| Unsupported-action rate | How often did the planner request unavailable capability? |
| Loop/budget rate | How often did the controller exhaust its bounds? |
| Human escalation precision | Did it escalate the cases that needed judgement? |
| Calls, cost and latency | What resources did successful and failed runs consume? |
| Trace completeness | Can each result be connected to proposals, operations and evidence? |

Report failures by category. A timeout, invalid route, missing permission, bad argument and unsupported request need different fixes.

## Explainability differs between controllers

A workflow trace explains which predefined transition ran and what it returned. It is compact and predictable. An agent trace must preserve the observation shown to the planner, the proposed action, validation outcome, actual tool execution, controlled error and terminal reason. A natural-language “thought process” is not required and should not be treated as an audit record.

Store operational facts that support replay and debugging:

- controller and prompt version;
- case and correlation ID;
- allowed tool catalogue version;
- proposed structured action;
- validation and authorization outcome;
- tool name, attempt count and bounded duration;
- result schema version and evidence IDs;
- budget counters and stop reason; and
- report digest and human decision metadata.

Do not log credentials, entire prompts containing sensitive data, raw documents or unrestricted tool results. An explainable system records what crossed its application boundaries; it does not expose private reasoning text.

## Common failure modes

### Calling a fixed sequence an agent

If code always calls A, then B, then C, it is a workflow even if an LLM writes the final paragraph. That is often the better design. Name the controller by who owns routing.

### Asking a model to enforce deterministic invariants

Models should not own numeric thresholds, required fields, access control, allowed transitions or maximum iterations. Encode those as application rules.

### Hiding the loop in a framework default

Know the actual maximum steps, retries, timeout behavior and terminal states. “The framework handles it” is not an operating policy.

### Counting only successful model calls

Rejected proposals and failed revisions still consume tokens and time. Track attempts and terminal failures in the same denominator.

### Comparing different tasks or tools

If the workflow gets clean structured data while the agent gets ambiguous documents, the result does not isolate the controller. Keep task, tools, decision logic and acceptance criteria equal.

### Treating human approval as a button after the effect

The system must pause before the guarded transition. Bind the decision to the reviewed snapshot, recheck current authority and record approve, reject or revise.

### Using an agent to avoid specifying the process

An agent still needs allowed actions, state, budgets, failure categories and acceptance criteria. Ambiguity moved into a prompt remains ambiguity.

## Select the smallest controller that fits

Use this decision table before choosing a framework:

| Task property | Prefer |
| --- | --- |
| Stable ordered steps | Deterministic workflow |
| Known branches expressible as rules | Workflow or state machine |
| One ambiguous classification inside a stable process | Workflow with one model-routing node |
| Dynamic tool choice from bounded read-only options | Bounded agent |
| Input-dependent decomposition into many independent tasks | Bounded orchestrator–worker |
| Draft quality can be checked against a semantic rubric | Bounded evaluator–optimizer |
| Consequential write or irreversible effect | Deterministic gate plus human approval |
| Tight latency, cost or reproducibility requirement | Deterministic workflow |
| No evaluation dataset or terminal bounds | Keep the route deterministic until those exist |

An agent is not the advanced choice by default. The advanced choice is the controller whose uncertainty, operating cost and failure behavior you can defend.

## Build the investigation in eight hours

1. Read `labs/week_14/LOGIC.md` and write down which component owns each decision.
2. Run the workflow for `price-spike`, `stable-price` and `missing-terms`. Confirm the three recommendation branches.
3. Inspect `WORKFLOW_ACTIONS`, `FixtureTools.execute` and `_build_report`. Trace dependencies from state to decision.
4. Run the happy agent and compare its report digest with the workflow report.
5. Run `detour`, `loop` and `unsafe`. Explain every rejection and terminal outcome from the trace.
6. Change the maximum steps or one planner script. Predict model/tool-call counts before running the test.
7. Apply a matching approval, then change the report and confirm the old approval no longer matches.
8. Run the comparison, replace one teaching assumption and explain why the resulting number is still not a provider benchmark.

Use the focused gates:

~~~shell
python -m labs.week_14.demo smoke
python -m pytest tests/test_week14_workflows.py -q
python -m ruff check labs/week_14 tests/test_week14_workflows.py
python -m ruff format --check labs/week_14 tests/test_week14_workflows.py
python -m mypy --strict --explicit-package-bases labs/week_14 tests/test_week14_workflows.py
~~~

## Independent exercises

1. Add a `supplier-suspended` case. Keep the same controller code and prove that both routes return `review_required`.
2. Add a clarification terminal state for a missing purchase-order ID. Decide whether clarification counts as success in your evaluation set.
3. Permit one correction after an unsupported proposal, then measure how the extra call changes cost and success.
4. Add a deterministic precondition check before `FixtureTools.execute`. Explain whether rejected proposals should count as tool calls.
5. Design an evaluator rubric for the report. Separate rules that belong in code from semantic criteria that may need a model.
6. Sketch a bounded orchestrator for contract, delivery and quality workers. Define fan-out, cancellation and merge-conflict behavior.
7. Replace the scripted planner with a provider adapter in a private branch. Version the model/prompt, preserve structured actions and evaluate it on labelled cases before comparing results.
8. Write a migration plan from in-memory approval to a durable service with identity, expiry, concurrency and audit history.

## Interview answer: when should you not use an agent?

A strong answer begins with control ownership:

> I would not use an agent when the application already knows the valid sequence or can express its branches with stable rules. A workflow is usually cheaper, faster, easier to test and easier to audit. I add model-directed routing only where input-dependent uncertainty justifies it, and I keep tools, permissions, invariants, budgets and consequential transitions under deterministic application control. Before release, I compare both controllers on the same labelled tasks using task success, route and argument errors, model/tool calls, cost, latency, loop rate and human-escalation quality. If an agent does not improve the required outcome enough to pay for its added failure surface, I keep the workflow.

Be prepared to give a hybrid example. “A deterministic lifecycle with one bounded model-routing node” demonstrates more engineering judgement than treating workflows and agents as mutually exclusive architectures.

## Finish with a controller you can defend

You are done when you can point to every routing decision and say whether code, a model or a human owns it. You should be able to reproduce a valid workflow, a valid agent route, a loop termination, an unsupported-action rejection and an approval mismatch. You should also be able to explain why the supplied metrics prove the harness behavior but not real-model quality.

Week 15 will express explicit state, nodes, edges, conditional routes, checkpointing and interrupts with LangGraph. The concepts in this week remain the test: a graph library can make control flow visible, but it cannot decide which transitions should be deterministic or where human authority belongs.

## Sources and further reading

- [Anthropic: Building effective AI agents](https://www.anthropic.com/research/building-effective-agents) distinguishes predefined workflows from model-directed agents and describes routing, orchestrator–worker and evaluator–optimizer patterns. Treat its examples as design guidance, not evidence for this lab's metrics.
- [OpenAI Agents SDK: Running agents](https://openai.github.io/openai-agents-python/running_agents/) documents a tool-using agent loop, structured termination and finite `max_turns`. The Week 14 lab implements its own provider-neutral teaching loop and does not import the SDK.
- [OpenAI Agents SDK: Human-in-the-loop](https://openai.github.io/openai-agents-python/human_in_the_loop/) shows pause, approve/reject and resume concepts. Its documentation also notes that serialized run state does not authenticate itself; a real application must protect identity, integrity and ownership separately.
- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) defines tasks, trials, graders, transcripts and outcomes for multi-turn evaluations. Use those distinctions when replacing the scripted control set with a labelled real-model evaluation.
- [LangGraph: Graph API overview](https://docs.langchain.com/oss/python/langgraph/graph-api) explains state, nodes and edges for explicit stateful workflows. Week 15 will apply that framework; Week 14 deliberately keeps the controller in ordinary Python so the design remains visible.
