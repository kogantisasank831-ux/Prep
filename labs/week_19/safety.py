"""Deterministic policy, approval, audit and sandbox controls for Week 19."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Final, Literal, cast

from pydantic import JsonValue

from labs.week_19.models import (
    ActionReceipt,
    ApprovalGrant,
    AuditEvent,
    DecisionCode,
    EventType,
    GatewayConfig,
    Permission,
    ToolMode,
    ToolName,
    ToolRequest,
    ToolResult,
    TrustedScope,
)


ROOT_HASH: Final = "0" * 64
IDENTIFIER_PATTERN: Final = re.compile(r"^[A-Za-z0-9._:-]{1,80}$")
SECRET_KEY_PARTS: Final[tuple[str, ...]] = (
    "api_key",
    "apikey",
    "authorization",
    "credential",
    "password",
    "secret",
    "token",
)


@dataclass(frozen=True, slots=True)
class ToolPolicy:
    """Server-owned policy for one closed tool entry."""

    permission: Permission
    mode: ToolMode
    argument_names: frozenset[str]


TOOL_POLICIES: Final[dict[ToolName, ToolPolicy]] = {
    "contract_lookup": ToolPolicy(
        permission="contract:read",
        mode="read",
        argument_names=frozenset({"contract_id"}),
    ),
    "purchase_order_lookup": ToolPolicy(
        permission="order:read",
        mode="read",
        argument_names=frozenset({"order_id"}),
    ),
    "supplier_risk_lookup": ToolPolicy(
        permission="risk:read",
        mode="read",
        argument_names=frozenset({"supplier_id"}),
    ),
    "review_flag_set": ToolPolicy(
        permission="review_flag:write",
        mode="write",
        argument_names=frozenset({"flag_id", "value"}),
    ),
    "review_flag_revert": ToolPolicy(
        permission="review_flag:revert",
        mode="write",
        argument_names=frozenset({"undo_token"}),
    ),
}


def argument_digest(arguments: dict[str, JsonValue]) -> str:
    """Return a stable digest without retaining the argument values."""

    encoded = json.dumps(
        arguments,
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_approval(
    scope: TrustedScope,
    request: ToolRequest,
    *,
    approval_id: str,
    approved_by: str,
) -> ApprovalGrant:
    """Build a fixture grant as if a separate trusted approval service issued it."""

    return ApprovalGrant(
        approval_id=approval_id,
        tenant_id=scope.tenant_id,
        principal_id=scope.principal_id,
        run_id=scope.run_id,
        case_id=scope.case_id,
        request_id=request.request_id,
        tool=request.tool,
        argument_sha256=argument_digest(request.arguments),
        approved_by=approved_by,
    )


def _event_body(event: AuditEvent) -> dict[str, JsonValue]:
    return {
        "approval_id": event.approval_id,
        "approved_by": event.approved_by,
        "argument_sha256": event.argument_sha256,
        "case_id": event.case_id,
        "code": event.code,
        "event_type": event.event_type,
        "previous_hash": event.previous_hash,
        "principal_id": event.principal_id,
        "run_id": event.run_id,
        "sequence": event.sequence,
        "tenant_id": event.tenant_id,
        "tool": event.tool,
    }


def _hash_event_body(body: dict[str, JsonValue]) -> str:
    encoded = json.dumps(
        body,
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class HashChainedAuditTrail:
    """Append-only in-process audit events with deterministic tamper evidence."""

    def __init__(self, scope: TrustedScope) -> None:
        self._scope = scope
        self._events: list[AuditEvent] = []

    @property
    def events(self) -> tuple[AuditEvent, ...]:
        return tuple(self._events)

    @property
    def head(self) -> str:
        return self._events[-1].event_hash if self._events else ROOT_HASH

    def record(
        self,
        *,
        event_type: EventType,
        tool: str,
        code: DecisionCode,
        argument_sha256: str,
        approval: ApprovalGrant | None = None,
    ) -> AuditEvent:
        seed = AuditEvent(
            sequence=len(self._events) + 1,
            event_type=event_type,
            tenant_id=self._scope.tenant_id,
            principal_id=self._scope.principal_id,
            run_id=self._scope.run_id,
            case_id=self._scope.case_id,
            tool=tool,
            code=code,
            argument_sha256=argument_sha256,
            approval_id=approval.approval_id if approval else None,
            approved_by=approval.approved_by if approval else None,
            previous_hash=self.head,
            event_hash=ROOT_HASH,
        )
        event = seed.model_copy(
            update={"event_hash": _hash_event_body(_event_body(seed))}
        )
        self._events.append(event)
        return event

    @staticmethod
    def verify(events: tuple[AuditEvent, ...]) -> bool:
        previous = ROOT_HASH
        for expected_sequence, event in enumerate(events, start=1):
            if event.sequence != expected_sequence or event.previous_hash != previous:
                return False
            if _hash_event_body(_event_body(event)) != event.event_hash:
                return False
            previous = event.event_hash
        return True


class SandboxFailure(Exception):
    """Internal expected failure carrying only a controlled public code."""

    def __init__(self, code: DecisionCode) -> None:
        super().__init__(code)
        self.code = code


class ApprovalLedger:
    """Trusted in-memory fixture for issued and consumed human grants."""

    def __init__(self, grants: tuple[ApprovalGrant, ...] = ()) -> None:
        if len({grant.approval_id for grant in grants}) != len(grants):
            raise ValueError("duplicate_approval_id")
        self._grants = {grant.approval_id: grant for grant in grants}
        self._consumed: set[str] = set()

    def issue(self, grant: ApprovalGrant) -> None:
        """Issue from trusted host code; the gateway never gives this to an agent."""

        if grant.approval_id in self._grants:
            raise ValueError("duplicate_approval_id")
        self._grants[grant.approval_id] = grant

    def get(self, approval_id: str) -> ApprovalGrant | None:
        return self._grants.get(approval_id)

    def is_consumed(self, approval_id: str) -> bool:
        return approval_id in self._consumed

    def consume(self, approval_id: str) -> None:
        self._consumed.add(approval_id)


@dataclass(slots=True)
class UndoRecord:
    tenant_id: str
    flag_id: str
    before: str
    after: str
    used: bool = False


class InMemorySandbox:
    """A fixed local dispatcher with no network, shell or filesystem capability."""

    def __init__(self, *, fail_tools: frozenset[ToolName] = frozenset()) -> None:
        self._fail_tools = fail_tools
        self._contracts: dict[tuple[str, str], dict[str, JsonValue]] = {
            ("tenant-acme", "CTR-171"): {
                "contract_id": "CTR-171",
                "price_variance_limit": "0.10",
                "supplier_id": "SUP-171",
            },
            ("tenant-rival", "CTR-171"): {
                "contract_id": "CTR-171",
                "price_variance_limit": "0.05",
                "supplier_id": "SUP-900",
            },
        }
        self._orders: dict[tuple[str, str], dict[str, JsonValue]] = {
            ("tenant-acme", "PO-918"): {
                "order_id": "PO-918",
                "contract_id": "CTR-171",
                "supplier_id": "SUP-171",
                "price_variance": "0.18",
            }
        }
        self._risks: dict[tuple[str, str], dict[str, JsonValue]] = {
            ("tenant-acme", "SUP-171"): {
                "supplier_id": "SUP-171",
                "status": "watch",
                "open_incidents": 1,
            }
        }
        self._flags: dict[tuple[str, str], str] = {("tenant-acme", "FLAG-918"): "clear"}
        self._undo: dict[str, UndoRecord] = {}

    def flag_value(self, tenant_id: str, flag_id: str) -> str | None:
        """Expose controlled state for lab assertions, not as an agent tool."""

        return self._flags.get((tenant_id, flag_id))

    def dispatch(
        self,
        *,
        tenant_id: str,
        request_id: str,
        tool: ToolName,
        arguments: dict[str, str],
    ) -> tuple[dict[str, JsonValue], ActionReceipt | None]:
        if tool in self._fail_tools:
            raise RuntimeError("synthetic database DSN and internal stack details")
        if tool == "contract_lookup":
            return self._read(
                self._contracts, tenant_id, arguments["contract_id"]
            ), None
        if tool == "purchase_order_lookup":
            return self._read(self._orders, tenant_id, arguments["order_id"]), None
        if tool == "supplier_risk_lookup":
            return self._read(self._risks, tenant_id, arguments["supplier_id"]), None
        if tool == "review_flag_set":
            return self._set_flag(tenant_id, request_id, arguments)
        if tool == "review_flag_revert":
            return self._revert_flag(tenant_id, arguments["undo_token"]), None
        raise SandboxFailure("unknown_tool")

    @staticmethod
    def _read(
        table: dict[tuple[str, str], dict[str, JsonValue]],
        tenant_id: str,
        resource_id: str,
    ) -> dict[str, JsonValue]:
        record = table.get((tenant_id, resource_id))
        if record is None:
            raise SandboxFailure("data_not_found")
        return dict(record)

    def _set_flag(
        self,
        tenant_id: str,
        request_id: str,
        arguments: dict[str, str],
    ) -> tuple[dict[str, JsonValue], ActionReceipt]:
        flag_id = arguments["flag_id"]
        key = (tenant_id, flag_id)
        before = self._flags.get(key)
        if before is None:
            raise SandboxFailure("data_not_found")
        after = arguments["value"]
        action_seed = f"{tenant_id}:{request_id}:{flag_id}:{before}:{after}"
        action_digest = hashlib.sha256(action_seed.encode("utf-8")).hexdigest()
        action_id = f"act-{action_digest[:24]}"
        undo_token = f"undo-{action_digest[24:48]}"
        self._flags[key] = after
        self._undo[undo_token] = UndoRecord(
            tenant_id=tenant_id,
            flag_id=flag_id,
            before=before,
            after=after,
        )
        receipt = ActionReceipt(
            action_id=action_id,
            tool="review_flag_set",
            resource_id=flag_id,
            before=cast(LiteralFlag, before),
            after=cast(LiteralFlag, after),
            undo_token=undo_token,
        )
        return {"flag_id": flag_id, "value": after}, receipt

    def _revert_flag(self, tenant_id: str, undo_token: str) -> dict[str, JsonValue]:
        undo = self._undo.get(undo_token)
        if undo is None or undo.tenant_id != tenant_id:
            raise SandboxFailure("undo_not_found")
        if undo.used:
            raise SandboxFailure("undo_already_used")
        key = (tenant_id, undo.flag_id)
        if self._flags.get(key) != undo.after:
            raise SandboxFailure("undo_conflict")
        self._flags[key] = undo.before
        undo.used = True
        return {"flag_id": undo.flag_id, "value": undo.before}


LiteralFlag = Literal["clear", "needs_human"]


def _contains_secret_key(
    value: JsonValue,
    *,
    allowed_secret_keys: frozenset[str] = frozenset(),
) -> bool:
    if isinstance(value, dict):
        for key, nested in value.items():
            normalized = key.lower().replace("-", "_")
            looks_secret = any(part in normalized for part in SECRET_KEY_PARTS)
            if looks_secret and normalized not in allowed_secret_keys:
                return True
            if _contains_secret_key(nested, allowed_secret_keys=allowed_secret_keys):
                return True
    elif isinstance(value, list):
        return any(
            _contains_secret_key(item, allowed_secret_keys=allowed_secret_keys)
            for item in value
        )
    return False


def _validated_arguments(
    tool: ToolName,
    arguments: dict[str, JsonValue],
) -> dict[str, str] | None:
    policy = TOOL_POLICIES[tool]
    if set(arguments) != policy.argument_names:
        return None
    values: dict[str, str] = {}
    for name, value in arguments.items():
        if not isinstance(value, str) or not IDENTIFIER_PATTERN.fullmatch(value):
            return None
        values[name] = value
    if tool == "review_flag_set" and values["value"] not in {"clear", "needs_human"}:
        return None
    return values


class GuardedToolGateway:
    """Enforce authorization before the closed sandbox dispatcher can run."""

    def __init__(
        self,
        scope: TrustedScope,
        *,
        config: GatewayConfig = GatewayConfig(),
        approval_ledger: ApprovalLedger | None = None,
        sandbox: InMemorySandbox | None = None,
    ) -> None:
        self.scope = scope
        self.config = config
        self.sandbox = sandbox or InMemorySandbox()
        self.audit = HashChainedAuditTrail(scope)
        self.approval_ledger = approval_ledger or ApprovalLedger()
        self._steps = 0

    @property
    def steps(self) -> int:
        return self._steps

    def execute(self, request: ToolRequest) -> ToolResult:
        self._steps += 1
        digest = argument_digest(request.arguments)
        self.audit.record(
            event_type="requested",
            tool=request.tool,
            code="request_received",
            argument_sha256=digest,
        )
        if self._steps > self.config.max_steps:
            return self._blocked(
                request, digest, "step_limit_exceeded", event_type="step_limit"
            )
        declared_sensitive_keys = (
            frozenset({"undo_token"})
            if request.tool == "review_flag_revert"
            else frozenset()
        )
        if _contains_secret_key(
            request.arguments,
            allowed_secret_keys=declared_sensitive_keys,
        ):
            return self._blocked(request, digest, "secret_material_rejected")
        if request.tool not in TOOL_POLICIES:
            return self._blocked(request, digest, "unknown_tool")

        tool = request.tool
        arguments = _validated_arguments(tool, request.arguments)
        if arguments is None:
            return self._blocked(request, digest, "invalid_arguments")
        policy = TOOL_POLICIES[tool]
        if policy.permission not in self.scope.permissions:
            return self._blocked(request, digest, "permission_denied")

        approval: ApprovalGrant | None = None
        if policy.mode == "write":
            approval, failure = self._check_approval(request, digest)
            if failure is not None:
                return self._blocked(request, digest, failure)
            assert approval is not None
            self.approval_ledger.consume(approval.approval_id)
            self.audit.record(
                event_type="approval_checked",
                tool=request.tool,
                code="approval_valid",
                argument_sha256=digest,
                approval=approval,
            )

        try:
            data, receipt = self.sandbox.dispatch(
                tenant_id=self.scope.tenant_id,
                request_id=request.request_id,
                tool=tool,
                arguments=arguments,
            )
        except SandboxFailure as error:
            return self._failed(request, digest, error.code, approval)
        except Exception:
            return self._failed(request, digest, "tool_failure", approval)

        event_type: EventType = (
            "reversed" if tool == "review_flag_revert" else "executed"
        )
        self.audit.record(
            event_type=event_type,
            tool=request.tool,
            code="ok",
            argument_sha256=digest,
            approval=approval,
        )
        return ToolResult(
            request_id=request.request_id,
            tool=request.tool,
            step=self._steps,
            status="completed",
            code="ok",
            data=data,
            receipt=receipt,
            audit_head=self.audit.head,
        )

    def _check_approval(
        self,
        request: ToolRequest,
        digest: str,
    ) -> tuple[ApprovalGrant | None, DecisionCode | None]:
        if request.approval_id is None:
            return None, "approval_required"
        approval = self.approval_ledger.get(request.approval_id)
        if approval is None:
            return None, "approval_not_found"
        if self.approval_ledger.is_consumed(approval.approval_id):
            return None, "approval_reused"
        expected = (
            self.scope.tenant_id,
            self.scope.principal_id,
            self.scope.run_id,
            self.scope.case_id,
            request.request_id,
            request.tool,
            digest,
        )
        actual = (
            approval.tenant_id,
            approval.principal_id,
            approval.run_id,
            approval.case_id,
            approval.request_id,
            approval.tool,
            approval.argument_sha256,
        )
        if actual != expected:
            return None, "approval_mismatch"
        return approval, None

    def _blocked(
        self,
        request: ToolRequest,
        digest: str,
        code: DecisionCode,
        *,
        event_type: EventType = "denied",
    ) -> ToolResult:
        self.audit.record(
            event_type=event_type,
            tool=request.tool,
            code=code,
            argument_sha256=digest,
        )
        return ToolResult(
            request_id=request.request_id,
            tool=request.tool,
            step=self._steps,
            status="blocked",
            code=code,
            data={},
            receipt=None,
            audit_head=self.audit.head,
        )

    def _failed(
        self,
        request: ToolRequest,
        digest: str,
        code: DecisionCode,
        approval: ApprovalGrant | None,
    ) -> ToolResult:
        self.audit.record(
            event_type="failed",
            tool=request.tool,
            code=code,
            argument_sha256=digest,
            approval=approval,
        )
        return ToolResult(
            request_id=request.request_id,
            tool=request.tool,
            step=self._steps,
            status="failed",
            code=code,
            data={},
            receipt=None,
            audit_head=self.audit.head,
        )
