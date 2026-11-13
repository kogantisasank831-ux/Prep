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
title: "Agent frameworks and libraries comparison interview cheat sheet"
description: "LangGraph, Google ADK, OpenAI Agents SDK, LlamaIndex, Haystack, PydanticAI, DSPy, Microsoft, and NVIDIA ecosystem decisions."
summary: "Compare orchestration, agent SDKs, retrieval frameworks, optimization libraries, protocols, model serving, guardrails, and migration trade-offs."
permalink: "/interview-prep/cheat-sheets/agent-frameworks-libraries-comparison/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 4 · Framework comparison"
current_label: "Revision guide"
alternate_label: "Cheat sheets hub"
alternate_url: "/cheat-sheets/"
---
> **Batch 4 source:** This page integrates the prepared revision artifact into the Prep site. It is separate from the Week 1–30 learning assessments.

**Target roles:** Agentic AI Engineer, GenAI Engineer, ML Engineer, AI Architect, Senior/Lead Data Scientist  
**Use:** framework selection, Google ADK, LangChain/LangGraph ecosystem, multi-agent libraries, NVIDIA stack, and migration decisions  
**Interview rule:** compare requirements and control models—not logo lists. A library accelerates implementation; it does not supply the product’s correctness, security, or operating model.

## 1. Thirty-second revision

- Choose an agent framework only after defining control flow, state, persistence, HITL, tool/protocol integration, deployment, evaluation, observability, and team constraints.
- **LangChain** supplies model/tool/retrieval abstractions; **LangGraph** supplies explicit stateful graph orchestration and durability.
- **Google ADK** is a code-first, model- and deployment-agnostic agent framework optimized for Google’s ecosystem, with LLM agents, deterministic workflow agents, sessions, tools, callbacks, evaluation, and deployment paths.
- **OpenAI Agents SDK** is a lightweight SDK centered on agents, tools, handoffs, guardrails, sessions, and tracing.
- **LlamaIndex** and **Haystack** are strong when data, retrieval, indexing, and pipelines dominate.
- **PydanticAI** emphasizes typed Python/dependency injection; **DSPy** emphasizes optimizing LM programs against metrics.
- Role-oriented multi-agent abstractions such as CrewAI can speed prototypes; explicit graphs often offer clearer control for complex production recovery.
- Microsoft’s current direction is **Microsoft Agent Framework**, with migration guidance from AutoGen and Semantic Kernel.
- **Nemotron** is an NVIDIA model family, not an orchestration library. NeMo Framework, Guardrails, NIM, and the newer Relay/Helix/Fabric products solve different layers.
- Prefer thin application-owned interfaces so model, tool, memory, tracing, and framework choices can evolve.

## 2. Decide the layer first

| Layer | Examples | What it solves |
|---|---|---|
| Model/provider SDK | OpenAI, Anthropic, Google Gen AI, Hugging Face | model API access |
| Model gateway/router | LiteLLM | common provider interface, routing, budgets, logging hooks |
| Agent SDK/framework | Google ADK, OpenAI Agents SDK, PydanticAI, Strands | agent loop, tools, handoffs, runtime abstractions |
| Orchestration | LangGraph, Microsoft Agent Framework workflows | explicit state, branches, cycles, durability |
| Retrieval/data framework | LlamaIndex, Haystack, LangChain | ingestion, indexing, retrieval, RAG pipelines |
| Prompt/program optimization | DSPy | optimize modular LM programs against a metric |
| Protocol | MCP, A2A | interoperability contracts between components/systems |
| Serving/runtime | vLLM, NVIDIA NIM, managed agent runtimes | scalable model or agent execution |
| Guardrails/evaluation/observability | NeMo Guardrails, LangSmith, OpenTelemetry, Ragas | policy, testing, traces, quality measurement |

Several products span layers. State the primary role and the part you will actually depend on.

## 3. Framework selection questions

Ask in this order:

1. Is the flow mostly deterministic, model-directed, or hybrid?
2. Do runs need durable checkpoints, resume, replay, and human approval?
3. Is the application retrieval-heavy or action/tool-heavy?
4. Is multi-agent coordination truly required?
5. Which languages, clouds, models, and deployment targets are mandatory?
6. What are the state, memory, tenant-isolation, and retention requirements?
7. Which tracing/evaluation standards and data residency rules apply?
8. How will long-running executions survive code/schema upgrades?
9. Can the team test, debug, and operate the abstraction?
10. What is the migration/lock-in strategy?

