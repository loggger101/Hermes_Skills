# Modern Python tooling: uv, ruff, ty, PEP 723

<!-- source: trailofbits/skills plugins/modern-python (starred-repo deep-dive 2026-09-05); based on
     trailofbits/cookiecutter-python. Was the standalone skill `modern-python-tooling` until round-57
     merged it into python-craft. -->

> **License:** this file is CC-BY-SA-4.0 (Trail of Bits, trailofbits/skills), unlike the MIT-licensed
> python-craft SKILL.md that links to it. Attribution retained per that license; derivatives of this
> file stay CC-BY-SA-4.0.

The full setup behind python-craft's Toolchain Defaults.

## What This Covers

Modern Python project setup with the current toolchain: **uv** (deps/envs), **ruff**
(lint+format, replaces flake8/black/isort/pyupgrade), **ty** (type check, Astral's faster
mypy alternative). Covers new projects, standalone scripts via PEP 723 inline metadata, and
migration from legacy tooling.

## When It Applies

- Creating any new Python project or package; writing a script with external dependencies
- Migrating requirements.txt/pip/Poetry/mypy/black setups (only when the user asks)
- NOT for: projects pinned to Python <3.11, non-Python codebases, or users who explicitly keep legacy tooling

## Anti-Patterns → Modern Equivalent

| Avoid | Use instead |
|---|---|
| `uv pip install` / editing pyproject.toml by hand | `uv add <pkg>` / `uv remove <pkg>` |
| requirements.txt for scripts | PEP 723 inline metadata (below) |
| `[project.optional-dependencies]` for dev tools | `[dependency-groups]` (PEP 735) |
| mypy / pyright | ty (`[tool.ty.environment] python-version`, NOT `[tool.ty]`) |
| `source .venv/bin/activate` then run | `uv run <cmd>` — never activate manually |
| hatchling build backend | `uv_build` (simpler, sufficient for most) |
| pre-commit | prek (Rust-native, no Python runtime needed) |

**Key principles:** always `uv add`/`uv remove`; never manage venvs by hand; dev/test/docs deps go in `[dependency-groups]`.

## Decision Tree

```text
Single-file script with dependencies?      → PEP 723 inline metadata (below)
New multi-file project, not distributed?   → Minimal uv setup (Quick Start)
New reusable package/library?              → Full setup: uv init --package + pyproject config below
Migrating existing project?                → Migration Guide below
```

## Quick Start: Minimal Project

```bash
uv init myproject && cd myproject
uv add requests rich                 # runtime deps
uv add --group dev pytest ruff ty    # dev deps via dependency groups
uv run python src/myproject/main.py  # everything runs through uv run
uv run pytest                        # tools too
```

## Full pyproject.toml (library)

```toml
[project]
name = "myproject"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[dependency-groups]
dev = [{include-group = "lint"}, {include-group = "test"}, {include-group = "audit"}]
lint = ["ruff", "ty"]
test = ["pytest", "pytest-cov"]
audit = ["pip-audit"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["ALL"]
ignore = ["D", "COM812", "ISC001"]   # explicit ignores, never blanket-quiet

[tool.pytest.ini_options]
addopts = ["--cov=myproject", "--cov-fail-under=80"]

[tool.ty.environment]
python-version = "3.11"              # NOTE: [tool.ty.environment], not [tool.ty]

[tool.ty.rules]
possibly-unresolved-reference = "error"
unused-ignore-comment = "warn"
```

Install all groups: `uv sync --all-groups`. Bootstrap a complete preconfigured project instead of hand-writing config: `uvx cookiecutter gh:trailofbits/cookiecutter-python`.

## PEP 723: Standalone Scripts with Dependencies

No venv, no requirements.txt — metadata lives in the script header and `uv run` resolves it on demand:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests",
#     "rich",
# ]
# ///
import requests, rich
print(requests.get("https://api.example.com/data").json())
```

Run: `uv run script.py` (or directly via shebang if uv is on PATH). Private index inside the block: `[tool.uv] extra-index-url = ["..."]`. Use for single-file automation; use pyproject.toml for anything multi-file.

## Ad-hoc Dependencies Without Touching the Project

```bash
uv run --with requests python -c "import requests; print(requests.get('https://httpbin.org/ip').json())"
uv run --with httpx pytest    # project deps + temporary extra
```

`--with` = one-off (testing, scripts outside a project); `uv add` = permanent project dependency.

## uv Command Quick Reference

| Command | Purpose |
|---|---|
| `uv init [--package]` | new project / distributable package |
| `uv add <pkg>` / `--group dev <pkg>` | add to deps / a group (updates lock) |
| `uv remove <pkg>` | remove dependency |
| `uv sync [--all-groups\|--group X]` | install from uv.lock |
| `uv run <cmd>` / `--with pkg <cmd>` | run in venv / with temp dep |
| `uv build` / `uv publish` | package / release to PyPI |

Commit `uv.lock`. Use `src/` layout for packages. Enforce coverage minimum (80%+).

## Migration Guide (when asked)

**requirements.txt + pip → uv:** scripts become PEP 723; projects:

```bash
uv init --bare
grep -v '^#' requirements.txt | grep -v '^-' | grep -v '^\s*$' | while read -r pkg; do
    uv add "$pkg" || echo "Failed to add: $pkg"   # review each package first
done
uv sync
# then delete requirements*.txt and the old venv/ dir; commit uv.lock
```

**setup.py/setup.cfg → pyproject:** `uv init --bare`, move deps via `uv add` (dev ones with `--group dev`), copy non-dep metadata into `[project]`, delete setup.py + MANIFEST.in.

**flake8+black+isort → ruff:** remove old tools, delete their configs, `uv add --group dev ruff`, add the `[tool.ruff]` block above, then `uv run ruff check --fix . && uv run ruff format .`.

**mypy/pyright → ty:** remove + delete mypy.ini/pyrightconfig.json, `uv add --group dev ty`, configure under `[tool.ty.environment]`, run `uv run ty check src/`.

## Security Tooling (pre-commit / CI)

| Tool | Catches | Runs in |
|---|---|---|
| shellcheck | shell script bugs | pre-commit |
| detect-secrets | committed secrets | pre-commit |
| actionlint + zizmor | workflow syntax / supply-chain risks | pre-commit, CI |
| pip-audit | vulnerable dependencies | CI, manual |
