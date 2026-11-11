"""Candidate Week 21–30 bank, executable-code and page contracts."""

from __future__ import annotations

import ast
import asyncio
from collections import Counter
import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import TypedDict, cast

import pytest

from assessment_runner import Check, Exercise, grade_submission
from scripts.build_candidate_assessments import build_bank


ROOT = Path(__file__).resolve().parents[1]
WEEKS = tuple(range(21, 31))


class Question(TypedDict, total=False):
    id: str
    type: str
    prompt: str
    explanation: str
    topic: str
    difficulty: str
    reference: str
    starter: str
    checks: list[Check]


class Bank(TypedDict):
    schema_version: int
    week: int
    version: str
    code_language: str
    questions: list[Question]


BANKS: dict[int, Bank] = {
    week: cast(
        Bank,
        json.loads((ROOT / f"assessments/week-{week:02d}.json").read_text()),
    )
    for week in WEEKS
}
CODING = [
    (week, question)
    for week, bank in BANKS.items()
    for question in bank["questions"]
    if question["type"] == "code"
]


def _exercise(question: Question) -> Exercise:
    return {"id": question["id"], "checks": question["checks"]}


@pytest.mark.parametrize("week", WEEKS)
def test_bank_distribution_and_teaching_context(week: int) -> None:
    bank = BANKS[week]
    assert bank["schema_version"] == 1
    assert bank["week"] == week
    assert bank["version"] == "1.0.0"
    assert bank["code_language"] == "python"
    assert len(bank["questions"]) == 100
    assert Counter(question["type"] for question in bank["questions"]) == {
        "single": 30,
        "multiple": 20,
        "match": 15,
        "short": 15,
        "code": 20,
    }
    assert [question["id"] for question in bank["questions"]] == [
        f"W{week:02d}-Q{index:03d}" for index in range(1, 101)
    ]
    assert len({question["prompt"] for question in bank["questions"]}) == 100
    assert all(len(question["explanation"]) > 30 for question in bank["questions"])
    assert Counter(question["difficulty"] for question in bank["questions"]) == {
        "foundation": 44,
        "applied": 56,
    }


@pytest.mark.parametrize("week", WEEKS)
def test_checked_in_bank_matches_deterministic_builder(week: int) -> None:
    assert BANKS[week] == build_bank(week)


@pytest.mark.parametrize(
    ("week", "question"),
    CODING,
    ids=[question["id"] for _, question in CODING],
)
def test_reference_passes_all_cases(week: int, question: Question) -> None:
    del week
    result = asyncio.run(grade_submission(question["reference"], _exercise(question)))
    assert result["passed"] == result["total"] == 5, result


@pytest.mark.parametrize(
    ("week", "question"),
    CODING,
    ids=[question["id"] for _, question in CODING],
)
def test_starter_and_simple_wrong_solution_lose_marks(
    week: int, question: Question
) -> None:
    del week
    compile(question["starter"], "starter.py", "exec")
    starter = asyncio.run(grade_submission(question["starter"], _exercise(question)))
    assert starter["passed"] == 0, starter
    tree = ast.parse(question["reference"])
    function = cast(ast.FunctionDef, tree.body[0]).name
    wrong = f"def {function}(*args, **kwargs):\n    return None\n"
    mutant = asyncio.run(grade_submission(wrong, _exercise(question)))
    assert mutant["passed"] < 5, mutant


@pytest.mark.parametrize("week", WEEKS)
def test_shared_browser_engine_contract(week: int) -> None:
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required for JavaScript paper/scoring checks.")
    completed = subprocess.run(
        [node, "scripts/verify_assessment.mjs", f"assessments/week-{week:02d}.json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "1,000 balanced reproducible papers" in completed.stdout


@pytest.mark.parametrize("week", WEEKS)
def test_page_and_lesson_links_are_candidate_only(week: int) -> None:
    page = (ROOT / f"assessments/week-{week:02d}.html").read_text()
    production = (ROOT / f"content/weeks/week-{week:02d}.md").read_text()
    beginner = (ROOT / f"content/weeks/week-{week:02d}-beginner.md").read_text()
    assert f"/assessments/week-{week:02d}.json" in page
    assert page.count('id="assessment-app"') == 1
    assert f"/assessments/week-{week:02d}/" in production
    assert f"/assessments/week-{week:02d}/" in beginner
    assert "status: review" in page
    assert "status: review" in production
    assert "status: review" in beginner


def test_candidate_weeks_are_not_published_before_approval() -> None:
    shell = (ROOT / "shell.js").read_text()
    match = re.search(r"window\.PUBLISHED_WEEKS = new Set\(\[([^]]+)\]\)", shell)
    assert match is not None
    published = {int(value.strip()) for value in match.group(1).split(",")}
    assert published == set(range(1, 21))
