# uv: killed installs leave phantom-complete packages (observed 2026-11-05)

**The failure mode.** A `uv pip install` interrupted mid-write (killed by a timeout, crash, or
Ctrl-C during the file-copy phase) can leave site-packages in a state where the **metadata says
the package is installed but files are missing**. Every later check passes — version queries,
import of top-level modules that happen to be present — and `uv pip install <same spec>` becomes
a silent no-op because the dist-info satisfies the requirement. The breakage surfaces only when
runtime code touches one of never-written files.

**Observed instance (Windows, uv-managed Python 3.14 venvs).** A prefect install killed at a
420 s timeout; reinstall reported done in seconds (no-op). First real use — `flow.run()` with an
ephemeral server — died during Alembic migration collection:

```
ImportError: Can't find Python file ...\site-packages\prefect\server\database\_migrations\versions\sqlite\2023_09_25_..._remove_flow_run_id_requirement_from_task_run.py
... uvicorn.error - Application startup failed. Exiting.
```

Note the shape: a *data-ish* file (migration script) missing from an otherwise importable
package — prefect itself imported fine, so nothing complained until server startup walked the
migrations directory on disk. Packages that ship file collections their code enumerates at
runtime (migrations, templates, bundled assets) expose this corruption earliest; pure-module
packages may hide it far longer.

**Remedies.**
- **Recreate the venv** (`rm -rf <venv> && uv venv ...`) — confirmed working path in the observed
  incident (fresh installs completed and booted the ephemeral server).
- `uv pip install --reinstall-package <name>` should repair by force-refetching that package even
  when metadata is satisfied; plausible cheaper fix, **untested here** — state it as such until
  measured.

**Prevention.** Long installs belong in a background process with completion notification, not a
foreground command whose timeout can execute this exact kill (see the repo's own tooling rule:
multi-minute jobs -> background terminal). If an install was ever killed, treat that venv as
suspect — do not trust its completeness.
