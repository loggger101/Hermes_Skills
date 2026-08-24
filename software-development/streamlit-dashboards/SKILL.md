---
name: streamlit-dashboards
description: "Streamlit dashboards: layout, caching, charts, state."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [streamlit, dashboards, data-viz, python, caching, state-management, plotly, performance]
    category: software-development
    related_skills: [python-craft]

---

# Streamlit Dashboard Craft

Practical guide for building Streamlit dashboards that don't feel like demos — state management, caching, layout, charts, performance, and the common mistakes that make dashboards sluggish or incoherent.


## What This Skill Does

Streamlit dashboards: layout, caching, charts, state.

## When to Use

- Building an internal dashboard for training monitoring, experiment comparison, or data exploration
- Wrapping a model or pipeline in an interactive UI for non-technical users
- Rapidly prototyping a data app where the value is in the interactivity, not the code structure

**Don't use** Streamlit when you need a responsive SPA, custom routing, authenticated multi-user access, or pixel-perfect layout control. For those, use a proper web framework. Streamlit is for data-facing internal tools and quick external demos.

## Execution Model

Streamlit re-runs the entire script from top to bottom on every interaction. This is the core thing to understand — everything else follows from it.

- A button click, slider move, selectbox change, etc. triggers a full re-run.
- The script must be idempotent in its side effects — re-running should not double-write a file or re-send a request.
- Order matters: top-to-bottom execution means the layout is defined by the order of your Streamlit calls.

Implications:
- Don't put expensive computation at the top level — it runs every re-render. Use caching.
- Don't rely on local variables persisting across re-runs — they don't. Use `st.session_state`.
- Don't write to disk or call external services at the top level without guarding — guard with buttons or session state flags.

## Project Layout

```
dashboard/
  app.py                 # entrypoint — st.write("run `streamlit run app.py`")
  config.py             # shared config, constants
  data.py               # data loading, cached
  computations.py       # heavy transforms, cached
  charts.py             # chart helpers (plotly, etc.)
  components/           # reusable composable pieces (optional)
    sidebar.py
    metrics_card.py
  styles.css            # custom CSS (via st.markdown + <style>)
```

Keep `app.py` thin — it assembles components, reads session state, and calls cached functions. Move logic out.

## Caching

Caching is the single biggest performance lever in Streamlit. Three decorators:

### `@st.cache_data`

For data that is *returned* from a function — DataFrames, arrays, dicts, lists. Caches by argument hash. Use for data loading, query results, computed tables.

```python
@st.cache_data(ttl=3600)        # refresh hourly
def load_training_metrics(run_dir: str) -> pd.DataFrame:
    rows = []
    for logfile in Path(run_dir).glob("*.log"):
        rows.extend(parse_log(logfile))
    return pd.DataFrame(rows)

@st.cache_data                  # no ttl — cached until the server restarts or cache clears
def load_card_data() -> pd.DataFrame:
    return pd.read_csv("assets/card_data.json")
```

### `@st.cache_resource`

For resources that are *mutable* or *non-serializable* — database connections, ML models, TensorFlow/ PyTorch sessions, API clients. Caches the object itself, not a copy.

```python
@st.cache_resource
def load_model(path: str):
    return torch.load(path, weights_only=False)

@st.cache_resource
def get_database_connection():
    return psycopg2.connect(DSN)
```

### Key differences

| | `cache_data` | `cache_resource` |
|---|---|---|
| What it caches | Return value (copied) | The object itself (reference) |
| Use for | DataFrames, arrays, dicts | Models, connections, clients |
| Serializable? | Yes — must be | No — can be mutable/live |
| Clear on reload? | Yes | Yes |

### Cache invalidation

- Change the function signature (add/remove an argument) — cache is keyed by call signature.
- Change the function body — Streamlit hashes the function source; changing it invalidates the cache.
- `ttl` for time-based refresh.
- Manual clear: `st.cache_data.clear()` / `st.cache_resource.clear()`, or the "Clear cache" button in the menu.

Common pitfall: caching something that shouldn't be cached (mutable state that changes per call, or a resource that holds a connection that should be pooled differently). If a cached function returns the same object every time and that object is mutated in place, you get shared mutable state — usually not what you want.

