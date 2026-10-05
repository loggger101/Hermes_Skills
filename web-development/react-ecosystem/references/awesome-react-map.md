---
description: "awesome-react categories with npm latest version and last-modified date for each pick (snapshot 2026-10-05), plus stale/renamed flags"
source_repo: enaqx/awesome-react (CC0 list); versions from `npm view <pkg> version time.modified deprecated`, run 2026-10-05
tested_version: npm registry queries only; no package installed or run
verified_date: "2026-10-05"
---

# awesome-react map with freshness

Versions are npm `latest` and the registry `time.modified` date on 2026-10-05. `time.modified` moves on any metadata
change, so treat it as an upper bound on last release. Re-run `npm view <pkg> version time.modified deprecated --json` before relying on a row.

## Frameworks and routing

| Package | Latest | Modified | Note |
|---|---|---|---|
| `next` | 16.3.8 | 2026-10-05 | default framework |
| `react-router` | 8.4.0 | 2026-09-15 | Remix's successor; framework mode |
| `@remix-run/react` | 2.17.5 | 2026-06-01 | legacy line |
| `gatsby` | 5.16.1 | 2026-06-30 | slow-moving |
| `vike` | 0.4.267 | 2026-10-04 | 0.x, active |
| `@tanstack/react-router` | 1.170.41 | 2026-09-30 | type-safe routing |
| `react-admin` | 5.15.4 | 2026-09-25 | B2B admin framework |
| `@refinedev/core` | 5.0.12 | 2026-04-20 | npm `refine` is a 2022 placeholder |
| `vite` | 8.3.2 | 2026-10-01 | |
| `parcel` | 2.16.4 | 2026-02-03 | |

## Component libraries

| Package | Latest | Modified |
|---|---|---|
| `antd` | 6.6.5 | 2026-09-20 |
| `@mui/material` | 9.4.0 | 2026-08-27 |
| `@chakra-ui/react` | 3.37.0 | 2026-08-28 |
| `@mantine/core` | 9.6.3 | 2026-09-26 |
| `@fluentui/react-components` | 9.74.9 | 2026-10-05 |
| `react-bootstrap` | 2.10.10 | 2025-09-22 |
| `@ariakit/react` | 0.4.40 | 2026-09-14 |
| `@headlessui/react` | 2.2.10 | 2026-04-13 |
| `radix-ui` | 1.6.7 | 2026-07-31 |
| `react-email` | 6.11.0 | 2026-09-23 |
| `lucide-react` | 1.52.0 | 2026-10-04 |

shadcn/ui is not a package: it copies component source (Radix + Tailwind 4.3.3) into your repo via its CLI.

## State and data

| Package | Latest | Modified | Note |
|---|---|---|---|
| `zustand` | 5.0.15 | 2026-08-13 | |
| `jotai` | 3.0.1 | 2026-09-29 | |
| `@reduxjs/toolkit` | 2.13.0 | 2026-09-29 | use this, not bare `redux` |
| `redux` | 5.0.1 | 2024-05-06 | core only |
| `mobx` | 7.0.6 | 2026-10-02 | |
| `xstate` | 5.33.2 | 2026-10-03 | |
| `immer` | 11.1.21 | 2026-10-02 | |
| `@tanstack/react-query` | 5.104.1 | 2026-10-02 | |
| `swr` | 2.5.1 | 2026-09-22 | |
| `@apollo/client` | 4.3.1 | 2026-09-18 | |

## Styling

| Package | Latest | Modified | Note |
|---|---|---|---|
| `tailwindcss` | 4.3.3 | 2026-09-25 | |
| `styled-components` | 6.5.3 | 2026-09-25 | runtime CSS-in-JS |
| `@emotion/react` | 11.14.0 | 2026-05-12 | runtime CSS-in-JS |
| `@vanilla-extract/css` | 1.21.2 | 2026-07-27 | zero runtime |

