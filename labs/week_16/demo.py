"""Command-line demonstrations for Week 16 case memory."""

from __future__ import annotations

import argparse
from datetime import timedelta
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Sequence

from labs.week_16.fixtures import CASE_ID, FIXED_NOW, case_memory, scope
from labs.week_16.memory import CaseMemoryStore, initialize
from labs.week_16.models import ContextSelection, MemoryError, MemoryWriteResult


def _store(path: Path) -> CaseMemoryStore:
    return CaseMemoryStore(path, clock=lambda: FIXED_NOW)


def _write_output(result: MemoryWriteResult) -> dict[str, object]:
    record = result.record
    return {
        "case_id": record.case_id,
        "revision": record.revision,
        "approval_status": record.approval_status,
        "replayed": result.replayed,
        "summary": record.summary,
        "expires_at": record.expires_at.isoformat().replace("+00:00", "Z"),
        "raw_conversation_stored": False,
    }


def _context_output(selection: ContextSelection) -> dict[str, object]:
    return {
        "case_id": selection.case_id,
        "revision": selection.memory_revision,
        "approval_status": selection.approval_status,
        "character_count": selection.character_count,
        "omitted_episode_count": selection.omitted_episode_count,
        "rendered": selection.rendered,
    }


def seed(path: Path) -> dict[str, object]:
    """Create a new store and remember one awaiting-review case."""
    initialize(path)
    result = _store(path).remember(
        scope(write=True),
        case_memory(),
        expected_revision=0,
    )
    return _write_output(result)


def approve(path: Path) -> dict[str, object]:
    """Advance only the approval status using the expected semantic revision."""
    result = _store(path).remember(
        scope(write=True),
        case_memory("approved"),
        expected_revision=1,
    )
    return _write_output(result)


def recall(path: Path, question: str, max_characters: int) -> dict[str, object]:
    """Select a bounded context for a new turn without saving its question."""
    selection = _store(path).context(
        scope(),
        CASE_ID,
        question,
        max_characters=max_characters,
    )
    return _context_output(selection)


def forget(path: Path) -> dict[str, object]:
    """Delete the one synthetic case through its authorized privacy boundary."""
    removed = _store(path).forget(scope(write=True), CASE_ID)
    return {"case_id": CASE_ID, "forgotten": removed}


def smoke() -> None:
    """Exercise persistence, replay, context selection, expiry and forgetting."""
    with TemporaryDirectory(prefix="week16-memory-") as directory:
        path = Path(directory) / "memory.sqlite3"
        seeded = seed(path)
        assert seeded["revision"] == 1
        store = _store(path)
        replay = store.remember(scope(write=True), case_memory(), expected_revision=0)
        assert replay.replayed is True
        before = store.context(
            scope(), CASE_ID, "Which supplier and calculation need approval?"
        )
        assert before.approval_status == "awaiting_approval"
        assert before.character_count <= 1200
        approved = approve(path)
        assert approved["revision"] == 2
        restarted = _store(path).recall(scope(), CASE_ID)
        assert restarted is not None and restarted.approval_status == "approved"
        assert len(_store(path).episodes(scope(), CASE_ID)) == 6
        assert (
            _store(path).recall(scope(), CASE_ID, at=FIXED_NOW + timedelta(days=31))
            is None
        )
        assert _store(path).purge_expired_case(
            scope(write=True), CASE_ID, at=FIXED_NOW + timedelta(days=31)
        )
        assert _store(path).recall(scope(), CASE_ID) is None


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    subcommands = root.add_subparsers(dest="command", required=True)
    seed_parser = subcommands.add_parser("seed", help="create a fresh memory store")
    seed_parser.add_argument("--db", type=Path, default=Path(".runtime/week16.sqlite3"))
    approve_parser = subcommands.add_parser(
        "approve", help="change awaiting memory to approved"
    )
    approve_parser.add_argument(
        "--db", type=Path, default=Path(".runtime/week16.sqlite3")
    )
    recall_parser = subcommands.add_parser(
        "recall", help="assemble bounded context for a new turn"
    )
    recall_parser.add_argument(
        "--db", type=Path, default=Path(".runtime/week16.sqlite3")
    )
    recall_parser.add_argument(
        "--question", default="What do we know about approval and price variance?"
    )
    recall_parser.add_argument("--max-characters", type=int, default=1200)
    forget_parser = subcommands.add_parser(
        "forget", help="remove the synthetic case and its episodes"
    )
    forget_parser.add_argument(
        "--db", type=Path, default=Path(".runtime/week16.sqlite3")
    )
    subcommands.add_parser("smoke")
    return root


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "smoke":
            smoke()
            output: dict[str, object] = {"checks": 12, "status": "ok"}
        elif args.command == "seed":
            output = seed(args.db)
        elif args.command == "approve":
            output = approve(args.db)
        elif args.command == "recall":
            output = recall(args.db, args.question, args.max_characters)
        else:
            output = forget(args.db)
    except (MemoryError, TypeError, ValueError) as error:
        print(json.dumps({"error": str(error)}, sort_keys=True))
        return 2
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
