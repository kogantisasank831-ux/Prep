# Week 2 technical review

## Result

Technical pass. No remaining technical publication blocker was found in the
final independent re-audit. Human content approval is still required.

## Scope

Published candidate: `content/weeks/week-02.md`

Executable source:

- `labs/week-02/sql/00_schema.sql`
- `labs/week-02/sql/30_transactions.sql`
- `labs/week-02/sql/10_seed.sql`
- `labs/week-02/sql/20_analytics.sql`
- `labs/week-02/sql/80_index_probe.sql`
- `labs/week-02/sql/90_verify.sql`

## Runtime evidence

- Review date: 2026-08-08
- Windows Podman client: 5.8.2
- Rootless WSL2 Linux/AMD64 Podman engine: 5.8.5
- PostgreSQL server: `18.4 (Debian 18.4-1.pgdg13+1)`
- Image:
  `docker.io/library/postgres:18.4@sha256:4cc13dede823cab4e05290c7fb3350fb4e599ecabd9b07e6706b5d5e8f5bc929`
- Image ID:
  `4b87d5343a0e499eea33b6c19ec152a3ed4a0d1a453eadd26ff415a406821a6e`

Query and race validation containers were disposable and had no host port. A
separate uniquely named volume was used only for the persistence check and was
removed afterward.

## Executed checks

The following files were applied in order with `psql -X` and stop-on-error:

1. schema reset and DDL;
2. transaction functions;
3. deterministic synthetic fixtures;
4. five analytical query families and overlap detection; and
5. assertion and negative-path verification.

Observed results:

- schema, triggers, functions, seed, views, and queries executed without error;
- `PO-1042` had 870 kg accepted, 130 kg remaining, and USD 1,560 open committed value at 2026-06-30;
- March committed spend was USD 2,115 after adding the multi-line mixed-unit
  regression fixture;
- the naive PO/delivery join inflated the two-line PO value and the assertion detected it;
- `SUP-A` ranked first and `SUP-B` second under the frozen minimum-three-order policy;
- NaN price/quantity inputs, aggregate over-acceptance, cancellation after an
  accepted receipt, invalid lifecycle mutations, immutable-fact mutations,
  orphaning a spot PO line, pre-order receipts, and out-of-range contract dates
  were rejected;
- a fully rejected receipt still allowed cancellation under the declared rule;
- explicit identity sequences accepted a later default-generated row;
- a future receipt did not alter the 2026-06-30 delayed result or the period-end
  reliability population;
- wrong-source, no-prior-price, currency/unit-mismatch, and spot-order price
  states were emitted by the analytical fixture; and
- the final assertion emitted `all implemented week-02 checks passed`.

Two independent-session races were then executed:

- concurrent 100 kg acceptances against a dedicated 130 kg order: the first
  committed, the second was rejected, and final accepted quantity was 100 kg;
- first accepted delivery versus cancellation: delivery committed, cancellation
  was rejected, final status remained `issued`, and accepted quantity was 10 kg.

The concurrency run exposed and led to correction of an initially unpinned
function `search_path`. Every PL/pgSQL function now pins
`search_path = week2, pg_temp`. A later independent audit found additional
fixture-masked issues: numeric NaN, spot-line FK ownership, immutable facts,
identity sequence state, mixed-unit aggregation, future-data leakage, and an
incorrect invoker-function permission suggestion. Those were corrected before
the final hardened rerun.

The complete hardened artifact sequence and both dedicated two-session races
passed after the corrections. A separate execution with
`-v as_of_date=2026-06-19` returned zero delayed lines, confirming that caller
parameters are not overwritten by defaults.

The final pass also confirmed that order-level quality contains no incompatible
physical-unit totals; header contract identity cannot change after lines exist;
issued PO numbers are immutable; issue revalidates every line against the header
policy; promise dates cannot precede order dates; and verification mutations
run inside a rolled-back transaction.

## Boundaries and remaining work

- All implemented fixture checks passed and the recorded outputs were observed
  at synthetic scale. This is not proof of general functional correctness and
  does not support production performance claims.
- A rolled-back 50,000-row product-price probe captured
  `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` before and after its workload-matched
  index. The observed plan changed from sequential scan plus sort to index scan;
  observed execution time changed from 11.512 ms to 0.071 ms. These numbers are
  environment-specific evidence, not a benchmark or production speed claim.
- A uniquely named Podman volume survived a container stop/remove/recreate cycle;
  `week2.suppliers` remained present. The temporary container and volume were
  then removed. The published cleanup names were not executed because they may
  belong to a learner's active lab.
- Direct table writes can bypass the aggregate delivery invariant. The lab uses
  `SECURITY INVOKER` functions and does not claim to enforce a protected write
  boundary; a safe definer/role design is explicitly out of scope.
- PostgreSQL, Podman, and Docker Official Image sources are linked in the draft;
  the final technical re-audit found no remaining citation blocker.
- Human pedagogical/content approval remains pending; nothing is approved for
  publication.
