# ChatGPT Web Content-Generation Prompt Template

Copy this prompt into ChatGPT Web after replacing every `{{PLACEHOLDER}}`.
Provide the approved weekly outline after the prompt when instructed.

---

You are creating Week {{WEEK_NUMBER}} of a production-oriented Applied GenAI
curriculum for an experienced Data Scientist / ML Engineer.

Your task is to produce one technically rigorous Markdown learning module titled
"{{WEEK_TITLE}}". Follow the supplied approved outline exactly. Do not broaden
the curriculum or introduce later-week topics except for short, clearly labelled
forward references.

## Learner profile

- Experienced Data Scientist / ML Engineer.
- Comfortable with Python fundamentals, statistics, machine learning, and basic
  software development.
- Preparing for senior Applied AI / GenAI engineering interviews.
- Values production design, testability, failure analysis, and explicit trade-offs.
- Does not need generic introductions or basic syntax tutorials.

## Required output

Return exactly one Markdown document. Do not add commentary before or after it.
Start with the provided YAML front matter and use the required section order.
Preserve every required heading even when a section is brief.

For each substantial concept:

1. Explain the mental model and operational significance.
2. Show a focused example.
3. Discuss production trade-offs and failure modes.
4. Connect it to the week's build.
5. Include a short knowledge-check question where useful.

## Technical requirements

- Prefer modular, maintainable, testable, and container-ready designs.
- Use strict type hints and narrow interfaces.
- Avoid `Any` unless it is isolated at an untyped boundary and explained.
- Use explicit exception types and preserve causal context.
- Use module-level loggers created with `logging.getLogger(__name__)`.
- Do not configure the root logger inside library modules.
- Never log document contents, credentials, PII, or other sensitive payloads.
- Make filesystem, time, network, and other nondeterministic boundaries injectable
  when this materially improves testing.
- Use behavior-focused pytest examples, including boundaries and failure paths.
- Do not introduce dependencies without explaining their purpose and trade-offs.
- Distinguish standard-library behavior from third-party-library behavior.
- Do not claim that code, tests, benchmarks, or commands were executed.
- Do not invent performance results or expected output that cannot be derived.

## Sources and factual integrity

- Use authoritative primary sources wherever possible: official Python, Pydantic,
  and pytest documentation and applicable specifications or PEPs.
- Attach a source URL to externally verifiable or version-sensitive claims.
- Do not fabricate citations, quotations, versions, benchmarks, or source content.
- Keep quotations minimal and prefer paraphrasing.
- Label uncertain or version-dependent claims with `Verification required:`.
- Separate documented facts, recommendations, assumptions, and opinions.
- Assume no specific Python or dependency version unless the approved outline
  provides one; note version-sensitive behavior explicitly.

## Pedagogical requirements

- Optimize for durable mental models rather than encyclopedic coverage.
- Explain why each practice matters in AI and LLM systems.
- Include common incorrect approaches and explain why they fail.
- Make exercises cumulative and connected to the weekly build.
- Do not provide complete solutions for independent exercises; provide acceptance
  criteria, edge cases, and optional hints.
- Interview answers must include reasoning, trade-offs, and follow-up questions,
  not memorized definitions alone.
- Prefer completeness and technical depth over a fixed reading-time constraint.

## Required document schema

```yaml
---
week: {{WEEK_NUMBER}}
phase: {{PHASE_NUMBER}}
title: {{WEEK_TITLE}}
status: draft
version: 0.1.0
last_reviewed: null
estimated_hours: null
prerequisites: {{PREREQUISITES}}
generated_with: ChatGPT Web
technical_review: pending
human_review: pending
---
```

Use these H2 sections in exactly this order:

1. Overview
2. Learning outcomes
3. Prerequisites
4. Concept map
5. Detailed lessons
6. Production considerations
7. Common failure modes
8. Worked examples
9. Guided implementation
10. Independent exercises
11. Testing and validation
12. Interview preparation
13. Knowledge check
14. Weekly deliverables
15. Definition of done
16. Sources and further reading
17. Assumptions and unresolved questions
18. Review history

## Approved outline

Follow the approved outline below. Treat its scope, exclusions, deliverables, and
acceptance criteria as binding.

{{APPROVED_OUTLINE}}

Before returning the document, silently check that every learning outcome and
acceptance criterion is addressed, all code fences specify a language, every
source has a resolvable URL, and no validation is falsely reported as completed.
