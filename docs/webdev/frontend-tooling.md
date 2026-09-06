---
description: "nicegui / Front-End-Checklist MCP / HTMLHint / dashy — frontend tooling reference from starred clones"
source_repos: zauberzeug/nicegui, FrontendChecklist/Front-End-Checklist (monorepo), HTMLHint/HTMLHint, lissy93/dashy
tested_version: clones @ 2026-09-05; nicegui ui.run() signature read from source this pass
verified_date: "2026-09-06"
---

# Frontend Tooling (round-2 deep dive)

## nicegui — `ui.run()` full parameter list [SRC, verified from source]
`nicegui/ui_run.py`, main branch as of 2026-09-05. **33 named parameters** (the "71 params" figure in earlier notes was wrong):

```
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

## HTMLHint — 34 built-in lint rules [SRC]
`lib/rules/`: alt-require, attr-lowercase, attr-no-duplication, attr-sorted, doctype-first/html5, empty-tag-not-self-closed, head-script-disabled, href-abs-or-rel, html-lang-require, id-class-ad-disabled, id-unique, inline-script/style-disabled, input-requires-label, script-disabled, spec-char-escape, tag-pair/self-close/name-lowercase, title-require, ...
Useful as a **rule vocabulary** when writing custom HTML linting for the audit pipeline — each rule is one small module with `test`/`fix` hooks.

## dashy — self-hosted dashboard [SRC]
Single-service docker-compose at repo root; config schema in `config.schema.json`. Relevant only if the user wants a personal ops dashboard (links, health checks) — not part of any current pipeline.

## gods-eye-view (creative reference) [SRC]
Cesium-based satellite/ADS-B visualization app: deps = @mapbox/vector-tile, cesium, egm96-universal, mgrs, pbf, satellite.js. `src/` layout worth copying for any Cesium project: `annotations/`, `data/adsbLolFallback/`, **`overlays/` (Web Worker)**, `scenes/director+recipes/`, `styles/{anime,noir,retro,snow,surveillance,thermal}/`, `voice/`. Notable discipline: **100% of modules have a `.test.mjs` sibling** — the bar for "done" in that repo is tested.
