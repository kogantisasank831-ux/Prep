# Week 22 MCP capability contracts — revision 1

Source: `Path.md` Week 22 and Model Context Protocol specification revision
`2026-07-28`. The dependency is pinned to the Python SDK 2.3.0. This lab teaches
capability shape and authorization; it is not an identity provider or a deployed
remote MCP service.

| ID | Effective rule and acceptance |
| --- | --- |
| W22-BR1 | Expose exactly one tool, one resource and one prompt so learners can distinguish model-controlled, application-controlled and user-controlled capability types. |
| W22-BR2 | Bind a trusted `Principal` when constructing the server. The tool accepts only `supplier_id`; tenant and actor are never model-supplied arguments. |
| W22-FR1 | Require `supplier:read` at invocation time and return a stable structured `forbidden` result when it is absent. |
| W22-FR2 | Filter every catalog lookup by the authenticated tenant. A cross-tenant identifier and a nonexistent identifier must produce the identical response. |
| W22-FR3 | Mark the tool read-only, non-destructive, idempotent and closed-world. Treat annotations as client hints, not authorization controls. |
| W22-FR4 | Return closed Pydantic structured output with a coherent status/supplier pair. |
| W22-FR5 | Expose only static, non-secret policy text as a resource. Never expose the in-memory catalog as a resource. |
| W22-FR6 | Keep the prompt bounded to lookup and summary; it grants no authority and embeds no supplier record. |
| W22-SR1 | Do not accept bearer tokens, tenant IDs or scopes in tool arguments. A real transport must authenticate and validate token audience before creating the principal. |
| W22-SR2 | Do not pass an incoming MCP token to another API. Use a separately acquired, correctly scoped downstream credential. |
| W22-NFR1 | Capability order and synthetic lookup results are deterministic and need no network, model, secret or database. |
| W22-ER1 | Test discovery, annotations, output schema, allowed/denied/missing/cross-tenant lookups, resource and prompt behavior, strict models and every non-blocking CLI path. |

## Modern protocol boundary

The lesson targets MCP specification revision `2026-07-28`. Modern remote MCP
uses a stateless request model with server discovery; older initialization,
session and legacy SSE examples may still appear in articles and SDK migration
material. The local SDK's in-process `list_*`, `call_tool`, `read_resource` and
`get_prompt` methods make the teaching checks deterministic; they do not replace
transport interoperability tests.

## Authorization boundary

Authentication is deliberately outside this server. `create_server` receives a
validated principal from that missing boundary. In production, the transport
must verify signature, issuer, expiry and audience, map identity to a tenant and
scopes, and prevent confused-deputy behavior. Tool annotations improve client
presentation only; the catalog repeats authorization for every call.

## Accepted limitations

- All supplier records and identities are synthetic and process-local.
- The CLI `serve` command can expose the SDK's stdio transport, but CI checks
  capabilities in-process and does not prove framing or third-party client
  interoperability.
- No OAuth authorization server, audience validation, consent UI, rate limit,
  audit sink, downstream API or secret store is implemented.
- The server has no write tool, so approval, idempotency and ambiguous write
  reconciliation are intentionally out of scope.
- The prompt is a template, not a security boundary; every tool invocation must
  still authorize independently.
