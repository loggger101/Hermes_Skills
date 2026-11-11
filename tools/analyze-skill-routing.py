#!/usr/bin/env python3
"""Routing-quality and conformance analysis for this skill corpus.

Round-308, ported from two upstream harnesses in addyosmani/agent-skills (MIT):
`scripts/run-evals.js` (Tier-2 deterministic routing evals) and
`scripts/lib/skill-lint.js` (the lint rules). Upstream ranks a prompt against every
skill DESCRIPTION with TF-IDF cosine similarity, because the description is what a
host injects into the system prompt for activation; two skills whose descriptions
vector-close make that choice ambiguous. It also requires each description to state
WHEN to use the skill, not just what it does.

This repo's gates (audit-skills.py, check-router-coverage.py) verify internal
consistency and lane presence; none of them measures routing separability or the
trigger clause. This tool fills that gap and is read-only: nothing here rewrites a
skill.

Checks reported as INFORMATIONAL (this repo's conventions differ on purpose -- see
skill-library-audits/references/routing-quality-harness.md):
  C3 description carries no positive "use when / use before|after|during" clause
  C4 top-level frontmatter keys outside the Agent Skills spec allowlist
     (name, description, license, compatibility, metadata, allowed-tools)
  C6 SKILL.md over --budget lines (a skill body loads in full on activation)

Checks reported as FINDINGS (fix or exempt deliberately):
  C1 frontmatter `name` != directory name            -> exit 1
  C2 skill dir / supporting .md basename not kebab   -> listed only
  C5 declared-but-empty supporting subdirectory      -> listed only
ROUTING description pairs: cosine >= --warn (default 0.5) listed; >= --error
(default 0.75, upstream's error threshold) also fails the run.

Usage:
    python tools/analyze-skill-routing.py [ROOT] [--probe "a prompt"]
        [--warn F] [--error F] [--budget N] [--json OUT.json] [--quiet]
Exit codes: 0 = no hard finding; 1 = C1 mismatch or a pair >= --error; 2 = bad ROOT.
"""

import argparse
import json
import math
import os
import re
import sys
from collections import Counter

SPEC_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
TRIGGER = re.compile(r"\buse (this )?when\b|\buse (before|after|during)\b", re.I)
NEGATE = re.compile(
    r"\b(?:do not|don't|dont|never) use (?:this )?(?:when|before|after|during)\b", re.I
)

# Directories never scanned: repo docs, exports and caches rather than skills.
SKIP_DIRS = {"profiles-export", "docs", ".git", "__pycache__", "node_modules", "archive"}

STOP = set(
    """a an and any are as at be before by for from in into is it its my need needs of on or our
so that the them this to use want we when with you your help me i""".split()
)

# Upstream's abbreviation map, ported verbatim (run-evals.js TOKEN_ALIASES): fold short
# forms onto the word their inflected cousins already stem to, so 'docs' clusters with
# 'documentation' instead of drifting off as its own term.
TOKEN_ALIASES = {
    "doc": "document",
    "docs": "document",
    "config": "configuration",
    "configs": "configuration",
    "auth": "authenticate",
    "authentication": "authenticate",
    "repo": "repository",
    "repos": "repository",
    "dep": "dependency",
    "deps": "dependency",
}


def tokenize(text):
    raw = re.split(r"[\s-]+", re.sub(r"[^a-z0-9\s-]", " ", text.lower()))
    out = []
    for t in raw:
        if len(t) <= 2 or t in STOP:
            continue
        out.append(stem(TOKEN_ALIASES.get(t, t)))
    return out


def parse_frontmatter(text):
    """Forgiving line parser (no yaml import: repo tooling stays stdlib-only).

    Returns (keys, body). Nested keys collapse onto their parent name; list items
    (`  - value`) become a list under the last top-level key seen.
    """
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw, body = text[3:end], text[end + 4 :]
    keys, cur = {}, None
    for line in raw.split("\n"):
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            k, v = m.group(1), m.group(2).strip().strip('"').strip("'")
            keys[k] = v
            cur = k
        elif re.match(r"^\s+-\s+", line) and cur:
            if not isinstance(keys[cur], list):
                keys[cur] = []
            keys[cur].append(line.strip()[1:].strip())
    return keys, body


