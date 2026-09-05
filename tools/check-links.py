#!/usr/bin/env python3
"""Broken-link checker for this second brain (stdlib only).

Scans every .md file in the repo and verifies that relative markdown links
point at files/directories that exist. Catches exactly the class of bug where a
doc references a file that was never created or got renamed (e.g. a dangling
AGENTS.md pointer) — cheap insurance for a discoverability-focused repo.

Rules:
- Skips external URLs (http/https/mailto), pure anchors (#...), absolute paths, and links inside
  fenced code blocks or inline `code` spans (docs show example syntax like ![alt](url)).
- Strips #anchors before checking existence.
- profiles-export/ is SKIPPED: those are historical per-profile snapshots (see profile/DESCRIPTION.md);
  they may predate later fixes and are regenerated from live environments, not hand-maintained here.

Usage: python tools/check-links.py          # exit 0 = no broken links, 1 = found some
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git"}
SNAPSHOT_PREFIXES = ("profiles-export/", "memories-export/")
LINK_RE = re.compile(r'\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)')


def main():
    broken = []
    checked = 0
    for p in REPO.rglob("*.md"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        rel_posix = str(p.relative_to(REPO)).replace("\\", "/")
        if rel_posix.startswith(SNAPSHOT_PREFIXES):
            continue  # historical snapshots — not hand-maintained (see module docstring)
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as e:
            print(f"WARNING — could not read {p}: {e}", file=sys.stderr)
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
    if broken:
        print(f"BROKEN LINKS ({len(broken)}):")
        for b in sorted(set(broken)):
            print("  " + b)
        sys.exit(1)
    print("no broken links")
    sys.exit(0)


if __name__ == "__main__":
    main()
