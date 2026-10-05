# PostCSS 8.5.29 and the usual plugins: what each does, config traps, and when native CSS replaces them (run live)

Source: [postcss/postcss](https://github.com/postcss/postcss) (29k stars, MIT, pushed daily). Installed together on Node 22.23.2 / Windows: `postcss` **8.5.29**
(2026-10-05), `postcss-cli` 12.0.0, `autoprefixer` 10.6.1, `postcss-nested` 8.0.1, `postcss-import` 17.0.0, `cssnano` 9.3.1, `postcss-preset-env` 11.6.1,
`postcss-scss` 4.0.9. Every output below is from running them. Not covered: source-map content, `postcss-import` resolution, Tailwind (v4 uses `@tailwindcss/postcss`
or its Vite plugin, never the `tailwindcss` package itself; see `creative/design-taste-frontend/SKILL.md`).

## The core in one screen

- `postcss.parse(css).toString()` round-trips byte for byte (raws such as `between` are kept: `":"` for `color:red`), so plugins that edit nodes leave the rest of the
  file untouched.
- **Plugin shape in 8**: an object `{ postcssPlugin: 'name', Declaration: { color: d => {...} }, Once, Rule, AtRule, ... }` returned from a factory that has
  `factory.postcss = true`. The visitor form ran (`a{color:blue}` to `a{color:red}`). `postcss.plugin()` (the 7.x helper) is still present as a function in 8.5.29 (calling it did not fail); write the object form.
- **Sync access to an async plugin throws**: `.process(css).css` with a plugin whose `Once` is `async` raised `Use process(css).then(cb) to work with async plugins`. Always `await postcss(plugins).process(css, { from })`.
- **Always pass `from`** (a path, or `undefined` to opt out). Without it PostCSS prints `Without 'from' option PostCSS could generate wrong source map and will not find Browserslist config. Set it to
  CSS file path or to 'undefined' to prevent this warning.`: it goes to the console, not to `result.warnings()` (which was empty), and **autoprefixer then cannot find your browserslist config**.
- Errors are `CssSyntaxError` with `reason`, `line`, `column`, `file`: `a{b:c` gives `Unclosed block` at 1:1, `a{} }` gives `Unexpected }`.
- Source maps: `map: { inline: false }` with `from`/`to` produced `result.map` whose `sources` is `["in.css"]`.
- **The default parser does not understand `//` comments**: `// line comment\na{b:c}` parsed with the selector `"// line comment\na"` and printed back unchanged, with no error. Use `postcss-scss`
  (`syntax: require('postcss-scss')`) for files that have them; it kept `// line comment`, `$v: 1px;` and the nesting exactly as written (it parses, it does not compile Sass).

## Plugin results

| Plugin | Input | Output |
|---|---|---|
| `autoprefixer({ overrideBrowserslist: ['Safari >= 12','Chrome >= 60'] })` | `user-select`, `backdrop-filter`, `position:sticky`, `mask-image` | `-webkit-user-select`, `-webkit-backdrop-filter`, `position:-webkit-sticky`, `-webkit-mask-image`, each followed by the standard property; `display:flex` untouched |
| same with `['last 1 Chrome version']` | same input | **no prefixes at all** |
| `autoprefixer()` with no config found | `a{user-select:none}` | `-webkit-user-select` **and `-moz-user-select`** (browserslist's default query, which I did not print): output depends on the installed browserslist data |
| `postcss-nested` | `.a{color:red; &:hover{...} .b &{x:y} @media(...){z:w}}` | `.a{color:red;} .a:hover{...} .b .a{x:y} @media (min-width:1px){.a{z:w}}` |
| `cssnano({ preset: 'default' })` | `color:#FFFFFF`, `margin:0px 0px 0px 0px`, `url( "x.png" )`, empty `b{ }`, comment | `color:#fff`, `margin:0`, `url(x.png)`, empty rule and comment dropped, `@media(min-width:1px)` (space removed) |
| cssnano, more | `margin:-0; font-weight:normal; transform:translate(0,0); .a{color:red}.b{color:red}; width:calc(100% - 0px)` | `margin:0`, `font-weight:400`, `translate(0)`, `.a,.b{color:red}`, and `calc(100% + calc(-1 * 0px))` (valid but not shorter: check calc rewrites in the diff) |
| `postcss-preset-env({ stage: 2, browsers: 'Chrome >= 60' })` | `inset:0` and `&:hover` nesting | `top:0;right:0;bottom:0;left:0;` and `a:hover{...}`; `var(--c)` kept |
| `postcss-preset-env({ browsers: 'last 1 Chrome version' })` | `inset:0; color:lab(...); &:hover{...}` | **unchanged**: nothing is transformed for a current browser |

So with a modern target `preset-env` and `autoprefixer` do nothing, and `postcss-nested` is replaced by native CSS nesting. What remains useful in 2026: `autoprefixer` for an
older-Safari/Firefox support matrix, `postcss-preset-env` when an old target is required, `cssnano` or Lightning CSS for minification, `postcss-import` for `@import` inlining (not exercised here).

## Config and CLI traps

- **`postcss-nested` 8.0.1 is ESM-only** (`type: module`, Node `^22 || ^24 || >=26`, so Node 20 is out). Loaded with `require()` in a CJS config it returns `{ __esModule, default }`, and calling
  it fails with `TypeError: nested is not a function`: use `.default`, or an ESM config.
- `postcss-cli` 12 finds `postcss.config.js` (CJS, with `module.exports = { plugins: [...] }`) and also `postcss.config.mjs` (an ESM `export default { plugins: [ae({...})] }` was loaded and applied).
  `postcss in.css -o out.css --no-map` exit code 0 and the expected CSS; a syntax error printed `CssSyntaxError: ...bad.css:1:1: Unclosed block` with a code frame and exit code **1**.
- Plugin order matters: `postcss-import` first, then nesting/preset-env, then autoprefixer, `cssnano` last.
- Pin plugin versions with the Node you run: `postcss-nested` 8 already needs Node 22 or newer.

## Choosing

Greenfield with a current-browsers target: native nesting plus the bundler's built-in minifier (Lightning CSS is the usual one; not tested here), no PostCSS at all. Existing pipelines: keep PostCSS, make `from` explicit, and put a
browserslist in `package.json` so autoprefixer's output is reproducible.
