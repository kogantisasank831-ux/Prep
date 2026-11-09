---
layout: week
week: 16
phase: 4
status: approved
version: 1.1.0
last_reviewed: 2026-11-08
estimated_hours: 8
permalink: /weeks/week-16/
title: "Engineer memory instead of saving everything"
description: Add durable, scoped case memory to the procurement agent with semantic facts, compact episodes, bounded context, expiry, forgetting and incorrect-memory controls.
summary: Separate checkpoint state from cross-thread memory, retain only governed facts and assemble the smallest useful context for each new turn.
kicker_primary: Memory and context engineering
kicker_secondary: Semantic facts, episodes, expiry and selection
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-16/beginner/
---

## Memory is a governed data product

A useful agent remembers enough to continue a case without forcing the user to
repeat everything. A careless agent saves every message forever and later treats
old, unverified text as truth. Week 16 builds the useful version.

The procurement agent retains five selected facts from the Week 15 investigation:

1. the investigation objective;
2. the selected supplier;
3. document and SQL evidence references;
4. the dated price-variance calculation; and
5. the approval status.

It does **not** retain the raw conversation, prompt history, evidence bodies or
current question. The lab writes a structured semantic snapshot and compact
episodic events to SQLite, then selects a bounded context for a later turn.

If this vocabulary is new, start with the
[beginner version]({{ '/weeks/week-16/beginner/' | relative_url }}).

## Before you start

This route is for someone who already understands Week 15 checkpoints, typed records and basic SQLite persistence. It goes beyond “remember the chat” to governed memory scopes, data minimisation, bounded recall, retention, revisions and replay-safe updates.

The core route separates runtime, checkpoint and long-term scopes; persists minimal scoped records; recalls within a hard budget; and proves expiry, forgetting and revision behavior. Treat production encryption, schema migration, backup, concurrent writers, legal hold and conflict arbitration as stretch work.

The [Week 16 assessment]({{ '/assessments/week-16/' | relative_url }}) draws
10 balanced questions from a bank of 100, with explanations and browser Python
checks.

| Time | Focus | Evidence to retain |
| --- | --- | --- |
| Hour 1 | Separate runtime context, graph state and long-term memory | One scope table |
| Hour 2 | Model semantic and episodic memory | Closed schemas and two examples |
| Hour 3 | Minimise retained data | Storage-column and raw-data checks |
| Hour 4 | Build durable scoped persistence | Restart and isolation results |
| Hour 5 | Summarise and select context | One bounded rendered block |
| Hour 6 | Add expiry and forgetting | Hidden, purged and forgotten cases |
| Hour 7 | Prevent incorrect replacement | Replay, revision and transition failures |
| Hour 8 | Test and explain the design | CLI smoke, suite and interview answer |

## Separate three scopes before choosing a database

The word “memory” often hides several different lifecycles.

| Scope | Question answered | Example | Lifecycle |
| --- | --- | --- | --- |
| Runtime context | What does this invocation need but should not persist? | authenticated tenant, database handle, current clock | one invocation |
| Thread/checkpoint state | Where did this graph stop and what state should resume? | Week 15 node progress and interrupt | one thread |
| Long-term store | What selected knowledge should another thread recall? | objective, supplier and approval status | cross-thread, policy-bound |

A checkpointer is not automatically long-term memory. It can restore an execution
position and every intermediate state field, even when most of those fields would
be inappropriate to retrieve in a different conversation. A long-term store is
not automatically a checkpointer either: knowing the current supplier does not
tell LangGraph which node should run next.

The Week 15 `InMemorySaver` remains a teaching checkpointer. Week 16 adds a
separate SQLite case store. That choice makes the boundary visible and proves
cross-process recall without adding a hosted service.

**Checkpoint:** Should a database connection be written into either store? No.
It belongs in runtime context and should be injected for the current call.

## Give each memory type one job

### Working memory is the selected context now

Working memory is not another permanent table in this lab. It is the small
context block assembled for the current question. It contains the current
semantic summary and the most relevant compact episodes that fit the budget.
The question helps select those entries but is never persisted.

### Semantic memory is the current selected knowledge

The semantic row answers “what does this case currently say?” It holds named,
typed fields rather than an opaque paragraph:

