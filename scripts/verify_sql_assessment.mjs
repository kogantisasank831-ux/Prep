/** Actual PostgreSQL checks. Supply the pinned PGlite module path; no server required. */
import assert from "node:assert/strict";
import fs from "node:fs";
import { pathToFileURL } from "node:url";
import path from "node:path";
import { validateBank } from "../assessment-core.mjs";
import { compareSqlResult, gradeSql } from "../assessment-sql-runner.mjs";

if (!process.argv[2]) throw new Error("Supply the installed @electric-sql/pglite@0.5.11 dist/index.js path (see README).");
const runtimePath = path.resolve(process.argv[2]);
const metadata = JSON.parse(fs.readFileSync(path.join(path.dirname(runtimePath), "../package.json"), "utf8"));
assert.equal(metadata.name, "@electric-sql/pglite");
assert.equal(metadata.version, "0.5.11", "Use the same pinned runtime as the browser.");
const { PGlite } = await import(pathToFileURL(runtimePath).href);
const bank = validateBank(JSON.parse(fs.readFileSync("assessments/week-02.json", "utf8")));
for (const mutate of [
  b => b.code_language = "unsupported",
  b => b.sql_schema = "",
  b => delete b.sql_fixtures.example,
  b => b.questions.find(q => q.type === "code").checks[0].fixture = "unknown",
  b => b.questions.find(q => q.type === "code").checks[0].columns = [],
  b => b.questions.find(q => q.type === "code").checks[0].rows = [[null]],
]) {
  const malformed = structuredClone(bank); mutate(malformed);
  assert.throws(() => validateBank(malformed));
}
const mutants = {
  "W02-Q081": "SELECT id, name FROM suppliers ORDER BY id;",
  "W02-Q082": "SELECT id, supplier_id FROM orders WHERE ordered_on < DATE '2026-06-30' AND status <> 'cancelled' ORDER BY id;",
  "W02-Q083": "SELECT id, quantity + unit_price AS committed_value FROM lines ORDER BY id;",
  "W02-Q084": "SELECT l.id AS line_id, COALESCE(SUM(r.delivered),0) AS accepted_qty FROM lines l LEFT JOIN receipts r ON r.line_id=l.id AND r.received_on <= DATE '2026-06-30' GROUP BY l.id ORDER BY l.id;",
  "W02-Q085": "SELECT id AS line_id, quantity AS remaining_qty FROM lines WHERE promised_on < DATE '2026-06-30' ORDER BY id;",
  "W02-Q086": "SELECT TO_CHAR(o.ordered_on,'YYYY-MM') AS month, o.currency, SUM(l.quantity*l.unit_price) AS committed_value FROM orders o JOIN lines l ON l.order_id=o.id GROUP BY 1,2 ORDER BY 1,2;",
  "W02-Q087": "SELECT s.id AS supplier_id, COUNT(*) AS order_count FROM suppliers s LEFT JOIN orders o ON o.supplier_id=s.id AND o.ordered_on <= DATE '2026-06-30' AND o.status <> 'cancelled' GROUP BY s.id ORDER BY s.id;",
  "W02-Q088": "SELECT l.id AS line_id FROM lines l WHERE NOT EXISTS (SELECT 1 FROM receipts r WHERE r.line_id=l.id) ORDER BY l.id;",
  "W02-Q089": "SELECT product, MAX(price) AS market_price FROM prices WHERE currency='USD' AND unit='kg' AND priced_on <= DATE '2026-06-15' GROUP BY product ORDER BY product;",
  "W02-Q090": "SELECT id AS receipt_id, line_id, SUM(accepted) OVER (PARTITION BY line_id ORDER BY received_on) AS running_qty FROM receipts WHERE received_on <= DATE '2026-06-30' ORDER BY id;",
  "W02-Q091": "SELECT id AS receipt_id, LAG(accepted,1,0) OVER (PARTITION BY line_id ORDER BY received_on,id) AS previous_accepted FROM receipts WHERE received_on <= DATE '2026-06-30' ORDER BY id;",
  "W02-Q092": "WITH c AS (SELECT s.id AS supplier_id,COUNT(o.id) AS order_count FROM suppliers s LEFT JOIN orders o ON o.supplier_id=s.id AND o.ordered_on <= DATE '2026-06-30' AND o.status <> 'cancelled' GROUP BY s.id) SELECT supplier_id,order_count,ROW_NUMBER() OVER(ORDER BY order_count DESC,supplier_id) AS supplier_rank FROM c ORDER BY supplier_id;",
  "W02-Q093": "WITH p AS (SELECT l.id,l.unit_price,AVG(l.unit_price) OVER () AS mean_price FROM lines l JOIN orders o ON o.id=l.order_id WHERE o.ordered_on <= DATE '2026-06-30' AND o.status <> 'cancelled') SELECT id AS line_id FROM p WHERE unit_price > mean_price ORDER BY id;",
  "W02-Q094": "WITH a AS (SELECT line_id,SUM(accepted) AS qty FROM receipts WHERE received_on <= DATE '2026-06-30' GROUP BY line_id) SELECT l.id AS line_id,ROUND(100*COALESCE(a.qty,0)/l.quantity,2) AS accepted_pct FROM lines l LEFT JOIN a ON a.line_id=l.id ORDER BY l.id;",
  "W02-Q095": "SELECT supplier_id,COUNT(*) AS order_count FROM orders WHERE ordered_on <= DATE '2026-06-30' AND status <> 'cancelled' GROUP BY supplier_id HAVING COUNT(*) > 2 ORDER BY supplier_id;",
  "W02-Q096": "SELECT id AS receipt_id,delivered AS rejected_qty FROM receipts WHERE received_on <= DATE '2026-06-30' AND delivered > accepted ORDER BY id;",
  "W02-Q097": "SELECT product,unit FROM lines UNION ALL SELECT product,unit FROM prices ORDER BY product,unit;",
  "W02-Q098": "SELECT o.currency,SUM(l.quantity*l.unit_price) AS open_value FROM orders o JOIN lines l ON l.order_id=o.id WHERE o.ordered_on <= DATE '2026-06-30' AND o.status <> 'cancelled' GROUP BY o.currency ORDER BY o.currency;",
  "W02-Q099": "SELECT l.id AS line_id,p.price AS market_price FROM lines l JOIN orders o ON o.id=l.order_id LEFT JOIN LATERAL (SELECT price FROM prices p WHERE p.product=l.product AND p.unit=l.unit AND p.currency=o.currency ORDER BY p.priced_on DESC,p.id DESC LIMIT 1) p ON TRUE WHERE o.ordered_on <= DATE '2026-06-30' AND o.status <> 'cancelled' ORDER BY l.id;",
  "W02-Q100": "SELECT l.id AS line_id,MIN(r.received_on) AS completed_on FROM lines l LEFT JOIN receipts r ON r.line_id=l.id AND r.received_on <= DATE '2026-06-30' GROUP BY l.id ORDER BY l.id;"
};
const db = await PGlite.create();
try {
  console.log((await db.query("SELECT version() AS version")).rows[0].version);
  for (const q of bank.questions.filter(x => x.type === "code")) {
    const exercise = { ...q, schema: bank.sql_schema, fixtures: bank.sql_fixtures };
    const reference = await gradeSql(db, q.reference, exercise);
    assert.equal(reference.passed, 5, JSON.stringify({ id: q.id, reference }));
    const starter = await gradeSql(db, q.starter, exercise);
    assert.equal(starter.passed, 0, q.id);
    const wrong = await gradeSql(db, mutants[q.id], exercise);
    assert.ok(wrong.passed < 5, "Plausible error received full marks: " + q.id);
  }
  const q = bank.questions.find(x => x.type === "code");
  const exercise = { ...q, schema: bank.sql_schema, fixtures: bank.sql_fixtures };
  for (const source of [
    "SELEC id FROM suppliers",
    "SELECT id,name FROM suppliers; SELECT id,name FROM suppliers",
    "WITH removed AS (DELETE FROM suppliers RETURNING *) SELECT id,name FROM removed",
  ]) assert.equal((await gradeSql(db, source, exercise)).passed, 0);
  assert.equal((await gradeSql(db, q.reference, exercise)).passed, 5, "A failed query must not poison later attempts.");
  await assert.rejects(() => gradeSql(db, "x".repeat(20001), exercise));
  await assert.rejects(() => gradeSql(db, q.reference, { ...exercise, schema: "invalid schema" }));
} finally { await db.close(); }

