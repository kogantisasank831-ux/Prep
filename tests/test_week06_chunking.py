"""Behavior checks for bounded parsing, evidence preservation, and comparison."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime
import json
from pathlib import Path
from typing import cast

import pytest

from labs.week_05.retrieval import VectorInvariantError
from labs.week_06.chunking import (
    BlockKind,
    Chunk,
    ChunkCollection,
    ChunkPolicyError,
    FixedSizePolicy,
    ManifestCompatibilityError,
    OverlapPolicy,
    ParentChildPolicy,
    ParseRejectedError,
    ParseStatus,
    ParsedBlock,
    SemanticPolicy,
    SentencePolicy,
    SharedTermSimilarity,
    SourceLocation,
    StaticChunkAccessPolicy,
    StructurePolicy,
    authorized_chunks,
    canonical_block_text,
    chunk_set_digest,
    digest_text,
    make_chunk,
    source_fingerprint,
)
from labs.week_06.compare import (
    TeachingEmbeddingAdapter,
    compare_policy,
    load_cases,
    normalized_batch,
    policy_candidates,
    run_comparison,
    select_context,
)
from labs.week_06.fixtures import (
    FIXED_TIME,
    PARSER,
    accepted_sources,
    block,
    fixture_documents,
    ocr_review_document,
)


def test_same_five_sources_and_quarantined_ocr() -> None:
    assert len(accepted_sources()) == 5
    result = PARSER.parse(ocr_review_document())
    assert result.status == ParseStatus.NEEDS_REVIEW
    assert result.source is not None
    assert "12.O0" in result.source.blocks[0].text
    with pytest.raises(ParseRejectedError):
        ChunkCollection.build(result.source, StructurePolicy(), created_at=FIXED_TIME)


@pytest.mark.parametrize("bad", ["", "  ", "x" * 1001, "bad\ud800text"])
def test_parser_rejects_invalid_text(bad: str) -> None:
    document = replace(
        fixture_documents()[0], raw_blocks=(block(BlockKind.PARAGRAPH, 1, 1, bad),)
    )
    assert PARSER.parse(document).status == ParseStatus.REJECTED


@pytest.mark.parametrize(
    "location",
    [
        SourceLocation(0, 1),
        SourceLocation(True, 1),
        SourceLocation(1, -1),
        SourceLocation(1, 1, "bad id"),
        SourceLocation(1, 1, row_index=True),
        SourceLocation(1, 1, start_char=0, end_char=1),
        cast(SourceLocation, None),
    ],
)
def test_parser_rejects_invalid_location(location: SourceLocation) -> None:
    document = replace(
        fixture_documents()[0],
        raw_blocks=(ParsedBlock(BlockKind.PARAGRAPH, location, "Text."),),
    )
    assert PARSER.parse(document).status == ParseStatus.REJECTED


def test_parser_preserves_review_required_table_and_rejects_duplicates() -> None:
    original = fixture_documents()[0]
    uncertain = block(BlockKind.TABLE_ROW, 1, 1, "USD 12.00 1,000 kg copper wire")
    result = PARSER.parse(replace(original, raw_blocks=(uncertain,)))
    assert result.status == ParseStatus.NEEDS_REVIEW
    assert result.source and result.source.blocks == (uncertain,)
    assert (
        PARSER.parse(replace(original, raw_blocks=original.raw_blocks * 2)).status
        == ParseStatus.REJECTED
    )
    headings = replace(
        original, raw_blocks=(block(BlockKind.HEADING, 1, 1, "Heading only"),)
    )
    assert PARSER.parse(headings).status == ParseStatus.NEEDS_REVIEW


def test_parser_resource_and_identity_bounds() -> None:
    original = fixture_documents()[0]
    assert (
        PARSER.parse(replace(original, tenant_id="../tenant")).status
        == ParseStatus.REJECTED
    )
    assert PARSER.parse(replace(original, raw_blocks=())).status == ParseStatus.REJECTED
    large = tuple(block(BlockKind.PARAGRAPH, 1, i + 1, "x" * 1000) for i in range(5))
    assert (
        PARSER.parse(replace(original, raw_blocks=large)).status == ParseStatus.REJECTED
    )


@pytest.mark.parametrize(
    "width,overlap", [(0, 0), (-1, 0), (True, 0), (120, -1), (120, 120), (120, True)]
)
def test_window_integer_contract(width: int, overlap: int) -> None:
    with pytest.raises(ChunkPolicyError):
        OverlapPolicy(width, overlap).chunk(accepted_sources()[0])


def test_overlap_has_no_redundant_tail_and_exact_spans() -> None:
    document = replace(
        fixture_documents()[0],
        raw_blocks=(block(BlockKind.PARAGRAPH, 1, 1, "x" * 200),),
    )
    result = PARSER.parse(document)
    assert result.source is not None
    chunks = OverlapPolicy(120, 40).chunk(result.source)
    assert [len(chunk.text) for chunk in chunks] == [120, 120]
    assert [
        (chunk.locations[0].start_char, chunk.locations[0].end_char) for chunk in chunks
    ] == [(0, 120), (80, 200)]


def test_fixed_windows_reconstruct_source_and_cite_only_intersecting_blocks() -> None:
    source = accepted_sources()[-1]
    chunks = FixedSizePolicy(40).chunk(source)
    assert "".join(chunk.text for chunk in chunks) == canonical_block_text(
        source.blocks
    )
    assert chunks[0].locations != tuple(block.location for block in source.blocks)
    for chunk in chunks:
        for location in chunk.locations:
            assert location.start_char is not None and location.end_char is not None
            matching = next(
                block
                for block in source.blocks
                if block.location == replace(location, start_char=None, end_char=None)
            )
            assert (
                matching.text.strip()[location.start_char : location.end_char]
                in chunk.text
            )


@pytest.mark.parametrize(
    "policy",
    [
        SentencePolicy(120),
        SemanticPolicy(SharedTermSimilarity(), 0.1),
        StructurePolicy(),
        ParentChildPolicy(),
    ],
)
def test_readable_policies_keep_all_p105_evidence(
    policy: SentencePolicy | SemanticPolicy | StructurePolicy | ParentChildPolicy,
) -> None:
    source = accepted_sources()[-1]
    text = "\n".join(chunk.text for chunk in policy.chunk(source))
    for original in source.blocks:
        assert original.text in text


def test_sentence_width_is_a_soft_target() -> None:
    source = accepted_sources()[0]
    assert any(len(chunk.text) > 10 for chunk in SentencePolicy(10).chunk(source))
    with pytest.raises(ChunkPolicyError):
        SentencePolicy(False).chunk(source)


@pytest.mark.parametrize("threshold", [float("nan"), float("inf"), -0.1, 1.1, True])
def test_semantic_threshold_validation(threshold: float) -> None:
    with pytest.raises(ChunkPolicyError):
        SemanticPolicy(SharedTermSimilarity(), threshold).chunk(accepted_sources()[-1])


def test_ids_bind_source_version_parser_and_layout() -> None:
    source = accepted_sources()[0]
    policy = FixedSizePolicy(120)
    first = policy.chunk(source)
    assert first == policy.chunk(source)
    for changed in [
        replace(source, parser_version="2"),
        replace(source, identity=replace(source.identity, version="2")),
        replace(
            source, blocks=(replace(source.blocks[0], location=SourceLocation(2, 1)),)
        ),
    ]:
        assert source_fingerprint(source) != source_fingerprint(changed)
        assert first[0].chunk_id != policy.chunk(changed)[0].chunk_id


def test_source_digest_and_timezone_checked() -> None:
    source = accepted_sources()[0]
    with pytest.raises(ManifestCompatibilityError):
        ChunkCollection.build(
            replace(
                source,
                identity=replace(
                    source.identity, content_digest=digest_text("changed")
                ),
            ),
            FixedSizePolicy(120),
            created_at=FIXED_TIME,
        )
    with pytest.raises(ValueError):
        ChunkCollection.build(
            source, FixedSizePolicy(120), created_at=datetime(2026, 10, 22)
        )


def test_manifest_checksum_and_identity_validation() -> None:
    source = accepted_sources()[0]
    collection = ChunkCollection.build(
        source, FixedSizePolicy(40), created_at=FIXED_TIME
    )
    changed = (replace(collection.chunks[0], text="Tampered"), *collection.chunks[1:])
    with pytest.raises(ManifestCompatibilityError):
        replace(collection, chunks=changed)
    foreign = (
        replace(
            collection.chunks[0],
            source_identity=replace(source.identity, tenant_id="other"),
        ),
        *collection.chunks[1:],
    )
    with pytest.raises(ManifestCompatibilityError):
        replace(
            collection,
            chunks=foreign,
            manifest=replace(
                collection.manifest, contents_digest=chunk_set_digest(foreign)
            ),
        )


def test_chunk_location_must_resolve_to_source() -> None:
    source = accepted_sources()[0]
    for location in [
        SourceLocation(9, 1),
        SourceLocation(1, 1, start_char=0),
        SourceLocation(1, 1, start_char=0, end_char=999),
    ]:
        with pytest.raises(ChunkPolicyError):
            make_chunk(
                source,
                FixedSizePolicy(120).identity,
                ordinal=0,
                text="Text",
                locations=[location],
            )


def test_parent_lineage_dedup_budget_and_authorization() -> None:
    source = accepted_sources()[-1]
    collection = ChunkCollection.build(
        source, ParentChildPolicy(), created_at=FIXED_TIME
    )
    children = [
        chunk
        for chunk in collection.chunks
        if chunk.parent_chunk_id is not None
        and "Invoicing" not in chunk.text
        and chunk.locations[0].block_index in {8, 9}
    ]
    allowed = StaticChunkAccessPolicy(
        frozenset({("reviewer", "northwind-procurement", "P-105", "1")})
    )
    context = select_context(
        children,
        collection.chunks,
        principal_id="reviewer",
        access=allowed,
        budget_chars=800,
    )
    assert len(context) == 1
    assert "Section 3" in context[0].text and "controls Schedule A" in context[0].text
    assert (
        select_context(
            children,
            collection.chunks,
            principal_id="reviewer",
            access=allowed,
            budget_chars=10,
        )
        == ()
    )
    assert authorized_chunks("other", collection.chunks, allowed) == ()
    assert (
        select_context(
            children,
            collection.chunks,
            principal_id="other",
            access=allowed,
            budget_chars=800,
        )
        == ()
    )

    class ChildOnly:
        def can_read(self, principal_id: str, chunk: Chunk) -> bool:
            return chunk.parent_chunk_id is not None

    assert (
        select_context(
            children,
            collection.chunks,
            principal_id="reviewer",
            access=ChildOnly(),
            budget_chars=800,
        )
        == ()
    )
    foreign = replace(
        children[0], source_identity=replace(source.identity, version="2")
    )
    with pytest.raises(ManifestCompatibilityError):
        select_context(
            [foreign],
            (*collection.chunks, foreign),
            principal_id="reviewer",
            access=ChildOnly(),
            budget_chars=800,
        )


def test_parent_policy_does_not_drop_isolated_heading() -> None:
    document = replace(
        fixture_documents()[0],
        raw_blocks=(
            block(BlockKind.HEADING, 1, 1, "First heading"),
            block(BlockKind.HEADING, 1, 2, "Second heading"),
            block(BlockKind.PARAGRAPH, 1, 3, "Body."),
        ),
    )
    result = PARSER.parse(document)
    assert result.source is not None
    text = "\n".join(chunk.text for chunk in ParentChildPolicy().chunk(result.source))
    assert "First heading" in text and "Second heading" in text and "Body." in text


def test_vector_contract_in_comparison() -> None:
    for vectors in [(), ((0.0, 0.0),), ((float("nan"), 1.0),), ((1.0,),)]:
        with pytest.raises(VectorInvariantError):
            normalized_batch(vectors, count=1, dimension=2)


def test_comparison_scope_metrics_and_sample() -> None:
    report = run_comparison()
    assert report["source_count"] == 5 and report["query_count"] == 9
    results = report["results"]
    assert isinstance(results, list) and len(results) == 6
    assert len({result["corpus_fingerprint"] for result in results}) == 1
    fixed, overlap, _, _, _, parent = results
    assert fixed["stored_chunk_count"] == fixed["indexed_chunk_count"] == 8
    assert fixed["stored_text_utf8_bytes"] == 763
    assert fixed["packed_float32_vector_bytes_estimate"] == 8 * 6 * 4
    assert overlap["stored_chunk_count"] == 9
    assert parent["stored_chunk_count"] == 17 and parent["indexed_chunk_count"] == 9
    for result in results:
        assert (
            result["labelled_query_count"] == 7 and result["no_gold_query_count"] == 2
        )
        assert (
            result["generated_answer_quality"] is None
            and result["average_tokens"] is None
        )
        for query in result.pop("queries"):
            assert query["context_chars"] <= 800
            if query["query_id"] in {"Q08", "Q09"}:
                assert query["document_recall_at_chunk_k"] is None
                assert query["complete_support_source_fraction"] is None
    expected = json.loads(Path("labs/week_06/sample-comparison.json").read_text())
    assert json.loads(json.dumps(report)) == expected


def test_comparison_rejects_ambiguous_snapshot_and_bad_budget() -> None:
    sources = accepted_sources()
    cases = load_cases(Path("labs/week_06/queries.jsonl"))
    for k, budget in [(0, 800), (True, 800), (3, 0), (3, True)]:
        with pytest.raises(ValueError):
            compare_policy(
                sources,
                cases,
                policy_candidates()[0],
                TeachingEmbeddingAdapter(),
                k=k,
                context_budget_chars=budget,
            )
    with pytest.raises(ValueError):
        compare_policy(
            (*sources, sources[0]),
            cases,
            FixedSizePolicy(120),
            TeachingEmbeddingAdapter(),
        )
    with pytest.raises(ValueError):
        compare_policy(
            sources[:1], cases, FixedSizePolicy(120), TeachingEmbeddingAdapter()
        )


@pytest.mark.parametrize(
    "content",
    [
        "",
        "{}",
        '{"query_id":"Q","split":"holdout","text":"test","support":{}}',
        '{"query_id":"Q","split":"practice","text":"test","support":{"P-101":[]}}',
    ],
)
def test_practice_loader_rejects_bad_inputs(tmp_path: Path, content: str) -> None:
    path = tmp_path / "queries.jsonl"
    path.write_text(content)
    with pytest.raises(ValueError):
        load_cases(path)
