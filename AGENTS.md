# Finance App Project Instructions

## Purpose and Scope

This repository contains a wealth-management application for portfolio tracking,
tax intelligence, alerts, and explainable AI-assisted asset-allocation decision
support.

These instructions apply to the entire repository. Keep this root `AGENTS.md` as
the single project-level instruction file unless the project owner explicitly
approves a different structure.

## Source of Truth

- Treat documents in `Design/` as the current product and architecture specification.
- Treat `Design/wealth-management-app-spec.md` as the product brief. Numbered
  implementation and low-level design documents refine it.
- Do not silently resolve contradictions between design documents. Identify the
  conflict, explain its impact, and record the agreed decision in the relevant document.
- Do not treat proposed libraries, frameworks, models, schedules, schemas,
  percentages, or deployment choices as final merely because they appear in a draft.
  Validate them during design review.
- Keep requirements, design decisions, implementation, and tests traceable to one another.

## Working Agreement

- Treat the project owner as an experienced Data Scientist / ML Engineer. Be concise
  and technical; omit generic introductions and basic syntax guidance.
- Work with the project owner to finalize design before beginning broad implementation.
- Before changing an existing design decision, state the issue, alternatives,
  trade-offs, and recommended option.
- Make reasonable, reversible decisions autonomously when they remain within an
  approved design. State material assumptions briefly.
- Ask before making choices that materially change product scope, compliance posture,
  architecture, cost, security boundaries, public contracts, or user-visible financial
  behavior.
- Prefer production-grade, maintainable, modular, and container-ready solutions.
- Make the smallest cohesive change that fully satisfies the approved requirement.
- Avoid speculative abstractions and dependencies for hypothetical future needs.
- Create new files only when separation of responsibility, reuse, or testability makes
  them structurally necessary.
- Preserve unrelated user changes; never overwrite, discard, revert, or reformat them.
- Prefer small, reviewable changes. Summarize files changed, decisions made, validation
  performed, assumptions, risks, and unresolved questions.
- Do not create additional instruction files, skills, or agent configurations unless
  the project owner requests them.

## Repository Scope and Safety

- Restrict file reads, searches, commands, and modifications to this repository.
- Do not access parent directories, home directories, or unrelated workspaces.
- Check the working tree before editing and preserve all unrelated changes.
- Do not perform destructive or irreversible operations without explicit approval.
- Do not modify generated files, lockfiles, schemas, migrations, CI, infrastructure,
  or public interfaces unless required by the approved task.
- Never expose, log, commit, or reproduce credentials, tokens, private keys, production
  data, personally identifiable information, or sensitive financial information.

## Repository Discovery

Before planning or editing:

1. Read this file and the relevant documents in `Design/`.
2. Inspect the repository layout, affected implementation, interfaces, and tests.
3. Identify the declared Python version, dependency manager, build system, and
   configured quality tools from repository files.
4. Reuse existing commands and conventions. Do not introduce a second formatter,
   linter, type checker, test framework, or package manager.
5. Check for contradictions, unresolved design questions, and unrelated working-tree changes.

If an essential command, requirement, or convention cannot be determined, ask rather
than inventing it.

## Development Lifecycle

For non-trivial changes:

1. Restate the objective, constraints, and acceptance criteria concisely.
2. Trace the requirement to the applicable design documents.
3. Inspect affected code paths, tests, contracts, data flows, and trust boundaries.
4. Identify compatibility, financial-correctness, data-quality, security, privacy,
   compliance, cost, and deployment risks.
5. Produce a concise implementation plan before editing.
6. Implement in small, reviewable increments.
7. Add or update tests alongside each meaningful behavior change.
8. Run the narrowest relevant checks during development.
9. Run all configured quality gates before final handoff when practical.
10. Review the final diff for regressions, leakage, security issues, dead code,
    accidental complexity, and unrelated changes.

Do not implement broad functionality while material requirements or design decisions
remain unresolved.

## Context Verification

