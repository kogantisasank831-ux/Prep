"""Week 20 bank content, executable checks and reliability contracts."""

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


BANK = cast(Bank, json.loads((ROOT / "assessments/week-20.json").read_text()))
CODING = [question for question in BANK["questions"] if question["type"] == "code"]
MUTANTS = {
    "W20-Q081": "def classify_outcome(status,elapsed_ms,timeout_ms,required_fields,data):\n    return 'ok' if status=='ok' else status\n",
    "W20-Q082": "def capped_backoff(attempt,base_ms,cap_ms):\n    return base_ms * (2 ** (attempt-1))\n",
    "W20-Q083": "def retry_delay(attempt,base_ms,backoff_cap_ms,retry_after_ms,retry_after_cap_ms):\n    backoff=min(backoff_cap_ms,base_ms*(2**(attempt-1)))\n    return backoff if retry_after_ms is None else min(backoff,retry_after_ms,retry_after_cap_ms)\n",
    "W20-Q084": "def should_retry(outcome,attempt,max_attempts,circuit_state,operation_safe):\n    return outcome in {'unavailable','rate_limited','timeout'} and attempt < max_attempts and circuit_state != 'open'\n",
    "W20-Q085": "def circuit_admission(state,now_ms,opened_at_ms,recovery_timeout_ms):\n    return (state,state!='open')\n",
    "W20-Q086": "def circuit_failure(state,consecutive_failures,threshold,now_ms):\n    failures=consecutive_failures+1\n    return {'state':'open' if failures>threshold else 'closed','consecutive_failures':failures,'opened_at_ms':now_ms if failures>threshold else None}\n",
    "W20-Q087": "def circuit_success(state,consecutive_failures,opened_at_ms):\n    return (state,consecutive_failures,opened_at_ms)\n",
    "W20-Q088": "def required_fields_present(required_fields,data):\n    return not required_fields or any(field in data for field in required_fields)\n",
    "W20-Q089": "def fallback_resolution(primary_code,fallback_name,data):\n    return {'status':'completed','code':'ok','selected_dependency':fallback_name,'data':data,'warnings':()}\n",
    "W20-Q090": "def terminal_failure_code(outcome,failure_kind):\n    return {'unavailable':'dependency_unavailable','rate_limited':'rate_limited','timeout':'timeout','invalid_response':'invalid_response','dependency_failure':'dependency_failure','circuit_open':'circuit_open'}[outcome]\n",
    "W20-Q091": "def register_idempotency(key,tenant,scenario,fingerprints):\n    if key in fingerprints: return 'duplicate'\n    fingerprints[key]=(tenant,scenario); return 'accept'\n",
    "W20-Q092": "def lease_next(pending,in_flight,deliveries):\n    return None if not pending else pending.pop(0)\n",
    "W20-Q093": "def acknowledge(job_id,result_job_id,idempotency_key,in_flight,results):\n    del in_flight[job_id]; results[idempotency_key]=result_job_id; return True\n",
    "W20-Q094": "def can_requeue(failure_kind,delivery_count,max_deliveries):\n    return failure_kind=='transient' and delivery_count <= max_deliveries\n",
    "W20-Q095": "def dead_letter_record(job,code,delivery_count,dependency_attempt_count):\n    return {**job,'code':code,'delivery_count':delivery_count,'dependency_attempt_count':dependency_attempt_count}\n",
    "W20-Q096": "def summarize_batch(statuses):\n    return {'completed_count':statuses.count('completed'),'degraded_count':statuses.count('degraded'),'dead_letter_count':statuses.count('failed'),'total':len(statuses)}\n",
    "W20-Q097": "def ordered_results(job_ids,results):\n    return tuple(results.values())\n",
    "W20-Q098": "def attempt_record(dependency,attempt,invoked,outcome,elapsed_ms,scheduled_backoff_ms,circuit_state_after):\n    return {'dependency':dependency,'attempt':attempt,'outcome':outcome,'elapsed_ms':elapsed_ms,'scheduled_backoff_ms':scheduled_backoff_ms,'circuit_state_after':circuit_state_after}\n",
    "W20-Q099": "def outcome_counts(attempts):\n    counts={}\n    for row in attempts: counts[row['dependency']]=counts.get(row['dependency'],0)+1\n    return counts\n",
    "W20-Q100": "def valid_reliability_lifecycle(events):\n    return bool(events) and events[0]=='submitted' and events[-1] in {'acknowledged','dead_lettered'}\n",
}


