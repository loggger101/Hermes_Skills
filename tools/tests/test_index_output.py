"""_index_output.emit(): the write-guard and --check behind every index generator.

Exit codes are the contract verify-all and the drift mutation test rely on:
1 = drift, 2 = scan below the floor (until round-256 the floor exited 1 as well).
"""

import pytest


@pytest.fixture
def io(load):
    return load("tools/_index_output.py")


def test_floor_exits_2_and_writes_nothing(io, tmp_path, capsys):
    out = tmp_path / "INDEX.md"
    out.write_text("good index\n", encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        io.emit(out, "", count=3, floor=10, label="t", check=False)
    assert e.value.code == 2
    assert out.read_text(encoding="utf-8") == "good index\n"
    assert "[FATAL]" in capsys.readouterr().err


def test_floor_applies_in_check_mode_too(io, tmp_path):
    with pytest.raises(SystemExit) as e:
        io.emit(tmp_path / "I.md", "x", count=0, floor=1, label="t", check=True)
    assert e.value.code == 2


def test_check_drift_exits_1(io, tmp_path, capsys):
    out = tmp_path / "INDEX.md"
    out.write_text("old\n", encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        io.emit(out, "new\n", count=5, floor=1, label="t", check=True)
    assert e.value.code == 1
    assert "first difference at line 1" in capsys.readouterr().out
    assert out.read_text(encoding="utf-8") == "old\n"  # check never writes


def test_check_missing_file_exits_1(io, tmp_path, capsys):
    with pytest.raises(SystemExit) as e:
        io.emit(tmp_path / "NOPE.md", "x\n", count=5, floor=1, label="t", check=True)
    assert e.value.code == 1
    assert "does not exist" in capsys.readouterr().out


def test_check_clean_returns(io, tmp_path, capsys):
    out = tmp_path / "INDEX.md"
    out.write_text("same\n", encoding="utf-8")
    io.emit(out, "same\n", count=5, floor=1, label="t", check=True)
    assert "[OK]" in capsys.readouterr().out


def test_write_mode_writes(io, tmp_path):
    out = tmp_path / "INDEX.md"
    io.emit(out, "fresh\n", count=5, floor=1, label="t", check=False)
    assert out.read_text(encoding="utf-8") == "fresh\n"


def test_wants_check(io):
    assert io.wants_check(["--check"]) is True
    assert io.wants_check([]) is False
