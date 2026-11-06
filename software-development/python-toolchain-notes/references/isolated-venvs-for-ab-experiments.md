# A/B experiments need isolated venvs — a shared uv env self-raced and faked an upstream failure (measured 2026-11-05/06)

What happened, as the cautionary shape: an experiment comparing package semantics across two versions ran both arms in
ONE uv-managed venv (`uv pip install pkg==A`, run arm, `uv pip install pkg==B`, run arm). Both arms failed with identical
leaf errors - server-side alembic tracebacks ending `ImportError: Can't find Python file ...<migration>.py` - and the
finding got banked as "environment cannot host this experiment". Wrong. Post-hoc disk inspection showed: (1) only ONE
env ever held the package, final version = arm-2's; (2) the allegedly-missing migration file EXISTS on disk now;
(3) both arms' logs pointed at the same site-packages path. Root cause (fully established on rerun): this box exports PYTHONPATH globally at a shared Hermes-managed venv,
so BOTH arms silently imported that env's copy regardless of which venv interpreter ran - per-venv isolation was an
illusion from the start. The alembic "Can't find Python file" then came from site-packages mutating while arm-1's
server enumerated its versions/ dir mid-startup (reinstall racing a live process); the file exists before and after.
The upstream package never failed; the harness did - twice identically because both arms shared through PYTHONPATH.

Rules:
- Version-comparison experiments get one venv per version (`uv venv --python 3.13 a && VIRTUAL_ENV=a uv pip install pkg==A`),
  created BEFORE any arm runs, never mutated during a run. Sequential reuse of an env is only safe when nothing that was
  imported is still executing.
- "Can't find Python file <path>" from alembic/pkg-loader machinery + the path existing now = suspect a concurrent
  install/reinstall on that exact interpreter, not package corruption and not platform incompatibility.
- On any machine exporting PYTHONPATH (hermes-managed venvs often do), `uv venv` isolation is VOID until you clear it:
  run probes as `PYTHONPATH= <venv>/Scripts/python.exe -I script.py`. `-I` alone does not cover every PYTHON* var on
  Windows shells; clearing the variable plus `-I` together is the belt. Verify by printing a package's resolved path
  (`print(pkg.__file__)`) inside each arm BEFORE trusting any measurement from it.
- Reproducing OLD versions for A/B may need era-pinning their deps too: prefect==3.8.7 declares fastapi>=0.139,<1.0.0
  but its server code passes Body(min_items=...), removed in the range's later minors - fresh resolve (fastapi 0.162)
  dies at import; pin fastapi to the old version's release-time low end.
- Before banking any experiment verdict as environmentally impossible: check per-arm env identity (dist-info versions,
  site-packages paths in tracebacks). Identical paths across arms is the tell of accidental sharing - it converts two
  supposed data points into one broken datapoint duplicated.
- Reinstall-mid-run corruption class applies beyond uv: any pip/uv write to an interpreter with live processes on
  Windows (where open .pyd/.dll can also block replacement outright) or long-lived server lifespans (migration-on-startup).
