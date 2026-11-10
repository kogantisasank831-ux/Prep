---
layout: "week"
status: "approved"
version: "1.0.0"
last_reviewed: "2026-11-10"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "AI security, privacy, and governance interview cheat sheet"
description: "Threat modeling, prompt injection, RAG and agent security, privacy, supply chain, red teaming, governance, regulation, release gates, and incidents."
summary: "Revise deterministic security boundaries around probabilistic models, impact-based assurance, privacy engineering, lifecycle governance, and recovery."
permalink: "/interview-prep/cheat-sheets/ai-security-privacy-governance/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 6 · Security, privacy, and governance"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 6 source:** This page integrates the prepared revision artifact into the Prep site. It is separate from the Week 1–20 learning assessments.

**Target roles:** AI Engineer, Agentic AI Engineer, ML Engineer, AI Security Engineer, Senior Data Scientist, AI/Data Science Lead  
**Use:** security design, threat modeling, red-team, governance, responsible-AI, architecture, and leadership rounds  
**Interview rule:** a model is an untrusted probabilistic component, not an authorization engine. Enforce security invariants in deterministic systems around it.

## 1. Thirty-second revision

- Bind the exact application, model/runtime, prompts, retrieval corpus/index, tools, identities, tenants, data classes, deployment, and external effects before discussing controls.
- Threat-model trust boundaries and business impact; do not treat an OWASP list or scanner as the complete model.
- Direct and indirect prompt injection are delivery mechanisms. The security question is whether untrusted content can cause unauthorized reading, disclosure, execution, or state change.
- Keep identity, authorization, secrets, tenant context, and policy outside model-controlled text.
- Treat user input, retrieved documents, tool results, memory, peer-agent messages, and model output as untrusted.
- Apply least privilege, scoped credentials, allowlists, schema plus semantic validation, sandbox/egress controls, approval, idempotency, and reconciliation at action boundaries.
- For RAG, authorize before retrieval and generation; retain source/ACL lineage; test poisoning, revoked data, and cross-tenant isolation.
- Red-team with synthetic canaries and deterministic impact oracles. A refusal message is not proof that no action occurred.
- Minimize sensitive data across prompts, traces, caches, evaluation datasets, fine-tuning, and logs; define retention and deletion propagation.
- Governance needs inventory, accountable owners, risk classification, documented evidence, evaluation, approval, monitoring, incident response, and retirement—not a one-time checklist.

## 2. Security model for AI applications

Separate four layers:

1. **Ordinary application security:** identity, authorization, injection, SSRF, secrets, tenancy, supply chain, encryption, logging, rate limits, recovery.
2. **AI component behavior:** prompt following, uncertainty, unsafe/misleading output, model extraction or evasion.
3. **AI data plane:** prompts, exemplars, retrieval content, embeddings, memory, feedback, training/evaluation data, adapters.
4. **Agent/action plane:** tools, connectors, credentials, approvals, operation ledger, external side effects.

AI-specific controls do not replace secure software engineering. A perfectly aligned model behind a broken authorization check is still insecure.

## 3. Threat-model method

For each system, identify:

- **assets:** sensitive data, secrets, model weights, prompts, indexes, tools, money, reputation, decisions;
- **actors:** users, administrators, developers, data publishers, tenants, external attackers, compromised dependencies;
- **entry points:** chat/API, uploaded files, URLs, email, OCR/images, retrieval, tools, memory, inter-agent messages, feedback, training pipeline;
- **trust boundaries:** user-to-app, app-to-model, app-to-retriever, model-to-tool, tenant-to-shared platform, CI-to-artifact, service-to-provider;
- **security properties:** confidentiality, integrity, availability, authorization, provenance, safety, privacy, non-repudiation;
- **impact evidence:** data read, cross-tenant result, tool call, privilege change, network destination, filesystem/database record, cost/budget, unsafe business outcome;
- **authority:** test environment, accounts, rate/cost cap, exclusions, abort condition, incident contact.

