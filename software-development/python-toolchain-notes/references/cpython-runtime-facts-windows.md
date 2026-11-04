---
description: "the CPython interpreter this box actually runs and how to discover it (Hermes-managed 3.14.9 standalone build that the Windows py launcher does NOT register, so `py -3.14` fails while `py -0p` shows only 3.13 and a uv-managed 3.11), its measured GIL state (Py_GIL_DISABLED=0 — a normal GIL build, not free-threaded, which is why cp314t wheels never get selected here), the real pip situation (`No module named pip` yet `ensurepip` importable, bootstrap deliberately left unverified), and how wheel ABI tags explain silent C-extension fallbacks like galpy's"
source_repo: python/cpython star context; all claims below measured on this machine 2026-11-04
tested_version: "Python **3.14.9** (main, Oct 21 2026) [MSC v.1944 64 bit (AMD64)], uv 0.12.14 — every number read live from the interpreter, not recalled"
verified_date: "2026-11-04"
---

# The CPython this box runs (measured), and what it implies

## Which interpreter you are actually in

```
$ python -VV
Python 3.14.9 (main, Oct 21 2026, 17:48:58) [MSC v.1944 64 bit (AMD64)]
exe: ...\hermes\installs\<hash>\environments\<hash>\venv\Scripts\python.exe
base install: ...\hermes\tools\python-3.14.9+...win32-x64\Lib\...
```

So the default `python` is a **Hermes-managed standalone CPython 3.14** (a python-build-standalone style tree under `hermes/tools`, with a venv on top) — *not* an Oracle/PSF-style install in `Program Files`, and not the system Python most tutorials assume.

**The launcher gap, measured.** `py -0p` lists:

```
 -V:3.13 *        C:\Users\Owner\AppData\Local\Programs\Python\Python313\python.exe
 -V:Astral/CPython3.11.16  ...\uv\python\cpython-3.11.16-windows-x86_64-none\python.exe
```

There is **no entry for 3.14** — the Hermes install isn't registered with the Windows launcher, and uv's own downloaded 3.11 appears only as an `Astral/` tag. Consequences worth remembering: `py -3.14` fails even though a working 3.14 is on PATH; conversely anything that resolves interpreters *through the launcher* (some build scripts, editors, `py`-based tooling) silently gets **3.13** and then reports confusing version errors about code you are running under 3.14 elsewhere. When a script claims "Python 3.13" while your shell says 3.14, check whether it went through `py`. Use the explicit interpreter path or drive installs with uv instead of relying on launcher selectors.

## GIL / free-threading: this is a normal build (measured)

```python
sysconfig.get_config_var("Py_GIL_DISABLED") -> 0
sys._is_gil_enabled()                       -> True
```

So despite being 3.14, **this interpreter has the GIL** — it is not a free-threaded build. Free-threading requires a separately built `python3.14t`-style interpreter and wheels tagged `cp314t`; because tag matching excludes them on a GIL build, installing packages here will never pull free-threaded binaries (and vice versa: code tested under `cp314t` elsewhere is not evidence about this box). Practical rule before anyone tries to "turn on" free-threading: it is an interpreter-build choice made at install time, not a runtime flag you can set.

## pip reality — and one thing deliberately left unverified

- `python -m pip --version` → **`No module named pip`** (no pip in the Hermes venv; uv-created venvs likewise ship without it).
- Yet `ensurepip` **is importable**: `...\hermes\tools\python-3.14.9+...win32-x64\Lib\ensurepip\__init__.py`.

Whether `python -m ensurepip` would actually succeed in bootstrapping pip was **not verified** — the probe I attempted hit this environment's approval gate and I stopped rather than retrying or routing around it, so treat that as an open question, not a capability. The route that *is* proven on this box is uv: `uv venv` then `VIRTUAL_ENV=... uv pip install <pkg>` (used repeatedly today, including for packages with compiled wheels). Recording the unverified item explicitly matters more than having a confident answer here; the failure mode it prevents is a future session "remembering" that ensurepip works and building on it.

## Why wheel tags explain silent C-extension fallbacks

Compiled-wheel filenames carry an ABI tag (`cp314`, `cp314t`, `abi3`, `py3`) — which interpreter build the binary matches. Two lessons measured today:

- galpy 1.12.1 installed fine as a **cp314 win_amd64** wheel, yet its compiled module failed at load time (`Could not find module ...libgalpy.cp314-win_amd64.pyd (or one of its dependencies)`) and the library continued in pure Python behind warnings. "Installs cleanly" therefore says nothing about whether the extension **loads**: a `.pyd` failure with *"or one of its dependencies"* means a dependent DLL is missing, not the file itself. Check warnings; don't infer health from silence (`data-science/astro-toolkit-selection/references/galpy-and-anise-measured.md`).
- Tag mismatch is invisible at install time: on this GIL build you get `cp314` binaries by construction, so a package that only ships `cp314t` or `abi3` variants resolves differently than the same command would on another machine. When reproducing someone's performance numbers, confirm interpreter **build** (the config var above) before suspecting your code — and prefer `uv pip install --python <path>` when several interpreters coexist here (Hermes 3.14 + system 3.13 + uv-managed 3.11).

## Environment facts worth pinning rather than re-deriving

| Fact | Value (measured) |
| --- | --- |
| Default interpreter | Python 3.14.9, MSC v.1944, AMD64, Hermes-managed standalone + venv |
| GIL build? | Yes — `Py_GIL_DISABLED = 0` |
| pip module | absent (`No module named pip`) |
| ensurepip importable | yes (bootstrap success **unverified**) |
| Installer that works here | uv 0.12.14 (x86_64-pc-windows-msvc) |
| Launcher-visible versions | 3.13 (default), Astral/CPython 3.11.16 — **no 3.14** |

Related in this skill: `modern-python-tooling.md` (same references directory) for the uv / ruff / ty / PEP 723 project setup this box expects, and `pytest-9-notes.md` for Windows-specific pytest gating. The system CPython **3.13** install at `C:\Users\Owner\AppData\Local\Programs\Python\Python313` (launcher default, measured above) stays available for stdlib-only scripts when a dependency-free interpreter is wanted.
