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

Test your understanding with the [Week 3 assessment]({{ '/assessments/week-03/' | relative_url }}): a random ten-question paper from 100 questions, including Python exercises on attention, sampling and controlled comparisons.

## Begin with one note and one request

Suppose you are a procurement analyst and a supplier sends this note:

> Supplier note: Northwind moved delivery to 18 August. Payment requires approval first.

You ask a language model:

> Summarize the supplied note in three bullets. Do not add facts that are not in the note.

One answer preserves the delivery date and the approval requirement. Another changes the date, says payment was already approved, or invents a plausible reason for the delay. Both can read smoothly.

How can a model write naturally and still get such a simple note wrong? That is the question we will work through.

An **LLM**, or large language model, is a neural network trained to predict likely continuations of token sequences. It starts with numeric token IDs, processes their representations through decoder blocks, scores possible next tokens, selects one, and repeats. It does not begin by looking up “the correct answer” in a database.

```text
prompt text
   -> token IDs
   -> contextual representations
   -> next-token scores
   -> select one token
   -> append it and repeat
   -> generated text
```

Training on many language patterns makes this process useful for summaries and other tasks. It also makes unsupported details possible: learning which text is likely to come next is different from verifying every fact.

**Check your understanding:** does a confident, natural answer establish correctness? No. Fluency describes the writing. To judge correctness, we need evidence that supports it.

## Text first becomes tokens

A neural network needs numbers. A **tokenizer** converts text into integer IDs from a fixed vocabulary. A vocabulary piece might be a whole word, part of a word, punctuation, a space or another recurring character sequence.

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

The real split depends on the tokenizer. An unusual supplier name might become several tokens, and spaces or punctuation can contribute pieces of their own. Two models can therefore count the same sentence differently.

The ID only identifies an entry. ID `9017` is not closer in meaning to `9018` than it is to `42`. It tells the model which row to look up in a learned table; that row supplies the useful numbers.

This matters when building an application:

- Both prompts and output consume a token budget.
- Languages and structured formats can use that budget differently.
- Truncation can remove an instruction or the fact needed to answer it.
- Counts from different tokenizers are not automatically comparable.

**Check your understanding:** does a 4,096-token context hold 4,096 English words? No. The limit uses the active tokenizer and chat template, not a fixed word count.

## Token IDs become vectors

For each token ID, the model looks up an **embedding vector**, an ordered list of learned numbers:

```text
token ID 4182
      |
      v
embedding table row
[0.12, -0.44, 0.08, ...]
```

The vector is a working representation, not a dictionary definition. Training adjusts these vectors and the remaining parameters to make useful patterns support next-token prediction. Related language uses may acquire helpful geometric relationships, but individual dimensions usually do not have simple meanings such as delivery or approval.

Keep these three objects separate:

| Object | What it represents |
| --- | --- |
| Token ID | a vocabulary label |
| Token embedding | the initial learned vector looked up for that label |
| Contextual hidden state | the token's evolving representation after it interacts with surrounding tokens |

In our note, the initial vector for `approval` comes from the same lookup row used elsewhere. After decoder layers process the surrounding text, its hidden state can reflect that approval must come *before payment*.

There is also a separate kind of model called an **embedding model**. It produces text vectors for comparing or retrieving related items. A generative LLM instead produces next-token distributions and text continuations. Both use vectors, but their application-facing purposes and outputs differ.

**Check your understanding:** is the final hidden state at `approval` just the original embedding row? No. The decoder has repeatedly updated it using permitted context.

## Generation is a repeated prediction loop

After processing the prompt, the model gives every vocabulary token a score. These raw scores are **logits**. Softmax converts them into probabilities summing to one.

Here is an illustrative distribution:

```text
candidate token       illustrative probability
------------------------------------------------
"-"                            0.48
"Northwind"                    0.24
"The"                          0.16
other tokens combined          0.12
```

A decoding rule chooses a token. The model appends it to the sequence, predicts the following token, and continues until a stopping token or the configured output limit.

```text
prompt -> predict token A
prompt + A -> predict token B
prompt + A + B -> predict token C
```

This is **autoregressive generation**. Each selected token becomes part of the prefix for the next prediction. An early choice can steer what follows, including an initially unsupported detail that the model continues to elaborate.

The model does not normally compose a finished answer and then reveal it one token at a time. It repeatedly selects what comes next using the sequence available so far.

**Check your understanding:** what makes this process autoregressive? The model appends each chosen token before computing the next distribution.

## Attention lets tokens use relevant earlier context

Recurrent models commonly carried context through a step-by-step hidden state. They are still useful in some settings. But passing information through a long sequential path can make distant relationships and parallel training difficult.

Transformers use **attention** to let positions interact more directly. Consider:

```text
Payment requires approval first
```

While updating `approval`, the model should be able to use the information at `Payment` and `requires`. Self-attention supplies learned matching and mixing operations for this interaction.

Each head creates three projected vectors at each position:

- A **query** represents what information the position seeks.
- A **key** supplies the representation used for matching.
- A **value** carries the information to mix if that position receives weight.

