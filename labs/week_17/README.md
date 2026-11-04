# Week 17: bounded supervisor and specialists

This local lab implements four explicit procurement specialists and a central
supervisor. Document, SQL and supplier-risk analysis form one independent wave;
commercial recommendation waits for all three validated findings. Every report
stops for human approval.

## Architecture

| Component | Receives | Returns | Does not own |
| --- | --- | --- | --- |
| Document specialist | case/order IDs and one document reference | terms found and threshold | price or risk decisions |
| SQL specialist | case/order/supplier IDs and one SQL reference | exact dated price variance | contract or risk policy |
| Supplier-risk specialist | case/supplier IDs and one risk reference | status, incidents and risk level | price or contract policy |
| Commercial specialist | three validated findings | recommendation, summary and evidence | source retrieval or external action |
| Supervisor | case and allowlisted registry | correlated run result and stable trace | domain interpretation inside a specialist |

All boundary models are strict, frozen and closed. The supervisor is the only
component that aggregates results. It validates specialist, run and case identity
before commercial synthesis.

## Run it

From the repository root in the declared development environment:

```shell
python -m pip install -r requirements-dev.txt
python -m labs.week_17.demo run --case price-spike --run-id demo-17
python -m labs.week_17.demo workflow --case price-spike --run-id demo-17
python -m labs.week_17.demo compare --case price-spike --run-id demo-17
python -m labs.week_17.demo smoke
```

Available cases exercise a price spike, a stable price, missing contract terms
and elevated supplier risk. Output is machine-readable JSON.

Run the behavior gates:

```shell
python -m pytest tests/test_week17_multi_agent.py -q
python -m ruff check labs/week_17 tests/test_week17_multi_agent.py
python -m ruff format --check labs/week_17 tests/test_week17_multi_agent.py
python -m mypy --strict --explicit-package-bases labs/week_17 tests/test_week17_multi_agent.py
```

## Read the implementation in this order

1. `LOGIC.md` defines the accepted business and coordination rules.
2. `models.py` closes assignments, findings, run results and comparisons.
3. `fixtures.py` provides synthetic sources with canonical digests.
4. `specialists.py` implements the four narrow domain boundaries.
5. `supervisor.py` owns bounded fan-out, validation and the sequential baseline.
6. `demo.py` exposes runnable JSON commands and smoke checks.
7. `tests/test_week17_multi_agent.py` proves the observable contracts.

## What the comparison means

The supervisor and sequential workflow use the same components and should return
the same report. The supervisor exposes four inter-agent handoffs and two
dependency stages: one parallel evidence wave, then recommendation. The workflow
has no inter-agent handoff and four sequential component stages.

Those are structural facts, not a latency benchmark. Local functions are too
small to support a production speed claim. Use multi-agent boundaries when the
isolation, ownership or independent work justifies their coordination cost; use a
single workflow when it is clearer.

## Failure and safety boundary

A technical coordination fault fails closed and produces no report. Missing
business evidence is different: the commercial result is `needs_human`, still
with an approval requirement. The lab has no retry loop, remote cancellation or
external side effect. Thread workers are suitable for this small local I/O-shaped
demonstration, not a substitute for production job infrastructure.

The fixture digest detects changed bytes but is not a signature. The case and
source IDs are not credentials. A real deployment still needs authenticated
principals, authorization, source governance, timeouts, idempotent retries,
durable state, tracing, evaluation and approval enforcement.

Read the official [LangChain multi-agent overview](https://docs.langchain.com/oss/python/langchain/multi-agent),
[subagents guide](https://docs.langchain.com/oss/python/langchain/multi-agent/subagents),
[handoffs guide](https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs)
and [Python `concurrent.futures` documentation](https://docs.python.org/3.13/library/concurrent.futures.html)
alongside the code.
