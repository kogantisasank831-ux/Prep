# Week 16: durable case memory and bounded context

This lab adds cross-thread case memory to the fictional procurement investigation.
It stores selected structured facts in a private SQLite file, records compact
episodes and assembles a bounded context block for a new turn. It never stores
raw conversation or evidence bodies.

## What is remembered

| Memory | Stored value | Deliberately absent |
| --- | --- | --- |
| Semantic | objective, supplier, evidence references, exact calculation, approval status, provenance, revision and expiry | prompts, chat transcript and evidence text |
| Episodic | compact ordered events for the initial facts and approval transition | copied messages and tool payloads |
| Working context | semantic summary plus question-relevant episodes within a hard budget | the transient question and unbounded history |

The SQLite file demonstrates persistence across Python processes. It is separate
from a LangGraph checkpointer: a checkpoint resumes node execution, while this
store recalls selected case knowledge in a future thread.

## Run the lifecycle

From the repository root in an activated environment:

```shell
python -m pip install -r requirements-dev.txt
python -m labs.week_16.demo seed --db .runtime/week16.sqlite3
python -m labs.week_16.demo recall --db .runtime/week16.sqlite3
python -m labs.week_16.demo approve --db .runtime/week16.sqlite3
python -m labs.week_16.demo forget --db .runtime/week16.sqlite3
```

`seed` intentionally refuses to replace an existing file. Use a new path for a
fresh run. The fixture clock is fixed at 2026-11-03 and the example expires on
2026-12-03 so output remains reproducible.

Run the automated checks:

```shell
python -m labs.week_16.demo smoke
python -m pytest tests/test_week16_memory.py -q
python -m ruff check labs/week_16 tests/test_week16_memory.py
python -m ruff format --check labs/week_16 tests/test_week16_memory.py
python -m mypy --strict --explicit-package-bases labs/week_16 tests/test_week16_memory.py
```

## Read the implementation in this order

1. `LOGIC.md` defines the accepted memory and privacy rules.
2. `models.py` closes every input/output schema and defines the trusted scope.
3. `fixtures.py` provides dated fictional facts and content digests.
4. `context.py` builds the deterministic summary and bounded selection.
5. `memory.py` owns SQLite transactions, revisions, expiry and forgetting.
6. `demo.py` exposes the lifecycle as machine-readable commands.
7. `tests/test_week16_memory.py` proves the behavior across processes.

## Incorrect-memory controls

- every snapshot contains document and SQL source references plus digests;
- source and expiry timestamps must be UTC and valid for the current clock;
- exact replays are idempotent;
- updates require the current revision;
- investigation facts cannot be rewritten through the approval endpoint;
- approval can move from waiting to one terminal value only; and
- recalled memory is labelled as data to verify, not an instruction or authority.

The report and content digests detect changed bytes; they are not signatures.
`AccessScope` demonstrates tenant/case isolation only after a trusted host has
authenticated and authorized the caller. A case ID is not a credential.

## Privacy and operations boundaries

The database is created with local mode `0600`, but it is not encrypted. A real
deployment needs platform-specific encryption, key management, backups,
migrations, authenticated principals, policy enforcement, concurrency design,
retention jobs, legal-hold decisions and deletion evidence.

The lab makes no model, network, provider or external-action call. GitHub Pages
publishes the lesson; this SQLite program runs locally.

Read the official [LangChain long-term memory](https://docs.langchain.com/oss/python/concepts/memory#long-term-memory),
[context engineering](https://docs.langchain.com/oss/python/langchain/context-engineering),
[LangGraph store](https://docs.langchain.com/oss/python/langgraph/persistence#memory-store)
and [Python SQLite](https://docs.python.org/3/library/sqlite3.html) documentation
alongside the code.
