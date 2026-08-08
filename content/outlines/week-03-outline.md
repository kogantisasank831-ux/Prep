---
week: 3
phase: 1
title: LLM foundations
status: draft
version: 0.1.0
estimated_hours: 16-20
week_2_dependency: deferred-behind-storage-port
execution_mode: local-only
---

# Week 3 outline: LLM foundations

## Objective

Build a first-principles mental model of how a prompt becomes tokens, hidden
representations, next-token probabilities, and generated text. Apply that model
by running the same controlled prompts against two models, recording comparable
measurements, and separating observed output from claims about model quality.

The lesson teaches one dependent concept at a time. It does not begin with an
SDK call or a complete Transformer diagram.

## Relationship to the deferred Week 2

Week 3 does not require joins, indexing, normalization, or transaction design.
The comparison application will create a typed, versioned experiment record and
write through a narrow storage interface. The Week 3 adapter uses JSONL v1 with
single-writer atomic append semantics. The later Week 2 work can design a
relational schema and replace the adapter while preserving the versioned storage
contract and model/evaluation boundaries.

Database schema, query design, and index selection therefore remain deferred.

## Prerequisites

- Week 1 Python boundaries: typed interfaces, Pydantic validation, exceptions,
  safe logging, dependency injection, async fundamentals, and pytest.
- Basic vectors, dot products, probability distributions, and neural-network
  terminology.
- Basic HTTP and JSON familiarity.
- Basic local-process operation: start, stop, inspect a health endpoint, and
  distinguish process startup from request execution.
- Sufficient local disk for two pinned GGUF artifacts, an NVIDIA driver capable
  of loading the selected CUDA build, and acceptance of the recorded model and
  runtime licenses.
- No SQL knowledge is required for this week.

The lesson must provide short intuition refreshers for vectors, softmax, and
matrix-shaped data rather than assuming a deep-learning derivation course.

## Measurable learning outcomes

By the end of Week 3, the learner should be able to:

1. Explain why an LLM processes tokens rather than words and show how token
   boundaries affect length, cost, truncation, and model input.
2. Distinguish token IDs, token embeddings, contextual hidden states, and
   standalone embedding-model outputs.
3. Trace autoregressive generation from prompt tokens to logits, a probability
   distribution, token selection, and repeated decoding.
4. Explain the limitations of sequential recurrent processing that motivated
   attention-based architectures, without claiming Transformers dominate every
   sequence problem.
5. Explain self-attention using query, key, and value roles; reason about masking,
   multiple heads, and the main computational trade-off.
6. Explain why token order must be represented explicitly and compare learned,
   sinusoidal, and rotary positional approaches at the appropriate depth.
7. Reconstruct the major components and data flow of a decoder-only Transformer
   block: embeddings, attention, residual paths, normalization, feed-forward
   network, and output projection.
8. Distinguish pretraining, supervised instruction tuning, and preference-based
   alignment by objective, data, and resulting behavior.
9. Explain context-window accounting and why a larger advertised window does not
   guarantee better retrieval, reasoning, instruction following, latency, or
   cost.
10. Explain temperature, greedy decoding, top-k, top-p, maximum output tokens,
    and seeds without treating them as universal quality controls.
11. Categorize major hallucination causes and distinguish model uncertainty from
    missing knowledge, ambiguous prompts, conflicting context, and decoding
    variability.
12. Compare hosted and open-weight models across control, privacy, licensing,
    hardware, latency, observability, operations, and total cost while keeping
    the Week 3 implementation entirely local.
13. Design and implement a reproducible two-model comparison that records
    outputs, latency, token usage or clearly marked unavailable estimates,
    parameters, exact model-artifact and runtime provenance, errors, and
    evaluation notes without treating cross-tokenizer counts as equivalent.
14. Defend Week 3 decisions in interview discussion without relying on memorized
    framework terminology.

## Concept-first teaching sequence

Every core unit uses: orienting question, first-principles explanation, small
example or diagram, boundary/counterexample, checkpoint, and bridge.

1. **One prompt, two different continuations.** Establish the observation to
   explain. Define the comparison contract without introducing model SDKs.
