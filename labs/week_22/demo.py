"""Inspect and exercise the Week 22 MCP server without a network dependency."""

from __future__ import annotations

import argparse
import asyncio
import json
from typing import Any, cast

from mcp.server import MCPServer
from mcp.types import CallToolResult, GetPromptResult, InputRequiredResult

from labs.week_22.models import Principal
from labs.week_22.server import create_server


def _principal(*, authorized: bool = True) -> Principal:
    scopes = ("supplier:read",) if authorized else ()
    return Principal(
        actor_id="learner-1",
        tenant_id="tenant-acme",
        scopes=scopes,
    )


async def _describe(server: MCPServer) -> dict[str, object]:
    tools = await server.list_tools()
    resources = await server.list_resources()
    prompts = await server.list_prompts()
    return {
        "prompts": [prompt.name for prompt in prompts],
        "resources": [str(resource.uri) for resource in resources],
        "tools": [tool.name for tool in tools],
    }


async def _call(server: MCPServer, supplier_id: str) -> dict[str, Any]:
    result = await server.call_tool("supplier_lookup", {"supplier_id": supplier_id})
    if not isinstance(result, CallToolResult):
        raise RuntimeError("unexpected_elicitation_request")
    assert result.structured_content is not None
    return cast(dict[str, Any], result.structured_content)


async def _smoke() -> dict[str, object]:
    checks = 0
    server = create_server(_principal())
    capabilities = await _describe(server)
    assert capabilities["tools"] == ["supplier_lookup"]
    assert capabilities["resources"] == ["procurement://policy/supplier-lookup"]
    assert capabilities["prompts"] == ["supplier_review"]
    checks += 3

    found = await _call(server, "supplier-101")
    assert found["status"] == "found"
    assert found["supplier"]["risk"] == "low"
    checks += 2

    hidden = await _call(server, "supplier-909")
    absent = await _call(server, "supplier-does-not-exist")
    assert hidden == absent
    checks += 1

    denied = await _call(create_server(_principal(authorized=False)), "supplier-101")
    assert denied["status"] == "forbidden"
    assert denied["supplier"] is None
    checks += 2

    contents = await server.read_resource("procurement://policy/supplier-lookup")
    assert not isinstance(contents, InputRequiredResult)
    resource_contents = tuple(contents)
    assert resource_contents[0].mime_type == "text/markdown"
    assert "cannot choose a tenant" in resource_contents[0].content
    checks += 2

    prompt = await server.get_prompt("supplier_review", {"supplier_id": "supplier-101"})
    assert isinstance(prompt, GetPromptResult)
    prompt_text = prompt.messages[0].content
    assert getattr(prompt_text, "text", "").startswith("Use supplier_lookup")
    checks += 1
    return {"checks": checks, "status": "ok"}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("describe", "call", "smoke", "serve"))
    parser.add_argument("--supplier-id", default="supplier-101")
    return parser


def main() -> None:
    args = _parser().parse_args()
    server = create_server(_principal())
    if args.command == "serve":
        server.run("stdio")
        return
    if args.command == "describe":
        payload: object = asyncio.run(_describe(server))
    elif args.command == "call":
        payload = asyncio.run(_call(server, args.supplier_id))
    else:
        payload = asyncio.run(_smoke())
    print(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
