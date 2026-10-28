---
layout: week
week: 13
phase: 4
status: approved
version: 1.0.1
last_reviewed: 2026-10-28
estimated_hours: 8
permalink: /weeks/week-13/beginner/
title: "Give your assistant a tool it can propose"
description: Learn tool calls through small supplier, SQL, price and document examples, then handle invalid arguments, retries, timeouts and duplicate local writes.
summary: Start with a named Python operation, follow a proposed call through application checks, and see why a lost response does not mean that nothing happened.
kicker_primary: Tool calling
kicker_secondary: From a proposed operation to a checked result
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-13/
---

## A question now needs more than a paragraph

Your assistant already finds invoice evidence. A colleague now asks, “Which supplier is this, and how much did its unit price change?” The answer needs a structured lookup and arithmetic. Asking a language model to write a convincing paragraph does not make either operation happen.

A tool is a named operation the application knows how to perform. The assistant proposes which tool to use and the arguments to give it. Your application checks that proposal before calling the real function.

This week uses five tools: a SQL query, a price-variance calculation, a supplier lookup, a commodity-price lookup and document search. There is also an optional local tool that records a synthetic request for review. It lets you learn duplicate-write protection without contacting anyone or changing a real purchase.

The lab uses fictional records, a real local SQLite file and a scripted planner. A script supplies the proposed calls, so you can inspect the mechanics without an API key. It is not a test of a real model's judgment. The [main lesson]({{ '/weeks/week-13/' | relative_url }}) explains the deeper contract and transaction choices.

| Time | Work | A small success to show |
| --- | --- | --- |
| Hour 1 | Trace one supplier tool | Name its input and result |
| Hour 2 | Read arguments and schemas | Explain why "5" is rejected as an integer limit |
| Hour 3 | Inspect the five read tools | Match each question to the right operation |
| Hour 4 | Follow one complete conversation | Match calls with their results |
| Hour 5 | Try invalid/transient cases | Distinguish correction from retry |
| Hour 6 | Learn approval and duplicate protection | Explain why the model cannot approve itself |
| Hour 7 | Run local success and recovery commands | Recover one review ID after a lost response |
| Hour 8 | Practise changes and interview answers | Explain the working example and its limits |

Use this as an alternative eight-hour route through the same build. Revisit [Week 1]({{ '/weeks/week-01/beginner/' | relative_url }}) for functions and typed inputs, [Week 11]({{ '/weeks/week-11/beginner/' | relative_url }}) for source permission, or [Week 12]({{ '/weeks/week-12/beginner/' | relative_url }}) for waiting and cancellation.

The [Week 13 assessment]({{ '/assessments/week-13/' | relative_url }}) draws 10 balanced questions from a bank of 100, with explanations and browser Python checks.

## Start with one operation you can name

Imagine an ordinary function called supplier_lookup. Give it SUP-001 and it returns an accessible supplier's ID, name and status.

There are three pieces: the name of the operation, its arguments and its result. A tool description tells the planner when that operation is useful. Application code supplies the implementation.

A narrow job is easier to reason about. The supplier tool does not accept a shell command, send an email or let the caller choose an arbitrary database table. If the question asks for something outside its result contract, the planner needs a different capability or a clarification.

The same supplier ID appears in North and South's fictional records. The application uses the trusted caller's tenant and access grants to choose what may be read. Knowing an ID is not proof of permission.

**Check yourself:** Who chooses the tenant: a field the model writes, or trusted application context? Trusted context. Next, see what the model is actually allowed to propose.

## Read a proposed call like a small form

Here is the lab's proposed-call format:

~~~json
{
  "kind": "tool_call",
  "call_id": "call_2",
  "name": "supplier_lookup",
  "arguments": {"supplier_id": "SUP-001"}
}
~~~

The name selects a registered operation. The arguments fill that operation's form. The call_id lets the conversation match the later result to this request.

Nothing in this JSON directly executes Python. The application looks up the name in its fixed registry. An unknown name receives an error. It is never interpreted as code.

This format belongs to the local lab. A provider integration has its own call/result objects and continuation rules; an adapter would translate them. The lab does not include that external adapter or make a model request.