## Session State

`st.session_state` is the only reliable way to persist data across re-runs within a session.

```python
# Initialize with a default
if "selected_run" not in st.session_state:
    st.session_state.selected_run = None

# Read
run = st.session_state.selected_run

# Write (from a widget callback or top-level)
st.session_state.selected_run = new_value

# Buttons can use session state to track clicks
if "trained" not in st.session_state:
    st.session_state.trained = False

if st.button("Start Training"):
    st.session_state.trained = True
    start_training()
```

### Callbacks

Use callbacks for side effects on widget changes — they run before the script re-runs.

```python
def on_run_select(change):
    st.session_state.selected_run = change["new"]

run_options = st.selectbox(
    "Run",
    run_ids,
    key="selected_run",           # key ties widget to session state
    on_change=on_run_select,
    args=(...),                   # passed to the callback
)
```

### When session state is the right tool

- Persisting a selection across widget interactions.
- Tracking whether a long-running operation has started/completed.
- Accumulating user input across steps (multi-step forms).
- Storing a toggle that controls layout (e.g., "show raw data" toggle).

### When it isn't

- Don't use session state for data that should come from a cached function — cache the data, read it from cache.
- Don't use it for cross-session state (it's per-browser-session). For that, you need a database or file.

## Layout

### Columns and rows

```python
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Mean fitness", f"{mean_fitness:.3f}")
with col2:
    st.metric("Best fitness", f"{best_fitness:.3f}")
with col3:
    st.metric("Population size", pop_size)

# Rows via columns with full width
st.divider()
```

### Sidebar for controls

```python
with st.sidebar:
    st.header("Controls")
    generations = st.slider("Generations", 10, 500, 100)
    pop_size = st.number_input("Population size", 10, 1000, 200)
    opponent = st.selectbox("Opponent", opponent_options)
    if st.button("Start training"):
        ...
```

Keep controls in the sidebar. Keep the main area for output — charts, tables, metrics.

### Expanders for detail

```python
with st.expander("Generation details"):
    st.dataframe(generation_table)
```

Use expanders for secondary detail that would clutter the main view.

### Tabs for multiple views

```python
tab1, tab2, tab3 = st.tabs(["Fitness", "Tournament", "Config"])
with tab1:
    st.plotly_chart(fitness_chart)
with tab2:
    st.dataframe(tournament_table)
with tab3:
    st.json(config)
```

Tabs are good for organizing a dashboard into logical views. Don't use them for a navigation system — they're view-switching, not page navigation.

### Metric cards

```python
st.metric("Best ELO", f"{best_elo:.0f}", delta=f"+{delta:+.0f} vs last gen")
```

`delta` renders as a small change indicator. Use it for "how did this change since last update."

## Charts

### Plotly (recommended for interactive)

```python
import plotly.express as px
import plotly.graph_objects as go

fig = px.line(
    fitness_df,
    x="generation",
    y="mean_fitness",
    error_y="std_fitness",
    title="Fitness over generations",
)
fig.update_layout(x_axis_title="Generation", y_axis_title="Mean fitness")
st.plotly_chart(fig, use_container_width=True)
```

```python
# Multiple traces
fig = go.Figure()
fig.add_trace(go.Scatter(x=gen, y=mean, name="Mean", line=dict(color="blue")))
fig.add_trace(go.Scatter(x=gen, y=best, name="Best", line=dict(color="green", dash="dash")))
fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02))
st.plotly_chart(fig, use_container_width=True)
```

### Best-fit via matplotlib (static)

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot(generations, mean_fitness, label="Mean")
ax.plot(generations, best_fitness, label="Best")
ax.set_xlabel("Generation")
ax.set_ylabel("Fitness")
ax.legend()
st.pyplot(fig)
```

### Scatter / histogram

```python
fig = px.scatter(
    agent_df,
    x="fitness",
    y="elo",
    color="species",
    hover_data=["genome_hash"],
    title="Fitness vs ELO by species",
)
st.plotly_chart(fig, use_container_width=True)

