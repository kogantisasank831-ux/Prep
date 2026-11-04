# Week 17 multi-agent coordination contracts — revision 2

Source: `Path.md`, Week 17, and the synthetic procurement investigation used in
Weeks 14–16. These rules describe a deterministic local teaching system. They do
not define a production procurement, identity or authorization policy.

| ID | Effective rule and acceptance |
| --- | --- |
| W17-BR1 | The system investigates one declared procurement case. It may recommend `no_review`, `review_required` or `needs_human`; every successful report stops at `awaiting_approval` and grants no authority to order, contact or pay. |
| W17-BR2 | Four specialist boundaries exist only where ownership is distinct: document terms, SQL price evidence, supplier risk and commercial synthesis. The commercial specialist owns no source retrieval. |
| W17-BR3 | Missing applicable contract terms are business uncertainty and produce `needs_human`. An elevated supplier risk or variance above the found threshold produces `review_required`. Otherwise the recommendation is `no_review`. |
| W17-FR1 | The supervisor dispatches document, SQL and supplier-risk work as one bounded first wave. It uses at most three worker threads and submits each declared specialist exactly once. |
| W17-FR2 | The commercial specialist runs only after all three first-wave results have passed identity and type validation. It receives those findings, not the whole case or conversation. |
| W17-FR3 | Every assignment and result is a strict, frozen, closed model correlated by run ID, case ID and specialist name. Source results also carry a governed source reference and digest. |
| W17-FR4 | The supervisor alone owns aggregate run state. Specialists are stateless functions over immutable assignments and do not read or mutate one another's state. |
| W17-FR5 | Completion order never changes the public trace. Results are collected and validated in the declared document, SQL, supplier-risk order after concurrent submission. |
| W17-FR6 | A missing specialist, raised exception, wrong result type, wrong specialist, wrong run or wrong case fails the run closed. A failed run contains no commercial report. |
| W17-FR7 | The sequential baseline invokes the same four components and business rules without parallel execution or inter-agent handoffs. Equal inputs must produce an equal commercial report. |
| W17-FR8 | The architecture comparison reports handoffs and dependency stages. It records no measured latency because the local fixtures do not represent model, network or production execution time. |
| W17-DR1 | Document, SQL and risk records are synthetic, local and addressed by distinct source references. A SHA-256 digest detects fixture-byte disagreement; it is not proof of truth, identity or authorization. |
| W17-DR2 | Money and percentage calculations use `Decimal` with an explicit two-decimal half-even result. No binary float participates in the decision. |
| W17-DR3 | Handoffs exclude prompts, raw conversation and unrelated source bodies. Each first-wave specialist receives only the identifiers and source reference required for its job. |
| W17-SR1 | The specialist registry is copied into an immutable allowlist of the four declared roles. A specialist cannot select another specialist or create unbounded fan-out. |
| W17-SR2 | Source kind, source digest, purchase order and supplier correlations are checked before a finding is returned. |
| W17-SR3 | Every successful report sets `requires_human_approval=true`. No lab function implements email, purchase-order mutation, supplier contact, payment or another external effect. |
| W17-SR4 | The lab catches ordinary specialist exceptions at the coordination boundary. Declared specialist/validation errors expose controlled codes; unexpected exceptions expose only their class, not arbitrary exception text. It does not catch interpreter-exit signals. |
| W17-NFR1 | Given the same case, run ID and registry, report, findings, metrics and trace are deterministic. |
| W17-NFR2 | The lab makes no model, provider, network, database or secret-dependent call and adds no dependency. |
| W17-NFR3 | Tests cover each business route, actual concurrent admission, dependency order, strict handoffs, deterministic output, corrupted provenance, failure propagation, bounded fan-out and baseline parity. |
| W17-AS1 | Publish a 100-item practice bank with 30 single-choice, 20 multiple-correct, 15 matching, 15 short-answer and 20 self-contained Python coding questions. Every generated 10-question paper contains exactly two of each type for 100 marks. Each coding task has five executable checks, its reference passes all five, its starter scores zero and a distinct plausible wrong implementation loses marks. |

## Decision precedence

The commercial specialist applies these rules in order:

1. missing terms or threshold → `needs_human`;
2. inactive supplier or elevated risk → `review_required`;
3. variance above the threshold → `review_required`; and
4. otherwise → `no_review`.

The precedence is deliberate. An unknown contract threshold cannot be repaired by
a low supplier-risk score, and a risky supplier still needs review when price is
within threshold.

## Explicit boundaries

The word “agent” names an ownership and contract boundary in this lab. The
specialists are deterministic functions so coordination behavior is observable
without mixing in model variability. A production adapter may use a governed
model or service behind the same contract, but it must preserve correlation,
validation, timeouts, authorization, observability and approval controls.
The browser assessment models the same observable contracts with small
independent standard-library functions; actual concurrent execution remains in
the local lab.

Cross-process job queues, cancellation of stuck remote work, retries,
idempotency keys, rate limits, model evaluation, authenticated identities,
production source adapters, durable checkpoints and distributed traces are out
of scope. Their absence prevents a production-readiness claim; it does not block
the Week 17 supervisor, handoff, boundary, parallelism and comparison outcomes.
