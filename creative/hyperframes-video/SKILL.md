---
name: hyperframes-video
description: "HTML + GSAP compositions rendered to deterministic MP4."
version: 1.0.0
author: Hermes Agent (ported from heygen-com/hyperframes, Apache-2.0; CLI run live)
license: Apache-2.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [video, html, gsap, ffmpeg, motion-graphics, rendering, deterministic]
    related_skills: [manim-video, ascii-video, awwwards-gsap-motion, p5js, architecture-diagram, remotion-video]
---

<!-- source: heygen-com/hyperframes README + skills/hyperframes-core (Apache-2.0); `hyperframes` 0.8.127 installed and run 2026-10-05 on Windows (Node 22.23, FFmpeg 9.0, system Chrome) -->

# HyperFrames: write HTML, render video

## What This Skill Does

HyperFrames turns an HTML file into an MP4 (also WebM, MOV with alpha, GIF, PNG sequence, HLS). A *composition* is HTML whose DOM declares timing with
`data-*` attributes, whose animation is a **paused, seekable GSAP timeline**, and whose media playback the framework owns. The renderer seeks
frame by frame in headless Chrome and encodes with FFmpeg, so output is deterministic. Good for product intros, explainers, motion graphics, captions,
beat-synced clips and slide decks, authored by an agent as ordinary HTML/CSS/JS.

## When to Use

- A short designed video (title cards, kinetic type, stat/chart hits, lower thirds, PR-to-changelog explainers) where you want to edit text and styling in a file and re-render
- Video built from web content, with reproducible output (CI, versioned compositions)
- Not for: math animations (`manim-video`), terminal/ASCII video (`ascii-video`), generative sketches (`p5js`), live-action editing beyond overlays and captions

## Requirements (checked)

Node >= 22, FFmpeg, and Chrome (system Chrome was found and used; `hyperframes browser ensure` downloads one otherwise). `npx hyperframes doctor` reports each
(whisper-cpp, Kokoro TTS and MusicGen are optional extras for transcription, voice and music). Install per project (`npm i hyperframes`, 119 MB with deps) or run via `npx`.

**Telemetry is on by default** ("anonymous usage data"; a signed-in HeyGen account links usage to it). Run `hyperframes telemetry disable` first.
`init` also checks AI skills against GitHub; `HYPERFRAMES_SKIP_SKILLS=1` skips it.

## Workflow

```bash
npx hyperframes init demo --example blank --non-interactive --resolution 1080p-square   # scaffold: index.html, hyperframes.json, AGENTS.md, CLAUDE.md
cd demo
npx hyperframes lint                  # fast static rules
npx hyperframes check                 # lint + runtime validation + layout/contrast inspection in one gate
npx hyperframes snapshot --at 1,2     # PNG frames to look at
npx hyperframes preview               # Studio in the browser
npx hyperframes render -q draft -f 24 -o renders/t.mp4      # quality: draft | looks (default, CRF 16) | delivery
```

Other useful commands: `timeline` (tracks and clips), `compositions`, `info`, `beats` (beat detection for music), `keyframes`, `compare`, `normalize-audio`,
`render --format webm|mov|gif|png-sequence|hls`, `--workers N`, `--gpu`, `--docker` (deterministic container render), `--strict` (fail on lint errors).
Render only after the user approves the preview.

## The composition contract (the rules that matter)

```html
<div id="root" data-composition-id="main" data-start="0" data-duration="2" data-width="1080" data-height="1080">
  <h1 id="title" class="clip" data-start="0" data-duration="2" data-track-index="0">Title</h1>
</div>
<script>
  const tl = gsap.timeline({ paused: true });
  tl.fromTo("#title", { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.6 }, 0);
  window.__timelines["main"] = tl;     // key MUST equal the root data-composition-id
</script>
```

- Timed elements carry `class="clip"` plus `data-start` / `data-duration` (seconds); the root `data-duration` sets total length, and a clip ending past it is cut off.
- Exactly **one paused timeline per composition**, registered at `window.__timelines["<id>"]` only after it is fully built.
- Canvas size is `data-width`/`data-height`; the root styles `width/height: 100%`, never hard-coded pixel sizes. A **standalone** root sits directly in `<body>` with no `<template>`; a **sub-composition** (`data-composition-src`) is wrapped in `<template>`, with its `<style>/<script>` inside the template.
- Determinism: no render-time clocks, unseeded `Math.random`, network calls or input state; `repeat: -1` only under a finite root duration.
- The framework owns clip visibility: never tween `display`, `visibility` or `autoAlpha` on a `.clip`; animate a child. Do not set an initial CSS `transform` on a node that GSAP also tweens (use `fromTo`).
- `<audio>`/`<video>` need an `id` (an id-less audio is silently dropped from the mix) and must not carry `crossorigin`; a `<video data-start>` must not sit inside another element that also has `data-start`.
- A named `font-family` needs an in-file `@font-face` to a shipped file. Keep ids unique across the assembled page. No `<br>` in body text.

## Verified here

- **Linter catches planted defects** (rule names as reported): an `<audio data-start>` with no id raised `media_missing_id` ("this audio will be SILENT"), a missing source file raised `audio_src_not_found`, and `tl.to("#title", {autoAlpha: 0})` on a `.clip` raised `gsap_animates_clip_element`; the run ended `3 error(s), 1 warning(s)`. The clean scaffold gave `0 errors, 0 warnings`. An inline `style="transform: ..."` plus an `x` tween was **not** flagged (the documented `gsap_css_transform_conflict` rule targets stylesheet transforms), so avoid both anyway.
- **Render**: the 2 s, 1080x1080, 24 fps draft rendered in 6.9 s wall (about 14 s including process start) to a 16 KB H.264 file; `ffprobe` confirmed 48 frames, 24/1 fps, 2.000 s. The log reported `drawelement capture`, `hardware gpu` and "static-dedup reused 30/78 frame(s)".
- **Determinism**: two separate renders of the same composition produced **byte-identical** MP4 files (same SHA-256) and 48 identical decoded-frame hashes (`ffmpeg -f framemd5`). One run logged `drawElement blank-frame suspect; re-capturing` for frame 12 and still came out identical. Identical output was shown on one machine; encoder or GPU differences across hosts can change bytes (use `--docker` for cross-host determinism).

## Pitfalls

- The scaffold loads GSAP from a CDN (`cdn.jsdelivr.net/.../gsap@3.14.2`), so a render needs network unless you vendor the script locally; pin it for reproducibility.
- A lint **error** switches off the layout and contrast audits; `check` then reports "0 samples" which looks clean but means nothing ran. Clear lint errors first.
- After `render`, read the summary's capture mode and GPU line; `screenshot` mode with software GPU is the slow path.
- Upstream also ships 21 task skills (product launch video, faceless explainer, PR-to-video, captions, music-to-video, slideshow, Remotion port) via `npx skills add heygen-com/hyperframes`; this skill covers the shared core contract and CLI, not those workflows.

## Verification

`npx hyperframes check` returns 0 findings, `snapshot` frames were viewed, the rendered file's `ffprobe` duration/frames/dimensions match the brief, and (for CI) two renders hash identically.
