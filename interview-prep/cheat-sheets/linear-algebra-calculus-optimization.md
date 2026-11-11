---
layout: "week"
status: "approved"
version: "1.1.0"
last_reviewed: "2026-11-11"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "Linear algebra, calculus, and optimization interview cheat sheet"
description: "Shapes, rank, conditioning, eigendecomposition, SVD and PCA, derivatives, automatic differentiation, optimizers, constraints, regularization, and numerical stability."
summary: "Revise the mathematical contracts behind modern ML, from tensor shapes and conditioning through gradients, curvature, constrained optimization, regularization, and stable computation."
permalink: "/interview-prep/cheat-sheets/linear-algebra-calculus-optimization/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 9 · Linear algebra, calculus, and optimization"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 9 source-backed scope:** This approved page publishes the canonical interview sheet without altering its instructional body. It remains separate from the Week 1–20 learning assessments.

**Target roles:** Lead Data Scientist, Senior Data Scientist, Applied Scientist, ML Engineer, AI Engineer  
**Use:** mathematical-foundation, modeling, deep-learning, optimization, debugging, and system-design interviews  
**Interview rule:** connect every equation to shapes, assumptions, computation, and failure modes. The goal is not symbolic recall; it is explaining why an algorithm works, when it becomes unstable, and how you would diagnose it.

## 1. Thirty-second revision

- A vector is an ordered set of features; a matrix is a linear transformation or collection of vectors; a tensor generalizes arrays to more axes.
- Always state shapes. For `X ∈ R^(n×d)` and `w ∈ R^d`, `Xw ∈ R^n`; many implementation bugs are shape or broadcasting bugs.
- A dot product measures aligned magnitude; cosine similarity normalizes magnitude; a norm measures size; a distance must satisfy metric properties.
- Rank is the number of independent directions. Rank deficiency creates non-identifiability and unstable inverses.
- Eigenvectors preserve direction under a square transformation. Singular value decomposition works for any matrix and exposes rank, conditioning, and best low-rank approximations.
- A gradient gives the steepest local increase; the negative gradient is the steepest local decrease under the Euclidean norm.
- The Jacobian generalizes first derivatives for vector outputs; the Hessian captures local curvature for scalar outputs.
- Backpropagation is efficient reverse-mode automatic differentiation using the chain rule; it is not a separate optimization algorithm.
- Convexity makes every local minimum global, but most neural-network objectives are non-convex.
- Learning rate is often the most important optimizer setting. Divergence, oscillation, plateaus, and noisy validation require different diagnoses.
- Adam adapts step sizes using gradient moments; AdamW decouples weight decay from the adaptive update. Neither removes the need for schedules, validation, or regularization.
- Numerical stability is part of correctness: prefer log-sum-exp, stable softmax, factorizations/solvers instead of explicit inverses, scaled inputs, and appropriate precision.

## 2. Shapes, vectors, matrices, and tensors

Let a batch of `n` examples with `d` features be `X ∈ R^(n×d)`.

| Object | Typical shape | ML meaning |
|---|---:|---|
| scalar | `()` | loss, learning rate, temperature |
| vector | `(d,)` | one example, weights, embedding |
| matrix | `(n, d)` | tabular batch or token embeddings flattened by batch |
| 3-D tensor | `(b, t, h)` | batch, sequence length, hidden size |
| 4-D tensor | `(b, c, h, w)` | image batch in channel-first format |

For a linear layer:

`Z = XW + b`

If `X` is `(n, d_in)`, `W` is `(d_in, d_out)`, and `b` is `(d_out,)`, then `Z` is `(n, d_out)`. Broadcasting repeats `b` across rows without materializing copies. State which axes are broadcast; accidental broadcasting can silently produce a plausible but wrong result.

### Core operations

- Dot product: `x · y = Σ x_i y_i`
- Euclidean norm: `||x||₂ = sqrt(Σ x_i²)`
- L1 norm: `||x||₁ = Σ |x_i|`
- Cosine similarity: `(x · y) / (||x||₂ ||y||₂)`
- Matrix product: each output entry is a row-column dot product.
- Outer product: `xyᵀ` creates a matrix of pairwise products.
- Projection of `x` onto nonzero `u`: `proj_u(x) = (x · u / u · u)u`

Cosine ignores overall scale but is undefined for a zero vector. Euclidean distance is scale-sensitive. Standardize or otherwise choose a geometry consistent with the data and downstream objective.

## 3. Span, basis, rank, and linear systems

- **Span:** all linear combinations of a set of vectors.
- **Linear independence:** no vector is redundant as a combination of the others.
- **Basis:** an independent set spanning a space.
- **Rank:** dimension of the column space; equivalently the number of nonzero singular values under exact arithmetic.
- **Null space:** vectors mapped to zero by a matrix.

