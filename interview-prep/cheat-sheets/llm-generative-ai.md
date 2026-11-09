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
title: "LLM and Generative AI interview cheat sheet"
description: "LLM foundations, prompting, structured output, fine-tuning, post-training, evaluation, quantization, and production decisions."
summary: "Revise model types, generation, prompt and adaptation choices, LoRA/QLoRA, SFT/DPO, evaluation, safety, cost, release gates, and rollback."
permalink: "/interview-prep/cheat-sheets/llm-generative-ai/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 2 · LLM and Generative AI"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 2 source:** This page integrates the prepared revision artifact into the Prep site. It is separate from the Week 1–20 learning assessments.

**Target roles:** Generative AI Engineer, Agentic AI Engineer, ML Engineer, Applied Scientist, Senior/Lead Data Scientist  
**Use:** quick revision, model/prompt/fine-tuning decisions, evaluation, and production design  
**Boundary:** RAG, agents, inference engines, guardrails, and observability receive dedicated sheets in later batches; this sheet establishes the LLM foundation.

## 1. Thirty-second revision

- A language model estimates token probabilities; an assistant is a base model plus post-training, prompting, tools/retrieval, safety controls, and a serving system.
- **Base model:** pretrained continuation model. **Instruct model:** post-trained to follow instructions. **Reasoning model:** optimized to spend additional inference computation on difficult tasks.
- Temperature rescales logits; top-$p$ keeps a probability-mass nucleus; they change sampling, not factual knowledge.
- Prompting changes the input. RAG supplies external evidence. Fine-tuning changes model behavior/parameters. Choose the least complex option that meets evidence.
- Structured output constrains response shape; it does not prove the values are factually or semantically correct.
- LoRA learns low-rank updates; QLoRA trains adapters while the frozen base is quantized to reduce memory.
- SFT teaches demonstrations; preference optimization teaches relative preference. DPO avoids training an explicit reward model/PPO loop but still needs sound preference data and evaluation.
- Quantization reduces memory/bandwidth with possible quality or kernel trade-offs. Distillation transfers behavior from a teacher to a smaller student.
- LLM evaluation must include task quality, grounding, safety, latency, cost, robustness, and regressions—not a single judge score.
- A production answer must address data boundaries, access control, prompt injection, validation, fallback, monitoring, release gates, and rollback.

## 2. What an LLM actually does

For a token sequence $x_{1:n}$, a causal language model factorizes:

$$
p(x_{1:n})=\prod_{t=1}^{n}p(x_t\mid x_{<t})
$$

At each step it outputs logits over the vocabulary. A decoding policy selects the next token, which is appended to the context.

This gives the model powerful pattern completion and in-context learning, but not a guaranteed database of truth, deterministic program, or calibrated confidence estimator.

## 3. Model categories

### Base model

Optimized primarily for continuation. It may complete an instruction rather than obey it and can be awkward for chat without the correct template.

### Instruct/chat model

Post-trained on instruction/response and often preference data. It expects a specific chat template with role/control tokens.

### Reasoning-oriented model

Trained/post-trained to perform better on multi-step tasks, often using more inference tokens or internal computation. More visible reasoning text is not automatically more correct, faithful, or safe.

### Multimodal model

Accepts or produces more than text—images, audio, video, documents, or actions. The modality encoder/projector and its training distribution determine actual capability.

### Embedding and reranking models

Not chat generators. Embedding models create vectors for similarity/retrieval; rerankers score query-document pairs. They frequently produce better, cheaper retrieval systems than asking a general LLM to rank everything.

## 4. Open-weight versus hosted models

| Dimension | Hosted API | Self-hosted/open-weight |
|---|---|---|
| Operations | Provider manages serving | Team owns serving, capacity, upgrades |
| Upfront effort | Low | Higher |
| Control | Limited to API/options | Weights, runtime, adapters, topology |
| Privacy | Contract and provider controls | Can keep data in controlled environment |
| Elasticity | Often simple | Must provision/autoscale |
| Unit economics | Pay per use | Hardware + engineering; can win at sustained load |
| Reproducibility | Provider versions may change | Pin weights, tokenizer, runtime, config |
| License | Terms of service | Model license and downstream obligations |

“Open-weight” is not always “open-source.” Read the license, acceptable-use conditions, redistribution terms, and model card.

## 5. Model-selection scorecard

Evaluate candidates on the actual workload:

