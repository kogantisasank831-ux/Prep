"""Scripted protocol scenarios over actual local SQLite and guarded retrieval."""

from __future__ import annotations

import argparse
import asyncio
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import time

from labs.week_11.fixtures import NORTH, QUESTION, SOUTH
from labs.week_11.policy import SecurityContext
from labs.week_13.contracts import (
    Actor,
    Approval,
    ReviewArgs,
    ToolError,
    intent_digest,
    wire,
)
from labs.week_13.runtime import (
    Dispatcher,
    Message,
    RunResult,
    ToolSpec,
    registry,
    run,
)
from labs.week_13.store import Store, initialize

REVIEW = ReviewArgs(purchase_order_id="PO-1001", reason="price_variance")


def proposal(call_id: str, name: str, arguments: dict[str, object]) -> str:
    return wire(dict(kind="tool_call", call_id=call_id, name=name, arguments=arguments))


def demo_actor(
    tenant: str = NORTH,
    *,
    writable: bool = False,
    approved: bool = False,
    operation_key: str = "demo-review-1",
) -> Actor:
    """Explicit synthetic host-side authority fixture, not human authentication."""
    actor = Actor(
        SecurityContext(tenant, "analyst", "week13-demo"),
        writable=writable,
        operation_key=operation_key,
    )
    if approved:
        actor = replace(
            actor,
            approval=Approval(
                intent_digest(actor, REVIEW),
                time.monotonic() + 30,
            ),
        )
    return actor


class ScriptedPlanner:
    """Fixed proposed turns; the final formatter reads actual tool envelopes."""

    def __init__(self, turns: list[str]) -> None:
        self.turns = tuple(turns)
        self.position = 0

    async def next_turn(
        self,
        messages: tuple[Message, ...],
        tools: tuple[dict[str, object], ...],
    ) -> str:
        if self.position < len(self.turns):
            turn = self.turns[self.position]
            self.position += 1
            return turn
        completed = []
        errors = 0
        for message in messages:
            if message.role == "tool":
                value = json.loads(message.content)
                if value["status"] == "ok":
                    completed.append(value["call_id"])
                else:
                    errors += 1
        return wire(
            dict(
                kind="final",
                text=f"Scripted demonstration: {len(completed)} successful calls; {errors} rejected calls. Inspect the synthetic results, units and source dates.",
                evidence_call_ids=completed,
            )
        )


def read_plan() -> list[str]:
    return [
        proposal(
            "call_1",
            "sql_query",
            dict(
                query_name="purchase_order_by_id", purchase_order_id="PO-1001", limit=1
            ),
        ),
        proposal("call_2", "supplier_lookup", dict(supplier_id="SUP-001")),
        proposal("call_3", "commodity_price", dict(commodity_id="STEEL")),
        proposal(
            "call_4",
            "price_variance",
            dict(
                baseline="2.00",
                current="2.20",
                baseline_currency="USD",
                current_currency="USD",
                baseline_unit="kg",
                current_unit="kg",
            ),
        ),
        proposal("call_5", "document_search", dict(question=QUESTION)),
    ]


async def scenario(
    path: Path,
    name: str,
    *,
    tenant: str = NORTH,
    operation_key: str = "demo-review-1",
) -> RunResult:
    store = Store(path)
    tools = registry(store)
    actor = demo_actor(
        tenant,
        writable=name in {"unapproved", "approved", "lost-response"},
        approved=name in {"approved", "lost-response"},
        operation_key=operation_key,
    )
    if name == "read":
        turns = read_plan()
        # The fixture prices are explicitly scripted, not inferred by a model.
        if tenant == SOUTH:
            turns[3] = proposal(
                "call_4",
                "price_variance",
                dict(
                    baseline="3.00",
                    current="3.30",
                    baseline_currency="INR",
                    current_currency="INR",
                    baseline_unit="kg",
                    current_unit="kg",
                ),
            )
    elif name == "invalid":
        turns = [
            proposal(
                "bad_1",
                "sql_query",
                dict(
                    query_name="open_purchase_orders", purchase_order_id=None, limit="5"
                ),
            ),
            proposal(
                "fixed_2",
                "sql_query",
                dict(
                    query_name="open_purchase_orders", purchase_order_id=None, limit=1
                ),
            ),
        ]
    elif name in {"unapproved", "approved", "lost-response"}:
        turns = [proposal("write_1", "create_review", REVIEW.model_dump(mode="json"))]
        if name == "lost-response":
            original = tools["create_review"]

            async def lost(actor: Actor, args: object) -> object:
                if not isinstance(args, ReviewArgs):
                    raise ToolError("invalid_arguments")
                value = store.create_review(actor, args)
                if value["replayed"] is False:
                    # Real local commit, followed by a controlled lost-response fault.
                    raise ToolError("unavailable")
                return value

            tools["create_review"] = replace(original, handler=lost)
    elif name == "transient":
        turns = [proposal("read_1", "commodity_price", dict(commodity_id="STEEL"))]
        original = tools["commodity_price"]
        count = 0

        async def transient(actor: Actor, args: object) -> object:
            nonlocal count
            count += 1
            if count == 1:
                raise ToolError("unavailable")
            from labs.week_13.contracts import CommodityArgs

            if not isinstance(args, CommodityArgs):
                raise ToolError("invalid_arguments")
            return store.commodity(actor, args)

        tools["commodity_price"] = replace(original, handler=transient)
    else:
        raise ValueError("scenario_invalid")
    return await run(
        actor,
        "Inspect the synthetic purchase-order example.",
        ScriptedPlanner(turns),
        Dispatcher(tools),
    )


