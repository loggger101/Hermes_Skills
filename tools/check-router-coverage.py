#!/usr/bin/env python3
"""Gate: the skill-flow-router must keep pace with the catalog it claims to map.

Round-43. Every other gate in this repo checks *internal consistency* -- counts
agree with counts, links resolve, indexes match disk. Nothing checked whether the
one file whose whole job is routing ("which skill fits this situation?") still
knows about the skills that have been added since it was written.

It didn't. The router was last touched at 4fe8077 (2026-09-06, 166 skills on disk);
47 skills were added afterwards and it was updated for none of them, while all 15
gates stayed green. That is a false-green in the sense failure-signal-audit means
it: a PASS with no observed check behind the claim.

The contract this gate enforces
-------------------------------
A skill is *in router scope* when its frontmatter tags intersect SCOPE_TAGS --
the router's own stated remit ("planning/spec/debugging/review skills"). Every
in-scope skill must EITHER be referenced in a routing lane, OR be named in the
router's '## Deliberately not routed here' block with a reason. A new skill in
that tag set can therefore never go silently unrouted: it fails here until a
human makes a conscious call, which is the same shape as every other gate.

Checks (each failure is reported; exit 1 if any):
  A  in-scope skill neither routed nor declared out-of-scope
  B  out-of-scope entry naming a skill that does not exist (phantom)
  C  out-of-scope entry with no reason after the em dash
  D  skill both routed AND declared out-of-scope (contradiction)
  E  a hardcoded catalog-size claim in the router ('160+ skills' rotted once already)

Usage:
    py tools/check-router-coverage.py
    ROUTER_SCAN_ROOT=/tmp/fixture py tools/check-router-coverage.py   # mutation self-test

Exit 0 = router coverage is honest. Exit 1 = at least one violation.
"""
import os
import re
import sys
from pathlib import Path

if sys.version_info < (3, 8):
    raise SystemExit("[FATAL] check-router-coverage.py needs Python 3.8+")
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

REPO = Path(os.environ.get("ROUTER_SCAN_ROOT")
            or Path(__file__).resolve().parents[1])
ROUTER = REPO / "software-development" / "skill-flow-router" / "SKILL.md"

# The router's declared remit, as tags. Kept deliberately narrow: widening this
# set is a decision about what the router is FOR, not a maintenance chore.
SCOPE_TAGS = {"planning", "debugging", "code-review", "verification"}

OPTOUT_HEADING = "## Deliberately not routed here"
SKIP_PARTS = {".git", ".hermes", "profiles-export", "memories", "memories-export"}
# '- `name` -- reason' (em dash, en dash or '--'); reason must be non-empty.
OPTOUT_RE = re.compile(r"^-\s+`([a-z0-9][a-z0-9-]+)`\s*(?:—|–|--)?\s*(.*)$")


def catalog(repo):
    """{skill-name: tagset} for every real skill (same scope as gen-skills-index.py)."""
    out = {}
    for p in repo.rglob("SKILL.md"):
        if any(part in SKIP_PARTS for part in p.relative_to(repo).parts):
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        fm = text.split("---")[1] if text.startswith("---") else ""
        m = re.search(r"tags: \[(.*?)\]", fm, re.S)
        tags = {t.strip() for t in m.group(1).split(",")} if m else set()
        out[p.parent.name] = tags
    return out


def parse_router(text):
    """-> (lane_refs, optout {name: reason}). The opt-out block is excluded from lanes."""
    head, sep, tail = text.partition(OPTOUT_HEADING)
    optout = {}
    lane_text = head
    if sep:
        # the block runs until the next '## ' heading
        block, nxt, rest = tail.partition("\n## ")
        for line in block.splitlines():
            m = OPTOUT_RE.match(line.strip())
            if m:
                optout[m.group(1)] = m.group(2).strip()
        lane_text += ("\n## " + rest) if nxt else ""
    return set(re.findall(r"`([a-z0-9][a-z0-9-]{3,})`", lane_text)), optout


def main():
    if not ROUTER.exists():
        print(f"[FATAL] router not found at {ROUTER}")
        return 1
    text = ROUTER.read_text(encoding="utf-8", errors="replace")
    skills = catalog(REPO)
    lanes, optout = parse_router(text)
    problems = []

    in_scope = {n for n, tags in skills.items()
                if tags & SCOPE_TAGS and n != "skill-flow-router"}

    # A) coverage
    for name in sorted(in_scope - lanes - set(optout)):
        why = ",".join(sorted(skills[name] & SCOPE_TAGS))
        problems.append(f"[A] `{name}` (tags: {why}) is in router scope but is neither "
                        f"routed in a lane nor listed under '{OPTOUT_HEADING}'")

    # B/C/D) the opt-out block must stay honest
    for name, reason in sorted(optout.items()):
        if name not in skills:
            problems.append(f"[B] out-of-scope list names `{name}`, which is not a skill "
                            f"in this repo (renamed or deleted?)")
        if not reason:
            problems.append(f"[C] out-of-scope entry `{name}` gives no reason — every "
                            f"opt-out must say why routing it would add no information")
        if name in lanes:
            problems.append(f"[D] `{name}` is both routed in a lane and declared "
                            f"out-of-scope — pick one")

    # E) no hardcoded catalog size (this exact claim rotted from 166 -> 210 unnoticed)
    body = text.split("---", 2)[2] if text.startswith("---") else text
    for m in re.finditer(r"\b(\d{2,4})\+?\s+skills\b", body):
        problems.append(f"[E] router hardcodes a catalog size ({m.group(0).strip()!r}); "
                        f"point at SKILLS-INDEX.md instead — this number rots silently")

    if problems:
        print(f"[FAIL] router coverage: {len(problems)} problem(s)")
        for p in problems:
            print("  " + p)
        return 1
    print(f"[OK] router coverage: {len(in_scope)} in-scope skills — "
          f"{len(in_scope & lanes)} routed, {len(optout)} declared out-of-scope, 0 unrouted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
