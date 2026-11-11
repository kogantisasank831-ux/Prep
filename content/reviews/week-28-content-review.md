# Week 28 content and lab review

## Scope and disposition

Roadmap source: `Path.md`, Week 28 — Instruction tuning. The candidate remains
unpublished pending human approval.

## Coverage and findings

The lessons cover behavior-first dataset design, provenance, chat-template
parity, response-only loss, padding, diversity, grouped splits, duplicates,
schemas, truncation, packing, memorisation and held-out evaluation. The lab
prepares aligned tokens and masks and contrasts exact train lookup with unseen
validation instructions; it does not claim to train a transformer.

Tests cover duplicate removal, group isolation, template/mask alignment,
training-only vocabulary, padded batches, memorisation gap, diversity, long
examples, strict inputs and CLI behavior.

