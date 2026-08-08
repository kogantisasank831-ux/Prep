\set ON_ERROR_STOP on

DROP SCHEMA IF EXISTS week2 CASCADE;
CREATE SCHEMA week2;
SET search_path TO week2, public;

CREATE TABLE suppliers (
    supplier_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    supplier_code text NOT NULL UNIQUE,
    supplier_name text NOT NULL,
    lifecycle_status text NOT NULL
        CHECK (lifecycle_status IN ('active', 'suspended', 'retired'))
);

CREATE TABLE products (
    product_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sku text NOT NULL UNIQUE,
    product_name text NOT NULL,
    canonical_unit text NOT NULL
);

CREATE TABLE contracts (
    contract_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    supplier_id bigint NOT NULL REFERENCES suppliers (supplier_id),
    contract_code text NOT NULL,
    version_no integer NOT NULL CHECK (version_no > 0),
    valid_from date NOT NULL,
    valid_to date NOT NULL CHECK (valid_to > valid_from),
    UNIQUE (contract_code, version_no),
    UNIQUE (contract_id, supplier_id)
);

CREATE TABLE contract_items (
    contract_id bigint NOT NULL REFERENCES contracts (contract_id),
    contract_item_no integer NOT NULL CHECK (contract_item_no > 0),
    product_id bigint NOT NULL REFERENCES products (product_id),
    agreed_unit_price numeric(19, 4) NOT NULL
        CHECK (agreed_unit_price <> 'NaN'::numeric AND agreed_unit_price >= 0),
    currency_code text NOT NULL,
    unit_code text NOT NULL,
    lead_time_days integer NOT NULL CHECK (lead_time_days >= 0),
    PRIMARY KEY (contract_id, contract_item_no),
    UNIQUE (contract_id, product_id)
);

CREATE TABLE purchase_orders (
    purchase_order_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    po_number text NOT NULL UNIQUE,
    supplier_id bigint NOT NULL REFERENCES suppliers (supplier_id),
    contract_id bigint,
    ordered_on date NOT NULL,
    lifecycle_status text NOT NULL
        CHECK (lifecycle_status IN ('draft', 'issued', 'cancelled')),
    FOREIGN KEY (contract_id, supplier_id)
        REFERENCES contracts (contract_id, supplier_id),
    UNIQUE (purchase_order_id, contract_id)
);

CREATE TABLE purchase_order_items (
    purchase_order_id bigint NOT NULL,
    line_no integer NOT NULL CHECK (line_no > 0),
    product_id bigint NOT NULL REFERENCES products (product_id),
    contract_id bigint,
    contract_item_no integer,
    ordered_quantity numeric(18, 3) NOT NULL
        CHECK (ordered_quantity <> 'NaN'::numeric AND ordered_quantity > 0),
    po_unit_price numeric(19, 4) NOT NULL
        CHECK (po_unit_price <> 'NaN'::numeric AND po_unit_price >= 0),
    contract_unit_price numeric(19, 4),
    currency_code text NOT NULL,
    unit_code text NOT NULL,
    promised_on date NOT NULL,
    PRIMARY KEY (purchase_order_id, line_no),
    FOREIGN KEY (purchase_order_id)
        REFERENCES purchase_orders (purchase_order_id),
    FOREIGN KEY (purchase_order_id, contract_id)
        REFERENCES purchase_orders (purchase_order_id, contract_id),
    FOREIGN KEY (contract_id, contract_item_no)
        REFERENCES contract_items (contract_id, contract_item_no),
    CHECK (
        (contract_id IS NULL AND contract_item_no IS NULL AND contract_unit_price IS NULL)
        OR
        (contract_id IS NOT NULL AND contract_item_no IS NOT NULL AND contract_unit_price IS NOT NULL)
    ),
    CHECK (
        contract_unit_price IS NULL
        OR (contract_unit_price <> 'NaN'::numeric AND contract_unit_price >= 0)
    )
);

CREATE TABLE deliveries (
    delivery_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    purchase_order_id bigint NOT NULL REFERENCES purchase_orders (purchase_order_id),
    receipt_reference text NOT NULL UNIQUE,
    received_on date NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT current_timestamp,
    UNIQUE (delivery_id, purchase_order_id)
);

CREATE TABLE delivery_items (
    delivery_id bigint NOT NULL,
    purchase_order_id bigint NOT NULL,
    po_line_no integer NOT NULL,
    delivered_quantity numeric(18, 3) NOT NULL
        CHECK (delivered_quantity <> 'NaN'::numeric AND delivered_quantity > 0),
    accepted_quantity numeric(18, 3) NOT NULL
        CHECK (
            accepted_quantity <> 'NaN'::numeric
            AND accepted_quantity >= 0
            AND accepted_quantity <= delivered_quantity
        ),
    PRIMARY KEY (delivery_id, po_line_no),
    FOREIGN KEY (delivery_id, purchase_order_id)
        REFERENCES deliveries (delivery_id, purchase_order_id),
    FOREIGN KEY (purchase_order_id, po_line_no)
        REFERENCES purchase_order_items (purchase_order_id, line_no)
);