Use a data-flow diagram and enumerate where text becomes code, a query, a URL, a rendered page, a permission-bearing request, or an irreversible action.

## 4. Core GenAI and agent threats

| Threat | What fails | Durable control boundary |
|---|---|---|
| Direct prompt injection | user text attempts to change application behavior | constrain capability; deterministic auth/policy; validate effects |
| Indirect prompt injection | document/tool/web content influences the model | provenance, content isolation, least privilege, approval, sandbox |
| Sensitive information disclosure | secrets/PII/internal data enter output or logs | minimization, ACL, redaction/DLP, output policy, logging controls |
| Supply-chain compromise | model, adapter, tokenizer, code, image, dataset, plugin is malicious/changed | provenance, signatures/digests, scanning, isolated evaluation, pinning |
| Data/model poisoning | training, feedback, retrieval, or memory corrupts behavior | trusted ingestion, review, anomaly checks, versioning, quarantine, rollback |
| Improper output handling | generated content reaches SQL/shell/HTML/code/template/tool sink | typed parsing, allowlists, escaping, sandbox, downstream authorization |
| Excessive agency | agent has more functionality, permissions, or autonomy than needed | scoped tools/credentials, budgets, approval, terminal-state controls |
| System-prompt/config leakage | hidden instructions or internal policy are exposed | do not place secrets there; minimize; treat disclosure as possible |
| Vector/retrieval weakness | unauthorized, stale, poisoned, or misleading context is retrieved | pre-retrieval ACL, metadata integrity, lineage, revocation, eval |
| Misinformation/overreliance | plausible output drives a bad decision | grounding, uncertainty, verification, human oversight, domain controls |
| Unbounded consumption | tokens, recursion, fan-out, modalities, or tools exhaust resources | quotas, admission, deadlines, bounded loops, cancellation, cost alerts |

Use the current OWASP GenAI/LLM catalog to seed scenarios, then add application-specific threats and ordinary web/cloud risks.

## 5. Prompt injection: the correct interview answer

Prompt injection cannot be solved by one stronger system prompt. Natural-language instructions and untrusted data share a channel, and models do not provide a formal privilege boundary.

Design so a successful injection still cannot produce an unauthorized effect:

- keep authenticated principal and tenant context in trusted application state;
- select tools in code/policy, not from arbitrary model-generated names;
- expose narrow, purpose-built functions instead of general shell/SQL/browser access;
- validate arguments syntactically and semantically;
- reauthorize the exact resource/action at execution time;
- use short-lived, scoped credentials bound to the service/user where possible;
- restrict network, filesystem, and process access;
- require explicit approval for high-impact or irreversible effects;
- use an operation ledger, idempotency keys, budgets, and reconciliation;
- separate untrusted content and retain provenance for review;
- monitor blocked and attempted actions without logging sensitive payloads.

Input classifiers, delimiters, prompt hierarchy, guard models, and content filters are useful defense in depth. They are not authorization boundaries.

## 6. RAG security

### Threats

- malicious instructions in documents, metadata, OCR, or linked content;
- corpus poisoning and authority spoofing;
- cross-tenant or revoked-document retrieval;
- embedding/ranking manipulation;
- stale ACLs, deletions, or retention rules;
- citation laundering: a citation exists but does not support the claim;
- document exfiltration through repeated queries;
- secrets or PII copied into embeddings, caches, traces, or evaluation sets.

### Controls

1. authenticate and authorize source ingestion;
2. validate file type/content, parse in isolation, scan and quarantine;
3. attach immutable source, tenant, ACL, version, and retention metadata;
4. enforce current authorization before candidate retrieval/assembly;
5. preserve chunk-to-source lineage and permission-aware caches;
6. treat retrieved text as evidence, not higher-priority instruction;
7. limit quotation/extraction and detect suspicious enumeration where appropriate;
8. validate citations and answer support;
9. propagate update, deletion, and revocation to derived indexes/caches;
10. red-team with synthetic protected documents and cross-tenant canaries.

