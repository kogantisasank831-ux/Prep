"use strict";

const content = document.querySelector("#lesson-content");
const toc = document.querySelector("#lesson-toc");
const toggle = document.querySelector("#toc-toggle");
const progress = document.querySelector("#reading-progress");
const sidebar = document.querySelector("#lesson-sidebar");
const applicationSidebar = document.querySelector("#app-sidebar");
const readModeToggle = document.querySelector("#read-mode-toggle");
const READ_MODE_STORAGE_KEY = "applied-genai-read-mode";

function setTocOpen(open) {
  toc?.classList.toggle("open", open);
  toggle?.setAttribute("aria-expanded", String(open));
  const icon = toggle?.querySelector("span[aria-hidden='true']");
  if (icon) icon.textContent = open ? "−" : "＋";
}

function setReadMode(enabled) {
  document.body.classList.toggle("lesson-read-mode-active", enabled);
  if (enabled) {
    document.body.classList.remove("app-nav-open");
    document.querySelector("[data-app-menu-toggle]")?.setAttribute("aria-expanded", "false");
  }
  readModeToggle?.setAttribute("aria-pressed", String(enabled));
  sidebar?.setAttribute("aria-hidden", String(enabled));
  if (applicationSidebar) {
    const applicationSidebarHidden = enabled || window.matchMedia("(max-width: 1099px)").matches;
    applicationSidebar.inert = applicationSidebarHidden;
    applicationSidebar.setAttribute("aria-hidden", String(applicationSidebarHidden));
  }
  const label = readModeToggle?.querySelector("[data-read-mode-label]");
  if (label) label.textContent = enabled ? "Show navigation" : "Read mode";
  if (readModeToggle) {
    readModeToggle.title = enabled ? "Restore lesson navigation" : "Hide navigation for focused reading";
  }
  if (enabled) {
    setTocOpen(false);
  }
  updateReadingProgress();
}

if (content && toc) {
  const headings = [...content.querySelectorAll("h2")];
  const fragment = document.createDocumentFragment();

  for (const heading of headings) {
    if (!heading.id) continue;
    const link = document.createElement("a");
    link.href = `#${heading.id}`;
    link.textContent = heading.textContent ?? "Section";
    link.dataset.level = heading.tagName.slice(1);
    link.addEventListener("click", () => {
      setTocOpen(false);
    });
    fragment.appendChild(link);
  }
  toc.appendChild(fragment);

  const links = [...toc.querySelectorAll("a")];
  const observer = new IntersectionObserver(
    (entries) => {
      const visible = entries.filter((entry) => entry.isIntersecting).at(-1);
      if (!visible) return;
      for (const link of links) {
        link.classList.toggle("active", link.hash === `#${visible.target.id}`);
      }
    },
    { rootMargin: "-15% 0px -75%", threshold: 0 },
  );
  for (const heading of headings) observer.observe(heading);
}

toggle?.addEventListener("click", () => {
  setTocOpen(!toc?.classList.contains("open"));
});

readModeToggle?.addEventListener("click", () => {
  const enabled = !document.body.classList.contains("lesson-read-mode-active");
  localStorage.setItem(READ_MODE_STORAGE_KEY, String(enabled));
  setReadMode(enabled);
});

function updateReadingProgress() {
  if (!content || !progress) return;
  const start = content.offsetTop;
  const distance = content.scrollHeight - window.innerHeight;
  const percent = distance <= 0 ? 100 : Math.min(100, Math.max(0, ((window.scrollY - start) / distance) * 100));
  progress.style.width = `${percent}%`;
}

window.addEventListener("scroll", updateReadingProgress, { passive: true });
window.addEventListener("resize", updateReadingProgress);
setReadMode(localStorage.getItem(READ_MODE_STORAGE_KEY) === "true");
updateReadingProgress();
