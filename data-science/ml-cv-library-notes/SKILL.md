---
name: ml-cv-library-notes
description: "Torch, CuPy, Open3D, gensim and CV libs: live-run traps."
version: 1.0.0
author: Hermes Agent (promoted from python-data-science references, live-run 2026-10)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [pytorch, autograd, cupy, open3d, supervision, gensim, gpu, computer-vision, point-cloud, nlp, install-reality]
    related_skills: [python-data-science, python-numerics-gotchas, model-export-deploy, test-infra-ml, evolutionary-ml]
---

# ML, GPU and computer-vision library notes

## What This Skill Does

Answers "will this library install and behave on this machine, and what fails silently" for six heavier libraries: PyTorch 2.14, HIPS autograd 1.9, CuPy 14.2, Open3D 0.20, roboflow supervision 0.30 and gensim 4.4. Each was installed and run on Windows with Python 3.14 (no GPU), and its reference records the exact outputs, install sizes and the errors you will meet.

## When to Use

- Choosing a differentiation, GPU-array, point-cloud, detection post-processing or topic-modelling library
- Writing code that must run without a GPU or without a C compiler (CI, agents, cron)
- A torch, DataLoader, ONNX or `torch.compile` call fails on Windows or Python 3.14
- Checking install size, wheel availability or licence before adding a dependency
- Not for the general modelling workflow (`python-data-science`), exporting trained models (`model-export-deploy`), or numpy/scipy/pandas behaviour (`python-numerics-gotchas`)

## Which library, which reference

| Task | Library | Reference | One-line warning |
|---|---|---|---|
| Neural nets, tensors, training | torch 2.14.1+cpu | `references/pytorch-notes.md` | default `torch.compile` needs `cl.exe`; bf16/fp16 on CPU is 150-450x slower; DataLoader workers re-import the main script on Windows |
| Gradients of plain NumPy code, `jac=True` for SciPy | autograd 1.9.1 | `references/autograd-notes.md` | import `autograd.numpy`; int input, non-scalar output and in-place assignment all raise; `check_grads` is the unit test |
| NumPy on an NVIDIA GPU | CuPy 14.2.0 | `references/cupy-notes.md` | `import cupy` succeeds with no GPU; test `cupy.cuda.is_available()` and the first allocation |
| Point clouds, meshes, ICP | Open3D 0.20.0 | `references/open3d-notes.md` | 488 MB install; reading a missing file returns an empty cloud, not an error; ICP is local, so give a good initial guess |
| Post-process detector output (NMS, zones, line counts) | supervision 0.30.7 | `references/supervision-cv-notes.md` | `ByteTrack` removed in 0.31; bad adapter input returns empty `Detections` silently |
| Word2Vec, LDA | gensim 4.4.0 | `references/gensim-notes.md` | no cp314 wheel (sdist needs a compiler), use a 3.11-3.13 venv; LGPL-2.1 |

## Procedure

1. Check wheel and footprint first: `pip download --no-deps <pkg>` or `uv pip install --dry-run`; the references give sizes (torch 664 MB, Open3D 488 MB, supervision 343 MB, CuPy 109 MB).
2. Gate GPU code on a real allocation, not on the import: `cp.cuda.is_available()`, then fall back to NumPy.
3. Make "nothing returned" distinguishable from "failed": assert non-empty results after Open3D reads and supervision adapters.
4. Windows multiprocessing: keep top-level code to imports and definitions, put the entry point under `if __name__ == "__main__":`, and use module-level functions (not lambdas) for `collate_fn`.
5. For export, use `torch.export.export(model.eval(), (x,))` on Python 3.14 (`jit.trace` warns), and install `onnxscript` before `torch.onnx.export`.
6. Record library, version and result in the owning reference when you find a new trap.

## Pitfalls

- Treating `import` success as capability (CuPy imports with no driver).
- Assuming `torch.load` accepts arbitrary pickles: `weights_only` resolves to True, so custom classes raise `UnpicklingError`.
- Running a `torch.compile` backend of `eager`/`aot_eager` for speed: it traces but gives no speedup.
- Comparing GPU or multithreaded results bit-for-bit: gensim `workers=1` plus a seed is the reproducible setting; others are not guaranteed.
- Quoting timings from the references on other hardware: they are single-machine measurements dated 2026-10-05.

## Verification

- [ ] The code path runs with no GPU and no C compiler, or the requirement is documented
- [ ] Each library's version matches its reference, or the probe was re-run
- [ ] Empty or default results are asserted against, not assumed to mean "nothing found"
- [ ] Dependency size and licence were checked before adding the library

## References

- `references/pytorch-notes.md` - torch 2.14.1+cpu on Windows/py3.14: `torch.compile` without a compiler, `jit.trace` warning, ONNX needs `onnxscript`, `torch.load` weights-only default, fp16/bf16 CPU slowness, DataLoader spawn costs, autograd error table
- `references/autograd-notes.md` - autograd 1.9.1 on numpy 2.5: `grad`/`jacobian`/`hessian`, SciPy `jac=True`, the four errors you hit, the double-`where` guard, `check_grads`
- `references/cupy-notes.md` - CuPy 14.2.0: installs and imports with no GPU, arrays fail; NumPy-difference rules, async timing and memory-pool rules from the docs
- `references/open3d-notes.md` - Open3D 0.20.0 headless: voxel/normals/ICP/KD-tree/PLY/mesh checks with numbers, empty cloud on a missing file, ICP is local
- `references/supervision-cv-notes.md` - supervision 0.30.7 on synthetic detections: `Detections`/NMS/zones/`LineZone`/annotators, optional OpenCV, deprecated ByteTrack, silent empty result
- `references/gensim-notes.md` - gensim 4.4.0: no cp314 wheel, small Word2Vec/LDA run in a 3.11 venv, reproducibility, out-of-vocabulary `KeyError`, LGPL note
