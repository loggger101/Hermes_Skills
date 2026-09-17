#!/usr/bin/env python3
"""Run every health gate in this repo and report one verdict.

The repo had several checks but no single command that ran them all, and nothing
at all that noticed when a generated index fell behind the files it describes --
which is how "166 skills" survived in README/DESCRIPTION while 167 were on disk.

Gates, in order (each must pass):

  1. audit-skills.py        frontmatter, descriptions, related_skills, body sections
  2. check-links.py         every relative markdown link resolves
  3. index drift            SKILLS/CODE/REFERENCES/DEPENDENCY and the Claude Code
                            plugin manifests match what is on disk
  4. cron validators        job configs are structurally valid, skill refs resolve
  5. doc counts             hand-written counts in README/DESCRIPTION match reality
  6. self-test harnesses    every registered *_verify.py executes (run-self-tests.py)
  7. gate self-tests        the doc-count and secret gates prove they fail loudly

Usage:
    py tools/verify-all.py            # Windows -- `python` is a Store alias stub
    python3 tools/verify-all.py       # Linux/macOS

Exit 0 = every gate passed. Exit 1 = at least one failed (details above the summary).
Child tools are launched with sys.executable, never a which() lookup.
"""
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

if sys.version_info < (3, 8):
    raise SystemExit(
        "[FATAL] verify-all.py needs Python 3.8+, got "
        + sys.version.split()[0] + " at " + (sys.executable or "<unknown interpreter>")
    )
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

REPO = Path(__file__).resolve().parents[1]
PY = sys.executable or "python3"


def run(label, args, cwd=REPO):
    """Run a child tool; return (label, ok, first meaningful output line)."""
    try:
        proc = subprocess.run([PY] + args, cwd=str(cwd), capture_output=True,
                              text=True, timeout=300)
    except Exception as e:
        return label, False, str(e)[:200]
    out = (proc.stdout or "") + (proc.stderr or "")
    tail = [ln for ln in out.splitlines() if ln.strip()]
    note = ""
    for ln in tail:
        if any(k in ln for k in ("FATAL", "DRIFT", "BROKEN", "ERROR", "Errors:")):
            note = ln.strip()
            break
    if not note and tail:
        note = tail[-1].strip()
    return label, proc.returncode == 0, note[:160]


def run_audit_gate():
    """audit-skills.py emits a JSON report; summarise it rather than echoing its last brace."""
    label = "audit-skills"
    try:
        proc = subprocess.run([PY, "tools/audit-skills.py"], cwd=str(REPO),
                              capture_output=True, text=True, timeout=300)
    except Exception as e:
        return label, False, str(e)[:200]
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        first = (proc.stdout + proc.stderr).strip().splitlines()
        return label, False, (first[0] if first else "no output")[:160]
    note = f"{data['skill_count']} skills, breached={data['threshold_breached']}"
    if data.get("breaches"):
        note += " | " + "; ".join(data["breaches"])
    return label, proc.returncode == 0 and not data["threshold_breached"], note[:160]


