"""Validate structural and publication-hygiene rules for the Week 1 lesson."""

from __future__ import annotations

import re
import sys
from pathlib import Path


PRODUCTION_HEADINGS = (
    "The service we are building",
    "From one route to deliberate design",
    "Classes should earn their place",
    "Types inside, validation at the boundary",
    "Model trusted state explicitly",
    "Make failures part of the design",
    "Observe behavior without leaking data",
    "Laziness, concurrency and resource lifetime",
    "Assemble the FastAPI boundary",
    "Prove the behavior with tests",
    "Practice and interview lab",
    "References",
)

BEGINNER_HEADINGS = (
    "What are we trying to build?",
    "Follow one request through the system",
    "Functions and classes solve different problems",
    "Types describe intent; validation checks reality",
    "Dataclasses represent trusted internal values",
    "Interfaces make dependencies replaceable",
    "Fail clearly and log safely",
    "Generators and async are choices, not upgrades",
    "Test behavior at each boundary",
    "You are ready for the production version",
)

FLOW_V2_HEADINGS = (
    "A dependable answer to one small question",
    "1. Begin with a transformation that has no hidden state",
    "2. Put state and responsibility where they belong",
    "3. Let type hints state intent, not pretend to police the boundary",
    "4. Validate untrusted values at the runtime boundary",
    "5. Carry trusted internal values as values",
    "6. Isolate strict decoding behind a small adapter",
    "7. Give failures a stable vocabulary",
    "8. Produce operational evidence without leaking the document",
    "9. Learn generators without smuggling in concurrency",
    "10. Choose concurrency from the work that actually waits",
    "11. Assemble the HTTP boundary after the domain is familiar",
    "12. Prove behavior in the same order it was built",
    "13. The complete request and failure traces",
    "14. Mistakes that make this service less dependable",
    "15. Exercises: extend the contract without dissolving it",
    "16. Mini-project: an extraction review queue",
    "17. Deeper practical checkpoints",
    "18. Interview practice: defend the trade-offs",
    "19. Active recall and knowledge check",
    "Where this foundation leads",
    "Primary documentation",
)

FORBIDDEN_PUBLIC_PHRASES = (
    "VERIFIED_EXCERPT",
    "technical review passed",
    "human review passed",
    "publication status",
    "review history",
    "approved outline",
    "weekly deliverables",
    "ChatGPT",
    "Codex",
    "HITL",
)


def main() -> int:
    path = Path(
        sys.argv[1]
        if len(sys.argv) > 1
        else "content/reviewed/week-01-public-review-candidate.md"
    )
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    front_matter = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if front_matter is None:
        errors.append("valid YAML front matter was not found")
    else:
        for required in ("layout: week", "permalink: /weeks/week-01/", "title:"):
            if required not in front_matter.group(1):
                errors.append(f"front matter is missing {required!r}")
        for internal_field in ("status", "technical_review", "human_review"):
            if re.search(
                rf"(?m)^{re.escape(internal_field)}\s*:",
                front_matter.group(1),
            ):
                errors.append(f"internal front-matter field leaked: {internal_field!r}")

    is_beginner = "permalink: /weeks/week-01/beginner/" in text
    is_flow_v2 = "## 1. Begin with a transformation that has no hidden state" in text
    expected_headings = (
        BEGINNER_HEADINGS
        if is_beginner
        else FLOW_V2_HEADINGS
        if is_flow_v2
        else PRODUCTION_HEADINGS
    )
    minimum_words = 1_500 if is_beginner else 8_000

    headings = tuple(re.findall(r"(?m)^## (.+)$", text))
    if headings != expected_headings:
        errors.append("top-level lesson headings differ from the reviewed structure")

    if is_flow_v2:
        sections = {
            match.group(1): match.group(2)
            for match in re.finditer(
                r"(?ms)^## (.+?)\n(.*?)(?=^## |\Z)",
                text,
            )
        }
        for heading in FLOW_V2_HEADINGS[1:13]:
            body = sections.get(heading, "")
            for marker in ("### Question:", "**Boundary.**", "**Checkpoint.**"):
                if marker not in body:
                    errors.append(f"{heading!r} is missing flow marker {marker!r}")

        ordered_markers = (
            "## 9. Learn generators without smuggling in concurrency",
            "## 10. Choose concurrency from the work that actually waits",
            "## 11. Assemble the HTTP boundary after the domain is familiar",
            "## 13. The complete request and failure traces",
        )
        positions = tuple(text.find(marker) for marker in ordered_markers)
        if any(position < 0 for position in positions) or positions != tuple(
            sorted(positions)
        ):
            errors.append("concept dependency order is invalid")

        for label in (
            "Repository excerpt:",
            "Illustrative code; not executed here.",
            "Repository-shaped example; not executed here.",
        ):
            if label in text:
                errors.append(f"learner-facing provenance label remains: {label!r}")

    lower_text = text.casefold()
    for phrase in FORBIDDEN_PUBLIC_PHRASES:
        if phrase.casefold() in lower_text:
            errors.append(f"internal phrase leaked into public content: {phrase!r}")

    fence_count = len(re.findall(r"(?m)^```", text))
    if fence_count % 2:
        errors.append("code fences are unbalanced")

    word_count = len(re.findall(r"\b[\w'-]+\b", text))
    if word_count < minimum_words:
        errors.append(f"lesson unexpectedly shrank to {word_count} words")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(
        f"PASS: {path} has {word_count} words, {len(headings)} chapters, "
        f"and {fence_count // 2} fenced examples"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
