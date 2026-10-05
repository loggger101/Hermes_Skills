---
name: react-ecosystem
description: "Pick React libraries by need, with live npm freshness."
version: 1.0.0
author: Hermes Agent (from enaqx/awesome-react, CC0 list, plus live npm checks)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [react, frontend, libraries, state-management, routing, component-library, nextjs, ecosystem]
    related_skills: [frontend-design, nicegui-app-builder, static-site-patterns, design-md, publish-site]
---

<!-- source: enaqx/awesome-react (curated list) + `npm view` of every pick, 2026-10-05; the table is a dated snapshot, re-run `npm view <pkg> version time.modified deprecated` before committing to a dependency -->

# React ecosystem guide

## What This Skill Does

Answers "which React library for X" with a short default per category, the alternatives worth considering, and a dated
freshness snapshot so you do not recommend a package that has been renamed, deprecated or abandoned. The full per-category
map is in `references/awesome-react-map.md`.

## When to Use

- Starting or extending a React / React Native project and choosing a framework, router, state, data-fetching, UI kit, styling, forms, tables, charts, or tests
- Auditing a React `package.json` for stale or renamed packages
- Not for plain static sites (`static-site-patterns`), Python UIs (`nicegui-app-builder`), or deciding the visual design (`frontend-design`, `design-md`)

## Defaults by need (2026-10-05)

| Need | Default | Consider instead | Note |
|---|---|---|---|
| Framework (SSR, routing, data) | **Next.js** 16.x | `react-router` 8 in framework mode (Remix merged into it); `vike` | `@remix-run/react` is still 2.17.x; new work goes through `react-router` |
| SPA tooling | **Vite** 8 | Parcel 2 | |
| Client state | **Zustand** 5 | Jotai 3 (atoms), Redux Toolkit 2 (large teams, devtools), MobX 7, XState 5 for statecharts | Do not put server data in client state stores |
| Server data / caching | **TanStack Query** 5 | SWR 2, Apollo Client 4 (GraphQL), Relay | |
| Routing (SPA) | `react-router` 8 | TanStack Router (type-safe) | |
| UI components, unstyled + Tailwind | **shadcn/ui** (Radix + Tailwind) | Headless UI, Ariakit, Radix primitives | copy-in components, you own the code |
| UI kit, enterprise/back-office | **Ant Design** 6 | MUI 9, Mantine 9, Chakra 3, Fluent UI 9 | see `design-md/references/antd-v6-design-md-exemplar.md` |
| Forms | React Hook Form 7 + Zod 4 | TanStack Form 1 | Formik 2.4.9 last touched 2025-11: avoid for new work |
| Tables | TanStack Table 9 (headless) | react-data-grid (still `7.0.0-beta.61`) | |
| Charts | Recharts 3 | visx 4, Victory 37, Nivo (0.99, last modified 2025-05) | |
| Animation | **Motion** 14 (`motion`, formerly `framer-motion`) | CSS, GSAP | `framer-motion` and `motion` both at 14.0.0 |
| Styling | Tailwind 4 | CSS Modules, vanilla-extract (zero runtime) | runtime CSS-in-JS (styled-components 6, Emotion 11) costs render time; prefer zero-runtime |
| Testing | Jest 30 + React Testing Library 16 | Playwright 1.63 or Cypress 16 for e2e | |
| Mobile | React Native 0.87 with Expo 57 | | React Navigation 7 (`@react-navigation/native` 7.5.0; v8 is alpha) or Expo Router; see `references/react-native-navigation.md` |
| Video from React | Remotion 4 | | |

## Freshness traps found by checking npm

- `refine` on npm is a 2022 placeholder (`0.0.1-alpha`); the real package is `@refinedev/core`.
- `loadable-components` is **deprecated** in favour of `@loadable/component`.
- `react-uploady` is a 404 on npm; the package is `@rpldy/uploady` (1.13.0, modified 2025-11-26).
- `why-did-you-render` last modified 2022-05; `eslint-plugin-react` 2025-04; `redux` core 5.0.1 from 2024-05 (use Redux Toolkit). Check these still behave on React 19 before adding.
- `react-bootstrap` 2.10.10 last modified 2025-09; fine but slow-moving.

## Procedure

1. Name the category, take the default from the table, and run `npm view <pkg> version time.modified deprecated --json` for it.
2. Prefer packages with a release in the last 6 months, no `deprecated` field, and a peer range that covers the project's React major (React is 19.3.0 here).
3. Prefer one library per concern; do not add a second state or data library "just in case" (`ponytail` ladder: reuse, platform, installed, then new).
4. Record the choice and the reason where the team will see it (ADR or README), including the freshness date.

