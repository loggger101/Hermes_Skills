---
description: "impeccable 4.1.0: a deterministic anti-slop detector CLI for UI (npx impeccable detect) run live on planted-slop and clean HTML, plus its PRODUCT.md-first workflow and 24 commands"
source_repo: pbakaus/impeccable (Apache-2.0)
tested_version: npm impeccable 4.1.0 (Windows x64 binary, 15 MB node_modules) run on two small HTML files; rule ids partly read from crates/core/src/checks/rules.rs; the 24 slash commands and live-browser mode were not run
verified_date: "2026-10-05"
---

# impeccable: design guidance plus a deterministic detector

Impeccable (from Paul Bakaus; started from Anthropic's `frontend-design` skill) ships **one skill with 24 commands** and a **detector of 61 deterministic rules** that runs with no LLM and no API key.
Repository layout includes harness folders for many agents (including `.hermes`, `.claude`, `.cursor`, `.codex`, `.gemini`). Install into a project: `npx impeccable install`, then `/impeccable init` in the agent.

## The workflow idea worth copying

`/impeccable init` records **durable product truth** in `PRODUCT.md` (audience, purpose, operating context, constraints, voice, evidence) and keeps it separate from surface-level visual choices; visual direction is chosen per surface later and an existing visual system is recorded in `DESIGN.md`
(see `design-md`). Commands then act on a named target: `craft` (shape then build with visual iteration), `shape` (plan UX before code), `critique` (hierarchy, clarity), `audit` (a11y, performance, responsive),
`polish`, `distill`, `harden` (errors, i18n, overflow, edge cases), `animate`, `typeset`, `layout`, `colorize`, `clarify`, `adapt`, `optimize`, `bolder`/`quieter`, `onboard`, `delight`, `overdrive`, `extract`, `document`, plus `live`/`generate` for variant iteration in a browser.
The common failure it targets: every model reproduces the same SaaS tells (Inter everywhere, purple-to-blue gradients, nested cards, grey text on colour, buzzword copy).

## The detector (run live)

```bash
npm i -D impeccable && npx impeccable detect index.html src/        # files, directories or URLs
npx impeccable detect --json page.html        # JSON on stdout: antipattern, name, description, severity, category, file, line, snippet
npx impeccable detect --scope type,layout dist/    # restrict to design domains
npx impeccable detect --viewport 390x844 https://localhost:3000    # URL scan at mobile width
```

Human-readable findings go to **stderr** (stdout is kept free for `--json`). Exit codes: **0** no primary findings, **1** a target could not be scanned, **2** primary findings were reported (operational failure takes precedence on a partial multi-target scan).
Some rules are **advisory** (listed separately, never counted, never change the exit code; `--no-advisory` hides them).

Waivers travel with the file: `<!-- impeccable-disable overused-font -- exported brand doc -->`, `/* impeccable-disable-line overused-font */`, `// impeccable-disable-next-line bounce-easing: intentional bounce`
(`impeccable-disable` is file-wide, `-line`/`-next-line` scoped; list ids comma-separated or omit for all). Project config in `.impeccable/config.json` (`detector.ignoreRules`, `ignoreFiles`, `ignoreValues`, `designSystem.enabled`); `--no-config` ignores it.

**Planted-defect test.** A page with Inter, a purple-blue gradient, a gradient-clipped heading, white text on `#667eea`, grey `#9ca3af` text on `#3b82f6`, nested glass cards, `transition: all`, a coloured left border and the headline "Supercharge your workflow" produced `8 anti-patterns found`, exit 2:

| Rule id | Fired on |
|---|---|
| `gradient-text` (twice) | `background-clip: text` over a gradient |
| `low-contrast` (twice) | `#ffffff` on `#667eea` = 3.7:1; `#9ca3af` on `#3b82f6` = 1.4:1 (need 4.5:1) |
| `gray-on-color` | grey text on a blue background |
| `overused-font` | primary font Inter (also lists Roboto, Fraunces, Geist, Plus Jakarta Sans, Space Grotesk) |
| `ai-color-palette` | purple/violet accents |
| `marketing-buzzword` | "Supercharge your workflow" |

**Not flagged in that sample** even though the rule list suggests related checks: `transition: all`, nested cards, the glass `backdrop-filter`, the left accent border (the source defines `side-tab`, `border-accent-on-rounded`, `layout-transition`, `dark-glow`, `box-shadow` style rules, so these may need a computed-style scan of a URL or different markup). Do not read a short finding list as a clean bill.

A deliberately plain serif page (cream background `#faf7f2`, one heading, accessible link and image) produced 1 finding, `cream-palette` ("a warm cream or beige page background has become the default 'tasteful' AI surface"): the detector has opinions, so treat findings as prompts to justify a choice, and waive with a reason where the choice is deliberate.

Other rule ids present in `rules.rs`: `accent-bold`, `bounce-easing`, `dash-prefix`, `flat-type-hierarchy`, `hero-eyebrow-chip`, `icon-tile-stack`, `italic-serif-display`, `kicker-above-heading`, `tracked-caps`, `text-shadow` and several spacing-property rules.

## How it fits with the other design skills

Same family as the auteur gates (`awwwards-gsap-motion/references/acceptance-gates.md`: slopscan, motionqa) and the taste rules in this skill. Use the detector as a CI step on built HTML and as a fast pre-review for generated pages, then look at the rendered result: a linter cannot judge hierarchy or composition.
Both detect *tells*, so passing them proves absence of the cliches, not presence of good design.
