"""Actual scoped PostgreSQL/pgvector reads and immutable source snapshots."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from math import sqrt
from typing import Protocol, cast

import psycopg
from psycopg.rows import dict_row

from labs.week_07.retrieval import (
    CorpusInvariantError,
    SourceChunk,
    digest_text,
    tokenize,
    validate_chunks,
)
from labs.week_11.policy import (
    DocumentPolicy,
    PolicyStore,
    SecurityContext,
    SecurityViolation,
    findings,
)
from labs.week_12.config import Settings

EMBEDDING_CONTRACT = "token-hash32-l2/v1"
SCHEMA_VERSION = "week12/1"


class RepositoryUnavailable(Exception):
    """A bounded repository failure; raw driver details stay out of responses."""


def embedding(text: str) -> tuple[float, ...]:
    """Synthetic deterministic token hashing, not a trained semantic encoder."""
    values = [0.0] * 32
    for term in tokenize(text):
        digest = sha256(term.encode()).digest()
        values[digest[0] % 32] += 1.0 if digest[1] % 2 else -1.0
    norm = sqrt(sum(value * value for value in values))
    return tuple(value / norm for value in values) if norm else ()


def vector_literal(values: tuple[float, ...]) -> str:
    return "[" + ",".join(format(value, ".12g") for value in values) + "]"


@dataclass(frozen=True)
class Snapshot:
    chunks: tuple[SourceChunk, ...]
    policies: tuple[DocumentPolicy, ...]

    def fingerprint(self) -> str:
        policies = []
        for policy in sorted(self.policies, key=lambda item: item.key):
            row = asdict(policy)
            row["readers"] = sorted(policy.readers)
            policies.append(row)
        return digest_text(
            json.dumps(
                {
                    "embedding": EMBEDDING_CONTRACT,
                    "chunks": [asdict(chunk) for chunk in self.chunks],
                    "policies": policies,
                },
                sort_keys=True,
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )


class Repository(Protocol):
    async def snapshot(self, context: SecurityContext, question: str) -> Snapshot: ...

    async def ready(self) -> bool: ...

    async def close(self) -> None: ...


def string(row: Mapping[str, object], name: str) -> str:
    value = row[name]
    if not isinstance(value, str):
        raise RepositoryUnavailable("stored_shape")
    return value


def chunk_from_json(value: object) -> SourceChunk:
    if not isinstance(value, dict) or set(value) != {
        "chunk_id",
        "tenant_id",
        "document_id",
        "document_version",
        "source_digest",
        "text",
        "metadata",
    }:
        raise RepositoryUnavailable("stored_shape")
    row = cast(dict[str, object], value)
    pairs = row["metadata"]
    if not isinstance(pairs, list) or not all(
        isinstance(pair, list)
        and len(pair) == 2
        and all(isinstance(item, str) for item in pair)
        for pair in pairs
    ):
        raise RepositoryUnavailable("stored_shape")
    metadata = tuple((str(pair[0]), str(pair[1])) for pair in pairs)
    return SourceChunk(
        string(row, "chunk_id"),
        string(row, "tenant_id"),
        string(row, "document_id"),
        string(row, "document_version"),
        string(row, "source_digest"),
        string(row, "text"),
        metadata,
    )


def policy_from_row(row: Mapping[str, object]) -> DocumentPolicy:
    readers, bindings, state = row["readers"], row["bindings"], row["state"]
    if (
        not isinstance(readers, list)
        or not all(isinstance(x, str) for x in readers)
        or not isinstance(bindings, dict)
        or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in bindings.items()
        )
        or state not in ("approved", "quarantined")
    ):
        raise RepositoryUnavailable("stored_shape")
    return DocumentPolicy(
        string(row, "tenant_id"),
        string(row, "document_id"),
        string(row, "document_version"),
        string(row, "source_digest"),
        frozenset(readers),
        state,
        tuple(sorted(bindings.items())),
    )


SCOPE_SQL = """
SELECT c.representation, d.tenant_id, d.document_id, d.document_version,
       d.source_digest, d.state, d.readers, d.bindings
