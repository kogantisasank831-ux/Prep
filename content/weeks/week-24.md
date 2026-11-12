---
layout: week
week: 24
phase: 6
status: approved
version: 1.0.0
last_reviewed: 2026-11-12
estimated_hours: 8
permalink: /weeks/week-24/
title: "Defend project impact without inventing certainty"
description: Build one evidence record, produce 2-minute, 10-minute and deep-dive versions, and rehearse technical, failure, leadership and ownership questions.
summary: A credible project story separates personal work, team results, evidence sources, decisions, failures and limitations.
kicker_primary: Project storytelling and mock interviews
kicker_secondary: Grounded claims, three depths and adversarial follow-ups
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-24/beginner/
---

## Before you start

This route is for candidates who have project experience and need to present it
at lead-level depth. Use the [beginner route]({{ '/weeks/week-24/beginner/' | relative_url }})
for the first evidence inventory and STAR structure.

The [Week 24 assessment]({{ '/assessments/week-24/' | relative_url }}) checks
ownership, evidence, trade-offs, failure and leadership reasoning.

## Write evidence before narrative

An interview story should be a view over one source of truth—not a fresh set of
claims each time it is told. Record:

- situation and user/business problem;
- task and constraints;
- personal role and team boundary;
- actions personally taken;
- decisions, reasons, rejected alternatives and consequences;
- metrics with value, baseline, time window, source and attribution;
- a failure or disagreement and response;
- current limitation; and
- reflection and next step.

Remove confidential identifiers and obtain any employer approval required for
external discussion. Never move secrets, private data or proprietary code into
the practice file.

## Attribute impact honestly

Use language that matches evidence:

| Evidence | Safer phrasing |
| --- | --- |
| personally implemented and measured | “I implemented…; my test showed…” |
| shared team delivery | “I owned X; our team delivered Y…” |
| organization business result | “The program reported Y; my component contributed X…” |
| estimate or modelled value | “We estimated Y under these assumptions…” |

Do not turn a team outcome into “I achieved.” Do not turn correlation into
causation. If a number cannot be sourced, qualify it or remove it.

## Prepare three depths from the same facts

### Two minutes

Use situation, task, personal role, one action, one sourced result and one
limitation. This version earns the next question; it does not recite the entire
architecture.

### Ten minutes

Add constraints, major decision and alternative, execution path, evaluation,
failure handling, leadership and reflection. Keep enough structure that an
interviewer can interrupt and branch.

### Deep dive

Add the remaining actions, decisions, metrics, capacity/cost evidence,
interfaces, rollout, monitoring and incident detail. Deep does not mean long
monologue—it means every important claim can survive a follow-up.

## Defend a technical decision

For each major choice answer:

1. What requirement drove it?
2. Which alternatives were considered?
3. What evidence distinguished them?
4. What did the choice make harder?
5. How was failure detected?
6. Under which changed condition would you choose differently?

“We used LangGraph” is not a decision explanation. “We needed durable,
inspectable state between bounded nodes; we compared a simple service workflow,
accepted the orchestration overhead, and tested resume behavior” is defensible.

## Prepare the uncomfortable questions

A lead interview should probe gaps:

- Which part did you personally code or decide?
- What would your teammate say you owned?
- How was the metric measured, and against which baseline?
- What failed first?
- Which safety or permission test failed?
- What did you disagree about?
- What trade-off did you accept?
- How would the system behave at ten times traffic?
- What would you remove if budget were halved?
- What limitation remains today?

Answer “I do not know” when appropriate, then explain how you would find out.
Confident invention is worse than a bounded gap.

## Tell leadership stories with observable behavior

Prepare separate examples for ambiguity, disagreement, mentoring, incident
response and prioritisation. Use situation, action, result and learning. Avoid
personality labels; describe the decision, evidence, communication and outcome.

A leadership story should show how other people could act more effectively—not
only that the candidate completed a difficult technical task alone.

## Run the evidence-grounded lab

~~~shell
python -m labs.week_24.demo story --depth two-minute
python -m labs.week_24.demo story --depth ten-minute
python -m labs.week_24.demo story --depth deep-dive
python -m labs.week_24.demo review
python -m labs.week_24.demo smoke
python -m pytest tests/test_week24_storytelling.py -q
~~~

The included supplier project and every number are fictional teaching data.
Replace the entire `ProjectEvidence` record; do not copy those metrics into a
real interview or résumé.

The rubric checks six visible categories: structure, ownership, evidence,
decisions, failure and reflection. It records provenance but cannot verify truth
externally or judge communication quality.

## Mock-interview loop

1. Record the two-minute version.
2. Transcribe claims and mark their evidence source.
3. Remove filler and unsupported certainty.
4. Ask five follow-ups without notes.
5. Have a reviewer challenge ownership and causality.
6. Update the evidence record first, then regenerate all depths.
7. Repeat with a system-design case from Week 23.

## Completion checklist

- Maintain one evidence source for all story depths.
- Label personal, team and organization attribution.
- Attach source, baseline and window to every important metric.
- Explain two decisions with rejected alternatives.
- Include a real failure, limitation and learning.
- Prepare leadership examples beyond technical heroics.
- Survive five adversarial follow-ups without inventing facts.
- Remove or anonymise confidential material.
