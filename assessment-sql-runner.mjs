/** Compare SQL results without rounding decimal money or dropping duplicate rows. */
const NUMERIC_TYPES = new Set([20, 21, 23, 700, 701, 1700]);

function decimal(value) {
  const match = String(value).match(/^([+-]?)(\d*)(?:\.(\d*))?(?:e([+-]?\d+))?$/i);
  if (!match || !(match[2] || match[3])) return null;
  const exponent = Number(match[4] ?? 0);
  if (!Number.isSafeInteger(exponent) || Math.abs(exponent) > 1000) return null;
  let digits = `${match[2]}${match[3] ?? ""}`.replace(/^0+/, "") || "0";
  let scale = (match[3]?.length ?? 0) - exponent;
  while (digits.endsWith("0") && digits !== "0") { digits = digits.slice(0, -1); scale--; }
  return digits === "0" ? "0" : `${match[1] === "-" ? "-" : ""}${digits}:${scale}`;
}

export function compareSqlResult(result, check) {
  if (JSON.stringify(result.fields.map(x => x.name)) !== JSON.stringify(check.columns)) return "Use the requested column names and order.";
  if (result.rows.length !== check.rows.length) return `Expected ${check.rows.length} row(s); received ${result.rows.length}. Check filters, joins and grouping.`;
  for (let i = 0; i < check.rows.length; i++) {
    for (let j = 0; j < check.columns.length; j++) {
      const actual = result.rows[i][j], expected = check.rows[i][j];
      const same = actual === null || expected === null ? actual === expected : NUMERIC_TYPES.has(result.fields[j].dataTypeID)
        ? decimal(actual) !== null && decimal(actual) === decimal(expected) : actual === expected;
      if (!same) return `Row ${i + 1}, ${check.columns[j]} differs. Check values, NULL handling and the requested ORDER BY.`;
    }
  }
  return null;
}

/** Fresh schema per case; learner statements execute in a read-only transaction. */
export async function gradeSql(db, source, exercise) {
  if (typeof source !== "string" || source.length > 20_000 || exercise.checks?.length !== 5) throw new Error("Invalid SQL submission.");
  const results = [];
  for (const check of exercise.checks) {
    // Fixture failures are infrastructure failures, never a failed learner answer.
    await db.exec(`DROP SCHEMA public CASCADE; CREATE SCHEMA public; ${exercise.schema}\n${exercise.fixtures[check.fixture]}`);
    await db.exec("BEGIN READ ONLY; SET LOCAL statement_timeout = '3s';");
    let detail;
    try {
      const result = await db.query(source, [], { rowMode: "array", parsers: {
        20: value => value, 700: value => value, 701: value => value,
        1700: value => value, 1082: value => value,
      } });
      detail = compareSqlResult(result, check);
    } catch (error) {
      detail = `SQL error: ${String(error?.message ?? error).slice(0, 350)}`;
    } finally {
      await db.exec("ROLLBACK;");
    }
    results.push({ label: check.label, passed: detail === null, detail: detail ?? "Passed" });
  }
  return { status: "checked", question_id: exercise.id, passed: results.filter(x => x.passed).length, total: 5, results, output: "" };
}
