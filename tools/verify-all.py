#!/usr/bin/env python3
"""Run every health gate in this repo and report one verdict.

The repo had several checks but no single command that ran them all, and nothing
at all that noticed when a generated index fell behind the files it describes --
which is how "166 skills" survived in README/DESCRIPTION while 167 were on disk.

Gates, in order (each must pass):

  1. audit-skills.py        frontmatter, descriptions, related_skills, body sections
  2. check-links.py         every relative markdown link resolves
  3. index drift            SKILLS/CODE/REFERENCES/DEPENDENCY and the Claude Code
                            plugin manifests, and the installed-plugins reference
                            match what is on disk / live environment
  4. cron validators        job configs are structurally valid, skill refs resolve
  5. doc counts             hand-written counts in README/DESCRIPTION match reality
  6. self-test harnesses    every registered *_verify.py executes (run-self-tests.py)
  7. router coverage        skill-flow-router routes (or explicitly declines) every
                            skill in its declared scope -- no silent unrouted skills
  8. skill pointers         every skill_view / hermes skill load / skill_manage install
                            pointer written in prose names a skill that exists
  9. gate self-tests        the doc-count, secret, harness, cron, router and pointer
                            gates all prove they fail loudly via mutation fixtures

Usage:
    py tools/verify-all.py            # Windows -- `python` is a Store alias stub
    python3 tools/verify-all.py       # Linux/macOS

Exit 0 = every gate passed. Exit 1 = at least one failed (details above the summary).
Child tools are launched with sys.executable, never a which() lookup.
"""

import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

if sys.version_info < (3, 8):
    raise SystemExit(
        "[FATAL] verify-all.py needs Python 3.8+, got "
        + sys.version.split()[0]
        + " at "
        + (sys.executable or "<unknown interpreter>")
    )
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

REPO = Path(__file__).resolve().parents[1]
PY = sys.executable or "python3"
# Children print UTF-8 (most reconfigure stdout; this env makes the rest agree), so decode it
# as UTF-8 — the Windows default codepage turned every '—' in the table into 'â€”'.
CHILD_IO = dict(encoding="utf-8", errors="replace", env=dict(os.environ, PYTHONIOENCODING="utf-8"))

# Single source of truth for "how many gates verify-all runs". main() builds its result list
# from this, and the doc-count gate checks every 'NNN gates' prose claim against it — so a new
# gate added to one place but not the other (or vice versa) fails loudly instead of rotting.
GATE_LABELS = [
    "audit-skills",  # incl. zero-threshold hardcoded-secret scan + its mutation self-test below
    "check-links",  # honest denominator: checked vs skipped-by-design per category
    "drift: SKILLS-INDEX",  # gen-skills-index.py --check (index + all 23 category DESCRIPTIONs)
    "drift: CODE-INDEX",  # gen-code-index.py --check
    "drift: REFERENCES-INDEX",  # gen-references-index.py --check
    "drift: DEPENDENCY",  # regen-dependency-map.py --check (xref network, broken refs, standalone)
    "drift: .claude-plugin",  # gen-claude-plugin.py --check (plugin.json + marketplace.json)
    "cron: configs",  # validate-cronjobs.py incl. threshold-key contract check
    "cron: skill refs",  # validate-skill-refs.py — every cron job's skills resolve in-repo
    "drift: installed-plugins",  # sync-installed-plugins.py --check (local Hermes plugins → ref doc)
    "doc counts",  # hand-written numbers vs machine truths (9 claim classes, self-tested)
    "router coverage",  # check-router-coverage.py — skill-flow-router vs the catalog it maps
    "skill pointers",  # check-skill-pointers.py — prose pointers (skill_view, skill load, install) resolve
    "self-test harnesses",  # run-self-tests.py executes the standalone *_verify.py harnesses
    "gate self-test",  # mutation-test-doc-gate.py — proves every doc-count class fails loud
    "secret gate self-test",  # mutation-test-secret-gate.py — plants fake creds, asserts zero misses
    "audit gate self-test",  # mutation-test-audit-gate.py — one planted defect per audit threshold class
    "harness gate self-test",  # mutation-test-selftest-gate.py — PASS/SKIP/FAIL classification proven
    "cron gate self-test",  # mutation-test-cron-gate.py — phantom threshold keys caught
    "router gate self-test",  # mutation-test-router-gate.py — proves all 5 coverage classes fail loud
    "pointer gate self-test",  # mutation-test-pointer-gate.py — one planted defect per pointer form
    "skill-test runner self-test",  # mutation-test-skilltest-gate.py — every suite verdict proven
    "link gate self-test",  # mutation-test-link-gate.py — broken path/anchor, unreadable, floor
    "drift gate self-test",  # mutation-test-drift-gates.py — each index --check reports planted drift
    "tool unit tests",  # tools/tests via run-skill-tests.py --root tools
]


