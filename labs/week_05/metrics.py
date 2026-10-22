"""Binary relevance metrics for labelled retrieval; no model is required."""

from __future__ import annotations

from dataclasses import dataclass
from math import log2
from collections.abc import Sequence


@dataclass(frozen=True, slots=True)
class RetrievalMetrics:
    precision_at_k: float
    recall_at_k: float | None
    reciprocal_rank_at_k: float | None
    ndcg_at_k: float | None
    returned_count: int
    relevant_count: int


def evaluate_ranking(
    ranked_ids: Sequence[str], relevant_ids: frozenset[str], *, k: int
) -> RetrievalMetrics:
    """Use P@k denominator k; undefined relevance metrics are null for no-gold cases.

    Rank IDs and relevance labels must use the same granularity and authorised
    source universe. This helper cannot establish either of those facts itself.
    """
    if type(k) is not int or k < 1:
        raise ValueError("k must be a positive integer")
    if len(set(ranked_ids)) != len(ranked_ids):
        raise ValueError("ranked IDs must not repeat")
    if any(not isinstance(value, str) or not value.strip() for value in ranked_ids):
        raise ValueError("ranked IDs must be non-blank strings")
    if any(not isinstance(value, str) or not value.strip() for value in relevant_ids):
        raise ValueError("relevant IDs must be non-blank strings")
    selected = ranked_ids[:k]
    hits = [rank for rank, item in enumerate(selected, 1) if item in relevant_ids]
    precision = len(hits) / k
    if not relevant_ids:
        return RetrievalMetrics(precision, None, None, None, len(selected), 0)
    ideal = sum(1 / log2(rank + 1) for rank in range(1, min(k, len(relevant_ids)) + 1))
    dcg = sum(1 / log2(rank + 1) for rank in hits)
    return RetrievalMetrics(
        precision,
        len(hits) / len(relevant_ids),
        0.0 if not hits else 1 / hits[0],
        dcg / ideal,
        len(selected),
        len(relevant_ids),
    )
