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
title: "Agentic AI Engineer foundation interview bank"
description: "Twenty guided foundation questions for AI and Agentic AI engineering interviews."
summary: "Practise production Python, SQL state, evaluation, reliability, system design, code review, incidents, and evidence-based architecture decisions."
permalink: "/interview-prep/roles/agentic-ai-engineer/"
kicker_primary: "Agentic AI Engineer"
kicker_secondary: "Batch 1 · 20 guided questions"
current_label: "Role bank"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
question_count: 20
---
## How to use this bank

These are interview-practice prompts, not a scored learning assessment. Answer aloud before opening the revision links. A strong response should state assumptions, make a decision, explain trade-offs, and identify evidence or failure modes. Use the follow-up probe to test whether the answer survives a deeper round.

### Suggested practice loop

1. Select five questions from different sections.
2. Give a 90-second answer without notes.
3. Compare your answer with the strong-answer signals.
4. Open only the revision sheet needed for the gap.
5. Repeat the answer in 45 seconds, then record one concrete project example.

**Bank size:** 20 questions · **Batch:** 1 core foundations · **Status:** review candidate

## Python and service engineering

### AIE-B1-01 — Why are mutable default arguments dangerous, and how would you fix the function?

**Round:** Python · **Depth:** Foundation

**Strong answer signals**

- Defaults are created once at function definition, so calls can share state.
- Use `None` or an immutable sentinel and create the container inside the function.
- Mention a regression test proving two calls do not affect one another.

**Follow-up probe:** How does this differ from a shallow-copy bug in nested state?

**Revision links:** [Python]({{ '/interview-prep/cheat-sheets/python/' | relative_url }})

### AIE-B1-02 — Choose among threads, processes, and `asyncio` for an AI API that performs HTTP model calls plus CPU-heavy parsing.

**Round:** Python · **Depth:** Applied

**Strong answer signals**

- Use async I/O for many waiting network calls with bounded concurrency.
- Move CPU-bound parsing to a process pool or separate worker; the GIL limits CPU-bound threads.
- Discuss timeouts, cancellation, pool limits, and measurement instead of choosing one mechanism globally.

**Follow-up probe:** What changes if the model client is synchronous and cannot be replaced?

**Revision links:** [Python]({{ '/interview-prep/cheat-sheets/python/' | relative_url }})

### AIE-B1-03 — How would you prevent 1,000 concurrent requests from overwhelming an external model endpoint?

**Round:** System design · **Depth:** Applied

**Strong answer signals**

- Bound admission and in-flight calls with queues, semaphores, or worker limits.
- Apply deadlines, rate limits, backpressure, and explicit overload responses.
- Track queue depth, saturation, latency percentiles, timeout rate, and downstream quotas.

**Follow-up probe:** Where should retries be placed, and when should they be disabled?

**Revision links:** [Python]({{ '/interview-prep/cheat-sheets/python/' | relative_url }}) · [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }})

### AIE-B1-04 — Design the validation and error contract for a classification endpoint.

**Round:** API design · **Depth:** Applied

**Strong answer signals**

- Validate types, sizes, enums, and cross-field invariants at the boundary.
- Return stable machine-readable error codes with safe messages and correlation IDs.
- Keep business failures distinct from transport failures and never expose prompts, secrets, or stack traces.

**Follow-up probe:** Which failures are safe to retry automatically?

**Revision links:** [Python]({{ '/interview-prep/cheat-sheets/python/' | relative_url }})

## Data and persistence

### AIE-B1-05 — A join doubled the reported number of successful model runs. How do you diagnose it?

**Round:** SQL · **Depth:** Foundation

**Strong answer signals**

- State the intended grain of every table before joining.
- Measure row counts and key uniqueness before and after each join.
- Pre-aggregate or deduplicate the many side, then validate totals against an independent query.

**Follow-up probe:** When is `COUNT(DISTINCT run_id)` a repair, and when does it hide a modeling error?

**Revision links:** [SQL]({{ '/interview-prep/cheat-sheets/sql/' | relative_url }})

### AIE-B1-06 — Design a minimal relational model for idempotent AI requests and attempts.

**Round:** SQL and architecture · **Depth:** Applied

**Strong answer signals**

