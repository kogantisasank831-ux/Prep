---
layout: "week"
status: "approved"
version: "1.1.0"
last_reviewed: "2026-11-13"
header_context: "Interview cheat sheets"
back_label: "Roadmap"
back_url: "/#roadmap"
toc_heading: "Cheat-sheet batches"
pagination_label: "Roadmap overview"
pagination_url: "/#roadmap"
title: "AI and Data Science interview cheat sheets"
description: "Forty concise revision guides for AI Engineer, Agentic AI Engineer, ML Engineer, Senior Data Scientist, and Data Science Technical Lead interviews."
summary: "Move from core Python, SQL, statistics, and ML through GenAI, agents, production platforms, specialized modeling, and end-to-end architecture."
permalink: "/cheat-sheets/"
kicker_primary: "Quick revision"
kicker_secondary: "40 sheets · 10 batches"
current_label: "Cheat sheets hub"
---
## How to use this collection

Choose one topic, complete its thirty-second revision from memory, then work through the decision tables, failure modes, rapid questions, and lead-level case. The collection serves AI Engineer, Agentic AI Engineer, ML Engineer, Senior Data Scientist, Applied Scientist, and Data Science Technical Lead interviews.

These 40 canonical Markdown sheets come from [`AI_Data_Science_Interview_Cheat_Sheets`](https://github.com/kogantisasank831-ux/transformer-explainer/tree/cdd45b6b0c08c5d88a626e4d16853abdf285f08d/AI_Data_Science_Interview_Cheat_Sheets) at source commit `cdd45b6b0c08c5d88a626e4d16853abdf285f08d`. Prep renders them in its reading layout and keeps the original technical content intact.

<section class="cheat-sheet-tools" data-cheat-sheet-tools hidden aria-labelledby="cheat-sheet-tools-title">
  <div class="cheat-sheet-tools-heading">
    <p class="cheat-sheet-tools-label">Revision workspace</p>
    <h3 id="cheat-sheet-tools-title">Find and track cheat sheets</h3>
    <p>Search all 40 sheets, narrow the collection by topic or revision state, and keep your progress on this browser.</p>
  </div>
  <form class="cheat-sheet-filters" data-cheat-sheet-filters role="search">
    <label class="cheat-sheet-field" for="cheat-sheet-search">
      <span>Search titles and focus areas</span>
      <input id="cheat-sheet-search" type="search" autocomplete="off" placeholder="Try RAG, SQL, security, or Kubernetes">
    </label>
    <label class="cheat-sheet-field" for="cheat-sheet-batch">
      <span>Topic or batch</span>
      <select id="cheat-sheet-batch">
        <option value="all">All topics · 10 batches</option>
        <option value="1">Batch 1 · Core foundations</option>
        <option value="2">Batch 2 · Deep learning and GenAI</option>
        <option value="3">Batch 3 · RAG and search</option>
        <option value="4">Batch 4 · Agent systems</option>
        <option value="5">Batch 5 · Production AI</option>
        <option value="6">Batch 6 · Data, security, and leadership</option>
        <option value="7">Batch 7 · Modeling and decision science</option>
        <option value="8">Batch 8 · Advanced modeling and assurance</option>
        <option value="9">Batch 9 · Specialized modeling</option>
        <option value="10">Batch 10 · AI engineering platform</option>
      </select>
    </label>
    <label class="cheat-sheet-field" for="cheat-sheet-progress-filter">
      <span>Revision state</span>
      <select id="cheat-sheet-progress-filter">
        <option value="all">All sheets</option>
        <option value="incomplete">Not revised</option>
        <option value="complete">Revised</option>
      </select>
    </label>
    <button class="cheat-sheet-button" id="clear-cheat-sheet-filters" type="button">Clear filters</button>
  </form>
  <div class="cheat-sheet-progress-card" aria-labelledby="cheat-sheet-progress-title">
    <div>
      <p class="cheat-sheet-tools-label">Your revision progress</p>
      <p class="cheat-sheet-progress-title" id="cheat-sheet-progress-title">0 of 40 revised</p>
      <p class="cheat-sheet-progress-note" id="cheat-sheet-progress-note">Saved only on this browser and device.</p>
    </div>
    <progress id="cheat-sheet-progress" value="0" max="40" aria-describedby="cheat-sheet-progress-note">0 of 40 revised</progress>
    <button class="cheat-sheet-button cheat-sheet-reset" id="reset-cheat-sheet-progress" type="button" disabled>Reset revision progress</button>
  </div>
  <p class="cheat-sheet-filter-status" id="cheat-sheet-filter-status" role="status" aria-live="polite">Showing all 40 cheat sheets.</p>
  <p class="cheat-sheet-empty" id="cheat-sheet-empty" hidden>No cheat sheets match these filters. Change the search or clear the filters.</p>
</section>

## Batch 1 — Core foundations

| Sheet | Focus |
| --- | --- |
| [01 · Python]({{ '/interview-prep/cheat-sheets/python/' | relative_url }}) | Language semantics, data structures, concurrency, APIs, testing, and production practice |
| [02 · SQL]({{ '/interview-prep/cheat-sheets/sql/' | relative_url }}) | Query correctness, analytical patterns, data modeling, transactions, and optimization |
| [03 · Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }}) | Probability, estimation, inference, power, experiments, and causal interpretation |
| [04 · Machine-learning fundamentals]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) | Framing, algorithms, validation, metrics, leakage, deployment, and monitoring |

