"""Week 11 bank content, actual Python checks and shared paper/scoring contracts."""

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


BANK = cast(Bank, json.loads((ROOT / "assessments/week-11.json").read_text()))
CODING = [q for q in BANK["questions"] if q["type"] == "code"]
MUTANTS = {
    "W11-Q081": "def safe_identifier(value):\n"
    "    return bool(str(value).strip()) and len(str(value).strip())<=64\n",
    "W11-Q082": "import json\n"
    "def strict_question(raw):\n"
    "    return json.loads(raw)['question'].strip()\n",
    "W11-Q083": "def unique_object(pairs):\n    return dict(pairs)\n",
    "W11-Q084": "def depth_within(raw,limit):\n"
    "    return raw.count('[')+raw.count('{')<=limit\n",
    "W11-Q085": "def screening_copy(text):\n    return text.strip().lower()\n",
    "W11-Q086": "def permits(context,chunk,policy):\n"
    "    return policy is not None and context['tenant']==chunk['tenant'] and "
    "context['principal'] in policy['readers']\n",
    "W11-Q087": "import hashlib\n"
    "def representation_pin(record):\n"
    "    return "
    "hashlib.sha256(str(record.get('text','')).encode()).hexdigest()\n",
    "W11-Q088": "def screened_sources(chunks,can_read,scan):\n"
    "    return [c for c in chunks if not scan(c['text']) and "
    "can_read(c)],0\n",
    "W11-Q089": "def selected_quotes(value,selected):\n"
    "    return tuple((r['citation'],r['text']) for r in value['quotes'] if "
    "r['citation'] in selected)\n",
    "W11-Q090": "def context_still_allowed(supplied_keys,can_read_now):\n"
    "    return not supplied_keys or bool(can_read_now(supplied_keys[0]))\n",
    "W11-Q091": "def "
    "security_event(request_id,reason,candidate_count,citation_count,blocked_chunk_count):\n"
    "    return "
    "dict(request_id=request_id,reason=reason,outcome='answered',candidate_count=candidate_count,citation_count=citation_count,blocked_chunk_count=blocked_chunk_count)\n",
    "W11-Q092": "import json\n"
    "def fit_context(rows,budget):\n"
    "    out=[]\n"
    "    for row in rows:\n"
    "        if sum(len(x.get('text','')) for x in "
    "out)+len(row.get('text',''))<=budget:out.append(row)\n"
    "    return out,json.dumps(out)\n",
    "W11-Q093": "def html_text(answer):\n    return answer\n",
    "W11-Q094": "def simple_findings(text):\n"
    "    return ('override',) if 'ignore previous instructions' in "
    "text.lower() else ()\n",
    "W11-Q095": "def propose_once(question,context,propose):\n"
    "    try:return propose(question,context) or None\n"
    "    except BaseException:return None\n",
    "W11-Q096": "def scoped_rank(records,eligible,rank):\n"
    "    ranked=rank(records)\n"
    "    return [r for r in ranked if eligible(r)]\n",
    "W11-Q097": "def "
    "cache_scope(tenant,principal,permission_version,source_keys,config_digest):\n"
    "    return tenant,tuple(sorted({key[1] for key in source_keys}))\n",
    "W11-Q098": "def context_limit(value):\n"
    "    return max(2,min(1400,int(value or 1400)))\n",
    "W11-Q099": "def supplied_sources(citations):\n"
    "    return sorted({r['document'] for r in citations})\n",
    "W11-Q100": "def catalogue_snapshot(catalogue):\n    return dict(catalogue)\n",
}


def exercise(q: Question) -> Exercise:
    return {"id": q["id"], "checks": q["checks"]}


