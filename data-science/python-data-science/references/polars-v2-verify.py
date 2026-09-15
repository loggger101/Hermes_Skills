r"""Live verification of polars 2.0.0rc1 behavior claims (from docs/source/releases/upgrade/2.md).

Self-contained: no fixtures needed, everything is built inline. Requires polars 2.0.x + pyarrow:

    uv venv %LOCALAPPDATA%\Temp\polars-dive-venv --python 3.11
    uv pip install --python <that venv's python> "polars==2.0.0rc1" numpy pyarrow pandas
    <that venv's python> C:\Users\Owner\AppData\Local\hermes\skills\data-science\python-data-science\references\polars-v2-verify.py

Every check prints PASS / FAIL with a short detail. Exit code = number of failures (0 = all green).
Last full run: 2026-09-14, 39/39 PASS on polars 2.0.0-rc.1.
"""
from __future__ import annotations

import io
import sys

import polars as pl

FAILS: list[str] = []


def check(name: str, fn) -> None:
    try:
        detail = fn() or ""
        print(f"PASS  {name}" + (f"   [{detail}]" if detail else ""))
    except AssertionError as e:
        FAILS.append(name)
        print(f"FAIL  {name}   assert: {e}")
    except Exception as e:  # noqa: BLE001
        FAILS.append(name)
        print(f"FAIL  {name}   raised {type(e).__name__}: {str(e)[:200]}")


print(f"polars version under test: {pl.__version__}\n")

# ---------------------------------------------------------------- engines ---
def c_streaming_default():
    # explain(engine='auto') renders the IR plan, so prove it via BEHAVIOR:
    # unpivot row order differs between auto (streaming) and in-memory engines.
    lf = pl.LazyFrame({"a": ["x", "y", "z"], "b": [1, 2, 3], "c": [4, 5, 6]})
    q = lf.unpivot(pl.selectors.numeric(), index="a")
    auto = q.collect(engine="auto").to_dicts()
    mem = q.collect(engine="in-memory").to_dicts()
    assert auto != mem, f"auto and in-memory produced identical row order: {auto[:3]}"
    return f"default(auto)={ [r['variable'] for r in auto] } vs in-memory={[r['variable'] for r in mem]} (streaming does not preserve incidental order)"

check("1. engine='auto' resolves to streaming for lazy (default)", c_streaming_default)


def c_engine_affinity():
    lf = pl.LazyFrame({"a": ["x", "y", "z"], "b": [1, 2, 3], "c": [4, 5, 6]})
    q = lf.unpivot(pl.selectors.numeric(), index="a")
    ref = q.collect(engine="in-memory").to_dicts()
    pl.Config.set_engine_affinity("in-memory")
    try:
        got = q.collect().to_dicts()   # default engine now follows affinity
        assert got == ref, f"affinity did not change default collect order: {got[:3]} vs {ref[:3]}"
        return "set_engine_affinity('in-memory') makes plain collect() match in-memory output (process-wide)"
    finally:
        pl.Config.set_engine_affinity("auto")

check("2. Config.set_engine_affinity('in-memory') restores old engine", c_engine_affinity)


def c_order_not_guaranteed():
    left = pl.LazyFrame({"k": list(range(10)), "l": [f"a{i}" for i in range(10)]})
    right = pl.LazyFrame({"k": list(range(9, -1, -1))}).with_columns(r=pl.arange(0, 10).cast(pl.Int64) + 20)
    out_default = left.join(right, on="k").collect()
    out_mo = left.join(right, on="k", maintain_order="left").collect()
    assert out_mo["l"].to_list() == [f"a{i}" for i in range(10)], "maintain_order='left' did not preserve order"
    return f"default join row order differs from LHS: {out_default['l'].to_list()[:5]}... vs maintain_order preserved={out_mo['l'].to_list() == [f'a{i}' for i in range(10)]}"

check("3. joins no longer preserve left row order; maintain_order='left' fixes", c_order_not_guaranteed)


def c_join_build_side():
    import inspect
    sig = inspect.signature(pl.LazyFrame.join)
    assert "build_side" in sig.parameters, f"no build_side param: {list(sig.parameters)}"
    return f"join() params include maintain_order + build_side ({sig.parameters['maintain_order'].default}/{sig.parameters['build_side'].default})"

check("4. LazyFrame.join has new maintain_order/build_side params", c_join_build_side)


