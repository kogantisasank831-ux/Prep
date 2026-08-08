\set ON_ERROR_STOP on
SET search_path TO week2, public;

BEGIN;

DO $$
DECLARE
    actual numeric;
    actual_date date;
    generated_id bigint;
BEGIN
    IF (SELECT COUNT(*) FROM suppliers) <> 4
       OR (SELECT COUNT(*) FROM products) <> 3
       OR (SELECT COUNT(*) FROM contracts) <> 4
       OR (SELECT COUNT(*) FROM purchase_orders) <> 11
       OR (SELECT COUNT(*) FROM purchase_order_items) <> 12 THEN
        RAISE EXCEPTION 'fixture counts mismatch';
    END IF;

    SELECT SUM(di.accepted_quantity) INTO actual
    FROM delivery_items di
    JOIN deliveries d USING (delivery_id, purchase_order_id)
    JOIN purchase_orders po USING (purchase_order_id)
    WHERE po.po_number = 'PO-1042' AND d.received_on <= DATE '2026-06-30';
    IF actual <> 870 THEN
        RAISE EXCEPTION 'PO-1042 as-of accepted: expected 870, got %', actual;
    END IF;

    SELECT SUM(poi.ordered_quantity * poi.po_unit_price) INTO actual
    FROM purchase_order_items poi JOIN purchase_orders po USING (purchase_order_id)
    WHERE po.po_number = 'A-003';
    IF actual <> 915 THEN
        RAISE EXCEPTION 'A-003 committed value: expected 915, got %', actual;
    END IF;
    IF NOT (
        (SELECT SUM(poi.ordered_quantity * poi.po_unit_price)
         FROM purchase_orders po
         JOIN purchase_order_items poi USING (purchase_order_id)
         JOIN delivery_items di USING (purchase_order_id)
         WHERE po.po_number = 'A-003') > actual
    ) THEN
        RAISE EXCEPTION 'fan-out fixture does not expose naive spend inflation';
    END IF;

    SELECT MIN(r.received_on) INTO actual_date
    FROM (
        SELECT d.received_on,
               SUM(di.accepted_quantity) OVER (ORDER BY d.received_on) AS running_accepted
        FROM deliveries d
        JOIN delivery_items di USING (delivery_id, purchase_order_id)
        JOIN purchase_orders po USING (purchase_order_id)
        WHERE po.po_number = 'A-002'
    ) r WHERE r.running_accepted >= 100;
    IF actual_date <> DATE '2026-02-25' THEN
        RAISE EXCEPTION 'A-002 completion date mismatch: %', actual_date;
    END IF;

    IF (SELECT COUNT(*) FROM (
        SELECT c1.contract_id
        FROM contracts c1 JOIN contract_items ci1 USING (contract_id)
        JOIN contracts c2
          ON c2.supplier_id = c1.supplier_id AND c2.contract_id > c1.contract_id
        JOIN contract_items ci2
          ON ci2.contract_id = c2.contract_id AND ci2.product_id = ci1.product_id
        WHERE daterange(c1.valid_from, c1.valid_to, '[)')
           && daterange(c2.valid_from, c2.valid_to, '[)')
    ) overlap_rows) <> 1 THEN
        RAISE EXCEPTION 'overlap detection fixture mismatch';
    END IF;

    IF (SELECT fully_accepted_on FROM order_quality WHERE po_number = 'PO-1042')
       <> DATE '2026-07-05' THEN
        RAISE EXCEPTION 'future receipt fixture does not complete PO-1042 on 2026-07-05';
    END IF;
    IF (SELECT COUNT(DISTINCT unit_code) FROM line_quality WHERE po_number = 'A-003') <> 2 THEN
        RAISE EXCEPTION 'mixed-unit A-003 must retain separate kg and ea line grains';
    END IF;
    IF (SELECT COUNT(*) FROM order_quality
        WHERE supplier_id = 1
          AND fully_accepted_on >= DATE '2026-01-01'
          AND fully_accepted_on < DATE '2026-07-01') <> 3 THEN
        RAISE EXCEPTION 'period-bounded SUP-A completion count mismatch';
    END IF;

    INSERT INTO suppliers (supplier_code, supplier_name, lifecycle_status)
    VALUES ('SEQUENCE-CHECK', 'Sequence Check', 'active')
    RETURNING supplier_id INTO generated_id;
    IF generated_id <= 4 THEN RAISE EXCEPTION 'supplier identity sequence is stale'; END IF;
    DELETE FROM suppliers WHERE supplier_id = generated_id;
END;
$$;

