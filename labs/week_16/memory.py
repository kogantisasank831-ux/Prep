"""Tenant-scoped SQLite semantic and episodic memory for Week 16."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import closing, contextmanager
from datetime import date, datetime, timedelta, timezone
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from typing import cast

from labs.week_16.context import (
    build_semantic_summary,
    initial_episode_specs,
    select_context,
)
from labs.week_16.models import (
    AccessScope,
    ApprovalStatus,
    Calculation,
    CaseMemoryInput,
    CaseMemoryRecord,
    ContextSelection,
    EpisodeKind,
    EpisodeRecord,
    EvidenceReference,
    MemoryError,
    MemoryWriteResult,
)


SCHEMA_VERSION = "week16/1"
SCHEMA = """
CREATE TABLE metadata(version TEXT NOT NULL);
CREATE TABLE case_semantic_memory(
  tenant_id TEXT NOT NULL,
  case_id TEXT NOT NULL,
  revision INTEGER NOT NULL CHECK(revision >= 1),
  objective TEXT NOT NULL,
  selected_supplier_id TEXT NOT NULL,
  evidence_json TEXT NOT NULL,
  calculation_json TEXT NOT NULL,
  approval_status TEXT NOT NULL
    CHECK(approval_status IN ('awaiting_approval','approved','rejected')),
  source_run_id TEXT NOT NULL,
  source_report_digest TEXT NOT NULL,
  observed_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  memory_digest TEXT NOT NULL,
  summary TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  PRIMARY KEY(tenant_id, case_id)
);
CREATE TABLE case_episodes(
  tenant_id TEXT NOT NULL,
  case_id TEXT NOT NULL,
  sequence INTEGER NOT NULL CHECK(sequence >= 1),
  kind TEXT NOT NULL,
  summary TEXT NOT NULL,
  occurred_at TEXT NOT NULL,
  source_run_id TEXT NOT NULL,
  memory_digest TEXT NOT NULL,
  PRIMARY KEY(tenant_id, case_id, sequence),
  FOREIGN KEY(tenant_id, case_id)
    REFERENCES case_semantic_memory(tenant_id, case_id) ON DELETE CASCADE
);
"""


def _iso(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise MemoryError("store_failed")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_datetime(value: object) -> datetime:
    if not isinstance(value, str):
        raise MemoryError("schema_invalid")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise MemoryError("schema_invalid") from error
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise MemoryError("schema_invalid")
    return parsed.astimezone(timezone.utc)


def _at_or_now(value: datetime | None, now: Callable[[], datetime]) -> datetime:
    if value is None:
        return now()
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise MemoryError("store_failed")
    return value.astimezone(timezone.utc)


def _json(value: object) -> str:
    try:
        return json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as error:
        raise MemoryError("store_failed") from error


def _json_object(value: object) -> dict[str, object]:
    if not isinstance(value, str):
        raise MemoryError("schema_invalid")
    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, UnicodeError) as error:
        raise MemoryError("schema_invalid") from error
    if not isinstance(parsed, dict):
        raise MemoryError("schema_invalid")
    return cast(dict[str, object], parsed)


def _json_list(value: object) -> list[object]:
    if not isinstance(value, str):
        raise MemoryError("schema_invalid")
    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, UnicodeError) as error:
        raise MemoryError("schema_invalid") from error
    if not isinstance(parsed, list):
        raise MemoryError("schema_invalid")
    return cast(list[object], parsed)


def memory_digest(memory: CaseMemoryInput) -> str:
    """Digest the complete selected memory snapshot, including its status."""
    payload = _json(memory.model_dump(mode="json"))
    return sha256(payload.encode("utf-8")).hexdigest()


def initialize(path: Path) -> None:
    """Create a new private memory store without replacing an existing file."""
    resolved = path.resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    try:
        with resolved.open("xb"):
            pass
    except FileExistsError as error:
        raise MemoryError("store_exists") from error
    except OSError as error:
        raise MemoryError("store_failed") from error
    resolved.chmod(0o600)
    try:
        with closing(sqlite3.connect(resolved, isolation_level=None)) as connection:
            connection.execute("PRAGMA foreign_keys=ON")
            connection.executescript("BEGIN IMMEDIATE;\n" + SCHEMA)
            connection.execute("INSERT INTO metadata VALUES (?)", (SCHEMA_VERSION,))
            connection.commit()
    except sqlite3.Error as error:
        raise MemoryError("store_failed") from error


class CaseMemoryStore:
    """Own durable, scoped case memory with explicit lifecycle controls."""

    def __init__(
        self,
        path: Path,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.path = path.resolve()
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def _now(self) -> datetime:
        value = self.clock()
        if not isinstance(value, datetime) or value.tzinfo is None:
            raise MemoryError("store_failed")
        return value.astimezone(timezone.utc)

    @contextmanager
    def _connect(self, *, write: bool = False) -> Iterator[sqlite3.Connection]:
        if not self.path.is_file():
            raise MemoryError("store_missing")
        connection: sqlite3.Connection | None = None
        try:
            connection = sqlite3.connect(
                self.path.as_uri() + ("?mode=rw" if write else "?mode=ro"),
                uri=True,
                isolation_level=None,
                timeout=0.25,
            )
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("PRAGMA trusted_schema=OFF")
            if not write:
                connection.execute("PRAGMA query_only=ON")
            metadata = connection.execute("SELECT version FROM metadata").fetchall()
            if len(metadata) != 1 or metadata[0]["version"] != SCHEMA_VERSION:
                raise MemoryError("schema_invalid")
            yield connection
        except MemoryError:
            raise
        except sqlite3.Error as error:
            raise MemoryError("store_failed") from error
        finally:
            if connection is not None:
                if connection.in_transaction:
                    connection.rollback()
                connection.close()

    @staticmethod
    def _evidence(value: object) -> tuple[EvidenceReference, ...]:
        items: list[EvidenceReference] = []
        for raw in _json_list(value):
            if not isinstance(raw, dict):
                raise MemoryError("schema_invalid")
            data = dict(raw)
            data["observed_at"] = _parse_datetime(data.get("observed_at"))
            try:
                items.append(EvidenceReference.model_validate(data))
            except ValueError as error:
                raise MemoryError("schema_invalid") from error
        return tuple(items)

    @staticmethod
    def _calculation(value: object) -> Calculation:
        data = _json_object(value)
        raw_date = data.get("reference_as_of")
        if not isinstance(raw_date, str):
            raise MemoryError("schema_invalid")
        try:
            data["reference_as_of"] = date.fromisoformat(raw_date)
            return Calculation.model_validate(data)
        except ValueError as error:
            raise MemoryError("schema_invalid") from error

    @classmethod
    def _record(cls, row: sqlite3.Row) -> CaseMemoryRecord:
        try:
            return CaseMemoryRecord(
                case_id=row["case_id"],
                objective=row["objective"],
                selected_supplier_id=row["selected_supplier_id"],
                evidence=cls._evidence(row["evidence_json"]),
                calculation=cls._calculation(row["calculation_json"]),
                approval_status=row["approval_status"],
                source_run_id=row["source_run_id"],
                source_report_digest=row["source_report_digest"],
                observed_at=_parse_datetime(row["observed_at"]),
                expires_at=_parse_datetime(row["expires_at"]),
                revision=row["revision"],
                memory_digest=row["memory_digest"],
                summary=row["summary"],
                created_at=_parse_datetime(row["created_at"]),
                updated_at=_parse_datetime(row["updated_at"]),
            )
        except (KeyError, TypeError, ValueError) as error:
            raise MemoryError("schema_invalid") from error

    @staticmethod
    def _episode(row: sqlite3.Row) -> EpisodeRecord:
        try:
            return EpisodeRecord(
                sequence=row["sequence"],
                kind=row["kind"],
                summary=row["summary"],
                occurred_at=_parse_datetime(row["occurred_at"]),
                source_run_id=row["source_run_id"],
                memory_digest=row["memory_digest"],
            )
        except (KeyError, TypeError, ValueError) as error:
            raise MemoryError("schema_invalid") from error

    @staticmethod
    def _immutable_fields(memory: CaseMemoryInput | CaseMemoryRecord) -> object:
        excluded = {
            "approval_status",
            "revision",
            "memory_digest",
            "summary",
            "created_at",
            "updated_at",
        }
        return memory.model_dump(mode="json", exclude=excluded)

    @staticmethod
    def _valid_transition(before: ApprovalStatus, after: ApprovalStatus) -> bool:
        return before == "awaiting_approval" and after in {"approved", "rejected"}

    @staticmethod
    def _insert_episode(
        connection: sqlite3.Connection,
        scope: AccessScope,
        memory: CaseMemoryInput,
        *,
        sequence: int,
        kind: EpisodeKind,
        summary: str,
        digest: str,
        occurred_at: datetime,
    ) -> None:
        connection.execute(
            """
            INSERT INTO case_episodes(
              tenant_id,case_id,sequence,kind,summary,occurred_at,
              source_run_id,memory_digest
            ) VALUES (?,?,?,?,?,?,?,?)
            """,
            (
                scope.tenant_id,
                memory.case_id,
                sequence,
                kind,
                summary,
                _iso(occurred_at),
                memory.source_run_id,
                digest,
            ),
        )

    def remember(
        self,
        scope: AccessScope,
        memory: CaseMemoryInput,
        *,
        expected_revision: int,
    ) -> MemoryWriteResult:
        """Create or update one semantic snapshot using compare-and-set."""
        scope.require(memory.case_id, write=True)
        if (
            type(expected_revision) is not int
            or isinstance(expected_revision, bool)
            or expected_revision < 0
        ):
            raise MemoryError("revision_conflict")
        now = self._now()
        if memory.observed_at > now + timedelta(minutes=5):
            raise MemoryError("source_in_future")
        if memory.expires_at <= now:
            raise MemoryError("memory_expired")
        digest = memory_digest(memory)
        summary = build_semantic_summary(memory)
        with self._connect(write=True) as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                """
                SELECT * FROM case_semantic_memory
                WHERE tenant_id=? AND case_id=?
                """,
                (scope.tenant_id, memory.case_id),
            ).fetchone()
            if row is None:
                if expected_revision != 0:
                    raise MemoryError("revision_conflict")
                created = _iso(now)
                connection.execute(
                    """
                    INSERT INTO case_semantic_memory(
                      tenant_id,case_id,revision,objective,selected_supplier_id,
                      evidence_json,calculation_json,approval_status,source_run_id,
                      source_report_digest,observed_at,expires_at,memory_digest,
                      summary,created_at,updated_at
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        scope.tenant_id,
                        memory.case_id,
                        1,
                        memory.objective,
                        memory.selected_supplier_id,
                        _json(
                            [item.model_dump(mode="json") for item in memory.evidence]
                        ),
                        _json(memory.calculation.model_dump(mode="json")),
                        memory.approval_status,
                        memory.source_run_id,
                        memory.source_report_digest,
                        _iso(memory.observed_at),
                        _iso(memory.expires_at),
                        digest,
                        summary,
                        created,
                        created,
                    ),
                )
                for sequence, (kind, episode_summary) in enumerate(
                    initial_episode_specs(memory), start=1
                ):
                    self._insert_episode(
                        connection,
                        scope,
                        memory,
                        sequence=sequence,
                        kind=cast(EpisodeKind, kind),
                        summary=episode_summary,
                        digest=digest,
                        occurred_at=memory.observed_at,
                    )
                saved = connection.execute(
                    "SELECT * FROM case_semantic_memory WHERE tenant_id=? AND case_id=?",
                    (scope.tenant_id, memory.case_id),
                ).fetchone()
                connection.commit()
                assert saved is not None
                return MemoryWriteResult(record=self._record(saved), replayed=False)

            current = self._record(row)
            if current.memory_digest == digest:
                connection.commit()
                return MemoryWriteResult(record=current, replayed=True)
            if expected_revision != current.revision:
                raise MemoryError("revision_conflict")
            if self._immutable_fields(current) != self._immutable_fields(memory):
                raise MemoryError("immutable_fact_changed")
            if not self._valid_transition(
                current.approval_status, memory.approval_status
            ):
                raise MemoryError("status_transition_invalid")
            next_revision = current.revision + 1
            updated = connection.execute(
                """
                UPDATE case_semantic_memory
                SET revision=?,approval_status=?,memory_digest=?,summary=?,updated_at=?
                WHERE tenant_id=? AND case_id=? AND revision=?
                """,
                (
                    next_revision,
                    memory.approval_status,
                    digest,
                    summary,
                    _iso(now),
                    scope.tenant_id,
                    memory.case_id,
                    current.revision,
                ),
            )
            if updated.rowcount != 1:
                raise MemoryError("revision_conflict")
            sequence_row = connection.execute(
                """
                SELECT COALESCE(MAX(sequence),0)+1 AS next_sequence
                FROM case_episodes WHERE tenant_id=? AND case_id=?
                """,
                (scope.tenant_id, memory.case_id),
            ).fetchone()
            assert sequence_row is not None
            self._insert_episode(
                connection,
                scope,
                memory,
                sequence=int(sequence_row["next_sequence"]),
                kind="approval_status_changed",
                summary=(
                    f"Approval status changed from {current.approval_status} "
                    f"to {memory.approval_status}."
                ),
                digest=digest,
                occurred_at=now,
            )
            saved = connection.execute(
                "SELECT * FROM case_semantic_memory WHERE tenant_id=? AND case_id=?",
                (scope.tenant_id, memory.case_id),
            ).fetchone()
            connection.commit()
            assert saved is not None
            return MemoryWriteResult(record=self._record(saved), replayed=False)

    def recall(
        self,
        scope: AccessScope,
        case_id: str,
        *,
        at: datetime | None = None,
    ) -> CaseMemoryRecord | None:
        """Return current semantic memory only while it is in retention."""
        scope.require(case_id)
        now = _at_or_now(at, self._now)
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM case_semantic_memory WHERE tenant_id=? AND case_id=?",
                (scope.tenant_id, case_id),
            ).fetchone()
        if row is None:
            return None
        record = self._record(row)
        return record if record.expires_at > now else None

    def episodes(
        self,
        scope: AccessScope,
        case_id: str,
        *,
        at: datetime | None = None,
    ) -> tuple[EpisodeRecord, ...]:
        """Return compact events for a retained, authorized case."""
        if self.recall(scope, case_id, at=at) is None:
            return ()
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM case_episodes
                WHERE tenant_id=? AND case_id=? ORDER BY sequence
                """,
                (scope.tenant_id, case_id),
            ).fetchall()
        return tuple(self._episode(row) for row in rows)

    def context(
        self,
        scope: AccessScope,
        case_id: str,
        question: str,
        *,
        max_characters: int = 1200,
    ) -> ContextSelection:
        """Assemble bounded context on demand without persisting the question."""
        record = self.recall(scope, case_id)
        if record is None:
            raise MemoryError("not_found")
        events = self.episodes(scope, case_id)
        return select_context(
            record,
            events,
            question,
            max_characters=max_characters,
        )

    def purge_expired_case(
        self,
        scope: AccessScope,
        case_id: str,
        *,
        at: datetime | None = None,
    ) -> bool:
        """Delete one authorized case only when its retention deadline passed."""
        scope.require(case_id, write=True)
        now = _at_or_now(at, self._now)
        with self._connect(write=True) as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                """
                SELECT expires_at FROM case_semantic_memory
                WHERE tenant_id=? AND case_id=?
                """,
                (scope.tenant_id, case_id),
            ).fetchone()
            if row is None or _parse_datetime(row["expires_at"]) > now:
                connection.commit()
                return False
            deleted = connection.execute(
                "DELETE FROM case_semantic_memory WHERE tenant_id=? AND case_id=?",
                (scope.tenant_id, case_id),
            ).rowcount
            connection.commit()
            return deleted == 1

    def forget(self, scope: AccessScope, case_id: str) -> bool:
        """Explicitly remove one authorized case and its cascaded episodes."""
        scope.require(case_id, write=True)
        with self._connect(write=True) as connection:
            connection.execute("BEGIN IMMEDIATE")
            deleted = connection.execute(
                "DELETE FROM case_semantic_memory WHERE tenant_id=? AND case_id=?",
                (scope.tenant_id, case_id),
            ).rowcount
            connection.commit()
            return deleted == 1
