---
layout: "week"
status: "review"
version: "0.1.0"
last_reviewed: "2026-11-10"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "LLM inference and serving optimization interview cheat sheet"
description: "TTFT, TPOT, prefill, decode, GPU and KV-cache memory, batching, caching, quantization, parallelism, benchmarking, and autoscaling."
summary: "Revise latency decomposition, memory and capacity estimates, serving-engine choices, workload-aware optimization, goodput, and production rollout."
permalink: "/interview-prep/cheat-sheets/llm-inference-serving-optimization/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 5 · Inference optimization"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 5 source:** This review candidate integrates the prepared revision artifact into the Prep site. It is separate from the Week 1–20 learning assessments.

**Target roles:** AI/ML Engineer, LLM Inference Engineer, GenAI Engineer, AI Platform Engineer, Senior/Lead Data Scientist  
**Use:** latency/throughput tuning, GPU memory estimation, serving-engine selection, capacity, autoscaling, and production rollout  
**Interview rule:** optimize a measured production bottleneck against quality and SLOs. A faster isolated kernel or higher GPU utilization does not prove better user-level goodput.

## 1. Thirty-second revision

- Pin model revision, tokenizer/chat template, dtype/quantization, engine/version, hardware, generation defaults, and workload before benchmarking.
- Decompose latency into admission/queue, tokenization, **prefill**, **decode**, post-processing, and delivery.
- Prefill processes input tokens and is commonly compute-intensive; decode generates tokens autoregressively and is commonly memory-bandwidth/KV-cache sensitive.
- Track end-to-end latency, time to first token (TTFT), inter-token latency/time per output token (ITL/TPOT), throughput, and **goodput within SLO**.
- Model weights, KV cache, activations/workspace, runtime graphs/kernels, adapters, fragmentation, and safety margin all consume memory.
- Continuous batching and paged KV-cache management increase utilization under mixed arrivals; tuning batch/token limits trades TTFT, TPOT, and throughput.
- Prefix caching helps only with repeated stable prefixes and correct version/tenant isolation.
- Quantization saves memory/bandwidth but needs compatibility and task-quality validation.
- Tensor/pipeline/data/expert/context parallelism solve different fit/scale problems and add communication.
- Use bounded queues, admission control, cancellation, warm-up, readiness, drain, and progressive rollout around the engine.

## 2. Bind the exact benchmark candidate

Record:

- model family, exact revision/digest, architecture, parameter count;
- tokenizer, vocabulary, special tokens, chat template, max context;
- adapters and multimodal encoders;
- weight, activation, and KV-cache precision/quantization;
- engine, framework/compiler/kernels, container, CUDA/driver;
- GPU type/count/memory/interconnect plus CPU/RAM/storage/network;
- API schema and generation parameters;
- warm versus cold state;
- dataset and arrival/input/output distributions.

Changing the chat template can change token length and quality; changing output limits can make a “faster” result incomplete.

## 3. Workload contract

Characterize distributions, not one average:

| Dimension | Examples |
|---|---|
| Request class | chat, extraction, coding, long-document, embedding, reranking |
| Arrival | steady, bursty, diurnal, batch |
| Input | p50/p95/max prompt tokens, repeated prefixes |
| Output | p50/p95/max generated tokens, early-stop behavior |
| Concurrency | active, queued, tenant/priority mix |
| Streaming | required TTFT and token cadence |
| Quality | task score, structured/tool success, numerical tolerance |
| SLO | p95 TTFT/E2E, availability, goodput, cost |

Load generators should reproduce request-rate and token-length correlations. Fixed concurrency and open-loop arrival-rate tests answer different questions.

## 4. Inference path

1. gateway/routing and admission;
2. queue wait;
3. parsing and tokenization;
4. model scheduling and batch formation;
5. prefill/encoder processing;
6. iterative decode;
7. detokenization, schema/guardrail processing;
8. streaming/network delivery;
9. application retrieval/tools where present.

Instrument each stage. A slow request can be queue-bound even when model execution is fast.

## 5. Core latency and throughput metrics

### Time to first token

$$
TTFT = t_{first\ token} - t_{request\ accepted}
$$

It includes queue and prefill unless you report stage-specific values.

### Inter-token latency / time per output token

For $N$ output tokens:

$$
TPOT \approx \frac{t_{last\ token}-t_{first\ token}}{N-1}
$$

### End-to-end latency

$$
E2E = t_{completed} - t_{request\ accepted}
$$

### Throughput and goodput

- request throughput: completed requests/second;
- token throughput: input or output tokens/second;
- goodput: requests/tokens completed **within accepted SLO and quality constraints**.

