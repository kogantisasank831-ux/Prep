---
layout: week
permalink: /weeks/week-03/
title: "LLM foundations: from tokens to a local model comparison"
description: Build first-principles LLM intuition and a reproducible, local-only comparison harness for two Qwen2.5 GGUF models.
summary: Trace a prompt through tokenization, a decoder-only Transformer, sampling, and a controlled localhost experiment without confusing fluent output with evidence.
kicker_primary: LLM foundations
kicker_secondary: Local, controlled evaluation
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-03/beginner/
---

Test your understanding with the [Week 3 assessment]({{ '/assessments/week-03/' | relative_url }}): a random ten-question paper from 100 questions, including Python exercises on attention, sampling and controlled comparisons.

## One prompt, two continuations

Imagine you receive this note from a supplier:

> Supplier note: Northwind moved delivery to 18 August. Payment requires approval first.

You ask a language model to do something quite ordinary:

> Summarize the supplied note in three bullets. Do not add facts that are not in the note.

One model keeps the date and the payment condition. Another changes the date, misses the approval requirement, or stops before finishing. Both may sound perfectly natural. So what happened between the prompt and the answer?

We will follow this note through the model, starting with tokens and working up to the Transformer. Once that path makes sense, we will build a small local experiment to compare two models. The aim is to understand what we observed and how we measured it, rather than choose a winner from one convincing answer.

The experiment uses local inference only. The Python harness can call the configured loopback server, but it must never send a generation request to a hosted service or paid API. Downloading model files is a separate network activity, handled outside the harness and governed separately.

### What you should already know, and what you will be able to do

Bring a basic understanding of vectors, dot products, probability, HTTP and JSON. We will also use familiar engineering habits: typed inputs, explicit exceptions, dependency injection and pytest. SQL and a full deep-learning derivation course are not prerequisites.

By the end, you should be able to explain how a decoder-only model processes the note, distinguish token embeddings from retrieval embeddings, reason about sampling and context limits, and design a local comparison that separates measurements from judgments about quality.

### Facts, observations, and inference

As you read, keep track of where each claim comes from:

- **Source-backed fact:** a primary source describes a method, model or API contract. That is background knowledge, not a measurement from our experiment.
- **Observed result:** we captured a response, failure or metric under a particular recorded configuration. It describes that run; it does not automatically apply elsewhere.
- **Inference:** we interpret facts and observations. We need to explain the assumptions and consider other possible explanations.

For example, “the shorter output followed the format” is an observation. It does not establish what an entire model family can do.

Let's start with what enters the model: the tokens.

## 1. Text becomes tokens

### Why does a language model not consume words directly?

We read characters, words and sentences. A neural network works with numbers. A tokenizer bridges that gap by turning a string into integer IDs from a finite vocabulary. Its decoder converts those IDs back into text.

Modern tokenizers commonly use subword pieces. Frequent patterns can become compact vocabulary entries; unfamiliar words can be assembled from smaller pieces. Here is an illustrative round trip:

```text
text:       "Northwind delivery"
tokenizer:  encode
token IDs:  [4182, 9017, 73]
tokenizer:  decode
text:       "Northwind delivery"
```

Those IDs are labels. ID `9017` is not inherently twice as related to `4508` as it is to `12`. The model will look up a learned vector for each ID; the ID itself has no meaningful numerical distance.

A token also need not be a word. Spaces, punctuation, code, uncommon names and different writing systems can produce different splits. Two tokenizers may represent the same sentence with different numbers of tokens. A chat template can add formatting or special tokens that were absent from the text you typed.

That is why “one token is about one word” is unsuitable for budgeting, especially across languages or structured text. A 4,096-token context is a limit measured with the active tokenizer and template. It is neither a character limit nor a fixed number of English words.

**Check your understanding:** can we compare prompt-token counts from our two models as though they were identical units? Only if we have verified that equivalence. Otherwise, record each runtime's count and tokenizer/template identity, and interpret the number within that model.

Now we have vocabulary IDs. Next, the model needs useful numeric representations for them.

## 2. IDs become vectors

### What does the model look up for token ID 9017?

An embedding table is a learned matrix with a row for each vocabulary item. For token ID `i`, the model selects row `E[i]`: a vector with width `d_model`.

```text
vocabulary size V                 model width d
embedding table E: [V, d]
                       lookup ID 9017
                                  |
                                  v
token vector x: [d]
```

A vector is an ordered list of numbers. Training adjusts the embedding table and later layers so that directions and combinations in this space help predict tokens. For `T` input tokens, the lookup gives a matrix of shape `[T, d]`, with one starting vector per position.

At this stage, the lookup is context-free. The ID for `approval` selects the same row whether the sentence concerns payment authorization or project sign-off. The surrounding text influences the representation later.

It helps to separate three terms that often get called “embeddings”:

1. A **token embedding** is the initial table row for a token ID.
2. A **contextual hidden state** is the vector at a particular position after Transformer layers have incorporated permitted context. The two uses of `approval` can now have different representations.
3. A **document or sentence embedding** is deliberately produced for similarity or retrieval, often using a separate model, objective and pooling method. A generative model's final token state is not automatically a substitute.

Cosine similarity does not settle whether two vectors capture meaning, truth or retrieval usefulness. That depends on the model, layer, objective, normalization and task. Having an embedding table inside a generative model does not make it an appropriate standalone embedding service.

**Check your understanding:** can the initial lookup for `approval` identify the kind of approval in our note? No. It provides the starting representation; the later layers add context.

Before opening those layers, let's see what the model ultimately needs to produce.

## 3. Generation is repeated next-token prediction

### What happens after the prompt has been encoded?

Given the prompt tokens `x_1, ..., x_T`, a causal language model produces scores for the next token. These scores are called **logits**, and there is one for each vocabulary item. Softmax converts them into non-negative probabilities that sum to one.

```text
logits for next token: [2.2, 0.1, -1.4, ...]
             softmax
probabilities:          [0.78, 0.10, 0.02, ...]
             selection
chosen token ID -> append to sequence -> predict again
```

Generation repeats a small sequence of steps:

1. Tokenize the prompt.
2. Compute next-token logits using the available prefix.
3. Select a token according to the decoding rule.
4. Append the token to the prefix.
5. Continue until an end token, another stop condition or the output cap.

This is autoregressive generation. The model does not produce the whole answer in a single selection; every chosen token changes the prefix for the next prediction.

Our build caps output at 512 generated tokens. That limits length but does not guarantee a finished answer. The configured context is 4,096 tokens, and the prompt, template and generated text share that bounded workspace under the runtime's behavior.

A probable continuation can still be false. The model might strongly prefer a plausible date because it fits learned patterns, even though that date is unsupported by the supplier note. Probability is a property of the learned distribution, not an external fact check.

**Check your understanding:** does selecting one token at a time mean the model uses only the last token? No. It conditions the next distribution on the permitted prefix. We will now look at how information from that prefix reaches each position.

## 4. Why recurrent paths motivated direct interaction

### What limitation appears when information must pass through every earlier position?

A recurrent neural network carries a hidden state forward through a sequence:

```text
x1 -> h1 -> h2 -> h3 -> ... -> hT
      ^     ^     ^
     x1    x2    x3
```

At step `t`, the state summarizes what has been processed so far. This can work well, and recurrent models remain useful for some constrained, streaming or specialized workloads.

For large language workloads, that sequential dependency creates a challenge. Later computation must wait for earlier steps, limiting parallel training across positions. Information from a distant token also travels through many state updates before reaching the current position.

