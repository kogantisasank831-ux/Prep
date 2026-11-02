"""Week 14 bank content, actual Python checks and shared paper contracts."""

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


BANK = cast(Bank, json.loads((ROOT / "assessments/week-14.json").read_text()))
CODING = [q for q in BANK["questions"] if q["type"] == "code"]
CODING_BY_ID = {q["id"]: q for q in CODING}
MUTANTS = {
    "W14-Q081": "def parse_action(value):\n"
    "    return value.strip().lower() if isinstance(value,str) else None\n",
    "W14-Q082": "ROUTE=('load_order','lookup_supplier','get_reference_price',"
    "'calculate_variance','search_contract_terms')\n"
    "def workflow_next(completed):\n"
    "    for action in ROUTE:\n"
    "        if action not in completed:return action\n"
    "    return 'finish'\n",
    "W14-Q083": "def proposal_decision(raw_action,completed,ready):\n"
    "    if raw_action=='finish':return 'finish'\n"
    "    return 'duplicate' if raw_action in completed else 'execute'\n",
    "W14-Q084": "def prerequisite_ok(action,state):\n"
    "    return action=='load_order' or state.get('order',False)\n",
    "W14-Q085": "ACTION_SLOT={'load_order':'order','lookup_supplier':'supplier',"
    "'get_reference_price':'reference','calculate_variance':'variance',"
    "'search_contract_terms':'contract'}\n"
    "def apply_observation(state,action,fact):\n"
    "    state[ACTION_SLOT[action]]=fact['value']\n"
    "    state['completed']=state['completed']|{action}\n"
    "    return state\n",
    "W14-Q086": "def ready_for_report(state):\n    return all(state.values())\n",
    "W14-Q087": "def recommendation(supplier_status,variance_percent,"
    "terms_found,max_variance_percent):\n"
    "    if not terms_found:return 'needs_human'\n"
    "    return 'review_required' if supplier_status!='active' or "
    "float(variance_percent)>=float(max_variance_percent) else 'no_review'\n",
    "W14-Q088": "def price_variance(reference,current,reference_currency,"
    "current_currency,reference_unit,current_unit):\n"
    "    delta=float(current)-float(reference)\n"
    "    return f'{delta:.2f}',f'{delta/float(current)*100:.2f}'\n",
    "W14-Q089": "def bounded_agent(choices,max_steps=8):\n"
    "    completed=[];tools=0\n"
    "    for raw in choices[:max_steps]:\n"
    "        if raw=='finish':return {'status':'awaiting_approval',"
    "'model_calls':1,'tool_calls':tools,'completed':tuple(completed),"
    "'failure_reason':None}\n"
    "        tools+=1;completed.append(raw)\n"
    "    return {'status':'failed','model_calls':len(choices[:max_steps]),"
    "'tool_calls':tools,'completed':tuple(completed),"
    "'failure_reason':'step_budget_exhausted'}\n",
    "W14-Q090": "from decimal import Decimal\n"
    "def planner_usage(observed_counts,had_errors,input_price_per_million='1.00',"
    "output_price_per_million='3.00'):\n"
    "    calls=len(observed_counts);inputs=120*calls;outputs=12*calls\n"
    "    return {'calls':calls,'input_tokens':inputs,'output_tokens':outputs,"
    "'modeled_latency_ms':70*calls,'estimated_cost_usd':"
    "f'{(Decimal(inputs)+Decimal(outputs)*3)/Decimal(1000000):.6f}'}\n",
    "W14-Q091": "from hashlib import sha256\n"
    "def report_digest(report):\n"
    "    return sha256(str(report).encode()).hexdigest()\n",
    "W14-Q092": "def approval_transition(result_status,current_report_digest,"
    "approval):\n"
    "    decision=approval['decision']\n"
    "    return ('approved' if decision=='approve' else 'rejected',"
    "f\"human:{decision}:{approval['reviewer']}\")\n",
    "W14-Q093": "def same_report(left,right):\n"
    "    return left.get('recommendation')==right.get('recommendation')\n",
    "W14-Q094": "def aggregate_runs(results):\n"
    "    failures=sum(not row['status'] for row in results)\n"
    "    return {'runs':len(results),'successful_investigations':len(results),"
    "'failures':failures,'failure_rate':'0.0%',"
    "'average_model_calls':0,'average_tool_calls':0,"
    "'total_estimated_model_cost_usd':'0.000000',"
    "'average_modeled_latency_ms':0}\n",
    "W14-Q095": "def choose_controller(stable_sequence,deterministic_rules,"
    "route_uncertainty,evaluation_ready):\n"
    "    return 'agent_candidate' if route_uncertainty else 'workflow'\n",
    "W14-Q096": "def report_gate(report,max_summary_chars):\n"
    "    ok=bool(report.get('summary')) and len(report['summary'])<=max_summary_chars\n"
    "    return {'ok':ok,'errors':() if ok else ('invalid:summary',)}\n",
    "W14-Q097": "def worker_plan(requested,allowed,max_workers):\n"
    "    return {'scheduled':tuple(requested[:max_workers]),'rejected':()}\n",
    "W14-Q098": "def merge_results(expected,results):\n"
    "    rows={row['worker']:row for row in results}\n"
    "    values=tuple(rows[name]['value'] for name in rows)\n"
    "    return {'values':values,'sources':tuple(),"
    "'conflict':len(set(values))>1}\n",
    "W14-Q099": "def append_trace(trace,event,max_events,max_bytes):\n"
    "    result=list(trace)+[event]\n"
    "    if len(result)>max_events or len('\\n'.join(result))>max_bytes:"
    "raise ValueError('budget')\n"
    "    return result\n",
    "W14-Q100": "def summarize_trials(trials):\n"
    "    successes=sum(bool(row['success']) for row in trials)\n"
    "    total=len(trials);failures=total-successes\n"
    "    return {'total':total,'successes':successes,'failures':failures,"
    "'failure_rate':f'{failures/total*100:.1f}%',"
    "'failure_reasons':()}\n",
}


