# ArcGIS Pro project layout + arcpy idioms (verified from PacktPublishing/Python-for-ArcGIS-Pro @ main, 2026-11-11)

Source: the code repo for *Python for ArcGIS Pro* (Packt), read this pass from its live git tree
(128 blobs) and one completed notebook extracted locally (`Chapter4/CompletedNotebooks/
AddCountyToStateCensusTract.ipynb`, converted from .ipynb with stdlib json — no ESRI software needed to
read it). **arcpy itself cannot run here** (it exists only inside an ArcGIS Pro install's Python), so the
code shapes below are source-read, not executed; everything about layout and naming is directly observed.

## 1. The book-repo shape doubles as a worked example of a real .aprx project — incl. its storage risks

What a chapter actually contains: `ChapterN.zip` (whole-chapter bundle), a **`.aprx`** project file, a
**file geodatabase committed to git as a directory** (`Chapter4.gdb/` with `*.atx` spatial-index files and
`*.gdbtablx` tables), loose **shapefile sidecar sets** (`UniqueStops_Summer21.shp/.shx/.dbf/.sbn` — the four
files are one dataset; a sync that copies three of four silently corrupts it), raw **TIGER/Line zips**, and
a `CensusCSV/ACSDT5Y2019.B03002_<timestamp>/…_data_with_overlays_.csv` directory whose *name encodes the
download timestamp* (ACS table id + fetch time kept in the path, not a metadata file).

Transferable to any GIS repo of one's own (e.g. an ArcGIS Pro project mirrored on OneDrive): a `.gdb` is a
**multi-file binary composite**, so cloud-sync/checkout tools treat its internals as independent files —
this upstream repo ships exactly that hazard inside git, and the book itself tells readers to re-download or
use the zip rather than trust loose copies. If a project must live under a syncing folder, keep canonical
geodata in single-file formats (GeoPackage is one file; shapefile and .gdb are not) and treat `.aprx` as
re-creatable config.

## 2. TIGER/Line naming convention (Census), read off the filenames themselves

`tl_<year>_<statefp|us>_<layer>[.<ext>]`: `tl_2019_us_county`, `tl_2019_06_tract`, `tl_2019_41_prisecroads`,
`tl_2020_06_place`, `tl_2019_06_arealm`, `tl_2019_us_uac10`, `tl_2019_us_cd116`. Layer codes seen: county,
tract, place, prisecroads (primary/secondary roads), arealm/pointlm (area/point landmarks), uac10 (urbanized
areas), cd116 (congressional districts). State FIPS is the 2-digit middle token (`06` CA, `41` OR, `53` WA,
`16` ID, `04` AZ, `56` WY, `32` NV); national extracts use literal `us`.

## 3. The GEOID join-without-a-spatial-join idiom (the notebook's actual lesson)

Census `GEOID` is a **concatenated fixed-prefix FIPS string**: state(2) + county(3) + tract(varies). So
"which county does this tract belong to" needs no intersection — just prefix matching on the code:

```python
# build lookup from the county layer, filtered by SQL WHERE passed TO the cursor (server-side filter)
countyLookUp = {}
with arcpy.da.SearchCursor(usCounty, ['STATEFP','COUNTYFP','NAMELSAD'], "STATEFP = '06'") as cur:
    for row in cur:
        if row[2] not in countyLookUp:          # dedupe on the dict key while building
            countyLookUp[row[2]] = row[1]

arcpy.management.AddField(tract, "CountyName", "STRING")
for countyName, countyFIPS in countyLookUp.items():
    sqlTract = "GEOID LIKE '06{0}%'".format(countyFIPS)   # state+county prefix per county
    with arcpy.da.UpdateCursor(tract, ["GEOID","CountyName"], sqlTract) as cur:
        for row in cur:
            row[1] = countyName
            cur.updateRow(row)
```

Shapes worth stealing (any GIS stack): filter **inside** the cursor's where-clause rather than filtering in
Python after fetching; do per-group updates with one `LIKE prefix%` query per group instead of a dict lookup
per row when the target has an index on that column. Honest caveat this repo also demonstrates: variable-
width trailing components make pure string-prefix joins fragile (tract lengths vary); when codes are fixed
width, slicing exact FIPS segments (`GEOID[:5]`) is safer than prefix `LIKE` — check widths before trusting
either. The general rule: **encode hierarchy in the identifier and attribute joins replace spatial ones** —
same trick as provenance-tagged asteroid catalogs where a source-code prefix answers "where from" without
re-deriving it.

## 4. What the chapter sequence says the full ArcGIS-Python workflow is (from README + dir names)

Basics → data management between **ArcGIS Pro and ArcGIS Online** → automating **map production for print**
→ building **custom script tools for sharing** → analysis & visualization on the Esri stack, with three
case studies. If an agent task touches arcpy at all, that is the capability map: Portal/AGOL item
management, layout-driven export (`.pagx`), and *script tools* (a .py packaged inside a toolbox `.tbx` so it
runs from Pro's UI) are first-class targets — not just notebook analysis.
