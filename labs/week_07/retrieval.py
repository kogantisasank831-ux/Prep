"""Exact sparse/dense/fusion contracts for the Week 7 teaching lab."""

from __future__ import annotations


from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass
from hashlib import sha256
from math import isfinite, log
import json
import platform
from types import MappingProxyType
import re
from typing import Protocol, Self


TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:[-_/][a-z0-9]+)*")
MANIFEST_SCHEMA = "procurement-hybrid-retrieval/1.1.0"


class RetrievalError(Exception):
    """Base class for explicit sparse/dense retrieval boundary failures."""


class CorpusInvariantError(RetrievalError):
    """Frozen chunks or authorised corpus invariants were violated."""


class ConfigurationError(RetrievalError):
    """Tokenizer, BM25, dense, or fusion configuration is invalid."""


class ManifestCompatibilityError(RetrievalError):
    """A caller attempted to combine incompatible retrieval artifacts."""


@dataclass(frozen=True)
class SourceChunk:
    chunk_id: str
    tenant_id: str
    document_id: str
    document_version: str
    source_digest: str
    text: str
    metadata: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class TokenContract:
    name: str
    version: str
    pattern: str

    def fingerprint(self) -> str:
        if not self.name or not self.version or not self.pattern:
            raise ConfigurationError("token contract fields must be non-empty")
        return digest_text("\x1f".join((self.name, self.version, self.pattern)))


DEFAULT_TOKEN_CONTRACT = TokenContract(
    name="identifier-preserving",
    version="1.0.0",
    pattern=TOKEN_PATTERN.pattern,
)


@dataclass(frozen=True)
class MetadataFilter:
    field: str
    value: str


@dataclass(frozen=True)
class RetrievalRequest:
    principal_id: str
    query_text: str
    top_k: int
    filters: tuple[MetadataFilter, ...] = ()


