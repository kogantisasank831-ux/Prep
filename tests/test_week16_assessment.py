"""Week 16 bank content, executable Python checks and memory contracts."""

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


BANK = cast(Bank, json.loads((ROOT / "assessments/week-16.json").read_text()))
CODING = [q for q in BANK["questions"] if q["type"] == "code"]
CODING_BY_ID = {q["id"]: q for q in CODING}
MUTANTS = {
    "W16-Q081": "def validate_scope(t,a,c,w,p):\n    return t,c\n",
    "W16-Q082": "def validate_retention(o,e,n,max_days=90):\n    return max_days*86400\n",
    "W16-Q083": "def select_evidence(items):\n    return [dict(x) for x in items]\n",
    "W16-Q084": "def build_semantic_summary(m):\n    return str(m)\n",
    "W16-Q085": "import hashlib\ndef memory_digest(m):\n    return hashlib.sha256(str(m).encode()).hexdigest()\n",
    "W16-Q086": "def write_decision(c,r,i,e):\n    return {'action':'update','revision':r+1}\n",
    "W16-Q087": "def approval_transition(before,after):\n    return before!=after\n",
    "W16-Q088": "def apply_status_update(record,new_status,expected_revision):\n    result=dict(record);result['status']=new_status;return result\n",
    "W16-Q089": "def rank_episodes(question,episodes):\n    return [x['id'] for x in reversed(episodes)]\n",
    "W16-Q090": "def pack_context(prefix,episodes,max_characters):\n    return (prefix+'\\n- '+'\\n- '.join(episodes))[:max_characters]\n",
    "W16-Q091": "def recall_record(records,tenant_id,case_id,now):\n    return next(x for x in records if x['case_id']==case_id)\n",
    "W16-Q092": "def purge_expired(records,now):\n    return {'kept':records,'deleted_ids':[]}\n",
    "W16-Q093": "def forget_case(records,tenant_id,case_id):\n    kept=[x for x in records if x['case_id']!=case_id];return {'records':kept,'deleted':len(records)-len(kept)}\n",
    "W16-Q094": "def namespace_key(tenant_id,case_id):\n    return tenant_id.strip()+':'+case_id.strip()\n",
    "W16-Q095": "def context_projection(memory):\n    return dict(memory)\n",
    "W16-Q096": "def validate_memory_payload(memory):\n    return bool(memory.get('summary'))\n",
    "W16-Q097": "def retention_metrics(records,now):\n    return {'active':len(records),'expired':0,'soonest_active_expiry':None}\n",
    "W16-Q098": "def verify_source_refs(memory,current_sources):\n    return all(x['id'] in current_sources for x in memory['evidence_refs'])\n",
    "W16-Q099": "def merge_episodes(existing,incoming,expected_next,max_events,max_bytes):\n    return existing+incoming\n",
    "W16-Q100": "def audit_memory_lifecycle(events):\n    return {'revision':events[-1]['revision'],'forgotten':events[-1]['action']=='forget','events':len(events)}\n",
}


def exercise(question: Question) -> Exercise:
    return {"id": question["id"], "checks": question["checks"]}


