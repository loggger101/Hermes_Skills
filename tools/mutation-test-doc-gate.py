#!/usr/bin/env python3
"""Mutation test for verify-all.check_doc_counts — the doc-count gate tests itself.

Why this exists (round-20b audit): check_doc_counts is a hand-maintained prose
checker, and its first version only matched the exact phrasing it was written
for — README's tagline (`**202 Hermes Agent skills**`) rotted for an entire
audit pass while every other count spot got fixed. A gate that cannot be wrong
is one whose failure modes are exercised on purpose: this script copies the
minimal file set into a temp dir, points verify-all's REPO at it, mutates each
claim class in turn, and asserts the gate FAILS LOUDLY on every mutation.

Anchors are DERIVED from live truth values (plugin.json array length, DEPENDENCY.md
Network stats, REFERENCES-INDEX header), never hard-coded — so routine count
changes cannot break this tool; it only fails loudly when a doc's WORDING drifts
from what the gate expects, which is exactly when a human must look.

If check_doc_counts gains a new claim class, add its mutation here — an
untested claim class is an unenforced one.

Run:  py tools/mutation-test-doc-gate.py     (also invoked by verify-all as a gate)
Exit 0 = baseline passes AND every mutation caught; exit 1 otherwise. Stdlib only.
"""

import importlib.util
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

if sys.version_info < (3, 8):
    raise SystemExit(
        "[FATAL] this tool needs Python 3.8+, got "
        + sys.version.split()[0]
        + f" at {sys.executable or '<unknown interpreter>'}"
    )
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

_HERE = Path(__file__).resolve()
# parents[1] is the repo only while this file lives in tools/. A copy run from anywhere
# else exits instead of falling back to a hard-coded checkout: that path existed on one
# machine only, and on it the test would have silently exercised a different tree.
REPO = _HERE.parents[1]
if not (REPO / "tools" / "verify-all.py").exists():
    raise SystemExit(
        f"[FATAL] {_HERE.name} must run from the repo's tools/ dir "
        f"(no tools/verify-all.py under {REPO})"
    )


def load_gate():
    """Import verify-all as a module and return it (top-level is side-effect free)."""
    spec = importlib.util.spec_from_file_location("verifyall", REPO / "tools" / "verify-all.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_runner():
    """Import run-skill-tests.py: the single source of what a suite is and how it counts."""
    spec = importlib.util.spec_from_file_location(
        "run_skill_tests", REPO / "tools" / "run-skill-tests.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_fixture(tmp: Path):
    """Copy the minimal file set check_doc_counts reads into tmp, preserving relative paths."""
    for p in REPO.rglob("SKILL.md"):
        rel = p.relative_to(REPO)
        if str(rel).startswith(("profiles-export", ".git")):
            continue  # outside the gate's counting scope; copying it only slows CI down
        d = tmp / rel.parent
        d.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, d / "SKILL.md")

    for fname in (
        "README.md",
        "DESCRIPTION.md",
        "DEPENDENCY.md",
        "REFERENCES-INDEX.md",
        "SKILLS-INDEX.md",
    ):
        src = REPO / fname
        if not src.exists():
            raise SystemExit(f"[FATAL] expected {fname} at the repo root — layout changed?")
        shutil.copy2(src, tmp / fname)

    plugin_json = REPO / ".claude-plugin" / "plugin.json"
    if plugin_json.exists():
        (tmp / ".claude-plugin").mkdir(parents=True, exist_ok=True)
        shutil.copy2(plugin_json, tmp / ".claude-plugin" / "plugin.json")

    # claim class 6 needs live discovery inside the fixture: copy run-skill-tests.py and
    # every file of every suite it discovers (pytest, node, sh, ps1; relative paths
    # preserved). Without these the gate reports 'no suites discovered' and the class's
    # mutations below would prove nothing.
    (tmp / "tools").mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO / "tools" / "run-skill-tests.py", tmp / "tools" / "run-skill-tests.py")
    rst = load_runner()
    for suite in rst.discover_suites(REPO):
        files = suite.files if suite.kind != "pytest" else sorted(suite.dir.rglob("*.py"))
        for f in files:
            dest = tmp / f.relative_to(REPO)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)
    for name in ("workflows",):
        src = REPO / ".github" / name / "ci.yml"
        (tmp / ".github" / name).mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, tmp / ".github" / name / "ci.yml")


