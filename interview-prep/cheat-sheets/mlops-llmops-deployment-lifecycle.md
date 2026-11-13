---
layout: "week"
status: "approved"
version: "1.0.1"
last_reviewed: "2026-11-13"
header_context: "Interview cheat sheets"
back_label: "Cheat sheets"
back_url: "/cheat-sheets/"
toc_heading: "Cheat-sheet sections"
pagination_label: "Cheat sheets hub"
pagination_url: "/cheat-sheets/"
title: "MLOps, LLMOps, deployment, and lifecycle interview cheat sheet"
description: "Reproducibility, lineage, registries, CI/CD/CT, prompt and index lifecycle, containers, Kubernetes, deployment strategies, rollback, and retirement."
summary: "Revise immutable AI release identity, lifecycle automation, validation gates, progressive deployment, monitoring, feedback governance, and recovery."
permalink: "/interview-prep/cheat-sheets/mlops-llmops-deployment-lifecycle/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 5 · MLOps and LLMOps"
current_label: "Revision guide"
alternate_label: "Cheat sheets hub"
alternate_url: "/cheat-sheets/"
---
> **Batch 5 source:** This page integrates the prepared revision artifact into the Prep site. It is separate from the Week 1–30 learning assessments.

**Target roles:** ML Engineer, AI Engineer, MLOps/LLMOps Engineer, GenAI Engineer, Senior Data Scientist, AI/ML Lead  
**Use:** reproducibility, pipelines, registries, CI/CD/CT, deployment, Kubernetes, lineage, rollback, and governance  
**Interview rule:** a deployed model is a versioned software-and-data product, not a single weight file. Reproduce and roll back the complete serving bundle.

## 1. Thirty-second revision

- MLOps applies software engineering, data engineering, model governance, deployment, and operations to the ML lifecycle.
- LLMOps extends this to prompts, model/provider APIs, retrieval indexes, evaluators, agents/tools, guardrails, tokens, and cost.
- Version code, data/labels/features, model/tokenizer/adapters, prompt/schema, index, tools/policies, dependencies, infrastructure, and evaluation set.
- Reproducibility requires exact inputs, environment, seeds where meaningful, deterministic limits, and retained artifacts—not merely a notebook.
- CI checks code/contracts/security; continuous delivery promotes accepted candidates; continuous training creates new candidates but should not auto-promote without gates.
- Use a registry for identity, lineage, evaluation, approval, aliases/stages, and retirement; an alias must resolve to an immutable version at runtime.
- Deployment strategies include shadow, canary, blue-green, rolling, and A/B; each answers a different question.
- Containers package dependencies; Kubernetes schedules and operates them; model-serving platforms add inference-specific control/data-plane features.
- Validate data, model, prompt, RAG, agent, service, load, recovery, and security behavior before promotion.
- Monitor the exact release, retain rapid rollback/kill switches, and govern feedback loops to prevent poisoning and evaluation leakage.

## 2. Lifecycle map

1. define problem, outcome, risk, and acceptance;
2. collect/version data, labels, documents, and feedback;
3. validate and transform features/corpus;
4. train/fine-tune or configure model/prompt/retrieval/agent;
5. evaluate quality, safety, robustness, performance, and cost;
6. package candidate and record lineage;
7. approve and deploy progressively;
8. monitor service and real outcomes;
9. retrain/reconfigure, roll back, or retire;
10. preserve audit evidence and deletion/retention requirements.

Automation makes this repeatable; it does not remove accountable approval.

## 3. Complete release identity

| Layer | Identity to retain |
|---|---|
| Source | commit SHA, build workflow, dependency lock |
| Runtime | image digest, OS, Python/runtime, CUDA/driver compatibility |
| Model | artifact digest/revision, tokenizer/template, adapters, dtype/quantization |
| Data | source snapshot, schema, transformations, label version |
| Classical ML | feature definitions and online/offline materialization |
| GenAI | prompt/examples/schema, generation defaults, provider-resolved model |
| RAG | corpus manifest, parser/chunker, embedding, index, reranker, ACL policy |
| Agent | graph, tools/contracts, memory/policy, MCP/A2A server versions |
| Evaluation | dataset/rubric/judge versions and thresholds |
| Deployment | environment, infrastructure/config/secret references, cohort/flags |

Do not log secret values. Store immutable identifiers and authorized references.

