#!/usr/bin/env python3
"""NHATS rank cross-check for the economicspace closed-form dv estimator.

JPL's NHATS study (ssd-api.jpl.nasa.gov/nhats.api) is — as of 2026-09-07, when
Asterank removed its `dv` column from the live API — the ONLY external delta-v
oracle available keyless. It covers ~7,033 NEAs with at least one viable CREWED
ROUND-TRIP trajectory (total dv < 12 km/s, duration < 450 days).

Interpretation rule (from SECOND-PASS F6): NHATS is round-trip + crewed-constrained,
so its number is an upper bound on a differently-shaped quantity. Transfer the RANK
disagreement with the shipped estimator (Spearman), never quote it as a second
estimate of one-way gap magnitude.

Usage:
    python nhats_rank_crosscheck.py <economicspace_catalog_or_results_csv> [--top N]

The input CSV must contain at least an asteroid designation column and either
`total_cost_usd / gross_value_usd` (the shipped ranking) or a dv-like column; the
script auto-detects: looks for columns matching des/designation/name first, then
any of {min_delta_v_kms, delta_v, dv} — otherwise it ranks by cost/value ratio.

Output: per-orbit-quality-band Spearman correlation between NHATS min_dv rank and
the shipped ranking, plus the top-N disagreement table (bodies where the two
rankings disagree most). Writes nothing; prints a report. Read-only research tool:
never feeds ranking math.
"""
import argparse
import math
import sys

import pandas as pd
import requests

JPL_BASE = "https://ssd-api.jpl.nasa.gov"


def jpl_query(endpoint: str, params=None, timeout: int = 120) -> dict:
    """Query a JPL SSD API endpoint; retries up to 3x with backoff on 5xx.

    (Pattern from space-datasets/scripts/jpl_api.py — the shared helper that
    fetched NHATS in the starred-repo audit.)"""
    url = f"{JPL_BASE}/{endpoint}"
    for attempt in range(3):
        resp = requests.get(url, params=params, timeout=timeout)
        if resp.status_code < 500:
            resp.raise_for_status()
            return resp.json()
        if attempt < 2:
            wait = 5 * (2 ** attempt)
            print(f"  JPL API {resp.status_code}, retrying in {wait}s ({attempt + 1}/3)...")
    import time; time.sleep(5)
    resp.raise_for_status()
    return resp.json()


def fetch_nhats() -> pd.DataFrame:
    payload = jpl_query("nhats.api")
    df = pd.DataFrame(payload["data"])
    # NHATS nests min_dv/min_dur as {"dv": ..., "dur": ...} dicts — unwrap.
    if "min_dv" in df.columns:
        df["min_delta_v_kms"] = df["min_dv"].apply(
            lambda x: x.get("dv") if isinstance(x, dict) else None)
    if "min_dur" in df.columns:
        df["min_mission_duration_days"] = df["min_dur"].apply(
            lambda x: x.get("dur") if isinstance(x, dict) else None)
    rename = {"des": "designation", "fullname": "full_name",
              "n_via_traj": "n_viable_trajectories", "occ": "orbit_condition_code"}
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    # NHATS occasionally returns numeric fields as strings — coerce defensively.
    if "min_delta_v_kms" in df.columns:
        df["min_delta_v_kms"] = pd.to_numeric(df["min_delta_v_kms"], errors="coerce")
    return df


def find_col(df: pd.DataFrame, candidates) -> str | None:
    low = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand in low:
            return low[cand]
    return None


