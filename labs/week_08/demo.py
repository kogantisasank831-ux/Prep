"""Run Procurement Knowledge Assistant v1 locally with cited source excerpts."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import logging
from pathlib import Path

from labs.week_07.retrieval import MetadataFilter, RetrievalRequest
from labs.week_08.data import demo_access, load_corpus
from labs.week_08.pipeline import (
    KnowledgeAssistant,
    PairScorer,
    PipelineConfig,
    TeachingPairScorer,
)


class SafeEventFormatter(logging.Formatter):
    """Allowlist request metadata; no query or document payload enters CLI logs."""

    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(
            {
                "event": record.getMessage(),
                **{
                    key: getattr(record, key)
                    for key in (
                        "request_id",
                        "candidate_count",
                        "selected_span_count",
                        "status",
                        "manifest_fingerprint",
                    )
                    if hasattr(record, key)
                },
            }
        )


def add_model_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--reranker-directory", type=Path)
    parser.add_argument("--reranker-id", default="reviewed-local-scalar-cross-encoder")
    parser.add_argument("--reranker-token-limit", type=int)


def select_scorer(
    args: argparse.Namespace, parser: argparse.ArgumentParser
) -> PairScorer:
    if args.reranker_directory is not None:
        if args.reranker_token_limit is None:
            parser.error(
                "local reranker requires --reranker-token-limit from its reviewed model contract"
            )
        from labs.week_08.local_reranker import LocalCrossEncoder

        return LocalCrossEncoder.from_directory(
            args.reranker_directory,
            model_id=args.reranker_id,
            token_limit=args.reranker_token_limit,
        )
    if args.reranker_token_limit is not None:
        parser.error("--reranker-token-limit requires --reranker-directory")
    return TeachingPairScorer()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus", type=Path, default=Path(__file__).with_name("corpus.jsonl")
    )
    parser.add_argument(
        "--query",
        default="What payment condition controls Schedule A for the 1,000 kg copper-wire line?",
    )
    parser.add_argument("--document-type")
    parser.add_argument("--supplier")
    parser.add_argument("--rewrite", action="append", default=[])
    parser.add_argument("--context-chars", type=int, default=1400)
    parser.add_argument("--compression", choices=("none", "sentences"), default="none")
    add_model_arguments(parser)
    args = parser.parse_args()
    scorer = select_scorer(args, parser)
    handler = logging.StreamHandler()
    handler.setFormatter(SafeEventFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[handler])
    corpus = load_corpus(args.corpus)
    filters = tuple(
        MetadataFilter(field, value)
        for field, value in (
            ("supplier", args.supplier),
            ("document_type", args.document_type),
        )
        if value is not None
    )
    result = KnowledgeAssistant(
        corpus.chunks,
        demo_access(),
        scorer=scorer,
        config=PipelineConfig(
            context_chars=args.context_chars, compression=args.compression
        ),
    ).ask(RetrievalRequest("analyst", args.query, 3, filters), rewrites=args.rewrite)
    print(
        json.dumps(
            {
                "name": "Procurement Knowledge Assistant v1",
                "scope": "local teaching CLI; cited source excerpts; no free-form answer generation",
                "accepted_documents": corpus.accepted_documents,
                "ingestion_issues": [asdict(issue) for issue in corpus.issues],
                "input_digest": corpus.input_digest,
                "reranker": asdict(scorer.identity),
                "status": result.status,
                "answer_mode": result.answer_mode,
                "answer": result.answer,
                "context_chars": len(result.context),
                "context": json.loads(result.context),
                "citations": [
                    {
                        "id": span.citation_id,
                        "document_id": span.chunk.document_id,
                        "version": span.chunk.document_version,
                        "chunk_id": span.chunk.chunk_id,
                        "source_digest": span.chunk.source_digest,
                        "locations": json.loads(
                            dict(span.chunk.metadata)["source_locations"]
                        ),
                        "start": span.start,
                        "end": span.end,
                        "quote": span.quote,
                    }
                    for span in result.citations
                ],
                "manifest_fingerprint": result.manifest_fingerprint,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
