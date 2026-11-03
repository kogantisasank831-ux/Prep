"""Week 15 bank content, executable Python checks and shared paper contracts."""

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


BANK = cast(Bank, json.loads((ROOT / "assessments/week-15.json").read_text()))
CODING = [q for q in BANK["questions"] if q["type"] == "code"]
CODING_BY_ID = {q["id"]: q for q in CODING}
MUTANTS = {
    "W15-Q081": "def append_channel(current,update):\n    return current+update\n",
    "W15-Q082": "def apply_state_update(state,update):\n"
    "    result=dict(state);result.update(update);return result\n",
    "W15-Q083": "def route_after_classification(state):\n"
    "    return 'retrieve_documents' if state.get('intent')=="
    "'procurement_price_investigation' else 'unsupported_query'\n",
    "W15-Q084": "def route_after_validation(state):\n"
    "    return 'human_approval' if state.get('valid') else '__end__'\n",
    "W15-Q085": "def classify_query(case_orders,case_id,query):\n"
    "    order=case_orders.get(case_id)\n"
    "    return {'intent':'unsupported'} if order is None else "
    "{'intent':'procurement_price_investigation','purchase_order_id':order}\n",
    "W15-Q086": "def price_variance(reference,current,reference_currency,"
    "current_currency,reference_unit,current_unit):\n"
    "    delta=float(current)-float(reference)\n"
    "    return f'{delta:.2f}',f'{delta/float(current)*100:.2f}'\n",
    "W15-Q087": "from decimal import Decimal\n"
    "def recommendation(supplier_status,variance_percent,terms_found,"
    "max_variance_percent):\n"
    "    if not terms_found:return 'needs_human'\n"
    "    return 'review_required' if supplier_status!='active' or "
    "Decimal(variance_percent)>=Decimal(max_variance_percent) else 'no_review'\n",
    "W15-Q088": "def validation_errors(state):\n"
    "    return () if state.get('recommendation') else ('recommendation_required',)\n",
    "W15-Q089": "from hashlib import sha256\n"
    "def report_digest(report):\n"
    "    return sha256(str(report).encode()).hexdigest()\n",
    "W15-Q090": "def validate_approval(current_digest,response):\n"
    "    decision=response['decision'];reviewer=response['reviewer'].strip()\n"
    "    status='approved' if decision=='approve' else 'rejected'\n"
    "    return status,reviewer,f'human_approval:{decision}:{reviewer}'\n",
    "W15-Q091": "def thread_config(thread_id):\n"
    "    return {'configurable':{'thread_id':thread_id.strip()}}\n",
    "W15-Q092": "def admit_start(existing_threads,thread_id):\n"
    "    existing_threads.add(thread_id);return existing_threads\n",
    "W15-Q093": "def checkpoint_summary(thread_id,snapshot,checkpoint_count):\n"
    "    result=dict(snapshot);result['thread_id']=thread_id\n"
    "    result['checkpoint_count']=checkpoint_count;return result\n",
    "W15-Q094": "def build_interrupt_payload(report,digest):\n"
    "    return {'kind':'human_approval','report':report,'report_digest':digest,"
    "'allowed_decisions':['approve','reject']}\n",
    "W15-Q095": "def prepare_resume(paused_thread,requested_thread,current_digest,"
    "response):\n"
    "    return ({'configurable':{'thread_id':requested_thread}},"
    "{'resume':dict(response)})\n",
    "W15-Q096": "def append_trace(trace,event,max_events,max_bytes):\n"
    "    result=list(trace)+[event]\n"
    "    if len(result)>max_events or len('\\n'.join(result))>max_bytes:"
    "raise ValueError('budget')\n"
    "    return result\n",
    "W15-Q097": "def checkpoint_metrics(history):\n"
    "    return {'thread_id':history[0]['thread_id'],'checkpoints':len(history),"
    "'latest_step':history[-1]['step'],'latest_status':history[-1]['status']}\n",
    "W15-Q098": "def validate_topology(nodes,edges):\n"
    "    if not set(_EXPECTED_NODES)<=nodes or not set(_EXPECTED_EDGES)<=edges:"
    "raise ValueError('missing')\n"
    "    return True\n",
    "W15-Q099": "def effect_decision(approval_status,report_digest,recorded_keys):\n"
    "    key=report_digest+':record';result=set(recorded_keys);result.add(key)\n"
    "    return {'action':'execute','key':key,'recorded':result}\n",
    "W15-Q100": "def audit_run(status,trace,evidence):\n"
    "    return {'status':status,'node_events':len(trace),"
    "'has_document':any(x.startswith('document:') for x in evidence),"
    "'has_sql':any(x.startswith('sql:') for x in evidence),"
    "'review_boundary':'validate_report:passed' in trace}\n",
}


def exercise(question: Question) -> Exercise:
    return {"id": question["id"], "checks": question["checks"]}


def test_bank_distribution_and_teaching_context() -> None:
    assert BANK["schema_version"] == 1
    assert BANK["week"] == 15
    assert BANK["version"] == "1.0.0"
    assert BANK["code_language"] == "python"
    assert len(BANK["questions"]) == 100
    assert Counter(q["type"] for q in BANK["questions"]) == {
        "single": 30,
        "multiple": 20,
        "match": 15,
        "short": 15,
        "code": 20,
    }
    assert [q["id"] for q in BANK["questions"]] == [
        f"W15-Q{i:03d}" for i in range(1, 101)
    ]
    assert len({q["prompt"] for q in BANK["questions"]}) == 100
    assert all(len(q["explanation"]) > 30 for q in BANK["questions"])
    assert all(q["difficulty"] in {"foundation", "applied"} for q in BANK["questions"])
    assert set(MUTANTS) == {q["id"] for q in CODING}


