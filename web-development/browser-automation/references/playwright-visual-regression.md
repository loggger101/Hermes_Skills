---
description: "Playwright screenshot (visual regression) suites: per-platform baselines, first-run and update-snapshots behavior, one-assert-per-test, file-level sharding, patterns from Ionic's e2e suite"
source_repo: ionic-team/ionic-framework (MIT)
tested_version: "@playwright/test 1.63.0 on Windows 11, Edge channel; Ionic docs and playwright.config.ts read via GitHub API (main, 2026-10-05)"
verified_date: "2026-10-05"
---

# Playwright visual-regression suites (lessons from Ionic's e2e setup)

Ionic Framework runs 400+ Playwright files with screenshot assertions across three mobile browsers, two
modes and two text directions. Its `docs/core/testing/` guides are a worked answer to "how do you keep a
screenshot suite from lying". The behaviours below marked **run** were reproduced here with
`@playwright/test` 1.63.0 on Windows (Edge via `channel: 'msedge'`, no browser download); items marked
**source-read** come from Ionic's docs and config and were not executed.

## 1. Baselines are per platform, so "green locally" proves little (run)

Playwright appends project and OS to the baseline name: `a-Edge-win32.png` here, `button-expand-md-ltr-Mobile-Chrome-linux.png`
in Ionic. A baseline made on Windows is a different file from the one CI (Linux) reads.

| Situation | Observed |
|---|---|
| No baseline, default mode (`missing`) | Test **fails once**, but writes the baseline for **every** `toHaveScreenshot` in the test, not just the first |
| Re-run, nothing changed | Passes, against the baseline just written |
| `--update-snapshots=none`, no baseline | Fails with `A snapshot doesn't exist at ...` and writes **nothing** |
| `--update-snapshots` (bare flag, preset `changed`) with a real mismatch | Prints `is re-generated, writing actual`, **overwrites the baseline, reports the test passed, exit 0** |

Consequences:

- A screenshot test run natively on a different OS than CI writes a local baseline, fails once, then passes forever
  against a file CI never sees. Ionic gitignores every non-`-linux` baseline for exactly this reason and tells
  contributors to run screenshot tests in Docker (`npm run test.e2e.docker`) so the platform matches CI.
- On CI use `--update-snapshots=none` so a missing baseline is a hard failure instead of a quiet self-heal.
- Never reproduce a flaky screenshot with the update command: the mismatch is overwritten and the run goes green
  with no diff images (Ionic's docs carry the same warning for `test.e2e.docker.update-snapshots`). Check
  `git status` for modified `.png` files after any update run.
- Baseline updates belong in the CI environment (Ionic uses a manually dispatched "update reference screenshots"
  workflow that pushes one commit to the branch) or the same container image, never a developer laptop.

## 2. One `toHaveScreenshot` per test (run)

A failed hard assertion ends the test. With two screenshots in one test and **both** changed, the report named
only the first (`a-Edge-win32.png`); the second was never compared and no `b-actual.png` or diff was produced. An
intentional visual change then needs one run per screenshot to see everything.

Two fixes, both run:

- Give each screenshot its own `test()` (Ionic's rule). Failures name the state that changed.
- If the screenshots share expensive setup, use `expect.soft(...)`: with the same two changed elements the report
  listed **both** mismatches (`a` and `b`) in one run and the test still failed.

## 3. Playwright shards by file, not by test (run)

Two files of four tests each, `--workers=4`, default (not `fullyParallel`): every test of file A ran on worker 0
and every test of file B on worker 1. With `--fully-parallel` the eight tests spread over all four workers. So:

- One slow file serialises its tests and sets the wall-clock floor for the whole run. Split slow files (Ionic's
  rule: "break up large or slow-running tests across multiple files").
- The same holds for `--shard=i/n` on CI: it splits by file. Ionic runs 20 shards.
- Setting `fullyParallel: true` is the alternative, at the price of no shared state between tests in a file.

## 4. Patterns worth copying (source-read)

- **A project-owned `test` fixture that waits for the app.** Ionic's docs: importing `test` straight from
  `@playwright/test` "will likely" give blank screenshots, because the custom fixture waits for the Stencil app to
  hydrate before the test body runs (it overrides `page.goto`/`page.setContent` and adds `waitForChanges`,
  `spyOnEvent`, `setIonViewport`). For any web-component or SPA suite: wrap `page` once, never wait ad hoc per test.
- **Generate matrix variants outside `test.describe`.** `configs().forEach(({ config, title }) => test.describe(title('x'), ...))`
  creates one `beforeEach` per describe; putting `forEach` inside the describe creates N `beforeEach` hooks that
  all run for every test. Unique titles per variant are mandatory (Playwright derives test ids from them), hence the
  `title()` and `screenshot()` helpers that append mode/direction.
- **Screenshots are for appearance, not behaviour.** Assert `toBeVisible`, emitted events or DOM state for
  functionality; keep rendering and behaviour tests in separate `describe` blocks (rendering needs the full
  mode x direction matrix, behaviour usually does not).
- **Do not compare computed pixel values** across browsers; let a screenshot catch layout drift.
- **Isolate the subject.** Unrelated styled components in a screenshot make every test that includes them fail
  when those components change. Use a plain native element for filler.
- **Pin locale-dependent output** (`locale="en-US"` on a datetime) because CI and the laptop differ.
- **Start from the final layout** (scroll target already in view): a `scrollIntoViewIfNeeded` costs ~300 ms on CI,
  multiplied by every variant.
- **Mobile viewports by default, tablet on purpose.** Their projects are Pixel 5 / iPhone 12 / a Firefox project with
  a hand-set 393x727 viewport, because `isMobile` is not supported on Firefox. Tablet-only layouts set the viewport
  in the test.
- **CI settings** (their `playwright.config.ts`): `forbidOnly: !!process.env.CI` (a stray `test.only` fails the
  build), `retries: 2` on CI, `trace: 'retain-on-failure'`, `toHaveScreenshot.threshold: 0.1`, and a `webServer`
  with `reuseExistingServer: !process.env.CI`. Debug flakes with `--repeat-each=10`, not by re-running once.
- A `basic/index.html` page per component exists purely so reviewers can paste a repro into a ready harness.

## 5. Windows gotcha: cloning the repo (observed)

`git clone --depth 1` of ionic-framework into a deep scratch path on Windows failed with hundreds of
`unable to create file ...-Mobile-Chrome-linux.png: Filename too long` errors: the committed ground truths have
long names (`accordion-basic-ios-ltr-Mobile-Chrome-linux.png` under `...e2e.ts-snapshots/`). Read such repos
through `gh api repos/OWNER/NAME/git/trees/HEAD?recursive=1` and `contents/...`, or clone to a short path (for example
`C:\w`) with `git -c core.longpaths=true clone`. The `core.longpaths` fix was not tried here.

## Reproduce the run checks

```bash
npm i -D @playwright/test        # 1.63.0 when checked; browsers: use channel 'msedge'/'chrome' to skip the download
# playwright.config.js: projects: [{ name: 'Edge', use: { channel: 'msedge' } }]
# test: await expect(page.locator('#a')).toHaveScreenshot('a.png');   # twice, with two different elements
npx playwright test                           # fails once, writes both baselines
npx playwright test                           # passes
npx playwright test --update-snapshots=none   # missing baseline -> hard fail, nothing written
```