Report p50/p95/p99 by request class. A throughput number without input/output lengths and quality is not comparable.

## 6. Prefill versus decode

### Prefill

- processes the prompt in parallel;
- creates KV cache;
- workload grows strongly with prompt length;
- often benefits from larger token batches and compute throughput.

### Decode

- produces one/few next tokens per sequence per iteration;
- repeatedly reads weights and KV cache;
- often memory-bandwidth bound for small batches;
- latency-sensitive for interactive streaming.

Mixing long prefills with decodes can hurt token cadence. Chunked prefill divides long prompts and schedules them alongside decode work; the best token budget depends on the workload and engine.

## 7. Weight-memory estimate

For $P$ parameters at $b$ bits per stored parameter:

$$
M_{weights} \approx \frac{P b}{8}
$$

This is a lower bound. Add quantization scales/metadata, tied/untied heads, adapters, runtime/allocator overhead, kernels/graphs, activations/workspaces, and fragmentation.

Example: a 7-billion-parameter model at 16 bits has a raw weight lower bound near 14 GB; it does not safely fit a 16 GB GPU once runtime memory is included.

## 8. KV-cache memory

For a decoder with:

- $L$ layers;
- $H_{kv}$ key/value heads;
- head dimension $D$;
- $B_e$ bytes per KV element;
- $T$ total cached tokens across active sequences;

$$
M_{KV} \approx 2 \times L \times H_{kv} \times D \times B_e \times T
$$

The factor 2 is for keys and values.

```python
from __future__ import annotations


def kv_cache_gib(
    *,
    layers: int,
    kv_heads: int,
    head_dim: int,
    bytes_per_element: int,
    total_cached_tokens: int,
) -> float:
    values = (layers, kv_heads, head_dim, bytes_per_element, total_cached_tokens)
    if any(value <= 0 for value in values):
        raise ValueError("all inputs must be positive")
    bytes_used = (
        2
        * layers
        * kv_heads
        * head_dim
        * bytes_per_element
        * total_cached_tokens
    )
    return bytes_used / (1024**3)
```

MHA typically has $H_{kv}=H_q$; GQA uses fewer KV heads; MQA commonly uses one. This is why GQA/MQA reduce KV memory. Parallel sharding and engine layout change per-GPU memory—verify actual engine metrics.

## 9. Capacity intuition

If one sequence can reach $C$ tokens, an unsafe upper-bound concurrency estimate is:

$$
N \lesssim \frac{M_{available\ KV}}{M_{KV\ per\ max\ sequence}}
$$

Real traffic has mixed lengths and early completion, while paging, fragmentation, preemption, batching, and safety margin matter. Treat theoretical capacity as feasibility, then run controlled load until SLO or memory limits are reached.

## 10. Continuous batching and scheduling

Static batching waits for a fixed batch and finishes it together. Continuous/in-flight batching can add/remove sequences at decode iterations, improving utilization for variable-length requests.

Tune:

- maximum concurrent sequences;
- maximum batched tokens;
- scheduler policy and priority;
- prefill chunk size;
- queue delay/admission;
- preemption/recompute policy;
- fairness across tenants and long/short requests.

Larger batches can raise throughput but also queue/TTFT and KV pressure. Optimize goodput, not maximum batch size.

## 11. Paged KV-cache management

PagedAttention-style systems manage KV cache in blocks/pages rather than requiring one large contiguous allocation per sequence. Benefits can include reduced fragmentation, flexible growth, and sharing/reuse features.

Monitor:

- allocated/free blocks;
- KV utilization and eviction;
- preemption/recompute;
- rejected sequences;
- fragmentation/allocator failures;
- cache reuse.

Paging does not remove the physical memory limit.

## 12. Prefix/prompt caching

Prefix caching reuses KV computation for a matching prompt prefix, useful for:

- long stable system prompts;
- shared document/context prefixes;
- repeated few-shot examples;
- multi-turn flows that preserve exact prefixes.

Define key semantics including model/tokenizer/template/adapters/precision and exact token sequence. Control tenant scope, TTL, memory, eviction, invalidation, and observability.

It will not help highly unique prompts. A configured cache can add memory/coordination overhead without hits.

## 13. Quantization

| Method | Main benefit | Main concern |
|---|---|---|
| BF16/FP16 | broad quality/compatibility baseline | high memory/bandwidth |
| FP8 | lower memory and faster supported kernels | hardware/engine/model compatibility |
| INT8 | weight/activation or KV savings depending method | calibration and kernel support |
| INT4 | large weight-memory/bandwidth reduction | quality loss and conversion/kernel choices |
| KV quantization | increases context/concurrency capacity | long-context/task quality and support |