def spearman(a: pd.Series, b: pd.Series) -> float:
    """Spearman rank correlation without scipy (stdlib + pandas only)."""
    ra = a.rank().astype(float)
    rb = b.rank().astype(float)
    da = ra - ra.mean()
    db = rb - rb.mean()
    denom = math.sqrt((da * da).sum() * (db * db).sum())
    if denom == 0:
        return float("nan")
    return float((da @ db) / denom)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("csv", help="economicspace catalog/results CSV with a designation column")
    ap.add_argument("--top", type=int, default=25, help="rows in the disagreement table (default 25)")
    args = ap.parse_args()

    cat = pd.read_csv(args.csv)
    des_col = find_col(cat, ["des", "designation", "asteroid_designation", "name"])
    if des_col is None:
        print("ERROR: no designation column found (tried des/designation/name).")
        return 1

    nhats = fetch_nhats()
    n_des = find_col(nhats, ["des", "designation", "full_name"]) or "designations"
    # Prefix NHATS' columns so they can NEVER collide with same-named catalog
    # columns (pandas would suffix _x/_y and break every lookup downstream).
    nh_sub = (nhats[[n_des, "min_delta_v_kms", "orbit_condition_code"]]
              .dropna(subset=["min_delta_v_kms"])
              .rename(columns={"min_delta_v_kms": "nhats_min_dv_kms",
                               "orbit_condition_code": "nhats_u"}))
    if n_des == des_col:
        m = cat.merge(nh_sub, on=des_col, how="inner")
    else:
        m = cat.merge(nh_sub, left_on=des_col, right_on=n_des, how="inner").drop(columns=[n_des])
    if len(m) < 50:
        print(f"ERROR: only {len(m)} bodies overlap with NHATS — check designation formats "
              f"(NHATS uses MPC des like '1999 AO10').")
        return 1

    # Shipped ranking: prefer an explicit estimator-dv column, else cost/value ratio.
    # (NHATS' own min_delta_v_kms is merged in — it must never be treated as shipped.)
    dv_col = find_col(m, ["delta_v_km_s", "dv"])
    if dv_col:
        shipped_rank = m[dv_col].rename("shipped")
        label = f"{dv_col} (ascending)"
    else:
        num = find_col(m, ["total_cost_usd"])
        den = find_col(m, ["gross_value_usd"])
        if not num or not den:
            print("ERROR: no dv column and no total_cost_usd/gross_value_usd pair — "
                  "pass a CSV with either.")
            return 1
        shipped_rank = (m[num] / m[den].replace(0, pd.NA)).rename("shipped")
        label = f"{num}/{den} (ascending)"

    both = pd.concat([m["nhats_min_dv_kms"], shipped_rank], axis=1) \
           .rename(columns={"nhats_min_dv_kms": "min_delta_v_kms"}).dropna()
    if len(both) < 50:
        print(f"ERROR: only {len(both)} bodies have both values.")
        return 1

    overall = spearman(both["min_delta_v_kms"], both.iloc[:, 1])
    print(f"\n=== NHATS rank cross-check ===")
    print(f"Bodies overlapping with NHATS: {len(m):,} | usable pairs: {len(both):,}")
    print(f"NHATS min_dv vs shipped ranking ({label}): Spearman = {overall:.3f}")

    # Band by orbit quality: prefer the CATALOG's own condition_code (that is what
    # the ranking actually runs on); NHATS' U is only a fallback when absent.
    occ = find_col(m, ["condition_code", "orbit_condition_code"]) or \
          ("nhats_u" if "nhats_u" in m.columns else None)
    if occ is not None and m[occ].notna().any():
        u = pd.to_numeric(m[occ], errors="coerce")
        # economicspace's condition_code is a concatenated string ("5 2019 34 ..." —
        # U first); extract the leading integer when direct coercion yields nothing.
        if u.isna().all():
            u = m[occ].astype(str).str.extract(r"^\s*(\d+)")[0] \
                .pipe(pd.to_numeric, errors="coerce")
        u = u.reindex(both.index)
        print("\nBy orbit quality (U parameter):")
        for lo, hi in [(0, 4), (5, 9)]:
            sel = both[(u >= lo) & (u <= hi)]
            if len(sel) > 30:
                s = spearman(sel["min_delta_v_kms"], sel.iloc[:, 1])
                print(f"  U {lo}-{hi}: Spearman = {s:.3f} (n={len(sel):,})")

    # Disagreement table: rank distance between the two orderings.
    r_nhats = both["min_delta_v_kms"].rank()
    r_ship = both.iloc[:, 1].rank()
    gap = (r_nhats - r_ship).abs() / len(both)
    top = pd.DataFrame({"nhats_rank": r_nhats, "shipped_rank": r_ship,
                        "gap_frac": gap}).sort_values("gap_frac", ascending=False).head(args.top)
    out = both.join(top).loc[top.index].join(
        m[[des_col]].rename(columns={des_col: "designation"})) \
            .reset_index(drop=True)
    print(f"\nTop {args.top} rank disagreements (NHATS says reachable, shipped ranking disagrees or vice versa):")
    print(out.to_string(index=False))

    print("\nNOTE: NHATS is round-trip + crewed-constrained — an upper bound on a")
    print("differently-shaped quantity. Transfer the RANK disagreement only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
