"""Command-line demonstrations for the Week 15 LangGraph lab."""

from __future__ import annotations

import argparse
import json
from typing import Sequence, cast

from langgraph.types import Interrupt

from labs.week_15.fixtures import CASES
from labs.week_15.graph import GraphRuntime
from labs.week_15.models import (
    ApprovalDecision,
    ApprovalResponse,
    ApprovalStatus,
    PublicRun,
    Recommendation,
)


def _interrupt_value(result: dict[str, object]) -> dict[str, object] | None:
    raw = result.get("__interrupt__")
    if not isinstance(raw, (list, tuple)) or not raw:
        return None
    first = raw[0]
    if not isinstance(first, Interrupt) or not isinstance(first.value, dict):
        return None
    return cast(dict[str, object], first.value)


def _public(result: dict[str, object]) -> PublicRun:
    """Project framework state into a stable JSON-safe teaching response."""
    recommendation = result.get("recommendation")
    status = result.get("approval_status", "validation_failed")
    trace = result.get("trace", [])
    evidence = result.get("evidence", [])
    return {
        "case_id": str(result.get("case_id", "")),
        "status": cast(ApprovalStatus, status),
        "recommendation": cast(Recommendation | None, recommendation),
        "report_digest": (
            str(result["report_digest"]) if "report_digest" in result else None
        ),
        "reviewer": str(result["reviewer"]) if "reviewer" in result else None,
        "trace": [str(item) for item in cast(list[object], trace)],
        "evidence": [str(item) for item in cast(list[object], evidence)],
        "interrupt": _interrupt_value(result),
    }


def _start(runtime: GraphRuntime, case_name: str, thread_id: str) -> dict[str, object]:
    case = CASES[case_name]
    return runtime.start(case["case_id"], case["query"], thread_id=thread_id)


def smoke() -> None:
    """Exercise routing, reducers, interruption, checkpoints and resume."""
    runtime = GraphRuntime()
    paused = _start(runtime, "price-spike", "smoke-price-spike")
    assert paused["approval_status"] == "awaiting_approval"
    assert paused["recommendation"] == "review_required"
    assert len(cast(list[object], paused["evidence"])) == 2
    interrupt_value = _interrupt_value(paused)
    assert interrupt_value is not None
    assert interrupt_value["report_digest"] == paused["report_digest"]
    assert runtime.checkpoint_count("smoke-price-spike") >= 8
    response = ApprovalResponse(
        decision="approve",
        reviewer="synthetic-demo-reviewer",
        report_digest=str(paused["report_digest"]),
    )
    approved = runtime.resume("smoke-price-spike", response)
    assert approved["approval_status"] == "approved"
    assert cast(list[str], approved["trace"])[-1].startswith("human_approval:approve")
    missing = _start(runtime, "missing-terms", "smoke-missing")
    assert missing["recommendation"] == "needs_human"
    unsupported = runtime.start(
        "price-spike", "Tell me a joke.", thread_id="smoke-unsupported"
    )
    assert unsupported["approval_status"] == "unsupported"


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    subcommands = root.add_subparsers(dest="command", required=True)
    run = subcommands.add_parser("run", help="run to the approval interrupt")
    run.add_argument("--case", choices=tuple(CASES), default="price-spike")
    run.add_argument("--thread", default="week15-demo")
    resume = subcommands.add_parser(
        "resume-demo", help="pause and resume in one in-memory process"
    )
    resume.add_argument("--case", choices=tuple(CASES), default="price-spike")
    resume.add_argument("--thread", default="week15-resume-demo")
    resume.add_argument("--decision", choices=("approve", "reject"), default="approve")
    subcommands.add_parser("smoke")
    return root


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "smoke":
        smoke()
        print(json.dumps({"checks": 10, "status": "ok"}, sort_keys=True))
        return 0
    runtime = GraphRuntime()
    paused = _start(runtime, str(args.case), str(args.thread))
    if args.command == "run":
        print(json.dumps(_public(paused), indent=2, sort_keys=True))
        return 0
    response = ApprovalResponse(
        decision=cast(ApprovalDecision, args.decision),
        reviewer="synthetic-demo-reviewer",
        report_digest=str(paused["report_digest"]),
    )
    final = runtime.resume(str(args.thread), response)
    print(json.dumps(_public(final), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