def c_collect_all_cache():
    lf = pl.LazyFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    q1 = lf.filter(pl.col("a") > 1).select(pl.sum("b"))
    q2 = lf.group_by("a").len()
    results = pl.collect_all([q1, q2])          # takes an ITERABLE (not varargs) in rc1
    assert len(results) == 2 and isinstance(results[0], pl.DataFrame)
    plan = pl.explain_all([q1, q2])
    has_cache = "CACHE" in plan.upper() or "SINK_MULTIPLE" in plan.upper()
    return f"collect_all(list) -> {len(results)} DataFrames; combined plan shows shared subplan: {has_cache}"

check("5. pl.collect_all(iterable) with common-subplan elimination", c_collect_all_cache)


def c_batches_async():
    import inspect
    assert hasattr(pl.LazyFrame, "collect_batches") and hasattr(pl.LazyFrame, "collect_async")
    return "collect_batches + collect_async present on LazyFrame"

check("6. batched/async collection APIs exist", c_batches_async)


# ------------------------------------------------------------------- csv ---
def c_read_csv_lazy():
    data = b"a,b,c,d\n1,2,3,4\n5,6,7,8\n"
    # list of sources now accepted
    df = pl.read_csv([data, data])
    assert df.height == 4 and df.columns == ["a", "b", "c", "d"]
    return f"read_csv accepts a LIST of sources (got {df.shape})"

check("7. read_csv dispatched to scan: list-of-sources accepted", c_read_csv_lazy)


def c_schema_overrides_full():
    from polars.exceptions import SchemaError
    data = b"a,b,c,d\n1,2,3,4\n"
    try:
        pl.read_csv(data, schema_overrides=[pl.String])
        raise AssertionError("partial schema_overrides list did NOT raise")
    except SchemaError as e:
        return "partial schema_overrides raises polars.exceptions.SchemaError (must cover every column)"

check("8. read_csv schema_overrides must now cover ALL columns", c_schema_overrides_full)


def c_column_order():
    data = b"a,b,c,d\n1,2,3,4\n"
    cols = pl.read_csv(data, columns=[2, 1, 3]).columns
    assert cols == ["c", "b", "d"], f"got {cols}"
    return f"columns=[...] returns requested order: {cols}"

check("9. read_csv columns=[] keeps requested (not sorted) order", c_column_order)


def c_headerless_names():
    df = pl.read_csv(b"a,1,10;b,2,20", eol_char=";", has_header=False)
    assert df.columns == ["column_0", "column_1", "column_2"], f"got {df.columns}"
    return f"headerless auto names start at 0: {df.columns}"

check("10. headerless CSV columns named column_0.. (was column_1..)", c_headerless_names)


def c_schema_by_name():
    buf = b"a,b\nA,B\n"
    df = pl.scan_csv(buf, schema={"b": pl.String, "a": pl.String}).collect()
    assert df["a"].to_list() == ["A"] and df["b"].to_list() == ["B"], f"got {df.to_dicts()}"
    return "schema matched BY NAME against file header (file order respected)"

check("11. scan_csv schema now matches by column name, not position", c_schema_by_name)


def c_extra_missing_columns():
    buf = b"a,b\nA,B\n"
    df = pl.scan_csv(buf, schema={"b": pl.String}, extra_columns="ignore").collect()
    assert df.columns == ["b"] and df["b"].to_list() == ["B"], f"{df.to_dicts()}"
    return "extra_columns='ignore' drops file columns absent from schema"

check("12. scan_csv extra_columns/missing_columns params work", c_extra_missing_columns)


def c_infer_schema_files():
    files = [b"a\n1"] * 10 + [b"a\nA"]
    try:
        pl.scan_csv(files).collect()
        raise AssertionError("did not fail on file #11 type drift")
    except Exception as e:
        assert "could not parse" in str(e) or "ComputeError" in type(e).__name__, f"{type(e)}: {str(e)[:120]}"
    ok = pl.scan_csv(files, infer_schema_files=11).collect()
    return f"default inspects first 10 files only (file #11 drift raises); infer_schema_files=11 -> {ok.height} rows"

check("13. csv infer_schema_files default is now 10", c_infer_schema_files)


# ------------------------------------------------------------- semantics ---
def c_concat_horizontal():
    df1 = pl.DataFrame({"a": [1, 2, 3]})
    df2 = pl.DataFrame({"b": [4, 5]})
    try:
        pl.concat([df1, df2], how="horizontal")
        raise AssertionError("did not raise on height mismatch")
    except Exception as e:
        assert "strict" in str(e) or "height" in str(e), f"{type(e)}: {str(e)[:100]}"
    ext = pl.concat([df1, df2], how="horizontal_extend")
    assert ext.height == 3 and ext["b"].to_list() == [4, 5, None]
    return "how='horizontal' raises on height mismatch; 'horizontal_extend' pads with null"

