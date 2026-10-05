# Skills shipped inside a UI library (Preline): what a vendor skill does well, and where it breaks our conventions

Source: the `skills/` directory of [htmlstreamofficial/preline](https://github.com/htmlstreamofficial/preline) (read through the
GitHub contents API on 2026-10-05; the library itself is covered in
`web-development/frontend-library-picks/references/preline-5-notes.md`). Source-read only: the MCP server these skills call was not
run, and the theme generator's scripts were not executed. Install command in the README: `npx skills add htmlstreamofficial/preline`.

## Layout

```
skills/
  preline-mcp/            SKILL.md (11.8 kB), agents/openai.yaml, references/{catalog-map,composite-layouts,mcp-tools-reference}.md
  theme-generator/        SKILL.md (2.5 kB), docs/{workflow,palette-guidance,final-output-style,validation-checklist,token-reference}.md,
                          examples.md, scripts/{find-themes-dir.js, generate-theme.js (37.8 kB), run-theme-generator.js}
```

- **Name/path mismatch**: `theme-generator/SKILL.md` declares `name: preline-theme-generator`. Our frontmatter audit rule 7
  (`software-development/skill-library-audits/references/frontmatter-audit-pattern.md`: `name:` must equal the directory name) would flag it. When importing, rename the directory
  or the field, not both ways.
- `agents/openai.yaml` is a per-agent UI manifest: `display_name`, `short_description`, and a `default_prompt` that names the skill
  with a `$preline-mcp` mention and spells out the first three calls. Useful as a model for a "starter prompt" for a skill whose tools must
  be called in a fixed order; our Hermes skills have no such file.

## Patterns worth copying (from `preline-mcp`)

1. **Never guess identifiers; discover, then fetch.** Every section/component/category slug is an exact kebab-case string, so the skill
   forces `components_list` / `blocks_categories` first. The same rule applies to any skill wrapping an API with opaque IDs.
2. **Scope list calls to avoid giant responses.** `components_list` with no `section` loads "300k+ characters"; the skill says to pass the
   inferred section whenever the type is known. State the cost of the unscoped call in the skill, not just the parameter.
3. **One at a time, finish before the next.** "Retrieve one component or block, integrate it fully, then move to the next."
4. **Ask only when the choice is real.** Ask the user to pick for (a) abstract requests ("something for a pricing page") and (b) tied
   candidates; if exactly one candidate satisfies everything named, do not interrogate. One focused question per round, with a short
   scannable list and the catalogue's own one-line descriptions.
5. **Composite requests: plan the tree first.** Lock cross-cutting constraints once (class system, shared surfaces, density), decompose
   into containers, regions and leaves, one fetch per leaf, assemble **outermost first** so the shell sets script/init anchors.
6. **Deterministic placement rules instead of "put it somewhere sensible"**: CSS goes in `<head>` just before `</head>`, never in `<body>`;
   external scripts go after the first *structural* closing tag found by scanning upward from `</body>`, ordered third-party scripts before
   the Preline core script and Preline helpers after it; the init `<script>` is last, immediately before `</body>`, wrapped in a `load`
   listener. A rule an agent can execute mechanically beats advice.
7. **Say which tool output is authoritative.** The "Trust the returned markup" section lists the three time sinks to avoid (grepping the
   user's compiled CSS to confirm a class exists, writing HTML validators, re-reading the placed file) and the replacement: verify the
   result **against the request** ("is every element the user named present?"), not the generated code.

**Reconciling #7 with `verification-before-completion` and the global "verify, don't assume":** trust applies to output a tool generates
by construction from the vendor's own catalogue (classes resolve at the consumer's build step, so a missing class in one stylesheet means
nothing). It does not exempt checking the integration itself (script order, init call, the page loading). Keep the carve-out narrow and
name the failure it prevents, as the Preline skill does.

## Patterns worth copying (from `theme-generator`)

- A **read order** in the SKILL.md (workflow, palette guidance, output style, validation checklist before closing, examples only if
  asked, the 21 kB token reference only when needed) keeps the large file out of context by default.
- A **validation checklist the agent must self-check before returning** (one file only, `theme-<name>` consistent, no raw hex/oklch in
  semantic tokens, dark mode via variables, full token coverage). Checklist items are mechanically testable, the kind our gates can enforce.
- **Security constraints stated as prohibitions**: no `npx` or network-fetched packages, no raw user text interpolated into shell
  commands, no broad `find .` for path discovery (use the bundled `find-themes-dir.js` or a user-confirmed path), no writing outside a
  confirmed directory, one script (`run-theme-generator.js`) as the only execution entry point. Compare with
  `references/skill-registry-security.md`: a skill that runs scripts should name its single entry point.
- It also says "do not bypass safety or approval prompts", which is wording a skill can safely repeat but cannot enforce.

## Caveats

- A skill that depends on a remote MCP server is only as available as that server; the Preline skill has no offline fallback and its
  catalogue grows server-side, so the example IDs in its references can go stale.
- 11.8 kB for the main SKILL.md is long; the vendor keeps it readable with tables and a decision table, but the three reference
  files hold the detail the skill only needs on composite requests.
