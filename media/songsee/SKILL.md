---
name: songsee
description: "Spectrogram / audio feature images via the songsee Go tool or ffmpeg showspectrumpic."
version: 2.1.0
author: "Hermes Agent (upstream: openclaw/songsee by steipete)"
license: MIT
platforms: [linux, macos, windows]
homepage: https://github.com/openclaw/songsee
metadata:
  hermes:
    tags: [Audio, Spectrogram, FFmpeg, MFCC, Chroma, Mel, Signal-Processing, Visualization]
    related_skills: [youtube-content, comfyui]
---

# Songsee — audio feature images (Go tool) + measured ffmpeg fallback

Generates spectrograms and multi-panel audio feature images from local audio. Two working routes: the **`songsee` Go binary** (Peter Steinberger's project, now under openclaw; README verified against upstream 2026-11-08) or stock **ffmpeg `showspectrumpic`** (measured end-to-end on this Windows box).

Honest correction history: v1 of this skill fabricated a Python CLI (`pip install songsee`, invented subcommands like `mel-spectrogram`) — PyPI/npm have no `songsee`; both registries return 404 (re-verified 2026-11-08). A repo-side correction pass then over-corrected, declaring the tool itself nonexistent. It is real: https://github.com/openclaw/songsee returns HTTP 200 with a full README; it simply ships no Python distribution and (so far) no Windows binaries.

## When to Use

"Generate a spectrogram from this file", "show me chroma/MFCC panels of this track", "slice 8s around the chorus and visualize it", or when an audio pipeline needs visual inspection (clipping, spectral gaps, synthesis debugging). Output images can be read back with `vision_analyze`. For **numeric** features (MFCC arrays, chroma vectors) you need `librosa`, not either tool — see the last section.

## Install routes for songsee (verified against upstream README 2026-11-08)

- macOS: `brew install steipete/tap/songsee`
- Anywhere with Go: `go install github.com/steipete/songsee/cmd/songsee@latest` (README still shows the pre-move module path)
- Docker: build from the repo — image bundles ffmpeg, so batch/server runs don't depend on host audio tooling.
- **Windows reality check:** releases API for v0.1.3/v0.1.2/v0.1.1 shows zero assets (re-checked 2026-11-08) — no prebuilt Windows binaries; this box also has no Go toolchain, so the ffmpeg route below is the working path here.

## songsee usage (flags cross-read from upstream README 2026-11-08)

```bash
# Default: 1920x1080 JPEG next to the input file
songsee track.mp3

# Mel spectrogram, magma palette, custom size
songsee track.mp3 --viz mel --style magma --width 2048 --height 1024

# All nine modes as one grid image
songsee track.mp3 --viz spectrogram,mel,chroma,hpss,selfsim,loudness,tempogram,mfcc,flux

# Time slice: start at 12.5s for 8 seconds
songsee track.mp3 --start 12.5 --duration 8 -o slice.jpg
```

| Flag | Meaning | Default |
|------|---------|---------|
| `--viz` | comma list (repeatable): spectrogram, mel, chroma, hpss, selfsim, loudness, tempogram, mfcc, flux — grid-rendered together | spectrogram |
| `--style` | palette: classic, magma, inferno, viridis, gray, claw | classic |
| `--width` / `--height` | output px | 1920 × 1080 |
| `--format` | jpg or png | jpg |
| `-o` / `--output` | output path | input name + ext |
| `--window` / `--hop` | FFT window / hop | 2048 / 512 |
| `--min-freq` / `--max-freq` | frequency range filter (Hz) | full band |
| `--start` / `--duration` | time slice in seconds | whole file |

WAV and MP3 decode natively; everything else falls back to ffmpeg at runtime — keep ffmpeg installed for other containers. Stdin/stdout piping is **not** documented upstream; don't assume it.

## Measured ffmpeg route (works everywhere songsee can't be installed)

Measured on this box: `ffmpeg 8.1.1-full_build` (Winget Gyan build), filter present:

```bash
ffmpeg -hide_banner -filters | grep showspectrumpic
# .S showspectrumpic   A->V   Convert input audio to a spectrum video output single picture.
```

### 1. Single-picture spectrogram (synthetic test signal)

```bash
ffmpeg -hide_banner -loglevel error \
  -f lavfi -i "sine=frequency=440:duration=2" \
  -lavfi "showspectrumpic=s=1024x512:legend=1" -y spec.png
```

Result on this box: **PNG, 69,080 bytes**. A waveform image in the same style: `-filter_complex "showwavespic=s=960x240"` (verified here too).

### 2. Verify the artifact instead of trusting exit code 0

ffmpeg can exit 0 having written nothing useful, so probe the output:

```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,codec_name -of default=nw=1 spec.png
# codec_name=png / width=1306 / height=640
```

**Measured gotcha:** the image is **larger than the requested `s=` size**. Asking for `1024x512` with `legend=1` produced **1306×640**, because the legend adds axis margins outside the plot area. If a layout needs exact geometry, request a smaller plot or re-scale afterwards — do not read `s=` as the output size.

### 3. Filtered / log-scale variants (measured)

```bash
ffmpeg -hide_banner -loglevel error -f lavfi -i "sine=frequency=880:duration=1" \
  -af "highpass=f=200" -lavfi "showspectrumpic=s=512x256:scale=log" -y spec2.png
# -> PNG, 60,780 bytes
```

Useful knobs (`ffmpeg -h filter=showspectrumpic` for the live list): `scale=` (lin/log/sqrt), `legend=1`, `axes=1`, `saturation=`, plus `-af highpass/lowpass` in front to zoom into a band; `mode=separate` gives per-channel panels.

### 4. Real files, including from a URL

Same shape: replace the `lavfi` input with `-i input.mp3` or an http(s) audio URL. For video containers ffmpeg takes the first audio stream; add `-vn` to be explicit and `-ac 1` for mono.

## Numeric features (`librosa`) — documented, NOT measured here

For arrays rather than pictures, `librosa` is the usual tool (e.g. `librosa.feature.mfcc(...)`). Its PyPI distribution exists, but **no install or run was performed on this machine**, so wheel availability for standalone CPython 3.14 on Windows stays an open question here rather than a claim. Verify before promising it: `uv venv`, install, then run one real call on one real file — install success proves nothing until the tool actually runs.

## Pitfalls

- **`songsee` is not on PyPI/npm** (both 404) — install only via brew/Go/Docker; don't claim songsee "isn't working" when it was never installable by the attempted route.
- **No prebuilt Windows binaries in any release so far** (v0.1.3 assets = 0, re-checked 2026-11-08) — use the ffmpeg route on this box.
- **Only WAV/MP3 decode natively** in songsee; other containers need ffmpeg present at runtime.
- Multi-panel grids get unreadable at small sizes: raise `--width/--height` when combining many `--viz` modes.
- **Silence looks like failure:** a silent input yields an empty-looking spectrogram, which is correct output. Check amplitude first: `ffmpeg -i in.mp3 -af volumedetect -f null -`.
- **`s=` is the plot area, not the file geometry** (measured legend gotcha above).
- **Log scale hides low-level content**; state the scale in any figure caption.
- **Long files are memory-hungry**; render a window with `-ss`/`-t` instead of whole albums.

## Verification

- [ ] `songsee --help` runs (or ffmpeg route used knowingly)
- [ ] `ffprobe` reports a PNG/JPEG with non-zero width and height (a byte count alone is not enough)
- [ ] Energy appears where expected: a 440 Hz tone must show as one low band; axes/labels make sense (`vision_analyze`)
- [ ] Time slice actually starts where expected (check audible content vs image); scale/legend/filters recorded next to the figure

## Related Skills

- `media/youtube-content` — get audio/transcripts from a link before analysing it
- `creative/comfyui`, `creative/p5js` — stylized or AI-generated visual follow-ups
