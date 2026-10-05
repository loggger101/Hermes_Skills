# Bun 1.4.2 on Windows: runtime, package manager, test runner, bundler (run live)

Source: [oven-sh/bun](https://github.com/oven-sh/bun) (MIT, v1.4.2 released 2026-09-05). Installed through npm into a scratch
directory, driven by one Python script that ran about 40 commands in a scratch project (Windows x64, Node 22.23.2 on PATH for
comparison). Each line is an observed result. Not covered: `bun --watch`/`--hot`, Workers, WebSocket servers, macOS/Linux
differences, Next.js/Vite under Bun.

## Getting the binary (npm 11 trap)

`npm i bun` printed `install-scripts ... 1 package had install scripts blocked because they are not covered by allowScripts`,
and `node_modules/.bin/bun` then failed with **`Error: Bun's postinstall script was not run`**. `npm install-scripts approve bun`
only records `"allowScripts": {"bun@1.4.2": true}` in `package.json`; the binary arrives after **`npm rebuild bun`**, which copied
an 86,096,984-byte `bun.exe` (and `bunx.exe`) into `node_modules/bun/bin/`. `bun --version` -> `1.4.2`. Other installers (the official script, `winget`) were not tried here.

## Runtime

| Probe | Result |
|---|---|
| `bun run a.ts` | TypeScript runs directly (0.08 s); `import.meta.dir`/`.file` work |
| `const y: string = 5` | runs and prints `5`: **no type checking**; keep `tsc --noEmit` in CI |
| syntax error, missing file | exit 1: `error: Expected identifier but found "(" at ...:1:10`, `error: Module not found "nope.ts"` |
| `process.exit(7)`, unhandled `Promise.reject` | exit 7, exit 1 (stack with source excerpt) |
| `process.versions` | `bun 1.4.2`, **`node: 26.3.0`** (the Node version it claims to be compatible with; not the Node on PATH), JSC (`webkit`) id `2e2aa229` |
| `.env` | auto-loaded (`FOO=from_env`), quoted values unquoted (`a b`), `${FOO}_x` expanded (`from_env_x`); a variable set in the shell **wins** over `.env` |
| `bun run hi` for a package script | prints `$ echo hello-script` before the output |
| node compatibility | `node:fs`, `node:path` (`\` sep on win32), `node:os`, `node:child_process` (`execSync`), `node:crypto` md5, `worker_threads`, `vm`, `cluster`, `structuredClone`, `AbortSignal.timeout`, `WebSocket` all present |
| startup, `console.log('hi')` x10 | **bun 54 ms vs node 116 ms** average; `fib(35)` 124 ms vs 127 ms (no CPU advantage on this loop) |

## Bun APIs

One script printed: `bun:sqlite` in-memory db with a parameterised insert/select (**SQLite 3.53.2**); `Bun.write`/`Bun.file`
(`size 7`, `text/plain;charset=utf-8`); `Bun.serve({port: 0, fetch})` answered `200 {"path":"/hi"}` with a numeric `srv.port`;
`` Bun.$`echo shell-ok`.text() `` -> `"shell-ok\n"` (the cross-platform shell works on Windows); `Bun.hash("a")` returns a **BigInt**
(`2941419223392617777n`); `new Bun.CryptoHasher("sha256")`; `Bun.password.hash` -> argon2; `Bun.semver.satisfies("1.2.3","^1.0.0")`
true; `typeof Bun.YAML` `object`; `Bun.Glob` a function.
**`Bun.write("tmp.txt", "héllo\n")` wrote a bare LF** (last bytes `111, 10`), unlike Python's `write_text` on Windows, which writes
CRLF. Byte-for-byte output is predictable in Bun.

## Package manager

- `bun add is-odd@3.0.1`: **0.39 s**, created **`bun.lock` (text)**, no `bun.lockb`; `package.json` gained `"is-odd": "3.0.1"`
  (exact, no caret, when the version was given on the command line); `node_modules` held `is-number` and `is-odd`.
- Delete `node_modules`, `bun install --frozen-lockfile`: 62 ms (`2 packages installed`); re-run: `Checked 2 installs across 3 packages (no changes)`.
- `bun pm cache` -> `C:\Users\Loggg\.bun\install\cache` (a global cache outside the project; mind it when sandboxing).
- **Auto-install**: with no `node_modules`, `bun --install=force -e "import ms from 'ms'; console.log(ms('2 days'))"` printed
  `172800000` after fetching in 0.34 s. `bunx`-style one-off: `bun x --bun semver 1.2.3 -i patch` -> `1.2.4`.
- Every command prints `[0.4ms] ".env"` timing lines when a `.env` is present (noise when parsing output).
- `bun outdated` with nothing outdated printed only its header.

## `bun test` (Jest-compatible, built in)

A file with `describe/test/expect/mock`, `test.skip`, `test.todo`, an async test, `toMatchSnapshot` and `test.each` ran in ~30 ms and
reported ` 6 pass / 1 skip / 1 todo / 1 fail / 1 snapshots, 8 expect() calls / Ran 9 tests across 1 file`; the failure shows a
unified diff (`- Expected - 1 / + Received + 1`) with the source line and caret. Files are discovered by name only
(`.test`, `_test_`, `.spec`, `_spec_`). Exit codes: **1** on a failure and **also 1 when a name filter matches no file**
(`The following filters did not match any test files`; `--pass-with-no-tests` makes it 0). Snapshots went to
`__snapshots__\math.test.ts.snap`; `--reporter=junit --reporter-outfile=out.xml` wrote the file. Flags seen in `--help`:
`--timeout` (default 5000 ms), `-u/--update-snapshots`, `--rerun-each`, `--only`, `--todo`, `--concurrent`, `--randomize`,
`-t/--test-name-pattern`, `--only-failures`, `--bail`, `--coverage` (a coverage table was not visible in my captured non-tty
output, unverified).

## Bundler and single-file executables

`bun build entry.ts --outdir dist` -> `Bundled 2 modules in 59ms`, `entry.js 62 bytes`; `bun dist/entry.js` printed `bundled 42`.
**`bun build entry.ts --compile --outfile app.exe`** took 0.72 s and produced an **86.1 MB** `app.exe` that ran standalone and
printed `bundled 42` (exit 0): the runtime is embedded, so a trivial program is 86 MB.

## When to pick it

Good for fast scripts, TypeScript without a build step, `bun test` without Jest/ts-jest, and one-file tools; check that any native
Node addons in your tree work before switching, and keep a type-check step. Pin the version in CI (`bun@1.4.2`); `process.versions.node` reports a Node release other than the one on PATH, so feature checks should
test for the API, not the version string.