def test_bank_distribution_and_teaching_context() -> None:
    assert BANK["schema_version"] == 1
    assert BANK["week"] == 16
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
        f"W16-Q{i:03d}" for i in range(1, 101)
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
        [node, "scripts/verify_assessment.mjs", "assessments/week-16.json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "1,000 balanced reproducible papers" in completed.stdout


def test_references_are_bounded_and_self_contained() -> None:
    permitted = {"copy", "datetime", "hashlib", "json", "re"}
    for question in CODING:
        assert len(question["reference"]) <= 20000
        tree = ast.parse(question["reference"])
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(alias.name in permitted for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                assert node.module in permitted and node.level == 0


def test_composed_memory_contracts() -> None:
    selected = tuple(
        f"W16-Q{i:03d}"
        for i in (81, 82, 83, 84, 85, 86, 89, 90, 91, 93, 95, 96, 98, 99, 100)
    )
    source = "\n".join(
        CODING_BY_ID[question_id]["reference"] for question_id in selected
    )
    checks: list[Check] = [
        {
            "label": "Scope, schema and minimal provenance compose",
            "code": "assert validate_scope('t',['c'],'c',True,True)==('t','c')\n"
            "payload={'schema_version':1,'category':'semantic','summary':'quote',"
            "'facts':{'supplier':'Acme'},'evidence_refs':['doc:1','sql:2'],"
            "'expires_at':'2026-04-01T00:00:00Z'}\n"
            "assert validate_memory_payload(payload)\n"
            "items=[{'kind':'document','ref':'doc:1','digest':'a'*64,'body':'raw'},"
            "{'kind':'sql','ref':'sql:2','digest':'b'*64,'body':'row'}]\n"
            "refs=select_evidence(items);assert all('body' not in x for x in refs)\n"
            "memory={'evidence_refs':[{'id':x['ref'],'digest':x['digest']} for x in refs]}\n"
            "sources={x['ref']:{'digest':x['digest'],'accessible':True} for x in refs}\n"
            "assert verify_source_refs(memory,sources)",
        },
        {
            "label": "Summary, digest and revisions compose",
            "code": "memory={'case_id':'c','supplier':'Acme','item':'valves',"
            "'currency':'USD','quoted_total':1250,'status':'draft',"
            "'evidence_refs':['sql:2','doc:1']}\n"
            "summary=build_semantic_summary(memory);digest=memory_digest(memory)\n"
            "assert 'doc:1,sql:2' in summary\n"
            "assert write_decision(None,0,digest,0)=={'action':'create','revision':1}\n"
            "assert write_decision(digest,1,digest,0)=="
            "{'action':'replay','revision':1}",
        },
        {
            "label": "Retention, recall, purge and forget agree",
            "code": "assert validate_retention('2026-01-01T00:00:00Z',"
            "'2026-04-01T00:00:00Z','2026-01-02T00:00:00Z')==90*86400\n"
            "records=[{'tenant_id':'t','case_id':'c','expires_at':"
            "'2026-04-01T00:00:00Z','summary':'s'}]\n"
            "assert recall_record(records,'t','c','2026-01-02T00:00:00Z')['summary']=='s'\n"
            "assert forget_case(records,'t','c')['deleted']==1",
        },
        {
            "label": "Ranked episodes fit a minimal context",
            "code": "episodes=[{'id':'e1','sequence':1,'text':'Acme quote'},"
            "{'id':'e2','sequence':2,'text':'Acme quote approved'}]\n"
            "assert rank_episodes('approved Acme quote',episodes)==['e2','e1']\n"
            "projection=context_projection({'tenant_id':'t','case_id':'c',"
            "'semantic_summary':'Acme quote','status':'awaiting_approval',"
            "'evidence_refs':['sql:2','doc:1'],'raw_conversation':['private']})\n"
            "packed=pack_context(projection['semantic_summary'],['e2','e1'],30)\n"
            "assert packed=='Acme quote\\n- e2\\n- e1' and 'private' not in packed",
        },
        {
            "label": "Bounded episodes produce an auditable lifecycle",
            "code": "episodes=merge_episodes([{'sequence':1,'text':'created'}],"
            "[{'sequence':2,'text':'approved'}],2,4,100)\n"
            "assert [x['sequence'] for x in episodes]==[1,2]\n"
            "events=[{'sequence':1,'action':'create','revision':1},"
            "{'sequence':2,'action':'replay','revision':1},"
            "{'sequence':3,'action':'status','revision':2},"
            "{'sequence':4,'action':'forget','revision':2}]\n"
            "assert audit_memory_lifecycle(events)=="
            "{'revision':2,'forgotten':True,'events':4}",
        },
    ]
    result = asyncio.run(
        grade_submission(source, {"id": "memory-contracts", "checks": checks})
    )
    assert result["passed"] == 5, result
