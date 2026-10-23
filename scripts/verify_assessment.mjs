/** Behavioral checks for the static engine. Called by the existing pytest suite. */
import assert from "node:assert/strict";
import fs from "node:fs";
import {
  TYPES, MAX_SOURCE, answered, buildPaper, gradeObjective, randomSeed,
  restoreAttempt, sanitizeAnswer, scorePaper, validCodeResult, validateBank,
} from "../assessment-core.mjs";

const bank = validateBank(JSON.parse(fs.readFileSync(process.argv[2] ?? "assessments/week-01.json", "utf8")));
const clone = value => JSON.parse(JSON.stringify(value));
const seed = "00000000000000000000000000000001";
const original = JSON.stringify(bank);
const coverage = new Set();
for (let i = 0; i < 1000; i++) {
  const paper = buildPaper(bank, i.toString(16).padStart(32, "0"));
  assert.equal(paper.length, 10);
  assert.equal(new Set(paper.map(q => q.id)).size, 10);
  for (const type of TYPES) assert.equal(paper.filter(q => q.type === type).length, 2);
  paper.forEach(q => coverage.add(q.id));
}
assert.equal(coverage.size, 100);
assert.equal(JSON.stringify(bank), original);
assert.deepEqual(buildPaper(bank, seed), buildPaper(bank, seed));
assert.notDeepEqual(buildPaper(bank, seed).map(q => q.id), buildPaper(bank, "f".repeat(32)).map(q => q.id));
assert.throws(() => buildPaper(bank, "bad"));
assert.equal(randomSeed({ getRandomValues: bytes => bytes.fill(1) }), "01".repeat(16));
for (const mutate of [
  b => b.questions.pop(),
  b => b.questions[1].id = b.questions[0].id,
  b => b.questions[0].correct = ["not-an-option"],
  b => b.questions[0].correct = [],
  b => b.questions.find(q => q.type === "multiple").correct = ["o1"],
  b => b.questions.find(q => q.type === "match").correct = {},
  b => b.questions.find(q => q.type === "short").accepted = [],
  b => b.questions.find(q => q.type === "code").checks.pop(),
]) {
  const malformed = clone(bank); mutate(malformed); assert.throws(() => validateBank(malformed));
}

for (const q of bank.questions) {
  if (q.type === "code") continue;
  const correct = q.type === "single" ? q.correct[0] : q.type === "short" ? q.accepted[0] : q.correct;
  assert.equal(gradeObjective(q, correct), 10, q.id);
  assert.equal(gradeObjective(q, null), 0, q.id);
  if (q.type === "single") assert.equal(gradeObjective(q, q.options.find(x => !q.correct.includes(x.id)).id), 0);
  if (q.type === "multiple") {
    assert.equal(gradeObjective(q, q.correct.slice(1)), 0);
    assert.equal(gradeObjective(q, q.options.map(x => x.id)), 0);
    assert.equal(gradeObjective(q, "o1"), 0);
  }
  if (q.type === "short") {
    assert.equal(gradeObjective(q, `  ${q.accepted[0]}  `), 10);
    assert.equal(gradeObjective(q, `${q.accepted[0]} extra`), 0);
    const wrongCase = q.accepted[0].toUpperCase() === q.accepted[0] ? q.accepted[0].toLowerCase() : q.accepted[0].toUpperCase();
    if (q.case_sensitive && !q.accepted.includes(wrongCase)) assert.equal(gradeObjective(q, wrongCase), 0);
  }
  if (q.type === "match") {
    assert.equal(gradeObjective(q, { [q.left[0].id]: q.correct[q.left[0].id] }), 2.5);
    const duplicate = Object.fromEntries(q.left.map(x => [x.id, q.right[0].id]));
    assert.equal(gradeObjective(q, duplicate), 0);
    const swapped = { ...q.correct, [q.left[0].id]: q.correct[q.left[1].id], [q.left[1].id]: q.correct[q.left[0].id] };
    assert.equal(gradeObjective(q, swapped), 5);
  }
}

const paper = buildPaper(bank, seed);
const answers = Object.fromEntries(paper.map(q => [q.id, q.type === "code" ? q.reference : q.type === "single" ? q.correct[0] : q.type === "short" ? q.accepted[0] : q.correct]));
const codeResults = Object.fromEntries(paper.filter(q => q.type === "code").map(q => [q.id, {
  source: q.reference, question_id: q.id, status: "checked", passed: 5, total: 5,
  results: q.checks.map(x => ({ label: x.label, passed: true, detail: "Passed" })), output: "",
}]));
assert.equal(scorePaper(paper, answers, codeResults).earned, 100);
assert.equal(scorePaper(paper, answers, codeResults).pending_max, 0);
assert.equal(scorePaper(paper, answers).earned, 80);
assert.equal(scorePaper(paper, answers).graded_max, 80);
assert.equal(scorePaper(paper, answers).pending_max, 20);
const codeQuestion = paper.find(q => q.type === "code");
assert.equal(validCodeResult(codeQuestion, undefined, undefined), false);
assert.equal(validCodeResult(codeQuestion, "", undefined), false);
assert.equal(validCodeResult(codeQuestion, null, null), false);
const stale = { ...answers, [codeQuestion.id]: "# edited solution" };
assert.equal(scorePaper(paper, stale, codeResults).pending_max, 10);
const partial = clone(codeResults);
partial[codeQuestion.id].passed = 4;
partial[codeQuestion.id].results[0].passed = false;
assert.equal(scorePaper(paper, answers, partial).earned, 98);
partial[codeQuestion.id].passed = 6;
assert.equal(validCodeResult(codeQuestion, codeQuestion.reference, partial[codeQuestion.id]), false);
assert.equal(scorePaper(paper, answers, partial).pending_max, 10);
assert.equal(sanitizeAnswer(codeQuestion, "a".repeat(MAX_SOURCE + 1)).length, MAX_SOURCE);
assert.equal(answered(codeQuestion, " \n"), false);

const state = { schema_version: 1, bank_version: bank.version, week: bank.week, seed, answers, code_results: codeResults, started_at: "2026-10-23T00:00:00Z", submitted_at: "2026-10-23T00:30:00Z" };
const restored = restoreAttempt(bank, seed, state);
assert.deepEqual(restored.answers, answers);
assert.equal(scorePaper(paper, restored.answers, restored.code_results).earned, 100);
assert.equal(restored.submitted_at, state.submitted_at);
assert.equal(restoreAttempt(bank, seed, { ...state, bank_version: "old" }).submitted_at, null);
assert.deepEqual(restoreAttempt(bank, seed, { ...state, bank_version: "old" }).answers, {});
const invalidSource = restoreAttempt(bank, seed, { ...state, answers: stale });
assert.equal(invalidSource.code_results[codeQuestion.id], undefined);
console.log("PASS: bank validation; 1,000 balanced reproducible papers; all objective keys; exact/partial/pending scoring; stale-code rejection; restored attempts.");
