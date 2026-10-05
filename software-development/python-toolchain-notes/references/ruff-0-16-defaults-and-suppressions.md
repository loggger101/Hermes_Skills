# Ruff 0.16: the default rule set changed, Markdown is formatted, `ruff: ignore`

Source: [astral-sh/ruff](https://github.com/astral-sh/ruff) (Rust, MIT). Everything below was run live with
`pip install --target <scratch> ruff` -> **ruff 0.16.10** (released 2026-10-01; 0.16.0 was 2026-07-23) on Windows,
plus the 0.16.0 release notes (`gh release view 0.16.0 -R astral-sh/ruff`). Weekly releases: pin the version.

## 1. The no-config default is now 413 rules, not 59

Before 0.16 a bare `ruff check` ran only `E4, E7, E9, F`. On 0.16.0+ it runs **413** rules (`ruff check --show-settings
--isolated` lists them): by prefix, `F:39 PYI:47 UP:42 PLE:33 RUF:36 B:29 SIM:21 PLW:20 C(4xx):17 FURB:17 PLR:13 ASYNC:10
DTZ:10 YTT:10 PIE:8 PLC:8 PT:6 ...` plus `I001` (import sorting), `S110/S112`, `BLE001`, `E722`, `W605`. Eighteen opinionated
`E`/`F` rules were dropped from it: `E401 E402 E701 E702 E703 E711 E712 E713 E714 E721 E731 E741 E742 E743 F403 F405 F406 F722`.

Probe (`import os, sys` / `List[int]=[]` / bare `except:` / stale `# noqa: E501` in one file):

| Command | Findings |
|---|---|
| `ruff check a.py` (no config, 0.16) | 9: I001 F401 UP035 UP006 B006 F841 E722 S110 RUF100 |
| `ruff check a.py --select E4,E7,E9,F` | 5: E401 F401 E741 F841 E722 |
| `ruff check a.py --select ALL` | 18, plus two stderr warnings that D203/D211 and D212/D213 are incompatible and one side is ignored |

Consequences:

- **A repo with no `[lint] select` silently changes meaning when it moves from 0.15 to 0.16.** This repo's `ruff.toml`
  went from a clean-ish pyflakes gate to 309 findings (statistics: BLE001 40, FURB167 36, PLW1510 35, UP036 22 ...).
  Fix: pin what you mean. `select = ["E4", "E7", "E9", "F"]` reproduces the old default exactly (12 findings here),
  or `extend-select` a deliberate set on top of the defaults. `ruff config lint.select` points at the live list.
- Pin the ruff version in the dev group / pre-commit (`rev:`); a floating `ruff` is a weekly rule change.
- `ruff check --fix` applies only safe fixes: the summary says `4 fixable with --fix (2 hidden fixes can be enabled with
  --unsafe-fixes)`. Preview with `--fix --diff`.

## 2. `ruff format` now rewrites Python blocks in Markdown

0.16 formats fenced ```` ```python ```` blocks in `.md` files **by default**. `ruff format --check .` on a skills repo
reported **168 files would be reformatted, 161 of them `.md`**. A test file: `import   math` / `x = {  "a":1 }`
became `import math` + blank line + `x = {"a": 1}`; `bash` blocks were untouched.

- Excluding is a `[format]` setting, not a flag: `[format] exclude = ["*.md"]` (or `--config 'format.exclude=["*.md"]'`);
  a top-level `extend-exclude = ["*.md"]` did **not** stop it, and `--exclude` did not either when the file is named
  explicitly on the command line (an explicit path wins; add `--force-exclude`, then it reports
  `No Python files found`).
- `--no-markdown` does not exist (checked `format --help`). If docs quote verified snippets, exclude `*.md` or accept the
  rewrite deliberately, in one commit.
- `ruff format --check` now prints a diff and supports `--output-format github|gitlab|json|concise` like the linter.

## 3. `# ruff: ignore[...]` comments (new in 0.16)

```py
import math  # ruff: ignore[F401]      # end-of-line
# ruff: ignore[F401]                    # or on the preceding line
import os
```

Probe: both forms suppressed F401. A suppression for a rule that does not fire (`# ruff: ignore[E501]` on `import re`) is
reported by RUF100 as `Unused suppression (non-enabled: E501)` when RUF100 is selected, and the real F401 still fires.
`noqa` still works.

## 4. Adopting a rule set on an old codebase

`ruff check --add-noqa` stamped 6 `# noqa:` comments and the next `ruff check` reported `All checks passed!`, exit 0.
Quirk: a stale `# noqa: E501` got `RUF100` **appended** (`# noqa: E501, RUF100`) instead of being removed, so the dead
suppression is now hidden. Run `ruff check --select RUF100 --fix` first, then `--add-noqa`.

## 5. Other commands worth knowing (all run)

- `ruff rule B006` prints the rule's docs; `ruff linter` lists the upstream linters; `ruff config <key>` documents a
  setting (`ruff config format` lists `exclude`, `preview`, `quote-style`, `docstring-code-format`, ...).
- `ruff analyze graph .` prints a JSON import graph (`{"m.py": ["b.py"]}`), with a warning that it is experimental.
- Exit codes: 0 clean, 1 findings, 2 bad flag or config (`error: invalid value 'E4' for '[RULE]'`: `ruff rule` takes one
  full code, not a prefix).
- `ruff check --output-format github` emits `::error title=ruff (F401),file=...,line=4,col=8::...` annotations; paths are
  absolute on Windows, so anchor the repo root in CI.

## Checklist when touching a repo's ruff config

1. `ruff --version` first; `ruff check --show-settings --isolated | grep -c '('` shows what the defaults mean today.
2. Write `select` / `extend-select` explicitly; never rely on the built-in default.
3. Decide on Markdown formatting (`[format] exclude`) before running `ruff format .` over docs.
4. Pin ruff in pre-commit and the dev group; bump it as its own commit with `--statistics` before and after.