For `Ax = b`:

- a unique solution requires sufficient independent constraints;
- no exact solution occurs when `b` is outside the column space;
- infinitely many solutions occur when a nontrivial null space remains.

Least squares minimizes `||Ax − b||₂²`. The normal equation `AᵀAx = Aᵀb` is useful conceptually, but computing `(AᵀA)⁻¹Aᵀb` explicitly can worsen conditioning and numerical error. Prefer QR, SVD, or a library solver.

### Conditioning

The condition number is approximately `largest singular value / smallest nonzero singular value`. A large value means small input or rounding changes can cause large solution changes. Remedies include:

- rescaling features;
- removing redundant variables;
- regularization;
- higher precision where justified;
- stable decompositions rather than explicit inversion;
- collecting more informative data.

Regularization can make a computation stable while changing the estimand. Report that trade-off.

## 4. Eigenvalues, covariance, PCA, and SVD

For a square matrix `A`, an eigenpair satisfies:

`Av = λv`

The direction `v` is preserved and scaled by `λ`. For a symmetric positive-semidefinite matrix, eigenvalues are real and nonnegative. A covariance matrix is positive semidefinite because every projected variance is nonnegative.

Singular value decomposition:

`A = UΣVᵀ`

It works for rectangular matrices. The columns of `V` are input directions, singular values in `Σ` quantify strength, and columns of `U` are corresponding output directions.

Important consequences:

- numerical rank comes from singular values relative to a tolerance;
- the top `k` singular components form the best rank-`k` approximation under common matrix norms;
- pseudoinverses use reciprocal nonzero singular values;
- tiny singular values reveal ill-conditioned directions.

### PCA

For centered data, PCA finds orthogonal directions of maximum variance. It can be computed through eigen-decomposition of covariance or SVD of the centered data matrix.

Explained variance ratio for component `j`:

`λ_j / Σ λ_i`

PCA is linear and variance-driven. It does not guarantee class separation, causal factors, semantic meaning, or faithful preservation of small but important signals. Scaling determines which features dominate. Fit preprocessing and PCA on training data only.

## 5. Derivatives and automatic differentiation

For scalar `f(x)`:

- derivative: local rate of change;
- partial derivative: rate with respect to one coordinate;
- gradient `∇f`: vector of partial derivatives;
- directional derivative along unit vector `u`: `∇f · u`;
- Hessian `H`: matrix of second partial derivatives.

For vector function `g: R^d → R^m`, the Jacobian contains output-input partial derivatives. Be explicit about library layout conventions.

### Chain rule and backpropagation

If `y = f(g(x))`, then the derivative composes local derivatives. Neural networks are long compositions, so reverse-mode automatic differentiation reuses intermediate values to compute a scalar loss gradient with respect to many parameters efficiently.

Key distinctions:

- **forward pass:** compute outputs and record required operations/intermediates;
- **backward pass:** propagate vector-Jacobian products;
- **optimizer step:** use gradients to update parameters;
- **zeroing gradients:** prevent unwanted accumulation between steps.

Common failures:

- detached tensors or non-differentiable operations break the graph;
- in-place mutation can invalidate saved intermediates;
- gradients accumulate unexpectedly;
- saturation causes very small derivatives;
- deep multiplication can cause vanishing/exploding gradients;
- a correct gradient can still optimize the wrong objective.

### Gradient checking

For coordinate `i`, the centered finite-difference approximation is:

`[f(x + εe_i) − f(x − εe_i)] / (2ε)`

Compare this with the analytical gradient on a tiny deterministic example using double precision. Too-large `ε` causes truncation error; too-small `ε` causes cancellation/rounding error. Gradient checking is a debugging tool, not a training method.

## 6. Optimization mental model

An optimization problem specifies:

1. decision variables/parameters;
2. objective;
3. constraints;
4. data distribution or finite dataset;
5. evaluation and stopping criteria.

Gradient descent:

`θ_(t+1) = θ_t − η∇L(θ_t)`

The learning rate `η` controls step size.

| Observed behavior | Likely causes | First checks |
|---|---|---|
| loss becomes `NaN`/infinite | large steps, overflow, invalid log/division | inputs, loss numerics, LR, gradient norm |
| loss oscillates | LR too high, sharp curvature, noisy batches | LR range, batch statistics, clipping |
| train loss flat | LR too low, dead/saturated activations, graph issue | gradients, activations, optimizer parameters |
| train improves, validation worsens | overfit, leakage, shift, weak regularization | split, pipeline, capacity, early stopping |
| highly variable runs | seed/data order, small validation, nondeterminism | repeated runs and confidence intervals |

### Batch, stochastic, and mini-batch updates

