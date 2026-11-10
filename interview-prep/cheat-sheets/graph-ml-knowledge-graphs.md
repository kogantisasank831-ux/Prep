---
layout: "week"
status: "review"
version: "0.1.0"
last_reviewed: "2026-11-10"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "Graph ML and knowledge graphs interview cheat sheet"
description: "Graph contracts, message passing, node and link tasks, temporal splits, negative sampling, heterogeneous graphs, knowledge graphs, GraphRAG, serving, security, and privacy."
summary: "Revise graph learning from typed time-valid structure and leakage-safe evaluation through scalable GNNs, knowledge evidence, production operations, and access control."
permalink: "/interview-prep/cheat-sheets/graph-ml-knowledge-graphs/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 9 · Graph ML and knowledge graphs"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 9 scope:** This review candidate derives from the approved master index and the cited primary documentation. It is separate from the Week 1–20 learning assessments.

**Target roles:** Data Scientist, Applied Scientist, ML Engineer, AI Engineer, Graph/Knowledge Engineer, AI/Data Science Lead  
**Use:** fraud, recommendation, search, entity resolution, link prediction, knowledge graphs, GraphRAG, system design, and research interviews  
**Interview rule:** define nodes, edges, direction, time, relation semantics, allowable neighborhoods, and the prediction unit before selecting a graph embedding, GNN, knowledge-graph model, or graph retrieval layer.

## 1. Thirty-second revision

- A graph is $G=(V,E)$ with nodes, edges, optional features, types, directions, timestamps, and weights.
- Use a graph when relationships add decision signal or constraints; do not convert ordinary tabular data into a graph without a relational hypothesis.
- Start with degree, recency, common-neighbor, path, and tabular baselines before a GNN.
- Node classification, edge/link prediction, graph classification, ranking, community detection, and graph retrieval need different splits and metrics.
- Random edge splitting can leak future links, reverse edges, duplicated relations, or information through the remaining neighborhood.
- Message passing aggregates neighbor representations, combines them with the current node, and repeats for a bounded number of layers.
- More layers can cause oversmoothing, oversquashing, greater cost, and larger leakage/security blast radius.
- GraphSAGE-style sampling supports inductive large-graph training; full-neighborhood aggregation may be infeasible.
- Heterogeneous graphs preserve node and relation types; relation-specific transformations need enough support and careful parameter sharing.
- Knowledge graphs store typed entities and relations; graph embeddings score triples but do not establish truth.
- GraphRAG should prove that graph traversal improves evidence retrieval versus simpler lexical/vector baselines.
- Production needs graph snapshot identity, point-in-time features, incremental updates, deletion/ACL propagation, embedding/index freshness, and fallback.

## 2. Define the graph contract

Record:

- node types, stable IDs, attributes, owners, and lifecycle;
- edge types, direction, multiplicity, timestamp, validity interval, provenance, and weight;
- whether missing edges mean negative, unknown, unobserved, or not yet created;
- prediction unit and decision time;
- neighborhood information available at that time;
- target, label maturation, action, and cost;
- inductive requirement for unseen nodes/graphs;
- privacy, tenant, deletion, and access boundaries.

Example:

> At transaction authorization time, score the new transaction node using account, merchant, device, and prior-edge evidence available before the request; do not use investigation outcomes or future chargebacks.

Graph construction is part of the model. Changing identity resolution, edge windows, direction, or deduplication changes the learning problem.

## 3. Core graph concepts

- **Degree:** number of incident edges; use in/out degree for directed graphs.
- **Path and shortest path:** a sequence of connected nodes; meaning depends on edge semantics and weights.
- **Connected component:** maximal connected subgraph.
- **Centrality:** degree, betweenness, closeness, PageRank-like measures; each encodes a different importance concept.
- **Homophily:** connected nodes tend to share labels/features.
- **Heterophily:** useful edges may connect different labels; vanilla smoothing assumptions can fail.
- **Community:** densely connected group under a chosen objective; not automatically a real-world category.
- **Bipartite graph:** edges connect two node sets, such as users and items.
- **Heterogeneous graph:** multiple node and/or edge types.
- **Dynamic/temporal graph:** topology or features change with time.

Sparse adjacency storage is usually required. Distinguish structural edges from trainable or predicted links and retain relation/time provenance.

