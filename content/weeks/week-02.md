---
layout: week
permalink: /weeks/week-02/
title: "SQL and data modelling: make procurement facts trustworthy"
description: Build a PostgreSQL procurement model and answer five operational questions without double-counting, ambiguous dates, or hidden metric definitions.
summary: Follow one Northwind Components purchase order from contract to receipt, then use SQL to make its operational evidence queryable and defensible.
kicker_primary: SQL and data modelling
kicker_secondary: Procurement facts before dashboards
---

## One order, one uncomfortable question

It is 30 June 2026. A procurement manager asks:

> Which orders are late, how much committed value remains open, and why should I trust the answer?

Keep one Northwind Components order with us. `PO-1042` orders 1,000 kg of copper wire at USD 12 per kg. Two receipts deliver 900 kg; inspection accepts only 870 kg. The promise date has passed.

The verified synthetic fixture therefore gives this line-level state at the cutoff:

| PO | ordered | delivered | accepted | remaining | open committed value |
| --- | ---: | ---: | ---: | ---: | ---: |
| `PO-1042` | 1,000 kg | 900 kg | 870 kg | 130 kg | USD 1,560 |

The arithmetic is easy. Trust is harder. Which row owns the ordered value? Why is accepted quantity the fulfillment fact? Did the query preserve orders with no receipt? Did two receipts duplicate the PO value? Was the cutoff supplied or taken from the machine clock?

This lesson answers those questions in dependency order. We first decide what a row means, aggregate one table, connect tables safely, and only then build delayed-order and supplier metrics. PostgreSQL syntax serves the reasoning; it does not replace it.

### The contract for every result

Every analytical answer must declare four things:

```text
metric definition + source facts + time boundary + output grain
```

For this lesson, fulfillment uses **accepted quantity**. Delivered quantity remains visible for rejection analysis. Monetary results remain separated by currency and unit unless an explicit conversion model exists. All data is synthetic, and invoices, payments, tax, FX, returns, and accounting recognition are outside the model.

You need only basic `SELECT`, `WHERE`, and `ORDER BY`. By the end, you should be able to defend joins, aggregations, subqueries, CTEs, windows, date boundaries, indexes, normalization choices, and transaction behavior—not merely write their syntax.

**Checkpoint.** Is `PO-1042` 90% fulfilled or 87% fulfilled? It is 90% physically delivered and 87% accepted. Calling either number simply “fulfillment” hides a business definition.

**Bridge.** Before calculating either percentage, we need to know what one row represents.

## 1. Grain comes before columns

### Orienting question: why not put the whole process in one spreadsheet?

A sheet containing supplier, contract price, PO number, delivery date, delivered quantity, and market price repeats facts that change at different rates. Two receipts repeat the PO line's ordered value twice. Updating a supplier name touches many event rows. Deleting the last receipt can erase the only visible copy of an order.

These are insertion, update, and deletion anomalies. Normalization separates facts that have different grains and lifecycles. Northwind uses nine tables because headers, lines, and observations are different facts:

| Table | One row means |
| --- | --- |
| `suppliers` | one supplier |
| `products` | one purchasable SKU |
| `contracts` | one immutable supplier-agreement version |
| `contract_items` | one product term in one agreement version |
| `purchase_orders` | one PO header |
| `purchase_order_items` | one product line on one PO |
| `deliveries` | one physical receipt event for one PO |
| `delivery_items` | one received PO line in one receipt |
| `commodity_prices` | one product/currency/unit/source observation on one date |

```text
supplier -> contract -> contract item
    |                       |
    +--> purchase order -> PO line <- delivery item <- delivery
                              |
                              +--> product <- commodity price
```

`PO-1042` appears once in `purchase_orders`, once per ordered product in `purchase_order_items`, once per receipt event in `deliveries`, and once per received line in each event's `delivery_items`. Those grains let a line be received in pieces without copying its order value.

### Keys protect relationships, not prose assumptions