- Separate the semantic request from individual attempts and outputs.
- Use a unique idempotency key scoped to tenant and operation, plus request fingerprint.
- Persist status transitions, model/config version, timestamps, error class, and audit-safe metrics transactionally.

**Follow-up probe:** How would you handle the same idempotency key with a different payload?

**Revision links:** [SQL]({{ '/interview-prep/cheat-sheets/sql/' | relative_url }}) · [Python]({{ '/interview-prep/cheat-sheets/python/' | relative_url }})

### AIE-B1-07 — Write the reasoning for selecting the latest valid model result per request.

**Round:** SQL · **Depth:** Applied

**Strong answer signals**

- Define valid status and deterministic ordering, including a tie-breaker.
- Use `ROW_NUMBER()` over request partitions ordered by completion time and attempt ID.
- Filter validity before ranking when invalid attempts must not displace a valid result.

**Follow-up probe:** How would late-arriving corrections change the query?

**Revision links:** [SQL]({{ '/interview-prep/cheat-sheets/sql/' | relative_url }})

## Evaluation and model decisions

### AIE-B1-08 — Explain a confidence interval for an observed 92% task-success rate.

**Round:** Statistics · **Depth:** Foundation

**Strong answer signals**

- It is an interval from a procedure with stated long-run coverage, not a probability that a fixed parameter lies inside.
- State the sample size, independence assumptions, and sampling design.
- Report the interval and important slices rather than only the point estimate.

**Follow-up probe:** What if cases are clustered by customer or workflow?

**Revision links:** [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

### AIE-B1-09 — For a rare unsafe-action detector, when would PR-AUC be more useful than ROC-AUC?

**Round:** Metrics · **Depth:** Applied

**Strong answer signals**

- Rare positives can make a small false-positive rate operationally large.
- PR focuses on precision and recall for the positive class and should be compared with prevalence.
- Still choose an operating threshold using harm, review capacity, and recall requirements.

**Follow-up probe:** What metric would you add if predicted probabilities drive escalation?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

### AIE-B1-10 — How do you detect leakage in an agent or LLM evaluation dataset?

**Round:** ML · **Depth:** Applied

**Strong answer signals**

- Trace whether labels, future outcomes, reference answers, or derived fields enter inputs.
- Check near-duplicate entities and templates across train, development, and held-out sets.
- Keep preprocessing and prompt/model selection inside the development boundary and protect the final set.

**Follow-up probe:** How would contamination from public benchmark answers appear?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

### AIE-B1-11 — A larger model improves accuracy by 1% but triples latency and cost. How do you decide?

**Round:** ML · **Depth:** Applied

**Strong answer signals**

- Start from minimum acceptable quality and operational constraints.
- Compare confidence intervals, failure slices, calibration, latency percentiles, throughput, and total cost.
- Consider routing, cascade, abstention, or a smaller baseline rather than one model for every case.

**Follow-up probe:** What evidence is required before claiming the 1% improvement is meaningful?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

### AIE-B1-12 — Design an experiment to compare a new AI-assisted workflow with the current process.

**Round:** Statistics and product · **Depth:** Applied

**Strong answer signals**

- Define the unit, randomization, primary outcome, guardrails, exposure, and analysis window.
- Estimate sample size from baseline, minimum useful effect, variance, and power.
- Plan for noncompliance, interference, novelty, sample-ratio mismatch, and operational adoption.

**Follow-up probe:** When would a switchback or cluster-randomized design be preferable?

**Revision links:** [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }}) · [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }})

## Production reasoning

### AIE-B1-13 — Offline accuracy improved, but production business outcomes did not. What do you check first?

**Round:** Debugging · **Depth:** Applied

**Strong answer signals**

- Verify instrumentation, population, label timing, and online/offline feature parity.
- Check threshold, calibration, workflow adoption, latency, capacity, and whether the action can change the outcome.
- Segment by time and cohort, compare with the baseline, and avoid blaming drift without evidence.

**Follow-up probe:** How would you separate model failure from product-workflow failure?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [SQL]({{ '/interview-prep/cheat-sheets/sql/' | relative_url }})

### AIE-B1-14 — Design a production email-classification service before adding any generative model.

**Round:** System design · **Depth:** Applied

**Strong answer signals**

