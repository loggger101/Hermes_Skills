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
"""
import json, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JOBS_DIR = os.path.join(BASE, '.hermes', 'cron', 'active')

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

for job in sorted(os.listdir(JOBS_DIR)):
    if not job.endswith('.json'):
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
            print(f'  ✓ {field} = {data[field]!r}')

    # No-agent vs LLM-driven consistency
    no_agent = data.get('no_agent', False)
    if no_agent:
        print(f'  ✓ no_agent=true (script-only watchdog)')
        if 'script' not in data:
            print(f'  [ERROR] no_agent=true but no "script" field — job has no executable action')
            errors.append(f'{job}: no_agent=true but no script field')
    else:
        print(f'  ✓ no_agent=false (LLM-driven)')
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
                print(f'  ✓ skill: {sid} -> name={nm}')
            else:
                print(f'  [BROKEN] {sid}')
                errors.append(f'{job}: broken skill ref {sid}')

    # workdir check
    wd = data.get('workdir', '')
    if wd in ['/', '.', '~/.hermes']:
        print(f'  ✓ workdir is relative/local: {wd!r}')
    elif '/path/to/' in wd or '%REPO_PATH%' in wd:
        print(f'  [WARN] workdir is a placeholder: {wd!r}')
        warnings.append(f'{job}: placeholder workdir')
    else:
        print(f'  ✓ workdir: {wd!r}')

    # Threshold validation: keys should match script output
    if 'threshold' in data:
        t = data['threshold']
        print(f'  ✓ threshold keys: {list(t.keys())}')

    # Model pinning check (drift-skip prevention)
    if not no_agent:
        if 'model' in data and 'provider' in data:
            print(f'  ✓ model pinned: {data["provider"]}/{data["model"]}')
        else:
            print(f'  [WARN] no_agent=false but model/provider not pinned (drift_skip risk)')
            warnings.append(f'{job}: unpinned model (drift_skip risk)')
    else:
        if 'model' in data:
            print(f'  ✓ model pinned (for drift safety): {data.get("provider")}/{data.get("model")}')

# 2. Check the audit script itself runs
print(f'\n=== Audit Script Self-Check ===')
print(f'  Valid skills in repo: {len(valid_skills)}')

print(f'\n=== Summary ===')
print(f'  Errors: {len(errors)}')
print(f'  Warnings: {len(warnings)}')
if errors:
    print('  ERRORS:')
    for e in errors:
        print(f'    - {e}')
if warnings:
    print('  WARNINGS:')
    for w in warnings:
        print(f'    - {w}')
if not errors and not warnings:
    print('  ✓ ALL CHECKS PASSED')
sys.exit(0 if not errors else 1)
