#!/usr/bin/env python3
"""Run every health gate in this repo and report one verdict.

The repo had several checks but no single command that ran them all, and nothing
at all that noticed when a generated index fell behind the files it describes --
which is how "166 skills" survived in README/DESCRIPTION while 167 were on disk.

Gates, in order (each must pass):

  1. audit-skills.py        frontmatter, descriptions, related_skills, body sections
  2. check-links.py         every relative markdown link resolves
  3. index drift            SKILLS/CODE/REFERENCES/DEPENDENCY match what is on disk
  4. cron validators        job configs are structurally valid, skill refs resolve
  5. doc counts             hand-written counts in README/DESCRIPTION match reality

Usage:
    py tools/verify-all.py            # Windows -- `python` is a Store alias stub
    python3 tools/verify-all.py       # Linux/macOS

Exit 0 = every gate passed. Exit 1 = at least one failed (details above the summary).
Child tools are launched with sys.executable, never a which() lookup.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

if sys.version_info < (3, 8):
    raise SystemExit(
        "[FATAL] verify-all.py needs Python 3.8+, got "
        + sys.version.split()[0] + " at " + (sys.executable or "<unknown interpreter>")
    )
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

REPO = Path(__file__).resolve().parents[1]
PY = sys.executable or "python3"


def run(label, args, cwd=REPO):
    """Run a child tool; return (label, ok, first meaningful output line)."""
    try:
        proc = subprocess.run([PY] + args, cwd=str(cwd), capture_output=True,
                              text=True, timeout=300)
    except Exception as e:
        return label, False, str(e)[:200]
    out = (proc.stdout or "") + (proc.stderr or "")
    tail = [ln for ln in out.splitlines() if ln.strip()]
    note = ""
    for ln in tail:
        if any(k in ln for k in ("FATAL", "DRIFT", "BROKEN", "ERROR", "Errors:")):
            note = ln.strip()
            break
    if not note and tail:
        note = tail[-1].strip()
    return label, proc.returncode == 0, note[:160]


def run_audit_gate():
    """audit-skills.py emits a JSON report; summarise it rather than echoing its last brace."""
    label = "audit-skills"
    try:
        proc = subprocess.run([PY, "tools/audit-skills.py"], cwd=str(REPO),
                              capture_output=True, text=True, timeout=300)
    except Exception as e:
        return label, False, str(e)[:200]
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        first = (proc.stdout + proc.stderr).strip().splitlines()
        return label, False, (first[0] if first else "no output")[:160]
    note = f"{data['skill_count']} skills, breached={data['threshold_breached']}"
    if data.get("breaches"):
        note += " | " + "; ".join(data["breaches"])
    return label, proc.returncode == 0 and not data["threshold_breached"], note[:160]


def check_doc_counts():
    """Hand-written counts in README/DESCRIPTION must match the live skill count."""
    skills = [p for p in REPO.rglob("SKILL.md")
              if not any(part in (".git", ".hermes", "profiles-export", "memories",
                                  "memories-export") for part in p.relative_to(REPO).parts)]
    live = len(skills)
    problems = []
    for name in ("README.md", "DESCRIPTION.md"):
        text = (REPO / name).read_text(encoding="utf-8")
        for m in re.finditer(r"\*\*(\d{2,4}) (?:verified, audit-passing skills|Hermes Agent skills|skills)", text):
            if int(m.group(1)) != live:
                problems.append(f"{name}: claims {m.group(1)} skills, disk has {live}")
        for m in re.finditer(r"all (\d{2,4}) skills", text):
            if int(m.group(1)) != live:
                problems.append(f"{name}: claims 'all {m.group(1)} skills', disk has {live}")
    return ("doc counts", not problems, "; ".join(problems)[:160] or f"{live} skills, counts agree")


def main():
    results = [
        run_audit_gate(),
        run("check-links", ["tools/check-links.py"]),
        run("drift: SKILLS-INDEX", ["tools/gen-skills-index.py", "--check"]),
        run("drift: CODE-INDEX", ["tools/gen-code-index.py", "--check"]),
        run("drift: REFERENCES-INDEX", ["tools/gen-references-index.py", "--check"]),
        run("drift: DEPENDENCY", ["tools/regen-dependency-map.py", "--check"]),
        run("cron: configs", [".hermes/cron/validate-cronjobs.py"]),
        run("cron: skill refs", [".hermes/cron/validate-skill-refs.py"]),
        check_doc_counts(),
    ]

    width = max(len(r[0]) for r in results)
    print("\n=== verify-all ===")
    for label, ok, note in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {label.ljust(width)}  {note}")

    failed = [r[0] for r in results if not r[1]]
    print()
    if failed:
        print(f"FAILED ({len(failed)}/{len(results)}): {', '.join(failed)}")
        return 1
    print(f"ALL {len(results)} GATES PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
