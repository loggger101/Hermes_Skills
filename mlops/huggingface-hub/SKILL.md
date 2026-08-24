---
name: huggingface-hub
description: "HuggingFace hf CLI: search/download/upload models"
version: 1.0.1
author: Hugging Face
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [huggingface, hf, models, datasets, hub, mlops]
    related_skills: [huggingface-trackio, llama-cpp]

---

# Hugging Face CLI (`hf`) Reference Guide

The `hf` command is the modern command-line interface for interacting with the Hugging Face Hub, providing tools to manage repositories, models, datasets, and Spaces.

> **IMPORTANT:** The `hf` command replaces the deprecated and now-removed `huggingface-cli` command. In `huggingface_hub` v1.0+, the legacy `huggingface-cli` executable was removed entirely; only `hf` (also aliased as `hf repo`, `hf datasets`, etc.) is available. Both `repos` and `repo` invoke the same command — `repo` is an alias of `repos`, not a separate command.

## When to Use

Use when you need to:
- Search for models or datasets on the Hugging Face Hub
- Download pre-trained models or datasets to local storage
- Upload new models, datasets, or Spaces
- Manage authentication and access tokens
- Run inference endpoints or batch jobs on HF infrastructure

**Skip when:** You need to track experiments (use `skill_view(name='huggingface-trackio')`), run local GGUF models (use `skill_view(name='llama-cpp')`), or do Python API-level operations (use the Python `huggingface_hub` library directly).

## Prerequisites

```bash
# Installation
curl -LsSf https://hf.co/cli/install.sh | bash -s

# Authentication
hf auth login
# Or set HF_TOKEN environment variable
export HF_TOKEN="your-token-here"
```

**Requirements:**
- Hugging Face account (free tier available)
- Sufficient disk space for large models
- For inference endpoints: paid HF account

## What This Skill Does

Manages the full lifecycle of Hugging Face Hub resources from the command line:

| Category | Commands | Purpose |
|----------|----------|---------|
| **Download** | `hf download` | Fetch files/models to local cache |
| **Upload** | `hf upload` | Push new files to a repo |
| **Auth** | `hf auth` | Login, logout, list tokens |
| **Repos** | `hf repos create/delete` | Manage repos |
| **Datasets** | `hf datasets` | Search, info, SQL queries |
| **Models** | `hf models` | Search and get model info |
| **Endpoints** | `hf endpoints` | Deploy/manage inference |
| **Jobs** | `hf jobs` | Run compute tasks |
| **Spaces** | `hf spaces` | Manage interactive apps |
| **Discussions** | `hf discussions` | Manage PRs and issues |

## Quick Start

- **Installation:** `curl -LsSf https://hf.co/cli/install.sh | bash -s`
- **Help:** Use `hf --help` to view all available functions and real-world examples.
- **Authentication:** Recommended via `HF_TOKEN` environment variable or the `--token` flag.

---

## Core Commands

### General Operations
- `hf download REPO_ID`: Download files from the Hub.
- `hf upload REPO_ID`: Upload files/folders (recommended for single-commit; also handles resumable uploads of large directories).
- `hf upload-large-folder REPO_ID LOCAL_PATH`: **[Deprecated]** — use `hf upload` instead.
- `hf sync`: Sync files between a local directory and a bucket.
- `hf env` / `hf version`: View environment and version details.

### Authentication (`hf auth`)
- `login` / `logout`: Manage sessions using tokens from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
- `list` / `switch`: Manage and toggle between multiple stored access tokens.
- `whoami`: Identify the currently logged-in account.

### Repository Management (`hf repos`)
- `create` / `delete`: Create or permanently remove repositories.
- `duplicate`: Clone a model, dataset, or Space to a new ID.
- `move`: Transfer a repository between namespaces.
- `branch` / `tag`: Manage Git-like references.
- `delete-files`: Remove specific files using patterns.

### Datasets & Models
- **Datasets:** `hf datasets list`, `info`, and `parquet` (list parquet URLs).
- **SQL Queries:** `hf datasets sql SQL` — Execute raw SQL via DuckDB against dataset parquet URLs.
- **Models:** `hf models list` and `info`.
- **Papers:** `hf papers ls` — View daily papers.

### Discussions & Pull Requests (`hf discussions`)
- Manage the lifecycle of Hub contributions: `list`, `create`, `info`, `comment`, `close`, `reopen`, and `rename`.
- `diff`: View changes in a PR.
- `merge`: Finalize pull requests.

### Infrastructure & Compute
- **Endpoints:** Deploy and manage Inference Endpoints (`deploy`, `pause`, `resume`, `scale-to-zero`, `catalog`).
- **Jobs:** Run compute tasks on HF infrastructure. Includes `hf jobs uv` for running Python scripts with inline dependencies and `stats` for resource monitoring.
- **Spaces:** Manage interactive apps. Includes `dev-mode` and `hot-reload` for Python files without full restarts.

### Storage & Automation
- **Buckets:** Full S3-like bucket management (`create`, `cp`, `mv`, `rm`, `sync`).
- **Cache:** Manage local storage with `list`, `prune` (remove detached revisions), and `verify` (checksum checks).
- **Webhooks:** Automate workflows by managing Hub webhooks (`create`, `watch`, `enable`/`disable`).
- **Collections:** Organize Hub items into collections (`add-item`, `update`, `list`).

---

## Advanced Usage & Tips

### Global Flags
- `--format json`: Produces machine-readable output for automation.
- `-q` / `--quiet`: Limits output to IDs only.

### Extensions & Skills
- **Extensions:** Extend CLI functionality via GitHub repositories using `hf extensions install REPO_ID`.
- **Skills:** Manage AI assistant skills with `hf skills add`.

## Examples

```bash
# Download a model
hf download meta-llama/Llama-2-7b-chat-hf

# Upload a file
hf upload your-username/your-dataset data.csv --commit-message "Add training data"

# List models by task
hf models list --filter "text-classification"

# Query a dataset with SQL
hf datasets sql "SELECT * FROM dataset_name LIMIT 10"

# Deploy an endpoint
hf endpoints deploy your-username/your-model
```

## Pitfalls

- **Large downloads**: Models can be several GB — check file sizes with `hf download --no-deps --include "*.safetensors"` first
- **Token permissions**: Ensure your `HF_TOKEN` has write access if uploading, and the right repo scope
- **Deprecated commands**: `huggingface-cli` is removed — always use `hf`; `hf upload-large-folder` is deprecated, use `hf upload`
- **Cache management**: Download cache grows quickly — run `hf cache prune` periodically
- **Network timeouts**: Large model downloads may timeout — use `--resume` flag or increase timeout

## Verification

- [ ] Authentication verified with `hf whoami`
- [ ] Download completed without errors (check exit code)
- [ ] Uploaded files are visible on the Hub web UI
- [ ] Dataset SQL query returns expected columns and row count
- [ ] No stale cache consuming disk space (`hf cache prune` if needed)

## Related Skills

- `skill_view(name='huggingface-trackio')` — ML experiment tracking
- `skill_view(name='llama-cpp')` — Local GGUF model inference
