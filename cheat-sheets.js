"use strict";

const CHEAT_SHEET_STORAGE_KEY = "applied-genai-cheat-sheets-v1";

/** @param {string} value @returns {string} */
function normaliseText(value) {
  return value.trim().toLocaleLowerCase().replace(/\s+/g, " ");
}

/** @param {string} href @param {string} baseHref @returns {string} */
function getSheetId(href, baseHref) {
  try {
    const parts = new URL(href, baseHref).pathname.split("/").filter(Boolean);
    return parts.at(-1) ?? "";
  } catch {
    return "";
  }
}

/** @param {Storage} storage @returns {Set<string>} */
function loadCompleted(storage) {
  try {
    const saved = JSON.parse(storage.getItem(CHEAT_SHEET_STORAGE_KEY) ?? "{}");
    if (!Array.isArray(saved.completed)) return new Set();
    return new Set(saved.completed.filter((item) => typeof item === "string" && item.length > 0));
  } catch (error) {
    console.warn("Could not load cheat-sheet progress.", error);
    return new Set();
  }
}

/** @param {Set<string>} completed @param {Storage} storage @returns {boolean} */
function saveCompleted(completed, storage) {
  try {
    storage.setItem(CHEAT_SHEET_STORAGE_KEY, JSON.stringify({ completed: [...completed].sort() }));
    return true;
  } catch (error) {
    console.warn("Could not save cheat-sheet progress.", error);
    return false;
  }
}

/**
 * @typedef {{ id: string, batch: string, searchText: string }} FilterableSheet
 */

/**
 * @param {FilterableSheet} sheet
 * @param {string} query
 * @param {string} batch
 * @param {string} progressState
 * @param {Set<string>} completed
 * @returns {boolean}
 */
function sheetMatches(sheet, query, batch, progressState, completed) {
  const matchesQuery = sheet.searchText.includes(normaliseText(query));
  const matchesBatch = batch === "all" || sheet.batch === batch;
  const isComplete = completed.has(sheet.id);
  const matchesProgress = progressState === "all"
    || (progressState === "complete" && isComplete)
    || (progressState === "incomplete" && !isComplete);
  return matchesQuery && matchesBatch && matchesProgress;
}

