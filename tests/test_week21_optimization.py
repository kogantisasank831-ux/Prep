"""Week 21 model-routing, token-budget, latency and cache contracts."""

from __future__ import annotations

import json
import subprocess
import sys

import pytest
from pydantic import ValidationError

from labs.week_21.demo import sample_workload
from labs.week_21.models import OptimisationPolicy, WorkItem
from labs.week_21.optimizer import (
    PROFILES,
    ScopedResponseCache,
    WorkloadEvaluator,
    compare_strategies,
)


def _item(**updates: object) -> WorkItem:
    values: dict[str, object] = {
        "request_id": "request-1",
        "tenant_id": "tenant-a",
        "task": "extraction",
        "input_tokens": 1_000,
        "output_tokens": 100,
        "optional_context_tokens": 0,
        "complexity_bps": 2_000,
        "cache_key": "document-1:v1",
    }
    values.update(updates)
    return WorkItem.model_validate(values)


def test_work_item_is_strict_frozen_and_closed() -> None:
    with pytest.raises(ValidationError):
        _item(input_tokens="1000")
    with pytest.raises(ValidationError):
        _item(unknown=True)
    item = _item()
    with pytest.raises(ValidationError):
        item.input_tokens = 2_000


def test_optional_context_cannot_exceed_total_input() -> None:
    with pytest.raises(ValidationError, match="optional_context_exceeds_input"):
        _item(input_tokens=100, optional_context_tokens=101)


def test_all_large_uses_large_profile_for_every_item() -> None:
    report = WorkloadEvaluator().evaluate(sample_workload(), "all-large")
    assert {row.selected_model for row in report.decisions} == {"large-model"}


def test_routed_strategy_keeps_simple_work_small_and_complex_work_large() -> None:
    report = WorkloadEvaluator().evaluate(sample_workload(), "routed")
    assert [row.selected_model for row in report.decisions] == [
        "small-model",
        "small-model",
        "large-model",
        "small-model",
    ]


def test_quality_floor_escalates_a_difficult_small_model_request() -> None:
    item = _item(task="recommendation", complexity_bps=5_000)
    policy = OptimisationPolicy(
        large_model_threshold_bps=9_000,
        quality_floor_bps=8_500,
    )
    decision = WorkloadEvaluator(policy).decide(item, "routed")
    assert decision.selected_model == "large-model"
    assert "quality_floor_escalation" in decision.warnings


def test_pruning_removes_only_declared_optional_context() -> None:
    item = _item(
        input_tokens=6_000,
        optional_context_tokens=3_000,
        output_tokens=100,
    )
    decision = WorkloadEvaluator().decide(item, "routed")
    assert decision.billed_input_tokens == 4_000
    assert decision.pruned_tokens == 2_000
    assert decision.estimated_quality_bps == 8_750


def test_required_context_is_not_cut_below_declared_boundary() -> None:
    item = _item(input_tokens=6_000, optional_context_tokens=500)
    decision = WorkloadEvaluator().decide(item, "routed")
    assert decision.billed_input_tokens == 5_500
    assert decision.pruned_tokens == 500


def test_request_over_cost_budget_is_rejected_without_model_selection() -> None:
    item = _item(
        task="recommendation",
        complexity_bps=9_000,
        input_tokens=10_000,
        output_tokens=5_000,
    )
    policy = OptimisationPolicy(max_request_cost_microunits=10)
    decision = WorkloadEvaluator(policy).decide(item, "routed")
    assert decision.status == "budget_rejected"
    assert decision.selected_model is None
    assert decision.estimated_cost_microunits > 10
    assert decision.end_to_end_ms == 0


def test_ttft_precedes_completion_and_large_profile_is_slower_fixture() -> None:
    item = _item()
    evaluator = WorkloadEvaluator()
    small = evaluator.decide(item, "routed")
    large = evaluator.decide(item, "all-large")
    assert small.ttft_ms < small.end_to_end_ms
    assert large.ttft_ms < large.end_to_end_ms
    assert large.end_to_end_ms > small.end_to_end_ms


def test_cost_uses_both_input_and_output_tokens() -> None:
    evaluator = WorkloadEvaluator()
    baseline = evaluator.decide(_item(output_tokens=1), "routed")
    longer = evaluator.decide(
        _item(request_id="request-2", output_tokens=500), "routed"
    )
    assert longer.estimated_cost_microunits > baseline.estimated_cost_microunits