Attention provides a more direct route. A position can score and combine information from other permitted positions. During training, many positions can perform these interactions in parallel. During causal generation, output is still sequential: we must choose the current token before predicting the next one.

So avoid the broad claim that Transformers simply replaced RNNs. Attention-based Transformers became effective for many large-scale language tasks because of direct contextual interaction and parallelizable training. Other architectures still have useful roles, depending on the constraints.

**Check your understanding:** does direct attention make long context free? No. Attention brings its own computation and memory costs, which increase with sequence length. We will leave detailed serving-capacity calculations for a later lesson.

## 5. One attention head mixes permitted information

### What does a token ask of the rest of the sequence?

Self-attention makes three learned projections of each hidden vector: a **query**, a **key** and a **value**. A useful intuition is that the query describes what a position seeks, the key describes what a position offers for matching, and the value carries the information that will be mixed.

For a sequence matrix `X`, one head computes:

```text
Q = X W_Q       K = X W_K       V = X W_V
scores = Q K^T / sqrt(d_k)
weights = softmax(scores)
output = weights V
```

In the supplier note, the query at `approval` can score the keys at other positions, including `payment` and `first`. Softmax turns the permitted scores into weights. The head then takes a weighted sum of the values.

This is a learned, differentiable computation. It is not a database lookup, and the weights do not by themselves give a reliable explanation of the final answer. Projections, values, residual paths and subsequent layers also contribute. A large weight does not prove that a token was understood or causally responsible for the output.

The factor `sqrt(d_k)` controls how dot-product magnitudes grow with key width. If there are `T` positions and each head uses width `d_k`, `Q` and `K` have shape `[T, d_k]`. Their product `QK^T` has roughly `T × T` scores. Full attention's score count and score-memory footprint therefore grow quadratically with sequence length.

**Check your understanding:** suppose we keep queries and keys unchanged but permute the values. What happens? The matching weights can stay the same, but the information carried into the output changes. Keys influence where to look; values determine what arrives.

Before introducing more heads, we need to decide which positions a head may inspect.

## 6. A causal mask protects the prediction task

### Why must a next-token model not inspect its answer during training?

Suppose the training text is `Northwind moved delivery`. While predicting `delivery` from the preceding text, the model must not inspect the future answer. That would leak the label.

A decoder-only model uses a **causal mask**. Each position can attend to itself and earlier positions, but cannot attend to later ones:

```text
allowed attention (row=query, column=key)

        1  2  3  4
q1      ✓  ×  ×  ×
q2      ✓  ✓  ×  ×
q3      ✓  ✓  ✓  ×
q4      ✓  ✓  ✓  ✓
```

The implementation makes prohibited scores unavailable to softmax, commonly using a mask that acts like negative infinity before normalization. Implementations vary; the requirement is that a prediction at position `t` cannot use future tokens.

During generation, after `- Delivery moved`, the next token can use that prefix. A future completion has not been selected and is unavailable. The mask enforces the same causal structure while training many positions in parallel.

This rule controls sequence visibility. It does not prevent prompt injection, memorization, unsupported statements or harmful output. It is not a safety policy.

**Check your understanding:** why can a causally masked model use the entire user prompt when starting its answer? All prompt positions occur before the newly generated token, so they are permitted context.

## 7. Multiple heads, multiple interaction spaces

### Why not make a single attention head wider?

Multi-head attention uses several sets of query, key and value projections. Their outputs are concatenated and projected back to the model's working width:

```text
X -> head 1 -> context pattern A --\
X -> head 2 -> context pattern B ----> concatenate -> output projection
X -> head h -> context pattern H --/
```

Each head can learn a different interaction space. For example, different patterns might help with syntax, agreement or distant entity references. Training learns these patterns; we do not assign a fixed job to each head. The heads are not guaranteed to be independent or easily interpretable.

With model width `d_model` and `h` equally sized heads, a common design uses head width around `d_model / h`, subject to the implementation. Several projections provide separate views and attention distributions before mixing. Splitting the width does not magically create more total information.

Be careful with statements such as “head 3 tracks dates.” A visualization may suggest that behavior for one prompt, while related computation is distributed across other heads and layers. A reliable interpretation needs controlled analysis, not one heat map.

**Check your understanding:** do multiple heads change the causal rule? No. Each decoder head follows the same visibility restriction while learning its own permitted interactions.

### From classical MHA to grouped-query attention

Classical multi-head attention (**MHA**) gives each query head its own key and value head. **Grouped-query attention (GQA)** keeps multiple query heads while sharing fewer key/value heads among groups of them.

The meaning of a query and the causal-attention calculation stay the same. Sharing changes the key/value representation and its serving trade-offs.

The official Qwen2.5 [1.5B configuration](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct/blob/main/config.json) specifies 12 query heads and 2 key/value heads. Its [7B configuration](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct/blob/main/config.json) specifies 28 query heads and 4 key/value heads. In both, several query heads share a key/value group.

These counts connect the classical explanation to the models we will use. They do not tell us that a particular head has a human-readable role, that one model is better, or how much memory the laptop will actually consume. The experiment records artifacts and runtime configuration; it does not infer hardware fit from head counts.

**Check your understanding:** what does GQA share? Key/value heads. The query heads still provide separate learned lookups.

Attention now connects positions. Next, those positions need an order signal.

## 8. Order does not come for free

### Why should “approve then pay” differ from “pay then approve”?

With content-only, unmasked attention, reordering the same token vectors simply reorders the outputs. Such a layer has no way to distinguish the meaning of “approve then pay” from “pay then approve.” Language needs the order to affect the computation.

An explicit positional mechanism is common, but it is not the only possible source of order. A causal mask already gives positions different sets of visible predecessors. Those boundary effects can supply an implicit signal. Some decoder architectures omit explicit positional embeddings, a choice often called **NoPE**, and rely on that structure.

The general requirement is that order enters the computation. It would be inaccurate to say that every decoder must add a separate position vector.

Three approaches you will encounter are:

- **Learned absolute positions:** learn a vector for each position and combine it with the token representation.
- **Sinusoidal encodings:** use fixed functions of position whose patterns can support learned relative relationships.
- **Rotary positional embeddings (RoPE):** apply position-dependent rotations to queries and keys, changing attention scores in a way that represents relative position.

```text
token embedding at position t
         + learned position vector       (one approach)
         |
         v
input to first block

or: position changes Q and K before QK^T (RoPE concept)
```

Our selected Qwen2.5 architectures use RoPE, so their query/key calculations include an explicit positional transformation. Other families may use different mechanisms. That is another reason to record architecture, tokenizer, template and runtime identity.

A large advertised context window does not establish equal quality at every length or position. Position effects, attention allocation, training distribution, runtime settings and the task itself can all affect what happens.

**Check your understanding:** does position information replace token embeddings? No. Embeddings supply token identity; an explicit positional mechanism or causal structure makes order available at the relevant point in the computation.

## 9. Residual paths and normalization preserve a working representation

### Why not replace a token’s vector completely after attention?

Attention produces an update to the current representation. A residual connection adds that update to what was already there:

```text
input x ----+--------------------> x + attention_update(x)
            |                                 |
            +-> attention sublayer -----------+
```

This gives information and gradients a more direct path through a deep network. Each layer can learn a change relative to the existing signal instead of completely replacing it.

Normalization manages activation scale and distribution within the network. Architectures may place it before or after a sublayer, producing pre-normalization and post-normalization arrangements. Rather than memorize one universal line of pseudocode, follow how normalization, the sublayer and residual addition work together.

