"""Evaluation contracts, denominators, failure localization and review provenance."""

from __future__ import annotations

from dataclasses import replace
import json
from math import log2
from pathlib import Path
from typing import cast

import pytest

from labs.week_05.metrics import evaluate_ranking
from labs.week_07.retrieval import ConfigurationError, digest_text
from labs.week_08.data import demo_access, load_corpus
from labs.week_08.pipeline import KnowledgeAssistant, PipelineConfig
from labs.week_09.audit import (
    audit_sources,
    chunk_key,
    load_source_checks,
    validate_case_labels,
)
from labs.week_09.dataset import (
    EvaluationCase,
    EvaluationDataError,
    load_cases,
    read_records,
)
from labs.week_09.metrics import (
    atom_coverage,
    exact_match,
    graded_ndcg,
    normalize_answer,
)
from labs.week_09.reviews import AXES, review_template, summarize_reviews
from labs.week_09.run import (
    CORPUS_PATH,
    DATASET_DIR,
    run_evaluation,
    save_run,
    score_result,
)


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> Path:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows))
    return path


def case_result(index: int = 8) -> tuple[EvaluationCase, object]:
    case = load_cases(DATASET_DIR / "cases.jsonl")[index]
    ingested = load_corpus(CORPUS_PATH)
    result = KnowledgeAssistant(ingested.chunks, demo_access()).ask(
        case.request(top_k=3)
    )
    return case, result


def test_dataset_has_30_unique_visible_cases_and_scoped_reference_citations() -> None:
    cases = load_cases(DATASET_DIR / "cases.jsonl")
    assert len(cases) == len({case.query_id for case in cases}) == 30
    assert sum(case.answerable for case in cases) == 22
    assert all(case.split == "practice" and case.reference_answers for case in cases)
    cross_reference = cases[8]
    assert len(cross_reference.evidence) == 3
    assert {label.document_id for label in cross_reference.evidence} == {"P-105"}
    assert len({label.location for label in cross_reference.evidence}) == 3
    checks = load_source_checks(DATASET_DIR / "source_checks.jsonl")
    validate_case_labels(cases, checks, demo_access(), read_records(CORPUS_PATH))


@pytest.mark.parametrize(
    "raw",
    [
        b"",
        b"{",
        b"[]",
        b"\xff",
        b'{"a":1,"a":2}',
        b'{"a":NaN}',
        b'{"a":Infinity}',
        b"x" * (256 * 1024 + 1),
    ],
)
def test_jsonl_boundary_rejects_invalid_input(raw: bytes, tmp_path: Path) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_bytes(raw)
    with pytest.raises(EvaluationDataError):
        read_records(path)


@pytest.mark.parametrize(
    "change",
    [
        "duplicate_id",
        "missing_field",
        "extra_field",
        "not_bool",
        "hidden_split",
        "no_reference",
        "missing_gold",
        "unsafe_id",
        "unknown_filter",
    ],
)
def test_case_schema_and_answerability_are_validated(
    change: str, tmp_path: Path
) -> None:
    original = dict(read_records(DATASET_DIR / "cases.jsonl")[0])
    rows = [original]
    if change == "duplicate_id":
        rows.append(dict(original))
    elif change == "missing_field":
        original.pop("category")
    elif change == "extra_field":
        original["invented_score"] = 1
    elif change == "not_bool":
        original["answerable"] = 1
    elif change == "hidden_split":
        original["split"] = "held_out"
    elif change == "no_reference":
        original["reference_answers"] = []
    elif change == "missing_gold":
        original["evidence"] = []
    elif change == "unsafe_id":
        original["query_id"] = "../unsafe"
    else:
        original["filters"] = {"tenant_id": "other-tenant"}
    path = write_jsonl(tmp_path / "cases.jsonl", rows)
    with pytest.raises((EvaluationDataError, ConfigurationError)):
        load_cases(path)


