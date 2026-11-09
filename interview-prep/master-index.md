---
layout: "week"
status: "review"
version: "0.1.0"
last_reviewed: "2026-11-09"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "AI and Data Science interview master index"
description: "A role-prioritized syllabus for AI Engineer, Agentic AI Engineer, Senior Data Scientist, and Data Science Technical Lead interviews."
summary: "Use this index to decide what to revise, how deeply to learn it, and which interview rounds require each topic."
permalink: "/interview-prep/master-index/"
kicker_primary: "Interview preparation"
kicker_secondary: "Master syllabus"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 1 source:** This page integrates the previously prepared revision artifact into the Prep site. It is separate from the Week 1–20 learning assessments.

**Purpose:** a comprehensive syllabus for building short, reusable cheat sheets for AI Engineer, Senior/Lead Data Scientist, Applied Scientist, ML Engineer, and Agentic AI Engineer interviews.

**Current as of:** 8 November 2026  
**Scope:** Python, SQL, statistics, machine learning, deep learning, neural networks, NLP, transformers, generative AI, RAG, agents, system design, MLOps, AI security, leadership, and the current library ecosystem.

> No finite list can cover every company or domain. This index covers the recurring topics found across current senior AI/ML job descriptions and the major interview formats. Domain-specific roles may add forecasting, recommendations, computer vision, risk, optimization, or causal inference.

## 1. How to use this index

### Priority

- **P0 — Must know:** common screening or core interview material.
- **P1 — Strong working knowledge:** frequently tested in senior technical and design rounds.
- **P2 — Role/specialization dependent:** learn deeply when it appears in the job description or your projects.

### Expected depth

For every P0 topic, be able to:

1. explain it in plain language;
2. give the intuition and essential formula or pseudocode;
3. state assumptions and trade-offs;
4. choose when to use or avoid it;
5. identify common failure modes;
6. implement or debug a small example;
7. connect it to a production or business use case.

For a lead role, add: architecture decisions, business impact, team guidance, risk management, and how you would measure success after launch.

## 2. Role emphasis matrix

| Area | AI Engineer | Lead Data Scientist | Typical interview evidence |
|---|---:|---:|---|
| Python and software engineering | High | Medium–High | Coding, debugging, API and code-design round |
| SQL and data manipulation | Medium–High | High | Live SQL, analytics case, data-quality reasoning |
| Probability and statistics | Medium | High | Theory, derivation, experiment or case round |
| Classical ML | High | High | Model selection, metrics, debugging, case study |
| Experimentation and causal inference | Medium | High | A/B test and product-decision cases |
| Deep learning | High | Medium–High | Architecture, training, debugging |
| LLM, RAG, and agents | High | Medium–High to High | Design, implementation, evaluation |
| Backend and distributed systems | High | Medium | Production/system-design round |
| MLOps and model lifecycle | High | High | End-to-end design and operational scenarios |
| Product and business framing | Medium–High | High | Ambiguous case and stakeholder round |
| Technical leadership | High for senior roles | Very high | Roadmap, mentoring, conflict, prioritization |
| Research depth | Role dependent | Role dependent | Paper discussion, model derivation, experiments |

## 3. Common interview round types

- **Recruiter/hiring-manager screen:** role fit, project impact, ownership, communication.
- **Python coding:** data structures, algorithms, clean code, testing, complexity.
- **SQL/data round:** joins, windows, cohorts, funnels, debugging and optimization.
- **Statistics/ML fundamentals:** assumptions, derivations, model and metric choice.
- **Modeling case:** frame an ambiguous problem, build a baseline, validate, deploy, monitor.
- **Deep learning/LLM round:** architecture, training, fine-tuning, inference and failure modes.
- **RAG/agent round:** retrieval, tools, memory, workflow, evaluation, safety and reliability.
- **ML/AI system design:** scale, latency, data, serving, observability, cost and rollback.
- **Product/experimentation case:** metrics, A/B tests, causal reasoning and business action.
- **Leadership/behavioral:** influence, mentoring, prioritization, disagreements and incidents.
- **Project deep dive:** defend your own decisions with numbers, alternatives and lessons.

---

# Part A — Coding, data, mathematics and statistics

## 4. Python and computer-science foundations

### P0 topics

- Data types; mutability; references; shallow versus deep copy.
- Lists, tuples, dictionaries, sets, strings and comprehensions.
- Functions, scope, closures, lambda functions and argument passing.
- Iterators, iterables, generators and lazy evaluation.
- Classes, inheritance, composition, dataclasses and abstract interfaces.
- Exceptions, resource cleanup and context managers.
- Type hints, protocols, generics, Pydantic models and validation.
- Time and space complexity; Big-O analysis.
- Arrays, hash maps, stacks, queues, heaps and linked lists.
- Sorting, binary search, two pointers, sliding window and prefix sums.
- Trees, graphs, BFS, DFS, topological sort and shortest-path intuition.
- Recursion, memoization and basic dynamic programming.
- Unit testing, mocking, fixtures, parameterization and test boundaries.
- Logging, configuration, packaging, dependency management and virtual environments.
- Clean code: separation of concerns, dependency injection, SOLID as practical guidance.

### P1 topics

