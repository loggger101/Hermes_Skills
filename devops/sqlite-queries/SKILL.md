---
name: sqlite-queries
description: "Query, inspect, and export SQLite databases."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [SQLite, SQL, database, query, export]
    related_skills: [sql-for-data]

---

# SQLite Queries

Query, inspect, and export SQLite databases. Encodes the workflow for database work via the `sqlite3` CLI.

## What This Skill Does

Implements a systematic SQLite workflow: locate and verify the database file, discover the schema (tables, columns, indexes, foreign keys), run queries (one-shot, CSV/JSON export, interactive exploration), handle data modifications with transactions + backups, and verify results by re-querying. Uses `sqlite3` CLI for all operations with `execute_code` (Python/pandas) for complex post-export processing. Loads `skill_view(name='sql-for-data')` for advanced SQL patterns.

## When to Use

- "What's in this SQLite database?"
- "Run this query against the DB"
- "Export some rows to CSV"
- "Find the schema / indexes / foreign keys"
- "How many rows / how big is the DB?"
- "Check for duplicates / missing values / inconsistencies"

Don't use for: client-server databases (PostgreSQL, MySQL need their own clients); ORM-level work; schema migrations (use the project's migration tooling).

## Prerequisites

- **`sqlite3` CLI** installed and on PATH (`sqlite3 --version`)
- A **path to the `.db`/`.sqlite`/`.sqlite3` file** — or the connection string if using a different driver
- Read access to the file (and write access if the task involves INSERT/UPDATE/DROP)

## How to Run

All SQLite work goes through `terminal` with the `sqlite3` CLI. Use `-header -csv` for machine-readable output, or raw mode for interactive exploration.

```bash
# Open interactively (use pty for interactive sessions)
sqlite3 mydb.db

# One-shot query → stdout
sqlite3 mydb.db "SELECT * FROM users LIMIT 5;"

# Header + CSV (good for parsing in scripts)
sqlite3 -header -csv mydb.db "SELECT id, name, email FROM users;"

# Export a full table to CSV
sqlite3 -header -csv mydb.db ".headers on\n.mode csv\n.output users.csv\nSELECT * FROM users;\n.output stdout"

# Schema: list tables
sqlite3 mydb.db ".tables"

# Schema: full CREATE statements
sqlite3 mydb.db ".schema"

# Schema: one table
sqlite3 mydb.db ".schema users"

# Indexes
sqlite3 mydb.db "SELECT * FROM sqlite_master WHERE type='index';"

# Row counts per table
sqlite3 mydb.db "SELECT name, COUNT(*) FROM sqlite_master WHERE type='table' GROUP BY name;"   # wrong — see Pitfalls
sqlite3 mydb.db "SELECT 'users', COUNT(*) FROM users UNION ALL SELECT 'orders', COUNT(*) FROM orders;"

# DB size on disk
ls -lh mydb.db
# Or in SQLite:
sqlite3 mydb.db "SELECT page_count * page_size AS size_bytes FROM pragma_page_count(), pragma_page_size();"

# Explain a query (plan)
sqlite3 mydb.db "EXPLAIN QUERY PLAN SELECT * FROM users WHERE email='x';"

# Import CSV into a table
sqlite3 mydb.db ".mode csv\n.import data.csv new_table"
```

## Procedure

### 1. Locate and verify the DB
- Confirm the file path exists and is readable
- Quick integrity check:
  ```bash
  sqlite3 mydb.db "PRAGMA integrity_check;"
  ```
  Returns `ok` on healthy DBs. Anything else means corruption — stop and flag it.

### 2. Discover the schema
```bash
sqlite3 mydb.db ".tables"                  # table names
sqlite3 mydb.db ".schema"                  # all CREATE statements
sqlite3 mydb.db "SELECT name, sql FROM sqlite_master WHERE type='table';"   # programmatic
sqlite3 mydb.db "PRAGMA foreign_key_list(users);"   # FKs on a table
sqlite3 mydb.db "PRAGMA index_list(users);"         # indexes on a table
```

### 3. Run the query
- Simple one-shot: `sqlite3 mydb.db "SELECT ..."`
- For results you need to parse: `sqlite3 -header -csv mydb.db "SELECT ..."` and read the stdout
- For aggregates/analytics: write the query, run it, read the output
- For exploratory work: interactive `sqlite3` with `pty=true`

