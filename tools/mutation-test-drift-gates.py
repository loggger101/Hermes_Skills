#!/usr/bin/env python3
"""Mutation self-test for the five index drift gates (`--check` of every generator).

verify-all runs gen-skills-index / gen-code-index / gen-references-index /
regen-dependency-map / gen-claude-plugin with --check, and until this existed none of
those checks had ever been seen failing: a generator whose --check compared the wrong
file, or always printed [OK], would have looked exactly like a healthy one. This copies
the tree to a temp dir (no repo file is touched) and asserts:

  D0  the unmutated copy                        -> every --check exits 0
  D1  a new skill (SKILL.md)                    -> SKILLS-INDEX, DEPENDENCY, .claude-plugin DRIFT
  D2  a new script with a docstring             -> CODE-INDEX DRIFT
  D3  a new references/*.md                     -> REFERENCES-INDEX DRIFT
  D4  each index hand-edited (one stale line)   -> that generator's --check DRIFT (x5)
  D5  an index deleted                          -> DRIFT 'does not exist'
  D6  every category dir removed, write mode    -> each generator exits 2 [FATAL] below its
                                                   floor AND leaves its index byte-identical

Exit code = number of failed checks (0 = all five drift gates proven fail-loud).
"""

import hashlib
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

if sys.version_info < (3, 8):
    raise SystemExit("[FATAL] needs Python 3.8+")
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
IGNORE = shutil.ignore_patterns(
    ".git",
    "profiles-export",
    "memories-export",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
)
# gate -> (generator, index file(s) it owns)
GATES = {
    "SKILLS-INDEX": ("tools/gen-skills-index.py", ["SKILLS-INDEX.md"]),
    "CODE-INDEX": ("tools/gen-code-index.py", ["CODE-INDEX.md"]),
    "REFERENCES-INDEX": ("tools/gen-references-index.py", ["REFERENCES-INDEX.md"]),
    "DEPENDENCY": ("tools/regen-dependency-map.py", ["DEPENDENCY.md"]),
    ".claude-plugin": ("tools/gen-claude-plugin.py", [".claude-plugin/plugin.json"]),
}
PROBE_SKILL = """---
name: zz-drift-probe
description: "Planted by mutation-test-drift-gates.py"
version: 1.0.0
author: test
platforms: [linux]
metadata:
  hermes:
    tags: [test]
    related_skills: [hermes-agent]
---

# zz-drift-probe

## What This Skill Does

Probe.

## When to Use

Never.
"""

failures = []


def rmtree(path):
    """shutil.rmtree that clears read-only bits (OneDrive-copied trees carry them on Windows)."""

    def retry(func, p, _exc):
        os.chmod(p, stat.S_IWRITE)
        func(p)

    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=retry)
    else:
        shutil.rmtree(path, onerror=retry)


def run(root, gate, check=True):
    gen = GATES[gate][0]
    return subprocess.run(
        [sys.executable, gen] + (["--check"] if check else []),
        cwd=str(root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )


def ok(name):
    print(f"  [OK] {name}")


def expect_drift(root, gates, label, needle="[DRIFT]"):
    for gate in gates:
        r = run(root, gate)
        out = r.stdout + r.stderr
        if r.returncode != 1 or needle not in out:
            failures.append(
                f"{label}: {gate} --check gave rc={r.returncode}, wanted 1 + {needle!r}\n{out.strip()[-400:]}"
            )
        else:
            ok(f"{label} -> {gate} DRIFT")


def plant(root, rel, content):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


with tempfile.TemporaryDirectory(prefix="drift-mut-") as tmp:
    root = Path(tmp) / "repo"
    shutil.copytree(REPO, root, ignore=IGNORE)

    # D0: the copy must start clean, or every 'caught' below proves nothing.
    clean = True
    for gate in GATES:
        r = run(root, gate)
        if r.returncode != 0:
            clean = False
            failures.append(
                f"D0 baseline: {gate} --check rc={r.returncode}\n{(r.stdout + r.stderr).strip()[-400:]}"
            )
    if clean:
        ok("D0 baseline copy passes all five --check gates")
    else:
        print("baseline is not clean: regenerate the indexes in the repo first")

    if clean:
        # D1: a new skill
        skill = plant(root, "devops/zz-drift-probe/SKILL.md", PROBE_SKILL)
        expect_drift(root, ["SKILLS-INDEX", "DEPENDENCY", ".claude-plugin"], "D1 new skill")
        rmtree(skill.parent)

        # D2: a new script
        script = plant(
            root,
            "devops/docker-containers/scripts/zz_drift_probe.py",
            '"""Planted by mutation-test-drift-gates.py."""\nprint("probe")\n',
        )
        expect_drift(root, ["CODE-INDEX"], "D2 new script")
        script.unlink()

        # D3: a new reference doc
        ref = plant(
            root,
            "devops/docker-containers/references/zz-drift-probe.md",
            "# Drift probe\n\nPlanted.\n",
        )
        expect_drift(root, ["REFERENCES-INDEX"], "D3 new reference doc")
        ref.unlink()

        # D4: each index hand-edited
        for gate, (_, files) in GATES.items():
            f = root / files[0]
            orig = f.read_bytes()
            if gate == ".claude-plugin":
                f.write_bytes(orig.replace(b'"name"', b'"name" ', 1))
            else:
                f.write_bytes(orig + b"- stale line added by hand\n")
            expect_drift(root, [gate], f"D4 hand-edited {files[0]}")
            f.write_bytes(orig)

        # D5: an index deleted
        dep = root / "DEPENDENCY.md"
        orig = dep.read_bytes()
        dep.unlink()
        expect_drift(root, ["DEPENDENCY"], "D5 deleted DEPENDENCY.md", needle="does not exist")
        dep.write_bytes(orig)

        # D6: every category dir removed -> write mode must refuse below the floor and leave
        # each index untouched (the failure the write-guard exists for).
        for child in root.iterdir():
            if child.is_dir() and any(child.rglob("SKILL.md")):
                rmtree(child)
        for gate, (_, files) in GATES.items():
            before = {f: digest(root / f) for f in files}
            r = run(root, gate, check=False)
            after = {f: digest(root / f) for f in files}
            out = r.stdout + r.stderr
            if r.returncode != 2 or "[FATAL]" not in out:
                failures.append(
                    f"D6 {gate}: emptied tree, write mode rc={r.returncode} (wanted 2 + [FATAL])\n{out.strip()[-300:]}"
                )
            elif before != after:
                failures.append(f"D6 {gate}: refused, but its index changed on disk anyway")
            else:
                ok(f"D6 emptied tree -> {gate} refuses to overwrite (floor)")

print()
if failures:
    print(f"FAILED ({len(failures)}):")
    for f in failures:
        print("  - " + f.replace("\n", "\n    "))
    sys.exit(len(failures))
print("ALL CHECKS PASSED — the five index drift gates verified fail-loud (drift, deletion, floor).")
sys.exit(0)
