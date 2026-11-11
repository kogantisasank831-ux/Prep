"""Week 22 MCP capability, authorization and isolation contracts."""

from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from collections.abc import Coroutine
from typing import Any, TypeVar

import pytest
from mcp.types import CallToolResult, GetPromptResult, InputRequiredResult
from pydantic import ValidationError

from labs.week_22.catalog import SupplierCatalog
from labs.week_22.models import Principal, SupplierLookupResult
from labs.week_22.server import create_server


T = TypeVar("T")


def _run(awaitable: Coroutine[Any, Any, T]) -> T:
    return asyncio.run(awaitable)


def _principal(
    *, tenant_id: str = "tenant-acme", scopes: tuple[str, ...] = ("supplier:read",)
) -> Principal:
    return Principal(
        actor_id="tester-1",
        tenant_id=tenant_id,
        scopes=scopes,
    )


def test_principal_is_strict_frozen_and_closed() -> None:
    with pytest.raises(ValidationError):
        Principal.model_validate(
            {"actor_id": 1, "tenant_id": "tenant-acme", "scopes": ()}
        )
    with pytest.raises(ValidationError):
        Principal.model_validate(
            {
                "actor_id": "tester-1",
                "tenant_id": "tenant-acme",
                "scopes": (),
                "admin": True,
            }
        )
    principal = _principal()
    with pytest.raises(ValidationError):
        principal.tenant_id = "tenant-bravo"


def test_lookup_result_requires_status_and_record_to_agree() -> None:
    with pytest.raises(ValidationError, match="found_result_requires_supplier"):
        SupplierLookupResult(status="found", supplier=None, message="Invalid fixture.")


def test_catalog_returns_visible_supplier() -> None:
    result = SupplierCatalog().lookup(_principal(), "supplier-101")
    assert result.status == "found"
    assert result.supplier is not None
    assert result.supplier.display_name == "Northwind Components"


def test_catalog_requires_read_scope() -> None:
    result = SupplierCatalog().lookup(_principal(scopes=()), "supplier-101")
    assert result.status == "forbidden"
    assert result.supplier is None


def test_cross_tenant_and_unknown_identifiers_are_indistinguishable() -> None:
    catalog = SupplierCatalog()
    hidden = catalog.lookup(_principal(), "supplier-909")
    absent = catalog.lookup(_principal(), "supplier-does-not-exist")
    assert hidden == absent
    assert "bravo" not in hidden.message.lower()


def test_tenant_bravo_can_see_only_its_record() -> None:
    catalog = SupplierCatalog()
    visible = catalog.lookup(_principal(tenant_id="tenant-bravo"), "supplier-909")
    hidden = catalog.lookup(_principal(tenant_id="tenant-bravo"), "supplier-101")
    assert visible.status == "found"
    assert hidden.status == "not_found"


def test_server_discovers_exact_capability_set() -> None:
    server = create_server(_principal())
    tools = _run(server.list_tools())
    resources = _run(server.list_resources())
    prompts = _run(server.list_prompts())
    assert [tool.name for tool in tools] == ["supplier_lookup"]
    assert [str(resource.uri) for resource in resources] == [
        "procurement://policy/supplier-lookup"
    ]
    assert [prompt.name for prompt in prompts] == ["supplier_review"]


def test_tool_declares_schema_and_safety_hints() -> None:
    tool = _run(create_server(_principal()).list_tools())[0]
    assert set(tool.input_schema["properties"]) == {"supplier_id"}
    assert tool.output_schema is not None
    assert tool.output_schema["additionalProperties"] is False
    assert tool.annotations is not None
    assert tool.annotations.read_only_hint is True
    assert tool.annotations.destructive_hint is False
    assert tool.annotations.idempotent_hint is True
    assert tool.annotations.open_world_hint is False


def test_tool_returns_structured_tenant_scoped_output() -> None:
    result = _run(
        create_server(_principal()).call_tool(
            "supplier_lookup", {"supplier_id": "supplier-202"}
        )
    )
    assert isinstance(result, CallToolResult)
    assert result.is_error is False
    assert result.structured_content is not None
    assert result.structured_content["status"] == "found"
    assert result.structured_content["supplier"]["risk"] == "medium"


def test_tool_cannot_be_redirected_by_model_supplied_tenant_argument() -> None:
    result = _run(
        create_server(_principal()).call_tool(
            "supplier_lookup",
            {"supplier_id": "supplier-909", "tenant_id": "tenant-bravo"},
        )
    )
    assert isinstance(result, CallToolResult)
    assert result.structured_content is not None
    assert result.structured_content["status"] == "not_found"
    assert result.structured_content["supplier"] is None


def test_tool_enforces_scope_at_invocation() -> None:
    result = _run(
        create_server(_principal(scopes=())).call_tool(
            "supplier_lookup", {"supplier_id": "supplier-101"}
        )
    )
    assert isinstance(result, CallToolResult)
    assert result.structured_content is not None
    assert result.structured_content["status"] == "forbidden"
    assert result.structured_content["supplier"] is None


def test_policy_resource_contains_no_catalog_records() -> None:
    server = create_server(_principal())
    contents = _run(server.read_resource("procurement://policy/supplier-lookup"))
    assert not isinstance(contents, InputRequiredResult)
    resource_contents = tuple(contents)
    assert len(resource_contents) == 1
    assert resource_contents[0].mime_type == "text/markdown"
    assert "cannot choose a tenant" in resource_contents[0].content
    assert "Northwind" not in resource_contents[0].content


def test_prompt_is_bounded_and_contains_no_supplier_data() -> None:
    prompt = _run(
        create_server(_principal()).get_prompt(
            "supplier_review", {"supplier_id": "supplier-101"}
        )
    )
    assert isinstance(prompt, GetPromptResult)
    assert len(prompt.messages) == 1
    text = getattr(prompt.messages[0].content, "text", "")
    assert "supplier_lookup" in text
    assert "Do not perform any write" in text
    assert "Northwind" not in text


@pytest.mark.parametrize("command", ["describe", "call", "smoke"])
def test_non_blocking_cli_commands(command: str) -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "labs.week_22.demo", command],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    if command == "describe":
        assert payload["tools"] == ["supplier_lookup"]
    elif command == "call":
        assert payload["status"] == "found"
    else:
        assert payload == {"checks": 11, "status": "ok"}