- Threading, multiprocessing, the GIL and async/await.
- Race conditions, locks, queues, backpressure and cancellation.
- Serialization: JSON, Pickle risks, Parquet, Arrow and Protobuf.
- Memory profiling, vectorization and performance debugging.
- REST APIs, FastAPI, authentication basics, pagination and error contracts.
- Git workflows, CI, code review, linting, formatting and static type checking.
- Design patterns commonly used in AI services: strategy, adapter, factory, repository.

### Typical questions

- Implement an LRU cache, top-K calculation, batcher, retry decorator or rate limiter.
- Explain generator versus list, process versus thread, sync versus async.
- Refactor a notebook into tested production code.
- Diagnose memory growth, blocked coroutines, duplicate work or a flaky test.

## 5. SQL, databases and analytical data modeling

### P0 topics

- SELECT, WHERE, CASE, GROUP BY, HAVING, ORDER BY and NULL semantics.
- INNER/LEFT/RIGHT/FULL/CROSS joins; semi-joins and anti-joins.
- UNION versus UNION ALL; INTERSECT and EXCEPT.
- Subqueries, correlated subqueries and common table expressions.
- Window functions: ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD, FIRST/LAST_VALUE.
- Window frames; rolling and cumulative calculations.
- Conditional aggregation, pivots, deduplication and top-N per group.
- Date/time operations and time-zone handling.
- Cohorts, retention, funnels, sessions, consecutive events and gaps-and-islands.
- Query correctness under duplicates, missing values and one-to-many joins.
- Primary/foreign keys, constraints and normalization basics.
- Fact/dimension tables, star schemas and metric definitions.

### P1 topics

- Query plans, indexes, partitioning, clustering and predicate pushdown.
- Join strategies, data skew, materialized views and incremental processing.
- Transactions, ACID, isolation levels, locks and optimistic concurrency.
- Slowly changing dimensions, event models and point-in-time correct joins.
- OLTP versus OLAP; row versus column stores.
- SQL versus document, key-value, wide-column, graph and vector databases.
- Data contracts, schema evolution, lineage and data-quality checks.

### Typical questions

- Find the second/latest event, longest streak, seven-day retention or conversion funnel.
- Explain why a join inflated a metric.
- Design a data model for experiments, recommendations, an LLM trace store or feature history.
- Optimize a slow query without changing its result.

## 6. Linear algebra, calculus and optimization

### P0 topics

- Scalars, vectors, matrices and tensors; shape and broadcasting.
- Dot products, matrix multiplication, norms and distances.
- Linear independence, rank, basis, projections and orthogonality.
- Eigenvalues/eigenvectors, covariance matrices and principal components.
- SVD and its relationship to PCA, compression and latent factors.
- Derivatives, partial derivatives, gradients, Jacobians and the chain rule.
- Gradient descent, stochastic and mini-batch gradient descent.
- Convex versus non-convex optimization; local minima and saddle points.
- L1 and L2 regularization and their geometric intuition.

### P1 topics

- Hessians and second-order intuition.
- Momentum, Adam/AdamW, learning-rate schedules and warm-up.
- Constrained optimization and Lagrange multipliers.
- Numerical stability: log-sum-exp, overflow/underflow and conditioning.

## 7. Probability and statistics

### P0 topics

- Random variables; PMF, PDF and CDF.
- Joint, marginal and conditional probability; Bayes' theorem.
- Independence versus conditional independence.
- Expectation, variance, covariance and correlation.
- Bernoulli, binomial, categorical, Poisson, uniform, normal and exponential distributions.
- Law of Large Numbers and Central Limit Theorem.
- Population versus sample; sampling bias and selection bias.
- Point estimation; bias, variance, consistency and efficiency.
- Maximum likelihood and MAP estimation.
- Confidence intervals and bootstrap methods.
- Null/alternative hypotheses, p-values, significance level and statistical power.
- Type I/II errors; effect size versus statistical significance.
- z-test, t-test, chi-square test, ANOVA and non-parametric alternatives.
- Multiple testing and false-discovery control.
- Pearson versus Spearman correlation; correlation is not causation.

### P1 topics

- Bayesian priors, posterior, credible intervals and posterior predictive checks.
- Likelihood-ratio tests and information criteria.
- Missing-data mechanisms: MCAR, MAR and MNAR.
- Robust statistics, outliers and heavy-tailed data.
- Monte Carlo simulation and importance-sampling intuition.

## 8. Experimentation and causal inference

### P0 topics

- Hypothesis, unit of randomization, treatment, control and guardrail metrics.
- Sample-size and power reasoning; minimum detectable effect.
- A/A and A/B tests; randomization and balance checks.
- Novelty, seasonality, interference, attrition and sample-ratio mismatch.
- One-sided versus two-sided tests; peeking and sequential testing.
- Practical versus statistical significance.
- Metric sensitivity, variance reduction and CUPED intuition.
- Simpson's paradox, survivorship bias and regression to the mean.
- Observational versus experimental evidence.
- Confounders, mediators, colliders and causal DAGs.

### P1/P2 topics

- Propensity scores, matching and inverse-probability weighting.
- Difference-in-differences, regression discontinuity and instrumental variables.
- Heterogeneous treatment effects, uplift modeling and causal forests.
- Quasi-experiments, switchback tests and geo experiments.
- Long-term effects, network effects and marketplace experiments.