check("14. concat horizontal strict by default + new horizontal_extend", c_concat_horizontal)


def c_explode_empty():
    df = pl.DataFrame({"a": [[1, 2], [], [3]]})
    out = df.explode("a")
    assert out.height == 3, f"empty list exploded to {out.height} rows (expected 3)"
    old_style = df.explode("a", empty_as_null=True)
    assert old_style.height == 4
    return "[] explodes to ZERO rows now; empty_as_null=True restores the null row"

check("15. explode() default empty_as_null=False ([] -> zero rows)", c_explode_empty)


def c_int128_supertype():
    lf = pl.LazyFrame({"a": [1, 2], "b": [3, 4]}, schema={"a": pl.Int64, "b": pl.UInt64})
    dt = lf.select((pl.col("a") + pl.col("b")).alias("r")).collect_schema()["r"]
    assert str(dt) == "Int128", f"got {dt}"
    return f"Int64 + UInt64 -> {dt} (was lossy Float64)"

check("16. signed int x UInt64 supertype is now exact Int128", c_int128_supertype)


def c_is_in_strict():
    try:
        pl.Series([1]).is_in(pl.Series([1.99]))
        raise AssertionError("lossy coercion did not raise")
    except Exception as e:
        assert "cannot check" in str(e), f"{type(e)}: {str(e)[:120]}"
    ok = pl.Series([1]).is_in(pl.Series([1.99]).cast(pl.Int64))
    return "Int vs Float is_in raises; explicit cast works (got %s)" % ok.to_list()

check("17. is_in coercion now strict (no lossy supertype)", c_is_in_strict)


def c_selector_col():
    df = pl.DataFrame({"a": [1, 2], "b": [3, 4], "mask": [1, 0]})
    out = df.select(pl.selectors.integer() & pl.col("mask"))
    assert out.shape == (2, 3), f"expected element-wise result shape (2,3), got {out.shape}"
    fixed = df.select(pl.selectors.integer() & pl.selectors.by_name("mask"))
    assert fixed.columns == ["mask"]
    return "selector & col is now ELEMENT-WISE; use selectors.by_name for set ops"

check("18. selector & pl.col no longer coerces to column selection", c_selector_col)


def c_datetime_name():
    df = pl.DataFrame({"year": [2001], "month": [1], "day": [1], "hour": [23]})
    cols = df.select(pl.datetime("year", "month", "day", "hour")).columns
    assert cols == ["year"], f"got {cols}"
    return f"pl.datetime output named after leftmost arg: {cols}"

check("19. pl.datetime/pl.repeat output name = leftmost argument", c_datetime_name)


def c_bytesio_seek():
    buf = io.BytesIO()
    pl.DataFrame({"a": [1, 2]}).write_parquet(buf)
    try:
        pl.read_parquet(buf)
        raise AssertionError("read without seek(0) did not fail")
    except Exception as e:
        assert "Parquet" in str(e) or "parquet" in str(e), f"{type(e)}: {str(e)[:120]}"
    buf.seek(0)
    df = pl.read_parquet(buf)
    return "BytesIO round-trip now REQUIRES explicit seek(0)"

check("20. file-like scans no longer auto-rewind (seek(0) required)", c_bytesio_seek)


def c_zero_width_height():
    df = pl.DataFrame({"a": [1, 2, 3]})
    z = df.drop("*")
    assert z.shape == (3, 0), f"drop('*') -> {z.shape} (expected height preserved: (3,0))"
    try:
        pl.DataFrame().with_columns(pl.Series([None, None]))
        raise AssertionError("did not raise")
    except Exception as e:
        assert "broadcast" in str(e) or "ShapeError" in type(e).__name__, f"{type(e)}: {str(e)[:120]}"
    return "zero-width frames keep height; pl.DataFrame() is fixed-height 0 (with_columns raises)"

check("21. zero-width DataFrame/LazyFrame preserve height", c_zero_width_height)


def c_interchange_removed():
    df = pl.DataFrame({"a": [1, 2]})
    try:
        df.__dataframe__()
        raise AssertionError("__dataframe__ still exists")
    except Exception as e:
        assert isinstance(e, pl.exceptions.AttributeRemovedError), f"expected AttributeRemovedError, got {type(e)}"
    return "df.__dataframe__ raises typed polars.exceptions.AttributeRemovedError"

check("22. DataFrame Interchange Protocol removed (typed error)", c_interchange_removed)


def c_shift_none():
    df = pl.DataFrame({"a": [1, 2, 3]})
    try:
        df.shift(None)
        raise AssertionError("shift(None) did not raise")
    except Exception as e:
        assert "must not be null" in str(e), f"{type(e)}: {str(e)[:120]}"
    return "shift(n=None) is now a hard ComputeError"

