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
title: "Data and distributed compute engineering interview cheat sheet"
description: "Workload contracts, partitions, shuffles, skew, files and tables, Kafka, streaming semantics, data contracts, distributed training, and backfills."
summary: "Revise execution-boundary choices, distributed data correctness, event-time processing, end-to-end effects, training parallelism, reliability, and cost."
permalink: "/interview-prep/cheat-sheets/data-distributed-compute-engineering/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 6 · Data and distributed compute"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 6 source:** This page integrates the prepared revision artifact into the Prep site. It is separate from the Week 1–20 learning assessments.

**Target roles:** AI Engineer, ML Engineer, Data Engineer, Senior Data Scientist, AI/Data Science Lead  
**Use:** data-platform, distributed-compute, streaming, training-infrastructure, and ML system-design rounds  
**Interview rule:** distributed systems do not remove work; they partition work and add communication, coordination, retries, and partial failure. Start with the workload and correctness contract, then select a tool.

## 1. Thirty-second revision

- Characterize data size, growth, shape, source, arrival pattern, skew, freshness, latency, retention, and replay needs before choosing an engine.
- Prefer the smallest system that meets the requirement: SQL/pandas/Polars/DuckDB on one machine can beat a cluster for many workloads.
- In Spark, reason about partitions, narrow versus wide transformations, stages, shuffles, skew, serialization, spill, and small files—not only API syntax.
- Separate event time from processing time. Define watermarks, late-data policy, state retention, replay, and corrections for streaming.
- Kafka orders records only within a partition. Consumer-group parallelism is bounded by the number of assigned partitions.
- “Exactly once” is an end-to-end property. It depends on replayable input, checkpointed progress, deterministic/idempotent processing, and a transactional or idempotent sink.
- Treat raw data as reproducible evidence, derived tables/features as rebuildable products, and schemas/contracts as versioned interfaces.
- Backfills are production workloads: isolate capacity, pin code/config/data identity, avoid double effects, and reconcile results.
- For distributed training, use data parallelism when the model fits one device, sharding when it does not, and tensor/pipeline parallelism only when required by scale.
- Measure useful throughput, stage time, shuffle/network bytes, spill, skew, checkpoint duration, retries, cost, and output correctness.

## 2. Workload contract

Record distributions and failure behavior, not one average:

| Dimension | Questions |
|---|---|
| Volume | current and forecast bytes/rows/events, file count, daily growth |
| Velocity | batch schedule, steady/bursty event rate, peak-to-average ratio |
| Variety | schemas, nested data, images/audio/documents, change frequency |
| Correctness | duplicates, ordering, missing/late data, update/delete semantics |
| Freshness | source-to-table/feature/index SLO; acceptable staleness |
| Latency | batch completion, per-event delay, interactive query target |
| Replay | source retention, deterministic rebuild, backfill window |
| Security | classification, tenant, residency, access, deletion, audit |
| Operations | owner, retry, quarantine, recovery, capacity, cost ceiling |

Ask whether the output drives analysis, training, online features, retrieval, a financial action, or an irreversible external effect. The stronger the consequence, the stronger the validation and reconciliation contract.

## 3. Choose the execution boundary

| Tool/family | Best fit | Do not choose merely because |
|---|---|---|
| SQL database/warehouse | governed relational analytics and set operations | the data contains tables |
| pandas | local exploration and data that safely fits memory | it is the familiar API |
| Polars | fast single-node columnar/lazy processing; streaming-capable plans | “Rust” automatically means every query is faster |
| DuckDB | embedded analytical SQL over local/remote columnar data | it replaces a transactional multi-user service |
| Spark | large distributed batch/SQL and stateful streaming ecosystem | data is larger than a CSV |
| Dask | Python-native parallel arrays/dataframes and custom workloads | every pandas operation will scale unchanged |
| Ray Data/Core | distributed Python tasks/actors, ML data, training/inference integration | actors remove state-consistency problems |
| Flink | low-latency, stateful event-time streaming | a daily batch job needs a stream processor |
| Kafka | durable partitioned event log and decoupled producers/consumers | it is a processing engine or database replacement |

Benchmark a representative slice. Include startup and coordination overhead, serialization, remote reads, spill, retries, operational complexity, and cost—not only compute time.

## 4. Distributed execution mental model

A logical plan describes **what** to compute. The physical plan decides operators, partitioning, exchanges, algorithms, and placement.

