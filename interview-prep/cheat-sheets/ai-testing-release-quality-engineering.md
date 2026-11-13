---
layout: "week"
status: "approved"
version: "1.0.0"
last_reviewed: "2026-11-11"
imported_on: "2026-11-13"
source_repository: "kogantisasank831-ux/transformer-explainer"
source_commit: "cdd45b6b0c08c5d88a626e4d16853abdf285f08d"
source_path: "AI_Data_Science_Interview_Cheat_Sheets/Batch_10_AI_Engineering_Platform/39_AI_Testing_Release_Quality_Engineering_Cheat_Sheet.md"
header_context: "Interview cheat sheets"
back_label: "Cheat sheets"
back_url: "/cheat-sheets/"
toc_heading: "Cheat-sheet sections"
pagination_label: "Cheat sheets hub"
pagination_url: "/cheat-sheets/"
title: "AI testing, release quality, and evaluation engineering interview cheat sheet"
description: "Interview revision for deterministic tests, model and GenAI evaluation, security and performance testing, release gates, canaries, and rollback."
summary: "Revise test boundaries, statistical model evaluation, RAG and agent evaluation, adversarial and performance tests, immutable candidates, release gates, canaries, and rollback."
permalink: "/interview-prep/cheat-sheets/ai-testing-release-quality-engineering/"
kicker_primary: "Interview revision"
kicker_secondary: "Batch 10 · Release quality"
current_label: "Revision guide"
alternate_label: "Cheat sheets hub"
alternate_url: "/cheat-sheets/"
---

**Target roles:** AI Engineer, ML Engineer, Applied Scientist, Senior/Lead Data Scientist, MLOps/LLMOps Engineer, AI Quality Lead<br>
**Use:** testing rounds, model/evaluation design, CI/CD, release reviews, GenAI/RAG/agent quality, incident prevention<br>
**Interview rule:** define the requirement, risk, oracle, data slice, threshold, uncertainty, release identity, and rollback before naming a testing tool. A high average benchmark score is not a production release decision.

## 1. Thirty-second revision

- Verification asks whether the system was built to its specification; validation asks whether it is fit for the intended use. AI release evidence needs both.
- Test deterministic code with exact assertions. Test probabilistic components with task-specific metrics, slices, repeated trials or confidence intervals, and predeclared decision rules.
- The test pyramid extends beyond unit tests: static checks, unit/property, component, contract, integration, end-to-end, model/data evaluation, security, performance, resilience, and canary verification.
- Separate code defects, data defects, model-quality regressions, nondeterminism, infrastructure failures, and evaluator noise.
- Keep evaluation datasets versioned with provenance, consent/license, cutoff, inclusion/exclusion rules, labels, slices, and contamination controls.
- A golden set protects known important behavior; a challenge set targets rare, adversarial, safety, and failure cases. Neither represents all future traffic.
- Compare the exact candidate with the exact approved baseline. Record code, model, prompt, index, tools, data, runtime, configuration, and evaluator identity.
- LLM-as-judge is a measurement instrument, not ground truth. Calibrate it against qualified human labels, test position/style bias, and record judge version and uncertainty.
- Test RAG retrieval and generation separately; test agents at tool schema, policy, state transition, termination, and end-to-end outcome levels.
- Gate on multiple dimensions: functionality, quality, safety, security, fairness where relevant, latency, capacity, reliability, and cost.
- Canary or shadow traffic reduces uncertainty but does not replace offline gates. Define stop conditions and rollback before exposure.
- After release, run smoke checks and monitor leading plus delayed outcome signals; a green deployment status is not user acceptance.

## 2. Quality contract and evidence boundary

Write:

> For **use case U** and **population/slice P**, candidate **C** must satisfy **requirements R** against baseline **B**, measured by **methods M** on dataset/workload **D**, within **uncertainty Q**, while passing **risk gates G**, before **exposure E**.

Clarify:

