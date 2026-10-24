"""Observe existing retrieval components without changing earlier teaching labs."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass
import json
from pathlib import Path

from labs.week_07.retrieval import (
    AccessPolicy,
    AuthorizedCorpus,
    BM25Config,
    DEFAULT_TOKEN_CONTRACT,
    DemoDenseAdapter,
    DenseAdapter,
    FusionConfig,
    ManifestCompatibilityError,
    RankedCandidate,
    RetrievalRequest,
    SourceChunk,
    corpus_fingerprint,
    digest_text,
    hybrid_candidates,
    make_manifest,
    reciprocal_rank_fusion,
    validate_request,
)
from labs.week_08.pipeline import (
    AssistantResult,
    PairScorer,
    PipelineConfig,
    PipelineError,
    TeachingPairScorer,
    context_json,
    deduplicate,
    pack_context,
    query_plan,
    rerank,
    validate_citations,
)
from labs.week_10.generation import (
    ModelBackend,
    ModelRun,
    RateCard,
    build_prompt,
    trace_generation,
)
from labs.week_10.tracing import Stage, TraceRecorder

PIPELINE_VERSION = "week10-observed-components/1.0.0"


def implementation_digest() -> str:
    """Development-file identity, not a signed/immutable production artifact."""
    root = Path(__file__).parents[1]
    files = {
        f"week_{week:02d}/{path.name}": digest_text(path.read_text(encoding="utf-8"))
        for week in range(5, 11)
        for path in sorted((root / f"week_{week:02d}").glob("*.py"))
    }
    return digest_text(json.dumps(files, sort_keys=True, separators=(",", ":")))


@dataclass(frozen=True)
class ObservedResult:
    retrieval: AssistantResult
    queries: tuple[str, ...]
    model: ModelRun | None

    @property
    def answer(self) -> str:
        return self.retrieval.answer


def observe_request(
    request: RetrievalRequest,
    chunks: Sequence[SourceChunk],
    access: AccessPolicy,
    recorder: TraceRecorder,
    *,
    config: PipelineConfig | None = None,
    rewrites: Sequence[str] = (),
    dense: DenseAdapter | None = None,
    scorer: PairScorer | None = None,
    model: ModelBackend | None = None,
    prices: RateCard | None = None,
) -> ObservedResult:
    """One synchronous request. Explicit spans wrap real, reused component calls."""
    config = config or PipelineConfig()
    dense = dense or DemoDenseAdapter()
    scorer = scorer or TeachingPairScorer()
    with recorder.span(Stage.REQUEST) as root:
        root.set(
            request_id=recorder.request_id,
            pipeline_version=PIPELINE_VERSION,
            implementation_id=implementation_digest(),
            config_id=digest_text(json.dumps(asdict(config), sort_keys=True)),
            generation_mode="model" if model else "cited_extractive",
        )
        if model is None:
            root.set(
                usage_source="not_applicable",
                input_tokens=None,
                output_tokens=None,
                cached_input_tokens=None,
                cost_reason="not_applicable",
            )
        with recorder.span(Stage.VALIDATION, parent=root):
            validate_request(request)
            if request.top_k != config.evidence_count:
                raise PipelineError("request top_k must match evidence count")
        with recorder.span(Stage.QUERY_PLAN, parent=root) as span:
            queries = query_plan(request.query_text, rewrites)
            span.set(
                query_chars=len(request.query_text),
                rewrite_count=len(rewrites),
                query_count=len(queries),
            )
        with recorder.span(Stage.SCOPE, parent=root) as span:
            corpus = AuthorizedCorpus.build(request, chunks, access)
            index = corpus.bm25(DEFAULT_TOKEN_CONTRACT, BM25Config())
            span.set(
                eligible_count=len(corpus.chunks),
                snapshot_id=corpus.partition_fingerprint,
            )
        dense_identity, reranker_identity = dense.config, scorer.identity
        lists: list[tuple[RankedCandidate, ...]] = []
        manifests: list[str] = []
        with recorder.span(Stage.RETRIEVAL, parent=root) as retrieval_span:
            retrieval_span.set(
                depth=config.retrieval_depth,
                k=config.candidate_count,
                model_contract_id=dense_identity.fingerprint(),
            )
            for number, query in enumerate(queries):
                with recorder.span(Stage.TOOL, parent=retrieval_span) as span:
                    span.set(operation="hybrid_search", attempt=1, query_index=number)
                    expanded = RetrievalRequest(
                        request.principal_id,
                        query,
                        config.candidate_count,
                        request.filters,
                    )
                    ranked = hybrid_candidates(
                        expanded,
                        corpus,
                        index,
                        dense,
                        FusionConfig(),
                        candidate_depth=config.retrieval_depth,
                    )
                    span.set(
                        candidate_count=len(ranked),
                        candidate_ids=tuple(c.chunk.chunk_id for c in ranked),
                        retrieval_scores=tuple(c.score for c in ranked),
                    )
                    lists.append(
                        tuple(
                            RankedCandidate(c.chunk, c.score, c.rank, f"q{number}")
                            for c in ranked
                        )
                    )
                    manifests.append(
                        make_manifest(
                            corpus,
                            DEFAULT_TOKEN_CONTRACT,
                            BM25Config(),
                            dense,
                            FusionConfig(),
                            candidate_depth=config.retrieval_depth,
                            top_k=config.candidate_count,
                        ).fingerprint()
                    )
        with recorder.span(Stage.FUSION, parent=root) as span:
            candidates = reciprocal_rank_fusion(
                lists,
                FusionConfig(
                    weights=tuple((f"q{number}", 1.0) for number in range(len(queries)))
                ),
                top_k=config.candidate_count,
            )
            span.set(
                candidate_count=len(candidates),
                candidate_ids=tuple(c.chunk.chunk_id for c in candidates),
            )
        with recorder.span(Stage.RERANK, parent=root) as span:
            reranked = rerank(request.query_text, candidates, scorer)
            span.set(
                model_id=reranker_identity.name,
                model_revision=reranker_identity.version,
                model_contract_id=digest_text(
                    json.dumps(asdict(reranker_identity), sort_keys=True)
                ),
                ranked_ids=tuple(c.chunk.chunk_id for c in reranked),
                reranker_scores=tuple(c.score for c in reranked),
            )
        with recorder.span(Stage.DEDUP, parent=root) as span:
            deduplicated, dropped = deduplicate(reranked)
            span.set(dropped_count=len(dropped))
        with recorder.span(Stage.CONTEXT, parent=root) as span:
            spans = pack_context(
                request.query_text, deduplicated, request.principal_id, access, config
            )
            context = context_json(spans)
            span.set(
                selected_ids=tuple(dict.fromkeys(s.chunk.chunk_id for s in spans)),
                citation_count=len(spans),
                context_chars=len(context),
            )
        with recorder.span(Stage.CITATIONS, parent=root):
            validate_citations(spans, corpus.chunks, request.principal_id, access)
            if dense.config != dense_identity or scorer.identity != reranker_identity:
                raise ManifestCompatibilityError(
                    "model configuration changed during request"
                )
        with recorder.span(Stage.ANSWER, parent=root) as span:
            manifest = digest_text(
                json.dumps(
                    {
                        "schema": "procurement-assistant/1.0.0",
                        "corpus": corpus_fingerprint(corpus.chunks),
                        "partition": corpus.partition_fingerprint,
                        "config": asdict(config),
                        "retrieval_manifests": manifests,
                        "query_digests": [digest_text(q) for q in queries],
                        "reranker": asdict(reranker_identity),
                        "dedup": "source-version-exact-text/v1",
                        "context": "exact-spans-json/v1",
                        "answer": "cited-extractive/v1",
                    },
                    sort_keys=True,
                )
            )
            status = (
                "evidence_available"
                if spans
                else ("no_evidence" if not candidates else "context_budget_exhausted")
            )
            answer = (
                "\n".join(f"{s.quote} [{s.citation_id}]" for s in spans)
                if spans
                else "No eligible evidence fits this request and context budget."
            )
            result = AssistantResult(
                status,
                "cited_extractive",
                answer,
                context,
                spans,
                candidates,
                reranked,
                deduplicated,
                dropped,
                manifest,
                tuple(manifests),
                len(corpus.chunks),
            )
            span.set(outcome=status, citation_count=len(spans))
        generated = None
        if model is not None and spans:
            with recorder.span(Stage.PROMPT, parent=root) as span:
                prompt = build_prompt(request.query_text, context)
                span.set(
                    prompt_version=prompt.version,
                    prompt_chars=sum(len(text) for _, text in prompt.messages),
                )
            generated = trace_generation(prompt, model, recorder, root, prices)
        elif model is not None:
            root.set(
                generation_mode="skipped_no_evidence",
                usage_source="not_applicable",
                input_tokens=None,
                output_tokens=None,
                cached_input_tokens=None,
                cost_reason="not_applicable",
            )
        root.set(outcome=status, request_manifest=manifest)
        return ObservedResult(result, queries, generated)
