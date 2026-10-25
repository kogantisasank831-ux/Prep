"""Week 10 bank content, actual Python checks and shared paper/scoring contracts."""

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


BANK = cast(Bank, json.loads((ROOT / "assessments/week-10.json").read_text()))
CODING = [q for q in BANK["questions"] if q["type"] == "code"]
MUTANTS = {
    "W10-Q081": "def valid_ids(trace_id, span_id):\n"
    "    return len(str(trace_id).strip())==32 and "
    "len(str(span_id).strip())==16\n",
    "W10-Q082": "def elapsed_ms(start_ns,end_ns):\n"
    "    if not start_ns or not end_ns:return 0.0\n"
    "    return abs(end_ns-start_ns)/1000\n",
    "W10-Q083": "def trace_root(spans):\n"
    "    return next(row['id'] for row in spans if row.get('parent') is "
    "None)\n",
    "W10-Q084": "def timeline(spans):\n"
    "    spans.sort(key=lambda row:row['start_ns'] or 0)\n"
    "    return spans\n",
    "W10-Q085": "def self_time_ns(start,end,children):\n"
    "    return end-start-sum(b-a for a,b in children)\n",
    "W10-Q086": "def "
    "usage_record(input_tokens,output_tokens,cached_input_tokens,source):\n"
    "    return dict(input_tokens=input_tokens or "
    "0,output_tokens=output_tokens or "
    "0,cached_input_tokens=cached_input_tokens or "
    "0,source='provider_reported')\n",
    "W10-Q087": "def token_cost(usage,rates):\n"
    "    return "
    "str(round(((usage['input_tokens']+usage['cached_input_tokens'])*float(rates['input'])+usage['output_tokens']*float(rates['output']))/1000000,2))\n",
    "W10-Q088": "def error_category(error):\n"
    "    if isinstance(error,OSError):return 'dependency'\n"
    "    return str(error)\n",
    "W10-Q089": "def metadata_only(record):\n"
    "    return {k:v for k,v in record.items() if k!='password'}\n",
    "W10-Q090": "def source_units(spans):\n"
    "    return sorted({row['key'][1] for row in spans})\n",
    "W10-Q091": "def first_difference(baseline,candidate):\n"
    "    for key in "
    "('response','prompt','context','reranked','candidates','queries','scope'):\n"
    "        if baseline[key]!=candidate[key]:return key\n",
    "W10-Q092": "import hashlib\n"
    "def manifest_digest(manifest):\n"
    "    return "
    "hashlib.sha256(str(manifest.get('model','')).encode()).hexdigest()\n",
    "W10-Q093": "def trace_summary(spans):\n"
    "    return "
    "dict(span_count=len(spans),error_span_count=0,cancelled_span_count=0,root_duration_ns=sum(s['duration_ns'] "
    "or 0 for s in spans))\n",
    "W10-Q094": "def append_bounded(records,record,limit):\n"
    "    records.append(record)\n"
    "    return records,False\n",
    "W10-Q095": "def synthetic_capture(request,spans,enabled):\n"
    "    return {'request':request,'spans':spans}\n",
    "W10-Q096": "def attempt_totals(attempts):\n"
    "    return "
    "dict(attempt_count=len(attempts),input_tokens=sum(r.get('input_tokens') "
    "or 0 for r in attempts),output_tokens=sum(r.get('output_tokens') or 0 "
    "for r in attempts))\n",
    "W10-Q097": "def run_observed(action,events):\n"
    "    events.append('start')\n"
    "    try:return action()\n"
    "    except Exception:return None\n",
    "W10-Q098": "def deliver_once(result,sink,trace):\n"
    "    try:sink(trace);sink(trace);return result,True\n"
    "    except BaseException:return None,False\n",
    "W10-Q099": "def validate_messages(messages):\n"
    "    return tuple((r['role'],r['content'].strip()) for r in messages)\n",
    "W10-Q100": "def paired_latency(baseline,candidate):\n"
    "    return "
    "dict(pairs=[dict(request_id=k,baseline_ms=v/1000,candidate_ms=candidate.get(k,0)/1000,delta_ms=abs(candidate.get(k,0)-v)/1000) "
    "for k,v in baseline.items() if v and candidate.get(k)],excluded=0)\n",
}


