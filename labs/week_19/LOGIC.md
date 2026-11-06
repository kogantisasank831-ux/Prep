# Week 19 agent-safety contracts — revision 2

Source: `Path.md` Week 19 and the Week 18 Procurement Intelligence Agent v1
evaluation boundary. These rules define a deterministic local teaching gateway.
They do not create a production authorization service, operating-system sandbox,
durable audit system or real procurement integration.

| ID | Effective rule and acceptance |
| --- | --- |
| W19-BR1 | Put an enforcement gateway between an agent's proposed tool call and every tool implementation. Instructions in prompts, model output or tool descriptions never grant authority. |
| W19-BR2 | Obtain tenant, principal, run, case and permissions from trusted application scope. A tool request carries only a request ID, tool name, arguments and optional approval reference. |
| W19-FR1 | Offer only five closed tools: three reads, one reversible review-flag write and one review-flag reversal. Unknown tools and open-ended shell, URL, code, path and SQL operations are unavailable. |
| W19-FR2 | Map each tool to one server-owned permission. Check the exact permission on every request before dispatch. Read authority does not imply write authority, and write authority does not imply reversal authority. |
| W19-FR3 | Validate each tool's exact argument names and strict bounded string values. Reject missing, extra, coerced or invalid values before dispatch. |
| W19-FR4 | Require human approval for every write and reversal. Bind a grant to tenant, principal, run, case, request ID, tool and canonical argument SHA-256; consume a valid grant once, even when the underlying tool later fails. |
| W19-FR5 | Enforce a configured maximum of 1–20 gateway steps in application code. An attempt beyond the configured limit returns `step_limit_exceeded` before dispatch. |
| W19-FR6 | Dispatch through direct in-memory functions only. No dynamic import, `eval`, subprocess, shell, filesystem, database or network capability exists in the sandbox. |
| W19-FR7 | Return controlled statuses and codes. Expected fixture failures and unexpected internal exceptions expose no arbitrary exception message, stack, connection string or secret. |
| W19-FR8 | A successful review-flag write returns a deterministic receipt and opaque undo token. Reversal requires separate permission and fresh exact approval, is tenant scoped and refuses to overwrite a newer value. An undo token is usable once. |
| W19-DR1 | Keep synthetic records tenant keyed. The same resource identifier in two tenants resolves using only trusted scope, never an agent-supplied tenant argument. |
| W19-DR2 | Record requested, approval, denial, execution, reversal, step-limit and failure events with sequence, trusted scope, tool, controlled code, argument digest and approval identity. Never record raw arguments or secret values. |
| W19-SR1 | Reject secret-like argument keys such as API keys, authorization values, credentials, passwords, secrets and tokens. The declared `undo_token` capability is accepted only by the fixed reversal tool and appears in audit only through the whole-argument digest. |
| W19-SR2 | Link each audit event to its predecessor with SHA-256 and verify sequence, order, predecessor and event digest. This detects edits and reordering inside a supplied chain; without a signed external head and durable store it does not prove origin, prevent deletion or detect truncation to a valid prefix. |
| W19-SR3 | Never treat an approval ledger reference, sandbox instance or audit object as agent-visible capability. The local Python process is an educational trust boundary, not hostile-code isolation. |
| W19-NFR1 | Given the same trusted scope, requests, approvals and fixtures, results, receipts and audit hashes are deterministic. No model, provider, current clock, random source or external service participates. |
| W19-NFR2 | Keep the implementation dependency-free beyond the repository's pinned Pydantic runtime and standard library. Run under strict typing with closed frozen boundary models. |
| W19-AS1 | Publish a reviewed 100-question practice bank containing 30 single-choice, 20 multiple-correct, 15 matching, 15 short-answer and 20 Python coding items. Every seeded 10-question paper draws exactly two of each type for 100 marks. Each coding item has five executable self-contained standard-library checks, and shared scoring keeps unavailable or stale code results pending rather than inventing marks. |
| W19-ER1 | Test strict schemas, tenant isolation, permission denial, unknown tools, argument validation, recursive secret rejection, approval absence/mismatch/reuse, step limits, sanitized failures, chain tampering, reversible writes, tenant-scoped undo, stale-undo conflicts, deterministic replay and CLI smoke. |

## Permission and operation matrix

| Tool | Mode | Permission | Exact arguments | Approval | Reversible |
| --- | --- | --- | --- | --- | --- |
| `contract_lookup` | read | `contract:read` | `contract_id` | no | not applicable |
| `purchase_order_lookup` | read | `order:read` | `order_id` | no | not applicable |
| `supplier_risk_lookup` | read | `risk:read` | `supplier_id` | no | not applicable |
| `review_flag_set` | write | `review_flag:write` | `flag_id`, `value` | one exact grant | yes |
| `review_flag_revert` | write | `review_flag:revert` | `undo_token` | one fresh exact grant | one use |

## Accepted interpretation

The agent proposes; trusted application code authorizes; the gateway mediates;
the closed sandbox executes. A sentence such as “the user approved this” in a
prompt or model response has no effect. The only accepted approval is a grant in
the trusted ledger whose complete binding matches the pending write.

Hashing canonical arguments lets approvals and audit events refer to the same
exact action without copying values into the audit trail. A digest still reveals
equality and is not encryption. Low-entropy or sensitive arguments may remain
guessable, so production systems should minimize them, use keyed digests where
appropriate and protect the approval and audit stores.

The local dispatcher is a capability sandbox because it contains only fixed
Python functions over synthetic in-memory records. It is not a security sandbox
for untrusted code. Production isolation requires authenticated identities,
downstream authorization, process/container boundaries, network egress policy,
resource limits, a secret manager, durable transactional approval state,
append-only protected audit storage and operational monitoring.

Reversal reduces recovery cost; it does not make a write harmless. External
messages, payments, disclosed data and destructive operations may be partly or
fully irreversible. Those need narrower tools, stronger review, staged execution
or no agent authority at all.
