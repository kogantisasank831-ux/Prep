# Week 23 GenAI system-design review contracts — revision 1

Source: `Path.md` Week 23. This lab supplies six synthetic interview cases and
a transparent structural rubric. It checks whether an answer is defensible; it
does not use an LLM to declare an architecture correct.

| ID | Effective rule and acceptance |
| --- | --- |
| W23-BR1 | Structure every answer in this order: requirements, metrics, data, architecture, retrieval/tools, model, evaluation, deployment, monitoring, security, cost and failure. |
| W23-BR2 | Keep the business goal and explicit constraints ahead of vendor or framework choices. |
| W23-FR1 | Score each dimension 0–4: one point each for a substantive decision, evidence, trade-off and failure control. The score is fully inspectable. |
| W23-FR2 | Require at least 36/48, no critical dimension below 3, at least one declared assumption and at least one rejected alternative before a mock-interview readiness gate can pass. |
| W23-FR3 | Treat requirements, evaluation, security, cost and failure as critical dimensions. A polished component diagram cannot compensate for one of those gaps. |
| W23-FR4 | Preserve the difference between missing evidence and an incorrect decision. This deterministic reviewer checks the former only. |
| W23-DR1 | Provide six cases covering RAG, a consequential agent, a live copilot, multimodal documents, a local-model gateway and agent evaluation. |
| W23-SR1 | Require trust boundaries, least privilege, tenant isolation and failure containment to appear in the answer; do not treat a model prompt as a security boundary. |
| W23-NFR1 | Identical typed proposals produce identical ordered reviews with no network, model, clock or random source. |
| W23-ER1 | Test case coverage, strict contracts, duplicate dimensions, partial scoring, critical gates, assumption/alternative gates, stable order and all CLI paths. |

## Why the rubric is structural

Semantic architecture review depends on workload measurements, regulatory
context, organizational constraints and details that a short fixture cannot
prove. Keyword scoring would reward jargon. This lab therefore asks a narrower,
useful question: has the candidate stated a decision, supporting evidence, a
trade-off and a failure control for every required dimension?

A human reviewer must still challenge feasibility, consistency, calculations,
threats, operational ownership and whether the evidence would actually validate
the stated goal.

## Accepted limitations

- Case traffic, data, latency and compliance constraints are synthetic.
- The rubric does not validate capacity arithmetic, semantic quality, security
  effectiveness, cost estimates or technology compatibility.
- Twelve short sections are a practice scaffold, not a mandatory production
  design-document format.
- A readiness pass means “ready to defend in a mock interview,” not “approved to
  build or release.”
