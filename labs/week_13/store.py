"""A separate synthetic SQLite fixture and atomic local review-intent ledger."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import closing, contextmanager
from pathlib import Path
import sqlite3
import time
from uuid import uuid4

from labs.week_11.fixtures import NORTH, SOUTH
from labs.week_13.contracts import (
    Actor,
    CommodityArgs,
    ReviewArgs,
    SqlArgs,
    SupplierArgs,
    ToolError,
    check_approval,
)

SCHEMA_VERSION = "week13/1"
SCHEMA = """
CREATE TABLE metadata(version TEXT NOT NULL);
CREATE TABLE suppliers(
 tenant TEXT NOT NULL, supplier_id TEXT NOT NULL, name TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status IN ('active','suspended')),
 PRIMARY KEY(tenant,supplier_id));
CREATE TABLE commodities(
 tenant TEXT NOT NULL, commodity_id TEXT NOT NULL, amount TEXT NOT NULL,
 currency TEXT NOT NULL, unit TEXT NOT NULL, as_of TEXT NOT NULL,
 PRIMARY KEY(tenant,commodity_id));
CREATE TABLE purchase_orders(
 tenant TEXT NOT NULL, purchase_order_id TEXT NOT NULL, supplier_id TEXT NOT NULL,
 commodity_id TEXT NOT NULL, baseline TEXT NOT NULL, current TEXT NOT NULL,
 currency TEXT NOT NULL, unit TEXT NOT NULL,
 PRIMARY KEY(tenant,purchase_order_id),
 FOREIGN KEY(tenant,supplier_id) REFERENCES suppliers(tenant,supplier_id),
 FOREIGN KEY(tenant,commodity_id) REFERENCES commodities(tenant,commodity_id));
CREATE TABLE grants(
 tenant TEXT NOT NULL, principal TEXT NOT NULL, purchase_order_id TEXT NOT NULL,
 can_review INTEGER NOT NULL CHECK(can_review IN (0,1)),
 PRIMARY KEY(tenant,principal,purchase_order_id),
 FOREIGN KEY(tenant,purchase_order_id) REFERENCES purchase_orders(tenant,purchase_order_id));
CREATE TABLE reviews(
 tenant TEXT NOT NULL, principal TEXT NOT NULL, operation_key TEXT NOT NULL,
 digest TEXT NOT NULL, review_id TEXT NOT NULL UNIQUE,
 purchase_order_id TEXT NOT NULL, reason TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status='open'),
 PRIMARY KEY(tenant,principal,operation_key),
 FOREIGN KEY(tenant,purchase_order_id) REFERENCES purchase_orders(tenant,purchase_order_id));
"""


def initialize(path: Path) -> None:
    """Create a NEW owned fixture file; never reset an existing file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb"):
        pass
    path.chmod(0o600)
    with closing(sqlite3.connect(path, isolation_level=None)) as connection:
        connection.execute("PRAGMA foreign_keys=ON")
        connection.executescript("BEGIN IMMEDIATE;\n" + SCHEMA)
        connection.execute("INSERT INTO metadata VALUES (?)", (SCHEMA_VERSION,))
        connection.executemany(
            "INSERT INTO suppliers VALUES (?,?,?,?)",
            [
                (NORTH, "SUP-001", "North Demo Metals", "active"),
                (NORTH, "SUP-PRIVATE", "Restricted Demo Supplier", "active"),
                (SOUTH, "SUP-001", "South Demo Metals", "suspended"),
            ],
        )
        connection.executemany(
            "INSERT INTO commodities VALUES (?,?,?,?,?,?)",
            [
                (NORTH, "STEEL", "2.10", "USD", "kg", "2026-10-01"),
                (SOUTH, "STEEL", "3.20", "INR", "kg", "2026-10-01"),
            ],
        )
        connection.executemany(
            "INSERT INTO purchase_orders VALUES (?,?,?,?,?,?,?,?)",
            [
                (NORTH, "PO-1001", "SUP-001", "STEEL", "2.00", "2.20", "USD", "kg"),
                (
                    NORTH,
                    "PO-PRIVATE",
                    "SUP-PRIVATE",
                    "STEEL",
                    "9.00",
                    "9.90",
                    "USD",
                    "kg",
                ),
                (SOUTH, "PO-1001", "SUP-001", "STEEL", "3.00", "3.30", "INR", "kg"),
            ],
        )
        connection.executemany(
            "INSERT INTO grants VALUES (?,?,?,?)",
            [
                (NORTH, "analyst", "PO-1001", 1),
                (NORTH, "finance", "PO-PRIVATE", 1),
                (SOUTH, "analyst", "PO-1001", 1),
            ],
        )
        connection.commit()


def record(row: sqlite3.Row) -> dict[str, object]:
    """Contain the dynamically typed database row at this adapter boundary."""
    return {key: row[key] for key in row.keys()}


