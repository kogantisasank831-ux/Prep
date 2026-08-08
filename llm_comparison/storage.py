from __future__ import annotations

import json
import os
from pathlib import Path
from typing import BinaryIO

import msvcrt
from pydantic import ValidationError

from llm_comparison.models import ENVELOPE_ADAPTER, Envelope


class StorageError(Exception):
    """Base storage failure."""


class RecordConflictError(StorageError):
    """A record ID already exists with different content."""


class DuplicateRecordError(StorageError):
    """A file contains the same record ID more than once."""


class CorruptJsonlError(StorageError):
    def __init__(self, byte_offset: int, detail: str) -> None:
        self.byte_offset = byte_offset
        super().__init__(f"corrupt JSONL at byte offset {byte_offset}: {detail}")


def _canonical(envelope: Envelope) -> bytes:
    value = ENVELOPE_ADAPTER.dump_python(envelope, mode="json")
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


class WindowsJsonlStore:
    """Append-only JSONL v1 store serialized by a Windows process lock."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._lock_path = path.with_name(path.name + ".lock")

    def append(self, envelope: Envelope) -> bool:
        line = _canonical(envelope)
        # Validate the precise bytes before they become durable.
        ENVELOPE_ADAPTER.validate_json(line)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._locked():
            existing = self._read_unlocked()
            for record in existing:
                if record.record_id != envelope.record_id:
                    continue
                if _canonical(record) == line:
                    return False
                raise RecordConflictError(envelope.record_id)
            with self._path.open("ab") as output:
                output.write(line + b"\n")
                output.flush()
                os.fsync(output.fileno())
        return True

    def read_all(self) -> tuple[Envelope, ...]:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._locked():
            return self._read_unlocked()

    def _read_unlocked(self) -> tuple[Envelope, ...]:
        if not self._path.exists():
            return ()
        data = self._path.read_bytes()
        if data and not data.endswith(b"\n"):
            offset = data.rfind(b"\n") + 1
            raise CorruptJsonlError(offset, "truncated final line")
        records: list[Envelope] = []
        seen: set[str] = set()
        offset = 0
        for raw_line in data.splitlines(keepends=True):
            payload = raw_line[:-1]
            try:
                record = ENVELOPE_ADAPTER.validate_json(payload, strict=True)
            except (ValidationError, ValueError) as exc:
                raise CorruptJsonlError(offset, type(exc).__name__) from exc
            if record.record_id in seen:
                raise DuplicateRecordError(record.record_id)
            seen.add(record.record_id)
            records.append(record)
            offset += len(raw_line)
        return tuple(records)

    def _locked(self) -> _WindowsLock:
        return _WindowsLock(self._lock_path)


class _WindowsLock:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._file: BinaryIO | None = None

    def __enter__(self) -> None:
        file = self._path.open("a+b")
        try:
            if file.tell() == 0:
                file.write(b"\0")
                file.flush()
            file.seek(0)
            msvcrt.locking(file.fileno(), msvcrt.LK_LOCK, 1)
            self._file = file
        except BaseException:
            file.close()
            raise

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        assert self._file is not None
        try:
            self._file.seek(0)
            msvcrt.locking(self._file.fileno(), msvcrt.LK_UNLCK, 1)
        finally:
            self._file.close()