2. **Text becomes tokens.** Characters, words, subwords, token IDs, vocabulary,
   encode/decode, and why token counts vary across models and languages.
3. **IDs become vectors.** Token-embedding lookup, vector intuition, and the
   difference between an embedding table, contextual hidden state, and an
   embedding model. Do not introduce attention yet.
4. **Generation is repeated next-token prediction.** Logits, softmax intuition,
   selection, append, repeat, and stopping. Introduce autoregression before
   Transformer internals.
5. **Why sequence models needed a different dependency path.** Explain recurrent
   bottlenecks and long-range information, then motivate direct token-to-token
   interaction. Avoid the false claim that Transformers universally replaced
   recurrent architectures.
6. **One attention head mixes information.** Query as the current lookup, keys
   as match descriptors, values as carried information, followed by scaled
   dot-product scores and a weighted sum. Add shapes only after intuition.
7. **Causality constrains what a token may inspect.** Introduce the causal mask
   as a separate mental model and connect it to next-token training and decoding.
8. **Multiple heads create multiple learned interaction spaces.** Extend the
   single-head mechanism only after its data flow and limitations are clear.
9. **Order does not come for free.** Show why identical token sets in different
   orders need positional information. Introduce learned positions, sinusoidal
   encoding, and RoPE conceptually. When the block is assembled, make explicit
   where each positional mechanism affects the attention computation.
10. **Residual paths preserve and update a representation.** Explain residual
    addition and normalization without yet presenting the complete block.
11. **The feed-forward sublayer transforms each position.** Explain the
    position-wise MLP, nonlinearity, and expansion/contraction role separately
    from token-to-token mixing.
12. **Assemble and stack decoder blocks.** Combine positional information,
    masked multi-head attention, residual paths, normalization, feed-forward
    transformation, stacking, final projection, and logits. Revisit the complete
    training and inference data flow only after every component is established.
13. **How the base model learns.** Pretraining data/objective, next-token loss,
   scale, memorization versus generalization, cutoffs, and why the objective does
   not guarantee truthfulness.
14. **How a base model becomes an assistant.** Supervised instruction tuning and
    preference alignment, what each changes, and what each cannot guarantee.
15. **Context is a bounded input workspace.** Input/output token budgets,
    truncation, position effects, distraction, latency/cost, and why more context
    is not automatically better. KV-cache capacity calculation is explicitly
    deferred to a serving/capacity lesson.
16. **Sampling changes selection, not knowledge.** Greedy, temperature, top-k,
    top-p, maximum output tokens, stop behavior, and limited determinism. Change
    one parameter at a time in examples.
17. **Why plausible falsehoods occur.** Connect training objective, unavailable
    knowledge, prompt ambiguity, context quality, and sampling to distinct
    failure modes. Avoid describing hallucination as one bug with one fix.
18. **Hosted versus open-weight is an operating-model decision.** Compare the
    conceptual boundaries, but make no hosted call in the Week 3 build.
19. **A local server is an external boundary.** Introduce the native Windows
    CUDA `llama-server` process, localhost health/startup contract, sequential
    model loading, chat templates, tokenizer coupling, and artifact provenance.
20. **Build the comparison harness.** Introduce one configurable HTTP adapter,
    validated request/result records, safe timing, stable errors, logging, and
    JSONL storage after the model concepts are understood.
21. **Run a controlled comparison.** Use frozen prompts and parameters, explicit
    warm-up and cache policies, measured repetitions, honest token accounting,
    and blinded human evaluation. Do not declare one model "better" from one
    prompt or generalize this bounded experiment to model families.
22. **Consolidate.** Complete request traces, common mistakes, interview questions
    by level, active recall, exercises, and a bounded mini-project.

## Build contract

Create a Python application that sends the same versioned prompt cases through a
common typed interface to two self-hosted models. No request may leave the
machine.

### Locked runtime and model decisions

- Runtime boundary: native Windows CUDA `llama-server`, bound to
  `127.0.0.1`, accessed over localhost HTTP by the Python harness.