- A **partition/block** is a unit of parallel data work.
- A **task** processes one partition or unit of computation.
- A **stage** is a set of tasks that can run without a global data exchange.
- A **shuffle/exchange** redistributes data, commonly for joins, grouping, sorting, or repartitioning.
- A **driver/coordinator** builds the plan and tracks work; workers/executors run tasks.
- A **straggler** delays completion of the whole stage.
- A **spill** moves intermediate data from memory to disk.

Narrow transformations, such as a row-wise filter, can often process each partition independently. Wide transformations require records with related keys to meet and therefore create network, serialization, disk, and skew costs.

## 5. Partition sizing and parallelism

Too few partitions underuse workers and make each failure expensive. Too many create scheduling overhead and small output files.

For input bytes $B$ and target bytes per partition $P$:

$$
N_{size}=\left\lceil\frac{B}{P}\right\rceil
$$

Also require enough tasks to keep available slots busy. Treat the estimate as a starting point and inspect real task durations, spill, memory, and skew.

```python
from __future__ import annotations

from math import ceil


def target_partitions(
    *,
    total_bytes: int,
    target_partition_mib: int,
    worker_slots: int,
    waves: int = 3,
) -> int:
    """Return a safe initial partition count, not a benchmark substitute."""
    values = (total_bytes, target_partition_mib, worker_slots, waves)
    if any(value <= 0 for value in values):
        raise ValueError("all inputs must be positive")
    by_size = ceil(total_bytes / (target_partition_mib * 1024**2))
    by_parallelism = worker_slots * waves
    return max(by_size, by_parallelism)


assert target_partitions(
    total_bytes=1_000 * 1024**3,
    target_partition_mib=256,
    worker_slots=200,
) == 4_000
```

Partition on columns that enable pruning and distribute work, but avoid very high-cardinality directory trees. Do not partition a lake table by a nearly unique request or customer identifier without a compelling access pattern.

## 6. Skew and hot keys

Skew occurs when some partitions contain much more work than others. Symptoms include a long tail of tasks, high spill on a few workers, uneven network traffic, or one consumer lagging.

Diagnose key-frequency and partition-size distributions. Useful comparisons include maximum/median task time and p99/median records per partition.

Mitigations:

- filter and project before a shuffle;
- broadcast a genuinely small dimension table;
- pre-aggregate locally;
- salt only hot keys and merge afterward;
- isolate exceptional keys;
- use adaptive execution where supported;
- choose a better partition key or increase partitions;
- remove expensive per-row Python/UDF work when native operators exist.

Salting trades one skewed join for extra complexity and a second aggregation. Explain its correctness and cleanup.

## 7. Files, formats, and table layers

- **Parquet/ORC:** columnar storage, compression, statistics, and projection/predicate pruning.
- **CSV/JSON:** interoperable but weakly typed and expensive for repeated analytics.
- **Object storage:** durable, scalable bytes; it does not itself provide table transactions.
- **Lakehouse table formats:** add metadata, snapshots, schema/partition evolution, and transactional table operations over files; compare Delta Lake, Apache Iceberg, and Apache Hudi against the actual platform.
- **Warehouse:** managed query, governance, concurrency, and optimized storage/compute behavior.

Control small files through reasonable write partitioning, compaction, and maintenance. Preserve immutable source evidence where policy permits; publish curated, tested, versioned tables as data products.

## 8. ETL/ELT, idempotency, and backfills

**ETL** transforms before loading to the main analytical target. **ELT** loads source data first and transforms within the target platform. The useful choice depends on governance, engine capability, data movement, latency, and cost.

An idempotent pipeline can repeat the same logical run without creating a different accepted result. Common patterns:

- deterministic business/run keys;
- merge/upsert on stable identifiers;
- write to a staged snapshot and atomically publish a pointer;
- partition overwrite for an explicitly bounded interval;
- deduplicate at a defined trust boundary;
- store run identity, source offsets/snapshots, code/config, and output manifest.

A backfill needs a time range, exact code/config, source snapshot or offsets, isolation/quotas, validation, publication plan, downstream notification, and rollback. Never silently mix historical recomputation with live irreversible actions.

## 9. Kafka fundamentals

- A **topic** is a named event stream split into partitions.
- A partition is an ordered append-only log addressed by offsets.
- A key normally controls partition selection and therefore per-key ordering.
- Replication protects availability/durability subject to broker and acknowledgment configuration.
- Within one consumer group, a partition is assigned to at most one consumer at a time; extra consumers can be idle.
- A rebalance changes assignments and can pause work or expose poor offset/effect handling.

