---
name: enricher-pipeline-architecture
description: "Layered enricher pipelines: types, tools, two phases."
version: 1.0.0
author: Hermes Agent (promoted from space-data-pipelines, reconurge/flowsint source read)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [pipelines, architecture, enrichers, plugin-registry, graph, osint, extension-builder, flowsint]
    related_skills: [space-data-pipelines, cron-pipeline-watchdog, repo-agent-instructions, cross-harness-skill-porting, rest-api-client]
---

# Enricher pipeline architecture

## What This Skill Does

A source-level read of reconurge/flowsint (v1.2.12, 325 Python files) used as a reference for any pipeline that chains transformations across several data sources and writes to a store: three strict layers, decorator auto-discovery, a two-phase run contract, declarative templates written by an LLM and validated, per-run audit logs, Docker tool wrappers, test conventions and a list of recurring bug classes. It also shows the anatomy of an embedded extension-builder skill. Read from source, not run.

## When to Use

- Designing a pipeline of enrichment steps (lookups, transforms, graph writes) that other people will extend
- Adding plugin auto-discovery or a registry that must survive one broken module
- Deciding where network calls and database writes belong so each part can be tested alone
- Letting an LLM generate pipeline extensions safely
- Not for scheduling and licensing of space datasets (`space-data-pipelines`), watching stale runs (`cron-pipeline-watchdog`), or porting skills between agent harnesses (`cross-harness-skill-porting`)

## Flowsint pipeline-architecture patterns (see `references/flowsint-pipeline-patterns.md`)

Source-level read of reconurge/flowsint @ 1820569 — an OSINT graph tool whose architecture is a clean reference for any multi-source chaining pipeline:

- The **three-layer split**: pure schema types / one-external-system-each tools returning raw data / typed enrichers that own all side effects.
- **Decorator auto-discovery** via os.walk with per-module import-error isolation + idempotent load flag.
- The **scan/postprocess two-phase contract**: the gather phase has no I/O and the persist phase has no network, so each is independently testable. It comes with strict `extra="forbid"` params models and deferred vault-secret resolution.
- **Neo4j MERGE semantics keyed on (type, nodeLabel, sketch_id)**: label collisions are graph-correctness bugs, not cosmetics. Also soft-delete resurrection and batched idempotent re-runs.

Also covered:

- Declarative YAML templates as a first-class extension mechanism, with an LLM generator gated by schema-in-prompt + fence-strip repair + `safe_load` + frozen Pydantic validation (LLM-writes-*config* beats LLM-writes-code).
- Per-run JSON audit logs with input-keyed memoization and fail-fast.
- DockerTool wrapper quirks (`TERM=dumb`, diagnostic re-run on non-zero exit).
- Test conventions for pipeline components.
- A recurring-bug-class checklist from their PR history (~8 naive-datetime fixes, IDOR, UTF-8 assumptions, tight healthcheck timeouts).
- The anatomy of their embedded agent extension-builder skill (source-paths table + decide-before-code tree + refuse-list).


## Procedure

1. Split the code into pure schema types, one-external-system tools that return raw data, and enrichers that own all side effects.
2. Register enrichers by decorator and discover them with a directory walk that isolates import errors per module and loads once.
3. Give each enricher a gather phase with no writes and a persist phase with no network; validate parameters with a strict model that forbids extra keys, and resolve secrets late.
4. Key graph writes on type, label and sketch id so reruns are idempotent; treat label collisions as correctness bugs.
5. When an LLM writes a template, require schema in the prompt, strip code fences, `safe_load`, then validate against a frozen model before saving.
6. Log each run as JSON with input-keyed caching and fail fast on the first error.
7. Run the bug-class checklist in the reference before release.

## Pitfalls

- Naive datetimes, UTF-8 assumptions and tight health-check timeouts: the recurring fixes in the upstream history.
- Swallowed exceptions in enrichers; every `except` should log.
- Letting an LLM write code rather than config.
- Hand-editing registry files that discovery should build.

## Verification

- [ ] Each layer imports without touching the network
- [ ] Gather and persist phases are tested separately
- [ ] A deliberately broken module does not stop discovery of the others
- [ ] A rerun of the same input writes no duplicate nodes

## References

- `references/flowsint-pipeline-patterns.md` - ten sections: layers, registry, two-phase execution, graph write semantics, YAML templates and LLM generation, orchestration, the embedded builder skill, Docker wrappers, tests, recurring bug classes