- intended user, decision, harm, and excluded use;
- deterministic versus statistical/probabilistic acceptance;
- business metric, model metric, service SLO, and safety/security constraints;
- evaluation unit: row, user, conversation, document, event, session, or workflow;
- positive/negative classes, severity, cost matrix, and abstention/escalation;
- dataset time cutoff, source, rights, privacy, and representativeness;
- baseline and minimum acceptable effect/non-inferiority margin;
- overall and critical-slice thresholds;
- sample size, repetitions/seeds, confidence method, and multiple comparisons;
- candidate and evaluator identities;
- who can approve an exception and its expiry;
- canary exposure, rollback condition, and post-release verification.

Do not invent a threshold because it is round. Tie it to user harm, business tolerance, SLO, regulation/policy, or an approved baseline.

## 3. Test portfolio by layer

| Layer | Purpose | Typical evidence |
|---|---|---|
| Static/build | prevent syntax, type, dependency, secret, and packaging defects | lint/type/build/SBOM/signature results |
| Unit | isolate deterministic rule or transformation | exact input/output and error assertions |
| Property/fuzz | explore invariant and input space | generated minimal counterexamples |
| Component | test one service/model adapter with controlled dependencies | lifecycle, edge, timeout, and resource tests |
| Contract | verify HTTP/event/schema compatibility | consumer/provider and OpenAPI/event checks |
| Integration | exercise real boundaries in a controlled environment | database/broker/object/model interactions |
| End-to-end | prove a critical user journey across deployed components | outcome plus trace/artifact evidence |
| Data/model eval | measure statistical performance and slices | versioned dataset, metrics, uncertainty |
| GenAI/RAG/agent eval | measure retrieval, grounding, policy, tool outcome | traces, scorers, human calibration |
| Performance | establish latency, throughput, saturation, cost | repeatable benchmark/load report |
| Security/resilience | find abuse and failure recovery gaps | threat-led tests, fault injection, recovery |
| Canary/post-release | test exact release under limited real conditions | guardrails, stop/rollback and monitoring |

More end-to-end tests do not compensate for missing unit or contract tests; they are slower, noisier, and harder to diagnose. Use the lowest layer that can expose the risk, then retain a few critical journeys.

## 4. Deterministic software testing

### Unit tests

Good unit tests:

- map to an accepted rule or invariant;
- cover happy, boundary, invalid, and failure paths;
- use one clear reason to fail;
- avoid wall clock, network, randomness, and shared mutable state unless controlled;
- assert behavior, not private implementation;
- test cleanup and error translation.

Parameterization expresses a compact input/output matrix. Fixtures should expose dependencies and clean up; overly broad fixtures create hidden coupling.

### Property-based and fuzz testing

Examples of properties:

- serialize then deserialize preserves the supported value;
- a ranking contains no ineligible item or duplicate;
- tenant A can never retrieve tenant B's resource;
- token/cost never exceeds the configured budget;
- retry count and elapsed deadline remain bounded;
- idempotent replay has the same durable effect;
- normalization is stable under equivalent whitespace/Unicode forms.

Property generators must include realistic domains and dangerous boundaries. A passing random sample is not a proof; preserve discovered regressions as explicit examples.

### Test doubles

- **Stub:** returns fixed data.
- **Fake:** lightweight working implementation, such as in-memory repository.
- **Mock:** verifies interactions.
- **Simulator/emulator:** approximates an external system.

Mock the boundary you own, not every line. An LLM mock proves control flow, not model behavior. Contract and integration tests must cover the real protocol and representative service behavior.

## 5. Contract and integration testing

### API/event contracts

Check:

- required/optional fields, types, units, enum and null behavior;
- additive versus breaking evolution;
- status/error codes and retry classification;
- auth scopes, tenant/resource ownership, pagination, idempotency;
- maximum payload/token sizes and streaming terminal/error events;
- event key, ordering, schema version, duplicate handling, and DLQ/replay.

Validate the OpenAPI/event schema itself, compare generated clients when used, and test both consumer and provider expectations. A syntactically valid schema can still encode the wrong business meaning.

### Integration environment

Prefer disposable real dependencies or a faithful controlled service for databases, brokers, object stores, caches, and vector stores. Pin image versions and migrations. Seed small deterministic data, isolate tests, and collect logs/traces on failure.