At the beginning of a new conversation or substantial task, before editing:

- Confirm the current working directory and repository root.
- List every applicable `AGENTS.md` file in precedence order.
- State which design documents and implementation files were actually inspected.
- Distinguish observed facts, supplied instructions, assumptions, and unknowns.
- Identify relevant files that have not yet been inspected.
- Never imply that an unread file or directory has been reviewed.
- If repository scope or applicable instructions are uncertain, stop and clarify.

## Financial and Regulatory Guardrails

- The application provides investment information and decision support, not regulated
  investment advice, unless the operator's legal and regulatory status explicitly
  permits otherwise.
- Never implement autonomous trade execution. AI recommendations must not directly
  modify holdings, place orders, or trigger financial transactions.
- Require explicit human approval for every AI-generated recommendation. Approval may
  create a plan or alert only; it must not execute a trade.
- Present allocation recommendations as explainable ranges or scenarios with assumptions,
  risks, and source attribution. Avoid guarantees and unsupported certainty.
- Keep rule-based portfolio alerts independent from AI recommendations.
- Treat tax results as estimates unless validated and approved for formal tax reporting.
  Display the applicable financial year, rule-set version, assumptions, and calculation
  provenance.
- Store tax rules as effective-dated or financial-year-versioned data. Never hardcode
  changeable tax rates, thresholds, holding periods, or exemptions in business logic.
- Verify current legal, tax, regulatory, exchange, and source-licensing claims against
  authoritative primary sources before finalizing or implementing them.
- Do not crawl or scrape a source until its API terms, robots policy where applicable,
  licensing, retention rights, and attribution requirements have been reviewed and recorded.

## Security, Privacy, and Data Integrity

- Treat portfolio data, transactions, tax records, identity data, uploaded statements,
  risk profiles, and recommendations as sensitive financial information.
- Enforce tenant isolation and object-level authorization on every user-owned resource.
  Never trust a client-supplied user or portfolio identifier without authorization checks.
- Apply least privilege, secure secret storage, encryption in transit, and encryption at rest.
- Minimize collected data and define retention and deletion behavior before production use.
- Maintain an append-only audit trail for imports, material corrections, tax calculations,
  recommendation generation, approvals, rejections, model/prompt versions, and
  administrative actions.
- Make imports idempotent and traceable to their source file and import run. Do not
  silently drop invalid rows, overwrite conflicting values, or delete holdings.
- Treat uploaded Excel, PDF, CAS, AIS, and 26AS files as untrusted. Validate type and
  size, isolate parsing, reject malformed content safely, and avoid logging sensitive content.
- Do not send financial data or PII to third-party AI or analytics services without
  explicit approval and documented data-handling terms.
- Validate all untrusted input at system boundaries and use explicit allowlists where practical.
- Use explicit exception types; never use bare `except` or silently suppress failures.

## AI and Model Guardrails

- Treat model output as untrusted structured input. Validate it with deterministic code
  and a versioned schema before storage or display.
- Enforce allocation totals, permitted asset classes, risk-profile bands, freshness,
  citation validity, and safe fallback behavior outside the model.
- Never fabricate citations. Every displayed citation must resolve to stored source
  material that supports the associated claim.
- Record the model, adapter, prompt, retrieval inputs, rule versions, and generation
  timestamp for reproducibility.
- Keep model and prompt promotion manual and gated by documented evaluation, safety
  checks, and backtesting. Never auto-promote from production feedback.
- Separate offline training/evaluation data from production data. Scrub PII, document
  consent and provenance, and prevent evaluation-set contamination.
- Compare AI-assisted strategies with simple rule-based baselines.
- Do not claim performance from backtests without accounting for leakage, transaction
  costs, slippage, survivorship bias, and limitations of historical simulation.
- Make dataset assumptions, feature definitions, targets, split strategy, evaluation
  windows, random seeds, and model/data versions explicit.
- Fit preprocessing only on training data and test for leakage where relevant.

