---
layout: week
week: 22
phase: 5
status: approved
version: 1.0.0
last_reviewed: 2026-11-12
estimated_hours: 8
permalink: /weeks/week-22/
title: "Expose interoperable tools without handing the model your identity"
description: Build a tenant-scoped MCP server with one tool, resource and prompt; inspect discovery, structured output, annotations and authorization boundaries.
summary: MCP standardises capability exchange, but every invocation still needs ordinary authentication, authorization, validation and audit controls.
kicker_primary: Model Context Protocol
kicker_secondary: Capabilities, discovery, identity and least privilege
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-22/beginner/
---

## Before you start

This route assumes you understand APIs, schemas and application authorization.
Use the [beginner route]({{ '/weeks/week-22/beginner/' | relative_url }}) first if
client/server or tool-calling terminology is new.

The lesson targets Model Context Protocol specification revision `2026-07-28`
and Python SDK 2.3.0. That revision has a stateless core and optional
`server/discover`; older initialize/session and legacy SSE examples are migration
material, not the default taught here.

The [Week 22 assessment]({{ '/assessments/week-22/' | relative_url }}) draws ten
questions from a 100-item practice bank.

| Hour | Focus | Evidence to retain |
| --- | --- | --- |
| 1 | Name host, client and server | one trust-boundary diagram |
| 2 | Separate capability types | tool/resource/prompt ownership table |
| 3 | Define schemas | closed input and structured output |
| 4 | Bind identity | tenant and scope derived outside tool input |
| 5 | Discover capabilities | deterministic lists and annotations |
| 6 | Threat-model the server | injection, confused deputy and token misuse |
| 7 | Exercise one local server | allowed, denied and cross-tenant cases |
| 8 | State transport gaps | what in-process tests cannot prove |

## Put MCP in the architecture

MCP is a protocol boundary between an AI application and capability servers.
Keep three roles distinct:

| Role | Responsibility |
| --- | --- |
| host | user-facing AI application and consent/policy boundary |
| client | protocol participant inside the host that connects to one server |
| server | declares and serves bounded capabilities |

A protocol makes integrations consistent; it does not decide business
authorization, make tool output trustworthy or turn an unsafe write into a safe
one.

## Distinguish tool, resource and prompt

The current Python SDK describes three server primitives by who selects them:

- a **tool** is an action the model may select, subject to host policy;
- a **resource** is read-only context the application selects; and
- a **prompt** is a named message template the user selects.

Week 22 exposes exactly one of each:

| Primitive | Lab capability | Important boundary |
| --- | --- | --- |
| tool | `supplier_lookup` | only `supplier_id` is model input |
| resource | `procurement://policy/supplier-lookup` | static, non-secret policy |
| prompt | `supplier_review` | grants no additional authority |

Discovery tells a client what exists. It is not permission to call everything.

## Build a tool schema for failure, not just success

The lookup tool returns structured output with one of three states:

- `found` with a small supplier record;
- `not_found` with no record; or
- `forbidden` with no record.

The Pydantic contract rejects extra fields, coercion and inconsistent pairs such
as `found` with no supplier. Structured output lets clients validate behavior
without scraping prose.

Tool annotations mark lookup read-only, non-destructive, idempotent and
closed-world. They are presentation and planning hints. The server must still
authorize the call; a malicious client can ignore hints.

## Keep identity out of model-generated arguments

The dangerous signature is:

~~~text
lookup_supplier(tenant_id, actor_id, scopes, supplier_id)
~~~

The model can then ask for another tenant or claim a stronger scope. The lab
instead constructs the server with a `Principal` supplied by a trusted transport
boundary. The tool accepts only `supplier_id`.

The catalog checks `supplier:read` and filters by the principal's tenant on every
invocation. A supplier belonging to another tenant returns the same `not_found`
shape as a nonexistent identifier, limiting enumeration leakage.

Authentication is intentionally not implemented in the lab. A production MCP
server must validate signature, issuer, expiry and audience before creating the
principal.

## Prevent the confused deputy

An MCP server that calls another API has two identities:

1. the inbound client identity accepted by the MCP server; and
2. the server's identity or delegated credential for the downstream API.

Do not forward the inbound MCP token as a general downstream token. Validate
that an inbound token was issued for this MCP server, then obtain a separate,
appropriately scoped credential for the upstream resource. Bind actions to the
authenticated user/tenant and preserve audit correlation without logging tokens.

## Understand the modern stateless core

In revision `2026-07-28`, each request carries protocol/client information and
can land on any instance. `server/discover` is optional, and list results can
carry caching hints with deterministic ordering. Header method/name fields help
gateways route and meter remote requests.

Application state can still exist, but it should be explicit—for example, a
tool returns a handle that a later call supplies—rather than hidden in a
transport session.

The SDK also supports multi-round-trip input-required results. Treat elicitation
as another consent and validation boundary, not as an excuse for an open-ended
model conversation inside a privileged tool.

## Run the local server

~~~shell
python -m labs.week_22.demo describe
python -m labs.week_22.demo call --supplier-id supplier-101
python -m labs.week_22.demo smoke
python -m pytest tests/test_week22_mcp.py -q
~~~

`serve` exposes the SDK's stdio transport for a local client:

~~~shell
python -m labs.week_22.demo serve
~~~

CI uses in-process capability calls so it stays deterministic. Those tests prove
registration and domain behavior, not wire framing or third-party client
interoperability.

## Production checklist

- Pin a protocol revision and SDK version; test upgrades deliberately.
- Validate inbound issuer, expiry, audience and scopes.
- Derive tenant and actor from trusted identity, never tool arguments.
- Authorize each invocation and minimise output.
- Treat annotations and prompts as hints, not security controls.
- Use separate downstream credentials; never pass through the inbound token.
- Add rate limits, bounded payloads, audit records and safe errors.
- Test stdio or remote transport with an independent client.
- Re-run authorization tests when tools, resources or prompts change.

## Primary references

- [MCP 2026-07-28 release](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- [MCP Python SDK server primitives](https://py.sdk.modelcontextprotocol.io/servers/)
- [MCP authorization security considerations](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/basic/authorization/security-considerations.mdx)
