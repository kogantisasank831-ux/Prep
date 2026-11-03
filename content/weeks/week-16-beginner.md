---
layout: week
week: 16
phase: 4
status: approved
version: 1.0.1
last_reviewed: 2026-11-03
estimated_hours: 8
permalink: /weeks/week-16/beginner/
title: "Give the agent a careful case notebook"
description: Learn working, semantic and episodic memory by saving a few useful procurement facts while leaving raw conversation out.
summary: Treat memory as a small, labelled case notebook with a lock, an expiry date and a rule for what may be written.
kicker_primary: Beginner path
kicker_secondary: Remember less, recall better
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-16/
---

## Think of a controlled case notebook

Imagine a procurement analyst starts a case on Monday and another analyst
continues it on Wednesday. The second analyst needs the objective, supplier,
evidence, calculation and approval status. They do not need every greeting,
typing mistake or repeated sentence from Monday’s conversation.

That is the Week 16 idea: give the agent a small controlled case notebook.

The notebook has:

- named fields instead of a pile of messages;
- source labels for important facts;
- a current summary;
- a short event history;
- a tenant and case boundary;
- an expiry date; and
- a way to forget the case.

The [production version]({{ '/weeks/week-16/' | relative_url }}) explains the
schemas, transactions, context budget and incorrect-memory controls in more depth.

The [Week 16 assessment]({{ '/assessments/week-16/' | relative_url }}) draws
10 balanced questions from a bank of 100, with explanations and browser Python
checks.

## Learn the four memory words

| Term | Plain meaning | Week 16 example |
| --- | --- | --- |
| Conversation state | information in the current exchange | today’s question |
| Working memory | the small selection needed right now | summary plus relevant events |
| Semantic memory | the current facts we chose to retain | supplier `SUP-115`, variance `10.00%` |
| Episodic memory | compact notes about what happened | “approval status changed to approved” |

Long-term memory means the semantic facts and episodes can be recalled by a
future conversation. It does not mean “keep everything forever.”

## A checkpoint and a notebook are different

Week 15 saved graph checkpoints. A checkpoint is like a bookmark inside a
process: it remembers which workstation the case reached and what state is needed
to resume that thread.

The Week 16 notebook answers a different question: what selected case knowledge
should a new thread know?

| Object | Like | Main purpose |
| --- | --- | --- |
| Checkpoint | bookmark | resume the same graph execution |
| Case memory | notebook | recall selected facts in another thread |
| Runtime context | desk key | provide temporary resources and caller scope |

Do not put a database connection or password in the notebook. Those values belong
to the current runtime and should disappear when the call finishes.

## See exactly what is saved

The fictional `price-spike` case saves:

~~~text
objective: investigate the dated variance for PO-1501
supplier: SUP-115
evidence: contract-1501-v1 and price-analysis-PO-1501
calculation: 10.00% USD/kg as of 2026-10-01
approval: awaiting_approval
~~~

It also saves source digests, the report digest, a revision and the expiry time.
A digest is a fingerprint of bytes. If the bytes change, the fingerprint changes.
It is useful for detecting a mismatch, but it does not prove the facts are true
or identify who wrote them.

The lab does not save:

- raw chat messages;
- the user’s current question;
- contract text;
- SQL result bodies;
- prompts; or
- unlimited history.

Evidence stays in its source system. Memory stores a reference and fingerprint so
the application knows what to re-fetch and verify later.

## Create the notebook

From the repository root, install the declared development environment:

~~~shell
python -m pip install -r requirements-dev.txt
~~~

Then create one new SQLite file:

~~~shell
python -m labs.week_16.demo seed --db .runtime/week16.sqlite3
~~~

The command refuses to replace an existing file. This protects an earlier
experiment from accidental overwrite. Choose another path if you want to start
again.

The JSON output should show:

- case `price-spike`;
- revision `1`;
- status `awaiting_approval`;
- expiry on 2026-12-03; and
- `raw_conversation_stored: false`.

SQLite writes the file to disk, so a later Python process can open the same
notebook. That is different from Week 15’s `InMemorySaver`, which disappears when
its Python process exits.

## Semantic memory says what we know now

The lab keeps one current semantic row per tenant and case. Its summary looks
like this:

~~~text
Objective: Investigate the dated price variance for purchase order PO-1501.
Selected supplier: SUP-115.
Evidence references: document:contract-1501-v1,
sql:price-analysis-PO-1501.
Calculation: price_variance_percent=10.00% USD/kg as of 2026-10-01.
Approval status: awaiting_approval.
~~~

Application code creates this summary in a fixed order. No model guesses what to
include. The exact values also stay in separate typed fields, so the summary is
not the only copy of the calculation.

## Episodic memory says what happened

When the case is first saved, the lab records five small events:

1. objective recorded;
2. supplier selected;
3. evidence references retained;
4. calculation recorded; and
5. approval status recorded.

When approval changes, it adds one more event. These are useful timeline notes,
not copied conversation turns.

Why not save every message as an event? Because a transcript mixes instructions,
questions, guesses, corrections and facts. It also grows without a clear limit.
The application should decide which facts meet the memory contract.

## Recall only what helps the current question