- Full-batch gradients are deterministic for fixed data but expensive.
- Stochastic gradients update from one example and are noisy.
- Mini-batches exploit accelerators while retaining useful noise.

Noise can help exploration, but it also increases variance. Batch size changes optimization dynamics, memory, throughput, and the number of updates per epoch. Do not scale learning rate without testing.

### Momentum, Adam, and AdamW

- Momentum accumulates a velocity, reducing zig-zagging and accelerating persistent directions.
- Adam keeps exponential moving averages of gradients and squared gradients with bias correction.
- AdamW applies weight decay separately from the adaptive gradient update.

Use SGD with momentum when its inductive bias and final generalization are validated; AdamW is a strong practical default for many transformer-style workloads. Optimizer choice is empirical and workload-specific.

## 7. Convexity, curvature, and constraints

A differentiable function is convex when its graph lies below every chord; equivalently, first-order supporting-hyperplane conditions hold. For twice-differentiable functions, a positive-semidefinite Hessian everywhere implies convexity.

Convex optimization advantages:

- any local minimum is global;
- optimality conditions are more informative;
- mature solvers can provide certificates or tight diagnostics.

Deep networks are non-convex. Practitioners therefore use initialization, normalization, residual connections, schedules, regularization, stochasticity, and repeated evaluation rather than expecting a global certificate.

### Second-order information

Newton's method uses inverse Hessian curvature to scale a step. It can converge quickly near a suitable optimum but is expensive and may move badly under indefinite curvature. Quasi-Newton methods such as BFGS/L-BFGS approximate curvature without storing a full Hessian.

### Constrained optimization

For equality constraint `g(θ)=0`, a Lagrangian is:

`L(θ, λ) = f(θ) + λg(θ)`

Karush-Kuhn-Tucker conditions extend this idea to inequalities under regularity assumptions. In interviews, explain feasibility, complementary slackness, and why conditions may be necessary rather than sufficient in non-convex problems.

Practical constraint strategies include projection, penalty/barrier methods, reparameterization, and specialized solvers. A penalty coefficient creates a trade-off; it does not guarantee exact feasibility.

## 8. Regularization and generalization

| Technique | Training effect | Important caveat |
|---|---|---|
| L2 penalty/weight decay | discourages large weights | adaptive optimizers make coupling details matter |
| L1 penalty | encourages sparsity | correlated features make selection unstable |
| dropout | noisy subnetworks during training | disabled or rescaled appropriately at inference |
| early stopping | limits optimization on training set | validation reuse can overfit decisions |
| data augmentation | encodes invariances | invalid transforms corrupt labels |
| label smoothing | softens confidence targets | can affect calibration and rare classes |
| normalization | improves scale/optimization behavior | train/eval state and small batches matter |

Regularization should be chosen against a held-out objective and operational constraints, not by tradition.

## 9. Numerical stability and precision

For logits `z`, stable softmax subtracts `max(z)` before exponentiation:

`softmax_i(z) = exp(z_i − m) / Σ exp(z_j − m)`

The stable log-sum-exp identity is:

`log Σ exp(z_i) = m + log Σ exp(z_i − m)`

Other practices:

- clip probabilities only when the objective's intended numerical contract justifies it;
- use fused cross-entropy-with-logits routines;
- avoid subtracting nearly equal large numbers;
- monitor finite values and gradient norms;
- accumulate sensitive reductions in adequate precision;
- use automatic mixed precision with scaling and overflow checks;
- recognize that floating-point operations are not associative.

Reproducibility is bounded: seeds help, but parallel reductions, hardware, kernels, and library versions may still change results.

## 10. Minimal dependency-free example: stable softmax

```python
from __future__ import annotations

from math import exp, isclose
from typing import Sequence


def stable_softmax(logits: Sequence[float]) -> list[float]:
    """Return stable softmax probabilities for a non-empty finite sequence."""
    if not logits:
        raise ValueError("logits must not be empty")

    maximum = max(logits)
    shifted = [exp(value - maximum) for value in logits]
    denominator = sum(shifted)
    if denominator == 0.0:
        raise ArithmeticError("softmax denominator underflowed to zero")
    return [value / denominator for value in shifted]


probabilities = stable_softmax([1000.0, 1001.0, 1002.0])
assert isclose(sum(probabilities), 1.0, rel_tol=0.0, abs_tol=1e-12)
assert probabilities[2] > probabilities[1] > probabilities[0]
assert stable_softmax([5.0, 5.0]) == [0.5, 0.5]
```

Production code should use the framework's fused, tested routines. This example demonstrates the stability transformation.

## 11. Library and solver map

