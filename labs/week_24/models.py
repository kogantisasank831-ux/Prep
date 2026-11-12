"""Closed evidence, story and review contracts for Week 24."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Identifier = Annotated[
    str, Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9._:-]+$")
]
Depth = Literal["two-minute", "ten-minute", "deep-dive"]
ClaimSource = Literal[
    "situation",
    "task",
    "role",
    "action",
    "decision",
    "metric",
    "failure",
    "limitation",
    "leadership",
    "reflection",
]
ReviewGate = Literal["ready_for_mock_interview", "revise"]


class StrictModel(BaseModel):
    """Reject coercion, unknown fields and mutation."""

    model_config = ConfigDict(
        allow_inf_nan=False, extra="forbid", frozen=True, strict=True
    )


class MetricEvidence(StrictModel):
    """A result with provenance and explicit attribution."""

    name: Annotated[str, Field(min_length=3, max_length=100)]
    value: Annotated[str, Field(min_length=1, max_length=100)]
    source: Annotated[str, Field(min_length=5, max_length=240)]
    attribution: Literal["individual", "team", "organization"]


class DecisionEvidence(StrictModel):
    """One architecture or delivery choice and the alternative considered."""

    decision: Annotated[str, Field(min_length=10, max_length=400)]
    reason: Annotated[str, Field(min_length=10, max_length=400)]
    rejected_alternative: Annotated[str, Field(min_length=10, max_length=400)]
    consequence: Annotated[str, Field(min_length=10, max_length=400)]


class LeadershipEvidence(StrictModel):
    """One bounded leadership example with an observable result."""

    situation: Annotated[str, Field(min_length=10, max_length=400)]
    action: Annotated[str, Field(min_length=10, max_length=400)]
    result: Annotated[str, Field(min_length=10, max_length=400)]
    learning: Annotated[str, Field(min_length=10, max_length=400)]


class ProjectEvidence(StrictModel):
    """The sole source of facts allowed in generated practice stories."""

    project_id: Identifier
    project_name: Annotated[str, Field(min_length=3, max_length=120)]
    situation: Annotated[str, Field(min_length=10, max_length=600)]
    task: Annotated[str, Field(min_length=10, max_length=600)]
    role: Annotated[str, Field(min_length=10, max_length=400)]
    actions: tuple[Annotated[str, Field(min_length=10, max_length=400)], ...]
    decisions: tuple[DecisionEvidence, ...]
    metrics: tuple[MetricEvidence, ...]
    failure: Annotated[str, Field(min_length=10, max_length=500)]
    limitation: Annotated[str, Field(min_length=10, max_length=500)]
    reflection: Annotated[str, Field(min_length=10, max_length=500)]
    leadership: LeadershipEvidence

    @model_validator(mode="after")
    def practice_story_has_core_evidence(self) -> ProjectEvidence:
        if not self.actions:
            raise ValueError("project_requires_action_evidence")
        if not self.decisions:
            raise ValueError("project_requires_decision_evidence")
        if not self.metrics:
            raise ValueError("project_requires_metric_evidence")
        return self


class StoryClaim(StrictModel):
    """One sentence tied to an explicit evidence category."""

    source: ClaimSource
    text: Annotated[str, Field(min_length=10, max_length=700)]


class StoryPack(StrictModel):
    """A depth-specific narrative plus questions that test its weak points."""

    project_id: Identifier
    depth: Depth
    estimated_minutes: Literal[2, 10, 20]
    claims: tuple[StoryClaim, ...]
    follow_up_questions: tuple[
        Annotated[str, Field(min_length=10, max_length=240)], ...
    ]
    warnings: tuple[str, ...]


class StoryReview(StrictModel):
    """Transparent readiness score for practicing, not factual verification."""

    gate: ReviewGate
    structure_score: Annotated[int, Field(ge=0, le=2)]
    ownership_score: Annotated[int, Field(ge=0, le=2)]
    evidence_score: Annotated[int, Field(ge=0, le=2)]
    decision_score: Annotated[int, Field(ge=0, le=2)]
    failure_score: Annotated[int, Field(ge=0, le=2)]
    reflection_score: Annotated[int, Field(ge=0, le=2)]
    total_score: Annotated[int, Field(ge=0, le=12)]
    gaps: tuple[str, ...]
    warnings: tuple[str, ...]

    @model_validator(mode="after")
    def total_matches_dimensions(self) -> StoryReview:
        expected = (
            self.structure_score
            + self.ownership_score
            + self.evidence_score
            + self.decision_score
            + self.failure_score
            + self.reflection_score
        )
        if self.total_score != expected:
            raise ValueError("story_review_total_mismatch")
        return self
