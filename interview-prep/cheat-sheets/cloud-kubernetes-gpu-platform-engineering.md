---
layout: "week"
status: "approved"
version: "1.0.0"
last_reviewed: "2026-11-11"
imported_on: "2026-11-13"
source_repository: "kogantisasank831-ux/transformer-explainer"
source_commit: "cdd45b6b0c08c5d88a626e4d16853abdf285f08d"
source_path: "AI_Data_Science_Interview_Cheat_Sheets/Batch_10_AI_Engineering_Platform/38_Cloud_Kubernetes_GPU_Platform_Engineering_Cheat_Sheet.md"
header_context: "Interview cheat sheets"
back_label: "Cheat sheets"
back_url: "/cheat-sheets/"
toc_heading: "Cheat-sheet sections"
pagination_label: "Cheat sheets hub"
pagination_url: "/cheat-sheets/"
title: "Cloud, Kubernetes, and GPU platform engineering interview cheat sheet"
description: "Interview revision for containers, Kubernetes, GPU scheduling, AI serving platforms, autoscaling, reliability, security, and cost."
summary: "Revise containers, Kubernetes reconciliation and scheduling, GPU stacks and memory, AI serving platforms, token-aware autoscaling, distributed training, security, and cost."
permalink: "/interview-prep/cheat-sheets/cloud-kubernetes-gpu-platform-engineering/"
kicker_primary: "Interview revision"
kicker_secondary: "Batch 10 · AI platform"
current_label: "Revision guide"
alternate_label: "Cheat sheets hub"
alternate_url: "/cheat-sheets/"
---

**Target roles:** AI Engineer, ML Platform Engineer, MLOps Engineer, Senior/Lead Data Scientist, AI Platform Lead<br>
**Use:** cloud and Kubernetes rounds, GPU serving/training design, capacity and cost cases, production readiness reviews<br>
**Interview rule:** begin with workload shape, SLO, accelerator need, security boundary, release identity, and failure domains. Kubernetes and GPUs are implementation choices, not the requirement.

## 1. Thirty-second revision

- A container image packages user space; it does not contain a kernel or guarantee portability across CPU architecture, accelerator driver, or runtime ABI.
- Kubernetes reconciles declared state through controllers. A Pod is replaceable; a Deployment manages stateless replicas; StatefulSet adds stable identity; Job/CronJob manages finite work.
- Requests drive scheduling and capacity planning; limits constrain runtime usage. Poor requests cause pending Pods, contention, throttling, or wasted nodes.
- Readiness determines traffic eligibility, startup protects slow initialization, and liveness detects a stuck process. Incorrect liveness can restart a healthy model during load.
- A GPU device plugin advertises extended resources such as `nvidia.com/gpu`. Scheduling a GPU does not install a compatible driver/runtime or prove the model fits memory.
- GPU memory capacity, compute utilization, memory bandwidth, tensor-core support, interconnect, CPU/RAM, storage, and network can each bottleneck.
- MIG partitions supported GPUs into isolated instances; time slicing shares access without equivalent memory/fault isolation; MPS is a CUDA process-sharing mechanism. Benchmark and threat-model the chosen mode.
- Autoscale on the constraint closest to user pain: concurrency/queue age, waiting requests, token backlog, or KV-cache pressure can be more useful than CPU for LLM serving.
- Scale-to-zero saves idle cost but adds image pull, node provisioning, model download/load, and cache-warm latency. Keep warm capacity when the SLO requires it.
- Distributed training needs correct world size/ranks, collective communication, checkpoint/restart, deterministic data sharding, and failure-aware orchestration.
- Cloud security uses least privilege, workload identity, network/egress control, encryption, signed/scanned artifacts, and audit logs—not credentials baked into images.
- Reliability requires multiple replicas/failure domains, disruption budgets, graceful draining, health checks, progressive delivery, tested rollback, and recovery of state outside Pods.

## 2. Platform requirement contract

State:

> Run **workload W** with **artifact A**, on **hardware/runtime H**, for **traffic or job distribution L**, meeting **SLO S** and **risk policy P**, at **cost boundary C**, with **release/rollback R**.

Ask:

- online inference, asynchronous inference, batch scoring, training, fine-tuning, notebook, or data processing;
- requests/tokens/jobs per second, burst, concurrency, sequence/input distribution, batchability, and seasonality;
- latency to first/complete result, throughput, availability, deadline, checkpoint interval, and recovery objective;
- model weights, precision/quantization, KV cache, activations, workspace, replicas, and parallelism;
- GPU class/features, VRAM, CPU, RAM, local/object/shared storage, network bandwidth, and interconnect;
- single tenant, trusted multi-tenant, or adversarial users;
- region, residency, availability zones, egress, quotas, and supply constraints;
- image/model/data/prompt/config identity and promotion policy;
- baseline, expected utilization, cost per valid result, and fallback.

