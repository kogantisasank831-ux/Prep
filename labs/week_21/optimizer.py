"""Deterministic model-routing, token-budget and cache simulator."""

from __future__ import annotations

from collections.abc import Iterable

from labs.week_21.models import (
    ComparisonReport,
    InferenceDecision,
    ModelName,
    ModelProfile,
    OptimisationPolicy,
    Strategy,
    StrategyReport,
    TaskKind,
    WorkItem,
)


PROFILES: dict[ModelName, ModelProfile] = {
    "small-model": ModelProfile(
        name="small-model",
        input_microunits_per_1k=120,
        output_microunits_per_1k=480,
        base_latency_ms=80,
        input_tokens_per_second=8_000,
        output_tokens_per_second=240,
    ),
    "large-model": ModelProfile(
        name="large-model",
        input_microunits_per_1k=1_000,
        output_microunits_per_1k=4_000,
        base_latency_ms=220,
        input_tokens_per_second=4_000,
        output_tokens_per_second=90,
    ),
}

_BASE_QUALITY: dict[tuple[ModelName, TaskKind], int] = {
    ("small-model", "routing"): 9_500,
    ("small-model", "extraction"): 9_000,
    ("small-model", "recommendation"): 7_600,
    ("large-model", "routing"): 9_700,
    ("large-model", "extraction"): 9_600,
    ("large-model", "recommendation"): 9_450,
}


def _ceil_div(numerator: int, denominator: int) -> int:
    return (numerator + denominator - 1) // denominator


def _cost(profile: ModelProfile, input_tokens: int, output_tokens: int) -> int:
    return _ceil_div(
        input_tokens * profile.input_microunits_per_1k
        + output_tokens * profile.output_microunits_per_1k,
        1_000,
    )


def _latency(
    profile: ModelProfile, input_tokens: int, output_tokens: int
) -> tuple[int, int]:
    prefill_ms = _ceil_div(input_tokens * 1_000, profile.input_tokens_per_second)
    decode_ms = _ceil_div(output_tokens * 1_000, profile.output_tokens_per_second)
    ttft_ms = profile.base_latency_ms + prefill_ms
    return ttft_ms, ttft_ms + decode_ms


def _quality(model: ModelName, item: WorkItem, pruned_tokens: int) -> int:
    quality = _BASE_QUALITY[(model, item.task)]
    if model == "small-model":
        quality -= item.complexity_bps // 8
    else:
        quality -= item.complexity_bps // 40
    if pruned_tokens:
        required_tokens = item.input_tokens - item.optional_context_tokens
        over_pruned = max(0, pruned_tokens - item.optional_context_tokens)
        quality -= _ceil_div(over_pruned * 4_000, max(required_tokens, 1))
    return max(0, min(10_000, quality))


def _prune_context(item: WorkItem, policy: OptimisationPolicy) -> tuple[int, int]:
    if item.input_tokens <= policy.max_context_tokens:
        return item.input_tokens, 0
    desired_prune = item.input_tokens - policy.max_context_tokens
    safe_prune = min(desired_prune, item.optional_context_tokens)
    return item.input_tokens - safe_prune, safe_prune


def _initial_model(
    item: WorkItem, strategy: Strategy, policy: OptimisationPolicy
) -> ModelName:
    if strategy == "all-large":
        return "large-model"
    if item.task == "recommendation" and (
        item.complexity_bps >= policy.large_model_threshold_bps
    ):
        return "large-model"
    return "small-model"


class ScopedResponseCache:
    """Exact, tenant/model/prompt-scoped cache for safe read-like tasks."""

    def __init__(self) -> None:
        self._entries: dict[tuple[str, str, str, str], InferenceDecision] = {}

    def get(
        self,
        *,
        tenant_id: str,
        model: ModelName,
        prompt_version: str,
        cache_key: str | None,
    ) -> InferenceDecision | None:
        if cache_key is None:
            return None
        return self._entries.get((tenant_id, model, prompt_version, cache_key))

    def put(
        self,
        *,
        tenant_id: str,
        model: ModelName,
        prompt_version: str,
        cache_key: str | None,
        decision: InferenceDecision,
    ) -> None:
        if cache_key is None:
            return
        self._entries[(tenant_id, model, prompt_version, cache_key)] = decision


