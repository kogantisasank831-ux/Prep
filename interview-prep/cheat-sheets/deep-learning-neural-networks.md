---
layout: "week"
status: "approved"
version: "1.0.0"
last_reviewed: "2026-11-09"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "Deep learning and neural networks interview cheat sheet"
description: "Neural-network mechanics, training, debugging, architectures, and production trade-offs for senior AI and Data Science interviews."
summary: "Revise forward and backward propagation, activations, losses, normalization, optimization, regularization, architectures, debugging, and deployment."
permalink: "/interview-prep/cheat-sheets/deep-learning-neural-networks/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 2 · Deep learning"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 2 source:** This page integrates the prepared revision artifact into the Prep site. It is separate from the Week 1–20 learning assessments.

**Target roles:** AI Engineer, ML Engineer, Applied Scientist, Senior/Lead Data Scientist  
**Goal:** explain neural-network mechanics, train and debug a model, and make architecture/production trade-offs.

## 1. Thirty-second revision

- A neural network repeatedly applies affine transformations and nonlinear activations.
- Forward pass produces predictions; loss measures error; backpropagation uses the chain rule; the optimizer updates parameters.
- ReLU/GELU dominate hidden layers; sigmoid is common for independent binary outputs; softmax produces a categorical distribution.
- Initialization, normalization, residual paths, learning rate, and data quality often matter more than adding layers.
- Training loss down while validation loss rises usually indicates overfitting or train/validation mismatch.
- Exploding gradients need diagnosis and sometimes clipping; vanishing gradients need suitable activations, initialization, normalization, and residual connections.
- In production, evaluate latency, memory, calibration, slices, robustness, and business value—not only average accuracy.

## 2. From neuron to network

A single neuron computes:

$$
z=w^Tx+b,\qquad a=\phi(z)
$$

For layer $l$:

$$
z^{(l)}=W^{(l)}a^{(l-1)}+b^{(l)},\qquad
a^{(l)}=\phi^{(l)}(z^{(l)})
$$

Without nonlinear activation functions, stacking linear layers is still equivalent to one linear transformation.

### Parameter count

A dense layer with `input_dim = d` and `output_dim = h` has:

$$
d\times h+h
$$

parameters: weights plus biases.

**Example:** `512 → 2048` contains `512 × 2048 + 2048 = 1,050,624` parameters.

## 3. Activation functions

| Activation | Formula/behavior | Use and trade-off |
|---|---|---|
| Sigmoid | $1/(1+e^{-z})$ | Binary probability output; saturates and can cause small gradients |
| Tanh | Range `[-1, 1]` | Zero-centered but still saturates |
| ReLU | $\max(0,z)$ | Fast and sparse; units can die on negative side |
| Leaky ReLU | Small negative slope | Reduces dying-ReLU risk |
| GELU | Smooth input-dependent gating | Common in transformers |
| Softmax | $e^{z_i}/\sum_j e^{z_j}$ | Mutually exclusive class distribution |
| Linear | Identity | Regression output or logits before a loss |

### Output/loss pairing

| Task | Output | Typical loss |
|---|---|---|
| Binary classification | One logit | Binary cross-entropy with logits |
| Multi-class, one label | `C` logits | Cross-entropy |
| Multi-label | `C` independent logits | Binary cross-entropy per label |
| Regression | One or more linear values | MSE, MAE, Huber, quantile |
| Embedding similarity | Vector | Contrastive/triplet/InfoNCE-style loss |

Use numerically stable “with logits” losses rather than applying sigmoid/softmax manually before the loss.

## 4. Loss functions

### Binary cross-entropy

$$
\mathcal L=-[y\log p+(1-y)\log(1-p)]
$$

### Multi-class cross-entropy

$$
\mathcal L=-\sum_{c=1}^{C}y_c\log p_c
$$

### Mean squared error

$$
\mathcal L=\frac{1}{n}\sum_i(y_i-\hat y_i)^2
$$

### Huber loss

Quadratic near zero and linear for large residuals; less sensitive to extreme errors than MSE while remaining smooth near the optimum.

