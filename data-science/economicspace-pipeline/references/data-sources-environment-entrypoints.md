# Data sources, environment & entry points (economicspace)

From CLAUDE.md "Data sources fail softly by design", "Google Drive makes the tree look dirty", "Environment" + "Another host: Linux", and "Entry points". Read when something behaves strangely and it isn't the model.

> **Re-checked 2026-10-01** against economicspace `29a0309` (master v1.40.0). Biggest change: since master v1.34.0 Stage 1 downloads a pinned AsteroidCatalog release, so the survey-source lore below (NEOWISE, SsODNet, MP3C) is history for this repo and now lives in versions.md > "Stage 1 when it built the catalog" and in AsteroidCatalog's tests. Also new: `tree_check.py`, the Drive-revert hazard, `_START HERE.vbs`, and the two stage harnesses.

## Stage 1 installs a pinned catalog release (since master v1.34.0)

- `CatalogConfig.catalog_release` pins one AsteroidCatalog GitHub Release (`data-2026-09-29c` at data contract 1.8.1, as of 2026-10-01). AsteroidCatalog gates a release before publishing it (every source contributed, stamps current, no shrink); publishing happens there (Actions > publish catalog), never here.
- **Nothing on disk changes until every byte matches**: assets stage into a fresh `tempfile.mkdtemp` directory (a fixed staging dir once blocked every later install on the Drive mount: `rmtree(ignore_errors=True)` swallowed a `WinError 5`), are checked (gzip, the decompressed CSV, the taxonomy), then moved; `catalog_manifest.json` is written last.
- **A repin moves every number**, exactly as a rebuild did: baseline, repin, run Stage 1, re-measure **on a cell**, record it in versions.md. Measure a repin as a paired median over the population, never the best row: catalog 1.5.0 made the median cislunar body about a fifth worse while the winner improved, and went unnoticed for three releases.
- `pipeline_version` is CHECKED here, not stamped: it is the data contract; Stage 1 refuses a release whose manifest disagrees. A contract change is adopted by asking who reads the labels (`verify_stage1.py` check 8 fails on a provenance label no reader knows).
- A catalog from before v1.34.0 has no manifest, so `verify_stage1.py` check 3 fails on it by design, including the 2026-08-11 catalog most committed tables were measured on. Keep a copy before the first install if you may need to reproduce one.
- `TAXONOMY_COMPOSITION` comes from the release's `taxonomy.json` (installed as `catalog_taxonomy.json`) and is empty until Stage 1 has run.

## Data sources fail softly BY DESIGN (Stages 2 and 3 now)

Unreachable or empty sources are tolerated and the run continues; since v1.34.0 that is about the two stages that still fetch. **A soft PRICE failure changes the answer without saying so in the number**: with yfinance unreachable, Stage 2 prices every metal off its USGS/LME reference row and Stage 3 prices RP-1 and methane off the table, and the run reports success. Paired comparisons where both sides saw the fallback stay valid; a LEVEL compared with a committed number does not. Read the per-ticker `FAIL` / `WARN` lines before quoting a level. `metals.dev` defaults to key `"DEMO"`, which makes the fetcher skip entirely (intentional; the demo endpoint is heavily rate-limited). Do NOT "fix" an empty source by flipping its toggle off: the toggle excludes a source deliberately, it doesn't route around an outage.

### History: when Stage 1 built the catalog (before master v1.34.0)

