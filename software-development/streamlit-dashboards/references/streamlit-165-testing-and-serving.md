---
description: "Streamlit 1.65.0 run on Python 3.14: browserless AppTest (0.24 s), cache hits, st.stop, exceptions; removed experimental APIs; use_container_width notice; headless server binds ALL interfaces by default"
source_repo: streamlit/streamlit (Apache-2.0); contribution policy from its CONTRIBUTING.md
tested_version: "streamlit 1.65.0 + pandas 3.0.6 + numpy 2.5.3 in a uv Python 3.14 venv on Windows 11 (install 4 s). AppTest script of about 15 interactions, a headless server started three times with curl, no browser. Components, auth, multipage navigation, st.connection and deployment were not exercised"
verified_date: "2026-10-05"
---

# Streamlit 1.65: testing without a browser, and serving safely

## Test the app with `AppTest` (run)

```python
from streamlit.testing.v1 import AppTest
at = AppTest.from_string(APP_SOURCE, default_timeout=10)    # or AppTest.from_file("app.py")
at.run()
at.text_input[0].set_value("Ann").run()        # widgets are found by type and index, or at.text_input(key="name")
at.button[0].click().run()
assert at.metric[0].value == "6" and len(at.exception) == 0
```

| Check | Observed |
|---|---|
| First run of a small app (title, text input, number input, button, `cache_data` function, metric) | **0.24 s**; later reruns about 0.00-0.01 s; no server, no browser |
| After `set_value("Ann")` | `at.markdown` values `['hello Ann x3 go=0', 'end']` |
| `button.click().run()` twice | counter `go=1` then `go=2`: each click triggers exactly one rerun and the button resets |
| `st.cache_data` function | body ran **once** across repeated runs with `n=3`; changing to `n=7` ran it again (metric `'14'`, 2 calls); back to `n=3` was a **cache hit** (metric `'6'`, still 2 calls) |
| App raising `ValueError("boom")` | captured: `len(at.exception) == 1`, `at.exception[0].value` starts `boom`; the traceback is also printed to stderr by the script runner |
| `st.stop()` | later output (`end`) absent, no exception |
| Value reading | `at.session_state["calls"]` works; `at.metric[0].value` is the displayed **string** (`'6'`), not a number |
| Noise | `missing ScriptRunContext! This warning can be ignored when running in bare mode.` appears on stderr |

So agents can regression-test dashboards in CI exactly like functions: assert on `at.markdown`, `at.metric`, `at.dataframe`, `at.exception`,
`at.session_state`. Keep browser tests for layout, JS components and real network behaviour.

## API removals and notices

- **Absent in 1.65.0**: `st.experimental_rerun`, `st.experimental_memo`, `st.experimental_singleton`, `st.cache`, `st.beta_columns`,
  `st.experimental_get_query_params`. Use `st.rerun`, `st.cache_data` / `st.cache_resource`, `st.columns`, `st.query_params`.
- **`use_container_width=True`** (on `st.dataframe`, `st.button`) still ran without an exception but logged
  `Please replace use_container_width with width ... will be removed after 2025-12-31 ... use width='stretch'` (`width='content'` for False).
  The stated removal date has already passed and 1.65.0 still accepts it; migrate anyway, it will go.

## Serving: the default listens on every interface (run)

```bash
streamlit run app.py --server.headless true --server.port 8599 --browser.gatherUsageStats false
```

- Health endpoint `GET /_stcore/health` returned `ok` (HTTP 200) about **1 s** after start; `GET /` 200 text/html (6.5 KB); `GET /_stcore/host-config` 200.
- The startup banner lists **Local, Network and External URLs** and the log says `Uvicorn server started on :::8599` (all interfaces). A request to the
  machine's **LAN address returned 200**, so the app is reachable by other hosts on the network by default.
- `--server.address 127.0.0.1` fixes that: log `Uvicorn server started on 127.0.0.1:8602`, localhost 200, LAN address connection failed (`000`).
- Telemetry: pass `--browser.gatherUsageStats false` (or set `STREAMLIT_BROWSER_GATHER_USAGE_STATS=false`) in unattended runs.

For any dashboard started by an agent or cron job: bind to `127.0.0.1` unless you mean to publish it, put authentication in front of anything else,
and never serve data you would not post on the LAN.

## Contributing

Per its `CONTRIBUTING.md` (see `github/github-pr-workflow/references/ai-policies-of-starred-repos.md`), outside pull requests are **paused** because AI tools
raised volume beyond what maintainers can review; contribute through detailed issues with a minimal reproducible app and version info.

Not run: `st.navigation` multipage apps, `st.connection`, custom components, authentication, Docker deployment, `AppTest` on `st.dataframe` / chart contents, or performance under load.
