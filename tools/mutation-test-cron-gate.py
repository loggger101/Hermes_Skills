#!/usr/bin/env python3
"""Mutation self-test for the cron threshold-key verification (round-36).

Proves validate-cronjobs.py's new check is fail-loud, using fully hermetic temp
fixtures (the validator reads its jobs dir from CRON_JOBS_DIR; script paths still
resolve against this repo, so no repo file is ever touched):

  M1  phantom threshold key        -> validator MUST exit 1 with 'never emitted'
  M2  phantom report_template key  -> validator MUST exit 1 (same message)
  M3  unmodified real configs      -> validator MUST pass clean (no false positive)
  M4  --job <file> flag            -> single-job mode works; unknown name exits 1

Exit code = number of failed checks.
"""
import json, os, shutil, subprocess, sys, tempfile

if sys.version_info < (3, 8):
    raise SystemExit("[FATAL] needs Python 3.8+")
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VALIDATOR = os.path.join(REPO, ".hermes", "cron", "validate-cronjobs.py")
ACTIVE = os.path.join(REPO, ".hermes", "cron", "active")


def run_validator(jobs_dir, extra=()):
    env = dict(os.environ)
    env["CRON_JOBS_DIR"] = jobs_dir
    return subprocess.run(
        [sys.executable, VALIDATOR] + list(extra),
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=REPO, timeout=120, env=env)


def copy_real_configs(tmp):
    for f in sorted(os.listdir(ACTIVE)):
        if f.endswith(".json"):
            shutil.copy2(os.path.join(ACTIVE, f), os.path.join(tmp, f))


failures = []

# M1: phantom threshold key (the exact class that rotted sync's config)
tmp = tempfile.mkdtemp(prefix="cron-mut-")
try:
    copy_real_configs(tmp)
    p = os.path.join(tmp, "sync-hermes-skills.json")
    d = json.load(open(p, encoding="utf-8"))
    d["threshold"]["total_skills"] = 0  # audit emits skill_count; sync emits neither
    json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
    r = run_validator(tmp)
    if r.returncode == 0 or "never emitted" not in (r.stdout + r.stderr):
        failures.append("M1 phantom threshold key NOT caught")

    # M2: same key planted in report_template.summary instead of threshold
    d["threshold"].pop("total_skills", None)
    d.setdefault("report_template", {}).setdefault("summary", {})["total_skills"] = 0
    json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
    r = run_validator(tmp)
    if r.returncode == 0 or "never emitted" not in (r.stdout + r.stderr):
        failures.append("M2 phantom report_template key NOT caught")

    # M3: unmodified real configs must pass clean (no false positive from the new check)
    for f in os.listdir(tmp):
        if f.endswith(".json"):
            shutil.copy2(os.path.join(ACTIVE, f), os.path.join(tmp, f))
    r = run_validator(tmp)
    if r.returncode != 0:
        failures.append("M3 real configs FAIL clean check (false positive)")

    # M4a: --job single-file mode on a valid job passes and only checks that file
    r = run_validator(tmp, extra=["--job", "skill-audit.json"])
    if r.returncode != 0 or "sync-hermes-skills.json ===" in r.stdout:
        failures.append("M4a --job single-file mode misbehaved")

    # M4b: --job with an unknown name exits 1 (flag is real, not silently ignored)
    r = run_validator(tmp, extra=["--job", "does-not-exist.json"])
    if r.returncode == 0 or "--job" not in (r.stdout + r.stderr):
        failures.append("M4b --job unknown-name did not fail loudly")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

if failures:
    for f in failures:
        print(f"[FAIL] {f}")
    sys.exit(len(failures))
print("[OK] all 5 cron-gate mutations verified (M1-M4b): phantom keys caught, "
      "real configs clean, --job flag live")
