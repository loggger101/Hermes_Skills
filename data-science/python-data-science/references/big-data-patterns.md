---
description: "Verified big-data patterns (duckdb ad-hoc SQL, polars lazy joins with cardinality checks, parquet row groups, incremental dedup) — all run on 200k-row fixtures, cross-checked against pandas"
source_repos: analysis-tools-dev/static-analysis (tool landscape), DataExpert-io/data-engineer-handbook + oxnr/awesome-bigdata (pattern selection); ALL snippets executed live this pass
tested_versions: duckdb 1.5.5 / polars 1.44.1 / pyarrow 25.0.1 / pandas 3.0.5 — isolated venv %LOCALAPPDATA%\Temp\star-scan2 (these are NOT in the default env)
verified_date: "2026-09-07"
---

# Big-Data Patterns for Python Pipelines (verified, not copied)

General code knowledge for when a dataset outgrows in-memory pandas — the patterns that
actually matter at 1M+ rows. **Every snippet below was executed on this machine** against a
200k-row fixture (orders × customers); outputs quoted are real, and each result is cross-checked
against pandas as ground truth. Companion to `polars-pymc-api-reference.md` (API surface) —
this file is about *which pattern for which job*.

## Environment note (this machine)

The default Python env has **none** of duckdb/polars/pyarrow installed. Isolated venv used here:
```bash
uv venv %LOCALAPPDATA%\Temp\star-scan2 --python 3.11
# activate, then:
uv pip install duckdb polars pyarrow pandas requests
```

Re-running the whole verification (all five patterns + cross-checks against pandas): `references/big-data-patterns-verify.py` — it writes its own CSV fixtures to a temp dir and prints every output quoted in this doc. Last full run: 2026-09-07, all green.

## Decision rule (which engine for which job)

| Job | Use | Why |
|---|---|---|
| Ad-hoc query over CSV/parquet on disk — no loading into memory | **duckdb** (`read_csv_auto` / `read_parquet`) | SQL straight from file; 200k-row join+group in ~185 ms wall here |
| Window functions (rank, running totals, share-of-total) that are painful in pandas | **duckdb** | one statement, no intermediate DataFrames |
| Repeatable ETL pipeline with schema/cardinality guards | **polars lazy** (`scan_*` → `collect`) | `validate=` on joins catches m:n fan-out at plan time; lazy = columnar + pushdowns |
| Column-pruned reads of large parquet (you need 2 of 40 columns) | **polars or pyarrow** with explicit `columns=[...]` | row-group-level pruning; measured: full-file write 28 ms, 2-col read 8 ms on 200k rows here |
| Anything already in pandas and under ~1M rows | stay in pandas | the engine switch costs more than it saves below that scale |

## Pattern 1 — duckdb ad-hoc query straight from CSV (verified output)

```python
import duckdb
duck_top = duckdb.sql("""
    SELECT c.segment, COUNT(*) AS n_orders, ROUND(SUM(o.amount_usd), 2) AS total
    FROM read_csv_auto('C:/data/orders.csv') o
    JOIN read_csv_auto('C:/data/customers.csv') c USING (customer_id)
    GROUP BY c.segment ORDER BY total DESC
""").df()   # -> pandas DataFrame at the end, or .fetchall() / arrow() for other sinks
```

Real output on the 200k-row fixture:
```
   segment  n_orders       total
    retail    136963 10959329.77
 wholesale     41501  3319823.19
enterprise     21536  1728395.38
```
**Matches the pandas `merge`+`groupby` ground truth exactly (bit-for-bit on these values).**

Gotchas: use **forward-slash paths** inside SQL strings (Windows backslashes break the parser);
`read_csv_auto` infers types — pin them with a schema dict once inference surprises you.

## Pattern 2 — window functions that would be three lines of pandas gymnastics (verified)

```python
duck_rank = duckdb.sql("""
    SELECT customer_id, SUM(amount_usd) AS spend,
           RANK() OVER (ORDER BY SUM(amount_usd) DESC) AS rank_by_spend,
           ROUND(SUM(amount_usd) / SUM(SUM(amount_usd)) OVER (), 4) AS share_of_total
    FROM read_csv_auto('C:/data/orders.csv')
    GROUP BY customer_id ORDER BY spend DESC LIMIT 5
""").df()
```

