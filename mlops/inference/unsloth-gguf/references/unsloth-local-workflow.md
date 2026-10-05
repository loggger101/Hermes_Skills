---
description: "Unsloth local workflow (unslothai/unsloth, Apache-2.0): LoRA fine-tuning -> GGUF export pipeline + `unsloth start hermes` one-command local-model bridge"
source_repos: unslothai/unsloth (clone @ 2026-09-13)
tested_version: main branch read 2026-09-13; no install attempted (GPU training stack, not needed for the patterns below)
verified_date: "2026-09-13"
---

# Unsloth — Local Fine-Tune → GGUF Workflow + Hermes Bridge [SRC]

Unsloth = fast LoRA/QLoRA fine-tuning of LLMs (Apache-2.0; the `studio/` web UI is AGPL-3.0). For a
local-model workflow it matters in two ways: **(1)** it's the most-used producer of the exact GGUF
quants you run on LM Studio, and **(2)** its CLI ships a **first-party Hermes Agent integration**.

## `unsloth start hermes` — one-command local model bridge [SRC]

From `unsloth_cli/commands/start.py`:

```bash
pip install unsloth        # PyPI metadata has NO "all" extra (see the 2026-10-05 check below); or the Unsloth Desktop app from GitHub releases
unsloth start hermes --model unsloth/Qwen3.8-27B-GGUF:UD-Q4_K_XL
# variant names follow llama.cpp quant naming; UD-* = Unsloth Dynamic quants
```

Verified mechanics from source (not marketing):

- It launches/attaches to a **local Unsloth server** (`--serve` auto-starts one with `llama-server`;
  attach mode uses an already-running server) and writes a **session-scoped Hermes config**: provider id
  `"unsloth"`, env key `UNSLOTH_API_KEY`, model default pointed at the loaded GGUF. No hosted API is involved.
- The README's own example pins `Qwen3.8-27B-GGUF:UD-Q4_K_XL` — i.e., this is a supported path for exactly
  the class of local quant you run via LM Studio today (`qwen3.8-27b@q4_k_xl`). Use it when you want an
  alternative local server (e.g. to test a freshly fine-tuned LoRA merge) without touching your LM Studio setup.
- **Security note from the source itself**: `unsloth start hermes` pins the Hermes installer script AND its
  repo checkout to one full commit (`_HERMES_INSTALL_COMMIT`) so upstream branch changes can't silently swap
  code it runs with your privileges — a good pattern, and a reason not to point other tools at unpinned
  install scripts.
- Server-side gotcha documented in the same file: llama-server sends **no SSE bytes while processing the
  prompt**; slow local hosts trip client reconnect timeouts (measured case: Codex's default 5-min silence
  limit, ~16 tok/s CPU box → first turn never completed). If you wire any agent to a slow local server,
  raise its idle-stream timeout well above one full cold first turn.

## Fine-tune → GGUF export pipeline [SRC]

The code path that turns a LoRA into the file LM Studio loads (`unsloth/save.py`):

1. `model.save_pretrained(...)` / `save_to_gguf(model, ...)` — PEFT (LoRA) adapters are **merged** during
   conversion; non-PEFT checkpoints convert in place from `_name_or_path`.
2. Conversion runs through `unsloth_zoo.llama_cpp` (`convert_to_gguf`, `quantize_gguf`) wrapping llama.cpp's
   converter — so the output is byte-compatible with any GGUF consumer (LM Studio, Ollama, llama-server).
3. Quant list: pass e.g. `["f16", "q4_k_m", "ud_q4_k_xl"]` to write several sizes in one export; a method
   equal to the initial conversion dtype is skipped (file already on disk).

Two source-verified traps worth knowing before debugging an export that "lost" space:

- **Intermediate f16/bf16 GGUF staging**: `convert_to_gguf` resolves its output against the process CWD when
  given a bare filename, then Unsloth *moves* it into the `_gguf/` dir — across filesystems that's a copy. On
  constrained disks (Kaggle `/kaggle/working`, small system drives) the ~2-bytes-per-parameter intermediate is
  the largest single staging artifact and can land where you didn't redirect output to. Check free space on the
  CWD, not just the target dir.
- **bf16→f16 fallback**: hardware without bf16 drops a requested `["bf16", ...]` export to f16 *after* dtype
  resolution — size estimates that assume one file can be off by an entire checkpoint (their example: ~15 GB on Qwen3-8B).

## When to use vs alternatives

| Goal | Pick | Why not the other |
|---|---|---|
| Fine-tune a model you'll run locally as GGUF | **Unsloth** → `save_to_gguf` | Raw llama.cpp converter needs manual LoRA merge first; Unsloth does it in one call |
| Just serve/run an existing GGUF on this box | LM Studio / llama-server (see `mlops/inference/llama-cpp/references/server.md`) | No training needed — don't pull a GPU stack for inference |
| Fine-tune without a big NVIDIA card | Unsloth QLoRA 4-bit + `--no-bf16` path, or skip fine-tuning and use prompt/RAG | Verify VRAM math first; the export staging trap above doubles peak disk need |

## 2026-10-05 re-check (PyPI JSON metadata, GitHub releases and commits; nothing installed or run)

- **PyPI**: `unsloth` **2026.9.14**, one pure-Python wheel (26.1 MB), `requires_python <3.15,>=3.9`. The README line
  `pip install unsloth[all]` above is not backed by the metadata: of **165 extras** (`huggingface`, `huggingfacenotorch`, `studio`,
  `windows`, `amd`, `conda`, `eval`, `flashattention`, `triton`, many `cuXXX-torchYYY` and `colab-*` combinations) there is **no `all`**;
  pip would warn that the extra is missing and install the base package only.
- **Base dependencies are the full GPU training stack**: `torch<2.13,>=2.4`, `torchvision`, `bitsandbytes`, `peft`, `accelerate`,
  `datasets<4.4`, `unsloth_zoo`, `xformers` and `triton` (`triton-windows` on Windows), plus CLI libraries (`tyro`, `typer`, `click`).
  Do not install it into a general environment just to run `unsloth start hermes`; use a dedicated venv, or the Desktop app.
- **Releases are two tracks**: PyPI date-versions (2026.9.x) for the library, and GitHub `v0.1.xxx-beta` tags (v0.1.902-beta on
  2026-10-01, three betas in eight days) carrying Unsloth Desktop installers (macOS dmg/app, Linux AppImage, Windows build) and
  a `prebuilt-wheels-cu13` release of CUDA 13 / torch 2.13 kernel wheels (for example `causal_conv1d`).
- **Fast-moving**: about 100 commits between 2026-09-13 and 2026-10-05, including an LM Studio provider and a reasoning-effort
  slider in Studio, a `--think` flag on the CLI to show a thinking model's reasoning when attached to a running Unsloth, MCP
  pre-registered OAuth clients, and Windows uv-cache placement. Re-read `unsloth_cli/commands/start.py` before relying on the
  `start hermes` flags above.