Residual connections do not make layers dispensable or eliminate training instability. Normalization is also different from standardizing dataset features once before training; it is an internal operation with architectural variants, not an external-data validation rule.

**Check your understanding:** if attention contributes a zero update, what does the residual connection carry onward? The original representation. That is the idea behind preserving a signal while updating it.

## 10. The feed-forward network transforms each position

### What computation happens after tokens have exchanged context?

The feed-forward network (**FFN**), also called the MLP sublayer, applies a learned nonlinear transformation independently at each position:

```text
hidden vector at position t
       -> expand -> nonlinearity/gating -> contract
       -> transformed vector at position t
```

Conceptually, it expands the vector into a wider intermediate representation, applies nonlinearity or gating, then contracts back to model width. The expansion adds capacity for nonlinear features; the return to model width allows a correctly shaped residual addition.

Attention selects and mixes information across positions. The FFN instead transforms the already contextualized vector at each position. The same FFN parameters are used throughout the sequence, but different input states produce different outputs.

This is why attention alone does not describe a Transformer. Attention, the FFN, residual paths and normalization work together; stacked blocks allow later transformations to build on earlier contextual updates.

**Check your understanding:** which sublayer can bring information directly from the first token to the last within one block? Attention. The FFN then transforms the resulting state at the last position.

## 11. Assemble and stack decoder blocks

### How does one prompt become next-token logits?

We can now put the pieces together:

```text
text -> tokenizer -> token IDs -> embedding lookup + positional information
                                      |
                                      v
                 [ masked multi-head attention -> residual/norm
                   position-wise FFN          -> residual/norm ] x N blocks
                                      |
                                      v
                              final hidden state at last position
                                      |
                                      v
                           output projection -> logits -> decoding rule
```

The bracketed decoder block repeats through the model's depth. Depending on the architecture, explicit position information affects the input to the stack or the query/key computation. Other designs derive order from causal structure without an explicit position embedding. Every decoder attention layer still follows the causal visibility rule.

After the last block, the output projection converts hidden width into one logit per vocabulary item. Softmax and the decoding rule select the next token. Appending that token takes us back through the generation loop.

Training and inference use the same autoregressive conditional formulation, but their roles differ. During training, the supplied sequence contains target tokens, many positions can be processed together under the mask, and a likelihood objective updates the parameters. During generation, parameters are frozen and each selected token extends the prefix. A long answer therefore takes time even when processing its prompt is fast.

This sketch leaves out backpropagation, optimizer state, quantization implementation, KV-cache capacity formulas, batching and kernel details. Those matter in other lessons; here we are tracing the causal model's path from text to output.

**Check your understanding:** where does the 512-token cap act? In the decoding policy. It stops the loop after at most 512 generated tokens, even if the model would otherwise continue.

## 12. Pretraining learns a distribution, not a truth database

### What objective teaches a base language model to continue text?

Pretraining shows the model many prefixes and their observed continuations. It adjusts parameters so that the continuation in the training data becomes more probable. This is next-token likelihood learning, commonly expressed as minimizing the negative log likelihood of target tokens.

```text
prefix:  "Northwind moved delivery to"
target:  " 18 August"
loss:    penalize low probability on the observed target token sequence
```

With enough varied data and capacity, this learning can produce useful representations and behavior beyond literal memorization. At inference, the frozen parameters provide the learned distribution; a decoding policy selects from it.

The objective rewards probability assigned to observed continuations. It does not directly require verified propositions, citations, rejection of every ambiguous request or compliance with a particular product policy. A frequent pattern in training can be plausible without being true in the current task.

Generalization and memorization can coexist. One output does not reveal which mechanism produced it. A model might reproduce training text, combine learned regularities in a new setting, or generate an unsupported pattern. Training cutoff and coverage also constrain knowledge held in its parameters.

Think of the parameters as a learned predictor, rather than a source database you can query for provenance. Fluent wording does not identify supporting evidence. Likewise, a refusal or uncertainty phrase does not prove the model lacks the information. A system that needs factual support must supply evidence and apply deterministic validation outside the generator.

**Check your understanding:** does next-token likelihood include a built-in check that a claim is externally verified? No. It measures how well predictions match observed training continuations.

## 13. Instruction tuning and preference alignment change behavior, not guarantees

### Why might a pretrained completion model not follow a user instruction reliably?

A model trained to continue general text does not automatically behave like an assistant. **Supervised instruction tuning** trains it on instruction-and-response examples, making task-following and assistant-style responses more likely.

**Preference-based alignment** uses preference information or reward-like objectives to favor responses that people or policies judge preferable. InstructGPT is a well-known example of this broad use of human feedback.

```text
pretraining:        predict general corpus continuations
instruction tuning: map instruction-style inputs to desired responses
alignment:          prefer some responses over alternatives under a rubric
```

These are changes to learned behavior, not guarantees of truth. Instruction-tuned models can misunderstand tasks. Preference optimization may help on the evaluated distribution while leaving failures elsewhere. An answer can be helpful, concise and wrong at the same time.

Both artifacts in our comparison are **Instruct** variants. That is relevant to expected chat behavior, but it does not establish that either will follow every constraint. The chat template is also part of the effective input, so we record its identity alongside the model.

Alignment includes objectives, datasets, annotator preferences, evaluation choices and deployment controls. It is not a single safety switch. Product authorization, deterministic validation and human approval remain responsibilities outside the model.

**Check your understanding:** if the model produces three bullets but invents a date, did it fail every part of the task? No. It followed the format while failing factual support. Our rubric needs separate criteria for those behaviors.

## 14. Context is a bounded workspace

### Why can a longer context window still yield a worse answer?

The context contains serialized prompt text, template or special tokens, and generated tokens under the runtime's configured behavior. With a 4,096-token context and a requested 512-token output, the input cannot independently consume all 4,096 tokens.

For example:

```text
context budget = prompt/template tokens + generated tokens

4,096 total configured tokens
  - 3,850 prompt/template tokens
  -   512 requested output tokens
  =  -266 tokens: request cannot satisfy both limits as stated
```

This arithmetic illustrates the shared budget. The actual runtime may reject, truncate or otherwise handle an oversized request according to its configuration. Count with the active tokenizer and template instead of estimating in characters.

More context helps when it adds relevant, clear evidence. It can hurt when it buries instructions, introduces conflicting claims, consumes output room, adds latency or places key evidence where the model uses it poorly.

Suppose our two-sentence supplier note appears after thousands of tokens of unrelated policy. The request might fit, yet the model may miss the delivery date. A large advertised window describes capacity, not assured quality. This lesson leaves detailed KV-cache memory derivations and serving-capacity design for later.

Context is also different from durable memory or retrieval quality. Passing every document ever seen can expose unnecessary sensitive information and make relevant facts harder to use.

**Check your understanding:** if 200 useful tokens are surrounded by 3,000 irrelevant ones, should we first raise the context limit or remove distractions? Removing irrelevant material may help more. Evaluate the result rather than assume that extra capacity improves it.

## 15. Sampling changes selection, not knowledge

### How can the same logits produce different outputs?

Once the model produces logits, the decoder decides which token to select. **Greedy decoding** chooses the most probable one. **Temperature** rescales the sharpness of the distribution: lower values concentrate probability and higher values spread it out.

**Top-k** keeps the `k` highest-probability candidates. **Top-p**, or nucleus sampling, keeps the smallest high-probability set whose cumulative probability reaches `p`.

```text
next token after "Delivery moved to":  "18" .55, "20" .25, "August" .12, other .08
greedy: choose "18"
top-k=2: sample only from "18"/"20"
top-p=.80: sample from the smallest prefix reaching .80 ("18"/"20")
```

