#!/usr/bin/env python3
"""Verify AEGIS cap-grid tiling invariants + LGRS converter logic (stdlib only).

Re-derives the math from nasa/aegis GIS_data_conversion_pipeline/esri-to-aegis-lunar-southpole/
(common/tile_to_cap_grid.py, grid/convert_lgrs.py) and checks it numerically:

  Part A — cap-grid tiling invariants (the z0 invariant + padding trap):
    * per-layer max_zoom = ceil(log2(z0_res / native_res)) never stores a layer coarser than source
    * the padded canvas is exactly one z0 tile wide (256 * z0_res) at EVERY max zoom — zoom-invariant
    * with that padding, tiles-per-row at every level z <= m is an exact integer power of two, so
      gdal's per-level ceil(rows/2) re-derivation never rounds and TMS row 0 stays anchored to the
      padded cap top (and bottom-left to CAP_MIN) — drift = 0 m at all zooms
    * counter-example: "pad only to next whole tile" produces up-to-a-tile northward drift at some
      coarser level for a realistic sub-cap data extent (the 'layer jumps when you zoom out' bug)

  Part B — LGRS converter logic (port of convert_lgrs.py, pure functions):
    * ACC split rules: 6-char -> [3:5]/[5:], 5-char -> [3:4]/[4:]
    * row/column scan over centre-Y steps with the blank-before-new-row rule

Exit code = number of failed checks (0 = all pass). Re-run any time: `py scripts/cap_grid_verify.py`.
"""

from __future__ import annotations

import math
import sys

# AEGIS lunar south-pole cap grid constants (config.py)
CAP_MIN = -931100.0   # cap bottom-left, both axes
CAP_MAX = 931100.0    # cap top-right, both axes
TILE = 256            # tile size in pixels
Z0_RES = 12800.0      # z0 units-per-pixel == mission projResUnitsPerPixel

FAILS = []


def check(name: str, ok: bool, detail: str = "") -> None:
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {name}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


def max_zoom_for(native_res: float) -> int:
    """Per-layer depth: next-deeper rung so out_res <= native_res."""
    return max(0, math.ceil(math.log2(Z0_RES / native_res)))


# ---------------------------------------------------------------------------
# Part A — cap-grid tiling invariants
# ---------------------------------------------------------------------------

def part_a() -> None:
    print("Part A: cap-grid tiling invariants")

    # A1. per-layer depth never stores a layer coarser than its source, and is the shallowest such rung
    for r_in in (5.0, 4.0, 3.0, 2.0, 1.0):
        m = max_zoom_for(r_in)
        out_res = Z0_RES / 2**m
        check(f"max_zoom({r_in:g} m/px)={m}", out_res <= r_in + 1e-12 and (Z0_RES / 2**(m - 1)) > r_in,
              f"out_res {out_res:g}")

    # A2. padded canvas span is zoom-invariant: exactly one z0 tile of 256*z0_res metres at every m
    for m in range(0, 15):
        out_res = Z0_RES / 2**m
        tile_span = TILE * out_res
        n_cap_tiles = 2**m
        span = n_cap_tiles * tile_span
        check(f"canvas span @z{m} == {TILE*Z0_RES:g} m", math.isclose(span, TILE * Z0_RES), f"got {span:g}")

    # A3. the padded canvas covers the whole cap (so no layer can fall off it)
    check("padded canvas >= cap width", TILE * Z0_RES >= CAP_MAX - CAP_MIN,
          f"{TILE*Z0_RES:g} vs {CAP_MAX-CAP_MIN:g}")

    # A4. full padding (2**m tiles = one z0 tile): canvas height in ground metres is a power-of-two
    #     multiple of every coarser level's tile span -> exact integer tile rows at all zooms, drift 0.
    H_full = TILE * Z0_RES
    for m in (14, 8, 3):
        worst_drift = 0.0
        for z in range(0, m + 1):
            span_z = TILE * Z0_RES / 2**z          # one tile's ground span at level z
            true_tiles_z = H_full / span_z         # canvas height expressed in tiles of this level
            if abs(true_tiles_z - round(true_tiles_z)) > 1e-9:
                worst_drift = max(worst_drift, min(true_tiles_z % 1, 1.0 - true_tiles_z % 1) * span_z)
        check(f"full padding -> integer tile rows at every z<=z{m}, drift=0", worst_drift == 0.0,
              f"worst drift {worst_drift:g} m")

    # A5. counter-example: naive "pad data extent to next whole tile at max zoom only". gdal re-derives
    #     the per-level tile count as ceil(tiles/2) walking up; an ODD padded tile count breaks exact
    #     halving, so some coarser level's grid is a non-integer number of ideal-lattice tiles — TMS row 0
    #     content walks off CAP_MIN (the 'layer jumps when you zoom out' bug).
    m = 14
    span_m = TILE * Z0_RES / 2**m                  # 200 m at z14
    data_h_odd = 500.0                             # sub-cap layer -> ceil(500/200) = 3 tiles (odd)
    t_naive = math.ceil(data_h_odd / span_m)       # naive padded tile count at max zoom
    check("naive padding yields an odd tile count", t_naive == 3, f"got {t_naive}")
    H_naive = t_naive * span_m                     # actual canvas ground height (600 m)
    bad_levels_odd = []
    for z in range(m - 1, -1, -1):                 # walk up from max zoom like gdal does
        true_tiles_z = H_naive / (TILE * Z0_RES / 2**z)   # ideal-lattice tile rows at this level
        if true_tiles_z >= 1.0 and abs(true_tiles_z - round(true_tiles_z)) > 1e-9:
            bad_levels_odd.append(z)               # grid cannot match the uniform lattice here
    check("naive (odd-tile) padding -> non-exact halving at some coarser level", len(bad_levels_odd) > 0,
          f"bad levels {sorted(bad_levels_odd)}")

    # A6. same naive procedure with an EVEN padded count: every coarser level is either exact or pure
    #     over-coverage (<1 ideal tile -> one row legitimately spans it), so the lattice never breaks.
    data_h_even = 400.0                            # ceil(400/200) = 2 tiles (even)
    t_naive_e = math.ceil(data_h_even / span_m)
    H_naive_e = t_naive_e * span_m
    bad_levels_even = []
    for z in range(m - 1, -1, -1):
        true_tiles_z = H_naive_e / (TILE * Z0_RES / 2**z)
        if true_tiles_z >= 1.0 and abs(true_tiles_z - round(true_tiles_z)) > 1e-9:
            bad_levels_even.append(z)
    check("even padded tile count -> exact lattice at every level (parity is what matters)",
          len(bad_levels_even) == 0, f"bad levels {sorted(bad_levels_even)}")