FROM week12_chunks c JOIN week12_documents d
  USING (tenant_id, document_id, document_version)
WHERE d.tenant_id = %s AND d.state = 'approved' AND %s = ANY(d.readers)
  AND c.embedding_contract = %s
ORDER BY c.chunk_id LIMIT 257
"""

VECTOR_SQL = """
WITH eligible AS MATERIALIZED (
  SELECT chunk_id, embedding FROM week12_chunks
  WHERE tenant_id = %s AND chunk_id = ANY(%s) AND embedding_contract = %s
)
SELECT chunk_id FROM eligible
ORDER BY embedding <=> %s::vector, chunk_id LIMIT 12
"""


@dataclass(frozen=True)
class PostgresRepository:
    settings: Settings

    async def connect(self) -> psycopg.AsyncConnection[dict[str, object]]:
        """One short-lived async connection per snapshot; no hidden global pool."""
        return await psycopg.AsyncConnection.connect(
            host=self.settings.host,
            port=self.settings.port,
            dbname=self.settings.database,
            user=self.settings.user,
            password=self.settings.password,
            connect_timeout=3,
            options="-c statement_timeout=2000 -c lock_timeout=1000",
            row_factory=dict_row,
        )

    async def snapshot(self, context: SecurityContext, question: str) -> Snapshot:
        try:
            async with await self.connect() as connection:
                async with connection.transaction():
                    await connection.execute(
                        "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"
                    )
                    cursor = await connection.execute(
                        SCOPE_SQL,
                        (context.tenant_id, context.principal_id, EMBEDDING_CONTRACT),
                    )
                    rows = await cursor.fetchall()
                    if len(rows) > 256:
                        raise RepositoryUnavailable("corpus_limit")
                    chunks = tuple(
                        chunk_from_json(row["representation"]) for row in rows
                    )
                    validate_chunks(chunks)
                    policies = {
                        policy.key: policy for policy in map(policy_from_row, rows)
                    }
                    store = PolicyStore(tuple(policies.values()))
                    eligible = {
                        chunk.chunk_id: chunk
                        for chunk in chunks
                        if store.can_read(context, chunk) and not findings(chunk.text)
                    }
                    vector = embedding(question)
                    if not eligible or not vector:
                        return Snapshot((), ())
                    ranked = await connection.execute(
                        VECTOR_SQL,
                        (
                            context.tenant_id,
                            list(eligible),
                            EMBEDDING_CONTRACT,
                            vector_literal(vector),
                        ),
                    )
                    selected = tuple(
                        eligible[string(row, "chunk_id")]
                        for row in await ranked.fetchall()
                    )
                    keys = {
                        (c.tenant_id, c.document_id, c.document_version)
                        for c in selected
                    }
                    return Snapshot(
                        selected, tuple(policies[key] for key in sorted(keys))
                    )
        except (
            psycopg.Error,
            OSError,
            CorpusInvariantError,
            SecurityViolation,
        ) as error:
            raise RepositoryUnavailable("repository_unavailable") from error

    async def ready(self) -> bool:
        try:
            async with await self.connect() as connection:
                cursor = await connection.execute(
                    "SELECT version FROM week12_schema WHERE singleton = true"
                )
                row = await cursor.fetchone()
                extension = await connection.execute(
                    "SELECT extversion FROM pg_extension WHERE extname = 'vector'"
                )
                installed = await extension.fetchone()
                await connection.execute("SELECT chunk_id FROM week12_chunks LIMIT 1")
                await connection.execute("SELECT state FROM week12_documents LIMIT 1")
                return (
                    row is not None
                    and row["version"] == SCHEMA_VERSION
                    and installed is not None
                )
        except (psycopg.Error, OSError) as error:
            raise RepositoryUnavailable("repository_unavailable") from error

    async def close(self) -> None:
        """Connections already close with their request's context manager."""
