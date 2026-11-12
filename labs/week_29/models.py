"""Strict contracts for comparable Week 29 evaluations."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Task = Literal["qa", "classification"]
Winner = Literal["left", "right", "tie"]


class EvaluationExample(BaseModel):
    """One frozen test case and its segment metadata."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    example_id: str = Field(min_length=1)
    task: Task
    segment: str = Field(min_length=1)
    expected: str = Field(min_length=1)
    contaminated: bool = False


class CandidateOutput(BaseModel):
    """Versioned candidate response on one frozen example."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    candidate: str = Field(min_length=1)
    example_id: str = Field(min_length=1)
    response: str = Field(min_length=1)
    negative_log_likelihood: float | None = Field(default=None, ge=0.0, le=100.0)


class PairwiseVote(BaseModel):
    """Blind human preference between two candidate outputs."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    case_id: str = Field(min_length=1)
    reviewer_id: str = Field(min_length=1)
    left_candidate: str = Field(min_length=1)
    right_candidate: str = Field(min_length=1)
    winner: Winner

    @model_validator(mode="after")
    def validate_pair(self) -> PairwiseVote:
        if self.left_candidate == self.right_candidate:
            raise ValueError("pair_requires_distinct_candidates")
        return self


class EvaluationConfig(BaseModel):
    """Frozen evaluation policy."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    baseline_candidate: str = "base"
    positive_label: str = "review"
    include_contaminated: bool = False
    bootstrap_samples: int = Field(default=500, ge=100, le=10_000)
    seed: int = Field(default=29, ge=0)


class SegmentMetric(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    segment: str
    count: int = Field(ge=1)
    exact_match_rate: float = Field(ge=0.0, le=1.0)


class CandidateMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    candidate: str
    count: int = Field(ge=1)
    exact_matches: int = Field(ge=0)
    exact_match_rate: float = Field(ge=0.0, le=1.0)
    classification_precision: float | None = Field(default=None, ge=0.0, le=1.0)
    classification_recall: float | None = Field(default=None, ge=0.0, le=1.0)
    classification_f1: float | None = Field(default=None, ge=0.0, le=1.0)
    perplexity: float | None = Field(default=None, ge=1.0)
    segments: tuple[SegmentMetric, ...]


class BaselineComparison(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    candidate: str
    baseline: str
    exact_match_delta: float = Field(ge=-1.0, le=1.0)
    bootstrap_low: float = Field(ge=-1.0, le=1.0)
    bootstrap_high: float = Field(ge=-1.0, le=1.0)


class PairwiseSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    left_candidate: str
    right_candidate: str
    left_wins: int = Field(ge=0)
    right_wins: int = Field(ge=0)
    ties: int = Field(ge=0)


class EvaluationReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    evaluated_example_ids: tuple[str, ...]
    excluded_contaminated_ids: tuple[str, ...]
    metrics: tuple[CandidateMetrics, ...]
    comparisons: tuple[BaselineComparison, ...]
    pairwise: tuple[PairwiseSummary, ...]
    limitations: tuple[str, ...]
