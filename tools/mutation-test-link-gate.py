#!/usr/bin/env python3
"""Mutation self-test for check-links.py.

The link checker had only ever been seen printing 'no broken links'. This builds hermetic
fixture trees (LINK_CHECK_ROOT redirects the scan; no repo file is touched) and asserts:

  K1  a link to a file that does not exist              -> exit 1, names the link
  K2  file.md#anchor where no heading has that slug     -> exit 1, names the anchor
  K3  same-file #anchor with no such heading            -> exit 1
  K4  a repeated heading's -1 slug, an <a id>, inline
      `code` and punctuation in headings                -> resolve, exit 0
  K5  broken links inside ``` fences and `code` spans   -> ignored, exit 0
  K6  a broken link under a templates/ dir              -> skipped by design, exit 0
  K7  an anchor into a .py file (script.py#L10)         -> out of scope, exit 0
  K8  a .md file that is not valid UTF-8                -> exit 2, FATAL unreadable
  K9  fewer links than the floor                        -> exit 2, FATAL scan failed
  K10 the clean fixture                                 -> exit 0
  K11 LINK_CHECK_MIN_LINKS without LINK_CHECK_ROOT      -> ignored (real floor stays 200)
  K12 the real repo                                     -> exit 0

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
GATE = REPO / "tools" / "check-links.py"

GUIDE = """# Guide

## Setup Steps

Text.

## Notes

## Notes

<a id="custom-spot"></a>

## The `run()` call: options & flags
"""
README = """# Fixture

See [the guide](docs/guide.md), [setup](docs/guide.md#setup-steps),
[second notes](docs/guide.md#notes-1), [custom](docs/guide.md#custom-spot),
[call](docs/guide.md#the-run-call-options--flags) and [below](#local-part).
Also [the script](tools/script.py) and [a line](tools/script.py#L3).

## Local Part
"""
FILES = {
    "README.md": README,
    "docs/guide.md": GUIDE,
    "tools/script.py": "print('x')\n",
}

failures = []


def build(root, extra=None, drop=()):
    files = dict(FILES)
    files.update(extra or {})
    for rel, content in files.items():
        if rel in drop:
            continue
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            p.write_bytes(content)
        else:
            p.write_text(content, encoding="utf-8")


def run(root=None, min_links="5", env_extra=None):
    env = dict(os.environ)
    env.pop("LINK_CHECK_ROOT", None)
    env.pop("LINK_CHECK_MIN_LINKS", None)
    if root is not None:
        env["LINK_CHECK_ROOT"] = str(root)
        env["LINK_CHECK_MIN_LINKS"] = min_links
    env.update(env_extra or {})
    return subprocess.run(
        [sys.executable, str(GATE)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
        env=env,
    )


def case(label, want_rc, needle=None, extra=None, drop=(), min_links="5"):
    tmp = tempfile.mkdtemp(prefix="link-mut-")
    try:
        root = Path(tmp)
        build(root, extra, drop)
        r = run(root, min_links)
        out = r.stdout + r.stderr
        if r.returncode != want_rc:
            failures.append(
                f"{label}: expected exit {want_rc}, got {r.returncode}\n{out.strip()[-500:]}"
            )
        elif needle and needle not in out:
            failures.append(
                f"{label}: exit {want_rc} but output lacks {needle!r}\n{out.strip()[-500:]}"
            )
        else:
            print(f"  [OK] {label}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


case("K1 missing file", 1, "docs/x.md -> missing.md", extra={"docs/x.md": "[gone](missing.md)\n"})
case(
    "K2 cross-file anchor",
    1,
    "#no-such-section",
    extra={"docs/y.md": "[bad](guide.md#no-such-section)\n"},
)
case("K3 same-file anchor", 1, "#nowhere", extra={"docs/z.md": "# Z\n\n[bad](#nowhere)\n"})
case("K4 repeat slug, <a id>, code + punctuation headings resolve", 0)
case(
    "K5 links in fences and code spans ignored",
    0,
    extra={"docs/c.md": "```\n[x](nope.md)\n```\n\nInline `[y](nope2.md)` example.\n"},
)
case(
    "K6 templates/ skipped",
    0,
    extra={"skill/templates/t.md": "[gen](diagrams/{{NAME}}.md)\n"},
)
case("K7 anchor into .py out of scope", 0)
case("K8 unreadable file", 2, "could not be read", extra={"docs/bad.md": b"\xff\xfe\x80 not utf-8"})
case("K9 below floor", 2, "floor", min_links="50")
case("K10 clean control", 0, "no broken links")

r = run(None, env_extra={"LINK_CHECK_MIN_LINKS": "999999"})
if r.returncode != 0:
    failures.append(
        "K11 LINK_CHECK_MIN_LINKS was honoured without LINK_CHECK_ROOT: "
        + (r.stdout + r.stderr).strip()[-300:]
    )
else:
    print("  [OK] K11 fixture floor ignored without a fixture root")

r = run(None)
if r.returncode != 0:
    failures.append("K12 real repo: " + (r.stdout + r.stderr).strip()[-500:])
else:
    print("  [OK] K12 real repo clean")

print()
if failures:
    print(f"FAILED ({len(failures)}):")
    for f in failures:
        print("  - " + f.replace("\n", "\n    "))
    sys.exit(len(failures))
print("ALL 12 CHECKS PASSED — link gate verified fail-loud (paths, anchors, unreadable, floor).")
sys.exit(0)
