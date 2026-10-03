#!/usr/bin/env python3
"""Mutation test for audit-skills.run_audit — the per-skill audit checks test themselves.

Same philosophy as mutation-test-secret-gate.py: a gate that cannot be shown to fail
has not been shown to work. This script builds a temp skill tree holding ONE planted
defect per threshold-gated issue class plus a clean control skill, points audit-skills'
REPO_ROOT at it, runs the full audit, and asserts:

  * every planted defect lands in its issue class, naming the defective skill
  * the clean control skill appears in no issue list (no false positives)
  * every threshold-gated class except hardcoded_secrets (mutation-test-secret-gate.py
    covers that one) has a mutation here -- a new threshold key without a planted
    defect fails this test until one is added

Two of these mutations were written for defects this gate used to wave through: a
SKILL.md with no frontmatter block was silently left out of the audit (M1), and the
frontmatter `script:` existence check could never match anything (M7).

Run:  py tools/mutation-test-audit-gate.py     (also invoked by verify-all as a gate)
Exit 0 = every mutation caught AND the control is clean; exit 1 otherwise.
"""

import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

if sys.version_info < (3, 8):
    raise SystemExit(
        "[FATAL] this tool needs Python 3.8+, got "
        + sys.version.split()[0]
        + f" at {sys.executable or '<unknown interpreter>'}"
    )
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

_HERE = Path(__file__).resolve()
REPO = _HERE.parents[1]
if not (REPO / "tools" / "audit-skills.py").exists():
    raise SystemExit(
        f"[FATAL] {_HERE.name} must run from the repo's tools/ dir "
        f"(no tools/audit-skills.py under {REPO})"
    )


def load_auditor():
    spec = importlib.util.spec_from_file_location("auditskills", REPO / "tools" / "audit-skills.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BODY = "\n## What This Skill Does\n\nx\n\n## When to Use\n\n- y\n"


def skill(name, *, description="Fine.", author="author: t\n", related="[]", extra=""):
    return (
        "---\n"
        f"name: {name}\n"
        f'description: "{description}"\n'
        "version: 1.0.0\n"
        f"{author}"
        "platforms: [linux]\n"
        "metadata:\n"
        "  hermes:\n"
        "    tags: [t]\n"
        f"    related_skills: {related}\n"
        f"{extra}"
        "---\n" + BODY
    )


# dir under cat/ -> SKILL.md content
FIXTURE = {
    "clean": skill("clean"),
    "m1-nofm": "# No frontmatter block\n" + BODY,
    "m2-nofield": skill("m2-nofield", author=""),
    "m3-longdesc": skill("m3-longdesc", description="x" * 80),
    "m4-badref": skill("m4-badref", related="[no-such-skill]"),
    "m5-dup-a": skill("m5-dup"),
    "m5-dup-b": skill("m5-dup"),
    "m6-nobody": skill("m6-nobody").replace(BODY, "\nBody without the required sections.\n"),
    "m7-script": skill("m7-script", extra="    script: scripts/missing.py\n"),
}

# (label, issue class, skill name that must appear in that class)
MUTATIONS = [
    ("M1 SKILL.md without frontmatter", "yaml_errors", "m1-nofm"),
    ("M2 missing required field", "yaml_errors", "m2-nofield"),
    ("M3 description over 59 chars", "long_descriptions", "m3-longdesc"),
    ("M4 broken related_skills ref", "broken_refs", "m4-badref"),
    ("M5 duplicate skill name", "duplicate_skills", "m5-dup"),
    ("M6 missing body sections", "missing_body_sections", "m6-nobody"),
    ("M7 frontmatter script not on disk", "temps_scripts", "m7-script"),
]


def main():
    mod = load_auditor()
    tmp = Path(tempfile.mkdtemp(prefix="audit-gate-mut-", dir=str(REPO.parent)))
    try:
        for d, text in FIXTURE.items():
            p = tmp / "cat" / d / "SKILL.md"
            p.parent.mkdir(parents=True)
            p.write_text(text, encoding="utf-8")
        (tmp / "cat" / "DESCRIPTION.md").write_text("cat\n", encoding="utf-8")
        mod.REPO_ROOT = tmp  # same monkeypatch trick as the other gate self-tests
        mod.MIN_EXPECTED_SKILLS = 1  # the fixture is tiny by design

        report = mod.run_audit()
        issues = report["issues"]
        failures = []

        for label, cls, name in MUTATIONS:
            hit = any(f.startswith(name) or f"{name}:" in f for f in issues.get(cls, []))
            print(f"  {'caught' if hit else 'MISSED'}: {label} -> {cls}")
            if not hit:
                failures.append(f"{label} not reported under {cls}")

        polluted = [
            f"{cls}: {f}" for cls, found in issues.items() for f in found if f.startswith("clean")
        ]
        print(f"  {'CLEAN ' if not polluted else 'FALSE-POSITIVE'}: control skill")
        failures.extend(f"control flagged: {p}" for p in polluted)

        if not report["threshold_breached"]:
            failures.append("run_audit did not report threshold_breached on a defective tree")

        uncovered = set(mod.THRESHOLDS) - {cls for _, cls, _ in MUTATIONS} - {"hardcoded_secrets"}
        if uncovered:
            failures.append(f"threshold class(es) with no planted mutation: {sorted(uncovered)}")

        if not failures:
            print(
                f"ALL {len(MUTATIONS)} MUTATIONS CAUGHT, CONTROL CLEAN — audit gate verified fail-loud."
            )
            return 0
        print("\nFAILED: " + "; ".join(failures))
        return 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
