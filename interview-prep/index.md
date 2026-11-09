---
layout: "week"
status: "approved"
version: "1.3.0"
last_reviewed: "2026-11-09"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "AI and Data Science interview preparation"
description: "Role-specific interview banks and compact revision guides for AI Engineer, Agentic AI Engineer, Senior Data Scientist, and Data Science Technical Lead roles."
summary: "Convert the validated learning roadmap into concise revision, spoken answers, system-design reasoning, and project evidence."
permalink: "/interview-prep/"
kicker_primary: "Interview conversion"
kicker_secondary: "Role banks · Cheat sheets"
current_label: "Interview prep hub"
---
## Start with your target role

| Role bank | Best for | Current coverage |
| --- | --- | --- |
| [Agentic AI Engineer]({{ '/interview-prep/roles/agentic-ai-engineer/' | relative_url }}) | AI Engineer, GenAI Engineer, Agentic AI Engineer | Production AI, embeddings, ingestion, RAG architecture, evaluation, security, reliability and incidents |
| [Data Science Technical Lead]({{ '/interview-prep/roles/data-science-technical-lead/' | relative_url }}) | Data Science Lead, Technical Lead, Applied AI Lead | Framing, ML and LLM decisions, retrieval and RAG leadership, governance, security and operating models |
| [Senior Data Scientist]({{ '/interview-prep/roles/senior-data-scientist/' | relative_url }}) | Senior Data Scientist, Applied Scientist | Statistics, ML, embeddings, retrieval experiments, RAG evaluation, monitoring and business impact |

Each role bank now contains 80 guided questions across Batches 1–4, with strong-answer signals, a deeper follow-up probe, and direct revision links. Batches 1–4 are approved. Stable IDs let you track weak areas and support later random-paper conversion.

## Batch 1 cheat sheets

| Revision sheet | Use it for |
| --- | --- |
| [Python]({{ '/interview-prep/cheat-sheets/python/' | relative_url }}) | Coding, debugging, concurrency, APIs, tests and production practices |
| [SQL]({{ '/interview-prep/cheat-sheets/sql/' | relative_url }}) | Query correctness, joins, windows, analytics, transactions and optimization |
| [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }}) | Probability, estimation, inference, power, experiments and causal interpretation |
| [Machine-learning fundamentals]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) | Framing, algorithms, metrics, validation, leakage, deployment and monitoring |

## Batch 2 cheat sheets

| Revision sheet | Use it for |
| --- | --- |
| [Deep learning and neural networks]({{ '/interview-prep/cheat-sheets/deep-learning-neural-networks/' | relative_url }}) | Forward/backpropagation, losses, optimization, regularization, architectures and training failures |
| [Natural language processing]({{ '/interview-prep/cheat-sheets/nlp/' | relative_url }}) | Text data, tokenization, representations, classification, extraction, evaluation and multilingual systems |
| [Transformers]({{ '/interview-prep/cheat-sheets/transformers/' | relative_url }}) | Attention, masks, position, architecture families, KV cache, GQA/MQA and efficiency |
| [LLM and Generative AI]({{ '/interview-prep/cheat-sheets/llm-generative-ai/' | relative_url }}) | Generation, prompting, structured output, fine-tuning, evaluation, safety and serving decisions |

## Batch 3 cheat sheets

| Revision sheet | Use it for |
| --- | --- |
| [Embeddings and vector search]({{ '/interview-prep/cheat-sheets/embeddings-vector-search/' | relative_url }}) | Similarity, sparse/dense/hybrid retrieval, bi-encoders, reranking, ANN indexes, filtering and search failures |
| [Document ingestion, chunking, and indexing]({{ '/interview-prep/cheat-sheets/document-ingestion-chunking-indexing/' | relative_url }}) | Parsing, provenance, chunking, idempotency, updates, deletions, backfills and index operations |
| [RAG architecture, retrieval, and generation]({{ '/interview-prep/cheat-sheets/rag-architecture-retrieval-generation/' | relative_url }}) | Query transformation, staged retrieval, reranking, context assembly, grounded generation, citations and abstention |
| [RAG evaluation, security, and production]({{ '/interview-prep/cheat-sheets/rag-evaluation-security-production/' | relative_url }}) | Retrieval and generation metrics, release gates, prompt injection defenses, observability, SLOs and incidents |

## Batch 4 cheat sheets

| Revision sheet | Use it for |
| --- | --- |
| [Agent fundamentals and workflow patterns]({{ '/interview-prep/cheat-sheets/agent-fundamentals-workflow-patterns/' | relative_url }}) | Agent boundaries, tool contracts, state, memory, routing, multi-agent patterns, budgets and human approval |
| [LangGraph deep dive]({{ '/interview-prep/cheat-sheets/langgraph-deep-dive/' | relative_url }}) | Typed state, reducers, routing, fan-out, checkpoints, stores, interrupts, replay, caching and tests |
| [Agent frameworks and libraries comparison]({{ '/interview-prep/cheat-sheets/agent-frameworks-libraries-comparison/' | relative_url }}) | LangGraph, Google ADK, OpenAI Agents SDK, PydanticAI, DSPy, retrieval frameworks, Microsoft and NVIDIA layers |
| [Agent protocols, reliability, security, and evaluation]({{ '/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/' | relative_url }}) | MCP, A2A, identity, idempotency, retries, resilience, trajectory evaluation, SLOs and release gates |

Use the [complete master index]({{ '/interview-prep/master-index/' | relative_url }}) to see the full topic backlog and expected depth for each role.

## Interview answer standard

A senior answer should normally cover:

1. the decision, user, and constraints;
2. assumptions and data or system boundaries;
3. the chosen approach and a credible baseline;
4. trade-offs and rejected alternatives;
5. evaluation and operational metrics;
6. failure handling, security, cost, and rollback where relevant;
7. measurable business or user impact;
8. what remains uncertain or unproven.

## Suggested weekly routine

| Session | Time | Work |
| --- | ---: | --- |
| Revision | 30 minutes | One cheat-sheet section and five recall prompts |
| Spoken practice | 45 minutes | Five role-bank questions, recorded |
| Deep dive | 45 minutes | One system/case question with trade-offs and metrics |
| Project evidence | 30 minutes | Add one example, number, failure, or lesson from your own work |

## Roadmap for later batches

| Batch | Planned scope |
| --- | --- |
| 5 | AI system design, MLOps, observability, security, leadership, project storytelling and mock rounds |

> The Week 1–20 question banks remain learning checks. These interview banks deliberately test role performance, decision quality, communication, and production judgment.
