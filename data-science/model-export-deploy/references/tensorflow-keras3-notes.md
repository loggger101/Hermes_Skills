---
description: "TensorFlow 2.21.0 + Keras 3.15.1 on Windows: no Python 3.14 wheel, CPU-only, model.save('.keras'/'.h5') works while SavedModel needs model.export(), dtype strictness, tf.function retracing, noisy stderr"
source_repo: tensorflow/tensorflow (Apache-2.0)
tested_version: "tensorflow 2.21.0 (PyPI 2026-03-06) in a uv Python 3.12.14 venv on Windows 11 (install 30 s, 351 MB wheel, 1.6 GB site-packages, no NVIDIA GPU); Keras 3.15.1, numpy 2.5.3; one script of about 25 checks. Python 3.14 availability checked with pip --python-version. GPU training, distributed strategies, TFLite and tf.data were not exercised"
verified_date: "2026-10-05"
---

# TensorFlow 2.21 / Keras 3 on a Windows dev box

## Installability (run)

| Question | Answer |
|---|---|
| Python versions with a Windows wheel | **3.10, 3.11, 3.12, 3.13**. `pip index versions tensorflow --python-version 3.14 --platform win_amd64` finds **no matching distribution**: on a default Python 3.14 this machine cannot install TensorFlow at all. Create a 3.12 or 3.13 environment (`uv venv --python 3.12`) |
| Size | win_amd64 wheel 351 MB (Linux x86_64 573 MB, macOS arm64 223 MB); 1.6 GB of site-packages after install; `import tensorflow` took 6.5 s |
| GPU | **none on native Windows**: TensorFlow logs `GPU support is not available on native Windows for TensorFlow >= 2.11 ... Please use WSL2 or the TensorFlow-DirectML plugin`; `list_physical_devices('GPU') == []`, `is_built_with_cuda() == False` |
| Keras | `tf.keras` is **Keras 3** (3.15.1 here) |

## Save and export formats (run)

| Call | Result |
|---|---|
| `model.save('m.keras')` | saved (native format); `load_model` round trip gave identical predictions (max diff 0.0) |
| `model.save('m.h5')` | saved (legacy HDF5) |
| `model.save('m_savedmodel')` (directory, no extension) | **`ValueError: Invalid filepath extension for saving`** (needs `.keras` or `.h5`) |
| `model.export('dir')` | writes a **SavedModel** for serving, endpoint `serve`, input `TensorSpec(shape=(None, 4), float32)` |
| `tf.keras.models.load_model('<SavedModel dir>')` | **`ValueError: File format not supported`**: a SavedModel from `export()` loads with `tf.saved_model.load`, not `load_model` |

Both saves emitted a numpy-2 warning (`__array__ implementation doesn't accept a copy keyword`). Pattern for deployment:
`.keras` for checkpoint/resume, `model.export()` for serving, ONNX or TFLite conversion from the exported artifact (conversion tools were not run here).

## Behaviour that bites

| Case | Result |
|---|---|
| `tf.constant([1,2,3])` dtype / `tf.constant([1.0])` / `tf.constant(np.array([1.0]))` | `int32` / `float32` / **`float64`** (numpy defaults are preserved) |
| `int32 tensor + float32 tensor`, and `int32 tensor + 1.5` | **`InvalidArgumentError: cannot compute AddV2 as input #1 was expected to be a int32 tensor but is a float tensor`**: no implicit promotion; cast explicitly |
| `tf.random.set_seed(1)` twice | identical draws; without re-seeding successive draws differ |
| `@tf.function` called with 5 different Python ints | **5 traces** plus a `retracing` warning; with 5 `tf.constant` values, 1 more trace in total. Pass tensors, or use `input_signature` |
| `tensor == numpy_array` | elementwise tensor `[True, True]`; `np.array(tensor)` works |
| Threads | `intra/inter_op_parallelism_threads` report `0` (TensorFlow picks) |

## stderr noise and reproducibility

At import TensorFlow prints (stderr, not stdout): an absl `All log messages before absl::InitializeLog()` warning, a
**oneDNN custom operations are on ... slightly different numerical results due to floating-point round-off** line, and a CPU
feature note (here `AVX2 AVX_VNNI FMA`). Silence with `TF_CPP_MIN_LOG_LEVEL=2`; for run-to-run bit-comparisons set
`TF_ENABLE_ONEDNN_OPTS=0` (not measured here) and seed with `tf.keras.utils.set_random_seed`. This repo's bit-identity pipelines
should not use TensorFlow numerics as a reference.

Not run: GPU/WSL2, `tf.data`, distribution strategies, TFLite/ONNX conversion, mixed precision, `tf_keras` (the legacy Keras 2 package).
