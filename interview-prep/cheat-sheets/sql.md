---
layout: "week"
status: "approved"
version: "1.0.0"
last_reviewed: "2026-11-09"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "SQL interview cheat sheet"
description: "SQL and database revision for Data Science, ML, analytics, and AI engineering interviews."
summary: "Revise query correctness, joins, windows, analytical patterns, transactions, indexing, and senior-level data reasoning."
permalink: "/interview-prep/cheat-sheets/sql/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 1 · SQL"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 1 source:** This page integrates the previously prepared revision artifact into the Prep site. It is separate from the Week 1–20 learning assessments.

**Target roles:** Lead Data Scientist, AI/ML Engineer, Analytics/Data Science roles  
**Dialect used:** PostgreSQL-style SQL; adapt date and percentile functions for the interview database.

## 1. Thirty-second revision

- Logical order: `FROM/JOIN → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT`.
- `WHERE` filters rows before aggregation; `HAVING` filters groups after aggregation.
- A one-to-many join can silently multiply rows and inflate metrics.
- Window functions retain row detail; aggregation collapses rows.
- Use `ROW_NUMBER` for one chosen row, `RANK` with gaps, and `DENSE_RANK` without gaps.
- Treat `NULL` with three-valued logic: compare with `IS NULL`, not `= NULL`.
- In senior interviews, explain correctness, grain, indexes, data skew, and point-in-time behavior.

## 2. Example schema

```sql
users(
    user_id       BIGINT PRIMARY KEY,
    signup_date   DATE NOT NULL,
    country       TEXT
)

orders(
    order_id      BIGINT PRIMARY KEY,
    user_id       BIGINT NOT NULL,
    order_time    TIMESTAMP NOT NULL,
    amount        NUMERIC(12, 2) NOT NULL,
    status        TEXT NOT NULL
)

events(
    event_id      BIGINT PRIMARY KEY,
    user_id       BIGINT NOT NULL,
    event_time    TIMESTAMP NOT NULL,
    event_name    TEXT NOT NULL
)

employees(
    employee_id   BIGINT PRIMARY KEY,
    department    TEXT NOT NULL,
    salary        NUMERIC(12, 2) NOT NULL
)
```

Always establish the **grain**: one row represents one user, one order, one event, or one daily aggregate.

## 3. Query structure and evaluation order

```sql
SELECT
    u.country,
    COUNT(DISTINCT o.user_id) AS purchasing_users,
    SUM(o.amount) AS revenue
FROM users AS u
JOIN orders AS o
  ON o.user_id = u.user_id
WHERE o.status = 'completed'
  AND o.order_time >= TIMESTAMP '2026-10-01'
GROUP BY u.country
HAVING SUM(o.amount) >= 10000
ORDER BY revenue DESC
LIMIT 10;
```

Aliases defined in `SELECT` are generally unavailable in `WHERE` because `WHERE` is logically evaluated earlier. Many dialects allow the alias in `ORDER BY`.

## 4. `NULL` and three-valued logic

`NULL` means unknown/missing, not zero or an empty string.

```sql
SELECT *
FROM users
WHERE country IS NULL;

SELECT
    COALESCE(country, 'unknown') AS country_label,
    COUNT(*) AS users
FROM users
GROUP BY COALESCE(country, 'unknown');
```

Important rules:

- `NULL = NULL` is unknown, not true.
- `COUNT(*)` counts rows; `COUNT(column)` ignores `NULL` values.
- `NOT IN` can return surprising results when its subquery contains `NULL`; prefer `NOT EXISTS`.
- `COALESCE(a, b, c)` returns the first non-null value.
- Use `NULLIF(denominator, 0)` to prevent division by zero.

```sql
SELECT
    successful_requests * 1.0 / NULLIF(total_requests, 0) AS success_rate
FROM service_metrics;
```

## 5. Joins and row multiplication

| Join | Keeps |
|---|---|
| `INNER JOIN` | Matching rows from both sides |
| `LEFT JOIN` | Every left row plus matches/nulls from right |
| `FULL OUTER JOIN` | All rows from both sides |
| `CROSS JOIN` | Every combination |
| `EXISTS` | Tests whether a match exists without returning/multiplying match rows |

