
# Phase 1: Foundations for Applied GenAI

## Week 1 — Python for production AI systems

### Learn

* Functions, classes and modules
* Type hints
* Dataclasses and Pydantic models
* Exception handling
* Logging
* Iterators and generators
* Async programming fundamentals
* Writing reusable and testable code
* Basic unit testing with `pytest`

### Build

Create a small Python service that:

* Accepts a document
* Extracts text
* Validates inputs
* Produces structured JSON
* Logs failures
* Includes unit tests

### Interview preparation

Be ready to explain:

* Mutable versus immutable objects
* Generators versus lists
* Threads versus async
* Why type validation matters in LLM applications

---

## Week 2 — SQL and data modelling

### Learn

* Joins
* CTEs
* Window functions
* Subqueries
* Aggregations
* Date operations
* Database indexes
* Normalisation versus denormalisation
* Transaction fundamentals

### Build

Design a PostgreSQL database containing:

* Suppliers
* Purchase orders
* Products
* Contracts
* Deliveries
* Commodity prices

Write queries for:

* Supplier performance
* Price variance
* Delayed orders
* Monthly procurement spend
* Most reliable suppliers

### Interview preparation

Solve approximately:

* 8 medium SQL questions
* 2 product analytics SQL questions

---

## Week 3 — LLM foundations

### Learn

* Tokenisation
* Embeddings
* Transformer architecture
* Self-attention
* Positional information
* Pretraining
* Instruction tuning
* Context windows
* Temperature and sampling parameters
* Hosted versus open-weight models

### Build

Create a simple application that:

* Sends prompts to two different models
* Captures output, latency and token usage
* Compares output quality
* Stores results for later evaluation

### Interview preparation

Prepare explanations for:

* Why transformers replaced many recurrent architectures
* Why hallucinations occur
* Why larger context windows do not automatically produce better answers
* Embedding models versus generative models

---

## Week 4 — Prompting and structured output

### Learn

* System, user and tool messages
* Zero-shot and few-shot prompting
* Role prompting
* Structured outputs
* JSON schema validation
* Prompt versioning
* Retry strategies
* Prompt sensitivity

### Build

Create a procurement-document extractor that returns:

* Supplier name
* Product
* Unit price
* Quantity
* Delivery date
* Payment terms
* Currency
* Confidence or validation status

Use Pydantic or JSON Schema to validate the response.

### Interview preparation

Explain why structured outputs are preferable to parsing free-form LLM responses.

# Phase 2: RAG Engineering

## Week 5 — Embeddings and vector retrieval

### Learn

* Semantic embeddings
* Similarity measures
* Cosine similarity
* Dense retrieval
* Vector indexing
* Approximate nearest-neighbour search
* Embedding dimensionality
* Domain-specific embeddings

### Build

Create a basic semantic-search system over procurement documents.

Do not use an orchestration framework initially. Implement:

* Document loading
* Chunking
* Embedding
* Vector storage
* Top-k retrieval

### Interview preparation

Prepare answers for:

* How embedding models are evaluated
* Why semantically similar text may still retrieve incorrectly
* How top-k affects recall and noise

---

## Week 6 — Document parsing and chunking

### Learn

* Fixed-size chunking
* Overlapping chunks
* Sentence-based chunking
* Semantic chunking
* Structure-aware chunking
* Parent-child retrieval
* Metadata extraction
* Table and PDF challenges

### Build

Compare at least three chunking strategies on the same document collection.

Record:

* Retrieval quality
* Number of chunks
* Average chunk length
* Storage impact
* Answer quality

### Interview preparation

Answer:

> How would you choose the correct chunk size?

Your response should discuss document structure, retrieval unit, context budget and evaluation—not just a fixed number such as 500 tokens.

---

## Week 7 — Sparse and hybrid retrieval

### Learn

* BM25
* Keyword retrieval
* Dense versus sparse search
* Hybrid retrieval
* Score normalisation
* Reciprocal rank fusion
* Metadata filtering

### Build

Add BM25 to your project and compare:

* Dense retrieval
* Sparse retrieval
* Hybrid retrieval

Use procurement queries containing:

* Exact product codes
* Supplier names
* Commercial terms
* Semantic questions

### Interview preparation

Explain why dense search may perform poorly for product codes, abbreviations and exact identifiers.

---

