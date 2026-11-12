# Week 27 content and lab review

## Scope and disposition

Roadmap source: `Path.md`, Week 27 — Fine-tuning and LoRA. The candidate remains
unpublished pending human approval.

## Coverage and findings

The lessons compare full tuning, LoRA and QLoRA; explain rank, alpha/rank,
initialisation and target modules; and require stability, domain, general and
safety evidence. The manual numerical lab freezes the base, updates only adapter
factors, clips gradients and optionally simulates signed 4-bit base storage.

Tests cover loss improvement, immutable base state, rank/scale/counts,
reproducibility, predictions, quantisation, clipping, strict inputs and both CLI
modes. The tiny matrix is explicitly not evidence for LLM memory, kernels,
quality or catastrophic-forgetting behavior.