1. task accuracy and failure severity;
2. domain/language/modality coverage;
3. context and output-length distribution;
4. structured-output/tool-call reliability;
5. groundedness and refusal/abstention behavior;
6. time to first token, inter-token latency, and throughput;
7. input/output token cost or infrastructure cost;
8. concurrency, batching, KV-cache, and memory;
9. privacy, residency, security, and compliance;
10. license, support, version stability, and exit strategy.

Use a smaller candidate as the baseline. Route only harder or higher-value cases to an expensive model when the evaluation supports it.

## 6. Prompt anatomy

A reliable prompt contract commonly contains:

- **role/instruction:** what the system must do and must not do;
- **task:** the concrete requested outcome;
- **context/evidence:** data to use, with clear delimiters;
- **rules:** constraints, definitions, and refusal conditions;
- **examples:** representative input-output demonstrations;
- **output contract:** schema, units, allowed labels, and formatting;
- **uncertainty behavior:** when to abstain or ask for clarification.

Place stable, high-priority instructions clearly. Treat retrieved documents, web text, emails, and user attachments as untrusted data—not instructions with equal authority.

## 7. Prompting techniques

| Technique | Use | Risk/caveat |
|---|---|---|
| Zero-shot | Clear, familiar task | May miss format/domain nuance |
| Few-shot | Demonstrate labels, style, edge cases | Consumes context; examples can bias output |
| Decomposition | Split a difficult task into bounded steps | More calls, latency, and failure surfaces |
| Generate then verify | Separate proposal from checks | Verifier may share model blind spots |
| Self-consistency | Sample multiple solutions and aggregate | Higher cost; agreement is not proof |
| ReAct-style loop | Alternate reasoning and tool actions | Needs step/tool limits and reliable state |
| Prompt chaining | Pass validated outputs between stages | Error propagation if contracts are weak |

Do not request hidden chain-of-thought as a correctness mechanism. Ask for concise rationale, evidence, intermediate artifacts, or independently checkable calculations when needed.

## 8. Chat templates and instruction hierarchy

Chat models serialize roles into model-specific control tokens. A simplified conversation might contain system, user, assistant, and tool messages, but exact syntax differs.

Failure modes:

- using a base model as if it were an instruct model;
- double-applying a chat template;
- training with one template and serving with another;
- omitting the assistant-generation marker;
- placing untrusted content in the system role;
- truncating the system instruction or latest user request.

Version the template with model and tokenizer artifacts.

## 9. Decoding controls

Let logits be $z_i$. Temperature $T$ produces:

$$
p_i=\frac{\exp(z_i/T)}{\sum_j\exp(z_j/T)}
$$

| Control | Effect | Notes |
|---|---|---|
| Temperature | Flattens/sharpens distribution | $T\to0$ approaches greedy behavior; exact determinism still depends on stack |
| Top-$k$ | Keep $k$ highest-probability tokens | Fixed candidate count |
| Top-$p$ | Keep smallest set whose probability mass reaches $p$ | Adaptive candidate count |
| Max new tokens | Output budget | Distinguish from total context limit |
| Stop sequences | Stop on defined patterns/tokens | Can appear in content unexpectedly |
| Repetition controls | Penalize repeated tokens/patterns | Aggressive values can damage coherence |
| Seed | Helps reproducibility where supported | Hardware/kernels/service changes may still vary |

For classification/extraction, prefer low-variance decoding and schema/label constraints. For creative generation, allow measured diversity.

## 10. Structured output versus tool/function calling

### Structured output

The model returns data matching a schema, such as a JSON object. Use it when your application consumes the response directly.

### Tool/function calling

The model selects a registered operation and proposes arguments. Your code validates authorization and arguments, executes the tool, and may return the result for another model turn.

### Both still require validation

Schema validity proves shape/type constraints, not that:

- an extracted invoice total matches the document;
- a date exists or is within policy;
- a customer ID belongs to the current tenant;
- a refund amount is authorized;
- a cited passage supports the answer.

Validate semantic invariants in application code and require confirmation for consequential actions.

```python
from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class Priority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TicketDecision(BaseModel):
    category: str = Field(min_length=1, max_length=80)
    priority: Priority
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(min_length=1, max_length=5)
    escalate: bool

    @model_validator(mode="after")
    def enforce_escalation_policy(self) -> "TicketDecision":
        if self.confidence < 0.70 and not self.escalate:
            raise ValueError("low-confidence decisions must be escalated")
        return self
```

Parse into the schema, reject extra/invalid data according to policy, apply business checks, and log validation failures without exposing sensitive prompt content.

