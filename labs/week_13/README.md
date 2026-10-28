# Week 13: local tool calling

Five read tools exercise SQL, price variance, supplier lookup, commodity lookup
and guarded document search. An optional sixth tool creates a synthetic local
review record. A scripted planner drives the protocol; no LLM/provider call,
API key, GPU, external action or new dependency is involved.

Read [LOGIC.md](LOGIC.md) for revision 1's contracts, then follow
contracts.py (closed schemas and authority), store.py (real SQLite),
runtime.py (registry, dispatcher and loop) and demo.py (scenarios).
This separate fixture does not change Week 12's PostgreSQL/API contracts.

From the repository root in the declared Python environment:

~~~shell
python -m pip install -r requirements-dev.txt
python -m labs.week_13.demo schemas
python -m labs.week_13.demo init
python -m labs.week_13.demo run --scenario read
python -m labs.week_13.demo run --scenario read --tenant south
python -m labs.week_13.demo run --scenario invalid
python -m labs.week_13.demo run --scenario transient
python -m labs.week_13.demo run --scenario unapproved
~~~

Init exclusively creates .runtime/week13.sqlite3 and refuses an existing file.
Initialize once, then reuse it. Supply --database with a fresh owned path to both
init and run for a separate fixture. It never resets an existing ledger or grant.
The file has an explicit schema version; mismatches fail without migration.

- Read: five actual tool outcomes, scoped by caller, with fictional dated prices.
- Invalid: string-valued SQL limit gets invalid_arguments with zero attempts;
  a new call corrects it.
- Transient: one injected read failure, then the real adapter; two attempts.
- Unapproved: missing exact approval prevents execution.

The read plan uses known fixture values. It does not infer the relationship
between SQL results and arithmetic arguments through a real model. Strict result
schemas and successful evidence-ID membership do not establish source truth,
summary entailment or model selection/argument quality.

Observe persistent duplicate protection:

~~~shell
python -m labs.week_13.demo run --scenario approved
python -m labs.week_13.demo run --scenario approved
python -m labs.week_13.demo run --scenario lost-response --operation-key lost-demo
python -m labs.week_13.demo run --scenario lost-response --operation-key lost-demo
~~~

The approved runs return the original review ID; the replay flag becomes true.
The CLI supplies a trusted synthetic in-process approval fixture for these local
records, not an authenticated human approval flow. The model cannot supply that
approval or the stable operation key through its argument schema.

For a fresh lost-demo key, the first lost-response run commits a real review,
then injects an unavailable response. It returns unknown_outcome and exit code 2.
Run the second command separately with the same key: current authority is checked
again and the saved result is replayed. Do not chain the first expected failure
with && or mistake it for proof of rollback. The scenario never contacts a network.

Scoped key, normalized argument digest, current grant/approval and insertion
share one BEGIN IMMEDIATE transaction. A mismatched reuse conflicts; concurrent
cooperating writers to this SQLite file receive one review ID. The ledger is
retained in that file without automatic expiry. Discarding the file loses history.
No external or distributed exactly-once guarantee is made.

~~~shell
python -m labs.week_13.demo smoke
python -m pytest tests/test_week13_tools.py -q
python -m ruff check labs/week_13 tests/test_week13_tools.py
python -m ruff format --check labs/week_13 tests/test_week13_tools.py
python -m mypy --strict --explicit-package-bases labs/week_13 tests/test_week13_tools.py
~~~

Smoke creates and removes only its own temporary fixture and checks twelve
observations over actual SQLite/search/loop behavior. Tests additionally exercise
closed schemas, invalid/extra fields, permission negatives, exact decimal rounding,
malformed results, correlation, budgets, cooperative timeout/cancellation, atomic
replay/conflict/concurrency, expiry/current grant on replay and lost-response recovery.

Timeouts are cooperative; the tiny synchronous SQLite adapters have a separate
0.25-second connection busy-wait bound. They are not preempted by asyncio timers.
No hard end-to-end latency, memory sandbox or hostile-plugin isolation is claimed.
Caller cancellation propagates; admitted writes may require reconciliation.
Never automatically retry a write with a fresh key after an uncertain result.

The ordinary SQL tool chooses one of two fixed parameterized queries over the
open synthetic fixture orders. There is no arbitrary SQL/URL/shell dispatcher.
Read-only connections and caller row filtering protect different boundaries.
The application/file owner remains trusted; this is not an independent database
authentication or per-tenant operating-system isolation mechanism.

Routine logging emits bounded categories and counts, without configuring global
handlers/retention. CLI output intentionally displays only synthetic lesson data.
GitHub Pages hosts the static lesson, while these commands run locally.
No provider-compatible request adapter or public backend is published.
