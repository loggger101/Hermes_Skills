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
| Mobile | React Native 0.87 with Expo 57 | | React Navigation 7 (`@react-navigation/native` 7.5.0; v8 is alpha) or Expo Router; see `web-development/react-library-notes/references/react-native-navigation.md` |
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
- `skill_view(name='js-tooling-notes')` — Bun runtime and standard/neostandard linting, plus PostCSS and js-beautify (moved there in round-251)
- `skill_view(name='react-library-notes')` - per-library traps for React 19, Next.js 16, Zustand 5, Motion 14, Popmotion, Ariakit, shadcn CLI, deck.gl and React Native (moved there in round-250)
