# PyTorch 2.14.1 (CPU) on Windows + Python 3.14: what actually happens

Source: [pytorch/pytorch](https://github.com/pytorch/pytorch) (BSD-3, v2.14.1 released 2026-09-30). `pip install torch` into a
scratch `--target` gave **`torch 2.14.1+cpu`** (cp314 win_amd64 wheel; 664 MB on disk with sympy, networkx, jinja2, fsspec,
filelock), Python 3.14.6, 12 CPU threads, no CUDA. Every line is a run result; GPU, distributed and `torch.compile` speedups
were not testable here. Complements `autograd-notes.md` (the HIPS library, not torch.autograd) and `cupy-notes.md`.

## 1. Things that changed or fail on this toolchain

| Probe | Result |
|---|---|
| `torch.compile(f)` (default inductor) | **`InductorError: InvalidCxxCompiler: Compiler: cl is not found`**: no `cl.exe`, `gcc` or `clang` on PATH. Install the MSVC Build Tools, or use a backend that needs no C++ compiler |
| `torch.compile(f, backend="eager")`, `"aot_eager"` | both returned the right values (0.0 s, 0.2 s): they trace but give **no speedup**; use them only to test graph capture |
| `torch.jit.trace(model, x)` | works but warns `FutureWarning: torch.jit.trace is not supported in Python 3.14+ and may break`; same for `trace_method` |
| `torch.export.export(model.eval(), (x,))` | returned an `ExportedProgram`: the supported path on 3.14 (saving it was not tested) |
| `torch.onnx.export(model, args, "m.onnx")` | `ModuleNotFoundError: No module named 'onnxscript'`: the current exporter needs `onnxscript` (and `onnx`) installed separately |
| `torch.load(f)` default | the signature default is `weights_only=None` which **resolves to True**: a checkpoint of tensors plus plain dicts loaded; a dict holding a custom class raised `UnpicklingError: Weights only load failed ...`. Pass `weights_only=False` only for files you produced |
| half precision on CPU | 1024x1024 matmul x3: fp32 **15-34 ms**, bfloat16 **4.9-5.7 s**, float16 **5.9-6.7 s** (roughly 150-450x slower). Do not run bf16/fp16 on this CPU; keep fp32 off-GPU |
| threads | 1024x1024 matmul x5: 1 thread 122-198 ms, 4 threads 63-81 ms, 12 threads 40-61 ms (three noisy runs); `torch.set_num_threads(n)` is the knob |

## 2. DataLoader workers on Windows (spawn)

- `num_workers=2` with a picklable dataset worked, but **every worker re-imports the main script**: all top-level code outside
  `if __name__ == "__main__":` ran again in each worker (my compile attempt and matmul benchmarks printed three times), and 8
  tiny items took **17.4 s**. Keep top-level code to imports and definitions.
- `collate_fn=lambda z: z` with workers -> `PicklingError: Can't pickle local object <lambda>`, preceded by `UserWarning: Got pickle
  error when attempting to start a worker Process` (its text points at the Python 3.14 start-method change): use a module-level function.
- `shuffle=True` is reproducible after `torch.manual_seed(0)` set before building the loader (checked first batch, workers=0).
- `tensor.share_memory_().is_shared()` is True.

## 3. Autograd traps, each reproduced (exact errors)

| Code | Error |
|---|---|
| `x.add_(1)` on a leaf with `requires_grad` | `a leaf Variable that requires grad is being used in an in-place operation` |
| `(x*2).backward()` on a vector | `grad can be implicitly created only for scalar outputs` (pass `gradient=` or reduce) |
| `backward()` twice on one graph | `Trying to backward through the graph a second time` (use `retain_graph=True` only if you must) |
| `torch.tensor([1, 2], requires_grad=True)` | `Only Tensors of floating point and complex dtype can require gradients` |
| `b = a.sigmoid(); b.add_(1); b.sum().backward()` | `one of the variables needed for gradient computation has been modified by an inplace operation ... output 0 of Sigmoid` |
| `with torch.inference_mode(): im = a*2` then `(im*a).sum().backward()` | `Inference tensors cannot be saved for backward` (`no_grad` outputs have `requires_grad False` and are fine to reuse) |
| `torch.ones(2, requires_grad=True).numpy()` | `Can't call numpy() on Tensor that requires grad. Use tensor.detach().numpy()` |

`detach()` shares storage with the source (same `data_ptr`); `clone()` does not.

## 4. Dtypes, views, shapes

- Defaults: `torch.tensor([1, 2])` is `int64`, `torch.tensor([1., 2])` is `float32`; `/` on two int tensors gives `float32`,
  `//` stays `int64`. `int tensor + 1.5` -> float32; `float32 + float64` -> **float64**.
- Integer overflow wraps silently: `uint8 255 + 1 = 0`, `int8 127 + 1 = -128`.
- `torch.from_numpy(a)` **shares memory** (writing `a[0]` changed the tensor) and keeps float64; `torch.tensor(a)` copies.
- `t().view(6)` on a non-contiguous tensor raises `view size is not compatible ... Use .reshape(...)`; `reshape` copies in that case
  and returns a view for contiguous input (same `data_ptr`).
- `mse_loss(pred(3,1), target(3,))` emits `UserWarning: Using a target size ... that is different to the input size`
  (it silently broadcasts to 3x3). Match shapes with `squeeze`/`unsqueeze`.
- `use_deterministic_algorithms(True)` did not break CPU `cumsum` or `index_add_` (results correct); it matters on GPU.

## 5. nn.Module behaviours

- Modules start in **training mode**; `eval()` flips it. `BatchNorm1d` in training mode with batch size 1 raises
  `ValueError: Expected more than 1 value per channel when training`; in eval mode a batch of 1 is fine.
- `state_dict()` tensors share storage with the parameters. `load_state_dict` with a missing key raises `RuntimeError: Error(s)
  in loading state_dict ... Missing key(s)`; `strict=False` returns `_IncompatibleKeys(missing_keys=[], unexpected_keys=['extra'])`
  instead of raising, so **check the returned lists** or typos pass silently.
- Seed reproducibility: `manual_seed(0)` twice gives identical `rand(3)`.

## Checklist before trusting a torch script on this machine

1. Print `torch.__version__` (look for `+cpu`) and `torch.cuda.is_available()` first.
2. Guard `main`, define collate functions at module level, keep top-level code import-only.
3. Replace `compile` with the default eager path (or install the C++ build tools) and fp16/bf16 with fp32 on CPU.
4. Use `torch.export` rather than `jit.trace` for new export code; install `onnx` + `onnxscript` for ONNX.
5. Pass `weights_only=True` unless you wrote the checkpoint yourself.
