---
description: "Finding free public APIs with the public-api-lists JSON feed (837 entries, 48 categories): schema, how to query it, measured link health, and metadata errors found (NASA auth, redirected Launch Library)"
source_repo: public-api-lists/public-api-lists (curated list; JSON at public-api-lists.github.io/public-api-lists/api/all.json)
tested_version: JSON fetched and analysed 2026-10-05 (HTTP 200, 221,269 bytes); 40 random landing pages and 6 specific endpoints requested with GET; list repo not cloned
verified_date: "2026-10-05"
---

# Discovering public APIs (and not trusting the metadata blindly)

`public-api-lists` is a hand-curated catalogue of free APIs with a **machine-readable feed**, which makes it usable by an agent that needs "an API for X".

```python
import json, urllib.request
req = urllib.request.Request("https://public-api-lists.github.io/public-api-lists/api/all.json", headers={"User-Agent": "my-agent/1.0"})
data = json.loads(urllib.request.urlopen(req, timeout=30).read())
entries = data["entries"]          # list of {name, url, description, auth, https, cors, category}
```

## What is in the feed (measured)

- `count` 837 and 837 entries (the README text says "730+": the feed is the source of truth), **48 categories**, no duplicate names, no empty descriptions.
- Fields: `name`, `url`, `description`, `auth` (`No` 397, `apiKey` 359, `OAuth` 77, `X-Mashape-Key` 4), `https` (true for all but 60), `cors` (`Unknown` 494, `Yes` 291, `No` 52), `category`.
- Biggest categories: Development 91, Geocoding 63, Games & Comics 47, Government 41, Transportation 39, Cryptocurrency 34, Finance 32, Social 26. Space and science sit under **Science & Math** (arcsecond.io, GBIF, ITIS, Launch Library, Minor Planet Center, NASA, Open Notify, Open Science Framework, ...), plus Weather, Open Data and Government.
- `cors: Unknown` for 59% of entries: do not assume browser calls work; proxy server-side.

Filter pattern: `[e for e in entries if e["category"] == "Science & Math" and e["auth"] == "No" and e["https"]]`.

## Health and accuracy of the metadata

- **Landing-page health sample** (40 random entries, GET of each `url`): 36 returned 2xx, 3 failed to connect (URLError), 1 returned 429. About 90% alive, so roughly one in ten entries is dead or flaky; always probe before depending on one.
- **`auth` can be wrong.** The NASA entry says `auth: No`, but `GET https://api.nasa.gov/planetary/apod` returned **403** and the same call with `?api_key=DEMO_KEY` returned 200 (DEMO_KEY is rate-limited; register a key for real use).
- **`url` is often a docs page, not the API base**, and can be stale: the "Launch Library" entry points to `launchlibrary.net/docs/1.3/api.html`, which now redirects to `thespacedevs.com`; the working endpoint family is `https://ll.thespacedevs.com/2.2.0/launch/upcoming/?limit=1` (200).
  The "Minor Planet Center" entry points to `http://www.asterank.com/mpc` (an Asterank page, plain http), not the MPC itself. Open Notify (`http://api.open-notify.org/astros.json`) answered 200 over plain http.
- A 200 on a landing page does not prove the API works: call a real endpoint and check the payload shape.

## Procedure for an agent

1. Pull the feed, filter by `category`/`auth`/`https`, and shortlist 3-5 candidates.
2. For each, read its docs for the real base URL, rate limits and terms; probe one endpoint; record the date and response shape.
3. Prefer `auth: No` and HTTPS; keep keys in environment variables (never in code); put a User-Agent on every request and honour 429s with backoff (see `ssrf-guard-and-outbound-http-hardening.md` for outbound-request safety).
4. Cache responses and record provenance (URL, retrieval time, licence). Free APIs change terms or die without notice; keep a fallback or a local snapshot for anything a pipeline depends on.
5. For space and astronomy data specifically see `data-science/space-data-pipelines` (data.gov, Asterank, HF mirrors) before picking a random free API.
