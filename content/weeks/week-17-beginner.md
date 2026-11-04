---
layout: week
week: 17
phase: 4
status: approved
version: 1.0.1
last_reviewed: 2026-11-04
estimated_hours: 8
permalink: /weeks/week-17/beginner/
title: "Build a small specialist team with one careful supervisor"
description: Learn multi-agent basics through four clear procurement roles, small handoff cards, safe parallel work and a comparison with one simple workflow.
summary: "A multi-agent system is a team design: give each specialist one job, let the supervisor own the case and stop safely when a required result fails."
kicker_primary: Beginner path
kicker_secondary: One supervisor, four specialists, bounded work
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-17/
---

## Think of a small investigation team

Imagine one analyst must inspect a contract, query prices, check supplier risk and
write a commercial recommendation. The analyst could do every step alone. Or a
supervisor could ask three specialists to inspect their own sources and then ask
a fourth specialist to combine the results.

That second design is a **multi-agent system**. In Week 17, “agent” means a
component with one owned job and a clear input/output contract. The lab uses
deterministic Python functions instead of model calls so you can see the
coordination rules without random answers, API keys or provider cost.

The [production version]({{ '/weeks/week-17/' | relative_url }}) explains strict
schemas, correlation checks, failure propagation and the architecture comparison
in more depth.

The [Week 17 assessment]({{ '/assessments/week-17/' | relative_url }}) draws
10 balanced questions from a bank of 100, with explanations and browser Python
checks.

## Meet the five roles

| Role | Simple question | Output |
| --- | --- | --- |
| Supervisor | Who should work, and are all results valid? | one controlled run |
| Document specialist | What variance does the contract allow? | threshold or “not found” |
| SQL specialist | How far is current price from reference price? | exact percentage |
| Risk specialist | Is this supplier active and incident-free? | low or elevated risk |
| Commercial specialist | What do the three findings mean together? | recommendation and evidence |

The supervisor does not pretend to be the contract, SQL or risk expert. The
specialists do not approve purchases. The commercial specialist does not contact
a supplier. Every successful report stops for a person.

## Ask why each specialist exists

Do not split a system just because five agents look impressive. Each extra role
creates another message, another validation step and another possible failure.

These three source specialists are reasonable because they use different kinds
of information:

- contract documents;
- relational price data; and
- a supplier risk register.

They could also have different permissions or different teams maintaining them.
The commercial role exists because combining approved finding types is a separate
decision from retrieving each source.

A “percentage-formatting agent” would not be reasonable here. One normal Python
function can format a percentage with less complexity.

## Use small handoff cards

When the supervisor gives work to a specialist, it sends a **handoff**. Think of
it as a small job card:

~~~text
run: run-17
case: price-spike
specialist: document
purchase order: PO-1701
source: contract-1701-v1
source fingerprint: 134e5c...
~~~

The card does not include the whole conversation, every source or another
specialist's notes. Smaller handoffs are easier to understand, validate and keep
within the right access boundary.

The document result is also small:

~~~text
run: run-17
case: price-spike
specialist: document
terms found: yes
maximum variance: 5.00%
source: contract-1701-v1
~~~

Run ID and case ID matter. A correct result from yesterday's run or another case
must not be mixed into this investigation.

## Keep one owner for the shared case

A common mistake is letting every specialist edit one shared dictionary. Then the
answer can depend on timing:

- one worker may read before another has written;
- two workers may overwrite the same key;
- a half-finished result may look complete; or
- the final trace may change on every run.

Week 17 gives the supervisor the only aggregate result list. Each specialist gets
a frozen assignment and returns a frozen finding. It cannot edit another role's
work.

The commercial specialist receives the three completed findings only after the
supervisor validates them.

## Run independent jobs together

Contract, price and risk checks do not depend on one another, so the supervisor
can start all three together:

~~~text
first stage:  document + SQL + supplier risk
second stage: commercial recommendation
final stop:   human approval
~~~

This is **parallel execution**. The lab uses at most three worker threads. It does
not create more workers in a loop, and a specialist cannot start more agents.

The commercial job is different. It needs all three earlier results, so starting
it at the same time would be wrong. Good parallel design respects dependencies;
it does not start everything at once.

## Keep the trace predictable

Workers may finish in different orders. If the system records whichever finishes
first, logs and tests can jump around even when the answer is the same.

The supervisor starts document, SQL and risk in that order, then collects and
records them in that same declared order. The work is concurrent, while the
public trace stays repeatable.

That does not hide failures. If the SQL job fails, the trace names SQL and the
run fails without creating a commercial report.

## Treat two kinds of problems differently

Some problems mean the system broke. Others mean the system learned that a human
decision is needed.

| Example | Meaning | Result |
| --- | --- | --- |
| document specialist raises an error | technical work did not complete | failed run, no report |
| SQL returns another case ID | unsafe coordination mismatch | failed run, no report |
| contract was searched but terms were absent | valid evidence is incomplete | `needs_human` report |
| supplier has open incidents | valid risk trigger | `review_required` report |

