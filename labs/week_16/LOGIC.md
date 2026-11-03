# Week 16 memory and context engineering contracts — revision 2

Source: `Path.md` Week 16 and the Week 15 checkpointed procurement report. These
rules describe a local synthetic teaching store. They are not a production
procurement system, identity service or authorization policy.

| ID | Effective rule and acceptance |
| --- | --- |
| W16-BR1 | Retain one case-level snapshot containing the investigation objective, selected supplier, document and SQL evidence references, exact calculation and approval status. A memory record supports future threads; it never grants authority to approve, order, contact or pay. |
| W16-FR1 | Separate current semantic memory from ordered episodic memory. The semantic row is the current selected case snapshot. Episodes are compact facts about objective, supplier, evidence, calculation and approval transitions; they are not copied chat turns. |
| W16-FR2 | Never accept or store raw conversation, message history or evidence bodies. Store source identifiers and SHA-256 content/report digests so a caller can re-fetch and verify governed evidence. The current turn question is transient. |
| W16-FR3 | Assemble context only after an authorized case read. Always include the deterministic semantic summary, revision, expiry and report digest; rank compact episodes against the current question and pack only complete entries within a hard 640–4,000 character budget. Recalled data is labelled for verification before consequential use. |
| W16-FR4 | Give each case an explicit UTC expiry no more than 90 days after observation. Expired records are hidden from recall and context, can be purged with their episodes, and can be explicitly forgotten before expiry. |
| W16-FR5 | Prevent silent incorrect-memory replacement with closed strict schemas, required document and SQL provenance, UTC/future checks, deterministic digests, idempotent replay, compare-and-set revisions and immutable investigation facts. Only `awaiting_approval` may transition once to `approved` or `rejected`. |
| W16-DR1 | Use a private schema-versioned SQLite file with parameterized values, tenant/case keys, foreign-key cascade and explicit transactions. `AccessScope` is supplied by a trusted host and checked on every operation; its identifiers are not credentials. |
| W16-DR2 | Use only dated fictional Week 15-derived fixtures. Preserve decimal display, currency/unit, reference date, rounding rule, source run ID and report digest. Add no provider, model, API key, network call, vector store or hosted backend. |
| W16-NFR1 | Context selection and summarisation are deterministic and independently testable. Re-opening the store in another Python process must preserve retained memory. Exact duplicate writes must not create another revision or episode. |
| W16-NFR2 | Create a new store with mode `0600` and refuse overwrite. Treat file permissions as one local safeguard, not encryption. Production work still needs authenticated identity, policy enforcement, encryption, migration, backup, concurrency, deletion evidence and operating ownership. |
| W16-ENG1 | Use the pinned project Pydantic and Python standard-library SQLite APIs only. Keep strict contracts in `models.py`, selection in `context.py`, durable lifecycle operations in `memory.py`, synthetic facts in `fixtures.py` and demonstrations in `demo.py`. |
| W16-ER1 | Test private initialization, schema version, restart persistence, data minimization, tenant/case scope, idempotency, revisions, approval transitions, immutable facts, time validation, bounded relevance, transient questions, expiry cascade, explicit forgetting, strict schemas, deterministic digest and cross-process CLI behavior. Run Ruff, format, strict mypy, the configured regression suite and CLI smoke before publication. |
| W16-AS1 | Publish a 100-item practice bank with 30 single-choice, 20 multiple-correct, 15 matching, 15 short-answer and 20 self-contained Python coding questions. Every generated 10-question paper contains exactly two of each type for 100 marks. Each coding task has five executable checks, its reference passes all five, its starter scores zero and a distinct plausible wrong implementation loses marks. |

Accepted engineering choices: SQLite demonstrates durable cross-process memory
without adding a service. One current semantic row plus compact episodes makes
the difference between “what is true now” and “what happened” inspectable.
Keyword overlap is a transparent selection baseline, not a claim of semantic
search quality. Deterministic summaries avoid introducing an unmeasured model
into a memory-correctness lesson. The browser assessment uses small independent
standard-library transformations; durable SQLite behavior remains in the lab.

Automated fact extraction from arbitrary dialogue, vector similarity, memory
consolidation, conflict arbitration between independent investigators, legal-hold
retention, production encryption and real identity/authorization are intentionally
out of scope. Their absence prevents a production-readiness claim but does not
block the roadmap’s case-memory and context-selection outcomes.
