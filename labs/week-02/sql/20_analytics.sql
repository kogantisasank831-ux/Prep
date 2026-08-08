\set ON_ERROR_STOP on
\if :{?as_of_date}
\else
  \set as_of_date '2026-06-30'
\endif
\if :{?period_start}
\else
  \set period_start '2026-01-01'
\endif
\if :{?period_end}
\else
  \set period_end '2026-07-01'
\endif
\if :{?source_code}
\else
  \set source_code 'MARKET_A'
\endif
SET search_path TO week2, public;

CREATE OR REPLACE VIEW line_quality AS
WITH receipt_day AS (
    SELECT di.purchase_order_id, di.po_line_no, d.received_on,
           SUM(di.delivered_quantity) AS delivered_that_day,
           SUM(di.accepted_quantity) AS accepted_that_day
    FROM deliveries AS d
    JOIN delivery_items AS di
      ON (di.delivery_id, di.purchase_order_id)
       = (d.delivery_id, d.purchase_order_id)
    GROUP BY di.purchase_order_id, di.po_line_no, d.received_on
), running AS (
    SELECT *,
           SUM(accepted_that_day) OVER (
               PARTITION BY purchase_order_id, po_line_no
               ORDER BY received_on
               ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
           ) AS cumulative_accepted
    FROM receipt_day
), completion AS (
    SELECT poi.purchase_order_id, poi.line_no,
           SUM(rd.delivered_that_day) AS delivered_quantity,
           SUM(rd.accepted_that_day) AS accepted_quantity,
           MIN(r.received_on) FILTER (
               WHERE r.cumulative_accepted >= poi.ordered_quantity
           ) AS fully_accepted_on
    FROM purchase_order_items AS poi
    LEFT JOIN receipt_day AS rd
      ON (rd.purchase_order_id, rd.po_line_no)
       = (poi.purchase_order_id, poi.line_no)
    LEFT JOIN running AS r
      ON (r.purchase_order_id, r.po_line_no, r.received_on)
       = (rd.purchase_order_id, rd.po_line_no, rd.received_on)
    GROUP BY poi.purchase_order_id, poi.line_no, poi.ordered_quantity
)
SELECT po.purchase_order_id, po.po_number, po.supplier_id, po.lifecycle_status,
       poi.line_no, poi.product_id, poi.unit_code, poi.ordered_quantity, poi.promised_on,
       COALESCE(c.delivered_quantity, 0) AS delivered_quantity,
       COALESCE(c.accepted_quantity, 0) AS accepted_quantity,
       COALESCE(c.delivered_quantity, 0) - COALESCE(c.accepted_quantity, 0)
           AS rejected_quantity,
       c.fully_accepted_on,
       c.fully_accepted_on IS NOT NULL
           AND c.fully_accepted_on <= poi.promised_on AS line_otif,
       CASE WHEN c.fully_accepted_on IS NOT NULL
            THEN GREATEST(c.fully_accepted_on - poi.promised_on, 0)
       END AS days_late
FROM purchase_orders AS po
JOIN purchase_order_items AS poi USING (purchase_order_id)
LEFT JOIN completion AS c
  ON (c.purchase_order_id, c.line_no)
   = (poi.purchase_order_id, poi.line_no);

CREATE OR REPLACE VIEW order_quality AS
SELECT purchase_order_id, po_number, supplier_id, lifecycle_status,
       CASE WHEN bool_and(fully_accepted_on IS NOT NULL)
            THEN MAX(fully_accepted_on) END AS fully_accepted_on,
       bool_and(line_otif) FILTER (WHERE fully_accepted_on IS NOT NULL)
           AND bool_and(fully_accepted_on IS NOT NULL) AS otif,
       CASE WHEN bool_and(fully_accepted_on IS NOT NULL)
            THEN MAX(days_late) END AS days_late
FROM line_quality
GROUP BY purchase_order_id, po_number, supplier_id, lifecycle_status;

\echo '1. Monthly committed procurement spend'
SELECT date_trunc('month', po.ordered_on)::date AS order_month,
       poi.currency_code,
       ROUND(SUM(poi.ordered_quantity * poi.po_unit_price), 2) AS committed_spend
