---
name: nano-pdf
description: "Edit text in existing PDFs via natural-language prompts."
version: 1.0.0
author: community
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [PDF, Documents, Editing, NLP, Productivity]
    homepage: https://pypi.org/project/nano-pdf/
    related_skills: [pdf, ocr-and-documents]

---

# nano-pdf

Edit PDFs using natural-language instructions. Point it at a page and describe what to change. For structural PDF work (merge, split, forms, watermarks, creation), see `skill_view(name='pdf')`; for text extraction from scans, see `skill_view(name='ocr-and-documents')`.

## When to Use

- "Fix a typo on page 3 of this PDF"
- "Change the client name from Acme Corp to Acme Industries"
- "Update the date from January to February"
- "Rewrite this paragraph to be clearer"

**Skip when:** You need structural changes (merge, split, add pages, fill forms) — use `skill_view(name='pdf')` instead. You need text extraction from scanned PDFs — use `skill_view(name='ocr-and-documents')` instead. For creating PDFs from scratch — use `skill_view(name='pdf')` (pdf_create).

## What This Skill Does

Wraps an LLM-based PDF text editor that locates text regions on a specific page by their coordinates and rewrites them based on a natural-language instruction. The tool:
1. Renders the target page to an image
2. Detects text blocks and their bounding boxes
3. Uses vision + LLM to understand the instruction and generate replacement text
4. Re-rasterizes the page with the edited text in-place

This is not a full PDF editor — it works best for targeted text changes on a single page at a time.

## Prerequisites

```bash
# Install with uv (recommended — already available in Hermes)
uv pip install nano-pdf

# Or with pip
pip install nano-pdf
```

**Requirements:**
- An OpenAI or Anthropic API key (set as `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`)
- The PDF must be text-based (not a scanned image — use `skill_view(name='ocr-and-documents')` for scans)

## Process

### 1. Identify the target
Note the page number and the exact text you want to change. Read the PDF first if needed:

```bash
# Check page count
nano-pdf info <file.pdf>
```

### 2. Edit the text
```bash
nano-pdf edit <file.pdf> <page_number> "<instruction>"
```

### 3. Verify the output
```bash
# Read the edited PDF to verify changes
read_file <output_file.pdf>
```

### 4. Iterate if needed
If the edit didn't apply correctly, re-run with a more specific instruction.

## Examples

```bash
# Change a title on page 1
nano-pdf edit deck.pdf 1 "Change the title to 'Q3 Results' and fix the typo in the subtitle"

# Update a date on a specific page
nano-pdf edit report.pdf 3 "Update the date from January to February 2026"

# Fix content
nano-pdf edit contract.pdf 2 "Change the client name from 'Acme Corp' to 'Acme Industries'"
```

## Pitfalls

- **Page numbering**: Page numbers may be 0-based or 1-based depending on version — if the edit hits the wrong page, retry with ±1
- **Not a full editor**: Complex layout modifications (adding/removing paragraphs, reflowing text) may need a different approach — use `skill_view(name='pdf')` for structural edits
- **Scanned PDFs**: nano-pdf cannot edit scanned/image-based PDFs. Use `skill_view(name='ocr-and-documents')` first to extract text, then consider recreating the PDF
- **Font matching**: The tool tries to match existing fonts, but complex font changes may look inconsistent
- **API key required**: The tool uses an LLM under the hood — ensure your API key is configured

## Verification

- [ ] The output PDF was read back and the edit was confirmed visually
- [ ] No other pages were affected by the edit
- [ ] File size is reasonable (not inflated by failed re-render)
- [ ] For multi-page PDFs: verify pages before and after the target page are unchanged

## Notes

- Always verify the output PDF after editing (use `read_file` to check file size, or open it)
- The tool uses an LLM under the hood — requires an API key (check `nano-pdf --help` for config)
- Works well for text changes; complex layout modifications may need `skill_view(name='pdf')` instead
