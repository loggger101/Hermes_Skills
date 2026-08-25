#!/usr/bin/env python3
"""Check for content differences between profile-local and repo skills."""
import os, hashlib
from pathlib import Path

HERMES_HOME = Path(os.environ.get('HERMES_HOME', str(Path.home() / '.hermes')))
LOCAL_SKILLS = HERMES_HOME / 'skills'
LOCAL_PROFILES = HERMES_HOME / 'profiles'
REPO = Path(__file__).resolve().parents[1]


def file_hash(path):
    return hashlib.md5(path.read_bytes()).hexdigest()


def norm(p):
    return str(p).replace('\\', '/')


# Compare local skills vs repo files
differ = []
local_only = []
repo_only = []
same = 0

# Get repo SKILL.md files
repo_files = {}
skip_dirs = {'.git', '.hermes', 'profiles-export', 'memories-export', 'tools', 'profile'}
for path in REPO.rglob('SKILL.md'):
    p = str(path)
    if any(d in p for d in skip_dirs):
        continue
    rel = norm(path.relative_to(REPO))
    repo_files[rel] = path

# Get local SKILL.md files
local_files = {}
for path in LOCAL_SKILLS.rglob('SKILL.md'):
    p = str(path)
    if any(d in p for d in skip_dirs):
        continue
    rel = norm(path.relative_to(LOCAL_SKILLS))
    local_files[rel] = path

# Also check local memories
local_mem = LOCAL_SKILLS.parent / 'memories'
if local_mem.exists():
    for path in local_mem.rglob('*.md'):
        rel = norm(path.relative_to(local_mem))
        local_files['memories/' + rel] = path

# Also check profile skills
for profile_dir in LOCAL_PROFILES.iterdir():
    if not profile_dir.is_dir() or profile_dir.name.startswith('.'):
        continue
    for path in profile_dir.rglob('SKILL.md'):
        rel = norm(path.relative_to(profile_dir))
        if rel not in local_files:  # Only track if not already in main skills
            pass  # Profile-specific skills don't have repo equivalents

all_local = set(local_files.keys())
all_repo = set(repo_files.keys())

for f in sorted(all_local | all_repo):
    if f in local_files and f in repo_files:
        lh = file_hash(local_files[f])
        rh = file_hash(repo_files[f])
        if lh != rh:
            differ.append(f)
        else:
            same += 1
    elif f in local_files:
        local_only.append(f)
    elif f in repo_files:
        repo_only.append(f)

print(f'Same content:      {same}')
print(f'Different content: {len(differ)}')
print(f'Local-only:        {len(local_only)}')
print(f'Repo-only:         {len(repo_only)}')

if differ:
    print('\nDiffering files (first 10):')
    for f in differ[:10]:
        print(f'  {f}')
        print(f'    local: {file_hash(local_files[f])}  repo: {file_hash(repo_files[f])}')
    if len(differ) > 10:
        print(f'  ... +{len(differ)-10} more')

if local_only:
    print(f'\nLocal-only (first 5): {local_only[:5]}')

if repo_only:
    print(f'\nRepo-only (first 5): {repo_only[:5]}')
