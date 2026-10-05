---
description: "Choosing a Python GUI toolkit (NiceGUI, Streamlit, Dear PyGui, plus others as reviewed) with Dear PyGui 2.3.1 run live: crash-on-no-context and duplicate-tag behaviour"
source_repo: hoffstadt/DearPyGui (MIT); other toolkits added as their starred repos are reviewed
tested_version: dearpygui 2.3.1 pip --target, Windows py3.14, headless item-API probe only (no viewport shown, no rendering)
verified_date: "2026-10-05"
---

# Python GUI toolkits: which one

| Need | Pick | Why |
|---|---|---|
| Web-served UI in pure Python, forms, dashboards, multi-user | NiceGUI (`nicegui-app-builder`) | runs in the browser, Tailwind/Quasar widgets, FastAPI underneath |
| Quick data app or report from a script | Streamlit (`streamlit-dashboards`) | rerun-on-interaction model, minimal code |
| Desktop tool with fast immediate-mode rendering, live plots, node editors, dev/debug panels | **Dear PyGui** (below) | GPU-rendered, claims 1M+ points at 60 fps in plots, built-in node editor and demo |
| Game window or simulation | pygame (`pygame` skill) | |
| Packaging a desktop app to an installer | `generating-python-installer` | Tkinter/PyQt size guidance there |

Kivy and PySimpleGUI are added here when their rows in the starred-repos review are done.

## Dear PyGui 2.3.1

MIT, GPU-rendered (Dear ImGui + ImPlot under a Python API). PyPI `dearpygui` 2.3.1 has a cp314 Windows wheel (installed fine). Features per its README:
theme and style control, plots (over a million data points at 60 fps), node editor, built-in demo (`dearpygui.demo`), developer tools (item inspector, metrics, debugger),
Windows/Linux/macOS. Python 3.10+ per the project's PyPI classifiers (not re-checked).

```python
import dearpygui.dearpygui as dpg
dpg.create_context()                                   # FIRST: every other call needs it
with dpg.window(label="Main", tag="main", width=300, height=200):
    dpg.add_input_text(tag="name", default_value="abc")
    dpg.add_button(label="go", tag="btn", callback=lambda sender, app_data, user_data: print(sender, app_data, user_data), user_data="U")
dpg.create_viewport(title="t", width=320, height=240)
dpg.setup_dearpygui(); dpg.show_viewport(); dpg.start_dearpygui(); dpg.destroy_context()
```

Items are addressed by integer id or a string **tag** (alias). Callbacks receive `(sender, app_data, user_data)`.

### Verified in a headless item-API probe (no window shown)

- `get_value("name")` returned `'abc'` and `get_value` of a slider returned `0.5`; `set_value` took effect; a line series' value came back as five lists (`[[0,1,2],[0,1,4],[],[],[]]`).
- **Any DPG call outside `create_context()` ... `destroy_context()` kills the interpreter with a segmentation fault (exit code 139), not an exception.** Reproduced two ways: `dpg.get_dearpygui_version()` before `create_context()`, and `dpg.add_window(...)` after `destroy_context()`. Nothing is printed, so a "silent crash" with no traceback usually means a call ran with no live context. In a test harness, run each case in a subprocess.
- **A duplicate tag raises `SystemError: <built-in function add_button> returned a result with an exception set`** (an unhelpful message), and in the same run the original item's tag then failed to resolve (`Error: [1005] ... Item not found` from `get_item_type`, `configure_item`, `get_item_callback`) even though the item still appeared among its parent's children. Treat a duplicate-tag error as corrupting that alias: generate unique tags (prefix with the owning panel) and never retry an `add_*` call with the same tag.
- `does_item_exist("nope")` returns `False` cleanly; missing-item errors from other calls are plain `Exception` carrying a bracketed code (`[1005]`).
- `create_viewport` without `show_viewport` returned `None` and `is_dearpygui_running()` stayed `False`.

Not tested here: actual rendering, callbacks firing, threading (callbacks run off the main thread per the docs: use thread-safe updates), and screenshots (`output_frame_buffer` needs a shown viewport).

## Rules of thumb

- Build the UI inside `with dpg.window(...)` context managers; keep tags unique and namespaced.
- Keep heavy work off the render thread; DPG is immediate-mode, so a slow callback stalls the frame.
- For tests, isolate DPG in a subprocess (crashes are process-level) and assert on `get_value`/`does_item_exist` rather than pixels.
