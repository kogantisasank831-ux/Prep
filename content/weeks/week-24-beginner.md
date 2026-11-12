---
layout: week
week: 24
phase: 6
status: approved
version: 1.0.0
last_reviewed: 2026-11-12
estimated_hours: 8
permalink: /weeks/week-24/beginner/
title: "Tell a clear project story using facts you can defend"
description: Collect evidence, separate your work from team work and practise short, medium and deep versions of one project.
summary: Start with what happened, what you owned, what changed, how it was measured and what you learned.
kicker_primary: Beginner path
kicker_secondary: One evidence sheet and three ways to explain it
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-24/
---

## Before you start

Choose one project you are allowed to discuss. Remove client names, secrets and
private data. The [production route]({{ '/weeks/week-24/' | relative_url }}) adds
causal attribution, adversarial follow-ups and lead-level decision defence.

The [Week 24 assessment]({{ '/assessments/week-24/' | relative_url }}) draws ten
balanced practice questions.

## Fill an evidence sheet

Write short factual answers:

1. What problem existed?
2. What was the team asked to deliver?
3. What did you personally own?
4. Which two actions did you take?
5. Which decision did you make, and why?
6. Which alternative did you reject?
7. What changed, and how was it measured?
8. What failed or surprised the team?
9. What limitation remains?
10. What would you do differently?

For every number, add its source. Mark it `individual`, `team` or
`organization`. If you cannot defend the source, do not make the number sound
more exact.

## Use STAR, then add evidence

- **Situation:** enough context to understand the problem.
- **Task:** the outcome and constraints.
- **Action:** what you personally did and decided.
- **Result:** measured change with honest attribution.
- **Learning:** failure, limitation and next step.

Avoid spending most of the answer on situation. Interviewers need your decisions
and evidence.

## Practise three versions

| Version | Include |
| --- | --- |
| two minutes | problem, role, one action, one result, limitation |
| ten minutes | constraints, decisions, evaluation, failure, leadership, learning |
| deep dive | remaining actions, metrics, alternatives, architecture and operations |

All three must use the same facts. A longer version adds detail; it must not add
new achievements.

## Run the fictional example

~~~shell
python -m labs.week_24.demo story --depth two-minute
python -m labs.week_24.demo story --depth ten-minute
python -m labs.week_24.demo story --depth deep-dive
python -m labs.week_24.demo review
~~~

The sample project is invented. Replace it completely. Record yourself, check
every claim against your evidence sheet and ask a friend: “Which part was yours?”

## Completion checklist

- Separate your action from the team's result.
- Give a source for each important number.
- Name one decision, alternative and consequence.
- Include one failure and one limitation.
- Tell the same facts at three depths.
- Remove confidential details before sharing or recording.
