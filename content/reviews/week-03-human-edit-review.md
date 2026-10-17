# Week 3 readability and content-preservation review

## Scope

Rewrite the explanations in the production and beginner Week 3 lessons using
plain language, shorter paragraphs and a continuous supplier-note example.
Retain the original teaching content, technical constraints and practice work.
The change applies to `kogantisasank831-ux/Prep` on `main`.

Reviewed against commit `a360bd5d44904e7fb2f2b289bddd2ae181a122fa`:

- [Production lesson](../weeks/week-03.md), original blob
  `184a5d54329e079eeac375f1a742d0dfcdcc11d4`.
- [Beginner lesson](../weeks/week-03-beginner.md), original blob
  `896078e13c7371ddd387f1a3676947fbe9023a6b`.

## Content retained

| Area | Retained content |
| --- | --- |
| Text and representations | Tokenization, vocabulary IDs, token/document embeddings, contextual states, shapes and similarity limitations |
| Generation | Logits, softmax, autoregressive prediction, stopping and shared input/output budgets |
| Architecture | Recurrent paths, Q/K/V, scaled attention, causal masking, MHA/GQA, model head counts, positional methods/NoPE/RoPE, residuals, normalization, FFNs and decoder stacking |
| Training and behavior | Pretraining, instruction tuning, preference alignment, context usefulness, decoding settings and causes of unsupported output |
| Operating choices | Hosted/local trade-offs, licenses, local-only inference, artifact provenance, operator-owned server lifecycle and hardware-fit limitations |
| Experiment contract | Request hashes, frozen plans/schedules, manifests, artifact shards, configuration pins, strict loopback transport and bounded parsing |
| Measurements and recovery | Health/model checks, metric boundaries and provenance, unavailable values, typed failures, lifecycle evidence, sequential loading, partial recovery and durable JSONL records |
| Evaluation | Disjoint calibration/held-out suites, blinded output IDs, separate identity maps, six rubric criteria, scoring anchors, uncertainty and confounders |
| Practice | Common mistakes, all 13 interview questions, 14 recall questions and their answers, six exercises, four-case mini-project scope and definition of done |
| Supporting material | Original diagrams, code examples, tables, primary-source links and beginner readiness checklist |

## Checks executed

- Compared the original and rewritten section sequences: all 32 production
  sections, including the 29 numbered sections, and all 14 beginner sections
  remain in order.
- Compared subsection topics after removing the repetitive “Orienting question”
  prefix: every topic remains.
- Compared all 37 fenced code/diagram blocks and four tables: exact matches.
- Compared all original external URL references and inline technical identifiers:
  retained in both lessons.
- Compared all interview question prompts: exact matches.
- Compared the recall question/answer block, all six exercises and their
  acceptance criteria, mini-project scope/definition of done, and beginner
  readiness checklist: exact matches.
- Checked YAML front matter, preserved metadata/permalinks and reciprocal
  beginner/production links.
- Rendered the lessons using Python Markdown and the repository's shared Liquid
  layout. Checked section and code-block counts, unique fragment IDs, absence of
  unresolved template markers, local navigation and asset targets.
- Ran `git diff --check`: passed.
- Reviewed the prose against the original for technical qualifications, numeric
  constraints, failure behavior, metric interpretation and evaluation rules.

## Validation limits

The local renderer used Python Markdown rather than the hosted Jekyll/kramdown
engine; Ruby/Jekyll is unavailable in this environment. The hosted build remains
the final rendering engine.

A desktop/mobile Playwright preview was attempted but could not run: no browser
binary was installed, and the attempted Chromium download returned an invalid
archive. No visual-browser pass is claimed.

The Python comparison implementation, SQL labs, page layout, JavaScript, CSS and
deployment configuration were not changed. Live-model/GPU evaluation was not run.
The lesson's earlier 80-test/Ruff/mypy evidence remains explicitly historical;
it is not presented as fresh validation of a model run or of this prose edit.