Do not request “a GPU” generically. A T4, L4, A100, H100, and newer accelerators differ in memory, supported precision, bandwidth, compute capability, power, partitioning, and price.

## 3. Containers and supply chain

### Image fundamentals

- Build reproducibly from a pinned base image digest when possible.
- Use multi-stage builds to exclude compilers and caches from runtime.
- Run as a non-root user; prefer read-only root filesystem and drop Linux capabilities.
- Keep model weights separate when lifecycle/size demands it, but verify their digest and access policy.
- Use `.dockerignore`, no embedded secrets, minimal packages, and explicit entrypoint/signals.
- Generate an SBOM, scan dependencies and image, record provenance/signature, and define remediation ownership.
- Test CPU architecture and CUDA/driver compatibility on target nodes.

Image tags are mutable labels. A release identity should resolve image digest, model digest/revision, tokenizer, runtime, configuration, prompt/index/tool policy, and infrastructure manifest.

### Runtime lifecycle

The process should:

1. validate required configuration;
2. initialize telemetry and clients;
3. load/warm the artifact under a startup probe;
4. become ready only when it can serve;
5. stop accepting work on termination;
6. drain/cancel/checkpoint inside the grace period;
7. close clients and emit a final state.

## 4. Kubernetes mental model and objects

Kubernetes stores desired state in an API. Controllers continuously reconcile actual state; the scheduler binds pending Pods to nodes; kubelet manages containers on a node.

| Object | Use | Common interview trap |
|---|---|---|
| Pod | smallest scheduled unit | not a durable machine or stable database identity |
| Deployment | stateless replicas and rollout | rollout success does not prove model quality |
| StatefulSet | stable identity/storage ordering | not automatically a highly available database |
| Job/CronJob | finite/scheduled work | retries require idempotent task effects |
| Service | stable virtual endpoint | does not make the backend ready or secure |
| Ingress/Gateway | external routing/TLS policy | proxy/body/stream timeout can break AI responses |
| ConfigMap/Secret | injected configuration | Kubernetes Secret needs encryption/RBAC policy |
| PVC | storage claim | access modes, zone binding, throughput, backup still matter |
| HPA | replica scaling from metrics | cannot create GPU nodes or eliminate cold start |
| PDB | voluntary-disruption availability | does not protect from node crash or bad release |

### Scheduling and placement

- **Resource requests:** scheduler reservation for CPU, memory, GPU, and extended resources.
- **Limits:** runtime ceiling where enforced; CPU may throttle, memory may cause OOM kill.
- **Node selector/affinity:** choose hardware, zone, or topology.
- **Taints/tolerations:** keep general workloads off scarce accelerator nodes; toleration alone does not select them.
- **Pod anti-affinity/topology spread:** reduce correlated replica loss.
- **Priority/preemption:** protect important work, with explicit fairness policy.
- **Quota/limit ranges:** prevent one namespace or tenant from consuming the cluster.

Pending Pods are a signal to inspect events, resource fit, affinity/taints, PVC zones, quotas, and cluster-autoscaler capability—not to restart them.

## 5. Probes and rollout behavior

- **Startup probe:** suppresses readiness/liveness during slow model initialization.
- **Readiness probe:** removes an instance from traffic while keeping it running.
- **Liveness probe:** restarts a process that cannot recover internally.

Probe an inexpensive local capability. A liveness check that fails whenever a remote database is slow can restart all replicas and amplify the outage.

For a rollout:

- pre-pull large images or account for pull time;
- use `maxUnavailable`/`maxSurge` consistent with capacity;
- ensure old and new schemas/contracts coexist;
- warm model/KV/prefix caches as appropriate;
- canary by traffic and tenant risk;
- gate on service, model, safety, cost, and business metrics;
- drain streaming/in-flight requests;
- retain the exact previous release and rollback path.

## 6. GPU stack and scheduling

The simplified stack is:

`GPU hardware → host driver → container runtime/toolkit → CUDA/runtime libraries → framework/kernel → model server → application`

Compatibility must be verified across every layer. A container can include CUDA user-space libraries but relies on a compatible host driver.

Kubernetes device plugins register vendor resources. A Pod typically requests an extended GPU resource; use node labels/affinity for GPU type and supported features. Extended resources are not overcommitted by default.

### Memory accounting

For inference, estimate:

`VRAM ≈ weights + KV cache + activations/workspace + runtime/graph buffers + fragmentation/headroom`