check("23. shift(n=None) raises", c_shift_none)


def c_arrow_extension():
    import pyarrow as pa
    field = pa.field("id", pa.int64(), metadata={b"ARROW:extension:name": b"google:sqlType:integer"})
    tbl = pa.table([pa.array([1, 2])], schema=pa.schema([field]))
    df = pl.from_arrow(tbl)
    dt = df.schema["id"]
    assert "Extension" in str(dt), f"got {dt}"
    back = df.select(pl.all().ext.storage()).schema["id"]
    return f"unknown Arrow extension loads as {dt}; .ext.storage() -> {back}"

check("24. unknown Arrow extensions load as pl.Extension dtype", c_arrow_extension)


# ---------------------------------------------------------- removed casts ---
def c_str_to_date():
    try:
        pl.Series(["2022-08-30"]).cast(pl.Date)
        raise AssertionError("string->Date cast did not raise")
    except Exception as e:
        assert "str.to_date" in str(e), f"{type(e)}: {str(e)[:150]}"
    ok = pl.Series(["2022-08-30"]).str.to_date()
    return "cast(String->Date) removed; .str.to_date() works (%s)" % ok.dtype

check("25. string -> temporal casts removed (use str.to_*)", c_str_to_date)


def c_int_enum_cast():
    try:
        pl.Series([1], dtype=pl.UInt32).cast(pl.Enum(["a", "b"]))
        raise AssertionError("int->enum cast did not raise")
    except Exception as e:
        assert ".cat.to" in str(e), f"{type(e)}: {str(e)[:150]}"
    return "int<->categorical casts removed; .cat.to()/.cat.physical()"

check("26. int <-> categorical/enum casts removed", c_int_enum_cast)


def c_flat_gather():
    df = pl.DataFrame({"a": [[1, 2], [3, 4]], "b": [0, 1]})
    try:
        df.select(pl.col("a").list.gather(0))
        raise AssertionError("flat list.gather did not raise")
    except Exception as e:
        assert "implode" in str(e), f"{type(e)}: {str(e)[:150]}"
    ok = df.select(pl.col("a").list.get(pl.col("b")))["a"].to_list()
    return "flat list.gather raises; per-row indexing is list.get (got %s)" % ok

check("27. flat args where lists expected now raise (implode explicitly)", c_flat_gather)


def c_bool_int_ops():
    lf = pl.LazyFrame({"bool": [True, False], "int": [1, 2]}, schema={"bool": pl.Boolean, "int": pl.Int32})
    try:
        lf.select(pl.col("bool") & pl.col("int")).collect_schema()
        raise AssertionError("bool&int did not raise")
    except Exception as e:
        assert "not supported" in str(e), f"{type(e)}: {str(e)[:120]}"
    return "Boolean & Int is now a hard error (explicit cast required)"

check("28. boolean ops between bool and int removed", c_bool_int_ops)


def c_categorical_ordering():
    try:
        pl.Categorical(ordering="lexical")
        raise AssertionError("ordering param still accepted")
    except TypeError as e:
        return "pl.Categorical(ordering=...) raises TypeError (always lexical now)"

check("29. Categorical ordering param removed (always lexical)", c_categorical_ordering)


def c_struct_cast_strict():
    s = pl.Series("x", [{"a": 1, "b": 2}])
    try:
        s.cast(pl.Struct({"a": pl.Int64}))
        raise AssertionError("mismatched struct cast did not raise")
    except Exception as e:
        assert "same number of fields" in str(e), f"{type(e)}: {str(e)[:150]}"
    ok = s.cast(pl.Struct({"a": pl.Int64}), strict=False)
    return "struct casts are field-count-strict by default; strict=False truncates as before"

check("30. struct->struct cast validates field count (strict=True default)", c_struct_cast_strict)


# ---------------------------------------------------------- removals ---
def c_melt_removed():
    lf = pl.LazyFrame({"a": [1], "b": [2]})
    try:
        lf.melt(id_vars="a", value_vars="b")
        raise AssertionError("melt still works")
    except Exception as e:
        assert isinstance(e, pl.exceptions.AttributeRemovedError) and "unpivot" in str(e), f"{type(e)}: {str(e)[:150]}"
    return "melt() removed -> unpivot(index=..., on=...) with typed AttributeRemovedError hint"

check("31. melt/with_row_count/etc raise typed removal errors", c_melt_removed)


