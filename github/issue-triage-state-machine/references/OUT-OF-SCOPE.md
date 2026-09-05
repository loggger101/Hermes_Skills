# Out-of-Scope Knowledge Base

The `.out-of-scope/` directory in a repo stores persistent records of rejected feature requests:
1. **Institutional memory**: why a feature was rejected, so reasoning isn't lost when the issue closes
2. **Deduplication**: new issues matching a prior rejection surface the previous decision instead of re-litigating

## Directory structure
```
.out-of-scope/
├── dark-mode.md
├── plugin-system.md
└── graphql-api.md
```
One file per **concept**, not per issue. Multiple issues requesting the same thing group under one file. Kebab-case names recognizable without opening: `dark-mode.md`, `plugin-system.md`.

## File format
Relaxed, readable style — a short design document, not a database entry. Paragraphs, code samples, examples.

```markdown
# Dark Mode

This project does not support dark mode or user-facing theming.

## Why this is out of scope

The rendering pipeline assumes a single color palette defined in `ThemeConfig`. Supporting multiple themes would require:
- A theme context provider wrapping the entire component tree
- Per-component theme-aware style resolution
- A persistence layer for user theme preferences

This is a significant architectural change that doesn't align with the project's focus on content authoring. Theming is a concern for downstream consumers who embed or redistribute the output.

```ts
// The current ThemeConfig interface is not designed for runtime switching:
interface ThemeConfig {
  colors: ColorPalette; // single palette, resolved at build time
  fonts: FontStack;
}
```

## Prior requests

- #42: "Add dark mode support"
- #87: "Night theme for accessibility"
- #134: "Dark theme option"
```

### Writing the reason
Substantive, not "we don't want this". Good reasons reference project scope/philosophy ("This project focuses on X; theming is downstream"), technical constraints ("would require Y, conflicting with Z architecture"), or strategic decisions. **Durable**: avoid temporary circumstances ("too busy right now") — those are deferrals, not rejections.

## When to check
During triage (gather context), read all `.out-of-scope/*.md`. Match by **concept similarity**, not keyword: "night theme" matches `dark-mode.md`. On a match, surface it: "This resembles `.out-of-scope/dark-mode.md` — we rejected this before because [reason]. Do you still feel the same way?" The maintainer then confirms (append to Prior requests + close), reconsiders (delete/update file; issue proceeds normally), or disagrees (related but distinct; proceed normally).

## When to write
Only when an **enhancement** (not a bug) is rejected as `wontfix` — including enhancement PRs, so the same request doesn't return as fresh code. Do **NOT** write here for already-implemented closures: that's a built feature, not a rejection; recording it poisons dedup with false rejections. Instead point to where the feature lives.

Flow: maintainer decides out of scope → check for existing matching file → append issue link if yes / create new file (concept name, decision, reason, first prior request) if no → comment on the issue explaining + mentioning the file → close with `wontfix`.

## Updating or removing
If the maintainer changes their mind: delete the `.out-of-scope/` file. No need to reopen old issues — they're historical records. The triggering new issue proceeds through normal triage.
