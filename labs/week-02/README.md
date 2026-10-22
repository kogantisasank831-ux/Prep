# Week 2 PostgreSQL lab

This is a destructive, synthetic local lab. It uses Podman and the pinned
PostgreSQL 18.4 Linux/AMD64 image from the Week 2 outline.

Before running the commands, open a terminal at the repository root. On Windows,
start your existing Podman machine. If you have not created one, use the main
lesson's Podman-machine setup first. Inspect existing machines with
`podman machine list`; the commands below assume a running engine.

Pull and inspect the exact reviewed image before using `--pull=never`. See the
[Podman pull reference](https://docs.podman.io/en/latest/markdown/podman-pull.1.html)
for digest-based pulls. This keeps
first-time setup consistent with the image reference in the lesson:

```powershell
podman pull docker.io/library/postgres:18.4@sha256:4cc13dede823cab4e05290c7fb3350fb4e599ecabd9b07e6706b5d5e8f5bc929
podman image inspect docker.io/library/postgres:18.4@sha256:4cc13dede823cab4e05290c7fb3350fb4e599ecabd9b07e6706b5d5e8f5bc929
```

Check that the container/volume names below do not belong to another active lab.
The database port is published only on loopback. Wait for `pg_isready` to report
that the server accepts connections before applying the SQL files.

```powershell
$env:POSTGRES_PASSWORD = Read-Host 'Local lab password'
podman volume create prep-week2-pgdata
podman run --detach --name prep-week2-postgres --pull=never `
  --env POSTGRES_DB=procurement `
  --env POSTGRES_USER=procurement `
  --env POSTGRES_PASSWORD `
  --publish 127.0.0.1:5432:5432 `
  --volume prep-week2-pgdata:/var/lib/postgresql `
  docker.io/library/postgres:18.4@sha256:4cc13dede823cab4e05290c7fb3350fb4e599ecabd9b07e6706b5d5e8f5bc929

podman exec prep-week2-postgres pg_isready -U procurement -d procurement

Get-Content -Raw labs/week-02/sql/00_schema.sql |
  podman exec -i prep-week2-postgres psql -X -U procurement -d procurement
Get-Content -Raw labs/week-02/sql/30_transactions.sql |
  podman exec -i prep-week2-postgres psql -X -U procurement -d procurement
Get-Content -Raw labs/week-02/sql/10_seed.sql |
  podman exec -i prep-week2-postgres psql -X -U procurement -d procurement
Get-Content -Raw labs/week-02/sql/20_analytics.sql |
  podman exec -i prep-week2-postgres psql -X -U procurement -d procurement
Get-Content -Raw labs/week-02/sql/80_index_probe.sql |
  podman exec -i prep-week2-postgres psql -X -U procurement -d procurement
Get-Content -Raw labs/week-02/sql/90_verify.sql |
  podman exec -i prep-week2-postgres psql -X -U procurement -d procurement
```

`00_schema.sql` drops and recreates schema `week2`; rerunning it deletes all lab
data. The volume and container names must be checked before cleanup.

The transaction functions serialize delivery and cancellation on the PO header,
then lock delivery lines in ascending line order. This single-role lab does not
prevent direct table writes from bypassing that procedural aggregate invariant.
The functions are `SECURITY INVOKER`; simply revoking table DML and granting
function execution would also remove the functions' ability to write. A real
protected write boundary requires a separately reviewed role, ownership, and
`SECURITY DEFINER` design and is outside this lab.

The analytical plan examples use synthetic data and cannot establish production
performance. Run `ANALYZE`, inspect `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)`,
and interpret the observed plan rather than asserting that an index must be used.

## What to run and what to inspect

| Script | Purpose |
| --- | --- |
| `00_schema.sql` | Reset the synthetic schema, create tables, constraints and guards |
| `30_transactions.sql` | Install delivery/cancellation functions before fixtures invoke them |
| `10_seed.sql` | Load the deterministic synthetic records |
| `20_analytics.sql` | Build the quality relations and execute the five analytical families |
| `80_index_probe.sql` | Compare plans on a temporary 50,000-row price relation, then roll back |
| `90_verify.sql` | Run assertions and negative paths inside a rolled-back transaction |

The default analytical cutoff is 2026-06-30. `PO-1042` should show 900 kg delivered,
870 kg accepted, 130 kg remaining and USD 1,560 open committed value at that
cutoff. Its later receipt completes acceptance on 2026-07-05. Those are separate
analytical states, both represented by the full seed.

The final verification message is `all implemented week-02 checks passed`.
That script checks a single-session fixture and negative paths. The original
technical review separately records two-session race tests; they are not
performed automatically by `90_verify.sql`.

For a concurrency exercise, create a dedicated new order with 130 kg ordered and
no prior accepted quantity. The original race accepted 100 kg once and rejected
the second 100 kg attempt. The full seed already completes `PO-1042`, so changing
`as_of_date` cannot make another 130 kg available to the write function.

Return to the [main lesson](https://kogantisasank831-ux.github.io/Prep/weeks/week-02/)
for the eight medium SQL and two product-analytics exercises, or use the
[beginner lesson](https://kogantisasank831-ux.github.io/Prep/weeks/week-02/beginner/)
for smaller practice steps. Keep all five outputs with their grain, cutoff,
currency/unit and denominator definitions. The supplied facts do not model
invoices or payments, so these queries cannot measure cash paid.