Quantization can make a model fit without making it faster if dequantization or unoptimized kernels dominate. Compare quality, memory, TTFT, TPOT, throughput, startup, and stability.

## 14. Speculative decoding

A draft method proposes multiple tokens; the target model verifies them. It helps when accepted-token savings exceed draft/verification overhead.

Options include a smaller draft model, n-gram/prompt lookup, or model-specific multi-token heads/approaches.

Measure:

- acceptance length/rate;
- draft and verification cost;
- TPOT and end-to-end change;
- extra memory;
- batch/concurrency impact;
- exact output or quality behavior under the engine’s method.

Low acceptance, short outputs, or an expensive draft can make it slower.

## 15. Parallelism strategies

| Strategy | What is divided/replicated | Use |
|---|---|---|
| Tensor parallelism | tensors/layers across accelerators | one model does not fit or faster single-request compute |
| Pipeline parallelism | layer stages | very large/multi-node models; adds bubbles/latency |
| Data parallelism | model replicas | throughput and horizontal scaling |
| Expert parallelism | MoE experts | distribute expert weights/compute |
| Context/sequence parallelism | long-sequence work/cache | very long context and supported architectures |

Communication topology matters: PCIe versus high-bandwidth links and cross-node network can dominate. More GPUs may reduce cost efficiency.

## 16. Prefill–decode disaggregation

Separate prefill and decode workers can scale compute-heavy prompt processing independently from bandwidth/KV-heavy generation. Potential benefits:

- hardware specialization;
- independent scaling;
- reduced interference;
- better routing by request shape.

Costs include KV transfer, network latency, routing/state complexity, failure recovery, and capacity imbalance. It is not automatically beneficial for small deployments.

## 17. Serving-engine and platform map

| Tool | Primary use | Important note |
|---|---|---|
| vLLM | high-throughput LLM engine/server | PagedAttention, continuous batching, broad optimization/distributed surface |
| SGLang | performance-oriented LLM/VLM runtime | strong structured generation and cache/execution optimizations; verify pinned support |
| llama.cpp | portable local/edge CPU/GPU inference | broad quantized local deployment; different throughput goals |
| Ollama | local model workflow/API | developer convenience; benchmark its underlying runtime/config |
| TensorRT-LLM | NVIDIA-optimized LLM runtime | engine/build/hardware-specific optimization |
| Triton Inference Server | multi-backend serving platform | model repository, scheduling, metrics, ensembles/backends |
| NVIDIA NIM | packaged model inference microservice | validated profiles and packaged runtime; license/support/hardware checks |
| Ray Serve LLM | distributed serving/orchestration | multi-node/model, autoscaling/routing around engines |
| KServe | Kubernetes model-serving control/data plane | runtimes, routing, rollout, autoscaling integration |
| BentoML | package/build/serve AI services | Python service composition and container/Kubernetes paths |

Hugging Face TGI remains relevant in existing systems but is officially in maintenance mode; current Hugging Face guidance recommends vLLM or SGLang for new optimized endpoint choices.

## 18. OpenAI-compatible does not mean identical

Compatibility varies across:

- endpoints and request fields;
- chat templates and reasoning/tool parsers;
- structured output and JSON schema behavior;
- logprobs, seeds, batching, cancellation, and streaming;
- error/status codes and token accounting;
- multimodal inputs and model-specific parameters.

Use contract tests against every engine/model route.

## 19. Benchmark design

1. freeze candidate, workload, hardware, and quality set;
2. warm model/kernels/caches explicitly, while measuring cold start separately;
3. test request-rate and concurrency sweeps;
4. include p50/p95/max input/output distributions and bursts;
5. record rejections, OOMs, cancellations, and timeouts;
6. repeat trials and report variability;
7. measure server and client timestamps;
8. verify output quality, schema, tool calling, and stop behavior;
9. run stress, spike, soak, and recovery tests;
10. calculate cost per accepted request/token/outcome.

Microbenchmarks cannot establish service capacity.

## 20. Autoscaling and production behavior

Useful signals include:

- queued/waiting requests or token backlog;
- TTFT and queue time;
- active sequences and KV-cache pressure;
- goodput/SLO breach rate;
- engine utilization and preemption;
- arrival-rate forecast.

GPU utilization alone may stay high while queues explode. Scaling is delayed by GPU scheduling, image/model download, load, compilation, and warm-up. Keep minimum warm capacity or accept cold-start latency.