def digest_text(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def tokenize(
    text: str, contract: TokenContract = DEFAULT_TOKEN_CONTRACT
) -> tuple[str, ...]:
    contract.fingerprint()
    if contract != DEFAULT_TOKEN_CONTRACT:
        raise ConfigurationError("reference tokenizer does not implement this contract")
    if not isinstance(text, str) or len(text) > 4000:
        raise ConfigurationError("tokenizer requires bounded text")
    try:
        text.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ConfigurationError("tokenizer requires valid UTF-8 text") from exc
    return tuple(TOKEN_PATTERN.findall(text.lower()))


def metadata_values(chunk: SourceChunk) -> dict[str, str]:
    return dict(chunk.metadata)


@dataclass(frozen=True)
class BM25Config:
    k1: float = 1.2
    b: float = 0.75
    algorithm: str = "log1p-idf-unique-query/v1"

    def fingerprint(self) -> str:
        if self.algorithm != "log1p-idf-unique-query/v1":
            raise ConfigurationError("unsupported BM25 algorithm contract")
        if (
            type(self.k1) not in (int, float)
            or type(self.b) not in (int, float)
            or not isfinite(self.k1)
            or not isfinite(self.b)
            or self.k1 <= 0
            or not 0 <= self.b <= 1
        ):
            raise ConfigurationError("BM25 requires finite k1 > 0 and b in [0, 1]")
        return digest_text(json.dumps(asdict(self), sort_keys=True))


@dataclass(frozen=True)
class BM25Index:
    chunks: tuple[SourceChunk, ...]
    term_frequencies: Mapping[str, Mapping[str, int]]
    document_frequencies: Mapping[str, int]
    document_lengths: Mapping[str, int]
    average_document_length: float
    token_contract: TokenContract
    config: BM25Config

    @classmethod
    def build(
        cls,
        chunks: Sequence[SourceChunk],
        *,
        token_contract: TokenContract,
        config: BM25Config,
    ) -> Self:
        config.fingerprint()
        token_contract.fingerprint()
        validate_chunks(chunks)
        if not chunks:
            raise CorpusInvariantError("BM25 requires at least one authorised chunk")
        frequencies: dict[str, Mapping[str, int]] = {}
        df: Counter[str] = Counter()
        lengths: dict[str, int] = {}
        for chunk in chunks:
            terms = tokenize(chunk.text, token_contract)
            if not terms:
                raise CorpusInvariantError("chunks must contain at least one token")
            counts = Counter(terms)
            frequencies[chunk.chunk_id] = MappingProxyType(dict(counts))
            lengths[chunk.chunk_id] = len(terms)
            df.update(counts.keys())
        return cls(
            tuple(chunks),
            MappingProxyType(frequencies),
            MappingProxyType(dict(df)),
            MappingProxyType(lengths),
            sum(lengths.values()) / len(lengths),
            token_contract,
            config,
        )

    def score(self, query_text: str, chunk: SourceChunk) -> float:
        if chunk not in self.chunks:
            raise ManifestCompatibilityError("scored chunk differs from index snapshot")
        frequencies = self.term_frequencies[chunk.chunk_id]
        length = self.document_lengths[chunk.chunk_id]
        total = 0.0
        # Query terms are unique in this version; repetition is not a hidden boost.
        for term in dict.fromkeys(tokenize(query_text, self.token_contract)):
            frequency = frequencies.get(term, 0)
            if frequency == 0:
                continue
            df = self.document_frequencies[term]
            idf = log(1.0 + (len(self.chunks) - df + 0.5) / (df + 0.5))
            norm = (
                1
                - self.config.b
                + self.config.b * length / self.average_document_length
            )
            k1 = self.config.k1
            # Equivalent ratio avoids overflow for a very large finite k1.
            tf_weight = (
                frequency * (1 + 1 / k1) / (frequency / k1 + norm)
                if k1 >= 1
                else frequency * (1 + k1) / (frequency + k1 * norm)
            )
            total += idf * tf_weight
        return total


def validate_request(request: RetrievalRequest) -> None:
    if (
        not isinstance(request.principal_id, str)
        or not request.principal_id.strip()
        or len(request.principal_id) > 128
        or not isinstance(request.query_text, str)
        or not request.query_text.strip()
        or len(request.query_text) > 1000
        or type(request.top_k) is not int
        or request.top_k < 1
        or request.top_k > 256
    ):
        raise ConfigurationError(
            "request requires bounded principal/query and integer top_k in [1, 256]"
        )
    try:
        request.query_text.encode("utf-8")
        request.principal_id.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ConfigurationError("request requires valid UTF-8 text") from exc
    validate_filters(request.filters)


def validate_chunks(chunks: Sequence[SourceChunk]) -> None:
    if len(chunks) > 256 or len({chunk.chunk_id for chunk in chunks}) != len(chunks):
        raise CorpusInvariantError("corpus must have at most 256 unique chunk IDs")
    for chunk in chunks:
        fields = (
            chunk.chunk_id,
            chunk.tenant_id,
            chunk.document_id,
            chunk.document_version,
            chunk.source_digest,
        )
        if (
            any(
                not isinstance(value, str) or not value.strip() or len(value) > 256
                for value in fields
            )
            or not isinstance(chunk.text, str)
            or not chunk.text.strip()
            or len(chunk.text) > 4000
            or len(chunk.metadata) > 32
            or len(dict(chunk.metadata)) != len(chunk.metadata)
            or any(
                not isinstance(k, str)
                or not k.strip()
                or not isinstance(v, str)
                or not v.strip()
                or len(k) > 100
                or len(v) > 1000
                for k, v in chunk.metadata
            )
        ):
            raise CorpusInvariantError(
                "chunks require bounded identity, text, and unique metadata"
            )
        try:
            for value in (
                *fields,
                chunk.text,
                *(value for pair in chunk.metadata for value in pair),
            ):
                value.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise CorpusInvariantError("chunks require valid UTF-8 text") from exc


def require_request_corpus(request: RetrievalRequest, corpus: AuthorizedCorpus) -> None:
    validate_request(request)
    if (
        request.principal_id != corpus.principal_id
        or tuple(sorted(request.filters, key=lambda f: f.field)) != corpus.filters
    ):
        raise ManifestCompatibilityError(
            "request principal/filters differ from authorised corpus"
        )


ALLOWED_FILTER_FIELDS = frozenset({"supplier", "document_type"})


class AccessPolicy(Protocol):
    def can_read(self, principal_id: str, chunk: SourceChunk) -> bool: ...


@dataclass(frozen=True)
class StaticObjectAccessPolicy:
    permitted: frozenset[tuple[str, str, str, str]]

    def can_read(self, principal_id: str, chunk: SourceChunk) -> bool:
        return (
            principal_id,
            chunk.tenant_id,
            chunk.document_id,
            chunk.document_version,
        ) in self.permitted


def validate_filters(filters: Sequence[MetadataFilter]) -> None:
    if len(filters) > len(ALLOWED_FILTER_FIELDS) or any(
        filter_.field not in ALLOWED_FILTER_FIELDS
        or not isinstance(filter_.value, str)
        or not filter_.value.strip()
        or len(filter_.value) > 200
        for filter_ in filters
    ):
        raise ConfigurationError(
            "metadata filters must use bounded allowlisted equality predicates"
        )
    if len({filter_.field for filter_ in filters}) != len(filters):
        raise ConfigurationError("metadata filter fields must be unique")


@dataclass(frozen=True)
class AuthorizedCorpus:
    principal_id: str
    chunks: tuple[SourceChunk, ...]
    partition_fingerprint: str
    filters: tuple[MetadataFilter, ...] = ()

    @classmethod
    def build(
        cls,
        request: RetrievalRequest,
        chunks: Sequence[SourceChunk],
        access_policy: AccessPolicy,
    ) -> Self:
        validate_request(request)
        if len(chunks) > 256:
            raise CorpusInvariantError("reference corpus exceeds 256 chunks")
        authorised = tuple(
            chunk
            for chunk in chunks
            if access_policy.can_read(request.principal_id, chunk)
        )
        validate_chunks(authorised)
        eligible = tuple(
            chunk
            for chunk in authorised
            if all(
                metadata_values(chunk).get(f.field) == f.value for f in request.filters
            )
        )
        filters = tuple(sorted(request.filters, key=lambda f: f.field))
        partition = digest_text(
            json.dumps(
                {
                    "principal": request.principal_id,
                    "corpus": corpus_fingerprint(eligible),
                    "filters": [asdict(f) for f in filters],
                },
                sort_keys=True,
            )
        )
        return cls(request.principal_id, eligible, partition, filters)

    def bm25(
        self, token_contract: TokenContract, config: BM25Config
    ) -> BM25Index | None:
        token_contract.fingerprint()
        config.fingerprint()
        return (
            BM25Index.build(self.chunks, token_contract=token_contract, config=config)
            if self.chunks
            else None
        )


@dataclass(frozen=True)
class DenseConfig:
    adapter_id: str
    artifact_digest: str
    runtime_id: str
    preprocessing_version: str
    metric: str
    minimum_score: float = 0.0
    dimension: int | None = None

    def fingerprint(self) -> str:
        if self.dimension is not None and (
            type(self.dimension) is not int or self.dimension < 1
        ):
            raise ConfigurationError(
                "dense dimension must be a positive integer when supplied"
            )
        if not all(
            isinstance(value, str) and value.strip()
            for value in (
                self.adapter_id,
                self.artifact_digest,
                self.runtime_id,
                self.preprocessing_version,
                self.metric,
            )
        ):
            raise ConfigurationError("dense configuration fields must be non-empty")
        if type(self.minimum_score) not in (int, float) or not isfinite(
            self.minimum_score
        ):
            raise ConfigurationError("dense minimum score must be finite")
        return digest_text(json.dumps(asdict(self), sort_keys=True))


class DenseAdapter(Protocol):
    @property
    def config(self) -> DenseConfig: ...

    def score(self, query_text: str, chunk_text: str) -> float: ...


@dataclass(frozen=True)
class DemoDenseAdapter:
    config: DenseConfig = DenseConfig(
        adapter_id="demo-procurement-features",
        artifact_digest="synthetic-only",
        runtime_id=f"python-stdlib/{platform.python_version()}",
        preprocessing_version="identifier-dropping-positive-candidates/v2",
        metric="jaccard-features",
    )

    def _features(self, text: str) -> frozenset[str]:
        preserved_terms = set(tokenize(text))
        component_terms = {
            component
            for term in preserved_terms
            for component in re.split(r"[-_/]", term)
        }
        terms = preserved_terms | component_terms
        features: set[str] = set()
        if terms & {"payment", "invoice", "due"}:
            features.add("payment")
        if terms & {"approval", "approve", "sign", "signs", "off"}:
            features.add("approval")
        if terms & {"inspection", "quality", "receiving"}:
            features.add("inspection")
        if terms & {"copper", "wire", "coil"}:
            features.add("copper-wire")
        return frozenset(features)

    def score(self, query_text: str, chunk_text: str) -> float:
        query_features = self._features(query_text)
        chunk_features = self._features(chunk_text)
        if not query_features or not chunk_features:
            return 0.0
        return len(query_features & chunk_features) / len(
            query_features | chunk_features
        )


@dataclass(frozen=True)
class RankedCandidate:
    chunk: SourceChunk
    score: float
    rank: int
    retriever: str


@dataclass(frozen=True)
class Contributor:
    retriever: str
    rank: int
    raw_score: float


@dataclass(frozen=True)
class FusedCandidate:
    chunk: SourceChunk
    score: float
    rank: int
    contributors: tuple[Contributor, ...]


@dataclass(frozen=True)
class FusionConfig:
    rank_constant: int = 60
    weights: tuple[tuple[str, float], ...] = (("bm25", 1.0), ("dense", 1.0))

    def fingerprint(self) -> str:
        if (
            type(self.rank_constant) is not int
            or self.rank_constant <= 0
            or not self.weights
            or any(
                not name
                or type(weight) not in (int, float)
                or not isfinite(weight)
                or weight <= 0
                for name, weight in self.weights
            )
        ):
            raise ConfigurationError(
                "RRF requires an integer rank constant and positive finite weights"
            )
        if len({name for name, _ in self.weights}) != len(self.weights):
            raise ConfigurationError("RRF retriever names must be unique")
        return digest_text(
            json.dumps(
                {"rank_constant": self.rank_constant, "weights": sorted(self.weights)},
                sort_keys=True,
            )
        )


def rank_candidates(
    scores: Iterable[tuple[SourceChunk, float]],
    *,
    top_k: int,
    retriever: str,
    minimum_score: float = 0.0,
) -> tuple[RankedCandidate, ...]:
    if type(top_k) is not int or top_k < 1 or not retriever:
        raise ValueError("positive integer top_k and retriever name are required")
    if type(minimum_score) not in (int, float) or not isfinite(minimum_score):
        raise ConfigurationError("score floor must be finite")
    items = tuple(scores)
    if any(
        type(score) not in (int, float) or not isfinite(score) for _, score in items
    ):
        raise ConfigurationError("candidate scores must be finite numbers")
    if len({chunk.chunk_id for chunk, _ in items}) != len(items):
        raise CorpusInvariantError("ranked candidates must have unique IDs")
    ordered = sorted(
        (item for item in items if item[1] > minimum_score),
        key=lambda item: (-item[1], item[0].chunk_id),
    )[:top_k]
    return tuple(
        RankedCandidate(chunk, score, rank, retriever)
        for rank, (chunk, score) in enumerate(ordered, 1)
    )


def sparse_candidates(
    request: RetrievalRequest, corpus: AuthorizedCorpus, index: BM25Index | None
) -> tuple[RankedCandidate, ...]:
    require_request_corpus(request, corpus)
    if not corpus.chunks and index is None:
        return ()
    if index is None or index.chunks != corpus.chunks:
        raise ManifestCompatibilityError(
            "BM25 index corpus differs from authorised corpus"
        )
    return rank_candidates(
        ((chunk, index.score(request.query_text, chunk)) for chunk in corpus.chunks),
        top_k=request.top_k,
        retriever="bm25",
    )


def dense_candidates(
    request: RetrievalRequest, corpus: AuthorizedCorpus, adapter: DenseAdapter
) -> tuple[RankedCandidate, ...]:
    require_request_corpus(request, corpus)
    config = adapter.config
    config.fingerprint()
    scores = tuple(
        (chunk, adapter.score(request.query_text, chunk.text))
        for chunk in corpus.chunks
    )
    if adapter.config != config:
        raise ManifestCompatibilityError("dense configuration changed during scoring")
    return rank_candidates(
        scores,
        top_k=request.top_k,
        retriever="dense",
        minimum_score=config.minimum_score,
    )


def min_max_normalize(scores: Mapping[str, float]) -> dict[str, float]:
    if not scores:
        return {}
    if any(
        type(value) not in (int, float) or not isfinite(value)
        for value in scores.values()
    ):
        raise ConfigurationError("normalization requires finite numeric scores")
    lower, upper = min(scores.values()), max(scores.values())
    if lower == upper:
        return {key: 0.0 for key in scores}
    # Scale first if subtracting extreme signed values would overflow.
    span = upper - lower
    if isfinite(span):
        return {key: (value - lower) / span for key, value in scores.items()}
    scale = max(abs(lower), abs(upper))
    lo, hi = lower / scale, upper / scale
    return {key: (value / scale - lo) / (hi - lo) for key, value in scores.items()}


def reciprocal_rank_fusion(
    ranked_lists: Sequence[Sequence[RankedCandidate]],
    config: FusionConfig,
    *,
    top_k: int,
) -> tuple[FusedCandidate, ...]:
    if type(top_k) is not int or top_k < 1:
        raise ValueError("top_k must be a positive integer")
    weights = dict(config.weights)
    config.fingerprint()
    fused_scores: defaultdict[str, float] = defaultdict(float)
    chunks: dict[str, SourceChunk] = {}
    contributors: defaultdict[str, list[Contributor]] = defaultdict(list)
    seen_contributors: set[tuple[str, str]] = set()
    ranks_by_retriever: defaultdict[str, set[int]] = defaultdict(set)
    for ranked_list in ranked_lists:
        for candidate in ranked_list:
            if candidate.retriever not in weights:
                raise ConfigurationError("fusion received an unconfigured retriever")
            if (
                type(candidate.rank) is not int
                or candidate.rank <= 0
                or type(candidate.score) not in (int, float)
                or not isfinite(candidate.score)
            ):
                raise ConfigurationError(
                    "fusion candidates require positive ranks and finite scores"
                )
            contribution_key = (candidate.retriever, candidate.chunk.chunk_id)
            if contribution_key in seen_contributors:
                raise ConfigurationError(
                    "fusion received a duplicate retriever/chunk contribution"
                )
            seen_contributors.add(contribution_key)
            if candidate.rank in ranks_by_retriever[candidate.retriever]:
                raise ConfigurationError("retriever ranks must be unique")
            ranks_by_retriever[candidate.retriever].add(candidate.rank)
            existing_chunk = chunks.get(candidate.chunk.chunk_id)
            if existing_chunk is not None and existing_chunk != candidate.chunk:
                raise CorpusInvariantError(
                    "one chunk ID resolved to conflicting source chunks"
                )
            fused_scores[candidate.chunk.chunk_id] += weights[candidate.retriever] / (
                config.rank_constant + candidate.rank
            )
            chunks[candidate.chunk.chunk_id] = candidate.chunk
            contributors[candidate.chunk.chunk_id].append(
                Contributor(candidate.retriever, candidate.rank, candidate.score)
            )
    if any(
        ranks != set(range(1, len(ranks) + 1)) for ranks in ranks_by_retriever.values()
    ):
        raise ConfigurationError("retriever ranks must be contiguous from one")
    if any(not isfinite(score) for score in fused_scores.values()):
        raise ConfigurationError("fusion score exceeded finite range")
    ordered = sorted(fused_scores.items(), key=lambda item: (-item[1], item[0]))[:top_k]
    return tuple(
        FusedCandidate(
            chunk=chunks[chunk_id],
            score=score,
            rank=rank,
            contributors=tuple(
                sorted(contributors[chunk_id], key=lambda item: item.retriever)
            ),
        )
        for rank, (chunk_id, score) in enumerate(ordered, start=1)
    )


def hybrid_candidates(
    request: RetrievalRequest,
    corpus: AuthorizedCorpus,
    index: BM25Index | None,
    adapter: DenseAdapter,
    fusion: FusionConfig,
    *,
    candidate_depth: int,
) -> tuple[FusedCandidate, ...]:
    if (
        type(candidate_depth) is not int
        or candidate_depth < request.top_k
        or candidate_depth > 256
    ):
        raise ConfigurationError("candidate depth must be at least top_k")
    expanded = RetrievalRequest(
        principal_id=request.principal_id,
        query_text=request.query_text,
        top_k=candidate_depth,
        filters=request.filters,
    )
    return reciprocal_rank_fusion(
        (
            sparse_candidates(expanded, corpus, index),
            dense_candidates(expanded, corpus, adapter),
        ),
        fusion,
        top_k=request.top_k,
    )


@dataclass(frozen=True)
class RetrievalManifest:
    schema_version: str
    corpus_fingerprint: str
    partition_fingerprint: str
    token_fingerprint: str
    bm25_fingerprint: str
    dense_fingerprint: str
    fusion_fingerprint: str
    candidate_depth: int
    top_k: int

    def fingerprint(self) -> str:
        if (
            self.schema_version != MANIFEST_SCHEMA
            or type(self.candidate_depth) is not int
            or type(self.top_k) is not int
            or not 1 <= self.top_k <= self.candidate_depth <= 256
        ):
            raise ConfigurationError("candidate depth must be at least positive top_k")
        fields = (
            self.schema_version,
            self.corpus_fingerprint,
            self.partition_fingerprint,
            self.token_fingerprint,
            self.bm25_fingerprint,
            self.dense_fingerprint,
            self.fusion_fingerprint,
            str(self.candidate_depth),
            str(self.top_k),
        )
        return digest_text("\x1f".join(fields))


def corpus_fingerprint(chunks: Sequence[SourceChunk]) -> str:
    """Bind actual chunk text and metadata as well as externally supplied source IDs."""
    records = [
        {**asdict(chunk), "metadata": sorted(chunk.metadata)}
        for chunk in sorted(chunks, key=lambda c: c.chunk_id)
    ]
    return digest_text(
        json.dumps(records, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    )


def make_manifest(
    corpus: AuthorizedCorpus,
    token_contract: TokenContract,
    bm25_config: BM25Config,
    dense_adapter: DenseAdapter,
    fusion_config: FusionConfig,
    *,
    candidate_depth: int,
    top_k: int,
) -> RetrievalManifest:
    tokenize("", token_contract)
    manifest = RetrievalManifest(
        schema_version=MANIFEST_SCHEMA,
        corpus_fingerprint=corpus_fingerprint(corpus.chunks),
        partition_fingerprint=corpus.partition_fingerprint,
        token_fingerprint=token_contract.fingerprint(),
        bm25_fingerprint=bm25_config.fingerprint(),
        dense_fingerprint=dense_adapter.config.fingerprint(),
        fusion_fingerprint=fusion_config.fingerprint(),
        candidate_depth=candidate_depth,
        top_k=top_k,
    )
    manifest.fingerprint()
    return manifest


def require_compatible(
    expected: RetrievalManifest, observed: RetrievalManifest
) -> None:
    if expected.fingerprint() != observed.fingerprint():
        raise ManifestCompatibilityError(
            "retrieval manifest differs from the requested contract"
        )


@dataclass(frozen=True)
class EvaluationCase:
    query_id: str
    request: RetrievalRequest
    relevant_chunk_ids: frozenset[str]
    required_atoms: frozenset[str]
    category: str


def recall_at_k(returned_ids: Sequence[str], relevant_ids: frozenset[str]) -> float:
    if not relevant_ids:
        raise ValueError("evaluation case needs at least one relevant chunk")
    return len(set(returned_ids) & relevant_ids) / len(relevant_ids)


def precision_at_k(
    returned_ids: Sequence[str], relevant_ids: frozenset[str], *, k: int
) -> float:
    if type(k) is not int or k < 1 or len(set(returned_ids)) != len(returned_ids):
        raise ValueError("positive k and unique ranking IDs are required")
    return len(set(returned_ids[:k]) & relevant_ids) / k


def reciprocal_rank(returned_ids: Sequence[str], relevant_ids: frozenset[str]) -> float:
    for rank, chunk_id in enumerate(returned_ids, start=1):
        if chunk_id in relevant_ids:
            return 1.0 / rank
    return 0.0


def support_complete(chunks: Sequence[SourceChunk], atoms: frozenset[str]) -> bool:
    source_text = "\n".join(chunk.text.lower() for chunk in chunks)
    return all(atom.lower() in source_text for atom in atoms)