---

# Part B — Data science and machine learning

## 9. Data preparation, EDA and feature engineering

### P0 topics

- Problem framing: target, unit of prediction, prediction horizon and action.
- Data collection, label definition and label-quality audits.
- Train/validation/test splitting; temporal, group and stratified splits.
- Leakage: target, future, train-test, preprocessing and entity leakage.
- Missing-value analysis and appropriate imputation.
- Duplicate detection, outliers and inconsistent units/categories.
- Scaling, normalization and transformations.
- Categorical encoding: one-hot, ordinal, frequency and target encoding with leakage control.
- Text, date/time, geographic, aggregate and interaction features.
- Feature selection: filter, wrapper and embedded approaches.
- Class imbalance: resampling, class weights, thresholding and appropriate metrics.
- Reproducible preprocessing pipelines and point-in-time correctness.

### P1 topics

- Feature stores and offline/online consistency.
- Data drift, concept drift, label drift and schema drift.
- Data validation and training-serving skew.
- Weak supervision, active learning and human labeling workflows.

## 10. Supervised machine learning

### P0 topics

- Baselines and when a simple rule is better than a model.
- Linear regression: assumptions, interpretation, residuals and regularization.
- Logistic regression: log-odds, decision boundary, calibration and regularization.
- k-nearest neighbors and the curse of dimensionality.
- Naive Bayes and conditional-independence assumption.
- Decision trees: splits, impurity, pruning and overfitting.
- Bagging and random forests; out-of-bag estimation.
- Boosting: AdaBoost and gradient boosting intuition.
- XGBoost, LightGBM and CatBoost: practical differences and tuning concepts.
- Support vector machines, margins and kernels.
- Bias-variance trade-off; underfitting versus overfitting.
- Hyperparameter search: grid, random, Bayesian and early stopping.
- Cross-validation: K-fold, stratified, grouped, nested and time-series.

### Evaluation P0

- Confusion matrix, accuracy, precision, recall, specificity and F1.
- ROC-AUC versus PR-AUC and when each misleads.
- Log loss, Brier score and probability calibration.
- Threshold selection based on costs and operational constraints.
- MAE, MSE, RMSE, RMSLE, MAPE limitations and quantile loss.
- Macro, micro and weighted averaging.
- Ranking metrics: Precision@K, Recall@K, MAP, MRR and NDCG.
- Confidence intervals, subgroup results and error analysis.

## 11. Unsupervised learning and anomaly detection

- **P0:** k-means, initialization, scaling and selecting K.
- **P0:** hierarchical clustering and linkage choices.
- **P0:** DBSCAN/HDBSCAN concepts and density-based clustering.
- **P1:** Gaussian mixture models and expectation-maximization.
- **P0:** PCA and explained variance.
- **P1:** t-SNE and UMAP as visualization tools, not proof of clusters.
- **P1:** isolation forest, one-class SVM, local outlier factor and autoencoders.
- **P1:** anomaly thresholds, scarce labels and alert-fatigue trade-offs.

## 12. Specialized modeling areas

### Time series and forecasting

- Trend, seasonality, cycles, stationarity and transformations.
- Autocorrelation, partial autocorrelation and lag features.
- Naive/seasonal baselines, moving averages and exponential smoothing.
- ARIMA/SARIMA concepts and residual diagnostics.
- Prophet-style decomposable models and their limits.
- Tree-based forecasting with lag/rolling features.
- Deep forecasting awareness: N-BEATS, DeepAR and Temporal Fusion Transformer.
- Rolling-origin backtesting, forecast horizons and leakage prevention.
- Prediction intervals, intermittent demand and hierarchical forecasting.

### Recommendation, search and ranking

- Popularity and content-based baselines.
- Collaborative filtering, matrix factorization and implicit feedback.
- Two-tower retrieval, candidate generation and ranking.
- Negative sampling, cold start and feedback loops.
- Pairwise/listwise losses and ranking metrics.
- Diversity, novelty, coverage and exploration/exploitation.

### Other role-dependent areas

- Computer vision: image preprocessing, CNNs, augmentation, transfer learning, detection, segmentation and vision transformers.
- Graph ML: graph concepts, node embeddings, message passing and GNN use cases.
- Survival analysis: censoring, Kaplan–Meier and Cox models.
- Optimization/operations research: linear/integer programming, constraints and solvers.
- Geospatial modeling, fraud, risk, pricing, demand, churn and lifetime value.

## 13. Explainability, fairness and model governance

- Global versus local explanation.
- Coefficients, feature importance and permutation importance.
- Partial dependence, ICE, SHAP and LIME limitations.
- Calibration, uncertainty and abstention.
- Subgroup performance, fairness definitions and unavoidable trade-offs.
- Dataset/model cards, lineage, approvals and audit trails.
- Reproducibility, documentation and independent validation.
- Challenger models, monitoring, retraining and retirement criteria.

---

# Part C — Deep learning, transformers and generative AI

## 14. Neural-network and deep-learning foundations

### P0 topics

