---
layout: week
week: 19
phase: 5
status: approved
version: 1.0.1
last_reviewed: 2026-11-06
estimated_hours: 6
permalink: /weeks/week-19/beginner/
title: "Give an agent a small keyring, a supervisor and an undo plan"
description: Learn agent safety through a local procurement workshop with narrow tools, permission badges, exact write approvals, step limits, safe records and reversible actions.
summary: Let the agent suggest work, but make trusted code check its key, work order and step budget before a tool can change anything.
kicker_primary: Beginner path
kicker_secondary: Small keys, exact approvals and safe stops
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-19/
---

## The agent suggests; the workshop decides

Imagine a trainee in a workshop. The trainee can suggest:

> “I should look up contract `CTR-171`.”

or:

> “I should mark order `FLAG-918` for human review.”

The suggestion is not a key. A locked control desk still checks the trainee's
badge, the named operation, its arguments, the remaining step budget and—before
any change—the supervisor's exact work order.

That is the Week 19 safety gateway. It sits between an agent and five tiny local
tools. The agent cannot create permission by saying “the user approved it.”

The [production version]({{ '/weeks/week-19/' | relative_url }}) explains the
strict contracts, approval digest, audit-chain properties and production limits
in more depth.

The [Week 19 assessment]({{ '/assessments/week-19/' | relative_url }}) draws
10 balanced questions from a bank of 100, with explanations and browser Python
checks.

## Learn nine small ideas

| Idea | Plain meaning | Week 19 example |
| --- | --- | --- |
| Least privilege | carry only the keys needed for this job | a contract reader cannot set a flag |
| Read permission | see information without changing it | `contract:read` |
| Write permission | change a specific kind of state | `review_flag:write` |
| Approval gate | a person reviews one exact change before it runs | grant for one flag and value |
| Allowlist | only names written in the safe registry exist | no shell or arbitrary URL tool |
| Step limit | stop after a fixed number of attempts | request 3 is blocked when the limit is 2 |
| Sandbox | a small workshop with limited equipment | fixed in-memory Python functions |
| Audit trail | safe record of what was requested and decided | sequence, tool, result code and digest |
| Reversal | a separately approved way to restore earlier state | turn the review flag back to `clear` |

## Start with a small tool belt

Giving an agent a general shell is like handing the trainee every master key and
saying, “Please open only the right cabinet.” A safer design offers the smallest
specific tools:

| Tool | What it can do | What it cannot do |
| --- | --- | --- |
| contract lookup | read one contract in the trusted tenant | edit, delete or read another tenant |
| order lookup | read one order | place or cancel an order |
| supplier-risk lookup | read one risk record | contact or block a supplier |
| review-flag set | change one local flag after approval | make a purchase or send a message |
| review-flag revert | restore one earlier flag after new approval | undo unrelated or newer work |

There is no `run_any_command`, `fetch_any_url` or `execute_sql` tool. If an agent
asks for `shell_exec`, the gateway returns `unknown_tool`.

**Check yourself:** if the agent never needs a capability, should it be present
but hidden in instructions? No. Remove it from the available tool surface.

## Give different badges for reading and changing

Reading and writing are not the same job. A museum visitor may read a label but
cannot rewrite it. In the lab:

- `contract:read` opens the contract lookup;
- `order:read` opens the order lookup;
- `risk:read` opens the risk lookup;
- `review_flag:write` allows a proposed flag change; and
- `review_flag:revert` allows a proposed restoration.

The gateway gets these badges from trusted application code. They do not arrive
inside the agent's request. If the request could add its own permission, it could
write a fake badge.

The same resource ID can exist in two tenants. Trusted tenant scope chooses the
record; the agent cannot put another tenant in its arguments and cross the wall.

## Check the exact shape of every request

Each tool has a tiny form:

~~~text
contract_lookup: contract_id
purchase_order_lookup: order_id
supplier_risk_lookup: supplier_id
review_flag_set: flag_id + value
review_flag_revert: undo_token
~~~

Extra fields are rejected. Missing fields are rejected. Numbers are not silently
turned into strings. The flag value must be exactly `clear` or `needs_human`.

This matters because a hidden extra field could try to add a callback URL,
different tenant or broad command. “The tool probably ignores it” is not a safe
contract.

## Ask a human about one exact write

Permission and approval answer different questions:

| Check | Question |
| --- | --- |
| Permission | Is this agent ever allowed to propose this kind of change? |
| Approval | Did a human approve this exact change in this run? |

The lab binds an approval to the tenant, agent, run, case, request, tool and exact
arguments. It makes a stable SHA-256 digest of the arguments. If the value changes
after the supervisor reviewed it, the digest changes and the gateway refuses the
grant.

One grant works once. Even if the tool later fails, retrying needs a new decision.
That prevents a stale approval from being copied across several writes.

The digest is a label for the exact arguments. It does not hide a weak secret and
does not prove the person understood the action. The approval screen still needs
to show clear details.

## Put the counter outside the agent

An agent may repeat a step because it is confused or because bad content tells it
to keep going. A prompt that says “stop soon” can be ignored.

The gateway owns the counter. Its maximum is between 1 and 20. In the
`max-steps` scenario, two reads finish and the third request returns:

~~~text
status: blocked
code: step_limit_exceeded
~~~

The third tool never runs. A real system may also limit time, tokens, cost,
network calls and output size.

## Keep the workshop truly small

The local sandbox is a workshop containing only fixed dictionaries and five
Python operations. There is no network, shell, file access, database or real
procurement action.

