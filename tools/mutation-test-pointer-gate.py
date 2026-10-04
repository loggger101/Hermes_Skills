#!/usr/bin/env python3
"""Mutation self-test for check-skill-pointers.py (round-65).

A gate that has only ever been observed passing is indistinguishable from one that cannot fail.
This plants one defect per pointer form in hermetic temp fixtures (SKILL_POINTER_SCAN_ROOT
redirects the gate's scan root; no repo file is touched) and asserts the gate exits 1 and names
the defect:

  M1  skill_view of a skill that does not exist (the 'wiretext' class)   -> no such skill
  M2  skill_view of a tool name (the 'web_extract' class)                -> no such skill
  M3  hermes skill load with the wrong category directory (README class) -> not at that path
  M4  hermes skill load of a path that does not exist                    -> no such skill
  M5  skill_manage("install", ...) of a skill that does not exist        -> no such skill
  M6  a phantom inside a JSON string (escaped quotes, as cron prompts)   -> no such skill
  M7  a phantom under docs/archive/                                      -> MUST be skipped
  M8  placeholders (xxx, <skill-name>, '...', plugin:foo)                -> MUST be skipped
  M9  unmutated fixture                                                  -> MUST pass
  M10 a scan root with no skills                                         -> MUST fail loud
  M11 the real repo                                                      -> MUST pass

Exit code = number of failed checks (0 = gate proven fail-loud).
"""

import os
import shutil
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
GATE = REPO / "tools" / "check-skill-pointers.py"

SKILLS = [
    ("software-development", "alpha-planner"),
    ("github", "beta-debug"),
    ("research", "gamma-search"),
]
CLEAN_DOC = """# Notes

Plan with `skill_view(name='alpha-planner')`, then `skill_view("beta-debug")`.
Quick start: hermes skill load github/beta-debug
Install: skill_manage("install", "gamma-search")
Docs may show placeholders: skill_view(name='xxx'), skill_view(name='<skill-name>'),
skill_view(name='...'), skill_view(name='plugin:some-skill'), hermes skill load <category>/<name>
"""


def build(tmp, extra_doc="", archive_doc=None, json_text=None, with_skills=True):
    root = Path(tmp)
    if with_skills:
        for cat, name in SKILLS:
            d = root / cat / name
            d.mkdir(parents=True, exist_ok=True)
            (d / "SKILL.md").write_text(
                f'---\nname: {name}\ndescription: "d"\n---\n\n# {name}\n', encoding="utf-8"
            )
    (root / "README.md").write_text(CLEAN_DOC + extra_doc, encoding="utf-8")
    if archive_doc is not None:
        (root / "docs" / "archive").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "archive" / "old.md").write_text(archive_doc, encoding="utf-8")
    if json_text is not None:
        (root / "job.json").write_text(json_text, encoding="utf-8")
    return root


def run(root):
    env = dict(os.environ, SKILL_POINTER_SCAN_ROOT=str(root))
    return subprocess.run(
        [sys.executable, str(GATE)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(REPO),
        timeout=120,
        env=env,
    )


failures = []


def expect_fail(label, needle, **kw):
    tmp = tempfile.mkdtemp(prefix="pointer-mut-")
    try:
        r = run(build(tmp, **kw))
        out = r.stdout + r.stderr
        if r.returncode == 0:
            failures.append(f"{label} NOT caught (gate passed)")
        elif needle not in out:
            failures.append(f"{label} caught but output lacks {needle!r}: {out.strip()[:140]}")
        else:
            print(f"  [OK] {label}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def expect_pass(label, **kw):
    tmp = tempfile.mkdtemp(prefix="pointer-mut-")
    try:
        r = run(build(tmp, **kw))
        if r.returncode != 0:
            failures.append(
                f"{label} FAILED (false positive): {(r.stdout + r.stderr).strip()[:160]}"
            )
        else:
            print(f"  [OK] {label}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


print("=== mutation-test: skill pointer gate ===")

expect_fail(
    "M1 phantom skill_view target",
    "wiretext  (no such skill)",
    extra_doc="\nUse skill_view(name='wiretext').\n",
)
expect_fail(
    "M2 tool name used as a skill",
    "web_extract  (no such skill)",
    extra_doc="\nLoad skill_view(name='web_extract').\n",
)
expect_fail(
    "M3 wrong category directory",
    "(skill exists but not at that path)",
    extra_doc="\nhermes skill load software-development/beta-debug\n",
)
expect_fail(
    "M4 skill load of a missing path",
    "github/ghost  (no such skill)",
    extra_doc="\nhermes skill load github/ghost\n",
)
expect_fail(
    "M5 install of a missing skill",
    "ghost-install  (no such skill)",
    extra_doc='\nskill_manage("install", "ghost-install")\n',
)
expect_fail(
    "M6 phantom inside a JSON string",
    "ghost-json  (no such skill)",
    json_text='{"prompt": "run skill_view(name=\\"ghost-json\\") first"}',
)

expect_pass(
    "M7 phantom under docs/archive is skipped", archive_doc="skill_view(name='long-gone')\n"
)
expect_pass("M8 placeholders are skipped (already in the clean doc)")
expect_pass("M9 clean fixture passes (no false positive)")

tmp = tempfile.mkdtemp(prefix="pointer-mut-")
try:
    r = run(build(tmp, with_skills=False))
    if r.returncode == 0 or "FATAL" not in (r.stdout + r.stderr):
        failures.append("M10 empty scan root did NOT fail loud")
    else:
        print("  [OK] M10 scan root with no skills fails loud")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

r = subprocess.run(
    [sys.executable, str(GATE)],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
    cwd=str(REPO),
    timeout=120,
)
if r.returncode != 0:
    failures.append(f"M11 real repo FAILED: {(r.stdout + r.stderr).strip()[:160]}")
else:
    print("  [OK] M11 real repo passes clean")

print()
if failures:
    print(f"FAILED ({len(failures)}):")
    for f in failures:
        print("  " + f)
    sys.exit(len(failures))
print("ALL 11 CHECKS PASSED — skill pointer gate verified fail-loud.")
sys.exit(0)
