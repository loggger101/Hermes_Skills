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
  2. PUSH  — copy new/modified local skills back to repo, git add + commit + push
  3. MEMORIES — export new/modified memory entries from ~/.hermes/memories/ into the repo
  4. PROFILES — export new/modified profile data into the repo
  5. AUDIT  — run tools/audit-skills.py to validate

Exit codes:
  0 = sync completed within thresholds (silent if no changes)
  1 = error occurred or threshold breached

Output: JSON summary (only if changes detected or errors occurred).
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

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
    """List all files in the repo tree, skipping hidden dirs and .git.

    Returns paths with forward-slash separators for cross-platform consistency."""
    files = {}
    if not directory.exists():
        return files
    for path in directory.rglob("*"):
        if path.is_file():
            # Skip hidden directories
            if any(part.startswith(".") for part in path.relative_to(directory).parts):
                continue
            rel = path.relative_to(directory)
            # Use forward slashes for consistency across platforms
            files[str(rel).replace(os.sep, "/")] = path
    return files


def list_memory_files(directory: Path):
    """List all memory files (*.md) in the memories directory."""
    files = {}
    if not directory.exists():
        return files
    for path in sorted(directory.rglob("*.md")):
        if any(part.startswith(".") for part in path.relative_to(directory).parts):
            continue
        rel = path.relative_to(directory)
        files[str(rel)] = path
    return files


# ── Git Operations ───────────────────────────────────────────────


def git_pull(repo_path: Path) -> dict:
    """Pull latest from upstream. Handles unstaged changes gracefully with stash."""
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

    if has_changes:
        # Stash changes, pull, then pop
        result["stashed"] = True
        try:
            subprocess.run(
                ["git", "stash"], cwd=repo_path, capture_output=True, text=True, timeout=30
            )
        except Exception:
            pass  # Continue even if stash fails — may have nothing to stash

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
            subprocess.run(
                ["git", "stash", "pop"], cwd=repo_path, capture_output=True, text=True, timeout=30
            )
        except Exception:
            pass  # Non-fatal — changes may still be in stash

    if result["success"] and "already up to date" not in result["output"].lower():
        result["changes"] = [l for l in result["output"].splitlines() if l.strip()]

    return result


def git_add_commit_push(repo_path: Path, message: str) -> dict:
    """Stage all changes, commit, and push. Push failure is non-fatal."""
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

            # Push (non-fatal if it fails — e.g. no credentials, diverged remote)
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
            if not result["pushed"]:
                result["output"] += "\nNOTE: git push failed — changes committed locally but not pushed"
        else:
            result["success"] = False
            result["output"] += "\nCommit failed"
    except Exception as e:
        result["success"] = False
        result["output"] = str(e)

    return result


# ── Sync Functions ───────────────────────────────────────────────


def sync_skills_pull(repo_root: Path, local_dir: Path) -> dict:
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
            # Skip export directories — these are sync outputs, not source skills
            if rel_path.startswith("memories-export/") or rel_path.startswith("profiles-export/"):
                continue
            # Skip the tools/ directory — scripts are repo infrastructure
            if rel_path.startswith("tools/"):
                continue
            # Skip the profile/ directory — handled separately by sync_profiles
            if rel_path.startswith("profile/"):
                continue

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

    local_files = list_repo_files(local_dir)

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

        # Skip export directories — these are sync outputs from this script
        if parts[0] == "memories-export" or parts[0] == "profiles-export":
            continue

        repo_path = repo_root / rel_path
        try:
            if not repo_path.exists():
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
    """Export profile-specific skills and memories from local to repo."""
    result = {"action": "sync_profiles", "files_synced": 0, "details": []}

    if not local_profiles_dir.exists():
        result["details"].append("No local profiles directory — skipping")
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


