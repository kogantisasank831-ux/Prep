"""Validate structural and publication-hygiene rules for the Week 1 lesson."""

from __future__ import annotations

import re
import sys
from pathlib import Path


EXPECTED_HEADINGS = (
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

FORBIDDEN_PUBLIC_PHRASES = (
    "VERIFIED_EXCERPT",
    "technical review",
    "human review",
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

    headings = tuple(re.findall(r"(?m)^## (.+)$", text))
    if headings != EXPECTED_HEADINGS:
        errors.append("top-level lesson headings differ from the reviewed structure")

    lower_text = text.casefold()
    for phrase in FORBIDDEN_PUBLIC_PHRASES:
        if phrase.casefold() in lower_text:
            errors.append(f"internal phrase leaked into public content: {phrase!r}")

    fence_count = len(re.findall(r"(?m)^```", text))
    if fence_count % 2:
        errors.append("code fences are unbalanced")

    word_count = len(re.findall(r"\b[\w'-]+\b", text))
    if word_count < 8_000:
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
