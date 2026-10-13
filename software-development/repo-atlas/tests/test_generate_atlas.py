"""scripts/generate_atlas.py, installed the way its usage line says (scripts/atlas/ inside a
target repo), run against throwaway git repos."""

import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "generate_atlas.py"


@pytest.fixture
def git_env(tmp_path, monkeypatch):
    cfg = tmp_path / "gitconfig"
    cfg.write_text("", encoding="utf-8")
    env = {
        "GIT_CONFIG_GLOBAL": str(cfg),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@example.invalid",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@example.invalid",
    }
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    return env


def make_repo(root, commits, git=True):
    (root / "src" / "app").mkdir(parents=True)
    (root / "src" / "app" / "main.py").write_text(
        'if __name__ == "__main__":\n    pass\n', encoding="utf-8"
    )
    (root / "README.md").write_text("# demo\n", encoding="utf-8")
    atlas = root / "scripts" / "atlas"
    atlas.mkdir(parents=True)
    shutil.copy2(SCRIPT, atlas / "generate_atlas.py")
    if not git:
        return
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, check=True)
    for message, date in commits:
        subprocess.run(["git", "add", "-A"], cwd=root, check=True)
        when = (datetime.now(timezone.utc) - timedelta(days=date)).strftime(
            "%Y-%m-%dT%H:%M:%S+0000"
        )
        env = dict(os.environ, GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
        subprocess.run(
            ["git", "commit", "-q", "--allow-empty", "-m", message], cwd=root, check=True, env=env
        )


def atlas(root, *args):
    proc = subprocess.run(
        [sys.executable, str(root / "scripts" / "atlas" / "generate_atlas.py"), *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )
    return proc.returncode, proc.stdout + proc.stderr


def changelog(root):
    return (root / "docs" / "atlas" / "08_CHANGELOG_LAST_14_DAYS.md").read_text(encoding="utf-8")


def test_write_then_check(tmp_path, git_env):
    make_repo(tmp_path, [("feat: add app", 2), ("fix(app): crash", 1)])
    rc, out = atlas(tmp_path, "--write")
    assert rc == 0 and "Atlas generation complete." in out
    repo_map = (tmp_path / "docs" / "atlas" / "repo-map.md").read_text(encoding="utf-8")
    assert "src" in repo_map and "README.md" in repo_map
    log = changelog(tmp_path)
    assert "2 commits in the last 14 days." in log and "fix(app): crash" in log
    assert atlas(tmp_path, "--check") == (0, "Atlas files are up to date.\n")


def test_check_reports_stale_and_missing_without_writing(tmp_path, git_env):
    make_repo(tmp_path, [("feat: one", 1)])
    rc, out = atlas(tmp_path, "--check")
    assert rc == 1 and "MISSING: docs" in out
    assert not (tmp_path / "docs").exists()  # --check used to create docs/atlas/
    atlas(tmp_path, "--write")
    (tmp_path / "src" / "newpkg").mkdir()
    (tmp_path / "src" / "newpkg" / "mod.py").write_text("x = 1\n", encoding="utf-8")
    rc, out = atlas(tmp_path, "--check")
    assert rc == 1 and "STALE: docs" in out


def test_quiet_window_is_not_reported_as_recent(tmp_path, git_env):
    """The last 20 commits used to be counted and listed as 'the last 14 days'."""
    make_repo(tmp_path, [("feat: ancient", 90), ("docs: old", 60)])
    rc, _ = atlas(tmp_path, "--write")
    assert rc == 0
    log = changelog(tmp_path)
    assert "0 commits in the last 14 days." in log
    assert "No commits in the window. The 2 most recent, for context:" in log
    assert "### Features" not in log


def test_git_failure_is_fatal_not_zero_commits(tmp_path, git_env):
    make_repo(tmp_path, [], git=False)
    rc, out = atlas(tmp_path, "--write")
    assert rc != 0 and "git log failed" in out
    assert not (tmp_path / "docs" / "atlas" / "08_CHANGELOG_LAST_14_DAYS.md").exists()


def test_docs_with_real_content_stays_in_the_map(tmp_path, git_env):
    make_repo(tmp_path, [("feat: one", 1)])
    (tmp_path / "docs" / "guides").mkdir(parents=True)
    (tmp_path / "docs" / "guides" / "intro.md").write_text("# hi\n", encoding="utf-8")
    atlas(tmp_path, "--write")
    repo_map = (tmp_path / "docs" / "atlas" / "repo-map.md").read_text(encoding="utf-8")
    assert "docs/" in repo_map and "guides/" in repo_map
    # the only atlas/ dir in the tree is scripts/atlas/, never the generated docs/atlas/
    assert sum(1 for ln in repo_map.splitlines() if ln.rstrip().endswith("atlas/")) == 1
    assert atlas(tmp_path, "--check")[0] == 0