A grounded answer can still be grounded in poisoned or unauthorized content. Evaluate authorization, source integrity, retrieval, generation, and citation separately.

## 7. Agent and tool security

For every tool define:

- caller identity and delegated user identity;
- allowed operations, resources, domains, and data classes;
- typed request/response schema and semantic constraints;
- read versus write versus irreversible effect;
- idempotency and duplicate/replay behavior;
- timeout, retry, cancellation, and budget;
- approval rule and approver identity;
- audit fields and reconciliation source of truth;
- credential scope, rotation, and revocation;
- sandbox, network egress, filesystem, and process boundaries.

Important attack paths include tool-name/argument manipulation, confused deputy, SSRF, hidden side effects, approval ambiguity, replay, memory poisoning, compromised connectors, malicious peer agents, loop amplification, and partial failure after an external effect.

The application must decide whether an action is allowed. The model may propose an action; it must not grant itself permission.

## 8. Insecure output handling

Generated output becomes dangerous when another system interprets it.

| Sink | Required controls |
|---|---|
| HTML/Markdown/UI | context-aware encoding, safe renderer, URL policy, CSP where applicable |
| SQL | parameterization, query builder/allowlist, read/write role, row/tenant authorization |
| Shell/code | avoid where possible; sandbox, allowlist, resource/network/filesystem limits |
| File path | canonicalize, allowed root, extension/type validation, no traversal |
| URL/HTTP | scheme/domain/IP allowlist, DNS/redirect checks, egress proxy, response limits |
| Tool/API | typed schema, semantic validation, reauthorization, idempotency, approval |
| Logs | structured fields, escaping, redaction, cardinality/size bounds |

Structured output makes parsing easier; it does not prove the requested action is safe or authorized.

## 9. Privacy engineering

Build a data inventory covering input, prompt, output, retrieval content, embeddings, memory, feedback, traces, caches, fine-tuning, evaluation, and provider telemetry.

Apply:

- purpose limitation and data minimization;
- lawful/organizational basis and consent where applicable;
- classification, residency, retention, and deletion policy;
- encryption in transit/at rest and controlled key access;
- tenant/user authorization and least privilege;
- redaction/tokenization/pseudonymization where useful;
- log/trace sampling and field-level suppression;
- provider contract and training/retention settings review;
- access/export/correction/deletion workflows;
- privacy-safe test data and synthetic canaries;
- incident response for disclosure.

### Privacy-enhancing techniques

| Technique | Benefit | Limit |
|---|---|---|
| Pseudonymization/tokenization | reduces direct identifiers | linkage or reidentification may remain |
| Differential privacy | bounds individual contribution under a declared privacy budget | utility/complexity trade-off; implementation matters |
| Federated learning | moves training toward data sources | updates can leak; coordination and heterogeneity remain |
| Secure aggregation/MPC | limits visibility of individual inputs/updates | compute/operational complexity |
| Confidential computing | protects data in use within a hardware trust model | does not fix application logic or output disclosure |

Never claim “anonymous” without an explicit threat model and reidentification assessment.

## 10. Model, data, and software supply chain

Record immutable identities and provenance for:

- source code, dependency lock, build workflow, container digest;
- base model, weights, tokenizer, config, license/usage terms;
- adapters/checkpoints and training code;
- training, evaluation, prompt, and retrieval datasets;
- prompt templates, tools, policies, guardrails, indexes;
- runtime/compiler/driver/CUDA and serving engine;
- evaluator/judge versions and scenario set.

Controls include trusted registries, checksums/signatures where available, SBOM/model BOM, license and vulnerability review, malware/unsafe-format scanning, restricted deserialization, isolated evaluation, access controls, change approval, and rollback.

