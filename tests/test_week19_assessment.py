"""Week 19 bank content, executable checks and guardrail contracts."""

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


BANK = cast(Bank, json.loads((ROOT / "assessments/week-19.json").read_text()))
CODING = [question for question in BANK["questions"] if question["type"] == "code"]
MUTANTS = {
    "W19-Q081": "def permission_allows(required, granted):\n    return required in granted\n",
    "W19-Q082": "def lookup_tool_policy(tool, registry):\n    return registry.get(tool)\n",
    "W19-Q083": "def exact_arguments(required_names, arguments):\n    return set(required_names) <= set(arguments)\n",
    "W19-Q084": "def scoped_lookup(trusted_tenant, resource_id, records):\n    for row in records:\n        if row['resource_id'] == resource_id:\n            return row['value']\n    return None\n",
    "W19-Q085": "def approval_matches(grant, context):\n    return not grant['consumed'] and grant['tool'] == context['tool'] and grant['argument_sha256'] == context['argument_sha256']\n",
    "W19-Q086": "def consume_approval(approval_id, ledger):\n    ledger[approval_id] = True\n    return True\n",
    "W19-Q087": "def within_step_budget(step, max_steps):\n    return step < max_steps\n",
    "W19-Q088": "def controlled_result(status, code):\n    return {'status':status,'code':code}\n",
    "W19-Q089": "def contains_secret_key(payload, allowed_keys=()):\n    return any('secret' in str(key).lower() or 'password' in str(key).lower() for key in payload)\n",
    "W19-Q090": "def safe_audit_projection(event):\n    return dict(event)\n",
    "W19-Q091": "import hashlib\n\ndef canonical_argument_digest(arguments):\n    return hashlib.sha256(repr(arguments).encode()).hexdigest()\n",
    "W19-Q092": "import hashlib\n\ndef linked_event(previous_hash, sequence, body):\n    return {'sequence':sequence,'previous_hash':previous_hash,'body':body,'event_hash':hashlib.sha256(repr(body).encode()).hexdigest()}\n",
    "W19-Q093": "def verify_audit_chain(events):\n    return all(event['sequence'] == index for index,event in enumerate(events,1))\n",
    "W19-Q094": "def reversal_decision(receipt, trusted_tenant, current_value, used_tokens):\n    return 'ok' if current_value == receipt['after'] else 'undo_conflict'\n",
    "W19-Q095": "def set_review_flag(flags, trusted_tenant, flag_id, value):\n    before=flags.get(flag_id,'clear'); flags[flag_id]=value; return {'before':before,'after':value}\n",
    "W19-Q096": "def revert_review_flag(flags, receipt, trusted_tenant, used_tokens):\n    flags[(trusted_tenant,receipt['flag_id'])]=receipt['before']; return receipt['before']\n",
    "W19-Q097": "def policy_decision(policy, granted, approval_present):\n    if policy['mode']=='write' and not approval_present: return 'approval_required'\n    return 'ok' if policy['permission'] in granted else 'permission_denied'\n",
    "W19-Q098": "def requires_approval(mode):\n    return mode != 'read'\n",
    "W19-Q099": "def public_failure(error_name):\n    return {'status':'failed','code':error_name}\n",
    "W19-Q100": "def valid_lifecycle(events):\n    return bool(events) and events[0]=='requested' and events[-1] in {'executed','failed','denied','step_limit','reversed'}\n",
}


def exercise(question: Question) -> Exercise:
    return {"id": question["id"], "checks": question["checks"]}