## Week 8 — Reranking and context construction

### Learn

* Cross-encoder rerankers
* Bi-encoder versus cross-encoder
* Query rewriting
* Multi-query retrieval
* Context compression
* Deduplication
* Lost-in-the-middle problems

### Build

Add:

* Retrieval
* Reranking
* Deduplication
* Context formatting
* Source citations

Measure whether reranking improves the top retrieved documents.

### Project milestone

By the end of Week 8, you should have:

**Procurement Knowledge Assistant v1**

It should support document ingestion, hybrid retrieval, reranking, cited answers and basic logging.

# Phase 3: RAG Evaluation and Production Quality

## Week 9 — RAG evaluation fundamentals

### Learn

Separate evaluation into:

* Parsing quality
* Chunking quality
* Retrieval quality
* Context relevance
* Answer faithfulness
* Answer correctness
* Citation correctness

Understand:

* Precision@k
* Recall@k
* Mean reciprocal rank
* NDCG
* Exact match
* Semantic similarity
* LLM-as-judge
* Human evaluation

### Build

Create a test dataset with approximately:

* 30 questions
* Expected answers
* Relevant source documents
* Expected citations

Run your system and store the results.

### Interview preparation

Explain why evaluating only the final answer hides retrieval failures.

---

## Week 10 — Observability and tracing

### Learn

* Request tracing
* Prompt tracing
* Retrieval traces
* Tool traces
* Latency tracking
* Token usage
* Cost monitoring
* Failure classification
* Prompt and model versioning

### Build

Add traces for:

* User query
* Rewritten query
* Retrieved documents
* Reranking results
* Prompt
* Model response
* Token consumption
* End-to-end latency

### Interview preparation

Prepare a debugging workflow for:

> The assistant answered correctly last week but now answers incorrectly.

---

## Week 11 — RAG security

### Learn

* Prompt injection
* Indirect prompt injection
* Malicious documents
* Data exfiltration
* Sensitive-data leakage
* Retrieval poisoning
* Tenant isolation
* Access-controlled retrieval
* Input and output filtering

### Build

Add:

* Document-level access metadata
* User-level filtering
* Prompt-injection test cases
* Output validation
* Unsafe instruction detection
* Maximum context limits

### Interview preparation

Explain why hiding instructions in a system prompt is not a complete security control.

---

## Week 12 — Deploying the RAG service

### Learn

* FastAPI
* Async endpoints
* Streaming
* Docker
* Environment configuration
* Secrets management
* Health checks
* Caching
* Rate limiting

### Build

Deploy your assistant as:

* FastAPI backend
* PostgreSQL database
* Vector store
* Dockerised services
* Simple interface or API documentation

### Project milestone

By the end of Week 12, your RAG project should be demonstrable in an interview.

# Phase 4: Agentic AI

## Week 13 — Tool calling

### Learn

* Function definitions
* Tool schemas
* Tool selection
* Argument generation
* Structured validation
* Tool-result handling
* Retries
* Timeouts
* Idempotency
* Side-effect protection

### Build

Give the assistant tools for:

* SQL queries
* Price-variance calculation
* Supplier lookup
* Commodity-price lookup
* Document search

### Interview preparation

Explain:

* What happens when tool arguments are invalid
* How duplicate tool execution can cause damage
* How to make a write operation idempotent

---

## Week 14 — Workflows versus agents

### Learn

* Deterministic workflows
* LLM-based routing
* State machines
* Agent loops
* Planner-executor
* Evaluator-optimizer
* Orchestrator-worker
* Human approval

### Build

Implement one procurement investigation in two ways:

1. A deterministic workflow
2. An autonomous tool-using agent

Compare:

* Reliability
* Number of model calls
* Cost
* Latency
* Failure rate
* Explainability

### Interview preparation

Prepare to answer:

> When should you not use an agent?

---

## Week 15 — LangGraph fundamentals

### Learn

* State
* Nodes
* Edges
* Conditional routing
* Reducers
* Checkpointing
* Interrupts
* Persistence

### Build

Create a graph with:

* Query classification
* Document retrieval
* SQL analysis
* Price calculation
* Recommendation generation
* Validation
* Human approval

### Interview preparation

Explain why graph-based orchestration can be more reliable than an unrestricted agent loop.

---

## Week 16 — Memory and context engineering

### Learn

