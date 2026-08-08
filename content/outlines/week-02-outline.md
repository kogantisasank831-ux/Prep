---
week: 2
phase: 1
title: SQL and data modelling
status: draft
version: 0.1.0
estimated_hours: 18-24
database: PostgreSQL 18.4
runtime: Podman
---

# Week 2 outline: SQL and data modelling

## Objective

Build a defensible procurement database and use it to answer one connected set
of questions: what was ordered, what did it cost, what arrived, what is late,
and which suppliers are reliably meeting agreed terms?

The lesson begins with the meaning and grain of a row, then introduces SQL
constructs as the questions become more demanding. It must not read as a list of
unrelated syntax features.

## Approved decisions

- Use PostgreSQL 18.4 in a rootless Podman machine as the reference runtime.
- Pin the Docker Official Image tag and immutable Linux/AMD64 digest:
  `docker.io/library/postgres:18.4@sha256:4cc13dede823cab4e05290c7fb3350fb4e599ecabd9b07e6706b5d5e8f5bc929`.
  Verified local image ID:
  `4b87d5343a0e499eea33b6c19ec152a3ed4a0d1a453eadd26ff415a406821a6e`.
- Use a normalized nine-table operational model. The six business concepts in
  `Path.md` remain visible, with line-item tables added where the cardinality
  requires them.
- Use only synthetic procurement data.
- Treat spend as committed purchase-order value. Invoices, payments, tax, FX,
  and accounting recognition are outside this week.
- Require explicit reporting cutoffs. Reproducible analytical queries must not
  depend on the machine clock.
- Keep SQL semantics distinct from PostgreSQL-specific syntax and planner
  behavior.

## Prerequisites

- Week 1 Python foundations are useful for the optional verification harness,
  but the SQL lesson must stand on its own.
- Familiarity with tables and basic `SELECT`, `WHERE`, and `ORDER BY` is helpful
  but not required.
- Podman Desktop/CLI with a running Linux machine and enough local disk for one
  PostgreSQL image and a small volume.

## Measurable learning outcomes

By the end of Week 2, the learner should be able to:

1. State the grain, key, and business meaning of every table before querying it.
2. Explain how primary keys, foreign keys, unique constraints, nullability, and
   checks protect different classes of invariant.
3. Normalize a spreadsheet-shaped procurement dataset and identify intentional
   historical snapshots that are not normalization mistakes.
4. Use inner and outer joins without dropping required rows or multiplying
   monetary facts.
5. Use aggregations, subqueries, CTEs, date operations, and window functions to
   answer progressively richer procurement questions.
6. Define supplier performance, price variance, delayed orders, committed
   monthly spend, and supplier reliability before implementing them.
7. Select candidate indexes from query predicates and ordering, then validate
   them with representative data and `EXPLAIN (ANALYZE, BUFFERS)`.
8. Use transactions and row locking to preserve a multi-row business invariant
   under concurrent delivery recording.
9. Explain when denormalized read models are justified and how their staleness
   and reconciliation risks differ from the source-of-truth model.
10. Solve eight medium SQL exercises and two product-analytics exercises while
    making grain, time window, null behavior, and limitations explicit.

## Running scenario

Use **Northwind Components**, a fictional manufacturer procuring raw materials
and components from contracted suppliers. Follow one copper-wire purchase order
from contract terms through partial deliveries and reporting. Expand the same
data model to steel, aluminium, fasteners, and electronic components only after
the core path is clear.

The opening question is:

> As of 2026-06-30, which orders are at risk, how much value remains
> outstanding, and what evidence supports the conclusion?

The learner should first inspect a small expected result and work backwards to
the facts needed to produce it.

## Data model and table grains

| Table | Grain | Role |
| --- | --- | --- |
| `suppliers` | one row per supplier | supplier identity and lifecycle |
| `products` | one row per purchasable SKU | product identity, reference-price classification, and canonical unit |
| `contracts` | one immutable supplier agreement version for an effective range | commercial agreement identity and dates |
| `contract_items` | one immutable product term within one contract version | agreed unit price, currency, unit, and lead time |
| `purchase_orders` | one purchase-order header | supplier, optional contract, order date, and lifecycle |
| `purchase_order_items` | one product line within a purchase order | ordered quantity, promised date, and snapshotted commercial terms |
| `deliveries` | one physical receipt event for a purchase order | receipt identity, date, and reference |
| `delivery_items` | one received product line within a delivery | delivered and accepted quantities by PO line |
| `commodity_prices` | one product/currency/unit/source observation per date | comparable market reference price |

The model must explicitly distinguish:

