# Week 11 — scoped RAG security lab

This local synthetic lab applies source policy before the real Week 8 retrieval
assistant, then validates a scripted quote-only response. No live model,
network/action dispatcher, server, authentication system or additional dependency
is supplied. The trusted responder implementation is Python code, not a sandbox.

From the repository root in the declared Python environment:

```bash
python -m labs.week_11.demo --scenario clean --output-dir .runtime/week11-clean --show-answer
python -m labs.week_11.demo --scenario malicious-document --output-dir .runtime/week11-malicious --show-answer
python -m labs.week_11.demo --scenario detector-miss --output-dir .runtime/week11-miss --show-answer
python -m labs.week_11.demo --scenario poisoned-fact --output-dir .runtime/week11-poisoned --show-answer
python -m pytest tests/test_week11_security.py -q
```

Choose new output directories. `event.json` contains metadata only; the optional
flag prints the allowed synthetic answer to the console. A controlled refusal
is a completed application outcome and exits zero. Existing files are preserved.
Unexpected adapter/runtime failures and cancellation propagate without retry or
model-only fallback. This is not an HTTP error contract or production CLI logger.

## Responsibilities and authority

- `policy.py`: caller-supplied trusted identity; strict bounded question JSON;
  separately controlled document/version/state/reader catalogue; protected
  representation pins covering content and metadata; narrow fixed screening.
- `assistant.py`: filter scope before index/reranking, exclude known flagged
  permitted chunks, bound serialized context, validate quote-only JSON and
  recheck all supplied sources before returning exact cited text.
- `fixtures.py`: synthetic source/catalogue setup and controlled response ports.
  The catalogue helper creates one chunk per source version for these examples.
- `demo.py`: thirteen fixed cases and exclusive diagnostic output.

`SecurityContext` validates shape only. A real adapter must derive tenant and
principal from authenticated membership. Uploaded text/metadata cannot supply
reader grants. `PolicyStore.replace()` models a trusted administrative update;
there is no public admin API or manifest signature verification service.

| Threat | Implemented local evidence | Residual boundary |
| --- | --- | --- |
| Client supplies tenant/admin fields | Exact question-only schema rejects them | No actual HTTP authentication supplied |
| Cross-tenant or document-version access | Current full-scope policy before retrieval; denied-source invariance | Real storage/query/identity adapters need integration checks |
| Changed approved representation | Full content/metadata pin differs and source is excluded | Baseline approval/signing/storage are trusted fixture inputs |
| Indirect instruction in allowed text | Known patterns exclude that chunk; good evidence remains | False positives, obfuscation and other channels remain |
| Unsafe proposed operation or changed quote | Closed envelope, selected label and exact text checks; no action dispatcher | Not arbitrary generated-claim validation or an OS egress firewall |
| Known email/canary content | Narrow pre/post checks and payload-free event | Not general PII/secret discovery or de-identification |
| Permission update during response | All supplied sources rechecked, including omitted quotes | Cannot retract prior reads or prove distributed atomicity |
| Resource exhaustion | Raw bytes, text, nesting, source count, context and output limits | No service rate limiter, process memory cap or provider deadline |
| Approved false statement | `poisoned-fact` intentionally returns false Net 1 quote | Permission/pins/exact citations do not establish factual truth |

The source inventory is bounded to 256 chunks. Trusted catalogue rows are bounded
to 64 sources with 32 bindings/readers each. Raw question JSON is <=4096 UTF-8
bytes; decoded question <=1000 characters; structure depth <=8. Context is <=1400
serialized characters, and output <=8192 UTF-8 bytes with 1..3 unique selected
quotes. These units are not provider-token measurements.

## Cases

| Name | Expected internal reason / observation |
| --- | --- |
| `clean` | `ok`; North Net 30 quote |
| `tenant-scope` | `ok`; South Net 15, same principal/document labels kept scoped |
| `direct-injection` | `input_blocked` before responder call |
| `forged-identity` | `input_invalid` for extra body authority |
| `malicious-document` | `ok`; one known flagged permitted chunk excluded |
| `sensitive-document` | `no_context`; declared email-like rule excludes chunk |
| `tampered` | `no_context`; representation no longer matches pin |
| `action-proposal` | `output_blocked` for an extra action field |
| `revocation` | `source_changed` after trusted grant removal |
| `tight-context` | `no_context`; responder skipped |
| `detector-miss` | Scanner misses spaced-out phrase; action proposal still blocked |
| `benign-quotation` | `no_context`; a deliberate detector false positive |
| `poisoned-fact` | `ok` while quoting an approved false fact; a documented quality failure |

Internal event reasons/counts are for trusted diagnostics; user-facing refusal
text is common across denied outcomes. Do not expose internal diagnostic records
as a public API indiscriminately. No raw query, prompt, answer, exception message
or denied source identifier is saved in the event. Correlation metadata still
needs an appropriate policy in a real service.

## Verify and extend deliberately

```bash
python -m ruff check labs/week_11 tests/test_week11_security.py
python -m ruff format --check labs/week_11 tests/test_week11_security.py
python -m mypy --strict --explicit-package-bases labs/week_11 tests/test_week11_security.py
python -m pytest tests/test_week11_security.py -q
```

Tests exercise actual local boundaries, same-name tenants, input ambiguity,
representation changes, selected-source exactness, revocation, benign utility,
detector misses/false positives, resource limits, cancellation/error propagation,
metadata minimization and all thirteen CLI cases. A retained HTML-like quote is
explicitly tested to require a separate safe renderer. Five fixed phrase rules
are not a model evaluation, penetration test or security certification.

Review the threat model when adding a provider, tool, source connector, cache,
history store, identity/admin service or new source classification. Keep real
credentials/data out of these synthetic exercises. Week 11 assessment questions
are deferred until the content workflow is complete.
