"""The four architecture-metrics scripts on fixture projects.

Round-257 cases: a file that stops parsing used to vanish from every metric (so breaking a
file's syntax made a session score better and the gates pass); quality_signal.py documented
a --baseline gate that was never implemented (always exit 0); a missing project dir scored
as a flawless empty project; `--dsm N` / `--days N` before the path took N as the path; and
evolution_metrics.py's merge detection queried a reflog index instead of a date.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def run(script, *args, cwd=None):
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / script), *map(str, args)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=cwd,
        timeout=180,
    )
    return proc.returncode, proc.stdout, proc.stderr


def write(root, files):
    for rel, src in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(src, encoding="utf-8")


PROJECT = {
    "pkg/__init__.py": "",
    "pkg/a.py": "import pkg.b\n\n\ndef fa(x):\n    return pkg.b.fb(x)\n",
    "pkg/b.py": "import pkg.c\n\n\ndef fb(x):\n    return pkg.c.fc(x) + 1\n",
    "pkg/c.py": "def fc(x):\n    if x:\n        return 1\n    return 0\n",
}
CYCLE = {
    "pkg/x.py": "import pkg.y\n\n\ndef fx():\n    return pkg.y\n",
    "pkg/y.py": "import pkg.x\n\n\ndef fy():\n    return pkg.x\n",
}


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "proj"
    write(root, PROJECT)
    return root


def am_json(root, *extra):
    rc, out, err = run("architecture_metrics.py", root, "--json", *extra)
    assert rc == 0, err
    return json.loads(out)


# ------------------------------------------------------------------- architecture_metrics
def test_architecture_graph(project):
    r = am_json(project)
    assert (r["files"], r["edges"], r["max_level"]) == (4, 2, 2)
    assert r["unparsable_files"] == [] and r["cycle_count"] == 0


def test_cycle_is_counted(project):
    write(project, CYCLE)
    assert am_json(project)["cycle_count"] == 1


def test_unparsable_file_is_reported_not_dropped(project):
    write(project, {"pkg/b.py": "import pkg.c\ndef fb(:\n"})
    r = am_json(project)
    assert r["unparsable_files"][0]["file"] == "pkg/b.py"
    assert "SyntaxError line 2" in r["unparsable_files"][0]["reason"]
    rc, out, _ = run("architecture_metrics.py", project)
    assert rc == 0 and "UNPARSABLE (left out of every metric): pkg/b.py" in out


def test_dsm_before_the_path(project):
    rc, out, err = run("architecture_metrics.py", "--dsm", "5", project)
    assert rc == 0, err
    assert "files=4" in out and "DSM marks" in out


@pytest.mark.parametrize("where", ["missing", "empty"])
def test_no_project_is_an_error(tmp_path, where):
    target = tmp_path / where
    if where == "empty":
        target.mkdir()
    rc, _, err = run("architecture_metrics.py", target, "--json")
    assert rc != 0 and ("no such directory" in err or "no readable .py files" in err)


# ------------------------------------------------------------------------- session_gate
def test_session_gate_pass_and_cycle(project, tmp_path):
    base = tmp_path / "base.json"
    assert run("session_gate.py", "save", project, "--baseline", base)[0] == 0
    rc, out, _ = run("session_gate.py", "check", project, "--baseline", base)
    assert rc == 0 and "RESULT: PASS" in out
    write(project, CYCLE)
    rc, out, _ = run("session_gate.py", "check", project, "--baseline", base)
    assert rc == 1 and "Cycles increased: 0 → 1" in out


def test_session_gate_catches_a_broken_file(project, tmp_path):
    """A syntax error used to remove the file from the scan and could pass the gate."""
    base = tmp_path / "base.json"
    run("session_gate.py", "save", project, "--baseline", base)
    write(project, {"pkg/c.py": "def fc(x:\n"})
    rc, out, _ = run("session_gate.py", "check", project, "--baseline", base)
    assert rc == 1 and "Unparsable files increased: 0 → 1 (pkg/c.py)" in out


def test_session_gate_needs_a_baseline_and_args(project, tmp_path):
    rc, _, err = run("session_gate.py", "check", project, "--baseline", tmp_path / "none.json")
    assert rc != 0 and "No baseline" in err
    rc, _, err = run("session_gate.py")
    assert rc != 0 and "Session quality gate" in err


# ------------------------------------------------------------------------ quality_signal
def test_quality_signal_report(project):
    rc, out, err = run("quality_signal.py", project, "--json")
    assert rc == 0, err
    r = json.loads(out)
    assert 0 < r["quality_signal"] <= 10000 and r["raw"]["cycles"] == 0
    assert set(r["scores"]) == {"modularity", "acyclicity", "depth", "equality", "redundancy"}


def test_quality_signal_baseline_gate(project, tmp_path):
    """--save-baseline/--baseline were documented, never implemented, and always exited 0."""
    base = tmp_path / "qs.json"
    rc, out, _ = run("quality_signal.py", project, "--save-baseline", base)
    assert rc == 0 and base.is_file()
    rc, out, _ = run("quality_signal.py", project, "--baseline", base)
    assert rc == 0 and "RESULT: PASS" in out
    write(project, CYCLE)
    rc, out, _ = run("quality_signal.py", project, "--baseline", base)
    assert rc == 1 and "cycles increased 0 -> 1" in out


def test_quality_signal_gate_catches_a_broken_file(project, tmp_path):
    base = tmp_path / "qs.json"
    run("quality_signal.py", project, "--save-baseline", base)
    write(project, {"pkg/a.py": "import pkg.b\ndef fa(:\n"})
    rc, out, _ = run("quality_signal.py", project, "--baseline", base)
    assert rc == 1 and "unparsable files increased 0 -> 1" in out


@pytest.mark.parametrize(
    "args, needle",
    [
        (["--baseline"], "usage: --baseline FILE.json"),
        (["--frobnicate"], "unknown option(s): --frobnicate"),
        (["--baseline", "nope.json"], "no baseline at"),
    ],
)
def test_quality_signal_bad_args(project, args, needle):
    rc, _, err = run("quality_signal.py", project, *args)
    assert rc != 0 and needle in err


# --------------------------------------------------------------------- evolution_metrics
@pytest.fixture
def repo(tmp_path, monkeypatch):
    cfg = tmp_path / "gitconfig"
    cfg.write_text("", encoding="utf-8")
    for k, v in {
        "GIT_CONFIG_GLOBAL": str(cfg),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "Ann",
        "GIT_AUTHOR_EMAIL": "a@example.invalid",
        "GIT_COMMITTER_NAME": "Ann",
        "GIT_COMMITTER_EMAIL": "a@example.invalid",
    }.items():
        monkeypatch.setenv(k, v)
    root = tmp_path / "repo"
    root.mkdir()

    def git(*a):
        subprocess.run(["git", *a], cwd=root, check=True, capture_output=True)

    git("init", "-q", "-b", "main")
    for i in range(4):  # a.py and b.py change together 4 times: a coupling pair
        write(root, {"a.py": f"x = {i}\n", "b.py": f"y = {i}\n"})
        git("add", "-A")
        git("commit", "-q", "-m", f"c{i}")
    git("checkout", "-q", "-b", "side")
    write(root, {"side.py": "s = 1\n"})
    git("add", "-A")
    git("commit", "-q", "-m", "side")
    git("checkout", "-q", "main")
    write(root, {"c.py": "z = 1\n"})
    git("add", "-A")
    git("commit", "-q", "-m", "main-only")
    git("merge", "-q", "--no-ff", "-m", "merge side", "side")
    return root


def test_evolution_metrics(repo):
    rc, out, err = run("evolution_metrics.py", repo, "--days", "30", "--json")
    assert rc == 0, err
    r = json.loads(out)
    assert r["commits_analyzed"] == 6  # 4 + side + main-only; the merge is skipped
    churn = {c["file"]: c["commits"] for c in r["top_churn"]}
    assert churn["a.py"] == 4 and churn["side.py"] == 1
    pair = r["coupling_pairs_top"][0]
    assert (pair["file_a"], pair["file_b"], pair["co_changes"]) == ("a.py", "b.py", 4)


def test_evolution_days_before_the_path(repo):
    rc, out, err = run("evolution_metrics.py", "--days", "30", repo, "--json")
    assert rc == 0, err
    assert json.loads(out)["lookback_days"] == 30


def test_evolution_not_a_repo(tmp_path):
    rc, _, err = run("evolution_metrics.py", tmp_path, "--json")
    assert rc != 0 and "git log failed" in err


def test_merge_with_changes_is_skipped(repo):
    """A merge that resolves a conflict carries its own numstat; it must still be skipped."""
    env = dict(os.environ)
    subprocess.run(["git", "checkout", "-q", "-b", "c2"], cwd=repo, check=True, env=env)
    write(repo, {"a.py": "x = 'branch'\n"})
    subprocess.run(["git", "commit", "-qam", "branch edit"], cwd=repo, check=True, env=env)
    subprocess.run(["git", "checkout", "-q", "main"], cwd=repo, check=True, env=env)
    write(repo, {"a.py": "x = 'main'\n"})
    subprocess.run(["git", "commit", "-qam", "main edit"], cwd=repo, check=True, env=env)
    subprocess.run(["git", "merge", "-q", "c2"], cwd=repo, env=env, capture_output=True)
    write(repo, {"a.py": "x = 'resolved'\n"})
    subprocess.run(["git", "commit", "-qam", "resolve"], cwd=repo, check=True, env=env)
    rc, out, err = run("evolution_metrics.py", repo, "--days", "30", "--json")
    assert rc == 0, err
    assert json.loads(out)["commits_analyzed"] == 8  # +2 edits, the conflict merge skipped
