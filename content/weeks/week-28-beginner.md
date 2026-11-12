---
layout: week
week: 28
phase: 7
status: approved
version: 1.0.0
last_reviewed: 2026-11-12
estimated_hours: 8
permalink: /weeks/week-28/beginner/
title: "Create clear instruction-and-answer training examples"
description: Learn example structure, chat roles, response-only loss, diversity, source splits and overfitting.
summary: Instruction tuning needs correct examples and masks, not only a file of conversations.
kicker_primary: Beginner path
kicker_secondary: Teach the response while keeping prompts as context
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-28/
---

## Start with the behavior you want

An instruction example has a request and a preferred response. Add category and
source so you can measure coverage and keep related examples together. The
[production route]({{ '/weeks/week-28/' | relative_url }}) adds schema,
provenance, packing and release evidence. The [assessment]({{ '/assessments/week-28/' | relative_url }})
draws ten questions from the full bank.

## Understand the chat template

Models use special tokens to distinguish system, user and assistant text. The
template must match the base model. During response-only training:

- system and user tokens are context, so their loss mask is 0;
- assistant answer tokens are targets, so their mask is 1; and
- padding has attention and loss 0.

Print one encoded example and inspect tokens, IDs and mask. Do not assume the
library created the intended labels.

## Build useful variety

Cover different tasks, lengths, difficulties and outcomes. Include unclear
requests, missing information, conflicts, safe refusals and exact output
formats. Check human- and model-generated answers; fluent text can still be
wrong.

Remove duplicates and keep all examples from one source or scenario in one
partition. Otherwise small rewrites can leak into validation.

## Watch for overfitting

Training loss can fall because the model memorised examples. Test new wording
and new source groups. Compare the original model, a well-prompted original and
the tuned version. Use task metrics, not only loss.

## Run the preparation example

~~~shell
python -m labs.week_28.demo smoke
python -m pytest tests/test_week28_instruction.py -q
~~~

Find the removed duplicate, source-level split, role tokens, loss masks and
padded batches. The lookup baseline remembers training questions exactly but
cannot answer unseen questions. The lab prepares data; it does not train an LLM.

## Completion checklist

- Store category and source with every example.
- Apply the base model's exact chat template.
- Mask prompt and padding tokens from response loss.
- Check diversity and correct answers.
- Split related examples together.
- Compare new held-out tasks with base and prompted baselines.
- Avoid claiming that low training loss proves generalisation.