fig = px.histogram(
    agent_df,
    x="fitness",
    nbins=30,
    title="Fitness distribution",
)
st.plotly_chart(fig, use_container_width=True)
```

### Heatmaps

```python
fig = px.imshow(
    correlation_matrix,
    labels=dict(x="Feature", y="Feature", color="Correlation"),
    color_continuous_scale="RdBu_r",
    zmin=-1, zmax=1,
)
st.plotly_chart(fig, use_container_width=True)
```

### Don't over-chart

One clear chart that answers a question is better than five that don't. Every chart should have a title, labeled axes, and a reason to exist on this dashboard. If a chart is "nice to have," put it in an expander.

## Performance

### Where Streamlit dashboards get slow

- Expensive computation at the top level (runs every re-render).
- Loading large data on every interaction.
- Rebuilding big charts from scratch every re-render.
- Too many widgets triggering re-runs (each one runs the whole script).

### How to make them fast

1. **Cache data and heavy computation.** This is the big one. `@st.cache_data` for DataFrames, `@st.cache_resource` for models/connections.
2. **Lazy-load heavy sections.** Use expanders or tabs to defer loading until the user asks for them.
3. **Subset data for display.** Show the last N rows, a sample, or an aggregated view — not the full million-row table. `df.tail(100)` or `df.sample(1000)` for display.
4. **Use `use_container_width=True`** on charts so they resize rather than triggering layout re-calculations.
5. **Minimize top-level widget re-runs.** A widget that doesn't actually control anything should not be at the top level triggering a re-run — put it in a sidebar or behind a conditional.
6. **Avoid re-running the whole script for a small change.** If a small interactive tweak (e.g., adjusting a smoothing parameter) doesn't need the full data reload, make sure the data is cached so the re-run is cheap.

### Profiling

Streamlit doesn't have a built-in profiler, but you can time sections:

```python
import time

t0 = time.perf_counter()
data = load_data()
st.caption(f"Data loaded in {time.perf_counter() - t0:.2f}s")
```

Wrap expensive sections and watch which ones dominate. If data loading takes 3 seconds every re-run, it should be cached.

## State Machines and Long-Running Operations

For operations that take a while (training, data collection, model export):

### Pattern: button triggers, status in session state

```python
if "training" not in st.session_state:
    st.session_state.training = False
    st.session_state.training_status = "idle"

if st.button("Start Training"):
    st.session_state.training = True
    st.session_state.training_status = "running"
    # Kick off the training (in a thread, or via a subprocess)
    threading.Thread(target=run_training, daemon=True).start()

# Display status
if st.session_state.training:
    st.info(f"Status: {st.session_state.training_status}")
    # Periodically refresh status from a log file or API
    status_df = load_latest_metrics()
    st.plotly_chart(update_chart(status_df))
