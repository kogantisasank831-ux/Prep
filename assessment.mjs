import {
  TYPE_LABELS, MAX_SOURCE, answered, buildPaper, emptyAnswer, randomSeed,
  restoreAttempt, sanitizeAnswer, scorePaper, validCodeResult, validSeed, validateBank,
} from "./assessment-core.mjs";

const root = document.querySelector("#assessment-app");
document.querySelector(".header-context").textContent = "Assessment";
const $ = selector => root.querySelector(selector);
const status = $("#assessment-status");
let bank, paper, attempt;
let activeRun = null;
let submitting = false;
let stopRequested = false;
let storageAvailable = true;
const controls = new Map();
const language = () => bank.code_language === "sql" ? "SQL" : "Python";
const typeLabel = q => q.type === "code" ? `${language()} coding` : TYPE_LABELS[q.type];

function element(tag, text = null, attributes = {}) {
  const node = document.createElement(tag);
  if (text !== null) node.textContent = text;
  for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, String(value));
  return node;
}

function codeBlock(text) {
  const pre = element("pre");
  pre.append(element("code", text));
  return pre;
}

function storageKey(seed = attempt.seed) { return `applied-genai-assessment:${bank.week}:${bank.version}:${seed}`; }
function currentKey() { return `applied-genai-assessment:${bank.week}:current`; }
function readStorage(key) {
  try { return localStorage.getItem(key); }
  catch { storageAvailable = false; return null; }
}
function save() {
  try {
    localStorage.setItem(storageKey(), JSON.stringify(attempt));
    localStorage.setItem(currentKey(), attempt.seed);
    storageAvailable = true;
  } catch {
    storageAvailable = false;
    status.textContent = "Autosave is unavailable. Keep this page open and download your result after submitting.";
    if (paper) updateProgress();
  }
}

function setBusyControls() {
  const busy = Boolean(activeRun) || submitting;
  $("#new-paper").disabled = busy;
  $("#submit-paper").disabled = busy || Boolean(attempt?.submitted_at);
  $("#stop-code").hidden = !activeRun;
  for (const [id, control] of controls) {
    if (control.runButton) control.runButton.disabled = busy;
    for (const input of control.inputs) input.disabled = busy || Boolean(attempt?.submitted_at);
    if (control.runButton && attempt?.submitted_at) {
      const q = paper.find(x => x.id === id);
      control.runButton.disabled ||= validCodeResult(q, attempt.answers[id], attempt.code_results[id]) || !answered(q, attempt.answers[id]);
    }
  }
}

function updateProgress() {
  const count = paper.filter(q => answered(q, attempt.answers[q.id])).length;
  $("#paper-progress").textContent = `${count}/10 answered · ${attempt.submitted_at ? "Submitted" : storageAvailable ? "Saved on this device" : "Not saved"}`;
  for (const link of $("#question-jumps").querySelectorAll("a")) {
    const q = paper.find(x => x.id === link.dataset.question);
    link.classList.toggle("answered", answered(q, attempt.answers[q.id]));
  }
}

function answerChanged(q, value) {
  attempt.answers[q.id] = sanitizeAnswer(q, value);
  if (q.type === "code") {
    delete attempt.code_results[q.id];
    controls.get(q.id).feedback.replaceChildren();
    controls.get(q.id).codeStatus.textContent = "Solution changed; run checks for this version.";
  }
  save(); updateProgress();
}

function showCodeChecks(q) {
  const control = controls.get(q.id);
  const result = attempt.code_results[q.id];
  control.feedback.replaceChildren();
  if (!validCodeResult(q, attempt.answers[q.id], result)) return;
  control.codeStatus.textContent = `${result.passed}/${result.total} checks passed${result.status === "timeout" ? " · execution limit exceeded" : ""}`;
  const list = element("ul");
  for (const item of result.results) {
    list.append(element("li", `${item.passed ? "Pass" : "Fail"}: ${item.label}${item.passed ? "" : ` — ${item.detail ?? "Check failed"}`}`));
  }
  control.feedback.append(list);
  if (result.output) {
    const details = element("details");
    details.append(element("summary", "Program output"), codeBlock(String(result.output).slice(0, 4000)));
    control.feedback.append(details);
  }
}