FROM purchase_orders AS po
JOIN purchase_order_items AS poi USING (purchase_order_id)
WHERE po.lifecycle_status = 'issued'
  AND po.ordered_on >= :'period_start'::date
  AND po.ordered_on < :'period_end'::date
GROUP BY date_trunc('month', po.ordered_on)::date, poi.currency_code
ORDER BY order_month, poi.currency_code;

\echo '2. Delayed PO lines as of cutoff'
WITH accepted_as_of AS (
    SELECT di.purchase_order_id, di.po_line_no,
           SUM(di.accepted_quantity) AS accepted_quantity
    FROM deliveries AS d
    JOIN delivery_items AS di
      ON (di.delivery_id, di.purchase_order_id)
       = (d.delivery_id, d.purchase_order_id)
    WHERE d.received_on <= :'as_of_date'::date
    GROUP BY di.purchase_order_id, di.po_line_no
)
SELECT po.po_number, poi.line_no, poi.promised_on, poi.ordered_quantity,
       COALESCE(a.accepted_quantity, 0) AS accepted_quantity,
       poi.ordered_quantity - COALESCE(a.accepted_quantity, 0) AS remaining_quantity,
       ROUND((poi.ordered_quantity - COALESCE(a.accepted_quantity, 0))
             * poi.po_unit_price, 2) AS open_committed_value,
       poi.currency_code
FROM purchase_orders AS po
JOIN purchase_order_items AS poi USING (purchase_order_id)
LEFT JOIN accepted_as_of AS a
  ON (a.purchase_order_id, a.po_line_no)
   = (poi.purchase_order_id, poi.line_no)
WHERE po.lifecycle_status = 'issued'
  AND po.ordered_on <= :'as_of_date'::date
  AND poi.promised_on < :'as_of_date'::date
  AND COALESCE(a.accepted_quantity, 0) < poi.ordered_quantity
ORDER BY poi.promised_on, po.po_number, poi.line_no;

\echo '3. Contract and selected-source price variance'
SELECT po.po_number, poi.line_no, poi.po_unit_price, poi.currency_code,
       poi.contract_unit_price,
       poi.po_unit_price - poi.contract_unit_price AS contract_variance_per_unit,
       market.price_date, market.unit_price AS market_unit_price,
       poi.po_unit_price - market.unit_price AS market_variance_per_unit,
       CASE WHEN poi.contract_unit_price IS NULL THEN 'spot_order'
            ELSE 'comparable' END AS contract_comparison_status,
       CASE
           WHEN market.unit_price IS NOT NULL THEN 'comparable'
           WHEN EXISTS (
               SELECT 1 FROM commodity_prices cp
               WHERE cp.product_id = poi.product_id
                 AND cp.source_code = :'source_code'
                 AND cp.price_date <= po.ordered_on
                 AND (cp.currency_code <> poi.currency_code
                      OR cp.unit_code <> poi.unit_code)
           ) THEN 'currency_or_unit_mismatch'
           WHEN EXISTS (
               SELECT 1 FROM commodity_prices cp
               WHERE cp.product_id = poi.product_id
                 AND cp.price_date <= po.ordered_on
                 AND cp.source_code <> :'source_code'
           ) THEN 'wrong_source'
           WHEN EXISTS (
               SELECT 1 FROM commodity_prices cp
               WHERE cp.product_id = poi.product_id
                 AND cp.currency_code = poi.currency_code
                 AND cp.unit_code = poi.unit_code
                 AND cp.source_code = :'source_code'
                 AND cp.price_date > po.ordered_on
           ) THEN 'no_prior_price'
           ELSE 'no_price_history'
       END AS market_comparison_status
FROM purchase_orders AS po
JOIN purchase_order_items AS poi USING (purchase_order_id)
LEFT JOIN LATERAL (
    SELECT cp.price_date, cp.unit_price
    FROM commodity_prices AS cp
    WHERE cp.product_id = poi.product_id
      AND cp.currency_code = poi.currency_code
      AND cp.unit_code = poi.unit_code
      AND cp.source_code = :'source_code'
      AND cp.price_date <= po.ordered_on
    ORDER BY cp.price_date DESC
    LIMIT 1
) AS market ON true
WHERE po.lifecycle_status = 'issued'
ORDER BY po.po_number, poi.line_no;

