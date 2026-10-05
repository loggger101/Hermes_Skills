# pandas 3.0.6: what changed from 2.x and what bites (run live)

Source: [pandas-dev/pandas](https://github.com/pandas-dev/pandas) (BSD-3). **pandas 3.0.6** (released 2026-09-17; 3.1.0rc0
is out, not tested) with numpy 2.5.3 and pyarrow 25.0.1, Python 3.14.6, Windows. About 90 calls, three probe scripts; each
line below is a measured result. A pandas 2 habit that still "works" often warns first: run with
`-W error::FutureWarning -W error::Pandas4Warning` to find them. The official guide for the string change is
`user_guide/migration-3-strings.html`.

## 1. The default string dtype is `str`

| Probe | Result on 3.0.6 |
|---|---|
| `pd.Series(["a","b",None]).dtype` | `str` (pyarrow-backed when installed); `isna()` -> `[F,F,T,F]`; the missing value is `nan`, not `None` |
| `pd.Series(["a", pd.NA])` / `["a", np.nan]` | both stored as `nan`; `isna` True for `nan`, `None`, `pd.NA` |
| `pd.DataFrame({"x": ["p","q"]})` | `StringDtype(na_value=nan)`; the **column index** is also `str` |
| `pd.Series(["a", 1, None]).dtype` | `object` (mixed stays object); `dtype=object` is honoured |
| `s.str.len()` | `int64` with no missing, **`float64` with any missing** (`[1.0, 1.0, nan, 1.0]`) |
| `s == "a"` with a missing value | plain `bool` dtype, missing compares **False** (no `<NA>`) |
| `s.str.contains("a")` with missing | `bool`, missing -> False |
| `Series(["a","b"])[0] = 5` | `TypeError: Invalid value '5' for dtype 'str'. Value should be a string or missing value` (pandas 2 made the column object; from the migration guide, not run here) |
| `Series([1.5, np.nan]).astype(str).tolist()` | `['1.5', nan]`: **NaN stays missing**, no longer the string `'nan'` |
| `is_object_dtype(str series)` / `is_string_dtype` | False / True; `to_numpy()` still returns an `object` ndarray; `.tolist()` items are `str` |
| `select_dtypes(include="object")` | still returns `str` columns but raises `Pandas4Warning: 'str' dtypes are included ... deprecated`; write `include="str"` (tested) for string columns |
| 100k short strings, `memory_usage(deep=True)` | `str` 1.1 MB vs `object` 5.2 MB; 300k `item_N` strings: 5.6 MB vs 17.9 MB, `str.upper` 11 ms vs 31 ms |

Fix recipe: replace `df[col].dtype == object` checks with `pd.api.types.is_string_dtype`; replace `== "nan"` string checks;
cast with `.astype("string")` (nullable, `<NA>` semantics) only when you want `pd.NA`.

## 2. Copy-on-Write is always on

- Writing to a derived object never touches the parent: `v = df["a"]; v.iloc[0] = 99` left `df["a"]` at `[1, 2, 3]`;
  `df.iloc[0:1].iloc[0, 0] = 9` and `df.copy(deep=False)` writes also left the parent unchanged.
- **Chained assignment does nothing and warns** (`ChainedAssignmentError`): `df["a"][0] = 100` (parent unchanged),
  `df[df.a > 1]["b"] = 0` (unchanged, `[4, 5, 6]`), and `df["b"].fillna(0, inplace=True)` (unchanged). The working form is
  `df.loc[df.a > 1, "b"] = 0` -> `[4, 0, 0]`, no warning.
- Arrays from pandas are **read-only**: `df.to_numpy().flags.writeable` and `df.values` -> False, and `arr[0,0] = 5` raises
  `ValueError: assignment destination is read-only`; `Series.to_numpy(copy=True)` is writeable.
- `pd.set_option("mode.copy_on_write", False)` returns but warns `Pandas4Warning: ... deprecated. Copy-on-Write can no
  longer be disabled`.

## 3. Datetimes: microsecond resolution, strict parsing

- `pd.to_datetime([...]).dtype`, `pd.date_range(...).dtype`, `Series([datetime.datetime(...)]).dtype` are all
  **`datetime64[us]`** (nanoseconds in pandas 2), `Timestamp(...).unit` is `'us'`, and year 2300 parses without overflow. A list of
  `datetime.date` objects stays `object`.
