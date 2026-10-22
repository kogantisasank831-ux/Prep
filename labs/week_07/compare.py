"""Run sparse, dense and RRF on one authorized frozen chunk snapshot."""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from statistics import mean

from labs.week_05.metrics import evaluate_ranking
from labs.week_05.retrieval import (
    LocalEmbeddingAdapter,
    VectorInvariantError,
    cosine_similarity,
)
from labs.week_07.fixtures import (
    PRINCIPAL,
    access_policy,
    denied_code_match,
    frozen_chunks,
    quarantine_summary,
)
from labs.week_07.retrieval import (
    AuthorizedCorpus,
    BM25Config,
    DEFAULT_TOKEN_CONTRACT,
    DemoDenseAdapter,
    DenseAdapter,
    DenseConfig,
    FusionConfig,
    FusedCandidate,
    ManifestCompatibilityError,
    MetadataFilter,
    RetrievalRequest,
    RankedCandidate,
    SourceChunk,
    corpus_fingerprint,
    dense_candidates,
    digest_text,
    hybrid_candidates,
    make_manifest,
    sparse_candidates,
)


@dataclass(frozen=True)
class PracticeCase:
    query_id: str
    category: str
    text: str
    filters: tuple[MetadataFilter, ...]
    support: tuple[tuple[str, tuple[str, ...]], ...]


def load_cases(path: Path) -> tuple[PracticeCase, ...]:
    if path.stat().st_size > 64 * 1024:
        raise ValueError("practice query fixture exceeds 64 KiB")
    cases: list[PracticeCase] = []
    seen: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        item = json.loads(line)
        if not isinstance(item, dict) or set(item) != {
            "query_id",
            "split",
            "category",
            "query",
            "filters",
            "support",
        }:
            raise ValueError("unexpected query fields")
        if (
            item["split"] != "practice"
            or any(
                not isinstance(item[k], str) or not item[k].strip()
                for k in ("query_id", "category", "query")
            )
            or item["query_id"] in seen
            or not isinstance(item["filters"], dict)
            or not isinstance(item["support"], dict)
        ):
            raise ValueError("invalid practice query")
        filters: list[MetadataFilter] = []
        for key, value in item["filters"].items():
            if not isinstance(value, str):
                raise ValueError("filter value must be a string")
            filters.append(MetadataFilter(key, value))
        support: list[tuple[str, tuple[str, ...]]] = []
        for key, atoms in item["support"].items():
            if (
                not key.strip()
                or not isinstance(atoms, list)
                or not atoms
                or any(not isinstance(atom, str) or not atom.strip() for atom in atoms)
            ):
                raise ValueError("invalid support labels")
            support.append((key, tuple(atoms)))
        cases.append(
            PracticeCase(
                item["query_id"],
                item["category"],
                item["query"],
                tuple(sorted(filters, key=lambda f: f.field)),
                tuple(sorted(support)),
            )
        )
        seen.add(item["query_id"])
    if not cases:
        raise ValueError("practice queries must be nonempty")
    return tuple(cases)


class LocalCosineAdapter:
    """Small pairwise reference; it does not measure an optimized dense index."""

    def __init__(
        self, backend: LocalEmbeddingAdapter, *, minimum_score: float = 0.0
    ) -> None:
        self.backend = backend
        self.identity = backend.identity
        self._config = DenseConfig(
            self.identity.model_id,
            self.identity.artifact_digest,
            self.identity.runtime_version,
            self.identity.preprocessing_version,
            "cosine",
            minimum_score,
            dimension=self.identity.dimension,
        )
        self._config.fingerprint()

    @property
    def config(self) -> DenseConfig:
        if self.backend.identity != self.identity:
            raise ManifestCompatibilityError("local encoder identity changed")
        return self._config

    def score(self, query_text: str, chunk_text: str) -> float:
        self.config.fingerprint()
        queries = self.backend.embed_queries((query_text,))
        documents = self.backend.embed_documents((chunk_text,))
        if (
            len(queries) != 1
            or len(documents) != 1
            or len(queries[0]) != self.identity.dimension
            or len(documents[0]) != self.identity.dimension
        ):
            raise VectorInvariantError("local embedding batch shape mismatch")
        self.config.fingerprint()
        return cosine_similarity(queries[0], documents[0])