## 11. Hallucination, grounding, and abstention

“Hallucination” covers several failures:

- unsupported factual statement;
- contradiction of supplied evidence;
- fabricated citation or identifier;
- confident answer to an unanswerable question;
- incorrect tool result interpretation.

Controls include:

- retrieve authoritative, access-controlled evidence;
- require evidence identifiers and validate citation entailment;
- constrain generation to known labels/schemas;
- add calculators, databases, or deterministic checks;
- teach and measure abstention;
- separate answerability from answer generation;
- route high-risk/low-confidence cases to human review.

Prompting alone cannot guarantee factuality.

## 12. Context engineering and token budgets

The usable context must contain instructions, history, retrieved evidence, tool results, and output budget.

Manage it by:

- removing boilerplate and duplicates;
- retrieving only task-relevant evidence;
- prioritizing recent and authoritative state;
- summarizing older history while retaining decisions and identifiers;
- preserving source provenance;
- reserving output tokens;
- measuring token count by model tokenizer;
- testing placement sensitivity and truncation behavior.

Compression is lossy. Keep original sources available for verification and do not compress away permissions, negations, quantities, or audit-critical details.

## 13. Prompt caching and semantic caching

### Prefix/prompt caching

Reuses computation for identical shared prefixes where the provider/runtime supports it. It works best when long stable prefixes repeat exactly and are ordered consistently.

### Exact response caching

Returns a prior result for the same normalized request/model/config. Safe only when data, permissions, and freshness allow it.

### Semantic caching

Returns a result for a similar request. It can reduce cost but risks stale, cross-user, or subtly incorrect reuse.

Cache keys may need tenant/user scope, model/version, prompt version, tool/retrieval state, locale, policy version, and data freshness. Never let caching bypass authorization.

## 14. Prompt, RAG, fine-tune, or train?

| Need | Preferred first option | Why |
|---|---|---|
| Clear task and model already capable | Prompt/schema | Lowest complexity |
| Fresh/private/citable knowledge | RAG or tools | Changes evidence without retraining |
| Stable style, format, behavior, domain mapping | Fine-tuning | Changes behavior efficiently |
| New vocabulary/domain capability at scale | Continued pretraining + post-training | Expensive; needs strong data/evidence |
| New foundation capability | Train from scratch | Very high data/compute/research cost |

RAG and fine-tuning are complementary: RAG supplies evidence; fine-tuning can improve how the model uses it. Do not fine-tune to memorize rapidly changing facts.

## 15. Generative AI lifecycle

1. define tasks, risks, metrics, and baseline;
2. select/collect and govern data;
3. pretrain or choose a foundation model;
4. supervised fine-tune for desired behavior;
5. align preferences/safety where justified;
6. compress/quantize/package for target serving;
7. evaluate offline by slice and red-team;
8. release through shadow/canary gates;
9. monitor quality, safety, cost, drift, and incidents;
10. feed adjudicated failures into data/evaluation, not blindly back into training.

Every artifact should be versioned: weights/adapters, tokenizer, chat template, prompt, dataset, code, runtime, quantization, and evaluation set.

## 16. Supervised fine-tuning

SFT minimizes token-level loss on desired demonstrations. Quality depends more on data relevance and correctness than raw example count.

Data checks:

- source rights, privacy, and consent;
- deduplication and contamination against evaluation;
- valid roles/chat template and label masking;
- representative languages/tasks/difficulty;
- contradiction and annotation review;
- train/validation/test separation by source/entity/time where needed;
- regression coverage for base capabilities and safety.

Common overfitting symptoms include copied phrasing, brittle formatting, lost generality, and worsened rare-case behavior.

## 17. LoRA and adapters

LoRA freezes a base weight $W$ and learns a low-rank update:

$$
W' = W + \Delta W,\qquad \Delta W = \frac{\alpha}{r}BA
$$

where rank $r$ is small relative to the original dimensions.

Key choices:

- target modules (for example attention projections and/or FFNs);
- rank $r$ and scaling $\alpha$;
- adapter dropout;
- learning rate and sequence length;
- which modules remain trainable;
- whether to keep adapters separate or merge for deployment.

LoRA reduces trainable parameters and optimizer state, but activations and the base model still consume memory.

## 18. QLoRA

QLoRA keeps the pretrained base quantized and trains LoRA adapters, substantially reducing fine-tuning memory. Core idea:

