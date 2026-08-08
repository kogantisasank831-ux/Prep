---
layout: week
permalink: /weeks/week-03/beginner/
title: "LLM foundations—a simpler introduction"
description: Build an intuitive mental model of tokens, Transformers, generation, and controlled local-model comparison before entering the production lesson.
summary: Follow one supplier note through an LLM, understand why its answer can vary or be wrong, and learn what a fair two-model comparison must record.
kicker_primary: LLM foundations
kicker_secondary: Beginner context
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-03/
---

## Begin with one note and one request

Imagine that a procurement analyst receives this short note:

> Supplier note: Northwind moved delivery to 18 August. Payment requires approval first.

The analyst asks a language model:

> Summarize the supplied note in three bullets. Do not add facts that are not in the note.

One model might preserve both facts and follow the requested format. Another might change the date, say that payment was already approved, or add a plausible reason for the delay. Both answers can be grammatically polished.

This gives us the central question for the lesson: how can a system produce fluent text without reliably knowing that every sentence is supported?

An **LLM**, or large language model, is a neural network trained to predict likely continuations of token sequences. It does not begin with a database lookup for “the correct answer.” It receives numeric token IDs, transforms their representations through many decoder blocks, produces scores for the next token, selects one token, and repeats.

```text
prompt text
   -> token IDs
   -> contextual representations
   -> next-token scores
   -> select one token
   -> append it and repeat
   -> generated text
```

That mechanism can produce useful summaries because training has exposed the model to many language patterns. The same mechanism can produce unsupported details because likely continuation is not the same objective as factual verification.

**Checkpoint.** If an answer sounds confident and reads naturally, has the model proved that it is correct? No. Fluency describes the text; correctness requires evidence outside the fluency itself.

## Text first becomes tokens

A neural network operates on numbers rather than raw words. A **tokenizer** converts text into a sequence of integer IDs from a fixed vocabulary. The pieces may be complete words, parts of words, punctuation, spaces, or other recurring character sequences.

For illustration, imagine this split:

```text
"Payment requires approval"
        |
        v
["Payment", " requires", " approval"]
        |
        v
[4182, 9017, 73]
```

Real token boundaries depend on the model's tokenizer, so the visible words above are only an intuition. An uncommon supplier name might become several tokens. Punctuation and whitespace may receive their own pieces. The same sentence can have different token counts under two models.

A token ID is only a label. ID `9017` is not numerically “closer in meaning” to ID `9018` than to ID `42`. The ID tells the model which row to retrieve from a learned table; the row contains the useful numbers.

Tokenization matters operationally:

- prompts and generated output consume a token budget;
- different languages and data formats can use that budget differently;
- truncating tokens can remove an instruction or supporting fact; and
- raw token counts are not automatically comparable across different tokenizers.

**Checkpoint.** Does a 4,096-token context mean 4,096 English words? No. It means 4,096 units under the active tokenizer and chat template.

## Token IDs become vectors

The model uses each token ID to look up an **embedding vector**: an ordered list of learned numbers. A vector gives the model a working numeric representation rather than a human-readable definition.

```text
token ID 4182
      |
      v
embedding table row
[0.12, -0.44, 0.08, ...]
```

During training, the model adjusts these vectors and the rest of its parameters so that useful patterns support next-token prediction. Related uses of language may develop useful geometric relationships, but individual dimensions usually do not have simple labels such as “delivery meaning” or “approval meaning.”

Three similarly named objects should remain separate:

| Object | What it represents |
| --- | --- |
| Token ID | a vocabulary label |
| Token embedding | the initial learned vector looked up for that label |
| Contextual hidden state | the token's evolving representation after it interacts with surrounding tokens |

An **embedding model** is also different from a generative LLM. An embedding model is used to produce a vector for a piece of text so applications can compare or retrieve related items. A generative model produces next-token distributions and can continue text. Both use vectors internally, but their exposed purpose and output contract differ.

In our note, the initial representation of `approval` is context-free. After decoder processing, its hidden state can reflect that approval is required *before payment*. Context changes the working representation.

**Checkpoint.** Is the final hidden state at `approval` simply the original embedding-table row? No. It has been repeatedly updated using permitted context.

## Generation is a repeated prediction loop

After processing the prompt, the model produces one score for every token in its output vocabulary. These raw scores are called **logits**. A softmax operation turns them into a probability distribution whose values sum to one.

```text
candidate token       illustrative probability
------------------------------------------------
"-"                            0.48
"Northwind"                    0.24
"The"                          0.16
other tokens combined          0.12
```

