# Rich Content Production Plan

## Objective

Create technically accurate, detailed learning material for the roadmap in
`Path.md`, one week at a time. Content generation will happen manually in
ChatGPT Web to conserve Codex usage. Codex will design the prompts, validate and
normalize the returned content, and integrate approved content into the static
website.

## Core Decisions

- Process exactly one week at a time.
- Use human-in-the-loop approval before publishing each week.
- Use ChatGPT Web for initial content generation.
- Store the approved source content as `content/weeks/week-NN.md`.
- Generate website HTML from the approved Markdown; do not maintain independent
  Markdown and HTML copies manually.
- Treat generated explanations, citations, code, and expected outputs as
  untrusted until reviewed or executed.
- Publish only content with `status: approved`.
- Keep generation provenance, review history, validation transcripts, publication
  status, and internal planning checklists in `content/reviews/`; do not render
  them as learner-facing lesson content.
- Write public lessons as coherent technical narratives rather than curriculum
  specifications or exhaustive reference dumps.

## Responsibilities

### Project owner

- Run the supplied prompt in ChatGPT Web.
- Return the complete response without manually restructuring it.
- Review the content for relevance, depth, clarity, and expected workload.
- Approve the outline and final content.

### Codex

- Read the relevant scope from `Path.md`.
- Produce a self-contained, week-specific generation prompt.
- Inspect the returned content for completeness and internal consistency.
- Verify technical claims against authoritative primary sources when required.
- Move executable examples into appropriate source and test files when needed.
- Run applicable validation and report exactly what was and was not verified.
- Normalize the approved draft into `content/weeks/week-NN.md`.
- Convert or render the Markdown as website content.
- Preserve review status, version, provenance, and source attribution.

### ChatGPT Web

- Generate the requested draft according to the supplied schema and constraints.
- Return Markdown only, without unrelated commentary.
- Explicitly identify uncertainty, assumptions, and claims requiring verification.
- Never invent citations, execution results, benchmarks, or source content.

## Content Lifecycle

Each week moves through the following states:

```text
planned -> outlined -> drafted -> technically-verified -> HITL-review -> approved
```

Rejected or incomplete content returns to `drafted` with recorded review notes.
Published content must not skip technical verification or HITL review.

## Weekly Workflow

### 1. Scope the week

Codex extracts the selected week's requirements from `Path.md` and defines:

- measurable learning outcomes;
- prerequisites;
- concepts in scope;
- concepts explicitly out of scope;
- build deliverables;
- interview outcomes;
- expected study time; and
- acceptance criteria.

The project owner approves this outline before full content generation.

### 2. Prepare the ChatGPT Web prompt

Codex supplies a complete prompt containing:

- the learner profile and assumed technical level;
- the approved weekly scope;
- required output schema;
- required technical depth;
- examples and exercise expectations;
- citation and uncertainty rules;
- requirements for production concerns and failure cases;
- instructions not to claim that code was executed; and
- a requirement to return a single Markdown document.

The prompt should request one bounded artifact. Follow-up prompts should revise
specific sections instead of regenerating the entire document unnecessarily.

### 3. Generate in ChatGPT Web

The project owner runs the prompt in ChatGPT Web and returns the result using one
of these methods, in preference order:

1. Save the exact response as `content/inbox/week-NN-draft.md`.
2. Attach the generated Markdown file in the conversation.
3. Paste the complete response in the conversation when the document is small.

Do not paste the result directly into `week-NN.md`; the inbox copy is unreviewed.

### 4. Structural review

Codex checks that the draft:

- follows the requested schema;
- covers every approved learning outcome;
- contains no unsupported claims of execution or validation;
- distinguishes facts, recommendations, assumptions, and open questions;
- provides useful examples and exercises rather than superficial summaries;
- contains no duplicated or contradictory sections; and
- uses valid, consistently structured Markdown.

### 5. Technical verification

Verification is proportional to the subject:

- Check time-sensitive technical claims against authoritative primary sources.
- Resolve every citation and confirm it supports the associated claim.
- Move substantial code examples into runnable repository files.
- Execute examples and tests using the repository's configured tools.
- Validate commands, SQL, schemas, expected outputs, and failure cases.
- Mark any item that cannot be verified and state the required follow-up.

Model review alone does not count as technical verification.

### 6. Human review

The project owner reviews the draft using the following rubric, scoring each item
from 1 to 5:

| Criterion | Review question |
| --- | --- |
| Correctness | Is the material technically accurate? |
| Depth | Is it suitable for a senior Data Scientist or ML Engineer? |
| Clarity | Can each concept be understood without avoidable ambiguity? |
| Practicality | Does the material support the weekly build? |
| Interview value | Does it prepare the learner to explain and defend decisions? |
| Scope | Can the work reasonably fit the weekly schedule? |

Any criterion below 4 requires a targeted revision or an explicitly accepted
limitation.

### 7. Revise and approve

Codex converts review feedback into targeted prompts for ChatGPT Web or makes
small, verifiable editorial corrections directly. Material technical changes are
returned for human review. After approval:

- set `status: approved`;
- update the version and review date;
- record remaining limitations;
- save the canonical document as `content/weeks/week-NN.md`; and
- retain sufficient provenance to reproduce the generation and review process.

### 8. Integrate into the website

Codex converts or renders the approved Markdown into the week's website page,
then verifies:

- navigation from the roadmap card;
- headings and table of contents;
- code blocks, tables, lists, citations, and callouts;
- responsive behavior;
- keyboard navigation and semantic structure;
- internal links and source links; and
- publication status enforcement.

Only approved content is linked from the public roadmap.

### 9. Retrospective

After completing the week, record:

- unclear explanations;
- exercises that were too easy, difficult, or ambiguous;
- incorrect assumptions;
- missing prerequisites;
- failed examples; and
- improvements for the next week's generation prompt.

Apply corrections as versioned updates rather than silently replacing approved
content.

## Canonical Weekly Document Schema

Each `content/weeks/week-NN.md` file should begin with:

```yaml
---
week: 1
phase: 1
title: Python for production AI systems
status: draft
version: 0.1.0
last_reviewed: null
estimated_hours: null
prerequisites: []
generated_with: ChatGPT Web
technical_review: pending
human_review: pending
---
```

The document should then contain these sections:

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

Sections may contain subsections, but their purpose and order should remain stable
so the website can render every week consistently.

## Prompt Design Rules

Every ChatGPT Web prompt must:

- be self-contained and specific to one week;
- state that the audience is an experienced Data Scientist or ML Engineer;
- request depth, trade-offs, operational concerns, and failure analysis;
- separate conceptual explanation from verified behavior;
- request decimal-safe, secure, typed, testable, and production-grade examples
  where relevant;
- prohibit fabricated sources, benchmarks, test results, and quotations;
- require explicit uncertainty markers;
- require source URLs for externally verifiable claims;
- request Markdown that follows the canonical schema; and
- prohibit extra text before or after the Markdown document.

## File and Version Conventions

- Use zero-padded names: `week-01.md` through `week-30.md`.
- Use semantic content versions: `0.x` for drafts and `1.0.0` for the first
  approved publication.
- Increment the patch version for corrections that do not change learning goals.
- Increment the minor version when examples or lessons materially expand.
- Require renewed approval when learning outcomes or technical recommendations
  change.
- Keep `Path.md` as the curriculum index and weekly files as detailed content.

## Website Architecture Decision

The current browser parser is suitable for the high-level roadmap but not for
rich weekly documents containing code blocks, tables, diagrams, citations, and
callouts. Before publishing Week 1, select and approve a Markdown-to-HTML build or
rendering approach.

The recommended direction is a lightweight static-site generator that:

- reads approved Markdown during the build;
- produces static HTML for GitHub Pages;
- rejects invalid metadata or unapproved content;
- supports syntax highlighting and structured navigation; and
- avoids client-side content generation and duplicated HTML sources.

Adopting a generator changes the build and deployment architecture and therefore
requires explicit project-owner approval before implementation.

## Initial Execution Sequence

1. Create the reusable ChatGPT Web prompt template.
2. Create the canonical weekly Markdown template.
3. Generate and approve the Week 1 outline.
4. Generate the Week 1 draft in ChatGPT Web.
5. Save the returned draft in `content/inbox/week-01-draft.md`.
6. Perform structural and technical verification.
7. Complete HITL review and targeted revisions.
8. Approve `content/weeks/week-01.md` as version `1.0.0`.
9. Select and approve the Markdown rendering architecture.
10. Integrate Week 1 into the website.
11. Retrospect and improve the prompt before starting Week 2.

## Definition of Done for a Week

A week is complete only when:

- every approved learning outcome is addressed;
- all material technical claims have traceable sources;
- executable examples have actually been validated where practical;
- exercises include clear objectives and evaluation criteria;
- interview answers include reasoning and trade-offs;
- no fabricated citation or validation claim remains;
- the HITL rubric is approved;
- the canonical Markdown status is `approved`;
- the website renders the content correctly; and
- remaining limitations and risks are recorded.
