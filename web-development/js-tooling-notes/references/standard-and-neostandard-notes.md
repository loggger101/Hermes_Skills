# standard 17.1.2 vs neostandard 0.13.0: zero-config JS linting, run live

Source: [standard/standard](https://github.com/standard/standard) (MIT, 29.4k stars, last push 2025-07-11, not archived).
`npm i standard` (17.1.2, modified 2026-08-18) and, for comparison, `npm i neostandard eslint` (0.13.0 on ESLint 9.39.5), in scratch
projects on Windows, Node 22.23.2. Every output below was captured from a run on small planted files; nothing was linted in a real
repository.

## What standard is now

- **17.1.2 still depends on ESLint `^8.41.0`** (resolved 8.57.1) and `eslint-config-standard 17.1.0`; `npm view eslint@8.57.1
  deprecated` says `This version is no longer supported`. `package.json` engines still allow Node 12.22 and 14.17.
- Zero config: `npx standard file.js`; `--fix` rewrites in place; `--stdin` lints a stream (`<text>:1:1: ...`). It keeps the
  rule set that bans semicolons, uses single quotes and a space before function parentheses. `neostandard` is a flat-config package for ESLint 9
  that produced the same findings here (its relationship to the standard project was not checked).

## One file, same findings in both

`bad.js`:

```js
const a = 1;
var b = "x"
function f(x){ return x==1 }
if (a) { console.log(b) };
let unused = 5
```

Both tools reported the same 10 problems (9 errors, 1 warning), exit **1**: `1:12 Extra semicolon (semi)`, `2:1 no-var` (a **warning**),
`2:9 Strings must use singlequote`, `3:10 'f' is defined but never used`, `3:11 Missing space before function parentheses`,
`3:14 Missing space before opening brace`, `3:24 Expected '===' (eqeqeq)` and `Operator '==' must be spaced`,
`5:5 'unused' is assigned a value but never used` and `'unused' is never reassigned. Use 'const' instead (prefer-const)`. Differences:
neostandard prefixes stylistic rule names (`@stylistic/semi`, `@stylistic/quotes`) and prints 6 errors plus 1 warning as
"potentially fixable with --fix"; standard prints `Some warnings are present which will be errors in the next version` (the `no-var`
warning) and `Run standard --fix to automatically fix some problems`.

- **`standard --fix` result:** `const a = 1`, `const b = 'x'`, `function f (x) { return x == 1 }`, `const unused = 5`. It did **not**
  fix the unused function, `==` (eqeqeq) or the `};` after the `if` block, and **did not report that trailing `;` at all** (line 4 was
  never flagged), so a clean standard run does not prove the file has no semicolons.
- `--stdin` with `var a = 1` -> `no-var (warning)` and `'a' is assigned a value but never used`.
- Default environments are permissive: `document.title = 'x'` and `process.env.X` produced no error, while `it('a', ...)` gave
  `'it' is not defined (no-undef)`: test globals need an environment or `globals` setting (the exact flag was not tested).

## Language support limits (ESLint 8.57.1 parser and ESLint 9.39.5 + neostandard)

| Source | standard 17.1.2 | neostandard 0.13.0 / ESLint 9.39.5 |
|---|---|---|
| top-level `await` in `.js` and `.mjs` | passes | passes |
| class private fields, `static {}` blocks, `Object.hasOwn`, `.at()`, `?.` `??` | passes | passes |
| `import fs from 'node:fs'` with `require` used in the same file | passes (node globals allowed) | not tested |
| regex `/[\p{L}--[a-z]]/v` (ES2024 `v` flag) | **`Parsing error: Invalid regular expression flag`**, exit 1 | same parsing error |
| `using x = null` (explicit resource management) | `Parsing error: Unexpected token x` | same parsing error |
| TypeScript (`const x: number = 1`) | `Parsing error: Unexpected token :` | the file is **ignored with a warning** (`File ignored because no matching configuration was supplied`) until TypeScript is enabled in the config |

A parse error is reported as a lint failure (exit 1) with `(null)` as the rule, so a newer-syntax file fails the gate even though it is
valid JavaScript.

## Setup for neostandard

`eslint.config.js`: `import neostandard from 'neostandard'; export default neostandard({})`, run `npx eslint file.js`. In a package with
`"type": "module"` this worked as written. Check the options README before enabling TypeScript or JSX.

## When to use which

- Existing repos already on standard keep working; pin `standard@17.1.2` and expect no new rules or parser updates.
- New projects: neostandard on ESLint 9, which carries the same rule outcomes (10 vs 10 on the probe) with a supported ESLint.
- Neither understands ES2024 `v` regexes or `using` at the versions tested; avoid those in linted source or exclude the file.
- Not covered: JSX/React rules, `ts-standard`, `--plugin`, ignore globs, and monorepo performance.