- Perceptron, multilayer perceptron, forward pass and backpropagation.
- Activation functions: sigmoid, tanh, ReLU, GELU, softmax and their failure modes.
- Losses: cross-entropy, binary cross-entropy, MSE, contrastive and triplet loss.
- Weight initialization, normalization, dropout and regularization.
- Vanishing/exploding gradients and gradient clipping.
- Optimizers: SGD, momentum, Adam and AdamW.
- Batch size, learning rate, epochs, convergence and early stopping.
- Batch, layer and RMS normalization.
- Training versus evaluation mode and reproducibility.

### Architecture families

- CNNs: convolution, padding, stride, pooling, receptive field and residual connections.
- RNNs, LSTMs and GRUs; sequence limitations.
- Encoder-decoder and sequence-to-sequence models.
- Attention and transformers.
- Autoencoders and variational autoencoders.
- GAN objectives and instability.
- Diffusion-model intuition and denoising.

### Framework knowledge

- Tensors, automatic differentiation, datasets/dataloaders and training loops.
- Checkpointing, mixed precision, gradient accumulation and distributed data parallelism.
- PyTorch is the highest-priority hands-on framework; know TensorFlow/Keras or JAX at awareness/working level when the role asks for it.

## 15. NLP and transformer foundations

### NLP P0

- Text normalization and when not to normalize.
- Tokenization: word, subword, BPE, WordPiece and SentencePiece.
- Bag-of-words, TF-IDF and BM25.
- Word embeddings: Word2Vec/GloVe intuition and contextual embeddings.
- Classification, NER, information extraction, semantic similarity and generation.
- Sequence metrics and task-specific evaluation.

### Transformer P0

- Query, key, value and scaled dot-product attention.
- Self-attention versus cross-attention.
- Multi-head attention, causal masks and padding masks.
- Positional encoding; awareness of RoPE and relative positions.
- Encoder-only, decoder-only and encoder-decoder architectures.
- Residual paths, normalization and feed-forward blocks.
- Pretraining objectives: masked language modeling versus next-token prediction.
- Tokenization effects, context windows and truncation.
- KV cache and why autoregressive decoding is expensive.

### P1 advanced architecture topics

- FlashAttention intuition, grouped/multi-query attention and sliding-window attention.
- Mixture-of-experts routing and sparse activation.
- State-space/hybrid architectures such as Mamba-style layers.
- Multimodal encoders, projectors and vision-language models.
- Scaling laws and data/compute/model trade-offs.

## 16. LLM and generative-AI engineering

### P0 concepts

- Base, instruct and reasoning models; open-weight versus hosted models.
- Temperature, top-p/top-k, max tokens, stop conditions and deterministic output.
- Prompt roles, instruction hierarchy and context construction.
- Zero-shot, few-shot, decomposition, ReAct and self-consistency concepts.
- Structured output, JSON Schema and validation/retry strategies.
- Function/tool calling and safe tool contracts.
- Context-window budgeting and prompt caching.
- Hallucination, grounding, refusal and uncertainty.
- Model selection by quality, latency, cost, privacy, context, modality and license.
- Multimodal input/output and document understanding.

### P1 topics

- Synthetic data generation and quality control.
- Prompt optimization and prompt versioning.
- Routing between models; fallback and graceful degradation.
- Semantic caching and exact/prefix caching.
- Distillation from a larger teacher to a smaller model.
- Long-context limitations and lost-in-the-middle behavior.

## 17. Fine-tuning and post-training

### P0/P1 topics

- When to prompt, use RAG, fine-tune or train from scratch.
- Data collection, deduplication, contamination checks and train/eval splits.
- Supervised fine-tuning and instruction/chat templates.
- Parameter-efficient tuning: adapters, LoRA and QLoRA.
- Preference data and reward modeling.
- RLHF concepts; PPO awareness.
- Direct preference optimization and related preference objectives.
- Reasoning-oriented reinforcement learning awareness, including GRPO-style methods.
- Catastrophic forgetting, overfitting and capability regression.
- Quantization-aware training versus post-training quantization.
- Evaluation gates, rollback and adapter/model version management.

### Libraries

- Hugging Face Transformers, Datasets, Tokenizers, Accelerate, PEFT and TRL.
- PyTorch, DeepSpeed/FSDP and distributed training primitives.
- bitsandbytes and other quantization tooling.
- NVIDIA NeMo Framework/AutoModel for large-scale training and customization when the NVIDIA stack is relevant.

## 18. Generative-AI evaluation

### Evaluation dimensions

- Task correctness and completeness.
- Groundedness/faithfulness and citation correctness.
- Relevance, coherence, style and instruction following.
- Safety, toxicity, privacy and policy adherence.
- Tool-selection, argument and execution correctness.
- Agent trajectory quality and task completion.
- Latency, time to first token, tokens/second, cost and failure rate.
- Robustness to paraphrases, noisy inputs and adversarial prompts.

### Methods

- Golden datasets, production traces and failure-case suites.
- Exact/rule-based checks, code execution and schema validation.
- Human evaluation with clear rubrics and inter-rater agreement.
- LLM-as-judge with calibration, position-bias checks and judge-model limitations.
- Pairwise comparisons, win rate and confidence intervals.
- Offline regression tests and online monitoring.
- Red-team tests and release gates.

