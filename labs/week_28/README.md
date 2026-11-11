# Week 28 instruction-tuning lab

The lab deduplicates domain instructions, splits by source group, applies an
explicit chat template, fits a training-only vocabulary, masks prompt tokens
from loss and creates padded batches. A lookup baseline makes memorisation and
held-out generalisation visibly different.

```shell
python -m labs.week_28.demo smoke
python -m pytest tests/test_week28_instruction.py -q
```

It prepares SFT inputs but does not train a transformer. Real work also requires
dataset consent/licensing, toxicity and privacy review, tokenizer/model template
compatibility, held-out safety/general-capability evaluation and GPU monitoring.

