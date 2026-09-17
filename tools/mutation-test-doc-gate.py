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
# parents[1] is correct once this file lives in tools/; while it sits elsewhere
# (e.g. Temp during development) fall back to the known repo location.
REPO = _HERE.parents[1]
if not (REPO / "tools" / "verify-all.py").exists():
    REPO = Path(r"C:\Users\Owner\OneDrive\Documents\GitHub\Hermes_Skills")


def load_gate():
    """Import verify-all as a module and return it (top-level is side-effect free)."""
    spec = importlib.util.spec_from_file_location("verifyall", REPO / "tools" / "verify-all.py")
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

    for fname in ("README.md", "DESCRIPTION.md", "DEPENDENCY.md", "REFERENCES-INDEX.md",
                  "SKILLS-INDEX.md"):
        src = REPO / fname
        if not src.exists():
            raise SystemExit(f"[FATAL] expected {fname} at the repo root — layout changed?")
        shutil.copy2(src, tmp / fname)

    plugin_json = REPO / ".claude-plugin" / "plugin.json"
    if plugin_json.exists():
        (tmp / ".claude-plugin").mkdir(parents=True, exist_ok=True)
        shutil.copy2(plugin_json, tmp / ".claude-plugin" / "plugin.json")

    # claim class 6 needs live discovery inside the fixture: copy run-skill-tests.py and
    # every pytest tests/ dir (relative paths preserved). Without these, suites_truth is
    # None in the gate and the whole class silently skips — which would make its
    # mutations below prove nothing.
    (tmp / "tools").mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO / "tools" / "run-skill-tests.py", tmp / "tools" / "run-skill-tests.py")
    for tf in REPO.rglob("*.py"):
        rel = tf.relative_to(REPO)
        parts = list(rel.parts)
        if len(parts) < 2 or parts[-2] != "tests":
            continue
        if any(x in parts for x in ("profiles-export", ".git")):
            continue
        d = tmp / Path(*parts[:-1])
        d.mkdir(parents=True, exist_ok=True)
        shutil.copy2(tf, d / tf.name)


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
    skills = [p for p in REPO.rglob("SKILL.md")
              if not any(part in (".git", ".hermes", "profiles-export", "memories",
                                  "memories-export") for part in p.relative_to(REPO).parts)]
    live = len(skills)

    xrefs = None
    dep = REPO / "DEPENDENCY.md"
    if dep.exists():
        m = re.search(r"\*\*Network stats:\*\* (\d+) `related_skills` cross-references",
                      dep.read_text(encoding="utf-8"))
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
        m = re.search(r"\*\*(\d+) reference documents?\*\*",
                      refs_index.read_text(encoding="utf-8"))
        refdocs = int(m.group(1)) if m else None

    return live, xrefs, exposed, refdocs