function initialiseCheatSheetHub() {
  const tools = document.querySelector("[data-cheat-sheet-tools]");
  const content = document.querySelector("#lesson-content");
  const search = document.querySelector("#cheat-sheet-search");
  const batchFilter = document.querySelector("#cheat-sheet-batch");
  const progressFilter = document.querySelector("#cheat-sheet-progress-filter");
  const clearFilters = document.querySelector("#clear-cheat-sheet-filters");
  const resetProgress = document.querySelector("#reset-cheat-sheet-progress");
  const progress = document.querySelector("#cheat-sheet-progress");
  const progressTitle = document.querySelector("#cheat-sheet-progress-title");
  const filterStatus = document.querySelector("#cheat-sheet-filter-status");
  const emptyState = document.querySelector("#cheat-sheet-empty");
  const filterForm = document.querySelector("[data-cheat-sheet-filters]");

  if (!(tools instanceof HTMLElement)
      || !(content instanceof HTMLElement)
      || !(search instanceof HTMLInputElement)
      || !(batchFilter instanceof HTMLSelectElement)
      || !(progressFilter instanceof HTMLSelectElement)
      || !(clearFilters instanceof HTMLButtonElement)
      || !(resetProgress instanceof HTMLButtonElement)
      || !(progress instanceof HTMLProgressElement)
      || !(progressTitle instanceof HTMLElement)
      || !(filterStatus instanceof HTMLElement)
      || !(emptyState instanceof HTMLElement)
      || !(filterForm instanceof HTMLFormElement)) return;

  const completed = loadCompleted(window.localStorage);
  const sheets = [];
  const groups = [];
  const batchHeadings = [...content.querySelectorAll("h2")]
    .filter((heading) => /^Batch \d+\b/.test(heading.textContent?.trim() ?? ""));

  for (const heading of batchHeadings) {
    const batchMatch = heading.textContent?.trim().match(/^Batch (\d+)\b/);
    const table = heading.nextElementSibling;
    if (!batchMatch || !(table instanceof HTMLTableElement)) continue;

    const batch = batchMatch[1];
    const headerRow = table.tHead?.rows[0];
    if (headerRow) {
      const progressHeader = document.createElement("th");
      progressHeader.scope = "col";
      progressHeader.textContent = "Revision";
      headerRow.append(progressHeader);
    }

    const groupSheets = [];
    for (const row of table.tBodies[0]?.rows ?? []) {
      const link = row.querySelector("a[href*='/interview-prep/cheat-sheets/']");
      const cells = row.querySelectorAll("td");
      if (!(link instanceof HTMLAnchorElement) || cells.length < 2) continue;

      const id = getSheetId(link.href, window.location.href);
      if (!id) continue;
      const title = link.textContent?.trim() ?? "Cheat sheet";
      const searchText = normaliseText(`${heading.textContent ?? ""} ${title} ${cells[1].textContent ?? ""}`);
      const progressCell = document.createElement("td");
      const label = document.createElement("label");
      const checkbox = document.createElement("input");
      const labelText = document.createElement("span");

      progressCell.className = "cheat-sheet-progress-cell";
      label.className = "cheat-sheet-progress-control";
      checkbox.type = "checkbox";
      checkbox.checked = completed.has(id);
      checkbox.setAttribute("aria-label", `Mark ${title} as revised`);
      labelText.textContent = "Revised";
      label.append(checkbox, labelText);
      progressCell.append(label);
      row.append(progressCell);

      const sheet = { id, batch, searchText, row, checkbox };
      sheets.push(sheet);
      groupSheets.push(sheet);

      checkbox.addEventListener("change", () => {
        if (checkbox.checked) completed.add(id);
        else completed.delete(id);
        saveCompleted(completed, window.localStorage);
        render();
      });
    }

    const tocLink = [...document.querySelectorAll("#lesson-toc a")]
      .find((link) => link.hash === `#${heading.id}`);
    groups.push({ heading, table, sheets: groupSheets, tocLink });
  }

  function updateProgress() {
    const completedCount = sheets.filter((sheet) => completed.has(sheet.id)).length;
    progress.max = sheets.length;
    progress.value = completedCount;
    progress.textContent = `${completedCount} of ${sheets.length} revised`;
    progressTitle.textContent = `${completedCount} of ${sheets.length} revised`;
    resetProgress.disabled = completedCount === 0;
    for (const sheet of sheets) {
      const isComplete = completed.has(sheet.id);
      sheet.checkbox.checked = isComplete;
      sheet.row.classList.toggle("cheat-sheet-row-complete", isComplete);
    }
  }

  function applyFilters() {
    const query = search.value;
    let visibleCount = 0;
    for (const group of groups) {
      let visibleInGroup = 0;
      for (const sheet of group.sheets) {
        const visible = sheetMatches(sheet, query, batchFilter.value, progressFilter.value, completed);
        sheet.row.hidden = !visible;
        if (visible) visibleInGroup += 1;
      }
      const groupHidden = visibleInGroup === 0;
      group.heading.hidden = groupHidden;
      group.table.hidden = groupHidden;
      if (group.tocLink instanceof HTMLElement) group.tocLink.hidden = groupHidden;
      visibleCount += visibleInGroup;
    }

    const filtered = normaliseText(query) !== ""
      || batchFilter.value !== "all"
      || progressFilter.value !== "all";
    filterStatus.textContent = filtered
      ? `Showing ${visibleCount} of ${sheets.length} cheat sheets.`
      : `Showing all ${sheets.length} cheat sheets.`;
    emptyState.hidden = visibleCount !== 0;
    clearFilters.disabled = !filtered;
  }

  function render() {
    updateProgress();
    applyFilters();
  }

  filterForm.addEventListener("submit", (event) => event.preventDefault());
  search.addEventListener("input", applyFilters);
  batchFilter.addEventListener("change", applyFilters);
  progressFilter.addEventListener("change", applyFilters);
  clearFilters.addEventListener("click", () => {
    search.value = "";
    batchFilter.value = "all";
    progressFilter.value = "all";
    applyFilters();
    search.focus();
  });
  resetProgress.addEventListener("click", () => {
    if (!window.confirm("Reset revision progress for all cheat sheets?")) return;
    completed.clear();
    saveCompleted(completed, window.localStorage);
    render();
  });
  window.addEventListener("storage", (event) => {
    if (event.key !== CHEAT_SHEET_STORAGE_KEY) return;
    completed.clear();
    for (const id of loadCompleted(window.localStorage)) completed.add(id);
    render();
  });

  tools.hidden = false;
  render();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initialiseCheatSheetHub);
} else {
  initialiseCheatSheetHub();
}