def measure_case(
    case: PracticeCase,
    eligible: tuple[SourceChunk, ...],
    returned: tuple[SourceChunk, ...],
    *,
    k: int,
) -> dict[str, object]:
    by_key = {dict(chunk.metadata)["evidence_key"]: chunk for chunk in eligible}
    if len(by_key) != len(eligible) or any(
        key not in by_key for key, _ in case.support
    ):
        raise ValueError(
            "labels must resolve uniquely inside the authorized/filter snapshot"
        )
    for key, atoms in case.support:
        if any(atom.casefold() not in by_key[key].text.casefold() for atom in atoms):
            raise ValueError("label atom is absent from its declared evidence chunk")
    gold_ids = frozenset(by_key[key].chunk_id for key, _ in case.support)
    metrics = evaluate_ranking([chunk.chunk_id for chunk in returned], gold_ids, k=k)
    text_by_key = {
        dict(chunk.metadata)["evidence_key"]: chunk.text.casefold()
        for chunk in returned
    }
    complete = (
        all(
            key in text_by_key
            and all(atom.casefold() in text_by_key[key] for atom in atoms)
            for key, atoms in case.support
        )
        if case.support
        else None
    )
    same_sources = {
        (chunk.tenant_id, chunk.document_id, chunk.document_version)
        for chunk in returned
    }
    return {
        **asdict(metrics),
        "support_complete": complete,
        "same_source_repeat_fraction": (len(returned) - len(same_sources))
        / len(returned)
        if returned
        else 0.0,
        "returned_evidence_keys": [
            dict(chunk.metadata)["evidence_key"] for chunk in returned
        ],
    }