def exercise(question: Question) -> Exercise:
    return {"id": question["id"], "checks": question["checks"]}


def test_bank_distribution_and_teaching_context() -> None:
    assert BANK["schema_version"] == 1
    assert BANK["week"] == 20
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
        f"W20-Q{index:03d}" for index in range(1, 101)
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
        [node, "scripts/verify_assessment.mjs", "assessments/week-20.json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "1,000 balanced reproducible papers" in completed.stdout


def test_references_are_bounded_and_self_contained() -> None:
    for question in CODING:
        assert len(question["reference"]) <= 20_000
        tree = ast.parse(question["reference"])
        assert not any(
            isinstance(node, (ast.Import, ast.ImportFrom)) for node in ast.walk(tree)
        )


def test_composed_reliability_contracts() -> None:
    source = "\n".join(question["reference"] for question in CODING)
    checks: list[Check] = [
        {
            "label": "Classification, delay and retry safety compose",
            "code": "outcome=classify_outcome('rate_limited',5,100,(),{})\n"
            "delay=retry_delay(1,100,1000,300,500)\n"
            "assert outcome=='rate_limited' and delay==300\n"
            "assert capped_backoff(3,100,250)==250\n"
            "assert should_retry(outcome,1,3,'closed',True)\n"
            "assert not should_retry('invalid_response',1,3,'closed',True)\n"
            "assert not should_retry('timeout',1,3,'closed',False)",
        },
        {
            "label": "Circuit threshold, fast fail and recovery compose",
            "code": "first=circuit_failure('closed',0,2,0); assert first['state']=='closed'\n"
            "second=circuit_failure('closed',first['consecutive_failures'],2,10); assert second['state']=='open'\n"
            "assert circuit_admission('open',509,second['opened_at_ms'],500)==('open',False)\n"
            "assert circuit_admission('open',510,second['opened_at_ms'],500)==('half_open',True)\n"
            "assert circuit_success('half_open',2,second['opened_at_ms'])==('closed',0,None)",
        },
        {
            "label": "Output validation, fallback and safe evidence compose",
            "code": "assert not required_fields_present(('supplier_id','risk'),{'supplier_id':'S1'})\n"
            "fallback=fallback_resolution('timeout','bounded-cache',{'orders':['PO-1'],'freshness':'stale-45s'})\n"
            "assert fallback['status']=='degraded' and fallback['code']=='fallback_used'\n"
            "assert terminal_failure_code('timeout','transient')=='retry_exhausted'\n"
            "attempt=attempt_record('database-primary',1,True,'timeout',250,100,'closed')\n"
            "counts=outcome_counts(({'dependency':attempt['dependency'],'outcome':attempt['outcome']},))\n"
            "assert counts['timeout']==1 and 'database-primary' not in counts",
        },
        {
            "label": "Idempotency, lease, acknowledgement and delivery budget compose",
            "code": "fingerprints={}; assert register_idempotency('k1','t1','rate-limit-errors',fingerprints)=='accept'\n"
            "assert register_idempotency('k1','t1','rate-limit-errors',fingerprints)=='duplicate'\n"
            "pending=['j1']; active={}; deliveries={}\n"
            "job=lease_next(pending,active,deliveries); assert job=='j1' and deliveries['j1']==1\n"
            "results={}; assert acknowledge(job,job,'k1',active,results)\n"
            "assert results=={'k1':'j1'} and not can_requeue('transient',2,2)",
        },
        {
            "label": "Partial batch, minimal dead letter and lifecycle compose",
            "code": "ids=('j1','j2','j3','j4','j5')\n"
            "statuses=ordered_results(ids,{'j1':'degraded','j2':'degraded','j3':'dead_letter','j4':'degraded','j5':'completed'})\n"
            "assert summarize_batch(statuses)=={'completed_count':1,'degraded_count':3,'dead_letter_count':1,'total':5}\n"
            "job={'job_id':'j3','tenant_id':'t1','idempotency_key':'k3','scenario':'invalid-api-result'}\n"
            "record=dead_letter_record(job,'invalid_response',1,1); assert 'idempotency_key' not in record\n"
            "assert valid_reliability_lifecycle(('submitted','leased','dead_lettered'))\n"
            "assert not valid_reliability_lifecycle(('submitted','dead_lettered'))",
        },
    ]
    result = asyncio.run(
        grade_submission(source, {"id": "W20-COMPOSED", "checks": checks})
    )
    assert result["passed"] == result["total"] == 5, result