class Store:
    def __init__(self, path: Path, clock: Callable[[], float] = time.monotonic) -> None:
        self.path = path.resolve()
        self.clock = clock

    @contextmanager
    def connect(self, *, write: bool = False) -> Iterator[sqlite3.Connection]:
        mode = "rw" if write else "ro"
        connection: sqlite3.Connection | None = None
        try:
            connection = sqlite3.connect(
                self.path.as_uri() + "?mode=" + mode,
                uri=True,
                isolation_level=None,
                timeout=0.25,
            )
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("PRAGMA trusted_schema=OFF")
            if not write:
                connection.execute("PRAGMA query_only=ON")
            row = connection.execute("SELECT version FROM metadata").fetchall()
            if len(row) != 1 or row[0]["version"] != SCHEMA_VERSION:
                raise ToolError("result_invalid")
            yield connection
        except sqlite3.Error as error:
            code = getattr(error, "sqlite_errorcode", None)
            transient = isinstance(code, int) and (code & 0xFF) in {
                sqlite3.SQLITE_BUSY,
                sqlite3.SQLITE_LOCKED,
            }
            raise ToolError("unavailable" if transient else "tool_failed") from error
        finally:
            if connection is not None:
                if connection.in_transaction:
                    connection.rollback()
                connection.close()

    def sql(self, actor: Actor, args: SqlArgs) -> dict[str, object]:
        # Only this application's two fixed templates can be selected.
        statement = """
        SELECT p.purchase_order_id,p.supplier_id,p.commodity_id,
               p.baseline,p.current,p.currency,p.unit
        FROM purchase_orders p JOIN grants g
          USING(tenant,purchase_order_id)
        WHERE p.tenant=? AND g.principal=?
        """
        values: list[object] = [actor.context.tenant_id, actor.context.principal_id]
        if args.query_name == "purchase_order_by_id":
            statement += " AND p.purchase_order_id=?"
            values.append(args.purchase_order_id)
        statement += " ORDER BY p.purchase_order_id LIMIT ?"
        values.append(args.limit)
        with self.connect() as connection:
            rows = connection.execute(statement, values).fetchall()
        return {"query_name": args.query_name, "rows": [record(row) for row in rows]}

    def supplier(self, actor: Actor, args: SupplierArgs) -> dict[str, object]:
        with self.connect() as connection:
            row = connection.execute(
                """
            SELECT s.supplier_id,s.name,s.status FROM suppliers s
            WHERE s.tenant=? AND s.supplier_id=? AND EXISTS(
              SELECT 1 FROM purchase_orders p JOIN grants g USING(tenant,purchase_order_id)
              WHERE p.tenant=s.tenant AND p.supplier_id=s.supplier_id AND g.principal=?)
            """,
                (actor.context.tenant_id, args.supplier_id, actor.context.principal_id),
            ).fetchone()
        if row is None:
            raise ToolError("not_found")
        return record(row)

    def commodity(self, actor: Actor, args: CommodityArgs) -> dict[str, object]:
        with self.connect() as connection:
            row = connection.execute(
                """
            SELECT c.commodity_id,c.amount,c.currency,c.unit,c.as_of
            FROM commodities c WHERE c.tenant=? AND c.commodity_id=? AND EXISTS(
              SELECT 1 FROM purchase_orders p JOIN grants g USING(tenant,purchase_order_id)
              WHERE p.tenant=c.tenant AND p.commodity_id=c.commodity_id AND g.principal=?)
            """,
                (
                    actor.context.tenant_id,
                    args.commodity_id,
                    actor.context.principal_id,
                ),
            ).fetchone()
        if row is None:
            raise ToolError("not_found")
        return {**record(row), "source": "synthetic-fixture"}

    def create_review(self, actor: Actor, args: ReviewArgs) -> dict[str, object]:
        """Authority, duplicate comparison and insertion share one transaction."""
        with self.connect(write=True) as connection:
            connection.execute("BEGIN IMMEDIATE")
            grant = connection.execute(
                """
            SELECT can_review FROM grants
            WHERE tenant=? AND principal=? AND purchase_order_id=?
            """,
                (
                    actor.context.tenant_id,
                    actor.context.principal_id,
                    args.purchase_order_id,
                ),
            ).fetchone()
            if grant is None or grant["can_review"] != 1:
                raise ToolError("not_found")
            digest = check_approval(actor, args, self.clock())
            scope = (
                actor.context.tenant_id,
                actor.context.principal_id,
                actor.operation_key,
            )
            saved = connection.execute(
                """
            SELECT digest,review_id,purchase_order_id,reason,status FROM reviews
            WHERE tenant=? AND principal=? AND operation_key=?
            """,
                scope,
            ).fetchone()
            if saved is not None:
                if saved["digest"] != digest:
                    raise ToolError("conflict")
                result = record(saved)
                del result["digest"]
                connection.commit()
                return {**result, "replayed": True}
            review_id = uuid4().hex
            connection.execute(
                "INSERT INTO reviews VALUES (?,?,?,?,?,?,?,?)",
                (
                    *scope,
                    digest,
                    review_id,
                    args.purchase_order_id,
                    args.reason,
                    "open",
                ),
            )
            connection.commit()
            return dict(
                review_id=review_id,
                purchase_order_id=args.purchase_order_id,
                reason=args.reason,
                status="open",
                replayed=False,
            )
