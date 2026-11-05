"""Contract and behavior checks for the Week 19 agent-safety lab."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import cast

from pydantic import ValidationError
import pytest

from labs.week_19.models import (
    GatewayConfig,
    ToolRequest,
    TrustedScope,
)
from labs.week_19.safety import (
    ApprovalLedger,
    GuardedToolGateway,
    HashChainedAuditTrail,
    InMemorySandbox,
    argument_digest,
    build_approval,
)


ROOT = Path(__file__).resolve().parents[1]


def _scope(*permissions: str, tenant_id: str = "tenant-acme") -> TrustedScope:
    return TrustedScope.model_validate(
        {
            "tenant_id": tenant_id,
            "principal_id": "agent-procurement-v1",
            "run_id": "run-19",
            "case_id": "case-price-spike",
            "permissions": permissions,
        }
    )


def _read(request_id: str = "read-1") -> ToolRequest:
    return ToolRequest(
        request_id=request_id,
        tool="contract_lookup",
        arguments={"contract_id": "CTR-171"},
    )


def _write(request_id: str = "write-1", value: str = "needs_human") -> ToolRequest:
    return ToolRequest(
        request_id=request_id,
        tool="review_flag_set",
        arguments={"flag_id": "FLAG-918", "value": value},
    )


def _approved_gateway(
    scope: TrustedScope,
    request: ToolRequest,
    *,
    sandbox: InMemorySandbox | None = None,
    approval_id: str = "approval-1",
) -> tuple[GuardedToolGateway, ToolRequest, ApprovalLedger]:
    grant = build_approval(
        scope, request, approval_id=approval_id, approved_by="reviewer-42"
    )
    ledger = ApprovalLedger((grant,))
    gateway = GuardedToolGateway(
        scope,
        approval_ledger=ledger,
        sandbox=sandbox,
    )
    approved = request.model_copy(update={"approval_id": grant.approval_id})
    return gateway, approved, ledger


def test_boundaries_are_strict_closed_frozen_and_authority_is_not_a_request_field() -> (
    None
):
    scope = _scope("contract:read")
    request = _read()
    with pytest.raises(ValidationError):
        ToolRequest.model_validate(
            {**request.model_dump(), "permissions": ["review_flag:write"]}
        )
    with pytest.raises(ValidationError):
        ToolRequest.model_validate({**request.model_dump(), "request_id": 19})
    with pytest.raises(ValidationError):
        request.tool = "review_flag_set"
    with pytest.raises(ValidationError):
        TrustedScope.model_validate(
            {**scope.model_dump(), "permissions": ["contract:read", "contract:read"]}
        )


def test_gateway_configuration_rejects_zero_and_unbounded_step_budgets() -> None:
    with pytest.raises(ValidationError):
        GatewayConfig(max_steps=0)
    with pytest.raises(ValidationError):
        GatewayConfig(max_steps=21)


def test_authorized_read_completes_and_records_a_minimal_valid_chain() -> None:
    gateway = GuardedToolGateway(_scope("contract:read"))
    result = gateway.execute(_read())
    assert result.status == "completed"
    assert result.code == "ok"
    assert result.data == {
        "contract_id": "CTR-171",
        "price_variance_limit": "0.10",
        "supplier_id": "SUP-171",
    }
    assert [event.event_type for event in gateway.audit.events] == [
        "requested",
        "executed",
    ]
    assert HashChainedAuditTrail.verify(gateway.audit.events)
    assert "CTR-171" not in json.dumps(
        [event.model_dump(mode="json") for event in gateway.audit.events]
    )


def test_trusted_tenant_scope_prevents_cross_tenant_record_access() -> None:
    acme = GuardedToolGateway(_scope("contract:read"))
    rival = GuardedToolGateway(_scope("contract:read", tenant_id="tenant-rival"))
    assert acme.execute(_read()).data["supplier_id"] == "SUP-171"
    assert rival.execute(_read()).data["supplier_id"] == "SUP-900"


def test_missing_permission_blocks_before_sandbox_execution() -> None:
    sandbox = InMemorySandbox(fail_tools=frozenset({"contract_lookup"}))
    result = GuardedToolGateway(_scope(), sandbox=sandbox).execute(_read())
    assert result.status == "blocked"
    assert result.code == "permission_denied"
    assert result.data == {}


def test_unknown_tool_fails_closed() -> None:
    request = ToolRequest(
        request_id="unknown-1",
        tool="shell_exec",
        arguments={"command": "whoami"},
    )
    result = GuardedToolGateway(_scope()).execute(request)
    assert result.status == "blocked"
    assert result.code == "unknown_tool"


@pytest.mark.parametrize(
    "arguments",
    [
        {},
        {"contract_id": "CTR-171", "extra": "value"},
        {"contract_id": 171},
        {"contract_id": "space is invalid"},
    ],
)
def test_tool_arguments_require_exact_names_and_strict_values(
    arguments: dict[str, object],
) -> None:
    request = ToolRequest.model_validate(
        {
            "request_id": "bad-arguments",
            "tool": "contract_lookup",
            "arguments": arguments,
        }
    )
    result = GuardedToolGateway(_scope("contract:read")).execute(request)
    assert result.status == "blocked"
    assert result.code == "invalid_arguments"


def test_secret_like_keys_are_rejected_recursively_and_values_never_reach_audit() -> (
    None
):
    for number, key in enumerate(
        (
            "api_key",
            "authorization_header",
            "client_credentials",
            "db_password",
            "shared_secret",
            "access_token",
        ),
        start=1,
    ):
        request = ToolRequest(
            request_id=f"secret-{number}",
            tool="contract_lookup",
            arguments={
                "contract_id": "CTR-171",
                "metadata": {key: "extremely-sensitive"},
            },
        )
        gateway = GuardedToolGateway(_scope("contract:read"))
        result = gateway.execute(request)
        audit_json = json.dumps(
            [event.model_dump(mode="json") for event in gateway.audit.events],
            sort_keys=True,
        )
        assert result.code == "secret_material_rejected"
        assert "extremely-sensitive" not in audit_json
        assert key not in audit_json


def test_write_without_human_approval_does_not_mutate_state() -> None:
    sandbox = InMemorySandbox()
    result = GuardedToolGateway(_scope("review_flag:write"), sandbox=sandbox).execute(
        _write()
    )
    assert result.status == "blocked"
    assert result.code == "approval_required"
    assert sandbox.flag_value("tenant-acme", "FLAG-918") == "clear"


def test_exact_human_approval_executes_write_and_returns_reversal_receipt() -> None:
    scope = _scope("review_flag:write")
    sandbox = InMemorySandbox()
    gateway, request, _ = _approved_gateway(scope, _write(), sandbox=sandbox)
    result = gateway.execute(request)
    assert result.status == "completed"
    assert result.receipt is not None
    assert result.receipt.before == "clear"
    assert result.receipt.after == "needs_human"
    assert result.receipt.undo_token.startswith("undo-")
    assert sandbox.flag_value("tenant-acme", "FLAG-918") == "needs_human"
    assert [event.event_type for event in gateway.audit.events] == [
        "requested",
        "approval_checked",
        "executed",
    ]


@pytest.mark.parametrize(
    ("field", "wrong_value"),
    [
        ("tenant_id", "tenant-rival"),
        ("principal_id", "another-agent"),
        ("run_id", "another-run"),
        ("case_id", "another-case"),
        ("request_id", "another-request"),
        ("tool", "review_flag_revert"),
        ("argument_sha256", "f" * 64),
    ],
)
def test_approval_must_match_every_bound_action_field(
    field: str,
    wrong_value: str,
) -> None:
    scope = _scope("review_flag:write")
    base = _write()
    grant = build_approval(
        scope, base, approval_id="approval-exact", approved_by="reviewer-42"
    )
    mismatched = grant.model_copy(update={field: wrong_value})
    sandbox = InMemorySandbox()
    gateway = GuardedToolGateway(
        scope,
        approval_ledger=ApprovalLedger((mismatched,)),
        sandbox=sandbox,
    )
    result = gateway.execute(
        base.model_copy(update={"approval_id": mismatched.approval_id})
    )
    assert result.code == "approval_mismatch"
    assert sandbox.flag_value("tenant-acme", "FLAG-918") == "clear"


def test_unknown_and_reused_approval_ids_fail_closed() -> None:
    scope = _scope("review_flag:write")
    missing = _write().model_copy(update={"approval_id": "not-issued"})
    assert GuardedToolGateway(scope).execute(missing).code == "approval_not_found"

    gateway, approved, _ = _approved_gateway(scope, _write())
    assert gateway.execute(approved).code == "ok"
    assert gateway.execute(approved).code == "approval_reused"


def test_maximum_steps_stop_before_a_third_dispatch() -> None:
    sandbox = InMemorySandbox()
    gateway = GuardedToolGateway(
        _scope("contract:read"),
        config=GatewayConfig(max_steps=2),
        sandbox=sandbox,
    )
    assert gateway.execute(_read("read-1")).code == "ok"
    assert gateway.execute(_read("read-2")).code == "ok"
    stopped = gateway.execute(_read("read-3"))
    assert stopped.status == "blocked"
    assert stopped.code == "step_limit_exceeded"
    assert gateway.audit.events[-1].event_type == "step_limit"


def test_unexpected_tool_failure_is_sanitized_and_still_audited() -> None:
    sandbox = InMemorySandbox(fail_tools=frozenset({"contract_lookup"}))
    gateway = GuardedToolGateway(_scope("contract:read"), sandbox=sandbox)
    result = gateway.execute(_read())
    serialized = json.dumps(result.model_dump(mode="json"), sort_keys=True)
    audit_json = json.dumps(
        [event.model_dump(mode="json") for event in gateway.audit.events],
        sort_keys=True,
    )
    assert result.status == "failed"
    assert result.code == "tool_failure"
    assert "database" not in serialized + audit_json
    assert "DSN" not in serialized + audit_json
    assert HashChainedAuditTrail.verify(gateway.audit.events)


def test_hash_chain_detects_event_mutation_and_reordering() -> None:
    gateway = GuardedToolGateway(_scope("contract:read"))
    gateway.execute(_read())
    events = gateway.audit.events
    tampered = events[0].model_copy(update={"tool": "purchase_order_lookup"})
    assert not HashChainedAuditTrail.verify((tampered, events[1]))
    assert not HashChainedAuditTrail.verify(tuple(reversed(events)))


def test_approved_reversal_restores_state_and_token_is_one_time() -> None:
    scope = _scope("review_flag:write", "review_flag:revert")
    sandbox = InMemorySandbox()
    gateway, approved, ledger = _approved_gateway(scope, _write(), sandbox=sandbox)
    written = gateway.execute(approved)
    assert written.receipt is not None

    reverse = ToolRequest(
        request_id="reverse-1",
        tool="review_flag_revert",
        arguments={"undo_token": written.receipt.undo_token},
    )
    reverse_grant = build_approval(
        scope, reverse, approval_id="approval-reverse-1", approved_by="reviewer-43"
    )
    ledger.issue(reverse_grant)
    reverted = gateway.execute(
        reverse.model_copy(update={"approval_id": reverse_grant.approval_id})
    )
    assert reverted.code == "ok"
    assert sandbox.flag_value("tenant-acme", "FLAG-918") == "clear"

    second_reverse = reverse.model_copy(update={"request_id": "reverse-2"})
    second_grant = build_approval(
        scope,
        second_reverse,
        approval_id="approval-reverse-2",
        approved_by="reviewer-44",
    )
    ledger.issue(second_grant)
    repeated = gateway.execute(
        second_reverse.model_copy(update={"approval_id": second_grant.approval_id})
    )
    assert repeated.status == "failed"
    assert repeated.code == "undo_already_used"


def test_reversal_token_is_tenant_scoped() -> None:
    acme_scope = _scope("review_flag:write")
    sandbox = InMemorySandbox()
    gateway, approved, _ = _approved_gateway(acme_scope, _write(), sandbox=sandbox)
    written = gateway.execute(approved)
    assert written.receipt is not None

    rival_scope = _scope("review_flag:revert", tenant_id="tenant-rival")
    reverse = ToolRequest(
        request_id="rival-reverse",
        tool="review_flag_revert",
        arguments={"undo_token": written.receipt.undo_token},
    )
    rival, approved_reverse, _ = _approved_gateway(
        rival_scope,
        reverse,
        sandbox=sandbox,
        approval_id="rival-approval",
    )
    assert rival.execute(approved_reverse).code == "undo_not_found"
    assert sandbox.flag_value("tenant-acme", "FLAG-918") == "needs_human"


def test_reversal_refuses_to_overwrite_a_newer_value() -> None:
    scope = _scope("review_flag:write", "review_flag:revert")
    sandbox = InMemorySandbox()
    ledger = ApprovalLedger()
    gateway = GuardedToolGateway(scope, approval_ledger=ledger, sandbox=sandbox)

    first = _write("write-first")
    first_grant = build_approval(
        scope, first, approval_id="approval-first", approved_by="reviewer-1"
    )
    ledger.issue(first_grant)
    first_result = gateway.execute(
        first.model_copy(update={"approval_id": first_grant.approval_id})
    )
    assert first_result.receipt is not None

    newer = _write("write-newer", value="clear")
    newer_grant = build_approval(
        scope, newer, approval_id="approval-newer", approved_by="reviewer-2"
    )
    ledger.issue(newer_grant)
    assert (
        gateway.execute(
            newer.model_copy(update={"approval_id": newer_grant.approval_id})
        ).code
        == "ok"
    )

    reverse = ToolRequest(
        request_id="reverse-stale",
        tool="review_flag_revert",
        arguments={"undo_token": first_result.receipt.undo_token},
    )
    reverse_grant = build_approval(
        scope, reverse, approval_id="approval-stale", approved_by="reviewer-3"
    )
    ledger.issue(reverse_grant)
    result = gateway.execute(
        reverse.model_copy(update={"approval_id": reverse_grant.approval_id})
    )
    assert result.code == "undo_conflict"
    assert sandbox.flag_value("tenant-acme", "FLAG-918") == "clear"


def test_argument_digest_and_full_scenario_replay_are_deterministic() -> None:
    assert argument_digest({"b": "2", "a": "1"}) == argument_digest(
        {"a": "1", "b": "2"}
    )
    scope = _scope("review_flag:write")
    request = _write()
    first, approved_first, _ = _approved_gateway(scope, request)
    second, approved_second, _ = _approved_gateway(scope, request)
    assert first.execute(approved_first) == second.execute(approved_second)
    assert first.audit.events == second.audit.events


def test_cli_scenarios_and_smoke_are_machine_readable() -> None:
    case = subprocess.run(
        [
            sys.executable,
            "-m",
            "labs.week_19.demo",
            "case",
            "--scenario",
            "reversal",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    case_payload = cast(dict[str, object], json.loads(case.stdout))
    assert case_payload["scenario"] == "reversal"
    assert case_payload["audit_chain_valid"] is True

    smoke = subprocess.run(
        [sys.executable, "-m", "labs.week_19.demo", "smoke"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(smoke.stdout) == {
        "checks": 12,
        "scenarios": 7,
        "status": "ok",
    }