\echo '4. Supplier performance components'
WITH receipt_day AS (
    SELECT di.purchase_order_id, di.po_line_no, d.received_on,
           SUM(di.delivered_quantity) AS delivered_quantity,
           SUM(di.accepted_quantity) AS accepted_quantity
    FROM deliveries d
    JOIN delivery_items di USING (delivery_id, purchase_order_id)
    WHERE d.received_on <= :'as_of_date'::date
    GROUP BY di.purchase_order_id, di.po_line_no, d.received_on
), receipt_running AS (
    SELECT *, SUM(accepted_quantity) OVER (
        PARTITION BY purchase_order_id, po_line_no ORDER BY received_on
    ) AS cumulative_accepted
    FROM receipt_day
), line_as_of AS (
    SELECT po.supplier_id, po.purchase_order_id, poi.line_no, poi.unit_code,
           poi.ordered_quantity, poi.promised_on,
           COALESCE(SUM(rd.delivered_quantity), 0) AS delivered_quantity,
           COALESCE(SUM(rd.accepted_quantity), 0) AS accepted_quantity,
           MIN(rr.received_on) FILTER (
               WHERE rr.cumulative_accepted >= poi.ordered_quantity
           ) AS fully_accepted_on
    FROM purchase_orders po
    JOIN purchase_order_items poi USING (purchase_order_id)
    LEFT JOIN receipt_day rd
      ON (rd.purchase_order_id, rd.po_line_no) = (poi.purchase_order_id, poi.line_no)
    LEFT JOIN receipt_running rr
      ON (rr.purchase_order_id, rr.po_line_no, rr.received_on)
       = (rd.purchase_order_id, rd.po_line_no, rd.received_on)
    WHERE po.lifecycle_status = 'issued' AND po.ordered_on <= :'as_of_date'::date
    GROUP BY po.supplier_id, po.purchase_order_id, poi.line_no, poi.unit_code,
             poi.ordered_quantity, poi.promised_on
)
SELECT s.supplier_code, l.unit_code,
       ROUND(SUM(l.accepted_quantity) / NULLIF(SUM(l.ordered_quantity), 0), 4)
           AS accepted_fill_rate,
       ROUND(SUM(l.delivered_quantity - l.accepted_quantity)
             / NULLIF(SUM(l.delivered_quantity), 0), 4) AS rejection_rate,
       COUNT(*) FILTER (
           WHERE l.promised_on < :'as_of_date'::date
             AND l.accepted_quantity < l.ordered_quantity
       ) AS open_late_lines
FROM line_as_of l
JOIN suppliers s USING (supplier_id)
GROUP BY s.supplier_code, l.unit_code
ORDER BY s.supplier_code, l.unit_code;

\echo '4b. Supplier completed-order outcomes at the same cutoff'
SELECT s.supplier_code,
       ROUND(AVG(oq.otif::integer) FILTER (
           WHERE oq.fully_accepted_on <= :'as_of_date'::date
       ), 4) AS completed_order_otif_rate,
       percentile_cont(0.5) WITHIN GROUP (ORDER BY oq.days_late)
           FILTER (WHERE oq.fully_accepted_on <= :'as_of_date'::date)
           AS median_days_late
FROM order_quality oq
JOIN suppliers s USING (supplier_id)
JOIN purchase_orders po USING (purchase_order_id)
WHERE oq.lifecycle_status = 'issued'
  AND po.ordered_on <= :'as_of_date'::date
GROUP BY s.supplier_code
ORDER BY s.supplier_code;

\echo '4c. Supplier committed value by currency at the cutoff'
SELECT s.supplier_code, poi.currency_code,
       ROUND(SUM(poi.ordered_quantity * poi.po_unit_price), 2) AS committed_value
FROM purchase_orders po
JOIN purchase_order_items poi USING (purchase_order_id)
JOIN suppliers s USING (supplier_id)
WHERE po.lifecycle_status = 'issued'
  AND po.ordered_on <= :'as_of_date'::date
GROUP BY s.supplier_code, poi.currency_code
ORDER BY s.supplier_code, poi.currency_code;

