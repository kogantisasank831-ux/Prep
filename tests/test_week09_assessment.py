"""Week 9 bank content, actual Python checks and shared paper/scoring contracts."""

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


BANK = cast(Bank, json.loads((ROOT / "assessments/week-09.json").read_text()))
CODING = [q for q in BANK["questions"] if q["type"] == "code"]
MUTANTS = {
    "W09-Q081": "import re\n"
    "def normalize_answer(text):\n"
    "    return re.sub(r'[^a-z0-9 ]','',text.lower()).strip()\n",
    "W09-Q082": "def exact_answer(answer,references):\n"
    "    return answer.lower().strip()==references[0].lower().strip()\n",
    "W09-Q083": "def atom_fraction(answer,atoms):\n"
    "    return 1.0 if any(a in answer for a in atoms) else 0.0\n",
    "W09-Q084": "def ranking_stats(ranked,gold,k):\n"
    "    hits=len(set(ranked[:k])&gold)\n"
    "    return "
    "dict(precision=hits/len(ranked[:k]),recall=hits/len(gold),reciprocal_rank=hits/k)\n",
    "W09-Q085": "def dcg_at_k(grades,k):\n    return float(sum(grades[:k]))\n",
    "W09-Q086": "def graded_ndcg(ranked,grades,k):\n"
    "    from math import log2\n"
    "    picked=[grades.get(x,0) for x in ranked[:k]]\n"
    "    ideal=sorted(picked,reverse=True)\n"
    "    d=lambda v:sum((2**g-1)/log2(i+2) for i,g in enumerate(v))\n"
    "    return d(picked)/d(ideal) if d(ideal) else 1.0\n",
    "W09-Q087": "def mean_observed(values):\n"
    "    kept=[x for x in values if x]\n"
    "    return sum(kept)/len(kept) if kept else 0.0\n",
    "W09-Q088": "def abstention_rate(cases):\n"
    "    return sum(not c['has_evidence'] for c in cases)/len(cases) if cases else "
    "1.0\n",
    "W09-Q089": "def citation_counts(validity):\n"
    "    return dict(count=len(validity),invalid=0,valid_fraction=1.0)\n",
    "W09-Q090": "def context_metrics(selected,gold):\n"
    "    docs={x[1] for x in selected};expected={x[1] for x in "
    "gold};hits=len(docs&expected)\n"
    "    return dict(precision=hits/len(docs) if docs else "
    "1,recall=hits/len(expected) if expected else 1)\n",
    "W09-Q091": "def support_complete(spans,expected):\n"
    "    text=' '.join(s['quote'] for s in spans).casefold()\n"
    "    return all(a.casefold() in text for atoms in expected.values() for a in "
    "atoms)\n",
    "W09-Q092": "def audit_units(expected,raw,parsed,chunks):\n"
    "    return dict(parsed_atom_recall=1.0,chunk_unit_recall=1.0)\n",
    "W09-Q093": "def failure_flags(state):\n"
    "    return [] if state['traceable'] else ['candidate_miss']\n",
    "W09-Q094": "def make_pending(records):\n"
    "    return [dict(r,status='reviewed',scores={'answer_correctness':5}) for r in "
    "records]\n",
    "W09-Q095": "def valid_review(review,expected):\n"
    "    return review['query_id']==expected['query_id']\n",
    "W09-Q096": "def summarize_ratings(records,reviews):\n"
    "    return "
    "dict(reviewed_count=len(reviews),pending_count=len(records)-len(reviews),groups={})\n",
    "W09-Q097": "def paired_changes(baseline,treatment):\n"
    "    return "
    "dict(lost_support=[],gained_support=[],exact_match_gains=[b['query_id'] for a,b "
    "in zip(baseline,treatment) if b['exact_match'] and not a['exact_match']])\n",
    "W09-Q098": "def grouped_splits(rows):\n    return {r['group']:r['split'] for r in rows}\n",
    "W09-Q099": "import hashlib\n"
    "def case_digest(record):\n"
    "    return hashlib.sha256(record['query_id'].encode()).hexdigest()\n",
    "W09-Q100": "import hashlib\n"
    "def run_identity(dataset,system,normalization):\n"
    "    return hashlib.sha256(dataset['corpus_digest'].encode()).hexdigest()\n",
}


