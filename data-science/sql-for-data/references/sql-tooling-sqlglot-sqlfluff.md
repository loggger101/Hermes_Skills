---
description: "SQL tooling from awesome-db-tools, run live: sqlglot 30.21 transpile/parse/AST (silent semantic changes, unknown functions pass through) and sqlfluff 4.4 lint/fix; plus the migration/schema tool map"
source_repo: mgramin/awesome-db-tools (curated list) -> tobymao/sqlglot (MIT), sqlfluff/sqlfluff (MIT)
tested_version: sqlglot 30.21.0 and sqlfluff 4.4.0 pip --target on Windows py3.14; SQLite 3.50.4 for executing a transpiled expression; migration tools (Atlas, Flyway, Liquibase, Sqitch) are list entries only, not run
verified_date: "2026-10-05"
---

# SQL tooling: parse, transpile and lint

The awesome-db-tools list spans IDEs, CLIs (`pgcli`, `litecli`), schema change tools (Atlas, Flyway, Liquibase, Sqitch), diagrams and documentation (SchemaCrawler), monitoring, backup, and a **SQL analyzers**
section (SQLCheck for anti-patterns, SQLFluff, SQLGlot). The two Python libraries are the ones an agent can call directly.

## sqlglot (parser, transpiler, builder)

```python
import sqlglot
from sqlglot import exp, parse_one
sqlglot.transpile("SELECT TOP 5 a FROM t ORDER BY a", read="tsql", write="sqlite")[0]
```

Observed (30.21.0):

| Input (dialect) | Output |
|---|---|
| `SELECT TOP 5 a FROM t ORDER BY a` (tsql -> sqlite) | `SELECT a FROM t ORDER BY a LIMIT 5` |
| ``SELECT `a` FROM `t` LIMIT 3`` (mysql -> postgres) | `SELECT "a" FROM "t" LIMIT 3` |
| `IFNULL(a, 0)` (mysql -> postgres) | `COALESCE(a, 0)` |
| `list_value(1,2), epoch_ms(1000)` (duckdb -> postgres) | `ARRAY[1, 2], TO_TIMESTAMP(CAST(1000 AS DOUBLE PRECISION) / POWER(10, 3))` |
| `DATE_ADD(d, INTERVAL 1 DAY)` (mysql -> sqlite) | `DATE(d, '1 DAY')`, which SQLite executed correctly (`DATE('2026-01-31','1 DAY')` = `2026-02-01`) |
| pretty printing | `transpile(sql, pretty=True)` returns an indented, multi-line query |
| AST queries | `parse_one(sql).find_all(exp.Table)` gave `['a','b']`; `find_all(exp.Column)` gave `a.id, a.x, b.id, b.y, b.z`: use it to extract table and column lineage |
| `SELECT FROM WHERE` | `ParseError: Expected table name but got WHERE ...` with line/column |

**Transpiling is not semantic equivalence.** Two things reproduced:

1. **An unknown function passes through untouched** (`my_custom_fn(a)` came out as `MY_CUSTOM_FN(a)` for SQLite): the output is syntactically fine and fails only at run time.
2. **A construct with no equal on the target is rewritten into something else, silently.** `ARRAY_AGG(a ORDER BY b)` (postgres -> mysql) became `GROUP_CONCAT(a ORDER BY CASE WHEN b IS NULL THEN 1 ELSE 0 END, b)`: an array became a comma-joined string. Nothing was logged, and `unsupported_level=ErrorLevel.RAISE` did **not** raise.
   Also, SQLite's `DATE('2026-01-31','+1 month')` gives `2026-03-03` (month overflow rolls forward); MySQL's `DATE_ADD(... INTERVAL 1 MONTH)` is documented to clamp to the last day (not run here), a semantic difference the transpiler cannot flag.

Rule: after transpiling, run both queries on a small fixture and compare result sets; treat sqlglot output as a draft. It is excellent for dialect-aware parsing, formatting, and extracting tables/columns, and good for the common 90% of translations.

## sqlfluff (linter and fixer)

`sqlfluff.lint(sql, dialect="ansi")` on `select a,b from t where a=1 and b = 2` returned violations `LT09` (select targets on new lines), `LT01` (spacing, three hits), `LT14` (keyword newlines), and `sqlfluff.fix(...)` rewrote it to

```text
select
    a,
    b
from t
where a = 1 and b = 2
```

Calling `lint` with no `dialect` did not raise on 4.4.0; it linted with the default dialect, so always pass `dialect=` explicitly (postgres, sqlite, duckdb, tsql, ...) or a parse that depends on dialect rules will mis-report.
A syntax error comes back as a violation with code `PRS` (plus layout rules), not as an exception: treat any `PRS` as a hard failure in CI. Keys on each violation dict include `code`, `start_line_pos` and `description`.

## Schema change and migration tools (list entries, not run)

| Need | Tools named in the list |
|---|---|
| Declarative schema inspect/apply | Atlas |
| Versioned migrations | Flyway, Liquibase, Sqitch |
| Schema docs and diagrams | SchemaCrawler |
| Interactive shells with completion | `pgcli`, `litecli` (SQLite) |
| SQL anti-pattern detection | SQLCheck |

For SQLite work in this repo see `sqlite-queries`; for analytics SQL see `sql-for-data` and `duckdb-querying`.
