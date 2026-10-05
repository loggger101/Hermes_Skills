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
uv run myproject                     # the [project.scripts] entry point `uv init` writes (uv 0.12.17: no main.py)
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

## uv 0.12.17: measured behaviour (run live on Windows; latest release is 0.12.23)

Scratch projects under a temp dir, about 45 commands, PyPI reachable. Exit codes and messages are quoted from the runs.

**`uv init` defaults changed.** A plain `uv init --name app1` (and `--app`) created `.git`, `.gitignore`, `.python-version` (`3.13`),
`README.md`, `pyproject.toml` and `src/app1/__init__.py`, with `[project.scripts] app1 = "app1:main"` and
`[build-system] requires = ["uv_build>=0.12.17,<0.13.0"]`: **no `main.py`**, so `uv run main.py` fails with
`Failed to spawn: main.py ... program not found`; `uv run app1` printed `Hello from app1!`. `uv init --bare` writes only a
`pyproject.toml` (no `[build-system]`, `requires-python` from `--python`). `uv init --script s.py --python 3.12` writes a PEP 723
header (`requires-python = ">=3.12"`, `dependencies = []`) and a `main()`. `uv init` runs `git init` unless you are inside a
repository; pass `--vcs none` to stop it. Inside an existing project, `uv init --lib sub` adds `sub` as a **workspace member**
(`[tool.uv.workspace] members = ["sub"]`), and **`uv build` run in `sub/` wrote the wheel and sdist to the workspace root
`dist/`**, not `sub/dist/`.

**Lock freshness (the CI-relevant part).** After hand-editing `six==1.16.0` -> `six==1.17.0` in `pyproject.toml`:

| Command | Result |
|---|---|
| `uv lock --check` | exit **1**: `The lockfile at uv.lock needs to be updated, but --check was provided` |
| `uv sync --locked` | exit **1**, same message: the CI gate |
| `uv sync --frozen` | exit 0, `Checked 1 package`: uses the stale lock and **ignores pyproject**; `uv run --frozen` printed `1.16.0` |
| `uv run python ...` (no flag) | re-locks and syncs on its own: printed `1.17.0`, `Uninstalled 1 package`, `Installed 1 package` |

Use `--locked` in CI so a forgotten `uv lock` fails the build; never `--frozen` unless the lock is the intended truth.

**Sync is exact.** `uv add --dev pytest` installed 6 packages; `uv sync --no-dev` then **uninstalled all 6** and
`uv run --no-sync pytest --version` failed with `Failed to spawn: pytest ... program not found`.

**Exit codes.** 0 ok; **1** for resolution failures (`add this-package-does-not-exist-zzz-123`: `was not found in the package registry`;
`add "six>=99"`: `only six<=1.17.0 is available ... requirements are unsatisfiable`) and stale-lock checks; **2** for usage-type errors
(`remove requests` when absent: `The dependency requests could not be found in project.dependencies`; `run nosuchcmd`;
`--nope`: `unexpected argument ... tip: a similar argument exists`; `python pin 3.12` against `requires-python >=3.13`:
`incompatible with the project requires-python value`).

**PEP 723 scripts.** `uv run --script s.py` with inline `dependencies = ["tomli-w"]` built an ephemeral environment in 0.78 s and printed
`a = 1 (3, 13)`; `uv add --script s.py six` rewrote the header (`"six>=1.17.0"`); `uv lock --script s.py` wrote `s.py.lock`.
**`uv run --python 3.10 --script s.py` with `requires-python = ">=3.11"` still ran** (after a 15 s download of CPython 3.10.21) and only
printed `warning: The requested interpreter resolved to Python 3.10.21, which is incompatible with the script's Python requirement`:
a warning is not a gate.

**Reproducibility.** `uv lock --exclude-newer 2024-01-01T00:00:00Z --upgrade` re-resolved despite the lockfile
(`Resolving despite existing lockfile due to addition of global exclude newer`) and, with `six==1.17.0` pinned, failed
`there is no version of six==1.17.0` (that release is newer than the cutoff): the flag makes old snapshots resolvable only for pins
that existed then.

**Other measured facts.** First `uv add` created `.venv` with `Using CPython 3.13.15` in 0.69 s; the first `uv lock --check` took 2.3 s, later resolves 3 ms
to 43 ms; `uv tool run ruff --version` -> `ruff 0.16.10` (3.5 s cold); `uv python dir` is `%APPDATA%\uv\python`,
`uv tool dir` `%APPDATA%\uv\tools`, `uv cache dir` `%LOCALAPPDATA%\uv\cache`; `uv python find` inside a project returns that
project's `.venv\Scripts\python.exe`; `uv version --bump minor --dry-run` prints `sublib 0.1.0 => 0.2.0`; `uv export --no-hashes
--no-emit-project` writes `six==1.17.0 # via demo`; `uv pip install --link-mode hardlink` worked on one drive (cache and project both on `C:`).
Not run: cross-drive link-mode warnings, `uv publish`, `uv python install`, workspaces with several members, `uv sync --inexact`.

## Managing Python versions (pyenv vs uv vs the Windows launcher)

`pyenv` is a Unix tool: its README states it **does not officially support Windows** and does not work outside WSL (there, it installs Linux Pythons, not native Windows ones). On Windows (and anywhere `uv` is installed) manage interpreters with `uv` or the `py` launcher instead:

| Task | Command (verified with uv 0.12.17 on this Windows box) |
|---|---|
| List what is installed | `uv python list --only-installed` showed the system 3.14.6 copies plus uv-managed `cpython-3.13.15` and `cpython-3.11.16` under `%APPDATA%\uv\python\` |
| List downloadable versions | `uv python list` (it showed 3.15.0rc2, 3.14.7 and free-threaded builds as `<download available>`) |
| New venv on a specific version | `uv venv --python 3.11 .venv` downloaded and used CPython 3.11.16 automatically; no separate install step needed |
| Install with a package | `uv pip install --python .venv/Scripts/python.exe <pkg>` |
| Windows launcher | `py -0` lists interpreters; uv-managed ones appear as `Astral/CPython3.11.16` |
| Pin per project | `.python-version` file (read by uv and pyenv) or `requires-python` in `pyproject.toml` |

Why it matters here: several tools in this repo's reviews have no wheel for the newest Python (Kivy 2.3.1, gensim 4.4.0, pykep, great-expectations 1.x, luigi cap `<3.14`); a `uv venv --python 3.11` side environment is the cheapest workaround
(see `data-science/build-systems-data/references/data-engineering-tool-map.md` and `frontend-design/nicegui-app-builder/references/python-gui-toolkits.md`).

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