The query is compared with keys at permitted positions. More compatible scores receive more weight, and the weighted values are combined:

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

Use this as an explanation of data flow, rather than a literal description of what a particular head understands. Attention weights are learned computational quantities. By themselves, they are not a faithful account of why the model produced an answer.

### The causal mask protects next-token prediction

A decoder-only model must not inspect future answers while training to predict them. A **causal mask** prevents a position from attending to positions on its right.

The representation at `approval` may use `Payment`, `requires` and itself. It cannot inspect a token that comes later. No future generated token is available at inference; the mask enforces the same causal structure while processing training positions in parallel.

The mask controls visibility. It does not choose the next token, check facts or prevent hallucinations.

### Multiple heads create multiple interaction spaces

One head provides one set of learned query, key and value projections. **Multi-head attention** runs several in parallel, combines their outputs and projects them back into the model's working width.

These heads can learn different interaction patterns, allowing several relationships to be represented at once. We should not assign a permanent role such as grammar head without evidence.

**Check your understanding:** does attention fetch facts from the live internet? No. It mixes representations available in the current sequence using the model's learned parameters.

## Word order must be represented

Content-only, unmasked attention has no inherent way to identify token order. Yet these phrases have different meanings:

```text
approval before payment
payment before approval
```

The computation needs an order signal. A causal mask already gives positions different patterns of visible predecessors. Most LLMs also use an explicit **positional mechanism**.

Some architectures combine learned or sinusoidal position representations with token vectors. Others use rotary positional embeddings, such as RoPE, to modify queries and keys. Some experimental decoder designs rely on causal structure without adding a separate positional embedding.

The method varies, but the purpose is to make position and relative order available. An explicit positional mechanism and the causal mask work together: one affects how positions enter the representation; the other restricts which positions can be seen.

**Check your understanding:** are these mechanisms interchangeable? No. Explain their roles according to the selected architecture.

## A decoder block performs two kinds of work

We now have enough pieces to follow a simplified decoder-only Transformer block. It performs two main operations:

1. **Masked self-attention** mixes information across permitted positions.
2. A **feed-forward network** transforms each position independently with the same learned function.

A **residual connection** adds the sublayer's update to its input rather than replacing the representation. **Normalization** manages internal scale, helping the deep network train and operate reliably. Both support the attention and feed-forward operations.

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

The feed-forward sublayer does not directly exchange information between positions. Attention handles that exchange; the feed-forward network performs a richer transformation at each position afterward. Stacking blocks allows contextual representations to develop through the model's depth.

After the final block, the hidden state at the newest position is projected into vocabulary logits. Softmax and the decoding policy then take us back to selecting the next token.

**Check your understanding:** which sublayer directly mixes information from `Payment` into `approval`? Attention. The feed-forward network transforms the resulting state at each position.

## Training teaches continuation before assistance

During **pretraining**, the model learns from large text collections by predicting tokens from preceding context. The objective rewards better probability assigned to the observed continuations.

This develops broad language capability and many statistical regularities. It does not require the model to verify each claim against an authoritative source. Training data can be incomplete, outdated, inconsistent or wrong. A model may generalize patterns, reproduce memorized fragments, or generate plausible combinations that no source actually stated.

Assistant behavior needs further learning. **Supervised instruction tuning** uses examples of instructions and desired responses. **Preference-based alignment** uses human or model preferences to encourage selected behaviors, such as usefulness or safer refusal.

```text
pretraining
  -> learns broad next-token behaviour

instruction tuning
  -> improves response to task-like instructions

preference alignment
  -> shifts behaviour toward preferred responses
```

These stages change behavior without guaranteeing truth. An instruction-tuned model may follow the three-bullet requirement and still invent a delivery date. An aligned model can express uncertainty and remain wrong.

**Check your understanding:** why can format be right while factual support is wrong? They are distinct behaviors. Score them separately.

## Context is a bounded workspace

The **context window** contains the prompt, previous messages, chat-template additions and generated output under the runtime's behavior. With context 4,096 and an allowance of up to 512 generated tokens, the input cannot independently use all 4,096 tokens.

Accepting a longer input does not establish better answers. Useful evidence can be truncated, buried among distractions, contradicted elsewhere or poorly used. More input also changes latency and memory requirements.

For the supplier note, a clear instruction and the small relevant reference may be more useful than a huge document collection. Leave appropriate room for the three-bullet response.

Ask two separate questions:

- **Capacity:** do these tokens fit the configured limit?
- **Quality:** does the model use the relevant information correctly?

**Check your understanding:** does accepting more tokens establish better retrieval or reasoning? No. Capacity helps accommodate long input, but it does not prove effective use.

## Sampling controls selection, not knowledge

The decoding policy chooses a token from the model's distribution:

- **Greedy decoding** selects the highest-probability token.
- **Temperature** adjusts distribution sharpness. Lower values concentrate probability; higher values spread it.
- **Top-k** restricts selection to the `k` highest-scoring candidates.
- **Top-p** keeps the smallest high-probability set reaching a cumulative threshold.
- **Maximum output tokens** ends generation when the budget is exhausted.
- A **seed** controls part of sampling when supported. It is not a universal reproducibility guarantee across runtimes.

