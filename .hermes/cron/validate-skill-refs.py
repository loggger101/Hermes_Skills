#!/usr/bin/env python3
"""Lightweight JSON + skill-ref validator (no_agent-compatible)."""
import json, os, sys
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JOBS_DIR = os.path.join(BASE, '.hermes', 'cron', 'active')
SKIP = ('/.git/', '/.hermes/cron/', 'profiles-export/', 'memories-export/', '/memories/')

valid = {}
for path, dirs, files in os.walk(BASE):
    if any(s in path.replace('\\', '/') for s in SKIP):
        continue
    if 'SKILL.md' in files:
        rel = os.path.relpath(path, BASE).replace('\\', '/')
        nm = '?'
        with open(os.path.join(path, 'SKILL.md'), encoding='utf-8') as f:
            for line in f:
                if line.startswith('name:'):
                    nm = line.split(':', 1)[1].strip()
                    break
        valid[rel] = nm

ok = True
for job in sorted(os.listdir(JOBS_DIR)):
    if not job.endswith('.json'):
        continue
    fp = os.path.join(JOBS_DIR, job)
    with open(fp, encoding='utf-8') as f:
        data = json.load(f)  # raises if invalid
    skills = data.get('skills', {})
    loaded = skills.get('loaded', skills) if isinstance(skills, dict) else skills
    if isinstance(loaded, str):
        loaded = [loaded]
    for s in loaded:
        sid = s if isinstance(s, str) else s.get('id', '?')
        if sid not in valid:
            print(f'  BROKEN: {job} -> {sid}')
            ok = False
        else:
            print(f'  OK:     {job} -> {sid} (name={valid[sid]})')
print(f'\n{"ALL OK" if ok else "ISSUES"} | valid_skills={len(valid)}')
sys.exit(0 if ok else 1)