## 4. Practical comparison matrix

This is a positioning guide, not a benchmark. Features evolve; verify pinned versions.

| Framework/library | Primary control model | Best fit | Main trade-off |
|---|---|---|---|
| LangChain | composable model/tool/retrieval components | broad LLM application integration | abstractions can become deep if used indiscriminately |
| LangGraph | explicit state graph with model-driven nodes | durable, branching, HITL agent workflows | requires deliberate state and graph design |
| Google ADK | agents plus sequential/parallel/loop workflow agents | code-first multi-agent apps, especially Google ecosystem | rapid evolution; Google deployment integrations may shape architecture |
| OpenAI Agents SDK | agent loop, tools, handoffs, guardrails, tracing | lightweight agent apps and handoffs | strongest fit with its native concepts/provider ecosystem |
| LlamaIndex | data/index/query workflows and agents | retrieval-heavy knowledge applications | less compelling when retrieval is minor |
| Haystack | component pipelines, agents, retrieval | explicit RAG/search pipelines and production components | pipeline concepts add another abstraction layer |
| PydanticAI | typed Python agents and dependencies | Python teams prioritizing validation/testability | smaller orchestration surface than a full graph runtime |
| Microsoft Agent Framework | agents plus graph/workflow orchestration | Microsoft/.NET/Azure and multi-provider enterprise apps | migration and product maturity must be assessed |
| CrewAI | role/task/crew-oriented collaboration | fast role-based multi-agent workflows | implicit coordination can be harder to debug at scale |
| Agno | agent/team/workflow SDK | compact agent services with tools and knowledge | validate persistence/operations needs for your workload |
| Strands Agents | model-driven loop with tools and hooks | AWS-oriented, extensible agent development | ecosystem fit and runtime coupling require review |
| DSPy | declarative LM modules optimized to a metric | systematic prompt/pipeline optimization | needs a representative metric and dataset; not a durable runtime |
| LiteLLM | provider-compatible gateway/client | multi-provider routing, budgets, fallbacks | gateway is not agent orchestration or semantic correctness |

## 5. LangChain versus LangGraph

### LangChain

Useful for:

- model and embedding integrations;
- tools and structured output;
- documents, retrievers, and vector stores;
- prompt/runnable composition;
- standard agent building blocks.

### LangGraph

Useful for:

- typed shared state;
- explicit branches, loops, and fan-out;
- checkpoints, threads, interrupts, and durable execution;
- subgraphs and multi-agent control;
- granular streaming and recovery.

They are complementary. A LangGraph node can use LangChain integrations, direct provider SDKs, or plain Python. Use the smallest necessary surface to avoid coupling every business layer to one framework.

## 6. Google Agent Development Kit (ADK)

ADK is an open-source, code-first toolkit for building, evaluating, and deploying agents. It is optimized for Gemini/Google services but documented as model- and deployment-agnostic.

### Core concepts

| Concept | Purpose |
|---|---|
| `LlmAgent` | model-driven reasoning, tool use, and delegation |
| Custom agent | application-defined orchestration/behavior |
| `SequentialAgent` | execute sub-agents in order |
| `ParallelAgent` | execute independent branches concurrently |
| `LoopAgent` | repeat a bounded refinement/processing flow |
| Tool | function, API, service, or another capability |
| Callback | intercept/inspect/customize lifecycle points |
| Session/state | conversation/run-scoped information |
| Memory | information retrievable beyond a single session |
| Runner/service | coordinate execution and persistence services |
| Evaluation | test final responses and agent trajectories |

### When ADK fits

- The team wants deterministic workflow agents and LLM agents in one composition model.
- Google Cloud, Gemini, Cloud Run/GKE, or Google managed agent runtimes are likely targets.
- MCP/A2A integration and multi-agent composition matter.
- Code-first testing, callbacks, evaluation, and deployment lifecycle are valued.

### Questions to ask before choosing it

- Which ADK language and version has the required features?
- Which session/memory services are production-ready for the target deployment?
- Are non-Gemini providers first-class for the required features?
- What is the serialization/state migration strategy?
- How will traces and evals integrate with the company’s platform?
- Which Google-specific services are optional versus architectural dependencies?

## 7. OpenAI Agents SDK