# A gate reports one of three verdicts. SKIP is not a pass: it is printed as SKIP, named in
# the summary line, and only gates declared skippable may produce it (child exit 77, the
# repo-wide convention). Before round-256 the installed-plugins gate skipped with exit 0
# and the table said PASS, the same word it used for a gate that had checked something.
PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"
SKIP_RC = 77
NUMBER_WORDS = (
    "One Two Three Four Five Six Seven Eight Nine Ten Eleven Twelve Thirteen Fourteen "
    "Fifteen Sixteen Seventeen Eighteen Nineteen Twenty"
).split()


def run(label, args, cwd=REPO, may_skip=False, timeout=300):
    """Run a child tool; return (label, verdict, first meaningful output line)."""
    try:
        proc = subprocess.run(
            [PY] + args, cwd=str(cwd), capture_output=True, timeout=timeout, **CHILD_IO
        )
    except subprocess.TimeoutExpired:
        return label, FAIL, f"TIMEOUT after {timeout}s"
    except OSError as e:
        return label, FAIL, f"could not start: {e}"[:200]
    out = (proc.stdout or "") + (proc.stderr or "")
    tail = [ln for ln in out.splitlines() if ln.strip()]
    # A failing gate is summarised by its first FATAL/DRIFT/... line; a passing one by its
    # last line (its verdict). Mutation tests print '[OK] ... is FATAL' for each caught
    # defect, which the keyword search would otherwise show as a passing gate's note.
    note = ""
    if proc.returncode != 0:
        for ln in tail:
            if any(k in ln for k in ("FATAL", "DRIFT", "BROKEN", "ERROR", "Errors:")):
                note = ln.strip()
                break
    if not note and tail:
        note = tail[-1].strip()
    if not tail:
        note = "(no output)"
    if proc.returncode == 0:
        return label, PASS, note[:160]
    if proc.returncode == SKIP_RC:
        if may_skip:
            return label, SKIP, note[:160]
        return label, FAIL, f"exit 77 (skip) from a gate that may not skip: {note}"[:160]
    return label, FAIL, f"exit {proc.returncode}: {note}"[:160]


