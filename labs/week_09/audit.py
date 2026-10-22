"""Audit controlled parsing/chunking against separately declared fixture facts."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
import json
from pathlib import Path
from typing import cast

from labs.week_06.chunking import (
    BlockKind,
    ParsedBlock,
    SourceLocation,
    UntrustedDocument,
    canonical_block_text,
)
from labs.week_06.fixtures import PARSER
from labs.week_07.retrieval import SourceChunk, StaticObjectAccessPolicy
from labs.week_08.data import IngestedCorpus
from labs.week_09.dataset import (
    EvaluationCase,
    EvaluationDataError,
    read_records,
    text,
    text_list,
)


@dataclass(frozen=True)
class SourceCheck:
    tenant_id: str
    document_id: str
    version: str
    expected_status: str
    units: tuple[tuple[str, tuple[str, ...]], ...]

    @property
    def identity(self) -> tuple[str, str, str]:
        return self.tenant_id, self.document_id, self.version


def load_source_checks(path: Path) -> tuple[SourceCheck, ...]:
    checks = []
    for item in read_records(path, limit=32, max_bytes=64 * 1024):
        if set(item) != {
            "tenant_id",
            "document_id",
            "version",
            "expected_status",
            "units",
        }:
            raise EvaluationDataError("unexpected source-check fields")
        if item["expected_status"] not in ("accepted", "needs_review", "rejected"):
            raise EvaluationDataError("unknown expected parser status")
        raw_units = item["units"]
        if not isinstance(raw_units, list) or not 1 <= len(raw_units) <= 32:
            raise EvaluationDataError("source checks require bounded evidence units")
        units = []
        for unit in raw_units:
            if not isinstance(unit, dict) or set(unit) != {"location", "atoms"}:
                raise EvaluationDataError("unexpected source unit fields")
            units.append(
                (text(unit["location"], maximum=200), text_list(unit["atoms"]))
            )
        if len({location for location, _ in units}) != len(units):
            raise EvaluationDataError("duplicate source-check location")
        checks.append(
            SourceCheck(
                text(item["tenant_id"], maximum=128),
                text(item["document_id"], maximum=128),
                text(item["version"], maximum=128),
                text(item["expected_status"]),
                tuple(units),
            )
        )
    if len({check.identity for check in checks}) != len(checks):
        raise EvaluationDataError("duplicate source-check identity")
    return tuple(checks)


def source_identity(chunk: SourceChunk) -> tuple[str, str, str]:
    return chunk.tenant_id, chunk.document_id, chunk.document_version


def chunk_key(chunk: SourceChunk) -> str:
    locations = json.loads(dict(chunk.metadata)["source_locations"])
    if (
        not isinstance(locations, list)
        or not locations
        or not isinstance(locations[-1], str)
    ):
        raise EvaluationDataError("chunk has no resolvable body location")
    return "/".join((*source_identity(chunk), locations[-1]))


def validate_case_labels(
    cases: Sequence[EvaluationCase],
    checks: Sequence[SourceCheck],
    access: StaticObjectAccessPolicy,
    records: Sequence[dict[str, object]],
) -> None:
    """Validate labels against input facts, not predicted chunks or answers."""
    by_identity = {check.identity: check for check in checks}
    raw_by_identity = {
        (row["tenant_id"], row["document_id"], row["version"]): row for row in records
    }
    if set(by_identity) != set(raw_by_identity):
        raise EvaluationDataError("source oracle must cover the exact input identities")
    for case in cases:
        for label in case.evidence:
            identity = (label.tenant_id, label.document_id, label.version)
            check = by_identity.get(identity)
            if check is None or check.expected_status != "accepted":
                raise EvaluationDataError(
                    "gold citation must resolve to an expected accepted source"
                )
            if (case.principal_id, *identity) not in access.permitted:
                raise EvaluationDataError(
                    "gold citation is outside the case's access grants"
                )
            record = raw_by_identity[identity]
            if any(
                record.get(predicate.field) != predicate.value
                for predicate in case.filters
            ):
                raise EvaluationDataError("gold citation is outside the case's filters")
            declared = dict(check.units).get(label.location)
            if declared is None or any(atom not in declared for atom in label.atoms):
                raise EvaluationDataError(
                    "gold facts must be declared in the independent source oracle"
                )
        source_atoms = "\n".join(
            atom for label in case.evidence for atom in label.atoms
        ).casefold()
        if any(atom.casefold() not in source_atoms for atom in case.answer_atoms):
            raise EvaluationDataError(
                "answer atom is absent from the declared source oracle"
            )


def audit_sources(
    records: Sequence[dict[str, object]],
    checks: Sequence[SourceCheck],
    ingested: IngestedCorpus,
) -> dict[str, object]:
    """Inspect the parser representation separately from emitted retrieval chunks.

    Records have already passed Week 8's strict bounded loader. These are
    synthetic layout fixtures, not a measure of arbitrary PDF/OCR extraction.
    """
    checks_by_id = {check.identity: check for check in checks}
    rows = []
    parsed_hits = parsed_total = unit_hits = unit_total = status_hits = 0
    for record in records:
        raw_blocks = cast(list[dict[str, object]], record["blocks"])
        blocks = tuple(
            ParsedBlock(
                BlockKind(text(block["kind"])),
                SourceLocation(
                    cast(int, block["page"]),
                    cast(int, block["block_index"]),
                    cast(str | None, block["table_id"]),
                    cast(int | None, block["row_index"]),
                ),
                text(block["text"]),
            )
            for block in raw_blocks
        )
        document = UntrustedDocument(
            text(record["tenant_id"]),
            text(record["document_id"]),
            text(record["version"]),
            text(record["title"]),
            blocks,
        )
        identity = (document.tenant_id, document.document_id, document.version)
        check = checks_by_id[identity]
        raw_by_location = {block.location.label(): block.text for block in blocks}
        # Wrong annotations fail before they can manufacture apparent parser loss.
        for location, atoms in check.units:
            if location not in raw_by_location or any(
                atom not in raw_by_location[location] for atom in atoms
            ):
                raise EvaluationDataError(
                    "source oracle fact is absent from its declared input block"
                )
        parsed = PARSER.parse(document)
        parsed_text = (
            canonical_block_text(parsed.source.blocks)
            if parsed.source is not None
            else ""
        )
        atoms = tuple(atom for _, values in check.units for atom in values)
        hits = sum(atom in parsed_text for atom in atoms)
        parsed_hits += hits
        parsed_total += len(atoms)
        status_match = parsed.status.value == check.expected_status
        status_hits += status_match
        complete = 0
        if check.expected_status == "accepted":
            for location, values in check.units:
                matches = [
                    chunk
                    for chunk in ingested.chunks
                    if source_identity(chunk) == identity
                    and location in json.loads(dict(chunk.metadata)["source_locations"])
                ]
                complete += bool(matches) and all(
                    any(atom in chunk.text for chunk in matches) for atom in values
                )
            unit_total += len(check.units)
            unit_hits += complete
        rows.append(
            {
                "source": "/".join(identity),
                "expected_status": check.expected_status,
                "observed_status": parsed.status.value,
                "status_matches": status_match,
                "parsed_atom_hits": hits,
                "parsed_atom_count": len(atoms),
                "complete_chunk_units": complete,
                "expected_chunk_units": len(check.units)
                if check.expected_status == "accepted"
                else 0,
            }
        )
    return {
        "scope": "controlled layout fixture facts and statuses; no PDF/OCR accuracy claim",
        "source_count": len(rows),
        "status_match_count": status_hits,
        "parsed_atom_recall": parsed_hits / parsed_total if parsed_total else None,
        "complete_chunk_unit_count": unit_hits,
        "expected_chunk_unit_count": unit_total,
        "chunk_unit_recall": unit_hits / unit_total if unit_total else None,
        "sources": rows,
    }
