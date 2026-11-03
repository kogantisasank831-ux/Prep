"""Behavior checks for the Week 16 memory and context-engineering lab."""

from __future__ import annotations

from datetime import datetime, timedelta
import json
from pathlib import Path
import sqlite3
import stat
import subprocess
import sys

from pydantic import ValidationError
import pytest

from labs.week_16.fixtures import CASE_ID, FIXED_NOW, case_memory, scope
from labs.week_16.memory import CaseMemoryStore, initialize, memory_digest
from labs.week_16.models import AccessScope, CaseMemoryInput, MemoryError


ROOT = Path(__file__).resolve().parents[1]


def _store(path: Path) -> CaseMemoryStore:
    return CaseMemoryStore(path, clock=lambda: FIXED_NOW)


def _replace(memory: CaseMemoryInput, **changes: object) -> CaseMemoryInput:
    data = memory.model_dump(mode="python")
    data.update(changes)
    return CaseMemoryInput.model_validate(data)


def _seed(path: Path) -> CaseMemoryStore:
    initialize(path)
    store = _store(path)
    store.remember(scope(write=True), case_memory(), expected_revision=0)
    return store


def test_initialize_is_private_versioned_and_never_overwrites(tmp_path: Path) -> None:
    path = tmp_path / "memory.sqlite3"
    initialize(path)
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT version FROM metadata").fetchone() == (
            "week16/1",
        )
    with pytest.raises(MemoryError, match="store_exists"):
        initialize(path)


def test_semantic_memory_survives_a_new_store_instance(tmp_path: Path) -> None:
    path = tmp_path / "memory.sqlite3"
    store = _seed(path)
    first = store.recall(scope(), CASE_ID)
    restarted = _store(path).recall(scope(), CASE_ID)
    assert first == restarted
    assert restarted is not None
    assert restarted.revision == 1
    assert restarted.selected_supplier_id == "SUP-115"
    assert restarted.calculation.value == "10.00"
    assert restarted.approval_status == "awaiting_approval"
    assert {item.source_type for item in restarted.evidence} == {"document", "sql"}


def test_schema_and_rows_exclude_raw_conversation_and_evidence_bodies(
    tmp_path: Path,
) -> None:
    path = tmp_path / "memory.sqlite3"
    _seed(path)
    with sqlite3.connect(path) as connection:
        semantic_columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(case_semantic_memory)"
            ).fetchall()
        }
        episode_columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(case_episodes)").fetchall()
        }
        rows = connection.execute(
            "SELECT evidence_json,summary FROM case_semantic_memory"
        ).fetchall()
    assert not {"messages", "conversation", "transcript", "raw_evidence"} & (
        semantic_columns | episode_columns
    )
    assert "fictional-contract-1501-v1" not in rows[0][0]
    assert "contract-1501-v1" in rows[0][0]
    assert "raw conversation" not in rows[0][1].casefold()


def test_scope_is_required_for_reads_and_writes(tmp_path: Path) -> None:
    path = tmp_path / "memory.sqlite3"
    store = _seed(path)
    other_tenant = AccessScope(
        tenant_id="tenant-south",
        allowed_case_ids=frozenset({CASE_ID}),
    )
    assert store.recall(other_tenant, CASE_ID) is None
    with pytest.raises(MemoryError, match="not_found"):
        store.recall(
            AccessScope(
                tenant_id="tenant-north",
                allowed_case_ids=frozenset({"another-case"}),
            ),
            CASE_ID,
        )
    with pytest.raises(MemoryError, match="forbidden"):
        store.remember(scope(), case_memory("approved"), expected_revision=1)


def test_exact_duplicate_write_is_idempotent(tmp_path: Path) -> None:
    path = tmp_path / "memory.sqlite3"
    store = _seed(path)
    replay = store.remember(scope(write=True), case_memory(), expected_revision=0)
    assert replay.replayed is True
    assert replay.record.revision == 1
    assert len(store.episodes(scope(), CASE_ID)) == 5


def test_status_update_uses_revision_and_appends_one_episode(tmp_path: Path) -> None:
    path = tmp_path / "memory.sqlite3"
    _seed(path)
    approval_time = FIXED_NOW + timedelta(hours=1)
    later_store = CaseMemoryStore(path, clock=lambda: approval_time)
    updated = later_store.remember(
        scope(write=True), case_memory("approved"), expected_revision=1
    )
    assert updated.replayed is False
    assert updated.record.revision == 2
    assert updated.record.approval_status == "approved"
    assert updated.record.updated_at == approval_time
    events = later_store.episodes(scope(), CASE_ID)
    assert len(events) == 6
    assert events[-1].kind == "approval_status_changed"
    assert events[-1].summary.endswith("to approved.")
    assert events[-1].occurred_at == approval_time


def test_stale_revision_and_changed_investigation_facts_are_rejected(
    tmp_path: Path,
) -> None:
    path = tmp_path / "memory.sqlite3"
    store = _seed(path)
    with pytest.raises(MemoryError, match="revision_conflict"):
        store.remember(scope(write=True), case_memory("approved"), expected_revision=0)
    changed_supplier = _replace(case_memory("approved"), selected_supplier_id="SUP-999")
    with pytest.raises(MemoryError, match="immutable_fact_changed"):
        store.remember(scope(write=True), changed_supplier, expected_revision=1)


