"""Closed contracts for the Week 18 offline agent evaluation."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator


Identifier = Annotated[
    str, Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9._:-]+$")
]
Category = Literal[
    "normal",
    "missing_information",
    "tool_failure",
    "conflicting_evidence",
    "prompt_injection",
    "invalid_tool_arguments",
    "approval_required",
]
Scenario = Literal[
    "normal",
    "fail_document",
    "fail_sql",
    "fail_supplier_risk",
    "fail_commercial",
    "wrong_run_document",
    "wrong_case_sql",
    "supplier_conflict",
    "bad_document_digest",
    "invalid_sql_arguments",
]
AgentStatus = Literal["completed", "escalated", "failed"]
RecommendationValue = Literal["no_review", "review_required", "needs_human"]
ToolValue = Literal["document", "sql", "supplier_risk", "commercial"]


class StrictModel(BaseModel):
    """Reject coercion and unknown fields at every evaluation boundary."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class AgentRequest(StrictModel):
    """The narrow public request accepted by Procurement Agent v1."""

    run_id: Identifier
    objective: Literal["investigate_procurement_case"]
    case_name: Literal["price-spike", "stable-price", "missing-terms", "supplier-risk"]
    requested_action: Literal["investigate", "approve", "purchase", "contact_supplier"]
    untrusted_text: Annotated[str | None, Field(max_length=600)] = None


class EvaluationCase(StrictModel):
    """One visible synthetic task with independently declared expectations."""

    case_id: Annotated[str, Field(pattern=r"^W18-[0-9]{3}$")]
    category: Category
    description: Annotated[str, Field(min_length=20, max_length=240)]
    payload: dict[str, JsonValue]
    scenario: Scenario
    expected_status: AgentStatus
    expected_recommendation: RecommendationValue | None
    expected_tools: tuple[ToolValue, ...]
    expected_failure_code: str | None

    @model_validator(mode="after")
    def expectation_fields_agree(self) -> EvaluationCase:
        if len(set(self.expected_tools)) != len(self.expected_tools):
            raise ValueError("expected_tools_not_unique")
        if self.expected_status == "completed":
            if self.expected_recommendation is None or self.expected_failure_code:
                raise ValueError("completed_expectation_invalid")
        elif self.expected_status == "escalated":
            has_business_result = self.expected_recommendation == "needs_human"
            has_failure = bool(self.expected_failure_code)
            if has_business_result == has_failure:
                raise ValueError("escalation_expectation_invalid")
        elif self.expected_recommendation is not None or not self.expected_failure_code:
            raise ValueError("failed_expectation_invalid")
        return self


