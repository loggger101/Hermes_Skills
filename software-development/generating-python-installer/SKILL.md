---
name: generating-python-installer
description: "Nuitka + Inno Setup: smallest, fastest Windows installers."
version: v0.1.0
author: Hermes Agent (ported from starred-repo research)
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [packaging, nuitka, inno-setup, windows-installer, python-deployment, dll-analysis]
    related_skills: [modern-python-tooling, test-driven-development]
---

<!-- source: affaan-m/ECC (MIT), ported 2026-09-09; Chinese original translated to English with all commands/flags preserved verbatim -->
# Generating Python Installers (Commercial Grade)

Ship the **smallest, fastest-starting, cleanest** Windows installer for a Python app. Core approach: **"Nuitka standalone folder mode (`dist`) + Inno Setup packaging"** — no single-file builds, no stray console window.

## What This Skill Does

- Compiles with Nuitka using module-exclusion and anti-bloat strategies tuned from a production PySide2/OpenCV/Playwright build (323 MB reference case)
- Slims the `dist` folder: debug symbols, type stubs, caches, test/doc dirs, install-time metadata — each step size-reported so nothing is silently lost
- Analyzes DLL footprint and flags optimization opportunities per dependency family
- Packages with Inno Setup 6.x: LZMA2/ultra compression, full metadata, residue-free uninstall, arch-matched VC++ redistributable

## When to Use

Activate when the user asks for **advanced** Python packaging or size/startup optimization on Windows: "Nuitka extreme / commercial-grade build", "smallest installer", "fastest startup", "my exe is 400 MB — halve it". Not for basic one-file script-to-exe conversion.

## Workflow (strict)

1. **Confirm build parameters** — app name, version, publisher, exe name, source/output dirs, icon. Never auto-fill; ask the user one by one.
2. **Verify the source build** before generating anything: console disabled (`--windows-console-mode=disable`), LTO enabled (`--lto=yes`), VC++ runtime present in `dist`. Inno Setup only packages — it cannot fix a bad compile.
3. **Compile with Nuitka** using the module-exclusion and plugin strategy below.
4. **Slim the `dist` folder** via `scripts/slim_dist.ps1` (7 passes, each size-reported).
5. **Analyze DLLs** via `scripts/analyze_dlls.py <dist-dir>` to find and trim the largest dependencies.
6. **Package with Inno Setup** using the template below — LZMA2 ultra compression, full metadata, residue-free uninstall, arch-matched VC++ redistributable.

## 32-bit vs 64-bit Strategy

| Component | 64-bit size | 32-bit size | Saving |
|-----------|------------|------------|--------|
| python3x.dll | ~4.5 MB | ~3.8 MB | 15% |
| Qt5Core.dll | ~8 MB | ~5 MB | 37% |
| numpy | ~30 MB | ~20 MB | 33% |
| **Total** | baseline | **-20~30%** | - |

Choose 32-bit when: memory footprint < 2 GB, no files > 2 GB processed, target users are ordinary office machines.

```bat
:: install 32-bit Python (coexists with 64-bit), then build with it
py -3.12-32 -m pip install -r requirements.txt
py -3.12-32 -m nuitka --standalone ...your flags...
```

## Module Exclusion List (production-verified)

Safe to exclude at runtime — saves **30–50 MB**:

```
unittest,test,pytest,_pytest,doctest,pdb,pdbpp,
setuptools,pip,distutils,pkg_resources,
email.mime,http.server,xmlrpc,pydoc
```

## GUI Framework Recipes

### Tkinter (lightest) — expect 80–120 MB after optimization

```bat
nuitka --standalone --windows-console-mode=disable ^
    --lto=yes --jobs=8 ^
    --enable-plugin=tk-inter --enable-plugin=anti-bloat ^
    --noinclude-pytest-mode=nofollow --noinclude-setuptools-mode=nofollow ^
    --nofollow-import-to=unittest,test,pytest,_pytest,doctest,pdb,pdbpp ^
    --nofollow-import-to=setuptools,pip,distutils,pkg_resources ^
    --nofollow-import-to=email.mime,http.server,xmlrpc,pydoc ^
    --python-flag=no_docstrings ^
    --output-dir=dist --windows-icon-from-ico=icon.ico --remove-output main.py
```

