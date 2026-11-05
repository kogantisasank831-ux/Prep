"""Closed contracts for the Week 19 agent-safety gateway."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator


Identifier = Annotated[
    str, Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9._:-]+$")
]
Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Permission = Literal[
    "contract:read",
    "order:read",
    "risk:read",
    "review_flag:write",
    "review_flag:revert",
]
ToolMode = Literal["read", "write"]
ToolName = Literal[
    "contract_lookup",
    "purchase_order_lookup",
    "supplier_risk_lookup",
    "review_flag_set",
    "review_flag_revert",
]
ResultStatus = Literal["completed", "blocked", "failed"]
EventType = Literal[
    "requested",
    "approval_checked",
    "denied",
    "executed",
    "reversed",
    "failed",
    "step_limit",
]
DecisionCode = Literal[
    "request_received",
    "approval_valid",
    "ok",
    "unknown_tool",
    "invalid_arguments",
    "secret_material_rejected",
    "permission_denied",
    "approval_required",
    "approval_not_found",
    "approval_mismatch",
    "approval_reused",
    "step_limit_exceeded",
    "data_not_found",
    "undo_not_found",
    "undo_already_used",
    "undo_conflict",
    "tool_failure",
]


class StrictModel(BaseModel):
    """Reject coercion and unknown fields at every trust boundary."""

    model_config = ConfigDict(
        allow_inf_nan=False, extra="forbid", frozen=True, strict=True
    )


class TrustedScope(StrictModel):
    """Identity and authority supplied by trusted application code."""

    tenant_id: Identifier
    principal_id: Identifier
    run_id: Identifier
    case_id: Identifier
    permissions: tuple[Permission, ...]

    @model_validator(mode="after")
    def permissions_are_unique(self) -> TrustedScope:
        if len(set(self.permissions)) != len(self.permissions):
            raise ValueError("duplicate_permission")
        return self


class GatewayConfig(StrictModel):
    """A hard execution budget, enforced outside agent-generated text."""

    max_steps: Annotated[int, Field(ge=1, le=20)] = 6


class ToolRequest(StrictModel):
    """One proposed tool call; authority is deliberately absent."""

    request_id: Identifier
    tool: Identifier
    arguments: dict[str, JsonValue]
    approval_id: Identifier | None = None


class ApprovalGrant(StrictModel):
    """One human decision bound to one exact write request."""

    approval_id: Identifier
    tenant_id: Identifier
    principal_id: Identifier
    run_id: Identifier
    case_id: Identifier
    request_id: Identifier
    tool: Identifier
    argument_sha256: Sha256
    approved_by: Identifier


class AuditEvent(StrictModel):
    """Secret-minimized, append-only event linked to its predecessor."""

    sequence: Annotated[int, Field(ge=1)]
    event_type: EventType
    tenant_id: Identifier
    principal_id: Identifier
    run_id: Identifier
    case_id: Identifier
    tool: Identifier
    code: DecisionCode
    argument_sha256: Sha256
    approval_id: Identifier | None
    approved_by: Identifier | None
    previous_hash: Sha256
    event_hash: Sha256


class ActionReceipt(StrictModel):
    """Proof of a reversible local write and its opaque undo capability."""

    action_id: Identifier
    tool: Literal["review_flag_set"]
    resource_id: Identifier
    before: Literal["clear", "needs_human"]
    after: Literal["clear", "needs_human"]
    undo_token: Identifier


class ToolResult(StrictModel):
    """A controlled result that never includes arbitrary exception text."""

    request_id: Identifier
    tool: Identifier
    step: Annotated[int, Field(ge=1)]
    status: ResultStatus
    code: DecisionCode
    data: dict[str, JsonValue]
    receipt: ActionReceipt | None
    audit_head: Sha256

    @model_validator(mode="after")
    def result_fields_agree(self) -> ToolResult:
        if self.status == "completed" and self.code != "ok":
            raise ValueError("completed_result_requires_ok")
        if self.status != "completed" and self.code == "ok":
            raise ValueError("noncompleted_result_cannot_be_ok")
        if self.receipt is not None and self.tool != "review_flag_set":
            raise ValueError("receipt_tool_mismatch")
        return self