- Define taxonomy, ambiguity/escalation policy, throughput, latency, privacy, and success metrics.
- Start with a deterministic or classical baseline, versioned preprocessing, API validation, and an auditable result store.
- Include canary rollout, monitoring, human review, retry/idempotency behavior, and rollback.

**Follow-up probe:** Which requirements would justify an LLM instead of a smaller classifier?

**Revision links:** [Python]({{ '/interview-prep/cheat-sheets/python/' | relative_url }}) · [SQL]({{ '/interview-prep/cheat-sheets/sql/' | relative_url }}) · [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }})

### AIE-B1-15 — An AI assistant returns five candidate documents. Which retrieval metrics would you use and why?

**Round:** Ranking metrics · **Depth:** Applied

**Strong answer signals**

- Use Recall@K when missing relevant evidence is costly.
- Use MRR for the first useful result and NDCG for graded relevance across the ranking.
- Define the judged query population and include latency, coverage, and failure slices.

**Follow-up probe:** How can a higher offline NDCG fail to improve answer quality?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

### AIE-B1-16 — Explain a safe retry policy for model calls.

**Round:** Reliability · **Depth:** Applied

**Strong answer signals**

- Classify transient versus permanent failures and require idempotent semantics.
- Bound attempts, backoff, jitter, per-attempt timeout, and total deadline.
- Honor server retry hints, prevent retry storms, and expose exhaustion as an explicit outcome.

**Follow-up probe:** Why is retrying a validation error harmful?

**Revision links:** [Python]({{ '/interview-prep/cheat-sheets/python/' | relative_url }})

## Ownership and evidence

### AIE-B1-17 — What do you inspect when reviewing a Python AI-service pull request?

**Round:** Code review · **Depth:** Lead

**Strong answer signals**

- Contracts, validation, authorization, resource cleanup, concurrency bounds, and failure semantics.
- Tests for happy, boundary, negative, duplicate, and cancellation paths.
- Observability, dependency/config changes, privacy, rollout, rollback, and whether complexity is justified.

**Follow-up probe:** Which issues block merge versus become follow-up work?

**Revision links:** [Python]({{ '/interview-prep/cheat-sheets/python/' | relative_url }})

### AIE-B1-18 — Explain one AI project at two-minute and ten-minute depth.

**Round:** Project deep dive · **Depth:** Lead

**Strong answer signals**

- Lead with the business decision, constraints, baseline, and measurable outcome.
- Defend architecture, data, evaluation, operational trade-offs, and alternatives.
- State what failed, what remains unproven, and what you would change next.

**Follow-up probe:** Which number would a skeptical interviewer ask you to prove?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

### AIE-B1-19 — A release increases p95 latency and duplicate downstream calls. How do you respond?

**Round:** Incident · **Depth:** Lead

**Strong answer signals**

- Stop or roll back the change using the safest bounded path.
- Use traces and idempotency evidence to isolate queueing, retry, and concurrency changes.
- Reconcile ambiguous side effects, communicate impact, and add a regression gate after root cause is established.

**Follow-up probe:** What data must be retained without logging sensitive payloads?

**Revision links:** [Python]({{ '/interview-prep/cheat-sheets/python/' | relative_url }}) · [SQL]({{ '/interview-prep/cheat-sheets/sql/' | relative_url }})

### AIE-B1-20 — When should an AI workflow remain deterministic instead of becoming an agent?

**Round:** Trade-off · **Depth:** Lead

**Strong answer signals**

- Prefer deterministic logic when the path, rules, and acceptable outputs are known.
- Use model-driven choice only when variability provides measurable value and is bounded by validation and authority.
- Compare reliability, auditability, latency, cost, security, and recovery—not novelty.

**Follow-up probe:** What is the smallest experiment that could justify agentic behavior?

**Revision links:** [Machine learning]({{ '/interview-prep/cheat-sheets/machine-learning/' | relative_url }}) · [Probability and statistics]({{ '/interview-prep/cheat-sheets/probability-statistics/' | relative_url }})

## Completion evidence

- You can answer at least 16 of 20 questions without reading the signals first.
- Every answer includes one relevant metric, constraint, failure mode, or project example.
- You can compress an applied answer from two minutes to 45 seconds without losing the decision.
- You have recorded weak areas against the stable question IDs for later re-testing.
