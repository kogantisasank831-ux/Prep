// PostgreSQL runs only in this disposable worker; no database server is contacted.
import { gradeSql } from "./assessment-sql-runner.mjs";
const RUNTIME = "https://cdn.jsdelivr.net/npm/@electric-sql/pglite@0.5.11/dist/index.js";

self.onmessage = async ({ data }) => {
  if (data?.kind !== "run") return;
  try {
    const { PGlite } = await import(RUNTIME);
    const db = await PGlite.create();
    self.postMessage({ kind: "ready" });
    const result = await gradeSql(db, data.source, data.exercise);
    self.postMessage({ kind: "result", result });
    await db.close();
  } catch (error) {
    self.postMessage({ kind: "unavailable", message: String(error?.message ?? error).slice(0, 500) });
  }
};
