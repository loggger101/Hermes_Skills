#!/usr/bin/env python3
"""Mutation self-test for check-router-coverage.py (round-43).

A gate that has only ever been observed passing is indistinguishable from a gate
that cannot fail -- which is the very failure class the router gate was added to
catch. So this plants one mutation per check class in hermetic temp fixtures
(ROUTER_SCAN_ROOT redirects the gate's whole scan root; no repo file is touched)
and asserts the gate exits 1 with the right class tag:

  M1  routed skill removed from every lane      -> [A] unrouted
  M2  brand-new in-scope skill appears on disk  -> [A] unrouted  (the real rot class)
  M3  opt-out entry stripped of its reason      -> [C] no reason
  M4  opt-out entry names a non-existent skill  -> [B] phantom
  M5  skill both routed and opted out           -> [D] contradiction
  M6  hardcoded '160+ skills' reintroduced      -> [E] rotting count
  M7  unmutated fixture                         -> MUST pass (no false positive)
  M8  the real repo                             -> MUST pass (no false positive)

Exit code = number of failed checks (0 = gate proven fail-loud).
"""
import os, shutil, subprocess, sys, tempfile
from pathlib import Path

if sys.version_info < (3, 8):
    raise SystemExit("[FATAL] needs Python 3.8+")
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
GATE = REPO / "tools" / "check-router-coverage.py"

ROUTER_TMPL = """---
name: skill-flow-router
description: "Route any task through the right skill flow in this brain."
tags: [router]
---

# Skill Flow Router

## The main flow
1. Sharpen by interview -> `alpha-planner`, then debug with `beta-debug`.
{extra_lane}
## Deliberately not routed here

- `{optout_name}` {dash}{optout_reason}

## How to use this router in practice
1. Name the situation.
"""


def skill(tags):
    return "---\nname: x\ndescription: \"d\"\nmetadata:\n  hermes:\n    tags: [%s]\n---\n\n# X\n" % tags


def build(tmp, *, extra_lane="", optout_name="gamma-tool", optout_reason="stack-specific.",
          dash="— ", extra_skills=()):
    root = Path(tmp)
    for name, tags in [("alpha-planner", "planning"), ("beta-debug", "debugging"),
                       ("gamma-tool", "debugging"), ("delta-unrelated", "python")] + list(extra_skills):
        d = root / "software-development" / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text(skill(tags), encoding="utf-8")
    rd = root / "software-development" / "skill-flow-router"
    rd.mkdir(parents=True, exist_ok=True)
    (rd / "SKILL.md").write_text(
        ROUTER_TMPL.format(extra_lane=extra_lane, optout_name=optout_name,
                           dash=dash, optout_reason=optout_reason), encoding="utf-8")
    return root


def run(root):
    env = dict(os.environ, ROUTER_SCAN_ROOT=str(root))
    return subprocess.run([sys.executable, str(GATE)], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", cwd=str(REPO),
                          timeout=120, env=env)


failures = []


def expect_fail(label, tag, **kw):
    tmp = tempfile.mkdtemp(prefix="router-mut-")
    try:
        r = run(build(tmp, **kw))
        out = r.stdout + r.stderr
        if r.returncode == 0:
            failures.append(f"{label} NOT caught (gate passed)")
        elif tag not in out:
            failures.append(f"{label} caught but not as {tag}: {out.strip()[:120]}")
        else:
            print(f"  [OK] {label} -> {tag}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


print("=== mutation-test: router coverage gate ===")

# M1: alpha-planner routed nowhere (drop it from the lane sentence)
tmp = tempfile.mkdtemp(prefix="router-mut-")
try:
    root = build(tmp)
    rp = root / "software-development" / "skill-flow-router" / "SKILL.md"
    rp.write_text(rp.read_text(encoding="utf-8").replace("`alpha-planner`, then debug with ", ""),
                  encoding="utf-8")
    r = run(root)
    if r.returncode == 0 or "[A]" not in (r.stdout + r.stderr):
        failures.append("M1 routed-skill-removed NOT caught as [A]")
    else:
        print("  [OK] M1 routed skill removed -> [A]")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# M2: a new in-scope skill lands on disk, router never mentions it (the real rot class)
expect_fail("M2 new in-scope skill unrouted", "[A]",
            extra_skills=[("epsilon-newflow", "planning")])
# M3: opt-out with no reason
expect_fail("M3 opt-out without reason", "[C]", optout_reason="", dash="")
# M4: opt-out names a phantom skill
expect_fail("M4 opt-out phantom", "[B]", optout_name="zeta-does-not-exist")
# M5: gamma-tool both routed and opted out
expect_fail("M5 routed AND opted out", "[D]",
            extra_lane="2. Also try `gamma-tool` for containers.\n\n")
# M6: hardcoded catalog size returns
expect_fail("M6 hardcoded count", "[E]",
            extra_lane="This brain has 160+ skills.\n\n")

# M7: unmutated fixture must pass
tmp = tempfile.mkdtemp(prefix="router-mut-")
try:
    r = run(build(tmp))
    if r.returncode != 0:
        failures.append(f"M7 clean fixture FAILED (false positive): {(r.stdout+r.stderr).strip()[:160]}")
    else:
        print("  [OK] M7 clean fixture passes (no false positive)")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# M8: the real repo must pass
r = subprocess.run([sys.executable, str(GATE)], capture_output=True, text=True,
                   encoding="utf-8", errors="replace", cwd=str(REPO), timeout=120)
if r.returncode != 0:
    failures.append(f"M8 real repo FAILED: {(r.stdout+r.stderr).strip()[:160]}")
else:
    print("  [OK] M8 real repo passes clean")

print()
if failures:
    print(f"FAILED ({len(failures)}):")
    for f in failures:
        print("  " + f)
    sys.exit(len(failures))
print("ALL 8 MUTATIONS CAUGHT — router coverage gate verified fail-loud.")
sys.exit(0)
