"""Week 12 bank content, actual Python checks and shared paper/scoring contracts."""

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


BANK = cast(Bank, json.loads((ROOT / "assessments/week-12.json").read_text()))
CODING = [q for q in BANK["questions"] if q["type"] == "code"]
MUTANTS = {
    "W12-Q081": "def config_integer(raw, minimum, maximum):\n"
    "    return max(minimum,min(maximum,int(raw)))\n",
    "W12-Q082": "def secret_value(raw):\n    return raw.decode().strip()\n",
    "W12-Q083": "import json\n"
    "def question_bytes(question):\n"
    "    return json.dumps({'question':question}).encode()\n",
    "W12-Q084": "def collect_body(chunks, limit):\n"
    "    raw=b''.join(chunks)\n"
    "    if len(raw)>limit:raise ValueError('request_too_large')\n"
    "    return raw\n",
    "W12-Q085": "def unit_vector(values):\n"
    "    scale=sum(abs(x) for x in values) or 1\n"
    "    return tuple(x/scale for x in values)\n",
    "W12-Q086": "def vector_candidates(rows, tenant, verified_ids, contract, limit):\n"
    "    ranked=sorted(rows,key=lambda r:r['distance'])[:limit]\n"
    "    return [r['chunk_id'] for r in ranked if r['tenant']==tenant and "
    "r['chunk_id'] in verified_ids]\n",
    "W12-Q087": "import hashlib\n"
    "def answer_key(tenant, principal, question, fingerprint, "
    "context_chars):\n"
    "    return "
    "principal,hashlib.sha256(question.strip().encode()).hexdigest()\n",
    "W12-Q088": "import hashlib,json\n"
    "def snapshot_digest(chunks, policies, contract):\n"
    "    return hashlib.sha256(json.dumps([c.get('text','') for c in "
    "chunks]).encode()).hexdigest()\n",
    "W12-Q089": "def renew_request(cached, request_id):\n"
    "    return dict(cached,request_id=request_id)\n",
    "W12-Q090": "def cache_read(entries, key, now):\n"
    "    if key not in entries:return None\n"
    "    expiry,value=entries[key]\n"
    "    if now>expiry:\n"
    "        del entries[key];return None\n"
    "    entries.move_to_end(key)\n"
    "    entries[key]=(now+15,value)\n"
    "    return value\n",
    "W12-Q091": "def cache_write(entries, key, result, now, ttl, capacity):\n"
    "    entries[key]=(now+ttl,result)\n"
    "    if len(entries)>capacity:entries.popitem()\n",
    "W12-Q092": "import math\n"
    "def window_step(state, now, limit):\n"
    "    window=int(now//60)\n"
    "    count=state[1] if state and state[0] else 0\n"
    "    return (window,count+1),0 if count<limit else int(60-now%60)\n",
    "W12-Q093": "def public_result(result, request_id, cache_hit):\n"
    "    return "
    "dict(result,request_id=request_id,status='answered',cache_hit=cache_hit)\n",
    "W12-Q094": "def sse_frame(event, payload):\n"
    "    return 'event: '+event+'\\ndata: '+str(payload)+'\\n\\n'\n",
    "W12-Q095": "def stream_complete(frames, request_id):\n"
    "    return any(event=='result' for event,payload in frames)\n",
    "W12-Q096": "def response_headers(request_id):\n"
    "    return "
    "{'X-Request-ID':str(request_id).strip(),'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}\n",
    "W12-Q097": "async def attempt_once(send):\n"
    "    try:return await send()\n"
    "    except BaseException:return None\n",
    "W12-Q098": "async def revalidate_once(read, compute):\n"
    "    first=await read()\n"
    "    result=await compute(first)\n"
    "    return result,True\n",
    "W12-Q099": "def own_slot(worker, token, release):\n    release(token)\n",
    "W12-Q100": "def seed_merge(existing, incoming):\n"
    "    return dict(existing,**incoming)\n",
}


def exercise(q: Question) -> Exercise:
    return {"id": q["id"], "checks": q["checks"]}


