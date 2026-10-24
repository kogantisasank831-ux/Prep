"""Week 7 bank content, actual Python checks and shared paper/scoring contracts."""

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


BANK = cast(Bank, json.loads((ROOT / "assessments/week-07.json").read_text()))
CODING = [q for q in BANK["questions"] if q["type"] == "code"]
MUTANTS = {
    "W07-Q081": "import re\ndef tokenize_text(text):\n    return tuple(re.findall(r'[a-z0-9]+',str(text).lower()))\n",
    "W07-Q082": "def term_views(text):\n    terms=text.lower().split()\n    return {x:1 for x in terms},tuple(sorted(set(terms)))\n",
    "W07-Q083": "from collections import Counter\ndef corpus_stats(documents):\n    tf=[dict(Counter(x.lower().split())) for x in documents];df=Counter()\n    for counts in tf:df.update(counts)\n    lengths=[sum(x.values()) for x in tf]\n    return {'tf':tf,'df':dict(df),'lengths':lengths,'avgdl':sum(lengths)/len(lengths)}\n",
    "W07-Q084": "import math\ndef positive_idf(total,df):\n    return math.log((total-df+.5)/(df+.5))\n",
    "W07-Q085": "def tf_weight(tf,dl,avgdl,k1=1.2,b=.75):\n    return tf*(k1+1)/(tf+k1*(1-b+b*dl/avgdl))\n",
    "W07-Q086": "def bm25_score(query,documents,index,k1=1.2,b=.75):\n    return float(sum(documents[index].lower().split().count(t) for t in query.lower().split()))\n",
    "W07-Q087": "def canonical_filters(filters):\n    return tuple(sorted(dict(filters).items()))\n",
    "W07-Q088": "def eligible_rows(rows,principal,grants,filters):\n    return [r for r in rows if all(r['metadata'].get(k)==v for k,v in filters)]\n",
    "W07-Q089": "def require_partition(request_principal,request_filters,stored_principal,stored_filters):\n    return True\n",
    "W07-Q090": "def rank_scores(rows,k,minimum_score=0):\n    return [{'id':i,'score':s,'rank':r} for r,(i,s) in enumerate(sorted(rows,key=lambda x:-x[1])[:k],1)]\n",
    "W07-Q091": "def minmax(scores):\n    lo=min(scores.values());hi=max(scores.values())\n    return {k:(v-lo)/(hi-lo) for k,v in scores.items()}\n",
    "W07-Q092": "def fusion_weights(pairs):\n    return dict(pairs)\n",
    "W07-Q093": "def rrf_vote(rank,constant=60,weight=1):\n    return weight/rank\n",
    "W07-Q094": "def validate_votes(rows,weights):\n    return True\n",
    "W07-Q095": "def fuse_votes(rows,weights,constant=60,k=3):\n    totals={}\n    for r in rows:totals[r['id']]=totals.get(r['id'],0)+r['raw_score']\n    return [{'id':i,'score':s,'rank':n,'contributors':[]} for n,(i,s) in enumerate(sorted(totals.items(),key=lambda x:-x[1])[:k],1)]\n",
    "W07-Q096": "def candidate_union(sparse_ids,dense_ids,depth):\n    return list(dict.fromkeys(sparse_ids+dense_ids))[:depth]\n",
    "W07-Q097": "import hashlib\ndef manifest_digest(config):\n    return hashlib.sha256(config['corpus_fingerprint'].encode()).hexdigest()\n",
    "W07-Q098": "def resolve_evidence(eligible,support):\n    text=' '.join(x['text'] for x in eligible).lower()\n    return frozenset(x['id'] for x in eligible if all(a.lower() in text for atoms in support.values() for a in atoms))\n",
    "W07-Q099": "def source_repeat_fraction(rows):\n    return (len(rows)-len({x['document_id'] for x in rows}))/len(rows) if rows else 0.0\n",
    "W07-Q100": "import hashlib\ndef corpus_digest(rows):\n    return hashlib.sha256(''.join(r['source_digest'] for r in rows).encode()).hexdigest()\n",
}


def exercise(q: Question) -> Exercise:
    return {"id": q["id"], "checks": q["checks"]}


def test_bank_distribution_and_teaching_context() -> None:
    assert BANK["schema_version"] == 1
    assert BANK["week"] == 7
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
        f"W07-Q{i:03d}" for i in range(1, 101)
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
    source = "\n".join(
        q["reference"]
        for q in CODING
        if q["id"]
        in {"W07-Q086", "W07-Q088", "W07-Q090", "W07-Q095", "W07-Q096", "W07-Q098"}
    )
    checks: list[Check] = [
        {
            "label": "Independent BM25 arithmetic and unique-query policy",
            "code": "import math\nd=['CW-1000','invoice invoice invoice']\nassert math.isclose(bm25_score('CW-1000',d,0),.8713850269896456)\nassert bm25_score('CW-1000 CW-1000',d,0)==bm25_score('CW-1000',d,0) and bm25_score('CW1000',d,0)==0",
        },
        {
            "label": "Denied source cannot alter eligible statistics",
            "code": "a={'id':'A','tenant_id':'N','document_id':'D','document_version':'1','text':'CW-1000','metadata':{}};denied=dict(a,id='X',tenant_id='S',text='CW-1000 CW-1000 extra');g={('alice','N','D','1')}\nbase=eligible_rows([a],'alice',g,[]);extra=eligible_rows([a,denied],'alice',g,[])\nassert base==extra and corpus_stats([r['text'] for r in base])==corpus_stats([r['text'] for r in extra])",
        },
        {
            "label": "Floor admission before fusion votes",
            "code": "assert rank_scores([('A',0),('B',-1)],3)==[] and fuse_votes([],{'bm25':1,'dense':1})==[]\nassert [x['id'] for x in rank_scores([('A',-.2)],3,-.5)]==['A']",
        },
        {
            "label": "Known RRF winner independent of raw scale",
            "code": "import math\nr=[{'id':'A','snapshot':'a','retriever':'bm25','rank':1,'raw_score':100},{'id':'B','snapshot':'b','retriever':'bm25','rank':2,'raw_score':1},{'id':'B','snapshot':'b','retriever':'dense','rank':1,'raw_score':.8}]\nf=fuse_votes(r,{'bm25':1,'dense':1});assert [x['id'] for x in f]==['B','A'] and math.isclose(f[0]['score'],1/61+1/62)\nr[0]['raw_score']=1000000;assert [x['id'] for x in fuse_votes(r,{'bm25':1,'dense':1})]==['B','A']",
        },
        {
            "label": "Source-bound labels and pre-fusion depth",
            "code": "assert candidate_union(['A','B'],['A','C'],1)==['A']\nrows=[{'id':'A','evidence_key':'D/1/1','text':'row'},{'id':'B','evidence_key':'D/1/2','text':'clause'}]\nassert resolve_evidence(rows,{'D/1/2':['clause']})==frozenset({'B'})\nassert raises(ValueError,resolve_evidence,rows,{'D/1/1':['clause']})",
        },
    ]
    result = asyncio.run(
        grade_submission(source, {"id": "hybrid-contracts", "checks": checks})
    )
    assert result["passed"] == 5, result


def test_complete_paper_and_stale_result_contracts() -> None:
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required for JavaScript paper/scoring checks.")
    completed = subprocess.run(
        [node, "scripts/verify_assessment.mjs", "assessments/week-07.json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "1,000 balanced reproducible papers" in completed.stdout
