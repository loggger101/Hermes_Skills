# e2e (tester-army/e2e): agent-step tests with a replay cache

Source: [tester-army/e2e](https://github.com/tester-army/e2e) (Apache-2.0, 4.2k stars, pre-1.0: APIs may change between
minors). npm `e2e` **0.17.0** plus `@e2e-dev/web` installed into a scratchpad on Windows (Python 3.14.6 box, Node project).
Everything marked *(live)* was run here; everything marked *(docs)* is from the package's shipped `docs/*.mdx`
(`node_modules/e2e/docs`) and was not exercised, because no model key was configured.

## What it is

A TypeScript test runner (`*.e2e.ts`) where one test mixes exact Playwright-style steps with natural-language agent steps:

```ts
import { test, expect } from 'e2e';
test('a member upgrades to Pro', async ({ app, agent, screen }) => {
  await app.open('/settings/billing');
  await agent.act('upgrade the workspace to the Pro plan');   // model drives the UI
  await expect(screen.getByRole('status')).toContainText('Pro'); // exact check, no model
});
```

Fixtures: `app` (open/URL), `screen` (role/name locators over an accessibility snapshot), `agent`
(`act`, `assert`, `waitFor`, `extract`), `browser` (web-only, import `test` from `@e2e-dev/web`). A test that takes
only `app` can `fetch` an API and `expect` on it. Engines: `@e2e-dev/web` (Chromium/Firefox/WebKit via Playwright),
`@e2e-dev/mobile` (iOS/Android through agent-device), hosted-browser and GitHub-comment reporters.