Avoid loading arbitrary pickled/model artifacts in a privileged environment. A known model name does not prove the bytes or tokenizer are trusted.

## 11. Resource and denial-of-wallet controls

Bound:

- input bytes/tokens and attachment count/size;
- context and output tokens;
- requests, concurrency, queue time, and retries;
- retrieval candidates and document expansion;
- tool calls, branches, agent steps, and wall-clock deadline;
- recursive/delegated work;
- image/audio/video resolution and duration;
- code runtime, CPU, memory, disk, processes, and network;
- per-user/tenant/project/provider spend.

Add admission control, fair quotas, cancellation, backpressure, circuit breakers, degraded modes, and anomaly alerts. Security testing must stop at approved caps rather than create uncontrolled load or spend.

## 12. Red-team campaign design

Each test scenario needs an impact-based oracle:

```python
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Outcome(str, Enum):
    BLOCKED = "blocked"
    ATTEMPTED = "attempted"
    COMMITTED = "committed"


@dataclass(frozen=True)
class SecurityScenario:
    scenario_id: str
    entry_point: str
    expected_control: str
    forbidden_effect: str
    synthetic_canary: str

    def validate(self) -> None:
        if not all(
            (
                self.scenario_id,
                self.entry_point,
                self.expected_control,
                self.forbidden_effect,
                self.synthetic_canary,
            )
        ):
            raise ValueError("scenario fields must be non-empty")


scenario = SecurityScenario(
    scenario_id="rag-cross-tenant-001",
    entry_point="retrieved document",
    expected_control="tenant authorization before retrieval",
    forbidden_effect="protected canary returned to another tenant",
    synthetic_canary="CANARY-TENANT-A",
)
scenario.validate()
assert Outcome.COMMITTED.value == "committed"
```

Record threat, prerequisite, delivery channel, benign test transformation, expected control, deterministic evidence, severity, cleanup, owner, and exact candidate identity.

Use isolated accounts and synthetic data. Distinguish:

1. attack delivered;
2. model produced unsafe text;
3. application attempted an action;
4. control blocked the action;
5. external effect committed.

For subjective content-safety labels, calibrate human/evaluator agreement and report false positives. For authorization, data access, tool effects, destinations, records, and budgets, prefer deterministic assertions.

## 13. Security testing tools: what they are for

| Tool/family | Useful for | It does not replace |
|---|---|---|
| Microsoft PyRIT | extensible automated/human-led red-team orchestration and scoring | application-specific impact oracles and authorization tests |
| NVIDIA garak | probing/scanning LLM targets for known weakness classes | a complete system threat model |
| promptfoo | configurable LLM/app evaluation and red-team regression | deterministic backend state assertions |
| NeMo Guardrails | programmable runtime rails and guardrail integrations | identity, authorization, sandboxing, and secure code |
| Microsoft Presidio | PII detection/anonymization components | data inventory, policy, consent, and deletion |
| Giskard/DeepEval/Ragas/custom suites | behavioral/evaluation cases | security ownership and manual investigation |
| OPA/Cedar/custom policy service | deterministic policy decisions | correct resource model and enforcement at every sink |
| Semgrep/CodeQL, Trivy/Grype, Syft | code/container/dependency and SBOM workflows | AI-specific adversarial testing |

Pin versions and review licenses, telemetry, provider calls, data handling, and evaluator dependencies. Scanner output is a finding to reproduce, not automatic proof of exploitability or safety.

## 14. Governance operating model

Governance should answer who can approve, change, deploy, monitor, and retire an AI system.

### Minimum lifecycle evidence

- inventory and accountable owner;
- intended use, users, excluded use, and system boundary;
- risk tier/classification and applicable policy/jurisdiction;
- data/model/prompt/index/tool lineage;
- evaluation sets, thresholds, limitations, and slice analysis;
- security/privacy threat model and tests;
- human oversight, appeal/escalation, and fallback;
- release approval, version, rollout, rollback, and exceptions;
- production monitoring, feedback governance, incidents, and change triggers;
- retention, deletion, audit, and retirement.