- load a supported low-bit frozen base;
- compute through dequantization-aware kernels;
- train higher-precision adapter parameters;
- save adapter/config separately or merge only when supported and validated.

It does not mean all training occurs in 4-bit arithmetic, nor that every quantization/model/runtime combination is equally supported. Evaluate final quality and deployment compatibility.

Illustrative PEFT configuration:

```python
from peft import LoraConfig, TaskType


config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    bias="none",
)
```

Module names are architecture-specific; inspect the model instead of copying a target list blindly.

## 19. Preference optimization

### Reward model + PPO-style RLHF

1. collect ranked response pairs;
2. train a reward model;
3. optimize the policy to increase reward while controlling drift from a reference policy, often using a KL term.

This is flexible but operationally complex and can exploit reward-model weaknesses.

### Direct Preference Optimization

DPO directly optimizes preference pairs relative to a reference model using a classification-style objective. It avoids a separate learned reward model and online PPO loop.

Still required:

- trustworthy chosen/rejected pairs;
- control of length/style shortcuts;
- reference and beta/hyperparameter choices;
- held-out task, safety, and capability regression tests.

### GRPO-style awareness

Group-relative objectives compare rewards among multiple sampled completions, often used in reasoning post-training. The exact algorithm/reward design matters. Verifiable rewards can help, but reward hacking and narrow specialization remain risks.

## 20. Distillation

A teacher produces soft targets, demonstrations, rationales, preference data, or synthetic tasks for a smaller student.

Potential benefits:

- lower latency and cost;
- domain/task specialization;
- deployment on constrained hardware.

Risks:

- teacher errors and bias are copied;
- synthetic data becomes repetitive or contaminated;
- student capacity is insufficient;
- licensing/terms may restrict generated-data use;
- headline benchmark gains may hide capability loss.

Evaluate the student independently on human-curated and adversarial sets.

## 21. Quantization overview

| Method | When | Main point |
|---|---|---|
| Post-training quantization | After training | Fast path; calibration may be required |
| Quantization-aware training | During training/fine-tuning | Simulates low precision; more effort |
| Weight-only quantization | Primarily weights | Reduces model storage/bandwidth |
| Weight + activation quantization | Weights and activations | Greater speed/memory opportunity, harder quality/kernel problem |
| KV-cache quantization | Serving cache | Helps long context/concurrency; may affect quality/support |

Memory savings do not guarantee latency gains. Kernel availability, dequantization overhead, batch size, hardware, and bottlenecks determine speed.

## 22. Evaluation framework

### Quality dimensions

- correctness and completeness;
- groundedness/faithfulness and citation accuracy;
- relevance and instruction following;
- schema/tool-call correctness;
- robustness across paraphrases and noise;
- safety, privacy, fairness, and refusal behavior;
- language/domain slices and long-tail cases.

### Operational dimensions

- time to first token and inter-token latency;
- p50/p95/p99 end-to-end latency;
- input/output tokens and cost per request;
- throughput and concurrency;
- retry, timeout, invalid-output, fallback, and successful-task rates.

### Methods

- deterministic rules and schema validation;
- exact match, unit tests, code execution, and reference calculations;
- human scoring with a clear rubric and agreement measurement;
- pairwise comparison and confidence intervals;
- calibrated LLM-as-judge;
- adversarial/red-team suites;
- online experiments with guardrails where appropriate.

## 23. LLM-as-judge limitations

Judges can show position, verbosity, style, self-preference, and domain biases. A strong process:

1. define a task-specific rubric;
2. randomize/swap answer order;
3. hide irrelevant identity information;
4. include reference evidence where required;
5. calibrate against expert human labels;
6. report judge-human agreement and disagreement slices;
7. use multiple checks for high-stakes gates;
8. retain deterministic checks whenever possible.

An LLM judge is a measurement instrument, not ground truth.

## 24. Security and privacy essentials

- Treat prompts, retrieved text, web pages, files, tool results, and memory as potentially hostile.
- Enforce authorization in code before retrieval and tool execution.
- Use least-privilege, allowlisted tools with typed schemas and bounded arguments.
- Separate instructions from untrusted content and resist indirect prompt injection.
- Redact/minimize sensitive data and define retention/logging policies.
- Do not place secrets in prompts; protect service credentials outside model context.
- Sandbox code/file/network actions and require approval for consequential operations.
- Validate outputs before they become SQL, shell commands, messages, or transactions.
- Test exfiltration, cross-tenant leakage, excessive agency, denial of service, and unsafe fallback.

