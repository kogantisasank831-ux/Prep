---
week: 3
status: approved
version: 1.0.0
last_reviewed: 2026-10-23
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested Week 3 within the established explicitly approved build-check-push-publish workflow
---

# Week 3 assessment review

## Scope and inspected baseline

Baseline main commit: 66dd40776839b83b47f1e714b4155a0bd3824d14, tree
e2cc6a3432604bcbc608b2c939a934d8a619dd39. The week03-assessment branch starts
from a fresh origin/main fetch. Root AGENTS.md is the only applicable instruction
file; no Design directory exists. Existing untracked QA work is retained. No
subagents were used.

Inspected both Week 3 lessons, their Transformer and experiment contracts,
relevant llm_comparison model/client/transport/storage descriptions and model
validation source, existing assessment bank/page/core/runner/worker, navigation,
README, requirements and assessment tests. The task continues the accepted
100-question weekly practice format. This pass enables Week 3 only.

There are 30 single-choice, 20 multiple-correct, 15 matching, 15 short syntax
and 20 written Python questions. All 100 IDs/prompts are unique. Every item has
a topic, foundation/applied difficulty and explanatory feedback. No independent
human item validation or psychometric calibration is claimed.

## Traceable learning and coding scope

| Lesson area | Assessment evidence |
| --- | --- |
| Tokens, IDs, embeddings, hidden states | Representation/shape questions, copied embedding lookup, exact token-budget arithmetic |
| Attention and decoder blocks | Query/key/value roles, scaling, causal masks, GQA, order/NoPE/RoPE, residual/FFN roles and vector functions |
| Training and generation | Pretraining, instruction tuning, preference alignment, autoregression, context and unsupported claims |
| Selection policy | Stable softmax, positive-temperature rescaling, top-k, top-p prefix and greedy tie rules |
| Frozen comparison | Exact prompt hashes, canonical JSON, settings validation and deterministic measured-trial order |
| External boundary | Literal loopback-origin validation, expected-identity/response parsing and unavailable token metrics |
| Retained evidence | In-memory idempotency/conflict behavior and separate single-criterion scoring |
| Experimental reasoning | Readiness versus identity/quality, timing provenance, durable failures, held-out leakage, blinding and confounders |

Coding functions use synthetic vectors, explicit candidate IDs, supplied token
counts and decoded response fixtures. They do not implement a real tokenizer,
load model weights, benchmark a model, contact a local server or call a hosted
inference API. The page states this scope. The full Windows/GPU comparison
remains a separate lesson exercise.

Tasks declare exact signatures, input domains, error types, tie rules and
mutation policy. Five public checks per task test ordinary behavior and
boundary/error cases. Expected arithmetic and representations are independently
specified in assertions, rather than obtained by calling the reference
implementation. Examples include the 584-token remaining budget, known softmax
probabilities, ten permitted entries in a four-position mask, scaled dot
products and weighted value mixtures.

Exercise-specific contracts are deliberately explicit: temperature rescaling
requires a positive temperature, while the full baseline may use zero under its
runtime convention; top-k selection requires a positive k while the baseline
allows zero; the literal-origin helper is a small string policy, not a drop-in
replacement for the full adapter. The evidence helper is in-memory and provides
no disk locking/durability. A score total covers one criterion across outputs,
not a weighted overall model winner.

## Shared behavior and compatibility

The existing engine is reused without implementation changes. Each paper samples
two of each format without replacement, then shuffles question/option order.
A seed plus bank version reproduces the paper. Each question is worth ten:
single/short exact keys, multiple-correct full set, matching 2.5 per correct pair
and coding two per passed check. No negative marks.

The new page selects the existing pinned Pyodide 0.29.3 worker via Python bank
metadata. No dependency, runtime, CI, Jekyll or server configuration changes.
Only the Week 3 bank/page, its tests/review, assessment enablement, README and a
link paragraph in each Week 3 lesson change. All original lesson text, metadata
and fenced examples remain byte-identical after removing those link paragraphs.
The comparison implementation and prior assessment banks/workers are unchanged.

Saved attempts, versioned paper links, locked submissions, explanations,
reference solutions, blank print and JSON downloads retain the existing
contracts. An unavailable runtime leaves submitted coding marks pending; retry
checks the same locked source. Stop terminates the worker and preserves source.
The 45-second loading and five-second execution deadlines remain unchanged.

Google Colab is the optional external workspace; learners copy/paste code, and
opening the link sends no answer or imports an external score. The page states
the Google sign-in requirement. The hosted site remains static GitHub Pages.

## Validation executed

Environment: native Python 3.12.14, Node 24.19.0, Chromium 153.0.8010.0. The real
browser worker reports Python 3.13.2 from the existing pinned distribution.

- 179 targeted pytest tests passed: 63 Week 3 tests, earlier assessment bank/
  scoring tests and Week 1 service regression modules.
- Every new reference passes five checks (100 total); every unimplemented
  starter scores zero; all twenty plausible wrong solutions lose marks.
- Additional numeric checks verify softmax shift invariance, context arithmetic,
  a nine-position causal triangle, independently chosen value arithmetic and
  width-four scaled attention.
- Shared engine checks generate 1,000 reproducible balanced papers for Week 3,
  reach every item, preserve the source bank and verify objective keys,
  partial/pending scores, stale-result rejection and attempt restoration.
- All twenty references pass their checks in the actual browser worker.
  A complete paper scores 100/100, reloads its saved result, locks submitted
  answers and downloads the expected JSON.
- Blocking runtime loading gives 80/80 graded plus 20 pending; retry advances to
  90/90 then 100/100. Stop and an infinite-loop execution deadline leave the UI
  responsive, preserve code and permit a correct later run.
- 390px light/dark layouts have no horizontal overflow. Blank print contains ten
  questions without answer keys. Share reproduction, new papers, active Week 3
  navigation and three dashboard assessment links pass. Inspected desktop and
  mobile screenshots; no browser page errors or failed requests.
- Ruff lint/format, strict mypy, JavaScript syntax checks and final whitespace/
  diff review pass. Both lesson sources retain their original content and
  fenced examples; prior banks/engine and comparison source are unchanged.

The local preview uses the existing layout through QA Markdown/Liquid/YAML
rendering, not a local Ruby/Jekyll build. The browser environment uses a QA relay
for original CDN HTTPS assets with TLS verification; normal browser web security
is enabled. The deployed URLs/worker are unchanged. Tests have
crossOriginIsolated false and no SharedArrayBuffer. Hosted Pages deployment and
live response/scoring checks follow publication.

## Sources, limits and rollback

Primary sources checked on 2026-10-23:

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- [Positional encodings and NoPE](https://arxiv.org/abs/2305.19466)
- [Pinned Pyodide worker documentation](https://pyodide.org/en/0.29.3/usage/webworker.html)
- [Google Colab FAQ](https://research.google.com/colaboratory/faq.html)

No GGUF download, CUDA/model inference, real model-quality comparison or Windows
storage/lifecycle integration was run for this assessment. Synthetic coding
checks do not establish laptop fit or model capability. They evaluate the
stated deterministic function contracts. The lesson's earlier harness/GPU
evidence is not relabelled as new validation.

The bank/keys are public, and browser scores are locally editable practice
results, not authenticated exam records. Five cases provide bounded feedback,
not proof for every possible implementation. Worker lifetime bounds execution
time, not memory. Runtime loading depends on network/browser support. No learner
identity, score upload, paid API or central score store is introduced.

Rollback is a normal feature revert. Future question-bank edits must increment
the bank version; attempts are isolated by week, version and seed.
