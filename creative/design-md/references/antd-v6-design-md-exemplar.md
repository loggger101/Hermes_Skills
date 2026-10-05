---
description: "Ant Design v6 as a real DESIGN.md exemplar and its theming API (ConfigProvider token/algorithm/components/cssVar), plus what its AGENTS.md teaches about agent-facing repo rules"
source_repo: ant-design/ant-design (MIT)
tested_version: DESIGN.md, AGENTS.md and README read via GitHub API @ master; npm view antd = 6.6.5 (peer react >=18); no antd app built or run here
verified_date: "2026-10-05"
---

# Ant Design v6: a worked DESIGN.md and the theming API behind it

Ant Design ships a `DESIGN.md` (Google's spec: YAML tokens plus prose) at its repo root. It is one of
the few published examples from a mature design system, so it shows what a *good* one carries beyond
a palette. Use it as a model when authoring a DESIGN.md, and as the briefing document when building
with `antd`.

## What the exemplar does well (copy these)

1. **Values stated once, then used as tie-breakers.** Four named values (Natural, Certain, Meaningful,
   Growing) with a rule: when two approaches conflict, the one yielding a more certain, legible state wins.
2. **A "why" for every number.** Base font 14px not 16 (information density in a 1440px console); a 4px
   spacing grid with six steps; 6px control radius vs 8px surfaces vs 4px tags; two font weights only (400, 600).
3. **Roles over hex.** "Never hard-code `#FFF` or `#FAFAFA`; read the token." The three-layer surface model
   (`bg-layout` page, `bg-container` content, `bg-elevated` floating) is what lets a dark algorithm flip
   surfaces without breaking layouts.
4. **Neutrals as translucent black.** Text and overlays are `rgba(0,0,0,a)` so they blend with tinted
   cards instead of breaking the tint with opaque grey.
5. **Component archetypes with states and a limit.** "Single dominant primary button per screen",
   "tags are never for critical state", "tabs have no background fill in any state", table rows hover-only
   (no default zebra).
6. **Do / Don't pairs that forbid the common AI move**: no second `primary` button, no invented accent
   colour outside the preset palette, no custom `cubic-bezier` (use the named easings), no magic pixel values.
7. **An honest accessibility note.** White text on the default `#1677FF` and primary text on pale selected
   backgrounds fall below WCAG AA 4.5:1 for small text; the file says so and tells you to darken
   `colorPrimary` for strict targets. A DESIGN.md that records its own known failures is more usable than one that claims compliance.

## Token values worth knowing

| Token | Value |
|---|---|
| `colorPrimary` / semantic seeds | `#1677FF` primary, `#52C41A` success, `#FAAD14` warning, `#FF4D4F` error |
| Control height | 32px (button, input, select all match) |
| Radius | 6px controls, 8px cards/modals, 4px tags/tooltips, 9999 only for avatar/badge/dot |
| Motion | `motionDurationFast` 0.1s (hover/focus), `Mid` 0.2s (collapse/fade), `Slow` 0.3s (modal/drawer) |
| Modal | 20px vertical / 24px horizontal body padding, mask `rgba(0,0,0,0.45)` |
| Tooltip | `rgba(0,0,0,0.85)` background, white text |
| Selected menu item | `#E6F4FF` background, primary text |

Preset colours (`blue`..`lime`) are for tags, charts and categorical data, never for primary UI affordances.

## Theming API (v6, React >= 18)

Theming is broader than swapping tokens. The entry point is `ConfigProvider`'s `theme` prop:

| Lever | Use |
|---|---|
| `theme.token` | override seeds (`colorPrimary`, `colorSuccess`, `colorBgBase`, `colorTextBase`, `borderRadius`, `fontFamily`, `fontSize`); gradients derive automatically through `@ant-design/colors` |
| `theme.algorithm` | `defaultAlgorithm`, `darkAlgorithm`, `compactAlgorithm`, alone or as an array. **Do not invert colours by hand**; the algorithms handle the non-linear palette, shadow and size relations |
| `theme.components.Button` | per-component token override without touching others |
| nested `ConfigProvider` | a local theme that inherits unchanged tokens from its parent |
| `theme.useToken()` | resolved tokens inside React; `theme.getDesignToken()` outside React |
| `theme.cssVar` | emit CSS variables when plain CSS needs the tokens |
| `theme.zeroRuntime` | disable runtime style generation when you ship prebuilt/extracted CSS |

Gotchas from the doc: static APIs (`message.xxx`, `Modal.xxx`, `notification.xxx`) do not automatically pick up
the surrounding context; when themed static feedback is needed, use the hook-based APIs, the `App` component, or explicit context holders.
For a custom theme, change the smallest seed set that does the job (usually primary, status colours,
`borderRadius`, `fontFamily`, `fontSize`, neutral bases) and keep antd's interaction structure, density
and state feedback intact.

Component root styling has a documented precedence, lowest to highest: ConfigProvider `styles.root`, then
ConfigProvider `style`, then the component's own `styles.root`, then its own `style`. Components expose
semantic-slot props (`classNames` / `styles`) rather than asking you to override generated class names.

## What its AGENTS.md teaches about writing repo rules for agents

The file (project layout, import rules, doc/API table format, PR template, changelog format) is itself a good template.
Patterns worth reusing in any repo's agent file:

- **Scope each rule to a path glob and say what the exception is.** Demo files import by absolute path; test files import by relative path; `_semantic*.tsx` demos are the named exception.
- **Say when a section does NOT apply.** The changelog section applies only when preparing a release; "do not raise a finding just because CHANGELOG was not touched." That prevents the reviewer-agent false positive.
- **Fixed-format artefacts get a literal template** (the API table columns, the one-emoji-per-entry changelog line, the PR title form `type: summary`).
- **Close with behavioural guardrails**: state assumptions and ask rather than guess; minimum code that solves the problem; touch only what the request requires and clean up only your own orphans; turn tasks into verifiable goals ("fix a bug" becomes "write a failing test, make it pass").

## Rule for custom themes

If a look cannot be expressed through tokens, algorithms, `theme.components`, CSS variables or extracted static
styles, antd's own guidance is to treat it as a design-system extension, not a one-off page style. Brand pages may look
distinct, but forms, tables, navigation, overlays, focus states and validation feedback should still read as the same system.
When a contrast finding appears for a seed colour (the exemplar admits `#1677FF` with white small text is under 4.5:1), decide
deliberately (darken the seed, or record the exception in the file) rather than silencing it.
