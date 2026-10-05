# pytest 9.1.1: exit codes, built-in subtests, strict mode, config precedence (run live)

Source: [pytest-dev/pytest](https://github.com/pytest-dev/pytest) (MIT). **pytest 9.1.1** (2026-06-19), Python 3.14.6,
Windows. A scratch project (`tests/`, a `conftest.py`, two same-named test files in sibling dirs) was run through one driver
script (about 25 runs with `subprocess`, `-p no:cacheprovider` unless noted). Every result below is observed; the probe
shows what an agent running pytest in a loop needs to read from the output.

## Exit codes (gate on these, not on the text)

| Situation | Exit |
|---|---|
| all pass (skips and non-strict xfail count as OK) | 0 |
| any test failed, including an `XPASS(strict)` | 1 |
| collection error (`import nosuchmodule` in a test file), `--strict-markers` error, interrupted | **2** |
| usage error: `--nope` -> `unrecognized arguments: --nope`; a path that does not exist -> `ERROR: file or directory not found` | **4** |
| nothing selected (`-k zzz`) | **5** |

An agent loop that treats "exit != 0" as "tests failed" will mis-handle 2, 4 and 5: 2 means the suite never ran,
4 means the command line is wrong, 5 means the selection was empty (a green gate may hide a deleted test; see
`autonomous-ai-agents/autonomous-loop-design/references/loop-goal-design-and-review.md`).

## Built-in subtests (new in 9.x)

The `subtests` fixture needs no plugin:

```python
def test_subs(subtests):
    for i in range(4):
        with subtests.test(msg="case", i=i):
            assert i != 2
```

Output: `SUBFAILED[case] (i=2) tests/test_sub.py::test_subs - assert 2 != 2`, the parent reports
`FAILED ... - contains 1 failed subtest`, and the summary line was `2 failed, 1 passed, 3 subtests passed`. The "2 failed" are the failing
subtest and its parent test; the other three iterations ran instead of stopping at the first failure, and `test_after` is the 1 passed. `-rA` lists each subtest.

## Strict mode and configuration files

- `pytest.toml` is a native config file: `[pytest]` table, `addopts = ["-ra"]`, `markers = [...]`, `strict = true`; the header
  printed `configfile: pytest.toml`. With `strict = true` a plain `@pytest.mark.xfail` that passes became a failure
  (`[XPASS(strict)]`): strict mode promotes non-strict xfails to strict. (`slow` was registered in that file, so unregistered marks under `strict = true` were not exercised.)
  Without strictness an unregistered mark only warns; `--strict-markers` on the command line gave exit 2 with
  `'slow' not found in `markers` configuration option` at collection.
- **Only one config file is used.** With `pytest.ini` and `pyproject.toml` (`[tool.pytest.ini_options]`) both present the
  header said `configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)`: options in the ignored file
  silently do nothing.
- `conftest.py` at the rootdir supplied a fixture to `tests/test_conf.py` with no import.

## Collection and import mode

Two files named `tests/test_dup.py` under `pkg_a/` and `pkg_b/` (no `__init__.py`) -> **exit 2** `ERROR pkg_b/tests/test_dup.py` (the
default `prepend` mode imports both as the module `test_dup`). `--import-mode=importlib` ran both (`2 passed`). Give test files
unique names, add `__init__.py`, or set `addopts = ["--import-mode=importlib"]`.

## Options that behave differently than expected

- **`--lf` needs the cache plugin**: with `-p no:cacheprovider` it is `unrecognized arguments: --lf` (exit 4). With the cache
  on, the second run reported `2 failed, 7 deselected` (only the previous failures) and created `.pytest_cache/`. Disabling
  the plugin in automation (as the loop gates here do) also stops stray `.pytest_cache` directories appearing in the repo.
- `-x` stops after the first failure (`1 failed, 1 passed`).
- `-W error` turned a `DeprecationWarning` raised in a test into `1 failed`; the default run only prints the warnings summary
  (exit 0). Use `-W error::DeprecationWarning` in CI for your own code.
- `--junitxml=out.xml` wrote a 1,480-byte file with `tests=` attributes even though the run failed (exit 1).
- `--setup-show` prints fixture SETUP/TEARDOWN lines; useful to confirm scope.

## Fixtures and built-ins, verified

- A module-scoped fixture feeding a function-scoped one produced exactly
  `mod-setup, fn-setup, a, fn-teardown, fn-setup, b, fn-teardown` (module teardown after the last test).
- `monkeypatch.setenv` is undone after the test (`PROBE_VAR` absent in the next test); `capsys.readouterr().out == "hello\n"`;
  `pytest.raises(ValueError, match=r"bad \d+")` matches with `re.search`; `0.1 + 0.2 == pytest.approx(0.3)` passes while the plain
  `==` fails (`assert (0.1 + 0.2) == 0.3`).
- **Windows trap in `tmp_path`:** `p.write_text("é\n", encoding="utf-8")` then `p.read_bytes()` gave `b'\xc3\xa9\r\n'`, not
  `b'\xc3\xa9\n'`: text mode translates newlines. A test comparing bytes fails only on Windows. Use `write_bytes`, or
  `p.write_text(s, encoding="utf-8", newline="\n")`, and always pass `encoding=`.

## Checklist for a pytest gate in an agent loop

1. `python -m pytest -p no:cacheprovider -q --tb=short`, and branch on the exit code table above.
2. Print the collected count (`--collect-only -q | tail -1`) before and after a change so a deleted test is visible.
3. Prefer `strict = true` in `pytest.toml` for new projects; keep exactly one config file.
4. Use `subtests` for table-driven checks instead of a loop that hides the second failure.
5. Not covered: xdist, `pytest-asyncio`, `pytest-cov`, `pytester`, `--pdb`, `monkeypatch.syspath_prepend`, doctest modules
   (see `data-science/algorithms-python-catalog/references/keon-algorithms-notes.md` for a doctest run).