### PyQt5 / PySide2 — expect 120–250 MB after optimization

Same as above with `--enable-plugin=pyqt5` added, plus:

```bat
    --nofollow-import-to=PyQt5.QtWebEngine,PyQt5.QtWebEngineWidgets ^
    --nofollow-import-to=PyQt5.Qt3D,PyQt5.QtCharts ^
    --include-qt-plugins=sensible,styles,platforms
```

## Bundled Scripts

| Script | Purpose |
|--------|---------|
| `scripts/build_optimized.bat` | One-shot: clean → Nuitka compile (auto-detected CPU cores) → size report → run slim script. Edit the 3 config vars at top (`APP_NAME`, `MAIN_FILE`, `ICON_FILE`). Uses `%NUMBER_OF_PROCESSORS%` — NOT wmic, which Windows 11 22H2+ removed; a failed probe would silently compile single-threaded with `--jobs=0`. |
| `scripts/slim_dist.ps1 <dist-dir>` | 7-pass dist slimming: `.pdb`, `.pyi`, `__pycache__`, test dirs, docs/examples dirs, `.pyc`, install-time metadata. Keeps `METADATA` and `entry_points.txt` inside `*.dist-info` (read at runtime by `importlib.metadata`; deleting them breaks plugin discovery). `$ErrorActionPreference = "Continue"` so a failed deletion is visible instead of masquerading as success. |
| `scripts/analyze_dlls.py <dist-dir>` | DLL footprint report: total count/size, >3 MB offenders with per-family optimization suggestions (OpenBLAS/MKL, OpenCV→headless, Qt module exclusion, software-GL removal), debug-suffix (`*d.dll`) detection, VC++ runtime inventory, top-20 table. Stdlib only — run `py analyze_dlls.py dist\YourApp.dist`. |

## VC++ Runtime Handling

**Option A (recommended): static link** — `nuitka --static-libpython=yes ...`

**Option B: bundle the redistributable** (commercial release). Architecture MUST match the Python/Nuitka build arch. This skill recommends 32-bit, so default to `vc_redist.x86.exe`; switch both spots to `vc_redist.x64.exe` for a 64-bit build.

```iss
[Files]
Source: "{#MySourceDir}\..\vc_redist.x86.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Run]
Filename: "{tmp}\vc_redist.x86.exe"; Parameters: "/quiet /norestart"; StatusMsg: "Installing runtime..."; Flags: waituntilterminated
```

Download: [Microsoft Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)

## Inno Setup Template (Commercial Grade, 6.x)

```iss
; =====================================================================
; Commercial-grade Python installer (Inno Setup 6.x)
; LZMA2 ultra compression | full metadata | residue-free uninstall
; Reference: production build, 323 MB pre-compression with LZMA2
; =====================================================================

#define MyAppName        "{{APP_NAME}}"
#define MyAppVersion     "{{APP_VERSION}}"
#define MyAppPublisher   "{{PUBLISHER}}"
#define MyAppURL         "{{APP_URL}}"
#define MyAppExeName     "{{EXE_NAME}}"
#define MySourceDir      "{{SOURCE_DIR}}"
#define MyOutputDir      "{{OUTPUT_DIR}}"
;#define MyIconPath      "{{ICON_PATH}}"

[Setup]
AppId={{GENERATE_RANDOM_GUID}}          ; Inno Setup: Tools > Generate GUID — must be unique per app
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableDirPage=no
DisableProgramGroupPage=no
PrivilegesRequired=admin

OutputDir={#MyOutputDir}
OutputBaseFilename=Setup_{#MyAppName}_v{#MyAppVersion}

WizardStyle=modern
#ifdef MyIconPath
SetupIconFile={#MyIconPath}
UninstallDisplayIcon={app}\{#MyAppExeName}
#endif

; Core compression (reference build)
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes

; Architecture: only set this for 64-bit Python builds. For the recommended
; 32-bit build keep it commented so the app installs as 32-bit and matches
; the bundled vc_redist.x86.exe above. Uncomment ONLY when compiling with
; 64-bit Python.
;ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "{#MySourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs exclude "_nuitka_temp.exe"

[UninstallDelete]
Type: filesandordirs; Name: "{app}\*"

[Icons]
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
```