def check_doc_counts():
    """Hand-written counts in README/DESCRIPTION must match the machine-generated truths.

    Covers every claim class found to rot by hand (round-20 audit):
      * skill totals — bold `**NNN ...skills` and prose 'all NNN skills' -> live SKILL.md count
        (same scope as gen-skills-index.py: profiles-export is a historical snapshot, not catalog)
      * cross-reference counts in any form ('514 cross-references', '`related_skills` xrefs')
        -> DEPENDENCY.md's Network stats line (the drift gate keeps that file fresh; this checks prose)
      * Claude-plugin exposure claims ('NNN skills load' / 'NNN exposed')
        -> .claude-plugin/plugin.json `skills` array length
      * reference-docs counts ('all NNN reference docs')
        -> REFERENCES-INDEX.md header count (same source its drift gate checks)
      * per-category rows of the README summary table ('| [cat/](./cat/) | ... | NN |')
        -> live SKILL.md count in that category dir
      * pytest suite counts — README's 'NNN suites currently: a N / b M / ...' line
        (round-33 audit found all seven hand-written numbers correct but guarded by
        nothing; the same rot class as every other claim here) -> live discovery via
        run-skill-tests.discover_suites() imported for real (single source of truth, so
        CI's suite set and this gate can never disagree), counting `def test_*` per suite.
        Known limitation: parametrize-expanded cases are not counted — if a suite ever
        gains them the numbers drift and this fails loudly, which is exactly when a human
        must update both README and (if desired) this counter.
      """
    skills = [p for p in REPO.rglob("SKILL.md")
              if not any(part in (".git", ".hermes", "profiles-export", "memories",
                                  "memories-export") for part in p.relative_to(REPO).parts)]
    live = len(skills)

    # truths from the machine-generated files (each already drift-gated upstream of here)
    xrefs, exposed, refdocs = None, None, None
    dep = REPO / "DEPENDENCY.md"
    if dep.exists():
        m = re.search(r"\*\*Network stats:\*\* (\d+) `related_skills` cross-references",
                      dep.read_text(encoding="utf-8"))
        xrefs = int(m.group(1)) if m else None
    plugin_json = REPO / ".claude-plugin" / "plugin.json"
    if plugin_json.exists():
        try:
            exposed = len(json.loads(plugin_json.read_text(encoding="utf-8")).get("skills", []))
        except (json.JSONDecodeError, OSError):
            pass
    refs_index = REPO / "REFERENCES-INDEX.md"
    if refs_index.exists():
        m = re.search(r"\*\*(\d+) reference documents?\*\*",
                      refs_index.read_text(encoding="utf-8"))
        refdocs = int(m.group(1)) if m else None

    # 6) pytest suite counts — truth = live discovery (imported, not reimplemented).
    #    run-skill-tests.py is loaded from the CURRENT REPO global so the mutation
    #    self-test's fixture tree works; counting `def test_*` per suite matches how
    #    a human reads "comfyui 117 / docx 29". Parametrize-expanded cases are NOT
    #    counted (documented limitation in the module docstring) — if a suite gains
    #    them, this fails loudly and forces a conscious README update.
    suites_truth = None
    try:
        spec = importlib.util.spec_from_file_location(
            "run_skill_tests", REPO / "tools" / "run-skill-tests.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        counts = {}
        for label, tests_dir in mod.discover_suites(REPO):
            n = 0
            for tf in sorted(tests_dir.rglob("*.py")):
                txt = tf.read_text(encoding="utf-8", errors="replace")
                n += len(re.findall(r"^\s*def (test_\w+)", txt, re.M))
            counts[label] = n
        suites_truth = counts if counts else None
    except Exception:  # discovery is a convenience truth; absence -> skip the class
        pass

    problems = []
    for name in ("README.md", "DESCRIPTION.md"):
        text = (REPO / name).read_text(encoding="utf-8")

        def check(pattern, truth, label):
            if truth is None:
                return  # source file missing — its own drift gate already failed or will
            for m in re.finditer(pattern, text):
                val = int(m.group(1))
                if val != truth:
                    problems.append(f"{name}: claims {val} {label}, "
                                    f"truth is {truth}")

        # 1) skill totals (bold + prose forms; both rotted in the wild).
        #    The bold pattern covers every form actually used across README/DESCRIPTION —
        #    **NNN Hermes Agent skills**, **Total: NNN skills ...**, and
        #    **NNN verified, audit-passing skills** — not just a bare `**NNN skills`
        #    (the old narrow pattern matched none of them; round-33 caught that via the
        #    mutation self-test's now-independent application).
        check(r"\*\*(?:Total: )?(\d{2,4})\s+(?:Hermes Agent |verified, audit-passing )?skills\b",
              live, "bold skill total")
        check(r"\ball (\d{2,4}) skills\b", live, "skills ('all NNN skills')")

        # 2) cross-reference counts — any prose form; truth = DEPENDENCY.md Network stats.
        check(r"\b(\d{2,4}) `related_skills` xrefs?\b", xrefs, "`related_skills` xrefs")
        # 'NNN (cross-)references' only when the sentence is about skills ("...across NNN skills"),
        # so unrelated uses of the word are never treated as an xref claim.
        check(r"\b(\d{2,4}) (?:cross-)?references\b(?=.{0,30}?across \d+ skills)", xrefs, "xref claims")

        # 3) Claude-plugin exposure — truth = plugin.json `skills` array length.
        #    Deliberately NOT 'NNN skills' bare: that is the catalog total, a different metric.
        check(r"\b(\d{2,4}) skills load\b", exposed, "plugin-exposed skills ('load')")
        check(r"\b(\d{2,4})(?:\s+skills)? exposed\b", exposed, "plugin-exposed skills")

        # 4) reference-docs counts — truth = REFERENCES-INDEX.md header (drift-gated).
        check(r"all (\d{2,4}) reference docs?\b", refdocs, "reference docs")

    # 5) README summary-table category rows: '| [cat/](./cat/) | ... | NN |'
    readme = REPO / "README.md"
    if readme.exists():
        for m in re.finditer(r"\|\s*\[([a-z0-9_-]+)/\]\(\./[a-z0-9_-]+/\)\s*\|[^\n|]*\|\s*(\d+)\s*\|",
                             readme.read_text(encoding="utf-8")):
            cat, claimed = m.group(1), int(m.group(2))
            # count by TOP-LEVEL dir (nested skills like mlops/inference/x belong to mlops)
            actual = sum(1 for p in skills if p.relative_to(REPO).parts[0] == cat)
            # a category may legitimately hold 0 SKILL.md (stub dir); only flag real drift
            if actual and claimed != actual:
                problems.append(f"README table: {cat}/ claims {claimed} skills, "
                                f"disk has {actual}")

    # 6) pytest suite counts — README's 'Seven suites currently: comfyui 117 / ...' line.
    #    Parsed from the segment between 'suites currently:' and the first '(' so the
    #    trailing '(counted YYYY-MM-DD; ...)' annotation can never be mistaken for a pair.
    if readme.exists() and suites_truth:
        text = readme.read_text(encoding="utf-8")
        m = re.search(r"\b(\w+) suites currently:\s*([^()\n]+)", text)
        listed = {}
        if not m:
            problems.append("README: 'NNN suites currently:' list missing while "
                            f"{len(suites_truth)} pytest suite(s) are on disk")
        else:
            # the count-word itself is a claim too ('Seven' must stay in sync with
            # both the listed pairs and discovery — round-33 found all three correct,
            # but none of them was guarded before this gate existed).
            word_to_n = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5,
                         "Six": 6, "Seven": 7, "Eight": 8, "Nine": 9, "Ten": 10}
            if m.group(1) not in word_to_n:
                problems.append(f"README suite list: count-word {m.group(1)!r} is not a "
                                f"recognized number (wording drifted from the gate's anchor)")
            elif word_to_n[m.group(1)] != len(suites_truth):
                problems.append(f"README suite list says '{m.group(1)} suites' but disk has "
                                f"{len(suites_truth)}")

            for tok in m.group(2).split("/"):
                pm = re.fullmatch(r"\s*(\S+)\s+(\d+)\s*", tok)
                if not pm:
                    problems.append(f"README suite list: unparseable token {tok!r}")
                    continue
                listed[pm.group(1)] = int(pm.group(2))

            # truth keyed by skill dir name (discovery labels are <cat>/<skill>/tests)
            truth_by_skill = {}
            for label, n in suites_truth.items():
                parts = Path(label).parts
                if len(parts) >= 3:
                    truth_by_skill[parts[-2]] = (label, n)

            for name, claimed in listed.items():
                t = truth_by_skill.get(name)
                if t is None:
                    problems.append(f"README suite list names '{name}' but no such "
                                    f"pytest suite exists on disk")
                elif claimed != t[1]:
                    problems.append(f"README suite list: {name} claims {claimed} tests, "
                                    f"disk has {t[1]} ({t[0]})")
            for name in truth_by_skill:
                if name not in listed:
                    label, n = truth_by_skill[name]
                    problems.append(f"README suite list omits live suite {label} "
                                    f"({n} tests)")

    return ("doc counts", not problems, "; ".join(problems)[:160] or f"{live} skills, counts agree")


