---
name: react-library-notes
description: "React 19, Next 16, Zustand, Motion: run-live traps."
version: 1.0.0
author: Hermes Agent (promoted from react-ecosystem references, run live 2026-10)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [react, nextjs, zustand, motion, ariakit, shadcn, react-native, deckgl, ssr, jsdom]
    related_skills: [react-ecosystem, frontend-library-picks, frontend-design, design-taste-frontend, publish-site]
---

# React library notes

## What This Skill Does

Per-library behaviour for the React stack's main pieces, each installed and exercised in Node (usually with jsdom or server rendering) so the traps are observed, not recalled: React 19.3, Next.js 16.3, Zustand 5, Motion 14 and its ancestor Popmotion 11, Ariakit, the shadcn CLI 4, deck.gl 9.4 and React Native 0.87 with React Navigation. `react-ecosystem` answers "which library for X"; this skill answers "how does the chosen one actually behave".

## When to Use

- Writing or debugging code against React 19, Next.js 16, Zustand 5, Motion 14, Ariakit, shadcn or deck.gl
- A hydration mismatch, stale closure, store selector or animation call fails in a way the docs do not explain
- Scaffolding with `create-next-app` or the shadcn CLI and the output differs from the tutorial
- Setting up React Native or choosing between React Navigation 7, 8 alpha and Expo Router
- Not for choosing libraries by need (`react-ecosystem`), non-React CSS/animation (`frontend-library-picks`), or visual design (`frontend-design`)

## Which reference

| Library | Reference | Key fact |
|---|---|---|
| React 19.3.0 | `references/react-19-core-notes.md` | ~70 probes: hoisted metadata and `_R_0_` ids in server output, StrictMode doubles effects, `useOptimistic`/`useActionState` need `globalThis.FormData` in jsdom, `Activity` keeps state, `React.cache` outside a request, removed APIs |
| Next.js 16.3.8 | `references/nextjs-16-notes.md` | scaffold 45 s, build 15 s, dev ready about 1 s; generated `AGENTS.md`/`CLAUDE.md` that `next dev` re-creates (disable with `agentRules: false`); 456 version-matched docs in `node_modules/next/dist/docs`; telemetry on by default |
| Zustand 5.0.15 | `references/zustand-v5-notes.md` | a fresh-object selector throws, removed equality arg, `setState(x, true)` drops actions, `persist` shallow merge and async hydration, no default export |
| Motion 14.0.0 (ex Framer Motion) | `references/motion-14-notes.md` | headless `animate` needs a rAF shim, a bad ease string throws asynchronously, SSR HTML ships the `initial` state, `LazyMotion` strict, `motion/mini` caveat |
| Popmotion 11.0.5 | `references/popmotion-11-notes.md` | frozen 2022; its `spring` gives the same numbers as Motion 14; `mix('#f00','#00f',.5)` returns `NaN#ff0000` (use `mixColor`); port to Motion rather than adopt |
| `@ariakit/react` 0.4.40 | `references/ariakit-notes.md` | store plus `render`-prop model; closed Dialog/Tooltip emit no SSR content; Tabs need `defaultSelectedId`; MIT packages vs proprietary Plus |
| shadcn CLI 4.21.2 | `references/shadcn-cli-4-notes.md` | `--defaults` help names a preset it rejects; default base is Base UI, not Radix; `cn` is now an npm package; `add -y` still prompts before overwriting an edited file (use `--diff`, then `-o`) |
| deck.gl 9.4.0 | `references/deckgl-notes.md` | all `@deck.gl/*` lockstep; default layer id collisions; `Deck` needs a DOM; pair with react-map-gl/maplibre |
| React Native 0.87.1 | `references/react-native-core.md` | Node and React peer requirements, Android vs iOS build host limits, monorepo layout, agent conventions from its AGENTS.md |
| React Navigation / Expo Router | `references/react-native-navigation.md` | v7 stable vs v8 alpha vs Expo Router; the default-branch (v8) docs trap |

## Procedure

1. Check the installed major against the reference (`npm ls react next zustand motion`); notes are pinned and dated 2026-10-05.
2. For server-rendered or tested code, reproduce the behaviour in jsdom or `renderToString` first; several traps only show there (hydration ids, `initial` state in SSR HTML, missing `FormData`).
3. Zustand: select primitives or use shallow selectors; never return a fresh object from a selector; check `persist` hydration timing.
4. Motion: import `motion` (not `framer-motion`), use `LazyMotion` strictly where bundle size matters, and install a rAF shim for headless tests.
5. Scaffolding tools: read the generated files (`AGENTS.md`, `components.json`, Tailwind setup) before editing; they change between CLI versions.
6. React Native: confirm Node and React peer versions first and decide Expo Router or React Navigation 7 before writing navigation code.
7. Add new probes and their observed output to the library's reference with version and date.

## Pitfalls

- Reading v8 (default-branch) React Navigation docs while using v7.
- Assuming Radix under shadcn: the 4.x CLI defaults to Base UI.
- `setState(x, true)` in Zustand 5 replaces the whole state and drops the store actions.
- Adopting Popmotion for new work; it is frozen and Motion supersedes it.
- Trusting jsdom for layout or transitions: it has none; real-browser behaviour is not covered by these notes.
- Version numbers drift within months; re-probe before quoting.

## Verification

- [ ] Installed majors match the references or the probe was re-run
- [ ] SSR output was inspected where the library renders on the server
- [ ] Generated scaffolding files were read, not assumed
- [ ] Any new trap was written back to the owning reference

## References

- `references/react-19-core-notes.md` - React 19.3.0 in Node + jsdom: server-render output, StrictMode effect doubling, batching and stale closures, optimistic/action state, `Activity`, `React.cache`, hydration errors, removed APIs
- `references/nextjs-16-notes.md` - Next.js 16.3.8 scaffold/build/dev on Windows, generated agent files, bundled docs, telemetry
- `references/zustand-v5-notes.md` - Zustand 5.0.15 traps on React 19.3 + jsdom: selectors, equality, `setState` replace, `persist`, no default export
- `references/motion-14-notes.md` - Motion 14.0.0 in Node + jsdom: spring/easing numbers, rAF shim, async ease errors, SSR initial state, `LazyMotion`
- `references/popmotion-11-notes.md` - Popmotion 11.0.5 (Motion's ancestor): identical spring numbers, deterministic driver, `mix` colour trap, port notes
- `references/ariakit-notes.md` - `@ariakit/react` 0.4.40: store and render-prop model, SSR output table, Tabs and disabled focus behaviour, licences
- `references/shadcn-cli-4-notes.md` - shadcn CLI 4.21.2 on a scratch Vite project: presets, Base UI default, `cn` package, Tailwind 4 without config, overwrite prompts
- `references/deckgl-notes.md` - deck.gl 9.4.0 layers/views model, Node-side construction, pairing with react-map-gl/maplibre
- `references/react-native-core.md` - React Native 0.87.1 requirements, build host limits, monorepo layout, AGENTS.md conventions
- `references/react-native-navigation.md` - React Navigation 7 vs 8 alpha vs Expo Router, npm versions, default-branch docs trap
