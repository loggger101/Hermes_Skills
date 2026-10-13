"""sync-hermes-skills.py: the git steps (round-257).

Every test drives real git against throwaway repos and a local bare remote, so an exit
code the code under test ignores shows up as a wrong verdict here. Before round-257 a
failed `git push` left the step at success=True (exit 0, a NOTE in the output), a failed
`git status` read as "No changes", and `git add` / `git rev-parse` exit codes were unread.
"""

import subprocess

import pytest

SYNC = "tools/sync-hermes-skills.py"


@pytest.fixture
def sync(load):
    return load(SYNC)


@pytest.fixture(autouse=True)
def isolated_git(tmp_path, monkeypatch):
    """No user/system git config (hooks, signing, credential helpers) leaks into a test."""
    empty = tmp_path / "empty.gitconfig"
    empty.write_text("", encoding="utf-8")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(empty))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("GIT_TERMINAL_PROMPT", "0")
    for var in ("GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME"):
        monkeypatch.setenv(var, "test")
    for var in ("GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL"):
        monkeypatch.setenv(var, "test@example.invalid")


def git(cwd, *args):
    proc = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    assert proc.returncode == 0, f"fixture git {args} failed: {proc.stderr}"
    return proc.stdout.strip()


@pytest.fixture
def clone(tmp_path):
    """A clone with one pushed commit, tracking a local bare remote."""
    remote = tmp_path / "remote.git"
    git(tmp_path, "init", "--bare", "-b", "main", str(remote))
    work = tmp_path / "work"
    git(tmp_path, "clone", str(remote), str(work))
    git(work, "checkout", "-b", "main")
    (work / "a.md").write_text("one\n", encoding="utf-8")
    git(work, "add", "-A")
    git(work, "commit", "-m", "init")
    git(work, "push", "-u", "origin", "main")
    return work, remote


# ------------------------------------------------------------------ git_add_commit_push
def test_push_lands_on_the_remote(sync, clone):
    work, remote = clone
    (work / "b.md").write_text("two\n", encoding="utf-8")
    res = sync.git_add_commit_push(work, "add b")
    assert res["success"] is True and res["pushed"] is True, res
    assert git(remote, "rev-parse", "HEAD")[:12] == res["commit_hash"]


def test_clean_tree_is_success_without_commit(sync, clone):
    work, _ = clone
    res = sync.git_add_commit_push(work, "nothing")
    assert res["success"] is True and res["pushed"] is False
    assert res["output"] == "No changes to commit"


def test_failed_push_fails_the_step(sync, clone):
    """The old code returned success=True here; main() then exited 0 with the commit local."""
    work, _ = clone
    git(work, "remote", "set-url", "origin", str(work.parent / "no-such-remote.git"))
    (work / "b.md").write_text("two\n", encoding="utf-8")
    res = sync.git_add_commit_push(work, "add b", max_retries=1)
    assert res["success"] is False and res["pushed"] is False, res
    assert res["error"].startswith("git push failed") and "exists locally only" in res["error"]
    assert res["commit_hash"]  # the commit happened; the report must name it
    assert sync.failed_steps([res]) == ["push"]


def test_failed_status_is_not_a_clean_tree(sync, tmp_path):
    """Outside a repo `git status` fails with empty stdout; that once meant 'No changes'."""
    not_a_repo = tmp_path / "plain"
    not_a_repo.mkdir()
    res = sync.git_add_commit_push(not_a_repo, "x")
    assert res["success"] is False and res["error"].startswith("git status failed"), res


def test_failed_commit_fails_the_step(sync, clone):
    work, _ = clone
    hook = work / ".git" / "hooks" / "pre-commit"
    hook.write_text("#!/bin/sh\necho refused by hook >&2\nexit 1\n", encoding="utf-8")
    hook.chmod(0o755)
    (work / "b.md").write_text("two\n", encoding="utf-8")
    res = sync.git_add_commit_push(work, "add b")
    assert res["success"] is False and res["error"].startswith("git commit failed"), res
    assert res["pushed"] is False and res["commit_hash"] is None


def test_failed_add_fails_the_step(sync, clone, monkeypatch):
    """`git add -A` was run without reading its exit code."""
    work, _ = clone
    (work / "b.md").write_text("two\n", encoding="utf-8")
    real_run = subprocess.run

    def run(cmd, *a, **kw):
        if cmd[:2] == ["git", "add"]:
            return subprocess.CompletedProcess(cmd, 128, "", "fatal: index.lock exists")
        return real_run(cmd, *a, **kw)

    monkeypatch.setattr(sync.subprocess, "run", run)
    res = sync.git_add_commit_push(work, "add b")
    assert res["success"] is False and res["error"].startswith("git add failed"), res
    assert "index.lock" in res["error"]


def test_dry_run_commits_nothing_and_claims_no_push(sync, clone):
    """Dry run used to set pushed=True ('Pretend success')."""
    work, remote = clone
    before = git(remote, "rev-parse", "HEAD")
    (work / "b.md").write_text("two\n", encoding="utf-8")
    res = sync.git_add_commit_push(work, "add b", dry_run=True)
    assert res["success"] is True and res["pushed"] is False and res["would_push"] is True
    assert git(work, "status", "--porcelain")  # still uncommitted
    assert git(remote, "rev-parse", "HEAD") == before


# ----------------------------------------------------------------------------- git_pull
def test_pull_outside_a_repo_fails(sync, tmp_path):
    plain = tmp_path / "plain"
    plain.mkdir()
    for dry in (False, True):
        res = sync.git_pull(plain, dry_run=dry)
        assert res["success"] is False and res["output"].startswith("git status failed"), res


def test_pull_clean_clone_succeeds(sync, clone):
    work, _ = clone
    res = sync.git_pull(work)
    assert res["success"] is True, res


def test_failed_stash_on_dirty_tree_stops_before_pull(sync, clone, monkeypatch):
    work, _ = clone
    (work / "a.md").write_text("edited\n", encoding="utf-8")
    real_run = subprocess.run
    calls = []

    def run(cmd, *a, **kw):
        calls.append(cmd[:2])
        if cmd[:2] == ["git", "stash"]:
            return subprocess.CompletedProcess(cmd, 1, "", "stash refused")
        return real_run(cmd, *a, **kw)

    monkeypatch.setattr(sync.subprocess, "run", run)
    res = sync.git_pull(work)
    assert res["success"] is False and "stash refused" in res["error"], res
    assert ["git", "pull"] not in calls  # never rebased over uncommitted work


# ------------------------------------------------------------------------- configure_git
def test_configure_git_failure_is_fatal(sync, tmp_path, monkeypatch):
    plain = tmp_path / "plain"
    plain.mkdir()
    monkeypatch.setattr(sync, "REPO_ROOT", plain)
    with pytest.raises(SystemExit) as exc:
        sync.configure_git()
    assert "git config user.name" in str(exc.value)


def test_configure_git_writes_only_repo_root(sync, clone, tmp_path, monkeypatch):
    """The old version also ran `git config` in the caller's cwd, whatever repo that was."""
    work, _ = clone
    bystander = tmp_path / "bystander"
    bystander.mkdir()
    git(bystander, "init")
    monkeypatch.chdir(bystander)
    monkeypatch.setattr(sync, "REPO_ROOT", work)
    sync.configure_git()
    assert git(work, "config", "--local", "user.name") == "hermes-cronbot"
    leaked = subprocess.run(
        ["git", "config", "--local", "user.name"], cwd=bystander, capture_output=True, text=True
    )
    assert leaked.returncode == 1 and leaked.stdout == "", "configure_git wrote the cwd's repo"
