"""Run the deterministic Week 21 workload comparison and smoke checks."""

from __future__ import annotations

import argparse
import json

from labs.week_21.models import WorkItem
from labs.week_21.optimizer import WorkloadEvaluator, compare_strategies


def sample_workload() -> tuple[WorkItem, ...]:
    """Return mixed work with one safe parallel group and optional context."""

    return (
        WorkItem(
            request_id="route-1",
            tenant_id="tenant-acme",
            task="routing",
            input_tokens=600,
            output_tokens=20,
            complexity_bps=2_000,
            cache_key="route:supplier-risk",
            parallel_group="intake",
        ),
        WorkItem(
            request_id="extract-1",
            tenant_id="tenant-acme",
            task="extraction",
            input_tokens=5_000,
            optional_context_tokens=1_500,
            output_tokens=180,
            complexity_bps=4_000,
            cache_key="extract:contract-171:v1",
            parallel_group="intake",
        ),
        WorkItem(
            request_id="recommend-1",
            tenant_id="tenant-acme",
            task="recommendation",
            input_tokens=3_200,
            output_tokens=500,
            complexity_bps=8_000,
        ),
        WorkItem(
            request_id="extract-2",
            tenant_id="tenant-acme",
            task="extraction",
            input_tokens=1_200,
            output_tokens=120,
            complexity_bps=3_000,
            cache_key="extract:invoice-42:v1",
        ),
    )


def _smoke() -> dict[str, object]:
    report = compare_strategies(sample_workload())
    checks = 0
    assert report.all_large.completed_count == 4
    assert report.routed.completed_count == 4
    checks += 2
    assert report.routed_cost_saving_microunits > 0
    assert report.routed_parallel_latency_saving_ms > 0
    checks += 2
    selected = [row.selected_model for row in report.routed.decisions]
    assert selected == [
        "small-model",
        "small-model",
        "large-model",
        "small-model",
    ]
    checks += 1
    assert report.routed.decisions[1].pruned_tokens == 1_000
    checks += 1
    evaluator = WorkloadEvaluator()
    item = sample_workload()[0]
    first = evaluator.decide(item, "routed", use_cache=True)
    second = evaluator.decide(
        item.model_copy(update={"request_id": "route-2"}),
        "routed",
        use_cache=True,
    )
    assert not first.cache_hit and second.cache_hit
    assert second.estimated_cost_microunits == 0
    checks += 2
    assert compare_strategies(sample_workload()) == compare_strategies(
        sample_workload()
    )
    checks += 1
    return {"checks": checks, "requests": 4, "status": "ok"}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("compare", "smoke"))
    return parser


def main() -> None:
    args = _parser().parse_args()
    payload: object
    if args.command == "smoke":
        payload = _smoke()
    else:
        payload = compare_strategies(sample_workload()).model_dump(mode="json")
    print(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
