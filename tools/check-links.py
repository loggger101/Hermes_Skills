#!/usr/bin/env python3
"""Broken-link checker for this second brain (stdlib only).

Scans every .md file in the repo and verifies that relative markdown links
point at files/directories that exist, and that every #anchor in a link to a
markdown file names a heading (or explicit <a id/name>) that exists in it.
Catches exactly the class of bug where a doc references a file that was never
created or got renamed (e.g. a dangling AGENTS.md pointer), or a section that
was retitled — cheap insurance for a discoverability-focused repo.

Rules:
- Skips external URLs (http/https/mailto), absolute paths, and links inside fenced code
  blocks or inline `code` spans (docs show example syntax like ![alt](url)).
- Skips every file under a <category>/<skill>/templates/ dir: those are scaffolds
  copied-and-filled at use time (e.g. software-development/code-wiki/templates/), so their
  relative links (diagrams/, modules/X.md) and {{TOKEN}} placeholders point at generated
  output by design.
- Anchors: `file.md#section` and same-file `#section` are checked against GitHub's heading
  slugs (lowercase, punctuation dropped, spaces to hyphens, -1/-2 for repeats) plus explicit
  `<a id="...">` / `<a name="...">`. Anchors on non-markdown targets (`script.py#L10`) and
  on directories are out of scope and counted as such. Until round-256 anchors were stripped
  unchecked: a retitled heading broke every link into it without a sound.
- memories/MEMORY.md and memories/USER.md are SKIPPED: one-way exports of the live store (see
  memories/DESCRIPTION.md). Entries quote markdown-shaped fragments as prose, and the repo cannot
  fix a link inside a file the next sync overwrites.
- profiles-export/ is SKIPPED: those are historical per-profile snapshots (see profile/DESCRIPTION.md);
  they may predate later fixes and are regenerated from live environments, not hand-maintained here.

Every skipped category is reported as an honest denominator in the summary line — a binary
"checked N / no broken links" hides how much of the repo's link surface was never actually
verifiable (pattern: repowise's doc-drift analysis, 4 verdicts instead of 2; see
autonomous-ai-agents/repowise/references/codebase-intelligence-patterns.md §11).

LINK_CHECK_ROOT redirects the scan to a fixture tree (used by mutation-test-link-gate.py);
LINK_CHECK_MIN_LINKS sets that fixture's floor and is honoured ONLY together with
LINK_CHECK_ROOT, so the real repo's floor can never be lowered from the environment.

Usage: python tools/check-links.py   # exit 0 = clean, 1 = broken links/anchors, 2 = scan failed
"""

import os
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

