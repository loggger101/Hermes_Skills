# CSS Blocks 1.5.0 (LinkedIn): dormant, breaks on Windows, and what it enforces (core API run on Node 22)

Source: [linkedin/css-blocks](https://github.com/linkedin/css-blocks) (6.3k stars, BSD-2-Clause, repo pushed 2023-05-20, default branch `master`,
189 open issues). npm `@css-blocks/core` **1.5.0** and `@css-blocks/cli`/`glimmer` 1.5.0, `jsx`/`webpack` 0.24.0, all last
published **2022-04 to 2022-06**. `@css-blocks/core@1.5.0` installed with postcss 8 and driven through `BlockFactory` on Node 22.23.2 /
Windows 11. Not covered: the JSX/Glimmer/webpack integrations, template analysis and the optimiser (`opticss`), `BlockCompiler` output (it threw
`Cannot read properties of undefined (reading 'has')` when called without a template analysis object, so it needs the analysis step I did not build).

## What the idea is

Each stylesheet is a **block** (`*.block.css`): `:scope` is the block root, `.name` are its classes, attribute selectors on `:scope` or a class are
**states** (`:scope[collapsed]`, `.title[big]`). Blocks `extends` other blocks, import with `@block name from "./file.block.css"`, and the build checks
that templates use only declared classes/states, resolves cascade conflicts statically, and emits atomic, deduplicated CSS. The goal is stylesheets whose
conflicts are impossible by construction rather than by naming convention.

## Verified on this machine

- **It crashes on Windows.** `BlockFactory.getBlockFromPath()` threw `TypeError: process.getuid is not a function` from
  `BlockParser/utils/genGuid.js`, which hashes `process.getuid()` plus the block identifier. A shim before loading
  (`process.getuid = () => 1000`) lets it run. The same code comment says the GUID depends on identifier, **machine and user**, so generated class
  names are not reproducible across users or CI hosts unless the build pins that.
- Syntax moved between versions: `[state|active]` (the old namespaced state syntax, still seen in older docs and posts) is rejected by 1.5.0 with
  `A block named "state" does not exist in this context` and `Cannot style values from other blocks`. In 1.x write `:scope[active]`, `.title[big]`.
  A state selector with no `:scope` or class in front (`[active]`) is `States without an explicit :scope or class selector are not supported`.
- A block with `:scope { extends: base; }` parsed: own selectors `:scope`, `:scope[collapsed]`, `.title`, `.title[big]`, and the inherited ones from the base
  (`:scope[active]`, `.label`) appeared through `block.all(true)`.
- **Strict validation** (the point of the tool), all `BlockSyntaxError`: `Distinct classes cannot be combined: .a .b` (a descendant of two classes is
  forbidden), `Tag name selectors are not allowed: div`, and `Missing block object in selector component`. Messages carry file:line:column.
- Install weight: 132 lines of `npm ls --all`, `npm audit` reported **7 vulnerabilities (2 moderate, 5 high)** in the dependency tree (old
  opticss/postcss-era packages), and Node printed `DEP0056 util.isString` deprecation warnings.

## Verdict for new work

Do not adopt it: unmaintained since 2022, a Windows crash, a vulnerable tree and a syntax that changed under its users. Take the idea
and use maintained tools: **CSS Modules** (hashed class names per file, ubiquitous), native **`@scope`**, **`@layer`** and **nesting** (in Chrome 152 `CSSScopeRule`,
`CSSLayerBlockRule` and `CSSNestedDeclarations` exist as interfaces), and stylelint rules such as `selector-max-type` and `selector-max-combinators` for the "no tag selectors, no descendant chains"
discipline. When maintaining an existing css-blocks codebase, shim `process.getuid` on Windows and plan the migration.
