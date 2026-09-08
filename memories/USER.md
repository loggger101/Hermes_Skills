Security rule: never preserve API keys/tokens/passwords/credentials — replace with [REDACTED]. Cronjob delivery: deliver='all' broadcasts to all bot platforms; deliver='origin' sends back to chat (requires Hermes gateway running).
§
Works on Hermes_Skills repo (167 skills / 23 categories; flat docs/ layer dissolved into owning skills' references/, docs/ = pointer index + archive) and aspirecures repo at C:/Users/Owner/OneDrive/Documents/GitHub/. Windows 11 with core.autocrlf=true + .gitattributes text=auto. Second brain should hold general programming knowledge & use-case docs, not just skills.
§
Prefers perfect/foolproof autonomous solutions. Triple-checks deliverables: (1) git pushed & 0 ahead/behind, (2) working tree clean, (3) no temp files, (4) no accidental deletions, (5) audit passes.
§
Commit author convention for automation: hermes-cronbot / cronbot@hermes.local.
§
Website audit project (loganmedwardsastrophy.com portfolio, 57-page final report): delivered in chat only — no standing file on disk; rebuild from python-docx builder scripts in skills/productivity/docx/specs/ if needed. User values analysis-only deliverables with zero source code changes.
§
Python-docx builder pattern for large reports: self-contained script (not JSON spec), safeCall wrapper, mkdir -p output dir first.
§
CRITICAL: Before building ANY analysis report from source code, ALWAYS verify current file state by checking git log --oneline -5 and re-reading critical files directly — NEVER trust stale snapshots or cached context. Every prior audit delivery failed because I built findings on old paths that returned empty content, then extrapolated conclusions without verifying against live repo state.
§
Website audit protocol: 1) Clone/fetch LATEST from GitHub before analysis (not rely on local stale copies); 2) Read every file directly with read_file; 3) Cross-reference EVERY factual claim against actual source content line-by-line before writing it to report; 4) Run mandatory final review pass checking all claims one more time. Never deliver unverified findings.
§
When asked to improve/update the second brain repo, expects a full autonomous pass: brainstorm + execute across all applicable dimensions (skill ports, docs/ knowledge layer, index/count consistency, memory updates) — not minimal gate re-runs. Every claim verified from source this pass, never carried over from prior notes.
§
CR-pipeline (Clash Royale GA) at C:/Users/Owner/OneDrive/Documents/GitHub/CR-pipeline, remote github.com/loggger101/CR-pipeline. Project env = system Python313 (C:\Users\Owner\AppData\Local\Programs\Python\Python313; torch 2.9.1+cu130, numpy 2.2.6, pytest 9.1.1) — NOT hermes venv. Full suite ~7 min → run background. pygame 2.6.1 installed there (added for the new arena viewer).