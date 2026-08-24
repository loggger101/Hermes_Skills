---
name: build-systems-data
description: "Data build systems: orchestration, versioning, CSV at scale."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [data-pipelines, build-orchestration, versioning, CSV, Parquet, idempotency, production-runs, module-concatenation]
    category: data-science
    related_skills: [python-data-science, python-craft]

---

# Build Systems for Data and ML Projects

Guide for orchestrating data build pipelines — from small scripts that produce a CSV to multi-module systems that concatenate into a production runner, with version stamping, idempotency, and the patterns that keep large data builds from becoming unmaintainable.

## When to Use

- Building a pipeline that produces data artifacts (CSV, Parquet, JSON, model files) from source modules or data
- Orchestrating multiple processing steps into a single production run
- Version-stamping data artifacts so you can tell which code produced which output
- Managing a project where the "source" is several modules that need to be assembled into one runnable artifact
- Keeping a data build idempotent so re-runs don't churn output or mislead version tracking

**Don't use** a build-system approach for one-off scripts that run once and are done. The overhead is for projects where the build runs repeatedly, produces artifacts that are consumed by something else, or has multiple contributors/modules.

## Module Concatenation / Assembly Pattern

A pattern that shows up in large data/ML projects: several independent modules (each a self-contained piece of logic) are concatenated or assembled into a single production runner.

### Why concatenate

- Each module is developed and tested independently.
- The production run is a single artifact that can be executed without assembling at runtime.
- Version stamping is simpler — one file, one version, one run.
- Deployment is one file, not a directory of modules with path setup.

### How to do it safely

**Don't just concatenate raw source.** The result must be a valid, runnable artifact. Common approaches:

1. **Explicit assembly function**: each module exposes a function or section; an assembler combines them in order, with clear boundaries.
2. **Markers/separators**: between concatenated sections, put a clear marker (comment, blank line, sentinel) so you can tell where one module ends and the next begins. Useful for debugging and for verifying the assembly.
3. **Post-assembly validation**: after assembly, run a check (syntax check, import test, smoke run) to confirm the result is valid.

### What can go wrong

- **Import collisions**: two modules import the same name differently, or define the same global. The concatenated result has conflicts.
- **Order dependence**: module B expects module A to have run first (defined a function, set a global). If the assembly order is wrong, the result breaks.
- **Duplicate definitions**: two modules define the same function/class with different bodies. The later one wins silently — a subtle bug.
- **State leakage**: module A sets a global that module B relies on, but module B is assembled before A. The concatenated order must preserve the runtime dependencies.
- **Version drift**: modules updated independently, but the assembly version isn't bumped. The artifact doesn't reflect the current module versions.

### Mitigation

- **Canonical assembly order**: document the order, make it part of the build, and validate it.
- **Namespace isolation**: modules shouldn't share globals with ambiguous names. Use explicit interfaces (function calls, passed state) over implicit globals.
- **No duplicate definitions**: check for them in the build (two modules defining the same top-level name is a build error).
- **Version stamp the assembly**: the assembled artifact carries a version that reflects which module versions went into it.
- **Test the assembled artifact**: not just the modules in isolation, but the concatenated result. A smoke run that exercises the assembled artifact catches assembly-order and collision bugs.

## Version Stamping

Data artifacts should carry a version that tells you what produced them.

### What to stamp

- **Code version**: git commit SHA, or a version string for the build code.
- **Module versions**: if the build is assembled from modules, each module's version or commit.
- **Build timestamp**: when the artifact was produced (not to be confused with content dates — see below).
- **Build parameters**: config, seed, input data version — enough to reproduce the artifact.

### How to stamp

- **Inside the artifact**: a header comment, a metadata row, a JSON sidecar. The stamp should travel with the data.
- **In the filename**: `data_v1.2_20260815.csv` — but filenames drift from reality. Metadata inside is the source of truth.
- **In a manifest**: a separate file that records what was built, when, from what. Useful when the artifact itself is binary or hard to inspect.

### Content dates vs build dates

A build timestamp is when the artifact was produced. A content date is when the underlying data last changed. Don't conflate them:

- A rebuild that produces byte-identical output should not change the content date.
- A content date that moves on every rebuild (even when nothing changed) is misleading — it makes the artifact look newer than it is.
- Derive content dates from the content's history, not from the build time.

## Idempotency

A build is idempotent if running it twice with the same inputs produces the same outputs.

### Why idempotency matters

- Rebuilds don't churn output — no false diffs, no wasted downstream work.
- You can rebuild confidently without worrying about side effects.
- Diff between builds tells you whether anything actually changed.
- Version tracking is reliable — a version change corresponds to a real change.

