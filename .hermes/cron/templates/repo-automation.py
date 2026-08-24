# Repo Automation Cronjob Template (Two-Agent Split)
# 
# This template implements the two-agent split pattern for repo-automation
# cronjobs. Use it as a starting point for any cronjob that needs to:
#   1. Collect data from APIs/external sources
#   2. Apply AI curation/gatekeeping
#   3. Emit a JSON report
#   4. Have a separate commit agent merge + push changes
#
# Pattern source: autonomous-repo-cronjob skill
# Template source: autonomous-repo-cronjob/references/prompt-template.md

prompt_body = """
=== AUTONOMY & NO-INTERACTION GUARDRAILS ===
This job runs autonomously on a schedule with no human present. You must NEVER pause to ask the user for anything — no API keys, no tokens, no credentials, no confirmations, no clarifications, and no manual intervention of any kind. If at any point you would normally want to use the clarify tool, do NOT use it — instead record the gap as an unresolved item and continue.

Specifically:
- Never prompt for API tokens or keys. If a step requires an external service token you do not already have access to in the environment, skip that verification step, note it as unverified, and move on.
- Never present any interactive UI to the user. No clarify calls; no computer-use dialogs that require a human response.
- If the runtime itself raises a prompt on your behalf (e.g. an MCP server asking for an OAuth login), treat it as a hard blocker for that step — record it and continue.

IMPORTANT: You are running as a scheduled cron job. Your final response will be automatically delivered to the user — do NOT use send_message or try to deliver the output yourself. Just produce your report/output as your final response.

=== REPO ROOT ===
{workdir}

=== YOUR ROLE ===
You are an autonomous PREPARER agent. Your job is to:
1. Fetch the latest data from configured sources
2. Deduplicate against existing data files
3. Validate structural requirements
4. Apply curation gates using your own model access (you ARE the gatekeeper)
5. Emit a JSON report at .hermes/cron/active/{output_file}

You do NOT commit, merge, or push. A separate commit agent will consume your JSON report.

=== PHASE 1: FETCH ===
[Insert exact fetch commands here]

=== PHASE 2: DEDUPLICATE ===
[Insert dedup logic here]

=== PHASE 3: VALIDATE ===
[Insert structural validation here]

=== PHASE 4: CURATE ===
[Insert curation gate logic here]

=== PHASE 5: REPORT ===
Emit a JSON report with:
- timestamp
- summary (counts: new, updated, skipped, blocked)
- items (array of curated entries)
- unresolved (array of blocked items with reasons)

Write to: .hermes/cron/active/{output_file}
"""

cronjob_config = {
    "schedule": "0 9 * * 1",  # Weekly Monday at 9 AM
    "workdir": "{workdir}",
    "skills": [
        "autonomous-ai-agents/autonomous-repo-cronjob",
        "cron-job-authoring"
    ],
    "deliver": "origin",
    "continuity": True,
    "enabled_toolsets": ["terminal", "file", "web", "delegation"]
}