class WorkloadEvaluator:
    """Apply one explicit optimisation policy to synthetic work."""

    def __init__(self, policy: OptimisationPolicy | None = None) -> None:
        self.policy = policy or OptimisationPolicy()
        self.cache = ScopedResponseCache()

    def decide(
        self,
        item: WorkItem,
        strategy: Strategy,
        *,
        prompt_version: str = "v1",
        use_cache: bool = False,
    ) -> InferenceDecision:
        billed_input, pruned = _prune_context(item, self.policy)
        model = _initial_model(item, strategy, self.policy)
        quality = _quality(model, item, pruned)
        warnings: list[str] = []
        if quality < self.policy.quality_floor_bps and model == "small-model":
            model = "large-model"
            quality = _quality(model, item, pruned)
            warnings.append("quality_floor_escalation")
        if pruned:
            warnings.append("optional_context_pruned")

        cached = self.cache.get(
            tenant_id=item.tenant_id,
            model=model,
            prompt_version=prompt_version,
            cache_key=item.cache_key,
        )
        if use_cache and cached is not None:
            return cached.model_copy(
                update={
                    "request_id": item.request_id,
                    "estimated_cost_microunits": 0,
                    "ttft_ms": 5,
                    "end_to_end_ms": 5,
                    "cache_hit": True,
                    "warnings": (*cached.warnings, "exact_response_cache_hit"),
                }
            )

        profile = PROFILES[model]
        estimated_cost = _cost(profile, billed_input, item.output_tokens)
        if estimated_cost > self.policy.max_request_cost_microunits:
            return InferenceDecision(
                request_id=item.request_id,
                status="budget_rejected",
                selected_model=None,
                original_input_tokens=item.input_tokens,
                billed_input_tokens=billed_input,
                pruned_tokens=pruned,
                output_tokens=item.output_tokens,
                estimated_quality_bps=0,
                estimated_cost_microunits=estimated_cost,
                ttft_ms=0,
                end_to_end_ms=0,
                cache_hit=False,
                warnings=(*warnings, "request_cost_budget_exceeded"),
            )
        ttft_ms, end_to_end_ms = _latency(profile, billed_input, item.output_tokens)
        decision = InferenceDecision(
            request_id=item.request_id,
            status="completed",
            selected_model=model,
            original_input_tokens=item.input_tokens,
            billed_input_tokens=billed_input,
            pruned_tokens=pruned,
            output_tokens=item.output_tokens,
            estimated_quality_bps=quality,
            estimated_cost_microunits=estimated_cost,
            ttft_ms=ttft_ms,
            end_to_end_ms=end_to_end_ms,
            cache_hit=False,
            warnings=tuple(warnings),
        )
        if use_cache and item.task in {"routing", "extraction"}:
            self.cache.put(
                tenant_id=item.tenant_id,
                model=model,
                prompt_version=prompt_version,
                cache_key=item.cache_key,
                decision=decision,
            )
        return decision

    def evaluate(self, items: Iterable[WorkItem], strategy: Strategy) -> StrategyReport:
        workload = tuple(items)
        decisions = tuple(self.decide(item, strategy) for item in workload)
        completed = tuple(
            decision for decision in decisions if decision.status == "completed"
        )
        total_cost = sum(row.estimated_cost_microunits for row in decisions)
        sequential_latency = sum(row.end_to_end_ms for row in completed)
        quality = (
            sum(row.estimated_quality_bps for row in completed) // len(completed)
            if completed
            else 0
        )

        grouped_latency: dict[str, int] = {}
        for item, decision in zip(workload, decisions, strict=True):
            if decision.status != "completed":
                continue
            group = item.parallel_group or item.request_id
            grouped_latency[group] = max(
                grouped_latency.get(group, 0), decision.end_to_end_ms
            )
        return StrategyReport(
            strategy=strategy,
            decisions=decisions,
            total_cost_microunits=total_cost,
            sequential_latency_ms=sequential_latency,
            parallel_latency_ms=sum(grouped_latency.values()),
            mean_quality_bps=quality,
            completed_count=len(completed),
            rejected_count=len(decisions) - len(completed),
        )


def compare_strategies(
    items: Iterable[WorkItem], policy: OptimisationPolicy | None = None
) -> ComparisonReport:
    """Evaluate identical materialized work under both routing strategies."""

    workload = tuple(items)
    evaluator = WorkloadEvaluator(policy)
    all_large = evaluator.evaluate(workload, "all-large")
    routed = evaluator.evaluate(workload, "routed")
    return ComparisonReport(
        all_large=all_large,
        routed=routed,
        routed_cost_saving_microunits=(
            all_large.total_cost_microunits - routed.total_cost_microunits
        ),
        routed_parallel_latency_saving_ms=(
            all_large.parallel_latency_ms - routed.parallel_latency_ms
        ),
        quality_delta_bps=routed.mean_quality_bps - all_large.mean_quality_bps,
    )