The SDK’s core concepts include agents, tools, handoffs, guardrails, sessions, tracing, and a runner/agent loop.

Good fit:

- a lightweight, code-first agent implementation;
- specialist handoffs or agents exposed as tools;
- built-in tracing and guardrail hooks;
- teams already using OpenAI-compatible concepts and APIs.

Evaluate:

- provider portability for every feature you need;
- durable long-running workflow requirements;
- external checkpoint/store integration;
- organization-specific authorization and approval controls;
- trace data residency and redaction.

Do not confuse a handoff abstraction with a complete business-workflow state machine.

## 8. LlamaIndex and Haystack

### LlamaIndex

Choose when data connectors, indexing, retrieval/query engines, knowledge agents, or document workflows are central. It can orchestrate agents, but its greatest differentiation is often the data/RAG layer.

### Haystack

Choose for explicit component pipelines that combine retrievers, rankers, generators, converters, and agents. Pipelines make inputs/outputs and RAG composition visible.

For both, benchmark:

- ingestion fidelity and metadata/ACL handling;
- retrieval and reranking quality;
- persistence/index portability;
- async/concurrency behavior;
- component observability and versioning;
- whether their agent layer or an external graph runtime should own control.

## 9. PydanticAI

PydanticAI is attractive to Python teams that want:

- typed dependencies and structured outputs;
- validation close to agent/tool boundaries;
- test-friendly dependency overrides;
- a relatively Pythonic agent abstraction;
- model/provider flexibility.

Typed output reduces integration errors but does not guarantee factual correctness, authorization, or safe side effects. Complex durable branching may still need a workflow/orchestration layer.

## 10. Microsoft Agent Framework, AutoGen, and Semantic Kernel

By late 2026, Microsoft documents **Microsoft Agent Framework** as its current agent/workflow SDK and provides migration paths from AutoGen and Semantic Kernel.

- **AutoGen** popularized conversational multi-agent patterns and remains important interview context.
- **Semantic Kernel** is an enterprise SDK with plugins/connectors and strong Microsoft/.NET history.
- **Microsoft Agent Framework** brings agents and explicit workflows together and supports several model providers.

For a new production system, assess the current Agent Framework rather than selecting an older package from name recognition alone. For an existing system, migration cost, feature parity, support timeline, and trace/state compatibility matter more than a rewrite for fashion.

## 11. CrewAI, Agno, and Strands Agents

### CrewAI

Role/task/crew abstractions can express researcher–writer–reviewer workflows quickly. Use explicit task outputs, budgets, and observability. Avoid unconstrained agent conversation when a deterministic sequence is enough.

### Agno

Provides compact building blocks for agents, teams, knowledge, memory, and workflows. Check persistence, isolation, deployment, and evaluation behavior against the target version.

### Strands Agents

An open-source SDK associated with AWS that emphasizes a model-driven agent loop, tools, hooks, and extensibility. It can fit AWS-heavy stacks, but separate the SDK from AWS managed services and verify non-AWS/provider requirements.

The right comparison is not “which has more agents?” It is which makes control flow, state, recovery, security, and testing clearest for your team.

## 12. DSPy

DSPy treats LM applications as modular programs that can be optimized against an evaluation metric and examples.

Use it when:

- prompts/demonstrations should be optimized systematically;
- a representative training/evaluation set exists;
- the pipeline can be expressed as modules/signatures;
- you can afford optimization experiments.

It does not replace a durable workflow runtime, access control, tool-side-effect safety, or production monitoring. Poor metrics optimize the wrong behavior.

## 13. LiteLLM

LiteLLM can provide a common OpenAI-compatible client/proxy across model providers, with routing, fallbacks, budgets, keys, and observability integrations depending on deployment.

Use cases:

- provider abstraction and centralized credentials;
- policy-based routing or fallback;
- model cost/rate-limit controls;
- a common interface for several agent frameworks.

Limitations:

- provider features are not perfectly interchangeable;
- fallback models can change tool/schema/safety behavior;
- it does not determine the correct route semantically;
- it does not provide graph persistence or agent evaluation by itself.

Test each model-route combination, including tool calling and structured output.

## 14. NVIDIA ecosystem: what each name means

