"""Week 24 evidence-grounded project storytelling contracts."""

from __future__ import annotations

import json
import subprocess
import sys

import pytest
from pydantic import ValidationError

from labs.week_24.demo import sample_evidence
from labs.week_24.models import MetricEvidence, ProjectEvidence
from labs.week_24.storytelling import build_story, review_evidence


def test_project_evidence_is_strict_frozen_and_closed() -> None:
    evidence = sample_evidence()
    with pytest.raises(ValidationError):
        evidence.project_name = "Changed"
    with pytest.raises(ValidationError):
        ProjectEvidence.model_validate({**evidence.model_dump(), "unknown": True})


def test_metrics_require_provenance_and_explicit_attribution() -> None:
    with pytest.raises(ValidationError):
        MetricEvidence(
            name="quality",
            value="90%",
            source="",
            attribution="team",
        )
    with pytest.raises(ValidationError):
        MetricEvidence.model_validate(
            {
                "name": "quality",
                "value": "90%",
                "source": "accepted test run",
                "attribution": "mine",
            }
        )


@pytest.mark.parametrize("field", ["actions", "decisions", "metrics"])
def test_core_evidence_collections_cannot_be_empty(field: str) -> None:
    evidence = sample_evidence()
    with pytest.raises(ValidationError, match="project_requires"):
        ProjectEvidence.model_validate({**evidence.model_dump(), field: ()})


def test_story_depths_add_detail_in_order() -> None:
    evidence = sample_evidence()
    short = build_story(evidence, "two-minute")
    medium = build_story(evidence, "ten-minute")
    deep = build_story(evidence, "deep-dive")
    assert short.estimated_minutes == 2
    assert medium.estimated_minutes == 10
    assert deep.estimated_minutes == 20
    assert len(short.claims) < len(medium.claims) < len(deep.claims)
    assert tuple(claim.source for claim in short.claims) == (
        "situation",
        "task",
        "role",
        "action",
        "metric",
        "limitation",
    )


def test_team_metric_is_not_presented_as_individual_result() -> None:
    pack = build_story(sample_evidence(), "two-minute")
    metric = next(claim for claim in pack.claims if claim.source == "metric")
    assert "our team's measured result" in metric.text
    assert "my measured result" not in metric.text


def test_deep_dive_preserves_all_actions_decisions_and_metrics() -> None:
    evidence = sample_evidence()
    pack = build_story(evidence, "deep-dive")
    assert sum(claim.source == "action" for claim in pack.claims) == len(
        evidence.actions
    )
    assert sum(claim.source == "decision" for claim in pack.claims) == len(
        evidence.decisions
    )
    assert sum(claim.source == "metric" for claim in pack.claims) == len(
        evidence.metrics
    )


def test_review_passes_complete_synthetic_evidence() -> None:
    review = review_evidence(sample_evidence())
    assert review.gate == "ready_for_mock_interview"
    assert review.total_score == 12
    assert not review.gaps
    assert review.warnings == ("rubric_checks_presence_not_external_truth",)


def test_review_flags_ambiguous_personal_ownership() -> None:
    evidence = sample_evidence().model_copy(
        update={
            "role": "I designed the retrieval and evaluation components independently."
        }
    )
    review = review_evidence(evidence)
    assert review.ownership_score == 1
    assert review.gate == "revise"
    assert "separate_individual_and_team_ownership" in review.gaps


def test_story_build_is_deterministic() -> None:
    evidence = sample_evidence()
    assert build_story(evidence, "deep-dive") == build_story(evidence, "deep-dive")


@pytest.mark.parametrize("command", ["story", "review", "smoke"])
def test_cli_commands(command: str) -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "labs.week_24.demo", command],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    if command == "story":
        assert payload["depth"] == "two-minute"
    elif command == "review":
        assert payload["gate"] == "ready_for_mock_interview"
    else:
        assert payload == {"checks": 11, "depths": 3, "status": "ok"}
