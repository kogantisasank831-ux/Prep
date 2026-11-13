import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import vm from "node:vm";

const source = readFileSync(new URL("../cheat-sheets.js", import.meta.url), "utf8");

function createStorage(savedValue = null) {
  const values = new Map();
  if (savedValue !== null) values.set("applied-genai-cheat-sheets-v1", savedValue);
  return {
    getItem(key) {
      return values.get(key) ?? null;
    },
    setItem(key, value) {
      values.set(key, String(value));
    },
    values,
  };
}

function loadScript(savedValue = null) {
  const storage = createStorage(savedValue);
  const window = {
    localStorage: storage,
    location: { href: "https://example.test/Prep/cheat-sheets/" },
    addEventListener() {},
  };
  const context = vm.createContext({
    URL,
    console: { warn() {} },
    document: {
      readyState: "loading",
      addEventListener() {},
    },
    localStorage: storage,
    window,
  });
  vm.runInContext(source, context, { filename: "cheat-sheets.js" });
  return { context, storage };
}

function evaluateJson(context, expression) {
  return JSON.parse(vm.runInContext(`JSON.stringify(${expression})`, context));
}

test("sheet IDs are stable across the GitHub Pages base path", () => {
  const { context } = loadScript();
  assert.equal(
    vm.runInContext(
      'getSheetId("/Prep/interview-prep/cheat-sheets/rag-evaluation-security-production/", window.location.href)',
      context,
    ),
    "rag-evaluation-security-production",
  );
  assert.equal(vm.runInContext('getSheetId("::bad-url", "::bad-base")', context), "");
});

test("saved completion state is validated and deduplicated", () => {
  const { context } = loadScript('{"completed":["python","sql","python",42,null]}');
  assert.deepEqual(evaluateJson(context, "[...loadCompleted(localStorage)].sort()"), ["python", "sql"]);

  const malformed = loadScript("not-json");
  assert.deepEqual(evaluateJson(malformed.context, "[...loadCompleted(localStorage)]"), []);
});

test("completion state is stored in deterministic order", () => {
  const { context, storage } = loadScript();
  assert.equal(vm.runInContext("saveCompleted(new Set(['sql', 'python']), localStorage)", context), true);
  assert.equal(
    storage.values.get("applied-genai-cheat-sheets-v1"),
    '{"completed":["python","sql"]}',
  );
});

test("search, batch, and progress filters compose", () => {
  const { context } = loadScript();
  const sheet = '{id:"rag-security",batch:"3",searchText:"batch 3 rag security evaluation"}';
  assert.equal(vm.runInContext(`sheetMatches(${sheet}, "SECURITY", "3", "incomplete", new Set())`, context), true);
  assert.equal(vm.runInContext(`sheetMatches(${sheet}, "security", "2", "all", new Set())`, context), false);
  assert.equal(
    vm.runInContext(`sheetMatches(${sheet}, "rag", "3", "complete", new Set(["rag-security"]))`, context),
    true,
  );
  assert.equal(vm.runInContext(`sheetMatches(${sheet}, "sql", "all", "all", new Set())`, context), false);
});