# ---------------------------------------------------------------------------
# Part B — LGRS converter logic (pure-function port of convert_lgrs.py)
# ---------------------------------------------------------------------------

def split_condensed(condensed: str) -> tuple[str, str]:
    half = len(condensed) // 2
    return condensed[:half], condensed[half:]


def clean_lgrs_coordinate(lgrs_acc: str, empty_lgrs: bool) -> tuple[str, str, str]:
    if empty_lgrs:
        return lgrs_acc, " ", " "
    n = len(lgrs_acc)
    if n == 6:   # 100 m interval
        return lgrs_acc, lgrs_acc[3:5], lgrs_acc[5:]
    if n == 5:   # 1 km interval
        return lgrs_acc, lgrs_acc[3:4], lgrs_acc[4:]
    raise ValueError(f"Unexpected LGRS length {n}")


def row_and_column_counter(dist: list[float], i: int, row: int, column: int) -> tuple[int, int, bool]:
    n = len(dist)
    empty_lgrs = False
    current, last = dist[i], (dist[i - 1] if i > 0 else None)
    next_val = dist[i + 1] if i < n - 1 else None
    if i == 0:
        return 0, 0, False
    if i == n - 1:
        row, column = (row + 1, 0) if current > last else (row, column + 1)
        return row, column, False
    if next_val is not None and current < next_val:
        empty_lgrs = True
    row, column = (row + 1, 0) if current > last else (row, column + 1)
    return row, column, empty_lgrs


def part_b() -> None:
    print("Part B: LGRS converter logic")

    # B1. condensed split halves easting/northing levels
    check("condensed 'Z4F3' -> ('Z4','F3')", split_condensed("Z4F3") == ("Z4", "F3"))
    check("condensed 'ZF'   -> ('Z','F')",  split_condensed("ZF") == ("Z", "F"))

    # B2. condensed split (generate_lgrs.py path) and legacy ACC truncation (ESRI export path).
    #     Fidelity: expected values are what the SOURCE code produces, not its prose. Note the
    #     verified source discrepancy documented in lunar-gis-patterns-aegis.md: for n==6 the
    #     comment claims "keep last 4 chars, split 2 + 2" but [3:5]+[5:] keeps only the LAST THREE
    #     as a 2+1 split. (n==5 branch matches its own docstring: last 2 chars, 1+1.)
    f1, l1, r1 = clean_lgrs_coordinate("AAQ9K7", False)   # 6-char input -> code does [3:5]/[5:]
    check(f"n=6 fidelity: 'AAQ9K7' -> L/R '{l1}'/'{r1}'", (f1, l1, r1) == ("AAQ9K7", "9K", "7"))
    f2, l2, r2 = clean_lgrs_coordinate("AB2C3", False)     # 5 chars -> [3:4]/[4:] (matches its docstring)
    check(f"n=5 fidelity: 'AB2C3' -> L/R '{l2}'/'{r2}'", (f2, l2, r2) == ("AB2C3", "C", "3"))
    # The discrepancy itself, made explicit: a 6-char string's docstring-promised output ('last4 as 2+2')
    promised = ("AAQ9K7"[2:], "AAQ9K7"[2:4], "AAQ9K7"[4:])   # what 'keep last 4, split 2+2' would give
    check("source discrepancy confirmed: code != its own docstring for n=6", (l1, r1) != (promised[1], promised[2]),
          f"code gives '{l1}'/'{r1}', docstring implies '{promised[1]}'/'{promised[2]}'")
    f3, l3, r3 = clean_lgrs_coordinate("AZUZ4F3", True)
    check("blank-before-new-row blanks L/R but keeps full ACC", (l3, r3) == (" ", " ") and f3 == "AZUZ4F3")

    # B3. row/column scan: 2 rows x 3 cols, centY steps by interval at each new row
    dist = [0.0, 0.0, 0.0, 100.0, 100.0, 100.0]           # metres; row-major order
    seq = []
    row = column = 0
    for i in range(len(dist)):
        row, column, empty = row_and_column_counter(dist, i, row, column)
        seq.append((row, column, empty))
    expected = [(0, 0, False), (0, 1, False), (0, 2, True),   # last point of row 0 -> blank flag
                (1, 0, False), (1, 1, False), (1, 2, False)]  # final feature closes the row without a next
    check("row/col scan over 2x3 grid", seq == expected, f"got {seq}")


def main() -> None:
    part_a()
    part_b()
    print(f"\n{'=' * 50}\n{len(FAILS)} failed / {'ALL CHECKS PASSED' if not FAILS else 'SEE ABOVE'}")
    sys.exit(len(FAILS))


if __name__ == "__main__":
    main()
