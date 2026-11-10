---
layout: "week"
status: "approved"
version: "1.0.0"
last_reviewed: "2026-11-10"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "Linear algebra, calculus, and optimization interview cheat sheet"
description: "Shapes, vector geometry, rank, projections, eigendecomposition, SVD, PCA, gradients, backpropagation, optimizers, regularization, constraints, and numerical stability."
summary: "Revise mathematical objects through their shapes, meaning, assumptions, optimization behavior, numerical consequences, and production evidence."
permalink: "/interview-prep/cheat-sheets/linear-algebra-calculus-optimization/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 7 · Mathematics and optimization"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 7 source:** This page integrates the newly prepared revision source into the Prep site. It is separate from the Week 1–20 learning assessments.

**Target roles:** AI Engineer, ML Engineer, Data Scientist, Applied Scientist, AI/Data Science Lead  
**Use:** mathematical-foundations, model-training, embeddings, optimization, and system-design rounds  
**Interview rule:** connect every mathematical object to its shape, meaning, assumption, and computational consequence. A formula without those four pieces is not yet an engineering answer.

## 1. Thirty-second revision

- A scalar has no axis, a vector has one, a matrix has two, and a tensor generalizes to more axes. State shapes before manipulating them.
- Broadcasting expands compatible singleton dimensions conceptually; it can also hide a wrong batch, feature, or sequence axis.
- A dot product measures aligned magnitude. Cosine similarity removes magnitude but is not automatically the right business similarity.
- Matrix rank is the number of independent directions. Low rank means redundancy and enables compression or latent-factor models.
- Projection finds the closest point in a subspace under a chosen geometry. Orthogonality makes coefficients and errors easier to reason about.
- Eigenvectors preserve direction under a linear map. Singular vectors exist for any rectangular matrix and power PCA, low-rank approximation, and conditioning analysis.
- A gradient gives the direction of steepest local increase; gradient descent moves against it. The learning rate controls the step, not the objective.
- Backpropagation is repeated chain rule with cached intermediate values; automatic differentiation does not fix a wrong computation graph or loss.
- Convexity gives global structure, but most deep-learning objectives are non-convex. Stable optimization still depends on scale, initialization, curvature, noise, and schedules.
- L1 encourages sparsity; L2 shrinks weights smoothly; AdamW decouples weight decay from the adaptive gradient update.
- Numerical stability is part of correctness: use log-sum-exp, stable softmax, clipping where justified, normalized inputs, and appropriate precision.

## 2. Shapes, axes, and broadcasting

For a batch of `B` sequences, length `T`, hidden width `D`, a transformer activation commonly has shape `(B, T, D)`. A linear layer with weight `(D, H)` produces `(B, T, H)`.

Matrix multiplication requires matching inner dimensions:

$$
A_{m\times n}B_{n\times p}=C_{m\times p}
$$

Elementwise operations require equal shapes or broadcast-compatible trailing dimensions. For dimensions compared from the right, values must be equal or one must be `1`.

Interview habit:

1. name every axis;
2. write input and parameter shapes;
3. distinguish elementwise multiplication from matrix multiplication;
4. check the output shape;
5. ask whether broadcasting is intended.

An accidental `(B, 1)` target against `(B, T, 1)` predictions may silently repeat labels across time. Shape-valid does not mean semantically valid.

## 3. Vectors, inner products, norms, and distance

For vectors $x,y\in\mathbb{R}^d$:

$$
x^\top y=\sum_i x_i y_i
$$

Common norms:

$$
\lVert x\rVert_1=\sum_i |x_i|,\qquad
\lVert x\rVert_2=\sqrt{\sum_i x_i^2},\qquad
\lVert x\rVert_\infty=\max_i |x_i|
$$

Cosine similarity is:

$$
\cos(x,y)=\frac{x^\top y}{\lVert x\rVert_2\lVert y\rVert_2}
$$

Euclidean distance preserves magnitude and direction; cosine emphasizes angle. On unit-normalized vectors, ranking by cosine, dot product, and squared Euclidean distance is equivalent up to monotone transformations. With unnormalized embeddings, they can produce different neighbors.

Choose geometry from the data and decision. Manhattan distance can be more robust in some sparse settings; Mahalanobis distance accounts for covariance but requires a stable covariance estimate.

## 4. Matrices, linear systems, rank, and conditioning

A linear system is $Ax=b$. An inverse is rarely the computational answer; solve the system with a factorization appropriate to the matrix.