def has_positive_trigger(description):
    """Upstream rule: a positive trigger clause must survive negation removal.

    Negated clauses ("Do not use when X") describe exclusions, not triggers. Every
    negated clause is stripped -- stripping only the first lets two negations pass on
    the leftovers. (In JS this needs a separate /g copy of the pattern because a
    global regex carries lastIndex across .test(); irrelevant in Python.)
    """
    if NEGATE.search(description):
        stripped = description
        while NEGATE.search(stripped):
            stripped = NEGATE.sub("", stripped, count=1)
        return bool(TRIGGER.search(stripped))
    return bool(TRIGGER.search(description))


def stem(word):
    """Light suffix folding so 'conflicts'/'conflict' cluster and nominalizations fold
    onto each other ('verification'/'verifications').

    '-ification' is folded to the verb-ish stem first, or 'specification' loses
    '-ication' and collides with 'specific'. Order matters: plural '-ations' must not
    survive as a longer stem than its singular form. Measured here (not upstream's claim):
    this folds nominalisations onto each other but NOT onto the bare verb --
    stem('verification') = stem('verifications') = 'verifi', while stem('verify') stays
    'verify'; the alias map is what bridges abbreviations ('docs' -> 'document'), not
    the stemmer.
    """
    t = word
    if len(t) > 10 and re.search(r"ifications?$", t):
        t = re.sub(r"ications?$", "i", t)
    for suf in ("ally", "ing", "ations", "ation", "ed", "es", "al"):
        if len(t) > len(suf) + 3 and t.endswith(suf):
            t = t[: -len(suf)]
            break
    if len(t) > 3 and t.endswith("s") and not t.endswith("ss"):
        t = t[:-1]
    if len(t) > 4 and t.endswith("e"):
        t = t[:-1]
    return t


def load_skills(root):
    skills = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith("."))
        if "SKILL.md" not in filenames:
            continue
        path = os.path.join(dirpath, "SKILL.md")
        with open(path, encoding="utf-8", errors="ignore") as fh:
            text = fh.read()
        fm, _body = parse_frontmatter(text)
        subdirs = {}
        for d in dirnames:
            full = os.path.join(dirpath, d)
            if not os.path.isdir(full):
                continue
            try:
                entries = [e for e in os.listdir(full) if not e.startswith(".")]
            except OSError:
                entries = ["<unreadable>"]
            subdirs[d] = entries
        skills.append(
            {
                "dir": os.path.basename(dirpath),
                "rel": os.path.relpath(dirpath, root).replace("\\", "/"),
                "fm": fm,
                "keys": list(fm.keys()),
                "description": str(fm.get("description", "")),
                "lines": text.count("\n") + 1,
                "siblings": sorted(f for f in filenames if f != "SKILL.md"),
                "subdirs": subdirs,
            }
        )
    return skills


def tfidf_vectors(docs):
    """docs: {key: Counter(tokens)} -> {key: {term: weight}} (log-idf, L2-normalise later)."""
    n = len(docs) or 1
    df = Counter()
    for counts in docs.values():
        df.update(counts.keys())
    vectors = {}
    for key, counts in docs.items():
        total = sum(counts.values()) or 1
        vectors[key] = {t: (f / total) * math.log(1 + n / (1 + df[t])) for t, f in counts.items()}
    return vectors


def cosine(a, b):
    if len(a) > len(b):
        a, b = b, a
    num = sum(w * b.get(t, 0.0) for t, w in a.items())
    na = math.sqrt(sum(w * w for w in a.values())) or 1e-9
    nb = math.sqrt(sum(w * w for w in b.values())) or 1e-9
    return num / (na * nb)