def test_labels_are_checked_independently_of_predictions_and_cannot_leak_private_gold() -> (
    None
):
    cases = load_cases(DATASET_DIR / "cases.jsonl")
    checks = load_source_checks(DATASET_DIR / "source_checks.jsonl")
    raw = read_records(CORPUS_PATH)
    with pytest.raises(EvaluationDataError, match="answer atom"):
        validate_case_labels(
            (replace(cases[0], answer_atoms=("USD 99.00",)),),
            checks,
            demo_access(),
            raw,
        )
    with pytest.raises(EvaluationDataError, match="access"):
        validate_case_labels(
            (replace(cases[0], principal_id="stranger"),), checks, demo_access(), raw
        )
    with pytest.raises(EvaluationDataError, match="filters"):
        validate_case_labels(
            (replace(cases[0], filters=cases[25].filters),), checks, demo_access(), raw
        )
    altered = replace(cases[0].evidence[0], atoms=("invented price USD 99.00",))
    with pytest.raises(EvaluationDataError, match="oracle"):
        validate_case_labels(
            (replace(cases[0], evidence=(altered,)),), checks, demo_access(), raw
        )


def test_source_audit_separates_parser_status_and_lost_chunk_units() -> None:
    ingested = load_corpus(CORPUS_PATH)
    checks = load_source_checks(DATASET_DIR / "source_checks.jsonl")
    records = read_records(CORPUS_PATH)
    audit = audit_sources(records, checks, ingested)
    assert audit["status_match_count"] == 9 and audit["parsed_atom_recall"] == 1
    assert (
        audit["complete_chunk_unit_count"] == audit["expected_chunk_unit_count"] == 12
    )
    reduced = replace(
        ingested,
        chunks=tuple(
            chunk
            for chunk in ingested.chunks
            if not chunk_key(chunk).endswith("P-105/1/p1:block-8")
        ),
    )
    audit = audit_sources(records, checks, reduced)
    assert audit["parsed_atom_recall"] == 1 and audit[
        "chunk_unit_recall"
    ] == pytest.approx(11 / 12)


def test_bad_source_oracle_fails_instead_of_becoming_a_parser_failure() -> None:
    checks = load_source_checks(DATASET_DIR / "source_checks.jsonl")
    forged = replace(checks[0], units=(("p1:block-1", ("USD 99.00",)),))
    with pytest.raises(EvaluationDataError, match="absent"):
        audit_sources(
            read_records(CORPUS_PATH), (forged, *checks[1:]), load_corpus(CORPUS_PATH)
        )


def test_hand_calculated_ranking_denominators_and_graded_ndcg() -> None:
    metric = evaluate_ranking(["irrelevant", "a", "b"], frozenset({"a", "b", "c"}), k=3)
    assert metric.precision_at_k == metric.recall_at_k == pytest.approx(2 / 3)
    assert metric.reciprocal_rank_at_k == 0.5
    assert evaluate_ranking(
        ["a"], frozenset({"a"}), k=3
    ).precision_at_k == pytest.approx(1 / 3)
    grades = {"a": 3, "b": 1}
    expected = (1 + 7 / log2(3)) / (7 + 1 / log2(3))
    assert graded_ndcg(["b", "a"], grades, k=2) == pytest.approx(expected)
    assert graded_ndcg(["a", "b"], grades, k=2) == 1
    assert graded_ndcg([], {}, k=2) is None


@pytest.mark.parametrize("grade", [True, -1, 4, 1.5])
def test_graded_metrics_reject_unreviewed_grades(grade: object) -> None:
    with pytest.raises(ValueError):
        graded_ndcg(["a"], cast(dict[str, int], {"a": grade}), k=1)


def test_exact_match_preserves_product_codes_numbers_and_negation() -> None:
    assert (
        normalize_answer("  Net 30  after approval. [S1]\n") == "net 30 after approval."
    )
    assert exact_match("Net 30 [S2]", ("net 30",))
    assert not exact_match("Net 15", ("Net 30",))
    assert not exact_match("CW1000", ("CW-1000",))
    assert not exact_match("not Net 30", ("Net 30",))
    with pytest.raises(ValueError):
        exact_match("x", ())
    # Coverage is deliberately a weak proxy and must not be called correctness.
    assert atom_coverage("not Net 30", ("Net 30",)) == 1
    assert atom_coverage("anything", ()) is None


