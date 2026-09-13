---
description: "All 230 keyless Hugging Face space/astro/physics mirrors from juliensimon/space-datasets — load_dataset one-liner, no API keys; grouped by domain"
source_repos: juliensimon/space-datasets README.md @ 5f886cd (catalog extracted programmatically this pass)
tested_version: clone @ 2026-09-12; NHATS mirror parquet endpoint re-probed LIVE same day (HTTP 200, real file list)
verified_date: "2026-09-12"
---

# Keyless Space Data Mirrors on Hugging Face (juliensimon/*)

**What this is:** ~230 space/astronomy/physics datasets published as Parquet+zstd to `huggingface.co/datasets/juliensimon/<name>`,
auto-refreshed daily by the upstream repo's GitHub Actions. **No API keys, no auth** — every dataset loads in one line:

```python
from datasets import load_dataset          # or just read the parquet directly with polars/duckdb/pandas
ds = load_dataset("juliensimon/<name>", split="train")
df = ds.to_pandas()
```

Parquet files live at `data/*.parquet` inside each repo; direct file URLs work too:
`https://huggingface.co/datasets/juliensimon/<name>/resolve/main/data/<file>.parquet`.
Verified 2026-09-12 (this machine): the HF parquet API endpoint for `nhats-accessible-asteroids` returns a real file list.

**Why this matters to the pipeline:** these are frozen, schema-stable snapshots of feeds that otherwise require per-body HTTP calls
(Asterank dv), dead endpoints (UCS), or authed sessions (Space-Track). A mirror is an *independent* copy — good for cross-checks and
backfills; but it lags the live feed by up to its update schedule, so treat row counts as "as of last refresh" (the repo's `status.json`
tracks per-dataset dates + `_rows`).

**Licensing caveat:** most are cc-by-4.0, but **~89 carry restrictive upstream terms** — see `space-data-licensing-audit.md` in this skill
(ESA mirrors = CC BY-NC 3.0 IGO; VizieR-sourced catalogs = scientific-use only). Check the per-dataset card before redistributing commercially.

## Catalog (224 datasets, alphabetical)

