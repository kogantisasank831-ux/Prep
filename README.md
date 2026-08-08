# Applied GenAI Roadmap

A static learning roadmap for the 30-week curriculum in [`Path.md`](Path.md).
The dashboard is dependency-free; GitHub Pages uses its native Jekyll build to
render approved weekly Markdown lessons. The site provides responsive sidebar
navigation, phase filtering, full-text search, light/dark and focused reading
modes, weekly completion tracking, and private browser-local notes.

## Run locally

The site loads `Path.md` with `fetch`, so it must be served over HTTP rather than
opened directly from the filesystem.

```powershell
python -m http.server 8000
```

Open <http://localhost:8000>.

## Publish with GitHub Pages

1. Push the repository to GitHub.
2. In **Settings → Pages**, select **Deploy from a branch**.
3. Select the repository's default branch and the `/ (root)` folder.
4. Save and open the published URL after the deployment completes.

GitHub Pages runs the Jekyll build automatically. Progress and notes are stored in
`localStorage`, so they remain specific to the current browser and device.

## Content workflow

`Path.md` is the source of truth. Keep phase headings in the form
`# Phase N: Title`, week headings as `## Week N — Title`, and subsection headings
as `### Title`. Changes that follow this structure appear automatically on the
website after refresh.

Approved detailed lessons live in `content/weeks/` with `layout: week` and a
stable permalink. Add the week number to `PUBLISHED_WEEKS` in `shell.js` only after
technical and human review pass.

The Python HTTP server can preview the dashboard shell, but it does not execute
Jekyll and therefore cannot render weekly Markdown pages. Use GitHub Pages or a
local Ruby/Jekyll installation for a complete preview.
