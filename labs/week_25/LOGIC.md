# Week 25 logic

1. Hash stable document IDs into train and validation before tokenisation.
2. Fit the vocabulary on train documents only; validation-only tokens become
   `<unk>`.
3. Create `<bos> → token → … → <eos>` next-token pairs.
4. Minimise mean cross-entropy using deterministic shuffled SGD, accumulated
   gradients and warm-up/linear-decay learning rates.
5. Record loss and a digest at bounded checkpoint intervals.

The digest is reproducibility evidence, not a model artefact. Mixed precision,
distributed training, attention, framework checkpoint restoration and hardware
throughput are intentionally outside this CPU teaching surrogate.

