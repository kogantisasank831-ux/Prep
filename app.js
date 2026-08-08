"use strict";

const STORAGE_KEY = "applied-genai-roadmap-v1";
const PUBLISHED_WEEKS = new Set([1, 2, 3]);

/** @typedef {{ heading: string, body: string[] }} RoadmapSection */
/** @typedef {{ number: number, title: string, sections: RoadmapSection[], searchableText: string }} Week */
/** @typedef {{ number: number, title: string, optional: boolean, weeks: Week[] }} Phase */

const state = {
  phases: /** @type {Phase[]} */ ([]),
  activePhase: "all",
  query: "",
  completed: new Set(),
  notes: {},
};

function loadSavedState() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "{}");
    state.completed = new Set(Array.isArray(saved.completed) ? saved.completed : []);
    state.notes = saved.notes && typeof saved.notes === "object" ? saved.notes : {};
  } catch (error) {
    console.warn("Could not load saved roadmap state.", error);
  }
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({
    completed: [...state.completed],
    notes: state.notes,
  }));
}

/** @param {string} markdown @returns {Phase[]} */
function parseRoadmap(markdown) {
  const lines = markdown.replace(/\r/g, "").split("\n");
  const phases = [];
  let phase = null;
  let week = null;
  let section = null;

  for (const rawLine of lines) {
    const line = rawLine.trim();
    const phaseMatch = line.match(/^# (Optional )?Phase (\d+): (.+)$/);
    const weekMatch = line.match(/^## Week (\d+) — (.+)$/);
    const sectionMatch = line.match(/^### (.+)$/);

    if (phaseMatch) {
      phase = { number: Number(phaseMatch[2]), title: phaseMatch[3], optional: Boolean(phaseMatch[1]), weeks: [] };
      phases.push(phase);
      week = null;
      section = null;
    } else if (line.startsWith("# ")) {
      phase = null;
      week = null;
      section = null;
    } else if (weekMatch && phase) {
      week = { number: Number(weekMatch[1]), title: weekMatch[2], sections: [], searchableText: "" };
      phase.weeks.push(week);
      section = null;
    } else if (sectionMatch && week) {
      section = { heading: sectionMatch[1], body: [] };
      week.sections.push(section);
    } else if (week && line !== "---") {
      if (!section) {
        section = { heading: "Overview", body: [] };
        week.sections.push(section);
      }
      if (line) section.body.push(line);
    }
  }

  for (const parsedPhase of phases) {
    for (const parsedWeek of parsedPhase.weeks) {
      parsedWeek.searchableText = [parsedWeek.title, ...parsedWeek.sections.flatMap((item) => [item.heading, ...item.body])]
        .join(" ").toLowerCase();
    }
  }
  return phases;
}

/** @param {string} text */
function inlineMarkup(text) {
  const escaped = text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
  return escaped
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
}

/** @param {RoadmapSection[]} sections */
function renderSections(sections) {
  return sections.map(({ heading, body }) => {
    const chunks = [`<h5>${inlineMarkup(heading)}</h5>`];
    let listOpen = false;
    for (const line of body) {
      const bullet = line.match(/^\* (.+)$/);
      if (bullet) {
        if (!listOpen) chunks.push("<ul>");
        listOpen = true;
        chunks.push(`<li>${inlineMarkup(bullet[1])}</li>`);
      } else {
        if (listOpen) chunks.push("</ul>");
        listOpen = false;
        if (/^\d+\. /.test(line)) chunks.push(`<p>${inlineMarkup(line)}</p>`);
        else if (line.startsWith("> ")) chunks.push(`<blockquote>${inlineMarkup(line.slice(2))}</blockquote>`);
        else chunks.push(`<p>${inlineMarkup(line)}</p>`);
      }
    }
    if (listOpen) chunks.push("</ul>");
    return chunks.join("");
  }).join("");
}

/** @param {Week} week */
function getTags(week) {
  const learn = week.sections.find((section) => section.heading.toLowerCase() === "learn");
  const candidates = (learn?.body ?? []).filter((line) => line.startsWith("* ")).slice(0, 3);
  return candidates.map((line) => line.slice(2));
}

function updateProgress() {
  const total = state.phases.reduce((sum, phase) => sum + phase.weeks.length, 0);
  const complete = [...state.completed].filter((weekNumber) => Number(weekNumber) <= total).length;
  const percent = total ? Math.round((complete / total) * 100) : 0;
  document.querySelector("#completed-count").textContent = String(complete);
  document.querySelector("#total-count").textContent = String(total);
  document.querySelector("#progress-percent").textContent = `${percent}%`;
  document.querySelector("#progress-fill").style.width = `${percent}%`;
  const track = document.querySelector(".progress-track");
  track.setAttribute("aria-valuenow", String(percent));
  document.querySelector("#progress-message").textContent = percent === 100
    ? "Roadmap complete. Turn the work into a compelling story."
    : complete === 0 ? "Start with the foundations. Consistency compounds." : "Keep the cadence. Each build becomes portfolio evidence.";
}

function renderFilters() {
  const container = document.querySelector("#phase-filters");
  const options = [{ id: "all", label: "All phases" }, ...state.phases.map((phase) => ({ id: String(phase.number), label: `Phase ${phase.number}` }))];
  container.replaceChildren(...options.map(({ id, label }) => {
    const button = document.createElement("button");
    button.className = "filter";
    button.type = "button";
    button.textContent = label;
    button.setAttribute("aria-pressed", String(state.activePhase === id));
    button.addEventListener("click", () => {
      state.activePhase = id;
      renderFilters();
      renderRoadmap();
    });
    return button;
  }));
}

function renderRoadmap() {
  const phaseList = document.querySelector("#phase-list");
  const phaseTemplate = document.querySelector("#phase-template");
  const weekTemplate = document.querySelector("#week-template");
  const fragment = document.createDocumentFragment();
  let visibleWeeks = 0;

  for (const phase of state.phases) {
    if (state.activePhase !== "all" && state.activePhase !== String(phase.number)) continue;
    const matchingWeeks = phase.weeks.filter((week) => week.searchableText.includes(state.query));
    if (!matchingWeeks.length) continue;
    visibleWeeks += matchingWeeks.length;
    const phaseNode = phaseTemplate.content.cloneNode(true);
    phaseNode.querySelector(".phase-number").textContent = `${phase.optional ? "Optional " : ""}Phase ${phase.number}`;
    phaseNode.querySelector("h3").textContent = phase.title;
    const firstWeek = phase.weeks[0].number;
    const lastWeek = phase.weeks.at(-1).number;
    phaseNode.querySelector(".phase-range").textContent = `Weeks ${firstWeek}–${lastWeek}`;
    const weekGrid = phaseNode.querySelector(".week-grid");

    for (const week of matchingWeeks) {
      const weekNode = weekTemplate.content.cloneNode(true);
      const card = weekNode.querySelector(".week-card");
      const checkbox = weekNode.querySelector("input[type=checkbox]");
      const notes = weekNode.querySelector("textarea");
      const weeklyPlan = weekNode.querySelector("details");
      const weekId = String(week.number);
      card.dataset.week = weekId;
      card.classList.toggle("completed", state.completed.has(weekId));
      checkbox.checked = state.completed.has(weekId);
      checkbox.setAttribute("aria-label", `Mark week ${week.number} complete`);
      weekNode.querySelector(".week-number").textContent = `Week ${week.number}`;
      weekNode.querySelector("h4").textContent = week.title;
      weekNode.querySelector(".week-tags").replaceChildren(...getTags(week).map((tag) => {
        const item = document.createElement("span");
        item.textContent = tag;
        return item;
      }));
      weekNode.querySelector(".week-content").innerHTML = renderSections(week.sections);
      const lessonLink = weekNode.querySelector(".week-direct-link");
      if (PUBLISHED_WEEKS.has(week.number)) {
        lessonLink.href = `weeks/week-${String(week.number).padStart(2, "0")}/`;
        lessonLink.setAttribute("aria-label", `Open the full Week ${week.number} lesson`);
        lessonLink.hidden = false;
      }
      weeklyPlan.addEventListener("toggle", () => {
        card.classList.toggle("plan-open", weeklyPlan.open);
        for (const grid of document.querySelectorAll(".week-grid")) {
          grid.classList.toggle("plan-visible", grid.querySelector("details[open]") !== null);
        }
        if (weeklyPlan.open) {
          for (const openPlan of document.querySelectorAll("#phase-list details[open]")) {
            if (openPlan !== weeklyPlan) openPlan.open = false;
          }
        }
      });
      notes.value = state.notes[weekId] ?? "";
      checkbox.addEventListener("change", () => {
        checkbox.checked ? state.completed.add(weekId) : state.completed.delete(weekId);
        card.classList.toggle("completed", checkbox.checked);
        saveState();
        updateProgress();
      });
      notes.addEventListener("input", () => {
        state.notes[weekId] = notes.value;
        saveState();
      });
      weekGrid.appendChild(weekNode);
    }
    fragment.appendChild(phaseNode);
  }
  phaseList.replaceChildren(fragment);
  document.querySelector("#empty-state").hidden = visibleWeeks > 0;
}

async function initialise() {
  loadSavedState();
  try {
    const response = await fetch("Path.md");
    if (!response.ok) throw new Error(`Roadmap request failed with status ${response.status}.`);
    state.phases = parseRoadmap(await response.text());
    if (!state.phases.length) throw new Error("No roadmap phases were found in Path.md.");
    document.querySelector("#load-state").hidden = true;
    renderFilters();
    renderRoadmap();
    updateProgress();
  } catch (error) {
    console.error(error);
    document.querySelector("#load-state").textContent = "The roadmap could not be loaded. Serve this directory through a local web server or GitHub Pages.";
  }

  document.querySelector("#search").addEventListener("input", (event) => {
    state.query = event.target.value.trim().toLowerCase();
    renderRoadmap();
  });
  document.querySelector("#reset-progress").addEventListener("click", () => {
    if (!window.confirm("Reset all completed weeks and private notes?")) return;
    state.completed.clear();
    state.notes = {};
    saveState();
    renderRoadmap();
    updateProgress();
  });
}

initialise();
