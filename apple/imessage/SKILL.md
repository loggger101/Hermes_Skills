---
name: imessage
description: "Send and receive iMessages/SMS via the imsg CLI on macOS."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [iMessage, SMS, messaging, macOS, Apple]
    related_skills: [apple-notes, apple-reminders, findmy]
prerequisites:
  commands: [imsg]
---

# iMessage

Use `imsg` to read and send iMessage/SMS via macOS Messages.app.

## What This Skill Does

Sends and receives iMessages and SMS messages via the `imsg` CLI tool, which interfaces with macOS Messages.app via AppleScript. Supports listing chats, viewing conversation history (with attachments), sending messages (text, attachments, forced iMessage/SMS), and watching for new messages in real-time. Loads `skill_view(name='apple-notes')` for note-taking and `skill_view(name='apple-reminders')` for task management.

## Prerequisites

- **macOS** with Messages.app signed in
- Install: `brew install steipete/tap/imsg`
- Grant Full Disk Access for terminal (System Settings → Privacy → Full Disk Access)
- Grant Automation permission for Messages.app when prompted
- `jq` for JSON parsing (standard on macOS via Homebrew)

## When to Use

- User asks to send an iMessage or text message
- Reading iMessage conversation history
- Checking recent Messages.app chats
- Sending to phone numbers or Apple IDs

## When NOT to Use

- Telegram/Discord/Slack/WhatsApp messages → use the appropriate gateway channel
- Group chat management (adding/removing members) → not supported
- Bulk/mass messaging → always confirm with user first

## Quick Reference

### List Chats

```bash
imsg chats --limit 10 --json
```

### View History

```bash
# By chat ID
imsg history --chat-id 1 --limit 20 --json

# With attachments info
imsg history --chat-id 1 --limit 20 --attachments --json
```

### Send Messages

```bash
# Text only
imsg send --to "+14155551212" --text "Hello!"

# With attachment
imsg send --to "+14155551212" --text "Check this out" --file /path/to/image.jpg

# Force iMessage or SMS
imsg send --to "+14155551212" --text "Hi" --service imessage
imsg send --to "+14155551212" --text "Hi" --service sms
```

### Watch for New Messages

```bash
imsg watch --chat-id 1 --attachments
```

## Service Options

- `--service imessage` — Force iMessage (requires recipient has iMessage)
- `--service sms` — Force SMS (green bubble)
- `--service auto` — Let Messages.app decide (default)

## Rules

1. **Always confirm recipient and message content** before sending
2. **Never send to unknown numbers** without explicit user approval
3. **Verify file paths** exist before attaching
4. **Don't spam** — rate-limit yourself

## Example Workflow

User: "Text mom that I'll be late"

```bash
# 1. Find mom's chat
imsg chats --limit 20 --json | jq '.[] | select(.displayName | contains("Mom"))'

# 2. Confirm with user: "Found Mom at +1555123456. Send 'I'll be late' via iMessage?"

# 3. Send after confirmation
imsg send --to "+155****3456" --text "I'll be late"
```

## Pitfalls

- **Permission errors**: If `imsg` fails, ensure Full Disk Access is granted in System Settings → Privacy & Security → Full Disk Access, and Automation permission for Messages.app is enabled
- **Phone number format**: Use E.164 international format (`+1XXXXXXXXXX`), not local format
- **iMessage vs SMS**: If the recipient doesn't use iMessage, messages fall back to SMS (green bubble) — use `--service imessage` to force and get an error if they don't have iMessage
- **Attachments**: File paths must be absolute; verify the file exists before sending
- **Rate limiting**: Don't send multiple messages in rapid succession — Messages.app may throttle
- **Chat ID stability**: Chat IDs can change if conversations are deleted and recreated
- **Large history**: `imsg history --limit` should always be set — omitting it can return thousands of messages

## Verification

- [ ] `imsg` is installed and authenticated (`imsg chats --limit 1` returns results)
- [ ] Sending test message to own phone number succeeds
- [ ] Attachment sending works with valid file path
- [ ] Chat history is retrieved with correct limit
- [ ] JSON output is valid and parseable by `jq`
- [ ] Watch mode detects new messages in target chat
