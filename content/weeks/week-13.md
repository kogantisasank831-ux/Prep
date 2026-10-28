---
layout: week
week: 13
phase: 4
status: approved
version: 1.0.1
last_reviewed: 2026-10-28
estimated_hours: 8
permalink: /weeks/week-13/
title: "Let the assistant propose a tool call"
description: Build a bounded tool-calling loop with strict arguments, scoped SQL and lookups, exact price variance, guarded search, explicit failure handling and local idempotent writes.
summary: Follow one procurement question from a proposed function call to a validated result, then handle invalid arguments, timeouts and a write whose response disappears.
kicker_primary: Tool calling
kicker_secondary: A proposal crosses an application boundary
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-13/beginner/
---

## The next question needs an operation

Your assistant can find an invoice clause and quote its payment terms. Now a colleague asks, “Which purchase order is this supplier attached to, how much did its unit price change, and should someone review it?” A paragraph from a document cannot perform every part of that task. Some facts live in structured records, some need arithmetic, and recording a review would change state.

A tool gives the assistant a named operation it can propose. The application still owns the implementation and decides whether to execute it. That distinction carries [Week 11's security boundary]({{ '/weeks/week-11/' | relative_url }}) into the service ideas from [Week 12]({{ '/weeks/week-12/' | relative_url }}): useful text can describe a request without acquiring authority to carry it out.

This week builds five tools: SQL queries, price-variance calculation, supplier lookup, commodity-price lookup and document search. A sixth, optional tool creates a local synthetic review record so duplicate-write protection has something observable to protect. It cannot place orders, make payments, contact suppliers or send messages.

The runnable lab uses a scripted planner, actual SQLite records and the existing guarded document assistant. No provider key or model download is needed. The planner's fixed proposals exercise the protocol; they do not measure whether a real model would choose the right tool, arguments or final answer. The [beginner version]({{ '/weeks/week-13/beginner/' | relative_url }}) follows the same build in smaller steps.

| Time | Focus | Evidence to retain |
| --- | --- | --- |
| Hour 1 | Separate a proposal from an executable function | Trace one supplier lookup |
| Hour 2 | Read schemas and test invalid arguments | A rejected string-valued SQL limit |
| Hour 3 | Examine the five tool implementations | Scoped records, arithmetic and dated evidence |
| Hour 4 | Follow correlated results through the loop | One complete five-tool transcript |
| Hour 5 | Classify failures, retries and timeouts | Attempt counts and a cancellation explanation |
| Hour 6 | Study approval and duplicate protection | One review ID returned across repeated requests |
| Hour 7 | Run failure cases and the tests | A lost-response recovery and a scope negative |
| Hour 8 | Change one boundary and explain it | A short demonstration and interview notes |

Use the lab as a reference you can run and modify. The eight-hour route does not require retyping the implementation.

The [Week 13 assessment]({{ '/assessments/week-13/' | relative_url }}) draws 10 balanced questions from a bank of 100, with explanations and browser Python checks.

## Begin with a function that has a narrow job

What could a supplier tool reasonably promise? Given a supplier ID, it can look up an accessible supplier and return its name and status. It should not also interpret arbitrary SQL, approve a purchase and follow a URL mentioned in a note.

In the lab, the operation is named supplier_lookup. Its argument is supplier_id. Its result contains supplier_id, name and status. The application implementation finds the row using the trusted caller's tenant and current access to a related purchase order.

That last part is deliberately absent from the model's arguments. The model may supply SUP-001; it may not choose another tenant or claim to be an administrator. North and South both use SUP-001 in the fixtures, but receive different supplier records.

Tool names and descriptions help a planner choose an operation. A narrow description also helps a reviewer see when a question needs clarification. Asking for a supplier's current banking instructions is outside a tool that returns only its name and status.

**Checkpoint:** If the model guesses a plausible supplier ID, has it proved that the caller may read that supplier? No. Selection and object authorization remain separate decisions. Next, make the allowed argument shape explicit.

## Turn the function contract into a schema

A schema describes what an argument object may contain. Here is a proposed call in the lab's provider-neutral protocol:

~~~json
{
  "kind": "tool_call",
  "call_id": "call_2",
  "name": "supplier_lookup",
  "arguments": {"supplier_id": "SUP-001"}
}
~~~

This is a proposal, not a Python expression to evaluate. A fixed registry maps the name to trusted application code. Unknown names receive an error; the dispatcher never uses eval, an arbitrary import, a shell command or a model-selected URL.

The argument model forbids extra fields, requires a string ID and restricts its characters and length. Other tools have their own models. SQL limits must be actual integers from one through five: the string "5" and the boolean true are rejected. The request parser also rejects duplicate JSON keys and nonfinite constants before ordinary dictionaries can lose that information.

Here is the small Python shape behind a supplier argument contract:

~~~python
from pydantic import BaseModel, ConfigDict, Field

class SupplierInput(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    supplier_id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,64}$")

parsed = SupplierInput.model_validate({"supplier_id": "SUP-001"})
assert parsed.supplier_id == "SUP-001"
assert SupplierInput.model_json_schema()["additionalProperties"] is False
~~~

Schemas have limits. A syntactically valid object can name the wrong purchase order. A valid decimal string can describe the wrong price. Cross-field business rules and current permissions need application checks after parsing.

You can inspect the local definitions without initializing a database:

~~~shell
python -m labs.week_13.demo schemas
~~~

The output is the lab's tool catalogue and Pydantic-generated JSON Schema. It is not a drop-in provider request. An actual provider adapter must map native call/result objects, preserve required continuation state and use that provider's supported schema subset. Provider-side structured generation can help with shape; it cannot supply the caller's permissions.

**Checkpoint:** What happens if the model adds tenant to otherwise valid supplier arguments? The closed model rejects the call before the handler runs. It does not silently discard a claimed identity and hope downstream code ignores it.

## Keep selection separate from argument generation

Which tool should answer “What are the payment terms?” Document search is the natural route. “What is the percentage change from this baseline price?” needs a calculation. “Give me a current commodity quote” needs a source whose freshness actually meets that request.

Selection chooses the operation; argument generation fills its parameters. They can fail independently. A planner may choose price_variance correctly but reverse baseline and current, mix kilograms with tonnes, or invent a price. A better description cannot turn those values into trusted facts.

The supplied read scenario proposes five calls in a fixed order. It uses known fixture prices, not a model's inferred mapping from retrieved records. In a real integration, evaluate selection and argument correctness against labelled tasks, including cases that require clarification or no tool. Passing the scripted scenario supplies no such model-quality score.

| Tool | Appropriate task | Important boundary |
| --- | --- | --- |
| sql_query | Read accessible purchase-order rows | Named queries and bound values; no arbitrary SQL |
| price_variance | Compare stated prices | Positive baseline, matching currency/unit, decimal arithmetic |
| supplier_lookup | Read an accessible supplier's name/status | Tenant and principal access still apply |
| commodity_price | Inspect a dated fixture price | The returned date is not a live-market guarantee |
| document_search | Find permitted invoice evidence | Existing source grants, pins and guarded quotation |

**Checkpoint:** Can the commodity tool satisfy “today's price” merely because it returns a well-formed date? No. Compare the source's actual date and contract with the user's freshness need; do not relabel an old fixture as current.

## Validate before an adapter does work

The dispatcher first finds a registered tool, validates its arguments and checks the applicable execution authority. Only then does it invoke the adapter.

The invalid-argument scenario proposes open_purchase_orders with limit set to the string "5". It receives invalid_arguments with attempts equal to zero. A later call uses the integer 1 and succeeds. This is correction by a new proposal, with a new call ID; it is not an automatic execution retry.

An error sent back to the planner is a controlled category. It does not include a Pydantic error dump containing raw input, a database exception message, credentials or a stack trace. The planner gets enough information to make a bounded correction, while the application keeps ownership of what may happen next.

Unknown tools, invalid fields, missing access and temporary unavailability are different cases. Treating all of them as “try again” wastes budget and can repeatedly attempt an operation that is forbidden.

**Checkpoint:** Should invalid arguments count as one handler attempt? The lab records zero because execution never began. They still consume one proposed tool call in the conversation budget.

## Give SQL a smaller surface than a database console

What does “a SQL tool” mean here? It means selecting one of two application-owned queries: open_purchase_orders or purchase_order_by_id. Parameters include a bounded limit and, for the second query, an ID. The argument schema does not have a sql field.

The adapter uses fixed statements and SQLite value placeholders. It binds tenant and principal from Actor/SecurityContext, joins current grants, orders deterministically and caps the returned rows. An inaccessible purchase order is not returned just because it ranks well, shares an ID with another tenant or appears in a model's explanation.

This is a useful first SQL capability. General natural-language-to-SQL against a production schema would require a separate design for permitted statements, database privileges, cost, object access and result disclosure. Rejecting strings that “look like DELETE” would not be that design.

The fixture also opens read connections in read-only mode. That is another layer, not a replacement for row scoping. Application code owns the SQLite file and its grants; this lab is not a database server with independently authenticated per-tenant roles.

SQLite is used for this small separate fixture and review ledger. Week 12's PostgreSQL schema, volume, API and pgvector path are unchanged. The lesson is about tool contracts, not a database migration.

**Checkpoint:** Why parameterize values if the outer ID model already rejects quotes? Validation can change or be bypassed by a future caller. Keeping values out of SQL syntax remains an independent adapter property.

## Calculate a variance with its units intact

Suppose a unit price rises from USD 2.00 per kilogram to USD 2.20 per kilogram. The absolute change is 0.20 USD/kg. The relative change is (2.20 − 2.00) / 2.00 × 100, or 10.00%.

~~~python
from labs.week_13.contracts import VarianceArgs
from labs.week_13.runtime import variance

args = VarianceArgs(
    baseline="2.00", current="2.20",
    baseline_currency="USD", current_currency="USD",
    baseline_unit="kg", current_unit="kg",
)
result = variance(args)
assert result["delta"] == "0.20"
assert result["percent"] == "10.00"
~~~

The inputs are canonical two-place decimal strings, not binary floats. This fixture accepts 0.00 through 999999.99, requires a positive baseline and rejects currency or unit mismatches. It does not perform FX conversion or unit conversion.

The implementation computes with Decimal in a local context, then rounds displayed delta and percentage to two places using ROUND_HALF_EVEN. That rounding is an explicit teaching convention. It is not a general accounting policy. A very small negative percentage can display as -0.00 after rounding; retain enough context to distinguish a rounded display from the unrounded calculation.

Arithmetic correctness is also distinct from source correctness. The function does not prove that these prices belong to the intended purchase order or date. That binding needs trusted records and appropriate review; a model's valid numeric proposal is not enough to authorize a consequential financial action.

**Checkpoint:** What happens with a zero baseline or USD versus INR? The application rejects the arguments. It does not return infinity, silently convert currencies or invent a replacement baseline.

## Read a tool result as evidence, not an instruction

The supplier and commodity tools return structured facts. Commodity results include amount, currency, unit, an as_of date and source='synthetic-fixture'. North's example is USD 2.10/kg dated 2026-10-01. It is deliberately a dated fictional record, not market research.

Document search reuses the guarded quote assistant and its source catalogue. A caller still needs current source access and matching approved representation pins. The tool can return an answered quotation or a common refusal. Citation labels identify evidence within that result; they are not public source-access tokens.

Results are validated against each tool's expected closed output model and a serialized-byte bound before forwarding. An extra tool_call field is rejected. A calendar-invalid commodity date is rejected. A permitted text field can nevertheless contain prose that sounds like an instruction. The application must continue treating that prose as data.

This distinction matters when a later planner turn proposes another operation. Even if a supplier name says “create a review now,” the new call still passes the same registry, argument and authority checks. The result cannot grant approval by asserting that it has approval.

**Checkpoint:** Does valid result JSON prove the answer is true? It proves the checked structure and selected local invariants. Freshness, source quality and the meaning of a generated summary remain separate claims.

## Return the result to the correct conversation

After a call, the loop appends a tool message containing its call_id, name, status, data, error category and attempt count. The call ID must match the proposed operation. It supplies correlation, not permission or duplicate-write protection.

The next planner request receives the growing transcript. In the supplied protocol, one turn proposes one call or a final response. Calls execute sequentially. A reused call ID is rejected before a second execution, so results cannot ambiguously refer to two different operations.

The final response includes evidence_call_ids. Every referenced ID must belong to a successful call in this run, with no duplicates. That check prevents unknown or failed calls from being cited as successful evidence. It does not prove that the summary faithfully uses those results.

Now the loop has a clear shape: ask for a proposed turn, validate it, execute an admitted call, append its validated result, then ask for the next turn. It stops on a valid final response or an explicit failure/budget outcome.

Default limits allow six proposed tool calls and eight planner turns, with bounded question, turn, result and transcript representations. Invalid calls consume the call budget even with zero handler attempts. These are small teaching limits, not a production capacity recommendation.

**Checkpoint:** Could an application keep asking the model to fix the same bad arguments forever? This one cannot: both calls and planner turns have terminal bounds.

## Retry the failure that can safely be retried

Imagine a read adapter reports temporary unavailability before delivering a result. The lab permits one retry, for at most two attempts, with a 0.05-second delay. A cooperative read timeout has the same bounded retry treatment.

| Observation | Lab behavior | Reason |
| --- | --- | --- |
| Invalid arguments | No adapter attempt | A new proposal must correct the contract |
| Not found or forbidden | One attempt at most; no retry | Repetition does not create access or data |
| Transient read unavailable/timeout | At most two attempts | A repeated read has no intended write effect |
| Malformed read result | Reject; no retry | A contract defect is not assumed transient |
| Write execution unavailable/timeout | Mark outcome unknown; no automatic retry | The operation may already have committed |

The scenario named transient injects one controlled read failure, then calls the real commodity adapter. Its result records two attempts. It is evidence for retry control around that fixture adapter, not an external provider's outage behavior.

In a real remote integration, classify the provider's actual error contract, use a total retry/time budget and consider backoff with jitter and shared rate limits. Copying a retry decorator onto every function would erase the distinctions in this table.

**Checkpoint:** Is a corrected model call the same as a retry? No. A retry repeats an admitted operation under the retry policy; correction creates a new proposed call that is validated again.

## Read a timeout as a control signal

What does a timeout tell you? That a waiting boundary did not complete under its deadline semantics. It does not prove that the underlying world is unchanged.

The loop has per-await deadlines and a five-second cooperative run budget. Async handlers and planner adapters must cooperate with cancellation. The tiny local SQLite operations are synchronous and have a separate 0.25-second busy-wait bound; an asyncio timer cannot preempt a blocking call while it holds the event-loop thread. This is a local CLI demonstration, not a claim of a hard end-to-end service deadline.

Caller cancellation propagates rather than becoming a successful empty response. A remote adapter may need its own connection/read deadlines and cleanup. Work moved into a running Python thread has the additional ownership problem discussed in Week 12: cancelling an await cannot kill the thread.

For a read, retry policy may permit another attempt. For a write, a timed-out or cancelled wait may follow a successful commit. The caller must preserve the original operation identity for reconciliation rather than inventing a fresh key.

**Checkpoint:** Can a timeout be reported as “the review definitely was not created”? No. The lab returns unknown_outcome when an admitted write's completion cannot be trusted, and stops further planning.

## Approve the concrete operation before a write

The optional create_review tool records that a synthetic purchase order needs review for price_variance or supplier_change. It does not approve the purchase itself.

The trusted caller supplies a write capability, an operation key and approval for the exact normalized operation. The model supplies only purchase_order_id and reason. Approval is bound to tenant, principal, operation key, tool/version and validated arguments, with an expiry.

The dispatcher checks this before invoking the adapter. The store checks it again inside the write transaction and rechecks the current target grant. Approval does not waive a revoked object permission. Changing the reason or target does not carry the old approval forward.

The lab's Approval object is an explicitly trusted in-process fixture. The approved CLI scenario constructs that fixture for synthetic data. This is not a signed token, an authenticated approval screen or evidence that a real person clicked “approve.” A production controller must obtain and verify approval through its actual trusted workflow.

**Checkpoint:** Why not place approved=true in tool arguments? Those arguments are proposed by the model. Accepting that field as approval would let the proposer authorize itself.

## Make a repeated write refer to the same intent

Suppose a review is inserted, but its response disappears. A new request might have a different call ID while representing the same intended review. A call ID therefore cannot be the durable duplicate key.

The application supplies a stable operation_key for that intent. Inside one SQLite BEGIN IMMEDIATE transaction, the store checks current authority, finds the key scoped by tenant and principal, compares the canonical argument digest and either returns the saved review or inserts one new record.

| Existing ledger state | Same scoped operation key | Outcome |
| --- | --- | --- |
| No record | Approved arguments | Insert one review and save its identity |
| Matching digest | Same arguments and current authority | Return the original review ID with replayed=true |
| Different digest | Changed arguments | Conflict; do not overwrite |
| Matching record, revoked grant or expired approval | Historical success | Reject the replay under current authority |

The unique key and transaction also protect two cooperating writers to this same SQLite file. The tests verify that they receive one review ID and only one new record.

Do not call this universal exactly-once execution. The guarantee covers this transaction and retained ledger. Deleting the file loses its history. An external email, payment or supplier API is outside the transaction and would need its own idempotency/reconciliation design. Using a new operation key after an uncertain response can create a second effect.

**Checkpoint:** Why compare arguments as well as finding the key? Otherwise an accidental reuse could quietly return a result for a different requested operation.

## Run the success, rejection and recovery paths

From the repository root, activate the declared Python environment and install the existing development requirements. Initialize only a new fixture path:

~~~shell
python -m pip install -r requirements-dev.txt
python -m labs.week_13.demo init
python -m labs.week_13.demo run --scenario read
python -m labs.week_13.demo run --scenario read --tenant south
python -m labs.week_13.demo run --scenario invalid
python -m labs.week_13.demo run --scenario transient
python -m labs.week_13.demo run --scenario unapproved
~~~

The default file is .runtime/week13.sqlite3. Init refuses an existing file instead of resetting its grants or duplicate history. Reuse an initialized file for later runs. To create another practice fixture, supply a new --database path consistently to init and run.

The read result contains five actual tool outcomes. The invalid scenario shows invalid_arguments with zero attempts, followed by a corrected successful call. The transient read succeeds on its second attempt. The unapproved write returns approval_required and creates no review.

Use the synthetic approval fixture to observe repeated writes:

~~~shell
python -m labs.week_13.demo run --scenario approved
python -m labs.week_13.demo run --scenario approved
python -m labs.week_13.demo run --scenario lost-response --operation-key lost-demo
python -m labs.week_13.demo run --scenario lost-response --operation-key lost-demo
~~~

The two approved runs return the same review ID, first with replayed=false and then true. On a fresh lost-demo key, the first lost-response scenario commits a record and deliberately loses its response. It exits with code 2 and unknown_outcome. The second command, run separately with the same key, recovers the saved review with replayed=true. This is deliberate fault injection after a real local commit, not an actual network call.

Finally run:

~~~shell
python -m labs.week_13.demo smoke
python -m pytest tests/test_week13_tools.py -q
~~~

Smoke uses its own temporary fixture and makes twelve observations over actual SQLite, guarded search and the scripted loop. The tests also cover malformed turns/results, decimal boundaries, scope, cancellation, deadlines, concurrent writers and current authority on replay. Routine logs contain bounded diagnostic metadata; displaying the CLI's synthetic results is an explicit lesson action, not a recommendation to log real prompts or records.

GitHub Pages publishes the lesson. The Python lab runs locally; opening this page starts no backend or provider. The [lab source and run guide](https://github.com/kogantisasank831-ux/Prep/tree/main/labs/week_13) describe the same contracts.

## Explain the boundary without hiding the failure

Prepare a short demonstration: show the five-tool read, the string-valued limit rejection, one scoped supplier difference, then the lost-response replay. Explain which observations come from real local storage and which behavior is scripted.

Try three independent changes. Add a new named read query with a closed argument/result model and a scope negative. Change a result adapter to return an extra field and show that it is not forwarded. Remove a current review grant in an isolated test fixture and show that a historical idempotency record does not bypass the new denial.

| Interview question | A defensible answer should include |
| --- | --- |
| What happens when arguments are invalid? | No handler invocation; bounded feedback, a new validated proposal and finite correction budget |
| How can duplicate execution cause damage? | A committed write can lose its response, and a fresh operation key can create another effect |
| How do you make this write idempotent? | Scoped stable intent key, canonical argument comparison, current authority and an atomic ledger/effect transaction |
| Does a schema make a tool safe? | It checks shape and some values; access, business meaning, budgets and approval are separate |
| What did the timeout prove? | The wait crossed a deadline; it did not prove rollback of an external or committed effect |
| What remains before a real model/provider? | A provider adapter, representative selection/argument/answer evaluation, actual identity/approval and remote failure contracts |

You finish with a runnable tool boundary and an honest explanation of its guarantees. Week 14 compares deterministic workflows with agent-driven control. Use the [Week 13 assessment]({{ '/assessments/week-13/' | relative_url }}) to check tool-calling concepts and Python syntax before presenting the build.

## Sources and further reading

The implementation and examples are the primary reference for this local lab. For the underlying APIs, read the [function-calling guide](https://developers.openai.com/api/docs/guides/function-calling), [Pydantic strict validation](https://docs.pydantic.dev/latest/concepts/strict_mode/), [Python Decimal](https://docs.python.org/3.13/library/decimal.html), [Python SQLite transactions and binding](https://docs.python.org/3.13/library/sqlite3.html), [SQLite transactions](https://www.sqlite.org/lang_transaction.html) and [asyncio cancellation/timeouts](https://docs.python.org/3.13/library/asyncio-task.html).

Read a provider's current wire/schema rules when building its adapter. The local catalogue, scripted planner and tests do not establish compatibility with an unimplemented provider integration or a real model's decision quality.