| HF dataset | What it is |
|---|---|
| `juliensimon/4xmm-dr14-xray-sources` | 630K+ unique X-ray sources from ESA XMM-Newton serendipitous survey (4XMM) |
| `juliensimon/aavso-vsx-variable-stars` | 1.5M+ variable stars from the AAVSO Variable Star Index (VSX) with types, periods, and magnitudes |
| `juliensimon/apogee-dr17` | APOGEE DR17 stellar parameters and abundances from high-resolution infrared spectroscopy |
| `juliensimon/artemis-ii` | Artemis II crewed lunar flyby: 1,285 trajectory vectors, crew manifest, mission timeline, payloads |
| `juliensimon/ast-spacemobile-fleet-data` | Daily AST SpaceMobile BlueBird + BlueWalker direct-to-cell constellation health |
| `juliensimon/asterank-asteroid-mining` | Mining economics for 400K+ asteroids: estimated value, profit, delta-v, and spectral types from Asterank |
| `juliensimon/asteroid-lightcurves-lcdb` | Rotation periods, lightcurve amplitudes, diameters, and taxonomies for 20K+ asteroids from LCDB |
| `juliensimon/astronaut-database` | Every person who has been to space — 560+ astronauts/cosmonauts |
| `juliensimon/astronomer-database` | 11K+ astronomers with affiliations, awards, and fields of work from Wikidata |
| `juliensimon/auger-cosmic-rays` | Ultra-high-energy cosmic ray events from Pierre Auger Observatory |
| `juliensimon/aurora-forecast` | Daily auroral activity index from NOAA SWPC OVATION nowcast — per-hemisphere integrated power, peak intensity, and oval extent |
| `juliensimon/auroral-electrojet-index` | Hourly AE/AU/AL/AO auroral electrojet indices from Kyoto WDC |
| `juliensimon/black-hole-catalog` | Known black hole systems and X-ray binaries from SIMBAD |
| `juliensimon/blue-origin-launches` | Complete Blue Origin launch manifest — New Shepard + New Glenn flights (past and upcoming) |
| `juliensimon/bright-star-catalog` | 9,110 naked-eye stars from the Bright Star Catalogue (BSC5, 5th Revised Edition) |
| `juliensimon/brown-dwarf-catalog` | 14K ultracool and brown dwarfs within 40 pc |
| `juliensimon/bus-demeo-asteroid-taxonomy` | Reference Bus-DeMeo spectroscopic taxonomy for 371 asteroids (24 classes, 0.45-2.45 um) |
| `juliensimon/carbon-stars` | 6,000+ Galactic carbon stars from the General Catalogue of Cool Carbon Stars (GCCS) |
| `juliensimon/cassini-saturn-observations` | 63K Saturn observation records from the Cassini mission (2004-2017) |
| `juliensimon/cataclysmic-variable-catalog` | 2,000+ cataclysmic variables — dwarf novae, polars, and classical novae |
| `juliensimon/cdaw-lasco-cme-catalog` | 42K+ coronal mass ejections from SOHO/LASCO since 1996 (NASA CDAW) — the canonical CME compilation |
| `juliensimon/celestrak-space-weather` | Consolidated space weather data for orbit propagation (Kp, Ap, F10.7) |
| `juliensimon/ceres-craters-dawn` | 44,594 impact craters on Ceres (>=1 km) from the Dawn Framing Camera |
| `juliensimon/chandra-x-ray-sources` | 28K X-ray sources from the Chandra Source Catalog (CSC 2.1) |
| `juliensimon/chime-frb-catalog` | 4,500+ fast radio bursts from the CHIME/FRB telescope |
| `juliensimon/cns5-nearby-stars` | Catalogue of Nearby Stars within 25 parsecs (CNS5) with astrometry and photometry |
| `juliensimon/comet-catalog` | 1,278 comets with orbital elements, discoverers, and discovery dates from Wikidata |
| `juliensimon/constellation-catalog` | 94 IAU constellations with abbreviations, areas, and brightest stars from Wikidata |
| `juliensimon/constellation-census` | 19 satellite constellations (Starlink, OneWeb, Kuiper, GPS, etc.) — 11K+ satellites |
| `juliensimon/constellation-tle-latest` | Daily TLE snapshots for 18 constellations: GNSS, OneWeb, Iridium, Planet, SES, Intelsat, and more |
| `juliensimon/cosmic-void-catalog` | 1,000+ cosmic voids from SDSS DR7 (Pan et al. 2012) |
| `juliensimon/cosmicflows-galaxy-distances` | 56K galaxy distances from Cosmicflows-4 (8 distance methods) |
| `juliensimon/crdb-cosmic-ray-spectra` | 316K cosmic ray measurements from 131 experiments |
| `juliensimon/deep-space-missions-tracker` | Daily positions of 9 active deep-space missions (Voyagers, New Horizons, Juno, Lucy, Psyche, Europa Clipper, OSIRIS-APEX, JUICE) — Sun/Earth distance, sky posit |
| `juliensimon/deep-space-probes` | 1.2M hourly readings from Voyager 1+2 and Pioneer 10+11 (1972-2025) |
| `juliensimon/desi-dr1-redshifts` | 1M+ spectroscopic redshifts from the DESI Data Release 1 Bright Galaxy Survey |
| `juliensimon/donki-space-weather-events` | 12K+ coronal mass ejections, geomagnetic storms, and solar particle events (2010+) |
| `juliensimon/dst-index` | 600K+ hourly geomagnetic storm intensity readings since 1957 (Dst index) |
| `juliensimon/erosita-erass1-xray` | 900K X-ray sources from the first eROSITA All-Sky Survey (eRASS1) |
| `juliensimon/esa-bepicolombo-observations` | 176K+ observation records from ESA/JAXA BepiColombo Mercury mission (11 instruments, cruise + flybys) |
| `juliensimon/esa-exomars-tgo-observations` | 27M+ observation records from ESA ExoMars TGO (4 instruments, since 2018) |
| `juliensimon/esa-huygens-titan-descent` | 14K+ observation metadata from ESA Huygens Titan descent (8 instruments, 2005) |
| `juliensimon/esa-juice-observations` | 6K+ observation records from ESA JUICE Jupiter mission (cruise phase, growing) |
| `juliensimon/esa-mars-express-observations` | 1.66M observation metadata from ESA Mars Express (8 instruments, since 2003) |
| `juliensimon/esa-rosetta-observations` | 14M+ observation records from ESA Rosetta at comet 67P (15 instruments incl. Philae) |
| `juliensimon/esa-venus-express-observations` | 525K observation metadata from ESA Venus Express (5 instruments, 2006-2014) |
| `juliensimon/euve-observations` | 1,367 EUVE extreme-UV observations (1992–2001) — the only EUV space mission ever flown (70–760 Å) |
| `juliensimon/f107-solar-flux` | Daily F10.7 cm solar radio flux since 1947 — primary proxy for atmospheric drag |
| `juliensimon/fcc-ngso-filings` | FCC IBFS filings for major NGSO constellations — requested satellite counts, shells, status |
| `juliensimon/feng-icme-catalog` | 219 ACE/WIND in-situ ICMEs 1998-2011 with shock arrival, body duration, and magnetic-cloud flag (Feng+ 2018) |
| `juliensimon/fermi-3fhl-hard-gamma-ray` | 1,558 hard gamma-ray sources (>10 GeV) from Fermi LAT 3FHL |
| `juliensimon/fermi-3pc-gamma-ray-pulsars` | 7K+ gamma-ray pulsars from Fermi LAT Third Pulsar Catalog (3PC) |
| `juliensimon/fermi-4fgl-dr4` | 7K gamma-ray sources from Fermi LAT 14-year all-sky survey |
| `juliensimon/fermi-4lac-agn-catalog` | 3,407 gamma-ray AGN from Fermi LAT Fourth AGN Catalog (4LAC) |
| `juliensimon/fermi-gbm-triggers` | 12.5K+ Fermi GBM triggers — all triggers, not just confirmed GRBs |
| `juliensimon/fireball-bolide-events` | Fireball and bolide atmospheric impact events detected by US government sensors |
| `juliensimon/first-radio-catalog` | 946K radio sources from the VLA FIRST Survey at 1.4 GHz (5" resolution) |
| `juliensimon/forbush-decreases` | 7,097 Forbush decrease events (1957-2016) with solar wind, IMF, and CME parameters from IZMIRAN |
| `juliensimon/fuse-observations` | 5,729 FUSE far-UV spectra (1999–2007) — highest-resolution 905–1187 Å spectrograph ever flown |
| `juliensimon/gaia-dr3-binary-masses` | 195K binary star component masses (m1, m2) from Gaia DR3 astrometric+spectroscopic solutions |
| `juliensimon/gaia-dr3-cepheids` | Gaia DR3 Cepheid variable stars with pulsation periods, multi-band photometry, and parallaxes |
| `juliensimon/gaia-dr3-chemical-cartography` | 5.6M stars with Galactic orbital actions, kinematics, and energy from Gaia DR3 |
| `juliensimon/gaia-dr3-compact-companions` | 6K candidates for stars orbiting compact objects (black holes/neutron stars) identified via Gaia DR3 ellipsoidal variability |
| `juliensimon/gaia-dr3-eclipsing-binaries` | Gaia DR3 eclipsing binary candidates with orbital periods and light-curve parameters |
| `juliensimon/gaia-dr3-long-period-variables` | 1.7M Mira and semi-regular variable stars (LPVs) from Gaia DR3 including carbon star classification |
| `juliensimon/gaia-dr3-qso-candidates` | 6.6M quasar/AGN candidates with DSC classifier probabilities and photometric redshifts from Gaia DR3 |
| `juliensimon/gaia-dr3-rotation-modulation` | 84K stellar rotation periods from Gaia DR3 photometric modulation with starspot activity indices |
| `juliensimon/gaia-dr3-rrlyrae` | 272K RR Lyrae pulsating stars from Gaia DR3 — distance ladder |
| `juliensimon/gaia-dr3-solar-system-objects` | 158K solar system objects (asteroids, comets) observed by Gaia DR3 with minor planet numbers and spectra counts |
| `juliensimon/gaia-dr3-spectroscopic-binaries` | 180K+ spectroscopic binary star orbital solutions (SB1+SB2) from Gaia DR3 |
| `juliensimon/gaia-dr3-white-dwarfs` | 359K white dwarf candidates with atmospheric parameters and masses from Gaia DR3 |
| `juliensimon/gaia-dr3-young-stellar-objects` | 79K+ young stellar object (YSO) candidates with classification scores and variability from Gaia DR3 |
| `juliensimon/galactic-novae-schaefer` | 402 Galactic classical novae with peak V magnitudes, reddening, and distance moduli (Schaefer 2022) |
| `juliensimon/galah-dr4-stellar-abundances` | GALAH DR4 radial velocities, stellar parameters, and elemental abundances for 917K stars |
| `juliensimon/galaxy-clusters` | 1,650+ galaxy clusters detected by Planck via the Sunyaev-Zeldovich effect |
| `juliensimon/galaxy-zoo-2-morphology` | 243K citizen-science galaxy morphology classifications with vote fractions and debiased probabilities |
| `juliensimon/galex-observations` | 275K GALEX UV survey observations (2003–2013) tagged with survey type (AIS, MIS, DIS, NGS, etc.) |
| `juliensimon/galileo-jupiter-atmosphere` | Jupiter atmospheric profile from Galileo Probe descent (1995) — temperature, pressure, density to 24 bar |
| `juliensimon/gamma-ray-bursts` | 4,200+ gamma-ray bursts from Fermi GBM with duration, flux, and spectral data |
| `juliensimon/gcat-deep-space` | 1,206 deep space objects and 469 planetary landings from GCAT |
| `juliensimon/gcat-launch-vehicles` | 4,875 launch vehicles, engines, and stages from GCAT |
| `juliensimon/gcat-satellite-catalog` | 68K+ satellites, rocket bodies, and debris from GCAT (Jonathan McDowell) |
| `juliensimon/gcvs-variable-stars` | 58K variable stars from the General Catalogue of Variable Stars |
| `juliensimon/geneva-copenhagen-stellar-survey` | 16,682 F and G dwarf stars in the solar neighbourhood with ages, metallicities, and kinematics |
| `juliensimon/geomagnetic-kp-index` | 3-hourly geomagnetic disturbance index (Kp 0-9) with NOAA storm scale |
| `juliensimon/global-meteor-network` | 3M+ individual meteor trajectories with orbits, velocities, and shower IDs from 500+ all-sky cameras worldwide (GMN) |
| `juliensimon/globalstar-fleet-data` | Daily Globalstar constellation health — per-generation satellite counts and status (Amazon-owned as of 2026) |
| `juliensimon/globular-star-clusters` | 167 Milky Way globular clusters with masses, structural parameters, and metallicities |
| `juliensimon/goes-xray-flux` | 1-minute GOES solar X-ray flux (both bands) with A/B/C/M/X flare classification from NOAA SWPC |
| `juliensimon/gravitational-lenses` | 33K strong gravitational lenses from the lenscat community catalog |
| `juliensimon/gravitational-wave-events` | 260+ black hole and neutron star mergers detected by LIGO/Virgo/KAGRA |
| `juliensimon/grbweb-unified-grb-catalog` | Unified GRB catalog from GRBweb combining Fermi, Swift, BATSE, BeppoSAX, and IPN detectors |
| `juliensimon/gswlc-galaxy-properties` | 659K galaxies with stellar masses, star formation rates, and dust attenuation from GALEX-SDSS-WISE |
| `juliensimon/hawc-tev-gamma-ray` | 65 TeV gamma-ray sources from the 3HWC HAWC catalog |
| `juliensimon/hecate-nearby-galaxies` | HECATE catalog of nearby galaxies within 200 Mpc with stellar masses, SFR, and morphology |
| `juliensimon/henry-draper-catalog` | 272K stars with MK spectral classifications — the foundational Henry Draper Catalogue (Cannon, 1918–1924) |
| `juliensimon/hipparcos-catalog` | 118K brightest stars with precise positions and parallaxes from ESA Hipparcos |
| `juliensimon/hot-subdwarf-stars` | 1,714 spectroscopically identified hot subdwarf (sdB/sdO) stars from Kilkenny+ III/137 |
| `juliensimon/hst-observations` | 2.6M+ Hubble Space Telescope observations (1990–present) — target, proposal, instrument, detector metadata from MAST |
| `juliensimon/huygens-titan-atmosphere` | Titan atmospheric profile from Huygens Probe descent (2005) — 1,400 km to surface |
| `juliensimon/hypervelocity-stars-li2023` | 52 hypervelocity star candidates with 6D phase-space and 5 Galactic-potential unbound probabilities (Li+ 2023) |
| `juliensimon/iau-meteor-showers` | 2,163 meteor shower records from the IAU Meteor Data Center |
| `juliensimon/icecat-neutrino-alerts` | High-energy neutrino alert events from the IceCube Neutrino Observatory (ICECAT-1) |
| `juliensimon/icecube-neutrino-catalog` | IceCube neutrino point sources from HEASARC |
| `juliensimon/icrf3-reference-frame` | 3,417 ICRF3 extragalactic radio sources — THE celestial reference frame |
| `juliensimon/iers-earth-orientation` | Daily Earth orientation parameters (polar motion, UT1-UTC, LOD) since 1973 |
| `juliensimon/impact-craters` | 4K+ impact craters across the solar system (Earth, Moon, Mars, etc.) from Wikidata |
| `juliensimon/insight-marsquake-catalog` | 2,715 marsquakes detected by InSight SEIS seismometer (2019-2022, final catalog) |
| `juliensimon/integral-ibis-hard-xray` | 929 hard X-ray sources from INTEGRAL IBIS 17-year survey (17-290 keV) |
| `juliensimon/iras-faint-source-catalog` | 173K mid-infrared sources (12/25/60/100 μm) from IRAS Faint Source Catalog v2.0 — first sensitive all-sky mid-IR survey |
| `juliensimon/isro-missions` | ISRO spacecraft, launchers, customer satellites, and research centres |
| `juliensimon/iue-observations` | 102K IUE UV spectra (1978–1996) — the longest-running UV space observatory, from SWP, LWP, LWR cameras |
| `juliensimon/jpl-small-body-database` | 1.4M+ asteroids and comets with orbital elements and physical parameters |
| `juliensimon/jwst-observations` | 960K+ JWST observations from MAST — proposal, target, instrument, timing, and wavelength metadata |
| `juliensimon/k2-observations` | 765K K2 extended-mission observations (2014–2018, campaigns C0–C19) with parsed EPIC ID, campaign, and cadence |
| `juliensimon/kepler-eclipsing-binaries` | 2,177 Kepler eclipsing binary stars |
| `juliensimon/kepler-observations` | 213K Kepler prime-mission observations (2009–2013) with KIC ID, cadence, and per-quarter observation mask |
| `juliensimon/kepler-transit-timing` | 295K transit times for 2,599 KOIs with O-C residuals, durations, and depths (Holczer+ 2016) |
| `juliensimon/kuiper-fleet-data` | Daily Amazon Project Kuiper constellation health — per-shell satellite counts and status |
| `juliensimon/launch-cost-to-leo` | Historical and current launch vehicle costs per kilogram to low Earth orbit (LEO) |
| `juliensimon/launch-vehicles` | 230+ orbital launch vehicles with specs and payload capacity from Wikidata |
| `juliensimon/lhaaso-gamma-ray-sources` | 180 ultra-high-energy gamma-ray sources from 1LHAASO (2024) |
| `juliensimon/lunar-craters-robbins` | 1.3M+ lunar impact craters from the Robbins 2019 database |
| `juliensimon/lunar-eclipse-catalog` | 12,064 lunar eclipses spanning 5 millennia (-1999 to +3000) from NASA — companion to solar-eclipse-catalog |
| `juliensimon/lunar-sample-geochemistry` | 58K geochemical analyses of Apollo/Luna/Chang'e 5 lunar samples (Astromat) |
| `juliensimon/mars-chemcam-compositions` | 30K+ Mars rock/soil oxide compositions from Curiosity ChemCam LIBS |
| `juliensimon/mars-craters-robbins` | 384K+ Mars impact craters from the Robbins & Hynek 2012 database |
| `juliensimon/mars-perseverance-weather` | Mars surface weather from Perseverance MEDA (temperature, pressure, wind, UV) |
| `juliensimon/maxi-xray-sources` | 170 persistent X-ray sources from the JAXA MAXI all-sky monitor on the ISS (2009+) |
| `juliensimon/mcgill-magnetar-catalog` | All known magnetars with spin parameters, magnetic field strengths, and X-ray properties |
| `juliensimon/mercury-crater-degradation` | 3,253 Mercury craters with degradation classification (Kinczyk et al. 2020) |
| `juliensimon/mercury-craters-herrick` | 16,876 Mercury impact craters from MESSENGER imagery (Herrick et al. 2011) |
| `juliensimon/messier-catalog` | The classic Messier catalog — 110 galaxies, nebulae, and star clusters |
| `juliensimon/meteorite-database` | 1,200+ named meteorites with classification, mass, and fall location from Wikidata |
| `juliensimon/meteorite-landings` | 45K+ known meteorite landings with classification and mass |
| `juliensimon/milliquas` | Milliquas v8 — the Million Quasars Catalog with positions, redshifts, and radio/X-ray associations |
| `juliensimon/mpc-comet-elements` | Orbital elements for all known comets from the Minor Planet Center |
| `juliensimon/nasa-apod` | 11K+ NASA Astronomy Picture of the Day entries since 1995 — images, videos, and ~2M words of expert astronomy prose |
| `juliensimon/nasa-eva-chronology` | 375 spacewalks (EVAs) — complete history from Gemini to ISS |
| `juliensimon/nasa-exoplanets` | 6,150 confirmed exoplanets with orbital, stellar, and discovery parameters |
| `juliensimon/nasa-mars-rover-images` | 400K+ image metadata from Perseverance and Curiosity rovers (sol, camera, position, URLs) |
| `juliensimon/nasa-maven-kp-insitu` | MAVEN Mars atmosphere key parameters: solar wind, magnetic field, ion composition at 4-8s cadence |
| `juliensimon/nebula-catalog` | 60K+ nebulae (emission, reflection, dark, planetary) with coordinates and distances from Wikidata |
| `juliensimon/neo-close-approaches` | 35K+ near-Earth asteroid and comet close approaches from NASA JPL |
| `juliensimon/neowise-asteroid-properties` | Diameters, albedos, and beaming parameters for 100K+ asteroids from WISE/NEOWISE |
| `juliensimon/nesvorny-asteroid-families` | 150K+ asteroids grouped into dynamical families by hierarchical clustering (Nesvorny et al.) |
| `juliensimon/neutron-monitor-cosmic-rays` | Hourly cosmic ray intensity from the global neutron monitor network |
| `juliensimon/ngc-ic-catalog` | 14K deep-sky objects — galaxies, nebulae, and star clusters (NGC + IC) |
| `juliensimon/nhats-accessible-asteroids` | 4,800+ asteroids accessible for human space missions with delta-v requirements |
| `juliensimon/nicer-observations` | 63K NICER X-ray timing observations from the ISS instrument — every pointing since 2018 |
| `juliensimon/nvss-radio-catalog` | 1.77M radio sources from the NRAO VLA Sky Survey at 1.4 GHz |
| `juliensimon/observatory-database` | 640+ ground and space observatories with locations, apertures, and wavelengths from Wikidata |
| `juliensimon/omni-solar-wind-parameters` | 561K+ hourly solar wind parameters (velocity, density, IMF) from NASA OMNI |
| `juliensimon/oneweb-fleet-data` | Daily OneWeb (Eutelsat) constellation health — per-plane satellite counts at ~1,200 km |
| `juliensimon/open-star-clusters` | 7,167 Gaia-era open star clusters with distances and ages |
| `juliensimon/open-supernova-catalog` | 72K supernovae with light curves, spectra references, and host galaxies |
| `juliensimon/orbital-fragmentation-events` | Catalog of orbital fragmentation events (breakups, explosions, collisions) from NORAD SATCAT |
| `juliensimon/otter-tde-catalog` | Tidal disruption events (TDEs) from the Open TDE Catalog — stars torn apart by black holes |
| `juliensimon/pantheon-plus-sne-ia` | 1,550 Type Ia supernovae — gold standard cosmological distance dataset |
| `juliensimon/parker-solar-probe-encounters` | 24 PSP perihelion encounters + 7 Venus gravity assists across 7 mission phases |
| `juliensimon/pdg-particle-properties` | Every known particle from the Particle Data Group |
| `juliensimon/pds-planetary-missions` | NASA PDS mission catalog — 98 missions, 115 spacecraft, 748 instruments with targets and cross-references |
| `juliensimon/physics-nobel-laureates` | 229 Physics Nobel Prize laureates with institutions and cited work from Wikidata |
| `juliensimon/planck-cold-clumps` | 13K+ Galactic cold clumps — pre-stellar cores and star-forming regions from Planck |
| `juliensimon/planck-sz2-clusters` | 1,650+ galaxy clusters from Planck SZ2 catalog with mass and redshift |
| `juliensimon/planetary-nebulae` | 1,715 planetary nebulae from MUSE survey |
| `juliensimon/planetary-nomenclature` | 15K+ IAU-approved named features on Moon, Mars, Venus, and Mercury |
| `juliensimon/pluto-atmosphere` | Pluto atmospheric profiles (temperature, pressure, composition, haze) from New Horizons |
| `juliensimon/pulsar-catalog` | 4,300+ pulsars with spin period, dispersion measure, and magnetic field |
| `juliensimon/pulsar-glitch-catalog` | 700+ pulsar glitch events from the Jodrell Bank Glitch Catalogue |
| `juliensimon/quasar-catalog` | 50K quasars, Seyfert galaxies, blazars, and active galactic nuclei |
| `juliensimon/rave-dr6` | RAVE DR6 stellar radial velocities, parameters, and elemental abundances for 518K spectra |
| `juliensimon/rc3-galaxy-morphology` | 23K bright galaxies with Hubble morphological types from RC3 |
| `juliensimon/reentry-events` | 35K satellite and debris reentry events with decay dates and locations |
| `juliensimon/rocket-lab-launches` | Complete Rocket Lab launch manifest — Electron + Neutron flights (past and upcoming) |
| `juliensimon/roma-bzcat-blazars` | 3,561 confirmed blazars (BL Lac + FSRQ) from Roma-BZCAT 5th edition |
| `juliensimon/rosat-bright-source-catalog` | 18,806 soft X-ray sources (0.1–2.4 keV) from the ROSAT All-Sky Survey Bright Source Catalogue (1RXS) |
| `juliensimon/satellite-conjunctions` | CelesTrak SOCRATES near-miss log — predicted satellite close approaches (<=1 km or Pc >=1e-4) with time, miss distance, and collision probability |
| `juliensimon/satnogs-transmitters` | 10K+ satellite radio transmitters and frequencies from SatNOGS |
| `juliensimon/sdss-asteroid-taxonomy` | Compositional taxonomy for 50K+ SDSS observations of asteroids with ugriz reflectances |
| `juliensimon/sentry-impact-risk` | Near-Earth objects with non-zero Earth impact probability |
| `juliensimon/silso-sunspot-number` | 120K+ daily sunspot numbers since 1818 from SILSO/Royal Observatory of Belgium |
| `juliensimon/solar-eclipse-catalog` | 12,000+ solar eclipses spanning 5 millennia (-1999 to +3000) from NASA |
| `juliensimon/solar-flare-events` | 16K+ individual solar flare detections from GOES X-ray sensors (2017+) |
| `juliensimon/solar-orbiter-encounters` | 13 Solar Orbiter perihelia + 5 Venus + 1 Earth gravity assists, ramping to 17°+ heliographic latitude |
| `juliensimon/solar-proton-events` | Solar proton events (SPEs) affecting the Earth environment from 1976 to present |
| `juliensimon/solar-radio-bursts` | Solar radio burst events (Type II/III/IV/V) from HEASARC |
| `juliensimon/solar-system-moons` | All 200+ known natural satellites of planets and dwarf planets with orbital and physical parameters |
| `juliensimon/solar-wind` | Real-time solar wind speed, density, temperature, and magnetic field from L1 |
| `juliensimon/space-agency-database` | Space agencies and governmental space organizations worldwide |
| `juliensimon/space-launch-log` | Every orbital and suborbital launch since 1957 with sites and outcomes |
| `juliensimon/space-missions` | 24K+ crewed and uncrewed space missions from Wikidata |
| `juliensimon/space-tourism-flights` | Commercial spaceflight passengers — 85 seats across Virgin Galactic, Blue Origin, SpaceX, Axiom, and Space Adventures (2001–) |
| `juliensimon/space-track-satcat` | Complete NORAD satellite catalog — 68K satellites, rocket bodies, and debris |
| `juliensimon/space-track-tle-history` | 238 million orbital element sets for every cataloged object since 1959 |
| `juliensimon/space-weather-indices` | Daily Kp, Ap, F10.7 solar and geomagnetic indices since 1957 |
| `juliensimon/spacecraft-database` | 8K+ spacecraft with operators, manufacturers, and orbits from Wikidata |
| `juliensimon/spacex-launches` | 659 SpaceX missions with timelines, descriptions, and carousel photos from spacex.com |
| `juliensimon/ssodnet-asteroid-properties` | Physical properties for 500K+ asteroids (diameters, albedos, taxonomy, masses) from IMCCE SsODNet |
| `juliensimon/stackexchange-space-qa` | 33K Q&A pairs from Astronomy + Space Exploration Stack Exchange sites — top-scored/accepted answers, CC-BY-SA 4.0 |
| `juliensimon/starlink-fleet-data` | Daily Starlink constellation health — per-shell satellite counts and status |
| `juliensimon/starlink-ground-stations` | Starlink gateway and point-of-presence locations worldwide |
| `juliensimon/starlink-tle-latest` | Latest Starlink + GPS TLEs in raw and Parquet format |
| `juliensimon/substorm-onsets` | 253K+ magnetospheric substorm onsets from 5 detection algorithms (SuperMAG) |
| `juliensimon/sumss-radio-catalog` | 211K southern radio sources at 843 MHz from SUMSS |
| `juliensimon/supernova-remnants` | 310 Galactic supernova remnants with radio flux and spectral index |
| `juliensimon/swift-bat-hard-xray-survey` | 1,891 hard X-ray sources (14-195 keV) from Swift-BAT 157-month survey |
| `juliensimon/swpc-alerts` | Official NOAA space weather alerts, watches, and warnings |
| `juliensimon/symbiotic-stars-catalog` | 218 confirmed + suspected symbiotic stars — interacting WD + red-giant binaries (Belczynski 2000) |
| `juliensimon/tess-toi-candidates` | 7K+ TESS Objects of Interest — active exoplanet candidates |
| `juliensimon/tevcat-tev-gamma-ray` | 322 TeV gamma-ray sources — THE ground-based VHE reference catalog |
| `juliensimon/tgss-radio-catalog` | 624K radio sources at 150 MHz from GMRT TGSS ADR1 |
| `juliensimon/tno-centaur-properties` | 652 TNO/Centaur physical properties (diameter, albedo, density) from PDS |
| `juliensimon/ucs-satellite-database` | 7,500+ active satellites with purpose, operator, and orbit metadata |
| `juliensimon/ula-launches` | Complete United Launch Alliance manifest — Atlas V, Delta, Vulcan Centaur flights |
| `juliensimon/unified-radio-catalog` | SPECFIND v3 unified radio source catalog cross-matching 50+ radio surveys |
| `juliensimon/veron-agn-quasar-catalog` | 169K quasars and AGN from Veron-Cetty & Veron 13th edition — canonical reference compilation |
| `juliensimon/vlass-radio-sources` | 3.4M radio sources from VLA Sky Survey Epoch 1 (VLASS) at 3 GHz |
| `juliensimon/wds-double-stars` | 157K visual double star systems from the Washington Double Star Catalog |
| `juliensimon/wise-hii-regions` | 8,000+ Galactic HII regions from WISE mid-infrared survey (Anderson+ 2014) |
| `juliensimon/wmo-oscar-satellites` | 1,025 Earth-observing satellites and 1,230 instruments from WMO OSCAR |
| `juliensimon/wolf-rayet-stars` | 383 Galactic Wolf-Rayet stars with Gaia DR2 distances and spectral types |
| `juliensimon/xray-binary-catalog` | 500+ high-mass and low-mass X-ray binaries (Liu et al. 2006/2007) |
| `juliensimon/yarkovsky-nea-drifts` | 247 Near-Earth Asteroids with direct Yarkovsky semimajor-axis drift measurements (Greenberg+ 2020) |

## Top downloaders (2026-09-12, from the repo README)

wmo-oscar-satellites · esa-rosetta-observations · esa-exomars-tgo-observations · space-track-tle-history · gaia-dr3-eclipsing-binaries / white-dwarfs / rrlyrae / cepheids / young-stellar-objects / spectroscopic-binaries — i.e. the ESA planetary-science observation tables and Gaia DR3 stellar subsets are by far the most reused; expect those to be the stable ones long-term.

## Update cadence (repo-level)

~50 datasets daily, ~20 weekly, rest static snapshots. The upstream repo's `status.json` holds per-dataset last-update dates + row counts
(153 tracked at this clone). Schedules are staggered across 06:00–19:30 UTC; a watchdog workflow runs at 21:00 UTC to retry/escalate stragglers.

## Notable for the economicspace pipeline specifically

- `nhats-accessible-asteroids` — population-scale Δv oracle mirror (see skill `economicspace-pipeline`).
- `asterank-asteroid-mining` — 50-col snapshot, NO dv column (dv is targeted-query-only on the live API; see SKILL.md).
- `jpl-small-body-database`, `neo-close-approaches`, `sentry-impact-risk`, `nesvorny-asteroid-families`, `bus-demeo-asteroid-taxonomy`, `sdss-asteroid-taxonomy`, `launch-cost-to-leo` — the soft-assumption sources tabulated in `economicspace-pipeline/references/dv-oracles-and-economics-sources.md`.
