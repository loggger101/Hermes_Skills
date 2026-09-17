#!/usr/bin/env python3
"""Validate cronjob JSON config files for structural correctness + cross-consistency.

Run this after ANY edit to `.hermes/cron/active/*.json` to catch:
  - Missing no_agent / enabled_toolsets fields (silently swallowed by JSON patches)
  - Broken skill references (path doesn't resolve to a real SKILL.md)
  - Threshold keys that don't match the script's JSON output
  - Workdir still pointing at placeholder paths
  - LLM-driven jobs missing their prompt body
  - no_agent=true jobs missing their script field

Usage:
  python .hermes/cron/validate-cronjobs.py
  python .hermes/cron/validate-cronjobs.py --job aspirecures-weekly.json   # single file

Threshold verification (round-36): for no_agent jobs whose script lives in THIS repo,
every key under "threshold" (and report_template.summary / actual_script_output.
summary_keys when present) must appear as a string literal somewhere in the script —
i.e. it is something the script can actually emit. A threshold key that matches nothing
is silently never evaluated by the cron system (always-pass), so this is an ERROR, not
a warning: phantom keys rotted sync-hermes-skills.json for months before round-35 hit
them in a live run. Jobs whose script is outside this repo are SKIPped with a label —
their contract must be verified where the script lives.

Set CRON_JOBS_DIR to point at an alternate jobs directory (used by the mutation self-test).
"""
import ast, json, os, sys

if sys.version_info < (3, 8):
    raise SystemExit(
        "[FATAL] this validator needs Python 3.8+, got "
        + sys.version.split()[0] + " at " + (sys.executable or "<unknown interpreter>")
    )

# Windows consoles default to cp1252: printing any non-ASCII byte (a job description's
# em dash, a skill name) raises UnicodeEncodeError and aborts validation mid-file.
# Force UTF-8 on the way out so a config is never left unvalidated by an encoding error.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JOBS_DIR = os.environ.get("CRON_JOBS_DIR") or os.path.join(BASE, '.hermes', 'cron', 'active')

# --job <name.json>: documented in the usage block but never implemented until round-36.
ONLY_JOB = None
for _i, _arg in enumerate(sys.argv):
    if _arg == '--job' and _i + 1 < len(sys.argv):
        ONLY_JOB = sys.argv[_i + 1]

def script_string_literals(script_path):
    """Every string literal the script source contains (AST walk) — i.e. every key name it
    could possibly emit in its JSON output. Returns None if the file is missing/unparseable."""
    try:
        with open(script_path, encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=script_path)
    except (OSError, SyntaxError):
        return None
    lits = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            lits.add(node.value)
    return lits


def verify_threshold_keys(job_name, data, script_literals_cache):
    """Round-36: every threshold key must be a string the script actually emits.

    Returns (errors, skips). A key absent from the script's literal set is silently never
    evaluated by the cron system — an always-pass phantom gate."""
    errs = []
    skips = []
    if not data.get('no_agent'):
        return errs, skips  # LLM-driven jobs have no machine-evaluated threshold contract
    script = data.get('script') or ''
    if not script:
        return errs, skips  # 'no script field' is already an error elsewhere
    rel = script.replace('\\', '/').lstrip('./')
    script_path = os.path.join(BASE, *rel.split('/'))
    if not os.path.isfile(script_path):
        skips.append(f'{job_name}: threshold NOT verified — {script} not in this repo (verify where it lives)')
        return errs, skips
    if rel not in script_literals_cache:
        script_literals_cache[rel] = script_string_literals(script_path)
    lits = script_literals_cache[rel]
    if lits is None:
        skips.append(f'{job_name}: threshold NOT verified — {script} unparseable')
        return errs, skips

    def check_key(key):
        # a key 'matches' if it appears verbatim as a literal (dict keys / .get() args are
        # all string constants in these scripts) or is built from one ('summary[' + field).
        if key not in lits:
            errs.append(f'{job_name}: threshold key {key!r} never emitted by {script}')

    t = data.get('threshold')
    if isinstance(t, dict):
        for k in t.keys():
            check_key(k)
    rt = (data.get('report_template') or {}).get('summary')
    if isinstance(rt, dict):
        for k in rt.keys():
            check_key(k)
    aso = data.get('actual_script_output') or {}
    sk = aso.get('summary_keys')
    if isinstance(sk, list):
        for k in sk:
            check_key(k)
    return errs, skips


