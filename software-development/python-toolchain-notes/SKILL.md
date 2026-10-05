---
name: python-toolchain-notes
description: "uv, ruff, ty, loguru, zstd, Codon: measured behavior."
version: 1.0.0
author: Hermes Agent (promoted from python-craft references; uv recipe from trailofbits/skills, live-run 2026-10)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [python, uv, ruff, ty, loguru, logging, zstd, codon, tooling, ci, pep-723]
    related_skills: [python-craft, test-driven-development, python-debugpy, systematic-debugging, failure-signal-audit]
---

# Python toolchain notes

## What This Skill Does

Reference for the tools around Python code rather than the code itself: **uv** project setup and PEP 723 scripts, **ruff** 0.16 rule-set changes, the **ty** type checker's CI behaviour, **loguru** logging, Python 3.14's `compression.zstd`, and the Codon ahead-of-time compiler. Each note records what was actually run, so a config or CI job can be set up without discovering the traps one red build at a time. `python-craft` stays the place for how to write Python; this skill is where tool behaviour lives.

## When to Use

- Starting a Python project or script and choosing the toolchain (uv, ruff, ty, pytest)
- A ruff upgrade suddenly reports hundreds of new findings, or `ruff format` touched Markdown
- ty exits 1 on warnings, or reports walls of `unresolved-import`
- Adding logging to a script or service (loguru vs stdlib), or logs contain colour codes or secrets
- Choosing a compressor (zstd vs zlib/bz2/lzma) or asking whether Codon is worth it
- Not for language idioms, patterns, packaging layout or testing approach (`python-craft`), or debugging runtime failures (`python-debugpy`, `systematic-debugging`)

## Which reference

| Question | Reference | Key fact |
|---|---|---|
| New project, standalone script, migrating from pip/Poetry/mypy/black | `references/modern-python-tooling.md` | `uv add` not `uv pip install`; PEP 723 inline metadata for scripts; `[dependency-groups]`; `uv run`, never activate; ty config lives under `[tool.ty.environment]`. CC-BY-SA-4.0 (Trail of Bits) |
| Ruff upgrade or no-config behaviour | `references/ruff-0-16-defaults-and-suppressions.md` | bare `ruff check` runs 413 rules since 0.16 (was 59); pin `select`; `ruff format` rewrites Markdown python blocks by default; `# ruff: ignore[...]` |
| ty in CI | `references/ty-0-0-84-notes.md` | warnings-only exits 1 (use `--exit-zero-on-warning`); `ty.toml` replaces pyproject's `[tool.ty]`, no merge; no `.venv` gives walls of `unresolved-import` |
| Logging | `references/logging-loguru.md` | brace-format `KeyError` once any argument is passed; `diagnose=True` leaks secrets; colour codes in captured output unless `colorize=False` |
| Compression | `references/compression-zstd-stdlib.md` | `compression.zstd` measured against zlib/bz2/lzma; dictionaries matter for tiny records; `level` and `options` conflict |
| Speeding up pure Python | `references/codon-compiler-notes.md` | AOT compiler, Linux/macOS only, 64-bit int and static-typing differences; source-read |

## Procedure

1. New project: follow `modern-python-tooling.md` (uv, ruff, ty, pytest), then pin the ruff version and an explicit `[lint] select` so a release cannot change your gate.
2. In CI, decide what should fail the build: for ty add `--exit-zero-on-warning` when only errors should gate, and use `--output-format concise` for agent-readable output.
3. Make sure ty can find the environment (`uv venv` first, or `[tool.ty.environment]`); a missing `.venv` produces noise, not a clean fail.
4. Logging in scripts: `logger.remove()`, add explicit sinks with `colorize=False`, `diagnose=False` for anything that can hold secrets, `enqueue=True` across processes, and `logger.complete()` before exit. For libraries other people import use stdlib `logging`.
5. Before changing compressor, benchmark on your data; for many small records train a dictionary.
6. Add new measured behaviour to the owning reference with tool version and date.

## Pitfalls

- A floating `ruff` version is a weekly rule change; an unpinned config meant "59 rules" yesterday and "413" today.
- Two ty config files: `ty.toml` silently wins over `pyproject.toml`.
- `[tool.ty] python-version = ...` is a hard error (exit 2), use `[tool.ty.environment]`.
- `logger.info("x {y}", 5)` crashes the logging call itself; f-strings containing braces plus an argument do too.
- Treating `uv pip install` as the project workflow: it bypasses lockfile management.
- Quoting tool numbers on newer versions: the notes are pinned (ruff 0.16.10, ty 0.0.84, loguru 0.7.3, uv 0.12.17).

## Verification

- [ ] Ruff version and `select` are pinned; the gate result matches the old baseline
- [ ] CI exit-code behaviour of ty was checked with a warnings-only file
- [ ] Log output from a captured run contains no ANSI codes or secrets
- [ ] Tool versions in use match the references, or the probe was re-run

## References

- `references/modern-python-tooling.md` - uv/ruff/ty/pytest setup, PEP 723 scripts, migration table; includes uv 0.12.17 measured behaviour (`uv init` makes a src package with no main.py, `--locked` vs `--frozen`, exit codes 1 vs 2)
- `references/ruff-0-16-defaults-and-suppressions.md` - ruff 0.16.10: default rule set 59 to 413, Markdown code-block formatting and how to exclude it, `# ruff: ignore[...]`, `--add-noqa`
- `references/ty-0-0-84-notes.md` - ty 0.0.84: exit codes in CI, interpreter discovery, `ty.toml` precedence, 136 rules by default level, output formats
- `references/logging-loguru.md` - loguru 0.7.3 setup and traps (brace-format `KeyError`, `diagnose=True` leaking secrets, colour codes), stdlib interception
- `references/compression-zstd-stdlib.md` - Python 3.14 `compression.zstd` vs zlib/bz2/lzma: ratio and speed, dictionary effect on small records, `level`/`options` conflict, `tar.zst`
- `references/codon-compiler-notes.md` - Codon (exaloop) AOT compiler: when it pays off, 64-bit int and static typing differences, `@codon.jit`, `-release`, `@par`