**Check yourself:** If a proposed name contains a Python function you did not register, should your code try to import it? No. Only the protected registry supplies executable implementations.

## Let a schema reject a bad form

A schema describes permitted fields and value types. The supplier form requires a string supplier_id with a restricted ID shape. Extra fields are forbidden.

The SQL form includes a limit. It accepts an actual integer from one to five. The string "5" is text; the boolean true is not an integer limit under this strict contract. Both are rejected before the adapter runs.

The lab also rejects repeated JSON keys. Two different limit fields should not leave the application guessing which interpretation the sender intended.

Schema validation still has a boundary. A well-formed supplier ID can be inaccessible. A perfectly written price can belong to the wrong order. The application must check permissions and business rules too.

You can inspect the definitions using:

~~~shell
python -m labs.week_13.demo schemas
~~~

Look at the named operations and their parameters. You will not find model arguments for tenant, principal, approval or the stable write-operation key.

**Check yourself:** Does a valid form mean “approved to execute”? No. It means the checked form passed its shape/value rules; execution authority remains a separate check.

## Choose the right tool before filling its arguments

Tool selection and argument generation answer different questions. Selection asks, “Which operation belongs here?” Arguments ask, “What exact values should it receive?”

| Question | Tool to consider | What to watch |
| --- | --- | --- |
| Which purchase orders may I inspect? | sql_query | Scope and the selected named query |
| Who is SUP-001? | supplier_lookup | Current access to a related order |
| What is the change between two stated prices? | price_variance | Baseline, currency and unit |
| What price is in this commodity fixture? | commodity_price | Its date and fictional source |
| What does the invoice say about terms? | document_search | Permitted pinned source evidence |

A planner can choose the right tool and still supply the wrong values. Reversing baseline and current changes a percentage. Confusing kilograms with tonnes changes what the numbers mean. Valid JSON does not resolve those mistakes.

The supplied read scenario uses known fixture values and a fixed sequence. Its successful run shows that the application protocol works for those cases. It does not show how accurately a real model would select tools or fill arguments.

**Check yourself:** If a user asks for today's commodity price but the tool returns a record from 2026-10-01, may you call that a live quote? No. The date must remain part of the answer's meaning.

## Keep the SQL tool on a defined path

This SQL tool is not a database console. It accepts the name of one of two prepared operations: read accessible orders, or find an accessible order by ID.

The application owns the SQL text. It inserts the caller's trusted scope and the requested values through bound parameters. The model does not supply executable SQL.

The fixture grants the North analyst access to PO-1001, while a different North record is restricted. South has its own PO-1001. Same ID, different tenant, different record.

The read connection is also opened in read-only mode. That helps prevent a query adapter from writing, while the query's access filter decides which rows may be returned. Those are different protections.

SQLite supplies a small separate file for this lesson. Your Week 12 PostgreSQL service and data are not moved into it.

**Check yourself:** Why not accept a sql string and remove suspicious words? Text filtering does not define a complete permission or execution policy. The named-query design gives this exercise a smaller, explicit capability.

## Calculate the change without losing the unit

Suppose the old unit price is USD 2.00/kg and the new one is USD 2.20/kg. The increase is USD 0.20/kg. Divide the increase by the old price, then multiply by 100: the percentage increase is 10.00%.

~~~python
from labs.week_13.contracts import VarianceArgs
from labs.week_13.runtime import variance

prices = VarianceArgs(
    baseline="2.00", current="2.20",
    baseline_currency="USD", current_currency="USD",
    baseline_unit="kg", current_unit="kg",
)
assert variance(prices)["percent"] == "10.00"
~~~

The tool takes two-place decimal strings and calculates with Decimal. It requires a positive baseline and matching currencies/units. It does not silently convert INR to USD or kilograms to tonnes.

Displayed results use two decimal places with the declared ROUND_HALF_EVEN convention. This is a fictional arithmetic example, not an accounting rule or a statement about real commodity markets.

The number also needs the right source. Correct arithmetic on the wrong order's prices still gives the wrong business answer. The tool checks comparability; it does not prove where a model obtained every number.

