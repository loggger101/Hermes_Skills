#!/usr/bin/env python3
"""Mutation test for audit-skills.scan_repo_for_secrets — the secret scan tests itself.

Same philosophy as mutation-test-doc-gate.py (round-20c): a gate that cannot be
wrong is one whose failure modes are exercised on purpose. This script builds a
temp fixture with ONE planted secret per pattern class plus negative controls,
points audit-skills' REPO_ROOT at it, and asserts:

  * every positive control fires (a dead regex or disabled scan would pass silently)
  * no negative control fires (env reads / placeholders must not be flagged)
  * an ORPHANED script dir with no SKILL.md is still scanned — the exact gap found
    when wiring this gate: a per-skill loop misses credentials committed in a
    directory that has no valid frontmatter, which is where they hide best.

If scan_repo_for_secrets gains a new pattern class, add its planted secret here —
an untested pattern is an unenforced one.

Run:  py tools/mutation-test-secret-gate.py     (also invoked by verify-all as a gate)
Exit 0 = every positive caught AND zero false positives; exit 1 otherwise. Stdlib only.
"""
import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

if sys.version_info < (3, 8):
    raise SystemExit(
        "[FATAL] this tool needs Python 3.8+, got "
        + sys.version.split()[0]
        + f" at {sys.executable or '<unknown interpreter>'}"
    )
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

_HERE = Path(__file__).resolve()
REPO = _HERE.parents[1]
if not (REPO / "tools" / "audit-skills.py").exists():
    REPO = Path(r"C:\Users\Owner\OneDrive\Documents\GitHub\Hermes_Skills")


def load_auditor():
    spec = importlib.util.spec_from_file_location("auditskills", REPO / "tools" / "audit-skills.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# One planted secret per pattern class. Shapes are valid but values are fake —
# they must match the REGEX, which is what we're testing (not real credentials).
POSITIVE_FILES = {
    "devops/fake-skill/scripts/aws_leak.py": 'KEY = "AKIAABCDEFGHIJKLMNOP"\n',
    "devops/fake-skill/scripts/gh_leak.py":  'TOKEN = "ghp_abcdefghijklmnopqrstuvwxyz0123456789AB"\n',
    "devops/fake-skill/scripts/oai_leak.py": 'SECRET = "sk-abcdefghijklmnopqrstuvwx"\n',
    "devops/fake-skill/scripts/slack_leak.py": 'SLACK = "xoxb-1234567890-abcdEFgh"\n',
    "devops/fake-skill/scripts/pem_leak.py":  'PEM = "-----BEGIN RSA PRIVATE KEY-----"\n',
    # secret_assignment: has digits, no placeholder marker, not an env read
    "devops/fake-skill/scripts/assign_leak.py": 'password = "s3cr3tvalue1234567890"\n',
}

# The orphan case: a script dir with NO SKILL.md at all. A per-skill scan loop
# never visits this; the repo-wide walk must.
ORPHAN_FILE = {
    "devops/orphan-dir/scripts/leak.py": 'AKIAQRSTUVWXYZ0123456789\n',
}

# Negative controls — each one LOOKS like it could match but MUST NOT fire:
NEGATIVE_FILES = {
    # env reads are the documented credential strategy for this repo's scripts
    "devops/fake-skill/scripts/env_ok.py": (
        'token = os.environ.get("MY_TOKEN")\n'
        'secret = getenv("S3CR3T", "")\n'
    ),
    # placeholder / example literals are teaching content, not credentials
    "devops/fake-skill/scripts/placeholder_ok.py": (
        'password = "your-password-here"\n'
        'api_key: "<paste-your-key>"\n'
        'token = "***REDACTED***"\n'
        'secret = "short123"  # under the 8-char floor\n'
    ),
}


def build_fixture(tmp: Path):
    for rel, content in {**POSITIVE_FILES, **ORPHAN_FILE, **NEGATIVE_FILES}.items():
        p = tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


def main():
    mod = load_auditor()
    if not hasattr(mod, "scan_repo_for_secrets"):
        print("[FAIL] audit-skills.py has no scan_repo_for_secrets — the secret gate is gone?")
        return 1

    tmp = Path(tempfile.mkdtemp(prefix="secret-gate-mut-", dir=str(REPO.parent)))
    try:
        build_fixture(tmp)
        mod.REPO_ROOT = tmp   # same monkeypatch trick as mutation-test-doc-gate.py

        findings = mod.scan_repo_for_secrets()
        text = "\n".join(findings)

        expected_positives = {rel for rel in POSITIVE_FILES} | set(ORPHAN_FILE)
        missed = [rel for rel in sorted(expected_positives) if not any(rel.replace("\\", "/") in f for f in findings)]

        # every planted file must be named by at least one finding
        for rel in sorted(expected_positives):
            hit = [f for f in findings if rel.replace("\\", "/") in f]
            print(f"  {'caught' if hit else 'MISSED'}: {rel}" + ("" if hit else "   <-- pattern dead or scan disabled"))

        # no negative-control file may appear at all (env reads / placeholders must stay clean)
        false_pos = []
        for rel in sorted(NEGATIVE_FILES):
            hit = [f for f in findings if rel.replace("\\", "/") in f]
            print(f"  {'CLEAN ' if not hit else 'FALSE-POSITIVE'}: {rel}")
            false_pos.extend(hit)

        ok = (not missed) and (not false_pos)
        # also assert the threshold wiring exists: hardcoded_secrets must be a zero-threshold key
        thr_ok = mod.THRESHOLDS.get("hardcoded_secrets") == 0
        print(f"  {'OK    ' if thr_ok else 'BROKEN'}: THRESHOLDS['hardcoded_secrets'] == {mod.THRESHOLDS.get('hardcoded_secrets')} (must be 0)")

        if ok and thr_ok:
            n = len(expected_positives)
            print(f"ALL {n} PLANTED SECRETS CAUGHT, ZERO FALSE POSITIVES — secret gate verified fail-loud.")
            return 0
        reasons = []
        if missed:
            reasons.append(f"{len(missed)} planted secrets not caught")
        if false_pos:
            reasons.append(f"{len(false_pos)} false positives on env/placeholder content")
        if not thr_ok:
            reasons.append("threshold is no longer zero (a secret would pass silently)")
        print("\nFAILED: " + "; ".join(reasons))
        return 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
