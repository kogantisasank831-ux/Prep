# Interview preparation Batch 1 review record

## Scope

Batch 1 creates a separate interview-preparation surface without changing the Week 1–20 lessons, labs, assessment banks, scoring, or question-selection behavior.

Public candidates:

- interview-prep hub and master syllabus;
- four core cheat sheets: Python, SQL, probability/statistics, and ML fundamentals;
- three role-specific banks with 20 stable questions each;
- shared navigation from the roadmap and lesson layout.

## Audience and purpose

| Artifact | Audience | Task |
| --- | --- | --- |
| Cheat sheets | Experienced Data Scientist / ML Engineer | Rapid recall with formulas, traps, code patterns, and production trade-offs |
| Role banks | Candidate targeting the named role | Practise spoken decisions, follow-up probes, and project evidence |
| Weekly assessments | Learner following Weeks 1–20 | Verify understanding of taught lesson material |

The role banks are not psychometrically calibrated, authenticated exams, or claims about a specific company's interview process.

## Source identity

The master index and four cheat sheets use the existing artifacts dated 8–9 November 2026. Integration removes only each source document's duplicate top-level heading and adds Jekyll metadata plus a source note; the instructional body remains unchanged.

## Structural decisions

- Reuse the existing `week` layout and reading-mode behavior through metadata rather than adding a second near-duplicate layout.
- Parameterize the shared layout with defaults so existing lessons and assessments keep their current labels and links.
- Use Markdown role banks for the first batch. Stable question IDs preserve a path to JSON/random-paper support after the content model is reviewed.
- Keep all interview content below `/interview-prep/` and add explicit navigation rather than mixing it into the weekly roadmap parser.

## Validation contract

- all nine public pages have unique stable permalinks and required front matter;
- each role bank has exactly 20 sequential unique IDs, 20 signal blocks, and 20 follow-up probes;
- the four cheat sheets retain their rapid-revision section;
- the hub links every public artifact;
- both roadmap and shared lesson navigation link to the hub;
- existing weekly assessment files are untouched.

## Review status

Technical structure is a review candidate. Human review should confirm role fit, answer depth, and prioritization before changing the public status from `review` to `approved` and merging.