### Contrastive learning intuition

Move semantically related examples closer in embedding space and unrelated examples apart. Negative sampling strategy strongly influences what the representation learns.

## 5. Backpropagation and the chain rule

For composed functions $L=f(g(h(x)))$:

$$
\frac{\partial L}{\partial x}=
\frac{\partial L}{\partial f}
\frac{\partial f}{\partial g}
\frac{\partial g}{\partial h}
\frac{\partial h}{\partial x}
$$

### Solved scalar example

Let:

$$
\hat y=wx+b,\qquad L=(\hat y-y)^2
$$

Then:

$$
\frac{\partial L}{\partial w}=2(\hat y-y)x,
\qquad
\frac{\partial L}{\partial b}=2(\hat y-y)
$$

With `x=3`, `y=10`, `w=2`, `b=1`, prediction is 7 and error is `-3`:

$$
\frac{\partial L}{\partial w}=2(-3)(3)=-18,
\qquad
\frac{\partial L}{\partial b}=-6
$$

Gradient descent subtracts the gradient, so a small update increases both parameters and moves prediction toward 10.

### Automatic differentiation

Frameworks record tensor operations into a computational graph and apply reverse-mode automatic differentiation during `backward()`.

```python
import torch

x = torch.tensor(3.0)
y = torch.tensor(10.0)
w = torch.tensor(2.0, requires_grad=True)
b = torch.tensor(1.0, requires_grad=True)

prediction = w * x + b
loss = (prediction - y) ** 2
loss.backward()

assert w.grad.item() == -18.0
assert b.grad.item() == -6.0
```

Gradients accumulate by default; clear them before the next optimization step.

## 6. Optimizers

### SGD

$$
\theta_{t+1}=\theta_t-\eta\nabla_\theta L_t
$$

### Momentum

Accumulates a velocity to reduce oscillation and move consistently through shallow directions.

### Adam and AdamW

Adam maintains exponential moving averages of first and second gradient moments. AdamW decouples weight decay from the adaptive gradient update and is a common default for transformers.

| Optimizer | Strength | Watch for |
|---|---|---|
| SGD + momentum | Often strong generalization; simple | More tuning and slower early progress |
| Adam | Fast adaptive progress | Coupled L2 behavior; may generalize differently |
| AdamW | Adaptive updates with decoupled weight decay | Learning rate/warm-up still critical |

### Learning-rate schedules

- Warm-up: gradually increase rate at the start, useful for large/transformer training.
- Step/exponential decay: reduce at fixed schedule.
- Cosine decay: smooth decrease, often with warm-up.
- Reduce-on-plateau: react to validation stagnation.

The learning rate is usually the most important hyperparameter.

## 7. Initialization

Poor initialization can make activations or gradients explode/vanish.

- Xavier/Glorot: maintains variance for tanh/linear-like activations.
- He/Kaiming: designed for ReLU-family activations.
- Biases are commonly zero or small values.
- Residual branches may use specialized scaling/initialization in deep models.

Check activation and gradient distributions instead of assuming an initializer solved the problem.

## 8. Normalization

| Method | Normalizes across | Common location |
|---|---|---|
| BatchNorm | Batch statistics per channel/feature | CNNs and large stable batches |
| LayerNorm | Features within each example/token | Transformers and variable-length sequences |
| GroupNorm | Channel groups within each example | Vision with small batches |
| RMSNorm | Root-mean-square magnitude, no mean centering | Modern language models |

### BatchNorm behavior

- Training: uses current mini-batch statistics and updates running estimates.
- Evaluation: uses stored running statistics.
- Small/nonrepresentative batches can make estimates noisy.

Forgetting `model.eval()` changes Dropout and BatchNorm behavior during validation/inference.

## 9. Regularization

- Weight decay/L2-like penalties discourage large weights.
- Dropout randomly zeros activations during training; disabled during evaluation.
- Early stopping prevents training beyond the validation optimum.
- Data augmentation injects valid invariances and often beats generic regularization.
- Label smoothing discourages extreme class probabilities but can affect calibration.
- Mixup/CutMix combine examples/labels for vision-like tasks.
- Stochastic depth drops residual blocks in very deep networks.

