---
description: "galpy 1.12.1 measured live on py3.14 Windows (its cp314 C extension fails to load and falls back silently; plain-float inputs are read in natural units so a 'solar' orbit escapes the galaxy with perfect energy conservation, while astropy Quantity inputs give the sane answer) and ANISE 0.10.6 as a SPICE replacement (kernel-support matrix showing CK/SCLK/DSK unsupported, TRL-9 flight heritage, bindings importable on py3.14 where anise.time is hifitime)"
source_repo: jobovy/galpy at PyPI/GitHub and nyx-space/anise crates.io + GitHub README, 2026-11-04
tested_version: "galpy **LIVE-RUN** on CPython 3.14.7 in an isolated venv with `PYTHONPATH` cleared (wheel install; A/B tests recorded below). ANISE **registry-verified + import-tested live** (`import anise` works, `Almanac()` signature measured); no ephemeris computation was performed because that requires kernel/meta files"
verified_date: "2026-11-04"
---

# galpy (measured) and ANISE (SPICE-replacement status)

## galpy 1.12.1 — two silent traps, both reproduced on this box

Install is fine (`uv pip install galpy` → cp314 win_amd64 wheel; numpy 2.5.4 + scipy 1.18.1 resolve cleanly). Then:

### Trap 1 — the compiled extension does not load, and nothing stops to tell you

```
galpyWarning: libgalpy C extension module not loaded, because of error 'Could not find module
'...\site-packages\libgalpy.cp314-win_amd64.pyd' (or one of its dependencies).'
galpyWarning: Cannot use C integration because C extension not loaded (using leapfrog instead)
```

The `.pyd` **is present** in the wheel yet fails to load ("or one of its dependencies" — a missing DLL dependency, not a missing file). galpy emits *warnings* and continues with pure-Python integration. So results stay correct but an orbit-integration study that was expected to take seconds takes minutes-to-hours, and any code path that depends on the C-only integrators (`dop853`, symplectic) silently degrades. Treat that warning as a hard stop in performance work: check `warnings` output rather than assuming silence means health.

### Trap 2 — plain floats are natural units, so your numbers can be wrong by ~two orders of magnitude with perfect diagnostics

The default normalisation is read straight from the installed package (`galpy/util/config.py`, line 9):

```python
"normalization": {"ro": "8.", "vo": "220."},
```

Measured `vcirc(MWPotential2014, R)` returns **dimensionless** values: at natural R = 1 it is exactly **1.0**, i.e. the potential is normalised so v_c(ro) = 1 → ×vo = **220 km/s**. At larger radii I measured 2→0.922, 5→0.826, 8→0.769, 12→0.712 — and reading `0.769` as "km/s at 8 kpc" is the mistake waiting to happen (it is natural velocity at **natural** R = 8, i.e. 64 kpc).

The consequence for orbits, measured: an apparently-canonical solar orbit written with plain floats — `Orbit([8.0, 5.0, 236.0, 0.01, 7.0, 0.0])` integrated over 1 Gyr in `MWPotential2014` — means R = 8 natural units (≈64 kpc) and v_T = 236 natural velocities (tens of thousands of km/s). It **escapes**, drifting to R ≈ 236 with z reaching ~7, raising *no error and no warning*.

