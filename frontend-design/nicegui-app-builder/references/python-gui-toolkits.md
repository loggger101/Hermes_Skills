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
| Touch/multitouch apps, one codebase for desktop plus Android/iOS | **Kivy** (below) | OpenGL ES 2.0, KV layout language, property-bound UI |
| Game window or simulation | pygame (`pygame` skill) | |
| Packaging a desktop app to an installer | `generating-python-installer` | Tkinter/PyQt size guidance there |

| Quick tkinter-based desktop forms and tools, minimal code | **PySimpleGUI 6** (below) or the FreeSimpleGUI fork | thin layer over tkinter (also Qt/wx/Remi backends in older releases) |

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

## Kivy 2.3.1

MIT, Python plus Cython on OpenGL ES 2.0; targets Windows, macOS, Linux (including Raspberry Pi), Android and iOS from one codebase, with multitouch in every widget.
UI is built from Python widgets and/or the **KV language** (declarative rules with property bindings).

**Install reality (verified):** PyPI `kivy` 2.3.1 ships wheels for CPython 3.8 to 3.13 (Windows amd64, macOS universal2, manylinux x86_64/aarch64) and **no cp314 wheel**. On Python 3.14.6,
`pip install kivy` falls back to the 24 MB sdist and fails at "Installing build dependencies" (the build pins `setuptools~=69.2.0`). Use a 3.13 or earlier venv:
`uv venv --python 3.11 kvenv` then `uv pip install --python kvenv/Scripts/python.exe kivy` installed it cleanly (61 MB venv).

Headless checks run on Python 3.11.16 / Windows (no window opened; `KIVY_NO_ARGS=1`, `KIVY_NO_CONSOLELOG=1`, `KIVY_NO_FILELOG=1` set before importing kivy):

- **Properties are the core.** `NumericProperty`, `StringProperty`, `ListProperty` on an `EventDispatcher` fire bound observers on change: `count = 3` fired once and setting `3` again fired nothing; `items.append(1)` and `items = [1, 2]` each fired. Wrong types raise `ValueError` (`'x'` into a `NumericProperty`: "could not convert string to float"; `5` into a `StringProperty`: "Model.name accept only str").
- **Undeclared attributes are not properties**: `m.oops = 1` worked but is not observable; declare the property or nothing will react.
- **KV rules** create and re-evaluate bound expressions: `double: self.value * 2` gave 2, then 10 after `value = 5`.
- `Clock.schedule_once` / `schedule_interval` run on `Clock.tick()` (three ticks produced `['once', 'tick', 'tick', 'tick']`), which makes UI logic testable without a window.
- A widget tree works without a window (`BoxLayout` with two children, default size `[100, 100]`); a `Label` created with no window returned `texture_size` `[0, 0]` and no error, so text metrics are only meaningful with a live GL context.
- Not run: the window, rendering, touch input, and Android/iOS packaging (buildozer / python-for-android).

Kivy writes a log directory on first import unless `KIVY_NO_FILELOG` is set; set the env variables above in tests and CI so imports do not parse `sys.argv` or create files.

## PySimpleGUI (licensing history matters)

PySimpleGUI is a thin declarative layer over tkinter (windows are lists of element rows plus an event loop). Its licensing history is the thing to know before choosing a version, from the project's own README and PyPI:

| Era | Status |
|---|---|
| 4.x (to 4.60.5.1) | LGPL open source; older pin still installable with `pip install PySimpleGUI==4.60.5.1` |
| 5.x | commercialised: licence keys and registration; the company (PySimpleSoft) announced shutdown in Feb 2025 |
| **6.x (current: 6.3.0.1, PyPI 2026-08-16, repo pushed 2026-08-30)** | released as open source again, **LGPL-3.0**, "after removing licensing and security components"; `pip install PySimpleGUI` now gives this |
| Fork | `FreeSimpleGUI` 5.3.0.post1 (2026-08-27, LGPL), a community continuation of the 4.60 line; `PySimpleGUI-4-foss` 4.60.4.1 (2024-02) is an older copy |

Checked here (Windows, Python 3.14.6): `import PySimpleGUI` worked, `sg.version` = `6.3.0.1`, Tk 8.6, 160 built-in themes, and the module exposes no licence or registration functions (only `upgrade_PySimpleGUI_gui` / GitHub upgrade helpers),
consistent with the README. No window was created. Tutorials from 2022-2024 target 4.x/5.x APIs and a licence flow that no longer exists.

Guidance: pin the exact version in `requirements.txt` (the project's own history shows why), prefer 6.x or FreeSimpleGUI for new work, check the LGPL terms if you ship a bundled executable (see `generating-python-installer`), and for anything web-served or multi-user prefer NiceGUI.