For training, include parameters, gradients, optimizer states, activations, communication buffers, temporary kernels, and framework overhead. Quantization may reduce weights while KV cache or activations remain dominant.

Monitor:

- allocated and used VRAM;
- GPU compute and memory-controller utilization;
- power/temperature/throttling;
- request/token throughput and queueing;
- batch size and padding;
- OOM/restarts/ECC or hardware errors;
- CPU preprocessing, host-to-device transfer, storage, and network.

High GPU utilization is not itself success; relate it to SLO and valid output. Low utilization can result from small batches, CPU/tokenization waits, network stalls, memory-bound kernels, or fragmentation.

### Sharing choices

| Mode | What it does | Main caveat |
|---|---|---|
| Exclusive GPU | one allocation uses a device | simplest isolation, possible low utilization |
| MIG | hardware partitions supported NVIDIA GPUs into instances | fixed profiles/operational reconfiguration; support is GPU-specific |
| Time slicing | multiplexes full-GPU access | no equivalent dedicated memory/fault isolation |
| CUDA MPS | lets CUDA processes share GPU execution resources | compatibility, isolation, QoS, and memory behavior require testing |
| Application/model multiplexing | one server hosts/batches models/adapters | a bad model or memory spike can affect co-tenants |

Use separate trust domains for hostile tenants unless the selected technology provides the required isolation. Measure latency fairness, OOM blast radius, and noisy-neighbor behavior.

## 7. Model-serving platform choices

| Need | Options to evaluate | Key question |
|---|---|---|
| Optimized framework serving | NVIDIA Triton, TensorFlow Serving, ONNX Runtime server patterns | supported backends, batching, model repository, metrics |
| LLM engine | vLLM, TensorRT-LLM, TGI, llama.cpp/Ollama for smaller/local uses | model/hardware support, scheduler, KV cache, API, quantization |
| Kubernetes model abstraction | KServe, Seldon ecosystem | CRDs, ingress, autoscaling, storage, upgrade burden |
| Python composition | Ray Serve, BentoML | arbitrary graph/business logic, scaling unit, cluster operations |
| Cloud managed service | provider model/ML endpoints | control, portability, compliance, quotas, unit economics |

Do not compare brand names alone. Benchmark exact model/runtime/config on representative input/output lengths and concurrency. Check active maintenance, licenses, security posture, API compatibility, upgrade path, and observability.

Dynamic/continuous batching trades a short scheduling wait for throughput. Tune maximum batch/tokens and delay against tail latency. Stateful sequence models and LLM decode require scheduler behavior different from stateless tensor inference.

## 8. Autoscaling and capacity

### Little's Law intuition

For a stable system:

`average in-flight work ≈ arrival rate × average time in system`

If 20 requests/s take 0.5 s on average, about 10 are in flight—before burst and tail headroom. For LLMs, request count hides token variation; use prefill/decode/token backlog and KV-cache pressure.

### Executable replica estimate

```python
import math


def required_replicas(
    arrival_rate_per_second: float,
    sustainable_rate_per_replica: float,
    *,
    target_utilization: float = 0.70,
    headroom_fraction: float = 0.20,
) -> int:
    if arrival_rate_per_second < 0:
        raise ValueError("arrival rate cannot be negative")
    if sustainable_rate_per_replica <= 0:
        raise ValueError("replica rate must be positive")
    if not 0 < target_utilization <= 1:
        raise ValueError("target utilization must be in (0, 1]")
    if headroom_fraction < 0:
        raise ValueError("headroom cannot be negative")

    planned_rate = arrival_rate_per_second * (1 + headroom_fraction)
    safe_rate = sustainable_rate_per_replica * target_utilization
    return max(1, math.ceil(planned_rate / safe_rate))


assert required_replicas(40, 10, target_utilization=0.8, headroom_fraction=0.2) == 6
assert required_replicas(0, 10) == 1
```

The input rate must come from a representative benchmark at the target SLO—not theoretical FLOPS. Add failure-domain redundancy, batch effects, warm-up, and node availability.

### Scaling layers

- HPA changes Pod replicas from CPU/memory/custom/external metrics.
- KEDA activates/scales workloads from event sources and external metrics.
- A serving-layer autoscaler may use queue or ongoing requests.
- Cluster autoscaler/provisioner creates/removes nodes when Pods cannot be placed.
- Cloud capacity/quota determines whether a requested GPU node can actually appear.

These loops have different delays and can oscillate. Define min/max, stabilization/cooldowns, rate limits, fallback metrics, and warm capacity. Scale on queue age/latency as well as depth when deadlines matter.

