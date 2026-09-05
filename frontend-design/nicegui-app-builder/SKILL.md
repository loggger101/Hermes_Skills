---
name: nicegui-app-builder
description: "Build Python reactive web/desktop apps with NiceGUI."
version: v0.9.0
author: Hermes Agent (ported from starred-repo research)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [nicegui, python-ui, fastapi, dashboards]
    related_skills: [streamlit-dashboards]
---


<!-- source: zauberzeug/nicegui starred repo deep-dive 2026-09-05; API verified from source clone -->
## When to Use

- When working on: Build Python reactive web/desktop apps with NiceGUI.

## What This Skill Does

```python from nicegui import ui


# NiceGUI App Builder

NiceGUI = reactive UI in plain Python on FastAPI + Vue. Elements are declared as functions (`ui.button`, `ui.table`...), state syncs via bindings, and the whole app runs with one `ui.run()` call.

## Minimal skeleton (verified pattern)
```python
from nicegui import ui

counter = 0

def increment():
    global counter
    counter += 1
    label.set_text(f'Count: {counter}')   # or bind element to a property

label = ui.label('Count: 0')
ui.button('Increment', on_click=increment)
ui.run(title='My App', port=8080, reload=True)
```

## `ui.run()` parameter map (verified from nicegui/ui_run.py:50 — v3.x signature)
| Param | Default | Use when |
|---|---|---|
| `host` / `port` | None/None | binding to LAN or specific port |
| `title`, `viewport`, `favicon` | 'NiceGUI'... | branding |
| `dark` | False | dark theme default |
| `native` | **False** | True = desktop window via pywebview (no browser) |
| `window_size`, `fullscreen`, `frameless` | None/False/False | native-window geometry |
| `tailwind` / `unocss` | True / None | CSS engine; unocss='mini'\|'wind3'\|'wind4' |
| `storage_secret` | None | **required** for encrypted session storage (`app.storage.user/session`) |
| `fastapi_docs` | False | expose Swagger UI at /docs |
| `reload` + `uvicorn_reload_includes/excludes` | True, '*.py', '.*...' | dev hot-reload scoping |
| `binding_refresh_interval` | 0.1s | polling cadence for bound values |
| `reconnect_timeout`, `message_history_length` | 3.0 / 1000 | websocket resilience |
| `on_air` | None | AirPlay-style screen casting of the UI |

## Multi-page & structure (from examples/modularization + single_page_app)
- **Pages**: `@ui.page('/path')` decorator on a function; kwargs pass through to FastAPI's @app.get. SPA mode: one page with sub-pages (`examples/single_page_app/custom_sub_pages.py`).
- **Modularization patterns** (all in examples/modularization/): api_router_example.py (FastAPI APIRouter for backend endpoints), class_example.py, function_example.py — plus theme.py for shared theming and menu.py.
- **Auth**: examples/authentication + descope_auth + google_oauth2 + google_one_tap; use `app.storage.user` with a storage_secret set.

## Example index by need (59 apps in examples/)
| Need | Look at |
|---|---|
| Chat / AI chat UI | chat_app, chat_with_ai, ai_interface |
| Data tables | editable_table, editable_ag_grid |
| Scheduling/calendar | fullcalendar |
| PDF output | generate_pdf |
| Long lists | infinite_scroll |
| Background work | global_worker (workers survive page reloads) |
| 3D / media | 3d_scene, audio_recorder, ffmpeg_extract_images |
| File download UX | download_text_as_file |
| Custom Vue component interop | custom_vue_component, image_mask_overlay |

## Testing pattern (verified: examples/todo_list/test_todo_list.py + pytest.ini)
NiceGUI apps are testable with pytest — the in-repo todo_list example ships `test_todo_list.py`. Pattern: import the app module, use NiceGUI's testing utilities to simulate user events against elements; assert **observable behavior** (element text/state), never internal element wiring.

## Project conventions worth copying from nicegui/AGENTS.md
- Requirements first: verify requirements before implementing, especially tests.
- Research before guessing: search the codebase for similar patterns before inventing APIs.
- No global mutable state in library-style modules; no unnecessary dependencies (check existing code suffices).
- **Reflexive regression test warning**: not every bug fix earns a test; assert observable behavior, not internals — no private attributes, no patched machinery. If you're building scaffolding to observe an internal mechanism, stop and find the user-visible effect instead. Before writing a test, read a recent one in the same file and copy its shape.

## Gotchas
- `ui.run()` args mostly apply only after full restart — not with auto-reload (per docstring).
- Storage without `storage_secret` = unencrypted; set it before using app.storage.user for anything sensitive.
- Native mode (`native=True`) needs pywebview installed and a display server; headless CI → use browser/websocket testing instead.