Test:

- transactions, isolation, rollback, outbox and duplicate delivery;
- timeout, cancellation, connection exhaustion and partial failure;
- index refresh and point-in-time visibility;
- credential expiry and permission denial;
- schema migration forward/backward compatibility;
- cleanup after worker/process termination.

## 6. Data and model evaluation

### Dataset identity

Record:

- immutable snapshot/digest and extraction query;
- source, collection period, cutoff, license/consent and privacy controls;
- label definition, annotator process, agreement/adjudication;
- deduplication, leakage and train/eval contamination checks;
- inclusion/exclusion and missingness;
- slice definitions and expected deployment mix;
- transformations and feature code;
- known gaps and review owner.

Never tune repeatedly on the final holdout and continue calling it unseen. Use train/tuning validation, locked test, challenge/safety sets, and post-release samples with explicit purposes.

### Metric and uncertainty

Match metric to the decision:

- classification: precision/recall/F1, PR-AUC/ROC-AUC, log loss, Brier, calibration, cost at threshold;
- ranking/retrieval: Recall@K, MRR, nDCG, coverage and latency;
- regression/forecast: MAE/RMSE/quantile loss, calibration/coverage by horizon;
- generative: task correctness, groundedness, citation accuracy, refusal/safety and human preference;
- operations: valid completion, override/escalation, latency, cost and downstream outcome.

Report confusion counts and slices, not one aggregate. Quantify uncertainty with an appropriate bootstrap, analytic interval, paired test, or repeated-run distribution. Pair candidate and baseline on the same examples when possible.

### Release comparison

Predeclare whether the goal is:

- superiority;
- non-inferiority within an approved margin;
- meeting an absolute minimum;
- Pareto improvement across quality, latency, and cost;
- no critical-slice regression.

A statistically detectable improvement may be operationally irrelevant; a small average loss may conceal severe harm in a critical slice.

## 7. GenAI, RAG, and agent testing

### Prompt and structured output

Test instruction hierarchy, variable escaping, schema validity, required evidence, refusals, language, length, and adversarial inputs. Use semantic assertions where exact strings are inappropriate. Validate output with deterministic code and handle repair/failure explicitly.

### RAG decomposition

1. **Ingestion:** parsing, OCR, chunk coverage, metadata, ACL, deletion, and index freshness.
2. **Retrieval:** Recall@K/MRR/nDCG on answerable queries, filters/tenant ACL, hard negatives, latency.
3. **Context:** evidence coverage, duplication, ordering, token budget, and injection exposure.
4. **Generation:** answer correctness, groundedness, citation entailment, abstention, completeness, safety.
5. **End-to-end:** user task success, latency/cost, stale/unauthorized evidence, escalation.

A correct answer from the model's prior knowledge can hide failed retrieval; require evidence attribution when the product promises grounding.

### Agents

Test at four levels:

- tool input/output schema, authorization, idempotency, timeout and side effects;
- node/state transition, reducers, checkpoints, interrupts, and resume;
- policy: allowed tools/resources, budgets, approval, termination and fallback;
- end-to-end outcome: correct task, evidence, no forbidden action, acceptable steps/cost/latency.

Use deterministic fake tools for workflow logic, sandboxed real tools for integration, frozen traces for regression, and scenario simulations for failures. Test loops, duplicate actions, stale state, concurrent turns, tool injection, approval bypass, and resume after crash.

### LLM-as-judge

- write a rubric with observable dimensions and anchored examples;
- blind candidate/baseline identity and randomize order;
- calibrate against representative expert labels;
- measure agreement and disagreement by slice;
- test verbosity, position, self-preference, and prompt-injection bias;
- pin judge model, prompt, temperature/settings, and retries;
- adjudicate high-risk or material differences with humans.

Judge scores are noisy measurements. Do not promote solely because one judge's mean increased.

## 8. Security and adversarial testing

Start from a threat model. Cover:

- direct and indirect prompt injection;
- cross-tenant retrieval/cache/session leakage;
- malicious files, URLs, archives, model artifacts, and deserialization;
- tool argument manipulation, SSRF, excessive agency, and approval bypass;
- training/RAG poisoning and hidden triggers;
- sensitive data extraction, memorization, logging, and deletion;
- model theft/abuse, denial of service/wallet, and quota evasion;
- dependency/image/model supply chain;
- jailbreaks and unsafe content relevant to intended use.

Use bounded, authorized test environments and privacy-safe data. Red-team findings need severity, reproducible evidence, owner, remediation, regression test, and retest. Absence of discovered findings is not proof of security.

## 9. Performance, load, and resilience

### Workload model

Define arrival pattern, concurrency, input/output/token distribution, cache ratio, tenant mix, streaming, think time, and downstream dependencies. Warm-up and steady state must be distinguished.

Measure:

- throughput and successful/valid throughput;
- queue wait, TTFT, inter-token and total p50/p95/p99;
- error/timeout/cancel/retry and partial response;
- CPU/RAM/GPU/VRAM, pools, queue depth/age;
- cost and energy if in scope;
- recovery time and work loss.

### Test types

- **Load:** expected and peak behavior.
- **Stress:** find saturation and degradation shape.
- **Spike:** rapid burst and autoscaling/admission response.
- **Soak:** leaks, fragmentation, drift and slow accumulation.
- **Capacity:** sustainable throughput under SLO with headroom.
- **Fault injection:** dependency delay/error, worker/Pod/node loss, credential or quota failure.

Test overload behavior: bounded queue, early rejection, priority, retry signal, graceful degradation, and recovery. “No errors” while latency exceeds the business deadline is a failed result.

## 10. Executable release-gate pattern

This small evaluator supports floors, ceilings, and maximum regression from a baseline. Real gates also need sample-size/uncertainty and critical-slice logic.

```python
from collections.abc import Mapping, Sequence


def evaluate_release_gates(
    candidate: Mapping[str, float],
    baseline: Mapping[str, float],
    gates: Sequence[Mapping[str, float | str]],
) -> list[str]:
    failures: list[str] = []

    for gate in gates:
        name = str(gate["metric"])
        direction = str(gate["direction"])
        value = candidate[name]
        previous = baseline[name]

        if direction == "higher":
            floor = float(gate["limit"])
            max_regression = float(gate.get("max_regression", 0.0))
            if value < floor:
                failures.append(f"{name}: {value} below floor {floor}")
            if previous - value > max_regression:
                failures.append(f"{name}: regression exceeds {max_regression}")
        elif direction == "lower":
            ceiling = float(gate["limit"])
            max_regression = float(gate.get("max_regression", 0.0))
            if value > ceiling:
                failures.append(f"{name}: {value} above ceiling {ceiling}")
            if value - previous > max_regression:
                failures.append(f"{name}: regression exceeds {max_regression}")
        else:
            raise ValueError(f"unknown direction: {direction}")

    return failures


candidate = {"grounded_accuracy": 0.91, "p95_ms": 820.0}
baseline = {"grounded_accuracy": 0.90, "p95_ms": 790.0}
gates = [
    {"metric": "grounded_accuracy", "direction": "higher", "limit": 0.88,
     "max_regression": 0.01},
    {"metric": "p95_ms", "direction": "lower", "limit": 900.0,
     "max_regression": 50.0},
]
assert evaluate_release_gates(candidate, baseline, gates) == []
```

Store gate definitions and results with the candidate; do not let a pipeline silently use today's changed default threshold against yesterday's result.

## 11. CI/CD/CT and release identity

A defensible pipeline may include:

1. formatting/lint/type, dependency lock and unit/property tests;
2. build immutable image/artifact, SBOM, scan, signature and provenance;
3. contract/integration/migration tests;
4. data schema/leakage/quality checks;
5. exact-candidate offline model/RAG/agent/safety evaluation;
6. performance/capacity and security tests proportionate to change;
7. deploy to controlled environment and run smoke/end-to-end;
8. approval with traceable evidence and exception handling;
9. shadow/canary/progressive exposure with automatic stop/rollback;
10. post-release smoke, SLO and quality verification.

