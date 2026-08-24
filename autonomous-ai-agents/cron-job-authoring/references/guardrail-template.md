# Guardrail Template — No-Interaction Block for Cron Jobs

This is the annotated starter for the autonomy section of any cron job prompt. Copy it in, then trim or expand based on what the job actually touches.

## Full block (copy-paste)

```
=== AUTONOMY & NO-INTERACTION GUARDRAILS ===
This job runs autonomously on a schedule with no human present. You must NEVER pause to ask the user for anything — no API keys, no tokens, no credentials, no confirmations, no clarifications, and no manual intervention of any kind. If at any point you would normally want to use the clarify tool, do NOT use it — instead record the gap as an unresolved item and continue.

Specifically:
- Never prompt for API tokens or keys. If a step requires an external service token you do not already have access to in the environment, skip that verification step, note it as unverified, and move on. Do not attempt to obtain the token by any means (no web searches for how to get one, no prompting, no interactive flows).
- Never present any interactive UI to the user. No clarify calls; no computer-use dialogs that require a human response; no browser flows that would open a consent/password/payment screen. If a tool you invoke would surface a dialog, abort that action and note it as blocked.
- If the runtime itself raises a prompt on your behalf (e.g. an MCP server asking for an OAuth login or a missing key), treat it as a hard blocker for that step — record it and continue. You are not the person who can authorize it.
- When a referenced external service/tool requires credentials you do not have, evaluate what you CAN verify without them and mark the credential-dependent checks as unverified with the reason "credential not available — manual verification needed."
```

## Annotation on each rule

**"NEVER pause to ask the user for anything"**
This is the headline. It eliminates the entire class of "the agent got stuck waiting for a human" failures. Without it, the agent may call `clarify` on any ambiguity and the cron run hangs.

**"no API keys, no tokens, no credentials, no confirmations"**
These are the four things an agent most commonly tries to ask for. Naming them explicitly preempts the instinct.

**"If at any point you would normally want to use the clarify tool, do NOT use it"**
Some agents treat `clarify` as a safe default for ambiguity. In a cron context it's a deadlock. This line gives the agent an explicit alternative: record the gap and continue.

**"Never prompt for API tokens or keys"**
This is the rule the user specifically asked for. It covers both direct prompting AND indirect attempts (web searches for how to get a token, OAuth flows, etc.).

**"Do not attempt to obtain the token by any means"**
The agent might try to be helpful by searching the web for how to get a token, or by attempting an OAuth login flow. Both are out of scope for an unattended run.

**"Never present any interactive UI to the user"**
Covers computer-use dialogs, browser consent screens, and payment prompts. These all require a human in front of the machine.

**"If the runtime itself raises a prompt on your behalf ... treat it as a hard blocker"**
The agent can't control what MCP servers or credential pools do. When one of them raises a prompt (OAuth, missing key), the agent's job is to record it and move on, not wait.

**"evaluate what you CAN verify without them"**
This is the constructive part. The agent shouldn't skip the whole skill or verification just because one check needs credentials. It should do everything credential-independent and mark the rest as unverified.

## Placement

Put this block AFTER any cross-profile or security notes and BEFORE the first phased instruction (Phase 1, Step 1, etc.). The agent reads top-down; if the guardrails come after the phases, the agent may have already called `clarify` by the time it reaches them.

## When to expand

- If the job touches specific external services (e.g. GitHub, HuggingFace, Google), add a line naming them: "If a step requires a GitHub token and one is not available, skip the GitHub-linked check and mark it unverified."
- If the job has a specific blocker behavior (e.g. "if the cross-profile write is refused, record as BLOCKED and do NOT fall back to patching the active profile's copy"), make that explicit rather than leaving it to the agent to infer.

## When to trim

- If the job is a pure no_agent script (no LLM), the guardrail block is unnecessary — there's no agent to prompt. The delivery discipline section still applies if the script produces output that gets delivered.
- If the job only touches local files and never reaches external services, the credential-related bullets can be shortened to "No step in this job requires external credentials."