### Framework map

- **NIST AI RMF:** voluntary risk-management structure commonly summarized as Govern, Map, Measure, and Manage.
- **NIST AI 600-1:** GenAI profile that adapts risk-management actions to generative AI.
- **OWASP GenAI/LLM risks:** application-security scenario seed catalog.
- **MITRE ATLAS:** living knowledge base of adversarial tactics and techniques for AI systems.
- **ISO/IEC 42001:** AI management-system standard; organizational certification and process scope differ from a product security test.
- **ISO/IEC 23894:** AI risk-management guidance.
- **EU AI Act and sector rules:** determine role, system category, jurisdiction, and applicable date with qualified legal/compliance owners.

Framework mapping is evidence organization, not compliance by association. A company using an OWASP checklist or NIST vocabulary is not automatically secure or compliant.

## 15. Regulatory interview answer

Do not memorize one universal rule. Say:

1. determine jurisdiction and sector;
2. identify whether the organization is provider, deployer, importer, distributor, or another regulated actor;
3. classify the system/use and prohibited or high-impact context;
4. map applicable dates and obligations from current official text;
5. implement technical and organizational evidence: risk management, data governance, documentation, logging/traceability, transparency, human oversight, accuracy/robustness/cybersecurity, monitoring, and incident response;
6. involve legal, privacy, security, model-risk, and domain owners;
7. preserve change control because a material change may alter the assessment.

As of this guide’s publication, the EU implementation timeline has changed through later legislation and differs across GPAI, transparency, high-risk use cases, and regulated products. Verify the current European Commission pages rather than relying on an old slide.

## 16. Release gates and incident response

Before promotion, require the accepted subset of:

- ordinary application/security tests;
- data/model/prompt/index/tool provenance checks;
- impact-based direct/indirect injection cases;
- tenant/ACL and secret/PII leakage tests;
- output-sink validation and sandbox/egress tests;
- agent permission, approval, replay, loop, and budget tests;
- RAG poisoning/revocation/citation tests;
- load/resource-abuse tests at safe caps;
- quality, latency, cost, and false-positive regression checks;
- rollback/kill-switch and recovery rehearsal.

Incident response may require disabling a tool/connector, rotating credentials, quarantining a corpus/model/prompt, containing a tenant, blocking a provider/model revision, preserving evidence, notifying owners, rebuilding derived stores, and reconciling external actions.

## 17. Common weak answers

- “We hide the system prompt.” Hidden prompts can leak and must not contain secrets.
- “The LLM checks whether the user is allowed.” The backend must authorize.
- “We use JSON schema, so tool calls are safe.” Schema does not validate intent, permission, resource, or business policy.
- “We sanitize all prompts.” Natural language has no general-purpose sanitizer that proves injection resistance.
- “The model refused, so the attack failed.” Check attempted and committed effects.
- “The vector database filter protects tenants.” Verify trusted tenant binding, current ACLs, cache/index keys, and adversarial tests.
- “A red-team tool passed, so the system is secure.” Coverage is finite and version/workflow-specific.
- “We are NIST/OWASP compliant.” These resources have different purposes; accountable owners determine controls and evidence.

## 18. Rapid interview questions

**Prompt injection versus jailbreak?**  
Prompt injection changes application behavior through untrusted instructions; a jailbreak commonly tries to bypass model behavior/content restrictions. They can overlap, but system impact depends on capabilities and controls.

**Why is a system prompt not a security boundary?**  
It is model context, not deterministic access control, and may be influenced or disclosed.

**Where should authorization happen in RAG?**  
Before retrieval/assembly using trusted identity and current resource permissions, then again before any external action.

**Guardrails versus policy engine?**  
Guardrails can classify or transform content and orchestrate checks. A policy engine/backend enforces deterministic permissions and business rules.

