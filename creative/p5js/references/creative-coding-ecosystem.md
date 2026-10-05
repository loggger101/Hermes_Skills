---
description: "Creative-coding libraries from awesome-creative-coding with npm versions (2026-10-05), the p5.js 1.x vs 2.x state, and what to reach for per task"
source_repo: terkelg/awesome-creative-coding (curated list); versions from npm and CDN endpoints, checked 2026-10-05
tested_version: npm registry queries and HTTP GETs of three CDN URLs; no library was executed
verified_date: "2026-10-05"
---

# Creative-coding ecosystem map

The awesome list covers books, courses, frameworks (Processing, py5, Cinder, openFrameworks, nannou, OPENRNDR, thi.ng, Lygia for shader functions, canvas-sketch), visual and sound programming languages, web libraries, projection mapping, math, ML/CV, and communities.
This note keeps the **web** libraries an agent can use in a single HTML file or a small Node project, with current versions.

## npm snapshot (2026-10-05)

| Library | Latest | Modified | Use |
|---|---|---|---|
| `p5` | **2.3.4** (`latest`); `r1` tag = 1.11.13; `beta` 2.3.1-rc.2 | 2026-09-25 | Processing-style sketches (`p5js` skill) |
| `three` | 0.186.1 | 2026-09-24 | general 3D |
| `@react-three/fiber` | 9.8.1 | 2026-10-02 | three.js in React |
| `pixi.js` | 8.22.0 | 2026-10-01 | fast 2D WebGL/WebGPU rendering |
| `@babylonjs/core` / `babylonjs` | 9.29.0 | 2026-10-01 | full 3D engine |
| `tone` | 15.1.22 | 2026-10-04 | Web Audio synthesis and music |
| `gsap` | 3.15.0 | 2026-04-13 | timelines, ScrollTrigger (`awwwards-gsap-motion`) |
| `lenis` | 1.3.26 | 2026-09-18 | smooth scroll |
| `ml5` | 1.4.0 | 2026-08-07 | friendly ML in the browser |
| `canvas-sketch` | 0.7.8 | 2026-05-26 | generative-art framework |
| `twgl.js` | 7.0.0 | 2025-07-16 | tiny WebGL helper |
| `ogl` | 1.0.11 | 2025-01-27 | minimal WebGL 3D |
| `regl` | 2.1.1 | 2024-11-12 | functional WebGL (quiet) |
| `paper` | 0.12.18 | 2024-07-17 | vector graphics scripting (quiet) |
| `matter-js` | 0.20.0 | 2024-06-23 | 2D physics (quiet) |
| `d3` | 7.9.0 | 2025-05-17 | data-driven SVG/canvas |

Entries from 2024-2025 are stable rather than dead (these libraries are small and finished); check issues before betting a new project on them.

## p5.js: 1.x vs 2.x (checked)

- npm `latest` is **2.3.4**; the 1.x line is tagged `r1` at **1.11.13**. The `p5js` skill defaults to 1.11.3 and documents 2.x differences (`async setup()` replacing `preload()`, new colour modes, shader `.modify()`); 1.11.3 is still on cdnjs.
- URLs that returned HTTP 200 on 2026-10-05: `https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.11.3/p5.min.js` (1,056,654 bytes), `https://cdn.jsdelivr.net/npm/p5@1.11.13/lib/p5.min.js` (1,063,246 bytes), `https://cdn.jsdelivr.net/npm/p5@2/lib/p5.min.js` (990,638 bytes).
- Pin an exact version in generated sketches (`p5@1.11.13` or `p5@2.3.4`), not a floating `@2`, so a sketch does not change under you; do not mix a 1.x `p5.sound` addon with 2.x core.

## Choosing

| Task | Pick |
|---|---|
| Quick generative sketch, teaching, single HTML file | p5.js |
| 3D scene or shader piece | three.js (or OGL for minimal) |
| Thousands of 2D sprites/particles | Pixi.js |
| Print-ready generative art with export | canvas-sketch |
| Audio-reactive visuals | Tone.js or Web Audio + p5.sound |
| Video output from a sketch | `hyperframes-video` / `remotion-video` |
| Shader snippets across GLSL/HLSL/WGSL/MSL | Lygia (from the list) |
| Python route | py5 (Processing in Python) |
