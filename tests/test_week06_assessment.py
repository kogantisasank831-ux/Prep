"""Week 6 bank content, actual Python checks and shared paper/scoring contracts."""

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


BANK = cast(Bank, json.loads((ROOT / "assessments/week-06.json").read_text()))
CODING = [q for q in BANK["questions"] if q["type"] == "code"]
MUTANTS = {
    "W06-Q081": "def canonical_text(blocks):\n    return ''.join(x.strip() for x in blocks)\n",
    "W06-Q082": "def block_status(block):\n    return 'accepted' if block.get('text') else 'rejected'\n",
    "W06-Q083": "def window_spans(length,width,overlap=0):\n    return [(i,min(i+width,length)) for i in range(0,length,width-overlap)]\n",
    "W06-Q084": "def window_text(text,width,overlap=0):\n    return [text[i:i+width].strip() for i in range(0,len(text),width-overlap)]\n",
    "W06-Q085": "def span_locations(blocks,start,end):\n    return [(i,start,end) for i in range(len(blocks))]\n",
    "W06-Q086": "def sentence_groups(text,target):\n    return [text[i:i+target] for i in range(0,len(text),target)]\n",
    "W06-Q087": "def structure_units(blocks,include_heading=True):\n    return [(b['text'],(b['location'],)) for b in blocks if b['kind']!='heading']\n",
    "W06-Q088": "def shared_terms(left,right):\n    a=left.lower().split();b=right.lower().split()\n    return sum(x in b for x in a)/len(a) if a else 0.0\n",
    "W06-Q089": "def paragraph_groups(paragraphs,scores,threshold):\n    return [' '.join(paragraphs)] if paragraphs else []\n",
    "W06-Q090": "import hashlib\ndef policy_fingerprint(name,version,parameters):\n    return hashlib.sha256(name.encode('utf-8')).hexdigest()\n",
    "W06-Q091": "import hashlib\ndef representation_hash(record):\n    return hashlib.sha256(str(record.get('text','')).encode('utf-8')).hexdigest()\n",
    "W06-Q092": "def child_ids(chunks):\n    return [x['id'] for x in chunks]\n",
    "W06-Q093": "def same_lineage(child,parent):\n    return child['parent']==parent['id']\n",
    "W06-Q094": "def expand_units(ranked_ids,records,can_read):\n    return [records[records[i]['parent']] if records[i]['parent'] else records[i] for i in ranked_ids if can_read(records[i])]\n",
    "W06-Q095": "def admit_context(units,budget):\n    out=[];used=0\n    for x in units:\n        if used+len(x['text'])<=budget:out.append(x['id']);used+=len(x['text'])\n    return out\n",
    "W06-Q096": "def text_storage(chunks):\n    return len('\\n'.join(x['text'] for x in chunks))\n",
    "W06-Q097": "def document_recall(ranked_documents,gold,k):\n    unique=list(dict.fromkeys(ranked_documents))\n    return len(set(unique[:k])&gold)/len(gold) if gold else 1.0\n",
    "W06-Q098": "def support_fraction(context,support):\n    text=' '.join(x['text'] for x in context).lower()\n    atoms=[a for values in support.values() for a in values]\n    return sum(a.lower() in text for a in atoms)/len(atoms) if atoms else 1.0\n",
    "W06-Q099": "def labelled_mean(values):\n    hits=[v for v in values if v]\n    return {'mean':sum(hits)/len(hits) if hits else 0.0,'labelled_count':len(hits),'no_gold_count':len(values)-len(hits)}\n",
    "W06-Q100": "def policy_summary(chunks,dimension,parent_child=False):\n    n=len(chunks)\n    return {'stored_chunk_count':n,'indexed_chunk_count':n,'average_stored_chunk_chars':sum(len(x['text']) for x in chunks)/n if n else 0,'stored_text_utf8_bytes':sum(len(x['text']) for x in chunks),'packed_float32_vector_bytes_estimate':n*dimension*4,'average_tokens':0,'generated_answer_quality':1.0}\n",
}


def exercise(q: Question) -> Exercise:
    return {"id": q["id"], "checks": q["checks"]}


def test_bank_distribution_and_teaching_context() -> None:
    assert BANK["schema_version"] == 1
    assert BANK["week"] == 6
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
        f"W06-Q{i:03d}" for i in range(1, 101)
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


def test_composed_chunking_contracts() -> None:
    source = "\n".join(q["reference"] for q in CODING)
    checks: list[Check] = [
        {
            "label": "Window coverage and exact reconstruction",
            "code": "for length in range(1,30):\n    text='x'*length\n    for width in range(1,8):\n        assert ''.join(window_text(text,width))==text\n        for overlap in range(width):\n            spans=window_spans(length,width,overlap)\n            assert spans[-1][1]==length and all(b<length for a,b in spans[:-1])\n            assert set(i for a,b in spans for i in range(a,b))==set(range(length))",
        },
        {
            "label": "Offsets cite actual trimmed block characters",
            "code": "b=[' ab ','cde'];canonical=canonical_text(b)\nassert canonical=='ab\\ncde' and canonical[1:5]=='b\\ncd'\nassert span_locations(b,1,5)==[(0,1,2),(1,0,2)] and span_locations(b,2,3)==[]",
        },
        {
            "label": "Parent reauthorization before whole-unit admission",
            "code": "p={'id':'P','parent':None,'source':('N','D','1','hash'),'policy':'p','text':'abcde'};c=dict(p,id='C',parent='P',text='abc');records={'P':p,'C':c}\nassert expand_units(['C'],records,lambda r:r['parent'] is not None)==[]\nunits=expand_units(['C','C'],records,lambda r:True)\nassert len(units)==1 and admit_context(units,4)==[] and admit_context(units,5)==['P']",
        },
        {
            "label": "Document recall is not support completeness",
            "code": "assert document_recall(['P-105'],{'P-105'},1)==1\ncontext=[{'document_id':'P-105','text':'product=wire; quantity=1000 kg'}];support={'P-105':['product=wire','Net 30 after inspection approval','controls Schedule A']}\nassert support_fraction(context,support)==0 and support_fraction(context,{}) is None\nassert labelled_mean([0,1,None])=={'mean':.5,'labelled_count':2,'no_gold_count':1}",
        },
        {
            "label": "Parents cost storage but not child-only vectors",
            "code": "chunks=[{'id':'P','parent':None,'text':'é猫'},{'id':'C','parent':'P','text':'é猫'}]\ns=policy_summary(chunks,2,True)\nassert text_storage(chunks)==10 and s['average_stored_chunk_chars']==2 and s['stored_chunk_count']==2 and s['indexed_chunk_count']==1 and s['packed_float32_vector_bytes_estimate']==8\nassert s['average_tokens'] is None and s['generated_answer_quality'] is None",
        },
    ]
    result = asyncio.run(
        grade_submission(source, {"id": "chunking-contracts", "checks": checks})
    )
    assert result["passed"] == 5, result


def test_complete_paper_and_stale_result_contracts() -> None:
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required for JavaScript paper/scoring checks.")
    completed = subprocess.run(
        [node, "scripts/verify_assessment.mjs", "assessments/week-06.json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "1,000 balanced reproducible papers" in completed.stdout