CREATE TABLE commodity_prices (
    product_id bigint NOT NULL REFERENCES products (product_id),
    currency_code text NOT NULL,
    unit_code text NOT NULL,
    source_code text NOT NULL,
    price_date date NOT NULL,
    unit_price numeric(19, 4) NOT NULL
        CHECK (unit_price <> 'NaN'::numeric AND unit_price >= 0),
    PRIMARY KEY (product_id, currency_code, unit_code, source_code, price_date)
);

CREATE INDEX deliveries_po_received_idx
    ON deliveries (purchase_order_id, received_on, delivery_id);
CREATE INDEX delivery_items_po_line_idx
    ON delivery_items (purchase_order_id, po_line_no, delivery_id);
CREATE INDEX purchase_order_items_promised_idx
    ON purchase_order_items (promised_on, purchase_order_id, line_no);
CREATE INDEX purchase_orders_ordered_idx
    ON purchase_orders (ordered_on, purchase_order_id);

CREATE FUNCTION validate_purchase_order() RETURNS trigger
LANGUAGE plpgsql
SET search_path = week2, pg_temp
AS $$
DECLARE
    selected_contract contracts%ROWTYPE;
BEGIN
    IF TG_OP = 'UPDATE'
       AND (NEW.supplier_id, NEW.contract_id, NEW.ordered_on)
           IS DISTINCT FROM
           (OLD.supplier_id, OLD.contract_id, OLD.ordered_on)
       AND EXISTS (
           SELECT 1 FROM purchase_order_items
           WHERE purchase_order_id = OLD.purchase_order_id
       ) THEN
        RAISE EXCEPTION 'supplier, contract, and order date cannot change after lines exist'
            USING ERRCODE = '23514';
    END IF;
    IF NEW.contract_id IS NULL THEN
        RETURN NEW;
    END IF;

    BEGIN
        SELECT * INTO STRICT selected_contract
        FROM contracts
        WHERE contract_id = NEW.contract_id;
    EXCEPTION WHEN no_data_found THEN
        RAISE EXCEPTION 'referenced contract does not exist'
            USING ERRCODE = '23514';
    END;

    IF selected_contract.supplier_id <> NEW.supplier_id THEN
        RAISE EXCEPTION 'contract supplier does not match PO supplier'
            USING ERRCODE = '23514';
    END IF;
    IF NOT (NEW.ordered_on >= selected_contract.valid_from
            AND NEW.ordered_on < selected_contract.valid_to) THEN
        RAISE EXCEPTION 'contract is not effective on PO order date'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER purchase_order_contract_guard
BEFORE INSERT OR UPDATE OF supplier_id, contract_id, ordered_on
ON purchase_orders
FOR EACH ROW EXECUTE FUNCTION validate_purchase_order();

CREATE FUNCTION validate_purchase_order_item() RETURNS trigger
LANGUAGE plpgsql
SET search_path = week2, pg_temp
AS $$
DECLARE
    parent_contract_id bigint;
    parent_status text;
    parent_ordered_on date;
    canonical_unit_code text;
    term contract_items%ROWTYPE;
BEGIN
    BEGIN
        SELECT contract_id, lifecycle_status, ordered_on
        INTO STRICT parent_contract_id, parent_status, parent_ordered_on
        FROM purchase_orders
        WHERE purchase_order_id = NEW.purchase_order_id
        FOR UPDATE;
    EXCEPTION WHEN no_data_found THEN
        RAISE EXCEPTION 'parent PO does not exist'
            USING ERRCODE = '23514';
    END;

    IF parent_status <> 'draft' THEN
        RAISE EXCEPTION 'PO lines can change only while the PO is draft'
            USING ERRCODE = '23514';
    END IF;
    IF NEW.promised_on < parent_ordered_on THEN
        RAISE EXCEPTION 'promise date cannot precede the PO order date'
            USING ERRCODE = '23514';
    END IF;

    BEGIN
        SELECT canonical_unit INTO STRICT canonical_unit_code
        FROM products
        WHERE product_id = NEW.product_id;
    EXCEPTION WHEN no_data_found THEN
        RAISE EXCEPTION 'referenced product does not exist'
            USING ERRCODE = '23514';
    END;

    IF NEW.unit_code <> canonical_unit_code THEN
        RAISE EXCEPTION 'PO unit must equal the product canonical unit'
            USING ERRCODE = '23514';
    END IF;

    IF parent_contract_id IS NULL THEN
        IF NEW.contract_id IS NOT NULL OR NEW.contract_item_no IS NOT NULL
           OR NEW.contract_unit_price IS NOT NULL THEN
            RAISE EXCEPTION 'spot PO lines cannot reference a contract term'
                USING ERRCODE = '23514';
        END IF;
        RETURN NEW;
    END IF;

    IF NEW.contract_id IS DISTINCT FROM parent_contract_id
       OR NEW.contract_item_no IS NULL OR NEW.contract_unit_price IS NULL THEN
        RAISE EXCEPTION 'contract-backed PO lines require a term from the header contract'
            USING ERRCODE = '23514';
    END IF;

    BEGIN
        SELECT * INTO STRICT term
        FROM contract_items
        WHERE contract_id = NEW.contract_id
          AND contract_item_no = NEW.contract_item_no;
    EXCEPTION WHEN no_data_found THEN
        RAISE EXCEPTION 'referenced contract term does not exist'
            USING ERRCODE = '23514';
    END;

    IF term.product_id <> NEW.product_id
       OR term.currency_code <> NEW.currency_code
       OR term.unit_code <> NEW.unit_code
       OR term.agreed_unit_price <> NEW.contract_unit_price THEN
        RAISE EXCEPTION 'PO contract snapshot does not match the immutable term'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER purchase_order_item_contract_guard
