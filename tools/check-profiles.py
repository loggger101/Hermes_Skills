#!/usr/bin/env python3
"""Check profile skills sync status."""
import os
from pathlib import Path

HERMES_HOME = Path(os.environ.get('HERMES_HOME', str(Path.home() / '.hermes')))
LOCAL_PROFILES = HERMES_HOME / 'profiles'
REPO = Path(__file__).resolve().parents[1]


def norm(p):
    return str(p).replace('\\', '/')


# Get all profile skill MD files locally
local_md = set()
for profile_dir in LOCAL_PROFILES.iterdir():
    if not profile_dir.is_dir() or profile_dir.name.startswith('.'):
        continue
    skills_dir = profile_dir / 'skills'
    if skills_dir.exists():
        for skill_path in skills_dir.rglob('SKILL.md'):
            rel = norm(skill_path.relative_to(skills_dir))
            local_md.add(rel)

    mem_dir = profile_dir / 'memories'
    if mem_dir.exists():
        for mem_path in mem_dir.rglob('*.md'):
            rel = norm(mem_path.relative_to(mem_dir))
            local_md.add(rel)

# Also check top-level memories
LOCAL_MEMORIES = HERMES_HOME / 'memories'
if LOCAL_MEMORIES.exists():
    for mem_path in LOCAL_MEMORIES.rglob('*.md'):
        rel = norm(mem_path.relative_to(LOCAL_MEMORIES))
        local_md.add(rel)

# Get all SKILL.md in repo (excluding runtime dirs)
repo_md = set()
skip_dirs = {'.git', '.hermes', 'profiles-export', 'memories-export', 'tools', 'profile'}
for path in REPO.rglob('SKILL.md'):
    p = str(path)
    if any(d in p for d in skip_dirs):
        continue
    rel = path.relative_to(REPO)
    parts = rel.parts
    if len(parts) >= 2:
        repo_md.add(norm('/'.join(parts)))

# Compare
local_only = local_md - repo_md
repo_only = repo_md - local_md

print(f'Profile skill paths in local env: {len(local_md)}')
print(f'Profile skill paths in repo: {len(repo_md)}')
print(f'In local but not repo: {len(local_only)}')
print(f'In repo but not local: {len(repo_only)}')

if local_only:
    for f in sorted(local_only)[:10]:
        print(f'  local-only: {f}')
    if len(local_only) > 10:
        print(f'  ... +{len(local_only)-10} more')

if repo_only:
    for f in sorted(repo_only)[:10]:
        print(f'  repo-only: {f}')
    if len(repo_only) > 10:
        print(f'  ... +{len(repo_only)-10} more')

# Also check if profiles-export exists (sync output)
export_dir = REPO / 'profiles-export'
if export_dir.exists():
    export_count = len(list(export_dir.rglob('SKILL.md')))
    print(f'\nprofiles-export/ exists: {export_count} SKILL.md files (should be gitignored)')
else:
    print(f'\nprofiles-export/: does not exist (clean)')