### Semi-join: users with at least one completed order

```sql
SELECT u.*
FROM users AS u
WHERE EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.user_id = u.user_id
      AND o.status = 'completed'
);
```

### Anti-join: users with no completed order

```sql
SELECT u.*
FROM users AS u
WHERE NOT EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.user_id = u.user_id
      AND o.status = 'completed'
);
```

### The inflated-metric trap

If a user has three orders and four support tickets, joining both detail tables by `user_id` creates 12 rows. Aggregate each child table to the required grain before joining.

```sql
WITH order_totals AS (
    SELECT user_id, SUM(amount) AS revenue
    FROM orders
    WHERE status = 'completed'
    GROUP BY user_id
),
ticket_totals AS (
    SELECT user_id, COUNT(*) AS tickets
    FROM support_tickets
    GROUP BY user_id
)
SELECT
    u.user_id,
    COALESCE(o.revenue, 0) AS revenue,
    COALESCE(t.tickets, 0) AS tickets
FROM users AS u
LEFT JOIN order_totals AS o USING (user_id)
LEFT JOIN ticket_totals AS t USING (user_id);
```

## 6. Aggregation and conditional aggregation

```sql
SELECT
    DATE(order_time) AS order_date,
    COUNT(*) AS total_orders,
    COUNT(*) FILTER (WHERE status = 'completed') AS completed_orders,
    SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END) AS revenue,
    AVG(amount) FILTER (WHERE status = 'completed') AS average_order_value
FROM orders
GROUP BY DATE(order_time)
ORDER BY order_date;
```

Portable conditional count:

```sql
SUM(CASE WHEN condition THEN 1 ELSE 0 END)
```

Be clear whether a metric needs `COUNT(*)`, `COUNT(order_id)`, or `COUNT(DISTINCT user_id)`.

## 7. CTEs, subqueries, and set operations

- Use a CTE to name a logical stage and make grain explicit.
- A correlated subquery executes conceptually per outer row; the optimizer may transform it.
- `UNION` removes duplicates; `UNION ALL` preserves them and is usually faster.
- Recursive CTEs handle hierarchies, graph traversal, and generated sequences.

```sql
WITH RECURSIVE numbers AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1
    FROM numbers
    WHERE n < 10
)
SELECT n FROM numbers;
```

## 8. Window functions

General form:

```sql
function(...) OVER (
    PARTITION BY ...
    ORDER BY ...
    ROWS BETWEEN ... AND ...
)
```

| Function | Use |
|---|---|
| `ROW_NUMBER()` | Unique sequence; select one row per group |
| `RANK()` | Ties share rank and leave gaps |
| `DENSE_RANK()` | Ties share rank without gaps |
| `LAG()/LEAD()` | Previous/next row |
| `FIRST_VALUE()/LAST_VALUE()` | Boundary value; frame definition matters |
| Aggregate over window | Running/rolling totals without collapsing rows |

### Latest order per user

```sql
WITH ranked AS (
    SELECT
        o.*,
        ROW_NUMBER() OVER (
            PARTITION BY user_id
            ORDER BY order_time DESC, order_id DESC
        ) AS row_number
    FROM orders AS o
)
SELECT *
FROM ranked
WHERE row_number = 1;
```

The second sort key makes tie handling deterministic.

### Second-highest distinct salary

```sql
WITH ranked AS (
    SELECT
        salary,
        DENSE_RANK() OVER (ORDER BY salary DESC) AS salary_rank
    FROM employees
)
SELECT DISTINCT salary
FROM ranked
WHERE salary_rank = 2;
```

### Top three employees per department

```sql
WITH ranked AS (
    SELECT
        e.*,
        DENSE_RANK() OVER (
            PARTITION BY department
            ORDER BY salary DESC
        ) AS salary_rank
    FROM employees AS e
)
SELECT *
FROM ranked
WHERE salary_rank <= 3;
```