Never turn a crashed specialist into an empty finding and continue. That would
make missing work look like real evidence.

## Follow one clear commercial rule

After validation, the commercial specialist checks in this order:

1. No contract threshold? Return `needs_human`.
2. Supplier inactive or elevated risk? Return `review_required`.
3. Price variance above threshold? Return `review_required`.
4. Otherwise return `no_review`.

The SQL specialist uses exact decimal arithmetic. For the `price-spike` case,
the current price is `2.20`, the reference is `2.00` and the variance is exactly
`10.00%`. The `5.00%` contract threshold is exceeded.

The final report says a human must review it. The code cannot change an order,
email a supplier or pay anyone.

## Run the specialist route

From the repository root, install the declared development environment:

~~~shell
python -m pip install -r requirements-dev.txt
~~~

Then run the supervisor:

~~~shell
python -m labs.week_17.demo run --case price-spike --run-id beginner-17
~~~

Look for these fields in the JSON:

~~~text
status: awaiting_approval
recommendation: review_required
specialist_calls: 4
handoffs: 4
parallel_groups: 1
dependency_stages: 2
~~~

Try the other cases:

~~~shell
python -m labs.week_17.demo run --case stable-price --run-id stable-17
python -m labs.week_17.demo run --case missing-terms --run-id missing-17
python -m labs.week_17.demo run --case supplier-risk --run-id risk-17
~~~

Expected recommendations are `no_review`, `needs_human` and
`review_required`, respectively.

## Compare with one simple workflow

Run the same work sequentially:

~~~shell
python -m labs.week_17.demo workflow --case price-spike --run-id beginner-17
~~~

Then compare both designs:

~~~shell
python -m labs.week_17.demo compare --case price-spike --run-id beginner-17
~~~

Both routes should return the same recommendation. The differences are in
coordination:

| Measure | Supervisor team | One workflow |
| --- | --- | --- |
| Component calls | 4 | 4 |
| Agent handoffs | 4 | 0 |
| Dependency stages | 2 | 4 |
| Parallel evidence stage | yes | no |
| Extra coordination failures | more | fewer |

Two stages do not prove the supervisor is faster in production. This lab does not
measure network, model, queue or service time. It shows the dependency shape.

Choose the team when source isolation, permissions, independent ownership or
parallel work are valuable. Choose the workflow when one path is easier to build,
test and operate.

## Avoid these beginner mistakes

### Sending the whole conversation to every specialist

Send the smallest typed job card. More context can increase cost, confuse the
role and expose information it does not need.

### Letting specialists call one another freely

That can create loops and unbounded fan-out. Keep routing in the supervisor.

### Starting dependent work too early

Commercial recommendation needs three validated findings. It belongs after the
parallel wave.

### Using the first answer that arrives

Fast is not the same as complete. Wait for every required specialist or fail
according to an explicit policy.

### Hiding exceptions as empty results

A technical failure should fail the run. Real missing evidence can be a valid
`needs_human` finding.

### Assuming more agents are better

Every agent needs a reason to exist. If one workflow is clearer and achieves the
same quality, use it.

## Run the tests

~~~shell
python -m labs.week_17.demo smoke
python -m pytest tests/test_week17_multi_agent.py -q
~~~

The checks prove that:

- every business scenario reaches the expected recommendation;
- the first three roles can enter their work concurrently;
- commercial synthesis waits for them;
- repeated traces stay identical;
- wrong case, role and source information is rejected;
- worker count is bounded;
- a failure never produces a report; and
- the simple workflow returns the same report.

## Practice questions

1. What information should the document specialist receive?
2. Why should the risk specialist not edit shared SQL state?
3. Which three jobs are independent?
4. Why must commercial recommendation wait?
5. What should happen if SQL returns the wrong case ID?
6. How is missing contract text different from a crashed document service?
7. Why is a source fingerprint not proof that the source is true?
8. What does a two-stage dependency shape tell you—and what does it not tell you?
9. When would one workflow be the better design?
10. How would you justify each of the four specialists in an interview?

Try the [Week 17 assessment]({{ '/assessments/week-17/' | relative_url }}) for a
random paper covering specialist jobs, small handoffs, safe parallel work,
failure handling, human approval and the one-workflow comparison.

## Read alongside the lab

- [Week 17 production lesson]({{ '/weeks/week-17/' | relative_url }})
- [Week 17 lab](https://github.com/kogantisasank831-ux/Prep/tree/main/labs/week_17)
- [LangChain multi-agent overview](https://docs.langchain.com/oss/python/langchain/multi-agent)
- [LangChain subagents guide](https://docs.langchain.com/oss/python/langchain/multi-agent/subagents)
- [LangChain handoffs guide](https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs)
- [Python futures documentation](https://docs.python.org/3.13/library/concurrent.futures.html)
