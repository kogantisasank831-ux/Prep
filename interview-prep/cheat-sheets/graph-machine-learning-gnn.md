---
layout: "week"
status: "approved"
version: "1.0.0"
last_reviewed: "2026-11-11"
imported_on: "2026-11-13"
source_repository: "kogantisasank831-ux/transformer-explainer"
source_commit: "cdd45b6b0c08c5d88a626e4d16853abdf285f08d"
source_path: "AI_Data_Science_Interview_Cheat_Sheets/Batch_9_Specialized_Modeling/34_Graph_Machine_Learning_GNN_Interview_Cheat_Sheet.md"
header_context: "Interview cheat sheets"
back_label: "Cheat sheets"
back_url: "/cheat-sheets/"
toc_heading: "Cheat-sheet sections"
pagination_label: "Cheat sheets hub"
pagination_url: "/cheat-sheets/"
title: "Graph machine learning and GNN interview cheat sheet"
description: "Interview revision for graph construction, graph algorithms, GNN architectures, evaluation, scaling, and production operations."
summary: "Revise graph contracts, structural baselines, message passing, GCN, GraphSAGE, GAT, GIN, evaluation, scaling, and production failure modes."
permalink: "/interview-prep/cheat-sheets/graph-machine-learning-gnn/"
kicker_primary: "Interview revision"
kicker_secondary: "Batch 9 · Graph ML"
current_label: "Revision guide"
alternate_label: "Cheat sheets hub"
alternate_url: "/cheat-sheets/"
---

**Target roles:** AI Engineer, ML Engineer, Applied Scientist, Senior Data Scientist, Recommendation/Fraud Engineer, Data Science Lead<br>
**Use:** graph modeling, GNN theory, recommendations, fraud, knowledge graphs, molecular ML, evaluation, and system-design interviews<br>
**Interview rule:** define nodes, edges, direction, time, prediction unit, and information available at scoring time before choosing a GNN. Graph construction is part of the model; a leaked or causally invalid edge can dominate any architecture.

## 1. Thirty-second revision

- A graph is `G=(V,E)` with nodes, edges, optional direction, types, features, timestamps, and weights.
- Graph tasks include node classification/regression, link prediction, edge classification, graph classification/regression, clustering/community detection, ranking, and generation.
- Always establish non-neural baselines: node/edge features, degrees, common neighbors, PageRank, shortest paths, matrix factorization, and gradient-boosted trees.
- Message-passing GNNs update each node from its current state and a permutation-invariant aggregation of neighbor messages.
- GCN normalizes and mixes neighbor features; GraphSAGE learns an inductive aggregator; GAT learns attention weights; GIN is designed for strong graph-structure expressiveness under its assumptions.
- One GNN layer usually propagates one hop. More layers expand receptive field but increase oversmoothing, oversquashing, sampling cost, and leakage risk.
- Transductive learning predicts within a known graph; inductive learning must generalize to unseen nodes or graphs using transferable features/functions.
- Graph splits must reflect deployment. Random edge splits can leak future links, duplicate reverse edges, shared identities, or message paths.
- Link prediction needs careful negative sampling and filtered evaluation. Missing edges are not automatically true negatives.
- Large graphs require neighbor/subgraph sampling, partitioning, mini-batching, caching, or layer-wise inference; sampled training and full-graph serving can differ.
- Heterogeneous graphs have node/edge types; temporal graphs have event time and state evolution. Collapsing types/time can destroy meaning or leak the future.
- Monitor graph schema, degree/edge-type distribution, connected components, feature freshness, embedding drift, new-node coverage, and online outcomes.

## 2. Define the graph contract

Write:

> At **decision time T**, construct graph **G** from entities and relationships available by T, predict **target Y** for **unit U**, and trigger **action A**, subject to **latency, freshness, privacy, and harm constraints C**.

Specify:

- node types and stable identifiers;
- edge semantics, direction, weight, timestamp, expiry, and source;
- whether absence means negative, unknown, or not observed;
- node/edge/graph features and availability time;
- prediction unit: node, pair, edge, subgraph, or whole graph;
- dynamic update cadence and deletion;
- training/inference graph boundary;
- new-node/new-edge behavior;
- allowed message paths and tenant/privacy boundaries.

Example: “user viewed item” is directional and time-stamped; “users share a device” may be undirected but sensitive; “paper cites paper” is directed and should not include future citations for a historical prediction.

## 3. Graph representation and terminology

### Core objects