Delivery semantics depend on when input progress is recorded relative to effects:

| Pattern | Failure result |
|---|---|
| commit offset, then process | possible loss; at-most-once behavior |
| process, then commit offset | possible duplicate; at-least-once behavior |
| atomically commit output plus offset | exactly-once within supported transactional boundary |

Kafka idempotent production prevents duplicate log records from producer retries in its supported scope. Transactions can atomically publish records and offsets for Kafka-to-Kafka processing. Writes to an external database/API still need a coordinated transaction, an idempotent sink/outbox, or reconciliation.

## 10. Event time, watermarks, and late data

- **Event time:** when the business event occurred.
- **Processing time:** when the system handled it.
- **Ingestion time:** when it entered a platform.
- **Watermark:** a progress estimate used to decide when state/windows can close.

A watermark is not proof that no earlier event will arrive. Define whether later records are dropped, sent to a side output, used to revise results, or retained for a batch correction.

Stateful streaming requires:

- state key and partitioning;
- state schema/version;
- TTL/retention and cleanup;
- checkpoint/savepoint identity;
- late/duplicate policy;
- replay and sink semantics;
- recovery time and storage cost.

Spark Structured Streaming, Flink, and other engines differ by execution mode, source/sink, and version. Read the exact compatibility and guarantee documentation.

## 11. “Exactly once” interview answer

Say: “Exactly once must be defined at the observable business effect.” Then establish:

1. a replayable source or retained input identity;
2. checkpointed/transactional progress;
3. deterministic transformation or controlled nondeterminism;
4. idempotent/transactional sink using a stable operation key;
5. atomicity between effect and progress, or reconciliation when atomicity is impossible;
6. tests that fail between each boundary.

An engine’s exactly-once state update does not automatically make an email, payment, HTTP call, or arbitrary database write exactly once.

## 12. Data contracts and quality gates

A contract should identify owner, schema, semantics, keys, nullability, units, event time, freshness, allowed evolution, privacy class, retention, and compatibility policy.

Validate:

- schema/type and required fields;
- key uniqueness/deduplication;
- referential and business invariants;
- volume and freshness;
- distribution/range/categories by meaningful slice;
- quarantine behavior;
- point-in-time correctness for ML;
- deletion and access propagation.

Tools such as Great Expectations, Pandera, Deequ, dbt tests, and warehouse constraints can express checks; the team still owns definitions, thresholds, response, and recovery.

## 13. Distributed training

Start with memory and communication:

- **DDP/data parallel:** full model replica on each worker; different mini-batches; gradients synchronized. Use when the model fits one device.
- **FSDP/ZeRO-style sharding:** shard parameters, gradients, and/or optimizer state to reduce per-device memory.
- **Tensor parallel:** split tensor operations across devices; frequent communication and topology sensitivity.
- **Pipeline parallel:** split layers/stages; micro-batches reduce bubbles but complicate scheduling.
- **Sequence/context parallel:** split long-sequence work where supported.

Global batch size is commonly:

$$
B_{global}=B_{device}\times N_{data\ parallel}\times N_{accumulation}
$$

Changing worker count without controlling global batch and optimizer schedule can change training behavior. Track samples/tokens processed, effective batch, learning-rate policy, precision, seeds/determinism limits, data order, checkpoint format, and resharding support.

Collectives such as all-reduce, all-gather, reduce-scatter, and all-to-all have different bandwidth and memory costs. Place communication-heavy groups on fast links, watch stragglers and topology, and test node loss/checkpoint recovery.

## 14. Reliability and observability

Monitor by run, stage, partition, tenant, and data interval:

- input/output counts and bytes;
- freshness/lag and watermark;
- task/stage latency distributions;
- shuffle read/write, network, spill, serialization;
- partition and key skew;
- executor/worker loss, retries, speculative work;
- checkpoint/savepoint duration and failure;
- CPU, memory, disk, GPU, interconnect, object-store requests;
- data-quality failures, quarantined records, reconciliation gaps;
- cost per accepted dataset/model/update.

Retry only retry-safe boundaries. A task retry is harmless for a pure transformation but can duplicate an external effect.

## 15. Common failure modes

