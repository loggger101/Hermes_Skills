"""Verify the general big-data patterns for python-data-science reference doc.

Every snippet below is what will be quoted in the doc; all outputs are real,
captured on this machine (Windows py3.11) 2026-09-07 with duckdb 1.5.5 / polars
1.44.1 / pyarrow 25.0.1. Ground truth = pandas for every comparison.

Portable: the fixture dir is a per-run tempdir (was a hardcoded Windows path,
which broke on Linux CI). Needs numpy/pandas/duckdb/polars/pyarrow importable;
exit code = number of failed checks (0 = all green), so it can run in CI.
"""
import os, time, io, tempfile
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 200_000

FAILURES: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    """Record + print one verification. Exit code at the end = number of failures."""
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"   [{detail}]" if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)


# ── fixture: two related tables (orders + customers), CSV on disk ───────────────
out_dir = os.path.join(tempfile.gettempdir(), "bignums-verify")
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
check("p1_duckdb_matches_pandas", match, f"duckdb={duck_top.values.tolist()} pandas={pandas_top.values.tolist()}")
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
# ground truth in pandas for the same top-5-by-spend slice
gt = (orders.groupby("customer_id", as_index=False)["amount_usd"].sum()
        .sort_values("amount_usd", ascending=False).reset_index(drop=True))
total_spend = float(gt["amount_usd"].sum())
top5 = gt.head(5)
duck_rows = duck_rank.reset_index(drop=True)
p2_ok = (len(top5) == 5 and len(duck_rows) == 5
         and list(duck_rows["customer_id"]) == list(top5["customer_id"]))
if p2_ok:
    for i in range(5):
        if abs(float(duck_rows.loc[i, "spend"]) - float(top5.loc[i, "amount_usd"])) > 1e-6 \
           or int(duck_rows.loc[i, "rank_by_spend"]) != i + 1 \
           or abs(float(duck_rows.loc[i, "share_of_total"]) - round(float(top5.loc[i, "amount_usd"]) / total_spend, 4)) > 1e-9:
            p2_ok = False
check("p2_window_rank_and_share_match_pandas", p2_ok)

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
print("\n=== PATTERN 3: polars lazy + validate='m:1' join ===")
print(polars_top.to_pandas().to_string(index=False))
# ground truth in pandas for the same group-by (counts per segment)
gt_seg = (orders.merge(customers, on="customer_id", how="left")
            .groupby("segment").agg(n_orders=("order_id", "count"),
                                    total=("amount_usd", lambda s: round(s.sum(), 2)))
            .reset_index())
pl_raw = polars_top.to_pandas()
# the unaliased sum column is named differently across polars versions — rename by position
if "total" not in pl_raw.columns and len(pl_raw.columns) == 3:
    pl_raw = pl_raw.rename(columns={pl_raw.columns[2]: "total"})
pl_df = pl_raw.sort_values("n_orders", ascending=False).reset_index(drop=True)
gt_sorted = gt_seg.sort_values("n_orders", ascending=False).reset_index(drop=True)
p3_ok = (list(pl_df["segment"]) == list(gt_sorted["segment"])
         and list(pl_df["n_orders"].astype(int)) == list(gt_sorted["n_orders"].astype(int)))
if p3_ok:
    for i in range(len(pl_df)):
        if abs(float(pl_df.loc[i, "total"]) - float(gt_sorted.loc[i, "total"])) > 1e-6:
            p3_ok = False
check("p3_polars_groupby_matches_pandas", p3_ok)

# cardinality check must actually FIRE on a bad join — prove it with m:n data
bad = pl.DataFrame({"customer_id": [1, 1, 2], "x": [1, 2, 3]})   # customer 1 appears twice
rejected = False
try:
    (lf_cust.join(bad.lazy(), on="customer_id", how="left", validate="m:1").collect())
except Exception as e:
    rejected = True
