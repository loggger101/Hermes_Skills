"""scripts/self_check.py: every shipped example passes, and each rule fails on a planted
defect in a known-good example (a checker that never fails proves nothing)."""

import re
import subprocess
import sys
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts" / "self_check.py"
ASSETS = SKILL / "assets"
STATIC = ASSETS / "example-architecture-dark.html"
MOTION = ASSETS / "example-queue-animated.html"


def check(*paths):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, paths)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=300,
    )
    return proc.returncode, proc.stdout


def test_every_shipped_example_passes():
    examples = sorted(ASSETS.glob("example-*.html"))
    assert len(examples) >= 150, "the example corpus shrank: mis-rooted test?"
    rc, out = check(*examples)
    assert rc == 0, "\n".join(ln for ln in out.splitlines() if not ln.startswith("OK"))
    assert out.count("\nOK ") + out.startswith("OK ") == len(examples)


def planted(tmp_path, base, old, new, count=1):
    text = base.read_text(encoding="utf-8")
    assert old in text, f"anchor {old!r} not in {base.name}: the fixture drifted"
    p = tmp_path / base.name
    p.write_text(text.replace(old, new, count), encoding="utf-8")
    return p


STATIC_DEFECTS = [
    ('role="img"', 'role="presentation"', "needs role=img"),
    (
        'aria-labelledby="architecture-dark-title architecture-dark-desc"',
        'aria-labelledby="architecture-dark-desc architecture-dark-title"',
        "aria-labelledby must name title then desc",
    ),
    ('id="architecture-dark-title"', 'id="title"', "must be diagram-prefixed"),
    ("</body>", '<img src="https://evil.example/x.png"></body>', "remote reference on <img>"),
    ("</body>", '<a href="javascript:alert(1)">x</a></body>', "executable URL on <a>"),
    ("</body>", "<script>alert(1)</script></body>", "must carry only the canonical"),
    (
        "https://fonts.googleapis.com/css2",
        "https://cdn.example.com/css2",
        "remote stylesheet is not the approved Google Fonts",
    ),
]


@pytest.mark.parametrize(
    "old, new, needle", STATIC_DEFECTS, ids=[d[2][:30] for d in STATIC_DEFECTS]
)
def test_static_rules_fail_on_planted_defects(tmp_path, old, new, needle):
    rc, out = check(planted(tmp_path, STATIC, old, new))
    assert rc == 1 and needle in out, out


def test_motion_example_passes_and_its_controller_is_pinned(tmp_path):
    assert check(MOTION)[0] == 0
    text = MOTION.read_text(encoding="utf-8")
    body = re.search(r"<script data-diagram-controls>(.*?)</script>", text, re.S).group(1)
    tweaked = body.replace("replay", "replay ", 1)
    rc, out = check(planted(tmp_path, MOTION, body, tweaked))
    assert rc == 1 and "must exactly match the controller" in out


def test_motion_mode_and_step_count_are_validated(tmp_path):
    mode = re.search(r'data-motion-mode="(\w+)"', MOTION.read_text(encoding="utf-8")).group(0)
    rc, out = check(planted(tmp_path, MOTION, mode, 'data-motion-mode="spin"'))
    assert rc == 1 and "data-motion-mode must be one of" in out


def test_no_svg_and_unreadable_file_fail(tmp_path):
    empty = tmp_path / "empty.html"
    empty.write_text("<!doctype html><title>x</title>", encoding="utf-8")
    missing = tmp_path / "missing.html"
    rc, out = check(empty, missing)
    assert rc == 1
    assert "needs at least one accessible" in out and f"FAIL {missing}" in out
