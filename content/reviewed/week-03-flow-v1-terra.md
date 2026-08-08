---
layout: week
permalink: /weeks/week-03/
title: LLM foundations: from tokens to a local model comparison
description: Build first-principles LLM intuition and a reproducible, local-only comparison harness for two Qwen2.5 GGUF models.
summary: Trace a prompt through tokenization, a decoder-only Transformer, sampling, and a controlled localhost experiment without confusing fluent output with evidence.
kicker_primary: LLM foundations
kicker_secondary: Local, controlled evaluation
---

## One prompt, two continuations

Keep one short reference-backed note with us throughout the lesson:

> Supplier note: Northwind moved delivery to 18 August. Payment requires approval first.

Now supply it as a single user message:

> Summarize the supplied note in three bullets. Do not add facts that are not in the note.

Two local models can continue that prompt differently. One might preserve the evidence and format; another might invent a date, omit a constraint, or stop early. The observation is simple, but it raises several different questions: how did the characters enter the model, why can the next word depend on an earlier phrase, why can a fluent answer be unsupported, and how would we compare the two outputs honestly?

This lesson answers them in dependency order. It deliberately does **not** start with an SDK call or a full Transformer diagram. The build at the end sends this same kind of controlled prompt to two local models, records what happened, and separates measurement from judgment.

The experiment is deliberately small enough to inspect, reproduce, and challenge. Its one operating constraint is local-only inference: the harness may contact a configured loopback server, but must not send a generation request to a hosted service or paid API. Downloading a model artifact is network activity, not inference; it is outside the harness and must be governed separately.

### What you should already know, and what you will be able to do

You need basic vectors, dot products, probability intuition, HTTP/JSON, and the engineering habits of typed boundaries, exceptions, dependency injection, and pytest. You do not need SQL or a deep-learning derivation course. By the end, you should be able to trace this note through a decoder-only model, distinguish token and document embeddings, explain sampling and context limits, and design a reproducible local comparison whose measurements are not mistaken for a quality verdict.

### Facts, observations, and inference

Keep three kinds of statement separate throughout the lesson.

- **Source-backed fact:** a primary source documents a method, model, or API contract; it is not a measurement from this experiment.
- **Observed result:** a response, failure, or metric captured under one recorded configuration; it does not automatically generalize.
- **Inference:** an interpretation drawn from facts and observations; state its assumptions and alternatives.

**Checkpoint.** Which category contains “the shorter output followed the format”? Observation, not a claim about model-family capability.

We begin with the object the model actually receives: tokens.

## 1. Text becomes tokens

### Orienting question: why does a language model not consume words directly?

Humans usually reason in characters, words, and sentences. A neural network needs a finite, numeric vocabulary. A tokenizer maps a string to a sequence of integer IDs drawn from that vocabulary; its decoder maps IDs back to text. Modern language-model tokenizers commonly use subword pieces, allowing frequent patterns to be represented compactly while still covering unfamiliar words by composing smaller pieces.

```text
text:       "Northwind delivery"
tokenizer:  encode
token IDs:  [4182, 9017, 73]
tokenizer:  decode
text:       "Northwind delivery"
```

The numbers are labels, not quantities with semantic distance. Token ID `9017` is not inherently twice as related to ID `4508` as to ID `12`. The learned embedding table later gives IDs useful vector representations.

Token boundaries need not align with words. Punctuation, whitespace, source code, uncommon names, and languages with different writing systems can be split differently. Two tokenizers can encode the same visible string into different lengths, and a model’s chat template can add special tokens or formatting that were not present in the user’s text.

**Boundary.** “One token is about one word” is a rough intuition at best, not a safe budget calculation. It fails particularly badly across languages and structured text. A 4,096-token context is a limit in the active model/tokenizer representation, not a character limit and not a fixed number of English words.

**Checkpoint.** Can the harness compare raw prompt-token counts from the two selected models as if they measured the same unit? No. Record each runtime-reported count and tokenizer/template identity, then interpret counts within that model unless equivalence is verified.

The IDs now locate learned information, but an ID itself has no geometry. That is the next mental model.

## 2. IDs become vectors

### Orienting question: what does the model look up for token ID 9017?

An embedding table is a learned matrix with one row per vocabulary item. For token ID `i`, lookup selects row `E[i]`, a vector of model width `d_model`. A vector is simply an ordered set of numbers; geometry becomes useful because training changes the table and later layers so that directions and combinations support prediction.

```text
vocabulary size V                 model width d
embedding table E: [V, d]
                       lookup ID 9017
                                  |
                                  v
token vector x: [d]
```

For a prompt of `T` tokens, lookup produces a matrix `[T, d]`: one starting vector at each position. At this point the vector for a token is context-independent. The same token ID receives the same lookup row whether `approval` refers to payment authorization or project sign-off.

Three related terms must not be collapsed:

1. A **token embedding** is the initial lookup vector associated with one token ID.
2. A **contextual hidden state** is the position-specific vector after Transformer layers have mixed information from permitted context. `approval` can acquire different hidden states in the two sentences.
3. A **document or sentence embedding** is an output deliberately produced for similarity/retrieval use, often by an embedding model with its own objective and pooling method. It is not automatically the same thing as a generative model’s final token state.

**Boundary.** Cosine similarity between vectors is not an oracle for meaning, truth, or suitability for retrieval. It depends on the model, layer, training objective, normalization, and task. A generative model can contain an embedding table without being an appropriate standalone embedding service.

**Checkpoint.** Before attention, can the lookup vector for `approval` know whether the note means payment authorization or project sign-off? No. It is an initial representation; contextualization comes later.

The model must turn these vectors into a distribution over possible next tokens. That can be understood before looking inside a Transformer.

## 3. Generation is repeated next-token prediction

### Orienting question: what happens after the prompt has been encoded?

For a prompt token sequence `x_1, ..., x_T`, a causal language model produces a vector of scores—**logits**—for the next position. There is one score per vocabulary token. Scores are not probabilities. Softmax transforms them into non-negative values summing to one:

```text
logits for next token: [2.2, 0.1, -1.4, ...]
             softmax
probabilities:          [0.78, 0.10, 0.02, ...]
             selection
chosen token ID -> append to sequence -> predict again
```

Autoregressive generation is the loop, not one giant act of text creation:

1. tokenize the prompt;
2. compute next-token logits from the available prefix;
3. select one token under a decoding rule;
4. append it to the prefix; and
5. repeat until a stop condition, end token, or output cap.

The output cap of 512 in this build limits generated tokens; it does not promise a complete answer. The context limit of 4,096 applies to the working input sequence under the runtime’s configured behavior. Prompt tokens, template tokens, and generated tokens compete for a bounded workspace.

**Boundary.** A high probability is a statement about the model’s learned distribution, not an external fact check. The model can assign high probability to a plausible false date because that continuation fits patterns in training and prompt context.

