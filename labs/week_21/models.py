"""Strict contracts for the Week 21 optimisation simulator."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Identifier = Annotated[
    str, Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9._:-]+$")
]
TaskKind = Literal["routing", "extraction", "recommendation"]
ModelName = Literal["small-model", "large-model"]
Strategy = Literal["all-large", "routed"]
DecisionStatus = Literal["completed", "budget_rejected"]


class StrictModel(BaseModel):
    """Reject coercion, non-finite values and unknown fields."""

    model_config = ConfigDict(
        allow_inf_nan=False, extra="forbid", frozen=True, strict=True
    )


class WorkItem(StrictModel):
    """One synthetic inference request with declared token and quality needs."""

    request_id: Identifier
    tenant_id: Identifier
    task: TaskKind
    input_tokens: Annotated[int, Field(ge=1, le=200_000)]
    output_tokens: Annotated[int, Field(ge=1, le=20_000)]
    optional_context_tokens: Annotated[int, Field(ge=0, le=200_000)] = 0
    complexity_bps: Annotated[int, Field(ge=0, le=10_000)]
    cache_key: Identifier | None = None
    parallel_group: Identifier | None = None

    @model_validator(mode="after")
    def optional_context_fits_input(self) -> WorkItem:
        if self.optional_context_tokens > self.input_tokens:
            raise ValueError("optional_context_exceeds_input")
        return self


class ModelProfile(StrictModel):
    """Synthetic model economics; values are not vendor prices or benchmarks."""

    name: ModelName
    input_microunits_per_1k: Annotated[int, Field(ge=0, le=1_000_000)]
    output_microunits_per_1k: Annotated[int, Field(ge=0, le=1_000_000)]
    base_latency_ms: Annotated[int, Field(ge=0, le=300_000)]
    input_tokens_per_second: Annotated[int, Field(ge=1, le=10_000_000)]
    output_tokens_per_second: Annotated[int, Field(ge=1, le=1_000_000)]


class OptimisationPolicy(StrictModel):
    """Finite routing, context and budget policy for the simulator."""

    large_model_threshold_bps: Annotated[int, Field(ge=0, le=10_000)] = 6_500
    quality_floor_bps: Annotated[int, Field(ge=0, le=10_000)] = 8_500
    max_context_tokens: Annotated[int, Field(ge=128, le=200_000)] = 4_000
    max_request_cost_microunits: Annotated[int, Field(ge=1, le=1_000_000_000)] = 100_000


class InferenceDecision(StrictModel):
    """One inspectable routing and cost decision."""

    request_id: Identifier
    status: DecisionStatus
    selected_model: ModelName | None
    original_input_tokens: int
    billed_input_tokens: int
    pruned_tokens: int
    output_tokens: int
    estimated_quality_bps: int
    estimated_cost_microunits: int
    ttft_ms: int
    end_to_end_ms: int
    cache_hit: bool
    warnings: tuple[str, ...]

    @model_validator(mode="after")
    def fields_match_status(self) -> InferenceDecision:
        if self.status == "budget_rejected" and self.selected_model is not None:
            raise ValueError("rejected_decision_cannot_select_model")
        if self.status == "completed" and self.selected_model is None:
            raise ValueError("completed_decision_requires_model")
        return self


class StrategyReport(StrictModel):
    """Aggregate evidence for one workload and one strategy."""

    strategy: Strategy
    decisions: tuple[InferenceDecision, ...]
    total_cost_microunits: int
    sequential_latency_ms: int
    parallel_latency_ms: int
    mean_quality_bps: int
    completed_count: int
    rejected_count: int


class ComparisonReport(StrictModel):
    """Side-by-side all-large and routed results over identical work."""

    all_large: StrategyReport
    routed: StrategyReport
    routed_cost_saving_microunits: int
    routed_parallel_latency_saving_ms: int
    quality_delta_bps: int