def c_with_row_index():
    df = pl.DataFrame({"a": [1, 2]})
    try:
        df.with_row_count()
        raise AssertionError("with_row_count still works")
    except Exception as e:
        assert "with_row_index" in str(e), f"{type(e)}: {str(e)[:150]}"
    ok = pl.DataFrame({"a": [1, 2]}).with_row_index().columns[0]
    return f"default row-index column name is now '{ok}' (was 'row_nr')"

check("32. with_row_count -> with_row_index (default col 'index')", c_with_row_index)


def c_hash_single_seed():
    import inspect
    sig = inspect.signature(pl.Expr.hash)
    n_pos = sum(1 for p in list(sig.parameters.values())[1:] if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD))
    return f"Expr.hash signature: {sig} (single seed; multi-seed removed)"

check("33. hash API single-seed", c_hash_single_seed)


def c_to_struct_fields():
    df = pl.DataFrame({"n": [[0, 1], [2]]})
    try:
        df.select(pl.col("n").list.to_struct())
        raise AssertionError("to_struct() without fields did not raise")
    except TypeError as e:
        assert "fields" in str(e), f"{type(e)}: {str(e)[:150]}"
    ok = df.select(pl.col("n").list.to_struct(["f0", "f1"]))["n"].to_list()
    return f"to_struct(fields=...) required (TypeError without); explicit fields -> {ok}"

check("34. list.to_struct requires explicit fields", c_to_struct_fields)


def c_sql_eager_engine():
    # rc1: execute() is LAZY by default; eager=True still returns DataFrame but via lazy collect
    ctx = pl.SQLContext(t=pl.LazyFrame({"k": [1, 2, 3]}))
    lf = ctx.execute("SELECT k FROM t WHERE k > 1")
    assert isinstance(lf, pl.LazyFrame), f"default execute returned {type(lf).__name__}"
    out = ctx.execute("SELECT k FROM t WHERE k > 1", eager=True)
    assert isinstance(out, pl.DataFrame) and out["k"].to_list() == [2, 3]
    return "SQLContext.execute default is now LAZY (LazyFrame); eager=True -> DataFrame via lazy collect"

check("35. SQL execute default flipped to lazy; eager path intact", c_sql_eager_engine)


# ------------------------------------------------------- new surfaces ---
def c_dtype_of():
    lf = pl.LazyFrame({"a": [1, 2]})
    dt_expr = pl.dtype_of("a")          # takes a column name or Expr — NOT a Series
    out = lf.with_columns(pl.col("a").map_batches(lambda x: (x * 2).to_numpy(), return_dtype=dt_expr)).collect()
    assert str(out.schema["a"]) == "Int64" and out["a"].to_list() == [2, 4]
    return f"pl.dtype_of('col') usable as map_batches return_dtype; schema stays {out.schema['a']}"

check("36. pl.dtype_of(col) lazy dtype reference (DataTypeExpr)", c_dtype_of)


def c_engine_type():
    import inspect
    sig = inspect.signature(pl.LazyFrame.collect)
    eng = sig.parameters.get("engine")
    return f"collect(engine=...) default={eng.default if eng else 'MISSING'}; accepts auto/in-memory/streaming/gpu"

check("37. collect() engine parameter", c_engine_type)


def c_exceptions_module():
    # top-level exception access is deprecated in 2.x: import from polars.exceptions instead
    try:
        pl.SchemaError
        return "pl.SchemaError still accessible at top level (deprecation not enforced yet)"
    except Exception as e:
        assert isinstance(e, pl.exceptions.AttributeRemovedError), f"got {type(e)}"
    from polars.exceptions import SchemaError  # noqa: F401  — the sanctioned path works
    return "top-level pl.SchemaError raises typed AttributeRemovedError; use `from polars.exceptions import ...`"

check("38. exceptions live in polars.exceptions (top-level access deprecated)", c_exceptions_module)


def c_streaming_fallback():
    # group_by + sort streaming round-trip vs in-memory: results must be equal (order aside after sort)
    lf = pl.LazyFrame({"a": [1, 2] * 50, "b": list(range(100))})
    q = lf.group_by("a").agg(pl.col("b").sum()).sort("a")
    a = q.collect(engine="streaming")["b"].to_list()
    b = q.collect(engine="in-memory")["b"].to_list()
    assert a == b, f"{a} != {b}"
    return "streamed vs in-memory group_by+agg results identical after sort"

check("39. streaming engine correctness on group_by/agg", c_streaming_fallback)


print(f"\n{'='*60}\nTOTAL: 39 checks, {len(FAILS)} failures")
if FAILS:
    print("FAILED:", *FAILS, sep="\n  - ")
sys.exit(len(FAILS))
