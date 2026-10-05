---
description: "Image of a math formula to LaTeX with pix2tex (LaTeX-OCR): usage, stale pinned dependencies, install resolution on Python 3.14 (dry-run only), alternatives"
source_repo: lukas-blecher/LaTeX-OCR (MIT)
tested_version: README and PyPI metadata read (pix2tex 0.1.4, 2025-01-18); `pip install --dry-run pix2tex` on Python 3.14.6 resolved a set; NOT installed or run (torch download is multi-GB)
verified_date: "2026-10-05"
---

# pix2tex: formula image to LaTeX

A learned model (ViT encoder, transformer decoder) that takes an image of a single math formula and returns LaTeX. Use it for equation snippets from screenshots or scans;
for whole scanned documents with equations use `marker-pdf` (see `SKILL.md`), which handles layout.

```bash
pip install "pix2tex[gui]"        # CLI `pix2tex`, GUI `latexocr`; checkpoints download automatically on first use
```

```python
from PIL import Image
from pix2tex.cli import LatexOCR
model = LatexOCR()                # downloads checkpoints at first call
print(model(Image.open("eq.png")))
```

Other interfaces per the README: `pix2tex` CLI (images from disk or clipboard), `latexocr` screenshot GUI (Linux needs `gnome-screenshot`, or `grim`+`slurp` on wlroots), a Streamlit
demo and FastAPI service (`pip install "pix2tex[api]"`, `python -m pix2tex.api.run`, port 8502; docker image `lukasblecher/pix2tex:api`). A `temperature` parameter makes the output deterministic when low and varied on "Retry" when higher.
The model works best on **small-resolution** images; a second network predicts the optimal resize automatically. Crop to one formula; it does not segment a page.

## Maintenance and install facts (checked 2026-10-05)

- Latest release **0.1.4 on 2025-01-18** (about nine months old at check time); MIT.
- Declared dependencies include exact pins from 2021-22: `x-transformers==0.15.0`, `timm==0.5.4`, `albumentations<=1.4.24`, plus `torch>=1.7.1`, `transformers>=4.18.0`, `opencv-python-headless`, `einops`.
- `pip install --dry-run pix2tex` on Python 3.14.6 (Windows) **resolved**: pix2tex 0.1.4, torch 2.14.1, torchvision 0.29.1, transformers 5.18.0, tokenizers 0.23.2, timm 0.5.4, x-transformers 0.15.0, albumentations 1.4.24, opencv-python-headless 5.0.0.93. Resolving is not working: a 2021-era `timm`/`x-transformers` against `transformers` 5.x and a very new `torch` may fail at import or inference. Untested; try it in an isolated venv (and an older Python if it breaks) and budget a multi-GB download.
- Checkpoints are fetched from the network at first run; for offline or reproducible pipelines, cache them and pin the files.

## Alternatives

| Need | Option |
|---|---|
| Equations inside scanned PDFs | `marker-pdf` (heavier, layout-aware); `texify` 0.2.1 (PyPI, Python `<4.0,>=3.10`, classifiers to 3.13, GPL-3.0-or-later) |
| Hosted OCR | a vision-capable LLM prompted for LaTeX, then verify by compiling |
| Handwritten math | not pix2tex's target; check the model card before use |

## Verify any OCR'd LaTeX

Compile the result (`pdflatex`/`tectonic`/KaTeX in a headless page) and compare the rendered image to the source; models produce plausible but wrong LaTeX (swapped sub/superscripts, dropped bars). Treat OCR output as a draft, never as ground truth.