The maximum output budget limits length. Stop tokens or strings can end generation according to the runtime's rules. A seed can help record and sometimes reproduce sampling in a fixed implementation, but it does not guarantee identical behavior across models, templates, tokenizers, kernels or runtime versions.

For a controlled example, change one parameter at a time. If you change temperature and top-p together, you cannot easily attribute the difference to either. The baseline records all sampling settings, stop rules, seeds and streaming choices, and uses non-streaming requests. The exact ordering and semantics of decoding operations are runtime-defined.

These settings select from the knowledge and context already available; they do not add facts. Greedy decoding can still choose an unsupported continuation.

**Check your understanding:** if a model invents a date at temperature zero, is lowering temperature a complete remedy? No. Its most probable continuation can itself be wrong.

## 16. Plausible falsehoods have several causes

### Why can a fluent answer be wrong despite a clear-looking prompt?

Calling an error a hallucination names a symptom. To choose a useful response, look at the cause:

- **Missing or stale knowledge:** the needed fact is absent from the parameters or changed after training.
- **Ambiguous request:** the prompt allows several plausible interpretations.
- **Unsupported completion pressure:** the model continues with a likely answer when it should acknowledge uncertainty.
- **Conflicting or irrelevant context:** the supplied information disagrees or distracts from the task.
- **Sampling variability:** stochastic decoding selects a less probable alternative.

Instruction following and format adherence are separate dimensions. A response can ignore the three-bullet format without making a false factual claim. It can also follow that format perfectly while inventing a date.

For a task grounded in a supplied note, ask a concrete question: does every date in the answer appear in the reference? That is more useful than deciding whether the summary sounds good, although it still does not establish perfect semantic correctness.

```text
reference: "Delivery moved to 18 August."
output:    "Delivery is confirmed for 20 August."

format may be correct; factual support is violated.
```

Match the mitigation to the problem. Clarify an ambiguous task, supply bounded authoritative context, constrain output where useful, validate deterministic fields, evaluate against references, or involve human review. No prompt suffix or sampling setting handles every cause.

Local inference does not make generated text trustworthy. Treat the output as data. Do not execute it, trust it as HTML, or let it run commands or mutate a system of record.

**Check your understanding:** can three well-formatted bullets still contain a fabricated payment condition? Yes. We need to score factual support and instruction/format behavior separately.

## 17. Hosted and open-weight are operating-model choices

### What changes when inference happens on someone else’s infrastructure?

A hosted service usually manages serving, scaling, updates and the API boundary. Running open weights locally gives you more control over artifacts, runtime version, timing and the data path. It also makes you responsible for licensing, hardware fit, patching, observability, storage and incident handling.

| Dimension | Hosted model | Local/open-weight runtime |
| --- | --- | --- |
| Data path | Leaves the client boundary under provider terms | Can remain on the machine, subject to local controls |
| Hardware/operations | Provider manages capacity | Operator manages driver, runtime, artifacts, and limits |
| Version control | Provider may change an endpoint/model | Operator can pin binary and artifact revisions |
| Latency | Network plus provider queueing | Localhost transport plus local queueing/inference |
| Cost | Usage pricing and contract terms | Hardware, power, engineering, storage, and operations |
| Licensing | Service terms govern access | Artifact and runtime licenses must be reviewed |

The right choice depends on the product's requirements. Local operation still needs file access controls, retention rules, safe logging and defenses against malicious software or artifacts. Hosted operation may suit the task when its governance, capability, support, capacity and contractual terms meet the requirements.

Our build makes no hosted inference call because we are learning to work with a controlled local boundary. That does not establish that local operation is universally cheaper, better or more private.

Open weights also do not imply an unrestricted license, safe files or a reproducible runtime. Record the repository and revision, GGUF file, SHA-256, declared license, license-file revision and runtime binary provenance before calling a run reproducible.

**Check your understanding:** is “it ran on my laptop” enough to describe a comparison? No. We also need the artifact, quantization, context, template, offload, driver/runtime and request settings.

## 18. The local server is an external boundary

### What should the Python harness assume about `llama-server`?

The Python application talks to a configured local HTTP server. It does not own the server process. For this exercise, a separate native Windows CUDA `llama-server` runs on the RTX 3070 Ti laptop with 8 GB VRAM and 16 GB RAM, bound to `127.0.0.1` rather than a LAN-facing address.

The operator downloads artifacts and installs, starts, switches and stops the server. The harness must not download, install, launch, kill or substitute it. Downloads involve network access and remain outside the harness's inference-only responsibility.

We use these two blocks, in this order, never loaded concurrently:

1. `Qwen/Qwen2.5-1.5B-Instruct-GGUF:Q4_K_M`.
2. `Qwen/Qwen2.5-7B-Instruct-GGUF:Q4_K_M`.

The initial settings are context size 4,096, maximum output 512, non-streaming generation and a first attempt at full GPU offload. The selected Qwen repositories declare Apache-2.0 and `llama.cpp` publishes MIT. Record the relevant runtime, artifact, template and license provenance in `RunManifest`.

The official documentation describes model-information and OpenAI-compatible chat-completion routes. It also makes chat behavior dependent on supported templates. Qwen's GGUF model cards show `llama-server` examples for the selected repositories. These are contracts to check against our actual binary; they do not certify its fields, template behavior or hardware fit.

```text
operator starts configured local server
              |
              v
harness -> health/readiness + /v1/models identity check
              |
              +-- unavailable/mismatch -> stable startup/configuration failure
              |
              v
POST local chat-completion -> validate response -> domain result
```

Q4 quantization and sequential loading make this a reasonable experiment to attempt on the laptop. They do not guarantee success. The 7B model could fail to load, need partial CPU offload or leave too little headroom for a 4,096-token context.

A health response only establishes readiness at the checked boundary. It does not prove model quality, correct chat-template use, full GPU offload or comparative performance. Preserve process-lifecycle evidence and any lower-offload fallback so we know what actually ran.

**Check your understanding:** why provide an expected model identity to the client? A server running the wrong model invalidates the comparison, even if it is responsive.

The minimum experiment is straightforward:

```text
fixed prompt/config -> expected-identity check -> generate -> record
        -> switch model -> repeat -> blinded criterion comparison
```

For example, here are two **illustrative outputs, not measurements from either selected model**:

```text
opaque-17
- Supplier: Northwind
- Delivery moved to 18 August
- Payment requires prior approval

opaque-42
- Northwind delayed delivery to 20 August
- Payment has already been approved
- Delivery is confirmed
```

Both have three bullets. Only `opaque-17` preserves the note's facts. Score format separately from factual support, and keep the identity mapping hidden until scoring is complete.

The concepts we learned now tell us what the experiment needs to retain:

| Theory | Experimental evidence |
| --- | --- |
| Tokenization and chat templates | tokenizer/template identities and runtime-reported token counts |
| Sampling | frozen temperature, top-k, top-p, seed, stop, and output-cap fields |
| Context window | configured 4,096-token budget plus per-model prompt-token provenance when exposed |
| Plausible falsehoods | reference-backed rubric criteria for factual support and unsupported claims |
| Local deployment | literal loopback origin, expected model identity, and externally verified runtime/model hashes |

Next, we will turn that simple experiment into code that keeps its requests, measurements and evidence consistent.

## 19. Hardening layer 1: a request that cannot silently change

### What must be fixed before the supplier note reaches a model?

The comparison package keeps six responsibilities separate:

