#!/usr/bin/env python3
"""Runnable reference implementation of the space-datasets pipeline pattern.

Distilled verbatim-in-spirit from juliensimon/space-datasets (MIT) shared helpers:
  scripts/jpl_api.py      -> jpl_query()        (JPL SSD API + retry/backoff)
  scripts/vizier_tap.py   -> vizier_query()     (ADQL pagination via recno, no OFFSET)
  scripts/validate.py     -> check_dataset()    (hard-fail row/schema/null gates)

The one-script-per-dataset pattern it demonstrates:
    Fetch -> Transform(pandas) -> Validate(check_dataset) -> Write(parquet zstd / CSV)
           -> [Upload HF — omitted here; see SKILL.md] -> Status(status.json)

This file runs end-to-end against the LIVE JPL NHATS endpoint as a self-test:

    python pipeline_skeleton.py            # fetch ~7k NEAs, validate, write parquet/CSV to ./out
    python pipeline_skeleton.py --dry-run  # stop after validation (no files written)

Dependencies: requests + pandas (core); pyarrow only if you want parquet output.
"""
import argparse
import io
import json
import sys
import time
from pathlib import Path

import pandas as pd
import requests

# ── Shared helper 1: JPL SSD API with retry/backoff (jpl_api.py pattern) ────────
JPL_BASE = "https://ssd-api.jpl.nasa.gov"


def jpl_query(endpoint: str, params: dict | None = None, timeout: int = 120) -> dict:
    """Query a JPL SSD API endpoint; retries up to 3x with backoff on 5xx."""
    url = f"{JPL_BASE}/{endpoint}"
    for attempt in range(3):
        resp = requests.get(url, params=params, timeout=timeout)
        if resp.status_code < 500:
            resp.raise_for_status()
            return resp.json()
        if attempt < 2:
            wait = 5 * (2 ** attempt)  # 5s, 10s
            print(f"  JPL API {resp.status_code}, retrying in {wait}s ({attempt + 1}/3)...")
            time.sleep(wait)
    resp.raise_for_status()
    return resp.json()


def jpl_fields_data_to_df(payload: dict) -> pd.DataFrame:
    """Convert JPL's {"fields": [...], "data": [[...]]} format to DataFrame."""
    return pd.DataFrame(payload["data"], columns=payload["fields"])


# ── Shared helper 2: VizieR TAP pagination (vizier_tap.py pattern) ───────────────
TAP_URL = "https://tapvizier.cds.unistra.fr/TAPVizieR/tap/sync"
PAGE_SIZE = 500_000


def _fetch_page(adql: str, timeout: int) -> pd.DataFrame:
    resp = requests.post(TAP_URL, data={"QUERY": adql}, params={"FORMAT": "text"},
                         timeout=timeout)
    resp.raise_for_status()
    return pd.read_csv(io.StringIO(resp.text), sep="\t")


def _add_recno_filter(adql: str, max_recno: int) -> str:
    """Append a recno cursor filter (VizieR TAP has no OFFSET — the gotcha)."""
    core = adql.split("WHERE")[0] if "WHERE" in adql else ""
    where = (" ".join(adql.split("WHERE")[1:]) + " AND ") if "WHERE" in adql else " WHERE "
    return f"{core}{where}recno > {max_recno}"


def vizier_query(adql: str, max_rows: int | None = None, timeout: int = 300) -> pd.DataFrame:
    """Run ADQL against VizieR TAP, paginating via recno for catalogs >500K rows."""
    print(f"  VizieR TAP: {adql.strip()[:80]}...")
    df = _fetch_page(adql, timeout)
    if len(df) < PAGE_SIZE and max_rows is None:
        return df
    all_dfs = [df]
    while True:
        if "recno" not in df.columns:
            print("  WARNING: no recno column for pagination; returning what we have")
            break
        paged = _add_recno_filter(adql, int(df["recno"].max()))
        time.sleep(1)
        df = _fetch_page(paged, timeout)
        if len(df) == 0:
            break
        all_dfs.append(df)
        print(f"  ... {sum(len(d) for d in all_dfs):,} rows fetched")
        if max_rows and sum(len(d) for d in all_dfs) >= max_rows:
            break
    result = pd.concat(all_dfs, ignore_index=True)
    return result.head(max_rows) if max_rows else result


