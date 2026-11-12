"""Weight/KV estimates and measured serving summaries."""

from __future__ import annotations

import math

from labs.week_30.models import ServingConfig, ServingObservation, ServingProfile


GIB = 1024**3


def _nearest_rank(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    rank = max(1, math.ceil(percentile * len(ordered)))
    return ordered[rank - 1]


def profile_serving(
    config: ServingConfig, observations: tuple[ServingObservation, ...]
) -> ServingProfile:
    """Combine transparent worst-context memory estimates with load evidence."""

    if not observations:
        raise ValueError("observations_required")
    weight_memory = (
        config.model_parameters_billions * 1_000_000_000 * config.weight_bits / 8 / GIB
    )
    kv_per_request = config.kv_bytes_per_token * config.max_context_tokens / GIB
    available_for_kv = (
        config.gpu_memory_gib - weight_memory - config.non_weight_memory_gib
    )
    max_concurrency = max(0, math.floor(available_for_kv / kv_per_request))
    requested_memory = (
        weight_memory
        + config.non_weight_memory_gib
        + kv_per_request * config.requested_concurrency
    )
    feasible = requested_memory <= config.gpu_memory_gib
    warnings = [
        "Weight memory is a theoretical packed-weight estimate, not measured allocation.",
        "Non-weight memory must include activations, runtime workspaces, fragmentation and safety headroom.",
        "KV capacity reserves maximum context for every concurrent request; real schedulers vary usage.",
    ]
    if not feasible:
        warnings.append(
            "Requested worst-case concurrency exceeds the declared GPU memory budget."
        )
    total_tokens = sum(observation.generated_tokens for observation in observations)
    total_duration = sum(observation.duration_seconds for observation in observations)
    ttft = [observation.time_to_first_token_ms for observation in observations]
    latency = [observation.end_to_end_latency_ms for observation in observations]
    return ServingProfile(
        weight_memory_gib=weight_memory,
        kv_cache_per_request_gib=kv_per_request,
        requested_memory_gib=requested_memory,
        estimated_max_concurrency=max_concurrency,
        requested_concurrency=config.requested_concurrency,
        feasible=feasible,
        measured_tokens_per_second=total_tokens / total_duration,
        ttft_p50_ms=_nearest_rank(ttft, 0.50),
        ttft_p95_ms=_nearest_rank(ttft, 0.95),
        latency_p50_ms=_nearest_rank(latency, 0.50),
        latency_p95_ms=_nearest_rank(latency, 0.95),
        warnings=tuple(warnings),
    )
