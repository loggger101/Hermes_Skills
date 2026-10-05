---
name: remotion-video
description: "React compositions rendered to deterministic MP4."
version: 1.0.0
author: Hermes Agent (from remotion-dev/remotion best-practices skills; CLI run live)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [video, react, remotion, ffmpeg, motion-graphics, rendering, deterministic]
    related_skills: [hyperframes-video, manim-video, react-ecosystem, awwwards-gsap-motion]
---

<!-- source: remotion-dev/remotion (packages/codex-plugin/skills/remotion-best-practices, LICENSE.md) read 2026-10-05; remotion 4.0.532 installed and a 30-frame composition rendered twice. Remotion itself is under its own LICENSE.md, NOT MIT: see License. -->

# Remotion: React to video

## What This Skill Does

Remotion renders video from React components: each frame is a pure function of `useCurrentFrame()`, rendered in headless Chrome and encoded with FFmpeg. Use it when the video is part of a React/TypeScript codebase, needs data-driven scenes, or is embedded with the `<Player>` or rendered on Lambda/Vercel/Cloudflare in a SaaS.
For plain HTML + GSAP compositions use `hyperframes-video`; for math animations `manim-video`.

## When to Use

- Programmatic, data-driven, or templated video (product tours, reports, changelog videos, social clips) in a Node/React project
- Interactive preview in Remotion Studio with edits that write back to code
- Not for non-React stacks (use `hyperframes-video`), or commercial work for a company over the free-licence size without a company licence (see License)

## License (read before commercial use)

Remotion is **source-available under its own `LICENSE.md`**, not an OSI licence. Free licence eligibility (per the file): an individual; a for-profit organisation with **up to 3 employees**; a **non-profit or not-for-profit** organisation; or someone evaluating it and not yet using it commercially.
Allowed: use commercially or not to create videos and images, and modify it for your own use. Disallowed: copying or modifying Remotion to sell, rent, license, relicense or sublicense your own derivative. Larger for-profit organisations need a company licence. The file also says the licence changes slightly in Remotion 5.0.
Check the current `LICENSE.md` and the organisation's status before shipping a product.

## Setup and the verified render

```bash
npx create-video@latest --yes --blank --no-tailwind my-video && cd my-video && npm i   # official scaffold
npx remotion studio            # preview (--no-open to print the URL only); open it BEFORE building the composition
npx remotion render src/index.tsx Main out/video.mp4
npx remotion still src/index.tsx Main out/frame.png --frame=29
```

Verified (Windows, Node 22, remotion/@remotion/cli **4.0.532**, react 19; 260 MB `node_modules`) with a hand-made project (a `registerRoot` file, one `Composition` of 30 frames, 30 fps, 640x360 with a `Easing.bezier` opacity fade):

- `remotion render ... --browser-executable="C:/Program Files/Google/Chrome/Application/chrome.exe"` rendered with the **system Chrome**, avoiding the headless-shell download: 15 s wall clock for 30 frames, a 31 KB H.264 file; `ffprobe`: 640x360, 30/1 fps, 30 frames, 1.000 s.
- **Two renders were byte-identical** (same SHA-256 prefix) and all 30 decoded-frame hashes (`ffmpeg -f framemd5`) matched. Identical output was shown on one machine only.
- `remotion still ... --frame=29` wrote a 19 KB PNG.
- Not run: Studio, Lambda, `<Player>`, captions, audio.

## Rules from the official best-practices skill

- Drive all animation from `useCurrentFrame()` and `interpolate()`; use `Easing.bezier()` / `Easing.spring()`. **CSS `transition`/`animation` and Tailwind animation classes will not render correctly** and must be rewritten as frame-driven values.
- Keep `interpolate()` **inline** in the `style` prop (so Studio can edit keyframes), and prefer the CSS `scale`, `translate`, `rotate` properties over a `transform` string; for `scale`, use `output: 'perceptual-scale'`. Always clamp: `extrapolateLeft: 'clamp', extrapolateRight: 'clamp'`.
- Assets go in `public/` and are referenced with `staticFile()`; media via `<Video>`/`<Audio>` from `@remotion/media`, images via `<CanvasImage>`, animated GIF/WebP/AVIF via `<AnimatedImage>` (`@remotion/gif` outside Chrome); remote URLs may be passed directly.
- Wrap scenes in `<AbsoluteFill>`; for multi-scene videos use sequences and the official multi-scene guidance; size text for video (large), not web.
- Do not overwrite edits the user made in the Studio or the code between turns; if something changed unexpectedly, assume it was intentional or ask.
- Use `<Interactive.*>` named elements so Studio edits write back to code.

## Remotion vs HyperFrames

| | Remotion | HyperFrames (`hyperframes-video`) |
|---|---|---|
| Authoring | React/TypeScript components | HTML + `data-*` attributes + paused GSAP timeline |
| Animation model | pure function of the frame number | seekable runtime (GSAP, Lottie, CSS, WAAPI adapters) |
| Best for | React apps, data-driven video, SaaS, Player embedding | agent-written HTML, no build step, quick compositions |
| Licence | Remotion LICENSE.md (free tier by org type/size) | Apache-2.0 |
| Verified here | 30-frame render, byte-identical twice | 48-frame render, byte-identical twice; lint caught planted defects |

HyperFrames also ships a `remotion-to-hyperframes` porting workflow for moving an existing composition.

## Pitfalls

- A transition that looks fine in the Studio preview but is CSS-driven renders as a static frame; grep compositions for `transition`/`@keyframes`/`animate-`.
- Default render downloads a Chrome Headless Shell on first use; pass `--browser-executable` to reuse an installed Chrome, and pin it in CI.
- Version-match `remotion` and every `@remotion/*` package exactly (they are released in lockstep).
- Frame-pure means no `Math.random()`, `Date.now()` or fetch-at-render inside components unless delayed through Remotion's data-fetch helpers; seeded values only.

## Verification

Studio preview loads, `remotion render` completes, `ffprobe` shows the intended duration/fps/size, and two renders hash identically (CI).

## References

- Docs and APIs: https://www.remotion.dev/docs (the official skills load current docs on demand)
- Official skills live in the repo at `packages/codex-plugin/skills/remotion-best-practices` (create, markup, maps, multimedia, interactivity, render, studio, captions, saas, docs, upgrade)
