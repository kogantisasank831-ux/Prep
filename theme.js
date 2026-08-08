"use strict";

const THEME_STORAGE_KEY = "applied-genai-theme";
const root = document.documentElement;

function preferredTheme() {
  const saved = localStorage.getItem(THEME_STORAGE_KEY);
  if (saved === "light" || saved === "dark") return saved;
  return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
}

function applyTheme(theme) {
  const isLight = theme === "light";
  root.dataset.theme = theme;
  root.style.colorScheme = theme;
  document.querySelector('meta[name="theme-color"]')?.setAttribute("content", isLight ? "#f4f7fb" : "#07101d");

  for (const button of document.querySelectorAll(".theme-toggle")) {
    const nextTheme = isLight ? "dark" : "light";
    button.setAttribute("aria-label", `Switch to ${nextTheme} mode`);
    button.setAttribute("title", `Switch to ${nextTheme} mode`);
    button.setAttribute("aria-pressed", String(isLight));
    const icon = button.querySelector("[data-theme-icon]");
    const label = button.querySelector("[data-theme-label]");
    if (icon) icon.textContent = isLight ? "☾" : "☀";
    if (label) label.textContent = isLight ? "Dark" : "Light";
  }
}

applyTheme(preferredTheme());

document.addEventListener("DOMContentLoaded", () => {
  applyTheme(root.dataset.theme || preferredTheme());
  for (const button of document.querySelectorAll(".theme-toggle")) {
    button.addEventListener("click", () => {
      const nextTheme = root.dataset.theme === "light" ? "dark" : "light";
      localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
      applyTheme(nextTheme);
    });
  }
});