def mutate(tmp: Path, fname: str, old: str, new: str):
    f = tmp / fname
    text = f.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise SystemExit(
            f"[FATAL] mutation anchor not unique in {fname} "
            f"({text.count(old)}x): {old[:70]!r}\n"
            "The doc's wording changed — update this test's anchors to match."
        )
    f.write_text(text.replace(old, new), encoding="utf-8")


def live_truths():
    """Same truths the gate compares against (each machine-generated and drift-gated)."""
    skills = [
        p
        for p in REPO.rglob("SKILL.md")
        if not any(
            part in (".git", ".hermes", "profiles-export", "memories", "memories-export")
            for part in p.relative_to(REPO).parts
        )
    ]
    live = len(skills)

    xrefs = None
    dep = REPO / "DEPENDENCY.md"
    if dep.exists():
        m = re.search(
            r"\*\*Network stats:\*\* (\d+) `related_skills` cross-references",
            dep.read_text(encoding="utf-8"),
        )
        xrefs = int(m.group(1)) if m else None

    exposed = None
    plugin_json = REPO / ".claude-plugin" / "plugin.json"
    if plugin_json.exists():
        try:
            exposed = len(json.loads(plugin_json.read_text(encoding="utf-8")).get("skills", []))
        except (json.JSONDecodeError, OSError):
            pass

    refdocs = None
    refs_index = REPO / "REFERENCES-INDEX.md"
    if refs_index.exists():
        m = re.search(r"\*\*(\d+) reference documents?\*\*", refs_index.read_text(encoding="utf-8"))
        refdocs = int(m.group(1)) if m else None

    return live, xrefs, exposed, refdocs


# Every class build_mutations() must produce. Adding a class to check_doc_counts means
# adding its mutation AND its name here; removing a name needs a reason in the commit.
REQUIRED_CLASSES = {
    "plugin exposure ('skills load')",
    "prose skill total ('all NNN skills')",
    "bold skill total ('**Total: NNN skills')",
    "cross-reference count (prose)",
    "category table row",
    "reference-docs count",
    "pytest suite count (listed pair)",
    "pytest suite count-word",
    "category count ('across NNN categories')",
    "gate count ('NNN gates')",
    "gate count ('NN health gates')",
    "category table missing row",
    "category table phantom row",
    "truth unreadable: DEPENDENCY network stats",
    "truth unreadable: REFERENCES-INDEX header",
    "truth unreadable: plugin.json skills key",
    "truth unreadable: SKILLS-INDEX footer",
    "truth unreadable: suite discovery crashes",
    "truth unreadable: ci.yml jobs",
}