// Test the grading boundary separately, including precision beyond JS safe integers.
const result = (rows, name = "amount", type = 1700) => ({ fields: [{ name, dataTypeID: type }], rows });
const check = rows => ({ columns: ["amount"], rows });
assert.equal(compareSqlResult(result([["9007199254740993.10"]]), check([["9007199254740993.1"]])), null);
assert.notEqual(compareSqlResult(result([["9007199254740993.11"]]), check([["9007199254740993.1"]])), null);
assert.equal(compareSqlResult(result([["1e-3"]]), check([["0.001"]])), null);
assert.equal(compareSqlResult(result([["-0.000"]]), check([[0]])), null);
assert.notEqual(compareSqlResult(result([[0]]), check([[null]])), null);
assert.notEqual(compareSqlResult(result([[""]], "amount", 25), check([[null]])), null);
assert.notEqual(compareSqlResult(result([[1], [1]]), check([[1]])), null);
assert.notEqual(compareSqlResult(result([[2], [1]]), check([[1], [2]])), null);
assert.notEqual(compareSqlResult(result([[1]], "wrong_alias"), check([[1]])), null);
assert.notEqual(compareSqlResult(result([["NaN"]]), check([["NaN"]])), null);
console.log("PASS: 100 reference result checks; 20 incomplete starters; 20 plausible wrong queries; syntax, multi-statement, read-only, reset and infrastructure failures; exact decimals, NULLs, duplicates, aliases and ordering.");
