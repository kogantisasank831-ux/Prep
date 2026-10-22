from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import replace
from datetime import UTC, datetime
import json
from pathlib import Path
from types import ModuleType
from typing import cast

import pytest

from labs.week_05 import local_model, retrieval
from labs.week_05.data import CORPUS_LIMIT, load_corpus, sample_documents
from labs.week_05.demo import ADAPTER, allow_all_sample_documents, sample_index
from labs.week_05.local_model import LocalSentenceTransformer, directory_digest
from labs.week_05.metrics import evaluate_ranking
from labs.week_05.retrieval import (
    DemoLocalEmbeddingAdapter,
    DocumentRejectedError,
    EmbeddingRuntimeError,
    IndexCompatibilityError,
    InMemoryCosineIndex,
    SearchRequest,
    StaticObjectAccessPolicy,
    UntrustedDocument,
    Vector,
    VectorInvariantError,
    cosine_similarity,
    dot_product,
    euclidean_distance,
    initial_chunks,
    load_documents,
    normalize,
)

NOW = datetime(2026, 10, 22, tzinfo=UTC)


def search(index: InMemoryCosineIndex, *, k: int = 2) -> tuple[str, ...]:
    return tuple(
        result.source.document_id
        for result in index.search(
            SearchRequest("analyst", "approval before payment", k),
            adapter=ADAPTER,
            access_policy=allow_all_sample_documents("analyst"),
        )
    )


@pytest.mark.parametrize(
    "left,right,expected",
    [
        ((1.0, 0.0), (1.0, 0.0), 1.0),
        ((1.0, 0.0), (0.0, 1.0), 0.0),
        ((1.0, 0.0), (-1.0, 0.0), -1.0),
        ((1e308, 1e308), (1e308, 1e308), 1.0),
        ((1e-308, 1e-308), (1e-308, 1e-308), 1.0),
        ((5e-324, 5e-324), (5e-324, 0.0), 0.7071067811865476),
    ],
)
def test_cosine_geometry_is_stable_at_small_and_large_scales(
    left: Vector, right: Vector, expected: float
) -> None:
    assert cosine_similarity(left, right) == pytest.approx(expected, abs=1e-12)
    assert dot_product(normalize(left), normalize(right)) == pytest.approx(
        expected, abs=1e-12
    )


@pytest.mark.parametrize(
    "vector",
    [
        (),
        (0.0, 0.0),
        (float("nan"), 1.0),
        (float("inf"), 1.0),
        (True, 1.0),
        ("bad", 1.0),
    ],
)
def test_vector_boundary_rejects_undefined_or_invalid_values(
    vector: tuple[object, ...],
) -> None:
    with pytest.raises(VectorInvariantError):
        normalize(cast(Vector, vector))


def test_metric_shape_and_finite_range_errors_are_explicit() -> None:
    with pytest.raises(VectorInvariantError):
        cosine_similarity((1.0,), (1.0, 2.0))
    with pytest.raises(VectorInvariantError):
        dot_product((1e308,), (1e308,))
    with pytest.raises(VectorInvariantError):
        euclidean_distance((1e308,), (-1e308,))
    assert euclidean_distance((0.0, 0.0), (3.0, 4.0)) == 5.0


def test_sample_search_returns_traceable_payment_candidates() -> None:
    index = sample_index()
    assert search(index) == ("P-101", "P-104")
    assert index.manifest.vector_count == 4
    result = index.search(
        SearchRequest("analyst", "approval before payment", 1),
        adapter=ADAPTER,
        access_policy=allow_all_sample_documents("analyst"),
    )[0]
    assert result.provenance.source_digest == result.source.content_digest
    assert result.provenance.index_id == index.manifest.index_id
    assert result.provenance.document_version == "1"


def test_tie_order_and_index_identity_do_not_depend_on_input_order() -> None:
    reverse = InMemoryCosineIndex.build(
        tuple(reversed(initial_chunks(sample_documents()))), ADAPTER, created_at=NOW
    )
    assert search(reverse) == search(sample_index())
    assert reverse.manifest.index_id == sample_index().manifest.index_id