**Checkpoint.** Does decoding one token at a time mean the model only considers the last token? No. The next distribution is conditioned on the permitted prefix; the architecture explains how representations mix that prefix.

To see why attention was useful, first consider a more sequential route for carrying context.

## 4. Why recurrent paths motivated direct interaction

### Orienting question: what limitation appears when information must pass through every earlier position?

A recurrent neural network processes a sequence by carrying a hidden state forward:

```text
x1 -> h1 -> h2 -> h3 -> ... -> hT
      ^     ^     ^
     x1    x2    x3
```

At position `t`, the state summarizes earlier processing. This can model sequences, and recurrent models remain useful in some constrained, streaming, or specialized settings. The limitation for large-scale language workloads is the dependency path: later computation depends on earlier sequential steps, which hinders parallel training across positions and makes distant information travel through many updates.

Attention offers a different path. A representation at one position can directly score and combine information from other permitted positions. During training, many positions can compute these interactions in parallel; at causal inference time, new tokens still arrive sequentially because each chosen token changes the prefix.

**Boundary.** “Transformers replaced RNNs” is too broad. It hides architecture variants, deployment constraints, streaming needs, and the fact that causal generation remains sequential in output length. The useful claim is narrower: attention-based Transformers became highly effective for many large-scale language-model workloads because they offer direct contextual interaction and parallelizable training computations.

**Checkpoint.** Does direct attention remove all cost of long context? No. Attention itself has computational and memory trade-offs that grow with sequence length; serving details are deferred to a later capacity lesson.

The next question is how one position chooses what to mix from another.

## 5. One attention head mixes permitted information

### Orienting question: what does a token ask of the rest of the sequence?

Self-attention creates three learned views of each hidden vector: a **query**, a **key**, and a **value**. Query means “what kind of information does this position seek?” Key means “what kind of information does this position offer for matching?” Value is the information carried if the position is selected.

For a sequence matrix `X`, one head uses learned projections:

```text
Q = X W_Q       K = X W_K       V = X W_V
scores = Q K^T / sqrt(d_k)
weights = softmax(scores)
output = weights V
```

For `approval` in the supplier note, its query can score keys at other positions, including `payment` and `first`. Softmax converts the permitted scores for that query position into weights. The resulting output is a weighted sum of value vectors. The head is not a database lookup and does not expose an interpretable “reason” merely because weights exist; it is a learned differentiable computation.

The scale factor `sqrt(d_k)` keeps dot-product magnitudes in a useful range as key dimension changes. Shape intuition is enough here: with `T` positions and head width `d_k`, `Q` and `K` are `[T, d_k]`; `QK^T` supplies roughly `T × T` scores—one for every query/key pair—so full attention's score count and score-memory footprint grow quadratically with sequence length.

**Boundary.** Attention scores are not a reliable explanation of model decisions. A large weight is neither a causal proof nor a guarantee that a token was “understood.” The network’s projections, values, residual paths, and later layers all matter.

**Checkpoint.** What changes if values are permuted while queries and keys stay fixed? Matching weights can remain the same, but the carried information changes. Keys decide where to look; values decide what arrives.

Before adding more heads, constrain which positions the head is allowed to inspect.

## 6. A causal mask protects the prediction task

### Orienting question: why must a next-token model not inspect its answer during training?

Suppose training text is `Northwind moved delivery`. At the position predicting `delivery`, looking directly at the token `delivery` would leak the label. A decoder-only language model therefore applies a **causal mask**: a position may attend to itself and earlier positions, but not later ones.

```text
allowed attention (row=query, column=key)

        1  2  3  4
q1      ✓  ×  ×  ×
q2      ✓  ✓  ×  ×
q3      ✓  ✓  ✓  ×
q4      ✓  ✓  ✓  ✓
```

Operationally, prohibited future scores are made unavailable to softmax (commonly by a mask that acts like negative infinity before normalization). The exact implementation can vary; the essential invariant is that a prediction for position `t` cannot use future tokens.

This mirrors inference. When the model has generated `- Delivery moved`, the next token can depend on those tokens but not on a future completion that has not yet been selected.

**Boundary.** Causal masking does not stop prompt injection, unsupported statements, memorization, or harmful output. It constrains sequence visibility for the objective. It is not a safety policy.

**Checkpoint.** If the mask is causal, why can the model use every word in the user prompt? When generating after the prompt, all prompt positions are earlier than the new token and therefore permitted.

One head supplies one learned interaction pattern. Language benefits from several patterns in parallel.

## 7. Multiple heads, multiple interaction spaces

### Orienting question: why not make a single attention head wider?

Multi-head attention runs several sets of query/key/value projections. Each head can learn a different interaction space, then their outputs are concatenated and projected back to model width.

```text
X -> head 1 -> context pattern A --\
X -> head 2 -> context pattern B ----> concatenate -> output projection
X -> head h -> context pattern H --/
```

One head might learn useful patterns around syntax, another around agreement, another around a long-range entity reference. This is a capability hypothesis learned through optimization, not a human-assigned role list. Heads are not guaranteed to be cleanly interpretable or independent.

If model width is `d_model` and there are `h` equally sized heads, a common design uses head width near `d_model / h`, subject to implementation details. Splitting does not magically create more total information; it gives the model several projected views and separate attention distributions before mixing them.

**Boundary.** “Head 3 tracks dates” is not a stable general statement. Even when a visualization appears suggestive for one prompt, another layer or head may carry related computation. Interpretability needs controlled analysis, not a single heat map.

**Checkpoint.** Does multi-head attention remove the causal rule? No. Each decoder head receives the same causal visibility constraint, then can learn different permitted interactions.

### From classical MHA to grouped-query attention

Classical multi-head attention (MHA) gives every query head its own key and value head. Grouped-query attention (GQA) keeps several query heads but shares a smaller number of key/value heads across groups. The attention computation and causal mask remain the same mental model; the sharing changes the key/value representation and serving trade-off, not the definition of a query.

For the selected Qwen2.5 architectures, the official [1.5B configuration](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct/blob/main/config.json) identifies 12 query heads and 2 key/value heads, while the official [7B configuration](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct/blob/main/config.json) identifies 28 query heads and 4 key/value heads. In each case, several query heads therefore share one key/value group. This is the bridge from the classical MHA explanation above to the actual model family; it is not evidence that any individual head has a human-readable role.

**Boundary.** Head counts describe one architecture configuration, not a quality ranking or a measured memory result on the laptop. The harness records the active artifact set and runtime configuration; it does not infer hardware fit from head counts.

**Checkpoint.** What is shared in GQA? Key/value heads are shared across groups of query heads; queries still express separate learned lookups.

The interactions need a way to distinguish the note's delivery date from its payment condition. That is an order question, but the answer is slightly subtler than “every decoder adds position embeddings.”

