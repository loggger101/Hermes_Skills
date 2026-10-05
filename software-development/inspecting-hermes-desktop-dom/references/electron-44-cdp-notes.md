# Electron 44.5.1: driving a stock app over CDP, security defaults, install quirks (run live on Windows 11)

Source: [electron/electron](https://github.com/electron/electron) (123k stars, MIT). npm `electron` **44.5.1** =
**Chromium 152.0.7977.130, Node 24.21.0, V8 15.2.124.28** (read from `/json/version` and
`ELECTRON_RUN_AS_NODE=1 electron.exe -e "process.versions"`). A three-file probe app (main, preload, `data:` page) launched from the
scratchpad with `show: false`; the CDP client was Node 22.23.2's built-in `WebSocket`. Not covered: packaged builds and
fuses (source-read only), auto-update, native modules, Playwright's `_electron.launch`, macOS/Linux.

This is the generic counterpart to `SKILL.md` (which is about attaching to Hermes' own dev server on 9222): everything below works on any
Electron app you can launch.

## Install and launch quirks

- `npm install electron --prefix DIR` finishes in ~6 s with **no binary** (`node_modules/electron/` has no `dist/` or `path.txt`);
  `npm rebuild electron` does nothing either. The binary is fetched **lazily on first run** (`electron --version` printed
  `Downloading Electron binary...` and took ~7 s) or by running `node node_modules/electron/install.js` (15 s). `dist/` is
  **368 MB**, so scratch installs belong in a scratch/temp directory, not a repo.
- `electron.exe` at `node_modules/electron/dist/electron.exe`; `node_modules/.bin/electron` is the shim. An app is a
  folder with `package.json` (`"main"`) run as `electron .`; `process.defaultApp` is `true` and `app.isPackaged` is `false` then.
- **`ELECTRON_RUN_AS_NODE=1 electron.exe script.js`** turns the binary into plain Node 24.21.0 (no Chromium, no `electron` module);
  useful for running a script with the exact Node/V8 the app ships.
- A run starts several `electron.exe` processes (main, GPU, renderer, utility). To clean up a hung one on Windows:
  `Get-Process electron | Stop-Process -Force`.

## Security defaults (read from `getLastWebPreferences()`, then tested from the page)

A `BrowserWindow` with only a `preload` set reported `contextIsolation: true`, `nodeIntegration: false`, **`sandbox: true`**,
`webSecurity: true`, `nodeIntegrationInWorker: false`, `allowRunningInsecureContent: false`, `webviewTag: false`. In the page
`typeof require` and `typeof process` were `undefined`.

- The **sandboxed preload cannot `require` Node built-ins**: `fs`, `path`, `os`, `child_process` all threw
  `module not found: <name>`; only `electron` (a reduced module in the sandbox) loaded. `process.type` is
  `renderer`, `process.sandboxed` is `true`. Anything needing the filesystem must go through `ipcRenderer.invoke` to the main process.
- `contextBridge.exposeInMainWorld('bridge', { ping, obj, leak })` appeared on `window.bridge` with `Object.keys` =
  `ping, obj, leak` (functions stay functions, values are cloned). A preload value computed with `process.versions.electron` reached the page as a plain
  string: **anything you put on the bridge is readable by the page**, so never expose a raw `ipcRenderer` or secrets.
- User agent: `... probe-app/1.0.0 Chrome/152.0.7977.130 Electron/44.5.1 Safari/537.36`: the app's `package.json` name and version
  are in it, which sites and scripts can sniff.

## Debug ports (both worked on an app that did nothing special)

| Flag | Target | Evidence |
|---|---|---|
| `electron --remote-debugging-port=9334 .` (or `app.commandLine.appendSwitch('remote-debugging-port', '9333')` before `ready`) | renderer pages, Chromium CDP 1.3 | `http://127.0.0.1:PORT/json/version` returned `Chrome/152...`; `/json/list` listed the page with its `webSocketDebuggerUrl`, `title`, `url`; stderr printed `DevTools listening on ws://...` |
| `electron --inspect=9230 .` | **main process**, Node inspector (`node.js/v24.21.0`, protocol 1.1) | `/json/version`, `/json/list` showed `node.js instance`; stderr `Debugger listening on ws://127.0.0.1:9230/<uuid>` |

Both bind 127.0.0.1. Over the page WebSocket these calls returned real values: `Runtime.evaluate` (computed `color`
`rgb(255, 0, 0)`, `font-size` `40px`, `innerWidth` 487), `DOM.getDocument` (root nodeId 1), and `Runtime.evaluate typeof require` = `undefined`.
Pattern: `fetch('/json/list')`, pick `type === 'page'`, `new WebSocket(webSocketDebuggerUrl)`, send `{id, method, params}` JSON, match replies by `id`.
Packaged apps may refuse these flags (an Electron fuse can disable `--inspect`); not tested here.

## Screenshots did not work in this session

With `show: false` on this machine (`app.getGPUFeatureStatus().gpu_compositing` = `disabled_software`):

- CDP `Page.captureScreenshot` produced **no reply within 5 s** (the same session answered `Runtime.evaluate` and `DOM.getDocument` at once).
- `webContents.capturePage()` **rejected with `UnknownVizError`**, both before showing and after `showInactive()` of a window placed at
  x/y -32000 (Electron clamped the bounds to -26214, so the window stayed "visible" but off screen).

So for facts (styles, geometry, text, console) use CDP evaluation; for "what does it look like" do not rely on
hidden-window screenshots: show the window on a real desktop session or have the user look. This matches the existing rule that CDP
answers factual questions only. The cause (software GPU, hidden window, or this session) was not isolated.

## Other facts from the run

- `app.requestSingleInstanceLock()` returned `true` on first launch; `app.getName()`/`getVersion()` come from `package.json`.
- `show: false` windows are still listed by `/json/list` and evaluate JS normally.
- In `data:` pages the title comes from `<title>`; the preload result was readable from `document.title` after `DOMContentLoaded`
  (a handy way to hand preload diagnostics to the CDP client without IPC).
