---
layout: week
week: 27
phase: 7
status: approved
version: 1.0.0
last_reviewed: 2026-11-12
estimated_hours: 8
permalink: /weeks/week-27/
title: "Choose and evaluate full fine-tuning, LoRA and QLoRA"
description: Understand adapter mathematics, rank, alpha, target modules, quantised bases, stability and catastrophic forgetting.
summary: Parameter-efficient tuning reduces trainable state, but data quality and evaluation still decide whether adaptation helps.
kicker_primary: Domain adaptation
kicker_secondary: Frozen bases, low-rank updates and retained capability
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-27/beginner/
---

## Choose adaptation only for a measured gap

Start with a versioned baseline and held-out tasks. Prompting may solve format or
instruction gaps; RAG may solve changing factual knowledge. Fine-tuning is a
candidate when repeatable behavior, terminology, style or task mapping remains
weak after simpler controls.

Use the [beginner route]({{ '/weeks/week-27/beginner/' | relative_url }}) for an
adapter-first explanation. The [assessment]({{ '/assessments/week-27/' | relative_url }})
checks the trade-offs and experiment design.

## Compare the three approaches

| Approach | Updated state | Main advantage | Main risk |
| --- | --- | --- | --- |
| full fine-tuning | all model weights | maximum adaptation freedom | high memory/compute and forgetting |
| LoRA | small adapter matrices | cheap, separable task artefacts | rank/target choices can underfit |
| QLoRA | adapters over a quantised frozen base | lower base-weight memory | quantisation/kernel complexity |

Parameter-efficient does not mean data-efficient, safe or automatically
better. Optimiser state, activations and temporary buffers still consume
memory.

## Understand the LoRA update

For a frozen weight matrix \(W\), LoRA learns

\[
h = Wx + \frac{\alpha}{r}BAx,
\]

where \(A\) and \(B\) have rank \(r\). Usually one factor starts random and the
other at zero, so the initial adapter leaves the base output unchanged. Only A
and B receive gradients.

Rank controls update capacity and parameter count. Alpha controls update scale;
the important quantity is often \(\alpha/r\). Higher values are not universally
better. Target modules decide which projections can adapt—attention projections
and sometimes MLP layers are common candidates, but architecture names and
workload evidence must drive the selection.

## Distinguish QLoRA from quantised inference

QLoRA stores a frozen base in low precision and trains higher-precision
adapters through dequantised compute. It is a training technique, not simply
saving an INT4 inference file. Quantisation format, compute dtype, hardware
kernel support, adapter dtype and merge/export behavior must be compatible.
Measure peak memory and throughput instead of estimating from weight bytes
alone.

## Control stability

Version model, tokenizer, adapter configuration, data and seed. Observe loss,
learning rate, gradient norm, tokens per second, peak memory and validation
metrics. Use bounded sequence length, gradient clipping, sensible warm-up and
checkpointing. Stop when held-out performance stops improving rather than
selecting the final epoch by habit.

Run several seeds when the dataset is small. One successful run can be random
variance. Inspect malformed outputs and category-level failures, not only mean
loss.

## Measure forgetting and safety regression

Domain improvement can reduce general instruction following or safety. Keep
three suites:

1. held-out domain tasks;
2. general capabilities the base already performed; and
3. safety, privacy and formatting constraints.

Compare base, prompted base and adapted model on the same examples. A release
gate should require domain gain without unacceptable regression. Keeping a base
copy does not make a harmful adapter safe to deploy.

## Run the manual adapter experiment

~~~shell
python -m labs.week_27.demo smoke
python -m labs.week_27.demo smoke --qlora
python -m pytest tests/test_week27_lora.py -q
~~~

The lab freezes a two-by-two matrix, computes `alpha / rank`, updates only LoRA
factors, clips gradients and optionally simulates signed 4-bit base weights. Its
tiny matrix does not demonstrate LLM parameter savings, target-module choice,
token loss or real GPU kernels.

## Plan the real small-model experiment

- Choose one open-weight model and confirm its licence.
- Freeze a base/prompted baseline and test set first.
- Train on licensed, deduplicated Week 26 data.
- Log adapter targets, rank, alpha, dtype, effective token batch and hardware.
- Compare full tuning only if compute permits a fair run.
- Evaluate domain, retained capability, safety, latency and artefact size.
- Record failures even when RAG or prompting wins.

## Completion checklist

- Explain full tuning, LoRA and QLoRA without conflating them.
- Derive adapter parameter count and `alpha / rank` scale.
- Justify target modules from model architecture and evidence.
- Measure full training memory, not weight bytes alone.
- Use domain, retention and safety suites.
- Compare against prompted and RAG baselines.
- Keep adapters, configuration and base identity reproducible.