async def smoke(path: Path) -> None:
    """Twelve independent observations over actual adapters and a persistent file."""
    initialize(path)
    normal = await scenario(path, "read")
    assert normal.status == "complete" and len(normal.outcomes) == 5
    assert all(outcome.status == "ok" for outcome in normal.outcomes)
    data = {outcome.name: outcome.data for outcome in normal.outcomes}
    sql = data["sql_query"]
    assert sql is not None and sql["rows"] == [
        dict(
            purchase_order_id="PO-1001",
            supplier_id="SUP-001",
            commodity_id="STEEL",
            baseline="2.00",
            current="2.20",
            currency="USD",
            unit="kg",
        )
    ]
    assert data["price_variance"] == dict(
        delta="0.20",
        percent="10.00",
        currency="USD",
        unit="kg",
        rounding="ROUND_HALF_EVEN",
    )
    assert data["supplier_lookup"] == dict(
        supplier_id="SUP-001", name="North Demo Metals", status="active"
    )
    assert data["commodity_price"] == dict(
        commodity_id="STEEL",
        amount="2.10",
        currency="USD",
        unit="kg",
        as_of="2026-10-01",
        source="synthetic-fixture",
    )
    search = data["document_search"]
    assert search is not None and "Net 30" in str(search["answer"])
    south = await scenario(path, "read", tenant=SOUTH)
    assert south.outcomes[1].data == dict(
        supplier_id="SUP-001", name="South Demo Metals", status="suspended"
    )
    invalid = await scenario(path, "invalid")
    assert (
        invalid.outcomes[0].error == "invalid_arguments"
        and invalid.outcomes[0].attempts == 0
    )
    assert invalid.outcomes[1].status == "ok"
    denied = await scenario(path, "unapproved")
    assert (
        denied.outcomes[0].error == "approval_required"
        and denied.outcomes[0].attempts == 0
    )
    first = await scenario(path, "approved")
    again = await scenario(path, "approved")
    assert first.outcomes[0].data is not None and again.outcomes[0].data is not None
    assert first.outcomes[0].data["review_id"] == again.outcomes[0].data["review_id"]
    assert (
        first.outcomes[0].data["replayed"] is False
        and again.outcomes[0].data["replayed"] is True
    )
    lost = await scenario(path, "lost-response", operation_key="lost-demo")
    recovered = await scenario(path, "lost-response", operation_key="lost-demo")
    assert lost.status == "unknown_outcome" and lost.outcomes[0].attempts == 1
    assert (
        recovered.outcomes[0].data is not None
        and recovered.outcomes[0].data["replayed"] is True
    )
    transient = await scenario(path, "transient")
    assert transient.outcomes[0].status == "ok" and transient.outcomes[0].attempts == 2
    print(
        wire(
            dict(
                status="passed",
                checks=12,
                storage="actual-sqlite",
                planner="scripted",
                external_actions=0,
            )
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("init", "run"):
        child = commands.add_parser(command)
        child.add_argument(
            "--database", type=Path, default=Path(".runtime/week13.sqlite3")
        )
        if command == "run":
            child.add_argument(
                "--scenario",
                choices=[
                    "read",
                    "invalid",
                    "unapproved",
                    "approved",
                    "lost-response",
                    "transient",
                ],
                default="read",
            )
            child.add_argument("--tenant", choices=["north", "south"], default="north")
            child.add_argument("--operation-key", default="demo-review-1")
    commands.add_parser("schemas")
    commands.add_parser("smoke")
    args = parser.parse_args()
    try:
        if args.command == "init":
            initialize(args.database)
            print(wire(dict(status="created", schema="week13/1")))
        elif args.command == "schemas":
            tools: dict[str, ToolSpec] = registry(
                Store(Path(".runtime/week13.sqlite3"))
            )
            print(wire([tool.definition() for tool in tools.values()], 32768))
        elif args.command == "smoke":
            Path(".runtime").mkdir(exist_ok=True)
            with tempfile.TemporaryDirectory(
                prefix="week13-smoke-", dir=".runtime"
            ) as folder:
                asyncio.run(smoke(Path(folder) / "fixture.sqlite3"))
        else:
            result = asyncio.run(
                scenario(
                    args.database,
                    args.scenario,
                    tenant=NORTH if args.tenant == "north" else SOUTH,
                    operation_key=args.operation_key,
                )
            )
            print(
                wire(
                    dict(
                        status=result.status,
                        text=result.text,
                        results=[outcome.envelope() for outcome in result.outcomes],
                    ),
                    32768,
                )
            )
            return 0 if result.status == "complete" else 2
    except (OSError, ToolError, ValueError, AssertionError) as error:
        print(wire(dict(status="failed", category=type(error).__name__)))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