| NVIDIA component | Category | Typical use |
|---|---|---|
| Nemotron | model family | reasoning, instruction following, tool/agent workloads depending on model |
| NeMo Framework | model development/customization | train, fine-tune, align, and scale models |
| NeMo Guardrails | programmable guardrails | input/output/dialog/retrieval/tool policy flows |
| NVIDIA NIM | inference microservices | deploy optimized model endpoints with standard APIs |
| NeMo Retriever | retrieval services/components | ingestion, embedding, reranking, retrieval pipelines |
| NeMo Evaluator | evaluation infrastructure | run and compare evaluation workloads |
| NeMo Relay | runtime instrumentation/middleware | intercept agent, tool, and model operations for policy/observability |
| NeMo Helix | agent evaluation/optimization tooling | evaluate, optimize, and harden agents from a CLI/workflow |
| NeMo Fabric | agent harness interface/runtime layer | work across agent harnesses through a consistent interface |

### Nemotron is not an agent framework

An NVIDIA Nemotron model can be called from LangGraph, ADK, CrewAI, a direct SDK, or another runtime if interfaces are compatible. Model choice affects reasoning/tool quality, context, latency, cost, deployment, and license; it does not define persistence or workflow control.

### NeMo Agent Toolkit lifecycle

NVIDIA’s official documentation marks NeMo Agent Toolkit as deprecated in October 2026 with end of support at the end of 2026. NVIDIA directs users toward:

- **NeMo Relay** for runtime instrumentation, middleware, governance, and observability;
- **NeMo Helix** for evaluation, optimization, and hardening;
- **NeMo Fabric** for a consistent interface to agent harnesses and custom agents.

Therefore, do not start a new long-lived design around the deprecated toolkit without an explicit migration plan.

## 15. Guardrails are not one filter

NeMo Guardrails or similar libraries can help implement conversational and safety controls, but production defense also needs:

- identity and authorization at data/tool boundaries;
- prompt-injection-resistant system design;
- schema and semantic validation;
- sandbox/egress controls for code and browsing;
- approval for consequential actions;
- monitoring, red-team tests, and incident response.

A guardrail model cannot safely compensate for an over-privileged tool.

## 16. Framework portability pattern

Keep business logic behind application-owned interfaces:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class AgentRequest:
    task: str
    tenant_id: str
    operation_id: str


@dataclass(frozen=True)
class AgentResult:
    status: str
    answer: str
    evidence_ids: tuple[str, ...]


class AgentRuntime(Protocol):
    def run(self, request: AgentRequest) -> AgentResult: ...