## Architecture and Engineering Principles

- Prefer the smallest architecture that satisfies approved requirements. Local
  development must not require Kubernetes.
- Keep financial calculations, authorization, validation, and recommendation guardrails
  in deterministic domain services rather than prompts or UI code.
- Separate domain logic from frameworks, persistence, networking, serialization, and UI.
- Use narrow, typed interfaces and dependency injection at external boundaries where it
  materially improves testability.
- Use decimal-safe types for money, units, rates, and percentages; never use binary
  floating point for persisted financial values.
- Define explicit precision, scale, currency, units, and rounding behavior.
- Store timestamps in UTC and retain relevant market/time-zone context. Make Indian
  financial-year boundaries explicit.
- Use database constraints for invariants where practical, including ownership,
  uniqueness, valid transitions, and non-negative quantities where appropriate.
- Make background jobs idempotent, retry-safe, observable, and protected against duplicates.
- Version public APIs and durable event/data contracts when compatibility matters.
- Preserve backward compatibility unless a breaking change is explicitly approved.
- Pin runtime dependencies and model artifacts. Document hardware/runtime compatibility
  for GPU workloads.

## Python Standards

- Follow the Python version and dependency strategy declared by the repository.
- Use explicit type hints for function signatures, public attributes, and non-obvious values.
- Avoid `Any`; when unavoidable at an untyped boundary, contain and document it.
- Prefer the standard library when sufficient.
- Use explicit exception types and preserve causal context with exception chaining.
- Make time, randomness, network, filesystem, and other nondeterministic dependencies
  injectable when needed for reliable tests.
- Do not add a dependency without explaining its purpose and maintenance, security,
  licensing, and deployment implications.

## Logging and Observability

- Use standard `logging` unless the repository already standardizes on another framework.
- Create module loggers with `logging.getLogger(__name__)`.
- Libraries must not configure the root logger or install global handlers. Applications
  should configure logging once at their entry point.
- Log meaningful lifecycle events, external calls, retries, state transitions, and failures
  at appropriate levels.
- Prefer queryable context through `extra` where compatible with project conventions.
- Preserve useful exception context using `logger.exception(...)` or `exc_info=True`.
- Avoid noisy logs in tight loops. Never log secrets, PII, financial payloads, uploaded
  document contents, or model prompts containing sensitive data.
- Define metrics, traces, correlation identifiers, and alerting expectations for critical
  imports, calculations, jobs, external calls, and recommendation workflows.

## Testing Standards

- Use the repository's configured framework; for a new Python project, prefer pytest.
- Add tests for every meaningful new or changed behavior, including expected behavior,
  boundaries, failure paths, and regression cases.
- Prefer behavior-focused tests over tests coupled to private implementation details.
- Unit-test deterministic domain logic. Add integration, contract, migration, and end-to-end
  tests at important boundaries in proportion to risk.
- Mock only external boundaries such as network, filesystem, clock, randomness, and
  third-party services. Do not mock the implementation under test.
- Tests must be deterministic and independent of order, live services, local timezone,
  uncontrolled time, and uncontrolled randomness.
- Test financial logic with fixed examples and boundary cases for each applicable financial
  year and asset type. Use independently calculated expected results for critical formulas.
- Test tenant isolation, authorization failures, import idempotency, duplicate jobs,
  malformed uploads, recommendation validation, approval transitions, and audit completeness.
- Do not delete, weaken, skip, or rewrite valid tests merely to make a change pass.
- Do not reduce configured coverage thresholds without explicit approval.
- Treat coverage as a diagnostic and enforcement floor, not a substitute for meaningful tests.

## Quality and Security Gates

- Use tools already configured in the repository.
- For a new Python project without established tooling, prefer:
  - Ruff for formatting and linting;
  - mypy or Pyright for static type checking;
  - pytest with coverage.py for testing and coverage;
  - Bandit for Python source security analysis;
  - pip-audit for dependency vulnerability scanning;
  - pre-commit for fast local validation;
  - Hadolint for Dockerfile linting;
  - Trivy for filesystem and container scanning;
  - Gitleaks or detect-secrets for secret detection.