Kept for the lessons, which generalise; the catalog-side code now lives in AsteroidCatalog. **A soft failure silently changed the population being measured**, invalidating comparisons without warning:
- Missing spectral types are backfilled by inferring coarse type from albedo → an outage does not SHRINK the catalog, it **INFLATES it with guessed taxonomy**. Check `spectral_type_source` (`source`/`tholen`/`albedo`/`albedo_assumed`/`unknown`) before comparing any run to a committed number.
- The startup banner's "Active sources" line lists what was ENABLED, not what ANSWERED — read the `Source summary: {...}` dict instead.
- ⚠️ **`Source summary` reports what was FETCHED, not what was USED** — and that gap is where NEOWISE hid for four releases (printed 183,408 on runs contributing zero rows; failure in merge key, not fetch). Since v1.1.0 `merge_sources` also reports how many of each supplement's designations MATCHED the backbone: read the `Merged <source>: N supplement records (M matched the backbone, +K new entries)` line — **M = 0 on a source that fetched rows is always a bug in that fetcher**, never an empty upstream table.
- One-line check against any catalog you didn't watch being built:
```bash
py -c "import pandas as pd; d=pd.read_csv('asteroid_pipeline/asteroid_catalog.csv',low_memory=False); print({c:int(d[c].notna().sum()) for c in d.columns if c.startswith('source_')})"
```
A `source_*` column at 0 while its fetcher reported success is the signature.

**A 2026-08 cislunar 2×2 was produced with TWO sources at zero rows and it didn't matter — but check before assuming that of the next one**: IRSA (NEOWISE) returned 502 all evening, MP3C contributed nothing (`{'JPL SBDB': 1555569, 'SsODNet': 1552868, 'NEOWISE': 0, 'MP3C': 0}`). The catalog was unharmed and the PROVENANCE COLUMNS say so rather than row counts: measured diameters 149,590 / taxonomy-from-source 171,007 / albedo-derivations 105,905 — all identical to committed v1.1.0 figures. That outage also quantified NEOWISE's worth: `diameter_source = derived_h_measured_albedo` is **20 rows of 1,555,667** (a body with measured albedo almost always has a measured diameter too — same thermal-IR fit). The v1.1.0 note that NEOWISE recovers IR albedo "for 132,691 bodies" is about COLUMNS and reads as though those rows were sized off it; they aren't.

#### The SsODNet outage that wasn't an outage (fixed v1.0.9)

ssoBFT renamed identity columns (`sso_number`/`sso_name`/`sso_id` → `number`/`name`/`id`). Column projection tolerated the loss, so `fetch_ssodnet` cheerfully returned 50,000 rows with no `designation`; merge dropped the entire source behind one ⚠️ line. A ~500 MB download — every literature diameter/density/rotation/taxonomy in it — went in the bin on EVERY run:

| | before | after |
|---|---|---|
| taxonomy measured | 1,854 | **24,675** |
| taxonomy guessed from albedo | 33,235 | 11,131 |
| density measured | 0 | **438** |
| V-type bodies | 3,988 | 2,614 |

Every number committed before v1.0.9 was measured on the degraded catalog (~1,900 real-taxonomy bodies instead of ~24,700). The V-type count is the tell: V-types are rare; 3,988 was an artefact of guessing from albedo. Three separate things kept it quiet — each a trap worth not rebuilding:
- **The drift warning only fired when fewer than 5 of 24 columns matched.** Fourteen still matched → losing every merge key read as healthy. A projection that tolerates missing columns must still ASSERT the ones it can't work without (`_SSODNET_REQUIRED`).
- **The row-cap sort key sat behind an `if in df.columns` guard** — truncation silently stopped sorting and took an arbitrary 50,000 rows starting near asteroid 367488 instead of Ceres. A guard that turns a wrong answer into a quiet one is worse than no guard.
- **`pq.ParquetFile.schema` is the PHYSICAL parquet schema**, naming nested list columns by inner path (`spins.period.value` read as absent). Test membership against `schema_arrow` — what `read(columns=…)` accepts.

**Spot-check against literature rather than trusting row counts.** Standing check (reproduced exactly on full 1,554,400-row catalog after v1.1.0 rebuild): Ceres 939.400 km / 2.162 g/cm³ / 9.074 h / C; Vesta 522.770 / 3.411 / 5.342 / V; Pallas 513.000 / 2.911 / 7.813 / B; Psyche 222.000 / 4.143 / 4.196 / X; Eros —/—/5.270/S. **All five must also report `diameter_source = measured`** — the check that H-derivation isn't overwriting a measurement, the half a row-count comparison cannot see.

