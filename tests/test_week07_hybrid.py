"""Sparse statistics, candidate gates, fusion arithmetic, and corpus isolation."""

from __future__ import annotations

from dataclasses import replace
import json
from math import log
from pathlib import Path
from typing import cast

import pytest

from labs.week_05.retrieval import DemoLocalEmbeddingAdapter, VectorInvariantError
from labs.week_06.chunking import StructurePolicy
from labs.week_06.fixtures import accepted_sources
from labs.week_07.compare import (
    LocalCosineAdapter,
    load_cases,
    measure_case,
    run_comparison,
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
    BM25Index,
    ConfigurationError,
    CorpusInvariantError,
    DEFAULT_TOKEN_CONTRACT,
    DemoDenseAdapter,
    FusionConfig,
    ManifestCompatibilityError,
    MetadataFilter,
    RankedCandidate,
    RetrievalRequest,
    SourceChunk,
    TokenContract,
    corpus_fingerprint,
    dense_candidates,
    digest_text,
    hybrid_candidates,
    make_manifest,
    min_max_normalize,
    rank_candidates,
    reciprocal_rank_fusion,
    require_compatible,
    sparse_candidates,
    tokenize,
)


def small_chunk(identity: str, text: str) -> SourceChunk:
    return SourceChunk(identity, "tenant", identity, "1", digest_text(text), text, ())


def corpus_for(request: RetrievalRequest) -> AuthorizedCorpus:
    chunks = frozen_chunks()
    return AuthorizedCorpus.build(request, chunks, access_policy(chunks))


def test_identifier_contract_is_explicit() -> None:
    assert tokenize("CW-1000 / PO_2026/18 PP-20 cw1000 CW-100O") == (
        "cw-1000",
        "po_2026/18",
        "pp-20",
        "cw1000",
        "cw-100o",
    )
    assert tokenize("CW-1000-ALT") == ("cw-1000-alt",)
    with pytest.raises(ConfigurationError):
        tokenize("CW-1000", TokenContract("unknown", "1", r"\w+"))


@pytest.mark.parametrize(
    "k1,b",
    [
        (0.0, 0.75),
        (-1.0, 0.75),
        (True, 0.75),
        (float("inf"), 0.75),
        (1.2, float("nan")),
        (1.2, True),
        (1.2, -0.1),
        (1.2, 1.1),
    ],
)
def test_invalid_bm25_configuration(k1: float, b: float) -> None:
    with pytest.raises(ConfigurationError):
        BM25Config(k1, b).fingerprint()


def test_bm25_hand_calculation_saturation_and_query_dedup() -> None:
    a, b = small_chunk("a", "CW-1000"), small_chunk("b", "invoice invoice invoice")
    index = BM25Index.build(
        (a, b), token_contract=DEFAULT_TOKEN_CONTRACT, config=BM25Config()
    )
    # N=2, df(code)=1, avgdl=2; dl(a)=1; tf=1.
    expected = log(2) * 2.2 / (1 + 1.2 * (0.25 + 0.75 / 2))
    assert index.score("CW-1000", a) == pytest.approx(expected)
    assert index.score("CW-1000 CW-1000", a) == pytest.approx(expected)
    assert index.score("missing", a) == 0
    repeated = BM25Index.build(
        (small_chunk("c", "term " * 10), small_chunk("d", "term")),
        token_contract=DEFAULT_TOKEN_CONTRACT,
        config=BM25Config(b=0),
    )
    assert repeated.score("term", repeated.chunks[0]) > repeated.score(
        "term", repeated.chunks[1]
    )
    assert repeated.score("term", repeated.chunks[0]) < 10 * repeated.score(
        "term", repeated.chunks[1]
    )
    huge = BM25Index.build(
        (a, b), token_contract=DEFAULT_TOKEN_CONTRACT, config=BM25Config(k1=1e308)
    )
    assert huge.score("CW-1000", a) > 0


def test_index_snapshot_is_immutable_and_bound_to_chunk() -> None:
    index = corpus_for(RetrievalRequest(PRINCIPAL, "CW-1000", 3)).bm25(
        DEFAULT_TOKEN_CONTRACT, BM25Config()
    )
    assert index is not None
    with pytest.raises(TypeError):
        cast(dict[str, int], index.document_frequencies)["cw-1000"] = 99
    with pytest.raises(TypeError):
        cast(dict[str, int], index.term_frequencies[index.chunks[0].chunk_id])[
            "cw-1000"
        ] = 99
    with pytest.raises(ManifestCompatibilityError):
        index.score("CW-1000", replace(index.chunks[0], text="changed"))