A primary key identifies one row. A unique constraint protects a candidate business identity. A foreign key proves that a referenced row exists. `NOT NULL` and `CHECK` protect row-local invariants. PostgreSQL documents these constraint types in [Constraints](https://www.postgresql.org/docs/18/ddl-constraints.html).

The full executable schema is in [00_schema.sql](../../labs/week-02/sql/00_schema.sql). Focus first on two relationship excerpts:

```sql
CREATE TABLE purchase_order_items (
    purchase_order_id bigint NOT NULL,
    line_no integer NOT NULL CHECK (line_no > 0),
    product_id bigint NOT NULL REFERENCES products (product_id),
    contract_id bigint,
    contract_item_no integer,
    ordered_quantity numeric(18, 3) NOT NULL
        CHECK (ordered_quantity <> 'NaN'::numeric AND ordered_quantity > 0),
    po_unit_price numeric(19, 4) NOT NULL
        CHECK (po_unit_price <> 'NaN'::numeric AND po_unit_price >= 0),
    contract_unit_price numeric(19, 4),
    currency_code text NOT NULL,
    unit_code text NOT NULL,
    promised_on date NOT NULL,
    PRIMARY KEY (purchase_order_id, line_no),
    FOREIGN KEY (purchase_order_id)
        REFERENCES purchase_orders (purchase_order_id),
    FOREIGN KEY (purchase_order_id, contract_id)
        REFERENCES purchase_orders (purchase_order_id, contract_id),
    FOREIGN KEY (contract_id, contract_item_no)
        REFERENCES contract_items (contract_id, contract_item_no)
    -- The full DDL also checks the all-null/all-present contract snapshot shape.
);

CREATE TABLE delivery_items (
    delivery_id bigint NOT NULL,
    purchase_order_id bigint NOT NULL,
    po_line_no integer NOT NULL,
    delivered_quantity numeric(18, 3) NOT NULL
        CHECK (delivered_quantity <> 'NaN'::numeric AND delivered_quantity > 0),
    accepted_quantity numeric(18, 3) NOT NULL
        CHECK (accepted_quantity <> 'NaN'::numeric
               AND accepted_quantity >= 0
               AND accepted_quantity <= delivered_quantity),
    PRIMARY KEY (delivery_id, po_line_no),
    FOREIGN KEY (delivery_id, purchase_order_id)
        REFERENCES deliveries (delivery_id, purchase_order_id),
    FOREIGN KEY (purchase_order_id, po_line_no)
        REFERENCES purchase_order_items (purchase_order_id, line_no)
);
```

The composite foreign keys prevent a receipt for one PO from containing a line from another PO. The complete schema also validates contract dates, matching product/currency/unit terms, and PO lifecycle transitions with narrowly scoped trigger functions.

Some rules cannot be honest row-local checks. “Accepted quantity across all receipts must not exceed ordered quantity” depends on several rows and concurrent writes. “The contract was effective on the order date” compares rows in different tables. PostgreSQL explicitly warns against using `CHECK` constraints to depend on other table data; the lab uses write-time functions for those rules.

### Normalization does not forbid historical snapshots

A contract amendment creates a new immutable agreement version. A PO line copies the price, currency, unit, and contract baseline that governed the commitment. That snapshot is not an accidental duplicate: it answers “what did this order commit to then?” A current contract term answers a different question.

The lab uses `NUMERIC(18,3)` for quantities and `NUMERIC(19,4)` for unit prices. These are domain choices, not universal standards. PostgreSQL `numeric` provides exact decimal arithmetic but also admits the special value `NaN`, so every financial and quantity constraint rejects it explicitly. Binary floating point and the locale-sensitive `money` type are unsuitable as the general price representation here. See [Numeric Types](https://www.postgresql.org/docs/18/datatype-numeric.html) and [Monetary Types](https://www.postgresql.org/docs/18/datatype-money.html).

**Checkpoint.** Why does a PO line retain `contract_unit_price` after the agreement changes? Because the line is historical evidence of the order, not a live pointer whose meaning should drift.

**Bridge.** With row meanings fixed, begin with arithmetic inside a single table. Joins can wait.

## 2. Aggregate one table before connecting tables

### Orienting question: what does `GROUP BY` do to grain?

Start with `purchase_order_items`, whose grain is one PO line. This query collapses those lines to one row per currency:

```sql
SELECT
    currency_code,
    SUM(ordered_quantity * po_unit_price) AS committed_line_value
FROM purchase_order_items
GROUP BY currency_code
ORDER BY currency_code;
```

`SUM`, `COUNT`, `MIN`, `MAX`, and `AVG` reduce rows within each group. `WHERE` filters input rows before grouping; `HAVING` filters groups after aggregation:

```sql
SELECT currency_code, SUM(ordered_quantity * po_unit_price) AS value
FROM purchase_order_items
WHERE promised_on < :'as_of_date'::date
GROUP BY currency_code
HAVING SUM(ordered_quantity * po_unit_price) > 1000;
```

Null is not zero. An aggregate over no qualifying rows can produce null; convert that to zero only after the business meaning says “absence means zero.” PostgreSQL documents aggregate semantics in [Aggregate Functions](https://www.postgresql.org/docs/18/functions-aggregate.html).

Do not add USD and EUR into a single total. Without FX data, the output grain includes currency. The same applies to incompatible physical units.

**Checkpoint.** After `GROUP BY currency_code`, can the result safely display an arbitrary `purchase_order_id`? No. That column is neither the group key nor an aggregate and no longer belongs to the output grain.

**Bridge.** One table cannot tell us whether a line arrived. Now we connect grains deliberately.

## 3. Joins connect facts—and can multiply them

### Orienting question: when is a syntactically valid join financially wrong?

An `INNER JOIN` retains matching rows. A `LEFT JOIN` retains every row from the left side and supplies nulls when the right side has no match. The choice encodes business meaning: a report about open commitments must retain PO lines with no delivery.

The dangerous case is a one-to-many join. `PO-1042` has one monetary PO line and two delivery items. This naive query repeats its ordered value once per receipt:

```sql
-- Deliberately wrong: used to expose fan-out.
SELECT
    po.po_number,
    SUM(poi.ordered_quantity * poi.po_unit_price) AS inflated_value
FROM purchase_orders AS po
JOIN purchase_order_items AS poi USING (purchase_order_id)
JOIN delivery_items AS di
  ON (di.purchase_order_id, di.po_line_no)
   = (poi.purchase_order_id, poi.line_no)
WHERE po.po_number = 'PO-1042'
GROUP BY po.po_number;
```

The correction is structural: aggregate the many side to PO-line grain first, then join exactly one receipt aggregate to each monetary line.

```sql
-- Output grain: one PO line as of a supplied cutoff.
WITH receipt_by_line AS (
    SELECT
        di.purchase_order_id,
        di.po_line_no,
        SUM(di.delivered_quantity) AS delivered_quantity,
        SUM(di.accepted_quantity) AS accepted_quantity
    FROM deliveries AS d
    JOIN delivery_items AS di
      ON (di.delivery_id, di.purchase_order_id)
       = (d.delivery_id, d.purchase_order_id)
    WHERE d.received_on <= :'as_of_date'::date
    GROUP BY di.purchase_order_id, di.po_line_no
)
SELECT
    po.po_number,
    poi.line_no,
    poi.ordered_quantity,
    COALESCE(r.delivered_quantity, 0) AS delivered_quantity,
    COALESCE(r.accepted_quantity, 0) AS accepted_quantity,
    poi.ordered_quantity - COALESCE(r.accepted_quantity, 0) AS remaining_quantity
FROM purchase_orders AS po
JOIN purchase_order_items AS poi USING (purchase_order_id)
LEFT JOIN receipt_by_line AS r
  ON (r.purchase_order_id, r.po_line_no)
   = (poi.purchase_order_id, poi.line_no)
ORDER BY po.po_number, poi.line_no;
```

`COALESCE` is used only after the left join: for fulfillment, no receipt means zero delivered and accepted. By contrast, a missing reference price later means “unavailable,” not zero.

The lab contains a multi-line, multi-receipt regression fixture whose assertion fails if ordered value is summed after fan-out. That is stronger than hoping the totals look plausible.

**Checkpoint.** Why not use `SUM(DISTINCT ordered_quantity * po_unit_price)` to repair fan-out? Equal-valued but genuinely different lines would collapse. Fix the grain, not the symptom.

**Bridge.** The join is now structurally safe, but “late” still changes with time. We need a reproducible boundary.

## 4. Dates turn a live system into a snapshot

### Orienting question: why avoid `CURRENT_DATE` in a reproducible report?

The same query should describe the same cutoff tomorrow. Pass dates explicitly in `psql`:

```powershell
podman exec -i prep-week2-postgres psql -X `
  -U procurement -d procurement `
  -v as_of_date=2026-06-30 `
  -v period_start=2026-01-01 `
  -v period_end=2026-07-01
```

Inside the script, read `:'as_of_date'::date`. The colon syntax is `psql` variable substitution, not a native SQL parameter placeholder.

Use half-open reporting periods:

```sql
WHERE ordered_on >= :'period_start'::date
  AND ordered_on <  :'period_end'::date
```

For June, use `[2026-06-01, 2026-07-01)`. The same form works across month and year boundaries. Contract validity uses the same shape: `valid_from <= ordered_on AND ordered_on < valid_to`.

Business calendar facts such as `ordered_on`, `promised_on`, and `received_on` are `date`. The ingestion/audit instant is `timestamptz`. PostgreSQL's time types and time-zone behavior are described in [Date/Time Types](https://www.postgresql.org/docs/18/datatype-datetime.html).

**Checkpoint.** Is a line promised on 30 June delayed at a 30 June cutoff? No. This lab requires `promised_on < as_of_date`.

**Bridge.** With comparable dates defined, a query can ask a smaller question inside a larger one.

## 5. Subqueries express existence and “latest applicable”

### Orienting question: what did the market know when `PO-1042` was ordered?

A subquery answers a bounded question for an outer query. Use `EXISTS` for existence, a scalar subquery only when at most one value is guaranteed, and an explicit latest-row strategy when several historical observations qualify.

For anti-existence, prefer `NOT EXISTS` when null-safe meaning is required:

```sql
SELECT s.supplier_code, s.supplier_name
FROM suppliers AS s
WHERE NOT EXISTS (
    SELECT 1
    FROM purchase_orders AS po
    WHERE po.supplier_id = s.supplier_id
      AND po.lifecycle_status = 'issued'
      AND po.ordered_on >= :'period_start'::date
      AND po.ordered_on <  :'period_end'::date
)
ORDER BY s.supplier_code;
```

`NOT IN (subquery)` can yield unknown when the subquery contains null, because SQL uses three-valued logic. PostgreSQL documents these forms in [Subquery Expressions](https://www.postgresql.org/docs/18/functions-subquery.html).

The price-variance query needs the latest comparable observation from a selected source on or before each PO date. `LEFT JOIN LATERAL` allows the inner relation to refer to the current outer PO line; the left join retains the PO line when no comparable price exists.

```sql
-- Output grain: one currently issued PO line.
SELECT
    po.po_number,
    poi.line_no,
    poi.po_unit_price,
    poi.currency_code,
    poi.unit_code,
    poi.contract_unit_price,
    poi.po_unit_price - poi.contract_unit_price AS contract_variance_per_unit,
    market.price_date,
    market.unit_price AS market_unit_price,
    CASE WHEN market.unit_price IS NULL THEN NULL
         ELSE poi.po_unit_price - market.unit_price
    END AS market_variance_per_unit,
    CASE WHEN market.unit_price IS NULL THEN 'unavailable'
         ELSE 'comparable'
    END AS market_comparison_status
FROM purchase_orders AS po
JOIN purchase_order_items AS poi USING (purchase_order_id)
LEFT JOIN LATERAL (
    SELECT cp.price_date, cp.unit_price
    FROM commodity_prices AS cp
    WHERE cp.product_id = poi.product_id
      AND cp.currency_code = poi.currency_code
      AND cp.unit_code = poi.unit_code
      AND cp.source_code = :'source_code'
      AND cp.price_date <= po.ordered_on
    ORDER BY cp.price_date DESC
    LIMIT 1
) AS market ON true
WHERE po.lifecycle_status = 'issued'
ORDER BY po.po_number, poi.line_no;
```

This is PostgreSQL syntax and behavior, documented under [LATERAL Subqueries](https://www.postgresql.org/docs/18/queries-table-expressions.html#QUERIES-LATERAL). `LATERAL` is not a synonym for “faster correlated subquery”; it makes an outer-row dependency explicit. Inspect the plan when performance matters.

Contract variance and market variance remain separate. A later-only, wrong-source, wrong-currency, or wrong-unit price is not comparable. Null communicates unavailable evidence; zero would falsely claim exact agreement.

**Checkpoint.** Why is `ORDER BY price_date DESC LIMIT 1` inside the lateral subquery? “Latest” is evaluated separately for the current PO line and its order date.

**Bridge.** The subquery solves one nested question. When several intermediate business facts must be composed, name them with CTEs.

## 6. CTEs name intermediate business facts

### Orienting question: can the delayed rule be read from top to bottom?

A common table expression exists for one statement. It helps us name the two relations needed for the delayed result: accepted quantity per line at the cutoff, then line status.

```sql
-- Output grain: one delayed, currently issued PO line at the supplied cutoff.
WITH accepted_as_of AS (
    SELECT
        di.purchase_order_id,
        di.po_line_no,
        SUM(di.accepted_quantity) AS accepted_quantity
    FROM deliveries AS d
    JOIN delivery_items AS di
      ON (di.delivery_id, di.purchase_order_id)
       = (d.delivery_id, d.purchase_order_id)
    WHERE d.received_on <= :'as_of_date'::date
    GROUP BY di.purchase_order_id, di.po_line_no
),
line_status AS (
    SELECT
        po.po_number,
        poi.line_no,
        poi.promised_on,
        poi.ordered_quantity,
        poi.po_unit_price,
        poi.currency_code,
        COALESCE(a.accepted_quantity, 0) AS accepted_quantity
    FROM purchase_orders AS po
    JOIN purchase_order_items AS poi USING (purchase_order_id)
    LEFT JOIN accepted_as_of AS a
      ON (a.purchase_order_id, a.po_line_no)
       = (poi.purchase_order_id, poi.line_no)
    WHERE po.lifecycle_status = 'issued'
)
SELECT
    po_number,
    line_no,
    promised_on,
    ordered_quantity,
    accepted_quantity,
    ordered_quantity - accepted_quantity AS remaining_quantity,
    ROUND((ordered_quantity - accepted_quantity) * po_unit_price, 2)
        AS open_committed_value,
    currency_code
FROM line_status
WHERE promised_on < :'as_of_date'::date
  AND accepted_quantity < ordered_quantity
ORDER BY promised_on, po_number, line_no;
```

For `PO-1042`, the verified fixture returns 870 kg accepted, 130 kg remaining, and USD 1,560 open committed value at 2026-06-30.

A CTE is an expression choice, not an automatic optimization. PostgreSQL can fold or materialize non-recursive CTEs depending on the query and usage. Read [WITH Queries](https://www.postgresql.org/docs/18/queries-with.html) and inspect the actual plan before making a performance claim.

**Checkpoint.** What would an inner join to `accepted_as_of` hide? Every PO line with no receipt—the exact work an open-order report must retain.

**Bridge.** CTEs name stages. Window functions let a stage compare rows without collapsing them.

## 7. Window functions retain detail while comparing rows

### Orienting question: on which receipt date did a line become fully accepted?

`GROUP BY` reduces rows to one per group. A window function calculates across related rows while retaining each input row. For `PO-1042`, first aggregate same-day receipt rows, then run accepted quantity over receipt dates:

```sql
WITH receipt_day AS (
    SELECT
        di.purchase_order_id,
        di.po_line_no,
        d.received_on,
        SUM(di.accepted_quantity) AS accepted_that_day
    FROM deliveries AS d
    JOIN delivery_items AS di
      ON (di.delivery_id, di.purchase_order_id)
       = (d.delivery_id, d.purchase_order_id)
    GROUP BY di.purchase_order_id, di.po_line_no, d.received_on
)
SELECT
    purchase_order_id,
    po_line_no,
    received_on,
    accepted_that_day,
    SUM(accepted_that_day) OVER (
        PARTITION BY purchase_order_id, po_line_no
        ORDER BY received_on
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_accepted
FROM receipt_day
ORDER BY purchase_order_id, po_line_no, received_on;
```

The frame is part of the metric. Same-day aggregation makes ordering deterministic at business-date grain. `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `LAG`, and framed aggregates answer different questions; PostgreSQL documents them in [Window Functions](https://www.postgresql.org/docs/18/functions-window.html).

A three-row frame is not automatically three calendar months:

```sql
SUM(committed_spend) OVER (
    PARTITION BY supplier_id, currency_code
    ORDER BY order_month
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
)
```

If a supplier has no April row, the frame skips April rather than inventing a zero. For three calendar months, generate a calendar spine, left join monthly spend, then window over the completed series.

**Checkpoint.** Why not calculate cumulative acceptance directly over raw delivery items? Multiple receipt rows on one business date would have no deterministic intra-day order, yet the metric only needs day-level completion.

**Bridge.** The running accepted quantity is the first stage of the supplier-quality pipeline. Now make every grain explicit.

## 8. Build one quality pipeline, grain by grain

### Orienting question: how does a receipt become a supplier rank?

The complete executable pipeline is in [20_analytics.sql](../../labs/week-02/sql/20_analytics.sql). Its relations have distinct contracts:

| Relation | Grain | Key derived fields |
| --- | --- | --- |
| `receipt_day` | PO line + receipt date | delivered and accepted that day |
| `running` | PO line + receipt date | cumulative accepted quantity |
| `line_quality` | one PO line with its unit | unit-safe totals, rejected quantity, `fully_accepted_on`, line OTIF, days late |
| `order_quality` | one PO | completion date, order OTIF, order days late; no mixed-unit quantity total |
| supplier rollups | supplier + unit, supplier + currency, or supplier in a declared window | fill, rejection, value, OTIF, lateness, eligibility, rank |

The reusable `line_quality` and `order_quality` views describe all receipts currently loaded, not a historical snapshot at an arbitrary cutoff. The delayed and supplier-performance queries therefore build their own cutoff-aware receipt aggregates and rebuild every downstream stage from the bounded relation; filtering only the final supplier rows would be too late.

### Stage 1: receipt day to line completion

`fully_accepted_on` is the earliest date on which cumulative accepted quantity reaches ordered quantity. An uncompleted line keeps it null.

```sql
MIN(r.received_on) FILTER (
    WHERE r.cumulative_accepted >= poi.ordered_quantity
) AS fully_accepted_on
```

At line grain:

```text
rejected_quantity = delivered_quantity - accepted_quantity
line_otif = fully_accepted_on is not null
            and fully_accepted_on <= promised_on
days_late = max(fully_accepted_on - promised_on, 0), when completed
```

### Stage 2: line completion to order quality

An order is complete only when every line is complete. It is OTIF only when every line is fully accepted by its own promise date. The order's days late is the maximum line lateness:

```sql
SELECT
    purchase_order_id,
    CASE WHEN bool_and(fully_accepted_on IS NOT NULL)
         THEN MAX(fully_accepted_on)
    END AS fully_accepted_on,
    bool_and(line_otif) FILTER (WHERE fully_accepted_on IS NOT NULL)
        AND bool_and(fully_accepted_on IS NOT NULL) AS otif,
    CASE WHEN bool_and(fully_accepted_on IS NOT NULL)
         THEN MAX(days_late)
    END AS days_late
FROM line_quality
GROUP BY purchase_order_id;
```

### Stage 3: order quality to supplier evidence

Supplier performance reports components at compatible grains; it does not hide them in one score:

- accepted fill rate and rejection rate are formed within supplier + unit;
- committed value is formed within supplier + currency;
- completed-order OTIF uses completed orders;
- median days late uses completed orders; and
- open late lines remain a separate count.

Supplier reliability then applies a narrower policy. Include only issued, completed orders whose `fully_accepted_on` is in `[period_start, period_end)`. Compute rejection per line, average those rates within an order, then average eligible orders so kilograms and individual items are never added. Require at least three eligible orders. Rank lexicographically by OTIF descending, rejection rate ascending, then median days late ascending. `RANK()` gives exact metric ties the same rank; supplier code stabilizes display only.

This distinction matters: a supplier below the threshold is **ineligible**, not unreliable. The rank describes the selected period and policy; it does not establish future performance or causality.

**Checkpoint.** Why must the reliability calculation use the same eligible order set for all three ranking components? Mixing samples would make the tuple internally inconsistent.

**Bridge.** The pipeline now supports all five operational answers without changing grain mid-metric.

## 9. The five analyses and their exact meanings

### 9.1 Delayed PO lines

Use the query from section 6.

- **Grain:** one delayed, currently issued PO line at `as_of_date`.
- **Rule:** `promised_on < as_of_date` and accepted through cutoff is below ordered.
- **Absence:** no receipt means zero accepted, so the line remains visible.
- **Boundary:** order-level delay is derived as “any line delayed”; it is not stored as a second truth.

### 9.2 Monthly procurement spend

```sql
-- Output grain: original order month and currency.
SELECT
    date_trunc('month', po.ordered_on)::date AS order_month,
    poi.currency_code,
    ROUND(SUM(poi.ordered_quantity * poi.po_unit_price), 2) AS committed_spend
FROM purchase_orders AS po
JOIN purchase_order_items AS poi USING (purchase_order_id)
WHERE po.lifecycle_status = 'issued'
  AND po.ordered_on >= :'period_start'::date
  AND po.ordered_on <  :'period_end'::date
GROUP BY date_trunc('month', po.ordered_on)::date, poi.currency_code
ORDER BY order_month, poi.currency_code;
```

This means **currently issued commitments grouped by original order month**. It is not delivered, invoiced, paid, or accounting spend. It is also not a historical month-end snapshot: if an order is cancelled later, rerunning the query removes it from its original month because the schema stores current lifecycle state, not status history. Historical as-of spend would require an effective-dated status history or event log.

Aggregate exact line products and round once at the reporting boundary. The fixture uses two-decimal output; that choice is explicit rather than universal.

### 9.3 Price variance

Use the query from section 5.

- **Contract baseline:** PO price minus the snapshotted contract price.
- **Market baseline:** PO price minus the latest comparable selected-source observation on or before order date.
- **Comparability:** product, currency, and unit must match.
- **Missing evidence:** return null/unavailable, never zero.

### 9.4 Supplier performance

The [verified analytical query](../../labs/week-02/sql/20_analytics.sql) rebuilds receipt facts using only `received_on <= as_of_date` and excludes POs ordered after that cutoff. It returns three deliberately separate grains:

- **supplier and unit:** accepted fill rate, rejection rate, and open late lines;
- **supplier:** completed-order OTIF and median days late; and
- **supplier and currency:** committed value.

This separation prevents kilograms and individual items from being summed into one physical quantity, and prevents USD and another currency from becoming one monetary value. The rates are dimensionless only after their numerator and denominator have been formed within a compatible unit. No opaque composite score hides which behavior changed.

The reusable `line_quality` and `order_quality` views remain useful current-state teaching relations, but they use all loaded receipts. Historical supplier performance must use the parameterized cutoff-bounded query, not those lifetime views directly.

### 9.5 Most reliable suppliers

Reliability uses another cutoff-bounded pipeline:

```text
receipts before period_end
  -> per-line completion and rejection rate
  -> per-order OTIF, lateness, and mean line rejection rate
  -> orders completed inside [period_start, period_end)
  -> suppliers with at least three eligible orders
  -> RANK by OTIF desc, rejection asc, median lateness asc
```

Computing rejection per line, then averaging lines within an order and eligible orders within a supplier, avoids adding quantities with incompatible units. Receipts at or after `period_end` cannot retroactively change the ranking. The complete executable CTE is in [20_analytics.sql](../../labs/week-02/sql/20_analytics.sql); the synthetic result ranks `SUP-A` before `SUP-B`, while `SUP-C` is ineligible with only two completed orders.

**Checkpoint.** Which analysis can answer “cash paid in March”? None. The model has no invoices or payments, and committed PO value is not cash flow.

**Bridge.** Correct results come before fast results. Index only the access paths the queries actually use.

## 10. Index observed access paths

### Orienting question: why can a sequential scan be the correct plan?

An index adds a read path, storage, and write maintenance. For a small table or a predicate returning much of a table, a sequential scan can cost less. PostgreSQL's planner uses statistics and estimates; inspect the chosen path with [Using EXPLAIN](https://www.postgresql.org/docs/18/using-explain.html).

The schema retains indexes that support verified join/filter paths:

```sql
CREATE INDEX deliveries_po_received_idx
    ON deliveries (purchase_order_id, received_on, delivery_id);

CREATE INDEX delivery_items_po_line_idx
    ON delivery_items (purchase_order_id, po_line_no, delivery_id);

CREATE INDEX purchase_order_items_promised_idx
    ON purchase_order_items (promised_on, purchase_order_id, line_no);

CREATE INDEX purchase_orders_ordered_idx
    ON purchase_orders (ordered_on, purchase_order_id);
```

Primary-key and unique constraints already create indexes. PostgreSQL does not automatically create an index on every foreign-key referencing side. For B-tree multi-column indexes, leading columns strongly shape which predicates can use the access path; see [Multicolumn Indexes](https://www.postgresql.org/docs/18/indexes-multicolumn.html).

The latest-price lookup motivates this workload-matched candidate:

```sql
CREATE INDEX commodity_prices_lookup_idx
    ON commodity_prices (
        product_id, currency_code, unit_code, source_code, price_date DESC
    );
```

The repository's [80_index_probe.sql](../../labs/week-02/sql/80_index_probe.sql) loads a rolled-back 50,000-row temporary price relation and captures JSON plans before and after the candidate index. That demonstrates how to gather environment-specific evidence; it is not a production benchmark or a promise that the planner always selects the index.

### Partial-index boundary

A tempting candidate is:

```sql
CREATE INDEX purchase_orders_current_issued_idx
    ON purchase_orders (ordered_on, supplier_id)
    WHERE lifecycle_status = 'issued';
```

The lab does not retain it. A partial index helps only when its smaller predicate matches an important workload and the planner can prove the query predicate implies the index predicate. Parameterized conditions can prevent that proof at planning time. PostgreSQL documents this limitation in [Partial Indexes](https://www.postgresql.org/docs/18/indexes-partial.html). Validate the exact prepared-query behavior and write cost before adopting it.

The evidence loop is simple:

```sql
ANALYZE;
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT ...;
```

Freeze query, parameters, fixture scale, and server configuration. Compare correctness first, then estimates versus actual rows, buffers, plan shape, and time.

**Checkpoint.** If an index scan appears after adding an index, have we proved production improvement? No. We observed one plan under one dataset and configuration.

**Bridge.** Indexes help reads. They do not make a multi-statement write atomic or safe under concurrency.

## 11. Transactions first protect atomic work

### Orienting question: what should happen if PO line 2 fails after the header and line 1 were inserted?

A transaction makes related writes succeed or fail as one unit. In `psql`, a small header-and-lines workflow can be expressed as:

```sql
BEGIN;

INSERT INTO purchase_orders (
    po_number, supplier_id, contract_id, ordered_on, lifecycle_status
)
VALUES ('PO-NEW', 1, 1, DATE '2026-06-30', 'draft')
RETURNING purchase_order_id \gset

INSERT INTO purchase_order_items (
    purchase_order_id, line_no, product_id,
    contract_id, contract_item_no,
    ordered_quantity, po_unit_price, contract_unit_price,
    currency_code, unit_code, promised_on
)
VALUES
    (:'purchase_order_id', 1, 1, 1, 1, 100, 12, 11.5, 'USD', 'kg', DATE '2026-07-10'),
    (:'purchase_order_id', 2, 3, 1, 3, 50, 2.1, 2, 'USD', 'ea', DATE '2026-07-12');

ROLLBACK;  -- Replace with COMMIT only in a disposable copy you intend to mutate.
```

`\gset` is a `psql` meta-command. This example rolls back so it does not break the deterministic fixture counts. In a real write, commit only after every statement succeeds; if an insert violates a constraint, roll back so the header and earlier lines do not remain as a partial business object. Atomicity does not by itself define who may see which changes or how simultaneous writers interact. PostgreSQL's [Transaction Isolation](https://www.postgresql.org/docs/18/transaction-iso.html) covers visibility and isolation behavior.

**Checkpoint.** Does `BEGIN` make invalid business data valid? No. Constraints and write protocols still reject it; the transaction controls the unit of commit or rollback.

**Bridge.** Atomicity handles failure inside one workflow. Row locks handle two workflows competing for the same remaining quantity.

## 12. Concurrency needs a shared lock order

### Orienting question: what if two receipts each consume the same 130 kg remaining on `PO-1042`?

If both sessions read 130 kg and each accepts 100 kg, a check-then-insert sequence can over-accept. A row-local delivery check cannot see the aggregate across receipt rows.

The lab's [30_transactions.sql](../../labs/week-02/sql/30_transactions.sql) exposes `record_delivery(...)` and `cancel_purchase_order(...)`. Both protocols:

1. begin inside the caller's transaction;
2. lock the PO header first;
3. require an issued PO for delivery;
4. lock target lines in ascending line order;
5. recompute accepted quantity while the locks are held;
6. reject aggregate over-acceptance;
7. insert the delivery header and lines atomically; and
8. commit or roll back.

Cancellation locks the same header before changing status. Its trigger proves there is no accepted receipt. A fully rejected physical delivery has zero accepted quantity and does not alone prevent cancellation under this lab rule.

The two-session fixture verifies the boundary rather than inferring it. When two 100 kg acceptances raced against 130 kg remaining, one committed, the other was rejected, and the final accepted total was 970 kg. When first acceptance raced cancellation, delivery committed, cancellation was rejected, and the PO remained issued.

Those are observations under the recorded PostgreSQL lab, not universal timing guarantees. Applications should distinguish a domain rejection from SQLSTATE `40001` serialization failure and `40P01` deadlock, and apply bounded retry policy only to retryable failures.

Direct inserts into delivery tables bypass the aggregate invariant. A production design would restrict table-write privileges and expose the validated function boundary. The local lab does not implement production authorization.

**Checkpoint.** Why do delivery and cancellation both lock the header first? They serialize incompatible state transitions at one shared boundary and reduce inconsistent lock ordering.

**Bridge.** The normalized write model is now correct under the tested transition. Faster reads may still justify a derived model.

## 13. Denormalization is a freshness contract

### Orienting question: should every dashboard recompute the full pipeline?

A supplier-month summary or materialized view can reduce repeated read work. It is derived evidence, not a new source of truth:

```text
normalized PO and receipt facts
             |
             +--> supplier_month_summary --> dashboard
```

Before using it, define refresh cadence, freshness timestamp, lineage to source rows, correction behavior, and reconciliation checks. A fast stale summary is still wrong for a live operational decision.

Do not confuse this with a PO snapshot. A PO line's historical price is an event fact required to preserve the commitment. A supplier-month total is recomputable and may become stale.

**Checkpoint.** What additional structure would make the monthly spend query historically reproducible after cancellation? An effective-dated lifecycle history or append-only status event stream, plus an as-of reconstruction rule.

**Bridge.** The model is complete enough to challenge. The exercises force every hidden boundary into the answer.

## 14. Exercises

Keep solutions separate. For each exercise, write the metric contract before SQL and test at least one row that defeats a plausible naive query.

### Eight medium SQL problems

1. **Active contract exposure**
   - Grain/columns: one contract item; contract code/version, supplier, product, term price/unit/currency, currently issued committed value.
   - Check: retain an active term with no PO and show zero commitment only after the left join.
   - Trap: joining receipts into the monetary total; treating `valid_to` as inclusive.
   - Follow-up: how would overlapping eligible agreements be surfaced without guessing one?

2. **Suppliers with no completed PO**
   - Grain/columns: one supplier; code, name, qualifying-order count.
   - Check: use a half-open period and include a supplier with POs but no completed PO.
   - Trap: `NOT IN` with a nullable subquery result; equating issued with completed.
   - Follow-up: when would an anti-join and `NOT EXISTS` produce different plans but the same semantics?

3. **PO-line fulfillment trace**
   - Grain/columns: one PO line; ordered, delivered, accepted, remaining, `fully_accepted_on`.
   - Check: cover no receipt, several receipt dates, rejection, and exact completion.
   - Trap: finding the first receipt instead of the first cumulative-full date.
   - Follow-up: how would returns or corrections invalidate monotonic cumulative acceptance?

4. **Market-price exception**
   - Grain/columns: one issued PO line above a supplied threshold; PO price, selected baseline date/price, percentage variance, comparison status.
   - Check: later-only, wrong-source, wrong-currency, and wrong-unit observations remain unavailable.
   - Trap: selecting the globally latest price or converting null to zero.
   - Follow-up: compare a `LATERAL` lookup with a window-ranked candidate-price relation.

5. **Supplier-month trend**
   - Grain/columns: supplier, currency, calendar month, committed spend, three-calendar-month total.
   - Check: include an empty middle month through a calendar spine.
   - Trap: `ROWS 2 PRECEDING` over observed months and calling it three calendar months.
   - Follow-up: what lifecycle history is needed for a historical month-end view?

6. **Product-specific reliability**
   - Grain/columns: product and eligible supplier; sample size, OTIF, rejection, lateness, rank.
   - Check: exact metric ties share a rank; below-threshold suppliers are excluded explicitly.
   - Trap: mixing line-level and order-level OTIF or changing the eligible set per component.
   - Follow-up: when is `DENSE_RANK` preferable to `RANK` for downstream presentation?

7. **First delayed PO per supplier**
   - Grain/columns: one supplier; PO, first delayed date, current remaining accepted quantity.
   - Check: define “first” as the earliest promise date strictly before the cutoff, then use deterministic tie-breaking.
   - Trap: ranking before filtering to actually delayed lines.
   - Follow-up: how would a first-observed-delay event differ from reconstructing delay at one cutoff?

8. **Contract-term overlap audit**
   - Grain/columns: one overlapping supplier/product agreement pair; both contract codes and validity ranges.
   - Check: adjacent `[start, end)` ranges are not overlaps; true containment is.
   - Trap: comparing contract headers without matching their product terms.
   - Follow-up: should overlap be prohibited, warned, or versioned, and what business rule decides?

### Two product-analytics problems

9. **Supplier cohorts**
   - Grain/columns: first-PO quarter and first-three-completed-order position; supplier count, OTIF, rejection, lateness.
   - Check: freeze cohort assignment, preserve suppliers with fewer than three observable completions, and expose sample size.
   - Trap: survivorship bias, right censoring, and comparing calendar periods with different exposure.
   - Follow-up: what question can a cohort comparison answer, and what causal claim can it not support?

10. **Ordered-value-weighted delay exposure**
    - Grain/columns: cutoff, currency, supplier; delayed open committed value, total eligible value, weighted exposure, late-order rate.
    - Check: compute at line grain before supplier rollup and keep currencies separate.
    - Trap: fan-out, mixing accepted and delivered remaining quantity, or letting one high-value order disappear inside an unweighted rate.
    - Follow-up: how do line-, order-, and supplier-level denominators change prioritization?

## 15. Common mistakes and their corrective question

### “The total looks plausible.”

What is the grain on each side of every join, and can either side match more than once?

### “No receipt means no row.”

Does absence carry business meaning? An open-work query usually needs the left row preserved.

### “Delivered means fulfilled.”

Is the process measuring physical arrival, inspection acceptance, invoice match, or payment? Name the event.

### “The latest price is the greatest date.”

Latest relative to which order date, source, product, currency, and unit?

### “A CTE or index makes it faster.”

What plan and representative dataset support that claim on the active PostgreSQL version?

### “The transaction removes the race.”

Which rows are locked, in what order, and what does the caller do with business rejection, `40001`, or `40P01`?

### “March spend is a March snapshot.”

Does the schema retain lifecycle history? Here it does not: the query groups current issued commitments by original order month.

### “Reliability is a fact column.”

Which window, completed-order rule, denominator, eligibility threshold, missing-data behavior, and tie policy define it?

## 16. Interview defense

**How does join fan-out corrupt financial results?**

One PO line owns one ordered amount; several delivery items match it. Summing after the join repeats the amount. Aggregate receipts to the line key first, then join one-to-one. `SUM(DISTINCT ...)` is unsafe because distinct legitimate lines may share a value.

**`WHERE` versus `HAVING`; aggregate versus window?**

`WHERE` filters source rows before grouping; `HAVING` filters groups after aggregation. `GROUP BY` reduces to group grain. A window computes across related rows while retaining input rows; its partition, order, and frame belong to the metric.

**Subquery, `LATERAL`, or CTE?**

Use `EXISTS` for existence, a scalar subquery only for one guaranteed value, `LATERAL` for an explicit outer-row-dependent relation such as latest applicable price, and a CTE to name composed intermediate facts. None has a universal performance advantage.

**Why can `NOT IN` fail an anti-join expectation?**

A null from the subquery can make comparisons unknown. `NOT EXISTS` states “no qualifying row exists” directly and is usually the safer semantic choice.

**How do you find the latest applicable price?**

Filter by product, selected source, currency, unit, and `price_date <= ordered_on`; order descending by price date and take one row per PO line. Preserve a missing match as unavailable.

**How do you choose composite-index order?**

Start with actual equality, range, join, and ordering predicates; account for existing key indexes and writes; then inspect estimates and actual execution. A partial index additionally requires the planner to prove predicate implication.

**Normalization versus snapshots versus read models?**

Normalize independently changing identities and events. Snapshot PO commercial terms to preserve historical commitment. Treat summaries as derived, freshness-bound data requiring lineage and reconciliation.

**Atomicity versus isolation versus locking?**

Atomicity commits or rolls back one unit. Isolation controls visibility and permitted anomalies between transactions. Row locks serialize conflicting business transitions; deterministic lock order reduces deadlock risk. Retry only failures classified as retryable.

**Why is the monthly spend result not historical as-of spend?**

It filters the current PO lifecycle and groups by original order month. A later cancellation changes an earlier month's recomputed value. Historical as-of reporting needs lifecycle history and reconstruction semantics.

**Why is supplier reliability not universal?**

It depends on the reporting window, completion definition, denominators, sample threshold, tie behavior, missing evidence, and data quality. Report the components and policy before the rank.

**What is intentionally absent?**

Invoices, payments, taxes, FX, unit conversion, returns, corrections, authentication, warehouse models, and production deployment controls. The omission keeps “committed value” from masquerading as accounting truth.

## 17. Active recall

1. What is the grain of `delivery_items`?
2. Why is a PO's contract price snapshot not a normalization mistake?
3. Why aggregate receipt facts before joining PO monetary facts?
4. When is absence zero, and when is it unavailable?
5. Why use half-open date ranges?
6. What does `LATERAL` make explicit?
7. Why is a three-row window not necessarily three calendar months?
8. Which grains connect `receipt_day` to a supplier rank?
9. Why can a sequential scan be correct?
10. What can a partial-index predicate prevent?
11. What does `BEGIN` protect before concurrency is considered?
12. Why do delivery and cancellation lock the PO header first?
13. What history is missing from the monthly spend metric?
14. Which definition choices make reliability reproducible?

## Next action: trace `PO-1042` yourself

Run the lab appendix, then do three things in order:

1. Query the source rows for `PO-1042` in `purchase_orders`, `purchase_order_items`, `deliveries`, and `delivery_items`; write the grain beside every result.
2. Run the deliberately naive fan-out join, predict the wrong value before seeing it, then repair it by pre-aggregating receipts.
3. Change only `as_of_date` and explain every row that enters or leaves the delayed result. Then run [90_verify.sql](../../labs/week-02/sql/90_verify.sql) to confirm that your schema and fixture still satisfy the deterministic assertions.

Do not start with the supplier leaderboard. Earn it by tracing receipt-day facts into line completion, order quality, and finally the supplier rollup.

## Appendix: Podman-first PostgreSQL lab

The repository lab targets PostgreSQL 18.4 in a rootless Podman machine and pins this Linux/AMD64 image digest:

```text
docker.io/library/postgres:18.4@sha256:4cc13dede823cab4e05290c7fb3350fb4e599ecabd9b07e6706b5d5e8f5bc929
```

Initialize the named Podman machine only if it does not already exist:

```powershell
podman machine init prep-week2 --cpus 2 --memory 2048 --disk-size 20
podman machine start prep-week2
```

Pull and inspect the pinned image, then start the loopback-only lab. Supply a local non-production password at runtime; do not commit it.

```powershell
podman pull docker.io/library/postgres:18.4@sha256:4cc13dede823cab4e05290c7fb3350fb4e599ecabd9b07e6706b5d5e8f5bc929
podman image inspect docker.io/library/postgres:18.4@sha256:4cc13dede823cab4e05290c7fb3350fb4e599ecabd9b07e6706b5d5e8f5bc929

$env:POSTGRES_PASSWORD = Read-Host 'Local lab password'
podman volume create prep-week2-pgdata
podman run --detach --name prep-week2-postgres --pull=never `
  --env POSTGRES_DB=procurement `
  --env POSTGRES_USER=procurement `
  --env POSTGRES_PASSWORD `
  --publish 127.0.0.1:5432:5432 `
  --volume prep-week2-pgdata:/var/lib/postgresql `
  docker.io/library/postgres:18.4@sha256:4cc13dede823cab4e05290c7fb3350fb4e599ecabd9b07e6706b5d5e8f5bc929

podman exec prep-week2-postgres pg_isready -U procurement -d procurement
```

Apply the executable artifacts in order. `00_schema.sql` drops and recreates schema `week2`; rerunning it deletes all current lab data.

```powershell
Get-Content -Raw labs/week-02/sql/00_schema.sql |
  podman exec -i prep-week2-postgres psql -X -U procurement -d procurement
Get-Content -Raw labs/week-02/sql/30_transactions.sql |
  podman exec -i prep-week2-postgres psql -X -U procurement -d procurement
Get-Content -Raw labs/week-02/sql/10_seed.sql |
  podman exec -i prep-week2-postgres psql -X -U procurement -d procurement
Get-Content -Raw labs/week-02/sql/20_analytics.sql |
  podman exec -i prep-week2-postgres psql -X -U procurement -d procurement
Get-Content -Raw labs/week-02/sql/80_index_probe.sql |
  podman exec -i prep-week2-postgres psql -X -U procurement -d procurement
Get-Content -Raw labs/week-02/sql/90_verify.sql |
  podman exec -i prep-week2-postgres psql -X -U procurement -d procurement
```

Check the exact names before cleanup. Removing the named volume permanently deletes this lab's PostgreSQL data:

```powershell
podman stop prep-week2-postgres
podman rm prep-week2-postgres
podman volume rm prep-week2-pgdata
```

This is a synthetic local learning environment. It does not supply production backups, TLS, secret management, authorization, monitoring, migrations, or recovery design.

## Primary sources and further reading

- [PostgreSQL 18: Constraints](https://www.postgresql.org/docs/18/ddl-constraints.html)
- [PostgreSQL 18: Numeric Types](https://www.postgresql.org/docs/18/datatype-numeric.html) and [Monetary Types](https://www.postgresql.org/docs/18/datatype-money.html)
- [PostgreSQL 18: Date/Time Types](https://www.postgresql.org/docs/18/datatype-datetime.html)
- [PostgreSQL 18: Aggregate Functions](https://www.postgresql.org/docs/18/functions-aggregate.html)
- [PostgreSQL 18: Subquery Expressions](https://www.postgresql.org/docs/18/functions-subquery.html) and [LATERAL Subqueries](https://www.postgresql.org/docs/18/queries-table-expressions.html#QUERIES-LATERAL)
- [PostgreSQL 18: WITH Queries](https://www.postgresql.org/docs/18/queries-with.html)
- [PostgreSQL 18: Window Functions](https://www.postgresql.org/docs/18/functions-window.html)
- [PostgreSQL 18: Transaction Isolation](https://www.postgresql.org/docs/18/transaction-iso.html)
- [PostgreSQL 18: Explicit Locking](https://www.postgresql.org/docs/18/explicit-locking.html)
- [PostgreSQL 18: CREATE FUNCTION](https://www.postgresql.org/docs/18/sql-createfunction.html) and [CREATE TRIGGER](https://www.postgresql.org/docs/18/sql-createtrigger.html)
- [PostgreSQL 18: Multicolumn Indexes](https://www.postgresql.org/docs/18/indexes-multicolumn.html), [Partial Indexes](https://www.postgresql.org/docs/18/indexes-partial.html), and [Using EXPLAIN](https://www.postgresql.org/docs/18/using-explain.html)
- [Podman: machine init](https://docs.podman.io/en/latest/markdown/podman-machine-init.1.html) and [podman run](https://docs.podman.io/en/latest/markdown/podman-run.1.html)
- [Docker Official Image: PostgreSQL](https://hub.docker.com/_/postgres)
