---
name: sql-for-data
description: "SQL for data: queries, joins, windows, aggregation."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [sql, data-analysis, joins, window-functions, aggregation, query-patterns, sqlite, postgresql, performance]
    category: data-science
    related_skills: [python-data-science, xlsx]

---

# SQL for Data Work

Practical SQL for data analysis and preparation — the queries you actually write when pulling data for analysis, not DBA tuning. Covers query patterns, joins, window functions, aggregation, and common pitfalls. Dialect notes where syntax diverges (SQLite vs PostgreSQL vs MySQL).


## What This Skill Does

SQL for data: queries, joins, windows, aggregation.

## When to Use

- Pulling data from a database for analysis in Python (pandas `read_sql`, etc.)
- Exploring a dataset directly in SQL before loading into Python
- Aggregating, joining, or transforming data in the database
- Writing queries for data pipelines or feature extraction
- Debugging why a query is slow or returning unexpected results

**Don't use** for DBA topics (index tuning at scale, replication setup, sharding). This is the analyst/scientist query layer.

## Dialect Quick Reference

| Feature | SQLite | PostgreSQL | MySQL |
|---|---|---|---|
| Window functions | 3.25+ | Full | 8.0+ |
| `LIMIT` / `OFFSET` | ✅ | ✅ | ✅ |
| `QUALIFY` | ❌ | ❌ | ❌ |
| `ILIKE` | ❌ | ✅ | ❌ (use `LIKE` + `LOWER`) |
| `EXCEPT` / `INTERSECT` | ✅ | ✅ | ✅ |
| `STRING_AGG` / `GROUP_CONCAT` | ❌ (`GROUP_CONCAT`) | `STRING_AGG` | `GROUP_CONCAT` |
| `DATE_TRUNC` | ❌ (use `strftime`) | ✅ | ❌ (use `DATE_FORMAT`) |
| `GENERATE_SERIES` | ❌ | ✅ | ❌ |
| CTE (`WITH`) | ✅ | ✅ | ✅ |
| Lateral join | ❌ | `LATERAL` / `CROSS JOIN LATERAL` | ❌ |

Prefer standard SQL where possible. Use dialect-specific features only when they materially help and you've noted the dependency.

## Query Anatomy

A well-formed query tells a story in order:

```sql
WITH recent_orders AS (
    SELECT *
    FROM orders
    WHERE created_at >= '2025-01-01'
),
order_totals AS (
    SELECT
        user_id,
        COUNT(*) AS order_count,
        SUM(amount) AS total_spent
    FROM recent_orders
    GROUP BY user_id
)
SELECT
    u.id,
    u.name,
    ot.order_count,
    ot.total_spent
FROM users u
JOIN order_totals ot ON u.id = ot.user_id
WHERE ot.total_spent > 100
ORDER BY ot.total_spent DESC
LIMIT 20;
```

