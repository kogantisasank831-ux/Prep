# Week 27 logic

For frozen weight matrix `W`, LoRA computes `W x + (alpha / rank) B A x`.
`A` starts with small random values and `B` with zeros, so the initial adapter
does not change the base. Mean squared error gradients update only A and B;
global-norm clipping limits unstable steps. The QLoRA switch dequantises a
simulated signed 4-bit base for forward passes while adapters remain full
precision.

Catastrophic forgetting cannot be demonstrated by this single synthetic task.
A real experiment needs held-out domain, general-capability and safety suites.

