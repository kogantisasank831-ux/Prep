---
layout: week
permalink: /weeks/week-02/beginner/
title: "SQL and data modelling: a beginner's introduction"
description: Learn how a relational database represents a purchase order, its deliveries, and the questions SQL can answer about them.
summary: Follow one purchase order from agreement to receipt, build the relational-data mental model, then continue to the production lesson and verified PostgreSQL lab.
kicker_primary: SQL and data modelling
kicker_secondary: Beginner context
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-02/
---

## Begin with one order

Northwind Components orders 1,000 kg of copper wire from Atlas Metals. The order number is `PO-1042`, its price is USD 12 per kg, and its promise date is 20 June 2026.

The supplier sends two physical receipts. By 30 June, they have delivered 900 kg, but inspection accepts only 870 kg. The remaining 130 kg has not yet been accepted.

At USD 12 per kg, that remaining commitment is `130 × 12 = USD 1,560`.

This small story shows why relational databases exist. A procurement manager might ask:

- Which promised lines are still open and late?
- What value has the company committed to buy?
- Did a supplier deliver the right quantity on time?
- Was the PO price comparable with the applicable contract or market observation?
- Which suppliers have reliable completed orders?

SQL asks these questions. Data modelling makes the answers mean what we think they mean. Start by asking, “What does one row represent?”

**Checkpoint.** At the 30 June cutoff, is `PO-1042` complete? No. It is 90% physically delivered (900 / 1,000) and 87% accepted (870 / 1,000). The lesson uses accepted quantity for fulfillment, because physical arrival and inspection acceptance are different events.

## A database is organised evidence

A relational database stores information in **tables**, each with named **columns** and many **rows**. We need several tables because the facts we track are not all the same kind of fact:

| Table | One row represents |
| --- | --- |
| `suppliers` | one supplier organisation |
| `products` | one product, such as copper wire |
| `contracts` | one version of an agreement with a supplier |
| `contract_items` | one product term within that agreement |
| `purchase_orders` | one order header, such as `PO-1042` |
| `purchase_order_items` | one product line on an order |
| `deliveries` | one physical receipt event |
| `delivery_items` | one PO line included in one receipt |
| `commodity_prices` | one market-price observation on one date |

The phrase “one row represents” is a table's **grain**. `purchase_orders` has one row for `PO-1042`; `delivery_items` has one row whenever a PO line is included in a receipt. An order line can therefore have several receipt rows.

```text
supplier -> contract -> contract item
    |                       |
    +--> purchase order -> PO line <- delivery item <- delivery
                              |
                              +--> product <- price observation
```

Separating facts avoids repetition. A supplier-name change touches its one supplier row, and two receipts do not turn one ordered amount into two orders.

### Rows need reliable identities

Each table has a **primary key**, a value (or small set of values) that identifies exactly one row. An order line needs both `purchase_order_id` and `line_no`, because line 1 is only unique inside its order.

A **foreign key** is a stored reference to a related row. A PO line refers to its header; a delivery item refers to its receipt and PO line. These references stop us recording a delivery for an order line that does not exist.

**Checkpoint.** Which table should contain the fact that 470 kg from the second receipt was accepted? `delivery_items`: that fact belongs to one received order line in one receipt, not to the order header.

## Why orders have headers and lines

An order is usually both a document and a list. Its **header** describes what is shared by the whole order: its number, supplier, order date, contract, and lifecycle status. Its **lines** describe what varies within that order: product, quantity, unit, unit price, and promise date.

`PO-1042` happens to contain one copper-wire line. Another PO can contain both steel plate and machine fasteners. A line is where the monetary commitment belongs:

```text
PO-1042 header
  supplier: Atlas Metals
  ordered on: 2026-06-01

line 1
  product: copper wire
  ordered: 1,000 kg
  price: USD 12/kg
  promised: 2026-06-20
```

