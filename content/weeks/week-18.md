---
layout: week
week: 18
phase: 4
status: approved
version: 1.0.1
last_reviewed: 2026-11-05
estimated_hours: 8
permalink: /weeks/week-18/
title: "Evaluate agents by outcomes, trajectories and safety"
description: Build a 28-case procurement-agent evaluation with explicit success criteria, deterministic graders, trace metrics, category slices and honest cost and latency boundaries.
summary: A useful agent evaluation names the task, expected end state, permitted trajectory and grader before running the candidate—and keeps every denominator visible.
kicker_primary: Agent evaluation
kicker_secondary: Tasks, trials, traces, graders and regression gates
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-18/beginner/
---

## An agent can reach the right answer the wrong way

A final answer alone is weak evidence for an agent. The agent may have called the
wrong tool, sent the wrong supplier ID, repeated a costly step, ignored a failed
source or attempted an action that needed approval. It may also fail to finish a
normal request while looking fluent.

Week 18 evaluates the bounded Procurement Intelligence Agent v1 from Week 17 on
28 synthetic cases. Every case declares:

- an input request;
- a controlled scenario;
- the expected status and recommendation or failure code;
- the exact ordered tool route; and
- a category used for slice analysis.

The evaluator records the candidate's end state and tool trajectory, applies
deterministic graders and aggregates quality, efficiency, escalation, cost,
latency and safety metrics. The implementation is local and repeatable so every
number can be checked by hand.

If tasks, traces and metric denominators are new, start with the
[beginner version]({{ '/weeks/week-18/beginner/' | relative_url }}).

The [Week 18 assessment]({{ '/assessments/week-18/' | relative_url }}) draws
10 balanced questions from a bank of 100, with explanations and browser Python
checks.

| Time | Focus | Evidence to retain |
| --- | --- | --- |
| Hour 1 | Write the evaluation objective | one candidate and one decision boundary |
| Hour 2 | Specify tasks and success criteria | versioned visible cases |
| Hour 3 | Capture end states and trajectories | one closed observation per trial |
| Hour 4 | Implement deterministic graders | independent outcome/tool/argument checks |
| Hour 5 | Define metric denominators | raw counts beside every rate |
| Hour 6 | Add adversarial and failure slices | category-level results |
| Hour 7 | Test the evaluator itself | mutation and replay evidence |
| Hour 8 | Interpret without overclaiming | regression gate and limitations |

## Define the evaluation unit before the metric

Useful terminology keeps teams from comparing different things:

| Term | Meaning in this lab |
| --- | --- |
| Candidate | Procurement Intelligence Agent v1.0.0 |
| Dataset | versioned collection of 28 visible tasks |
| Task or case | one input plus declared success criteria |
| Trial | one candidate attempt at one task |
| Observation | end state, tool calls, steps, escalation, cost/latency fixtures and unsafe actions |
| Grader | deterministic logic scoring one aspect of an observation |
| Score | one case's outcome and trajectory judgments |
| Run | all 28 observations, scores and aggregates for one candidate version |

Model-backed agents are variable, so one task normally needs multiple trials.
This lab uses deterministic functions and controlled fixtures; repeated trials
would be identical. That makes one trial per case sufficient for teaching the
grader contracts, but not a general model-evaluation policy.

**Checkpoint:** a case is not just a prompt. It needs success criteria that an
independent grader can apply to observable evidence.

## Start with the decision the evaluation must support

“Evaluate the agent” is too vague. Decide whether the result will:

- block a regression before merge;
- compare two candidate versions;
- identify failure categories for improvement;
- estimate production quality on representative traffic;
- calibrate a human or model judge; or
- monitor deployed behavior.

Week 18 supports a narrow pre-deployment decision: does this deterministic
candidate still satisfy its accepted procurement contracts on the visible
regression suite, and do its tool trajectories expose the one injected argument
defect?

It does not estimate production incident frequency. The dataset intentionally
contains many failures, conflicts and approval requests. Its mix is useful for
stress coverage and misleading as a traffic forecast.

## Freeze the candidate and dataset identity

An aggregate without candidate and dataset identity cannot be reproduced. The
result records:

- candidate version `procurement-agent-v1.0.0`;
- dataset ID `week18-procurement-agent-v1`;
- semantic dataset version `1.0.0`; and
- SHA-256 of the exact dataset bytes.

Changing an expected outcome, description or input changes the digest. A new
meaningful dataset revision should also change the semantic version. Never place
two different suites behind the same version and then compare their rates as if
only the candidate changed.

The loader bounds input size, requires UTF-8 JSON, rejects duplicate keys and
non-finite constants, and then validates a strict closed schema. Duplicate case
IDs, an incorrect total and missing category coverage fail before evaluation.

A digest detects changed bytes. It does not prove who authored the dataset,
whether the expectations are correct or whether the cases represent production.

## Cover normal work and consequential boundaries

The roadmap asks for approximately 20–30 agent cases. This suite uses 28:

| Category | Count | Accepted behavior |
| --- | ---: | --- |
| Normal request | 6 | complete with the policy recommendation |
| Missing information | 4 | reject malformed input or escalate valid missing evidence |
| Tool failure | 4 | fail closed without a commercial report |
| Conflicting evidence | 4 | reject wrong identity, supplier conflict or digest mismatch |
| Prompt injection | 4 | keep untrusted text outside routing and tool arguments |
| Invalid tool arguments | 3 | reject bad request data and expose one wrong SQL supplier argument |
| Approval required | 3 | stop approve, purchase and supplier-contact requests before tools |

Positive cases prove the system can work. Negative cases prove it can stop.
Neither replaces the other.

Do not create 28 paraphrases of the happy path. Vary the contract boundary:
missing fields, incompatible identities, source failure, cross-source conflict,
malicious-looking content, invalid arguments and prohibited actions.

## Keep the oracle independent of the behavior under test

An **oracle** is the source of expected truth. If the candidate calculates its
own expected result, the evaluator can repeat the same bug and award a pass.

The Week 18 dataset declares expected end states and tool routes. Expected tool
arguments are projected independently from the accepted request and immutable
Week 17 case fixture. The fault adapter for `W18-025` changes the actual SQL
supplier argument to `SUP-INVALID`; it cannot change the expected supplier
`SUP-171`.

That case is deliberately subtle:

- the SQL specialist detects the bad supplier and fails closed;
- the expected safe end state therefore passes;
- the exact tool route still passes; but
- only two of three expected tool arguments pass.

If “task success” required every trajectory grader to pass, the evaluator would
hide the important distinction between safe failure handling and the upstream
defect that caused it.

## Capture a trace that is useful but not excessive

For each trial the evaluator retains:

~~~python
class AgentObservation(StrictModel):
    case_id: Identifier
    status: AgentStatus
    recommendation: RecommendationValue | None
    failure_code: str | None
    tool_calls: tuple[ToolCall, ...]
    steps: int
    human_escalated: bool
    requires_human_approval: bool
    cost_units: int
    fixture_latency_ms: int
    unsafe_actions: tuple[str, ...]
~~~

Each tool call includes its ordered step, tool name, minimal projected arguments,
fixture cost and fixture latency. Raw source bodies, prompts, secrets and hidden
reasoning are excluded.

Trace data should answer the grader's questions. Collecting every intermediate
byte “just in case” increases privacy, retention and access risk. Conversely, a
trace that contains only the final answer cannot grade routing, arguments, loops
or escalation.

## Define task completion as an end-state contract

Task completion is not “the agent returned text.” This lab requires:

1. the expected case identity;
2. the expected status;
3. the expected recommendation or controlled failure code; and
4. zero observed unsafe actions.

A normal price spike succeeds with `completed/review_required`. Missing contract
terms succeed with `escalated/needs_human`. A simulated document outage succeeds
as an evaluation task only when it returns the declared fail-closed code with no
report or action.

This convention measures whether the candidate handled the situation correctly.
It does not call the underlying outage desirable.

Formula:

~~~text
task completion rate = successful end-state contracts / all cases
~~~

Report the raw numerator and denominator beside the rate. `28/28` is more
informative than `100%` alone.

## Grade tool selection exactly

Tool selection asks whether the candidate chose the exact ordered route declared
for the case.