## Batch 2 — Deep learning and GenAI

| Sheet | Focus |
| --- | --- |
| [05 · Deep learning and neural networks]({{ '/interview-prep/cheat-sheets/deep-learning-neural-networks/' | relative_url }}) | Backpropagation, losses, optimization, regularization, architectures, and training failures |
| [06 · Natural language processing]({{ '/interview-prep/cheat-sheets/nlp/' | relative_url }}) | Text pipelines, representations, modeling, multilingual systems, and evaluation |
| [07 · Transformers]({{ '/interview-prep/cheat-sheets/transformers/' | relative_url }}) | Attention, masks, position, architecture families, KV cache, MQA/GQA, and efficiency |
| [08 · LLM and Generative AI]({{ '/interview-prep/cheat-sheets/llm-generative-ai/' | relative_url }}) | Generation, prompting, structured output, fine-tuning, evaluation, safety, and serving |

## Batch 3 — RAG and search

| Sheet | Focus |
| --- | --- |
| [09 · Embeddings and vector search]({{ '/interview-prep/cheat-sheets/embeddings-vector-search/' | relative_url }}) | Sparse, dense, and hybrid retrieval, similarity, ANN, reranking, and filtering |
| [10 · Document ingestion, chunking, and indexing]({{ '/interview-prep/cheat-sheets/document-ingestion-chunking-indexing/' | relative_url }}) | Parsing, provenance, chunking, idempotency, updates, deletion, and backfills |
| [11 · RAG architecture, retrieval, and generation]({{ '/interview-prep/cheat-sheets/rag-architecture-retrieval-generation/' | relative_url }}) | Query transformation, staged retrieval, context assembly, citations, and abstention |
| [12 · RAG evaluation, security, and production]({{ '/interview-prep/cheat-sheets/rag-evaluation-security-production/' | relative_url }}) | Quality metrics, release gates, injection defenses, observability, SLOs, and incidents |

## Batch 4 — Agent systems

| Sheet | Focus |
| --- | --- |
| [13 · Agent fundamentals and workflow patterns]({{ '/interview-prep/cheat-sheets/agent-fundamentals-workflow-patterns/' | relative_url }}) | Boundaries, tools, state, memory, routing, multi-agent patterns, budgets, and approvals |
| [14 · LangGraph deep dive]({{ '/interview-prep/cheat-sheets/langgraph-deep-dive/' | relative_url }}) | Typed state, reducers, routing, fan-out, persistence, interrupts, replay, and caching |
| [15 · Agent frameworks and libraries]({{ '/interview-prep/cheat-sheets/agent-frameworks-libraries-comparison/' | relative_url }}) | Framework selection across orchestration, retrieval, model gateways, and evaluation |
| [16 · Agent protocols, reliability, security, and evaluation]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }}) | MCP, A2A, identity, retries, resilience, trajectory evaluation, and release gates |

## Batch 5 — Production AI

| Sheet | Focus |
| --- | --- |
| [17 · AI/ML system design and production architecture]({{ '/interview-prep/cheat-sheets/ai-ml-system-design-production-architecture/' | relative_url }}) | Requirements, metrics, capacity, planes, storage, queues, tenancy, security, and rollout |
| [18 · LLM inference and serving optimization]({{ '/interview-prep/cheat-sheets/llm-inference-serving-optimization/' | relative_url }}) | TTFT/TPOT, prefill/decode, memory, batching, caching, quantization, and autoscaling |
| [19 · MLOps, LLMOps, deployment, and lifecycle]({{ '/interview-prep/cheat-sheets/mlops-llmops-deployment-lifecycle/' | relative_url }}) | Lineage, registries, CI/CD/CT, model/prompt/index lifecycle, release, and rollback |
| [20 · AI production monitoring, cost, and capacity]({{ '/interview-prep/cheat-sheets/ai-production-monitoring-cost-capacity/' | relative_url }}) | SLOs, drift, delayed labels, GenAI monitoring, telemetry, capacity, and FinOps |

## Batch 6 — Data, security, and leadership