---

# Part D — Retrieval, RAG and agents

## 19. Search, embeddings and RAG

### Retrieval foundations P0

- Sparse retrieval, inverted indexes, TF-IDF and BM25.
- Dense embeddings and semantic similarity.
- Cosine similarity, dot product and Euclidean distance.
- Approximate nearest-neighbor search; HNSW/IVF awareness.
- Recall versus precision trade-offs in candidate retrieval.
- Bi-encoders versus cross-encoder rerankers.

### RAG pipeline P0

- Source ingestion, parsing, OCR, tables and document structure.
- Cleaning, deduplication, metadata and document versioning.
- Chunk size, overlap, semantic/structural chunking and parent-child retrieval.
- Embedding-model selection and dimensionality.
- Vector index, metadata filters and access control.
- Query rewriting, decomposition, multi-query and hybrid search.
- Reranking, context compression and context assembly.
- Prompt grounding, citations and no-answer behavior.
- Index refresh, deletion, tenancy and point-in-time correctness.

### Advanced P1/P2

- HyDE, reciprocal-rank fusion and query routing.
- Multi-vector/late-interaction retrieval and ColBERT awareness.
- Contextual/late chunking and long-document strategies.
- Knowledge-graph and GraphRAG patterns.
- Multimodal retrieval.
- Corrective, adaptive and agentic RAG.
- Retrieval caching and semantic caching.

### RAG evaluation

- Retrieval: Recall@K, Precision@K, MRR and NDCG.
- Generation: answer correctness, groundedness, relevance and citation accuracy.
- Component-level ablations and end-to-end task success.
- Adversarial documents, prompt injection and unauthorized retrieval tests.

## 20. Agent concepts and workflow design

### P0 concepts

- Agent = model + instructions + tools + state + control loop.
- Deterministic workflow versus open-ended agent; choosing the simplest sufficient design.
- Observe–reason/plan–act–observe loops and ReAct.
- Tools/functions, schemas, validation, permissions and side effects.
- Single-agent versus multi-agent systems.
- Router, supervisor/manager, handoff, agents-as-tools and map-reduce patterns.
- State machines and graph-based orchestration.
- Short-term conversation state versus long-term memory.
- Semantic, episodic and procedural memory concepts.
- Checkpoints, durable execution, resumability and human-in-the-loop approval.
- Streaming, parallel tool calls and asynchronous execution.

### Reliability P0/P1

- Idempotency, retries, timeouts, circuit breakers and fallbacks.
- Duplicate side effects and exactly-once illusions.
- Tool errors, partial failure, compensation and workflow recovery.
- Bounded loops, budgets and stop conditions.
- Context compaction, summarization and memory contamination.
- Sandbox isolation for generated code.
- Trace/span design and correlation IDs.
- Latency, token and cost budgets per step.

### Agent evaluation

- Final task success, trajectory correctness and tool-use accuracy.
- Handoff/router accuracy and argument validity.
- Loop count, token use, latency, cost and recovery rate.
- Deterministic workflow tests with mocked models/tools.
- Simulation, adversarial cases and human review.

## 21. Agent interoperability and protocols

- **MCP:** hosts, clients and servers; tools, resources and prompts; transports; authentication; capability discovery; user consent and security boundaries.
- **A2A:** discoverable remote agents, task delegation and agent-to-agent interoperability.
- **OpenAPI/JSON Schema:** tool contracts and structured arguments.
- **Event-driven integration:** queues, webhooks, Kafka and long-running tasks.
- **Identity and authorization:** user versus service identity, delegated authority and least privilege.
- **Interview focus:** explain why a protocol is not an authorization system and where validation, policy and audit controls belong.

## 22. Agent framework map — what each is for

| Framework/tool | Primary use | What to know for interviews | Suggested depth |
|---|---|---|---|
| **LangChain** | Components/integrations for LLM apps, tools and retrieval | Models, prompts, runnables, tools, retrievers; avoid treating it as the architecture itself | Working |
| **LangGraph** | Stateful graph workflows and production agents | State, nodes/edges, reducers, checkpoints, interrupts, durable execution, subgraphs, streaming, human approval | Deep for agent roles |
| **Google ADK** | Modular agents/workflows with tools, sessions, memory, evaluation and deployment, especially in the Google ecosystem | Agent types, sequential/parallel/loop workflows, callbacks, state/session/memory, tools, MCP/A2A and evaluation | Working–Deep if job uses Google Cloud |
| **OpenAI Agents SDK** | Lightweight agent runner around tools, handoffs, guardrails, sessions and tracing | Manager versus handoff orchestration, agents-as-tools, guardrails, sessions, structured output, tracing | Working–Deep if OpenAI stack |
| **LlamaIndex** | Data-centric LLM apps and RAG/agent workflows | Readers, indexes, retrievers, query engines, workflows and evaluation | Working for RAG roles |
| **Haystack** | Component pipelines for retrieval, RAG and agents | Pipeline components, document stores, retrievers, generators and evaluation | Working/awareness |
| **PydanticAI** | Typed Python agents with validation and dependency injection | Typed dependencies/results, tool schemas, retries and testability | Working/awareness |
| **Semantic Kernel** | Enterprise agent/process orchestration across Microsoft languages/ecosystem | Plugins, planners/agents, memory and Azure integration | Working if Microsoft stack |
| **AutoGen** | Conversational and multi-agent application patterns | Agent messaging, group orchestration and termination; assess complexity carefully | Awareness/working |
| **CrewAI** | Role/task/crew-style multi-agent orchestration | Agents, tasks, crews/flows, state and monitoring | Awareness/working |
| **Agno** | Lightweight agent teams and multimodal workflows | Tools, knowledge, memory, teams and serving | Awareness |
| **AWS Strands Agents** | Model-driven agents integrated with AWS tools/services | Agent loop, tools, hooks, sessions and Bedrock/AgentCore integration | Working if AWS stack |
| **DSPy** | Programmatic LM modules and optimization against metrics | Signatures, modules, optimizers, datasets/metrics; useful for systematic prompt/program optimization | Working/awareness |
| **LiteLLM** | Provider-normalized model gateway/client | Model routing, fallbacks, budgets, retries, observability and provider differences | Working for platform roles |

