---
name: model-export-deploy
description: "Model export: ONNX, TorchScript, HDF5, NumPy, JSON."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [model-export, ONNX, TorchScript, serialization, model-versioning, deployment, HDF5, NumPy, JSON]
    category: data-science
    related_skills: [python-craft, evolutionary-ml]

---

# Model Export and Deployment

Guide for exporting trained models out of the training pipeline and into something that can be loaded, versioned, and run elsewhere. Covers formats, what to export with them, validation on load, versioning, and the common failure modes that only show up after the model leaves the training code.


## What This Skill Does

Model export: ONNX, TorchScript, HDF5, NumPy, JSON.

## When to Use

- Exporting a trained model for inference in a different environment (serving, edge, another language)
- Packaging a model with its config so it can be reproduced
- Versioning models so you can tell which code produced which artifact
- Loading an exported model and trusting that it behaves the same as it did in training

**Don't use** this for "how do I serve this at scale" — that's infrastructure (serving stack, batching, GPU provisioning). This is the artifact boundary: what you write out, how you validate it, and how you version it.

## What to Export

A model export is not just weights. It's weights + the information needed to run them correctly. At minimum:

- **Weights / parameters** — the genome, the state dict, the weight matrices.
- **Architecture** — enough to reconstruct the network topology, layer sizes, activation functions, input/output shapes.
- **Config** — any parameters the model depends on that aren't in the weights (binning thresholds, feature indices, scaling params, opponent config, etc.).
- **Metadata** — what produced this export (code version, training run ID, generation/epoch, fitness/ELO, date, random seed).

If any of these is missing, the export is fragile — someone loading it later has to guess or reconstruct what they're missing.

## Format Selection

### NumPy `.npy` / `.npz`

Good for: flat weight vectors, arrays, genomes that are just a list of floats. Simple, fast, universally readable.

```python
import numpy as np

# Flat genome
np.save("agent_genome.npy", genome)              # .npy, single array
np.savez("agent.npz", genome=genome, config=config_dict)   # .npz, multiple arrays + scalars

# Load
genome = np.load("agent_genome.npy")
data = np.load("agent.npz")
genome = data["genome"]
```

- `.npy` is one array. `.npz` is a zip of named arrays — use it when you have multiple arrays or want to bundle scalars alongside.
- NumPy format is stable and versioned; old files load in new NumPy.
- For a genome that's a flat vector, `.npy` is the right choice. For a structured genome (multiple arrays, metadata), `.npz` or a directory of files is better.

### PyTorch `state_dict` + `torch.save`

Good for: PyTorch models where you want to preserve the exact parameter tensors and reload into the same architecture.

```python
# Save
torch.save({
    "model_state_dict": model.state_dict(),
    "config": config,
    "metadata": {"run_id": run_id, "generation": gen, "fitness": fitness},
}, "model_checkpoint.pt")

# Load
checkpoint = torch.load("model_checkpoint.pt", weights_only=False)
model = build_model(checkpoint["config"])
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()
```

- `weights_only=False` is needed when the checkpoint contains non-tensor objects (config dicts, metadata). Security-conscious loading uses `weights_only=True` for pure tensor loads, but then you can't load arbitrary objects — which is the point.
- `state_dict` is an ordered dict of parameter tensors — it's tied to the module's parameter names. Loading it into a differently-structured model fails. That's good — it means the export is architecture-specific and you can't silently misload.

### TorchScript

Good for: deploying a PyTorch model in environments without the full training code, or where you want a serialized, runnable representation.

```python
# Trace (requires an example input; works for static graphs)
example_input = torch.randn(1, input_size)
traced = torch.jit.trace(model, example_input)
traced.save("model_traced.pt")

# Script (works for dynamic control flow; no example needed)
scripted = torch.jit.script(model)
scripted.save("model_scripted.pt")

# Load
loaded = torch.jit.load("model_traced.pt")
loaded.eval()
output = loaded(example_input)
```

- **Trace** records the operations performed for one example input. It doesn't capture dynamic control flow (if the model behaves differently for different inputs, tracing may bake in the wrong path). Use trace for simple feedforward; use script for anything with conditionals or loops.
- **Script** compiles the model's Python into TorchScript IR. Handles control flow, but can fail on Python features TorchScript doesn't support (some builtins, complex Python idioms).
- TorchScript files are self-contained runnable models — they include the architecture and weights. Loading them doesn't require the original class definition, which is the main advantage over `state_dict`.

### ONNX

Good for: cross-platform deployment, inference in non-Python environments (C++, Rust, Go, mobile, web), or serving with an ONNX runtime.

```python
torch.onnx.export(
    model,
    example_input,
    "model.onnx",
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={"input": {0: "batch"}, "output": {0: "batch"}},
    opset_version=17,
    verbose=False,
)
```

- ONNX is a graph format — it captures the computation, not the Python. Loading it doesn't require PyTorch.
- `dynamic_axes` lets you mark which dimensions are variable (batch size is the common one). Without it, the model is fixed to the example input shape.
- `opset_version` controls the operator set. Newer opsets support more operators; pick one compatible with your target runtime.
- Validate the ONNX export by running the same input through the original PyTorch model and the ONNX model and comparing outputs.

### HDF5

Good for: large models, layered data, when you want a single file with named datasets and metadata. Common in scientific computing.

```python
import h5py

with h5py.File("model.h5", "w") as f:
    f.attrs["run_id"] = run_id
    f.attrs["generation"] = gen
    f.attrs["fitness"] = fitness
    f.create_dataset("genome", data=genome)
    f.create_dataset("config_json", data=json.dumps(config))

# Load
with h5py.File("model.h5", "r") as f:
    run_id = f.attrs["run_id"]
    genome = f["genome"][:]
    config = json.loads(f["config_json"][()].decode())
```

