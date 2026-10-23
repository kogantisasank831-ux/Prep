/** Pure assessment contracts shared by the page and validation tools. */
export const TYPES = ["single", "multiple", "match", "short", "code"];
export const POINTS = 10;
export const MAX_SOURCE = 20_000;
export const TYPE_LABELS = {
  single: "Single choice", multiple: "Multiple correct", match: "Match the following",
  short: "Short syntax answer", code: "Python coding",
};

function invariant(condition, message) {
  if (!condition) throw new Error(message);
}

export function validateBank(bank) {
  invariant(bank?.schema_version === 1 && Number.isInteger(bank.week), "Unsupported assessment bank.");
  invariant(typeof bank.version === "string" && bank.questions?.length === 100, "A weekly bank needs exactly 100 questions.");
  invariant(bank.paper_policy?.questions === 10 && bank.paper_policy.per_type === 2 && bank.paper_policy.points_each === POINTS, "Unsupported paper scoring policy.");
  const ids = new Set();
  for (const q of bank.questions) {
    invariant(typeof q.id === "string" && !ids.has(q.id), "Question IDs must be unique.");
    ids.add(q.id);
    invariant(TYPES.includes(q.type) && typeof q.prompt === "string" && q.prompt.length > 10, `Invalid question ${q.id}.`);
    invariant(typeof q.topic === "string" && typeof q.explanation === "string" && q.explanation.length > 10, `Missing teaching context ${q.id}.`);
    if (["single", "multiple"].includes(q.type)) {
      invariant(Array.isArray(q.options) && q.options.length >= 3, `Missing choices ${q.id}.`);
      const keys = q.options.map(x => x.id);
      invariant(new Set(keys).size === keys.length && q.options.every(x => typeof x.id === "string" && x.id.length && typeof x.text === "string"), `Invalid choices ${q.id}.`);
      invariant(Array.isArray(q.correct) && new Set(q.correct).size === q.correct.length && q.correct.every(x => keys.includes(x)), `Invalid key ${q.id}.`);
      invariant(q.type === "single" ? q.correct.length === 1 : q.correct.length >= 2 && q.correct.length < keys.length, `Ambiguous choice count ${q.id}.`);
    } else if (q.type === "match") {
      invariant(q.left?.length === 4 && q.right?.length === 4, `Matching needs four pairs ${q.id}.`);
      for (const side of [q.left, q.right]) invariant(new Set(side.map(x => x.id)).size === 4 && side.every(x => typeof x.text === "string"), `Invalid match options ${q.id}.`);
      invariant(Object.keys(q.correct ?? {}).length === 4 && q.left.every(x => q.right.some(y => y.id === q.correct[x.id])) && new Set(Object.values(q.correct)).size === 4, `Invalid match key ${q.id}.`);
    } else if (q.type === "short") {
      invariant(q.accepted?.length > 0 && q.accepted.every(x => typeof x === "string" && x.trim().length), `Missing short-answer key ${q.id}.`);
      invariant(typeof q.case_sensitive === "boolean", `Declare case policy ${q.id}.`);
    } else {
      invariant(typeof q.starter === "string" && typeof q.reference === "string" && q.checks?.length === 5, `Coding needs a starter, reference and five checks ${q.id}.`);
      invariant(q.checks.every(x => typeof x.label === "string" && typeof x.code === "string"), `Invalid code checks ${q.id}.`);
    }
  }
  for (const type of TYPES) invariant(bank.questions.filter(q => q.type === type).length >= 2, `Insufficient ${type} questions.`);
  return bank;
}

export function randomSeed(cryptoSource = globalThis.crypto) {
  const bytes = new Uint8Array(16);
  cryptoSource.getRandomValues(bytes);
  return [...bytes].map(x => x.toString(16).padStart(2, "0")).join("");
}

export function validSeed(seed) { return typeof seed === "string" && /^[a-f0-9]{32}$/.test(seed); }

