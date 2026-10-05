---
name: windows-agent-shell
description: "Windows Bash-tool traps: heredocs, cp1252, CRLF."
version: 1.0.0
author: Hermes Agent (from the owner's user-level CLAUDE.md and the vault's agent-working-environment page, 2026-10)
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [windows, bash, heredoc, python, encoding, cp1252, crlf, agent-environment, permissions]
    related_skills: [python-craft, python-toolchain-notes, git-on-sync-clients, verification-before-completion, systematic-debugging, windows-desktop-e2e]
---

# Windows agent shell traps

## What This Skill Does

Collects the shell and text-encoding traps that agent sessions on the owner's Windows machines keep relearning when they use a Bash tool (Git Bash) from Windows: heredocs that eat backslashes, `python -` that hangs, Python's cp1252 stdout raising after a write succeeded, CRLF in Python-written files, shadowing installs, plus the rules for stamping dates, porting code and handling permission-classifier denials. Having a rule loaded is not the same as following it: the vault saw both loaded and both traps hit anyway, in one-liners written in passing.

## When to Use

- Writing any script from the Bash tool on Windows, especially with backslashes, regexes or triple quotes
- A Python one-liner hangs, prints a `UnicodeEncodeError`, or leaves odd `\r` characters
- A module imports an old version from `site-packages` instead of the repo
- A command such as `gh pr merge` or `git filter-branch` is refused
- Not for git-in-OneDrive problems (`git-on-sync-clients`), Python language traps (`python-craft`), or UI testing (`windows-desktop-e2e`)

## Shell and encoding rules

| Trap | Rule |
|---|---|
| Heredocs eat backslashes, even quoted (`<<'EOF'`): `\b` became a backspace in a Python regex | write any script containing backslashes, regexes or `'''` with the **Write** tool, then run it; even for short ones, and look at what reached the disk |
| `python - <<'EOF'` hangs until timeout | put the script in the scratchpad and run `timeout N python f.py < /dev/null` |
| A patch script that asserts after editing looks half-done when it fails; opening a file for writing before the new text is built truncates it | assert every anchor first, build the new text, then write |
| Python stdout is cp1252: printing an em dash or arrow raises *after* the file write succeeded | print ASCII status only or `sys.stdout.reconfigure(encoding="utf-8")`; check the disk before re-running |
| Python-written files can end in CRLF, so a `while read` loop carries `\r` into URLs | pipe through `tr -d '\r'` |
| A global or editable install shadows the repo (an old `spacecost` 0.1.1; a package installed from another clone) | run from the repo root or set `PYTHONPATH=.` / `PYTHONPATH=src`; check `module.__file__` |
| A written Python version rots (wrong three ways in six days in one repo) | ask the machine: `py -VV` |
| On the Owner machine `python`/`python3` are Store stubs that exit 49, which `| tail` hides | use `py`, spawn helpers with `sys.executable`, read exit codes without a pipe. On `Loggg` they are real 3.14 aliases |

## Verify, don't assume

- **Dates**: run `date` before writing a stamp or branch name; never infer it from build output.
- **Ported code**: extract programmatically and diff against the source; hand copying silently changed literals, escapes and a Unicode apostrophe.
- **Gates**: prove a check fails on a planted defect before trusting its pass; a check that never ran prints the same clean line as one that works.
- **Numbers**: cite them and confirm by a second independent route where one exists.

## Permission classifier

- `gh pr merge` is sometimes denied: attempt it when asked; if refused, hand over the exact command.
- `git filter-branch` is denied even when requested: prepare the rewrite, create a backup ref, and hand over the command.
- Rerouting a denied command through another tool is working around the denial; do not.

## Long runs (Owner machine)

Detach from the console, not just the parent: a scheduled `cmd /c x.bat` was killed by a Ctrl+C aimed at another tool call, so run long work with no console at all. The in-app Browser pane there never composites frames, so computed styles go stale silently; drive headless Chrome over CDP for visual checks.

## Pitfalls

- Believing a rule is followed because it is in context; the failures happened in passing one-liners, not planned scripts.
- Re-running a script after a cp1252 error without checking whether the first run already wrote the file.
- Letting `| tail` hide a non-zero exit code.

## Verification

- [ ] Every script with backslashes or regexes was written with the Write tool and inspected on disk
- [ ] No `python -` heredoc was used; scripts ran with `timeout` and `< /dev/null`
- [ ] The date, interpreter version and module path were asked of the machine
- [ ] Denied actions were handed to the user rather than rerouted