- Mixed formats now raise: `to_datetime(["2024-01-01", "01/02/2024"])` -> `ValueError: time data "01/02/2024" doesn't match
  format "%Y-%m-%d"`; pass `format="mixed"` (gave Jan 2) or one explicit `format=`.
- `infer_datetime_format=` is gone (`TypeError: unexpected keyword`). `dayfirst=True` read `03/04/2024` as 3 April.
- Frequency aliases: `resample("M")` -> `ValueError: 'M' is no longer supported for offsets. Please use 'ME'`;
  `date_range(freq="H")` raises, use `"h"`.

## 4. Removed or renamed (hasattr / call checks)

Gone: `DataFrame.append`, `Series.append`, `DataFrame.applymap` (use `DataFrame.map`, which exists), `swapaxes`, `iteritems`, `mad`,
`ix`, `lookup`, `DataFrame.bool`, `Series.view`, `pd.Int64Index`, `pd.datetime`. Keyword removals:
`fillna(method="ffill")` -> `TypeError` (use `.ffill()`), `groupby(..., axis=1)` -> `TypeError`.

## 5. read_csv / to_csv on Windows

- Inference on `id,name,score,when,flag`: `int64, str, float64, str, bool`. **Dates stay `str`** unless `parse_dates=` is
  given; the `NA` token -> NaN in a float column; `dtype_backend="numpy_nullable"` gives `Int64, string, Float64,
  datetime64[us], boolean`.
- A blank cell turns an int column into `float64` (`[1.0, nan, 3.0]`); `.astype(int)` then raises `IntCastingNaNError`;
  `.astype("Int64")` gives `[1, <NA>, 3]`. A fully blank *line* is skipped (`[1, 3]`).
- Leading zeros are lost (`007` -> 7) unless `dtype=str` (`['007', '010']`).
- Non-UTF-8 bytes: `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9`; `encoding_errors="replace"` yields `caf�`.
  Say `encoding="cp1252"` or `"latin-1"` when you know it.
- **`to_csv` writes CRLF on Windows**: `b'a\r\n1\r\n2\r\n'`; pass `lineterminator="\n"` for `b'a\n1\n2\n'` (needed for
  byte-identical artefacts, see the `bit-identity-float-pipelines` skill). Default encoding is UTF-8 (`é` -> `c3 a9`).

## 6. groupby, merge, aggregation behaviours

- Categorical keys: `groupby("k")` returns only observed categories (1 row of 2); `observed=False` returns 2.
- NaN keys are dropped by default: `{'x': 4}`; `dropna=False` keeps them (`{'x': 4, nan: 2}`); `transform("sum")` returns NaN
  for the NaN-key row (`[4.0, nan, 4.0]`).
- `groupby(...).apply(f)` receives frames **without the grouping column** (`['v']` only).
- `value_counts()` returns a Series named `count` and keeps the `a`/`b` index.
- `merge` with duplicate keys on both sides yields 4 rows (many-to-many); **`validate="1:1"` / `"m:1"` raise `MergeError`** listing
  the duplicates: use them on every join whose cardinality you assume. Overlapping columns get `_x`, `_y` suffixes.
- `concat([DataFrame(), df])` gave `int64` with no warning on 3.0.6.
- `Series.sum()` of empty or all-NaN is `0.0`; `min_count=1` gives NaN; `mean()` of empty is NaN. `NaN == NaN` is False but
  `Series.equals` treats aligned NaNs as equal.
- `reindex` on an `int64` column makes it `float64`; an `Int64` column stays `Int64`.

## 7. Timing (300,000 rows, this machine)

`groupby("k").v.sum()` 4.6 ms; vectorised `df.v * 2` 1.2 ms; **`df.apply(lambda r: r.v * 2, axis=1)` 1,565 ms** (about 1,300x
slower). Avoid `axis=1` apply; use column arithmetic, `np.where`, `Series.map` or `numpy` on `to_numpy()`.

## Not covered

3.1.0rc0, `pd.read_parquet` / pyarrow dtype backend, `MultiIndex` and `pivot` edge cases, `Styler`, plotting, `eval`/`query`,
extension arrays beyond strings, and the pandas test suite itself.