That makes the lab easy to inspect and repeat. It does not make one Python
process safe for hostile code. A production system that runs risky code needs a
separate process, container or virtual machine plus network and resource limits.

Approval is like a signed work order. A sandbox is the locked workshop. You often
need both; one does not replace the other.

## Keep secrets off the workbench

An agent normally should not receive passwords, API keys or access tokens. A
trusted tool can use a short-lived credential behind the boundary without adding
it to model context.

The lab rejects keys that look like:

- `api_key`;
- `authorization`;
- `credential`;
- `password`;
- `secret`; or
- `token`.

The reversal needs one special `undo_token`. Only that exact tool accepts it, and
the audit record keeps a digest rather than the raw token. This simple check is
not a complete secret detector; a secret could have a harmless-looking name.

## Keep a useful record, not a dangerous copy

The audit trail records what investigators need:

- sequence number;
- trusted tenant, agent, run and case;
- tool name;
- safe decision code;
- digest of the arguments;
- valid approval identity when used; and
- links to the previous and current event hashes.

It does not record raw arguments, passwords or internal exception messages.

Changing or reordering one supplied event breaks the hash chain. But the local
chain is not a magic unchangeable ledger. It does not prove who wrote the events,
and someone could remove a valid ending unless a protected system stores or
anchors the final hash.

## Make the safe change undoable

After an approved flag update, the tool returns a receipt:

~~~text
before: clear
after: needs_human
undo token: opaque local capability
~~~

Undo is also a write. It needs its own permission and a fresh human approval. It
works only in the same tenant and only once.

The gateway also checks whether newer work changed the flag. If the current value
no longer matches the first write, old undo information must not overwrite it.
The result is `undo_conflict`, and a person decides what to do.

Some actions cannot really be undone. A recipient may already have read a
message, copied data or received money. For those actions, use a draft, delay,
second review or no agent write access.

## Return safe failures

The caller receives a short status and code:

| Status | Meaning | Example |
| --- | --- | --- |
| completed | allowed work finished | `ok` |
| blocked | a safety rule stopped it | `permission_denied` |
| failed | allowed work could not finish safely | `tool_failure` |

The lab deliberately raises an exception containing fake internal database
details. The public result contains only `tool_failure`. Real diagnostic details
belong in a protected operator system, not in the agent's next prompt or a public
audit stream.

## Run the lab

~~~shell
python -m pip install -r requirements-dev.txt
python -m labs.week_19.demo case --scenario read
python -m labs.week_19.demo case --scenario write-without-approval
python -m labs.week_19.demo case --scenario approved-write
python -m labs.week_19.demo case --scenario reversal
python -m labs.week_19.demo case --scenario secret-rejected
python -m labs.week_19.demo case --scenario max-steps
python -m labs.week_19.demo case --scenario tool-failure
python -m labs.week_19.demo smoke
python -m pytest tests/test_week19_agent_safety.py -q
~~~

Look for these outcomes:

| Scenario | Expected result |
| --- | --- |
| read | contract data returns and audit chain verifies |
| write without approval | blocked; flag stays `clear` |
| approved write | flag becomes `needs_human`; receipt appears |
| reversal | new approval restores `clear` |
| secret rejected | raw secret is absent from audit |
| maximum steps | request 3 stops before the tool |
| tool failure | stable code hides fake internal details |

The 29 tests also try wrong permissions, unknown tools, malformed arguments,
cross-tenant access, mismatched and reused approvals, changed audit events,
reused undo and stale undo.

## Common mistakes

### “The prompt says not to write”

A prompt is guidance. Remove write permission or require an external gate.

### One giant tool with many commands

An allowlisted giant shell is still a giant shell. Offer narrow operations.

### One approval for the whole conversation

The action can change after review. Bind approval to one exact call.

### Logging every argument

More data can mean more leaked secrets. Record safe decision metadata and keep
protected diagnostics separate.

### Calling a normal function a sandbox

A name does not create isolation. List the capabilities the executor truly has.

### Undo without checking current state

An old undo can destroy newer work. Compare the expected state first.

### Treating hash links as an unchangeable ledger

A local chain detects some changes in supplied events. Durable protected storage
and an external anchor are separate controls.

## Practice questions

1. Why should a tool request not contain its own permission list?
2. What is the difference between `contract:read` and `review_flag:write`?
3. Why does a write need both permission and approval?
4. Which fields should an exact approval bind?
5. Why is a hard counter stronger than a prompt instruction?
6. What makes this lab's dispatcher closed?
7. Why are raw tool arguments absent from the audit events?
8. What can the hash chain detect, and what can it not prove?
9. Why does reversal need a new approval?
10. Why must a stale undo refuse to overwrite newer state?
11. Why is `tool_failure` safer than returning a raw exception?
12. What extra controls would a production sandbox need?

Try the [Week 19 assessment]({{ '/assessments/week-19/' | relative_url }}) for a
random paper covering trusted scope, narrow tools, exact write approval, step
limits, safe audit evidence, controlled failures and one-use reversal.

## Read alongside the lab

- [Week 19 production lesson]({{ '/weeks/week-19/' | relative_url }})
- [Week 19 lab](https://github.com/kogantisasank831-ux/Prep/tree/main/labs/week_19)
- [OWASP Excessive Agency guidance](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)
- [OWASP AI Agent Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html)
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [NIST least-privilege definition](https://csrc.nist.gov/glossary/term/least_privilege)
- [OpenAI human-in-the-loop guide](https://openai.github.io/openai-agents-python/human_in_the_loop/)
- [OpenAI tools guide](https://openai.github.io/openai-agents-python/tools/)