- HDF5 supports hierarchical datasets, compression, and large files. Good when the model is big or has a complex structure.
- Downsides: requires `h5py`, and HDF5 files can be opaque to version control (binary, not diffable).

### JSON

Good for: small models, genomes that are lists of numbers, config-only exports, or when you need a human-readable, version-control-friendly format.

```python
export = {
    "version": 1,
    "genome": genome.tolist(),
    "config": config,
    "metadata": {"run_id": run_id, "fitness": fitness, "date": date.isoformat()},
}
with open("model.json", "w") as f:
    json.dump(export, f, indent=2)
```

- JSON is diffable, human-readable, and universally parseable. Great for genomes that fit comfortably as a list of floats.
- Bad for large models (text representation is bulky, parsing is slow). Don't JSON-serialize a 100MB weight matrix.

### Pickle

Good for: Python-to-Python transfer of arbitrary objects when you control both ends and trust the source.

- **Pitfall**: pickle is tied to the class definitions at load time. If the class changes, unpickling can break or silently misbehave. It's also a security risk — unpickling untrusted data can execute arbitrary code. Don't unpickle data from an untrusted source.
- Prefer explicit formats (NumPy, state_dict, JSON) over pickle when the export needs to outlive the training code or be loaded by something other than the exact same Python environment.

## Validation on Load

An export that loads without error is not necessarily correct. Validate after loading.

### Shape validation

```python
def load_genome(path: str, expected_size: int) -> np.ndarray:
    genome = np.load(path)
    if genome.shape != (expected_size,):
        raise ValueError(f"Genome size mismatch: {genome.shape} vs expected ({expected_size},)")
    return genome
```

Reject by shape. A genome file that's the wrong length is corrupted or from a different model — don't load it silently and hope.

### Output comparison (for ONNX, TorchScript)

```python
def validate_export(export_path, test_input, reference_model, atol=1e-5):
    reference_output = reference_model(test_input).detach().numpy()
    exported_output = run_exported(export_path, test_input)   # ONNX runtime, TorchScript load, etc.
    if not np.allclose(reference_output, exported_output, atol=atol):
        raise ValueError(f"Export mismatch: max diff {np.abs(reference_output - exported_output).max()}")
```

Run a few test inputs through both and compare. For floating point, use `np.allclose` with a tolerance, not exact equality.

### Behavioral validation (for evolved agents)

For evolved policies, the right validation is behavioral, not just output-matching:

- Load the exported genome.
- Run it in the same environment with the same seeds.
- Compare the action sequence to the training-time agent's actions.
- If they diverge, something in the export/load path changed the policy.

This catches issues that output-comparison on a single input misses — e.g., a loading bug that permutes the weight order, or a config parameter that changed the feature computation.

## Versioning

### What to version

- **Code version** — what code produced this model. A git commit SHA, a release tag, or a `pipeline_version` string.
- **Model version** — a version for the model itself, independent of code. Increment when the model's behavior or structure changes.
- **Config version** — if the config schema changes, old configs may not be loadable by new code. Version the config format.

### How to version

- Stamp the version into the export metadata.
- Don't rely on filenames alone for versioning (e.g., `model_v3.pt`) — filenames drift from reality. Metadata is the source of truth.
- Keep a mapping somewhere (a registry file, a database, a meta-json) that records which model version is which — what code, what run, what fitness.

### Example metadata block

```json
{
  "model_version": "1.2.0",
  "code_version": "git:91f2763",
  "run_id": "run_20260815_022753",
  "generation": 150,
  "fitness": 1.32,
  "elo": 1280,
  "config": {"pop_size": 200, "mutation_rate": 0.1, ...},
  "exported_by": "train.py:exporter",
  "exported_at": "2026-08-15T02:27:53"
}
```

## Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Export only weights, no config | Loaded model runs but produces wrong results (feature computation changed, etc.) | Export config alongside weights; validate config is loadable |
| Load without shape validation | Wrong-size genome loads silently, produces garbage or crashes later | Validate shape/size on load; reject mismatches |
| TorchScript trace captures wrong path | Model works for the example input but fails for others | Use `torch.jit.script` for dynamic models, or validate trace against multiple inputs |
| ONNX export misses dynamic axes | Model only runs for the exact batch size used at export | Set `dynamic_axes` for variable dimensions |
| Pickle from old code loaded by new code | Unpickling breaks or silently misbehaves | Prefer explicit formats; if using pickle, version the class and test loading old pickles after changes |
| Metadata missing or in filename only | Can't tell which code produced which model | Stamp metadata inside the file; keep a registry |
| Export/load path changes the policy (evolved agents) | Loaded agent behaves differently from training agent | Behavioral validation: run both in the same env with same seeds, compare action sequences |
| Large model in JSON | Bloated file, slow parse | Use NumPy/.npy/.npz/HDF5 for large arrays; JSON only for small genomes or config |
| No validation after export | Export looks fine until it's loaded in production and fails | Validate exports as part of the export step — shape check, output comparison, behavioral check |

## Verification Checklist

Before treating an export as ready:

- [ ] Export includes weights + architecture + config + metadata
- [ ] Load function validates shape/size and rejects mismatches
- [ ] Output comparison passes (for ONNX, TorchScript, state_dict reloads)
- [ ] Behavioral validation passes for evolved agents (same actions in same env)
- [ ] Metadata includes code version, model version, and what produced it
- [ ] Export is loadable by the intended consumer (same Python env, ONNX runtime, etc.)
- [ ] Old exports still load after code changes (backward compatibility tested, or breakage documented)
- [ ] File size is reasonable for the format (no 100MB JSON, no uncompressed huge arrays when compression is available)