### How to compare frameworks in an interview

Do not answer with popularity alone. Compare:

1. control model: graph, code-first loop, planner or conversational agents;
2. state, persistence and durable execution;
3. tool typing, validation and authorization hooks;
4. human-in-the-loop support;
5. observability, evaluation and deterministic testing;
6. provider/cloud coupling;
7. deployment and scaling model;
8. ecosystem maturity and migration cost.

## 23. Nemotron and the NVIDIA AI stack

### Important distinction

- **NVIDIA Nemotron** is a family of open models for reasoning, agentic and retrieval-related workloads. It is a model choice, not an agent framework.
- **NVIDIA NeMo** is a broader collection of training, customization, retrieval, evaluation, guardrail and agent-lifecycle components.
- **NVIDIA NIM** packages optimized model inference behind deployable microservice APIs.
- **TensorRT-LLM/Triton** are lower-level serving and optimization technologies in the NVIDIA ecosystem.

### What to learn

- When an open-weight model is preferable: privacy, on-premises deployment, customization, predictable throughput or cost control.
- Nemotron model-card evaluation, license, hardware requirements, context/modality and tool-use capability.
- Nemotron Retrieval models for extraction, embeddings and reranking.
- Nemotron safety/jailbreak/content-safety models when appropriate.
- NeMo Framework/AutoModel for pretraining, SFT, PEFT/LoRA, distillation and distributed training.
- NeMo Retriever, NeMo Evaluator and NeMo Guardrails.
- NIM, vLLM, SGLang, Ollama or llama.cpp as possible deployment routes depending on hardware and scale.

### Current lifecycle warning

The **NeMo Agent Toolkit** was deprecated in October 2026 and is scheduled for end of life by the end of 2026. Know what it did, but do not make it the main framework in a new learning plan. NVIDIA directs users toward newer NeMo Relay, Helix and Fabric components for relevant lifecycle needs.

---

# Part E — Production AI, MLOps and system design

## 24. LLM inference and optimization

### P0/P1 concepts

- Prefill versus decode; time to first token versus time per output token.
- Throughput, concurrency, tail latency and GPU utilization.
- KV cache, memory pressure and context-length trade-offs.
- Dynamic/continuous batching and PagedAttention concepts.
- Prefix/prompt caching and cache invalidation.
- Quantization: FP16/BF16, FP8, INT8 and INT4 trade-offs.
- Speculative decoding and when it helps.
- Tensor, pipeline, data, sequence/context and expert parallelism.
- Model sharding, replication and autoscaling.
- Streaming and cancellation.
- Rate limiting, admission control and priority scheduling.
- Model routing, fallbacks and quality/cost tiers.

### Serving tools

- **vLLM:** high-throughput OpenAI-compatible serving; continuous batching, cache and distributed inference concepts.
- **SGLang:** serving/runtime with structured generation and performance-oriented execution.
- **Hugging Face TGI:** production serving for supported transformer models.
- **llama.cpp/Ollama:** local and edge-friendly quantized inference and developer workflows.
- **TensorRT-LLM + Triton:** NVIDIA-optimized inference and serving.
- **NVIDIA NIM:** packaged optimized inference microservices.
- **Ray Serve, KServe, BentoML or Seldon:** scalable service/deployment layers.

## 25. MLOps and LLMOps

### Lifecycle P0

- Reproducible training, experiment tracking and artifact lineage.
- Data, code, model, prompt and configuration versioning.
- Model registry, approval stages and deployment metadata.
- Training pipelines, scheduled jobs and event-driven pipelines.
- CI/CD/continuous training; unit, data, model and integration tests.
- Batch, online, streaming and edge inference.
- Shadow, canary, blue-green and A/B deployment.
- Monitoring: service, data, model, business and safety metrics.
- Drift detection, delayed labels and performance estimation.
- Retraining triggers, rollback, incident response and retirement.

### GenAI-specific operations

- Prompt registry and prompt regression tests.
- Trace collection across model, retriever, tool and agent steps.
- Token, latency and cost attribution.
- Online/offline evaluation and production feedback loops.
- Golden datasets built from representative and failed traces.
- Provider/model change management.
- RAG index lifecycle and document deletion/permission propagation.

