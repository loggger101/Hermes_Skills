# Output Alignment Reference

## The Pitfall
Cron configs declare `threshold` keys and `post_run_verification` commands that
don't match what the script **actually** emits to stdout/JSON. This produces:
- **False alerts**: threshold keys that don't exist in script output are silently
  ignored (always pass) — real problems slip through.
- **Missed alerts**: threshold keys the script DOES emit but the cron omits — no
  alerting even when the script fails.
- **Fictional commands**: `--list-broken-refs`, `--suggest-trims` style CLI flags
  that the script never supported (no argparse, no CLI flags).

## Correct Pattern
1. **Read the script's summary/threshold dict** — that's the source of truth for
   what the cron `threshold` block must mirror.
2. **Read the script's report `issues` / `summary` keys** — these define the
   `report_template` structure.
3. **Never invent `--flags`** — if the script has no argparse, provide JSON
   extraction one-liners instead:
   ```
   python -c "import json,sys; d=json.load(sys.stdin); print(json.dumps(d['issues']['broken_refs'], indent=2))"
   ```
4. **Add an `actual_script_output` / `actual_audit_output` section** to the cron
   config documenting the exact output keys the script produces.
5. **Verify with real execution** before committing — `python tools/script.py --dry-run`
   then check the JSON keys match.

## Script Output Mapping

### audit-skills.py (no_agent=true)
- **THRESHOLDS dict** (6 keys): `broken_refs`, `yaml_errors`, `long_descriptions`,
  `duplicate_skills`, `temps_scripts`, `missing_body_sections`
- **Top-level output**: `threshold_breached`, `exit_code`
- **issues keys** (8): `broken_refs`, `yaml_errors`, `long_descriptions`,
  `duplicate_skills`, `temps_scripts`, `missing_body_sections`,
  `missing_related_skills`, `placeholder_markers`, `missing_category_descriptions`
- **summary keys** (8, mirrors THRESHOLDS): same 6 + `missing_related_skills` +
  `placeholder_markers` + `missing_category_descriptions`
- **Reported but NOT threshold-gated**: `missing_frontmatter_fields` (goes into
  `yaml_errors`), `missing_category_descriptions` (stored in issues but not in
  THRESHOLDS dict)
- **No CLI flags**: script takes no argparse arguments — uses JSON extraction

### sync-hermes-skills.py (no_agent=true)
- **summary keys**: `files_pulled_to_local`, `files_skipped_pull`,
  `new_local_files_in_repo`, `updated_files_in_repo`, `deleted_files_in_repo`,
  `memories_synced`, `profiles_synced`, `profiles_exported`, `profiles_skipped`,
  `git_pull_success`, `git_push_success`, `audit_passed`, `lint_passed`,
  `threshold_breached`, `push_error`
- **CLI flags**: `--dry-run` (skips all file ops + git commits/pushes)

### fetch_curate.mjs (CI pipeline — aspirecures repo)
- Not a script the cron runs directly — the cron agent substitutes itself for this
  script's Claude gate step. The cron must document the data shapes, dedup logic,
  and date-churn algorithm this script implements so the agent can replicate it.