def test_bank_distribution_and_teaching_context() -> None:
    assert BANK["schema_version"] == 1
    assert BANK["week"] == 12
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
        f"W12-Q{i:03d}" for i in range(1, 101)
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
        [node, "scripts/verify_assessment.mjs", "assessments/week-12.json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "1,000 balanced reproducible papers" in completed.stdout


def test_references_are_bounded_and_self_contained() -> None:
    permitted = {"re", "hashlib", "json", "copy", "math", "asyncio", "collections"}
    for question in CODING:
        assert len(question["reference"]) <= 20000
        tree = ast.parse(question["reference"])
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(alias.name in permitted for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                assert node.module in permitted and node.level == 0


def test_composed_service_contracts() -> None:
    source = "\n".join(q["reference"] for q in CODING)
    checks: list[Check] = [
        {
            "label": "Configuration and compact representation preserve boundaries",
            "code": "assert config_integer('12',1,120)==12 and "
            "secret_value(b'A'*32+b'\\n')=='A'*32\n"
            "q='\\x00'*680+'a';raw=question_bytes(q);assert len(raw)==4096 and "
            "collect_body([raw[:2000],raw[2000:]],4096)==raw and "
            "raises(ValueError,question_bytes,'\\x00'*681)\n"
            "assert response_headers('a'*32)['Cache-Control']=='no-store'",
        },
        {
            "label": "Eligibility and complete identity prevent collapsed cache reuse",
            "code": "v=unit_vector([3,4]+[0]*30);assert v[:2]==(.6,.8)\n"
            "rows=[dict(tenant='S',chunk_id='denied',embedding_contract='v1',distance=0),dict(tenant='N',chunk_id='a',embedding_contract='v1',distance=.2)];assert "
            "vector_candidates(rows,'N',{'a'},'v1',1)==['a']\n"
            "p=[dict(tenant='N',document='D',version='1',readers=['a'],bindings={'a':'pin'})];c=[{'id':'a','metadata':{'page':1}}];fp=snapshot_digest(c,p,'v1');old=answer_key('N','a','Q',fp,1400);p[0]['readers']=[];new=answer_key('N','a','Q',snapshot_digest(c,p,'v1'),1400);assert "
            "old!=new and old!=answer_key('S','a','Q',fp,1400)",
        },
        {
            "label": "Cache recency, expiry and fresh public response remain separate",
            "code": "from collections import OrderedDict\n"
            "r={'reason':'ok','answer':'Net "
            "30','citation_ids':['S1'],'request_id':'old','denied_ids':['private']};e=OrderedDict();cache_write(e,'a',r,0,15,2);cache_write(e,'b',dict(r),1,15,2);hit=cache_read(e,'a',14);assert "
            "hit is "
            "r;fresh=renew_request(hit,'new');public=public_result(fresh,'new',True);assert "
            "public==dict(request_id='new',status='answered',answer='Net "
            "30',citation_ids=['S1'],cache_hit=True) and r['request_id']=='old';assert "
            "cache_read(e,'a',15) is None\n"
            "cache_write(e,'c',r,2,15,2);cache_write(e,'d',r,3,15,2);assert "
            "list(e)==['c','d'];before=list(e.items());cache_write(e,'z',dict(r,reason='source_changed'),4,15,2);assert "
            "list(e.items())==before",
        },
        {
            "label": "Fixed-window boundaries and complete SSE framing",
            "code": "import json\n"
            "state,retry=window_step(None,0,1);assert (state,retry)==((0,1),0);assert "
            "window_step(state,59.9,1)==((0,1),1) and "
            "window_step(state,60,1)==((1,1),0)\n"
            "rid='a'*32;payload=public_result(dict(reason='ok',answer='line1\\n\\nevent: "
            "forged',citation_ids=['S1']),rid,False);frames=[('meta',dict(request_id=rid,mode='validated-result')),('result',payload),('done',dict(request_id=rid,complete=True))];encoded=[sse_frame(event,p) "
            "for event,p in frames];decoded=[(event,json.loads(raw.splitlines()[1][6:])) "
            "for (event,_),raw in zip(frames,encoded)];assert "
            "stream_complete(decoded,rid) and not stream_complete(decoded[:-1],rid) and "
            "response_headers(rid)['X-Request-ID']==rid",
        },
        {
            "label": "Actual asynchronous completion owns admission and fresh recheck",
            "code": "import asyncio\n"
            "released=[];started=asyncio.Event();finish=asyncio.Event();reads=[]\n"
            "async def read():\n"
            "    reads.append('read');return {'fingerprint':'before' if len(reads)==1 "
            "else 'after','records':[]}\n"
            "async def compute(snapshot):\n"
            "    started.set();await finish.wait();return {'answer':'old'}\n"
            "async def send():return await revalidate_once(read,compute)\n"
            "worker=asyncio.create_task(attempt_once(send));own_slot(worker,'slot',released.append);await "
            "started.wait();assert released==[];finish.set();assert await "
            "worker==(None,False);await asyncio.sleep(0);assert released==['slot'] and "
            "reads==['read','read']",
        },
    ]
    result = asyncio.run(
        grade_submission(source, {"id": "service-contracts", "checks": checks})
    )
    assert result["passed"] == 5, result