* Conversation state
* Working memory
* Long-term memory
* Semantic memory
* Episodic memory
* Summarisation
* Context selection
* Memory expiry
* Privacy
* Incorrect-memory prevention

### Build

Add case-level memory to your procurement agent.

The system should remember:

* Investigation objective
* Selected supplier
* Retrieved evidence
* Calculations
* Approval status

Do not store all raw conversation data indefinitely.

---

## Week 17 — Multi-agent systems

### Learn

* Supervisor-specialist pattern
* Handoffs
* Agent boundaries
* Shared state
* Parallel execution
* Coordination failures
* Error propagation
* When multi-agent designs are unnecessary

### Build

Create specialists for:

* Document analysis
* SQL analysis
* Supplier-risk assessment
* Commercial recommendation

The supervisor should combine results.

Then compare this architecture against the single-agent or graph workflow.

### Interview preparation

Be prepared to justify why each agent exists.

---

## Week 18 — Agent evaluation

### Learn

* Task-completion rate
* Tool-selection accuracy
* Tool-argument accuracy
* Step efficiency
* Loop rate
* Human escalation rate
* Cost per successful task
* Latency per task
* Unsafe-action rate

### Build

Create approximately 20–30 agent test cases.

Include:

* Normal requests
* Missing information
* Tool failures
* Conflicting evidence
* Prompt injection
* Invalid tool arguments
* Requests requiring approval

### Project milestone

By the end of Week 18, you should have:

**Procurement Intelligence Agent v1**

# Phase 5: Production Agent Systems

## Week 19 — Agent safety and guardrails

### Learn

* Least-privilege tools
* Read versus write permissions
* Approval gates
* Allowlisted operations
* Maximum-step limits
* Sandboxed execution
* Secret isolation
* Audit trails
* Reversible actions

### Build

Add:

* Human approval before write actions
* Maximum iteration limits
* Tool permission checks
* Full audit logging
* Safe failure responses

---

## Week 20 — Reliability and failure handling

### Learn

* Retries with backoff
* Circuit breakers
* Model fallbacks
* Tool fallbacks
* Timeout handling
* Queue-based processing
* Partial failure
* Graceful degradation
* Dead-letter queues

### Build

Simulate:

* LLM-provider outage
* Database timeout
* Invalid API result
* Vector-store failure
* Rate-limit errors

Document how the system behaves in each case.

---

## Week 21 — Cost and latency optimisation

### Learn

* Model routing
* Small versus large models
* Prompt compression
* Context pruning
* Semantic caching
* Response caching
* Parallel tool calls
* Batching
* Streaming
* Token budgeting

### Build

Compare:

* One large model for all tasks
* Small model for routing and extraction
* Large model only for complex recommendations

Track quality, latency and estimated cost.

---

## Week 22 — MCP and interoperable tools

### Learn

* MCP host
* MCP client
* MCP server
* Tools
* Resources
* Prompts
* Capability discovery
* Security boundaries

### Build

Expose one project capability through a small MCP server, such as:

* Supplier lookup
* Contract search
* Procurement-policy search
* Price analysis

MCP should remain a supporting topic, not the centre of your preparation.

# Phase 6: Interview Conversion

## Week 23 — GenAI system design

Practise designing:

* Enterprise RAG platform
* Procurement copilot
* Analytics assistant
* Customer-support agent
* Research agent
* Multi-tenant document assistant

Use this answer structure:

**requirements → metrics → data → architecture → retrieval/tools → model choice → evaluation → deployment → monitoring → security → cost → failure handling**

Record yourself answering at least two system-design questions.

---

## Week 24 — Project storytelling and mock interviews

Prepare your main project explanation at three depths:

### Two-minute version

* Business problem
* Solution
* Architecture
* Outcome

### Ten-minute version

* Requirements
* Major design decisions
* Evaluation
* Deployment
* Challenges
* Results

### Deep-dive version

Be prepared to defend:

* Chunking choice
* Embedding choice
* Agent versus workflow choice
* Evaluation design
* Security controls
* Cost
* Failure handling
* Scalability

Also prepare leadership stories around:

* Technical disagreement
* Mentoring
* Ambiguity
* Project failure
* Production issue
* Stakeholder communication
* Scope reduction
* Architectural decision

# Optional Phase 7: LLM Training Experiment