function renderQuestions() {
  controls.clear();
  const container = $("#assessment-questions");
  container.replaceChildren();
  $("#question-jumps").replaceChildren();
  paper.forEach((q, index) => {
    const card = element("section", null, { class: "assessment-question", id: `question-${index + 1}`, "aria-labelledby": `prompt-${q.id}` });
    card.append(element("span", `${index + 1}/10 · ${typeLabel(q)} · 10 marks`, { class: "assessment-tag" }));
    card.append(element("h3", q.prompt, { id: `prompt-${q.id}` }));
    if (q.snippet) card.append(codeBlock(q.snippet));
    const control = { card, inputs: [], feedback: element("div", null, { class: "assessment-feedback" }) };
    controls.set(q.id, control);
    const answer = attempt.answers[q.id] ?? emptyAnswer(q);
    if (["single", "multiple"].includes(q.type)) {
      const fieldset = element("fieldset");
      fieldset.append(element("legend", q.type === "single" ? "Choose one answer." : "Select every correct answer. The full set is required."));
      q.options.forEach((option, optionIndex) => {
        const label = element("label", null, { class: "assessment-option" });
        const input = element("input", null, { type: q.type === "single" ? "radio" : "checkbox", name: q.id, value: option.id });
        input.checked = q.type === "single" ? answer === option.id : answer.includes(option.id);
        input.addEventListener("change", () => {
          answerChanged(q, q.type === "single" ? input.value : control.inputs.filter(x => x.checked).map(x => x.value));
        });
        label.append(input, element("span", `${String.fromCharCode(65 + optionIndex)}. ${option.text}`));
        fieldset.append(label); control.inputs.push(input);
      });
      card.append(fieldset);
    } else if (q.type === "match") {
      card.append(element("p", "Match all four pairs. Use each option once.", { class: "assessment-note" }));
      const synchronizeOptions = () => {
        const used = new Set(control.inputs.map(x => x.value).filter(Boolean));
        for (const select of control.inputs) for (const option of select.options) option.disabled = Boolean(option.value) && used.has(option.value) && select.value !== option.value;
      };
      q.left.forEach(left => {
        const row = element("div", null, { class: "assessment-match-row" });
        const id = `match-${q.id}-${left.id}`;
        const select = element("select", null, { id });
        select.append(element("option", "Choose a match…", { value: "" }));
        q.right.forEach(right => select.append(element("option", right.text, { value: right.id })));
        select.value = answer[left.id] ?? "";
        select.dataset.left = left.id;
        select.addEventListener("change", () => {
          const value = Object.fromEntries(control.inputs.filter(x => x.value).map(x => [x.dataset.left, x.value]));
          answerChanged(q, value); synchronizeOptions();
        });
        row.append(element("label", left.text, { for: id }), select); card.append(row); control.inputs.push(select);
      });
      synchronizeOptions();
    } else if (q.type === "short") {
      const id = `short-${q.id}`;
      card.append(element("label", `Your answer · ${q.case_sensitive ? "case-sensitive" : "case-insensitive"}; surrounding spaces ignored`, { for: id, class: "assessment-note" }));
      const input = element("input", null, { type: "text", id, maxlength: 200, autocomplete: "off", autocapitalize: "off", spellcheck: "false" });
      input.value = answer;
      input.addEventListener("input", () => answerChanged(q, input.value));
      card.append(input); control.inputs.push(input);
    } else {
      const id = `code-${q.id}`;
      card.append(element("label", language() === "SQL" ? "Write one PostgreSQL SELECT or WITH query. Use the exact output columns and ordering requested." : "Write your Python solution. Define the requested names; do not read input().", { for: id, class: "assessment-note" }));
      if (language() === "SQL") {
        const fixture = element("details");
        fixture.append(element("summary", "Schema and example dataset"), element("p", "All five checks use this schema with different synthetic data. Copy this setup to an external PostgreSQL workspace if useful."), codeBlock(`${bank.sql_schema}\n${bank.sql_fixtures.example}`));
        card.append(fixture);
      }
      const input = element("textarea", null, { id, maxlength: MAX_SOURCE, spellcheck: "false", autocomplete: "off", autocapitalize: "off", autocorrect: "off" });
      input.value = answer || q.starter;
      input.addEventListener("input", () => answerChanged(q, input.value));
      control.inputs.push(input); card.append(input);
      const actions = element("div", null, { class: "assessment-code-actions" });
      control.runButton = element("button", `Run ${language()} checks`, { type: "button" });
      control.codeStatus = element("span", "Five checks · 2 marks each", { class: "assessment-code-status", role: "status" });
      control.runButton.addEventListener("click", async () => {
        if (!attempt.submitted_at && !attempt.answers[q.id]) answerChanged(q, input.value);
        await runCode(q);
        if (attempt.submitted_at) renderResult();
      });
      const external = element("a", language() === "SQL" ? "Open db<>fiddle ↗" : "Open Google Colab ↗", { href: language() === "SQL" ? "https://dbfiddle.uk/?rdbms=postgres_18" : "https://colab.research.google.com/", target: "_blank", rel: "noopener noreferrer" });
      actions.append(control.runButton, external, control.codeStatus); card.append(actions);
    }
    card.append(control.feedback); container.append(card);
    const jump = element("a", String(index + 1), { href: `#question-${index + 1}`, "aria-label": `Go to question ${index + 1}` });
    jump.dataset.question = q.id; $("#question-jumps").append(jump);
    if (q.type === "code") showCodeChecks(q);
  });
  updateProgress(); setBusyControls();
}

