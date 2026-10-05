---
description: "React Native 0.87.1 requirements (Node, React peer), what you can and cannot build per OS, the monorepo layout and agent conventions from its AGENTS.md; npm/README-sourced"
source_repo: react/react-native (formerly facebook/react-native; MIT)
tested_version: npm metadata (react-native 0.87.1, engines, peer dependencies, dist-tags) and the repo AGENTS.md read 2026-10-05; no React Native project was created or built; Node 22.23.2 on this machine checked against the engines range
verified_date: "2026-10-05"
---

# React Native core: requirements and repo conventions

The project now lives at `github.com/react/react-native` (the `react` organisation). npm `react-native` **0.87.1** (2026-10-05, MIT).

## Requirements (from npm)

| Item | Requirement |
|---|---|
| Node | `^22.13.0 || ^24.3.0 || >= 26.0.0` (this machine's Node 22.23.2 satisfies it) |
| React peer | `react ^19.2.3` and `@types/react ^19.1.1` (npm `react` is 19.3.0) |
| Release lines | many `*-stable` dist-tags back to 0.63 (`0.81-stable` 0.81.6, `0.83-stable` 0.83.10, ...); stay on one line and upgrade deliberately, since native modules are tied to the React Native version |

## What you can build on which OS (from the repo's own AGENTS.md)

- **JavaScript work** (lint, Flow/TypeScript type checks, Jest, Metro bundling) needs only Node and Yarn, on any platform.
- **Android** builds need the Android SDK and NDK with Gradle (works on Windows, macOS, Linux).
- **iOS** builds need Xcode with CocoaPods or Swift Package Manager, which means **macOS only**. A Windows/Linux machine cannot produce an iOS build locally; use a Mac or a cloud build service.
- Formatting of the repo itself covers JS/TS, C/C++/Objective-C, Kotlin, Java, Python (pinned Ruff) and Swift, requiring a JDK 17+, Python 3 and a Swift 6.3+ toolchain in addition to Node (contributors only).

## Repo layout (monorepo)

| Path | Contents |
|---|---|
| `packages/react-native/Libraries`, `src/private` | JavaScript (Flow); `Libraries` is the legacy location being moved to `src/private` |
| `packages/react-native/ReactCommon` | shared C++: Fabric renderer, TurboModules, JSI, Yoga, `jsinspector-modern` |
| `packages/react-native/ReactAndroid`, `React`, `ReactApple` | Android (Kotlin/Java/JNI) and Apple (Obj-C++/Swift) runtimes |
| `packages/rn-tester` | RNTester showcase app with a `Playground` scratch surface |
| `packages/*` | Metro config, Codegen, ESLint config, dev-middleware, DevTools frontend |
| `private/*` | `helloworld` sample app, `react-native-fantom` test runner |

Architecture notes sit in `__docs__` directories next to the code they describe.

## Agent-facing conventions worth copying (from its AGENTS.md)

- State the environment precisely (package manager pinned via `packageManager`: Yarn v1; run commands from the repo root) and what needs what (JS-only versus native toolchains).
- A command table: `yarn test <path>` (Jest), `yarn fantom <path>` (integration tests named `*-itest.js`, building a native tester on first run), `yarn lint` (`--max-warnings 0`), `yarn flow-check`, `yarn format` / `yarn format-check` and per-language variants.
- A **verification step proportional to the change**: `yarn start` serves RNTester over Metro at `http://localhost:8081`, and a `curl` of the bundle URL (`/js/RNTesterApp.bundle?platform=ios&dev=...`) checks that the bundler builds; reserved for changes that must be seen running (UI behaviour).
- CI is named: JavaScript CI is the `lint`, `test_js` and `build_js_types` jobs, with separate Fantom and native jobs, so an agent knows which checks gate a merge.

## Choosing around it

Navigation: `react-native-navigation.md` in this folder. Library choices (state, data, forms, tests): `react-ecosystem/references/awesome-react-map.md` and `SKILL.md`. Expo (`expo` 57.0.26) wraps React Native with managed builds and Expo Router, and is the easiest path when you lack a Mac.