And the part that makes this genuinely dangerous: integrator self-checks stay perfect on nonsense. Over that same run I measured energy drift **0.006 ppm** and Lz drift **0.000 ppm**. Conservation validates the *integrator*, never your unit assumption — so a "the numerics are fine" check is not evidence the answer is physical. (This is pstack's *Explain the Number* in practice: name what limits the number and rule out that it measured something else — `verification-culture/references/pstack-principle-steering.md`.)

**Falsified along the way:** installing astropy does **not** switch galpy to physical units. I re-ran the identical probe after adding astropy (with pyerfa) — output byte-for-byte unchanged, still natural units. So "just install astropy" is not the fix; be explicit at construction time.

**The working recipe, measured:** pass **astropy Quantity** objects and galpy carries real units through integration:

```python
Orbit([8.*u.kpc, 5.*u.km/u.s, 236.*u.km/u.s, 0.01*u.kpc, 7.*u.km/u.s, 0.*u.deg])
# integrated 1 Gyr in MWPotential2014 -> R stays in [8.000, 8.634] kpc: a sane near-circular orbit
```

Note `Orbit(..., ro=8.2, vo=236.)` kwargs alone did **not** reinterpret the positional floats (same escape behaviour measured) — those arguments set scale metadata rather than declaring "these inputs are km/s". Use Quantity inputs; don't rely on the kwargs. Corollary worth keeping generally: **never attach units to output that were not attached to input** — `.R(ts)` returns whatever system the orbit carries, so a `kpc` label you added in your own f-string is how this bug survives code review.

## ANISE 0.10.6 — where it genuinely replaces SPICE, and where it cannot

Registry: crates.io **anise 0.10.6**, updated 2026-10-19, ~241 k downloads; PyPI bindings also at **0.10.6** with `cp314-win_amd64` wheels *and* free-threaded `cp314t` builds — installed and imported here without trouble (no runtime deps declared). Measured API surface: `Almanac, MetaAlmanac, MetaFile, LocationDataSet, Aberration, rotation, time, astro, constants, analysis`, and **`Almanac()` requires a positional kernel/meta path** (`TypeError: Almanac.__new__() missing 1 required positional argument: 'path'`) — nothing computes until you point it at meta/kernel files.

Useful structural fact: `anise.time` *is* the hifitime binding surface (measured exports `Epoch, TimeScale, Duration, LeapSecondsFile, HifitimeError, Ut1Provider, TimeSeries…`), so this catalog's existing hifitime notes apply directly to ANISE timing work.

Heritage claim from its README (source-read, not independently verified): **NASA TRL 9**, "used throughout the operations of the Firefly Blue Ghost lunar lander, from launch until successful landing". Its pitch against CSPICE/SpiceyPy is thread safety by Rust ownership (SPICE keeps global state + locks), parallel queries, type-checked frames, and S-expression serialisation.

**The decision-critical part is its kernel matrix** — read it before promising anyone a SPICE replacement:

| Kernel | ANISE status | Meaning in practice |
| --- | --- | --- |
| **BSP / SPK** | ✅ as-is | ephemerides work today |
| **BPC** (planetary constants) | ✅ as-is | GMs etc. via binary |
| **TK** text frame kernel | 🔄 needs conversion to `.pca`/`.lka` | extra preprocessing step |
| **LSK**, **GM** | 🔄 need conversion | leap-second/metadata must be transformed first |
| **CK** (attitude) | ❌ unsupported | **no attitude reconstruction** |
| **SCLK** | ❌ unsupported | no spacecraft-clock handling |
| **DSK** (terrain/shape) | ❌ unsupported | no shape models / occultation-terrain |
| **IK / EK** (instruments/events) | ❌ unsupported | no instrument geometry or event tables |

So: for ephemeris-driven work (positions/velocities from SPK, frame transforms, planning batches) ANISE is a credible modern option with flight heritage and thread-safety SPICE lacks. For anything touching **attitude, spacecraft clock, body shape or instrument/event metadata it cannot replace SpiceyPy yet** — keep the legacy toolchain for those rather than discovering this mid-analysis. Text-kernel inputs (TK/LSK/GM) also cost you a conversion step; budget that into any migration.

## Choosing among them here

`galpy` is galactic-dynamics science (potentials, orbits, disc distributions) — nothing to do with mission ephemerides; `ANISE`/SPICE are mission time-and-position infrastructure. They rarely substitute for each other; both complement the skyfield/NAIF-SPK route already covered in this skill and the hifitime notes in `astro-library-notes`.