def test_index_rejects_empty_tokenless_and_duplicate_sources() -> None:
    for chunks in [(), (small_chunk("a", "---"),), (small_chunk("a", "text"),) * 2]:
        with pytest.raises(CorpusInvariantError):
            BM25Index.build(
                chunks, token_contract=DEFAULT_TOKEN_CONTRACT, config=BM25Config()
            )


@pytest.mark.parametrize(
    "query,k",
    [
        ("", 3),
        (" ", 3),
        ("x" * 1001, 3),
        ("bad\ud800", 3),
        ("code", 0),
        ("code", True),
        ("code", 257),
    ],
)
def test_request_bounds(query: str, k: int) -> None:
    with pytest.raises(ConfigurationError):
        corpus_for(RetrievalRequest(PRINCIPAL, query, k))


def test_filter_is_not_a_grant_and_request_scope_cannot_drift() -> None:
    chunks = frozen_chunks()
    request = RetrievalRequest(
        PRINCIPAL,
        "CW-1000",
        3,
        (
            MetadataFilter("document_type", "catalogue"),
            MetadataFilter("supplier", "Atlas Metals"),
        ),
    )
    corpus = AuthorizedCorpus.build(
        request, (*chunks, denied_code_match()), access_policy(chunks)
    )
    assert {item.document_id for item in corpus.chunks} == {"P-107"}
    reverse = replace(request, filters=tuple(reversed(request.filters)))
    assert (
        AuthorizedCorpus.build(
            reverse, chunks, access_policy(chunks)
        ).partition_fingerprint
        == corpus.partition_fingerprint
    )
    index = corpus.bm25(DEFAULT_TOKEN_CONTRACT, BM25Config())
    for changed in [
        replace(request, principal_id="other"),
        replace(request, filters=()),
    ]:
        with pytest.raises(ManifestCompatibilityError):
            sparse_candidates(changed, corpus, index)
        with pytest.raises(ManifestCompatibilityError):
            dense_candidates(changed, corpus, DemoDenseAdapter())
    for filters in [
        (MetadataFilter("tenant_id", "other-tenant"),),
        (MetadataFilter("supplier", ""),),
        (MetadataFilter("supplier", "Atlas Metals"),) * 2,
    ]:
        with pytest.raises(ConfigurationError):
            corpus_for(replace(request, filters=filters))


def test_denied_source_cannot_change_statistics_scores_or_fusion() -> None:
    chunks = frozen_chunks()
    request = RetrievalRequest(PRINCIPAL, "CW-1000 copper wire quote", 3)
    base = AuthorizedCorpus.build(request, chunks, access_policy(chunks))
    extra = AuthorizedCorpus.build(
        request, (*chunks, denied_code_match()), access_policy(chunks)
    )
    assert base == extra
    a, b = [c.bm25(DEFAULT_TOKEN_CONTRACT, BM25Config()) for c in (base, extra)]
    assert a is not None and b is not None
    assert a.document_frequencies == b.document_frequencies
    assert a.average_document_length == b.average_document_length
    assert sparse_candidates(request, base, a) == sparse_candidates(request, extra, b)
    assert dense_candidates(request, base, DemoDenseAdapter()) == dense_candidates(
        request, extra, DemoDenseAdapter()
    )
    assert hybrid_candidates(
        request, base, a, DemoDenseAdapter(), FusionConfig(), candidate_depth=5
    ) == hybrid_candidates(
        request, extra, b, DemoDenseAdapter(), FusionConfig(), candidate_depth=5
    )


def test_empty_authorized_corpus_and_no_positive_match() -> None:
    request = RetrievalRequest("denied", "SECRET-900", 3)
    corpus = corpus_for(request)
    assert corpus.chunks == ()
    assert sparse_candidates(request, corpus, None) == ()
    assert dense_candidates(request, corpus, DemoDenseAdapter()) == ()
    assert (
        hybrid_candidates(
            request, corpus, None, DemoDenseAdapter(), FusionConfig(), candidate_depth=5
        )
        == ()
    )
    request = replace(request, principal_id=PRINCIPAL)
    corpus = corpus_for(request)
    assert (
        sparse_candidates(
            request, corpus, corpus.bm25(DEFAULT_TOKEN_CONTRACT, BM25Config())
        )
        == ()
    )
    assert dense_candidates(request, corpus, DemoDenseAdapter()) == ()