def build_mutations(tmp: Path):
    """Return [(label, file, old, new)] with anchors derived from live truths."""
    live, xrefs, exposed, refdocs = live_truths()
    readme = (tmp / "README.md").read_text(encoding="utf-8")
    desc = (tmp / "DESCRIPTION.md").read_text(encoding="utf-8")
    mutations = []

    # 1) plugin exposure — README's 'NNN skills load' must equal the manifest length.
    if exposed is not None:
        old = f"and {exposed} skills load"
        if readme.count(old) == 1:
            mutations.append(("plugin exposure ('skills load')", "README.md",
                              old, f"and {exposed - 4} skills load"))

    # 2) prose skill total — DESCRIPTION's 'index of all NNN skills'.
    old = f"index of all {live} skills"
    if desc.count(old) == 1:
        mutations.append(("prose skill total ('all NNN skills')", "DESCRIPTION.md",
                          old, f"index of all {live - 1} skills"))

    # 3) bold skill total — README's '**Total: NNN skills across ...**' (the unique
    #    full phrase; the bare tagline '**NNN Hermes Agent skills**' appears twice).
    m = re.search(r"\*\*Total: (\d+) skills across \d+ categories\*\*", readme)
    if m and int(m.group(1)) == live:
        mutations.append(("bold skill total ('**Total: NNN skills')", "README.md",
                          f"**Total: {live} skills", f"**Total: {live + 1} skills"))

    # 4) cross-reference count — README carries the xref number in two wordings;
    #    try each full phrase as a unique anchor (the bare 'NNN references' is not).
    if xrefs is not None:
        candidates = [
            f"{xrefs} cross-references mapped across {live} skills",  # overview line
            "\u2014 " + f"{xrefs} cross-references across {live} skills",  # invariants bullet
        ]
        for old in candidates:
            if readme.count(old) == 1:
                mutations.append(("cross-reference count (prose)", "README.md",
                                  old, old.replace(str(xrefs), str(xrefs - 1), 1)))
                break

    # 5) category table row — the full line is unique per row (its [cat/](./cat/) link).
    #    Pick the largest-count row; strip its trailing count cell and append +1.
    rows = re.findall(
        r"\|\s*\[([a-z0-9_-]+)/\]\(\./[a-z0-9_-]+/\)\s*\|[^\n|]*\|\s*(\d+)\s*\|", readme)
    if rows:
        cat, count = max(rows, key=lambda r: int(r[1]))
        link = f"[{cat}/](./{cat}/)"
        row_line = next((l for l in readme.splitlines() if link in l), None)
        suffix = f"| {count} |"
        if row_line is not None and row_line.rstrip().endswith(suffix):
            body = row_line.rstrip()[: -len(suffix)]
            mutations.append((f"category table row ({cat}/)", "README.md",
                              row_line, body + f"| {int(count) + 1} |"))

    # 6) reference-docs count — DESCRIPTION's 'all NNN reference docs'.
    if refdocs is not None:
        old = f"all {refdocs} reference docs"
        if desc.count(old) == 1:
            mutations.append(("reference-docs count", "DESCRIPTION.md",
                              old, f"all {refdocs - 1} reference docs"))

    # 7+8) pytest suite counts — README's 'Seven suites currently: comfyui N / ...' line.
    #      Truth comes from run-skill-tests.discover_suites() — the SAME imported path
    #      verify-all uses, so this test and the gate can never disagree on what a suite is.
    spec = importlib.util.spec_from_file_location(
        "run_skill_tests", REPO / "tools" / "run-skill-tests.py")
    rst = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rst)
    suite_counts = {}
    for label, tests_dir in rst.discover_suites(REPO):
        n = 0
        for tf in sorted(tests_dir.rglob("*.py")):
            txt = tf.read_text(encoding="utf-8", errors="replace")
            n += len(re.findall(r"^\s*def (test_\w+)", txt, re.M))
        parts = Path(label).parts
        if len(parts) >= 3:
            suite_counts[parts[-2]] = n

    m = re.search(r"\b(\w+) suites currently:\s*([^()\n]+)", readme)
    if m and len(suite_counts):
        # 7) one listed count off by one (largest suite, so the anchor 'name N' is unique)
        name, n = max(suite_counts.items(), key=lambda kv: kv[1])
        old = f"{name} {n}"
        if readme.count(old) == 1 and m.group(2).count(old):
            mutations.append(("pytest suite count (listed pair)", "README.md",
                              old, f"{name} {n + 1}"))
        # 8) the count-word itself ('Seven suites' vs disk truth)
        word_to_n = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5,
                     "Six": 6, "Seven": 7, "Eight": 8, "Nine": 9, "Ten": 10}
        if m.group(1) in word_to_n and word_to_n[m.group(1)] == len(suite_counts):
            wrong = {v: k for k, v in word_to_n.items()}[len(suite_counts) - 1] \
                if len(suite_counts) >= 2 else "Six"
            old = f"{m.group(1)} suites currently:"
            if readme.count(old) == 1 and wrong != m.group(1):
                mutations.append(("pytest suite count-word", "README.md",
                                  old, f"{wrong} suites currently:"))

    # 9) category counts — README's '**Total: NNN skills across M categories**' line.
    #    (The bare '23 categories' appears twice in README + DESCRIPTION; this full bold
    #    phrase is the unique anchor.) Truth = SKILLS-INDEX.md footer, same as the gate.
    m = re.search(r"\*\*Total: \d+ skills across (\d+) categories\*\*", readme)
    sk_footer = (tmp / "SKILLS-INDEX.md").read_text(encoding="utf-8")
    fm_ = re.search(r"\*\s*\d+ skills across (\d+) categories\b", sk_footer)
    if m and fm_ and int(m.group(1)) == int(fm_.group(1)):
        mutations.append(("category count ('across NNN categories')", "README.md",
                          f"skills across {m.group(1)} categories**",
                          f"skills across {int(m.group(1)) + 1} categories**"))

    return live, xrefs, exposed, refdocs, mutations


def main():
    mod = load_gate()
    tmp = Path(tempfile.mkdtemp(prefix="doc-gate-mut-", dir=str(REPO.parent)))
    try:
        build_fixture(tmp)
        # check_doc_counts reads verify-all's module-level REPO global — point it at the fixture.
        mod.REPO = tmp

        # The fixture must start green — otherwise the mutations prove nothing.
        label, ok, note = mod.check_doc_counts()
        if not ok:
            print(f"[FAIL] baseline does not pass on the real docs: {note}")
            return 1
        print(f"baseline OK ({note})")

        live, xrefs, exposed, refdocs, mutations = build_mutations(tmp)
        missing_truths = [n for n, v in (("skills", live), ("xrefs", xrefs),
                                         ("plugin exposure", exposed),
                                         ("ref docs", refdocs)) if v is None]
        # 9 claim classes (skills total bold+prose, xrefs, plugin exposure, ref docs,
        # category table row, pytest suite count + count-word, category count). The floor
        # counts BUILT mutations; each class contributes at least one when its truths are
        # present. A missing anchor means a doc's wording drifted from what this test
        # expects — fail loudly rather than silently stop guarding that class.
        if len(mutations) < 9:
            print(f"[FAIL] only {len(mutations)}/9 mutations built — truths missing: "
                  f"{missing_truths or 'none'}; a doc's wording must have drifted from an anchor")
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
                _, ok, note = mod.check_doc_counts()
            finally:
                f.write_text(orig, encoding="utf-8")  # always restore the clean baseline
            if ok:
                failures.append(label)
                print(f"[FAIL] mutation NOT caught: {label}")
            else:
                print(f"  caught: {label} -> {note[:100]}")

        # final sanity: after all reverts the fixture must be green again — a leak in
        # any revert would otherwise silently corrupt nothing but prove our loop is broken.
        _, ok, note = mod.check_doc_counts()
        if not ok:
            print(f"[FAIL] baseline no longer passes after mutation cycle (revert leaked): {note}")
            return 1

        if failures:
            print(f"\nFAILED ({len(failures)}/{len(mutations)} mutations missed): "
                  f"{', '.join(failures)}")
            return 1
        print(f"ALL {len(mutations)} MUTATIONS CAUGHT — doc-count gate verified fail-loud.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
