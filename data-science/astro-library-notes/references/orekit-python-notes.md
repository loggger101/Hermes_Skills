---
description: "Orekit from Python via orekit-jpype 13.1.9: pip-only setup with jdk4py, import-after-initVM rule, what works without data files, data setup helpers"
source_repo: CS-SI/Orekit (Apache-2.0) + gitlab.orekit.org/orekit/orekit_jpype (Apache-2.0)
tested_version: orekit-jpype 13.1.9.0 + jdk4py 25.0.2.1 (JDK 25), pip --target install, Windows py3.14; Kepler propagation run live; orekit-data NOT downloaded, so UTC/ITRF paths verified only as failing
verified_date: "2026-10-05"
---

# Orekit from Python (orekit-jpype)

Orekit (CS GROUP, Apache-2.0) is the production-grade Java space-dynamics library: orbits, frames, time scales
with leap seconds, analytical/numerical/TLE propagation, event detection (eclipses, station visibility),
maneuvers, orbit determination, many file formats. Latest release 13.1.9 (2026-10-03). Use it as a high-fidelity
reference or for operations-style problems; for quick delta-v estimates it is overkill (see the decision table in `SKILL.md`).

## Setup that works with pip only (verified)

No JDK or Maven is needed if you take the `jdk4py` extra, which ships a JDK inside a wheel.

```bash
pip install orekit-jpype jdk4py        # ~82MB incl. Orekit jars; PyPI name is orekit-jpype, plain `orekit` does not exist
```

```python
import os, jdk4py
os.environ["JAVA_HOME"] = str(jdk4py.JAVA_HOME)     # must be set before initVM
import orekit_jpype as orekit
orekit.initVM()                                      # 1.6 s here; vmargs="-Xmx2g" (comma-separated string) optional

from org.orekit.time import AbsoluteDate, TimeScalesFactory    # Java imports ONLY after initVM()
from org.orekit.frames import FramesFactory
from org.orekit.orbits import KeplerianOrbit, PositionAngleType
from org.orekit.propagation.analytical import KeplerianPropagator
from org.orekit.utils import Constants
```

Rules that bite:

- **Import Java classes after `initVM()`**; before it, `from org.orekit... import` fails because JPype does not know the packages yet.
- **The JVM cannot be restarted** in one process after `jpype.shutdownJVM()`. Start it once at program entry.
- With a JDK 25 runtime the JVM prints four `WARNING: A restricted method in java.lang.System has been called ... --enable-native-access=ALL-UNNAMED` lines on startup. Harmless; they come from JPype's `System::load`. Pass `vmargs="--enable-native-access=ALL-UNNAMED"` to silence them (not tested here).
- Classes come back as real Java types (`org.orekit.orbits.KeplerianOrbit`); unlike the older JCC wrapper no `.cast_()` is needed. Java interfaces are implemented as Python classes with a decorator; abstract Java classes cannot be subclassed from Python.
- `initVM(additional_classpaths=[...])` adds your own jars; `jvmpath=` points at a specific `libjvm`.

## Verified run: Kepler propagation needs no data files

```python
tai = TimeScalesFactory.getTAI()
eme = FramesFactory.getEME2000()
epoch = AbsoluteDate(2026, 10, 5, 0, 0, 0.0, tai)
orb = KeplerianOrbit(7000e3, 0.001, 0.9, 0.0, 0.0, 0.0, PositionAngleType.MEAN, eme, epoch, Constants.WGS84_EARTH_MU)
st = KeplerianPropagator(orb).propagate(epoch.shiftedBy(3600.0))
pv = st.getPVCoordinates(); p = pv.getPosition()      # metres, m/s (SI throughout, angles in radians)
orb.getKeplerianPeriod()                               # 5828.5166... s for a = 7000 km
```

Result for the case above: period 5828.516637686015 s, position after 3600 s `[-5183064.2, -2929381.9, -3691484.7]` m.
Orekit works in SI units and radians everywhere (constructor arguments are `a` in metres, angles in radians), the opposite of
SPICE's km. `shiftedBy(seconds)` returns a new date; objects are immutable.

## What fails without data

`TimeScalesFactory.getUTC()` and any ITRF transform raise
`org.orekit.errors.OrekitException: no IERS UTC-TAI history data loaded`. Verified. EME2000 and GCRF (`EME2000.getTransformTo(GCRF, date)`) worked with no data loaded, and TAI is available. So anything involving UTC dates, Earth rotation,
ground stations or EOP needs the data set.

Data options (not run here: they download from `gitlab.orekit.org`):

```python
from orekit_jpype.pyhelpers import download_orekit_data_curdir, setup_orekit_curdir, setup_orekit_data
download_orekit_data_curdir()        # fetches orekit-data.zip (main branch archive) into the CWD
setup_orekit_curdir()                # registers ./orekit-data.zip with the DataContext
# or: pip install git+https://gitlab.orekit.org/orekit/orekit-data.git ; setup_orekit_data(from_pip_library=True)
```

Pin the data version in the repo like any other kernel/EOP file: leap-second and EOP files age, and the `main` archive
changes over time, so a reproducible pipeline vendors one dated copy. Helpers `absolutedate_to_datetime` and
`datetime_to_absolutedate` convert to Python `datetime`; `np_to_JArray_double` moves NumPy arrays into Java.

## Choosing against the other tools

| Situation | Pick |
|---|---|
| Operational-style tasks: eclipse/visibility events, TLE propagation, orbit determination, many time scales, CCSDS formats | Orekit (Java; this note) |
| Planetary ephemerides, spacecraft/instrument geometry, NAIF kernels | SpiceyPy (`spiceypy-notes.md`) |
| One Python library with propagators and SBDB/Horizons/SPICE clients | brahe |
| High-fidelity cross-check with Rust performance (AGPL, reference only) | nyx |

Orekit is Apache-2.0, so unlike nyx it can be linked into shipped code. Cost of ownership is the JVM: startup time,
the 82MB install, and JPype's one-JVM-per-process limit.
