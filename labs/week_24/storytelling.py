"""Build and inspect project stories using only declared evidence."""

from __future__ import annotations

from typing import Literal

from labs.week_24.models import (
    Depth,
    ProjectEvidence,
    ReviewGate,
    StoryClaim,
    StoryPack,
    StoryReview,
)


_MINUTES: dict[Depth, Literal[2, 10, 20]] = {
    "two-minute": 2,
    "ten-minute": 10,
    "deep-dive": 20,
}


def _core_claims(evidence: ProjectEvidence) -> list[StoryClaim]:
    metric = evidence.metrics[0]
    attribution = {
        "individual": "my measured result",
        "team": "our team's measured result",
        "organization": "the organization's measured result",
    }[metric.attribution]
    return [
        StoryClaim(source="situation", text=evidence.situation),
        StoryClaim(source="task", text=evidence.task),
        StoryClaim(source="role", text=evidence.role),
        StoryClaim(source="action", text=evidence.actions[0]),
        StoryClaim(
            source="metric",
            text=(
                f"{metric.name}: {metric.value}; describe this as {attribution}. "
                f"Evidence source: {metric.source}."
            ),
        ),
        StoryClaim(source="limitation", text=evidence.limitation),
    ]


def build_story(evidence: ProjectEvidence, depth: Depth) -> StoryPack:
    """Create a narrative scaffold without inventing facts or precision."""

    claims = _core_claims(evidence)
    if depth in {"ten-minute", "deep-dive"}:
        decision = evidence.decisions[0]
        claims.extend(
            (
                StoryClaim(
                    source="decision",
                    text=(
                        f"Decision: {decision.decision} Reason: {decision.reason} "
                        f"Rejected alternative: {decision.rejected_alternative} "
                        f"Consequence: {decision.consequence}"
                    ),
                ),
                StoryClaim(source="failure", text=evidence.failure),
                StoryClaim(
                    source="leadership",
                    text=(
                        f"{evidence.leadership.situation} "
                        f"{evidence.leadership.action} "
                        f"{evidence.leadership.result} "
                        f"Learning: {evidence.leadership.learning}"
                    ),
                ),
                StoryClaim(source="reflection", text=evidence.reflection),
            )
        )
    if depth == "deep-dive":
        claims.extend(
            StoryClaim(source="action", text=action) for action in evidence.actions[1:]
        )
        claims.extend(
            StoryClaim(
                source="decision",
                text=(
                    f"Decision: {decision.decision} Reason: {decision.reason} "
                    f"Rejected alternative: {decision.rejected_alternative} "
                    f"Consequence: {decision.consequence}"
                ),
            )
            for decision in evidence.decisions[1:]
        )
        claims.extend(
            StoryClaim(
                source="metric",
                text=(
                    f"{metric.name}: {metric.value}; attribution={metric.attribution}; "
                    f"evidence source: {metric.source}."
                ),
            )
            for metric in evidence.metrics[1:]
        )
    follow_up_questions = (
        "Which part did you personally own, and which part did the team own?",
        "How was each reported metric measured and what is its baseline?",
        "Which alternative did you reject and what evidence drove that choice?",
        "What failed, how did you detect it and what changed afterward?",
        "What limitation remains, and what would you do next with more time?",
    )
    return StoryPack(
        project_id=evidence.project_id,
        depth=depth,
        estimated_minutes=_MINUTES[depth],
        claims=tuple(claims),
        follow_up_questions=follow_up_questions,
        warnings=(
            "practice_scaffold_verify_every_claim_before_real_interview",
            "do_not_convert_team_or_organization_results_to_individual_claims",
        ),
    )


def review_evidence(evidence: ProjectEvidence) -> StoryReview:
    """Score explicit evidence categories; do not verify their truth externally."""

    structure_score = 2
    ownership_score = 2 if "team" in evidence.role.lower() else 1
    evidence_score = (
        2
        if len(evidence.metrics) >= 2
        and all(metric.source.strip() for metric in evidence.metrics)
        else 1
    )
    decision_score = 2 if len(evidence.decisions) >= 2 else 1
    failure_score = 2 if len(evidence.failure.strip()) >= 40 else 1
    reflection_score = 2 if len(evidence.reflection.strip()) >= 40 else 1
    total = (
        structure_score
        + ownership_score
        + evidence_score
        + decision_score
        + failure_score
        + reflection_score
    )
    gaps: list[str] = []
    if ownership_score < 2:
        gaps.append("separate_individual_and_team_ownership")
    if evidence_score < 2:
        gaps.append("add_a_second_sourced_metric")
    if decision_score < 2:
        gaps.append("add_a_second_decision_with_alternative")
    if failure_score < 2:
        gaps.append("expand_failure_detection_and_response")
    if reflection_score < 2:
        gaps.append("expand_learning_and_next_step")
    gate: ReviewGate = (
        "ready_for_mock_interview" if total >= 10 and ownership_score == 2 else "revise"
    )
    return StoryReview(
        gate=gate,
        structure_score=structure_score,
        ownership_score=ownership_score,
        evidence_score=evidence_score,
        decision_score=decision_score,
        failure_score=failure_score,
        reflection_score=reflection_score,
        total_score=total,
        gaps=tuple(gaps),
        warnings=("rubric_checks_presence_not_external_truth",),
    )
