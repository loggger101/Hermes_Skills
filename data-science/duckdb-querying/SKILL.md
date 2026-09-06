---
name: duckdb-querying
description: "Query CSV/Parquet/S3 data ad-hoc via DuckDB Friendly SQL."
version: v1.0.0
author: Hermes Agent (ported from duckdb/duckdb-skills, verified against source)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [duckdb, sql, data-analysis, parquet, csv, s3]
    related_skills: [sql-for-data, space-data-pipelines]
---

<!-- source: duckdb/duckdb-skills (official DuckDB repo, starred-repo deep-dive 2026-09-05); idioms verified from skills/query/SKILL.md + read-file/SKILL.md -->

## What This Skill Does

Ad-hoc data querying without a database server: point DuckDB at files (CSV/Parquet/JSON/Avro/
Excel/spatial/SQLite) or remote URLs and run SQL. Includes the **Friendly SQL** idiom set that
makes generated queries shorter, plus a sandboxed ad-hoc pattern that limits file access to only
the referenced paths.

## When to Use

- "What's in this CSV/Parquet?" / quick profiling of any tabular data file
- Aggregations over large files (DuckDB is columnar — handles GB-scale Parquet where pandas OOMs)
- Joining heterogeneous sources: `FROM 'a.csv'` JOIN `read_parquet('b/*.parquet')` in one query
- NOT for persistent state, concurrent writes, or when the project already has a DB layer

## Setup (one-time)

```bash
# Windows: winget install duckdb.duckdb   | macOS: brew install duckdb   | Linux: see docs
duckdb -c "SELECT 1"   # verify
```

Extensions load on demand: `LOAD httpfs;` for S3/HTTPS, `LOAD spatial;`, `LOAD excel;`.

## Sandboxed Ad-hoc Query (preferred pattern)

Restrict the engine to exactly the files the query references — no accidental reads elsewhere:

```bash
duckdb :memory: -csv <<'SQL'
SET allowed_paths=['C:/data/sales.csv'];   -- every file the query touches, absolute paths
SET enable_external_access=false;
SET allow_persistent_secrets=false;
SET lock_configuration=true;
FROM 'C:/data/sales.csv' WHERE region = 'EMEA' ORDER BY ALL LIMIT 20;
SQL
```

Always use heredocs (`<<'SQL'`) for multi-line queries — avoids shell quoting hell.

## Universal File Reader (any format, one macro)

From the official `read-file` skill — auto-detects CSV/JSON/Parquet/Avro/XLSX/spatial/SQLite:

```sql
CREATE OR REPLACE MACRO read_any(file_name) AS TABLE
  WITH json_case    AS (FROM read_json_auto(file_name)),
       csv_case     AS (FROM read_csv(file_name)),
       parquet_case AS (FROM read_parquet(file_name)),
       avro_case    AS (FROM read_avro(file_name)),
       excel_case   AS (FROM read_xlsx(file_name)),
       sqlite_case  AS (FROM sqlite_scan(file_name, (SELECT name FROM sqlite_master(file_name) LIMIT 1)))
  SELECT * FROM parquet_case;   -- reorder cases by likelihood for your data
```

Remote files: prepend `LOAD httpfs;` (+ `CREATE SECRET (TYPE S3, PROVIDER credential_chain);` for s3://).

## Friendly SQL Idioms (prefer these when generating queries)

| Idiom | Example | Replaces |
|---|---|---|
| FROM-first implicit select | `FROM t WHERE x > 10` | `SELECT * FROM ...` |
| GROUP BY ALL / ORDER BY ALL | auto-groups/orders non-aggregates | listing every column |
| SELECT \* EXCLUDE (col) | drop columns from wildcard | rewriting the list |
| SELECT \* REPLACE (expr AS col) | transform one column in place | full re-list |
| count() | no star needed | `count(*)` |
| Reusable aliases | alias usable in WHERE/GROUP BY/HAVING | subquery |
| Lateral aliases | `SELECT i+1 AS j, j+2 AS k` | nested exprs |
| COLUMNS(\*) | apply expr across columns (regex/EXCLUDE/lambdas) | per-column repetition |
| FILTER clause | `count() FILTER (WHERE x > 10)` | conditional SUM(CASE...) |
| Top-N per group | `max(col, 3)`, `arg_max(arg, val, n)` | window + row_number dance |
| DESCRIBE / SUMMARIZE t | instant schema / statistical profile | manual profiling queries |
| PIVOT / UNPIVOT | wide↔long reshape | self-joins |
| LIMIT 10% | percentage limit | computed count |
| Dot chaining | `col.trim().lower()`, `'x'.upper()` | nested function calls |
| List comprehensions | `[x*2 FOR x IN list_col]` | unnest+transform |
| ASOF / POSITIONAL joins | ordered-approx / row-position matching | manual lag/row_number |

Data import: `FROM 'data/part-*.parquet'` globs multiple files; CSV headers auto-detected.

## Workflow (from the official query skill)

1. **Profile first**: `DESCRIBE t;` then `SUMMARIZE t;` — never guess schema
2. **Estimate size before running**: if source >1M rows and no LIMIT/aggregation, add one or ask
3. Run with `-csv` for parseable output; note truncation past ~100 rows
4. On "Extension not loaded" → `LOAD <ext>;` retry; on unclear error → search DuckDB docs

## Gotchas (verified)

- Windows paths in `allowed_paths`: use forward slashes or double backslashes — MSYS-style `/c/...` won't resolve inside the engine
- `read_csv` infers schema from first rows: for mixed-type columns pass `header=true, all_varchar=true` then cast explicitly
- Parquet globbing is case-sensitive on Linux; quote paths with spaces