## Pitfalls

- A list entry is a pointer, not an endorsement; awesome lists include stale and promotional items.
- Version numbers here are a snapshot; majors change within months (several above crossed a major recently: MUI 9, Mantine 9, Jotai 3, Preact 11, Apollo 4, Vite 8, Motion 14).
- Package renames hide in plain sight (`framer-motion` to `motion`, Remix to React Router, `loadable-components` to `@loadable/component`): search the registry for the current name before pinning.

## References

- `references/awesome-react-map.md` - per-category picks from the awesome-react list with npm version and last-modified date for each
- `references/react-native-navigation.md` - React Navigation 7 stable vs 8 alpha vs Expo Router, npm versions, the default-branch (v8) docs trap
- `references/deckgl-notes.md` - deck.gl 9.4.0 (all @deck.gl/* lockstep): layers/views model, Node-side layer construction checked (default id collisions, `Deck` needs a DOM), pairing with react-map-gl/maplibre, rules
- `references/react-native-core.md` - React Native 0.87.1 requirements (Node, React peer), Android vs iOS build host limits, monorepo layout, agent conventions from its AGENTS.md
- `references/zustand-v5-notes.md` - Zustand 5.0.15 traps run on React 19.3 + jsdom: fresh-object selector throws, removed equality arg, `setState(x, true)` drops actions, `persist` shallow merge / dropped versions / async hydration, no default export
- `references/ariakit-notes.md` - `@ariakit/react` 0.4.40 (190 exports) server-rendered and driven in jsdom: store + `render`-prop model, SSR HTML table (closed Dialog/Tooltip emit no content, Select/Menu lists and Tab panels do, Tabs need `defaultSelectedId`), disabled Tabs still arrow-focusable, MIT packages vs proprietary Plus examples and website
- `references/shadcn-cli-4-notes.md` - shadcn CLI 4.21.2 run live on a scratch Vite project: `--defaults` help names a preset (`base-nova`) it rejects, default base is Base UI not Radix, `cn` is now an npm package, Tailwind 4 with no config file, `add -y` still prompts before overwriting an edited file (use `--diff` then `-o`), `search` needs a configured registry.
- `references/standard-and-neostandard-notes.md` - standard 17.1.2 (still on ESLint 8.57.1, marked unsupported) vs neostandard 0.13.0 on ESLint 9.39.5, same 10 findings on a planted file; `--fix` limits, unflagged trailing `;`, parse errors on the regex `v` flag and `using`, TypeScript files ignored/failing.
- `references/popmotion-11-notes.md` - Popmotion 11.0.5 (frozen 2022, Motion's ancestor) run in plain Node: its `spring` generator gives numbers identical to Motion 14's (34.03, 84.943, 115.312, ...), deterministic `driver` stepping, `mix` is numeric-only (`mix('#f00','#00f',.5)` returns `NaN#ff0000`, use `mixColor`), port-to-Motion notes
- `references/motion-14-notes.md` - Motion 14.0.0 (ex Framer Motion) run in Node + jsdom: spring/easing numbers, headless `animate` needs a rAF shim imported first, a bad ease string throws asynchronously, jsdom globals needed, SSR HTML ships the `initial` state, LazyMotion strict, `motion/mini` caveat.
- `references/react-19-core-notes.md` - React 19.3.0 run in Node + jsdom (~70 probes): server-render output (hoisted metadata, `_R_0_` ids, renderToString vs Suspense), StrictMode effect doubling, batching and stale closures, useOptimistic/useActionState (jsdom needs `globalThis.FormData`), Activity keeps state, `React.cache` outside a request, hydration mismatch errors, removed APIs.
- `references/bun-runtime-notes.md` - Bun 1.4.2 on Windows, about 40 commands run: npm 11 blocks its postinstall (`npm rebuild bun` after approving), no type checking, text `bun.lock`, 0.4 s `bun add`, built-in `bun test` (exit 1 even when no file matches), `--compile` makes an 86 MB exe, `Bun.write` keeps LF, startup 54 ms vs node 116 ms.
- `references/nextjs-16-notes.md` - Next.js 16.3.8 scaffold/build/dev run on Windows: 45 s create, 15 s build, ~1 s dev ready; generated `AGENTS.md`/`CLAUDE.md` that `next dev` re-creates (disable with `agentRules: false`); 456 version-matched docs inside `node_modules/next/dist/docs`; telemetry on by default.
