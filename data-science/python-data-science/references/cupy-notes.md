---
description: "CuPy 14.2.0: install and import verified on a machine with no NVIDIA GPU (import succeeds, arrays fail), plus the NumPy-difference, benchmarking and memory-pool rules from its docs (source-read)"
source_repo: cupy/cupy (MIT)
tested_version: "PyPI wheel cupy-cuda13x 14.2.0 installed in a uv Python 3.14 venv on Windows 11 with NO NVIDIA GPU or CUDA toolkit (6 s, 109 MB site-packages); import and device queries run. Everything about kernel results, speed and memory behaviour is source-read from docs/source/user_guide/{difference,performance,memory}.rst on main, because no GPU was available. GPU timings for this repo's pipeline (from the other machine) are in economicspace-pipeline/references/defect-classes-and-traps.md"
verified_date: "2026-10-05"
---

# CuPy 14.2.0

CuPy is NumPy/SciPy on NVIDIA GPUs. Pick the wheel for the CUDA major version of the driver:
`cupy-cuda12x` and `cupy-cuda13x` both resolve to 14.2.0 on PyPI.

## On a machine with no GPU (run)

| Step | Result |
|---|---|
| `uv pip install cupy-cuda13x numpy` on Python 3.14 / Windows | succeeds in about 6 s; 109 MB of site-packages |
| `import cupy` | **succeeds** in 0.5 s, with two `UserWarning`s: `CUDA path could not be detected` and `Failed to detect number of GPUs: cudaErrorInsufficientDriver: CUDA driver version is insufficient for CUDA runtime version` |
| `cupy.cuda.is_available()` | `False` |
| `cupy.cuda.runtime.getDeviceCount()` and `cupy.arange(5)` | raise `CUDARuntimeError cudaErrorInsufficientDriver` |
| `cupy.show_config()` | prints `CUDA Driver Version : 0`, `CUDA Runtime Version : 13020 (linked to CuPy)`, and `DynamicLibNotFoundError` for cudart, nvrtc, curand, nvJitLink |

**Do not use `import cupy` as the GPU test.** It imports fine without a device. Use:

```python
try:
    import cupy as cp
    xp = cp if cp.cuda.is_available() else np
except ImportError:
    xp = np
```

and wrap the first real allocation too if a driver mismatch (like the one above) is possible. A missing toolkit shows as
`NVRTC unavailable`, which matters for `ElementwiseKernel`/`RawKernel` and JIT-compiled reductions.

## Differences from NumPy that change results (docs, source-read)

| Topic | CuPy behaviour |
|---|---|
| Float to integer casts | undefined in C++; docs' Intel-CPU example: NumPy `float32(-1).astype(uint32)` = 4294967295, CuPy 0; `inf -> int32`: NumPy -2147483648, CuPy 2147483647 |
| Out-of-bounds integer indices | NumPy raises `IndexError`; CuPy **wraps around** (`x[[1,3]] = 10` on a length-3 array sets index 0 as well) |
| Duplicate indices in `a[i] = v` | the stored value is **undefined** in CuPy (NumPy keeps the last) |
| Reductions (`cupy.sum`) | return **0-d cupy arrays**, not scalars, to avoid a GPU-CPU sync; cast with `float(...)`/`.item()` deliberately |
| ufunc arguments | only CuPy arrays or scalars: `cupy.power([cupy.arange(5)], 2)` raises `TypeError: Unsupported type <class 'list'>` |
| Implicit host conversion | not allowed; use `cupy.asnumpy(x)` / `x.get()` and `cupy.asarray(host)` |
| dtypes | numeric only (no str/object); minimal structured dtype support |
| `random` | accepts `dtype=`; array seeds are hashed to one number (less entropy than NumPy takes from an array seed) |
| `numpy.matrix` | not provided; sparse `*_matrix` results are plain arrays |

## Timing and memory (docs, source-read)

- GPU work is **asynchronous**: `time.perf_counter()` or `%timeit` around a CuPy call measures the launch, not the compute.
  Use `cupyx.profiler.benchmark(fn, args, n_repeat=20)` (CUDA events, warm-up included) or record events and
  `end.synchronize()`.
- First call in a process pays context creation (seconds) and per-dtype/shape kernel compilation; compiled kernels are cached
  under `~/.cupy/kernel_cache` (`CUPY_CACHE_DIR`). Warm up before timing and in CI.
- Device and pinned **memory pools** are on by default; freed blocks stay cached, so `nvidia-smi` shows memory in use after
  `del x`. Use `cupy.get_default_memory_pool().free_all_blocks()` (and the pinned pool) to release it; `cupyx.empty_pinned`
  and friends allocate pinned host arrays for faster transfers.
- Optional accelerators (CUB, cuTENSOR) speed some reductions/scans but "there could be exceptions": benchmark.
- FP64 throughput on consumer GPUs is a small fraction of FP32; this repo recorded a 7.6x slowdown versus CPU for a 40M-element
  fp64 `exp` on a TU102 card, and fp32 results are not bit-identical, which rules CuPy out for bit-identity pipelines.

## When it fits here

Large dense array maths on a machine with a supported NVIDIA GPU and a matching driver. Not for: bit-identical regression
pipelines (see above), Windows boxes without a GPU (use NumPy; keep the `xp` switch), or small arrays where transfer and
launch costs dominate.

Not run: any kernel, `cupyx.scipy`, FFT, sparse, memory-pool statistics, streams, DLPack interop, or an AMD/ROCm build.
