\set ON_ERROR_STOP on
SET search_path TO week2, public;

BEGIN;

CREATE TEMP TABLE price_probe (
    product_id bigint NOT NULL,
    currency_code text NOT NULL,
    unit_code text NOT NULL,
    source_code text NOT NULL,
    price_date date NOT NULL,
    unit_price numeric(19, 4) NOT NULL
);

INSERT INTO price_probe
SELECT 1, 'USD', 'kg', 'MARKET_A',
       DATE '1889-01-01' + series_no,
       10.0000 + (series_no % 100)::numeric / 100
FROM generate_series(1, 50000) AS series_no;

ANALYZE price_probe;

\echo 'Before the workload-matched index'
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT price_date, unit_price
FROM price_probe
WHERE product_id = 1
  AND currency_code = 'USD'
  AND unit_code = 'kg'
  AND source_code = 'MARKET_A'
  AND price_date <= DATE '2026-06-01'
ORDER BY price_date DESC
LIMIT 1;

CREATE INDEX price_probe_lookup_idx
    ON price_probe (
        product_id, currency_code, unit_code, source_code, price_date DESC
    );
ANALYZE price_probe;

\echo 'After the workload-matched index'
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT price_date, unit_price
FROM price_probe
WHERE product_id = 1
  AND currency_code = 'USD'
  AND unit_code = 'kg'
  AND source_code = 'MARKET_A'
  AND price_date <= DATE '2026-06-01'
ORDER BY price_date DESC
LIMIT 1;

ROLLBACK;