## Google Drive makes the tree look dirty: run the hooks

🚨 **FIRST check which working copy you're in.** This section describes a checkout on a Drive File Stream mount whose `.git` is a ONE-LINE POINTER to an external git dir. A plain clone with a real `.git` directory has neither bug nor need for the hooks:
```bash
ls -d .git && cat .git 2>/dev/null   # "gitdir: ..." = Drive setup
git rev-parse --show-toplevel
```
⚠️ **More than one working copy is the documented divergence hazard, not a convenience** (the parallel-repo divergence shipped `1.0.6`/`1.1.4`/`1.3.6` as two different things). A second checkout many merges behind happily rebuilds master.py from ITS modules → CSV stamped with a version that means something else. Before building/measuring anywhere: confirm branch + up to date with remote.

Symptom: `git status` reports modified, `git diff` shows nothing, every blob hash matches; then `checkout`/`merge --ff-only` aborts "your local changes would be overwritten" — a merged PR silently fails to land locally (bit twice before diagnosed).
Cause: Drive File Stream reports placeholder size 16384 when git stats right after writing during checkout; git caches that in the index stat (`git ls-files --debug master.py` → `size: 16384` vs actual 328,335); every later status sees mismatch and reports modified WITHOUT reading the file. NOT a stat-metadata problem — `core.checkStat=minimal`, `core.trustctime=false`, `core.fscache=false` each tried, none help; don't re-add them.
Fix: `.githooks/drive-restat.sh` (re-stats entries whose content already matches index) wired to post-checkout/post-merge/post-rewrite. Fresh clone opts in once: `git config core.hooksPath .githooks`. Run by hand any time the tree looks wrong: `sh .githooks/drive-restat.sh`. Only touches files whose hash equals the index blob — cannot stage/hide/discard a real edit. Heavier reset when badly tangled (safe when working tree matches HEAD; discards staging only):
```bash
rm -f "$(git rev-parse --git-dir)/index" && git reset
```
A checkout moving BACK to a commit predating the hooks deletes them mid-checkout — repair by hand afterwards.

**The mount can also serve a file as ABSENT or STALE to Python** while `git status` stays clean (2026-09-15: a harness ran an older version of itself and printed OK). `tree_check.py` catches both: it hashes every tracked file through `git hash-object` (never raw sha256, since `.gitattributes` normalises line endings) against the index, and uses `git status` to tell an edit from a bad read: content differs + status clean = changed underneath you; missing + clean = a tracked file is not there. Whole tree, ~0.4 s, and **every harness runs it first and refuses on a finding**: `py tree_check.py`. One gap: a harness's own source is compiled before the check runs.

🚨 **A Drive revert is a silent `git checkout --` of work you have not committed** (2026-09-22, three times in one session): the mount resolves a sync conflict by putting the file BACK and dropping the newer content beside it as `<name>-DESKTOP-<HOSTNAME>.<ext>`. `tree_check.py` cannot see it (the reverted file matches the index). `git add -A` then commits the revert AND adds the conflict copy as a new tracked file. The habit that caught it: **read `git show --stat` after every commit, before pushing** — a file you didn't edit, or a `-DESKTOP-` path, is the whole diagnosis.

## Environment & cross-host