- Do not disable a lint, type, test, coverage, or security rule merely to obtain a
  passing result. Fix the cause or add the narrowest justified suppression.
- Keep local and CI commands aligned. Pin or lock dependencies with the repository's
  selected strategy.
- CI must be deterministic and must fail when an enforced gate is violated.
- Run relevant formatting, linting, typing, tests, migration checks, contract validation,
  security analysis, and dependency scanning after implementation changes.

## Containers and Configuration

- Keep images minimal, reproducible, and suitable for non-root execution.
- Use multi-stage builds when they materially reduce runtime size or attack surface.
- Never bake credentials, secrets, production data, or environment-specific values into images.
- Use the repository's typed configuration or environment mechanism.
- Add health checks and graceful shutdown for long-running services when relevant.
- Pin base images according to project policy and scan final images when tooling exists.

## Design Documentation Standards

- Each finalized design must state scope, assumptions, decisions, alternatives, data
  ownership, trust boundaries, failure modes, security/privacy impact, observability,
  testing strategy, rollout/rollback considerations, and unresolved questions.
- Use consistent terminology and identifiers across product specifications, LLDs,
  database schemas, APIs, events, and UI flows.
- Mark uncertain or unverified claims explicitly. Retain an `Open Questions` section
  until material decisions are resolved.
- Use Mermaid or simple text diagrams only when they clarify component, data, trust,
  or state-transition relationships.
- Use UTF-8 for all text files.
- Update documentation, examples, configuration templates, and contracts whenever
  behavior or interfaces change.
- Add docstrings to public APIs and non-obvious domain logic; avoid redundant docstrings.
- Record material architectural decisions through the existing design/ADR process.

## Collaboration and Agents

- The primary Codex agent owns integration and the final response.
- Use sub-agents only when the project owner explicitly requests delegation or parallel work.
- If requested, give each sub-agent a bounded, non-overlapping task. All agents must
  follow this file, preserve shared-workspace changes, and report assumptions and findings
  to the primary agent.

## Approval Boundaries

Obtain explicit project-owner approval before:

- expanding the product into trade execution or regulated personalized advice;
- adopting a paid service, restrictive data license, or architecture with material cost;
- sending sensitive data to an external service;
- changing an approved public contract, core financial calculation, compliance control,
  or security boundary;
- deleting or irreversibly migrating user data;
- deploying to a shared or production environment;
- weakening authentication, authorization, encryption, auditing, testing, human approval,
  tenant isolation, or other security controls; or
- modifying a finalized design decision with material product or operational impact.

## Definition of Done

A design is not final while material compliance, data-ownership, authorization,
calculation, security, privacy, failure-handling, or rollout questions remain unresolved.

An implementation change is complete only when:

- approved requirements and acceptance criteria are satisfied;
- requirements, design decisions, implementation, and tests remain traceable;
- relevant tests have been added or updated and pass;
- configured formatting, linting, static typing, migration, contract, security, and
  dependency checks pass;
- documentation, examples, schemas, and configuration templates are updated where needed;
- compatibility, migration, rollback, and operational implications are addressed;
- the final diff contains no unrelated changes; and
- residual financial, data-quality, compliance, security, and operational risks are reported.

Run the repository's complete configured validation command before handoff when practical.
If no aggregate command exists, run each applicable configured gate individually.

Never claim a check passed unless it was executed successfully. If a check cannot run,
state exactly what was not run, why, and the command that should be executed later.

## Final Handoff

Report concisely:

- the outcome and high-level structure of the change;
- materially changed files;
- requirements or design decisions affected;
- tests and quality gates executed, including results;
- assumptions made; and
- unresolved risks, limitations, or follow-up work.

Do not provide lengthy line-by-line explanations unless requested.