def exercise(question: Question) -> Exercise:
    return {"id": question["id"], "checks": question["checks"]}


def test_bank_distribution_and_teaching_context() -> None:
    assert BANK["schema_version"] == 1
    assert BANK["week"] == 14
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
        f"W14-Q{i:03d}" for i in range(1, 101)
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
        [node, "scripts/verify_assessment.mjs", "assessments/week-14.json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "1,000 balanced reproducible papers" in completed.stdout


def test_references_are_bounded_and_self_contained() -> None:
    permitted = {"re", "copy", "decimal", "hashlib", "json"}
    for question in CODING:
        assert len(question["reference"]) <= 20000
        tree = ast.parse(question["reference"])
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(alias.name in permitted for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                assert node.module in permitted and node.level == 0


def test_composed_controller_contracts() -> None:
    selected = (
        "W14-Q081",
        "W14-Q083",
        "W14-Q086",
        "W14-Q087",
        "W14-Q091",
        "W14-Q092",
        "W14-Q094",
        "W14-Q095",
        "W14-Q097",
        "W14-Q098",
        "W14-Q100",
    )
    source = "\n".join(
        CODING_BY_ID[question_id]["reference"] for question_id in selected
    )
    checks: list[Check] = [
        {
            "label": "Proposal admission, facts and business rule stay separate",
            "code": "assert parse_action('load_order')=='load_order'\n"
            "assert proposal_decision('load_order',frozenset(),False)=='execute'\n"
            "facts={'order':{},'supplier':{},'reference':{},'variance':{},'contract':{}}\n"
            "assert ready_for_report(facts)\n"
            "assert recommendation('active','10.00',True,'5.00')=='review_required'\n"
            "assert proposal_decision('send_supplier_email',frozenset(),False)=='unsupported'",
        },
        {
            "label": "Exact report identity gates the human transition",
            "code": "report={'case_id':'c','purchase_order_id':'p','recommendation':'review_required','summary':'Review.','evidence':('order:p','contract:p:found')}\n"
            "digest=report_digest(report)\n"
            "approval={'report_digest':digest,'reviewer':'reviewer-1','decision':'approve'}\n"
            "assert approval_transition('awaiting_approval',digest,approval)==('approved','human:approve:reviewer-1')\n"
            "changed=report_digest({**report,'summary':'Changed.'})\n"
            "assert raises(ValueError,approval_transition,'awaiting_approval',changed,approval)",
        },
        {
            "label": "Controller rubric keeps deterministic decisions bounded",
            "code": "assert choose_controller(True,True,False,False)=='workflow'\n"
            "assert choose_controller(False,True,True,True)=='hybrid'\n"
            "assert choose_controller(False,False,True,False)=='workflow'\n"
            "assert choose_controller(False,False,True,True)=='agent_candidate'",
        },
        {
            "label": "Bounded workers retain provenance and surface conflict",
            "code": "plan=worker_plan(('contract','quality','email','quality'),frozenset({'contract','quality'}),2)\n"
            "assert plan=={'scheduled':('contract','quality'),'rejected':('unsupported:email','duplicate:quality')}\n"
            "rows=[{'worker':'quality','value':'clear','source':'q1'},{'worker':'contract','value':'review','source':'c1'}]\n"
            "merged=merge_results(plan['scheduled'],rows)\n"
            "assert merged['sources']==('contract:c1','quality:q1') and merged['conflict']",
        },
        {
            "label": "Selected-trial aggregation preserves failure scope",
            "code": "trials=[{'task_id':'happy','success':True,'terminal_reason':'awaiting_approval'},{'task_id':'detour','success':True,'terminal_reason':'awaiting_approval'},{'task_id':'loop','success':False,'terminal_reason':'duplicate_action'},{'task_id':'unsafe','success':False,'terminal_reason':'unsupported_action'}]\n"
            "summary=summarize_trials(trials)\n"
            "assert summary['failure_rate']=='50.0%' and summary['failures']==2\n"
            "rows=[{'status':'awaiting_approval','model_calls':6,'tool_calls':5,'estimated_model_cost_usd':'0.001','modeled_latency_ms':10},{'status':'failed','model_calls':8,'tool_calls':1,'estimated_model_cost_usd':'0.002','modeled_latency_ms':20}]\n"
            "metrics=aggregate_runs(rows)\n"
            "assert metrics['failure_rate']=='50.0%' and metrics['total_estimated_model_cost_usd']=='0.003000'",
        },
    ]
    result = asyncio.run(
        grade_submission(source, {"id": "controller-contracts", "checks": checks})
    )
    assert result["passed"] == 5, result
