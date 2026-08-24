---
name: youtube-content
description: "YouTube transcripts to summaries, threads, blogs."
version: 1.0.0
author: Teknium (teknium1), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [YouTube, Video, Transcripts, Media]
    related_skills: [blogwatcher, songsee]

---

# YouTube Content Tool

## What This Skill Does

Extracts transcripts from YouTube videos and transforms them into structured content (chapters, summaries, threads, blog posts, quotes). Uses `youtube-transcript-api` via a helper script to fetch transcripts (auto-generated or manual), validates the output, chunks long transcripts, and formats the result according to the user's request. Loads `skill_view(name='songsee')` for audio analysis and `skill_view(name='blogwatcher')` for RSS monitoring.

Extracts transcripts from YouTube videos and converts them into useful formats.

## When to Use

Use when the user shares a YouTube URL or video link, asks to summarize a video, requests a transcript, or wants to extract and reformat content from any YouTube video. Transforms transcripts into structured content (chapters, summaries, threads, blog posts).

## Prerequisites

```bash
uv pip install youtube-transcript-api
```

**Requirements:**
- A working internet connection
- The video must have transcripts available (auto-generated or manual)
- `uv` for dependency management (already available in Hermes)

## Helper Script

`SKILL_DIR` is the directory containing this SKILL.md file. The script accepts any standard YouTube URL format, short links (youtu.be), shorts, embeds, live links, or a raw 11-character video ID.

```bash
# JSON output with metadata
uv run python SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# Plain text (good for piping into further processing)
uv run python SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only

# With timestamps
uv run python SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps

# Specific language with fallback chain
uv run python SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
```

## Output Formats

After fetching the transcript, format it based on what the user asks for:

- **Chapters**: Group by topic shifts, output timestamped chapter list
- **Summary**: Concise 5-10 sentence overview of the entire video
- **Chapter summaries**: Chapters with a short paragraph summary for each
- **Thread**: Twitter/X thread format — numbered posts, each under 280 chars
- **Blog post**: Full article with title, sections, and key takeaways
- **Quotes**: Notable quotes with timestamps

### Example — Chapters Output

```
00:00 Introduction — host opens with the problem statement
03:45 Background — prior work and why existing solutions fall short
12:20 Core method — walkthrough of the proposed approach
24:10 Results — benchmark comparisons and key takeaways
31:55 Q&A — audience questions on scalability and next steps
```

## Process

1. **Fetch** the transcript using the helper script with `--text-only --timestamps` via `uv run python`.
2. **Validate**: confirm the output is non-empty and in the expected language. If empty, retry without `--language` to get any available transcript. If still empty, tell the user the video likely has transcripts disabled.
3. **Chunk if needed**: if the transcript exceeds ~50K characters, split into overlapping chunks (~40K with 2K overlap) and summarize each chunk before merging.
4. **Transform** into the requested output format. If the user did not specify a format, default to a summary.
5. **Verify**: re-read the transformed output to check for coherence, correct timestamps, and completeness before presenting.

## Format Selection Guide

| User asks for | Output format |
|---------------|--------------|
| "summarize" | Summary — 5-10 bullet points covering all key points |
| "twitter thread" | Thread — 8-15 numbered posts, each < 280 chars |
| "blog post" | Blog — title, intro, sections, key takeaways |
| "chapters" | Timestamps + topic labels, grouped by content shift |
| "key points" | Bullet list of the 5-7 most important facts |
| "quotes" | Notable quotes with timestamps for attribution |

## Error Handling

- **Transcript disabled**: tell the user; suggest they check if subtitles are available on the video page.
- **Private/unavailable video**: relay the error and ask the user to verify the URL.
- **No matching language**: retry without `--language` to fetch any available transcript, then note the actual language to the user.
- **Dependency missing**: run `uv pip install youtube-transcript-api` and retry.
- **API quota exceeded**: YouTube may rate-limit transcript requests; suggest waiting and retrying.

## Pitfalls

- **Auto-generated vs manual**: Auto-generated transcripts may contain errors — verify factual claims against the video content
- **Long videos**: Transcripts for videos >30 minutes can be 20K+ characters — always chunk before processing
- **Multiple languages**: The `--language` flag with fallback chain handles this, but verify the correct language was fetched
- **Music-only segments**: Transcripts may contain `[Music]` placeholders — handle these gracefully in summaries
- **Speaker changes**: Transcripts don't clearly mark speaker changes — annotate when creating thread/blog formats

## Verification

- [ ] Transcript was fetched and validated (non-empty, correct language)
- [ ] Long videos were chunked before processing (if >50K chars)
- [ ] Output format matches what the user requested
- [ ] Timestamps in chapter/thread formats are accurate
- [ ] Key facts are verifiable against the transcript
