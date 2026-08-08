\set ON_ERROR_STOP on
SET search_path TO week2, public;

INSERT INTO suppliers (supplier_id, supplier_code, supplier_name, lifecycle_status)
OVERRIDING SYSTEM VALUE VALUES
    (1, 'SUP-A', 'Atlas Metals', 'active'),
    (2, 'SUP-B', 'Beacon Industrial', 'active'),
    (3, 'SUP-C', 'Cedar Components', 'active'),
    (4, 'SUP-D', 'Dormant Supply', 'active');

INSERT INTO products (product_id, sku, product_name, canonical_unit)
OVERRIDING SYSTEM VALUE VALUES
    (1, 'COPPER-WIRE', 'Copper wire', 'kg'),
    (2, 'STEEL-PLATE', 'Steel plate', 'kg'),
    (3, 'FASTENER', 'Machine fastener', 'ea');

INSERT INTO contracts (
    contract_id, supplier_id, contract_code, version_no, valid_from, valid_to
) OVERRIDING SYSTEM VALUE VALUES
    (1, 1, 'ATLAS-2026', 1, DATE '2026-01-01', DATE '2027-01-01'),
    (2, 2, 'BEACON-2026', 1, DATE '2026-01-01', DATE '2027-01-01'),
    (3, 3, 'CEDAR-2026', 1, DATE '2026-01-01', DATE '2027-01-01'),
    (4, 1, 'ATLAS-FASTENER-PARALLEL', 1, DATE '2026-03-01', DATE '2026-07-01');

INSERT INTO contract_items VALUES
    (1, 1, 1, 11.5000, 'USD', 'kg', 15),
    (1, 2, 2,  8.0000, 'USD', 'kg', 15),
    (1, 3, 3,  2.0000, 'USD', 'ea', 15),
    (2, 1, 1, 11.8000, 'USD', 'kg', 15),
    (2, 2, 2,  8.2000, 'USD', 'kg', 15),
    (3, 1, 1, 12.1000, 'USD', 'kg', 15),
    (4, 1, 3,  2.1000, 'USD', 'ea', 15);

INSERT INTO purchase_orders (
    purchase_order_id, po_number, supplier_id, contract_id, ordered_on, lifecycle_status
) OVERRIDING SYSTEM VALUE VALUES
    (101, 'A-001', 1, 1, DATE '2026-01-05', 'draft'),
    (102, 'A-002', 1, 1, DATE '2026-02-05', 'draft'),
    (103, 'A-003', 1, 1, DATE '2026-03-05', 'draft'),
    (104, 'PO-1042', 1, 1, DATE '2026-06-01', 'draft'),
    (201, 'B-001', 2, 2, DATE '2026-01-08', 'draft'),
    (202, 'B-002', 2, 2, DATE '2026-02-08', 'draft'),
    (203, 'B-003', 2, 2, DATE '2026-03-08', 'draft'),
    (301, 'C-001', 3, 3, DATE '2026-01-10', 'draft'),
    (302, 'C-002', 3, 3, DATE '2026-02-10', 'draft'),
    (401, 'SPOT-001', 4, NULL, DATE '2026-06-10', 'draft'),
    (402, 'SPOT-ISSUED', 4, NULL, DATE '2026-06-10', 'draft');

INSERT INTO purchase_order_items (
    purchase_order_id, line_no, product_id, contract_id, contract_item_no,
    ordered_quantity, po_unit_price, contract_unit_price,
    currency_code, unit_code, promised_on
) VALUES
    (101, 1, 1, 1, 1, 100, 11.60, 11.50, 'USD', 'kg', DATE '2026-01-20'),
    (102, 1, 1, 1, 1, 100, 11.70, 11.50, 'USD', 'kg', DATE '2026-02-20'),
    (103, 1, 2, 1, 2, 100,  8.10,  8.00, 'USD', 'kg', DATE '2026-03-20'),
    (103, 2, 3, 1, 3,  50,  2.10,  2.00, 'USD', 'ea', DATE '2026-03-22'),
    (104, 1, 1, 1, 1, 1000, 12.00, 11.50, 'USD', 'kg', DATE '2026-06-20'),
    (201, 1, 1, 2, 1, 100, 11.90, 11.80, 'USD', 'kg', DATE '2026-01-23'),
    (202, 1, 2, 2, 2, 100,  8.30,  8.20, 'USD', 'kg', DATE '2026-02-23'),
    (203, 1, 1, 2, 1, 100, 12.00, 11.80, 'USD', 'kg', DATE '2026-03-23'),
    (301, 1, 1, 3, 1, 100, 12.20, 12.10, 'USD', 'kg', DATE '2026-01-25'),
    (302, 1, 1, 3, 1, 100, 12.20, 12.10, 'USD', 'kg', DATE '2026-02-25'),
    (401, 1, 2, NULL, NULL, 50, 9.00, NULL, 'USD', 'kg', DATE '2026-06-25'),
    (402, 1, 2, NULL, NULL, 50, 9.00, NULL, 'USD', 'kg', DATE '2026-07-10');

