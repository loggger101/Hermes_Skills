---
description: "Find the style guide a repo follows and the tool that enforces it: language -> canonical guide (from awesome-guidelines) -> enforcer with current version, plus config files to detect"
source_repo: Kristories/awesome-guidelines (curated link list); versions from PyPI/npm on 2026-10-05
tested_version: registry queries only; no formatter or linter was run in this note (config-file detection hints are general practice, not verified per tool)
verified_date: "2026-10-05"
---

# Style guides and the tools that enforce them

When onboarding to a repo (or writing code in one), do not guess a style: find what is enforced, run that tool, and follow the existing code where no tool decides.
`awesome-guidelines` is a link list of official and company style guides per language; this note pairs the guides worth citing with the automated enforcer.

## Detect first

| Signal in the repo | Means |
|---|---|
| `.editorconfig` | baseline indentation, line endings, charset; honour it in any language |
| `pyproject.toml` with `[tool.ruff]`, `[tool.black]`, `setup.cfg`/`tox.ini` with `[pycodestyle]`/`[flake8]` | Python formatter/linter configuration |
| `eslint.config.js` / `.eslintrc*`, `.prettierrc*`, `biome.json`, `package.json` key `"standard"` | JS/TS lint and format |
| `.stylelintrc*` | CSS (see `web-development/static-site-patterns/SKILL.md`) |
| `rustfmt.toml`, `clippy.toml`; `.clang-format`; `.golangci.yml` | Rust, C/C++, Go |
| `.pre-commit-config.yaml`, CI workflow lint steps | the commands that actually gate merges: run exactly those |

If both a config file and CI disagree, CI wins. If no tool exists, match the surrounding files and propose a tool in a separate change.

## Language, canonical guide, enforcer

| Language | Canonical guide (listed) | Enforcer (registry, 2026-10-05) |
|---|---|---|
| Python | PEP 8 (peps.python.org/pep-0008), Google Python Style Guide, Hitchhiker's Guide | `ruff` 0.16.10 (linter + formatter, replaces flake8/isort/pyupgrade); `pycodestyle` 2.15.0 (PEP 8 checker only); `black` 26.10.0 (formatter); `mypy` 2.4.0 / `pyright` 1.1.414 for types |
| JavaScript | Google JS Style Guide, Airbnb JavaScript Style Guide, JS The Right Way | `eslint` 10.12.0 + `prettier` 3.9.9; or `standard` 17.1.2 (zero-config lint + format); `xo` 5.0.1; `@biomejs/biome` 2.5.15 (one binary for lint and format) |
| TypeScript | listed under TypeScript | `eslint` with typescript-eslint, `prettier`/`biome`, `tsc --noEmit` for types |
| CSS | (frontend section of the list) | `stylelint` 17.16.0 |
| HTML | | `htmlhint` 1.9.2 |
| Markdown | Markdown section | `markdownlint-cli2` 0.23.3 |
| SQL | | `sqlfluff` 4.4.0 |
| Shell | Google Shell Style Guide (Development Environment section) | `shellcheck` (PyPI wrapper `shellcheck-py` 0.11.0.1), `shfmt` |
| YAML | | `yamllint` 1.38.0 (GPL-3.0-or-later) |
| Rust | Rust Style Guide, Rust API Guidelines (rust-lang.github.io/api-guidelines) | `rustfmt` and `clippy` ship with the toolchain (`cargo fmt`, `cargo clippy`) |
| Go | Go section of the list | `gofmt`/`go vet` (toolchain), `golangci-lint` |
| C/C++ | C++ Core Guidelines, Google C++ Style Guide | `clang-format`, `clang-tidy` |
| Spelling in code | | `codespell` 2.4.3 (GPL-2.0-only) |

## Notes from the registry check

- `yapf` 0.43.0 was last released 2024-11 (classifiers up to Python 3.11): prefer `ruff format` or `black` for new work.
- `pylint` 4.1.2 is GPL-2.0-or-later and `yamllint`/`codespell` are GPL; fine to run as dev tools, but do not vendor them into code you ship under another licence.
- Prettier, ESLint, Biome and stylelint all moved major versions recently (ESLint 10, Stylelint 17, Black calendar-versioned 26.x); a committed lockfile and the repo's pinned version matter more than the latest release, because formatting output changes across majors.
- Style guides are decisions about trade-offs, not facts. Quote the repo's configured rules in review rather than a guide's text.

## Procedure

1. Run `git ls-files | grep -E "(\.editorconfig|pyproject\.toml|eslint|prettier|biome|stylelint|rustfmt|clang-format|pre-commit|golangci)"` to list tool configs.
2. Run the enforcers the CI runs, on the files you touched only (`ruff check <files>`, `npx eslint <files>`), and fix findings that your change introduced.
3. Do not reformat unrelated code in a feature change; a formatting-only commit goes separately.
4. Record the style decision (tool + version) in the repo's `AGENTS.md`/`CLAUDE.md` so the next agent skips this step.
