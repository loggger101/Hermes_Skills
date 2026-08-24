---
name: apple-reminders
description: "Apple Reminders via remindctl: add, list, complete."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [Reminders, tasks, todo, macOS, Apple]
    related_skills: [apple-notes, findmy, imessage, cron-job-authoring, hermes-agent]
prerequisites:
  commands: [remindctl]

---

# Apple Reminders

Use `remindctl` to manage Apple Reminders directly from the terminal. Tasks sync across all Apple devices via iCloud.

## Prerequisites

- **macOS** with Reminders.app
- Install: `brew install steipete/tap/remindctl`
- Grant Reminders permission when prompted
- Check: `remindctl status` / Request: `remindctl authorize`

## What This Skill Does

Uses the `remindctl` CLI to manage Apple Reminders.app via AppleScript. Covers: viewing reminders (today, overdue, all, by date), managing lists, creating reminders with due dates and alarms, completing/deleting reminders, and output formatting. Loads `skill_view(name='hermes-agent')` for cron integration and `skill_view(name='cron-job-authoring')` for scheduled reminder checks.

## When to Use

- User mentions "reminder" or "Reminders app"
- Creating personal to-dos with due dates that sync to iOS
- Managing Apple Reminders lists
- User wants tasks to appear on their iPhone/iPad

## When NOT to Use

- Scheduling agent alerts → use the cronjob tool instead
- Calendar events → use Apple Calendar or Google Calendar
- Project task management → use GitHub Issues, Notion, etc.
- If user says "remind me" but means an agent alert → clarify first

## Quick Reference

### View Reminders

```bash
remindctl                    # Today's reminders
remindctl today              # Today
remindctl tomorrow           # Tomorrow
remindctl week               # This week
remindctl overdue            # Past due
remindctl all                # Everything
remindctl 2026-01-04         # Specific date
```

### Manage Lists

```bash
remindctl list               # List all lists
remindctl list Work          # Show specific list
remindctl list Projects --create    # Create list
remindctl list Work --delete        # Delete list
```

### Create Reminders

```bash
remindctl add "Buy milk"
remindctl add --title "Call mom" --list Personal --due tomorrow
remindctl add --title "Meeting prep" --due "2026-02-15 09:00"
```

### Due Time vs Alarm / Early Nudge

`--due` and `--alarm` are different fields:

- `--due` sets the reminder's due date/time.
- `--alarm` sets the EventKit alarm/notification trigger. Timed due reminders may default to an alarm at the due time, but pass `--alarm` explicitly when the user asks for an earlier nudge.

For a reminder due at 2:00 PM with a notification 30 minutes earlier:

```bash
remindctl add --title "Hairdresser" --due "2026-05-15 14:00" --alarm "2026-05-15 13:30"
```

To edit an existing reminder:

```bash
remindctl edit 87354 --due "2026-05-15 14:00" --alarm "2026-05-15 13:30"
```

The Reminders UI may show or group the item by the alarm time because that is when the notification fires. Verify with JSON instead of assuming the due time moved:

```bash
remindctl today --json
```

Expected shape:

- `dueDate`: actual due time
- `alarmDate`: notification / early nudge time

Apple's public `EKReminder` docs list only reminder-specific properties. Alarm support comes from inherited `EKCalendarItem` behavior exposed by remindctl's `--alarm` flag.

### Complete / Delete

```bash
remindctl complete 1 2 3          # Complete by ID
remindctl delete 4A83 --force     # Delete by ID
```

### Output Formats

```bash
remindctl today --json       # JSON for scripting
remindctl today --plain      # TSV format
remindctl today --quiet      # Counts only
```

## Date Formats

Accepted by `--due` and date filters:
- `today`, `tomorrow`, `yesterday`
- `YYYY-MM-DD`
- `YYYY-MM-DD HH:mm`
- ISO 8601 (`2026-01-04T12:34:56Z`)

## Rules

1. When user says "remind me", clarify: Apple Reminders (syncs to phone) vs agent cronjob alert
2. Always confirm reminder content and due date before creating
3. Use `--json` for programmatic parsing

## Pitfalls

- **Permission denied**: If `remindctl` fails, run `remindctl authorize` and grant reminders permission in System Settings
- **Due vs alarm confusion**: `--due` sets when it's due; `--alarm` sets when the notification fires. Don't use `--alarm` unless the user specifically wants a notification nudge
- **Date format parsing**: Natural language like "tomorrow at 3pm" may not parse consistently — use explicit format `YYYY-MM-DD HH:mm`
- **Duplicate reminders**: `remindctl add` doesn't check for duplicates — search first with `remindctl today -s "query"`
- **iCloud sync delays**: Changes may take seconds to appear on other devices — don't assume immediate sync
- **Interactive prompts**: Some operations require interactive selection — use `pty=true` in terminal for these
- **List names with spaces**: Wrap in quotes — `--list "My List"`

## Verification

- [ ] `remindctl` is installed (`which remindctl`)
- [ ] Permissions granted (`remindctl status` shows connected)
- [ ] Reminder created with correct due date and alarm (verify with `--json` output)
- [ ] List management (create/delete) works
- [ ] Completion status updates correctly
- [ ] Date format parsing tested with various inputs