def generate_dependency_map(repo_root: Path) -> dict:
    """Regenerate DEPENDENCY.md from current related_skills frontmatter.

    Scans all SKILL.md files, builds a dependency map, and writes
    DEPENDENCY.md to the repo root. Uses the same logic as the standalone
    audit script's related_skills check.

    Returns a dict with stats: {skills_scanned, total_refs, hubs, standalone}
    """
    result = {"action": "dependency_map", "success": True, "files_scanned": 0,
              "total_refs": 0, "error": None}

    try:
        import re as re_mod
        import yaml as yaml_mod

        skills = {}  # slug -> name
        refs = {}    # skill_name -> [list of related_skills]

        # First pass: collect all skill names
        for path in sorted(repo_root.rglob("SKILL.md")):
            if '.git' in str(path):
                continue
            try:
                text = path.read_text(encoding="utf-8")
                m = re_mod.match(r'^---\n(.*?)\n---', text, re_mod.DOTALL)
                if not m:
                    continue
                fm = yaml_mod.safe_load(m.group(1))
                if not fm or not isinstance(fm, dict):
                    continue

                name = fm.get("name", "")
                related = fm.get("metadata", {}).get("hermes", {}).get("related_skills", [])
                if isinstance(related, str):
                    related = [related]
                if not isinstance(related, list):
                    related = []

                result["files_scanned"] += 1
                skills[name] = name
                refs[name] = related
                result["total_refs"] += len(related)
            except Exception:
                continue

        # Build reverse map: who references each skill
        incoming = {name: [] for name in skills}
        for name, related_list in refs.items():
            for ref in related_list:
                if ref in incoming:
                    incoming[ref].append(name)

        # Hub skills (referenced by 2+)
        hubs = {k: v for k, v in incoming.items() if len(v) >= 2}
        hubs_sorted = sorted(hubs.items(), key=lambda x: (-len(x[1]), x[0]))

        # Standalone skills (no outgoing refs AND no incoming refs)
        standalone = [name for name in skills if not refs[name] and not incoming[name]]
        standalone_sorted = sorted(standalone)

        # Generate DEPENDENCY.md
        lines = []
        lines.append("# Skill Dependency Map\n")
        lines.append(f"This document maps the relationship network between all **{len(skills)} Hermes skills** in this repository. It is generated from the `related_skills` field in each skill's frontmatter.\n")
        lines.append(f"**Network stats:** {result['total_refs']} `related_skills` cross-references across {len(refs)} skills ({len(standalone_sorted)} skills are standalone with no `related_skills` entries).\n")

        lines.append("## Hub Skills (referenced by 2+ other skills)\n")
        lines.append("These are the core skills that serve as building blocks, referenced by many other skills:\n")
        lines.append("| Skill | Referenced By (count) | Referencing Skills |\n")
        lines.append("|-------|-----------------------|---------------------|\n")
        for skill_name, referrers in hubs_sorted:
            ref_str = ", ".join(sorted(referrers))
            lines.append(f"| `{skill_name}` | {len(referrers)} | {ref_str} |\n")

        lines.append("## Standalone Skills\n")
        lines.append(f"The following {len(standalone_sorted)} skills have no `related_skills` entries of their own (they do not reference other skills). These are genuinely standalone — no other skill references them either:\n")
        for name in standalone_sorted:
            lines.append(f"- `{name}`\n")

        lines.append("## Related Skills Validation\n")
        broken = []
        for name, related_list in refs.items():
            for ref in related_list:
                if ref not in skills:
                    broken.append((name, ref))
        if broken:
            for name, ref in broken:
                lines.append(f"- ⚠️ `{name}` references non-existent skill `{ref}`\n")
        else:
            lines.append(f"All {result['total_refs']} `related_skills` references in the repository resolve to existing in-repo skills. Verified against {len(skills)} unique skill names.\n")

        lines.append("\n---\n")
        lines.append(f"\n*Last generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')} from live frontmatter analysis of all {len(skills)} skills.*\n")

        dep_path = repo_root / "DEPENDENCY.md"
        existing = dep_path.read_text(encoding="utf-8") if dep_path.exists() else ""
        new_content = "".join(lines)
        if existing != new_content:
            dep_path.write_text(new_content, encoding="utf-8")
            result["updated"] = True
        else:
            result["updated"] = False

        result["hub_count"] = len(hubs_sorted)
        result["standalone_count"] = len(standalone_sorted)

    except Exception as e:
        result["success"] = False
        result["error"] = str(e)

    return result


def run_audit(repo_root: Path) -> dict:
    """Run the skill audit script and include results."""
    audit_script = repo_root / "tools" / "audit-skills.py"
    result = {"action": "audit", "success": True, "error": None}
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
                result["threshold_breached"] = False
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            result["threshold_breached"] = False
    else:
        result["success"] = False
        result["error"] = f"Audit script not found at {audit_script}"
        result["threshold_breached"] = False
    return result


# ── Main ──


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

    # Step 5.5: Regenerate DEPENDENCY.md from current related_skills frontmatter
    dep_result = generate_dependency_map(REPO_ROOT)
    report["steps"].append(dep_result)

    # Step 6: Run audit (before commit to catch issues early)
    audit_result = run_audit(REPO_ROOT)
    report["steps"].append(audit_result)

    # Step 7: If there are changes from local env, commit and push
    dep_updated = dep_result.get("updated", False)
    total_changes = (
        push_skills["files_copied"]
        + push_skills["files_new"]
        + mem_result["files_synced"]
        + prof_result["files_synced"]
        + (1 if dep_updated else 0)
    )
    if total_changes > 0:
        commit_result = git_add_commit_push(
            REPO_ROOT,
            f"chore: sync {total_changes} file(s) from Hermes local env — "
            f"{push_skills['files_copied']} skills updated, {push_skills['files_new']} new skills, "
            f"{mem_result['files_synced']} memories, {prof_result['files_synced']} profile files, "
            f"{1 if dep_updated else 0} dependency map updates",
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
        "dep_map_updated": dep_result.get("updated", False),
    }

    # Silent mode: only output if there are changes, errors, or threshold breach
    has_errors = any(
        not step.get("success", True) for step in report["steps"] if step.get("action") in ("pull", "push", "audit", "dependency_map")
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
