# Week 26 data-pipeline lab

The lab applies explicit licence/language/quality gates, exact deduplication,
benchmark-contamination checks, source caps, PII redaction, stable document
splitting, training-only vocabulary fitting and bounded token sequences.

```shell
python -m labs.week_26.demo smoke
python -m pytest tests/test_week26_data_pipeline.py -q
```

The examples are synthetic or labelled CC BY for teaching. The code does not
infer legal permission, perform fuzzy/semantic deduplication, recognise every
PII form, or make an unknown source safe to use.

