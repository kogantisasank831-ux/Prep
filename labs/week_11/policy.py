"""Trusted identity/catalogue boundaries and deliberately narrow screening rules."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass
import json
import re
from typing import Literal
import unicodedata

from labs.week_07.retrieval import (
    CorpusInvariantError,
    SourceChunk,
    digest_text,
    validate_chunks,
)

SourceKey = tuple[str, str, str]
SAFE_ID = re.compile(r"[A-Za-z0-9_-]{1,64}")
HEX_DIGEST = re.compile(r"[a-f0-9]{64}")


class SecurityViolation(ValueError):
    """Bounded internal category; never include untrusted payload in the message."""


def representation_digest(chunk: SourceChunk) -> str:
    """Pin validated content AND metadata, including source-location assertions."""
    validate_chunks((chunk,))
    return digest_text(
        json.dumps(
            asdict(chunk), sort_keys=True, ensure_ascii=False, separators=(",", ":")
        )
    )


def identifier(value: str) -> None:
    if not isinstance(value, str) or SAFE_ID.fullmatch(value) is None:
        raise SecurityViolation("identity_shape")


@dataclass(frozen=True)
class SecurityContext:
    """Injected by a trusted caller; construction is NOT authentication."""

    tenant_id: str
    principal_id: str
    request_id: str

    def __post_init__(self) -> None:
        for value in (self.tenant_id, self.principal_id, self.request_id):
            identifier(value)


@dataclass(frozen=True)
class DocumentPolicy:
    """Protected catalogue metadata, separately supplied from document content."""

    tenant_id: str
    document_id: str
    version: str
    source_digest: str
    readers: frozenset[str]
    state: Literal["approved", "quarantined"]
    bindings: tuple[tuple[str, str], ...]

    @property
    def key(self) -> SourceKey:
        return self.tenant_id, self.document_id, self.version

    def __post_init__(self) -> None:
        for value in self.key:
            identifier(value)
        if (
            not isinstance(self.source_digest, str)
            or HEX_DIGEST.fullmatch(self.source_digest) is None
            or self.state not in ("approved", "quarantined")
            or not isinstance(self.readers, frozenset)
            or len(self.readers) > 32
            or not isinstance(self.bindings, tuple)
            or not 1 <= len(self.bindings) <= 32
        ):
            raise SecurityViolation("catalogue_shape")
        for reader in self.readers:
            identifier(reader)
        ids = set()
        for pair in self.bindings:
            if not isinstance(pair, tuple) or len(pair) != 2:
                raise SecurityViolation("catalogue_binding")
            name, digest = pair
            identifier(name)
            if (
                name in ids
                or not isinstance(digest, str)
                or HEX_DIGEST.fullmatch(digest) is None
            ):
                raise SecurityViolation("catalogue_binding")
            ids.add(name)


class PolicyStore:
    """Trusted local catalogue; replace() models an authorized admin update only."""

    def __init__(self, documents: Sequence[DocumentPolicy]) -> None:
        if len(documents) > 64 or len({d.key for d in documents}) != len(documents):
            raise SecurityViolation("catalogue_size_or_duplicate")
        self._documents = {d.key: d for d in documents}

    def replace(self, document: DocumentPolicy) -> None:
        if document.key not in self._documents:
            raise SecurityViolation("catalogue_update_missing")
        self._documents[document.key] = document

    def get(self, key: SourceKey) -> DocumentPolicy:
        return self._documents[key]

    def can_read(self, context: SecurityContext, chunk: SourceChunk) -> bool:
        if context.tenant_id != chunk.tenant_id:
            return False
        policy = self._documents.get(
            (chunk.tenant_id, chunk.document_id, chunk.document_version)
        )
        if (
            policy is None
            or policy.state != "approved"
            or context.principal_id not in policy.readers
            or policy.source_digest != chunk.source_digest
        ):
            return False
        # Pin source identity and the actual chunk representation. A body field
        # claiming that its own checksum/ACL is approved has no authority here.
        expected = dict(policy.bindings).get(chunk.chunk_id)
        if expected is None:
            return False
        try:
            return expected == representation_digest(chunk)
        except CorpusInvariantError:
            return False


@dataclass(frozen=True)
class ScopedAccess:
    context: SecurityContext
    store: PolicyStore

    def can_read(self, principal_id: str, chunk: SourceChunk) -> bool:
        return principal_id == self.context.principal_id and self.store.can_read(
            self.context, chunk
        )


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    output: dict[str, object] = {}
    for key, value in pairs:
        if key in output:
            raise SecurityViolation("json_duplicate_key")
        output[key] = value
    return output


def _invalid_constant(value: str) -> object:
    raise SecurityViolation("json_nonfinite")


def bounded_json(raw: str, *, max_bytes: int) -> object:
    """Bound before decoding and cap structural nesting, respecting JSON strings."""
    if not isinstance(raw, str):
        raise SecurityViolation("json_type")
    try:
        encoded = raw.encode("utf-8")
    except UnicodeError as error:
        raise SecurityViolation("json_encoding") from error
    if len(encoded) > max_bytes:
        raise SecurityViolation("json_size")
    depth, quoted, escaped = 0, False, False
    for char in raw:
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in "[{":
            depth += 1
            if depth > 8:
                raise SecurityViolation("json_depth")
        elif char in "]}":
            depth -= 1
    try:
        return json.loads(
            raw, object_pairs_hook=_unique_object, parse_constant=_invalid_constant
        )
    except (json.JSONDecodeError, RecursionError) as error:
        raise SecurityViolation("json_syntax") from error


def parse_question(raw: str) -> str:
    value = bounded_json(raw, max_bytes=4096)
    if not isinstance(value, dict) or set(value) != {"question"}:
        raise SecurityViolation("request_schema")
    question = value["question"]
    if not isinstance(question, str) or not question.strip() or len(question) > 1000:
        raise SecurityViolation("question_shape")
    try:
        question.encode("utf-8")
    except UnicodeError as error:
        raise SecurityViolation("question_encoding") from error
    return question


def findings(text: str) -> tuple[str, ...]:
    """A few fixed teaching signals, with known false positives and misses."""
    normalized = " ".join(unicodedata.normalize("NFKC", text).casefold().split())
    patterns = (
        (
            "instruction_override",
            r"\b(?:ignore|disregard) (?:all |the )?(?:previous|earlier|system) instructions\b",
        ),
        (
            "prompt_extraction",
            r"\b(?:reveal|print|show) (?:the |your )?system prompt\b",
        ),
        ("exfiltration_instruction", r"\b(?:send|upload|export)\b.{0,100}\bhttps?://"),
        ("synthetic_canary", r"demo-canary-[a-z0-9_-]+"),
        ("contact_email", r"\b[a-z0-9._%+-]+@(?:[a-z0-9-]+\.)+[a-z]{2,}\b"),
    )
    return tuple(name for name, pattern in patterns if re.search(pattern, normalized))