## 8. Order does not come for free

### Orienting question: why should “approve then pay” differ from “pay then approve”?

For a content-only, unmasked attention layer, reordering the same token vectors merely reorders the outputs: the layer has no way to distinguish “approve then pay” from “pay then approve.” Language order changes meaning, scope, and obligations, so a useful decoder needs an order signal somewhere in its computation.

An explicit positional mechanism is common, but it is not the only possible source. A causal mask already gives each token a different pattern of permitted predecessors; boundary effects can therefore provide an implicit position signal. Some decoder architectures deliberately omit explicit positional embeddings (often called **NoPE**) and rely on that structure. The safe general claim is that order must affect the computation—not that every decoder must add a separate position vector.

Three conceptual approaches are common:

- **Learned absolute positions:** a learned vector is associated with each position and combined with the token representation.
- **Sinusoidal encodings:** fixed functions of position provide a pattern from which relative relationships can be learned.
- **Rotary positional embeddings (RoPE):** position-dependent rotations are applied in the query/key representation space, affecting attention scores in a way that represents relative position.

```text
token embedding at position t
         + learned position vector       (one approach)
         |
         v
input to first block

or: position changes Q and K before QK^T (RoPE concept)
```

The selected Qwen2.5 architectures use RoPE, so their query/key calculations receive an explicit positional transformation. Other decoder families make different choices. The comparison harness records architecture, template, tokenizer, and runtime identity rather than treating one mechanism as universal.

**Boundary.** An advertised large context capability does not prove equally good behavior at all positions or all lengths. Position effects, attention allocation, training distribution, runtime configuration, and task structure can all affect practical quality.

**Checkpoint.** Does a positional mechanism replace token embeddings? No. Token embeddings represent vocabulary identity; explicit positional information or causal structure supplies order. The mechanisms affect designated parts of the computation.

Attention mixes information across positions. The next two components make it possible to preserve and transform each position’s representation through depth.

## 9. Residual paths and normalization preserve a working representation

### Orienting question: why not replace a token’s vector completely after attention?

Attention proposes an update to a representation. A residual path adds the update to the existing representation, keeping an easier route for information and gradients through many layers:

```text
input x ----+--------------------> x + attention_update(x)
            |                                 |
            +-> attention sublayer -----------+
```

Normalization stabilizes activation scale and distribution according to the architecture’s chosen scheme. You will encounter pre-normalization and post-normalization arrangements; both combine normalization, a sublayer, and a residual addition in different orders. The important lesson here is not to memorize a single line of pseudocode. It is to see that a block updates a representation instead of repeatedly discarding it.

Residual connections do not prove that a layer can be skipped without consequence, nor do they eliminate training instability. They provide a structural path that helps deep networks learn transformations relative to an existing signal.

**Boundary.** Normalization is not feature standardization done once over a dataset, and it is not an external-data validation rule. It is an internal neural-network operation with architectural variants.

**Checkpoint.** If the attention update were zero, what can the residual path carry forward? The original representation. This is the intuition behind “preserve and update.”

After position mixing, each token also needs a rich local transformation.

## 10. The feed-forward network transforms each position

### Orienting question: what computation happens after tokens have exchanged context?

The feed-forward network (FFN), often called the MLP sublayer, applies the same learned nonlinear transformation independently at each sequence position. Conceptually:

```text
hidden vector at position t
       -> expand -> nonlinearity/gating -> contract
       -> transformed vector at position t
```

Unlike attention, the FFN does not choose information from other positions in that sublayer. It transforms each already contextualized vector. An expansion to a wider intermediate representation gives capacity for nonlinear features; contraction returns to model width so a residual addition remains well-shaped.

This is why “attention is the whole Transformer” is incomplete. Attention mixes across positions; FFNs perform rich position-wise transformations; residual and normalization structure their composition. Repeating blocks lets later layers build on earlier contextual updates.

**Boundary.** “Position-wise” does not mean the same output occurs at every position. The same FFN parameters are applied, but each input hidden state differs because token identity, position, and attention-derived context differ.

**Checkpoint.** Which sublayer can directly bring information from the first token to the last in one block? Attention. Which then transforms the result at the last position? The FFN.

Every component is now familiar enough to assemble the decoder block without turning the architecture into unexplained boxes.

## 11. Assemble and stack decoder blocks

### Orienting question: how does one prompt become next-token logits?

At a high level, a decoder-only Transformer does the following:

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

The bracketed block is stacked many times. In many architectures, explicit positional information affects the representation entering the stack or the attention query/key calculations; others use causal structure to make order available without an explicit embedding. Causal masking protects every decoder attention computation. The final output projection maps hidden width back to one score per vocabulary token. Softmax and sampling select the next token, which extends the sequence for the next pass.

Training and inference share the autoregressive next-token conditional formulation, but only training optimizes a likelihood objective. During training, the sequence supplies target next tokens and many positions can be processed together under the causal mask. During generation, frozen parameters define the next-token distribution and each selected token is appended, so output proceeds step by step. This is one reason a long answer has latency even when prompt processing is fast.

**Boundary.** This diagram omits backpropagation, optimizer state, quantization implementation, KV-cache capacity formulas, batching, and kernel details. Omitting them is not denying their importance; it keeps the mental model focused on the causal language-model flow.

**Checkpoint.** Where does a 512-token output cap act? In decoding policy: it stops the autoregressive loop after at most that many generated tokens, regardless of whether the model would continue.

The architecture tells us how scores are produced. The next question is how its parameters acquired useful statistical structure.

## 12. Pretraining learns a distribution, not a truth database

### Orienting question: what objective teaches a base language model to continue text?

Training and inference share the same autoregressive conditional formulation: a prefix determines a distribution for its next token. Pretraining optimizes next-token likelihood over a large corpus; given prefixes, training adjusts parameters to increase probability of observed continuations. At inference, the frozen parameters apply that learned causal next-token distribution and a decoding policy selects text. Across enough varied data and capacity, this can produce representations and continuation behavior that generalize beyond literal memorization.

The objective is often expressed as minimizing negative log likelihood of target next tokens. Intuitively, a model is rewarded for placing more probability on the continuation present in training data. It is not directly rewarded for stating only verified propositions, showing sources, refusing every ambiguous request, or respecting a particular product policy.

```text
prefix:  "Northwind moved delivery to"
target:  " 18 August"
loss:    penalize low probability on the observed target token sequence
```

Generalization and memorization are not mutually exclusive labels that can be inferred from one output. A model may reproduce some training content, compose learned regularities in new contexts, or produce a plausible but unsupported pattern. Training-data cutoff and coverage also limit what can be known from parameters alone.

**Boundary.** Pretraining data is not a queryable provenance store. A fluent statement does not identify a supporting source, and a refusal or uncertainty phrase does not prove the model lacks knowledge. Systems needing factual support require evidence-bearing context and deterministic validation outside the generator.