## 9. Solved interview patterns

### Pattern 1: deduplicate and keep the newest row

```sql
WITH ranked AS (
    SELECT
        p.*,
        ROW_NUMBER() OVER (
            PARTITION BY natural_key
            ORDER BY updated_at DESC, record_id DESC
        ) AS row_number
    FROM predictions AS p
)
SELECT *
FROM ranked
WHERE row_number = 1;
```

### Pattern 2: day-over-day change

```sql
WITH daily AS (
    SELECT
        DATE(order_time) AS order_date,
        SUM(amount) AS revenue
    FROM orders
    WHERE status = 'completed'
    GROUP BY DATE(order_time)
)
SELECT
    order_date,
    revenue,
    revenue - LAG(revenue) OVER (ORDER BY order_date) AS absolute_change,
    100.0 * (revenue / NULLIF(LAG(revenue) OVER (ORDER BY order_date), 0) - 1)
        AS percentage_change
FROM daily
ORDER BY order_date;
```

### Pattern 3: seven-row rolling average

```sql
WITH daily AS (
    SELECT
        DATE(order_time) AS order_date,
        SUM(amount) AS revenue
    FROM orders
    WHERE status = 'completed'
    GROUP BY DATE(order_time)
)
SELECT
    order_date,
    revenue,
    AVG(revenue) OVER (
        ORDER BY order_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_seven_row_average
FROM daily;
```

This is seven **rows**, not necessarily seven calendar days. For calendar-day logic, join to a complete date spine first.

### Pattern 4: consecutive active-day streaks (gaps and islands)

```sql
WITH distinct_days AS (
    SELECT DISTINCT user_id, DATE(event_time) AS activity_date
    FROM events
),
numbered AS (
    SELECT
        user_id,
        activity_date,
        ROW_NUMBER() OVER (
            PARTITION BY user_id
            ORDER BY activity_date
        ) AS row_number
    FROM distinct_days
),
islands AS (
    SELECT
        user_id,
        activity_date,
        activity_date - row_number * INTERVAL '1 day' AS island_key
    FROM numbered
)
SELECT
    user_id,
    MIN(activity_date) AS streak_start,
    MAX(activity_date) AS streak_end,
    COUNT(*) AS streak_days
FROM islands
GROUP BY user_id, island_key
ORDER BY user_id, streak_start;
```

### Pattern 5: Day-1 retention by signup cohort

```sql
SELECT
    u.signup_date,
    COUNT(DISTINCT u.user_id) AS new_users,
    COUNT(DISTINCT e.user_id) AS retained_users,
    COUNT(DISTINCT e.user_id) * 1.0
        / NULLIF(COUNT(DISTINCT u.user_id), 0) AS day_1_retention
FROM users AS u
LEFT JOIN events AS e
  ON e.user_id = u.user_id
 AND DATE(e.event_time) = u.signup_date + INTERVAL '1 day'
GROUP BY u.signup_date
ORDER BY u.signup_date;
```

Define whether “Day 1” means the next calendar day or 24–48 hours after signup.

### Pattern 6: ordered funnel

```sql
WITH event_times AS (
    SELECT
        user_id,
        MIN(event_time) FILTER (WHERE event_name = 'view') AS view_time,
        MIN(event_time) FILTER (WHERE event_name = 'add_to_cart') AS cart_time,
        MIN(event_time) FILTER (WHERE event_name = 'purchase') AS purchase_time
    FROM events
    GROUP BY user_id
)
SELECT
    COUNT(*) FILTER (WHERE view_time IS NOT NULL) AS viewed,
    COUNT(*) FILTER (
        WHERE cart_time IS NOT NULL
          AND cart_time >= view_time
    ) AS added_after_view,
    COUNT(*) FILTER (
        WHERE purchase_time IS NOT NULL
          AND cart_time >= view_time
          AND purchase_time >= cart_time
    ) AS purchased_after_cart
FROM event_times;
```

For repeated sessions or multiple funnel attempts, build sessions/attempt IDs first; global minimum timestamps can misclassify behavior.

