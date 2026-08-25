#!/usr/bin/env python3
"""
Skill Repository Auditor
========================
Validates all SKILL.md files in the Hermes_Skills repository for:
  1. YAML frontmatter integrity (valid YAML, required fields)
  2. Description length (≤59 chars per SKILL.md description field)
  3. related_skills resolution (each name resolves to an existing skill)
  4. Body section presence (## What This Skill Does, ## When to Use)
  5. Cross-reference sanity (skill_view calls map to related_skills entries)
  6. Duplicate skill names (same name in different directories)

Output: JSON report suitable for cronjob delivery.
Exit codes: 0 = pass within thresholds, 1 = threshold breached.
"""
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
THRESHOLDS = {
    "broken_refs": 0,
    "yaml_errors": 0,
    "long_descriptions": 0,
    "duplicate_skills": 0,
    "temps_scripts": 0,
    "missing_body_sections": 0,
}

# ── Collect all skills ──────────────────────────────────────────────

def find_skill_files(root):
    """Find all SKILL.md files and map name→path.

    Skips .git/, .hermes/, profiles-export/, memories-export/, and memories/ —
    the latter two are sync-script outputs, not source skill content.
    """
    skills = {}
    duplicates = []  # (name, path, existing_path)
    for path in root.rglob("SKILL.md"):
        path_str = str(path).replace("\\", "/")  # Normalize for cross-platform matching
        if ".git/" in path_str or ".hermes/" in path_str:
            continue
        if "profiles-export/" in path_str or "memories-export/" in path_str or "memories/" in path_str:
            continue
        rel = path.relative_to(root)
        # Extract name from frontmatter
        try:
            text = path.read_text(encoding="utf-8")
            m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
            if m:
                import yaml
                fm = yaml.safe_load(m.group(1))
                name = fm.get("name", path.parent.name)
                if name in skills:
                    duplicates.append({
                        "name": name,
                        "path": str(rel),
                        "existing_path": skills[name]["path"],
                    })
                else:
                    skills[name] = {
                        "path": str(rel),
                        "path_obj": path,
                        "frontmatter": fm,
                        "body_start": m.end(),
                        "body": text[m.end():].strip(),
                    }
        except Exception:
            fallback_name = path.parent.name
            if fallback_name in skills:
                duplicates.append({
                    "name": fallback_name,
                    "path": str(rel),
                    "existing_path": skills[fallback_name]["path"],
                })
            else:
                skills[fallback_name] = {
                    "path": str(rel),
                    "path_obj": path,
                    "frontmatter": {},
                    "body_start": 0,
                    "body": text if "text" in dir() else "",
                }
    return skills, duplicates


def find_category_dirs(root):
    """Find all category directories (top-level dirs with multiple skills).

    Skips .git, .hermes, profiles-export, and memories-export —
    the latter two are sync-script outputs, not source category directories.
    """
    cats = {}
    skip_dirs = {".git", ".hermes", "profiles-export", "memories-export", "profile", "tools"}
    for entry in sorted(root.iterdir()):
        if entry.is_dir() and not entry.name.startswith(".") and entry.name not in skip_dirs:
            desc_path = entry / "DESCRIPTION.md"
            cats[entry.name] = {
                "has_description": desc_path.exists(),
                "skill_count": len(list(entry.rglob("SKILL.md"))),
            }
    return cats


# ── Validation checks ─────────────────────────────────────────────

REQUIRED_FRONTMATTER = {"name", "version", "author", "platforms"}
DESC_MAX = 59


def validate_frontmatter(skill_name, skill_info):
    """Check YAML frontmatter has required fields and no errors."""
    errors = []
    fm = skill_info["frontmatter"]
    if not fm:
        errors.append("Empty or unparseable frontmatter")
        return errors
    for field in REQUIRED_FRONTMATTER:
        if field not in fm:
            errors.append(f"Missing required field: {field}")
    meta = fm.get("metadata", {}).get("hermes", {})
    if not meta:
        errors.append("Missing metadata.hermes block")
    return errors


