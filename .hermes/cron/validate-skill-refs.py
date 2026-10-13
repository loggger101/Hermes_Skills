#!/usr/bin/env python3
"""Lightweight JSON + skill-ref validator (no_agent-compatible)."""

import json
import os
import sys

# ── Environment guard ───────────────────────────────────────────────────────
# A wrong interpreter must fail HERE, loudly — never half-run and report clean.
# On Windows, bare `python` / `python3` are usually Microsoft Store alias stubs
# that never execute the script at all; use `py` there (README → Verification).
if sys.version_info < (3, 8):
    raise SystemExit(
        "[FATAL] this tool needs Python 3.8+, got "
        f"{sys.version.split()[0]} at {sys.executable or '<unknown interpreter>'}"
    )
try:  # repo content is UTF-8; a cp1252 console must not abort an otherwise-clean run
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JOBS_DIR = os.path.join(BASE, ".hermes", "cron", "active")
SKIP = ("/.git/", "/.hermes/cron/", "profiles-export/", "memories-export/", "/memories/")

valid = {}
for path, _dirs, files in os.walk(BASE):
    if any(s in path.replace("\\", "/") for s in SKIP):
        continue
    if "SKILL.md" in files:
        rel = os.path.relpath(path, BASE).replace("\\", "/")
        nm = "?"
        with open(os.path.join(path, "SKILL.md"), encoding="utf-8") as f:
            for line in f:
                if line.startswith("name:"):
                    nm = line.split(":", 1)[1].strip()
                    break
        valid[rel] = nm

ok = True
jobs = sorted(j for j in os.listdir(JOBS_DIR) if j.endswith(".json"))
if not jobs:
    # Round-257: an empty (or emptied) active/ dir printed "ALL OK" having checked nothing.
    print(f"[FATAL] no job configs (*.json) in {JOBS_DIR}: nothing to validate")
    sys.exit(2)
refs = 0
for job in jobs:
    fp = os.path.join(JOBS_DIR, job)
    with open(fp, encoding="utf-8") as f:
        data = json.load(f)  # raises if invalid
    skills = data.get("skills", {})
    loaded = skills.get("loaded", skills) if isinstance(skills, dict) else skills
    if isinstance(loaded, str):
        loaded = [loaded]
    if not loaded:
        print(f"  NONE:   {job} loads no skills")
    for s in loaded:
        refs += 1
        sid = s if isinstance(s, str) else s.get("id", "?")
        if sid not in valid:
            print(f"  BROKEN: {job} -> {sid}")
            ok = False
        else:
            print(f"  OK:     {job} -> {sid} (name={valid[sid]})")
print(f"\n{'ALL OK' if ok else 'ISSUES'} | jobs={len(jobs)} refs={refs} valid_skills={len(valid)}")
sys.exit(0 if ok else 1)
