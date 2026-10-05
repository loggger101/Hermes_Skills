---
description: "Next.js 16.3.8 scaffold-build-dev run on Windows (45 s create, 15 s build, 1 s dev ready): generated AGENTS.md/CLAUDE.md that next dev rewrites, bundled docs in node_modules, telemetry, audit and lint notices"
source_repo: vercel/next.js (MIT)
tested_version: "create-next-app@latest -> next 16.3.8 (npm latest, modified 2026-10-05), react / react-dom 19.2.8, typescript ^5, eslint ^9; Node 22.23.2, npm 12.0.2, Windows 11, project under the Windows temp folder (not OneDrive). One scaffold, one production build, one `next dev` session with curl. No deployment, auth, database or Server Action work"
verified_date: "2026-10-05"
---

# Next.js 16 as an agent meets it (run)

`SKILL.md` names Next.js 16.x as the default framework. This is what a non-interactive scaffold actually produces and costs.

## Scaffold

```bash
npx -y create-next-app@latest app --ts --app --eslint --no-tailwind --src-dir --use-npm --no-react-compiler --import-alias "@/*" --yes
```

- Took **45 s** (344 packages installed in 34 s), then ran `next typegen` and `git init` with a first commit. `--yes` plus explicit flags
  means no prompts; leave a flag out and the CLI may ask.
- Generated: `AGENTS.md`, `CLAUDE.md`, `README.md`, `eslint.config.mjs`, `next-env.d.ts`, `next.config.ts`, `package.json`,
  `package-lock.json`, `public/`, `src/`, `tsconfig.json`. Scripts: `dev`, `build`, `start`, `lint` (`eslint`, not `next lint`).
- Install noise worth knowing: `npm warn deprecated eslint@9.39.5: This version is no longer supported`, an npm `install-scripts`
  notice (npm 12 asks you to approve lifecycle scripts with `npm install-scripts approve <pkg>`), and
  **"5 high severity vulnerabilities"** reported for the fresh install. Read `npm audit` before shipping; do not blanket `--force` fix.

## Agent files Next writes for you

The scaffold's `AGENTS.md` is a marked block (`<!-- BEGIN:nextjs-agent-rules --> ... END`) titled **"This is NOT the Next.js you know"**: it
tells agents the version has breaking changes and to read the relevant guide in **`node_modules/next/dist/docs/`** before
writing code. `CLAUDE.md` is one line: `@AGENTS.md`.

- The docs are real: `node_modules/next/dist/docs/` holds `01-app`, `02-pages`, `03-architecture`, `04-community` and `index.md`,
  **456 markdown files**, version-matched to the installed `next`. Search them instead of relying on training data.
- **`next dev` re-creates these files.** After deleting both, starting `next dev` printed
  `Generated AGENTS.md and CLAUDE.md for AI agents. Set agentRules: false in next.config to disable.` and both reappeared byte-identical
  (git status clean). Source: `node_modules/next/dist/server/lib/generate-agent-files.js`. Commit them with your work or set
  `agentRules: false`; don't fight them. In a monorepo the file warns that `next` may not resolve from the repo root.

## Timings (this machine, one run each)

| Step | Result |
|---|---|
| `npm run build` | **15.3 s**: "Next.js 16.3.8 (Turbopack)", compile 4.4 s, TypeScript 5.2 s, 4 static pages in 516 ms with 5 workers; routes `/` and `/_not-found` both static |
| `next dev -p 3123` | "Ready in 1010 ms"; first `GET /` 200 in **1.7 s** (compile), second 37 ms; `GET /nope` 404 in 225 ms |

**Turbopack is the default** for both dev and build in 16. **Telemetry is on by default**: the first build prints
"Next.js now collects completely anonymous telemetry"; set `NEXT_TELEMETRY_DISABLED=1` (or `npx next telemetry disable`) in CI and
agent runs. `du` over `node_modules` took over two minutes on this box (hundreds of small files): don't size or scan it in
a tool call with a short timeout.

## Practical rules

1. Pin the scaffold with explicit flags and `--yes`; check `package.json` for `next`, `react`, `react-dom` versions afterwards (`next`,
   `react`, `react-dom` and `eslint-config-next` are exact-pinned here at 16.3.8 / 19.2.8; the type packages use carets).
2. For any API question, grep `node_modules/next/dist/docs/` first.
3. Keep dev servers on a chosen port and stop them; set telemetry off; treat the audit warnings as a to-do.
4. Keep projects off OneDrive-synced folders (thousands of small files in `node_modules` and `.next`).

Not run: `next start` of the build, middleware/proxy, Server Actions, image optimisation, `output: 'export'`, deployment targets, the
React compiler option, Tailwind variants, or the repo's own contribution workflow (its `AGENTS.md` was not read).
