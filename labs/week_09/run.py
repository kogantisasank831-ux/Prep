"""Run and persist a versioned, stage-by-stage procurement evaluation."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Sequence
from dataclasses import asdict
import json
from pathlib import Path
import platform
import re
from statistics import mean

from labs.week_05.metrics import evaluate_ranking
from labs.week_07.retrieval import AuthorizedCorpus, SourceChunk, digest_text
from labs.week_08.data import demo_access, load_corpus
from labs.week_08.pipeline import (
    AssistantResult,
    KnowledgeAssistant,
    PipelineConfig,
    PipelineError,
    validate_citations,
)
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
    unique_object,
)
from labs.week_09.metrics import NORMALIZATION, atom_coverage, exact_match
from labs.week_09.reviews import review_template, summarize_reviews

DATASET_DIR = Path(__file__).parent
CORPUS_PATH = DATASET_DIR.parent / "week_08" / "corpus.jsonl"


def _digest(value: object) -> str:
    return digest_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    )


def _mean(values: Sequence[object]) -> float | None:
    numbers = [value for value in values if isinstance(value, (int, float))]
    return mean(numbers) if numbers else None


def _manifest(directory: Path) -> dict[str, object]:
    path = directory / "dataset.json"
    with path.open("rb") as handle:
        raw_manifest = handle.read(16 * 1024 + 1)
    if len(raw_manifest) > 16 * 1024:
        raise EvaluationDataError("dataset manifest exceeds 16 KiB")
    try:
        item = json.loads(raw_manifest.decode("utf-8"), object_pairs_hook=unique_object)
    except (json.JSONDecodeError, UnicodeDecodeError, RecursionError) as exc:
        raise EvaluationDataError("malformed dataset manifest") from exc
    if not isinstance(item, dict) or set(item) != {
        "schema",
        "dataset_id",
        "version",
        "split",
        "corpus_digest",
        "cases_digest",
        "source_checks_digest",
    }:
        raise EvaluationDataError("unexpected dataset manifest fields")
    if (
        item["schema"] != "procurement-evaluation-dataset/1.0.0"
        or item["split"] != "practice"
        or item["dataset_id"] != "week09-procurement"
        or not isinstance(item["version"], str)
        or re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", item["version"]) is None
    ):
        raise EvaluationDataError("unsupported dataset identity")
    for field, source in (
        ("corpus_digest", CORPUS_PATH),
        ("cases_digest", directory / "cases.jsonl"),
        ("source_checks_digest", directory / "source_checks.jsonl"),
    ):
        maximum = 64 * 1024 if field == "source_checks_digest" else 256 * 1024
        with source.open("rb") as handle:
            raw_source = handle.read(maximum + 1)
        if len(raw_source) > maximum:
            raise EvaluationDataError("dataset/input exceeds byte limit: " + field)
        try:
            source_digest = digest_text(raw_source.decode("utf-8"))
        except UnicodeDecodeError as exc:
            raise EvaluationDataError("dataset/input must be UTF-8: " + field) from exc
        if item[field] != source_digest:
            raise EvaluationDataError("dataset/input fingerprint mismatch: " + field)
    return item


def score_result(
    case: EvaluationCase,
    result: AssistantResult,
    eligible: Sequence[SourceChunk],
    *,
    config: PipelineConfig,
) -> dict[str, object]:
    """Score labelled source units, exact spans and explicit lexical proxies."""
    gold = frozenset(label.key for label in case.evidence)
    candidate_keys = [chunk_key(item.chunk) for item in result.candidates]
    hybrid_keys = candidate_keys[: config.evidence_count]
    reranked_keys = [
        chunk_key(item.chunk) for item in result.reranked[: config.evidence_count]
    ]
    candidates = asdict(
        evaluate_ranking(candidate_keys, gold, k=config.candidate_count)
    )
    hybrid = asdict(evaluate_ranking(hybrid_keys, gold, k=config.evidence_count))
    reranked = asdict(evaluate_ranking(reranked_keys, gold, k=config.evidence_count))
    valid_spans = []
    seen: set[str] = set()
    access = demo_access()
    for span in result.citations:
        try:
            if span.citation_id in seen:
                raise PipelineError("duplicate citation label")
            validate_citations((span,), eligible, case.principal_id, access)
            valid_spans.append(span)
        except PipelineError:
            pass  # This is an evaluated failure counted below, never a hidden pass.
        seen.add(span.citation_id)
    by_key: dict[str, str] = {}
    for span in valid_spans:
        key = chunk_key(span.chunk)
        by_key[key] = by_key.get(key, "") + "\n" + span.quote
    selected_keys = list(by_key)
    evidence_hits = sum(key in gold for key in selected_keys)
    context_precision = (
        evidence_hits / len(selected_keys)
        if case.answerable and selected_keys
        else (0.0 if case.answerable else None)
    )
    context_recall = evidence_hits / len(gold) if gold else None
    complete = (
        all(
            label.key in by_key and atom_coverage(by_key[label.key], label.atoms) == 1
            for label in case.evidence
        )
        if gold
        else None
    )
    coverage = atom_coverage(result.answer, case.answer_atoms)
    exact = exact_match(result.answer, case.reference_answers)
    invalid = len(result.citations) - len(valid_spans)
    traceable = (
        result.answer
        == "\n".join(f"{span.quote} [{span.citation_id}]" for span in result.citations)
        and invalid == 0
        if result.citations
        else None
    )
    failures = []
    if case.answerable:
        if candidates["recall_at_k"] != 1:
            failures.append("candidate_miss")
        if candidates["recall_at_k"] == 1 and reranked["recall_at_k"] != 1:
            failures.append("ranking_loss")
        if reranked["recall_at_k"] == 1 and not complete:
            failures.append("context_loss")
        if complete and coverage != 1:
            failures.append("answer_atom_loss")
        if not result.citations:
            failures.append("unexpected_abstention")
    elif result.citations:
        failures.append("unanswerable_evidence_returned")
    if invalid:
        failures.append("invalid_citation")
    if traceable is False:
        failures.append("extractive_format_mismatch")
    return {
        "candidate": candidates,
        "hybrid": hybrid,
        "reranked": reranked,
        "context_source_precision": context_precision,
        "expected_citation_recall": context_recall,
        "context_support_complete": complete,
        "answer_atom_coverage": coverage,
        "exact_match": exact,
        "citation_count": len(result.citations),
        "invalid_citation_count": invalid,
        "citation_valid_fraction": len(valid_spans) / len(result.citations)
        if result.citations
        else None,
        "extractive_traceability": traceable,
        "response_behavior_matches": bool(result.citations) == case.answerable,
        "semantic_similarity": None,
        "answer_faithfulness": None,
        "answer_correctness": None,
        "citation_semantic_support": None,
        "review_status": "not_reviewed",
        "failures": failures,
        "diagnostics": []
        if exact
        else ["exact_match_mismatch_is_not_a_semantic_verdict"],
        "candidate_keys": candidate_keys,
        "hybrid_keys": hybrid_keys,
        "reranked_keys": reranked_keys,
        "context_keys": selected_keys,
    }


def run_evaluation(
    *,
    dataset_dir: Path = DATASET_DIR,
    config: PipelineConfig | None = None,
    review_file: Path | None = None,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    config = config or PipelineConfig()
    manifest = _manifest(dataset_dir)
    cases = load_cases(dataset_dir / "cases.jsonl")
    checks = load_source_checks(dataset_dir / "source_checks.jsonl")
    ingested = load_corpus(CORPUS_PATH)
    input_records = read_records(CORPUS_PATH, limit=32, max_bytes=128 * 1024)
    access = demo_access()
    validate_case_labels(cases, checks, access, input_records)
    source_audit = audit_sources(input_records, checks, ingested)
    assistant = KnowledgeAssistant(ingested.chunks, access, config=config)
    implementation = {
        f"week_{week:02d}/{path.name}": digest_text(path.read_text(encoding="utf-8"))
        for week in range(5, 10)
        for path in sorted((DATASET_DIR.parent / f"week_{week:02d}").glob("*.py"))
    }
    system = {
        "config": asdict(config),
        "dense": asdict(assistant.dense.config),
        "reranker": asdict(assistant.scorer.identity),
        "python": platform.python_version(),
        "implementation_digest": _digest(implementation),
    }
    run_id = _digest(
        {"dataset": manifest, "system": system, "normalization": NORMALIZATION}
    )
    rows: list[dict[str, object]] = []
    for case in cases:
        request = case.request(top_k=config.evidence_count)
        eligible = AuthorizedCorpus.build(request, ingested.chunks, access).chunks
        result = assistant.ask(request, request_id=case.query_id)
        metrics = score_result(case, result, eligible, config=config)
        row: dict[str, object] = {
            "query_id": case.query_id,
            "run_id": run_id,
            "category": case.category,
            "answerable": case.answerable,
            "question": case.question,
            "principal_id": case.principal_id,
            "filters": [asdict(predicate) for predicate in case.filters],
            "reference_answers": case.reference_answers,
            "expected_evidence": [asdict(label) for label in case.evidence],
            "status": result.status,
            "answer_mode": result.answer_mode,
            "answer": result.answer,
            "context_chars": len(result.context),
            "context_digest": digest_text(result.context),
            "citations": [
                {
                    "id": span.citation_id,
                    "chunk_id": span.chunk.chunk_id,
                    "source_key": chunk_key(span.chunk),
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
            "eligible_count": result.eligible_count,
            "request_manifest": result.manifest_fingerprint,
            "metrics": metrics,
        }
        row["record_digest"] = _digest(row)
        rows.append(row)
    labelled = [row for row in rows if row["answerable"]]
    unanswerable = [row for row in rows if not row["answerable"]]

    def metrics_of(group: Sequence[dict[str, object]]) -> list[dict[str, object]]:
        values = [row["metrics"] for row in group]
        if not all(isinstance(value, dict) for value in values):
            raise EvaluationDataError("internal metric record is invalid")
        return [value for value in values if isinstance(value, dict)]

    labelled_metrics = metrics_of(labelled)
    all_metrics = metrics_of(rows)
    retrieval: dict[str, object] = {}
    for mode in ("candidate", "hybrid", "reranked"):
        metric_rows = [item[mode] for item in labelled_metrics]
        retrieval[mode] = {
            key: _mean([item[key] for item in metric_rows if isinstance(item, dict)])
            for key in (
                "precision_at_k",
                "recall_at_k",
                "reciprocal_rank_at_k",
                "ndcg_at_k",
            )
        }
    failures = Counter(
        failure
        for item in all_metrics
        if isinstance(failures_for_case := item["failures"], list)
        for failure in failures_for_case
    )
    summary = {
        "schema": "week09-stage-evaluation/1.0.0",
        "run_id": run_id,
        "scope": "visible synthetic practice questions; deterministic proxies, not learned-model or semantic correctness certification",
        "dataset": manifest,
        "system": system,
        "normalization": NORMALIZATION,
        "query_count": len(rows),
        "answerable_count": len(labelled),
        "unanswerable_count": len(unanswerable),
        "source_audit": source_audit,
        "retrieval": retrieval,
        "context_support_complete_fraction": _mean(
            [item["context_support_complete"] for item in labelled_metrics]
        ),
        "context_source_precision": _mean(
            [item["context_source_precision"] for item in labelled_metrics]
        ),
        "expected_citation_recall": _mean(
            [item["expected_citation_recall"] for item in labelled_metrics]
        ),
        "answer_atom_coverage": _mean(
            [item["answer_atom_coverage"] for item in labelled_metrics]
        ),
        "exact_match_fraction": _mean([item["exact_match"] for item in all_metrics]),
        "answerable_exact_match_fraction": _mean(
            [item["exact_match"] for item in labelled_metrics]
        ),
        "unanswerable_abstention_fraction": _mean(
            [item["response_behavior_matches"] for item in metrics_of(unanswerable)]
        ),
        "invalid_citation_count": sum(
            int(item["invalid_citation_count"])
            for item in all_metrics
            if isinstance(item["invalid_citation_count"], int)
        ),
        "extractive_traceability_fraction": _mean(
            [item["extractive_traceability"] for item in all_metrics]
        ),
        "failure_counts": dict(sorted(failures.items())),
        "categories": {
            category: {
                "case_count": len(group),
                "behavior_matches": _mean(
                    [item["response_behavior_matches"] for item in metrics_of(group)]
                ),
                "context_support_complete": _mean(
                    [item["context_support_complete"] for item in metrics_of(group)]
                ),
            }
            for category in sorted({case.category for case in cases})
            if (group := [row for row in rows if row["category"] == category])
        },
        "reviews": summarize_reviews(review_file, rows),
        "unmeasured": [
            "semantic similarity",
            "claim entailment/faithfulness",
            "semantic answer correctness",
            "semantic citation support",
            "real model quality",
            "latency",
            "memory",
            "general PDF/OCR accuracy",
        ],
    }
    return summary, rows


def save_run(
    output_dir: Path, summary: dict[str, object], rows: Sequence[dict[str, object]]
) -> None:
    """Create a fresh local result directory; refuse to overwrite prior evidence."""
    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "results.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
    (output_dir / "review-template.jsonl").write_text(
        "".join(
            json.dumps(row, ensure_ascii=False) + "\n" for row in review_template(rows)
        ),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-dir", type=Path, default=DATASET_DIR)
    parser.add_argument(
        "--output-dir", type=Path, default=Path(".runtime/week09-default")
    )
    parser.add_argument("--context-chars", type=int, default=1400)
    parser.add_argument("--compression", choices=("none", "sentences"), default="none")
    parser.add_argument("--reviews", type=Path)
    args = parser.parse_args()
    summary, rows = run_evaluation(
        dataset_dir=args.dataset_dir,
        config=PipelineConfig(
            context_chars=args.context_chars, compression=args.compression
        ),
        review_file=args.reviews,
    )
    try:
        save_run(args.output_dir, summary, rows)
    except FileExistsError:
        parser.error(
            "output directory already exists; use a fresh --output-dir to preserve prior results"
        )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