- adjacency matrix `A ∈ R^(|V|×|V|)`;
- node-feature matrix `X ∈ R^(|V|×d)`;
- edge list/COO representation `edge_index ∈ N^(2×|E|)`;
- degree `d_i`;
- neighborhood `N(i)`;
- graph Laplacian `L=D−A` or normalized variants.

Sparse representations are essential because real graphs usually have far fewer than `|V|²` edges.

### Graph properties

| Property | Question |
|---|---|
| directed | does `u→v` imply `v→u`? |
| weighted | does edge strength/count/distance matter? |
| heterogeneous | are there multiple node and relation types? |
| temporal | when did an edge exist, and for how long? |
| multigraph | can the same pair have multiple relations/events? |
| connectedness | are there isolated nodes or components? |
| homophily | do connected nodes tend to share labels/features? |

Symmetrizing, removing multi-edges, or ignoring timestamps is a modeling decision that must be justified.

## 4. Strong non-GNN baselines

### Structural features

- in/out degree and weighted degree;
- common neighbors;
- Jaccard coefficient;
- Adamic-Adar;
- preferential attachment;
- shortest-path distance;
- triangles/clustering coefficient;
- PageRank or centrality;
- community membership;
- motif counts.

Combine structural features with node/edge attributes in logistic regression, boosted trees, or ranking models.

### Embedding baselines

- matrix factorization;
- spectral embeddings;
- random-walk methods such as DeepWalk/node2vec;
- knowledge-graph embeddings such as TransE-style models;
- learned two-tower embeddings.

GNNs should demonstrate incremental value over these baselines under the same split, candidate set, and latency.

## 5. Message passing

A general layer:

`m_i^(l) = AGGREGATE({φ(h_i^(l), h_j^(l), e_ji) : j∈N(i)})`

`h_i^(l+1) = γ(h_i^(l), m_i^(l))`

The aggregation must be permutation invariant for unordered neighbors, commonly sum, mean, max, or attention-weighted sum.

After `L` layers, a node normally depends on an `L`-hop neighborhood. Graph-level tasks add a permutation-invariant readout/pooling over nodes.

Key design choices:

- self-loops;
- direction and reverse relations;
- normalization by degree;
- edge features;
- aggregation;
- residual/skip connections;
- normalization/dropout;
- readout;
- depth and sampling.

## 6. Common GNN architectures

### GCN

A simplified normalized update:

`H^(l+1) = σ(D_hat^(-1/2) A_hat D_hat^(-1/2) H^(l) W^(l))`

where `A_hat=A+I`. It mixes normalized neighbor/self features, then transforms them. Good baseline for homophilous graphs; full-batch form can be expensive.

### GraphSAGE

Aggregates sampled neighbor states and combines them with the node state. The shared aggregator supports inductive inference for unseen nodes with features. Neighbor sampling controls scale but introduces variance and may miss important neighbors.

### GAT

Learns attention weights over neighbors. Attention can differentiate neighbor importance, but it adds computation and does not automatically provide faithful explanation or solve noisy edges.

### GIN

Uses sum aggregation and an MLP update designed to match the distinguishing power of the Weisfeiler-Lehman graph isomorphism test under conditions. It is common for graph-level tasks, but expressiveness does not guarantee generalization.

### Relational and heterogeneous GNNs

Use relation-specific transformations/aggregators or type-aware attention. Parameter count and sparse relation coverage become concerns. A schema-level graph helps define permitted paths.

### Graph transformers

Global or sparse attention can model long-range interactions with structural/positional encodings. Full pairwise attention is expensive; graph bias, sampling, and positional choices are decisive.

## 7. Minimal dependency-free example: mean message passing

```python
from __future__ import annotations

from collections.abc import Mapping, Sequence


def mean_neighbor_aggregate(
    features: Mapping[str, Sequence[float]],
    adjacency: Mapping[str, Sequence[str]],
) -> dict[str, list[float]]:
    """Aggregate each node's own vector and its listed neighbors by mean."""
    if not features:
        raise ValueError("features must not be empty")
    width = len(next(iter(features.values())))
    if width == 0 or any(len(vector) != width for vector in features.values()):
        raise ValueError("feature vectors must share a nonzero width")

    output: dict[str, list[float]] = {}
    for node, vector in features.items():
        neighbors = adjacency.get(node, [])
        unknown = [neighbor for neighbor in neighbors if neighbor not in features]
        if unknown:
            raise ValueError(f"unknown neighbors for {node}: {unknown}")
        vectors = [vector, *(features[neighbor] for neighbor in neighbors)]
        output[node] = [
            sum(values) / len(vectors)
            for values in zip(*vectors, strict=True)
        ]
    return output


node_features = {"a": [1.0, 0.0], "b": [0.0, 1.0], "c": [1.0, 1.0]}
edges = {"a": ["b"], "b": ["a", "c"], "c": ["b"]}
aggregated = mean_neighbor_aggregate(node_features, edges)
assert aggregated["a"] == [0.5, 0.5]
assert aggregated["b"] == [2 / 3, 2 / 3]
assert aggregated["c"] == [0.5, 1.0]
```

