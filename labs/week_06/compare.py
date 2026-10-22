"""Compare six policies on one frozen, synthetic parsed collection."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from dataclasses import asdict, dataclass, replace
import json
from pathlib import Path
from statistics import mean

from labs.week_05.retrieval import (
    DemoLocalEmbeddingAdapter,
    EmbeddingModelIdentity,
    LocalEmbeddingAdapter,
    Vector,
    VectorInvariantError,
    cosine_similarity,
    normalize,
)
from labs.week_06.chunking import (
    Chunk,
    ChunkAccessPolicy,
    ChunkCollection,
    ChunkPolicy,
    FixedSizePolicy,
    ManifestCompatibilityError,
    OverlapPolicy,
    ParentChildPolicy,
    ParsedSource,
    SemanticPolicy,
    SentencePolicy,
    SharedTermSimilarity,
    StaticChunkAccessPolicy,
    StructurePolicy,
    authorized_chunks,
    digest_text,
    source_fingerprint,
)
from labs.week_06.fixtures import (
    FIXED_TIME,
    PARSER,
    accepted_sources,
    ocr_review_document,
)


@dataclass(frozen=True)
class PracticeCase:
    query_id: str
    text: str
    support: tuple[tuple[str, tuple[str, ...]], ...]


def load_cases(path: Path) -> tuple[PracticeCase, ...]:
    """Load bounded practice labels; this is not a held-out evaluation set."""
    if path.stat().st_size > 64 * 1024:
        raise ValueError("query fixture exceeds 64 KiB")
    cases: list[PracticeCase] = []
    seen: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        item = json.loads(line)
        if not isinstance(item, dict) or set(item) != {
            "query_id",
            "split",
            "text",
            "support",
        }:
            raise ValueError("unexpected practice query fields")
        query_id, text, support = item["query_id"], item["text"], item["support"]
        if (
            item["split"] != "practice"
            or not isinstance(query_id, str)
            or not query_id.strip()
            or query_id in seen
            or not isinstance(text, str)
            or not text.strip()
            or len(text) > 1000
            or not isinstance(support, dict)
        ):
            raise ValueError("invalid practice query")
        labels: list[tuple[str, tuple[str, ...]]] = []
        for document_id, atoms in support.items():
            if (
                not isinstance(document_id, str)
                or not document_id.strip()
                or not isinstance(atoms, list)
                or not atoms
                or any(not isinstance(atom, str) or not atom.strip() for atom in atoms)
            ):
                raise ValueError("invalid support labels")
            labels.append((document_id, tuple(atoms)))
        cases.append(PracticeCase(query_id, text, tuple(sorted(labels))))
        seen.add(query_id)
    if not cases:
        raise ValueError("practice queries must be non-empty")
    return tuple(cases)


@dataclass(frozen=True)
class TeachingEmbeddingAdapter:
    """Week 5 hand features plus a bias so heading-only chunks are nonzero."""

    identity: EmbeddingModelIdentity = replace(
        DemoLocalEmbeddingAdapter.identity,
        model_id="week06-teaching-features-with-bias",
        preprocessing_version="week05-features-plus-constant-0.1/v1",
        dimension=6,
    )

    def embed_documents(self, texts: Sequence[str]) -> tuple[Vector, ...]:
        return tuple(
            (*vector, 0.1)
            for vector in DemoLocalEmbeddingAdapter().embed_documents(texts)
        )

    def embed_queries(self, texts: Sequence[str]) -> tuple[Vector, ...]:
        return tuple(
            (*vector, 0.1)
            for vector in DemoLocalEmbeddingAdapter().embed_queries(texts)
        )


def policy_candidates() -> tuple[ChunkPolicy, ...]:
    return (
        FixedSizePolicy(120),
        OverlapPolicy(120, 40),
        SentencePolicy(120),
        StructurePolicy(),
        SemanticPolicy(SharedTermSimilarity(), 0.1),
        ParentChildPolicy(),
    )


def select_context(
    ranked: Sequence[Chunk],
    all_chunks: Sequence[Chunk],
    *,
    principal_id: str,
    access: ChunkAccessPolicy,
    budget_chars: int,
) -> tuple[Chunk, ...]:
    """Expand authorized parents, deduplicate, and retain only whole units that fit."""
    if type(budget_chars) is not int or budget_chars < 1:
        raise ValueError("context budget must be a positive character count")
    by_id = {chunk.chunk_id: chunk for chunk in all_chunks}
    selected: list[Chunk] = []
    seen: set[str] = set()
    used = 0
    for hit in ranked:
        if by_id.get(hit.chunk_id) != hit:
            raise ManifestCompatibilityError("ranked hit is outside this collection")
        if not access.can_read(principal_id, hit):
            continue
        candidate = hit
        if hit.parent_chunk_id is not None:
            parent = by_id.get(hit.parent_chunk_id)
            if (
                parent is None
                or parent.parent_chunk_id is not None
                or parent.source_identity != hit.source_identity
                or parent.policy_fingerprint != hit.policy_fingerprint
            ):
                raise ManifestCompatibilityError("invalid parent expansion")
            if not access.can_read(principal_id, parent):
                continue
            candidate = parent
        if candidate.chunk_id in seen:
            continue
        cost = len(candidate.text) + (1 if selected else 0)
        if used + cost <= budget_chars:
            selected.append(candidate)
            seen.add(candidate.chunk_id)
            used += cost
    return tuple(selected)


def normalized_batch(
    vectors: Sequence[Vector], *, count: int, dimension: int
) -> tuple[Vector, ...]:
    if len(vectors) != count or any(len(vector) != dimension for vector in vectors):
        raise VectorInvariantError("embedding batch shape differs from manifest")
    return tuple(normalize(vector) for vector in vectors)


def compare_policy(
    sources: Sequence[ParsedSource],
    cases: Sequence[PracticeCase],
    policy: ChunkPolicy,
    adapter: LocalEmbeddingAdapter,
    *,
    k: int = 3,
    context_budget_chars: int = 800,
) -> dict[str, object]:
    """Measure document recall at a chunk budget and a conservative support proxy."""
    if (
        not sources
        or not cases
        or type(k) is not int
        or k < 1
        or type(context_budget_chars) is not int
        or context_budget_chars < 1
    ):
        raise ValueError("nonempty sources/cases and positive integer k are required")
    # The practice IDs are document-only, so the snapshot must have one tenant/version per ID.
    if len({source.identity.document_id for source in sources}) != len(sources):
        raise ValueError("practice labels require unique document IDs in this snapshot")
    documents = {source.identity.document_id for source in sources}
    if any(
        document_id not in documents
        for case in cases
        for document_id, _ in case.support
    ):
        raise ValueError("practice label refers to a source outside this snapshot")
    collections = tuple(
        ChunkCollection.build(source, policy, created_at=FIXED_TIME)
        for source in sources
    )
    stored = tuple(chunk for collection in collections for chunk in collection.chunks)
    principal = "practice-reviewer"
    access = StaticChunkAccessPolicy(
        frozenset(
            (
                principal,
                source.identity.tenant_id,
                source.identity.document_id,
                source.identity.version,
            )
            for source in sources
        )
    )
    eligible = authorized_chunks(principal, stored, access)
    indexed = (
        tuple(chunk for chunk in eligible if chunk.parent_chunk_id is not None)
        if isinstance(policy, ParentChildPolicy)
        else eligible
    )
    identity = adapter.identity
    vectors = normalized_batch(
        adapter.embed_documents(tuple(chunk.text for chunk in indexed)),
        count=len(indexed),
        dimension=identity.dimension,
    )
    query_vectors = normalized_batch(
        adapter.embed_queries(tuple(case.text for case in cases)),
        count=len(cases),
        dimension=identity.dimension,
    )
    if adapter.identity != identity:
        raise ManifestCompatibilityError("embedding identity changed during comparison")
    rows: list[dict[str, object]] = []
    recalls: list[float] = []
    support_rates: list[float] = []
    for case, query in zip(cases, query_vectors, strict=True):
        ranked = sorted(
            zip(indexed, vectors, strict=True),
            key=lambda item: (-cosine_similarity(query, item[1]), item[0].chunk_id),
        )
        hits = tuple(chunk for chunk, _ in ranked[:k])
        context = select_context(
            hits,
            stored,
            principal_id=principal,
            access=access,
            budget_chars=context_budget_chars,
        )
        retrieved_documents = {hit.source_identity.document_id for hit in hits}
        recall = (
            len(retrieved_documents & dict(case.support).keys()) / len(case.support)
            if case.support
            else None
        )
        # Never combine atoms from different document IDs to manufacture complete evidence.
        complete = []
        for document_id, atoms in case.support:
            text = "\n".join(
                chunk.text
                for chunk in context
                if chunk.source_identity.document_id == document_id
            ).casefold()
            complete.append(all(atom.casefold() in text for atom in atoms))
        support_rate = mean(complete) if complete else None
        if recall is not None:
            recalls.append(recall)
        if support_rate is not None:
            support_rates.append(support_rate)
        rows.append(
            {
                "query_id": case.query_id,
                "ranked_chunk_ids": [hit.chunk_id for hit in hits],
                "retrieved_document_ids": sorted(retrieved_documents),
                "context_chunk_ids": [chunk.chunk_id for chunk in context],
                "context_chars": sum(len(chunk.text) for chunk in context)
                + max(0, len(context) - 1),
                "document_recall_at_chunk_k": recall,
                "complete_support_source_fraction": support_rate,
            }
        )
    return {
        "policy": asdict(policy.identity),
        "corpus_fingerprint": digest_text(
            "\n".join(sorted(source_fingerprint(source) for source in sources))
        ),
        "stored_chunk_count": len(stored),
        "indexed_chunk_count": len(indexed),
        "average_stored_chunk_chars": mean(len(chunk.text) for chunk in stored),
        "average_indexed_chunk_chars": mean(len(chunk.text) for chunk in indexed),
        "stored_text_utf8_bytes": sum(
            len(chunk.text.encode("utf-8")) for chunk in stored
        ),
        "packed_float32_vector_bytes_estimate": len(indexed) * identity.dimension * 4,
        "document_recall_at_chunk_k": mean(recalls) if recalls else None,
        "complete_support_source_fraction": mean(support_rates)
        if support_rates
        else None,
        "labelled_query_count": len(recalls),
        "no_gold_query_count": len(cases) - len(recalls),
        "generated_answer_quality": None,
        "average_tokens": None,
        "queries": rows,
    }


def run_comparison(
    adapter: LocalEmbeddingAdapter | None = None,
    *,
    k: int = 3,
    context_budget_chars: int = 800,
) -> dict[str, object]:
    adapter = adapter or TeachingEmbeddingAdapter()
    cases_path = Path(__file__).with_name("queries.jsonl")
    cases = load_cases(cases_path)
    sources = accepted_sources()
    quarantine = PARSER.parse(ocr_review_document())
    return {
        "schema": "week06-practice-comparison/1.0.0",
        "measurement_scope": "synthetic practice; teaching features unless an explicit local model is supplied",
        "model": asdict(adapter.identity),
        "query_fixture_digest": digest_text(cases_path.read_text(encoding="utf-8")),
        "source_count": len(sources),
        "query_count": len(cases),
        "k_chunks": k,
        "context_budget_chars": context_budget_chars,
        "quarantined": [
            {
                "document_id": "P-106",
                "status": quarantine.status,
                "reasons": quarantine.reasons,
            }
        ],
        "unmeasured": [
            "generated answers/human answer grades",
            "token lengths",
            "latency",
            "actual vector/index/metadata memory",
            "real PDF/OCR accuracy",
        ],
        "results": [
            compare_policy(
                sources,
                cases,
                policy,
                adapter,
                k=k,
                context_budget_chars=context_budget_chars,
            )
            for policy in policy_candidates()
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-directory", type=Path)
    parser.add_argument("--model-id", default="local-week06-model")
    parser.add_argument("--query-prefix", default="")
    parser.add_argument("--document-prefix", default="")
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--context-budget-chars", type=int, default=800)
    parser.add_argument("--summary", action="store_true", help="omit per-query detail")
    args = parser.parse_args()
    adapter: LocalEmbeddingAdapter = TeachingEmbeddingAdapter()
    if args.model_directory is not None:
        from labs.week_05.local_model import LocalSentenceTransformer

        adapter = LocalSentenceTransformer.from_directory(
            args.model_directory,
            model_id=args.model_id,
            query_prefix=args.query_prefix,
            document_prefix=args.document_prefix,
        )
    report = run_comparison(
        adapter, k=args.k, context_budget_chars=args.context_budget_chars
    )
    if args.summary:
        results = report["results"]
        assert isinstance(results, list)
        for result in results:
            result.pop("queries")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