A decoding rule chooses a token from that distribution. The chosen token is appended to the sequence, the model produces a distribution for the following position, and the cycle repeats until it selects a stopping token or reaches a configured output limit.

```text
prompt -> predict token A
prompt + A -> predict token B
prompt + A + B -> predict token C
```

This is **autoregressive generation**: each newly selected token becomes part of the input for the next selection. An early choice can therefore steer many later choices.

The model does not normally draft a complete answer and then reveal it token by token. It repeatedly decides what comes next based on the sequence available so far.

**Checkpoint.** What makes generation autoregressive? Each selected token is appended before the next token distribution is computed.

## Attention lets tokens use relevant earlier context

Before Transformers, recurrent architectures commonly processed a sequence through a step-by-step state. They remain useful in some settings, but the long sequential path can make distant relationships and parallel training difficult. Transformers introduced a more direct way for positions to interact through **attention**.

Consider the phrase:

```text
Payment requires approval first
```

When updating the representation at `approval`, the model should be able to use `Payment` and `requires`. Self-attention provides learned lookup and mixing operations for that interaction.

For each position, a single attention head creates three projected vectors:

- a **query**: what information is this position looking for?
- a **key**: what kind of information can this position match?
- a **value**: what information should this position contribute if selected?

The query at one position is compared with keys at permitted positions. Higher compatibility produces more weight. The weighted values are then combined into an updated representation.

```text
query at "approval"
       |
       +-- compare with key at "Payment"  -> weight
       +-- compare with key at "requires" -> weight
       +-- compare with key at "approval" -> weight
                                              |
                                              v
                                  weighted value mixture
```

This analogy explains the data flow, not the internal meaning of a specific head. Attention weights are learned computational values; they are not automatically a faithful explanation of why a model produced an answer.

### The causal mask protects next-token prediction

A decoder-only model must not look at future answers while learning to predict them. A **causal mask** blocks each position from attending to positions on its right.

When processing `approval`, the representation may use `Payment`, `requires`, and itself. It cannot inspect a token that has not occurred yet. During generation there is no future generated token available anyway; the mask makes the same causal structure explicit during parallel training.

The mask controls information visibility. It does not choose the next token, verify facts, or prevent hallucinations.

### Multiple heads create multiple interaction spaces

One attention head provides one learned set of query, key, and value projections. **Multi-head attention** runs several such projections in parallel, combines their outputs, and maps them back into the model's working width.

Different heads can learn different interaction patterns, but we should not assign each head a permanent human role such as “grammar head” without evidence. Multiple heads increase the model's capacity to represent several relationships at once.

**Checkpoint.** Does attention retrieve facts from the live internet? No. It mixes representations already available inside the model's current sequence and parameters.

## Word order must be represented

Content-only, unmasked attention comparisons do not inherently identify token order. Yet these statements do not mean the same thing:

```text
approval before payment
payment before approval
```

The computation therefore needs an order signal. A causal mask already creates an asymmetric pattern of visible predecessors. Most LLMs also use an explicit **positional mechanism**: an architecture can add learned or sinusoidal position representations to token representations, or modify query/key relationships using rotary positional embeddings such as RoPE. Some experimental decoder architectures instead rely on causal structure without a separate position embedding.

The exact technique varies, but the purpose is stable: make position and relative order available to the computation. An explicit positional mechanism works together with the causal mask. Position affects *where* tokens occur; the causal mask restricts *which positions are visible*.

**Checkpoint.** Are an explicit positional mechanism and the causal mask interchangeable? No. They affect order through different mechanisms and must be described according to the selected architecture.

## A decoder block performs two kinds of work

We can now assemble a simplified decoder-only Transformer block. It alternates two major operations:

1. **masked self-attention** mixes information across permitted token positions;
2. a **feed-forward network** transforms each position independently using the same learned function.

Residual connections and normalization support both operations. A **residual connection** adds a sublayer's update back to its input instead of replacing the representation completely. **Normalization** keeps internal scales controlled and helps deep networks train and operate reliably.

```text
token representations + architecture's order signal
              |
              v
   normalization / masked attention
              |
       residual update
              |
              v
   normalization / feed-forward network
              |
       residual update
              |
              v
       next decoder block
```

The feed-forward network does not directly exchange information between positions. Attention performs cross-position mixing; the feed-forward sublayer performs a richer transformation at each position. Stacking many blocks lets contextual representations develop over depth.