def run_audit_gate():
    """audit-skills.py emits a JSON report; summarise it rather than echoing its last brace."""
    label = "audit-skills"
    try:
        proc = subprocess.run(
            [PY, "tools/audit-skills.py"],
            cwd=str(REPO),
            capture_output=True,
            timeout=300,
            **CHILD_IO,
        )
    except (subprocess.TimeoutExpired, OSError) as e:
        return label, FAIL, str(e)[:200]
    try:
        data = json.loads(proc.stdout)
        note = f"{data['skill_count']} skills, breached={data['threshold_breached']}"
        breached = data["threshold_breached"]
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        first = (proc.stdout + proc.stderr).strip().splitlines()
        return (
            label,
            FAIL,
            f"unreadable report ({type(e).__name__}): {first[0] if first else 'no output'}"[:160],
        )
    if data.get("breaches"):
        note += " | " + "; ".join(data["breaches"])
    return label, PASS if proc.returncode == 0 and not breached else FAIL, note[:160]


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
      * category counts ('NNN categories') -> live top-level dirs holding SKILL.md files
        (same enumeration gen-skills-index.py uses for its 'across NNN categories' line).
    """
    skills = [
        p
        for p in REPO.rglob("SKILL.md")
        if not any(
            part in (".git", ".hermes", "profiles-export", "memories", "memories-export")
            for part in p.relative_to(REPO).parts
        )
    ]
    live = len(skills)

    # Truths from the machine-generated files (each drift-gated upstream of here). A truth
    # that cannot be derived is itself a problem: until round-256 a missing file or a
    # changed header made its whole claim class return early, so a generator rewording
    # its own header silently switched this gate off for that class.
    problems = []

    def truth_regex(path, pattern, what):
        if not path.exists():
            problems.append(f"{path.name} missing: {what} claims cannot be checked")
            return None
        m = re.search(pattern, path.read_text(encoding="utf-8"))
        if not m:
            problems.append(
                f"{path.name}: no line matches {pattern!r} — its format changed, so "
                f"{what} claims cannot be checked"
            )
            return None
        return int(m.group(1))

    xrefs = truth_regex(
        REPO / "DEPENDENCY.md",
        r"\*\*Network stats:\*\* (\d+) `related_skills` cross-references",
        "cross-reference",
    )
    refdocs = truth_regex(
        REPO / "REFERENCES-INDEX.md", r"\*\*(\d+) reference documents?\*\*", "reference-doc"
    )
    exposed = None
    plugin_json = REPO / ".claude-plugin" / "plugin.json"
    try:
        skills_list = json.loads(plugin_json.read_text(encoding="utf-8"))["skills"]
        if not isinstance(skills_list, list):
            raise TypeError(f"`skills` is a {type(skills_list).__name__}")
        exposed = len(skills_list)
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as e:
        problems.append(
            f".claude-plugin/plugin.json unreadable ({type(e).__name__}: {e}) — "
            "plugin-exposure claims cannot be checked"
        )

    # 6) test suite counts — truth = live discovery (imported, not reimplemented).
    #    run-skill-tests.py is loaded from the CURRENT REPO global so the mutation
    #    self-test's fixture tree works, and its own count_tests() does the counting, so
    #    the README line, CI's suite set and this gate can never disagree. Static counts
    #    (`def test_*`, `test(`, smoke `pass` call sites), not runtime cases — documented
    #    in count_tests(). A discovery crash or an empty result is a problem, not a skip.
    suites_truth = None
    try:
        spec = importlib.util.spec_from_file_location(
            "run_skill_tests", REPO / "tools" / "run-skill-tests.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        counts = {}
        for suite in mod.discover_suites(REPO):
            if suite.key in counts:
                problems.append(f"two test suites share the README key {suite.key!r}")
            counts[suite.key] = (suite.label, mod.count_tests(suite))
        if counts:
            suites_truth = counts
        else:
            problems.append("run-skill-tests discovered no suites: suite counts cannot be checked")
    except Exception as e:  # noqa: BLE001 — any crash here means the class went unchecked
        problems.append(
            f"suite discovery crashed ({type(e).__name__}: {e}): suite counts unchecked"
        )
    for name in ("README.md", "DESCRIPTION.md"):
        text = (REPO / name).read_text(encoding="utf-8")

        def check(pattern, truth, label):
            if truth is None:
                return  # already reported above as an underivable truth
            for m in re.finditer(pattern, text):
                val = int(m.group(1))
                if val != truth:
                    problems.append(f"{name}: claims {val} {label}, truth is {truth}")

        # 1) skill totals (bold + prose forms; both rotted in the wild).
        #    The bold pattern covers every form actually used across README/DESCRIPTION —
        #    **NNN Hermes Agent skills**, **Total: NNN skills ...**, and
        #    **NNN verified, audit-passing skills** — not just a bare `**NNN skills`
        #    (the old narrow pattern matched none of them; round-33 caught that via the
        #    mutation self-test's now-independent application).
        check(
            r"\*\*(?:Total: )?(\d{2,4})\s+(?:Hermes Agent |verified, audit-passing )?skills\b",
            live,
            "bold skill total",
        )
        check(r"\ball (\d{2,4}) skills\b", live, "skills ('all NNN skills')")

        # 2) cross-reference counts — any prose form; truth = DEPENDENCY.md Network stats.
        check(r"\b(\d{2,4}) `related_skills` xrefs?\b", xrefs, "`related_skills` xrefs")
        # 'NNN (cross-)references' only when the sentence is about skills ("...across NNN skills"),
        # so unrelated uses of the word are never treated as an xref claim.
        check(
            r"\b(\d{2,4}) (?:cross-)?references\b(?=.{0,30}?across \d+ skills)",
            xrefs,
            "xref claims",
        )

        # 3) Claude-plugin exposure — truth = plugin.json `skills` array length.
        #    Deliberately NOT 'NNN skills' bare: that is the catalog total, a different metric.
        check(r"\b(\d{2,4}) skills load\b", exposed, "plugin-exposed skills ('load')")
        check(r"\b(\d{2,4})(?:\s+skills)? exposed\b", exposed, "plugin-exposed skills")

        # 4) reference-docs counts — truth = REFERENCES-INDEX.md header (drift-gated).
        check(r"all (\d{2,4}) reference docs?\b", refdocs, "reference docs")

    # 5) README summary-table category rows: '| [cat/](./cat/) | ... | NN |'
    #    Both directions: every row matches disk, and every category on disk has a row.
    #    (Before round-256 a category added without a row, or a row whose skills were
    #    all removed, passed: only rows that existed AND had skills were compared.)
    readme = REPO / "README.md"
    if readme.exists():
        # count by TOP-LEVEL dir (nested skills like mlops/inference/x belong to mlops)
        on_disk = {}
        for p in skills:
            top = p.relative_to(REPO).parts[0]
            on_disk[top] = on_disk.get(top, 0) + 1
        rows = {}
        for m in re.finditer(
            r"\|\s*\[([a-z0-9_-]+)/\]\(\./[a-z0-9_-]+/\)\s*\|[^\n|]*\|\s*(\d+)\s*\|",
            readme.read_text(encoding="utf-8"),
        ):
            cat, claimed = m.group(1), int(m.group(2))
            if cat in rows:
                problems.append(f"README table lists {cat}/ twice")
            rows[cat] = claimed
            actual = on_disk.get(cat, 0)
            if claimed != actual:
                problems.append(f"README table: {cat}/ claims {claimed} skills, disk has {actual}")
        if not rows:
            problems.append("README category table not found (row format changed?)")
        for cat in sorted(set(on_disk) - set(rows)):
            problems.append(f"README table has no row for {cat}/ ({on_disk[cat]} skills on disk)")

    # 6) test suite counts — README's 'Twelve suites currently: comfyui 117 / ...' line.
    #    Parsed from the segment between 'suites currently:' and the first '(' so the
    #    trailing '(counted YYYY-MM-DD; ...)' annotation can never be mistaken for a pair.
    #    Keys are run-skill-tests' Suite.key: the skill dir for pytest suites, '<skill>:<kind>'
    #    for node/sh/ps1 suites. (The old parts[-2] keying silently dropped any suite whose
    #    label had fewer than three path parts from the per-name comparison.)
    if readme.exists() and suites_truth:
        text = readme.read_text(encoding="utf-8")
        m = re.search(r"\b(\w+) suites currently:\s*([^()\n]+)", text)
        listed = {}
        if not m:
            problems.append(
                "README: 'NNN suites currently:' list missing while "
                f"{len(suites_truth)} test suite(s) are on disk"
            )
        else:
            # the count-word itself is a claim too ('Twelve' must stay in sync with
            # both the listed pairs and discovery — round-33 found all three correct,
            # but none of them was guarded before this gate existed).
            word_to_n = {w: i for i, w in enumerate(NUMBER_WORDS, start=1)}
            if m.group(1) not in word_to_n:
                problems.append(
                    f"README suite list: count-word {m.group(1)!r} is not a "
                    f"recognized number (wording drifted from the gate's anchor)"
                )
            elif word_to_n[m.group(1)] != len(suites_truth):
                problems.append(
                    f"README suite list says '{m.group(1)} suites' but disk has {len(suites_truth)}"
                )

            for tok in m.group(2).split("/"):
                pm = re.fullmatch(r"\s*(\S+)\s+(\d+)\s*", tok)
                if not pm:
                    problems.append(f"README suite list: unparseable token {tok!r}")
                    continue
                if pm.group(1) in listed:
                    problems.append(f"README suite list names {pm.group(1)!r} twice")
                listed[pm.group(1)] = int(pm.group(2))

            for name, claimed in listed.items():
                t = suites_truth.get(name)
                if t is None:
                    problems.append(
                        f"README suite list names '{name}' but no such test suite exists on disk"
                    )
                elif claimed != t[1]:
                    problems.append(
                        f"README suite list: {name} claims {claimed} tests, "
                        f"disk has {t[1]} ({t[0]})"
                    )
            for name, (label, n) in suites_truth.items():
                if name not in listed:
                    problems.append(
                        f"README suite list omits live suite {label} as '{name}' ({n} tests)"
                    )

    # 7) category counts — 'NNN categories' prose claims. Truth = SKILLS-INDEX.md's own
    #    footer ('*N skills across M categories.*'), the same line its drift gate keeps
    #    fresh, so this can never disagree with gen-skills-index.py's enumeration.
    cats_truth = truth_regex(
        REPO / "SKILLS-INDEX.md", r"\*\s*(?:\d+) skills across (\d+) categories\b", "category-count"
    )
    if cats_truth is not None:
        for name in ("README.md", "DESCRIPTION.md"):
            f = REPO / name
            if not f.exists():
                continue
            text = f.read_text(encoding="utf-8")
            for m in re.finditer(r"\b(\d{2,3}) categories\b", text):
                if int(m.group(1)) != cats_truth:
                    problems.append(
                        f"{name}: claims {m.group(1)} categories, SKILLS-INDEX has {cats_truth}"
                    )

    # 8) gate counts — 'NNN gates' prose vs the GATE_LABELS list that main() actually runs.
    #    (round-42: every round added a gate and hand-edited four doc lines; nothing checked.)
    #    One qualifier word is allowed ('18 health gates'): round-46 found DESCRIPTION's CI line
    #    still saying '15 health gates' three gates later, invisible to the bare 'NN gates' form.
    if len(GATE_LABELS):
        for name in ("README.md", "DESCRIPTION.md"):
            text = (REPO / name).read_text(encoding="utf-8")
            for m in re.finditer(r"\b(\d{2}) (?:[a-z]+ )?gates\b", text):
                if int(m.group(1)) != len(GATE_LABELS):
                    problems.append(
                        f"{name}: claims {m.group(1)} gates, verify-all runs {len(GATE_LABELS)}"
                    )

    # 9) CI job counts — 'three jobs' prose vs the actual jobs in ci.yml.
    ci = REPO / ".github" / "workflows" / "ci.yml"
    if ci.exists():
        n_jobs = None
        try:
            import yaml as _yaml

            n_jobs = len(_yaml.safe_load(ci.read_text(encoding="utf-8")).get("jobs") or {})
        except Exception as e:  # noqa: BLE001 — unreadable means the class is unchecked
            problems.append(f"ci.yml unreadable ({type(e).__name__}: {e}): CI job claims unchecked")
        if n_jobs == 0:
            problems.append("ci.yml defines no jobs: CI job claims cannot be checked")
        if n_jobs:
            word_to_n = {w.lower(): i for i, w in enumerate(NUMBER_WORDS, start=1)}
            for name in ("README.md", "DESCRIPTION.md"):
                text = (REPO / name).read_text(encoding="utf-8")
                for m in re.finditer(r"\b(" + "|".join(word_to_n) + r") jobs\b", text):
                    if word_to_n[m.group(1)] != n_jobs:
                        problems.append(
                            f"{name}: claims {m.group(1)} CI jobs, ci.yml defines {n_jobs}"
                        )

    if problems:
        return "doc counts", FAIL, "; ".join(problems)[:300]
    return "doc counts", PASS, f"{live} skills, counts agree"


def main():
    # Built explicitly (each gate has its own invocation), but the labels MUST equal
    # GATE_LABELS in order — that list is what the doc-count gate counts against, so a
    # divergence here would make 'NNN gates' prose uncheckable. The assertion makes it fail loud.
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
        # Local-only gate: verifies references/installed-plugins.md matches the
        # live Hermes plugin registry. The one gate allowed to SKIP (exit 77): in CI there
        # is no Hermes install, and on the other machine the doc is not its inventory. A
        # Hermes install whose CLI cannot answer is a FAIL, never a skip.
        run(
            "drift: installed-plugins",
            ["autonomous-ai-agents/hermes-agent/scripts/sync-installed-plugins.py", "--check"],
            may_skip=True,
        ),
        check_doc_counts(),
        # The router is the brain's discovery entry point, and until round-43 nothing
        # checked it against the catalog: 47 skills were added after its last edit and it
        # knew about none of them while every gate stayed green. In-scope skills must be
        # routed or explicitly declared out-of-scope with a reason.
        run("router coverage", ["tools/check-router-coverage.py"]),
        # audit-skills validates the related_skills frontmatter, but pointers written in running
        # text (skill_view(name=...), `hermes skill load <category>/<name>`, skill_manage install) rotted
        # unchecked until round-64 found three: a skill that never existed, a tool name used
        # as a skill, and a Quick Start command with the wrong category directory.
        run("skill pointers", ["tools/check-skill-pointers.py"]),
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
        # The rest of the audit tests itself: one planted defect per threshold-gated class
        # (no frontmatter, missing field, long description, broken ref, duplicate name,
        # missing sections, missing script) plus a clean control that must stay clean.
        run("audit gate self-test", ["tools/mutation-test-audit-gate.py"]),
        # The harness runner (gate 6) tests itself: proves PASS/SKIP-rc77/SKIP-dep/FAIL
        # classification and manifest-drift detection on throwaway temp fixtures.
        run("harness gate self-test", ["tools/mutation-test-selftest-gate.py"]),
        # The cron threshold-key check (gate 8) tests itself: plants phantom keys in temp
        # fixture copies and asserts the validator fails loudly, plus proves --job works.
        run("cron gate self-test", ["tools/mutation-test-cron-gate.py"]),
        # The router gate (gate 11) tests itself: plants an unrouted skill, a reasonless
        # opt-out, a phantom, a contradiction and a rotting count in temp fixtures.
        run("router gate self-test", ["tools/mutation-test-router-gate.py"]),
        # The pointer gate tests itself: one planted defect per pointer form (missing skill, tool
        # name as skill, wrong category, missing path, missing install, JSON-escaped), plus
        # placeholders, archive files and a clean control that must stay clean.
        run("pointer gate self-test", ["tools/mutation-test-pointer-gate.py"]),
        # The skill-test runner (CI's skill-tests job) tests itself: pass/fail/all-skipped/
        # zero-collected/collection-error per suite kind (pytest, node, sh, ps1), orphan test
        # files and an empty scan. Round-256 found it blind to node and shell suites.
        run("skill-test runner self-test", ["tools/mutation-test-skilltest-gate.py"], timeout=600),
        # The link checker tests itself: a broken path, a broken #anchor, an unreadable file,
        # links inside code that must be ignored, and a scan below its floor.
        run("link gate self-test", ["tools/mutation-test-link-gate.py"]),
        # The five index drift gates test themselves: a temp copy of the tree gets one planted
        # change per index and each --check must report DRIFT; an emptied tree must hit the floor.
        run("drift gate self-test", ["tools/mutation-test-drift-gates.py"], timeout=600),
        # Unit tests for the tooling itself (tools/tests/): the sync pre-push decision and
        # its error propagation, the installed-plugins failure paths, verify-all's verdicts
        # and the index write-guard. Run by the same proven runner as the skill suites.
        run("tool unit tests", ["tools/run-skill-tests.py", "--root", "tools"]),
    ]
    assert [r[0] for r in results] == GATE_LABELS, (
        "verify-all's result labels diverged from GATE_LABELS — the doc-count gate counts "
        f"against that list: {[r[0] for r in results]}"
    )

    bad = [r for r in results if r[1] not in (PASS, FAIL, SKIP)]
    assert not bad, f"gate returned an unknown verdict: {bad}"

    width = max(len(r[0]) for r in results)
    print("\n=== verify-all ===")
    for label, verdict, note in results:
        print(f"  {verdict}  {label.ljust(width)}  {note}")

    failed = [r[0] for r in results if r[1] == FAIL]
    skipped = [r[0] for r in results if r[1] == SKIP]
    print()
    if failed:
        print(f"FAILED ({len(failed)}/{len(results)}): {', '.join(failed)}")
        if skipped:
            print(f"also SKIPPED (not checked): {', '.join(skipped)}")
        return 1
    if skipped:
        # Exit 0: every skip here is a declared, explained one (may_skip=True). But the line
        # never says 'ALL GATES PASSED' while something went unchecked.
        print(
            f"{len(results) - len(skipped)}/{len(results)} GATES PASSED, "
            f"{len(skipped)} SKIPPED (not checked here): {', '.join(skipped)}"
        )
        return 0
    print(f"ALL {len(results)} GATES PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