## 4. Task families and baselines

| Task | Unit | Baselines | Useful metrics |
|---|---|---|---|
| Node classification | node | node features, degree, neighbor-label aggregates | macro F1, PR-AUC, calibration by slice |
| Link prediction | candidate pair | popularity, common neighbors, Adamic-Adar, matrix factorization | MRR, Hits@K, Recall@K, calibrated probability |
| Edge classification | observed edge | edge features + endpoint features | F1/PR-AUC, cost-weighted utility |
| Graph classification | whole graph | aggregate counts, fingerprints, pooled tabular model | macro F1/AUC, calibration |
| Node/graph regression | node/graph | tabular regression on engineered aggregates | MAE/RMSE, calibration/intervals |
| Ranking/recommendation | ordered candidates | popularity, co-visitation, matrix factorization | Recall@K, NDCG, coverage, online outcome |
| Community/anomaly | node/subgraph | connected components, degree/rule baselines | stability, scarce-label utility, alert cost |

Graph models should beat a baseline that already has fair access to useful node, edge, and aggregate features.

## 5. Message passing

A generic layer computes:

$$
m_i^{(k)}=\operatorname{AGG}^{(k)}\left(\left\{\phi^{(k)}(h_i^{(k-1)},h_j^{(k-1)},e_{ji}) : j\in\mathcal{N}(i)\right\}\right)
$$

$$
h_i^{(k)}=\psi^{(k)}\left(h_i^{(k-1)},m_i^{(k)}\right)
$$

where $h_i$ is a node representation, $e_{ji}$ optional edge information, and aggregation must be permutation invariant for unordered neighbors.

Know the intuition:

- **GCN:** normalized neighborhood smoothing with shared transformation;
- **GraphSAGE:** samples/aggregates neighbors and can generalize inductively using features;
- **GAT:** learns attention weights over neighbors, but weights are not automatically faithful explanations;
- **GIN:** expressive sum aggregation for graph-level tasks under stated assumptions;
- **R-GCN/heterogeneous layers:** relation-specific message transformations;
- **temporal GNNs:** incorporate event order, memory, or time encoding.

After $k$ layers, a node receives information from up to $k$ hops, subject to sampling and connectivity. Depth is a modeling and security decision, not just a hyperparameter.

## 6. Oversmoothing, oversquashing, and scale

- **Oversmoothing:** node representations become too similar after repeated aggregation.
- **Oversquashing:** exponentially growing distant information is compressed through fixed-size representations and graph bottlenecks.
- **Neighbor explosion:** high degree makes full aggregation expensive.

Mitigations include shallow architectures, residual/skip connections, normalization, sampling, attention or gating, positional/structural encodings, graph rewiring under a valid semantic contract, and task-specific subgraphs. Validate rather than assuming a named method solves the failure.

For scale, choose among full-batch, neighbor sampling, cluster/subgraph batching, temporal sampling, distributed partitioning, and offline embeddings. Report sampling fan-out, seed-node distribution, effective neighborhood, bias/variance, memory, throughput, and reproducibility.

## 7. Split and leakage design

### Node tasks

Transductive evaluation allows the test graph structure during training while hiding test labels. Inductive evaluation holds out new nodes or graphs. State which one matches production.

### Link prediction

Avoid:

- placing one direction of an undirected relation in train and the reverse in test;
- sampling negatives that become positives later or were impossible/unknown;
- leaving the target edge in message-passing adjacency;
- using features or paths created after the prediction time;
- selecting candidates with future knowledge;
- reporting sampled-negative ranking as full-corpus ranking without disclosure.

Use temporal cutoffs when links arrive over time. Build features and neighborhoods as of each origin and evaluate realistic candidate generation separately from scoring.

### Entity and graph identity

If multiple nodes or graphs derive from one customer, device, document, molecule scaffold, or event, group them appropriately. Identity resolution itself can leak labels or create false edges.

## 8. Link prediction and negative sampling

An embedding model often scores a pair or triple. For dot-product link prediction:

$$
s(u,v)=z_u^\top z_v
$$

Training may contrast observed edges with sampled non-edges. But a non-edge may mean unobserved, not negative.

Define:

- eligible pair universe;
- positive timestamp and label policy;
- random, degree-aware, in-batch, local, or hard-negative sampling;
- false-negative handling;
- correction/weighting when sample and serving distributions differ;
- evaluation against a representative or full candidate set.

Hard negatives can improve discrimination but can amplify label uncertainty and leakage if mined from future or target-derived evidence.

## 9. Heterogeneous and temporal graphs

For heterogeneous graphs, keep node/edge type semantics explicit. A user–buys→item relation should not silently share all parameters with user–reports→item. Options include relation-specific layers, basis decomposition, shared encoders with relation embeddings, and meta-path features.

For temporal graphs:

- distinguish event time, processing time, and availability time;
- sample only historical neighbors;
- version mutable node attributes;
- represent edge expiry and correction;
- evaluate across multiple temporal origins;
- handle new nodes, dormant nodes, and changing degree.

A static snapshot may be a valid baseline, but it must not contain future structure.

## 10. Knowledge graphs

A knowledge graph represents triples $(head, relation, tail)$ plus provenance and optional qualifiers. Interview topics:

- ontology/schema and relation direction;
- entity resolution and canonical IDs;
- open-world versus closed-world assumptions;
- provenance, confidence, validity intervals, and contradictions;
- rules/path queries versus embeddings;
- triple scoring models such as translational, bilinear, or complex embeddings;
- filtered ranking evaluation and negative construction;
- updates, deletion, ACLs, and auditability.

Embedding similarity or a high triple score proposes a relation; it does not make the relation an accepted fact. Preserve source evidence and confidence.

## 11. Graph retrieval and GraphRAG

A graph-assisted retrieval system may:

1. resolve entities from the query;
2. retrieve authorized seed nodes/documents;
3. traverse typed, bounded, time-valid edges;
4. score/prune subgraphs or paths;
5. combine graph evidence with lexical/vector retrieval;
6. assemble provenance-rich context;
7. generate or return structured evidence with citations.

Evaluate entity linking, seed recall, path/subgraph recall, evidence precision, answer groundedness, latency, token/cost, and authorization violations separately.

GraphRAG is justified when relationships, multi-hop evidence, global structure, or controlled traversal add value. Compare against vector-only, lexical, metadata filter, and simple SQL/graph-query baselines. A graph can increase noise and cost when extraction or entity resolution is weak.

## 12. Evaluation and uncertainty

Report:

- exact graph snapshot, feature/label time, node/edge schema, code, seed, and model;
- realistic candidate universe and negative policy;
- overall and slice metrics by degree, age, type, community, geography/site where relevant, and cold start;
- confidence intervals accounting for dependence where feasible;
- calibration and threshold utility;
- ablations: node features only, structure only, simple aggregates, and graph model;
- sensitivity to edge removal, sampling, identity-resolution errors, and stale data;
- serving cost, latency, memory, and freshness.

Edges make observations dependent. A naive row-level bootstrap or random split can overstate certainty.

## 13. Production architecture

Separate:

- canonical entity/edge store with provenance and validity;
- graph snapshot or streaming update pipeline;
- point-in-time feature generation;
- training sampler and model artifacts;
- batch embedding/index publication;
- online subgraph/feature retrieval;
- inference/ranking service;
- ACL/deletion propagation and audit;
- quality, freshness, drift, latency, and outcome monitoring.

Use immutable snapshot/manifests and atomic promotion. Define how late edges, entity merges/splits, reprocessing, revoked access, and deletion affect derived features, embeddings, indexes, caches, and training sets.

Fallback may use tabular features, popularity/rules, cached embeddings within a freshness limit, or safe abstention. Stale graph evidence should not silently become current truth.

## 14. Security and privacy

- Graph neighborhoods can reveal sensitive associations even when node attributes are hidden.
- Authorization must apply during seed retrieval and traversal, not only after context assembly.
- Multi-hop expansion needs depth, fan-out, cost, and tenant boundaries.
- Prevent untrusted extracted entities/edges from becoming trusted graph facts without validation.
- Propagate deletion and revocation through aggregates, embeddings, indexes, training data, caches, and generated summaries.
- Audit entity resolution, relation provenance, model/snapshot versions, and returned paths.
- Consider membership, link-inference, poisoning, sybil, and graph-extraction risks under the accepted threat model.