### How to make a build idempotent

- **No live timestamps in output**: don't embed `datetime.now()` in the artifact unless it's meaningful. If you need a date, derive it from content history, not the current time.
- **Deterministic ordering**: sorted directory listings, sorted dict iteration (Python 3.7+ is insertion-ordered, but explicit sorting is safer for reproducibility), deterministic RNG seeds.
- **No random values in output**: cache-busting tokens, unique IDs, or random seeds that change every build make the output non-idempotent. If you need a unique ID, derive it from content (hash) or make it stable.
- **Stable dependencies**: the build should produce the same output for the same inputs. If a dependency changes under you (a library version, a data source), the output changes — that's expected, but it should be traceable to the dependency change.

### Verifying idempotency

Run the build twice and diff the outputs. If they differ, find out why:
- Timestamps? Ordering? RNG? External dependency?
- Fix the cause or accept it as a known non-idempotency (and document it).

## Production Run Orchestration

A production run is the full pipeline from source to final artifact, run end-to-end.

### Structure

1. **Input validation**: confirm inputs exist, are the expected version, are readable.
2. **Processing steps**: each step does one thing, produces intermediate output, and can be re-run independently.
3. **Assembly**: combine intermediates into the final artifact.
4. **Validation**: confirm the final artifact is valid (schema, size, smoke test).
5. **Version stamp**: stamp the artifact and/or manifest.
6. **Output**: place the artifact where consumers expect it.

### Intermediate artifacts

Keep intermediates — they let you re-run a single step without re-running the whole pipeline. But they also accumulate. Have a strategy:
- Keep intermediates in a scratch directory, clean it periodically.
- Or keep them in versioned storage (one intermediate set per run).
- Or don't keep them at all and re-run from source when needed (cheap steps only).

### Error handling

- A failing step should not produce a partial artifact that looks complete. Either fail the whole build, or mark the artifact as incomplete.
- Log what failed, where, and why. A production run that fails silently (produces nothing, or produces a truncated file) is hard to debug.
- For long-running builds, checkpoint intermediates so a failure near the end doesn't waste the whole run.

## CSV / Parquet at Scale

### CSV

Good for: human-readable, universally parseable, small-to-medium datasets. Bad for: large datasets (slow I/O, no type safety, no compression), binary data, complex types.

```python
import csv

with open("output.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["col1", "col2", "col3"])
    for row in rows:
        writer.writerow(row)
```

For large CSV writes, use buffered I/O and write in chunks. Watch for:
- **Dialect issues**: comma vs tab, quoting, encoding. Specify explicitly (`delimiter=`, `quoting=`, `encoding=`).
- **Float formatting**: default `str(float)` can produce unexpectedly long representations. Format consistently if precision matters.
- **Missing values**: decide on a representation (empty string, `NA`, `null`) and use it consistently.

### Parquet

Good for: large datasets, typed data, compression, columnar access. Requires `pyarrow` or `fastparquet`.

```python
import pandas as pd

df.to_parquet("output.parquet", index=False, compression="snappy")
```

- Parquet preserves types, compresses well, and is fast for columnar reads. Use it for large datasets that will be read by something that understands Parquet (pandas, pyarrow, Spark, etc.).
- For production runs producing 1.5M+ rows, Parquet is usually better than CSV — smaller files, faster reads, type safety.

### Chunked writes for large datasets

When the dataset doesn't fit in memory, write in chunks:

```python
import pandas as pd

def write_large_csv(rows_iterator, path, chunk_size=100000):
    first = True
    buffer = []
    for row in rows_iterator:
        buffer.append(row)
        if len(buffer) >= chunk_size:
            df = pd.DataFrame(buffer)
            df.to_csv(path, mode="a", header=first, index=False)
            first = False
            buffer = []
    if buffer:
        df = pd.DataFrame(buffer)
        df.to_csv(path, mode="a", header=first, index=False)
```

### Accumulation across runs

For projects that produce data cumulatively (each run adds to a growing dataset):
- Append to existing files, or maintain a partitioned layout (one file per run, read across them).
- Track what's been incorporated — a manifest or a high-water mark — so you don't double-count.
- Watch for schema drift across runs (a column appears or changes type). Validate schema on load.

## Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Raw concatenation without validation | Assembled artifact is broken or silently wrong | Validate after assembly; use markers; check for duplicate definitions |
| No version stamp on artifacts | Can't tell what produced which output | Stamp code version, module versions, build time inside the artifact |
| Build timestamp used as content date | Content date moves on every rebuild, even when nothing changed | Derive content dates from content history |
| Non-idempotent build (timestamps, RNG, random IDs) | Rebuilds churn, false diffs, wasted work | Remove live timestamps; deterministic ordering; stable seeds |
| No intermediate artifacts | One step fails, re-run everything from scratch | Keep intermediates; re-run individual steps |
| CSV for large datasets | Slow I/O, no type safety, big files | Use Parquet for large typed datasets |
| Schema drift across cumulative runs | Load fails or misreads after a run changes the schema | Validate schema on load; track schema version |
| Partial artifact on failure | Looks complete but is truncated/wrong | Fail the whole build, or mark incomplete; log the failure |
| Module order wrong in assembly | Broken artifact, subtle bugs | Document and validate assembly order; test the assembled artifact |
| Duplicate definitions across modules | Later definition silently wins | Check for duplicates in build; use explicit interfaces over shared globals |

## The economicspace Master-File Pattern

A real pattern from economicspace: 4 modules concatenated into one ~9600-line `master.py`, with version stamping, production-run orchestration, and a CSV output at scale (1.5M+ rows).

**Why concatenation here:**
- 4 modules (prospecting logic, economics, orbital mechanics, output/write) developed and tested independently.
- The production run is a single artifact — one file, runnable without assembling at runtime, deployable as one unit.
- Version stamping is simpler — one file carries one version.

**How the concatenation works:**
- Each module is a self-contained section with a clear boundary (markers between sections).
- The assembler combines them in the canonical order (module 1, module 2, module 3, module 4) with clear separators.
- The result is a valid Python file that can be run directly.

**What the build system owns:**
- The assembly order and validation (syntax check after assembly, smoke run).
- The version stamp (which module versions went into this master.py, what version the assembly is).
- The production-run orchestration (run master.py with the right config, validate the output, stamp the artifact).

**Version stamping in practice:**
- The master.py carries a version stamp (header comment or metadata) that records which module versions and what assembly version produced it.
- The production run records the version of the master.py it ran, the config, the seed, the input data version, and the output artifact version.
- The output CSV carries a version stamp (header rows or a sidecar) that ties it to the master.py version and the run parameters.

**Idempotency:**
- Running master.py twice with the same inputs should produce the same CSV (byte-identical or content-identical).
- This means: no live timestamps in the output, deterministic ordering, stable seeds, stable dependencies.
- If the output changes between runs with the same inputs, find out why (timestamp? ordering? RNG? dependency change?) and fix it or document it.

**Production-run orchestration:**
- Validate inputs (source data exists, is the right version, is readable).
- Run master.py with the right config and parameters.
- Validate the output (correct shape, correct schema, size in expected range, no NaN where not expected, checksum or version stamp present).
- Stamp the output artifact (version, run parameters, timestamp if meaningful).
- Place the output where consumers expect it (the catalog, the CSV, the report).

**Intermediate artifacts:**
- If the 4 modules produce intermediates (partial results, intermediate files), keep them or reconstruct them so a single step can be re-run.
- Or don't keep them (if the run is fast enough to re-run from scratch when needed).
- Decide based on the cost of re-running vs the cost of storing.

