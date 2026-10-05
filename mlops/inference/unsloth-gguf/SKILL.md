---
name: unsloth-gguf
description: "Unsloth fine-tune to GGUF; unsloth start hermes."
version: 1.0.0
author: Hermes Agent (promoted from llama-cpp references; source-read of unslothai/unsloth, 2026-09-13)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [unsloth, lora, qlora, fine-tuning, gguf, llama-cpp, lm-studio, hermes, local-models]
    related_skills: [llama-cpp, serving-llms-vllm, huggingface-hub, model-export-deploy, hermes-agent]
---

# Unsloth: local fine-tune to GGUF

## What This Skill Does

Explains how Unsloth (fast LoRA/QLoRA fine-tuning, Apache-2.0; its `studio/` web UI is AGPL-3.0) fits a local-model workflow: it produces the GGUF quants you run in LM Studio, llama-server or Ollama, and its CLI ships a first-party Hermes Agent bridge (`unsloth start hermes`). Findings are **source-read** from the repo (no GPU training stack was installed), so treat mechanics as read, not run.

## When to Use

- Fine-tuning a model with LoRA and needing a GGUF file for local inference
- Pointing Hermes at a local model through Unsloth's server instead of LM Studio
- An export "lost" disk space or wrote an unexpected file size
- Not for running or tuning an existing GGUF (`llama-cpp`), serving at scale (`serving-llms-vllm`), or exporting non-GGUF formats (`model-export-deploy`)

## Procedure

1. Install: `pip install unsloth` (PyPI metadata has no `all` extra) or the Unsloth Desktop app.
2. Local Hermes bridge: `unsloth start hermes --model unsloth/Qwen3.8-27B-GGUF:UD-Q4_K_XL`. Variant names follow llama.cpp quant naming; `UD-*` are Unsloth Dynamic quants. It starts or attaches to a local Unsloth server (`--serve` auto-starts one with `llama-server`) and writes a session-scoped Hermes config (provider id `unsloth`, env key `UNSLOTH_API_KEY`); no hosted API is involved.
3. Export: `model.save_pretrained(...)` or `save_to_gguf(model, ...)`. LoRA adapters are merged during conversion, then `unsloth_zoo.llama_cpp` wraps llama.cpp's converter and quantizer, so output is compatible with LM Studio, Ollama and llama-server. Pass several quants at once, e.g. `["f16", "q4_k_m", "ud_q4_k_xl"]`.
4. Before exporting, check free space on the **current working directory**, not only the target directory (below).
5. Wiring any agent to a slow local server: raise its idle-stream timeout above one full cold first turn.

## Pitfalls

- **Intermediate f16/bf16 staging**: `convert_to_gguf` resolves a bare output filename against the CWD and then moves it into `_gguf/`; across filesystems that is a copy, and the roughly 2 bytes per parameter intermediate is the largest staging artifact. Small system drives and Kaggle `/kaggle/working` run out.
- **bf16 to f16 fallback**: hardware without bf16 drops a requested `bf16` export to f16 after dtype resolution, so size estimates can be off by a whole checkpoint (their example: about 15 GB for Qwen3-8B).
- **No SSE bytes while the prompt is processed**: llama-server stays silent during prompt processing; a slow host (about 16 tok/s CPU) tripped a client's default 5-minute silence limit and the first turn never completed.
- A method equal to the initial conversion dtype is skipped because the file already exists.
- Security pattern to copy: `unsloth start hermes` pins both the Hermes installer script and its repo checkout to one full commit, so upstream branch changes cannot swap the code it runs. Do not point tools at unpinned install scripts.

## Verification

- [ ] Free space on the working directory was checked against about 2 bytes per parameter before export
- [ ] The exported GGUF loads in the target runtime (LM Studio, llama-server)
- [ ] The agent's stream timeout exceeds the slowest cold first turn
- [ ] Any installer run through the bridge is pinned to a commit

## References

- `references/unsloth-local-workflow.md` - `unsloth start hermes` mechanics, the fine-tune to GGUF export code path, the two export traps, and the 2026-10-05 install check (source-read)
