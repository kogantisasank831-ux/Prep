---
layout: week
week: 27
phase: 7
status: approved
version: 1.0.0
last_reviewed: 2026-11-12
estimated_hours: 8
permalink: /weeks/week-27/beginner/
title: "Adapt a model with small LoRA matrices"
description: Compare full fine-tuning, LoRA and QLoRA, then watch a frozen base learn through an adapter.
summary: LoRA keeps the base fixed and learns a smaller update that can be stored separately.
kicker_primary: Beginner path
kicker_secondary: Adaptation without changing every base weight
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-27/
---

## Decide whether training is needed

Use prompting for clearer instructions and RAG for changing facts first. Fine-
tuning is useful when a model repeatedly misses a task pattern, terminology or
format that good examples can teach. The [production route]({{ '/weeks/week-27/' | relative_url }})
adds equations, target modules and stability controls. The [assessment]({{ '/assessments/week-27/' | relative_url }})
tests the differences.

## Compare the choices

- **Full fine-tuning:** update all weights. Flexible but expensive.
- **LoRA:** freeze the model and learn small low-rank matrices.
- **QLoRA:** keep the frozen base quantised and train adapters in higher
  precision to reduce memory.

Rank is the adapter's capacity. Alpha scales its effect. Target modules are the
model layers that receive adapters. These are experiment choices, not magic
defaults.

## Protect what the model already knows

An adapted model can improve on domain examples and get worse elsewhere. This
is catastrophic forgetting or capability regression. Keep separate test sets
for domain tasks, general behavior and safety. Compare the same cases before and
after tuning.

## Run the numerical example

~~~shell
python -m labs.week_27.demo smoke
python -m labs.week_27.demo smoke --qlora
python -m pytest tests/test_week27_lora.py -q
~~~

Check that the original base matrix stays unchanged while final loss falls.
Change rank or alpha and observe the parameter count and scale. The `--qlora`
case simulates 4-bit base storage; it is not a real GPU fine-tune.

## Completion checklist

- Explain why prompting or RAG may be enough.
- Distinguish LoRA from QLoRA.
- Describe rank, alpha and target modules.
- Confirm only adapter values change.
- Evaluate held-out domain, general and safety cases.
- Report model, data, adapter configuration and hardware.