**Testing the assembled artifact:**
- Test the modules in isolation (each module's logic is correct).
- Test the assembled master.py (the concatenation didn't introduce collisions, order issues, or duplicate definitions).
- A smoke run of master.py with a small config produces the expected small output — catches assembly-order and collision bugs.

**What can go wrong with this pattern:**
- A module is updated but the assembly isn't re-run (the master.py is stale — it doesn't reflect the current module versions).
- The assembly order is wrong (module B expects module A's output, but B is assembled before A — the master.py breaks or produces wrong output).
- Duplicate definitions across modules (two modules define the same function — the later one wins silently).
- Version drift (modules updated independently, assembly version not bumped — you can't tell which module versions produced a given master.py).
- Non-idempotent output (timestamps, RNG, non-deterministic ordering in one of the modules — the CSV changes between runs with the same inputs).

**Mitigation:**
- Canonical assembly order, documented and validated.
- Namespace isolation between modules (no ambiguous shared globals; explicit interfaces).
- No duplicate definitions (check in the build).
- Version stamp the assembly and the output.
- Test the assembled artifact (smoke run).
- Verify idempotency (run twice, diff).

## Large-Scale CSV Output Patterns

When the output is a large CSV (economicspace: 1.5M+ rows) — write it efficiently and correctly.

**Writing large CSV efficiently:**
- Buffered I/O (Python's `open()` is buffered by default, but be aware of buffer size for very large writes).
- Write in chunks (accumulate N rows, write them, clear the buffer) — avoids holding the entire dataset in memory.
- Use `csv.writer` for correct CSV encoding (quoting, escaping, dialect).
- Specify dialect explicitly (delimiter, quoting, encoding) — don't rely on defaults that might vary.

**Writing large Parquet efficiently:**
- Parquet is usually better for large typed datasets (smaller files, faster reads, type safety).
- Write with `pandas.to_parquet` or `pyarrow` directly.
- Compression (Snappy, Gzip, etc.) — Snappy is a good default (fast, decent compression).
- Chunked writing if the dataset doesn't fit in memory (write partitions to separate Parquet files, or use PyArrow's chunked writer).

**Schema consistency:**
- Define the schema explicitly (column names, types) and write to that schema.
- Validate the output against the schema (correct columns, correct types, no unexpected nullability).
- For cumulative runs, validate that the schema hasn't drifted across runs (a column added, a type changed, a column dropped).

**Float formatting:**
- Default `str(float)` can produce unexpectedly long representations (many decimal places). If precision matters, format floats consistently (e.g., `f"{value:.6f}"`).
- For CSV that will be read by other tools, consistent float formatting avoids parser differences.

**Missing values:**
- Decide on a representation (empty string, `NA`, `null`, `NaN`) and use it consistently across the output.
- Document the representation (in the schema, in a header comment, in the README).
- For Parquet, missing values are represented natively (null) — no need for a string sentinel.

**Chunked reads for verification:**
- When verifying a large output, read it in chunks (don't load 1.5M rows into memory to check it).
- Check schema, shape, and a sample of rows — not every row (unless the dataset is small enough).
- Check the version stamp and checksum (if present) — that's the provenance check.

## Build Orchestration with Make/Just/Custom Scripts

When the build is more than one script — orchestrate it.

**Make:**
- Good for: dependency-driven builds (rebuild X if Y changed), simple pipelines, projects that already use Make.
- A Makefile with targets for each step (assemble, test, run, validate, clean) and dependencies between them.
- `make` handles the dependency graph — don't rebuild steps whose inputs haven't changed.
- Pitfall: Make's dependency detection is file-based — if the build depends on something that isn't a file (a config value, a git revision), Make may not detect the change.

**just:**
- Good for: command recipes (like a Makefile but without the dependency-graph semantics), projects that want a simple command registry.
- A `justfile` with recipes for each operation (assemble, test, run, validate).
- Simpler than Make for command orchestration; doesn't try to be a dependency solver.
- Pitfall: just is less common than Make — contributors may not know it. Document it.

**Custom script:**
- Good for: builds with custom logic that doesn't fit Make/just (conditional steps, complex validation, API calls, interactive steps).
- A script (Python, shell, etc.) that orchestrates the build: validates inputs, runs steps in order, validates outputs, stamps artifacts, reports results.
- More flexible than Make/just, but you're writing and maintaining the orchestration logic.
- Pitfall: the script becomes a second codebase to maintain. Keep it thin — delegate to the step scripts, don't reimplement them.

**What the orchestrator should do:**
- Validate inputs (exist, right version, readable).
- Run steps in the canonical order.
- Validate outputs (schema, size, version stamp, checksum).
- Handle errors (fail the build, don't produce partial artifacts, log what failed).
- Stamp artifacts (version, run parameters, timestamp if meaningful).
- Report results (what was built, what the output is, any warnings).

**What the orchestrator should NOT do:**
- Reimplement the steps (delegate to the step scripts, don't re-encode their logic).
- Hidden state (the build should be understandable from the orchestrator + step scripts, not from hidden globals or side channels).
- Non-determinism (the orchestrator should produce the same result for the same inputs — no live timestamps, no random IDs, no non-deterministic ordering).

- [ ] Assembly validates after concatenation (syntax check, smoke run, no duplicate definitions)
- [ ] Artifact carries a version stamp (code version, module versions, build time)
- [ ] Content dates are derived from content, not build time
- [ ] Build is idempotent (run twice, diff outputs — same)
- [ ] Intermediates are kept or reconstructable (individual steps re-runnable)
- [ ] Failed steps don't produce partial-looking artifacts
- [ ] Large datasets use appropriate format (Parquet for typed/large, CSV for small/human-readable)
- [ ] Schema is validated on load, especially for cumulative runs
- [ ] Assembly order is documented and correct
- [ ] Module interfaces are explicit (no ambiguous shared globals)
