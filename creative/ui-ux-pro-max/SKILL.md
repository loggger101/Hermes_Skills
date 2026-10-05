---
name: ui-ux-pro-max
description: "Design-system generator: BM25 search over UI/UX data."
version: 1.0.0
author: Hermes Agent (ported from nextlevelbuilder/ui-ux-pro-max-skill, MIT)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design, ui, ux, design-system, palettes, typography, accessibility, landing-page, reasoning]
    related_skills: [design-taste-frontend, popular-web-designs, design-md, frontend-design, no-ai-slop]
---

<!-- source: nextlevelbuilder/ui-ux-pro-max-skill src/ui-ux-pro-max (MIT, clone @ main 2026-10-05). Omitted to keep size down: google-fonts.csv, google-font-licenses.json, phosphor-icons-upstream.json, tests, validate_data.py -->

# UI UX Pro Max (searchable design intelligence)

## What This Skill Does

Gives an agent a local, offline knowledge base for UI/UX decisions and a script that searches it. The data are CSV tables: 88 UI styles (79 searchable), 192 product types each with a
matched palette and a reasoning profile, 74 font pairings, 119 UX guidelines, 25 chart types, 35 landing-page patterns, 17 motion presets, 105 curated icons, and per-stack guideline tables for 22 stacks (React, Next.js, Vue, Svelte, Astro,
SwiftUI, React Native, Flutter, Angular, shadcn, html-tailwind, Three.js, Jetpack Compose, and more). `search.py` ranks rows with BM25 and can assemble a complete **design system** recommendation
(pattern, style, colour tokens with on-colours, typography, key effects, things to avoid, pre-delivery checklist) for a product description.

## When to Use

- Starting a UI for a named product type and wanting a defensible palette, type pairing and page pattern rather than the model's defaults
- Looking up a UX rule (contrast, touch targets, forms, motion) or a stack-specific guideline (`--stack react`)
- Producing a persistent `MASTER.md` design system for a project, with page-level overrides
- Complements `design-taste-frontend` (dial-based taste rules) and `design-md` (token files); use it as an input to those, not instead of looking at the result

## Usage (run from `scripts/`; stdlib Python, UTF-8 output forced)

```bash
python search.py "wellness spa booking calm" --design-system -p "Serenity Spa"          # full design-system recommendation
python search.py "meditation app" --design-system --variance 3 --motion 2 --density 3    # taste dials 1-10
python search.py "glassmorphism" --domain style                                          # one domain
python search.py "form validation" --stack react                                         # stack guidelines
python search.py "contrast accessibility" --domain ux --max-results 2
python search.py "..." --design-system --persist -p "Name" --output-dir "<project-root>" [--page dashboard] [--force]
```

Domains: `style`, `color`, `chart`, `landing`, `product`, `ux`, `typography`, `icons`, `gsap`, `react`, `web` (the upstream `google-fonts` domain needs `google-fonts.csv`, which is **not** vendored here; it fails with "File not found").
`--persist` writes `design-system/<project-slug>/MASTER.md` and refuses to overwrite an existing one without `--force`, so earlier design decisions are not lost; always pass `--output-dir` pointing at the project root, since the default is the current directory.
`--variance` (centered/minimal to bold/asymmetric), `--motion` (subtle to complex; attaches a GSAP snippet) and `--density` (spacious to dashboard-dense, overrides the spacing scale) bias the recommendation.

## Verified here (Windows, Python 3.14, vendored subset)

- The Serenity Spa query returned pattern "Hero + Testimonials + CTA", style "Soft UI Evolution" (light supported, avoid dark), a 16-token palette with `on-*` colours (primary `#EC4899`, background `#FDF2F8`), typography Lora / Raleway (mood calm/wellness/spa), key effects, an Avoid list, and a pre-delivery checklist (no emoji icons, visible focus, `prefers-reduced-motion`, 4.5:1 contrast, responsive at 375/768/1024/1440).
- The dial query (`--variance 3 --motion 2 --density 3`) for "meditation app" returned a different style ("Minimalism & Swiss Style") and palette (primary `#7C3AED`) than the default run, confirming the dials change the output.
- `--domain ux "contrast accessibility"` returned a High-severity rule: "Minimum 4.5:1 ratio for normal text" with a good (`#333` on white, 7:1) and bad (`#999` on white, 2.8:1) example. `--stack react` returned stack rows (Category/Guideline/Do/Don't).
- A query "fintech dashboard dense" returned the landing pattern "Enterprise Gateway" (contact-sales CTA): the pattern engine is landing-page oriented, so for an app dashboard take the style, palette and UX rules and ignore the page pattern.

## Pitfalls

- The reasoning is lookup, not judgement: check the palette contrast yourself (the generated pairs carry `on-*` colours, but verify with `design-md` lint or a contrast checker) and look at a rendered result.
- The upstream project counts 9 deprecated and 29 supplemental styles; only 79 are searchable. Data freshness metadata is in `data/data-provenance.json` (`manual-verified` 365 days, `needs-review` 90 days) and `data/catalog-summary.json` (verified 2026-08-26).
- Google Fonts links in the output load fonts from Google's CDN at page load; self-host for privacy or CSP-restricted sites (see `static-site-seo`).
- Treat generated copy-ready CSS tokens as a starting point; keep one source of truth for tokens in the project.

## References

- `data/*.csv` - the knowledge tables; `data/stacks/*.csv` - per-stack guidelines; `data/catalog-summary.json` - counts and verification date
- `LICENSE` - MIT, Next Level Builder