# ── Load all valid skills ──
valid_skills = {}
for path, dirs, files in os.walk(BASE):
    np = path.replace('\\', '/')
    if any(s in np for s in ['/.git/', '/.hermes/cron/', 'profiles-export/',
                              'memories-export/', '/memories/', '/tools/']):
        continue
    if 'SKILL.md' in files:
        rel = os.path.relpath(path, BASE).replace('\\', '/')
        nm = None
        with open(os.path.join(path, 'SKILL.md'), encoding='utf-8') as f:
            for line in f:
                if line.startswith('name:'):
                    nm = line.split(':', 1)[1].strip()
                    break
        if nm:
            valid_skills[rel] = nm

errors = []
warnings = []
skips = []
script_literals_cache = {}

job_files = sorted(os.listdir(JOBS_DIR)) if os.path.isdir(JOBS_DIR) else []
if ONLY_JOB and not any(f == ONLY_JOB for f in job_files):
    print(f'[FAIL] --job {ONLY_JOB}: no such file in {JOBS_DIR}')
    sys.exit(1)

for job in job_files:
    if not job.endswith('.json'):
        continue
    if ONLY_JOB and job != ONLY_JOB:
        continue
    fp = os.path.join(JOBS_DIR, job)
    with open(fp, encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f'[FAIL] {job}: JSON error: {e}')
            errors.append(f'{job}: JSON error')
            continue

    print(f'\n=== {job} ===')

    # Required fields
    for field in ['name', 'description', 'schedule', 'workdir', 'deliver', 'continuity']:
        if field not in data:
            print(f'  [MISSING] {field}')
            errors.append(f'{job}: missing {field}')
        else:
            print(f'  [OK] {field} = {data[field]!r}')

    # No-agent vs LLM-driven consistency
    no_agent = data.get('no_agent', False)
    if no_agent:
        print(f'  [OK] no_agent=true (script-only watchdog)')
        if 'script' not in data:
            print(f'  [ERROR] no_agent=true but no "script" field — job has no executable action')
            errors.append(f'{job}: no_agent=true but no script field')
    else:
        print(f'  [OK] no_agent=false (LLM-driven)')
        if 'prompt' not in data:
            print(f'  [WARN] no_agent=false but no "prompt" field — agent has no instructions')
            warnings.append(f'{job}: no_agent=false without prompt')

    # Skills validation
    skills = data.get('skills', {})
    loaded = skills.get('loaded', skills) if isinstance(skills, dict) else skills
    if isinstance(loaded, str):
        loaded = [loaded]

    if not loaded:
        print(f'  (no skills array — script-only job)')
    else:
        for s in loaded:
            sid = s if isinstance(s, str) else s.get('id', '?')
            nm = valid_skills.get(sid)
            if nm:
                print(f'  [OK] skill: {sid} -> name={nm}')
            else:
                print(f'  [BROKEN] {sid}')
                errors.append(f'{job}: broken skill ref {sid}')

    # workdir check
    wd = data.get('workdir', '')
    if wd in ['/', '.', '~/.hermes']:
        print(f'  [OK] workdir is relative/local: {wd!r}')
    elif '/path/to/' in wd or '%REPO_PATH%' in wd:
        print(f'  [WARN] workdir is a placeholder: {wd!r}')
        warnings.append(f'{job}: placeholder workdir')
    else:
        print(f'  [OK] workdir: {wd!r}')

    # Threshold validation (round-36): keys must match what the script actually emits —
    # a phantom key is silently never evaluated by the cron system (always-pass).
    t_errs, t_skips = verify_threshold_keys(job, data, script_literals_cache)
    if 'threshold' in data:
        print(f'  [OK] threshold keys: {list(data["threshold"].keys())}')
    errors.extend(t_errs)
    skips.extend(t_skips)

    # Model pinning check (drift-skip prevention)
    if not no_agent:
        if 'model' in data and 'provider' in data:
            print(f'  [OK] model pinned: {data["provider"]}/{data["model"]}')
        else:
            print(f'  [WARN] no_agent=false but model/provider not pinned (drift_skip risk)')
            warnings.append(f'{job}: unpinned model (drift_skip risk)')
    else:
        if 'model' in data:
            print(f'  [OK] model pinned (for drift safety): {data.get("provider")}/{data.get("model")}')

# 2. Check the audit script itself runs
print(f'\n=== Audit Script Self-Check ===')
print(f'  Valid skills in repo: {len(valid_skills)}')

print(f'\n=== Summary ===')
print(f'  Errors: {len(errors)}')
print(f'  Warnings: {len(warnings)}')
if skips:
    print(f'  Skipped (by design): {len(skips)}')
    for s in skips:
        print(f'    - SKIP {s}')
if errors:
    print('  ERRORS:')
    for e in errors:
        print(f'    - {e}')
if warnings:
    print('  WARNINGS:')
    for w in warnings:
        print(f'    - {w}')
if not errors and not warnings:
    print('  [OK] ALL CHECKS PASSED')
sys.exit(0 if not errors else 1)
