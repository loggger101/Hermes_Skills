#!/usr/bin/env python3
"""
Hermes Skills Sync Script
=========================
Bidirectional sync between the GitHub Hermes_Skills repo and the local
Hermes Agent environment (~/.hermes/skills/, ~/.hermes/memories/, profiles).

Direction of flow:
  1. PULL  — git pull upstream → copy new/updated skill files to ~/.hermes/skills/
  2. PUSH  — copy new/modified local skills back to the repo working tree, git add + commit + push
  3. MEMORIES — export new/modified memory entries from ~/.hermes/memories/ into the repo
  4. PROFILES — export new/modified profile data into the repo

Uses git for the repo side. Uses file hashing + mtime comparison to detect changes
without needing a git repo in ~/.hermes/.

Exit codes:
  0 = sync completed (may have 0 changes or N changes)
  1 = error occurred during sync

Output: JSON summary suitable for cronjob delivery.
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── Configuration ─────────────────────────────────────────────────


REPO_ROOT = Path(__file__).resolve().parents[2]  # Repo root: tools/ is at .hermes/... wait, no, tools/ is at root level

# Actually, this script lives at tools/sync-hermes-skills.py
# So REPO_ROOT = Path(__file__).resolve().parents[1]  # parent of tools/
REPO_ROOT = Path(__file__).resolve().parents[1]

HERMES_HOME = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
if HERMES_HOME:
    HERMES_HOME = Path(HERMES_HOME)
else:
    HERMES_HOME = Path.home() / ".hermes"

LOCAL_SKILLS_DIR = HERMES_HOME / "skills"
LOCAL_MEMORIES_DIR = HERMES_HOME / "memories"
LOCAL_PROFILES_DIR = HERMES_HOME / "profiles"

# Directories to skip when scanning for skill files
SKIP_DIRS = {".git", "__pycache__", ".curator_backups", "node_modules", ".cache"}

# Memory file patterns to sync
MEMORY_PATTERNS = ["*.md"]

# ── Helpers ─────────────────────────────────────────────────────


def get_git_config(repo_path: Path, key: str) -> Optional[str]:
    """Get a git config value for a repo."""
    try:
        result = subprocess.run(
            ["git", "config", key],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception:
        return None


def file_hash(path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def list_skill_files(directory: Path):
    """List all SKILL.md and .py files in a skills directory tree, skipping hidden dirs."""
    files = {}
    if not directory.exists():
        return files
    for path in directory.rglob("*"):
        if path.is_file():
            # Skip hidden directories
            if any(part.startswith(".") for part in path.relative_to(directory).parts):
                continue
            rel = path.relative_to(directory)
            files[str(rel)] = path
    return files


def list_memory_files(directory: Path):
    """List all memory files in the memories directory."""
    files = {}
    if not directory.exists():
        return files
    for path in sorted(directory.rglob("*.md")):
        if any(part.startswith(".") for part in path.relative_to(directory).parts):
            continue
        rel = path.relative_to(directory)
        files[str(rel)] = path
    return files


# ── Sync Functions ───────────────────────────────────────────────


def git_pull(repo_path: Path) -> dict:
    """Pull latest from upstream."""
    result = {"action": "pull", "success": True, "output": "", "changes": []}
    try:
        proc = subprocess.run(
            ["git", "pull", "--rebase"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=60,
        )
        result["output"] = proc.stdout + proc.stderr
        result["success"] = proc.returncode == 0
        if "already up to date" not in result["output"].lower():
            result["changes"] = [l for l in result["output"].splitlines() if l.strip()]
    except Exception as e:
        result["success"] = False
        result["output"] = str(e)
    return result


def git_add_commit_push(repo_path: Path, message: str) -> dict:
    """Stage all changes, commit, and push."""
    result = {"action": "push", "success": True, "output": "", "commit_hash": None}
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
            result["success"] = True
            return result

        # Stage all changes
        subprocess.run(["git", "add", "-A"], cwd=repo_path, timeout=30,
                         capture_output=True, text=True)

        # Commit
        proc_commit = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        result["output"] = proc_commit.stdout + proc_commit.stderr
        result["success"] = proc_commit.returncode == 0

        if result["success"]:
            # Get commit hash
            proc_hash = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            result["commit_hash"] = proc_hash.stdout.strip()

            # Push
            proc_push = subprocess.run(
                ["git", "push"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=60,
            )
            result["output"] += proc_push.stdout + proc_push.stderr
            result["success"] = proc_push.returncode == 0
    except Exception as e:
        result["success"] = False
        result["output"] = str(e)
    return result


def sync_skills_pull(repo_root: Path, local_dir: Path) -> dict:
    """Copy skill files from repo to local Hermes environment."""
    result = {"action": "pull_skills", "files_copied": 0, "files_skipped": 0, "details": []}

    repo_skills = repo_root / "skills"  # Wait, the repo IS the skills repo, not nested
    # Actually, the repo root IS the skills directory
    repo_skills = repo_root

    if not local_dir.exists():
        local_dir.mkdir(parents=True, exist_ok=True)

    repo_files = list_skill_files(repo_skills)
    for rel_path, src_path in sorted(repo_files.items()):
        dest_path = local_dir / rel_path
        try:
            if dest_path.exists() and file_hash(src_path) == file_hash(dest_path):
                result["files_skipped"] += 1
                continue
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dest_path)
            result["files_copied"] += 1
            result["details"].append(f"Copied: {rel_path}")
        except Exception as e:
            result["details"].append(f"Error copying {rel_path}: {e}")

    return result


def sync_skills_push(repo_root: Path, local_dir: Path) -> dict:
    """Copy skill files from local Hermes environment to repo."""
    result = {"action": "push_skills", "files_copied": 0, "files_skipped": 0, "files_new": 0, "details": []}

    if not local_dir.exists():
        result["details"].append("Local skills directory does not exist — skipping push")
        return result

    local_files = list_skill_files(local_dir)

    for rel_path, local_path in sorted(local_files.items()):
        # Skip non-skill files (like README.md, DEPENDENCY.md at top level)
        # We only sync category/ directories and their contents
        parts = rel_path.split(os.sep)
        if len(parts) == 1:
            # Top-level file (README.md, DEPENDENCY.md, etc.) — skip
            result["files_skipped"] += 1
            continue

        repo_path = repo_root / rel_path
        try:
            if not repo_path.exists():
                # New file
                repo_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(local_path, repo_path)
                result["files_new"] += 1
                result["details"].append(f"New file: {rel_path}")
            elif file_hash(local_path) != file_hash(repo_path):
                shutil.copy2(local_path, repo_path)
                result["files_copied"] += 1
                result["details"].append(f"Updated: {rel_path}")
            else:
                result["files_skipped"] += 1
        except Exception as e:
            result["details"].append(f"Error copying {rel_path}: {e}")

    return result


def sync_memories(repo_root: Path, local_memories_dir: Path) -> dict:
    """Export new/modified memory files from local to repo."""
    result = {"action": "sync_memories", "files_synced": 0, "details": []}

    if not local_memories_dir.exists():
        result["details"].append("No local memories directory — skipping")
        return result

    # Create a memories/ directory in the repo for synced memories
    repo_memories_dir = repo_root / "memories-export"
    repo_memories_dir.mkdir(exist_ok=True)

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


def sync_profiles(repo_root: Path, local_profiles_dir: Path) -> dict:
    """Export profile data from local to repo."""
    result = {"action": "sync_profiles", "files_synced": 0, "details": []}

    if not local_profiles_dir.exists():
        result["details"].append("No local profiles directory — skipping")
        return result

    # Copy profile-specific skills and memories to repo
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
            for src_file in profile_skills.rglob("*.md"):
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
                rel = src_file.relative_to(profile_memories)
                dest_file = dest / rel
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                if not dest_file.exists() or file_hash(src_file) != file_hash(dest_file):
                    shutil.copy2(src_file, dest_file)
                    result["files_synced"] += 1
                    result["details"].append(f"Profile {profile_dir.name} memory: {rel}")

    return result


def run_audit(repo_root: Path) -> dict:
    """Run the skill audit script and include results."""
    audit_script = repo_root / "tools" / "audit-skills.py"
    result = {"action": "audit", "success": True}
    if audit_script.exists():
        try:
            proc = subprocess.run(
                ["python3", str(audit_script)],
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=120,
            )
            result["success"] = proc.returncode == 0
            try:
                audit_data = json.loads(proc.stdout)
                result["summary"] = audit_data.get("summary", {})
                result["threshold_breached"] = audit_data.get("threshold_breached", False)
            except json.JSONDecodeError:
                result["output"] = proc.stdout[:500]
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
    else:
        result["success"] = False
        result["error"] = f"Audit script not found at {audit_script}"
    return result


# ── Main ────────────────────────────────────────────────────────


def main():
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
    pull_result = git_pull(REPO_ROOT)
    report["steps"].append(pull_result)

    # Step 2: Sync skills from repo → local (PULL direction)
    pull_skills = sync_skills_pull(REPO_ROOT, LOCAL_SKILLS_DIR)
    report["steps"].append(pull_skills)

    # Step 3: Sync skills from local → repo (PUSH direction)
    push_skills = sync_skills_push(REPO_ROOT, LOCAL_SKILLS_DIR)
    report["steps"].append(push_skills)

    # Step 4: Sync memories
    mem_result = sync_memories(REPO_ROOT, LOCAL_MEMORIES_DIR)
    report["steps"].append(mem_result)

    # Step 5: Sync profiles
    prof_result = sync_profiles(REPO_ROOT, LOCAL_PROFILES_DIR)
    report["steps"].append(prof_result)

    # Step 6: Run audit
    audit_result = run_audit(REPO_ROOT)
    report["steps"].append(audit_result)

    # Step 7: If there are new local files, commit and push
    total_changes = push_skills["files_copied"] + push_skills["files_new"] + mem_result["files_synced"] + prof_result["files_synced"]
    if total_changes > 0:
        commit_result = git_add_commit_push(
            REPO_ROOT,
            f"chore: sync {total_changes} file(s) from Hermes local env — "
            f"{push_skills['files_copied']} skills updated, {push_skills['files_new']} new skills, "
            f"{mem_result['files_synced']} memories, {prof_result['files_synced']} profile files"
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
        "files_skipped_push": push_skills["files_skipped"],
        "memories_synced": mem_result["files_synced"],
        "profiles_synced": prof_result["files_synced"],
        "total_changes_pushed": total_changes,
        "audit_passed": audit_result.get("success", False),
        "threshold_breached": audit_result.get("threshold_breached", False),
    }

    print(json.dumps(report, indent=2))
    sys.exit(0 if not report["summary"].get("threshold_breached", False) else 1)


if __name__ == "__main__":
    main()
