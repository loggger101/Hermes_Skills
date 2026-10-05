# ty 0.0.84 (Astral type checker): CI exit codes, interpreter discovery, config precedence (run live)

Source: [astral-sh/ty](https://github.com/astral-sh/ty) (19.8k stars, beta). `pip install --target` of PyPI `ty` **0.0.84**
(build 8dd9a7f7f, 2026-09-24) on Windows 11 / Python 3.14.6; a planted-defect file, a pyproject/`ty.toml` scratch project and a
`uv venv` (3.12 + attrs 26.1) were used. `modern-python-tooling.md` already says "configure under `[tool.ty.environment]`, not
`[tool.ty]`"; this note confirms that and adds what only a run shows. Not covered: the language server (`ty server`), editor
setup, `ty check --watch`, speed claims (the README's "10x-100x faster than mypy and Pyright" was not measured here).

## Exit codes and flags that matter in CI

| Situation | Exit |
|---|---|
| Clean | 0 (`All checks passed!`) |
| **Warnings only** (an unused `# type: ignore` plus an info) | **1** by default |
| Warnings only with `--exit-zero-on-warning` | 0 |
| `--exit-zero` with errors | 0 |
| Info only (a `reveal_type` with the import) | 0 |
| `--error-on-warning` | 1, same as the default here; it is refused (usage error, exit 2) when combined with `--exit-zero` or `--exit-zero-on-warning` |
| Missing path, or a config error (below) | 2 |

So a CI job that treats exit 1 as "type errors" will also go red on warning-level rules such as `unused-ignore-comment`,
`undefined-reveal` and `deprecated` (info-level output such as `revealed-type` does not); add `--exit-zero-on-warning` when only errors should gate. `-q` keeps a clean run silent.
Output formats (`--output-format`, env `TY_OUTPUT_FORMAT`): `full` (default, rustc-style with context), `concise` (one line per
diagnostic: `file:line:col: error[rule] message`, best for agents and grep), `github` (`::error title=ty (rule),file=...,line=..`
annotations carrying **absolute** file paths), `gitlab` (Code Quality JSON with a `fingerprint`, repo-relative path) and `junit`
(every diagnostic, warnings included, counted as a `failure`).

## Configuration

- The wrong table is a hard error: `[tool.ty] python-version = "3.11"` exits 2 with `unknown field 'python-version', expected one
  of environment, src, rules, terminal, analysis, overrides`. Right: `[tool.ty.environment]`.
- **A `ty.toml` beside `pyproject.toml` wins completely**: ty prints `WARN Ignoring the tool.ty section in pyproject.toml because
  ty.toml takes precedence` and does not merge the two (a `rules` entry in pyproject silently stopped applying). In `ty.toml` the
  keys drop the `tool.ty` prefix (`[rules]`, `[environment]`).
- Unknown rule names in config are only a warning (`warning[unknown-rule] ... Unknown rule 'bogus-rule'`, pointed at
  `pyproject.toml:10:1`), so a typo in a rule name does not fail the run: grep the output.
- Per-file settings: `[[tool.ty.overrides]] include = ["tests/**"]` with `[tool.ty.overrides.rules]` removed the
  `invalid-return-type` warning from `tests/test_m.py` only. Ad hoc: `--error|--warn|--ignore RULE` (repeatable, `all` accepted)
  and `-c 'rules.invalid-return-type="error"'` (beats every config file). `--exclude`, `--exclude-scripts` (skips PEP 723 files)
  and `--python-platform` exist.
- **Default python-version**: from `project.requires-python`'s minimum, else the active environment, else the newest supported.
  `--python-version` accepts 3.7 to 3.15. At `3.9`, `match` and `type X = ...` became `error[invalid-syntax] ... (syntax was
  added in Python 3.10 / 3.12)`: handy for checking a syntax floor.

## Interpreter discovery (the trap)

Without an activated venv or a `.venv` directory, **ty does not fall back to the Python on PATH**. In an empty folder with
Python 3.14 (pip installed) on PATH, `import pip` and `import attr` were both `unresolved-import`, and the cascade followed:
`P(x="s")` on an unresolved `attr.define` class reported `unknown-argument ... object.__init__` instead of the real type error.
After `uv venv --python 3.12 .venv` and installing attrs, ty found `.venv` by itself, resolved `attr`, and reported the true
`invalid-argument-type: Expected int, found "s"`; `pip` stayed unresolved because it is not in that venv. `--python PATH` (interpreter,
venv dir or `sys.prefix`) points it explicitly: `--python $(python -c "import sys;print(sys.executable)")` resolved `pip`.
Rule of thumb: run `uv run ty check` (the venv is active) or pass `--python`; a wall of `unresolved-import` means ty
cannot see the environment, not that the imports are wrong.

## Rules and defaults (`ty explain rule --output-format json`, 136 rules)

- **95 default to error, 25 to warn, 16 to ignore.** Off by default and worth enabling: `possibly-unresolved-reference` (a name set
  in only one `if` branch was **not** reported until set to `error`, which the modern-python-tooling template does),
  `possibly-missing-attribute`, `possibly-missing-import`, `missing-override-decorator`, `missing-type-argument`,
  `division-by-zero`, `unsound-assignment`, `unsound-return-statement`, `blanket-ignore-comment`, `missing-direct-dependency`.
- Warn by default: `unused-ignore-comment`, `unused-type-ignore-comment`, `undefined-reveal`, `deprecated`, `redundant-cast`,
  `redundant-condition`, `unused-awaitable`, `unsupported-base`, `invalid-ignore-comment`, `ignore-comment-unknown-rule`.
- One rule is `preview` (all others `stable`); `ty explain rule NAME` prints the rationale and an example for any rule.
- `reveal_type(x)` works without an import but yields `warning[undefined-reveal]` plus `info[revealed-type]`: both count
  as diagnostics, so remove it before CI. `from typing import reveal_type` silences the warning and leaves only the info line (exit 0).
- Gradual typing: `def h(a, b): return a + b; h(1, "a")` produced no diagnostic. Unannotated code is not checked for call
  compatibility, so add annotations at boundaries first.

## Suppressions and bulk actions

- Both `# ty: ignore[rule]` and `# type: ignore` suppress; an unused one is reported (`unused-ignore-comment` for ty's, and
  `Unused blanket 'type: ignore' directive` for the PEP 484 form). ty's form takes a rule list, which is the one to use.
- `ty check --add-ignore` appended `# ty: ignore[rule]` to every **rule** diagnostic (8 comments in a file with 11) and left the
  unused-ignore/info/reveal ones; it appends after an existing comment (`# invalid-argument-type  # ty: ignore[invalid-argument-type]`),
  so the comment pile is ugly but valid. Use it to adopt ty on an existing codebase, then ratchet.
- `ty check --fix` removed 2 unused ignore comments and left the rest (`Found 3 diagnostics (2 fixed, 1 remaining)`).

## Running without installing

`uvx ty@0.0.84 check` works (the same build string printed). Pin the version in CI: the project is in beta and the `0.0.x`
rule set changes between releases (rule `since` values in the JSON run from `0.0.1-alpha.1` to `0.0.83`).