def test_parallel_groups_use_critical_path_not_sum() -> None:
    items = (
        _item(request_id="a", parallel_group="group-1"),
        _item(request_id="b", parallel_group="group-1", output_tokens=200),
        _item(request_id="c", parallel_group=None),
    )
    report = WorkloadEvaluator().evaluate(items, "routed")
    first, second, third = report.decisions
    assert report.sequential_latency_ms == sum(
        row.end_to_end_ms for row in report.decisions
    )
    assert (
        report.parallel_latency_ms
        == max(first.end_to_end_ms, second.end_to_end_ms) + third.end_to_end_ms
    )


def test_cache_hit_is_scoped_and_avoids_synthetic_model_cost() -> None:
    evaluator = WorkloadEvaluator()
    first = evaluator.decide(_item(request_id="first"), "routed", use_cache=True)
    second = evaluator.decide(_item(request_id="second"), "routed", use_cache=True)
    assert not first.cache_hit
    assert second.cache_hit
    assert second.estimated_cost_microunits == 0
    assert second.end_to_end_ms == 5


def test_cache_does_not_cross_tenant_model_or_prompt_version() -> None:
    evaluator = WorkloadEvaluator()
    evaluator.decide(_item(request_id="first"), "routed", use_cache=True)
    tenant = evaluator.decide(
        _item(request_id="tenant", tenant_id="tenant-b"),
        "routed",
        use_cache=True,
    )
    model = evaluator.decide(_item(request_id="model"), "all-large", use_cache=True)
    prompt = evaluator.decide(
        _item(request_id="prompt"),
        "routed",
        use_cache=True,
        prompt_version="v2",
    )
    assert not tenant.cache_hit
    assert not model.cache_hit
    assert not prompt.cache_hit


def test_recommendations_are_not_cached_by_default() -> None:
    evaluator = WorkloadEvaluator()
    item = _item(task="recommendation", complexity_bps=9_000)
    first = evaluator.decide(item, "routed", use_cache=True)
    second = evaluator.decide(
        item.model_copy(update={"request_id": "second"}),
        "routed",
        use_cache=True,
    )
    assert not first.cache_hit
    assert not second.cache_hit


def test_cache_ignores_missing_keys() -> None:
    cache = ScopedResponseCache()
    assert (
        cache.get(
            tenant_id="tenant-a",
            model="small-model",
            prompt_version="v1",
            cache_key=None,
        )
        is None
    )


def test_routed_strategy_saves_fixture_cost_and_latency() -> None:
    report = compare_strategies(sample_workload())
    assert report.routed_cost_saving_microunits > 0
    assert report.routed_parallel_latency_saving_ms > 0
    assert report.routed.mean_quality_bps >= 8_500
    assert report.quality_delta_bps <= 0


def test_comparison_materializes_generators_once() -> None:
    report = compare_strategies(item for item in sample_workload())
    assert len(report.all_large.decisions) == 4
    assert len(report.routed.decisions) == 4


def test_evaluate_materializes_generators_before_parallel_grouping() -> None:
    report = WorkloadEvaluator().evaluate(
        (item for item in sample_workload()), "routed"
    )
    assert len(report.decisions) == 4
    assert report.parallel_latency_ms > 0
    assert report.parallel_latency_ms < report.sequential_latency_ms


def test_identical_inputs_are_deterministic() -> None:
    assert compare_strategies(sample_workload()) == compare_strategies(
        sample_workload()
    )


def test_profiles_are_explicit_synthetic_fixtures() -> None:
    assert PROFILES["large-model"].input_microunits_per_1k > (
        PROFILES["small-model"].input_microunits_per_1k
    )
    assert PROFILES["large-model"].base_latency_ms > (
        PROFILES["small-model"].base_latency_ms
    )


@pytest.mark.parametrize("command", ["compare", "smoke"])
def test_cli_commands(command: str) -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "labs.week_21.demo", command],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    if command == "smoke":
        assert payload == {"checks": 9, "requests": 4, "status": "ok"}
    else:
        assert payload["all_large"]["completed_count"] == 4
        assert payload["routed"]["completed_count"] == 4