Normal investigation expects:

~~~text
document → sql → supplier_risk → commercial
~~~

The first three are dispatched as one Week 17 parallel wave; the ordered trace is
still stable for grading. A first-wave failure expects all three dispatched tools
and no commercial call. Approval-required and malformed requests expect an empty
tool tuple.

Correctly selecting no tool is a meaningful case-level decision and receives
tool-selection credit. It must not automatically receive tool-argument credit,
because there were no expected argument positions.

~~~text
tool-selection accuracy = exact route matches / all cases
~~~

This strict grader is appropriate because the route is deterministic. A more
open agent may have several valid routes; its task must declare an allowed set or
grade required/forbidden properties rather than one arbitrary trace.

## Score tool arguments over real opportunities

For every expected call position, compare the actual projected arguments with
the independent expectation. Missing calls, the wrong tool at that position or a
different argument map receive no credit.

~~~text
tool-argument accuracy = correct expected call positions / expected call positions
~~~

The overall denominator is 73, not 28. Eight no-tool cases contribute zero
argument opportunities. They are excluded rather than granted perfect arguments.

Also retain per-case and per-tool details. One aggregate can conceal that every
document argument is correct while a specific SQL supplier field is wrong.

## Penalize missing and extra steps symmetrically

“Fewer steps” is not always more efficient. An agent that skips required risk
analysis is short and incorrect. An agent that repeats SQL five times is long and
wasteful.

This lab defines:

~~~text
step efficiency = min(expected steps, actual steps)
                  / max(expected steps, actual steps)
~~~

One preflight step is always present, followed by zero or more tool calls. Exact
execution scores `1.0`; both missing and extra work lose credit. Task and tool
graders still determine whether the steps were correct.

Other systems may use excess-step rate, tokens-to-success or a task-specific
optimality model. Name the contract instead of treating “efficiency” as universal.

## Detect loops separately

The Week 18 candidate has no retry loop. A repeated tool name in one trajectory
therefore counts as a loop:

~~~text
loop rate = cases with a repeated tool / all cases
~~~

That heuristic would be wrong for a system where bounded retries are expected.
Such a system should distinguish allowed retries from identical repeated states,
no-progress cycles or exhausted budgets.

Always pair loop detection with hard runtime controls: maximum steps, deadline,
cost budget and cancellation policy. A grader explains behavior after a run; it
does not stop an unbounded production loop by itself.

## Interpret escalation in context

Human escalation includes malformed required input, valid business uncertainty,
technical or correlation failure, and approval-required action.

~~~text
human escalation rate = explicitly escalated cases / all cases
~~~

The baseline is `18/28 = 0.642857`. That is not a target and not an estimate of
production workload. It is a consequence of a suite where 22 of 28 cases probe
non-happy paths.

Escalation can be correct, excessive or missing:

- missing escalation risks unsupported or unauthorized action;
- excessive escalation shifts avoidable work to people; and
- correct escalation routes the right evidence to an accountable reviewer.

Measure escalation quality and operational capacity, not just a low rate.

## Charge failures and label synthetic economics

This lab assigns fixed cost units to tool calls:

| Tool | Fixture cost | Fixture latency |
| --- | ---: | ---: |
| Document | 4 units | 12 ms |
| SQL | 3 units | 8 ms |
| Supplier risk | 3 units | 7 ms |
| Commercial | 5 units | 6 ms |

Cost per successful task is:

~~~text
total cost across every attempt / successful tasks
~~~

Failed attempts remain in the numerator. Otherwise a candidate could spend heavily
on failures while appearing cheap on successes.

Latency uses a deterministic critical-path fixture:

~~~text
1 ms preflight + max(first-wave tool fixtures) + commercial fixture if called
~~~

These values teach accounting and parallel critical paths. They are not measured
wall-clock time, provider billing or production latency. A deployed evaluation
should retain actual tokens, prices, tool/service time and end-to-end percentiles,
with the pricing date and concurrency policy.

## Make unsafe action a hard signal

Unsafe-action rate is:

~~~text
cases with any observed unsafe action / all cases
~~~

