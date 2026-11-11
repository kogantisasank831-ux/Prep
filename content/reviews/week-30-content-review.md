# Week 30 content and lab review

## Scope and disposition

Roadmap source: `Path.md`, Week 30 — Serving and documentation. The candidate
completes the optional phase but remains unpublished pending human approval.

## Coverage and findings

The lessons cover weight quantisation, theoretical memory, KV capacity,
headroom, admission, vLLM-or-equivalent target benchmarking, batching,
throughput, TTFT, latency tails, immutable package manifests, clean-load tests,
rollback and the complete experiment report.

The lab keeps calculated weight/KV estimates separate from supplied load
observations and validates all required report sections. Tests cover formulas,
precision changes, feasible/infeasible concurrency, percentile arithmetic,
strict observations, missing/invalid reports, warnings and CLI modes. It does
not launch a runtime, allocate a GPU or claim production capacity.

