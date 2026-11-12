# Week 25 content and lab review

## Scope and disposition

Roadmap source: `Path.md`, Week 25 — Training foundations. The reviewed scope
adds two lesson depths and an inspectable causal-training surrogate. Publication
was approved on 2026-11-12.

## Coverage and findings

The lessons cover causal next-token loss, document-level splits, training-only
vocabulary fitting, tokenisation, optimiser state, update-based schedules,
gradient accumulation, mixed precision and resumable checkpoints. The lab
implements deterministic bigram cross-entropy and SGD so every update is
inspectable; it repeatedly states that it is not a transformer or useful LLM.

Tests cover stable/disjoint splits, leakage boundaries, reproducibility,
schedule shape, accumulation, checkpoints, strict inputs and CLI behavior. A
real tiny-transformer stretch run still needs an isolated pinned framework,
licensed data, hardware evidence and restore testing.