BEFORE INSERT OR UPDATE
ON purchase_order_items
FOR EACH ROW EXECUTE FUNCTION validate_purchase_order_item();

CREATE FUNCTION guard_purchase_order_item_delete() RETURNS trigger
LANGUAGE plpgsql
SET search_path = week2, pg_temp
AS $$
DECLARE
    parent_status text;
BEGIN
    SELECT lifecycle_status INTO STRICT parent_status
    FROM purchase_orders
    WHERE purchase_order_id = OLD.purchase_order_id
    FOR UPDATE;
    IF parent_status <> 'draft' THEN
        RAISE EXCEPTION 'PO lines can change only while the PO is draft'
            USING ERRCODE = '23514';
    END IF;
    RETURN OLD;
END;
$$;

CREATE TRIGGER purchase_order_item_delete_guard
BEFORE DELETE ON purchase_order_items
FOR EACH ROW EXECUTE FUNCTION guard_purchase_order_item_delete();

CREATE FUNCTION guard_immutable_contract() RETURNS trigger
LANGUAGE plpgsql
SET search_path = week2, pg_temp
AS $$
BEGIN
    RAISE EXCEPTION 'contract versions and terms are immutable; insert a new version'
        USING ERRCODE = '23514';
END;
$$;

CREATE TRIGGER contract_immutable_guard
BEFORE UPDATE OR DELETE ON contracts
FOR EACH ROW EXECUTE FUNCTION guard_immutable_contract();

CREATE TRIGGER contract_item_immutable_guard
BEFORE UPDATE OR DELETE ON contract_items
FOR EACH ROW EXECUTE FUNCTION guard_immutable_contract();

CREATE FUNCTION validate_purchase_order_transition() RETURNS trigger
LANGUAGE plpgsql
SET search_path = week2, pg_temp
AS $$
DECLARE
    accepted_total numeric;
BEGIN
    IF OLD.lifecycle_status <> 'draft'
       AND (NEW.po_number, NEW.supplier_id, NEW.contract_id, NEW.ordered_on)
           IS DISTINCT FROM
           (OLD.po_number, OLD.supplier_id, OLD.contract_id, OLD.ordered_on) THEN
        RAISE EXCEPTION 'issued PO commercial identity is immutable'
            USING ERRCODE = '23514';
    END IF;
    IF NEW.lifecycle_status = OLD.lifecycle_status THEN RETURN NEW; END IF;
    IF OLD.lifecycle_status = 'cancelled'
       OR (OLD.lifecycle_status = 'issued' AND NEW.lifecycle_status = 'draft') THEN
        RAISE EXCEPTION 'invalid PO lifecycle transition'
            USING ERRCODE = '23514';
    END IF;
    IF OLD.lifecycle_status = 'draft' AND NEW.lifecycle_status = 'issued'
       AND NOT EXISTS (
           SELECT 1 FROM purchase_order_items
           WHERE purchase_order_id = OLD.purchase_order_id
       ) THEN
        RAISE EXCEPTION 'a PO requires at least one line before issue'
            USING ERRCODE = '23514';
    END IF;
    IF OLD.lifecycle_status = 'draft' AND NEW.lifecycle_status = 'issued'
       AND (
           (NEW.contract_id IS NULL AND EXISTS (
               SELECT 1 FROM purchase_order_items
               WHERE purchase_order_id = OLD.purchase_order_id
                 AND (contract_id IS NOT NULL OR contract_item_no IS NOT NULL)
           ))
           OR
           (NEW.contract_id IS NOT NULL AND EXISTS (
               SELECT 1 FROM purchase_order_items
               WHERE purchase_order_id = OLD.purchase_order_id
                 AND (contract_id IS DISTINCT FROM NEW.contract_id
                      OR contract_item_no IS NULL)
           ))
       ) THEN
        RAISE EXCEPTION 'PO lines do not match the header contract policy'
            USING ERRCODE = '23514';
    END IF;
    IF NEW.lifecycle_status = 'cancelled' THEN
        SELECT COALESCE(SUM(di.accepted_quantity), 0) INTO accepted_total
        FROM delivery_items AS di
        WHERE di.purchase_order_id = OLD.purchase_order_id;
        IF accepted_total > 0 THEN
            RAISE EXCEPTION 'a PO with accepted receipts cannot be cancelled'
                USING ERRCODE = '23514';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER purchase_order_lifecycle_guard
BEFORE UPDATE
ON purchase_orders
FOR EACH ROW EXECUTE FUNCTION validate_purchase_order_transition();
