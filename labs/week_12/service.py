"""Process-local admission/cache/rate controls around the actual Week 11 flow."""

from __future__ import annotations

import asyncio
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, replace
from math import ceil
import json
import logging
import time

from labs.week_07.retrieval import digest_text
from labs.week_11.assistant import Limits, REFUSAL, SecuredResult, secure_ask
from labs.week_11.policy import PolicyStore, SecurityContext, findings
from labs.week_12.config import Settings
from labs.week_12.store import Repository, Snapshot

logger = logging.getLogger(__name__)
Compute = Callable[[SecurityContext, str, Snapshot, Limits], SecuredResult]
CacheKey = tuple[str, str, str, str, int]


class Busy(Exception):
    """No process-local expensive-work slot is available."""


class FixedWindow:
    """Two authenticated demo identities bound this limiter's key population."""

    def __init__(self, limit: int, clock: Callable[[], float] = time.monotonic) -> None:
        self.limit = limit
        self.clock = clock
        self.windows: dict[tuple[str, str], tuple[int, int]] = {}

    def consume(self, context: SecurityContext) -> int:
        """Return zero if admitted, else Retry-After seconds. One event loop only."""
        now = self.clock()
        window = int(now // 60)
        key = context.tenant_id, context.principal_id
        previous, count = self.windows.get(key, (window, 0))
        if previous != window:
            count = 0
        if count >= self.limit:
            return max(1, ceil((window + 1) * 60 - now))
        self.windows[key] = window, count + 1
        return 0


@dataclass(frozen=True)
class CacheEntry:
    expires: float
    result: SecuredResult


class ResultCache:
    def __init__(
        self, seconds: int, clock: Callable[[], float] = time.monotonic
    ) -> None:
        self.seconds = seconds
        self.clock = clock
        self.entries: OrderedDict[CacheKey, CacheEntry] = OrderedDict()

    def get(self, key: CacheKey) -> SecuredResult | None:
        entry = self.entries.get(key)
        if entry is None:
            return None
        if self.clock() >= entry.expires:
            del self.entries[key]
            return None
        self.entries.move_to_end(key)
        return entry.result

    def put(self, key: CacheKey, result: SecuredResult) -> None:
        if result.reason != "ok":
            return
        self.entries[key] = CacheEntry(self.clock() + self.seconds, result)
        self.entries.move_to_end(key)
        while len(self.entries) > 32:
            self.entries.popitem(last=False)


def compute_answer(
    context: SecurityContext, question: str, snapshot: Snapshot, limits: Limits
) -> SecuredResult:
    return secure_ask(
        context,
        json.dumps({"question": question}, ensure_ascii=False, separators=(",", ":")),
        snapshot.chunks,
        PolicyStore(snapshot.policies),
        limits=limits,
    )


class GuardedService:
    def __init__(
        self,
        settings: Settings,
        repository: Repository,
        *,
        clock: Callable[[], float] = time.monotonic,
        compute: Compute = compute_answer,
    ) -> None:
        self.repository = repository
        self.limits = Limits(settings.context_chars)
        self.rate = FixedWindow(settings.requests_per_minute, clock)
        self.cache = ResultCache(settings.cache_seconds, clock)
        self.compute = compute
        self.slots: asyncio.Queue[int] = asyncio.Queue(maxsize=2)
        for token in range(2):
            self.slots.put_nowait(token)
        self.work: set[asyncio.Task[SecuredResult]] = set()

    async def ask(
        self, context: SecurityContext, question: str
    ) -> tuple[SecuredResult, bool]:
        if findings(question):
            return SecuredResult(
                REFUSAL, (), context.request_id, "input_blocked", 0, 0
            ), False
        try:
            token = self.slots.get_nowait()
        except asyncio.QueueEmpty as error:
            raise Busy("busy") from error
        worker: asyncio.Task[SecuredResult] | None = None
        try:
            async with asyncio.timeout(4):
                first = await self.repository.snapshot(context, question)
            fingerprint = first.fingerprint()
            key = (
                context.tenant_id,
                context.principal_id,
                digest_text("week12-guarded-v1\x00" + question),
                fingerprint,
                self.limits.context_chars,
            )
            cached = self.cache.get(key)
            hit = cached is not None
            if cached is None:
                worker = asyncio.create_task(
                    asyncio.to_thread(
                        self.compute, context, question, first, self.limits
                    )
                )
                self.work.add(worker)
                worker.add_done_callback(self.work.discard)
                # Cancelling this await cannot terminate a running Python thread.
                result = await asyncio.shield(worker)
            else:
                result = replace(cached, request_id=context.request_id)
            # A NEW transaction sees changes hidden by the earlier repeatable-read snapshot.
            async with asyncio.timeout(4):
                current = await self.repository.snapshot(context, question)
            if current.fingerprint() != fingerprint:
                self.cache.entries.pop(key, None)
                return SecuredResult(
                    REFUSAL, (), context.request_id, "source_changed", 0, 0
                ), False
            if not hit:
                self.cache.put(key, result)
            logger.info(
                "rag_answer_checked",
                extra={
                    "request_id": context.request_id,
                    "reason": result.reason,
                    "cache_hit": hit,
                },
            )
            return result, hit
        finally:
            if worker is not None and not worker.done():

                def release_after_completion(task: asyncio.Task[SecuredResult]) -> None:
                    if not task.cancelled():
                        task.exception()  # Retrieve a failure without printing its payload.
                    self.slots.put_nowait(token)

                worker.add_done_callback(release_after_completion)
            else:
                self.slots.put_nowait(token)

    async def close(self) -> None:
        if self.work:
            await asyncio.gather(*tuple(self.work), return_exceptions=True)
        self.cache.entries.clear()
        self.rate.windows.clear()
        await self.repository.close()