- **Rank:** number of linearly independent rows or columns.
- **Null space:** directions mapped to zero.
- **Column space:** reachable outputs $Ax$.
- **Full column rank:** unique least-squares coefficients when the design is otherwise well posed.
- **Condition number:** sensitivity of the solution to input perturbations.

For least squares, minimize:

$$
\min_w \lVert Xw-y\rVert_2^2
$$

The normal equations $X^\top Xw=X^\top y$ explain the solution, but QR or SVD is usually more numerically stable than explicitly computing $(X^\top X)^{-1}$.

Multicollinearity makes coefficient estimates unstable: predictions may remain acceptable while individual coefficients change sharply. Regularization, feature redesign, or a lower-dimensional basis can help.

## 5. Basis, orthogonality, and projection

A basis spans a vector space with independent directions. An orthonormal basis has unit, mutually orthogonal vectors, so coordinates are simple dot products.

Projection of $x$ onto a unit vector $u$ is:

$$
\operatorname{proj}_u(x)=(u^\top x)u
$$

For a matrix $Q$ with orthonormal columns, projection onto its column space is $QQ^\top x$.

Least squares chooses the prediction $X\hat w$ whose residual is orthogonal to the column space of $X$:

$$
X^\top(y-X\hat w)=0
$$

This geometric view explains why the fitted point is the closest point in the model subspace under squared Euclidean loss.

## 6. Eigenvalues, covariance, and PCA

For square $A$, an eigenpair satisfies:

$$
Av=\lambda v
$$

The eigenvalue describes scaling along eigenvector $v$. For a centered data matrix $X$, covariance is proportional to $X^\top X$. PCA finds orthogonal directions of maximum variance, equivalently eigenvectors of the covariance matrix or right singular vectors of centered $X$.

PCA workflow:

1. split data before fitting preprocessing;
2. impute and scale where feature units require it;
3. center using training statistics;
4. fit PCA on training data only;
5. select components using validation performance, reconstruction needs, or a justified variance target;
6. preserve the transformation for serving.

High explained variance does not prove high predictive value, fairness, or cluster quality. PCA is linear and sensitive to scale and outliers.

## 7. SVD and low-rank approximation

Any matrix $A\in\mathbb{R}^{m\times n}$ has singular value decomposition:

$$
A=U\Sigma V^\top
$$

The singular values are nonnegative and measure strength along paired input/output directions. Keeping the top $k$ terms gives the best rank-$k$ approximation under Frobenius and spectral norms:

$$
A_k=U_k\Sigma_kV_k^\top
$$

Uses include latent semantic analysis, recommendation, compression, denoising, pseudoinverses, and diagnosing ill-conditioning. A sharp singular-value decay suggests a compact approximation; a flat spectrum does not.

Truncated SVD on a sparse term-document matrix often avoids centering to preserve sparsity, so do not casually call it identical to centered PCA.

## 8. Derivatives, gradients, Jacobians, and Hessians

- A derivative is the local rate of change of a scalar function of one variable.
- A partial derivative changes one input while holding others fixed.
- The gradient $\nabla f\in\mathbb{R}^d$ contains partial derivatives of scalar $f$ with respect to vector input.
- A Jacobian contains derivatives of a vector output with respect to a vector input.
- A Hessian contains second derivatives of a scalar output and describes local curvature.

For $f(w)=\lVert Xw-y\rVert_2^2/n$:

$$
\nabla_w f=\frac{2}{n}X^\top(Xw-y)
$$

The gradient has the same shape as $w$. A useful interview check is to verify dimensional consistency before doing algebra.

## 9. Chain rule and backpropagation

For $z=f(y)$ and $y=g(x)$:

$$
\frac{dz}{dx}=\frac{dz}{dy}\frac{dy}{dx}
$$

Neural networks compose many functions. Backpropagation traverses the computation graph in reverse, multiplying local derivatives by the upstream sensitivity. Reverse-mode automatic differentiation is efficient for a scalar loss with many parameters.

Common gradient failures:

- detached tensors or non-differentiable operations;
- in-place mutation of needed intermediates;
- saturation in sigmoid/tanh;
- exploding/vanishing products through depth or time;
- incorrect reduction or masking;
- loss computed on padded or leaked targets;
- mixed-precision underflow/overflow.

Check gradients with small synthetic cases, finite differences, parameter/activation statistics, and overfitting one tiny batch.

## 10. Objectives, losses, and metrics

The training objective is what optimization sees; the business metric is what the system must improve. They need not be identical.