def exercise(q: Question) -> Exercise:
    return {"id": q["id"], "checks": q["checks"]}


def test_bank_distribution_and_teaching_context() -> None:
    assert BANK["schema_version"] == 1
    assert BANK["week"] == 10
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
        f"W10-Q{i:03d}" for i in range(1, 101)
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
        [node, "scripts/verify_assessment.mjs", "assessments/week-10.json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "1,000 balanced reproducible papers" in completed.stdout


def test_references_are_bounded_and_self_contained() -> None:
    permitted = {"re", "decimal", "hashlib", "json", "copy"}
    for question in CODING:
        assert len(question["reference"]) <= 20000
        tree = ast.parse(question["reference"])
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(alias.name in permitted for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                assert node.module in permitted and node.level == 0


def test_composed_observability_contracts() -> None:
    wanted = {
        f"W10-Q{i:03d}"
        for i in (82, 83, 85, 86, 87, 89, 90, 91, 92, 93, 96, 97, 98, 100)
    }
    source = "\n".join(q["reference"] for q in CODING if q["id"] in wanted)
    checks: list[Check] = [
        {
            "label": "Tree order and independent interval union",
            "code": "s=[dict(id='child',parent='root',status='ok',duration_ns=60),dict(id='root',parent=None,status='ok',duration_ns=100)];assert trace_root(s)=='root' and trace_summary(s)['root_duration_ns']==100\nassert self_time_ns(0,100,[(10,60),(40,80)])==30 and elapsed_ms(0,2500000)==2.5 and raises(ValueError,trace_root,[dict(id='r',parent=None),dict(id='x',parent='x')])",
        },
        {
            "label": "Independent cached arithmetic and incomplete retry accounting",
            "code": "u=usage_record(1000,300,200,'provider_reported');rates=dict(input='2',output='8',cached='0.50');assert token_cost(u,rates)=='0.0041' and token_cost(dict(u,cached_input_tokens=None),rates) is None\na=[dict(attempt_id='1',input_tokens=1000,output_tokens=300),dict(attempt_id='2',input_tokens=None,output_tokens=0)];assert attempt_totals(a)==dict(attempt_count=2,input_tokens=None,output_tokens=300)",
        },
        {
            "label": "Context first difference and complete config identity",
            "code": "a={k:[] for k in ('scope','queries','candidates','reranked','context','prompt','response')};a.update(candidates=['a','b'],reranked=['b','a'],context=['a','b']);b=dict(a,context=['a'],response='short');assert first_difference(a,b)=='context'\nassert manifest_digest({'model':'m','budget':1400})!=manifest_digest({'model':'m','budget':300})\nx=('N','D','1','p1');y=('N','D','2','p1');assert source_units([dict(key=x),dict(key=x),dict(key=y)])==[x,y]",
        },
        {
            "label": "One application call and a separate failed export",
            "code": "calls=[];events=[];answer={'text':'computed'};result=run_observed(lambda:(calls.append(1),answer)[1],events)\ndef bad_sink(trace):raise OSError('raw details')\nout,ok=deliver_once(result,bad_sink,{'status':'ok'});assert out is answer and ok is False and calls==[1] and events==['start','ok','end']\nassert metadata_only(dict(request_id='r',prompt='SECRET',exception_message='SECRET',input_tokens=None,output_tokens=0))==dict(request_id='r',input_tokens=None,output_tokens=0)",
        },
        {
            "label": "Matched population preserves zero, direction and missingness",
            "code": "a={'slow':2000000,'zero':0,'unknown':None};b={'slow':1000000,'zero':0,'unknown':0};o=paired_latency(a,b);assert o['excluded']==1 and [r['request_id'] for r in o['pairs']]==['slow','zero'] and o['pairs'][0]['delta_ms']==-1.0 and o['pairs'][1]['delta_ms']==0.0\nassert raises(ValueError,paired_latency,a,{'other':0}) and a['unknown'] is None",
        },
    ]
    result = asyncio.run(
        grade_submission(source, {"id": "observability-contracts", "checks": checks})
    )
    assert result["passed"] == 5, result
