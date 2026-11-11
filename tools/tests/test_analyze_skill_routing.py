"""tools/analyze-skill-routing.py (round-308) on throwaway trees and pure functions.

Covers the parts a wrong edit would silently break: the trigger-clause rule's
negation handling, name!=directory detection driving the exit code, the TF-IDF
collision pair actually firing between near-duplicate descriptions while an unrelated
skill stays clear, and --probe ranking the right skill first.
"""

import json
import subprocess
import sys

from conftest import REPO, load_tool

SCRIPT = REPO / "tools" / "analyze-skill-routing.py"


def mod():
    return load_tool("tools/analyze-skill-routing.py")


def write_skill(root, rel, name, description, extra_fm="", subdirs=()):
    d = root / rel
    d.mkdir(parents=True)
    for sub in subdirs:
        (d / sub).mkdir()
    text = f'---\nname: {name}\ndescription: "{description}"\n{extra_fm}---\n\n# body\n'
    (d / "SKILL.md").write_text(text, encoding="utf-8")


def run(root, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(root), *args],
        capture_output=True,
        text=True,
        timeout=120,
    )


# ---- trigger-clause rule (upstream skill-lint.js DESCRIPTION_TRIGGER) ----


def test_trigger_accepts_positive_and_rejects_noun_phrase():
    m = mod()
    assert m.has_positive_trigger("Use when routing prompts across skills.")
    assert m.has_positive_trigger("Use before writing code to pin versions.")
    assert not m.has_positive_trigger("Query CSV/Parquet/S3 data ad-hoc via DuckDB.")


def test_negated_only_clause_is_not_a_trigger():
    m = mod()
    assert not m.has_positive_trigger("Do not use when the file is already pinned.")
    # two negations and no positive clause: stripping only the first would pass on leftovers
    assert not m.has_positive_trigger("Don't use when editing docs. Never use before review.")


def test_positive_survives_a_negated_clause():
    m = mod()
    assert m.has_positive_trigger("Use when auditing a skill library; do not use when writing one.")


# ---- stemmer folds the pairs upstream documented ----


def test_stem_folds_plural_and_nominalisation():
    m = mod()
    assert m.stem("conflicts") == m.stem("conflict")
    assert m.stem("verification").startswith(m.stem("verify")[:4])
    # '-ification' must fold to the verb stem, not lose '-ication' into 'specific'
    assert m.stem("specifications") != m.stem("specific")


# ---- C1 name mismatch is a hard finding and fails the run ----


def test_name_mismatch_is_hard_and_exits_1(tmp_path):
    write_skill(tmp_path / "cat", "name-mismatch", "other-name", "Use when doing work.")
    proc = run(tmp_path, "--quiet")
    assert proc.returncode == 1
    out = tmp_path / "r.json"
    run(tmp_path, "--quiet", "--json", str(out))
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["skills_scanned"] == 1
    assert report["C1_name_ne_dir"][0]["name"] == "other-name"
    assert report["hard_findings"] >= 1


# ---- routing collisions: near-duplicate descriptions pair, unrelated does not ----
# Scores below are what this corpus actually produces with upstream's weighting
# (name tokens 2x + description); they were measured here, not assumed.


def test_collision_pair_detected_and_unrelated_skill_clear(tmp_path):
    write_skill(
        tmp_path / "video",
        "hyperframes-video",
        "hyperframes-video",
        "HTML compositions rendered to deterministic MP4 video.",
    )
    write_skill(
        tmp_path / "video",
        "remotion-video",
        "remotion-video",
        "React compositions rendered to deterministic MP4 video.",
    )
    write_skill(
        tmp_path / "gis",
        "duckdb-querying",
        "duckdb-querying",
        "Use when querying parquet tables with SQL in a notebook session.",
    )
    out = tmp_path / "r.json"
    proc = run(tmp_path, "--quiet", "--json", str(out))
    report = json.loads(out.read_text(encoding="utf-8"))
    pair = [
        p
        for p in report["routing_pairs"]
        if {p["a"], p["b"]} == {"video/hyperframes-video", "video/remotion-video"}
    ]
    assert len(pair) == 1, report["routing_pairs"]
    # measured 0.598 here: warn band, not error -- the doubled name tokens are what keep
    # two same-prose skills from reading as duplicates, so this must NOT fail the run.
    assert 0.5 <= pair[0]["score"] < 0.75, pair
    assert report["hard_findings"] == 0 and proc.returncode == 0
    gis_involved = [p for p in report["routing_pairs"] if "duckdb" in json.dumps(p)]
    assert not gis_involved, f"unrelated skill paired: {gis_involved}"