The line retains the price and contract information that governed the order. A newer contract version may later differ; the original price is historical evidence. Currencies and units remain explicit: USD cannot be added meaningfully to EUR without FX conversion, and kg and `ea` are not interchangeable.

## Normalization and intentional summaries

Separating suppliers, order headers, lines, and receipts is **normalization**. Facts that change independently live in different tables, which reduces contradictory copies and makes each row's meaning clearer.

The PO line's copied commercial terms are not an accidental duplicate. They are a historical snapshot of what the company committed to when it issued the order. If a contract changes later, the old PO must keep its original meaning.

**Denormalization** serves a different purpose: it creates a read-oriented summary, such as monthly supplier performance, from normalized source facts. A summary can make repeated reporting simpler or faster, but it can become stale. It therefore needs a declared refresh point, traceable source rows, and a reconciliation check. The normalized facts remain the evidence from which the summary is rebuilt.

**Checkpoint.** Is the price stored on an issued PO line the same kind of duplication as a cached monthly dashboard total? No. The first preserves a historical event fact; the second is a derived read model that must be refreshed.

## First questions: filtering and aggregation

`SELECT` chooses columns, `FROM` names a table, and `WHERE` keeps rows satisfying a condition.

```sql
SELECT po_number, ordered_on
FROM purchase_orders
WHERE lifecycle_status = 'issued';
```

This returns issued PO headers. Its grain remains one PO, because it has not combined or collapsed anything.

An **aggregate** combines input rows into a summary. `SUM` adds values and `COUNT` counts rows; `GROUP BY` specifies the summary grain.

```sql
SELECT
    currency_code,
    SUM(ordered_quantity * po_unit_price) AS committed_value
FROM purchase_order_items
GROUP BY currency_code;
```

This begins with one row per PO line and ends with one row per currency. `WHERE` filters before aggregation; `HAVING` filters groups after it. State the output grain before writing the query.

**Checkpoint.** If a report groups by supplier, what does one output row represent? One supplier's summary, not one individual receipt or PO line.

## Joins: connect related tables carefully

A **join** combines rows that have matching keys. To show an order number beside its product lines, join the PO header to the PO-line table on the PO identifier:

```sql
SELECT po.po_number, poi.line_no, poi.ordered_quantity, poi.unit_code
FROM purchase_orders AS po
JOIN purchase_order_items AS poi
  ON poi.purchase_order_id = po.purchase_order_id;
```

This is an `INNER JOIN`: it keeps only matches. A `LEFT JOIN` keeps every row from the table on its left even when no matching row exists on the right. For open-work reporting, that difference matters. An ordered line with no receipt is still an important line, so it must not disappear simply because there is no delivery row.

`WITH ... AS (...)` gives a name to an intermediate query result; this is called a common table expression, or CTE. We will revisit CTEs later. Here it lets us define exactly which line-level receipts existed at the cutoff before joining them to monetary facts:

```sql
WITH receipt_before_cutoff AS (
    SELECT di.purchase_order_id, di.po_line_no,
           d.received_on, di.delivered_quantity, di.accepted_quantity
    FROM deliveries AS d
    JOIN delivery_items AS di
      ON (di.delivery_id, di.purchase_order_id)
       = (d.delivery_id, d.purchase_order_id)
    WHERE d.received_on <= DATE '2026-06-30'
)
SELECT po.po_number, poi.line_no, r.received_on
FROM purchase_orders AS po
JOIN purchase_order_items AS poi USING (purchase_order_id)
LEFT JOIN receipt_before_cutoff AS r
  ON (r.purchase_order_id, r.po_line_no)
   = (poi.purchase_order_id, poi.line_no);
```

The result above exposes **fan-out**. One PO line can match many delivery rows. If you sum its USD 12,000 value after joining it to two receipts, that one ordered value appears twice. Valid SQL, wrong financial result.

First summarise receipts to one row per PO line, then join that to the monetary PO line:

```sql
WITH receipt_by_line AS (
    SELECT di.purchase_order_id, di.po_line_no,
           SUM(di.delivered_quantity) AS delivered_quantity,
           SUM(di.accepted_quantity) AS accepted_quantity
    FROM deliveries AS d
    JOIN delivery_items AS di
      ON (di.delivery_id, di.purchase_order_id)
       = (d.delivery_id, d.purchase_order_id)
    WHERE d.received_on <= DATE '2026-06-30'
    GROUP BY di.purchase_order_id, di.po_line_no
)
SELECT po.po_number, poi.line_no, poi.ordered_quantity,
       COALESCE(r.delivered_quantity, 0) AS delivered_quantity,
       COALESCE(r.accepted_quantity, 0) AS accepted_quantity
FROM purchase_orders AS po
JOIN purchase_order_items AS poi USING (purchase_order_id)
LEFT JOIN receipt_by_line AS r
  ON (r.purchase_order_id, r.po_line_no)
   = (poi.purchase_order_id, poi.line_no);
```

For `PO-1042`, this produces 900 kg delivered and 870 kg accepted at 30 June. The verified 5 July receipt is intentionally outside this cutoff.

`COALESCE(value, 0)` says to use zero when null. Here no receipt means zero accepted quantity. A missing comparable market price is instead “unavailable,” not zero.

**Checkpoint.** Why not use `SUM(DISTINCT ...)` to fix duplicated order value? Two separate legitimate lines can happen to have the same value. Repair the join grain instead of removing equal values blindly.

## Dates make results repeatable

“Late” is not a timeless property. It depends on a cutoff date. For this story, the cutoff is 30 June 2026. `PO-1042` is late because its promise date, 20 June, is earlier than the cutoff and its accepted quantity is still below 1,000 kg.

Use an explicit input date rather than today's date so the query remains reproducible.

```sql
WHERE poi.promised_on < DATE '2026-06-30'
  AND accepted_quantity < poi.ordered_quantity
```

For a reporting period, use a **half-open interval**: include the start and exclude the end.

```sql
WHERE ordered_on >= DATE '2026-06-01'
  AND ordered_on <  DATE '2026-07-01'
```

This means all of June without inventing a “last instant of June.” It also means a line promised on 30 June is not delayed *at* the 30 June cutoff in this lab: the delayed rule is strictly earlier than the cutoff.

## Nested questions: subqueries, CTEs, and windows

Some questions contain smaller questions. A **subquery** is a query inside another query. “Does this supplier have no issued POs in the period?” can use `NOT EXISTS (...)`.

Another nested question is “what was the latest comparable market price when this PO was ordered?” Comparable means the same product, currency, unit, selected source, and a price date on or before the PO date. A later price, another currency, or another unit is not evidence for that comparison. The production lesson uses a PostgreSQL `LATERAL` join to ask that latest-price question separately for every PO line.

A **common table expression** (CTE) names an intermediate result inside one statement. `receipt_by_line` above makes “accepted quantity by PO line” readable before the late-line filter.

A **window function** compares related rows while retaining each row. Imagine the accepted receipts for `PO-1042` as a timeline:

```text
18 June: accepted 400 kg  -> running accepted 400 kg
25 June: accepted 470 kg  -> running accepted 870 kg
05 July: accepted 130 kg  -> running accepted 1,000 kg
```

`SUM(...) OVER (...)` calculates that running total without collapsing receipt dates. It can find the first day accepted quantity reaches the order: 5 July here.

**Checkpoint.** When should you use a CTE? When naming an intermediate fact makes the business logic clearer. It is a readability tool, not a promise of faster execution.

## Indexes are a map, not a free speed switch

An **index** is an extra data structure that can help the database find qualifying rows without reading every row. It is like a book index: useful when you seek a small, well-described part of a large book.

For a delayed-line query, an index beginning with `promised_on` may help for suitable data and predicates. But writes must maintain it, and scanning a small table can be cheaper. The verified lab includes an index probe; a plan is evidence for one dataset and configuration, not a permanent guarantee.