def run_comparison(
    adapter: DenseAdapter | None = None,
    *,
    top_k: int = 3,
    candidate_depth: int = 5,
    rank_constant: int = 60,
) -> dict[str, object]:
    adapter = adapter or DemoDenseAdapter()
    initial_config = adapter.config
    path = Path(__file__).with_name("queries.jsonl")
    cases = load_cases(path)
    chunks = frozen_chunks()
    access = access_policy(chunks)
    fusion = FusionConfig(rank_constant)
    mode_rows: dict[str, list[dict[str, object]]] = defaultdict(list)
    for case in cases:
        request = RetrievalRequest(PRINCIPAL, case.text, top_k, case.filters)
        # The denied distractor is present at the boundary, never in either scored set.
        corpus = AuthorizedCorpus.build(request, (*chunks, denied_code_match()), access)
        index = corpus.bm25(DEFAULT_TOKEN_CONTRACT, BM25Config())
        manifest = make_manifest(
            corpus,
            DEFAULT_TOKEN_CONTRACT,
            BM25Config(),
            adapter,
            fusion,
            candidate_depth=candidate_depth,
            top_k=top_k,
        )
        rankings: dict[str, tuple[RankedCandidate | FusedCandidate, ...]] = {
            "sparse": sparse_candidates(request, corpus, index),
            "dense": dense_candidates(request, corpus, adapter),
            "hybrid": hybrid_candidates(
                request, corpus, index, adapter, fusion, candidate_depth=candidate_depth
            ),
        }
        for mode, ranked in rankings.items():
            result = measure_case(
                case, corpus.chunks, tuple(item.chunk for item in ranked), k=top_k
            )
            provenance = []
            for item in ranked:
                if mode == "hybrid":
                    # FusedCandidate's contributors are inspected only for fused results.
                    assert isinstance(item, FusedCandidate)
                    provenance.append(
                        {
                            "chunk_id": item.chunk.chunk_id,
                            "rank": item.rank,
                            "rrf_score": item.score,
                            "contributors": [asdict(c) for c in item.contributors],
                        }
                    )
            mode_rows[mode].append(
                {
                    "query_id": case.query_id,
                    "category": case.category,
                    "manifest_fingerprint": manifest.fingerprint(),
                    "corpus_fingerprint": manifest.corpus_fingerprint,
                    "eligible_chunk_count": len(corpus.chunks),
                    **result,
                    "ranking": [
                        {
                            "chunk_id": item.chunk.chunk_id,
                            "rank": item.rank,
                            "score": item.score,
                            "document_id": item.chunk.document_id,
                            "version": item.chunk.document_version,
                            "source_locations": json.loads(
                                dict(item.chunk.metadata)["source_locations"]
                            ),
                        }
                        for item in ranked
                    ],
                    "fusion_provenance": provenance,
                }
            )
    if adapter.config != initial_config:
        raise ManifestCompatibilityError(
            "dense configuration changed across the comparison"
        )
    results: list[dict[str, object]] = []
    for mode, rows in mode_rows.items():
        labelled = [row for row in rows if row["relevant_count"]]

        def mean_field(group: list[dict[str, object]], field: str) -> float | None:
            numbers = [
                value for row in group if isinstance(value := row[field], (int, float))
            ]
            return mean(numbers) if numbers else None

        categories = sorted({str(row["category"]) for row in rows})
        results.append(
            {
                "mode": mode,
                "labelled_query_count": len(labelled),
                "no_gold_query_count": len(rows) - len(labelled),
                "macro_precision_at_k": mean_field(labelled, "precision_at_k"),
                "macro_recall_at_k": mean_field(labelled, "recall_at_k"),
                "mrr_at_k": mean_field(labelled, "reciprocal_rank_at_k"),
                "mean_binary_ndcg_at_k": mean_field(labelled, "ndcg_at_k"),
                "support_complete_fraction": mean_field(labelled, "support_complete"),
                "empty_result_count": sum(row["returned_count"] == 0 for row in rows),
                "no_gold_queries_with_candidates": sum(
                    bool(row["returned_count"])
                    for row in rows
                    if not row["relevant_count"]
                ),
                "category_recall": {
                    category: mean_field(
                        [row for row in rows if row["category"] == category],
                        "recall_at_k",
                    )
                    for category in categories
                },
                "queries": rows,
            }
        )
    return {
        "schema": "week07-practice-comparison/1.0.0",
        "scope": "synthetic visible practice; default dense path is a teaching feature scorer",
        "source_count": len(
            {
                (chunk.tenant_id, chunk.document_id, chunk.document_version)
                for chunk in chunks
            }
        ),
        "chunk_count": len(chunks),
        "query_count": len(cases),
        "top_k": top_k,
        "candidate_depth": candidate_depth,
        "fusion": asdict(fusion),
        "dense": asdict(initial_config),
        "token_contract": asdict(DEFAULT_TOKEN_CONTRACT),
        "bm25": asdict(BM25Config()),
        "full_corpus_fingerprint": corpus_fingerprint(chunks),
        "metadata_policy": "curated-synthetic-fixture-labels/1.0.0",
        "candidate_policy": "strictly above zero for sparse; dense floor in its config",
        "query_fixture_digest": digest_text(path.read_text(encoding="utf-8")),
        "quarantined": quarantine_summary(),
        "unmeasured": [
            "real-model quality",
            "latency",
            "actual sparse/dense index memory",
            "generated-answer quality",
        ],
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--candidate-depth", type=int, default=5)
    parser.add_argument("--rank-constant", type=int, default=60)
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--model-directory", type=Path)
    parser.add_argument("--model-id", default="reviewed-local-model")
    parser.add_argument("--query-prefix", default="")
    parser.add_argument("--document-prefix", default="")
    parser.add_argument("--dense-min-score", type=float, default=0.0)
    args = parser.parse_args()
    adapter: DenseAdapter = DemoDenseAdapter()
    if args.model_directory is not None:
        from labs.week_05.local_model import LocalSentenceTransformer

        adapter = LocalCosineAdapter(
            LocalSentenceTransformer.from_directory(
                args.model_directory,
                model_id=args.model_id,
                query_prefix=args.query_prefix,
                document_prefix=args.document_prefix,
            ),
            minimum_score=args.dense_min_score,
        )
    elif args.dense_min_score != 0.0:
        parser.error("--dense-min-score applies only to an explicit local model")
    report = run_comparison(
        adapter,
        top_k=args.top_k,
        candidate_depth=args.candidate_depth,
        rank_constant=args.rank_constant,
    )
    if args.summary:
        results = report["results"]
        assert isinstance(results, list)
        for result in results:
            result.pop("queries")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