After the last block, the hidden state at the newest position is projected into vocabulary logits. Softmax and the decoding policy then return us to the next-token loop.

**Checkpoint.** Which sublayer directly mixes information between `Payment` and `approval`? Self-attention. The feed-forward network transforms each position after that contextual mixing.

## Training teaches continuation before assistance

During **pretraining**, a base language model learns from large text collections by predicting tokens from preceding context. The training objective rewards better probability estimates for observed continuations.

This develops broad language capability and encodes many statistical regularities, but the objective is not “verify every claim against an authoritative source.” Training data can be incomplete, outdated, inconsistent, or wrong. The model can generalize patterns, reproduce memorized fragments, or generate a plausible combination that was never stated anywhere.

A pretrained completion model also does not automatically behave like a helpful assistant. **Supervised instruction tuning** trains on examples of instructions and desired responses. **Preference-based alignment** uses human or model preference signals to encourage selected behaviours, such as usefulness or safer refusal.

```text
pretraining
  -> learns broad next-token behaviour

instruction tuning
  -> improves response to task-like instructions

preference alignment
  -> shifts behaviour toward preferred responses
```

These stages change behaviour; they do not create a truth guarantee. An instruction-tuned model can follow “three bullets” while inventing a date. An aligned model can express uncertainty while still being wrong.

**Checkpoint.** Why can a model follow the requested format but fail factual support? Format following and factual support are different behaviours and must be evaluated separately.

## Context is a bounded workspace

The **context window** is the bounded token workspace available for the prompt, chat-template additions, previous messages, and generated output. If the runtime uses a 4,096-token context and reserves up to 512 generated tokens, the input cannot independently consume all 4,096 tokens.

A larger advertised context window does not automatically make answers better. Relevant evidence can still be truncated, buried among distractions, contradicted elsewhere, or poorly used. Longer input also changes memory requirements and latency.

For our supplier note, the best context is not the longest possible document collection. It is a clear instruction plus the small, relevant note and an output budget appropriate for three bullets.

Treat context capacity and effective use as separate questions:

- **capacity:** can these tokens fit under the configured limit?
- **quality:** does the model use the relevant tokens correctly?

**Checkpoint.** If a model accepts more tokens, has it proved better retrieval or reasoning? No. Capacity is necessary for long input, but it does not establish effective use.

## Sampling controls selection, not knowledge

The decoding policy decides how the next token is selected from the distribution.

- **Greedy decoding** selects the highest-probability token each time.
- **Temperature** changes how sharp or flat the distribution is before sampling. Lower values concentrate probability; higher values spread it.
- **Top-k** restricts selection to the `k` highest-scoring candidates.
- **Top-p** keeps the smallest high-probability set whose cumulative probability reaches a threshold.
- **Maximum output tokens** stops generation after a configured budget.
- A **seed** can control part of the sampling process when the runtime supports it, but it is not a universal cross-runtime reproducibility guarantee.

These controls affect which continuation is selected. They do not add current facts to the model, repair missing source context, or make an unsupported claim true. Changing several parameters together also makes it difficult to explain why two outputs differ.

For a controlled comparison, freeze the prompt, output cap, sampling values, stop rules, seed policy, and runtime configuration before collecting measured responses.

**Checkpoint.** Does temperature zero prove factual correctness? No. It makes selection more deterministic under a given implementation; it does not change the evidence available to the model.

## Fluent falsehoods have different causes

“Hallucination” is often used as one broad label, but incorrect output can arise through different paths:

- the needed fact was not present in training or context;
- training contained outdated or conflicting statements;
- the prompt was ambiguous;
- relevant context was truncated, buried, or contradicted;
- autoregressive generation committed to an early unsupported choice;
- sampling selected a less-supported continuation; or
- the requested task itself required information outside the supplied evidence.

The mitigation should match the cause. Supply a bounded authoritative reference when the task depends on one. Clarify ambiguous instructions. Validate deterministic fields. Use retrieval when current external knowledge is required. Evaluate outputs against references and retain human review for consequential decisions.

No prompt suffix or sampling setting fixes every cause. Model output remains untrusted data: do not execute it as a command or let it directly mutate a system of record.

For the Northwind task, a useful rubric can score **format adherence** and **factual support** separately. An answer can earn full format credit for three bullets and still fail support by changing 18 August to 20 August.

## Hosted and local models change the operating boundary

A hosted service manages model serving behind a network API. A local open-weight runtime lets the operator choose and run model artifacts on controlled hardware. Neither option is universally better.

