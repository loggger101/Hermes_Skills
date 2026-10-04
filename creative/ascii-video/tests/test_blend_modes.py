"""Run the blend-mode table that references/shaders.md teaches, on real arrays.

The table is pulled out of the doc, so editing the doc re-tests the doc. It shipped broken once:
two entries were bare comments (the dict did not parse), and `hard_mix`, `lighten` and `darken`
used scalar `if` / `max` / `min`, which raise on the float32 canvases `blend_canvas` feeds them.

Needs numpy; skips cleanly without it.
"""

import re
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")

SHADERS_MD = Path(__file__).resolve().parents[1] / "references" / "shaders.md"


def load():
    text = SHADERS_MD.read_bytes().decode("utf-8").replace("\r\n", "\n")
    blocks = re.findall(r"```python\n(.*?)```", text, flags=re.S)
    table = [b for b in blocks if "BLEND_MODES = {" in b]
    usage = [b for b in blocks if "def blend_canvas" in b]
    assert len(table) == 1 and len(usage) == 1
    ns = {"np": np}
    exec(table[0], ns)
    exec(usage[0].split("# Multi-layer compositing")[0], ns)  # the def only, not the example calls
    return ns["BLEND_MODES"], ns["blend_canvas"]


BLEND_MODES, blend_canvas = load()
MODES = sorted(BLEND_MODES)

# 0 and 1 are where dodge/burn divide by zero, so the edges are part of every sweep
EDGE = np.array([0.0, 0.25, 0.5, 0.75, 1.0], dtype=np.float32)
A, B = (g.astype(np.float32) for g in np.meshgrid(EDGE, EDGE))


@pytest.mark.parametrize("mode", MODES)
def test_every_mode_is_array_safe_and_finite_on_the_edges(mode):
    with np.errstate(all="raise"):
        out = BLEND_MODES[mode](A, B)
    assert np.shape(out) == A.shape
    assert np.isfinite(out).all()


@pytest.mark.parametrize("mode", MODES)
def test_every_mode_runs_through_blend_canvas_on_uint8(mode):
    rng = np.random.default_rng(0)
    base = rng.integers(0, 256, (6, 5, 3), dtype=np.uint8)
    top = rng.integers(0, 256, (6, 5, 3), dtype=np.uint8)
    top[0, 0], base[0, 0] = 0, 255  # extremes in the mix
    top[1, 1], base[1, 1] = 255, 0
    out = blend_canvas(base, top, mode, 0.7)
    assert out.dtype == np.uint8 and out.shape == base.shape


def test_known_values():
    f = lambda m, a, b: float(BLEND_MODES[m](np.float32(a), np.float32(b)))  # noqa: E731
    assert f("overlay", 0.25, 0.5) == pytest.approx(0.25)  # a < 0.5: 2ab
    assert f("overlay", 0.75, 0.5) == pytest.approx(0.75)  # a >= 0.5: 1 - 2(1-a)(1-b)
    assert f("hard_mix", 0.6, 0.5) == 1.0 and f("hard_mix", 0.2, 0.3) == 0.0
    assert f("lighten", 0.2, 0.7) == pytest.approx(0.7) and f("darken", 0.2, 0.7) == pytest.approx(0.2)
    assert f("pin_light", 0.5, 0.25) == pytest.approx(0.5)  # b < 0.5: min(a, 2b)
    assert f("pin_light", 0.5, 0.75) == pytest.approx(0.5)  # b >= 0.5: max(a, 2b-1)
    assert f("vividlight", 0.5, 0.25) == pytest.approx(0.0)  # burn branch
    assert f("vividlight", 0.25, 0.75) == pytest.approx(0.5)  # dodge branch


def test_hardlight_is_overlay_with_the_arguments_swapped():
    assert np.allclose(BLEND_MODES["hardlight"](A, B), BLEND_MODES["overlay"](B, A))


def test_normal_and_opacity():
    rng = np.random.default_rng(1)
    base = rng.integers(0, 256, (4, 4, 3), dtype=np.uint8)
    top = rng.integers(0, 256, (4, 4, 3), dtype=np.uint8)
    assert np.array_equal(blend_canvas(base, top, "normal", 1.0), top)
    assert np.array_equal(blend_canvas(base, top, "normal", 0.0), base)
    mid = blend_canvas(base, top, "normal", 0.5).astype(int)
    assert np.abs(mid - (base.astype(int) + top.astype(int)) / 2).max() <= 1