- Squared loss strongly penalizes large residuals and estimates a conditional mean under familiar assumptions.
- Absolute loss is more robust and targets a conditional median.
- Cross-entropy trains probabilities by maximizing log likelihood for classification.
- Ranking or contrastive losses optimize relative ordering or representation geometry.

An objective can include regularization and constraints:

$$
J(w)=\frac{1}{n}\sum_{i=1}^n \ell(y_i,f_w(x_i))+\lambda R(w)
$$

Validate whether improvements in the surrogate loss transfer to calibration, decision thresholds, latency, cost, fairness, and the downstream outcome.

## 11. Gradient descent, SGD, and learning rate

Full-batch gradient descent uses all examples per update:

$$
w_{t+1}=w_t-\eta\nabla J(w_t)
$$

Stochastic or mini-batch gradients trade exactness for cheaper, noisier updates. Mini-batches exploit hardware parallelism and often improve optimization throughput.

Learning rate too high can diverge or oscillate; too low can stall. Batch size changes gradient noise, memory, throughput, and sometimes the appropriate learning-rate policy. Compare runs by examples/tokens, optimizer steps, and wall-clock cost—not epochs alone.

Use warmup when early updates are unstable, decay to refine later training, gradient accumulation when memory limits the physical batch, and clipping when large gradients are a diagnosed risk.

## 12. Momentum, Adam, AdamW, and schedules

Momentum smooths updates using an exponential history of gradients. Adam maintains first- and second-moment estimates to adapt step sizes per parameter.

AdamW applies weight decay separately from the adaptive gradient update. That distinction matters because adding an L2 term to the loss is not generally equivalent under adaptive scaling.

Interview comparison:

| Choice | Strength | Watch |
|---|---|---|
| SGD + momentum | simple, often strong final generalization | sensitive schedules; slower early progress |
| Adam/AdamW | fast, robust initial optimization | memory, hyperparameters, decay semantics |
| constant LR | predictable baseline | may waste late-stage refinement |
| cosine/step decay | lower late-stage steps | schedule tied to correct step budget |
| warmup | stabilizes early training | too long delays useful learning |

Do not declare one optimizer universally best; report the model, data, batch, schedule, compute budget, and validation evidence.

## 13. Curvature, conditioning, and optimization geometry

The Hessian describes local curvature. Large curvature differences across directions create narrow valleys: one learning rate may be too large for a steep direction and too small for a flat one.

Normalization, feature scaling, residual connections, initialization, preconditioning, adaptive optimizers, and momentum can improve the effective geometry. A low training loss with poor validation performance is primarily a generalization problem, not proof that the optimizer failed.

Saddle points have zero gradient but mixed positive and negative curvature. Plateaus have small gradients across broad regions. Both differ from a useful local minimum.

## 14. Convexity and constrained optimization

A convex objective over a convex feasible set has no suboptimal local minimum. Strong convexity adds curvature and can give uniqueness and faster convergence guarantees.

Many classical losses are convex in linear-model parameters; neural-network training is not. Convex intuition is still useful locally and for subproblems.

For equality constraint $g(w)=0$, the Lagrangian is:

$$
\mathcal{L}(w,\lambda)=f(w)+\lambda g(w)
$$

Lagrange multipliers represent sensitivity of the optimum to a constraint under suitable conditions. In production optimization, validate units, feasibility, solver status, tolerance, and what happens when no feasible solution exists.

## 15. L1, L2, and regularization

L1 regularization adds $\lambda\lVert w\rVert_1$ and can produce exact zeros because of its geometry. L2 adds $\lambda\lVert w\rVert_2^2$ and smoothly shrinks correlated coefficients.

Regularization controls effective complexity but does not repair leakage, distribution shift, a wrong label, or a biased sample. Tune strength inside the training/validation process. Apply weight decay selectively: biases and normalization parameters are often handled differently in deep networks.

Early stopping, data augmentation, dropout, and architectural constraints are also regularizers, but they work through different mechanisms.

## 16. Numerical stability and precision

Stable softmax subtracts the maximum logit:

$$
\operatorname{softmax}(z_i)=\frac{e^{z_i-m}}{\sum_j e^{z_j-m}},\quad m=\max_j z_j
$$

Use `logsumexp` for log probabilities, `log1p` for $\log(1+x)$ near zero, and stable library losses that combine activation and log operations. Avoid explicit matrix inverses and probabilities rounded to exactly zero before logging.

Mixed precision improves throughput and memory but needs supported kernels, loss scaling where applicable, stable reductions, and accuracy checks against an appropriate baseline. Monitor NaN/Inf counts, gradient norms, activation ranges, and the first failing step.

## 17. Two derivations worth speaking

