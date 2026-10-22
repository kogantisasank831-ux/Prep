"""Paired same-candidate reranking comparison on the visible Week 7 practice set."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
from statistics import mean

from labs.week_05.metrics import evaluate_ranking
from labs.week_07.compare import PracticeCase, load_cases
from labs.week_07.retrieval import (
    AuthorizedCorpus,
    BM25Config,
    DEFAULT_TOKEN_CONTRACT,
    DemoDenseAdapter,
    FusionConfig,
    RetrievalRequest,
    SourceChunk,
    digest_text,
)
from labs.week_08.data import demo_access, evidence_keys, load_corpus
from labs.week_08.demo import add_model_arguments, select_scorer
from labs.week_08.pipeline import (
    KnowledgeAssistant,
    PairScorer,
    PipelineConfig,
    TeachingPairScorer,
)


def measure_ranking(
    case: PracticeCase,
    eligible: tuple[SourceChunk, ...],
    returned: tuple[SourceChunk, ...],
    *,
    k: int,
) -> dict[str, object]:
    by_key = evidence_keys(eligible)
    for key, atoms in case.support:
        if key not in by_key or any(
            atom.casefold() not in by_key[key].text.casefold() for atom in atoms
        ):
            raise ValueError(
                "practice label does not resolve to its declared eligible evidence"
            )
    gold = frozenset(by_key[key].chunk_id for key, _ in case.support)
    return asdict(evaluate_ranking([item.chunk_id for item in returned], gold, k=k))


def run_comparison(
    scorer: PairScorer | None = None,
    *,
    config: PipelineConfig | None = None,
) -> dict[str, object]:
    scorer = scorer or TeachingPairScorer()
    config = config or PipelineConfig()
    corpus_path = Path(__file__).with_name("corpus.jsonl")
    query_path = Path(__file__).parents[1] / "week_07" / "queries.jsonl"
    ingested = load_corpus(corpus_path)
    access = demo_access()
    assistant = KnowledgeAssistant(
        ingested.chunks, access, scorer=scorer, config=config
    )
    rows: list[dict[str, object]] = []
    for case in load_cases(query_path):
        request = RetrievalRequest(
            "analyst", case.text, config.evidence_count, case.filters
        )
        eligible = AuthorizedCorpus.build(request, ingested.chunks, access).chunks
        result = assistant.ask(request)
        baseline = tuple(
            item.chunk for item in result.candidates[: config.evidence_count]
        )
        reranked = tuple(
            item.chunk for item in result.reranked[: config.evidence_count]
        )
        candidate_metrics = measure_ranking(
            case,
            eligible,
            tuple(item.chunk for item in result.candidates),
            k=config.candidate_count,
        )
        selected_text: dict[str, str] = {}
        for span in result.citations:
            key = dict(span.chunk.metadata)["evidence_key"]
            selected_text[key] = selected_text.get(key, "") + span.quote.casefold()
        support_complete = (
            all(
                key in selected_text
                and all(atom.casefold() in selected_text[key] for atom in atoms)
                for key, atoms in case.support
            )
            if case.support
            else None
        )
        rows.append(
            {
                "query_id": case.query_id,
                "category": case.category,
                "labelled": bool(case.support),
                "candidate_recall": candidate_metrics["recall_at_k"],
                "hybrid": measure_ranking(
                    case, eligible, baseline, k=config.evidence_count
                ),
                "reranked": measure_ranking(
                    case, eligible, reranked, k=config.evidence_count
                ),
                "hybrid_keys": [
                    dict(item.metadata)["evidence_key"] for item in baseline
                ],
                "reranked_keys": [
                    dict(item.metadata)["evidence_key"] for item in reranked
                ],
                "context_keys": list(selected_text),
                "context_support_complete": support_complete,
                "context_chars": len(result.context),
                "span_count": len(result.citations),
                "dropped_duplicate_count": len(result.dropped_duplicate_ids),
                "status": result.status,
                "manifest_fingerprint": result.manifest_fingerprint,
            }
        )
    labelled = [row for row in rows if row["labelled"]]

    def mean_values(values: list[object]) -> float | None:
        numbers = [value for value in values if isinstance(value, (int, float))]
        return mean(numbers) if numbers else None

    quality: dict[str, object] = {
        "candidate_recall": mean_values([row["candidate_recall"] for row in labelled]),
        "context_support_complete_fraction": mean_values(
            [row["context_support_complete"] for row in labelled]
        ),
    }
    for mode in ("hybrid", "reranked"):
        metrics = [row[mode] for row in labelled]
        quality[mode] = {
            key: mean_values([item[key] for item in metrics if isinstance(item, dict)])
            for key in (
                "precision_at_k",
                "recall_at_k",
                "reciprocal_rank_at_k",
                "ndcg_at_k",
            )
        }
    return {
        "schema": "week08-same-pool-comparison/1.0.0",
        "scope": "visible synthetic practice; default reranker uses handwritten teaching rules",
        "query_count": len(rows),
        "labelled_query_count": len(labelled),
        "no_gold_query_count": len(rows) - len(labelled),
        "accepted_documents": ingested.accepted_documents,
        "ingestion_issues": [asdict(issue) for issue in ingested.issues],
        "input_digest": ingested.input_digest,
        "query_digest": digest_text(query_path.read_text(encoding="utf-8")),
        "config": asdict(config),
        "reranker": asdict(scorer.identity),
        "first_stage": {
            "dense": asdict(DemoDenseAdapter().config),
            "bm25": asdict(BM25Config()),
            "token_contract": asdict(DEFAULT_TOKEN_CONTRACT),
            "fusion": asdict(FusionConfig()),
        },
        "quality": quality,
        "unmeasured": [
            "learned reranker quality",
            "generated answer faithfulness",
            "latency",
            "memory",
            "position effects",
        ],
        "queries": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--context-chars", type=int, default=1400)
    parser.add_argument("--compression", choices=("none", "sentences"), default="none")
    add_model_arguments(parser)
    args = parser.parse_args()
    report = run_comparison(
        select_scorer(args, parser),
        config=PipelineConfig(
            context_chars=args.context_chars,
            compression=args.compression,
        ),
    )
    if args.summary:
        report.pop("queries")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