**What is an impact oracle?**  
An observable assertion such as a protected canary read, unauthorized record, tool effect, network destination, or exceeded budget—not a model’s explanation.

**How do you test indirect injection safely?**  
Use controlled documents/tool outputs, isolated identities, synthetic secrets, bounded tools, explicit caps, and external-state assertions.

**What must be logged?**  
Enough identity, policy, release, operation, and outcome metadata to investigate and reconcile, while redacting sensitive payloads and controlling retention.

**Who accepts residual AI risk?**  
The accountable business/security/risk owner, with documented scope, rationale, expiry, and compensating controls—not the model or scanner.

## 19. Lead-level case: procurement document agent

Design an agent that reads supplier documents, retrieves policy, drafts recommendations, and can create a procurement action after approval.

A strong answer covers:

1. **Boundary:** users, tenants, document/data classes, allowed decisions, prohibited autonomy, external action and approval.
2. **Ingestion:** authenticated source, isolated parser, malware/type checks, prompt-injection/poisoning review, metadata/ACL lineage, quarantine.
3. **Retrieval:** user/tenant-bound authorization before search, permission-aware cache, source/citation support, revocation/deletion propagation.
4. **Model:** no secrets in prompts, untrusted context separation, bounded output, uncertainty/abstention, provider data settings.
5. **Tools:** narrow APIs, scoped credentials, typed and semantic validation, reauthorization, idempotency, approval token, operation ledger.
6. **Security tests:** cross-tenant canaries, malicious documents, tool-result injection, SSRF/egress, replay, approval confusion, budget exhaustion.
7. **Privacy/governance:** inventory, retention, minimization, audit, human oversight, appeal, release evidence, risk owner.
8. **Operations:** denied-action and ACL alerts, kill switch, credential rotation, corpus quarantine, rollback, reconciliation and incident runbook.

State which invariants are enforced outside the model and how you prove an unauthorized purchase cannot commit.

## 20. Final checklist

- [ ] I can bind assets, identities, tenants, data, models, tools, and trust boundaries.
- [ ] I distinguish model text, attempted action, blocked action, and committed impact.
- [ ] I can defend against direct/indirect injection without relying on a prompt alone.
- [ ] I understand RAG poisoning, ACL, revocation, lineage, citation, and exfiltration risks.
- [ ] I can design least-privilege agent tools with approval, idempotency, and reconciliation.
- [ ] I protect sensitive data across prompts, traces, caches, indexes, training, and evaluation.
- [ ] I can plan bounded red-team cases with synthetic canaries and deterministic oracles.
- [ ] I know what PyRIT, garak, promptfoo, NeMo Guardrails, and Presidio do and do not prove.
- [ ] I can map lifecycle evidence to NIST, OWASP, MITRE, ISO, and applicable regulation without claiming automatic compliance.
- [ ] I include release gates, monitoring, containment, recovery, and a residual-risk owner.

## 21. Primary references

- OWASP GenAI Security Project, [Top 10 for LLM and GenAI](https://genai.owasp.org/llm-top-10/)
- NIST, [AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- NIST AI 600-1, [Generative AI Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence)
- MITRE, [ATLAS](https://atlas.mitre.org/)
- European Commission, [AI Act policy and implementation timeline](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)
- Microsoft, [PyRIT documentation](https://microsoft.github.io/PyRIT/)
- NVIDIA, [garak](https://github.com/NVIDIA/garak)
- promptfoo, [Red-team documentation](https://www.promptfoo.dev/docs/red-team/quickstart/)
- NVIDIA, [NeMo Guardrails documentation](https://docs.nvidia.com/nemo/guardrails/)
- Microsoft, [Presidio documentation](https://microsoft.github.io/presidio/)

Standards, laws, model behavior, tools, and attack methods change. Recheck the current official source and test the exact deployed candidate.
