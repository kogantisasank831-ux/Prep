import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import vm from "node:vm";

const shellSource = readFileSync(new URL("../shell.js", import.meta.url), "utf8");

function createClassList(initial = []) {
  const values = new Set(initial);
  return {
    add(...names) {
      for (const name of names) values.add(name);
    },
    contains(name) {
      return values.has(name);
    },
    toggle(name, force) {
      const enabled = force === undefined ? !values.has(name) : Boolean(force);
      if (enabled) values.add(name);
      else values.delete(name);
      return enabled;
    },
  };
}

function createLink() {
  const attributes = new Map();
  return {
    classList: createClassList(),
    getAttribute(name) {
      return attributes.get(name) ?? null;
    },
    removeAttribute(name) {
      attributes.delete(name);
    },
    setAttribute(name, value) {
      attributes.set(name, String(value));
    },
  };
}

function loadShell(pathname, hash = "") {
  const roadmapLink = createLink();
  const interviewPrepLink = createLink();
  const cheatSheetsLink = createLink();
  const bodyClassList = createClassList(["app-shell-page"]);
  const context = vm.createContext({
    URL,
    console,
    document: {
      body: { classList: bodyClassList },
      currentScript: { src: "https://example.test/Prep/shell.js" },
      addEventListener() {},
      querySelector(selector) {
        if (selector === '[data-nav-section="roadmap"]') return roadmapLink;
        if (selector === '[data-nav-section="interview-prep"]') return interviewPrepLink;
        if (selector === '[data-nav-section="cheat-sheets"]') return cheatSheetsLink;
        return null;
      },
      querySelectorAll() {
        return [];
      },
    },
    window: {
      addEventListener() {},
      location: { hash, pathname },
      matchMedia() {
        return {
          matches: true,
          addEventListener() {},
          addListener() {},
        };
      },
    },
  });
  vm.runInContext(shellSource, context, { filename: "shell.js" });
  return { context, roadmapLink, interviewPrepLink, cheatSheetsLink };
}

function updateNavigation(context) {
  vm.runInContext("updateActiveNavigation()", context);
}

test("Interview Prep is the only selected content section on interview routes", () => {
  const { context, roadmapLink, interviewPrepLink, cheatSheetsLink } = loadShell("/Prep/interview-prep/");
  updateNavigation(context);
  assert.equal(roadmapLink.classList.contains("active"), false);
  assert.equal(roadmapLink.getAttribute("aria-current"), null);
  assert.equal(interviewPrepLink.classList.contains("active"), true);
  assert.equal(interviewPrepLink.getAttribute("aria-current"), "page");
  assert.equal(cheatSheetsLink.classList.contains("active"), false);
  assert.equal(cheatSheetsLink.getAttribute("aria-current"), null);
});

test("Cheat Sheets is the only selected section on its hub", () => {
  const { context, roadmapLink, interviewPrepLink, cheatSheetsLink } = loadShell("/Prep/cheat-sheets/");
  updateNavigation(context);
  assert.equal(roadmapLink.classList.contains("active"), false);
  assert.equal(interviewPrepLink.classList.contains("active"), false);
  assert.equal(cheatSheetsLink.classList.contains("active"), true);
  assert.equal(cheatSheetsLink.getAttribute("aria-current"), "page");
});

test("Cheat Sheets remains selected for legacy nested sheet routes", () => {
  const { context, roadmapLink, interviewPrepLink, cheatSheetsLink } = loadShell(
    "/Prep/interview-prep/cheat-sheets/python/",
  );
  updateNavigation(context);
  assert.equal(roadmapLink.classList.contains("active"), false);
  assert.equal(interviewPrepLink.classList.contains("active"), false);
  assert.equal(cheatSheetsLink.classList.contains("active"), true);
  assert.equal(cheatSheetsLink.getAttribute("aria-current"), "page");
});

test("Roadmap remains selected on the roadmap route", () => {
  const { context, roadmapLink, interviewPrepLink, cheatSheetsLink } = loadShell("/Prep/");
  updateNavigation(context);
  assert.equal(roadmapLink.classList.contains("active"), true);
  assert.equal(roadmapLink.getAttribute("aria-current"), "page");
  assert.equal(interviewPrepLink.classList.contains("active"), false);
  assert.equal(cheatSheetsLink.classList.contains("active"), false);
});

test("Roadmap is not selected on a published week route", () => {
  const { context, roadmapLink, interviewPrepLink, cheatSheetsLink } = loadShell("/Prep/weeks/week-30/");
  updateNavigation(context);
  assert.equal(roadmapLink.classList.contains("active"), false);
  assert.equal(roadmapLink.getAttribute("aria-current"), null);
  assert.equal(interviewPrepLink.classList.contains("active"), false);
  assert.equal(cheatSheetsLink.classList.contains("active"), false);
});