def test_changed_document_version_and_content_require_a_new_index() -> None:
    sources = list(sample_documents())
    sources[0] = load_documents(
        [
            UntrustedDocument(
                "northwind-procurement",
                "P-101",
                "2",
                sources[0].title,
                "Payment is due immediately on receipt.",
            )
        ]
    )[0]
    rebuilt = InMemoryCosineIndex.build(
        initial_chunks(sources), ADAPTER, created_at=NOW
    )
    assert rebuilt.manifest.corpus_digest != sample_index().manifest.corpus_digest
    assert rebuilt.manifest.index_id != sample_index().manifest.index_id


@pytest.mark.parametrize("text", ["", " ", "x" * 1001, "\ud800"])
def test_document_loader_rejects_out_of_policy_text(text: str) -> None:
    with pytest.raises(DocumentRejectedError):
        load_documents([UntrustedDocument("tenant", "D1", "1", "title", text)])


def test_duplicate_and_invalid_source_identities_fail() -> None:
    document = UntrustedDocument("tenant", "D1", "1", "title", "payment approval")
    with pytest.raises(DocumentRejectedError):
        load_documents([document, document])
    with pytest.raises(DocumentRejectedError):
        load_documents([replace(document, document_id="bad:separator")])


@pytest.mark.parametrize(
    "raw",
    [
        b"",
        b"not json",
        b"\xff",
        b"[]",
        b"{}",
        b'{"tenant_id":"a","tenant_id":"b"}',
        b"x" * (CORPUS_LIMIT + 1),
    ],
)
def test_jsonl_loader_rejects_malformed_or_oversized_corpus(
    tmp_path: Path, raw: bytes
) -> None:
    path = tmp_path / "corpus.jsonl"
    path.write_bytes(raw)
    with pytest.raises(DocumentRejectedError):
        load_corpus(path)


def test_authorization_happens_before_scoring(monkeypatch: pytest.MonkeyPatch) -> None:
    index = sample_index()
    allowed = index.entries[0]
    forbidden_vectors = [entry.vector for entry in index.entries[1:]]
    original = retrieval.cosine_similarity
    calls: list[Vector] = []

    def score(left: Vector, right: Vector) -> float:
        assert all(right is not forbidden for forbidden in forbidden_vectors)
        calls.append(right)
        return original(left, right)

    monkeypatch.setattr(retrieval, "cosine_similarity", score)
    policy = StaticObjectAccessPolicy(
        frozenset(
            {
                (
                    "analyst",
                    allowed.source.tenant_id,
                    allowed.source.document_id,
                    allowed.source.document_version,
                )
            }
        )
    )
    result = index.search(
        SearchRequest("analyst", "approval before payment", 1),
        adapter=ADAPTER,
        access_policy=policy,
    )
    assert len(result) == len(calls) == 1
    calls.clear()
    assert (
        index.search(
            SearchRequest("denied", "approval before payment", 1),
            adapter=ADAPTER,
            access_policy=policy,
        )
        == ()
    )
    assert calls == []


def test_other_tenant_and_old_version_are_not_retrievable() -> None:
    extra = load_documents(
        [
            UntrustedDocument(
                "other-tenant",
                "SECRET",
                "1",
                "private",
                "Payment is due after approval.",
            )
        ]
    )
    index = InMemoryCosineIndex.build(
        initial_chunks((*sample_documents(), *extra)), ADAPTER, created_at=NOW
    )
    assert "SECRET" not in search(index, k=4)
    wrong_version = StaticObjectAccessPolicy(
        frozenset({("analyst", "northwind-procurement", "P-101", "0")})
    )
    assert (
        index.search(
            SearchRequest("analyst", "approval", 1),
            adapter=ADAPTER,
            access_policy=wrong_version,
        )
        == ()
    )


@pytest.mark.parametrize(
    "query,k",
    [
        ("", 1),
        (" ", 1),
        ("x" * 1001, 1),
        ("\ud800", 1),
        ("approval", 0),
        ("approval", -1),
        ("approval", True),
        ("approval", 5),
    ],
)
def test_invalid_queries_and_cutoffs_fail(query: str, k: int) -> None:
    with pytest.raises(ValueError):
        sample_index().search(
            SearchRequest("analyst", query, k),
            adapter=ADAPTER,
            access_policy=allow_all_sample_documents("analyst"),
        )


def test_model_compatibility_is_more_than_dimension() -> None:
    changed = DemoLocalEmbeddingAdapter(
        replace(ADAPTER.identity, artifact_digest="changed")
    )
    with pytest.raises(IndexCompatibilityError):
        sample_index().search(
            SearchRequest("analyst", "approval", 1),
            adapter=changed,
            access_policy=allow_all_sample_documents("analyst"),
        )