Production essentials:

- startup/liveness/readiness probes with model warm-up;
- graceful drain and streaming cancellation;
- bounded queues and 429/503 overload contracts;
- per-tenant quotas/fairness;
- retry-storm protection;
- failure-domain-aware replicas;
- model artifact/cache strategy;
- exact image/model/config rollout and rollback.

## 21. Common interview traps

- Comparing requests/second without token lengths.
- Treating p50 as the SLO.
- Fitting raw weights exactly into GPU memory.
- Calling KV cache “model memory” without context/concurrency assumptions.
- Copying vLLM flags from another version/model/GPU.
- Assuming prefix caching helps unique prompts.
- Assuming INT4 is always faster or quality-equivalent.
- Adding GPUs without measuring communication and scaling efficiency.
- Autoscaling only on CPU/GPU utilization.
- Excluding rejected, timed-out, or OOM requests from results.

## 22. Rapid interview questions

**Q1. TTFT versus TPOT?**  
TTFT measures delay until the first streamed token; TPOT/ITL measures generation cadence after the first token.

**Q2. Why is decode often memory-bound?**  
Each step produces little work per sequence while repeatedly reading large weights and growing KV cache.

**Q3. How does GQA reduce memory?**  
Several query heads share fewer key/value heads, reducing KV elements per token.

**Q4. Continuous batching benefit?**  
It admits and retires variable-length sequences during decoding, improving utilization under live traffic.

**Q5. When does prefix caching fail to help?**  
When prefixes rarely match, versions differ, or cache coordination/memory costs exceed saved prefill compute.

**Q6. Tensor versus data parallelism?**  
Tensor parallelism shards one model execution; data parallelism replicates the model to serve more work.

**Q7. What is goodput?**  
The throughput that meets the accepted latency and quality contract, not all completed work.

**Q8. How do you size serving capacity?**  
Estimate model/KV fit, benchmark per-replica goodput across production-like distributions, then apply peak/failure headroom and validate with load/fault tests.

## 23. Lead-level design case

**Prompt:** Serve a 30B-class model for 500 concurrent enterprise users with mixed 1K–32K prompts and streaming responses.

A strong answer should:

1. clarify arrival rate, active concurrency, output distribution, TTFT/TPOT SLO, quality, residency, and budget;
2. pin model architecture/precision and compute weight/KV lower bounds;
3. benchmark candidate GPUs, quantizations, and engine versions;
4. segment interactive short and long-context traffic or use priority/chunked prefill;
5. choose parallelism from model fit and topology, then measure scaling efficiency;
6. set continuous-batching/admission/token limits using SLO sweeps;
7. use prefix caching only for measured repeated tenant-safe prefixes;
8. size replicas from goodput plus burst/failure headroom;
9. autoscale on queue/token/KV/SLO signals with warm capacity;
10. canary exact model/engine/config with quality, OOM, tail latency, and cost abort gates.

## 24. Final checklist

- [ ] I can separate queue, prefill, decode, and delivery latency.
- [ ] I can explain TTFT, TPOT/ITL, throughput, and goodput.
- [ ] I can estimate weight and KV-cache memory and state limitations.
- [ ] I understand continuous batching, paging, chunked prefill, and prefix caching.
- [ ] I can compare quantization, speculation, and parallelism with quality gates.
- [ ] I recognize engine versus platform responsibilities and current lifecycle notices.
- [ ] I can design reproducible load/quality/cost benchmarks.
- [ ] I cover admission, autoscaling, warm-up, drain, monitoring, rollout, and rollback.

## 25. Primary references

- vLLM, [Official documentation](https://docs.vllm.ai/en/stable/)
- vLLM, [Optimization and tuning](https://docs.vllm.ai/en/latest/configuration/optimization/)
- SGLang, [Official documentation](https://docs.sglang.ai/)
- Hugging Face, [Text Generation Inference](https://huggingface.co/docs/text-generation-inference/en/index)
- NVIDIA, [TensorRT-LLM documentation](https://nvidia.github.io/TensorRT-LLM/)
- NVIDIA, [Triton Inference Server](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/)
- Ray, [Serve LLM](https://docs.ray.io/en/latest/serve/llm/index.html)
- KServe, [Generative inference](https://kserve.github.io/website/docs/model-serving/generative-inference/overview)
- NVIDIA, [NIM for LLMs](https://docs.nvidia.com/nim/large-language-models/latest/)

Inference features and defaults are version-sensitive. Pin the complete candidate and re-benchmark after model, engine, driver, GPU, or workload changes.
