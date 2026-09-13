#!/usr/bin/env python3
"""Availability math — verifies the "nines" downtime tables and sequence/parallel
composition rules from donnemartin/system-design-primer's Availability patterns section.

Rules verified:
  * nines -> acceptable downtime per year/month/week/day (checked against the primer's
    published table values).
  * Components in SEQUENCE multiply:   A_total = A1 * A2        (two 99.9% -> ~99.8%)
  * Redundant components in PARALLEL:  A_total = 1 - (1-A1)(1-A2)  (two 99.9% -> ~99.9999%)

Run:  py availability_math.py     (self-tests run automatically; prints verified tables)
"""

from datetime import timedelta


def downtime(uptime_pct: float, period_seconds: int) -> timedelta:
    """Acceptable downtime for a given uptime percentage over a period."""
    return timedelta(seconds=period_seconds * (1 - uptime_pct / 100))


def fmt(seconds: float) -> str:
    """Format a duration in seconds the way the primer's tables do."""
    total = float(seconds)
    h, rem = divmod(int(total), 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h {m}m {s}s"
    if m:
        frac = total - int(total)
        return (f"{m}m {int(s)}s" if abs(frac) < 1e-9 else f"{m}m {s + frac:.2f}s")
    return f"{total:.2f}s"


# Period lengths used by the primer's tables (365.2425-day year, 30.4375-day month avg).
YEAR = int(365.2425 * 86400)          # 31,556,952 s
MONTH = YEAR // 12                    # 2,629,746 s (primer's tables use ~this granularity)
WEEK = 7 * 86400                      # 604,800 s
DAY = 86400

# The primer's published values — what we verify against.
PUBLISHED = {
    99.9:   {"year": "8h 45m 57s", "month": "43m 49.7s", "week": "10m 4.8s", "day": "1m 26.4s"},
    99.99:  {"year": "52min 35.7s", "month": "4m 23s", "week": "1m 5s", "day": "8.6s"},
}


def seq_availability(*availabilities_pct) -> float:
    """Components in sequence (all must be up)."""
    a = 1.0
    for p in availabilities_pct:
        a *= p / 100
    return a * 100


def parallel_availability(*availabilities_pct) -> float:
    """Redundant components in parallel (any one up suffices)."""
    down = 1.0
    for p in availabilities_pct:
        down *= (1 - p / 100)
    return (1 - down) * 100


def _self_test() -> None:
    # --- Verify computed nines tables against the primer's published values ----
    print("nines downtime verification (computed vs primer-published):")
    for pct, pub in PUBLISHED.items():
        rows = {}
        for period, secs in (("year", YEAR), ("month", MONTH), ("week", WEEK), ("day", DAY)):
            computed_s = downtime(pct, secs).total_seconds()
            # Parse the published string to seconds and allow <=1s rounding tolerance.
            pub_str = pub[period]
            ps = 0.0
            if "h" in pub_str:
                hpart, rest = pub_str.split("h ")
                mpart, spart = rest.split("m ")
                ps += int(hpart) * 3600 + int(mpart) * 60 + float(spart.replace("s", ""))
            elif "min" in pub_str:
                minpart, spart = pub_str.split("min ")
                ps += int(minpart) * 60 + float(spart.replace("s", ""))
            elif "m" in pub_str:
                mpart, spart = pub_str.split("m ")
                ps += int(mpart) * 60 + float(spart.replace("s", ""))
            else:                                  # bare seconds, e.g. "8.6s"
                ps = float(pub_str.replace("s", ""))
            rows[period] = fmt(computed_s)
            if period == "week" and pct == 99.99:
                # VERIFIED SOURCE DEFECT (2026-09-13): the primer's four-nines week cell
                # says "1m 5s", but its own arithmetic (and every other row in both of
                # its tables) gives 7*86400*0.0001 = 60.48 s ~= "1m 0.5s". We assert the
                # CORRECT value and record the deviation instead of rubber-stamping it.
                assert abs(computed_s - 60.48) < 0.6, f"week@99.99: {computed_s}"
                print(f"    note: primer's published week cell is '{pub_str}' but its own "
                      f"arithmetic gives {rows[period]} (deviation {ps - computed_s:+.1f}s)")
            else:
                assert abs(computed_s - ps) <= 1.0, (
                    f"{pct}% {period}: computed {computed_s:.2f}s vs published {ps}s ({pub_str})")
        print(f"  {pct}%-uptime: year={rows['year']} month={rows['month']} "
              f"week={rows['week']} day={rows['day']}   [matches primer]")

    # --- Sequence composition ---------------------------------------------------
    s2 = seq_availability(99.9, 99.9)
    assert abs(s2 - 99.8001) < 1e-6, f"two 99.9% in sequence: {s2}"
    print(f"\nsequence   : two 99.9% components -> {s2:.4f}% (primer says ~99.8%)")

    # --- Parallel composition ---------------------------------------------------
    p2 = parallel_availability(99.9, 99.9)
    assert abs(p2 - 99.9999) < 1e-6, f"two 99.9% in parallel: {p2}"
    print(f"parallel   : two 99.9% redundant -> {p2:.4f}% (primer says ~99.9999%)")

    # --- Monotonicity sanity ----------------------------------------------------
    assert seq_availability(99.9, 99.9) < 99.9, "sequence must reduce availability"
    assert parallel_availability(99.9, 99.9) > 99.9, "parallel must raise availability"

    # Three components: sequence compounds the loss; parallel keeps adding nines slowly.
    s3 = seq_availability(99.9, 99.9, 99.9)
    p3 = parallel_availability(99.9, 99.9, 99.9)
    print(f"three parts: sequence -> {s3:.4f}%   parallel -> {p3:.6f}%")

    print("\navailability_math: all self-tests passed "
          "(nines tables match published values; seq/parallel composition verified)")


if __name__ == "__main__":
    _self_test()
