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
title: "Transformers interview cheat sheet"
description: "Transformer architecture, attention, masking, position, efficiency, inference, and model-family trade-offs."
summary: "Revise QKV attention, masks, residual blocks, positional methods, encoder and decoder families, KV cache, GQA/MQA, FlashAttention, and long-context limits."
permalink: "/interview-prep/cheat-sheets/transformers/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 2 · Transformers"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 2 source:** This page integrates the prepared revision artifact into the Prep site. It is separate from the Week 1–20 learning assessments.

**Target roles:** AI Engineer, ML Engineer, Applied Scientist, Senior/Lead Data Scientist  
**Use:** fast revision, interview answers, architecture comparison, and production trade-off discussion  
**Interview rule:** explain tensor shapes, masking, computational cost, and inference behavior—not only the block diagram.

## 1. Thirty-second revision

- A transformer repeatedly applies **attention**, a position-wise **feed-forward network**, residual connections, and normalization.
- Scaled dot-product attention is $\operatorname{softmax}(QK^T / \sqrt{d_k})V$.
- Self-attention relates tokens within one sequence; cross-attention reads a different sequence or modality.
- Encoder-only models build bidirectional representations; decoder-only models generate causally; encoder-decoder models map an input sequence to an output sequence.
- Attention itself is permutation-equivariant, so positional information must be added or encoded.
- Full attention materializes an $n\times n$ interaction pattern and has quadratic sequence-length cost.
- During autoregressive inference, the KV cache reuses earlier keys and values; it saves recomputation but consumes memory.
- MQA/GQA reduce KV-cache size; FlashAttention reduces attention memory traffic without changing exact attention semantics.
- Long context does not guarantee good use of every token. Retrieval, chunking, position, and evaluation still matter.
- For a lead interview, connect architecture choice to data, latency, memory, throughput, quality, licensing, and operational risk.

## 2. Transformer block: the mental model

For hidden states $X\in\mathbb{R}^{n\times d_{model}}$:

1. project $X$ into queries, keys, and values;
2. mix information across token positions using attention;
3. add the residual path and normalize;
4. transform each position independently with an MLP/FFN;
5. add another residual path and normalize;
6. repeat for many layers.

The common pre-norm form is:

$$
H = X + \operatorname{Attention}(\operatorname{Norm}(X))
$$

$$
Y = H + \operatorname{FFN}(\operatorname{Norm}(H))
$$

Architectures differ in norm placement, activation, bias use, positional method, attention pattern, and FFN design.

## 3. Tokens, embeddings, and shapes

Text is first converted to token IDs. An embedding table maps each ID to a vector:

$$
X = E[\text{token ids}],\quad X\in\mathbb{R}^{B\times n\times d_{model}}
$$

where:

- $B$: batch size;
- $n$: sequence length;
- $d_{model}$: hidden dimension.

The same architecture can consume image patches, audio frames, or multimodal projected features once they are represented as a sequence of vectors.

**Interview trap:** the tokenizer and embedding table are part of the model contract. Swapping tokenizers changes IDs, lengths, and semantics.

## 4. Query, key, and value

For one head:

$$
Q=XW_Q,\quad K=XW_K,\quad V=XW_V
$$

Intuition:

- **Query:** what information does this position seek?
- **Key:** what kind of information does each position offer?
- **Value:** what content is returned if the position receives attention?

The similarity $QK^T$ produces one score for every allowed query-key pair. Softmax converts scores into weights, and the weighted values form the output.

## 5. Scaled dot-product attention

$$
\operatorname{Attention}(Q,K,V)=
\operatorname{softmax}\left(\frac{QK^T}{\sqrt{d_k}}+M\right)V
$$

$M$ is a mask/bias. Disallowed positions receive a very negative value before softmax.

### Why divide by $\sqrt{d_k}$?

If query/key components have roughly unit variance, their dot product variance grows with $d_k$. Large logits make softmax extremely peaked and gradients weak. Scaling stabilizes their magnitude.

### Shape walkthrough

With $Q,K,V\in\mathbb{R}^{B\times h\times n\times d_h}$:

