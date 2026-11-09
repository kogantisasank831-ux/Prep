# Interview preparation navigation-state review record

## Component and contract

- Journey: move between the Roadmap, published weeks, and Interview Prep using the shared sidebar.
- Routes: the root roadmap, `/weeks/week-NN/`, and `/interview-prep/` descendants.
- Rendering: static HTML/Jekyll templates with shared `shell.js` URL-derived navigation state.
- Required behavior: exactly the current top-level content section carries the selected style and `aria-current="page"`.
- Review trigger: shared-navigation markup, routing, or active-state logic changes.

## Observed defect and cause

The Interview Prep template correctly marked its link active, but `shell.js` treated every route without a week number as the Roadmap. It therefore added the active class and `aria-current` to Roadmap after page load, leaving both controls selected.

## Implemented behavior

- stable `data-nav-section` identities distinguish Roadmap and Interview Prep links;
- Roadmap is active only when no week is selected and the pathname is not an Interview Prep route;
- the server-rendered Interview Prep state remains authoritative for Interview Prep descendants;
- a Node regression test covers roadmap, week, and Interview Prep paths;
- the existing interview-preparation content contract is now executed by CI.

## Evidence boundary and handoff

The automated tests verify state logic and markup contracts in a controlled runtime. Final confirmation still requires the exact merged GitHub Pages deployment and a post-deployment navigation check. Browser/device and assistive-technology conformance beyond the selected-state behavior were not claimed.
