"""Small explicit metrics; lexical proxies are not semantic correctness judges."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from math import log2, pow
import re


NORMALIZATION = "strip-S-labels/casefold/collapse-whitespace/v1"


def normalize_answer(value: str) -> str:
    """Preserve punctuation, digits, negation and units; remove display S-labels only."""
    return " ".join(re.sub(r"\[S[1-9][0-9]*\]", "", value).casefold().split())


def exact_match(answer: str, references: Sequence[str]) -> bool:
    if not references or any(not reference.strip() for reference in references):
        raise ValueError("exact match requires nonblank reference alternatives")
    return normalize_answer(answer) in {
        normalize_answer(reference) for reference in references
    }


def atom_coverage(answer: str, atoms: Sequence[str]) -> float | None:
    """Substring coverage only: 'not Net 30' still contains 'Net 30'."""
    if not atoms:
        return None
    normalized = normalize_answer(answer)
    return sum(normalize_answer(atom) in normalized for atom in atoms) / len(atoms)


def graded_ndcg(
    ranked_ids: Sequence[str], grades: Mapping[str, int], *, k: int
) -> float | None:
    """Teaching metric with gain 2**grade-1; the run uses binary Week 5 metrics."""
    if type(k) is not int or k < 1 or len(set(ranked_ids)) != len(ranked_ids):
        raise ValueError("positive integer k and unique ranking IDs required")
    if any(type(grade) is not int or not 0 <= grade <= 3 for grade in grades.values()):
        raise ValueError("this contract accepts integer relevance grades 0 to 3")
    ideal_grades = sorted(grades.values(), reverse=True)[:k]
    ideal = sum(
        (pow(2.0, grade) - 1) / log2(rank + 1)
        for rank, grade in enumerate(ideal_grades, 1)
    )
    if not ideal:
        return None
    dcg = sum(
        (pow(2.0, grades.get(key, 0)) - 1) / log2(rank + 1)
        for rank, key in enumerate(ranked_ids[:k], 1)
    )
    return dcg / ideal