def test_terminal_approval_status_cannot_be_rewritten(tmp_path: Path) -> None:
    path = tmp_path / "memory.sqlite3"
    store = _seed(path)
    store.remember(scope(write=True), case_memory("approved"), expected_revision=1)
    with pytest.raises(MemoryError, match="status_transition_invalid"):
        store.remember(scope(write=True), case_memory("rejected"), expected_revision=2)


def test_future_and_already_expired_sources_are_not_saved(tmp_path: Path) -> None:
    path = tmp_path / "memory.sqlite3"
    initialize(path)
    store = _store(path)
    future = _replace(
        case_memory(),
        observed_at=FIXED_NOW + timedelta(minutes=6),
        expires_at=FIXED_NOW + timedelta(days=1),
    )
    with pytest.raises(MemoryError, match="source_in_future"):
        store.remember(scope(write=True), future, expected_revision=0)
    expired = _replace(
        case_memory(),
        observed_at=FIXED_NOW - timedelta(days=2),
        expires_at=FIXED_NOW - timedelta(days=1),
    )
    with pytest.raises(MemoryError, match="memory_expired"):
        store.remember(scope(write=True), expired, expected_revision=0)
    with pytest.raises(MemoryError, match="store_failed"):
        store.recall(scope(), CASE_ID, at=datetime(2026, 11, 3, 5, 0))


def test_context_is_bounded_relevant_and_contains_provenance(tmp_path: Path) -> None:
    path = tmp_path / "memory.sqlite3"
    store = _seed(path)
    selected = store.context(
        scope(),
        CASE_ID,
        "Which supplier and price variance need approval?",
        max_characters=900,
    )
    assert selected.character_count == len(selected.rendered) <= 900
    assert selected.approval_status == "awaiting_approval"
    assert "SUP-115" in selected.semantic_summary
    assert "10.00%" in selected.semantic_summary
    assert "document:contract-1501-v1" in selected.semantic_summary
    assert selected.source_report_digest in selected.rendered
    assert selected.selected_episodes[0].startswith("Objective recorded:")
    assert selected.selected_episodes[1:3] == (
        "Approval status recorded: awaiting_approval.",
        "Supplier selected: SUP-115.",
    )


def test_turn_question_is_transient_and_never_written(tmp_path: Path) -> None:
    path = tmp_path / "memory.sqlite3"
    store = _seed(path)
    marker = "TRANSIENT-QUESTION-7f03d9"
    store.context(scope(), CASE_ID, f"What about {marker}?")
    assert marker.encode("utf-8") not in path.read_bytes()


def test_expiry_hides_context_and_purge_cascades_episodes(tmp_path: Path) -> None:
    path = tmp_path / "memory.sqlite3"
    store = _seed(path)
    after_expiry = FIXED_NOW + timedelta(days=31)
    assert store.recall(scope(), CASE_ID, at=after_expiry) is None
    assert store.episodes(scope(), CASE_ID, at=after_expiry) == ()
    assert store.purge_expired_case(scope(write=True), CASE_ID, at=after_expiry)
    with sqlite3.connect(path) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM case_semantic_memory"
        ).fetchone() == (0,)
        assert connection.execute("SELECT COUNT(*) FROM case_episodes").fetchone() == (
            0,
        )


def test_explicit_forgetting_removes_semantic_and_episodic_memory(
    tmp_path: Path,
) -> None:
    path = tmp_path / "memory.sqlite3"
    store = _seed(path)
    assert store.forget(scope(write=True), CASE_ID) is True
    assert store.forget(scope(write=True), CASE_ID) is False
    assert store.recall(scope(), CASE_ID) is None
    assert store.episodes(scope(), CASE_ID) == ()


def test_strict_schema_rejects_raw_messages_and_invalid_evidence() -> None:
    data = case_memory().model_dump(mode="python")
    data["raw_conversation"] = ["store everything"]
    with pytest.raises(ValidationError):
        CaseMemoryInput.model_validate(data)
    only_document = case_memory().model_dump(mode="python")
    only_document["evidence"] = (case_memory().evidence[0], case_memory().evidence[0])
    with pytest.raises(ValidationError):
        CaseMemoryInput.model_validate(only_document)


def test_memory_digest_is_deterministic_and_changes_with_status() -> None:
    assert memory_digest(case_memory()) == memory_digest(case_memory())
    assert memory_digest(case_memory()) != memory_digest(case_memory("approved"))


def test_cli_smoke_and_cross_process_flow_are_machine_readable(
    tmp_path: Path,
) -> None:
    smoke = subprocess.run(
        [sys.executable, "-m", "labs.week_16.demo", "smoke"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(smoke.stdout) == {"checks": 12, "status": "ok"}

    path = tmp_path / "cli.sqlite3"
    seed = subprocess.run(
        [
            sys.executable,
            "-m",
            "labs.week_16.demo",
            "seed",
            "--db",
            str(path),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(seed.stdout)["revision"] == 1
    recalled = subprocess.run(
        [
            sys.executable,
            "-m",
            "labs.week_16.demo",
            "recall",
            "--db",
            str(path),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(recalled.stdout)["approval_status"] == "awaiting_approval"
    approved = subprocess.run(
        [
            sys.executable,
            "-m",
            "labs.week_16.demo",
            "approve",
            "--db",
            str(path),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(approved.stdout)["revision"] == 2