## Placeholder Reference

| Placeholder | Meaning | Example |
|-------------|---------|---------|
| `{{APP_NAME}}` | Display name | `RedInk` |
| `{{APP_VERSION}}` | Semver | `1.0.0` |
| `{{PUBLISHER}}` | Company (Control Panel) | `MyCompany` |
| `{{APP_URL}}` | Website | `https://example.com` |
| `{{EXE_NAME}}` | Main executable | `RedInk.exe` |
| `{{SOURCE_DIR}}` | Nuitka dist folder | `D:\project\dist\RedInk.dist` |
| `{{OUTPUT_DIR}}` | Installer output dir | `D:\project\output` |
| `{{ICON_PATH}}` | .ico file (optional) | `D:\project\icon.ico` |
| `{{GENERATE_RANDOM_GUID}}` | **Generate a unique GUID** — Inno Setup "Tools > Generate GUID" | - |

## FAQ

- **"Installed but double-click does nothing"** → run the exe from CMD to see the error; check VC++ runtime presence; confirm Nuitka compiled with `--standalone`.
- **Installer too big?** → 32-bit Python (-20–30%), module exclusion list, anti-bloat plugin, dist slimming script, DLL analysis. In order of effort.
- **Antivirus false positives** → submit to AV vendors for whitelisting; buy a code-signing certificate (Sectigo, DigiCert); avoid UPX compression entirely — it shrinks further but triggers false-positive reports at high rates.
- **"Windows protected your PC"** → an EV code-signing certificate earns trust immediately; ordinary certificates accumulate trust with install volume over time.

## Field Notes (production incidents)

- **Missing `python3xx.dll` after install** → must use Nuitka `--standalone`; confirm the dll exists in dist; never ship single-file builds.
- **GUI unresponsive on launch** → heavy dependencies block startup; defer their import to first action ("start export"); add logging to diagnose.
- **Nuitka + MinGW fails on non-ASCII paths** → copy sources into an ASCII path and compile there; set `PYTHONIOENCODING=utf-8`.
- **Inno Setup warns `x64` deprecated** (only relevant when a 64-bit build needs 64-bit install mode) → use `ArchitecturesInstallIn64BitMode=x64compatible`; not needed for 32-bit builds.
- **`--disable-console` is deprecated** → use `--windows-console-mode=disable`.
- **`_nuitka_temp.exe` appears in dist** → exclude it in `[Files]` (template does this).

## Expected Optimization Impact

| Combination | Size reduction | Startup improvement | Risk |
|-------------|---------------|--------------------:|------|
| Baseline compile | - | - | none |
| + `--lto=yes` | 5–10% | 10–20% | none |
| + anti-bloat plugin | 15–25% | - | none |
| + module exclusion | 20–35% | ~5% | none |
| + dist slimming | 25–40% | - | none |
| + 32-bit build | 40–60% | - | none |
| **All combined** | **45–65%** | **15–25%** | **none** |

> Do NOT use UPX compression: it shrinks further but triggers antivirus false-positive reports at high rates.

## Reference Case (production PySide2 desktop app)

323 MB total with OpenCV + Playwright, Python 3.8 32-bit, 71 DLLs / 93.23 MB: playwright 76.74 MB (drop if unused), OpenCV 62.38 MB (switch to `opencv-python-headless`), PySide2 22.52 MB (exclude WebEngine/3D/Charts). Verified strategies: 32-bit Python (-20–30%), compressed stdlib zip, module exclusion list, Qt plugin pruning.
