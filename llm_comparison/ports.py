from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Mapping, Protocol

from llm_comparison.models import BaselineRequest, Envelope, TrialResult


class ModelClientError(Exception):
    """Expected adapter failure containing only a stable, pre-sanitized code."""

    def __init__(self, category: str, safe_code: str) -> None:
        if not safe_code.replace("_", "").isalnum() or len(safe_code) > 128:
            raise ValueError("safe_code must be a bounded identifier")
        self.category = category
        self.safe_code = safe_code
        super().__init__(safe_code)


class Clock(Protocol):
    def monotonic(self) -> float: ...

    def utc_now(self) -> datetime: ...


class SystemClock:
    def monotonic(self) -> float:
        return time.monotonic()

    def utc_now(self) -> datetime:
        return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class HttpResponse:
    status_code: int
    body: bytes
    headers: Mapping[str, str]


class HttpTransport(Protocol):
    """Synchronous transport.

    A timeout bounds how long the caller waits. It does not prove that generation
    has stopped in the external server process.
    """

    def request(
        self,
        *,
        method: str,
        url: str,
        headers: Mapping[str, str],
        body: bytes | None,
        timeout_seconds: float,
    ) -> HttpResponse: ...


class ModelClient(Protocol):
    def generate(self, request: BaselineRequest) -> TrialResult: ...


class EnvelopeStore(Protocol):
    def append(self, envelope: Envelope) -> bool: ...

    def read_all(self) -> tuple[Envelope, ...]: ...
