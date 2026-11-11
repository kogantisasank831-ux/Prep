# Week 22: expose interoperable capabilities without delegating identity

This lab creates a small MCP server with one read-only supplier tool, one static
policy resource and one review prompt. It binds an authenticated principal at
server construction, filters every lookup by tenant and returns the same
`not_found` response for missing and cross-tenant identifiers.

The records are synthetic. No remote service, model, token, secret or database
is used.

## Run it

From the repository root in the pinned development environment:

```shell
python -m pip install -r requirements-dev.txt
python -m labs.week_22.demo describe
python -m labs.week_22.demo call --supplier-id supplier-101
python -m labs.week_22.demo smoke
```

To connect a local MCP client over standard input/output, run:

```shell
python -m labs.week_22.demo serve
```

The stdio path is intentionally not exercised by CI. The deterministic tests
call the same registered capabilities in-process.

## Capability ownership

| Capability | Who normally selects it | Lab example |
| --- | --- | --- |
| Tool | Model, subject to client/user policy | `supplier_lookup` |
| Resource | Application | `procurement://policy/supplier-lookup` |
| Prompt | User | `supplier_review` |

Discovery is not authorization. The tool annotation says that lookup is
read-only, non-destructive, idempotent and closed-world, but the catalog still
checks `supplier:read` and tenant scope on every call.

## Read the implementation in this order

1. `LOGIC.md` defines the accepted boundary and limitations.
2. `models.py` closes identity, supplier and result contracts.
3. `catalog.py` applies scope and tenant filtering.
4. `server.py` registers tool, resource and prompt.
5. `demo.py` discovers and calls those capabilities without network I/O.
6. `tests/test_week22_mcp.py` verifies behavior and isolation.

For production, add a real authentication boundary, audience-bound tokens,
separate downstream credentials, transport interoperability tests, rate limits,
safe audit records and deployment controls. Do not accept tenant or privilege
claims from model-generated tool arguments.
