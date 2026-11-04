"""Machine-readable CLI for the Week 17 multi-agent lab."""

from __future__ import annotations

import argparse
import json
from typing import Callable

from labs.week_17.fixtures import CASES
from labs.week_17.models import (
    Assignment,
    Recommendation,
    SpecialistName,
    SpecialistResult,
)
from labs.week_17.specialists import DEFAULT_SPECIALISTS, SpecialistFailure
from labs.week_17.supervisor import (
    Supervisor,
    compare_architectures,
    default_supervisor,
    run_single_workflow,
)


def _json(value: object) -> None:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    print(json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2))


def _failed_document(_: Assignment) -> SpecialistResult:
    raise SpecialistFailure("fixture_document_unavailable")


def _smoke() -> dict[str, object]:
    checks = 0
    expected = {
        "price-spike": Recommendation.REVIEW_REQUIRED,
        "stable-price": Recommendation.NO_REVIEW,
        "missing-terms": Recommendation.NEEDS_HUMAN,
        "supplier-risk": Recommendation.REVIEW_REQUIRED,
    }
    for case_name, recommendation in expected.items():
        result = default_supervisor().run(CASES[case_name], run_id=f"smoke-{case_name}")
        assert result.report is not None
        assert result.report.recommendation is recommendation
        checks += 1

    first = default_supervisor().run(CASES["price-spike"], run_id="smoke-repeat")
    second = default_supervisor().run(CASES["price-spike"], run_id="smoke-repeat")
    assert first == second
    checks += 1

    compared = compare_architectures(CASES["price-spike"], run_id="smoke-compare")
    assert compared.outcome_equal
    checks += 1
    assert compared.supervisor_handoffs == 4 and compared.workflow_handoffs == 0
    checks += 1
    assert (
        compared.supervisor_dependency_stages == 2
        and compared.workflow_dependency_stages == 4
    )
    checks += 1

    registry: dict[SpecialistName, Callable[[Assignment], SpecialistResult]] = dict(
        DEFAULT_SPECIALISTS
    )
    registry[SpecialistName.DOCUMENT] = _failed_document
    failed = Supervisor(registry).run(CASES["price-spike"], run_id="smoke-failure")
    assert failed.report is None and failed.failure_reason is not None
    checks += 1
    assert "fixture_document_unavailable" in failed.failure_reason
    checks += 1
    return {"checks": checks, "status": "ok"}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("run", "workflow", "compare", "smoke"))
    parser.add_argument("--case", choices=tuple(CASES), default="price-spike")
    parser.add_argument("--run-id", default="week17-demo")
    return parser


def main() -> None:
    args = _parser().parse_args()
    if args.command == "smoke":
        _json(_smoke())
        return
    case = CASES[args.case]
    if args.command == "run":
        _json(default_supervisor().run(case, run_id=args.run_id))
    elif args.command == "workflow":
        _json(run_single_workflow(case, run_id=args.run_id))
    else:
        _json(compare_architectures(case, run_id=args.run_id))


if __name__ == "__main__":
    main()