\echo '5. Eligible supplier reliability ranking'
WITH eligible AS (
    WITH receipt_day AS (
        SELECT di.purchase_order_id, di.po_line_no, d.received_on,
               SUM(di.delivered_quantity) AS delivered_quantity,
               SUM(di.accepted_quantity) AS accepted_quantity
        FROM deliveries d JOIN delivery_items di USING (delivery_id, purchase_order_id)
        WHERE d.received_on < :'period_end'::date
        GROUP BY di.purchase_order_id, di.po_line_no, d.received_on
    ), running AS (
        SELECT *, SUM(accepted_quantity) OVER (
            PARTITION BY purchase_order_id, po_line_no ORDER BY received_on
        ) AS cumulative_accepted
        FROM receipt_day
    ), line_policy AS (
        SELECT po.supplier_id, po.purchase_order_id, poi.line_no,
               MIN(r.received_on) FILTER (
                   WHERE r.cumulative_accepted >= poi.ordered_quantity
               ) AS fully_accepted_on,
               SUM(rd.delivered_quantity - rd.accepted_quantity)
                   / NULLIF(SUM(rd.delivered_quantity), 0) AS line_rejection_rate,
               poi.promised_on
        FROM purchase_orders po
        JOIN purchase_order_items poi USING (purchase_order_id)
        LEFT JOIN receipt_day rd
          ON (rd.purchase_order_id, rd.po_line_no) = (poi.purchase_order_id, poi.line_no)
        LEFT JOIN running r
          ON (r.purchase_order_id, r.po_line_no, r.received_on)
           = (rd.purchase_order_id, rd.po_line_no, rd.received_on)
        WHERE po.lifecycle_status = 'issued'
        GROUP BY po.supplier_id, po.purchase_order_id, poi.line_no,
                 poi.ordered_quantity, poi.promised_on
    ), order_policy AS (
        SELECT supplier_id, purchase_order_id,
               CASE WHEN bool_and(fully_accepted_on IS NOT NULL)
                    THEN MAX(fully_accepted_on) END AS fully_accepted_on,
               bool_and(fully_accepted_on <= promised_on)
                   AND bool_and(fully_accepted_on IS NOT NULL) AS otif,
               AVG(COALESCE(line_rejection_rate, 0)) AS rejection_rate,
               MAX(GREATEST(fully_accepted_on - promised_on, 0)) AS days_late
        FROM line_policy
        GROUP BY supplier_id, purchase_order_id
    )
    SELECT supplier_id, COUNT(*) AS completed_order_count,
           AVG(otif::integer)::numeric AS otif_rate,
           AVG(rejection_rate) AS rejection_rate,
           percentile_cont(0.5) WITHIN GROUP (ORDER BY days_late) AS median_days_late
    FROM order_policy
    WHERE fully_accepted_on >= :'period_start'::date
      AND fully_accepted_on < :'period_end'::date
    GROUP BY supplier_id HAVING COUNT(*) >= 3
), ranked AS (
    SELECT *, RANK() OVER (
        ORDER BY otif_rate DESC, rejection_rate ASC NULLS LAST,
                 median_days_late ASC
    ) AS reliability_rank
    FROM eligible
)
SELECT r.reliability_rank, s.supplier_code, r.completed_order_count,
       ROUND(r.otif_rate, 4) AS otif_rate,
       ROUND(r.rejection_rate, 4) AS rejection_rate,
       r.median_days_late
FROM ranked AS r
JOIN suppliers AS s USING (supplier_id)
ORDER BY r.reliability_rank, s.supplier_code;

\echo 'Data-quality: overlapping supplier/product agreement versions'
SELECT c1.supplier_id, ci1.product_id,
       c1.contract_code AS left_contract, c2.contract_code AS right_contract
FROM contracts AS c1
JOIN contract_items AS ci1 USING (contract_id)
JOIN contracts AS c2
  ON c2.supplier_id = c1.supplier_id AND c2.contract_id > c1.contract_id
JOIN contract_items AS ci2
  ON ci2.contract_id = c2.contract_id AND ci2.product_id = ci1.product_id
WHERE daterange(c1.valid_from, c1.valid_to, '[)')
   && daterange(c2.valid_from, c2.valid_to, '[)')
ORDER BY c1.supplier_id, ci1.product_id;
