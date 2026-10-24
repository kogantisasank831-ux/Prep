"""Week 8 bank content, actual Python checks and shared paper/scoring contracts."""

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


BANK = cast(Bank, json.loads((ROOT / "assessments/week-08.json").read_text()))
CODING = [q for q in BANK["questions"] if q["type"] == "code"]
MUTANTS = {
    "W08-Q081": "def checked_scores(values,count):\n    return tuple(float(x) for x in values)\n",
    "W08-Q082": "def rerank_rows(rows,scores):\n"
    "    return [dict(r,score=s) for r,s in sorted(zip(rows,scores),key=lambda "
    "x:-x[1])]\n",
    "W08-Q083": "def query_pairs(original,passages):\n"
    "    return tuple((original.strip(),p.strip()) for p in passages)\n",
    "W08-Q084": "def protected_terms(text):\n    return frozenset(text.lower().split())\n",
    "W08-Q085": "def make_query_plan(original,rewrites=()):\n"
    "    return tuple(dict.fromkeys([original,*rewrites]))\n",
    "W08-Q086": "def "
    "validate_budgets(evidence,candidates,depth,chars,sentences=2,compression='none'):\n"
    "    return "
    "dict(evidence_count=evidence,candidate_count=candidates,retrieval_depth=depth,context_chars=chars,max_sentences=sentences,compression=compression)\n",
    "W08-Q087": "def dedupe_evidence(rows):\n"
    "    seen=set();kept=[];dropped=[]\n"
    "    for r in rows:\n"
    "        if r['document_id'] in seen:dropped.append(r['id'])\n"
    "        else:seen.add(r['document_id']);kept.append(r)\n"
    "    return kept,dropped\n",
    "W08-Q088": "def sentence_spans(text):\n"
    "    return ((0,len(text.strip())),) if text.strip() else ()\n",
    "W08-Q089": "def select_spans(query,text,limit=2,table_row=False):\n"
    "    return ((0,min(len(text),20)),)\n",
    "W08-Q090": "import json\n"
    "def render_context(spans):\n"
    "    return json.dumps([s['quote'] for s in spans])\n",
    "W08-Q091": "def pack_units(units,chars,evidence_count):\n"
    "    selected=[]\n"
    "    for unit in units[:evidence_count]:\n"
    "        for s in unit:\n"
    "            if sum(len(x['quote']) for x in "
    "selected)+len(s['quote'])<=chars:selected.append(dict(s,citation_id=f'S{len(selected)+1}'))\n"
    "    return selected\n",
    "W08-Q092": "def validate_citations(spans,stored,principal,grants):\n    return True\n",
    "W08-Q093": "def support_complete(spans,required):\n"
    "    text=''.join(s['quote'] for s in spans).casefold()\n"
    "    return all(a.casefold() in text for atoms in required.values() for a in "
    "atoms)\n",
    "W08-Q094": "def result_status(candidate_count,span_count):\n"
    "    return 'evidence_available' if span_count else 'no_evidence'\n",
    "W08-Q095": "def unique_records(records):\n"
    "    return list({(r['tenant_id'],r['document_id'],r['version']):r for r in "
    "records}.values())\n",
    "W08-Q096": "import json\ndef decode_unique_json(text):\n    return json.loads(text)\n",
    "W08-Q097": "def joint_pair_ids(rows,limit,expected_count):\n"
    "    return tuple(tuple(r[:limit]) for r in rows)\n",
    "W08-Q098": "def safe_event(fields):\n    return dict(fields)\n",
    "W08-Q099": "import hashlib\n"
    "def request_digest(manifest):\n"
    "    return hashlib.sha256(manifest['corpus'].encode()).hexdigest()\n",
    "W08-Q100": "def paired_metrics(pool,reranked,gold,k):\n"
    "    before=len(set(pool[:k])&gold);after=len(set(reranked[:k])&gold)\n"
    "    return "
    "dict(candidate_recall=1,before_recall=before/len(gold),after_recall=after/len(gold),before_precision=before/len(pool[:k]),after_precision=after/len(reranked[:k]))\n",
}