# ── Shared helper 3: validation gate (validate.py pattern) ───────────────────────
def check_dataset(df: pd.DataFrame, dataset_name: str, min_rows: int,
                  expected_columns: list[str], critical_columns: list[str] | None = None,
                  max_null_pct: float = 0.05, status_file: Path | None = None) -> None:
    """Hard-fail (SystemExit(1)) on row count below minimum, missing columns, or
    completely-empty columns; warn on critical-column nulls and >20% row drops."""
    # Row count
    if len(df) < min_rows:
        print(f"::error::VALIDATION FAILED [{dataset_name}]: "
              f"{len(df):,} rows < minimum {min_rows:,}")
        sys.exit(1)
    # Schema
    missing = set(expected_columns) - set(df.columns)
    if missing:
        print(f"::error::VALIDATION FAILED [{dataset_name}]: missing columns: {sorted(missing)}")
        sys.exit(1)
    # All-null columns (always fatal — a column that is 100% null means the fetch broke)
    all_null = [c for c in df.columns if df[c].isna().all()]
    if all_null:
        print(f"::error::VALIDATION FAILED [{dataset_name}]: completely empty columns: {sorted(all_null)}")
        sys.exit(1)
    # Critical-column nulls (warn only)
    warnings = 0
    for col in critical_columns or []:
        if col not in df.columns:
            continue
        null_pct = float(df[col].isna().mean())
        if null_pct > max_null_pct:
            print(f"::warning::[{dataset_name}] '{col}' has {null_pct:.1%} nulls (>{max_null_pct:.0%})")
            warnings += 1
    # Row-count trend vs previous run (the truncated-upload guard)
    if status_file and Path(status_file).exists():
        try:
            prev = json.loads(Path(status_file).read_text()).get("_rows", {}).get(dataset_name)
            if prev and len(df) < prev * 0.8:
                drop = (prev - len(df)) / prev
                print(f"::warning::[{dataset_name}] row count dropped {drop:.0%}: "
                      f"{prev:,} -> {len(df):,}")
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
    print(f"Validation passed [{dataset_name}]: {len(df):,} rows, "
          f"{len(df.columns)} columns, {'0 warnings' if not warnings else str(warnings) + ' warning(s)'}")


# ── The dataset script itself: NHATS (the one that matters for economicspace) ────
def fetch_nhats() -> pd.DataFrame:
    """Fetch NASA JPL NHATS accessible-asteroids data and normalize it."""
    payload = jpl_query("nhats.api")
    df = pd.DataFrame(payload["data"])
    # Nested min_dv/min_dur dicts {"dv": ..., "dur": ...} — unwrap (gotcha).
    if "min_dv" in df.columns:
        df["min_delta_v_kms"] = df["min_dv"].apply(
            lambda x: x.get("dv") if isinstance(x, dict) else None)
    if "min_dur" in df.columns:
        df["min_mission_duration_days"] = df["min_dur"].apply(
            lambda x: x.get("dur") if isinstance(x, dict) else None)
    rename = {"des": "designation", "fullname": "full_name",
              "n_via_traj": "n_viable_trajectories", "occ": "orbit_condition_code"}
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    # JPL returns some numerics as strings — coerce (gotcha found live 2026-09-07).
    for col in ("min_delta_v_kms", "orbit_condition_code"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="validate only; write nothing")
    ap.add_argument("--out-dir", default="out", help="output directory (default ./out)")
    args = ap.parse_args()

    print("Fetching NASA NHATS accessible asteroids...")
    df = fetch_nhats()
    print(f"  {len(df):,} rows fetched")

    check_dataset(
        df,
        dataset_name="nhats-accessible-asteroids",
        min_rows=5000,          # the study covers ~7k NEAs; a drop below this = broken fetch
        expected_columns=["designation", "min_delta_v_kms", "orbit_condition_code"],
        critical_columns=["min_delta_v_kms", "n_viable_trajectories"],
    )

    if args.dry_run:
        print("--dry-run: skipping write.")
        return 0

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    try:
        import pyarrow  # noqa: F401
        path = out / "nhats.parquet"
        df.to_parquet(path, compression="zstd", index=False)
    except ImportError:
        path = out / "nhats.csv"
        df.to_csv(path, index=False)
        print(f"  (pyarrow not installed — wrote CSV instead of parquet)")
    # status.json is the row-trend guard's memory across runs.
    sf = out / "status.json"
    prev = json.loads(sf.read_text()) if sf.exists() else {"_rows": {}}
    prev["_rows"]["nhats-accessible-asteroids"] = len(df)
    sf.write_text(json.dumps(prev, indent=2))
    print(f"Wrote {path} ({len(df):,} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