- $QK^T$: $[B,h,n,n]$;
- attention probabilities: $[B,h,n,n]$;
- probabilities times $V$: $[B,h,n,d_h]$;
- concatenate heads: $[B,n,h d_h]=[B,n,d_{model}]$.

## 6. Self-attention, cross-attention, and causal attention

| Type | Q source | K/V source | Typical use |
|---|---|---|---|
| Self-attention | Current sequence | Same sequence | Contextualize tokens |
| Causal self-attention | Current prefix | Same prefix, future masked | Decoder-only generation |
| Cross-attention | Decoder/query stream | Encoder or another modality | Translation, captioning, multimodal fusion |

Bidirectional encoder attention can use both left and right context. A causal decoder position may attend only to itself and earlier tokens.

## 7. Masks and attention bias

### Padding mask

Prevents real tokens from attending to padding. It usually marks valid key positions.

### Causal mask

Prevents position $i$ from reading any position $j>i$ during next-token training and generation.

### Packed-sequence mask

When multiple samples share a packed sequence, it prevents one document from attending to another.

### Common failures

- wrong broadcasting dimension;
- inverted Boolean meaning;
- masking after softmax rather than before it;
- using finite values that are not negative enough for the dtype;
- missing document boundaries in packed training;
- off-by-one label shifting in causal language modeling.

## 8. Multi-head attention

Instead of one large attention calculation, use $h$ heads:

$$
\operatorname{MHA}(X)=\operatorname{Concat}(head_1,\ldots,head_h)W_O
$$

Different heads can learn different interaction patterns. This is capacity, not a guarantee that each head becomes human-interpretable.

Usually $d_h=d_{model}/h$. Increasing head count while holding $d_{model}$ fixed makes each head narrower; it does not automatically increase total attention parameter count substantially.

## 9. Feed-forward network

Each token is transformed independently with shared parameters:

$$
\operatorname{FFN}(x)=W_2\,\phi(W_1x+b_1)+b_2
$$

The intermediate dimension is commonly several times $d_{model}$. Modern variants often use gated activations such as GLU/SwiGLU.

Attention mixes information **between positions**; the FFN transforms features **within each position**.

## 10. Residual connections and normalization

Residual connections provide an identity path for information and gradients. Normalization controls activation scale.

| Pattern | Form | Practical intuition |
|---|---|---|
| Post-norm | $\operatorname{Norm}(x+F(x))$ | Original transformer form; deep training can be less stable |
| Pre-norm | $x+F(\operatorname{Norm}(x))$ | Stronger gradient path; common in modern LLMs |

LayerNorm normalizes across hidden features per token. RMSNorm uses the root-mean-square magnitude without subtracting the mean and is common in decoder LLMs.

## 11. Positional information

Attention alone does not know token order.

### Sinusoidal encoding

Fixed sine/cosine signals at different frequencies are added to embeddings. They require no learned position table.

### Learned absolute positions

A learned vector is associated with each position. Straightforward, but extension beyond trained positions is not automatic.

### Relative position bias

Attention scores depend on relative distance or buckets rather than only absolute indices.

### RoPE

Rotary position embeddings rotate query/key pairs by position-dependent angles so their dot products encode relative displacement. Context extension still requires validation; merely accepting a larger token count does not prove quality.

### ALiBi awareness

Adds head-specific distance penalties to attention scores. It can support length extrapolation behavior without adding position embeddings to token vectors.

## 12. Three major architecture families

| Family | Attention | Training objective example | Strengths | Examples of use |
|---|---|---|---|---|
| Encoder-only | Bidirectional | Masked-token prediction | Representation, classification, extraction | BERT-style tasks |
| Decoder-only | Causal | Next-token prediction | Open-ended generation, in-context learning | GPT/Llama-style assistants |
| Encoder-decoder | Encoder bidirectional; decoder causal + cross-attention | Denoising or sequence-to-sequence | Conditioned transformation | T5-style summarization/translation |

Choose by task and evidence, not by fashion. Encoder models can be much cheaper for classification or retrieval than generative models.

## 13. Pretraining objectives

### Masked language modeling

Predict hidden/corrupted tokens using surrounding context. Good for bidirectional representations.

### Causal language modeling

Factorizes sequence probability:

$$
p(x_{1:n})=\prod_{t=1}^{n}p(x_t\mid x_{<t})
$$

