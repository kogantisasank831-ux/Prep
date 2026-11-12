# Week 24: tell one truthful project story at three depths

This lab keeps project evidence separate from narrative delivery. One strict
record feeds a concise 2-minute story, a 10-minute walkthrough and a deep-dive
pack. Metrics retain provenance and attribution, and decisions retain rejected
alternatives and consequences.

## Run it

```shell
python -m labs.week_24.demo story --depth two-minute
python -m labs.week_24.demo story --depth ten-minute
python -m labs.week_24.demo story --depth deep-dive
python -m labs.week_24.demo review
python -m labs.week_24.demo smoke
```

The included project is fictional. Replace the complete `ProjectEvidence`
record before practicing your own answer; do not copy its numbers into a résumé
or interview.

## Read the implementation in this order

1. `LOGIC.md` defines truth, attribution and readiness boundaries.
2. `models.py` closes metric, decision, leadership and story contracts.
3. `storytelling.py` builds three depths and scores declared evidence.
4. `demo.py` supplies a clearly synthetic example.
5. `tests/test_week24_storytelling.py` proves grounding and determinism.

After the automated check, rehearse with a human who can challenge ownership,
technical depth, missing baselines, causal overclaiming and communication.
