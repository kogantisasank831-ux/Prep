# Week 1 ChatGPT Web Generation Instructions

## Files to attach

Attach both of these repository files to a new ChatGPT Web conversation:

1. `content/templates/chatgpt-web-prompt.md`
2. `content/outlines/week-01-outline.md`

## Prompt to paste

```text
Create the complete Week 1 learning module using the two attached files.

Treat `week-01-outline.md` as the approved and binding content scope. Treat
`chatgpt-web-prompt.md` as the generation policy and required document schema.
Resolve its placeholders as follows:

- WEEK_NUMBER: 1
- PHASE_NUMBER: 1
- WEEK_TITLE: Python for production AI systems
- PREREQUISITES: ["Working knowledge of Python syntax", "Basic JSON knowledge"]
- APPROVED_OUTLINE: the complete attached `week-01-outline.md`

Additional binding requirements:

1. Target Python 3.13.12 and installation through `pip`.
2. Use a small FastAPI application with thin routes and a separated service
   layer; do not replace it with a framework-independent-only example.
3. Support UTF-8 `.txt` documents only.
4. Explain Python classes explicitly before relying on them. Cover instance state,
   class attributes, constructors, instance/class/static methods, composition,
   inheritance, and when a class is unnecessary.
5. Explain that Pydantic models are Python classes derived from `BaseModel`.
   Cover annotated fields, model configuration, field validators, model
   validators, serialization, and appropriate model methods using Pydantic v2
   concepts.
6. Contrast plain classes, dataclasses, frozen dataclasses, and Pydantic models by
   responsibility and boundary placement.
7. Prefer content quality and completeness over any fixed duration or word count.
8. Use official Python, FastAPI, Pydantic, pytest, and relevant PEP documentation
   as primary sources. Include direct source URLs and flag claims that require
   current-version verification.
9. Do not claim that any code, command, test, or URL was executed or verified.
10. Return one Markdown document only. Do not wrap the entire document in a code
    fence and do not add commentary before or after it.

Before responding, silently confirm that all learning outcomes, worked examples,
independent exercises, interview outcomes, and acceptance criteria from the
approved outline are covered.
```

## Save the response

Save the exact generated response without corrections as:

```text
content/inbox/week-01-draft.md
```

Do not save it directly as `content/weeks/week-01.md`. The inbox version must
undergo structural review, source verification, executable-code validation, and
HITL review before publication.

