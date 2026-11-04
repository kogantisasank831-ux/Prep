"""Week 17 bank content, executable checks and coordination contracts."""

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


class Bank(TypedDict):
    schema_version: int
    week: int
    version: str
    code_language: str
    questions: list[Question]


BANK = cast(Bank, json.loads((ROOT / "assessments/week-17.json").read_text()))
CODING = [question for question in BANK["questions"] if question["type"] == "code"]
CODING_BY_ID = {question["id"]: question for question in CODING}
MUTANTS = {
    "W17-Q081": "def validate_handoff(envelope, expected_specialist, run_id, case_id):\n    return envelope['payload']\n",
    "W17-Q082": "def minimal_assignment(case, specialist):\n    return dict(case)\n",
    "W17-Q083": "def validate_result(result, expected_specialist, run_id, case_id):\n    return result['data']\n",
    "W17-Q084": "def plan_stages(requested):\n    return (tuple(requested),)\n",
    "W17-Q085": "def bounded_batches(roles, max_workers):\n    return (tuple(roles),)\n",
    "W17-Q086": "def collect_declared(declared, completed):\n    return tuple(completed.items())\n",
    "W17-Q087": "def failure_outcome(outcomes):\n    return {'status':'ready_for_commercial','report':None,'failure_reason':None}\n",
    "W17-Q088": "def commercial_recommendation(terms_found, threshold, variance, supplier_status, risk_level):\n    return 'no_review'\n",
    "W17-Q089": "def price_variance(current_price, reference_price):\n    return round((float(current_price)-float(reference_price))/float(reference_price)*100,2)\n",
    "W17-Q090": "def validate_sources(sources):\n    return tuple(sources)\n",
    "W17-Q091": "def correlate_findings(findings, run_id, case_id):\n    return tuple(row['data'] for row in findings)\n",
    "W17-Q092": "def build_evidence(findings):\n    return tuple(row['source']['source_id'] for row in findings)\n",
    "W17-Q093": "def sanitize_failure(controlled_code, exception_name):\n    return controlled_code or exception_name\n",
    "W17-Q094": "def build_report(run_id, case_id, recommendation, summary, evidence):\n    return {'run_id':run_id,'case_id':case_id,'recommendation':recommendation,'summary':summary,'evidence':evidence,'requires_human_approval':False}\n",
    "W17-Q095": "def compare_structures(supervisor, workflow):\n    return {'outcome_equal':supervisor['report']==workflow['report']}\n",
    "W17-Q096": "def choose_architecture(requirements):\n    return 'supervisor_specialists'\n",
    "W17-Q097": "def validate_registry(registry):\n    return tuple(registry)\n",
    "W17-Q098": "def retry_candidates(failures, max_attempts):\n    return tuple(row['specialist'] for row in failures)\n",
    "W17-Q099": "def trace_is_valid(trace):\n    return bool(trace)\n",
    "W17-Q100": "def audit_run(result):\n    return dict(result)\n",
}


def exercise(question: Question) -> Exercise:
    return {"id": question["id"], "checks": question["checks"]}