```text
validated request + persisted plan + persisted manifest
                         |
                         v
comparison service -> ModelClient -> HttpTransport -> llama-server
        |
        v
versioned envelopes -> append-only JSONL
```

The request defines the question. The experiment plan freezes the cases and settings. The manifest records the declared model, runtime, tokenizer, template, hardware and server configuration. The client translates local HTTP responses into typed results. The service preserves each outcome. Storage keeps the evidence durable.

Keeping these boundaries small helps us answer “what changed?” when two outputs differ. It also allows us to test the comparison without loading a model.

### The request owns its own fingerprint

`BaselineRequest` takes the actual prompt text and computes its SHA-256. It rejects a supplied hash that disagrees with that text. This prevents the caller from attaching an old prompt identity to a changed question.

The baseline fixes context at 4,096, output at 512 and streaming at `False`. It validates identifiers, stop strings, finite sampling values and a bounded timeout. Here is the essential part of the existing implementation:

```python
# Abridged from tested source: BaselineRequest
class BaselineRequest(StrictModel):
    prompt: str
    prompt_hash: str = ""
    context_size: Literal[4096] = 4096
    max_output_tokens: Literal[512] = 512
    stream: Literal[False] = False
    temperature: float
    top_k: int
    top_p: float
    seed: int
    timeout_seconds: float

    @model_validator(mode="after")
    def derive_prompt_hash(self) -> Self:
        expected = sha256_text(self.prompt)
        if self.prompt_hash and self.prompt_hash != expected:
            raise ValueError("prompt_hash does not match canonical prompt")
        object.__setattr__(self, "prompt_hash", expected)
        return self
```

The complete model persists every identifier and generation setting. Its `generation_fingerprint()` hashes the prompt hash, context and output limits, sampling settings, seed, stop strings, streaming choice and timeout. The timeout belongs there because changing it can change whether a trial succeeds.

Canonical JSON uses sorted keys, compact separators, UTF-8 and `allow_nan=False`. This gives one consistent representation and prevents non-finite values or ambiguous serialization from quietly changing the experiment.

### Loopback means one literal origin

A friendly-looking hostname is not enough to establish that the experiment is local. `AdapterConfig` accepts only an HTTP origin with the literal hostname `127.0.0.1` and an explicit port. Usernames, passwords, paths, queries and fragments are forbidden.

It rejects `localhost`, IPv6 loopback, wildcard binds, LAN addresses, credential-bearing URLs and look-alike hostnames. This deliberately narrow rule makes the boundary easy to inspect and prevents configuration drift into an outbound request. It does not establish that the local process or artifact is trustworthy.

The transport follows the same rule. It disables ambient proxies with `ProxyHandler({})`, rejects redirects, and reads no more than 4 MiB. Redirect status codes, invalid or conflicting `Content-Length` headers and oversized bodies are failures.

```python
# Abridged from tested source: loopback transport construction
def build_local_opener() -> LocalOpener:
    return LocalOpener(build_opener(ProxyHandler({}), _RejectRedirects()))

MAX_RESPONSE_BYTES = 4 * 1024 * 1024
body = response.read(MAX_RESPONSE_BYTES + 1)
if len(body) > MAX_RESPONSE_BYTES:
    raise OSError("response body exceeds configured limit")
```

Disabling proxies prevents machine-level proxy settings from creating an undeclared intermediary. Refusing redirects prevents a local endpoint from sending the request elsewhere. Bounded reads prevent a malformed or hostile process from forcing an unbounded allocation. These controls protect the HTTP boundary; they do not improve model quality.

### A manifest says what ran; a plan says what was intended

These are related questions, but they need separate records. For each model block, `RunManifest` binds the run to:

- the literal loopback adapter and expected reported identity;
- the pinned runtime revision and binary SHA-256;
- ordered GGUF shard filenames, sizes and SHA-256 values;
- repository revision, quantization, license revision, template hash and tokenizer hash;
- requested and effective GPU layers, context/output limits, warm-up and cache policies;
- OS, GPU/VRAM, RAM, driver, CUDA backend, CPU threads and harness version; and
- evidence IDs for startup, readiness, warm-up, prior shutdown and any full-offload failure.

The 1.5B model must use its one expected artifact filename. The 7B model must use its two expected shard filenames in the correct order. A reported model alias is only a consistency check; it cannot replace hashes of the intended files.

These are unkeyed SHA-256 integrity links. They can reveal inconsistent declared values, but they do not authenticate artifact origin or prove which bytes the server loaded. The operator must independently hash runtime and model files, then compare them with pins obtained through a trusted source and workflow.

`ExperimentPlan` freezes the experiment across both blocks. It records whether the run is calibration or held-out evaluation, the model/block order, suite/reference/rubric hashes, deterministic case order and seed, and the runtime/artifact/configuration/template/tokenizer pins. It also fixes one warm-up and three measured trials per held-out case. `PlanEnvelope` computes a canonical `plan_hash` over the complete plan.

Placeholders may be useful while designing the exercise. They are invalid for runtime or artifact pins in a measured held-out run. Resolve them before claiming evidence.

The request schedule has its own hash. It includes each ordered trial's case ID, prompt hash, suite ID, sampling settings, seed, stop strings, timeout, context and output limits, and trial ID. Before calling the client, the service recomputes the prompt-suite and schedule hashes. Even a changed timeout or suite identifier causes a failure before generation.

```text
plan hash       -> binds the record to the declared experimental contract
suite hash      -> integrity-links ordered case IDs and prompt hashes
schedule hash   -> integrity-links ordered trials and generation settings
manifest hashes -> check consistency with declared runtime/model/configuration pins
```

This makes it harder to observe an answer, adjust a supposedly minor setting, and describe the result as though it came from the original frozen protocol.

## 20. Hardening layer 2: one local client with explicit measurements

### Which parts of a response are observed, reported, or unavailable?

`LlamaServerClient` checks the request against its manifest, calls `/health` and `/v1/models`, then sends one user message to `/v1/chat/completions`. A ready server reporting the wrong model becomes a configuration failure. It is not a fallback candidate.

The completion request contains the expected model identity, one user message, frozen sampling settings, seed, maximum output tokens and `stream: false`. The `stop` field is omitted when empty. A successful response must have HTTP status 200, valid UTF-8 JSON, the expected model identity, exactly one choice and string message content. The service receives a typed result rather than an arbitrary runtime dictionary.

The baseline starts its wall-clock measurement immediately before dispatching the completion request and stops after reading, parsing and validating the full response. `request_wall_time` includes localhost transport, queueing, prompt processing, decoding and response transfer. It is not pure GPU inference time.

Because the request is non-streaming, time to first token is explicitly unavailable. Do not invent it from the total duration.

Each metric explains its value, unit, measurement boundary and provenance:

```python
# Abridged from tested source: Metric
class Metric(StrictModel):
    name: str
    value: int | float | None
    unit: str
    boundary: str
    source: Literal["client_observed", "runtime_reported", "derived"]
    unavailable_reason: str | None = None
```

A metric must contain either a finite non-negative value or a reason why it is unavailable. Token metrics require non-negative integers. Booleans, NaN, infinity, negative values, absent fields and malformed runtime values cannot be accepted as measurements.

When prompt-token, completion-token, total-token, prompt-time or decode-time fields are absent, store `null` with an explanation. Estimating them would blur the distinction between what we observed and what we assumed.

The schema reserves `derived` as a source category, but the baseline emits no derived metrics. A reproducible derived value would also need its formula and input provenance, which this build does not yet model.

