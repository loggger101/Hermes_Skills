""".hermes/cron/validate-skill-refs.py (verify-all gate 'cron: skill refs') on throwaway trees.

The script locates the repo from its own path, so each test copies it into a temp tree
with its own skills and job configs. Its failure paths had never been planted; and an
empty active/ dir printed "ALL OK" having checked nothing (round-257).
"""

import json
import shutil
import subprocess
import sys

from conftest import REPO

SCRIPT = REPO / ".hermes" / "cron" / "validate-skill-refs.py"


def tree(tmp_path, jobs, skills=("cat/alpha", "cat/beta")):
    cron = tmp_path / ".hermes" / "cron"
    (cron / "active").mkdir(parents=True)
    shutil.copy2(SCRIPT, cron / SCRIPT.name)
    for s in skills:
        d = tmp_path / s
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(f"---\nname: {s.split('/')[-1]}\n---\n", encoding="utf-8")
    for name, data in jobs.items():
        text = data if isinstance(data, str) else json.dumps(data)
        (cron / "active" / name).write_text(text, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(cron / SCRIPT.name)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    return proc.returncode, proc.stdout + proc.stderr


def test_all_refs_resolve(tmp_path):
    jobs = {
        "a.json": {"skills": {"loaded": ["cat/alpha", {"id": "cat/beta"}]}},
        "b.json": {"skills": "cat/alpha"},
        "c.json": {"skills": ["cat/beta"]},
    }
    rc, out = tree(tmp_path, jobs)
    assert rc == 0, out
    assert "OK:     a.json -> cat/beta (name=beta)" in out
    assert "ALL OK | jobs=3 refs=4 valid_skills=2" in out


def test_broken_ref_fails(tmp_path):
    rc, out = tree(tmp_path, {"a.json": {"skills": ["cat/alpha", "cat/gone"]}})
    assert rc == 1 and "BROKEN: a.json -> cat/gone" in out and "ISSUES" in out


def test_ref_without_id_fails(tmp_path):
    rc, out = tree(tmp_path, {"a.json": {"skills": [{"name": "alpha"}]}})
    assert rc == 1 and "BROKEN: a.json -> ?" in out


def test_misspelled_loaded_key_fails(tmp_path):
    """{'load': [...]} iterates as the dict's keys, which resolve to nothing."""
    rc, out = tree(tmp_path, {"a.json": {"skills": {"load": ["cat/alpha"]}}})
    assert rc == 1 and "BROKEN: a.json -> load" in out


def test_job_with_no_skills_is_named(tmp_path):
    rc, out = tree(tmp_path, {"a.json": {"skills": []}, "b.json": {"skills": ["cat/alpha"]}})
    assert rc == 0 and "NONE:   a.json loads no skills" in out


def test_no_jobs_is_not_all_ok(tmp_path):
    rc, out = tree(tmp_path, {"README.txt": "not a job"})
    assert rc == 2 and "no job configs" in out and "ALL OK" not in out


def test_invalid_json_fails_loudly(tmp_path):
    rc, out = tree(tmp_path, {"a.json": "{broken"})
    assert rc == 1 and "JSONDecodeError" in out