## 15. Minimal neighborhood aggregation example

```python
from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable


def mean_neighbor_value(
    edges: Iterable[tuple[str, str]],
    values: dict[str, float],
) -> dict[str, float]:
    neighbors: dict[str, list[float]] = defaultdict(list)
    for source, target in edges:
        if source in values:
            neighbors[target].append(values[source])
    return {
        node: sum(items) / len(items)
        for node, items in neighbors.items()
        if items
    }
```

This is a deterministic one-hop baseline. A production version needs direction/type/time rules, missing-value policy, access control, incremental behavior, and leakage-safe feature origins.

## 16. Common failure modes

- Using a graph because it is fashionable, without proving relational lift.
- Randomly splitting future edges or connected identities.
- Leaving target edges in the training adjacency.
- Treating every missing edge as a negative.
- Comparing sampled-candidate metrics with full-corpus metrics.
- Ignoring degree/popularity shortcuts and cold-start slices.
- Adding layers until oversmoothing or neighbor explosion appears.
- Using attention weights as complete explanations.
- Building a knowledge graph without provenance or validity intervals.
- Letting entity resolution merge distinct people/accounts.
- Traversing unauthorized or deleted nodes in GraphRAG.
- Updating embeddings without atomically updating the serving index and version.

## 17. Rapid interview questions

**When should you use a GNN?** When relational structure adds validated signal and the graph can be constructed point-in-time with acceptable scale, privacy, and operational cost.

**What is message passing?** A permutation-invariant aggregation of neighbor messages followed by an update of each node representation.

**Transductive versus inductive?** Transductive evaluation can use the known graph containing test nodes without their labels; inductive evaluation must generalize to unseen nodes or graphs.

**Why is link-prediction splitting hard?** Edges are time-dependent and non-independent; reverse links, future neighborhoods, target edges, and unrealistic negatives can leak.

**What is oversmoothing?** Repeated aggregation makes node representations less distinguishable; depth and mitigation must be validated for the task.

**When does GraphRAG help?** When verified relationships or bounded multi-hop evidence improve retrieval/grounding beyond simpler baselines under acceptable latency and security.

## 18. Design case: fraud graph

For a real-time fraud graph, cover:

1. transaction, account, merchant, device, address, and investigation identities;
2. typed/directed/time-valid edges and entity-resolution uncertainty;
3. authorization-time cutoff and delayed chargeback labels;
4. rule, tabular, aggregate, and graph baselines;
5. temporal splits, target-edge removal, negative/candidate policy;
6. sampling, feature/embedding freshness, online lookup, latency, fallback;
7. calibration and thresholds under investigation capacity;
8. degree/new-entity/site/fraud-pattern slices and graph-drift monitoring;
9. poisoning/sybil, privacy, deletion, provenance, and audit controls;
10. shadow/canary release, investigator feedback, rollback, and retrospective evaluation.

## 19. Interview checklist

- [ ] I can define a graph schema, prediction unit, time boundary, and missing-edge meaning.
- [ ] I can explain message passing, sampling, oversmoothing, heterogeneity, and temporal graphs.
- [ ] I can design leakage-safe node and link evaluation with realistic negatives.
- [ ] I can compare tabular/aggregate baselines with GNN evidence.
- [ ] I can explain knowledge-graph provenance and GraphRAG evaluation.
- [ ] I can design snapshot identity, incremental updates, ACL/deletion propagation, serving, monitoring, and fallback.

## References

- PyTorch Geometric, [Documentation](https://pytorch-geometric.readthedocs.io/en/latest/)
- PyTorch Geometric, [Creating Message Passing Networks](https://pytorch-geometric.readthedocs.io/en/latest/notes/create_gnn.html)
- PyTorch Geometric, [Heterogeneous Graph Learning](https://pytorch-geometric.readthedocs.io/en/latest/notes/heterogeneous.html)
- Kipf and Welling, [Semi-Supervised Classification with Graph Convolutional Networks](https://arxiv.org/abs/1609.02907)
- Hamilton, Ying, and Leskovec, [Inductive Representation Learning on Large Graphs](https://arxiv.org/abs/1706.02216)

Graph libraries and operators evolve. Pin the graph construction, snapshot, sampler, model, candidate policy, evaluation protocol, and runtime used for every claim.