### Pattern 7: median

```sql
SELECT
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) AS median_order_amount
FROM orders
WHERE status = 'completed';
```

`PERCENTILE_CONT` may interpolate; `PERCENTILE_DISC` chooses an observed value.

### Pattern 8: A/B conversion rate

```sql
WITH user_outcomes AS (
    SELECT
        a.experiment_group,
        a.user_id,
        MAX(CASE WHEN e.event_name = 'purchase' THEN 1 ELSE 0 END) AS converted
    FROM assignments AS a
    LEFT JOIN events AS e
      ON e.user_id = a.user_id
     AND e.event_time >= a.assigned_at
     AND e.event_time < a.assigned_at + INTERVAL '7 days'
    WHERE a.experiment_name = 'checkout_v2'
    GROUP BY a.experiment_group, a.user_id
)
SELECT
    experiment_group,
    COUNT(*) AS assigned_users,
    SUM(converted) AS converted_users,
    AVG(converted * 1.0) AS conversion_rate
FROM user_outcomes
GROUP BY experiment_group;
```

The assignment table—not the event table—must define the denominator.

## 10. Point-in-time correct feature joins

Never join a training row to information created after its prediction timestamp.

```sql
SELECT
    p.prediction_id,
    p.user_id,
    p.prediction_time,
    f.feature_value,
    f.feature_time
FROM prediction_examples AS p
LEFT JOIN LATERAL (
    SELECT feature_value, feature_time
    FROM feature_history AS f
    WHERE f.user_id = p.user_id
      AND f.feature_time <= p.prediction_time
    ORDER BY f.feature_time DESC
    LIMIT 1
) AS f ON TRUE;
```

This “as-of join” prevents future leakage. At scale, use appropriate partitioning/indexing or a point-in-time feature-store operation.

## 11. Dates and time zones

- Store event timestamps in UTC; retain the business/user time zone separately.
- Convert to the business time zone before defining a “day.”
- Use half-open ranges: `timestamp >= start AND timestamp < end`.
- Avoid casting an indexed timestamp in a filter if a range can be used.

```sql
-- More index-friendly than DATE(order_time) = DATE '2026-11-01'
WHERE order_time >= TIMESTAMP '2026-11-01 00:00:00'
  AND order_time <  TIMESTAMP '2026-11-02 00:00:00'
```

## 12. Transactions and consistency

### ACID

- **Atomicity:** all changes commit or none do.
- **Consistency:** constraints/invariants remain valid.
- **Isolation:** concurrent transactions have controlled visibility.
- **Durability:** committed work survives failure.

Isolation anomalies to recognize:

- dirty read;
- non-repeatable read;
- phantom read;
- lost update/write skew.

For an idempotent request, enforce uniqueness in the database rather than relying only on an application check.

```sql
CREATE UNIQUE INDEX uq_request_id
    ON inference_requests(request_id);
```

## 13. Data modeling essentials

| Model | Good for | Watch for |
|---|---|---|
| Normalized OLTP | Correct transactional updates | Many joins for analytics |
| Star schema | Fast, understandable analytics | Dimension/history governance |
| Event log | Behavioral and temporal analysis | Schema evolution, duplicates, ordering |
| Document store | Flexible aggregate-shaped records | Cross-document joins/constraints |
| Key-value store | Very fast key access | Limited query patterns |
| Graph database | Relationship traversal | Operational complexity |
| Vector database/index | Similarity search | Metadata filters, freshness, authorization |

For ML/AI, explicitly model:

- event time versus ingestion time;
- entity and feature keys;
- model/prompt/retriever version;
- request, trace and tool-call IDs;
- prediction, confidence and outcome/label;
- tenant/user authorization scope;
- retention and deletion requirements.

## 14. Performance and query plans

