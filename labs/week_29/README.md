# Week 29 model-evaluation lab

The lab compares synthetic base, prompted-base, fine-tuned and RAG outputs on
the exact same frozen cases. It reports normalised exact match, binary
classification precision/recall/F1, synthetic-token perplexity, segment
metrics, paired bootstrap deltas, contamination exclusions and blind pairwise
vote counts.

```shell
python -m labs.week_29.demo smoke
python -m pytest tests/test_week29_evaluation.py -q
```

The fixtures are constructed teaching data. Metric arithmetic can be tested;
production quality, factuality, judge validity and human agreement cannot be
inferred from these numbers.

