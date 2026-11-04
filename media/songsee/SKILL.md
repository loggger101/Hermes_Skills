---
name: songsee
description: "Spectrograms from audio with ffmpeg showspectrumpic"
version: 2.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Audio, Spectrogram, FFmpeg, Signal-Processing, Visualization]
    related_skills: [youtube-content, comfyui]
---

# Audio spectrograms (there is no `songsee` package)

## What This Skill Does

Produces spectrogram images from local audio or a URL using **ffmpeg's built-in
`showspectrumpic` filter**, and states plainly what the previous version of this skill got wrong.

**Corrected 2026-11-05.** Version 1.0.0 documented a CLI called `songsee` — subcommands, flags, a
defaults table, a verification checklist. **No such distribution exists on PyPI**:
`https://pypi.org/pypi/songsee/json` returns HTTP 404 (checked 2026-11-05), so every install line in
v1 (`uv pip install songsee`, `pip install songsee`) failed by construction and the documented flags
were never observed running. Nothing below is carried over from v1; what follows was run on this
machine today.

## When to Use

- Render a spectrogram of a recording to inspect it visually.
- Check bandwidth, hum, clipping or silence in a file before processing it.
- Make a time-frequency figure without Python.

For **numeric** features (MFCC arrays, chroma vectors) you need `librosa`, not ffmpeg — see the last
section; that route is *not* measured on this box and is labelled accordingly.

## Prerequisites

ffmpeg only. Measured here: `ffmpeg 8.1.1-full_build` (Winget Gyan build), filter present:

```bash
ffmpeg -hide_banner -filters | grep showspectrumpic
# .S showspectrumpic   A->V   Convert input audio to a spectrum video output single picture.
```

## Procedure

### 1. Single-picture spectrogram

Measured command (synthetic 440 Hz, 2 s):

```bash
ffmpeg -hide_banner -loglevel error \
  -f lavfi -i "sine=frequency=440:duration=2" \
  -lavfi "showspectrumpic=s=1024x512:legend=1" -y spec.png
```

Result on this box: **PNG, 69,080 bytes**.

### 2. Verify the artifact instead of trusting exit code 0

ffmpeg can exit 0 having written nothing useful, so probe the output:

```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,codec_name -of default=nw=1 spec.png
# codec_name=png / width=1306 / height=640
```

**Measured gotcha:** the image is **larger than the requested `s=` size**. Asking for `1024x512`
with `legend=1` produced **1306×640**, because the legend adds axis margins outside the plot area. If
a layout needs an exact geometry, request a smaller plot or re-scale afterwards — do not read `s=` as
the output size.

### 3. Filtered / log-scale variants

Measured: chaining audio filters ahead of the picture filter works —

```bash
ffmpeg -hide_banner -loglevel error -f lavfi -i "sine=frequency=880:duration=1" \
  -af "highpass=f=200" -lavfi "showspectrumpic=s=512x256:scale=log" -y spec2.png
# -> PNG, 60,780 bytes
```

Useful knobs (`ffmpeg -h filter=showspectrumpic` for the live list): `scale=` (`lin`, `log`, `sqrt`),
`legend=1`, `axes=1`, `saturation=`, plus `-af highpass/lowpass` in front to zoom into a band.

### 4. Real files, including from a URL

Same shape: replace the `lavfi` input with `-i input.mp3` or an http(s) audio URL. For video
containers ffmpeg takes the first audio stream; add `-vn` to be explicit and `-ac 1` for mono.

## Numeric features (`librosa`) — documented, NOT measured here

For arrays rather than pictures, `librosa` is the usual tool (e.g. `librosa.feature.mfcc(...)`). Its
PyPI distribution exists, but **no install or run was performed on this machine**, so wheel
availability for this interpreter (standalone CPython 3.14 — see
`software-development/python-toolchain-notes/references/cpython-runtime-facts-windows.md`) stays an
open question here rather than a claim. Verify before promising it: `uv venv`, install, then run one
real call on one real file. Same rule as
`data-science/gis-spatial-analysis/references/geospatial-stack-freshness.md`: install success proves
nothing until a tool actually runs.

## Pitfalls

- **Do not search for or install `songsee`.** It is not a package; v1 of this skill invented it.
- **Silence looks like failure:** a silent input yields an empty-looking spectrogram, which is correct output. Check amplitude first: `ffmpeg -i in.mp3 -af volumedetect -f null -`.
- **`s=` is the plot area, not the file geometry** (measured legend gotcha above).
- **Log scale hides low-level content**; state the scale in any figure caption.
- **Long files are memory-hungry**; render a window with `-ss`/`-t` instead of whole albums.

## Verification

- [ ] `ffprobe` reports a PNG with non-zero width and height (a byte count alone is not enough).
- [ ] Energy appears where expected: a 440 Hz tone must show as one low band.
- [ ] Scale, legend and any `-af` filters used are recorded next to the figure.

## Related Skills

- `media/youtube-content` — get audio or transcripts from a link before analysing it.
- `creative/comfyui` — turn a spectrogram into stylised imagery.
