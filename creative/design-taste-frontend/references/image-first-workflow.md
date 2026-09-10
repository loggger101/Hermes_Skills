---
description: "Image-first web design-to-code workflow distilled from taste-skill's imagegen/image-to-code/brandkit skills - generate, analyze, implement; per-section frames; consistency rules"
source_repos: Leonxlnx/taste-skill skills/{image-to-code-skill,imagegen-frontend-web,imagegen-frontend-mobile,brandkit} (MIT), clone @ ccbc156 mined 2026-09-10 - pattern distilled from the four ~4.5k-line image-direction skills
verified_date: "2026-09-10"
---

# Image-First Design-to-Code Workflow (distilled)

The four large taste-skill image skills (~4,500 lines of art direction between them) share one workflow and a set of hard-won rules. This reference captures the transferable pattern; load `design-taste-frontend` for code-phase execution.

## The mandatory order: generate → analyze → implement

For visually important web tasks (hero sections, landing pages, marketing sites, editorial brand pages, premium multi-section websites, redesigns where visual quality matters):

1. **Generate the design image(s) first** — if any image generation is available, do not skip it and do not start with freeform coding. The generated images are the primary visual source of truth.
2. **Deeply analyze them second** — extract layout structure, type scale, spacing rhythm, color roles, component shapes *from the actual pixels* before writing code ("clean analysis standard": name what you see, don't re-invent it).
3. **Implement third**, matching the reference as closely as is reasonable; where fidelity and practicality conflict (e.g., a photo that can't be reproduced in CSS), keep the composition and swap the asset.

Why this works: freeform coding collapses into repetitive defaults (one giant compressed image for too many sections, centered dark hero clichés, card spam, repeated left-text/right-image layouts). An art-directed reference forces decisions to happen *before* code, where they're cheap to change.

## Per-section frames beat one giant board

The single most important rule across all four skills: **generate enough separate images — one per major section** (hero, features/bento, media/scroll-story, pricing/action, footer) instead of one compressed full-page board. The failure mode it prevents is text becoming too small to read and "nice-looking but unextractable" designs.

Supporting rules:
- **Large, readable, section-specific images over tiny compressed boards.** If a frame contains more than ~2 sections, split it.
- **Fresh standalone regeneration beats cropping old images** — for detail views or second passes, regenerate at the right aspect ratio instead of slicing an existing board (cropping destroys composition and resolution).
- **Don't crop to fit; regenerate to fit.** Same principle for mobile screens: generate each screen at its own 9:16 frame.

## Multi-image consistency contract

Because every section is its own image, consistency must be enforced explicitly across frames:

**Must stay identical:** brand world (palette + type scale logic), spacing discipline, CTA family (style variations OK, identity not), icon/illustration mood, image treatment (grade, framing, material vocabulary), tonal language of any copy.

**May vary per section:** composition anchor, background mode, section size and density, which "second-read" moment appears.

Litmus test: a viewer flipping through every frame must still recognize one brand. Anything that breaks brand recall is over-variation. (Brandkit adds the same contract at identity level: logo system + color system + typography + applications all in one coherent board.)

## Anti-slop lists for image direction

Banned **layout slop**: endless centered sections; identical card rows repeated section after section; cloned left-text/right-image blocks; perfect but lifeless symmetry; fake complexity without hierarchy.
Banned **visual slop**: default purple/blue AI gradients; too many glowing edges; floating spheres/blobs everywhere; glassmorphism stacked without reason; over-rendered noise that hides the layout.
Banned **typography slop**: giant heading + weak tiny subcopy; too many font moods in one page; lazy all-caps everywhere; gradient headline as a shortcut for "premium".
Banned **content slop** (fake brand names and AI copy clichés): Acme, Nexus, NovaCore-style nonsense wordmarks; "unleash / elevate / revolutionize / next-gen / seamless / powerful solution / transformative platform". Use short, believable, design-friendly copy.

## Mobile-specific rules worth keeping

- **Screen-first**: each screen is its own generated frame at 9:16 — never a desktop layout with phone borders drawn on top.
- **Generate enough screens** for the flow (onboarding sequence = one image per step; don't imply "and so on").
- **Safe-area discipline**: system regions (status bar, home indicator) respected in every frame; interactive targets ≥44px equivalent.
- **First-screen cleanliness**: the very first screen carries no navigation chrome clutter — it's the thumbnail of the product.

## Brandkit board anatomy (for identity work)

A premium brand-kit overview image is a grid presentation board, not a moodboard: dark charcoal outer canvas; strong gutters between panels; sparse typography; large negative space. Standard panel set: logo cover → logo construction (geometry/meaning made visible) → digital application (browser chrome / app header / terminal frame mockups) → brand essence → color system → typography. Logo concept methods worth reusing when art-directing marks: monogram+meaning, product action, metaphor fusion, negative space, construction geometry — each with the rationale stated in the board itself.

## Where this pattern does NOT apply

Dashboards, data tables, multi-step product UIs, code editors, and internal tools are out of scope for image-first treatment (same as `design-taste-frontend`): their quality is structural/functional, not art-directed, so a generated reference adds cost without signal. Use the direct code path there.