Use it when the UI is the contract and selectors churn; use plain Playwright/Selenium (this skill's main body) when every
step is deterministic and no model should sit in the loop. Tests with no `agent.*` call need no model at all *(live)*.

## Model-free smoke path that works on Windows *(live)*

```bash
npm i e2e @e2e-dev/web            # package.json needs "type": "module"
npx e2e run                        # first run downloads Chrome Headless Shell (~115 MiB) + winldd into %LOCALAPPDATA%\ms-playwright
```

`e2e.config.ts`: `targets: [{ engine: web(), app: { url, command: { executable, args, log } } }]`. With
`app.command` the runner spawns the server, waits until the URL answers, and stops it (a `python -m http.server 8123
--directory site` was enough). First-run "prepared 31.9s / command ready 15.3s" was the browser download; the next runs
took 317-563 ms of startup. Pin the install as its own CI step: `npx @e2e-dev/web install chromium --with-deps`.

A passing test printed `✓ button click 1.75s`, exit **0**, report `.e2e/report.json`.

## Behaviours recorded *(live)*

| Probe | Result |
|---|---|
| Planted wrong `toHaveText('Wrong')` | exit **1**, `ASSERTION_FAILED` with `locator`, `expected`, `observed: text "Clicked" (match count 1)` |
| Failure evidence on disk | `.e2e/artifacts/web/<test>/default/attempt-0/failure/screen.txt` (accessibility tree: `#n18 button "Go" [focused]`), `screenshots/001-failure.png`, `trace/trace.zip` |
| `agent.act` with no model configured | **whole run interrupted**, `MODEL_UNAVAILABLE`, exit 2; the *other* test in the file shows `skipped [run interrupted before execution]`. A missing key hides unrelated results, so run `--grep` for the model-free tests |
| Passing run artifacts | essentially none kept (1 file) |
| `--grep zzz` (no match) | exit **2** `NO_TESTS`; `--pass-with-no-tests` makes it 0 |
| Unknown flag (`-g`, `--no-such`) | exit 2; use `--grep <regex>`, `--tag`, `file:line` |
| `e2e list` | prints `file › title [target]` without running |
| `npx` noise | npm 11 prints `npm notice run <pkg>@<ver> npx` on every call; filter it before parsing output |

Exit classes *(docs, errors reference)*: test 1, configuration 2, infrastructure 3, internal 4, interrupted 130. So a CI
gate can tell "app is broken" (1) from "key missing / app did not start" (2/3).

## The replay cache *(docs; `cache ls` live: empty without a model)*

After an `agent.act` is followed by a **verification** that passes, the actions are recorded under `.e2e/cache/`; the next
run replays them with zero model calls and falls back to the agent only if the screen no longer matches.
`agent.assert/waitFor/extract` always run live. Run summary: `4 replayed · 1 handed off · 1 missed`.

- Verification that counts: locator matchers (`toHaveText`, ...), engine assertions (`toHaveURL`), `locator.waitFor`,
  `agent.assert/waitFor`. Does **not** count: `expect(plainValue).toBe`, `expect.poll`, `textContent()` reads,
  `agent.extract`, another `act`. An `act` that is never checked is never cached; follow every `act` with a check.
- Cache key: test, target, instruction, params, agent (and its `context`), engine major.minor. Changing the model does
  **not** miss. Run with `--no-cache` first when a failure might be cache-related.
- Anything unique per run (timestamp, fresh email) must be wrapped `unique(value)` in `params` or every run misses.
- Route identity: origin + path + query; ids, tokens, timestamps in path or query are placeholders; other query values
  and tracking params make a different screen. Set `app.identity` so preview deployments share a cache.
- Reasons in `step.cache.reason`: `no-entry`, `wrong-context` (opened a different screen), `target-not-found`
  (15 s), `target-ambiguous` (repeated unnamed controls: give them names), `gap` (values the agent read off the screen,
  minted tokens, dates, pixels cannot replay), `end-mismatch` (leftover data, a banner, or a real regression).
- Modes: `read-write` locally, `read-only` in CI when unset (CI never records unless `cache: 'read-write'`).
  `--strict-cache` turns a stale recording into `REPLAY_STALE` instead of silently handing it back to the model:
  use it in CI to catch UI drift without paying for it.
- Entries hold typed values verbatim (secrets only by name): review before committing `.e2e/cache/`; `init` gitignores it.
- A run where no model answered (`MODEL_UNAVAILABLE`, provider 5xx/429/missing key) keeps existing recordings;
  a wrong-shaped answer or a timeout counts as a flow failure and evicts implicated entries.

## Agent-step budget and safety *(docs)*

The model sees a redacted text snapshot (roles, names, states; password fields masked, configured secrets shown as
`<secret:name>`), not HTML, cookies or headers. After 3 consecutive failed actions it is told to change approach,
after 5 to give a verdict. Verdicts: `passed`, `failed` (`ASSERTION_INCONCLUSIVE` when evidence is insufficient),
`blocked` (environment/seed/auth/automation, classed so exit codes stay honest). A targeted action times out at
15 s. `vision: true` adds a masked screenshot; no screenshot is sent after a secret fill. Use `Secret`/`credentials`
for passwords, never `params`.

## CI recipe *(docs)*

Install browsers, `npx e2e run --reporter list,junit`, upload `.e2e/report.json`, `.e2e/junit.xml` and `.e2e/artifacts`
on `!cancelled()` (so a test that failed then passed on retry keeps its evidence). `CI=1 npx e2e run` reproduces CI
defaults locally. App startup failures (`APP_UNREACHABLE`) appear in a `run` suite of the JUnit file. Model credentials
come from `AI_GATEWAY_API_KEY` (AI SDK `gateway()`), a subscription login (`e2e login`), or any AI SDK model, including a
local one.

## For coding agents *(docs + live)*

`e2e init` writes `.agents/skills/e2e/` (symlinked to `.claude/skills/e2e/`) and registers `e2e mcp` in `.mcp.json`;
`npx e2e guide [topic]` prints the same skill from the installed package, and `node_modules/e2e/docs` holds every page
offline: read those before writing a test rather than guessing the API. The MCP `locate` tool returns test code only when
exactly one element matches, a good guard against ambiguous locators. `e2e explore '<goal>'` runs the agent against the
app with no test file and reports findings (uses the model; does not use the cache).

## Pitfalls

- Treating a passing agent test as proof: pair `act` with a locator assertion, since `agent.assert` is another model
  judgment and the cache only records after a deterministic or verified check.
- A test that edits shared data re-runs against leftovers: use `unique()` data and clean up in `afterEach`, or replays end
  in `end-mismatch`.
- Telemetry is on by default (commands/engines/failure points, no test content): `E2E_TELEMETRY_DISABLED=1` in locked-down environments.
- Not run here: any `agent.*` step, replay, `e2e explore`, mobile engines, hosted browsers, the GitHub reporter.