**Checkpoint.** Does next-token likelihood contain a built-in concept of “this claim is externally verified”? No. It scores alignment with training continuations, not live source verification.

Base completion behavior is useful but not automatically assistant-like. That change has separate objectives and data.

## 13. Instruction tuning and preference alignment change behavior, not guarantees

### Orienting question: why might a pretrained completion model not follow a user instruction reliably?

Supervised instruction tuning trains on examples of instruction-and-response behavior. It teaches the model a format and task-following distribution closer to an assistant interaction. Preference-based alignment methods use preference information or reward-like objectives to bias behavior toward responses people or policies judge preferable. The original InstructGPT work is a canonical example of using human feedback in this broad family of approaches.

```text
pretraining:        predict general corpus continuations
instruction tuning: map instruction-style inputs to desired responses
alignment:          prefer some responses over alternatives under a rubric
```

Neither transformation converts a probabilistic generator into a guaranteed source of truth. Instruction-tuned models can misunderstand instructions. Preference optimization can improve behavior on a distribution yet leave out-of-distribution failures. A model can be helpful, concise, and wrong simultaneously.

For the local comparison, both selected artifacts are **Instruct** variants. That is relevant to expected chat behavior, but it is not evidence that either model will follow every constrained prompt. The harness records the chat-template identity because formatting between a user message and model input is part of the effective experiment.

**Boundary.** Do not describe “alignment” as a single safety switch. It encompasses objectives, datasets, annotator preferences, evaluation choices, and deployment controls. Product authorization, deterministic validation, and human approval remain outside the model.

**Checkpoint.** If a model follows a three-bullet format but inserts an unsupported date, did instruction tuning fail completely? No. Format adherence and factual support are separate rubric properties.

The next practical constraint is what can be placed in the model’s bounded input workspace at all.

## 14. Context is a bounded workspace

### Orienting question: why can a longer context window still yield a worse answer?

The active context includes serialized prompt content, template/special tokens, and generated tokens subject to runtime behavior. With a 4,096-token configured context and a 512-token output cap, a long input can leave little room for a response or trigger truncation/rejection depending on the runtime and request. Count actual tokens with the active model/template; do not budget in characters.

More supplied text can help when it contains relevant, clear evidence and instructions. It can also distract the model, bury an instruction, introduce conflicts, consume output budget, increase latency, or place relevant text in a difficult position. In the Northwind case, placing the two-sentence supplier note after thousands of tokens of unrelated policy may make the delivery date harder to use even though the request still fits. “The model supports a large context” is a capacity statement, not a quality guarantee.

```text
context budget = prompt/template tokens + generated tokens

4,096 total configured tokens
  - 3,850 prompt/template tokens
  -   512 requested output tokens
  =  -266 tokens: request cannot satisfy both limits as stated
```

The arithmetic is conceptual; exact handling depends on the active runtime configuration. The lesson intentionally defers KV-cache memory derivations and serving-capacity design.

**Boundary.** Context is not durable memory and it is not retrieval quality. Passing every document the system has ever seen into a prompt can increase exposure of sensitive data while reducing relevance.

**Checkpoint.** If the evidence is 200 tokens and the prompt is 3,000 tokens of unrelated policy, which change may improve groundedness: raising a headline context limit, or removing the irrelevant material? Often the latter; evaluate rather than assume.

Even with an ideal context, the final selection policy changes which high-probability continuation becomes text.

## 15. Sampling changes selection, not knowledge

### Orienting question: how can the same logits produce different outputs?

After logits become probabilities, a decoder chooses a token. **Greedy decoding** selects the highest-probability token. **Temperature** rescales relative logit sharpness before sampling: lower temperatures concentrate probability mass; higher values flatten it. **Top-k** keeps only the `k` highest-probability candidates before sampling. **Top-p** (nucleus sampling) keeps the smallest high-probability set whose cumulative mass reaches `p`.

```text
next token after "Delivery moved to":  "18" .55, "20" .25, "August" .12, other .08
greedy: choose "18"
top-k=2: sample only from "18"/"20"
top-p=.80: sample from the smallest prefix reaching .80 ("18"/"20")
```

Maximum output tokens limits length. Stop tokens or stop strings can end a response under the runtime’s semantics. A seed can help record and sometimes reproduce a sampling process in one fixed implementation, but it is not a cross-model determinism guarantee: tokenizers, templates, kernels, runtime versions, and sampling implementations differ.

Change one parameter at a time in a controlled example. Raising temperature and changing top-p simultaneously makes an output difference hard to attribute. The baseline comparison uses non-streaming requests and records every sampling, stop, seed, and stream setting.

**Boundary.** Temperature does not make a model more knowledgeable, and greedy output is not necessarily factual. Sampling is a selection policy over the model’s current distribution.

**Checkpoint.** If a response invents a date at temperature zero, is “lower temperature” a complete remedy? No. The selected high-probability continuation can still be unsupported.

That distinction leads directly to a more useful failure vocabulary than “hallucination happened.”

## 16. Plausible falsehoods have several causes

### Orienting question: why can a fluent answer be wrong despite a clear-looking prompt?

“Hallucination” is an umbrella term, not a diagnosis. Separate at least these causes:

- **Missing or stale knowledge:** the needed fact is absent from parameters or changed after training.
- **Ambiguous request:** the prompt leaves multiple plausible interpretations.
- **Unsupported completion pressure:** the model predicts a likely continuation where it should express uncertainty.
- **Conflicting or irrelevant context:** supplied text contains incompatible claims or distractors.
- **Sampling variability:** a lower-probability alternative is selected under stochastic decoding.

Instruction-following and format failures are adjacent evaluation dimensions, not automatically hallucinations. A response can ignore a three-bullet requirement while making no factual claim; it can also obey the format perfectly while inventing a date. The rubric must score those properties separately.

For a reference-backed prompt, a rubric can ask: “Does every named date in the output occur in the supplied note?” That is stronger than asking whether the answer “sounds good.” It does not require claiming perfect semantic correctness.

```text
reference: "Delivery moved to 18 August."
output:    "Delivery is confirmed for 20 August."

format may be correct; factual support is violated.
```

Mitigations match causes: clarify the task, supply bounded authoritative context, constrain output where appropriate, validate deterministic fields, evaluate against references, or design human review. No single prompt suffix or sampling knob solves every category.

**Boundary.** Local inference reduces network exposure but does not make generated text trusted. Treat output as data: do not execute it, turn it into trusted HTML, or allow it to execute commands or mutate a system of record.

**Checkpoint.** Is a model’s uncertainty phrase proof that its claim is safe? No. It is text generated by the model; evaluate the claim and evidence separately.

Similar capability and weights can operate under different boundaries. Choose the operating model by obligations and controls, not marketing labels.