def test_bank_distribution_and_teaching_context() -> None:
    assert BANK["schema_version"] == 1
    assert BANK["week"] == 19
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
        f"W19-Q{index:03d}" for index in range(1, 101)
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
        [node, "scripts/verify_assessment.mjs", "assessments/week-19.json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "1,000 balanced reproducible papers" in completed.stdout


def test_references_are_bounded_and_self_contained() -> None:
    permitted = {"hashlib", "json"}
    for question in CODING:
        assert len(question["reference"]) <= 20_000
        tree = ast.parse(question["reference"])
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(alias.name in permitted for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                assert node.module in permitted and node.level == 0


def test_composed_guardrail_contracts() -> None:
    source = "\n".join(question["reference"] for question in CODING)
    checks: list[Check] = [
        {
            "label": "Closed registry permission arguments and approval remain separate",
            "code": "registry={'contract_lookup':{'mode':'read','permission':'contract:read','arguments':('contract_id',)},'review_flag_set':{'mode':'write','permission':'review_flag:write','arguments':('flag_id','value')}}\n"
            "read=lookup_tool_policy('contract_lookup',registry); write=lookup_tool_policy('review_flag_set',registry)\n"
            "assert lookup_tool_policy('shell_exec',registry) is None\n"
            "assert permission_allows(read['permission'],('contract:read',))\n"
            "assert exact_arguments(read['arguments'],{'contract_id':'C1'})\n"
            "write_policy={'mode':write['mode'],'permission':write['permission']}\n"
            "assert policy_decision(write_policy,('review_flag:write',),False)=='approval_required'",
        },
        {
            "label": "Exact one-use approval and step ceiling block replay and overrun",
            "code": "d=canonical_argument_digest({'flag_id':'F1','value':'needs_human'})\n"
            "context={'tenant_id':'t','principal_id':'p','run_id':'r','case_id':'c','request_id':'q','tool':'review_flag_set','argument_sha256':d}\n"
            "grant={**context,'approval_id':'a1','consumed':False}\n"
            "assert approval_matches(grant,context) and within_step_budget(2,2)\n"
            "ledger={'a1':False}; assert consume_approval('a1',ledger)\n"
            "assert raises(ValueError,consume_approval,'a1',ledger)\n"
            "assert within_step_budget(3,2) is False",
        },
        {
            "label": "Secret minimization and linked audit evidence compose",
            "code": "assert contains_secret_key({'password':'x'}) is True\n"
            "event={'sequence':1,'tenant_id':'t','principal_id':'p','tool':'contract_lookup','code':'ok','arguments':{'contract_id':'C1'},'exception':None}\n"
            "safe=safe_audit_projection(event); assert 'arguments' not in safe and 'exception' not in safe\n"
            "body={'event_type':'requested','tenant_id':'t','tool':'contract_lookup','code':'request_received','argument_sha256':safe['argument_sha256']}\n"
            "first=linked_event(None,1,body); second=linked_event(first['event_hash'],2,{**body,'event_type':'executed','code':'ok'})\n"
            "assert verify_audit_chain((first,second))",
        },
        {
            "label": "Tenant-scoped write and conflict-aware one-use reversal compose",
            "code": "flags={}; receipt=set_review_flag(flags,'t','F1','needs_human'); used=set()\n"
            "decision_receipt={key:receipt[key] for key in ('tenant_id','undo_token','before','after')}\n"
            "assert reversal_decision(decision_receipt,'t',flags[('t','F1')],tuple(used))=='ok'\n"
            "assert revert_review_flag(flags,receipt,'t',used)=='clear'\n"
            "assert flags[('t','F1')]=='clear' and receipt['undo_token'] in used\n"
            "assert raises(ValueError,revert_review_flag,flags,receipt,'t',used)",
        },
        {
            "label": "Controlled status failure and lifecycle contracts agree",
            "code": "assert controlled_result('blocked','permission_denied')==public_failure('permission_error')\n"
            "assert public_failure('postgres://secret@db')=={'status':'failed','code':'tool_failure'}\n"
            "assert requires_approval('write') and not requires_approval('read')\n"
            "assert valid_lifecycle(('requested','denied'))\n"
            "assert valid_lifecycle(('requested','approval_checked','reversed'))\n"
            "assert not valid_lifecycle(('requested','reversed'))",
        },
    ]
    result = asyncio.run(
        grade_submission(source, {"id": "W19-COMPOSED", "checks": checks})
    )
    assert result["passed"] == result["total"] == 5, result