| Question | Hosted service | Local open-weight runtime |
| --- | --- | --- |
| Where does the request travel? | across a provider boundary | can remain on the local machine |
| Who manages serving capacity? | provider | operator |
| How is a version selected? | provider contract and model identifier | pinned runtime and artifact files |
| What creates cost? | service usage and contract | hardware, power, storage, and operations |
| What must be governed? | provider terms and data handling | licenses, artifacts, host security, and operations |

“Open weight” does not mean unrestricted use, trusted files, or zero cost. “Local” does not automatically mean secure or private: local logs, files, access controls, retention, and artifact provenance still matter.

This repository's comparison uses a separate `llama-server` process bound to the literal loopback address `127.0.0.1`. The Python harness calls that local HTTP boundary and makes no hosted inference request. The operator—not the harness—downloads artifacts and starts or switches the server.

**Checkpoint.** Does a successful local health check prove model quality? No. It shows that a process responded at one boundary; identity, configuration, output, and quality require separate evidence.

## Compare two models as an experiment

We now return to the two continuations. A fair comparison needs more than sending a prompt twice and choosing the answer we prefer.

The local experiment runs two Qwen2.5 GGUF model blocks sequentially because the target laptop has 8 GB VRAM and 16 GB RAM. Sequential loading reduces capacity pressure and keeps the active model boundary clear. Hardware fit—especially for the 7B model—is something to test and record, not promise in advance.

```text
freeze prompt cases and settings
             |
             v
start model A -> verify identity -> warm up -> measured trials -> store
             |
             v
stop model A; start model B -> repeat the same schedule -> store
             |
             v
hide model identity -> score outputs against the same rubric
```

The comparison should record:

- the exact prompt and a hash that exposes silent changes;
- model artifact, runtime, tokenizer, template, and configuration identity;
- sampling parameters, seed, output cap, timeout, and trial number;
- response or a preserved failure;
- wall-clock latency with its measurement boundary;
- runtime-reported token usage, or an explicit unavailable reason; and
- separate human scores for support, format, completeness, and unsupported claims.

Latency is an observation, not a quality score. The measured wall time includes local transport, queueing, prompt processing, decoding, and response transfer; it is not pure GPU compute. Token counts from models with different tokenizers should not be treated as one common unit without proving equivalence.

The output should be evaluated under an opaque identifier so model name or size does not bias the reviewer. Keep each criterion separate rather than manufacturing one universal winner. A model may be faster but less supported, or more complete but more verbose.

Results are stored as versioned, append-only JSONL evidence. Already persisted trials are not silently rerun, and failures remain in the record. This protects the experiment from selecting only successful or attractive outputs.

**Checkpoint.** If model B wins on one Northwind prompt, have we proved that its model family is universally better? No. We have one bounded observation under a recorded prompt, runtime, artifact, hardware, and rubric.

## Continue with the production lesson

You now have the mental map needed for the complete version:

- tokenization converts visible text into model-specific IDs;
- embeddings provide initial vectors and hidden states add context;
- autoregressive generation repeatedly selects and appends tokens;
- masked self-attention mixes permitted earlier information;
- positional mechanisms make order available;
- residual paths, normalization, and feed-forward networks complete each decoder block;
- pretraining, instruction tuning, and preference alignment have different objectives;
- context capacity does not guarantee effective use;
- sampling changes token selection rather than model knowledge;
- fluent output still requires external validation; and
- a two-model comparison must separate measurements, failures, and blinded quality judgment.

Continue with the [production version]({{ '/weeks/week-03/' | relative_url }}). It develops the mechanisms in detail and connects them to the typed local comparison implementation in this repository.

### Readiness checklist

- [ ] I can distinguish text, tokens, token IDs, embeddings, and contextual hidden states.
- [ ] I can trace one prompt from tokenization to repeated next-token selection.
- [ ] I can explain query, key, and value roles without claiming attention is a factual database.
- [ ] I know why positional information and a causal mask solve different problems.
- [ ] I can identify attention, feed-forward, residual, and normalization roles in a decoder block.
- [ ] I can distinguish pretraining, instruction tuning, and preference alignment.
- [ ] I know why larger context and lower temperature do not guarantee correctness.
- [ ] I can explain several causes of unsupported output and match controls to the cause.
- [ ] I can compare hosted and local operation without calling either universally better.
- [ ] I can separate latency/token observations from blinded output-quality evaluation.
