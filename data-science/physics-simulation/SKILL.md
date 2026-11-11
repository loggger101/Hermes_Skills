---
name: physics-simulation
description: "MuJoCo physics sim: install split, determinism, API traps."
version: 0.1.0
author: Hermes Agent (mined from starred repos, 2026-11-11)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [physics-simulation, mujoco, rl-environments, mjcf, contact-dynamics]
    related_skills: [bit-identity-float-pipelines, python-numerics-gotchas, evolutionary-ml]
---

# Physics Simulation (MuJoCo)

Load when running contact dynamics from Python — MuJoCo installs, MJCF models, headless rendering, RL rollout
reproducibility — or when a simulation result looks suspiciously convenient. Every number below was measured on
this machine (Windows, mujoco 4.0.0, Python 3.14); re-measure before quoting for another version.

## What This Skill Does

Run MuJoCo from Python on Windows for simulation, RL environments and contact-dynamics checks, with the packaging,
API and fixture traps that cost real debugging time recorded as measured facts.

## When to Use

- You need fast contact dynamics (manipulation, locomotion, drop/settle tests) behind a Python API.
- An RL or optimisation loop needs thousands of physics steps per second and reproducible rollouts.
- A pipeline must render state headlessly (no display) into images for reports or vision models.

## Install: the PyPI name is a shim, not the engine

`pip install mujoco` resolves to three distributions pinned to each other exactly — `mujoco==4.0.0` (a
`py3-none-any` wheel containing **no** native libraries), `mujoco-core==4.0.0` and `mujoco-studio==4.0.0`. The
core/studio wheels drop `.pyd`s and `mujoco.dll` into the *same* `site-packages/mujoco/` directory, so **three
distributions share one import namespace**: you still write `import mujoco`.

- Consequence for tooling: a registry probe that asks "does `mujoco` ship Windows wheels?" against PyPI JSON sees
  only the shim's two files and answers **no**. MuJoCo absolutely works on Windows — check `mujoco-core` /
  `mujoco-studio`, which publish cp311-cp314 plus free-threaded `cp314t` win_amd64 wheels (~260-320 MB per release
  across platforms). Older line (<=3.9.0) shipped ~26 platform-tagged files under the single name.
- Requires Python >=3.11 on this version line; measured working here on **Python 3.14**.

## Measured behaviour (Windows, mujoco 4.0.0, py3.14)

| Check | Result |
|---|---|
| Defaults when unspecified | `opt.timestep = 0.002`, integrator enum 0 (Euler), gravity `(0, 0, -9.81)` |
| Settle correctness | box on plane: `ncon=4` contacts; summed contact normal forces **9.8100 N** vs weight 9.8100 N |
| Throughput | 1500 steps of a 2-body scene in ~7 ms wall (3.0 s sim time) — hundreds x realtime, single thread |
| Determinism | same model + same step count twice -> identical sha256 over `qpos`+`qvel`. Bit-reproducible rollouts |
| Headless rendering | `Renderer(m, height=64, width=64)` then `update_scene/render` -> `(64, 64, 3) uint8`, **no display needed** on Windows |

Determinism is the property most worth knowing for agent work: a rollout can be hashed and compared exactly (see
`bit-identity-float-pipelines`) instead of being checked with tolerances. It held single-threaded here; treat
multi-threaded or `mjx`/GPU paths as a different claim that needs re-measuring.

## API traps found by probing (not from docs)

- **Contact force is not an attribute.** `MjContact` has no field containing "force" (`AttributeError`). The real
  call is per-contact and takes a shaped out-array — signature read straight off the TypeError:
  `mujoco.mj_contactForce(model, data, id, result)` where `result` is a writeable float64 `[6, 1]`. Loop over
  `range(data.ncon)`; pass one array per contact.
- **Bad MJCF raises `ValueError`** with text like `XML Error: Schema violation: unrecognized element ... line N` —
  catch it as ValueError (not a parse error class) when validating user-supplied models.
- **`mujoco.mjx` does not exist without JAX**: importing it gives `ModuleNotFoundError: No module named
  'mujoco.mjx'`. GPU-batched simulation is a *JAX* install decision, and the error reads like MuJoCo is broken.
- The `rollout` helper surface was **absent** from this wheel (`hasattr(mujoco, "rollout") == False`) — do not
  write batched-env code against it without checking in your own environment first.

## Fixture trap: a probe model that silently never moves

A hinge whose axis is **parallel** to the body-offset direction produces zero torque and no motion — correct
physics, but it looks exactly like "the install is broken". Measured pair:

- capsule `fromto="0 0 0 0 -0.5 0"` (offset along y) with `<joint axis="0 1 0">`: `qacc[0] = +0.0000`, angle
  unchanged after 500 steps.
- same capsule offset along x (`fromto="0 0 0 0.4 0 0"`), axis still y: `qacc[0] = +29.2869 rad/s^2`, swinging.

When validating a new MuJoCo install, use an offset perpendicular to the joint axis and assert on motion (or
`mj_contactForce` summing to weight), never merely on "no exception" — a degenerate model passes silently.

## Control-loop shape for RL code

An `<actuator><motor joint gear ctrlrange="-5 5"/></actuator>` gives `nu=1`; drive it with `data.ctrl[0]` before
`mj_step`. Note the rate consequence: at the default `timestep=0.002`, one policy step per sim step is a **500 Hz**
controller — RL code normally wants several sim steps per action (`for _ in range(int(control_dt/model.opt.timestep))`)
so gains are not silently applied 10-100x more often than intended. `actuator_ctrlrange` is `(nu, 2)` and
`ctrl` outside the range is clamped.

## Pitfalls

- Judging wheel/platform support from the `mujoco` PyPI name alone (see Install). Wrong answer, twice over.
- Reading contact forces off `MjContact`, or expecting `mjx`/`rollout` to be present by default.
- Declaring a rollout reproducible without hashing state; and re-checking determinism if you move threads or GPU.
- Trusting "no exception" from a smoke test — use the perpendicular-offset fixture above.

## Verification

A pass means: model compiles, box settles with contact forces summing to within float error of total weight,
`Renderer(...).render()` returns `(H, W, 3)` without a display, and two identical runs hash equal. All four were
observed here on Windows/Python 3.14/mujoco 4.0.0 (2026-11-11); re-run rather than assuming they hold for other
versions or platforms.
