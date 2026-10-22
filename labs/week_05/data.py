"""Bounded JSONL loading for the synthetic Week 5 corpus."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from labs.week_05.retrieval import (
    DocumentRejectedError,
    SourceDocument,
    UntrustedDocument,
    load_documents,
)

CORPUS_LIMIT = 64 * 1024
FIELDS = {"tenant_id", "document_id", "document_version", "title", "text"}


def _unique(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise DocumentRejectedError("corpus record contains repeated keys")
        result[key] = value
    return result


def load_corpus(path: Path) -> tuple[SourceDocument, ...]:
    """Load a local lab dataset; a web-upload parser is outside this interface."""
    with path.open("rb") as handle:
        raw = handle.read(CORPUS_LIMIT + 1)
    if len(raw) > CORPUS_LIMIT:
        raise DocumentRejectedError("corpus exceeds lab byte budget")
    try:
        text = raw.decode("utf-8", errors="strict")
        records: list[UntrustedDocument] = []
        for line in text.splitlines():
            if not line.strip():
                continue
            value: object = json.loads(line, object_pairs_hook=_unique)
            if not isinstance(value, dict) or set(value) != FIELDS:
                raise DocumentRejectedError("corpus record has the wrong fields")
            if not all(isinstance(item, str) for item in value.values()):
                raise DocumentRejectedError("corpus record fields must be strings")
            # The JSON boundary has now checked every key and value.
            fields = cast(dict[str, str], value)
            records.append(UntrustedDocument(**fields))
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise DocumentRejectedError("corpus must be valid UTF-8 JSONL") from exc
    if not records:
        raise DocumentRejectedError("corpus must contain documents")
    return load_documents(records)


def sample_documents() -> tuple[SourceDocument, ...]:
    return load_corpus(Path(__file__).with_name("corpus.jsonl"))
