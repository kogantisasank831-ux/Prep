"""A bounded serial loop around untrusted proposals and trusted local adapters."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
import logging
import math
from typing import Literal, Protocol

from pydantic import BaseModel, ValidationError

from labs.week_11.assistant import secure_ask
from labs.week_11.policy import PolicyStore, SecurityViolation, parse_question
from labs.week_12.fixtures import seed_records
from labs.week_13.contracts import (
    Actor,
    CommodityArgs,
    CommodityResult,
    ErrorCode,
    FinalTurn,
    ReviewArgs,
    ReviewResult,
    SearchArgs,
    SearchResult,
    SqlArgs,
    SqlResult,
    SupplierArgs,
    SupplierResult,
    ToolCall,
    ToolError,
    VarianceArgs,
    VarianceResult,
    check_approval,
    parse_turn,
    wire,
)
from labs.week_13.store import Store

logger = logging.getLogger(__name__)
Handler = Callable[[Actor, BaseModel], Awaitable[object]]
Effect = Literal["read", "write"]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    arguments: type[BaseModel]
    result: type[BaseModel]
    effect: Effect
    handler: Handler

    def definition(self) -> dict[str, object]:
        return dict(
            name=self.name,
            description=self.description,
            effect=self.effect,
            parameters=self.arguments.model_json_schema(),
        )


def variance(args: VarianceArgs) -> dict[str, object]:
    with localcontext() as context:
        context.prec = 28
        delta = Decimal(args.current) - Decimal(args.baseline)
        percent = delta / Decimal(args.baseline) * 100
        return dict(
            delta=str(delta.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)),
            percent=str(percent.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)),
            currency=args.current_currency,
            unit=args.current_unit,
            rounding="ROUND_HALF_EVEN",
        )


def registry(store: Store) -> dict[str, ToolSpec]:
    chunks, policies = seed_records()
    catalogue = PolicyStore(policies)

    async def execute(actor: Actor, args: BaseModel) -> object:
        # These fixed tiny synchronous local adapters do not create threads.
        # Their driver busy bound is separate from cooperative asyncio deadlines.
        if isinstance(args, SqlArgs):
            return store.sql(actor, args)
        if isinstance(args, VarianceArgs):
            return variance(args)
        if isinstance(args, SupplierArgs):
            return store.supplier(actor, args)
        if isinstance(args, CommodityArgs):
            return store.commodity(actor, args)
        if isinstance(args, ReviewArgs):
            return store.create_review(actor, args)
        if isinstance(args, SearchArgs):
            result = secure_ask(
                actor.context,
                wire({"question": args.question}, 4096),
                chunks,
                catalogue,
            )
            return dict(
                status="answered" if result.reason == "ok" else "refused",
                answer=result.answer,
                citation_ids=list(result.citation_ids),
            )
        raise ToolError("invalid_arguments")

    rows: list[tuple[str, str, type[BaseModel], type[BaseModel], Effect]] = [
        (
            "sql_query",
            "Read accessible purchase orders using one of two named queries.",
            SqlArgs,
            SqlResult,
            "read",
        ),
        (
            "price_variance",
            "Compare two stated prices only in the same currency and unit.",
            VarianceArgs,
            VarianceResult,
            "read",
        ),
        (
            "supplier_lookup",
            "Read a supplier linked to a purchase order you may access.",
            SupplierArgs,
            SupplierResult,
            "read",
        ),
        (
            "commodity_price",
            "Read a dated synthetic commodity fixture, not a live quote.",
            CommodityArgs,
            CommodityResult,
            "read",
        ),
        (
            "document_search",
            "Search allowed pinned sources through the guarded quote assistant.",
            SearchArgs,
            SearchResult,
            "read",
        ),
        (
            "create_review",
            "Create one local review record with separate authority and approval.",
            ReviewArgs,
            ReviewResult,
            "write",
        ),
    ]
    return {
        name: ToolSpec(name, description, args, output, effect, execute)
        for name, description, args, output, effect in rows
    }


@dataclass(frozen=True)
class Outcome:
    call_id: str
    name: str
    status: Literal["ok", "error", "unknown"]
    data: dict[str, object] | None
    error: ErrorCode | None
    attempts: int

    def envelope(self) -> dict[str, object]:
        return dict(
            call_id=self.call_id,
            name=self.name,
            status=self.status,
            data=self.data,
            error=self.error,
            attempts=self.attempts,
        )


class Dispatcher:
    def __init__(
        self,
        tools: dict[str, ToolSpec],
        *,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        clock: Callable[[], float] | None = None,
    ) -> None:
        import time

        self.tools = dict(tools)
        self.sleep = sleep
        self.clock = clock or time.monotonic

    def definitions(self, actor: Actor) -> tuple[dict[str, object], ...]:
        return tuple(
            spec.definition()
            for spec in self.tools.values()
            if spec.effect == "read" or actor.writable
        )

    async def call(self, actor: Actor, call: ToolCall, seconds: float) -> Outcome:
        spec = self.tools.get(call.name)
        if spec is None:
            return Outcome(call.call_id, call.name, "error", None, "unknown_tool", 0)
        try:
            arguments = spec.arguments.model_validate(call.arguments)
            wire(arguments.model_dump(mode="json"))
            if spec.effect == "write":
                if not isinstance(arguments, ReviewArgs):
                    raise ToolError("forbidden")
                check_approval(actor, arguments, self.clock())
        except (ValidationError, UnicodeError):
            return Outcome(
                call.call_id, call.name, "error", None, "invalid_arguments", 0
            )
        except ToolError as error:
            return Outcome(call.call_id, call.name, "error", None, error.code, 0)
        attempts = 2 if spec.effect == "read" else 1
        for attempt in range(1, attempts + 1):
            code: ErrorCode
            try:
                async with asyncio.timeout(seconds):
                    value = await spec.handler(actor, arguments)
                if isinstance(value, BaseModel):
                    value = value.model_dump(mode="python")
                output = spec.result.model_validate(value).model_dump(mode="json")
                wire(output, 4096)
                logger.info(
                    "tool_attempt_finished",
                    extra={
                        "request_id": actor.context.request_id,
                        "tool": spec.name,
                        "category": "ok",
                        "attempts": attempt,
                    },
                )
                return Outcome(call.call_id, call.name, "ok", output, None, attempt)
            except TimeoutError:
                code = "timeout"
            except (ValidationError, UnicodeError):
                code = "result_invalid"
            except ToolError as error:
                code = error.code
            except Exception as error:
                logger.error(
                    "tool_adapter_failed",
                    extra={
                        "request_id": actor.context.request_id,
                        "tool": spec.name,
                        "error_type": type(error).__name__,
                    },
                )
                code = "tool_failed"
            # Cancellation is BaseException and deliberately propagates.
            if spec.effect == "write" and code not in {
                "forbidden",
                "not_found",
                "approval_required",
                "conflict",
                "invalid_arguments",
            }:
                logger.warning(
                    "tool_outcome_unknown",
                    extra={
                        "request_id": actor.context.request_id,
                        "tool": spec.name,
                        "category": "unknown_outcome",
                        "attempts": attempt,
                    },
                )
                return Outcome(
                    call.call_id, call.name, "unknown", None, "unknown_outcome", attempt
                )
            if code not in {"timeout", "unavailable"} or attempt == attempts:
                logger.info(
                    "tool_attempt_finished",
                    extra={
                        "request_id": actor.context.request_id,
                        "tool": spec.name,
                        "category": code,
                        "attempts": attempt,
                    },
                )
                return Outcome(call.call_id, call.name, "error", None, code, attempt)
            await self.sleep(0.05)
        raise AssertionError("unreachable_attempt_state")


@dataclass(frozen=True)
class Message:
    role: Literal["user", "assistant", "tool"]
    content: str
    call_id: str | None = None

    def envelope(self) -> dict[str, object]:
        return dict(role=self.role, content=self.content, call_id=self.call_id)


class Planner(Protocol):
    async def next_turn(
        self,
        messages: tuple[Message, ...],
        tools: tuple[dict[str, object], ...],
    ) -> str: ...


@dataclass(frozen=True)
class Limits:
    max_calls: int = 6
    max_turns: int = 8
    attempt_seconds: float = 0.5
    run_seconds: float = 5.0
    transcript_bytes: int = 32768

    def __post_init__(self) -> None:
        for value, low, high in (
            (self.max_calls, 1, 6),
            (self.max_turns, 1, 8),
            (self.transcript_bytes, 1024, 32768),
        ):
            if type(value) is not int or not low <= value <= high:
                raise ValueError("limits_invalid")
        for seconds in (self.attempt_seconds, self.run_seconds):
            if (
                type(seconds) not in (int, float)
                or not math.isfinite(seconds)
                or not 0 < seconds <= 5
            ):
                raise ValueError("limits_invalid")


@dataclass(frozen=True)
class RunResult:
    status: str
    text: str
    outcomes: tuple[Outcome, ...]
    messages: tuple[Message, ...]


async def run(
    actor: Actor,
    question: str,
    planner: Planner,
    dispatcher: Dispatcher,
    limits: Limits = Limits(),
) -> RunResult:
    """Execute the local protocol; callbacks must cooperate with cancellation."""
    messages: list[Message] = []
    outcomes: list[Outcome] = []
    seen: set[str] = set()
    active: ToolCall | None = None

    def finish(status: str, text: str) -> RunResult:
        return RunResult(status, text, tuple(outcomes), tuple(messages))

    def append(message: Message) -> None:
        wire([m.envelope() for m in (*messages, message)], limits.transcript_bytes)
        messages.append(message)

    try:
        question = parse_question(wire({"question": question}, 4096))
    except (SecurityViolation, ToolError):
        return finish(
            "invalid_request", "The question does not meet the input contract."
        )
    try:
        append(Message("user", question))
    except ToolError:
        return finish(
            "budget_exhausted", "The serialized transcript budget was exhausted."
        )
    try:
        async with asyncio.timeout(limits.run_seconds):
            for _ in range(limits.max_turns):
                async with asyncio.timeout(limits.attempt_seconds):
                    raw = await planner.next_turn(
                        tuple(messages), dispatcher.definitions(actor)
                    )
                try:
                    turn = parse_turn(raw)
                except (SecurityViolation, ValidationError, ValueError, ToolError):
                    return finish(
                        "invalid_model_output", "The proposed turn was rejected."
                    )
                if isinstance(turn, FinalTurn):
                    successful = {o.call_id for o in outcomes if o.status == "ok"}
                    if not set(turn.evidence_call_ids) <= successful:
                        return finish(
                            "invalid_model_output",
                            "The final evidence references were rejected.",
                        )
                    append(Message("assistant", wire(turn.model_dump(mode="json"))))
                    return finish("complete", turn.text)
                if turn.call_id in seen:
                    return finish("invalid_model_output", "A call ID was reused.")
                if len(outcomes) >= limits.max_calls:
                    return finish(
                        "budget_exhausted", "The tool-call budget was exhausted."
                    )
                seen.add(turn.call_id)
                append(
                    Message(
                        "assistant", wire(turn.model_dump(mode="json")), turn.call_id
                    )
                )
                active = turn
                result = await dispatcher.call(actor, turn, limits.attempt_seconds)
                outcomes.append(result)
                active = None
                append(Message("tool", wire(result.envelope()), turn.call_id))
                if result.status == "unknown":
                    return finish(
                        "unknown_outcome", "Reconcile using the original operation key."
                    )
            return finish("budget_exhausted", "The planner-turn budget was exhausted.")
    except TimeoutError:
        if active is not None:
            spec = dispatcher.tools.get(active.name)
            if spec is not None and spec.effect == "write":
                outcomes.append(
                    Outcome(
                        active.call_id,
                        active.name,
                        "unknown",
                        None,
                        "unknown_outcome",
                        1,
                    )
                )
                return finish(
                    "unknown_outcome", "Reconcile using the original operation key."
                )
        return finish("budget_exhausted", "A cooperative deadline was reached.")
    except ToolError:
        return finish(
            "budget_exhausted", "The serialized transcript budget was exhausted."
        )
    except Exception as error:
        logger.error(
            "planner_failed",
            extra={
                "request_id": actor.context.request_id,
                "error_type": type(error).__name__,
            },
        )
        return finish("planner_failed", "The planner did not complete.")
