---
description: "catalog.data.gov search API as of 2026-10-05: the CKAN /api/3/action endpoints are gone (404); /search + /api/* replace them. Parameters, pagination, response shape, traps. Live-probed."
source_repo: GSA/data.gov (platform hub) -> GSA/datagov-catalog (Flask/OpenSearch app)
tested_version: live GET requests to https://catalog.data.gov on 2026-10-05 (read-only, no auth); OpenAPI spec at /openapi.json
verified_date: "2026-10-05"
---

# data.gov catalog API (post-CKAN)

`GSA/data.gov` is the platform's project hub, not a library. The useful thing it points at is **catalog.data.gov**: 515,000+ federal, state,
municipal and university datasets (the catalog README's figure), including NASA planetary-science and asteroid data. Old tutorials and
agent memory use the CKAN API. **That API no longer exists there**:

```text
GET https://catalog.data.gov/api/3/action/package_search?q=asteroid   -> 404 {"message":"Not Found"}
GET https://catalog.data.gov/api/action/package_search?q=asteroid     -> 404
GET https://catalog.data.gov/api/3/action/package_show?id=x           -> 404
```

The catalog is now a Flask (APIFlask) app over OpenSearch. Its OpenAPI document is at `https://catalog.data.gov/openapi.json` (the HTML `/docs` page is a 404; use the JSON).
No key is needed. Send a `User-Agent` header.

## Endpoints (from the OpenAPI document, then exercised)

| Endpoint | Purpose |
|---|---|
| `GET /search` | dataset search; params `q`, `sort` (`relevance`, `popularity` observed), `per_page`, `after` (cursor), `accessLevel`, `keyword` (repeatable), `org_slug`, `org_type` (repeatable), `publisher`, `geography_label`, `spatial_geometry`, `spatial_within`, plus more spatial filters |
| `GET /api/dataset/{slug_or_id}` | one dataset, by slug or id |
| `GET /api/keywords` | keyword counts; params `size`, `min_count`, `search`, `keyword` |
| `GET /api/organizations` | all organisations (121 at check time) |
| `GET /api/publishers` | publishers by count; `page_size`, `from_page` |
| `GET /api/locations/search`, `GET /api/location/{id}` | geography lookup |
| `GET /api/stats`, `GET /api/opensearch/health` | metrics, cluster health |

## Response shape

`/search` returns `{"results": [...], "after": "<cursor>", "sort": "relevance"}`. There is **no total count in `/search`**; page by passing the returned `after` back
unchanged (verified: page 2 started with a different dataset). Stop when `results` is shorter than `per_page` or empty.

Each result carries: `slug`, `identifier`, `title`, `description`, `type`, `organization` (object with `name`, `slug`, `organization_type`), `publisher`, `keyword`, `theme`,
`access_level`, `has_download`, `has_spatial`, `popularity`, `last_harvested_date`, `dcat`, `harvest_record`, plus `_score`/`_sort`. The `dcat` object is the DCAT-US record: `title`, `description`,
`identifier`, `keyword`, `modified`, `license`, `publisher`, `contactPoint`, `accessLevel`, `theme`, `bureauCode`, `programCode`, and **`distribution` only when the publisher supplied one**.
A distribution entry has `title`, `description`, `downloadURL` (or `accessURL`), `format`, `mediaType`.

`/api/dataset/{slug}` returned the same envelope as search (`results` with one item, `total: 1`, `aggregations`, `search_after`), so read `results[0]`.

## Verified behaviours and traps

- **Wrong filter values return empty, not an error.** `org_slug=nasa-gov` gave 0 results with HTTP 200; the real NASA slug is `nasa`. Get slugs from `/api/organizations` first (it lists `slug`, `name`, `dataset_count`; for example the Census Bureau entry reported 329,326 datasets).
- **`per_page=1000` was accepted** (1000 results in 0.2 s, about 3 MB for `q=asteroid`). No cap was hit; still page in modest sizes in scheduled jobs.
- **Many records have no downloadable distribution.** `q="asteroid densities"` returned a NASA PDS "context" dataset with `has_download: false` and no `distribution`; in a 17-result search for "near earth object", 12 had a `distribution` and 10 had `has_download: true`. Filter on `has_download`, and treat the landing page (`dcat.landingPage` if present) as the fallback.
- **Distribution entries are often HTML pages, not files** (`format: "HTML"`, a project page URL labelled "Download this dataset"). Check `mediaType`/`format` before treating a URL as machine-readable data.
- A record's distribution list looked unrelated to its title in one case (a "near-earth-object ... NHATS" slug listing ATTREX atmospheric-research URLs): harvested metadata is publisher-supplied and can be wrong, so validate against the title and a sample fetch.
- Keyword counts help scoping: `/api/keywords?search=asteroid` returned `asteroid` 463, `near-earth-asteroid-rendezvous` 177, `multiple-asteroids` 53.

## Minimal client

```python
import json, urllib.parse, urllib.request
def get(path, **params):
    url = "https://catalog.data.gov" + path + "?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, headers={"User-Agent": "my-pipeline/1.0"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())

page = get("/search", q="asteroid", per_page=100, org_slug="nasa")
while page["results"]:
    for r in page["results"]:
        ...                                   # r["slug"], r["dcat"].get("distribution", [])
    if len(page["results"]) < 100: break
    page = get("/search", q="asteroid", per_page=100, org_slug="nasa", after=page["after"])
```

Record the request URL, the harvest date (`last_harvested_date`) and the dataset `identifier` in your provenance (see `space-data-licensing-audit.md` for reuse terms).
