---
description: "React Native navigation choices (React Navigation 7 stable vs 8 alpha vs Expo Router) with npm versions and the default-branch trap; source-read"
source_repo: react-navigation/react-navigation (MIT)
tested_version: README and npm registry queries (dist-tags, versions, peer dependencies) on 2026-10-05; no React Native app was built or run
verified_date: "2026-10-05"
---

# React Native navigation (React Navigation vs Expo Router)

## Versions on npm (2026-10-05)

| Package | Version | Modified |
|---|---|---|
| `@react-navigation/native` | **7.5.0** (`latest`) | 2026-10-02 |
| `@react-navigation/native-stack` | 7.20.0 | 2026-10-02 |
| `@react-navigation/bottom-tabs` | 7.20.0 | 2026-10-02 |
| `@react-navigation/drawer` | 7.14.3 | 2026-10-02 |
| `@react-navigation/stack` (JS-based stack) | 7.12.0 | 2026-10-02 |
| `expo-router` | 57.0.24 | 2026-10-03 |
| `react-native-screens` | 4.28.0 | 2026-10-04 |
| `react-native-safe-area-context` | 5.10.1 | 2026-09-29 |

dist-tags for `@react-navigation/native`: `latest` 7.5.0, **`next` 8.0.0-alpha.50**, plus legacy `5.x` 5.9.8 and `4.x` 3.8.4.
`@react-navigation/native` 7.5.0 peers: `react >= 18.2.0`, `react-native *`.

## The default-branch trap

The GitHub repository's default branch README is headed **"React Navigation 8"** ("the upcoming major version"); the README lists `7.x` as the **latest stable** branch. Docs and code read from the default branch can describe
v8-alpha APIs that `npm install @react-navigation/native` (7.5.0) does not have. Match the docs version (reactnavigation.org version selector) and the installed package version before copying an API.

## Choosing

| Situation | Pick |
|---|---|
| Expo app, file-system routing, deep links and web for free | `expo-router` (built on React Navigation) |
| Bare React Native or custom navigator composition | `@react-navigation/native` + `native-stack` (native primitives) and `bottom-tabs` / `drawer` as needed |
| Need JS-driven custom transitions | `@react-navigation/stack` (JS) instead of `native-stack` |
| New project wanting v8 features | evaluate `next` (8.0.0-alpha.50) only if you accept alpha churn; pin an exact version |

Package family (from the README): `core`, `routers`, `native`, `native-stack`, `stack`, `bottom-tabs`, `drawer`, `material-top-tabs`, `elements`, `devtools`, plus `react-native-tab-view` and `react-native-drawer-layout`.
Native stack depends on `react-native-screens` and `react-native-safe-area-context`; install matching versions through `npx expo install` in Expo projects so they agree with the SDK.

## Practical rules

- Install the peer natives with the framework's tool (`npx expo install ...`) rather than the latest from npm, since native modules are tied to the React Native/Expo SDK version.
- Keep route param types in one place (a `RootStackParamList`) so navigation calls are type-checked.
- Do not mix Expo Router and a hand-built `NavigationContainer` in the same app root.
- Re-check this table before pinning: all of these packages move monthly.