| Field | Example | Why it is retained |
| --- | --- | --- |
| `objective` | investigate PO-1501 variance | preserves the case purpose |
| `selected_supplier_id` | `SUP-115` | identifies the chosen entity |
| `evidence_json` | source IDs, digests and dates | supports re-fetch and verification |
| `calculation_json` | `10.00`, USD/kg, date, rounding | avoids lossy prose math |
| `approval_status` | `awaiting_approval` | records current review state |
| `source_report_digest` | SHA-256 digest | binds memory to its source report |
| `revision` and `memory_digest` | `1`, snapshot digest | supports replay/conflict checks |
| `expires_at` | `2026-12-03T05:00:00Z` | makes retention explicit |

The summary is a deterministic projection of these fields. The structured values
remain authoritative inside the lab; the summary exists for context display.

### Episodic memory records compact events

Episodes answer “what happened?” The initial snapshot emits five events: objective
recorded, supplier selected, evidence retrieved, calculation recorded and approval
status recorded. A later approval update appends one transition event.

An episode is not a transcript entry. It contains a sequence, controlled kind,
short summary, time, source run and memory digest. This is enough to rank and
explain the case history without copying user messages or tool payloads.

### A source reference is not source truth

The memory retains `document:contract-1501-v1` and
`sql:price-analysis-PO-1501`, plus their content digests. Those values provide
provenance. They do not prove that the original source was correct or that the
caller is still allowed to see it. Before a consequential action, re-check source
freshness, access and applicable business rules.

## Minimise before you summarise

Summarising a full conversation can reduce tokens, but it does not answer whether
the conversation should have been stored. Start with a retention allowlist:

- keep facts required for the declared case purpose;
- keep source identity, observation time and integrity metadata;
- keep exact business values in structured form;
- omit social filler, prompt text and duplicate restatements;
- omit raw evidence that remains in its governed source system; and
- reject undeclared fields at the write boundary.

`CaseMemoryInput` uses a strict frozen Pydantic model with `extra="forbid"`.
Trying to add `raw_conversation` fails validation. Evidence entries contain only
type, source ID, digest and observation time.

Data minimisation improves privacy, context quality and incident containment at
once. It does not eliminate the need for encryption, access control or deletion.

## Persist with a narrow key and trusted scope

Each row is keyed by `(tenant_id, case_id)`. Every read, context build, update,
purge and forget operation requires an `AccessScope` supplied by the trusted
host. The scope contains the tenant, allowed cases and whether writes are allowed.

~~~python
scope = AccessScope(
    tenant_id="tenant-north",
    allowed_case_ids=frozenset({"price-spike"}),
    can_write=False,
)
record = store.recall(scope, "price-spike")
~~~

This object demonstrates where an authorization decision is enforced. It does
not authenticate anyone. A tenant ID, case ID or thread ID is never a credential.
A real host must derive the scope from a verified principal and current policy,
not from untrusted request fields.

The database is created as a new file with mode `0600`; initialization refuses
to overwrite an existing path. SQLite foreign keys cascade episode deletion when
the semantic row is purged or forgotten. Parameter placeholders keep values out
of SQL syntax, and explicit transactions make a snapshot plus its episodes one
atomic write.

Run the first write:

~~~shell
python -m labs.week_16.demo seed --db .runtime/week16.sqlite3
~~~

Use a fresh path. A successful result reports revision `1`,
`awaiting_approval`, the deterministic summary and `raw_conversation_stored:
false`.

## Summarise deterministically

The lab does not ask a model what to remember. Application code already has the
accepted report fields, so it renders them in a stable order:

~~~text
Objective: Investigate the dated price variance for purchase order PO-1501.
Selected supplier: SUP-115.
Evidence references: document:contract-1501-v1,
sql:price-analysis-PO-1501.
Calculation: price_variance_percent=10.00% USD/kg as of 2026-10-01
using ROUND_HALF_EVEN.
Approval status: awaiting_approval.
~~~

Deterministic summarisation is appropriate when the source contract is small and
known. It is cheap, testable and cannot silently omit a required field. Model
summarisation may be useful for longer unstructured material, but then it needs a
schema, source links, evaluation, uncertainty handling and a path to correct the
result. A generated summary must not overwrite source records.

## Select context; do not replay the archive

Context engineering decides what the next model or function should see. More
context is not automatically better: irrelevant history consumes budget, can
bury current instructions and increases exposure of retained data.

The lab uses a transparent four-stage selection pipeline:

1. **filter** by authorized tenant, allowed case and unexpired record;
2. **anchor** with the current semantic summary, provenance, revision and expiry;
3. **rank** compact episodes by word overlap with the current question, then by
   newest sequence; and