- agreement headers from product-level terms;
- order headers from ordered lines;
- delivery events from delivered lines;
- delivered quantity from accepted quantity;
- current reference data from historical PO snapshots; and
- operational facts from derived analytical metrics.

Relationship invariants must be designed rather than left implicit:

- `purchase_orders.supplier_id` is required; `contract_id` is optional for spot
  purchases. `contracts` exposes `UNIQUE (contract_id, supplier_id)`, and a
  composite foreign key proves a referenced contract belongs to the same
  supplier.
- PO items use `PRIMARY KEY (purchase_order_id, line_no)`. Deliveries expose
  `UNIQUE (delivery_id, purchase_order_id)`. A delivery item carries
  `delivery_id`, `purchase_order_id`, and `po_line_no`, with composite foreign
  keys to both parents. This prevents a receipt for one PO containing another
  PO's line.
- Contracts are immutable effective-dated agreement versions; their items have
  no separate validity interval. An amendment creates a new contract header
  version and new items. A contract-backed PO requires every line to reference
  an item from that exact contract version; a spot PO has a null header contract
  and null contract-item references. Each line snapshots its baseline price,
  currency, unit, and promise date. Historical variance never joins to a mutable
  current term.
- A referenced contract must satisfy
  `valid_from <= purchase_orders.ordered_on < valid_to`. Because that rule spans
  tables, enforce it in the PO-write protocol/DB function and audit it in
  verification SQL rather than implying a simple foreign key is sufficient.
- Parallel or overlapping agreements are permitted and surfaced by a
  data-quality query; the database does not guess which agreement applies.
- Without an explicit conversion table, contract, PO, delivery, and product-price
  values are comparable only when currency and unit codes match the relevant PO
  line and product canonical unit.

## Financial and temporal semantics

- Use `NUMERIC`, never binary floating point or PostgreSQL `money`, for quantity
  and price arithmetic.
- Store currency and unit directly, or inherit them through an immutable,
  constrained foreign key, for every value whose comparability depends on them.
  Do not convert currencies or units in this scope.
- Use `DATE` for business calendar dates and `TIMESTAMPTZ` for audit instants.
- Model contract validity as a half-open interval: `valid_from <= date < valid_to`.
- Require `valid_to NOT NULL` and `valid_to > valid_from` in this lab. An order
  on `valid_from` is eligible; one on `valid_to` is not.
- Define committed line value as `ordered_quantity * po_unit_price`.
- Define fulfillment using accepted quantity; retain delivered quantity for
  physical-volume and rejection analysis.
- Preserve PO price, currency, unit, and promise facts after a contract changes.
- Do not cascade-delete historical purchase orders or receipts.
- Record the receipt business date as `received_on DATE` and ingestion/audit
  time as `recorded_at TIMESTAMPTZ`. Promise comparisons use `received_on`.

Keep the mutable PO lifecycle deliberately small: `draft`, `issued`, and
`cancelled`. Fulfillment (`open`, `partially_fulfilled`, `fulfilled`, `late`) and
completion dates are derived from accepted delivery facts at a declared cutoff,
not stored as competing truth. Cancellation after any accepted receipt is
rejected transactionally; `cancelled` is terminal. Valid header transitions are
`draft -> issued` and `draft|issued -> cancelled` subject to that receipt rule.
Analytical metrics exclude drafts and cancellations unless their definition
explicitly states otherwise.

Initial precision choices must be documented and tested against the synthetic
domain. Candidate values are `NUMERIC(18,3)` for quantities and
`NUMERIC(19,4)` for unit prices; they are not universal financial standards.
All value outputs group by currency. Synthetic fixture currencies use a declared
two-decimal reporting scale: aggregate exact line products first and round once
at the reporting boundary using PostgreSQL numeric rounding semantics.

## Metric contracts fixed before SQL

### Delayed order

At `:as_of_date`, a PO line is delayed when its promised date is before the
cutoff and cumulative accepted quantity through the cutoff is below ordered
quantity. Order-level status must state how multiple lines are combined.

### Monthly procurement spend

Committed spend grouped by PO order month. It is not delivered, invoiced, paid,
or recognized accounting spend.

### Price variance

Expose two comparator variants within this one required query family:

1. PO unit price versus the applicable contract-item price; and
2. PO unit price versus the latest comparable product reference price from an
   explicit `:source_code` on or before the PO date.

Missing or currency/unit-incomparable references produce an explicit
unavailable result, not zero variance.

### Supplier performance

