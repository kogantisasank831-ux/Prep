"""Bind optional human/LLM ratings to exact saved case records; never invent ratings."""

from __future__ import annotations

from collections.abc import Sequence
import json
from pathlib import Path
from statistics import mean

from labs.week_09.dataset import EvaluationDataError, read_records, text

AXES = (
    "context_relevance",
    "answer_faithfulness",
    "answer_correctness",
    "citation_support",
)
RUBRIC_VERSION = "procurement-review/1.0.0"


def review_template(records: Sequence[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "query_id": record["query_id"],
            "run_id": record["run_id"],
            "record_digest": record["record_digest"],
            "rubric_version": RUBRIC_VERSION,
            "status": "pending",
            "reviewer_kind": None,
            "reviewer_id": None,
            "judge_prompt_version": None,
            "scores": {axis: None for axis in AXES},
            "rationale": None,
        }
        for record in records
    ]


def summarize_reviews(
    path: Path | None, records: Sequence[dict[str, object]]
) -> dict[str, object]:
    if path is None:
        return {
            "reviewed_count": 0,
            "pending_count": len(records),
            "groups": {},
            "note": "No human or LLM review was executed; null is not a passing score.",
        }
    by_id = {record["query_id"]: record for record in records}
    seen: set[tuple[str, str, str, str]] = set()
    reviewed_queries: set[str] = set()
    groups: dict[str, list[dict[str, int]]] = {}
    for item in read_records(path, limit=256, max_bytes=512 * 1024):
        if set(item) != {
            "query_id",
            "run_id",
            "record_digest",
            "rubric_version",
            "status",
            "reviewer_kind",
            "reviewer_id",
            "judge_prompt_version",
            "scores",
            "rationale",
        }:
            raise EvaluationDataError("unexpected review fields")
        query_id = text(item["query_id"], maximum=64)
        expected = by_id.get(query_id)
        if (
            expected is None
            or item["run_id"] != expected["run_id"]
            or item["record_digest"] != expected["record_digest"]
        ):
            raise EvaluationDataError(
                "review does not match this exact run and case record"
            )
        if item["rubric_version"] != RUBRIC_VERSION:
            raise EvaluationDataError("review rubric version mismatch")
        scores = item["scores"]
        if not isinstance(scores, dict) or set(scores) != set(AXES):
            raise EvaluationDataError("review must contain every rubric axis")
        if item["status"] == "pending":
            if any(value is not None for value in scores.values()) or any(
                item[key] is not None
                for key in (
                    "reviewer_kind",
                    "reviewer_id",
                    "judge_prompt_version",
                    "rationale",
                )
            ):
                raise EvaluationDataError(
                    "pending review cannot contain invented ratings or reviewer identity"
                )
            continue
        if item["status"] != "reviewed" or item["reviewer_kind"] not in (
            "human",
            "llm",
        ):
            raise EvaluationDataError(
                "completed review requires an explicit human or LLM reviewer"
            )
        kind = text(item["reviewer_kind"])
        reviewer = text(item["reviewer_id"], maximum=200)
        text(item["rationale"], maximum=4000)
        if kind == "llm":
            text(item["judge_prompt_version"], maximum=200)
        elif item["judge_prompt_version"] is not None:
            raise EvaluationDataError("human review must not claim a judge prompt")
        prompt_version = (
            text(item["judge_prompt_version"], maximum=200) if kind == "llm" else ""
        )
        key = (query_id, kind, reviewer, prompt_version)
        if key in seen:
            raise EvaluationDataError("duplicate reviewer rating for a case")
        seen.add(key)
        typed_scores: dict[str, int] = {}
        for axis in AXES:
            value = scores[axis]
            if type(value) is not int or not 1 <= value <= 5:
                raise EvaluationDataError("review ratings must be integers 1 to 5")
            typed_scores[axis] = value
        reviewed_queries.add(query_id)
        # Keep reviewers/models separate; do not blend human and model scores.
        group_name = kind + "/" + reviewer
        if kind == "llm":
            group_name = "llm/" + json.dumps(
                [reviewer, prompt_version], ensure_ascii=False, separators=(",", ":")
            )
        groups.setdefault(group_name, []).append(typed_scores)
    return {
        "reviewed_count": len(reviewed_queries),
        "pending_count": len(records) - len(reviewed_queries),
        "groups": {
            name: {
                "rating_count": len(rows),
                "mean_scores": {axis: mean(row[axis] for row in rows) for axis in AXES},
            }
            for name, rows in groups.items()
        },
        "note": "Imported self-declared ratings; identity is metadata, not authentication or independent verification.",
    }
