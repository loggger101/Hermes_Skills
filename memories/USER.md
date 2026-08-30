Works on Hermes_Skills repo (127 skills, 25 categories) at C:/Users/Owner/OneDrive/Documents/GitHub/Hermes_Skills and aspirecures repo. Windows 11 with core.autocrlf=true + .gitattributes text=auto.
§
Hermes_Skills: 25 categories (autonomous-ai-agents, apple, creative, data-science, devops, doc-coauthoring, dogfood, email, frontend-design, github, huggingface-trackio, media, mlops, note-taking, productivity, research, security, smart-home, social-media, software-development). Total 127 SKILL.md files. Latest commit: 58b5b05 "chore: bump 12 alpha skills to v1.0" — 67 commits total on main.
§
Hermes_Skills supporting tools/scripts: tools/audit-skills.py (validates all 127 SKILL.md files), tools/sync-hermes-skills.py (bidirectional sync local↔repo). DEPENDENCY.md has 332 cross-references; hub skills = requesting-code-review(14 refs), systematic-debugging(11), test-driven-development(10). NOTES.md is 262 lines of audit findings. Profile exports in profiles-export/.
§
Cronjob names+models: (1) aspirecures-weekly-research — qwen/qwen3.6-35b, schedule=17 13 * * 1 (Mon 9:17 AM ET), two-agent research pipeline for 9 disease pages; (2) hermes-skills-audit — same model, schedule=0 3 * * 0 (Sun 3am), runs tools/audit-skills.py with no_agent=true; (3) hermes-skills-bidirectional-sync — same model, schedule=0 2 * * 0 (Sun 2am), runs sync-hermes-skills.py bidirectionally.
§
Hermes config: default model qwen/qwen3.6-35b-a3b via LMStudio at http://127.0.0.1:1234/v1 (fallback poolside/laguna-s-2.1:free). Memory limits: memory_char_limit 22000, user_char_limit 2375; compression threshold 0.5, target_ratio 0.2, protect_last_n 20, protect_first_n 3. Tool loop guardrails: warn after exact_failure=2/same_tool_failure=3/idempotent_no_progress=2; hard stop at 5/8/5.
§
Skill description limit: max 59 chars + period (60-char budget). Index truncates >57 chars to '...' destroying routing signal. Keep descriptions as one sentence, trigger word first, end with period.
§
Windows gotchas for Hermes_Skills repo work: str(path) uses backslash so forward-slash substring filters fail silently; python3 is broken Store stub — use shutil.which('python') or 'python' command directly; HERMES_HOME=C:\Users\Owner\AppData\Local\hermes; cronjob system runs on Windows.
§
Profile structure: PROFILE.md (metadata), USER.md, MEMORY.md, config.yaml, .usage.json (per-skill metrics), .curator_ledger.jsonl (audit trail with sha256). 5 bot platforms at profile level: telegram/hermes-telegram, discord/hermes-discord, whatsapp/hermes-whatsapp, slack/hermes-slack, signal/hermes-signal.
§
User triple-checks after deliverables: (1) git fully pushed & 0 ahead/behind, (2) working tree clean, (3) no temp files, (4) no accidental deletions, (5) audit passes. Prefers perfect/foolproof autonomous solutions.
§
Commit author convention: hermes-cronbot / cronbot@hermes.local for automation commits. Never preserve API keys/tokens — replace with [REDACTED]. Display settings: personality=technical, pet=cache-capy (0.33 scale), show_reasoning=true.