Real GNN layers add trainable transformations, batching, edge direction/type, normalization, and gradient-based learning.

## 8. Task-specific modeling

### Node prediction

Examples: fraud-account risk, product category, churn, paper topic. Decide whether labels and graph are known for all nodes at training time.

- transductive: evaluation nodes exist in the training graph, though labels are withheld;
- inductive: evaluation nodes or entire graphs are unseen.

Do not claim inductive generalization from a transductive random-node split.

### Link prediction

Score candidate pair `(u,v)` using:

- dot product or cosine;
- bilinear/relation-specific score;
- MLP on endpoint embeddings/features;
- subgraph/path model.

Challenges:

- candidate generation at scale;
- missing-not-at-random edges;
- negative sampling;
- temporal leakage;
- symmetric/reverse duplicates;
- new nodes;
- filtered ranking when other known positives exist.

Metrics include Hits@K, MRR, Recall@K, precision-recall, calibration, and business outcomes. Define the candidate universe; sampled negatives can inflate metrics.

### Edge and graph prediction

Edge classification uses endpoint, relation, and context. Graph prediction pools node/edge states for molecules, transactions, or programs. Batch graphs with correct component boundaries and preserve graph-level splits/scaffolds where domain requires.

### Graph anomaly/fraud

Anomalies may be unusual nodes, edges, subgraphs, or coordinated temporal patterns. Labels are selective and adversaries adapt. Combine rules, graph features, GNN scores, investigation capacity, and incident-level evaluation.

## 9. Splits, negative sampling, and leakage

### Split strategies

| Deployment claim | Suitable test evidence |
|---|---|
| future edges/nodes | chronological split with past-only graph |
| new users/items | inductive node holdout |
| new molecules/scaffolds | scaffold/domain group split |
| new geographic network | component/site holdout |
| same static graph, unknown labels | transductive mask with controlled message paths |

Leakage examples:

- target edge left in adjacency while predicting it;
- reverse edge or duplicated relation remains;
- future interactions construct historical features;
- labels/features propagate through message passing from unavailable nodes;
- train/test users share a household/device entity that reveals outcome;
- negative becomes positive later.

### Negative sampling

Uniform random non-edges are often too easy. Consider:

- degree-aware or popularity-aware negatives;
- hard negatives from retrieval;
- time-valid negatives;
- relation/type-valid negatives;
- adversarial negatives with safeguards.

Do not sample a known positive as negative. Missing edges may be unobserved positives, so interpret supervised labels carefully.

## 10. Scaling graph learning

### Why full-batch fails

Memory stores node features, edges, activations, optimizer state, and gradients. An `L`-layer neighborhood can grow exponentially with degree.

Approaches:

- neighbor sampling around seed nodes;
- cluster/partition-based mini-batches;
- subgraph sampling such as GraphSAINT-style methods;
- layer-wise sampling;
- distributed graph storage/training;
- feature/embedding caches;
- offline precomputation;
- shallow GNN plus scalable retrieval/ranker.

Sampling details are part of the model:

- fanout per layer/type;
- replacement;
- direction/subgraph type;
- seed-node loss only;
- inclusion probability and bias;
- train versus inference sampling.

For link prediction, sample neighborhoods around both endpoints without reintroducing the target edge.

### Inference

- full-graph layer-wise embedding refresh;
- incremental update for changed nodes/edges;
- online neighborhood sampling;
- precomputed embeddings plus online features;
- fallback for isolated/new nodes.

State embedding staleness and graph-refresh SLA. Avoid mixing embeddings from incompatible model and graph versions.

## 11. Failure modes and debugging

### Oversmoothing

Repeated neighbor mixing makes node representations less distinguishable. Symptoms include declining performance with depth and low embedding variance. Mitigations include shallow depth, residual/jumping connections, normalization, personalized propagation, edge dropout, or architecture changes—validated empirically.

