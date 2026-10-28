"""Week 13 bank content, actual Python checks and shared paper/scoring contracts."""

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


BANK = cast(Bank, json.loads((ROOT / "assessments/week-13.json").read_text()))
CODING = [q for q in BANK["questions"] if q["type"] == "code"]
MUTANTS = {
    "W13-Q081": "def tool_name(value):\n"
    "    return isinstance(value,str) and "
    "value.strip().lower().replace('_','').isalpha()\n",
    "W13-Q082": "def sql_arguments(value):\n"
    "    return dict(value,limit=int(value['limit']))\n",
    "W13-Q083": "from decimal import Decimal\n"
    "def money_value(value):\n"
    "    return Decimal(float(value))\n",
    "W13-Q084": "def price_change(baseline, current, base_currency, new_currency, "
    "base_unit, new_unit):\n"
    "    delta=float(current)-float(baseline)\n"
    "    return f'{delta:.2f}',f'{delta/float(current)*100:.2f}'\n",
    "W13-Q085": "def tool_definition(name, description, properties, required, effect):\n"
    "    return "
    "dict(name=name,description=description,effect=effect,parameters=dict(type='object',properties=properties,required=required))\n",
    "W13-Q086": "def visible_tools(definitions, writable):\n"
    "    return definitions if writable else [d for d in definitions if "
    "d['effect']=='read']\n",
    "W13-Q087": "def correlated_reply(expected_call_id, reply):\n"
    "    return dict(reply,call_id=expected_call_id)\n",
    "W13-Q088": "def error_reply(call_id, name, code, attempts):\n"
    "    return "
    "dict(call_id=call_id,name=name,status='error',data=None,error=str(code),attempts=attempts)\n",
    "W13-Q089": "def evidence_ok(references, outcomes):\n"
    "    return all(x in {r['call_id'] for r in outcomes} for x in "
    "references)\n",
    "W13-Q090": "import hashlib\n"
    "def operation_digest(tenant, principal, key, arguments):\n"
    "    return hashlib.sha256(key.encode()).hexdigest()\n",
    "W13-Q091": "def approval_allows(writable, expected_digest, approval, now):\n"
    "    return bool(writable and approval and now<=approval['expires'])\n",
    "W13-Q092": "def intent_state(ledger, scope, digest):\n"
    "    return 'replay' if scope in ledger else 'new'\n",
    "W13-Q093": "import copy\n"
    "def read_saved(lookup, authorized, approved, digest):\n"
    "    row=lookup()\n"
    "    return None if row is None else copy.deepcopy(row['result'])\n",
    "W13-Q094": "def store_once(ledger, scope, digest, make):\n"
    "    if scope in ledger:return ledger[scope]['result'],True\n"
    "    value=make();ledger[scope]={'digest':digest,'result':value};return "
    "value,False\n",
    "W13-Q095": "def retry_action(effect, code, attempt):\n"
    "    return 'retry' if code in ('unavailable','timeout') and attempt<2 "
    "else 'stop'\n",
    "W13-Q096": "async def retry_read(send, delay):\n"
    "    try:return await send()\n"
    "    except BaseException:\n"
    "        await delay(0.05)\n"
    "        return await send()\n",
    "W13-Q097": "async def checked_read(validate, execute, project, raw):\n"
    "    value=await execute(raw)\n"
    "    validate(raw)\n"
    "    return value\n",
    "W13-Q098": "import asyncio\n"
    "async def timed_read(operation, seconds):\n"
    "    try:\n"
    "        async with asyncio.timeout(seconds):\n"
    "            return await operation()\n"
    "    except (TimeoutError, ValueError):\n"
    "        return None\n",
    "W13-Q099": "def append_message(messages, message, limit):\n"
    "    if sum(len(m.get('content','')) for m in "
    "messages)+len(message.get('content',''))>limit:\n"
    "        raise ValueError('transcript_budget')\n"
    "    return messages+[message]\n",
    "W13-Q100": "def purchase_rows(records, tenant, principal, limit):\n"
    "    return [dict(r) for r in sorted(records,key=lambda "
    "r:r['purchase_order_id'])[:limit] if r['tenant']==tenant]\n",
}


def exercise(q: Question) -> Exercise:
    return {"id": q["id"], "checks": q["checks"]}


