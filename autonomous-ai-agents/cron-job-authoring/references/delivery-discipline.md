# Delivery Discipline for Cron Jobs

Why the delivery reminder matters, what goes wrong without it, and the exact wording to use.

## The problem

In an interactive session, an agent might summarize mid-run, deliver a partial result, or try to "help" by sending a message before the full report is ready. In a cron context, that produces duplicate or partial deliveries — the user gets a mid-run summary AND the final report, or gets a partial report that looks complete.

The cron system handles delivery automatically: the agent's final response is what gets delivered. The agent does not need to (and should not) call `send_message`, `clarify`, or any other delivery tool.

## The reminder

Add this to the prompt for every LLM-driven cron job:

```
IMPORTANT: You are running as a scheduled cron job. Your final response will be automatically delivered to the user — do NOT use send_message or try to deliver the output yourself. Just produce your report/output as your final response and the system handles the rest.
```

Place it near the top, alongside the no-interaction guardrails. It's part of the same "you are running autonomously" framing.

## What goes wrong without it

- **Mid-run delivery.** The agent sends a "here's what I've found so far" message partway through. The user gets an incomplete picture, and the final report may arrive separately or not at all if the run is interrupted.
- **Duplicate delivery.** The agent delivers a summary at the end AND the system delivers the final response. The user sees the same content twice.
- **Partial report delivered as complete.** The agent calls `send_message` with what it has so far, thinks it's done, and stops. The system never receives the "final response" it expects, so nothing else is delivered.
- **Tool loops on delivery.** An agent that tries to delivery-check or re-deliver can enter a loop where it keeps re-sending the same content.

## When the reminder is not needed

- **no_agent script jobs.** There's no LLM; the script's stdout is delivered verbatim. The delivery reminder has no agent to address.
- **Jobs that produce no output.** Silent watchdog jobs that suppress delivery when nothing changed (e.g. `wakeAgent: false`) don't need the reminder — there's nothing to deliver.

## Relationship to the no-interaction guardrails

The delivery reminder and the no-interaction guardrails are complementary:

- Guardrails say: don't prompt, don't ask, don't wait.
- Delivery reminder says: don't deliver early, don't deliver yourself, don't duplicate.

Both belong in the same autonomy framing at the top of the prompt.

## Verification

After adding the reminder, run the job once and check the session transcript for:

1. Any `send_message` or delivery tool calls — there should be none.
2. Any mid-run "here's a summary" messages — there should be none.
3. The final response is the complete report, not a teaser or partial.