Training predicts the next token with teacher forcing; inference feeds generated tokens back autoregressively.

### Denoising/sequence-to-sequence

Corrupt input spans and reconstruct them with an encoder-decoder model.

**Important:** next-token prediction teaches a distribution over continuations. Instruction following is generally added through post-training and data, not guaranteed by pretraining alone.

## 14. Training versus autoregressive inference

During causal training, all target positions can be scored in parallel because the full shifted sequence is known and the causal mask blocks future information.

During generation:

1. run a **prefill** over the prompt;
2. sample/select one new token;
3. append it;
4. run a **decode** step for the new position;
5. repeat until a stop condition.

Decode is sequential across output tokens. This explains why time to first token and inter-token latency are different metrics.

## 15. KV cache

Without caching, each decode step would recompute keys and values for the entire prefix. The KV cache stores prior-layer keys and values and computes only the new token's projections.

Approximate cache elements for a decoder are proportional to:

$$
2\times L\times n\times h_{kv}\times d_h
$$

where 2 represents K and V, $L$ is layer count, $n$ is cached tokens, and $h_{kv}$ is the number of KV heads. Multiply by batch/concurrent sequences and bytes per element for memory.

The KV cache:

- reduces repeated compute;
- grows with context length, concurrency, layers, head dimension, KV-head count, and precision;
- can dominate serving memory even when model weights fit;
- must be managed with paging, eviction, prefix reuse, and batching policies.

## 16. MHA, MQA, and GQA

| Design | Query heads | KV heads | Main trade-off |
|---|---:|---:|---|
| MHA | Many | Same as query heads | Highest KV-cache footprint |
| MQA | Many | One shared KV head | Small cache and fast decode; may reduce quality/capacity |
| GQA | Many | Fewer KV groups | Compromise between MHA and MQA |

Do not confuse **attention heads** with **KV heads**. GQA keeps multiple query heads while groups share K/V projections.

## 17. Complexity and memory

For full self-attention with sequence length $n$ and hidden size $d$:

- attention score computation is roughly $O(n^2d)$;
- the score/probability matrix is $O(n^2)$ per head/batch;
- projection and FFN costs also matter and may dominate at shorter sequences.

Saying “transformers are $O(n^2)$” is incomplete: identify which operation, and distinguish training/prefill from single-token decode.

## 18. FlashAttention

FlashAttention changes the execution algorithm for exact attention. It tiles computation so large intermediate attention matrices need not be repeatedly written to and read from slow high-bandwidth memory.

- **It is:** an IO-aware exact-attention implementation.
- **It is not:** sparse attention, approximate attention, a different learned architecture, or KV-cache compression.
- Benefit depends on hardware, dtype, sequence shape, kernel support, and surrounding bottlenecks.

## 19. Long-context strategies

| Strategy | Idea | Trade-off |
|---|---|---|
| Sliding-window attention | Attend within a local window | Linear-ish local pattern; limited direct global interaction |
| Sparse/global tokens | Select allowed long-range links | Pattern must match task |
| Chunking + retrieval | Put only relevant chunks into context | Retrieval errors and lost cross-chunk dependencies |
| Position scaling/interpolation | Adapt positional behavior | Quality can degrade; must evaluate at length |
| Compression/summarization | Replace old detail with a compact state | Information can be lost or distorted |
| Recurrent/state-space memory | Carry state rather than all pairwise links | Different optimization and capability trade-offs |

Test “needle” retrieval, multi-evidence synthesis, position sensitivity, citation correctness, latency, and memory—not only the advertised maximum context.

## 20. Mixture of experts

A sparse MoE replaces some dense FFNs with multiple experts and a router. Each token activates only a subset, increasing parameter capacity without activating every parameter per token.

Key concepts:

- top-$k$ routing;
- router/load-balancing loss;
- expert capacity and token dropping/overflow;
- expert parallelism and all-to-all communication;
- routing instability and hot experts;
- total parameters versus active parameters.

MoE can reduce compute per parameter count, but distributed communication and serving complexity increase.

## 21. State-space and hybrid architectures

Mamba-style selective state-space models process sequences through a learned state update rather than full pairwise attention at every layer. They target linear sequence scaling and efficient long-sequence processing.