```

### Pattern: polling via periodic reload

Streamlit doesn't have a built-in auto-refresh, but you can use `st.rerun()` with a sleep in a loop, or have the dashboard read from a shared log/file that the training process writes to, and check it on each re-run.

For a training monitor, the cleanest pattern is:
- Training writes metrics to a file / database as it runs.
- Dashboard reads the file (cached, with ttl) on each re-run.
- Dashboard auto-reruns via a small delay loop or user refresh.

### Graceful shutdown

If the dashboard triggers a long-running process, make sure the process can be stopped. A "Stop" button that sets a flag in session state, checked by the training loop, is the simple approach. For subprocesses, track the PID and offer to kill it.

### Threading caveat

Streamlit runs your script in a single thread per session. Spawning a daemon thread for long-running work (training, data collection) can work, but be aware:

- **Streamlit may restart the script** on certain actions (widget changes, `st.rerun()`), which can leave daemon threads running orphaned.
- **Thread state doesn't survive re-runs.** If the script re-runs, your thread is still running in the background but the session state may have changed — guard with flags in `st.session_state` and check them in the thread.
- **For production dashboards**, prefer external process management: the training process writes metrics to a file/database, and the dashboard reads them (cached). The dashboard doesn't control the process directly — it observes it. This decouples the dashboard's lifecycles from the training process.

## Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Expensive call at top level | Dashboard re-runs slowly on every interaction | Move to cached function |
| Local variable used across re-runs | Value disappears after widget change | Use `st.session_state` |
| Mutable object in `cache_data` | Shared state bugs, cached object mutated | Use `cache_resource` for mutable objects, or return a copy |
| Over-use of `st.rerun()` | Loops, flickering, confusing flow | Prefer session state + natural re-runs from widget interaction |
| Chart re-created from scratch every time | Slow re-render on interaction | Cache the chart figure, or cache the data it's built from |
| Loading full dataset for a small view | Slow, memory-heavy | Subset in the cached function or at display time |
| Button triggers re-run but state doesn't persist | Button click does nothing on second click | Track button state in session state |
| Sidebar too cluttered | User can't find controls | Group controls, use expanders, only show relevant controls |
| No title or description on a chart | Chart is ambiguous | Every chart has a title and axis labels |
| Hardcoded paths in the dashboard | Breaks when moved | Use relative paths, config, or environment variables |

### Threading caveat

Streamlit runs your script in a single thread per session. Spawning a daemon thread for long-running work (training, data collection) can work, but be aware:

- **Streamlit may restart the script** on certain actions (widget changes, `st.rerun()`), which can leave daemon threads running orphaned.
- **Thread state doesn't survive re-runs.** If the script re-runs, your thread is still running in the background but the session state may have changed — guard with flags in `st.session_state` and check them in the thread.
- **For production dashboards**, prefer external process management: the training process writes metrics to a file/database, and the dashboard reads them (cached). The dashboard doesn't control the process directly — it observes it. This decouples the dashboard's lifecycles from the training process.

## Multi-Tab Dashboard Architecture from CR-Pipeline

A real pattern from CR-pipeline's Streamlit dashboard: 8 tabs covering fitness, statistics, tournament results, run comparison, run browsing, config inspection, live monitoring, and card metadata. The dashboard reads from the same run-artifact directories that the CLI writes.

**Tab structure:**

| Tab | Purpose | Data source |
|---|---|---|
| Fitness | Per-run fitness curves (mean, best, std), smoothing, per-generation metrics | `experiment_tracking.py` run metrics files |
| Statistics | Population statistics: diversity, species distribution, genome stats, ELO distribution | Run artifacts + population files |
| Tournament | ELO charts, brackets, head-to-head, champion lineage | `tournament_collector.py` results |
| Comparison | Side-by-side comparison of multiple runs (fitness curves overlaid, stats compared) | Multiple run directories |
| Runs | Browse past runs, select one to inspect, see run metadata and status | Run directory discovery |
| Config | Show the config that produced the current/selected run (for reproducibility) | Run's config snapshot |
| Monitoring | Live resource monitoring (CPU/GPU/memory) during a running training session | `resource_monitor.py` metrics |
| Card Meta | Card data reference (card stats, levels, effects) — useful context for understanding the sim | `assets/card_data.json` |

**Cross-tab state:**
- A run selection in one tab (e.g., Runs tab picks a run to inspect) should be reflected in other tabs (Fitness shows that run's curves, Config shows that run's config).
- Use `st.session_state` to carry the selected run across tabs — each tab reads it.
- Don't reload the data for each tab independently — cache the data loading, and have tabs read from the cached data.

**Run comparison (the most complex tab):**
- Select multiple runs (checkboxes or multi-select).
- Overlays their fitness curves (mean, best) on the same chart, with a legend.
- Compares final stats side by side (final best fitness, final diversity, generations, evaluation time).
- Optionally: tournament results between the champions of the selected runs (who beats whom).

**Smoothing and statistical overlays:**
- Fitness curves are noisy — apply smoothing (rolling mean, LOESS) for the visual, but show the raw data too (or on hover).
- Statistical significance testing between runs (if two runs are selected, test whether their fitness difference is significant, not just whether the curves look different).

**Live monitoring during training:**
- A training run writes metrics as it goes (per-generation files or a live log).
- The dashboard reads the latest metrics (cached with a short ttl) and updates the chart.
- Resource monitoring (CPU/GPU/memory) from `resource_monitor.py` — show whether the run is CPU-bound, GPU-bound, memory-limited.
- A "Stop" button that sets a flag in session state, checked by the training loop.

**Performance at scale:**
- Browsing many runs: don't load all runs' full metrics into memory at once. Load the selected run's metrics on demand (cached).
- Large populations: show aggregated stats (mean, std, distribution) not the full per-agent table unless the user asks.
- Long runs: paginate or limit the displayed generations (last N, or a downsampling) — a 1000-generation run doesn't need 1000 points on screen.

**Layout patterns for multi-tab dashboards:**
- Sidebar for global controls (run selection, refresh, stop training, clear cache).
- Each tab is self-contained (its own data loading, its own charts) but reads shared state from session state and cached data.
- A "Select run first" prompt if no run is selected and a tab needs one.
- Use `st.tabs` for the tab bar, `st.columns` within tabs for side-by-side charts, `st.expander` for detail tables.

## Custom Components and Theming

**Custom CSS:**
- Inject custom CSS via `st.markdown("<style>...</style>", unsafe_allow_html=True)`.
- Use for: consistent card styling, metric card layout, chart container sizing, sidebar styling, font overrides.
- Keep custom CSS minimal — Streamlit's defaults are usually fine, and heavy CSS customization can break across Streamlit versions.

**Custom components (advanced):**
- Streamlit supports custom components (React-based, packaged as a component) for things the built-in widgets don't cover.
- Use when: you need a chart type Streamlit doesn't support, a custom interactive visualization, or a UI element that Streamlit can't express.
- Don't use for: anything that existing Streamlit widgets + Plotly can do — adding a custom component for a standard chart is over-engineering.

**Theming:**
- Streamlit has a theme system (light/dark, primary color, background, secondary background, text color) set in the config or the UI.
- Set a consistent theme for the dashboard — don't leave it to the user's default.
- Match the theme to the project's branding if the dashboard is customer-facing.

## Error Handling and User Feedback in Dashboards

**What to show when data loading fails:**
- A clear error message (what failed, why, what to do).
- Not a stack trace (the user doesn't care about the traceback; it goes in the logs).
- An offer to retry or to select a different run (if the failure is "this run doesn't exist").

**What to show when no data is available:**
- A clear "no data" state (no runs found, no metrics for this run, this run hasn't produced data yet).
- Not an empty chart or an error — a "no data" state is informative.
- Guidance: "Select a run from the Runs tab" or "This run is still training — check back in X minutes."

**What to show during long-running operations:**
- A status indicator ("Training in progress...", "Generation 47/200", "Best fitness so far: X").
- A progress indicator if the total is known (progress bar for a known-length operation).
- A "Stop" button if the operation can be stopped.
- Don't leave the user looking at a frozen screen with no feedback.

**Loading states:**
- For data that takes a noticeable time to load (even cached), a brief "Loading..." indicator is nicer than a spinner that appears to be a hang.
- For cached data that loads instantly, no loading state is needed — the dashboard should feel snappy.

## Testing Dashboards

**What to test:**
- The dashboard loads without errors on first visit (no missing state, no errors from uninitialized session state).
- Run selection works (select a run, other tabs reflect the selection).
- Charts render with data (not empty, not erroring).
- Error states work (no data, bad run, failed load — each shows a clear state).
- Caching works (second visit to the same run is fast; changing the run reloads the data).

**How to test:**
- Load the dashboard as a subprocess (`streamlit run app.py`), point the browser at it, and check the page content.
- Or test the underlying data-loading and chart-building functions directly (unit test the functions, not just the UI).
- For dashboards that read run artifacts, use a small test run artifact (a directory with minimal metrics) so the tests are fast and deterministic.

**What not to test:**
- Pixel-perfect layout (Streamlit's layout isn't pixel-perfect and shouldn't be tested that way).
- The exact chart appearance (colors, exact sizing) — test that the chart has the right data and the right axes, not that it looks identical to a reference image.

- [ ] Expensive data loading is cached (`@st.cache_data`)
- [ ] Mutable resources (models, connections) use `@st.cache_resource`
- [ ] Persistent state uses `st.session_state`, not local variables
- [ ] Controls are in the sidebar, output in the main area
- [ ] Every chart has a title, axis labels, and a reason to exist
- [ ] Large datasets are subset for display (not loaded fully into a table widget)
- [ ] Long-running operations have a status indicator and a way to stop
- [ ] Dashboard runs cleanly on first load (no errors from missing state)
- [ ] Paths/config are not hardcoded to one machine
- [ ] Cache is invalidated appropriately (ttl or function change)