## 9. Distributed training and batch workloads

### Data parallel training

Each rank holds a model replica, processes a different mini-batch shard, and synchronizes gradients through collectives. Effective global batch is approximately:

`per-device batch × data-parallel workers × gradient-accumulation steps`

Changing world size can change optimization behavior. Record seeds, sampler epoch/state, precision, optimizer/scheduler, code, data snapshot, and environment.

For models that do not fit, evaluate parameter/optimizer sharding, tensor parallelism, pipeline parallelism, activation checkpointing, offload, and quantization—with communication and complexity costs.

Production considerations:

- NCCL/network topology and interface selection;
- rendezvous and rank membership;
- local versus shared/object checkpoint storage;
- frequent atomic checkpoints with manifest and integrity;
- preemption/spot interruption;
- straggler and node/GPU failure;
- deterministic data ownership and no duplicated/skipped samples;
- elastic restart policy and maximum wasted compute.

Jobs must be restartable from a validated checkpoint. A completed Kubernetes Job does not prove the model artifact was registered, evaluated, or promotable.

## 10. Storage, network, identity, and secrets

### Storage

- **Object:** durable artifacts/datasets/checkpoints; high throughput but different semantics from POSIX.
- **Block/PVC:** low-latency mounted volume, often zone-bound and single-writer.
- **Shared filesystem:** convenient distributed access; metadata and aggregate throughput can bottleneck.
- **Local NVMe:** fast cache/scratch; ephemeral and node-specific.

Design caching, integrity, versioning, lifecycle, backup, and restore. Thousands of small files can overwhelm metadata; shard/package formats appropriately.

### Network

Plan ingress limits, streaming timeouts, service discovery, DNS, cross-zone cost, egress control, network policy, TLS/mTLS policy, load balancing, and collective bandwidth. Avoid downloading multi-gigabyte weights for every restart when a safe node/model cache is justified.

### Identity

Use workload identity bound to service accounts instead of static cloud keys. Grant the smallest object prefix, queue, secret, and API permissions. Rotate secrets and audit access. Separate deployment permission from model promotion and production-data access.

## 11. Reliability and disaster recovery

- Spread replicas across nodes/zones when the dependency and budget support it.
- Use PDBs for voluntary disruption but maintain spare capacity.
- Define regional dependency failure and data-recovery behavior.
- Back up source-of-truth metadata/configuration and verify restoration; caches and derived indexes may be rebuilt if lineage is complete.
- Run failure drills: Pod kill, node drain, GPU failure, object-store delay, broker outage, bad model, expired credential, quota exhaustion.
- Maintain a CPU/smaller-model/provider/manual fallback only when its quality, security, and contract are approved.
- Record RTO/RPO for stateful components and maximum acceptable queued work loss.

## 12. Cost and capacity

Measure cost per accepted, valid business result—not only GPU-hour. Include idle/warm capacity, failed/retried work, storage, network egress, control plane, observability, support, and engineering operations.

Optimize in order:

1. remove unnecessary calls/work;
2. right-size model and sequence length;
3. batch/cache safely;
4. improve kernels/precision/runtime;
5. right-size replicas and sharing;
6. use committed/spot capacity where recovery permits;
7. revisit managed versus self-hosted total cost.

Underprovisioning creates queueing, retries, timeouts, and lost trust; “100% utilization” is not automatically cost optimal.

## 13. Failure modes and debugging

| Symptom | Likely causes | Evidence |
|---|---|---|
| Pod pending | no GPU fit, taint/affinity, quota, PVC zone | scheduler events, node allocatable, quota |
| CrashLoop/OOMKilled | model/kv/workspace memory, bad probe/config | termination reason, VRAM/RAM, startup logs |
| Ready but errors | shallow readiness, bad dependency/config | synthetic inference, trace, release identity |
| Tail latency spikes | batching wait, queue, cold Pod/node, noisy neighbor | queue age, batch, startup, per-tenant traces |
| HPA does nothing | wrong/missing metric, max reached, no node | HPA status/events, metrics adapter, pending Pods |
| GPU low utilization | CPU/tokenization/storage wait, small batches | profiles, batch size, CPU/network/storage metrics |
| Distributed job hangs | rank failure, network/NCCL mismatch | rank logs, topology, collective timeout |
| Rollout stalls | insufficient surge GPU capacity, startup probe | deployment events, node supply, model load time |

## 14. Rapid interview questions

**1. Request versus limit?**<br>
The scheduler uses requests to place Pods; limits constrain runtime where supported. Both must follow measured workload behavior.

**2. Why can a liveness probe cause an outage?**<br>
If it depends on an unhealthy remote service or model load is slow, Kubernetes may restart every otherwise recoverable replica.

