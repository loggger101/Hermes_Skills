---
name: ssh-remote
description: "Run commands and transfer files on remote machines over SSH."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [SSH, remote, devops, file-transfer, tunnels]
    related_skills: []
---

# SSH Remote Access

Run commands on remote machines and transfer files over SSH. Encodes auth patterns and pitfalls so remote work is predictable.

## When to Use

- "Run this command on the server"
- "Copy files to/from the remote host"
- "Set up a tunnel or port forward"
- "Debug why I can't SSH in"
- "Check disk usage / logs / processes on the remote box"

Don't use for: local-only work; hosts you don't have credentials for (stop and ask).

## Prerequisites

- **SSH client** available (`ssh`, `scp`, `rsync` preferred)
- **Auth** sorted before the first call:
  - Key-based preferred: private key at a known path, or `ssh-agent` running with the key loaded
  - Password auth is fragile in non-interactive contexts — prefer keys
  - First connection may prompt to accept a host key — handle once, then cached
- **Known host spec**: `user@host` or an alias from `~/.ssh/config`
- **Network**: remote host reachable from this machine (no firewall/NAT blocking the port)

## How to Run

All remote commands go through `terminal` with `ssh` as the transport:

```bash
# Single command
ssh user@host 'uname -a'

# Interactive shell (pty needed for prompts like sudo passwords)
ssh user@host          # pty=true if you need to respond to prompts

# With a specific key
ssh -i ~/.ssh/my_key user@host 'df -h'

# Custom port
ssh -p 2222 user@host 'uptime'

# SSH config host alias
ssh myalias 'systemctl status nginx'
```

File transfer:

```bash
# Single file up
scp localfile user@host:/remote/path/

# Single file down
scp user@host:/remote/path/file .

# Directory up (recursive)
scp -r localdir user@host:/remote/

# rsync (efficient for large/partial syncs)
rsync -avz --progress localdir/ user@host:/remote/dir/

# rsync down
rsync -avz user@host:/remote/dir/ ./local/
```

Port forwarding:

```bash
# Local → remote (access remote service on local port)
ssh -L 8080:localhost:80 user@host
# Then http://localhost:8080 hits the remote's port 80

# Remote → local (expose local service to remote)
ssh -R 9090:localhost:3000 user@host

# Dynamic SOCKS proxy
ssh -D 1080 user@host
```

## Procedure

### 1. Verify connectivity
```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 user@host 'echo ok' 2>&1
```
Exit 0 = key auth works, host reachable. Non-zero = diagnose (wrong key, host down, firewall, host key not accepted).

### 2. Pick the transport
- One-off command → `ssh user@host 'command'`
- Multi-step session → background SSH or persistent control socket
- File transfer → `scp` for simple, `rsync` for large/incremental
- Service access → port forwarding (`-L`/`-R`) then hit localhost

### 3. Handle auth
- Key not loaded in agent? `ssh-add ~/.ssh/key` first (may need `pty` if ssh-add prompts)
- First-time host key? Pre-accept: `ssh-keyscan -H host >> ~/.ssh/known_hosts` (trusted networks only)
- Password auth is last resort; user must be present to type the password

### 4. Run and verify
- Read remote stdout/stderr from the `terminal` result
- Long-running remote commands: `terminal(background=true)` and poll
- After file transfers, verify with remote `ls -la` or `du -sh` via a follow-up SSH call

### 5. Clean up
- Background SSH sessions: close when done
- Port forwards: the SSH process holds the tunnel; kill it when no longer needed

## Quick Reference

| Task | Command |
|------|---------|
| Connectivity check | `ssh -o BatchMode=yes -o ConnectTimeout=5 user@host true` |
| Run command | `ssh user@host 'cmd'` |
| Interactive shell | `ssh user@host` (pty if prompts expected) |
| File up (simple) | `scp file user@host:/path/` |
| File down (simple) | `scp user@host:/path/file .` |
| Directory sync up | `rsync -avz src/ user@host:/dest/` |
| Directory sync down | `rsync -avz user@host:/src/ ./dest/` |
| Local forward | `ssh -L local_port:remote_host:remote_port user@host` |
| Remote forward | `ssh -R remote_port:local_host:local_port user@host` |
| SOCKS proxy | `ssh -D 1080 user@host` |
| Add key to agent | `ssh-add ~/.ssh/key` |
| Pre-accept host key | `ssh-keyscan -H host >> ~/.ssh/known_hosts` |
| Verbose (debug) | `ssh -vvv user@host` |

## Pitfalls

- **Host key prompts block automation.** First connection may hang on "Are you sure?". Pre-accept with `ssh-keyscan` only on trusted networks, do one interactive accept, or use `-o StrictHostKeyChecking=accept-new`.
- **Password auth doesn't work non-interactively.** If password is the only option, the user must be present. Don't silently retry.
- **Ctrl-C on remote commands may not propagate.** If the remote process ignores signals, kill the local ssh process.
- **rsync trailing slash matters.** `rsync src/ dest/` copies contents of `src/` into `dest/`; `rsync src dest/` copies the `src` directory itself. Wrong slash = extra nesting level.
- **Windows SSH clients vary.** Git Bash/MSYS ssh works; PowerShell's `ssh` may differ. Test connectivity with the same shell the agent uses.
- **Agent forwarding exposes local keys on the remote.** Only use `-A` when needed; don't forward to untrusted hosts.
- **Very long one-liners may hit remote shell limits.** Write long scripts to a remote file first, then execute it.

## Verification

- Connectivity check returns exit 0
- Remote command output matches expected result
- File transfers verified with remote `ls`/`du`/checksums
- Tunnels actually reach the target service (curl from local)
- No unexpected prompts left hanging

## Related

For local file operations, use `read_file` / `write_file` / `patch` / `search_files` instead of SSH. For GUI automation on the remote host, you'd need `computer_use` running on that machine — this skill covers CLI-over-SSH only.