- Client boundary: one configurable HTTP adapter, instantiated with the active
  local endpoint and expected model identity. Two provider abstractions are not
  required because both models use the same runtime contract.
- Models:
  - `Qwen/Qwen2.5-1.5B-Instruct-GGUF:Q4_K_M`;
  - `Qwen/Qwen2.5-7B-Instruct-GGUF:Q4_K_M`.
- Initial runtime limits: context size 4096 and maximum generated tokens 512.
- Loading policy: run one model at a time. Stop the current server, start the
  next model, wait for a successful health response, perform the declared
  warm-up, and only then collect measured trials.
- GPU policy: first attempt full GPU offload. Reduce GPU-offloaded layers only
  after an observed load failure, preserve that failure, and record the attempted
  and effective settings. Never silently choose a different configuration.
- License baseline: both selected model repositories declare Apache-2.0 and
  `llama.cpp` declares MIT. Verify and record the license texts at the pinned
  revisions before downloading or publishing instructions.
- Feasibility on the supplied RTX 3070 Ti with 8 GB VRAM and 16 GB system RAM is
  an inference to test, not a guarantee. A successful health check and a bounded
  smoke generation are the implementation-time fit gates for each artifact.
- Hosted inference and paid APIs are prohibited. Hosted versus open-weight
  remains a conceptual comparison only.

The Python application and the local server remain separate processes. The
harness does not own installation or silently launch, kill, replace, or download
the server/model. It validates the configured localhost endpoint, checks health
and expected model identity, and fails with a stable startup/configuration error
when the boundary is not ready.

### Required components

- `ModelClient` protocol with one narrow, typed generation operation and explicit
  timeout/cancellation behavior. The comparison service depends only on this
  protocol.
- One `llama-server` HTTP adapter. Runtime response objects do not enter the
  domain comparison service.
- Validated generation request containing experiment, run, trial, prompt-suite,
  and prompt-case identifiers; canonical prompt text submitted as the sole user
  content; prompt hash; sampling and stop parameters; seed; maximum output
  tokens; streaming mode; and timeout. System/tool-message design remains Week 4.
- A discriminated success/failure result. Every result records:
  - JSONL schema version and adapter/configuration version;
  - experiment, run, trial, suite, and prompt-case identifiers;
  - UTC start timestamp and canonical prompt hash;
  - runtime name, pinned runtime version/commit, API route, and server arguments;
  - source model repository and revision, exact GGUF filename and SHA-256,
    quantization, declared license and verified license revision;
  - model-reported identity, chat-template identity/hash, tokenizer identity,
    context size, maximum output tokens, requested/effective GPU-offload layers,
    and all sampling/stop/seed/stream settings;
  - OS version, GPU model/VRAM, system RAM, NVIDIA driver version, CUDA backend
    information reported by the runtime, CPU/thread settings, and harness version;
  - generated text for success, or a stable failure category and sanitized error
    detail for failure;
  - metric values, units, boundaries, source, and explicit `null` plus an
    unavailability reason when a metric is not exposed; and
  - raw-measurement provenance separate from optional human evaluation records.
- Comparison service that invokes each configured model independently and
  preserves successful and failed trials without overwriting either.
- Safe logs that avoid full prompts/outputs and model download credentials by
  default. Generated text is data: never execute it or render it as trusted HTML.
- Deterministic unit tests using fake clients and a small opt-in integration test
  boundary for the two explicitly configured local models.

### JSONL v1 storage contract

- Each UTF-8 line is one complete envelope with `schema_version: 1`, a stable
  `record_id`, `record_type`, experiment/run/trial identifiers, and a typed
  payload. Raw measurements and human evaluations use different record types.
- The adapter is single-writer. It serializes one line in memory, appends the
  complete line plus newline under an exclusive process lock, flushes, and calls
  the platform durability primitive before reporting success.
- `record_id` is unique and append is idempotent: an already persisted identical
  record is a no-op; the same ID with different content is a conflict. No record
  is updated or deleted in place.
- Readers reject or quarantine a malformed/truncated final line and report its
  byte offset; they do not silently skip corruption. Recovery is an explicit
  copy-to-new-file operation outside the measured run.
