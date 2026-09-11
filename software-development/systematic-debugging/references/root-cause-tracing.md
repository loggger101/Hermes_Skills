# Root-Cause Tracing (Trace Backward to the Original Trigger)

Use when a bug manifests deep in the call stack — e.g., `git init` ran in the wrong directory, a file was created in the wrong location, or a database opened with the wrong path. The error is not at the entry point; the stack trace shows a long chain; you don't know where the invalid value originated.

Source: adapted from obra/superpowers v6.3.0 (`skills/systematic-debugging/root-cause-tracing.md`, MIT). Examples re-expressed for Python/pytest.

**Core principle:** Trace backward through the call chain until you find the original trigger, then fix at the source — never where the error appears.

## The Tracing Process (5 steps)

1. **Observe the symptom.** Capture it exactly: `Error: git init failed in ~/project/packages/core`.
2. **Find the immediate cause.** What code directly causes this? e.g. `subprocess.run(['git', 'init'], cwd=directory)` with an empty `cwd` resolving to `os.getcwd()`.
3. **Ask: what called this?** Walk the caller chain upward, one frame at a time (`WorktreeManager.create_session_worktree(project_dir) <- Session.initialize_workspace() <- Session.create() <- test at Project.create()`).
4. **Keep tracing up.** At each level ask *what value was passed?* — find `project_dir = ''` (empty string), and why: an empty string as cwd resolves to the process working directory.
5. **Find the original trigger.** e.g., a top-level test fixture returning `{ 'temp_dir': '' }` accessed before setup ran.

**NEVER fix just where the error appears.** Trace back to find the original trigger, then fix at the source — and consider `defense-in-depth.md` for adding validation along the path.

## Stack-Trace Instrumentation (when you can't see the chain)

Log *before* the dangerous operation, not after it fails:

```python
import os, traceback

def git_init(directory: str):
    print(f"DEBUG git init: directory={directory!r} cwd={os.getcwd()!r}")  # console output, not logger — loggers may be suppressed in tests
    traceback.print_stack()          # complete call chain at the point of interest
    subprocess.run(['git', 'init'], cwd=directory)
```

Capture with: `python -m pytest path/test.py 2>&1 | grep "DEBUG git init"`

**Stack-trace tips:**
- In tests use raw print/stderr, not a logger — loggers may be suppressed.
- Log before the dangerous operation, not after it fails.
- Include context: directory, cwd, environment variables, timestamps.
- `traceback.print_stack()` / `new Error().stack` show the complete call chain at that point.

## Real Example (the story this technique exists for)

**Symptom:** `.git` created inside source code (`packages/core/`).

**Trace chain:**
1. `git init` runs in process cwd <- empty directory parameter
2. WorktreeManager called with empty project_dir
3. Session.create() passed an empty string
4. Test accessed `context.temp_dir` before setup ran
5. Fixture initially returns `{ 'temp_dir': '' }`

**Root cause:** top-level variable initialization accessing the value too early.
**Fix at source:** make temp_dir a property that raises if accessed before setup.
**Defense-in-depth added (see defense-in-depth.md):** entry validation, business-logic check, environment guard refusing `git init` outside tmpdir during tests, stack-trace logging before the operation. Result: full suite green, zero pollution — and each layer later caught a bug the others missed.

## Finding *Which Test* Did It (polluter bisection)

If an unwanted artifact appears during the test run but you don't know which test creates it, use `scripts/find_polluter.sh` in this skill's directory:

```bash
./find_polluter.sh '.git' 'tests/**/*.py'   # runs tests one-by-one, stops at first polluter
```

It checks for the artifact before each run (skipping if pollution pre-exists), so attribution stays correct even mid-run.