Guardrails are defense in depth; they do not replace access control and safe application design.

## 25. Library and ecosystem map

| Need | Common libraries/platforms | What they are for |
|---|---|---|
| Model definitions/inference/training | Hugging Face Transformers, PyTorch | Load/run/train transformer models |
| Data | Hugging Face Datasets, PyTorch Data | Dataset processing, streaming, batching |
| Tokenization | Hugging Face Tokenizers, SentencePiece | Train/apply tokenizers |
| Distributed launch/training | Accelerate, FSDP, DeepSpeed | Device placement, sharding, distributed execution |
| Parameter-efficient tuning | PEFT | LoRA/adapters and related methods |
| Post-training | TRL | SFT, DPO, reward/preference/RL workflows |
| Low-bit training/loading | bitsandbytes and model-specific kernels | Quantized weights/optimizers where supported |
| NVIDIA training/customization | NeMo Framework/AutoModel | NVIDIA-centered model training/customization stack |
| NVIDIA model families | Nemotron | Models/datasets/recipes; not itself an agent framework |
| Local/simple serving | Ollama, llama.cpp | Convenient local or quantized inference |
| High-throughput serving | vLLM, TensorRT-LLM, SGLang | Batching, KV-cache management, optimized serving |
| Provider abstraction | LiteLLM | OpenAI-style gateway/routing across providers |
| Experiment/evaluation tracking | MLflow, Weights & Biases, evaluation frameworks | Artifacts, metrics, comparisons |

Names are not architecture decisions. Check model support, version compatibility, license, kernel/hardware fit, maintenance, and measured behavior.

### Frequently confused NVIDIA names

- **Nemotron:** NVIDIA-branded model/model-data/reward-model families and recipes.
- **NeMo Framework:** tooling for training, adapting, and scaling models in the NVIDIA ecosystem.
- **NeMo Guardrails:** programmable conversational/AI guardrail layer; it does not make a model inherently safe.
- **NIM:** packaged inference microservices for supported models.

## 26. Hosted and self-hosted production patterns

### Hosted API path

- provider adapter/gateway;
- deadlines, bounded retries, idempotency where actions occur;
- rate limiting and fallback policy;
- prompt/model version pinning when available;
- cost/token telemetry and data-governance review.

### Self-hosted path

- model/runtime compatibility and quantization;
- GPU memory for weights, KV cache, activations/workspace, and headroom;
- continuous batching and admission control;
- tensor/pipeline/data/expert parallelism where justified;
- autoscaling, cold-start strategy, health/readiness, and rollback;
- model artifact integrity and license tracking.

Avoid retry storms: enforce a total deadline, exponential backoff with jitter, retry only transient failures, and use circuit breaking/backpressure.

## 27. Monitoring and release gates

Monitor:

- request volume, queue, timeout, failure, and fallback rates;
- TTFT, tokens/s, end-to-end percentiles, GPU/CPU/memory/utilization;
- token/cost distribution and cache hit rate;
- schema validation and tool execution failures;
- sampled quality, grounding, safety, and human-escalation outcomes;
- input/domain/language mix and known failure slices;
- model/prompt/retriever/tool/policy version per trace.

Release only when critical evaluation slices meet thresholds. Shadow/canary the change, compare against the incumbent, define automatic/manual rollback triggers, and keep artifacts reproducible.

## 28. Common interview traps

- Treating temperature 0 as a universal guarantee of identical output.
- Claiming structured JSON guarantees truth.
- Fine-tuning to inject frequently changing knowledge.
- Selecting a model by parameter count or leaderboard alone.
- Reporting average latency while hiding p95/p99 and failures.
- Using the same examples for training, prompt demonstrations, and evaluation.
- Calling QLoRA “training the whole model in 4-bit.”
- Assuming quantization always improves speed.
- Using one LLM judge as ground truth.
- Letting retrieved text or tool output override system policy.
- Logging full prompts/responses without privacy controls.
- Building an autonomous workflow where a deterministic service is sufficient.

## 29. Rapid interview questions and answers

