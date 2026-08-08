# Week 2 PostgreSQL lab

This is a destructive, synthetic local lab. It uses Podman and the pinned
PostgreSQL 18.4 Linux/AMD64 image from the Week 2 outline.

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