## Transactions protect all-or-nothing work

A **transaction** groups related changes into one unit. If a delivery item fails validation, we do not want a half-created receipt. A transaction commits the whole unit or rolls it back.

```sql
BEGIN;
-- create one delivery and its items
COMMIT;
```

Before `COMMIT`, `ROLLBACK` abandons uncommitted changes. This is atomicity: all succeeds, or none becomes durable. Constraints still decide validity.

Concurrency adds another problem. Two staff members might each accept 100 kg when only 130 kg remains. The lab locks the shared PO header first, then affected lines in a consistent order, rechecks the quantity, and accepts or rejects the attempt.

## What the five procurement analyses actually mean

The production lesson and lab use five analyses. Their names are shorter than their definitions, so keep the meanings explicit.

1. **Monthly committed procurement spend**: sum ordered quantity × PO unit price for currently issued POs, grouped by original order month and currency. It is committed value, not cash paid; invoices and payments are not modelled.
2. **Delayed PO lines**: one currently issued PO line whose promise date is before the supplied cutoff and whose accepted quantity at that cutoff is still below its ordered quantity. The result includes remaining quantity and open committed value.
3. **Contract and market price variance**: compare a PO line's price separately with its stored contract price and with the latest applicable selected-source market observation. Missing comparable evidence stays unavailable; it is not coerced to zero.
4. **Supplier performance components**: at the cutoff, calculate fill and rejection at supplier + unit, committed value at supplier + currency, and OTIF/lateness over completed orders. These separate grains prevent kg, individual items, or currencies from being added into meaningless totals.
5. **Eligible supplier reliability ranking**: include suppliers with at least three issued, non-cancelled orders whose `fully_accepted_on` falls inside the half-open reporting period. Rank by OTIF descending, unit-safe rejection rate ascending, then median days late ascending; exact metric ties share a `RANK`. This is a declared lab policy, not an intrinsic attribute of a supplier.

The same discipline applies to every result: define the metric, source facts, time boundary, and output grain before trusting the number.

## Continue with the complete lesson

You now have the vocabulary to read the production version without treating SQL as magic:

- tables separate facts with different grains and lifecycles;
- primary and foreign keys give rows stable identities and valid relationships;
- headers and lines separate shared order facts from product-specific facts;
- `WHERE`, `GROUP BY`, and joins change what each result row means;
- left joins preserve absence when absence is operationally important;
- fan-out is a grain error that can inflate totals;
- explicit dates make results reproducible;
- subqueries, CTEs, and windows express nested and time-ordered reasoning;
- indexes trade extra write work for possible read efficiency; and
- transactions and locks protect a valid write workflow under failure and competition.

Continue with the [production version]({{ '/weeks/week-02/' | relative_url }}). It provides the exact query contracts, full PostgreSQL schema, advanced query patterns, boundary cases, performance investigation, and concurrency semantics. Then use the [verified Week 2 lab on GitHub](https://github.com/kogantisasank831-ux/Prep/tree/main/labs/week-02) to inspect the fixture and execute the supplied checks in a local synthetic environment.

### Readiness checklist

- [ ] I can say what one row means in a table before I query it.
- [ ] I can distinguish an order header, an order line, a delivery, and a delivery item.
- [ ] I know why a missing receipt may need a left join rather than an inner join.
- [ ] I can explain why ordered value must not be summed after a one-to-many receipt join.
- [ ] I can describe `PO-1042` separately in ordered, delivered, and accepted quantities at a stated cutoff.
- [ ] I know that dates, currencies, units, and metric denominators are part of a query's meaning.
- [ ] I can distinguish normalized source facts, historical event snapshots, and denormalized read summaries.
- [ ] I can recognise a CTE as a named intermediate result and a window as a way to retain detail while comparing rows.
- [ ] I know that an index and a transaction solve different problems.