Readability rules:
- One clause per line, indentation for subqueries and CTEs.
- Capitalize keywords (`SELECT`, `FROM`, `WHERE`).
- Alias tables meaningfully (`users u` is fine for short queries; don't use `a`, `b`, `c` unless the query is genuinely tiny).
- Comment non-obvious logic.

## SELECT and Projection

### What to select

- Select only what you need. `SELECT *` is fine for exploration, bad for production queries and large tables.
- Be explicit about columns — makes the query self-documenting and resilient to schema changes.
- Use column aliases to make results readable: `SUM(amount) AS total_spent`, not `SUM(amount)`.

### Filtering

```sql
-- WHERE filters rows before aggregation — use it early
SELECT *
FROM events
WHERE event_type = 'purchase'
  AND created_at >= '2025-01-01'
  AND user_id IS NOT NULL;

-- HAVING filters after aggregation
SELECT user_id, COUNT(*) AS event_count
FROM events
GROUP BY user_id
HAVING COUNT(*) > 10;
```

### NULL handling

- `NULL` is not equal to anything, including itself. `WHERE col = NULL` returns nothing. Use `IS NULL` / `IS NOT NULL`.
- `NULL` in arithmetic propagates: `5 + NULL` → `NULL`. Use `COALESCE` to provide defaults.
- `NULL` in `GROUP BY` groups together (all NULLs in one group).
- `COUNT(*)` counts rows; `COUNT(col)` counts non-NULL values of that column. Know which you want.

```sql
SELECT
    user_id,
    COALESCE(referral_source, 'unknown') AS source,
    COUNT(*) AS events
FROM events
GROUP BY user_id, COALESCE(referral_source, 'unknown');
```

## JOINS

### Inner join — rows that match in both tables

```sql
SELECT u.name, o.amount
FROM users u
JOIN orders o ON u.id = o.user_id;
```

### Left join — all rows from the left table, matches from the right

The most common join in data work. Use it when you want all rows from one table regardless of whether there's a match.

```sql
-- All users, with their order count (0 if no orders)
SELECT u.id, u.name, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;
```

Watch for the multiply effect: if one side of the join has multiple matching rows, the other side gets duplicated. Aggregate *after* joining, or aggregate before joining, depending on what you want.

```sql
-- WRONG: join then aggregate — duplicates orders if a user has multiple events
SELECT u.name, COUNT(o.id) AS order_count, COUNT(e.id) AS event_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
LEFT JOIN events e ON u.id = e.user_id
GROUP BY u.id, u.name;
-- order_count and event_count are both inflated

-- RIGHT: aggregate each side first, then join
WITH order_counts AS (
    SELECT user_id, COUNT(*) AS order_count FROM orders GROUP BY user_id
),
event_counts AS (
    SELECT user_id, COUNT(*) AS event_count FROM events GROUP BY user_id
)
SELECT u.name, COALESCE(oc.order_count, 0), COALESCE(ec.event_count, 0)
FROM users u
LEFT JOIN order_counts oc ON u.id = oc.user_id
LEFT JOIN event_counts ec ON u.id = ec.user_id;
```

### Right join — all rows from the right table

Rarely used. Same as left join with the tables swapped. Prefer writing left joins consistently for readability.

### Full outer join — all rows from both tables

```sql
SELECT *
FROM table_a a
FULL OUTER JOIN table_b b ON a.id = b.id;
```

Not supported in MySQL. In SQLite, emulate with `UNION` of left and right joins where the join column is NULL on the other side.

### Cross join — Cartesian product

Every row from A paired with every row from B. Useful for generating combinations, dangerous if accidental.

```sql
-- Generate all date × product combinations for a reporting grid
SELECT d.date, p.product_id
FROM (VALUES ('2025-01-01'), ('2025-01-02')) AS d(date)
CROSS JOIN products p;
```

### Self join — a table joined to itself

```sql
-- Find users who signed up on the same day as someone else
SELECT a.name AS user1, b.name AS user2, a.created_at AS signup_date
FROM users a
JOIN users b ON a.created_at = b.created_at AND a.id < b.id;
```

The `a.id < b.id` avoids duplicate pairs and self-pairs.

### Anti-join — rows in A with no match in B

```sql
-- Users with no orders
SELECT u.id, u.name
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id IS NULL;

-- Or using NOT EXISTS (often clearer and sometimes faster)
SELECT u.id, u.name
FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);
```

### Semi-join — rows in A that have a match in B (without pulling B's columns)

```sql
-- Users who have placed at least one order
SELECT u.id, u.name
FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);
```

Prefer `EXISTS` over `IN (SELECT ...)` for large subqueries.

## Aggregation

### GROUP BY essentials

```sql
SELECT
    user_id,
    COUNT(*) AS event_count,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount,
    MIN(created_at) AS first_event,
    MAX(created_at) AS last_event
FROM events
GROUP BY user_id;
```

- Every non-aggregated column in SELECT must be in GROUP BY (standard SQL).
- Aggregate before joining, as shown above, to avoid the multiply effect.

### GROUP BY extensions

```sql
-- GROUP BY with ROLLUP for subtotals
SELECT
    category,
    subcategory,
    COUNT(*) AS item_count,
    SUM(price) AS total_value
FROM products
GROUP BY ROLLUP (category, subcategory);
-- Produces rows for (category, subcategory), (category, NULL), and (NULL, NULL)

-- GROUP BY with CUBE for all combinations (can be large)
GROUP BY CUBE (category, subcategory);
```

### Conditions on aggregates

Use `HAVING`, not `WHERE`, for conditions on aggregated values.

```sql
SELECT user_id, COUNT(*) AS event_count
FROM events
GROUP BY user_id
HAVING COUNT(*) > 10;   -- correct

-- WRONG: WHERE on aggregate (syntax error in most dialects)
WHERE COUNT(*) > 10;
```

### Handling empty groups

`LEFT JOIN` + `GROUP BY` can produce NULL aggregates for groups with no matches. Use `COALESCE`.

```sql
SELECT u.id, COALESCE(COUNT(o.id), 0) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id;
```

## Window Functions

Window functions compute values across a set of rows related to the current row — without collapsing the result. Essential for ranking, running totals, lag/lead analysis, and partitioned calculations.

### Syntax

```sql
FUNCTION(args) OVER (
    PARTITION BY expr
    ORDER BY expr
    frame_clause
)
```

- `PARTITION BY` — groups rows like GROUP BY but doesn't collapse.
- `ORDER BY` — defines row order within the partition (required for order-sensitive functions).
- Frame clause — `ROWS` or `RANGE` with bounds; default is `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` when ORDER BY is present.

### Ranking

```sql
-- Row number (unique sequential, no ties)
SELECT
    user_id,
    total_spent,
    ROW_NUMBER() OVER (ORDER BY total_spent DESC) AS rank
FROM user_totals;

-- Rank (ties get same rank, gaps after)
SELECT
    user_id,
    total_spent,
    RANK() OVER (ORDER BY total_spent DESC) AS rank
FROM user_totals;

-- Dense rank (ties get same rank, no gaps)
SELECT
    user_id,
    total_spent,
    DENSE_RANK() OVER (ORDER BY total_spent DESC) AS rank
FROM user_totals;
```

### Partitioned windows

```sql
-- Rank within each category
SELECT
    product_id,
    category,
    price,
    RANK() OVER (PARTITION BY category ORDER BY price DESC) AS category_rank
FROM products;
```

### Lag and lead — look at neighboring rows

```sql
-- Month-over-month change
SELECT
    month,
    revenue,
    LAG(revenue, 1) OVER (ORDER BY month) AS prev_revenue,
    revenue - LAG(revenue, 1) OVER (ORDER BY month) AS mom_change
FROM monthly_revenue;

-- First and last value in a partition
SELECT
    user_id,
    event_time,
    event_type,
    FIRST_VALUE(event_type) OVER (
        PARTITION BY user_id ORDER BY event_time
    ) AS first_event
FROM user_events;
```

### Running totals and moving averages

```sql
-- Running total
SELECT
    day,
    revenue,
    SUM(revenue) OVER (ORDER BY day) AS running_total
FROM daily_revenue;

-- 7-day moving average
SELECT
    day,
    revenue,
    AVG(revenue) OVER (
        ORDER BY day
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7d
FROM daily_revenue;
```

### NTILE — bucket rows into N groups

```sql
-- Divide users into 4 spend quartiles
SELECT
    user_id,
    total_spent,
    NTILE(4) OVER (ORDER BY total_spent) AS spend_quartile
FROM user_totals;
```

## Common Table Expressions (CTEs)

CTEs make complex queries readable and modular. Use them liberally for anything beyond a simple SELECT.

```sql
WITH
filtered_events AS (
    SELECT * FROM events WHERE created_at >= '2025-01-01'
),
daily_counts AS (
    SELECT date(created_at) AS day, COUNT(*) AS event_count
    FROM filtered_events
    GROUP BY date(created_at)
),
running_total AS (
    SELECT
        day,
        event_count,
        SUM(event_count) OVER (ORDER BY day) AS cumulative
    FROM daily_counts
)
SELECT * FROM running_total ORDER BY day;
```

- CTEs are readable and composable. They're not always materialized (the planner may inline them), so don't assume they're cached.
- For reuse *and* materialization, consider a temporary table for very large intermediate results.

## Subqueries

### Scalar subqueries — return a single value

```sql
SELECT
    user_id,
    total_spent,
    (SELECT AVG(total_spent) FROM user_totals) AS global_avg
FROM user_totals;
```

### Row subqueries — return a single row

```sql
SELECT * FROM products
WHERE (category, price) = (
    SELECT category, MAX(price) FROM products GROUP BY category LIMIT 1
);
```

### Table subqueries — in FROM or JOIN

```sql
SELECT *
FROM (
    SELECT user_id, COUNT(*) AS event_count
    FROM events
    GROUP BY user_id
    HAVING COUNT(*) > 10
) AS active_users;
```

### EXISTS / NOT EXISTS — semi and anti joins

Covered above in the joins section. Prefer over `IN (SELECT ...)` for large subqueries and when you only need existence.

## Set Operations

### UNION — combine results, deduplicate

```sql
SELECT user_id FROM orders
UNION
SELECT user_id FROM refunds;
-- Unique user_ids that appear in either table
```

### UNION ALL — combine results, keep duplicates

Faster than `UNION` (no deduplication). Use when you know there are no overlaps or you want them.

```sql
SELECT 'order' AS source, user_id FROM orders
UNION ALL
SELECT 'refund' AS source, user_id FROM refunds;
```

### EXCEPT / MINUS — rows in first not in second

```sql
-- Users who ordered but never refunded
SELECT user_id FROM orders
EXCEPT
SELECT user_id FROM refunds;
```

MySQL uses `NOT EXISTS` or `LEFT JOIN ... WHERE right IS NULL` instead. SQLite and PostgreSQL support `EXCEPT`.

### INTERSECT — rows in both

```sql
-- Users who both ordered and refunded
SELECT user_id FROM orders
INTERSECT
SELECT user_id FROM refunds;
```

## Date and Time

### Getting current time

```sql
-- Standard
SELECT CURRENT_TIMESTAMP;
SELECT CURRENT_DATE;

-- SQLite
SELECT datetime('now');
SELECT date('now');

-- PostgreSQL
SELECT now();
SELECT current_date;
```

### Date truncation and extraction

```sql
-- PostgreSQL
SELECT date_trunc('month', created_at) AS month, COUNT(*) FROM events GROUP BY 1;

-- SQLite
SELECT strftime('%Y-%m-01', created_at) AS month, COUNT(*) FROM events GROUP BY 1;

-- MySQL
SELECT DATE_FORMAT(created_at, '%Y-%m-01') AS month, COUNT(*) FROM events GROUP BY 1;
```

### Extracting parts

```sql
-- PostgreSQL / MySQL
SELECT EXTRACT(YEAR FROM created_at) AS year FROM events;

-- SQLite
SELECT strftime('%Y', created_at) AS year FROM events;
```

### Date arithmetic

```sql
-- PostgreSQL
SELECT created_at + INTERVAL '7 days' FROM events;
SELECT created_at - INTERVAL '1 month' FROM events;

-- SQLite
SELECT date(created_at, '+7 days') FROM events;
SELECT date(created_at, '-1 month') FROM events;

-- MySQL
SELECT DATE_ADD(created_at, INTERVAL 7 DAY) FROM events;
SELECT DATE_SUB(created_at, INTERVAL 1 MONTH) FROM events;
```

### Time between two dates

```sql
-- PostgreSQL
SELECT created_at - refund_date AS diff FROM orders;

-- SQLite (days as integer)
SELECT julianday(created_at) - julianday(refund_date) AS days_diff FROM orders;

-- MySQL
SELECT DATEDIFF(created_at, refund_date) AS days_diff FROM orders;
```

## Conditional Logic

### CASE — the standard conditional

```sql
SELECT
    user_id,
    total_spent,
    CASE
        WHEN total_spent >= 1000 THEN 'high'
        WHEN total_spent >= 100 THEN 'medium'
        ELSE 'low'
    END AS spend_tier
FROM user_totals;
```

### Simple CASE — when comparing one column to values

```sql
SELECT
    status,
    CASE status
        WHEN 'pending' THEN 1
        WHEN 'shipped' THEN 2
        WHEN 'delivered' THEN 3
        ELSE 0
    END AS sort_order
FROM orders;
```

### Coalesce — first non-NULL value

```sql
SELECT
    user_id,
    COALESCE(display_name, name, email, 'Anonymous') AS label
FROM users;
```

### Nullif — return NULL if two values are equal

```sql
-- Prevent division by zero
SELECT total / NULLIF(count, 0) AS avg FROM stats;
```

## Handling Duplicates

### DISTINCT — remove duplicate rows

```sql
SELECT DISTINCT user_id, event_type FROM events;
```

Use sparingly — `DISTINCT` is a hint that the join or logic may be producing duplicates. Prefer fixing the root cause.

### Deduplicate to first occurrence

```sql
-- Keep the most recent event per user
WITH ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn
    FROM events
)
SELECT * FROM ranked WHERE rn = 1;
```

### Deduplicate by aggregation

```sql
-- One row per user with the latest event time
SELECT user_id, MAX(created_at) AS last_event
FROM events
GROUP BY user_id;
```

## Query Performance Basics

Analyst-level performance — enough to avoid ruinously slow queries, not DBA-level tuning.

### What makes a query slow

- **Full table scans** — filtering on a column without an index, or on an expression of a column (`WHERE YEAR(created_at) = 2025` prevents index use; use `WHERE created_at >= '2025-01-01' AND created_at < '2026-01-01'` instead).
- **Expensive joins** — joining on non-indexed columns, or joining large tables without filtering first.
- **O(n²) patterns** — correlated subqueries in SELECT that run once per row, self-joins without filters.
- **SELECT *** — pulling more data than needed, especially from wide tables or over a network.
- **Nested loops from bad plans** — sometimes a CTE or subquery that looks clean causes the planner to pick a bad plan.

### Index-friendly patterns

```sql
-- GOOD: sargable (can use an index on created_at)
WHERE created_at >= '2025-01-01' AND created_at < '2026-01-01'

-- BAD: non-sargable (can't use a plain index on created_at)
WHERE YEAR(created_at) = 2025
WHERE DATE(created_at) = '2025-03-15'

-- GOOD: filter early in a CTE before joining
WITH recent AS (
    SELECT * FROM orders WHERE created_at >= '2025-01-01'
)
SELECT * FROM recent JOIN users ON recent.user_id = users.id;
```

### EXPLAIN — look at the plan

```sql
-- PostgreSQL
EXPLAIN ANALYZE SELECT ...;

-- SQLite
EXPLAIN QUERY PLAN SELECT ...;

-- MySQL
EXPLAIN SELECT ...;
```

Look for: full table scans on large tables, nested loops over large sets, estimated row counts that are wildly off.

### When to aggregate in the database vs in Python

- **Aggregate in SQL** when the dataset is large and you only need summaries — the database is optimized for this.
- **Pull raw rows into Python** when you need per-row transformations, complex logic, or visualization easier in pandas/plotting.
- **Hybrid** — do the heavy filtering and aggregation in SQL, pull the reduced result into Python for analysis and plotting.

### Beware of COUNT(*) on huge tables

`COUNT(*)` without a WHERE clause on a large table is expensive — it scans the whole table (or index). If you just need an approximate count, look for system tables or statistics. If you need an exact count, accept the cost or maintain a counter.

## SQLite-Specific Notes

SQLite is common for local data work and embedded use. Key quirks:

- Dynamic typing — column types are advisory, not enforced.
- `GROUP_CONCAT` instead of `STRING_AGG`:
  ```sql
  SELECT group_concat(name, ', ') FROM users;
  ```
- Date functions use `strftime`, `datetime`, `julianday`, `date`.
- No `FULL OUTER JOIN` — emulate with `UNION` of left and right joins.
- No `LATERAL` — use subqueries or CTEs.
- `INSERT ... ON CONFLICT DO UPDATE` (upsert) supported since 3.24.
- `PRAGMA` commands for introspection: `PRAGMA table_info(table_name)`, `PRAGMA index_list(table_name)`.

## PostgreSQL-Specific Notes

- `STRING_AGG(value, delimiter)` for string aggregation.
- `DATE_TRUNC('unit', timestamp)` for truncation.
- `GENERATE_SERIES(start, stop, step)` for generating sequences — useful for time grids.
- `LATERAL` joins for correlated subqueries that reference preceding tables.
- `FILTER (WHERE ...)` for conditional aggregation:
  ```sql
  SELECT
      user_id,
      COUNT(*) FILTER (WHERE event_type = 'purchase') AS purchase_count,
      COUNT(*) FILTER (WHERE event_type = 'view') AS view_count
  FROM events
  GROUP BY user_id;
  ```
- `ILIKE` for case-insensitive pattern matching.
- `UNNEST(array)` to expand arrays into rows.

## MySQL-Specific Notes

- `GROUP_CONCAT` for string aggregation (with `SEPARATOR` option).
- No `DATE_TRUNC` — use `DATE_FORMAT`.
- `EXCEPT`/`INTERSECT` not supported — use `NOT EXISTS` or `LEFT JOIN`.
- Window functions supported since 8.0.
- `LIMIT` is standard; `OFFSET` for pagination (watch for performance on large offsets — use keyset pagination instead).

## Composing Queries for Data Work

A typical data-extraction query follows this shape:

```sql
WITH
-- 1. Filter raw data to the time range / scope of interest
filtered AS (
    SELECT * FROM events
    WHERE created_at >= :start_date AND created_at < :end_date
),
-- 2. Join to bring in dimensions
with_users AS (
    SELECT f.*, u.name AS user_name, u.segment
    FROM filtered f
    JOIN users u ON f.user_id = u.id
),
-- 3. Aggregate to the grain you need
daily AS (
    SELECT
        date(created_at) AS day,
        user_segment,
        COUNT(*) AS event_count,
        SUM(amount) AS total_revenue
    FROM with_users
    GROUP BY date(created_at), user_segment
)
-- 4. Final projection — only what the analysis needs
SELECT * FROM daily ORDER BY day, user_segment;
```

Parameters (`:start_date`, `:end_date`) are placeholders — substitute with actual values or use your client's parameter binding.

## Anti-Patterns

| Anti-pattern | Why it's bad | Fix |
|---|---|---|
| `SELECT *` in production queries | Pulls unnecessary data, fragile to schema changes | List columns explicitly |
| `WHERE col = NULL` | Never matches (NULL is not equal to anything) | `WHERE col IS NULL` |
| `COUNT(col)` when you mean rows | Skips NULLs in that column | `COUNT(*)` for row count |
| Join then aggregate when both sides have multiple rows | Multiplies rows, inflates aggregates | Aggregate each side first, then join |
| Correlated subquery in SELECT for every row | Runs once per row — slow on large sets | Rewrite as JOIN or CTE |
| `DISTINCT` to fix a join that's producing duplicates | Hides the real problem, costs a sort/dedup | Fix the join logic |
| Non-sargable date filter | Prevents index use, forces full scan | Use range comparisons on the raw column |
| `ORDER BY` without `LIMIT` on large result sets | Sorts everything, returns everything | Add `LIMIT` for exploration; sort in Python if needed |
| Implicit column order dependencies | `INSERT INTO t SELECT * FROM s` breaks when schemas change | List columns explicitly |
| Mixing aggregation levels in one query | Confusing and error-prone | Use CTEs to separate aggregation levels |

## Verification Checklist

Before running a query on real data:

- [ ] Columns selected are explicit (not `SELECT *` for anything beyond exploration)
- [ ] Filters are sargable where an index exists
- [ ] Joins are the right type (inner vs left vs semi vs anti)
- [ ] Aggregation happens at the right grain (no accidental multiply)
- [ ] NULL handling is intentional (COALESCE, IS NULL, etc.)
- [ ] Date/time comparisons use the right dialect functions
- [ ] Window functions have the right PARTITION BY and ORDER BY
- [ ] CTEs make the query readable, not just nested subqueries
- [ ] Test on a small subset first (add LIMIT or filter to a known small key set)
- [ ] For large queries, check the plan if the dialect supports it
