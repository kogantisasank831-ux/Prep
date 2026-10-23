"""Week 3 bank content, actual Python checks and shared paper/scoring contracts."""

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


BANK = cast(Bank, json.loads((ROOT / "assessments/week-03.json").read_text()))
CODING = [q for q in BANK["questions"] if q["type"] == "code"]
MUTANTS = {
    "W03-Q081": "def remaining_budget(context,prompt_tokens,output_reserve):\n    return context-prompt_tokens\n",
    "W03-Q082": "import math\ndef stable_softmax(logits):\n    weights=[math.exp(x) for x in logits]\n    return [x/sum(weights) for x in weights]\n",
    "W03-Q083": "def scale_logits(logits,temperature):\n    return [x*temperature for x in logits]\n",
    "W03-Q084": "def top_k_ids(scores,k):\n    return list(range(len(scores)))[:k]\n",
    "W03-Q085": "def nucleus_ids(probabilities,p):\n    return [i for i,x in enumerate(probabilities) if x>=p]\n",
    "W03-Q086": "def greedy_id(logits):\n    return logits.index(min(logits))\n",
    "W03-Q087": "def causal_mask(length):\n    return [[j<i for j in range(length)] for i in range(length)]\n",
    "W03-Q088": "def mix_values(weights,values):\n    return [sum(row[j] for row in values)/len(values) for j in range(len(values[0]))]\n",
    "W03-Q089": "def lookup_embeddings(token_ids,table):\n    return [table[i] for i in token_ids]\n",
    "W03-Q090": "def attention_scores(query,keys):\n    return [sum(a*b for a,b in zip(query,k)) for k in keys]\n",
    "W03-Q091": "def residual_add(state,update):\n    return list(update)\n",
    "W03-Q092": "import json\ndef canonical_json(value):\n    return json.dumps(value,sort_keys=True)\n",
    "W03-Q093": "import hashlib\ndef prompt_sha256(prompt):\n    return hashlib.sha256(prompt.strip().encode('utf-8')).hexdigest()\n",
    "W03-Q094": "def valid_baseline(settings):\n    return settings.get('context_size')==4096 and settings.get('max_output_tokens')==512\n",
    "W03-Q095": "def allowed_origin(url):\n    return isinstance(url,str) and url.startswith('http://127.0.0.1:')\n",
    "W03-Q096": "def token_metric(value):\n    return {'value':value or 0,'unit':'tokens','unavailable_reason':None}\n",
    "W03-Q097": "def completion_text(payload,expected_model):\n    return payload['choices'][0]['message']['content']\n",
    "W03-Q098": "def trial_schedule(case_ids):\n    return [(c,n) for c in sorted(case_ids) for n in (1,2,3)]\n",
    "W03-Q099": "def add_record(records,record):\n    return [*records,record]\n",
    "W03-Q100": "def criterion_total(scores):\n    return sum(s or 0 for s in scores),2*len(scores)\n",
}


def exercise(q: Question) -> Exercise:
    return {"id": q["id"], "checks": q["checks"]}


def test_bank_distribution_and_teaching_context() -> None:
    assert BANK["schema_version"] == 1
    assert BANK["week"] == 3
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
        f"W03-Q{i:03d}" for i in range(1, 101)
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


def test_independent_numeric_properties() -> None:
    by_id = {q["id"]: q for q in CODING}
    source = "\n".join(
        by_id[qid]["reference"]
        for qid in ["W03-Q081", "W03-Q082", "W03-Q087", "W03-Q088", "W03-Q090"]
    )
    checks: list[Check] = [
        {
            "label": "Shared context arithmetic",
            "code": "assert remaining_budget(4096,3500,512)==84",
        },
        {
            "label": "Softmax shift invariance",
            "code": "import math\na=stable_softmax([1,2,3]);b=stable_softmax([10001,10002,10003]);assert len(a)==len(b)==3 and all(math.isclose(x,y,abs_tol=1e-12) for x,y in zip(a,b))",
        },
        {
            "label": "Causal triangle",
            "code": "m=causal_mask(9);assert sum(sum(row) for row in m)==45 and m[5]==[True]*6+[False]*3",
        },
        {
            "label": "Independent value arithmetic",
            "code": "assert mix_values([.5,.5],[[3,0],[-1,4]])==[1,2]",
        },
        {
            "label": "Width-four attention scale",
            "code": "assert attention_scores([1,2,0,0],[[2,3,0,0],[0,-1,0,0]])==[4,-1]",
        },
    ]
    result = asyncio.run(
        grade_submission(source, {"id": "numeric-properties", "checks": checks})
    )
    assert result["passed"] == 5, result


def test_complete_paper_and_stale_result_contracts() -> None:
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required for JavaScript paper/scoring checks.")
    completed = subprocess.run(
        [node, "scripts/verify_assessment.mjs", "assessments/week-03.json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "1,000 balanced reproducible papers" in completed.stdout