function generator(seed) {
  let state = 2166136261;
  for (const c of seed) state = Math.imul(state ^ c.charCodeAt(0), 16777619) >>> 0;
  return () => {
    state = (state + 0x6D2B79F5) >>> 0;
    let value = Math.imul(state ^ (state >>> 15), 1 | state);
    value ^= value + Math.imul(value ^ (value >>> 7), 61 | value);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
}

export function shuffled(items, random) {
  const result = [...items];
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}

export function buildPaper(bank, seed) {
  validateBank(bank);
  invariant(validSeed(seed), "Invalid paper seed.");
  const random = generator(`${bank.week}:${bank.version}:${seed}`);
  const chosen = TYPES.flatMap(type => shuffled(bank.questions.filter(q => q.type === type), random).slice(0, 2));
  return shuffled(chosen, random).map(q => ({
    ...q,
    ...(q.options ? { options: shuffled(q.options, random) } : {}),
    ...(q.right ? { right: shuffled(q.right, random) } : {}),
  }));
}

export function emptyAnswer(q) {
  return q.type === "multiple" ? [] : q.type === "match" ? {} : "";
}

export function sanitizeAnswer(q, answer) {
  if (["short", "code"].includes(q.type)) return typeof answer === "string" ? answer.slice(0, q.type === "code" ? MAX_SOURCE : 200) : "";
  if (q.type === "single") return q.options.some(x => x.id === answer) ? answer : "";
  if (q.type === "multiple") return Array.isArray(answer) ? [...new Set(answer.filter(x => q.options.some(o => o.id === x)))] : [];
  const result = {};
  for (const left of q.left) if (q.right.some(x => x.id === answer?.[left.id])) result[left.id] = answer[left.id];
  return result;
}

export function answered(q, answer) {
  if (q.type === "multiple") return Array.isArray(answer) && answer.length > 0;
  if (q.type === "match") return q.left.some(x => typeof answer?.[x.id] === "string" && answer[x.id]);
  return typeof answer === "string" && answer.trim().length > 0;
}

export function gradeObjective(q, rawAnswer) {
  invariant(q.type !== "code", "Coding requires executed checks.");
  const answer = sanitizeAnswer(q, rawAnswer);
  if (q.type === "single") return q.correct.includes(answer) ? POINTS : 0;
  if (q.type === "multiple") return answer.length === q.correct.length && q.correct.every(x => answer.includes(x)) ? POINTS : 0;
  if (q.type === "short") {
    const normalize = value => q.case_sensitive ? value.trim() : value.trim().toLowerCase();
    return q.accepted.some(x => normalize(x) === normalize(answer)) ? POINTS : 0;
  }
  const selected = Object.values(answer);
  if (new Set(selected).size !== selected.length) return 0;
  return POINTS * q.left.filter(x => answer[x.id] === q.correct[x.id]).length / q.left.length;
}

export function validCodeResult(q, source, result) {
  return Boolean(result && typeof source === "string" && result.source === source && result.question_id === q.id && result.total === q.checks.length &&
    ["checked", "timeout"].includes(result.status) && Array.isArray(result.results) &&
    result.results.length === q.checks.length && result.results.every((x, i) => typeof x.passed === "boolean" && x.label === q.checks[i].label) &&
    result.passed === result.results.filter(x => x.passed).length);
}

export function scorePaper(paper, answers = {}, codeResults = {}) {
  const rows = paper.map(q => {
    const answer = sanitizeAnswer(q, answers[q.id]);
    if (q.type !== "code") return { id: q.id, type: q.type, earned: gradeObjective(q, answer), max: POINTS, pending: false };
    if (!answered(q, answer)) return { id: q.id, type: q.type, earned: 0, max: POINTS, pending: false };
    const result = codeResults[q.id];
    if (!validCodeResult(q, answer, result)) return { id: q.id, type: q.type, earned: null, max: POINTS, pending: true };
    return { id: q.id, type: q.type, earned: POINTS * result.passed / result.total, max: POINTS, pending: false };
  });
  return {
    earned: rows.reduce((sum, x) => sum + (x.earned ?? 0), 0),
    graded_max: rows.filter(x => !x.pending).reduce((sum, x) => sum + x.max, 0),
    pending_max: rows.filter(x => x.pending).reduce((sum, x) => sum + x.max, 0),
    max: paper.length * POINTS, rows,
  };
}

export function restoreAttempt(bank, seed, raw) {
  const paper = buildPaper(bank, seed);
  const base = { schema_version: 1, bank_version: bank.version, week: bank.week, seed, started_at: new Date().toISOString(), answers: {}, code_results: {}, submitted_at: null };
  if (raw?.schema_version !== 1 || raw.bank_version !== bank.version || raw.seed !== seed || raw.week !== bank.week) return base;
  if (typeof raw.started_at === "string" && !Number.isNaN(Date.parse(raw.started_at))) base.started_at = raw.started_at;
  if (typeof raw.submitted_at === "string" && !Number.isNaN(Date.parse(raw.submitted_at))) base.submitted_at = raw.submitted_at;
  for (const q of paper) {
    const answer = sanitizeAnswer(q, raw.answers?.[q.id]);
    base.answers[q.id] = answer;
    if (q.type === "code" && validCodeResult(q, answer, raw.code_results?.[q.id])) base.code_results[q.id] = raw.code_results[q.id];
  }
  return base;
}
