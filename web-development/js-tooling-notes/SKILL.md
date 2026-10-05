---
name: js-tooling-notes
description: "Bun, standard, PostCSS, js-beautify: measured."
version: 1.0.0
author: Hermes Agent (promoted from react-ecosystem and frontend-library-picks references, run live 2026-10)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bun, node, linting, standard, neostandard, eslint, postcss, autoprefixer, js-beautify, tooling]
    related_skills: [react-ecosystem, frontend-library-picks, static-site-patterns, publish-site, ast-grep]
---

# JavaScript and CSS tooling notes

## What This Skill Does

Per-tool behaviour for the Node-side tooling around a frontend project, each run on Windows with Node 22: the **Bun** runtime and package manager, **standard** vs **neostandard** zero-config linting, **PostCSS 8** with its usual plugins, and **js-beautify**. The notes record install traps, exit codes, silent behaviours and when native features replace the tool.

## When to Use

- Installing or scripting with Bun, or comparing it with Node
- Picking a zero-config JavaScript linter, or linting breaks after an ESLint upgrade
- Setting up PostCSS (autoprefixer, nesting, cssnano) or debugging why autoprefixer ignores browserslist
- Reformatting minified or legacy JS, CSS or HTML
- Not for choosing React libraries (`react-ecosystem`, `react-library-notes`), CSS frameworks and icon sets (`frontend-library-picks`), or site structure and CSP (`static-site-patterns`)

## Which reference

| Tool | Reference | Key facts |
|---|---|---|
| Bun 1.4.2 | `references/bun-runtime-notes.md` | npm 11 blocks its postinstall (`npm install-scripts approve bun`, then `npm rebuild bun`); runs TypeScript directly with **no type checking** (keep `tsc --noEmit` in CI); `.env` auto-loaded and the shell wins; text `bun.lock`; built-in `bun test`; `--compile` makes an 86 MB executable |
| standard 17.1.2 / neostandard 0.13.0 | `references/standard-and-neostandard-notes.md` | standard still depends on ESLint 8.57.1, which npm marks unsupported; neostandard runs on ESLint 9 flat config and gave the same findings on a planted file; limits of `--fix`; parse errors on newer syntax; TypeScript files not handled |
| PostCSS 8.5.29 | `references/postcss-8-notes.md` | object-form plugins only; `await` async plugins; always pass `from`, otherwise autoprefixer cannot find your browserslist config; default parser keeps `//` comments without error (use `postcss-scss`); native CSS replaces some plugins |
| js-beautify 2.0.3 | `references/js-beautify-notes.md` | whitespace re-flow, not a parser: broken code exits 0; with two or more inputs or any glob it **overwrites files in place** without `--replace`; no check mode |

## Procedure

1. Name the tool and version; open its reference and read the install and trap sections before scripting it.
2. Bun: keep Node and `tsc` in the loop for type checking; approve and rebuild the binary after `npm i bun` under npm 11.
3. Linting: choose neostandard on ESLint 9 for new projects; treat standard 17 as pinned to an unsupported ESLint.
4. PostCSS: pass `from`, `await` the result, and ask whether native CSS (nesting, custom properties) removes the plugin.
5. js-beautify: run it on a clean git tree or one file at a time with output to stdout; use a real parser (Prettier) when code must be valid.
6. Add new measured behaviour to the owning reference with version and date.

## Pitfalls

- Assuming `bun run` type checks.
- Running `js-beautify '*.js'` and rewriting every file silently.
- Calling `postcss.plugin()` (7.x style) or reading sync results from async plugins.
- Treating "no findings" from standard as correctness for syntax it cannot parse.
- Quoting versions: all are 2026-10 snapshots.

## Verification

- [ ] Tool versions match the references or the behaviour was re-probed
- [ ] CI keeps an independent type check when Bun runs TypeScript
- [ ] PostCSS runs with `from` set and the browserslist config is picked up
- [ ] Formatter runs never touch files outside the intended set

## References

- `references/bun-runtime-notes.md` - Bun 1.4.2 on Windows: install trap, runtime, `.env`, package manager, test runner, bundler, compile
- `references/standard-and-neostandard-notes.md` - standard 17.1.2 vs neostandard 0.13.0 on a planted file, `--fix` limits, unsupported syntax
- `references/postcss-8-notes.md` - PostCSS 8.5.29 with autoprefixer, postcss-nested, postcss-import, cssnano, preset-env and postcss-scss, config traps, native replacements
- `references/js-beautify-notes.md` - js-beautify 2.0.3: tolerant formatter, in-place-rewrite CLI trap, comparison with Prettier