def test_missing_candidates_are_measured_as_losses_not_invalid_gold() -> None:
    from labs.week_08.pipeline import AssistantResult

    case, raw = case_result()
    assert isinstance(raw, AssistantResult)
    missing = replace(
        raw,
        candidates=(),
        reranked=(),
        citations=(),
        answer="No evidence",
        context="[]",
    )
    scores = score_result(
        case, missing, load_corpus(CORPUS_PATH).chunks, config=PipelineConfig()
    )
    assert "candidate_miss" in cast(list[str], scores["failures"])
    assert "unexpected_abstention" in cast(list[str], scores["failures"])
    assert cast(dict[str, object], scores["candidate"])["recall_at_k"] == 0


def test_context_loss_is_distinct_from_a_good_reranked_pool() -> None:
    from labs.week_08.pipeline import AssistantResult

    case, raw = case_result()
    assert isinstance(raw, AssistantResult)
    spans = tuple(span for span in raw.citations if "Net 30" not in span.quote)
    modified = replace(
        raw,
        citations=spans,
        answer="\n".join(f"{span.quote} [{span.citation_id}]" for span in spans),
    )
    scores = score_result(
        case, modified, load_corpus(CORPUS_PATH).chunks, config=PipelineConfig()
    )
    assert "context_loss" in cast(list[str], scores["failures"])
    assert scores["context_support_complete"] is False
    assert cast(dict[str, object], scores["reranked"])["recall_at_k"] == 1


@pytest.mark.parametrize("corruption", ["quote", "duplicate", "version"])
def test_invalid_citations_are_counted_as_failures(corruption: str) -> None:
    from labs.week_08.pipeline import AssistantResult

    case, raw = case_result()
    assert isinstance(raw, AssistantResult)
    first = raw.citations[0]
    if corruption == "quote":
        spans = (replace(first, quote="invented"), *raw.citations[1:])
    elif corruption == "version":
        spans = (
            replace(first, chunk=replace(first.chunk, document_version="2")),
            *raw.citations[1:],
        )
    else:
        spans = (*raw.citations, first)
    scores = score_result(
        case,
        replace(raw, citations=spans),
        load_corpus(CORPUS_PATH).chunks,
        config=PipelineConfig(),
    )
    assert scores["invalid_citation_count"] == 1
    assert "invalid_citation" in cast(list[str], scores["failures"])
    assert scores["extractive_traceability"] is False


def test_unavailable_fact_has_valid_citations_but_fails_expected_behavior() -> None:
    from labs.week_08.pipeline import AssistantResult

    case, raw = case_result(22)
    assert isinstance(raw, AssistantResult) and not case.answerable and raw.citations
    scores = score_result(
        case, raw, load_corpus(CORPUS_PATH).chunks, config=PipelineConfig()
    )
    assert scores["citation_valid_fraction"] == 1
    assert scores["response_behavior_matches"] is False
    assert (
        scores["answer_correctness"] is None and scores["answer_faithfulness"] is None
    )
    assert scores["semantic_similarity"] is None
    assert scores["failures"] == ["unanswerable_evidence_returned"]
    assert cast(dict[str, object], scores["reranked"])["recall_at_k"] is None


def test_full_evaluation_is_reproducible_and_persists_raw_case_results(
    tmp_path: Path,
) -> None:
    summary, rows = run_evaluation()
    repeat, repeat_rows = run_evaluation()
    assert summary == repeat and rows == repeat_rows
    assert summary["query_count"] == len(rows) == 30
    assert summary["answerable_count"] == 22 and summary["unanswerable_count"] == 8
    assert summary["failure_counts"] == {"unanswerable_evidence_returned": 3}
    assert summary["unanswerable_abstention_fraction"] == 5 / 8
    assert summary["context_support_complete_fraction"] == 1
    assert summary["answerable_exact_match_fraction"] == 4 / 22
    assert summary["exact_match_fraction"] == 9 / 30
    output = tmp_path / "run"
    save_run(output, summary, rows)
    assert len(read_records(output / "results.jsonl")) == 30
    templates = read_records(output / "review-template.jsonl")
    assert len(templates) == 30 and all(
        item["status"] == "pending" for item in templates
    )
    assert (
        summarize_reviews(output / "review-template.jsonl", rows)["reviewed_count"] == 0
    )
    original = (output / "summary.json").read_bytes()
    with pytest.raises(FileExistsError):
        save_run(output, {}, ())
    assert (output / "summary.json").read_bytes() == original