- The storage port exposes append and read operations in terms of versioned
  envelopes, allowing Week 2 persistence to implement the same contract without
  importing SQL concerns into the comparison service.

### Measurement protocol

- Use non-streaming generation for the baseline. Time with a monotonic clock from
  immediately before HTTP request dispatch until the complete response body is
  received and validated; record this as client-observed request wall time. It
  includes localhost transport and server queueing and is not pure inference
  time. Time to first token is `null` for this protocol.
- Record model-load readiness separately when the operator uses the supplied
  startup measurement command: elapsed monotonic time from native server process
  invocation until the health endpoint first reports ready. This operational
  observation is outside the comparison harness and is never included in request
  wall time. If it is not captured, store `null` with the reason.
- Perform one declared, unmeasured warm-up request after each model load. Record
  the cache policy supported by the pinned runtime. If cache reuse cannot be
  disabled or reset, state that limitation and never describe trials as
  cache-isolated.
- Run three measured trials per held-out case and model. Use a recorded seed for
  deterministic prompt ordering within each sequential model block. Preserve
  the model-block order and acknowledge thermal/order effects rather than
  presenting the result as a serving benchmark.
- Record runtime-reported prompt and generated token counts and prompt/decode
  durations only when exposed by the verified API. Mark their source as
  `runtime_reported`; derived metrics name their formula and inputs. Otherwise
  store `null` and a reason. Never fabricate or silently estimate counts.
- The same canonical prompt text is supplied to both models as one user turn.
  Do not assume their chat templates or tokenizers are identical: verify and
  record their identities/hashes and the resulting input counts. If they differ,
  interpret token counts and tokens/second within each model rather than treating
  raw counts or throughput as directly equivalent.

### Quality comparison rubric

Use prompt cases with explicit expected properties rather than an undefined
“quality” score:

- instruction following;
- factual support against supplied reference text;
- format adherence;
- completeness;
- unsupported claims;
- concision/relevance; and
- evaluator notes and uncertainty.

Score each applicable property on anchored values: `0` = violated, `1` = partly
or ambiguously satisfied, and `2` = satisfied. Use `null/not_applicable` rather
than forcing a score. Each evaluation records blinded output ID, rubric version,
evaluator ID, UTC timestamp, notes, and uncertainty.

Human scores remain separate from latency and token measurements. No single
weighted leaderboard is produced for Week 3.

### Evaluation protocol and leakage controls

- Create a small calibration suite for harness and rubric debugging, then freeze
  a separate held-out suite, reference material, expected properties, rubric,
  model/configuration choices, and hashes before either model generates held-out
  output.
- Calibration outputs may change prompts or parameters. Held-out outputs may not:
  after the first held-out generation, do not tune prompts, rubric anchors,
  parameters, model artifacts, or selection rules against those results. A
  changed protocol creates a new version and a new held-out run.
- Strip model identity from evaluation views, assign stable opaque output IDs,
  and deterministically randomize presentation order with a recorded seed. Store
  the identity mapping separately until scoring is complete.
- Preserve all held-out outputs and failures. Do not select a preferred sample
  from repeated trials before scoring.
- Prefer bespoke, reference-backed cases over public benchmark items. Still state
  that unknown pretraining contamination cannot be excluded.
- Treat the result as a bounded observational comparison confounded by model
  size, quantization, tokenizer, chat template, and training data. It does not
  establish a causal architecture claim or general model-family ranking.

## Interview outcomes

The learner must be able to answer and defend:

- Why did Transformers replace recurrent architectures for many large-scale
  language-model workloads, and where is that statement too broad?
- What is the difference between a token embedding, contextual representation,
  and a sentence/document embedding?
- What do queries, keys, and values do in self-attention?
- Why is positional information necessary?
- How do pretraining and instruction tuning differ?
- Why can a fluent model hallucinate?
- Why does a larger context window not guarantee a better answer?
- How do temperature, top-k, and top-p interact?
- When is a hosted model preferable to an open-weight deployment, and vice versa?
- Why are latency and token counts not sufficient measures of model quality?
- How would you make a two-model comparison reproducible and honest?

