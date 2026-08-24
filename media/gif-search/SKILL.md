---
name: gif-search
description: "Search/download GIFs from Tenor via curl + jq."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
prerequisites:
  env_vars: [TENOR_API_KEY]
  commands: [curl, jq]
metadata:
  hermes:
    tags: [GIF, Media, Search, Tenor, API]
    related_skills: [youtube-content]
---

# GIF Search (Tenor API)

Search and download GIFs directly via the Tenor API using curl. No extra tools needed.

## What This Skill Does

Searches and downloads GIFs from the Tenor API using `curl` and `jq`. The `TENOR_API_KEY` environment variable provides authentication. GIF URLs can be used directly in chat (markdown image syntax) or saved to disk. Loads `skill_view(name='youtube-content')` for video-based GIF creation from YouTube videos.

## When to Use

Useful for finding reaction GIFs, creating visual content, and sending GIFs in chat.

## Setup

Set your Tenor API key in your environment (add to `${HERMES_HOME:-~/.hermes}/.env`):

```bash
TENOR_API_KEY=your_key_here
```

Get a free API key at https://developers.google.com/tenor/guides/quickstart — the Google Cloud Console Tenor API key is free and has generous rate limits.

## Prerequisites

- `curl` and `jq` (both standard on macOS/Linux)
- `TENOR_API_KEY` environment variable

## Search for GIFs

```bash
# Search and get GIF URLs
curl -s "https://tenor.googleapis.com/v2/search?q=thumbs+up&limit=5&key=${TENOR_API_KEY}" | jq -r '.results[].media_formats.gif.url'

# Get smaller/preview versions
curl -s "https://tenor.googleapis.com/v2/search?q=nice+work&limit=3&key=${TENOR_API_KEY}" | jq -r '.results[].media_formats.tinygif.url'
```

## Download a GIF

```bash
# Search and download the top result
URL=$(curl -s "https://tenor.googleapis.com/v2/search?q=celebration&limit=1&key=${TENOR_API_KEY}" | jq -r '.results[0].media_formats.gif.url')
curl -sL "$URL" -o celebration.gif
```

## Get Full Metadata

```bash
curl -s "https://tenor.googleapis.com/v2/search?q=cat&limit=3&key=${TENOR_API_KEY}" | jq '.results[] | {title: .title, url: .media_formats.gif.url, preview: .media_formats.tinygif.url, dimensions: .media_formats.gif.dims}'
```

## API Parameters

| Parameter | Description |
|-----------|-------------|
| `q` | Search query (URL-encode spaces as `+`) |
| `limit` | Max results (1-50, default 20) |
| `key` | API key (from `$TENOR_API_KEY` env var) |
| `media_filter` | Filter formats: `gif`, `tinygif`, `mp4`, `tinymp4`, `webm` |
| `contentfilter` | Safety: `off`, `low`, `medium`, `high` |
| `locale` | Language: `en_US`, `es`, `fr`, etc. |

## Available Media Formats

Each result has multiple formats under `.media_formats`:

| Format | Use case |
|--------|----------|
| `gif` | Full quality GIF |
| `tinygif` | Small preview GIF |
| `mp4` | Video version (smaller file size) |
| `tinymp4` | Small preview video |
| `webm` | WebM video |
| `nanogif` | Tiny thumbnail |

## Notes

- URL-encode the query: spaces as `+`, special chars as `%XX`
- For sending in chat, `tinygif` URLs are lighter weight
- GIF URLs can be used directly in markdown: `![alt](url)`

## Pitfalls

- **Missing API key**: If `TENOR_API_KEY` is not set, all requests return 401 — verify with `echo $TENOR_API_KEY`
- **Rate limiting**: Tenor API has rate limits — space out requests for bulk operations
- **GIF not loading**: Some GIFs may be from deleted/suspended accounts — try alternative search terms
- **Large GIF files**: Full-size GIFs can be 5-10MB — prefer `tinygif` or `mp4` formats for chat
- **Content filtering**: Use `contentfilter=high` for family-safe searches
- **URL encoding**: Spaces must be `+` or `%20`, special chars must be URL-encoded

## Verification

- [ ] `TENOR_API_KEY` is set in environment
- [ ] Search returns results (non-empty JSON response)
- [ ] GIF URLs are valid and download successfully
- [ ] Downloaded file is a valid GIF (check file size > 1KB)
- [ ] Content filter is set appropriately for the context
- [ ] For chat: GIF URL loads inline (test with markdown syntax)