- Windows, invoked as `py` (bare `python` hits the Microsoft Store alias and fails). Working tree on Google Drive with git dir outside it.
- **The interpreter version is NOT stated in CLAUDE.md, and that IS the fix.** It was wrong in three directions inside a week (3.13 vs 3.14 installs appearing and disappearing; by 2026-09-08 `py` was back on 3.13). Ask the machine:
```bash
py -VV && py -0
py platform_check.py   # prints running versions beside the reference host's
```
- **Don't type library versions either**: `platform_reference.json` records them, `requirements-lock.txt` and the `Dockerfile` pin them, `platform_check.py` prints both sets. Why pandas matters: pandas **3.0** infers a plain text column as Arrow-backed `str` where 2.x gives `object`, and every dtype trap lives on the object path.
- **The numeric probes govern hash comparability** (libm, numpy kernels, the CRLF pin, the float round trip); when they match, cell hashes are comparable with versions.md. `platform_check.py` has five probes: `probe_libm`, `probe_numpy`, `probe_csv`, `probe_pandas_dtypes`, `probe_spawn`.
- ⚠️ `platform_check.py` once failed for five days on the host its own reference names: `str_dtype` had been recorded on a transient 3.14/pandas 3.0 install while every other key came from 3.13. Fixed 2026-09-08 by re-recording on one host (exactly that key moved). Rules: record a reference file on ONE host in ONE `--record` run; and a library version is not a defect — `pandas.*` has its own report bucket now ("contract differs, no float moved").
- General lesson: a version spelled out in prose is a number waiting to rot; three files already derive/pin it (`requirements-lock.txt`, `Dockerfile`, `platform_reference.json`).

### Another host: Linux / DGX Spark (GB10, aarch64) — what does not travel

`SPARK_SETUP.md` is the long form. Four traps:
- 🚨 **`lineterminator="\r\n"` IS PINNED in the five CSV writers AND verify.py and must NOT be "cleaned up".** `pandas.to_csv` defaults it to os.linesep; cell_hash is taken over exactly that text, so every hash in versions.md is a hash of CRLF. Unpin → byte-perfect Linux run reports DIFFER on all four cells with every float identical (reads like a Windows leftover — precisely why called out). On Windows the pin is a measured no-op (`5fc52123ed1ecc3a` either way; LF gives `9f6e314f49dc64ef`).
- 🚨 **THE INPUTS ARE NOT IN GIT** and that's what stops a second host first: `asteroid_pipeline/` is gitignored in full — fresh clone has code + frozen Stage-2 prices under `campaign/stage2/`, none of the ~868 MB Stage 4 reads. `preflight()` refuses that run in a second; `run_pipeline.py --check-inputs` (`./run.sh inputs`) answers before a campaign is queued. **Copy them, do not regenerate.** Stage 1 is the exception now: it installs the pinned catalog release, the same bytes on every host. Stages 2 and 3 re-fetch live prices, so a regenerated Stage 2 or 3 table is comparable with nothing already measured.
- ⚠️ **BIT-IDENTITY IS NOT PROMISED ACROSS HOSTS and cannot be made so**: math.exp/log/cos are platform libm; numpy picks SIMD kernels per architecture; none IEEE-required correctly rounded (only sqrt etc.). The rocket equation is `math.exp(dv/ve)` and estimated_mass_kg comes out of `np.power(10.0, -H/5.0)` — not a corner. platform_check.py answers in ten seconds by hashing raw IEEE bit patterns over the model's own argument ranges (sqrt as control). If it reports divergence: re-baseline on that host, compare across hosts with tolerance. **Do NOT file deltas as regressions.**
- ⚠️ **Contradiction inside the repo (2026-10-01):** CLAUDE.md's Linux section still says "the queue is the five measured destinations, not seven", but `campaign/run_queue.py`'s `DESTS` holds all seven and `campaign/stage2/` has a frozen catalog for each. The code is current; that paragraph predates the 28-cell matrix.

## Entry points (read the `runs` column; do NOT count rows)

Everything consuming built master.py sits at repo root. Three that run the model import master BY NAME with repo on sys.path — the only form the worker pool tolerates (`_spawn_environment`).