@pytest.mark.parametrize("score", [float("nan"), float("inf"), True])
def test_invalid_scores_fail_before_ranking(score: float) -> None:
    with pytest.raises(ConfigurationError):
        rank_candidates(((small_chunk("a", "text"), score),), top_k=1, retriever="test")


def test_rank_floor_and_deterministic_ties() -> None:
    a, b, c = [small_chunk(key, "text") for key in ("a", "b", "c")]
    ranked = rank_candidates(((b, 0.5), (a, 0.5), (c, 0.0)), top_k=3, retriever="test")
    assert [item.chunk.chunk_id for item in ranked] == ["a", "b"]
    assert [item.rank for item in ranked] == [1, 2]
    assert (
        rank_candidates(((a, -0.2),), top_k=1, retriever="test", minimum_score=-0.5)[
            0
        ].score
        == -0.2
    )
    with pytest.raises(CorpusInvariantError):
        rank_candidates(((a, 1.0), (a, 2.0)), top_k=2, retriever="test")


def test_min_max_constant_extreme_and_nonfinite_scores() -> None:
    assert min_max_normalize({}) == {}
    assert min_max_normalize({"a": 5, "b": 5}) == {"a": 0, "b": 0}
    assert min_max_normalize({"a": -1e308, "b": 0, "c": 1e308}) == {
        "a": 0,
        "b": 0.5,
        "c": 1,
    }
    with pytest.raises(ConfigurationError):
        min_max_normalize({"a": float("nan")})


def test_rrf_arithmetic_provenance_and_ties() -> None:
    a, b = small_chunk("a", "text"), small_chunk("b", "text")
    result = reciprocal_rank_fusion(
        (
            (RankedCandidate(a, 100, 1, "bm25"), RankedCandidate(b, 1, 2, "bm25")),
            (RankedCandidate(b, 0.8, 1, "dense"),),
        ),
        FusionConfig(),
        top_k=2,
    )
    assert result[0].chunk == b
    assert result[0].score == pytest.approx(1 / 62 + 1 / 61)
    assert {(c.retriever, c.rank, c.raw_score) for c in result[0].contributors} == {
        ("bm25", 2, 1),
        ("dense", 1, 0.8),
    }
    tied = reciprocal_rank_fusion(
        ((RankedCandidate(b, 1, 1, "bm25"),), (RankedCandidate(a, 1, 1, "dense"),)),
        FusionConfig(),
        top_k=2,
    )
    assert [item.chunk.chunk_id for item in tied] == ["a", "b"]


@pytest.mark.parametrize(
    "mode",
    [
        "duplicate",
        "duplicate_rank",
        "gap",
        "unknown",
        "conflicting",
        "nan",
        "bool_rank",
    ],
)
def test_rrf_rejects_invalid_contributions(mode: str) -> None:
    a, b = small_chunk("a", "text"), small_chunk("b", "text")
    first = RankedCandidate(a, 1.0, 1, "bm25")
    second = {
        "duplicate": first,
        "duplicate_rank": RankedCandidate(b, 1.0, 1, "bm25"),
        "gap": RankedCandidate(b, 1.0, 3, "bm25"),
        "unknown": RankedCandidate(b, 1.0, 1, "unknown"),
        "conflicting": RankedCandidate(replace(a, text="changed"), 1.0, 1, "dense"),
        "nan": RankedCandidate(b, float("nan"), 1, "dense"),
        "bool_rank": RankedCandidate(b, 1.0, True, "dense"),
    }[mode]
    with pytest.raises((ConfigurationError, CorpusInvariantError)):
        reciprocal_rank_fusion(((first, second),), FusionConfig(), top_k=2)


@pytest.mark.parametrize(
    "config",
    [
        FusionConfig(True),
        FusionConfig(0),
        FusionConfig(weights=(("bm25", True),)),
        FusionConfig(weights=(("bm25", float("inf")),)),
        FusionConfig(weights=(("bm25", 1), ("bm25", 1))),
    ],
)
def test_invalid_fusion_configuration(config: FusionConfig) -> None:
    with pytest.raises(ConfigurationError):
        config.fingerprint()