def build_mutations(tmp: Path):
    """Return [(label, file, old, new)] with anchors derived from live truths."""
    live, xrefs, exposed, refdocs = live_truths()
    n_gates = len(load_gate().GATE_LABELS)  # class-8 truth (same list verify-all runs)
    readme = (tmp / "README.md").read_text(encoding="utf-8")
    desc = (tmp / "DESCRIPTION.md").read_text(encoding="utf-8")
    mutations = []

    # 1) plugin exposure — README's 'NNN skills load' must equal the manifest length.
    if exposed is not None:
        old = f"and {exposed} skills load"
        if readme.count(old) == 1:
            mutations.append(
                (
                    "plugin exposure ('skills load')",
                    "README.md",
                    old,
                    f"and {exposed - 4} skills load",
                )
            )

    # 2) prose skill total — DESCRIPTION's 'index of all NNN skills'.
    old = f"index of all {live} skills"
    if desc.count(old) == 1:
        mutations.append(
            (
                "prose skill total ('all NNN skills')",
                "DESCRIPTION.md",
                old,
                f"index of all {live - 1} skills",
            )
        )

    # 3) bold skill total — README's '**Total: NNN skills across ...**' (the unique
    #    full phrase; the bare tagline '**NNN Hermes Agent skills**' appears twice).
    m = re.search(r"\*\*Total: (\d+) skills across \d+ categories\*\*", readme)
    if m and int(m.group(1)) == live:
        mutations.append(
            (
                "bold skill total ('**Total: NNN skills')",
                "README.md",
                f"**Total: {live} skills",
                f"**Total: {live + 1} skills",
            )
        )

    # 4) cross-reference count — README carries the xref number in two wordings;
    #    try each full phrase as a unique anchor (the bare 'NNN references' is not).
    if xrefs is not None:
        candidates = [
            f"{xrefs} cross-references mapped across {live} skills",  # overview line
            "\u2014 " + f"{xrefs} cross-references across {live} skills",  # invariants bullet
        ]
        for old in candidates:
            if readme.count(old) == 1:
                mutations.append(
                    (
                        "cross-reference count (prose)",
                        "README.md",
                        old,
                        old.replace(str(xrefs), str(xrefs - 1), 1),
                    )
                )
                break

    # 5) category table row — the full line is unique per row (its [cat/](./cat/) link).
    #    Pick the largest-count row; strip its trailing count cell and append +1.
    rows = re.findall(
        r"\|\s*\[([a-z0-9_-]+)/\]\(\./[a-z0-9_-]+/\)\s*\|[^\n|]*\|\s*(\d+)\s*\|", readme
    )
    if rows:
        cat, count = max(rows, key=lambda r: int(r[1]))
        link = f"[{cat}/](./{cat}/)"
        row_line = next((line for line in readme.splitlines() if link in line), None)
        suffix = f"| {count} |"
        if row_line is not None and row_line.rstrip().endswith(suffix):
            body = row_line.rstrip()[: -len(suffix)]
            mutations.append(
                (
                    f"category table row ({cat}/)",
                    "README.md",
                    row_line,
                    body + f"| {int(count) + 1} |",
                )
            )

    # 6) reference-docs count — DESCRIPTION's 'all NNN reference docs'.
    if refdocs is not None:
        old = f"all {refdocs} reference docs"
        if desc.count(old) == 1:
            mutations.append(
                ("reference-docs count", "DESCRIPTION.md", old, f"all {refdocs - 1} reference docs")
            )

    # 7+8) pytest suite counts — README's 'Seven suites currently: comfyui N / ...' line.
    #      Truth comes from run-skill-tests.discover_suites() — the SAME imported path
    #      verify-all uses, so this test and the gate can never disagree on what a suite is.
    rst = load_runner()
    suite_counts = {s.key: rst.count_tests(s) for s in rst.discover_suites(REPO)}

    m = re.search(r"\b([\w-]+) suites currently:\s*([^()\n]+)", readme)
    if m and len(suite_counts):
        # 7) one listed count off by one (largest suite, so the anchor 'name N' is unique)
        name, n = max(suite_counts.items(), key=lambda kv: kv[1])
        old = f"{name} {n}"
        if readme.count(old) == 1 and m.group(2).count(old):
            mutations.append(
                ("pytest suite count (listed pair)", "README.md", old, f"{name} {n + 1}")
            )
        # 8) the count-word itself ('Seven suites' vs disk truth)
        word_to_n = {w: i for i, w in enumerate(load_gate().NUMBER_WORDS, start=1)}
        if m.group(1) in word_to_n and word_to_n[m.group(1)] == len(suite_counts):
            wrong = (
                {v: k for k, v in word_to_n.items()}[len(suite_counts) - 1]
                if len(suite_counts) >= 2
                else "Six"
            )
            old = f"{m.group(1)} suites currently:"
            if readme.count(old) == 1 and wrong != m.group(1):
                mutations.append(
                    ("pytest suite count-word", "README.md", old, f"{wrong} suites currently:")
                )

    # 9) category counts — README's '**Total: NNN skills across M categories**' line.
    #    (The bare '23 categories' appears twice in README + DESCRIPTION; this full bold
    #    phrase is the unique anchor.) Truth = SKILLS-INDEX.md footer, same as the gate.
    m = re.search(r"\*\*Total: \d+ skills across (\d+) categories\*\*", readme)
    sk_footer = (tmp / "SKILLS-INDEX.md").read_text(encoding="utf-8")
    fm_ = re.search(r"\*\s*\d+ skills across (\d+) categories\b", sk_footer)
    if m and fm_ and int(m.group(1)) == int(fm_.group(1)):
        mutations.append(
            (
                "category count ('across NNN categories')",
                "README.md",
                f"skills across {m.group(1)} categories**",
                f"skills across {int(m.group(1)) + 1} categories**",
            )
        )

    # 10) gate counts — README's 'NNN gates' prose vs GATE_LABELS (the list verify-all runs).
    #     Class-9 truth (ci.yml job count) lives outside the fixture, so only class 8 is
    #     mutation-provable here; its anchor is unique in README ('# NNN gates;' quickstart line).
    if n_gates:
        old = f"# {n_gates} gates;"
        if readme.count(old) == 1:
            mutations.append(
                ("gate count ('NNN gates')", "README.md", old, f"# {n_gates + 1} gates;")
            )
        # the qualified form ('NN health gates', DESCRIPTION's CI line) — round-46 widened the
        # gate's regex after this exact line sat at a stale '15' for three rounds.
        desc = (tmp / "DESCRIPTION.md").read_text(encoding="utf-8")
        old = f"all {n_gates} health gates"
        if desc.count(old) == 1:
            mutations.append(
                (
                    "gate count ('NN health gates')",
                    "DESCRIPTION.md",
                    old,
                    f"all {n_gates - 3} health gates",
                )
            )

    # 11) category table, both directions (round-256): a category on disk with no row, and
    #     a row for a category that has no skills. Before, both passed silently.
    if rows:
        cat, count = rows[0]
        link = f"[{cat}/](./{cat}/)"
        row_line = next((line for line in readme.splitlines() if link in line), None)
        if row_line is not None:
            mutations.append(("category table missing row", "README.md", row_line + "\n", ""))
            phantom = row_line.replace(f"[{cat}/](./{cat}/)", "[zz-ghost/](./zz-ghost/)", 1)
            mutations.append(
                ("category table phantom row", "README.md", row_line, row_line + "\n" + phantom)
            )

    # 12) underivable truths (round-256): each source's anchor line reworded or its file
    #     made unreadable must FAIL the gate. Before, each made its class return early, so
    #     a generator rewording its own header switched that class off without a sound.
    dep = (tmp / "DEPENDENCY.md").read_text(encoding="utf-8")
    m = re.search(r"\*\*Network stats:\*\* \d+ `related_skills` cross-references", dep)
    if m:
        mutations.append(
            (
                "truth unreadable: DEPENDENCY network stats",
                "DEPENDENCY.md",
                m.group(0),
                m.group(0).replace("Network stats", "Graph stats"),
            )
        )
    ri = (tmp / "REFERENCES-INDEX.md").read_text(encoding="utf-8")
    m = re.search(r"\*\*\d+ reference documents?\*\*", ri)
    if m:
        mutations.append(
            (
                "truth unreadable: REFERENCES-INDEX header",
                "REFERENCES-INDEX.md",
                m.group(0),
                m.group(0).replace("reference doc", "reference file"),
            )
        )
    pj = (tmp / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
    if pj.count('"skills"') == 1:
        mutations.append(
            (
                "truth unreadable: plugin.json skills key",
                ".claude-plugin/plugin.json",
                '"skills"',
                '"skillz"',
            )
        )
    m = re.search(r"\d+ skills across \d+ categories", sk_footer)
    if m and sk_footer.count(m.group(0)) == 1:
        mutations.append(
            (
                "truth unreadable: SKILLS-INDEX footer",
                "SKILLS-INDEX.md",
                m.group(0),
                m.group(0).replace("categories", "groups"),
            )
        )
    mutations.append(
        (
            "truth unreadable: suite discovery crashes",
            "tools/run-skill-tests.py",
            "    root = Path(root or REPO)\n    by_key = {}\n",
            '    raise RuntimeError("planted discovery crash")\n',
        )
    )
    ci = (tmp / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    if ci.count("\njobs:\n") == 1:
        mutations.append(
            (
                "truth unreadable: ci.yml jobs",
                ".github/workflows/ci.yml",
                "\njobs:\n",
                "\njobs: [\n",
            )
        )

    return live, xrefs, exposed, refdocs, mutations


def main():
    mod = load_gate()
    tmp = Path(tempfile.mkdtemp(prefix="doc-gate-mut-", dir=str(REPO.parent)))
    try:
        build_fixture(tmp)
        # check_doc_counts reads verify-all's module-level REPO global — point it at the fixture.
        mod.REPO = tmp

        # The fixture must start green — otherwise the mutations prove nothing.
        label, verdict, note = mod.check_doc_counts()
        if verdict != mod.PASS:
            print(f"[FAIL] baseline does not pass on the real docs: {note}")
            return 1
        print(f"baseline OK ({note})")

        live, xrefs, exposed, refdocs, mutations = build_mutations(tmp)
        missing_truths = [
            n
            for n, v in (
                ("skills", live),
                ("xrefs", xrefs),
                ("plugin exposure", exposed),
                ("ref docs", refdocs),
            )
            if v is None
        ]
        # Every claim class must build its mutation, BY NAME. (The old check was a floor of
        # 11 on the total: one class could lose its anchor while another gained a mutation,
        # and the class would go unguarded behind an unchanged count.) A missing class
        # means a doc's wording drifted from this test's anchor — fail loudly.
        built = {
            label.split(" (")[0] if label.startswith("category table row") else label
            for label, *_ in mutations
        }
        missing = sorted(REQUIRED_CLASSES - built)
        if missing:
            print(
                f"[FAIL] {len(missing)} claim class(es) built no mutation: {missing}; "
                f"truths missing: {missing_truths or 'none'}. A doc's wording drifted from an "
                "anchor in build_mutations(); update the anchor, never drop the class."
            )
            return 1

        failures = []
        for label, fname, old, new in mutations:
            # Apply each mutation to a CLEAN copy of its file and revert afterwards.
            # (The original loop applied them cumulatively — later "caught" results were
            # then contaminated by earlier drift in the same file, so they proved nothing
            # about their own class. Round-33 fix: every mutation is proven independently.)
            f = tmp / fname
            orig = f.read_text(encoding="utf-8")
            try:
                mutate(tmp, fname, old, new)
                _, verdict, note = mod.check_doc_counts()
            finally:
                f.write_text(orig, encoding="utf-8")  # always restore the clean baseline
            if verdict == mod.PASS:
                failures.append(label)
                print(f"[FAIL] mutation NOT caught: {label}")
            else:
                print(f"  caught: {label} -> {note[:100]}")

        # final sanity: after all reverts the fixture must be green again — a leak in
        # any revert would otherwise silently corrupt nothing but prove our loop is broken.
        _, verdict, note = mod.check_doc_counts()
        if verdict != mod.PASS:
            print(f"[FAIL] baseline no longer passes after mutation cycle (revert leaked): {note}")
            return 1

        if failures:
            print(
                f"\nFAILED ({len(failures)}/{len(mutations)} mutations missed): "
                f"{', '.join(failures)}"
            )
            return 1
        print(f"ALL {len(mutations)} MUTATIONS CAUGHT — doc-count gate verified fail-loud.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
