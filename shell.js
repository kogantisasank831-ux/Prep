"use strict";

window.PUBLISHED_WEEKS = new Set([1, 2, 3, 4, 5, 6, 7]);

const shellScriptUrl = new URL(document.currentScript.src);
const roadmapBasePath = shellScriptUrl.pathname.replace(/\/shell\.js$/, "");
const shellSidebar = document.querySelector("#app-sidebar");
const shellOverlay = document.querySelector("#app-overlay");
const shellToggles = [...document.querySelectorAll("[data-app-menu-toggle]")];
const weekNavigation = document.querySelector("#app-week-navigation");
const contentNavigationLink = document.querySelector(".app-content-link");
const desktopQuery = window.matchMedia("(min-width: 1100px)");

function setApplicationMenuOpen(open) {
  const readingModeActive = document.body.classList.contains("lesson-read-mode-active");
  const mobileOpen = !readingModeActive && !desktopQuery.matches && open;
  document.body.classList.toggle("app-nav-open", mobileOpen);
  for (const toggle of shellToggles) toggle.setAttribute("aria-expanded", String(mobileOpen));
  if (shellSidebar) {
    const sidebarHidden = readingModeActive || (!desktopQuery.matches && !mobileOpen);
    shellSidebar.inert = sidebarHidden;
    shellSidebar.setAttribute("aria-hidden", String(sidebarHidden));
  }
}

for (const toggle of shellToggles) {
  toggle.addEventListener("click", () => {
    setApplicationMenuOpen(!document.body.classList.contains("app-nav-open"));
  });
}

shellOverlay?.addEventListener("click", () => setApplicationMenuOpen(false));
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") setApplicationMenuOpen(false);
});

const handleDesktopChange = () => {
  setApplicationMenuOpen(false);
};
if (typeof desktopQuery.addEventListener === "function") desktopQuery.addEventListener("change", handleDesktopChange);
else desktopQuery.addListener(handleDesktopChange);

/** @param {string} markdown */
function parseWeekNavigation(markdown) {
  const weeks = [];
  for (const rawLine of markdown.replace(/\r/g, "").split("\n")) {
    const match = rawLine.trim().match(/^## Week (\d+) — (.+)$/);
    if (match) weeks.push({ number: Number(match[1]), title: match[2] });
  }
  return weeks;
}

function currentWeekNumber() {
  const pathMatch = window.location.pathname.match(/\/weeks\/week-(\d+)\//);
  if (pathMatch) return Number(pathMatch[1]);
  const hashMatch = window.location.hash.match(/^#week-(\d+)$/);
  return hashMatch ? Number(hashMatch[1]) : null;
}

function updateActiveNavigation() {
  const activeWeek = currentWeekNumber();
  contentNavigationLink?.classList.toggle("active", activeWeek === null);
  if (contentNavigationLink) {
    if (activeWeek === null) contentNavigationLink.setAttribute("aria-current", "page");
    else contentNavigationLink.removeAttribute("aria-current");
  }
  for (const link of weekNavigation?.querySelectorAll(".app-week-link") ?? []) {
    const active = Number(link.dataset.week) === activeWeek;
    link.classList.toggle("active", active);
    if (active) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  }
}

/** @param {{ number: number, title: string }} week */
function createWeekNavigationItem(week) {
  const published = window.PUBLISHED_WEEKS.has(week.number);
  const paddedWeek = String(week.number).padStart(2, "0");
  const link = document.createElement("a");
  link.className = "app-nav-link app-week-link";
  link.dataset.week = String(week.number);
  link.href = published
    ? `${roadmapBasePath}/weeks/week-${paddedWeek}/`
    : `${roadmapBasePath}/#week-${week.number}`;
  link.setAttribute("aria-label", published ? `Open the Week ${week.number} lesson` : `View the Week ${week.number} plan in the roadmap`);
  if (!published) link.classList.add("upcoming");

  const number = document.createElement("span");
  number.className = "app-week-number";
  number.textContent = `Week ${week.number}`;
  const title = document.createElement("span");
  title.className = "app-week-title";
  title.textContent = week.title;
  link.append(number, title);
  link.addEventListener("click", () => setApplicationMenuOpen(false));
  return link;
}

async function initialiseApplicationNavigation() {
  if (!weekNavigation) return;
  try {
    const response = await fetch(`${roadmapBasePath}/Path.md`);
    if (!response.ok) throw new Error(`Navigation request failed with status ${response.status}.`);
    const weeks = parseWeekNavigation(await response.text());
    weekNavigation.replaceChildren(...weeks.map(createWeekNavigationItem));
    updateActiveNavigation();
  } catch (error) {
    console.error(error);
    weekNavigation.textContent = "Week navigation is unavailable.";
  }
}

shellSidebar?.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => setApplicationMenuOpen(false));
});

setApplicationMenuOpen(false);
window.addEventListener("hashchange", updateActiveNavigation);
initialiseApplicationNavigation();