def exercise(q: Question) -> Exercise:
    return {"id": q["id"], "checks": q["checks"]}


def test_bank_distribution_and_teaching_context() -> None:
    assert BANK["schema_version"] == 1
    assert BANK["week"] == 8
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
        f"W08-Q{i:03d}" for i in range(1, 101)
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


def test_composed_evidence_contracts() -> None:
    wanted = {
        "W08-Q085",
        "W08-Q087",
        "W08-Q089",
        "W08-Q091",
        "W08-Q092",
        "W08-Q093",
        "W08-Q094",
        "W08-Q099",
        "W08-Q100",
    }
    source = "\n".join(q["reference"] for q in CODING if q["id"] in wanted)
    checks: list[Check] = [
        {
            "label": "Constraint guard and candidate ceiling",
            "code": "o='CW-1000 Net 30 after approval';assert raises(ValueError,make_query_plan,o,['CW-1000 Net 15 after approval'])\nm=paired_metrics(['noise','row','clause'],['clause','row','noise'],{'row','clause','link'},3);assert m['candidate_recall']==2/3 and m['after_recall']==2/3",
        },
        {
            "label": "Complementary clauses survive exact deduplication",
            "code": "a=dict(id='row',tenant_id='N',document_id='D',version='1',digest='h',text='1000 kg');b=dict(a,id='clause',text='Net 30 after approval');c=dict(a,id='link',text='Schedule A uses that condition');r,d=dedupe_evidence([a,b,dict(b,id='copy'),c]);assert [x['id'] for x in r]==['row','clause','link'] and d==['copy']",
        },
        {
            "label": "Exact valid citation can lose a condition",
            "code": "t='Payment is due. Except disputed invoices require approval.';a,b=select_spans('payment due',t,1)[0];r=dict(id='x',tenant_id='N',document_id='D',version='1',digest='h',text=t,metadata={});s=dict(citation_id='S1',chunk=r,start=a,end=b,quote=t[a:b]);g={('alice','N','D','1')};assert validate_citations([s],[r],'alice',g)\nassert support_complete([dict(evidence_key='D/1/1',quote=s['quote'])],{'D/1/1':['Except disputed invoices']}) is False and raises(ValueError,validate_citations,[s],[r],'alice',set())",
        },
        {
            "label": "Serialized admission and availability differ from completeness",
            "code": "s=dict(tenant_id='N',document_id='D',version='1',locations=[],quote='row');assert pack_units([[s]],2,1)==[] and result_status(1,0)=='context_budget_exhausted'\nout=pack_units([[dict(s,quote='x'*1000)],[s,s]],1000,1);assert len(out)==2 and [x['citation_id'] for x in out]==['S1','S2'] and len(render_context(out))<=1000 and result_status(2,len(out))=='evidence_available'",
        },
        {
            "label": "Whole request identity and own-source support",
            "code": "m=dict(corpus='c',partition='p',query_digests=['o','v'],retrieval_manifests=['r'],reranker={'id':'rules'},config={'chars':1400},dedup='d',context='x',answer='a');assert request_digest(m)!=request_digest(dict(m,config={'chars':300})) and request_digest(m)!=request_digest(dict(m,query_digests=['v','o']))\nassert support_complete([{'evidence_key':'D/1/2','quote':'Net 30'}],{'D/1/1':['Net 30']}) is False",
        },
    ]
    result = asyncio.run(
        grade_submission(source, {"id": "evidence-contracts", "checks": checks})
    )
    assert result["passed"] == 5, result


def test_complete_paper_and_stale_result_contracts() -> None:
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required for JavaScript paper/scoring checks.")
    completed = subprocess.run(
        [node, "scripts/verify_assessment.mjs", "assessments/week-08.json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "1,000 balanced reproducible papers" in completed.stdout
