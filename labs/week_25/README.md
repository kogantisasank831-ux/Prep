# Week 25 training-loop lab

This dependency-free lab makes the causal next-token objective, document split,
training-only vocabulary, SGD schedule, gradient accumulation and checkpoint
metadata inspectable. It trains a bigram surrogate, **not a transformer or a
useful language model**. Use an isolated framework environment and a tiny public
dataset for the optional transformer experiment described in the lesson.

```shell
python -m labs.week_25.demo smoke
python -m pytest tests/test_week25_training.py -q
```

