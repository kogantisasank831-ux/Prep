"""Command-line demonstrations for Week 14 workflow and agent control flow."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from typing import Sequence

from labs.week_14.controllers import (
    PLANNER_SCRIPTS,
    ScriptedPlanner,
    comparison,
    run_agent,
    run_workflow,
)
from labs.week_14.models import (
    ApprovalDecision,
    HumanApproval,
    RunResult,
    RunStatus,
    finalize,
)
from labs.week_14.tools import CASES


def _wire(result: RunResult) -> dict[str, object]:
    value = asdict(result)
    value["route"] = result.route
    value["status"] = result.status
    if result.report is not None:
        value["report"] = {
            **asdict(result.report),
            "recommendation": result.report.recommendation,
            "digest": result.report.digest(),
        }
    return value


def _maybe_approve(result: RunResult, approve: bool) -> RunResult:
    if not approve:
        return result
    if result.status is not RunStatus.AWAITING_APPROVAL or result.report is None:
        return result
    return finalize(
        result,
        HumanApproval(
            result.report.digest(),
            "synthetic-demo-reviewer",
            ApprovalDecision.APPROVE,
        ),
    )


def smoke() -> None:
    workflow = run_workflow(CASES["price-spike"])
    assert workflow.status is RunStatus.AWAITING_APPROVAL
    assert workflow.report is not None
    assert workflow.report.recommendation == "review_required"
    happy = run_agent(CASES["price-spike"], ScriptedPlanner(PLANNER_SCRIPTS["happy"]))
    assert happy.status is RunStatus.AWAITING_APPROVAL
    assert happy.report == workflow.report
    loop = run_agent(CASES["price-spike"], ScriptedPlanner(PLANNER_SCRIPTS["loop"]))
    assert loop.status is RunStatus.FAILED
    missing = run_workflow(CASES["missing-terms"])
    assert missing.report is not None
    assert missing.report.recommendation == "needs_human"
    approved = _maybe_approve(workflow, True)
    assert approved.status is RunStatus.APPROVED
    rows = comparison(CASES["price-spike"])
    assert rows["workflow"]["failure_rate"] == "0.0%"
    assert rows["agent"]["failure_rate"] == "50.0%"


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    subcommands = root.add_subparsers(dest="command", required=True)
    for name in ("workflow", "agent"):
        command = subcommands.add_parser(name)
        command.add_argument("--case", choices=tuple(CASES), default="price-spike")
        command.add_argument("--approve", action="store_true")
        if name == "agent":
            command.add_argument(
                "--script", choices=tuple(PLANNER_SCRIPTS), default="happy"
            )
    subcommands.add_parser("compare")
    subcommands.add_parser("smoke")
    return root


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "smoke":
        smoke()
        print(json.dumps({"status": "ok", "checks": 8}, sort_keys=True))
        return 0
    if args.command == "compare":
        print(json.dumps(comparison(CASES["price-spike"]), indent=2, sort_keys=True))
        return 0
    if args.command == "workflow":
        result = run_workflow(CASES[args.case])
    else:
        result = run_agent(
            CASES[args.case], ScriptedPlanner(PLANNER_SCRIPTS[args.script])
        )
    result = _maybe_approve(result, args.approve)
    print(json.dumps(_wire(result), indent=2, sort_keys=True))
    return 2 if result.status is RunStatus.FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
