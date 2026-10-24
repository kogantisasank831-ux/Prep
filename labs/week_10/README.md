# Week 10 — local request tracing

Observe the real Week 7–8 authorized hybrid-search, reranking, context and citation
components. The returned answer remains the Week 8 cited-extractive response.
An optional scripted model fixture is observed separately; it does not replace
that answer or perform inference. No additional dependencies or API keys.

From the repository root in the declared Python environment:

```bash
python -m labs.week_10.demo --scenario payment --output-dir .runtime/week10-payment
python -m labs.week_10.demo --scenario tight --output-dir .runtime/week10-tight
python -m labs.week_10.demo --scenario model-fixture --output-dir .runtime/week10-model --capture-synthetic-content
python -m pytest tests/test_week10_tracing.py -q
```

Use a fresh output directory on every run. The writer refuses to replace earlier
artifacts. `trace.json` contains bounded metadata. The explicit synthetic capture
also writes request/rewrites, authorized retrieved chunks, reranked identities,
context, constructed prompt and fixture response when available. A failed call
may have no completed content result; inspect its recorded stages instead.

| Scenario | Expected behavior |
| --- | --- |
| `payment` | Three supporting spans for the Schedule A payment question |
| `tight` | Same candidates/ranking; 300-character context retains the payment term but loses the connecting clause and line item |
| `denied` | No evidence for an ungranted principal; completed operational outcome |
| `missing-fact` | Catalogue excerpts lack the requested date; execution success does not establish quality |
| `bad-rewrite` | Query planner rejects lost protected terms; nonzero exit |
| `model-fixture` | Explicit prompt/model spans, scripted 1,000/300/0 usage and illustrative USD 0.0044 estimate |
| `model-timeout` | Scripted timeout, missing usage, closed error spans; nonzero exit |
| `model-invalid` | Empty scripted response rejected at the model contract; nonzero exit |

## Files and contracts

- `tracing.py`: request-local IDs, explicit active parents, UTC chronology,
  monotonic intervals, closed bounded attributes, failure categories and delivery.
- `generation.py`: raw-text prompt, typed model response/identity, usage
  provenance and exact Decimal arithmetic with caller-supplied per-million rates.
- `pipeline.py`: spans around reused domain functions; parity tested against all
  30 Week 9 cases. Model output remains separate from the extractive answer.
- `demo.py`: fixed synthetic scenarios and exclusive file output.

Schema `week10-local-trace/1.0.0` is custom teaching JSON, **not OTLP**. Records
are in completion order; rebuild hierarchy with IDs and sort valid start offsets
for a timeline. Status `ok/error/cancelled` is a local operational contract, not
an OTel status enum or answer-quality score. Null timings/counts stay unknown.

The root interval excludes ingestion and export, and includes observation and
development source hashing. One recorder handles one synchronous request; it is
not thread-safe, asynchronous, distributed or a durable audit log. At most 64
spans are retained by default; drops/timing errors are visible. Export is one
best-effort attempt with a separate result and no retry/model fallback.

Raw query/prompt/passage/response and exception messages are excluded by the
pipeline's routine projection. The attribute allowlist bounds shape/size; it is
not content-aware DLP. Metadata/hashes still require an appropriate access and
retention policy. The optional capture is for this synthetic corpus only and
goes nowhere external.

Default generation usage is not applicable. Fixture counters are scripted, not
tokenizer measurements. Provider mode is only a typed extension port, with no
live adapter supplied. Timeout is an injected exception, not a network deadline.
The illustrative rate card is not a provider price list or an invoice; unknown
usage/cache/rates produce a null estimate rather than zero. The prompt/output
contracts do not establish faithfulness, truth or injection resistance.

## Validation

```bash
python -m ruff check labs/week_10 tests/test_week10_tracing.py
python -m ruff format --check labs/week_10 tests/test_week10_tracing.py
python -m mypy --strict --explicit-package-bases labs/week_10 tests/test_week10_tracing.py
python -m pytest tests/test_week10_tracing.py -q
```

Tests cover all 30-case parity, denied-source invariance, parent lifecycle,
bounded storage, invalid clocks, failure/cancellation propagation, export
isolation, explicit content capture, usage provenance, exact cost and the
paired context regression. These establish local fixture behavior, not deployed
model quality, provider billing correctness or production latency.
