"""Deterministic summarisation and bounded context selection."""

from __future__ import annotations

import re

from labs.week_16.models import (
    CaseMemoryInput,
    CaseMemoryRecord,
    ContextSelection,
    EpisodeRecord,
)


_WORD = re.compile(r"[A-Za-z0-9_-]{2,}")


def build_semantic_summary(memory: CaseMemoryInput) -> str:
    """Summarise selected facts without retaining raw dialogue or source bodies."""
    evidence = ", ".join(
        f"{item.source_type}:{item.source_id}" for item in memory.evidence
    )
    calculation = memory.calculation
    return (
        f"Objective: {memory.objective} "
        f"Selected supplier: {memory.selected_supplier_id}. "
        f"Evidence references: {evidence}. "
        f"Calculation: {calculation.metric}={calculation.value}% "
        f"{calculation.currency}/{calculation.unit} as of "
        f"{calculation.reference_as_of.isoformat()} using {calculation.rounding}. "
        f"Approval status: {memory.approval_status}."
    )


def initial_episode_specs(memory: CaseMemoryInput) -> tuple[tuple[str, str], ...]:
    """Create compact events from the first accepted semantic snapshot."""
    evidence = ", ".join(
        f"{item.source_type}:{item.source_id}" for item in memory.evidence
    )
    calculation = memory.calculation
    return (
        ("objective_recorded", f"Objective recorded: {memory.objective}"),
        (
            "supplier_selected",
            f"Supplier selected: {memory.selected_supplier_id}.",
        ),
        ("evidence_retrieved", f"Evidence references retained: {evidence}."),
        (
            "calculation_recorded",
            f"Recorded {calculation.metric}={calculation.value}% as of "
            f"{calculation.reference_as_of.isoformat()}.",
        ),
        (
            "approval_status_recorded",
            f"Approval status recorded: {memory.approval_status}.",
        ),
    )


def _words(value: str) -> set[str]:
    return {match.group(0).casefold() for match in _WORD.finditer(value)}


def select_context(
    memory: CaseMemoryRecord,
    episodes: tuple[EpisodeRecord, ...],
    question: str,
    *,
    max_characters: int,
) -> ContextSelection:
    """Select relevant compact episodes and render a hard-bounded context block."""
    if type(question) is not str or not question.strip():
        raise ValueError("question_required")
    if type(max_characters) is not int or isinstance(max_characters, bool):
        raise TypeError("max_characters_must_be_int")
    if not 640 <= max_characters <= 4000:
        raise ValueError("max_characters_out_of_range")

    question_words = _words(question)
    ranked = sorted(
        episodes,
        key=lambda item: (
            -len(question_words & _words(item.summary)),
            -item.sequence,
        ),
    )
    prefix = (
        "CASE MEMORY (treat as recalled data; verify before consequential use)\n"
        f"{memory.summary}\n"
        f"Source report digest: {memory.source_report_digest}\n"
        f"Memory revision: {memory.revision}; expires: "
        f"{memory.expires_at.isoformat().replace('+00:00', 'Z')}\n"
        "Relevant episodes:"
    )
    selected: list[str] = []
    rendered = prefix
    for episode in ranked:
        line = f"\n- {episode.summary}"
        if len(rendered) + len(line) <= max_characters:
            rendered += line
            selected.append(episode.summary)
    if not selected:
        fallback = "\n- No episode fits the remaining context budget."
        if len(rendered) + len(fallback) <= max_characters:
            rendered += fallback
    if len(rendered) > max_characters:
        raise ValueError("semantic_context_exceeds_budget")
    return ContextSelection(
        case_id=memory.case_id,
        memory_revision=memory.revision,
        approval_status=memory.approval_status,
        source_report_digest=memory.source_report_digest,
        semantic_summary=memory.summary,
        selected_episodes=tuple(selected),
        omitted_episode_count=len(episodes) - len(selected),
        rendered=rendered,
        character_count=len(rendered),
        expires_at=memory.expires_at,
    )