## 17. Hosted and open-weight are operating-model choices

### Orienting question: what changes when inference happens on someone else’s infrastructure?

A hosted model service typically manages model serving, scaling, updates, and an API boundary. An open-weight/local arrangement gives the operator more control over artifact selection, network boundary, timing, runtime version, and data path, while also taking responsibility for licensing, hardware fit, patching, observability, model storage, and incident handling.

| Dimension | Hosted model | Local/open-weight runtime |
| --- | --- | --- |
| Data path | Leaves the client boundary under provider terms | Can remain on the machine, subject to local controls |
| Hardware/operations | Provider manages capacity | Operator manages driver, runtime, artifacts, and limits |
| Version control | Provider may change an endpoint/model | Operator can pin binary and artifact revisions |
| Latency | Network plus provider queueing | Localhost transport plus local queueing/inference |
| Cost | Usage pricing and contract terms | Hardware, power, engineering, storage, and operations |
| Licensing | Service terms govern access | Artifact and runtime licenses must be reviewed |

Neither column is universally “more private,” “cheaper,” or “better.” Local storage still needs access control, retention policy, malware/supply-chain controls, and safe logs. Hosted use can be appropriate when governance, capacity, capability, support, and contractual terms satisfy the product’s constraints. This build makes no hosted call because its purpose is to learn a controlled local boundary.

**Boundary.** Open weight does not mean unrestricted license, safe artifact, or reproducible runtime. Record the model repository/revision, GGUF file, SHA-256, declared license, license-file revision, and runtime binary provenance before treating a run as reproducible.

**Checkpoint.** Is “the model ran on my laptop” enough provenance for a comparison? No. It omits artifact revision, quantization, context, template, offload, driver/runtime, and parameters.

The next section turns the operating decision into one narrow local boundary without pretending hardware fit is already observed.

## 18. The local server is an external boundary

### Orienting question: what should the Python harness assume about `llama-server`?

Assume only a configured localhost HTTP boundary, not ownership of the process. The native Windows CUDA `llama-server` runs separately from Python on the Windows laptop with an RTX 3070 Ti (8 GB VRAM) and 16 GB system RAM. It must bind to `127.0.0.1`, not a LAN-facing interface. The harness does not download artifacts, install binaries, start, stop, kill, or replace the server. Artifact download is network activity and is intentionally outside its inference-only responsibility.

The two local model blocks are `Qwen/Qwen2.5-1.5B-Instruct-GGUF:Q4_K_M` followed by `Qwen/Qwen2.5-7B-Instruct-GGUF:Q4_K_M`, never concurrently. The initial policy is context size 4,096, maximum output 512, non-streaming generation, and first attempt at full GPU offload. The selected Qwen repositories declare Apache-2.0; `llama.cpp` publishes MIT. Runtime, artifact, template, and license provenance belong in the `RunManifest`, not in an informal result description.

The official server documentation describes a model-information route and OpenAI-compatible chat-completions route; it notes that chat behavior depends on supported templates. The Qwen GGUF model cards show `llama-server` use for the exact selected repository names. The documentation provides a contract to test; it does not certify a local binary, exact API usage fields, template behavior, or hardware fit.

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

Run exactly one model at a time. Process lifecycle and any reduced-offload fallback become durable evidence; the hardening layers below define those checks once rather than hiding them in an operator narrative.

**Hardware-fit inference.** Q4 quantization and sequential loading make the experiment plausible enough to test on the stated machine. The 7B artifact may still fail, run partially offloaded, or leave insufficient headroom at 4,096 context. Treat health and bounded smoke generation as observations of a recorded configuration, never as an advance guarantee.

**Boundary.** A server health response says the process is ready to accept a request; it does not establish output quality, correct template use, complete GPU offload, or comparative performance.

**Checkpoint.** Why is the client instantiated with an expected identity? A responsive wrong model invalidates a controlled comparison just as surely as an unavailable server.

Before the hardening details, keep the minimum Northwind path visible:

```text
fixed prompt/config -> expected-identity check -> generate -> record
        -> switch model -> repeat -> blinded criterion comparison
```

Two opaque outputs make the final step concrete. They are **illustrative text, not measurements from either model**:

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

The evaluator can mark format adherence independently from factual support: both examples have three bullets, while only `opaque-17` stays within the note. The identity mapping remains hidden until scoring is complete.

The theory now maps to explicit evidence rather than disappearing when code begins:

| Theory | Experimental evidence |
| --- | --- |
| Tokenization and chat templates | tokenizer/template identities and runtime-reported token counts |
| Sampling | frozen temperature, top-k, top-p, seed, stop, and output-cap fields |
| Context window | configured 4,096-token budget plus per-model prompt-token provenance when exposed |
| Plausible falsehoods | reference-backed rubric criteria for factual support and unsupported claims |
| Local deployment | literal loopback origin, expected model identity, and externally verified runtime/model hashes |

We can now harden this simple path one layer at a time.

## 19. Hardening layer 1: a request that cannot silently change

### Orienting question: what must be fixed before the supplier note reaches a model?

The Python package is deliberately split at six boundaries:

```text
validated request + persisted plan + persisted manifest
                         |
                         v
comparison service -> ModelClient -> HttpTransport -> llama-server
        |
        v
versioned envelopes -> append-only JSONL
```

The diagram is small, but each boundary prevents a different ambiguity. The request fixes what will be asked. The experiment plan fixes which cases and settings constitute the comparison. The manifest identifies the runtime, model bytes, template, tokenizer, hardware, and server configuration. The client translates one local HTTP protocol into typed success or failure. The service preserves each outcome independently. Storage makes the evidence durable.

### The request owns its own fingerprint

`BaselineRequest` accepts the canonical prompt text, not a caller-supplied claim about that text. Validation derives the SHA-256 hash and rejects a conflicting hash. The baseline also fixes context at 4,096, output at 512, and streaming to `False`; it validates finite sampling values, a bounded timeout, identifiers, and stop strings.

The implementation's essential idea is:

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

The full model persists all identifiers and generation settings. Its `generation_fingerprint()` hashes prompt hash, context/output limits, sampling values, stop strings, seed, streaming mode, and timeout. Timeout belongs in the fingerprint because it can change whether a trial succeeds. Canonical JSON uses sorted keys, compact separators, UTF-8, and `allow_nan=False`, so ambiguous serialization and non-finite numbers cannot quietly produce a different experiment.

### Loopback means one literal origin

“Local” is enforced as data, not inferred from a friendly hostname. `AdapterConfig` accepts only an HTTP origin whose parsed hostname is the literal `127.0.0.1`, with an explicit port and no username, password, path, query, or fragment. `localhost`, IPv6 loopback, wildcard binds, LAN addresses, URLs with credentials, and look-alike hostnames are rejected.

