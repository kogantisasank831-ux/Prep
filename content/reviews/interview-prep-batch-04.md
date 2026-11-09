# Interview preparation Batch 4 review record

## Approval

- Decision: approved for merge and publication on 2026-11-10.
- Approved scope: four agent-focused revision guides and twenty new questions per role bank.
- Authority: explicit repository-owner approval in the Batch 4 review conversation.
- Merge gate: the approval candidate must pass the content, navigation, regression, and PostgreSQL/pgvector integration jobs.

## Documentation set

- Audience: AI Engineer, Agentic AI Engineer, Data Science Technical Lead, and Senior Data Scientist candidates with foundational ML, LLM, and RAG knowledge.
- Task: revise agent systems quickly and practise role-specific design, implementation, evaluation, reliability, and leadership answers.
- Scope: four revision guides plus twenty new questions per role bank.
- Environment: GitHub Pages Markdown backed by repository CI.
- Sensitivity: public instructional content; no credentials, personal data, or internal systems.
- Owner and review trigger: repository owner; review after source, question, navigation, framework-version, protocol, or publishing-contract changes.

## Canonical sources

- `13_Agent_Fundamentals_Workflow_Patterns_Cheat_Sheet.md`;
- `14_LangGraph_Deep_Dive_Interview_Cheat_Sheet.md`;
- `15_Agent_Frameworks_Libraries_Comparison_Cheat_Sheet.md`;
- `16_Agent_Protocols_Reliability_Evaluation_Cheat_Sheet.md`.

The instructional bodies are unchanged apart from removing each duplicate top-level heading and adding Jekyll metadata plus a Batch 4 source note.

## Role-bank extension

| Role | Approved Batches 1–3 | New Batch 4 | Approved total |
| --- | ---: | ---: | ---: |
| Agentic AI Engineer | 60 | 20 | 80 |
| Data Science Technical Lead | 60 | 20 | 80 |
| Senior Data Scientist | 60 | 20 | 80 |

Batch 4 separates engineering, technical-lead, and data-science perspectives across agent patterns, LangGraph, framework choices, protocols, reliability, security, and evaluation.

## Accuracy and validation contract

- Batch 1–3 IDs and question content remain present and ordered;
- each role adds exactly `B4-01` through `B4-20` with unique IDs;
- every new question has three strong-answer signals, one follow-up probe, and direct revision links;
- source bodies retain their rapid-revision sections and exact instructional content;
- all Batch 4 public pages and expanded role banks use `status: approved` after human approval;
- unique permalinks, complete hub links, Markdown structure, linting, tests, and repository integration checks are merge gates.

## Evidence boundary and handoff

Automated checks establish repository consistency, not interview-market completeness, psychometric calibration, reader comprehension, or framework/API freshness. The questions are guided practice prompts rather than authenticated exams. Post-merge publication verification remains required.