| Tool | Use it for | Verify before production |
|---|---|---|
| NumPy | dense array operations and linear algebra | shapes, dtype, copies/views, solver choice |
| SciPy | sparse/dense solvers and optimization | convergence flags, bounds, tolerances, scaling |
| PyTorch | tensors, reverse-mode autograd, neural optimization | train/eval modes, device/dtype, gradient flow |
| JAX | composable transformations, autodiff, compilation | purity/static-shape constraints and compilation behavior |
| CVXPY | modeling disciplined convex programs | problem class, solver support, status/certificates |
| OR-Tools | discrete, routing, and constraint optimization | optimality gap, time limits, business constraints |

Do not claim “the solver succeeded” from the absence of an exception. Read the termination status, residuals, feasibility, objective gap, iteration limit, and sensitivity.

## 12. Rapid interview questions

**Why avoid a matrix inverse?**  
Solving a system through QR, Cholesky, SVD, or another suitable factorization is typically more stable and efficient than forming an inverse.

**Eigen-decomposition versus SVD?**  
Eigen-decomposition applies to square matrices and may involve complex values. SVD applies to any matrix and directly exposes singular directions, rank, and conditioning.

**Why does feature scaling affect gradient descent?**  
Unequal scales create elongated loss contours; one learning rate then overshoots steep directions or crawls along flat ones.

**What does a zero gradient mean?**  
It may be a minimum, maximum, saddle, flat/saturated region, non-differentiable convention, or graph bug. Inspect loss, curvature/perturbations, and gradient flow.

**Why can cosine and Euclidean nearest neighbors disagree?**  
Cosine uses angle while Euclidean uses angle and magnitude. Normalizing vectors makes their rankings more closely related.

**What is exploding-gradient clipping doing?**  
It bounds update-driving gradient magnitude. It can stabilize training but may hide a bad learning rate, architecture, data scale, or loss.

**Does Adam always converge faster or generalize better?**  
No. It often reaches useful loss quickly, but results depend on objective, schedule, regularization, and workload.

**Why is an ill-conditioned problem risky?**  
Small data or rounding changes can cause large parameter changes, producing unstable estimates and unreliable extrapolation.

## 13. Lead-level case: training diverges after a larger rollout

Structure the answer:

1. Freeze the exact data snapshot, code, config, seed, container, and hardware metadata.
2. Compare old/new data schemas, feature ranges, missingness, duplicates, labels, sampling, and batch composition.
3. Reproduce on a minimal deterministic slice; assert finite inputs, logits, losses, and gradients.
4. Log per-layer activation/gradient norms and the first failing step.
5. Check mixed-precision scaling, optimizer state restoration, schedule position, effective batch size, gradient accumulation, and distributed reduction.
6. Run an LR range reduction and full-precision control; temporarily disable questionable augmentations or fused kernels.
7. Verify the objective and labels, not only mechanics.
8. Fix the root cause, add a regression test and numerical guardrail, rerun repeated-seed evaluation, then stage the rollout.

The lead answer connects mathematics to reproducible operations and prevents recurrence.

## 14. Final checklist

- [ ] I state tensor shapes and broadcasting axes.
- [ ] I can explain norms, cosine, projections, rank, and conditioning.
- [ ] I distinguish eigen-decomposition, SVD, and PCA.
- [ ] I explain gradient, Jacobian, Hessian, chain rule, and reverse-mode autodiff.
- [ ] I can diagnose divergence, oscillation, plateaus, and overfitting.
- [ ] I distinguish SGD, momentum, Adam, and AdamW without claiming a universal winner.
- [ ] I understand convexity, constraints, solver status, and optimization gaps.
- [ ] I use stable softmax/log-sum-exp and avoid explicit inverses.
- [ ] I connect regularization and precision choices to validation evidence.
- [ ] I can turn a numerical failure into a reproducible debugging plan.

## 15. Primary references

- [PyTorch automatic differentiation documentation](https://docs.pytorch.org/docs/stable/autograd.html)
- [PyTorch autograd mechanics](https://docs.pytorch.org/docs/stable/notes/autograd.html)
- [PyTorch numerical accuracy notes](https://docs.pytorch.org/docs/stable/notes/numerical_accuracy.html)
- [PyTorch AdamW documentation](https://docs.pytorch.org/docs/stable/generated/torch.optim.AdamW.html)
- [NumPy linear algebra documentation](https://numpy.org/doc/stable/reference/routines.linalg.html)
- [SciPy optimization documentation](https://docs.scipy.org/doc/scipy/reference/optimize.html)
- [JAX automatic differentiation guide](https://docs.jax.dev/en/latest/automatic-differentiation.html)
- [CVXPY disciplined convex programming tutorial](https://www.cvxpy.org/tutorial/dcp/)
- [Boyd and Vandenberghe, Convex Optimization](https://web.stanford.edu/~boyd/cvxbook/)
- [scikit-learn PCA documentation](https://scikit-learn.org/stable/modules/decomposition.html#pca)
