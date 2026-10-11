"""verify-all.py: gate verdicts (PASS / FAIL / SKIP) and the audit summariser.

A skip used to print PASS; any exit 77 would now be a SKIP only for a gate declared
skippable, so a mutation test that happens to fail 77 checks can never pass as a skip.
"""

import sys
import types

import pytest


@pytest.fixture
def va(load):
    return load("tools/verify-all.py")


def child(tmp_path, body, name="child.py"):
    p = tmp_path / name
    p.write_text(body, encoding="utf-8")
    return str(p)


@pytest.mark.parametrize(
    "body, may_skip, verdict",
    [
        ("print('[OK] fine')", False, "PASS"),
        ("import sys; print('broken'); sys.exit(1)", False, "FAIL"),
        ("import sys; print('skipped: no env'); sys.exit(77)", True, "SKIP"),
        ("import sys; print('77 failures'); sys.exit(77)", False, "FAIL"),
        ("raise RuntimeError('crash')", False, "FAIL"),
    ],
)
def test_run_verdicts(va, tmp_path, body, may_skip, verdict):
    label, got, note = va.run("x", [child(tmp_path, body)], cwd=tmp_path, may_skip=may_skip)
    assert got == verdict, note


def test_run_failure_note_carries_exit_code(va, tmp_path):
    _, verdict, note = va.run(
        "x", [child(tmp_path, "import sys; print('[FATAL] bad'); sys.exit(2)")], cwd=tmp_path
    )
    assert verdict == "FAIL" and "exit 2" in note and "[FATAL] bad" in note


def test_run_timeout_is_fail(va, tmp_path):
    _, verdict, note = va.run(
        "x", [child(tmp_path, "import time; time.sleep(30)")], cwd=tmp_path, timeout=1
    )
    assert verdict == "FAIL" and "TIMEOUT" in note


def _fake_audit(va, monkeypatch, stdout, rc=0):
    monkeypatch.setattr(
        va.subprocess,
        "run",
        lambda *a, **k: types.SimpleNamespace(returncode=rc, stdout=stdout, stderr=""),
    )
    return va.run_audit_gate()


@pytest.mark.parametrize(
    "stdout, rc, verdict",
    [
        ('{"skill_count": 3, "threshold_breached": false}', 0, "PASS"),
        ('{"skill_count": 3, "threshold_breached": true, "breaches": ["x"]}', 1, "FAIL"),
        ('{"skill_count": 3, "threshold_breached": false}', 1, "FAIL"),  # rc wins
        ("not json at all", 0, "FAIL"),
        ('{"threshold_breached": false}', 0, "FAIL"),  # report missing a field
        ("[1, 2]", 0, "FAIL"),
    ],
)
def test_audit_gate_verdicts(va, monkeypatch, stdout, rc, verdict):
    assert _fake_audit(va, monkeypatch, stdout, rc)[1] == verdict


def test_gate_labels_unique(va):
    assert len(va.GATE_LABELS) == len(set(va.GATE_LABELS))


def test_number_words_cover_every_suite_count_up_to_twenty(va):
    assert va.NUMBER_WORDS[0] == "One" and va.NUMBER_WORDS[-1] == "Twenty"
    assert len(va.NUMBER_WORDS) == 20


def test_main_prints_skip_and_never_says_all_passed(va, monkeypatch, capsys):
    results = {label: (label, va.PASS, "ok") for label in va.GATE_LABELS}
    results["drift: installed-plugins"] = ("drift: installed-plugins", va.SKIP, "skipped: CI")

    monkeypatch.setattr(va, "run_audit_gate", lambda: results["audit-skills"])
    monkeypatch.setattr(va, "check_doc_counts", lambda: results["doc counts"])
    monkeypatch.setattr(va, "run", lambda label, *a, **k: results[label])
    assert va.main() == 0
    out = capsys.readouterr().out
    assert "  SKIP  drift: installed-plugins" in out
    assert "ALL" not in out.split("=== verify-all ===")[1].splitlines()[-1]
    assert "1 SKIPPED" in out


def test_main_fails_on_any_fail(va, monkeypatch, capsys):
    monkeypatch.setattr(va, "run_audit_gate", lambda: ("audit-skills", va.FAIL, "x"))
    monkeypatch.setattr(va, "check_doc_counts", lambda: ("doc counts", va.PASS, "ok"))
    monkeypatch.setattr(va, "run", lambda label, *a, **k: (label, va.PASS, "ok"))
    assert va.main() == 1
    assert "FAILED (1/" in capsys.readouterr().out


def test_python_is_this_interpreter(va):
    assert va.PY == (sys.executable or "python3")
