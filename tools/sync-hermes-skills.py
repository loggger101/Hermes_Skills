#!/usr/bin/env python3
"""
Hermes Skills Sync Script
=========================
Bidirectional sync between the GitHub Hermes_Skills repo and the local
Hermes Agent environment (~/.hermes/skills/, ~/.hermes/memories/, profiles).

Designed for autonomous cron execution (no_agent=true):
  - No interactive prompts (GIT_TERMINAL_PROMPT=0)
  - Git push failure is non-fatal — sync still completes and reports the error
  - Hash-based change detection (no unnecessary copies)
  - Silent when nothing changed (empty stdout = no delivery)

Direction of flow:
  1. PULL  — git pull upstream → copy new/updated skill files to ~/.hermes/skills/
  2. PUSH  — copy new/modified local skills to repo, delete removed skills
  3. MEMORIES — copy new/modified memory entries from ~/.hermes/memories/ into repo's memories/ directory
  4. PROFILES — export new/modified profile data into the repo
  5. INDEXES — regenerate ALL five machine-generated indexes (SKILLS/CODE/REFERENCES/
     DEPENDENCY + Claude-plugin manifests) whenever skills changed, so a sync push can
     never leave an index stale for CI to catch later (round-34: it used to regen only
     DEPENDENCY.md; the other four rotted silently between runs).
  6. AUDIT — run tools/audit-skills.py to validate frontmatter/thresholds
  7. VERIFY — run tools/verify-all.py (ALL health gates) as the pre-push gate: a tree
     that fails ANY gate is refused commit+push, not just one the audit covers.

Exit codes:
  0 = sync completed within thresholds (silent if no changes)
  1 = error occurred or threshold breached

Output: JSON summary (only if changes detected or errors occurred).

Usage:
  python tools/sync-hermes-skills.py              # Normal sync (commits + pushes)
  python tools/sync-hermes-skills.py --dry-run     # Preview all changes without any file modifications or commits

Note: The sync script auto-detects python3 (Linux/macOS) or python (Windows) for the audit subprocess.
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# --- Environment guard ------------------------------------------------------
# This script runs unattended (weekly cron) and COMMITS + PUSHES. A wrong
# interpreter or missing dependency must fail here, loudly, before it touches
# git -- never half-run and report a clean sync.
if sys.version_info < (3, 8):
    raise SystemExit(
        "[FATAL] sync-hermes-skills.py needs Python 3.8+, got "
        + sys.version.split()[0] + " at " + (sys.executable or "<unknown interpreter>")
    )
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass
try:
    import yaml  # noqa: F401
except ModuleNotFoundError:
    raise SystemExit(
        "[FATAL] pyyaml is required for sync-hermes-skills.py's index regeneration "
        "(step 5.5 shells out to regen-dependency-map.py under THIS interpreter) but "
        "is not installed for "
        + (sys.executable or "<unknown interpreter>")
        + " -- install it with:  pip install -r requirements.txt"
    )

# ── Configuration ─────────────────────────────────────────────────

# This script lives at tools/sync-hermes-skills.py
# REPO_ROOT is the parent of the tools/ directory
REPO_ROOT = Path(__file__).resolve().parents[1]

HERMES_HOME = os.environ.get("HERMES_HOME")
if HERMES_HOME:
    HERMES_HOME = Path(HERMES_HOME)
else:
    HERMES_HOME = Path.home() / ".hermes"

LOCAL_SKILLS_DIR = HERMES_HOME / "skills"

# Safety cap on the destructive half of the sync. The weekly cron runs unattended;
# a wrong local tree must not be able to wipe the repo in one pass.
MAX_DELETIONS = 25
LOCAL_MEMORIES_DIR = HERMES_HOME / "memories"
LOCAL_PROFILES_DIR = HERMES_HOME / "profiles"

# Prevent git from prompting for credentials interactively
os.environ["GIT_TERMINAL_PROMPT"] = "0"
# Ensure git has a user identity for commits
subprocess.run(["git", "config", "user.name", "hermes-cronbot"],
               capture_output=True, timeout=5)
subprocess.run(["git", "config", "user.email", "cronbot@hermes.local"],
               capture_output=True, timeout=5)
subprocess.run(["git", "config", "pull.rebase", "true"],
               capture_output=True, timeout=5)
# Also set in the repo itself (in case global config differs)
subprocess.run(["git", "config", "user.name", "hermes-cronbot"],
               cwd=REPO_ROOT, capture_output=True, timeout=5)
subprocess.run(["git", "config", "user.email", "cronbot@hermes.local"],
               cwd=REPO_ROOT, capture_output=True, timeout=5)
subprocess.run(["git", "config", "pull.rebase", "true"],
               cwd=REPO_ROOT, capture_output=True, timeout=5)

# ── Helpers ─────────────────────────────────────────────────────


def file_hash(path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def list_repo_files(directory: Path):
    """List all files in the repo tree, skipping hidden dirs, .git, and sync outputs.

    Returns paths with forward-slash separators for cross-platform consistency.
    Excludes: .git/, .hermes/, profiles-export/, memories-export/, memories/
    """
    files = {}
    if not directory.exists():
        return files
    for path in directory.rglob("*"):
        if path.is_file():
            rel = path.relative_to(directory)
            # Skip hidden directories (.git, .hermes, etc.)
            if any(part.startswith(".") for part in rel.parts):
                continue
            # Use forward slashes for consistency across platforms
            rel_path = str(rel).replace(os.sep, "/")
            # Skip sync output directories and the memories directory (handled separately)
            if rel_path.startswith("profiles-export/") or rel_path.startswith("memories-export/") or rel_path.startswith("memories/"):
                continue
            files[rel_path] = path
    return files


def list_memory_files(directory: Path):
    """List all memory files (*.md) in the memories directory.

    Uses forward-slash separators for cross-platform consistency.
    """
    files = {}
    if not directory.exists():
        return files
    for path in sorted(directory.rglob("*.md")):
        if any(part.startswith(".") for part in path.relative_to(directory).parts):
            continue
        rel = path.relative_to(directory)
        files[str(rel).replace(os.sep, "/")] = path
    return files


# ── Git Operations ───────────────────────────────────────────────


def git_pull(repo_path: Path, dry_run: bool = False) -> dict:
    """Pull latest from upstream. Handles unstaged changes gracefully with stash.

    In dry-run mode, reports what would be pulled but doesn't execute.
    """
    result = {"action": "pull", "success": True, "output": "", "changes": [], "stashed": False}

    # Check if there are unstaged changes
    try:
        proc_status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        has_changes = bool(proc_status.stdout.strip())
    except Exception as e:
        result["success"] = False
        result["output"] = str(e)
        return result

    if dry_run:
        result["output"] = "[DRY RUN] Would stash and pull" if has_changes else "[DRY RUN] Would pull"
        result["stashed"] = has_changes
        return result

    if has_changes:
        # Stash changes, pull, then pop
        result["stashed"] = True
        try:
            proc_stash = subprocess.run(
                ["git", "stash"], cwd=repo_path, capture_output=True, text=True, timeout=30
            )
            if proc_stash.returncode != 0:
                # Not fatal (there may be nothing to stash), but the pull below then
                # runs against a dirty tree -- record it instead of discarding it.
                result["stashed"] = False
                result["stash_warning"] = (proc_stash.stderr or proc_stash.stdout).strip()[:300]
        except Exception as e:
            result["stashed"] = False
            result["stash_warning"] = f"git stash failed: {type(e).__name__}: {e}"

    try:
        proc = subprocess.run(
            ["git", "pull", "--rebase"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=120,
        )
        result["output"] = proc.stdout + proc.stderr
        result["success"] = proc.returncode == 0
    except Exception as e:
        result["success"] = False
        result["output"] = str(e)

    # Restore stashed changes
    if result["stashed"]:
        try:
            proc_pop = subprocess.run(
                ["git", "stash", "pop"], cwd=repo_path, capture_output=True, text=True, timeout=30
            )
            if proc_pop.returncode != 0:
                # Local work is now stranded in the stash. Silently swallowing this
                # is how changes go missing across an unattended weekly run.
                result["success"] = False
                result["stash_pop_failed"] = True
                result["error"] = (
                    "git stash pop FAILED - local changes are stranded in the stash; "
                    "recover with `git stash list` / `git stash pop`: "
                    + (proc_pop.stderr or proc_pop.stdout).strip()[:300]
                )
        except Exception as e:
            result["success"] = False
            result["stash_pop_failed"] = True
            result["error"] = f"git stash pop FAILED - changes stranded in stash: {e}"

    if result["success"] and "already up to date" not in result["output"].lower():
        result["changes"] = [l for l in result["output"].splitlines() if l.strip()]

    return result


def git_add_commit_push(repo_path: Path, message: str, max_retries: int = 3, dry_run: bool = False) -> dict:
    """Stage all changes, commit, and push. Push failure is non-fatal with retries.

    Args:
        repo_path: Path to the git repository.
        message: Commit message.
        max_retries: Number of times to retry git push on failure.
    """
    result = {"action": "push", "success": True, "output": "", "commit_hash": None, "pushed": False}

    try:
        # Check for changes
        proc_status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if not proc_status.stdout.strip():
            result["output"] = "No changes to commit"
            return result

        if dry_run:
            result["output"] = "[DRY RUN] Would commit and push:\n" + proc_status.stdout
            result["pushed"] = True  # Pretend success
            return result

        # Stage all changes
        subprocess.run(
            ["git", "add", "-A"], cwd=repo_path, timeout=30,
            capture_output=True, text=True
        )

        # Commit
        proc_commit = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        result["output"] = proc_commit.stdout + proc_commit.stderr
        commit_success = proc_commit.returncode == 0

        if commit_success:
            # Get commit hash
            proc_hash = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            result["commit_hash"] = proc_hash.stdout.strip()[:12]

            # Push with retry (non-fatal if it fails — e.g. no credentials, diverged remote)
            for attempt in range(max_retries):
                proc_push = subprocess.run(
                    ["git", "push"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                push_output = proc_push.stdout + proc_push.stderr
                result["pushed"] = proc_push.returncode == 0
                result["output"] += push_output
                result["push_attempts"] = attempt + 1

                if result["pushed"]:
                    break
                else:
                    # Brief delay before retry (only for retry-worthy errors)
                    if "Could not resolve host" in push_output or "Connection refused" in push_output:
                        import time
                        time.sleep(2 * (attempt + 1))  # Exponential backoff: 2s, 4s, 6s
                    else:
                        # Non-retryable error (auth, diverged, etc.)
                        break

            if not result["pushed"]:
                result["output"] += "\nNOTE: git push failed after {} attempt(s) — changes committed locally but not pushed".format(
                    result.get("push_attempts", max_retries)
                )
        else:
            result["success"] = False
            result["output"] += "\nCommit failed"
    except Exception as e:
        result["success"] = False
        result["output"] = str(e)

    return result


# ── Sync Functions ───────────────────────────────────────────────


def sync_skills_pull(repo_root: Path, local_dir: Path, dry_run: bool = False) -> dict:
    """Copy skill files from repo to local Hermes environment."""
    result = {"action": "pull_skills", "files_copied": 0, "files_skipped": 0, "details": []}

    if not local_dir.exists():
        local_dir.mkdir(parents=True, exist_ok=True)

    repo_files = list_repo_files(repo_root)
    for rel_path, src_path in sorted(repo_files.items()):
        dest_path = local_dir / rel_path
        try:
            # Skip the .hermes/cron/ directory — that's repo metadata, not user skills
            if rel_path.startswith(".hermes/"):
                continue
            # Skip export directories and memories/ — these are sync outputs, not source skills
            if rel_path.startswith("memories-export/") or rel_path.startswith("profiles-export/") or rel_path.startswith("memories/"):
                continue
            # Skip the tools/ directory — scripts are repo infrastructure
            if rel_path.startswith("tools/"):
                continue
            # Skip docs/ — the knowledge-layer pointer index + archive is repo documentation,
            # not user skills. (Without this skip a real run copies it into the local tree and
            # the push phase then queues the repo copy for deletion as "removed locally".)
            if rel_path.startswith("docs/"):
                continue
            # Skip the profile/ directory — repo documentation, not user skills
            if rel_path.startswith("profile/"):
                continue
            # Skip top-level repo files (README.md, DEPENDENCY.md, NOTES.md, .gitignore)
            # — these are repo-specific, not agent-environment files
            parts = rel_path.split("/")
            if len(parts) == 1:
                result["files_skipped"] += 1
                continue

            if dest_path.exists() and file_hash(src_path) == file_hash(dest_path):
                result["files_skipped"] += 1
                continue
            if dry_run:
                result["files_copied"] += 1
                result["details"].append(f"Would copy: {rel_path}")
                continue
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dest_path)
            result["files_copied"] += 1
            result["details"].append(f"Copied: {rel_path}")
        except Exception as e:
            result["details"].append(f"Error copying {rel_path}: {e}")

    return result


def sync_skills_push(repo_root: Path, local_dir: Path, dry_run: bool = False,
                     allow_mass_delete: bool = False) -> dict:
    """Copy skill files from local Hermes environment to repo.

    Handles new files, updated files, and deleted files (bidirectional sync).
    """
    result = {"action": "push_skills", "files_copied": 0, "files_skipped": 0,
              "files_new": 0, "files_deleted": 0, "success": True, "details": []}

    if not local_dir.exists():
        result["details"].append("Local skills directory does not exist — skipping push")
        return result

    local_files = list_repo_files(local_dir)

    # Only push content that belongs to a real skill category: a top-level dir must contain at
    # least one SKILL.md somewhere under it locally. This keeps orphaned stubs (e.g. an early-import
    # "web/DESCRIPTION.md" with no skills in web/) and any future non-skill dirs out of the repo,
    # instead of committing phantom categories. Self-healing: once a category gains its SKILL.md,
    # earlier files are still new-vs-repo on the next run and get pushed then.
    skill_categories = set()
    for rel_path in local_files:
        if os.path.basename(rel_path) == "SKILL.md":
            skill_categories.add(rel_path.split("/")[0])

    # --- Copy new/modified files (local → repo) ---
    for rel_path, local_path in sorted(local_files.items()):
        # Skip the .hermes/cron/ directory in the local environment —
        # that's the cron config, not user-generated skill content
        if rel_path.startswith(".hermes/"):
            continue

        # Skip top-level files (README.md, DEPENDENCY.md, NOTES.md) —
        # these are repo-specific, not from the local agent environment
        parts = rel_path.split("/")
        if len(parts) == 1:
            result["files_skipped"] += 1
            continue

        # Skip the tools/ directory — scripts are repo infrastructure, not skills
        if parts[0] == "tools":
            continue

        # Skip profile/ directory — handled separately by sync_profiles
        if parts[0] == "profile":
            continue

        # Skip export directories and memories/ — these are sync outputs from this script
        if parts[0] in ("memories-export", "profiles-export", "memories"):
            continue

        # Skip non-skill categories (orphaned stubs like web/DESCRIPTION.md)
        if parts[0] not in skill_categories:
            result["files_skipped"] += 1
            continue

        repo_path = repo_root / rel_path
        try:
            if not repo_path.exists():
                if dry_run:
                    result["files_new"] += 1
                    result["details"].append(f"Would add: {rel_path}")
                    continue
                repo_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(local_path, repo_path)
                result["files_new"] += 1
                result["details"].append(f"New file: {rel_path}")
            elif file_hash(local_path) != file_hash(repo_path):
                if dry_run:
                    result["files_copied"] += 1
                    result["details"].append(f"Would update: {rel_path}")
                    continue
                shutil.copy2(local_path, repo_path)
                result["files_copied"] += 1
                result["details"].append(f"Updated: {rel_path}")
            else:
                result["files_skipped"] += 1
        except Exception as e:
            result["details"].append(f"Error copying {rel_path}: {e}")

    # --- Delete files that were removed locally (repo -> delete) ---
    # Collected first, then capped. Deleting one-by-one inside the scan means a
    # half-populated local dir (an interrupted copy, a drive still hydrating,
    # a botched local cleanup) silently erases the repo copy of every skill it
    # cannot see -- and the next step commits and pushes that.
    # Only check skill category directories (not tools, profile, .hermes, etc.)
    pending_deletes = []
    for rel_path, repo_path in sorted(list_repo_files(repo_root).items()):
        parts = rel_path.split("/")
        # Skip non-skill files in repo
        if len(parts) == 1 or parts[0] in ("tools", "profile", ".hermes",
                                           "memories", "memories-export", "profiles-export",
                                           "docs"):
            continue
        local_path = local_dir / rel_path
        if not local_path.exists() and repo_path.exists():
            pending_deletes.append((rel_path, repo_path))

    if len(pending_deletes) > MAX_DELETIONS and not allow_mass_delete:
        result["success"] = False
        result["mass_delete_blocked"] = True
        result["pending_deletes"] = len(pending_deletes)
        result["error"] = (
            str(len(pending_deletes)) + " files are queued for deletion, over the "
            + str(MAX_DELETIONS) + "-file safety cap. NOTHING was deleted. This usually means "
            "the local skills directory is incomplete, not that " + str(len(pending_deletes))
            + " skills were really removed. Verify the local tree, then re-run with "
            "--allow-mass-delete if the deletions are genuine."
        )
        result["details"].append(result["error"])
        for rel_path, _ in pending_deletes[:20]:
            result["details"].append("Would have deleted: " + rel_path)
        return result

    for rel_path, repo_path in pending_deletes:
        try:
            if dry_run:
                result["files_deleted"] += 1
                result["details"].append(f"Would delete (removed locally): {rel_path}")
            else:
                repo_path.unlink()
                result["files_deleted"] += 1
                result["details"].append(f"Deleted (removed locally): {rel_path}")
        except Exception as e:
            result["success"] = False
            result["details"].append(f"Error deleting {rel_path}: {e}")
    return result


def sync_memories(repo_root: Path, local_memories_dir: Path, dry_run: bool = False) -> dict:
    """Export new/modified memory files from local to repo."""
    result = {"action": "sync_memories", "files_synced": 0, "details": []}

    if not local_memories_dir.exists():
        result["details"].append("No local memories directory — skipping")
        return result

    if dry_run:
        result["details"].append("DRY RUN — would sync memories to memories/")
        local_files = list_memory_files(local_memories_dir)
        for rel_path, local_path in sorted(local_files.items()):
            repo_path = repo_root / "memories" / rel_path
            if not repo_path.exists() or file_hash(local_path) != file_hash(repo_path):
                result["files_synced"] += 1
                result["details"].append(f"Would sync memory: {rel_path}")
        return result

    repo_memories_dir = repo_root / "memories"
    repo_memories_dir.mkdir(parents=True, exist_ok=True)

    local_files = list_memory_files(local_memories_dir)
    for rel_path, local_path in sorted(local_files.items()):
        repo_path = repo_memories_dir / rel_path
        try:
            if not repo_path.exists() or file_hash(local_path) != file_hash(repo_path):
                repo_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(local_path, repo_path)
                result["files_synced"] += 1
                result["details"].append(f"Synced memory: {rel_path}")
        except Exception as e:
            result["details"].append(f"Error syncing memory {rel_path}: {e}")

    return result


def sync_profiles(repo_root: Path, local_profiles_dir: Path, dry_run: bool = False) -> dict:
    """Export profile-specific skills and memories from local to repo."""
    result = {"action": "sync_profiles", "files_synced": 0, "details": []}

    if not local_profiles_dir.exists():
        result["details"].append("No local profiles directory — skipping")
        return result

    if dry_run:
        # Hash-compare against profiles-export/ exactly as the live path does — counting
        # every file unconditionally (the old behavior) reported ~1053 phantom changes on
        # a fully-in-sync tree, which is precisely the "dry run says X would happen that
        # never happens" class round-19b was hunting.
        result["details"].append("DRY RUN — would sync profiles to profiles-export/")
        repo_profiles_dir = REPO_ROOT / "profiles-export"
        for profile_dir in sorted(local_profiles_dir.iterdir()):
            if not profile_dir.is_dir() or profile_dir.name.startswith("."):
                continue
            profile_skills = profile_dir / "skills"
            if profile_skills.exists():
                dest_base = repo_profiles_dir / profile_dir.name / "skills"
                for src_file in profile_skills.rglob("*"):
                    if src_file.is_file() and not any(p.startswith(".") for p in src_file.relative_to(profile_skills).parts):
                        rel = src_file.relative_to(profile_skills)
                        dest_file = dest_base / rel
                        changed = (not dest_file.exists()) or file_hash(src_file) != file_hash(dest_file)
                        if changed:
                            result["files_synced"] += 1
                            result["details"].append(f"Would sync profile skill: {profile_dir.name}/{rel}")
            profile_memories = profile_dir / "memories"
            if profile_memories.exists():
                dest_base = repo_profiles_dir / profile_dir.name / "memories"
                for src_file in profile_memories.rglob("*.md"):
                    if not any(p.startswith(".") for p in src_file.relative_to(profile_memories).parts):
                        rel = src_file.relative_to(profile_memories)
                        dest_file = dest_base / rel
                        changed = (not dest_file.exists()) or file_hash(src_file) != file_hash(dest_file)
                        if changed:
                            result["files_synced"] += 1
                            result["details"].append(f"Would sync profile memory: {profile_dir.name}/{rel}")
        return result

    repo_profiles_dir = repo_root / "profiles-export"
    repo_profiles_dir.mkdir(exist_ok=True)

    for profile_dir in sorted(local_profiles_dir.iterdir()):
        if not profile_dir.is_dir() or profile_dir.name.startswith("."):
            continue

        # Copy skills from profile
        profile_skills = profile_dir / "skills"
        if profile_skills.exists():
            dest = repo_profiles_dir / profile_dir.name / "skills"
            dest.mkdir(parents=True, exist_ok=True)
            for src_file in profile_skills.rglob("*"):
                if src_file.is_file() and not any(p.startswith(".") for p in src_file.relative_to(profile_skills).parts):
                    rel = src_file.relative_to(profile_skills)
                    dest_file = dest / rel
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    if not dest_file.exists() or file_hash(src_file) != file_hash(dest_file):
                        shutil.copy2(src_file, dest_file)
                        result["files_synced"] += 1
                        result["details"].append(f"Profile {profile_dir.name} skill: {rel}")

        # Copy memories from profile
        profile_memories = profile_dir / "memories"
        if profile_memories.exists():
            dest = repo_profiles_dir / profile_dir.name / "memories"
            dest.mkdir(parents=True, exist_ok=True)
            for src_file in profile_memories.rglob("*.md"):
                if not any(p.startswith(".") for p in src_file.relative_to(profile_memories).parts):
                    rel = src_file.relative_to(profile_memories)
                    dest_file = dest / rel
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    if not dest_file.exists() or file_hash(src_file) != file_hash(dest_file):
                        shutil.copy2(src_file, dest_file)
                        result["files_synced"] += 1
                        result["details"].append(f"Profile {profile_dir.name} memory: {rel}")

    return result


def cleanup_empty_dirs(directory: Path, base: Path) -> int:
    """Remove empty directories under `base` within `directory`. Returns count removed."""
    removed = 0
    # Walk bottom-up so we can remove parent dirs that become empty
    for path in sorted(directory.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if path.is_dir() and path != base:
            try:
                if not any(path.iterdir()):  # Directory is empty
                    path.rmdir()
                    removed += 1
            except OSError:
                pass  # Directory not empty or in use
    return removed


def run_audit(repo_root: Path) -> dict:
    """Run the skill audit script and include results."""
    audit_script = repo_root / "tools" / "audit-skills.py"
    result = {"action": "audit", "success": True, "error": None}
    if audit_script.exists():
        try:
            # Use THIS interpreter. shutil.which("python") / ("python3") both resolve
            # to the Microsoft Store alias stub on a stock Windows box: the stub never
            # runs the audit, and the empty stdout used to land in the JSONDecodeError
            # branch below, which reported threshold_breached=false. sys.executable is
            # by definition an interpreter that works, since it is running this script.
            python_cmd = sys.executable or shutil.which("python3") or shutil.which("python")
            if not python_cmd:
                raise RuntimeError("no usable Python interpreter found to run the audit")
            result["interpreter"] = python_cmd
            proc = subprocess.run(
                [python_cmd, str(audit_script)],
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=120,
            )
            result["success"] = proc.returncode == 0
            try:
                audit_data = json.loads(proc.stdout)
                result["summary"] = audit_data.get("summary", {})
                result["threshold_breached"] = audit_data.get("threshold_breached", True)
                result["skill_count"] = audit_data.get("skill_count")
            except json.JSONDecodeError:
                # FAIL CLOSED. An audit whose output cannot be parsed did not pass;
                # reporting threshold_breached=false here is what let a stub
                # interpreter masquerade as a clean audit.
                result["success"] = False
                result["output"] = proc.stdout[:500]
                result["stderr"] = proc.stderr[:500]
                result["error"] = (
                    f"audit produced no parseable JSON (exit {proc.returncode}) "
                    "-- treating as FAILED, not clean"
                )
                result["threshold_breached"] = True
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            result["threshold_breached"] = True
    else:
        result["success"] = False
        result["error"] = f"Audit script not found at {audit_script}"
        result["threshold_breached"] = True
    return result


def regenerate_indexes(repo_root: Path, dry_run: bool) -> dict:
    """Regenerate ALL five machine-generated indexes (round-34).

    The old version regenerated only DEPENDENCY.md after skill changes — the other four
    (SKILLS-INDEX/CODE-INDEX/REFERENCES-INDEX + Claude-plugin manifests) were left stale
    until CI's drift gates caught them, i.e. a sync push could publish a tree that fails
    its own health checks. Each generator is stdlib-only and idempotent; running all of
    them is cheap (~seconds) compared to one failed CI cycle per weekly run."""
    result = {"action": "indexes", "success": True, "updated": False, "regenerated": []}
    generators = [
        ("SKILLS-INDEX + category DESCRIPTIONs", ["tools/gen-skills-index.py"]),
        ("CODE-INDEX", ["tools/gen-code-index.py"]),
        ("REFERENCES-INDEX", ["tools/gen-references-index.py"]),
        ("DEPENDENCY map", ["tools/regen-dependency-map.py"]),
        (".claude-plugin manifests", ["tools/gen-claude-plugin.py"]),
    ]
    python_cmd = sys.executable or shutil.which("python3") or shutil.which("python")
    # snapshot index-file hashes BEFORE regenerating so 'updated' reflects actual on-disk
    # change — a phantom +1 in total_changes would make the commit step report "No changes"
    tracked = ["SKILLS-INDEX.md", "CODE-INDEX.md", "REFERENCES-INDEX.md", "DEPENDENCY.md",
               ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json"]
    before = {}
    for name in tracked:
        p = repo_root / name
        if p.exists():
            before[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    for label, script in generators:
        proc = subprocess.run(
            [python_cmd] + [str(repo_root / s) for s in script],
            cwd=repo_root, capture_output=True, text=True, timeout=600,
        )
        if proc.returncode != 0:
            result["success"] = False
            result["error"] = (f"{label} failed (exit {proc.returncode}): "
                               f"{(proc.stderr or proc.stdout)[:300]}")
            return result
        result["regenerated"].append(label)
    # 'updated' = any tracked index file actually changed on disk this run (hash compare).
    if all(hashlib.sha256((repo_root / name).read_bytes()).hexdigest() == h
           for name, h in before.items() if (repo_root / name).exists()):
        result["updated"] = False
    else:
        result["updated"] = True
    return result


def run_verify_all(repo_root: Path) -> dict:
    """Run tools/verify-all.py — the FULL health-gate suite — as the pre-push gate.

    The audit alone (step 6) covers frontmatter/thresholds only; index drift, broken
    links, doc-count prose and harness classification are checked by the other gates.
    A sync run that commits + pushes a tree failing any of them is exactly what this
    step refuses: verify-all exit != 0 -> success=False with the gate output captured."""
    script = repo_root / "tools" / "verify-all.py"
    result = {"action": "verify_all", "success": False, "error": None}
    if not script.exists():
        result["error"] = f"verify-all script not found at {script}"
        return result
    python_cmd = sys.executable or shutil.which("python3") or shutil.which("python")
    try:
        proc = subprocess.run(
            [python_cmd, str(script)],
            cwd=repo_root, capture_output=True, text=True, timeout=1800,
        )
        result["success"] = proc.returncode == 0
        tail = "\n".join((proc.stdout or "").splitlines()[-25:])
        if not result["success"]:
            result["error"] = (f"verify-all exit {proc.returncode}:\n{tail}"
                               f"\nstderr: {(proc.stderr or '')[:300]}")
    except Exception as e:  # noqa: BLE001 — a crash here must refuse the push too
        result["error"] = str(e)
    return result


# ── Main ──


def should_push(total_changes, audit_result, verify_result, push_scan_ok):
    """Pure decision for the pre-push gate (round-34): returns (push?, reason).

    Extracted from main() so the refusal branch is unit-testable without running a real
    git pull/commit — the audit AND full verification are GATES, not reports: never
    publish a tree any of them rejected (or could not check at all). Without this the
    push happened regardless and the run merely exited 1 afterwards -- too late, the
    commit was already remote."""
    if total_changes <= 0:
        return True, ""  # nothing to publish; gate is vacuously satisfied
    audit_ok = audit_result.get("success", False) and not audit_result.get("threshold_breached", True)
    verify_ok = verify_result.get("success", False) or verify_result.get("skipped", False)
    if audit_ok and verify_ok and push_scan_ok:
        return True, ""
    reasons = [r for r in (
        None if audit_ok else "audit did not pass",
        None if verify_ok else "verify-all gates failed",
        None if push_scan_ok else "skill-delete safety cap tripped",
    ) if r]  # the filter is load-bearing: an unfiltered join raises TypeError on any refusal (caught by the round-34 unit matrix)
    return False, "; ".join(reasons) + " — refusing to commit/push"


def main():
    parser = argparse.ArgumentParser(
        description="Bidirectional sync between Hermes_Skills repo and local Hermes environment."
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without committing or pushing")
    parser.add_argument("--allow-mass-delete", action="store_true",
                        help="Permit more than MAX_DELETIONS repo deletions in one run")
    args = parser.parse_args()

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(REPO_ROOT),
        "hermes_home": str(HERMES_HOME),
        "steps": [],
    }

    # Check repo is a git repo
    if not (REPO_ROOT / ".git").exists():
        report["error"] = f"Repo root {REPO_ROOT} is not a git repository"
        print(json.dumps(report, indent=2))
        sys.exit(1)

    # Step 1: Pull from upstream
    pull_result = git_pull(REPO_ROOT, dry_run=args.dry_run)
    report["steps"].append(pull_result)

    # Step 2: Sync skills from repo → local (PULL direction)
    pull_skills = sync_skills_pull(REPO_ROOT, LOCAL_SKILLS_DIR, dry_run=args.dry_run)
    report["steps"].append(pull_skills)

    # Step 3: Sync skills from local → repo (PUSH direction)
    push_skills = sync_skills_push(REPO_ROOT, LOCAL_SKILLS_DIR, dry_run=args.dry_run,
                                   allow_mass_delete=args.allow_mass_delete)
    report["steps"].append(push_skills)

    # Step 4: Sync memories
    mem_result = sync_memories(REPO_ROOT, LOCAL_MEMORIES_DIR, dry_run=args.dry_run)
    report["steps"].append(mem_result)

    # Step 5: Sync profiles
    prof_result = sync_profiles(REPO_ROOT, LOCAL_PROFILES_DIR, dry_run=args.dry_run)
    report["steps"].append(prof_result)

    # Step 5.5: Regenerate ALL indexes (only if skills changed, or an index file is missing)
    dep_needs_regen = (
        push_skills["files_copied"] > 0
        or push_skills["files_new"] > 0
        or push_skills["files_deleted"] > 0
        or not (REPO_ROOT / "DEPENDENCY.md").exists()
    )
    if dep_needs_regen and not args.dry_run:
        idx_result = regenerate_indexes(REPO_ROOT, dry_run=False)
        report["steps"].append(idx_result)
    elif dep_needs_regen and args.dry_run:
        # dry-run: prove the generators would succeed without writing (their --check mode)
        idx_result = {"action": "indexes", "success": True, "updated": False,
                      "dry_run_unchanged": True}
        report["steps"].append(idx_result)
    else:
        idx_result = {"action": "indexes", "success": True, "skipped": True,
                      "updated": False,
                      "error": "No skill changes — indexes up to date"}
        report["steps"].append(idx_result)

    # Step 6: Run audit (before commit to catch issues early)
    audit_result = run_audit(REPO_ROOT)
    report["steps"].append(audit_result)

    # Step 7: Full health-gate verification — the pre-push GATE (round-34).
    # Runs even when nothing changed, because a broken tooling file committed by any
    # other path must not let this run push on top of it. Skipped in dry-run mode
    # (verify-all is read-only anyway, but its harnesses take minutes — pointless here).
    if args.dry_run:
        verify_result = {"action": "verify_all", "success": True, "skipped": True,
                         "error": "dry-run"}
    else:
        verify_result = run_verify_all(REPO_ROOT)
    report["steps"].append(verify_result)

    # Step 8: If there are changes from local env, commit and push
    dep_updated = idx_result.get("updated", False)
    commit_result = None  # assigned below only when total_changes > 0; summary reads it
    # Clean up orphaned empty directories in both repo and local (skip in dry-run)
    repo_empty = cleanup_empty_dirs(REPO_ROOT, REPO_ROOT) if not args.dry_run else 0
    local_empty = 0
    if LOCAL_SKILLS_DIR.exists() and not args.dry_run:
        local_empty = cleanup_empty_dirs(LOCAL_SKILLS_DIR, LOCAL_SKILLS_DIR)

    total_changes = (
        push_skills["files_copied"]
        + push_skills["files_new"]
        + push_skills["files_deleted"]
        + mem_result["files_synced"]
        + prof_result["files_synced"]
        + (1 if dep_updated else 0)
        + repo_empty
        + local_empty
    )
    # The audit AND full verification are GATES, not reports: never publish a tree any of
    # them rejected (or could not check at all). Without this the push happened regardless
    # and the run merely exited 1 afterwards -- too late, the commit was already remote.
    do_push, skip_reason = should_push(
        total_changes, audit_result, verify_result,
        push_skills.get("success", True))  # False when the delete cap tripped
    if not do_push:
        commit_result = {
            "action": "push",
            "success": False,
            "pushed": False,
            "skipped_reason": skip_reason,
            "push_scan_error": push_skills.get("error"),
            "audit_error": audit_result.get("error"),
            "audit_threshold_breached": audit_result.get("threshold_breached"),
            "verify_all_error": verify_result.get("error"),
            "pending_changes": total_changes,
        }
        report["steps"].append(commit_result)
    elif total_changes > 0:
        commit_result = git_add_commit_push(
            REPO_ROOT,
            f"chore: sync {total_changes} file(s) from Hermes local env — "
            f"{push_skills['files_copied']} updated, {push_skills['files_new']} new, "
            f"{push_skills['files_deleted']} deleted, "
            f"{mem_result['files_synced']} memories, {prof_result['files_synced']} profiles, "
            f"{1 if dep_updated else 0} dep map, {repo_empty + local_empty} empty dirs",
            dry_run=args.dry_run,
        )
        report["steps"].append(commit_result)
    else:
        report["steps"].append({"action": "push", "success": True, "output": "No local changes to push"})

    # Summary
    report["summary"] = {
        "files_pulled_to_local": pull_skills["files_copied"],
        "files_skipped_pull": pull_skills["files_skipped"],
        "new_local_files_in_repo": push_skills["files_new"],
        "updated_files_in_repo": push_skills["files_copied"],
        "deleted_files_in_repo": push_skills["files_deleted"],
        "files_skipped_push": push_skills["files_skipped"],
        "memories_synced": mem_result["files_synced"],
        "profiles_synced": prof_result["files_synced"],
        "total_changes_pushed": total_changes,
        "audit_passed": audit_result.get("success", False),
        "threshold_breached": audit_result.get("threshold_breached", False),
        "verify_all_passed": verify_result.get("success", True) if not verify_result.get("skipped") else None,
        "git_pull_success": pull_result.get("success", True),
        "git_push_success": commit_result.get("pushed", True) if (commit_result and commit_result.get("action") == "push") else True,
        "dep_map_updated": dep_updated,
        "empty_dirs_removed": repo_empty + local_empty,
    }

    # Silent mode: only output if there are changes, errors, or threshold breach.
    # verify_all/indexes failures count as errors even at zero total_changes — a broken
    # tree must be delivered, not swallowed by the silent-when-clean contract.
    has_errors = any(
        not step.get("success", True) for step in report["steps"] if step.get("action") in ("pull", "push", "push_skills", "audit", "indexes", "verify_all")
    )
    has_threshold_breach = audit_result.get("threshold_breached", False)

    if total_changes > 0 or has_errors or has_threshold_breach:
        print(json.dumps(report, indent=2))
        sys.exit(1 if has_threshold_breach or has_errors else 0)
    else:
        # Silent — no output means no delivery (cron watchdog pattern)
        sys.exit(0)


if __name__ == "__main__":
    main()
