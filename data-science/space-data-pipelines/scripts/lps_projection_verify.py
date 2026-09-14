#!/usr/bin/env python3
"""Verify the south-pole Lunar Polar Stereographic (LPS) projection math used by nasa/aegis (AEGIS).

The AEGIS TypeScript port (src/utils/lgrs/southLps.ts) claims equivalence with pinned Python
lgrs 0.3.0. This script re-implements the same math in stdlib-only Python and checks it against
oracle vectors generated from the real lgrs 0.3.0 package on 2026-09-13 (Python 3.13 venv):

    $ uv pip install --python <py3.13> lgrs   # requires Python >= 3.13
    >>> from lgrs.coords import LatLonPoint
    >>> p = LatLonPoint(-84.5276, 0.0)        # NOTE: (latitude, longitude) order!
    >>> e, n = p.to_lps().easting, p.to_lps().northing

Oracle vectors below were produced exactly that way and embedded so the script is self-contained.
Exit code 0 = all checks pass; 1 = any error exceeds tolerance (default: sub-millimetre).

Usage:
    py lps_projection_verify.py            # stdlib-only, embedded oracles
    py lps_projection_verify.py --oracle   # additionally re-generates vectors from installed lgrs
                                           # (needs Python >= 3.13 + `pip install lgrs`)
"""

from __future__ import annotations

import math
import sys

# --- Constants: nasa/aegis src/utils/consts.ts (cross-checked against lgrs output) -------------
MOON_MEAN_RADIUS = 1737.4e3   # m
K0 = 0.994                    # central scale factor at the pole
FALSE_EASTING = 500_000.0     # m — LPS easting of the south pole
FALSE_NORTHING = 500_000.0    # m — LPS northing of the south pole

# --- Oracle vectors: lgrs 0.3.0, generated 2026-09-13 -----------------------------------------
ORACLES = [
    # (name, latitude_deg, longitude_deg, e_lps_m, n_lps_m)
    ("south_pole", -90.0, 0.0, 500_000.0, 500_000.0),
    ("artemis_base_camp_area", -84.5276, 0.0, 500_000.0, 665_071.3605489866),
    ("shackleton_rim_west", -89.0, -13.9, 492_759.004188882, 529_259.5065272454),
]

TOLERANCE_M = 1e-3  # sub-millimetre; the verified port error was ~3.5e-10 m


def lat_lon_to_south_lps(lat_deg: float, lon_deg: float) -> tuple[float, float]:
    """Polar stereographic, origin (-90 deg, 0 deg), scale K0 at pole — AEGIS southLps.ts math."""
    phi = math.radians(lat_deg)
    lam = math.radians(lon_deg)
    phi_o = -math.pi / 2.0
    lam_o = 0.0

    denom = 1 + (math.sin(phi_o) * math.sin(phi)
                 + math.cos(phi_o) * math.cos(phi) * math.cos(lam - lam_o))
    scale = (2 * K0) / denom

    easting = MOON_MEAN_RADIUS * scale * math.cos(phi) * math.sin(lam) + FALSE_EASTING
    northing = (MOON_MEAN_RADIUS * scale
                * (math.cos(phi_o) * math.sin(phi)
                   - math.sin(phi_o) * math.cos(phi) * math.cos(lam - lam_o))
                ) + FALSE_NORTHING
    return easting, northing


def check_oracles() -> float:
    max_err = 0.0
    for name, lat, lon, e_ref, n_ref in ORACLES:
        e, n = lat_lon_to_south_lps(lat, lon)
        de, dn = abs(e - e_ref), abs(n - n_ref)
        max_err = max(max_err, de, dn)
        status = "OK" if max(de, dn) <= TOLERANCE_M else "FAIL"
        print(f"  [{status}] {name:24s} ({lat:+8.4f}, {lon:+7.3f}) -> "
              f"e={e:.6f} n={n:.6f} | dE={de:.3e} m dN={dn:.3e} m")
    return max_err


def check_live_lgrs() -> None:
    """Re-generate oracle vectors from the installed lgrs package (Python >= 3.13)."""
    try:
        import lgrs  # noqa: F401
        from lgrs.coords import LatLonPoint
    except Exception as exc:  # ImportError or version gate
        print(f"  [SKIP] live lgrs check unavailable ({exc.__class__.__name__}: {exc})")
        return

    for name, lat, lon, e_ref, n_ref in ORACLES:
        p = LatLonPoint(lat, lon)  # (latitude, longitude) order — the classic swap trap
        lps = p.to_lps()           # LpsPoint object; .easting/.northing attrs (not subscriptable)
        de, dn = abs(float(lps.easting) - e_ref), abs(float(lps.northing) - n_ref)
        print(f"  [OK] live lgrs {name:24s} vs embedded oracle dE={de:.3e} m")


def main(argv: list[str]) -> int:
    print("LPS projection verification (nasa/aegis south-pole LPS math)")
    max_err = check_oracles()

    if "--oracle" in argv:
        print("\nLive lgrs cross-check:")
        check_live_lgrs()

    # Domain-limit sanity: the -80 deg cutoff AEGIS uses for its viewport domain radius.
    r_domain = 2 * MOON_MEAN_RADIUS * K0 * math.tan(math.radians((90 + (-80)) / 2))
    print(f"\nViewport domain radius (to lat=-80): {r_domain:.1f} m")

    if max_err <= TOLERANCE_M:
        print(f"PASS — max error vs lgrs 0.3.0 oracle: {max_err:.3e} m "
              f"(tolerance {TOLERANCE_M:g} m)")
        return 0
    print(f"FAIL — max error {max_err:.3e} m exceeds tolerance {TOLERANCE_M:g} m")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