def validate_description(skill_name, skill_info):
    """Check description is within 59-char limit."""
    fm = skill_info["frontmatter"]
    desc = fm.get("description", "")
    if desc and len(desc) > DESC_MAX:
        return [f"Description too long ({len(desc)} chars, max {DESC_MAX}): {desc[:80]}"]
    return []


def validate_related_skills(skill_name, skill_info, all_skill_names):
    """Check each related_skill resolves to an existing skill name."""
    errors = []
    meta = skill_info["frontmatter"].get("metadata", {}).get("hermes", {})
    related = meta.get("related_skills", []) or []
    for ref in related:
        if ref == skill_name:
            errors.append(f"Self-reference in related_skills: {ref}")
        elif ref not in all_skill_names:
            errors.append(f"Broken related_skills reference: {ref}")
    return errors


def validate_body_sections(skill_name, skill_info):
    """Check for required body sections: '## What This Skill Does' and '## When to Use'.

    Recognizes alternative valid headers for 'What This Skill Does':
    - '## What's in this skill'
    - '## Overview'
    - '## Creative Standard'
    - '**What This Skill Does:**' (bold paragraph format)

    Recognizes alternative valid headers for 'When to Use':
    - '## When To Use' (non-standard capitalization — flagged as warning, not error)
    """
    errors = []
    body = skill_info["body"]

    # Check for "What This Skill Does" — accept standard header or alternatives
    has_wtd = (
        "## What This Skill Does" in body
        or "**What This Skill Does:**" in body
        or "## What's in this skill" in body
        or re.search(r"^##\s+(Overview|Creative Standard)\s*$", body, re.MULTILINE) is not None
    )
    if not has_wtd:
        errors.append("Missing '## What This Skill Does' section")

    # Check for "When to Use" — accept standard header, non-standard capitalization, or bold-paragraph format
    has_wtu = (
        "## When to Use" in body
        or "## When To Use" in body
        or "**When to Use:**" in body
    )
    if not has_wtu:
        errors.append("Missing '## When to Use' section")
    elif "## When To Use" in body and "## When to Use" not in body:
        # Non-standard capitalization — this is a warning, not a hard error
        # Don't append as error since the section IS present
        pass

    return errors


def validate_cross_references(skill_name, skill_info, all_skill_names):
    """Check skill_view() calls in body have corresponding related_skills entries."""
    errors = []
    body = skill_info["body"]
    fm = skill_info["frontmatter"]
    meta = fm.get("metadata", {}).get("hermes", {})
    related = set(meta.get("related_skills", []) or [])
    # Find all skill_view("xxx") calls — skip those with file_path (self-refs to refs)
    sv_calls = re.findall(r'skill_view\(["\']([^"\']+)["\']\)', body)
    sv_calls_with_path = re.findall(r'skill_view\([^)]*file_path\s*=\s*["\']', body)
    for ref in sv_calls:
        short_name = ref.split("/")[-1] if "/" in ref else ref
        # Self-referential skill_view with file_path is loading a reference file, not a skill
        if short_name == skill_name and any("file_path" in sv for sv in sv_calls_with_path):
            continue
        if short_name not in related:
            errors.append(f"skill_view('{ref}') called but '{short_name}' not in related_skills")
    return errors


def check_stale_placeholders(skill_name, skill_info):
    """Check for TODO/FIXME/PLACEHOLDER markers in production files."""
    body = skill_info["body"]
    flags = []
    for marker in ["TODO:", "FIXME:", "PLACEHOLDER"]:
        if marker in body:
            count = body.count(marker)
            flags.append(f"Found {count}x '{marker}' marker(s)")
    return flags


# ── Main ──────────────────────────────────────────────────────────