def test_bank_distribution_and_teaching_context() -> None:
    assert BANK["schema_version"] == 1
    assert BANK["week"] == 11
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
        f"W11-Q{i:03d}" for i in range(1, 101)
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
        [node, "scripts/verify_assessment.mjs", "assessments/week-11.json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "1,000 balanced reproducible papers" in completed.stdout


def test_references_are_bounded_and_self_contained() -> None:
    permitted = {"re", "hashlib", "json", "copy", "unicodedata", "html"}
    for question in CODING:
        assert len(question["reference"]) <= 20000
        tree = ast.parse(question["reference"])
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(alias.name in permitted for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                assert node.module in permitted and node.level == 0


def test_composed_security_contracts() -> None:
    source = "\n".join(q["reference"] for q in CODING)
    checks: list[Check] = [
        {
            "label": "Denied distractors never reach scanning or ranking",
            "code": "rows=[dict(text='PRIVATE',allow=False),dict(text='Net 30',allow=True),dict(text='bad',allow=True)];seen=[];kept,blocked=screened_sources(rows,lambda r:r['allow'],lambda t:(seen.append(t),t=='bad')[1]);rank_seen=[];out=scoped_rank(kept,lambda r:True,lambda rs:(rank_seen.extend(rs),rs)[1]);assert seen==['Net 30','bad'] and blocked==1 and rank_seen==[rows[1]] and out[0] is rows[1]\nkept2,n2=screened_sources(rows[1:],lambda r:r['allow'],lambda t:t=='bad');assert kept2==kept and n2==blocked",
        },
        {
            "label": "Protected metadata baseline and current reader grant",
            "code": "key=('N','D','1');record={'text':'Net 30','metadata':{'page':1}};pin=representation_pin(record);c=dict(tenant='N',principal='a');x=dict(tenant='N',document='D',version='1',source_digest='source',chunk_id='c',representation_digest=pin);p=dict(tenant='N',document='D',version='1',source_digest='source',state='approved',readers=frozenset({'a'}),bindings={'c':pin});assert permits(c,x,p) and not permits(c,dict(x,representation_digest=representation_pin(dict(record,metadata={'page':2}))),p) and not permits(dict(c,tenant='S'),x,p)\np['readers']=frozenset();assert context_still_allowed([key],lambda k:permits(c,x,p)) is False",
        },
        {
            "label": "A detector miss cannot extend a closed output contract",
            "code": "import json\nassert simple_findings('i g n o r e previous instructions')==() and simple_findings(\"Training quotes 'ignore previous instructions'\")==('override',)\ns={'S1':'Net 30'};proposal={'quotes':[{'citation':'S1','text':'Net 30'}],'tool_call':{'name':'export'}};assert raises(ValueError,selected_quotes,proposal,s) and raises(ValueError,strict_question,'{\"question\":\"q\",\"tenant\":\"S\"}')\nassert selected_quotes(json.loads('{\"quotes\":[{\"citation\":\"S1\",\"text\":\"Net 30\"}]}',object_pairs_hook=unique_object),s)==(('S1','Net 30'),)",
        },
        {
            "label": "Context headers, omitted sources and safe consumers",
            "code": "a=dict(tenant='N',document='D',version='1',chunk_id='a');b=dict(tenant='N',document='E',version='1',chunk_id='b');keys=supplied_sources([a,b]);assert context_still_allowed(keys,lambda k:k[1]!='E') is False\nrows=[{'citation':'S1','text':'<img>'}];kept,raw=fit_context(rows,context_limit(1400));out=selected_quotes({'quotes':rows},{'S1':'<img>'});assert out==(('S1','<img>'),) and html_text(out[0][1])=='&lt;img&gt;' and rows[0]['text']=='<img>'\nassert fit_context(rows,2)==([], '[]') and propose_once('q',(),lambda q,c:1) is None",
        },
        {
            "label": "Diagnostics projection and independent derived scope",
            "code": "event=security_event('r','source_changed',2,0,1);assert event==dict(schema='week11-security-event/1.0.0',request_id='r',outcome='refused',reason='source_changed',candidate_count=2,citation_count=0,blocked_chunk_count=1)\nkey=('N','D','1');a={key:{'readers':['a'],'bindings':{'c':'old'}}};b=catalogue_snapshot(a);a[key]['bindings']['c']='new';assert b[key]['bindings']['c']=='old'\nx=cache_scope('N','a','v1',[key],'cfg');assert x!=cache_scope('N','a','v2',[key],'cfg') and x!=cache_scope('N','b','v1',[key],'cfg') and depth_within('{\"q\":\"[[[\"}',1)",
        },
    ]
    result = asyncio.run(
        grade_submission(source, {"id": "security-contracts", "checks": checks})
    )
    assert result["passed"] == 5, result