### Important tool families

| Need | Tools to recognize/use |
|---|---|
| Experiment/model/prompt lifecycle | MLflow, Weights & Biases, DVC |
| Pipelines/orchestration | Airflow, Dagster, Prefect, Kubeflow Pipelines |
| Feature store | Feast and managed cloud feature stores |
| Data quality | Great Expectations, Pandera, Deequ |
| Model/data monitoring | Evidently, Arize and managed platform tools |
| LLM tracing/evaluation | MLflow, LangSmith, Langfuse, Phoenix, Weave, OpenTelemetry |
| RAG/LLM evaluation | Ragas, DeepEval, promptfoo, TruLens plus custom evaluators |
| Serving | KServe, Seldon, BentoML, Ray Serve, FastAPI/gRPC |
| Infrastructure | Docker, Kubernetes, Terraform and cloud-native services |

## 26. Data and distributed-compute engineering

- Spark execution model, transformations/actions, shuffles, partitions and skew.
- Pandas versus Polars versus Spark versus Ray/Dask.
- Batch versus streaming; event time, watermarks and late data.
- Kafka concepts: topics, partitions, consumer groups, offsets and delivery semantics.
- Data lake/lakehouse/warehouse concepts; Parquet and columnar storage.
- ETL versus ELT, idempotent pipelines and backfills.
- Distributed training: workers, collective communication, checkpoints and fault tolerance.
- GPU scheduling, topology, memory and multi-node considerations.
- Cloud building blocks across AWS/Azure/GCP without memorizing every product name.

## 27. AI/ML system design

### Design method

1. Clarify users, business objective, constraints and non-goals.
2. Define success, guardrail and operational metrics.
3. Estimate scale, latency, throughput, data volume and cost.
4. Design data/label flow and baseline.
5. Select model/retrieval/agent approach with alternatives.
6. Define APIs, state, storage, online/offline paths and failure handling.
7. Add evaluation, security, observability, rollout and rollback.
8. Explain trade-offs and an incremental delivery plan.

### Common design prompts

- Churn/fraud/credit-risk prediction platform.
- Search, recommendation or ranking system.
- Demand forecasting or dynamic-pricing platform.
- Document Q&A/RAG system with citations and access controls.
- Enterprise assistant that calls internal tools.
- Multi-agent workflow for research, coding or operations.
- Real-time content moderation or anomaly detection.
- Large-scale LLM inference gateway with cost/latency tiers.

### Production topics

- API contracts, pagination, streaming, async jobs and webhooks.
- Caches, queues, load balancing, partitioning and replication.
- Availability, consistency and graceful degradation.
- Idempotency keys, retries and dead-letter queues.
- SLOs/SLIs, tracing, logs, metrics and alerting.
- Capacity planning, cost estimation and multi-tenancy.

## 28. AI and agent security

### P0 threats and controls

- Direct and indirect prompt injection.
- Data exfiltration and cross-tenant leakage.
- Poisoned documents, embeddings, training data or tool output.
- Insecure output handling and code/command injection.
- Excessive agency and unauthorized side effects.
- Tool/schema manipulation, confused-deputy problems and privilege escalation.
- Sensitive-data/PII leakage in prompts, traces, caches and logs.
- Model or dependency supply-chain risk.
- Denial of service, unbounded loops and cost exhaustion.

### Defenses

- Treat model output and retrieved content as untrusted.
- Least privilege, scoped credentials and user-bound authorization.
- Allowlisted tools/domains, strict validation and policy checks outside the model.
- Human approval for high-impact or irreversible actions.
- Sandboxed code execution and network/filesystem isolation.
- Output encoding, secret scanning, DLP and tenant-aware retrieval filters.
- Budgets, timeouts, rate limits, circuit breakers and audit logs.
- Adversarial tests, red teams and continuous security monitoring.

### Governance awareness

- Privacy by design, retention, consent and data minimization.
- Explainability and human oversight for high-impact decisions.
- Model/data documentation, risk classification and audit evidence.
- Applicable organizational standards and regulations for the target domain.

---

# Part F — Leadership, product thinking and project defense

## 29. Lead Data Scientist and senior AI Engineer competencies

### Problem and product leadership

- Translate an ambiguous request into a decision, action and measurable outcome.
- Select a baseline and justify why ML/GenAI is needed.
- Define north-star, input, guardrail and operational metrics.
- Estimate value, cost, risk and time to impact.
- Prioritize experiments and create an incremental roadmap.
- Decide build versus buy and hosted versus open/self-hosted.
- Stop or redirect a low-value project using evidence.

### Technical leadership

- Write/review design documents and define technical standards.
- Make reversible versus irreversible decisions appropriately.
- Review models, code, data and experiments—not only slides.
- Manage technical debt and migrate systems safely.
- Mentor different experience levels and delegate ownership.
- Coordinate Data Science, ML Engineering, Product, Data Engineering, Security and Legal.
- Communicate uncertainty and trade-offs to executives.
- Own production incidents and blameless postmortems.

### Behavioral question bank

