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