def exercise(q: Question) -> Exercise:
    return {"id": q["id"], "checks": q["checks"]}


def test_bank_distribution_and_teaching_context() -> None:
    assert BANK["schema_version"] == 1
    assert BANK["week"] == 9
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
        f"W09-Q{i:03d}" for i in range(1, 101)
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


def test_composed_evaluation_contracts() -> None:
    wanted = {
        "W09-Q082",
        "W09-Q083",
        "W09-Q084",
        "W09-Q086",
        "W09-Q090",
        "W09-Q091",
        "W09-Q092",
        "W09-Q093",
        "W09-Q094",
        "W09-Q095",
        "W09-Q096",
        "W09-Q097",
        "W09-Q099",
    }
    source = "\n".join(q["reference"] for q in CODING if q["id"] in wanted)
    checks: list[Check] = [
        {
            "label": "Independent ranking arithmetic and proxy limits",
            "code": "from math import isclose,log2\nm=ranking_stats(['noise','a','b'],{'a','b','c'},3);assert m['precision']==2/3 and m['recall']==2/3 and m['reciprocal_rank']==.5\nassert isclose(graded_ndcg(['b','a'],{'a':3,'b':1},2),(1+7/log2(3))/(7+1/log2(3))) and atom_fraction('Net 30 does not apply',['Net 30'])==1 and not exact_answer('Net 15',['Net 30'])",
        },
        {
            "label": "Independent source labels expose a lost chunk",
            "code": "k=('N','D','1','b8');e={k:['Net 30','approval']};raw={k:'Net 30 after approval'};m=audit_units(e,raw,raw,[]);assert m=={'parsed_atom_recall':1,'chunk_unit_recall':0}\nforeign=('S','D','1','b8');assert context_metrics([foreign],{k})['recall']==0 and support_complete([dict(key=foreign,quote=raw[k])],e) is False and raises(ValueError,audit_units,{k:['invented']},raw,raw,[])",
        },
        {
            "label": "Same retrieval can hide a harmful exact-match gain",
            "code": "a=[dict(query_id='Q',support_complete=True,exact_match=False)];b=[dict(query_id='Q',support_complete=False,exact_match=True)];o=paired_changes(a,b);assert o['lost_support']==o['exact_match_gains']==['Q']\ns=dict(answerable=True,candidate_recall=1,ranked_recall=1,context_complete=False,answer_coverage=.5,citation_count=1,invalid_count=0,traceable=True);assert failure_flags(s)==['context_loss']",
        },
        {
            "label": "Observation changes invalidate prior review binding",
            "code": "r=dict(query_id='Q',run_id='r',answer='Net 30');r['record_digest']=case_digest(r);p=make_pending([r])[0];assert valid_review(p,r) is True\nchanged=dict(r,answer='Net 15');changed['record_digest']=case_digest(changed);assert r['record_digest']!=changed['record_digest'] and raises(ValueError,valid_review,p,changed)",
        },
        {
            "label": "Actual rating coverage remains separate from group counts",
            "code": "r=dict(query_id='Q',run_id='r',record_digest='d');p=make_pending([r])[0];h=dict(p,status='reviewed',reviewer_kind='human',reviewer_id='synthetic-test',rationale='Test input, not a claimed actual review.',scores={a:4 for a in p['scores']});m=dict(h,reviewer_kind='llm',reviewer_id='fake-model',judge_prompt_version='v1');assert valid_review(h,r) and valid_review(m,r)\no=summarize_ratings([r],[p,h,m]);assert o['reviewed_count']==1 and o['pending_count']==0 and len(o['groups'])==2 and raises(ValueError,summarize_ratings,[r],[h,h])",
        },
    ]
    result = asyncio.run(
        grade_submission(source, {"id": "evaluation-contracts", "checks": checks})
    )
    assert result["passed"] == 5, result


def test_complete_paper_and_stale_result_contracts() -> None:
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required for JavaScript paper/scoring checks.")
    completed = subprocess.run(
        [node, "scripts/verify_assessment.mjs", "assessments/week-09.json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "1,000 balanced reproducible papers" in completed.stdout
