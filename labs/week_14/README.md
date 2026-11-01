# Week 14: workflows versus agents

This lab investigates the same fictional purchase order with two controllers:
an explicit state-machine workflow and a bounded planner–executor agent. Both
controllers share the same tools, typed state, decision rule, deterministic
report and human-approval boundary.

Read [LOGIC.md](LOGIC.md), then inspect `models.py`, `tools.py`,
`controllers.py` and `demo.py`. No API key, provider, model download, network,
database or new dependency is required.

From the repository root in the declared Python environment:

~~~shell
python -m pip install -r requirements-dev.txt
python -m labs.week_14.demo workflow --case price-spike
python -m labs.week_14.demo agent --case price-spike --script happy
python -m labs.week_14.demo compare
python -m labs.week_14.demo smoke
~~~

The two successful commands return the same recommendation and stop at
`awaiting_approval`. The workflow makes no model calls. The agent's scripted
planner makes one assumed model call per proposal. The fixed per-token prices
and latency values are explicit teaching assumptions, not current provider
prices or wall-clock measurements.

Try the bounded failure paths:

~~~shell
python -m labs.week_14.demo agent --case price-spike --script loop
python -m labs.week_14.demo agent --case price-spike --script unsafe
~~~

These commands intentionally exit with status 2 after the eight-proposal budget.
Repeated reads are rejected without a second tool execution. `send_supplier_email`
is not in the action enum, so it never reaches a tool. The selected scripts create
the reported failure rate; the result is a control-flow demonstration, not a
real-model benchmark.

The optional `--approve` flag supplies an explicit synthetic host-side reviewer
decision after the report exists:

~~~shell
python -m labs.week_14.demo workflow --case price-spike --approve
~~~

Approval is bound to the exact report digest and accepts only this local report.
It is not login, a signature or authority for an external action. The lab has no
email, payment, purchase-order approval or supplier-write capability.

Run the focused gates:

~~~shell
python -m pytest tests/test_week14_workflows.py -q
python -m ruff check labs/week_14 tests/test_week14_workflows.py
python -m ruff format --check labs/week_14 tests/test_week14_workflows.py
python -m mypy --strict --explicit-package-bases labs/week_14 tests/test_week14_workflows.py
~~~

The fixtures are fictional and the reference prices are dated 2026-10-01. This
lab tests orchestration contracts, dependency ordering, termination and approval
binding. It does not measure a provider, model quality, live price accuracy,
real latency, production reliability or business outcome quality.
