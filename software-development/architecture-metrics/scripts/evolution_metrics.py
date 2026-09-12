#!/usr/bin/env python3
"""Git evolution metrics: churn, change coupling, temporal hotspots, code age, bus factor.

Derived from sentrux/sentrux (MIT) metrics/evo — same formulas and skip rules,
stdlib + `git` CLI only (sentrux uses libgit2; the CLI gives identical data).

Skip rules (from source): merge commits double-count changes -> skipped;
mega-commits > 50 files add noise -> skipped; renames are not churn.
Constants: default lookback 90 days, min co-changes for a coupling pair = 3.

Usage: python evolution_metrics.py <repo-dir> [--days N] [--json]
"""
import ast
import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def git(repo: str, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)


def is_merge(repo: str, epoch_s: str) -> bool:
    """True if the commit at this timestamp has >1 parent (sentrux skip rule)."""
    out = git(repo, "rev-list", "--parents", "-n", "1", f"@{epoch_s}").stdout.split()
    return len(out) > 2


def walk_commits(repo: str, days: int):
    """Yield (epoch, author, [(path, added, removed)]) for non-merge commits in window.

    Sequential single pass over `git log --numstat`: each '@' header finalizes the
    previous record (applying sentrux's skip rules) and starts a new one."""
    r = git(repo, "log", f"--since={days} days ago", "--no-renames", "--numstat",
            "--date=format-local:%s", "--pretty=format:@%ad|%an")
    if r.returncode != 0:
        raise SystemExit(f"git log failed (not a git repo?): {r.stderr.strip()}")

    records, cur = [], None

    def finalize():
        nonlocal cur
        if cur is not None and cur["files"] and len(cur["files"]) <= 50 \
                and not cur["is_merge"]:
            # sentrux parity: skip merge commits (double-count changes) and
            # mega-commits >50 files (noise). Renames excluded via --no-renames.
            records.append((cur["epoch"], cur["author"], cur["files"]))
        cur = None

    for line in r.stdout.splitlines():
        if not line.strip():
            continue
        if line.startswith("@"):
            finalize()
            epoch_s, author = line[1:].split("|", 1)
            cur = {"epoch": int(epoch_s), "author": author, "files": [],
                   "is_merge": is_merge(repo, epoch_s)}
        else:
            parts = line.split("\t")
            if len(parts) < 3 or not parts[2]:
                continue  # malformed / no path — skip
            a = int(parts[0]) if parts[0].isdigit() else 0   # binary files show "-" -> zero churn, still touched
            b = int(parts[1]) if parts[1].isdigit() else 0
            cur["files"].append((parts[2], a, b))
    finalize()

    return sorted(records, key=lambda x: -x[0])


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    days = 90
    for i, a in enumerate(sys.argv):
        if a == "--days":
            days = int(sys.argv[i + 1])
    repo = Path(args[0] if args else ".").resolve()

    commits = walk_commits(str(repo), days)
    now = datetime.now(timezone.utc).timestamp()

    # ── churn per file (saturating semantics: plain ints are fine in Python) ──
    churn, last_touched, authors_by_file = {}, {}, defaultdict(lambda: defaultdict(int))
    commit_files = []  # list of frozensets for coupling
    for epoch, author, files in commits:
        touched = set()
        for p, a, r in files:
            c = churn.setdefault(p, {"commits": 0, "added": 0, "removed": 0})
            c["commits"] += 1
            c["added"] += a
            c["removed"] += r
            last_touched[p] = max(last_touched.get(p, 0), epoch)
            authors_by_file[p][author] += 1
            touched.add(p)
        commit_files.append(touched)

    # ── change coupling: Jaccard co-change pairs (sentrux: min count 3) ──
    pair_count = defaultdict(int)
    for i, fa in enumerate(commit_files):
        flist = sorted(fa)
        for j in range(len(flist)):
            for k in range(j + 1, len(flist)):
                pair_count[(flist[j], flist[k])] += 1
    commit_counts = {p: churn[p]["commits"] for p in churn}
    pairs = []
    for (a, b), n in pair_count.items():
        if n < 3:
            continue
        union = commit_counts[a] + commit_counts[b] - n
        strength = n / union if union else 0.0
        pairs.append({"file_a": a, "file_b": b, "co_changes": n,
                      "coupling_strength": round(strength, 4)})
    pairs.sort(key=lambda x: (-x["coupling_strength"], x["file_a"], x["file_b"]))

    # ── temporal hotspots: churn_count × max_complexity (Nagappan & Ball) ──
    def file_max_cc(path):
        try:
            src = (repo / path).read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(src)
        except (OSError, SyntaxError, ValueError):
            return 0
        mx = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                cc = 1
                for sub in ast.walk(node):
                    if isinstance(sub, (ast.If, ast.For, ast.While, ast.AsyncFor,
                                        ast.ExceptHandler, ast.Assert, ast.comprehension)):
                        cc += 1
                    elif isinstance(sub, ast.BoolOp):
                        cc += len(sub.values) - 1
                mx = max(mx, cc)
        return mx

    hotspots = []
    for p in sorted(churn):
        if not p.endswith(".py"):
            continue
        cc = file_max_cc(p)
        risk = churn[p]["commits"] * cc
        if cc:
            hotspots.append({"file": p, "churn_commits": churn[p]["commits"],
                             "max_complexity": cc, "risk_score": risk})
    hotspots.sort(key=lambda x: -x["risk_score"])

    # ── code age + bus factor (Ricca et al.) ──
    code_age = {p: int((now - t) // 86400) for p, t in last_touched.items()}
    single_author = sum(1 for p in churn if len(authors_by_file[p]) == 1)
    total_files = len(churn) or 1
    single_ratio = single_author / total_files

    # ── scores (sentrux formulas, verbatim semantics) ──
    bus_factor_score = max(0.0, min(1.0, 1.0 - single_ratio))
    churn_vals = sorted((c["added"] + c["removed"] for c in churn.values()), reverse=True)
    total_churn = sum(churn_vals) or 1
    top_n = max(len(churn_vals) // 10, 1)
    concentration = sum(churn_vals[:top_n]) / total_churn
    churn_score = max(0.0, min(1.0, 1.0 - concentration))

    result = {
        "repo": str(repo), "lookback_days": days, "commits_analyzed": len(commits),
        "files_touched": len(churn),
        "top_churn": sorted(({"file": p, **c} for p, c in churn.items()),
                            key=lambda x: -(x["added"] + x["removed"]))[:15],
        "coupling_pairs_top": pairs[:15],
        "temporal_hotspots_top": hotspots[:10],
        "oldest_files": sorted(({"file": p, "age_days": d} for p, d in code_age.items()),
                               key=lambda x: -x["age_days"])[:10],
        "bus_factor": {"single_author_files": single_author,
                       "single_author_ratio": round(single_ratio, 4),
                       "score": round(bus_factor_score, 4)},
        "churn_concentration_score": round(churn_score, 4),
        "evolution_score": round(min(bus_factor_score, churn_score), 4),
    }

    if as_json:
        print(json.dumps(result, indent=2))
    else:
        r = result
        def short(p):  # last two path components — basenames collide across skills/
            parts = p.replace("\\", "/").split("/")
            return "/".join(parts[-2:]) if len(parts) > 1 else p
        print(f"Evolution report — {r['repo']} (last {days} days)")
        print(f"  commits={r['commits_analyzed']} files_touched={r['files_touched']} "
              f"evolution_score={r['evolution_score']}")
        tc = ", ".join(f"{short(t['file'])}(+{t['added']}/-{t['removed']}x{t['commits']})"
                       for t in r["top_churn"][:5])
        print(f"  top churn: {tc or '(none)'}")
        cp = ", ".join(f"{short(p['file_a'])}<->{short(p['file_b'])}"
                       f"(n={p['co_changes']},J={p['coupling_strength']})" for p in r["coupling_pairs_top"][:5])
        print(f"  co-change pairs: {cp or '(none)'}")
        th = ", ".join(f"{short(h['file'])}(c{h['churn_commits']}xCC{h['max_complexity']})"
                       for h in r["temporal_hotspots_top"][:5])
        print(f"  temporal hotspots: {th or '(none)'}")
        b = r["bus_factor"]
        print(f"  bus factor: {b['single_author_files']} single-author files "
              f"(ratio {b['single_author_ratio']}) score={b['score']} | churn concentration={r['churn_concentration_score']}")


if __name__ == "__main__":
    main()
