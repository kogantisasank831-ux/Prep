---
week: 2
phase: 1
status: approved
version: 1.1.0
last_reviewed: 2026-10-22
generation_surface: Codex in ChatGPT Work
publication_authorization: User requested Week 2 within the established explicitly approved create-check-push-publish workflow
---

# Week 2 content refresh review

## Scope and authorization

Repository `kogantisasank831-ux/Prep`, main baseline
`cb96eb6275656bf8cd097d0f730748c5a58eeec8`, tree
`c381e23757bd355f1e49b757502279e28d747586`. Work used
`week02-refresh` after fetching `origin/main`. The sole applicable instruction
file is root `AGENTS.md`; this curriculum repository has no `Design/` directory.
Existing untracked Week 4–9 QA directories were preserved.

The user explicitly requested Week 2. This revisits the existing SQL and data
modelling lessons rather than advancing to Week 10. Publication follows the
previously authorized direct push and Pages workflow. Approval metadata records
that authorization, not an invented independent human pedagogical assessment.
The August technical review remains unchanged as historical evidence; its old
pending-publication statement predates the user's publication authorization.

Inspected the Week 2 roadmap and outline, both complete lessons, lab README,
the six SQL sources, the existing technical review, the shared layout/config,
and repository dependency/validation conventions. Only four documentation files
change: both lessons, the lab README and this review. No application, SQL,
schema, dependency, navigation or other week changes are included.

## Learner-facing changes

- Both lessons gain publication metadata and an eight-hour route connecting
  grains/keys, joins/aggregation/dates, CTEs/subqueries/windows, indexes,
  normalization and transaction reasoning to the five procurement outputs.
- The main lesson adds concise answers to its fourteen existing recall questions.
  Its eight medium SQL and two product-analytics exercises and complete interview
  section remain intact.
- The beginner lesson adds six small exercises, six spoken recall prompts and a
  concrete handoff. Every original section remains verbatim.
- The standalone README now pulls and inspects the existing pinned image before
  `--pull=never`, explains prerequisites, maps the six-script execution order,
  gives expected cutoff quantities and distinguishes single-session assertions
  from the separately recorded concurrent tests.

Two main-lesson statements are corrected against existing evidence. The recorded
race used a fresh 130 kg order and ended with 100 kg accepted, rather than the
previous claim of 970 kg on the story's order. `PO-1042` has only 870 kg accepted
at the June 30 analytical cutoff, while the full seed includes the July 5 receipt
that completes its 1,000 kg order. A reporting cutoff cannot free capacity for a
write against the fully loaded database.

The functions use the default `SECURITY INVOKER` behavior. Revoking the caller's
table writes would also prevent those functions from writing. The lesson now
matches the README and historical review: the shared locking protocol does not
establish a production authorization boundary. No role/security design changed.

## Validation executed for this refresh

Environment: Linux, Python 3.12; local structural preview uses Markdown 3.11.2,
python-liquid 2.3.5 and PyYAML 6.0.3. These are QA environment dependencies only;
repository requirements are unchanged.

| Check | Result |
| --- | --- |
| Existing fenced blocks | All 30 main and 11 beginner blocks preserved exactly, in order |
| Existing source URLs | Every original HTTP/HTTPS source URL retained |
| Existing learning material | Main exercises, interview section and all fourteen recall prompts preserved; every original beginner section preserved |
| Front matter | Week/phase/version/status/hours and existing permalinks valid |
| Markdown/Liquid structural rendering | Both lessons rendered through the existing layout; main 57 sections/4 tables, beginner 18 sections/1 table |
| HTML structure and internal targets | One H1 per page, no duplicate IDs or unresolved templates; alternate lesson/assets/SQL targets resolve |
| Lab setup order | Pull precedes `podman run --pull=never`; six SQL scripts retain their existing execution order |
| SQL preservation | All six SQL files byte-identical to the baseline |
| Independent arithmetic | `(1000 - 870) * 12 = 1560`; `400 + 470 + 130 = 1000` using Decimal |

Candidate checks ran before canonical integration. Final diff/whitespace and
commit-tree integrity checks run before publication. The hosted Pages build and
live main/beginner responses are checked after the push and reported in the
handoff. Local structural previews are not a Ruby/Jekyll build or visual browser
inspection.

## Source and execution limits

Checked official PostgreSQL 18 documentation for function invocation security,
explicit locking and window functions, and the Podman pull reference for
digest-based image pulls. Existing primary links remain in the lessons; the
README adds the official pull reference.

- https://www.postgresql.org/docs/18/sql-createfunction.html
- https://www.postgresql.org/docs/18/explicit-locking.html
- https://www.postgresql.org/docs/18/functions-window.html
- https://docs.podman.io/en/latest/markdown/podman-pull.1.html

No fresh PostgreSQL/container execution occurred in this documentation pass:
`psql`, `postgres`, `podman` and `docker` are unavailable on PATH. SQL files and
the previously reviewed image pin are unchanged. The PostgreSQL 18.4 execution,
negative-path checks, two-session races and environment-specific index results
remain attributed to `week-02-technical-review.md` dated 2026-08-08. They are not
presented as newly executed results or production guarantees.

To repeat that runtime verification, use the README's pinned-image PowerShell
commands from the repository root, apply all six scripts with `psql -X` and
`ON_ERROR_STOP=1`, and inspect the final assertion. Concurrent acceptance and
cancellation checks require separate sessions and dedicated fresh fixtures;
`90_verify.sql` does not run them automatically. No Python application behavior
changed, so the application test suite was not rerun for this refresh.