Continuous training must produce a candidate; it must not automatically promote merely because training completed. Separate build, evaluation, approval, deployment, and verification identities and permissions.

Release identity includes:

- code/image digest and dependency lock;
- data/feature snapshot and schema;
- model/tokenizer/adapter/runtime;
- prompt/template/guardrail;
- embedding/chunker/index/corpus;
- workflow graph/tools/policies;
- evaluation data/scorers/judge;
- infrastructure/config/secret references;
- approval, deployment, and rollback record.

## 12. Progressive delivery and production verification

### Shadow

Send copied traffic to a candidate without affecting the user. Protect data, avoid duplicate side effects, and compare paired outcomes. Shadow cannot measure user behavior caused by candidate output.

### Canary

Expose a small eligible population. Predefine allocation, duration/sample, guardrail metrics, stop rules, maximum blast radius, and rollback. Avoid assigning related users inconsistently when interference matters.

### After release

Verify exact version, health, representative request, auth denial, telemetry, queue/latency, model output contract, and rollback readiness. Watch delayed labels and human overrides. Absence of alerts may mean telemetry failure; monitor the monitor.

## 13. Tool map

| Need | Tools to recognize | Selection caution |
|---|---|---|
| Python tests | pytest, unittest, Hypothesis | design and isolation matter more than runner |
| API contracts | OpenAPI validators, Schemathesis, Pact | schema correctness does not prove business semantics |
| Disposable dependencies | Testcontainers | pin images and avoid hiding unavailable production features |
| Load | Locust, k6, JMeter | workload distribution and coordinated omission matter |
| Data validation | Pandera, Great Expectations, TFDV | define ownership and failure policy |
| Tracking/registry | MLflow, Weights & Biases, cloud registries | lineage and promotion controls vary |
| ML monitoring | Evidently and platform-specific tools | detection is not diagnosis or remediation |
| RAG/GenAI eval | Ragas, DeepEval, TruLens, promptfoo, MLflow eval | scorer validity and judge calibration vary |
| Security evaluation | garak, PyRIT, promptfoo red-team features | authorized scope and scenario relevance are essential |

Libraries and APIs evolve. Verify version, maintained status, license, data handling, reproducibility, and whether a scorer has evidence for your use case.

## 14. Failure modes and debugging

| Failure | Why it happens | Better response |
|---|---|---|
| Flaky tests | uncontrolled time/randomness/network/shared state | seed/freeze/isolate, record failing input, fix ownership |
| Green offline, bad production | leakage, mismatch, weak slices, wrong metric | provenance, temporal holdout, replay, canary, outcome monitoring |
| Judge score jumps | judge/prompt changed or bias | pin identity, paired blind review, human calibration |
| Load result too good | cached tiny inputs, no arrivals, coordinated omission | representative open/closed model and tail checks |
| Agent test loops | no step/tool/token deadline | policy budgets, termination state and loop regression |
| Canary cannot rollback | incompatible data/schema/index side effect | expand/contract migration, dual compatibility, restore plan |
| Gate becomes ceremonial | thresholds waived without expiry/owner | risk-based exception with compensating controls and review |
| Test suite slow | too many broad integration/E2E tests | move invariants down, parallelize safely, retain critical journeys |

## 15. Rapid interview questions

**1. What is a model test oracle?**<br>
The rule or reference used to judge output: label, invariant, metric threshold, expert rubric, metamorphic relation, or approved baseline. It must be valid for the decision.

**2. How do you test nondeterministic LLM output?**<br>
Use task-level semantic/structural assertions, representative datasets and slices, repeated runs when needed, calibrated scorers/humans, uncertainty, and deterministic safety/contract checks.

**3. Golden versus challenge set?**<br>
Golden protects known high-value expected behavior; challenge targets difficult, rare, adversarial, or safety cases. Both need provenance and maintenance.

**4. Shadow versus canary?**<br>
Shadow observes candidate output without user effect; canary serves it to a limited population and can measure real behavior with risk controls.