That narrow rule serves two purposes. It prevents configuration drift from turning a local experiment into an outbound request, and it makes the trust boundary reviewable. It does not prove that the local process or model artifact is safe.

The transport tightens the same boundary. Its opener installs `ProxyHandler({})`, disables redirects, and reads at most 4 MiB. It rejects redirect status codes, conflicting or invalid `Content-Length` headers, and bodies that exceed the cap:

```python
# Abridged from tested source: loopback transport construction
def build_local_opener() -> LocalOpener:
    return LocalOpener(build_opener(ProxyHandler({}), _RejectRedirects()))

MAX_RESPONSE_BYTES = 4 * 1024 * 1024
body = response.read(MAX_RESPONSE_BYTES + 1)
if len(body) > MAX_RESPONSE_BYTES:
    raise OSError("response body exceeds configured limit")
```

Ignoring ambient proxies matters even for a loopback URL: a machine-level proxy configuration should not become an undeclared intermediary. Rejecting redirects prevents a local endpoint from redirecting the client elsewhere. Bounded reads stop a malformed or hostile process from forcing an unbounded allocation. These are transport controls, not model-quality controls.

### A manifest says what ran; a plan says what was intended

One record cannot answer both questions cleanly. `RunManifest` binds one model block to:

- the literal loopback adapter and expected reported identity;
- pinned runtime revision and binary SHA-256;
- ordered GGUF shard filenames, sizes, and SHA-256 values;
- repository revision, quantization, license revision, template hash, and tokenizer hash;
- requested and effective GPU layers, context/output limits, warm-up and cache policies;
- OS, GPU/VRAM, RAM, driver, CUDA backend, CPU threads, and harness version; and
- startup, readiness, warm-up, prior shutdown, and optional full-offload-failure evidence IDs.

The 1.5B artifact is constrained to one expected filename; the 7B artifact is constrained to its two ordered shard filenames. A runtime model alias is only a consistency check. It cannot substitute for hashes of the intended bytes.

These are unkeyed SHA-256 integrity links, not authentication. They bind records to declared values and expose inconsistent changes, but they do not prove artifact origin or which bytes a process actually loaded. The operator must independently hash the downloaded runtime and model files and compare them with pins obtained through a trusted source and workflow.

`ExperimentPlan` freezes the comparison across both blocks. It stores calibration versus held-out mode, model and block order, suite/reference/rubric hashes, deterministic case order and seed, runtime/artifact/configuration/template/tokenizer pins, one warm-up, and three measured trials per held-out case. The surrounding `PlanEnvelope` derives a canonical `plan_hash` from the complete plan.

For a measured held-out run, unresolved runtime or artifact pins are invalid. This is intentional: an unresolved placeholder is acceptable while designing the exercise, but not while claiming measured evidence.

The request schedule receives its own hash. It covers every ordered trial's case ID, prompt hash, suite ID, sampling parameters, seed, stop strings, timeout, context/output limits, and trial ID. Before a client call, the service recomputes both the prompt-suite hash and schedule hash. Changing even the timeout or suite identifier causes failure before generation.

```text
plan hash       -> binds the record to the declared experimental contract
suite hash      -> integrity-links ordered case IDs and prompt hashes
schedule hash   -> integrity-links ordered trials and generation settings
manifest hashes -> check consistency with declared runtime/model/configuration pins
```

This distinction prevents a common evaluation leak: observing an output, changing one “minor” parameter, and still presenting the run as if it followed the original protocol.

## 20. Hardening layer 2: one local client with explicit measurements

### Orienting question: which parts of a response are observed, reported, or unavailable?

`LlamaServerClient` first checks request/manifest consistency, then calls `/health` and `/v1/models`, and finally sends one user message to `/v1/chat/completions`. A responsive server with the wrong model is a configuration failure, not a usable fallback.

The completion request contains only the expected model identity, one user message, frozen sampling settings, seed, maximum tokens, and `stream: false`; `stop` is omitted when empty. Response parsing requires HTTP 200, valid UTF-8 JSON, the expected model identity, exactly one choice, and string message content. Runtime dictionaries never enter the comparison service.

The baseline wall clock starts immediately before completion dispatch and stops after the full body is parsed and validated. The stored `request_wall_time` therefore includes localhost transport, queueing, prompt processing, decoding, and response transfer. It is not pure GPU inference time. Because the request is non-streaming, time to first token is explicitly unavailable.

Every metric carries four pieces of meaning:

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

Validation requires exactly one of a finite non-negative value or an unavailability reason. Token metrics require non-negative integers; booleans, NaN, infinity, negative values, missing fields, and malformed runtime values cannot masquerade as measurements. Missing prompt-token, completion-token, total-token, prompt-time, or decode-time fields become `null` with a reason rather than an estimate.

The `derived` source value is reserved by the schema, but this baseline emits no derived metrics: it does not yet model the formula and input provenance required to make a derived value reproducible.

Success and failure are discriminated records. Failures use stable categories—`not_ready`, `configuration`, `timeout`, `transport`, `protocol`, or `server`—and bounded sanitized detail. A timeout means the client stopped waiting; the harness does not claim that the server cancelled generation. Both success and post-dispatch failure retain elapsed time under a stated boundary.

**Checkpoint.** If one model reports 114 prompt tokens and the other reports 109, have we proved that the first received “more information”? No. Tokenizers and chat templates may differ. Record both counts and identities; interpret token throughput within each model unless equivalence is established.

## 21. Hardening layer 3: sequential lifecycle evidence

### Orienting question: why not start both models and loop over them?

The supplied 8 GB VRAM and 16 GB RAM make concurrent loading an unnecessary confounder and likely capacity pressure. The plan therefore fixes two sequential blocks: Qwen2.5 1.5B first, then Qwen2.5 7B. The operator owns process lifecycle; Python does not silently install, download, launch, kill, or substitute a server.

A measured block needs durable operational evidence for startup, readiness, one warm-up, and—between blocks—the preceding server shutdown. Startup and readiness store finite elapsed time. If full GPU offload fails and fewer layers are used, the manifest must reference a preceding `gpu_load_failure` record containing the attempted layer count. The service validates identity, configuration hash, block number, success semantics, and event chronology before generating a held-out trial.

```text
block 0: startup -> ready -> warm-up -> trials persisted -> block-completed
                                              |
                                              v
                                         shutdown
                                              |
block 1: startup -> ready -> warm-up -> trials persisted -> block-completed
```

`block_completed` is more than a marker. It records the plan ID/hash, frozen schedule hash, durable trial count, and a hash of the exact persisted trial set. The second block requires a completion record that is internally consistent with block 0 plus matching shutdown evidence. An inconsistent or stale marker fails these declared-consistency checks; the unkeyed hashes do not provide adversarial tamper authentication.

### Partial recovery does not silently rerun durable trials

