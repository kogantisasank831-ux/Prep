# Week 21 content and lab review

## Scope and disposition

Roadmap source: `Path.md`, Week 21 — Cost and latency optimisation.

Reviewed artifacts are the production and beginner lessons, `labs/week_21/`,
`tests/test_week21_optimization.py` and the Week 21 portion of the shared
assessment bank test. Version 1.0.0 is `status: approved`; Week 21 is included in
both public navigation allowlists after user approval on 2026-11-12.

## Coverage

| Roadmap requirement | Treatment | Executable evidence |
| --- | --- | --- |
| Model routing | task/complexity routing plus quality escalation | small/large selection and escalation tests |
| Token budgeting | input/output accounting and per-request ceiling | visible budget rejection |
| Context pruning | required versus optional boundary | only declared optional tokens removed |
| Caching | tenant/model/prompt/data exact scope | hit, miss and cross-scope tests |
| Parallel calls | independent group critical path | max-within-group versus sequential sum |
| Batching/streaming | throughput/queue and TTFT/completion distinctions | explicit lesson limits; latency fixture |
| Quality/cost/latency comparison | identical workload under two strategies | deterministic comparison report |

## Review findings

The lab uses integer microunits, basis points and milliseconds so exact results
remain deterministic. Values are labelled synthetic throughout; they are not
vendor pricing, model benchmarks or capacity claims. The workload is
materialised before two strategies run, preventing generator exhaustion from
fabricating a saving. The cache omits recommendation work and scopes eligible
read-like results by tenant, model, prompt and data key.

Both lessons distinguish TTFT from completion, batching from parallelism and
exact caching from semantic caching. Production gaps—tokenizer/model calls,
queue contention, continuous batching, cancellation, GPU memory and semantic
false hits—are explicit.

## Focused verification

- Ruff lint/format and strict mypy pass for the Week 21 lab and tests.
- All focused Week 21 behavior and CLI tests pass.
- The Week 21 bank passes the shared 1,000-paper JavaScript contract and all 20
  coding references pass five checks.
- Publication is approved and the completed live checks are recorded in the
  [Weeks 21–30 publication verification](weeks-21-30-publication-verification.md).