Successes and failures use distinct record types. Failures have stable categories: `not_ready`, `configuration`, `timeout`, `transport`, `protocol` or `server`. Their detail is bounded and sanitized. A client timeout means the client stopped waiting; it does not establish that the server cancelled generation. Successes and failures after dispatch both retain elapsed time under a stated boundary.

**Check your understanding:** if the two models report 114 and 109 prompt tokens, does the first receive more information? We cannot conclude that. Templates and tokenizers may differ. Preserve the counts and identities, and compare throughput within a model unless equivalent token units have been established.

## 21. Hardening layer 3: sequential lifecycle evidence

### Why not start both models and loop over them?

With 8 GB VRAM and 16 GB RAM, loading both models adds capacity pressure and makes the experiment harder to interpret. We therefore run Qwen2.5 1.5B first and Qwen2.5 7B second, in separate blocks.

The operator manages the processes. Python must not silently install, download, launch, kill or replace a server.

Each measured block needs durable evidence of startup, readiness and one warm-up. The transition also needs evidence that the preceding server was shut down. Startup and readiness record finite elapsed times. If full GPU offload fails and the operator chooses fewer GPU layers, the manifest must point to an earlier `gpu_load_failure` record containing the attempted layer count.

Before generating a held-out trial, the service checks identity, configuration hash, block number, success semantics and event chronology.

```text
block 0: startup -> ready -> warm-up -> trials persisted -> block-completed
                                              |
                                              v
                                         shutdown
                                              |
block 1: startup -> ready -> warm-up -> trials persisted -> block-completed
```

A `block_completed` record contains the plan ID/hash, frozen schedule hash, number of durable trials and a hash of the exact stored trial set. The second block requires a completion record consistent with block 0 and matching shutdown evidence.

An inconsistent or stale completion marker fails the checks. As elsewhere, these unkeyed hashes check declared consistency; they are not authentication against an adversary.

### Partial recovery does not silently rerun durable trials

Imagine the first block stops partway through. On resumption, the service reads the trials already saved rather than generating new answers for them.

Each trial **record ID** is a SHA-256 derived from stable request settings and target identity. The caller's `trial_id` is a separate field. An identical existing record is reused. A conflicting or duplicate record stops the run. Missing trials can continue independently, and an expected client failure is stored without preventing later trials.

This recovery preserves the original sample. It does not retry until a nicer answer appears or discard failures to make results look better.

The service then checks the completed block against the persisted schedule and exact trial set. Recovery is valid only while the durable evidence remains linked to the frozen plan.

## 22. Hardening layer 4: append-only JSONL evidence

### What makes one local file more trustworthy than “dump some JSON”?

We use versioned, discriminated envelopes for plans, manifests, operational events, trial observations, blinded human evaluations and identity mappings. A trial retains the frozen request and its typed result. Validation checks agreement between their experiment, run, trial, case, prompt and fingerprint fields.

`WindowsJsonlStore` converts an envelope into canonical strict UTF-8 JSON, then takes an exclusive one-byte `msvcrt` lock. Under that lock, it reads and validates the existing file and checks record-ID idempotency. It appends one complete line, flushes and calls `os.fsync()` before reporting success.

```python
# Abridged from tested source: WindowsJsonlStore.append
with self._locked():
    existing = self._read_unlocked()
    # identical ID/content -> no-op; same ID/different content -> conflict
    with self._path.open("ab") as output:
        output.write(line + b"\n")
        output.flush()
        os.fsync(output.fileno())
```

An identical ID and content produce a no-op; the same ID with different content is a conflict. Readers reject truncated final lines, schema violations, duplicate IDs and malformed UTF-8 or JSON. Corruption reports an exact byte offset instead of silently skipping the damaged record. Serialization forbids NaN and infinity so strict JSONL readers can consume the file.

This is a Windows-specific, single-writer contract. Locking and `fsync` reduce crash and concurrency risks, but the file is not a transactional database for multiple writers. To recover from corruption, follow an explicit procedure that copies valid evidence into a new file. Do not edit measured records in place.

## 23. Hardening layer 5: separate, blinded quality evaluation

### How do we judge the two continuations without letting identity choose the result?

First use a calibration suite to check serialization, warm-up behavior and rubric anchors. Then freeze a held-out suite disjoint from calibration, its references, rubric, plan and request schedule before either model generates measured output.

The service enforces three held-out trials per case and deterministic case order. If a held-out answer prompts you to change the prompt, sampling, artifact or rubric, create a new protocol version. The previous held-out suite cannot become tuning data while still being described as untouched evaluation.

For scoring, replace the model name with a stable opaque output ID. Randomize presentation order deterministically using a recorded seed. `BlindedEvaluation` stores evaluator ID, UTC timestamp, rubric version, notes, uncertainty and separate `0/1/2/null` criterion scores. A separate `IdentityMapping` links that opaque ID to its trial and stays apart until scoring is finished.

The supplier-note rubric covers:

- instruction following;
- factual support against the supplied note;
- format adherence;
- completeness;
- unsupported claims; and
- concision/relevance.

Use `0` for violated, `1` for partial or ambiguous, and `2` for satisfied. Use `null` only with a not-applicable reason. Latency and token measurements remain outside the human score.

Keep the criteria separate rather than combining them into one weighted winner. A faster answer can be less supported; a more complete answer can be less concise.

The comparison is a bounded observation, not a universal ranking. Model size, quantization, training data, tokenizer, chat template, runtime, block order, cache state and thermal state can confound it. It cannot establish a model-family leaderboard or a causal claim about architecture.

## 24. What has been proved, and what still requires the laptop

The existing lesson records a deterministic harness validation performed without a GPU:

- 80 tests passed;
- Ruff lint and formatting checks passed; and
- strict mypy passed.

That is earlier validation evidence, not a claim that a real model comparison has now run. Source, dependency, runtime, test or configuration changes require the relevant gates to be rerun before repeating the claim.

The recorded checks covered strict request/manifest/plan validation, loopback URL attacks, proxy-disabled opener construction, a redirect-rejecting handler, bounded reads, identity checks, sanitized failures, finite metrics and schedule freezing. They also covered lifecycle chronology, sequential block transitions, partial recovery, canonical record IDs, JSONL idempotency/durability/corruption handling, and keeping evaluations separate from identity mappings. They did not exercise a live ambient proxy or a real HTTP 302 exchange.

The opt-in `llama-server` integration test was skipped. We therefore have no executed evidence that the pinned models load on this laptop, that full GPU offload succeeds, that the chosen binary exposes the expected API fields, or that the 7B model fits at context 4,096. Exact runtime/model revisions and SHA-256 values remain unresolved until the learner pins the files and runs the gate.

The integration test needs `LLM_COMPARISON_INTEGRATION=1`, plus variables for endpoint, expected model, runtime revision/hash and model revision/hash. It checks that hash values are present and have lowercase SHA-256 syntax; it does not hash files, attest the process or identify which bytes were loaded.

The test then checks `/health`, `/v1/models`, expected identity and one bounded non-streaming completion. Passing establishes that one declared configuration crossed that HTTP contract. It neither authenticates the declared hashes nor constitutes a quality benchmark.

### Bounded runbook

Follow this sequence when you are ready to run the local experiment:

1. Pin the `llama.cpp` revision and Windows CUDA binary SHA-256. Record its license revision.
2. Pin each Qwen repository revision, ordered GGUF shard filename/size/SHA-256, chat-template hash, tokenizer hash and license-file revision.
3. Build and persist the calibration or held-out `ExperimentPlan`. Check its suite, rubric, reference, schedule, artifact and configuration hashes.
4. Start `llama-server` externally with `--host 127.0.0.1`, context 4,096 and the requested full-offload setting. Do not expose its port to the LAN.
5. Record startup and readiness, then verify `/v1/models` identity. If full offload fails, retain the failed attempt before choosing and recording fewer GPU layers.
6. Independently verify binary and artifact hashes, then run the declared-provenance smoke test. Stop if it fails; do not silently change the configuration or substitute a model.
7. Record one unmeasured warm-up, cache policy and manifest for block 0. Run the frozen schedule, saving every success and failure.
8. Check block-completion consistency and record shutdown. Repeat the same bounded lifecycle for block 1.
9. Create blinded evaluation views and store identity mappings separately. Score all retained held-out outputs and report individual criteria, uncertainty and confounders.
10. Retain the append-only JSONL file and environment/run notes. Limit claims about laptop fit, quality and reproducibility to the configuration actually observed.

## 25. Common mistakes and their corrective question

### Calling every vector an embedding

Identify which vector you mean: an initial table row, a contextual hidden state, or an embedding model's similarity-oriented output. That choice determines which comparisons are justified.

### Treating attention as an explanation dashboard

Ask what the attention map establishes. It shows an intermediate learned quantity; without controlled causal analysis, it does not prove why the answer occurred. A heat map alone cannot provide a factual rationale.

### Mixing the causal mask with sampling

Locate the operation in the pipeline. The mask restricts information visible inside the model. Sampling selects from the next-token distribution after logits are produced. They solve different problems.

### Treating context length as memory or quality

Inspect the actual tokens, their relevance, the remaining output budget and where evidence appears. An advertised maximum does not tell you whether the supplied context was useful or correctly used.

### Calling all incorrect output hallucination

Diagnose the error: missing or stale facts, ambiguity, conflicting context, ignored instructions, unsupported continuation pressure or sampling variability. Choose the mitigation for that cause.

### Measuring a local request as pure model latency

Name the start and stop of the timer. The baseline stores `request_wall_time` in seconds, including localhost transport and queueing. Without runtime timing fields, calling it inference-only would misdescribe the measurement.

### Comparing token rates across tokenizers as a single speed contest

Check whether the tokenizers and template serializations produce equivalent units. Otherwise, tokens per second should be interpreted within the model's own tokenizer context.

### Letting calibration leak into evaluation

Ask whether prompts, rubrics, parameters or model choices changed after a held-out result was seen. If they did, version a new experiment. Do not describe it as an untouched held-out comparison.

### Silently changing offload or model after failure

Make the requested setting, failure, effective fallback and active identity visible. Without them, another reader cannot reconstruct what the hardware and model actually did.

## 26. Interview practice

### Foundation

**Why do Transformers work well for many language-model workloads, and where is that too broad?**

Explain the recurrent dependency path first: information passes through sequential state updates, which limits parallel training across positions. Attention allows direct contextual interaction. Then add the qualification that causal decoding still generates tokens sequentially, and recurrent or other sequence architectures remain useful under different constraints. No architecture is universally best.

**Differentiate token embedding, contextual state, and document embedding.**

Walk through the lifecycle. An ID selects a context-free embedding-table row. Decoder blocks turn it into a context- and position-dependent hidden state. A retrieval embedding model produces a task-oriented vector, usually through a dedicated objective and pooling. The latter two are not automatically interchangeable.

**What are Q, K, and V?**

The query describes what a position seeks, the key provides a matching representation, and the value carries what will be mixed after scores are normalized. Mention the causal mask, and explain that attention weights alone do not prove an explanation of the final decision.

**Why is positional information necessary?**

Content-only attention cannot distinguish the same embeddings in different orders. Learned absolute positions, sinusoidal encodings or RoPE can make order available. With RoPE, position changes query/key geometry before attention scores. A larger position capacity does not guarantee equal long-context quality.

**Embedding model versus generative model: objective and output?**

An embedding model exposes a fixed-size task-oriented vector for similarity or retrieval, commonly using pooling and a dedicated training objective. A causal generative model learns next-token likelihood and exposes distributions and continuations. Its internal embeddings and states are not automatically a retrieval embedding API.

**Pretraining versus instruction tuning?**

Pretraining learns broad next-token likelihood from corpus continuations. Supervised instruction tuning learns instruction/response behavior. Preference alignment adds an objective favoring selected responses. Their effects depend on data and objective; none establishes source-grounded truth on its own.

**How do temperature, top-k, and top-p interact?**

Temperature changes the sharpness of logits before sampling. Top-k limits selection to a fixed number of candidates. Top-p retains the smallest high-probability set reaching cumulative probability `p`. The runtime defines exact ordering and semantics. Record all three and change one at a time instead of attributing a result vaguely to creativity.

### Applied design

**Why can a fluent model hallucinate?**

It predicts plausible continuations rather than retrieving verified truth. Distinguish missing or stale knowledge, ambiguous requests, conflicting context, unsupported completion pressure and sampling variability. Keep instruction and format behavior as separate rubric criteria. Match the mitigation to the cause, and distinguish generated statements from supporting evidence.

**Why does a larger context window not automatically improve an answer?**

The window is a bounded workspace. It is not durable memory or a relevance filter. More text can reduce output room, bury evidence, introduce conflicts, add latency and expose unnecessary data. Budget using the active tokenizer/template, then evaluate relevance and placement instead of assuming quality from capacity.

**Why not declare the 7B model better from one local response?**

One response mixes effects from prompt, sampling, template, model version, quantization, thermal state and evaluator preference. Freeze the held-out cases and settings, preserve all trials and failures, record provenance, blind evaluation and score separate dimensions. Report uncertainty rather than a universal ranking.

**Hosted versus open-weight: which should we choose?**

Start with product constraints: data handling, capability, licensing, latency, operations, support, cost and reproducibility. Local operation provides control but adds runtime/artifact/hardware responsibilities. Hosted operation reduces some local work while changing network, contractual and version-control boundaries. The choice depends on the requirements.

### Senior follow-ups

**Why is `ModelClient` a protocol rather than two provider clients?**

Both selected models expose the same `llama-server` HTTP interface. The service needs a typed generation operation, not an artificial provider taxonomy. The adapter owns HTTP details, and a fake client makes deterministic tests possible. Add abstractions when distinct behavior actually requires them.

**How would you interpret token and latency measurements?**

State their origin and boundary. Preserve runtime token counts and durations only when reported; otherwise, use `null` with an explanation. `request_wall_time` runs from dispatch to a fully validated response and includes local transport and queueing. Tokenizer/template differences prevent simplistic token-rate comparisons. Score quality separately.

**What does local-only protect, and what does it not?**

It prevents the harness from sending an inference request to a hosted endpoint. It does not authorize sensitive prompts, secure files, validate responses, protect against malicious artifacts or solve access and retention. Bind to loopback, pin and independently verify artifacts, and minimize the data used.

## 27. Active recall

Try answering these aloud or in your interview notebook before reading the answers. If an explanation feels vague, return to that part of the prompt-to-output path.

1. Why is a token ID not a semantic coordinate?
2. What distinguishes an embedding table row from a contextual hidden state?
3. What makes decoding autoregressive?
4. What does the causal mask prevent, and what does it not prevent?
5. Why add multiple attention heads?
6. Where can positional information affect a decoder?
7. What roles do residual addition and normalization play?
8. What does pretraining optimize that factual verification does not?
9. Why can 4,096 context tokens and a 512-token cap be mutually infeasible for a long prompt?
10. What is temperature changing?
11. Why is local Q4 feasibility an inference rather than a promise on this laptop?
12. What timing boundary does the baseline record?
13. Why preserve a failed trial in JSONL?
14. What separates calibration from held-out evaluation?