function executeCode(q, source) {
  return new Promise(resolve => {
    let worker;
    let timer;
    let settled = false;
    let executionStarted = false;
    const finish = value => {
      if (settled) return;
      settled = true; clearTimeout(timer); worker?.terminate(); activeRun = null;
      resolve(value);
    };
    try { worker = new Worker(new URL(language() === "SQL" ? "./assessment-sql-worker.mjs" : "./assessment-worker.mjs", import.meta.url), { type: "module" }); }
    catch { finish({ status: "unavailable", message: `This browser could not start the ${language()} worker.` }); return; }
    activeRun = { cancel: () => finish({ status: "unavailable", message: "Run stopped. Your solution is preserved." }) };
    timer = setTimeout(() => finish({ status: "unavailable", message: `${language()} did not load within 45 seconds. Check your connection and retry.` }), 45_000);
    worker.onerror = event => {
      event.preventDefault();
      finish({ status: "unavailable", message: `${language()} could not load. Retry, or use the external workspace and paste your solution back here.` });
    };
    worker.onmessage = ({ data }) => {
      if (settled) return;
      if (data?.kind === "ready") {
        if (executionStarted) return;
        executionStarted = true;
        clearTimeout(timer);
        controls.get(q.id).codeStatus.textContent = "Running the five checks…";
        timer = setTimeout(() => finish({
          status: "timeout", question_id: q.id, passed: 0, total: q.checks.length,
          results: q.checks.map(x => ({ label: x.label, passed: false, detail: "5-second execution limit exceeded" })), output: "",
        }), 5000);
      } else if (data?.kind === "result") finish(data.result);
      else if (data?.kind === "unavailable") finish({ status: "unavailable", message: `The ${language()} checker could not complete. Your solution is preserved; retry its checks.` });
    };
    worker.postMessage({ kind: "run", source, exercise: { id: q.id, checks: q.checks, ...(language() === "SQL" ? { schema: bank.sql_schema, fixtures: bank.sql_fixtures } : {}) } });
    setBusyControls();
  });
}

