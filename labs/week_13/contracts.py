"""Closed local contracts; model data cannot construct caller authority."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from hashlib import sha256
import json
import math
from typing import Annotated, Literal, Self, get_args

from pydantic import BaseModel, ConfigDict, Field, model_validator

from labs.week_11.policy import SecurityContext, bounded_json, identifier

Identifier = Annotated[str, Field(pattern=r"^[A-Za-z0-9_-]{1,64}$")]
Money = Annotated[str, Field(pattern=r"^(0|[1-9][0-9]{0,5})\.[0-9]{2}$")]
Currency = Literal["USD", "INR"]
Unit = Literal["kg", "tonne", "piece"]
Reason = Literal["price_variance", "supplier_change"]
ErrorCode = Literal[
    "invalid_arguments",
    "unknown_tool",
    "forbidden",
    "not_found",
    "approval_required",
    "conflict",
    "unavailable",
    "timeout",
    "unknown_outcome",
    "result_invalid",
    "tool_failed",
]


class ToolError(Exception):
    """Only controlled categories cross the tool-result boundary."""

    def __init__(self, code: ErrorCode) -> None:
        if not isinstance(code, str) or code not in get_args(ErrorCode):
            code = "tool_failed"
        super().__init__(code)
        self.code = code


class Closed(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class SqlArgs(Closed):
    query_name: Literal["open_purchase_orders", "purchase_order_by_id"]
    purchase_order_id: Identifier | None
    limit: int = Field(ge=1, le=5)

    @model_validator(mode="after")
    def selected_query(self) -> Self:
        if (self.query_name == "purchase_order_by_id") != (
            self.purchase_order_id is not None
        ):
            raise ValueError("query_arguments")
        return self


class VarianceArgs(Closed):
    baseline: Money
    current: Money
    baseline_currency: Currency
    current_currency: Currency
    baseline_unit: Unit
    current_unit: Unit

    @model_validator(mode="after")
    def comparable(self) -> Self:
        if (
            Decimal(self.baseline) <= 0
            or self.baseline_currency != self.current_currency
            or self.baseline_unit != self.current_unit
        ):
            raise ValueError("incomparable_prices")
        return self


class SupplierArgs(Closed):
    supplier_id: Identifier


class CommodityArgs(Closed):
    commodity_id: Identifier


class SearchArgs(Closed):
    question: str = Field(min_length=1, max_length=1000)

    @model_validator(mode="after")
    def usable_question(self) -> Self:
        if not self.question.strip():
            raise ValueError("question")
        self.question.encode("utf-8")
        raw = json.dumps(
            {"question": self.question}, ensure_ascii=False, separators=(",", ":")
        )
        if len(raw.encode("utf-8")) > 4096:
            raise ValueError("question_bytes")
        return self


class ReviewArgs(Closed):
    purchase_order_id: Identifier
    reason: Reason


class ToolCall(Closed):
    kind: Literal["tool_call"]
    call_id: Identifier
    name: Annotated[str, Field(pattern=r"^[a-z_]{1,40}$")]
    arguments: dict[str, object]


class FinalTurn(Closed):
    kind: Literal["final"]
    text: str = Field(min_length=1, max_length=1000)
    evidence_call_ids: list[Identifier] = Field(max_length=6)

    @model_validator(mode="after")
    def unique_evidence(self) -> Self:
        if len(set(self.evidence_call_ids)) != len(self.evidence_call_ids):
            raise ValueError("duplicate_evidence")
        return self


class PurchaseOrder(Closed):
    purchase_order_id: Identifier
    supplier_id: Identifier
    commodity_id: Identifier
    baseline: Money
    current: Money
    currency: Currency
    unit: Unit


class SqlResult(Closed):
    query_name: Literal["open_purchase_orders", "purchase_order_by_id"]
    rows: list[PurchaseOrder] = Field(max_length=5)


class VarianceResult(Closed):
    delta: Annotated[str, Field(pattern=r"^-?[0-9]{1,14}\.[0-9]{2}$")]
    percent: Annotated[str, Field(pattern=r"^-?[0-9]{1,14}\.[0-9]{2}$")]
    currency: Currency
    unit: Unit
    rounding: Literal["ROUND_HALF_EVEN"]


class SupplierResult(Closed):
    supplier_id: Identifier
    name: str = Field(min_length=1, max_length=80)
    status: Literal["active", "suspended"]


class CommodityResult(Closed):
    commodity_id: Identifier
    amount: Money
    currency: Currency
    unit: Unit
    as_of: Annotated[str, Field(pattern=r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")]
    source: Literal["synthetic-fixture"]

    @model_validator(mode="after")
    def calendar_date(self) -> Self:
        date.fromisoformat(self.as_of)
        return self


class SearchResult(Closed):
    status: Literal["answered", "refused"]
    answer: str = Field(max_length=2000)
    citation_ids: list[Identifier] = Field(max_length=3)


class ReviewResult(Closed):
    review_id: Annotated[str, Field(pattern=r"^[a-f0-9]{32}$")]
    purchase_order_id: Identifier
    reason: Reason
    status: Literal["open"]
    replayed: bool


@dataclass(frozen=True)
class Approval:
    """Trusted in-process evidence fixture, NOT a signed or authenticated token."""

    digest: str
    expires: float


@dataclass(frozen=True)
class Actor:
    """Trusted caller supplies this; its constructor is not a login service."""

    context: SecurityContext
    writable: bool = False
    operation_key: str | None = None
    approval: Approval | None = None

    def __post_init__(self) -> None:
        if (
            not isinstance(self.context, SecurityContext)
            or type(self.writable) is not bool
        ):
            raise ValueError("actor_invalid")
        if self.operation_key is not None:
            identifier(self.operation_key)
        if self.approval is not None and (
            not isinstance(self.approval, Approval)
            or not math.isfinite(self.approval.expires)
        ):
            raise ValueError("actor_invalid")


def wire(value: object, max_bytes: int = 8192) -> str:
    """Bound the actual compact UTF-8 representation, without silent coercion."""
    try:
        raw = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        if len(raw.encode("utf-8")) > max_bytes:
            raise ToolError("result_invalid")
    except (TypeError, ValueError, UnicodeError) as error:
        raise ToolError("result_invalid") from error
    return raw


def parse_turn(raw: str) -> ToolCall | FinalTurn:
    value = bounded_json(raw, max_bytes=8192)
    if not isinstance(value, dict):
        raise ValueError("turn_shape")
    turn = (
        FinalTurn.model_validate(value)
        if value.get("kind") == "final"
        else ToolCall.model_validate(value)
    )
    wire(turn.model_dump(mode="json"))
    return turn


def intent_digest(actor: Actor, arguments: ReviewArgs) -> str:
    if actor.operation_key is None:
        raise ToolError("approval_required")
    return sha256(
        wire(
            {
                "schema": "create_review/1",
                "tenant": actor.context.tenant_id,
                "principal": actor.context.principal_id,
                "operation_key": actor.operation_key,
                "arguments": arguments.model_dump(mode="json"),
            }
        ).encode("utf-8")
    ).hexdigest()


def check_approval(actor: Actor, arguments: ReviewArgs, now: float) -> str:
    if not actor.writable:
        raise ToolError("forbidden")
    digest = intent_digest(actor, arguments)
    if (
        actor.approval is None
        or actor.approval.digest != digest
        or now >= actor.approval.expires
    ):
        raise ToolError("approval_required")
    return digest
