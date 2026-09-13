#!/usr/bin/env python3
"""Regenerate the Claude Code plugin manifests from live skill frontmatter.

This repo is laid out for Hermes (`<category>/<skill>/SKILL.md`). Claude Code's
skill loader only auto-discovers skills one level under a plugin's `skills/`
directory -- it does NOT walk category folders, so pointing it at the repo root
finds exactly zero skills. Verified against Claude Code 2.1.270:

    skills/<category>/<skill>/SKILL.md   ->  Skills (0)
    skills/<skill>/SKILL.md              ->  Skills (2)

The fix is the explicit `skills` array in `.claude-plugin/plugin.json`, which
accepts arbitrary nested paths. That lets the repo keep its Hermes-native shape
and be a valid Claude Code plugin at the same time, with no duplicated files and
no per-skill symlinks. This tool writes that array.

It also writes `.claude-plugin/marketplace.json` so the repo can be installed on
any machine with:

    claude plugin marketplace add loggger101/Hermes_Skills
    claude plugin install hermes@hermes-skills

Usage:
    py tools/gen-claude-plugin.py            # write the manifests
    py tools/gen-claude-plugin.py --check    # fail on drift, write nothing (CI)

Stdlib only -- name/description come out of the frontmatter with the same regex
approach as gen-skills-index.py; audit-skills.py owns the strict validation.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _index_output import emit, wants_check

# ── Environment guard ───────────────────────────────────────────────────────
# Same guard as the other generators: a wrong interpreter must fail HERE, not
# half-run and report clean. On Windows bare `python` is often a Store stub.
if sys.version_info < (3, 8):
    raise SystemExit(
        "[FATAL] this tool needs Python 3.8+, got "
        f"{sys.version.split()[0]} at {sys.executable or '<unknown interpreter>'}"
    )
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / ".claude-plugin"

SKIP_PARTS = (".git/", ".hermes/", "profiles-export/", "memories-export/", "memories/")

# These three are Nous Research ports of capabilities Claude Code already ships
# as first-party skills (anthropic-skills:docx / :pdf / :xlsx, which carry much
# longer trigger descriptions). Exposing both puts two near-identical entries in
# front of the model for the same request, which degrades skill selection for no
# added capability. They stay in the repo for Hermes; they stay out of the plugin.
SKIP_NAMES = {"docx", "pdf", "xlsx"}

PLUGIN_NAME = "hermes"
MARKETPLACE_NAME = "hermes-skills"
PLUGIN_VERSION = "1.0.0"
OWNER = "loggger101"

NAME_RE = re.compile(r"^name:\s*[\"']?([^\"'\n]+)", re.M)


def collect():
    """Return (sorted skill dir paths relative to REPO, list of skipped names)."""
    paths, skipped = [], []
    for p in REPO.rglob("SKILL.md"):
        rel = p.relative_to(REPO).as_posix()
        if any(s in rel for s in SKIP_PARTS):
            continue
        m = NAME_RE.search(p.read_text(encoding="utf-8", errors="replace"))
        name = m.group(1).strip() if m else p.parent.name
        if name in SKIP_NAMES:
            skipped.append(name)
            continue
        paths.append("./" + p.parent.relative_to(REPO).as_posix())
    return sorted(paths), sorted(skipped)


def render_plugin(paths):
    return json.dumps(
        {
            "name": PLUGIN_NAME,
            "version": PLUGIN_VERSION,
            "description": (
                f"Hermes second brain: {len(paths)} skills across "
                f"{len({p.split('/')[1] for p in paths})} categories."
            ),
            "author": {"name": "Hermes Agent", "url": f"https://github.com/{OWNER}"},
            "homepage": f"https://github.com/{OWNER}/Hermes_Skills",
            "license": "MIT",
            "skills": paths,
        },
        indent=2,
        ensure_ascii=False,
    ) + "\n"


def render_marketplace(paths):
    return json.dumps(
        {
            "name": MARKETPLACE_NAME,
            "owner": {"name": OWNER, "url": f"https://github.com/{OWNER}"},
            "metadata": {
                "description": "Hermes Agent skills, installable into Claude Code.",
                "version": PLUGIN_VERSION,
            },
            "plugins": [
                {
                    "name": PLUGIN_NAME,
                    "source": "./",
                    "description": (
                        f"Hermes second brain: {len(paths)} skills across "
                        f"{len({p.split('/')[1] for p in paths})} categories."
                    ),
                    "version": PLUGIN_VERSION,
                    "license": "MIT",
                }
            ],
        },
        indent=2,
        ensure_ascii=False,
    ) + "\n"


def main():
    check = wants_check()
    paths, skipped = collect()
    OUT_DIR.mkdir(exist_ok=True)

    # Floor is well under the real count (202 on disk at time of writing) but far
    # above anything a broken scan would produce -- see _index_output.emit.
    emit(OUT_DIR / "plugin.json", render_plugin(paths),
         count=len(paths), floor=150, label="claude plugin manifest", check=check)
    emit(OUT_DIR / "marketplace.json", render_marketplace(paths),
         count=len(paths), floor=150, label="claude marketplace manifest", check=check)

    if not check:
        print(f"[OK] .claude-plugin/plugin.json -- {len(paths)} skills exposed")
        if skipped:
            print(f"     skipped (duplicates Claude built-ins): {', '.join(skipped)}")


if __name__ == "__main__":
    main()
