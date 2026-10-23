"""Evidence for the Week 1 bank, Python checker and static grading engine."""

import asyncio
from collections import Counter
from collections.abc import Awaitable
import json
from pathlib import Path
import shutil
import subprocess
from typing import TypedDict, cast

import pytest

from assessment_runner import Check, Exercise, grade_submission


ROOT = Path(__file__).resolve().parents[1]


class Question(TypedDict, total=False):
    id: str
    type: str
    prompt: str
    reference: str
    starter: str
    checks: list[Check]
    snippet: str
    verification: dict[str, str]


class Bank(TypedDict):
    schema_version: int
    week: int
    version: str
    questions: list[Question]


BANK = cast(Bank, json.loads((ROOT / "assessments/week-01.json").read_text()))
CODING = [q for q in BANK["questions"] if q["type"] == "code"]


def exercise(question: Question) -> Exercise:
    return {"id": question["id"], "checks": question["checks"]}


def run[T](operation: Awaitable[T]) -> T:
    async def execute() -> T:
        return await operation

    return asyncio.run(execute())


def test_bank_count_distribution_and_unique_prompts() -> None:
    assert BANK["schema_version"] == 1
    assert BANK["week"] == 1
    assert len(BANK["questions"]) == 100
    assert Counter(q["type"] for q in BANK["questions"]) == {
        "single": 30,
        "multiple": 20,
        "match": 15,
        "short": 15,
        "code": 20,
    }
    assert len({q["id"] for q in BANK["questions"]}) == 100
    assert len({q["prompt"] for q in BANK["questions"]}) == 100
    assert [q["id"] for q in BANK["questions"]] == [
        f"W01-Q{i:03d}" for i in range(1, 101)
    ]


@pytest.mark.parametrize("question", CODING, ids=[q["id"] for q in CODING])
def test_reference_passes_all_five_checks(question: Question) -> None:
    result = run(grade_submission(question["reference"], exercise(question)))
    assert result["passed"] == result["total"] == 5, result
    assert len(result["results"]) == 5


@pytest.mark.parametrize("question", CODING, ids=[q["id"] for q in CODING])
def test_unimplemented_starter_does_not_pass(question: Question) -> None:
    compile(question["starter"], "starter.py", "exec")
    result = run(grade_submission(question["starter"], exercise(question)))
    assert result["passed"] < 5


MUTANTS = {
    "W01-Q081": 'def normalize_newlines(text):\n    return text.replace("\\r\\n", "\\n").replace("\\r", "\\n").strip()',
    "W01-Q082": 'def decode_utf8(content):\n    return content.decode("utf-8", errors="replace")',
    "W01-Q083": "def accepts_size(content, limit=1048576):\n    if limit <= 0: raise ValueError()\n    return len(content) < limit",
    "W01-Q084": 'def logical_lines(text):\n    return text.count("\\n") + 1',
    "W01-Q085": "def nonblank_lines(text):\n    for line in text.splitlines():\n        if line.strip(): yield line.strip()",
    "W01-Q086": "def safe_id(value):\n    return value.isalnum()",
    "W01-Q087": "from dataclasses import dataclass\n@dataclass(slots=True)\nclass DocumentInfo:\n    correlation_id: str\n    character_count: int",
    "W01-Q088": "def freeze_labels(labels):\n    return labels",
    "W01-Q089": 'def event_metadata(correlation_id, text, filename):\n    return {"correlation_id":correlation_id,"character_count":len(text),"line_count":len(text.splitlines()) or 1,"filename":filename}',
    "W01-Q090": 'async def read_utf8(reader):\n    return reader.read().decode("utf-8")',
    "W01-Q091": "def supported_upload(filename, declared_type, upload_type):\n    return declared_type == upload_type",
    "W01-Q092": "def error_status(code):\n    return 422",
    "W01-Q093": 'def decode_using(reader, content):\n    return content.decode("utf-8")',
    "W01-Q094": "def add_label(label, labels=None):\n    result = [] if labels is None else labels\n    result.append(label)\n    return result",
    "W01-Q095": "def first_or_default(values, default):\n    items = list(values)\n    return items[0] if items else default",
    "W01-Q096": 'class IntegerParseError(ValueError): pass\ndef parse_integer(text):\n    try: return int(text)\n    except ValueError: raise IntegerParseError("invalid integer")',
    "W01-Q097": 'def build_result(correlation_id, content):\n    text=content.decode("utf-8").replace("\\r\\n","\\n").replace("\\r","\\n").strip()\n    if not text: raise ValueError()\n    return {"correlation_id":correlation_id,"text":text,"character_count":len(text),"line_count":len(text.splitlines()) or 1}',
    "W01-Q098": 'def log_summary(logger, correlation_id, character_count):\n    logger.info("document_processed", extra={"correlation_id":correlation_id})',
    "W01-Q099": "def document_length(content: bytes) -> int:\n    return len(content)",
    "W01-Q100": "class TextService:\n    def __init__(self, reader): self.reader=reader\n    def extract(self, content): return self.reader.decode(content).strip()",
}


@pytest.mark.parametrize("question", CODING, ids=[q["id"] for q in CODING])
def test_plausible_wrong_solution_loses_marks(question: Question) -> None:
    if question["id"] == "W01-Q090":
        with pytest.warns(RuntimeWarning, match="never awaited"):
            result = run(grade_submission(MUTANTS[question["id"]], exercise(question)))
    else:
        result = run(grade_submission(MUTANTS[question["id"]], exercise(question)))
    assert result["passed"] < 5, result


def test_check_failure_is_partial_not_all_or_nothing() -> None:
    question = CODING[0]
    result = run(grade_submission(MUTANTS[question["id"]], exercise(question)))
    assert 0 < result["passed"] < 5


def test_syntax_failure_reports_five_named_failures() -> None:
    result = run(grade_submission("def broken(:", exercise(CODING[0])))
    assert result["passed"] == 0
    assert [x["label"] for x in result["results"]] == [
        x["label"] for x in CODING[0]["checks"]
    ]
    assert all("SyntaxError" in x["detail"] for x in result["results"])


def test_output_is_bounded_and_namespaces_do_not_leak() -> None:
    question = CODING[0]
    result = run(
        grade_submission(
            'print("x" * 10000)\n' + question["reference"], exercise(question)
        )
    )
    assert len(result["output"]) == 4000
    result = run(grade_submission("", exercise(question)))
    assert result["passed"] == 0


def test_oversized_source_is_rejected() -> None:
    with pytest.raises(ValueError, match="20,000"):
        run(grade_submission("x" * 20001, exercise(CODING[0])))


def test_runnable_output_questions_match_their_keys() -> None:
    for question in BANK["questions"]:
        if "verification" not in question:
            continue
        result = subprocess.run(
            [shutil.which("python") or "python", "-c", question["snippet"]],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert result.stdout == question["verification"]["stdout"], question["id"]


def test_javascript_bank_selection_scoring_and_restore() -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node 20+ is required for JavaScript assessment checks")
    result = subprocess.run(
        [node, "scripts/verify_assessment.mjs"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert "PASS:" in result.stdout