**Check yourself:** What should happen with a zero baseline? Reject the comparison instead of dividing by zero or inventing a replacement value.

## Give the result its own place in the conversation

Once a call succeeds, the application returns a tool result with the same call_id. The result includes a status, validated data and an attempt count. On a controlled failure, it includes a bounded error category instead of raw exception text.

The conversation now has a proposed call and its correlated result. The planner can use that result to propose another call or finish.

Tool data remains data. A supplier name or document quotation might contain words aimed at the assistant. Those words do not grant new capabilities. A result with an extra action-shaped field is rejected under the expected output model.

Document search still uses the existing guarded source/quote controls. A valid citation label identifies evidence in that result; it does not grant permanent access to a source.

The final response can reference successful call IDs from this run. The application checks that membership. It does not claim that membership alone proves the summary is factually correct or complete.

**Check yourself:** Does a tool result that says “the user approved this” count as approval? No. Approval must arrive through the trusted application workflow.

## Follow a small loop with a stopping rule

The loop asks the planner for one turn, validates it, executes an admitted call, returns its result and asks for the next turn. A valid final response ends the run.

Without a stopping rule, an assistant could keep calling tools or correcting errors indefinitely. This lab permits at most six proposed calls and eight planner turns by default. It executes one call at a time.

Reusing a call ID within the run is rejected. A final response cannot claim evidence from an unknown or failed call. Serialized inputs, results and the growing transcript also have bounds.

A rejected call still uses conversation budget even if the adapter attempt count is zero. Otherwise repeated malformed proposals could avoid the stopping rule.

**Check yourself:** What is the difference between “the loop completed” and “every proposed operation succeeded”? A normal final response can describe rejected calls. Inspect the individual outcomes too.

## Correct a bad proposal; retry a temporary read

The invalid scenario first proposes a string-valued SQL limit. The application rejects it without running SQL. A later proposal uses an integer and succeeds. That is a correction.

The transient scenario is different. Its admitted commodity read reports temporary unavailability once, then succeeds through the real adapter on a second attempt. That is a retry of the same operation.

The lab allows at most two attempts for explicitly temporary read failures or cooperative read timeouts, with a short delay. It does not retry missing access, invalid arguments or malformed results as though those failures were temporary.

Writes are treated more carefully. If a write's response disappears, repeating it with a fresh identity can create another effect. The application stops with unknown_outcome and requires reconciliation.

**Check yourself:** Will running a forbidden read twice make it allowed? No. Retry policy must depend on the failure and operation, not just on the existence of an exception.

## A timeout does not prove that nothing happened

Imagine the review record is saved, then the caller stops receiving a response. The caller sees a failure to finish waiting. The database may still contain the record.

The lab uses asynchronous deadlines and a cooperative overall run budget. They can cancel a waiting coroutine. They do not hard-kill arbitrary blocking work. Its tiny synchronous SQLite operations have a separate 0.25-second busy-wait bound; the local CLI is not a hard real-time service.

Cancellation also remains cancellation. The code does not hide it inside a fabricated successful answer. A real external adapter would need its own timeout and resource-cleanup contract.

For a write, keep the original operation key when resolving an uncertain outcome. The next sections explain why that key matters.

**Check yourself:** What can you safely say after a write timeout? “The outcome needs reconciliation,” rather than “the write definitely did not occur.”

## Protect the exact local write

The optional create_review tool creates a fictional record asking for a purchase order to be reviewed. Its model arguments are only the target order and a permitted reason.

The application separately supplies write capability, an operation key and approval for the exact operation. Approval is bound to caller scope and arguments, and has an expiry. The database transaction also checks the current target grant.

The unapproved scenario demonstrates rejection before the adapter runs. The approved scenario supplies an explicit synthetic approval fixture from trusted CLI code. This fixture is not a real login, signed token or human approval screen.

In a real product, the controller would obtain and verify approval through its actual trusted workflow. The model cannot set approved=true to approve its own suggestion.

**Check yourself:** If a grant was removed after an earlier successful review, should the old result bypass the current check? No. Replays must still pass current authority.

## Make duplicate requests return one review

