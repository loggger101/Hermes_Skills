"""sync-hermes-skills.py: the pre-push decision and error propagation.

The module's should_push() docstring cited a 'round-34 unit matrix' that was never in the
repo. This is that matrix, plus the round-256 failure paths: copy errors that used to be
details-only lines while the run exited 0.
"""

import shutil

import pytest

SYNC = "tools/sync-hermes-skills.py"

AUDIT_OK = {"action": "audit", "success": True, "threshold_breached": False}
VERIFY_OK = {"action": "verify_all", "success": True}


@pytest.fixture
def sync(load):
    return load(SYNC)


# --------------------------------------------------------------------------- should_push
@pytest.mark.parametrize(
    "audit, verify, scan_ok, want",
    [
        (AUDIT_OK, VERIFY_OK, True, True),
        ({"success": False, "threshold_breached": False}, VERIFY_OK, True, False),
        ({"success": True, "threshold_breached": True}, VERIFY_OK, True, False),
        ({"success": True}, VERIFY_OK, True, False),  # breach key missing = not proven
        ({}, VERIFY_OK, True, False),
        (AUDIT_OK, {"success": False}, True, False),
        (AUDIT_OK, {}, True, False),  # verify result without a verdict
        (AUDIT_OK, {"success": None, "skipped": True}, True, True),  # dry-run skip
        (AUDIT_OK, VERIFY_OK, False, False),  # delete cap / copy failure
    ],
)
def test_should_push_matrix(sync, audit, verify, scan_ok, want):
    push, reason = sync.should_push(5, audit, verify, scan_ok)
    assert push is want
    if not want:
        assert reason.endswith("refusing to commit/push")


def test_should_push_names_every_reason(sync):
    push, reason = sync.should_push(1, {}, {}, False)
    assert not push
    for part in ("audit did not pass", "verify-all gates failed", "safety cap"):
        assert part in reason


def test_nothing_to_publish_is_vacuously_ok(sync):
    assert sync.should_push(0, {}, {}, False) == (True, "")


# --------------------------------------------------------------------------- failed_steps
def test_failed_steps_missing_success_is_not_success(sync):
    steps = [
        {"action": "pull", "success": True},
        {"action": "pull_skills"},  # no verdict at all
        {"action": "sync_memories", "success": False},
        {"action": "indexes", "success": None, "skipped": True},
    ]
    assert sync.failed_steps(steps) == ["pull_skills", "sync_memories"]


def test_failed_steps_unknown_action_is_reported(sync):
    assert sync.failed_steps([{"action": "mystery", "success": True}]) == [
        "unknown step action 'mystery'"
    ]


# --------------------------------------------------------------------------- copy errors
def _make_skill(root, rel, text="x\n"):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def _failing_copy(monkeypatch, sync):
    def boom(src, dst, *a, **k):
        raise PermissionError(f"planted: cannot write {dst}")

    monkeypatch.setattr(sync.shutil, "copy2", boom)


def test_pull_copy_error_fails_the_step(sync, tmp_path, monkeypatch):
    repo, local = tmp_path / "repo", tmp_path / "local"
    _make_skill(repo, "devops/a/SKILL.md")
    local.mkdir()
    _failing_copy(monkeypatch, sync)
    res = sync.sync_skills_pull(repo, local)
    assert res["success"] is False
    assert res["errors"] and "planted" in res["errors"][0]
    assert sync.failed_steps([res]) == ["pull_skills"]


def test_push_copy_error_fails_the_step(sync, tmp_path, monkeypatch):
    repo, local = tmp_path / "repo", tmp_path / "local"
    repo.mkdir()
    _make_skill(local, "devops/a/SKILL.md")
    _failing_copy(monkeypatch, sync)
    res = sync.sync_skills_push(repo, local)
    assert res["success"] is False
    assert res["errors"]


def test_memory_copy_error_fails_the_step(sync, tmp_path, monkeypatch):
    repo, mem = tmp_path / "repo", tmp_path / "mem"
    repo.mkdir()
    _make_skill(mem, "MEMORY.md")
    _failing_copy(monkeypatch, sync)
    res = sync.sync_memories(repo, mem)
    assert res["success"] is False
    assert res["errors"]


def test_clean_pull_and_push_succeed(sync, tmp_path):
    repo, local = tmp_path / "repo", tmp_path / "local"
    _make_skill(repo, "devops/a/SKILL.md", "repo\n")
    local.mkdir()
    pulled = sync.sync_skills_pull(repo, local)
    assert pulled["success"] is True and pulled["files_copied"] == 1
    pushed = sync.sync_skills_push(repo, local)
    assert pushed["success"] is True
    assert (pushed["files_new"], pushed["files_copied"], pushed["files_deleted"]) == (0, 0, 0)


# --------------------------------------------------------------------------- dry run
def test_dry_run_planned_pulls_are_not_deletes_or_updates(sync, tmp_path):
    """A machine behind the repo: in dry run the pull copies nothing, and the push must
    not read the files the pull would have brought in as deleted or changed locally."""
    repo, local = tmp_path / "repo", tmp_path / "local"
    for i in range(sync.MAX_DELETIONS + 5):
        _make_skill(repo, f"devops/s{i}/SKILL.md", "new upstream\n")
    _make_skill(repo, "devops/changed/SKILL.md", "upstream v2\n")
    _make_skill(local, "devops/changed/SKILL.md", "local v1\n")
    _make_skill(local, "devops/local-only/SKILL.md", "mine\n")

    pulled = sync.sync_skills_pull(repo, local, dry_run=True)
    planned = frozenset(pulled["planned"])
    assert "devops/changed/SKILL.md" in planned

    naive = sync.sync_skills_push(repo, local, dry_run=True)
    assert naive.get("mass_delete_blocked") is True  # the false alarm this fixes

    res = sync.sync_skills_push(repo, local, dry_run=True, pulled_in_dry_run=planned)
    assert res["success"] is True
    assert res["files_deleted"] == 0
    assert res["files_copied"] == 0  # the stale local 'changed' copy is not pushed back
    assert res["files_new"] == 1  # devops/local-only is genuinely new


def test_mass_delete_cap_blocks_and_deletes_nothing(sync, tmp_path):
    repo, local = tmp_path / "repo", tmp_path / "local"
    for i in range(sync.MAX_DELETIONS + 1):
        _make_skill(repo, f"devops/s{i}/SKILL.md")
    _make_skill(local, "devops/keep/SKILL.md")
    res = sync.sync_skills_push(repo, local)
    assert res["success"] is False and res["mass_delete_blocked"] is True
    assert len(list(repo.rglob("SKILL.md"))) == sync.MAX_DELETIONS + 1 + 1  # +1 new 'keep'


def test_import_has_no_git_side_effects(load, monkeypatch):
    calls = []
    import subprocess

    real = subprocess.run
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: calls.append(a) or real(*a, **k))
    load(SYNC)
    assert not [c for c in calls if c and c[0][:2] == ["git", "config"]]


def test_shutil_not_shadowed(sync):
    assert sync.shutil is shutil