These settings alter selection. They do not add current facts, repair missing references or turn an unsupported claim into a true one. Changing several settings at once also makes the cause of an output difference harder to explain.

Before measuring a comparison, freeze the prompt, output budget, sampling values, stop rules, seed policy and runtime configuration.

**Check your understanding:** does temperature zero guarantee factual correctness? No. It makes selection more deterministic within a particular implementation; it does not change the available evidence.

## Fluent falsehoods have different causes

When an answer is wrong, work out what went wrong rather than stop at the label hallucination. Possible causes include:

- a needed fact missing from training or supplied context;
- outdated or conflicting training statements;
- an ambiguous prompt;
- relevant context that was truncated, buried or contradicted;
- an early unsupported choice carried forward by autoregressive generation;
- sampling that selected a less-supported continuation; or
- a task that required information beyond the supplied evidence.

Then match the response to the cause. Supply a bounded authoritative reference, clarify the request, validate deterministic fields, or retrieve current knowledge when needed. Evaluate against references and keep human review for consequential decisions.

No prompt suffix or sampling setting fixes all of these problems. Treat generated output as untrusted data: do not execute it as a command or allow it to mutate a system of record directly.

In the Northwind example, three bullets can satisfy the format and still fail factual support by replacing 18 August with 20 August. The rubric should make those separate judgments.

## Hosted and local models change the operating boundary

A hosted service manages serving behind a network API. With a local open-weight runtime, you select model artifacts and run them on controlled hardware. Which arrangement suits the task depends on the requirements.

| Question | Hosted service | Local open-weight runtime |
| --- | --- | --- |
| Where does the request travel? | across a provider boundary | can remain on the local machine |
| Who manages serving capacity? | provider | operator |
| How is a version selected? | provider contract and model identifier | pinned runtime and artifact files |
| What creates cost? | service usage and contract | hardware, power, storage, and operations |
| What must be governed? | provider terms and data handling | licenses, artifacts, host security, and operations |

Open weights do not imply unrestricted use, trusted artifacts or no cost. Local operation still needs secure files, safe logs, access controls, retention decisions and provenance. Being on the same machine does not automatically make data handling private or secure.

Our comparison uses a separate `llama-server` at the literal loopback address `127.0.0.1`. The Python harness calls this local HTTP boundary and makes no hosted inference request. The operator downloads artifacts and starts or switches the server.

**Check your understanding:** does a successful health check establish quality? No. It shows a response from the checked process. Identity, configuration, actual output and quality need their own evidence.

## Compare two models as an experiment

Let's return to those two summaries. Sending the prompt twice and preferring one answer is not enough for a fair comparison.

The experiment loads two Qwen2.5 GGUF models sequentially on the laptop with 8 GB VRAM and 16 GB RAM. One-at-a-time loading reduces capacity pressure and makes the active model clear. Especially for the 7B model, hardware fit must be tested and recorded rather than promised.

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

Retain enough detail to explain each result:

- the exact prompt and a hash that reveals silent changes;
- model artifact, runtime, tokenizer, template and configuration identity;
- sampling parameters, seed, output budget, timeout and trial number;
- the response or a preserved failure;
- wall-clock latency and exactly what that timer includes;
- runtime token usage, or a reason why it was unavailable; and
- separate human scores for support, format, completeness and unsupported claims.

Latency is a measurement, not a quality judgment. The timer includes local transport, queueing, prompt processing, decoding and response transfer. It does not measure only GPU compute. Similarly, token counts need verified equivalence before treating different tokenizers as one common unit.

Hide model identity behind an opaque output ID when evaluating. Keep each criterion separate instead of constructing a universal winner. A model can be faster but less supported, or more complete but more verbose.

Use versioned, append-only JSONL records. Keep failures and reuse already persisted trials rather than silently generating new ones. Otherwise, the experiment could end up retaining only successful or attractive outputs.

**Check your understanding:** if one model wins on a Northwind prompt, does that establish its family as universally better? No. It gives a bounded observation under the recorded prompt, artifact, runtime, hardware and rubric.

## Continue with the production lesson

You can now follow the prompt-to-answer path and explain why the comparison needs an experimental protocol:

- Tokenization converts text into model-specific IDs.
- Embeddings provide starting vectors; hidden states add context.
- Autoregressive generation selects and appends tokens repeatedly.
- Masked self-attention mixes permitted earlier information.
- Positional mechanisms make order available.
- Residual paths, normalization and feed-forward networks complete decoder blocks.
- Pretraining, instruction tuning and preference alignment use different objectives.
- Context capacity does not establish effective use.
- Sampling changes selection, not knowledge.
- Fluent output still needs external validation.
- A comparison separates measurements, failures and blinded quality judgments.

Continue with the [production version]({{ '/weeks/week-03/' | relative_url }}). It explains these mechanisms in more detail and connects them to the repository's typed local-comparison implementation.

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
