---
layout: week
week: 17
phase: 4
status: approved
version: 1.1.0
last_reviewed: 2026-11-09
estimated_hours: 8
permalink: /weeks/week-17/
title: "Coordinate specialists without creating agent chaos"
description: Build a bounded supervisor with document, SQL, supplier-risk and commercial specialists, then compare it honestly with one sequential workflow.
summary: Use typed handoffs, isolated ownership, bounded parallel work and fail-closed aggregation only where multiple agents earn their coordination cost.
kicker_primary: Multi-agent systems
kicker_secondary: Supervisors, handoffs, boundaries and failure propagation
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-17/beginner/
---

## Before you start

This route is for someone who already understands Python type hints, structured tool inputs and the difference between a deterministic workflow and an agent-selected step. Familiarity with basic concurrency is useful, but the lesson explains the bounded first-wave pattern. Use the beginner route first if supervisor and handoff terminology is new.

For the core route, defend each specialist boundary, trace the immutable assignments, validate every correlated result, prove the commercial dependency order and compare the supervisor with the sequential baseline. Treat remote-worker cancellation, durable queues, retries, authenticated source adapters and model-backed specialist evaluation as stretch topics beyond this local coordination lab.

## Multi-agent is a coordination choice

Adding agents does not automatically add intelligence. It adds boundaries,
handoffs, scheduling and more ways to fail. Those costs are worthwhile only when
specialists have genuinely different context, tools, ownership or independent
work.

Week 17 extends the fictional procurement investigation with four specialists:

1. document analysis finds the applicable contract threshold;
2. SQL analysis calculates a dated price variance;
3. supplier-risk assessment classifies status and incidents; and
4. commercial recommendation combines validated findings.

A central supervisor dispatches the first three as one bounded parallel wave,
validates every result and then calls the commercial specialist. The same domain
components also run through one sequential baseline. Equal outputs make the
architecture comparison honest: the supervisor adds isolation and one parallel
stage, but also adds four inter-agent handoffs.

If agents, handoffs and parallel execution are new, start with the
[beginner version]({{ '/weeks/week-17/beginner/' | relative_url }}).

The [Week 17 assessment]({{ '/assessments/week-17/' | relative_url }}) draws
10 balanced questions from a bank of 100, with explanations and browser Python
checks.

| Time | Focus | Evidence to retain |
| --- | --- | --- |
| Hour 1 | Decide whether multiple agents are justified | one boundary table |
| Hour 2 | Define supervisor and specialist contracts | strict assignment/result schemas |
| Hour 3 | Implement three evidence specialists | isolated findings with provenance |
| Hour 4 | Add commercial synthesis | explicit decision precedence |
| Hour 5 | Coordinate one bounded parallel wave | stable trace and worker bound |
| Hour 6 | Propagate coordination failures | failed runs with no report |
| Hour 7 | Build the sequential baseline | outcome and structural comparison |
| Hour 8 | Test and explain the trade-off | CLI smoke, suite and interview answer |

## Give every specialist one defensible reason to exist

The test is not “can I write a different prompt?” The test is “does this boundary
own a coherent capability that benefits from isolation?”

| Specialist | Owned context and capability | Narrow result | Why separate here |
| --- | --- | --- | --- |
| Document | governed contract source and terms interpretation | threshold or explicit absence | document tooling and policy text differ from relational analysis |
| SQL | purchase-order and reference-price rows | exact dated variance | query access and numeric validation form a distinct boundary |
| Supplier risk | supplier register and incidents | status and risk level | risk data and governance may have different owners and permissions |
| Commercial | three approved finding types and decision policy | recommendation and evidence list | synthesis should not retrieve or mutate sources |

The commercial specialist would be a poor place to hide another document search
or SQL query. That would make its input contract untruthful and blur access
control, testing and failure ownership.

Likewise, do not create a formatting agent, a percentage agent and a sentence
agent merely to increase the agent count. Those tiny steps share one context and
one decision path; normal functions are clearer.

**Checkpoint:** Why does the SQL specialist exist? Not because SQL sounds
specialized, but because it owns a distinct governed source, exact comparison
logic and a narrow result that can be tested independently.

## Name the pattern precisely

“Multi-agent” covers several architectures. Two are easy to confuse:

| Pattern | Who retains control? | Typical use |
| --- | --- | --- |
| Supervisor with subagents | central supervisor routes work and combines returned results | isolated domains, centralized control, parallel independent work |
| Conversational handoff | active state or agent changes and can interact directly with the user | staged support or another multi-turn transfer of control |

This lab uses the first pattern. The supervisor remains in control. It passes
typed work assignments to specialists and receives typed findings. We still call
those boundary messages **handoffs**, but they transfer data and responsibility
for a subtask, not ownership of the user conversation.

That distinction matters in design reviews. Saying only “the agents hand off”
does not reveal who owns state, who may speak to the user, how control returns or
which component is accountable for the final result.

## Make handoffs smaller than prompts

A handoff is a contract, not a dump of everything the supervisor knows. The
document assignment contains only:

~~~python
class DocumentAssignment(StrictModel):
    run_id: Identifier
    case_id: Identifier
    specialist: Literal[SpecialistName.DOCUMENT]
    purchase_order_id: Identifier
    source: SourceReference
~~~

It excludes the raw conversation, SQL rows, risk record and commercial policy.
The result returns the same run/case identity, the source reference, whether terms
were found and the threshold.

Every Week 17 model is:

- strict, so an integer cannot silently become a run ID;
- closed, so undeclared transcript or prompt fields are rejected;
- frozen, so a worker cannot mutate its assignment in place; and
- correlated, so the supervisor can reject the right type from the wrong run.

Source references include a SHA-256 digest. The specialist recalculates the
fixture digest before returning a finding. That detects changed source bytes. It
does not prove the source was correct, identify its author or authorize access.

## Keep aggregate state in one place

Shared mutable state creates coordination bugs that are hard to reproduce. One
specialist may overwrite another field, read a half-complete value or depend on
which worker finishes first.

Week 17 uses a simpler rule:

- specialists receive immutable assignments;
- specialists return immutable findings;
- specialists never read one another's state;
- the supervisor owns the result collection; and
- the commercial specialist receives one immutable aggregate assignment.

This is message passing, even though the teaching implementation runs in one
Python process. A production queue or service boundary would add serialization,
delivery and retry concerns, but the ownership rule should remain visible.

Do not confuse supervisor-owned state with globally shared conversation memory.
The Week 16 case store is not copied into every specialist. Each role receives the
minimum selected data for the current job.

## Parallelize independence, not dependency

Document, SQL and supplier-risk analysis depend on the case but not on one
another. They form one parallel group. Commercial recommendation depends on all
three and therefore forms a second stage.

~~~text
stage 1: document + SQL + supplier risk
stage 2: commercial recommendation
stop:    human approval
~~~

The lab submits exactly three first-wave callables to a
`ThreadPoolExecutor(max_workers=3)`. Threads fit this small local demonstration
of I/O-shaped specialist calls. They do not make CPU-heavy Python automatically
faster and they are not a production distributed-job system.

Bound the work explicitly:

- keep an allowlist of four specialists;
- submit each first-wave role once;
- cap the worker count at three;
- do not let specialists spawn specialists;
- run commercial synthesis once; and
- terminate at approval or failure.

The futures may finish in any order. The public trace does not. The supervisor
collects results in the declared document, SQL, supplier-risk order, so repeated
runs produce stable evidence and tests.

## Validate before merging a result

A Python object returned by a worker is not trusted merely because its function
completed. Before aggregation, the supervisor checks:

1. the exact result class expected for that role;
2. the declared specialist name;
3. the run ID;
4. the case ID; and
5. the role-specific source, order and supplier correlations already checked by
   the specialist.

A valid document finding from another case is still invalid. So is a document
finding returned from the SQL slot. Correlation checks prevent plausible-looking
evidence from silently entering the wrong investigation.

The commercial specialist repeats cross-finding checks. SQL supplier identity
must match risk supplier identity, and all findings must belong to the same run
and case. Defense in depth is useful at a consequential synthesis boundary.

## Separate technical failure from business uncertainty

“Could not complete the system” and “completed the investigation but evidence is
uncertain” need different outcomes.

| Condition | Run status | Report | Reasoning |
| --- | --- | --- | --- |
| missing registry entry | `failed` | none | deployment/configuration fault |
| specialist exception | `failed` | none | required technical work did not complete |
| wrong type, run or case | `failed` | none | coordination integrity failed |
| contract terms not found | `awaiting_approval` | `needs_human` | valid business finding is incomplete |
| complete evidence | `awaiting_approval` | policy result | recommendation still needs a person |

The supervisor catches ordinary exceptions from specialist calls, cancels work
that has not started and returns a controlled reason. It does not invent a
default finding or continue to commercial synthesis.

Local thread cancellation cannot stop a callable that is already running. A real
distributed design also needs per-call deadlines, cooperative cancellation,
idempotency keys, retry classification, durable job state and a policy for late
results. The lab names those remaining requirements rather than pretending a
thread pool solves them.

## Apply commercial policy in one deterministic order

The commercial specialist does not vote across agents. It applies one reviewed
policy:

1. if contract terms or threshold are missing, return `needs_human`;
2. if supplier status is inactive or risk is elevated, return
   `review_required`;
3. if price variance exceeds the contract threshold, return
   `review_required`; and
4. otherwise return `no_review`.

Price math uses `Decimal` and half-even quantization to two decimal places. A
`10.00%` variance remains an exact business value, not a binary-float artifact.

Every report sets `requires_human_approval=true`. Even `no_review` means the
automated investigation found no configured trigger; it does not authorize a
purchase order, supplier message or payment.

## Compare with one workflow using the same rules

An architecture comparison is useful only if the business task stays constant.
`run_single_workflow` invokes the same three evidence components and commercial
policy sequentially. It produces the same report for the same case and run ID.

