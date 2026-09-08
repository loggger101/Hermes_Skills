"""Verify the general big-data patterns for python-data-science reference doc.

Every snippet below is what will be quoted in the doc; all outputs are real,
captured on this machine (Windows py3.11) 2026-09-07 with duckdb 1.5.5 / polars
1.44.1 / pyarrow 25.0.1. Ground truth = pandas for every comparison.
"""
import os, time, io
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 200_000

# ── fixture: two related tables (orders + customers), CSV on disk ───────────────
out_dir = r"C:\Users\Owner\AppData\Local\Temp\bignums"
os.makedirs(out_dir, exist_ok=True)
cust_id = rng.integers(1, 5_000, size=N)
customers = pd.DataFrame({
    "customer_id": np.arange(1, 5_001),
    "segment": rng.choice(["retail", "wholesale", "enterprise"], size=5_000, p=[.7, .2, .1]),
})
orders = pd.DataFrame({
    "order_id": np.arange(N),
    "customer_id": cust_id,
    "amount_usd": rng.gamma(2.0, 40.0, size=N).round(2),
    "day": pd.to_datetime("2026-01-01") + pd.to_timedelta(rng.integers(0, 90, N), unit="D"),
})
csv_orders = os.path.join(out_dir, "orders.csv")
csv_customers = os.path.join(out_dir, "customers.csv")
orders.to_csv(csv_orders, index=False)
customers.to_csv(csv_customers, index=False)
print(f"fixture: {N:,} orders x 5k customers -> CSV on disk")

# ══ PATTERN 1: duckdb ad-hoc query straight from CSV (no pandas load) ═══════════
import duckdb
t0 = time.perf_counter()
duck_top = duckdb.sql(f"""
    SELECT c.segment, COUNT(*) AS n_orders, ROUND(SUM(o.amount_usd), 2) AS total
    FROM read_csv_auto('{csv_orders.replace(os.sep, "/")}') o
    JOIN read_csv_auto('{csv_customers.replace(os.sep, "/")}') c USING (customer_id)
    GROUP BY c.segment ORDER BY total DESC
""").df()
t_duck = time.perf_counter() - t0

pandas_top = (orders.merge(customers, on="customer_id")
              .groupby("segment").agg(n_orders=("order_id", "count"),
                                      total=("amount_usd", lambda s: round(s.sum(), 2)))
              .reset_index().sort_values("total", ascending=False).reset_index(drop=True))
print("\n=== PATTERN 1: duckdb ad-hoc vs pandas ground truth ===")
print(duck_top.to_string(index=False))
match = (duck_top.sort_values("segment").values == pandas_top.sort_values("segment").values).all()
print(f"matches pandas exactly: {match} | duckdb wall time: {t_duck*1000:.0f} ms")

# ══ PATTERN 2: window function in SQL that would be painful in pandas ═══════════
duck_rank = duckdb.sql(f"""
    SELECT customer_id, SUM(amount_usd) AS spend,
           RANK() OVER (ORDER BY SUM(amount_usd) DESC) AS rank_by_spend,
           ROUND(SUM(amount_usd) / SUM(SUM(amount_usd)) OVER (), 4) AS share_of_total
    FROM read_csv_auto('{csv_orders.replace(os.sep, "/")}')
    GROUP BY customer_id ORDER BY spend DESC LIMIT 5
""").df()
print("\n=== PATTERN 2: window functions (top-5 customers by spend + share) ===")
print(duck_rank.to_string(index=False))

# ══ PATTERN 3: polars lazy pipeline with validate= cardinality checks ═══════════
import polars as pl
t0 = time.perf_counter()
lf_orders = pl.scan_csv(csv_orders).with_columns(pl.col("day").str.strptime(pl.Date, "%Y-%m-%d"))
lf_cust = pl.scan_csv(csv_customers)
result = (lf_orders.join(lf_cust, on="customer_id", how="left", validate="m:1")   # every order -> exactly one customer
          .group_by("segment")
          .agg(pl.len().alias("n_orders"), (pl.col("amount_usd").sum() * 100).round(2) / 100.0)
          .sort("n_orders", descending=True))
polars_top = result.collect()
t_plr = time.perf_counter() - t0
print("\n=== PATTERN 3: polars lazy + validate='n:1' join ===")
print(polars_top.to_pandas().to_string(index=False))

# cardinality check must actually FIRE on a bad join — prove it with m:n data
bad = pl.DataFrame({"customer_id": [1, 1, 2], "x": [1, 2, 3]})   # customer 1 appears twice
try:
    (lf_cust.join(bad.lazy(), on="customer_id", how="left", validate="m:1").collect())
    print("validate='n:1' did NOT fire — BUG")
except Exception as e:
    print(f"validate='n:1' correctly REJECTED the m:n join: {type(e).__name__}")

# ══ PATTERN 4: parquet zstd round-trip + row-group control at scale ════════════
pq_path = os.path.join(out_dir, "orders.parquet")
t0 = time.perf_counter()
df_pl = pl.from_pandas(orders)
df_pl.write_parquet(pq_path, compression="zstd", row_group_size=50_000)   # 4 groups for 200k rows
write_ms = (time.perf_counter() - t0) * 1000

t0 = time.perf_counter()
back = pl.read_parquet(pq_path, columns=["order_id", "amount_usd"])
read_ms = (time.perf_counter() - t0) * 1000
identical = back["amount_usd"].to_list() == orders["amount_usd"].tolist()

import pyarrow.parquet as pq
meta = pq.ParquetFile(pq_path).metadata
print("\n=== PATTERN 4: parquet zstd round-trip ===")
print(f"write {write_ms:.0f} ms | read (2 of 4 cols) {read_ms:.0f} ms | "
      f"row_groups={meta.num_row_groups} rows/group={meta.row_group(0).num_rows}")
print("bit-identical round-trip:", identical, "| file size:", os.path.getsize(pq_path), "bytes")

# ══ PATTERN 5: incremental update — concat + drop_duplicates keep='last' ═══════
# simulate a second day's batch with some overlapping order_ids (updated amounts)
batch2 = orders.iloc[:10_000].copy()
batch2["amount_usd"] = (batch2["amount_usd"] * 1.5).round(2)   # "corrected" values
pq_batch2 = os.path.join(out_dir, "orders_day2.parquet")
pl.from_pandas(batch2).write_parquet(pq_batch2)

merged = (pl.scan_parquet([pq_path, pq_batch2])
          .unique(subset="order_id", keep="last")      # newer file wins on overlap
          .collect())
print("\n=== PATTERN 5: incremental dedup (keep='last' across files) ===")
print(f"rows after merge+dedup: {len(merged):,} (expect exactly {N:,})")
# the corrected rows must carry day-2 values
check = merged.filter(pl.col("order_id") == 7)["amount_usd"].to_list()[0]
expected = float(batch2.loc[batch2["order_id"] == 7, "amount_usd"].iloc[0])
print(f"overlap row order_id=7: got {check} expected(day-2 value) {expected} -> match={abs(check-expected)<1e-9}")

# pandas equivalent for the record (the space-datasets pattern uses exactly this):
pd_merged = pd.concat([orders, batch2]).drop_duplicates(subset="order_id", keep="last")
print(f"pandas-equivalent row count: {len(pd_merged):,} -> same={len(pd_merged)==N}")