check("p3_validate_m1_rejects_many_to_one_bad_join", rejected)
print(f"validate='m:1' correctly REJECTED the m:n join" if rejected else "BUG: validate did NOT fire")

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
check("p4_parquet_zstd_roundtrip_bit_identical", identical)
check("p4_row_group_control_200k_over_50k_is_4_groups", meta.num_row_groups == 4 and meta.row_group(0).num_rows == 50_000,
      f"(groups={meta.num_row_groups})")

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
got7 = merged.filter(pl.col("order_id") == 7)["amount_usd"].to_list()[0]
expected = float(batch2.loc[batch2["order_id"] == 7, "amount_usd"].iloc[0])
print(f"overlap row order_id=7: got {got7} expected(day-2 value) {expected} -> match={abs(got7-expected)<1e-9}")
check("p5_dedup_keeps_last_across_files", len(merged) == N, f"(got {len(merged)})")
check("p5_overlap_row_carries_day2_value", abs(got7 - expected) < 1e-9, f"(got {got7} want {expected})")

# pandas equivalent for the record (the space-datasets pattern uses exactly this):
pd_merged = pd.concat([orders, batch2]).drop_duplicates(subset="order_id", keep="last")
print(f"pandas-equivalent row count: {len(pd_merged):,} -> same={len(pd_merged)==N}")
check("p5_pandas_equivalent_same_row_count", len(pd_merged) == N and (pd_merged.sort_values("order_id")["amount_usd"]
      .reset_index(drop=True) == merged.to_pandas().sort_values("order_id")["amount_usd"].reset_index(drop=True)).all())

# ══ PATTERN 6: PyArrow row-group iteration — column-pruned null audit (space-datasets audit-nulls.py) ═══
import pyarrow.parquet as pq
null_df = pd.DataFrame({
    "id": np.arange(N),
    "a": rng.integers(0, 100, N).astype("int64"),
    "b": [None if i % 7 == 0 else float(i) for i in range(N)],   # every 7th row null = 14.29%
    "c": ["x" if i % 3 else None for i in range(N)],             # 1/3 = 33.33% nulls
})
pq_nulls = os.path.join(out_dir, "null_audit.parquet")
null_df.to_parquet(pq_nulls, compression="zstd", row_group_size=50_000)

def audit_nulls(path):
    pf = pq.ParquetFile(path)                       # metadata only; no data loaded yet
    total_rows = 0
    null_counts = {}                                # col -> int
    for batch in pf.iter_batches(batch_size=50_000):   # or columns=[...] to prune further
        n = batch.num_rows
        total_rows += n
        for i, name in enumerate(batch.schema.names):
            nulls = batch.column(i).null_count      # O(1) per column — validity bitmap precomputed
            if nulls:
                null_counts[name] = null_counts.get(name, 0) + nulls
    return total_rows, null_counts

t_total, t_nc = audit_nulls(pq_nulls)
exp_b = int((null_df["b"].isna()).sum()); exp_c = int((null_df["c"].isna()).sum())
print("\n=== PATTERN 6: pyarrow row-group null audit vs pandas ground truth ===")
for col in ("a", "b", "c"):
    got, want = t_nc.get(col, 0), {"a": 0, "b": exp_b, "c": exp_c}[col]
    print(f"  {col}: row-groups={got} nulls (pandas says {want}) -> match={got == want}")
check("p6_null_audit_matches_pandas", t_total == N and t_nc.get("a", 0) == 0 and t_nc["b"] == exp_b and t_nc["c"] == exp_c,
      f"(total={t_total}, b={t_nc.get('b')}/{exp_b}, c={t_nc.get('c')}/{exp_c})")
print(f"rows scanned: {t_total:,} | audit matched pandas exactly (b={exp_b}, c={exp_c})")

# ── summary (fail loud) ───────────────────────────────────────────────────────────
if FAILURES:
    print(f"\nFAILED ({len(FAILURES)}): {', '.join(FAILURES)}")
    raise SystemExit(len(FAILURES))
print("\nALL CHECKS PASSED — big-data patterns verified against pandas ground truth.")
