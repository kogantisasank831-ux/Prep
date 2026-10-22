"""Strict, versioned practice labels independent of the assistant's predictions."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re

from labs.week_07.retrieval import MetadataFilter, RetrievalRequest, validate_request


class EvaluationDataError(ValueError):
    """Evaluation input is malformed, ambiguous or incompatible with the run."""


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise EvaluationDataError("duplicate JSON object key")
        result[key] = value
    return result


def _constant(value: str) -> object:
    raise EvaluationDataError("nonfinite JSON constant: " + value)


def read_records(
    path: Path, *, limit: int = 64, max_bytes: int = 256 * 1024
) -> tuple[dict[str, object], ...]:
    with path.open("rb") as handle:
        raw = handle.read(max_bytes + 1)
    if len(raw) > max_bytes:
        raise EvaluationDataError("evaluation input exceeds byte limit")
    try:
        lines = [line for line in raw.decode("utf-8").splitlines() if line.strip()]
        if not 1 <= len(lines) <= limit:
            raise EvaluationDataError(
                "evaluation input exceeds record bounds or is empty"
            )
        records = []
        for line in lines:
            item = json.loads(
                line, object_pairs_hook=unique_object, parse_constant=_constant
            )
            if not isinstance(item, dict):
                raise EvaluationDataError("each JSONL record must be an object")
            records.append(item)
        return tuple(records)
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise EvaluationDataError("invalid UTF-8 or JSON input") from exc


def text(value: object, *, maximum: int = 1000) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise EvaluationDataError("expected bounded nonblank text")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise EvaluationDataError("text must be valid UTF-8") from exc
    return value


def text_list(value: object, *, allow_empty: bool = False) -> tuple[str, ...]:
    if (
        not isinstance(value, list)
        or len(value) > 16
        or (not value and not allow_empty)
    ):
        raise EvaluationDataError("expected bounded text list")
    result = tuple(text(item) for item in value)
    if len(set(result)) != len(result):
        raise EvaluationDataError("duplicate label text")
    return result


@dataclass(frozen=True)
class ExpectedEvidence:
    tenant_id: str
    document_id: str
    version: str
    location: str
    atoms: tuple[str, ...]

    @property
    def key(self) -> str:
        return "/".join((self.tenant_id, self.document_id, self.version, self.location))


@dataclass(frozen=True)
class EvaluationCase:
    query_id: str
    category: str
    split: str
    principal_id: str
    question: str
    filters: tuple[MetadataFilter, ...]
    answerable: bool
    reference_answers: tuple[str, ...]
    answer_atoms: tuple[str, ...]
    evidence: tuple[ExpectedEvidence, ...]

    def request(self, *, top_k: int) -> RetrievalRequest:
        return RetrievalRequest(self.principal_id, self.question, top_k, self.filters)


def load_cases(path: Path) -> tuple[EvaluationCase, ...]:
    cases = []
    ids: set[str] = set()
    for item in read_records(path):
        if set(item) != {
            "query_id",
            "category",
            "split",
            "principal_id",
            "question",
            "filters",
            "answerable",
            "reference_answers",
            "answer_atoms",
            "evidence",
        }:
            raise EvaluationDataError("unexpected evaluation case fields")
        query_id = text(item["query_id"], maximum=64)
        if re.fullmatch(r"[A-Za-z0-9_-]+", query_id) is None or query_id in ids:
            raise EvaluationDataError("case IDs must be unique safe identifiers")
        ids.add(query_id)
        if item["split"] != "practice" or type(item["answerable"]) is not bool:
            raise EvaluationDataError(
                "this visible fixture must be labelled practice with boolean answerability"
            )
        raw_filters = item["filters"]
        if not isinstance(raw_filters, dict):
            raise EvaluationDataError("filters must be an object")
        filters = tuple(
            MetadataFilter(text(key), text(value, maximum=200))
            for key, value in sorted(raw_filters.items())
        )
        raw_evidence = item["evidence"]
        if not isinstance(raw_evidence, list) or len(raw_evidence) > 16:
            raise EvaluationDataError("evidence must be a bounded list")
        evidence = []
        for label in raw_evidence:
            if not isinstance(label, dict) or set(label) != {
                "tenant_id",
                "document_id",
                "version",
                "location",
                "atoms",
            }:
                raise EvaluationDataError("unexpected expected-citation fields")
            evidence.append(
                ExpectedEvidence(
                    text(label["tenant_id"], maximum=128),
                    text(label["document_id"], maximum=128),
                    text(label["version"], maximum=128),
                    text(label["location"], maximum=200),
                    text_list(label["atoms"]),
                )
            )
        if len({label.key for label in evidence}) != len(evidence):
            raise EvaluationDataError("duplicate expected evidence")
        atoms = text_list(item["answer_atoms"], allow_empty=True)
        answerable = item["answerable"]
        if answerable != bool(evidence) or answerable != bool(atoms):
            raise EvaluationDataError(
                "answerable cases require evidence and answer atoms; unanswerable cases require neither"
            )
        case = EvaluationCase(
            query_id,
            text(item["category"], maximum=64),
            "practice",
            text(item["principal_id"], maximum=128),
            text(item["question"]),
            filters,
            answerable,
            text_list(item["reference_answers"]),
            atoms,
            tuple(evidence),
        )
        validate_request(case.request(top_k=3))
        cases.append(case)
    return tuple(cases)
