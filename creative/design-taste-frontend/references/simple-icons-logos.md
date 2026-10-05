---
description: "simple-icons 16.34.0 / cdn.simpleicons.org checked live: LinkedIn, Slack, Microsoft, AWS, Adobe, OpenAI are absent (npm and CDN 404), X replaces Twitter; API shape, 5 MB root import, brand-guideline caveat"
source_repo: simple-icons/simple-icons (CC0-1.0 package; individual brand marks stay their owners' trademarks)
tested_version: "npm simple-icons 16.34.0 (modified 2026-10-04) installed in a scratch folder under Node 22.23.2; cdn.simpleicons.org requested with curl on 2026-10-05 for 7 slugs"
verified_date: "2026-10-05"
---

# Simple Icons for logo walls

`SKILL.md` recommends Simple Icons for "Trusted by / Used by" logo walls and says it "covers most known brands". It covers
3 464 icons, but **not every brand a customer wall needs**, and a missing slug fails silently as a broken image.

## Brands that are not there (run)

Searched in `data/simple-icons.json` (3 464 entries) and via the CDN:

| Brand | Package data | `cdn.simpleicons.org/<slug>/ffffff` |
|---|---|---|
| LinkedIn, Microsoft, Adobe, Amazon Web Services | no entry | `linkedin`, `microsoft`: **404** |
| Slack | only "Slackware" | `slack`: **404** |
| OpenAI | only "OpenAI Gym" | `openai`: **404** |
| Twitter | no `siTwitter`; the entry is **"X"** (`aliases.aka: ["Twitter"]`, export `siX`, slug `x`) | `x`: 200 |
| GitHub, YouTube, Google (+ many Google products), Facebook, Instagram, Meta, Anthropic, Claude | present | `github`, `anthropic`: 200 |

I did not establish why the first group is absent (the data simply has no entry). The project's
`DISCLAIMER.md` also says that CC0 for the package "doesn't mean to imply that all icons within the project are also CC0",
that missing licence data does not mean there is no licence, and that users should read it before including an icon.
Practical rule: check the slug in `data/simple-icons.json` (or request the CDN URL and expect 200) **before** designing
the wall, and fall back to the brand's own press kit or a text wordmark (with permission) for absent brands. Never invent
a lookalike mark for a real company.

## API (run, Node CJS)

```js
const si = require('simple-icons');          // 3464 named exports: siGithub, siX, siDotenv ...
si.siGithub  // { title:'GitHub', slug:'github', svg:'<svg role="img" viewBox="0 0 24 24" ...><title>GitHub</title><path .../></svg>',
             //   path, source, hex:'181717', guidelines }       (guidelines present on 837 of 3464 icons)
const sdk = require('simple-icons/sdk');     // titleToSlug, slugToVariableName, getIconSlug, getIconsData, svgToPath, ...
sdk.titleToSlug('AT&T')  // 'atandt' ;  sdk.titleToSlug('C++') // 'cplusplus'
```

- Subpaths: `simple-icons/icons` (named exports without the data), `simple-icons/icons/<slug>.svg` (single file), `simple-icons/icons.json`
  (data), `simple-icons/sdk`. Importing `simple-icons/package.json` throws `ERR_PACKAGE_PATH_NOT_EXPORTED`.
- Icons are one 24x24 path with **no fill**; colour them yourself: `svg.replace('<svg ', '<svg fill="#'+hex+'" ')` (brand
  colour) or `fill="currentColor"` for a one-colour wall that follows the theme.
- `require('simple-icons')` loads a 5.25 MB `index.js`: 51 ms and about 45 MB RSS here. In a browser bundle import named
  icons from an ESM build with tree shaking, or read just `icons/<slug>.svg` (0.3 ms) at build time and inline it.
- Variable names are `si` + a transformed title/slug, so verify an export exists before using it (`si.siX`, not `si.siTwitter`).

## Logo-wall checklist

1. Look the slug up first; list the brands that are missing and decide per brand.
2. Inline the SVG with `fill="currentColor"` and set colour with CSS so it works in light and dark.
3. Keep `<title>` for accessibility, or set `aria-label` and drop `role="img"` duplication.
4. Do not alter proportions or recolour a mark against its `guidelines` entry where one exists.
5. Contributing here: the repo requires disclosure of AI tool use in the PR (see
   `github/github-pr-workflow/references/ai-policies-of-starred-repos.md`).

Not run: a rendered logo wall, the CDN size/colour parameters beyond `/<slug>/ffffff`, the browser ESM tree-shaking, the
project's `lint`/`build` scripts, or the separate site icon preview.