class EvaluationDataset(StrictModel):
    """Versioned collection of visible offline agent tasks."""

    schema_version: Literal["procurement-agent-evaluation/1.0.0"] = Field(
        alias="schema"
    )
    dataset_id: Literal["week18-procurement-agent-v1"]
    version: Annotated[str, Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")]
    cases: tuple[EvaluationCase, ...]

    @model_validator(mode="after")
    def cases_are_complete(self) -> EvaluationDataset:
        if len(self.cases) != 28:
            raise ValueError("dataset_requires_28_cases")
        if len({case.case_id for case in self.cases}) != len(self.cases):
            raise ValueError("duplicate_case_id")
        expected_categories = {
            "normal",
            "missing_information",
            "tool_failure",
            "conflicting_evidence",
            "prompt_injection",
            "invalid_tool_arguments",
            "approval_required",
        }
        if {case.category for case in self.cases} != expected_categories:
            raise ValueError("category_coverage_incomplete")
        return self


class ToolCall(StrictModel):
    """Minimal tool trajectory record; source bodies and prompts are excluded."""

    step: Annotated[int, Field(ge=1, le=8)]
    tool: ToolValue
    arguments: dict[str, JsonValue]
    cost_units: Annotated[int, Field(ge=0, le=100)]
    fixture_latency_ms: Annotated[int, Field(ge=0, le=10_000)]


class AgentObservation(StrictModel):
    """Observable end state and trajectory for one candidate attempt."""

    case_id: Identifier
    status: AgentStatus
    recommendation: RecommendationValue | None
    failure_code: str | None
    tool_calls: tuple[ToolCall, ...]
    steps: Annotated[int, Field(ge=1, le=20)]
    human_escalated: bool
    requires_human_approval: bool
    cost_units: Annotated[int, Field(ge=0, le=1_000)]
    fixture_latency_ms: Annotated[int, Field(ge=0, le=100_000)]
    unsafe_actions: tuple[str, ...]

    @model_validator(mode="after")
    def outcome_fields_agree(self) -> AgentObservation:
        if self.steps != 1 + len(self.tool_calls):
            raise ValueError("step_count_mismatch")
        if self.cost_units != sum(call.cost_units for call in self.tool_calls):
            raise ValueError("cost_total_mismatch")
        if self.status == "completed":
            if self.recommendation is None or self.failure_code is not None:
                raise ValueError("completed_observation_invalid")
        elif self.status == "escalated":
            has_business_result = self.recommendation == "needs_human"
            has_failure = bool(self.failure_code)
            if has_business_result == has_failure or not self.human_escalated:
                raise ValueError("escalated_observation_invalid")
        elif self.recommendation is not None or not self.failure_code:
            raise ValueError("failed_observation_invalid")
        return self


class CaseScore(StrictModel):
    """Deterministic graders for one case and one candidate observation."""

    case_id: Identifier
    task_success: bool
    outcome_correct: bool
    tool_selection_correct: bool
    tool_argument_correct: Annotated[int, Field(ge=0)]
    tool_argument_total: Annotated[int, Field(ge=0)]
    step_efficiency: Annotated[float, Field(ge=0, le=1)]
    loop_detected: bool
    human_escalated: bool
    unsafe_action: bool
    failures: tuple[str, ...]


class MetricSet(StrictModel):
    """Aggregate metrics with their raw denominators kept visible."""

    cases: Annotated[int, Field(ge=1)]
    successful_cases: Annotated[int, Field(ge=0)]
    expected_tool_arguments: Annotated[int, Field(ge=0)]
    correct_tool_arguments: Annotated[int, Field(ge=0)]
    task_completion_rate: Annotated[float, Field(ge=0, le=1)]
    tool_selection_accuracy: Annotated[float, Field(ge=0, le=1)]
    tool_argument_accuracy: Annotated[float | None, Field(ge=0, le=1)]
    mean_step_efficiency: Annotated[float, Field(ge=0, le=1)]
    loop_rate: Annotated[float, Field(ge=0, le=1)]
    human_escalation_rate: Annotated[float, Field(ge=0, le=1)]
    total_cost_units: Annotated[int, Field(ge=0)]
    cost_units_per_successful_task: Annotated[float | None, Field(ge=0)]
    mean_fixture_latency_ms: Annotated[float, Field(ge=0)]
    unsafe_action_rate: Annotated[float, Field(ge=0, le=1)]


class CategoryMetrics(StrictModel):
    """A named dataset slice and its independently computed metrics."""

    category: Category
    metrics: MetricSet


class EvaluationRun(StrictModel):
    """Complete, reproducible evaluation artifact."""

    schema_version: Literal["procurement-agent-evaluation-result/1.0.0"] = Field(
        alias="schema"
    )
    dataset_id: Identifier
    dataset_version: str
    dataset_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    candidate_version: Identifier
    overall: MetricSet
    categories: tuple[CategoryMetrics, ...]
    status_counts: dict[AgentStatus, Annotated[int, Field(ge=0)]]
    observations: tuple[AgentObservation, ...]
    scores: tuple[CaseScore, ...]

    @model_validator(mode="after")
    def result_rows_align(self) -> EvaluationRun:
        if len(self.observations) != self.overall.cases:
            raise ValueError("observation_count_mismatch")
        if len(self.scores) != self.overall.cases:
            raise ValueError("score_count_mismatch")
        observation_ids = tuple(row.case_id for row in self.observations)
        if observation_ids != tuple(row.case_id for row in self.scores):
            raise ValueError("result_case_order_mismatch")
        if sum(self.status_counts.values()) != self.overall.cases:
            raise ValueError("status_count_mismatch")
        return self
