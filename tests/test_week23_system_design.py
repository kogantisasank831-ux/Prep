"""Week 23 system-design case and structural-rubric contracts."""

from __future__ import annotations

import json
import subprocess
import sys

import pytest
from pydantic import ValidationError

from labs.week_23.cases import CASES, get_case
from labs.week_23.demo import sample_proposal
from labs.week_23.models import DesignProposal, SectionAnswer
from labs.week_23.reviewer import review_proposal


def test_six_cases_cover_the_planned_system_families() -> None:
    assert tuple(CASES) == (
        "enterprise-rag",
        "procurement-agent",
        "support-copilot",
        "document-intelligence",
        "local-model-gateway",
        "agent-evaluation-platform",
    )
    assert all(case.constraints for case in CASES.values())
    assert all(case.risk_focus for case in CASES.values())


def test_case_lookup_returns_immutable_strict_contract() -> None:
    case = get_case("enterprise-rag")
    with pytest.raises(ValidationError):
        case.title = "Changed"
    with pytest.raises(ValidationError):
        case.model_copy(update={"unknown": True}).model_validate(
            {**case.model_dump(), "unknown": True}
        )


def test_duplicate_design_dimensions_are_rejected() -> None:
    section = SectionAnswer(dimension="requirements", decision="A clear decision")
    with pytest.raises(ValidationError, match="duplicate_design_dimension"):
        DesignProposal(
            case_id="enterprise-rag",
            sections=(section, section),
            assumptions=(),
            rejected_alternatives=(),
        )


def test_complete_fixture_passes_structural_gate() -> None:
    review = review_proposal(sample_proposal("enterprise-rag"))
    assert review.gate == "ready_for_mock_interview"
    assert review.total_score == review.maximum_score == 48
    assert not review.missing_dimensions
    assert not review.critical_gaps


def test_partial_field_scoring_is_transparent() -> None:
    proposal = DesignProposal(
        case_id="enterprise-rag",
        sections=(
            SectionAnswer(
                dimension="requirements",
                decision="Define active users and grounded answer scope.",
                evidence="Measure accepted answer and abstention rates.",
                trade_off="",
                failure_control="Reject requests outside the declared scope.",
            ),
        ),
        assumptions=("Traffic shape needs production measurement.",),
        rejected_alternatives=("Unbounded public search is outside the boundary.",),
    )
    review = review_proposal(proposal)
    requirements = review.reviews[0]
    assert requirements.score == 3
    assert requirements.missing_fields == ("trade_off",)
    assert review.missing_dimensions[0] == "metrics"


def test_missing_critical_dimensions_block_gate() -> None:
    review = review_proposal(sample_proposal("enterprise-rag", complete=False))
    assert review.gate == "revise"
    assert review.critical_gaps == ("evaluation", "security", "failure")
    assert review.total_score == 36


@pytest.mark.parametrize(
    ("field", "warning"),
    [
        ("assumptions", "assumptions_not_declared"),
        ("rejected_alternatives", "alternatives_not_compared"),
    ],
)
def test_missing_reasoning_context_blocks_gate(field: str, warning: str) -> None:
    proposal = sample_proposal("enterprise-rag").model_copy(update={field: ()})
    review = review_proposal(proposal)
    assert review.total_score == 48
    assert review.gate == "revise"
    assert warning in review.warnings


def test_short_placeholders_do_not_receive_points() -> None:
    proposal = DesignProposal(
        case_id="enterprise-rag",
        sections=(
            SectionAnswer(
                dimension="requirements",
                decision="TBD",
                evidence="later",
                trade_off="none",
                failure_control="unknown",
            ),
        ),
        assumptions=(),
        rejected_alternatives=(),
    )
    assert review_proposal(proposal).reviews[0].score == 0


def test_review_is_ordered_and_deterministic() -> None:
    proposal = sample_proposal("local-model-gateway")
    first = review_proposal(proposal)
    second = review_proposal(proposal)
    assert first == second
    assert first.reviews[0].dimension == "requirements"
    assert first.reviews[-1].dimension == "failure"


@pytest.mark.parametrize("command", ["cases", "review", "smoke"])
def test_cli_commands(command: str) -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "labs.week_23.demo", command],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    if command == "cases":
        assert len(payload) == 6
    elif command == "review":
        assert payload["review"]["gate"] == "ready_for_mock_interview"
    else:
        assert payload == {"cases": 6, "checks": 16, "status": "ok"}
