"""Week 4 bank content, actual Python checks and shared paper/scoring contracts."""

import asyncio
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


BANK = cast(Bank, json.loads((ROOT / "assessments/week-04.json").read_text()))
CODING = [q for q in BANK["questions"] if q["type"] == "code"]
MUTANTS = {
    "W04-Q081": "from decimal import Decimal\ndef decimal_string(value):\n    return Decimal(str(value))\n",
    "W04-Q082": "from decimal import Decimal\ndef amount_valid(value,field):\n    return isinstance(value,Decimal) and value.is_finite() and value>=0\n",
    "W04-Q083": "from datetime import date\ndef candidate_date(value):\n    return None if value is None else date.fromisoformat(value)\n",
    "W04-Q084": "def contract_text(value):\n    return str(value).strip()\n",
    "W04-Q085": "def key_issues(candidate):\n    required={'supplier_name','product','quantity','unit','unit_price','currency','payment_terms'}\n    return sorted(required-set(candidate)),[]\n",
    "W04-Q086": "def unique_pairs(pairs):\n    return dict(pairs)\n",
    "W04-Q087": "import json\ndef candidate_object(raw,byte_limit=32768):\n    return json.loads(raw)\n",
    "W04-Q088": "def fits_utf8(text,limit):\n    return len(text)<=limit\n",
    "W04-Q089": "def labelled_fields(text):\n    return {line.split(':',1)[0].strip().lower():line.split(':',1)[1].strip() for line in text.splitlines() if ':' in line}\n",
    "W04-Q090": "from decimal import Decimal\ndef source_quantity(text):\n    amount,unit=text.split()\n    return Decimal(amount.replace(',','')),unit\n",
    "W04-Q091": "from decimal import Decimal\ndef source_price(text):\n    currency,amount,_,unit=text.split()\n    return Decimal(amount),unit\n",
    "W04-Q092": "def same_amount(a,b):\n    return str(a)==str(b)\n",
    "W04-Q093": "def mismatch_names(candidate,evidence):\n    return tuple(k for k in candidate if str(candidate[k]).lower()!=str(evidence[k]).lower())\n",
    "W04-Q094": "def outcome_status(schema_ok,mismatches,delivery_date):\n    if delivery_date is None:return 'needs_review','DELIVERY_DATE_ABSENT'\n    return ('valid',None) if schema_ok and not mismatches else ('needs_review','SCHEMA_INVALID')\n",
    "W04-Q095": "def document_payload(document):\n    return '{\"document\":\"'+document+'\"}'\n",
    "W04-Q096": "import hashlib,json\ndef request_digest(messages,schema,prompt_version,schema_version):\n    return hashlib.sha256(json.dumps(messages).encode()).hexdigest()\n",
    "W04-Q097": "def call_cap(transport_attempts=2,repair_attempts=1):\n    return transport_attempts+repair_attempts\n",
    "W04-Q098": "def attempt_kind(repair_round,transport_index):\n    return 'validation_repair' if repair_round else 'transport_retry' if transport_index else 'initial'\n",
    "W04-Q099": "def recovery_trace(events):\n    kinds=['initial']+['transport_retry']*(len(events)-1)\n    return ('valid',None,kinds) if 'valid' in events else ('needs_review','TRANSPORT_EXHAUSTED',kinds)\n",
    "W04-Q100": "def support_metrics(results):\n    n=len(results);schema=sum(x[0] for x in results);supported=sum(x[1] for x in results)\n    return {'total':n,'schema_passed':schema,'evidence_supported':supported,'schema_rate':schema/n if n else None,'support_rate':supported/schema if schema else None}\n",
}


def exercise(q: Question) -> Exercise:
    return {"id": q["id"], "checks": q["checks"]}


def test_bank_distribution_and_teaching_context() -> None:
    assert BANK["schema_version"] == 1
    assert BANK["week"] == 4
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
        f"W04-Q{i:03d}" for i in range(1, 101)
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


def test_composed_business_contracts() -> None:
    by_id = {q["id"]: q for q in CODING}
    source = "\n".join(
        by_id[qid]["reference"]
        for qid in [
            "W04-Q081",
            "W04-Q082",
            "W04-Q085",
            "W04-Q090",
            "W04-Q091",
            "W04-Q094",
            "W04-Q099",
        ]
    )
    checks: list[Check] = [
        {
            "label": "Exact committed amount",
            "code": "from decimal import Decimal\nassert decimal_string('1000')*decimal_string('12.00')==Decimal('12000')\nassert amount_valid(Decimal('0'),'quantity') is False and amount_valid(Decimal('0'),'unit_price') is True",
        },
        {
            "label": "Presence is independent of null",
            "code": "x=dict.fromkeys(['supplier_name','product','quantity','unit','unit_price','currency','delivery_date','payment_terms']);assert key_issues(x)==([],[])\ndel x['delivery_date'];assert key_issues(x)==(['delivery_date'],[])",
        },
        {
            "label": "Comparable evidence units",
            "code": "from decimal import Decimal\nq,u=source_quantity('1,000 kg');p,v=source_price('USD 12.00 per kg');assert u==v=='kg' and q*p==Decimal('12000')\nassert source_price('USD 12.00 per ea')[1]!=u",
        },
        {
            "label": "Missing-date status cannot hide a mismatch",
            "code": "assert outcome_status(True,['supplier_name'],None)==('needs_review','EVIDENCE_MISMATCH')",
        },
        {
            "label": "Repair transport cap",
            "code": "assert recovery_trace(['schema','transport','transport','valid'])==('needs_review','TRANSPORT_EXHAUSTED',['initial','validation_repair','transport_retry'])",
        },
    ]
    result = asyncio.run(
        grade_submission(source, {"id": "business-contracts", "checks": checks})
    )
    assert result["passed"] == 5, result


def test_complete_paper_and_stale_result_contracts() -> None:
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required for JavaScript paper/scoring checks.")
    completed = subprocess.run(
        [node, "scripts/verify_assessment.mjs", "assessments/week-04.json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "1,000 balanced reproducible papers" in completed.stdout