Report transparent components such as ordered value, accepted fulfillment,
on-time/in-full rate, median days late, rejection rate, and eligible order
count. Fill rate uses ordered quantity as its denominator; rejection rate uses
delivered quantity. OTIF requires every eligible line to be accepted in full by
its own promised date. Median days late applies only to completed eligible
orders, while still-open late work is reported separately. Do not collapse the
components into an unexplained score.

### Supplier reliability

Rank suppliers using a disclosed definition, reporting window, eligibility
threshold, completed-order rule, and tie behavior. For the lab, an eligible
supplier has at least three completed, issued, non-cancelled orders in the
half-open reporting period, where derived `fully_accepted_on` falls in
`[period_start, period_end)`; completion requires every eligible line to reach
ordered accepted quantity, and all reliability components use this same order
set. Rank lexicographically by OTIF rate descending,
rejection rate ascending, then median days late ascending; use `RANK` so exact
metric ties share a rank and use supplier code only for deterministic display.
The threshold and ordering are illustrative, fixture-pinned, and not a universal
policy. The result is descriptive, not a causal claim about supplier quality.

## Concept-first teaching sequence

Every unit uses: orienting question, first-principles explanation, small example
or diagram, counterexample, checkpoint, and bridge to the next question.

1. **Begin with the delayed-order answer.** Inspect an expected result and
   identify the facts, grain, cutoff date, and missing-data behavior needed to
   trust it.
2. **A row must represent one kind of fact.** Introduce entity, event, header,
   line, grain, candidate key, primary key, and relationship using the running
   PO and its two partial deliveries.
3. **Constraints turn assumptions into executable rules.** Add identities,
   natural-code uniqueness, foreign keys, checks, nullability, and safe delete
   behavior. Show what remains cross-row or temporal and cannot be expressed by
   a simple `CHECK`.
4. **Normalize the procurement spreadsheet.** Derive the nine tables through
   insertion, update, and deletion anomalies. Explain why historical commercial
   snapshots on PO lines are deliberate event facts.
5. **Filter and aggregate one table first.** Establish `CASE`, `COUNT`, `SUM`,
   `AVG`, `MIN`, `MAX`, `GROUP BY`, `HAVING`, `NULL`, and numeric arithmetic
   before adding joins.
6. **Joins connect facts and can multiply them.** Introduce `INNER JOIN` and
   `LEFT JOIN`, then demonstrate fan-out by joining PO lines to multiple delivery
   items. Establish pre-aggregation of the many side as a correctness rule.
7. **Dates turn a live system into a reproducible snapshot.** Use explicit
   cutoffs, half-open reporting ranges, intervals, month bucketing, and time-zone
   boundaries. Label PostgreSQL `DATE_TRUNC` and interval syntax accordingly.
8. **Subqueries answer a question inside another question.** Cover scalar and
   correlated subqueries, `EXISTS`, `IN`, and the `NULL` trap in `NOT IN`. Use
   latest comparable product reference price from a selected source as the main
   example.
9. **CTEs name intermediate business facts.** Build `accepted_as_of`,
   `line_status`, and `supplier_rollup` stages. Explain readability and scope;
   do not describe a CTE as inherently materialized or faster.