def test_bank_distribution_and_teaching_context() -> None:
    assert BANK["schema_version"] == 1
    assert BANK["week"] == 17
    assert BANK["version"] == "1.0.0"
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
        f"W17-Q{index:03d}" for index in range(1, 101)
    ]
    assert len({question["prompt"] for question in BANK["questions"]}) == 100
    assert all(len(question["explanation"]) > 30 for question in BANK["questions"])
    assert all(
        question["difficulty"] in {"foundation", "applied"}
        for question in BANK["questions"]
    )
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
        [node, "scripts/verify_assessment.mjs", "assessments/week-17.json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "1,000 balanced reproducible papers" in completed.stdout


def test_references_are_bounded_and_self_contained() -> None:
    permitted = {"copy", "decimal", "re"}
    for question in CODING:
        assert len(question["reference"]) <= 20_000
        tree = ast.parse(question["reference"])
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(alias.name in permitted for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                assert node.module in permitted and node.level == 0


def test_composed_coordination_contracts() -> None:
    selected = tuple(
        f"W17-Q{index:03d}"
        for index in (
            81,
            82,
            83,
            84,
            85,
            86,
            87,
            88,
            89,
            90,
            91,
            92,
            93,
            94,
            95,
            96,
            97,
            99,
            100,
        )
    )
    source = "\n".join(
        CODING_BY_ID[question_id]["reference"] for question_id in selected
    )
    checks: list[Check] = [
        {
            "label": "Minimal handoffs validate and correlate",
            "code": "case={'case_id':'c','purchase_order_id':'po','selected_supplier_id':'s',"
            "'sources':{'document':'d','sql':'q','supplier_risk':'r'}}\n"
            "assignment=minimal_assignment(case,'sql')\n"
            "envelope={'run_id':'run','case_id':'c','specialist':'sql','payload':assignment}\n"
            "payload=validate_handoff(envelope,'sql','run','c')\n"
            "result={'specialist':'sql','run_id':'run','case_id':'c','data':payload}\n"
            "assert validate_result(result,'sql','run','c')['selected_supplier_id']=='s'",
        },
        {
            "label": "Bounded wave collects in a stable valid trace",
            "code": "assert plan_stages(['commercial','sql','document','supplier_risk'])[0]=="
            "('document','sql','supplier_risk')\n"
            "assert bounded_batches(['document','sql','supplier_risk'],3)=="
            "(('document','sql','supplier_risk'),)\n"
            "completed={'supplier_risk':{'v':3},'sql':{'v':2},'document':{'v':1}}\n"
            "assert collect_declared(['document','sql','supplier_risk'],completed)[0][0]=='document'\n"
            "trace=['supervisor:start','supervisor:dispatch:document','supervisor:dispatch:sql',"
            "'supervisor:dispatch:supplier_risk','supervisor:complete:document',"
            "'supervisor:complete:sql','supervisor:complete:supplier_risk',"
            "'supervisor:dispatch:commercial','supervisor:complete:commercial',"
            "'supervisor:awaiting_approval']\nassert trace_is_valid(trace)",
        },
        {
            "label": "Exact evidence reaches an approval report",
            "code": "from decimal import Decimal\n"
            "assert price_variance(Decimal('110'),Decimal('100'))==Decimal('10.00')\n"
            "assert commercial_recommendation(True,Decimal('5'),Decimal('10'),"
            "'active','low')=='review_required'\n"
            "sources=[{'kind':'document','source_id':'d','digest':'a'*64},"
            "{'kind':'sql','source_id':'q','digest':'b'*64},"
            "{'kind':'risk_register','source_id':'r','digest':'c'*64}]\n"
            "assert validate_sources(sources)[0][0]=='document'\n"
            "findings=[{'specialist':'document','source':sources[0]},"
            "{'specialist':'sql','source':sources[1]},"
            "{'specialist':'supplier_risk','source':sources[2]}]\n"
            "evidence=list(build_evidence(findings))\n"
            "report=build_report('run','c','review_required','Human review.',evidence)\n"
            "assert report['requires_human_approval'] is True",
        },
        {
            "label": "Technical failure stays reportless and sanitized",
            "code": "rows=[{'specialist':'document','status':'ok','code':None},"
            "{'specialist':'sql','status':'technical_failure','code':'timeout'},"
            "{'specialist':'supplier_risk','status':'ok','code':None}]\n"
            "outcome=failure_outcome(rows);assert outcome['report'] is None\n"
            "assert sanitize_failure(None,'RuntimeError')=='unexpected_RuntimeError'\n"
            "result={'architecture':'supervisor_specialists','status':'failed',"
            "'report':None,'findings':[],'metrics':{'handoffs':3,'dependency_stages':1},"
            "'failure_reason':outcome['failure_reason']}\n"
            "assert audit_run(result)['has_report'] is False",
        },
        {
            "label": "Architecture selection and comparison stay evidence bounded",
            "code": "requirements={'distinct_context':True,'separate_governance':True,"
            "'independent_work':True,'coordination_cost_justified':True}\n"
            "assert choose_architecture(requirements)=='supervisor_specialists'\n"
            "fn=lambda value=None:value\n"
            "assert validate_registry({role:fn for role in "
            "('document','sql','supplier_risk','commercial')})[-1]=='commercial'\n"
            "report={'recommendation':'review_required'}\n"
            "compared=compare_structures({'report':report,'handoffs':4,'dependency_stages':2},"
            "{'report':dict(report),'handoffs':0,'dependency_stages':4})\n"
            "assert compared['outcome_equal'] and compared['measured_latency_ms'] is None",
        },
    ]
    result = asyncio.run(
        grade_submission(source, {"id": "coordination-contracts", "checks": checks})
    )
    assert result["passed"] == 5, result