### Answers

1. It is a vocabulary label; learned vectors create useful geometry.
2. The table row is context-free lookup; the hidden state has passed through contextual decoder computation.
3. Each selected token is appended before the next distribution is computed.
4. It prevents future-token visibility in causal prediction; it does not prevent falsehoods or unsafe behavior.
5. Multiple projected interaction spaces can learn different patterns before outputs are mixed.
6. By combining with input representations or by modifying attention query/key computations, depending on architecture.
7. They preserve/update representations and stabilize internal computation across depth.
8. It optimizes observed next-token likelihood, not live-source support or truth certification.
9. Prompt/template and requested generated tokens share one bounded workspace.
10. Relative distribution sharpness before sampling, not model knowledge.
11. Artifact details, runtime, driver, offload, context, and overhead determine observed fit.
12. Monotonic time from immediately before local HTTP dispatch to validated complete response; it includes localhost transport and queueing.
13. Otherwise the experiment hides availability/reliability evidence and biases results.
14. Calibration may change the protocol; the frozen held-out suite may not be used for same-version tuning.

## 28. Exercises

These exercises move from reasoning about the model to checking the experiment's implementation. The acceptance criteria matter: use them to decide whether the work is complete.

### Exercise A: token-budget prediction

Design three prompts containing the same factual note: concise, verbose, and verbose with an irrelevant appendix. For each, predict the relative token budget pressure and likely evaluation risks before running anything.

**Acceptance criteria:** state which text/template/output components share the 4,096-token budget; avoid character-to-token estimates as facts; write one property that a reference-backed evaluator can score; explain why a higher advertised context window alone would not answer the quality question.

**Edge case:** include a non-English name or structured table fragment and explain why different tokenizers may count it differently.

### Exercise B: pure decoding-policy tests

Implement a pure function that validates allowed `temperature`, `top_k`, `top_p`, 512-token cap, and `stream=False` for the baseline request. Do not make an HTTP call.

**Acceptance criteria:** explicit types; deterministic tests for valid values, boundaries, and invalid values; an explicit error type; and no claim that a parameter implies truthfulness or cross-model determinism. The exact baseline accepts `context_size == 4096`, `max_output_tokens == 512`, `stream is False`, finite `0.0 <= temperature <= 2.0`, integer `top_k >= 0`, finite `0.0 < top_p <= 1.0`, and finite `0.0 < timeout_seconds <= 3600.0`; reject every violated equality, type, or range.

**Hint:** distinguish a configuration invariant from a quality preference. `max_output_tokens == 512` is a baseline rule; “temperature 0.2 is better” is not a universal invariant.

### Exercise C: adapter failure translation

Create a fake `HttpTransport` that returns a successful health/model response, a wrong identity, malformed completion JSON, and a timeout/transport error. Test that `LlamaServerClient` translates each into the stable adapter result; then use a fake `ModelClient` to test comparison-service preservation of partial failures.

**Acceptance criteria:** use a fake storage port; assert record identity/content conflict behavior; prove no full prompt/output is sent to logs; assert `request_wall_time` in seconds on success and elapsed time on failure; and distinguish sanitized failure detail from a traceback retained only in controlled diagnostics.

### Exercise D: blinded rubric

Write two reference-backed prompt cases and an evaluation sheet with opaque output IDs. Define anchors for factual support and format adherence separately.

**Acceptance criteria:** freeze the held-out prompt/reference/rubric hash before output generation; record `0/1/2/null`, uncertainty, evaluator ID, and UTC timestamp; randomize view order with a recorded seed; retain all outputs/failures; do not create a weighted winner.

### Exercise E: hardware-fit runbook design

Design, but do not automate, an operator runbook for the two model blocks.

**Acceptance criteria:** the `RunManifest` identifies runtime, artifact set, template, and license provenance; server binds to `127.0.0.1`; full GPU offload is attempted first; a lower offload setting requires preserved observed failure; health, identity, warm-up, smoke generation, model-load readiness, cache policy, and shutdown are recorded; artifact download occurs outside the harness.

### Exercise F: Transformer trace

Trace the simplified Northwind fragment `[Payment, requires, approval]` while predicting the next token after `approval`. Write the path from token IDs to logits and name which fragment positions the representation at `approval` may inspect in a causal decoder. Then identify where token identity, order, cross-position mixing, position-wise transformation, and output-vocabulary scores enter. Treat each bracketed item as one illustrative token; the real tokenizer may split the visible words differently.

**Expected reasoning:** lookup maps the three IDs to token embeddings; explicit positional mechanisms or causal structure make order available; every causal attention head at `approval` may inspect `Payment`, `requires`, and `approval`, but not a future token; multi-head outputs are mixed and added through residual/normalization structure; the FFN transforms the resulting hidden state at `approval`; stacked blocks repeat this; the final hidden state is projected to logits over the vocabulary; a decoding policy selects the next ID. A correct answer must not claim the causal mask chooses the next token or that the FFN directly mixes `Payment` into `approval`.

## 29. Mini-project: local evidence comparison

Bring the pieces together in a comparison application using four reference-backed note cases. You should finish with a record another person can inspect: what was asked, which declared configuration ran, what succeeded or failed, and how the retained outputs were judged.

### Scope

- two sequential local model blocks: official Qwen2.5 1.5B and 7B Instruct GGUF `Q4_K_M`;
- native Windows CUDA `llama-server` bound to loopback only;
- context 4,096, maximum output 512, non-streaming baseline;
- one canonical user message per case; no system/tool-message design;
- one warm-up plus three measured trials per held-out case/model;
- append-only JSONL v1 raw measurement envelopes; and
- separate, blinded human-evaluation envelopes.

### Definition of done

- Every measured trial links to a manifest that declares its runtime/artifact/configuration/hardware context; unavailable measurements carry an explicit reason.
- Server readiness and expected identity are checked before a measured request; an unavailable/mismatched boundary becomes a preserved failure record.
- Full prompts/outputs and credentials are absent from default logs, while raw evaluated output is retained only in the governed measurement data path.
- The held-out suite is frozen before either model generates it; calibration changes create a new version.
- The report states that results are bounded observations, lists confounders and order/thermal/cache limitations, and does not claim an overall winner from latency or one subjective score.
- No model output executes a command or mutates a system of record.

## Where this leads

You now have the mechanism behind later lessons on prompting, retrieval, evaluation and serving. Keep the same engineering habits as the systems grow: validate model text before treating it as data, retain source and metric provenance, use narrow typed interfaces for external boundaries, and make changes to prompts or evaluation protocols explicit.

## Primary sources and further reading

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762) for the Transformer architecture and attention formulation.
- [The Impact of Positional Encoding on Length Generalization in Transformers](https://arxiv.org/abs/2305.19466) for empirical analysis of explicit positional encodings and NoPE under causal attention.
- [Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155) for the instruction-following/alignment distinction.
- [Qwen2.5 announcement and usage example](https://qwenlm.github.io/blog/qwen2.5/) for Qwen2.5 model and chat-template context.
- [Qwen2.5-1.5B-Instruct-GGUF model card](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/tree/main) and [Qwen2.5-7B-Instruct-GGUF model card](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/tree/main) for the selected repository names, GGUF artifacts, declared Apache-2.0 license, and local `llama-server` examples. Pin exact revisions and hashes before use.
- [llama.cpp HTTP server documentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md) for the model-information and chat-completions endpoints. Pin the exact runtime release/commit before treating route fields or behavior as fixed.