10. **Window functions compare without collapsing detail.** Contrast
    `GROUP BY` (one row per group) with `OVER` (detail rows remain), then use
    `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `LAG`,
    running totals, and rolling windows.
11. **Assemble the five required analyses.** Build supplier performance, price
    variance as one family with two separate comparators, delayed orders,
    monthly committed spend, and reliable supplier ranking in dependency order.
12. **Indexes optimize observed access paths.** Derive candidates from the five
    queries, load representative synthetic scale, run `ANALYZE`, and compare
    plans before and after. Cover B-tree ordering, selectivity, composite and
    partial indexes, write cost, and why a sequential scan can be correct.
13. **Transactions protect a business transition.** Atomically create a PO
    header and its lines. Then record a delivery by locking the relevant PO
    line, recomputing accepted quantity, rejecting over-acceptance, and inserting
    the receipt in one transaction. Both delivery and cancellation paths first
    lock the PO header; delivery then locks lines in deterministic
    `(purchase_order_id, line_no)` order and validates that the header is
    `issued`. Cancellation holds the same header lock while proving no accepted
    receipt exists. Establish atomicity, isolation, and rollback before the
    PostgreSQL-specific two-session race demonstrations.
14. **Denormalization is an operational trade-off.** Introduce a supplier-month
    summary or materialized view only after the source queries are correct.
    Discuss refresh, staleness, lineage, and reconciliation.
15. **Prove the model and queries.** Exercise happy paths, constraints, fan-out
    regressions, boundary dates, no-delivery and partial-delivery orders, missing
    prices, rejection, insufficient samples, and transaction conflicts.
16. **Consolidate and defend.** Trace one answer back to source rows, review
    common errors, complete exercises, and answer interview follow-ups.

## PostgreSQL-specific boundary

Keep portable relational reasoning separate from PostgreSQL implementation
details. PostgreSQL-specific material includes:

- identity columns, `NUMERIC(p, s)`, `TIMESTAMPTZ`, and selected DDL syntax;
- `DATE_TRUNC`, intervals, aggregate `FILTER`, and optional `LATERAL` examples;
- CTE inlining/materialization behavior;
- `EXPLAIN (ANALYZE, BUFFERS)` and index plan interpretation;
- transaction isolation commands, `SELECT ... FOR UPDATE`, SQLSTATE-based retry
  decisions, and PostgreSQL lock behavior; and
- Podman lifecycle and `psql` invocation commands.

## Build contract

Create a repository-contained, Podman-first PostgreSQL lab with:

- a reproducible container start and explicitly destructive local-lab reset
  workflow using the pinned image with `--pull=never` after verification;
- schema DDL for the nine tables and required constraints;
- deterministic synthetic seed data containing purposeful edge cases;
- the five named analytical query families;
- transaction and concurrency demonstrations;
- SQL assertions for constraints, result correctness, and fan-out regressions;
- before/after index-plan fixtures at a scale where planner decisions are
  meaningful; and
- concise commands for start, readiness, seed, verify, inspect, and stop.

Runtime state, volumes, credentials, and generated outputs must remain ignored.
Use a local non-production password supplied at runtime; do not commit secrets.
Bind only to localhost if a host port is needed.

The delivery/cancellation write protocol is an application/DB-function contract,
not a plain declarative constraint: both paths lock the PO header first;
delivery then locks target lines in the same order, recomputes cumulative
accepted quantities, validates them, and inserts the header/items atomically.
Cancellation checks that cumulative accepted quantity is zero while holding the
common header lock; a fully rejected delivery does not by itself prevent
cancellation.
Distinguish business rejection from retryable SQLSTATE `40001` serialization
failures and `40P01` deadlocks.
Returns and receipt corrections are outside scope, so accepted quantities are
monotonic. Row checks require delivered quantity `> 0`, accepted quantity
`>= 0`, accepted quantity `<= delivered quantity`, and at most one row for a PO
line within one delivery.

## Candidate indexes to validate, not assume

- composite delivery-item foreign-key indexes matched to the locked key design;
- `deliveries(purchase_order_id, received_on, delivery_id)`;
- a PO-line promised-date path and a PO-header order-date path matched to actual
  filters;
- `purchase_order_items(product_id, purchase_order_id)` only if product-first
  analysis justifies it;
- a product-first contract-term lookup only if existing PK/unique indexes do not
  already serve it; and
- `commodity_prices(product_id, currency_code, unit_code, source_code, price_date DESC)`.

Primary-key and unique-constraint indexes must be considered before adding
duplicates. PostgreSQL does not automatically index the referencing side of a
foreign key. Final indexes require observed plans after `ANALYZE`.

## Query acceptance criteria

Every published analytical query must:

- declare its output grain and metric definition;
- take an explicit cutoff or half-open reporting range where applicable;
- use deterministic ordering when presentation requires it;
- pre-aggregate delivery facts before combining them with PO monetary facts;
- preserve no-delivery rows when the business question requires them;
- keep currency and unit comparisons compatible;
- distinguish zero from missing/not-comparable;
- include at least one fixture that makes a plausible naive query fail; and
- be executed against PostgreSQL 18.4 before any result is described as
  validated.

In `psql`, the reproducible cutoff is supplied with `-v as_of_date=2026-06-30`
and read as `:'as_of_date'::date`; `:as_of_date` is lesson notation, not native
SQL parameter syntax. Monthly queries use half-open `DATE` ranges. Session time
zone affects `TIMESTAMPTZ` display, not the stored instant.

## Required edge cases

- PO with no deliveries;
- partially delivered multi-line PO;
- multiple delivery events for one PO line;
- delivered quantity greater than accepted quantity;
- attempted accepted quantity above ordered quantity;
- receipt exactly on the promised date and just after it;
- contract effective boundary date and overlapping-contract detection;
- absent, later-only, wrong-source, and currency/unit-incomparable product prices;
- cancelled PO excluded from appropriate metrics;
- supplier below the reliability eligibility threshold;
- equal-ranking suppliers and explicit tie behavior;
- month and year boundary; and
- concurrent delivery attempts against the same remaining quantity.
- concurrent cancellation and first-delivery attempts against the same PO.

## Exercises

### Eight medium SQL exercises

1. Return active contract items and current committed PO totals, retaining items
   with no POs.
2. Find suppliers with no completed PO in a supplied reporting period using
   null-safe anti-join semantics.
3. Return ordered, delivered, accepted, remaining, and first fully accepted date
   for every PO line.
4. Find PO lines whose unit price exceeds the latest comparable product price
   by a supplied percentage.
5. Return supplier-month committed spend and a three-month rolling total.
6. Rank eligible suppliers per product by on-time/in-full rate with explicit
   ties.
7. Find the first delayed PO per supplier as of a supplied date.
8. Detect supplier/product term overlap by joining contract-item products to
   their contract-header validity ranges.

### Two product-analytics exercises

9. Define supplier cohorts by first PO quarter and compare reliability across
   their first three eligible orders. Discuss small samples, censoring, and
   survivorship.
10. Define ordered-value-weighted delay exposure as of a supplied date, contrast
    it with late-order rate, and explain how the chosen value and time grain can
    change prioritization.

Each exercise must include objective, expected output grain and columns,
acceptance checks, likely traps, and interview follow-ups. Solutions should be
separated so the learner can attempt each problem first.

## Interview outcomes

The learner must be able to explain and defend:

- how join fan-out causes incorrect financial results;
- `WHERE` versus `HAVING` and aggregate versus window semantics;
- subqueries versus CTEs as expression choices rather than universal performance
  rules;
- why `NOT IN` can behave unexpectedly with `NULL`;
- how the latest applicable price query works and when `LATERAL` or a window
  approach is useful;
- composite-index column order and why a planner may prefer a sequential scan;
- normalization versus intentional historical snapshots and read models;
- transaction atomicity, isolation anomalies, row locks, deadlocks, and retries;
- why reliability depends on definition, eligibility, window, and data quality;
  and
- what the schema intentionally does not model.

## Explicitly out of scope

- ORM or application API integration;
- migration-framework selection;
- authentication, authorization, tenancy, or production secret management;
- invoices, payments, taxes, accounting ledgers, returns, and credit notes;
- currency or unit conversion;
- autonomous supplier decisions or procurement execution;
- CDC, replication, partitioning, warehouse/star-schema design, and production
  performance claims; and
- treating a local Podman lab as a production deployment pattern.

## Validation and publication gates

Before HITL review:

1. Start the pinned PostgreSQL image under Podman and pass readiness checks.
2. Apply schema twice where idempotency is claimed.
3. Load deterministic seed data and confirm row-count/checksum expectations.
4. Execute all lesson queries and compare exact expected results.
5. Execute constraint, rollback, fan-out, and concurrency tests.
6. Run representative `EXPLAIN (ANALYZE, BUFFERS)` checks after `ANALYZE`.
   Capture dataset hash, server configuration, and machine-readable plans as
   evidence, but do not require byte-identical plans or universal index use.
7. Verify every external claim against PostgreSQL 18 primary documentation.
8. Run an independent technical and pedagogical audit.
9. Obtain explicit human approval before creating or publishing canonical Week 2
   content.

## Outline acceptance criteria

- Every Week 2 topic and deliverable from `Path.md` is traceable to a section.
- The nine-table model preserves realistic multi-line contracts, POs, and
  deliveries without hiding cardinality assumptions.
- One Northwind procurement story connects row grain through analytics,
  indexing, and transactions.
- Definitions precede queries and correctness precedes optimization.
- Portable SQL reasoning and PostgreSQL-specific behavior are clearly labeled.
- Financial and temporal semantics prevent silent double counting or invalid
  comparisons.
- The content includes eight medium SQL and two product-analytics exercises.
- Learner-facing content contains no internal week plan, review status, or
  approval metadata.
- No execution, result, or performance claim is published before it is actually
  verified.

## Runtime gate evidence

Observed on 2026-08-08:

- Windows Podman client 5.8.2 connected to a rootless WSL2 Linux/AMD64 Podman
  engine 5.8.5;
- isolated `prep-week2` machine started successfully;
- the pinned image resolved to the recorded digest and image ID above;
- a disposable container reached `pg_isready` and reported server version
  `18.4 (Debian 18.4-1.pgdg13+1)` for database `procurement` through a real
  `psql` query; and
- the smoke container used no host port or persistent volume and was removed
  after the check.

This proves local runtime compatibility only. It does not validate the Week 2
schema, data, analytical queries, concurrency behavior, or performance.