Regularization cannot repair target leakage, invalid splits, or bad labels.

## 10. Vanishing and exploding gradients

### Symptoms

- Vanishing: early-layer gradient norms near zero; no learning.
- Exploding: loss becomes `NaN/Inf`, gradients spike, parameters diverge.

### Controls

- suitable activation and initialization;
- normalization;
- residual/skip connections;
- gated recurrence such as LSTM/GRU;
- gradient clipping;
- lower learning rate or stable optimizer settings;
- mixed-precision loss scaling;
- shorter unrolls/truncated backprop for long recurrent sequences.

```python
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

Clipping limits damage but does not identify the underlying cause.

## 11. Architecture families

### Multilayer perceptron

Good for fixed-size features and learned nonlinear interactions. For ordinary tabular data, compare with gradient-boosted trees; neural networks do not automatically win.

### Convolutional neural network

Convolution uses local shared kernels:

$$
\text{output size}=\left\lfloor\frac{N+2P-K}{S}\right\rfloor+1
$$

where input size is $N$, padding $P$, kernel $K$, and stride $S$.

Benefits: translation-related inductive bias, parameter sharing, hierarchical spatial features. Key concepts: receptive field, channels, stride, dilation, pooling, residual blocks.

### RNN, LSTM, and GRU

RNN recurrence:

$$
h_t=\phi(W_xx_t+W_hh_{t-1}+b)
$$

LSTM/GRU gates improve gradient flow and selective memory, but sequential recurrence limits parallel training and long-range modeling compared with transformers.

### Autoencoder

Encoder compresses input into latent representation; decoder reconstructs it. Uses include compression, denoising, representation learning, and anomaly detection—with carefully chosen thresholds and validation.

### Variational autoencoder

Learns a distributional latent space using reconstruction plus KL-divergence regularization, enabling sampling but often producing smoother outputs.

### GAN

Generator competes against discriminator. Can produce sharp samples but training may suffer instability, mode collapse, and evaluation difficulty.

### Diffusion model

Learns to reverse a gradual noising process. Stable training and strong generative quality, but iterative sampling can be computationally expensive.

## 12. Residual connections

Residual block:

$$
y=F(x)+x
$$

The identity path improves gradient flow and lets layers learn a residual transformation. Shapes must match or the skip path needs projection.

Transformers use residual paths around attention and feed-forward sublayers. Pre-norm versus post-norm placement changes optimization behavior.

## 13. Embeddings

An embedding maps a discrete ID/token/category to a dense vector. Similarity emerges from the training objective—not from dimensionality alone.

Interview points:

- learned lookup versus pretrained embedding;
- embedding dimension and vocabulary size;
- cold/unseen IDs;
- normalization and cosine similarity;
- negative sampling;
- leakage and privacy from memorized identifiers;
- version compatibility between model and embedding index.

## 14. Training loop in PyTorch

```python
from collections.abc import Iterable

import torch
from torch import nn
from torch.optim import AdamW

def train_epoch(
    model: nn.Module,
    batches: Iterable[tuple[torch.Tensor, torch.Tensor]],
    optimizer: AdamW,
    loss_fn: nn.Module,
    device: torch.device,
) -> float:
    model.train()
    total_loss = 0.0
    examples = 0

    for features, labels in batches:
        features = features.to(device)
        labels = labels.to(device)

        optimizer.zero_grad(set_to_none=True)
        logits = model(features)
        loss = loss_fn(logits, labels)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        batch_size = features.shape[0]
        total_loss += loss.item() * batch_size
        examples += batch_size

    return total_loss / max(examples, 1)