## Explicitly out of scope

- Training or fine-tuning a model in code.
- Full backpropagation derivations or exhaustive Transformer mathematics.
- Deriving GPU memory or KV-cache formulas, implementing quantization, continuous
  batching, vLLM, or production serving-capacity planning. Selecting and
  verifying the pinned GGUF artifacts, CUDA offload, context cap, server health,
  and local fit are in scope because the build depends on them.
- Prompt-engineering patterns, structured output, retry design, and prompt
  versioning beyond what the comparison record minimally needs; these belong to
  Week 4.
- Retrieval, vector databases, RAG, agents, or tool calling.
- SQL schema design, migrations, and database indexes; these remain Week 2.
- Production deployment, autoscaling, multi-tenancy, authentication, billing, or
  runtime failover.
- Benchmark claims based on uncontrolled public leaderboards or a handful of
  prompts.

## Technical and evaluation guardrails

- Treat model output as untrusted text.
- Bind the server to `127.0.0.1`; do not expose it to the LAN or internet. Make no
  hosted inference call and do not add a paid API dependency.
- Do not place secrets, PII, financial records, or other sensitive material in
  prompts merely because inference is local. Never log full sensitive prompts,
  outputs, credentials, or model-download tokens.
- Obtain artifacts only from the locked repositories, pin revisions and hashes,
  scan/download through approved tooling, and record license provenance. Treat
  model files and runtime binaries as supply-chain inputs, not trusted source.
- Record exact runtime, artifact, configuration, hardware, and timestamps because
  local behavior changes with every one of those inputs.
- Distinguish runtime-reported measurements from derived values and unavailable
  fields. Client-observed wall time includes localhost transport and queueing.
- State warm-up, cache, process-restart, model-order, retry, and streaming policy.
  Retries do not replace failed measured trials.
- Do not claim deterministic equivalence between models from a shared seed or
  temperature of zero.
- Do not call generated text “correct” without an explicit reference or human
  evaluation rule.
- Verify the pinned `llama-server` API, health behavior, usage/timing fields,
  model artifacts, chat templates, licenses, and runtime compatibility against
  authoritative primary sources before finalizing commands or recommendations.

## Unresolved implementation pins

Before implementation or command generation, pin and record:

1. the exact `llama.cpp` release or commit and Windows CUDA binary SHA-256; and
2. each selected repository revision, resolved Q4_K_M GGUF filename, artifact
   SHA-256, chat-template identity/hash, and license-file revision.

These are verification tasks, not open architecture choices. Content generation
must mark commands or fields that depend on them as unresolved until verified.

## Acceptance criteria

- All `Path.md` Week 3 learning topics and interview outcomes are explicit.
- Skipping Week 2 introduces no hidden SQL prerequisite.
- Tokenization precedes embeddings; embeddings precede attention; autoregressive
  generation precedes Transformer internals.
- Sampling is taught after logits/probabilities and separately from model
  knowledge.
- Context length is not conflated with memory capacity or answer quality.
- Hosted/open-weight trade-offs are explained before specific product choices.
- The build uses only the native Windows CUDA `llama-server` localhost boundary,
  one configurable adapter, and the two locked Qwen2.5 GGUF models sequentially.
- Context is initially 4096 and maximum output is 512; full GPU offload is tried
  first and any fallback follows a preserved, observed load failure.
- Local hardware feasibility is reported only after health and smoke-generation
  verification, never promised from nominal model size.
- The build records measurement provenance and unavailable values honestly.
- Chat-template/tokenizer differences, model-load time, warm-up, caching, model
  order, and client-observed latency boundaries are recorded explicitly.
- Model quality uses explicit criteria and does not collapse into latency or one
  subjective score.
- Calibration and frozen held-out suites are separate; held-out evaluation is
  blinded, retains all trials, and cannot be used for same-version retuning.
- JSONL v1 records are versioned, append-only, single-writer, idempotent by record
  ID, and explicit about corruption.
- Code, commands, citations, model names, APIs, and usage accounting are verified
  before publication.
- The candidate receives technical review and explicit human approval before it
  replaces any canonical public content.