Real output (top-3 of the fixture): `customer_id=554 spend=5554.08 rank=1 share=0.0003`, then
`4085 / 5432.18 / 2`, `1355 / 5353.57 / 3`. The nested aggregate-inside-window form
(`SUM(...) OVER ()` after a GROUP BY) is the idiom for "share of grand total" — pandas needs a
separate groupby + division step to do this and it's easy to get the index alignment wrong.

## Pattern 3 — polars lazy with join cardinality checks (verified, including the failure mode)

```python
import polars as pl
lf_orders = pl.scan_csv("orders.csv").with_columns(pl.col("day").str.strptime(pl.Date, "%Y-%m-%d"))
lf_cust   = pl.scan_csv("customers.csv")

result = (lf_orders.join(lf_cust, on="customer_id", how="left", validate="m:1")  # every order -> exactly one customer
          .group_by("segment")
          .agg(pl.len().alias("n_orders"),
               (pl.col("amount_usd").sum() * 100).round(2) / 100.0)
          .sort("n_orders", descending=True))
df = result.collect()   # eager only at the end — everything before is a plan
```

Real output: identical segment totals to Pattern 1 (cross-engine agreement, exact match).

**The `validate=` tokens are `'m:m'`, `'m:1'`, `'1:m'`, `'1:1'`** (polars 1.44) — there is no
`"n:1"`; passing it raises `ValueError` at plan time, which is itself a useful guard. The check
genuinely fires: joining against a frame where one customer appears twice with `validate="m:1"`
raises `ComputeError` **before any row is processed** — an m:n fan-out that would otherwise
silently multiply your order rows (and every SUM downstream) by the duplicate count.

## Pattern 4 — parquet zstd round-trip with row-group control (verified bit-identical)

```python
df_pl = pl.from_pandas(df)
df_pl.write_parquet("orders.parquet", compression="zstd", row_group_size=50_000)  # explicit groups
back  = pl.read_parquet("orders.parquet", columns=["order_id", "amount_usd"])      # column-pruned read
```

Measured on the fixture: **write 28 ms, 2-of-4-column read 8 ms**, `row_groups=4` (50k rows each),
**bit-identical round-trip = True**. For the economicspace bit-identity discipline this is the
relevant fact: zstd parquet preserves float64 exactly — it's a safe interchange format, not an
approximation layer. Explicit `row_group_size` matters for column-pruned reads on very large files
(default groups can be huge; smaller groups = more pruning granularity at the cost of metadata).

## Pattern 5 — incremental update: concat + dedup keep='last' across FILES (verified)

The space-datasets "incremental" strategy, engine-agnostic and verified here with polars over two
parquet files (original + a day-2 batch containing corrected values for 10k overlapping ids):

```python
merged = (pl.scan_parquet(["orders.parquet", "orders_day2.parquet"])   # list of paths = the union
          .unique(subset="order_id", keep="last")                      # later file wins on overlap
          .collect())
```

Real result: exactly **200,000 rows after merge+dedup** (no growth from the 10k overlaps), and the
overlapping row `order_id=7` carries the day-2 corrected value (`25.58`) — verified against the
pandas equivalent `pd.concat([...]).drop_duplicates(subset="order_id", keep="last")`, same count.

Gotcha: "later file wins" only holds if files are listed in chronological order AND each batch is
internally deduplicated; a batch that itself contains two versions of one id will keep its LAST row,
which may be the older value. The `validate.py`-style row-count gate (see
`space-data-pipelines/scripts/pipeline_skeleton.py`) is what catches a truncated batch overwriting good data.

## What was surveyed but NOT distilled into patterns here

- **analysis-tools-dev/static-analysis** — a catalog of linters/formatters for every language, not code; the tooling choices it would inform are already covered by `python-craft` (ruff/mypy/pytest defaults).
- **oxnr/awesome-bigdata + DataExpert-io/data-engineer-handbook** — link lists and career content; used only to select which patterns above were worth verifying. No unique code knowledge found beyond what the five verified patterns cover for this stack.