1. **Base versus instruct model?** A base model learns continuation; an instruct model is post-trained to follow requests and chat conventions.
2. **Temperature versus top-$p$?** Temperature rescales the distribution; top-$p$ truncates it to an adaptive probability-mass set.
3. **Prompt versus RAG versus fine-tuning?** Prompt defines behavior, RAG provides external evidence, and fine-tuning changes learned behavior.
4. **What does structured output guarantee?** Schema-conformant shape when successfully enforced—not factual correctness.
5. **LoRA benefit?** Train small low-rank updates while freezing the base, reducing trainable parameters and optimizer memory.
6. **QLoRA benefit?** Keep the frozen base quantized while training adapters, lowering fine-tuning memory.
7. **DPO versus RLHF/PPO?** DPO directly learns from preference pairs relative to a reference; PPO-style RLHF uses a reward signal and online policy optimization.
8. **How reduce hallucination?** Ground with authoritative evidence/tools, validate claims/citations, constrain outputs, evaluate answerability, and abstain/escalate.
9. **How choose a model?** Use task-specific quality plus latency, cost, privacy, context, modality, license, and operational fit.
10. **Why can an LLM judge mislead?** It has systematic biases and model errors; calibrate it against human/deterministic evidence.

## 30. Lead-level case: enterprise assistant

**Question:** Design a private procurement assistant that answers policy questions, extracts fields, and can draft—but not autonomously send—supplier emails.

**Strong answer structure:**

1. Separate answer, extraction, and drafting tasks; define users, data classifications, actions, risks, and success metrics.
2. Establish deterministic/search baselines and a versioned golden set with answerable/unanswerable, multilingual, prompt-injection, and access-control cases.
3. Retrieve only documents authorized for that user; retain source IDs and effective dates.
4. Use structured schemas for extracted fields and deterministic validation against procurement systems.
5. Keep email sending outside the model; require a human preview/approval and revalidate recipients/content at action time.
6. Compare hosted and self-hosted models using privacy, accuracy, p95 latency, throughput, and cost per successful task.
7. Use prompt/RAG first; fine-tune only if repeated stable behavior gaps remain after prompt and data fixes.
8. Add citation entailment, abstention, injection tests, PII minimization, least-privilege tools, and audit logs.
9. Trace model/prompt/retrieval/tool versions; monitor invalid outputs, unsupported claims, escalations, latency, cost, and confirmed user corrections.
10. Canary releases, gate critical regressions, preserve rollback, and convert adjudicated failures into new evaluation cases.

## 31. Hardware-constrained fine-tuning case

**Question:** You have one 8 GB GPU locally and access to two 16 GB T4 GPUs. How would you adapt a model for email classification and response drafting?

**Strong answer:**

- Start with TF-IDF/encoder baselines for classification; do not force generation into every task.
- Benchmark a small instruct model zero/few-shot for drafting with a schema/rubric.
- If fine-tuning is justified, use a small model, short measured sequence lengths, QLoRA/LoRA, gradient accumulation, mixed precision supported by T4, and gradient checkpointing.
- Keep adapters/version metadata separate; evaluate before merging.
- Use group/time-aware splits to avoid template/customer leakage.
- Report macro F1/calibration for classification and human/rubric/grounding metrics for drafting.
- Benchmark inference under realistic concurrent prompts; model weights fitting is not proof that serving capacity is adequate.
- Compare total engineering/hardware cost with a hosted API and retain an exit path.

## 32. Final revision checklist

- [ ] I can distinguish base, instruct, reasoning, multimodal, embedding, and reranking models.
- [ ] I can explain temperature, top-$p$, stop conditions, and output budgets.
- [ ] I can design a prompt and chat-template contract.
- [ ] I can distinguish structured output from function/tool calling.
- [ ] I can choose prompt, RAG, fine-tuning, or training from scratch.
- [ ] I can explain SFT, LoRA, QLoRA, RLHF/PPO, DPO, and distillation.
- [ ] I can design an evaluation across quality, safety, latency, cost, and regressions.
- [ ] I understand LLM-as-judge bias and calibration.
- [ ] I can explain Nemotron, NeMo Framework, NeMo Guardrails, and serving libraries without conflating them.
- [ ] I can design authorization, validation, monitoring, canary, and rollback around an LLM.

## Primary references

- [Hugging Face Transformers documentation](https://huggingface.co/docs/transformers/)
- [Hugging Face PEFT documentation](https://huggingface.co/docs/peft/)
- [Hugging Face TRL documentation](https://huggingface.co/docs/trl/)
- [Direct Preference Optimization](https://arxiv.org/abs/2305.18290)
- [Google Cloud: Introduction to prompting](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/introduction-prompt-design)
- [Google Cloud: Structured output](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/control-generated-output)
- [NVIDIA NeMo documentation](https://docs.nvidia.com/nemo-framework/)
