---
description: "Notebook tooling run live (jupytext, nbformat, nbconvert, papermill, nbmake, nbdiff): text round-trips, validation, execution failures, parameter injection traps, tests, diffs"
source_repo: markusschanta/awesome-jupyter (curated list; categories: runtimes, visualization, rendering/conversion, version control, testing, extensions)
tested_version: jupytext 1.19.6, nbformat 5.11.1, nbconvert 7.17.1, nbclient 0.11.0, papermill 2.7.0, nbdime 4.0.4, nbmake 1.5.5, ipykernel 7.4.0 in a Python 3.11.16 venv on Windows; one probe script, outputs quoted
verified_date: "2026-10-05"
---

# Notebook tooling beyond "open it in JupyterLab"

The awesome-jupyter list groups tools by runtime, visualization, rendering and conversion, **version control**, **testing**, and extensions. These are the ones that make notebooks
work in a repo and in automation, with what each did when run.

## Version control: keep a text twin (jupytext)

`jupytext --to py:percent a.ipynb` produced a plain `.py` with a YAML header (kernelspec, jupytext version) and `# %%` cell markers, tags preserved (`# %% tags=["parameters"]`), markdown as comment blocks.
Converting back (`--to ipynb -o b.ipynb a.py`) restored the cell types `['markdown','code','code']` with **no outputs and no execution counts**. So the `.py` is the reviewable source of truth and the `.ipynb` is a build product;
commit the `.py` (or pair them with `jupytext --set-formats ipynb,py:percent`) and strip outputs from committed `.ipynb` files.
The header embeds the jupytext version, which makes the file change when the tool upgrades.

`nbdiff a.ipynb pm.ipynb --no-color` is a structural diff (cell-level add/remove/modify, metadata aware); it reported 110 lines for a papermill-run notebook because papermill adds metadata blocks to every cell,
so diff the source twins instead when reviewing.

## Validation

`nbformat.validate(nbformat.read(path, as_version=4))` raised `NotebookValidationError: 'source' is a required property` for a code cell with its `source` removed. Validate notebooks that tools or agents generate before committing or executing them.

## Execution and failure behaviour

| Command | Observed |
|---|---|
| `jupyter nbconvert --to notebook --execute err.ipynb` (last cell `1/0`) | exit 1, `ZeroDivisionError`, **no output file written**: the partial results of the cells that did run are lost |
| same with `--allow-errors` | exit 0, output notebook written with the error captured in the cell output; check outputs for `output_type == "error"` yourself, since the exit code no longer signals failure |
| `papermill a.ipynb pm.ipynb -p x 5 -k <kernel>` | exit 0; inserts a new cell tagged `injected-parameters` immediately after the cell tagged `parameters` |

A kernel for the interpreter must exist (`python -m ipykernel install --user --name NAME`) and be named in the notebook metadata or with `-k`.

### papermill traps (both reproduced)

1. **Code in the `parameters` cell runs before the injected values.** With `x = 2; print(x * 21)` in the parameters cell and `-p x 5`, the cell printed `42`, not 105: the injected cell comes *after* it. Keep the parameters cell to plain defaults (assignments only) and put work in later cells.
2. **No cell tagged `parameters` means the parameter is silently ignored**: the run exited 0 with only the message `Passed unknown parameter: x`. Assert on the injected-parameters cell in automation, or fail on that warning.

## Testing notebooks

`pytest --nbmake t` ran two notebooks, one whose last cell raises and one clean, giving `1 failed, 1 passed in 3.13s` and exit 1: each notebook is one test, executed top to bottom, failing on any cell exception.
Use it in CI so notebooks do not rot; keep them fast and seeded.

## Choosing

| Goal | Tool |
|---|---|
| Review notebooks in pull requests | jupytext `py:percent` twins, `nbdime` for structural diffs |
| Parameterised batch runs / reports | papermill (mind the two traps above) |
| One-off conversion to HTML/PDF/script | `jupyter nbconvert` (`--execute` to run first) |
| Notebooks as tests | `nbmake` under pytest |
| Programmatic execution inside Python | `nbclient` (what nbconvert/papermill build on) |

Interactive agent use of a live kernel is covered in `../SKILL.md`; this note is for the file-and-CI side.
