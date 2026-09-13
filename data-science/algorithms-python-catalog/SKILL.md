---
name: algorithms-python-catalog
description: "Python algorithm catalog: when to hand-roll vs stdlib."
version: v0.1.0
author: Hermes Agent (mined from TheAlgorithms/Python, all ported code oracle-verified)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [algorithms, strings, checksums, geodesy, numerical-methods, dp, backtracking, catalog]
    related_skills: [python-craft, maps, system-design-scaling, evolutionary-ml, optimization-modeling-pyomo, scrapling]
---

<!-- source: TheAlgorithms/Python (MIT) cloned at 2026-09-13 @ commit 23c4208; every snippet in this skill and its references was executed live on Windows / Python 3.13 and cross-checked against stdlib oracles (zlib, bisect, re, numpy.roots) before being recorded -->

## What This Skill Does

Curated navigator for TheAlgorithms/Python — a 1,466-file educational catalog of
algorithm implementations in ~50 categories. Carries three layers:

1. **A decision map** (`references/catalog-map.md`): all 50 categories with what each is worth,
   which files are stdlib-only vs numpy/tensorflow-dependent, and the "use X instead" rule for
   every category (the repo's own README warns its implementations may be less efficient than
   stdlib — that warning is correct).
2. **Verified from-scratch code** (`references/algorithms-from-scratch.md`): hand-rolled string
   matching (KMP, Z-function, Aho-Corasick, Rabin-Karp), checksums (Adler/Fletcher/djb2/sdbm/Luhn),
   haversine geodesy, Brent/Newton root-finding, O(n log n) LIS, N-queens diagonal invariants,
   financial formulas, CPU scheduling — each with its decision rule and verified numbers.
3. **A re-runnable verification harness** (`scripts/algorithms_verify.py`): every recorded claim is
   asserted live (KMP vs `str.find`, Aho-Corasick vs regex ground truth incl. nested keywords,
   Adler-32 == `zlib.adler32`, haversine vs OSRM road distance, Brent vs `numpy.roots`, N-queens
   solution counts 2/4/92).

## When to Use

- You need multi-pattern search over text (profanity lists, error codes, DNA motifs) → Aho-Corasick section
- You need a non-cryptographic checksum or string hash and want the *why* behind each constant → checksums section
- Offline great-circle distance between two lat/lons without an API call → haversine section (maps skill's OSRM is road distance; this is straight-line)
- Root-finding / ODE solving from scratch, or understanding what `scipy.optimize`/`solve_ivp` do internally → numerical methods section
- Interview-style DP/backtracking patterns you want to see implemented plainly (LIS patience sorting, N-queens invariants) → combinatorics section
- You're deciding whether a problem is worth hand-rolling at all vs `bisect`/`heapq`/`collections`/regex → the decision tables here and in `catalog-map.md`

## Quick Decision Table (the whole skill in one view)

| Need | Use instead of hand-rolling | Hand-roll only when... |
|---|---|---|
| Find a pattern once | `str.find` / `re.search` | — (C-speed, no reason to beat it) |
| All occurrences, overlapping | `re.findall(r'(?=pat)', s)` | Pattern set is dynamic and huge → Aho-Corasick |
| Many patterns, one text | per-pattern regex loop | Text × patterns is large enough that O(n·m) hurts → Aho-Corasick (verified vs regex ground truth) |
| Sliding-window substring equality | rolling hash idea only in theory | Rabin-Karp — but know the docstring's "O(nm)" claim is wrong; it's expected-linear with a verify step |
| Checksum for integrity | `zlib.crc32` / `hashlib.blake2b` | Teaching, or protocol parity (gzip needs Adler-32 exactly) |
| String hash for dicts/sets | Python's built-in `hash()` | You need cross-language stable values → djb2/sdbm (mind the 64-bit wrap pitfall) |
| Card number validation | Luhn — it IS the standard, no library needed | always hand-rollable in 10 lines |
| Straight-line distance on Earth | `geopy`/OSRM for road distance | Offline / no API → haversine (verified: NYC→LA 3,935.7 km straight vs ~3,940 km OSRM great-circle sanity) |
| Root of f(x)=0 with a bracket | `scipy.optimize.brentq` | No scipy available → Brent's method section (robust; verified vs numpy.roots) |
| Root when you have a good guess + derivative-free setting | Newton-Raphson section — but it DIVERGES without care (verified: cos at 0 raises, x²+1 never converges) | |
| ODE integration | `scipy.integrate.solve_ivp` (adaptive!) | Learning only — the repo's "RKF45" is fixed-step and does NOT adapt its step size despite the name |
| LIS length | patience-sorting tails array, O(n log n) section | verified vs bisect-based reference on random arrays |

## Verification Status

Run `py scripts/algorithms_verify.py` — it re-executes every claim in this skill (stdlib-only;
the numpy cross-checks are optional and skipped if numpy is absent). All checks passed at mining
time 2026-09-13 on Python 3.13, Windows 11.
