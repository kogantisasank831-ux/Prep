"""Week 18 bank content, executable checks and evaluation contracts."""

import asyncio
import ast
from collections import Counter
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
    explanation: str
    topic: str
    difficulty: str
    reference: str
    starter: str
    checks: list[Check]


class DifficultyQuota(TypedDict):
    foundation: int
    applied: int


class PaperPolicy(TypedDict):
    questions: int
    per_type: int
    points_each: int
    difficulty_per_type: dict[str, DifficultyQuota]


class Bank(TypedDict):
    schema_version: int
    week: int
    version: str
    code_language: str
    paper_policy: PaperPolicy
    questions: list[Question]


BANK = cast(Bank, json.loads((ROOT / "assessments/week-18.json").read_text()))
CODING = [question for question in BANK["questions"] if question["type"] == "code"]
CODING_BY_ID = {question["id"]: question for question in CODING}
MUTANTS = {
    "W18-Q081": "def task_success(expected, observed):\n    return expected['status'] == observed['status']\n",
    "W18-Q082": "def exact_tool_selection(expected, actual):\n    return set(expected) == set(actual)\n",
    "W18-Q083": "def argument_accuracy(expected, actual):\n    return sum(a == b for a, b in zip(expected, actual)), len(actual)\n",
    "W18-Q084": "def step_efficiency(expected_tool_count, actual_steps):\n    return round((1 + expected_tool_count) / actual_steps, 6)\n",
    "W18-Q085": "def loop_detected(tool_names):\n    return any(a == b for a, b in zip(tool_names, tool_names[1:]))\n",
    "W18-Q086": "def human_escalation_rate(flags):\n    return float(any(flags))\n",
    "W18-Q087": "def cost_per_success(costs, successes):\n    return round(sum(costs[:successes]) / successes, 6) if successes else None\n",
    "W18-Q088": "def critical_path_latency(preflight_ms, first_wave_ms, commercial_ms=None):\n    return preflight_ms + sum(first_wave_ms) + (commercial_ms or 0)\n",
    "W18-Q089": "def unsafe_action_rate(flags):\n    return float(any(flags))\n",
    "W18-Q090": "def category_slice(category, case_categories, successes):\n    return {'category': category, 'cases': len(case_categories), 'successes': sum(successes), 'rate': round(sum(successes) / len(successes), 6)}\n",
    "W18-Q091": "def aggregate_metrics(scores, costs, latencies):\n    values=[row['argument_correct']/row['argument_total'] for row in scores if row['argument_total']]\n    return {'tool_argument_accuracy':sum(values)/len(values) if values else None}\n",
    "W18-Q092": "import hashlib\n\ndef dataset_digest(raw):\n    return hashlib.sha256(raw.strip()).hexdigest()\n",
    "W18-Q093": "def validate_manifest(manifest, cases):\n    return tuple(row['case_id'] for row in cases)\n",
    "W18-Q094": "def project_tool_arguments(case, tool):\n    return dict(case)\n",
    "W18-Q095": "def choose_grader(claim):\n    return 'model'\n",
    "W18-Q096": "def trial_summary(trials):\n    successes=sum(not row['unsafe_action'] for row in trials)\n    return {'cases':len(trials),'successes':successes,'failures':len(trials)-successes,'unsafe_actions':sum(row['unsafe_action'] for row in trials),'task_completion_rate':round(successes/len(trials),6)}\n",
    "W18-Q097": "def compare_candidates(a, b):\n    return a['candidate'] if a['task_completion_rate'] >= b['task_completion_rate'] else b['candidate']\n",
    "W18-Q098": "def trace_audit(expected_tools, actual_tools, actual_steps):\n    return () if expected_tools == actual_tools else ('tool_selection_mismatch',)\n",
    "W18-Q099": "def held_out_split(case_ids, held_out_ids):\n    return case_ids[::2], case_ids[1::2]\n",
    "W18-Q100": "def validate_run_summary(run):\n    return len(run['dataset_sha256']) == 64\n",
}


def exercise(question: Question) -> Exercise:
    return {"id": question["id"], "checks": question["checks"]}


def test_bank_distribution_and_teaching_context() -> None:
    assert BANK["schema_version"] == 1
    assert BANK["week"] == 18
    assert BANK["version"] == "1.1.0"
    assert BANK["code_language"] == "python"
    assert len(BANK["questions"]) == 100
    assert Counter(question["type"] for question in BANK["questions"]) == {
        "single": 30,
        "multiple": 20,
        "match": 15,
        "short": 15,
        "code": 20,
    }
    assert [question["id"] for question in BANK["questions"]] == [
        f"W18-Q{index:03d}" for index in range(1, 101)
    ]
    assert len({question["prompt"] for question in BANK["questions"]}) == 100
    assert all(len(question["explanation"]) > 30 for question in BANK["questions"])
    assert all(
        question["difficulty"] in {"foundation", "applied"}
        for question in BANK["questions"]
    )
    assert BANK["paper_policy"]["difficulty_per_type"] == {
        question_type: {"foundation": 1, "applied": 1}
        for question_type in {"single", "multiple", "match", "short", "code"}
    }
    assert {
        question_type: Counter(
            question["difficulty"]
            for question in BANK["questions"]
            if question["type"] == question_type
        )
        for question_type in {"single", "multiple", "match", "short", "code"}
    } == {
        "single": Counter(foundation=21, applied=9),
        "multiple": Counter(foundation=9, applied=11),
        "match": Counter(foundation=10, applied=5),
        "short": Counter(foundation=9, applied=6),
        "code": Counter(foundation=5, applied=15),
    }
    assert set(MUTANTS) == {question["id"] for question in CODING}