async function runCode(q) {
  if (activeRun) return;
  if (!submitting) stopRequested = false;
  const source = attempt.answers[q.id] ?? "";
  if (!source.trim()) return;
  controls.get(q.id).codeStatus.textContent = `Loading ${language()} on this device…`;
  const result = await executeCode(q, source);
  const record = { ...result, source };
  if (validCodeResult(q, source, record)) {
    attempt.code_results[q.id] = record;
    showCodeChecks(q);
  } else {
    delete attempt.code_results[q.id];
    controls.get(q.id).codeStatus.textContent = result.message ?? "Checks are pending; please retry.";
  }
  save(); setBusyControls();
}

function correctAnswerText(q) {
  if (["single", "multiple"].includes(q.type)) return q.correct.map(id => q.options.find(x => x.id === id).text).join("; ");
  if (q.type === "short") return q.accepted.join(" or ");
  return q.left.map(left => `${left.text} → ${q.right.find(x => x.id === q.correct[left.id]).text}`).join("\n");
}

function downloadResult() {
  const result = {
    schema_version: 1, assessment: "browser practice checks; not an authenticated record",
    week: bank.week, bank_version: bank.version, paper_seed: attempt.seed,
    started_at: attempt.started_at, submitted_at: attempt.submitted_at,
    score: scorePaper(paper, attempt.answers, attempt.code_results),
    question_ids: paper.map(q => q.id), answers: attempt.answers, code_results: attempt.code_results,
  };
  const url = URL.createObjectURL(new Blob([JSON.stringify(result, null, 2)], { type: "application/json" }));
  const link = element("a", "Download result", { href: url, download: `week-${String(bank.week).padStart(2, "0")}-${attempt.seed.slice(0, 8)}-result.json` });
  document.body.append(link); link.click(); link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function renderResult() {
  const score = scorePaper(paper, attempt.answers, attempt.code_results);
  const box = $("#assessment-result");
  box.hidden = false; box.replaceChildren();
  box.append(element("h2", score.pending_max ? "Provisional result" : "Your result", { id: "paper-result" }));
  box.append(element("p", `${score.earned} / ${score.pending_max ? score.graded_max : score.max}${score.pending_max ? " graded marks" : " marks"}`, { class: "assessment-score" }));
  if (score.pending_max) box.append(element("p", `${score.pending_max} coding marks are pending. Retry the pending checks below; your submitted solution stays locked. The complete paper is worth ${score.max}.`));
  else box.append(element("p", "Review each explanation and the checks below. Your answers are locked; start a new paper to try again."));
  const download = element("button", "Download result JSON", { type: "button" });
  download.addEventListener("click", downloadResult); box.append(download);
  for (const [index, q] of paper.entries()) {
    const control = controls.get(q.id);
    const row = score.rows[index];
    control.feedback.replaceChildren();
    if (q.type === "code") showCodeChecks(q);
    control.feedback.append(element("p", row.pending ? "Coding score pending" : `${row.earned} / ${row.max} marks`, { class: "assessment-mark" }));
    if (q.type !== "code") control.feedback.append(element("p", `Correct answer: ${correctAnswerText(q)}`));
    control.feedback.append(element("p", q.explanation));
    if (q.type === "code") {
      const solution = element("details");
      solution.append(element("summary", "Reference solution"), codeBlock(q.reference));
      control.feedback.append(solution);
    }
  }
  setBusyControls(); updateProgress();
}

function renderPrintPaper() {
  const target = document.querySelector("#assessment-print");
  target.replaceChildren(element("h2", `Week ${bank.week} · ${language()} assessment · 100 marks`));
  target.append(element("p", `Paper ${attempt.seed} · bank ${bank.version} · 10 questions. Name: __________________  Date: __________`));
  target.append(element("p", `10 marks each. Multiple-correct requires the full set. Matching: 2.5 per pair, each option once. Coding: five checks at 2 marks each. Write ${language()} solutions separately if needed.`));
  if (language() === "SQL") target.append(element("h3", "Coding schema and example data (all SQL tasks)"), codeBlock(`${bank.sql_schema}\n${bank.sql_fixtures.example}`));
  paper.forEach((q, index) => {
    const section = element("section");
    section.append(element("h3", `${index + 1}. ${q.prompt} [${typeLabel(q)} · 10 marks]`));
    if (q.snippet) section.append(codeBlock(q.snippet));
    if (q.options) q.options.forEach((option, i) => section.append(element("p", `${String.fromCharCode(65 + i)}. ${option.text}`)));
    if (q.type === "match") {
      q.left.forEach((left, i) => section.append(element("p", `${i + 1}. ${left.text}   → _____`)));
      q.right.forEach((right, i) => section.append(element("p", `${String.fromCharCode(65 + i)}. ${right.text}`)));
    }
    if (q.type === "code") section.append(codeBlock(q.starter), element("div", null, { class: "answer-space" }));
    else section.append(element("div", null, { class: "answer-line" }));
    target.append(section);
  });
}

function startPaper(seed) {
  let saved;
  try {
    const raw = readStorage(storageKey(seed));
    if (raw && raw.length <= 400_000) saved = JSON.parse(raw);
  } catch { status.textContent = "The saved attempt could not be read. This paper starts with a fresh answer sheet."; }
  attempt = restoreAttempt(bank, seed, saved);
  paper = buildPaper(bank, seed);
  const address = new URL(location.href);
  address.searchParams.set("paper", seed); address.searchParams.set("v", bank.version);
  history.replaceState(null, "", address);
  $("#paper-id").textContent = `Paper W${String(bank.week).padStart(2, "0")}-${seed.slice(0, 8)}`;
  $("#assessment-result").hidden = true;
  $("#assessment-toolbar").hidden = false; $("#assessment-form").hidden = false;
  renderQuestions(); renderPrintPaper(); save();
  if (attempt.submitted_at) renderResult();
}

$("#new-paper").addEventListener("click", () => {
  save(); startPaper(randomSeed());
  status.textContent = storageAvailable ? "New random paper ready. Previous papers remain saved under their paper links on this device." : "New paper ready. Autosave is unavailable; keep this page open and download the result.";
  $("#paper-id").scrollIntoView({ block: "center" });
});
$("#copy-paper").addEventListener("click", async () => {
  try { await navigator.clipboard.writeText(location.href); status.textContent = "Paper link copied. It reproduces the same questions and option order, without sharing your answers."; }
  catch { status.textContent = `Copy this paper address: ${location.href}`; }
});
$("#print-paper").addEventListener("click", () => window.print());
$("#stop-code").addEventListener("click", () => { stopRequested = true; activeRun?.cancel(); });
$("#assessment-form").addEventListener("submit", async event => {
  event.preventDefault();
  if (submitting || activeRun || attempt.submitted_at) return;
  const missing = paper.filter(q => !answered(q, attempt.answers[q.id])).length;
  if (missing && !window.confirm(`${missing} question(s) are unanswered and will receive zero. Submit this paper?`)) return;
  submitting = true; stopRequested = false; setBusyControls();
  for (const q of paper.filter(x => x.type === "code")) {
    if (stopRequested) break;
    if (answered(q, attempt.answers[q.id]) && !validCodeResult(q, attempt.answers[q.id], attempt.code_results[q.id])) await runCode(q);
  }
  submitting = false; attempt.submitted_at = new Date().toISOString(); save(); renderResult();
  $("#assessment-result").scrollIntoView({ block: "start" });
});

try {
  const response = await fetch(root.dataset.bank);
  if (!response.ok) throw new Error("The question bank is unavailable. Please reload this page.");
  bank = validateBank(await response.json());
  const params = new URL(location.href).searchParams;
  if (params.has("v") && params.get("v") !== bank.version) throw new Error("This paper link belongs to a different bank version. Open the assessment without its query string to start a current paper.");
  const requested = params.get("paper");
  const previous = readStorage(currentKey());
  const seed = validSeed(requested) ? requested : validSeed(previous) ? previous : randomSeed();
  status.textContent = "100 questions ready. Your paper draws two questions from each format.";
  startPaper(seed);
} catch (error) {
  status.textContent = error.message ?? "The assessment could not load. Please reload this page.";
}
