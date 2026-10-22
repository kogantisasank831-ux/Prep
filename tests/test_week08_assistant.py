"""Behavioral coverage for the Week 8 ingestion-to-citation boundary."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import replace
import json
import logging
from pathlib import Path
from types import ModuleType
from typing import cast

import pytest

from labs.week_07.fixtures import frozen_chunks
from labs.week_07.retrieval import (
    AuthorizedCorpus,
    FusedCandidate,
    ManifestCompatibilityError,
    MetadataFilter,
    RetrievalRequest,
    StaticObjectAccessPolicy,
)
from labs.week_08.compare import run_comparison
from labs.week_08.data import IngestionError, demo_access, evidence_keys, load_corpus
from labs.week_08.demo import SafeEventFormatter
from labs.week_08.local_reranker import LocalCrossEncoder, PairTokenizer
from labs.week_08.pipeline import (
    EvidenceSpan,
    KnowledgeAssistant,
    PipelineConfig,
    PipelineError,
    ScoredChunk,
    TeachingPairScorer,
    context_json,
    deduplicate,
    pack_context,
    query_plan,
    rerank,
    validate_citations,
)

CORPUS = Path(__file__).parents[1] / "labs/week_08/corpus.jsonl"
QUESTION = (
    "What payment condition controls Schedule A for the 1,000 kg copper-wire line?"
)


def request(query: str = QUESTION, *, principal: str = "analyst") -> RetrievalRequest:
    return RetrievalRequest(
        principal, query, 3, (MetadataFilter("document_type", "framework_agreement"),)
    )


def test_ingestion_preserves_existing_sources_and_quarantine() -> None:
    ingested = load_corpus(CORPUS)
    assert ingested.accepted_documents == 8 and len(ingested.chunks) == 12
    assert len(ingested.issues) == 1
    assert ingested.issues[0].source_key.endswith("P-106/1")
    assert ingested.issues[0].status == "needs_review"
    visible = AuthorizedCorpus.build(
        RetrievalRequest("analyst", "CW-1000", 3), ingested.chunks, demo_access()
    ).chunks
    assert len(visible) == 11
    old = {chunk.chunk_id: chunk for chunk in frozen_chunks()}
    assert set(old) == {chunk.chunk_id for chunk in visible}
    for chunk in visible:
        previous = old[chunk.chunk_id]
        assert (chunk.text, chunk.source_digest) == (
            previous.text,
            previous.source_digest,
        )
        assert (
            dict(chunk.metadata)["source_locations"]
            == dict(previous.metadata)["source_locations"]
        )


def test_ingestion_is_idempotent_but_conflicting_version_fails(tmp_path: Path) -> None:
    first = CORPUS.read_text().splitlines()[0]
    path = tmp_path / "input.jsonl"
    path.write_text(first + "\n" + first)
    assert load_corpus(path).accepted_documents == 1
    changed = json.loads(first)
    changed["blocks"][0]["text"] = "Changed immutable source."
    path.write_text(first + "\n" + json.dumps(changed))
    with pytest.raises(IngestionError, match="conflicting"):
        load_corpus(path)


@pytest.mark.parametrize(
    "data",
    [
        b"",
        b"{",
        b"\xff",
        b"{}",
        b'{"tenant_id":"a","tenant_id":"b"}',
        b"x" * (128 * 1024 + 1),
    ],
)
def test_malformed_ingestion_fails(data: bytes, tmp_path: Path) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_bytes(data)
    with pytest.raises(IngestionError):
        load_corpus(path)


@pytest.mark.parametrize(
    "mutate", ["bool_page", "unknown_kind", "empty_supplier", "unknown_field"]
)
def test_ingestion_schema_is_strict(mutate: str, tmp_path: Path) -> None:
    record = json.loads(CORPUS.read_text().splitlines()[0])
    if mutate == "bool_page":
        record["blocks"][0]["page"] = True
    elif mutate == "unknown_kind":
        record["blocks"][0]["kind"] = "execute"
    elif mutate == "empty_supplier":
        record["supplier"] = ""
    else:
        record["grant_access"] = True
    path = tmp_path / "bad.jsonl"
    path.write_text(json.dumps(record))
    with pytest.raises(IngestionError):
        load_corpus(path)


def test_parser_rejection_is_retained_as_an_issue(tmp_path: Path) -> None:
    record = json.loads(CORPUS.read_text().splitlines()[0])
    record["blocks"].append(record["blocks"][0])
    path = tmp_path / "rejected.jsonl"
    path.write_text(json.dumps(record))
    result = load_corpus(path)
    assert not result.chunks and result.accepted_documents == 0
    assert result.issues[0].status == "rejected"


@pytest.mark.parametrize(
    "rewrite",
    ["CW-1000 Net 30", "CW1000 Net 30 after approval", "CW-1000 Net 15 after approval"],
)
def test_rewrite_cannot_drop_code_number_or_condition(rewrite: str) -> None:
    with pytest.raises(PipelineError):
        query_plan("CW-1000 Net 30 after approval", (rewrite,))


def test_query_variants_keep_original_and_guard_is_only_lexical() -> None:
    original = "CW-1000 Net 30 after approval"
    assert (
        query_plan(original, (original, "CW-1000 terms Net 30 after approval"))[0]
        == original
    )
    assert len(query_plan(original, (original,))) == 1
    # Same protected words can reverse a relation. A human still reviews meaning.
    assert query_plan(original, ("approval after Net 30 CW-1000",))[1].startswith(
        "approval after"
    )
    with pytest.raises(PipelineError):
        query_plan(original, (original,) * 3)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"candidate_count": True},
        {"retrieval_depth": 5},
        {"evidence_count": 7},
        {"context_chars": 1},
        {"context_chars": 16001},
        {"compression": "summary"},
        {"max_sentences": 0},
    ],
)
def test_configuration_rejects_invalid_budgets(kwargs: dict[str, object]) -> None:
    factory = cast(Callable[..., PipelineConfig], PipelineConfig)
    with pytest.raises(PipelineError):
        factory(**kwargs)


def test_reranking_promotes_missing_clause_from_exactly_the_same_pool() -> None:
    ingested = load_corpus(CORPUS)
    result = KnowledgeAssistant(ingested.chunks, demo_access()).ask(request())
    before = [
        dict(item.chunk.metadata)["evidence_key"] for item in result.candidates[:3]
    ]
    after = [dict(item.chunk.metadata)["evidence_key"] for item in result.reranked[:3]]
    assert "P-105/1/8" not in before
    assert set(after) == {"P-105/1/6", "P-105/1/8", "P-105/1/9"}
    assert {item.chunk for item in result.candidates} == {
        item.chunk for item in result.reranked
    }
    assert result.answer_mode == "cited_extractive"
    assert all(f"[{span.citation_id}]" in result.answer for span in result.citations)
    assert "Net 30 after inspection approval" in result.answer


class ScriptedScorer:
    identity = TeachingPairScorer().identity

    def __init__(self, values: object, *, drift: bool = False) -> None:
        self.values = values
        self.drift = drift
        self.seen: list[tuple[str, str]] = []

    def score_pairs(self, pairs: Sequence[tuple[str, str]]) -> tuple[float, ...]:
        self.seen.extend(pairs)
        if self.drift:
            self.identity = replace(self.identity, version="changed")
        if self.values is None:
            return tuple(0.0 for _ in pairs)
        return cast(tuple[float, ...], self.values)


@pytest.mark.parametrize("values", [(), (float("nan"),), (float("inf"),), (True,)])
def test_bad_pair_scores_fail(values: object) -> None:
    chunk = frozen_chunks()[0]
    with pytest.raises(PipelineError):
        rerank("payment", (FusedCandidate(chunk, 1, 1, ()),), ScriptedScorer(values))


def test_reranker_identity_drift_fails() -> None:
    chunk = frozen_chunks()[0]
    with pytest.raises(ManifestCompatibilityError):
        rerank(
            "payment",
            (FusedCandidate(chunk, 1, 1, ()),),
            ScriptedScorer((1.0,), drift=True),
        )


def test_scorer_sees_original_query_and_only_authorized_candidates() -> None:
    ingested = load_corpus(CORPUS)
    scorer = ScriptedScorer(None)
    assistant = KnowledgeAssistant(ingested.chunks, demo_access(), scorer=scorer)
    assistant.ask(
        RetrievalRequest("analyst", "CW-1000", 3), rewrites=("CW-1000 catalogue",)
    )
    assert scorer.seen and all(query == "CW-1000" for query, _ in scorer.seen)
    assert all("SECRET-900" not in passage for _, passage in scorer.seen)


def test_denied_document_cannot_change_result_or_manifest() -> None:
    chunks = load_corpus(CORPUS).chunks
    public = tuple(chunk for chunk in chunks if chunk.document_id != "PRIVATE")
    first = KnowledgeAssistant(public, demo_access()).ask(
        RetrievalRequest("analyst", "CW-1000", 3)
    )
    second = KnowledgeAssistant(chunks, demo_access()).ask(
        RetrievalRequest("analyst", "CW-1000", 3)
    )
    assert first == second
    denied = KnowledgeAssistant(chunks, demo_access()).ask(
        request(principal="stranger")
    )
    assert denied.status == "no_evidence" and not denied.citations
    secret = KnowledgeAssistant(chunks, demo_access()).ask(
        RetrievalRequest("analyst", "SECRET-900", 3)
    )
    assert secret.status == "no_evidence" and not secret.candidates


def test_dedup_keeps_other_versions_sources_and_complementary_clauses() -> None:
    original = frozen_chunks()[0]
    variants = (
        original,
        replace(original, chunk_id="duplicate"),
        replace(original, chunk_id="version2", document_version="2"),
        replace(original, chunk_id="otherdoc", document_id="OTHER"),
        replace(original, chunk_id="otherclause", text="A different clause."),
    )
    kept, dropped = deduplicate(
        tuple(ScoredChunk(chunk, 1, rank) for rank, chunk in enumerate(variants, 1))
    )
    assert dropped == ("duplicate",)
    assert [item.chunk.chunk_id for item in kept] == [
        variants[i].chunk_id for i in (0, 2, 3, 4)
    ]


def test_context_counts_serialized_headers_and_does_not_slice_a_source() -> None:
    chunk = frozen_chunks()[0]
    access = demo_access()
    ranked = (ScoredChunk(chunk, 1, 1),)
    full = pack_context("payment", ranked, "analyst", access, PipelineConfig())
    exact_size = len(context_json(full))
    assert exact_size > len(chunk.text)
    assert (
        pack_context(
            "payment",
            ranked,
            "analyst",
            access,
            PipelineConfig(context_chars=exact_size),
        )
        == full
    )
    assert not pack_context(
        "payment",
        ranked,
        "analyst",
        access,
        PipelineConfig(context_chars=exact_size - 1),
    )
    result = KnowledgeAssistant(
        (chunk,), access, config=PipelineConfig(context_chars=2)
    ).ask(RetrievalRequest("analyst", "invoice", 3))
    assert result.status == "context_budget_exhausted" and result.context == "[]"


def test_sentence_compression_can_drop_a_qualifier_while_offsets_still_validate() -> (
    None
):
    chunk = replace(
        frozen_chunks()[0],
        text="Payment is due. Except disputed invoices require approval.",
    )
    spans = pack_context(
        "payment due",
        (ScoredChunk(chunk, 1, 1),),
        "analyst",
        demo_access(),
        PipelineConfig(compression="sentences", max_sentences=1),
    )
    assert len(spans) == 1 and "Except" not in spans[0].quote
    validate_citations(spans, (chunk,), "analyst", demo_access())


def test_table_rows_remain_atomic_under_sentence_compression() -> None:
    chunk = next(
        chunk
        for chunk in frozen_chunks()
        if ":row-" in dict(chunk.metadata)["source_locations"]
    )
    spans = pack_context(
        "price",
        (ScoredChunk(chunk, 1, 1),),
        "analyst",
        demo_access(),
        PipelineConfig(compression="sentences", max_sentences=1),
    )
    assert len(spans) == 1 and spans[0].quote == chunk.text


@pytest.mark.parametrize(
    "forgery", ["quote", "offset", "bool_offset", "label", "version", "duplicate"]
)
def test_invalid_citations_fail(forgery: str) -> None:
    chunk = frozen_chunks()[0]
    span = EvidenceSpan("S1", chunk, 0, len(chunk.text), chunk.text)
    if forgery == "quote":
        span = replace(span, quote="invented")
    elif forgery == "offset":
        span = replace(span, end=len(chunk.text) + 1)
    elif forgery == "bool_offset":
        span = replace(span, start=True)
    elif forgery == "label":
        span = replace(span, citation_id="../file")
    elif forgery == "version":
        span = replace(span, chunk=replace(chunk, document_version="2"))
    spans = (span, span) if forgery == "duplicate" else (span,)
    with pytest.raises(PipelineError):
        validate_citations(spans, (chunk,), "analyst", demo_access())


def test_logging_contains_counts_and_identity_without_payload(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.INFO, logger="labs.week_08.pipeline"):
        KnowledgeAssistant(load_corpus(CORPUS).chunks, demo_access()).ask(
            request(), request_id="test-request"
        )
    record = caplog.records[-1]
    text = SafeEventFormatter().format(record)
    assert "test-request" in text and "manifest_fingerprint" in text
    assert "1,000" not in text and "Net 30" not in text and "USD" not in text


class FakeTokenizer:
    model_max_length = 512

    def __init__(self, length: int = 8) -> None:
        self.length = length

    def __call__(
        self,
        first: list[str],
        second: list[str],
        *,
        add_special_tokens: bool,
        truncation: bool,
    ) -> Mapping[str, object]:
        assert add_special_tokens and not truncation
        assert len(first) == len(second)
        return {"input_ids": [[1] * self.length for _ in first]}


class FakeArray:
    def __init__(self, values: object) -> None:
        self.values = values

    def tolist(self) -> object:
        return self.values


class FakeBackend:
    num_labels = 1
    max_seq_length = 64

    def __init__(self, values: object = None) -> None:
        self.tokenizer: PairTokenizer = FakeTokenizer()
        self.values = [0.7] if values is None else values
        self.calls = 0

    def predict(
        self,
        pairs: list[list[str]],
        *,
        prompt: str,
        batch_size: int,
        show_progress_bar: bool,
        convert_to_numpy: bool,
        apply_softmax: bool,
    ) -> FakeArray:
        assert pairs == [["query", "passage"]]
        assert prompt == "" and batch_size == 8
        assert not show_progress_bar and convert_to_numpy and not apply_softmax
        self.calls += 1
        return FakeArray(self.values)


def local(backend: FakeBackend) -> LocalCrossEncoder:
    return LocalCrossEncoder(
        backend=backend,
        model_id="fake",
        artifact_digest="fake-digest",
        runtime="fake-runtime",
        token_limit=64,
    )


def test_local_pair_backend_and_joint_limit_prevent_silent_truncation() -> None:
    backend = FakeBackend()
    assert local(backend).score_pairs((("query", "passage"),)) == (0.7,)
    backend.tokenizer = FakeTokenizer(65)
    with pytest.raises(PipelineError, match="joint token"):
        local(backend).score_pairs((("query", "passage"),))
    assert backend.calls == 1


@pytest.mark.parametrize(
    "values", [[], [[0.7]], [True], [float("nan")], [float("inf")], [0.7, 0.8]]
)
def test_local_backend_rejects_invalid_output_shapes_and_values(values: object) -> None:
    with pytest.raises(PipelineError):
        local(FakeBackend(values)).score_pairs((("query", "passage"),))


@pytest.mark.parametrize("attribute,value", [("num_labels", 2), ("max_seq_length", 65)])
def test_local_backend_runtime_drift_is_rejected(attribute: str, value: int) -> None:
    backend = FakeBackend()
    adapter = local(backend)
    setattr(backend, attribute, value)
    with pytest.raises(PipelineError):
        adapter.score_pairs((("query", "passage"),))


def test_local_loader_uses_materialized_artifact_and_offline_flags(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from labs.week_08 import local_reranker

    (tmp_path / "config.json").write_text("{}")
    calls: dict[str, object] = {}

    def factory(path: str, **kwargs: object) -> FakeBackend:
        calls.update(kwargs)
        assert path == str(tmp_path.resolve())
        return FakeBackend()

    module = ModuleType("fake_sentence_transformers")
    setattr(module, "CrossEncoder", factory)
    monkeypatch.setattr(local_reranker, "import_module", lambda name: module)
    monkeypatch.setattr(local_reranker, "version", lambda name: "test")
    adapter = LocalCrossEncoder.from_directory(
        tmp_path, model_id="fake", token_limit=64
    )
    assert adapter.identity.artifact_digest
    assert calls["local_files_only"] is True and calls["trust_remote_code"] is False
    assert calls["token"] is False and calls["device"] == "cpu"
    assert calls["max_length"] == 64 and calls["prompts"] == {
        "query": "",
        "document": "",
        "passage": "",
    }


def test_comparison_is_paired_and_sample_reproduces() -> None:
    full = run_comparison()
    assert full["query_count"] == 14 and full["labelled_query_count"] == 10
    quality = full["quality"]
    assert isinstance(quality, dict) and quality["candidate_recall"] == 1
    hybrid, reranked = quality["hybrid"], quality["reranked"]
    assert isinstance(hybrid, dict) and isinstance(reranked, dict)
    assert hybrid["recall_at_k"] == pytest.approx(29 / 30)
    assert reranked["recall_at_k"] == 1 and reranked["reciprocal_rank_at_k"] == 0.95
    rows = full.pop("queries")
    assert isinstance(rows, list) and all(
        row["status"] == "no_evidence" for row in rows if not row["labelled"]
    )
    sample = json.loads(CORPUS.with_name("sample-comparison.json").read_text())
    # Runtime identity is recorded, but the Python patch version is not a quality claim.
    sample["first_stage"]["dense"]["runtime_id"] = cast(
        dict[str, dict[str, object]], full["first_stage"]
    )["dense"]["runtime_id"]
    assert json.loads(json.dumps(full)) == sample


def test_compression_and_budget_ablations_expose_support_loss() -> None:
    compressed = run_comparison(config=PipelineConfig(compression="sentences"))[
        "quality"
    ]
    tight = run_comparison(config=PipelineConfig(context_chars=300))["quality"]
    assert isinstance(compressed, dict) and isinstance(tight, dict)
    assert compressed["context_support_complete_fraction"] == 0.9
    assert tight["context_support_complete_fraction"] == 0.7


def test_ambiguous_practice_keys_are_rejected() -> None:
    chunk = frozen_chunks()[0]
    with pytest.raises(IngestionError):
        evidence_keys(
            (chunk, replace(chunk, chunk_id="other", tenant_id="another-tenant"))
        )


def test_request_contract_and_revoked_citations_fail() -> None:
    chunk = frozen_chunks()[0]
    assistant = KnowledgeAssistant((chunk,), demo_access())
    with pytest.raises(PipelineError):
        assistant.ask(RetrievalRequest("analyst", "payment", 1))
    with pytest.raises(PipelineError):
        assistant.ask(
            RetrievalRequest("analyst", "payment", 3), request_id="line\nbreak"
        )
    span = EvidenceSpan("S1", chunk, 0, len(chunk.text), chunk.text)
    with pytest.raises(PipelineError):
        validate_citations(
            (span,), (chunk,), "analyst", StaticObjectAccessPolicy(frozenset())
        )
