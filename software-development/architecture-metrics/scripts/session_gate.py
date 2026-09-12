#!/usr/bin/env python3
"""Session quality gate: save an architectural baseline before an agent session,
compare after — catches silent structural degradation (sentrux `gate` workflow).

Implements sentrux/sentrux (MIT) ArchBaseline/ArchDiff rules verbatim in spirit,
using architecture_metrics.py as the scan engine (subprocess --json):
  - quality signal drop > SIGNAL_DROP points   (sentrux: delta < -0.02 on a [0,1] scale; ours is 0–100)
  - SDP coupling score rise > COUPLING_RISE    (sentrux: +0.05)
  - circular-dependency count increased        (any increase = violation)
  - god-file count increased                   (any increase = violation)
  - complex-function (CC>15) count increased   (any increase = violation)
degraded = signal drop OR any violation — exit 0 pass / 1 degraded, CI-friendly.

Usage:
  python session_gate.py save  <project-dir> [--baseline PATH]   # before agent writes code
  python session_gate.py check <project-dir> [--baseline PATH]   # after; prints diff + violations
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

AM = str(Path(__file__).with_name("architecture_metrics.py"))
SIGNAL_DROP = 2.0      # points on the 0–100 composite (sentrux: 0.02 on [0,1])
COUPLING_RISE = 0.05   # sentrux ArchDiff threshold


def scan(root):
    r = subprocess.run([sys.executable, AM, str(root), "--json"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"scan failed:\n{r.stderr.strip()}")
    return json.loads(r.stdout)


def save(project, baseline):
    snap = scan(project)
    doc = {"saved_at": datetime.now(timezone.utc).isoformat(), "project": str(project),
           **{k: snap[k] for k in ("quality_signal", "sdp_coupling_score", "cycle_count",
                                   "complex_functions_gt15")},
           "god_file_count": len(snap["god_files"]),
           "modules": snap["modules"], "edges": snap["edges"]}
    baseline.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"Baseline saved — {baseline}")
    print(f"  signal={doc['quality_signal']} coupling={doc['sdp_coupling_score']} "
          f"cycles={doc['cycle_count']} god_files={doc['god_file_count']} "
          f"complex_fns={doc['complex_functions_gt15']}")


def check(project, baseline):
    if not baseline.exists():
        raise SystemExit(f"No baseline at {baseline} — run `session_gate.py save` first.")
    base = json.loads(baseline.read_text(encoding="utf-8"))
    cur = scan(project)

    violations = []
    delta = round(cur["quality_signal"] - base["quality_signal"], 2)
    if delta < -SIGNAL_DROP:
        violations.append(f"Quality signal dropped: {base['quality_signal']} → "
                          f"{cur['quality_signal']} ({delta:+.1f})")
    if cur["sdp_coupling_score"] > base["sdp_coupling_score"] + COUPLING_RISE:
        violations.append("Coupling degraded: "
                          f"{base['sdp_coupling_score']:.3f} → {cur['sdp_coupling_score']:.3f}")
    if cur["cycle_count"] > base["cycle_count"]:
        violations.append(f"Cycles increased: {base['cycle_count']} → {cur['cycle_count']}")
    gf = len(cur["god_files"])
    if gf > base.get("god_file_count", 0):
        violations.append(f"God files increased: {base.get('god_file_count', 0)} → {gf}")
    cf = cur["complex_functions_gt15"]
    if cf > base.get("complex_functions_gt15", 0):
        violations.append(f"Complex functions (CC>15) increased: "
                          f"{base.get('complex_functions_gt15', 0)} → {cf}")

    degraded = delta < -SIGNAL_DROP or bool(violations)
    print("Session gate — " + str(project))
    print(f"  signal: {base['quality_signal']} → {cur['quality_signal']} ({delta:+.1f})")
    print(f"  coupling: {base['sdp_coupling_score']:.3f} → {cur['sdp_coupling_score']:.3f}")
    print(f"  cycles: {base['cycle_count']} → {cur['cycle_count']} | "
          f"god files: {base.get('god_file_count', '?')} → {gf} | complex fns: "
          f"{base.get('complex_functions_gt15', '?')} → {cf}")
    if violations:
        print("  VIOLATIONS:")
        for v in violations:
            print(f"   - {v}")
        print(f"RESULT: DEGRADED — architecture got worse during this session")
    else:
        print("RESULT: PASS — no structural degradation detected")
    return 1 if degraded else 0


def main():
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    baseline_arg = None
    for i, a in enumerate(sys.argv):
        if a == "--baseline":
            baseline_arg = Path(sys.argv[i + 1])
    cmd = sys.argv[1]
    project = Path(args[0]).resolve()
    baseline = baseline_arg or (project / ".sentrux-baseline.json")
    if cmd == "save":
        save(project, baseline)
    elif cmd == "check":
        sys.exit(check(project, baseline))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