- A project with measurable impact: baseline, intervention, result and attribution.
- A model that failed after deployment and how you diagnosed it.
- A disagreement on model/architecture choice.
- A time you influenced without authority.
- A roadmap trade-off under limited people, compute or time.
- A weak team member you coached and the outcome.
- A data-quality or ethics risk you escalated.
- A project you stopped and why.
- A severe incident: detection, containment, communication and prevention.
- A decision where a simpler solution beat a sophisticated model.

## 30. Project deep-dive checklist

For each resume project, prepare a two-minute summary and a 20-minute defense covering:

- user/business problem and why it mattered;
- scale, constraints and baseline;
- data and label construction;
- architecture and your exact contribution;
- alternatives considered and rejected;
- model, prompt, retrieval or agent choices;
- offline metrics and why they match the objective;
- experiment or rollout method;
- production latency, throughput, cost and reliability;
- security, privacy and governance;
- observed business result and how causality was established;
- failures, surprises and what you would change now.

Never claim impact without explaining the baseline, time window and measurement method.

---

# Part G — Cheat-sheet production plan

## 31. Recommended cheat-sheet sequence

### Phase 1 — Universal screening core

1. Python interview patterns and complexity
2. SQL interview patterns
3. Probability and statistics
4. Experimentation and causal inference
5. Classical ML algorithms
6. ML metrics, validation and leakage

### Phase 2 — Modeling depth

7. Feature engineering and EDA
8. Time series
9. Recommendation/search/ranking
10. Neural networks and backpropagation
11. CNN/RNN/deep-learning training
12. NLP and transformers

### Phase 3 — Generative and agentic AI

13. LLM foundations and prompting
14. Fine-tuning, PEFT and post-training
15. Embeddings, vector search and RAG
16. RAG evaluation and optimization
17. Agent patterns and reliability
18. LangGraph
19. Google ADK
20. OpenAI Agents SDK and cross-framework comparison
21. MCP, A2A and tool security
22. Nemotron and the NVIDIA stack
23. GenAI/agent evaluation and observability

### Phase 4 — Production and design

24. MLOps/LLMOps
25. LLM inference and cost/latency optimization
26. Docker, Kubernetes and cloud for AI
27. Distributed data/training/serving
28. ML system design
29. RAG/agent system design
30. AI security, privacy and governance

### Phase 5 — Lead-level rounds

31. Product metrics and business cases
32. Technical leadership and behavioral stories
33. Project deep-dive preparation
34. End-to-end mock interview cases

## 32. Standard format for each cheat sheet

Every sheet should contain:

1. **One-line definition**
2. **Intuition**
3. **Core formula or execution flow**
4. **Assumptions**
5. **When to use / avoid**
6. **Key hyperparameters or design choices**
7. **Trade-offs**
8. **Failure modes and debugging**
9. **Minimal Python/SQL/pseudocode example**
10. **Production considerations**
11. **Five rapid interview questions with answers**
12. **One design/case question**
13. **Thirty-second revision box**

## 33. Recommended preparation strategy

- Learn one primary tool deeply in each category instead of memorizing every library.
- Be framework-independent first: understand state, tools, retrieval, evaluation and failure recovery before LangGraph/ADK syntax.
- Build one strong end-to-end project that includes data, evaluation, API, deployment, monitoring and security.
- For lead roles, connect every technical choice to business impact, team execution and operational risk.
- Use the library map as recognition coverage; expand only the tools required by the target job description.

---

# Sources used to calibrate the 2026 role expectations

Current senior role descriptions emphasize Python/SQL, end-to-end ML, statistics/experimentation, deep learning, GenAI, RAG, agents, evaluation, cloud-native services, MLOps, communication and technical leadership:

- [NVIDIA Senior AI/ML Software Engineer](https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/India-Bengaluru/Senior-AI-ML-Software-Engineer_JR2024127)
- [NVIDIA Senior Software Engineer, Generative AI Systems](https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/Senior-Software-Engineer--Generative-AI-Systems_JR2018830)
- [Amazon Data Scientist, Alexa Connections](https://amazon.jobs/en/jobs/10574038/data-scientist-alexa-connections)
- [Amazon Senior Applied Scientist, Alexa Ads](https://www.amazon.jobs/en/jobs/10417197/senior-applied-scientist-alexa-ads)
- [Walmart Principal Data Scientist](https://careers.walmart.com/us/en/jobs/R-2613895)
- [Walmart Senior Data Scientist](https://careers.walmart.com/us/en/jobs/R-2648117)

Framework/ecosystem references:

- [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/overview)
- [Google Agent Development Kit documentation](https://google.github.io/adk-docs/)
- [OpenAI Agents SDK documentation](https://openai.github.io/openai-agents-python/)
- [Model Context Protocol documentation](https://modelcontextprotocol.io/)
- [NVIDIA Nemotron](https://developer.nvidia.com/topics/ai/Nemotron)
- [NVIDIA NeMo documentation](https://docs.nvidia.com/nemo/index.html)
- [NeMo Agent Toolkit deprecation notice](https://docs.nvidia.com/nemo/agent-toolkit/latest/)
- [Hugging Face documentation](https://huggingface.co/docs)
- [vLLM documentation](https://docs.vllm.ai/en/latest/)
- [MLflow documentation](https://mlflow.org/docs/latest)
- [Ray documentation](https://docs.ray.io/en/latest/)