**3. HPA versus cluster autoscaler?**<br>
HPA changes workload replicas. Cluster autoscaling changes nodes so unschedulable Pods can run. Their control loops and delays differ.

**4. Why is CPU a weak LLM autoscaling metric?**<br>
GPU scheduling, tokens, waiting requests, KV cache, and sequence lengths often dominate while CPU stays moderate.

**5. MIG versus time slicing?**<br>
MIG creates hardware-partitioned instances on supported GPUs; time slicing multiplexes access to a GPU without equivalent memory/fault isolation.

**6. What makes scale-to-zero risky?**<br>
Node launch, image pull, model download, load, compilation, and warm-up can exceed the first caller's deadline.

**7. Why can a Pod request a GPU yet fail at startup?**<br>
The GPU type, VRAM, driver/runtime/framework compatibility, model files, or additional host resources may not satisfy it.

**8. What should be immutable in an AI release?**<br>
Resolvable digests/revisions for code image, model/tokenizer, configuration, prompt/index/tool policy, evaluation evidence, and deployment manifest.

## 15. Lead-level case: self-hosted LLM platform

**Prompt:** Build an internal OpenAI-compatible LLM platform for ten teams with interactive and batch traffic.

Strong answer:

1. Segment workload by model, input/output tokens, concurrency, streaming, latency class, region, sensitivity, and budget.
2. Benchmark candidate model/runtime/precision on target GPUs; measure TTFT, inter-token latency, throughput, quality, OOM, and cost.
3. Put authenticated gateway/admission in front; enforce tenant token/rate/concurrency/spend quotas and approved model aliases.
4. Use separate pools for interactive and batch or priority-aware bounded scheduling; avoid batch starvation of interactive work.
5. Deploy engine replicas with startup/readiness, model cache, topology constraints, PDB, graceful draining, and exact release identity.
6. Autoscale on waiting requests/token backlog/KV pressure with warm minima; coordinate Pod and node provisioning.
7. Protect weights, prompts, traces, and endpoints with workload identity, egress policy, encryption, audit, and tenant-safe caches.
8. Evaluate model and system releases on frozen/challenge sets, load, security, and failure tests; canary and retain rollback.
9. Track per-tenant quality proxy, availability, TTFT, completion latency, tokens, queue age, GPU memory/utilization, error and cost.
10. Define approved provider/smaller-model/manual fallback, capacity reservation, region failure, quota exhaustion, and incident ownership.

## 16. Final checklist

- [ ] Workload, SLO, scale, data class, release identity, and cost unit are explicit.
- [ ] Image is minimal, non-root, scanned, signed/provenanced, and digest-pinned.
- [ ] Requests/limits, placement, quota, probes, draining, PDB, and topology are measured.
- [ ] GPU type, VRAM, precision, runtime, driver, sharing, and isolation are verified.
- [ ] Serving benchmark uses representative token/input/output and concurrency distributions.
- [ ] Autoscaling metric reflects the actual bottleneck; warm-up and node delay are modeled.
- [ ] Training has deterministic sharding, collectives, checkpoints, restart, and artifact registration.
- [ ] Storage, network, workload identity, secrets, tenant isolation, and egress are controlled.
- [ ] Canary, model/system gates, rollback, backup/restore, and failure drills exist.
- [ ] Capacity and cost include headroom, failures, idle time, observability, and operations.

## Primary references

- [Kubernetes documentation — Resource Management for Pods and Containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Kubernetes documentation — Configure Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Kubernetes documentation — Schedule GPUs](https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/)
- [Kubernetes documentation — Horizontal Pod Autoscaling](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/)
- [NVIDIA GPU Operator documentation](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/)
- [NVIDIA Multi-Instance GPU User Guide](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/)
- [KEDA documentation — Scaling Deployments, StatefulSets and Custom Resources](https://keda.sh/docs/latest/concepts/scaling-deployments/)
- [KServe documentation](https://kserve.github.io/website/docs/)
- [Ray Serve documentation](https://docs.ray.io/en/latest/serve/)
- [NVIDIA Triton documentation — Batchers](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/batcher.html)
- [PyTorch documentation — Distributed Data Parallel](https://docs.pytorch.org/docs/stable/generated/torch.nn.parallel.DistributedDataParallel.html)
- [Google SRE Book — Production Services Best Practices](https://sre.google/sre-book/service-best-practices/)

**Evidence boundary:** manifests and formulas are planning aids. Only pinned-hardware benchmarks, integration/load tests, security review, failure drills, and observed canary behavior establish fitness for a specific production workload.
