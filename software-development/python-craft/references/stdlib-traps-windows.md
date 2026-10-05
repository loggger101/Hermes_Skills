---
description: "Python stdlib traps measured on Windows / Python 3.14.6: open() cp1252 default, csv blank lines, rename vs replace, rmtree read-only, strftime %-d, json NaN, naive/aware datetimes; plus facts that are no longer traps"
source_repo: gto76/python-cheatsheet (topic list: numbers, datetime, json, csv, open, os)
tested_version: one probe script run on Python 3.14.6, Windows 11, locale cp1252, utf8_mode 0; every line below is an observed result
verified_date: "2026-10-05"
---

# Stdlib traps, measured on Windows (Python 3.14.6)

Environment: `sys.flags.utf8_mode` 0, `locale.getencoding()` = `cp1252`. Complements "Windows host pitfalls (measured)" in `python-craft/SKILL.md`.

## Bite you: always pass the argument

| Call | Observed | Fix |
|---|---|---|
| `open(p).read()` on a UTF-8 file containing `é — →` | returns mojibake `'cafÃ© â€” â†’'` with **no error** | `open(p, encoding="utf-8")`, or `Path.read_text(encoding="utf-8")` |
| `open(p, "w").write("— →")` | `UnicodeEncodeError` (the arrow is not in cp1252; the em dash alone is) | `encoding="utf-8"` on every text open |
| `csv.writer(open(p, "w"))` row `["a","b"]` | bytes `a,b\r\r\n`: blank line between rows when read back | `open(p, "w", newline="")` |
| `os.rename(a, b)` with `b` existing | `FileExistsError` | `os.replace(a, b)` (overwrites; atomic on the same volume) |
| `shutil.rmtree(d)` containing a read-only file (git object files are) | `PermissionError` | clear the read-only bit in an error handler (`onexc=` in 3.12+) |
| `dt.datetime(...).strftime("%-d %b")` | `ValueError: Invalid format string` (glibc-only flag) | `%#d` on Windows (gave `5 Oct`), or `f"{d.day} {d:%b}"` everywhere |
| `json.dumps({"x": float("nan")})` | emits `{"x": NaN}`, which is **not valid JSON** and `json.loads` accepts it back | `allow_nan=False` (raised `ValueError`) so a NaN fails at the writer |
| `json.dumps({1: "a"})` then `loads` | key comes back as the string `"1"` | use string keys deliberately |
| `datetime.now() < datetime.now(timezone.utc)` | `TypeError: can't compare offset-naive and offset-aware` | keep one convention: aware UTC everywhere inside, convert at the edges |
| `datetime.utcnow()` | `DeprecationWarning` | `datetime.now(timezone.utc)` |
| `[lambda: i for i in range(3)]` called | `[2, 2, 2]` (late binding) | `lambda i=i: i` or `functools.partial` |

The cp1252 default is why a "works on my machine" script that writes arrows or checkmarks fails on this one; set the encoding at each call
(or run Python with `-X utf8` / `PYTHONUTF8=1`, which makes `utf8_mode` 1; a process-level switch you must also set for child processes).

## Facts that are not traps here (do not "fix" them)

- `sum([0.1] * 10)` returned exactly `1.0` on 3.14 (same as `math.fsum`): current `sum` compensates float error. The classic `0.9999999999999999` result no longer appears; keep `fsum` only if you need to support older interpreters.
- `time.time()` is fine-grained on this box (about 517,000 distinct values in 0.2 s) and `perf_counter` resolution is 1e-7 s; the old "Windows clock ticks at 15.6 ms" worry did not reproduce.
- A 357-character directory path was created without error: long paths are enabled for this Python build. Do not add `\\?\` prefixes preemptively; test on the target machine.
- `datetime.fromisoformat("2026-10-05T12:00:00Z")` parses the trailing `Z` (aware, UTC).
- `Path.glob`/`exists` are **case-insensitive on Windows** (`glob("data.*")` matched `Data.TXT`; `Path("DATA.TXT").exists()` was True) and case-sensitive on Linux; a test that passes on Windows can fail in CI.
- `zoneinfo.ZoneInfo("America/New_York")` worked because the `tzdata` package is installed here. Windows has no system timezone database, so a fresh environment without `tzdata` will raise `ZoneInfoNotFoundError` (documented behaviour, not reproduced here); add `tzdata` as a dependency of anything using `zoneinfo`.

## Arithmetic and strings (portable, easy to forget)

- `round(2.5) == 2`, `round(3.5) == 4`, `round(0.5) == 0`, `round(-1.5) == -2`: round-half-to-even, not half-up. Use `decimal.Decimal(...).quantize(..., ROUND_HALF_UP)` when money rules say half-up.
- `-7 // 2 == -4` and `-7 % 2 == 1` (floor semantics); `int(-7 / 2) == -3` truncates toward zero. `divmod(-7, 2) == (-4, 1)`.
- `int("١٢٣") == 123`: `int()` accepts Unicode decimal digits. Validate with `str.isascii()` first if the input is untrusted.
- `"ß".upper() == "SS"` and `"ﬁ".upper()` has length 2: case conversion can change string length; compare with `casefold()`.
- `" a  b ".split()` is `['a', 'b']` but `split(" ")` is `['', 'a', '', 'b', '']`.