def analyse(root, warn=0.5, error=0.75, budget=500):
    skills = load_skills(root)
    report = {
        "root": root.replace("\\", "/"),
        "skills_scanned": len(skills),
        "thresholds": {"warn": warn, "error": error, "budget_lines": budget},
        "C1_name_ne_dir": [],
        "C2_non_kebab_names": [],
        "C3_no_trigger_clause": [],
        "C4_non_spec_keys": {},
        "C5_empty_subdirs": [],
        "C6_over_budget": [],
        "routing_pairs": [],
    }
    extra = Counter()
    for s in skills:
        if s["fm"].get("name", "").strip() != s["dir"]:
            report["C1_name_ne_dir"].append({"skill": s["rel"], "name": s["fm"].get("name")})
        if not KEBAB.match(s["dir"]):
            report["C2_non_kebab_names"].append({"skill": s["rel"], "kind": "skill-dir"})
        for f in s["siblings"]:
            if f.endswith(".md") and not KEBAB.match(f[:-3]):
                report["C2_non_kebab_names"].append({"skill": s["rel"], "kind": f})
        if not has_positive_trigger(s["description"]):
            report["C3_no_trigger_clause"].append(s["rel"])
        for k in s["keys"]:
            if k not in SPEC_KEYS:
                extra[k] += 1
        for d, entries in s["subdirs"].items():
            if not entries and d != "tests":
                report["C5_empty_subdirs"].append({"skill": s["rel"], "dir": d})
        if s["lines"] > budget:
            report["C6_over_budget"].append({"skill": s["rel"], "lines": s["lines"]})
    report["C4_non_spec_keys"] = dict(extra.most_common())

    # Corpus doc per skill, faithful to upstream buildCorpus(): name tokens weighted 2x
    # plus description tokens. The doubled name is what keeps two skills with similar
    # prose but different names from reading as duplicates.
    docs = {}
    for s in skills:
        name_tokens = tokenize(s["dir"])
        toks = name_tokens + name_tokens + tokenize(s["description"])
        docs[s["rel"]] = Counter(toks)
    vectors = tfidf_vectors(docs)
    keys = sorted(vectors)
    pairs = []
    for i, ka in enumerate(keys):
        for kb in keys[i + 1 :]:
            c = cosine(vectors[ka], vectors[kb])
            if c >= warn:
                pairs.append({"score": round(c, 4), "a": ka, "b": kb})
    pairs.sort(key=lambda p: -p["score"])
    report["routing_pairs"] = pairs

    hard = list(report["C1_name_ne_dir"]) + [p for p in pairs if p["score"] >= error]
    report["hard_findings"] = len(hard)
    return report, vectors


def rank_prompt(vectors, prompt):
    q = Counter(tokenize(prompt))
    n = len(vectors) or 1
    df = Counter()
    for v in vectors.values():
        df.update(k for k, w in v.items())
    total = sum(q.values()) or 1
    qv = {t: (f / total) * math.log(1 + n / (1 + df[t])) for t, f in q.items()}
    return sorted(((cosine(qv, v), k) for k, v in vectors.items()), reverse=True)[:10]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Routing-quality and conformance analysis")
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument(
        "--probe", action="append", default=[], help="rank skills for a prompt (repeatable)"
    )
    ap.add_argument("--warn", type=float, default=0.5)
    ap.add_argument("--error", type=float, default=0.75)
    ap.add_argument("--budget", type=int, default=500)
    ap.add_argument("--json", dest="json_out")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    report, vectors = analyse(root, args.warn, args.error, args.budget)

    def say(*a):
        if not args.quiet:
            print(*a)

    n = report["skills_scanned"]
    say(f"skills scanned: {n}")
    say(f"C1 name != directory: {len(report['C1_name_ne_dir'])}")
    for item in report["C1_name_ne_dir"]:
        say("   ", item["skill"], "->", repr(item["name"]))
    say(
        f"C2 non-kebab skill dir / supporting .md: {len(report['C2_non_kebab_names'])} (informational)"
    )
    for item in report["C2_non_kebab_names"][:20]:
        say("   ", item["skill"], "|", item["kind"])
    c3 = len(report["C3_no_trigger_clause"])
    pct = 100.0 * c3 / n if n else 0.0
    say(f"C3 descriptions with no positive trigger clause: {c3}/{n} ({pct:.0f}%) (informational)")
    say("C4 non-spec top-level frontmatter keys:", json.dumps(report["C4_non_spec_keys"]))
    say(f"C5 empty supporting subdirs: {len(report['C5_empty_subdirs'])}")
    for item in report["C5_empty_subdirs"][:15]:
        say("   ", item["skill"], "/", item["dir"])
    say(f"C6 SKILL.md over {args.budget} lines: {len(report['C6_over_budget'])} (informational)")
    for item in sorted(report["C6_over_budget"], key=lambda x: -x["lines"])[:15]:
        say("   ", item["skill"], item["lines"], "lines")
    pairs = report["routing_pairs"]
    hard_pairs = [p for p in pairs if p["score"] >= args.error]
    say(f"ROUTING collisions >= {args.warn}: {len(pairs)}   >= {args.error}: {len(hard_pairs)}")
    for p in pairs[:30]:
        mark = "ERROR" if p["score"] >= args.error else "warn "
        say(f"   {mark} {p['score']:.3f}  {p['a']}  <->  {p['b']}")
    for prompt in args.probe:
        say(f"\nPROBE: '{prompt}'")
        for score, key in rank_prompt(vectors, prompt):
            say(f"   {score:.3f}  {key}")

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=1)
    return 1 if report["hard_findings"] else 0


if __name__ == "__main__":
    sys.exit(main())