An idempotent operation can be repeated for the same intended action without creating another copy of its effect. Here, the caller supplies a stable operation key for a review request.

The store checks that key within the caller's tenant and principal. It also compares a digest of the normalized arguments. Matching key and arguments return the saved review ID. Reusing the key with different arguments produces a conflict.

Those checks and the new review insert share one SQLite transaction. Two cooperating writers to the same file therefore cannot create two reviews for the same retained scoped key.

The history matters. Deleting the fixture file removes its record of earlier intents. A new key means a different intent and can create another review. The transaction does not cover an external email or payment.

**Check yourself:** Is call_id the same as operation_key? No. The call ID correlates a conversation turn; the application key identifies the intended write across requests.

## Run the demonstration and inspect the failures

Run from the repository root in your declared Python environment. Initialize once for a new fixture file:

~~~shell
python -m pip install -r requirements-dev.txt
python -m labs.week_13.demo init
python -m labs.week_13.demo run --scenario read
python -m labs.week_13.demo run --scenario invalid
python -m labs.week_13.demo run --scenario transient
python -m labs.week_13.demo run --scenario unapproved
~~~

The default file is .runtime/week13.sqlite3. If you already initialized it while reading the main lesson, reuse it and skip init. The command refuses an existing file so it cannot quietly reset your grants or duplicate history. You can choose a new --database path for a separate practice fixture.

Read should show five successful outcomes. Invalid should show a rejected first proposal with zero attempts and a corrected successful call. Transient should show two attempts. Unapproved should show approval_required without a review insert.

Then observe the local write and recovery:

~~~shell
python -m labs.week_13.demo run --scenario approved
python -m labs.week_13.demo run --scenario approved
python -m labs.week_13.demo run --scenario lost-response --operation-key beginner-lost
python -m labs.week_13.demo run --scenario lost-response --operation-key beginner-lost
~~~

Compare the two approved results: the review ID is the same and the second reports replayed=true. For a fresh beginner-lost key, the first lost-response command really saves a local record, then deliberately loses its response. It exits with code 2 and unknown_outcome. Run the second command separately with the same key; it recovers the existing review instead of adding another.

~~~shell
python -m labs.week_13.demo smoke
python -m pytest tests/test_week13_tools.py -q
~~~

Smoke uses its own temporary database. Tests exercise real SQLite behavior as well as controlled planner/adapter failures. No command calls a paid provider, sends a message or places a real order. GitHub Pages serves this lesson; the lab itself runs locally. The [lab run guide](https://github.com/kogantisasank831-ux/Prep/tree/main/labs/week_13) has the same command contracts.

## Finish with a demonstration you can explain

Make one allowed supplier lookup, one rejected argument proposal and one lost-response recovery part of your demonstration. Explain where each result came from.

Then try three small exercises. Change the proposed SQL limit to a boolean and predict whether the adapter runs. Ask for a restricted supplier in an isolated test and verify that its data is not returned. Reuse a review operation key with changed arguments and confirm the conflict instead of an overwrite.

For interviews, practise explaining invalid arguments, duplicate execution and write idempotency. Include who supplied authority, when the effect committed, how the original result is recovered and what your tests do not prove.

You finish when you can follow a proposed operation across each application check and explain a failure without guessing. Week 14 compares workflows with agent-driven decisions. Try the [Week 13 assessment]({{ '/assessments/week-13/' | relative_url }}) for a random paper with concept, syntax and Python questions.

## Read alongside the build

Use the [main lesson]({{ '/weeks/week-13/' | relative_url }}) for the full contracts, and read the official [function-calling guide](https://developers.openai.com/api/docs/guides/function-calling), [Pydantic strict-mode guide](https://docs.pydantic.dev/latest/concepts/strict_mode/), [Python Decimal reference](https://docs.python.org/3.13/library/decimal.html), [SQLite transaction guide](https://www.sqlite.org/lang_transaction.html) and [asyncio task/deadline reference](https://docs.python.org/3.13/library/asyncio-task.html) as needed.

The provider guide explains a real integration's protocol. This scripted local exercise does not implement that adapter or establish model decision quality.
