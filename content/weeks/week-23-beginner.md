---
layout: week
week: 23
phase: 6
status: review
version: 1.0.0
last_reviewed: 2026-11-11
estimated_hours: 8
permalink: /weeks/week-23/beginner/
title: "Answer an AI system-design question without getting lost"
description: Use twelve simple questions to turn an open-ended design prompt into a measurable, safe and testable answer.
summary: First understand the problem, then choose components, then explain how you know the system works and fails safely.
kicker_primary: Beginner path
kicker_secondary: One repeatable answer map for six interview cases
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-23/
---

## Before you start

You should know the basic purpose of an API, database, model and retrieval. The
[production route]({{ '/weeks/week-23/' | relative_url }}) adds capacity math,
trust boundaries, release gates and segmented evaluation.

The [Week 23 assessment]({{ '/assessments/week-23/' | relative_url }}) draws ten
balanced questions.

## Ask twelve questions in order

1. What does the user need?
2. How will success and harm be measured?
3. Which data is needed and who owns it?
4. What are the major services and data flows?
5. Does the system retrieve information or call tools?
6. Which model class fits the task, and why?
7. How will we test quality before launch?
8. How will we deploy and roll back?
9. What should be monitored?
10. Who is allowed to see or do what?
11. How much traffic and cost should we expect?
12. What happens when each dependency fails?

Do not begin with “I will use framework X.” A framework is one implementation
choice, not the requirement.

## Add four sentences to every section

For each question write:

- **Decision:** what you propose.
- **Evidence:** what measurement would test it.
- **Trade-off:** what the choice improves and gives up.
- **Failure control:** how a problem is detected and contained.

The lab scores these four fields. It does not know whether the decision is
technically correct; a human must challenge that.

## Work one small example

For an employee document assistant:

- Requirement: answer only from documents the employee may read.
- Metric: permission-negative tests must all be blocked.
- Data: documents, versions and permission metadata.
- Retrieval: filter by permission before semantic ranking.
- Model: start with one capable baseline, then compare smaller options.
- Evaluation: grounded answers, citations, abstentions and permission tests.
- Failure: if permission data is stale, stop instead of returning text.

Notice that the database and model appear only after the user and safety need.

## Run the cases

~~~shell
python -m labs.week_23.demo cases
python -m labs.week_23.demo review --case enterprise-rag
python -m labs.week_23.demo review --case enterprise-rag --incomplete
python -m labs.week_23.demo smoke
~~~

Choose one case and replace every sample sentence. Say the answer aloud in 20
minutes, then repeat it in 10. Ask a friend to change one constraint and update
the design.

## Completion checklist

- Use all twelve questions without reading from the page.
- Declare assumptions instead of inventing facts.
- Give one metric for quality, safety, latency and cost.
- Explain one rejected alternative.
- Name a timeout, stale-data or permission failure.
- State that a structural score is not architecture approval.
