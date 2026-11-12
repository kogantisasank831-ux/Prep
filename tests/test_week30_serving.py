"""Week 30 serving-capacity and report contracts."""

from __future__ import annotations

import math
import subprocess
import sys

import pytest
from pydantic import ValidationError

from labs.week_30.demo import (
    sample_config,
    sample_observations,
    sample_report,
)
from labs.week_30.models import ServingConfig, ServingObservation
from labs.week_30.reporting import REQUIRED_SECTIONS, review_report
from labs.week_30.serving import GIB, profile_serving


def test_weight_and_kv_memory_formulas_are_explicit() -> None:
    profile = profile_serving(sample_config(), sample_observations())
    expected_weight = 3_000_000_000 * 4 / 8 / GIB
    expected_kv = 131_072 * 4_096 / GIB
    assert math.isclose(profile.weight_memory_gib, expected_weight)
    assert math.isclose(profile.kv_cache_per_request_gib, expected_kv)


def test_weight_bits_change_only_the_weight_estimate() -> None:
    base = sample_config()
    int4 = profile_serving(base, sample_observations())
    int8 = profile_serving(
        base.model_copy(update={"weight_bits": 8}), sample_observations()
    )
    assert math.isclose(int8.weight_memory_gib, int4.weight_memory_gib * 2)
    assert int8.kv_cache_per_request_gib == int4.kv_cache_per_request_gib


def test_requested_profile_is_feasible_with_visible_capacity() -> None:
    profile = profile_serving(sample_config(), sample_observations())
    assert profile.feasible is True
    assert profile.estimated_max_concurrency >= profile.requested_concurrency
    assert len(profile.warnings) == 3


def test_infeasible_concurrency_is_visible() -> None:
    config = sample_config().model_copy(update={"requested_concurrency": 30})
    profile = profile_serving(config, sample_observations())
    assert profile.feasible is False
    assert "exceeds" in profile.warnings[-1]


def test_throughput_and_nearest_rank_percentiles_use_observations() -> None:
    observations = sample_observations()
    profile = profile_serving(sample_config(), observations)
    assert math.isclose(
        profile.measured_tokens_per_second,
        sum(item.generated_tokens for item in observations)
        / sum(item.duration_seconds for item in observations),
    )
    assert profile.ttft_p50_ms == 110.0
    assert profile.ttft_p95_ms == 240.0
    assert profile.latency_p50_ms == 790.0
    assert profile.latency_p95_ms == 1_280.0


def test_empty_observations_and_invalid_latency_are_rejected() -> None:
    with pytest.raises(ValueError, match="observations_required"):
        profile_serving(sample_config(), ())
    with pytest.raises(ValidationError, match="end_to_end_before"):
        ServingObservation(
            generated_tokens=1,
            duration_seconds=1.0,
            batch_size=1,
            time_to_first_token_ms=20.0,
            end_to_end_latency_ms=10.0,
        )


def test_complete_report_passes_with_visible_zero_cost_warning() -> None:
    report = sample_report()
    review = review_report(report.model_dump(mode="json"))
    assert review.valid is True
    assert review.missing_sections == ()
    assert any("Zero external spend" in warning for warning in review.warnings)


def test_missing_report_sections_are_listed() -> None:
    review = review_report({"objective": "too short"})
    assert review.valid is False
    assert review.missing_sections == REQUIRED_SECTIONS[1:]


def test_non_mapping_report_is_rejected() -> None:
    review = review_report("report")
    assert review.valid is False
    assert review.missing_sections == REQUIRED_SECTIONS


def test_failed_loss_trend_and_empty_failures_create_warnings() -> None:
    report = sample_report().model_copy(
        update={"loss_curve": (1.0, 1.1), "failures": ()}
    )
    review = review_report(report.model_dump(mode="json"))
    assert review.valid is True
    assert any("Final loss" in warning for warning in review.warnings)
    assert any("No failures" in warning for warning in review.warnings)


def test_strict_serving_config_rejects_unsupported_precision() -> None:
    with pytest.raises(ValidationError):
        ServingConfig(
            model_parameters_billions=3.0,
            weight_bits=3,  # type: ignore[arg-type]
            gpu_memory_gib=16.0,
            non_weight_memory_gib=3.0,
            kv_bytes_per_token=1,
            max_context_tokens=1,
            requested_concurrency=1,
        )


def test_cli_modes() -> None:
    for command, marker in (
        ("capacity", '"weight_memory_gib"'),
        ("report", '"rag_comparison"'),
        ("smoke", '"report_review"'),
    ):
        completed = subprocess.run(
            [sys.executable, "-m", "labs.week_30.demo", command],
            check=True,
            capture_output=True,
            text=True,
        )
        assert marker in completed.stdout