def test_bank_distribution_and_teaching_context() -> None:
    assert BANK["schema_version"] == 1
    assert BANK["week"] == 13
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
        f"W13-Q{i:03d}" for i in range(1, 101)
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
        [node, "scripts/verify_assessment.mjs", "assessments/week-13.json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "1,000 balanced reproducible papers" in completed.stdout


def test_references_are_bounded_and_self_contained() -> None:
    permitted = {"re", "hashlib", "json", "copy", "decimal", "asyncio"}
    for question in CODING:
        assert len(question["reference"]) <= 20000
        tree = ast.parse(question["reference"])
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(alias.name in permitted for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                assert node.module in permitted and node.level == 0


def test_composed_tool_contracts() -> None:
    source = "\n".join(q["reference"] for q in CODING)
    checks: list[Check] = [
        {
            "label": "Closed capability and caller-scoped rows remain separate",
            "code": "properties={'query_name':{'type':'string'},'purchase_order_id':{'type':['string','null']},'limit':{'type':'integer'}}\n"
            "definition=tool_definition('sql_query','Named "
            "reads',properties,list(properties),'read')\n"
            "assert tool_name(definition['name']) and "
            "definition['parameters']['additionalProperties'] is False\n"
            "write=tool_definition('create_review','Local review',{},[],'write')\n"
            "assert visible_tools([definition,write],False)==[definition]\n"
            "args=sql_arguments(dict(query_name='open_purchase_orders',purchase_order_id=None,limit=1))\n"
            "assert raises(ValueError,sql_arguments,dict(args,tenant='South'))\n"
            "base=dict(supplier_id='S',commodity_id='C',baseline='10.00',current='11.00',currency='USD',unit='kg')\n"
            "records=[dict(base,tenant='South',readers=['alice'],purchase_order_id='A'),dict(base,tenant='North',readers=['other'],purchase_order_id='B'),dict(base,tenant='North',readers=['alice'],purchase_order_id='C')]\n"
            "rows=purchase_rows(records,'North','alice',args['limit'])\n"
            "assert [r['purchase_order_id'] for r in rows]==['C'] and 'readers' not in "
            "rows[0] and 'tenant' not in rows[0]",
        },
        {
            "label": "Exact arithmetic, correlated results and successful evidence",
            "code": "assert str(money_value('10.00'))=='10.00'\n"
            "assert "
            "price_change('10.00','11.00','USD','USD','kg','kg')==('1.00','10.00')\n"
            "assert "
            "price_change('200.00','200.01','USD','USD','kg','kg')==('0.01','0.00')\n"
            "result=dict(call_id='c1',name='price_variance',status='ok',data={'delta':'1.00','percent':'10.00'},error=None,attempts=1)\n"
            "safe=correlated_reply('c1',result)\n"
            "assert safe==result and safe is not result and "
            "raises(ValueError,correlated_reply,'different',result)\n"
            "failure=error_reply('c2','create_review','unknown_outcome',1)\n"
            "assert failure['status']=='unknown' and "
            "retry_action('write','unavailable',1)=='unknown'\n"
            "assert evidence_ok(['c1'],[safe,failure]) and not "
            "evidence_ok(['c2'],[safe,failure])\n"
            "messages=append_message([],safe,4096)\n"
            "messages[0]['data']['delta']='changed'\n"
            "assert safe['data']['delta']=='1.00'",
        },
        {
            "label": "Full scoped intent, current approval and retained conflict",
            "code": "scope=('North','alice','intent-1');args={'purchase_order_id':'PO-1001','reason':'price_variance'}\n"
            "digest=operation_digest(*scope,args)\n"
            "assert approval_allows(True,digest,dict(digest=digest,expires=11),10)\n"
            "assert not approval_allows(True,digest,dict(digest=digest,expires=11),11)\n"
            "ledger={};calls=[]\n"
            "def make():calls.append(1);return {'review_id':'R1','notes':[]}\n"
            "assert intent_state(ledger,scope,digest)=='new'\n"
            "result,replayed=store_once(ledger,scope,digest,make)\n"
            "assert result['review_id']=='R1' and replayed is False\n"
            "result['notes'].append('local')\n"
            "assert "
            "store_once(ledger,scope,digest,make)==({'review_id':'R1','notes':[]},True) "
            "and calls==[1]\n"
            "changed=operation_digest(*scope,dict(args,reason='supplier_change'))\n"
            "assert changed!=digest and intent_state(ledger,scope,changed)=='conflict'\n"
            "assert raises(ValueError,store_once,ledger,scope,changed,make) and "
            "calls==[1]\n"
            "assert intent_state(ledger,('South','alice','intent-1'),digest)=='new'\n"
            "assert operation_digest('South','alice','intent-1',args)!=digest",
        },
        {
            "label": "Current replay authority and failed creation preserve ownership",
            "code": "events=[];saved={'digest':'d','result':{'review_id':'R','notes':[]}}\n"
            "def allowed():events.append('grant');return True\n"
            "def approved():events.append('approval');return True\n"
            "def lookup():events.append('lookup');return saved\n"
            "out=read_saved(lookup,allowed,approved,'d')\n"
            "assert events==['grant','approval','lookup']\n"
            "out['notes'].append('changed');assert saved['result']['notes']==[]\n"
            "events.clear()\n"
            "def denied():events.append('grant');return False\n"
            "assert raises(PermissionError,read_saved,lookup,denied,approved,'d') and "
            "events==['grant']\n"
            "ledger={};scope=('N','a','key');error=RuntimeError('create failed')\n"
            "def fail():raise error\n"
            "try:store_once(ledger,scope,'d',fail)\n"
            "except RuntimeError as actual:assert actual is error\n"
            "else:raise AssertionError('original failure hidden')\n"
            "assert ledger=={}",
        },
        {
            "label": "Validation, bounded transient read and projection compose in order",
            "code": "events=[];count=0;raw=dict(query_name='open_purchase_orders',purchase_order_id=None,limit=1)\n"
            "def validate(value):events.append('validate');return sql_arguments(value)\n"
            "async def execute(value):\n"
            "    events.append('execute');assert value==raw\n"
            "    async def send():\n"
            "        global count\n"
            "        count+=1;events.append('send')\n"
            "        if count==1:raise ConnectionError('temporary')\n"
            "        return "
            "dict(call_id='c1',name='sql_query',status='ok',data={'rows':[]},error=None,attempts=2)\n"
            "    async def delay(seconds):events.append('delay');assert seconds==0.05\n"
            "    async def operation():return await retry_read(send,delay)\n"
            "    return await timed_read(operation,1)\n"
            "def project(value):events.append('project');return "
            "correlated_reply('c1',value)\n"
            "out=await checked_read(validate,execute,project,raw)\n"
            "assert out['attempts']==2 and "
            "events==['validate','execute','send','delay','send','project']\n"
            "events.clear()\n"
            "try:await checked_read(validate,execute,project,dict(raw,limit='1'))\n"
            "except ValueError:pass\n"
            "else:raise AssertionError('invalid input reached execution')\n"
            "assert events==['validate'] and count==2",
        },
    ]
    result = asyncio.run(
        grade_submission(source, {"id": "tool-contracts", "checks": checks})
    )
    assert result["passed"] == 5, result
