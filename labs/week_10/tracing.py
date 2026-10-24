"""Bounded request-local spans. This is a teaching format, not an OTel exporter."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from math import isfinite
import re
import secrets
from time import perf_counter_ns
from typing import Literal, TypeAlias

from labs.week_07.retrieval import ManifestCompatibilityError

Scalar: TypeAlias = str | int | float | bool | None
Attribute: TypeAlias = Scalar | tuple[Scalar, ...]
Status: TypeAlias = Literal["ok", "error", "cancelled"]


class TraceError(ValueError):
    """Invalid recorder setup, ownership or metadata contract."""


class ModelOutputError(ValueError):
    """A model adapter violated its declared response/identity contract."""


class Stage(StrEnum):
    REQUEST = "request"
    VALIDATION = "validation"
    QUERY_PLAN = "query_plan"
    SCOPE = "eligible_snapshot"
    RETRIEVAL = "retrieval"
    TOOL = "tool.hybrid_search"
    FUSION = "query_fusion"
    RERANK = "rerank"
    DEDUP = "deduplicate"
    CONTEXT = "context"
    CITATIONS = "citations"
    ANSWER = "extractive_answer"
    PROMPT = "prompt"
    MODEL = "model"


ALLOWED_ATTRIBUTES = frozenset(
    {
        "request_id",
        "pipeline_version",
        "implementation_id",
        "config_id",
        "snapshot_id",
        "request_manifest",
        "query_chars",
        "rewrite_count",
        "query_count",
        "query_index",
        "eligible_count",
        "candidate_count",
        "depth",
        "k",
        "candidate_ids",
        "retrieval_scores",
        "ranked_ids",
        "reranker_scores",
        "dropped_count",
        "selected_ids",
        "citation_count",
        "context_chars",
        "operation",
        "attempt",
        "outcome",
        "generation_mode",
        "prompt_version",
        "prompt_chars",
        "model_id",
        "model_revision",
        "model_mode",
        "model_contract_id",
        "input_tokens",
        "output_tokens",
        "cached_input_tokens",
        "usage_source",
        "price_id",
        "currency",
        "cost_estimate",
        "cost_reason",
    }
)


def _attributes(values: Mapping[str, Attribute]) -> dict[str, Attribute]:
    if len(values) > 16 or not set(values) <= ALLOWED_ATTRIBUTES:
        raise TraceError("unsupported or excessive trace attributes")
    for value in values.values():
        items = value if isinstance(value, tuple) else (value,)
        if len(items) > 32:
            raise TraceError("trace attribute array exceeds limit")
        for item in items:
            if type(item) not in (str, int, float, bool, type(None)):
                raise TraceError("trace attribute must be a bounded scalar")
            if isinstance(item, str) and len(item) > 256:
                raise TraceError("trace attribute text exceeds limit")
            if type(item) is int and abs(item) > 10**15:
                raise TraceError("trace attribute integer exceeds limit")
            if type(item) is float and not isfinite(item):
                raise TraceError("trace attribute must be finite")
    return dict(values)


def failure_code(error: BaseException) -> str:
    """Closed categories; never export an exception message or traceback."""
    if isinstance(error, (KeyboardInterrupt, SystemExit)):
        return "cancelled"
    if not isinstance(error, Exception):
        return "cancelled"
    if isinstance(error, ModelOutputError):
        return "model_contract"
    if isinstance(error, ManifestCompatibilityError):
        return "identity_drift"
    if isinstance(error, TimeoutError):
        return "timeout"
    if isinstance(error, PermissionError):
        return "permission"
    if isinstance(error, (ConnectionError, OSError)):
        return "dependency"
    if isinstance(error, ValueError):
        return "validation"
    return "internal"


@dataclass(frozen=True)
class SpanRecord:
    span_id: str
    parent_span_id: str | None
    name: str
    start_offset_ns: int | None
    duration_ns: int | None
    status: Status
    error_code: str | None
    attributes: tuple[tuple[str, Attribute], ...]


class Span:
    """A request-owned handle; explicit parents avoid global mutable context."""

    def __init__(
        self,
        owner: TraceRecorder,
        name: Stage,
        parent: Span | None,
        span_id: str | None,
        start: int | None,
    ) -> None:
        self.owner = owner
        self.name = name
        self.parent = parent
        self.span_id = span_id
        self.start = start
        self.closed = False
        self.values: dict[str, Attribute] = {}

    def set(self, **values: Attribute) -> None:
        if self.closed:
            raise TraceError("cannot change a closed span")
        self.values = _attributes({**self.values, **values})


class TraceRecorder:
    """One synchronous request, no shared task/thread state or background export."""

    def __init__(
        self,
        request_id: str,
        *,
        clock: Callable[[], int] = perf_counter_ns,
        ids: Callable[[int], str] = secrets.token_hex,
        utc_now: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
        clock_source: Literal["perf_counter_ns", "scripted_test"] = "perf_counter_ns",
        max_spans: int = 64,
    ) -> None:
        if (
            not isinstance(request_id, str)
            or re.fullmatch(r"[A-Za-z0-9_-]{1,64}", request_id) is None
        ):
            raise TraceError("request ID requires bounded safe characters")
        if type(max_spans) is not int or not 1 <= max_spans <= 256:
            raise TraceError("span capacity must be 1 to 256")
        if clock_source not in ("perf_counter_ns", "scripted_test"):
            raise TraceError("explicit clock source required")
        now = utc_now()
        offset = now.utcoffset()
        if now.tzinfo is None or offset is None or offset.total_seconds() != 0:
            raise TraceError("trace chronology requires aware UTC")
        self.request_id = request_id
        self.started_at = now.isoformat()
        self.clock_source = clock_source
        self.clock = clock
        self.ids = ids
        self.max_spans = max_spans
        self.used_ids: set[str] = set()
        self.trace_id = self._id(16)
        self.records: list[SpanRecord] = []
        self.dropped_spans = 0
        self.timing_errors = 0
        self.allocated = 0
        self.active = 0
        self.open_handles: set[Span] = set()
        self.root_started = False
        self.previous_tick: int | None = None
        self.origin = self._now()

    def _id(self, size: int) -> str:
        value = self.ids(size)
        if (
            not isinstance(value, str)
            or re.fullmatch(rf"[0-9a-f]{{{size * 2}}}", value) is None
            or set(value) == {"0"}
            or value in self.used_ids
        ):
            raise TraceError("identity factory returned an invalid or repeated ID")
        self.used_ids.add(value)
        return value

    def _now(self) -> int | None:
        try:
            value = self.clock()
            if (
                type(value) is not int
                or value < 0
                or (self.previous_tick is not None and value < self.previous_tick)
            ):
                raise TraceError("invalid monotonic reading")
        except Exception:
            self.timing_errors += 1
            return None
        self.previous_tick = value
        return value

    @contextmanager
    def span(self, name: Stage, *, parent: Span | None = None) -> Iterator[Span]:
        if not isinstance(name, Stage):
            raise TraceError("span name must be a declared stage")
        if parent is None:
            if self.root_started or name != Stage.REQUEST:
                raise TraceError("one request root required")
            self.root_started = True
        elif (
            parent.owner is not self or parent.closed or parent not in self.open_handles
        ):
            raise TraceError("parent must be active in this request")
        enabled = self.allocated < self.max_spans and (
            parent is None or parent.span_id is not None
        )
        if enabled:
            identifier = self._id(8)
            self.allocated += 1
        else:
            identifier = None
            self.dropped_spans += 1
        handle = Span(self, name, parent, identifier, self._now() if enabled else None)
        status: Status = "ok"
        code = None
        self.active += 1
        self.open_handles.add(handle)
        try:
            yield handle
        except BaseException as error:
            code = failure_code(error)
            status = "cancelled" if code == "cancelled" else "error"
            raise
        finally:
            end = self._now() if enabled else None
            handle.closed = True
            self.active -= 1
            self.open_handles.remove(handle)
            if identifier is not None:
                start = handle.start
                self.records.append(
                    SpanRecord(
                        identifier,
                        parent.span_id if parent else None,
                        name.value,
                        start - self.origin
                        if start is not None and self.origin is not None
                        else None,
                        end - start if end is not None and start is not None else None,
                        status,
                        code,
                        tuple(handle.values.items()),
                    )
                )

    def document(self) -> dict[str, object]:
        if self.active or not any(
            s.name == Stage.REQUEST.value and s.parent_span_id is None
            for s in self.records
        ):
            raise TraceError("trace must have a completed request root")
        return {
            "schema": "week10-local-trace/1.0.0",
            "trace_id": self.trace_id,
            "request_id": self.request_id,
            "started_at_utc": self.started_at,
            "clock_source": self.clock_source,
            "dropped_span_count": self.dropped_spans,
            "timing_error_count": self.timing_errors,
            "telemetry_complete": self.dropped_spans == self.timing_errors == 0,
            "spans": [
                {
                    "span_id": s.span_id,
                    "parent_span_id": s.parent_span_id,
                    "name": s.name,
                    "start_offset_ns": s.start_offset_ns,
                    "duration_ns": s.duration_ns,
                    "status": s.status,
                    "error_code": s.error_code,
                    "attributes": dict(s.attributes),
                }
                for s in self.records
            ],
        }


@dataclass(frozen=True)
class Delivery:
    delivered: bool
    error_code: str | None


def deliver(
    recorder: TraceRecorder, sink: Callable[[dict[str, object]], None]
) -> Delivery:
    """One explicit export attempt; preserve the separately obtained application result."""
    document = recorder.document()
    try:
        sink(document)
    except Exception:
        return Delivery(False, "telemetry_delivery_failed")
    return Delivery(True, None)