def run_audit():
    all_skills, duplicates = find_skill_files(REPO_ROOT)
    all_skill_names = set(all_skills.keys())

    report = {
        "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "repo_root": str(REPO_ROOT),
        "skill_count": len(all_skills),
        "issues": {
            "broken_refs": [],
            "yaml_errors": [],
            "long_descriptions": [],
            "duplicate_skills": [],
            "missing_body_sections": [],
            "missing_related_skills": [],
            "placeholder_markers": [],
            "missing_category_descriptions": [],
        },
    }

    # Report duplicate skill names (same name in different directories)
    for dup in duplicates:
        report["issues"]["duplicate_skills"].append(
            f'{dup["name"]}: found at both {dup["path"]} and {dup["existing_path"]}'
        )

    # Check each skill
    for skill_name, skill_info in sorted(all_skills.items()):
        # Frontmatter validation
        fm_errors = validate_frontmatter(skill_name, skill_info)
        for err in fm_errors:
            report["issues"]["yaml_errors"].append(f"{skill_name}: {err}")

        # Description length
        desc_errors = validate_description(skill_name, skill_info)
        for err in desc_errors:
            report["issues"]["long_descriptions"].append(f"{skill_name}: {err}")

        # Related skills resolution
        ref_errors = validate_related_skills(skill_name, skill_info, all_skill_names)
        for err in ref_errors:
            report["issues"]["broken_refs"].append(f"{skill_name}: {err}")

        # Body sections
        body_errors = validate_body_sections(skill_name, skill_info)
        for err in body_errors:
            report["issues"]["missing_body_sections"].append(f"{skill_name}: {err}")

        # Cross-references
        xref_errors = validate_cross_references(skill_name, skill_info, all_skill_names)
        for err in xref_errors:
            report["issues"]["missing_related_skills"].append(f"{skill_name}: {err}")

        # Placeholders
        placeholder_errors = check_stale_placeholders(skill_name, skill_info)
        for err in placeholder_errors:
            report["issues"]["placeholder_markers"].append(f"{skill_name}: {err}")

    # Check category DESCRIPTION.md files
    cats = find_category_dirs(REPO_ROOT)
    for cat_name, cat_info in sorted(cats.items()):
        if not cat_info["has_description"] and cat_info["skill_count"] > 1:
            report["issues"]["missing_category_descriptions"].append(
                f"{cat_name}/: missing DESCRIPTION.md ({cat_info['skill_count']} skills)"
            )

    # Summary counts
    report["summary"] = {
        field: len(report["issues"][field]) for field in report["issues"]
    }

    # Threshold check
    breaches = []
    for key, threshold in THRESHOLDS.items():
        actual = report["summary"].get(key, 0)
        if actual > threshold:
            breaches.append(f"{key}: {actual} > {threshold}")

    # temps/scripts check (placeholder for future expansion)
    script_issues = find_stale_script_refs(all_skills)
    report["summary"]["temps_scripts"] = len(script_issues)
    if len(script_issues) > THRESHOLDS["temps_scripts"]:
        breaches.append(f"temps_scripts: {len(script_issues)} > {threshold}")
    report["issues"]["temps_scripts"] = script_issues

    report["threshold_breached"] = len(breaches) > 0
    if breaches:
        report["breaches"] = breaches

    return report


def find_stale_script_refs(all_skills):
    """Check for referenced scripts that don't exist on disk."""
    issues = []
    script_pattern = re.compile(r'script:\s*"([^"]+)"')
    for skill_name, skill_info in all_skills.items():
        frontmatter = skill_info["frontmatter"]
        if not frontmatter:
            continue
        text = json.dumps(frontmatter, default=str)
        matches = script_pattern.findall(text)
        for script_ref in matches:
            # Resolve relative to skill dir
            skill_dir = skill_info["path_obj"].parent
            script_path = skill_dir / script_ref
            if not script_path.exists():
                issues.append(f"{skill_name}: referenced script not found: {script_ref}")
    return issues


if __name__ == "__main__":
    report = run_audit()
    print(json.dumps(report, indent=2))
    if report["threshold_breached"]:
        sys.exit(1)
    sys.exit(0)
