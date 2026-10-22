"""Run the four-document fixture without downloading or calling a model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import UTC, datetime

from labs.week_05.data import sample_documents
from labs.week_05.local_model import LocalSentenceTransformer
from labs.week_05.retrieval import (
    DemoLocalEmbeddingAdapter,
    LocalEmbeddingAdapter,
    InMemoryCosineIndex,
    SearchRequest,
    StaticObjectAccessPolicy,
    initial_chunks,
)

FIXED_BUILD_TIME = datetime(2026, 8, 16, tzinfo=UTC)
ADAPTER = DemoLocalEmbeddingAdapter()


def allow_all_sample_documents(principal_id: str) -> StaticObjectAccessPolicy:
    return StaticObjectAccessPolicy(
        permitted=frozenset(
            (
                principal_id,
                source.tenant_id,
                source.document_id,
                source.document_version,
            )
            for source in initial_chunks(sample_documents())
        )
    )


def sample_index() -> InMemoryCosineIndex:
    return InMemoryCosineIndex.build(
        initial_chunks(sample_documents()),
        ADAPTER,
        created_at=FIXED_BUILD_TIME,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Week 5 local procurement retrieval lab"
    )
    parser.add_argument("--model-directory", type=Path)
    parser.add_argument("--query-prefix", default="")
    parser.add_argument("--document-prefix", default="")
    args = parser.parse_args()
    adapter: LocalEmbeddingAdapter
    if args.model_directory is None:
        adapter = ADAPTER
        mode = "teaching features; not semantic-model evaluation"
    else:
        adapter = LocalSentenceTransformer.from_directory(
            args.model_directory,
            model_id=args.model_directory.name,
            query_prefix=args.query_prefix,
            document_prefix=args.document_prefix,
        )
        mode = "local model; relevance quality requires a labelled evaluation"
    index = InMemoryCosineIndex.build(
        initial_chunks(sample_documents()), adapter, created_at=datetime.now(UTC)
    )
    results = index.search(
        SearchRequest(
            "analyst-1", "Which supplier documents require approval before payment?", 2
        ),
        adapter=adapter,
        access_policy=allow_all_sample_documents("analyst-1"),
    )
    print(
        json.dumps(
            {
                "mode": mode,
                "index_id": index.manifest.index_id,
                "model_fingerprint": index.manifest.model_fingerprint,
                "results": [
                    {
                        "document_id": r.source.document_id,
                        "score": r.score,
                        "text": r.source.text,
                    }
                    for r in results
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