### Oversquashing

Information from exponentially many distant nodes is compressed through fixed-size messages/bottlenecks. Long-range tasks suffer. Rewiring, positional/global features, attention, larger state, or hierarchical models may help.

### Heterophily

Connected nodes may have different labels, so naive smoothing hurts. Use ego/self features, relation/direction-aware models, signed/compatibility models, higher-order patterns, or non-GNN baselines.

### Other failures

- high-degree hubs dominate;
- isolated nodes lack messages;
- neighbor sampler omits rare signal;
- type imbalance starves relation parameters;
- dynamic graph becomes stale;
- attention interpreted as causal explanation;
- graph construction captures sensitive proxies;
- embedding IDs shift after reindexing.

Debug with tiny graphs, manual message calculations, degree/edge-type slices, feature ablations, shuffled-edge controls, gradient checks, seed repeats, and baseline comparisons.

## 12. Temporal and heterogeneous graphs

### Temporal graphs

Edges/events have timestamps; node state evolves. Decide:

- discrete snapshots versus event stream;
- valid event ordering;
- memory/state update before or after prediction;
- temporal negative sampling;
- expiration;
- delayed labels.

Never let a future edge influence an earlier prediction. Evaluate rolling horizons and cold-start periods.

### Heterogeneous graphs

Represent node types and edge triplets such as `(user, buys, product)`. Type-specific features can have different dimensions. Use relation-aware message passing, metapaths, or separate encoders.

### Knowledge graphs

Knowledge-graph completion scores subject-relation-object triples. Entity/relation embeddings, rule/path methods, GNNs, and text encoders can be combined.

GraphRAG is primarily a retrieval/organization approach for LLM context; it is not synonymous with GNN training. A knowledge graph can support both.

## 13. Evaluation and release evidence

Evaluate:

- task metric and calibration;
- node degree, edge type, community, component, and new-node slices;
- temporal stability and future holdout;
- hard-negative/candidate-set behavior;
- fairness and sensitive proxy effects;
- robustness to missing/noisy/adversarial edges;
- repeated seeds and sampling variance;
- memory, throughput, p95 latency, refresh time, and storage;
- comparison to non-graph and structural baselines.

For online systems, test downstream conversion, fraud loss, investigation yield, or scientific utility. An offline link metric is not causal product evidence.

Artifact identity includes graph snapshot/query, node/edge schemas, ID mapping, features, negative sampler, split, model, sampler, seed, library/runtime, and inference graph version.

## 14. Production architecture and monitoring

Typical flow:

`events/tables → graph builder → validated snapshot/store → training/sampling → registry → batch/online embeddings → scorer/ranker → action and feedback`

Controls:

- idempotent graph construction;
- point-in-time joins;
- tenant/authorization boundary;
- deletion propagation;
- stable ID mapping and schema version;
- model-graph compatibility checks;
- sampling determinism where required;
- fallback feature-only model;
- staged rollout and rollback.

Monitor:

- node/edge counts by type;
- degree and component distributions;
- orphan/new-node rate;
- graph/feature freshness;
- sampler fanout and truncation;
- embedding norm/similarity/drift;
- score and candidate distributions;
- slice performance and delayed outcomes;
- online cache/storage latency and failures.

## 15. Library map

| Tool | Best fit | Verify |
|---|---|---|
| NetworkX | analysis, algorithms, small graph prototypes | not a large-scale GNN engine |
| PyTorch Geometric | PyTorch message passing, sampling, heterogeneous graphs | data flow direction, loader semantics, optional dependencies |
| DGL | graph neural networks and distributed tooling | backend/version support and sampler behavior |
| OGB | standardized graph datasets/splits/evaluators | dataset task, metric, license, contamination |
| Neo4j/graph databases | graph storage/query and feature extraction | not automatically a GNN trainer |
| RAPIDS cuGraph | GPU graph analytics and integrations | hardware/memory and supported algorithms |
| GraphLearn-for-PyTorch/production samplers | large-scale sampling | integration maturity and graph update contract |

Pin versions. Equivalent layer names can normalize, direct edges, add self-loops, and aggregate differently.

## 16. Rapid interview questions

**Why use a graph?**<br>
The relationship structure contains predictive or decision-relevant information that independent rows lose.

**What is message passing?**<br>
Each node aggregates permutation-invariant messages from neighbors and updates its representation with shared learnable functions.

**GCN versus GraphSAGE?**<br>
GCN performs normalized neighborhood mixing; GraphSAGE explicitly learns aggregators and is commonly used with sampling for inductive settings.