| Property | Supervisor + specialists | Single workflow |
| --- | --- | --- |
| Domain component calls | 4 | 4 |
| Inter-agent handoffs | 4 | 0 |
| Independent evidence wave | yes | no |
| Dependency stages in this implementation | 2 | 4 |
| Central result validation | explicit at each handoff | component boundary checks |
| Ownership isolation | visible and replaceable | internal to one route |
| Coordination failure surface | larger | smaller |
| Measured production latency | not measured | not measured |

Dependency stages are a structural observation, not a latency claim. The local
functions finish too quickly and do not include model, service, queue or network
behavior. A useful benchmark would use representative workloads, percentiles,
timeouts, errors, token usage and cost.

## Know when multiple agents are unnecessary

Prefer one workflow or one agent with ordinary tools when:

- all steps need the same small context and permissions;
- later steps depend on every earlier step;
- deterministic functions already express the policy;
- the task is cheap enough that parallelism has no material value;
- separate ownership or deployment is unlikely;
- more model calls would add cost and inconsistency; or
- the team cannot observe and operate the extra failure paths.

Use specialists when context isolation, distinct governance, independent team
ownership, parallel work or separately evaluated capabilities materially improve
the system.

Week 17 deliberately sits near the boundary. The source domains are distinct and
the first wave is independent, so a supervisor is defensible. The sequential
workflow remains simpler and reaches the same answer. Neither architecture wins
without deployment evidence and organizational requirements.

## Test coordination behavior, not agent theatre

The test suite proves observable contracts:

- all four business routes return the expected recommendation;
- three first-wave workers reach a synchronization barrier concurrently;
- commercial dispatch occurs after all required results;
- repeated runs have identical findings and trace;
- unknown fields and coerced identities are rejected;
- changed source digests fail closed;
- missing, raising and identity-mismatched specialists produce no report;
- worker count and fan-out stay bounded;
- the sequential baseline returns an equal report; and
- comparison output records no fake latency measurement.

Avoid tests that only assert a prompt contains the word “specialist.” The system
contract is routing, isolation, validation, policy and failure behavior.

Run the focused evidence:

~~~shell
python -m labs.week_17.demo smoke
python -m pytest tests/test_week17_multi_agent.py -q
python -m ruff check labs/week_17 tests/test_week17_multi_agent.py
python -m ruff format --check labs/week_17 tests/test_week17_multi_agent.py
python -m mypy --strict --explicit-package-bases labs/week_17 tests/test_week17_multi_agent.py
~~~

## A concise interview answer

> I use multiple agents only for defensible ownership boundaries. In this system,
> document, SQL and supplier-risk specialists receive minimal immutable handoffs
> and run as one bounded independent wave. The supervisor owns aggregate state,
> validates type and run/case identity, then invokes commercial synthesis. A
> technical specialist fault fails closed; missing valid evidence becomes an
> explicit human decision. The same rules also run in one sequential workflow,
> which exposes the trade-off: specialists add isolation and a parallel stage but
> also add four handoffs and more operational failure paths. I would choose using
> representative latency, cost, quality and ownership evidence, not agent count.

## Independent exercises

1. Add a delivery-performance specialist. Write its owned source, minimal
   assignment and result contract before changing the registry.
2. Add an overall deadline without leaving background work unaccounted for.
   Explain what a local thread cannot cancel safely.
3. Introduce one retryable source error and one non-retryable validation error.
   Prove retries are bounded and idempotent.
4. Add a test where a valid finding carries the wrong run ID. Confirm commercial
   synthesis is never called.
5. Measure a representative service-backed version. Report p50/p95 latency,
   failure rate, calls and cost for both architectures.
6. Replace the deterministic document specialist with a model adapter while
   preserving the assignment/result boundary. Add an evaluation dataset before
   considering deployment.

## Finish with evidence

You are done when you can show:

- one written reason for every specialist;
- minimal typed handoffs with source provenance;
- one bounded independent wave and one dependent stage;
- supervisor-owned aggregation with stable trace order;
- fail-closed technical errors and explicit business uncertainty;
- an approval boundary with no external action;
- equal supervisor/workflow reports on the controlled cases; and
- passing smoke, tests, lint, format and strict typing.

Use the [Week 17 assessment]({{ '/assessments/week-17/' | relative_url }}) to
practise specialist boundaries, minimal handoffs, dependency order, fail-closed
coordination, exact decision policy and evidence-bounded architecture comparison.

## Sources and further reading

- [LangChain multi-agent overview](https://docs.langchain.com/oss/python/langchain/multi-agent)
  for pattern selection, context engineering, parallelization and the warning
  that a single agent can often solve the same task.
- [LangChain subagents](https://docs.langchain.com/oss/python/langchain/multi-agent/subagents)
  for central supervisor control, isolated context, specialist inputs/outputs and
  the simpler-single-agent alternative.
- [LangChain handoffs](https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs)
  for the distinct state-driven transfer-of-control pattern.
- [Python `concurrent.futures`](https://docs.python.org/3.13/library/concurrent.futures.html)
  for executor, future, worker-bound, exception and shutdown behavior.
- [Week 17 lab](https://github.com/kogantisasank831-ux/Prep/tree/main/labs/week_17)
  for the complete local implementation and tests.