@torch.inference_mode()
def evaluate(
    model: nn.Module,
    batches: Iterable[tuple[torch.Tensor, torch.Tensor]],
    loss_fn: nn.Module,
    device: torch.device,
) -> float:
    model.eval()
    total_loss = 0.0
    examples = 0

    for features, labels in batches:
        features = features.to(device)
        labels = labels.to(device)
        loss = loss_fn(model(features), labels)
        batch_size = features.shape[0]
        total_loss += loss.item() * batch_size
        examples += batch_size

    return total_loss / max(examples, 1)
```

Production additions: deterministic data split, seed/versions, checkpoints, AMP, scheduler, distributed sampler, metric aggregation, early stopping, and resume integrity.

## 15. Batch size and gradient accumulation

- Larger batch: smoother gradient estimate and higher hardware utilization, but more memory and sometimes different generalization.
- Smaller batch: noisier updates, potentially useful regularization, but lower utilization.
- Gradient accumulation simulates a larger effective batch:

$$
B_{effective}=B_{micro}\times N_{accumulation}\times N_{data\ parallel\ workers}
$$

Divide loss by accumulation steps or otherwise ensure gradient scale is correct. Scheduler step semantics must match optimizer updates, not blindly every micro-batch.

## 16. Mixed precision and distributed training

### Mixed precision

Uses lower precision for suitable operations while retaining higher precision where needed.

Benefits: lower memory and often faster tensor-core compute. Risks: overflow, underflow, unsupported/unstable operations, and unnoticed quality differences. Use autocast and gradient scaling; compare exact candidate quality.

### Distributed data parallel

Each process has a model replica, processes different data, and synchronizes gradients. The data must be sharded correctly; communication, stragglers, and global batch size matter.

### Model/state sharding

FSDP/ZeRO-style approaches shard parameters, gradients, and/or optimizer state when a full replica does not fit. Tensor/pipeline parallelism split computation differently and introduce communication/scheduling trade-offs.

## 17. Memory accounting

Training memory includes:

- parameters;
- gradients;
- optimizer states;
- activations saved for backward;
- temporary workspaces;
- framework/allocator overhead.

For Adam with full-precision states, optimizer plus gradients can exceed parameter memory several times over. Activation memory grows with batch, sequence/spatial size, layer width, and depth. Techniques: activation checkpointing, mixed precision, smaller micro-batch, sharding, efficient attention, and parameter-efficient fine-tuning.

## 18. Transfer learning

Workflow:

1. choose a pretrained model matching modality/license/task;
2. replace/adapt the task head;
3. freeze most layers for a baseline;
4. unfreeze gradually or fine-tune all layers at a lower learning rate;
5. monitor catastrophic forgetting and domain shift;
6. compare against training from scratch and simpler baselines.

Avoid transferring from data with unacceptable leakage, license restrictions, or domain mismatch.

## 19. Debugging checklist

### Model cannot overfit a tiny sample

- Verify labels and input alignment.
- Check loss/output compatibility and tensor shapes.
- Disable augmentation/dropout temporarily.
- Inspect learning rate, gradients, and parameter updates.
- Confirm train mode and that parameters require gradients.
- Compare to a tiny known-correct implementation.

### Training loss decreases, validation is poor

- Leakage-safe split and train/validation distribution.
- Overfitting, duplicates, class imbalance, or label noise.
- Preprocessing differences and augmentation validity.
- Threshold/calibration and subgroup performance.

### Loss is NaN

- Bad inputs/labels, division/log of invalid values.
- Excessive learning rate or exploding gradients.
- Mixed-precision overflow.
- Unstable custom operation or invalid normalization batch.

Log distributions and summaries—not sensitive raw samples.

## 20. Evaluation and error analysis

- Match metrics to task and operating threshold.
- Report uncertainty and meaningful slices.
- Compare to business/simple baselines.
- Inspect false positives/negatives or large residuals.
- Evaluate calibration for decisions using probabilities.
- Test robustness to plausible corruptions and drift.
- Measure latency, throughput, memory, and cost on target hardware.
- Keep a final test set independent of model/hyperparameter selection.

## 21. Common traps

| Trap | Better reasoning |
|---|---|
| More layers always improve results | Capacity helps only with suitable data, optimization, and regularization |
| Apply softmax before cross-entropy-with-logits | Pass logits to the numerically stable loss |
| Forget to clear gradients | Gradients accumulate in PyTorch by default |
| Validate in training mode | Use `eval()` and inference/no-grad context |
| Clip gradients and declare problem solved | Diagnose data, loss, precision, and learning rate |
| Use BatchNorm with tiny unstable batches | Consider GroupNorm/LayerNorm or other design |
| Compare models on different splits | Use identical data and evaluation contract |
| Claim reproducibility from one seed | Record lineage and quantify seed/numerical variability |
| GPU utilization alone means efficiency | Reconcile throughput, latency, memory, quality, and cost |

## 22. Rapid interview questions and answers

1. **Why nonlinear activation?** Without it, stacked affine layers collapse to one affine transformation.
2. **Why scale dot products or initialize weights carefully?** Uncontrolled magnitudes saturate activations/softmax and destabilize gradients.
3. **BatchNorm versus LayerNorm?** BatchNorm uses batch statistics per feature/channel; LayerNorm normalizes features within each example/token.
4. **Dropout at inference?** Normally disabled; Monte Carlo dropout is a deliberate uncertainty technique, not default behavior.
5. **Why residual connections?** They create identity gradient paths and let layers learn residual transformations.
6. **SGD versus AdamW?** AdamW adapts per-parameter steps and often converges quickly; SGD may generalize well but needs more tuning. Compare on the task.
7. **What is gradient accumulation?** Sum gradients over micro-batches before one optimizer update to increase effective batch size.
8. **Why can mixed precision fail?** Limited numeric range/precision can overflow or underflow; scaling and operation selection matter.
9. **What does `model.eval()` do?** Switches modules such as Dropout and BatchNorm to evaluation behavior; it does not itself disable gradients.
10. **How do you debug a deep model?** Verify data/shapes/loss, overfit a tiny sample, inspect gradients/activations, simplify, then add complexity incrementally.

## 23. Lead-level case

**Question:** Build a visual defect-classification system when only 20,000 labeled images are available and false negatives are expensive.

**Strong answer structure:**

1. Define defect taxonomy, unit, image-capture process, decision, review workflow, latency, and false-negative cost.
2. Split by production line/time/batch to prevent near-duplicate and source leakage.
3. Start with quality-control rules and pretrained vision-model transfer learning.
4. Validate labels with domain reviewers; measure inter-rater disagreement and ambiguous class policy.
5. Use physically valid augmentation, class-weighted/focal-style loss only after establishing baseline, and calibrated probabilities.
6. Evaluate recall at acceptable precision/review capacity, per-defect recall, PR curves, calibration, and confidence intervals.
7. Add abstention/human review for uncertain or novel images; never force every prediction.
8. Test lighting/camera/line shifts and out-of-distribution cases.
9. Optimize model size/precision only with candidate-matched quality checks on target hardware.
10. Deploy shadow then canary; monitor capture quality, drift, review disagreement, latency, and confirmed missed defects.

## 24. Final revision checklist

- [ ] I can derive a simple gradient using the chain rule.
- [ ] I can choose activation, output, and loss correctly.
- [ ] I understand initialization, normalization, residuals, and regularization.
- [ ] I can explain SGD, momentum, AdamW, warm-up, and schedules.
- [ ] I can write and debug a safe training/evaluation loop.
- [ ] I understand effective batch size, mixed precision, and distributed training.
- [ ] I can compare MLP, CNN, RNN, autoencoder, GAN, and diffusion models.
- [ ] I can estimate major training-memory components.
- [ ] I can design evaluation, rollout, monitoring, and human fallback.

## Primary references

- [PyTorch documentation](https://docs.pytorch.org/docs/stable/)
- [PyTorch autograd mechanics](https://docs.pytorch.org/docs/stable/notes/autograd.html)
- [PyTorch DistributedDataParallel](https://docs.pytorch.org/docs/stable/generated/torch.nn.parallel.DistributedDataParallel.html)
