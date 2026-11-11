#!/usr/bin/env python3
"""Occasional instrument: is every references/*.md reachable through its OWNING skill?

For each reference file, probe tools/analyze-skill-routing.py with the filename-derived phrase and check
whether the owner skill (<category>/<skill>) lands in that probe's top-5. The harness scores name +
description only - exactly what a host injects for activation - so this finds topics present at reference
layer but absent from the one-line description (r313 fixed gis-spatial-analysis/ArcGIS that way).

READ THE NUMBER HONESTLY: filename phrases are not task phrasings, and out-of-vocabulary probes collapse to a
fixed arbitrary ranking (0.000 blocks), so misses = upper bound on vocabulary mismatch, never a defect count.
Act only on individual rows where a human-plausible SENTENCE probe also fails; mass description rewrites here
would be keyword-stuffing. Interpretation + traps documented in
software-development/skill-library-audits/references/routing-quality-harness.md.

Usage: python tools/sweep-reference-reachability.py [root] [--top N] [--chunk N] [--out FILE]
Exit codes: 0 sweep completed (misses are findings, not failures), 2 bad root / harness missing.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

HARNESS = "tools/analyze-skill-routing.py"
SKIP_DIRS = {".git", "__pycache__", "profiles-export", "memories", "profile"}


def collect_refs(root: str) -> list[tuple[str, str]]:
    """Return (owner-relative skill path, reference relpath) for every refs file."""
    root_norm = os.path.abspath(root).replace("\\", "/")
    depth_prefix = len(root_norm.split("/"))
    out: list[tuple[str, str]] = []
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        rp = os.path.abspath(dirpath).replace("\\", "/")
        parts = rp.split("/")
        if "references" not in parts:
            continue
        i = parts.index("references")
        owner = "/".join(parts[depth_prefix:i])
        if not owner or (len(parts) - depth_prefix) < 2:
            continue  # refs must live under <category>/<skill>/references
        for fn in sorted(files):
            if fn.endswith(".md"):
                rel = "/".join(parts[depth_prefix:]) + "/" + fn
                out.append((owner, rel))
    return out


def rank_for(harness: str, root: str, phrases: list[str]) -> dict[str, list[tuple[float, str]]]:
    """Run the harness once with all probes; parse PROBE blocks from unquiet stdout.

    (--quiet suppresses probe rankings entirely - do not add it back.)
    """
    cmd = [sys.executable, harness] + sum([["--probe", p] for p in phrases], [])
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=root)
    res: dict[str, list[tuple[float, str]]] = {}
    cur: str | None = None
    for line in proc.stdout.splitlines():
        pm = re.match(r"PROBE: '(.*)'", line.strip())
        if pm:
            cur = pm.group(1)
            res[cur] = []
            continue
        m = re.match(r"\s+([0-9.]+)\s+(\S+)", line)
        if m and cur is not None and len(res[cur]) < 6:
            res[cur].append((float(m.group(1)), m.group(2)))
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "root", nargs="?", default=None, help="skills repo root (default: this script's parent)"
    )
    ap.add_argument("--top", type=int, default=5, help="owner must rank within top N (default 5)")
    ap.add_argument("--chunk", type=int, default=40, help="probes per harness process (default 40)")
    ap.add_argument("--out", default=None, help="write miss lines to FILE as well as stdout")
    args = ap.parse_args()

    root = (
        os.path.abspath(args.root)
        if args.root
        else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    harness = os.path.join(root, HARNESS)
    if not os.path.isfile(harness):
        print(f"bad root: no {HARNESS} under {root}")
        return 2

    refs = collect_refs(root)
    lines = [f"refs found: {len(refs)}"]
    misses: list[str] = []
    for i in range(0, len(refs), args.chunk):
        ph2owners: dict[str, list[tuple[str, str]]] = {}
        for owner, rel in refs[i : i + args.chunk]:
            phrase = os.path.basename(rel)[:-3].replace("-", " ")
            ph2owners.setdefault(phrase, []).append((owner, rel))
        ranks = rank_for(harness, root, list(ph2owners))
        for phrase, owners in ph2owners.items():
            names = [n for _, n in ranks.get(phrase, [])]
            for owner, rel in owners:
                if owner not in names[: args.top]:
                    misses.append(f"{rel}   | probe '{phrase}' top{args.top}: {names[:3]}")
    lines.append(
        f"owner-not-in-top{args.top}: {len(misses)}  (upper bound on vocabulary mismatch, NOT defect count)"
    )
    lines.extend("  " + m for m in misses)
    text = "\n".join(lines)
    print(text)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
