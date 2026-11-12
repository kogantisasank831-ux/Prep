# Week 22 content and lab review

## Scope and disposition

Roadmap source: `Path.md`, Week 22 — MCP and interoperable tools.

The reviewed scope includes two lessons, `labs/week_22/`, focused tests and a
100-item assessment. It targets specification revision `2026-07-28` and pinned
Python SDK 2.3.0. All pages are `status: approved`; publication was authorized
on 2026-11-12.

## Coverage

| Requirement | Treatment | Executable evidence |
| --- | --- | --- |
| Host/client/server | trust roles and responsibility split | lesson and capability inspection |
| Tools/resources/prompts | exactly one of each | deterministic discovery lists |
| Capability discovery | current stateless/discovery model | in-process lists and ordering |
| Structured contracts | closed Pydantic input/output | schema and coherence tests |
| Security | trusted principal outside model input | scope, tenant and cross-tenant tests |
| Authorization | per-invocation `supplier:read` check | allowed and forbidden results |
| Interoperability | stdio entry point and explicit gap | local server command; no false wire claim |

## Source and protocol review

Primary sources reviewed on 2026-11-11 were the MCP `2026-07-28` release,
official Python SDK server documentation and official authorization security
considerations. The lessons distinguish the modern stateless core and optional
`server/discover` from older initialize/session examples. They state that tools
are model-selected, resources application-selected and prompts user-selected.

The lab binds a trusted principal at server construction, accepts only
`supplier_id` from the tool caller and makes missing and cross-tenant IDs
indistinguishable. Tool annotations are described as hints, not enforcement.
Token audience validation and the prohibition on inbound-token passthrough are
covered, while authentication itself is explicitly outside the lab.

## Focused verification

- Ruff, formatting and strict mypy pass for the server and tests.
- Discovery, schema, annotation, scope, isolation, resource, prompt and CLI tests
  pass without a model, token, database or network.
- The Week 22 assessment passes the shared browser and executable-code gates.
- Independent-client transport and OAuth checks remain future production work
  and are not claimed by this bounded lab.
