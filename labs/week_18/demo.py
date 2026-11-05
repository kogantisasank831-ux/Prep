"""Run and inspect the deterministic Week 18 procurement-agent evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from labs.week_18.agent import run_candidate
from labs.week_18.evaluation import (
    load_dataset,
    persist_run,
    run_evaluation,
    score_case,
)
from labs.week_18.models import EvaluationRun


DEFAULT_DATASET = Path(__file__).with_name("cases.json")


def _json(value: object) -> None:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    print(json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True))


def _summary(run: EvaluationRun, output: Path | None) -> dict[str, object]:
    result = run.model_dump(mode="json", by_alias=True)
    summary = {
        "candidate_version": result["candidate_version"],
        "dataset_id": result["dataset_id"],
        "dataset_sha256": result["dataset_sha256"],
        "dataset_version": result["dataset_version"],
        "overall": result["overall"],
        "categories": result["categories"],
        "status_counts": result["status_counts"],
    }
    if output is not None:
        summary["result_path"] = str(output)
    return summary


def _smoke(dataset_path: Path) -> dict[str, object]:
    first = run_evaluation(dataset_path)
    second = run_evaluation(dataset_path)
    checks = 0
    assert first == second
    checks += 1
    assert first.overall.cases == 28
    checks += 1
    assert first.overall.successful_cases == 28
    checks += 1
    assert first.overall.tool_selection_accuracy == 1
    checks += 1
    assert first.overall.expected_tool_arguments == 73
    assert first.overall.correct_tool_arguments == 72
    checks += 1
    assert first.overall.loop_rate == 0 and first.overall.unsafe_action_rate == 0
    checks += 1
    assert first.overall.total_cost_units == 265
    checks += 1
    assert first.status_counts == {"completed": 10, "escalated": 9, "failed": 9}
    checks += 1
    return {
        "cases": first.overall.cases,
        "checks": checks,
        "status": "ok",
        "task_completion_rate": first.overall.task_completion_rate,
        "tool_argument_accuracy": first.overall.tool_argument_accuracy,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("evaluate", "case", "smoke"))
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--case-id", default="W18-001")
    parser.add_argument("--output-dir", type=Path)
    return parser


def main() -> None:
    args = _parser().parse_args()
    dataset_path: Path = args.dataset
    if args.command == "smoke":
        _json(_smoke(dataset_path))
        return
    if args.command == "case":
        dataset, _ = load_dataset(dataset_path)
        selected = next(
            (case for case in dataset.cases if case.case_id == args.case_id),
            None,
        )
        if selected is None:
            raise SystemExit(f"unknown case ID: {args.case_id}")
        observation = run_candidate(selected)
        _json(
            {
                "case": selected.model_dump(mode="json"),
                "observation": observation.model_dump(mode="json"),
                "score": score_case(selected, observation).model_dump(mode="json"),
            }
        )
        return

    run = run_evaluation(dataset_path)
    output_path = (
        persist_run(run, args.output_dir) if args.output_dir is not None else None
    )
    _json(_summary(run, output_path))


if __name__ == "__main__":
    main()