- Cluster overhead makes a small workload slower than one node.
- A wide join explodes rows or shuffles far more data than expected.
- Hot keys create one straggler partition.
- Driver/coordinator collects too much metadata or data.
- Millions of small files overload metadata/listing and reduce scan efficiency.
- Schema evolution silently changes meaning while remaining type-compatible.
- Checkpoints are deleted, incompatible, or slower than the recovery objective.
- Auto-scaling removes cached/stateful capacity or reacts after the deadline.
- Backfill competes with the live SLA.
- Duplicate events produce duplicate business effects.
- Training scales workers but loses speed to communication or input starvation.

## 16. Rapid interview questions

**Why can more partitions be slower?**  
Scheduling, metadata, open/close, serialization, shuffle, and small-file overhead can exceed useful work.

**Repartition versus coalesce?**  
Conceptually, repartition redistributes for a new partitioning requirement; coalescing reduces partitions with less movement where the engine permits. Verify exact engine behavior.

**Why is a broadcast join useful?**  
It sends a small relation to workers so the large side avoids a full shuffle. It fails when the supposedly small side exceeds memory or thresholds.

**Can Kafka guarantee global order?**  
Not across all partitions. It provides order within a partition; keying defines which events share that order.

**What does a watermark do?**  
It estimates event-time progress so an engine can close windows, fire timers, and clean state under a declared late-data policy.

**Why is a Spark/Flink “exactly once” claim insufficient?**  
The source, sink, effects, checkpointing, and failure boundaries determine end-to-end behavior.

**DDP versus FSDP?**  
DDP replicates a model and synchronizes gradients; FSDP shards model state to reduce per-device memory at added communication/complexity.

**What is the first optimization step?**  
Inspect the physical plan and stage/partition metrics; do not tune a guessed bottleneck.

## 17. Lead-level case: real-time fraud features

Design a platform that consumes transactions, creates online fraud features within seconds, and produces point-in-time-correct training data.

A strong response covers:

1. **Contract:** event IDs, account key, event time, ordering assumptions, duplicate and correction behavior, freshness/availability targets.
2. **Ingestion:** partitioned event log, schema registry/compatibility, authentication, retention, replay, dead-letter/quarantine path.
3. **Streaming:** event-time windows, watermarks, keyed state, late-data correction, checkpointing, deterministic feature version.
4. **Storage:** immutable governed raw events; curated table snapshots; online feature store with TTL; offline point-in-time feature history.
5. **Correctness:** idempotent event handling, stable feature keys, online/offline parity, replay tests, reconciliation counts.
6. **Serving:** request-time feature lookup, freshness metadata, fallback for missing/stale features, tenant/user authorization.
7. **Operations:** lag, state size, skew, checkpoint health, feature quality, backfill isolation, cost and disaster recovery.
8. **Rollout:** shadow features, compare online/offline values, canary consumers, rollback by feature version.

State the simplest initial version and how evidence would justify lower latency or a more complex streaming engine.

## 18. Final checklist

- [ ] I can choose single-node, batch-distributed, and streaming tools from a workload contract.
- [ ] I can explain partitions, stages, shuffles, skew, spill, and physical plans.
- [ ] I can explain Kafka partitions, groups, offsets, rebalances, idempotence, and transactions.
- [ ] I distinguish event time, processing time, watermarks, state, and late-data policy.
- [ ] I define exactly once at the business-effect boundary.
- [ ] I can design idempotent pipelines and isolated, reproducible backfills.
- [ ] I understand Parquet, object storage, table formats, small files, and pruning.
- [ ] I can compare DDP, FSDP/sharding, tensor, and pipeline parallelism.
- [ ] I monitor correctness, useful throughput, skew, recovery, and cost—not CPU alone.

## 19. Primary references

- Apache Spark, [Structured Streaming documentation](https://spark.apache.org/docs/latest/streaming/)
- Apache Kafka, [Design and delivery semantics](https://kafka.apache.org/documentation/#design)
- Apache Flink, [Fault tolerance](https://nightlies.apache.org/flink/flink-docs-stable/docs/learn-flink/fault_tolerance/)
- PyTorch, [Distributed overview](https://docs.pytorch.org/tutorials/beginner/dist_overview.html)
- Ray, [Ray Data internals](https://docs.ray.io/en/latest/data/internals.html)
- Polars, [Lazy and streaming execution](https://docs.pola.rs/user-guide/lazy/)
- Dask, [DataFrame best practices](https://docs.dask.org/en/latest/dataframe-best-practices.html)
- DuckDB, [Why DuckDB](https://duckdb.org/why_duckdb)

Engine behavior and guarantees are version- and connector-specific. Pin the exact stack and validate it with representative data and injected failures.
