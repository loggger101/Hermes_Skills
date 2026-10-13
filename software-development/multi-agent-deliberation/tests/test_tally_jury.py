"""scripts/tally_jury.py: the verdict cascade, and bad input refused instead of defaulted."""

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "tally_jury.py"


def tally(data):
    """Run the script on a jury dict; return (rc, parsed RESULT json or None, stderr)."""
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps(data),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    result = None
    if proc.returncode == 0:
        result = json.loads(proc.stdout[proc.stdout.rindex("\n{") :])
    return proc.returncode, result, proc.stderr


def juror(i, c1, k1, c2, k2, grade="B", why=""):
    return {
        "id": f"j{i}",
        "initial_choice": c1,
        "initial_confidence": k1,
        "final_choice": c2,
        "final_confidence": k2,
        "flip_reason": why,
        "evidence_grade": grade,
    }


@pytest.fixture
def example():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--example"], capture_output=True, text=True, timeout=60
    )
    assert proc.returncode == 0
    return json.loads(proc.stdout)


def test_example_verdict(example):
    rc, res, _ = tally(example)
    assert rc == 0
    assert res["winner"] == "tune" and res["confidence"] == "HIGH"
    assert res["aggregate_source"] == "final" and res["bandwagon_suspect"] is False


def test_unjustified_flips_fall_back_to_round_one():
    jurors = [
        juror(1, "A", 80, "B", 80),  # flips with no reason
        juror(2, "A", 70, "B", 70),  # flips with no reason
        juror(3, "B", 60, "B", 60),
    ]
    rc, res, _ = tally({"diversity": "high", "jurors": jurors})
    assert rc == 0
    assert res["bandwagon_suspect"] is True and res["aggregate_source"] == "round1_independent"
    assert res["winner"] == "A" and res["confidence"] == "LOW"


def test_weak_evidence_caps_confidence():
    jurors = [juror(i, "A", 90, "A", 90, grade="D") for i in range(3)]
    rc, res, _ = tally({"diversity": "high", "jurors": jurors})
    assert rc == 0 and res["confidence"] == "LOW" and "evidence mostly grade D" in res["caps"]


def test_low_diversity_drops_a_tier():
    jurors = [juror(i, "A", 90, "A", 90, grade="A") for i in range(3)]
    _, high, _ = tally({"diversity": "high", "jurors": jurors})
    _, low, _ = tally({"diversity": "low", "jurors": jurors})
    assert (high["confidence"], low["confidence"]) == ("HIGH", "MEDIUM")


def test_near_tie_breaks_on_evidence():
    jurors = [
        juror(1, "A", 50, "A", 50, grade="D"),
        juror(2, "B", 49, "B", 49, grade="A"),
        juror(3, "C", 10, "C", 10, grade="B"),
    ]
    rc, res, _ = tally({"diversity": "high", "jurors": jurors})
    assert rc == 0 and res["tie_flag"] is True and res["winner"] == "B"


# ---------------------------------------------- input the port used to default silently
@pytest.mark.parametrize(
    "mutate, needle",
    [
        (lambda d: d["jurors"][0].pop("evidence_grade"), "missing field 'evidence_grade'"),
        (lambda d: d["jurors"][0].update(evidence_grade="E"), "must be A, B, C or D"),
        (lambda d: d["jurors"][0].update(final_confidence=None), "must be a number 0..100"),
        (lambda d: d["jurors"][0].update(final_confidence="80"), "must be a number 0..100"),
        (lambda d: d["jurors"][0].update(initial_confidence=101), "must be a number 0..100"),
        (lambda d: d["jurors"][0].update(initial_confidence=True), "must be a number 0..100"),
        (lambda d: d.update(diversity="lo"), "must be high, medium or low"),
        (lambda d: d.update(jurors=d["jurors"][:2]), "need at least 3 jurors"),
    ],
)
def test_bad_input_is_refused(example, mutate, needle):
    data = copy.deepcopy(example)
    mutate(data)
    rc, _, err = tally(data)
    assert rc == 2 and needle in err, err


def test_lowercase_grade_is_accepted(example):
    data = copy.deepcopy(example)
    for j in data["jurors"]:
        j["evidence_grade"] = j["evidence_grade"].lower()
    rc, res, _ = tally(data)
    assert rc == 0 and res["winner"] == "tune"


def test_empty_and_malformed_input():
    for raw in ("", "{not json"):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT)], input=raw, capture_output=True, text=True, timeout=60
        )
        assert proc.returncode == 2 and proc.stderr.startswith("ERROR")