_FIXTURE_ROOT = os.environ.get("LINK_CHECK_ROOT")
REPO = Path(_FIXTURE_ROOT).resolve() if _FIXTURE_ROOT else Path(__file__).resolve().parents[1]
# floor: below this the scan failed, whatever it reports
MIN_EXPECTED_LINKS = int(os.environ.get("LINK_CHECK_MIN_LINKS", "200")) if _FIXTURE_ROOT else 200
SKIP_DIRS = {".git"}
SNAPSHOT_PREFIXES = ("profiles-export/", "memories-export/")
# One-way exports of the live Hermes memory store: their entries quote markdown-shaped
# fragments as prose, and the repo cannot fix a link inside a file the next sync overwrites.
# Deliberately file-scoped, not "memories/" -- the hand-written memories/DESCRIPTION.md
# stays gated like any other doc.
EXPORTED_FILES = ("memories/MEMORY.md", "memories/USER.md")
LINK_RE = re.compile(r'\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
FENCE_RE = re.compile(r"```.*?```", re.S)
HEADING_RE = re.compile(r"^#{1,6}[ \t]+(.+?)[ \t]*#*[ \t]*$", re.M)
HTML_ANCHOR_RE = re.compile(r"<a\s+[^>]*?(?:name|id)=[\"']([^\"']+)[\"']", re.I)


def slugify(heading: str) -> str:
    """GitHub's heading slug: drop markup, lowercase, keep word chars/space/-, spaces -> -."""
    h = re.sub(r"`([^`]*)`", r"\1", heading)
    h = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", h)  # [text](url) -> text
    h = re.sub(r"<[^>]+>", "", h)  # inline html
    h = h.strip().lower()
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")


_anchor_cache = {}


def anchors_of(path: Path) -> set:
    """Every anchor a link may target in `path` (heading slugs with GitHub's -N repeats)."""
    if path not in _anchor_cache:
        text = FENCE_RE.sub("", path.read_text(encoding="utf-8"))
        found, seen = set(), {}
        for m in HEADING_RE.finditer(text):
            s = slugify(m.group(1))
            n = seen.get(s, 0)
            found.add(s if n == 0 else f"{s}-{n}")
            seen[s] = n + 1
        found.update(a for a in HTML_ANCHOR_RE.findall(text))
        _anchor_cache[path] = found
    return _anchor_cache[path]


def main():
    broken = []
    unreadable = []  # files the scan could not open: coverage gaps, not warnings
    checked = n_anchors_checked = 0
    # honest denominators (repowise doc-drift pattern): every skipped category counted and
    # reported, so "no broken links" always says how much surface was actually verifiable.
    n_ext_url = n_mailto = n_abs_path = n_code_span = n_anchor_non_md = 0
    n_template_files = n_snapshot_export_files = 0
    for p in REPO.rglob("*.md"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        rel_posix = str(p.relative_to(REPO)).replace("\\", "/")
        if rel_posix.startswith(SNAPSHOT_PREFIXES) or rel_posix in EXPORTED_FILES:
            n_snapshot_export_files += 1
            continue  # historical snapshots / live-memory exports — not hand-maintained (see docstring)
        parts = p.relative_to(REPO).parts
        if "templates" in parts:
            n_template_files += 1
            continue  # skill template scaffolds — links resolve only after generation
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as e:
            unreadable.append(f"{p}: {e}")
            continue
        # strip fenced code blocks so example links in docs don't count,
        # then inline `code` spans (e.g. markdown syntax examples like ![alt](url))
        text_no_code = FENCE_RE.sub("", text)
        n_code_span += len(LINK_RE.findall(text)) - len(LINK_RE.findall(text_no_code))
        text_no_code = re.sub(r"`[^`\n]*`", "", text_no_code)
        for m in LINK_RE.finditer(text_no_code):
            target = m.group(1).strip()
            if not target or target.startswith(("http://", "https://")):
                n_ext_url += 1
                continue
            if target.startswith("mailto:"):
                n_mailto += 1
                continue
            path_part, _, anchor = target.partition("#")
            if path_part.startswith("/"):
                n_abs_path += 1
                continue  # absolute — out of scope for this checker
            if path_part:
                checked += 1
                resolved = (p.parent / path_part).resolve()
                try:
                    ok = resolved.exists()
                except OSError:
                    ok = False
                if not ok:
                    broken.append(f"{rel_posix} -> {target}")
                    continue
            else:
                resolved = p  # same-file anchor
            if not anchor:
                continue
            if resolved.is_dir() or resolved.suffix.lower() != ".md":
                n_anchor_non_md += 1
                continue
            n_anchors_checked += 1
            try:
                known = anchors_of(resolved)
            except (UnicodeDecodeError, OSError) as e:
                unreadable.append(f"{resolved}: {e} (anchor target of {rel_posix})")
                continue
            if anchor.lower() not in known and anchor not in known:
                broken.append(f"{rel_posix} -> {target}  (no heading or anchor '#{anchor}')")

    print(
        f"checked {checked} relative links and {n_anchors_checked} #anchors "
        f"(skipped, by design: {n_ext_url} external URLs, {n_mailto} mailto, "
        f"{n_abs_path} absolute paths, {n_code_span} in code spans/fences, "
        f"{n_anchor_non_md} anchors into non-markdown targets; "
        f"{n_template_files} template + {n_snapshot_export_files} snapshot/export files not scanned)"
    )
    if unreadable:
        print(
            f"[FATAL] {len(unreadable)} file(s) could not be read -- link coverage is "
            "incomplete, so a clean result would be meaningless:",
            file=sys.stderr,
        )
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
