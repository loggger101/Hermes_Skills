---
description: "Prefect 3.8.7 run locally: ephemeral-server cost (13 s cold, ~1 s per flow), retries, INPUTS caching, parameter validation, failure behaviour, PREFECT_HOME, plus its AGENTS.md rules"
source_repo: PrefectHQ/prefect (Apache-2.0)
tested_version: "prefect 3.8.7 (released 2026-09-26) in a uv Python 3.14 venv on Windows 11, installed in about 11 s; PREFECT_HOME pointed at a scratch folder; every behaviour below was one run of the script, not a benchmark. No server, worker, deployment, schedule or UI was started"
verified_date: "2026-10-05"
---

# Prefect 3 (3.8.7), measured locally

`data-engineering-tool-map.md` lists Prefect as the Python-first orchestration step up (`>=3.10,<3.15`). Python 3.14 is
inside that range and installs cleanly. What running flows without a server actually looks like:

## Costs and files (run)

| Item | Result |
|---|---|
| `import prefect` | 2.1 s |
| First flow run in an empty `PREFECT_HOME` | **13.2 s** (starts the ephemeral API and creates the SQLite database) |
| Every later flow run, even a flow that adds two numbers | **about 1.05 s** (ephemeral API round trips) |
| A `@task` called directly, outside any flow | 0.03 s and just returns the value |
| `PREFECT_HOME` after the run | `prefect.db` (+ `-shm`/`-wal`), `memo_store.toml`, `storage/<uuid>` result files. **Default location is `~/.prefect`**: set `PREFECT_HOME` for experiments or tests so a throwaway run does not write into the profile |

So Prefect is for jobs that last minutes, not for wrapping a millisecond function: a 1 s tax per flow call dominates small work.

## Behaviours (run)

| Case | Result |
|---|---|
| `@task(retries=2, retry_delay_seconds=0)` on a function that fails twice | succeeded on the third attempt (3 calls, final value returned) |
| `@task(cache_policy=INPUTS, cache_expiration=timedelta(minutes=5))`, called with 21, 21, 22 | body ran **2** times; results `[42, 42, 44]` |
| `add.submit(i, i)` x3 then `.result()` | `[0, 2, 4]` |
| Flow parameter `n: int` given `'5'` | coerced to 5 |
| Flow parameter `n: int` given `'abc'` | **`ParameterTypeError`** ("Flow run received invalid parameters") raised to the caller; an ERROR log precedes it |
| A task that raises inside a flow | the **original** `ValueError` propagates out of the flow call (not wrapped); the flow run is recorded as failed |
| `task(return_state=True)` / `flow(return_state=True)` | returns the state object instead of raising: `state.type.value == 'FAILED'`, `is_failed() is True` |

Noise: even with `PREFECT_LOGGING_LEVEL=WARNING` a failing task prints a full traceback twice (task run and flow run) plus
the "Finished in state Failed" line. Capture or filter stderr in agent runs, and use `return_state=True` when you want to
branch on failure without a traceback.

## Prefect's own `AGENTS.md` (source-read)

- Read `docs/contribute/dev-contribute.mdx` first; the root `AGENTS.md` is a map to per-folder `AGENTS.md` files
  (`src/prefect/`, `tests/`, `docs/`, `ui-v2/`, integrations, `formal/tla/`).
- **Use `uv` for everything; never `pip install` or `uv pip`**, no deferred (in-function) imports unless breaking a cycle or for
  an optional dependency, never commit to `main`, never `--no-verify`, never `--amend`.
- Flow state transitions always go through the server's orchestration API, even in tests; task transitions are local.
- Check the profile (`prefect config view`) and have a server (`prefect server start`) before running tests that need one.
- Repro scripts go in `repros/<issue-number>.py` (one per issue, gitignored); add a unit test with every fix.
- No public API change without approval; TLA+ models under `formal/tla/<protocol>/` are for interleaving-sensitive protocols.
- `REVIEW.md`: review on two independent axes (repository **standards** and issue **spec**), cite the instruction file or the
  requirement for each finding, skip what linters catch.
- AI policy (`dev-contribute.mdx`, "Using AI tools responsibly"): AI use is allowed as a starting point, not as evidence of
  correctness; maintainers may close issues or PRs that look low-effort, unverified, AI-generated without concrete detail or
  far from the expected implementation, whether or not AI was used. See also
  `github/agent-oss-contributions/references/ai-policies-of-starred-repos.md`.

Not run: `prefect server start`, deployments and workers, schedules, work pools, blocks, automations, the UI,
`flow.serve()`, task runners other than the default, async flows, and the `prefect-client` package.

## Returned-Failed retries were silently stranded before 3.9.1 (added r294, source-derived)

**The behaviour gap.** A flow that *returns* a `Failed` state object instead of raising it did not
rely on anything exotic - but with `retries=N`, prefect <= 3.9.0 never retried: the run ended in
status **`AwaitingRetry`**, and nothing ever picked it up again. Silent non-retry, no error line.

**Mechanism (from merged fix PR text).** The server policy `RetryFailedFlows` did propose a retry -
it turned the proposed `Failed` into `AwaitingRetry` with `retry_type="in_process"`. But only
`handle_exception` / `handle_timeout` in the engine recognised that signal and looped back to
`Running`; **`handle_success` (sync and async) did not**, so when a flow *returned* failure the
engine loop exited, leaving the run parked in `AwaitingRetry` - and workers skip `in_process` runs,
so no scheduler ever resumed it. Fix: `handle_success` now applies the same check as the other two
handlers (`terminal_state.is_failed() and state.is_scheduled()`), resets `_return_value` to `NotSet`,
sets `Running`, returns early (skipping success telemetry/result linking). Resetting `_return_value`
matters because a stale return value otherwise survives into the retry.

**Versions.** Bug report [#23534](https://github.com/PrefectHQ/prefect/issues/23534); fix PR
[#23535](https://github.com/PrefectHQ/prefect/pull/23535) merged 2026-10-23 (merge commit
`b79132f125`). `3.9.1.dev*` builds began the same day, so **affected: <= 3.9.0; first stable with
the fix: >= 3.9.1** - which is this skill's tested pin line. Practical audit rule when upgrading
from <= 3.9.0: any flow that returns state objects (rather than raising) and relies on `retries`
was silently not retrying before the upgrade; after it, those flows start actually looping - budget
for that side effect.

**Evidence tier + local measurement note.** Claims above derive from upstream issue/PR text, not a
local A/B: this machine could not boot prefect's ephemeral API server on fresh Python 3.14 venvs of
either version (both died with `RuntimeError: Timed out while attempting to connect to ephemeral
Prefect API server`, uvicorn startup failing - environment-specific, likely localhost-port or
first-run-DB interaction; earlier r279 measurements ran fine in the then-current setup). The half-install
incident during that diagnosis is separately documented in
`software-development/python-toolchain-notes/references/uv-killed-install-recovery.md`.

Still not run: everything in the paragraph above - this section adds knowledge from upstream, not new execution.

