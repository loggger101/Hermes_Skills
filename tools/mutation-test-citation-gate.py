#!/usr/bin/env python3
"""Mutation self-test for check-citations.py.

A gate that has only ever been observed passing is indistinguishable from one that cannot
fail. This builds hermetic fixture trees (CITATION_CHECK_ROOT redirects the scan; no repo
file is touched) and asserts:

  C1   stale citation, filename exists elsewhere        -> exit 1, names moved?-> target
  C2   cross-skill SKILL.md whose skill dir was renamed -> exit 1, names moved?-> target
  C3   exact path resolves                              -> exit 0
  C4   skill-relative shorthand references/x.md         -> exit 0 (one owner)
  C5   ambiguous shorthand (two owners)                 -> exit 0 by design
  C6   citation inside a ``` fence                      -> ignored, exit 0
  C7   path whose first segment is not a repo dir       -> upstream path, ignored, exit 0
  C8   filename that exists nowhere here                -> WARN only, exit 0
  C9   stale citation under docs/archive/               -> skipped by design, exit 0
  C10  glob token `devops/*.md`                         -> ignored, exit 0
  C11  fixture below the scan floor                     -> exit 2 [FATAL]
  C12  MIN_CITATIONS set WITHOUT a fixture root         -> must be ignored (real run exits 0)
  C13  markdown that is not valid UTF-8                 -> exit 2 [FATAL]
  C15  a moved SCRIPT (unique tail-two match)           -> exit 1, names moved?-> target
  C16  ambiguous generic code basename (index.js x2)    -> WARN only, exit 0
  C14  the real repo                                    -> exit 0

Exit 1 if any check failed (never the count: it wraps at 256 and 77 means SKIP) (0 = gate proven fail-loud).
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
GATE = REPO / "tools" / "check-citations.py"

# a citation that always resolves, so 'skipped' cases still clear the scan floor
LIVE = "`devops/alpha/references/live.md` is here\n"


def build(root: Path, doc="", archive=None, extra=None, bad_bytes=False):
    (root / "devops" / "alpha" / "references").mkdir(parents=True, exist_ok=True)
    (root / "github" / "beta" / "references").mkdir(parents=True, exist_ok=True)
    (root / "devops" / "alpha" / "SKILL.md").write_text("# alpha\n", encoding="utf-8")
    (root / "github" / "beta" / "SKILL.md").write_text("# beta\n", encoding="utf-8")
    (root / "devops" / "alpha" / "references" / "live.md").write_text("# live\n", encoding="utf-8")
    # a file whose basename is unique in the tree -> move-signature anchor for C1
    (root / "github" / "beta" / "references" / "orphan-note.md").write_text(
        "# orphan\n", encoding="utf-8"
    )
    body = LIVE + doc
    if bad_bytes:
        body += "\n`devops/alpha/references/live.md`\n"
    (root / "README.md").write_text(body, encoding="utf-8")
    if bad_bytes:
        # undecodable bytes in a separate scanned file
        (root / "devops" / "broken.md").write_bytes(b"\xff\xfe\x80 not utf-8 `x/y.md`\n")
    for rel, content in (extra or {}).items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    if archive is not None:
        (root / "docs" / "archive").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "archive" / "old-audit.md").write_text(archive, encoding="utf-8")
    return root


def run(root=None, min_cit=None):
    env = dict(os.environ)
    env.pop("CITATION_CHECK_ROOT", None)
    env.pop("CITATION_CHECK_MIN_CITATIONS", None)
    if root is not None:
        env["CITATION_CHECK_ROOT"] = str(root)
        if min_cit is not None:
            env["CITATION_CHECK_MIN_CITATIONS"] = str(min_cit)
    return subprocess.run(
        [sys.executable, str(GATE)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(REPO),
        timeout=300,
        env=env,
    )


failures = []


def case(label, want_rc, needle=None, min_cit=1, **kw):
    tmp = Path(tempfile.mkdtemp(prefix="cite-mut-"))
    try:
        r = run(build(tmp, **kw), min_cit=min_cit)
        out = r.stdout + r.stderr
        if r.returncode != want_rc:
            failures.append(
                f"{label}: expected exit {want_rc}, got {r.returncode}\n{out.strip()[-400:]}"
            )
        elif needle and needle not in out:
            failures.append(
                f"{label}: exit {want_rc} but output lacks {needle!r}\n{out.strip()[-400:]}"
            )
        else:
            print(f"  [OK] {label}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


print("=== mutation-test: citation gate ===")

case(
    "C1 stale citation with unique basename elsewhere",
    1,
    "moved?->github/beta/references/orphan-note.md",
    doc="See `devops/alpha/references/orphan-note.md`.\n",
)
case(
    "C2 cross-skill SKILL.md whose dir was renamed",
    1,
    "moved?->github/beta/SKILL.md",
    doc="Read `devops/beta/SKILL.md`.\n",
)
case(
    "C3 exact path resolves",
    0,
    "stale (must fix): 0",
    doc="See `devops/alpha/references/live.md`.\n",
)
case(
    "C4 skill-relative shorthand with one owner",
    0,
    "informational: 0",
    extra={
        "github/beta/SKILL.md": "# beta\n\nsee references/orphan-note.md and `references/orphan-note.md`\n"
    },
)
case(
    "C5 ambiguous shorthand tolerated",
    0,
    doc="See `devops/alpha/references/live.md`.\n",
    extra={
        "github/beta/references/dup.md": "# dup\n",
        "devops/alpha/references/dup.md": "# dup\n",
        "github/beta/SKILL.md": "# beta\n\n`references/dup.md`\n",
    },
)
case(
    "C6 citation inside a fence is ignored",
    0,
    doc="```\nSee `devops/alpha/references/orphan-note.md`.\n```\n",
)
case(
    "C7 upstream path (first segment not a repo dir) ignored",
    0,
    doc="Upstream docs: `polars-src/docs/source/lazy.md`.\n",
)
case(
    "C8 filename that exists nowhere here is WARN only",
    0,
    "informational: 1",
    doc="Mentions `devops/alpha/references/deleted-long-ago.md`.\n",
)
case(
    "C9 stale citation under docs/archive is skipped by design",
    0,
    archive="As of the audit it lived at `devops/alpha/references/orphan-note.md`.\n",
)
case("C10 glob token ignored", 0, doc="Pattern `devops/*.md` matches files.\n")

# C11: fixture with one citation but a floor of 5 -> must fail loud
tmp = Path(tempfile.mkdtemp(prefix="cite-mut-"))
try:
    build(tmp)
    r = run(tmp, min_cit=5)
    out = r.stdout + r.stderr
    if r.returncode != 2 or "[FATAL]" not in out:
        failures.append(
            f"C11 below floor: rc={r.returncode}, wanted 2 + [FATAL]\n{out.strip()[-300:]}"
        )
    else:
        print("  [OK] C11 fixture below scan floor fails loud")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# C12: MIN_CITATIONS without a fixture root must be ignored (cannot disarm the real gate)
env = dict(os.environ, CITATION_CHECK_MIN_CITATIONS="999999")
env.pop("CITATION_CHECK_ROOT", None)
r = subprocess.run(
    [sys.executable, str(GATE)],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
    cwd=str(REPO),
    timeout=300,
    env=env,
)
if r.returncode != 0:
    failures.append(
        "C12 MIN_CITATIONS honoured without a fixture root: " + (r.stdout + r.stderr).strip()[-300:]
    )
else:
    print("  [OK] C12 scan floor env ignored without a fixture root")

case(
    "C13 markdown that is not valid UTF-8 fails loud",
    2,
    "[FATAL]",
    bad_bytes=True,
)

# C15: a moved SCRIPT (unique tail-two-segment match) is the same defect class as a moved doc.
case(
    "C15 moved script citation fails loud",
    1,
    "moved?->devops/alpha/scripts/perf_audit.py",
    extra={"devops/alpha/scripts/perf_audit.py": '"""audit"""\n'},
    doc="Run `github/beta/scripts/perf_audit.py` before shipping.\n",
)

# C16: generic code names collide across projects - an ambiguous code hit must stay a WARN.
case(
    "C16 ambiguous generic code basename is WARN only",
    0,
    "informational: 1",
    extra={"web/x/index.js": "// a\n", "tools/y/index.js": "// b\n"},
    doc="See `web/z/index.js` for the pattern.\n",
)

r = subprocess.run(
    [sys.executable, str(GATE)],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
    cwd=str(REPO),
    timeout=300,
)
if r.returncode != 0:
    failures.append("C14 real repo FAILED: " + (r.stdout + r.stderr).strip()[-400:])
else:
    print("  [OK] C14 real repo passes clean")

print()
if failures:
    print(f"FAILED ({len(failures)}):")
    for f in failures:
        print("  - " + f.replace("\n", "\n    "))
    sys.exit(1 if failures else 0)
print(
    "ALL 16 CHECKS PASSED — citation gate verified fail-loud (doc moves, script moves, fences, archives, floor, unreadable)."
)
sys.exit(0)