| Sheet | Focus |
| --- | --- |
| [21 · Data and distributed compute engineering]({{ '/interview-prep/cheat-sheets/data-distributed-compute-engineering/' | relative_url }}) | Partitions, shuffles, skew, storage, streaming, backfills, and distributed training |
| [22 · AI security, privacy, and governance]({{ '/interview-prep/cheat-sheets/ai-security-privacy-governance/' | relative_url }}) | Threat modeling, prompt injection, privacy, supply chain, red teaming, and incidents |
| [23 · AI technical leadership and product thinking]({{ '/interview-prep/cheat-sheets/ai-technical-leadership-product-thinking/' | relative_url }}) | Framing, metric trees, roadmaps, build-versus-buy, team leadership, and delivery |
| [24 · Project deep dives, behavioral answers, and mocks]({{ '/interview-prep/cheat-sheets/project-deep-dive-behavioral-mock-interview/' | relative_url }}) | Project defense, truthful ownership, impact, behavioral stories, cases, and scoring |

## Batch 7 — Modeling and decision science

| Sheet | Focus |
| --- | --- |
| [25 · Experimentation and causal inference]({{ '/interview-prep/cheat-sheets/experimentation-causal-inference/' | relative_url }}) | Estimands, power, telemetry, variance reduction, sequential tests, DAGs, and uplift |
| [26 · Feature engineering and ML data validation]({{ '/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/' | relative_url }}) | Data identity, leakage-safe splits, point-in-time features, quality gates, and parity |
| [27 · Time series and forecasting]({{ '/interview-prep/cheat-sheets/time-series-forecasting/' | relative_url }}) | Forecast contracts, baselines, models, rolling evaluation, uncertainty, and hierarchy |
| [28 · Recommendation, search, and ranking]({{ '/interview-prep/cheat-sheets/recommendation-search-ranking/' | relative_url }}) | Candidate generation, ranking, exposure, offline/online metrics, and cold start |

## Batch 8 — Advanced modeling and model assurance

| Sheet | Focus |
| --- | --- |
| [29 · Linear algebra, calculus, and optimization]({{ '/interview-prep/cheat-sheets/linear-algebra-calculus-optimization/' | relative_url }}) | Geometry, rank, eigen/SVD/PCA, gradients, optimizers, constraints, and stability |
| [30 · Unsupervised learning and dimensionality reduction]({{ '/interview-prep/cheat-sheets/unsupervised-learning-dimensionality-reduction/' | relative_url }}) | Clustering, mixtures, density methods, PCA, t-SNE/UMAP, stability, and production |
| [31 · Anomaly detection and rare-event modeling]({{ '/interview-prep/cheat-sheets/anomaly-detection-rare-event-modeling/' | relative_url }}) | Detection contracts, robust and learned methods, calibration, metrics, and alerts |
| [32 · Explainability, fairness, uncertainty, and governance]({{ '/interview-prep/cheat-sheets/explainability-fairness-uncertainty-model-governance/' | relative_url }}) | Explanations, calibration, conformal coverage, fairness, evidence, and release gates |

## Batch 9 — Specialized modeling

| Sheet | Focus |
| --- | --- |
| [33 · Computer vision and multimodal AI]({{ '/interview-prep/cheat-sheets/computer-vision-multimodal-ai/' | relative_url }}) | CNNs, ViTs, detection, segmentation, OCR, video, multimodal evaluation, and safety |
| [34 · Graph machine learning and GNNs]({{ '/interview-prep/cheat-sheets/graph-machine-learning-gnn/' | relative_url }}) | Graph construction, structural baselines, message passing, evaluation, and scale |
| [35 · Survival analysis and reliability modeling]({{ '/interview-prep/cheat-sheets/survival-analysis-reliability-modeling/' | relative_url }}) | Censoring, KM, Cox/AFT, competing risks, maintenance decisions, and monitoring |
| [36 · Operations research, scheduling, and optimization]({{ '/interview-prep/cheat-sheets/operations-research-scheduling-optimization/' | relative_url }}) | LP, MILP, CP-SAT, scheduling, routing, uncertainty, feasibility, and fallback |

## Batch 10 — AI engineering platform

| Sheet | Focus |
| --- | --- |
| [37 · AI backend, API, and async-service engineering]({{ '/interview-prep/cheat-sheets/ai-backend-api-async-service-engineering/' | relative_url }}) | APIs, concurrency, queues, idempotency, backpressure, transactions, and recovery |
| [38 · Cloud, Kubernetes, and GPU platform engineering]({{ '/interview-prep/cheat-sheets/cloud-kubernetes-gpu-platform-engineering/' | relative_url }}) | Containers, Kubernetes, GPU scheduling, serving platforms, autoscaling, and cost |
| [39 · AI testing, release quality, and evaluation]({{ '/interview-prep/cheat-sheets/ai-testing-release-quality-engineering/' | relative_url }}) | Deterministic tests, model/RAG/agent evaluation, security, load, canary, and rollback |
| [40 · End-to-end AI architecture and mock interviews]({{ '/interview-prep/cheat-sheets/end-to-end-ai-architecture-mock-interview/' | relative_url }}) | Timed requirements, capacity math, architecture, lifecycle, operations, and leadership |

## Revision standard

For every topic, be able to explain the intuition, assumptions, trade-offs, failure modes, evaluation method, and one production use case. For senior and lead roles, add business impact, risk, architecture decisions, rollout, monitoring, and rollback.
