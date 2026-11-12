"""Create a modern, tenant-scoped MCP server with three capability types."""

from __future__ import annotations

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from labs.week_22.catalog import SupplierCatalog
from labs.week_22.models import Principal, SupplierLookupResult


POLICY_TEXT = """# Supplier lookup policy

- The transport authenticates the caller before constructing the server.
- The tool derives tenant and actor context from that authenticated principal.
- Callers supply only a supplier identifier; they cannot choose a tenant.
- `supplier:read` is required for every invocation.
- Missing and cross-tenant identifiers return the same `not_found` response.
- This teaching server is read-only and uses synthetic records.
"""


def create_server(
    principal: Principal, catalog: SupplierCatalog | None = None
) -> MCPServer:
    """Bind trusted identity once, then expose a least-privilege capability set."""

    supplier_catalog = catalog or SupplierCatalog()
    server = MCPServer(
        "prep-week22-supplier-server",
        instructions=(
            "Read-only synthetic supplier lookup. Never infer a tenant from tool input."
        ),
    )

    @server.tool(
        name="supplier_lookup",
        description=(
            "Look up one supplier visible to the authenticated tenant. "
            "The caller cannot select a tenant."
        ),
        annotations=ToolAnnotations(
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
        structured_output=True,
    )
    def supplier_lookup(supplier_id: str) -> SupplierLookupResult:
        """Return a scoped synthetic supplier view."""

        return supplier_catalog.lookup(principal, supplier_id)

    @server.resource(
        "procurement://policy/supplier-lookup",
        name="supplier-lookup-policy",
        title="Supplier lookup authorization policy",
        description="Static, non-secret rules governing the supplier tool.",
        mime_type="text/markdown",
    )
    def supplier_lookup_policy() -> str:
        """Expose the stable policy as application-controlled context."""

        return POLICY_TEXT

    @server.prompt(
        name="supplier_review",
        title="Review a visible supplier",
        description="Prepare a bounded read-only supplier review.",
    )
    def supplier_review(supplier_id: str) -> str:
        """Return a user-selected prompt without embedding supplier data."""

        return (
            f"Use supplier_lookup for {supplier_id}. Summarize only the returned "
            "status and risk. If access is forbidden or the supplier is not found, "
            "say so without guessing. Do not perform any write or external action."
        )

    return server