def test_records_bind_observed_output_to_exact_digest() -> None:
    _, rows = run_evaluation()
    first = dict(rows[0])
    expected = first.pop("record_digest")
    actual = digest_text(
        json.dumps(first, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    )
    assert actual == expected
    first["answer"] = "changed"
    assert (
        digest_text(
            json.dumps(first, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        )
        != expected
    )


def test_changed_dataset_cannot_reuse_a_stale_manifest(tmp_path: Path) -> None:
    for name in ("dataset.json", "cases.jsonl", "source_checks.jsonl"):
        (tmp_path / name).write_bytes((DATASET_DIR / name).read_bytes())
    path = tmp_path / "cases.jsonl"
    path.write_text(path.read_text() + "\n")
    with pytest.raises(EvaluationDataError, match="fingerprint"):
        run_evaluation(dataset_dir=tmp_path)


def test_review_import_keeps_actual_reviewers_separate(tmp_path: Path) -> None:
    _, rows = run_evaluation()
    template = review_template(rows)[0]
    human = {
        **template,
        "status": "reviewed",
        "reviewer_kind": "human",
        "reviewer_id": "test-reviewer",
        "scores": {axis: 4 for axis in AXES},
        "rationale": "Synthetic test input; not a claimed real review.",
    }
    llm = {
        **human,
        "reviewer_kind": "llm",
        "reviewer_id": "fake-test-model",
        "judge_prompt_version": "test-prompt/v1",
    }
    report = summarize_reviews(
        write_jsonl(
            tmp_path / "reviews.jsonl",
            [
                human,
                llm,
                {**llm, "reviewer_id": "org/model", "judge_prompt_version": "v1"},
                {**llm, "reviewer_id": "org", "judge_prompt_version": "model/v1"},
            ],
        ),
        rows,
    )
    assert report["reviewed_count"] == 1 and report["pending_count"] == 29
    groups = cast(dict[str, object], report["groups"])
    assert len(groups) == 4
    assert "human/test-reviewer" in groups
    assert all(
        cast(dict[str, object], group)["rating_count"] == 1 for group in groups.values()
    )


@pytest.mark.parametrize(
    "corruption",
    [
        "stale_run",
        "stale_record",
        "bool_score",
        "out_of_range",
        "missing_rationale",
        "llm_no_prompt",
        "pending_score",
        "duplicate",
    ],
)
def test_untrusted_review_ratings_are_validated(
    corruption: str, tmp_path: Path
) -> None:
    _, rows = run_evaluation()
    item = {
        **review_template(rows)[0],
        "status": "reviewed",
        "reviewer_kind": "human",
        "reviewer_id": "test",
        "scores": {axis: 4 for axis in AXES},
        "rationale": "Test input only.",
    }
    if corruption == "stale_run":
        item["run_id"] = "old"
    elif corruption == "stale_record":
        item["record_digest"] = "old"
    elif corruption == "bool_score":
        cast(dict[str, object], item["scores"])[AXES[0]] = True
    elif corruption == "out_of_range":
        cast(dict[str, object], item["scores"])[AXES[0]] = 6
    elif corruption == "missing_rationale":
        item["rationale"] = ""
    elif corruption == "llm_no_prompt":
        item["reviewer_kind"] = "llm"
    elif corruption == "pending_score":
        item["status"] = "pending"
    records = [item, dict(item)] if corruption == "duplicate" else [item]
    with pytest.raises(EvaluationDataError):
        summarize_reviews(write_jsonl(tmp_path / "bad-review.jsonl", records), rows)


def test_context_ablations_preserve_retrieval_but_expose_downstream_loss() -> None:
    default, _ = run_evaluation()
    compressed, _ = run_evaluation(config=PipelineConfig(compression="sentences"))
    tight, _ = run_evaluation(config=PipelineConfig(context_chars=300))
    assert default["retrieval"] == compressed["retrieval"] == tight["retrieval"]
    assert cast(float, compressed["context_support_complete_fraction"]) < 1
    assert cast(float, tight["context_support_complete_fraction"]) < 1
    assert len({default["run_id"], compressed["run_id"], tight["run_id"]}) == 3
