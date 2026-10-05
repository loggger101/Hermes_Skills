---
description: "astropy 8.0.1 traps run on Python 3.12: JD defaults to UTC (TT differs 69.184 s), string offsets rejected, Time+float assumes days, AltAz without location gives an AttributeError, jplephem absent, IERS auto-download defaults"
source_repo: astropy/astropy (BSD-3-Clause)
tested_version: "astropy 8.0.1 + numpy 2.5.3 in a uv Python 3.12 venv on Windows 11 (two scripts, about 45 calls, warnings forced on). The repo already uses astropy as the truth oracle in hifitime-time-scales.md and spacekit-notes.md. No remote catalogue (SIMBAD/astroquery), FITS image, WCS or cosmology work was exercised"
verified_date: "2026-10-05"
---

# astropy 8.0.1 (time, units, coordinates, tables): measured traps

Companions: `hifitime-time-scales.md` (astropy as truth for TAI/TT/TDB), `skyfield-api-reference.md`.

## Time

| Call | Result |
|---|---|
| `Time(2451545.0, format='jd')` | **scale is UTC**. A Julian date taken from an ephemeris table is usually TT or TDB; `Time(2461318.5, format='jd', scale='tt') - Time(2461318.5, format='jd')` is **-69.184 s**. Always pass `scale=` for numeric JD/MJD |
| `Time('2000-01-01 12:00:00')`, `Time.now()` | scale `utc` |
| `Time('2016-12-31T23:59:60')` | accepted; `.tai` = `2017-01-01T00:00:36.000`. `Time('2017-01-01') - Time('2016-12-31')` = **86 401 s** (the leap day) |
| `Time('2026-10-05', scale='tt') - Time('2026-10-05', scale='utc')` | -69.184 s (the same calendar label is a different instant) |
| `.jd` / `.mjd` | expressed in the object's **own** scale: `Time(..., scale='tt').mjd - Time(..., scale='utc').mjd` was 0.0 for the same label; convert (`.utc`, `.tt`) first |
| `Time(datetime(2026,10,5,12, tzinfo=-04:00))` | `2026-10-05 16:00:00` (converted to UTC); a **naive** datetime is taken as UTC |
| `Time('2026-10-05T12:00:00+04:00')` | **ValueError** (string offsets not parsed): parse with `datetime.fromisoformat` and pass the aware datetime |
| `Time([Time(.., 'utc'), Time(.., 'tt')])` | returns scale `utc`: the elements are converted silently to the first one's scale |
| `Time('2026-10-05') + 1.0` | works but warns `TimeDeltaMissingUnitWarning ... assuming days`; write `+ 1*u.day` |
| `Time(... ) + 1e-12*u.day` | difference recovered as 86.398 ns (true 86.4): sub-ns precision is kept to about 2 ps |

### UT1 and IERS

- `iers.conf.auto_download` defaults to **True**, `iers_auto_url = https://datacenter.iers.org/data/9/finals2000A.all`,
  `auto_max_age = 30` days, `remote_timeout = 10` s. The first UT1-dependent operation (UT1, AltAz) may fetch from the network.
- `Time('2026-10-05').ut1` -> `2026-10-04 23:59:59.975`. `Time('2100-01-01').ut1` and `Time('2040-01-01').ut1` (even with
  `auto_download=False`) return a value with `ErfaWarning ... dubious year`, i.e. an extrapolation, not an error.
- AltAz at `obstime=2300-01-01` works with `AstropyWarning: Tried to get polar motions for times after IERS data is valid.
  Defaulting to polar motion from the 50-yr mean`. Treat results beyond the IERS table as approximate.
- Set `XDG_CACHE_HOME`/`ASTROPY_CONFIGDIR` deliberately: astropy warns when the cache dir is overridden and writes its
  downloaded tables there.

## Units and angles

| Call | Result |
|---|---|
| `1*u.deg + 1*u.rad` | `58.2958 deg` (left operand's unit wins) |
| `5*u.m + 5*u.s` | `UnitConversionError: Can only apply 'add' function to quantities with compatible dimensions` |
| `3*u.m == 3.0` | **False** (only dimensionless compares to a bare float) |
| `(6*u.hourangle).to(u.deg)` | `89.99999999999999 deg` (float round-off: use `np.isclose`) |
| `Angle(370*u.deg).wrap_at(180*u.deg)` ; `Longitude(-10*u.deg)` | `10 deg` ; `350 deg` (longitudes wrap to 0-360) |
| `(20*u.deg_C).to(u.K)` | `UnitConversionError`; use `equivalencies=u.temperature()` -> `293.15 K` |
| `SkyCoord(ra=12.5, dec=45)` | `UnitTypeError: Longitude instances require units equivalent to 'rad', but no unit was given` |
| `const.G`, `const.c`, `const.M_sun` | 6.6743e-11, 299792458.0, 1.98841e30; reference string `CODATA 2022` |

## Coordinates

- `SkyCoord(...).transform_to(AltAz(obstime=t, location=loc))` works with an `EarthLocation` (a fixed star at NYC on
  2026-10-05 12:00 UTC gave alt 30.02, az 200.647).
- **`AltAz(obstime=t)` without `location`** fails with `AttributeError: 'NoneType' object has no attribute 'to_geodetic'`:
  the message does not say a location is missing.
- `get_body('mars', t)` uses `solar_system_ephemeris` = `builtin` (1.634 AU on 2026-10-05). `solar_system_ephemeris.set('jpl')`
  raises `ModuleNotFoundError: ... require the jplephem package`; install `jplephem` and expect a kernel download on first use.
- `separation` of the two poles = 180 deg exactly.

## Tables

- ECSV roundtrip preserves NaN and the string column (`<U1`), and keeps a masked integer column's mask (shown as `--`).
- FITS write of a table with a string column works; reading it back gives bytes-kind (`S`) strings.

## Habits

1. Name the scale on every numeric time; convert before reading `.jd`/`.mjd`.
2. Treat any UT1/AltAz result after the IERS table end as approximate and capture warnings in logs.
3. Pin offline behaviour for CI: `iers.conf.auto_download = False` and a pre-fetched table, or accept network calls.
4. Compare floats from unit conversions with tolerances.

Not run: `SkyCoord.from_name` (needs network), astroquery, WCS/FITS images, cosmology, modelling, `astropy.timeseries`.
