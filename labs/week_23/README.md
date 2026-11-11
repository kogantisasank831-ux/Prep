# Week 23: make a GenAI design answer defensible

This lab turns six open-ended interview prompts into a repeatable answer
structure. Every proposal covers twelve dimensions and shows four kinds of
evidence per dimension: decision, validation evidence, trade-off and failure
control.

## Run it

```shell
python -m labs.week_23.demo cases
python -m labs.week_23.demo review --case enterprise-rag
python -m labs.week_23.demo review --case procurement-agent --incomplete
python -m labs.week_23.demo smoke
```

The complete sample scores 48/48 because it fills every structural field. Its
sentences are scaffolding, not a good interview answer. Replace them with your
own calculations, boundaries and evidence.

## Read the implementation in this order

1. `LOGIC.md` defines what the gate can and cannot claim.
2. `cases.py` defines the six bounded prompts.
3. `models.py` closes the twelve-dimension contracts.
4. `reviewer.py` implements the visible 0–4 rubric.
5. `demo.py` compares complete and intentionally incomplete fixtures.
6. `tests/test_week23_system_design.py` proves deterministic behavior.

Use the report to find missing parts, then have a human interviewer challenge
whether the decisions are technically coherent and supported by real evidence.
