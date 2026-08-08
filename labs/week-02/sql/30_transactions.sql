\set ON_ERROR_STOP on
SET search_path TO week2, public;

CREATE OR REPLACE FUNCTION record_delivery(
    target_po_number text,
    new_receipt_reference text,
    new_received_on date,
    target_line_numbers integer[],
    delivered_quantities numeric[],
    accepted_quantities numeric[]
) RETURNS bigint
LANGUAGE plpgsql
SET search_path = week2, pg_temp
AS $$
DECLARE
    target_po_id bigint;
    target_status text;
    target_ordered_on date;
    new_delivery_id bigint;
    item record;
    ordered_amount numeric;
    accepted_before numeric;
BEGIN
    IF cardinality(target_line_numbers) IS NULL
       OR cardinality(target_line_numbers) = 0
       OR cardinality(target_line_numbers) <> cardinality(delivered_quantities)
       OR cardinality(target_line_numbers) <> cardinality(accepted_quantities) THEN
        RAISE EXCEPTION 'delivery arrays must be non-empty and have equal length'
            USING ERRCODE = '22023';
    END IF;
    IF cardinality(target_line_numbers)
       <> (SELECT COUNT(DISTINCT line_no) FROM unnest(target_line_numbers) AS line_no) THEN
        RAISE EXCEPTION 'a delivery cannot repeat a PO line'
            USING ERRCODE = '22023';
    END IF;

    SELECT purchase_order_id, lifecycle_status, ordered_on
    INTO STRICT target_po_id, target_status, target_ordered_on
    FROM purchase_orders
    WHERE po_number = target_po_number
    FOR UPDATE;

    IF target_status <> 'issued' THEN
        RAISE EXCEPTION 'deliveries require an issued PO'
            USING ERRCODE = '23514';
    END IF;
    IF new_received_on IS NULL OR new_received_on < target_ordered_on THEN
        RAISE EXCEPTION 'receipt date cannot precede the PO order date'
            USING ERRCODE = '23514';
    END IF;

    FOR item IN
        SELECT line_no, delivered_quantity, accepted_quantity
        FROM unnest(target_line_numbers, delivered_quantities, accepted_quantities)
            AS u(line_no, delivered_quantity, accepted_quantity)
        ORDER BY line_no
    LOOP
        IF item.line_no IS NULL
           OR item.delivered_quantity IS NULL
           OR item.accepted_quantity IS NULL
           OR item.delivered_quantity = 'NaN'::numeric
           OR item.accepted_quantity = 'NaN'::numeric
           OR item.delivered_quantity <= 0
           OR item.accepted_quantity < 0
           OR item.accepted_quantity > item.delivered_quantity THEN
            RAISE EXCEPTION 'invalid delivered or accepted quantity'
                USING ERRCODE = '23514';
        END IF;

        SELECT ordered_quantity INTO STRICT ordered_amount
        FROM purchase_order_items
        WHERE purchase_order_id = target_po_id AND line_no = item.line_no
        FOR UPDATE;

        SELECT COALESCE(SUM(accepted_quantity), 0) INTO accepted_before
        FROM delivery_items
        WHERE purchase_order_id = target_po_id AND po_line_no = item.line_no;

        IF accepted_before + item.accepted_quantity > ordered_amount THEN
            RAISE EXCEPTION 'accepted quantity would exceed ordered quantity'
                USING ERRCODE = '23514';
        END IF;
    END LOOP;

    INSERT INTO deliveries (purchase_order_id, receipt_reference, received_on)
    VALUES (target_po_id, new_receipt_reference, new_received_on)
    RETURNING delivery_id INTO new_delivery_id;

    INSERT INTO delivery_items (
        delivery_id, purchase_order_id, po_line_no,
        delivered_quantity, accepted_quantity
    )
    SELECT new_delivery_id, target_po_id, line_no,
           delivered_quantity, accepted_quantity
    FROM unnest(target_line_numbers, delivered_quantities, accepted_quantities)
        AS u(line_no, delivered_quantity, accepted_quantity);

    RETURN new_delivery_id;
END;
$$;

CREATE OR REPLACE FUNCTION cancel_purchase_order(target_po_number text) RETURNS void
LANGUAGE plpgsql
SET search_path = week2, pg_temp
AS $$
DECLARE
    target_po_id bigint;
BEGIN
    SELECT purchase_order_id INTO STRICT target_po_id
    FROM purchase_orders
    WHERE po_number = target_po_number
    FOR UPDATE;

    UPDATE purchase_orders
    SET lifecycle_status = 'cancelled'
    WHERE purchase_order_id = target_po_id;
END;
$$;
