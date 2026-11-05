"""Run the deterministic Week 19 guardrail scenarios and smoke checks."""

from __future__ import annotations

import argparse
import json
from typing import Literal, TypedDict, cast

from labs.week_19.models import GatewayConfig, ToolRequest, ToolResult, TrustedScope
from labs.week_19.safety import (
    ApprovalLedger,
    GuardedToolGateway,
    HashChainedAuditTrail,
    InMemorySandbox,
    build_approval,
)


Scenario = Literal[
    "read",
    "write-without-approval",
    "approved-write",
    "reversal",
    "secret-rejected",
    "max-steps",
    "tool-failure",
]
SCENARIOS: tuple[Scenario, ...] = (
    "read",
    "write-without-approval",
    "approved-write",
    "reversal",
    "secret-rejected",
    "max-steps",
    "tool-failure",
)


class ScenarioPayload(TypedDict):
    audit: list[dict[str, object]]
    audit_chain_valid: bool
    results: list[dict[str, object]]
    scenario: Scenario


def _scope(*permissions: str) -> TrustedScope:
    return TrustedScope.model_validate(
        {
            "tenant_id": "tenant-acme",
            "principal_id": "agent-procurement-v1",
            "run_id": "run-week19",
            "case_id": "price-spike",
            "permissions": permissions,
        }
    )


def _read_request(request_id: str = "read-contract") -> ToolRequest:
    return ToolRequest(
        request_id=request_id,
        tool="contract_lookup",
        arguments={"contract_id": "CTR-171"},
    )


def _write_request(request_id: str = "set-review") -> ToolRequest:
    return ToolRequest(
        request_id=request_id,
        tool="review_flag_set",
        arguments={"flag_id": "FLAG-918", "value": "needs_human"},
    )


def run_scenario(name: Scenario) -> ScenarioPayload:
    """Run one documented scenario and return a JSON-safe projection."""

    results: tuple[ToolResult, ...]
    if name == "read":
        gateway = GuardedToolGateway(_scope("contract:read"))
        results = (gateway.execute(_read_request()),)
    elif name == "write-without-approval":
        gateway = GuardedToolGateway(_scope("review_flag:write"))
        results = (gateway.execute(_write_request()),)
    elif name == "approved-write":
        scope = _scope("review_flag:write")
        base = _write_request()
        grant = build_approval(
            scope, base, approval_id="approval-set", approved_by="reviewer-42"
        )
        gateway = GuardedToolGateway(scope, approval_ledger=ApprovalLedger((grant,)))
        results = (
            gateway.execute(base.model_copy(update={"approval_id": grant.approval_id})),
        )
    elif name == "reversal":
        scope = _scope("review_flag:write", "review_flag:revert")
        ledger = ApprovalLedger()
        gateway = GuardedToolGateway(scope, approval_ledger=ledger)
        base = _write_request()
        write_grant = build_approval(
            scope, base, approval_id="approval-set", approved_by="reviewer-42"
        )
        ledger.issue(write_grant)
        written = gateway.execute(
            base.model_copy(update={"approval_id": write_grant.approval_id})
        )
        assert written.receipt is not None
        reverse = ToolRequest(
            request_id="revert-review",
            tool="review_flag_revert",
            arguments={"undo_token": written.receipt.undo_token},
        )
        reverse_grant = build_approval(
            scope, reverse, approval_id="approval-revert", approved_by="reviewer-43"
        )
        ledger.issue(reverse_grant)
        reverted = gateway.execute(
            reverse.model_copy(update={"approval_id": reverse_grant.approval_id})
        )
        results = (written, reverted)
    elif name == "secret-rejected":
        gateway = GuardedToolGateway(_scope("contract:read"))
        request = ToolRequest(
            request_id="secret-attempt",
            tool="contract_lookup",
            arguments={"contract_id": "CTR-171", "api_key": "do-not-log-me"},
        )
        results = (gateway.execute(request),)
    elif name == "max-steps":
        gateway = GuardedToolGateway(
            _scope("contract:read"), config=GatewayConfig(max_steps=2)
        )
        results = tuple(
            gateway.execute(_read_request(f"read-{number}")) for number in range(1, 4)
        )
    else:
        sandbox = InMemorySandbox(fail_tools=frozenset({"contract_lookup"}))
        gateway = GuardedToolGateway(_scope("contract:read"), sandbox=sandbox)
        results = (gateway.execute(_read_request()),)

    return {
        "audit": [event.model_dump(mode="json") for event in gateway.audit.events],
        "audit_chain_valid": HashChainedAuditTrail.verify(gateway.audit.events),
        "results": [result.model_dump(mode="json") for result in results],
        "scenario": name,
    }


def _smoke() -> dict[str, object]:
    checks = 0
    read = run_scenario("read")
    assert read["results"][0]["status"] == "completed"
    checks += 1
    no_approval = run_scenario("write-without-approval")
    assert no_approval["results"][0]["code"] == "approval_required"
    checks += 1
    approved = run_scenario("approved-write")
    receipt = cast(dict[str, object], approved["results"][0]["receipt"])
    assert receipt["before"] == "clear"
    checks += 1
    reversed_action = run_scenario("reversal")
    assert [row["code"] for row in reversed_action["results"]] == ["ok", "ok"]
    checks += 1
    secret = run_scenario("secret-rejected")
    assert secret["results"][0]["code"] == "secret_material_rejected"
    checks += 1
    assert "do-not-log-me" not in json.dumps(secret["audit"], sort_keys=True)
    checks += 1
    bounded = run_scenario("max-steps")
    assert bounded["results"][2]["code"] == "step_limit_exceeded"
    checks += 1
    failure = run_scenario("tool-failure")
    assert failure["results"][0]["code"] == "tool_failure"
    checks += 1
    assert "database" not in json.dumps(failure, sort_keys=True)
    checks += 1
    assert all(
        bool(run_scenario(scenario)["audit_chain_valid"]) for scenario in SCENARIOS
    )
    checks += 1
    assert run_scenario("reversal") == run_scenario("reversal")
    checks += 1
    assert len(SCENARIOS) == 7
    checks += 1
    return {"checks": checks, "scenarios": len(SCENARIOS), "status": "ok"}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("case", "smoke"))
    parser.add_argument("--scenario", choices=SCENARIOS, default="reversal")
    return parser


def main() -> None:
    args = _parser().parse_args()
    payload = _smoke() if args.command == "smoke" else run_scenario(args.scenario)
    print(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