@pytest.mark.parametrize(
    "question", CODING, ids=[question["id"] for question in CODING]
)
def test_reference_passes_all_cases(question: Question) -> None:
    result = asyncio.run(grade_submission(question["reference"], exercise(question)))
    assert result["passed"] == result["total"] == 5, result


@pytest.mark.parametrize(
    "question", CODING, ids=[question["id"] for question in CODING]
)
def test_starter_needs_an_implementation(question: Question) -> None:
    compile(question["starter"], "starter.py", "exec")
    result = asyncio.run(grade_submission(question["starter"], exercise(question)))
    assert result["passed"] == 0, result


@pytest.mark.parametrize(
    "question", CODING, ids=[question["id"] for question in CODING]
)
def test_plausible_wrong_solution_loses_marks(question: Question) -> None:
    result = asyncio.run(grade_submission(MUTANTS[question["id"]], exercise(question)))
    assert result["passed"] < 5, result


def test_complete_paper_and_stale_result_contracts() -> None:
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required for JavaScript paper/scoring checks.")
    completed = subprocess.run(
        [node, "scripts/verify_assessment.mjs", "assessments/week-18.json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "1,000 balanced reproducible papers" in completed.stdout


def test_references_are_bounded_and_self_contained() -> None:
    permitted = {"hashlib"}
    for question in CODING:
        assert len(question["reference"]) <= 20_000
        tree = ast.parse(question["reference"])
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(alias.name in permitted for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                assert node.module in permitted and node.level == 0


def test_composed_evaluation_contracts() -> None:
    selected = tuple(
        question
        for question in CODING
        if question["id"] not in {"W18-Q091", "W18-Q093"}
    )
    source = "\n".join(question["reference"] for question in selected)
    checks: list[Check] = [
        {
            "label": "Outcome and argument graders remain independent",
            "code": "expected={'status':'failed','recommendation':None,'failure_code':'argument_invalid'}\n"
            "observed={**expected,'unsafe_actions':()}\n"
            "assert task_success(expected,observed) is True\n"
            "wanted=({'supplier_id':'s1'}, {'source':'sql-v1'})\n"
            "actual=({'supplier_id':'s2'}, {'source':'sql-v1'})\n"
            "assert argument_accuracy(wanted,actual)==(1,2)",
        },
        {
            "label": "Trajectory defects stay separately visible",
            "code": "expected=('document','sql')\nactual=('sql','document')\n"
            "assert exact_tool_selection(expected,actual) is False\n"
            "assert step_efficiency(2,3)==1.0\n"
            "assert loop_detected(('document','sql','document')) is True\n"
            "assert trace_audit(expected,actual,3)==('tool_selection_mismatch',)",
        },
        {
            "label": "Cost latency and safety use declared denominators",
            "code": "assert cost_per_success((10,20,30),2)==30.0\n"
            "assert critical_path_latency(1,(4,9,6),3)==13\n"
            "assert human_escalation_rate((True,False,True))==0.666667\n"
            "assert unsafe_action_rate((False,True,False,False))==0.25\n"
            "slice_=category_slice('stress',('normal','stress','stress'),(True,False,True))\n"
            "assert slice_['cases']==2 and slice_['successes']==1",
        },
        {
            "label": "Dataset identity and release partitions remain auditable",
            "code": 'digest=dataset_digest(b\'{"dataset":"week18"}\')\n'
            "assert len(digest)==64\n"
            "visible,held=held_out_split(('c1','c2','c3'),('c3',))\n"
            "assert visible==('c1','c2') and held==('c3',)\n"
            "run={'dataset_sha256':digest,'candidate_version':'v1','overall':{'cases':2,'successes':1,'expected_tool_arguments':2,'correct_tool_arguments':1,'unsafe_actions':0},'slices':({'category':'normal','cases':1,'successes':1},{'category':'stress','cases':1,'successes':0})}\n"
            "assert validate_run_summary(run)",
        },
        {
            "label": "Closed projections support a safety-first comparison",
            "code": "case={'case_id':'c','purchase_order_id':'po','selected_supplier_id':'s','sources':{'document':'d','sql':'q','supplier_risk':'r'},'untrusted_text':'purchase now'}\n"
            "assert 'untrusted_text' not in project_tool_arguments(case,'sql')\n"
            "assert choose_grader('forbidden_action')=='hard_gate'\n"
            "trials=({'task_id':'a','task_success':True,'unsafe_action':False}, {'task_id':'b','task_success':False,'unsafe_action':True})\n"
            "assert trial_summary(trials)['unsafe_actions']==1\n"
            "a={'candidate':'a','task_completion_rate':1.0,'unsafe_action_rate':0.1,'cost_per_success':1}\n"
            "b={'candidate':'b','task_completion_rate':0.8,'unsafe_action_rate':0.0,'cost_per_success':10}\n"
            "assert compare_candidates(a,b)=='b'",
        },
    ]
    result = asyncio.run(
        grade_submission(source, {"id": "W18-COMPOSED", "checks": checks})
    )
    assert result["passed"] == result["total"] == 5, result