class DriftingAdapter:
    def __init__(self) -> None:
        self.identity = ADAPTER.identity

    def embed_documents(self, texts: Sequence[str]) -> tuple[Vector, ...]:
        self.identity = replace(self.identity, artifact_digest="changed-during-call")
        return ADAPTER.embed_documents(texts)

    def embed_queries(self, texts: Sequence[str]) -> tuple[Vector, ...]:
        self.identity = replace(self.identity, artifact_digest="changed-during-call")
        return ADAPTER.embed_queries(texts)


def test_observed_identity_drift_is_rejected_during_build_and_search() -> None:
    with pytest.raises(IndexCompatibilityError):
        InMemoryCosineIndex.build(
            initial_chunks(sample_documents()), DriftingAdapter(), created_at=NOW
        )
    with pytest.raises(IndexCompatibilityError):
        sample_index().search(
            SearchRequest("analyst", "approval", 1),
            adapter=DriftingAdapter(),
            access_policy=allow_all_sample_documents("analyst"),
        )


def test_tampered_manifest_and_source_digest_are_rejected() -> None:
    index = sample_index()
    with pytest.raises(IndexCompatibilityError):
        replace(index, manifest=replace(index.manifest, corpus_digest="0" * 64))
    with pytest.raises(IndexCompatibilityError):
        replace(
            index,
            entries=(
                replace(
                    index.entries[0],
                    source=replace(index.entries[0].source, text="changed"),
                ),
                *index.entries[1:],
            ),
        )
    with pytest.raises(VectorInvariantError):
        replace(
            index,
            entries=(replace(index.entries[0], vector=(1.0,)), *index.entries[1:]),
        )


def test_embedding_batch_cardinality_is_checked() -> None:
    class EmptyAdapter:
        identity = ADAPTER.identity

        def embed_documents(self, texts: Sequence[str]) -> tuple[Vector, ...]:
            return ()

        def embed_queries(self, texts: Sequence[str]) -> tuple[Vector, ...]:
            return ()

    with pytest.raises(EmbeddingRuntimeError):
        InMemoryCosineIndex.build(
            initial_chunks(sample_documents()), EmptyAdapter(), created_at=NOW
        )
    with pytest.raises(EmbeddingRuntimeError):
        sample_index().search(
            SearchRequest("analyst", "approval", 1),
            adapter=EmptyAdapter(),
            access_policy=allow_all_sample_documents("analyst"),
        )


@pytest.mark.parametrize("dimension", [0, -1, True])
def test_embedding_identity_dimension_is_a_positive_integer(dimension: int) -> None:
    with pytest.raises(ValueError):
        replace(ADAPTER.identity, dimension=dimension)


def test_worked_relevance_metrics_match_independent_arithmetic() -> None:
    ranked = ["P-103", "P-101", "P-102", "P-104"]
    gold = frozenset({"P-101", "P-104"})
    top2 = evaluate_ranking(ranked, gold, k=2)
    assert top2.precision_at_k == top2.recall_at_k == top2.reciprocal_rank_at_k == 0.5
    top4 = evaluate_ranking(ranked, gold, k=4)
    assert top4.precision_at_k == 0.5
    assert top4.recall_at_k == 1.0
    assert top4.ndcg_at_k == pytest.approx(0.6509209298)


def test_metric_missing_results_and_no_gold_policy_are_explicit() -> None:
    assert evaluate_ranking(["P-101"], frozenset({"P-101"}), k=2).precision_at_k == 0.5
    empty = evaluate_ranking([], frozenset({"P-101"}), k=2)
    assert empty.recall_at_k == empty.ndcg_at_k == empty.reciprocal_rank_at_k == 0.0
    no_gold = evaluate_ranking(["P-101"], frozenset(), k=2)
    assert (
        no_gold.recall_at_k is no_gold.ndcg_at_k is no_gold.reciprocal_rank_at_k is None
    )
    with pytest.raises(ValueError):
        evaluate_ranking(["P-101", "P-101"], frozenset({"P-101"}), k=2)


class FakeArray:
    def __init__(self, data: object) -> None:
        self.data = data

    def tolist(self) -> object:
        return self.data


