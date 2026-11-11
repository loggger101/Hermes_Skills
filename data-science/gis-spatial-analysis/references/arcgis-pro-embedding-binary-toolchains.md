# Embedding an external binary toolchain inside ArcGIS Pro (verified from opengeos/WhiteboxTools-ArcGIS @ main, 2026-11-11)

Source: read this pass from the live tree + the shipped generator/wrapper file itself
(`WBT/PRE/WhiteboxTools.py`, **1.46 MB**, and `WhiteboxTools.pyt`; repo also carries
`whitebox_tools.exe` + per-tool plugin `.exe`s under `WBT/plugins/`). ArcGIS Pro is licensed software so
nothing was executed here — everything below is read from shipped source, which for a *layout/pattern*
claim is the right evidence class. MIT (opengeos).

## 1. The scale trick: 554 generated tool classes, none hand-written

`grep -c "^class .*object:" = 554`. Each WhiteboxTools tool becomes one ArcToolbox **tool class** with
the standard four-method `.pyt` protocol (`getParameterInfo / updateParameters / updateMessages / execute`), a
label+description+category in `__init__`, and typed `arcpy.Parameter`s (`datatype="GPRasterLayer"`,
`parameterType="Required"`) — all emitted from the tool metadata list (the file literally builds
`tool_labels.append(...)` for every tool, then class-per-tool). The toolbox **categories mirror the upstream
taxonomy** ("Hydrological Analysis", "Math and Stats Tools"), so 500+ tools stay navigable.

Transferable: when wrapping a large CLI surface into any UI/agent schema (MCP server with hundreds of
tools, skill pack generated from an API spec), generate per-item classes from the machine-readable tool
list — including each item's own category field for grouping — rather than curating entries; curation at
that scale is where wrappers rot. Same discipline as pstack `statechart` generating views from IR, and our
own index generators (`gen-*-index.py`) doing it for docs.

## 2. The binary-resolution idiom (the actual Pro-specific trap)

Every execute path resolves the executable **relative to the wrapper file**, never CWD or PATH:

```python
dir_path = os.path.dirname(os.path.realpath(__file__))
exe_path = os.path.join(dir_path, "WBT/whitebox_tools.exe")
cmd = '{} --run={} {}'.format(exe_path, tool_name, args)
messages.addMessage(cmd)                      # the command itself goes to the toolbox log
messages.addMessage(os.popen(cmd).read().rstrip())   # stdout -> toolbox Messages pane
```

Why it matters specifically in ArcGIS Pro: a `.pyt` runs with **Pro's process CWD**, not the toolbox's — any
relative path or PATH-dependent lookup breaks depending on how Pro was launched. `__file__`-anchored,
self-contained bin+plugins (the per-tool plugin exes sit next to the main exe so it finds them) is the
correct shape for ANY "ship binaries inside a host app's extension dir" task — QGIS plugins and VS Code
extension bundles have the identical constraint.

Honest weaknesses of this shipping implementation (don't copy these parts): `os.popen` drops stderr into
whichever stream isn't captured, no exit-code check at all (a failed tool prints nothing to Messages and
still "succeeds" in the toolbox), and unquoted f-string command assembly breaks on spaces in Windows paths.
A hardened wrapper would use `subprocess.run(..., capture_output=True)`, check returncode, fail the ArcToolbox
tool explicitly, and quote args — three defects visible in five lines that our own binary-embedding skills
should gate against.

## 3. Version-straddling caveat (ties to what this catalog already holds live)

This toolbox wraps **WhiteboxTools v1-era exes** vendored in-repo; the current pip route (`whitebox`
2.3.x → WhiteboxTools v2.4.0, measured elsewhere in `gis-spatial-analysis`: instance API only — no
module-level tool functions — with a non-interactive first-use binary auto-download) is the maintained
line. So: same underlying engine, two distributions with **different tool-name surfaces** (v1 exes expose
per-plugin executables; v2 exposes 575 snake_case methods and some plural renames). If embedding for Pro,
decide which generation to wrap deliberately — a name list copied between generations silently misses or
misnames tools. And per the existing note: expect a network fetch on first `WhiteboxTools()` instantiation
in CI/sandboxes; vendoring exes (this repo's choice) trades that download for Windows-only + repo weight.