Try a new question:

~~~shell
python -m labs.week_16.demo recall \
  --db .runtime/week16.sqlite3 \
  --question "Which supplier and price variance need approval?" \
  --max-characters 900
~~~

The current question is used only to rank the small event notes. Words such as
“supplier,” “price,” “variance” and “approval” move matching events toward the
front.

The output always includes the current summary, source report digest, revision
and expiry. It then adds complete events while they fit the budget. It does not
cut an event halfway through.

This is context selection. The goal is not to show everything the system has ever
stored. The goal is to show the smallest useful, authorized and current context
for this task.

The context begins with a warning that recalled memory is data and should be
verified before consequential use. A sentence found in memory cannot give itself
system authority or tool permission.

## Scope the notebook before reading it

The same case ID could exist for different tenants. The database therefore uses
both tenant and case as its key. Every operation receives a scope saying which
tenant and case the trusted host has allowed.

This is not a login system. A caller must not be allowed to invent its own scope.
In a real service:

1. authenticate the person or service;
2. load current permissions;
3. build the trusted scope; and
4. let the memory store enforce it.

An ID tells the program which record to seek. It does not prove permission to
read that record.

## Stop repeated or stale writes

Networks fail. A client may save a record successfully, miss the response and
try the same request again. The lab recognizes the exact same memory digest and
returns the existing revision. It does not add another copy of every event.

For a real change, the client must provide the revision it read. If the database
has moved to a newer revision, the write fails instead of silently overwriting
someone else’s work.

The example also locks the investigation facts. Its update path can change only
approval status:

~~~shell
python -m labs.week_16.demo approve --db .runtime/week16.sqlite3
~~~

The row becomes revision `2` and one new event says the status changed from
waiting to approved. It cannot later be flipped to rejected through this method.

If the supplier itself was wrong, use a visible correction process with new
evidence. Quietly editing history would make the memory hard to trust.

## Expire and forget

Memory needs an end date. The fixture was observed on 2026-11-03 and expires on
2026-12-03. After expiry, recall returns nothing. A purge operation can then
delete both the current row and all its event notes.

The lab also supports an explicit forget request:

~~~shell
python -m labs.week_16.demo forget --db .runtime/week16.sqlite3
~~~

The first call removes the case. Calling it again safely reports that nothing was
removed.

A real deletion policy must also cover replicas, backups, logs and legal holds.
The application should say exactly what it can delete and how completion is
checked.

## Avoid these beginner mistakes

1. **Calling all stored state memory.** A graph checkpoint, case record and
   temporary runtime resource have different jobs.
2. **Saving every message.** Decide which typed facts support the case purpose.
3. **Trusting a summary as a source.** Keep provenance and re-fetch important
   evidence.
4. **Using an ID as permission.** Authenticate first and enforce tenant/case
   scope on every operation.
5. **Letting the newest write silently win.** Use revisions and visible conflict
   handling.
6. **Keeping memory forever.** Set expiry, hide expired records and run deletion.
7. **Truncating context blindly.** Keep required provenance and add only complete
   optional entries that fit.
8. **Treating a digest as a signature.** It detects changed bytes but does not
   prove identity or truth.

## Run the tests

~~~shell
python -m labs.week_16.demo smoke
python -m pytest tests/test_week16_memory.py -q
~~~

The tests check persistence in a new process, raw-data minimisation, tenant/case
scope, retries, revisions, approval rules, context size, transient questions,
expiry, forgetting and strict input schemas.

The smoke command creates a temporary notebook, writes the first snapshot,
replays it, recalls context, approves the case, reopens the store, checks expiry
and purges it. It does not leave a database behind.

## Practice questions

1. What is the difference between working and long-term memory?
2. What does semantic memory store in this case?
3. What does episodic memory store?
4. Why is a graph checkpoint not the same as case memory?
5. Why are source IDs and digests stored instead of evidence bodies?
6. Why is the current question not written to the database?
7. What does the context budget protect?
8. Why must the trusted host build `AccessScope`?
9. What happens when the exact same write is retried?
10. Why does a new update need the current revision?
11. What happens after expiry?
12. Why must important facts be checked again before a purchase?

You are ready when you can reopen the SQLite file in another process, explain
every saved field, show that the question was not stored and remove the case on
request.

Week 17 will introduce supervisors and specialist agents. A careful shared
notebook will help them coordinate without giving every agent every message.

Try the [Week 16 assessment]({{ '/assessments/week-16/' | relative_url }}) for a
random paper covering careful case memory, source labels, expiry, forgetting and
the difference between saved knowledge and current context.

## Read alongside the lab

- [Long-term memory](https://docs.langchain.com/oss/python/concepts/memory#long-term-memory)
  explains cross-thread storage and namespaced records.
- [Context engineering](https://docs.langchain.com/oss/python/langchain/context-engineering)
  separates runtime context, state and long-term stores.
- [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
  explains the difference between checkpointers and stores.
- [Python `sqlite3`](https://docs.python.org/3/library/sqlite3.html) explains the
  local database used by the lab.

These sources explain software behavior. The procurement case, supplier, prices
and dates are fictional teaching fixtures.