def test_fingerprints_bind_text_metadata_parameters_and_source_versions() -> None:
    chunks = frozen_chunks()
    assert corpus_fingerprint(chunks) == corpus_fingerprint(tuple(reversed(chunks)))
    for changed in [
        replace(chunks[0], text="changed"),
        replace(chunks[0], metadata=(("supplier", "Other"),)),
        replace(chunks[0], document_version="2"),
    ]:
        assert corpus_fingerprint((changed, *chunks[1:])) != corpus_fingerprint(chunks)
    assert (
        BM25Config(1.20000000000001).fingerprint()
        != BM25Config(1.20000000000002).fingerprint()
    )
    request = RetrievalRequest(PRINCIPAL, "code", 3)
    manifest = make_manifest(
        corpus_for(request),
        DEFAULT_TOKEN_CONTRACT,
        BM25Config(),
        DemoDenseAdapter(),
        FusionConfig(),
        candidate_depth=5,
        top_k=3,
    )
    with pytest.raises(ManifestCompatibilityError):
        require_compatible(manifest, replace(manifest, candidate_depth=6))


def test_dense_configuration_drift_is_rejected() -> None:
    class Drifting:
        config = DemoDenseAdapter().config

        def score(self, query_text: str, chunk_text: str) -> float:
            self.config = replace(self.config, preprocessing_version="changed")
            return 0.5

    request = RetrievalRequest(PRINCIPAL, "payment", 3)
    with pytest.raises(ManifestCompatibilityError):
        dense_candidates(request, corpus_for(request), Drifting())


def test_local_cosine_adapter_uses_role_apis_and_checks_shape() -> None:
    adapter = LocalCosineAdapter(DemoLocalEmbeddingAdapter())
    assert adapter.score("payment approval", "Invoice after approval") == pytest.approx(
        1.0
    )
    assert adapter.config.metric == "cosine"
    with pytest.raises(VectorInvariantError):
        adapter.score("CW-1000", "payment")


def test_week06_sources_and_locations_are_unchanged() -> None:
    actual = frozen_chunks()
    for source in accepted_sources():
        expected = StructurePolicy().chunk(source)
        observed = [c for c in actual if c.document_id == source.identity.document_id]
        assert [c.chunk_id for c in observed] == [c.chunk_id for c in expected]
        assert [c.text for c in observed] == [c.text for c in expected]
        assert all(c.source_digest == source.identity.content_digest for c in observed)
        assert all(json.loads(dict(c.metadata)["source_locations"]) for c in observed)
    assert "P-106" not in {c.document_id for c in actual}
    assert quarantine_summary()["status"] == "needs_review"


def test_practice_metrics_nulls_fixed_denominator_and_sample() -> None:
    report = run_comparison()
    assert report["chunk_count"] == 11 and report["query_count"] == 14
    results = report["results"]
    assert isinstance(results, list)
    for result in results:
        assert (
            result["labelled_query_count"] == 10 and result["no_gold_query_count"] == 4
        )
        rows = result.pop("queries")
        for row in rows:
            if row["relevant_count"] == 0:
                assert row["recall_at_k"] is None and row["support_complete"] is None
            if row["query_id"] == "Q01" and result["mode"] == "sparse":
                assert row["precision_at_k"] == pytest.approx(1 / 3)
                assert row["recall_at_k"] == 1
    sample = json.loads(Path("labs/week_07/sample-comparison.json").read_text())
    # Runtime is recorded, but Python patch versions do not change hand-feature arithmetic.
    sample["dense"]["runtime_id"] = cast(dict[str, object], report["dense"])[
        "runtime_id"
    ]
    assert json.loads(json.dumps(report)) == sample


def test_evidence_labels_must_be_visible_and_true_to_the_fixture() -> None:
    cases = load_cases(Path("labs/week_07/queries.jsonl"))
    corpus = corpus_for(RetrievalRequest(PRINCIPAL, "code", 3))
    with pytest.raises(ValueError):
        measure_case(
            replace(cases[0], support=(("missing/1/1", ("CW-1000",)),)),
            corpus.chunks,
            (),
            k=3,
        )
    with pytest.raises(ValueError):
        measure_case(
            replace(cases[0], support=(("P-107/1/1", ("NOT-IN-SOURCE",)),)),
            corpus.chunks,
            (),
            k=3,
        )