| file | runs model? | what it is |
|---|---|---|
| `run_pipeline.py` | yes | headless CLI: --preset, --stages, --destination, row caps; carries preflight() + check_defaults_preset(); the ONE entry point immune to the destination trap. Stages 1–3 re-fetch and overwrite the only copy of their CSVs, so it names what a run would re-fetch and waits for `yes` (unless file missing or --yes); run.bat passes --yes on any invocation carrying an argument |
| `ui.py` | yes | Streamlit dashboard. **Defaults a CACHED stage OFF unless Stage 4** (fetches nothing — that's the button's point); ticking a fetching stage still works and now says what it will destroy. Sidebar runtime estimate reads committed full-catalog cislunar cells directly (no ratio; anchored on calc 1.17.7's 733/1,253/3,424/5,692 s when distilled — README notes the banners still derive from calc 1.22.0's cells, on the old 17-vehicle grid) — a CISLUNAR prior, so it reads LOW at leo/mars_surface/earth_surface (2.1–2.7× slower per cell), deliberately. Destination selector SEEDS FROM THE CATALOG ON DISK, not the config default (CALC_CONFIG is earth_surface; catalog usually cislunar) — visible in a selectbox with caption "matches data on disk"; NOT the silent adoption preflight() refuses headless: **a UI default that's visible ≠ a CLI default that isn't** |
| `verify.py` | yes | the release checks (count them in its own header); sets destination explicitly, asserts MISMATCH absent from stdout |
| `tree_check.py` | no | does the disk hold what git says it holds; every harness calls it first and refuses on a finding |
| `verify_stage1.py` | no | Stage 1's seam: the pinned release exists at this pipeline's data contract (network checks run on CI) and the on-disk catalog is that release byte for byte. Never writes the catalog |
| `verify_stage3.py` | no | Stage 3's seam: the adapter against the pinned `spacecost` package; temp dir, no baseline, no network |
| `.github/workflows/verify.yml` | no | CI: build-sync, docs checks, both seams, `platform_check.py` as a report. Not `verify.py`, which needs inputs no clone has |
| `verify_docs.py` | no | docs checks (count them in its own docstring); imports master + four configs but never builds a stage |
| `run.bat` / `run.sh` | no | Windows / POSIX launchers: terminal menu over run_pipeline/verify/build_master/dashboard. Same options and semantics (`quick` 400-row sample all stages, `rerun` Stage-4-only against on-disk catalogs, `standard` 20k rows Stage-4-only, `full` = THE PIPELINE DEFAULTS — measured 13,581 s / 3.8 h at earth_surface vs 5,692 s cislunar). run.sh adds `setup`, `platform`, `inputs` (second-host checks) and runs the dashboard in foreground on 0.0.0.0. No model behaviour of their own; quick/standard cap rows + raw ore N=1 rather than starting the multi-hour default cell |
| `_START HERE.vbs` | no | double-click entry point (was `Dashboard.vbs` until 2026-09-04): starts the dashboard with NO console, ever, via Windows Script Host. Both oddities in the name are load-bearing: `_` (not `!`, which `run.bat`'s delayed expansion eats) sorts it first in Explorer, and the space makes it read as an instruction. Callers must quote it: `start "" wscript.exe "_START HERE.vbs"` |
| `launch_ui.py` | no | supervises `streamlit run ui.py`, owns the stop button. **Deliberately imports NOTHING from this project** (not master/ui/modules) — spawns streamlit as child + watches a socket; it's the one process that must not fail, so putting a 1 MB module + multiprocessing pool inside the supervisor is exactly backwards |

⚠️ `campaign/` holds more ways in: `campaign/run_cell.py` shells out to run_pipeline.py AS A SUBPROCESS (one per cell) — inherits preflight(), can't hit the destination trap; `analyse.py`/`population.py` read archived CSVs and never build a stage. **`campaign/worked_calculation.py` imports master** and answers the destination trap differently: it reads `delivery_destination` (and the Stage 2/3 tables) off the archived ROW it re-derives, so do NOT add `preflight()` to it — that would refuse exactly the archived cells it exists to read. If you add another Stage-4-only entry point not going through run_pipeline.py, call preflight() from it.

## Line endings are pinned per file type (.gitattributes) — do not "normalise" them

- `*.py *.ipynb *.md *.txt` → **LF**: sources get pasted into Colab/Jupyter, and core.autocrlf=true on this machine would otherwise rewrite every checkout to CRLF.
- `*.sh .githooks/*` → LF: a fresh clone with CRLF hooks fails `#!/bin/sh` as "bad interpreter" — silently, because a failing hook is easy to miss; these are the very hooks that repair the Drive stat cache.
- `Dockerfile *.json *.yml *.yaml` → LF: a CR after a backslash continuation puts it into the argument and breaks multi-line RUN on the build host.
- `*.bat *.vbs` → **CRLF**: batch is all labels/goto/call (where LF-only misbehaves) and wscript expects CRLF.
- `master.py linguist-generated=true`; `*.tab -text` (originally for `sdsstax_ast.tab`): a PDS3 archive arrives CRLF and must be checked out byte-for-byte — a mechanically rewritten archive file is no longer the artefact its citation names, in a repo that argues releases from byte-identity.

## Launcher prompt rule (both run.bat and run.sh)

Nothing may prompt once an argument was given: `set /p`/`read` against a stdin a scheduled job holds open but never writes to does not read EOF — it **waits there forever**, so the failure is a hang rather than an exit code. The destination prompt is guarded on "no argument" AND (for run.sh) "stdin is a terminal". Test with `run.bat <option>` / `./run.sh quick < /dev/null` from a non-interactive shell, not from a console.

## Windows dashboard traps (hit building launch_ui.py; each looks fine from console)

- 🚨 **SO_REUSEADDR is INVERTED on Windows**: Unix = "reuse port stuck in TIME_WAIT"; Windows = "bind even though someone else holds it". Setting it made a free-port probe return True for the port Streamlit was serving AT THAT MOMENT → second launch would start a duplicate server on an occupied port. `_port_is_free` does bare bind; "is something listening" is `_port_answers`; `_choose_port` asks that first.
- 🚨 **A process started with `start` inherits this console's stdout** — `run.bat ui > log` blocked until dashboard closed (120 s+ vs 0.46 s); `<nul >nul 2>&1` does NOT fix it. Going through Windows Script Host (`Run`) doesn't pass caller handles → `_START HERE.vbs` delegation, one windowless-start implementation instead of two.
- ⚠️ **Tk.after is not thread-safe** and raises once main loop gone: worker posts callables to a queue.Queue; main thread drains; worker never touches a widget. Cancel the pending pump in quit() too (clearing reschedule flag leaves one already in flight firing into destroyed interpreter).
- 🚨 **Closing window mid-spawn leaked a server nothing could stop**: Popen returns with child alive → assigning to self.proc afterwards left a window where quit() found None, killed nothing. Two things needed: lock makes hand-over atomic AND main() must JOIN the boot thread after mainloop() (daemon thread — without join interpreter exits and kills it wherever it stands).
- ⚠️ **A health check identifies Streamlit, not YOUR Streamlit**: adopting any server answering `/_stcore/health` on 8501 could open somebody else's project. `.launcher/running.json` records port+pid we started; reuse requires marker + live pid AND healthy port (crashed launcher / recycled pid / stranger's app each fail a different one of the three).
- 🚨 **The dashboard's defaults must never re-fetch on their own** — Stages 1–3 all fetch and each overwrites the only copy of its CSV, invalidating every .verify baseline (a mistake made here on 2026-08-23: first click of "Run pipeline" re-priced Stage 2+3 against live quotes).
- Console output is ASCII and must stay that way (final CLAUDE.md section) — the dashboard/console path renders non-ASCII as mojibake.