## 4. Release manifest pattern

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReleaseManifest:
    source_commit: str
    image_digest: str
    model_revision: str
    tokenizer_revision: str
    prompt_version: str
    data_or_index_version: str
    evaluation_suite_version: str
    runtime_config_digest: str

    def validate(self) -> None:
        values = vars(self)
        missing = [name for name, value in values.items() if not value.strip()]
        if missing:
            raise ValueError(f"missing release identity: {', '.join(missing)}")
        if not self.image_digest.startswith("sha256:"):
            raise ValueError("image_digest must be immutable")
```

Production manifests may include signatures, SBOM/provenance, approvals, compatibility, deployment target, and rollback reference.

## 5. Reproducible experimentation and training

Record:

- hypothesis and metric definitions;
- dataset/query and exact snapshot/manifest;
- code/config/environment and hardware;
- preprocessing/feature/tokenization/template;
- initialization/checkpoint and random seeds;
- hyperparameters, optimizer/schedule, precision, distributed topology;
- logs, checkpoints, metrics by slice, failures, and cost;
- final artifact digest and evaluation result.

Deterministic seeds do not make GPU/distributed training fully deterministic. Record known nondeterminism and compare within tolerance.

## 6. Experiment tracking versus registry

### Experiment tracker

Captures runs, parameters, metrics, artifacts, and comparisons during development.

### Registry

Manages candidate identity, lineage, validation, approval, aliases/stages, deployment metadata, and retirement.

A tracker answers “what happened in this run?” A registry answers “which accepted artifact is eligible or deployed?” Tools such as MLflow may provide both, but the responsibilities remain distinct.

## 7. Data and feature operations

Validate:

- schema/type/range/category constraints;
- missingness, duplicates, volume, distribution, freshness;
- label leakage and point-in-time correctness;
- source/partition completeness;
- train/validation/test separation and entity overlap;
- transformations shared or equivalent between training and serving;
- backfill/replay behavior and deletion.

A feature store can help define, materialize, discover, and serve features consistently. It does not automatically prevent leakage or guarantee feature usefulness.

## 8. Pipeline design

Each stage should have:

- typed inputs/outputs and immutable artifact references;
- validation and acceptance criteria;
- idempotency and safe rerun behavior;
- caching keyed by exact inputs/version;
- resource requests and timeout;
- retry classification;
- lineage and logs;
- failure/partial-output cleanup;
- owner and notification.

Avoid one monolithic pipeline task. Boundaries should support recovery and diagnosis without producing inconsistent partial releases.

## 9. CI, CD, and CT

### Continuous integration

- formatting/lint/type/unit tests;
- schema and contract tests;
- data/transformation tests with controlled fixtures;
- model/prompt/RAG/agent regression suite;
- dependency, secret, container, and license/security checks;
- build reproducibility and artifact signing/provenance.

### Continuous delivery/deployment

- promote the exact tested artifact;
- environment policy/approval;
- infrastructure/config validation;
- smoke, integration, load, and security gates;
- progressive rollout, abort, rollback, and post-release verification.

### Continuous training

Creates a new candidate from approved triggers/data. It should not silently replace production because a pipeline completed.

## 10. Test pyramid for AI systems

| Test layer | Examples |
|---|---|
| Unit | feature transform, parser, route, reducer, validation |
| Data | schema, freshness, leakage, label rules, document manifest |
| Contract | API/event/tool/model server schema and compatibility |
| Integration | feature store, registry, index, model endpoint, queue |
| Model quality | frozen holdout, slices, calibration, robustness |
| GenAI evaluation | task, groundedness, citation, tool/agent trajectory, safety |
| Performance | load, stress, spike, soak, memory, cold/warm start |
| Recovery | crash/resume, duplicate delivery, dependency outage, rollback |
| Security | access control, prompt injection, artifact/supply-chain, secrets |

Deterministic checks should precede expensive model judges. Calibrate judge-based scores against human or deterministic labels.

## 11. Prompt and GenAI configuration management

A prompt release contains more than text:

- system/developer/user templates;
- variables and validation;
- few-shot examples;
- output schema and parser;
- model and generation defaults;
- tools and tool descriptions;
- guardrails/policies;
- evaluation dataset/rubric.

Use immutable versions and aliases, review diffs, run regression evaluation, and record which prompt version generated each trace. Do not edit a production prompt in place without lineage.

## 12. RAG index lifecycle

Version:

- source/corpus snapshot and permissions;
- parser/OCR/table extraction;
- cleaning, chunking, metadata;
- embedding model/dimension/normalization;
- vector/lexical index parameters;
- reranker and retrieval configuration.

Use a staged index build, completeness/quality checks, atomic alias or routing switch, canary queries, rollback to prior index, and asynchronous cleanup. Propagate document updates, revocation, and deletion to derived chunks, embeddings, caches, and backups per policy.

## 13. Agent and tool lifecycle

Track:

- graph/workflow and state schema;
- model/prompt per node;
- tool schemas and downstream versions;
- identity/authorization policy;
- checkpoints/memory schema;
- retry/budget/termination settings;
- MCP/A2A server capability versions;
- trajectory and side-effect evaluation.

Changing a tool description or schema can change agent behavior even when model weights are unchanged.

## 14. Packaging and containers

Container practices:

- pin base image and dependencies;
- use multi-stage builds and minimal runtime image;
- run as non-root with read-only filesystem where possible;
- separate model artifacts from application image when operationally useful;
- generate SBOM and scan/sign image/artifacts;
- avoid credentials in layers or environment dumps;
- define startup, health, signal handling, and graceful shutdown;
- set CPU/RAM/GPU requests/limits based on measurement.

Rebuilding the same tag can produce different bytes. Deploy immutable digests.

## 15. Kubernetes for AI workloads

Kubernetes provides scheduling and lifecycle primitives; it does not understand model quality.

Important concepts:

- Deployment/StatefulSet/Job/CronJob and services/ingress;
- resource requests/limits and GPU device scheduling;
- node selectors/affinity, taints/tolerations, topology and placement;
- ConfigMaps/secrets and service accounts/RBAC;
- startup, readiness, and liveness probes;
- graceful termination, pre-stop/draining, disruption budgets;
- HPA/KEDA/custom metrics and cluster autoscaling;
- persistent/object storage and artifact caches;
- network policies and observability.

For slow model startup, a startup probe should protect initialization; readiness should become true only after the model is loaded/warmed enough to accept traffic. Liveness should detect unrecoverable process health, not restart a merely busy server.

## 16. Serving platforms

| Platform | Main role |
|---|---|
| KServe | Kubernetes CRDs/control plane, inference runtimes, routing, autoscaling/rollout patterns |
| Ray Serve | Python-native distributed serving, composition, replicas/autoscaling, LLM orchestration |
| BentoML | package APIs/models into services and containers; compose model/application logic |
| Seldon | Kubernetes model deployment/operations ecosystem |
| Triton | high-performance multi-framework model server/data plane |
| vLLM/SGLang/TensorRT-LLM | LLM inference engines rather than complete platform lifecycle |

Choose only after testing language/runtime fit, multi-node behavior, rollout, observability, security, support, and operator complexity.

## 17. Deployment strategies

| Strategy | Best question | Limitation |
|---|---|---|
| Rolling | can healthy replicas replace old ones gradually? | versions coexist; rollback may take time |
| Blue-green | can traffic switch between complete environments? | duplicate capacity/data coordination |
| Canary | does candidate satisfy service/quality/safety on a small cohort? | needs routing and comparable cohorts |
| Shadow | how would candidate behave without affecting response? | doubles work; side effects must be disabled |
| A/B | which accepted variant improves product outcome? | experimentation design and user impact |

Canary is a release-risk control; A/B is a product experiment. Do not treat them as synonyms.

## 18. Rollback and forward recovery

Rollback requires:

- prior immutable artifact/config/index available;
- state/schema backward compatibility or migration plan;
- database/index changes that can coexist or be reversed;
- prompt/tool/policy version rollback;
- active-job/thread strategy;
- traffic switch and cache invalidation;
- post-rollback verification.

Sometimes forward-fix is safer, especially after irreversible data migrations or side effects. Decide before release.

## 19. Provider and model change management

Managed model aliases can resolve to new backend versions. Preserve requested and resolved identity when available.

Before switching model/provider:

- run contract/tool/schema tests;
- evaluate quality/safety slices;
- compare tokenization/context/output limits;
- load-test latency/rate limits and fallback;
- assess retention/residency/license/pricing;
- canary exact routes;
- update cost and incident runbooks.

“OpenAI-compatible” does not guarantee behavioral equivalence.

## 20. Monitoring and feedback loop

Monitor service, data, model, GenAI, safety, business, and cost signals tied to exact lineage. Join delayed outcomes without rewriting original predictions.

Feedback entering training, prompts, retrieval, or memory needs:

- provenance and consent;
- deduplication and abuse resistance;
- privacy/retention;
- quality review and disagreement handling;
- quarantine after incidents;
- train/eval leakage prevention;
- reproducible dataset version.

Do not train automatically on every user correction or model-generated trace.

## 21. Governance and retirement

Maintain model/data/system cards or equivalent records covering intended/excluded use, evaluation, limitations, owners, approvals, and monitoring.

Retirement includes:

- remove traffic and dependencies;
- cancel schedules and credentials;
- archive/delete artifacts/data according to policy;
- preserve required audit evidence;
- update documentation and ownership;
- verify no active caller still depends on the version.

## 22. Common interview traps

- Saying Git plus Docker alone provides reproducibility.
- Versioning weights but not tokenizer, prompt, features, or index.
- Letting continuous training auto-promote without gates.
- Mutating “production” aliases without resolving immutable IDs in traces.
- Using liveness to restart a model during normal long initialization.
- Treating passing unit tests as model acceptance.
- Shadowing a side-effecting agent without disabling writes.
- Calling canary and A/B the same.
- Assuming rollback works without state/schema compatibility.
- Feeding production logs directly back into training.

## 23. Rapid interview questions

**Q1. MLOps versus LLMOps?**  
LLMOps adds prompt/model-provider, retrieval, trace/evaluator, token/cost, and agent/tool lifecycle concerns to core MLOps.

**Q2. Experiment tracker versus model registry?**  
The tracker records development runs; the registry governs candidate identity, lineage, approval, deployment, and retirement.

**Q3. CI versus continuous training?**  
CI validates changes; continuous training produces new model candidates from approved data/triggers. Neither automatically authorizes production promotion.

**Q4. Why image digest rather than tag?**  
Tags can be moved or rebuilt; a digest identifies immutable bytes.

**Q5. Readiness versus liveness?**  
Readiness controls traffic eligibility; liveness determines whether the container should be restarted.

**Q6. Why version a RAG index?**  
Retrieval behavior depends on corpus, extraction, chunking, embeddings, metadata/ACLs, index, and reranker—not just the generator.

**Q7. Canary versus shadow?**  
Canary responses affect a small cohort; shadow results are compared without affecting the user path or performing side effects.

**Q8. What is continuous delivery’s key rule?**  
Promote the exact tested candidate through controlled environments with retained gates and rollback.

## 24. Lead-level design case

**Prompt:** Design the delivery lifecycle for a RAG and agent platform used by several enterprise teams.

A strong answer should:

1. define platform versus product-team responsibilities and tenancy;
2. create an immutable release manifest covering code, model, prompt, index, graph, tools, policies, and evaluation;
3. provide reusable CI templates and isolated environments;
4. version corpus/index builds with ACL/deletion tests and atomic promotion;
5. enforce deterministic, model-quality, trajectory, safety, load, and recovery gates;
6. package workloads in signed/scanned images and deploy by digest;
7. use shadow/canary with side effects disabled or idempotently fenced;
8. maintain fast rollback for model/prompt/index/tool changes;
9. correlate production outcomes/cost to exact versions;
10. govern feedback, incidents, access, retention, and retirement.

## 25. Final checklist

- [ ] I can describe the complete ML/LLM lifecycle and release bundle.
- [ ] I can make training/evaluation reproducible within stated limits.
- [ ] I distinguish experiment tracking, registry, CI, CD, and CT.
- [ ] I cover prompt, RAG index, and agent/tool lifecycle.
- [ ] I understand container and Kubernetes production primitives.
- [ ] I can compare serving engines and serving platforms.
- [ ] I can choose and explain shadow, canary, blue-green, rolling, and A/B.
- [ ] I plan monitoring, feedback governance, rollback, incident response, and retirement.

## 26. Primary references

- MLflow, [MLflow documentation](https://mlflow.org/docs/latest/)
- MLflow, [Agents and LLMs](https://mlflow.org/docs/latest/genai/)
- Kubernetes, [Concepts](https://kubernetes.io/docs/concepts/)
- Kubernetes, [Liveness, readiness, and startup probes](https://kubernetes.io/docs/concepts/workloads/pods/probes/)
- KServe, [Official documentation](https://kserve.github.io/website/docs/intro)
- Ray, [Ray Serve](https://docs.ray.io/en/latest/serve/)
- BentoML, [Official documentation](https://docs.bentoml.com/en/latest/)
- Feast, [Feature store documentation](https://docs.feast.dev/)
- OpenLineage, [Official documentation](https://openlineage.io/docs/)
- SLSA, [Supply-chain levels for software artifacts](https://slsa.dev/)

Tool features and defaults change. Pin versions, preserve immutable candidate identity, and validate the actual CI and deployment environment.
