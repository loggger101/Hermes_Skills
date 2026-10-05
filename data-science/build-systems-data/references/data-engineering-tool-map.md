---
description: "Data-engineering tool picks from awesome-data-engineering with PyPI freshness and a Python 3.14 install trap (pip silently installs an old great-expectations 0.18 and luigi 3.6)"
source_repo: igorbarinov/awesome-data-engineering (curated list); versions from the PyPI JSON API on 2026-10-05
tested_version: PyPI metadata queries + `pip install --dry-run --no-deps` on Python 3.14.6 / Windows; no pipeline tool was run
verified_date: "2026-10-05"
---

# Data-engineering tool map (with install reality on this machine)

The awesome list covers databases, ingestion, streaming, batch, workflow, lakes, serialization, quality and monitoring (hundreds of entries, many abandoned
or promotional; it labels a few "Deprecated"). This note keeps the Python-installable picks that fit the scale of this repo's pipelines (single machine,
CSV/Parquet, DuckDB/Polars) and checks which actually install on **Python 3.14.6**.

## The install trap

`pip install` on an interpreter newer than a package's `Requires-Python` does **not fail**: it quietly resolves the newest release that still allows your Python.
Dry-run on 3.14.6, Windows:

| You ask for | PyPI latest | `Requires-Python` | pip would install |
|---|---|---|---|
| `great-expectations` | 1.23.2 | `<3.14,>=3.10` | **0.18.22** (the pre-1.0 API line; code and docs for 1.x do not apply) |
| `luigi` | 3.8.1 | `<3.14,>=3.10` | **3.6.0** |
| `polars` | 1.44.2 | `>=3.10` | 1.44.2 (classifiers list up to 3.13 but the requirement allows 3.14) |

Always read the resolved version in the install output (or run `pip install --dry-run pkg`) and check `pkg.__version__`. For tools capped below 3.14,
use a 3.12/3.13 venv (`py -3.13 -m venv`), or pick an alternative that supports 3.14.

## Picks by stage (PyPI snapshot 2026-10-05)

| Stage | Tool | Version | Released | Python | Notes |
|---|---|---|---|---|---|
| Ingestion (pipelines as Python) | `dlt` | 1.30.0 | 2026-08-11 | `<3.15,>=3.10`, cl. 3.14 | Apache-2.0; runs in notebooks, cloud functions, Airflow |
| Ingestion (CLI copy DB to DB) | `ingestr` | 1.1.61 | 2026-10-01 | `>=3.10` | |
| ELT, Singer taps | `meltano` / `singer-sdk` | 4.4.0 / 0.54.7 | 2026-09-29 | `>=3.10`, cl. 3.14 | |
| Orchestration (heavy, many users) | `apache-airflow` | 3.3.2 | 2026-09-17 | `!=3.15,>=3.10` | |
| Orchestration (asset-centric) | `dagster` | 1.13.25 | 2026-10-01 | `<3.15,>=3.10` | |
| Orchestration (Python-first, flows) | `prefect` | 3.8.7 | 2026-09-27 | `<3.15,>=3.10` | |
| Orchestration (simple batch DAG) | `luigi` | 3.8.1 | 2026-05-07 | **`<3.14`** | see trap |
| Pipeline framework | `kedro` | 1.7.0 | 2026-09-28 | `>=3.10` | |
| Transform as functions-DAG | `sf-hamilton` | 1.90.0 | 2026-04-25 | `<4,>=3.10.1` | |
| SQL transform | `dbt-core` + `dbt-duckdb` | 1.12.5 / 1.11.0 | 2026-09-15 / 2026-08-07 | `>=3.10`; dbt-duckdb cl. 3.13 | |
| SQL transform | `sqlmesh` | 0.236.2 | 2026-09-08 | `>=3.9` | |
| Pipeline UI | `mage-ai` | 0.9.79 | 2026-01-21 | `>=3.9` | slower cadence |
| Data quality (YAML or code) | `great-expectations` | 1.23.2 | 2026-09-25 | **`<3.14`** | see trap |
| DataFrame contracts | `pandera` (not on the list) / `daffy` | 0.33.1 / 3.1.0 | 2026-09-01 / 2026-08-10 | `>=3.10`, cl. 3.14 | decorator-style checks at function boundaries |
| Data contracts | `datacontract-cli` | 1.2.2 | 2026-09-25 | `<3.15,>=3.10` | |
| Quality scans | `soda-core` | 4.25.0 | 2026-09-23 | `>=3.10` | PyPI metadata license field says "Proprietary"; read its licence before using |
| Engines | `duckdb` 1.5.6, `polars` 1.44.2, `pyarrow` 25.0.1, `dask` 2026.8.0, `pyspark` 4.2.0 | | 2026-07..09 | `>=3.10` | |

## Name collisions on PyPI

- `bruin` on PyPI is a **2021 unrelated package** (0.3.3, `>=3.6`); the list's Bruin pipeline tool is a separate Go CLI. `pip install bruin` is the wrong software.
- `evidence` on PyPI is a 2023 unrelated package; the BI-as-code tool Evidence is a JavaScript project.
- Check the project's own install instructions (repo README) rather than guessing the PyPI name.

## Choosing at this repo's scale

- One machine, files in and out: a script per dataset plus DuckDB/Polars (see `build-systems-data/SKILL.md`, `duckdb-querying`, `python-data-science`) beats any orchestrator; add one only when you need retries, schedules across many jobs, or lineage.
- First step up: `dlt` for sources with schemas and incremental loads, `prefect` or `dagster` for scheduling, `pandera`/`daffy`/`great-expectations` for checks at stage boundaries.
- Streaming and Hadoop-era entries on the list (Kafka tooling, Sqoop, Oozie, Azkaban, Heka, Gobblin) are irrelevant at this scale; several carry a "Deprecated" tag in the list itself.
- Treat unsupported-Python caps as a hard planning input: record the interpreter version next to the tool choice.