**5. Why test retrieval separately from answer quality?**<br>
The generator can guess correctly despite failed retrieval, hiding grounding, freshness, authorization, and citation defects.

**6. What blocks an AI release?**<br>
Failed required functional, quality/slice, safety/security, reliability, performance/cost, or migration gates; missing identity/evidence; or no safe rollback.

**7. What is a flaky evaluation?**<br>
A decision changes materially without a meaningful candidate change because of sampling, model/judge randomness, service variability, or unstable data/tooling.

**8. Does 100% test pass mean complete quality?**<br>
No. It means the implemented checks passed in that environment. Missing requirements, untested distributions, human factors, and production differences remain.

## 16. Lead-level case: release a procurement agent

**Prompt:** Approve a new agent that reads tenders, retrieves policy, drafts recommendations, and can submit an action after human approval.

Strong answer:

1. Decompose risks: extraction accuracy, policy retrieval, recommendation grounding, tenant confidentiality, action authorization, human approval, duplicate submission, availability/cost.
2. Freeze a candidate identity across parser, model, prompt, index/corpus, workflow, tools, guardrails, and runtime.
3. Build temporal, representative golden data plus rare/challenge/adversarial scenarios; obtain qualified labels and approval-policy examples.
4. Unit/property-test parsers, budgets, authorization and idempotency; contract-test tool schemas; integration-test ACL retrieval, state/checkpoint and duplicate delivery.
5. Evaluate extraction fields, retrieval Recall@K/ACL, grounded recommendation/citations, abstention, unsafe action rate, critical slices, latency and cost.
6. Red-team indirect injection in documents, tool manipulation, cross-tenant access, approval bypass, SSRF and denial of wallet.
7. Run replay plus sandbox end-to-end; fault broker/model/index, crash before/after action, and verify resume without duplicate submission.
8. Shadow read-only decisions, then canary low-risk cases with mandatory approval; define stop rules and manual fallback.
9. Monitor valid completion, evidence quality samples, human edit/override, forbidden/duplicate attempts, latency, token/tool cost, and delayed business outcome.
10. Record approver, exception expiry, runbook, rollback and audit retention. Do not enable autonomous submission until separate risk acceptance and evidence exist.

## 17. Final checklist

- [ ] Requirement, risk, oracle, dataset/workload, baseline, threshold and uncertainty are explicit.
- [ ] Exact candidate and evaluator identities are immutable and traceable.
- [ ] Unit/property, contract, integration and critical E2E tests cover deterministic behavior.
- [ ] Evaluation data has provenance, rights/privacy, leakage controls, slices and known limits.
- [ ] Model/GenAI metrics align with user decision and include critical-slice evidence.
- [ ] RAG retrieval/generation and agent tool/state/policy/outcome are tested separately.
- [ ] Judge/scorer is calibrated; high-risk decisions include qualified human evidence.
- [ ] Security, load/stress/soak, failure recovery, migration and rollback are tested.
- [ ] CI gates cannot be silently bypassed; exceptions have owner, rationale and expiry.
- [ ] Shadow/canary, stop conditions, post-release verification and delayed monitoring exist.

## Primary references

- [pytest documentation](https://docs.pytest.org/en/stable/)
- [Hypothesis documentation](https://hypothesis.readthedocs.io/en/latest/)
- [OpenAPI Specification](https://spec.openapis.org/oas/)
- [MLflow documentation — Model Evaluation](https://mlflow.org/docs/latest/ml/evaluation/)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [NIST AI Resource Center — TEVV resources](https://airc.nist.gov/)
- [OWASP GenAI Security Project](https://genai.owasp.org/)
- [Google SRE Workbook — Canarying Releases](https://sre.google/workbook/canarying-releases/)
- [Kubernetes documentation — Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [OpenSSF — SLSA specification](https://slsa.dev/spec/)

**Evidence boundary:** passing checks demonstrates only the defined behavior on the recorded data, workload, candidate, evaluator, and environment. It does not prove universal correctness, fairness, security, causal business impact, or future production performance.
