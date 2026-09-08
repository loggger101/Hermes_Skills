#!/usr/bin/env python3
"""Broken-link checker for this second brain (stdlib only).

Scans every .md file in the repo and verifies that relative markdown links
point at files/directories that exist. Catches exactly the class of bug where a
doc references a file that was never created or got renamed (e.g. a dangling
AGENTS.md pointer) — cheap insurance for a discoverability-focused repo.

Rules:
- Skips external URLs (http/https/mailto), pure anchors (#...), absolute paths, and links inside
  fenced code blocks or inline `code` spans (docs show example syntax like ![alt](url)).
- Skips link targets containing {{TOKEN}} placeholders — skill template files (e.g.
  software-development/code-wiki/templates/) ship fill-in-the-blank links that only resolve
  after generation; they are not hand-maintained references. Same rule applies to every file
  under a <category>/<skill>/templates/ dir: those are scaffolds copied-and-filled at use time,
  so their relative links (diagrams/, modules/X.md) point at generated output by design.
- Strips #anchors before checking existence.
- memories/MEMORY.md and memories/USER.md are SKIPPED: one-way exports of the live store (see
  memories/DESCRIPTION.md). Entries quote markdown-shaped fragments as prose, and the repo cannot
  fix a link inside a file the next sync overwrites.
- profiles-export/ is SKIPPED: those are historical per-profile snapshots (see profile/DESCRIPTION.md);
  they may predate later fixes and are regenerated from live environments, not hand-maintained here.

Usage: python tools/check-links.py          # exit 0 = no broken links, 1 = found some
"""
import re
import sys
from pathlib import Path

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

REPO = Path(__file__).resolve().parents[1]
MIN_EXPECTED_LINKS = 200  # floor: below this the scan failed, whatever it reports
SKIP_DIRS = {".git"}
SNAPSHOT_PREFIXES = ("profiles-export/", "memories-export/")
# One-way exports of the live Hermes memory store: their entries quote markdown-shaped
# fragments as prose, and the repo cannot fix a link inside a file the next sync overwrites.
# Deliberately file-scoped, not "memories/" -- the hand-written memories/DESCRIPTION.md
# stays gated like any other doc.
EXPORTED_FILES = ("memories/MEMORY.md", "memories/USER.md")
LINK_RE = re.compile(r'\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)')


def main():
    broken = []
    unreadable = []  # files the scan could not open: coverage gaps, not warnings
    checked = 0
    for p in REPO.rglob("*.md"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        rel_posix = str(p.relative_to(REPO)).replace("\\", "/")
        if rel_posix.startswith(SNAPSHOT_PREFIXES):
            continue  # historical snapshots — not hand-maintained (see module docstring)
        if rel_posix in EXPORTED_FILES:
            continue  # live-memory exports — see module docstring
        parts = p.relative_to(REPO).parts
        if "templates" in parts:
            continue  # skill template scaffolds — links resolve only after generation
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as e:
            unreadable.append(f"{p}: {e}")
            continue
        # strip fenced code blocks so example links in docs don't count,
        # then inline `code` spans (e.g. markdown syntax examples like ![alt](url))
        text_no_code = re.sub(r'```.*?```', '', text, flags=re.S)
        text_no_code = re.sub(r'`[^`\n]*`', '', text_no_code)
        for m in LINK_RE.finditer(text_no_code):
            target = m.group(1).strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path_part = target.split("#")[0]
            if not path_part:
                continue  # pure anchor
            if path_part.startswith("/"):
                continue  # absolute — out of scope for this checker
            checked += 1
            resolved = (p.parent / path_part).resolve()
            try:
                ok = resolved.exists()
            except OSError:
                ok = False
            if not ok:
                rel_from_repo = str(p.relative_to(REPO)).replace("\\", "/")
                broken.append(f"{rel_from_repo} -> {target}")

    print(f"checked {checked} relative links across repo .md files")
    if unreadable:
        print(f"[FATAL] {len(unreadable)} file(s) could not be read -- link coverage is "
              "incomplete, so a clean result would be meaningless:", file=sys.stderr)
        for u in unreadable:
            print("  " + u, file=sys.stderr)
        sys.exit(2)
    if checked < MIN_EXPECTED_LINKS:
        print(
            f"[FATAL] only {checked} links checked (floor {MIN_EXPECTED_LINKS}) -- the scan "
            "itself failed. A link checker that found nothing to check has not verified "
            "anything; treat this as broken, not clean.",
            file=sys.stderr,
        )
        sys.exit(2)
    if broken:
        print(f"BROKEN LINKS ({len(broken)}):")
        for b in sorted(set(broken)):
            print("  " + b)
        sys.exit(1)
    print("no broken links")
    sys.exit(0)


if __name__ == "__main__":
    main()
