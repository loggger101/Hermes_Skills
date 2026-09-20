Security rule: never preserve API keys/tokens/passwords/credentials — replace with [REDACTED]. Cronjob delivery: deliver='all' broadcasts to all bot platforms; deliver='origin' sends back to chat (requires Hermes gateway running).
§
Works on Hermes_Skills repo (190 skills / 23 categories) and aspirecures repo. Windows 11 + core.autocrlf + .gitattributes text=auto. Synced local Hermes env from repo: 190 skills, 304 ref docs, 470 xrefs, audit 0 issues. Second brain holds general programming knowledge + use-case docs.
§
Prefers perfect/foolproof autonomous solutions. Triple-checks deliverables: (1) git pushed & 0 ahead/behind, (2) working tree clean, (3) no temp files, (4) no accidental deletions, (5) audit passes.
§
Commit author convention for automation: hermes-cronbot / cronbot@hermes.local.
§
Website audit project (loganmedwardsastrophy.com portfolio, 57-page final report): delivered in chat only — no standing file on disk; rebuild from python-docx builder scripts in skills/productivity/docx/specs/ if needed. User values analysis-only deliverables with zero source code changes.
§
CRITICAL: Before building ANY analysis report from source code, ALWAYS verify current file state by checking git log --oneline -5 and re-reading critical files directly — NEVER trust stale snapshots or cached context. Every prior audit delivery failed because I built findings on old paths that returned empty content, then extrapolated conclusions without verifying against live repo state.
§
Website audit protocol: 1) Clone/fetch LATEST from GitHub before analysis (not rely on local stale copies); 2) Read every file directly with read_file; 3) Cross-reference EVERY factual claim against actual source content line-by-line before writing it to report; 4) Run mandatory final review pass checking all claims one more time. Never deliver unverified findings.
§
When asked to improve/update the second brain repo, expects a full autonomous pass: brainstorm + execute across all applicable dimensions (skill ports, docs/ knowledge layer, index/count consistency, memory updates) — not minimal gate re-runs. Every claim verified from source this pass, never carried over from prior notes.