Each trial **record ID** is a SHA-256 over stable request settings and target identity; the caller-supplied `trial_id` remains a separate field. When a block resumes, the service reads already durable trial records. An identical existing record is reused; a conflicting or duplicate record stops the run. Missing trials continue independently, and an expected client failure is persisted without preventing later trials.

This is partial recovery, not retry-based result selection. It avoids generating a second answer for a trial that was already stored, which would change the sample while keeping the same logical identity. It also preserves partial failure as experimental evidence instead of biasing the data toward successful calls.

The service then checks the completed block against the persisted schedule and exact trial set. Recovery is accepted only when the durable records remain integrity-linked to the frozen plan.

## 22. Hardening layer 4: append-only JSONL evidence

### Orienting question: what makes one local file more trustworthy than “dump some JSON”?

All durable objects use a versioned discriminated envelope. Record types are separate for the experiment plan, manifest, operational evidence, trial observation, blinded human evaluation, and identity mapping. A trial stores both the frozen request settings and the typed result, and validation checks that their experiment/run/trial/case/prompt/fingerprint fields agree.

`WindowsJsonlStore` canonicalizes each envelope to strict UTF-8 JSON before acquiring an exclusive one-byte `msvcrt` lock. Under the lock it reads and validates the existing file, enforces record-ID idempotency, appends one complete line, flushes, and calls `os.fsync()` before reporting success.

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

Readers reject a truncated final line, invalid schema, duplicate ID, or malformed UTF-8/JSON. Corruption reports the exact byte offset; it is not silently skipped. JSON serialization forbids NaN and infinity, so the file remains valid JSONL for other strict readers.

The contract is intentionally single-writer and Windows-specific. Locking plus `fsync` narrows crash and concurrency risk, but it does not turn JSONL into a transactional multi-writer database. Recovery from corruption should copy valid evidence to a new file under an explicit procedure; it should not edit measured records in place.

## 23. Hardening layer 5: separate, blinded quality evaluation

### Orienting question: how do we judge the two continuations without letting identity choose the result?

First use a calibration suite to debug serialization, warm-up, and rubric anchors. Then freeze a disjoint held-out suite, reference material, rubric, plan, and request schedule before generation. The service enforces exactly three held-out trials per case and deterministic case order. Seeing a held-out output and changing the prompt, sampling, artifact, or rubric requires a new protocol version.

The evaluation view replaces model identity with a stable opaque output ID and deterministically randomizes presentation order with a recorded seed. `BlindedEvaluation` stores evaluator ID, UTC time, rubric version, notes, uncertainty, and independent `0/1/2/null` criterion scores. `IdentityMapping` is a different envelope linking the opaque ID to the trial record and remains separate until scoring is complete.

Use these properties for the supplier-note cases:

- instruction following;
- factual support against the supplied note;
- format adherence;
- completeness;
- unsupported claims; and
- concision/relevance.

Score `0` for violated, `1` for partial or ambiguous, `2` for satisfied, and `null` only with a not-applicable reason. Keep latency and token measurements outside the human score. Do not manufacture one weighted winner: the output can be faster yet less supported, or more complete yet less concise.

**Boundary.** This remains a bounded observational comparison. Model size, quantization, training data, tokenizer, chat template, runtime, block order, caching, and thermal state are confounders. The result cannot establish a universal model-family ranking or a causal architecture claim.

## 24. What has been proved, and what still requires the laptop

The deterministic harness was checked without a GPU. For this repository snapshot, the executed validation evidence is:

- 80 tests passed;
- Ruff lint and formatting checks passed; and
- strict mypy passed.

Those checks cover strict request/manifest/plan validation, loopback URL attacks, static opener construction with proxy disabling and a redirect-rejecting handler, bounded reads, identity checks, sanitized failures, finite metrics, schedule freezing, lifecycle chronology, sequential block transitions, partial recovery, canonical trial record IDs, JSONL idempotency/durability/corruption handling, and separation of evaluation from identity mapping. They did not exercise a live ambient proxy or a live HTTP 302 exchange.

This evidence is maintenance-sensitive: changes to source, dependencies, runtime, tests, or configuration require rerunning the gates before repeating the claim.

The real `llama-server` integration test is opt-in and was skipped. Therefore no executed evidence yet proves that either pinned model loads on this laptop, that full GPU offload succeeds, that the expected API fields appear for the chosen runtime revision, or that the 7B model fits with a 4,096-token context. Exact runtime/model revisions and SHA-256 values also remain unresolved until the learner pins the artifacts and runs the gate.

The opt-in test requires `LLM_COMPARISON_INTEGRATION=1` plus endpoint, expected model, runtime revision/hash, and model revision/hash variables. For the hash variables, the test checks only presence and lowercase SHA-256 syntax; it does not hash a file, attest a process, or verify which bytes were loaded. It then checks `/health`, `/v1/models`, expected identity, and one bounded non-streaming smoke completion. Passing it would show only that one declared configuration crossed that contract boundary; it would not authenticate the declared hashes or constitute a quality benchmark.

### Bounded runbook

1. Pin the `llama.cpp` revision and Windows CUDA binary SHA-256; record its license revision.
2. Pin each Qwen repository revision, ordered GGUF shard filename/size/SHA-256, template hash, tokenizer hash, and license-file revision.
3. Build and persist the calibration or held-out `ExperimentPlan`; confirm its suite, rubric, reference, request-schedule, artifact, and configuration hashes.
4. Start `llama-server` externally with `--host 127.0.0.1`, context 4,096, and the requested full-offload setting. Never expose the port to the LAN.
5. Record startup and readiness evidence; verify `/v1/models` identity. If full offload fails, preserve the failed attempt before choosing and recording fewer GPU layers.
6. Independently verify binary/artifact hashes, then run the declared-provenance smoke test. If it fails, stop: do not substitute a different model or silently change configuration.
7. Record one unmeasured warm-up, cache policy, and the manifest for block 0. Run the frozen schedule and persist every success or failure.
8. Verify block-completion consistency, record server shutdown, then repeat the bounded lifecycle for block 1.
9. Generate blinded views, store identity mappings separately, score all retained held-out outputs, and report criterion-level results with uncertainty and confounders.
10. Preserve the append-only JSONL file and environment/run notes. Do not claim laptop fit, comparative quality, or reproducibility beyond the exact configuration actually observed.

## 25. Common mistakes and their corrective question

### Calling every vector an embedding

Ask: is this an initial lookup vector, a contextual hidden state, or an output from an embedding model trained for similarity? The answer changes what similarity claims are justified.

### Treating attention as an explanation dashboard

Ask: does this attention map establish a causal mechanism, or is it only one intermediate learned quantity? Do not turn a heat map into a factual rationale.

### Mixing the causal mask with sampling

Ask: is this rule constraining visibility inside the model, or selecting among next-token probabilities after logits? The mask enforces temporal access; sampling changes output selection.

### Treating context length as memory or quality