This comes **after the main 24-week track**. It is useful for learning, but you should not delay applications until it is complete.

## Week 25 — Training foundations

### Learn

* Pretraining objective
* Causal language modelling
* Dataset construction
* Tokenisation
* Training-validation split
* Optimisers
* Learning-rate schedules
* Gradient accumulation
* Mixed precision
* Checkpointing

### Experiment

Train a very small transformer on a small financial or procurement text corpus.

The goal is understanding the training loop, not building a useful production LLM.

---

## Week 26 — Data preparation

### Learn

* Deduplication
* Cleaning
* Language filtering
* Quality filtering
* Document mixing
* Contamination
* Licensing
* Personal information removal

### Build

Create a reproducible data pipeline that:

* Loads documents
* Cleans them
* Removes duplicates
* Chunks or packs sequences
* Tokenises
* Produces train and validation datasets

---

## Week 27 — Fine-tuning and LoRA

### Learn

* Full fine-tuning
* Parameter-efficient fine-tuning
* LoRA
* QLoRA
* Rank and alpha
* Target modules
* Catastrophic forgetting
* Training stability

### Experiment

Fine-tune a small open-weight model for:

* Financial question answering
* Procurement terminology
* Structured extraction
* Domain classification

---

## Week 28 — Instruction tuning

### Learn

* Instruction-response datasets
* Chat templates
* Supervised fine-tuning
* Dataset diversity
* Response formatting
* Overfitting
* Domain adaptation

### Build

Create a small instruction dataset from your domain and run supervised fine-tuning.

---

## Week 29 — Model evaluation

### Learn

* Perplexity
* Task-specific benchmarks
* Exact match
* Classification metrics
* Pairwise human evaluation
* LLM-as-judge limitations
* Baseline comparison

### Evaluate

Compare:

* Base model
* Prompted base model
* Fine-tuned model
* RAG system

A common result may be that RAG outperforms fine-tuning for factual knowledge. That is still a valuable experiment.

---

## Week 30 — Serving and documentation

### Learn

* Quantisation
* Model serving
* vLLM or equivalent serving tools
* Throughput
* Batching
* GPU memory
* Latency
* Model packaging

### Deliverable

Create an experiment report covering:

* Objective
* Dataset
* Training configuration
* Compute used
* Loss curves
* Evaluation
* Failures
* Cost
* Comparison with RAG
* Lessons learned

# What to do every week

Maintain four documents throughout the roadmap.

## 1. Interview notebook

Record:

* Concepts learned
* Questions you struggled with
* Improved answers
* Common mistakes

## 2. Architecture decision records

For each major project choice, document:

* Decision
* Alternatives
* Rationale
* Trade-offs
* Consequences

Examples:

* Why hybrid retrieval?
* Why LangGraph?
* Why not a fully autonomous agent?
* Why PostgreSQL?
* Why this reranker?

## 3. Evaluation log

Track:

* Dataset version
* Prompt version
* Model version
* Retrieval settings
* Metrics
* Failed cases

## 4. Weekly project changelog

Record what you completed each week. This helps with resume writing, GitHub documentation and interview storytelling.

# When to begin applying

You should not wait for Week 24.

Start in stages:

* **Week 4:** update resume and LinkedIn
* **Week 8:** begin applying selectively
* **Week 12:** actively apply to Senior Data Scientist–GenAI and Applied AI roles
* **Week 18 onward:** apply to stronger product companies and technical-owner roles
* **Week 24:** begin intensive interview cycles

# Minimum weekly schedule

A practical working-professional schedule:

| Day      |    Time | Work                            |
| -------- | ------: | ------------------------------- |
| Tuesday  |  1 hour | Concepts                        |
| Thursday |  1 hour | Concepts                        |
| Friday   |  1 hour | Interview questions             |
| Saturday | 3 hours | Side project                    |
| Sunday   | 2 hours | Side project, testing and notes |

On difficult work weeks, preserve at least:

* 1 hour learning
* 1 hour interview preparation
* 2 hours project work

Consistency is more important than occasionally doing a 12-hour weekend.

The main objective after 24 weeks is not to know every GenAI framework. It is to be able to **design, build, evaluate, secure, deploy and defend a production-grade RAG and agentic system**, while retaining sufficient Python, SQL, statistics, ML and leadership depth for a senior or technical-lead interview.
