---
description: "Deploying to Cloudflare Workers/Pages from GitHub Actions with wrangler-action v4: inputs, outputs, permissions, preview-per-PR, secrets"
source_repo: cloudflare/wrangler-action (Apache-2.0)
tested_version: README and action.yml read via GitHub API @ v4.1.3 (2026-09-24); no workflow was run against a Cloudflare account
verified_date: "2026-10-05"
---

# Cloudflare deploys from CI (wrangler-action v4)

`publish-site` deploys by hand with `wrangler`. When the site should redeploy on every merge, or get a
preview URL per pull request, run the same commands in GitHub Actions through `cloudflare/wrangler-action@v4`.
It installs Wrangler, runs your command, and exposes the deployment URL as an output.

## Minimal workflows

Workers deploy on merge (the default `command` is `deploy`):

```yaml
on: { push: { branches: [main] } }
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: cloudflare/wrangler-action@v4
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
```

Static site to Pages (build first; Pages needs `accountId`):

```yaml
    permissions: { contents: read, deployments: write }   # deployments:write only when gitHubToken is set
    steps:
      - uses: actions/checkout@v6
      - run: npm ci && npm run build
      - id: deploy
        uses: cloudflare/wrangler-action@v4
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          command: pages deploy dist --project-name=my-site
          gitHubToken: ${{ secrets.GITHUB_TOKEN }}        # optional: records a GitHub Deployment
      - run: echo "${{ steps.deploy.outputs.deployment-url }}"
```

A non-`main` branch gets a preview deployment, and `pages-deployment-alias-url` is its stable branch URL.

## Inputs (from `action.yml`)

| Input | Notes |
|---|---|
| `apiToken`, `accountId` | credentials; keep both in repo secrets. Global API key + email auth is no longer supported (v3+); use a scoped API token |
| `command` | Wrangler command; multi-line allowed, one command per line; default `deploy` |
| `wranglerVersion` | any npm spec: `4.81.0`, `4`, `^4.0.0`, `latest`. Omitted: uses an installed Wrangler if present, else a default. **Quote it** (`"4"`) so YAML keeps it a string. The action defaults to Wrangler v4; pin `3.x` explicitly to stay on v3 |
| `workingDirectory` | run from a subfolder (monorepos) |
| `environment` | named environment from the Wrangler config, for `deploy --env` and per-env secrets |
| `secrets` | newline list of names; each must also be set in the step's `env:`; they become Worker secrets |
| `vars` | same shape, bound as plain (non-secret) variables |
| `preCommands` / `postCommands` | shell or `wrangler` commands before/after, e.g. `wrangler kv:key put ...` |
| `packageManager` | otherwise inferred from the lockfile |
| `quiet` | suppress Wrangler output |
| `gitHubToken` | enables GitHub Deployments and job summary |

## Outputs

`command-output`, `command-stderr`, `deployment-url` (Workers, Workers Preview or Pages), `pages-deployment-alias-url`
(Wrangler >= 3.78), `pages-deployment-id` and `pages-environment` (>= 3.81), and for Workers Previews (>= 4.136.3)
`preview-url`, `preview-deployment-url`, `preview-name`, `preview-id`, `preview-deployment-id`. Pass outputs through
`env:` into `run:` steps instead of interpolating `${{ ... }}` directly into the script, so a URL or log line cannot inject shell.

## Preview per pull request (Workers)

```yaml
on: [pull_request]
permissions: { contents: read, deployments: write }
...
      - id: preview
        uses: cloudflare/wrangler-action@v4
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          wranglerVersion: "4.136.3"
          command: preview --name pr-${{ github.event.pull_request.number }}
          gitHubToken: ${{ secrets.GITHUB_TOKEN }}
```

Previews need Wrangler 4.136.3 or newer, so pin `wranglerVersion` explicitly.

## Other triggers

- `schedule:` with cron for periodic redeploys (data-baked sites); `workflow_dispatch:` with an `environment` input feeding `command: deploy --env ${{ github.event.inputs.environment }}` for manual releases.
- `command: versions upload` creates a Worker version without deploying it; promote later with `wrangler versions deploy` (gradual rollouts).

## Pitfalls

- **Fork PRs get no secrets.** A `pull_request` from a fork cannot read `CLOUDFLARE_API_TOKEN`; do not "fix" this with `pull_request_target` plus a checkout of the fork's code, which runs untrusted code with your secret.
- Scope the API token to what the job needs (Workers Scripts edit, or Pages edit, for one account); an all-access token in CI is the blast radius.
- Pin the action to a major (`@v4`), and Wrangler to a version, for reproducible deploys; `latest` lets a Wrangler release change a production deploy.
- Each name in `secrets:` must also appear in the step's `env:` (per `action.yml`); after the first deploy confirm they bound with `wrangler secret list`.
- Commands run from `workingDirectory` when set, so `pages deploy <dir>` paths are relative to it.

Pitfalls 1-3 are general GitHub Actions / Cloudflare hygiene, not statements from the action's README.
