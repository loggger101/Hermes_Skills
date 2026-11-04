#!/usr/bin/env python3
"""Check that backticked in-repo path citations resolve to real files.

Why this exists: tools/check-links.py validates markdown *links* ([text](path)), but
prose frequently cites a file as `category/skill/references/foo.md` inside BACKTICKS.
Those are plain text, so a move or rename silently leaves a citation pointing at
nothing -- and a later session reading it concludes the knowledge is missing (or
re-mines ground already covered). Round-250's move of per-library notes out of
astro-toolkit-selection left 70 such citations behind across four files, none of which
failed any existing gate.

Classification (deliberately conservative):
  FAIL -- the cited path is absent but its filename exists elsewhere in this repo:
          strong evidence of a move/rename whose citation was never updated. Fix it.
  WARN -- no such filename anywhere here. Usually an intentional reference INTO an
          upstream project (`docs/source/user-guide/lazy/using.md` is polars' docs,
          not ours), so it must not block; reported for eyeballing only (--warn-list).

Skipped by design: fenced code blocks (examples), `profiles-export/**` and
`docs/archive/**` (historical audit notes quote paths as-of-writing -- rewriting them
would falsify the record), glob tokens, and any token whose first segment is not a
top-level dir of this repo (those are upstream paths by construction).

Scan-integrity guards (a clean run of nothing must not look like success):
  * unreadable markdown (not valid UTF-8)  -> [FATAL], exit 2;
  * citation count below the floor         -> [FATAL], exit 2.
    Real runs use REAL_FLOOR; CITATION_CHECK_MIN_CITATIONS is honoured only together
    with CITATION_CHECK_ROOT, so a stray env var cannot silently disarm the real gate.

Exit code: 0 clean | 1 stale citations found | 2 fatal (unreadable file / scan floor).
stdlib only. Usage: python tools/check-citations.py [--quiet] [--warn-list]
"""

from __future__ import annotations

import os
import re
import sys

REAL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.environ.get("CITATION_CHECK_ROOT") or REAL_ROOT
IS_FIXTURE = bool(os.environ.get("CITATION_CHECK_ROOT"))
# 780 citations were live when this gate was written; a real run far below that means the
# scan itself broke (regex, walker, or root), not that knowledge disappeared.
REAL_FLOOR = int(os.environ.get("CITATION_CHECK_REAL_FLOOR", "400"))

SKIP_DIRS = {".git", "profiles-export", "node_modules", "__pycache__"}
# historical snapshots quote paths as-of-writing; rewriting them would falsify the record
SKIP_REL_PREFIXES = ("docs/archive/",)
FENCE = re.compile(r"^\s*(```|~~~)")
CITATION = re.compile(r"`([^`\s]+/[^`\s]+\.md)`")


def top_level_dirs() -> set[str]:
    return {
        d
        for d in os.listdir(ROOT)
        if os.path.isdir(os.path.join(ROOT, d)) and d not in SKIP_DIRS and not d.startswith(".")
    }


TOPS = top_level_dirs()


def all_md_paths():
    """Repo-relative markdown paths, skipping excluded dirs and archived notes."""
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if not f.endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(root, f), ROOT).replace("\\", "/")
            if rel.startswith(SKIP_REL_PREFIXES):
                continue
            yield rel


ALLPATHS = set(all_md_paths())

BY_BASE: dict[str, list[str]] = {}
for _rel in ALLPATHS:
    BY_BASE.setdefault(_rel.rsplit("/", 1)[-1], []).append(_rel)

# skill-directory index so cross-skill `.../<skill>/SKILL.md` citations resolve by tail
TAIL2: dict[str, list[str]] = {}
for _rel in ALLPATHS:
    if _rel.endswith("/SKILL.md"):
        TAIL2.setdefault("/".join(_rel.split("/")[-2:]), []).append(_rel)

# reference shorthand index: `references/<name>.md` -> owning skills that carry it
SHORTHAND: dict[str, list[str]] = {}
for _rel in ALLPATHS:
    if "/references/" in _rel:
        SHORTHAND.setdefault("references/" + _rel.split("/references/", 1)[1], []).append(_rel)


