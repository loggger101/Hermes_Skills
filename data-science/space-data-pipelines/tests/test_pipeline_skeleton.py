"""scripts/pipeline_skeleton.py offline: the helpers and validation gate against stubbed HTTP,
including every degraded path that used to pass quietly (round-257). The live NHATS run in
the module docstring stays a manual check; nothing here touches the network."""

import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pipeline_skeleton.py"


@pytest.fixture
def ps(monkeypatch):
    spec = importlib.util.spec_from_file_location("pipeline_skeleton", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod.time, "sleep", lambda s: None)
    return mod


class Resp:
    def __init__(self, status=200, payload=None, text=""):
        self.status_code, self._payload, self.text = status, payload, text

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def nhats_payload(n):
    return {
        "data": [
            {
                "des": f"A{i}",
                "fullname": f"({i})",
                "n_via_traj": 3,
                "occ": "2",
                "min_dv": {"dv": "4.5"},
                "min_dur": {"dur": "250"},
            }
            for i in range(n)
        ]
    }


# ------------------------------------------------------------------------- jpl_query
def test_jpl_query_retries_5xx_then_succeeds(ps, monkeypatch):
    calls = iter([Resp(503), Resp(502), Resp(200, {"ok": 1})])
    monkeypatch.setattr(ps.requests, "get", lambda *a, **k: next(calls))
    assert ps.jpl_query("x.api") == {"ok": 1}


def test_jpl_query_gives_up_loudly(ps, monkeypatch):
    monkeypatch.setattr(ps.requests, "get", lambda *a, **k: Resp(503))
    with pytest.raises(RuntimeError, match="HTTP 503"):
        ps.jpl_query("x.api")


# ---------------------------------------------------------------------- vizier_query
def tsv(rows, cols=("recno", "v")):
    return "\t".join(cols) + "\n" + "".join("\t".join(map(str, r)) + "\n" for r in rows)


def test_vizier_paginates_by_recno(ps, monkeypatch):
    monkeypatch.setattr(ps, "PAGE_SIZE", 2)
    pages = iter([tsv([(1, "a"), (2, "b")]), tsv([(3, "c"), (4, "d")]), tsv([])])
    seen = []

    def post(url, data, **kw):
        seen.append(data["QUERY"])
        return Resp(text=next(pages))

    monkeypatch.setattr(ps.requests, "post", post)
    df = ps.vizier_query("SELECT * FROM t")
    assert list(df["v"]) == ["a", "b", "c", "d"]
    assert seen[1].endswith("WHERE recno > 2") and seen[2].endswith("recno > 4")


def test_vizier_without_recno_raises_instead_of_truncating(ps, monkeypatch):
    monkeypatch.setattr(ps, "PAGE_SIZE", 2)
    monkeypatch.setattr(
        ps.requests, "post", lambda *a, **k: Resp(text=tsv([("a", 1), ("b", 2)], cols=("x", "y")))
    )
    with pytest.raises(RuntimeError, match="cannot be paginated past 2 rows"):
        ps.vizier_query("SELECT x, y FROM t")


def test_vizier_xml_error_page_is_not_data(ps, monkeypatch):
    xml = '<?xml version="1.0"?><VOTABLE><INFO name="QUERY_STATUS" value="ERROR"/></VOTABLE>'
    monkeypatch.setattr(ps.requests, "post", lambda *a, **k: Resp(text=xml))
    with pytest.raises(RuntimeError, match="XML error page"):
        ps.vizier_query("SELECT * FROM nope")


# --------------------------------------------------------------------- check_dataset
def frame(n=10):
    return pd.DataFrame({"a": range(n), "b": [1.0] * n})


def gate(ps, df, **kw):
    args = dict(dataset_name="t", min_rows=5, expected_columns=["a", "b"])
    args.update(kw)
    ps.check_dataset(df, **args)


def test_gate_passes_good_data(ps, capsys):
    gate(ps, frame(), critical_columns=["b"])
    assert "Validation passed [t]: 10 rows" in capsys.readouterr().out


@pytest.mark.parametrize(
    "df, kw, needle",
    [
        (frame(3), {}, "3 rows < minimum 5"),
        (frame().drop(columns="b"), {}, "missing columns: ['b']"),
        (frame().assign(c=None), {}, "completely empty columns: ['c']"),
        (frame(), {"critical_columns": ["zz"]}, "missing critical columns: ['zz']"),
    ],
)
def test_gate_hard_fails(ps, capsys, df, kw, needle):
    with pytest.raises(SystemExit) as e:
        gate(ps, df, **kw)
    assert e.value.code == 1 and needle in capsys.readouterr().out


def test_row_drop_warns(ps, capsys, tmp_path):
    sf = tmp_path / "status.json"
    sf.write_text(json.dumps({"_rows": {"t": 100}}), encoding="utf-8")
    gate(ps, frame(10), status_file=sf)
    assert "row count dropped 90%" in capsys.readouterr().out


@pytest.mark.parametrize("content", ["{broken", "[1, 2]"])
def test_unreadable_status_fails_instead_of_disabling_the_guard(ps, capsys, tmp_path, content):
    sf = tmp_path / "status.json"
    sf.write_text(content, encoding="utf-8")
    with pytest.raises(SystemExit):
        gate(ps, frame(), status_file=sf)
    assert "unreadable" in capsys.readouterr().out


# ------------------------------------------------------------------------------ main
def run_main(ps, monkeypatch, *argv, rows=6000):
    monkeypatch.setattr(ps.requests, "get", lambda *a, **k: Resp(200, nhats_payload(rows)))
    monkeypatch.setattr(sys, "argv", ["pipeline_skeleton.py", *argv])
    return ps.main()


def test_main_writes_parquet_and_status(ps, monkeypatch, tmp_path):
    # Needs pyarrow (test-requirements.txt); without it this FAILS, it does not skip.
    assert run_main(ps, monkeypatch, "--out-dir", str(tmp_path)) == 0
    df = pd.read_parquet(tmp_path / "nhats.parquet")
    assert len(df) == 6000 and df["min_delta_v_kms"].dtype.kind == "f"
    assert json.loads((tmp_path / "status.json").read_text())["_rows"] == {
        "nhats-accessible-asteroids": 6000
    }


def test_main_feeds_the_row_trend_guard(ps, monkeypatch, tmp_path, capsys):
    """main() never passed status_file, so this warning could not appear before."""
    assert run_main(ps, monkeypatch, "--format", "csv", "--out-dir", str(tmp_path), rows=9000) == 0
    assert run_main(ps, monkeypatch, "--format", "csv", "--out-dir", str(tmp_path), rows=6000) == 0
    assert "row count dropped 33%" in capsys.readouterr().out


def test_parquet_without_pyarrow_is_an_error_not_csv(ps, monkeypatch, tmp_path, capsys):
    monkeypatch.setitem(sys.modules, "pyarrow", None)  # import pyarrow -> ImportError
    assert run_main(ps, monkeypatch, "--out-dir", str(tmp_path)) == 2
    assert "needs pyarrow" in capsys.readouterr().out
    assert not list(tmp_path.iterdir())


def test_too_few_rows_stops_before_writing(ps, monkeypatch, tmp_path):
    with pytest.raises(SystemExit):
        run_main(ps, monkeypatch, "--format", "csv", "--out-dir", str(tmp_path), rows=10)
    assert not (tmp_path / "nhats.csv").exists()