The candidate exposes no purchase, message, payment or external-write tool. An
approve, purchase or supplier-contact request stops during preflight and escalates.
Any recorded external action makes task success false even if the final
recommendation matches.

A zero unsafe-action rate here means zero actions in 28 controlled trials against
a candidate with no such capability. It does not prove that a model-connected,
tool-enabled production agent is safe.

## Treat prompt-injection results as narrow evidence

Four cases place direct, forged-system, indirect-document and tool-command-like
strings in `untrusted_text`. The deterministic adapter never uses that field for
routing, tool arguments, registry selection or authorization. Tests remove the
text and require an identical observation.

That proves one data-flow property of this adapter. It does not show resistance
to arbitrary prompt injection because no language model reads the string. Real
systems must evaluate direct and indirect injection across every model-readable
source and enforce least privilege, structured validation and human approval for
consequential actions.

No finite prompt set proves absence of injection vulnerabilities. New attacks,
models, tools and data sources require continuing adversarial evaluation.

## Use the right grader for each criterion

| Criterion | Good first grader | Why |
| --- | --- | --- |
| Exact schema/status/code | deterministic code | objective and cheap |
| Tool name/order/arguments | deterministic code | fully observable contract |
| Database or file result | executable test | checks environment state |
| Semantic helpfulness | calibrated human rubric or model judge | acceptable wording varies |
| Policy nuance | reviewed rubric plus targeted code checks | combines judgment and invariants |
| Safety-critical action | hard allow/deny checks plus human review | judge prose alone is insufficient |

Use code where truth is exact. A model judge is useful for open-ended meaning,
but it is another model with bias, variance, cost and possible prompt injection.
Calibrate it against blinded human labels, test disagreements and version the
judge prompt/model.

Do not ask one judge for a vague `1–10 quality` score. Split criteria such as
correctness, evidence support, policy adherence and clarity, then define anchors.

## Slice results before celebrating the average

The overall baseline looks strong:

| Metric | Baseline |
| --- | ---: |
| Task completion | 28 / 28 |
| Exact tool selection | 28 / 28 |
| Tool arguments | 72 / 73 |
| Mean step efficiency | 1.000000 |
| Loop rate | 0 / 28 |
| Human escalation | 18 / 28 |
| Total fixture cost | 265 units |
| Fixture cost per success | 9.464286 units |
| Mean fixture latency | 12.357143 ms |
| Unsafe actions | 0 / 28 |

The category slice exposes the defect: invalid-tool-argument cases score `2/3`
on arguments while every other expected argument is correct. Without slices,
`98.63%` may look like harmless noise.

Useful slices include category, tool, request type, risk level, language, tenant,
model version and input length—but only where the dataset has enough governed
examples. Small-slice percentages should retain counts and uncertainty.

## Test the evaluator, not only the candidate

A broken grader can turn a broken agent green. The Week 18 tests mutate a valid
observation and require the graders to detect:

- wrong recommendation;
- changed tool arguments;
- extra tool selection;
- repeated-tool loop;
- inefficient step count; and
- unsafe external action.

The suite also proves strict dataset loading, category coverage, all 28 expected
outcomes, prompt-text isolation, approval stops, metric arithmetic, deterministic
replay, critical-path fixture latency, fresh-directory persistence and CLI JSON.

Run the focused evidence:

~~~shell
python -m labs.week_18.demo case --case-id W18-025
python -m labs.week_18.demo evaluate
python -m labs.week_18.demo smoke
python -m pytest tests/test_week18_agent_evaluation.py -q
python -m ruff check labs/week_18 tests/test_week18_agent_evaluation.py
python -m ruff format --check labs/week_18 tests/test_week18_agent_evaluation.py
python -m mypy --strict --explicit-package-bases labs/week_18 tests/test_week18_agent_evaluation.py
~~~

## Separate offline gates from online monitoring

Offline evaluation runs curated cases before deployment. It supports unit checks,
regression gates, benchmarking and backtesting. It is repeatable and can include
rare failures that production traffic may not reveal quickly.

Online evaluation samples real deployed traces. It can detect drift, new inputs,
latency/cost changes and failures the curated suite missed. It also brings privacy,
consent, retention, incident and sampling responsibilities.

Use both:

1. deterministic unit and contract tests on every change;
2. a versioned regression suite before promotion;
3. repeated model trials for variable candidates;
4. representative held-out and adversarial sets;
5. limited, governed production rollout; and
6. online monitoring that feeds reviewed failures back into offline cases.

Never copy a production incident blindly into a public dataset. Minimize,
de-identify, authorize and retain it according to policy.

## Avoid evaluation leakage and overfitting

A visible regression set is useful for debugging and CI. It becomes less useful
as an unbiased benchmark after developers repeatedly tune to it.

Maintain separate layers:

- visible development cases for fast diagnosis;
- held-out cases for candidate selection;
- adversarial cases maintained by another reviewer or team;
- recent governed production samples; and
- a final promotion set with restricted access.

Do not optimize one score while degrading another. A candidate can improve task
completion by calling more tools, raise cost and latency, and increase unsafe
actions. Promotion criteria should name hard safety gates and acceptable quality/
efficiency trade-offs before results are seen.

## A concise interview answer

> I evaluate an agent at both the task and trajectory levels. Each versioned case
> defines its input, accepted end state, permitted tool route and grader. I keep
> task completion separate from tool selection, argument accuracy, step efficiency,
> loops, escalation, cost, latency and unsafe action, with raw denominators and
> category slices. Exact contracts use deterministic code graders; subjective
> criteria use calibrated rubrics and repeated trials. Dataset and candidate
> identities are retained, failed attempts still count toward cost, and safety
> gates cannot be averaged away. Offline regression suites are complemented by
> governed production monitoring, because a finite stress set is evidence—not a
> production forecast or safety certificate.

## Independent exercises

1. Add a delivery-performance case and its independent expected tool arguments.
2. Add a second candidate with one unnecessary SQL retry. Compare task success,
   selection, loop rate, step efficiency, cost and latency.
3. Run five trials for a deliberately variable candidate. Report pass@1 and the
   distribution of cost and steps without averaging away unsafe trials.
4. Create a held-out dataset version. Explain who may see it and when it can be
   promoted into the visible regression set.
5. Add a subjective explanation rubric and calibrate two reviewers on ten cases.
   Report agreement and disputed examples.
6. Replace fixture latency with real monotonic measurements around controlled
   service calls. Report p50/p95 and timeout policy.
7. Expand prompt-injection testing to a model-readable document sandbox with no
   write capability. Define the exact safe behavior before running it.

## Finish with evidence

You are done when you can show:

- one named candidate and versioned, digested dataset;
- 28 cases covering all seven roadmap categories;
- independent expected outcomes, routes and arguments;
- closed observations with minimal useful trajectories;
- explicit formulas, counts and denominators for every metric;
- separate task, tool, argument, efficiency, loop, escalation and safety graders;
- stress-category slices and honest cost/latency labels;
- mutation tests proving graders fail when evidence is wrong;
- deterministic replay and fresh result persistence; and
- passing smoke, tests, lint, format and strict typing.

Use the [Week 18 assessment]({{ '/assessments/week-18/' | relative_url }}) to
practise dataset identity, independent outcome and trajectory graders, raw
denominators, category slices, safety gates and evidence-bounded interpretation.

## Sources and further reading

- [OpenAI agent evals](https://developers.openai.com/api/docs/guides/agent-evals)
  for evaluating end-to-end agent workflows, tool calls and handoffs.
- [OpenAI trace grading](https://developers.openai.com/api/docs/guides/trace-grading)
  for scoring structured traces rather than only final outputs.
- [OpenAI evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
  for objectives, datasets, metrics, comparison and continuous evaluation.
- [LangSmith evaluation types](https://docs.langchain.com/langsmith/evaluation-types)
  for offline benchmarks, unit/regression tests, backtesting and online evaluation.
- [Anthropic, Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)
  for tasks, trials, graders, traces and repeated evaluation of variable agents.
- [OWASP LLM01:2025 Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
  for direct/indirect injection risks and the limits of prompt-only defenses.
- [Week 18 lab](https://github.com/kogantisasank831-ux/Prep/tree/main/labs/week_18)
  for the complete local dataset, evaluator, tests and CLI.
