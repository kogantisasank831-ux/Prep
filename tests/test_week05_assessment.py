"""Week 5 bank content, actual Python checks and shared paper/scoring contracts."""

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


BANK = cast(Bank, json.loads((ROOT / "assessments/week-05.json").read_text()))
CODING = [q for q in BANK["questions"] if q["type"] == "code"]
MUTANTS = {
    "W05-Q081": "def finite_vector(values):\n    return tuple(float(x) for x in values)\n",
    "W05-Q082": "def checked_dot(left,right):\n    return sum(x*y for x,y in zip(left,right))\n",
    "W05-Q083": "import math\ndef unit_vector(values):\n    n=math.sqrt(sum(x*x for x in values))\n    return tuple(x/n for x in values)\n",
    "W05-Q084": "def cosine(left,right):\n    return sum(x*y for x,y in zip(left,right))\n",
    "W05-Q085": "def distance(left,right):\n    return sum((x-y)**2 for x,y in zip(left,right))\n",
    "W05-Q086": "def coordinate_bytes(count,dimension,bytes_per_coordinate=4):\n    return count*dimension*bytes_per_coordinate\n",
    "W05-Q087": "def ranked_ids(rows,k):\n    return [x[0] for x in sorted(rows,key=lambda x:-x[1])[:k]]\n",
    "W05-Q088": "def readable_rows(rows,principal,grants):\n    ids={g[2] for g in grants}\n    return [r for r in rows if r['document_id'] in ids]\n",
    "W05-Q089": "def authorized_topk(rows,principal,grants,k,score):\n    ranked=sorted(rows,key=lambda r:(-score(r),r['chunk_id']))[:k]\n    return [r['chunk_id'] for r in ranked if (principal,r['tenant_id'],r['document_id'],r['document_version']) in grants]\n",
    "W05-Q090": "import hashlib\ndef initial_chunk(r):\n    text=r['text'][:1000].strip()\n    return {'chunk_id':r['document_id']+':0','tenant_id':r['tenant_id'],'document_id':r['document_id'],'document_version':r['document_version'],'text':text,'content_digest':hashlib.sha256(text.encode()).hexdigest()}\n",
    "W05-Q091": "import hashlib\ndef embedding_fingerprint(x):\n    return hashlib.sha256(str(x['dimension']).encode()).hexdigest()\n",
    "W05-Q092": "def checked_batch(raw,count,dimension):\n    return tuple(tuple(v) for v in raw[:count])\n",
    "W05-Q093": "import hashlib\ndef chunk_corpus_digest(chunks):\n    return hashlib.sha256(''.join(x['content_digest'] for x in chunks).encode()).hexdigest()\n",
    "W05-Q094": "def precision_at_k(ranked,gold,k):\n    selected=ranked[:k]\n    return sum(x in gold for x in selected)/len(selected) if selected else 0.0\n",
    "W05-Q095": "def recall_at_k(ranked,gold,k):\n    return sum(x in gold for x in ranked[:k])/k if gold else 1.0\n",
    "W05-Q096": "def rr_at_k(ranked,gold,k):\n    hits=[1/(i+1) for i,x in enumerate(ranked[:k]) if x in gold]\n    return sum(hits)/len(hits) if hits else 0.0\n",
    "W05-Q097": "def ndcg_at_k(ranked,gold,k):\n    return sum(x in gold for x in ranked[:k])/len(gold) if gold else 1.0\n",
    "W05-Q098": "def summarize_rr(values):\n    hits=[x for x in values if x]\n    return {'mean_rr':sum(hits)/len(hits) if hits else 0.0,'defined_count':len(hits),'undefined_count':len(values)-len(hits)}\n",
    "W05-Q099": "def neighbor_overlap(exact,approximate,k):\n    return sum(a==b for a,b in zip(exact[:k],approximate[:k]))/k\n",
    "W05-Q100": "def exact_search(query,rows,k):\n    return sorted([(r['chunk_id'],sum(a*b for a,b in zip(query,r['vector']))) for r in rows],key=lambda x:-x[1])[:k]\n",
}


def exercise(q: Question) -> Exercise:
    return {"id": q["id"], "checks": q["checks"]}


def test_bank_distribution_and_teaching_context() -> None:
    assert BANK["schema_version"] == 1
    assert BANK["week"] == 5
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
        f"W05-Q{i:03d}" for i in range(1, 101)
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


def test_composed_retrieval_contracts() -> None:
    by_id = {q["id"]: q for q in CODING}
    source = "\n".join(
        by_id[qid]["reference"]
        for qid in [
            "W05-Q083",
            "W05-Q084",
            "W05-Q085",
            "W05-Q089",
            "W05-Q094",
            "W05-Q095",
            "W05-Q096",
            "W05-Q097",
            "W05-Q098",
            "W05-Q100",
        ]
    )
    checks: list[Check] = [
        {
            "label": "Unit-vector metric identity on independent directions",
            "code": "import math\nfor a,b in [([3,4],[-4,3]),([1,2,3],[3,2,1]),([-1,0],[1,0])]:\n    u,v=unit_vector(a),unit_vector(b)\n    assert math.isclose(distance(u,v)**2,2-2*cosine(u,v),abs_tol=1e-12)",
        },
        {
            "label": "Authorize before even evaluating a score",
            "code": "rows=[{'tenant_id':'N','document_id':'D','document_version':'v1','chunk_id':'N:D:v1:0'}, {'tenant_id':'S','document_id':'D','document_version':'v1','chunk_id':'S:D:v1:0'}]\nseen=[]\ndef score(r):\n    assert r['tenant_id']=='N'\n    seen.append(r['chunk_id']);return .2\nassert authorized_topk(rows,'alice',{('alice','N','D','v1')},1,score)==['N:D:v1:0'] and len(seen)==1",
        },
        {
            "label": "Known lesson ranking, not generated expectations",
            "code": "import math\nr=['P-103','P-101','P-102','P-104'];g={'P-101','P-104'}\nassert precision_at_k(r,g,2)==.5 and recall_at_k(r,g,2)==.5 and rr_at_k(r,g,2)==.5\nassert recall_at_k(r,g,4)==1 and math.isclose(ndcg_at_k(r,g,4),.6509209298071326)",
        },
        {
            "label": "No-gold stays separate from zero-hit",
            "code": "assert recall_at_k(['X'],set(),1) is None and rr_at_k(['X'],set(),1) is None and ndcg_at_k(['X'],set(),1) is None\nassert recall_at_k(['X'],{'A'},1)==0 and rr_at_k(['X'],{'A'},1)==0\nassert summarize_rr([None,0,1])=={'mean_rr':.5,'defined_count':2,'undefined_count':1}",
        },
        {
            "label": "Exact ranking and unchanged synthetic input",
            "code": "rows=[{'chunk_id':'B','vector':[3,4]},{'chunk_id':'A','vector':[6,8]},{'chunk_id':'C','vector':[-3,-4]}]\nr=exact_search([3,4],rows,3)\nassert [x[0] for x in r]==['A','B','C'] and rows[0]['vector']==[3,4]",
        },
    ]
    result = asyncio.run(
        grade_submission(source, {"id": "retrieval-contracts", "checks": checks})
    )
    assert result["passed"] == 5, result


def test_complete_paper_and_stale_result_contracts() -> None:
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required for JavaScript paper/scoring checks.")
    completed = subprocess.run(
        [node, "scripts/verify_assessment.mjs", "assessments/week-05.json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "1,000 balanced reproducible papers" in completed.stdout
