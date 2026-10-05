---
description: "tqdm 4.70.1 measured: bar goes to stderr and floods piped logs with CRs, print() corrupts it, TQDM_ASCII=1 crashes the program, TQDM_DISABLE and MININTERVAL tame logs, per-iteration cost"
source_repo: tqdm/tqdm (MPL-2.0 and MIT)
tested_version: "tqdm 4.70.1 on Python 3.14.6, Windows 11, uv venv; two scripts rendered into StringIO and into piped child processes (bytes captured). Notebook, async and rich widgets not run"
verified_date: "2026-10-05"
---

# tqdm in scripts, logs and CI (run)

`SKILL.md` says periodic prints beat a progress bar for CI. These are the measured reasons, and the settings that make a
bar acceptable when you want one.

## Where it writes, and what a log file gets

| Case | Observed |
|---|---|
| Default stream | **stderr**; stdout stays clean (`done` only). A bar in a pipeline does not corrupt captured stdout |
| Child process piped (not a TTY), 40 iterations over 2 s | 23 carriage-return updates in stderr: one "line" in a log file ends up with dozens of `\r`-separated redraws |
| `TQDM_DISABLE=1` | no output at all |
| `TQDM_MININTERVAL=30` | 3 CRs in the same run (updates at most every 30 s plus first and last) |
| Output captured with `text=True` | CRs are turned into newlines by universal-newline decoding, so a naive reader sees many lines; read bytes to see what was written |
| Generator without `total` | no percent or ETA: `3it [00:00, 51358.82it/s]` |
| `disable=True` | empty output |
| Windows cp1252 pipe (`PYTHONIOENCODING=cp1252`) | no crash: tqdm fell back to `#` bars |
| UTF-8 stream | block characters (`██████`) |

For agent and CI runs: `tqdm(it, disable=not sys.stderr.isatty())`, or leave it on with `mininterval=30` (or env
`TQDM_MININTERVAL`), or set `TQDM_DISABLE=1` in the job environment.

## Traps

| # | Code | Observed |
|---|---|---|
| 1 | `print("msg")` inside a `for _ in tqdm(...)` loop | the message lands right after the `\r` redraw on the same line (`...0/2 [00:00<?, ?it/s]log line 0`) and the next redraw follows it: the display is corrupted. Use `tqdm.write("msg")` (it clears the bar, prints, and redraws; in a non-TTY file the clear is written as spaces plus CR) |
| 2 | Environment variable **`TQDM_ASCII=1`** | the program **exits with code 1** (`ZeroDivisionError: division by zero`) before the loop runs, so stdout was empty. The value `1` is taken as the bar character set (one symbol), not as a flag. `TQDM_ASCII=True`, `false` and a custom string like ` .oO0` all worked. A bad environment value can kill a job that only wanted a progress bar |
| 3 | `tqdm.auto.tqdm` | resolves to `tqdm.asyncio` outside a notebook (still a normal terminal bar) |
| 4 | `from tqdm.contrib.concurrent import process_map, thread_map` | importable; not exercised |

## Cost

2 000 000 iterations of an empty loop: plain `for` 0.019 s, `tqdm` with defaults 0.174 s (about 78 ns per iteration, 9x on a
body that does nothing). `miniters=1000, mininterval=1` was not faster here (0.214 s, within noise on a single run). Negligible
for real work; avoid wrapping a hot inner loop whose body costs under a microsecond, and wrap the outer loop instead.

## Environment variables tqdm reads

`TQDM_DISABLE`, `TQDM_MININTERVAL`, `TQDM_ASCII` and `TQDM_NCOLS` were set above; the first two worked as expected, `TQDM_NCOLS=30`
ran normally (exit 0; its effect on the bar width was not inspected). Treat any `TQDM_*` value in a shared environment as code that can change or break your script, and
set them explicitly in CI rather than inheriting.

Not run: Jupyter (`tqdm.notebook`), `tqdm.rich`, `tqdm.asyncio` loops, `trange` with multiprocessing locks, the `tqdm`
command-line pipe mode, and positioned (`position=`) nested bars.
