"""Strict contracts for the Week 23 system-design rubric."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Identifier = Annotated[
    str, Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9._:-]+$")
]
CaseId = Literal[
    "enterprise-rag",
    "procurement-agent",
    "support-copilot",
    "document-intelligence",
    "local-model-gateway",
    "agent-evaluation-platform",
]
Dimension = Literal[
    "requirements",
    "metrics",
    "data",
    "architecture",
    "retrieval_tools",
    "model",
    "evaluation",
    "deployment",
    "monitoring",
    "security",
    "cost",
    "failure",
]
Gate = Literal["ready_for_mock_interview", "revise"]
MissingField = Literal["decision", "evidence", "trade_off", "failure_control"]


DIMENSIONS: tuple[Dimension, ...] = (
    "requirements",
    "metrics",
    "data",
    "architecture",
    "retrieval_tools",
    "model",
    "evaluation",
    "deployment",
    "monitoring",
    "security",
    "cost",
    "failure",
)
CRITICAL_DIMENSIONS: frozenset[Dimension] = frozenset(
    {"requirements", "evaluation", "security", "cost", "failure"}
)


class StrictModel(BaseModel):
    """Reject coercion, unknown fields and mutation."""

    model_config = ConfigDict(
        allow_inf_nan=False, extra="forbid", frozen=True, strict=True
    )


class DesignCase(StrictModel):
    """One bounded interview prompt and its non-negotiable constraints."""

    case_id: CaseId
    title: Annotated[str, Field(min_length=5, max_length=120)]
    goal: Annotated[str, Field(min_length=20, max_length=400)]
    constraints: tuple[Annotated[str, Field(min_length=5, max_length=240)], ...]
    risk_focus: tuple[Annotated[str, Field(min_length=3, max_length=120)], ...]


class SectionAnswer(StrictModel):
    """Evidence fields used to assess one design dimension structurally."""

    dimension: Dimension
    decision: Annotated[str, Field(max_length=1_000)] = ""
    evidence: Annotated[str, Field(max_length=1_000)] = ""
    trade_off: Annotated[str, Field(max_length=1_000)] = ""
    failure_control: Annotated[str, Field(max_length=1_000)] = ""


class DesignProposal(StrictModel):
    """A complete or partial answer that can be reviewed without an LLM."""

    case_id: CaseId
    sections: tuple[SectionAnswer, ...]
    assumptions: tuple[Annotated[str, Field(min_length=3, max_length=240)], ...]
    rejected_alternatives: tuple[
        Annotated[str, Field(min_length=3, max_length=300)], ...
    ]

    @model_validator(mode="after")
    def section_dimensions_are_unique(self) -> DesignProposal:
        dimensions = [section.dimension for section in self.sections]
        if len(dimensions) != len(set(dimensions)):
            raise ValueError("duplicate_design_dimension")
        return self


class DimensionReview(StrictModel):
    """A transparent 0–4 completeness score for one dimension."""

    dimension: Dimension
    score: Annotated[int, Field(ge=0, le=4)]
    missing_fields: tuple[MissingField, ...]


class DesignReview(StrictModel):
    """Deterministic structural readiness evidence, not semantic approval."""

    case_id: CaseId
    gate: Gate
    total_score: Annotated[int, Field(ge=0, le=48)]
    maximum_score: Literal[48] = 48
    reviews: tuple[DimensionReview, ...]
    missing_dimensions: tuple[Dimension, ...]
    critical_gaps: tuple[Dimension, ...]
    warnings: tuple[str, ...]

    @model_validator(mode="after")
    def aggregate_fields_agree(self) -> DesignReview:
        if self.total_score != sum(review.score for review in self.reviews):
            raise ValueError("review_score_mismatch")
        if len(self.reviews) != len(DIMENSIONS):
            raise ValueError("all_dimensions_must_be_reviewed")
        if self.gate == "ready_for_mock_interview" and self.critical_gaps:
            raise ValueError("ready_gate_cannot_have_critical_gaps")
        return self
