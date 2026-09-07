#!/usr/bin/env python3
"""Asterank orbit-sigma + Shoemaker-Helin dv probe.

Two things this API gives for free, both verified live 2026-09-07 (this machine):

1. The DIAGONAL of each body's orbital covariance — sigma_a/sigma_e/sigma_i/
   sigma_om/sigma_w/sigma_ma (+ derived sigma_q/ad/per/n/tp) for ~600K bodies, a
   cheap input to any confidence-weighted ranking or pymc layer (see SKILL.md open
   candidates); complements NEODyS's full 6x6 matrix on the top-N.

2. The Shoemaker-Helin `dv` column — STILL LIVE via targeted queries
   ({"name":"Eros"} -> 6.112, {"pdes":"1999 AO10"} -> 5.380; stable across repeats).
   CORRECTION to the 2026-09-07 audit: bulk-scan projections (query={}) simply do not
   carry a dv key at all — that is why it looked dead. Asterank remains an external
   delta-v oracle for targeted bodies alongside JPL NHATS.

Lookup keys (verified 2026-09-07): MPC des via `pdes` ("1999 AO10"), proper names
via `name` ("Eros"); the query param is a JSON object, not free text.

Usage:
    python asterank_sigma_probe.py "1999 AO10" Eros   # spot-check specific bodies
    python asterank_sigma_probe.py --top N            # sample N rows for schema sanity

Output: a compact table of the sigma columns + observation provenance keys, with
sanity notes (empty strings = not populated; garbage economics fields are known).
Read-only research tool. Endpoint is keyless and paginated — be polite (one page
per run by default).
"""
import argparse
import json
import re

import pandas as pd
import requests

API = "http://www.asterank.com/api/asterank"


def fetch_page(query: str, limit: int, offset: int) -> list[dict]:
    resp = requests.get(API, params={"query": query, "limit": limit,
                                     "offset": offset}, timeout=120)
    resp.raise_for_status()
    return resp.json()


SIGMA_COLS = ["sigma_a", "sigma_e", "sigma_i", "sigma_om", "sigma_w", "sigma_ma",
              "sigma_q", "sigma_ad", "sigma_per", "sigma_n", "sigma_tp"]
PROVENANCE = ["n_del_obs_used", "n_dop_obs_used", "data_arc", "rms",
              "condition_code", "orbit_id"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("designations", nargs="*", help="bodies to look up (MPC des like '1999 AO10', or proper name like 'Eros')")
    ap.add_argument("--top", type=int, default=10, help="--top mode: sample N rows")
    args = ap.parse_args()

    if args.designations:
        # Asterank's query param is a JSON object; lookup keys verified 2026-09-07:
        #   pdes  -> MPC designation ("1999 AO10"); name -> proper name ("Eros").
        frames = []
        for des in args.designations[:25]:  # politeness cap
            rows, tried = [], None
            if re.match(r"^\d{4}\s", des.strip()):       # MPC-style temporary/permanent des
                qobj = {"pdes": des}
            elif des.isdigit():                            # plain number -> pdes is numeric for numbered bodies
                qobj = {"pdes": des}
            else:                                          # proper names and anything else
                qobj = {"name": des}
            tried = json.dumps(qobj)
            try:
                rows = fetch_page(tried, limit=5, offset=0)
            except requests.RequestException as e:
                print(f"  {des}: FETCH FAILED ({e})")
                continue
            if not rows:
                # fallback: the other key style
                alt = {"name": des} if "pdes" in qobj else {"pdes": des}
                try:
                    rows = fetch_page(json.dumps(alt), limit=5, offset=0)
                except requests.RequestException as e:
                    print(f"  {des}: FETCH FAILED on fallback ({e})")
            if not rows:
                print(f"  {des}: no match (tried pdes + name)")
                continue
            frames.append(rows[0])
        df = pd.DataFrame(frames)
    else:
        n = max(1, min(args.top, 50))
        rows = fetch_page("{}", limit=n, offset=0)
        df = pd.DataFrame(rows)

    if df.empty:
        print("No data returned.")
        return 1

    id_cols = [c for c in ("name", "pdes", "prov_des") if c in df.columns]
    cols = id_cols + [c for c in SIGMA_COLS + PROVENANCE if c in df.columns]
    out = df[cols].copy()
    # Asterank returns empty strings where a value is absent — make that explicit.
    for c in SIGMA_COLS:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")

    print(f"=== Asterank sigma probe ({len(out)} rows) ===")
    with pd.option_context("display.width", 200, "display.max_columns", None):
        print(out.to_string(index=False))

    # Schema sanity notes (the 2026-09-07 re-probe findings, checked live each run).
    missing = [c for c in SIGMA_COLS if c not in df.columns]
    empty_frac = {c: float((df[c].astype(str) == "").mean())
                  for c in SIGMA_COLS if c in df.columns}
    print("\nSchema notes:")
    print(f"  sigma columns present: {len(SIGMA_COLS) - len(missing)}/{len(SIGMA_COLS)}"
          + (f" MISSING: {missing}" if missing else ""))
    for c, f_ in empty_frac.items():
        flag = "  <-- EMPTY on every sampled row" if f_ >= 1.0 else ""
        print(f"  {c}: empty-string fraction {f_:.0%}{flag}")
    dead = [c for c in ("dv",) if c in df.columns]
    new_keys = [c for c in ("two_body", "DT") if c in df.columns]
    print(f"  legacy dv column: {'present on these rows' if dead else 'absent from this projection'} — NOTE the two API modes differ:")
    if dead:
        nonempty_dv = sum(1 for v in df["dv"] if str(v).strip() not in ("", "None"))
        print(f"    targeted-query rows carry real Shoemaker-Helin values ({nonempty_dv}/{len(df)} populated here);")
        print("    bulk-scan (query={}) projections have NO dv key at all — the 2026-09-07 'dv column gone' finding was a projection artifact.")
    if new_keys:
        all_empty = all((df[c].astype(str) == "").all() for c in new_keys)
        print(f"  placeholder keys {new_keys}: "
              f"{'empty on every sampled row' if all_empty else 'NOW POPULATED — re-audit!'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