## Forms, tables, charts, maps

| Package | Latest | Modified | Note |
|---|---|---|---|
| `react-hook-form` | 7.89.0 | 2026-09-26 | |
| `@tanstack/react-form` | 1.33.5 | 2026-08-21 | |
| `formik` | 2.4.9 | 2025-11-10 | avoid for new work |
| `zod` | 4.6.5 | 2026-10-02 | schema validation |
| `@rjsf/core` | 6.11.0 | 2026-09-29 | forms from JSON Schema |
| `@formily/core` | 2.3.7 | 2025-05-15 | Alibaba; slow-moving |
| `@tanstack/react-table` | 9.2.6 | 2026-10-04 | headless |
| `react-data-grid` | 7.0.0-beta.61 | 2026-07-14 | still beta |
| `react-grid-layout` | 2.2.4 | 2026-07-29 | |
| `recharts` | 3.10.1 | 2026-10-03 | |
| `@visx/visx` | 4.0.0 | 2026-06-11 | |
| `victory` | 37.3.6 | 2026-07-20 | |
| `@nivo/core` | 0.99.0 | 2025-05-23 | |
| `@xyflow/react` | 12.12.0 | 2026-09-24 | node-based editors |
| `react-map-gl` | 8.1.3 | 2026-09-02 | |
| `react-leaflet` | 5.0.0 | 2024-12-14 | stable, quiet |

## Renderers, i18n, animation, misc

| Package | Latest | Modified | Note |
|---|---|---|---|
| `@react-three/fiber` | 9.8.1 | 2026-10-02 | Three.js renderer |
| `ink` | 8.0.0 | 2026-10-03 | React for CLIs |
| `remotion` | 4.0.532 | 2026-10-01 | video from React |
| `@react-pdf/renderer` | 4.9.0 | 2026-08-27 | PDFs from React |
| `markdown-to-jsx` | 9.10.3 | 2026-09-15 | |
| `react-i18next` | 17.0.15 | 2026-09-21 | |
| `react-intl` | 12.1.3 | 2026-09-24 | FormatJS |
| `motion` / `framer-motion` | 14.0.0 | 2026-10-02 | both at 14.0.0 |
| `@react-spring/web` | 10.1.2 | 2026-10-01 | the `react-spring` package itself is 10.0.4 |
| `@formkit/auto-animate` | 0.10.0 | 2026-07-10 | |
| `preact` | 11.0.0 | 2026-09-30 | |
| `ai` (Vercel AI SDK) | 7.0.127 | 2026-10-01 | |
| `@floating-ui/react` | 0.27.20 | 2026-07-11 | |
| `downshift` | 9.4.0 | 2026-06-30 | |
| `react-error-boundary` | 6.1.6 | 2026-09-20 | |

## Dev tools and tests

| Package | Latest | Modified | Note |
|---|---|---|---|
| `react` | 19.3.0 | 2026-10-02 | |
| `react-native` | 0.87.1 | 2026-10-05 | with `expo` 57.0.26 |
| `jest` | 30.5.2 | 2026-09-18 | |
| `@testing-library/react` | 16.3.3 | 2026-08-27 | |
| `playwright` | 1.63.0 | 2026-10-05 | |
| `cypress` | 16.1.1 | 2026-09-29 | |
| `react-scan` | 0.5.7 | 2026-05-27 | render performance scanner |
| `eslint-plugin-react` | 7.37.5 | 2025-04-03 | quiet |
| `why-did-you-render` | 1.0.1 | 2022-05-24 | stale; check against React 19 |

## Flagged

- `refine` (npm name) = 2022 placeholder `0.0.1-alpha`; use `@refinedev/core`.
- `loadable-components` = **deprecated** ("Please use @loadable/component"); `@loadable/component` 5.16.7, modified 2025-05-18.
- `react-uploady` = 404 on the npm registry under that name; the list entry's package name differs from the repo name.
