// A new worker is created and terminated for every submitted solution.
const RUNTIME = "https://cdn.jsdelivr.net/pyodide/v0.29.3/full/";

self.onmessage = async ({ data }) => {
  if (data?.kind !== "run") return;
  try {
    const { loadPyodide } = await import(`${RUNTIME}pyodide.mjs`);
    const pyodide = await loadPyodide({ indexURL: RUNTIME, stdout: () => {}, stderr: () => {} });
    const response = await fetch(new URL("assessment_runner.py", import.meta.url));
    if (!response.ok) throw new Error("The exercise checker could not be loaded.");
    await pyodide.runPythonAsync(await response.text());
    pyodide.globals.set("_assessment_source", data.source);
    pyodide.globals.set("_assessment_exercise_json", JSON.stringify(data.exercise));
    self.postMessage({ kind: "ready" });
    const raw = await pyodide.runPythonAsync(
      "import json\njson.dumps(await grade_submission(_assessment_source, json.loads(_assessment_exercise_json)))",
    );
    self.postMessage({ kind: "result", result: JSON.parse(raw) });
  } catch (error) {
    self.postMessage({ kind: "unavailable", message: String(error?.message ?? error).slice(0, 500) });
  }
};