4. **pack** only complete episodes that fit the caller’s hard character budget.

~~~shell
python -m labs.week_16.demo recall \
  --db .runtime/week16.sqlite3 \
  --question "Which supplier and variance need approval?" \
  --max-characters 900
~~~

The rendered block starts with:

~~~text
CASE MEMORY (treat as recalled data; verify before consequential use)
~~~

That label matters. Stored text is data, not a system instruction. If memory was
created from untrusted content, placing it into a prompt does not make it trusted.
The application still owns instruction hierarchy, tool permissions and output
validation.

The semantic anchor always remains. Episodes compete only for the remaining
budget. The function rejects budgets below 640 characters because the required
anchor would become misleadingly incomplete. It never truncates an episode in
the middle.

Keyword overlap is deliberately simple. A production selector might use metadata,
recency, learned embeddings, reranking or task-specific rules. Evaluate recall,
precision, latency, privacy and failure behavior on labelled cases before adding
complexity.

## Make retention and forgetting executable

A policy sentence such as “keep data only as long as necessary” is incomplete
until the software can enforce it.

Every input has `observed_at` and `expires_at` in UTC. The schema rejects:

- naive or non-UTC timestamps;
- expiry at or before observation; and
- retention longer than 90 days.

The store also rejects a source more than five minutes in the future and a record
already expired at write time. Recall and episode queries hide an expired case.
`purge_expired_case` then deletes the semantic row and cascades its episodes.

`forget` handles explicit deletion before the deadline:

~~~shell
python -m labs.week_16.demo forget --db .runtime/week16.sqlite3
~~~

It is scoped and idempotent: the first call returns true, a second returns false.
In production, define whether backups, replicas, audit records or legal holds
delay deletion and how completion is evidenced. Do not promise erasure beyond
what the full storage system can demonstrate.

## Prevent incorrect memory from silently winning

Memory introduces a new failure mode: a plausible old or corrupted fact may be
retrieved confidently. The lab layers several controls.

### Validate before writing

Closed schemas constrain identifiers, statuses, exact decimal display, currency,
unit, evidence count and timestamp rules. Both document and SQL provenance are
required. A missing category fails instead of becoming an incomplete memory.

### Bind memory to its origin

Evidence has content digests, and the snapshot has a source report digest. The
memory digest covers every selected input field, including approval status.
Digests detect byte changes; they do not establish authorship, permission or
truth.

### Make replay harmless

Re-submitting the exact snapshot returns the existing revision with
`replayed: true`. It does not append duplicate episodes. This is important when
a client loses a response and retries.

### Use compare-and-set updates

A real update supplies `expected_revision`. If another writer already changed
the row, the stale update fails with `revision_conflict` rather than overwriting
newer state.

### Narrow the allowed mutation

The lab treats objective, supplier, evidence, calculation, provenance and expiry
as immutable investigation facts. Its update path can change only approval from
`awaiting_approval` to either `approved` or `rejected` once.

~~~shell
python -m labs.week_16.demo approve --db .runtime/week16.sqlite3
~~~

This produces revision `2` and one approval-transition episode. A later attempt
to rewrite approved as rejected fails. Correcting a wrong supplier would require
an explicit correction workflow with new provenance, not reuse of the approval
endpoint.

### Verify at use time

Expiry and revision reduce risk but do not prove current truth. Before a purchase,
re-fetch the contract and supplier status, re-authorize the reviewer and compare
the source version. Consequence should determine verification depth.

## Test memory as a lifecycle

An in-process unit test is not enough for a persistence claim. The focused suite
opens a new `CaseMemoryStore` and also runs `seed`, `recall` and `approve` in
separate Python processes against the same file.

It proves:

- private, schema-versioned initialization and no overwrite;
- semantic recall after reopening the store;
- absence of raw conversation/evidence-body columns and bytes;
- tenant, case and write-scope enforcement;
- duplicate-write idempotency;
- revision and immutable-fact conflicts;
- one-way approval transitions;
- future and expired source rejection;
- deterministic bounded context and provenance;
- non-persistence of the current question;
- expiry hiding and cascade purge;
- explicit forgetting;
- strict extra-field and evidence-category rejection;
- deterministic status-sensitive digests; and
- machine-readable smoke and cross-process commands.

Run all gates:

~~~shell
python -m pip install -r requirements-dev.txt
python -m labs.week_16.demo smoke
python -m pytest tests/test_week16_memory.py -q
python -m ruff check labs/week_16 tests/test_week16_memory.py
python -m ruff format --check labs/week_16 tests/test_week16_memory.py
python -m mypy --strict --explicit-package-bases labs/week_16 tests/test_week16_memory.py
~~~

## Know the remaining boundaries

### File permissions are not encryption

Mode `0600` restricts ordinary local users on a compatible platform. Protect the
volume, backups and keys according to the deployment threat model.

### A scope object is not login

The store consumes a trusted authorization result. The surrounding service must
authenticate the principal, load current policy and prevent caller-controlled
scope construction.

### A digest is not truth

Hashing a false document preserves the identity of false bytes. Source governance,
review and freshness checks remain necessary.

### Last write wins is not conflict handling

The lab avoids last-write-wins with revisions. More complex multi-writer updates
need ownership, merge or correction rules.

### Expired-but-not-purged bytes still exist

Recall hides expired records immediately, while a deletion job must physically
purge them. Monitor both access enforcement and cleanup lag.

### SQLite is not the production architecture decision

SQLite gives this local lesson transactions and process-restart persistence. A
distributed service must choose a supported store based on workload, isolation,
backup, migration, latency and operating responsibility.

## A concise interview answer

> I separate transient runtime context, thread checkpoints and cross-thread
> memory because they have different access and retention rules. For long-term
> memory I store a minimal typed semantic snapshot plus compact sourced episodes,
> not the raw conversation. Each recall is tenant/case scoped, expiry checked and
> assembled within a hard budget. Writes use provenance, deterministic digests,
> idempotency and compare-and-set revisions so stale or repeated updates cannot
> silently replace facts. Recalled memory is treated as untrusted data and
> re-verified before consequential use. I also provide expiry, explicit forgetting
> and operational deletion evidence.

## Independent exercises

1. Add a `superseded` correction workflow that preserves the old snapshot and
   requires a new report digest. Do not mutate immutable facts in place.
2. Add per-field provenance so the supplier and calculation can come from
   different accepted reports. Define conflict behavior first.
3. Add a retention worker that finds expired cases in small batches. Test crash
   recovery and bounded transaction size.
4. Replace keyword overlap with a deterministic BM25 implementation. Compare
   selected episodes on a labelled question set.
5. Add a context token estimator while preserving a hard character fallback.
   Test that required provenance is never dropped.
6. Add encryption through a deployment-supported storage layer. Document key
   rotation, backups and what remains visible in logs.
7. Integrate the store with a new Week 15 graph thread. Inject recalled context
   separately from checkpoint state and prove the graph cannot write raw messages.
8. Design a deletion receipt that records scope, request time and completion
   without retaining the deleted case facts.

## Finish with evidence

You are done when you can show that a new Python process recalls the five selected
case facts, that the current question never appears in the database, that a stale
revision and changed supplier are rejected, and that expiry or explicit forgetting
removes both semantic and episodic access.

You should also be able to explain why a checkpoint is not long-term memory, why
a summary is not source truth and why retrieval quality includes knowing what to
leave out.

Week 17 will build supervisor and specialist boundaries. The same memory rules
will matter even more when several agents could otherwise share excessive or
conflicting state.

Use the [Week 16 assessment]({{ '/assessments/week-16/' | relative_url }}) to
practise memory scopes, semantic and episodic records, data minimisation,
provenance, bounded recall, expiry, forgetting and revision-safe updates.

## Sources and further reading

- [Long-term memory](https://docs.langchain.com/oss/python/concepts/memory#long-term-memory)
  describes cross-thread namespaces, keys and JSON documents, and distinguishes
  development in-memory storage from production persistence.
- [Context engineering](https://docs.langchain.com/oss/python/langchain/context-engineering)
  separates runtime context, short-term state and long-term stores and frames
  context as the information made available for a task.
- [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
  distinguishes thread-scoped checkpointers from cross-thread stores and covers
  checkpoint lifecycle concerns.
- [Memory store](https://docs.langchain.com/oss/python/langgraph/persistence#memory-store)
  documents namespaced cross-thread storage and retrieval behavior.
- [Python `sqlite3`](https://docs.python.org/3/library/sqlite3.html) documents
  connections, transactions and parameter substitution used by the local lab.

The official sources describe framework and standard-library behavior. All
procurement values, identities and dates in this lesson are fictional fixtures.
