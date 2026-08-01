"use strict";

const content = document.querySelector("#lesson-content");
const toc = document.querySelector("#lesson-toc");
const toggle = document.querySelector("#toc-toggle");
const progress = document.querySelector("#reading-progress");

if (content && toc) {
  const headings = [...content.querySelectorAll("h2, h3")];
  const fragment = document.createDocumentFragment();

  for (const heading of headings) {
    if (!heading.id) continue;
    const link = document.createElement("a");
    link.href = `#${heading.id}`;
    link.textContent = heading.textContent ?? "Section";
    link.dataset.level = heading.tagName.slice(1);
    link.addEventListener("click", () => {
      toc.classList.remove("open");
      toggle?.setAttribute("aria-expanded", "false");
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
  const open = toc?.classList.toggle("open") ?? false;
  toggle.setAttribute("aria-expanded", String(open));
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
updateReadingProgress();