def test_same_prose_different_name_crosses_error_threshold(tmp_path):
    # measured 0.8302 here: same trigger clause, one differing word, near-identical shape
    write_skill(
        tmp_path / "c",
        "same-a",
        "same-a",
        "Use when rendering HTML compositions to MP4 video deterministically.",
    )
    write_skill(
        tmp_path / "c",
        "same-b",
        "same-b",
        "Use when rendering React compositions to MP4 video deterministically.",
    )
    out = tmp_path / "r.json"
    proc = run(tmp_path, "--quiet", "--json", str(out))
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["routing_pairs"][0]["score"] >= 0.75, report["routing_pairs"]
    assert report["hard_findings"] >= 1 and proc.returncode == 1


def test_lower_warn_reports_without_failing(tmp_path):
    write_skill(
        tmp_path / "cat",
        "alpha-tool",
        "alpha-tool",
        "Use when rendering video frames from HTML compositions deterministically.",
    )
    write_skill(
        tmp_path / "cat",
        "beta-other",
        "beta-other",
        "Use when auditing repository documentation links and headers.",
    )
    out = tmp_path / "r.json"
    proc = run(tmp_path, "--quiet", "--json", str(out), "--warn", "0.2")
    report = json.loads(out.read_text(encoding="utf-8"))
    assert all(p["score"] < 0.75 for p in report["routing_pairs"]), report["routing_pairs"]
    assert proc.returncode == 0


# ---- probe ranking + informational counters ----


def test_probe_ranks_matching_skill_first(tmp_path):
    write_skill(
        tmp_path / "cat",
        "video-render",
        "video-render",
        "Use when rendering HTML compositions to MP4 video.",
    )
    write_skill(
        tmp_path / "cat",
        "csv-import",
        "csv-import",
        "Use when importing CSV files into a spreadsheet report.",
    )
    proc = run(tmp_path, "--probe", "render my composition to mp4")
    assert proc.returncode == 0
    rows = [row for row in proc.stdout.splitlines() if row.strip().startswith("0.")]
    assert rows and "video-render" in rows[0], proc.stdout


def test_informational_counters_report_but_do_not_fail(tmp_path):
    # noun-phrase description + non-spec top-level keys: informational only
    write_skill(
        tmp_path / "cat",
        "plain-skill",
        "plain-skill",
        "Query parquet tables ad-hoc with SQL.",
        extra_fm="version: 1.0.0\nauthor: t\n",
    )
    out = tmp_path / "r.json"
    proc = run(tmp_path, "--quiet", "--json", str(out))
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["C3_no_trigger_clause"] == ["cat/plain-skill"]
    assert report["C4_non_spec_keys"].get("version") == 1
    assert "description" not in report["C4_non_spec_keys"]
    assert proc.returncode == 0


def test_empty_supporting_subdir_is_listed(tmp_path):
    write_skill(
        tmp_path / "cat",
        "with-empty",
        "with-empty",
        "Use when doing the thing.",
        subdirs=("references",),
    )
    out = tmp_path / "r.json"
    proc = run(tmp_path, "--quiet", "--json", str(out))
    report = json.loads(out.read_text(encoding="utf-8"))
    assert {"skill": "cat/with-empty", "dir": "references"} in report["C5_empty_subdirs"]
    assert proc.returncode == 0
