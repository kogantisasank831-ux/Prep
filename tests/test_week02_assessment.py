"""Week 2 content contracts and reuse of the static paper/scoring engine."""

from collections import Counter
import json
from pathlib import Path
import shutil
import subprocess
from typing import TypedDict, cast

import pytest

ROOT = Path(__file__).resolve().parents[1]


class Check(TypedDict):
    label: str
    fixture: str
    columns: list[str]
    rows: list[list[str | int | float | bool | None]]


class Question(TypedDict, total=False):
    id: str
    type: str
    prompt: str
    explanation: str
    topic: str
    difficulty: str
    starter: str
    reference: str
    checks: list[Check]


class Bank(TypedDict):
    schema_version: int
    week: int
    version: str
    code_language: str
    sql_schema: str
    sql_fixtures: dict[str, str]
    questions: list[Question]


BANK = cast(Bank, json.loads((ROOT / "assessments/week-02.json").read_text()))
CODING = [q for q in BANK["questions"] if q["type"] == "code"]


def test_bank_distribution_and_unique_content() -> None:
    assert BANK["schema_version"] == 1
    assert BANK["week"] == 2
    assert BANK["version"] == "1.0.0"
    assert BANK["code_language"] == "sql"
    assert len(BANK["questions"]) == 100
    assert Counter(q["type"] for q in BANK["questions"]) == {
        "single": 30,
        "multiple": 20,
        "match": 15,
        "short": 15,
        "code": 20,
    }
    assert [q["id"] for q in BANK["questions"]] == [
        f"W02-Q{i:03d}" for i in range(1, 101)
    ]
    assert len({q["prompt"] for q in BANK["questions"]}) == 100
    assert all(len(q["explanation"]) > 30 for q in BANK["questions"])
    assert all(q["difficulty"] in {"foundation", "applied"} for q in BANK["questions"])


@pytest.mark.parametrize("question", CODING, ids=[q["id"] for q in CODING])
def test_sql_exercises_declare_five_result_cases(question: Question) -> None:
    checks = question["checks"]
    assert len(checks) == 5
    assert {check["fixture"] for check in checks} == set(BANK["sql_fixtures"])
    assert len({check["label"] for check in checks}) == 5
    assert question["reference"].lstrip().upper().startswith(("SELECT", "WITH"))
    assert question["starter"].startswith("--")
    assert (
        "ordered by" in question["prompt"].lower()
        or "order" in question["prompt"].lower()
    )
    for check in checks:
        assert check["columns"]
        assert all(len(row) == len(check["columns"]) for row in check["rows"])


def test_independent_procurement_arithmetic_anchors() -> None:
    by_id = {q["id"]: q for q in CODING}

    def rows(
        qid: str, fixture: str = "example"
    ) -> list[list[str | int | float | bool | None]]:
        return next(c["rows"] for c in by_id[qid]["checks"] if c["fixture"] == fixture)

    assert next(r[1] for r in rows("W02-Q084") if r[0] == 11) == "870"
    assert [11, "130"] in rows("W02-Q085")
    assert ["USD", "1610"] in rows("W02-Q098")  # 130*12 + (50-45)*10
    assert [11, None] in rows("W02-Q100")  # July receipt cannot complete June.
    assert [1001, None] in rows("W02-Q094", "boundaries")  # Zero denominator.
    assert [2001, None] in rows("W02-Q099", "sparse")  # EUR/kg != USD/kg.
    assert ["copper", "8"] in rows("W02-Q089")  # Latest is not MAX(price).
    assert [31, 2, 1] in rows("W02-Q092", "ties")
    assert [32, 2, 1] in rows("W02-Q092", "ties")


def test_balanced_papers_scoring_and_restoration() -> None:
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required for the JavaScript engine checks.")
    result = subprocess.run(
        [node, "scripts/verify_assessment.mjs", "assessments/week-02.json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "1,000 balanced reproducible papers" in result.stdout