### 4. Export
- To CSV: `sqlite3 -header -csv db "SELECT ..." > out.csv`
- To JSON (SQLite 3.38+): `sqlite3 -json db "SELECT ..."`
- To a file inside SQLite: use `.output filename` then `.output stdout`

### 5. Modify data (if the task requires it)
- Use transactions for multi-statement changes:
  ```bash
  sqlite3 mydb.db "BEGIN; UPDATE ...; INSERT ...; COMMIT;"
  ```
- Back up the DB file before destructive changes if it's not already backed up:
  ```bash
  cp mydb.db mydb.db.bak
  ```

### 6. Verify
- Re-run the query or a summary to confirm the result matches expectation
- For exports, read back the CSV/JSON and check row counts and key values

## Quick Reference

| Task | Command |
|------|---------|
| Integrity check | `sqlite3 db "PRAGMA integrity_check;"` |
| List tables | `sqlite3 db ".tables"` |
| Full schema | `sqlite3 db ".schema"` |
| One table schema | `sqlite3 db ".schema tablename"` |
| Query (raw) | `sqlite3 db "SELECT ..."` |
| Query (CSV + header) | `sqlite3 -header -csv db "SELECT ..."` |
| Query (JSON) | `sqlite3 -json db "SELECT ..."` |
| Export table to CSV | `sqlite3 -header -csv db "SELECT * FROM t;" > t.csv` |
| Import CSV | `sqlite3 db ".mode csv\n.import data.csv t"` |
| Row count | `sqlite3 db "SELECT COUNT(*) FROM t;"` |
| DB file size | `ls -lh db` or `PRAGMA page_count, page_size` |
| Query plan | `sqlite3 db "EXPLAIN QUERY PLAN SELECT ..."` |
| Indexes | `sqlite3 db "SELECT * FROM sqlite_master WHERE type='index';"` |
| Foreign keys | `sqlite3 db "PRAGMA foreign_key_list(t);"` |
| Backup file | `cp db db.bak` |

## Pitfalls

- **`COUNT(*)` from `sqlite_master` is wrong.** `sqlite_master` lists schema objects, not rows. To count rows, query the actual table: `SELECT COUNT(*) FROM tablename;`. There's no single query that returns row counts for all tables without knowing their names.
- **CSV import creates the table if it doesn't exist**, using the CSV header as column names. This can produce a table with wrong types (all TEXT). Check the schema after import.
- **No native date type.** SQLite stores dates as TEXT, REAL, or INTEGER. Comparisons work if the format is consistent (ISO-8601 TEXT is common), but `DATE()`/`DATETIME()` functions expect specific formats.
- **`.` commands vs SQL.** `.tables`, `.schema`, `.import`, `.mode`, `.output` are dot-commands, not SQL — they go to `sqlite3` directly, not inside a `sqlite3 "…"` one-liner unless embedded with `\n`. SQL statements go inside the quotes.
- **`-json` requires SQLite 3.38+ (2022).** Older installs don't support it. Fall back to CSV + parse in Python if needed.
- **Concurrent writes.** SQLite locks the database for writes. If another process is writing, your query may fail with `database is locked`. Retry or schedule around it.
- **Large exports in one-liners.** Very large result sets may be better exported with `.output` inside an interactive session, or via `sqlite3 ... ".output file\nSELECT ...\n.output stdout"`.
- **The DB file is the whole database.** There's no separate server. Back it up by copying the file (ideally while no writer is active, or use the backup API / `.backup` command).

## Verification

- `PRAGMA integrity_check` returns `ok`
- Schema discovery returns the expected tables/columns
- Query output matches expected rows/values
- Exports parse correctly (CSV has headers, JSON is valid, row counts match)
- Destructive changes verified by re-querying and, if appropriate, comparing against the backup

## Related

For file-level operations on the DB file itself, use `read_file` (won't work on binary DBs), `write_file` (don't write binary DBs via this), `patch`, `search_files`. For big data processing after export, use `execute_code` with pandas or stdlib csv. For other database engines, use the appropriate client (`psql`, `mysql`, etc.) — this skill is SQLite-specific.
