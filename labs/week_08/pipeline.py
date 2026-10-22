"""Same-pool reranking, exact deduplication, and validated extractive answers."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass
import json
import logging
from math import isfinite
import re
from typing import Protocol

from labs.week_07.retrieval import (
    AccessPolicy,
    AuthorizedCorpus,
    BM25Config,
    DEFAULT_TOKEN_CONTRACT,
    DemoDenseAdapter,
    DenseAdapter,
    FusedCandidate,
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
    tokenize,
    validate_request,
)

logger = logging.getLogger(__name__)


class PipelineError(ValueError):
    """A reranking or evidence boundary failed validation."""


@dataclass(frozen=True)
class RerankerIdentity:
    name: str
    version: str
    artifact_digest: str
    runtime: str
    preprocessing: str


class PairScorer(Protocol):
    @property
    def identity(self) -> RerankerIdentity: ...

    def score_pairs(self, pairs: Sequence[tuple[str, str]]) -> tuple[float, ...]: ...


@dataclass(frozen=True)
class TeachingPairScorer:
    """Handwritten visible-fixture rules, not a trained cross-encoder."""

    identity: RerankerIdentity = RerankerIdentity(
        "teaching-pair-rules",
        "1.0.0",
        "synthetic",
        "python-stdlib",
        "unique-terms-and-commercial-phrases/v1",
    )

    def score_pairs(self, pairs: Sequence[tuple[str, str]]) -> tuple[float, ...]:
        scores = []
        for query, passage in pairs:
            query_terms, document_terms = set(tokenize(query)), set(tokenize(passage))
            score = len(query_terms & document_terms) / max(1, len(query_terms))
            score += sum(
                0.5
                for phrase in ("net 30", "net 15", "inspection approval", "signs off")
                if phrase in query.lower() and phrase in passage.lower()
            )
            if "payment" in query_terms and query_terms & {"condition", "terms"}:
                if (
                    "invoice terms" in passage.lower()
                    or "payment is due" in passage.lower()
                ):
                    score += 0.6
            scores.append(score)
        return tuple(scores)


def query_plan(original: str, rewrites: Sequence[str] = ()) -> tuple[str, ...]:
    """Keep original plus at most two caller-reviewed, lexically guarded variants.

    Preserving tokens cannot establish semantic equivalence. No automatic LLM
    rewrite is performed and principal/metadata predicates are never rewritten.
    """
    if not isinstance(original, str) or not original.strip() or len(original) > 1000:
        raise PipelineError("original query must be bounded nonblank text")
    if len(rewrites) > 2:
        raise PipelineError("at most two reviewed rewrites")
    protected = {
        term
        for term in tokenize(original)
        if any(character.isdigit() for character in term)
        or term
        in {"not", "no", "without", "never", "except", "unless", "after", "before"}
    }
    planned = [original]
    for rewrite in rewrites:
        if not isinstance(rewrite, str) or not rewrite.strip() or len(rewrite) > 1000:
            raise PipelineError("rewrite must be bounded nonblank text")
        if not protected <= set(tokenize(rewrite)):
            raise PipelineError(
                "rewrite dropped an identifier, number, or condition token"
            )
        if rewrite not in planned:
            planned.append(rewrite)
    return tuple(planned)


@dataclass(frozen=True)
class PipelineConfig:
    candidate_count: int = 6
    retrieval_depth: int = 8
    evidence_count: int = 3
    context_chars: int = 1400
    compression: str = "none"
    max_sentences: int = 2

    def __post_init__(self) -> None:
        numbers = (
            self.candidate_count,
            self.retrieval_depth,
            self.evidence_count,
            self.context_chars,
            self.max_sentences,
        )
        if any(type(value) is not int for value in numbers) or not (
            1
            <= self.evidence_count
            <= self.candidate_count
            <= self.retrieval_depth
            <= 32
            and 2 <= self.context_chars <= 16000
            and 1 <= self.max_sentences <= 4
            and self.compression in {"none", "sentences"}
        ):
            raise PipelineError(
                "invalid candidate, evidence, compression, or context budget"
            )


@dataclass(frozen=True)
class ScoredChunk:
    chunk: SourceChunk
    score: float
    retrieval_rank: int


def rerank(
    query: str,
    candidates: Sequence[FusedCandidate],
    scorer: PairScorer,
) -> tuple[ScoredChunk, ...]:
    """Reorder exactly these candidates; reject invalid or drifting score contracts."""
    if len(candidates) > 32 or len({c.chunk.chunk_id for c in candidates}) != len(
        candidates
    ):
        raise PipelineError("reranker requires at most 32 unique candidates")
    if not candidates:
        return ()
    identity = scorer.identity
    scores = scorer.score_pairs(tuple((query, item.chunk.text) for item in candidates))
    if len(scores) != len(candidates) or any(
        type(value) not in (int, float) or not isfinite(value) for value in scores
    ):
        raise PipelineError("reranker must return one finite scalar per candidate")
    if scorer.identity != identity:
        raise ManifestCompatibilityError("reranker identity changed during scoring")
    return tuple(
        sorted(
            (
                ScoredChunk(item.chunk, float(score), item.rank)
                for item, score in zip(candidates, scores, strict=True)
            ),
            key=lambda item: (-item.score, item.retrieval_rank, item.chunk.chunk_id),
        )
    )


def deduplicate(
    ranked: Sequence[ScoredChunk],
) -> tuple[tuple[ScoredChunk, ...], tuple[str, ...]]:
    """Collapse only identical text within the same tenant/source/version/digest."""
    seen: set[tuple[str, str, str, str, str]] = set()
    kept, dropped = [], []
    for item in ranked:
        chunk = item.chunk
        key = (
            chunk.tenant_id,
            chunk.document_id,
            chunk.document_version,
            chunk.source_digest,
            chunk.text,
        )
        if key in seen:
            dropped.append(chunk.chunk_id)
        else:
            seen.add(key)
            kept.append(item)
    return tuple(kept), tuple(dropped)


@dataclass(frozen=True)
class EvidenceSpan:
    citation_id: str
    chunk: SourceChunk
    start: int
    end: int
    quote: str


def _spans(
    query: str, chunk: SourceChunk, config: PipelineConfig
) -> tuple[tuple[int, int], ...]:
    if config.compression == "none" or ":row-" in dict(chunk.metadata).get(
        "source_locations", ""
    ):
        return ((0, len(chunk.text)),)
    boundaries = [
        0,
        *(match.end() for match in re.finditer(r"(?<=[.!?])\s+", chunk.text)),
        len(chunk.text),
    ]
    spans = [
        (start, end) for start, end in zip(boundaries, boundaries[1:]) if start < end
    ]
    query_terms = set(tokenize(query))
    selected = sorted(
        spans,
        key=lambda span: (
            -len(query_terms & set(tokenize(chunk.text[span[0] : span[1]]))),
            span[0],
        ),
    )[: config.max_sentences]
    return tuple(sorted(selected))


def context_json(spans: Sequence[EvidenceSpan]) -> str:
    return json.dumps(
        [
            {
                "citation_id": span.citation_id,
                "tenant_id": span.chunk.tenant_id,
                "document_id": span.chunk.document_id,
                "version": span.chunk.document_version,
                "locations": json.loads(dict(span.chunk.metadata)["source_locations"]),
                "text": span.quote,
            }
            for span in spans
        ],
        ensure_ascii=False,
        separators=(",", ":"),
    )


def pack_context(
    query: str,
    ranked: Sequence[ScoredChunk],
    principal: str,
    access: AccessPolicy,
    config: PipelineConfig,
) -> tuple[EvidenceSpan, ...]:
    """Count the whole serialized context; admit all selected spans of a chunk together."""
    selected: list[EvidenceSpan] = []
    source_units = 0
    for item in ranked:
        if source_units >= config.evidence_count:
            break
        if not access.can_read(principal, item.chunk):
            raise PipelineError("source permission changed before context construction")
        proposed = [*selected]
        for start, end in _spans(query, item.chunk, config):
            proposed.append(
                EvidenceSpan(
                    f"S{len(proposed) + 1}",
                    item.chunk,
                    start,
                    end,
                    item.chunk.text[start:end],
                )
            )
        if len(context_json(proposed)) <= config.context_chars:
            selected = proposed
            source_units += 1
    return tuple(selected)


def validate_citations(
    spans: Sequence[EvidenceSpan],
    stored: Sequence[SourceChunk],
    principal: str,
    access: AccessPolicy,
) -> None:
    """Verify stored identity, authorization and exact offsets; this is not entailment."""
    by_id = {chunk.chunk_id: chunk for chunk in stored}
    seen: set[str] = set()
    for span in spans:
        if (
            span.citation_id in seen
            or re.fullmatch(r"S[1-9][0-9]*", span.citation_id) is None
            or by_id.get(span.chunk.chunk_id) != span.chunk
            or not access.can_read(principal, span.chunk)
            or type(span.start) is not int
            or type(span.end) is not int
            or not 0 <= span.start < span.end <= len(span.chunk.text)
            or span.quote != span.chunk.text[span.start : span.end]
        ):
            raise PipelineError(
                "citation does not resolve to an authorized stored exact span"
            )
        seen.add(span.citation_id)


@dataclass(frozen=True)
class AssistantResult:
    status: str
    answer_mode: str
    answer: str
    context: str
    citations: tuple[EvidenceSpan, ...]
    candidates: tuple[FusedCandidate, ...]
    reranked: tuple[ScoredChunk, ...]
    deduplicated: tuple[ScoredChunk, ...]
    dropped_duplicate_ids: tuple[str, ...]
    manifest_fingerprint: str
    retrieval_manifests: tuple[str, ...]
    eligible_count: int


class KnowledgeAssistant:
    """Local in-memory teaching milestone; answers consist of cited source excerpts."""

    def __init__(
        self,
        chunks: Sequence[SourceChunk],
        access: AccessPolicy,
        *,
        scorer: PairScorer | None = None,
        dense: DenseAdapter | None = None,
        config: PipelineConfig | None = None,
    ) -> None:
        self.chunks = tuple(chunks)
        self.access = access
        self.scorer = scorer or TeachingPairScorer()
        self.dense = dense or DemoDenseAdapter()
        self.config = config or PipelineConfig()

    def ask(
        self,
        request: RetrievalRequest,
        *,
        rewrites: Sequence[str] = (),
        request_id: str = "local-demo",
    ) -> AssistantResult:
        validate_request(request)
        if re.fullmatch(r"[A-Za-z0-9_-]{1,64}", request_id) is None:
            raise PipelineError("request ID requires 1 to 64 safe characters")
        config = self.config
        if request.top_k != config.evidence_count:
            raise PipelineError("request top_k must match the evidence-unit budget")
        queries = query_plan(request.query_text, rewrites)
        corpus = AuthorizedCorpus.build(request, self.chunks, self.access)
        index = corpus.bm25(DEFAULT_TOKEN_CONTRACT, BM25Config())
        dense_identity, reranker_identity = self.dense.config, self.scorer.identity
        lists: list[tuple[RankedCandidate, ...]] = []
        manifests: list[str] = []
        for number, query in enumerate(queries):
            expanded = RetrievalRequest(
                request.principal_id, query, config.candidate_count, request.filters
            )
            ranked = hybrid_candidates(
                expanded,
                corpus,
                index,
                self.dense,
                FusionConfig(),
                candidate_depth=config.retrieval_depth,
            )
            lists.append(
                tuple(
                    RankedCandidate(item.chunk, item.score, item.rank, f"q{number}")
                    for item in ranked
                )
            )
            manifests.append(
                make_manifest(
                    corpus,
                    DEFAULT_TOKEN_CONTRACT,
                    BM25Config(),
                    self.dense,
                    FusionConfig(),
                    candidate_depth=config.retrieval_depth,
                    top_k=config.candidate_count,
                ).fingerprint()
            )
        candidates = reciprocal_rank_fusion(
            lists,
            FusionConfig(
                weights=tuple((f"q{number}", 1.0) for number in range(len(queries)))
            ),
            top_k=config.candidate_count,
        )
        reranked = rerank(request.query_text, candidates, self.scorer)
        deduplicated, dropped = deduplicate(reranked)
        spans = pack_context(
            request.query_text, deduplicated, request.principal_id, self.access, config
        )
        validate_citations(spans, corpus.chunks, request.principal_id, self.access)
        if (
            self.dense.config != dense_identity
            or self.scorer.identity != reranker_identity
        ):
            raise ManifestCompatibilityError(
                "model configuration changed during the request"
            )
        manifest = digest_text(
            json.dumps(
                {
                    "schema": "procurement-assistant/1.0.0",
                    "corpus": corpus_fingerprint(corpus.chunks),
                    "partition": corpus.partition_fingerprint,
                    "config": asdict(config),
                    "retrieval_manifests": manifests,
                    "query_digests": [digest_text(query) for query in queries],
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
        answer = "\n".join(f"{span.quote} [{span.citation_id}]" for span in spans)
        if not spans:
            answer = "No eligible evidence fits this request and context budget."
        logger.info(
            "assistant_request_completed",
            extra={
                "request_id": request_id,
                "candidate_count": len(candidates),
                "selected_span_count": len(spans),
                "status": status,
                "manifest_fingerprint": manifest,
            },
        )
        return AssistantResult(
            status,
            "cited_extractive",
            answer,
            context_json(spans),
            spans,
            candidates,
            reranked,
            deduplicated,
            dropped,
            manifest,
            tuple(manifests),
            len(corpus.chunks),
        )