class FakeTokenizer:
    def __call__(
        self, texts: list[str], *, add_special_tokens: bool, truncation: bool
    ) -> Mapping[str, object]:
        assert add_special_tokens and not truncation
        return {"input_ids": [list(range(len(text.split()) + 2)) for text in texts]}


class FakeBackend:
    max_seq_length = 16
    tokenizer: local_model.Tokenizer = FakeTokenizer()

    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []
        self.result: object | None = None

    def get_sentence_embedding_dimension(self) -> int | None:
        return 2

    def encode_query(self, texts: list[str], **kwargs: object) -> FakeArray:
        self.calls.append(("query", kwargs["prompt"]))
        return FakeArray(
            self.result if self.result is not None else [[1.0, 2.0] for _ in texts]
        )

    def encode_document(self, texts: list[str], **kwargs: object) -> FakeArray:
        self.calls.append(("document", kwargs["prompt"]))
        return FakeArray(
            self.result if self.result is not None else [[2.0, 1.0] for _ in texts]
        )


def local_adapter(backend: FakeBackend) -> LocalSentenceTransformer:
    return LocalSentenceTransformer(
        backend=backend,
        model_id="fake",
        artifact_digest="test",
        runtime_version="test",
        query_prefix="query: ",
        document_prefix="passage: ",
    )


def test_local_adapter_preserves_query_and_document_encoding_roles() -> None:
    backend = FakeBackend()
    adapter = local_adapter(backend)
    assert adapter.embed_queries(["payment"]) == ((1.0, 2.0),)
    assert adapter.embed_documents(["approval"]) == ((2.0, 1.0),)
    assert backend.calls == [("query", "query: "), ("document", "passage: ")]
    assert adapter.identity.dimension == 2
    assert adapter.embed_queries([]) == ()


def test_local_adapter_refuses_silent_token_truncation() -> None:
    backend = FakeBackend()
    with pytest.raises(EmbeddingRuntimeError):
        local_adapter(backend).embed_queries(["word " * 20])
    assert backend.calls == []


@pytest.mark.parametrize(
    "raw", [[], [[1.0]], [[True, 1.0]], [["1", "2"]], [[float("nan"), 1.0]]]
)
def test_local_adapter_checks_returned_vector_contract(raw: object) -> None:
    backend = FakeBackend()
    backend.result = raw
    with pytest.raises((EmbeddingRuntimeError, VectorInvariantError)):
        local_adapter(backend).embed_documents(["approval"])


def test_directory_digest_tracks_names_and_contents(tmp_path: Path) -> None:
    path = tmp_path / "model"
    path.mkdir()
    weights = path / "weights.safetensors"
    weights.write_bytes(b"synthetic")
    before = directory_digest(path)
    weights.write_bytes(b"changed")
    assert directory_digest(path) != before
    before = directory_digest(path)
    weights.rename(path / "renamed.safetensors")
    assert directory_digest(path) != before
    with pytest.raises(ValueError):
        directory_digest(tmp_path / "missing")


def test_optional_model_loading_uses_local_only_arguments(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    model = tmp_path / "model"
    model.mkdir()
    (model / "weights").write_bytes(b"fixture")
    observed: dict[str, object] = {}

    def factory(path: str, **kwargs: object) -> FakeBackend:
        observed.update(kwargs)
        return FakeBackend()

    module = ModuleType("fake_sentence_transformers")
    setattr(module, "SentenceTransformer", factory)
    monkeypatch.setattr(local_model, "import_module", lambda name: module)
    monkeypatch.setattr(local_model, "version", lambda name: "test-version")
    adapter = LocalSentenceTransformer.from_directory(
        model, model_id="fixture", query_prefix="", document_prefix=""
    )
    assert observed == {
        "local_files_only": True,
        "trust_remote_code": False,
        "token": False,
        "device": "cpu",
    }
    assert adapter.identity.artifact_digest == directory_digest(model)


def test_practice_queries_reference_only_the_published_source_snapshot() -> None:
    path = Path(__file__).resolve().parents[1] / "labs/week_05/queries.jsonl"
    queries = [json.loads(line) for line in path.read_text().splitlines()]
    ids = {document.document_id for document in sample_documents()}
    assert len(queries) == len({q["query_id"] for q in queries}) == 12
    assert all(set(q["relevant_document_ids"]) <= ids for q in queries)
    assert all(q["split"] == "practice" for q in queries)
