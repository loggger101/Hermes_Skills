---
description: "16 keyless live feeds from gods-eye-view's DATA_SOURCES.md requested once from this machine on 2026-10-05: status, size, latency, payload shape, rate limits and the dead CelesTrak txt path"
source_repo: bilawalsidhu/gods-eye-view (DATA_SOURCES.md read at main, 2026-10-05; the app itself was not run)
tested_version: "One GET per endpoint from Windows with Python urllib, identifying User-Agent, gzip accepted, 1.2 s apart, no API keys and no contact address sent. Results are a snapshot of that minute; shapes and limits are the useful part"
verified_date: "2026-10-05"
---

# Live open-data feeds for watchers

`gods-eye-view` (a Cesium 3D-globe OSINT viewer) documents about 60 live sources and, unusually, what each licence and rate
limit asks of clients. Its `DATA_SOURCES.md` is the catalogue. This note records which keyless feeds a polling script can
use today and what each returns. Use with `devops/watchers` (watermarks, dedup).

## Results (run, one request each)

| Feed | Status | Size / latency | Shape |
|---|---|---|---|
| USGS quakes `earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson` | 200 | 8 KB, 0.2 s | GeoJSON `features[]` with `properties.mag/place/time` (epoch ms) and `geometry.coordinates = [lon, lat, depth_km]` |
| CelesTrak GP `celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=json` | 200 | 9.7 KB, 0.6 s | JSON list of 23 objects, 17 keys each (`OBJECT_NAME`, `OBJECT_ID`, `EPOCH`, `MEAN_MOTION`, `ECCENTRICITY`, `INCLINATION` ...): OMM records, not TLE lines |
| CelesTrak legacy `celestrak.org/NORAD/elements/stations.txt` | **404** | | the old static TLE path is gone; use `gp.php` (the `FORMAT=tle` variant is CelesTrak-documented and was not requested here) |
| OpenSky `opensky-network.org/api/states/all?lamin=&lomin=&lamax=&lomax=` | 200 | 20.6 KB, 0.7 s | `{time, states[]}`, 162 vectors; each state is a **17-element positional array** (`[icao24, callsign (padded), country, time_position, last_contact, lon, lat, baro_alt, on_ground, ...]`). Header `X-Rate-Limit-Remaining: 398` (anonymous credits). Licence non-commercial |
| adsb.lol `api.adsb.lol/v2/point/<lat>/<lon>/<radius_nm>` | 200 | 42.7 KB, 0.6 s | `{ac[], now (ms), total, ctime, ptime, msg}`; each `ac` has `hex, flight, lat, lon, alt_baro, gs, r, ...` (about 26 keys, some optional). 78 aircraft within 50 nm of 47N 8E; the count moves between calls (67 a few seconds later) |
| adsbdb `api.adsbdb.com/v0/aircraft/<hex>` | 200 | 0.5 KB | `{response: {aircraft: {type, icao_type, manufacturer, registration, registered_owner, registered_owner_country_*, url_photo...}}}`. It returns the **registered owner**: treat as personal data when the owner is a private individual |
| Launch Library 2.3 `ll.thespacedevs.com/2.3.0/launches/upcoming/?limit=1&mode=list` | 200 | 1.3 KB, 0.2 s | `{count: 470, next, previous, results[]}` (`id, name, status, net, window_start, window_end, ...`). Anonymous limit per the catalogue: 15 calls/hour; no throttle headers were returned |
| Open-Meteo `api.open-meteo.com/v1/forecast?latitude=&longitude=&current=temperature_2m,...` | 200 | 0.4 KB, 0.6 s | `{latitude, longitude, current_units, current{...}}` (CC BY 4.0 attribution required) |
| NHC `www.nhc.noaa.gov/CurrentStorms.json` | 200 | 4.6 KB, 0.1 s | `{activeStorms[]}` with `id, name, classification, intensity, pressure, latitude, longitude, movementDir, movementSpeed, lastUpdate, publicAdvisory`. The list can be empty |
| TfL JamCams `api.tfl.gov.uk/Place/Type/JamCam` | 200 | **1.1 MB**, 0.3 s | JSON list of 890 places (`$type, id, url, commonName, placeType, additionalProperties`). TfL attribution required |
| Digitraffic weathercams `tie.digitraffic.fi/api/weathercam/v1/stations` (header `Digitraffic-User`) | 200 | 464 KB, 0.5 s | GeoJSON `features[]` (808 stations), `properties.presets[]` per camera, top-level `dataUpdatedTime`. CC BY 4.0 |
| Radio Browser `de1.api.radio-browser.info/json/stations/search?has_geo_info=true&limit=1` | 200 | 1.1 KB, 0.7 s | JSON list of station objects (`stationuuid, name, url_resolved, ...`). It is one of several mirrors; the catalogue says to discover mirrors |
| NOAA GFS bucket listing `noaa-gfs-bdp-pds.s3.amazonaws.com/?list-type=2&prefix=gfs.<date>/` | 200 | 0.4 KB, 0.2 s | anonymous S3 `ListBucketResult` XML; GRIB2 data are read by byte range |
| Photon `photon.komoot.io/api/?q=Tallinn&limit=1` | 200 | 0.4 KB, **5.0 s** | GeoJSON `features[]`; slow on this call (fair-use public instance) |
| GDELT DOC 2.0 `api.gdeltproject.org/api/v2/doc/doc?query=...&mode=artlist&format=json` | **429** | 10.8 s | body: "Please limit requests to one every 5 seconds"; add a client-side 5 s gap |
| NASA GIBS `gibs.earthdata.nasa.gov/wmts/epsg4326/best/1.0.0/WMTSCapabilities.xml` | **timeout** | >25 s | the capabilities document is very large; do not poll it, fetch it once and cache |

## Rules these results support

- **Respect the documented gaps**: GDELT one request per 5 s; Launch Library anonymous 15 per hour (cache for 15 minutes as the
  app does); OpenSky anonymous credits shrink per call (watch `X-Rate-Limit-Remaining`); Nominatim and Photon are fair-use,
  not bulk.
- **Identify the client**: Digitraffic asks for a `Digitraffic-User` header; others expect a descriptive User-Agent. Do not put
  a personal email in it unless the service documents that as the polite route.
- **Positional arrays break silently**: OpenSky states are untyped lists; map by index through a named tuple and assert the
  length (17 here).
- **Keep stale and empty distinct**: NHC returns an empty `activeStorms`, OpenSky/adsb.lol return whatever is in range; a
  watcher should record "no data" separately from "feed failed" (HTTP error, timeout, 429).
- **Large catalogues are fetch-once**: TfL (1.1 MB), Digitraffic (464 KB) and GIBS capabilities change rarely; cache them and
  poll only the frames or states.
- **Licences differ per feed** (OpenSky non-commercial; ODbL for adsb.lol/OSM; CC BY 4.0 for Open-Meteo and Digitraffic; TfL
  requires "Powered by TfL Open Data"; US government feeds are public domain). The catalogue lists them; keep attribution
  with the data.
- **Camera and aircraft-owner data can identify people.** The source repo relays frames as served and does not redact them; a
  pipeline of your own should not store frames or owner names beyond what the task needs.

Not run: the app, its server proxies, AISStream (needs a key), Google Map Tiles, TomTom, the other CCTV providers, GTFS-Realtime
transit feeds, NOAA nowCOAST WMS, ECMWF open data, local RTL-SDR input, or any of its 460 KB `CURRENT-STATE.md`.