UPDATE purchase_orders
SET lifecycle_status = 'issued'
WHERE purchase_order_id <> 401;

SELECT record_delivery('A-001', 'R-A001', DATE '2026-01-18', ARRAY[1], ARRAY[100]::numeric[], ARRAY[100]::numeric[]);
SELECT record_delivery('A-002', 'R-A002', DATE '2026-02-25', ARRAY[1], ARRAY[100]::numeric[], ARRAY[100]::numeric[]);
SELECT record_delivery(
    'A-003', 'R-A003', DATE '2026-03-19',
    ARRAY[1, 2], ARRAY[100, 50]::numeric[], ARRAY[100, 50]::numeric[]
);
SELECT record_delivery('PO-1042', 'R-1042-1', DATE '2026-06-18', ARRAY[1], ARRAY[400]::numeric[], ARRAY[400]::numeric[]);
SELECT record_delivery('PO-1042', 'R-1042-2', DATE '2026-06-25', ARRAY[1], ARRAY[500]::numeric[], ARRAY[470]::numeric[]);
SELECT record_delivery('PO-1042', 'R-1042-FUTURE', DATE '2026-07-05', ARRAY[1], ARRAY[130]::numeric[], ARRAY[130]::numeric[]);
SELECT record_delivery('B-001', 'R-B001', DATE '2026-01-22', ARRAY[1], ARRAY[110]::numeric[], ARRAY[100]::numeric[]);
SELECT record_delivery('B-002', 'R-B002', DATE '2026-02-28', ARRAY[1], ARRAY[100]::numeric[], ARRAY[100]::numeric[]);
SELECT record_delivery('B-003', 'R-B003', DATE '2026-03-28', ARRAY[1], ARRAY[100]::numeric[], ARRAY[100]::numeric[]);
SELECT record_delivery('C-001', 'R-C001', DATE '2026-01-24', ARRAY[1], ARRAY[100]::numeric[], ARRAY[100]::numeric[]);
SELECT record_delivery('C-002', 'R-C002', DATE '2026-02-24', ARRAY[1], ARRAY[100]::numeric[], ARRAY[100]::numeric[]);

INSERT INTO commodity_prices VALUES
    (1, 'USD', 'kg', 'MARKET_A', DATE '2026-05-15', 11.7000),
    (1, 'USD', 'kg', 'MARKET_A', DATE '2026-06-01', 11.9000),
    (1, 'USD', 'kg', 'MARKET_A', DATE '2026-06-15', 12.1000),
    (1, 'EUR', 'kg', 'MARKET_A', DATE '2026-06-01', 10.9000),
    (2, 'EUR', 'kg', 'MARKET_A', DATE '2026-02-01',  7.5000),
    (2, 'USD', 'kg', 'MARKET_A', DATE '2026-03-01',  8.0500),
    (3, 'USD', 'ea', 'OTHER_SOURCE', DATE '2026-01-01', 1.9000);

SELECT setval(pg_get_serial_sequence('suppliers', 'supplier_id'), 4, true);
SELECT setval(pg_get_serial_sequence('products', 'product_id'), 3, true);
SELECT setval(pg_get_serial_sequence('contracts', 'contract_id'), 4, true);
SELECT setval(pg_get_serial_sequence('purchase_orders', 'purchase_order_id'), 402, true);
