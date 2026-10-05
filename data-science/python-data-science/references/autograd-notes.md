---
description: "HIPS/autograd 1.9.1 on numpy 2.5: grad/jacobian/hessian usage, scipy.optimize integration, and the errors you hit (int input, non-scalar output, in-place assignment, sqrt at 0). Run live."
source_repo: HIPS/autograd (MIT)
tested_version: autograd 1.9.1, numpy 2.5.3, scipy 1.18.1, Python 3.14.6 on Windows; 20-line probe, outputs quoted below
verified_date: "2026-10-05"
---

# autograd: automatic differentiation of NumPy code

Differentiates native Python plus NumPy: loops, `if`, recursion, closures, higher-order derivatives, reverse mode (gradients of scalar functions)
and forward mode. Use it for gradient-based optimisation of NumPy-style models, checking hand-derived gradients, and sensitivity of small simulations.
It is a small, pure-Python library; for GPU, JIT compilation or large models the same authors' successor is JAX (`jax` 0.11.2 on PyPI at the time of checking; not tested here).
`autograd` exposes no `__version__`; read it from pip metadata (1.9.1).

```python
import autograd.numpy as np                     # thin wrapper: use THIS numpy inside differentiated code
from autograd import grad, value_and_grad, jacobian, hessian, elementwise_grad, hessian_vector_product
from autograd.test_util import check_grads
```

## What worked (all executed)

| Call | Result |
|---|---|
| `grad(lambda x: np.sum(np.sin(x)**2))(x0)` for `x0 = [0.3, 1.2, -0.7]` | `[0.5646, 0.6755, -0.9854]`, equal to `2 sin(x) cos(x)` |
| `value_and_grad(f)(x0)` | `(1.37104..., gradient)` in one pass; pass it to SciPy as `minimize(value_and_grad(f), x0, jac=True, method="BFGS")` (Rosenbrock from `[-1.2, 1.0]` converged to `[1, 1]` in 32 iterations) |
| `jacobian(g)(x0)` for a 2-vector function of 3 inputs | shape `(2, 3)` |
| `hessian(lambda x: np.sum(x**3))(x0)` diagonal | `[1.8, 7.2, -4.2]` (= 6x); `hessian_vector_product` agreed |
| `elementwise_grad(np.tanh)([0., 1.])` | `[1., 0.41997434]` |
| `grad(f, 1)(a, b)` (argnum) | derivative wrt the second argument: `12.0` for `a*b**2` at `(2, 3)` |
| Python loop with an `if` inside | differentiated correctly (`14.0` for the test function at 2.0) |
| `check_grads(f, modes=["rev"], order=2)(x0)` | passes: compares against finite differences, use it as a unit test for any new differentiable function |
| `float32` input | gradient dtype stays `float32` |
| plain `numpy` (not `autograd.numpy`) `sin`/`sum` inside the function | still gave the correct gradient `cos(x)` in this version; do not rely on it, import `autograd.numpy` (other functions may not dispatch) |

## Errors you will meet

| Situation | Error |
|---|---|
| `grad(lambda x: x**2)(3)` (Python int) | `TypeError: Can't differentiate w.r.t. type <class 'int'>`; pass `3.0` or a float array |
| `grad(lambda x: x*2)(array)` (non-scalar output) | `TypeError: Grad only applies to real scalar-output functions. Try jacobian, elementwise_grad or holomorphic_grad.` |
| in-place assignment `y = np.zeros(3); y[0] = x[0]*2` | `ValueError: setting an array element with a sequence.` (misleading text). Build arrays functionally: `np.concatenate([...])`, `np.stack`, `np.where` (the concatenate version returned `[2, 0, 0]`) |
| `grad(np.sqrt)(0.0)` | `ZeroDivisionError: zero to a negative power` (not `inf`/`nan`) |

The `sqrt` case is the general "derivative undefined at a branch point" problem. The standard guard is the **double-where** trick:
`np.where(x > 0, np.sqrt(np.where(x > 0, x, 1.0)), 0.0)` returned a gradient of `0.0` at `x = 0` instead of raising. A single `where` is not enough, because the unselected branch is still differentiated.

## Practical rules

- One scalar objective, many parameters: reverse mode (`grad`) costs about one extra function evaluation regardless of parameter count; many outputs of few inputs, use `jacobian` or forward mode.
- Keep the differentiated function pure: no in-place writes, no mutation of arguments, no side-effect state.
- Gradient-check anything new with `check_grads` before trusting an optimiser run; compare orbital or physical code to a finite-difference reference.
- For constrained or mixed-integer problems use `optimization-modeling-pyomo`; autograd gives derivatives, not solvers. For astrodynamics sensitivities the JAX-based `OpenSCvx` (`astro-toolkit-selection/references/openscvx-patterns.md`) is the JAX route.