Interview-level comparison:

- attention offers content-based random access to earlier positions;
- state-space layers compress history into state;
- hybrid models can combine attention and state-space blocks;
- empirical task quality, kernels, hardware, and ecosystem support decide—not asymptotics alone.

## 22. Minimal PyTorch attention

This example is educational; production kernels handle fused operations, masks, layouts, and numerical details more efficiently.

```python
from __future__ import annotations

import math

import torch
from torch import Tensor, nn


class CausalSelfAttention(nn.Module):
    def __init__(self, d_model: int, num_heads: int) -> None:
        super().__init__()
        if d_model % num_heads != 0:
            raise ValueError("d_model must be divisible by num_heads")
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        self.qkv = nn.Linear(d_model, 3 * d_model, bias=False)
        self.out = nn.Linear(d_model, d_model, bias=False)

    def forward(self, x: Tensor) -> Tensor:
        batch, seq_len, d_model = x.shape
        qkv = self.qkv(x)
        qkv = qkv.view(batch, seq_len, 3, self.num_heads, self.head_dim)
        q, k, v = qkv.unbind(dim=2)
        q = q.transpose(1, 2)  # [B, H, T, D]
        k = k.transpose(1, 2)
        v = v.transpose(1, 2)

        scores = q @ k.transpose(-2, -1) / math.sqrt(self.head_dim)
        causal = torch.triu(
            torch.ones(seq_len, seq_len, device=x.device, dtype=torch.bool),
            diagonal=1,
        )
        scores = scores.masked_fill(causal, torch.finfo(scores.dtype).min)
        probabilities = torch.softmax(scores, dim=-1)
        context = probabilities @ v
        context = context.transpose(1, 2).contiguous().view(batch, seq_len, d_model)
        return self.out(context)
```

In real PyTorch code, prefer supported scaled-dot-product attention APIs when appropriate so optimized kernels can be selected.

## 23. Training stability and scaling

Controls commonly discussed in interviews:

- warm-up followed by a decay schedule;
- AdamW and appropriate weight decay exclusions;
- pre-normalization/RMSNorm;
- residual scaling or careful initialization;
- gradient clipping and gradient-norm monitoring;
- mixed precision with numerically sensitive operations handled safely;
- gradient accumulation, checkpointing, and distributed sharding;
- deduplicated, balanced, high-quality data;
- checkpoint/evaluation gates and reproducibility metadata.

Scaling model size without scaling data and compute appropriately can undertrain the model. Scaling laws describe empirical trade-offs; they do not replace task-specific evaluation.

## 24. Debugging transformer failures

### Loss does not decrease

- verify shifted labels and ignore index;
- inspect masks and packed-document boundaries;
- overfit a tiny batch;
- confirm tokenizer/model vocabulary alignment;
- check learning rate, frozen parameters, gradients, and precision overflow.

### Generation repeats or never stops

- verify end-of-sequence IDs and chat template;
- inspect sampling and repetition settings;
- check maximum-new-token handling;
- compare greedy output with sampled output;
- check fine-tuning examples for repeated formats.

### Fine-tuned model loses base capabilities

- check data diversity, amount, and learning rate;
- mix replay/general data if justified;
- compare adapters versus full fine-tuning;
- maintain regression suites across capabilities and safety.

### Long-context accuracy is poor

- measure by evidence position and number of supporting facts;
- test truncation/tokenization and prompt layout;
- compare retrieval/chunking with full-context input;
- verify positional/context-extension method was trained and evaluated.

## 25. Architecture selection table

| Problem | Reasonable starting point | Why |
|---|---|---|
| Intent classification | Small encoder or sparse baseline | Low latency and direct discriminative output |
| Semantic retrieval | Bi-encoder, optional cross-encoder reranker | Precompute corpus embeddings; rerank a small set |
| Open-ended assistant | Decoder-only instruct model | Flexible conditional generation |
| Translation/summarization | Encoder-decoder or capable decoder | Strong input-conditioned generation |
| Document extraction | Encoder/encoder-decoder or constrained LLM | Depends on layout, schema complexity, and data |
| Image question answering | Vision encoder/projector + language model | Fuse visual tokens and language generation |