```

Then adapters translate to LangGraph, ADK, or another runtime. Also own:

- domain state and event schemas;
- tool interfaces and authorization;
- evaluation datasets/metrics;
- trace correlation IDs;
- model/provider policy;
- external side-effect ledger.

Perfect framework neutrality is unrealistic, but boundary ownership reduces rewrite cost.

## 17. Build-versus-adopt trade-off

Adopt a framework when it removes proven complexity—checkpointing, tool loop, protocol adapters, tracing—without hiding critical behavior.

Build a thin custom loop when:

- the workflow is small;
- dependencies must be minimal;
- strict control/review matters;
- framework abstractions exceed the problem.

Do not rebuild durable orchestration, distributed queues, OAuth, or telemetry casually. Conversely, do not adopt a large framework to call one model and one tool.

## 18. Evaluation scorecard

Score candidates with a small proof of concept using the same scenario set:

| Dimension | Evidence to collect |
|---|---|
| Correctness | task and trajectory metrics |
| Control | explicit routes, budgets, cancellation, HITL |
| Durability | restart/resume and duplicate-side-effect test |
| Security | identity propagation, tenant isolation, tool approval |
| Observability | traces, versions, tokens, cost, redaction |
| Performance | p50/p95 latency, throughput, memory, token use |
| Testability | fake model/tool support and deterministic branch tests |
| Portability | alternate model/store/deployment experiment |
| Operations | migrations, rollback, failure recovery, support lifecycle |
| Team fit | languages, skills, debugging clarity, maintenance burden |

Run failure scenarios, not only a happy-path demo.

## 19. Common interview traps

- Calling Nemotron, MCP, A2A, LiteLLM, or NIM an agent framework.
- Comparing frameworks only by GitHub stars or number of integrations.
- Claiming “model agnostic” means identical behavior across providers.
- Choosing multi-agent software before proving the need for multiple agents.
- Ignoring framework state/checkpoint migrations.
- Assuming built-in tracing is safe to store without redaction.
- Treating structured output as factual validation.
- Starting new work on a deprecated library without checking lifecycle notices.
- Saying one framework is universally “best.”

## 20. Rapid interview questions

**Q1. LangChain versus LangGraph?**  
LangChain provides broad LLM/retrieval/tool components; LangGraph provides explicit stateful orchestration and durability. They can be used together or independently.

**Q2. Why choose Google ADK?**  
For code-first LLM and deterministic workflow agents, multi-agent composition, tools/callbacks, sessions/memory, evaluation, and strong Google ecosystem paths—after checking version and portability needs.

**Q3. Is Nemotron a framework?**  
No. It is an NVIDIA model family. Use an orchestration/runtime layer around the model.

**Q4. When choose LlamaIndex/Haystack?**  
When ingestion, indexing, retrieval, ranking, and data pipelines are the center of the application.

**Q5. PydanticAI’s main value?**  
Pythonic typed dependencies, validation, structured outputs, and testability around agent boundaries.

**Q6. What does LiteLLM replace?**  
It can centralize/provider-normalize model access and routing; it does not replace agent state, orchestration, authorization, or evaluation.

**Q7. Why use DSPy?**  
To optimize modular LM programs against a representative metric rather than hand-tuning prompts alone.

**Q8. How do you avoid lock-in?**  
Own domain/tool/state/eval contracts, isolate framework adapters, use open telemetry/protocols where useful, and continuously test an exit path for critical dependencies.

## 21. Lead-level design case

**Prompt:** Select a stack for a regulated multi-agent assistant with RAG, human approval, self-hosted models, and optional cloud fallback.

A strong answer should:

1. define risk, latency, concurrency, data residency, and recovery requirements;
2. use an explicit durable graph/runtime for approvals and long-running state;
3. choose a retrieval framework only if it improves the data plane;
4. place self-hosted models behind a stable gateway and test feature parity before fallback;
5. use MCP for governed tool/context integration and A2A only for remote agent boundaries;
6. keep authorization in services/tools, not prompts;
7. evaluate Nemotron or other models on task/tool/safety/latency metrics rather than brand;
8. add guardrails, tracing, evaluation, and adversarial tests as separate layers;
9. validate lifecycle/support status of every framework;
10. prototype two stacks against failure, resume, migration, and operations scorecards.

## 22. Final checklist

- [ ] I can classify model SDKs, gateways, frameworks, orchestration, protocols, serving, and guardrails.
- [ ] I can compare LangChain, LangGraph, ADK, OpenAI Agents SDK, retrieval frameworks, and typed/multi-agent libraries.
- [ ] I can explain ADK’s LLM and sequential/parallel/loop workflow agents.
- [ ] I know Microsoft’s current Agent Framework direction.
- [ ] I can explain Nemotron, NeMo, NIM, Relay, Helix, and Fabric without mixing layers.
- [ ] I can create a workload-specific framework scorecard and proof of concept.
- [ ] I can design application-owned boundaries that reduce lock-in.
- [ ] I check version, license, support lifecycle, and migration path before adoption.

## 23. Primary references

- LangChain, [LangChain overview](https://docs.langchain.com/oss/python/langchain/overview)
- LangChain, [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)
- Google, [Agent Development Kit](https://google.github.io/adk-docs/)
- OpenAI, [Agents SDK](https://openai.github.io/openai-agents-python/)
- LlamaIndex, [Framework documentation](https://developers.llamaindex.ai/python/framework/)
- deepset, [Haystack documentation](https://docs.haystack.deepset.ai/docs/intro)
- Pydantic, [PydanticAI documentation](https://ai.pydantic.dev/)
- Microsoft, [Agent Framework overview](https://learn.microsoft.com/agent-framework/overview)
- AWS, [Strands Agents SDK](https://strandsagents.com/)
- Stanford NLP, [DSPy documentation](https://dspy.ai/)
- BerriAI, [LiteLLM documentation](https://docs.litellm.ai/)
- NVIDIA, [NeMo Agent Toolkit overview and lifecycle notice](https://docs.nvidia.com/nemo/agent-toolkit/latest/overview/index.html)
- NVIDIA, [NeMo Agent Toolkit migration guide](https://docs.nvidia.com/nemo/agent-toolkit/latest/migration-guide/index.html)

Framework capabilities and product lifecycles change quickly. Recheck official documentation before interviews and production decisions.
