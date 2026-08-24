---
name: docker-containers
description: "Build and debug Docker containers and Compose stacks."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Docker, containers, devops, Compose, debugging]
    related_skills: [ssh-remote]

---

# Docker & Containers

Build, run, inspect, and debug Docker containers and Docker Compose stacks.

## When to Use

- "Build and run this Dockerfile"
- "Start the stack with Compose"
- "Why is this container crashing?"
- "Check logs, exec in, inspect a running container"
- "Clean up images/containers/volumes"
- "Debug a port mapping or networking issue"

Don't use for: orchestration beyond Compose (Kubernetes needs its own workflow); bare-metal/VM provisioning.

## Prerequisites

- **Docker daemon** running and reachable (`docker info` works)
- On Linux: user has permission to the Docker socket (or `sudo`)
- On macOS/Windows: Docker Desktop (or OrbStack/Rancher) running
- **Dockerfile** or **docker-compose.yml** present, or an image name known
- Disk space awareness: images, stopped containers, and build cache accumulate fast

## How to Run

All Docker commands go through `terminal`:

```bash
# Image lifecycle
docker pull nginx:alpine
docker build -t myapp:dev .
docker images
docker rmi myapp:dev

# Container lifecycle
docker run -d --name myapp -p 8080:80 myapp:dev
docker ps
docker ps -a
docker stop myapp
docker rm myapp
docker run --rm -it myapp:dev bash

# Inspect & debug
docker logs myapp
docker logs -f --tail 50 myapp
docker inspect myapp
docker stats myapp
docker top myapp

# Exec into a running container
docker exec -it myapp bash
docker exec myapp cat /etc/os-release

# Compose
docker compose up -d
docker compose down
docker compose logs -f
docker compose ps
docker compose build
docker compose up --build --force-recreate
```

## Procedure

### 1. Verify the daemon
```bash
docker info
```
Failures: Docker not running or permission issue. Linux: try `sudo docker info`. macOS/Windows: check Docker Desktop is running.

### 2. Image: pull or build
- **Pull**: `docker pull <image>`
- **Build**: `docker build -t <name>:<tag> .`
  - Context is the directory you run from (or `-f` for a specific Dockerfile)
  - `--no-cache` when a stale layer masks a real problem
  - `--progress=plain` for verbose output when debugging

### 3. Run
- **One-shot**: `docker run --rm <image> <cmd>`
- **Daemon**: `docker run -d --name <name> -p <host>:<container> <image>`
- **Interactive**: `docker run -it --rm <image> bash` (or `sh`)
- **Env/volume**: `docker run -e KEY=val -v /host/path:/container/path ...`

### 4. Debug a failing container
```bash
# 1. Why did it exit?
docker logs <name>
docker inspect <name> | grep -A 5 '"State"'

# 2. What's happening now?
docker stats <name>
docker top <name>

# 3. Get inside (if still running)
docker exec -it <name> sh

# 4. Reproduce interactively
docker run -it --rm -v /host/path:/work <image> sh
# then manually run the failing command
```

### 5. Compose stacks
```bash
docker compose up -d
docker compose ps
docker compose logs --tail 100
docker compose build
docker compose up -d --force-recreate
docker compose down
docker compose down -v
```

### 6. Cleanup (periodically, not by default)
```bash
docker container prune       # stopped containers
docker image prune           # unused images
docker system prune          # dangling images + stopped containers + networks + build cache
docker system prune -a      # also removes unused images (not just dangling)
docker volume prune          # volumes — data! only if you mean to delete it
```

## Quick Reference

| Task | Command |
|------|---------|
| Daemon check | `docker info` |
| List images | `docker images` |
| Build image | `docker build -t name:tag .` |
| Run detached | `docker run -d --name n -p H:C img` |
| Run one-shot | `docker run --rm img cmd` |
| Run interactive | `docker run -it --rm img bash` |
| List running | `docker ps` |
| List all | `docker ps -a` |
| View logs | `docker logs <name>` |
| Follow logs | `docker logs -f <name>` |
| Last 50 lines | `docker logs --tail 50 <name>` |
| Exec shell | `docker exec -it <name> bash` |
| Exec command | `docker exec <name> cmd` |
| Inspect | `docker inspect <name>` |
| Live stats | `docker stats <name>` |
| Stop | `docker stop <name>` |
| Remove | `docker rm <name>` |
| Prune stopped | `docker container prune` |
| Prune images | `docker image prune` |
| Prune all unused | `docker system prune` |
| Compose up | `docker compose up -d` |
| Compose down | `docker compose down` |
| Compose logs | `docker compose logs -f` |
| Compose rebuild | `docker compose build && docker compose up -d --force-recreate` |

## Pitfalls

- **Container exits immediately** = command failed or service isn't staying foreground. Check `docker logs`. A web server backgrounded and then exited is the classic: the main process must stay foreground.
- **`docker exec` requires the container running.** If it exited, you can't exec — reproduce with `docker run -it --rm` instead, or inspect logs.
- **`docker system prune` is destructive.** Stopped containers and dangling images are safe; unused images and volumes may not be. Don't run `-a` or volume pruning blindly.
- **Volume mounts don't auto-create host directories.** `-v /host/path:/container/path` where host path doesn't exist → Docker creates it as root. Pre-create host paths or use named volumes.
- **Port already in use.** `docker run -p 8080:80` fails if something on the host already uses 8080. `docker ps` won't show it — check with `ss -tlnp | grep 8080`.
- **Build context bloat.** `docker build .` sends the entire directory to the daemon. A `.dockerignore` keeps it lean; without one, large `node_modules/` or `.git/` slows builds and can OOM the daemon.
- **Compose v1 vs v2.** `docker-compose` (hyphen, v1) vs `docker compose` (space, v2). Both usually work; prefer `docker compose` on modern installs. If one fails, try the other.
- **Platform mismatches.** Building on Apple Silicon for AMD64 (or vice versa) needs `--platform linux/amd64` and runs slow under emulation. Multi-arch uses buildx.

## Verification

- `docker info` succeeds
- Image builds without error (or error is the real bug)
- Container stays running (or exits with expected code)
- Logs show expected startup output
- Port reachable from host (`curl localhost:<port>`)
- Compose stack: `docker compose ps` shows expected states

## Related

For remote Docker hosts, combine with `skill_view(name='ssh-remote')` — SSH into the box and run Docker there. For containerized CI, this skill covers local reproduction; CI-specific issues need additional context.