Always establish a task metric, latency/cost envelope, baseline, and error analysis before selecting the largest model.

## 26. Common interview traps

- Saying attention “understands importance” without explaining learned query-key similarity.
- Treating attention weights as a guaranteed causal explanation.
- Calling FlashAttention approximate or sparse.
- Claiming KV caching makes generation parallel across future output tokens.
- Ignoring batch/concurrency in KV-cache memory.
- Confusing total MoE parameters with active parameters per token.
- Assuming a long advertised context gives uniform recall.
- Forgetting that encoder-only models may be the best production choice.
- Describing RoPE as a simple position vector added to embeddings.
- Discussing Big-O without hardware, kernels, shapes, and measured latency.

## 27. Rapid interview questions and answers

1. **Why scale attention logits?** Dot-product variance grows with key dimension; scaling prevents overly saturated softmax.
2. **Self- versus cross-attention?** Self-attention obtains Q/K/V from one stream; cross-attention obtains Q from one and K/V from another.
3. **Why positional encoding?** Plain self-attention does not encode token order.
4. **Encoder versus decoder?** Encoder attention is usually bidirectional; decoder attention is causal and supports autoregressive generation.
5. **What does the KV cache save?** Recalculation of earlier keys and values during decoding, at the cost of memory.
6. **MHA versus GQA?** GQA lets multiple query heads share fewer KV heads, reducing cache and bandwidth.
7. **What does FlashAttention optimize?** Memory IO and tiling for exact attention.
8. **Why residual connections?** They preserve an identity path and improve information/gradient flow.
9. **Why is decoding slow?** Output tokens are generated sequentially, with model work at each step.
10. **How evaluate long context?** Slice by evidence position/length and test retrieval, synthesis, quality, latency, and memory.

## 28. Lead-level design case

**Question:** Serve a document assistant with 32K-token prompts, 500 concurrent users, and strict citation requirements.

**Strong answer structure:**

1. Clarify arrival rate, active concurrency, prompt/output distributions, TTFT/inter-token SLOs, accuracy, privacy, and hardware/budget.
2. Build a representative evaluation set with answerability, multi-evidence, position, language, and refusal cases.
3. Compare retrieval-selected context with sending whole documents; measure citation faithfulness.
4. Shortlist models by quality and license, then benchmark the actual context/output distribution.
5. Calculate weights plus KV-cache/headroom memory; account for GQA, cache dtype, concurrency, and fragmentation.
6. Use continuous/dynamic batching, paged KV management, prefix caching where prompts genuinely repeat, and admission/backpressure.
7. Separate prefill-heavy and decode-heavy measurements; report TTFT, tokens/s, p95/p99, OOM rate, and cost per successful answer.
8. Enforce document access before retrieval and carry source IDs through generation/citation validation.
9. Add groundedness/citation gates, low-confidence abstention, monitoring, canary release, and rollback.
10. Revisit chunking, prompt length, model size, quantization, and routing using production traces.

## 29. Final revision checklist

- [ ] I can derive attention and state every tensor shape.
- [ ] I can explain padding, causal, and packed-document masks.
- [ ] I can compare encoder-only, decoder-only, and encoder-decoder models.
- [ ] I understand positional encoding, RoPE, and relative-position intuition.
- [ ] I can distinguish training, prefill, and decode.
- [ ] I can estimate the drivers of KV-cache memory.
- [ ] I can compare MHA, MQA, GQA, FlashAttention, sparse attention, and MoE.
- [ ] I can discuss long-context failure modes rather than quoting context length.
- [ ] I can debug label shifting, masks, tokenizer mismatch, repetition, and capability regression.
- [ ] I can make an architecture decision using quality, latency, memory, cost, license, and risk.

## Primary references

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- [RoFormer: Enhanced Transformer with Rotary Position Embedding](https://arxiv.org/abs/2104.09864)
- [FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness](https://arxiv.org/abs/2205.14135)
- [Mamba: Linear-Time Sequence Modeling with Selective State Spaces](https://arxiv.org/abs/2312.00752)
- [PyTorch scaled dot-product attention documentation](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html)
- [Hugging Face Transformers documentation](https://huggingface.co/docs/transformers/)