**Does GAT attention explain a decision?**<br>
Not necessarily. Attention weights are model mechanics and may be unstable or insufficient as faithful explanations.

**Why are random edge splits risky?**<br>
They can retain future/reverse/duplicate relationships and make train and test neighborhoods unrealistically similar.

**What is oversmoothing?**<br>
Repeated aggregation makes node embeddings increasingly alike, reducing discriminative information.

**What is oversquashing?**<br>
Too much distant information is compressed through limited message capacity or graph bottlenecks.

**How do you handle a new node?**<br>
Use inductive features/aggregators, a cold-start model, and a defined fallback until enough edges arrive.

**Why is negative sampling important?**<br>
It defines the learning/evaluation contrast. Easy or invalid negatives produce misleading performance.

**How do you scale a GNN?**<br>
Use sampling/partitioning, sparse operations, caches/distribution, shallow architectures, and batch embedding refresh, validated for train-serving parity.

## 17. Lead-level case: coordinated procurement fraud

Answer in this order:

1. Define fraud event, decision/action, monetary/time window, review capacity, and harm of false accusation.
2. Create point-in-time node types—supplier, employee, bank account, address, device, purchase order—and typed temporal edges.
3. Threat-model identity errors, shared legitimate infrastructure, privacy, tenant boundaries, and adversarial adaptation.
4. Establish rules and tabular/structural-feature boosted-tree baselines.
5. Split chronologically and by investigation/identity groups; keep future and target edges out of message paths.
6. Compare heterogeneous GNN/link/subgraph models only if they add value at review capacity.
7. Evaluate incident-level recall, precision at K, loss prevented, lead time, degree/community/new-supplier slices, calibration, and stability.
8. Explain alerts with verifiable paths/features rather than treating attention as proof.
9. Design daily graph snapshots or streaming updates, stable IDs, deletion, embedding freshness, queue backpressure, human adjudication, and feedback auditing.
10. Shadow/canary, retain rules/tabular fallback, monitor adversarial drift and reviewer bias, and preserve appeal/rollback.

## 18. Final checklist

- [ ] I define nodes, edges, direction, type, time, prediction unit, and action.
- [ ] I compare GNNs with structural, tabular, factorization, and random-walk baselines.
- [ ] I can derive the message-passing update and explain GCN, GraphSAGE, GAT, and GIN.
- [ ] I distinguish node, edge/link, and graph tasks.
- [ ] I design temporal/inductive/component-aware splits and valid negatives.
- [ ] I prevent target-edge, reverse-edge, future, identity, and message-path leakage.
- [ ] I understand sampling, neighbor explosion, layer depth, and inference refresh.
- [ ] I diagnose oversmoothing, oversquashing, heterophily, hubs, and isolated nodes.
- [ ] I version graph construction, ID maps, samplers, features, model, and embeddings.
- [ ] I design privacy boundaries, monitoring, fallback, rollout, and rollback.

## 19. Primary references

- [PyTorch Geometric documentation](https://pytorch-geometric.readthedocs.io/en/latest/)
- [PyG MessagePassing API](https://pytorch-geometric.readthedocs.io/en/stable/generated/torch_geometric.nn.conv.MessagePassing.html)
- [PyG neighbor-sampling tutorial](https://pytorch-geometric.readthedocs.io/en/latest/tutorial/neighbor_loader.html)
- [PyG heterogeneous-graph tutorial](https://pytorch-geometric.readthedocs.io/en/latest/notes/heterogeneous.html)
- [Deep Graph Library documentation](https://www.dgl.ai/pages/start.html)
- [Open Graph Benchmark](https://ogb.stanford.edu/)
- [Kipf and Welling, Semi-Supervised Classification with Graph Convolutional Networks](https://openreview.net/forum?id=SJU4ayYgl)
- [Hamilton, Ying, and Leskovec, Inductive Representation Learning on Large Graphs](https://proceedings.neurips.cc/paper/2017/hash/5dd9db5e033da9c6fb5ba837a7ebea9-Abstract.html)
- [Veličković et al., Graph Attention Networks](https://openreview.net/forum?id=rJXMpikCZ)
- [Xu et al., How Powerful are Graph Neural Networks?](https://openreview.net/forum?id=ryGs6iA5Km)
- [Gilmer et al., Neural Message Passing for Quantum Chemistry](https://proceedings.mlr.press/v70/gilmer17a.html)
