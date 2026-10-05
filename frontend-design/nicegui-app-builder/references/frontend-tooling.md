---
description: "nicegui / Front-End-Checklist MCP / HTMLHint (44 rules, only 10 default, run) / dashy — frontend tooling reference from starred clones"
source_repos: zauberzeug/nicegui, FrontendChecklist/Front-End-Checklist (monorepo), HTMLHint/HTMLHint, lissy93/dashy
tested_version: clones @ 2026-09-05; nicegui ui.run() signature read from source; htmlhint 1.9.2 run via npm on 2026-10-05 (the rest remains source-read)
verified_date: "2026-10-05"
---

# Frontend Tooling (round-2 deep dive)

## nicegui — `ui.run()` full parameter list [SRC, verified from source]

`nicegui/ui_run.py`, main branch as of 2026-09-05. **33 named parameters** (the "71 params" figure in earlier notes was wrong):

```text
root, host, port, title, viewport, favicon, dark, language, binding_refresh_interval,
reconnect_timeout, message_history_length, cache_control_directives, gzip_middleware_factory,
fastapi_docs, show, on_air, native, window_size, fullscreen, frameless, reload,
uvicorn_logging_level, uvicorn_reload_dirs, uvicorn_reload_includes, uvicorn_reload_excludes,
tailwind, unocss, prod_js, endpoint_documentation, storage_secret, session_middleware_kwargs,
show_welcome_message, markdown
```

The ones that matter for this stack:

- **`native=True`** → pywebview desktop window (pairs with the nicegui-app-builder skill's native mode).
- **`storage_secret=...`** — REQUIRED to use `app.storage.user/secret` encrypted storage; without it those raise.
- **`on_air=True`** — remote access via NiceGUI Air (no tunnel setup needed for demos).
- `reload=` + the three `uvicorn_reload_*` knobs control dev hot-reload scope precisely.
- `show_welcome_message=False` silences the first-run banner in production.

## Front-End-Checklist — QA rules as a machine-consumable MCP server [SRC]

The repo is a monorepo; **the interesting part is `packages/mcp/`** (`@repo/mcp`) with deps:
`@frontendchecklist/rules`, `node-html-parser`, `zod`, `@modelcontextprotocol/sdk`.
Meaning: the entire checklist (a11y, performance, SEO, best practices) ships as **structured rules an agent can query and apply**, not just a human-readable list. If you want automated frontend QA in an agent workflow, this is the reference implementation — point any MCP-capable agent at it instead of re-encoding the rules by hand.

## HTMLHint — 44 built-in lint rules, only 10 on by default [SRC + RUN 2026-10-05]

`lib/rules/`: alt-require, attr-lowercase, attr-no-duplication, attr-sorted, doctype-first/html5, empty-tag-not-self-closed, head-script-disabled, href-abs-or-rel, html-lang-require, id-class-ad-disabled, id-unique, inline-script/style-disabled, input-requires-label, script-disabled, spec-char-escape, tag-pair/self-close/name-lowercase, title-require, ...
Useful as a **rule vocabulary** when writing custom HTML linting for the audit pipeline — each rule is one small module with `test`/`fix` hooks.
**Run (htmlhint 1.9.2, `npm i htmlhint`, Node 22).**

- `npx htmlhint --list` prints **44** rules; the earlier "34" was out of date.
- With no config the CLI applies a **default ruleset of 10**: `tagname-lowercase, attr-lowercase, attr-value-double-quotes,
  doctype-first, tag-pair, spec-char-escape, id-unique, src-not-empty, attr-no-duplication, title-require`.
- A planted-defect page (uppercase tag, duplicate attribute and id, single-quoted value, unclosed `<p>`, empty `src`, no
  doctype or title, plus inline style, a head script, an obsolete `<center>`, a button without type, an unlabeled input, an
  `<a href="">`) produced **8 errors by default and 22 with an extended config** (the default rules plus alt-require,
  attr-value-not-empty, button-type-require, head-script-disabled, inline-style-disabled, inline-script-disabled,
  input-requires-label, tag-no-obsolete, attr-value-no-duplication, h1-require, html-lang-require, meta-viewport-require,
  meta-charset-require, main-require, empty-tag-not-self-closed).
- The default run passes inline style, `<center>`, a head `<script>`, a missing `alt`, an unlabeled input and a button without `type`.
- Exit code is **1** when errors exist. `--format json` gives `[{file, messages[{type, message, line, col, evidence, rule{id, description, link}}]}]`.
- A `.htmlhintrc` in the working directory was applied to a file in a subfolder. A directory or glob argument scanned only the
  project's own files (not `node_modules`).
- In the extended run `inline-script-disabled` did not flag the inline `<script>var x=1;</script>` element (`head-script-disabled`
  did); it was not tested against `onclick` attributes. No rule tested flagged `<a href="">`.
- Enable the rules you need explicitly in `.htmlhintrc` rather than trusting the default pass.

## dashy — self-hosted dashboard [SRC + schema RUN 2026-10-05]

Single-service docker-compose at repo root. Relevant only if the user wants a personal ops dashboard (links, health checks) — not part of any current pipeline.
(MIT. The config schema is `src/utils/config/ConfigSchema.json`, 64 KB; the older note naming `config.schema.json` was wrong. Docs: `docs/configuring.md`,
47 KB, with sections `pageInfo`, `appConfig`, `appConfig.auth` (built-in users, Keycloak, header, OIDC), `sections[]`, `items`, widgets, `displayData`.)

**Validating a `conf.yml` offline (run, `jsonschema` + `pyyaml`).** The schema is JSON Schema draft-07 with `required: ["sections"]`
and `additionalProperties: false` at the root, where only keys matching `^x-` are allowed as custom extensions. The repo's own
`user-data/conf.yml` validates with no errors. Planted mistakes:

| Mistake | Result |
|---|---|
| `pageinfo` instead of `pageInfo`; `section` instead of `sections` | caught (key not matching `^x-`; `sections` required) |
| `appConfig.theme: 123`, `statusCheck: 'yes'`, `displayData.cols: 'two'` | caught (type errors) |
| `appConfig.layout: 'diagonal'` | caught (enum: horizontal, vertical, auto, masonry, sidebar) |
| unknown `appConfig` key `statuscheck` | caught (additional properties not allowed) |
| item without `title`; `pageInfo` without `title` | caught (required) |
| **item without `url`** | **not caught** (zero errors) |
| **`item.target: 'newwindow'`** | **not caught** (any string accepted) |

So the schema is good for typos and types and silent on semantic gaps. Put `# yaml-language-server: $schema=<ConfigSchema.json URL>`
on the first line (the sample does) for editor checks, and validate with the schema before restarting the container. Dashy
was not run (no Docker or build); the app's behaviour is not verified here.

## gods-eye-view (creative reference) [SRC]

Cesium-based satellite/ADS-B visualization app: deps = @mapbox/vector-tile, cesium, egm96-universal, mgrs, pbf, satellite.js. `src/` layout worth copying for any Cesium project: `annotations/`, `data/adsbLolFallback/`, **`overlays/` (Web Worker)**, `scenes/director+recipes/`, `styles/{anime,noir,retro,snow,surveillance,thermal}/`, `voice/`. Notable discipline: **100% of modules have a `.test.mjs` sibling** — the bar for "done" in that repo is tested.