Ask: what exact tokens are in the request, which are relevant, what output budget remains, and what was the observed behavior at the chosen placement? Capacity is not usefulness.

### Calling all incorrect output hallucination

Ask: was the fact absent, stale, ambiguous, contradicted by context, ignored by the instruction behavior, or selected stochastically? The mitigation depends on the category.

### Measuring a local request as pure model latency

Ask: where did timing start and stop? The baseline records `request_wall_time` in seconds, including localhost transport and queueing. It must not be labeled “inference-only” without runtime timing fields.

### Comparing token rates across tokenizers as a single speed contest

Ask: did the two models/template serializations produce the same token counts? If not, raw tokens/second is only comparable within the model’s own tokenizer context.

### Letting calibration leak into evaluation

Ask: was this prompt, rubric, parameter, or model choice changed after a held-out result was seen? If yes, version a new experiment; do not present the result as an untouched held-out comparison.

### Silently changing offload or model after failure

Ask: can a reviewer see the requested setting, observed failure, effective fallback, and active model identity? If not, hardware behavior cannot be reconstructed.

## 26. Interview practice

### Foundation

**Why do Transformers work well for many language-model workloads, and where is that too broad?**

Start with the recurrent dependency path: it forces information through sequential state updates and limits parallel training across positions. Explain that attention gives direct contextual interaction, while causal decoding still emits tokens sequentially. Qualify the claim: recurrent and other sequence architectures remain relevant under different constraints; no architecture is universally superior.

**Differentiate token embedding, contextual state, and document embedding.**

Give the lifecycle. An ID indexes a context-free token embedding. Decoder blocks turn it into a position/context-dependent hidden state. An embedding model produces a task-oriented vector for similarity/retrieval, usually with pooling and a dedicated objective. Do not infer that the last two are interchangeable.

**What are Q, K, and V?**

Query describes what a position seeks, key describes what another position offers for matching, and value is what gets mixed after normalized scores. Then state the causal-mask constraint and qualify attention weights as non-proof of explanation.

**Why is positional information necessary?**

Without position, the same token embeddings in different orders are indistinguishable to content-only attention. Learned absolute vectors, sinusoidal encodings, or RoPE supply order; in RoPE, position changes query/key geometry before attention scores. Position capacity does not guarantee equal long-context quality.

**Embedding model versus generative model: objective and output?**

An embedding model is trained and exposed to produce a fixed-size task-oriented vector for similarity or retrieval, commonly after pooling. A generative causal model is trained for next-token likelihood and exposes a distribution/continuation over vocabulary tokens. Its token embeddings and hidden states are not automatically a replacement retrieval embedding API.

**Pretraining versus instruction tuning?**

Pretraining learns broad next-token likelihood from corpus continuations. Supervised instruction tuning trains instruction/response behavior; preference alignment adds an objective over preferred responses. Each changes behavior under its data/objective; none alone establishes source-grounded truth.

**How do temperature, top-k, and top-p interact?**

Temperature changes relative logit sharpness before sampling. Top-k removes all but a fixed number of candidates; top-p keeps the smallest candidate set reaching cumulative probability `p`. Their order and exact semantics are runtime-defined, so change one parameter at a time and record all three rather than attributing an output to “creativity.”

### Applied design

**Why can a fluent model hallucinate?**

The objective predicts plausible continuations rather than fetching verified truth. Then separate missing/stale knowledge, ambiguity, conflicting context, unsupported continuation pressure, and sampling variability. Treat instruction and format behavior as adjacent rubric dimensions. Propose a cause-matched mitigation and preserve the distinction between a model statement and external evidence.

**Why does a larger context window not automatically improve an answer?**

Context is a bounded workspace, not durable memory or a relevance filter. More tokens can leave less output room, bury relevant evidence, introduce conflicts, increase latency, and expose unnecessary data. Count the active template/tokenizer representation and evaluate placement and relevance; do not infer quality from an advertised maximum.

**Why not declare the 7B model better from one local response?**

One response confounds prompt, sampling, template, model version, quantization, thermal state, and evaluator preference. A limited comparison freezes held-out cases/parameters, retains trials and failures, records provenance, blinds evaluation, separates quality dimensions, and reports uncertainty rather than a leaderboard.

**Hosted versus open-weight: which should we choose?**

Start with product constraints: data handling, capabilities, license, latency, operations, support, cost, and reproducibility. Local operation provides more control but adds artifact/runtime/hardware obligations. Hosted operation can reduce local operations but changes network, contract, and version-control boundaries. Avoid a universal recommendation.

### Senior follow-ups

**Why is `ModelClient` a protocol rather than two provider clients?**

Both locked models expose the same `llama-server` HTTP boundary. The comparison service needs one typed generation operation, not provider taxonomy. The adapter contains HTTP details; a fake client supports deterministic tests. Add abstractions only when distinct behavior requires them.

**How would you interpret token and latency measurements?**

Name their provenance and boundary. Runtime-reported token counts/durations are used only when exposed; otherwise `null` is honest. `request_wall_time` is measured in seconds from dispatch to validated response and includes local transport/queueing. Tokenizer/template differences prevent simplistic cross-model token-rate comparisons. Quality remains separately scored.

**What does local-only protect, and what does it not?**

It can keep a harness request off a hosted inference endpoint. It does not authorize sensitive prompts, secure local files, validate outputs, protect against malicious artifacts, or solve retention/access control. Bind to loopback, pin and verify supply-chain inputs, and apply data minimization.

## 27. Active recall

Try these before consulting the answers.

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

Build the comparison application for a four-case reference-note suite. The goal is an evidence record, not a model leaderboard.

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

This lesson establishes the mechanism underneath later prompting, retrieval, evaluation, and serving decisions. Keep the same contract discipline: distinguish model text from validated data, preserve source and metric provenance, isolate external boundaries behind narrow typed interfaces, and make a change to prompts or evaluation protocol visible rather than silently rewriting history.

## Primary sources and further reading

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762) for the Transformer architecture and attention formulation.
- [The Impact of Positional Encoding on Length Generalization in Transformers](https://arxiv.org/abs/2305.19466) for empirical analysis of explicit positional encodings and NoPE under causal attention.
- [Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155) for the instruction-following/alignment distinction.
- [Qwen2.5 announcement and usage example](https://qwenlm.github.io/blog/qwen2.5/) for Qwen2.5 model and chat-template context.
- [Qwen2.5-1.5B-Instruct-GGUF model card](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/tree/main) and [Qwen2.5-7B-Instruct-GGUF model card](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/tree/main) for the selected repository names, GGUF artifacts, declared Apache-2.0 license, and local `llama-server` examples. Pin exact revisions and hashes before use.
- [llama.cpp HTTP server documentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md) for the model-information and chat-completions endpoints. Pin the exact runtime release/commit before treating route fields or behavior as fixed.