def main():
    results = [
        run_audit_gate(),
        run("check-links", ["tools/check-links.py"]),
        run("drift: SKILLS-INDEX", ["tools/gen-skills-index.py", "--check"]),
        run("drift: CODE-INDEX", ["tools/gen-code-index.py", "--check"]),
        run("drift: REFERENCES-INDEX", ["tools/gen-references-index.py", "--check"]),
        run("drift: DEPENDENCY", ["tools/regen-dependency-map.py", "--check"]),
        run("drift: .claude-plugin", ["tools/gen-claude-plugin.py", "--check"]),
        run("cron: configs", [".hermes/cron/validate-cronjobs.py"]),
        run("cron: skill refs", [".hermes/cron/validate-skill-refs.py"]),
        check_doc_counts(),
        # The repo's other fail-loud mechanism: standalone *_verify.py harnesses that
        # re-execute documented behavior (polars/duckdb/pyomo/cap-grid/ssrf/algorithms).
        # Missing optional deps classify as SKIP; a real regression fails the gate.
        run("self-test harnesses", ["tools/run-self-tests.py"]),
        # The doc-count gate tests itself: mutates each claim class in a temp copy and
        # asserts the gate fails loudly. Keeps an untested claim class from ever shipping.
        run("gate self-test", ["tools/mutation-test-doc-gate.py"]),
        # The secret scan (audit check 7) tests itself: plants one fake credential per
        # pattern class plus env/placeholder negative controls in a temp fixture and
        # asserts every positive is caught with zero false positives.
        run("secret gate self-test", ["tools/mutation-test-secret-gate.py"]),
        # The harness runner (gate 6) tests itself: proves PASS/SKIP-rc77/SKIP-dep/FAIL
        # classification and manifest-drift detection on throwaway temp fixtures.
        run("harness gate self-test", ["tools/mutation-test-selftest-gate.py"]),
    ]

    width = max(len(r[0]) for r in results)
    print("\n=== verify-all ===")
    for label, ok, note in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {label.ljust(width)}  {note}")

    failed = [r[0] for r in results if not r[1]]
    print()
    if failed:
        print(f"FAILED ({len(failed)}/{len(results)}): {', '.join(failed)}")
        return 1
    print(f"ALL {len(results)} GATES PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
