"""A local quote-only RAG boundary, not a general-purpose model security filter."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
import json
from typing import Protocol

from labs.week_07.retrieval import RetrievalRequest, SourceChunk
from labs.week_08.pipeline import (
    EvidenceSpan,
    KnowledgeAssistant,
    PipelineConfig,
    validate_citations,
)
from labs.week_11.policy import (
    PolicyStore,
    ScopedAccess,
    SecurityContext,
    SecurityViolation,
    bounded_json,
    findings,
    parse_question,
)

REFUSAL = "I cannot produce an allowed answer for this request."


@dataclass(frozen=True)
class Limits:
    context_chars: int = 1400

    def __post_init__(self) -> None:
        if type(self.context_chars) is not int or not 2 <= self.context_chars <= 1400:
            raise SecurityViolation("context_limit")


class Responder(Protocol):
    def propose(self, question: str, context: str) -> str: ...


@dataclass(frozen=True)
class QuoteOnlyResponder:
    """A scripted response formatter, NOT an LLM or injection-efficacy experiment."""

    def propose(self, question: str, context: str) -> str:
        entries = json.loads(context)
        return json.dumps(
            {
                "quotes": [
                    {"citation": row["citation_id"], "text": row["text"]}
                    for row in entries
                ]
            },
            ensure_ascii=False,
        )


@dataclass(frozen=True)
class SecuredResult:
    """Only safe answer text/labels plus local internal diagnostic metadata."""

    answer: str
    citation_ids: tuple[str, ...]
    request_id: str
    reason: str
    candidate_count: int
    blocked_chunk_count: int

    def safe_event(self) -> dict[str, str | int]:
        return {
            "schema": "week11-security-event/1.0.0",
            "request_id": self.request_id,
            "outcome": "answered" if self.reason == "ok" else "refused",
            "reason": self.reason,
            "candidate_count": self.candidate_count,
            "citation_count": len(self.citation_ids),
            "blocked_chunk_count": self.blocked_chunk_count,
        }


def validate_proposal(
    raw: str, spans: Sequence[EvidenceSpan]
) -> tuple[EvidenceSpan, ...]:
    """Closed JSON envelope and exact selected quotes; does not judge source truth."""
    value = bounded_json(raw, max_bytes=8192)
    if not isinstance(value, dict) or set(value) != {"quotes"}:
        raise SecurityViolation("output_schema")
    rows = value["quotes"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= 3:
        raise SecurityViolation("output_count")
    permitted = {span.citation_id: span for span in spans}
    output: list[EvidenceSpan] = []
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"citation", "text"}:
            raise SecurityViolation("quote_schema")
        label, text = row["citation"], row["text"]
        if not isinstance(label, str) or not isinstance(text, str):
            raise SecurityViolation("quote_types")
        selected = permitted.get(label)
        if selected is None or label in seen or text != selected.quote:
            raise SecurityViolation("quote_not_selected")
        if findings(text):
            raise SecurityViolation("output_content")
        seen.add(label)
        output.append(selected)
    return tuple(output)


def secure_ask(
    context: SecurityContext,
    raw_request: str,
    chunks: Sequence[SourceChunk],
    store: PolicyStore,
    *,
    responder: Responder | None = None,
    limits: Limits | None = None,
) -> SecuredResult:
    """Apply scope BEFORE retrieval and independently validate proposed output.

    No action dispatcher, provider transport, cache, HTTP auth or HTML renderer
    is supplied. Runtime errors/cancellation from an adapter propagate; they are
    not converted into successful answers or automatically retried.
    """
    limits = limits or Limits()
    candidate_count = blocked = 0

    def refusal(reason: str) -> SecuredResult:
        return SecuredResult(
            REFUSAL, (), context.request_id, reason, candidate_count, blocked
        )

    try:
        question = parse_question(raw_request)
    except SecurityViolation:
        return refusal("input_invalid")
    if findings(question):
        return refusal("input_blocked")
    if len(chunks) > 256:
        raise SecurityViolation("corpus_limit")
    access = ScopedAccess(context, store)
    eligible = []
    for chunk in chunks:
        if not access.can_read(context.principal_id, chunk):
            continue
        if findings(chunk.text):
            blocked += 1
            continue
        eligible.append(chunk)
    result = KnowledgeAssistant(
        eligible, access, config=PipelineConfig(context_chars=limits.context_chars)
    ).ask(
        RetrievalRequest(context.principal_id, question, 3),
        request_id=context.request_id,
    )
    candidate_count = len(result.candidates)
    if not result.citations:
        return refusal("no_context")
    raw_output = (responder or QuoteOnlyResponder()).propose(question, result.context)
    try:
        selected = validate_proposal(raw_output, result.citations)
    except SecurityViolation:
        return refusal("output_blocked")
    # Recheck ALL supplied context after the responder returns, including spans
    # omitted from its response. This cannot retract data already read earlier.
    if not all(
        access.can_read(context.principal_id, s.chunk) for s in result.citations
    ):
        return refusal("source_changed")
    validate_citations(selected, eligible, context.principal_id, access)
    answer = "\n".join(f"{s.quote} [{s.citation_id}]" for s in selected)
    return SecuredResult(
        answer,
        tuple(s.citation_id for s in selected),
        context.request_id,
        "ok",
        candidate_count,
        blocked,
    )