def resolve(tok: str):
    """Return (kind, note); kind in {ok, fail, warn}."""
    if tok in ALLPATHS:
        return "ok", "exact"

    if tok.endswith("/SKILL.md"):
        tail = "/".join(tok.split("/")[-2:])
        hits = TAIL2.get(tail, [])
        if len(hits) == 1:
            return "fail", "moved?->" + hits[0]
        if not hits:
            return "warn", "no-such-skill-here(upstream-path?)"
        return "warn", "skill-name-ambiguous(%d)" % len(hits)

    if tok.startswith("references/"):
        hits = SHORTHAND.get(tok, [])
        if len(hits) == 1:
            return "ok", "shorthand->" + hits[0]
        if len(hits) > 1:
            return "ok", "shorthand-ambiguous(%d)" % len(hits)

    base = tok.rsplit("/", 1)[-1]
    hits = BY_BASE.get(base, [])
    if not hits:
        return "warn", "no-such-filename-here(upstream-path?)"
    if len(hits) == 1:
        return "fail", "moved?->" + hits[0]
    tail_cands = [h for h in hits if tok.endswith("/" + "/".join(h.split("/")[-2:]))]
    if len(tail_cands) == 1:
        return "fail", "moved?->" + tail_cands[0]
    return "warn", "basename-elsewhere(%d)-ambiguous" % len(hits)


def read_lines(rel_self: str):
    """Strict UTF-8 read; raise on undecodable bytes so the run fails loud."""
    path = os.path.join(ROOT, rel_self.replace("/", os.sep))
    with open(path, "rb") as fh:
        raw = fh.read()
    return raw.decode("utf-8").splitlines(keepends=True)


def citations_in(rel_self: str):
    """Yield (lineno, token) for backticked in-repo citation candidates."""
    infence = False
    for n, line in enumerate(read_lines(rel_self), 1):
        if FENCE.match(line):
            infence = not infence
            continue
        if infence:
            continue
        for tok in CITATION.findall(line):
            tok = tok.strip().strip("./")
            if "*" in tok or "?" in tok:  # glob examples, not citations
                continue
            if tok.split("/", 1)[0] in TOPS:
                yield n, tok


def main() -> int:
    quiet = "--quiet" in sys.argv
    show_warn = "--warn-list" in sys.argv

    unreadable: list[tuple[str, str]] = []
    fails: list[tuple[str, int, str, str]] = []
    warns: list[tuple[str, int, str, str]] = []
    checked = 0

    for rel_self in sorted(ALLPATHS):
        try:
            found = list(citations_in(rel_self))
        except UnicodeDecodeError as e:
            unreadable.append((rel_self, str(e)))
            continue
        for lineno, tok in found:
            checked += 1
            kind, note = resolve(tok)
            if kind == "fail":
                fails.append((rel_self, lineno, tok, note))
            elif kind == "warn":
                warns.append((rel_self, lineno, tok, note))

    print("checked %d backticked in-repo path citations" % checked)

    fatal: list[str] = []
    if unreadable:
        for rel, err in unreadable[:10]:
            print("  [FATAL] unreadable markdown (not valid UTF-8): %s (%s)" % (rel, err))
        fatal.append("%d unreadable file(s)" % len(unreadable))

    if IS_FIXTURE:
        floor = int(os.environ.get("CITATION_CHECK_MIN_CITATIONS", "1"))
    else:
        floor = REAL_FLOOR
    if checked < floor:
        print(
            "  [FATAL] scan found %d citations, below floor %d -- the scanner or its root is broken"
            % (checked, floor)
        )
        fatal.append("scan below floor")

    print("stale (must fix): %d | informational: %d" % (len(fails), len(warns)))

    if fails and not quiet:
        for rel, lineno, tok, note in fails[:60]:
            print("  FAIL %s:%d  %s   [%s]" % (rel, lineno, tok, note))
        if len(fails) > 60:
            print("  ... %d more stale citations" % (len(fails) - 60))
    if warns and show_warn and not quiet:
        for rel, lineno, tok, note in warns[:25]:
            print("  warn %s:%d  %s   [%s]" % (rel, lineno, tok, note))

    if fatal:
        return 2
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