### Mean-squared-error gradient

For $J(w)=\lVert Xw-y\rVert_2^2/n$, let $r=Xw-y$. Then $J=r^\top r/n$ and:

$$
\nabla_wJ=\frac{2}{n}X^\top r
$$

Explain shapes: `X` is `(n, d)`, `w` is `(d,)`, `r` is `(n,)`, so the gradient is `(d,)`.

### Binary logistic loss gradient

For logits $z=Xw$, probabilities $p=\sigma(z)$, and average binary cross-entropy:

$$
\nabla_wJ=\frac{1}{n}X^\top(p-y)
$$

The residual is probability error rather than raw prediction error. Regularization adds its own gradient.

## 18. Small numerical checks

```python
from __future__ import annotations

from collections.abc import Callable

import numpy as np
from numpy.typing import NDArray


def stable_softmax(logits: NDArray[np.float64]) -> NDArray[np.float64]:
    shifted = logits - np.max(logits, axis=-1, keepdims=True)
    exp = np.exp(shifted)
    return exp / np.sum(exp, axis=-1, keepdims=True)


def central_difference(
    objective: Callable[[NDArray[np.float64]], float],
    weights: NDArray[np.float64],
    index: int,
    eps: float = 1e-6,
) -> float:
    plus = weights.copy()
    minus = weights.copy()
    plus[index] += eps
    minus[index] -= eps
    return float((objective(plus) - objective(minus)) / (2 * eps))
```

Finite differences are a diagnostic on small smooth cases, not a scalable training method. Compare absolute and relative error, and avoid testing exactly at non-differentiable points.

## 19. Common interview failure modes

- multiplying matrices without stating shapes;
- saying cosine is a distance without defining the conversion and normalization;
- claiming PCA selects predictive features;
- computing inverses explicitly as the default solver;
- confusing gradient direction with the parameter update direction;
- treating epoch count as comparable when batch size or dataset size changed;
- saying Adam includes the same L2 behavior as AdamW;
- using gradient clipping to hide a broken data or loss pipeline;
- attributing poor validation solely to a local minimum;
- ignoring NaNs, overflow, masking, and reduction semantics.

## 20. Rapid interview Q&A

**Why normalize embeddings for cosine search?**  
It makes the dot product equal cosine similarity and removes vector magnitude from ranking. Confirm that magnitude is not useful information.

**Why can PCA hurt a tree model?**  
It mixes interpretable axis-aligned features, can discard low-variance predictive directions, and may add unnecessary preprocessing.

**Why is $X^\top X$ often worse conditioned than $X$?**  
Its condition number is approximately squared, amplifying numerical sensitivity.

**What does a zero gradient mean?**  
A stationary point or numerical issue—not necessarily a minimum. Inspect curvature, neighborhood behavior, and implementation.

**When is L1 useful?**  
When a sparse solution is plausible and useful, while accounting for instability among correlated features.

## 21. Lead-level case

**Case:** training loss becomes NaN after scaling batch size across GPUs.

A strong answer should:

1. pin the exact code, data, optimizer, precision, global batch, accumulation, and learning-rate schedule;
2. find the first non-finite activation, loss, gradient, or parameter using a small reproducible run;
3. verify target range, masks, reductions, normalization, loss implementation, and distributed aggregation;
4. compare full precision, lower learning rate, warmup, stable kernels, loss scaling, and clipping only with a causal hypothesis;
5. restore from a known checkpoint and re-run a bounded acceptance set;
6. add finite-value assertions, gradient telemetry, and a batch/learning-rate scaling test to the release gate.

## 22. Final checklist

- Can you annotate shapes through a linear layer and attention score calculation?
- Can you explain cosine versus dot product versus Euclidean ranking?
- Can you connect rank, projection, eigendecomposition, SVD, and PCA?
- Can you derive MSE or logistic-loss gradients with shapes?
- Can you explain backpropagation as chain rule rather than a library call?
- Can you compare SGD, momentum, Adam, AdamW, schedules, and batch size?
- Can you distinguish optimization failure, numerical failure, and generalization failure?
- Can you explain L1/L2, convexity, conditioning, and constraints without overclaiming?

## Primary references

- NumPy documentation: array broadcasting and linear algebra.
- PyTorch documentation: autograd mechanics, numerical accuracy, and optimizer APIs.
- Golub and Van Loan, *Matrix Computations*.
- Boyd and Vandenberghe, *Convex Optimization*.
- Goodfellow, Bengio, and Courville, *Deep Learning*, optimization and numerical computation chapters.
