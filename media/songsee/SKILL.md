---
name: songsee
description: "Audio spectrograms and feature extraction via CLI."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Audio, Spectrogram, Features, MFCC, Chroma, Mel, Signal-Processing]
    related_skills: [comfyui, youtube-content]
---

# Songsee — Audio Feature Extraction

## What This Skill Does

Generates audio spectrograms, chroma features, MFCCs, and other signal-processing visualizations from local audio files or YouTube URLs. Wraps the `librosa` library and `ffmpeg` into a CLI tool (`songsee`) that handles format conversion, parameter selection, and output rendering. Loads `skill_view(name='youtube-content')` for transcript extraction and `skill_view(name='comfyui')` for AI-generated visual art.

Audio spectrograms and feature extraction via CLI. Generates mel spectrograms, chroma features, MFCCs, and other audio analysis visualizations from audio files or YouTube links.

## When to Use

Use when the user wants to:
- "Generate a spectrogram from this audio file"
- "Extract MFCC features from this song"
- "Show me the chroma features of this track"
- "Analyze the frequency content of this recording"
- "Convert this YouTube link to a spectrogram"

## Prerequisites

```bash
# Install with uv (recommended)
uv pip install songsee

# Or with pip
pip install songsee
```

**Requirements:**
- `ffmpeg` installed (for audio format conversion)
- `numpy` and `scipy` (installed automatically)
- `matplotlib` for visualizations (install: `uv pip install matplotlib`)

## Process

### 1. Identify the audio source

The tool accepts:
- Local file path: `path/to/audio.mp3`
- YouTube URL: `https://youtube.com/watch?v=VIDEO_ID`
- Any URL: direct link to an audio file

### 2. Choose the feature type

| Feature | Description | Best For |
|---------|-------------|----------|
| **Mel spectrogram** | 2D time-frequency representation using mel-scale | General audio analysis, vocal detection |
| **Chroma** | 12-bin pitch class representation | Key detection, chord analysis, cover song ID |
| **MFCC** | 13 coefficients representing spectral envelope | Speech recognition, genre classification |
| **Spectral centroid** | "Brightness" of the spectrum over time | Timbral analysis, instrument identification |
| **Spectral rolloff** | Frequency below which 85% of energy lies | Texture analysis |
| **Zero crossing rate** | Rate of sign changes in the signal | Rhythm analysis, onset detection |

### 3. Run the extraction

```bash
# Mel spectrogram from local file
songsee mel-spectrogram audio.mp3 --output mel.png

# Chroma features from YouTube
songsee chroma "https://youtube.com/watch?v=VIDEO_ID" --output chroma.png

# MFCC with default settings
songsee mfcc audio.wav --output mfcc.png

# Spectral features (multiple at once)
songsee features audio.mp3 --output features.png
```

### 4. Analyze results

- Examine the visualization for patterns (repeating sections, key changes, timbral shifts)
- Check for artifacts (clipping, silence, noise bursts)
- Compare features across tracks for similarity analysis

### 5. Iterate if needed

Adjust parameters:
```bash
# Customize mel spectrogram
songsee mel-spectrogram audio.mp3 \
  --sr 22050 \
  --n-mels 128 \
  --n-fft 2048 \
  --hop-length 512 \
  --output custom_mel.png

# Save raw data as JSON
songsee mfcc audio.wav --save-data features.json --output mfcc.png
```

## Common Use Cases

### Vocal Analysis
```bash
# Extract vocal mel-spectrogram (isolate vocal range)
songsee mel-spectrogram audio.mp3 --min-freq 80 --max-freq 400 --output vocal_mel.png
```

### Rhythm Analysis
```bash
# Zero crossing rate for percussion detection
songsee zero-crossing-rate audio.mp3 --output zcr.png
```

### Genre Classification
```bash
# Full feature set for ML pipeline
songsee features audio.mp3 \
  --output-spec \
  --output-mfcc \
  --output-chroma \
  --save-data features.json
```

## Parameters Reference

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `--sr` | 22050 | 8000-48000 | Sample rate in Hz |
| `--n-mels` | 128 | 32-256 | Number of mel bands |
| `--n-mfcc` | 13 | 10-40 | Number of MFCC coefficients |
| `--n-fft` | 2048 | 512-8192 | FFT window size |
| `--hop-length` | 512 | 128-2048 | Hop length for framing |
| `--min-freq` | 0 | 0-20000 | Minimum frequency |
| `--max-freq` | 11025 | 1000-22050 | Maximum frequency |

## Pitfalls

- **Silent files**: Audio files with silence will produce empty/near-empty visualizations — check amplitude first
- **YouTube rate limiting**: YouTube may block frequent automated requests — use direct file URLs when possible
- **Format compatibility**: Some formats (e.g., AAC in MP4) may require additional ffmpeg codecs
- **Memory usage**: High-resolution spectrograms on long files can use significant RAM
- **Mono vs stereo**: Some features expect mono input — convert with `ffmpeg -i input.mp3 -ac 1 output.wav`
- **Clipping**: Distorted audio will show as saturated bands in spectrograms

## Verification

- [ ] Audio was successfully loaded and sampled (check for "loaded N samples" output)
- [ ] Output visualization file exists and is non-empty
- [ ] Features match the expected type (verify labels on axes)
- [ ] For raw data: JSON contains expected fields and dimensions
- [ ] No silent/empty regions in the visualization

## Related Skills

- `creative/comfyui` — for AI-generated visual art including spectrogram-to-image
- `creative/p5js` — for custom audio visualization rendering
