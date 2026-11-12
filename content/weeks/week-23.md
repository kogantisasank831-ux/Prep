---
layout: week
week: 23
phase: 6
status: review
version: 1.0.0
last_reviewed: 2026-11-11
estimated_hours: 8
permalink: /weeks/week-23/
title: "Defend a GenAI system design from requirement to failure mode"
description: Practise six system-design cases with a twelve-part answer structure and a transparent decision/evidence/trade-off/failure rubric.
summary: Strong design answers begin with measurable requirements and finish with security, cost and failure—not a list of fashionable components.
kicker_primary: GenAI system design
kicker_secondary: Six cases, twelve dimensions and explicit trade-offs
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-23/beginner/
---

## Before you start

This route assumes working knowledge of RAG, agents, APIs, model serving and
production monitoring. Use the [beginner route]({{ '/weeks/week-23/beginner/' | relative_url }})
for a guided answer scaffold.

The [Week 23 assessment]({{ '/assessments/week-23/' | relative_url }}) checks
design reasoning, calculations and failure handling.

## Use one answer spine

Under interview pressure, a stable sequence prevents attractive details from
hiding missing fundamentals:

1. requirements and non-goals;
2. success, safety and operational metrics;
3. data sources, ownership and freshness;
4. architecture and trust boundaries;
5. retrieval and tools;
6. model choice and routing;
7. offline and online evaluation;
8. deployment and release strategy;
9. monitoring and incident evidence;
10. security and privacy;
11. capacity and cost; and
12. failure behavior and recovery.

For every dimension state four things: the decision, evidence that would test
it, the trade-off, and a plausible failure control. The local rubric awards one
point for each field. It deliberately does not score keywords or claim semantic
correctness.

## Clarify the problem before drawing boxes

Ask who uses the system, what decision it supports, what happens when it is
wrong, which data it may access and what latency/volume matters. Separate:

- functional behavior from quality expectations;
- average traffic from peaks and bursts;
- advisory output from consequential writes;
- freshness from consistency;
- launch scope from future scale; and
- measured constraints from assumptions.

Declare assumptions rather than silently inventing numbers. An interviewer can
then change one assumption and see whether the architecture adapts.

## Translate goals into gates

“Accurate and fast” is not measurable. Choose metrics tied to the case:

| Concern | Example evidence |
| --- | --- |
| retrieval | recall@k, permission-negative pass rate, stale-document rate |
| answer | grounded correctness, citation support, abstention quality |
| agent | task success, unsafe action rate, approval bypass rate |
| service | p50/p95/p99 latency, error rate, queue age, saturation |
| economics | input/output tokens, GPU-seconds, cost per completed task |
| rollout | regression set, canary threshold, rollback condition |

Do not collapse all quality into one average. Segment by language, document
type, difficulty, tenant risk and failure class.

## Show the data and trust paths

Describe ingestion, validation, storage, indexing, permission updates, retention
and deletion before selecting a vector database. At query time, show where
identity enters, where authorization is enforced, what context reaches the
model and what leaves the boundary.

For tools, specify schemas, least privilege, timeout/retry policy, approval,
idempotency and audit behavior. A consequential tool needs a much stronger
contract than a read-only search.

## Choose models after constraints

Model selection follows task evidence:

- modality and context requirements;
- structured-output/tool support;
- quality by task segment;
- latency and throughput under target load;
- privacy and deployment boundary;
- fallback compatibility; and
- cost under expected token sizes.

Explain routing and escalation criteria. Name the evaluation that would let you
replace a large model with a smaller one. Avoid saying “use model X because it
is best” without workload evidence.

## Calculate one capacity path

A design answer becomes concrete when it carries units:

~~~text
arrival rate = active users × requests per user / time window
required concurrency ≈ arrival rate × average service time
daily cost = requests × cost per completed request
~~~

Then test peak factors, queueing, retries, cache hit rate, fallback capacity and
headroom. State whether a number is measured, vendor-documented or assumed.

## Design the failure answer before the happy demo

For every remote dependency ask:

- What can time out, throttle, return invalid data or become stale?
- Is retry safe and which layer owns the budget?
- Is there a contract-compatible fallback?
- What does the user see when behavior degrades?
- Which metric alerts an operator?
- How is state reconciled after an ambiguous write?

Include model outage, retrieval failure, policy-store failure, partial batch
failure and bad rollout. “The framework handles it” is not a failure design.

## Practise six cases

The lab supplies:

1. enterprise RAG with permission drift;
2. an approval-bound procurement agent;
3. a real-time support copilot;
4. a multimodal document pipeline;
5. a cost-aware local-model gateway; and
6. a continuous agent-evaluation platform.

~~~shell
python -m labs.week_23.demo cases
python -m labs.week_23.demo review --case enterprise-rag
python -m labs.week_23.demo review --case procurement-agent --incomplete
python -m labs.week_23.demo smoke
python -m pytest tests/test_week23_system_design.py -q
~~~

The complete sample receives 48/48 because every structural field is filled.
Its placeholder sentences are not a strong design. Replace each with a concrete
decision, calculation and test.

## Rubric and limits

Five dimensions are critical: requirements, evaluation, security, cost and
failure. A mock-interview readiness pass needs at least 36/48, no critical score
below three, one declared assumption and one rejected alternative.

The rubric cannot prove feasibility, consistency, security or semantic quality.
A human reviewer must challenge the answer and the candidate must update it
without losing the stated goal.

## Completion checklist

- Lead with requirements, non-goals and assumptions.
- Define quality, safety, operations and cost metrics.
- Trace data, identity and trust boundaries.
- Justify retrieval, tools and model choices with evidence.
- Carry units through one capacity and cost estimate.
- Include deployment, monitoring, rollback and failure behavior.
- Compare at least one rejected alternative.
- Complete two timed cases and one adversarial follow-up round.