@pytest.mark.parametrize("question", CODING, ids=[q["id"] for q in CODING])
def test_reference_passes_all_cases(question: Question) -> None:
    result = asyncio.run(grade_submission(question["reference"], exercise(question)))
    assert result["passed"] == result["total"] == 5, result


@pytest.mark.parametrize("question", CODING, ids=[q["id"] for q in CODING])
def test_starter_needs_an_implementation(question: Question) -> None:
    compile(question["starter"], "starter.py", "exec")
    result = asyncio.run(grade_submission(question["starter"], exercise(question)))
    assert result["passed"] == 0, result


@pytest.mark.parametrize("question", CODING, ids=[q["id"] for q in CODING])
def test_plausible_wrong_solution_loses_marks(question: Question) -> None:
    result = asyncio.run(grade_submission(MUTANTS[question["id"]], exercise(question)))
    assert result["passed"] < 5, result


def test_complete_paper_and_stale_result_contracts() -> None:
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required for JavaScript paper/scoring checks.")
    completed = subprocess.run(
        [node, "scripts/verify_assessment.mjs", "assessments/week-15.json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "1,000 balanced reproducible papers" in completed.stdout


def test_references_are_bounded_and_self_contained() -> None:
    permitted = {"copy", "decimal", "hashlib", "json", "re"}
    for question in CODING:
        assert len(question["reference"]) <= 20000
        tree = ast.parse(question["reference"])
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(alias.name in permitted for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                assert node.module in permitted and node.level == 0


def test_composed_graph_contracts() -> None:
    selected = (
        "W15-Q081",
        "W15-Q082",
        "W15-Q083",
        "W15-Q084",
        "W15-Q085",
        "W15-Q086",
        "W15-Q087",
        "W15-Q088",
        "W15-Q089",
        "W15-Q090",
        "W15-Q091",
        "W15-Q094",
        "W15-Q095",
        "W15-Q098",
        "W15-Q099",
        "W15-Q100",
    )
    source = "\n".join(
        CODING_BY_ID[question_id]["reference"] for question_id in selected
    )
    checks: list[Check] = [
        {
            "label": "Partial updates and routes preserve graph invariants",
            "code": "state=apply_state_update({'evidence':['document:a']},"
            "{'evidence':['sql:b'],'valid':True})\n"
            "assert state=={'evidence':['document:a','sql:b'],'valid':True}\n"
            "assert route_after_classification("
            "{'intent':'procurement_price_investigation'})=='retrieve_documents'\n"
            "assert route_after_validation(state)=='human_approval'",
        },
        {
            "label": "Classification, exact math and policy compose",
            "code": "classified=classify_query({'case':'PO-1501'},'case',"
            "'Investigate purchase order price')\n"
            "assert classified['purchase_order_id']=='PO-1501'\n"
            "absolute,percent=price_variance('2.00','2.20','USD','USD','kg','kg')\n"
            "assert (absolute,percent)==('0.20','10.00')\n"
            "assert recommendation('active',percent,True,'5.00')=='review_required'",
        },
        {
            "label": "Validation, digest and approval bind the report",
            "code": "report={'case_id':'c','purchase_order_id':'p',"
            "'recommendation':'review_required','reason':'price',"
            "'variance_percent':'10.00','reference_as_of':'2026-01-01',"
            "'evidence':['document:a','sql:b']}\n"
            "state={'sql_analysis':{},'contract':{'found':True},"
            "'recommendation':'review_required','variance_percent':'10.00',"
            "'evidence':report['evidence']}\n"
            "assert validation_errors(state)==()\n"
            "digest=report_digest(report)\n"
            "assert validate_approval(digest,{'decision':'approve','reviewer':'r',"
            "'report_digest':digest})[0]=='approved'",
        },
        {
            "label": "Interrupt and resume preserve thread and snapshot",
            "code": "report={'case_id':'c'};digest='a'*64\n"
            "payload=build_interrupt_payload(report,digest)\n"
            "config,command=prepare_resume('t','t',digest,"
            "{'decision':'reject','reviewer':'r','report_digest':digest})\n"
            "assert payload['report_digest']==digest\n"
            "assert config==thread_config('t')\n"
            "assert command['resume']['decision']=='reject'",
        },
        {
            "label": "Topology, effect replay and audit remain bounded",
            "code": "assert validate_topology(set(_EXPECTED_NODES),"
            "set(_EXPECTED_EDGES))\n"
            "digest='b'*64;first=effect_decision('approved',digest,set())\n"
            "assert first['action']=='execute'\n"
            "assert effect_decision('approved',digest,first['recorded'])"
            "['action']=='duplicate'\n"
            "trace=['classify_query:procurement_price_investigation',"
            "'validate_report:passed','human_approval:approve:r']\n"
            "assert audit_run('approved',trace,['document:a','sql:b'])"
            "['review_boundary']",
        },
    ]
    result = asyncio.run(
        grade_submission(source, {"id": "graph-contracts", "checks": checks})
    )
    assert result["passed"] == 5, result