DO $$
BEGIN
    BEGIN
        INSERT INTO commodity_prices VALUES
            (1, 'USD', 'kg', 'NAN-CHECK', DATE '2026-01-01', 'NaN'::numeric);
        RAISE EXCEPTION 'expected NaN price rejection did not occur';
    EXCEPTION WHEN check_violation THEN NULL;
    END;

    BEGIN
        INSERT INTO commodity_prices VALUES
            (1, 'USD', 'kg', 'INFINITY-CHECK', DATE '2026-01-01', 'Infinity'::numeric);
        RAISE EXCEPTION 'expected infinity price rejection did not occur';
    EXCEPTION WHEN numeric_value_out_of_range THEN NULL;
    END;

    BEGIN
        INSERT INTO purchase_order_items VALUES
            (401, 2, 3, NULL, NULL, 'NaN'::numeric, 2, NULL,
             'USD', 'ea', DATE '2026-06-25');
        RAISE EXCEPTION 'expected NaN quantity rejection did not occur';
    EXCEPTION WHEN check_violation THEN NULL;
    END;

    BEGIN
        PERFORM record_delivery(
            'PO-1042', 'NAN-DELIVERY', DATE '2026-06-30',
            ARRAY[1], ARRAY['NaN'::numeric], ARRAY[0]::numeric[]
        );
        RAISE EXCEPTION 'expected NaN delivery rejection did not occur';
    EXCEPTION WHEN check_violation THEN NULL;
    END;

    BEGIN
        PERFORM record_delivery(
            'PO-1042', 'OVER-ACCEPT', DATE '2026-07-06',
            ARRAY[1], ARRAY[1]::numeric[], ARRAY[1]::numeric[]
        );
        RAISE EXCEPTION 'expected aggregate over-acceptance rejection did not occur';
    EXCEPTION WHEN check_violation THEN NULL;
    END;

    BEGIN
        PERFORM record_delivery(
            'PO-1042', 'BEFORE-ORDER', DATE '2026-05-31',
            ARRAY[1], ARRAY[1]::numeric[], ARRAY[1]::numeric[]
        );
        RAISE EXCEPTION 'expected pre-order receipt rejection did not occur';
    EXCEPTION WHEN check_violation THEN NULL;
    END;

    BEGIN
        DELETE FROM purchase_orders WHERE po_number = 'SPOT-001';
        RAISE EXCEPTION 'expected spot PO parent-delete rejection did not occur';
    EXCEPTION WHEN foreign_key_violation THEN NULL;
    END;

    BEGIN
        UPDATE contract_items SET agreed_unit_price = 99 WHERE contract_id = 1;
        RAISE EXCEPTION 'expected immutable contract-term rejection did not occur';
    EXCEPTION WHEN check_violation THEN NULL;
    END;

    BEGIN
        UPDATE purchase_order_items SET ordered_quantity = 1
        WHERE purchase_order_id = 101 AND line_no = 1;
        RAISE EXCEPTION 'expected issued PO-line mutation rejection did not occur';
    EXCEPTION WHEN check_violation THEN NULL;
    END;

    BEGIN
        UPDATE purchase_orders SET supplier_id = 2 WHERE purchase_order_id = 101;
        RAISE EXCEPTION 'expected issued PO-header mutation rejection did not occur';
    EXCEPTION WHEN check_violation THEN NULL;
    END;

    BEGIN
        UPDATE purchase_orders SET po_number = 'MUTATED' WHERE purchase_order_id = 101;
        RAISE EXCEPTION 'expected issued PO-number mutation rejection did not occur';
    EXCEPTION WHEN check_violation THEN NULL;
    END;

    BEGIN
        UPDATE purchase_orders SET contract_id = 1 WHERE purchase_order_id = 401;
        RAISE EXCEPTION 'expected spot-to-contract mutation rejection did not occur';
    EXCEPTION WHEN check_violation THEN NULL;
    END;

    BEGIN
        INSERT INTO purchase_order_items VALUES
            (401, 2, 3, NULL, NULL, 1, 2, NULL,
             'USD', 'ea', DATE '2026-06-09');
        RAISE EXCEPTION 'expected pre-order promise rejection did not occur';
    EXCEPTION WHEN check_violation THEN NULL;
    END;

    INSERT INTO purchase_order_items VALUES
        (401, 2, 3, NULL, NULL, 1, 2, NULL,
         'USD', 'ea', DATE '2026-06-10');
    DELETE FROM purchase_order_items
    WHERE purchase_order_id = 401 AND line_no = 2;

    BEGIN
        INSERT INTO purchase_orders (po_number, supplier_id, ordered_on, lifecycle_status)
        VALUES ('NO-LINES', 4, DATE '2026-06-01', 'draft');
        UPDATE purchase_orders SET lifecycle_status = 'issued' WHERE po_number = 'NO-LINES';
        RAISE EXCEPTION 'expected issue-without-lines rejection did not occur';
    EXCEPTION WHEN check_violation THEN NULL;
    END;

    BEGIN
        PERFORM cancel_purchase_order('PO-1042');
        RAISE EXCEPTION 'expected cancellation rejection did not occur';
    EXCEPTION WHEN check_violation THEN NULL;
    END;

    BEGIN
        INSERT INTO purchase_orders (
            po_number, supplier_id, contract_id, ordered_on, lifecycle_status
        ) VALUES ('BAD-DATE', 1, 1, DATE '2027-01-01', 'draft');
        RAISE EXCEPTION 'expected invalid contract-date rejection did not occur';
    EXCEPTION WHEN check_violation THEN NULL;
    END;

    UPDATE purchase_orders SET lifecycle_status = 'issued' WHERE po_number = 'SPOT-001';
    PERFORM record_delivery(
        'SPOT-001', 'FULLY-REJECTED', DATE '2026-06-20',
        ARRAY[1], ARRAY[10]::numeric[], ARRAY[0]::numeric[]
    );
    PERFORM cancel_purchase_order('SPOT-001');
    IF (SELECT lifecycle_status FROM purchase_orders WHERE po_number = 'SPOT-001')
       <> 'cancelled' THEN
        RAISE EXCEPTION 'fully rejected delivery should still allow cancellation';
    END IF;
    BEGIN
        UPDATE purchase_orders SET lifecycle_status = 'issued' WHERE po_number = 'SPOT-001';
        RAISE EXCEPTION 'expected cancelled PO transition rejection did not occur';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
END;
$$;

ROLLBACK;

SELECT 'all implemented week-02 checks passed' AS result;
