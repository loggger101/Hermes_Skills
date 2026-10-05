# js-beautify 2.0.3: the tolerant formatter, and the CLI that rewrites files without `--replace` (run live)

Source: [beautifier/js-beautify](https://github.com/beautifier/js-beautify) (9k stars, MIT, pushed 2026-10-03). npm
`js-beautify` **2.0.3** (Node >= 14; deps config-chain, editorconfig, glob, js-cookie, nopt) with Prettier 3.9.9 as the
comparison, Node on Windows. Probed through the API (`require('js-beautify').js/.css/.html`) and the three CLI binaries
(`js-beautify`, `css-beautify`, `html-beautify`). Not covered: the Python package, the in-browser build, performance.

## Read this first: the CLI trap

**With two or more input files, or any glob, `js-beautify` overwrites the files in place without `--replace`.** One explicit file
prints to stdout and leaves the file alone; `js-beautify one.js two.js` printed `beautified one.js`, `beautified two.js` and
`one.js` changed from `x=1` to `x = 1`. A glob matching a single file (`'*.cjs'`) also rewrote it, and so did `'*.js'` on a file that
was not even valid JavaScript. In a repo, run it on a clean git tree or give it one file at a time plus `-o`/stdout.
Prettier by comparison needs `--write` for any edit.

## What it is (and is not)

A **whitespace re-flower**, not a parser. It never adds or removes semicolons, never changes quote style, and never rewrites tokens
(`const s = 'it\'s' + "x"` came back byte-identical). That is why it tolerates anything and also why it cannot detect broken code.

- **Syntax errors are not errors.** `function ( { var = ;;; )))` produced `function({\nvar = ;;;)))` with **exit 0**, the CLI
  rewrote such a file in place, and there is no `--check`/`--diff` mode (`--check` is not an option: the run just printed the help text). Prettier
  exits 2 with `SyntaxError: Unexpected token (1:9)` and has `--check` (exit 1 when files differ). For a CI "is it formatted"
  gate use Prettier (or format to a temp file and `git diff --exit-code`).
- **Handles modern JS**: optional chaining, `??`, private fields (`#p`), class statics, numeric separators and BigInt (`1_000n`),
  top-level `await`, `for await`, template literals (`${ b+c }` left as written), regex-vs-division (`a / b / c` and `/=/.test(x)`
  both right). Idempotent on every valid sample (formatting its own output changed nothing).
- **Does not understand TypeScript or JSX; the output is damaged.** `type T<U> = ...` became `type T < U > = ...`,
  `const a: A = {x: 1} as A` moved `as A;` onto its own line, and JSX became `< div className = "a"\nonClick = {\n () => go() } > hi {\n name } < /div>`
  (the text whitespace inside JSX is significant, so this is a semantic change). Decorators (`@dec class A {}`) were left on the
  class line. Prettier formatted the same `.tsx` correctly. Use js-beautify on plain JS, JSON, CSS and HTML only.
- **Defaults**: 4 spaces, `brace_style: collapse,preserve-inline`, `preserve_newlines: true` (max 10), `end_with_newline`
  **false** (the output has no trailing newline: `}` then EOF; set `-n`), no line wrapping (`wrap_line_length: 0`), `else`
  on the closing-brace line. A blank line is inserted before a `function` that follows a statement.

## Options that did what the docs say

`indent_with_tabs`, `brace_style: expand` (puts `{` and `else` on their own lines), `wrap_line_length: 30` (wrapped call arguments,
continuation indented 4), `preserve_newlines: false` (collapsed three blank lines to none), `break_chained_methods: true`
(`a.b()\n    .c()\n    .d()`), `space_in_paren`, `jslint_happy` (adds the space in `function ()`),
`operator_position: 'after-newline'`. Same names in `.jsbeautifyrc` (snake_case) and in the API; the CLI uses dashed flags
(`--indent-size`, `-s`).

## Config discovery

- `.jsbeautifyrc` (JSON) is found by walking **up** from the file: a copy under `sub/deeper/` used the
  parent's `indent_size: 2`. Sections `js`, `css`, `html` override per language (`css: {indent_size: 8}` produced 8-space CSS). `--config PATH`
  overrides discovery.
- **`.editorconfig` is ignored unless you pass `--editorconfig`** (`indent_style=tab` gave spaces without it, tabs with it).
  Prettier reads `.editorconfig` by default, so the same repo formats differently under the two tools unless you set it.
- The CLI picks the language from the file extension (`s.css` through plain `js-beautify` came out as CSS); stdin (`-f -`) was treated as JS.
  `css-beautify` and `html-beautify` are separate binaries for the other two languages.

## HTML and CSS specifics

- HTML: formats inline `<script>` and `<style>` with the JS and CSS rules, keeps `<pre>` and `<textarea>` content verbatim,
  leaves `{{ msg }}` and Vue-style `:class="{a:b}"` / `@click` attributes alone, wraps inline text at `wrap_line_length`
  (`wrap 40` gave a hanging 4-space indent). Unclosed `<li>` stays unclosed (it does not repair markup).
- Handlebars/PHP/ERB/Django/Smarty tags inside HTML are preserved (`templating: auto` = everything but angular for HTML), though
  `{{#each}}` blocks still get an odd two-level indent. **Templating tags in plain JS are not understood** (`var a = {{foo}};` was
  exploded across lines): pass real JS only.
- CSS: **does not add a space around `>` or after `:` in at-rule conditions** (`@media (min-width:600px)`, `.b>.c` kept as written),
  keeps colour/`URL()` case, drops no semicolons (the last declaration keeps the source's choice: `color: red` had none), supports
  nesting (`&:hover`), `@layer`, `@container`, SCSS `@mixin/@include` and `//` comments. Use stylelint rules for ordering/lint
  (see the csscomb section of `SKILL.md`).
- Escape hatches: `/* beautify preserve:start */ ... /* beautify preserve:end */` keeps the lines between the markers,
  `/* beautify ignore:start */ ... /* beautify ignore:end */` keeps even the same-line text exactly.

## Which tool when

Prettier for anything with TypeScript/JSX or when a CI gate is needed; js-beautify for legacy or broken JS, minified-code reading,
HTML with server-side template tags, and when the diff must stay whitespace-only (no semicolon or quote churn). Never
run either across a tree you did not intend to reformat; both rewrite on request only, except the js-beautify multi-file case above.