Start with correctness, then measure.

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT ...;
```

Check:

- estimated versus actual rows;
- sequential scan versus appropriate index scan;
- join algorithm and join order;
- repeated scans and correlated work;
- sorts/hash operations spilling to disk;
- skewed keys and poor statistics;
- partition pruning;
- filters applied late;
- functions/casts preventing index use.

Index principles:

- Index columns used selectively in joins and filters.
- Composite index order should match frequent access patterns.
- More indexes speed some reads but cost storage and slow writes.
- A covering index may avoid table lookups but increases index size.
- Low-cardinality columns alone often have limited selectivity.

## 15. Common traps

| Trap | Correction |
|---|---|
| `LEFT JOIN` then right-table condition in `WHERE` | Move the condition into `ON` if unmatched left rows must remain |
| One-to-many joins inflate sums | Pre-aggregate each side to the target grain |
| `NOT IN` with `NULL` | Use `NOT EXISTS` |
| `COUNT(column)` used as row count | Use `COUNT(*)` if nulls must count |
| Integer division | Cast/multiply by `1.0` |
| Rolling seven rows called seven days | Use a date spine/calendar-aware range |
| Non-deterministic `ROW_NUMBER` | Add a stable tie-breaker |
| Future feature joined to training row | Use an as-of/point-in-time join |
| Average of averages | Recompute from weighted numerator/denominator |
| Conversion denominator from converters | Begin with all assigned/eligible users |

## 16. Rapid interview questions and answers

1. **`WHERE` versus `HAVING`?** `WHERE` filters input rows; `HAVING` filters aggregated groups.
2. **`ROW_NUMBER` versus `RANK`?** `ROW_NUMBER` is unique; `RANK` gives ties the same rank and leaves gaps; `DENSE_RANK` leaves no gaps.
3. **`UNION` versus `UNION ALL`?** `UNION` deduplicates; `UNION ALL` preserves rows and avoids that cost.
4. **Why did revenue double after a join?** The join changed the grain through one-to-many/many-to-many matches; inspect key cardinality and aggregate before joining.
5. **`EXISTS` versus join?** Use `EXISTS` when only match existence matters; it avoids exposing/multiplying matched rows.
6. **Window function versus `GROUP BY`?** A window computes across related rows while keeping each row; `GROUP BY` collapses rows.
7. **Clustered versus nonclustered index?** A clustered organization controls/approximates physical row order depending on database; secondary indexes are separate access structures pointing to rows.
8. **What is a point-in-time join?** It selects feature data available at or before each prediction time, preventing future leakage.
9. **Why use half-open time intervals?** Adjacent windows do not overlap and precision/time values at the end boundary are handled consistently.
10. **CTE versus temporary table?** A CTE is a query expression; a temp table materializes reusable intermediate data and can be indexed/analyzed, with write/management overhead.

## 17. Lead-level case

**Question:** Design the analytical and feature data model for a churn model that retrains weekly and scores customers daily.

**Strong answer structure:**

1. Define entity grain, observation date, prediction horizon, label window and actionability.
2. Keep raw immutable events with event time, ingestion time, source and deduplication key.
3. Build conformed customer/account dimensions with history where needed.
4. Create point-in-time feature snapshots keyed by customer and feature timestamp.
5. Construct labels only from the future label window and exclude incomplete windows.
6. Store training dataset version, query/code version, model version and feature definitions.
7. Separate offline feature computation from an online serving table if low-latency scoring is required.
8. Enforce data contracts, uniqueness, null/range checks, freshness and lineage.
9. Partition by date, index entity/time access paths, and design incremental backfills.
10. Log predictions and later outcomes for monitoring, calibration and retraining.
11. Apply tenant/access controls, retention and deletion propagation.
12. Validate offline/online parity and guard against label/feature leakage.

## 18. Final revision checklist

- [ ] I can state table grain before writing a query.
- [ ] I understand joins, null semantics and row multiplication.
- [ ] I can solve latest-row, top-N, rolling, retention, funnel and streak questions.
- [ ] I can explain and use window frames.
- [ ] I can build point-in-time correct datasets.
- [ ] I can read a query plan and recommend measured optimizations.
- [ ] I understand transactions, indexes and analytical data models.
- [ ] I test duplicates, nulls, ties, missing dates and empty denominators.
