# Interview preparation Batch 7 review record

## Approval

- Decision: approved for merge and publication on 2026-11-10.
- Approved scope: four revision guides covering mathematical foundations and optimization, experimentation and causal inference, data preparation and feature engineering, and unsupervised learning and anomaly detection, plus twenty new questions per role bank.
- Authority: explicit repository-owner approval in the Batch 7 review conversation.
- Merge gate: the approval state must pass the content, navigation, regression, and PostgreSQL/pgvector integration jobs.

## Documentation set

- Audience: AI Engineer, Agentic AI Engineer, Data Science Technical Lead, and Senior Data Scientist candidates with basic statistics, ML, and production-system foundations.
- Task: revise core mathematical, causal, data, feature, clustering, and anomaly concepts, then practise role-specific decisions, derivations, diagnostics, and operational evidence.
- Scope: four revision guides plus twenty new questions per role bank.
- Environment: GitHub Pages Markdown backed by repository CI.
- Sensitivity: public instructional content; no credentials, personal data, client-identifying details, or internal systems.
- Owner and review trigger: repository owner; review after source, formula, causal assumption, role question, navigation, publishing contract, or role-scope changes.

## Canonical sources

- `25_Linear_Algebra_Calculus_Optimization_Cheat_Sheet.md`;
- `26_Experimentation_Causal_Inference_Cheat_Sheet.md`;
- `27_Data_Preparation_EDA_Feature_Engineering_Cheat_Sheet.md`;
- `28_Unsupervised_Learning_Anomaly_Detection_Cheat_Sheet.md`.

The candidate pages preserve each prepared instructional body apart from removing its duplicate top-level heading and adding Jekyll metadata plus a Batch 7 source note.

## Role-bank extension

| Role | Approved Batches 1–6 | Approved Batch 7 | Approved total |
| --- | ---: | ---: | ---: |
| Agentic AI Engineer | 120 | 20 | 140 |
| Data Science Technical Lead | 120 | 20 | 140 |
| Senior Data Scientist | 120 | 20 | 140 |

Each role uses the same four topic blocks but changes the decision boundary: implementation and production debugging for AI engineering, standards and operating models for technical leadership, and derivation, identification, validation, and interpretation for senior data science.

## Accuracy and validation contract

- Batch 1–6 IDs and question content remain present and ordered;
- each role adds exactly `B7-01` through `B7-20` with unique IDs;
- every new question has three strong-answer signals, one follow-up probe, and direct revision links;
- source bodies retain their rapid-revision sections and exact prepared instructional content;
- all Batch 7 public pages, expanded role banks, and navigation use `status: approved`;
- formulas, shapes, causal assumptions, time/identity boundaries, clustering geometry, anomaly thresholds, and evidence limitations are explicit;
- unique permalinks, complete hub links, Markdown structure, linting, tests, and repository integration checks are merge gates.

## Evidence boundary and handoff

Automated checks establish source fidelity and repository consistency, not interview-market completeness, psychometric calibration, reader comprehension, causal validity for a particular business, or production fitness of any named method. The questions are guided practice prompts rather than authenticated exams. A cold-reader exercise remains future evidence. Post-merge publication verification remains required.
